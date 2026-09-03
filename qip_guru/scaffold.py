"""Project scaffold creation for QIP Guru."""

from __future__ import annotations

import os
import stat
from contextlib import suppress
from datetime import date as date_type
from pathlib import Path

from qip_guru.paths import data_path
from qip_guru.sources import load_profile, source_map_markdown


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


def _write_new_file(
    destination: Path,
    content: str,
    created: list[tuple[Path, int, int]],
) -> None:
    """Exclusively create a file and record its identity before writing it."""

    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(destination, flags, 0o666)
    file_stat = os.fstat(descriptor)
    created.append((destination, file_stat.st_dev, file_stat.st_ino))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            descriptor = -1
            output.write(content)
    finally:
        if descriptor != -1:
            with suppress(OSError):
                os.close(descriptor)


def _remove_created_file(path: Path, device: int, inode: int) -> None:
    """Remove path only if it is still the regular file created by this call."""

    try:
        current = path.lstat()
        if not stat.S_ISREG(current.st_mode):
            return
        if (current.st_dev, current.st_ino) != (device, inode):
            return
        path.unlink()
    except OSError:
        pass


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
    created_files: list[tuple[Path, int, int]] = []
    target_stat = None
    try:
        target_stat = target.lstat()
        for source, filename in SCAFFOLD_FILES:
            content = source.read_text(encoding="utf-8")
            for placeholder, value in replacements.items():
                content = content.replace(placeholder, value)
            destination = target / filename
            _write_new_file(destination, content, created_files)
            created.append(destination)
        source_map = target / "source-map.md"
        _write_new_file(source_map, source_map_markdown(profile), created_files)
        created.append(source_map)
    except Exception:
        for path, device, inode in reversed(created_files):
            _remove_created_file(path, device, inode)
        with suppress(OSError):
            current_target = target.lstat()
            if (
                target_stat is not None
                and stat.S_ISDIR(current_target.st_mode)
                and (current_target.st_dev, current_target.st_ino)
                == (target_stat.st_dev, target_stat.st_ino)
            ):
                target.rmdir()
        raise
    return created
