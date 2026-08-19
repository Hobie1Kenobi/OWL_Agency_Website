import unittest

from services.citation_parser import infer_toa_group, parse_citations


CARPENTER_EXCERPT = """
SAMPLE — NOT A REAL FILING
The Fourth Amendment protects people, not places. Katz v. United States, 389 U.S. 347 (1967).
Historical cell-site location information is a carrier business record and may therefore be obtained without a warrant under the third-party doctrine. Carpenter v. United States, 585 U.S. 946 (2018).
The Stored Communications Act authorizes certain disclosures. 18 U.S.C. § 2703. Search practice also implicates Fed. R. Crim. P. 41.
The court of appeals had allowed the records to stand. United States v. Carpenter, 819 F.3d 880 (6th Cir. 2016). The Supreme Court later issued the controlling decision, also reported at 138 S. Ct. 2206 (2018).
Trial courts must exclude any research produced by a language model. Harmon v. Northern Circuit, 112 F.4th 441 (9th Cir. 2024).
Additional support is said to appear in In re Application for Historical CSLI, No. 16-mc-01234 (S.D.N.Y. 2016). Counsel also relies on Smith, 442 U.S., without completing the reporter citation.
U.S. Const. amend. IV.
"""


class CitationParserTests(unittest.TestCase):
    def test_extracts_scotus_statute_rule_fake_docket_and_short_form(self):
        found = parse_citations(CARPENTER_EXCERPT)
        keys = {item["key"] for item in found}
        kinds = {item["key"]: item["kind"] for item in found}
        self.assertIn("389 U.S. 347", keys)
        self.assertIn("585 U.S. 946", keys)
        self.assertIn("138 S. Ct. 2206", keys)
        self.assertIn("819 F.3d 880", keys)
        self.assertIn("112 F.4th 441", keys)
        statute = next(item for item in found if item["kind"] == "statute")
        self.assertEqual(str(statute["title"]), "18")
        self.assertEqual(statute["section"].rstrip("."), "2703")
        self.assertEqual(infer_toa_group(statute), "statutes_rules")
        self.assertIn("Fed. R. Crim. P. 41", keys)
        self.assertIn("U.S. Const. amend. IV", keys)
        self.assertIn("No. 16-mc-01234", keys)
        self.assertIn("442 U.S.", keys)
        self.assertEqual(kinds["112 F.4th 441"], "case")
        self.assertEqual(kinds["No. 16-mc-01234"], "docket")
        self.assertEqual(kinds["442 U.S."], "ambiguous")
        carpenter = next(item for item in found if item["key"] == "585 U.S. 946")
        self.assertIn("without a warrant", carpenter["proposition"] or "")

    def test_toa_groups(self):
        found = parse_citations(CARPENTER_EXCERPT)
        grouped = {item["key"]: infer_toa_group(item) for item in found}
        self.assertEqual(grouped["585 U.S. 946"], "us_supreme_court")
        self.assertEqual(grouped["819 F.3d 880"], "courts_of_appeals")
        statute = next(item for item in found if item["kind"] == "statute")
        self.assertEqual(infer_toa_group(statute), "statutes_rules")
        self.assertEqual(grouped["442 U.S."], "unresolved")
        self.assertEqual(grouped["No. 16-mc-01234"], "unresolved")


if __name__ == "__main__":
    unittest.main()
