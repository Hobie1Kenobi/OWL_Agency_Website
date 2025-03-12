# OWL AI Agency Website

A modern, responsive website for the OWL AI Agency based on the Arsha template.

## Features

- Modern and responsive design
- Interactive pricing calculator
- Contact form with validation
- Color-changing animated owl logo
- Service showcases
- Team member profiles
- Testimonials section
- Subscription plans

## Project Structure

```
OWL_Agency_Website/
├── index.html                  # Main HTML file
├── assets/
│   ├── css/
│   │   └── style.css           # Custom styles 
│   ├── js/
│   │   ├── main.js             # Main JavaScript functionality
│   │   ├── contact.js          # Contact form handling
│   │   └── pricing-calculator.js # Service pricing calculator
│   └── img/
│       └── owl-logo.svg        # SVG logo with color-changing effect
└── README.md                   # This file
```

## Setup Instructions

1. **Clone or download this repository**

2. **Local Development**
   - Open the project folder in your code editor
   - For local development with live reload, you can use any local server like:
     - Live Server extension for VS Code
     - Python's http.server: `python -m http.server`
     - Node.js http-server: `npx http-server`

3. **Required Dependencies**
   The website uses CDN links for:
   - Bootstrap 5
   - AOS (Animate on Scroll)
   - Boxicons
   - GLightbox
   - Swiper
   - Remixicon
   
   No local installation is needed as these are loaded via CDN.

## Customization Guide

### General Customization

1. **Edit Text Content**
   - Open `index.html` and modify the text content within each section.

2. **Update Images**
   - Replace images in the `assets/img/` directory with your own.
   - Update image paths in the HTML as needed.

3. **Colors and Styling**
   - Edit `assets/css/style.css` to change colors, spacing, and other styling.
   - The main color scheme is defined at the top of the CSS file.

### Logo Customization

1. **Edit the SVG Logo**
   - Modify `assets/img/owl-logo.svg` to change the logo design.
   - Keep the `class="owl-logo-color"` attribute to maintain the color-changing effect.

2. **Change Logo Animation**
   - Edit the `@keyframes logoColorChange` in `assets/css/style.css` to change the color sequence or timing.

### Pricing Calculator

1. **Update Service Prices**
   - Edit the `servicePrices` object in `assets/js/pricing-calculator.js`.
   - Match these prices with your actual service offerings.

2. **Subscription Plans**
   - Modify the `subscriptionDiscounts` object to reflect your subscription tiers.
   - Update the corresponding HTML in the pricing section of `index.html`.

### Contact Form

1. **Set Up Form Submission**
   - Uncomment and configure the fetch API code in `assets/js/contact.js`.
   - Replace `'your-server-endpoint'` with your actual form handling endpoint.

## Deployment

1. **Prepare for Production**
   - Consider minifying CSS and JavaScript for production.
   - Optimize images for web delivery.

2. **Deployment Options**
   - GitHub Pages: Push to a GitHub repository and enable GitHub Pages.
   - Netlify: Connect your repository or drag-and-drop the folder to deploy.
   - Vercel: Similar to Netlify, connect your repository for automatic deployments.
   - Traditional web hosting: Upload files via FTP to your web hosting provider.

## License

This template is based on the Arsha Bootstrap template.

## About OWL AI Agency

OWL AI Agency provides AI-powered services including content creation, technical documentation, data analysis, and coding services. Our team of specialized AI agents work together to deliver high-quality results for our clients. 