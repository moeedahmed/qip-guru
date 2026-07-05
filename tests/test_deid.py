from pathlib import Path

from qip_guru.deid import redact_text, scan_text


def test_scan_text_classifies_planted_identifiers_with_positions():
    text = (
        "patient,email,postcode,dob,phone,nhs,possible\n"
        "Fake patient,alex.fake@example.nhs.uk,SW1A 1AA,12/03/1978,"
        "07123 456789,943 476 5919,1234567890\n"
    )

    findings = scan_text(text)
    by_type = {finding.finding_type: finding for finding in findings}

    assert by_type["NHS_NUMBER"].line == 2
    assert by_type["NHS_NUMBER"].column > 1
    assert by_type["NHS_NUMBER"].preview == "943******9"
    assert by_type["POSSIBLE_NHS_NUMBER"].preview == "123******0"
    assert by_type["EMAIL_ADDRESS"].preview == "a***@example.nhs.uk"
    assert by_type["UK_POSTCODE"].preview == "SW1A ***"
    assert by_type["DOB_LIKE_DATE"].preview == "**/**/1978"
    assert by_type["UK_PHONE_NUMBER"].preview == "071******89"


def test_redact_text_replaces_each_finding_without_touching_clean_text():
    text = (
        "Synthetic row for testing only: 943 476 5919, 1234567890, "
        "alex.fake@example.nhs.uk, SW1A 1AA, 12/03/1978, 07123 456789."
    )

    redacted = redact_text(text)

    assert "Synthetic row for testing only" in redacted
    assert "943 476 5919" not in redacted
    assert "1234567890" not in redacted
    assert "alex.fake@example.nhs.uk" not in redacted
    assert "SW1A 1AA" not in redacted
    assert "12/03/1978" not in redacted
    assert "07123 456789" not in redacted
    assert "[NHS_NUMBER]" in redacted
    assert "[POSSIBLE_NHS_NUMBER]" in redacted


def test_scan_file_redaction_does_not_modify_input(tmp_path):
    from qip_guru.deid import redact_file

    source = tmp_path / "input.csv"
    output = tmp_path / "redacted.csv"
    original = "note,nhs,email\nSynthetic only,943 476 5919,alex.fake@example.nhs.uk\n"
    source.write_text(original, encoding="utf-8")

    redact_file(source, output)

    assert source.read_text(encoding="utf-8") == original
    redacted = output.read_text(encoding="utf-8")
    assert "943 476 5919" not in redacted
    assert "alex.fake@example.nhs.uk" not in redacted


def test_redact_file_refuses_unsafe_paths(tmp_path):
    from qip_guru.deid import redact_file

    source = tmp_path / "input.txt"
    source.write_text("Synthetic NHS 943 476 5919", encoding="utf-8")

    try:
        redact_file(source, source)
    except ValueError as exc:
        assert "input file" in str(exc)
    else:
        raise AssertionError("redact_file should refuse to overwrite its input")

    output = tmp_path / "output.txt"
    output.write_text("existing", encoding="utf-8")
    try:
        redact_file(source, output)
    except FileExistsError:
        pass
    else:
        raise AssertionError("redact_file should refuse to overwrite output")


def test_synthetic_fixture_contains_only_fake_planted_identifiers():
    fixture = Path("examples/synthetic_ward_audit.csv")

    text = fixture.read_text(encoding="utf-8")
    findings = scan_text(text)

    assert "SYNTHETIC TEST DATA" in text
    assert "943 476 5919" in text
    assert "alex.fake@example.nhs.uk" in text
    assert {finding.finding_type for finding in findings} >= {
        "NHS_NUMBER",
        "POSSIBLE_NHS_NUMBER",
        "EMAIL_ADDRESS",
        "UK_POSTCODE",
        "DOB_LIKE_DATE",
        "UK_PHONE_NUMBER",
    }
