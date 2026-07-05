from qipkit.scaffold import create_project


def test_create_project_writes_expected_scaffold_with_substitutions(tmp_path):
    project_dir = tmp_path / "demo_qip_project"

    created = create_project(project_dir, "demo_qip_project", date="2026-07-04")

    expected_files = {
        "charter.md",
        "pdsa-log.md",
        "driver-diagram.md",
        "data-collection-spec.md",
        "audit-standards.md",
        "ig-caldicott.md",
        "deid-checklist.md",
        "qip-registration.md",
        "source-map.md",
    }
    assert {path.name for path in created} == expected_files
    assert project_dir.is_dir()

    charter = (project_dir / "charter.md").read_text(encoding="utf-8")
    assert "{{PROJECT_NAME}}" not in charter
    assert "{{DATE}}" not in charter
    assert "# QIP Charter: demo_qip_project" in charter
    assert "Created: 2026-07-04" in charter

    deid_checklist = (project_dir / "deid-checklist.md").read_text(encoding="utf-8")
    assert "synthetic or fully de-identified" in deid_checklist
    assert "local IG" in deid_checklist

    source_map = (project_dir / "source-map.md").read_text(encoding="utf-8")
    assert "Global Core" in source_map
    assert "Institute for Healthcare Improvement" in source_map


def test_create_project_uses_country_source_profile(tmp_path):
    project_dir = tmp_path / "uk_demo"

    create_project(project_dir, "uk_demo", date="2026-07-04", profile_id="uk")

    source_map = (project_dir / "source-map.md").read_text(encoding="utf-8")
    assert "United Kingdom" in source_map
    assert "Patient Safety Incident Response Framework" in source_map
    assert "Healthcare Quality Improvement Partnership" in source_map


def test_create_project_refuses_to_overwrite_existing_directory(tmp_path):
    project_dir = tmp_path / "demo_qip_project"
    project_dir.mkdir()
    (project_dir / "keep.txt").write_text("do not touch", encoding="utf-8")

    try:
        create_project(project_dir, "demo_qip_project", date="2026-07-04")
    except FileExistsError:
        pass
    else:
        raise AssertionError("create_project should refuse existing directories")

    assert (project_dir / "keep.txt").read_text(encoding="utf-8") == "do not touch"
