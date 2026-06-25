from pathlib import Path

from file_utils import parse_filename_claim
from review_rules import evaluate_reimbursement, records_csv_bytes, totals_by_currency
from schemas import ReimbursementExtractionResult

ROOT = Path(__file__).resolve().parents[1]


def load_sample() -> ReimbursementExtractionResult:
    return ReimbursementExtractionResult.model_validate_json((ROOT / "sample_data" / "sample_result.json").read_text(encoding="utf-8"))


def test_totals_by_currency():
    result = load_sample()

    totals = totals_by_currency(result.records)

    assert totals["USD"] == 7.99
    assert totals["CNY"] == 2136.0


def test_multi_currency_and_missing_payment_proof_detection():
    result = load_sample()
    review = evaluate_reimbursement(result, parse_filename_claim(result.source_files[0]))

    assert review.multiple_currencies is True
    assert review.cross_currency_review_required is True
    assert review.payment_evidence_exists is False
    assert review.human_review_recommended is True
    assert any(finding.code == "PAYMENT_PROOF_MISSING" for finding in review.findings)
    assert any(finding.code == "FILENAME_TOTAL_RECHECK_REQUIRED" for finding in review.findings)


def test_csv_export_contains_expected_columns():
    result = load_sample()

    csv_text = records_csv_bytes(result).decode("utf-8-sig")

    assert "Source file" in csv_text
    assert "UPWORK-INV-001" in csv_text
