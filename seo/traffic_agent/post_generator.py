"""Generate ready-to-post copy for platforms that need manual accounts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config

TEMPLATES = {
    "product_hunt": """# Product Hunt — OWL Legal Research

**Tagline:** Six AI agents verify live legal sources and draft court-ready memos

**Description:**
OWL Legal Research runs a six-agent paralegal pipeline for law firms—not a chatbot. It queries Cornell LII, Oyez, CourtListener, and GovInfo during each run and outputs memos, briefs, and Bluebook tables of authorities.

Try the public Carpenter v. United States demo (no signup):
{demo_url}

Compare vs ChatGPT: {site}/compare/owl-vs-chatgpt-legal-research.html

**Maker comment:** Hi PH — I'm Hobie, founder. We built this after seeing one too many AI briefs with fake citations. Happy to answer questions about the agent architecture.

**Topics:** Legal Tech, AI, Productivity, Developer Tools
""",
    "hacker_news": """Title: Show HN: Six-agent legal research pipeline with live source verification

We built OWL Legal Research — a multi-agent system that queries public legal DBs (Cornell LII, Oyez, CourtListener, GovInfo) and produces memos/briefs with citations, not a single LLM chat.

Public demo on Carpenter v. United States (585 U.S. 946):
{demo_url}

Backend is FastAPI + agent orchestrator on Render; frontend is static GitHub Pages.

Comparison write-up vs generic ChatGPT legal use:
{site}/compare/owl-vs-chatgpt-legal-research.html

Would love feedback from anyone who's dealt with legal citation hallucinations.
""",
    "quora": """Question: Can ChatGPT be used for legal research in a law firm?

**Answer (post as Hobie Cunningham, legal tech founder):**

ChatGPT is useful for brainstorming, but I would not file its output without independent cite-checking. Courts have sanctioned attorneys for AI-generated fake citations.

What works better for firm workflows is a structured pipeline that verifies live public legal databases during each run—not one chat session. At OWL AI Agency we use six agents (research, precedent, analysis, citation, brief, filing) and attach retrievable URLs to authorities.

You can see this on a public SCOTUS demo (Carpenter v. United States):
{demo_url}

We also published a comparison guide:
{site}/compare/owl-vs-chatgpt-legal-research.html

Attorney review is still required before filing; automation compresses paralegal hours on source gathering and first drafts.
""",
    "quora_cost": """Question: How much does legal research automation cost for a small law firm?

**Answer:**

For structured AI legal research (not generic chat subscriptions), OWL AI Agency offers project packages:

- Starter $3,000 — 25 research runs, 72-hour SLA
- Professional $6,000 — 75 runs, 48-hour SLA  
- Enterprise $12,000 — unlimited runs, 24-hour SLA

Each run produces memos, briefs, and citation-verified tables of authorities after querying live public legal sources. Free consultation available to scope jurisdiction and deliverables:

{site}/legal-research.html#intake

Demo (no payment): {demo_url}
""",
    "indie_hackers": """# Building a six-agent legal research product (week 1)

I'm Hobie, building OWL Legal Research — automating paralegal-grade research for law firms.

**Problem:** Paralegals spend 4–8 hours on complex matters; generic AI hallucinates citations.

**Solution:** Six agents + live verification against Cornell LII, Oyez, CourtListener, GovInfo.

**Traction:** Public Carpenter v. US demo, comparison pages for SEO/GEO, directory outreach.

**Stack:** FastAPI on Render, static site on GitHub Pages, Resend for nurture, Zoho for outreach.

**Ask:** Feedback on positioning — law firms vs legal ops vs solo attorneys?

Demo: {demo_url}
""",
    "devto": """---
title: Building a Multi-Agent Legal Research Pipeline with Live Source Verification
tags: ai, legal, python, fastapi
---

Law firms don't need another chatbot—they need **verified citations**.

## Architecture

Six agents: Research → Precedent → Analysis → Citation → Brief Writer → Filing.

Each run queries public legal APIs/pages (Cornell LII, Oyez, CourtListener, GovInfo).

## Demo

Public Carpenter v. United States walkthrough:
{demo_url}

## Code

FastAPI orchestrator on Render; agents produce memos, briefs, TOA.

## Compare

Why not ChatGPT alone: {site}/compare/owl-vs-chatgpt-legal-research.html

— Hobie Cunningham, OWL AI Agency
""",
}


def generate_form_payload(platform: dict, profile: dict) -> dict:
    site = config.SITE_URL
    return {
        "platform": platform["id"],
        "url": platform.get("url", ""),
        "fields": {
            "product_name": "OWL Legal Research",
            "company": profile["company_name"],
            "website": site,
            "demo": profile["demo_url"],
            "description": profile["value_proposition"],
            "contact_name": profile["sender_name"],
            "contact_email": profile["sender_email"],
            "phone": profile["phone"],
            "tags": "legal research, AI, paralegal, law firm, citations",
        },
    }


def generate_all_drafts() -> list[Path]:
    config.ensure_dirs()
    profile = config.load_profile()
    site = config.SITE_URL
    demo = profile["demo_url"]
    registry = config.load_registry()
    written: list[Path] = []

    for platform in registry["platforms"]:
        if platform.get("action") == "generate_post":
            post_type = platform.get("post_type", platform["id"])
            template = TEMPLATES.get(post_type, "")
            if not template:
                continue
            text = template.format(site=site, demo_url=demo)
            out = config.DRAFTS_DIR / f"{platform['id']}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
            out.write_text(text, encoding="utf-8")
            written.append(out)

        elif platform.get("action") == "form_payload":
            payload = generate_form_payload(platform, profile)
            out = config.PAYLOADS_DIR / f"{platform['id']}_payload.json"
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            written.append(out)

    return written
