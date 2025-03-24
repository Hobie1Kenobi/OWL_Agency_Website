/**
 * Legal Research Landing Page JavaScript
 * Version: 1.0.0
 */
(function() {
  'use strict';
  
  // Initialize Stripe
  let stripe;
  let elements;
  let card;
  
  // API key (replace with your actual key in production)
  const stripePublicKey = 'pk_test_TYooMQauvdEDq54NiTphI7jx';
  
  // DOM elements
  const stripeForm = document.getElementById('stripe-form');
  const cryptoForm = document.getElementById('crypto-form');
  const paymentTabs = document.querySelectorAll('.payment-tab');
  const paymentForms = document.querySelectorAll('.payment-form');
  const stripePaymentBtn = document.getElementById('stripe-payment-btn');
  const cryptoPaymentBtn = document.getElementById('crypto-payment-btn');
  const cardholderName = document.getElementById('cardholder-name');
  const email = document.getElementById('email');
  const submitBtn = document.getElementById('submit-payment');
  
  // Plan prices
  const planPrices = {
    'starter': 3000,
    'professional': 6000,
    'enterprise': 12000
  };
  
  // Selected plan
  let selectedPlan = 'starter';
  
  // Initialize on DOM loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Check for plan in URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const planParam = urlParams.get('plan');
    
    if (planParam && planPrices[planParam]) {
      selectedPlan = planParam;
    }
    
    // Initialize Stripe
    stripe = Stripe(stripePublicKey);
    elements = stripe.elements();
    
    // Create card element
    card = elements.create('card', {
      style: {
        base: {
          color: '#32325d',
          fontFamily: '"Open Sans", sans-serif',
          fontSmoothing: 'antialiased',
          fontSize: '16px',
          '::placeholder': {
            color: '#aab7c4'
          }
        },
        invalid: {
          color: '#fa755a',
          iconColor: '#fa755a'
        }
      }
    });
    
    // Mount card element
    card.mount('#card-element');
    
    // Handle real-time validation errors
    card.on('change', function(event) {
      const displayError = document.getElementById('card-errors');
      if (event.error) {
        displayError.textContent = event.error.message;
      } else {
        displayError.textContent = '';
      }
    });
    
    // Handle form submission
    const paymentForm = document.getElementById('payment-form');
    paymentForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // Disable the submit button to prevent repeated clicks
      submitBtn.disabled = true;
      submitBtn.textContent = 'Processing...';
      
      // Create payment method
      stripe.createPaymentMethod({
        type: 'card',
        card: card,
        billing_details: {
          name: cardholderName.value,
          email: email.value
        }
      }).then(function(result) {
        if (result.error) {
          // Show error to customer
          const errorElement = document.getElementById('card-errors');
          errorElement.textContent = result.error.message;
          submitBtn.disabled = false;
          submitBtn.textContent = 'Pay Now';
        } else {
          // In a real implementation, you would send the payment method ID to your server
          // and create a payment intent. For demo purposes, we'll simulate success.
          simulatePaymentSuccess(result.paymentMethod.id);
        }
      });
    });
    
    // Simulate payment success (in production, this would be handled by your server)
    function simulatePaymentSuccess(paymentMethodId) {
      // Simulate API call delay
      setTimeout(function() {
        // Show success message
        stripeForm.innerHTML = `
          <div class="text-center">
            <i class="fas fa-check-circle" style="font-size: 60px; color: #47b2e4; margin-bottom: 20px;"></i>
            <h3>Payment Successful!</h3>
            <p>Thank you for your purchase. Your payment of $${planPrices[selectedPlan]} has been processed successfully.</p>
            <p>Payment Method ID: ${paymentMethodId}</p>
            <p>You will receive a confirmation email shortly with details about your legal research service.</p>
            <div class="mt-4">
              <a href="index.html" class="btn-get-started">Return to Home</a>
            </div>
          </div>
        `;
      }, 2000);
    }
    
    // Payment option buttons
    stripePaymentBtn.addEventListener('click', function() {
      stripeForm.style.display = 'block';
      cryptoForm.style.display = 'none';
      
      // Scroll to the form
      stripeForm.scrollIntoView({ behavior: 'smooth' });
    });
    
    cryptoPaymentBtn.addEventListener('click', function() {
      cryptoForm.style.display = 'block';
      stripeForm.style.display = 'none';
      
      // Scroll to the form
      cryptoForm.scrollIntoView({ behavior: 'smooth' });
    });
    
    // Handle plan selection
    const planButtons = document.querySelectorAll('[data-plan]');
    planButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Get selected plan
        const selectedPlanName = this.getAttribute('data-plan');
        selectedPlan = selectedPlanName;
        
        // Update payment form
        updatePaymentForm(selectedPlanName);
        
        // Scroll to payment section
        document.getElementById('payment').scrollIntoView({ behavior: 'smooth' });
      });
    });
    
    // Update payment form based on selected plan
    function updatePaymentForm(plan) {
      const planName = plan.charAt(0).toUpperCase() + plan.slice(1);
      const planPrice = planPrices[plan];
      
      // Update payment forms
      if (stripeForm && cryptoForm) {
        // Update Stripe form
        const stripePlanInfo = document.createElement('div');
        stripePlanInfo.className = 'alert alert-info mb-4';
        stripePlanInfo.innerHTML = `Selected Plan: <strong>${planName} Package</strong> - <strong>$${planPrice.toLocaleString()}</strong>`;
        
        // Remove existing plan info if present
        const existingStripePlanInfo = stripeForm.querySelector('.alert');
        if (existingStripePlanInfo) {
          existingStripePlanInfo.remove();
        }
        
        stripeForm.insertBefore(stripePlanInfo, stripeForm.firstChild);
        
        // Update Crypto form
        const cryptoPlanInfo = document.createElement('div');
        cryptoPlanInfo.className = 'alert alert-info mb-4';
        cryptoPlanInfo.innerHTML = `Selected Plan: <strong>${planName} Package</strong> - <strong>$${planPrice.toLocaleString()}</strong>`;
        
        // Remove existing plan info if present
        const existingCryptoPlanInfo = cryptoForm.querySelector('.alert');
        if (existingCryptoPlanInfo) {
          existingCryptoPlanInfo.remove();
        }
        
        cryptoForm.insertBefore(cryptoPlanInfo, cryptoForm.firstChild);
      }
      
      // Update Stripe payment button
      const stripeButton = document.querySelector('#stripe-form button');
      if (stripeButton) {
        stripeButton.textContent = `Pay $${planPrice.toLocaleString()} with Card`;
      }
    }
    
    // Initialize with default plan
    updatePaymentForm(selectedPlan);
  });
  
})();
