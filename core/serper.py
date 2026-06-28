"""Serper.dev REST API client (PRD §5.5).

Handles per-query SERP retrieval across configurable page depth, brand
position detection, rate-limit back-off, optional proxy routing (needed when
``google.serper.dev`` is geo-blocked on the caller's network) and per-query
error isolation.
"""
from __future__ import annotations

import time
from typing import Any, Callable
from urllib.parse import urlparse

import requests

SERPER_ENDPOINT = "https://google.serper.dev/search"


class SerperError(Exception):
    """Unrecoverable Serper problem (invalid key, persistent rate limit)."""


class SerperBlockedError(SerperError):
    """Request blocked before reaching the API (geo/network/proxy issue)."""


def _proxies(proxy: str | None) -> dict[str, str] | None:
    """Build a requests proxies dict. Supports http(s):// and socks5:// URLs."""
    proxy = (proxy or "").strip()
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def _domain_from_url(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


def _is_brand(domain: str, brand_name: str) -> bool:
    if not brand_name:
        return False
    token = brand_name.strip().lower().replace(" ", "")
    return bool(token) and token in domain.replace(".", "").replace("-", "")


def _interpret_failure(resp: requests.Response) -> SerperError:
    """Translate a non-200 response into a precise, user-facing error.

    A genuine Serper auth failure returns JSON (``application/json``). The
    HTML ``403 Forbidden`` page produced by Google's frontend when the source
    IP is geo-blocked is NOT an auth error and must not be reported as a bad
    key (PRD §8 nuance).
    """
    ctype = resp.headers.get("Content-Type", "").lower()
    is_json = "application/json" in ctype
    if resp.status_code in (401, 403):
        if is_json:
            msg = ""
            try:
                msg = str(resp.json().get("message", "")).strip()
            except Exception:
                pass
            return SerperError(
                "API key is invalid or unauthorized. Please check your Serper.dev key."
                + (f" (Serper: {msg})" if msg else "")
            )
        return SerperBlockedError(
            "Request was blocked before reaching Serper (HTTP 403, non-API HTML "
            "response). This is a network/geo block — not your API key. "
            "google.serper.dev is unreachable from this IP. Set a Proxy on the "
            "Global Config page (e.g. socks5://127.0.0.1:1080 or http://host:port) "
            "or run behind a VPN."
        )
    body = (resp.text or "")[:200]
    return SerperError(f"Serper API error {resp.status_code}: {body}")


def _call_serper(
    api_key: str, payload: dict[str, Any], proxy: str | None = None
) -> dict[str, Any]:
    """Single Serper call with proxy routing and rate-limit back-off."""
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    proxies = _proxies(proxy)
    backoff = 5
    for attempt in range(4):
        try:
            resp = requests.post(
                SERPER_ENDPOINT, headers=headers, json=payload,
                timeout=30, proxies=proxies,
            )
        except requests.exceptions.ProxyError as exc:
            raise SerperBlockedError(
                f"Proxy connection failed: {exc}. Check the Proxy URL on the "
                "Global Config page."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise SerperBlockedError(
                "Could not reach google.serper.dev "
                f"({type(exc).__name__}). If you are on a restricted network, "
                "configure a Proxy on the Global Config page."
            ) from exc

        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            if attempt == 3:
                raise SerperError("Rate limit hit repeatedly. Aborting run.")
            time.sleep(backoff)
            backoff *= 2
            continue
        raise _interpret_failure(resp)
    raise SerperError("Serper API unreachable after retries.")


def validate_api_key(
    api_key: str, region: str = "ir", language: str = "fa", proxy: str | None = None
) -> tuple[bool, str]:
    """Probe the key. Returns ``(ok, message)`` so the UI can show the real cause."""
    if not api_key:
        return False, "No API key set."
    try:
        _call_serper(
            api_key,
            {"q": "test", "gl": region, "hl": language, "num": 10, "page": 1},
            proxy,
        )
    except SerperError as exc:
        return False, str(exc)
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"Unexpected error: {exc}"
    return True, "API key is valid."


def track_query(
    api_key: str,
    query_item: dict[str, Any],
    config: dict[str, Any],
    proxy: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch all configured SERP pages for one query and parse the results."""
    rows: list[dict[str, Any]] = []
    num_pages = int(config.get("num_pages", 1))
    brand_name = config.get("brand_name", "")
    position = 0

    for page in range(1, num_pages + 1):
        payload = {
            "q": query_item["query"],
            "gl": config.get("region", "ir"),
            "hl": config.get("language", "fa"),
            "num": 10,
            "page": page,
            "device": config.get("device", "desktop"),
        }
        data = _call_serper(api_key, payload, proxy)
        organic = data.get("organic", []) or []
        for result in organic:
            position += 1
            url = result.get("link", "")
            domain = _domain_from_url(url)
            rows.append(
                {
                    "Query": query_item["query"],
                    "Template": query_item["template"],
                    "Coin (fa_name)": query_item.get("fa_name", ""),
                    "Coin (en_name)": query_item.get("en_name", ""),
                    "Coin (symbol)": query_item.get("symbol", ""),
                    "Position": position,
                    "Page": page,
                    "Domain": domain,
                    "Title": result.get("title", ""),
                    "URL": url,
                    "Snippet": result.get("snippet", ""),
                    "Is Brand": _is_brand(domain, brand_name),
                }
            )

    if not rows:
        rows.append(
            {
                "Query": query_item["query"],
                "Template": query_item["template"],
                "Coin (fa_name)": query_item.get("fa_name", ""),
                "Coin (en_name)": query_item.get("en_name", ""),
                "Coin (symbol)": query_item.get("symbol", ""),
                "Position": "Not Found",
                "Page": "",
                "Domain": "",
                "Title": "",
                "URL": "",
                "Snippet": "",
                "Is Brand": False,
            }
        )
    return rows


def run_tracking(
    api_key: str,
    queries: list[dict[str, Any]],
    config: dict[str, Any],
    progress_cb: Callable[[int, int, int], None] | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Execute tracking over all queries with per-query error isolation.

    ``progress_cb(done, total, errors)`` is invoked after each query.
    Returns ``(all_rows, error_count)``.
    """
    all_rows: list[dict[str, Any]] = []
    errors = 0
    total = len(queries)
    delay = float(config.get("delay_ms", 200)) / 1000.0
    proxy = config.get("proxy", "")

    for idx, item in enumerate(queries, start=1):
        try:
            all_rows.extend(track_query(api_key, item, config, proxy))
        except SerperError:
            raise  # invalid key / block / persistent rate limit -> stop the run
        except Exception:  # network/parse failure on a single query (PRD §8)
            errors += 1
        if progress_cb:
            progress_cb(idx, total, errors)
        if delay and idx < total:
            time.sleep(delay)

    return all_rows, errors
