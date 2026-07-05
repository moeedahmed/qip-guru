"""Source profile loading for QIP Guru Kit."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qipkit.paths import data_path


STANDARDS_DIR = data_path("standards")


def list_profiles() -> list[dict[str, Any]]:
    """Return all available source profiles in stable id order."""

    profiles = [load_profile(path.stem) for path in sorted(STANDARDS_DIR.glob("*.json"))]
    return sorted(profiles, key=lambda profile: profile["id"])


def load_profile(profile_id: str) -> dict[str, Any]:
    """Load a country or global source profile."""

    normalised = profile_id.lower().strip()
    path = STANDARDS_DIR / f"{normalised}.json"
    if not path.exists():
        available = ", ".join(profile["id"] for profile in list_profiles()) if STANDARDS_DIR.exists() else ""
        raise ValueError(f"unknown source profile '{profile_id}'. Available profiles: {available}")
    with path.open(encoding="utf-8") as handle:
        profile = json.load(handle)
    _validate_profile(profile, path)
    return profile


def format_profile(profile: dict[str, Any]) -> str:
    """Format a source profile for CLI output."""

    lines = [
        f"{profile['name']} ({profile['id']})",
        profile["summary"],
        "",
        "Use for:",
    ]
    lines.extend(f"- {item}" for item in profile["use_for"])
    lines.extend(["", "Sources:"])
    for source in profile["sources"]:
        lines.append(f"- {source['title']} | {source['organisation']} | {source['url']}")
    if profile.get("incident_learning"):
        lines.extend(["", "Incident learning:"])
        lines.append(profile["incident_learning"]["position"])
        lines.extend(f"- {item}" for item in profile["incident_learning"]["boundaries"])
    return "\n".join(lines)


def source_map_markdown(profile: dict[str, Any]) -> str:
    """Render a profile into a project-ready markdown source map."""

    lines = [
        f"# Source Map: {profile['name']}",
        "",
        profile["summary"],
        "",
        "This source map is a starting point. Check current local governance before using it for real patient data, live service change, formal audit registration, or publication.",
        "",
        "## Use For",
        "",
    ]
    lines.extend(f"- {item}" for item in profile["use_for"])
    lines.extend(["", "## Primary Sources", ""])
    for source in profile["sources"]:
        lines.extend(
            [
                f"### {source['title']}",
                "",
                f"- Organisation: {source['organisation']}",
                f"- URL: {source['url']}",
                f"- Use: {source['use']}",
                f"- Checked: {source['checked_on']}",
                "",
            ]
        )
    incident = profile.get("incident_learning")
    if incident:
        lines.extend(["## Incident Learning Position", "", incident["position"], ""])
        lines.extend(f"- {item}" for item in incident["boundaries"])
    return "\n".join(lines).rstrip() + "\n"


def _validate_profile(profile: dict[str, Any], path: Path) -> None:
    required = {"id", "name", "summary", "use_for", "sources"}
    missing = required - set(profile)
    if missing:
        raise ValueError(f"{path} missing required keys: {', '.join(sorted(missing))}")
    if not isinstance(profile["sources"], list) or not profile["sources"]:
        raise ValueError(f"{path} must contain at least one source")
    for source in profile["sources"]:
        for key in ("title", "organisation", "url", "use", "checked_on"):
            if key not in source:
                raise ValueError(f"{path} source missing key: {key}")
