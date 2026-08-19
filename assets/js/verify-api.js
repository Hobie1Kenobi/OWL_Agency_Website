/**
 * OWL citation verification client.
 *
 *   POST {API_BASE}/api/verify/citations
 *   Request JSON: { "text": "...", "matter_id": "optional" }
 *   Response 200 JSON: live report (citations, toa, audit, sources_queried).
 *
 * Sample packs supply SAMPLE excerpt text only. Results come from the backend.
 * Live fetch is not skipped for sample matters. If the API is unreachable,
 * the UI must show an explicit error — not a silent mock report.
 */
(function (window) {
  'use strict';

  var CHECK_META = [
    { id: 'existence', label: 'Existence' },
    { id: 'citation_format', label: 'Citation format' },
    { id: 'holding_support', label: 'Holding support' },
    { id: 'verification_path', label: 'Verification path' },
    { id: 'human_review_flag', label: 'Human review flag' }
  ];

  var TOA_GROUPS = [
    { id: 'us_supreme_court', label: 'U.S. Supreme Court' },
    { id: 'courts_of_appeals', label: 'Courts of Appeals' },
    { id: 'district_courts', label: 'District Courts' },
    { id: 'statutes_rules', label: 'Statutes / Rules' },
    { id: 'unresolved', label: 'Unresolved / short form' }
  ];

  var LIVE_TIMEOUT_MS = 45000;
  var MATTER_BASE = 'assets/data/verify-matters/';
  var packCache = { index: null, byId: {}, loading: null };

  function check(id, status, detail, extras) {
    extras = extras || {};
    var meta = CHECK_META.filter(function (item) { return item.id === id; })[0];
    return {
      id: id,
      label: meta ? meta.label : id,
      status: status,
      detail: detail,
      checked: extras.checked || '',
      against: extras.against || '',
      sourceUrl: extras.sourceUrl || null
    };
  }

  function humanReview(detail) {
    return check(
      'human_review_flag',
      'needs-review',
      detail || 'A person must review this result before the citation is used in a filing. OWL is a verification tool, not legal advice.',
      { checked: 'Whether a human still needs to look at this output', against: 'Filing accountability — the signer of the brief remains responsible' }
    );
  }

  function fetchJson(path) {
    return fetch(path, { headers: { Accept: 'application/json' } }).then(function (res) {
      if (!res.ok) throw new Error('HTTP ' + res.status + ' for ' + path);
      return res.json();
    });
  }

  function inferToaGroup(citation) {
    if (citation.toa_group) return citation.toa_group;
    if (citation.error === 'ambiguous') return 'unresolved';
    var blob = ((citation.normalized || citation.raw || '') + ' ' + (citation.reporter || '')).toLowerCase();
    if (/u\.s\.c\.|fed\.\s*r\.|u\.s\.\s*const/.test(blob)) return 'statutes_rules';
    if (/f\.\s*supp/.test(blob)) return 'district_courts';
    if (/f\.(?:2d|3d|4th)/.test(blob)) return 'courts_of_appeals';
    if (/\bu\.s\.|s\.\s*ct/.test(blob)) return 'us_supreme_court';
    return 'unresolved';
  }

  function overallStatus(citation) {
    var substantive = (citation.checks || []).filter(function (item) {
      return item.id !== 'human_review_flag';
    });
    if (citation.error === 'not_found' || substantive.some(function (item) { return item.status === 'fail'; })) {
      return 'fail';
    }
    if (
      citation.error === 'ambiguous' ||
      citation.error === 'source_unavailable' ||
      substantive.some(function (item) { return item.status === 'needs-review'; })
    ) {
      return 'needs-review';
    }
    return 'pass';
  }

  function isFlagged(citation) {
    return overallStatus(citation) !== 'pass';
  }

  function slugId(value, index) {
    var base = String(value || 'cite')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 40);
    return (base || 'cite') + '-' + index;
  }

  function ensureCitationShape(citation, index) {
    var copy = citation || {};
    copy.id = copy.id || slugId(copy.normalized || copy.raw, index);
    copy.span = copy.span || copy.raw || copy.normalized || '';
    copy.toa_group = inferToaGroup(copy);
    if (!copy.verification_path || !copy.verification_path.length) {
      copy.verification_path = [];
    }
    return copy;
  }

  function buildToa(citations) {
    var groups = TOA_GROUPS.map(function (group) {
      return { id: group.id, label: group.label, entries: [] };
    });
    var byId = {};
    groups.forEach(function (group) { byId[group.id] = group; });
    (citations || []).forEach(function (citation) {
      var group = byId[inferToaGroup(citation)] || byId.unresolved;
      group.entries.push({
        citationId: citation.id,
        cite: citation.normalized || citation.raw,
        court: citation.court || null,
        year: citation.year || null,
        overall: overallStatus(citation)
      });
    });
    return groups.filter(function (group) { return group.entries.length; });
  }

  function buildAudit(citations) {
    return (citations || []).map(function (citation) {
      return {
        citationId: citation.id,
        cite: citation.normalized || citation.raw,
        overall: overallStatus(citation),
        error: citation.error || null,
        flagged: isFlagged(citation),
        checks: citation.checks || []
      };
    });
  }

  function prefetchMatters() {
    if (packCache.loading) return packCache.loading;
    packCache.loading = fetchJson(MATTER_BASE + 'index.json').then(function (index) {
      packCache.index = index;
      var matters = (index && index.matters) || [];
      return Promise.all(matters.map(function (meta) {
        return fetchJson(MATTER_BASE + meta.file).then(function (pack) {
          packCache.byId[pack.id || meta.id] = pack;
          return pack;
        }).catch(function () {
          return null;
        });
      }));
    }).catch(function () {
      packCache.loading = null;
      return [];
    });
    return packCache.loading;
  }

  function listMatters() {
    return prefetchMatters().then(function () {
      return packCache.index || { matters: [] };
    });
  }

  function getMatter(id) {
    return prefetchMatters().then(function () {
      var pack = packCache.byId[id];
      if (!pack) throw new Error('Unknown sample matter: ' + id);
      return pack;
    });
  }

  function apiBase() {
    var cfg = window.OWL_LEGAL_CONFIG || {};
    return cfg.API_BASE || '';
  }

  function sourcesDown(payload) {
    var sources = (payload && payload.sources_queried) || [];
    if (!sources.length) return false;
    return sources.every(function (item) {
      return item.status === 'timeout' || item.status === 'blocked' || item.status === 'error';
    });
  }

  function normalizeLivePayload(data, text, matterId) {
    if (!data || !Array.isArray(data.citations)) {
      throw new Error('Live verify returned no citations array');
    }
    data.mode = 'live';
    data.input = text;
    data.excerpt = data.excerpt || text;
    data.citations = data.citations.map(ensureCitationShape);
    data.toa = data.toa && data.toa.length ? data.toa : buildToa(data.citations);
    data.audit = data.audit && data.audit.length ? data.audit : buildAudit(data.citations);
    data.sources_queried = data.sources_queried || [];
    if (typeof data.matter === 'undefined' || data.matter === null) {
      var pack = packCache.byId[matterId];
      data.matter = pack ? {
        id: pack.id,
        title: pack.title,
        matter_name: pack.matter_name || pack.title,
        practice_area: pack.practice_area || '',
        warning_banner: pack.warning_banner || '',
        default_selected: pack.default_selected || (data.citations[0] && data.citations[0].id) || null
      } : null;
    }
    if (sourcesDown(data)) {
      var err = new Error('PUBLIC_SOURCES_UNAVAILABLE');
      err.payload = data;
      throw err;
    }
    return data;
  }

  function tryLive(text, matterId) {
    var base = apiBase();
    if (!base) return Promise.reject(new Error('No API base'));
    var controller = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, LIVE_TIMEOUT_MS) : null;
    var body = { text: text };
    if (matterId) body.matter_id = matterId;
    return fetch(base.replace(/\/$/, '') + '/api/verify/citations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(body),
      signal: controller ? controller.signal : undefined
    }).then(function (res) {
      if (timer) clearTimeout(timer);
      if (!res.ok) throw new Error('Live verify HTTP ' + res.status);
      return res.json();
    }).then(function (data) {
      if (timer) clearTimeout(timer);
      return normalizeLivePayload(data, text, matterId);
    }).catch(function (err) {
      if (timer) clearTimeout(timer);
      throw err;
    });
  }

  function verify(text, matterId) {
    var trimmed = String(text || '').trim();
    return prefetchMatters().then(function () {
      return tryLive(trimmed, matterId);
    });
  }

  function offlinePreview(text) {
    var trimmed = String(text || '').trim();
    var pack = null;
    var ids = Object.keys(packCache.byId);
    for (var i = 0; i < ids.length; i++) {
      var candidate = packCache.byId[ids[i]];
      if (candidate && candidate.excerpt && trimmed === String(candidate.excerpt).trim()) {
        pack = candidate;
        break;
      }
    }
    var payload = {
      mode: 'offline-preview',
      input: trimmed,
      excerpt: trimmed,
      matter: pack ? {
        id: pack.id,
        title: pack.title,
        matter_name: pack.matter_name || pack.title,
        practice_area: pack.practice_area || '',
        warning_banner: pack.warning_banner || '',
        default_selected: null
      } : null,
      citations: [{
        id: 'offline-preview-0',
        span: trimmed.slice(0, 80),
        raw: trimmed.slice(0, 80),
        normalized: 'Offline sample preview',
        court: null,
        year: null,
        toa_group: 'unresolved',
        error: 'source_unavailable',
        errorMessage: 'This is an offline sample preview — not a live source check. Public sources were not queried.',
        proposition: trimmed.slice(0, 280),
        verification_path: [],
        checks: [
          check('existence', 'needs-review', 'Offline preview does not check existence against public sources.', { checked: trimmed.slice(0, 80), against: 'No live source' }),
          check('citation_format', 'needs-review', 'Offline preview does not score citation format.', { checked: trimmed.slice(0, 80), against: 'No live source' }),
          check('holding_support', 'needs-review', 'Offline preview does not score holding support.', { checked: 'SAMPLE excerpt', against: 'No live source' }),
          check('verification_path', 'fail', 'No public source was contacted.', { checked: 'SAMPLE excerpt', against: 'Offline preview' }),
          humanReview('Retry live verification when public sources are reachable. This preview is not a filing check.')
        ]
      }],
      toa: [],
      audit: [],
      sources_queried: []
    };
    payload.citations = payload.citations.map(ensureCitationShape);
    payload.toa = buildToa(payload.citations);
    payload.audit = buildAudit(payload.citations);
    return Promise.resolve(payload);
  }

  prefetchMatters();

  window.OWLVerifyAPI = {
    CHECK_META: CHECK_META,
    TOA_GROUPS: TOA_GROUPS,
    LIVE_TIMEOUT_MS: LIVE_TIMEOUT_MS,
    verify: verify,
    offlinePreview: offlinePreview,
    listMatters: listMatters,
    getMatter: getMatter,
    overallStatus: overallStatus,
    isFlagged: isFlagged,
    buildToa: buildToa,
    buildAudit: buildAudit,
    sourcesDown: sourcesDown
  };
})(window);
