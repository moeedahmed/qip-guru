from scripts.release_check import run_release_checks


def test_release_check_exercises_public_safe_launch_proof(tmp_path):
    workdir = tmp_path / "release-smoke"

    proof = run_release_checks(workdir)

    assert any(line.startswith("profiles:") for line in proof)
    assert any("scaffold: uk" in line for line in proof)
    assert any("scaffold: global" in line for line in proof)
    assert any("deid:" in line for line in proof)
    assert any("run-charts:" in line for line in proof)
    assert any("skills:" in line for line in proof)

    uk_source_map = (workdir / "uk_synthetic_demo" / "source-map.md").read_text(encoding="utf-8")
    global_source_map = (workdir / "global_synthetic_demo" / "source-map.md").read_text(encoding="utf-8")
    redacted = (workdir / "synthetic_ward_audit_redacted.csv").read_text(encoding="utf-8")

    assert "Patient Safety Incident Response Framework" in uk_source_map
    assert "Institute for Healthcare Improvement" in global_source_map
    assert "943 476 5919" not in redacted
    assert "alex.fake@example.nhs.uk" not in redacted
    assert "[NHS_NUMBER]" in redacted
