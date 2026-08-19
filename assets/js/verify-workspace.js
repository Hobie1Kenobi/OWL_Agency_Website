/**
 * /verify interactive workspace: excerpt highlights, five-check panel,
 * Table of Authorities, human-review queue, and downloadable HTML artifacts.
 */
(function (window, document) {
  'use strict';

  var api = window.OWLVerifyAPI;
  var root = document.getElementById('verify-workspace');
  var state = { payload: null, selectedId: null };

  if (!root || !api) return;

  function escapeHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function asArray(value) {
    if (Array.isArray(value)) return value;
    if (value == null || value === '') return [];
    if (typeof value === 'object') {
      if (Array.isArray(value.groups)) return value.groups;
      if (Array.isArray(value.entries)) return [value];
      return Object.keys(value).map(function (key) { return value[key]; });
    }
    return [];
  }

  function asCheck(check) {
    if (check && typeof check === 'object') return check;
    return {
      id: 'unknown',
      label: 'Check',
      status: 'needs-review',
      detail: check == null ? 'This check was malformed and needs human review.' : String(check),
      checked: '',
      against: '',
      sourceUrl: null
    };
  }

  function statusLabel(status) {
    if (status === 'pass' || status === 'ok') return 'Pass';
    if (status === 'fail') return 'Fail';
    if (status === 'timeout') return 'Timed out';
    if (status === 'blocked') return 'Blocked';
    if (status === 'no_match') return 'No match';
    if (status === 'error') return 'Error';
    return 'Needs review';
  }

  function renderSourceChips(sources) {
    var list = asArray(sources);
    if (!list.length) {
      return '<p class="small text-muted mb-0">No source-family status was returned for this run.</p>';
    }
    return (
      '<ul class="verify-source-chips">' +
        list.map(function (source) {
          if (!source || typeof source !== 'object') {
            return '<li class="verify-chip is-down"><span>Unknown source</span><span class="verify-chip-status">Needs review</span></li>';
          }
          var cls = source.status === 'ok' ? 'is-ok' : 'is-down';
          var extra = source.http_status
            ? ' HTTP ' + source.http_status
            : (source.error ? ' ' + source.error : '');
          return (
            '<li class="verify-chip ' + cls + '">' +
              '<span>' + escapeHtml(source.name || source.id) + '</span>' +
              '<span class="verify-chip-status">' + escapeHtml(statusLabel(source.status)) + extra + '</span>' +
            '</li>'
          );
        }).join('') +
      '</ul>'
    );
  }

  function citationById(id) {
    var list = asArray(state.payload && state.payload.citations);
    for (var i = 0; i < list.length; i++) {
      if (list[i] && list[i].id === id) return list[i];
    }
    return null;
  }

  function errorBanner(citation) {
    if (!citation.error) return '';
    var titles = {
      not_found: 'Citation not found',
      ambiguous: 'Ambiguous citation',
      source_unavailable: 'Source unavailable'
    };
    return (
      '<div class="verify-error" role="alert">' +
        '<strong>' + escapeHtml(titles[citation.error] || citation.error) + '.</strong> ' +
        escapeHtml(citation.errorMessage || 'This check did not pass silently.') +
      '</div>'
    );
  }

  function highlightExcerpt(excerpt, citations) {
    var text = excerpt || '';
    var hits = [];
    asArray(citations).forEach(function (citation) {
      if (!citation || typeof citation !== 'object') return;
      var candidates = [citation.normalized, citation.raw, citation.span].filter(Boolean);
      candidates.sort(function (a, b) { return a.length - b.length; });
      var span = '';
      var start = -1;
      for (var i = 0; i < candidates.length; i++) {
        start = text.indexOf(candidates[i]);
        if (start !== -1) {
          span = candidates[i];
          break;
        }
      }
      if (start === -1 || !span || !citation.id) return;
      hits.push({ start: start, end: start + span.length, citation: citation });
    });
    hits.sort(function (a, b) { return a.start - b.start; });
    var parts = [];
    var cursor = 0;
    hits.forEach(function (hit) {
      if (hit.start < cursor) return;
      if (hit.start > cursor) {
        parts.push(escapeHtml(text.slice(cursor, hit.start)));
      }
      var overall = api.overallStatus(hit.citation);
      var selected = hit.citation.id === state.selectedId;
      parts.push(
        '<button type="button" class="verify-cite is-' + escapeHtml(overall) +
          (selected ? ' is-selected' : '') +
          '" data-cite-id="' + escapeHtml(hit.citation.id) + '"' +
          ' aria-pressed="' + (selected ? 'true' : 'false') + '">' +
          escapeHtml(text.slice(hit.start, hit.end)) +
        '</button>'
      );
      cursor = hit.end;
    });
    if (cursor < text.length) parts.push(escapeHtml(text.slice(cursor)));
    return parts.join('').replace(/\n/g, '<br/>');
  }

  function renderCheck(check) {
    check = asCheck(check);
    var path = '';
    if (check.checked || check.against) {
      path =
        '<p class="verify-path"><span>Checked:</span> ' + escapeHtml(check.checked || '—') +
        '<br/><span>Against:</span> ' + escapeHtml(check.against || '—') + '</p>';
    }
    var link = check.sourceUrl
      ? '<p class="verify-source"><a href="' + escapeHtml(check.sourceUrl) + '" rel="noopener noreferrer">Open public source</a></p>'
      : '';
    return (
      '<li class="verify-check is-' + escapeHtml(check.status) + '">' +
        '<div class="verify-check-head">' +
          '<h3>' + escapeHtml(check.label) + '</h3>' +
          '<span class="verify-pill">' + escapeHtml(statusLabel(check.status)) + '</span>' +
        '</div>' +
        '<p>' + escapeHtml(check.detail) + '</p>' +
        path +
        link +
      '</li>'
    );
  }

  function renderPathSteps(citation) {
    var steps = asArray(citation && citation.verification_path);
    if (!steps.length) {
      return '<p class="small text-muted mb-0">No verification-path steps were recorded for this cite.</p>';
    }
    return (
      '<ol class="verify-path-steps">' +
        steps.map(function (step) {
          if (!step || typeof step !== 'object') {
            return '<li><span>' + escapeHtml(step) + '</span></li>';
          }
          var source = step.url
            ? '<a href="' + escapeHtml(step.url) + '" rel="noopener noreferrer">' + escapeHtml(step.source || 'Public source') + '</a>'
            : escapeHtml(step.source || 'Public source');
          return (
            '<li>' +
              '<strong>' + source + '</strong>' +
              '<span>' + escapeHtml(step.what || '') + '</span>' +
            '</li>'
          );
        }).join('') +
      '</ol>'
    );
  }

  function renderDetail(citation) {
    if (!citation) {
      return '<p class="text-muted mb-0">Select a highlighted citation in the excerpt, or a row in the Table of Authorities.</p>';
    }
    var heading = citation.normalized || citation.raw || 'Citation';
    var meta = [];
    if (citation.court) meta.push(escapeHtml(citation.court));
    if (citation.year) meta.push(escapeHtml(String(citation.year)));
    var overall = api.overallStatus(citation);
    return (
      '<article class="verify-card mb-0" aria-labelledby="selected-cite-heading">' +
        '<div class="verify-check-head">' +
          '<h3 id="selected-cite-heading">' + escapeHtml(heading) + '</h3>' +
          '<span class="verify-pill">' + escapeHtml(statusLabel(overall)) + '</span>' +
        '</div>' +
        (meta.length ? '<p class="verify-raw">' + meta.join(' · ') + '</p>' : '') +
        (citation.proposition ? '<p class="verify-proposition"><span>Proposition checked:</span> ' + escapeHtml(citation.proposition) + '</p>' : '') +
        errorBanner(citation) +
        '<ol class="verify-checks">' + asArray(citation.checks).map(renderCheck).join('') + '</ol>' +
        '<details class="verify-path-panel mt-3"' + (overall === 'fail' ? ' open' : '') + '>' +
          '<summary>Verification path</summary>' +
          renderPathSteps(citation) +
          '<p class="small text-muted mt-2 mb-0">Public sources are listed as what was checked against. OWL is not a citator product.</p>' +
        '</details>' +
      '</article>'
    );
  }

  function renderToa(payload) {
    var groups = asArray(payload && payload.toa);
    if (!groups.length) {
      return '<p class="text-muted mb-0">No Table of Authorities could be built from this result set.</p>';
    }
    return groups.map(function (group) {
      if (!group || typeof group !== 'object') return '';
      var rows = asArray(group.entries).map(function (entry) {
        if (!entry || typeof entry !== 'object') return '';
        var selected = entry.citationId === state.selectedId;
        return (
          '<tr class="' + (selected ? 'is-selected' : '') + '">' +
            '<td>' +
              '<button type="button" class="verify-toa-link" data-cite-id="' + escapeHtml(entry.citationId) + '">' +
                escapeHtml(entry.cite || 'Citation') +
              '</button>' +
            '</td>' +
            '<td>' + escapeHtml(entry.court || '—') + '</td>' +
            '<td>' + escapeHtml(entry.year ? String(entry.year) : '—') + '</td>' +
            '<td><span class="verify-pill">' + escapeHtml(statusLabel(entry.overall || 'needs-review')) + '</span></td>' +
          '</tr>'
        );
      }).join('');
      return (
        '<div class="verify-toa-group">' +
          '<h3 class="h6">' + escapeHtml(group.label) + '</h3>' +
          '<div class="table-responsive">' +
            '<table class="table table-sm verify-toa-table">' +
              '<thead><tr><th>Authority</th><th>Court</th><th>Year</th><th>Status</th></tr></thead>' +
              '<tbody>' + rows + '</tbody>' +
            '</table>' +
          '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderQueue(payload) {
    var flagged = asArray(payload && payload.citations).filter(function (citation) {
      return citation && typeof citation === 'object' && api.isFlagged(citation);
    });
    if (!flagged.length) {
      return '<p class="mb-0">No existence, format, holding-support, or source failures in this SAMPLE. A person still reviews every cite before filing — the human-review flag remains on each card.</p>';
    }
    return (
      '<p class="small text-muted mb-0">These are the cites a person should review before filing: fails and holding/source issues. Human must review before filing. OWL is not a paralegal replacement.</p>' +
      '<ul class="verify-queue-list">' +
        flagged.map(function (citation) {
          var overall = api.overallStatus(citation);
          var selected = citation.id === state.selectedId;
          return (
            '<li>' +
              '<button type="button" class="verify-queue-item is-' + escapeHtml(overall) +
                (selected ? ' is-selected' : '') +
                '" data-cite-id="' + escapeHtml(citation.id) + '">' +
                '<span class="verify-pill">' + escapeHtml(statusLabel(overall)) + '</span>' +
                '<span>' + escapeHtml(citation.normalized || citation.raw || 'Citation') + '</span>' +
              '</button>' +
            '</li>'
          );
        }).join('') +
      '</ul>'
    );
  }

  function reportDate() {
    try {
      return new Date().toISOString().slice(0, 10);
    } catch (err) {
      return '';
    }
  }

  function artifactShell(title, bodyHtml) {
    var matter = (state.payload && state.payload.matter) || {};
    var name = matter.matter_name || matter.title || 'Pasted citation check';
    return (
      '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>' +
      '<meta name="viewport" content="width=device-width, initial-scale=1"/>' +
      '<title>' + escapeHtml(title) + '</title>' +
      '<style>' +
        'body{font-family:Georgia,Times,serif;max-width:800px;margin:2rem auto;padding:0 1.25rem;color:#222;line-height:1.5}' +
        'h1,h2,h3{font-family:"Jost",Georgia,sans-serif;color:#37517e}' +
        '.banner{border:1px solid #c58b00;background:#fff9ec;padding:.75rem 1rem;margin:1rem 0}' +
        '.cite{border:1px solid #e6ebf2;padding:1rem;margin:1rem 0}' +
        '.pass{border-left:5px solid #198754}.fail{border-left:5px solid #dc3545}.review{border-left:5px solid #c58b00}' +
        'table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #ddd;padding:.4rem .35rem;text-align:left;vertical-align:top}' +
        'footer{margin-top:2rem;font-size:.9rem;color:#444}' +
      '</style></head><body>' +
      '<p><strong>SAMPLE</strong> — Not a real filing. OWL AI Agency citation verification.</p>' +
      '<h1>' + escapeHtml(title) + '</h1>' +
      '<p>Date: ' + escapeHtml(reportDate()) + '<br/>Matter: ' + escapeHtml(name) + '</p>' +
      (matter.warning_banner ? '<div class="banner">' + escapeHtml(matter.warning_banner) + '</div>' : '') +
      bodyHtml +
      '<footer>' +
        '<p>OWL is a verification tool, not legal advice, and does not create an attorney-client relationship. Human review of all outputs is required. Public sources (CourtListener, SCOTUS, GovInfo, Justia, Cornell LII) are listed as what was checked against. OWL is not a citator product and does not replace a lawyer, a paralegal, or Westlaw/Lexis.</p>' +
        '<p>OWL AI Agency · Ingleside, TX 78362 · <a href="tel:+19857901830">(985) 790-1830</a> · <a href="mailto:hobiecunningham@owl-ai-agency.com">hobiecunningham@owl-ai-agency.com</a></p>' +
      '</footer></body></html>'
    );
  }

  function checkRows(citation) {
    return asArray(citation && citation.checks).map(function (check) {
      check = asCheck(check);
      return (
        '<tr>' +
          '<td>' + escapeHtml(check.label) + '</td>' +
          '<td>' + escapeHtml(statusLabel(check.status)) + '</td>' +
          '<td>' + escapeHtml(check.detail) + '</td>' +
        '</tr>'
      );
    }).join('');
  }

  function buildReportHtml(payload) {
    var blocks = asArray(payload.citations).map(function (citation) {
      if (!citation || typeof citation !== 'object') return '';
      var overall = api.overallStatus(citation);
      var cls = overall === 'pass' ? 'pass' : overall === 'fail' ? 'fail' : 'review';
      return (
        '<section class="cite ' + cls + '">' +
          '<h2>' + escapeHtml(citation.normalized || citation.raw) + '</h2>' +
          (citation.proposition ? '<p><em>Proposition:</em> ' + escapeHtml(citation.proposition) + '</p>' : '') +
          (citation.errorMessage ? '<p><strong>' + escapeHtml(citation.errorMessage) + '</strong></p>' : '') +
          '<table><thead><tr><th>Check</th><th>Result</th><th>Detail</th></tr></thead><tbody>' +
          checkRows(citation) +
          '</tbody></table>' +
        '</section>'
      );
    }).join('');
    return artifactShell('Citation Verification Report — SAMPLE', blocks);
  }

  function buildFlaggedHtml(payload) {
    var flagged = asArray(payload.citations).filter(function (citation) {
      return citation && typeof citation === 'object' && api.isFlagged(citation);
    });
    var body;
    if (!flagged.length) {
      body = '<p>No flagged authorities in this SAMPLE beyond the standing instruction that a person reviews every cite before filing.</p>';
    } else {
      body =
        '<p><strong>Human must review before filing.</strong> This memorandum lists only citations that failed or need review on existence, citation format, holding support, or verification path.</p>' +
        flagged.map(function (citation) {
          var overall = api.overallStatus(citation);
          var cls = overall === 'fail' ? 'fail' : 'review';
          return (
            '<section class="cite ' + cls + '">' +
              '<h2>' + escapeHtml(citation.normalized || citation.raw) + '</h2>' +
              '<p>Overall: ' + escapeHtml(statusLabel(overall)) + '</p>' +
              (citation.proposition ? '<p><em>Proposition:</em> ' + escapeHtml(citation.proposition) + '</p>' : '') +
              (citation.errorMessage ? '<p><strong>' + escapeHtml(citation.errorMessage) + '</strong></p>' : '') +
              '<table><thead><tr><th>Check</th><th>Result</th><th>Detail</th></tr></thead><tbody>' +
              checkRows(citation) +
              '</tbody></table>' +
            '</section>'
          );
        }).join('');
    }
    return artifactShell('Flagged Authorities Memorandum — SAMPLE', body);
  }

  function downloadHtml(filename, html) {
    var blob = new Blob([html], { type: 'text/html;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function paint() {
    var payload = state.payload;
    if (!payload) return;
    var banner = document.getElementById('verify-matter-banner');
    var excerptEl = document.getElementById('verify-excerpt');
    var detailEl = document.getElementById('verify-cite-detail');
    var toaEl = document.getElementById('verify-toa');
    var queueEl = document.getElementById('verify-queue');
    var modeEl = document.getElementById('verify-mode-note');
    if (modeEl) {
      if (payload.mode === 'live') {
        modeEl.textContent = 'Live verification against public sources. Failures below are from this run, not a canned demo file.';
      } else if (payload.mode === 'offline-preview') {
        modeEl.innerHTML = '<strong>Offline sample preview</strong> — not a live source check. Public databases were not queried.';
      } else {
        modeEl.textContent = 'Verification result. Confirm the mode above before relying on these checks.';
      }
    }
    var chipsEl = document.getElementById('verify-source-chips');
    if (chipsEl) {
      chipsEl.innerHTML = renderSourceChips(payload.sources_queried);
    }
    if (banner) {
      if (payload.matter && payload.matter.warning_banner) {
        banner.hidden = false;
        banner.textContent = payload.matter.warning_banner;
      } else {
        banner.hidden = true;
        banner.textContent = '';
      }
    }
    if (excerptEl) {
      excerptEl.innerHTML = highlightExcerpt(payload.excerpt || payload.input || '', payload.citations);
    }
    if (detailEl) {
      detailEl.innerHTML = renderDetail(citationById(state.selectedId));
    }
    if (toaEl) toaEl.innerHTML = renderToa(payload);
    if (queueEl) queueEl.innerHTML = renderQueue(payload);
  }

  function selectCite(id, scrollDetail) {
    if (!citationById(id)) return;
    state.selectedId = id;
    paint();
    if (scrollDetail && window.matchMedia && window.matchMedia('(max-width: 991.98px)').matches) {
      var detailEl = document.getElementById('verify-cite-detail');
      if (detailEl) detailEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function defaultSelected(payload) {
    if (payload.matter && payload.matter.default_selected && citationById(payload.matter.default_selected)) {
      return payload.matter.default_selected;
    }
    var flagged = asArray(payload.citations).filter(function (citation) {
      return citation && typeof citation === 'object' && api.isFlagged(citation);
    });
    if (flagged.length) return flagged[0].id;
    var first = asArray(payload.citations)[0];
    return first && first.id ? first.id : null;
  }

  function render(payload) {
    try {
      state.payload = payload;
      state.selectedId = null;
      if (!payload || !asArray(payload.citations).length) {
        root.hidden = true;
        return false;
      }
      root.hidden = false;
      state.selectedId = defaultSelected(payload);
      paint();
      return true;
    } catch (err) {
      try {
        root.hidden = true;
      } catch (hideErr) {}
      return false;
    }
  }

  root.addEventListener('click', function (event) {
    var button = event.target.closest('[data-cite-id]');
    if (!button || !root.contains(button)) return;
    selectCite(button.getAttribute('data-cite-id'), true);
  });

  var reportBtn = document.getElementById('verify-download-report');
  var flaggedBtn = document.getElementById('verify-download-flagged');
  if (reportBtn) {
    reportBtn.addEventListener('click', function () {
      if (!state.payload) return;
      downloadHtml('owl-citation-verification-report-sample.html', buildReportHtml(state.payload));
    });
  }
  if (flaggedBtn) {
    flaggedBtn.addEventListener('click', function () {
      if (!state.payload) return;
      downloadHtml('owl-flagged-authorities-memorandum-sample.html', buildFlaggedHtml(state.payload));
    });
  }

  window.OWLVerifyWorkspace = {
    render: render,
    selectCite: selectCite
  };
})(window, document);
