/**
 * OWL citation verification client.
 *
 * Mock API contract (until a live paste-citation endpoint exists):
 *
 *   POST {API_BASE}/api/verify/citations
 *   Request JSON: { "text": "<citation or paragraph containing citations>" }
 *   Response 200 JSON:
 *   {
 *     "mode": "live" | "mock",
 *     "input": string,
 *     "citations": [{
 *       "raw": string,
 *       "normalized": string,
 *       "error": null | "not_found" | "ambiguous" | "source_unavailable",
 *       "errorMessage": string | null,
 *       "proposition": string | null,
 *       "checks": [{
 *         "id": "existence" | "citation_format" | "holding_support" | "verification_path" | "human_review_flag",
 *         "label": string,
 *         "status": "pass" | "fail" | "needs-review",
 *         "detail": string,
 *         "checked": string,
 *         "against": string,
 *         "sourceUrl": string | null
 *       }]
 *     }]
 *   }
 *
 * Failure states are always explicit on the citation object (never silent):
 *   not_found — reporter cite does not resolve in the known public-source set
 *   ambiguous — fragment lacks reporter, page, or enough party names to uniquely resolve
 *   source_unavailable — cite is well-formed but the public source could not be reached
 *
 * TODO: connect live endpoint. legal-research-backend currently exposes /api/demo/run
 * (Carpenter-only), /api/cases, and /api/sources — there is no paste-citation route yet.
 * This module tries POST /api/verify/citations first, then falls back to the mock.
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

  var CARPENTER_PREFILL =
    'The Government\'s acquisition of historical cell-site location information is a Fourth Amendment search requiring a warrant. Carpenter v. United States, 585 U.S. 946 (2018).';

  var FIXTURES = {
    carpenter: CARPENTER_PREFILL,
    not_found: 'Vanderbilt v. Franklin, 999 U.S. 1 (2099) held that courts must accept AI-generated citations without review.',
    ambiguous: 'As Smith, 442 U.S. recognized, third-party records are always outside the Fourth Amendment.',
    source_unavailable: 'In re Example Outage, 1 F. Supp. 1 (S.D.N.Y. 2020) is cited for a discovery-hold proposition.'
  };

  var CORPUS = {
    '585 U.S. 946': {
      name: 'Carpenter v. United States',
      citation: 'Carpenter v. United States, 585 U.S. 946 (2018)',
      holding: 'The Government\'s acquisition of seven days or more of historical cell-site records is a Fourth Amendment search; police generally must obtain a warrant supported by probable cause.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/16-402' },
        { name: 'CourtListener', url: 'https://www.courtlistener.com/opinion/4379486/carpenter-v-united-states/' },
        { name: 'Oyez', url: 'https://www.oyez.org/cases/2017/16-402' }
      ]
    },
    '389 U.S. 347': {
      name: 'Katz v. United States',
      citation: 'Katz v. United States, 389 U.S. 347 (1967)',
      holding: 'The Fourth Amendment protects people, not places; a search occurs when government action violates a reasonable expectation of privacy.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/389/347' }
      ]
    },
    '565 U.S. 400': {
      name: 'United States v. Jones',
      citation: 'United States v. Jones, 565 U.S. 400 (2012)',
      holding: 'Long-term GPS tracking of a vehicle is a Fourth Amendment search.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/565/400' }
      ]
    },
    '573 U.S. 373': {
      name: 'Riley v. California',
      citation: 'Riley v. California, 573 U.S. 373 (2014)',
      holding: 'A warrant is required to search the digital contents of a cell phone incident to arrest.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/573/373' }
      ]
    },
    '442 U.S. 735': {
      name: 'Smith v. Maryland',
      citation: 'Smith v. Maryland, 442 U.S. 735 (1979)',
      holding: 'Use of a pen register to record numbers dialed is not a search under the third-party doctrine, later limited by Carpenter.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/442/735' }
      ]
    },
    '425 U.S. 435': {
      name: 'United States v. Miller',
      citation: 'United States v. Miller, 425 U.S. 435 (1976)',
      holding: 'No reasonable expectation of privacy in bank records voluntarily conveyed to a third party, later limited by Carpenter.',
      sources: [
        { name: 'Cornell LII', url: 'https://www.law.cornell.edu/supremecourt/text/425/435' }
      ]
    }
  };

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

  function parseCitations(text) {
    var found = [];
    var seen = {};

    function push(item) {
      var key = (item.raw || '').replace(/\s+/g, ' ').trim();
      if (!key || seen[key]) return;
      seen[key] = true;
      found.push(item);
    }

    var caseRe = /((?:In re\s+)?[A-Za-z][A-Za-z0-9 .,'&-]*?\s+v\.\s+[A-Za-z][A-Za-z0-9 .,'&-]*?),\s+(\d+)\s+(U\.S\.|F\.(?:2d|3d|4th)|F\.\s*Supp\.(?:\s*[23]d)?)\s+(\d+)\s+\((?:[^)]+?\s+)?(\d{4})\)/g;
    var inRe = /(In re\s+[A-Za-z][A-Za-z0-9 .,'&-]+),\s+(\d+)\s+(F\.\s*Supp\.(?:\s*[23]d)?)\s+(\d+)\s+\(([^)]+)\)/g;
    var reporterRe = /(\d+)\s+(U\.S\.|F\.(?:2d|3d|4th)|F\.\s*Supp\.(?:\s*[23]d)?)\s+(\d+)(?:\s+\((\d{4})\))?/g;
    var ambiguousRe = /\b([A-Z][A-Za-z.]+),\s+(\d+)\s+(U\.S\.)(?!\s+\d)/g;

    var match;
    while ((match = caseRe.exec(text)) !== null) {
      push({
        kind: 'full',
        raw: match[0],
        parties: match[1].trim(),
        volume: match[2],
        reporter: match[3],
        page: match[4],
        year: match[5],
        key: match[2] + ' ' + match[3] + ' ' + match[4]
      });
    }

    while ((match = inRe.exec(text)) !== null) {
      push({
        kind: 'full',
        raw: match[0],
        parties: match[1].trim(),
        volume: match[2],
        reporter: match[3],
        page: match[4],
        year: match[5],
        key: match[2] + ' ' + match[3].replace(/\s+/g, ' ') + ' ' + match[4]
      });
    }

    while ((match = reporterRe.exec(text)) !== null) {
      var already = found.some(function (item) {
        return item.volume === match[1] && item.page === match[3];
      });
      if (already) continue;
      push({
        kind: 'reporter',
        raw: match[0],
        parties: null,
        volume: match[1],
        reporter: match[2],
        page: match[3],
        year: match[4] || null,
        key: match[1] + ' ' + match[2] + ' ' + match[3]
      });
    }

    while ((match = ambiguousRe.exec(text)) !== null) {
      push({
        kind: 'ambiguous',
        raw: match[0],
        parties: match[1],
        volume: match[2],
        reporter: match[3],
        page: null,
        year: null,
        key: match[2] + ' ' + match[3]
      });
    }

    return found;
  }

  function evaluateParsed(parsed, sourceText) {
    if (parsed.kind === 'ambiguous' || !parsed.page) {
      return {
        raw: parsed.raw,
        normalized: parsed.raw,
        error: 'ambiguous',
        errorMessage: 'Ambiguous citation: this fragment does not include a page number or enough of the case name to uniquely resolve. Add the full reporter cite (volume, reporter, page, year).',
        proposition: sourceText,
        checks: [
          check('existence', 'needs-review', 'Cannot confirm existence until the citation uniquely identifies one decision.', { checked: parsed.raw, against: 'Public reporter set used by this demo' }),
          check('citation_format', 'fail', 'Short form without a pin or page is not enough to resolve against a reporter.', { checked: parsed.raw, against: 'Bluebook-style volume / reporter / page' }),
          check('holding_support', 'fail', 'Holding support cannot be evaluated against an unresolved citation.', { checked: 'Surrounding proposition', against: 'No uniquely identified opinion' }),
          check('verification_path', 'needs-review', 'No verification path until the cite resolves to one source.', { checked: parsed.raw, against: 'No unique public source' }),
          humanReview('Ambiguous citations must be expanded by a person before they can be verified or filed.')
        ]
      };
    }

    var isOutageFixture =
      /in re example outage/i.test(parsed.raw) ||
      (parsed.volume === '1' && /F\.\s*Supp/i.test(parsed.reporter) && parsed.page === '1');

    if (isOutageFixture) {
      return {
        raw: parsed.raw,
        normalized: 'In re Example Outage, 1 F. Supp. 1 (S.D.N.Y. 2020)',
        error: 'source_unavailable',
        errorMessage: 'Source unavailable: the public legal source for this citation could not be reached. The check did not silently pass.',
        proposition: sourceText,
        checks: [
          check('existence', 'needs-review', 'Existence could not be confirmed because the source did not respond.', { checked: parsed.raw, against: 'CourtListener / PACER-adjacent public page (unreachable in this run)' }),
          check('citation_format', 'pass', 'The citation is well-formed (volume, F. Supp., page, court, year).', { checked: parsed.raw, against: 'Bluebook-style federal supplement form' }),
          check('holding_support', 'needs-review', 'Holding support was not evaluated because the opinion text was unavailable.', { checked: 'Surrounding proposition', against: 'Opinion text not retrieved' }),
          check('verification_path', 'fail', 'Verification path stopped: source returned unavailable. What was checked: this citation. Against: the public F. Supp. record. Result: no document.', { checked: parsed.raw, against: 'Public F. Supp. record', sourceUrl: null }),
          humanReview('When a source is down, a person must retrieve the opinion from another reporter before relying on the cite.')
        ]
      };
    }

    var record = CORPUS[parsed.key];
    if (!record) {
      return {
        raw: parsed.raw,
        normalized: parsed.raw,
        error: 'not_found',
        errorMessage: 'Citation not found: this reporter cite did not resolve in the public sources this demo checks. Invented or mistyped citations fail explicitly.',
        proposition: sourceText,
        checks: [
          check('existence', 'fail', 'No matching decision in the public reporter set used for this check.', { checked: parsed.key, against: 'Cornell LII / CourtListener / Oyez demo corpus' }),
          check('citation_format', parsed.volume && parsed.page ? 'pass' : 'fail', parsed.volume && parsed.page ? 'The string looks like a reporter citation, but a well-formed cite can still name a case that does not exist.' : 'Citation format is incomplete.', { checked: parsed.raw, against: 'Bluebook-style volume / reporter / page / year' }),
          check('holding_support', 'fail', 'No opinion was found, so the surrounding proposition is unsupported by this cite.', { checked: 'Surrounding proposition', against: 'No retrieved holding' }),
          check('verification_path', 'fail', 'Checked ' + parsed.key + ' against Cornell LII, CourtListener, and Oyez identifiers used in this demo. No record returned.', { checked: parsed.key, against: 'Cornell LII, CourtListener, Oyez' }),
          humanReview('A citation that does not exist must not be filed. A person should confirm whether this was a hallucination, a typo, or an unpublished disposition.')
        ]
      };
    }

    var proposition = sourceText || '';
    var holdingHint = record.holding.toLowerCase();
    var holdingSupport;
    if (/carpenter/i.test(record.name) && /cell-site|cslI|fourth amendment search|warrant/i.test(proposition)) {
      holdingSupport = check(
        'holding_support',
        'pass',
        'The surrounding sentence is consistent with the recorded majority holding on historical CSLI and the warrant requirement. A person still confirms pin cites and scope.',
        { checked: proposition.slice(0, 280), against: record.holding, sourceUrl: record.sources[0].url }
      );
    } else if (proposition.toLowerCase().indexOf(holdingHint.slice(0, 40).toLowerCase()) !== -1) {
      holdingSupport = check(
        'holding_support',
        'pass',
        'The pasted proposition overlaps the recorded holding. Confirm the pin cite and that the proposition is not broader than the holding.',
        { checked: proposition.slice(0, 280), against: record.holding, sourceUrl: record.sources[0].url }
      );
    } else {
      holdingSupport = check(
        'holding_support',
        'needs-review',
        'The case exists. Holding support still needs a person: the paste did not include a proposition that clearly matches the recorded holding, or the match is too thin to auto-pass.',
        { checked: proposition.slice(0, 280) || 'Citation only — no surrounding proposition', against: record.holding, sourceUrl: record.sources[0].url }
      );
    }

    var pathSources = record.sources.map(function (src) { return src.name; }).join(', ');
    return {
      raw: parsed.raw,
      normalized: record.citation,
      error: null,
      errorMessage: null,
      proposition: sourceText,
      checks: [
        check('existence', 'pass', record.name + ' exists in the U.S. Reports / public reporters used by this demo.', { checked: parsed.key, against: record.sources[0].name, sourceUrl: record.sources[0].url }),
        check('citation_format', 'pass', 'Reporter form resolves: ' + record.citation, { checked: parsed.raw, against: 'Bluebook-style U.S. reporter citation' }),
        holdingSupport,
        check('verification_path', 'pass', 'Checked ' + record.citation + ' against ' + pathSources + '. Primary public URL is listed.', { checked: record.citation, against: pathSources, sourceUrl: record.sources[0].url }),
        humanReview('Even a passing check requires a person to confirm the pin cite, subsequent history, and that the proposition is not overstated before filing.')
      ]
    };
  }

  function mockVerify(text) {
    var trimmed = String(text || '').trim();
    var parsed = parseCitations(trimmed);
    var citations;
    if (!parsed.length) {
      citations = [{
        raw: trimmed || '(empty)',
        normalized: '',
        error: 'ambiguous',
        errorMessage: 'Ambiguous citation: no reporter citation could be parsed from this text. Paste a citation (for example, Carpenter v. United States, 585 U.S. 946 (2018)) or a paragraph that contains one.',
        proposition: trimmed,
        checks: [
          check('existence', 'fail', 'Nothing in the paste resolved to a case in the reporter set.', { checked: trimmed.slice(0, 280) || '(empty)', against: 'Public reporter set used by this demo' }),
          check('citation_format', 'fail', 'No volume / reporter / page pattern was found.', { checked: trimmed.slice(0, 280) || '(empty)', against: 'Bluebook-style citation' }),
          check('holding_support', 'fail', 'Holding support requires an identified opinion.', { checked: 'Pasted text', against: 'No opinion' }),
          check('verification_path', 'fail', 'Nothing was checked against a public source because no citation was found.', { checked: 'Pasted text', against: 'No source selected' }),
          humanReview('If you intended to verify a citation, add the full reporter form and run again.')
        ]
      }];
    } else {
      citations = parsed.map(function (item) {
        return evaluateParsed(item, trimmed);
      });
    }
    return {
      mode: 'mock',
      input: trimmed,
      citations: citations
    };
  }

  function apiBase() {
    var cfg = window.OWL_LEGAL_CONFIG || {};
    return cfg.API_BASE || '';
  }

  function tryLive(text) {
    var base = apiBase();
    if (!base) return Promise.reject(new Error('No API base'));
    var controller = typeof AbortController === 'function' ? new AbortController() : null;
    var timer = controller ? setTimeout(function () { controller.abort(); }, 4000) : null;
    return fetch(base.replace(/\/$/, '') + '/api/verify/citations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ text: text }),
      signal: controller ? controller.signal : undefined
    }).then(function (res) {
      if (timer) clearTimeout(timer);
      if (!res.ok) throw new Error('Live verify HTTP ' + res.status);
      return res.json();
    }).then(function (data) {
      if (!data || !Array.isArray(data.citations)) throw new Error('Live verify returned no citations array');
      data.mode = 'live';
      data.input = text;
      return data;
    });
  }

  function verify(text) {
    var trimmed = String(text || '').trim();
    return tryLive(trimmed).catch(function () {
      return new Promise(function (resolve) {
        window.setTimeout(function () {
          resolve(mockVerify(trimmed));
        }, 280);
      });
    });
  }

  window.OWLVerifyAPI = {
    CARPENTER_PREFILL: CARPENTER_PREFILL,
    FIXTURES: FIXTURES,
    CHECK_META: CHECK_META,
    verify: verify,
    mockVerify: mockVerify
  };
})(window);
