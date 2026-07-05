# QIP Guru Product Positioning

## Decision

QIP Guru is the public product and the open-source repo/toolkit name.

The current implementation should be described as a repo/toolkit with a small CLI and static agent skill guides. It is not a full engine.

## Product Shape

| Surface | Decision | Notes |
| --- | --- | --- |
| Public brand | QIP Guru | The user-facing product family name, consistent with Exam Guru, Career Guru, and Portfolio Guru. |
| Open-source repo/toolkit | QIP Guru | The public package of templates, source profiles, static skills, synthetic examples, and local checks. |
| Python distribution | `qip-guru` | Public install and package metadata name. |
| Python helper package | `qip_guru` | Internal helper package for deterministic local file work. |
| CLI | `qip` / `python3 qip.py` | Local scaffold, source display, and assistive de-id commands. |
| Static skills | `skills/*.md` | Copyable guide material for agent contexts; not auto-loaded by this repo. |
| Engine | Not yet | No hosted runtime, orchestration layer, model router, MCP server, dashboard, workflow engine, or background service. |

## What It Does

- Creates synthetic-safe QIP and audit project scaffolds.
- Shows source profiles for global, UK, US, Canadian, and Australian starting points.
- Provides static agent skill guides for QIP planning, PDSA, audit standards, SMART aims, and incident-learning triage.
- Runs deterministic local scans for a narrow set of supported identifier patterns in CSV or text files.
- Writes redacted copies without modifying input files.

## What It Does Not Do

- It does not approve, register, govern, or clinically validate a QIP.
- It does not provide clinical decision support.
- It does not reliably de-identify real patient data.
- It does not process real patient records, incident narratives, or staff-identifiable material.
- It does not make legal, regulatory, Caldicott, IG, ethics, research, audit, or publication decisions.
- It does not call LLMs, external APIs, MCP tools, web servers, dashboards, or hosted services.

## Naming Guidance

Use `QIP Guru` when discussing the product, repository, toolkit, or product family.

Use `qip-guru` for Python distribution/package metadata.

Use `qip` for the CLI command and `qip_guru` for the Python helper package.

## Release Copy Boundary

Public copy should say:

> QIP Guru helps clinicians and QI teams structure quality-improvement work with source-grounded scaffolds, static agent skill guides, synthetic examples, and local safety checks.

Public copy should not say:

- "approved by governance"
- "safe for patient data"
- "automated de-identification"
- "clinical decision support"
- "AI engine"
- "QIP approval platform"
- "incident reporting tool"
