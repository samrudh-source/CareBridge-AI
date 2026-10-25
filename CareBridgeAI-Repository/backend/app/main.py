
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import SearchRequest, SearchResponse
from app.services.demo_data import (
    TITLES,
    DESCRIPTIONS,
    SAFETY_NOTICE,
    synthetic_results,
)
from app.services.tinyfish_client import run_live_task

app = FastAPI(
    title="CareBridge AI API",
    description=(
        "Healthcare information discovery using source listings "
        "and clearly labeled demo data."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"^https://[a-z0-9-]+\.app\.github\.dev$",
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "CareBridge AI API",
        "live_tinyfish_enabled": bool(
            os.getenv("TINYFISH_API_KEY", "").strip()
        ),
        "note": (
            "Live search requires the TinyFish SDK and a valid server-side "
            "TINYFISH_API_KEY. "
            "Search listings do not verify medical availability "
            "or eligibility."
        ),
    }


@app.get("/api/workflows")
def workflows():
    return [
        {
            "id": key,
            "title": title,
            "description": DESCRIPTIONS[key],
        }
        for key, title in TITLES.items()
    ]


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    if request.mode == "live":
        live_response = await run_live_task(
            request.workflow,
            request.query,
            request.location,
        )

        # Return the actual TinyFish response, not demo fixtures.
        return SearchResponse(**live_response)

    return SearchResponse(
        workflow=request.workflow,
        mode="demo",
        query=request.query,
        location=request.location,
        overall_status="SYNTHETIC DEMO",
        message=(
            f"{TITLES[request.workflow]} demo response. "
            "These records are synthetic placeholders, "
            "not live source findings."
        ),
        results=synthetic_results(
            request.workflow,
            request.query,
            request.location,
        ),
        safety_notice=SAFETY_NOTICE,
    )
