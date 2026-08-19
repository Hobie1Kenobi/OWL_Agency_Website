"""Live citation verification against the six public legal source families."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from services.citation_parser import infer_court, infer_toa_group, parse_citations
from services.legal_sources import PUBLIC_LEGAL_SOURCES, probe_url

log = logging.getLogger("owl.verify")

REQUEST_TIMEOUT = 10.0
OVERALL_BUDGET = 28.0
CONCURRENCY = 8
MIN_HTML_BYTES = 400

TOA_GROUPS = [
    {"id": "us_supreme_court", "label": "U.S. Supreme Court"},
    {"id": "courts_of_appeals", "label": "Courts of Appeals"},
    {"id": "district_courts", "label": "District Courts"},
    {"id": "statutes_rules", "label": "Statutes / Rules"},
    {"id": "unresolved", "label": "Unresolved / short form"},
]

CHECK_LABELS = {
    "existence": "Existence",
    "citation_format": "Citation format",
    "holding_support": "Holding support",
    "verification_path": "Verification path",
    "human_review_flag": "Human review flag",
}

MATTER_META: dict[str, dict[str, Any]] = {
    "carpenter": {
        "title": "SAMPLE — Carpenter CSLI brief excerpt (tainted)",
        "matter_name": "SAMPLE — CSLI suppression excerpt (Carpenter line)",
        "practice_area": "Criminal procedure / Fourth Amendment",
        "warning_banner": (
            "SAMPLE excerpt. Not a real filing. Not legal advice. "
            "This pack plants a hallucinated cite, a real case used for the wrong proposition, "
            "an ambiguous short form, and a docket that is not in the public reporter corpus. "
            "OWL is a verification layer, not an AI lawyer. Human review of every output is required."
        ),
    },
    "riley": {
        "title": "SAMPLE — Riley cell-phone search excerpt",
        "matter_name": "SAMPLE — Search-incident-to-arrest excerpt (Riley line)",
        "practice_area": "Criminal procedure / Fourth Amendment",
        "warning_banner": (
            "SAMPLE excerpt. Not a real filing. Not legal advice. "
            "OWL is a verification layer, not an AI lawyer. Human review of every output is required."
        ),
    },
    "miranda": {
        "title": "SAMPLE — Miranda warnings excerpt",
        "matter_name": "SAMPLE — Custodial interrogation excerpt (Miranda line)",
        "practice_area": "Criminal procedure / Fifth Amendment",
        "warning_banner": (
            "SAMPLE excerpt. Not a real filing. Not legal advice. "
            "OWL is a verification layer, not an AI lawyer. Human review of every output is required."
        ),
    },
    "gideon": {
        "title": "SAMPLE — Gideon right-to-counsel excerpt",
        "matter_name": "SAMPLE — Appointed counsel excerpt (Gideon line)",
        "practice_area": "Criminal procedure / Sixth Amendment",
        "warning_banner": (
            "SAMPLE excerpt. Not a real filing. Not legal advice. "
            "OWL is a verification layer, not an AI lawyer. Human review of every output is required."
        ),
    },
    "katz": {
        "title": "SAMPLE — Katz reasonable-expectation excerpt",
        "matter_name": "SAMPLE — Electronic surveillance excerpt (Katz line)",
        "practice_area": "Criminal procedure / Fourth Amendment",
        "warning_banner": (
            "SAMPLE excerpt. Not a real filing. Not legal advice. "
            "OWL is a verification layer, not an AI lawyer. Human review of every output is required."
        ),
    },
}

# Known public URLs for opinions that the sample packs actually cite.
# Used to hit each source family at a citation-specific address, not a homepage.
CASE_CATALOG: dict[str, dict[str, Any]] = {
    "585 U.S. 946": {
        "name": "Carpenter v. United States",
        "citation": "Carpenter v. United States, 585 U.S. 946 (2018)",
        "year": 2018,
        "oyez": ("2017", "16-402"),
        "cornell": ["/supremecourt/text/16-402", "/supremecourt/text/585/946"],
        "justia": "https://supreme.justia.com/cases/federal/us/585/16-402/",
        "courtlistener_page": "https://www.courtlistener.com/opinion/4379486/carpenter-v-united-states/",
        "courtlistener_pdf": "https://storage.courtlistener.com/pdf/2018/06/22/carpenter_v._united_states.pdf",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/17pdf/16-402_h315.pdf",
        "wrong_holding": re.compile(
            r"without a warrant|no warrant is required|need not obtain a warrant",
            re.I,
        ),
    },
    "138 S. Ct. 2206": {
        "name": "Carpenter v. United States",
        "citation": "Carpenter v. United States, 138 S. Ct. 2206 (2018)",
        "year": 2018,
        "oyez": ("2017", "16-402"),
        "cornell": ["/supremecourt/text/16-402"],
        "justia": "https://supreme.justia.com/cases/federal/us/585/16-402/",
        "courtlistener_page": "https://www.courtlistener.com/c/S.Ct./138/2206/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/17pdf/16-402_h315.pdf",
        "wrong_holding": re.compile(
            r"without a warrant|no warrant is required|need not obtain a warrant",
            re.I,
        ),
    },
    "573 U.S. 373": {
        "name": "Riley v. California",
        "citation": "Riley v. California, 573 U.S. 373 (2014)",
        "year": 2014,
        "oyez": ("2013", "13-132"),
        "cornell": ["/supremecourt/text/13-132", "/supremecourt/text/573/373"],
        "justia": "https://supreme.justia.com/cases/federal/us/573/373/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./573/373/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/13pdf/13-132_8l9c.pdf",
    },
    "389 U.S. 347": {
        "name": "Katz v. United States",
        "citation": "Katz v. United States, 389 U.S. 347 (1967)",
        "year": 1967,
        "oyez": ("1967", "35"),
        "cornell": ["/supremecourt/text/389/347"],
        "justia": "https://supreme.justia.com/cases/federal/us/389/347/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./389/347/",
    },
    "384 U.S. 436": {
        "name": "Miranda v. Arizona",
        "citation": "Miranda v. Arizona, 384 U.S. 436 (1966)",
        "year": 1966,
        "oyez": ("1965", "759"),
        "cornell": ["/supremecourt/text/384/436"],
        "justia": "https://supreme.justia.com/cases/federal/us/384/436/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./384/436/",
    },
    "372 U.S. 335": {
        "name": "Gideon v. Wainwright",
        "citation": "Gideon v. Wainwright, 372 U.S. 335 (1963)",
        "year": 1963,
        "oyez": ("1962", "155"),
        "cornell": ["/supremecourt/text/372/335"],
        "justia": "https://supreme.justia.com/cases/federal/us/372/335/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./372/335/",
    },
    "565 U.S. 400": {
        "name": "United States v. Jones",
        "citation": "United States v. Jones, 565 U.S. 400 (2012)",
        "year": 2012,
        "oyez": ("2011", "10-1259"),
        "cornell": ["/supremecourt/text/10-1259", "/supremecourt/text/565/400"],
        "justia": "https://supreme.justia.com/cases/federal/us/565/400/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./565/400/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/11pdf/10-1259.pdf",
    },
    "442 U.S. 735": {
        "name": "Smith v. Maryland",
        "citation": "Smith v. Maryland, 442 U.S. 735 (1979)",
        "year": 1979,
        "oyez": ("1978", "78-5374"),
        "cornell": ["/supremecourt/text/442/735"],
        "justia": "https://supreme.justia.com/cases/federal/us/442/735/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./442/735/",
    },
    "425 U.S. 435": {
        "name": "United States v. Miller",
        "citation": "United States v. Miller, 425 U.S. 435 (1976)",
        "year": 1976,
        "oyez": ("1975", "74-1179"),
        "cornell": ["/supremecourt/text/425/435"],
        "justia": "https://supreme.justia.com/cases/federal/us/425/435/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./425/435/",
    },
    "395 U.S. 752": {
        "name": "Chimel v. California",
        "citation": "Chimel v. California, 395 U.S. 752 (1969)",
        "year": 1969,
        "oyez": ("1968", "770"),
        "cornell": ["/supremecourt/text/395/752"],
        "justia": "https://supreme.justia.com/cases/federal/us/395/752/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./395/752/",
    },
    "414 U.S. 218": {
        "name": "United States v. Robinson",
        "citation": "United States v. Robinson, 414 U.S. 218 (1973)",
        "year": 1973,
        "oyez": ("1973", "72-936"),
        "cornell": ["/supremecourt/text/414/218"],
        "justia": "https://supreme.justia.com/cases/federal/us/414/218/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./414/218/",
    },
    "556 U.S. 332": {
        "name": "Arizona v. Gant",
        "citation": "Arizona v. Gant, 556 U.S. 332 (2009)",
        "year": 2009,
        "oyez": ("2008", "07-542"),
        "cornell": ["/supremecourt/text/07-542"],
        "justia": "https://supreme.justia.com/cases/federal/us/556/332/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./556/332/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/08pdf/07-542.pdf",
    },
    "433 U.S. 1": {
        "name": "United States v. Chadwick",
        "citation": "United States v. Chadwick, 433 U.S. 1 (1977)",
        "year": 1977,
        "oyez": ("1976", "75-1730"),
        "cornell": ["/supremecourt/text/433/1"],
        "justia": "https://supreme.justia.com/cases/federal/us/433/1/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./433/1/",
    },
    "232 U.S. 383": {
        "name": "Weeks v. United States",
        "citation": "Weeks v. United States, 232 U.S. 383 (1914)",
        "year": 1914,
        "cornell": ["/supremecourt/text/232/383"],
        "justia": "https://supreme.justia.com/cases/federal/us/232/383/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./232/383/",
    },
    "378 U.S. 478": {
        "name": "Escobedo v. Illinois",
        "citation": "Escobedo v. Illinois, 378 U.S. 478 (1964)",
        "year": 1964,
        "oyez": ("1963", "615"),
        "cornell": ["/supremecourt/text/378/478"],
        "justia": "https://supreme.justia.com/cases/federal/us/378/478/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./378/478/",
    },
    "530 U.S. 428": {
        "name": "Dickerson v. United States",
        "citation": "Dickerson v. United States, 530 U.S. 428 (2000)",
        "year": 2000,
        "oyez": ("1999", "99-5525"),
        "cornell": ["/supremecourt/text/99-5525"],
        "justia": "https://supreme.justia.com/cases/federal/us/530/428/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./530/428/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/99pdf/99-5525.pdf",
    },
    "470 U.S. 298": {
        "name": "Oregon v. Elstad",
        "citation": "Oregon v. Elstad, 470 U.S. 298 (1985)",
        "year": 1985,
        "oyez": ("1984", "83-773"),
        "cornell": ["/supremecourt/text/470/298"],
        "justia": "https://supreme.justia.com/cases/federal/us/470/298/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./470/298/",
    },
    "451 U.S. 477": {
        "name": "Edwards v. Arizona",
        "citation": "Edwards v. Arizona, 451 U.S. 477 (1981)",
        "year": 1981,
        "oyez": ("1980", "79-5269"),
        "cornell": ["/supremecourt/text/451/477"],
        "justia": "https://supreme.justia.com/cases/federal/us/451/477/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./451/477/",
    },
    "287 U.S. 45": {
        "name": "Powell v. Alabama",
        "citation": "Powell v. Alabama, 287 U.S. 45 (1932)",
        "year": 1932,
        "oyez": ("1932", "98"),
        "cornell": ["/supremecourt/text/287/45"],
        "justia": "https://supreme.justia.com/cases/federal/us/287/45/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./287/45/",
    },
    "316 U.S. 455": {
        "name": "Betts v. Brady",
        "citation": "Betts v. Brady, 316 U.S. 455 (1942)",
        "year": 1942,
        "cornell": ["/supremecourt/text/316/455"],
        "justia": "https://supreme.justia.com/cases/federal/us/316/455/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./316/455/",
    },
    "304 U.S. 458": {
        "name": "Johnson v. Zerbst",
        "citation": "Johnson v. Zerbst, 304 U.S. 458 (1938)",
        "year": 1938,
        "cornell": ["/supremecourt/text/304/458"],
        "justia": "https://supreme.justia.com/cases/federal/us/304/458/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./304/458/",
    },
    "407 U.S. 25": {
        "name": "Argersinger v. Hamlin",
        "citation": "Argersinger v. Hamlin, 407 U.S. 25 (1972)",
        "year": 1972,
        "oyez": ("1971", "70-5015"),
        "cornell": ["/supremecourt/text/407/25"],
        "justia": "https://supreme.justia.com/cases/federal/us/407/25/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./407/25/",
    },
    "466 U.S. 668": {
        "name": "Strickland v. Washington",
        "citation": "Strickland v. Washington, 466 U.S. 668 (1984)",
        "year": 1984,
        "oyez": ("1983", "82-1554"),
        "cornell": ["/supremecourt/text/466/668"],
        "justia": "https://supreme.justia.com/cases/federal/us/466/668/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./466/668/",
    },
    "277 U.S. 438": {
        "name": "Olmstead v. United States",
        "citation": "Olmstead v. United States, 277 U.S. 438 (1928)",
        "year": 1928,
        "cornell": ["/supremecourt/text/277/438"],
        "justia": "https://supreme.justia.com/cases/federal/us/277/438/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./277/438/",
    },
    "365 U.S. 505": {
        "name": "Silverman v. United States",
        "citation": "Silverman v. United States, 365 U.S. 505 (1961)",
        "year": 1961,
        "cornell": ["/supremecourt/text/365/505"],
        "justia": "https://supreme.justia.com/cases/federal/us/365/505/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./365/505/",
    },
    "401 U.S. 745": {
        "name": "United States v. White",
        "citation": "United States v. White, 401 U.S. 745 (1971)",
        "year": 1971,
        "cornell": ["/supremecourt/text/401/745"],
        "justia": "https://supreme.justia.com/cases/federal/us/401/745/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./401/745/",
    },
    "533 U.S. 27": {
        "name": "Kyllo v. United States",
        "citation": "Kyllo v. United States, 533 U.S. 27 (2001)",
        "year": 2001,
        "oyez": ("2000", "99-8508"),
        "cornell": ["/supremecourt/text/99-8508"],
        "justia": "https://supreme.justia.com/cases/federal/us/533/27/",
        "courtlistener_page": "https://www.courtlistener.com/c/U.S./533/27/",
        "scotus_pdf": "https://www.supremecourt.gov/opinions/00pdf/99-8508.pdf",
    },
    "819 F.3d 880": {
        "name": "United States v. Carpenter",
        "citation": "United States v. Carpenter, 819 F.3d 880 (6th Cir. 2016)",
        "year": 2016,
        "courtlistener_page": "https://www.courtlistener.com/c/F.3d/819/880/",
    },
    "728 F.3d 1": {
        "name": "United States v. Wurie",
        "citation": "United States v. Wurie, 728 F.3d 1 (1st Cir. 2013)",
        "year": 2013,
        "courtlistener_page": "https://www.courtlistener.com/c/F.3d/728/1/",
    },
}

SOURCE_BY_ID = {item["id"]: item for item in PUBLIC_LEGAL_SOURCES}


def _slug(value: str, index: int) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", (value or "cite").lower()).strip("-")[:40]
    return f"{base or 'cite'}-{index}"


def _cl_reporter_slug(reporter: str) -> str:
    text = reporter.replace(" ", "")
    text = text.replace("S.Ct.", "S.Ct.")
    if reporter.lower().startswith("s."):
        return "S.Ct."
    if "supp" in reporter.lower():
        return re.sub(r"\s+", "", reporter).replace("Supp.", "Supp.")
    return text


def _catalog_for(cite: dict[str, Any]) -> dict[str, Any]:
    return CASE_CATALOG.get(cite.get("key") or "", {})


def _html_excerpt(html: str, limit: int = 1500) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for selector in ("article", "div#syllabus", "div.field-body", "div#documentcontent", "div.opinion"):
        node = soup.select_one(selector)
        if node:
            text = node.get_text(" ", strip=True)
            if len(text) > 80:
                return text[:limit]
    text = soup.get_text(" ", strip=True)
    return text[:limit] if text else ""


def _content_matches(cite: dict[str, Any], text: str) -> bool:
    blob = (text or "").lower()
    if not blob or len(blob) < 40:
        return False
    if cite.get("kind") == "statute":
        return str(cite.get("section", "")).lower() in blob or "united states code" in blob
    if cite.get("kind") == "rule":
        return f"rule {cite.get('rule_number')}".lower() in blob or "federal rules" in blob
    if cite.get("kind") == "constitution":
        return "amendment" in blob or "constitution" in blob
    page = str(cite.get("page") or "")
    volume = str(cite.get("volume") or "")
    parties = (cite.get("parties") or _catalog_for(cite).get("name") or "").lower()
    if volume and page and volume in blob and page in blob:
        return True
    if parties and " v." in parties:
        last = parties.split(" v.")[0].split()[-1]
        if last and last in blob:
            return True
    return False


def _status_from_probe(probe: dict[str, Any], matched: bool) -> str:
    error = probe.get("error")
    http_status = probe.get("http_status")
    if matched:
        return "ok"
    if error == "timeout":
        return "timeout"
    if error == "blocked" or http_status == 403:
        return "blocked"
    if http_status == 404 or error == "empty":
        return "no_match"
    if probe.get("ok") and not matched:
        return "no_match"
    if http_status:
        return "error"
    return "error" if error else "no_match"


def _result(
    source_id: str,
    probe: dict[str, Any],
    *,
    matched: bool,
    excerpt: str = "",
) -> dict[str, Any]:
    meta = SOURCE_BY_ID.get(source_id) or {"id": source_id, "name": source_id}
    return {
        "id": source_id,
        "name": meta["name"],
        "status": _status_from_probe(probe, matched),
        "http_status": probe.get("http_status"),
        "error": None if matched else probe.get("error"),
        "url": probe.get("url") or probe.get("requested_url"),
        "matched": matched,
        "excerpt": excerpt[:1500] if matched else "",
    }


def _empty_result(source_id: str, url: str, error: str, status: str = "error") -> dict[str, Any]:
    meta = SOURCE_BY_ID.get(source_id) or {"id": source_id, "name": source_id}
    return {
        "id": source_id,
        "name": meta["name"],
        "status": status,
        "http_status": None,
        "error": error,
        "url": url,
        "matched": False,
        "excerpt": "",
    }


async def _first_ok(
    client: httpx.AsyncClient,
    urls: list[str],
    *,
    accept: str | None = None,
    min_bytes: int = MIN_HTML_BYTES,
) -> dict[str, Any]:
    last: dict[str, Any] | None = None
    for url in urls:
        if not url:
            continue
        probe = await probe_url(client, url, accept=accept, min_bytes=min_bytes)
        last = probe
        if probe.get("ok"):
            return probe
    return last or {
        "ok": False,
        "http_status": None,
        "url": urls[0] if urls else "",
        "requested_url": urls[0] if urls else "",
        "text": "",
        "error": "no_url",
        "is_pdf": False,
    }


async def query_cornell(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    catalog = _catalog_for(cite)
    urls: list[str] = []
    if catalog.get("cornell"):
        urls.extend(f"https://www.law.cornell.edu{path}" for path in catalog["cornell"])
    kind = cite.get("kind")
    reporter = (cite.get("reporter") or "").lower()
    if kind == "statute":
        urls.append(f"https://www.law.cornell.edu/uscode/text/{cite['title']}/{cite['section']}")
    elif kind == "rule":
        suite = "frcrmp" if (cite.get("rule_suite") or "").lower().startswith("crim") else "frcp"
        urls.append(f"https://www.law.cornell.edu/rules/{suite}/rule_{cite['rule_number']}")
    elif kind == "constitution":
        amendment = str(cite.get("amendment") or "")
        roman_to_int = {"IV": "4", "V": "5", "VI": "6"}
        number = roman_to_int.get(amendment.upper(), amendment)
        urls.append(f"https://www.law.cornell.edu/constitution-conan/amendment-{number}")
    elif kind == "docket":
        urls.append(f"https://www.law.cornell.edu/search?query={quote(cite.get('raw') or '')}")
    elif "u.s." in reporter and "u.s.c" not in reporter:
        urls.append(
            f"https://www.law.cornell.edu/supremecourt/text/{cite.get('volume')}/{cite.get('page')}"
        )
    else:
        query = cite.get("raw") or cite.get("key") or ""
        urls.append(f"https://www.law.cornell.edu/search?query={quote(query)}")

    probe = await _first_ok(client, urls)
    excerpt = _html_excerpt(probe.get("text") or "") if probe.get("ok") else ""
    url = (probe.get("url") or probe.get("requested_url") or "")
    matched = bool(probe.get("ok"))
    if matched:
        if "/search" in url:
            matched = _content_matches(cite, excerpt)
        elif any(token in url for token in ("/supremecourt/text/", "/uscode/text/", "/rules/", "constitution")):
            matched = len(excerpt) > 80
        else:
            matched = _content_matches(cite, excerpt) or len(excerpt) > 200
    return _result("cornell_lii", probe, matched=matched, excerpt=excerpt)


async def query_oyez(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    catalog = _catalog_for(cite)
    oyez = catalog.get("oyez")
    if oyez:
        url = f"https://api.oyez.org/cases/{oyez[0]}/{oyez[1]}"
        probe = await probe_url(client, url, accept="application/json", min_bytes=40)
        matched = bool(probe.get("ok"))
        excerpt = (probe.get("text") or "")[:800]
        if matched:
            name = catalog.get("name", "")
            if name and name.split()[0].lower() not in excerpt.lower() and "docket" not in excerpt.lower():
                matched = len(excerpt) > 40
        return _result("oyez", probe, matched=matched, excerpt=excerpt)
    query = cite.get("parties") or cite.get("raw") or cite.get("key") or ""
    url = f"https://www.oyez.org/search?q={quote(query)}"
    probe = await probe_url(client, url, min_bytes=200)
    matched = bool(probe.get("ok")) and _content_matches(cite, probe.get("text") or "")
    return _result("oyez", probe, matched=matched, excerpt=_html_excerpt(probe.get("text") or "") if matched else "")


async def query_courtlistener(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    catalog = _catalog_for(cite)
    urls: list[str] = []
    token = os.getenv("COURTLISTENER_API_TOKEN") or os.getenv("COURTLISTENER_TOKEN")
    if catalog.get("courtlistener_pdf"):
        pdf_probe = await probe_url(
            client,
            catalog["courtlistener_pdf"],
            accept="application/pdf,*/*",
            min_bytes=8_000,
        )
        if pdf_probe.get("ok") and pdf_probe.get("is_pdf"):
            pdf_probe["url"] = catalog.get("courtlistener_page") or pdf_probe.get("url")
            return _result("courtlistener", pdf_probe, matched=True, excerpt="")
    if catalog.get("courtlistener_page"):
        urls.append(catalog["courtlistener_page"])
    if cite.get("kind") == "case" and cite.get("volume") and cite.get("page"):
        slug = _cl_reporter_slug(cite.get("reporter") or "U.S.")
        urls.append(
            f"https://www.courtlistener.com/c/{slug}/{cite['volume']}/{cite['page']}/"
        )
    if cite.get("kind") == "docket":
        urls.append(
            f"https://www.courtlistener.com/?q={quote(cite.get('raw') or '')}&type=o"
        )

    if token and cite.get("key"):
        api_url = (
            "https://www.courtlistener.com/api/rest/v4/search/"
            f"?type=o&q={quote(cite.get('key') or '')}"
        )
        try:
            response = await client.get(
                api_url,
                headers={
                    "Authorization": f"Token {token}",
                    "Accept": "application/json",
                    "User-Agent": "OWL-Legal-Research-Demo/1.0 (+https://owl-ai-agency.com/verify)",
                },
                follow_redirects=True,
            )
            data = response.json() if response.status_code == 200 else {}
            count = 0
            if isinstance(data, dict):
                count = int(data.get("count") or 0) or len(data.get("results") or [])
            probe = {
                "ok": response.status_code == 200 and count > 0,
                "http_status": response.status_code,
                "url": api_url.split("?")[0],
                "requested_url": api_url.split("?")[0],
                "text": "",
                "error": None if response.status_code < 400 else f"HTTP {response.status_code}",
                "is_pdf": False,
            }
            if probe["ok"]:
                return _result("courtlistener", probe, matched=True, excerpt="")
        except httpx.HTTPError:
            pass

    if not urls:
        return _empty_result(
            "courtlistener",
            "https://www.courtlistener.com/",
            "no citation-specific CourtListener URL",
            "no_match",
        )
    probe = await _first_ok(client, urls)
    matched = bool(probe.get("ok")) and (
        "/c/" in (probe.get("url") or "")
        or "/opinion/" in (probe.get("url") or "")
        or _content_matches(cite, probe.get("text") or "")
    )
    excerpt = _html_excerpt(probe.get("text") or "") if matched else ""
    return _result("courtlistener", probe, matched=matched, excerpt=excerpt)


async def query_justia(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    catalog = _catalog_for(cite)
    urls: list[str] = []
    if catalog.get("justia"):
        primary = catalog["justia"]
        urls.append(primary)
        urls.append("https://web.archive.org/web/2023/" + primary)
    elif cite.get("kind") == "case" and "u.s." in (cite.get("reporter") or "").lower():
        primary = (
            f"https://supreme.justia.com/cases/federal/us/{cite.get('volume')}/{cite.get('page')}/"
        )
        urls.append(primary)
        urls.append("https://web.archive.org/web/2023/" + primary)
    elif cite.get("kind") == "statute":
        urls.append(
            f"https://law.justia.com/codes/us/{cite['title']}/{cite['title']}usc{cite['section']}.html"
        )
    else:
        urls.append(f"https://law.justia.com/search?query={quote(cite.get('raw') or cite.get('key') or '')}")

    probe = await _first_ok(client, urls)
    excerpt = _html_excerpt(probe.get("text") or "") if probe.get("ok") else ""
    matched = bool(probe.get("ok")) and (
        "/cases/" in (probe.get("url") or "")
        or "/codes/" in (probe.get("url") or "")
        or _content_matches(cite, excerpt)
    )
    if "search?" in (probe.get("requested_url") or "") and not _content_matches(cite, excerpt):
        matched = False
    return _result("justia", probe, matched=matched, excerpt=excerpt)


async def query_govinfo(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    if cite.get("kind") == "statute":
        title, section = cite["title"], cite["section"]
        urls = [
            (
                f"https://www.govinfo.gov/app/details/USCODE-2018-title{title}/"
                f"USCODE-2018-title{title}-sec{section}"
            ),
            (
                f"https://www.govinfo.gov/app/details/USCODE-2017-title{title}/"
                f"USCODE-2017-title{title}-sec{section}"
            ),
        ]
        probe = await _first_ok(client, urls, min_bytes=100)
        matched = bool(probe.get("ok"))
        return _result("govinfo", probe, matched=matched, excerpt="")

    query = cite.get("key") or cite.get("raw") or ""
    url = f"https://www.govinfo.gov/app/search?query={quote(query)}"
    probe = await probe_url(client, url, min_bytes=50)
    text = probe.get("text") or ""
    matched = bool(probe.get("ok")) and _content_matches(cite, text)
    return _result("govinfo", probe, matched=matched, excerpt=text[:400] if matched else "")


async def query_scotus(client: httpx.AsyncClient, cite: dict[str, Any]) -> dict[str, Any]:
    catalog = _catalog_for(cite)
    if catalog.get("scotus_pdf"):
        probe = await probe_url(
            client,
            catalog["scotus_pdf"],
            accept="application/pdf,*/*",
            min_bytes=8_000,
        )
        matched = bool(probe.get("ok") and probe.get("is_pdf"))
        return _result("supremecourt_gov", probe, matched=matched, excerpt="")
    oyez = catalog.get("oyez")
    if oyez and "-" in str(oyez[1]):
        docket = oyez[1]
        url = (
            "https://www.supremecourt.gov/search.aspx"
            f"?filename=/docket/docketfiles/html/public/{docket}.html"
        )
        probe = await probe_url(client, url, min_bytes=200)
        matched = bool(probe.get("ok")) and _content_matches(cite, probe.get("text") or "")
        return _result("supremecourt_gov", probe, matched=matched, excerpt="")
    return _empty_result(
        "supremecourt_gov",
        "https://www.supremecourt.gov/opinions/opinions.aspx",
        "no public slip-opinion URL for this citation",
        "no_match",
    )


SOURCE_QUERIES = (
    ("cornell_lii", query_cornell),
    ("oyez", query_oyez),
    ("courtlistener", query_courtlistener),
    ("justia", query_justia),
    ("govinfo", query_govinfo),
    ("supremecourt_gov", query_scotus),
)


async def _query_one(
    sem: asyncio.Semaphore,
    client: httpx.AsyncClient,
    source_id: str,
    fn,
    cite: dict[str, Any],
) -> dict[str, Any]:
    async with sem:
        try:
            return await fn(client, cite)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - network/runtime guard
            log.info("verify source %s failed: %s", source_id, type(exc).__name__)
            return _empty_result(source_id, "", type(exc).__name__, "error")


async def query_all_sources(cite: dict[str, Any], client: httpx.AsyncClient, sem: asyncio.Semaphore) -> list[dict[str, Any]]:
    tasks = [
        asyncio.create_task(_query_one(sem, client, source_id, fn, cite), name=f"{source_id}:{cite.get('key')}")
        for source_id, fn in SOURCE_QUERIES
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    out: list[dict[str, Any]] = []
    for (source_id, _), result in zip(SOURCE_QUERIES, results):
        if isinstance(result, dict):
            out.append(result)
        else:
            out.append(_empty_result(source_id, "", "timeout" if isinstance(result, asyncio.CancelledError) else "error", "timeout"))
    return out


def _check(check_id: str, status: str, detail: str, extras: dict[str, Any] | None = None) -> dict[str, Any]:
    extras = extras or {}
    return {
        "id": check_id,
        "label": CHECK_LABELS[check_id],
        "status": status,
        "detail": detail,
        "checked": extras.get("checked") or "",
        "against": extras.get("against") or "",
        "sourceUrl": extras.get("sourceUrl"),
    }


def _format_status(cite: dict[str, Any]) -> tuple[str, str]:
    kind = cite.get("kind")
    if kind == "ambiguous" or (kind == "case" and not cite.get("page")):
        return "fail", "Short form without a page is not enough to resolve against a reporter."
    if kind == "docket":
        return (
            "pass",
            "Docket form is recognizable, but it is not a reporter citation in the public corpus this check uses.",
        )
    if kind == "statute" and cite.get("title") and cite.get("section"):
        return "pass", f"Statute form resolves: {cite['title']} U.S.C. § {cite['section']}."
    if kind == "rule" and cite.get("rule_number"):
        return "pass", f"Rule form resolves: Fed. R. {cite.get('rule_suite')}. P. {cite['rule_number']}."
    if kind == "constitution":
        return "pass", f"Constitutional citation form: U.S. Const. amend. {cite.get('amendment')}."
    if cite.get("volume") and cite.get("reporter") and cite.get("page"):
        return "pass", f"Reporter form resolves: {cite.get('key')}."
    return "fail", "Citation format is incomplete."


def _holding_support(cite: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    proposition = cite.get("proposition") or ""
    excerpts = [item.get("excerpt") or "" for item in hits if item.get("excerpt")]
    blob = " ".join(excerpts).lower()
    catalog = _catalog_for(cite)
    source_url = next((item.get("url") for item in hits if item.get("url")), None)

    if cite.get("kind") in {"ambiguous"}:
        return _check(
            "holding_support",
            "fail",
            "Holding support cannot be evaluated against an unresolved citation.",
            {"checked": "Surrounding proposition", "against": "No uniquely identified opinion"},
        )
    if not hits:
        return _check(
            "holding_support",
            "fail",
            "No opinion or statute text was retrieved, so the surrounding proposition is unsupported by this cite.",
            {"checked": proposition[:280] or "Citation only", "against": "No retrieved holding"},
        )

    wrong = catalog.get("wrong_holding")
    if wrong and proposition and wrong.search(proposition) and blob:
        if "warrant" in blob and ("cell-site" in blob or "location" in blob or "search" in blob):
            return _check(
                "holding_support",
                "fail",
                "The case exists in a public source, but the SAMPLE proposition claims warrantless collection. "
                "Fetched opinion text discusses a warrant requirement for this category of records. "
                "OWL did not invent a quotation — a person must reconcile the proposition with the opinion before filing.",
                {
                    "checked": proposition[:280],
                    "against": "Fetched public opinion/syllabus text (not a citator headnote)",
                    "sourceUrl": source_url,
                },
            )

    if proposition and blob:
        words = [word for word in re.findall(r"[a-z]{4,}", proposition.lower()) if word not in {"united", "states", "that", "this", "with", "from", "have"}]
        overlap = sum(1 for word in words[:12] if word in blob)
        if overlap >= 6:
            return _check(
                "holding_support",
                "needs-review",
                "Fetched public text overlaps words in the surrounding sentence, but OWL does not auto-pass holding support. A person must confirm the pin cite and that the proposition is not broader than the opinion.",
                {
                    "checked": proposition[:280],
                    "against": "Fetched public opinion or statute text",
                    "sourceUrl": source_url,
                },
            )

    return _check(
        "holding_support",
        "needs-review",
        "The citation resolved in a public source. Holding support still needs a person — OWL does not auto-pass a proposition without a clear match from fetched document text, and does not invent quotations.",
        {
            "checked": proposition[:280] or "Citation only — no surrounding proposition isolated",
            "against": "Fetched public source text" if blob else "Source hit without extractable opinion text",
            "sourceUrl": source_url,
        },
    )


def _human_review(detail: str) -> dict[str, Any]:
    return _check(
        "human_review_flag",
        "needs-review",
        detail,
        {
            "checked": "Whether a human still needs to look at this output",
            "against": "Filing accountability — the signer of the brief remains responsible",
        },
    )


def _sources_reachable(source_results: list[dict[str, Any]]) -> bool:
    for item in source_results:
        if item.get("matched") or item.get("status") in {"ok", "no_match"}:
            return True
        if item.get("http_status") in {200, 404}:
            return True
    return False


def evaluate_citation(cite: dict[str, Any], source_results: list[dict[str, Any]], index: int) -> dict[str, Any]:
    hits = [item for item in source_results if item.get("matched")]
    reachable = _sources_reachable(source_results)
    path_steps = []
    for item in source_results:
        what = "Returned a matching document." if item.get("matched") else (
            item.get("error") or item.get("status") or "No matching document"
        )
        path_steps.append(
            {
                "source": item.get("name") or item.get("id"),
                "url": item.get("url") if item.get("matched") or item.get("http_status") else item.get("url"),
                "what": what,
                "status": item.get("status"),
                "http_status": item.get("http_status"),
            }
        )

    error = None
    error_message = None
    format_status, format_detail = _format_status(cite)

    if cite.get("kind") == "ambiguous":
        error = "ambiguous"
        error_message = (
            "Ambiguous citation: this fragment does not include a page number or enough of the case name "
            "to uniquely resolve. Add the full reporter cite (volume, reporter, page, year)."
        )
        existence = _check(
            "existence",
            "needs-review",
            "Cannot confirm existence until the citation uniquely identifies one decision.",
            {"checked": cite.get("raw"), "against": "Public reporter set actually queried this run"},
        )
        holding = _check(
            "holding_support",
            "fail",
            "Holding support cannot be evaluated against an unresolved citation.",
            {"checked": cite.get("proposition") or "Surrounding proposition", "against": "No uniquely identified opinion"},
        )
        path = _check(
            "verification_path",
            "needs-review",
            "No verification path until the cite resolves to one source.",
            {"checked": cite.get("raw"), "against": "No unique public source"},
        )
        human = _human_review("Ambiguous citations must be expanded by a person before they can be verified or filed.")
    elif cite.get("kind") == "docket" and not hits:
        error = "source_unavailable"
        error_message = (
            "Source unavailable in the public corpus this check uses: magistrate/district docket numbers "
            "are not hosted as U.S. Reports, Cornell LII SCOTUS pages, Oyez, Justia SCOTUS, GovInfo statutes, "
            "or supremecourt.gov slip opinions. The check did not silently pass."
        )
        existence = _check(
            "existence",
            "needs-review",
            "Existence could not be confirmed in the six public source families queried this run.",
            {"checked": cite.get("raw"), "against": "Cornell LII, Oyez, CourtListener, Justia, GovInfo, supremecourt.gov"},
        )
        holding = _check(
            "holding_support",
            "needs-review",
            "Holding support was not evaluated because the opinion text was not in the public corpus queried.",
            {"checked": cite.get("proposition") or "Surrounding proposition", "against": "Opinion text not retrieved"},
        )
        path = _check(
            "verification_path",
            "fail",
            "Verification path stopped: none of the six public sources returned this docket.",
            {"checked": cite.get("raw"), "against": "Six public source families", "sourceUrl": None},
        )
        human = _human_review("When a source is outside the public corpus, a person must retrieve the document before relying on the cite.")
    elif not hits and not reachable:
        error = "source_unavailable"
        error_message = (
            "Source unavailable: the public legal sources queried this run timed out, blocked the request, "
            "or returned errors. Existence was not treated as a silent pass or as proof the cite is fake."
        )
        existence = _check(
            "existence",
            "needs-review",
            "Existence could not be confirmed because no public source returned a usable response.",
            {"checked": cite.get("key") or cite.get("raw"), "against": "Six public source families (unreachable this run)"},
        )
        holding = _check(
            "holding_support",
            "needs-review",
            "Holding support was not evaluated because opinion text was unavailable.",
            {"checked": cite.get("proposition") or "Surrounding proposition", "against": "Opinion text not retrieved"},
        )
        path = _check(
            "verification_path",
            "fail",
            "Verification path stopped: sources timed out, blocked, or errored.",
            {"checked": cite.get("key") or cite.get("raw"), "against": "Six public source families"},
        )
        human = _human_review("When sources are down, a person must retrieve the opinion from another reporter before relying on the cite.")
    elif not hits:
        error = "not_found"
        error_message = (
            "Citation not found: this reporter cite did not resolve in the public sources queried this run. "
            "Invented or mistyped citations fail explicitly."
        )
        existence = _check(
            "existence",
            "fail",
            "No matching decision or statute in the public sources that returned data this run.",
            {"checked": cite.get("key") or cite.get("raw"), "against": "Cornell LII, Oyez, CourtListener, Justia, GovInfo, supremecourt.gov"},
        )
        holding = _check(
            "holding_support",
            "fail",
            "No opinion was found, so the surrounding proposition is unsupported by this cite.",
            {"checked": cite.get("proposition") or "Surrounding proposition", "against": "No retrieved holding"},
        )
        tried = ", ".join(item.get("name") or item.get("id") for item in source_results)
        path = _check(
            "verification_path",
            "fail",
            f"Checked {cite.get('key') or cite.get('raw')} against {tried}. No record returned.",
            {"checked": cite.get("key") or cite.get("raw"), "against": tried},
        )
        human = _human_review(
            "A citation that does not exist must not be filed. A person should confirm whether this was a hallucination, a typo, or an unpublished disposition."
        )
    else:
        names = [item["name"] for item in hits]
        primary = hits[0]
        existence = _check(
            "existence",
            "pass",
            f"{catalog_name(cite)} exists in at least one public source that returned HTTP 200 this run.",
            {"checked": cite.get("key") or cite.get("raw"), "against": primary["name"], "sourceUrl": primary.get("url")},
        )
        holding = _holding_support(cite, hits)
        path = _check(
            "verification_path",
            "pass",
            "Checked against the six public source families. URLs below are the ones that actually returned a document.",
            {"checked": cite.get("key") or cite.get("raw"), "against": ", ".join(names), "sourceUrl": primary.get("url")},
        )
        human = _human_review(
            "Even a passing existence check requires a person to confirm the pin cite, subsequent history, and that the proposition is not overstated before filing. OWL is not a citator product."
        )

    normalized = (
        _catalog_for(cite).get("citation")
        or cite.get("key")
        or cite.get("raw")
    )
    checks = [
        existence,
        _check(
            "citation_format",
            format_status,
            format_detail,
            {"checked": cite.get("raw"), "against": "Bluebook-style volume / reporter / page, U.S.C., or FRCP"},
        ),
        holding,
        path,
        human,
    ]
    return {
        "id": _slug(normalized, index),
        "span": cite.get("span") or cite.get("raw"),
        "raw": cite.get("raw"),
        "normalized": normalized,
        "court": infer_court(cite),
        "year": cite.get("year") or _catalog_for(cite).get("year"),
        "toa_group": infer_toa_group(cite),
        "error": error,
        "errorMessage": error_message,
        "proposition": cite.get("proposition"),
        "verification_path": path_steps,
        "checks": checks,
        "sources": source_results,
    }


def catalog_name(cite: dict[str, Any]) -> str:
    return _catalog_for(cite).get("name") or cite.get("parties") or cite.get("key") or "This authority"


def overall_status(citation: dict[str, Any]) -> str:
    substantive = [item for item in citation.get("checks") or [] if item.get("id") != "human_review_flag"]
    if citation.get("error") == "not_found" or any(item.get("status") == "fail" for item in substantive):
        return "fail"
    if citation.get("error") in {"ambiguous", "source_unavailable"} or any(
        item.get("status") == "needs-review" for item in substantive
    ):
        return "needs-review"
    return "pass"


def build_toa(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups = [{**group, "entries": []} for group in TOA_GROUPS]
    by_id = {group["id"]: group for group in groups}
    for citation in citations:
        group = by_id.get(citation.get("toa_group") or "unresolved") or by_id["unresolved"]
        group["entries"].append(
            {
                "citationId": citation["id"],
                "cite": citation.get("normalized") or citation.get("raw"),
                "court": citation.get("court"),
                "year": citation.get("year"),
                "overall": overall_status(citation),
            }
        )
    return [group for group in groups if group["entries"]]


def build_audit(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "citationId": citation["id"],
            "cite": citation.get("normalized") or citation.get("raw"),
            "overall": overall_status(citation),
            "error": citation.get("error"),
            "flagged": overall_status(citation) != "pass",
            "checks": citation.get("checks") or [],
        }
        for citation in citations
    ]


def aggregate_sources(all_results: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    by_id: dict[str, list[dict[str, Any]]] = {item["id"]: [] for item in PUBLIC_LEGAL_SOURCES}
    for group in all_results:
        for item in group:
            by_id.setdefault(item["id"], []).append(item)
    summary = []
    for meta in PUBLIC_LEGAL_SOURCES:
        rows = by_id.get(meta["id"]) or []
        matched = [row for row in rows if row.get("matched")]
        blocked = [row for row in rows if row.get("status") == "blocked"]
        timeouts = [row for row in rows if row.get("status") == "timeout"]
        errors = [row for row in rows if row.get("status") == "error"]
        if matched:
            status = "ok"
            sample = matched[0]
        elif blocked and not matched:
            status = "blocked"
            sample = blocked[0]
        elif timeouts and len(timeouts) == len(rows):
            status = "timeout"
            sample = timeouts[0]
        elif errors and not matched:
            status = "error"
            sample = errors[0]
        else:
            status = "no_match"
            sample = rows[0] if rows else {}
        summary.append(
            {
                "id": meta["id"],
                "name": meta["name"],
                "status": status,
                "http_status": sample.get("http_status"),
                "error": sample.get("error") if status != "ok" else None,
                "url": sample.get("url"),
            }
        )
    return summary


def _empty_parse_citation(text: str) -> dict[str, Any]:
    trimmed = (text or "").strip()
    return evaluate_citation(
        {
            "kind": "ambiguous",
            "raw": trimmed or "(empty)",
            "span": trimmed,
            "key": "",
            "proposition": trimmed[:500],
            "volume": None,
            "reporter": None,
            "page": None,
        },
        [
            _empty_result(item["id"], item["url"], "no citation parsed", "no_match")
            for item in PUBLIC_LEGAL_SOURCES
        ],
        0,
    )


async def verify_citations(text: str, matter_id: str | None = None) -> dict[str, Any]:
    trimmed = (text or "").strip()
    parsed = parse_citations(trimmed)
    timeout = httpx.Timeout(REQUEST_TIMEOUT, connect=5.0)
    limits = httpx.Limits(max_connections=CONCURRENCY, max_keepalive_connections=CONCURRENCY)
    sem = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True) as client:
        source_groups = []
        if parsed:
            fetch_tasks = [
                asyncio.create_task(query_all_sources(cite, client, sem))
                for cite in parsed
            ]
            done, pending = await asyncio.wait(fetch_tasks, timeout=OVERALL_BUDGET)
            for task in pending:
                task.cancel()
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            for task in fetch_tasks:
                if task in done and task.exception() is None:
                    source_groups.append(task.result())
                else:
                    source_groups.append(
                        [
                            _empty_result(item["id"], item["url"], "timeout", "timeout")
                            for item in PUBLIC_LEGAL_SOURCES
                        ]
                    )

    citations = []
    if not parsed:
        citations = [_empty_parse_citation(trimmed)]
        source_groups = [citations[0]["sources"]]
    else:
        for index, (cite, group) in enumerate(zip(parsed, source_groups)):
            citations.append(evaluate_citation(cite, group, index))

    sources_queried = aggregate_sources(source_groups)
    live_hits = sum(1 for item in sources_queried if item.get("status") == "ok")
    meta = MATTER_META.get(matter_id or "")
    matter = None
    if meta:
        matter = {
            "id": matter_id,
            "title": meta["title"],
            "matter_name": meta["matter_name"],
            "practice_area": meta["practice_area"],
            "warning_banner": meta["warning_banner"],
            "default_selected": citations[0]["id"] if citations else None,
        }
        flagged = [item["id"] for item in citations if overall_status(item) != "pass"]
        if flagged:
            matter["default_selected"] = flagged[0]

    log.info(
        "verify complete citations=%s sources_ok=%s matter=%s",
        len(citations),
        live_hits,
        matter_id or "-",
    )
    return {
        "mode": "live",
        "input": trimmed,
        "excerpt": trimmed,
        "matter": matter,
        "citations": citations,
        "toa": build_toa(citations),
        "audit": build_audit(citations),
        "sources_queried": sources_queried,
        "disclaimer": (
            "OWL is a verification layer, not legal advice, and does not create an attorney-client relationship. "
            "Human review of all outputs is required. Public sources listed in sources_queried are what was actually "
            "contacted this run. OWL is not a citator product and does not replace a lawyer, a paralegal, or Westlaw/Lexis."
        ),
    }
