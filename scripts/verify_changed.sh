#!/usr/bin/env bash
# Fast change-safety gate. Run before calling any change "done".
#
# Covers, offline and deterministically:
#   - full pytest suite (unit contracts for deid/charts/scaffold/sources/packaging)
#   - byte-compile of all shipped/test/script modules (import-time syntax safety)
#   - release_check.py's in-process smoke proof (scaffold creation for all 5
#     source profiles, de-id scan/redact round-trip, run-chart signal
#     detection, skill-guide frontmatter/safety-anchor integrity)
#
# Does NOT include the --install-smoke venv-install tier or the source-URL
# check -- those are release-tier only (scripts/verify_release.sh) because
# they are slower and, in check_sources.py's non-dry-run mode, would touch
# the network. This script never touches the network.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "== verify:changed -- pytest =="
python3 -m pytest -q

echo "== verify:changed -- compileall =="
python3 -m compileall qip.py qip_guru tests scripts

echo "== verify:changed -- release_check (no install-smoke) =="
python3 scripts/release_check.py

echo "== verify:changed -- OK =="
