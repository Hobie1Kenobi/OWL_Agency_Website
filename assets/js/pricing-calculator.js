/**
 * Pricing Calculator for OWL AI Agency
 * Version: 1.0.0
 */
(function() {
  "use strict";
  
  // Service base prices (corresponds to the pricing in agent_config.yaml)
  const servicePrices = {
    'content-creation': {
      base: 0.10, // per word
      unit: 'per word',
      complexityFactors: {
        low: 1.0,
        medium: 1.5,
        high: 2.0
      }
    },
    'technical-documentation': {
      base: 0.20, // per word
      unit: 'per word',
      complexityFactors: {
        low: 1.0,
        medium: 1.25,
        high: 1.5
      }
    },
    'data-analysis': {
      base: 150.00, // flat rate
      unit: 'flat rate',
      complexityFactors: {
        low: 1.0,
        medium: 1.5,
        high: 2.5
      }
    },
    'coding-services': {
      base: 200.00, // flat rate
      unit: 'flat rate',
      complexityFactors: {
        low: 1.0,
        medium: 1.75,
        high: 3.0
      }
    }
  };
  
  // Subscription discounts
  const subscriptionDiscounts = {
    'none': 0,
    'basic': 0.05,    // 5% discount
    'professional': 0.15, // 15% discount
    'enterprise': 0.25  // 25% discount
  };
  
  // Payment method discounts
  const paymentDiscounts = {
    'stripe': 0,
    'crypto': 0.05  // 5% discount for crypto payments
  };
  
  document.addEventListener('DOMContentLoaded', function() {
    const calculateButton = document.getElementById('calculate-price');
    const serviceType = document.getElementById('service-type');
    const complexity = document.getElementById('complexity');
    const quantity = document.getElementById('quantity');
    const subscription = document.getElementById('subscription');
    const paymentMethod = document.getElementById('payment-method');
    const priceResult = document.getElementById('price-result');
    const priceBreakdown = document.getElementById('price-breakdown');
    
    // Handle URL parameters
    function getUrlParameter(name) {
      name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
      const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
      const results = regex.exec(location.search);
      return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }
    
    // Set form values from URL parameters if they exist
    function setFormFromUrlParams() {
      const serviceParam = getUrlParameter('service');
      const complexityParam = getUrlParameter('complexity');
      const quantityParam = getUrlParameter('quantity');
      const subscriptionParam = getUrlParameter('subscription');
      
      if (serviceParam) {
        serviceType.value = serviceParam;
      }
      
      if (complexityParam) {
        complexity.value = complexityParam;
      }
      
      if (quantityParam) {
        quantity.value = quantityParam;
      }
      
      if (subscriptionParam) {
        subscription.value = subscriptionParam;
      }
      
      // Auto-calculate price if parameters are provided
      if (serviceParam || complexityParam || quantityParam || subscriptionParam) {
        calculatePrice();
      }
    }
    
    // Calculate price based on inputs
    function calculatePrice() {
      let basePrice = 0;
      let complexityMultiplier = 1;
      let subscriptionDiscount = 0;
      let paymentDiscount = 0;
      
      // Set base price based on service type
      switch (serviceType.value) {
        case 'content-creation':
          basePrice = 0.10; // per word
          break;
        case 'technical-documentation':
          basePrice = 0.20; // per word
          break;
        case 'data-analysis':
          basePrice = 150.00; // per analysis
          break;
        case 'coding-services':
          basePrice = 200.00; // per service
          break;
        case 'research':
          basePrice = 175.00; // per research task
          break;
      }
      
      // Set complexity multiplier
      switch (complexity.value) {
        case 'low':
          complexityMultiplier = 0.8;
          break;
        case 'medium':
          complexityMultiplier = 1.0;
          break;
        case 'high':
          complexityMultiplier = 1.5;
          break;
      }
      
      // Set subscription discount
      switch (subscription.value) {
        case 'none':
          subscriptionDiscount = 0;
          break;
        case 'basic':
          subscriptionDiscount = 0.05; // 5% off
          break;
        case 'professional':
          subscriptionDiscount = 0.15; // 15% off
          break;
        case 'enterprise':
          subscriptionDiscount = 0.25; // 25% off
          break;
      }
      
      // Set payment method discount
      paymentDiscount = paymentMethod.value === 'crypto' ? 0.05 : 0; // 5% off for crypto
      
      // Calculate total price
      let quantityValue = parseInt(quantity.value);
      let totalBeforeDiscounts = 0;
      
      if (serviceType.value === 'content-creation' || serviceType.value === 'technical-documentation') {
        totalBeforeDiscounts = basePrice * quantityValue * complexityMultiplier;
      } else {
        totalBeforeDiscounts = basePrice * complexityMultiplier;
      }
      
      const subscriptionAmount = totalBeforeDiscounts * subscriptionDiscount;
      const paymentAmount = totalBeforeDiscounts * paymentDiscount;
      const finalPrice = totalBeforeDiscounts - subscriptionAmount - paymentAmount;
      
      // Display the result
      priceResult.textContent = '$' + finalPrice.toFixed(2);
      
      // Show price breakdown
      priceBreakdown.style.display = 'block';
      priceBreakdown.innerHTML = `
        <div class="price-breakdown-item">
          <span>Base Price:</span>
          <span>$${totalBeforeDiscounts.toFixed(2)}</span>
        </div>
        <div class="price-breakdown-item">
          <span>Subscription Discount:</span>
          <span>-$${subscriptionAmount.toFixed(2)}</span>
        </div>
        <div class="price-breakdown-item">
          <span>Payment Method Discount:</span>
          <span>-$${paymentAmount.toFixed(2)}</span>
        </div>
        <div class="price-breakdown-item total">
          <span>Total:</span>
          <span>$${finalPrice.toFixed(2)}</span>
        </div>
      `;
    }
    
    // Add event listener for calculate button
    calculateButton.addEventListener('click', calculatePrice);
    
    // Set form values from URL parameters on page load
    setFormFromUrlParams();
  });
})(); 