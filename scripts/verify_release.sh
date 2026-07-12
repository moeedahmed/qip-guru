#!/usr/bin/env bash
# Release-tier change-safety gate. Run before claiming "release-ready" or
# tagging a release. Superset of verify:changed.
#
# Adds:
#   - release_check.py --install-smoke: installs this checkout into a fresh,
#     network-isolated venv and drives the packaged `qip`/`qip-guru` console
#     entry points end to end (sources list, scaffold, deid scan/redact,
#     run-chart) -- the only proof that the packaging metadata in
#     pyproject.toml actually produces a working install, not just working
#     source imports.
#   - check_sources.py --dry-run: confirms every source-profile URL is still
#     listed and well-formed. Dry-run only -- this script does not make live
#     network requests. A separate, human-triggered run of
#     `python3 scripts/check_sources.py` (without --dry-run) is the live
#     link-rot check and is intentionally not part of this gate.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

./scripts/verify_changed.sh

echo "== verify:release -- release_check --install-smoke =="
python3 scripts/release_check.py --install-smoke

echo "== verify:release -- check_sources --dry-run =="
python3 scripts/check_sources.py --dry-run

echo "== verify:release -- OK =="
