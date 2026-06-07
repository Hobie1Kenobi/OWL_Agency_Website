import json
import os
from pathlib import Path

from dotenv import load_dotenv

AGENT_DIR = Path(__file__).resolve().parent
SEO_DIR = AGENT_DIR.parent
SITE_ROOT = SEO_DIR.parent
BACKEND_DIR = SITE_ROOT / "legal-research-backend"
INTAKE_DIR = BACKEND_DIR / "data" / "intakes"
DEMO_LEADS_DIR = BACKEND_DIR / "data" / "demo_leads"
REPORTS_DIR = AGENT_DIR / "reports"
LEADS_FILE = AGENT_DIR / "nurture_leads.csv"
GEO_CONFIG_FILE = AGENT_DIR / "geo_config.json"
SEQUENCES_FILE = AGENT_DIR / "nurture_sequences.json"
COMPANY_PROFILE_FILE = SEO_DIR / "outreach_agent" / "company_profile.json"

BACKEND_ENV = BACKEND_DIR / ".env"
load_dotenv(BACKEND_ENV)
load_dotenv(SEO_DIR / ".env")
load_dotenv(AGENT_DIR / ".env")

SITE_URL = os.getenv("GEO_SITE_URL", "https://owl-ai-agency.com").rstrip("/")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
NURTURE_FROM_EMAIL = os.getenv(
    "NURTURE_FROM_EMAIL",
    os.getenv("INTAKE_FROM_EMAIL", "OWL Legal Research <onboarding@resend.dev>"),
)
INTAKE_NOTIFY_EMAIL = os.getenv("INTAKE_NOTIFY_EMAIL", "sales@owl-ai-agency.com")

INDEXNOW_KEY = os.getenv("INDEXNOW_KEY", "")
GSC_DAILY_URL_LIMIT = int(os.getenv("GEO_GSC_DAILY_URL_LIMIT", "8"))

NURTURE_DELAYS_DAYS = {
    0: 0,
    1: 3,
    2: 7,
    3: 14,
}


def load_company_profile() -> dict:
    with open(COMPANY_PROFILE_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_geo_config() -> dict:
    with open(GEO_CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_sequences() -> dict:
    with open(SEQUENCES_FILE, encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
