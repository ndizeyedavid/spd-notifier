"""Persistence for the SPD-Hub session cookie and user notification settings."""

from __future__ import annotations

import hashlib
import json
import os
import re

from .config import COOKIE_FILE, SETTINGS_FILE


# --------------------------------------------------------------------------- #
# Session cookie
# --------------------------------------------------------------------------- #

def load_cookies() -> str | None:
    """Load a previously saved session-cookie string, or None."""
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh).get("cookies")
    except (OSError, ValueError):
        return None


def save_cookies(cookies: str | None) -> None:
    """Persist (or clear, if None) the session-cookie string."""
    try:
        if cookies:
            with open(COOKIE_FILE, "w", encoding="utf-8") as fh:
                json.dump({"cookies": cookies}, fh)
        else:
            os.remove(COOKIE_FILE)
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# Notification settings (keyed by a hash of the WordPress username)
# --------------------------------------------------------------------------- #

def _settings_key(cookies: str | None) -> str:
    """Create a non-reversible settings key from the WP username."""
    match = re.search(r"wordpress_logged_in_[^=]+=([^;]+)", cookies or "")
    identity = match.group(1).split("%7C", 1)[0] if match else "anonymous"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def load_settings(cookies: str | None = None) -> dict:
    """Load settings for the current authenticated user."""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh).get(_settings_key(cookies), {})
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict, cookies: str | None = None) -> dict:
    """Validate and persist notification preferences for the current user."""
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            all_settings = json.load(fh)
    except (OSError, ValueError):
        all_settings = {}

    clean = {
        "email": str(settings.get("email", "")).strip()[:254],
        "phone": str(settings.get("phone", "")).strip()[:32],
        "paused": bool(settings.get("paused", False)),
        "updated_at": _now(),
    }
    all_settings[_settings_key(cookies)] = clean
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(all_settings, fh, indent=2)
    return clean


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
