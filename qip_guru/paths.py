"""Runtime path helpers for source and installed layouts."""

from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath
import sys


SOURCE_ROOT = Path(__file__).resolve().parents[1]
INSTALLED_DATA_ROOT = Path(sys.prefix) / "qip-guru"


def data_path(*parts: str) -> Path:
    """Return a data path from source checkout or installed package data."""

    if not parts:
        return SOURCE_ROOT

    for part in parts:
        if not isinstance(part, str):
            raise TypeError("data path components must be strings")

        components = (PurePosixPath(part), PureWindowsPath(part))
        if any(component.anchor for component in components):
            raise ValueError("data path components must be relative")
        if any(".." in component.parts for component in components):
            raise ValueError("data path components must not contain '..'")

    for root in (SOURCE_ROOT, INSTALLED_DATA_ROOT):
        candidate = root.joinpath(*parts)
        resolved_root = root.resolve()
        resolved_candidate = candidate.resolve()
        if not resolved_candidate.is_relative_to(resolved_root):
            raise ValueError("data path escapes its data root")
        if candidate.exists():
            return candidate
    return SOURCE_ROOT.joinpath(*parts)
