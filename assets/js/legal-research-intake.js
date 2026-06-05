/**
 * Legal Research Intake Form — submits to OWL Legal Research API
 */
(function () {
  'use strict';

  var PLAN_LABELS = {
    starter: 'Starter Package — $3,000',
    professional: 'Professional Package — $6,000',
    enterprise: 'Enterprise Package — $12,000',
    consultation: 'Free Consultation'
  };

  function getApiBase() {
    return (window.OWL_LEGAL_CONFIG && window.OWL_LEGAL_CONFIG.API_BASE) ||
      'https://owl-agency-website.onrender.com';
  }

  function showError(fieldId, message) {
    var input = document.getElementById(fieldId);
    var err = document.getElementById(fieldId + '-error');
    if (input) input.classList.add('is-invalid');
    if (err) err.textContent = message;
  }

  function clearErrors() {
    document.querySelectorAll('#legal-intake-form .is-invalid').forEach(function (el) {
      el.classList.remove('is-invalid');
    });
    document.querySelectorAll('#legal-intake-form .intake-error').forEach(function (el) {
      el.textContent = '';
    });
  }

  function validateForm(data) {
    var valid = true;
    clearErrors();

    if (!data.full_name || data.full_name.length < 2) {
      showError('intake-name', 'Please enter your full name.');
      valid = false;
    }
    if (!data.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      showError('intake-email', 'Please enter a valid email address.');
      valid = false;
    }
    if (!data.firm_name || data.firm_name.length < 2) {
      showError('intake-firm', 'Please enter your firm or organization name.');
      valid = false;
    }
    if (!data.jurisdiction || data.jurisdiction.length < 2) {
      showError('intake-jurisdiction', 'Please specify jurisdiction.');
      valid = false;
    }
    if (!data.practice_area || data.practice_area.length < 2) {
      showError('intake-practice', 'Please specify practice area.');
      valid = false;
    }
    if (!data.research_question || data.research_question.length < 20) {
      showError('intake-question', 'Please describe your research needs (at least 20 characters).');
      valid = false;
    }
    return valid;
  }

  function collectFormData() {
    return {
      full_name: document.getElementById('intake-name').value.trim(),
      email: document.getElementById('intake-email').value.trim(),
      phone: document.getElementById('intake-phone').value.trim() || null,
      firm_name: document.getElementById('intake-firm').value.trim(),
      firm_size: document.getElementById('intake-firm-size').value || null,
      plan: document.getElementById('intake-plan').value,
      jurisdiction: document.getElementById('intake-jurisdiction').value.trim(),
      practice_area: document.getElementById('intake-practice').value.trim(),
      case_count: parseInt(document.getElementById('intake-cases').value, 10) || null,
      research_question: document.getElementById('intake-question').value.trim(),
      urgency: document.getElementById('intake-urgency').value,
      has_documents: document.getElementById('intake-has-docs').checked,
      preferred_contact: document.getElementById('intake-contact-pref').value,
      referral_source: document.getElementById('intake-referral').value.trim() || null,
      demo_viewed: window.location.pathname.indexOf('legal-research-demo') !== -1 ||
        document.referrer.indexOf('legal-research-demo') !== -1
    };
  }

  function setPlan(plan) {
    var select = document.getElementById('intake-plan');
    var badge = document.getElementById('intake-plan-badge');
    if (select && PLAN_LABELS[plan]) {
      select.value = plan;
    }
    if (badge) {
      badge.textContent = 'Selected: ' + (PLAN_LABELS[plan] || plan);
      badge.style.display = 'inline-block';
    }
  }

  function showSuccess(result) {
    document.getElementById('intake-form-wrap').classList.add('hidden');
    var success = document.getElementById('intake-success');
    success.classList.add('visible');
    document.getElementById('intake-ref-id').textContent = result.intake_id;
    document.getElementById('intake-success-message').textContent = result.message;

    var stepsList = document.getElementById('intake-next-steps');
    stepsList.innerHTML = '';
    (result.next_steps || []).forEach(function (step) {
      var li = document.createElement('li');
      li.textContent = step;
      stepsList.appendChild(li);
    });

    var paymentLink = document.getElementById('intake-go-payment');
    if (paymentLink && result.intake_id) {
      paymentLink.href = '#payment';
      paymentLink.style.display = 'inline-block';
      paymentLink.addEventListener('click', function () {
        if (window.OWLLegalResearch && window.OWLLegalResearch.setPlan) {
          var plan = document.getElementById('intake-plan').value;
          if (plan !== 'consultation') window.OWLLegalResearch.setPlan(plan);
        }
      });
    }

    success.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  async function submitIntake(event) {
    event.preventDefault();
    var data = collectFormData();
    if (!validateForm(data)) return;

    var btn = document.getElementById('intake-submit');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';

    try {
      var response = await fetch(getApiBase() + '/api/intake', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(data)
      });

      var result = await response.json();
      if (!response.ok) {
        var detail = result.detail;
        var msg = Array.isArray(detail)
          ? detail.map(function (d) { return d.msg; }).join(', ')
          : (detail || 'Submission failed. Please try again.');
        throw new Error(msg);
      }
      showSuccess(result);
    } catch (err) {
      alert('Could not submit intake: ' + err.message + '\n\nEmail us directly at sales@owl-ai-agency.com');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Submit Research Request';
    }
  }

  function initFromUrl() {
    var params = new URLSearchParams(window.location.search);
    var plan = params.get('plan');
    if (plan && PLAN_LABELS[plan]) setPlan(plan);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('legal-intake-form');
    if (form) form.addEventListener('submit', submitIntake);
    initFromUrl();

    document.querySelectorAll('[data-plan][href="#intake"], [data-plan][href="#payment"]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var plan = btn.getAttribute('data-plan');
        if (plan) setPlan(plan);
      });
    });
  });

  window.OWLIntake = { setPlan: setPlan };
})();
