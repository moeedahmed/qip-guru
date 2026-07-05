#!/usr/bin/env python3
"""Local release-readiness smoke check for QIP Guru Kit."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qipkit.deid import redact_file, scan_file  # noqa: E402
from qipkit.scaffold import create_project  # noqa: E402
from qipkit.sources import format_profile, list_profiles, load_profile  # noqa: E402


EXPECTED_PROFILES = {"global", "uk", "us", "canada", "australia"}
EXPECTED_FINDINGS = {
    "NHS_NUMBER",
    "POSSIBLE_NHS_NUMBER",
    "EMAIL_ADDRESS",
    "UK_POSTCODE",
    "DOB_LIKE_DATE",
    "UK_PHONE_NUMBER",
}
REQUIRED_SKILLS = {
    "source-grounded-qip-planner.md": ("Select a source profile", "clinical decision-support recommendations"),
    "pdsa-coach.md": ("small Plan-Do-Study-Act cycle", "Use synthetic or fully de-identified examples"),
    "audit-standard-finder.md": ("Confirm the source is current", "local audit or governance team"),
    "draft-smart-aim.md": ("Do not use real patient-identifiable data", "Confirm all real project details"),
    "incident-learning-triage.md": ("Do not ask for names", "PSIRF is relevant"),
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local QIP Guru Kit release-readiness smoke checks.")
    parser.add_argument(
        "--workdir",
        help="empty directory for generated synthetic scaffolds; defaults to a temporary directory",
    )
    parser.add_argument(
        "--install-smoke",
        action="store_true",
        help="also install this checkout into a temporary venv without network access and run the qip console script",
    )
    args = parser.parse_args(argv)

    try:
        with _prepared_workdir(args.workdir) as workdir:
            lines = run_release_checks(workdir)
            if args.install_smoke:
                lines.extend(run_install_smoke(workdir / "install-smoke"))
            for line in lines:
                print(line)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


def run_release_checks(workdir: str | Path) -> list[str]:
    """Run deterministic local release checks and return human-readable proof lines."""

    base = Path(workdir)
    base.mkdir(parents=True, exist_ok=True)
    proof: list[str] = []

    profiles = {profile["id"]: profile for profile in list_profiles()}
    missing = EXPECTED_PROFILES - set(profiles)
    if missing:
        raise AssertionError(f"missing expected source profiles: {', '.join(sorted(missing))}")
    proof.append(f"profiles: {', '.join(sorted(profiles))}")

    for profile_id in sorted(EXPECTED_PROFILES):
        profile = load_profile(profile_id)
        display = format_profile(profile)
        if profile["name"] not in display or "Sources:" not in display:
            raise AssertionError(f"profile display missing source content for {profile_id}")

        project_dir = base / f"{profile_id}_synthetic_demo"
        created = create_project(
            project_dir,
            f"synthetic_{profile_id}_demo",
            date="2026-07-05",
            profile_id=profile_id,
        )
        source_map = project_dir / "source-map.md"
        source_text = source_map.read_text(encoding="utf-8")
        if source_map not in created or profile["name"] not in source_text:
            raise AssertionError(f"source map missing profile content for {profile_id}")
        if "local governance" not in source_text:
            raise AssertionError(f"source map missing local governance boundary for {profile_id}")
        proof.append(f"scaffold: {profile_id} -> {project_dir}")

    uk_source_map = (base / "uk_synthetic_demo" / "source-map.md").read_text(encoding="utf-8")
    if "Patient Safety Incident Response Framework" not in uk_source_map:
        raise AssertionError("UK scaffold missing PSIRF source anchor")

    fixture = ROOT / "examples" / "synthetic_ward_audit.csv"
    original = fixture.read_text(encoding="utf-8")
    findings = scan_file(fixture)
    finding_types = {finding.finding_type for finding in findings}
    missing_findings = EXPECTED_FINDINGS - finding_types
    if missing_findings:
        raise AssertionError(f"synthetic fixture missing expected findings: {', '.join(sorted(missing_findings))}")

    redacted_path = base / "synthetic_ward_audit_redacted.csv"
    redact_file(fixture, redacted_path)
    if fixture.read_text(encoding="utf-8") != original:
        raise AssertionError("redaction modified the source fixture")
    redacted = redacted_path.read_text(encoding="utf-8")
    for planted_identifier in ("943 476 5919", "alex.fake@example.nhs.uk", "SW1A 1AA", "12/03/1978"):
        if planted_identifier in redacted:
            raise AssertionError(f"redacted output still contains planted identifier: {planted_identifier}")
    proof.append(f"deid: {len(findings)} synthetic findings redacted -> {redacted_path}")

    _check_skill_guides()
    proof.append(f"skills: {', '.join(sorted(REQUIRED_SKILLS))}")

    return proof


def run_install_smoke(workdir: str | Path, python_executable: str | Path | None = None) -> list[str]:
    """Install the repo into a temporary venv and prove the packaged console path."""

    base = Path(workdir)
    if base.exists() and any(base.iterdir()):
        raise ValueError(f"install smoke workdir must be empty: {base}")
    base.mkdir(parents=True, exist_ok=True)

    venv_dir = base / ".venv"
    python = str(python_executable or sys.executable)

    # Python 3.14 venvs in this environment do not bundle setuptools. System
    # site packages let the no-network install use the already available build backend.
    _run_checked([python, "-m", "venv", "--system-site-packages", str(venv_dir)], cwd=base)
    venv_python, qip_command = _venv_commands(venv_dir)
    _run_checked(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-build-isolation",
            "--no-deps",
            str(ROOT),
        ],
        cwd=base,
    )

    proof: list[str] = []
    sources = _run_checked([str(qip_command), "sources", "list"], cwd=base).stdout
    for profile_id in EXPECTED_PROFILES:
        if f"{profile_id}\t" not in sources:
            raise AssertionError(f"installed qip sources list missing profile: {profile_id}")
    proof.append("install: qip sources list found all expected profiles")

    project_dir = base / "installed_cli_uk_demo"
    _run_checked([str(qip_command), "new", str(project_dir), "--profile", "uk"], cwd=base)
    source_map = project_dir / "source-map.md"
    source_text = source_map.read_text(encoding="utf-8")
    if "United Kingdom" not in source_text or "local governance" not in source_text:
        raise AssertionError("installed qip scaffold did not include UK source-map boundaries")
    proof.append(f"install: qip new created UK scaffold -> {project_dir}")

    fixture = ROOT / "examples" / "synthetic_ward_audit.csv"
    scan = _run_checked([str(qip_command), "deid", "scan", str(fixture)], cwd=base, expected_returncode=1)
    if "NHS_NUMBER" not in scan.stdout or "EMAIL_ADDRESS" not in scan.stdout:
        raise AssertionError("installed qip deid scan missing expected synthetic findings")
    redacted_path = base / "installed_cli_redacted.csv"
    _run_checked([str(qip_command), "deid", "redact", str(fixture), "--out", str(redacted_path)], cwd=base)
    redacted = redacted_path.read_text(encoding="utf-8")
    if "943 476 5919" in redacted or "alex.fake@example.nhs.uk" in redacted:
        raise AssertionError("installed qip redaction left planted synthetic identifiers")
    proof.append(f"install: qip deid scan/redact handled synthetic fixture -> {redacted_path}")

    return proof


def _check_skill_guides() -> None:
    skills_dir = ROOT / "skills"
    for filename, anchors in REQUIRED_SKILLS.items():
        path = skills_dir / filename
        if not path.exists():
            raise AssertionError(f"missing skill guide: {filename}")
        text = path.read_text(encoding="utf-8")
        for anchor in anchors:
            if anchor not in text:
                raise AssertionError(f"{filename} missing safety/source anchor: {anchor}")


@contextmanager
def _prepared_workdir(raw_workdir: str | None) -> Iterator[Path]:
    if raw_workdir:
        workdir = Path(raw_workdir)
        if workdir.exists() and any(workdir.iterdir()):
            raise ValueError(f"workdir must be empty: {workdir}")
        workdir.mkdir(parents=True, exist_ok=True)
        yield workdir
        return

    with TemporaryDirectory(prefix="qip-guru-kit-release-") as temp_dir:
        yield Path(temp_dir)


def _venv_commands(venv_dir: Path) -> tuple[Path, Path]:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe", venv_dir / "Scripts" / "qip.exe"
    return venv_dir / "bin" / "python", venv_dir / "bin" / "qip"


def _run_checked(
    command: list[str],
    cwd: Path,
    expected_returncode: int = 0,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != expected_returncode:
        rendered = " ".join(command)
        raise AssertionError(
            f"command failed with exit {result.returncode}, expected {expected_returncode}: {rendered}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
