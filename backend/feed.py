"""RSS feed fetching and parsing for the SPD-Notifier backend."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.request import Request, urlopen, URLError

from .config import DEFAULT_HEADERS, KNOWN_ITEM_FIELDS, build_feed_url


def fetch_feed(url: str, cookies: str | None = None, timeout: int = 30) -> tuple[str, str]:
    """
    Download the feed. Returns (body_text, content_type).

    Raises URLError on network failure.
    """
    headers = dict(DEFAULT_HEADERS)
    if cookies:
        headers["Cookie"] = cookies
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", "replace")
        ctype = resp.headers.get("Content-Type", "")
    return body, ctype


def looks_like_xml(body: str, content_type: str) -> bool:
    """Heuristic: did we actually get feed XML, or the login page?"""
    if "xml" in content_type.lower():
        return True
    stripped = body.lstrip().lower()
    return stripped.startswith("<?xml") or stripped.startswith("<rss") or stripped.startswith("<feed")


def _localname(tag: str) -> str:
    """Strip XML namespace from a tag, e.g. '{http://...}title' -> 'title'."""
    return tag.split("}", 1)[1] if "}" in tag else tag


def _text(elem: ET.Element) -> str:
    """Return trimmed text content of an element (and its children)."""
    if elem is None:
        return ""
    txt = "".join(elem.itertext())
    return re.sub(r"\s+", " ", txt).strip()


def _strip_html(raw: str) -> str:
    """Convert HTML description into a short plain-text summary."""
    if not raw:
        return ""
    no_tags = re.sub(r"<[^>]+>", " ", raw)
    no_tags = html.unescape(no_tags)
    no_tags = re.sub(r"\s+", " ", no_tags).strip()
    return no_tags


def _parse_date(value: str) -> str | None:
    """Parse an RSS/Atom date into ISO-8601 UTC. Returns None if unparseable."""
    if not value:
        return None
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(value.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def _collect_item(item: ET.Element) -> dict:
    """Turn a single <item>/<entry> element into a clean dict."""
    data: dict = {
        "title": "",
        "link": "",
        "description_html": "",
        "summary": "",
        "pub_date": None,
        "guid": "",
        "author": "",
        "categories": [],
        "extra": {},
    }

    for child in item:
        name = _localname(child.tag)
        text = _text(child)

        if name == "title":
            data["title"] = text
        elif name in ("link",) and not text and child.get("href"):
            data["link"] = child.get("href")
        elif name == "link":
            data["link"] = text
        elif name in ("description", "summary", "content"):
            data["description_html"] = text
            data["summary"] = _strip_html(text)[:400]
        elif name in ("pubDate", "published", "updated"):
            data["pub_date"] = _parse_date(text)
        elif name in ("guid", "id"):
            data["guid"] = text or (child.get("id") or "")
        elif name == "author":
            data["author"] = text
        elif name == "category":
            label = text or (child.get("term") or "")
            if label:
                data["categories"].append(label)
        else:
            if name not in KNOWN_ITEM_FIELDS:
                data["extra"][name] = text

    if not data["guid"] and data["link"]:
        data["guid"] = data["link"]
    return data


def parse_feed(xml_text: str) -> list[dict]:
    """Parse RSS/Atom XML text into a list of job dicts."""
    root = ET.fromstring(xml_text)
    items = root.findall(".//item") or root.findall(".//{*}item")
    if not items:
        items = root.findall(".//entry") or root.findall(".//{*}entry")
    return [_collect_item(it) for it in items]


def collect(cookies: str | None = None, url: str | None = None) -> dict:
    """
    Fetch + parse the feed and return the full JSON-ready dict.

    On an auth wall or network error, returns a dict with `status: error`
    and a human-readable `message` (never raises for expected failures).
    """
    from .storage import load_cookies

    feed_url = url or build_feed_url()
    if cookies is None:
        cookies = load_cookies()
    result = {
        "status": "ok",
        "source": feed_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "count": 0,
        "jobs": [],
    }
    try:
        body, ctype = fetch_feed(feed_url, cookies=cookies)
    except URLError as exc:
        result["status"] = "error"
        result["message"] = f"Network error while fetching feed: {exc}"
        return result

    if not looks_like_xml(body, ctype):
        result["status"] = "auth_required"
        result["message"] = (
            "The feed returned the login page instead of XML. "
            "SPD-Hub requires an ALU Google sign-in. Supply a valid "
            "session cookie (see README) to retrieve real listings."
        )
        return result

    try:
        jobs = parse_feed(body)
    except ET.ParseError as exc:
        result["status"] = "error"
        result["message"] = f"Failed to parse feed XML: {exc}"
        return result

    result["jobs"] = jobs
    result["count"] = len(jobs)
    return result
