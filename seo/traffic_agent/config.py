import json
import os
from pathlib import Path

from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parent
SEO_DIR = AGENT_DIR.parent
SITE_ROOT = SEO_DIR.parent
REGISTRY_FILE = AGENT_DIR / "platforms_registry.json"
TRACKER_FILE = AGENT_DIR / "traffic_tracker.csv"
DRAFTS_DIR = AGENT_DIR / "drafts"
PAYLOADS_DIR = AGENT_DIR / "payloads"
LOG_FILE = AGENT_DIR / "traffic_log.jsonl"
COMPANY_PROFILE = SEO_DIR / "outreach_agent" / "company_profile.json"

load_dotenv(SITE_ROOT / "legal-research-backend" / ".env")
load_dotenv(SEO_DIR / ".env")
load_dotenv(AGENT_DIR / ".env")

SITE_URL = os.getenv("TRAFFIC_SITE_URL", "https://owl-ai-agency.com").rstrip("/")
SITEMAP_URL = f"{SITE_URL}/sitemap.xml"
INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "")

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "")

ZOHO_FROM = os.getenv("ZOHO_FROM_EMAIL", "hobiecunningham@owl-ai-agency.com")
ZOHO_APP_PASSWORD = os.getenv("ZOHO_APP_PASSWORD", "")

TRAFFIC_EMAIL_DELAY = int(os.getenv("TRAFFIC_EMAIL_DELAY", "120"))

PRIORITY_URLS = [
    f"{SITE_URL}/",
    f"{SITE_URL}/legal-research.html",
    f"{SITE_URL}/legal-research-demo.html",
    f"{SITE_URL}/compare/owl-vs-chatgpt-legal-research.html",
    f"{SITE_URL}/compare/owl-vs-manual-legal-research.html",
    f"{SITE_URL}/compare/",
    f"{SITE_URL}/llms.txt",
    f"{SITE_URL}/blog/legal-research-automation.html",
    f"{SITE_URL}/blog/batch-processing-legal-research.html",
    SITEMAP_URL,
]


def load_registry() -> dict:
    with open(REGISTRY_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_profile() -> dict:
    with open(COMPANY_PROFILE, encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs() -> None:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)
