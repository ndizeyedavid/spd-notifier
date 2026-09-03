"""Configuration constants for the SPD-Notifier backend."""

from __future__ import annotations

import os

# All SPD-Hub job types we want in the feed query.
JOB_TYPES = [
    "alche-2", "alche", "alu", "casual", "challenge", "entrepreneurship",
    "externship", "fellowships", "freelance", "full-time", "graduate-programme",
    "internship", "only-alc-applicants", "others", "part-time", "research",
    "scholarships", "volunteer",
]

BASE_FEED_URL = "https://spdhub.alueducation.com/"
LOGIN_URL = "https://spdhub.alueducation.com/"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# Persisted state files (kept out of version control).
_ROOT = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE = os.path.join(_ROOT, "..", ".spd_session.json")
SETTINGS_FILE = os.path.join(_ROOT, "..", ".spd_settings.json")

# RSS/Atom element names we treat as plain text (everything else -> `extra`).
KNOWN_ITEM_FIELDS = {
    "title", "link", "description", "summary", "content",
    "pubDate", "published", "updated", "guid", "id", "author",
    "category", "comments",
}


def build_feed_url() -> str:
    """Construct the full RSS feed URL with all job types selected."""
    from urllib.parse import urlencode

    params = {
        "feed": "job_feed",
        "job_types": ",".join(JOB_TYPES),
        "search_location": "",
        "job_categories": "",
        "search_keywords": "",
        "author": "",
    }
    return BASE_FEED_URL + "?" + urlencode(params)
