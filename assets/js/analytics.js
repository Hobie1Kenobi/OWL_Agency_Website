/**
 * OWL analytics. Fires Microsoft UET custom events (tag 97179628).
 * To add GA4 later: set window.OWL_GA4_ID = 'G-XXXXXXXX' before this file and load gtag.js — do not invent an ID.
 */
(function (window, document) {
  'use strict';

  window.uetq = window.uetq || [];

  function track(name, params) {
    var payload = params || {};
    try {
      window.uetq.push('event', name, payload);
    } catch (err) {
      if (window.console && console.warn) {
        console.warn('OWL analytics UET event failed:', name, err);
      }
    }
    if (window.OWL_GA4_ID && typeof window.gtag === 'function') {
      try {
        window.gtag('event', name, payload);
      } catch (err) {
        if (window.console && console.warn) {
          console.warn('OWL analytics GA4 event failed:', name, err);
        }
      }
    }
  }

  window.OWLAnalytics = { track: track };

  document.addEventListener('click', function (event) {
    var el = event.target.closest('[data-owl-event]');
    if (!el) return;
    var name = el.getAttribute('data-owl-event');
    if (!name) return;
    var params = {};
    var tier = el.getAttribute('data-owl-tier');
    if (tier) params.tier = tier;
    var label = el.getAttribute('data-owl-label');
    if (label) params.event_label = label;
    track(name, params);
  });

  document.addEventListener('submit', function (event) {
    var form = event.target;
    if (!form || !form.getAttribute) return;
    var name = form.getAttribute('data-owl-event');
    if (name) track(name, { event_label: form.id || 'form' });
  });

  var path = (window.location.pathname || '').toLowerCase();
  var onPricing = path.indexOf('/pricing') !== -1 || /pricing\.html$/.test(path);
  if (onPricing) {
    var fromQuery = /(?:\?|&)from=verify(?:&|$)/.test(window.location.search || '');
    var fromRef = /\/verify(?:\.html)?(?:[?#]|$)/i.test(document.referrer || '');
    if (fromQuery || fromRef) {
      track('pricing_view_from_demo', {
        source: fromQuery ? 'query' : 'referrer',
        event_label: 'verify'
      });
    }
  }
})(window, document);
