from pathlib import Path

import pytest
from pydantic import ValidationError

from schemas import ExtractedRecord, ReimbursementExtractionResult

ROOT = Path(__file__).resolve().parents[1]


def test_sample_result_validates():
    payload = (ROOT / "sample_data" / "sample_result.json").read_text(encoding="utf-8")

    result = ReimbursementExtractionResult.model_validate_json(payload)

    assert result.records
    assert "USD" in result.detected_currencies
    assert result.records[0].document_type == "invoice"


def test_invalid_document_type_is_rejected():
    with pytest.raises(ValidationError):
        ExtractedRecord(source_file="x.pdf", document_type="contract")
