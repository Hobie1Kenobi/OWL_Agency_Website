/**
 * Structured Data Implementation for OWL AI Agency
 * Service-based schema only (no Product/Merchant listings).
 */

const SITE = 'https://owl-ai-agency.com';

const legalResearchHowToSchema = {
  '@context': 'https://schema.org',
  '@type': 'HowTo',
  name: 'How to Start OWL Legal Research for Your Law Firm',
  description: 'Submit intake, complete payment, and run the six-agent paralegal pipeline in your private workspace.',
  totalTime: 'P1D',
  step: [
    {
      '@type': 'HowToStep',
      name: 'Select a package',
      text: 'Choose Starter ($3,000), Professional ($6,000), or Enterprise ($12,000) based on your case volume.',
      url: SITE + '/legal-research.html#pricing'
    },
    {
      '@type': 'HowToStep',
      name: 'Submit intake',
      text: 'Complete the intake form with jurisdiction, practice area, and research question.',
      url: SITE + '/legal-research.html#intake'
    },
    {
      '@type': 'HowToStep',
      name: 'Pay and unlock workspace',
      text: 'Secure checkout activates your private legal research workspace immediately.',
      url: SITE + '/legal-research.html#payment'
    },
    {
      '@type': 'HowToStep',
      name: 'Run the paralegal pipeline',
      text: 'Submit research questions and download memos, briefs, motions, and CSV reports.',
      url: SITE + '/legal-research-workspace.html'
    }
  ]
};

const localBusinessSchema = {
  '@context': 'https://schema.org',
  '@type': 'ProfessionalService',
  name: 'OWL AI Agency',
  description: 'AI-powered legal research automation and multi-agent paralegal services for law firms.',
  url: SITE,
  logo: SITE + '/assets/img/favicon.svg',
  image: SITE + '/assets/img/blog/legal-research-automation.jpg',
  telephone: '+1-985-790-1830',
  email: 'sales@owl-ai-agency.com',
  priceRange: '$$$',
  areaServed: 'Worldwide',
  sameAs: [
    'https://twitter.com/OWL_AI_Agency',
    'https://www.linkedin.com/company/owl-ai-agency'
  ]
};

const batchProcessingServiceSchema = {
  '@context': 'https://schema.org',
  '@type': 'Service',
  name: 'Batch Processing for Legal Research',
  description: 'Process multiple legal questions and generate comprehensive reports in batch, reducing analysis time significantly.',
  serviceType: 'Legal Research Automation',
  image: SITE + '/assets/img/blog/batch-processing.jpg',
  url: SITE + '/blog/batch-processing-legal-research.html',
  provider: {
    '@type': 'Organization',
    name: 'OWL AI Agency',
    url: SITE
  },
  offers: {
    '@type': 'Offer',
    price: '6000',
    priceCurrency: 'USD',
    availability: 'https://schema.org/InStock',
    url: SITE + '/legal-research.html#intake',
    itemOffered: {
      '@type': 'Service',
      name: 'Professional Legal Research Package',
      description: 'Includes batch-capable research runs for mid-sized firms.'
    }
  }
};

const speakableSchema = {
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  speakable: {
    '@type': 'SpeakableSpecification',
    cssSelector: ['.speakable', 'h1', '.section-title h2']
  },
  url: SITE + '/legal-research.html'
};

function injectStructuredData() {
  const path = window.location.pathname.replace(/\/$/, '') || '/';
  const applicableSchemas = [];

  if (path === '/' || path === '/index.html') {
    applicableSchemas.push(localBusinessSchema);
  }

  if (path === '/legal-research.html') {
    applicableSchemas.push(legalResearchHowToSchema);
    applicableSchemas.push(speakableSchema);
  }

  if (path === '/blog/batch-processing-legal-research.html') {
    applicableSchemas.push(batchProcessingServiceSchema);
  }

  applicableSchemas.forEach(function (schema) {
    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);
  });
}

document.addEventListener('DOMContentLoaded', injectStructuredData);
