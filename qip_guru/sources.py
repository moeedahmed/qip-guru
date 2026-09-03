"""Source profile loading for QIP Guru."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from qip_guru.paths import data_path


STANDARDS_DIR = data_path("standards")
_PROFILE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[a-z0-9_-]*[a-z0-9])?$")


def list_profiles() -> list[dict[str, Any]]:
    """Return all available source profiles in stable id order."""

    profiles = [load_profile(path.stem) for path in sorted(STANDARDS_DIR.glob("*.json"))]
    return sorted(profiles, key=lambda profile: profile["id"])


def load_profile(profile_id: str) -> dict[str, Any]:
    """Load a country or global source profile."""

    if not isinstance(profile_id, str):
        raise ValueError("source profile ID must be a nonblank string")
    normalised = profile_id.lower().strip()
    if not normalised:
        raise ValueError("source profile ID must be a nonblank string")
    if not _PROFILE_ID_PATTERN.fullmatch(normalised):
        raise ValueError(
            "source profile ID must contain only letters, numbers, hyphens, or underscores"
        )
    path = STANDARDS_DIR / f"{normalised}.json"
    if not path.exists():
        available = ", ".join(profile["id"] for profile in list_profiles()) if STANDARDS_DIR.exists() else ""
        raise ValueError(f"unknown source profile '{profile_id}'. Available profiles: {available}")
    with path.open(encoding="utf-8") as handle:
        try:
            profile = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{path} contains malformed JSON at line {exc.lineno}, column {exc.colno}"
            ) from None
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


def _validate_profile(profile: Any, path: Path) -> None:
    if not isinstance(profile, dict):
        raise ValueError(f"{path} profile root must be an object")

    required = {"id", "name", "summary", "use_for", "sources"}
    missing = required - set(profile)
    if missing:
        raise ValueError(f"{path} missing required keys: {', '.join(sorted(missing))}")

    for key in ("id", "name", "summary"):
        if not _is_nonblank_string(profile[key]):
            raise ValueError(f"{path} field '{key}' must be a nonblank string")

    use_for = profile["use_for"]
    if not isinstance(use_for, list) or not use_for:
        raise ValueError(f"{path} field 'use_for' must be a nonempty list")
    for index, item in enumerate(use_for):
        if not _is_nonblank_string(item):
            raise ValueError(f"{path} field 'use_for[{index}]' must be a nonblank string")

    if not isinstance(profile["sources"], list) or not profile["sources"]:
        raise ValueError(f"{path} field 'sources' must be a nonempty list")
    for index, source in enumerate(profile["sources"]):
        if not isinstance(source, dict):
            raise ValueError(f"{path} field 'sources[{index}]' must be an object")
        for key in ("title", "organisation", "url", "use", "checked_on"):
            if key not in source:
                raise ValueError(f"{path} source {index} missing required key: {key}")
            if not _is_nonblank_string(source[key]):
                raise ValueError(
                    f"{path} field 'sources[{index}].{key}' must be a nonblank string"
                )

    if "incident_learning" in profile:
        incident = profile["incident_learning"]
        if not isinstance(incident, dict):
            raise ValueError(f"{path} field 'incident_learning' must be an object")
        if not _is_nonblank_string(incident.get("position")):
            raise ValueError(
                f"{path} field 'incident_learning.position' must be a nonblank string"
            )
        boundaries = incident.get("boundaries")
        if not isinstance(boundaries, list):
            raise ValueError(
                f"{path} field 'incident_learning.boundaries' must be a list"
            )
        for index, boundary in enumerate(boundaries):
            if not _is_nonblank_string(boundary):
                raise ValueError(
                    f"{path} field 'incident_learning.boundaries[{index}]' "
                    "must be a nonblank string"
                )


def _is_nonblank_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
