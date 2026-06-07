// Enhanced Schema Markup for OWL AI Agency
const SITE = 'https://owl-ai-agency.com';
const LEGAL_RESEARCH_IMAGE = SITE + '/assets/img/blog/legal-research-automation.jpg';

const organizationSchema = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'OWL AI Agency',
  url: SITE,
  logo: SITE + '/assets/img/favicon.svg',
  sameAs: [
    'https://twitter.com/OWL_AI_Agency',
    'https://linkedin.com/company/owl-ai-agency'
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+1-985-790-1830',
    contactType: 'customer service',
    areaServed: 'Worldwide'
  }
};

const legalResearchOfferCatalog = {
  '@type': 'OfferCatalog',
  name: 'OWL Legal Research Packages',
  itemListElement: [
    {
      '@type': 'Offer',
      name: 'Starter Package',
      price: '3000',
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: SITE + '/legal-research.html#intake',
      itemOffered: {
        '@type': 'Service',
        name: 'Starter Legal Research Package',
        description: 'Up to 25 case research runs with research memo, case brief, and table of authorities. 72-hour turnaround.'
      }
    },
    {
      '@type': 'Offer',
      name: 'Professional Package',
      price: '6000',
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: SITE + '/legal-research.html#intake',
      itemOffered: {
        '@type': 'Service',
        name: 'Professional Legal Research Package',
        description: 'Up to 75 case research runs with full six-document paralegal package, custom branding, and 48-hour turnaround.'
      }
    },
    {
      '@type': 'Offer',
      name: 'Enterprise Package',
      price: '12000',
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: SITE + '/legal-research.html#intake',
      itemOffered: {
        '@type': 'Service',
        name: 'Enterprise Legal Research Package',
        description: 'Unlimited case research runs, premium templates, API access, white-label branding, and 24-hour turnaround.'
      }
    },
    {
      '@type': 'Offer',
      name: 'Free Consultation',
      price: '0',
      priceCurrency: 'USD',
      availability: 'https://schema.org/InStock',
      url: SITE + '/legal-research.html#intake',
      itemOffered: {
        '@type': 'Service',
        name: 'Legal Research Consultation',
        description: 'Complimentary scoping call for law firms evaluating OWL legal research automation.'
      }
    }
  ]
};

const legalResearchServiceSchema = {
  '@context': 'https://schema.org',
  '@type': 'Service',
  name: 'OWL AI Legal Research Automation',
  description: 'AI-powered multi-agent paralegal research for law firms. Six specialized agents analyze case law, map precedents, draft memos and briefs, and verify live public legal databases.',
  serviceType: 'Legal Research Automation',
  image: LEGAL_RESEARCH_IMAGE,
  url: SITE + '/legal-research.html',
  provider: {
    '@type': 'Organization',
    name: 'OWL AI Agency',
    url: SITE
  },
  areaServed: 'Worldwide',
  hasOfferCatalog: legalResearchOfferCatalog
};

const faqSchema = {
  '@context': 'https://schema.org',
  '@type': 'FAQPage',
  mainEntity: [
    {
      '@type': 'Question',
      name: 'What is legal research automation?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'Legal research automation uses AI agents to streamline finding relevant cases, statutes, and precedents. OWL deploys six paralegal agents that verify live public legal sources and produce filing-ready drafts.'
      }
    },
    {
      '@type': 'Question',
      name: 'How much does legal research automation cost?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'OWL Legal Research offers project packages: Starter at $3,000 (25 runs), Professional at $6,000 (75 runs), and Enterprise at $12,000 (unlimited runs). A free consultation is also available.'
      }
    },
    {
      '@type': 'Question',
      name: 'How long does implementation take?',
      acceptedAnswer: {
        '@type': 'Answer',
        text: 'After intake and payment, your private research workspace is available immediately. Turnaround SLAs are 72 hours (Starter), 48 hours (Professional), or 24 hours (Enterprise) per research run.'
      }
    }
  ]
};

const reviewSchema = {
  '@context': 'https://schema.org',
  '@type': 'Review',
  reviewRating: {
    '@type': 'Rating',
    ratingValue: '5',
    bestRating: '5'
  },
  author: {
    '@type': 'Person',
    name: 'John Smith'
  },
  reviewBody: "OWL AI Agency's legal research automation has transformed our practice. We've reduced research time by 70% while maintaining high accuracy. The ROI has been exceptional.",
  datePublished: '2024-02-15',
  itemReviewed: {
    '@type': 'Service',
    name: 'OWL AI Legal Research Automation',
    url: SITE + '/legal-research.html'
  }
};

const breadcrumbSchema = {
  '@context': 'https://schema.org',
  '@type': 'BreadcrumbList',
  itemListElement: [
    {
      '@type': 'ListItem',
      position: 1,
      name: 'Home',
      item: SITE
    },
    {
      '@type': 'ListItem',
      position: 2,
      name: 'Legal Research',
      item: SITE + '/legal-research.html'
    }
  ]
};

function injectSchemas() {
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  const schemas = [organizationSchema];

  if (path === '/' || path === '/index.html' || path === '/legal-research.html') {
    schemas.push(legalResearchServiceSchema);
  }

  if (path === '/legal-research.html') {
    schemas.push(faqSchema, reviewSchema, breadcrumbSchema);
  }

  schemas.forEach(function (schema) {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
  });
}

document.addEventListener('DOMContentLoaded', injectSchemas);
