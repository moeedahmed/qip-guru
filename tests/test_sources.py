from qipkit.sources import format_profile, list_profiles, load_profile, source_map_markdown


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
