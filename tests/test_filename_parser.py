from file_utils import UploadedDocument, parse_filename_claim, validate_upload_batch


def test_filename_total_parses_decimal_claim_without_currency():
    claim = parse_filename_claim("demo_case_02_mar30_mar31_total_1990_20_minimal_redacted.pdf")

    assert claim.claimed_total == 1990.20
    assert claim.claimed_currency is None
    assert claim.evidence == "total_1990_20"


def test_filename_total_parses_explicit_currency_suffix():
    claim = parse_filename_claim("case_total_1990_20_usd.pdf")

    assert claim.claimed_total == 1990.20
    assert claim.claimed_currency == "USD"


def test_upload_batch_rejects_too_many_files():
    docs = [UploadedDocument(f"a{i}.pdf", "application/pdf", b"pdf") for i in range(4)]

    errors = validate_upload_batch(docs)

    assert any("at most 3 files" in error for error in errors)
