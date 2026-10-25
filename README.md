CareBridge AI
 Source-Aware Healthcare Information Discovery

TinyFish Hackathon Project | Team DUALITH**

CareBridge AI is a healthcare information discovery platform that helps users navigate fragmented healthcare resources through a unified, workflow-driven interface. By integrating TinyFish Search with a React frontend and FastAPI backend, the platform retrieves relevant web listings across hospital access, medicine and blood resources, clinical trials, and healthcare financial assistance.

The project focuses on simplifying healthcare information discovery while maintaining source transparency and distinguishing live search results from synthetic demonstration data.

---

 1. Problem Statement

Healthcare information is distributed across hospital websites, public registries, blood-bank portals, and government scheme platforms. Finding relevant information across these sources can be time-consuming, particularly when users do not know which organizations or websites to consult.

CareBridge AI addresses this discovery challenge by bringing multiple healthcare information workflows into a single interface.

 2. Proposed Solution

CareBridge AI provides a unified search experience organized around four healthcare domains. Users select a workflow, describe their information needs, specify a location where relevant, and review structured results with source links and follow-up guidance.

The platform uses TinyFish Search to retrieve relevant online listings. Results are presented as information for further investigation, not as independently verified medical or provider claims.

 3. Core Capabilities

 Hospital Access
Discover hospital websites, healthcare facilities, departments, and provider contact information where available from returned sources.

 Medicine & Blood Resources
Discover blood banks, blood donation services, and relevant medicine-related information. Current stock and availability must be confirmed directly with providers.

 Clinical Trial Discovery
Find public clinical-trial registry listings and source links to support further review by users and qualified healthcare professionals.

 Healthcare Financial Assistance
Discover government healthcare schemes, official information portals, published eligibility criteria, and application resources where available.

 Source-Aware Results
- Structured result cards with titles and descriptions.
- Original source links where returned by the search service.
- Search timestamps and explicit result statuses.
- Recommended follow-up actions.
- Separate live-search and synthetic-demo modes.
- Clear notices about the limits of search-based information.

 4. System Architecture

```text
┌──────────────────────────────┐
│           User               │
└──────────────┬───────────────┘
               │ Search request
               ▼
┌──────────────────────────────┐
│    React + Vite Frontend     │
└──────────────┬───────────────┘
               │ HTTP API request
               ▼
┌──────────────────────────────┐
│       FastAPI Backend        │
│                              │
│ Request validation           │
│ Workflow routing             │
│ Response structuring         │
└──────────────┬───────────────┘
               │ Live search request
               ▼
┌──────────────────────────────┐
│       TinyFish Search        │
└──────────────┬───────────────┘
               │ Returned listings
               ▼
┌──────────────────────────────┐
│ Structured source results    │
│ and follow-up guidance       │
└──────────────────────────────┘
```

The backend also supports a demonstration mode that uses synthetic records. These records are intended for interface demonstration and must not be interpreted as live search findings.

 5. Technology Stack

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React | User interface and workflow interaction |
| Frontend tooling | Vite | Development server and production build |
| Backend | Python, FastAPI | API routes and search orchestration |
| Data validation | Pydantic | Request and response validation |
| Search integration | TinyFish Python SDK | Live web search |
| Version control | Git, GitHub | Source management and collaboration |

 6. Repository Structure

```text
CareBridgeAI-Repository/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── demo_data.py
│   │       └── tinyfish_client.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md
```

*Repository layout shown for documentation; verify it against the committed source tree.*

 7. Installation and Setup

 Prerequisites
- Python version compatible with the backend dependencies.
- Node.js and npm.
- A TinyFish API key for live-search functionality.

 Step 1 — Clone the repository

```bash
git clone https://github.com/samrudh-source/CareBridge-AI.git
cd CareBridge-AI/CareBridgeAI-Repository
```

 Step 2 — Configure the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure the API key in the backend terminal:

```bash
export TINYFISH_API_KEY="YOUR_TINYFISH_API_KEY"
```

Replace the placeholder locally with your actual key. Do not commit API credentials to source control.

 Step 3 — Run the backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

FastAPI interactive documentation:

`http://localhost:8000/docs`

 Step 4 — Run the frontend

Open a second terminal from the repository root:

```bash
cd CareBridge-AI/CareBridgeAI-Repository/frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the local URL displayed by Vite. In GitHub Codespaces, use the forwarded frontend port and ensure the frontend is configured to reach the backend through its accessible URL.

 8. API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Backend health information |
| `GET` | `/api/workflows` | Available healthcare workflows |
| `POST` | `/api/search` | Submit a healthcare information search |

 Example Request

```json
{
  "workflow": "hospital_access",
  "query": "hospitals in Bengaluru",
  "location": "Bengaluru, India",
  "mode": "live"
}
```

Supported workflow identifiers:

- `hospital_access`
- `medicine_blood`
- `clinical_trials`
- `financial_assistance`

The request and response schemas define the accepted fields and returned result structure.

## 9. Responsible Use and Data Limitations

CareBridge AI supports information discovery. It does not provide medical diagnosis, prescribe treatment, or replace qualified healthcare professionals.

- Search listings are not a guarantee that every claim is accurate or current.
- A hospital listing does not establish appointment availability.
- A blood-bank or medicine listing does not establish current stock.
- A clinical-trial listing does not establish eligibility or medical suitability.
- Published scheme information does not guarantee eligibility or approval.
- Users should verify critical information with the original source or relevant provider.

Live results must remain distinguishable from synthetic demonstration records. Search failures and empty responses should be reported transparently rather than represented as successful live findings.

 10. Security Considerations

- Store API credentials in environment variables or an appropriate secrets manager.
- Never expose the TinyFish API key in frontend code.
- Exclude `.env` files, virtual environments, dependency folders, and other sensitive or generated files from Git.
- Avoid logging secrets or returning credentials in API responses.

 11. Future Development

Potential areas for further development include:

- Improved relevance ranking and duplicate-result filtering.
- More consistent extraction of provider contact information.
- Stronger prioritization of official healthcare and government sources.
- Expanded automated tests for live search, empty results, and service failures.
- Improved deployment configuration, accessibility, and mobile responsiveness.
- Additional validation of source freshness and information quality.

These items represent potential enhancements, not necessarily completed features.

## 12. Team

**Team Name:** DUALITH

Contributors
- Samrudh N.
- Khyati Agarwal

Project Objective

CareBridge AI explores how source-aware web search can make healthcare information discovery more organized, accessible, and transparent.

CareBridge AI — Bridging the gap between people and healthcare information.
