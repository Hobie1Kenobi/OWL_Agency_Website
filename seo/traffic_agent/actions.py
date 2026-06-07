"""Automated traffic actions — instant tier and env credentials."""

from __future__ import annotations

import json
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import httpx

from . import config


def _log(action: str, status: str, detail: str) -> None:
    entry = {
        "at": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "status": status,
        "detail": detail[:500],
    }
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def indexnow_ping(urls: list[str] | None = None) -> dict:
    key = config.INDEXNOW_KEY
    if not key:
        return {"skipped": True, "reason": "Set INDEXNOW_KEY in legal-research-backend/.env"}

    host = config.SITE_URL.replace("https://", "").replace("http://", "")
    url_list = urls or config.PRIORITY_URLS
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"{config.SITE_URL}/{key}.txt",
        "urlList": url_list,
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post("https://api.indexnow.org/indexnow", json=payload)
        ok = r.status_code in (200, 202)
        _log("indexnow", "ok" if ok else "error", f"{r.status_code} {len(url_list)} urls")
        return {"status_code": r.status_code, "urls": len(url_list), "body": r.text[:200]}
    except httpx.HTTPError as e:
        _log("indexnow", "error", str(e))
        return {"error": str(e)}


def bing_sitemap_ping() -> dict:
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            r = client.get(
                "https://www.bing.com/ping",
                params={"sitemap": config.SITEMAP_URL},
            )
        ok = r.status_code == 200
        _log("bing_ping", "ok" if ok else "error", str(r.status_code))
        return {"status_code": r.status_code}
    except httpx.HTTPError as e:
        _log("bing_ping", "error", str(e))
        return {"error": str(e)}


def pingomatic() -> dict:
    site = config.SITE_URL
    blog_name = "OWL AI Agency Legal Research"
    xml = f"""<?xml version="1.0"?>
<methodCall>
  <methodName>weblogUpdates.ping</methodName>
  <params>
    <param><value>{blog_name}</value></param>
    <param><value>{site}/</value></param>
  </params>
</methodCall>"""
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.post(
                "https://rpc.pingomatic.com/",
                content=xml,
                headers={"Content-Type": "text/xml"},
            )
        ok = r.status_code == 200 and "flerror" not in r.text.lower()
        _log("pingomatic", "ok" if ok else "error", str(r.status_code))
        return {"status_code": r.status_code, "snippet": r.text[:150]}
    except httpx.HTTPError as e:
        _log("pingomatic", "error", str(e))
        return {"error": str(e)}


def wayback_save(urls: list[str] | None = None, delay: float = 2.0) -> dict:
    targets = urls or config.PRIORITY_URLS[:8]
    results = []
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        for url in targets:
            save_url = f"https://web.archive.org/save/{quote(url, safe=':/')}"
            try:
                r = client.get(save_url)
                ok = r.status_code in (200, 302)
                results.append({"url": url, "status": r.status_code, "ok": ok})
                _log("wayback", "ok" if ok else "error", url)
            except httpx.HTTPError as e:
                results.append({"url": url, "error": str(e)})
                _log("wayback", "error", str(e))
            time.sleep(delay)
    saved = sum(1 for x in results if x.get("ok"))
    return {"saved": saved, "total": len(targets), "results": results}


def cloudflare_purge(urls: list[str] | None = None) -> dict:
    token = config.CLOUDFLARE_API_TOKEN
    zone = config.CLOUDFLARE_ZONE_ID
    if not token or not zone or token.startswith("your_"):
        return {"skipped": True, "reason": "CLOUDFLARE_API_TOKEN or ZONE_ID not set"}

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"purge_everything": True} if not urls else {"files": urls}
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                f"https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache",
                headers=headers,
                json=body,
            )
        data = r.json()
        ok = data.get("success", False)
        _log("cloudflare_purge", "ok" if ok else "error", json.dumps(data)[:200])
        return {"success": ok, "response": data}
    except httpx.HTTPError as e:
        _log("cloudflare_purge", "error", str(e))
        return {"error": str(e)}


def llms_refresh() -> dict:
    try:
        from geo_nurture_agent.geo_agent import generate_llms_txt

        path = generate_llms_txt(config.SITE_ROOT / "llms.txt")
        _log("llms_refresh", "ok", str(path))
        return {"path": str(path)}
    except Exception as e:
        _log("llms_refresh", "error", str(e))
        return {"error": str(e)}


def ensure_syndication_hub() -> dict:
    """On-site hub — no external account; drives internal links + crawl paths."""
    resources_dir = config.SITE_ROOT / "resources"
    resources_dir.mkdir(parents=True, exist_ok=True)
    profile = config.load_profile()
    site = config.SITE_URL
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <link rel="canonical" href="{site}/resources/" />
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>OWL Legal Research Resources — Demos, Comparisons &amp; Guides</title>
  <meta name="description" content="Official OWL AI Agency resource hub: live Carpenter SCOTUS demo, OWL vs ChatGPT, OWL vs manual research, pricing, and intake for law firms."/>
  <link href="../assets/css/style.css" rel="stylesheet"/>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"CollectionPage","name":"OWL Legal Research Resources",
    "url":"{site}/resources/","publisher":{{"@type":"Organization","name":"{profile['company_name']}"}}}}
  </script>
</head>
<body class="container py-5" style="padding-top:100px">
  <h1>OWL Legal Research Resources</h1>
  <p>By <strong>{profile['sender_name']}</strong>, {profile['sender_title']} — {profile['company_name']}</p>
  <ul>
    <li><a href="../legal-research-demo.html?autostart=1">Live demo — Carpenter v. United States</a></li>
    <li><a href="../compare/owl-vs-chatgpt-legal-research.html">OWL vs ChatGPT for legal research</a></li>
    <li><a href="../compare/owl-vs-manual-legal-research.html">OWL vs manual paralegal research</a></li>
    <li><a href="../legal-research.html">Product &amp; pricing</a></li>
    <li><a href="../llms.txt">llms.txt (AI citation file)</a></li>
    <li><a href="../blog/legal-research-automation.html">Blog: legal research automation</a></li>
  </ul>
  <p>Contact: <a href="mailto:{profile['sender_email']}">{profile['sender_email']}</a> · {profile['phone']}</p>
  <p class="text-muted small">Updated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</p>
</body>
</html>
"""
    index_path = resources_dir / "index.html"
    index_path.write_text(html, encoding="utf-8")
    _log("site_syndication", "ok", str(index_path))
    return {"path": str(index_path), "url": f"{site}/resources/"}


def sitemap_urls_from_file() -> list[str]:
    path = config.SITE_ROOT / "sitemap.xml"
    if not path.exists():
        return config.PRIORITY_URLS
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in root.findall(".//sm:loc", ns) if loc.text]


def run_instant_tier() -> list[dict]:
    results = []
    results.append({"action": "llms_refresh", **llms_refresh()})
    results.append({"action": "site_syndication", **ensure_syndication_hub()})
    results.append({"action": "indexnow", **indexnow_ping()})
    results.append({"action": "bing_ping", **bing_sitemap_ping()})
    results.append({"action": "pingomatic", **pingomatic()})
    results.append({"action": "wayback", **wayback_save()})
    results.append({"action": "cloudflare_purge", **cloudflare_purge()})
    return results
