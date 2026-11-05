// Drives the local editor in headless Edge over the DevTools protocol: opens the edit dialog, adds an item,
// moves a card with the Down button, opens History, and saves screenshots. Local dev only.
// Usage: node scripts/cdp_admin_demo.mjs http://localhost:8790 shots
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const base = process.argv[2] ?? 'http://localhost:8790';
const out = process.argv[3] ?? 'shots';
const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9333;
const proc = spawn(edge, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, '--window-size=1440,1000', '--user-data-dir=' + process.env.TEMP + '/edge-cdp-demo', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let targets;
for (let i = 0; i < 40; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await sleep(250); } }
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;
const shot = async (name) => { const r = await send('Page.captureScreenshot', { format: 'png' }); writeFileSync(`${out}/${name}.png`, Buffer.from(r.result.data, 'base64')); };

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url: `${base}/admin/roadmap.html` });
await sleep(2500);
const log = [];
log.push('cards: ' + await ev("document.querySelectorAll('.rm-card').length"));

// edit dialog
await ev("[...document.querySelectorAll('.ad-mini')].find(b=>b.textContent==='Edit').click()");
await sleep(500); await shot('admin-edit-dialog');
await ev("document.getElementById('ad-cancel').click()");

// add item through the form
await ev("document.getElementById('ad-add').click()");
await sleep(300);
await ev(`(()=>{document.getElementById('f-title').value='Demo item (delete me)';document.getElementById('f-description').value='<b>not bold</b> plain text only';document.getElementById('f-status').value='idea';document.getElementById('ad-form').requestSubmit();})()`);
await sleep(1200);
log.push('after add, cards: ' + await ev("document.querySelectorAll('.rm-card').length"));
log.push('markup rendered as text: ' + await ev("[...document.querySelectorAll('.rm-desc')].some(p=>p.textContent.includes('<b>not bold</b>') && !p.querySelector('b'))"));

// invalid input shows an error in the dialog
await ev("document.getElementById('ad-add').click()");
await sleep(200);
await ev("(()=>{document.getElementById('f-title').value='';document.getElementById('ad-form').requestSubmit();})()");
await sleep(800);
log.push('empty title error: ' + await ev("document.getElementById('ad-form-error').textContent"));
await shot('admin-edit-error');
await ev("document.getElementById('ad-cancel').click()");

// reorder with Down
const firstNext = "document.querySelector('.rm-col[data-status=next] .rm-title').textContent";
log.push('next[0] before: ' + await ev(firstNext));
await ev("document.querySelector('.rm-col[data-status=next] .ad-mini[aria-label^=\"Move\"][aria-label$=\"down\"]').click()");
await sleep(1200);
log.push('next[0] after Down: ' + await ev(firstNext));

// delete the demo item (two-step) and show history
await ev(`(()=>{const c=[...document.querySelectorAll('.rm-card')].find(c=>c.querySelector('.rm-title').textContent.startsWith('Demo item'));const b=[...c.querySelectorAll('.ad-mini')].find(b=>b.textContent==='Delete');b.click();b.click();})()`);
await sleep(1200);
log.push('after delete, cards: ' + await ev("document.querySelectorAll('.rm-card').length"));
await ev("document.getElementById('ad-history').click()");
await sleep(1000); await shot('admin-history');
log.push('history rows: ' + await ev("document.querySelectorAll('#ad-hist-list li').length"));
console.log(log.join('\n'));
ws.close(); proc.kill();
process.exit(0);
