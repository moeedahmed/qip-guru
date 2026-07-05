"""Runtime path helpers for source and installed layouts."""

from __future__ import annotations

from pathlib import Path
import sys


SOURCE_ROOT = Path(__file__).resolve().parents[1]
INSTALLED_DATA_ROOT = Path(sys.prefix) / "qip-guru"


def data_path(*parts: str) -> Path:
    """Return a data path from source checkout or installed package data."""

    for root in (SOURCE_ROOT, INSTALLED_DATA_ROOT):
        candidate = root.joinpath(*parts)
        if candidate.exists():
            return candidate
    return SOURCE_ROOT.joinpath(*parts)
