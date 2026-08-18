/**
 * /verify UI: paste a citation or load a sample matter, run five checks, show the workspace.
 */
(function () {
  'use strict';

  var form = document.getElementById('verify-form');
  var input = document.getElementById('citation-input');
  var statusEl = document.getElementById('verify-status');
  var resultsEl = document.getElementById('verify-results');
  var convertEl = document.getElementById('verify-convert');
  var submitBtn = document.getElementById('verify-submit');
  var matterMount = document.getElementById('verify-matter-buttons');
  var api = window.OWLVerifyAPI;
  var workspace = window.OWLVerifyWorkspace;

  if (!form || !input || !api) return;

  function setStatus(kind, message) {
    if (!statusEl) return;
    statusEl.hidden = !message;
    statusEl.className = 'verify-status' + (kind ? ' is-' + kind : '');
    statusEl.textContent = message || '';
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function setBusy(busy) {
    if (!submitBtn) return;
    submitBtn.disabled = busy;
    if (busy) submitBtn.setAttribute('aria-busy', 'true');
    else submitBtn.removeAttribute('aria-busy');
    document.querySelectorAll('[data-verify-matter], [data-verify-prefill]').forEach(function (button) {
      button.disabled = busy;
    });
  }

  function showEmptyFailure(message) {
    if (workspace) workspace.render({ citations: [] });
    if (!resultsEl) return;
    resultsEl.hidden = false;
    resultsEl.innerHTML = '<div class="verify-error" role="alert">' + escapeHtml(message) + '</div>';
  }

  function renderPayload(payload) {
    if (resultsEl) {
      resultsEl.innerHTML = '';
      resultsEl.hidden = true;
    }
    if (!payload || !payload.citations || !payload.citations.length) {
      showEmptyFailure('No verification result was returned. The check did not fail silently — try again or contact OWL.');
      return;
    }
    var rendered = workspace ? workspace.render(payload) : false;
    if (!rendered && resultsEl) {
      resultsEl.hidden = false;
      resultsEl.innerHTML = '<div class="verify-error" role="alert">The workspace could not render this result. The check did not fail silently.</div>';
    }
    if (convertEl) convertEl.hidden = false;
  }

  function finishAnalytics(payload) {
    if (!window.OWLAnalytics) return;
    window.OWLAnalytics.track('verify_completed', {
      event_label: payload && payload.matter ? payload.matter.id : 'verify_demo',
      citation_count: payload && payload.citations ? payload.citations.length : 0,
      mode: (payload && payload.mode) || 'mock'
    });
  }

  function startAnalytics(label) {
    if (window.OWLAnalytics) {
      window.OWLAnalytics.track('verify_started', { event_label: label || 'verify_demo' });
    }
  }

  function handlePayload(payload) {
    setStatus('ok', payload.mode === 'live' ? 'Verification complete (live).' : 'Verification complete (demo). Review every check before filing.');
    renderPayload(payload);
    finishAnalytics(payload);
    var workspaceEl = document.getElementById('verify-workspace');
    if (workspaceEl && !workspaceEl.hidden) {
      workspaceEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function handleFailure() {
    setStatus('fail', 'Verification could not run. The failure is shown here rather than ignored. Try again, or email hobiecunningham@owl-ai-agency.com.');
    showEmptyFailure('The verification request failed. No silent pass was recorded.');
  }

  function runVerify() {
    var text = input.value.trim();
    if (!text) {
      setStatus('fail', 'Paste a citation or a paragraph that contains one, then run the check.');
      input.focus();
      return;
    }
    setBusy(true);
    setStatus('info', 'Running five checks…');
    if (convertEl) convertEl.hidden = true;
    startAnalytics('verify_demo');
    api.verify(text).then(handlePayload).catch(handleFailure).then(function () {
      setBusy(false);
    });
  }

  function loadMatter(id) {
    setBusy(true);
    setStatus('info', 'Loading sample matter and running five checks…');
    if (convertEl) convertEl.hidden = true;
    startAnalytics(id || 'sample_matter');
    api.loadMatter(id).then(function (payload) {
      if (payload && payload.excerpt) input.value = payload.excerpt;
      handlePayload(payload);
    }).catch(handleFailure).then(function () {
      setBusy(false);
    });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    runVerify();
  });

  document.querySelectorAll('[data-verify-prefill]').forEach(function (button) {
    button.addEventListener('click', function () {
      var key = button.getAttribute('data-verify-prefill');
      if (key === 'carpenter') {
        loadMatter('carpenter');
        return;
      }
      var value = api.FIXTURES[key] || '';
      input.value = value;
      input.focus();
      runVerify();
    });
  });

  if (matterMount && api.listMatters) {
    api.listMatters().then(function (index) {
      var matters = (index && index.matters) || [];
      if (!matters.length) {
        matterMount.innerHTML = '<p class="small text-muted mb-0">Sample matters could not be listed. Paste a citation instead, or use Try Carpenter v. United States.</p>';
        return;
      }
      matterMount.innerHTML = matters.map(function (matter) {
        return (
          '<button type="button" class="btn btn-outline-primary" data-verify-matter="' + escapeHtml(matter.id) + '">' +
            escapeHtml(matter.short_label || matter.title) +
          '</button>'
        );
      }).join('');
    }).catch(function () {
      matterMount.innerHTML = '<p class="small text-muted mb-0">Sample matters could not load. Paste a citation instead.</p>';
    });
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-verify-matter]');
    if (!button) return;
    loadMatter(button.getAttribute('data-verify-matter'));
  });
})();
