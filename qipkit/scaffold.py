"""Project scaffold creation for QIP Guru Kit."""

from __future__ import annotations

from contextlib import suppress
from datetime import date as date_type
from pathlib import Path

from qipkit.paths import data_path
from qipkit.sources import load_profile, source_map_markdown


SCAFFOLD_FILES = (
    (data_path("templates", "charter.md"), "charter.md"),
    (data_path("templates", "pdsa-log.md"), "pdsa-log.md"),
    (data_path("templates", "driver-diagram.md"), "driver-diagram.md"),
    (data_path("templates", "data-collection-spec.md"), "data-collection-spec.md"),
    (data_path("templates", "audit-standards.md"), "audit-standards.md"),
    (data_path("checklists", "ig-caldicott.md"), "ig-caldicott.md"),
    (data_path("checklists", "deid-checklist.md"), "deid-checklist.md"),
    (data_path("checklists", "qip-registration.md"), "qip-registration.md"),
)


def create_project(
    project_dir: str | Path,
    project_name: str | None = None,
    date: str | None = None,
    profile_id: str = "global",
) -> list[Path]:
    """Create a QIP project folder from static templates."""

    target = Path(project_dir)
    if target.exists():
        raise FileExistsError(f"project folder already exists: {target}")

    profile = load_profile(profile_id)
    rendered_name = project_name or target.name
    rendered_date = date or date_type.today().isoformat()
    replacements = {
        "{{PROJECT_NAME}}": rendered_name,
        "{{DATE}}": rendered_date,
    }

    target.mkdir(parents=False)
    created: list[Path] = []
    try:
        for source, filename in SCAFFOLD_FILES:
            content = source.read_text(encoding="utf-8")
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            destination = target / filename
            destination.write_text(content, encoding="utf-8")
            created.append(destination)
        source_map = target / "source-map.md"
        source_map.write_text(source_map_markdown(profile), encoding="utf-8")
        created.append(source_map)
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        with suppress(OSError):
            target.rmdir()
        raise
    return created
