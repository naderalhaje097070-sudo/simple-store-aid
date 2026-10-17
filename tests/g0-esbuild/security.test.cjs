// Native servedir regression, only dummy files outside a disposable web root.
const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const http = require('node:http');
const esbuild = require(path.resolve(process.env.ESBUILD_ROOT || 'node_modules/esbuild'));
const out = path.resolve(process.env.ESBUILD_EVIDENCE || 'evidence/g0-esbuild');
const observations = [{ platform: process.platform, node: process.version, version: esbuild.version }];
let root, context, port;
const marker = 'outside-web-root-dummy-marker';
before(async () => {
  if (process.env.REQUIRE_NATIVE_WINDOWS === '1') assert.equal(process.platform, 'win32');
  root = fs.mkdtempSync(path.join(os.tmpdir(), 'g0-esbuild-'));
  const www = path.join(root, 'www'); fs.mkdirSync(www);
  fs.writeFileSync(path.join(root, 'sentinel.txt'), marker);
  fs.writeFileSync(path.join(www, 'benign.txt'), 'public-marker');
  fs.writeFileSync(path.join(root, 'app.js'), 'console.log("bundle-marker")');
  context = await esbuild.context({ entryPoints: [path.join(root, 'app.js')], bundle: true, outdir: www });
  ({ port } = await context.serve({ host: '127.0.0.1', port: 0, servedir: www }));
});
after(async () => {
  if (context) await context.dispose();
  if (root) fs.rmSync(root, { recursive: true, force: true });
  fs.mkdirSync(out, { recursive: true });
  fs.writeFileSync(path.join(out, 'security-observations.json'), JSON.stringify(observations, null, 2) + '\n');
});
function request(rawPath) {
  return new Promise((resolve, reject) => {
    const req = http.get({ host: '127.0.0.1', port, path: rawPath }, res => {
      let body = ''; res.setEncoding('utf8'); res.on('data', x => { body += x; });
      res.on('end', () => resolve({ status: res.statusCode, body }));
    });
    req.setTimeout(5000, () => req.destroy(Error('Request timeout'))); req.on('error', reject);
  });
}
test('benign servedir file remains available', async () => {
  const r = await request('/benign.txt'); assert.equal(r.status, 200); assert.equal(r.body, 'public-marker');
});
test('built entry remains available', async () => {
  const r = await request('/app.js'); assert.equal(r.status, 200); assert.match(r.body, /bundle-marker/);
});
test('missing public file is rejected', async () => { assert.equal((await request('/absent.txt')).status, 404); });
for (const [label, rawPath] of [['raw-backslash', '/..\\sentinel.txt'], ['encoded-backslash', '/%2e%2e%5csentinel.txt']]) {
  test('security-' + label + '-outside-root', async () => {
    const r = await request(rawPath); observations.push({ case: label, rawPath, ...r });
    assert.ok([400, 404].includes(r.status), JSON.stringify(r)); assert.ok(!r.body.includes(marker));
  });
}
