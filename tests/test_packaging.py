import tomllib
from pathlib import Path

from qip import _build_parser
from qipkit.paths import INSTALLED_DATA_ROOT


def test_public_distribution_identity_matches_release_decision():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["name"] == "qip-guru-kit"
    assert pyproject["project"]["version"] == "0.1.0rc1"
    assert pyproject["project"]["scripts"]["qip"] == "qip:main"
    assert pyproject["tool"]["setuptools"]["packages"]["find"]["include"] == ["qipkit*"]
    assert set(pyproject["tool"]["setuptools"]["data-files"]) == {
        "qip-guru-kit/checklists",
        "qip-guru-kit/standards",
        "qip-guru-kit/templates",
    }
    assert INSTALLED_DATA_ROOT.name == "qip-guru-kit"


def test_cli_help_uses_installed_command_name():
    parser = _build_parser()

    assert parser.prog == "qip"
