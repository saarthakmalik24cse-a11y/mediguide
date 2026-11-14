"""Visible release identity prevents confusing old and new server processes."""
VERSION = "0.8.0-demo"


def readiness():
    from .vectorstore import VectorStore
    checks = []
    for route in ("medical", "patient", "lab", "discharge", "medication", "insurance"):
        try:
            store = VectorStore(route)
            checks.append({"module": route, "ready": bool(store.chunks),
                           "sources": len({c.source for c in store.chunks}), "chunks": len(store.chunks)})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            checks.append({"module": route, "ready": False, "error": type(exc).__name__})
    return checks
