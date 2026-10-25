# CareBridge AI — Team DUALITH

**Swim with Tiny Fish Hackathon** · Samrudh N. and Khyati Agarwal  
**Tagline:** One Patient. One Journey. Connected Care.

CareBridge AI is a healthcare-information navigation prototype for hospital
access, medicine and blood resources, registered clinical trials, and Indian
government healthcare assistance.

## Search modes and limitations

- **Synthetic demo** returns fictional examples from `backend/app/services/demo_data.py`.
  These records are not providers, sources, or availability claims.
- **Live sources** uses the TinyFish Search API to find source listings for the
  selected workflow. Results include source URLs, returned snippets and
  retrieval timestamps when available. A listing is **not independently
  verified**.
- Addresses, phone numbers, stock, recruitment, eligibility, and document
  requirements are only shown when actually returned by a source. This
  integration currently relies on TinyFish's search-result fields and does not
  independently extract every such detail from provider pages.
- Search results do not guarantee appointments, medicine or blood stock,
  clinical-trial eligibility, or scheme approval. The app does not diagnose,
  prescribe, determine medical suitability, or make eligibility decisions.
- Do not enter patient-identifying or sensitive health information. This is
  not an emergency service; seek local emergency care when needed.

## Structure

```text
backend/   FastAPI API, TinyFish Search integration, and synthetic fixtures
frontend/  React + Vite responsive application
```

## Run locally

Requirements: Python 3.11+, Node.js 20.19+ (or 22.12+), and npm.

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Live mode needs a TinyFish API key set **in the backend environment only**:

```bash
export TINYFISH_API_KEY="your-tinyfish-api-key"
```

Set it before starting Uvicorn. Never add the key to frontend files, Vite
variables, source control, or API requests. Without it, live searches return an
explicit service-unavailable response; demo mode remains available.

API docs: http://127.0.0.1:8000/docs  
Health check: http://127.0.0.1:8000/api/health

### Frontend (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open the local Vite URL, usually http://127.0.0.1:5173. Vite proxies `/api`
requests to the local backend. For a separately hosted API, configure
`VITE_API_BASE_URL` with its base URL before starting/building the frontend.
Never place the TinyFish key in a `VITE_*` variable.

## API

- `GET /api/health`
- `GET /api/workflows`
- `POST /api/search`

Example body:

```json
{
  "workflow": "medicine_blood",
  "query": "O-negative blood near Bengaluru",
  "location": "Bengaluru",
  "mode": "live"
}
```

Use `mode: "demo"` for explicitly labeled synthetic records or `mode: "live"`
for the TinyFish Search API. Live provider errors return an explicit HTTP error;
an empty provider response returns an empty, `NOT VERIFIED` result rather than
demo data.

## Tests

Run the backend tests from `backend/`:

```bash
python -m unittest discover -s tests
```

Build the frontend from `frontend/`:

```bash
npm run build
```
