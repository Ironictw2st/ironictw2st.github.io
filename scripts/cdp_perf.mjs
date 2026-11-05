// Page weight as the browser sees it (headless Edge, cold cache): bytes over the wire, by type.
// Usage: node scripts/cdp_perf.mjs <url>
import { spawn } from 'node:child_process';

const url = process.argv[2];
const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9500 + Math.floor(Math.random() * 90);
const proc = spawn(edge, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, '--user-data-dir=' + process.env.TEMP + '/edge-cdp-perf-' + port, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 40; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await sleep(250); } }
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map(); const reqs = new Map(); const done = [];
ws.onmessage = (m) => {
  const d = JSON.parse(m.data);
  if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); return; }
  if (d.method === 'Network.responseReceived') reqs.set(d.params.requestId, { url: d.params.response.url, type: d.params.type, status: d.params.response.status });
  if (d.method === 'Network.loadingFinished') { const r = reqs.get(d.params.requestId); if (r) done.push({ ...r, bytes: d.params.encodedDataLength }); }
};
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });

await send('Network.enable');
await send('Network.setCacheDisabled', { cacheDisabled: true });
await send('Page.enable');
await send('Page.navigate', { url });
await sleep(9000);

const by = {};
let total = 0;
for (const r of done) { by[r.type] = (by[r.type] || 0) + r.bytes; total += r.bytes; }
const mb = (n) => (n / 1e6).toFixed(2) + ' MB';
console.log(`${url}\n  requests: ${done.length}   total: ${mb(total)}`);
console.log('  by type: ' + Object.entries(by).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${mb(v)}`).join(', '));
console.log('  biggest: ' + done.sort((a, b) => b.bytes - a.bytes).slice(0, 5).map((r) => `${r.url.split('/').slice(-2).join('/')} ${mb(r.bytes)}`).join(' | '));
ws.close(); proc.kill(); process.exit(0);
