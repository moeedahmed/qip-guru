# AGENTS.md — QIP Guru

## Project

QIP Guru: agent-native, local-first healthcare quality-improvement (QI)
toolkit. Ships as a Python package with `qip`/`qip-guru` console entry
points: project scaffolding by source-region profile, deterministic
de-identification (PII scan/redact) of CSV exports, run-chart statistical
analysis for QI/audit data, and static agent skill guides. No database, no
web server, no bot — pure library + CLI.

## Stack

- Python 3.11–3.14, `setuptools`/`pyproject.toml` packaging
- `qip_guru/{charts,deid,scaffold,sources,paths}.py` — engine modules
- `qip.py` — CLI entry point (`qip`/`qip-guru` console scripts)
- `pytest` for unit tests (`tests/`)
- GitHub Actions CI: `.github/workflows/ci.yml`, matrix across
  ubuntu/macos/windows x Python 3.11–3.14

## Change safety gate

Do not claim a change is "done" or "release-ready" without a green run of
the relevant gate below. State which one you ran and paste/summarise its
output as proof.

- **Every change**: `./scripts/verify_changed.sh` — full pytest suite +
  `compileall` + `scripts/release_check.py` (in-process smoke: all 5 source
  profiles scaffold correctly, de-id scan/redact round-trips on the
  synthetic fixture, run-chart analysis produces shift signals on all 3
  synthetic examples, skill-guide frontmatter/safety anchors intact). Fast,
  fully offline. Run before calling any change done.
- **Before release/tag**: `./scripts/verify_release.sh` — `verify_changed`
  plus `release_check.py --install-smoke` (installs into a fresh
  network-isolated venv and drives the packaged `qip`/`qip-guru` console
  commands end to end) and `check_sources.py --dry-run` (source-profile URL
  list integrity, no live requests). CI (`.github/workflows/ci.yml`) runs
  the equivalent steps on every push/PR. See `docs/rollback.md` for the
  rollback playbook.

No repo here owns a database or applies schema migrations, so there is no
migration-safety policy — see `docs/rollback.md` for why.

## Safety boundaries

See `SAFETY.md`. The de-id scanner is assistive pattern-matching, not
proof of anonymisation; this is not clinical decision support or an
information-governance tool of record.

## Rules

- Complete code only, no placeholders or TODOs
- Commit messages: conventional commits (feat/fix/chore/docs)
- Never use real patient-identifiable data anywhere in this repo, including
  test fixtures — synthetic data only (NHS England `999` test-range
  convention for NHS numbers)
- Never remove the `SAFETY.md` boundaries when editing skill guides or docs

## Compatibility

`CLAUDE.md` is a symlink to this file for Claude Code compatibility. Do not
maintain duplicate long-form agent context files.
