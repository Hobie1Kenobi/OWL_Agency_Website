/**
 * Structured Data Implementation for OWL AI Agency
 * This file contains JSON-LD structured data to enhance search engine visibility
 * and SERP features for the OWL AI Agency website.
 */

// Service schema for Legal Research Automation
const legalResearchServiceSchema = {
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Legal Research Automation",
  "description": "AI-powered legal research automation service that analyzes cases, statutes, and precedents 10x faster than traditional methods.",
  "provider": {
    "@type": "Organization",
    "name": "OWL AI Agency",
    "logo": "https://owl-ai-agency.com/assets/img/logo.png",
    "url": "https://owl-ai-agency.com"
  },
  "serviceType": "Legal Technology",
  "areaServed": "Global",
  "offers": {
    "@type": "Offer",
    "price": "499.00",
    "priceCurrency": "USD",
    "priceValidUntil": "2025-12-31",
    "availability": "https://schema.org/InStock"
  },
  "termsOfService": "https://owl-ai-agency.com/terms-of-service",
  "url": "https://owl-ai-agency.com/legal-research.html"
};

// HowTo schema for implementing legal research automation
const legalResearchHowToSchema = {
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Implement Legal Research Automation in Your Law Firm",
  "description": "A step-by-step guide to implementing AI-powered legal research automation in your law practice.",
  "totalTime": "P2D",
  "tool": [
    {
      "@type": "HowToTool",
      "name": "OWL AI Agency Platform"
    },
    {
      "@type": "HowToTool",
      "name": "Document Management System"
    }
  ],
  "step": [
    {
      "@type": "HowToStep",
      "name": "Initial Assessment",
      "text": "Evaluate your current legal research processes and identify areas for automation.",
      "url": "https://owl-ai-agency.com/legal-research.html#assessment"
    },
    {
      "@type": "HowToStep",
      "name": "Platform Integration",
      "text": "Connect the OWL AI platform with your existing document management system.",
      "url": "https://owl-ai-agency.com/legal-research.html#integration"
    },
    {
      "@type": "HowToStep",
      "name": "Template Customization",
      "text": "Customize document templates to match your firm's branding and requirements.",
      "url": "https://owl-ai-agency.com/legal-research.html#customization"
    },
    {
      "@type": "HowToStep",
      "name": "Training and Deployment",
      "text": "Train your team on using the automated research tools and deploy the system.",
      "url": "https://owl-ai-agency.com/legal-research.html#deployment"
    }
  ]
};

// LocalBusiness schema for OWL AI Agency
const localBusinessSchema = {
  "@context": "https://schema.org",
  "@type": "ProfessionalService",
  "name": "OWL AI Agency",
  "description": "AI-powered service platform specializing in legal research automation and document analysis.",
  "url": "https://owl-ai-agency.com",
  "logo": "https://owl-ai-agency.com/assets/img/logo.png",
  "image": "https://owl-ai-agency.com/assets/img/hero-bg.jpg",
  "telephone": "+1-555-OWL-TECH",
  "email": "info@owl-ai-agency.com",
  "priceRange": "$$$",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 AI Boulevard",
    "addressLocality": "Tech City",
    "addressRegion": "CA",
    "postalCode": "94043",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 37.4220,
    "longitude": -122.0841
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "09:00",
      "closes": "17:00"
    }
  ],
  "sameAs": [
    "https://twitter.com/owlaiagency",
    "https://www.linkedin.com/company/owl-ai-agency",
    "https://github.com/owl-ai-agency"
  ]
};

// Product schema for Batch Processing feature
const batchProcessingProductSchema = {
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Batch Processing for Legal Research",
  "description": "Process multiple legal questions and generate comprehensive reports in batch, reducing analysis time by 85%.",
  "brand": {
    "@type": "Brand",
    "name": "OWL AI Agency"
  },
  "offers": {
    "@type": "Offer",
    "price": "799.00",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "priceValidUntil": "2025-12-31"
  },
  "image": "https://owl-ai-agency.com/assets/img/blog/batch-processing.jpg",
  "url": "https://owl-ai-agency.com/blog/batch-processing-legal-research.html"
};

// Speakable schema for voice search optimization
const speakableSchema = {
  "@context": "https://schema.org",
  "@type": "WebPage",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".speakable", "h1", ".section-title h2"]
  },
  "url": "https://owl-ai-agency.com/legal-research.html"
};

// Function to inject structured data into the page
function injectStructuredData() {
  const currentPage = window.location.pathname;
  
  // Array to hold applicable schemas for the current page
  const applicableSchemas = [];
  
  // Add schemas based on the current page
  if (currentPage === '/' || currentPage === '/index.html') {
    applicableSchemas.push(localBusinessSchema);
  }
  
  if (currentPage === '/legal-research.html') {
    applicableSchemas.push(legalResearchServiceSchema);
    applicableSchemas.push(legalResearchHowToSchema);
    applicableSchemas.push(speakableSchema);
  }
  
  if (currentPage === '/blog/batch-processing-legal-research.html') {
    applicableSchemas.push(batchProcessingProductSchema);
  }
  
  // Inject each applicable schema into the page
  applicableSchemas.forEach(schema => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
  });
}

// Execute when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', injectStructuredData);
