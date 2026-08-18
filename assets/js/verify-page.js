/**
 * /verify UI: paste a citation or a paragraph, run five checks, show failure states.
 */
(function () {
  'use strict';

  var form = document.getElementById('verify-form');
  var input = document.getElementById('citation-input');
  var statusEl = document.getElementById('verify-status');
  var resultsEl = document.getElementById('verify-results');
  var convertEl = document.getElementById('verify-convert');
  var submitBtn = document.getElementById('verify-submit');
  var api = window.OWLVerifyAPI;

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

  function statusLabel(status) {
    if (status === 'pass') return 'Pass';
    if (status === 'fail') return 'Fail';
    return 'Needs review';
  }

  function errorBanner(citation) {
    if (!citation.error) return '';
    var titles = {
      not_found: 'Citation not found',
      ambiguous: 'Ambiguous citation',
      source_unavailable: 'Source unavailable'
    };
    return (
      '<div class="verify-error" role="alert">' +
        '<strong>' + escapeHtml(titles[citation.error] || citation.error) + '.</strong> ' +
        escapeHtml(citation.errorMessage || 'This check did not pass silently.') +
      '</div>'
    );
  }

  function renderCheck(check) {
    var path = '';
    if (check.checked || check.against) {
      path =
        '<p class="verify-path"><span>Checked:</span> ' + escapeHtml(check.checked || '—') +
        '<br/><span>Against:</span> ' + escapeHtml(check.against || '—') + '</p>';
    }
    var link = check.sourceUrl
      ? '<p class="verify-source"><a href="' + escapeHtml(check.sourceUrl) + '" rel="noopener noreferrer">Open public source</a></p>'
      : '';
    return (
      '<li class="verify-check is-' + escapeHtml(check.status) + '">' +
        '<div class="verify-check-head">' +
          '<h3>' + escapeHtml(check.label) + '</h3>' +
          '<span class="verify-pill">' + escapeHtml(statusLabel(check.status)) + '</span>' +
        '</div>' +
        '<p>' + escapeHtml(check.detail) + '</p>' +
        path +
        link +
      '</li>'
    );
  }

  function renderCitation(citation, index) {
    var heading = citation.normalized || citation.raw || ('Citation ' + (index + 1));
    return (
      '<article class="verify-card" aria-labelledby="cite-heading-' + index + '">' +
        '<h2 id="cite-heading-' + index + '">' + escapeHtml(heading) + '</h2>' +
        (citation.normalized && citation.raw && citation.normalized !== citation.raw
          ? '<p class="verify-raw">Pasted as: ' + escapeHtml(citation.raw) + '</p>'
          : '') +
        errorBanner(citation) +
        '<ol class="verify-checks">' + (citation.checks || []).map(renderCheck).join('') + '</ol>' +
      '</article>'
    );
  }

  function renderResults(payload) {
    if (!resultsEl) return;
    if (!payload || !payload.citations || !payload.citations.length) {
      resultsEl.innerHTML = '<div class="verify-error" role="alert">No verification result was returned. The check did not fail silently — try again or contact OWL.</div>';
      resultsEl.hidden = false;
      return;
    }
    var modeNote = payload.mode === 'live'
      ? '<p class="verify-mode">Live verification endpoint.</p>'
      : '<p class="verify-mode">Demo verification on the documented mock contract. TODO: connect live endpoint — <code>/api/verify/citations</code> is not on the Render backend yet.</p>';
    resultsEl.innerHTML = modeNote + payload.citations.map(renderCitation).join('');
    resultsEl.hidden = false;
    if (convertEl) convertEl.hidden = false;
  }

  function runVerify() {
    var text = input.value.trim();
    if (!text) {
      setStatus('fail', 'Paste a citation or a paragraph that contains one, then run the check.');
      input.focus();
      return;
    }
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute('aria-busy', 'true');
    }
    setStatus('info', 'Running five checks…');
    if (convertEl) convertEl.hidden = true;
    if (window.OWLAnalytics) window.OWLAnalytics.track('verify_started', { event_label: 'verify_demo' });
    api.verify(text).then(function (payload) {
      setStatus('ok', payload.mode === 'live' ? 'Verification complete (live).' : 'Verification complete (demo). Review every check before filing.');
      renderResults(payload);
      if (window.OWLAnalytics) {
        window.OWLAnalytics.track('verify_completed', {
          event_label: 'verify_demo',
          citation_count: payload.citations ? payload.citations.length : 0,
          mode: payload.mode || 'mock'
        });
      }
      if (resultsEl) resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }).catch(function () {
      setStatus('fail', 'Verification could not run. The failure is shown here rather than ignored. Try again, or email hobiecunningham@owl-ai-agency.com.');
      if (resultsEl) {
        resultsEl.hidden = false;
        resultsEl.innerHTML = '<div class="verify-error" role="alert">The verification request failed. No silent pass was recorded.</div>';
      }
    }).then(function () {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.removeAttribute('aria-busy');
      }
    });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    runVerify();
  });

  document.querySelectorAll('[data-verify-prefill]').forEach(function (button) {
    button.addEventListener('click', function () {
      var key = button.getAttribute('data-verify-prefill');
      var value = key === 'carpenter' ? api.CARPENTER_PREFILL : (api.FIXTURES[key] || '');
      input.value = value;
      input.focus();
      runVerify();
    });
  });
})();
