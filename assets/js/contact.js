/**
 * Contact Form Handler for OWL AI Agency
 * Version: 1.0.0
 */
(function() {
  "use strict";

  // Select the contact form and form elements
  const contactForm = document.querySelector('.php-email-form');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      // Basic form validation
      let valid = true;
      const name = contactForm.querySelector('[name="name"]');
      const email = contactForm.querySelector('[name="email"]');
      const subject = contactForm.querySelector('[name="subject"]');
      const message = contactForm.querySelector('[name="message"]');
      
      // Clear previous error states
      contactForm.querySelectorAll('.error-message').forEach(el => el.remove());
      contactForm.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));
      
      // Validate name
      if (!name.value.trim()) {
        displayError(name, 'Please enter your name');
        valid = false;
      }
      
      // Validate email
      if (!isEmailValid(email.value)) {
        displayError(email, 'Please enter a valid email address');
        valid = false;
      }
      
      // Validate subject
      if (!subject.value.trim()) {
        displayError(subject, 'Please enter a subject');
        valid = false;
      }
      
      // Validate message
      if (!message.value.trim()) {
        displayError(message, 'Please enter your message');
        valid = false;
      }
      
      if (valid) {
        // Show loading indicator
        contactForm.querySelector('.loading').style.display = 'block';
        contactForm.querySelector('.error-message').style.display = 'none';
        contactForm.querySelector('.sent-message').style.display = 'none';
        
        // Simulate form submission (In a real app, replace with actual AJAX form submission)
        setTimeout(function() {
          // Hide loading indicator
          contactForm.querySelector('.loading').style.display = 'none';
          
          // Show success message
          contactForm.querySelector('.sent-message').style.display = 'block';
          
          // Reset form
          contactForm.reset();
          
          // In a real implementation, you would send the form data to your server
          /*
          fetch('your-server-endpoint', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: name.value,
              email: email.value,
              subject: subject.value,
              message: message.value
            })
          })
          .then(response => response.json())
          .then(data => {
            contactForm.querySelector('.loading').style.display = 'none';
            if (data.success) {
              contactForm.querySelector('.sent-message').style.display = 'block';
              contactForm.reset();
            } else {
              throw new Error(data.message || 'Form submission failed');
            }
          })
          .catch(error => {
            contactForm.querySelector('.loading').style.display = 'none';
            contactForm.querySelector('.error-message').textContent = error.message;
            contactForm.querySelector('.error-message').style.display = 'block';
          });
          */
        }, 1500);
      }
    });
  }
  
  // Helper function to display error messages
  function displayError(input, message) {
    input.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
  }
  
  // Helper function to validate email format
  function isEmailValid(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
})(); 