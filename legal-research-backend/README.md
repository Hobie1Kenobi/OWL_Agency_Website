# OWL Legal Research Backend

Multi-agent paralegal API for the **Carpenter v. United States** demo.

## Agents

| Agent | Role |
|-------|------|
| Research Agent | Retrieves primary sources from public legal databases |
| Precedent Agent | Maps controlling authority chain (Katz → Jones → Riley → Carpenter) |
| Analysis Agent | IRAC issue spotting and application |
| Citation Agent | Bluebook formatting and Table of Authorities |
| Brief Writer Agent | Drafts court-ready prose |
| Filing Agent | Assembles e-filing package with certificate of service |

## Public Legal Sources (No API Keys)

- **Cornell LII** — opinions, U.S. Code, rules
- **Oyez** — SCOTUS metadata (public JSON API)
- **CourtListener** — public opinion pages (Free Law Project)
- **Justia** — case summaries
- **GovInfo** — federal statutes
- **SupremeCourt.gov** — slip opinions

## Local Development

```bash
cd legal-research-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open `legal-research-demo.html` locally (Live Server on port 5500 is in CORS allowlist).

API docs: http://localhost:8000/docs

## Deploy to Render (Free Tier)

### Option A — Docker (recommended, always Python 3.11)

1. Push this repo to GitHub
2. Render Dashboard → your Web Service → **Settings**
3. Set **Language** to **Docker**
4. **Root Directory:** `legal-research-backend`
5. **Dockerfile Path:** `Dockerfile` (relative to root directory)
6. Add environment variable: `ALLOWED_ORIGINS=https://owl-ai-agency.com,https://hobie1kenobi.github.io`
7. Deploy

### Option B — Native Python (current service)

Render **cannot convert** an existing Python service to Docker. Use this path:

1. **Root Directory:** `legal-research-backend`
2. **Build Command:** `./build.sh` (or `pip install --upgrade pip && pip install -r requirements.txt`)
3. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. On the **Web Service → Environment** tab (not only Environment Group), add:
   - `PYTHON_VERSION` = `3.11.11` (fully qualified)
   - `ALLOWED_ORIGINS` = `https://owl-ai-agency.com,https://hobie1kenobi.github.io`
5. When saving env vars, choose **Save, rebuild, and deploy**

Requirements use `pydantic>=2.13` which has pre-built wheels for Python 3.14, so builds succeed even if `PYTHON_VERSION` is not applied.

### Render CLI (optional)

Install: https://render.com/docs/cli

```bash
render login
render services list
render services update srv-YOUR_ID --env-var PYTHON_VERSION=3.11.11 --env-var ALLOWED_ORIGINS=https://owl-ai-agency.com,https://hobie1kenobi.github.io
```

Then trigger Manual Deploy in the dashboard.

### Keep-Alive (Optional)

Render free tier sleeps after 15 min idle. Use [cron-job.org](https://cron-job.org) (free) to ping `/health` every 14 minutes.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/sources` | List public legal data systems |
| GET | `/api/cases` | Available demo cases |
| POST | `/api/intake` | Submit legal research intake form |
| GET | `/api/intake/{id}` | Look up intake by reference number |
| GET | `/api/tiers` | List paid tier entitlements |
| GET | `/api/config/stripe` | Stripe publishable key for checkout |
| POST | `/api/payment/create-intent` | Create Stripe PaymentIntent for intake |
| POST | `/api/payment/confirm` | Confirm payment and activate workspace |
| GET | `/api/workspace/{token}` | Customer workspace (tier, credits, jobs) |
| POST | `/api/workspace/{token}/research` | Run tier-gated paralegal pipeline |
| GET | `/api/workspace/{token}/jobs/{id}` | Download research job deliverables |

### Email notifications (optional)

Add to Render environment:

| Variable | Description |
|----------|-------------|
| `RESEND_API_KEY` | API key from [resend.com](https://resend.com) (free tier) |
| `INTAKE_NOTIFY_EMAIL` | Where intake alerts go (default: sales@owl-ai-agency.com) |
| `INTAKE_FROM_EMAIL` | Sender address (must be verified in Resend) |

Intakes are saved locally on the server even without email configured.

### Stripe payments (required for paid tiers)

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Secret key from [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| `STRIPE_PUBLISHABLE_KEY` | Publishable key (exposed via `/api/config/stripe`) |

**Customer flow:** Intake → Payment → Workspace at `legal-research-workspace.html?token=...`

| Tier | Price | Research runs | Documents per run |
|------|-------|---------------|-------------------|
| Starter | $3,000 | 25 | Memo, Brief, TOA |
| Professional | $6,000 | 75 | Full 6-document package |
| Enterprise | $12,000 | Unlimited | Full package + API key |

## Demo Case

**Carpenter v. United States**, 585 U.S. 946 (2018) — Fourth Amendment warrant requirement for historical cell-site location information.

Generated documents:
- Legal Research Memorandum
- Case Brief (IRAC)
- Motion to Suppress CSLI
- Appellate Brief Excerpt
- Table of Authorities
- Certificate of Service
