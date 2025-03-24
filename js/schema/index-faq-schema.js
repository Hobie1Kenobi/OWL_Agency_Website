// FAQ Schema for index.html
document.addEventListener('DOMContentLoaded', function() {
    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    schemaScript.innerHTML = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What services does OWL AI Agency provide?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "OWL AI Agency specializes in legal research automation, providing law firms with AI-powered tools for case law analysis, document review, precedent identification, and jurisdiction-specific research. Our services include batch processing for multiple documents, custom AI model training for specialized practice areas, and integration with existing legal databases."
      }
    },
    {
      "@type": "Question",
      "name": "How can law firms implement OWL AI's research automation?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Implementation follows a straightforward four-step process: initial consultation to understand your firm's research needs, system configuration and integration with your existing tools, custom training on your firm's precedent library, and ongoing optimization. Most firms are fully operational within 2-4 weeks with minimal disruption to existing workflows."
      }
    },
    {
      "@type": "Question",
      "name": "Does OWL AI support international legal research?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, OWL AI Agency supports international legal research across multiple jurisdictions including the US, UK, EU, Canada, and Australia. Our systems are designed to understand jurisdiction-specific legal language, citation formats, and precedent hierarchies, making them valuable for firms with international clients or cross-border cases."
      }
    }
  ]
};
    document.head.appendChild(schemaScript);
});
