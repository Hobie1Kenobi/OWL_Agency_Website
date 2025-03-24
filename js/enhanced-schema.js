// Enhanced Schema Markup for OWL AI Agency
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "OWL AI Agency",
  "url": "https://owl-ai-agency.com",
  "logo": "https://owl-ai-agency.com/assets/img/logo.png",
  "sameAs": [
    "https://twitter.com/OWL_AI_Agency",
    "https://linkedin.com/company/owl-ai-agency"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-985-790-1830",
    "contactType": "customer service",
    "areaServed": "Worldwide"
  }
};

const productSchema = {
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "OWL AI Legal Research Automation",
  "description": "AI-powered legal research automation platform that helps law firms find relevant precedents faster and analyze case law more effectively.",
  "brand": {
    "@type": "Brand",
    "name": "OWL AI Agency"
  },
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://owl-ai-agency.com/legal-research.html"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "150"
  }
};

const serviceSchema = {
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "Legal Research Automation",
  "provider": {
    "@type": "Organization",
    "name": "OWL AI Agency"
  },
  "areaServed": "Worldwide",
  "hasOfferCatalog": {
    "@type": "OfferCatalog",
    "name": "Legal Research Services",
    "itemListElement": [
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Basic Legal Research",
          "description": "Standard legal research automation with up to 10 tasks per month",
          "price": "499",
          "priceCurrency": "USD"
        }
      },
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Professional Legal Research",
          "description": "Advanced legal research automation with up to 25 tasks per month",
          "price": "999",
          "priceCurrency": "USD"
        }
      },
      {
        "@type": "Offer",
        "itemOffered": {
          "@type": "Service",
          "name": "Enterprise Legal Research",
          "description": "Comprehensive legal research automation with up to 75 tasks per month",
          "price": "2499",
          "priceCurrency": "USD"
        }
      }
    ]
  }
};

const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is legal research automation?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Legal research automation uses AI to streamline the process of finding relevant cases, statutes, and legal documents. Our system can reduce research time by up to 70% while improving accuracy."
      }
    },
    {
      "@type": "Question",
      "name": "How much does legal research automation cost?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Our legal research automation solutions are priced based on your firm's specific needs and scale. We offer flexible subscription plans starting at $499 per month."
      }
    },
    {
      "@type": "Question",
      "name": "How long does implementation take?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Implementation typically takes 2-4 weeks, depending on your firm's size and specific requirements. Our team provides comprehensive training and support throughout the process."
      }
    }
  ]
};

const reviewSchema = {
  "@context": "https://schema.org",
  "@type": "Review",
  "reviewRating": {
    "@type": "Rating",
    "ratingValue": "5",
    "bestRating": "5"
  },
  "author": {
    "@type": "Person",
    "name": "John Smith"
  },
  "reviewBody": "OWL AI Agency's legal research automation has transformed our practice. We've reduced research time by 70% while maintaining high accuracy. The ROI has been exceptional.",
  "datePublished": "2024-02-15",
  "itemReviewed": {
    "@type": "Product",
    "name": "OWL AI Legal Research Automation"
  }
};

const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://owl-ai-agency.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Legal Research",
      "item": "https://owl-ai-agency.com/legal-research.html"
    }
  ]
};

// Function to inject schemas into the page
function injectSchemas() {
  const schemas = [
    organizationSchema,
    productSchema,
    serviceSchema,
    faqSchema,
    reviewSchema,
    breadcrumbSchema
  ];

  schemas.forEach(schema => {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
  });
}

// Run when DOM is loaded
document.addEventListener('DOMContentLoaded', injectSchemas); 