"""Per-user, private API-key handling (PRD §6 Security).

The Serper API key is held only in ``st.session_state`` — Streamlit isolates
session state per browser session, so each visitor supplies and uses their own
key and nobody can see anyone else's. The key is NEVER written to the shared
``config.json`` or to the repository.

Owner convenience: a key set via ``st.secrets`` or the ``SERPER_API_KEY``
environment variable is used only to *prefill the owner's own session*. For a
public multi-user deployment, leave it unset so every visitor enters their own.
"""
from __future__ import annotations

import os

import streamlit as st

_KEY = "serper_api_key"


def _owner_default() -> str:
    """Optional prefill from Streamlit secrets / env (single-owner convenience)."""
    try:
        if "SERPER_API_KEY" in st.secrets:  # type: ignore[operator]
            return str(st.secrets["SERPER_API_KEY"]).strip()
    except Exception:
        pass
    return os.getenv("SERPER_API_KEY", "").strip()


def get_api_key() -> str:
    """Return the current session's key, seeding it from the owner default once."""
    if _KEY not in st.session_state:
        st.session_state[_KEY] = _owner_default()
    return st.session_state[_KEY]


def set_api_key(key: str) -> None:
    """Store the key for this session only (not persisted to disk)."""
    st.session_state[_KEY] = (key or "").strip()


def clear_api_key() -> None:
    st.session_state[_KEY] = ""


def has_api_key() -> bool:
    return bool(get_api_key())
