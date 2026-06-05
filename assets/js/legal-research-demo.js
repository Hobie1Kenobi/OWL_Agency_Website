/**
 * OWL Legal Research Demo — Interactive multi-agent pipeline UI
 */
(function () {
  'use strict';

  const AGENT_META = [
    { id: 'research', icon: 'fa-search', label: 'Research Agent' },
    { id: 'precedent', icon: 'fa-balance-scale', label: 'Precedent Agent' },
    { id: 'analysis', icon: 'fa-brain', label: 'Analysis Agent' },
    { id: 'citation', icon: 'fa-book', label: 'Citation Agent' },
    { id: 'brief_writer', icon: 'fa-file-alt', label: 'Brief Writer' },
    { id: 'filing', icon: 'fa-gavel', label: 'Filing Agent' },
  ];

  const DOC_LABELS = {
    legal_research_memorandum: 'Research Memo',
    case_brief: 'Case Brief',
    motion_to_suppress: 'Motion to Suppress',
    appellate_brief_excerpt: 'Appellate Brief',
    table_of_authorities: 'Table of Authorities',
    certificate_of_service: 'Certificate of Service',
  };

  const PUBLIC_SOURCES = [
    { name: 'Cornell LII', url: 'https://www.law.cornell.edu', types: 'Opinions, Statutes, Rules' },
    { name: 'Oyez', url: 'https://www.oyez.org', types: 'SCOTUS metadata, oral args' },
    { name: 'CourtListener', url: 'https://www.courtlistener.com', types: 'Opinions, dockets' },
    { name: 'Justia', url: 'https://supreme.justia.com', types: 'Case summaries' },
    { name: 'GovInfo', url: 'https://www.govinfo.gov', types: 'U.S. Code, statutes' },
    { name: 'SupremeCourt.gov', url: 'https://www.supremecourt.gov', types: 'Slip opinions' },
  ];

  let demoData = null;

  function getApiBase() {
    return (window.OWL_LEGAL_CONFIG && window.OWL_LEGAL_CONFIG.API_BASE) || 'http://localhost:8000';
  }

  function setStatus(message, type) {
    const el = document.getElementById('demo-status');
    if (!el) return;
    el.textContent = message;
    el.className = 'demo-status ' + (type || 'info');
    el.style.display = 'block';
  }

  function renderAgentPipeline() {
    const container = document.getElementById('agent-pipeline');
    if (!container) return;
    container.innerHTML = AGENT_META.map(function (a) {
      return (
        '<div class="agent-card pending" id="agent-' + a.id + '" data-agent="' + a.id + '">' +
        '<div class="agent-icon"><i class="fas ' + a.icon + '"></i></div>' +
        '<h4>' + a.label + '</h4>' +
        '<p class="agent-status">Waiting...</p></div>'
      );
    }).join('');
  }

  function setAgentState(agentId, state, message) {
    const card = document.getElementById('agent-' + agentId);
    if (!card) return;
    card.className = 'agent-card ' + state;
    const statusEl = card.querySelector('.agent-status');
    if (statusEl) statusEl.textContent = message || state;
  }

  async function animatePipeline(agents) {
    for (let i = 0; i < AGENT_META.length; i++) {
      const meta = AGENT_META[i];
      setAgentState(meta.id, 'running', 'Processing...');
      await delay(600);
      const agent = agents.find(function (a) { return a.agent_id === meta.id; });
      if (agent) {
        setAgentState(meta.id, 'complete', agent.summary.slice(0, 60) + '...');
      } else {
        setAgentState(meta.id, 'complete', 'Done');
      }
    }
  }

  function delay(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  function renderDocuments(documents) {
    const tabsEl = document.getElementById('doc-tabs');
    const contentEl = document.getElementById('doc-content');
    if (!tabsEl || !contentEl) return;

    const keys = Object.keys(documents);
    tabsEl.innerHTML = keys.map(function (key, i) {
      return '<li class="' + (i === 0 ? 'active' : '') + '" data-doc="' + key + '">' +
        (DOC_LABELS[key] || key) + '</li>';
    }).join('');

    contentEl.innerHTML = '<pre class="legal-doc-paper">' + escapeHtml(documents[keys[0]]) + '</pre>';

    tabsEl.querySelectorAll('li').forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabsEl.querySelectorAll('li').forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        const key = tab.getAttribute('data-doc');
        contentEl.innerHTML = '<pre class="legal-doc-paper">' + escapeHtml(documents[key]) + '</pre>';
      });
    });
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function renderMetrics(data) {
    const agents = data.agents || [];
    const totalMs = agents.reduce(function (sum, a) { return sum + (a.duration_ms || 0); }, 0);
    const docs = Object.keys(data.documents || {}).length;

    document.getElementById('metric-agents').textContent = agents.length;
    document.getElementById('metric-docs').textContent = docs;
    document.getElementById('metric-time').textContent = (totalMs / 1000).toFixed(1) + 's';
    document.getElementById('metric-sources').textContent = (data.live_sources || []).filter(function (s) {
      return s.status === 'live';
    }).length;
  }

  function renderLiveSources(liveSources) {
    const el = document.getElementById('live-sources');
    if (!el) return;
    if (!liveSources || !liveSources.length) {
      el.innerHTML = '<p class="text-muted">Live source verification unavailable — using bundled case corpus.</p>';
      return;
    }
    el.innerHTML = liveSources.map(function (s) {
      const live = s.status === 'live';
      const label = s.source || 'unknown';
      const url = s.url || '#';
      return '<span class="source-chip ' + (live ? 'live' : '') + '">' +
        (live ? '<span class="dot"></span>' : '') +
        '<a href="' + url + '" target="_blank" rel="noopener">' + label + '</a>' +
        ' (' + (s.status || 'unknown') + ')</span>';
    }).join('');
  }

  function renderPublicSourcesList() {
    const el = document.getElementById('public-sources-list');
    if (!el) return;
    el.innerHTML = PUBLIC_SOURCES.map(function (s) {
      return '<div class="col-md-6 col-lg-4 mb-3">' +
        '<div class="feature-box h-100">' +
        '<strong><a href="' + s.url + '" target="_blank" rel="noopener">' + s.name + '</a></strong>' +
        '<p class="small text-muted mb-0 mt-1">No API key required · ' + s.types + '</p></div></div>';
    }).join('');
  }

  async function fetchDemo() {
    const apiBase = getApiBase();
    setStatus('Connecting to OWL Legal Research API at ' + apiBase + '...', 'info');

    try {
      const response = await fetch(apiBase + '/api/demo/run', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) throw new Error('API returned ' + response.status);
      return await response.json();
    } catch (err) {
      console.warn('Live API unavailable, loading bundled fallback:', err.message);
      const fallback = await fetch('assets/data/carpenter-demo-fallback.json');
      if (fallback.ok) {
        setStatus('Using bundled demo data (deploy backend to Render for live agent pipeline).', 'info');
        return await fallback.json();
      }
      throw err;
    }
  }

  async function runDemo() {
    const btn = document.getElementById('btn-run-demo');
    const results = document.getElementById('demo-results');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Agents Working...'; }

    renderAgentPipeline();
    AGENT_META.forEach(function (a) { setAgentState(a.id, 'pending', 'Queued...'); });

    try {
      demoData = await fetchDemo();
      setStatus('Pipeline complete — ' + demoData.metadata.case.full_name, 'success');
      await animatePipeline(demoData.agents);
      renderDocuments(demoData.documents);
      renderMetrics(demoData);
      renderLiveSources(demoData.live_sources);
      if (results) results.classList.add('visible');
    } catch (err) {
      setStatus(
        'Could not reach the backend API. Start it locally: cd legal-research-backend && pip install -r requirements.txt && uvicorn main:app --reload — or deploy to Render (see legal-research-backend/README.md).',
        'error'
      );
      AGENT_META.forEach(function (a) { setAgentState(a.id, 'error', 'Offline'); });
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play-circle me-2"></i>Run Demo Analysis';
      }
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    renderAgentPipeline();
    renderPublicSourcesList();

    const btn = document.getElementById('btn-run-demo');
    if (btn) btn.addEventListener('click', runDemo);

    const params = new URLSearchParams(window.location.search);
    if (params.get('autostart') === '1') runDemo();
  });
})();
