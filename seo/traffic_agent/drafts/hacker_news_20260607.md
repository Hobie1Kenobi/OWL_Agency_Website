Title: Show HN: Six-agent legal research pipeline with live source verification

We built OWL Legal Research — a multi-agent system that queries public legal DBs (Cornell LII, Oyez, CourtListener, GovInfo) and produces memos/briefs with citations, not a single LLM chat.

Public demo on Carpenter v. United States (585 U.S. 946):
https://owl-ai-agency.com/legal-research-demo.html?autostart=1

Backend is FastAPI + agent orchestrator on Render; frontend is static GitHub Pages.

Comparison write-up vs generic ChatGPT legal use:
https://owl-ai-agency.com/compare/owl-vs-chatgpt-legal-research.html

Would love feedback from anyone who's dealt with legal citation hallucinations.
