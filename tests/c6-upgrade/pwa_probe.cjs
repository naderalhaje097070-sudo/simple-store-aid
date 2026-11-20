const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const ctx = await b.newContext(); const p = await ctx.newPage();
  const logs = []; p.on('console', m => logs.push(m.type() + ': ' + m.text().slice(0, 160)));
  const reqs = []; p.on('response', r => { if (/sw\.js|workbox/.test(r.url())) reqs.push(r.status() + ' ' + r.url()); });
  const resp = await p.goto(process.argv[2], { waitUntil: 'networkidle' });
  await p.waitForTimeout(5000);
  const regs = await p.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).map(r => (r.active || r.installing || r.waiting || {}).scriptURL || 'none'));
  const ctrl = await p.evaluate(() => !!navigator.serviceWorker.controller);
  console.log(JSON.stringify({ status: resp.status(), html_cache_control: resp.headers()['cache-control'] || null, sw_requests: reqs, registrations: regs, controlled: ctrl, pwa_logs: logs.filter(l => /pwa|service ?worker|sw\.js/i.test(l)) }, null, 1));
  await b.close();
})();
