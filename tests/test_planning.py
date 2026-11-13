import pytest
from mediguide.planning import Action, demo_actions, uniform_cost_plan, schedule_tasks
from mediguide.knowledge_graph import build_graph
from mediguide.documents import chunk_pages


def test_ucs_selects_cheaper_bundle():
    result = uniform_cost_plan({"discharge", "bill", "identity", "form"}, {"identity"}, demo_actions())
    assert result["found"] and result["cost"] == 4
    assert result["steps"] == ["Request hospital document bundle", "Complete claim form"]


def test_ucs_changes_plan_when_bundle_is_expensive():
    from dataclasses import replace
    actions = demo_actions()
    actions[2] = replace(actions[2], cost=8)
    result = uniform_cost_plan({"form"}, {"identity"}, actions)
    assert result["cost"] == 5
    assert "Request hospital document bundle" not in result["steps"]


def test_ucs_initial_goal_unreachable_and_negative_cost():
    assert uniform_cost_plan({"a"}, {"a"}, [])["cost"] == 0
    assert not uniform_cost_plan({"a"}, set(), [])["found"]
    with pytest.raises(ValueError):
        uniform_cost_plan({"a"}, set(), [Action("bad", frozenset({"a"}), -1)])


def test_csp_satisfies_dependencies_and_capacity():
    domains = {"papers": [2, 3, 4, 5], "id": [1, 2, 3, 4, 5], "form": [1, 2, 3, 4, 5], "submit": [1, 2, 3, 4, 5]}
    assignment = schedule_tasks(domains, [("papers", "form"), ("id", "form"), ("form", "submit")])["assignment"]
    assert assignment is not None
    assert assignment["papers"] < assignment["form"] < assignment["submit"]
    assert assignment["id"] < assignment["form"]
    assert len(set(assignment.values())) == len(assignment)
    assert all(assignment[t] in domains[t] for t in domains)


def test_csp_impossible_and_cycle():
    assert schedule_tasks({"a": [1], "b": [1]}, [("a", "b")])["assignment"] is None
    assert schedule_tasks({"a": [1, 2], "b": [1, 2]}, [("a", "b"), ("b", "a")])["assignment"] is None


def test_graph_keeps_provenance_and_does_not_infer_causation():
    graph = build_graph(chunk_pages([(2, "This evidence mentions iron and hemoglobin.")], "report.pdf", "lab"))
    assert {"Route", "Document", "Evidence", "Concept"} == {n["type"] for n in graph["nodes"]}
    assert {"contains", "has_evidence", "mentions"} == {e["relation"] for e in graph["edges"]}
    assert any(n.get("page") == 2 for n in graph["nodes"])
