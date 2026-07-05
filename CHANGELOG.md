# Changelog

All notable changes to QIP Guru will be documented here.

## 0.1.0rc1 - Unreleased

- Defines QIP Guru as the public brand and open-source toolkit.
- Uses `qip-guru` as the Python distribution name, `qip_guru` as the import package, and both `qip-guru` and `qip` as CLI commands.
- Includes global, UK, US, Canadian, and Australian source profiles.
- Includes static agent skill guides for QIP planning, PDSA, audit standards, SMART aims, and incident-learning triage.
- Includes synthetic ED flow, sepsis documentation, and analgesia-time demo datasets.
- Adds lightweight run-chart CSV annotation for synthetic or properly de-identified QIP data.
- Includes deterministic assistive de-id scanning/redaction for synthetic CSV/text examples.
- Hardens NHS-number and UK-phone scanning so matches cannot span newlines.
- Keeps valid-checksum NHS fixture numbers in the NHS England synthetic `999` test range convention, with one invalid-checksum row for `POSSIBLE_NHS_NUMBER`.
- Adds parseable frontmatter to static agent skill guides.
- Adds local release checks for scaffolding, source profiles, synthetic de-id proof, NHS fixture range checks, run-chart proof, skill-guide frontmatter/safety anchors, tracked generated artifacts, and installed console-command smoke testing.
- Adds GitHub Actions CI, a bug-report template, and a code of conduct.

No public package publication, repository creation, deployment, or external announcement has happened in this release-candidate pass.
