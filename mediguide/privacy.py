"""Request-local storage scope. Never derive an authenticated identity from a widget."""
from contextvars import ContextVar
from hashlib import sha256
from pathlib import Path
import os
from .config import DATA_DIR, DB_PATH, INDEX_DIR

identity = ContextVar("mediguide_identity", default=None)


def set_identity(issuer: str, subject: str) -> None:
    if not issuer or not subject:
        raise ValueError("Verified issuer and subject are required")
    identity.set(sha256((issuer + "\0" + subject).encode()).hexdigest())


def user_root() -> Path | None:
    key = identity.get()
    return DATA_DIR / "users" / key if key else None


def database_path() -> Path:
    root = user_root()
    return root / "history.db" if root else DB_PATH


def index_path(route: str) -> Path:
    root = user_root()
    # Public library is read-only for signed-in users; personal documents private.
    return root / "indexes" if root and route not in {"medical", "medication"} else INDEX_DIR


def gate() -> bool:
    """Returns admin permission; fail closed when authentication is requested."""
    import streamlit as st
    identity.set(None)
    if os.getenv("MEDIGUIDE_AUTH_REQUIRED", "false").lower() != "true":
        return True  # explicitly local demo; not multiuser authentication
    if not st.user.get("is_logged_in", False):
        st.title("Your private MediGuide space")
        st.caption("Sign in with Google to access your documents and conversations.")
        if st.button("Continue with Google"):
            try:
                st.login()
            except Exception:
                st.error("Google login is not configured. Follow ADVANCED_SETUP.md.")
        st.stop()
    claims = st.user.to_dict()
    if not claims.get("sub") or not claims.get("iss"):
        st.error("The provider did not return a verified identity.")
        st.stop()
    set_identity(claims["iss"], claims["sub"])
    with st.sidebar:
        st.caption("Signed in · private document storage")
        if st.button("Sign out"):
            st.logout()
    admins = {x.strip() for x in os.getenv("MEDIGUIDE_ADMIN_SUBJECTS", "").split(",") if x.strip()}
    return claims["sub"] in admins
