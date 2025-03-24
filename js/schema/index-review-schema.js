// Review Schema for index.html
document.addEventListener('DOMContentLoaded', function() {
    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    schemaScript.innerHTML = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "OWL AI Agency",
  "url": "https://owl-ai-agency.com",
  "description": "AI solutions for legal research automation and document analysis",
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "bestRating": "5",
    "worstRating": "1",
    "ratingCount": "68"
  },
  "reviews": [
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "David Thornton",
        "jobTitle": "CTO, Thornton Legal Group"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "5",
        "bestRating": "5"
      },
      "datePublished": "2024-12-05",
      "reviewBody": "OWL AI Agency has revolutionized how our firm approaches legal research. Their AI solutions are intuitive, powerful, and designed specifically for legal professionals. The ROI has been substantial."
    },
    {
      "@type": "Review",
      "author": {
        "@type": "Person",
        "name": "Amanda Patel",
        "jobTitle": "Senior Associate, International Law Partners"
      },
      "reviewRating": {
        "@type": "Rating",
        "ratingValue": "4.5",
        "bestRating": "5"
      },
      "datePublished": "2024-11-18",
      "reviewBody": "Working with OWL AI has given our firm a competitive edge. Their understanding of legal research challenges and ability to customize solutions to our specific practice areas has been invaluable."
    }
  ]
};
    document.head.appendChild(schemaScript);
});
