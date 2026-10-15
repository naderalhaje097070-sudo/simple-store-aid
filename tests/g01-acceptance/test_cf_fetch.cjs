// Exercise actual installed vendor functions offline, before credentials exist.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const path = '/tmp/g01-tools/node_modules/miniflare/dist/src/index.js';
const source = fs.readFileSync(path, 'utf8');
const names = ['isCfFetchDisabledByEnv', 'getCfPathFromEnv', 'getCfOptionWithEnvOverride', 'setupCf'];
// These pinned bundled functions have no nested template literal braces. Refuse a changed shape.
const functions = names.map(name => {
  const match = new RegExp('(?:async )?function ' + name + '\\([^)]*\\) \\{').exec(source);
  assert.ok(match, 'missing pinned function ' + name);
  let depth = 1, end = match.index + match[0].length;
  for (; end < source.length && depth; end++) {
    if (source[end] === '{') depth++;
    if (source[end] === '}') depth--;
  }
  assert.equal(depth, 0);
  return source.slice(match.index, end);
});
async function run(setting, explicitCf) {
  let reads = 0, fetches = 0;
  const fallback = Object.freeze({fixture: 'vendor-fallback-identity'});
  const env = setting === undefined ? {} : {CLOUDFLARE_CF_FETCH_ENABLED: setting};
  const readFile = async () => { reads++; throw new Error('absent fixture cache'); };
  const fetch = async () => { fetches++; throw new Error('offline network trap'); };
  const globals = {process: {env}, fallbackCf: fallback,
    CF_FETCH_ENABLED_ENV_VAR: 'CLOUDFLARE_CF_FETCH_ENABLED',
    CF_FETCH_PATH_ENV_VAR: 'CLOUDFLARE_CF_FETCH_PATH',
    getDefaultCfPath: () => '/offline-absent-cache',
    defaultCfFetchEndpoint: 'https://workers.cloudflare.com/cf.json', readFile, fetch,
    AbortSignal, dim: x => x,
  };
  // esbuild names imported module namespaces; provide only the offline methods used here.
  for (const [, module, method] of functions.join('\n').matchAll(/\b(import_[\w$]+)\.(readFile|fetch|dim)\b/g)) {
    (globals[module] ??= {})[method] = {readFile, fetch, dim: x => x}[method];
  }
  // The installed bundle renames bundled imports (observed dim2). Keep vendor code intact.
  for (const [, name, method] of functions.join('\n').matchAll(/\b((readFile|fetch|dim)\d*)\s*\(/g)) {
    globals[name] = {readFile, fetch, dim: x => x}[method];
  }
  const context = vm.createContext(globals);
  vm.runInContext(functions.join('\n'), context, {timeout: 1000});
  const result = await context.setupCf({warn() {}, debug() {}}, explicitCf);
  return {result, fallback, reads, fetches};
}
(async () => {
  const disabled = await run('false');
  assert.equal(disabled.result, disabled.fallback);
  assert.equal(disabled.reads, 0); assert.equal(disabled.fetches, 0);
  const baseline = await run(undefined);
  assert.equal(baseline.result, baseline.fallback);
  assert.equal(baseline.reads, 1); assert.equal(baseline.fetches, 1);
  const explicit = {};
  assert.equal((await run('false', explicit)).result, explicit);
  console.log(JSON.stringify({vendor_cf_fixture: 'PASS', cases: 3,
    bundle_sha256: crypto.createHash('sha256').update(source).digest('hex'),
    functions_sha256: crypto.createHash('sha256').update(functions.join('\n')).digest('hex'),
    miniflare_version: JSON.parse(fs.readFileSync('/tmp/g01-tools/node_modules/miniflare/package.json', 'utf8')).version}));
})().catch(error => {
  // This fixture runs before credentials and evaluates only pinned public vendor source.
  console.error('vendor_cf_fixture: FAIL', error.stack);
  process.exitCode = 1;
});
