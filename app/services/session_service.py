from typing import Dict, Any


# In-memory session store
sessions: Dict[str, Dict[str, Any]] = {}


def get_session(phone: str) -> Dict[str, Any]:
    """
    Returns the user's session.
    Creates a new session if one doesn't exist.
    """

    if phone not in sessions:
        sessions[phone] = {
            "state": "MAIN_MENU",
            "rank": None,
            "category": None,
            "gender": None,
            "branch": None,
        }

    return sessions[phone]


def reset_session(phone: str) -> None:
    """
    Reset a user's session to its initial state.
    """

    sessions[phone] = {
        "state": "MAIN_MENU",
        "rank": None,
        "category": None,
        "gender": None,
        "branch": None,
    }


def clear_all_sessions() -> None:
    """
    Clear all active sessions.
    Useful during development/testing.
    """

    sessions.clear()