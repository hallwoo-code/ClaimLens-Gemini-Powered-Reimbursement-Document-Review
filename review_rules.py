from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from file_utils import FilenameClaim
from schemas import ExtractedRecord, ReimbursementExtractionResult


@dataclass
class ReviewFinding:
    code: str
    severity: str
    message: str


@dataclass
class DeterministicReview:
    totals_by_currency: Dict[str, float]
    record_count: int
    invoice_count: int
    payment_proof_count: int
    missing_critical_fields: List[str]
    multiple_currencies: bool
    payment_evidence_exists: bool
    filename_total_match: Optional[bool]
    cross_currency_review_required: bool
    human_review_recommended: bool
    findings: List[ReviewFinding] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totals_by_currency": self.totals_by_currency,
            "record_count": self.record_count,
            "invoice_count": self.invoice_count,
            "payment_proof_count": self.payment_proof_count,
            "missing_critical_fields": self.missing_critical_fields,
            "multiple_currencies": self.multiple_currencies,
            "payment_evidence_exists": self.payment_evidence_exists,
            "filename_total_match": self.filename_total_match,
            "cross_currency_review_required": self.cross_currency_review_required,
            "human_review_recommended": self.human_review_recommended,
            "findings": [finding.__dict__ for finding in self.findings],
        }


def totals_by_currency(records: Iterable[ExtractedRecord]) -> Dict[str, float]:
    totals: Dict[str, float] = {}
    for record in records:
        if record.amount is None or not record.currency:
            continue
        currency = record.currency.upper()
        totals[currency] = round(totals.get(currency, 0.0) + float(record.amount), 2)
    return dict(sorted(totals.items()))


def _critical_missing(records: Iterable[ExtractedRecord]) -> List[str]:
    missing: List[str] = []
    for index, record in enumerate(records, start=1):
        label = f"{record.source_file} record {index}"
        if record.amount is None:
            missing.append(f"{label}: amount")
        if not record.currency:
            missing.append(f"{label}: currency")
        if record.document_type == "invoice" and not record.document_date:
            missing.append(f"{label}: document_date")
    return missing


def evaluate_reimbursement(result: ReimbursementExtractionResult, filename_claim: Optional[FilenameClaim] = None) -> DeterministicReview:
    records = result.records
    totals = totals_by_currency(records)
    currencies = set(totals.keys()) | {currency.upper() for currency in result.detected_currencies if currency}
    invoice_count = sum(1 for record in records if record.document_type == "invoice")
    payment_proof_count = sum(1 for record in records if record.payment_proof_found or record.document_type in {"payment_proof", "wechat_transfer"})
    missing = _critical_missing(records)
    multiple_currencies = len(currencies) > 1
    payment_evidence_exists = bool(result.payment_proof_found or payment_proof_count)
    findings: List[ReviewFinding] = []

    filename_total_match: Optional[bool] = None
    if filename_claim and filename_claim.claimed_total is not None:
        if filename_claim.claimed_currency:
            total = totals.get(filename_claim.claimed_currency.upper())
            filename_total_match = total is not None and abs(total - filename_claim.claimed_total) < 0.01
        elif len(totals) == 1:
            only_total = next(iter(totals.values()))
            filename_total_match = abs(only_total - filename_claim.claimed_total) < 0.01
        else:
            filename_total_match = False
        if filename_total_match is False:
            findings.append(ReviewFinding("FILENAME_TOTAL_RECHECK_REQUIRED", "warning", "The claimed filename total cannot be directly matched to extracted totals."))

    if multiple_currencies:
        findings.append(ReviewFinding("CROSS_CURRENCY_REVIEW_REQUIRED", "warning", "Multiple currencies were detected, so exchange-rate and reimbursement-policy review is required."))
    if invoice_count and not payment_evidence_exists:
        findings.append(ReviewFinding("PAYMENT_PROOF_MISSING", "warning", "Invoice records were found, but no reliable payment proof was detected."))
    if missing:
        findings.append(ReviewFinding("MISSING_CRITICAL_FIELDS", "error", "One or more records are missing amount, currency, or invoice date fields."))
    if filename_claim and filename_claim.claimed_total is not None:
        findings.append(ReviewFinding("FILENAME_NOT_APPROVAL_EVIDENCE", "info", "A filename total is treated only as a claim, never as approval evidence."))

    human_review = bool(findings or result.warnings or result.uncertain_fields)
    if human_review:
        findings.append(ReviewFinding("HUMAN_REVIEW_RECOMMENDED", "warning", "Human review is recommended before reimbursement approval."))

    return DeterministicReview(totals, len(records), invoice_count, payment_proof_count, missing, multiple_currencies, payment_evidence_exists, filename_total_match, multiple_currencies, human_review, findings)


def records_dataframe(result: ReimbursementExtractionResult) -> pd.DataFrame:
    rows = []
    for record in result.records:
        rows.append({
            "Source file": record.source_file,
            "Document type": record.document_type,
            "Invoice number": record.invoice_number,
            "Date": record.document_date,
            "Amount": record.amount,
            "Currency": record.currency,
            "Seller or counterparty": record.seller_or_counterparty,
            "Payment proof": "yes" if record.payment_proof_found else "no",
            "Warnings": "; ".join(record.warnings),
        })
    return pd.DataFrame(rows)


def records_csv_bytes(result: ReimbursementExtractionResult) -> bytes:
    return records_dataframe(result).to_csv(index=False).encode("utf-8-sig")


def result_json_bytes(result: ReimbursementExtractionResult, review: DeterministicReview) -> bytes:
    payload = result.model_dump(mode="json")
    payload["deterministic_review"] = review.to_dict()
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")

