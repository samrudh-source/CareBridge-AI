from typing import Literal

from pydantic import BaseModel, Field, field_validator

Workflow = Literal["hospital_access", "medicine_blood", "clinical_trials", "financial_assistance"]
Mode = Literal["demo", "live"]

class SearchRequest(BaseModel):
    workflow: Workflow
    query: str = Field(min_length=3, max_length=500)
    location: str = Field(default="Bengaluru", min_length=2, max_length=120)
    mode: Mode = "demo"

    @field_validator("query", "location", mode="before")
    @classmethod
    def trim_text(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ResultItem(BaseModel):
    title: str
    provider_name: str | None = None
    source_name: str | None = None
    description: str | None = None
    summary: str | None = None
    address: str | None = None
    phone: str | None = None
    location: str | None = None
    recruitment_status: str | None = None
    eligibility: str | None = None
    documents_required: str | None = None
    status: Literal[
        "SYNTHETIC DEMO",
        "SOURCE LISTING",
        "LIVE SOURCE LISTING",
        "LIVE CHECK COMPLETED",
        "NEEDS CONFIRMATION",
        "NOT VERIFIED",
    ]
    verification_status: Literal[
        "SYNTHETIC DEMO",
        "NOT VERIFIED",
        "VERIFIED",
    ] | None = None
    source_url: str | None = None
    source_date: str | None = None
    checked_at: str | None = None
    synthetic: bool = False
    next_step: str | None = None

class SearchResponse(BaseModel):
    workflow: Workflow
    mode: Mode
    query: str
    location: str
    overall_status: str
    message: str
    results: list[ResultItem]
    safety_notice: str
