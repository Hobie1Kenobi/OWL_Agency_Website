/**
 * /verify UI: select a SAMPLE matter or paste text, run live public-source checks.
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
  var offlineBtn = document.getElementById('verify-offline-preview');
  var api = window.OWLVerifyAPI;
  var workspace = window.OWLVerifyWorkspace;
  var selectedMatterId = null;
  var lastFailure = null;

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
    document.querySelectorAll('[data-verify-matter]').forEach(function (button) {
      button.disabled = busy;
    });
    if (offlineBtn) offlineBtn.disabled = busy;
  }

  function markSelectedMatter(id) {
    selectedMatterId = id;
    document.querySelectorAll('[data-verify-matter]').forEach(function (button) {
      var on = button.getAttribute('data-verify-matter') === id;
      button.classList.toggle('is-selected', on);
      button.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
  }

  function showEmptyFailure(message, offerPreview) {
    if (workspace) workspace.render({ citations: [] });
    if (!resultsEl) return;
    resultsEl.hidden = false;
    var preview = offerPreview
      ? '<p class="mb-0 mt-2"><button type="button" class="btn btn-outline-secondary btn-sm" id="verify-offline-preview-inline">Offline sample preview (not live)</button></p>'
      : '';
    resultsEl.innerHTML =
      '<div class="verify-error" role="alert">' + escapeHtml(message) + preview + '</div>';
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
    var rendered = false;
    try {
      rendered = workspace ? workspace.render(payload) : false;
    } catch (err) {
      rendered = false;
    }
    if (!rendered && resultsEl) {
      resultsEl.hidden = false;
      resultsEl.innerHTML = '<div class="verify-error" role="alert">The workspace could not render this result. The check did not fail silently.</div>';
    }
    if (convertEl) convertEl.hidden = false;
  }

  function finishAnalytics(payload) {
    if (!window.OWLAnalytics) return;
    window.OWLAnalytics.track('verify_completed', {
      event_label: payload && payload.matter ? payload.matter.id : 'verify_live',
      citation_count: payload && payload.citations ? payload.citations.length : 0,
      mode: (payload && payload.mode) || 'live'
    });
  }

  function startAnalytics(label) {
    if (window.OWLAnalytics) {
      window.OWLAnalytics.track('verify_started', { event_label: label || 'verify_live' });
    }
  }

  function handlePayload(payload) {
    var sourceNote = '';
    if (payload.sources_queried && payload.sources_queried.length) {
      var ok = payload.sources_queried.filter(function (item) { return item.status === 'ok'; }).length;
      sourceNote = ' ' + ok + ' of ' + payload.sources_queried.length + ' public source families returned data.';
    }
    if (payload.mode === 'live') {
      setStatus('ok', 'Verification complete (live).' + sourceNote + ' Review every check before filing.');
    } else {
      setStatus('fail', 'Offline sample preview — not a live source check.');
    }
    renderPayload(payload);
    finishAnalytics(payload);
    var workspaceEl = document.getElementById('verify-workspace');
    if (workspaceEl && !workspaceEl.hidden) {
      workspaceEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function handleFailure(err) {
    lastFailure = err || true;
    setStatus('fail', 'Public sources unavailable — retry');
    showEmptyFailure('Public sources unavailable — retry. OWL did not substitute a mock report.', true);
    if (offlineBtn) offlineBtn.hidden = false;
  }

  function runOfflinePreview() {
    var text = input.value.trim();
    if (!text) return;
    setBusy(true);
    setStatus('info', 'Building an offline sample preview. This is not a live source check.');
    startAnalytics((selectedMatterId || 'verify_live') + '_offline_preview');
    api.offlinePreview(text).then(handlePayload).catch(handleFailure).then(function () {
      setBusy(false);
    });
  }

  function runVerify() {
    var text = input.value.trim();
    if (!text) {
      setStatus('fail', 'Paste a citation or load a SAMPLE matter, then run verification.');
      input.focus();
      return;
    }
    setBusy(true);
    lastFailure = null;
    if (offlineBtn) offlineBtn.hidden = true;
    setStatus('info', 'Checking Cornell LII, CourtListener, Oyez, Justia, GovInfo, Supreme Court…');
    if (convertEl) convertEl.hidden = true;
    startAnalytics(selectedMatterId || 'verify_live');
    api.verify(text, selectedMatterId).then(handlePayload).catch(handleFailure).then(function () {
      setBusy(false);
    });
  }

  function loadMatterExcerpt(id) {
    api.getMatter(id).then(function (pack) {
      markSelectedMatter(id);
      if (pack && pack.excerpt) input.value = pack.excerpt;
      input.focus();
      setStatus('info', 'SAMPLE loaded. Run verification to check public sources. This is not legal advice.');
    }).catch(function () {
      setStatus('fail', 'Sample matter could not load. Paste a citation instead.');
    });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    runVerify();
  });

  if (offlineBtn) {
    offlineBtn.addEventListener('click', runOfflinePreview);
  }

  if (matterMount && api.listMatters) {
    api.listMatters().then(function (index) {
      var matters = (index && index.matters) || [];
      if (!matters.length) {
        matterMount.innerHTML = '<p class="small text-muted mb-0">Sample matters could not be listed. Paste a citation instead.</p>';
        return;
      }
      matterMount.innerHTML = matters.map(function (matter) {
        return (
          '<button type="button" class="btn btn-outline-primary" data-verify-matter="' +
            escapeHtml(matter.id) +
            '" aria-pressed="false">' +
            escapeHtml(matter.short_label || matter.title) +
          '</button>'
        );
      }).join('');
    }).catch(function () {
      matterMount.innerHTML = '<p class="small text-muted mb-0">Sample matters could not load. Paste a citation instead.</p>';
    });
  }

  document.addEventListener('click', function (event) {
    var matterBtn = event.target.closest('[data-verify-matter]');
    if (matterBtn) {
      loadMatterExcerpt(matterBtn.getAttribute('data-verify-matter'));
      return;
    }
    if (event.target.closest('#verify-offline-preview-inline')) {
      runOfflinePreview();
    }
  });
})();
