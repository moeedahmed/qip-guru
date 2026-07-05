# Release Readiness Gate

This gate is for shaping QIP Guru toward a public-safe release. Passing it does not mean the project is published, clinically approved, or safe for real patient data.

## Current Product Verdict

QIP Guru is the public brand and repo/toolkit. The current release shape is:

- repo/toolkit: yes
- static skills: yes
- local CLI: yes
- synthetic run-chart helper: yes
- source profiles: yes
- engine: no
- hosted service: no
- clinical decision support: no
- governance approval tool: no

## Hard Release Boundaries

Do not publish or promote a release unless these statements remain true:

- Only synthetic examples are included.
- Real patient data is explicitly out of scope.
- The scanner is described as assistive pattern matching, not reliable de-identification.
- Local QI, audit, clinical governance, IG, Caldicott, ethics, and publication routes remain required where relevant.
- Incident learning is separate from QIP unless converted into a measured improvement project.
- No LLM calls, external API calls, MCP calls, hosted services, dashboards, background jobs, or agent runtime claims have been added.

## Required Local Proof

Run from the repo root:

```bash
python3 -m pytest -q
python3 -m compileall qip.py qip_guru tests scripts
python3 scripts/release_check.py --install-smoke
python3 scripts/check_sources.py --dry-run
```

The source freshness dry-run lists URLs only. Before an actual public release, run the networked source check and manually review any blocked, redirected, or failed source:

```bash
python3 scripts/check_sources.py
```

## Synthetic Demo Proof

The release smoke check must demonstrate all of the following without real patient data:

- UK scaffold generation with UK source-map content.
- International scaffold generation from global, US, Canadian, and Australian profiles.
- Source display for profiles through the CLI/source formatting path.
- Synthetic run-chart annotation for ED flow, sepsis documentation, and analgesia-time demo datasets.
- Synthetic identifier scan on `examples/synthetic_ward_audit.csv`.
- Valid-checksum NHS-number fixtures use the NHS England synthetic `999` test range convention.
- Redacted output written to a new file without modifying the input.
- Static agent skill guides present with parseable `name`/`description` frontmatter plus source-profile and safety pause anchors.
- No generated artifacts are tracked by `git ls-files`.
- Local install smoke in a temporary venv, proving the packaged `qip-guru` and `qip` console commands can find installed data files and run outside the source tree.

Equivalent release-smoke command:

```bash
python3 scripts/release_check.py --install-smoke
```

`deid scan` exits with status `1` when supported synthetic identifiers are found. That is expected for the included synthetic fixture.

## Repository Preflight

Before any external/public action, verify:

- public repo/toolkit name: QIP Guru
- Python distribution name: `qip-guru`
- Python import package: `qip_guru`
- CLI commands: `qip-guru` and `qip`
- no `.egg-info`, cache, build, dist, venv, or generated smoke-output files are included
- no valid-checksum NHS fixture number outside the `999` test range is included
- no real patient, staff, organisation-sensitive, or incident-identifiable data is included
- `python3 scripts/release_check.py --install-smoke` passes in the extracted checkout

## Public Release Checklist

- [ ] README leads with QIP Guru positioning and no-engine boundary.
- [ ] `SAFETY.md` says the kit is educational and not reliable de-identification for real patient data.
- [ ] `docs/PRODUCT_POSITIONING.md` is current.
- [ ] Source profile URLs have been re-checked and `checked_on` dates updated where needed.
- [ ] All examples are synthetic and marked as synthetic.
- [ ] Valid-checksum NHS-number examples use the NHS England synthetic `999` test range convention, with only one invalid-checksum row retained for `POSSIBLE_NHS_NUMBER`.
- [ ] Synthetic run-chart examples are included and do not imply live clinical performance benchmarking.
- [ ] No generated `.egg-info`, cache, build, or virtual environment files are included in the release diff.
- [ ] Tests, compileall, source dry-run, and install smoke pass locally.
- [ ] Package/distribution naming is `qip-guru`; import remains `qip_guru`; CLI commands are `qip-guru` and `qip`.
- [ ] Founder/product review has approved public copy.
- [ ] Medic/clinical safety review has approved boundaries and non-claims.

## Remaining Before Public Release

- Extract into the intended public repository target without generated caches or local workspace-only files.
- Re-check official source URLs near the release date.
- Review public README wording for non-claims before any announcement.
- Confirm the intended open-source release target, license posture, and contribution policy.
