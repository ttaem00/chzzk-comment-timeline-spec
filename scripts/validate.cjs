// Static documentation checks; optional parser conformance uses an explicit local module.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const fixtures = JSON.parse(fs.readFileSync(path.join(root, 'examples/fixtures.json'), 'utf8'));
const ids = new Set();
for (const item of fixtures.cases) {
  assert.ok(item.id && !ids.has(item.id)); ids.add(item.id);
  assert.ok(item.documents.length && item.documents.every(d => typeof d.raw === 'string'));
  assert.equal(item.expected.starts.length, item.expected.ends.length);
}
for (const name of ['README.md', 'SPEC.md', 'SUPPORT.md', 'VALIDATION.md', 'CONTRIBUTING.md']) {
  const text = fs.readFileSync(path.join(root, name), 'utf8');
  assert.equal((text.match(/^```/gm) || []).length % 2, 0, `unclosed code fence in ${name}`);
  for (const [, target] of text.matchAll(/\]\(([^)]+)\)/g)) {
    if (/^https?:/.test(target)) continue;
    assert.ok(fs.existsSync(path.resolve(root, target.split('#')[0])), `missing link ${target}`);
  }
}
console.log(`Static documentation PASS; ${fixtures.cases.length} synthetic cases`);
const index = process.argv.indexOf('--parser');
if (index >= 0) {
  assert.ok(process.argv[index + 1], 'provide an explicit local parser module');
  const parser = require(path.resolve(process.argv[index + 1]));
  for (const item of fixtures.cases) {
    const result = parser.parseCompatibleComments(item.documents, {durationSec:36000, ...(item.context || {})});
    assert.deepEqual(result.entries.map(e=>e.startSec), item.expected.starts, item.id);
    assert.deepEqual(result.entries.map(e=>e.geometry==='interval'?e.resolvedEndSec:null), item.expected.ends, item.id);
    assert.deepEqual(result.diagnostics.map(d=>d.code), item.expected.diagnostics, item.id);
    assert.deepEqual(result.documents.flatMap(d=>d.untimedBlocks.map(b=>b.raw)), item.expected.untimed, item.id);
  }
  console.log(`Parser conformance PASS; ${fixtures.cases.length} synthetic cases; ${parser.version}`);
}
