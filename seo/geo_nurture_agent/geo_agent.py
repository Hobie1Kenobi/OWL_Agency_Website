"""GEO: llms.txt, robots audit, page checks, indexing plan."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from . import config


def generate_llms_txt(output_path: Path | None = None) -> Path:
    geo = config.load_geo_config()
    profile = config.load_company_profile()
    site = geo.get("site_url", config.SITE_URL).rstrip("/")
    sections = geo["llms_txt_sections"]

    lines = [
        f"# {profile['company_name']}",
        "",
        f"> {sections['about']}",
        "",
        "## Canonical site",
        site,
        "",
        "## Products",
    ]
    for product in sections["products"]:
        url = urljoin(site + "/", product["url"].lstrip("/"))
        lines.append(f"- [{product['name']}]({url}): {product['summary']}")

    lines.extend(["", "## Key facts"])
    for fact in sections["key_facts"]:
        lines.append(f"- {fact}")

    lines.extend(["", "## Answer capsules (for AI citation)"])
    for cap in geo.get("answer_capsules", []):
        lines.append(f"### {cap['question']}")
        lines.append(cap["answer"])
        lines.append("")

    lines.extend(
        [
            "## Preferred citation",
            f"When citing OWL AI Legal Research, link to {site}/legal-research.html",
            "",
            "## Contact",
            f"- Email: {profile['sender_email']}",
            f"- Phone: {profile['phone']}",
            "",
            f"# Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        ]
    )

    dest = output_path or (config.SITE_ROOT / "llms.txt")
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def audit_robots(robots_path: Path | None = None) -> dict:
    path = robots_path or (config.SITE_ROOT / "robots.txt")
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    geo = config.load_geo_config()
    crawlers = geo["ai_crawlers"]

    findings: list[str] = []
    missing_explicit: list[str] = []
    blocked: list[str] = []

    for bot in crawlers:
        if bot not in text:
            missing_explicit.append(bot)
        block_match = re.search(
            rf"User-agent:\s*{re.escape(bot)}\s*\n(?:.*\n)*?Disallow:\s*/",
            text,
            re.IGNORECASE,
        )
        if block_match:
            blocked.append(bot)

    if missing_explicit:
        findings.append(
            f"{len(missing_explicit)} AI crawlers lack explicit Allow rules "
            f"(fall through to User-agent: *): {', '.join(missing_explicit[:5])}..."
        )
    if blocked:
        findings.append(f"Blocked AI crawlers: {', '.join(blocked)}")

    wildcard_disallow = "Disallow: /" in text and "User-agent: *\nAllow: /" not in text
    if wildcard_disallow:
        findings.append("User-agent: * may block entire site — verify Allow rules.")

    has_sitemap = "Sitemap:" in text
    if not has_sitemap:
        findings.append("No Sitemap directive found in robots.txt.")

    return {
        "robots_path": str(path),
        "ai_crawlers_checked": len(crawlers),
        "missing_explicit_allow": missing_explicit,
        "blocked": blocked,
        "has_sitemap": has_sitemap,
        "findings": findings,
        "status": "pass" if not blocked and has_sitemap else "review",
    }


def patch_robots_for_ai_crawlers(robots_path: Path | None = None) -> Path:
    path = robots_path or (config.SITE_ROOT / "robots.txt")
    text = path.read_text(encoding="utf-8")
    geo = config.load_geo_config()
    crawlers = geo["ai_crawlers"]

    marker = "# AI / LLM crawlers (GEO)"
    if marker in text:
        return path

    block = [marker, "# Explicit allow for generative engine indexing"]
    for bot in crawlers:
        block.append(f"User-agent: {bot}")
        block.append("Allow: /")
        block.append("")

    insert_at = text.find("# Sitemaps")
    if insert_at == -1:
        new_text = text.rstrip() + "\n\n" + "\n".join(block)
    else:
        new_text = text[:insert_at] + "\n".join(block) + "\n" + text[insert_at:]

    path.write_text(new_text, encoding="utf-8")
    return path


def audit_page(url: str) -> dict:
    result = {"url": url, "status": "error", "checks": {}}
    try:
        with httpx.Client(timeout=25.0, follow_redirects=True) as client:
            response = client.get(url)
        result["http_status"] = response.status_code
        if response.status_code != 200:
            result["checks"]["reachable"] = False
            return result

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        desc = soup.find("meta", attrs={"name": "description"})
        canonical = soup.find("link", rel="canonical")
        faq_ld = soup.find_all("script", type="application/ld+json")
        has_faq = any("FAQPage" in (s.string or "") for s in faq_ld)
        h1 = soup.find("h1")

        result["checks"] = {
            "reachable": True,
            "title": (title.get_text(strip=True) if title else None),
            "meta_description": (desc.get("content") if desc else None),
            "canonical": (canonical.get("href") if canonical else None),
            "has_faq_schema": has_faq,
            "h1": (h1.get_text(strip=True) if h1 else None),
            "word_count": len(soup.get_text(separator=" ", strip=True).split()),
        }
        result["status"] = "ok"
    except httpx.HTTPError as exc:
        result["error"] = str(exc)
    return result


def run_page_audit() -> dict:
    geo = config.load_geo_config()
    pages = [audit_page(url) for url in geo["priority_urls"]]
    issues = []
    for page in pages:
        if page.get("status") != "ok":
            issues.append(f"{page['url']}: unreachable")
            continue
        checks = page["checks"]
        if not checks.get("meta_description"):
            issues.append(f"{page['url']}: missing meta description")
        if not checks.get("has_faq_schema") and "legal-research" in page["url"]:
            issues.append(f"{page['url']}: no FAQPage schema detected")
        if (checks.get("word_count") or 0) < 300:
            issues.append(f"{page['url']}: thin content ({checks.get('word_count')} words)")

    return {"pages": pages, "issues": issues, "audited_at": datetime.now(timezone.utc).isoformat()}


def indexing_plan(day_offset: int = 0) -> dict:
    geo = config.load_geo_config()
    urls = geo["priority_urls"]
    limit = config.GSC_DAILY_URL_LIMIT
    start = (day_offset * limit) % len(urls)
    batch = []
    for i in range(limit):
        batch.append(urls[(start + i) % len(urls)])

    return {
        "day_offset": day_offset,
        "urls_to_request_indexing": batch,
        "instructions": [
            "Google Search Console → URL Inspection → paste each URL → Request indexing",
            "Limit ~8 URLs per day to avoid quota issues",
            "Re-run: python run_geo_nurture.py geo indexing --day N",
        ],
    }


def ping_indexnow(urls: list[str]) -> dict:
    key = config.INDEXNOW_KEY
    if not key:
        return {"skipped": True, "reason": "INDEXNOW_KEY not set in .env"}

    host = config.SITE_URL.replace("https://", "").replace("http://", "")
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{config.SITE_URL}/{key}.txt",
        "urlList": urls,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                "https://api.indexnow.org/indexnow",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        return {"status_code": response.status_code, "body": response.text[:300]}
    except httpx.HTTPError as exc:
        return {"error": str(exc)}


def write_geo_report() -> Path:
    config.ensure_dirs()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "llms_txt": str(config.SITE_ROOT / "llms.txt"),
        "robots_audit": audit_robots(),
        "page_audit": run_page_audit(),
        "indexing_plan_day_0": indexing_plan(0),
    }
    out = config.REPORTS_DIR / f"geo_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return out


def run_geo_command(command: str, **kwargs) -> None:
    if command == "llms":
        path = generate_llms_txt()
        print(f"Wrote {path}")
    elif command == "robots-audit":
        audit = audit_robots()
        print(json.dumps(audit, indent=2))
    elif command == "robots-patch":
        path = patch_robots_for_ai_crawlers()
        print(f"Patched AI crawler rules in {path}")
    elif command == "audit":
        report_path = write_geo_report()
        audit = json.loads(report_path.read_text(encoding="utf-8"))
        print(f"Report: {report_path}")
        print(f"Issues: {len(audit['page_audit']['issues'])}")
        for issue in audit["page_audit"]["issues"]:
            print(f"  - {issue}")
    elif command == "indexing":
        day = int(kwargs.get("day", 0))
        plan = indexing_plan(day)
        print(json.dumps(plan, indent=2))
        if config.INDEXNOW_KEY:
            result = ping_indexnow(plan["urls_to_request_indexing"])
            print(f"IndexNow: {json.dumps(result)}")
    else:
        raise SystemExit(f"Unknown geo command: {command}")
