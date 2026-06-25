from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from pydantic import ValidationError

from file_utils import UploadedDocument, parse_filename_claim, validate_upload_batch
from gemini_client import GeminiExtractionError, GeminiNotConfigured, configured_api_key, configured_model, extract_reimbursement
from review_rules import evaluate_reimbursement, records_csv_bytes, records_dataframe, result_json_bytes
from schemas import ReimbursementExtractionResult

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_RESULT_PATH = PROJECT_ROOT / "sample_data" / "sample_result.json"
MODEL_NAME = configured_model(getattr(st, "secrets", None))

st.set_page_config(page_title="ClaimLens — Gemini-Powered Reimbursement Document Review", page_icon="CL", layout="wide")

st.markdown("""
<style>
.main .block-container {max-width: 1220px; padding-top: 1.8rem; padding-bottom: 3rem;}
.cl-header {border: 1px solid #d9e2ec; background: #ffffff; border-radius: 8px; padding: 24px 28px;}
.cl-title {font-size: 2.6rem; line-height: 1.05; margin: 0; color: #111827; font-weight: 760; letter-spacing: 0;}
.cl-subtitle {font-size: 1.1rem; color: #64748b; margin-top: 6px;}
.cl-badge {display: inline-block; border: 1px solid #bfdbfe; background: #eff6ff; color: #1e40af; border-radius: 999px; padding: 5px 10px; font-size: 0.82rem; font-weight: 700; margin-right: 8px;}
.cl-live {border-left: 5px solid #0f766e; background: #ecfdf5; color: #134e4a; padding: 12px 14px; border-radius: 8px; font-weight: 740;}
.cl-missing {border-left: 5px solid #b45309; background: #fffbeb; color: #78350f; padding: 12px 14px; border-radius: 8px; font-weight: 740;}
.cl-sample {border-left: 5px solid #1d4ed8; background: #eff6ff; color: #1e3a8a; padding: 12px 14px; border-radius: 8px; font-weight: 740;}
.cl-finding {border: 1px solid #fed7aa; background: #fff7ed; color: #9a3412; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px;}
div[data-testid="stMetricValue"] {font-weight: 760;}
</style>
""", unsafe_allow_html=True)


def load_sample_result() -> ReimbursementExtractionResult:
    try:
        return ReimbursementExtractionResult.model_validate_json(SAMPLE_RESULT_PATH.read_text(encoding="utf-8"))
    except (OSError, ValidationError) as exc:
        st.error(f"Sample result could not be loaded safely: {exc}")
        st.stop()


def st_secrets_dict() -> dict:
    try:
        return dict(st.secrets)
    except Exception:
        return {}


def make_uploaded_documents(uploaded_files) -> list[UploadedDocument]:
    documents: list[UploadedDocument] = []
    for uploaded in uploaded_files or []:
        documents.append(UploadedDocument(name=uploaded.name, mime_type=uploaded.type, data=uploaded.getvalue()))
    return documents


def display_file_list(documents: list[UploadedDocument]) -> None:
    if not documents:
        st.info("Upload up to 3 redacted reimbursement files to begin.")
        return
    rows = [{"File": doc.name, "Type": doc.mime_type, "Size MB": round(doc.size_mb, 2)} for doc in documents]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def display_results(result: ReimbursementExtractionResult, mode_label: str, filename_claim) -> None:
    review = evaluate_reimbursement(result, filename_claim)
    df = records_dataframe(result)
    if mode_label == "live":
        st.markdown("<div class='rg-live'>LIVE GEMINI REVIEW</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='rg-sample'>SAMPLE / CACHED RESULT - NOT A LIVE GEMINI RESPONSE</div>", unsafe_allow_html=True)

    st.write("")
    metric_cols = st.columns(7)
    metric_cols[0].metric("Files processed", len(result.source_files))
    metric_cols[1].metric("Records", review.record_count)
    metric_cols[2].metric("Invoices", review.invoice_count)
    totals_text = ", ".join(f"{currency} {amount:,.2f}" for currency, amount in review.totals_by_currency.items()) or "None"
    metric_cols[3].metric("Total by currency", totals_text)
    metric_cols[4].metric("Payment proof", "Found" if review.payment_evidence_exists else "Missing")
    metric_cols[5].metric("Risk count", len(review.findings))
    metric_cols[6].metric("Recommendation", "Human review" if review.human_review_recommended else "Ready for review")

    st.subheader("Structured Records Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    left, right = st.columns([1, 1])
    with left:
        st.subheader("Layout and Extraction Findings")
        st.markdown("**Layout observations**")
        st.write(result.layout_observations or ["No layout observations returned."])
        st.markdown("**Uncertain fields**")
        st.write(result.uncertain_fields or ["No uncertain fields reported."])
        st.markdown("**Gemini warnings**")
        st.write(result.warnings or ["No Gemini warnings reported."])
    with right:
        st.subheader("Review Summary")
        st.write({
            "cross_currency_review": review.cross_currency_review_required,
            "payment_proof_complete": review.payment_evidence_exists,
            "filename_total_match": review.filename_total_match,
            "missing_fields": review.missing_critical_fields,
            "human_review_recommended": review.human_review_recommended,
        })
        for finding in review.findings:
            st.markdown(f"<div class='rg-finding'><strong>{finding.code}</strong>: {finding.message}</div>", unsafe_allow_html=True)

    with st.expander("Validated structured JSON", expanded=False):
        st.json(result.model_dump(mode="json"))

    export_cols = st.columns(2)
    export_cols[0].download_button("Download CSV", data=records_csv_bytes(result), file_name="claimlens_records.csv", mime="text/csv", use_container_width=True)
    export_cols[1].download_button("Download JSON", data=result_json_bytes(result, review), file_name="claimlens_review.json", mime="application/json", use_container_width=True)


st.markdown(f"""
<div class="cl-header">
  <span class="cl-badge">Powered by Gemini</span>
  <span class="cl-badge">Model: {MODEL_NAME}</span>
  <h1 class="cl-title">ClaimLens — Gemini-Powered Reimbursement Document Review</h1>
  <div class="cl-subtitle">Multimodal Reimbursement Review</div>
</div>
""", unsafe_allow_html=True)

st.write("")
left_col, right_col = st.columns([1.1, 0.9])

with left_col:
    st.subheader("Upload Reimbursement Evidence")
    uploaded_files = st.file_uploader("PDF/PNG/JPG/JPEG files", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, help="Use redacted documents only. Public demo limit: 3 files, 30 MB each.")
    documents = make_uploaded_documents(uploaded_files)
    display_file_list(documents)
    st.caption("Privacy: uploaded documents are sent to Gemini only when you click Run Gemini Review. The app does not permanently store uploads.")

with right_col:
    st.subheader("Processing Mode")
    api_key = configured_api_key(st_secrets_dict())
    if api_key:
        st.markdown("<div class='rg-live'>LIVE GEMINI REVIEW available</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='rg-missing'>GEMINI API KEY NOT CONFIGURED</div>", unsafe_allow_html=True)
        st.caption("Add GEMINI_API_KEY locally or in Streamlit Secrets. Sample mode is cached and explicitly labeled.")
    sample_clicked = st.button("Load Redacted Sample Result", use_container_width=True)

batch_errors = validate_upload_batch(documents) if documents else []
for error in batch_errors:
    st.error(error)

run_clicked = st.button("Run Gemini Review", type="primary", use_container_width=True, disabled=not documents or bool(batch_errors) or not api_key)

result: Optional[ReimbursementExtractionResult] = None
mode_label: Optional[str] = None
filename_claim = parse_filename_claim(documents[0].name) if documents else parse_filename_claim("demo_case_02_mar30_mar31_total_1990_20_minimal_redacted.pdf")

if sample_clicked:
    result = load_sample_result()
    mode_label = "sample"
elif run_clicked:
    status = st.status("Preparing Gemini review", expanded=True)
    try:
        status.write("1. Uploading document")
        status.write("2. Gemini document understanding")
        live_result = extract_reimbursement(documents, api_key=api_key, model=MODEL_NAME)
        status.write("3. Validating structured JSON")
        result = ReimbursementExtractionResult.model_validate(live_result.model_dump())
        status.write("4. Calculating totals and risks")
        evaluate_reimbursement(result, filename_claim)
        status.write("5. Preparing results")
        status.update(label="Gemini review complete", state="complete")
        mode_label = "live"
    except GeminiNotConfigured:
        status.update(label="Gemini API key missing", state="error")
        st.error("GEMINI_API_KEY is not configured. Live review was not run.")
    except GeminiExtractionError as exc:
        status.update(label="Gemini extraction failed safely", state="error")
        st.error(str(exc))
        st.info("No financial decision was made. You can retry after checking the file and configuration.")
    except Exception as exc:
        status.update(label="Review failed safely", state="error")
        st.error(f"Unexpected safe failure: {exc}")

if result and mode_label:
    st.divider()
    display_results(result, mode_label, filename_claim)
else:
    st.write("")
    st.info("Run a live Gemini review or explicitly load the redacted sample result to see metrics, tables, warnings, JSON, and exports.")
