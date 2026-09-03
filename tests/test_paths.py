from pathlib import Path

import pytest

import qip_guru.paths as paths


def set_data_roots(monkeypatch, tmp_path):
    source = tmp_path / "source"
    installed = tmp_path / "installed"
    source.mkdir()
    installed.mkdir()
    monkeypatch.setattr(paths, "SOURCE_ROOT", source)
    monkeypatch.setattr(paths, "INSTALLED_DATA_ROOT", installed)
    return source, installed


def test_data_path_without_parts_returns_source_root(monkeypatch, tmp_path):
    source = tmp_path / "missing-source"
    installed = tmp_path / "installed"
    installed.mkdir()
    monkeypatch.setattr(paths, "SOURCE_ROOT", source)
    monkeypatch.setattr(paths, "INSTALLED_DATA_ROOT", installed)

    assert paths.data_path() == source


def test_data_path_prefers_existing_nested_source_file(monkeypatch, tmp_path):
    source, installed = set_data_roots(monkeypatch, tmp_path)
    source_file = source / "nested" / "data.txt"
    installed_file = installed / "nested" / "data.txt"
    source_file.parent.mkdir()
    installed_file.parent.mkdir()
    source_file.write_text("source", encoding="utf-8")
    installed_file.write_text("installed", encoding="utf-8")

    assert paths.data_path("nested", "data.txt") == source_file


def test_data_path_falls_back_to_existing_installed_file(monkeypatch, tmp_path):
    source, installed = set_data_roots(monkeypatch, tmp_path)
    installed_file = installed / "nested" / "data.txt"
    installed_file.parent.mkdir()
    installed_file.write_text("installed", encoding="utf-8")

    assert paths.data_path("nested", "data.txt") == installed_file


def test_data_path_returns_source_candidate_when_neither_exists(monkeypatch, tmp_path):
    source, _ = set_data_roots(monkeypatch, tmp_path)

    assert paths.data_path("nested", "missing.txt") == source / "nested" / "missing.txt"


@pytest.mark.parametrize("parts", [("",), (".",), ("nested", "", ".", "file")])
def test_data_path_allows_harmless_components(monkeypatch, tmp_path, parts):
    source, _ = set_data_roots(monkeypatch, tmp_path)

    assert paths.data_path(*parts) == source.joinpath(*parts)


@pytest.mark.parametrize(
    "parts",
    [
        ("/absolute",),
        ("safe", "/absolute"),
        (r"\absolute",),
        (r"C:\absolute",),
        (r"C:drive-relative",),
        (r"\\server\share\file",),
    ],
)
def test_data_path_rejects_absolute_components(monkeypatch, tmp_path, parts):
    set_data_roots(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="relative"):
        paths.data_path(*parts)


@pytest.mark.parametrize(
    "part", ["..", "../outside", "nested/../outside", r"..\outside"]
)
def test_data_path_rejects_traversal_segments(monkeypatch, tmp_path, part):
    set_data_roots(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match=r"\.\."):
        paths.data_path(part)


@pytest.mark.parametrize("part", [None, 1, Path("file")])
def test_data_path_rejects_non_string_components(monkeypatch, tmp_path, part):
    set_data_roots(monkeypatch, tmp_path)

    with pytest.raises(TypeError, match="strings"):
        paths.data_path(part)


def test_data_path_fails_closed_on_source_symlink_escape(monkeypatch, tmp_path):
    source, installed = set_data_roots(monkeypatch, tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "data.txt").write_text("outside", encoding="utf-8")
    (installed / "link").mkdir()
    (installed / "link" / "data.txt").write_text("installed", encoding="utf-8")
    try:
        (source / "link").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlinks are not supported: {exc}")

    with pytest.raises(ValueError, match="escapes"):
        paths.data_path("link", "data.txt")
