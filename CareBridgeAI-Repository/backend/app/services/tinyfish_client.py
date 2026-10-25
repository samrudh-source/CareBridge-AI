import os
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from fastapi import HTTPException
from pydantic import ValidationError
from tinyfish import AsyncTinyFish
from tinyfish._utils.exceptions import SDKError


WORKFLOW_SEARCH = {
    "hospital_access": {
        "query_terms": (
            "hospital department services official hospital website India "
            "government AIIMS NIMHANS Karnataka"
        ),
        "purpose": (
            "Find official hospitals and department pages relevant to the "
            "request. Prioritize government and hospital-owned websites; "
            "return only source-supported contact and location details."
        ),
        "official_domains": (
            "gov.in",
            "nic.in",
            "aiims.edu",
            "nimhans.ac.in",
            "sctimst.ac.in",
        ),
        "next_step": (
            "Open the hospital's official page and contact its department "
            "to confirm services and current availability."
        ),
    },
    "medicine_blood": {
        "query_terms": (
            "licensed blood bank e-RaktKosh medicine information official "
            "India CDSCO"
        ),
        "purpose": (
            "Find official e-RaktKosh or licensed blood-bank listings and "
            "reliable medicine information relevant to the request. Never "
            "treat a listing as confirmation of stock or suitability."
        ),
        "official_domains": (
            "eraktkosh.in",
            "gov.in",
            "nic.in",
            "cdsco.gov.in",
            "who.int",
        ),
        "next_step": (
            "Contact the listed provider to confirm current stock, and ask a "
            "qualified clinician or pharmacist about medicine use."
        ),
    },
    "clinical_trials": {
        "query_terms": (
            "registered clinical trial ClinicalTrials.gov CTRI India WHO ICTRP "
            "recruitment location"
        ),
        "purpose": (
            "Find registered clinical-trial records relevant to the request. "
            "Prioritize ClinicalTrials.gov, India's CTRI, WHO ICTRP, and "
            "official registry pages. Report recruitment and eligibility "
            "only as stated by the source; do not assess suitability."
        ),
        "official_domains": (
            "clinicaltrials.gov",
            "ctri.nic.in",
            "who.int",
            "gov.in",
            "nic.in",
        ),
        "next_step": (
            "Review the original registry record with the trial team and "
            "treating clinician; the listing does not determine eligibility."
        ),
    },
    "financial_assistance": {
        "query_terms": (
            "PM-JAY Arogya Karnataka Indian and Karnataka government "
            "healthcare scheme eligibility application documents official portal"
        ),
        "purpose": (
            "Find official Indian or Karnataka government healthcare "
            "assistance schemes relevant to the request. Prioritize official "
            "scheme portals and report eligibility and document requirements "
            "only when published by the source."
        ),
        "official_domains": (
            "pmjay.gov.in",
            "arogyakarnataka.gov.in",
            "karnataka.gov.in",
            "services.india.gov.in",
            "nhm.gov.in",
            "gov.in",
            "nic.in",
        ),
        "next_step": (
            "Open the official scheme portal and confirm current eligibility "
            "and required documents with the administering authority."
        ),
    },
}


def _field(item: Any, name: str) -> Any:
    if isinstance(item, Mapping):
        return item.get(name)
    return getattr(item, name, None)


def _source_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    url = value.strip()
    try:
        parsed = urlsplit(url)
    except ValueError:
        return None
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
    ):
        return None
    return url


def _canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not key.lower().startswith("utm_")
    ]
    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            urlencode(sorted(query)),
            "",
        )
    )


def _is_official_source(url: str, workflow: str) -> bool:
    hostname = (urlsplit(url).hostname or "").lower()
    return any(
        hostname == domain or hostname.endswith(f".{domain}")
        for domain in WORKFLOW_SEARCH[workflow]["official_domains"]
    )


def _text(value: Any, limit: int) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value[:limit] if value else None


async def run_live_task(workflow: str, query: str, location: str) -> dict[str, Any]:
    config = WORKFLOW_SEARCH.get(workflow)
    if config is None:
        raise HTTPException(
            status_code=400,
            detail="Unsupported healthcare workflow.",
        )

    api_key = os.getenv("TINYFISH_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "NOT VERIFIED",
                "message": "Live search is unavailable: TINYFISH_API_KEY is not configured.",
            },
        )

    search_query = (
        f"{query.strip()} {config['query_terms']} "
        f"{location.strip()} India"
    )
    try:
        async with AsyncTinyFish(
            api_key=api_key,
            timeout=30,
            max_retries=1,
        ) as client:
            response = await client.search.query(
                search_query,
                purpose=config["purpose"],
                location=f"{location.strip()}, India",
                language="en",
            )
    except (SDKError, httpx.HTTPError, ValidationError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "status": "NOT VERIFIED",
                "message": (
                    "TinyFish live search failed. Check backend connectivity, "
                    "API-key configuration, and TinyFish account access."
                ),
            },
        ) from exc

    raw_results = _field(response, "results")
    if not isinstance(raw_results, Sequence) or isinstance(
        raw_results, (str, bytes, bytearray)
    ):
        raise HTTPException(
            status_code=502,
            detail={
                "status": "NOT VERIFIED",
                "message": (
                    "TinyFish returned a malformed search response. "
                    "No results were presented."
                ),
            },
        )

    checked_at = datetime.now(timezone.utc).isoformat()
    candidates: list[tuple[bool, dict[str, Any]]] = []
    seen_urls: set[str] = set()
    malformed_count = 0

    for item in raw_results:
        title = _text(_field(item, "title"), 300)
        source_url = _source_url(_field(item, "url"))
        if not title or not source_url:
            malformed_count += 1
            continue

        canonical_url = _canonical_url(source_url)
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)

        description = _text(
            _field(item, "snippet") or _field(item, "description"),
            1500,
        )
        source_name = _text(
            _field(item, "site_name") or _field(item, "publisher"),
            200,
        )
        source_date = _text(_field(item, "date"), 100)
        candidates.append(
            (
                _is_official_source(source_url, workflow),
                {
                    "title": title,
                    "provider_name": None,
                    "source_name": source_name,
                    "description": description,
                    "summary": description,
                    "address": None,
                    "phone": None,
                    "location": None,
                    "recruitment_status": None,
                    "eligibility": None,
                    "documents_required": None,
                    "status": "LIVE SOURCE LISTING",
                    "verification_status": "NOT VERIFIED",
                    "source_url": source_url,
                    "source_date": source_date,
                    "checked_at": checked_at,
                    "synthetic": False,
                    "next_step": config["next_step"],
                },
            )
        )

    if raw_results and not candidates and malformed_count:
        raise HTTPException(
        status_code=502,
        detail={
            "status": "NOT VERIFIED",
            "message": (
                "TinyFish returned no usable source records. "
                "No results were presented."
            ),
        },
        )

    candidates.sort(key=lambda candidate: not candidate[0])
    results = [result for _, result in candidates[:8]]

    return {
        "workflow": workflow,
        "mode": "live",
        "query": query,
        "location": location,
        "overall_status": (
            "LIVE SOURCE LISTING" if results else "NOT VERIFIED"
        ),
        "message": (
            "Live source listings were returned. Their content and current "
            "availability have not been independently verified."
            if results
            else "TinyFish returned no usable source listings. No findings "
            "could be verified."
        ),
        "results": results,
        "safety_notice": (
            "Information discovery only, not medical advice. Search results "
            "do not guarantee appointment availability, blood or medicine "
            "stock, clinical-trial eligibility, or scheme approval."
        ),
    }
