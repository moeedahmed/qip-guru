# Contributing

QIP Guru is a public-safe educational scaffold for healthcare quality improvement and audit work. Contributions should improve structure, source grounding, static skill guides, or deterministic local tooling without turning the kit into clinical decision support, governance approval software, a hosted agent engine, or a patient-data processor.

## Core Rules

- Do not add real patient, staff, organisation-sensitive, or incident-identifiable data.
- Do not copy large sections of copyrighted guidance into the repo.
- Prefer official, primary, or nationally recognised sources over blogs or secondary summaries.
- Keep country-specific standards in country profiles rather than the global core.
- Keep outputs assistive. The kit should prompt local review, not replace local QI, audit, Caldicott, IG, ethics, or governance processes.

## Add or Update a Source Profile

Source profiles live in `standards/`.

Each source entry should include:

- `title`
- `organisation`
- `url`
- `summary`
- `checked_on`

Use ISO dates for `checked_on`, for example `2026-07-04`. Before each release, run:

```bash
python3 scripts/check_sources.py --dry-run
python3 scripts/check_sources.py
```

If a source cannot be reached by the checker but is still valid in a browser, document that in the pull request rather than deleting it automatically.

## Add a Country Module

Country modules should be adapters, not forks of the whole kit.

Include:

- source anchors for QI, audit, patient safety, or reporting standards
- local boundaries such as audit vs research vs service evaluation
- incident-learning position if relevant
- known governance caveats

Do not assume that one country's de-identification, consent, reporting, or incident-learning rules apply elsewhere.

## Add a Detector

Detectors should be narrow, deterministic, and tested.

Required:

- a clear jurisdiction or generic scope
- positive and negative synthetic fixtures
- tests for scanning and redaction
- documentation of false-positive and false-negative risks

Do not add free-text name detection, clinical NER, or ML-based redaction without a separate design review. That would change the product risk profile.

## Add a Chart or Measurement Helper

Measurement helpers should stay transparent and lightweight unless the project has a reviewed statistical design.

Required:

- synthetic or properly de-identified fixture data
- tests for normal and failure cases
- clear output column names
- documentation of what the helper does and does not prove

Do not imply that QIP Guru provides full statistical process control, clinical benchmarking, or governance-ready performance reporting.

## Add an Agent Skill Guide

Files in `skills/` are static agent skill guides. They are written so a human or agent can copy them into an agent context. They are not auto-loaded by this repo.

Skill guides should:

- start with frontmatter containing `name` and `description`
- name the source profile they rely on
- ask for missing local governance information
- separate QIP, audit, research, service evaluation, and incident learning
- avoid drafting from real patient-identifiable data
- state uncertainty plainly

When copying a guide into an agent skill directory, copy the complete file and keep the frontmatter plus safety, pause, refusal, and source-check sections intact.

## Local Checks

Run from the repo root:

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m compileall qip.py qip_guru tests scripts
qip sources list
qip-guru charts run-chart examples/synthetic_ed_flow_qip.csv --value-column median_time_to_initial_assessment_minutes --date-column week --baseline-points 4 --out /tmp/ed_flow_run_chart.csv
qip deid scan examples/synthetic_ward_audit.csv
python3 scripts/release_check.py --install-smoke
python3 scripts/check_sources.py --dry-run
```

The scan command should exit `1` when supported synthetic identifiers are present.
