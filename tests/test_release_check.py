from pathlib import Path

from scripts.release_check import parse_skill_frontmatter, run_release_checks


def test_release_check_exercises_public_safe_launch_proof(tmp_path):
    workdir = tmp_path / "release-smoke"

    proof = run_release_checks(workdir)

    assert any(line.startswith("profiles:") for line in proof)
    assert any("scaffold: uk" in line for line in proof)
    assert any("scaffold: global" in line for line in proof)
    assert any("deid:" in line for line in proof)
    assert any("examples:" in line and "999" in line for line in proof)
    assert any("run-charts:" in line for line in proof)
    assert any("skills:" in line and "frontmatter" in line for line in proof)
    assert any("tracked-files:" in line for line in proof)

    uk_source_map = (workdir / "uk_synthetic_demo" / "source-map.md").read_text(encoding="utf-8")
    global_source_map = (workdir / "global_synthetic_demo" / "source-map.md").read_text(encoding="utf-8")
    redacted = (workdir / "synthetic_ward_audit_redacted.csv").read_text(encoding="utf-8")

    assert "Patient Safety Incident Response Framework" in uk_source_map
    assert "Institute for Healthcare Improvement" in global_source_map
    assert "999 000 0018" not in redacted
    assert "alex.fake@example.nhs.uk" not in redacted
    assert "[NHS_NUMBER]" in redacted


def test_skill_frontmatter_parser_requires_name_and_description():
    frontmatter = parse_skill_frontmatter(Path("skills/source-grounded-qip-planner.md"))

    assert frontmatter["name"] == "source-grounded-qip-planner"
    assert "QIP" in frontmatter["description"]
