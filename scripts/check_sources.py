#!/usr/bin/env python3
"""Check QIP Guru source profile URLs for obvious link rot."""

from __future__ import annotations

import argparse
from http.client import RemoteDisconnected
from pathlib import Path
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qip_guru.sources import list_profiles  # noqa: E402


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "close",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check QIP Guru source profile URLs.")
    parser.add_argument("--dry-run", action="store_true", help="list URLs without making network requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="request timeout in seconds")
    parser.add_argument("--retries", type=int, default=2, help="network attempts before reporting a source check result")
    args = parser.parse_args(argv)

    failures = 0
    for profile in list_profiles():
        for source in profile["sources"]:
            label = f"{profile['id']} | {source['title']} | {source['url']}"
            if args.dry_run:
                print(label)
                continue
            ok, detail = _check_url(source["url"], args.timeout, args.retries)
            if ok:
                print(f"OK | {label} | {detail}")
                continue
            url_check = source.get("url_check", {})
            if url_check.get("expected_slow") or url_check.get("allow_transient_failure"):
                reason = url_check.get("reason", "manual verification required")
                print(f"NOTE | {label} | expected slow/transient check: {detail}; {reason}")
                continue
            print(f"FAIL | {label} | {detail}")
            failures += 1
    return 1 if failures else 0


def _check_url(url: str, timeout: float, retries: int) -> tuple[bool, str]:
    attempts = max(1, retries)
    last_detail = "not checked"
    for attempt in range(1, attempts + 1):
        ok, detail = _check_once(url, timeout)
        if ok:
            if attempt == 1:
                return True, detail
            return True, f"{detail} after {attempt} attempts"
        last_detail = detail
    if attempts == 1:
        return False, last_detail
    return False, f"{last_detail} after {attempts} attempts"


def _check_once(url: str, timeout: float) -> tuple[bool, str]:
    request = Request(url, method="HEAD", headers=BROWSER_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status < 400, str(response.status)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            return _check_get(url, timeout)
        return False, str(exc.code)
    except (TimeoutError, socket.timeout):
        return False, "timeout"
    except RemoteDisconnected:
        return False, "remote disconnected"
    except ConnectionResetError:
        return False, "connection reset"
    except URLError as exc:
        return False, str(exc.reason)


def _check_get(url: str, timeout: float) -> tuple[bool, str]:
    request = Request(url, method="GET", headers=BROWSER_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status < 400, f"GET {response.status}"
    except HTTPError as exc:
        return False, f"GET {exc.code}"
    except (TimeoutError, socket.timeout):
        return False, "GET timeout"
    except RemoteDisconnected:
        return False, "GET remote disconnected"
    except ConnectionResetError:
        return False, "GET connection reset"
    except URLError as exc:
        return False, str(exc.reason)


if __name__ == "__main__":
    raise SystemExit(main())
