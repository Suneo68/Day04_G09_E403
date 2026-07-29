from __future__ import annotations
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PARAMETERS = {
    "dclid",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "msclkid",
}


def _is_tracking_parameter(name: str) -> bool:
    normalized = name.strip().lower()
    return normalized.startswith("utm_") or normalized in TRACKING_PARAMETERS


def _normalize_url(value: str) -> str:
    url = (value or "").strip()
    if not url:
        return ""

    try:
        parts = urlsplit(url)
        scheme = parts.scheme.lower()
        hostname = (parts.hostname or "").lower()

        if hostname.startswith("www."):
            hostname = hostname[4:]

        try:
            port = parts.port
        except ValueError:
            port = None

        is_default_port = (
            (scheme == "http" and port == 80)
            or (scheme == "https" and port == 443)
        )
        netloc = hostname
        if port is not None and not is_default_port:
            netloc = f"{hostname}:{port}"

        path = re.sub(r"/+$", "", parts.path) or "/"

        query_items = [
            (name, query_value)
            for name, query_value in parse_qsl(
                parts.query,
                keep_blank_values=True,
            )
            if not _is_tracking_parameter(name)
        ]
        query_items.sort(key=lambda item: (item[0].lower(), item[1]))
        query = urlencode(query_items, doseq=True)

        return urlunsplit((scheme, netloc, path, query, ""))
    except ValueError:
        without_fragment = url.split("#", 1)[0]
        return without_fragment.rstrip("/").casefold()


def _normalize_title(value: str) -> str:
    title = (value or "").casefold()
    title = re.sub(r"[\W_]+", " ", title, flags=re.UNICODE)
    return " ".join(title.split())


def _item_identity(item: dict[str, Any], key: str) -> str | None:
    if key in {"auto", "url"}:
        normalized_url = _normalize_url(str(item.get("url") or ""))
        if normalized_url:
            return f"url:{normalized_url}"

    if key in {"auto", "title"}:
        normalized_title = _normalize_title(str(item.get("title") or ""))
        if normalized_title:
            return f"title:{normalized_title}"

    return None


def deduplicate_sources(
    items: list[dict[str, Any]] | None = None,
    key: str = "auto",
) -> dict[str, Any]:
    normalized_key = (key or "auto").strip().lower()
    if normalized_key not in {"auto", "url", "title"}:
        raise ValueError("key must be one of: auto, url, title")

    if items is None:
        items = []
    if not isinstance(items, list):
        raise TypeError("items must be a list of objects")

    unique_items: list[dict[str, Any]] = []
    seen: set[str] = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise TypeError(f"items[{index}] must be an object")

        identity = _item_identity(item, normalized_key)

        # Items without the selected identity are preserved instead of being
        # incorrectly grouped together as duplicates.
        if identity is None:
            unique_items.append(dict(item))
            continue

        if identity in seen:
            continue

        seen.add(identity)
        unique_items.append(dict(item))

    original_count = len(items)
    unique_count = len(unique_items)

    return {
        "tool": "deduplicate_sources",
        "key": normalized_key,
        "items": unique_items,
        "original_count": original_count,
        "unique_count": unique_count,
        "duplicates_removed": original_count - unique_count,
    }