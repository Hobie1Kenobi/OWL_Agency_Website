from __future__ import annotations

import asyncio
import unittest

from services.citation_verify import (
    cl_result_matches,
    evaluate_citation,
    openjurist_opinion_url,
    overall_status,
    query_courtlistener,
    source_covers,
)


def _source(source_id: str, status: str, matched: bool, http_status=None, excerpt="", covers=True, url=None):
    return {
        "id": source_id,
        "name": source_id,
        "status": status,
        "http_status": http_status,
        "error": None if matched else status,
        "url": url if url is not None else ("https://example.test/" + source_id),
        "matched": matched,
        "excerpt": excerpt,
        "covers": covers,
        "link_ok": matched,
    }


WURIE = {
    "kind": "case",
    "key": "728 F.3d 1",
    "raw": "United States v. Wurie, 728 F.3d 1 (1st Cir. 2013)",
    "span": "United States v. Wurie, 728 F.3d 1 (1st Cir. 2013)",
    "parties": "United States v. Wurie",
    "volume": "728",
    "reporter": "F.3d",
    "page": "1",
    "year": 2013,
    "proposition": "The First Circuit reached the same conclusion for a flip phone seized at arrest.",
}


class EvaluateCitationTests(unittest.TestCase):
    def test_fake_cite_fails_existence_when_sources_respond(self):
        cite = {
            "kind": "case",
            "key": "112 F.4th 441",
            "raw": "Harmon v. Northern Circuit, 112 F.4th 441 (9th Cir. 2024)",
            "span": "Harmon v. Northern Circuit, 112 F.4th 441 (9th Cir. 2024)",
            "parties": "Harmon v. Northern Circuit",
            "volume": "112",
            "reporter": "F.4th",
            "page": "441",
            "year": 2024,
            "proposition": "Trial courts must exclude language-model research.",
        }
        sources = [
            _source("cornell_lii", "no_match", False, 404, covers=False),
            _source("oyez", "no_match", False, 404, covers=False),
            _source("courtlistener", "no_match", False, 200),
            _source("openjurist", "no_match", False, 404),
            _source("justia", "no_match", False, 404, covers=False),
            _source("govinfo", "no_match", False, 404, covers=False),
            _source("supremecourt_gov", "no_match", False, None, covers=False),
        ]
        result = evaluate_citation(cite, sources, 0)
        self.assertEqual(result["error"], "not_found")
        existence = next(item for item in result["checks"] if item["id"] == "existence")
        self.assertEqual(existence["status"], "fail")
        self.assertEqual(overall_status(result), "fail")

    def test_total_outage_is_unavailable_not_not_found(self):
        cite = {
            "kind": "case",
            "key": "585 U.S. 946",
            "raw": "Carpenter v. United States, 585 U.S. 946 (2018)",
            "span": "Carpenter v. United States, 585 U.S. 946 (2018)",
            "volume": "585",
            "reporter": "U.S.",
            "page": "946",
            "year": 2018,
            "proposition": "Warrant required.",
        }
        sources = [
            _source("cornell_lii", "timeout", False),
            _source("oyez", "blocked", False, 403),
            _source("courtlistener", "timeout", False),
            _source("justia", "error", False),
            _source("govinfo", "timeout", False),
            _source("supremecourt_gov", "timeout", False),
        ]
        result = evaluate_citation(cite, sources, 0)
        self.assertEqual(result["error"], "source_unavailable")
        existence = next(item for item in result["checks"] if item["id"] == "existence")
        self.assertEqual(existence["status"], "needs-review")

    def test_wrong_carpenter_holding_fails_when_excerpt_discusses_warrant(self):
        cite = {
            "kind": "case",
            "key": "585 U.S. 946",
            "raw": "Carpenter v. United States, 585 U.S. 946 (2018)",
            "span": "Carpenter v. United States, 585 U.S. 946 (2018)",
            "volume": "585",
            "reporter": "U.S.",
            "page": "946",
            "year": 2018,
            "proposition": "Historical cell-site records may therefore be obtained without a warrant under the third-party doctrine.",
        }
        sources = [
            _source(
                "cornell_lii",
                "ok",
                True,
                200,
                excerpt="The Government's acquisition of historical cell-site records is a search. Police must get a warrant.",
            ),
            _source("oyez", "ok", True, 200, excerpt="cell-site location warrant"),
            _source("courtlistener", "no_match", False, 404),
            _source("justia", "no_match", False, 404),
            _source("govinfo", "no_match", False, 404),
            _source("supremecourt_gov", "ok", True, 200),
        ]
        result = evaluate_citation(cite, sources, 0)
        holding = next(item for item in result["checks"] if item["id"] == "holding_support")
        self.assertEqual(holding["status"], "fail")
        existence = next(item for item in result["checks"] if item["id"] == "existence")
        self.assertEqual(existence["status"], "pass")

    def test_wurie_exists_when_courtlistener_api_matches(self):
        sources = [
            _source("cornell_lii", "no_match", False, 200, covers=False),
            _source("oyez", "no_match", False, None, covers=False),
            _source(
                "courtlistener",
                "ok",
                True,
                200,
                excerpt="This case requires us to decide whether the police, after seizing a cell phone",
                url="https://www.courtlistener.com/opinion/870435/united-states-v-wurie/",
            ),
            _source(
                "openjurist",
                "ok",
                True,
                200,
                excerpt="United States v. Wurie 728 F.3d 1",
                url="https://openjurist.org/728/f3d/1",
            ),
            _source("justia", "blocked", False, 403, covers=False),
            _source("govinfo", "no_match", False, None, covers=False),
            _source("supremecourt_gov", "no_match", False, None, covers=False),
        ]
        result = evaluate_citation(WURIE, sources, 0)
        self.assertIsNone(result["error"])
        existence = next(item for item in result["checks"] if item["id"] == "existence")
        self.assertEqual(existence["status"], "pass")
        self.assertEqual(
            result["authority_url"],
            "https://www.courtlistener.com/opinion/870435/united-states-v-wurie/",
        )
        self.assertNotIn("/c/F.3d/", result["authority_url"])
        holding = next(item for item in result["checks"] if item["id"] == "holding_support")
        self.assertEqual(holding["status"], "needs-review")
        path_urls = [step.get("url") for step in result["verification_path"] if step.get("url")]
        self.assertTrue(all("/c/" not in url for url in path_urls))

    def test_circuit_covering_outage_is_unavailable_not_fake(self):
        sources = [
            _source("cornell_lii", "no_match", False, 200, covers=False),
            _source("oyez", "no_match", False, None, covers=False),
            _source("courtlistener", "timeout", False),
            _source("openjurist", "timeout", False),
            _source("justia", "blocked", False, 403, covers=False),
            _source("govinfo", "no_match", False, None, covers=False),
            _source("supremecourt_gov", "no_match", False, None, covers=False),
        ]
        result = evaluate_citation(WURIE, sources, 0)
        self.assertEqual(result["error"], "source_unavailable")
        existence = next(item for item in result["checks"] if item["id"] == "existence")
        self.assertEqual(existence["status"], "needs-review")
        self.assertNotEqual(result["error"], "not_found")


class ReporterHelpersTests(unittest.TestCase):
    def test_openjurist_url_for_wurie_and_riley(self):
        self.assertEqual(openjurist_opinion_url(WURIE), "https://openjurist.org/728/f3d/1")
        riley = {"kind": "case", "volume": "573", "reporter": "U.S.", "page": "373"}
        self.assertEqual(openjurist_opinion_url(riley), "https://openjurist.org/573/us/373")
        carpenter_sct = {"kind": "case", "volume": "138", "reporter": "S. Ct.", "page": "2206"}
        self.assertEqual(openjurist_opinion_url(carpenter_sct), "https://openjurist.org/138/sct/2206")
        self.assertIsNone(openjurist_opinion_url({"kind": "statute", "reporter": "U.S.C."}))

    def test_source_coverage_for_circuit_vs_scotus(self):
        self.assertTrue(source_covers("courtlistener", WURIE))
        self.assertTrue(source_covers("openjurist", WURIE))
        self.assertFalse(source_covers("oyez", WURIE))
        self.assertFalse(source_covers("supremecourt_gov", WURIE))
        self.assertFalse(source_covers("govinfo", WURIE))
        scotus = {"kind": "case", "reporter": "U.S.", "volume": "573", "page": "373"}
        self.assertTrue(source_covers("oyez", scotus))
        self.assertTrue(source_covers("cornell_lii", scotus))
        self.assertFalse(source_covers("cornell_lii", WURIE))

    def test_cl_result_requires_exact_citation(self):
        wurie_row = {"citation": ["728 F.3d 1", "2013 WL 2129119"], "caseName": "United States v. Wurie"}
        self.assertTrue(cl_result_matches(WURIE, wurie_row))
        other = {"citation": ["573 F. Supp. 373"], "caseName": "Alexander v. Alexander"}
        riley = {"kind": "case", "key": "573 U.S. 373", "volume": "573", "reporter": "U.S.", "page": "373"}
        self.assertFalse(cl_result_matches(riley, other))


class CourtListenerQueryTests(unittest.TestCase):
    def test_api_match_returns_opinion_url_not_constructed_c_path(self):
        class _Resp:
            def __init__(self, payload):
                self.status_code = 200
                self._payload = payload

            def json(self):
                return self._payload

        class _Client:
            def __init__(self):
                self.urls = []

            async def get(self, url, headers=None, follow_redirects=None):
                self.urls.append(url)
                return _Resp(
                    {
                        "count": 2,
                        "results": [
                            {
                                "absolute_url": "/opinion/870435/united-states-v-wurie/",
                                "caseName": "United States v. Wurie",
                                "citation": ["728 F.3d 1"],
                                "opinions": [
                                    {
                                        "snippet": "This case requires us to decide whether the police, after seizing a cell phone."
                                    }
                                ],
                            }
                        ],
                    }
                )

        client = _Client()
        result = asyncio.run(query_courtlistener(client, WURIE))
        self.assertTrue(result["matched"])
        self.assertEqual(result["url"], "https://www.courtlistener.com/opinion/870435/united-states-v-wurie/")
        self.assertTrue(any("api/rest/v4/search" in url for url in client.urls))
        self.assertFalse(any("/c/F.3d/" in url for url in client.urls))

    def test_api_empty_is_no_match_without_dead_url(self):
        class _Resp:
            status_code = 200

            def json(self):
                return {"count": 0, "results": []}

        class _Client:
            async def get(self, url, headers=None, follow_redirects=None):
                return _Resp()

        result = asyncio.run(query_courtlistener(_Client(), {
            "kind": "case",
            "key": "112 F.4th 441",
            "raw": "Harmon v. Northern Circuit, 112 F.4th 441 (9th Cir. 2024)",
            "parties": "Harmon v. Northern Circuit",
            "volume": "112",
            "reporter": "F.4th",
            "page": "441",
        }))
        self.assertFalse(result["matched"])
        self.assertEqual(result["status"], "no_match")
        self.assertIsNone(result["url"])


if __name__ == "__main__":
    unittest.main()
