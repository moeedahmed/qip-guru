# Source Policy

Use primary or official sources first:

1. international method or reporting standards
2. national healthcare quality/safety bodies
3. regulator or accreditation bodies
4. local organisational policy
5. peer-reviewed literature only when no standard exists

The kit should store source metadata and original summaries, not scraped policy copies.

## Current Source Anchors

- Institute for Healthcare Improvement: Model for Improvement
- SQUIRE: international QI reporting guidance
- World Health Organization: global patient-safety framing
- HQIP: UK clinical audit guidance
- HQIP: UK QI tools guide
- NHS England: PSIRF and supporting guidance
- NHS England NHS IMPACT: improvement resource directory
- N-QI-CAN: UK clinical audit and QI network resource directory
- AHRQ: US quality and patient-safety tools
- Healthcare Excellence Canada: Canadian patient-safety learning
- CanadiEM HiQuiPs: Canadian emergency medicine QI and patient-safety education series
- Australian Commission on Safety and Quality in Health Care: NSQHS Standards

## Candidate Sources Not Yet Added

- Health Innovation Network: site fetch was blocked during the 2026-07-04 source check, so it needs manual verification before inclusion.
- Any Quality improvement resource pack PDF shared later by the user should be verified against its owning organisation and licence before inclusion.

## Agent Rule

An agent using this kit should say:

- which source profile it used
- what local source still needs checking
- whether the output is QIP, audit, service evaluation, research, or incident learning
- what cannot be safely inferred from the information provided

## Update Rule

Before publishing or relying on a source profile, re-check the official source URL and update `checked_on`.

For a quick link-rot check:

```bash
python3 scripts/check_sources.py --dry-run
python3 scripts/check_sources.py
```

Some official sites are slow or block command-line clients. If a source has an `expected_slow` URL-check annotation, the checker reports a `NOTE` rather than a warning. The source needs browser/manual verification before public release, and the verification should be recorded in the source metadata or release notes.
