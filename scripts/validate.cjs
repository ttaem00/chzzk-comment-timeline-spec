// Static documentation checks; optional parser conformance uses an explicit local module.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const fixtures = JSON.parse(fs.readFileSync(path.join(root, 'examples/fixtures.json'), 'utf8'));
const naturalFixtures = JSON.parse(fs.readFileSync(path.join(root, 'examples/natural-hierarchy.json'), 'utf8'));
const cases = [...fixtures.cases, ...naturalFixtures.cases];
const ids = new Set();
for (const item of cases) {
  assert.ok(item.id && !ids.has(item.id)); ids.add(item.id);
  assert.ok(item.documents.length && item.documents.every(d => typeof d.raw === 'string'));
  assert.equal(item.expected.starts.length, item.expected.ends.length);
  for (const key of ['roles', 'depths', 'parents']) {
    if (item.expected[key]) assert.equal(item.expected[key].length, item.expected.starts.length);
  }
}
for (const name of ['README.md', 'SPEC.md', 'SUPPORT.md', 'VALIDATION.md', 'CONTRIBUTING.md']) {
  const text = fs.readFileSync(path.join(root, name), 'utf8');
  assert.equal((text.match(/^```/gm) || []).length % 2, 0, `unclosed code fence in ${name}`);
  for (const [, target] of text.matchAll(/\]\(([^)]+)\)/g)) {
    if (/^https?:/.test(target)) continue;
    assert.ok(fs.existsSync(path.resolve(root, target.split('#')[0])), `missing link ${target}`);
  }
}
console.log(`Static documentation PASS; ${cases.length} synthetic cases`);
const index = process.argv.indexOf('--parser');
if (index >= 0) {
  assert.ok(process.argv[index + 1], 'provide an explicit local parser module');
  const parser = require(path.resolve(process.argv[index + 1]));
  for (const item of cases) {
    const result = parser.parseCompatibleComments(item.documents, {durationSec:36000, ...(item.context || {})});
    assert.deepEqual(result.entries.map(e=>e.startSec), item.expected.starts, item.id);
    assert.deepEqual(result.entries.map(e=>e.geometry==='interval'?e.resolvedEndSec:null), item.expected.ends, item.id);
    if (item.expected.diagnostics) assert.deepEqual(result.diagnostics.map(d=>d.code), item.expected.diagnostics, item.id);
    if (item.expected.untimed) assert.deepEqual(result.documents.flatMap(d=>d.untimedBlocks.map(b=>b.raw)), item.expected.untimed, item.id);
    if (item.expected.roles) assert.deepEqual(result.entries.map(e=>e.role), item.expected.roles, item.id);
    if (item.expected.depths) assert.deepEqual(result.entries.map(e=>e.depth), item.expected.depths, item.id);
    if (item.expected.parents) assert.deepEqual(result.entries.map(e=>result.entries.findIndex(p=>p.entryId===e.parentId)), item.expected.parents, item.id);
    for (const doc of result.documents) assert.equal(doc.raw, item.documents[result.documents.indexOf(doc)].raw, item.id);
  }
  console.log(`Parser conformance PASS; ${cases.length} synthetic cases; ${parser.version}`);
}
