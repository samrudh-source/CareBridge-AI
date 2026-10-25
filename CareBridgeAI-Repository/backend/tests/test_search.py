import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi import HTTPException
from tinyfish._utils.exceptions import SDKError

from app.main import app
from app.services.tinyfish_client import run_live_task


class FakeSearch:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.arguments = None

    async def query(self, *args, **kwargs):
        self.arguments = (args, kwargs)
        if self.error:
            raise self.error
        return self.response


class FakeTinyFish:
    def __init__(self, search):
        self.search = search

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return None


def search_result(
    title="Official result",
    url="https://health.example.gov.in/hospital",
    snippet="Details published by the source.",
    site_name="Health Department",
    date="2026-10-24",
):
    return SimpleNamespace(
        title=title,
        url=url,
        snippet=snippet,
        site_name=site_name,
        date=date,
    )


class LiveSearchTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"TINYFISH_API_KEY": "test-key"})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def run_search(self, search, workflow="hospital_access"):
        fake_client = FakeTinyFish(search)
        client_patch = patch(
            "app.services.tinyfish_client.AsyncTinyFish",
            return_value=fake_client,
        )
        client_patch.start()
        self.addCleanup(client_patch.stop)
        result = asyncio.run(
            run_live_task(workflow, "cardiology services", "Bengaluru")
        )
        return result, search

    def test_live_success_uses_workflow_purpose_and_source_fields(self):
        search = FakeSearch(
            SimpleNamespace(
                results=[
                    search_result(
                        url="https://www.example.gov.in/hospital",
                    ),
                    search_result(
                        title="Other source",
                        url="https://private.example/hospital",
                    ),
                ]
            )
        )

        response, search = self.run_search(search)
        result = response["results"][0]

        self.assertEqual(response["mode"], "live")
        self.assertEqual(response["overall_status"], "LIVE SOURCE LISTING")
        self.assertEqual(result["status"], "LIVE SOURCE LISTING")
        self.assertEqual(result["verification_status"], "NOT VERIFIED")
        self.assertEqual(result["source_name"], "Health Department")
        self.assertEqual(result["description"], "Details published by the source.")
        self.assertEqual(result["source_date"], "2026-10-24")
        self.assertTrue(result["checked_at"])
        self.assertEqual(result["source_url"], "https://www.example.gov.in/hospital")
        self.assertIsNone(result["address"])
        self.assertIsNone(result["phone"])
        self.assertFalse(result["synthetic"])

        query, options = search.arguments
        self.assertIn("cardiology services", query[0])
        self.assertIn("Bengaluru", query[0])
        self.assertIn("India", query[0])
        self.assertIn("official hospitals", options["purpose"])
        self.assertEqual(options["location"], "Bengaluru, India")

    def test_duplicate_sources_are_removed_and_official_sources_are_prioritized(self):
        search = FakeSearch(
            SimpleNamespace(
                results=[
                    search_result(
                        title="General result",
                        url="https://private.example/hospital",
                    ),
                    search_result(
                        title="Official result",
                        url="https://health.example.gov.in/hospital?utm_source=test",
                    ),
                    search_result(
                        title="Duplicate",
                        url="https://health.example.gov.in/hospital",
                    ),
                ]
            )
        )

        response, _ = self.run_search(search)

        self.assertEqual(len(response["results"]), 2)
        self.assertEqual(response["results"][0]["title"], "Official result")

    def test_empty_results_are_an_explicit_unverified_empty_response(self):
        response, _ = self.run_search(FakeSearch(SimpleNamespace(results=[])))

        self.assertEqual(response["results"], [])
        self.assertEqual(response["overall_status"], "NOT VERIFIED")
        self.assertIn("no usable source listings", response["message"])

    def test_provider_error_is_reported_without_leaking_provider_details(self):
        with self.assertRaises(HTTPException) as error:
            self.run_search(FakeSearch(error=SDKError("secret provider detail")))

        self.assertEqual(error.exception.status_code, 502)
        self.assertNotIn("secret provider detail", str(error.exception.detail))

    def test_malformed_search_response_is_reported(self):
        with self.assertRaises(HTTPException) as error:
            self.run_search(FakeSearch(SimpleNamespace(results="not-a-list")))

        self.assertEqual(error.exception.status_code, 502)
        self.assertIn("malformed", error.exception.detail["message"])

    def test_malformed_result_records_are_not_presented(self):
        with self.assertRaises(HTTPException) as error:
            self.run_search(
                FakeSearch(
                    SimpleNamespace(
                        results=[search_result(url="javascript:alert(1)")]
                    )
                )
            )

        self.assertEqual(error.exception.status_code, 502)
        self.assertIn("no usable source records", error.exception.detail["message"])

    def test_missing_api_key_is_an_explicit_service_error(self):
        with patch.dict(os.environ, {"TINYFISH_API_KEY": ""}):
            with self.assertRaises(HTTPException) as error:
                asyncio.run(
                    run_live_task(
                        "hospital_access",
                        "cardiology services",
                        "Bengaluru",
                    )
                )

        self.assertEqual(error.exception.status_code, 503)
        self.assertIn("not configured", error.exception.detail["message"])


class SearchRouteTests(unittest.TestCase):
    @staticmethod
    async def post_search(payload):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post("/api/search", json=payload)

    def test_demo_mode_returns_only_labeled_synthetic_records(self):
        response = asyncio.run(
            self.post_search(
                {
                    "workflow": "medicine_blood",
                    "query": "O-negative blood",
                    "location": "Bengaluru",
                    "mode": "demo",
                }
            )
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "demo")
        self.assertEqual(payload["overall_status"], "SYNTHETIC DEMO")
        self.assertTrue(payload["results"])
        self.assertTrue(all(item["synthetic"] for item in payload["results"]))
        self.assertTrue(
            all(
                item["verification_status"] == "SYNTHETIC DEMO"
                for item in payload["results"]
            )
        )

    def test_live_mode_serializes_source_listing_from_tinyfish(self):
        fake_search = FakeSearch(
            SimpleNamespace(results=[search_result()])
        )
        fake_client = FakeTinyFish(fake_search)
        with (
            patch.dict(os.environ, {"TINYFISH_API_KEY": "test-key"}),
            patch(
                "app.services.tinyfish_client.AsyncTinyFish",
                return_value=fake_client,
            ),
        ):
            response = asyncio.run(
                self.post_search(
                    {
                        "workflow": "hospital_access",
                        "query": "cardiology",
                        "location": "Bengaluru",
                        "mode": "live",
                    }
                )
            )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["mode"], "live")
        self.assertEqual(payload["results"][0]["status"], "LIVE SOURCE LISTING")
        self.assertIsNone(payload["results"][0]["phone"])


if __name__ == "__main__":
    unittest.main()
