import json
import re

import pytest

import qip_guru.sources as sources_module
from qip_guru.sources import format_profile, list_profiles, load_profile, source_map_markdown


def valid_profile():
    return {
        "id": "test",
        "name": "Test profile",
        "summary": "A test profile.",
        "use_for": ["Testing"],
        "sources": [
            {
                "title": "Source",
                "organisation": "Organisation",
                "url": "https://example.com",
                "use": "Tests",
                "checked_on": "2026-09-03",
            }
        ],
    }


def write_profile(directory, profile, *, contents=None):
    path = directory / "test.json"
    path.write_text(contents if contents is not None else json.dumps(profile), encoding="utf-8")
    return path


def test_source_profiles_load_with_required_sources():
    profiles = {profile["id"]: profile for profile in list_profiles()}

    assert {"global", "uk", "us", "canada", "australia"} <= set(profiles)
    assert "Institute for Healthcare Improvement" in format_profile(profiles["global"])
    assert "NHS England" in format_profile(profiles["uk"])
    assert "NHS IMPACT" in format_profile(profiles["uk"])
    assert "National Quality Improvement" in format_profile(profiles["uk"])
    assert "CanadiEM" in format_profile(profiles["canada"])
    assert "Agency for Healthcare Research and Quality" in format_profile(profiles["us"])


def test_source_map_markdown_includes_boundaries():
    profile = load_profile("uk")

    markdown = source_map_markdown(profile)

    assert "# Source Map: United Kingdom" in markdown
    assert "Incident Learning Position" in markdown
    assert "do not process identifiable incident narratives" in markdown


def test_unknown_profile_raises_helpful_error():
    try:
        load_profile("mars")
    except ValueError as exc:
        assert "Available profiles" in str(exc)
        assert "global" in str(exc)
    else:
        raise AssertionError("unknown source profile should raise ValueError")


@pytest.mark.parametrize(
    "profile_id",
    [None, 1, "", "   ", ".", "..", "../test", "test/file", r"test\file", "test.json"],
)
def test_invalid_profile_ids_are_rejected_before_file_access(monkeypatch, tmp_path, profile_id):
    class UnreadablePath:
        def __truediv__(self, child):
            raise AssertionError(f"attempted profile-file access for {child}")

    monkeypatch.setattr(sources_module, "STANDARDS_DIR", UnreadablePath())

    with pytest.raises(ValueError, match="source profile ID"):
        load_profile(profile_id)


def test_profile_id_normalisation_remains_supported(monkeypatch, tmp_path):
    write_profile(tmp_path, valid_profile())
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    assert load_profile(" TEST ")["id"] == "test"


def test_malformed_json_has_helpful_value_error(monkeypatch, tmp_path):
    path = write_profile(tmp_path, None, contents='{\n  "id":')
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match=rf"^{re.escape(str(path))} contains malformed JSON at line 2, column 8$"):
        load_profile("test")


@pytest.mark.parametrize("root", [[], "profile", None, 42])
def test_profile_root_must_be_an_object(monkeypatch, tmp_path, root):
    write_profile(tmp_path, root)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match="profile root must be an object"):
        load_profile("test")


@pytest.mark.parametrize("field", ["id", "name", "summary"])
@pytest.mark.parametrize("value", [None, 7, "", "  "])
def test_required_text_fields_must_be_nonblank_strings(monkeypatch, tmp_path, field, value):
    profile = valid_profile()
    profile[field] = value
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match=rf"field '{field}' must be a nonblank string"):
        load_profile("test")


@pytest.mark.parametrize("value", [None, {}, [], [""], [4], ["  "]])
def test_use_for_must_be_a_nonempty_list_of_nonblank_strings(monkeypatch, tmp_path, value):
    profile = valid_profile()
    profile["use_for"] = value
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match="field 'use_for"):
        load_profile("test")


@pytest.mark.parametrize("value", [None, {}, [], ["not an object"]])
def test_sources_must_be_a_nonempty_list_of_objects(monkeypatch, tmp_path, value):
    profile = valid_profile()
    profile["sources"] = value
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match="field 'sources"):
        load_profile("test")


@pytest.mark.parametrize("field", ["title", "organisation", "url", "use", "checked_on"])
@pytest.mark.parametrize("value", [None, 9, "", "  "])
def test_source_fields_are_required_nonblank_strings(monkeypatch, tmp_path, field, value):
    profile = valid_profile()
    if value is None:
        profile["sources"][0].pop(field)
    else:
        profile["sources"][0][field] = value
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match=field):
        load_profile("test")


@pytest.mark.parametrize(
    ("incident", "message"),
    [
        (None, "must be an object"),
        ({}, "position.*nonblank string"),
        ({"position": "  ", "boundaries": []}, "position.*nonblank string"),
        ({"position": "Position", "boundaries": None}, "boundaries.*must be a list"),
        ({"position": "Position", "boundaries": [""]}, "boundaries\\[0\\].*nonblank string"),
        ({"position": "Position", "boundaries": [3]}, "boundaries\\[0\\].*nonblank string"),
    ],
)
def test_incident_learning_schema_is_validated(monkeypatch, tmp_path, incident, message):
    profile = valid_profile()
    profile["incident_learning"] = incident
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    with pytest.raises(ValueError, match=message):
        load_profile("test")


def test_valid_incident_learning_loads(monkeypatch, tmp_path):
    profile = valid_profile()
    profile["incident_learning"] = {"position": "Learn safely", "boundaries": []}
    write_profile(tmp_path, profile)
    monkeypatch.setattr(sources_module, "STANDARDS_DIR", tmp_path)

    assert load_profile("test") == profile
