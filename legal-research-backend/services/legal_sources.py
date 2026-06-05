"""
Public legal data connectors — no API keys required.

Sources used:
  - Cornell LII (law.cornell.edu) — opinions, U.S. Code, Constitution
  - Oyez (oyez.org / api.oyez.org) — Supreme Court metadata
  - CourtListener (storage.courtlistener.com) — public opinion PDFs
  - Justia (supreme.justia.com) — case summaries (Wayback mirror fallback)
  - GovInfo (govinfo.gov) — federal statutes
  - Supreme Court (supremecourt.gov) — official slip opinions
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (compatible; OWL-Legal-Research-Demo/1.0; "
    "+https://owl-ai-agency.com/legal-research-demo.html)"
)
TIMEOUT = 20.0

CARPENTER = {
    "docket": "16-402",
    "cornell_opinion_path": "/supremecourt/text/16-402",
    "courtlistener_pdf": (
        "https://storage.courtlistener.com/pdf/2018/06/22/carpenter_v._united_states.pdf"
    ),
    "courtlistener_page": (
        "https://www.courtlistener.com/opinion/4379486/carpenter-v-united-states/"
    ),
    "justia_url": "https://supreme.justia.com/cases/federal/us/585/16-402/",
    "justia_mirror": (
        "https://web.archive.org/web/2023/"
        "https://supreme.justia.com/cases/federal/us/585/16-402/"
    ),
    "scotus_pdf": "https://www.supremecourt.gov/opinions/17pdf/16-402_h315.pdf",
}

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


def _default_headers(accept: str = "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8") -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": accept,
        "Accept-Language": "en-US,en;q=0.9",
    }


async def _get(
    client: httpx.AsyncClient,
    url: str,
    *,
    accept: str | None = None,
    min_bytes: int = 500,
) -> httpx.Response | None:
    headers = _default_headers(accept) if accept else _default_headers()
    try:
        response = await client.get(url, headers=headers, follow_redirects=True)
        if response.status_code == 200 and len(response.content) >= min_bytes:
            return response
    except httpx.HTTPError:
        pass
    return None


def _extract_html_text(soup: BeautifulSoup, *selectors: str) -> str:
    for selector in selectors:
        node = soup.select_one(selector)
        if node:
            return node.get_text("\n", strip=True)
    return ""


async def fetch_oyez_case(term: str = "2017", docket: str = "16-402") -> dict[str, Any]:
    """Oyez public JSON API — no authentication."""
    url = f"https://api.oyez.org/cases/{term}/{docket}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url, accept="application/json", min_bytes=50)
        if response:
            data = response.json()
            if isinstance(data, dict):
                return {
                    "source": "oyez",
                    "url": url,
                    "data": {
                        "name": data.get("name"),
                        "docket_number": data.get("docket_number"),
                        "decided": data.get("decided"),
                    },
                    "status": "live",
                }
    return {"source": "oyez", "url": url, "data": None, "status": "unavailable"}


async def fetch_cornell_opinion(path: str) -> dict[str, Any]:
    """Fetch opinion text from Cornell LII public pages."""
    url = f"https://www.law.cornell.edu{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url)
        if not response:
            return {"source": "cornell_lii", "url": url, "excerpt": None, "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        text = _extract_html_text(
            soup,
            "article",
            "div.field-body",
            "div#documentcontent",
            "div#tab-opinion",
        )
        if not text:
            text = soup.get_text("\n", strip=True)
        excerpt = text[:1200] + ("..." if len(text) > 1200 else "")
        return {
            "source": "cornell_lii",
            "url": url,
            "excerpt": excerpt,
            "title": "Carpenter v. United States",
            "status": "live",
        }


async def fetch_cornell_statute(title: int, section: str) -> dict[str, Any]:
    """Cornell LII U.S. Code — public HTML."""
    url = f"https://www.law.cornell.edu/uscode/text/{title}/{section}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url)
        if not response:
            return {
                "source": "cornell_lii_statute",
                "url": url,
                "citation": f"{title} U.S.C. § {section}",
                "status": "unavailable",
            }

        soup = BeautifulSoup(response.text, "html.parser")
        excerpt = _extract_html_text(soup, "div.field-body", "article")[:600]
        return {
            "source": "cornell_lii_statute",
            "url": url,
            "citation": f"{title} U.S.C. § {section}",
            "excerpt": excerpt,
            "status": "live",
        }


async def fetch_cornell_constitution(amendment: int) -> dict[str, Any]:
    """Cornell LII Constitution Annotated."""
    url = f"https://www.law.cornell.edu/constitution-conan/amendment-{amendment}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url)
        if not response:
            return {
                "source": "cornell_lii_constitution",
                "url": url,
                "citation": f"U.S. Const. amend. {amendment}",
                "status": "unavailable",
            }

        soup = BeautifulSoup(response.text, "html.parser")
        excerpt = _extract_html_text(soup, "article", "div.field-body")[:600]
        return {
            "source": "cornell_lii_constitution",
            "url": url,
            "citation": f"U.S. Const. amend. {amendment}",
            "excerpt": excerpt,
            "status": "live",
        }


async def fetch_cornell_precedent(path: str, case_name: str) -> dict[str, Any]:
    """Retrieve a controlling precedent opinion from Cornell LII."""
    url = f"https://www.law.cornell.edu{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url)
        if not response:
            return {
                "source": "cornell_lii_precedent",
                "url": url,
                "title": case_name,
                "status": "unavailable",
            }

        soup = BeautifulSoup(response.text, "html.parser")
        excerpt = _extract_html_text(soup, "article", "div.field-body")[:400]
        return {
            "source": "cornell_lii_precedent",
            "url": url,
            "title": case_name,
            "excerpt": excerpt,
            "status": "live",
        }


async def search_cornell(query: str) -> dict[str, Any]:
    """Cornell LII site search (public HTML results)."""
    url = f"https://www.law.cornell.edu/search?query={quote(query)}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url, min_bytes=100)
        if not response:
            return {"source": "cornell_lii_search", "url": url, "results": [], "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            title = link.get_text(strip=True)
            if not title or len(title) < 8:
                continue
            if "carpenter" in title.lower() or "cell-site" in title.lower() or "fourth amendment" in title.lower():
                results.append({"title": title, "url": href})
            if len(results) >= 5:
                break

        return {
            "source": "cornell_lii_search",
            "url": url,
            "results": results,
            "result_count": len(results),
            "status": "live",
        }


async def fetch_courtlistener_opinion_pdf(
    pdf_url: str,
    page_url: str,
    title: str = "Carpenter v. United States",
) -> dict[str, Any]:
    """
    CourtListener HTML is WAF-protected from datacenter IPs; the public
    storage PDF endpoint is reachable without authentication.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(
            client,
            pdf_url,
            accept="application/pdf,*/*",
            min_bytes=10_000,
        )
        if not response:
            return {
                "source": "courtlistener",
                "url": page_url,
                "title": None,
                "status": "unavailable",
            }

        content_type = response.headers.get("content-type", "")
        is_pdf = "pdf" in content_type.lower() or response.content[:4] == b"%PDF"
        return {
            "source": "courtlistener",
            "url": page_url,
            "pdf_url": pdf_url,
            "title": title,
            "bytes": len(response.content),
            "format": "pdf" if is_pdf else "unknown",
            "status": "live" if is_pdf else "unavailable",
        }


async def fetch_justia_case(primary_url: str, mirror_url: str) -> dict[str, Any]:
    """Justia blocks many server IPs; fall back to an Internet Archive mirror."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, primary_url)
        used_url = primary_url
        if not response:
            response = await _get(client, mirror_url)
            used_url = mirror_url
        if not response:
            return {"source": "justia", "url": primary_url, "summary": None, "status": "unavailable"}

        soup = BeautifulSoup(response.text, "html.parser")
        summary = _extract_html_text(soup, "div#syllabus", "div.opinion", "article")[:800]
        if not summary:
            summary = soup.get_text("\n", strip=True)[:800]
        return {
            "source": "justia",
            "url": used_url,
            "canonical_url": primary_url,
            "summary": summary,
            "mirror": used_url != primary_url,
            "status": "live",
        }


async def fetch_govinfo_statute(title: int, section: str) -> dict[str, Any]:
    """GovInfo US Code granule links are public."""
    url = (
        f"https://www.govinfo.gov/app/details/USCODE-2017-title{title}/"
        f"USCODE-2017-title{title}-sec{section}"
    )
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, url, min_bytes=100)
        status = "live" if response else "unavailable"
        return {
            "source": "govinfo",
            "url": url,
            "citation": f"{title} U.S.C. § {section}",
            "status": status,
        }


async def fetch_supremecourt_slip_opinion(pdf_url: str) -> dict[str, Any]:
    """Official SCOTUS slip opinion PDF."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await _get(client, pdf_url, accept="application/pdf,*/*", min_bytes=10_000)
        if not response:
            return {
                "source": "supremecourt_gov",
                "url": pdf_url,
                "status": "unavailable",
            }

        text_sample = response.content[:5000].decode("latin-1", errors="ignore")
        docket_match = re.search(r"No\.\s*16[–-]402", text_sample)
        return {
            "source": "supremecourt_gov",
            "url": pdf_url,
            "bytes": len(response.content),
            "docket_confirmed": bool(docket_match),
            "status": "live",
        }


async def gather_carpenter_sources() -> list[dict[str, Any]]:
    """Pull live metadata from all public sources for the demo case."""
    import asyncio

    tasks = [
        fetch_oyez_case("2017", CARPENTER["docket"]),
        fetch_cornell_opinion(CARPENTER["cornell_opinion_path"]),
        fetch_courtlistener_opinion_pdf(
            CARPENTER["courtlistener_pdf"],
            CARPENTER["courtlistener_page"],
        ),
        fetch_justia_case(CARPENTER["justia_url"], CARPENTER["justia_mirror"]),
        fetch_govinfo_statute(18, "2703"),
        fetch_supremecourt_slip_opinion(CARPENTER["scotus_pdf"]),
        search_cornell("Carpenter cell-site Fourth Amendment"),
        fetch_cornell_statute(18, "2703"),
        fetch_cornell_constitution(4),
        fetch_cornell_precedent("/supremecourt/text/389/347", "Katz v. United States"),
        fetch_cornell_precedent("/supremecourt/text/10-1259", "United States v. Jones"),
        fetch_cornell_precedent("/supremecourt/text/13-132", "Riley v. California"),
    ]

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
