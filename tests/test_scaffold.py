import pytest

from qip_guru.scaffold import create_project


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


def test_create_project_removes_partially_written_current_file(tmp_path, monkeypatch):
    project_dir = tmp_path / "partial"
    original_write_text = type(project_dir).write_text
    writes = 0

    def fail_second_write(path, content, *args, **kwargs):
        nonlocal writes
        writes += 1
        if writes == 2:
            original_write_text(path, content[:12], *args, **kwargs)
            raise OSError("injected partial write")
        return original_write_text(path, content, *args, **kwargs)

    monkeypatch.setattr(type(project_dir), "write_text", fail_second_write)

    with pytest.raises(OSError, match="injected partial write"):
        create_project(project_dir, date="2026-07-04")

    assert not project_dir.exists()


def test_create_project_preserves_raced_symlink_on_failed_write(
    tmp_path, monkeypatch
):
    project_dir = tmp_path / "raced"
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    original_write_text = type(project_dir).write_text
    writes = 0

    def fail_second_write(path, content, *args, **kwargs):
        nonlocal writes
        writes += 1
        if writes == 2:
            path.symlink_to(outside)
            raise OSError("injected raced write")
        return original_write_text(path, content, *args, **kwargs)

    monkeypatch.setattr(type(project_dir), "write_text", fail_second_write)

    with pytest.raises(OSError, match="injected raced write"):
        create_project(project_dir, date="2026-07-04")

    raced = project_dir / "pdsa-log.md"
    assert raced.is_symlink()
    assert raced.read_text(encoding="utf-8") == "outside"
    assert outside.read_text(encoding="utf-8") == "outside"
    assert not (project_dir / "charter.md").exists()
