# ReimBand Gemini

### Multimodal Reimbursement Review Powered by Gemini

ReimBand Gemini is a multimodal reimbursement review assistant that transforms invoices, receipts, payment records, and PDF files into structured, reviewable financial data.

Instead of relying on a single chatbot to approve or reject a reimbursement request, ReimBand separates the workflow into three specialized stages:

1. **Document Intake**
2. **Policy Review**
3. **Audit Review**

The system uses Gemini’s multimodal document understanding and structured outputs to identify missing evidence, detect cross-currency risks, explain inconsistencies, and recommend when human review is required.

> ReimBand Gemini Edition evolved from an earlier reimbursement workflow prototype. The Gemini-powered multimodal pipeline, structured extraction, policy review, and audit reasoning were developed for the Build with Gemini hackathon.

---

## Live Demo

* **Streamlit Demo:** [Open ReimBand Gemini](YOUR_STREAMLIT_DEMO_URL)
* **Demo Video:** [Watch the presentation](YOUR_VIDEO_URL)

Replace the placeholder URLs above with the final public links.

---

## Inspiration

Reimbursement review is a real but often overlooked workflow problem.

Finance teams need to inspect:

* Invoices and receipts
* Payment records
* Amounts and currencies
* Supporting documents
* Reimbursement policies
* Missing or inconsistent evidence
* Cross-currency transactions

This process is repetitive, slow, and easy to get wrong, especially when documents use different layouts, contain multiple currencies, or do not include complete payment evidence.

We wanted to explore whether Gemini could do more than summarize a document. Our goal was to use Gemini’s multimodal capabilities to turn complex reimbursement files into structured data and then use specialized review stages to explain risks and recommend next actions.

---

## What ReimBand Does

A user uploads a redacted:

* PDF
* Invoice image
* Receipt
* Bank statement
* Payment record
* Supporting reimbursement document

Gemini analyzes both the visual layout and textual content of the uploaded document.

It extracts structured reimbursement information such as:

* Document type
* Invoice number
* Invoice date
* Amount
* Currency
* Seller or counterparty
* Payment-proof status
* Claimed total
* Detected currencies
* Uncertain fields
* Risk warnings

The extracted data is then passed through three specialized review stages.

---

## Review Workflow

### 1. Document Intake

The Document Intake stage reads the uploaded PDF or image and converts it into structured reimbursement records.

It identifies:

* Invoice and payment information
* Amounts and currencies
* Document categories
* Counterparties
* Missing fields
* Uncertain values
* Initial risk warnings

This stage extracts and normalizes information but does not make the final reimbursement decision.

### 2. Policy Review

The Policy Review stage checks whether the case contains the evidence normally required for reimbursement.

It evaluates:

* Required supporting documents
* Missing payment evidence
* Cross-currency review requirements
* Blocking issues
* Policy completeness
* Recommended next steps

### 3. Audit Review

The Audit Review stage performs the final consistency and risk assessment.

It checks:

* Amount consistency
* Currency consistency
* Payment-proof status
* Missing supporting materials
* Conflicting records
* Risk level
* Whether human review is required

The final result may recommend:

* Approval
* Recheck
* Additional document upload
* Human review

---

## Example Scenario

The demonstration case uses the following redacted file:

```text
demo_case_02_mar30_mar31_total_1990_20_minimal_redacted.pdf
```

The file name indicates a claimed total of:

```text
1990.20 CNY
```

However, the uploaded material also contains USD invoice records.

ReimBand Gemini identifies that:

* Multiple currencies are present
* Cross-currency review is required
* Payment evidence may be missing or insufficient
* The claimed total should not be automatically approved
* A human reviewer should verify the payment record and exchange-rate evidence

This prevents the application from making unsupported financial decisions.

---

## How We Built It

ReimBand Gemini is built with Python and Streamlit.

The application uses the official Google Gen AI SDK to send uploaded PDFs and images to the Gemini API.

Gemini performs:

* Multimodal PDF understanding
* Image and invoice interpretation
* Financial field extraction
* Structured JSON generation
* Policy completeness reasoning
* Audit and risk reasoning

Instead of requesting a general natural-language response, the application defines explicit schemas for the intake, policy, and audit stages.

The returned data is validated before being displayed in the interface.

This makes the output easier to:

* Display
* Compare
* Pass between review stages
* Export as CSV
* Audit
* Integrate with future finance systems

---

## Application Interface

The Streamlit interface displays:

* Uploaded document information
* Live or cached processing mode
* Gemini model information
* Extracted reimbursement records
* Amount and currency summaries
* Policy findings
* Missing supporting documents
* Audit risks and explanations
* Recommended next actions
* Downloadable CSV results

The interface is designed as a lightweight finance workflow rather than a general-purpose chatbot.

---

## Live and Cached Modes

ReimBand Gemini supports two processing modes.

### Live Gemini Mode

When a valid Gemini API key is configured, the application sends the uploaded document to Gemini for real multimodal analysis.

Live results are clearly labeled:

```text
LIVE GEMINI REVIEW
```

### Cached Demo Mode

A redacted cached case is included so the demonstration remains available when the Gemini API is unavailable or no API key is configured.

Cached results are clearly labeled:

```text
CACHED DEMO RESULT
```

Cached responses are never presented as live Gemini output.

---

## Key Features

* Multimodal PDF and image understanding
* Structured financial-data extraction
* Invoice and payment-record analysis
* Cross-currency risk detection
* Payment-proof checking
* Multi-stage policy and audit reasoning
* Explainable risk decisions
* Human-in-the-loop recommendations
* Live and cached demo modes
* CSV export
* Streamlit web interface
* Redacted and synthetic demonstration data

---

## Challenges

### Inconsistent Document Formats

Invoices use different layouts, date formats, currencies, field names, and visual structures.

Gemini’s multimodal understanding helps interpret both document text and layout, but the extracted results still need to be normalized into a consistent schema.

### Claimed Totals Versus Detected Records

A file name may contain a claimed reimbursement total that does not directly match the records detected inside the document.

ReimBand treats the file name as supporting context rather than verified financial evidence.

### Cross-Currency Review

The demo case includes a claimed total in CNY while some invoice records are in USD.

The system must flag this for exchange-rate and payment-proof verification instead of automatically comparing the numbers.

### Preventing Unsupported Decisions

Financial workflows require caution.

To reduce unsupported conclusions, ReimBand separates:

* Extraction
* Policy checking
* Audit reasoning

Each stage must identify uncertainty, missing evidence, and human-review requirements.

### Privacy and Deployment

Financial documents may contain sensitive information.

The online demo therefore uses:

* Redacted files
* Synthetic records
* Environment variables
* Streamlit secrets
* Cached fallback data
* No committed API keys

---

## Accomplishments

ReimBand Gemini is not just a document chatbot.

It demonstrates an end-to-end operational workflow:

* Multimodal document understanding
* Structured reimbursement extraction
* Cross-currency risk detection
* Payment-evidence checking
* Multi-stage policy and audit reasoning
* Explainable human-review recommendations
* CSV export
* Accessible online deployment

The project shows how Gemini can support real workflows where accuracy, traceability, and uncertainty handling matter.

---

## What We Learned

### Multimodal Understanding Matters

Important reimbursement information is often distributed across:

* Text
* Tables
* Images
* Layout
* File names
* Multiple document pages

A multimodal model can reason across these different sources more effectively than a text-only pipeline.

### Structured Outputs Are Essential

A natural-language answer may appear convincing but is difficult to validate or integrate into a workflow.

Validated structured outputs are easier to:

* Display
* Store
* Compare
* Export
* Pass between stages
* Review programmatically

### AI Should Not Blindly Approve Financial Claims

A useful finance assistant should explain:

* What it detected
* What remains uncertain
* Which evidence is missing
* Why a case is risky
* When human review is required

ReimBand is designed to support human reviewers rather than replace financial accountability.

---

## Technology Stack

* **Gemini API**
* **Google Gen AI SDK**
* **Python**
* **Streamlit**
* **Pandas**
* **Pydantic**
* **JSON Schema**
* **GitHub**
* **Streamlit Community Cloud**
* **Multimodal PDF Processing**
* **Structured Outputs**

---

## Project Structure

```text
reimband-gemini/
├── streamlit_app.py
├── gemini_client.py
├── schemas.py
├── prompts/
│   ├── intake.md
│   ├── policy.md
│   └── audit.md
├── demo_data/
│   ├── demo_records.csv
│   └── demo_agent_review.json
├── assets/
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── .dockerignore
└── README.md
```

The exact structure may differ slightly depending on the deployed version.

---

## Local Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file or configure Streamlit secrets.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit this file to GitHub.

### 5. Start the application

```bash
streamlit run streamlit_app.py
```

The application should open at:

```text
http://localhost:8501
```

---

## Streamlit Community Cloud Deployment

1. Upload the project to a public GitHub repository.
2. Sign in to Streamlit Community Cloud.
3. Select **Create app**.
4. Choose the repository and branch.
5. Select the application entry file:

```text
streamlit_app.py
```

6. Open **Advanced settings**.
7. Add the Gemini API key to Streamlit secrets:

```toml
GEMINI_API_KEY = "your_gemini_api_key"
```

8. Click **Deploy**.

Never add the real key to:

* `README.md`
* `.env.example`
* Python source files
* GitHub commits
* Screenshots

---

## Security and Privacy

This repository must not contain:

* Real API keys
* Band credentials
* Private invoices
* Bank-account information
* Unredacted payment screenshots
* Personal financial documents

The public demo uses only redacted or synthetic data.

API credentials should be stored in:

* Environment variables
* Local `.env` files excluded by `.gitignore`
* Streamlit secrets
* Cloud secret-management services

---

## Future Roadmap

Future development may include:

* A larger reimbursement-policy knowledge base
* More invoice and payment-document formats
* Improved multi-document matching
* Exchange-rate evidence and currency conversion
* Printable reimbursement packs
* Persistent audit histories
* User authentication
* Enterprise finance-system integration
* Google Cloud Run deployment
* Database-backed review records
* Human approval and escalation workflows

Our long-term goal is to make reimbursement review faster without sacrificing transparency, traceability, or human oversight.

---

## Hackathon

ReimBand Gemini Edition was developed for the **Build with Gemini** hackathon.

The Gemini-specific work includes:

* Multimodal document processing
* Structured reimbursement extraction
* Policy review
* Audit reasoning
* Cross-currency risk analysis
* Gemini-powered live review
* Structured output validation

---

## License

This project is provided for hackathon demonstration and educational purposes.

See the repository’s `LICENSE` file for details.
