# QIP Guru Kit

QIP Guru is the public product concept. QIP Guru Kit is this open-source repo/toolkit: a local-first starter kit for clinicians, QI teams, and agent builders to structure healthcare improvement projects with source-grounded governance profiles, static agent skill guides, synthetic examples, and a deterministic assistive de-identification scanner. No patient data required.

This MVP is deliberately small:

- Creates a local QIP project scaffold from static templates.
- Attaches a source profile such as `global`, `uk`, `us`, `canada`, or `australia`.
- Provides static agent skill guides that can be copied into an agent context.
- Scans `.csv` and `.txt` files for a narrow set of deterministic identifier patterns.
- Writes redacted copies without modifying the input file.
- Uses Python standard library only at runtime.
- Makes no LLM calls, external API calls, MCP calls, web server calls, or dashboard calls.

This is an educational scaffold. It is not an information governance tool of record, not clinical decision support, not a governance approval tool, and not reliable de-identification for real patient data.

## Product Verdict

- Public brand: QIP Guru.
- Open-source repo/toolkit: QIP Guru Kit.
- Python distribution: `qip-guru-kit`.
- Python import package: `qipkit`.
- Static skills: included as guide material in `skills/`.
- Local CLI: included as `qip` / `python3 qip.py`.
- Engine: not yet. There is no hosted runtime, model orchestration layer, MCP server, dashboard, or background service.

See `docs/PRODUCT_POSITIONING.md` for naming and non-claim guidance.

## Requirements

- Python 3.11 or newer.
- `pytest` only for running the test suite.

## Install

From a local checkout:

```bash
python3 -m pip install -e ".[dev]"
qip sources list
```

> **Homebrew Python / modern Linux note:** If you see `error: externally-managed-environment` (PEP 668), create a virtual environment first:
>
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> python3 -m pip install -e ".[dev]"
> ```
>
> Alternatively, install with `--break-system-packages`, though a venv is strongly recommended.

You can also run the repo-local script directly with `python3 qip.py ...`. If your environment maps `python` to Python 3.11 or newer, `python` is fine.

## Quickstart

Run these commands from inside a QIP Guru Kit checkout after installing the local package:

```bash
qip new demo_qip_project
qip new uk_demo --profile uk
qip sources list
qip sources show global
qip deid scan examples/synthetic_ward_audit.csv
qip deid redact examples/synthetic_ward_audit.csv --out /tmp/synthetic_ward_audit_redacted.csv
python3 -m pytest -q
```

The scan command exits `1` when findings are present and `0` when no supported patterns are found. The redact command refuses to overwrite the input file and refuses to overwrite an existing output file.

## Commands

### Create a project scaffold

```bash
qip new <project-name> [--profile global|uk|us|canada|australia]
```

Creates a new folder containing:

- QIP charter
- PDSA log
- Driver diagram
- Data collection specification
- Audit standards worksheet
- IG/Caldicott checklist
- De-id checklist
- QIP registration checklist
- source map for the selected profile

Existing project folders are never overwritten.

### Inspect source profiles

```bash
qip sources list
qip sources show uk
```

Source profiles live in `standards/`. They provide primary source anchors and boundaries for different jurisdictions. They do not replace local governance.

### Scan for supported identifier patterns

```bash
qip deid scan <file.csv|file.txt>
```

Reports findings to stdout as:

```text
line:column    FINDING_TYPE    masked-preview
```

Supported deterministic detectors are currently UK-focused:

- Valid NHS number using the modulus-11 checksum.
- Invalid or format-only 10-digit NHS-like number as `POSSIBLE_NHS_NUMBER`.
- UK postcode.
- DOB-like date.
- UK phone number.
- Email address.

The scanner does not attempt free-text name detection.

### Write a redacted copy

```bash
qip deid redact <input> --out <output>
```

The input file is read as UTF-8 text and is never modified. The output path must be different from the input path and must not already exist.

## Public-Safe Use

Use the included fixture only for testing. Do not put real patient-identifiable data into this kit. If a QIP or audit requires real patient data, use locally approved NHS systems, agreed minimisation controls, and your organisation's IG process.

## Limitations

- Pattern matching can miss identifiers and can produce false positives.
- The de-id scanner treats CSV as text; it does not understand CSV headers, cell types, or jurisdiction-specific identifiers outside the listed patterns.
- Redaction replaces matched text with bracketed labels and may change field length or formatting.
- Free-text names, addresses beyond postcodes, hospital numbers, record numbers, rare diagnoses, small-cell disclosure, and contextual re-identification are outside this MVP.
- The scaffold helps structure QIP thinking; it does not approve, register, govern, or clinically validate a project.

## Release Readiness

Run the local release smoke check before any public-facing release work:

```bash
python3 -m pytest -q
python3 -m compileall qip.py qipkit tests scripts
python3 scripts/release_check.py --install-smoke
python3 scripts/check_sources.py --dry-run
```

The smoke check proves UK and international profile scaffolds, source display, synthetic de-id scan/redact, static skill-guide safety anchors, and the installed `qip` console command path. See `docs/RELEASE_READINESS.md`.

## Architecture

The repo is the kit. The `skills/` directory contains static agent skill guides for use in an agent context; they are not auto-loaded by an agent runtime. The `qip.py` CLI handles deterministic local file work. The `standards/` directory holds global and country source profiles. See `docs/ARCHITECTURE.md`.

## Source Freshness

Before release, re-check source URLs:

```bash
python3 scripts/check_sources.py --dry-run
python3 scripts/check_sources.py
```

## Contributing

See `CONTRIBUTING.md` before adding country profiles, source anchors, de-identification detectors, or agent skill guides. Contributions must use synthetic examples only and should keep country-specific rules out of the global core.

## Security

Do not include real patient, staff, organisation-sensitive, incident-identifiable, credential, or secret material in bug reports. See `SECURITY.md`.

## Incident Learning

Incident learning is adjacent to QIP, not identical to QIP. UK PSIRF is handled as a UK incident-learning module rather than the universal core. See `docs/INCIDENT_LEARNING.md`.
