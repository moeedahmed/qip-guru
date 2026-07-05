"""Deterministic assistive de-identification helpers for QIP scaffolds."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


@dataclass(frozen=True)
class Finding:
    """A deterministic pattern finding in text."""

    line: int
    column: int
    finding_type: str
    preview: str
    start: int
    end: int
    value: str


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
POSTCODE_RE = re.compile(
    r"\b(?:GIR ?0AA|[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})\b",
    re.IGNORECASE,
)
DATE_RE = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2}|(?:19|20)\d{2}[/-]\d{1,2}[/-]\d{1,2})\b"
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+44[ \t]?0?|0)(?:[ \t-]?\d){9,10}(?!\d)")
NHS_RE = re.compile(r"(?<!\d)(?:\d[ \t-]?){9}\d(?!\d)")


def scan_file(path: str | Path) -> list[Finding]:
    """Scan a UTF-8 text or CSV file for supported identifier patterns."""

    return scan_text(Path(path).read_text(encoding="utf-8"))


def scan_text(text: str) -> list[Finding]:
    """Return deterministic findings with 1-based line and column positions."""

    raw: list[tuple[int, int, str, str]] = []

    for match in EMAIL_RE.finditer(text):
        raw.append((match.start(), match.end(), "EMAIL_ADDRESS", _mask_email(match.group(0))))

    for match in POSTCODE_RE.finditer(text):
        raw.append((match.start(), match.end(), "UK_POSTCODE", _mask_postcode(match.group(0))))

    for match in DATE_RE.finditer(text):
        value = match.group(0)
        if _is_valid_dob_like_date(value):
            raw.append((match.start(), match.end(), "DOB_LIKE_DATE", _mask_date(value)))

    for match in PHONE_RE.finditer(text):
        value = match.group(0)
        if _normalised_digits(value).startswith(("0", "44")):
            raw.append((match.start(), match.end(), "UK_PHONE_NUMBER", _mask_phone(value)))

    for match in NHS_RE.finditer(text):
        value = match.group(0)
        digits = _normalised_digits(value)
        if len(digits) == 10:
            finding_type = "NHS_NUMBER" if _has_valid_nhs_checksum(digits) else "POSSIBLE_NHS_NUMBER"
            raw.append((match.start(), match.end(), finding_type, _mask_nhs_like(value)))

    line_starts = _line_starts(text)
    findings = [
        Finding(
            line=_line_for_index(line_starts, start),
            column=start - line_starts[_line_for_index(line_starts, start) - 1] + 1,
            finding_type=finding_type,
            preview=preview,
            start=start,
            end=end,
            value=text[start:end],
        )
        for start, end, finding_type, preview in _non_overlapping(raw)
    ]
    return sorted(findings, key=lambda finding: (finding.start, finding.end, finding.finding_type))


def redact_file(input_path: str | Path, output_path: str | Path) -> Path:
    """Write a redacted copy, refusing to overwrite input or an existing output."""

    source = Path(input_path)
    destination = Path(output_path)

    if source.resolve() == destination.resolve():
        raise ValueError("output path must not be the input file")
    if destination.exists():
        raise FileExistsError(f"output file already exists: {destination}")

    redacted = redact_text(source.read_text(encoding="utf-8"))
    with destination.open("x", encoding="utf-8") as handle:
        handle.write(redacted)
    return destination


def redact_text(text: str) -> str:
    """Return text with supported findings replaced by bracketed finding labels."""

    findings = scan_text(text)
    if not findings:
        return text

    pieces: list[str] = []
    cursor = 0
    for finding in findings:
        pieces.append(text[cursor : finding.start])
        pieces.append(f"[{finding.finding_type}]")
        cursor = finding.end
    pieces.append(text[cursor:])
    return "".join(pieces)


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for index, char in enumerate(text):
        if char == "\n":
            starts.append(index + 1)
    return starts


def _line_for_index(line_starts: list[int], index: int) -> int:
    low = 0
    high = len(line_starts)
    while low + 1 < high:
        mid = (low + high) // 2
        if line_starts[mid] <= index:
            low = mid
        else:
            high = mid
    return low + 1


def _non_overlapping(raw: list[tuple[int, int, str, str]]) -> list[tuple[int, int, str, str]]:
    priority = {
        "EMAIL_ADDRESS": 0,
        "NHS_NUMBER": 1,
        "POSSIBLE_NHS_NUMBER": 2,
        "UK_PHONE_NUMBER": 3,
        "UK_POSTCODE": 4,
        "DOB_LIKE_DATE": 5,
    }
    ordered = sorted(raw, key=lambda item: (item[0], -(item[1] - item[0]), priority[item[2]]))
    accepted: list[tuple[int, int, str, str]] = []
    occupied: list[range] = []
    for item in ordered:
        start, end, _finding_type, _preview = item
        if any(start < span.stop and end > span.start for span in occupied):
            continue
        accepted.append(item)
        occupied.append(range(start, end))
    return sorted(accepted, key=lambda item: (item[0], item[1], item[2]))


def _normalised_digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def _has_valid_nhs_checksum(digits: str) -> bool:
    if len(digits) != 10:
        return False
    total = sum(int(digit) * weight for digit, weight in zip(digits[:9], range(10, 1, -1)))
    remainder = total % 11
    check_digit = 11 - remainder
    if check_digit == 11:
        check_digit = 0
    if check_digit == 10:
        return False
    return check_digit == int(digits[-1])


def _is_valid_dob_like_date(value: str) -> bool:
    separator = "/" if "/" in value else "-"
    parts = value.split(separator)
    try:
        if len(parts[0]) == 4:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        else:
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        parsed = date(year, month, day)
    except (ValueError, IndexError):
        return False
    return 1900 <= parsed.year <= date.today().year


def _mask_phone(value: str) -> str:
    digits = _normalised_digits(value)
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{digits[:3]}{'*' * max(3, len(digits) - 5)}{digits[-2:]}"


def _mask_nhs_like(value: str) -> str:
    digits = _normalised_digits(value)
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{digits[:3]}{'*' * max(3, len(digits) - 4)}{digits[-1:]}"


def _mask_email(value: str) -> str:
    local, domain = value.split("@", 1)
    first = local[:1] or "*"
    return f"{first}***@{domain}"


def _mask_postcode(value: str) -> str:
    compact = re.sub(r"\s+", "", value.upper())
    if len(compact) <= 3:
        return "***"
    return f"{compact[:-3]} ***"


def _mask_date(value: str) -> str:
    separator = "/" if "/" in value else "-"
    parts = value.split(separator)
    if len(parts[0]) == 4:
        return f"****{separator}**{separator}**"
    return f"**{separator}**{separator}{parts[2]}"
