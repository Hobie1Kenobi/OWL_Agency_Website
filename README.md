# OWL AI Agency Website

Public site for **OWL AI Agency**, a **legal citation verification** product. OWL is a verification layer on research you already have. It is not a general AI agency, not an AI lawyer, not a paralegal replacement, and not a Westlaw competitor.

Message: **Legal AI should not just answer. It should verify.**

## Product

- **[/verify](https://owl-ai-agency.com/verify)** — paste a citation or a paragraph; five checks (existence, citation format, holding support, verification path, human review flag). First check free, no signup.
- **[/legal-research](https://owl-ai-agency.com/legal-research)** — how verification works.
- **[/pricing](https://owl-ai-agency.com/pricing)** — Free, per-document, firm, enterprise/API. Dollar figures live in `assets/data/pricing.json` only.

NAP: Ingleside, TX 78362 · (985) 790-1830 · hobiecunningham@owl-ai-agency.com

OWL is a verification tool, not legal advice, and does not create an attorney-client relationship. Human review of all outputs is required.

## Local development

```bash
python -m http.server
```

Open `http://localhost:8000/`. GitHub Pages serves `file.html` at `/file`; navigation uses extensionless paths.

## Analytics

Microsoft UET tag `97179628` is loaded via `assets/js/ms-uet-tag.js`. Custom events are in `assets/js/analytics.js` (`verify_started`, `verify_completed`, `pricing_view_from_demo`, `contact_form_submit`, `pricing_cta_click`). No GA4 measurement ID is shipped. To add GA4 later, set `window.OWL_GA4_ID` and load `gtag.js` — do not invent an ID.

## Repository notes

- Surviving pages: `/`, `/verify`, `/legal-research`, `/pricing`, `/about`, `/contact`, `/blog/`, and the blog posts.
- Archived URLs are noindex stubs with a refresh to the replacement page. Copies live under `archive/`.
- `legal-research-backend` is the existing Render demo API (Carpenter `/api/demo/run`). `/verify` scaffolds against `POST /api/verify/citations` and falls back to a documented mock until that route exists.
