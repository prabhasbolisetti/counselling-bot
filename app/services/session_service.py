from datetime import datetime, timedelta
from typing import Any, Dict


SESSION_TIMEOUT = timedelta(minutes=30)


# In-memory session store
sessions: Dict[str, Dict[str, Any]] = {}


def _new_session() -> Dict[str, Any]:
    """
    Creates a fresh user session.
    """

    return {
        "state": "MAIN_MENU",
        "rank": None,
        "category": None,
        "gender": None,
        "branch": None,
        "last_activity": datetime.now(),
    }


def get_session(phone: str) -> Dict[str, Any]:
    """
    Returns the user's session.

    Creates a new session if one doesn't exist.

    Automatically expires inactive sessions.
    """

    session = sessions.get(phone)

    if session is None:
        session = _new_session()
        sessions[phone] = session
        return session

    if datetime.now() - session["last_activity"] > SESSION_TIMEOUT:
        session = _new_session()
        sessions[phone] = session
        return session

    session["last_activity"] = datetime.now()

    return session


def update_session(
    phone: str,
    **kwargs,
) -> Dict[str, Any]:
    """
    Update one or more session values.
    """

    session = get_session(phone)

    session.update(kwargs)

    session["last_activity"] = datetime.now()

    return session


def reset_session(phone: str) -> None:
    """
    Reset a user's session.
    """

    sessions[phone] = _new_session()


def delete_session(phone: str) -> None:
    """
    Remove a user's session completely.
    """

    sessions.pop(phone, None)


def clear_expired_sessions() -> None:
    """
    Removes inactive sessions.
    """

    now = datetime.now()

    expired = []

    for phone, session in sessions.items():

        if now - session["last_activity"] > SESSION_TIMEOUT:
            expired.append(phone)

    for phone in expired:
        del sessions[phone]


def clear_all_sessions() -> None:
    """
    Clears every active session.
    Useful during development.
    """

    sessions.clear()