"""
Public legal data connectors — no API keys required.

Sources used:
  - Cornell LII (law.cornell.edu) — opinions & U.S. Code
  - Oyez (oyez.org / api.oyez.org) — Supreme Court metadata
  - CourtListener (courtlistener.com) — public opinion pages
  - Justia (supreme.justia.com) — case summaries
  - GovInfo (govinfo.gov) — federal statutes
  - Supreme Court (supremecourt.gov) — official slip opinions
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

USER_AGENT = "OWL-Legal-Research-Demo/1.0 (+https://owl-ai-agency.com/legal-research-demo.html)"
TIMEOUT = 15.0

PUBLIC_LEGAL_SOURCES = [
    {
        "id": "cornell_lii",
        "name": "Cornell Legal Information Institute",
        "url": "https://www.law.cornell.edu",
        "requires_api_key": False,
        "data_types": ["opinions", "statutes", "rules"],
    },
    {
        "id": "oyez",
        "name": "Oyez (Chicago-Kent IIT)",
        "url": "https://www.oyez.org",
        "requires_api_key": False,
        "data_types": ["scotus_metadata", "oral_arguments", "vote_breakdown"],
    },
    {
        "id": "courtlistener",
        "name": "CourtListener / Free Law Project",
        "url": "https://www.courtlistener.com",
        "requires_api_key": False,
        "data_types": ["opinions", "dockets", "citations"],
    },
    {
        "id": "justia",
        "name": "Justia U.S. Supreme Court Center",
        "url": "https://supreme.justia.com",
        "requires_api_key": False,
        "data_types": ["summaries", "opinions"],
    },
    {
        "id": "govinfo",
        "name": "GovInfo (U.S. Government Publishing Office)",
        "url": "https://www.govinfo.gov",
        "requires_api_key": False,
        "data_types": ["statutes", "us_code"],
    },
    {
        "id": "supremecourt_gov",
        "name": "Supreme Court of the United States",
        "url": "https://www.supremecourt.gov",
        "requires_api_key": False,
        "data_types": ["slip_opinions", "orders"],
    },
]


async def _get(client: httpx.AsyncClient, url: str) -> httpx.Response | None:
    try:
        response = await client.get(url, follow_redirects=True)
        if response.status_code == 200:
            return response
    except httpx.HTTPError:
        pass
    return None


async def fetch_oyez_case(docket: str = "16-402") -> dict[str, Any]:
    """Oyez public JSON API — no authentication."""
    url = f"https://api.oyez.org/cases/{docket}"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await _get(client, url)
        if response:
            return {"source": "oyez", "url": url, "data": response.json(), "status": "live"}
    return {"source": "oyez", "url": url, "data": None, "status": "unavailable"}


async def fetch_cornell_opinion(path: str) -> dict[str, Any]:
    """Fetch opinion text from Cornell LII public pages."""
    url = f"https://www.law.cornell.edu{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await _get(client, url)
        if not response:
            return {"source": "cornell_lii", "url": url, "excerpt": None, "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("article") or soup.find("div", class_="field-body")
        text = article.get_text("\n", strip=True) if article else ""
        excerpt = text[:1200] + ("..." if len(text) > 1200 else "")
        return {"source": "cornell_lii", "url": url, "excerpt": excerpt, "status": "live"}


async def fetch_courtlistener_opinion(slug: str) -> dict[str, Any]:
    """CourtListener public opinion pages — browseable without login."""
    url = f"https://www.courtlistener.com/opinion/{slug}/"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await _get(client, url)
        if not response:
            return {"source": "courtlistener", "url": url, "title": None, "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        title_el = soup.find("h1")
        title = title_el.get_text(strip=True) if title_el else None
        return {"source": "courtlistener", "url": url, "title": title, "status": "live"}


async def search_cornell(query: str) -> dict[str, Any]:
    """Cornell LII site search (public HTML results)."""
    url = f"https://www.law.cornell.edu/search/site/{quote(query)}"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await _get(client, url)
        if not response:
            return {"source": "cornell_lii_search", "url": url, "results": [], "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for item in soup.select(".search-result, .search-results li, ol.search-results > li")[:5]:
            link = item.find("a")
            if link and link.get("href"):
                results.append({"title": link.get_text(strip=True), "url": link["href"]})
        return {"source": "cornell_lii_search", "url": url, "results": results, "status": "live"}


async def fetch_govinfo_statute(title: int, section: str) -> dict[str, Any]:
    """GovInfo US Code granule links are public."""
    url = f"https://www.govinfo.gov/app/details/USCODE-2017-title{title}/USCODE-2017-title{title}-sec{section}"
    async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
        response = await _get(client, url)
        status = "live" if response else "unavailable"
        return {
            "source": "govinfo",
            "url": url,
            "citation": f"{title} U.S.C. § {section}",
            "status": status,
        }


async def gather_carpenter_sources() -> list[dict[str, Any]]:
    """Pull live metadata from public sources for the demo case."""
    tasks = [
        fetch_oyez_case("16-402"),
        fetch_cornell_opinion("/supremecourt/text/18/946"),
        fetch_courtlistener_opinion("4379486"),
        search_cornell("Carpenter Fourth Amendment cell-site"),
        fetch_govinfo_statute(18, "2703"),
    ]
    import asyncio

    results = await asyncio.gather(*tasks, return_exceptions=True)
    sources: list[dict[str, Any]] = []
    for result in results:
        if isinstance(result, dict):
            sources.append(result)
        else:
            sources.append({"status": "error", "detail": str(result)})
    return sources


def list_public_sources() -> list[dict[str, Any]]:
    return PUBLIC_LEGAL_SOURCES
