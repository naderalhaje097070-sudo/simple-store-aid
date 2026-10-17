// Official pinned archives only. Inspection never executes MCP package scripts.
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const out = path.resolve('evidence/g0-esbuild');
fs.mkdirSync(out, { recursive: true });
const save = (n, v) => fs.writeFileSync(path.join(out, n), JSON.stringify(v, null, 2) + '\n');
const receipts = [];
async function get(url, name) {
  const u = new URL(url);
  if (u.protocol !== 'https:' || u.hostname !== 'registry.npmjs.org' || u.username || u.password) throw Error('Nonofficial URL');
  const r = await fetch(u, { redirect: 'error', signal: AbortSignal.timeout(45000) });
  const chunks = []; let size = 0;
  for await (const c of r.body) { size += c.length; if (size > 32 * 1024 * 1024) throw Error('Size cap'); chunks.push(c); }
  const bytes = Buffer.concat(chunks);
  fs.writeFileSync(path.join(out, name), bytes);
  receipts.push({ url, name, status: r.status, bytes: size, sha256: crypto.createHash('sha256').update(bytes).digest('hex'), at: new Date().toISOString() });
  save('requests.json', receipts);
  if (!r.ok) throw Error('HTTP ' + r.status);
  return bytes;
}
async function main() {
  save('identity.json', { source: process.env.GITHUB_SHA, run_id: process.env.GITHUB_RUN_ID, attempt: process.env.GITHUB_RUN_ATTEMPT, workflow: process.env.GITHUB_WORKFLOW_REF, node: process.version, platform: process.platform });
  for (const [name, version, label, pinned] of [
    ['@lovable.dev/mcp-js', '0.20.1', 'baseline', 'sha512-om6CeutH0umP7WJLNqO7HnBYBnPje6iqQbSrE4PTFiWu0XhwC4BbEC6j0AmhiZWDV00Fu1TVidXCnAn45KVw2A=='],
    ['esbuild', '0.28.1', 'patched-esbuild', 'sha512-HrJrvZv5ayxBzPfwphOoNzkzOIIlifzk0KJrGK2c8R4+LKpMtpYLQeUdjnwjWv/LZlkH2laZk+4w78pi99D4Vw=='],
  ]) {
    const m = JSON.parse(await get('https://registry.npmjs.org/' + encodeURIComponent(name) + '/' + version, label + '-metadata.json'));
    if (m.name !== name || m.version !== version || m.dist.integrity !== pinned) throw Error('Pinned official identity mismatch');
    const bytes = await get(m.dist.tarball, label + '.tgz');
    const actual = 'sha512-' + crypto.createHash('sha512').update(bytes).digest('base64');
    save(label + '-integrity.json', { expected: pinned, actual, matches: actual === pinned });
    if (actual !== pinned) throw Error('Archive integrity mismatch');
  }
}
main().catch(e => { save('failure.json', { message: e.message }); console.error(e); process.exitCode = 1; });
