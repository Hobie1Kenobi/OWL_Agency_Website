/**
 * Use Cases Filter JS for OWL AI Agency
 * Version: 1.0.0
 */
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    let selectEl = select(el, all)
    if (selectEl) {
      if (all) {
        selectEl.forEach(e => e.addEventListener(type, listener))
      } else {
        selectEl.addEventListener(type, listener)
      }
    }
  }

  /**
   * Use Case filter
   */
  const useCaseFilter = () => {
    const filterItems = select('.filter-item', true);
    const useCaseItems = select('.use-case-item', true);
    
    if (filterItems.length && useCaseItems.length) {
      // Initialize with all items visible and "Featured" active
      let activeFilter = 'all';
      
      // Add click event to filter items
      on('click', '.filter-item', function(e) {
        e.preventDefault();
        
        // Remove active class from all filter items
        filterItems.forEach(item => {
          item.classList.remove('active');
        });
        
        // Add active class to clicked filter item
        this.classList.add('active');
        
        // Get the data-filter value
        activeFilter = this.getAttribute('data-filter');
        
        // Filter the use case items
        useCaseItems.forEach(item => {
          const category = item.getAttribute('data-category');
          
          if (activeFilter === 'all' || category === activeFilter) {
            item.style.display = 'block';
            // Add animation
            setTimeout(() => {
              item.style.opacity = '1';
              item.style.transform = 'translateY(0)';
            }, 50);
          } else {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            setTimeout(() => {
              item.style.display = 'none';
            }, 300);
          }
        });
      });
    }
  };

  // Initialize the use case filter
  useCaseFilter();
  
  // Add animation to use case cards on page load
  const animateUseCaseCards = () => {
    const cards = select('.use-case-card', true);
    
    if (cards.length) {
      cards.forEach((card, index) => {
        setTimeout(() => {
          card.classList.add('animated');
        }, index * 100);
      });
    }
  };
  
  // Initialize animations
  animateUseCaseCards();

  /**
   * URL parameter handling for pricing calculator
   */
  window.addEventListener('load', () => {
    // Check if we're on the pricing calculator page
    const calculator = select('#pricing-calculator');
    if (!calculator) return;
    
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    
    // Set service type if in URL
    const serviceParam = urlParams.get('service');
    const serviceSelect = select('#service-type');
    if (serviceParam && serviceSelect) {
      serviceSelect.value = serviceParam;
      // Trigger change event to update UI
      serviceSelect.dispatchEvent(new Event('change'));
    }
    
    // Set complexity if in URL
    const complexityParam = urlParams.get('complexity');
    const complexitySelect = select('#complexity');
    if (complexityParam && complexitySelect) {
      complexitySelect.value = complexityParam;
    }
    
    // Set quantity if in URL
    const quantityParam = urlParams.get('quantity');
    const quantityInput = select('#quantity');
    if (quantityParam && quantityInput) {
      quantityInput.value = quantityParam;
    }
    
    // Set subscription if in URL
    const subscriptionParam = urlParams.get('subscription');
    const subscriptionSelect = select('#subscription');
    if (subscriptionParam && subscriptionSelect) {
      subscriptionSelect.value = subscriptionParam;
    }
    
    // Trigger calculation if parameters were provided
    if (serviceParam || complexityParam || quantityParam || subscriptionParam) {
      const calculateBtn = select('#calculate-price');
      if (calculateBtn) {
        calculateBtn.click();
      }
    }
  });

})(); 