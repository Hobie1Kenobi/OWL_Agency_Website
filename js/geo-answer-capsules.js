// GEO answer capsules — concise Q&A blocks for AI citation (40–80 words each)
(function () {
  var SITE = 'https://owl-ai-agency.com';
  var capsules = [
    {
      question: 'What is OWL AI Legal Research?',
      answer:
        'OWL AI Legal Research is a six-agent paralegal automation platform for law firms. It verifies live public legal databases, maps precedents, and produces filing-ready memos, briefs, and tables of authorities. Packages start at $3,000 for 25 research runs.'
    },
    {
      question: 'How is OWL different from generic AI legal tools?',
      answer:
        'OWL runs a structured six-agent pipeline with live source verification—not a single chatbot. Outputs include Bluebook citations, case briefs, research memos, and motion drafts. A public Carpenter v. United States demo shows 12 authoritative sources end to end.'
    },
    {
      question: 'What does legal research automation cost for a mid-size firm?',
      answer:
        'OWL offers Starter at $3,000 (25 runs, 72-hour SLA), Professional at $6,000 (75 runs, 48-hour SLA), and Enterprise at $12,000 (unlimited runs, 24-hour SLA). A free consultation scopes jurisdiction, practice area, and deliverables before purchase.'
    },
    {
      question: 'How fast can a law firm start using OWL legal research?',
      answer:
        'After intake and payment, firms receive a private research workspace immediately. Turnaround per research run follows the package SLA: 72, 48, or 24 hours. Batch processing handles multiple matters in one workspace session.'
    }
  ];

  var schema = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: capsules.map(function (c) {
      return {
        '@type': 'Question',
        name: c.question,
        acceptedAnswer: { '@type': 'Answer', text: c.answer }
      };
    })
  };

  function injectCapsules() {
    var path = window.location.pathname.replace(/\/$/, '') || '/';
    if (path !== '/legal-research.html' && path !== '/legal-research') {
      return;
    }

    var script = document.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    document.head.appendChild(script);

    var section = document.getElementById('geo-answer-capsules');
    if (!section) {
      return;
    }
    var html = '<div class="container"><div class="row"><div class="col-lg-10 mx-auto">';
    html += '<h2 class="h4 mb-4">Quick answers</h2>';
    capsules.forEach(function (c) {
      html +=
        '<article class="mb-3" itemscope itemtype="https://schema.org/Question">' +
        '<h3 class="h6" itemprop="name">' +
        c.question +
        '</h3>' +
        '<p itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">' +
        '<span itemprop="text">' +
        c.answer +
        '</span></p></article>';
    });
    html += '<p class="small text-muted">Last updated: ' + new Date().toISOString().slice(0, 10) + '</p>';
    html += '</div></div></div>';
    section.innerHTML = html;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectCapsules);
  } else {
    injectCapsules();
  }
})();
