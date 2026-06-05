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

1. Push this repo to GitHub
2. Create account at [render.com](https://render.com) (no credit card for free tier)
3. **New → Blueprint** → connect repo → Render reads `render.yaml`
4. Or **New → Web Service** → set root directory to `legal-research-backend`
5. Build: `pip install -r requirements.txt`
6. Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Update `assets/js/legal-research-config.js` with your Render URL

### Keep-Alive (Optional)

Render free tier sleeps after 15 min idle. Use [cron-job.org](https://cron-job.org) (free) to ping `/health` every 14 minutes.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/sources` | List public legal data systems |
| GET | `/api/cases` | Available demo cases |
| POST | `/api/demo/run` | Run full agent pipeline |

## Demo Case

**Carpenter v. United States**, 585 U.S. 946 (2018) — Fourth Amendment warrant requirement for historical cell-site location information.

Generated documents:
- Legal Research Memorandum
- Case Brief (IRAC)
- Motion to Suppress CSLI
- Appellate Brief Excerpt
- Table of Authorities
- Certificate of Service
