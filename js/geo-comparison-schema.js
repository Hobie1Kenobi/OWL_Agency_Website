(function () {
  if (!window.OWL_GEO_COMPARISON) return;

  var data = window.OWL_GEO_COMPARISON;
  var schema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: (data.faqs || []).map(function (f) {
      return {
        '@type': 'Question',
        name: f.q,
        acceptedAnswer: { '@type': 'Answer', text: f.a }
      };
    })
  };

  var script = document.createElement('script');
  script.type = 'application/ld+json';
  script.text = JSON.stringify(schema);
  document.head.appendChild(script);

  if (data.webPage) {
    var wp = document.createElement('script');
    wp.type = 'application/ld+json';
    wp.text = JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'WebPage',
      name: data.webPage.name,
      description: data.webPage.description,
      url: data.webPage.url,
      dateModified: data.webPage.dateModified || new Date().toISOString().slice(0, 10),
      publisher: { '@type': 'Organization', name: 'OWL AI Agency', url: 'https://owl-ai-agency.com' }
    });
    document.head.appendChild(wp);
  }
})();
