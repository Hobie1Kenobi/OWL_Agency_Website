"""Generate court-formatted legal documents for the Carpenter v. United States demo."""

from __future__ import annotations

from datetime import date
from typing import Any

from agents.base import PipelineState


def _caption(case: dict[str, Any]) -> str:
    return f"""UNITED STATES DISTRICT COURT
EASTERN DISTRICT OF MICHIGAN
SOUTHERN DIVISION

UNITED STATES OF AMERICA,
          Plaintiff,
     v.                                      Case No. 2:12-cr-00202
TIMOTHY IVAN CARPENTER, et al.,
          Defendants.

____________________________________/"""


def generate_all_documents(case: dict[str, Any], state: PipelineState) -> dict[str, str]:
    today = date.today().strftime("%B %d, %Y")
    return {
        "legal_research_memorandum": _research_memo(case, today),
        "case_brief": _case_brief(case),
        "motion_to_suppress": _motion_to_suppress(case, today),
        "appellate_brief_excerpt": _appellate_brief_excerpt(case),
        "table_of_authorities": _table_of_authorities(case),
        "certificate_of_service": _certificate_of_service(case, today),
    }


def _research_memo(case: dict[str, Any], today: str) -> str:
    scenario = case["demo_scenario"]
    precedents = "\n".join(
        f"  • {p['case']}, {p['citation']} — {p['principle']}" for p in case["key_precedents"]
    )
    return f"""{_caption(case)}

                    CONFIDENTIAL ATTORNEY WORK PRODUCT
                    LEGAL RESEARCH MEMORANDUM

TO:         Criminal Defense Team
FROM:       OWL Paralegal Research System — Research Agent
DATE:       {today}
RE:         {scenario['research_question']}
CLIENT:     {scenario['client_name']}

────────────────────────────────────────────────────────────────────────
QUESTION PRESENTED
────────────────────────────────────────────────────────────────────────

{case['issue']}

────────────────────────────────────────────────────────────────────────
BRIEF ANSWER
────────────────────────────────────────────────────────────────────────

Yes. In {case['full_name']}, {case['citation']}, the Supreme Court held ({case['vote']}) that
the Government's acquisition of {scenario['research_question'].split('127 days')[0] if '127' in scenario['research_question'] else 'historical '}
cell-site location information from wireless carriers is a Fourth Amendment search requiring a
warrant supported by probable cause. SCA orders under 18 U.S.C. § 2703(d) are constitutionally
insufficient for extended CSLI.

────────────────────────────────────────────────────────────────────────
FACTS
────────────────────────────────────────────────────────────────────────

{case['facts_summary']}

────────────────────────────────────────────────────────────────────────
DISCUSSION
────────────────────────────────────────────────────────────────────────

I.  Fourth Amendment Framework

The Fourth Amendment protects "[t]he right of the people to be secure in their persons, houses,
papers, and effects, against unreasonable searches and seizures." U.S. Const. amend. IV. Under
Katz v. United States, 389 U.S. 347 (1967), a search occurs when government conduct violates a
subjective expectation of privacy that society recognizes as reasonable.

II.  Digital Privacy and Location Tracking

In United States v. Jones, 565 U.S. 400 (2012), five Justices agreed that long-term GPS monitoring
of a vehicle constitutes a search. Riley v. California, 573 U.S. 373 (2014), recognized that cell
phones contain "the privacies of life" and require a warrant for content searches incident to arrest.

III. Application to CSLI

Historical CSLI — which can reconstruct a person's movements with precision over weeks or months —
implicates the same privacy interests. The Court declined to extend Smith v. Maryland, 442 U.S. 735
(1979), and United States v. Miller, 425 U.S. 435 (1976), to "the qualitatively different category
of cell-site records."

IV.  Warrant Requirement

Police must generally obtain a warrant supported by probable cause before acquiring seven days or
more of historical CSLI. {case['holding']}

────────────────────────────────────────────────────────────────────────
CONTROLLING AUTHORITIES
────────────────────────────────────────────────────────────────────────

{precedents}

  • {case['statutes'][0]['citation']} — {case['statutes'][0]['title']}

────────────────────────────────────────────────────────────────────────
RECOMMENDATION
────────────────────────────────────────────────────────────────────────

File Motion to Suppress CSLI evidence. Seek suppression under the exclusionary rule. If necessary,
preserve issue for interlocutory appeal / certiorari on Fourth Amendment grounds.

Respectfully submitted,

/s/ OWL Research Agent
Automated Paralegal Research System | OWL AI Agency
"""


def _case_brief(case: dict[str, Any]) -> str:
    return f"""{_caption(case)}

                         CASE BRIEF
                    {case['full_name']}
                         {case['citation']}

COURT:          {case['court']}
DATE DECIDED:   {case['decision_date']}
AUTHOR:         {case['author']}
VOTE:           {case['vote']}

────────────────────────────────────────────────────────────────────────
FACTS
────────────────────────────────────────────────────────────────────────

{case['facts_summary']}

────────────────────────────────────────────────────────────────────────
PROCEDURAL HISTORY
────────────────────────────────────────────────────────────────────────

{chr(10).join('  • ' + p for p in case['procedural_history'])}

────────────────────────────────────────────────────────────────────────
ISSUE
────────────────────────────────────────────────────────────────────────

{case['issue']}

────────────────────────────────────────────────────────────────────────
HOLDING
────────────────────────────────────────────────────────────────────────

{case['holding']}

────────────────────────────────────────────────────────────────────────
REASONING (IRAC)
────────────────────────────────────────────────────────────────────────

Rule:     Katz reasonable-expectation-of-privacy framework; Jones long-term tracking;
          Riley cell-phone privacy; SCA § 2703(d) below probable-cause standard.

Analysis: 127 days of CSLI is not comparable to pen-register data in Smith. CSLI provides a
          comprehensive chronicle of the user's physical presence — "near perfect surveillance."
          Third-party doctrine does not categorically bar a privacy claim to location records.

Conclusion: Warrant required. Convictions affirmed on other grounds; remanded for further
            proceedings consistent with opinion.

────────────────────────────────────────────────────────────────────────
DISPOSITION
────────────────────────────────────────────────────────────────────────

Affirmed in part; judgment vacated in part; case remanded.

Prepared by: OWL Precedent Agent | OWL AI Agency
"""


def _motion_to_suppress(case: dict[str, Any], today: str) -> str:
    return f"""{_caption(case)}

              DEFENDANT'S MOTION TO SUPPRESS
           CELL-SITE LOCATION INFORMATION (CSLI)

TO THE HONORABLE COURT:

NOW COMES Defendant {case['demo_scenario']['client_name']}, by and through undersigned counsel,
and respectfully moves this Court pursuant to the Fourth Amendment and Fed. R. Crim. P. 12(b)(3)(C)
to suppress all cell-site location information obtained by the Federal Bureau of Investigation from
MetroPCS and Sprint without a warrant supported by probable cause.

────────────────────────────────────────────────────────────────────────
I.  INTRODUCTION
────────────────────────────────────────────────────────────────────────

The Government acquired 127 days of Defendant's historical cell-site location records pursuant to
court orders under 18 U.S.C. § 2703(d) — not a warrant. Such acquisition constitutes a search
under Carpenter v. United States, {case['citation']}.

────────────────────────────────────────────────────────────────────────
II. STATEMENT OF FACTS
────────────────────────────────────────────────────────────────────────

{case['facts_summary']}

────────────────────────────────────────────────────────────────────────
III. LEGAL STANDARD
────────────────────────────────────────────────────────────────────────

A Fourth Amendment search occurs when the Government violates a reasonable expectation of privacy.
Katz v. United States, 389 U.S. 347 (1967). Warrantless searches are per se unreasonable unless
an exception applies. The good-faith exception does not apply where no warrant was sought.

────────────────────────────────────────────────────────────────────────
IV. ARGUMENT
────────────────────────────────────────────────────────────────────────

A. Acquisition of Historical CSLI Is a Fourth Amendment Search.

   In Carpenter, the Supreme Court held that accessing historical CSLI is a search. {case['holding']}
   The records here — 127 days — far exceed the seven-day threshold discussed by the Court.

B. The Stored Communications Act Cannot Authorize Unconstitutional Searches.

   18 U.S.C. § 2703(d) requires only "reasonable grounds" — less than probable cause. A statute
   cannot lower the constitutional floor for searches implicating core privacy interests.

C. Suppression Is the Appropriate Remedy.

   Evidence obtained in violation of the Fourth Amendment must be suppressed. Mapp v. Ohio,
   367 U.S. 643 (1961).

────────────────────────────────────────────────────────────────────────
V.  CONCLUSION
────────────────────────────────────────────────────────────────────────

For the foregoing reasons, Defendant respectfully requests that this Court GRANT the Motion and
suppress all CSLI evidence and derivative fruits.

Respectfully submitted,

_________________________________
Counsel for Defendant {case['demo_scenario']['client_name']}

Dated: {today}

Prepared by: OWL Brief Writer Agent | OWL AI Agency
"""


def _appellate_brief_excerpt(case: dict[str, Any]) -> str:
    return f"""IN THE SUPREME COURT OF THE UNITED STATES

TIMOTHY IVAN CARPENTER, Petitioner,
                                    v.
UNITED STATES OF AMERICA, Respondent.

On Writ of Certiorari to the United States Court of Appeals
for the Sixth Circuit

BRIEF FOR PETITIONER (EXCERPT)

QUESTION PRESENTED

{case['issue']}

────────────────────────────────────────────────────────────────────────
STATEMENT OF THE CASE
────────────────────────────────────────────────────────────────────────

A.  Proceedings Below

{chr(10).join(case['procedural_history'])}

B.  Facts

{case['facts_summary']}

────────────────────────────────────────────────────────────────────────
SUMMARY OF ARGUMENT
────────────────────────────────────────────────────────────────────────

Historical cell-site records reveal the whole of a person's physical movements over time. When
the Government compels a third party to surrender 127 days of such records without a warrant, it
conducts a Fourth Amendment search. This Court should hold that the exclusionary rule requires
suppression when CSLI is obtained in violation of Carpenter.

────────────────────────────────────────────────────────────────────────
ARGUMENT
────────────────────────────────────────────────────────────────────────

I.  THE GOVERNMENT'S ACQUISITION OF HISTORICAL CSLI WAS A SEARCH.

   Cell phones are "almost a feature of human anatomy." Riley v. California, 573 U.S. 373, 385
   (2014). CSLI generated by those phones chronicles past movements with detail that was
   "previously inconceivable." Carpenter, {case['citation']}.

   The Government argues Smith v. Maryland permits warrantless access because CSLI is "business
   records" held by carriers. That argument fails. Carpenter declined to extend the third-party
   doctrine to "a qualitatively different category of cell-site records."

II. A WARRANT WAS REQUIRED.

   Probable cause, not "reasonable grounds," is the minimum constitutional requirement. The SCA's
   § 2703(d) standard cannot substitute for a warrant when the search implicates the privacies
   of life protected by the Fourth Amendment.

III. SUPPRESSION FOLLOWS.

   Petitioner seeks the remedy the Constitution demands: exclusion of unlawfully obtained evidence.

CONCLUSION

The judgment of the Sixth Circuit should be reversed.

Respectfully submitted,

/s/ Counsel for Petitioner

Prepared by: OWL Analysis & Brief Writer Agents | OWL AI Agency
"""


def _table_of_authorities(case: dict[str, Any]) -> str:
    rows = [
        f"Cases",
        f"",
        f"  Carpenter v. United States, {case['citation']} ........................ passim",
    ]
    for p in case["key_precedents"]:
        short = p["case"].split(" v. ")[0] if " v. " in p["case"] else p["case"]
        rows.append(f"  {p['case']}, {p['citation']} ........................ cited")
    rows.extend(["", "Constitutional Provisions", ""])
    for s in case["statutes"]:
        rows.append(f"  {s['citation']} ........................ passim")
    rows.extend(["", "Statutes", "", f"  {case['statutes'][0]['citation']} ........................ passim"])
    return f"""{_caption(case)}

                      TABLE OF AUTHORITIES

{chr(10).join(rows)}

Prepared by: OWL Citation Agent | Bluebook (21st ed.) formatting
"""


def _certificate_of_service(case: dict[str, Any], today: str) -> str:
    return f"""{_caption(case)}

                  CERTIFICATE OF SERVICE

I hereby certify that on {today}, a true and correct copy of the foregoing

    • Defendant's Motion to Suppress Cell-Site Location Information
    • Memorandum in Support
    • Table of Authorities

was served via the Court's CM/ECF electronic filing system upon all registered counsel of record,
including:

    United States Attorney's Office
    Eastern District of Michigan
    211 West Fort Street
    Detroit, MI 48226

_________________________________
/s/ OWL Filing Agent
OWL AI Agency — Paralegal Automation System

Prepared by: OWL Filing Agent | OWL AI Agency
"""
