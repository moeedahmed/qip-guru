# Safety

QIP Guru is a public-safe educational scaffold for quality improvement and audit preparation.

Hard boundaries:

- Assistive de-id only. The scanner uses deterministic pattern matching and cannot prove that data is anonymous.
- The scanner is not reliable de-identification for real patient data.
- Names and free-text identifiers are not covered.
- This is not clinical decision support.
- This is not an information governance tool of record.
- This is not governance, audit, ethics, Caldicott, IG, or publication approval.
- Do not use real patient-identifiable data in this kit.

Before using any output in a real NHS QIP or audit:

- Confirm the project route with the local QI, audit, or clinical governance team.
- Confirm data handling with the local IG or Caldicott route.
- Minimise data before extraction.
- Use synthetic or fully de-identified data for development and demonstrations.
- Keep source data in approved systems only.
- Check small numbers and rare combinations for re-identification risk.

The included example data is synthetic test data with planted fake identifiers for scanner tests. Valid-checksum NHS-number fixtures use the NHS England synthetic `999` test range convention, and one invalid-checksum NHS-like value is retained only to test `POSSIBLE_NHS_NUMBER`.

Scanner date matching is deliberately narrow: two-digit-year dates such as `12/03/78` are out of scope and should not be treated as proof that a file is de-identified.
