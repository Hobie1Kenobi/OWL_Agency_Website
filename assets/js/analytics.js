/**
 * OWL analytics. Fires Microsoft UET custom events (tag 97179628).
 * GA4 measurement ID is public by design. Loads gtag.js once when OWL_GA4_ID is set.
 * Do not also paste the Google HTML snippet on the same page (double-counts).
 */
(function (window, document) {
  'use strict';

  if (window.OWLAnalytics) return;

  if (!window.OWL_GA4_ID) {
    window.OWL_GA4_ID = 'G-Z6GYW6ZHNX';
  }

  window.uetq = window.uetq || [];

  function ensureGtag(id) {
    if (!id) return;
    if (typeof window.gtag === 'function') return;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag('js', new Date());
    window.gtag('config', id);
    if (document.querySelector('script[src*="googletagmanager.com/gtag/js"]')) return;
    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
    var first = document.getElementsByTagName('script')[0];
    if (first && first.parentNode) {
      first.parentNode.insertBefore(script, first);
    } else if (document.head) {
      document.head.appendChild(script);
    } else {
      document.documentElement.appendChild(script);
    }
  }

  ensureGtag(window.OWL_GA4_ID);

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
