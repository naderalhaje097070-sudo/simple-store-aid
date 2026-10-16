// Read-only official npm inspection. Never installs or executes package code.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const semver = require(path.join(process.env.NPM_GLOBAL_ROOT, 'npm/node_modules/semver'));
const out = path.resolve(process.argv[2]);
fs.mkdirSync(out, { recursive: true });
const write = (name, data) => fs.writeFileSync(path.join(out, name), JSON.stringify(data, null, 2) + '\n');
const hash = (bytes, algorithm = 'sha256', encoding = 'hex') => crypto.createHash(algorithm).update(bytes).digest(encoding);
const requests = [];
async function get(url, name, limit = 32 * 1024 * 1024) {
  const u = new URL(url);
  if (u.protocol !== 'https:' || u.hostname !== 'registry.npmjs.org' || u.username || u.password) throw Error('Nonofficial URL rejected');
  const receipt = { url, name, started: new Date().toISOString() };
  requests.push(receipt);
  try {
    const response = await fetch(u, { redirect: 'error', signal: AbortSignal.timeout(45000), headers: { accept: 'application/json' } });
    receipt.status = response.status;
    receipt.headers = Object.fromEntries(['content-type', 'content-length', 'etag', 'last-modified'].map(k => [k, response.headers.get(k)]));
    if (Number(response.headers.get('content-length')) > limit) throw Error('Response too large');
    const chunks = []; let total = 0;
    for await (const chunk of response.body) {
      total += chunk.length;
      if (total > limit) throw Error('Response exceeds limit');
      chunks.push(chunk);
    }
    const bytes = Buffer.concat(chunks);
    fs.writeFileSync(path.join(out, name), bytes);
    Object.assign(receipt, { bytes: bytes.length, sha256: hash(bytes), finished: new Date().toISOString() });
    if (!response.ok) throw Error('Official HTTP ' + response.status);
    return bytes;
  } catch (error) {
    receipt.error = error.message;
    throw error;
  } finally { write('requests.json', requests); }
}
const metadata = async (name, file) => JSON.parse(await get('https://registry.npmjs.org/' + encodeURIComponent(name), file));
function manifestFields(m) {
  return Object.fromEntries(['name', 'version', 'engines', 'packageManager', 'dependencies', 'optionalDependencies', 'peerDependencies', 'peerDependenciesMeta', 'exports', 'bin', 'scripts', 'type', 'main', 'module', 'types'].map(k => [k, m[k] ?? null]));
}
async function archive(manifest, label) {
  if (!manifest.dist?.integrity?.startsWith('sha512-')) throw Error('Missing official SHA512 integrity');
  const bytes = await get(manifest.dist.tarball, label + '.tgz');
  const actual = 'sha512-' + hash(bytes, 'sha512', 'base64');
  const integrity = { version: manifest.version, url: manifest.dist.tarball, expected: manifest.dist.integrity, actual, matches: actual === manifest.dist.integrity, sha256: hash(bytes), bytes: bytes.length };
  write(label + '-integrity.json', integrity);
  if (!integrity.matches) throw Error(label + ' official integrity mismatch');
}
async function main() {
  write('identity.json', { task: 'G0-MCP-JS-COMPAT-01', source: process.env.SOURCE_SHA, run_id: process.env.DIAGNOSTIC_RUN_ID, run_attempt: process.env.DIAGNOSTIC_ATTEMPT, workflow: process.env.DIAGNOSTIC_WORKFLOW, node: process.version, platform: process.platform, arch: process.arch, semver: require(path.join(process.env.NPM_GLOBAL_ROOT, 'npm/node_modules/semver/package.json')).version, started: new Date().toISOString() });
  const mcp = await metadata('@lovable.dev/mcp-js', 'mcp-packument.json');
  const esbuild = await metadata('esbuild', 'esbuild-packument.json');
  const safeEsbuild = Object.keys(esbuild.versions).filter(v => semver.valid(v) && !semver.prerelease(v) && semver.gte(v, '0.28.1')).sort(semver.compare);
  if (!safeEsbuild.length) throw Error('No official patched stable esbuild observed');
  const versions = Object.keys(mcp.versions).filter(v => semver.valid(v) && !semver.prerelease(v) && semver.gt(v, '0.20.1')).sort(semver.compare);
  const table = versions.map(version => {
    const m = mcp.versions[version], range = m.dependencies?.esbuild ?? m.optionalDependencies?.esbuild ?? m.peerDependencies?.esbuild;
    return { version, published: mcp.time?.[version] ?? null, deprecated: m.deprecated ?? null, type: m.dependencies?.esbuild ? 'required' : m.optionalDependencies?.esbuild ? 'optional' : m.peerDependencies?.esbuild ? 'peer' : 'absent', range: range ?? null, fixed: range && semver.validRange(range) ? safeEsbuild.find(v => semver.satisfies(v, range)) ?? null : null };
  });
  write('all-stable-versions.json', table);
  // Do not silently skip an earlier qualifying deprecated version: expose it for review.
  const first = table.find(row => row.fixed);
  if (!first) { write('result.json', { status: 'NO_QUALIFYING_DECLARED_RANGE', versions_inspected: table.length }); return; }
  const baseline = mcp.versions['0.20.1'], candidate = mcp.versions[first.version];
  if (!baseline || candidate.name !== '@lovable.dev/mcp-js') throw Error('Unexpected official identity');
  write('baseline-metadata.json', baseline); write('candidate-metadata.json', candidate);
  write('comparison.json', { first, baseline: manifestFields(baseline), candidate: manifestFields(candidate), candidateAgeSeconds: first.published ? (Date.now() - Date.parse(first.published)) / 1000 : null, nodeCompatible: candidate.engines?.node ? semver.satisfies(process.version, candidate.engines.node) : null, preservedSdkAccepted: candidate.dependencies?.['@modelcontextprotocol/sdk'] ? semver.satisfies('1.31.0', candidate.dependencies['@modelcontextprotocol/sdk']) : null, esbuildFixed: manifestFields(esbuild.versions[first.fixed]), fixedEsbuildRangeAccepted: semver.satisfies(first.fixed, first.range) });
  const locked = JSON.parse(fs.readFileSync('bun.lock', 'utf8').replace(/,\s*([}\]])/g, '$1'));
  const current = Object.entries(locked.packages).flatMap(([record, value]) => ['dependencies', 'optionalDependencies', 'peerDependencies'].flatMap(type => value[2]?.[type]?.esbuild ? [{ record, parent: value[0], type, range: value[2][type].esbuild, acceptsFixed: semver.satisfies(first.fixed, value[2][type].esbuild) }] : []));
  write('current-esbuild-edges.json', { consumers: current, esbuildRecords: Object.entries(locked.packages).filter(([, v]) => v[0].startsWith('esbuild@')).map(([record, v]) => ({ record, identity: v[0] })), note: 'Current graph only; no candidate graph generated or installed.' });
  await archive(baseline, 'baseline'); await archive(candidate, 'candidate');
  for (const [name, version, label] of [['@modelcontextprotocol/sdk', '1.31.0', 'preserved-sdk'], ['hono', '4.13.7', 'preserved-hono'], ['@hono/node-server', '1.19.15', 'preserved-node-server']]) {
    const doc = JSON.parse(await get('https://registry.npmjs.org/' + encodeURIComponent(name) + '/' + version, label + '-metadata.json'));
    if (doc.name !== name || doc.version !== version) throw Error('Preserved dependency identity mismatch');
  }
  write('result.json', { status: 'STATIC_INSPECTION_READY', first, versions_inspected: table.length, baseline: baseline.version, candidate: candidate.version, installed: false, scriptsExecuted: false, candidateGraphGenerated: false });
  console.log(JSON.stringify({ task: 'G0-MCP-JS-COMPAT-01', first, versions_inspected: table.length, artifact: 'g0-mcp-js-official-inspection' }));
}
main().catch(error => { write('failure.json', { message: error.message, at: new Date().toISOString() }); console.error(error.message); process.exitCode = 1; });
