"""Viva demonstration screens, separated from the patient-facing app."""
import json
import streamlit as st
from .planning import uniform_cost_plan, schedule_tasks, demo_actions
from .knowledge_graph import build_graph
from .vectorstore import VectorStore


def render_coursework():
    st.header("AI methods lab")
    st.caption("Inspect the algorithms behind claim preparation and evidence organization.")
    search_tab, csp_tab, graph_tab = st.tabs(["State-space search", "CSP schedule", "Knowledge representation"])
    with search_tab:
        st.write("Find the lowest-effort sequence for collecting claim paperwork. Effort costs are demonstration inputs, not fees or insurer rules.")
        required = ["discharge", "bill", "identity", "form"]
        available = st.multiselect("Documents already available", required, default=["identity"])
        actions = demo_actions()
        bundle_cost = st.number_input("Hospital bundle effort", min_value=0, max_value=10, value=3, step=1)
        from dataclasses import replace
        actions[2] = replace(actions[2], cost=int(bundle_cost))
        st.dataframe([{"action": a.name, "provides": ", ".join(sorted(a.provides)), "requires": ", ".join(sorted(a.requires)), "cost": a.cost} for a in actions])
        if st.button("Find preparation plan"):
            result = uniform_cost_plan(required, available, actions)
            st.session_state.search_demo = result
        if "search_demo" in st.session_state:
            result = st.session_state.search_demo
            st.write("Last computed plan (rerun after changing inputs)")
            if result["found"]:
                st.success(f"Goal reached at effort cost {result['cost']}")
                for i, step in enumerate(result["steps"], 1):
                    st.write(f"{i}. {step}")
            else:
                st.warning("The available actions cannot reach the goal.")
            with st.expander("Expanded states and search explanation"):
                st.write("Initial state: available documents. Goal: all required documents. An action adds documents when its prerequisites hold. Uniform-cost search expands the least-cost frontier state.")
                st.dataframe(result["trace"])
    with csp_tab:
        st.write("Schedule document collection before submission. Dates and availability are user assumptions; confirm actual deadlines with the insurer.")
        deadline = st.slider("Submission deadline (day number)", 1, 14, 5)
        hospital_day = st.slider("Hospital documents available from day", 1, 14, 2)
        capacity = st.selectbox("Tasks you can complete per day", [1, 2, 3])
        domains = {"Collect hospital papers": list(range(hospital_day, deadline+1)),
                   "Collect identity proof": list(range(1, deadline+1)),
                   "Complete claim form": list(range(1, deadline+1)),
                   "Submit claim": list(range(1, deadline+1))}
        dependencies = [("Collect hospital papers", "Complete claim form"),
                        ("Collect identity proof", "Complete claim form"), ("Complete claim form", "Submit claim")]
        with st.expander("Variables, domains and constraints"):
            st.json(domains)
            st.write("Each task is assigned one allowed day. Dependencies require a strictly earlier day. Daily capacity must not be exceeded. Submission must occur by the deadline.")
        if st.button("Build feasible schedule"):
            st.session_state.csp_demo = schedule_tasks(domains, dependencies, capacity)
        if "csp_demo" in st.session_state:
            result = st.session_state.csp_demo
            st.caption("Last computed schedule; rerun after changing inputs.")
            if result["assignment"] is None:
                st.warning("No feasible schedule under these constraints. Check the availability, deadline or daily capacity.")
            else:
                st.dataframe([{"task": t, "day": d} for t, d in sorted(result["assignment"].items(), key=lambda pair: pair[1])])
            with st.expander("Backtracking trace"):
                st.json(result["trace"])
    with graph_tab:
        route = st.selectbox("Evidence collection", ["medical", "patient", "lab", "discharge", "medication", "insurance"])
        graph = build_graph(VectorStore(route).chunks)
        st.write("Typed semantic network: Route contains Document; Document has Evidence; Evidence mentions Concept. Mentions are exact dictionary matches, not medical diagnoses.")
        st.metric("Nodes", len(graph["nodes"]))
        st.dataframe(graph["edges"])
        st.download_button("Download semantic network", json.dumps(graph, indent=2), "knowledge-graph.json", "application/json")
