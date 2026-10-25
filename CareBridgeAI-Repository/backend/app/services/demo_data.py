from datetime import datetime, timezone

TITLES = {
    "hospital_access": "Hospital access",
    "medicine_blood": "Medicine & blood",
    "clinical_trials": "Clinical-trial discovery",
    "financial_assistance": "Financial assistance",
}
DESCRIPTIONS = {
    "hospital_access": "Explore hospital departments and official contact pathways.",
    "medicine_blood": "Explore provider listings; availability must be confirmed directly.",
    "clinical_trials": "Review public registry listings with the treating clinician.",
    "financial_assistance": "Review official scheme information and required documents.",
}
SAFETY_NOTICE = ("Information-navigation prototype only. Not medical advice. Confirm details with the "
                 "responsible provider or authority. Do not rely on this demo for urgent care.")

def synthetic_results(workflow: str, query: str, location: str) -> list[dict]:
    """Fictional fixtures only; no live sources are checked in demo mode."""
    checked = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = {
        "status": "SYNTHETIC DEMO",
        "verification_status": "SYNTHETIC DEMO",
        "source_url": None,
        "checked_at": checked,
        "synthetic": True,
    }
    examples = {
        "hospital_access": [
            ("Sample Hospital Listing A", f"Illustrative placeholder for {location}; no bed, specialist or appointment availability is verified.", "Open an official hospital source and contact the hospital to confirm."),
            ("Sample Hospital Listing B", "Synthetic example only; not a real hospital recommendation.", "Confirm the relevant department and current availability directly."),
        ],
        "medicine_blood": [
            ("Sample Blood Bank Listing A", f"Synthetic example related to: {query}. No blood units or stock are confirmed.", "Contact a licensed blood bank/provider directly; do not rely on this sample."),
            ("Sample Pharmacy Listing B", "Synthetic example only. Medicine stock and suitability are not verified.", "Confirm stock with the provider and consult a qualified clinician/pharmacist."),
        ],
        "clinical_trials": [
            ("Sample Clinical-Trial Registry Entry", "Illustrative placeholder, not a real registry record or eligibility assessment.", "Search an official trial registry and discuss candidate listings with the treating clinician."),
        ],
        "financial_assistance": [
            ("Sample Healthcare Assistance Programme", "Synthetic placeholder. No eligibility, funding or approval is confirmed.", "Check the official scheme source and confirm requirements with the authority."),
        ],
    }
    return [{**base, "title": title, "summary": summary, "next_step": next_step}
            for title, summary, next_step in examples[workflow]]
