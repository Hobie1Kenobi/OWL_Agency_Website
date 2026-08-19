from __future__ import annotations

import unittest

from services.citation_verify import evaluate_citation, overall_status


def _source(source_id: str, status: str, matched: bool, http_status=None, excerpt=""):
    return {
        "id": source_id,
        "name": source_id,
        "status": status,
        "http_status": http_status,
        "error": None if matched else status,
        "url": "https://example.test/" + source_id,
        "matched": matched,
        "excerpt": excerpt,
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
            _source("cornell_lii", "no_match", False, 404),
            _source("oyez", "no_match", False, 404),
            _source("courtlistener", "no_match", False, 404),
            _source("justia", "no_match", False, 404),
            _source("govinfo", "no_match", False, 404),
            _source("supremecourt_gov", "no_match", False, None),
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


if __name__ == "__main__":
    unittest.main()
