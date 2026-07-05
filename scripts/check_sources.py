#!/usr/bin/env python3
"""Check QIP Guru Kit source profile URLs for obvious link rot."""

from __future__ import annotations

import argparse
from pathlib import Path
import socket
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qipkit.sources import list_profiles  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Check QIP Guru Kit source profile URLs.")
    parser.add_argument("--dry-run", action="store_true", help="list URLs without making network requests")
    parser.add_argument("--timeout", type=float, default=10.0, help="request timeout in seconds")
    args = parser.parse_args(argv)

    failures = 0
    for profile in list_profiles():
        for source in profile["sources"]:
            label = f"{profile['id']} | {source['title']} | {source['url']}"
            if args.dry_run:
                print(label)
                continue
            ok, detail = _check_url(source["url"], args.timeout)
            if ok:
                print(f"OK | {label} | {detail}")
                continue
            if source.get("url_check", {}).get("allow_transient_failure"):
                reason = source["url_check"].get("reason", "manual verification required")
                print(f"WARN | {label} | {detail}; {reason}")
                continue
            print(f"FAIL | {label} | {detail}")
            failures += 1
    return 1 if failures else 0


def _check_url(url: str, timeout: float) -> tuple[bool, str]:
    request = Request(url, method="HEAD", headers=BROWSER_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status < 400, str(response.status)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            return _check_get(url, timeout)
        return False, str(exc.code)
    except TimeoutError:
        return False, "timeout"
    except socket.timeout:
        return False, "timeout"
    except URLError as exc:
        return False, str(exc.reason)


def _check_get(url: str, timeout: float) -> tuple[bool, str]:
    request = Request(url, method="GET", headers=BROWSER_HEADERS)
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status < 400, f"GET {response.status}"
    except HTTPError as exc:
        return False, f"GET {exc.code}"
    except TimeoutError:
        return False, "GET timeout"
    except socket.timeout:
        return False, "GET timeout"
    except URLError as exc:
        return False, str(exc.reason)


if __name__ == "__main__":
    raise SystemExit(main())
