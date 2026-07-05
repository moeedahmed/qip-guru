# QIP Guru

QIP Guru is a local-first open-source toolkit for clinicians, QI teams, and agent builders to structure healthcare improvement projects with source-grounded governance profiles, static agent skill guides, synthetic examples, and a deterministic assistive de-identification scanner. No patient data required.

This MVP is deliberately small:

- Creates a local QIP project scaffold from static templates.
- Attaches a source profile such as `global`, `uk`, `us`, `canada`, or `australia`.
- Provides static agent skill guides that can be copied into an agent context.
- Analyses synthetic or de-identified run-chart CSVs with simple shift/trend annotations.
- Scans `.csv` and `.txt` files for a narrow set of deterministic identifier patterns.
- Writes redacted copies without modifying the input file.
- Uses Python standard library only at runtime.
- Makes no LLM calls, external API calls, MCP calls, web server calls, or dashboard calls.

This is an educational scaffold. It is not an information governance tool of record, not clinical decision support, not a governance approval tool, and not reliable de-identification for real patient data.

## Product Verdict

- Public brand and open-source repo: QIP Guru.
- Python distribution: `qip-guru`.
- Python import package: `qip_guru`.
- Static skills: included as guide material in `skills/`.
- Local CLI: included as `qip-guru`, `qip`, and `python3 qip.py`.
- Engine: not yet. There is no hosted runtime, model orchestration layer, MCP server, dashboard, or background service.

See `docs/PRODUCT_POSITIONING.md` for naming and non-claim guidance.

## Requirements

- Python 3.11 or newer.
- `pytest` only for running the test suite.

## Install

From a local checkout:

```bash
python3 -m pip install -e ".[dev]"
qip-guru sources list
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

Run these commands from inside a QIP Guru checkout after installing the local package:

```bash
qip new demo_qip_project
qip new uk_demo --profile uk
qip-guru sources list
qip sources show global
qip-guru charts run-chart examples/synthetic_ed_flow_qip.csv --value-column median_time_to_initial_assessment_minutes --date-column week --baseline-points 4 --out /tmp/ed_flow_run_chart.csv
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

### Analyse a run chart CSV

```bash
qip-guru charts run-chart <input.csv> --value-column <column> --out <annotated.csv>
```

Optional flags:

- `--date-column <column>` validates a date/period column exists.
- `--baseline-points <n>` calculates the median from the first `n` rows.
- `--run-length <n>` changes the threshold for same-side shift signals.
- `--trend-length <n>` changes the threshold for consecutive improvement/worsening trend signals.

The command writes a new annotated CSV with `qip_` columns for baseline median, side of median, run length, shift signal, trend direction, trend length, and trend signal. It is a lightweight helper for synthetic or properly de-identified learning data, not a statistical process control package.

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

## How QIP Guru Fits

QIP Guru is not trying to replace mature QI platforms or statistical packages at this stage.

- **Life QI** is the closest product benchmark: a paid QI project platform with dashboards, reporting, organisation portfolios, and community features. QIP Guru is local-first, open-source, and scaffold-focused.
- **QI Macros** is the closest Excel/SPC benchmark: strong charts, Pareto, fishbone, templates, and statistics inside Excel. QIP Guru is not an Excel add-in and does not yet compete on SPC depth.
- **IHI, NHS IMPACT, HQIP, SQUIRE, AHRQ, and Healthcare Excellence Canada** are source and training benchmarks. QIP Guru links users back to source-grounded methods rather than copying guidance.
- **runcharter, qicharts, and spccharter** are open-source R charting benchmarks. QIP Guru's run-chart helper is deliberately lightweight; stronger SPC support may come later.

The wedge is: open-source, local-first, agent-ready QIP scaffolding with source-grounded country profiles, synthetic-safe examples, and deterministic safety checks.

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
python3 -m compileall qip.py qip_guru tests scripts
python3 scripts/release_check.py --install-smoke
python3 scripts/check_sources.py --dry-run
```

The smoke check proves UK and international profile scaffolds, source display, synthetic de-id scan/redact, synthetic run-chart analysis, static skill-guide safety anchors, and the installed `qip-guru` / `qip` console command paths. See `docs/RELEASE_READINESS.md`.

## Architecture

The repo is the kit. The `skills/` directory contains static agent skill guides for use in an agent context; they are not auto-loaded by an agent runtime. The `qip.py` CLI handles deterministic local file work. The `examples/` directory holds synthetic fixtures and demo QIP datasets. The `standards/` directory holds global and country source profiles. See `docs/ARCHITECTURE.md`.

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
