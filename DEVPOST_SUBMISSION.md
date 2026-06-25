# Devpost Submission: ClaimLens — Gemini-Powered Reimbursement Document Review

## Project Name

ClaimLens — Gemini-Powered Reimbursement Document Review: Multimodal Reimbursement Review

## Elevator Pitch

Gemini-powered reimbursement review that turns PDFs and invoice images into validated JSON, finance tables, and deterministic risk checks.

## Inspiration

Reimbursement review is slow because evidence is fragmented across invoices, screenshots, payment records, statements, and filenames. Finance reviewers need to compare visual layouts, totals, currencies, dates, and payment proof. ClaimLens — Gemini-Powered Reimbursement Document Review was built to show how Gemini multimodal understanding can transform messy reimbursement evidence into a clear, auditable workflow.

## What It Does

ClaimLens — Gemini-Powered Reimbursement Document Review lets users upload redacted reimbursement PDFs or images. Gemini reads document content and layout, classifies document types, extracts reimbursement fields, and returns structured JSON. Pydantic validates the response, then Python calculates deterministic checks such as totals by currency, missing critical fields, payment-proof completeness, filename-total comparison, and whether human review is recommended.

The Streamlit interface displays metrics, records, warnings, layout findings, validated JSON, and downloadable CSV/JSON exports.

## How We Built It

We built a Streamlit application with the official Google Gen AI Python SDK, using `gemini-2.5-flash` for multimodal document understanding. The extraction response is constrained by Pydantic models. Pandas powers the records table and CSV export. Python review rules handle arithmetic and risk checks after extraction. Secrets are configured through local environment variables or Streamlit Community Cloud Secrets.

The implementation uses one strong Gemini extraction call for document understanding, then keeps financial review calculations deterministic.

## Challenges We Faced

- Designing a schema strict enough for finance review but flexible enough for messy documents.
- Avoiding false confidence when fields are missing or uncertain.
- Keeping cached sample mode clearly separate from live Gemini mode.
- Treating filename totals as claims instead of proof.
- Supporting PDFs and images without permanently storing uploads.

## Accomplishments

- Built a working Streamlit prototype ready for deployment.
- Integrated real Gemini API use through the official SDK.
- Added structured JSON output and Pydantic validation.
- Added deterministic checks for currencies, totals, payment proof, and human review.
- Added CSV and JSON exports.
- Prepared tests, README, video script, and Devpost copy.

## What We Learned

Gemini is valuable when reimbursement evidence is visual and contextual, not just text. Layout, tables, labels, and screenshots all matter. We also learned that financial applications need deterministic post-processing: Gemini extracts and explains, while Python verifies totals and risk conditions.

## What Is Next

- Add policy profiles for universities, research labs, and enterprise finance teams.
- Add exchange-rate evidence and conversion review.
- Add reviewer notes and decision logging.
- Add more redacted benchmark documents.
- Add privacy-focused pre-upload redaction checks.

## Built With

- Gemini API
- `gemini-2.5-flash`
- Google Gen AI Python SDK (`google-genai`)
- Streamlit
- Python
- Pydantic
- Pandas
- python-dotenv
- Pytest

## Gemini API Usage Explanation

ClaimLens — Gemini-Powered Reimbursement Document Review sends uploaded PDFs and images to Gemini using the official `google-genai` SDK. Gemini performs multimodal document understanding: it reads text, visual layout, tables, labels, currency symbols, page structure, and relationships between invoice and payment fields. The response is constrained to a Pydantic-backed structured JSON schema, then validated before the app displays metrics, tables, warnings, and exports.

The model used is `gemini-2.5-flash`.

## Image Gallery Checklist

- Upload screen with file list and privacy notice.
- Live Gemini review status.
- Extracted records table.
- Risk and deterministic review summary.
- Validated JSON expandable section.
- CSV/JSON download buttons.

## Video Link Placeholder

YOUR_YOUTUBE_URL

## Project Links

- Live demo: YOUR_STREAMLIT_URL
- GitHub: YOUR_GITHUB_URL
- Hackathon: https://build-with-gemini-0.devpost.com/
