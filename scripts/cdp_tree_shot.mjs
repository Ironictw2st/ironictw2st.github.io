// Screenshot just the family-tree panel of a character page in headless Edge (local dev helper).
// Usage: node scripts/cdp_tree_shot.mjs <baseUrl> <templateKey> <width> <outfile>
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const [base, key, widthArg, outfile] = process.argv.slice(2);
const width = Number(widthArg) || 1440;
const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9340 + Math.floor(Math.random() * 50);
const proc = spawn(edge, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, '--user-data-dir=' + process.env.TEMP + '/edge-cdp-tree-' + port, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 40; i++) { try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await sleep(250); } }
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => (ws.onopen = r));
let id = 0; const pending = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (expr) => (await send('Runtime.evaluate', { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: width < 600 });
await send('Page.navigate', { url: `${base}/total_war/character.html?key=${key}` });
await sleep(4000);
const rect = JSON.parse(await ev(`(() => { const e = document.getElementById('tab-family-tree'); e.scrollIntoView(); const r = e.getBoundingClientRect(); return JSON.stringify({ x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height, nodes: document.querySelectorAll('.ftd-node').length, cw: document.querySelector('.ft-canvas').style.width, ch: document.querySelector('.ft-canvas').style.height, zoom: (document.querySelector('.ft-zoom-level')||{}).textContent }); })()`));
const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: rect.x, y: rect.y, width: rect.w, height: Math.min(rect.h, 2400), scale: 1 } });
writeFileSync(outfile, Buffer.from(shot.result.data, 'base64'));
console.log(JSON.stringify(rect));
ws.close(); proc.kill(); process.exit(0);
