// Review Schema for legal-research.html
document.addEventListener('DOMContentLoaded', function() {
    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    schemaScript.innerHTML = {
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Legal Research Automation",
  "description": "AI-powered legal research automation for law firms",
  "provider": {
    "@type": "Organization",
    "name": "OWL AI Agency",
    "url": "https://owl-ai-agency.com"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "bestRating": "5",
    "worstRating": "1",
    "ratingCount": "42"
  },
  "reviews": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Sarah Johnson",
        "jobTitle": "Managing Partner, Johnson & Associates"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5"
      },
      "datePublished": "2024-11-15",
      "reviewBody": "OWL AI's legal research automation has transformed our practice. We've reduced research time by 65% while improving the quality of our case preparation. The batch processing feature is a game-changer for our litigation team."
    },
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Michael Chen",
        "jobTitle": "Legal Technology Director, Global Law Partners"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "4.5",
        "bestRating": "5"
      },
      "datePublished": "2024-10-22",
      "reviewBody": "After implementing OWL AI's research tools, our associates can focus on higher-value analysis rather than preliminary research. The international jurisdiction support has been particularly valuable for our cross-border cases."
    },
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Elizabeth Rodriguez",
        "jobTitle": "Litigation Partner, Rodriguez & Williams LLP"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5"
      },
      "datePublished": "2024-09-30",
      "reviewBody": "The precision of OWL AI's legal research automation is remarkable. We've discovered relevant precedents that would have been nearly impossible to find through traditional methods. This has directly contributed to favorable outcomes in several complex cases."
    }
  ]
};
    document.head.appendChild(schemaScript);
});
