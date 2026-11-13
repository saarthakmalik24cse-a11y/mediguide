"""Small, inspectable classical-AI examples for claim preparation.

These algorithms plan paperwork, never medical treatment or insurance approval.
"""
from dataclasses import dataclass
import heapq
from itertools import count


@dataclass(frozen=True)
class Action:
    name: str
    provides: frozenset[str]
    cost: int
    requires: frozenset[str] = frozenset()


def uniform_cost_plan(required, available, actions):
    """Find the least-cost path to all required documents (Dijkstra/UCS).

    State = frozenset of available documents. Costs are user-defined effort units.
    A heap expands the cheapest frontier state; best_cost prunes inferior paths.
    """
    required, initial = frozenset(required), frozenset(available)
    if len(actions) > 20 or len(set().union(required, initial, *(a.provides for a in actions))) > 20:
        raise ValueError("This educational planner supports at most 20 actions/documents.")
    if any(a.cost < 0 for a in actions):
        raise ValueError("Uniform-cost search requires nonnegative action costs.")
    serial = count()
    frontier = [(0, next(serial), initial, [])]
    best_cost = {initial: 0}
    trace = []
    while frontier:
        cost, _, state, path = heapq.heappop(frontier)
        if cost != best_cost[state]:
            continue
        trace.append({"documents": sorted(state), "cost": cost})
        if required <= state:
            return {"found": True, "cost": cost, "steps": path, "trace": trace,
                    "initial": sorted(initial), "goal": sorted(required)}
        for action in actions:
            if not action.requires <= state:
                continue
            successor = state | action.provides
            new_cost = cost + action.cost
            if successor != state and new_cost < best_cost.get(successor, float("inf")):
                best_cost[successor] = new_cost
                heapq.heappush(frontier, (new_cost, next(serial), successor, path + [action.name]))
    return {"found": False, "cost": None, "steps": [], "trace": trace,
            "initial": sorted(initial), "goal": sorted(required)}


def schedule_tasks(domains, dependencies, daily_capacity=1):
    """CSP backtracking with minimum-remaining-values (MRV) and forward checking.

    Variables are tasks. Domains are allowed integer days. Constraints enforce
    strict precedence and a daily capacity. Returns a feasible schedule or None.
    """
    if daily_capacity < 1 or len(domains) > 10:
        raise ValueError("Use capacity >= 1 and at most 10 tasks.")
    if any(a not in domains or b not in domains for a, b in dependencies):
        raise ValueError("Every dependency must reference a known task.")
    if any(len(days) > 30 or any(not isinstance(d, int) or d < 1 for d in days) for days in domains.values()):
        raise ValueError("Each domain must contain at most 30 positive integer days.")
    assignment, trace = {}, []

    def allowed(task, day):
        if sum(value == day for value in assignment.values()) >= daily_capacity:
            return False
        for before, after in dependencies:
            if task == after and before in assignment and assignment[before] >= day:
                return False
            if task == before and after in assignment and day >= assignment[after]:
                return False
        return True

    def solve():
        if len(assignment) == len(domains):
            return dict(assignment)
        remaining = {task: sorted(set(d for d in days if allowed(task, d)))
                     for task, days in domains.items() if task not in assignment}
        task = min(remaining, key=lambda name: (len(remaining[name]), name))
        if not remaining[task]:
            trace.append({"task": task, "event": "empty domain / backtrack"})
            return None
        for day in remaining[task]:
            assignment[task] = day
            trace.append({"task": task, "day": day, "event": "try"})
            result = solve()
            if result is not None:
                return result
            del assignment[task]
            trace.append({"task": task, "day": day, "event": "undo"})
        return None

    return {"assignment": solve(), "trace": trace}


def demo_actions():
    return [Action("Get discharge summary", frozenset({"discharge"}), 2),
            Action("Get itemized bill", frozenset({"bill"}), 2),
            Action("Request hospital document bundle", frozenset({"discharge", "bill"}), 3),
            Action("Collect identity proof", frozenset({"identity"}), 1),
            Action("Complete claim form", frozenset({"form"}), 1, frozenset({"discharge", "bill", "identity"}))]
