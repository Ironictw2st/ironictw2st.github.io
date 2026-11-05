// Full-page screenshot in headless Edge with a chosen theme (local dev helper).
// Usage: node scripts/cdp_shot.mjs <url> <light|dark> <width> <maxHeight> <outfile>
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';

const [url, theme, widthArg, maxH, outfile] = process.argv.slice(2);
const width = Number(widthArg) || 1440;
const edge = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const port = 9400 + Math.floor(Math.random() * 90);
const proc = spawn(edge, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, '--user-data-dir=' + process.env.TEMP + '/edge-cdp-shot-' + port, 'about:blank'], { stdio: 'ignore' });
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
await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
await send('Page.addScriptToEvaluateOnNewDocument', { source: `try{localStorage.setItem('theme','${theme}')}catch(e){}` });
await send('Page.navigate', { url });
await sleep(4500);
const h = Math.min(Number(maxH) || 1600, Number(await ev('document.documentElement.scrollHeight')) || 1600);
const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width, height: h, scale: 1 } });
writeFileSync(outfile, Buffer.from(shot.result.data, 'base64'));
console.log(`${outfile} ${width}x${h} theme=${await ev("document.documentElement.getAttribute('data-theme')")}`);
ws.close(); proc.kill(); process.exit(0);
