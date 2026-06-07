/**
 * Demo lead capture — email after demo completes (inbound nurture)
 */
(function () {
  'use strict';

  function getApiBase() {
    return (window.OWL_LEGAL_CONFIG && window.OWL_LEGAL_CONFIG.API_BASE) || 'http://localhost:8000';
  }

  function showPanel() {
    var panel = document.getElementById('demo-lead-capture');
    if (panel) panel.classList.add('visible');
  }

  function setMessage(text, type) {
    var el = document.getElementById('demo-lead-message');
    if (!el) return;
    el.textContent = text;
    el.className = 'demo-lead-message ' + (type || '');
    el.style.display = text ? 'block' : 'none';
  }

  async function submitLead(event) {
    event.preventDefault();
    var form = document.getElementById('demo-lead-form');
    if (!form) return;

    var email = form.querySelector('[name="email"]').value.trim();
    var fullName = form.querySelector('[name="full_name"]').value.trim();
    var firmName = form.querySelector('[name="firm_name"]').value.trim();
    var btn = form.querySelector('button[type="submit"]');

    if (!email) {
      setMessage('Please enter your email.', 'error');
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Sending...';
    }
    setMessage('', '');

    try {
      var response = await fetch(getApiBase() + '/api/demo-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          email: email,
          full_name: fullName || null,
          firm_name: firmName || null,
        }),
      });
      var data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Submission failed');
      setMessage(data.message || 'Thanks! Check your inbox.', 'success');
      form.reset();
      try { sessionStorage.setItem('owl_demo_lead_submitted', '1'); } catch (e) { /* ignore */ }
    } catch (err) {
      setMessage(err.message || 'Could not submit. Try again or use the intake form.', 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Send Me Next Steps';
      }
    }
  }

  function init() {
    var form = document.getElementById('demo-lead-form');
    if (form) form.addEventListener('submit', submitLead);

    try {
      if (sessionStorage.getItem('owl_demo_lead_submitted') === '1') {
        showPanel();
        setMessage('You are already subscribed to demo follow-up.', 'success');
      }
    } catch (e) { /* ignore */ }

    document.addEventListener('owl-demo-complete', function () {
      try {
        if (sessionStorage.getItem('owl_demo_lead_submitted') === '1') return;
      } catch (e) { /* ignore */ }
      showPanel();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
