/**
 * Legal Research Landing Page — Payment & Plan Selection
 */
(function() {
  'use strict';

  var stripe;
  var elements;
  var card;
  var stripePublicKey = null;
  var currentIntakeId = null;

  var stripeForm = document.getElementById('stripe-form');
  var cryptoForm = document.getElementById('crypto-form');
  var stripePaymentBtn = document.getElementById('stripe-payment-btn');
  var cryptoPaymentBtn = document.getElementById('crypto-payment-btn');
  var cardholderName = document.getElementById('cardholder-name');
  var email = document.getElementById('email');
  var submitBtn = document.getElementById('submit-payment');

  var planPrices = {
    starter: 3000,
    professional: 6000,
    enterprise: 12000
  };

  var selectedPlan = 'starter';

  function getApiBase() {
    return (window.OWL_LEGAL_CONFIG && window.OWL_LEGAL_CONFIG.API_BASE) ||
      'https://owl-agency-website.onrender.com';
  }

  async function loadStripeKey() {
    try {
      var res = await fetch(getApiBase() + '/api/config/stripe');
      var data = await res.json();
      if (data.publishable_key) {
        stripePublicKey = data.publishable_key;
        return true;
      }
    } catch (e) { /* fallback below */ }
    stripePublicKey = 'pk_test_TYooMQauvdEDq54NiTphI7jx';
    return false;
  }

  function updatePaymentForm(plan) {
    var planName = plan.charAt(0).toUpperCase() + plan.slice(1);
    var planPrice = planPrices[plan];

    if (stripeForm && cryptoForm) {
      var stripePlanInfo = document.createElement('div');
      stripePlanInfo.className = 'alert alert-info mb-4';
      stripePlanInfo.innerHTML = 'Selected Plan: <strong>' + planName + ' Package</strong> — <strong>$' + planPrice.toLocaleString() + '</strong>';

      var existingStripe = stripeForm.querySelector('.alert');
      if (existingStripe) existingStripe.remove();
      stripeForm.insertBefore(stripePlanInfo, stripeForm.firstChild);

      var cryptoPlanInfo = document.createElement('div');
      cryptoPlanInfo.className = 'alert alert-info mb-4';
      cryptoPlanInfo.innerHTML = 'Selected Plan: <strong>' + planName + ' Package</strong> — <strong>$' + planPrice.toLocaleString() + '</strong>';

      var existingCrypto = cryptoForm.querySelector('.alert');
      if (existingCrypto) existingCrypto.remove();
      cryptoForm.insertBefore(cryptoPlanInfo, cryptoForm.firstChild);
    }

    var stripeButton = document.querySelector('#stripe-form button');
    if (stripeButton) {
      stripeButton.textContent = 'Pay $' + planPrice.toLocaleString() + ' with Card';
    }

    var intakeHint = document.getElementById('payment-intake-hint');
    if (intakeHint) {
      if (currentIntakeId) {
        intakeHint.textContent = 'Paying for intake ' + currentIntakeId;
        intakeHint.style.display = 'block';
      } else {
        intakeHint.textContent = 'Complete the intake form above first to link payment to your project.';
        intakeHint.style.display = 'block';
      }
    }
  }

  function showPaymentSuccess(accessToken) {
    stripeForm.innerHTML =
      '<div class="text-center">' +
      '<i class="fas fa-check-circle" style="font-size: 60px; color: #47b2e4; margin-bottom: 20px;"></i>' +
      '<h3>Payment Successful!</h3>' +
      '<p>Your ' + selectedPlan + ' workspace is now active.</p>' +
      '<a href="legal-research-workspace.html?token=' + accessToken + '" class="btn-get-started btn-lg mt-3">' +
      '<i class="fas fa-arrow-right me-2"></i>Open Your Workspace</a>' +
      '<p class="text-muted small mt-3">Bookmark this page — your private research portal.</p></div>';
  }

  async function processPayment(event) {
    event.preventDefault();

    if (!currentIntakeId) {
      document.getElementById('card-errors').textContent =
        'Please complete the intake form first so we can link payment to your project.';
      document.getElementById('intake').scrollIntoView({ behavior: 'smooth' });
      return;
    }

    if (selectedPlan === 'consultation') {
      document.getElementById('card-errors').textContent = 'Free consultation does not require payment.';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';

    try {
      var intentRes = await fetch(getApiBase() + '/api/payment/create-intent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intake_id: currentIntakeId, plan: selectedPlan })
      });
      var intentData = await intentRes.json();

      if (!intentRes.ok) {
        throw new Error(intentData.detail?.detail || intentData.detail?.error || 'Could not start payment');
      }

      if (intentData.already_paid && intentData.access_token) {
        showPaymentSuccess(intentData.access_token);
        return;
      }

      var result = await stripe.confirmCardPayment(intentData.client_secret, {
        payment_method: {
          card: card,
          billing_details: {
            name: cardholderName.value,
            email: email.value
          }
        }
      });

      if (result.error) {
        throw new Error(result.error.message);
      }

      var confirmRes = await fetch(getApiBase() + '/api/payment/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intake_id: currentIntakeId,
          payment_intent_id: result.paymentIntent.id
        })
      });
      var confirmData = await confirmRes.json();

      if (!confirmRes.ok) {
        throw new Error(confirmData.detail?.detail || confirmData.detail?.error || 'Payment confirmation failed');
      }

      showPaymentSuccess(confirmData.access_token);
    } catch (err) {
      document.getElementById('card-errors').textContent = err.message;
      submitBtn.disabled = false;
      submitBtn.textContent = 'Pay Now';
    }
  }

  document.addEventListener('DOMContentLoaded', async function() {
    var urlParams = new URLSearchParams(window.location.search);
    var planParam = urlParams.get('plan');
    if (planParam && planPrices[planParam]) selectedPlan = planParam;

    await loadStripeKey();
    stripe = Stripe(stripePublicKey);
    elements = stripe.elements();

    card = elements.create('card', {
      style: {
        base: {
          color: '#32325d',
          fontFamily: '"Open Sans", sans-serif',
          fontSmoothing: 'antialiased',
          fontSize: '16px',
          '::placeholder': { color: '#aab7c4' }
        },
        invalid: { color: '#fa755a', iconColor: '#fa755a' }
      }
    });
    card.mount('#card-element');

    card.on('change', function(event) {
      document.getElementById('card-errors').textContent = event.error ? event.error.message : '';
    });

    var paymentForm = document.getElementById('payment-form');
    if (paymentForm) paymentForm.addEventListener('submit', processPayment);

    if (stripePaymentBtn) {
      stripePaymentBtn.addEventListener('click', function() {
        stripeForm.style.display = 'block';
        cryptoForm.style.display = 'none';
        stripeForm.scrollIntoView({ behavior: 'smooth' });
      });
    }

    if (cryptoPaymentBtn) {
      cryptoPaymentBtn.addEventListener('click', function() {
        cryptoForm.style.display = 'block';
        stripeForm.style.display = 'none';
        cryptoForm.scrollIntoView({ behavior: 'smooth' });
      });
    }

    document.querySelectorAll('[data-plan]').forEach(function(button) {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        selectedPlan = this.getAttribute('data-plan');
        updatePaymentForm(selectedPlan);
        if (window.OWLIntake && window.OWLIntake.setPlan) {
          window.OWLIntake.setPlan(selectedPlan);
        }
        var target = document.getElementById('intake') || document.getElementById('payment');
        if (target) target.scrollIntoView({ behavior: 'smooth' });
      });
    });

    updatePaymentForm(selectedPlan);
  });

  window.OWLLegalResearch = {
    setPlan: function(plan) {
      if (planPrices[plan]) {
        selectedPlan = plan;
        updatePaymentForm(plan);
      }
    },
    setIntake: function(intakeId, plan, contactEmail, contactName) {
      currentIntakeId = intakeId;
      if (plan && planPrices[plan]) selectedPlan = plan;
      if (contactEmail && email) email.value = contactEmail;
      if (contactName && cardholderName) cardholderName.value = contactName;
      updatePaymentForm(selectedPlan);
    }
  };
})();
