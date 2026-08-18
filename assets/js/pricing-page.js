/**
 * Renders pricing tiers from assets/data/pricing.json (single source of dollar figures).
 */
(function () {
  'use strict';

  var container = document.getElementById('pricing-tiers');
  var errorEl = document.getElementById('pricing-error');
  if (!container) return;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function cadenceSuffix(tier) {
    if (tier.cadence === 'month') return '<span>per month</span>';
    if (tier.cadence === 'per_document') return '<span>per brief or memo</span>';
    return '';
  }

  function render(data) {
    var order = ['free', 'perDocument', 'firm', 'enterprise'];
    var html = order.map(function (key, index) {
      var tier = data.tiers[key];
      if (!tier) return '';
      var featured = key === 'firm' ? ' featured' : '';
      var delay = (index + 1) * 100;
      var tierTag = key === 'perDocument' ? 'per_document' : key;
      var features = (tier.features || []).map(function (item) {
        return '<li><i class="bx bx-check"></i> ' + escapeHtml(item) + '</li>';
      }).join('');
      return (
        '<div class="col-lg-3 col-md-6 mt-4 mt-lg-0" data-aos="fade-up" data-aos-delay="' + delay + '">' +
          '<div class="box' + featured + '">' +
            '<h3>' + escapeHtml(tier.name) + '</h3>' +
            '<h4>' + escapeHtml(tier.priceLabel) + cadenceSuffix(tier) + '</h4>' +
            '<p>' + escapeHtml(tier.summary) + '</p>' +
            '<ul>' + features + '</ul>' +
            '<a class="buy-btn" href="' + escapeHtml(tier.ctaHref) + '" data-owl-event="pricing_cta_click" data-owl-tier="' + escapeHtml(tierTag) + '">' + escapeHtml(tier.ctaLabel) + '</a>' +
          '</div>' +
        '</div>'
      );
    }).join('');
    container.innerHTML = html;
  }

  fetch('assets/data/pricing.json')
    .then(function (res) {
      if (!res.ok) throw new Error('Could not load pricing');
      return res.json();
    })
    .then(render)
    .catch(function () {
      if (errorEl) errorEl.hidden = false;
    });
})();
