/**
 * Node unit for the /verify workspace renderer against a saved Riley fixture.
 * Run: node tests/test_verify_workspace_render.js
 */
'use strict';

var fs = require('fs');
var path = require('path');
var vm = require('vm');

var failed = 0;
function ok(name) { console.log('ok - ' + name); }
function fail(name, err) {
  failed += 1;
  console.error('not ok - ' + name + ': ' + (err && err.message ? err.message : err));
}

var repoRoot = path.resolve(__dirname, '..', '..');
var workspaceSrc = fs.readFileSync(path.join(repoRoot, 'assets', 'js', 'verify-workspace.js'), 'utf8');
var apiSrc = fs.readFileSync(path.join(repoRoot, 'assets', 'js', 'verify-api.js'), 'utf8');
var fixture = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'fixtures', 'riley-verify-payload.json'), 'utf8')
);

try {
  new Function(workspaceSrc);
  ok('verify-workspace.js parses');
} catch (err) {
  fail('verify-workspace.js parses', err);
}

var elements = {};
function makeEl(id) {
  if (!elements[id]) {
    elements[id] = {
      id: id,
      hidden: true,
      innerHTML: '',
      textContent: '',
      addEventListener: function () {},
      contains: function () { return false; }
    };
  }
  return elements[id];
}

var sandboxWindow = {
  matchMedia: function () { return { matches: false }; }
};
var sandboxDocument = {
  getElementById: function (id) { return makeEl(id); }
};
sandboxWindow.document = sandboxDocument;

var context = {
  window: sandboxWindow,
  document: sandboxDocument,
  fetch: function () { return Promise.reject(new Error('offline test')); },
  console: console,
  URL: { createObjectURL: function () { return ''; }, revokeObjectURL: function () {} },
  Blob: function () {}
};
context.global = context;
context.window.OWL_LEGAL_CONFIG = { API_BASE: '' };

try {
  vm.runInNewContext(apiSrc + '\n' + workspaceSrc, context);
  if (!sandboxWindow.OWLVerifyAPI) throw new Error('OWLVerifyAPI missing');
  if (!sandboxWindow.OWLVerifyWorkspace) throw new Error('OWLVerifyWorkspace missing');
  ok('workspace IIFE boots with mocked DOM');
} catch (err) {
  fail('workspace IIFE boots with mocked DOM', err);
  process.exit(1);
}

var rendered;
try {
  rendered = sandboxWindow.OWLVerifyWorkspace.render(fixture);
  if (!rendered) throw new Error('render returned false');
  ok('Riley fixture render() returns true');
} catch (err) {
  fail('Riley fixture render() returns true', err);
}

function assertContains(name, haystack, needle) {
  if (String(haystack || '').indexOf(needle) === -1) {
    fail(name, new Error('missing ' + JSON.stringify(needle)));
  } else {
    ok(name);
  }
}

var excerptHtml = makeEl('verify-excerpt').innerHTML;
assertContains('excerpt highlights Riley', excerptHtml, 'Riley v. California, 573 U.S. 373 (2014)');
assertContains('excerpt uses cite buttons', excerptHtml, 'data-cite-id=');
assertContains('five-check panel present', makeEl('verify-cite-detail').innerHTML, 'verify-checks');
assertContains('TOA lists Riley', makeEl('verify-toa').innerHTML, 'Riley v. California');
assertContains('source chips present', makeEl('verify-source-chips').innerHTML, 'Cornell LII');
assertContains('human-review queue lists Wurie', makeEl('verify-queue').innerHTML, 'Wurie');
assertContains('source list is labeled Sources checked', makeEl('verify-cite-detail').innerHTML, 'Sources checked');
assertContains('Wurie open-source control is present', makeEl('verify-cite-detail').innerHTML, 'Open source');
assertContains('copy cite control is present', makeEl('verify-cite-detail').innerHTML, 'Copy cite');
assertContains('authority links open in a new tab', makeEl('verify-cite-detail').innerHTML, 'target="_blank"');
assertContains('Wurie links to a CourtListener opinion page', makeEl('verify-cite-detail').innerHTML, '/opinion/870435/united-states-v-wurie/');
assertContains('TOA includes an Open control', makeEl('verify-toa').innerHTML, 'verify-toa-open');

var messy = JSON.parse(JSON.stringify(fixture));
messy.citations.push({ id: 'broken-row', raw: 'Broken v. Cite, 1 U.S. 1 (1800)' });
messy.citations.push(null);
try {
  if (!sandboxWindow.OWLVerifyWorkspace.render(messy)) {
    throw new Error('render returned false on extra malformed row');
  }
  ok('malformed extra citation does not fail the workspace');
} catch (err) {
  fail('malformed extra citation does not fail the workspace', err);
}

if (failed) {
  console.error(failed + ' failed');
  process.exit(1);
}
console.log('all passed');
