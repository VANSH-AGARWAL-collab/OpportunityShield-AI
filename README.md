# OpportunityShield AI 🛡️
### *Forensic AI Opportunity Investigation Platform for Indian Students & Jobseekers*
**Built for the SerpApi India Hackathon 2026**  
**Primary Track:** Knowledge & Public Interest • **Secondary Track:** AI Agents

---

## 📌 Executive Summary

Every year, millions of Indian college students and early-career jobseekers fall victim to employment and internship fraud. Scammers exploit campus anxieties through:
- **Advance-Fee Laptop / Training Scams**: Demanding ₹2,000–₹5,000 "refundable security deposits" or courier fees via UPI before shipping dummy hardware.
- **Brand Impersonation & Phishing**: Operating lookalike typo domains (e.g., `tcs-careers-onboarding.in` instead of `tcs.com`) with spoofed offer letters.
- **Untraceable Messaging Channels**: Conducting mock interviews exclusively on Telegram channels or WhatsApp groups, then vanishing once payments are received.

**OpportunityShield AI** is a competition-ready, full-stack intelligence platform that acts as an automated forensic investigator. By orchestrating multi-engine searches across **SerpApi Google Search, Google News, and Google Jobs**, OpportunityShield AI extracts opportunity claims, cross-references digital footprints, analyzes scam disclosures, and synthesizes an explainable, auditable 7-section investigation dossier—**empowering applicants to verify before they trust.**

> *"Check the evidence before you trust an opportunity."*

---

## 🌟 Key Capabilities & Differentiators

| Feature | Description | Technical Implementation |
| :--- | :--- | :--- |
| **Multi-Engine SerpApi Intelligence** | Queries Google Search (official domain check & scam forums), Google News (press sentiment), and Google Jobs (market benchmark). | `services/serpapi_service.py` with multi-engine query orchestration, deduplication, and normalization. |
| **Real-Time Entity Extractor** | Parses unstructured job posts, offer letters, or emails to isolate companies, domains, recruiter webmail, roles, and payment red flags. | `services/extractor_service.py` with zero-latency preview as the user types. |
| **Auditable Heuristic Risk Engine** | Transparent 0–100 Risk Index with mathematical breakdown and cited evidence. No black-box hallucinations. | `services/investigation_engine.py` evaluates explicit rules (fee demands, lookalikes, Telegram channels, Knowledge Graph). |
| **Zero-Paid-API Resiliency** | Seamlessly works without paid LLM keys; includes curated synthetic benchmark simulation datasets accessible as a standalone demo mode. | `services/benchmark_data.py` containing 4 curated archetype cases. |
| **India-Specific Safeguards** | Features National Cyber Crime Reporting Portal (`cybercrime.gov.in`), Helpline `1930`, MCA21 incorporation checks, and Zero-Fee hiring directives. | Built directly into Section F of every investigation report and the Indian Safety Handbook modal. |
| **Persistent Investigation Dossiers** | Stores full historical investigations in SQLite for audit trails, comparison, PDF export, and markdown sharing. | `services/database.py` with full SQLite schema and REST API. |

---

## 🏗️ System Architecture

```
                          ┌───────────────────────────┐
                          │   Indian Jobseeker / User │
                          └─────────────┬─────────────┘
                                        │ (Paste Job Description or Offer Letter)
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │              OpportunityShield AI - Frontend Dashboard                 │
    │  - Real-time Entity Chip Preview    - Interactive Evidence Explorer    │
    │  - Agentic Multi-Step Visualizer    - 7-Section Dossier (Print/PDF)    │
    │  - Standalone Demo Mode Selector    - Clear Simulated/Live Badges      │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ JSON API Request
                                        ▼
    ┌────────────────────────────────────────────────────────────────────────┐
    │                      Flask REST Backend (app.py)                       │
    ├────────────────────────────────────────────────────────────────────────┤
    │  1. Extractor Service: Regex + NLP entity extraction & trigger alerts  │
    │  2. SerpApi Multi-Engine Search Orchestrator:                          │
    │     ├── Engine 1: Google Search (Official Domain + Knowledge Graph)    │
    │     ├── Engine 2: Google Search (Scam, Fraud & Consumer Complaints)    │
    │     ├── Engine 3: Google News (Recent Corporate Press Sentiment)       │
    │     └── Engine 4: Google Jobs (Role Verification & Market Benchmarks)  │
    │  3. Evidentiary Normalizer & Deduplicator                              │
    │  4. Explainable Heuristic Rule Engine (Transparent 0-100 Risk Index)   │
    │  5. SQLite Persistence Layer (Audit History & Dossier Archival)        │
    └───────────────────────────────────┬────────────────────────────────────┘
                                        │ HTTPS
                                        ▼
                          ┌───────────────────────────┐
                          │   SerpApi Official API    │
                          │   (Google Search/News/Jobs)
                          └───────────────────────────┘
```

---

## 📑 The 7-Section Investigation Report

Every completed investigation generates a comprehensive evidentiary dossier:

1. **Section A: Investigation Overview**: Opportunity title, target company, target domain, recruiter email, total sources retrieved, query latency, and index limitation disclaimers.
2. **Section B: Overall Assessment & Risk Gauge**:
   - Qualitative indicator: `Low observed concern` (🟢), `Needs further verification` (🟡), `Elevated concern` (🔴), or `Insufficient public evidence` (🟡).
   - Numerical 0–100 Risk Score with mathematical formula breakdown. **Important:** The risk score is an evidentiary indicator and decision-support metric, not definitive proof that an opportunity is legitimate or fraudulent.
   - Interactive factor cards showing each active rule, weight, rationale, nature tag, and cited source.
3. **Section C: Positive Signals**: Confirmation of indexed official domain, Google Knowledge Panel entity presence, active Google Jobs listings, or matching corporate email domains (all qualified as corporate entity existence signals, not proof of individual recruiter authorization).
4. **Section D: Warning Red Flags**: Explicit upfront fee/deposit demands, brand lookalike spoofing, free recruiter webmail (`@gmail.com`), Telegram-only interviews, or adverse press.
5. **Section E: Interactive Evidence Explorer**: Filterable by Engine (Google Search, Google News, Google Jobs) and Stance (Supports, Contradicts, Inconclusive), with direct external clickable links.
6. **Section F: Prioritized Applicant Checklist (India Guidelines)**: Actionable protocols including Helpline `1930`, `cybercrime.gov.in`, MCA21 incorporation checks, and LinkedIn verification.
7. **Section G: Comparable Opportunities & Market Benchmarks**: Comparable openings discovered via Google Jobs to benchmark legitimate role expectations.

---

## 🔬 Benchmark Archetypes Included (Simulated Demonstrations)

The platform includes four curated synthetic benchmark cases reflecting real-world recruitment challenges in India. All benchmark data consists of simulated demonstration fixtures and does not represent live search or verified real-world evidence:

| Benchmark Case | Target Entity | Scenario Archetype | Risk Score | Key Triggers Identified |
| :--- | :--- | :--- | :--- | :--- |
| **1. Laptop Deposit Scam** | Apex Tech Solutions | Advance-fee remote data entry fraud simulation | **98 / 100** (Elevated Concern) | Demands ₹2,500 UPI laptop deposit; `@gmail.com` HR; Telegram interview; consumer complaints found on Google. |
| **2. TCS Lookalike Phishing** | Tata Consultancy Services | Enterprise brand impersonation simulation | **88 / 100** (Elevated Concern) | Spoofed domain `tcs-careers-onboarding.in` vs official `tcs.com`; ₹4,999 onboarding fee. |
| **3. Legitimate Tech Startup** | Hasura | High-growth engineering role simulation | **12 / 100** (Low Concern) | Simulated Knowledge Panel presence; simulated Google Jobs listings; TechCrunch coverage sample; zero fee demands. |
| **4. Sparse Footprint Studio** | NovaSphere Media | Unregistered local boutique design shop simulation | **30 / 100** (Low Concern) | Sparse search indexing; no adverse complaints, but early-stage caution advised. |

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.11 recommended)
- Git

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/opportunity-shield-ai.git
cd opportunity-shield-ai

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure SerpApi Key

Create your local `.env` file from the provided `.env.example`:

```bash
cp .env.example .env
```

Open `.env` and insert your SerpApi key:

```env
# Get your free key at https://serpapi.com (250 free searches/month per hackathon terms; please confirm current account terms)
SERPAPI_KEY=your_actual_serpapi_key_here

# Application configuration (Debug disabled by default)
FLASK_DEBUG=0
PORT=5000
```

### 4. Operational Modes: Live vs. Benchmark Demonstration

OpportunityShield AI strictly distinguishes between live search intelligence and educational benchmark testing:

1. **Live SerpApi Search Mode (Active Key)**:
   - When `SERPAPI_KEY` is configured in `.env`, the platform dispatches real-time queries to Google Search (official domain check & scam complaint analysis), Google News (press sentiment), and Google Jobs (market comparability).
   - If an unconfigured key or network failure occurs during a search for an arbitrary real company, OpportunityShield AI **never substitutes a canned benchmark or invents fake search results**. Instead, it presents an honest `search_status: "unconfigured_key"` and an `Insufficient public evidence` assessment advising independent verification.
2. **Benchmark Demonstration Mode (Zero-Credit Exploration)**:
   - Evaluators can test the 4 curated scenario archetypes (Apex Scam, TCS Spoof, Hasura Legit, NovaSphere) without consuming SerpApi search credits.
   - All benchmark evidence items and job listings are transparently badged with `[Simulated Example]` and `Simulated benchmark fixture` timestamps to prevent misleading demo results.

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated Test Suite

Run the full automated test suite covering DNS label boundary matching, entity extraction, heuristic calculation, SerpApi query builders, and REST endpoints:

```bash
pytest -v
```

**Verified Test Execution Results (Python 3.11 / pytest 9.1.1):**
```
============================= test session starts =============================
platform win32 -- Python 3.11.6, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\SerpApi Hackathon project
collected 29 items

tests/test_api.py::test_index_route PASSED                               [  3%]
tests/test_api.py::test_api_status PASSED                                [  6%]
tests/test_api.py::test_api_benchmarks PASSED                            [ 10%]
tests/test_api.py::test_api_extract PASSED                               [ 13%]
tests/test_api.py::test_api_investigate_benchmark PASSED                 [ 17%]
tests/test_api.py::test_api_status_does_not_leak_keys PASSED             [ 20%]
tests/test_api.py::test_api_investigate_custom_company_without_key PASSED [ 24%]
tests/test_api.py::test_config_security_defaults PASSED                  [ 27%]
tests/test_extractor.py::test_clean_domain PASSED                        [ 31%]
tests/test_extractor.py::test_extract_entities_advance_fee_scam PASSED   [ 34%]
tests/test_extractor.py::test_extract_entities_brand_spoofing PASSED     [ 37%]
tests/test_extractor.py::test_extract_entities_legitimate_startup PASSED [ 41%]
tests/test_extractor.py::test_dns_label_matching_exact_and_subdomain PASSED [ 44%]
tests/test_extractor.py::test_dns_label_matching_prevents_malicious_suffix_and_lookalikes PASSED [ 48%]
tests/test_extractor.py::test_extract_entities_detects_malicious_suffix_spoof PASSED [ 51%]
tests/test_extractor.py::test_spoofed_enterprise_brand_domains PASSED    [ 55%]
tests/test_investigation.py::test_investigation_high_risk_scam PASSED    [ 58%]
tests/test_investigation.py::test_investigation_legitimate_startup PASSED [ 62%]
tests/test_investigation.py::test_investigation_insufficient_evidence_unconfigured_search PASSED [ 65%]
tests/test_investigation.py::test_investigation_zero_search_results_insufficient_evidence PASSED [ 68%]
tests/test_investigation.py::test_investigation_positive_signals_qualified_not_guarantee PASSED [ 72%]
tests/test_investigation.py::test_investigation_search_failed_returns_insufficient_evidence PASSED [ 75%]
tests/test_investigation.py::test_investigation_does_not_certify_offer_authentic PASSED [ 79%]
tests/test_serpapi.py::test_serpapi_benchmark_loading PASSED             [ 82%]
tests/test_serpapi.py::test_serpapi_unconfigured_key_does_not_fake_results PASSED [ 86%]
tests/test_serpapi.py::test_serpapi_all_searches_fail_does_not_fake_results PASSED [ 89%]
tests/test_serpapi.py::test_serpapi_explicit_benchmark_demonstration PASSED [ 93%]
tests/test_serpapi.py::test_serpapi_domain_extraction PASSED             [ 96%]
tests/test_serpapi.py::test_serpapi_news_classification_relevance_check PASSED [100%]

============================= 29 passed in 0.41s ==============================
```

Run benchmark scenario verification (runs in-process or against local HTTP):
```bash
python tests/verify_benchmarks.py
```

**Verified Benchmark Script Output:**
```
================================================================================
OpportunityShield AI - Automated Benchmark Verification
================================================================================
(*) Local HTTP server not running on port 5000; executing via Flask application context.
[APEX_SCAM       ] Apex Tech Solutions          | Score: 98/100 | Elevated concern          | [Simulated] | Warn: 4 | Pos: 0 | Sources: 5
[TCS_SPOOF       ] Tata Consultancy Services    | Score: 88/100 | Elevated concern          | [Simulated] | Warn: 2 | Pos: 2 | Sources: 6
[HASURA_LEGIT    ] Hasura                       | Score: 12/100 | Low observed concern      | [Simulated] | Warn: 1 | Pos: 4 | Sources: 6
[UNINDEXED_ENTITY] NovaSphere Media             | Score: 30/100 | Low observed concern      | [Simulated] | Warn: 1 | Pos: 2 | Sources: 2
================================================================================
All 4 benchmark archetypes verified successfully!
```

---

## 🛡️ Security, Privacy & Fairness Safeguards

1. **Strict DNS Label Boundary Verification**: Replaced naive substring matching with normalized hostname comparisons (`cand == auth or cand.endswith("." + auth)`). Malicious lookalikes such as `tcs.com.attacker.example` or `tcs-careers.in` are blocked from matching `tcs.com`.
2. **Contextual Signals vs. Absolute Fraud Accusations**: Free webmail (`@gmail.com`), Telegram interviews, and sparse search indices are treated as contextual risk indicators, not definitive proof of fraud. Emerging startups with minimal online records receive an `Insufficient public evidence` assessment with neutral disclaimers.
3. **Qualified Positive Signals**: Official domain matches, Knowledge Panels, and Google Jobs listings confirm organizational entity footprint, with explicit caveats noting that entity existence does not certify individual recruiter authorization.
4. **Target-Specific News Relevance**: News mentions of fraud or law enforcement action only affect risk scores if the target company is specifically named in the reporting.
5. **No Client-Side Secrets & Safe Defaults**: `SERPAPI_KEY` is strictly managed server-side and never exposed in HTML, client scripts, logs, or error responses. `/api/status` returns boolean availability only. Production defaults generate random secrets (`os.urandom(32).hex()`) and disable debug mode.
6. **Request Size Limits & Escaping**: 1 MB payload limits (`MAX_CONTENT_LENGTH`) prevent resource exhaustion, and dynamic text inputs are sanitized and escaped against XSS.

---

## 🤖 AI-Assisted Development Disclosure

In accordance with hackathon evaluation guidelines, development of OpportunityShield AI was assisted by generative AI tools (Anthropic Claude / Google DeepMind Agentic Pair Programming) for iterative code structuring, test generation, and documentation refinement. All domain logic, heuristic formulas, SerpApi orchestration routines, and security safeguards were manually reviewed, verified, and validated against live test executions.

---

## 📹 3-Minute Demo Video Script (Hackathon Submission)

- **[0:00 - 0:35] Problem**: Introduce the epidemic of fake internship offers and Telegram deposit scams in India. Show the first screen: *"Check the evidence before you trust an opportunity."*
- **[0:35 - 1:15] Investigation Flow**: Click the **Laptop Deposit Scam** benchmark (Apex Tech). Show real-time entity extraction chips updating automatically (Company, UPI deposit trigger, Telegram channel). Click **Launch Multi-Source Investigation**.
- **[1:15 - 1:55] SerpApi Live Engine In Action**: Watch the agentic progress tracker query Google Search (official), Google Search (scam complaints), Google News, and Google Jobs.
- **[1:55 - 2:35] Dossier Walkthrough**: Inspect Section B (Risk Score 98/100, formula breakdown), Section D (Warning red flags), Section E (Filterable Evidence Explorer with clickable links), and Section F (Helpline 1930 & MCA21 verification guide).
- **[2:35 - 3:00] Legitimate Comparison & Closing**: Contrast with the **Hasura** benchmark (Score 12/100, Knowledge Panel presence, active Google Jobs). Export the PDF report. Reiterate how SerpApi empowers public interest knowledge for Indian youth.

---

## 📦 Project Structure

```
├── .env.example                # Sample environment configuration
├── .env                        # Local environment file (ignored by git)
├── .gitignore                  # Safeguards secrets, SQLite DB, and caches
├── requirements.txt            # Python dependencies (Flask, Requests, Pytest)
├── config.py                   # Centralized configuration and secret loading
├── app.py                      # Flask entry point and REST API routes
├── services/
│   ├── __init__.py
│   ├── extractor_service.py    # Entity, contact, and red flag trigger extraction
│   ├── serpapi_service.py      # Multi-engine search, deduplication & fallback
│   ├── investigation_engine.py # Explainable heuristic risk scoring engine
│   ├── benchmark_data.py       # Curated realistic benchmark cases
│   └── database.py             # SQLite persistence layer for investigation history
├── static/
│   ├── css/
│   │   └── style.css           # Deep navy theme, high-contrast dossier, print styles
│   ├── js/
│   │   ├── app.js              # Application state, debounced extraction, animations
│   │   └── report.js           # 7-section report renderer, filters, markdown export
│   └── images/
│       └── logo.svg            # Custom vector shield logo
├── templates/
│   └── index.html              # Accessible dashboard shell with native dialogs
└── tests/
    ├── __init__.py
    ├── test_extractor.py       # Unit tests for entity extraction & spoof detection
    ├── test_investigation.py   # Unit tests for scoring logic & rule factors
    ├── test_serpapi.py         # Unit tests for SerpApi normalization & benchmarks
    ├── test_api.py             # Integration tests for Flask endpoints
    └── verify_benchmarks.py    # Automated end-to-end benchmark verification script
```

---

## ⚖️ License & Disclaimer

OpportunityShield AI is released under the **MIT License**.  
*Disclaimer: OpportunityShield AI provides automated evidentiary analysis based on publicly available search engine data. A risk score is an informational indicator and decision-support metric, not definitive proof that an opportunity is legitimate or fraudulent. Users should always exercise independent diligence before making financial or career decisions.*

