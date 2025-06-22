"""Utility for logging conversation events to Supabase.

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY) env vars.
Uses the official `supabase-py` client. Ensure it's in requirements.txt.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    from supabase import create_client, Client  # type: ignore
except ImportError:  # pragma: no cover
    # In case supabase-py isn't installed yet, fail gracefully – caller should
    # ensure dependency is available.
    create_client = None  # type: ignore
    Client = None  # type: ignore

_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
)

_supabase: Optional["Client"] = None
if _SUPABASE_URL and _SUPABASE_KEY and create_client:
    _supabase = create_client(_SUPABASE_URL, _SUPABASE_KEY)


def log_event(event: dict) -> None:
    """Insert an event dict into the `conversation_events` table.

    Expected keys: session_id, sender, message_text, intent, timestamp.
    Missing keys are tolerated.
    """
    if not _supabase:
        return
    try:
        _supabase.table("conversation_events").insert(event).execute()
    except Exception as exc:  # pragma: no cover
        # Never crash the caller – just log to stderr.
        import logging

        logging.warning("Failed to log event to Supabase: %s", exc)
