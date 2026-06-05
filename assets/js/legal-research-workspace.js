/**
 * OWL Legal Research — Customer Workspace
 */
(function () {
  'use strict';

  var EXAMPLE_QUESTIONS = [
    {
      label: 'Fourth Amendment — Cell-Site Location (Carpenter-type)',
      case: 'State v. Martinez',
      jurisdiction: 'Sixth Circuit / U.S. District Court',
      practice: 'Criminal Defense / Fourth Amendment',
      facts: 'Prosecution obtained 90 days of historical CSLI via court order under 18 U.S.C. § 2703(d) without a warrant. Defendant seeks suppression.',
      question: 'Whether the government\'s warrantless acquisition of 90 days of historical cell-site location information violates the Fourth Amendment under Carpenter v. United States, 585 U.S. 946 (2018).',
      relief: 'Motion to suppress CSLI evidence'
    },
    {
      label: 'Motion to Suppress — GPS Tracking',
      case: 'United States v. Chen',
      jurisdiction: 'Ninth Circuit',
      practice: 'Federal Criminal Defense',
      facts: 'FBI attached GPS device to defendant\'s vehicle for 45 days without warrant. Location data used to establish presence at crime scenes.',
      question: 'Whether prolonged warrantless GPS surveillance constitutes a Fourth Amendment search requiring suppression under United States v. Jones, 565 U.S. 400 (2012).',
      relief: 'Motion to suppress GPS-derived evidence'
    },
    {
      label: 'Appellate — Sentencing Guidelines',
      case: 'People v. Johnson',
      jurisdiction: 'Michigan Court of Appeals',
      practice: 'Criminal Appeals',
      facts: 'Defendant sentenced above guidelines range based on judicial fact-finding not admitted by jury or proven beyond reasonable doubt.',
      question: 'Whether the sentencing court\'s upward departure based on judicial fact-finding violated the defendant\'s Sixth Amendment jury trial right under Apprendi v. New Jersey.',
      relief: 'Remand for resentencing'
    }
  ];

  var workspace = null;
  var currentJob = null;
  var accessToken = null;

  function getApiBase() {
    return (window.OWL_LEGAL_CONFIG && window.OWL_LEGAL_CONFIG.API_BASE) ||
      'https://owl-agency-website.onrender.com';
  }

  function getToken() {
    return new URLSearchParams(window.location.search).get('token');
  }

  function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function showStatus(msg, type) {
    var el = document.getElementById('rq-status');
    el.className = 'alert alert-' + (type || 'info') + ' mt-3';
    el.textContent = msg;
    el.style.display = 'block';
  }

  function renderStats(data) {
    var tier = data.tier || {};
    document.getElementById('ws-stats').innerHTML =
      '<div class="ws-stat"><div class="num">' + data.cases_remaining + '</div><div class="lbl">Credits Remaining</div></div>' +
      '<div class="ws-stat"><div class="num">' + data.cases_used + '</div><div class="lbl">Runs Completed</div></div>' +
      '<div class="ws-stat"><div class="num">' + (tier.documents || []).length + '</div><div class="lbl">Doc Types / Run</div></div>' +
      '<div class="ws-stat"><div class="num">' + (tier.turnaround_hours || '—') + 'h</div><div class="lbl">Turnaround SLA</div></div>';
  }

  function renderOnboarding(steps) {
    document.getElementById('ws-onboarding').innerHTML = (steps || []).map(function (s) {
      return '<div class="onboard-step ' + (s.complete ? 'complete' : '') + '">' +
        '<div class="step-num">Step ' + s.step_number + (s.complete ? ' ✓' : '') + '</div>' +
        '<h5 class="mt-2">' + escapeHtml(s.title) + '</h5>' +
        '<p class="small text-muted mb-0">' + escapeHtml(s.description) + '</p></div>';
    }).join('');
  }

  function renderTierFeatures(tier) {
    var html = '<h5><i class="fas fa-box-open me-2"></i>Your ' + escapeHtml(tier.name) + ' Includes</h5><ul>';
    (tier.features || []).forEach(function (f) {
      html += '<li><i class="fas fa-check text-primary me-2"></i>' + escapeHtml(f) + '</li>';
    });
    html += '</ul>';
    document.getElementById('ws-tier-features').innerHTML = html;
  }

  function renderExamples() {
    document.getElementById('example-questions').innerHTML = EXAMPLE_QUESTIONS.map(function (ex, i) {
      return '<div class="example-q" data-idx="' + i + '"><strong>' + escapeHtml(ex.label) + '</strong><br>' +
        '<span class="text-muted small">' + escapeHtml(ex.question.substring(0, 100)) + '...</span></div>';
    }).join('');

    document.querySelectorAll('.example-q').forEach(function (el) {
      el.addEventListener('click', function () {
        var ex = EXAMPLE_QUESTIONS[parseInt(el.getAttribute('data-idx'), 10)];
        document.getElementById('rq-case').value = ex.case;
        document.getElementById('rq-jurisdiction').value = ex.jurisdiction;
        document.getElementById('rq-practice').value = ex.practice;
        document.getElementById('rq-facts').value = ex.facts;
        document.getElementById('rq-question').value = ex.question;
        document.getElementById('rq-relief').value = ex.relief;
      });
    });
  }

  function prefillFromWorkspace(data) {
    if (data.jurisdiction) document.getElementById('rq-jurisdiction').value = data.jurisdiction;
    if (data.practice_area) document.getElementById('rq-practice').value = data.practice_area;
    if (data.initial_research_question) document.getElementById('rq-question').value = data.initial_research_question;
  }

  function renderJobList(jobs) {
    var section = document.getElementById('ws-jobs-section');
    var list = document.getElementById('ws-job-list');
    if (!jobs || !jobs.length) {
      section.style.display = 'none';
      return;
    }
    section.style.display = 'block';
    list.innerHTML = jobs.map(function (j) {
      return '<div class="job-card" data-job="' + j.job_id + '">' +
        '<strong>' + escapeHtml(j.case_name) + '</strong>' +
        '<p class="small text-muted mb-1">' + escapeHtml(j.created_at.substring(0, 10)) + '</p>' +
        '<span class="badge bg-success">' + j.document_count + ' docs</span></div>';
    }).join('');

    list.querySelectorAll('.job-card').forEach(function (card) {
      card.addEventListener('click', function () {
        loadJobDetail(card.getAttribute('data-job'));
        list.querySelectorAll('.job-card').forEach(function (c) { c.classList.remove('active'); });
        card.classList.add('active');
      });
    });
  }

  async function loadJobDetail(jobId) {
    var detail = document.getElementById('ws-job-detail');
    detail.innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Loading...</p>';
    try {
      var res = await fetch(getApiBase() + '/api/workspace/' + accessToken + '/jobs/' + jobId);
      if (!res.ok) throw new Error('Job not found');
      currentJob = await res.json();
      renderJobDetail(currentJob);
    } catch (err) {
      detail.innerHTML = '<p class="text-danger">' + escapeHtml(err.message) + '</p>';
    }
  }

  function renderJobDetail(job) {
    var labels = job.document_labels || {};
    var keys = Object.keys(job.documents || {});
    var tabs = keys.map(function (k, i) {
      return '<li class="' + (i === 0 ? 'active' : '') + '" data-doc="' + k + '">' +
        escapeHtml(labels[k] || k) + '</li>';
    }).join('');

    var detail = document.getElementById('ws-job-detail');
    detail.innerHTML =
      '<h4>' + escapeHtml(job.case_name) + '</h4>' +
      '<p class="text-muted small">' + escapeHtml(job.research_question) + '</p>' +
      '<div class="mb-3">' +
      '<button class="btn btn-sm btn-outline-primary me-2" id="btn-dl-txt"><i class="fas fa-download me-1"></i>Download All (.txt)</button>' +
      '<button class="btn btn-sm btn-outline-success" id="btn-dl-csv"><i class="fas fa-file-csv me-1"></i>Download CSV Report</button>' +
      '</div>' +
      '<ul class="doc-tabs-ws">' + tabs + '</ul>' +
      '<div class="doc-viewer-ws"><pre class="legal-doc-paper">' + escapeHtml(job.documents[keys[0]] || '') + '</pre></div>';

    detail.querySelectorAll('.doc-tabs-ws li').forEach(function (tab) {
      tab.addEventListener('click', function () {
        detail.querySelectorAll('.doc-tabs-ws li').forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        var key = tab.getAttribute('data-doc');
        detail.querySelector('pre').textContent = job.documents[key];
      });
    });

    document.getElementById('btn-dl-txt').addEventListener('click', function () {
      var text = keys.map(function (k) {
        return '=== ' + (labels[k] || k) + ' ===\n\n' + job.documents[k];
      }).join('\n\n');
      downloadFile(text, job.case_name.replace(/\s+/g, '_') + '_deliverables.txt', 'text/plain');
    });

    document.getElementById('btn-dl-csv').addEventListener('click', function () {
      downloadFile(job.csv_export || '', job.case_name.replace(/\s+/g, '_') + '_report.csv', 'text/csv');
    });
  }

  function downloadFile(content, filename, mime) {
    var blob = new Blob([content], { type: mime });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  async function loadWorkspace() {
    accessToken = getToken();
    if (!accessToken) {
      document.getElementById('ws-locked').style.display = 'block';
      return;
    }

    try {
      var res = await fetch(getApiBase() + '/api/workspace/' + accessToken);
      if (!res.ok) throw new Error('Invalid or expired workspace token');
      workspace = await res.json();

      document.getElementById('ws-app').style.display = 'block';
      document.getElementById('ws-tier-badge').textContent = workspace.tier.name + ' — ' + workspace.tier.price_display;
      document.getElementById('ws-welcome').textContent = 'Welcome, ' + workspace.contact_name.split(' ')[0];
      document.getElementById('ws-firm-line').textContent = workspace.firm_name + ' · Ref ' + workspace.intake_id;

      renderStats(workspace);
      renderOnboarding(workspace.onboarding_steps);
      renderTierFeatures(workspace.tier);
      renderExamples();
      prefillFromWorkspace(workspace);
      renderJobList(workspace.research_jobs);

      if (workspace.api_key) {
        document.getElementById('ws-api-section').style.display = 'block';
        document.getElementById('ws-api-key').textContent = workspace.api_key;
      }
    } catch (err) {
      document.getElementById('ws-locked').style.display = 'block';
      document.querySelector('#ws-locked p').textContent = err.message;
    }
  }

  async function submitResearch(event) {
    event.preventDefault();
    var payload = {
      case_name: document.getElementById('rq-case').value.trim(),
      jurisdiction: document.getElementById('rq-jurisdiction').value.trim(),
      practice_area: document.getElementById('rq-practice').value.trim(),
      research_question: document.getElementById('rq-question').value.trim(),
      key_facts: document.getElementById('rq-facts').value.trim() || null,
      relief_sought: document.getElementById('rq-relief').value.trim() || null,
      desired_deliverables: []
    };

    if (payload.research_question.length < 20) {
      showStatus('Research question must be at least 20 characters.', 'warning');
      return;
    }

    var btn = document.getElementById('rq-submit');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Agents Working...';
    showStatus('Deploying six-agent paralegal pipeline — this may take up to 60 seconds...', 'info');

    try {
      var res = await fetch(getApiBase() + '/api/workspace/' + accessToken + '/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload)
      });
      var result = await res.json();
      if (!res.ok) {
        var detail = result.detail || result;
        throw new Error(detail.detail || detail.error || 'Research failed');
      }

      showStatus('Pipeline complete! ' + result.cases_remaining + ' credits remaining.', 'success');
      workspace.cases_used = result.cases_used;
      workspace.cases_remaining = result.cases_remaining;
      workspace.research_jobs = [{
        job_id: result.job.job_id,
        case_name: result.job.case_name,
        status: 'complete',
        created_at: result.job.created_at,
        document_count: Object.keys(result.job.documents).length
      }].concat(workspace.research_jobs || []);

      renderStats({
        cases_used: result.cases_used,
        cases_remaining: result.cases_remaining,
        tier: workspace.tier
      });
      renderJobList(workspace.research_jobs);
      loadJobDetail(result.job.job_id);
      document.getElementById('ws-jobs-section').scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
      showStatus(err.message, 'danger');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-play-circle me-2"></i>Run Paralegal Pipeline';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    loadWorkspace();
    var form = document.getElementById('research-query-form');
    if (form) form.addEventListener('submit', submitResearch);
  });
})();
