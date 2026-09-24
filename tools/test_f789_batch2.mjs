import fs from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';

const html = fs.readFileSync('index.html', 'utf8');
const vc = new VirtualConsole();
vc.on('jsdomError', e => { throw e; });
const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'http://localhost/', virtualConsole: vc });
const { document } = dom.window;

const click = (selector, label) => {
  const b = document.querySelector(selector);
  if (!b || typeof b.onclick !== 'function') throw new Error(`Missing handler: ${label}`);
  b.click();
};
const result = () => document.getElementById('result').textContent;
const expr = () => document.getElementById('expr').textContent;
const assertEq = (actual, expected, label) => {
  if (String(actual) !== String(expected)) throw new Error(`${label}: expected ${expected}, got ${actual}`);
};
const assertClose = (actual, expected, eps, label) => {
  const n = Number(actual);
  if (!Number.isFinite(n) || Math.abs(n - expected) > eps) throw new Error(`${label}: expected ${expected}, got ${actual}`);
};
const reset = () => document.getElementById('on').click();

// EXP: 4 EXP 3 = 4000.
reset();
click('[data-v="4"]', '4');
click('[data-action="exp"]', 'EXP');
click('[data-v="3"]', '3');
document.getElementById('equals').click();
assertEq(result(), '4000', 'EXP scientific notation');

// Shift log -> 10^x: 10^2 = 100.
reset();
document.getElementById('shift').click();
click('[data-action="log"]', 'Shift log / 10^n');
click('[data-v="2"]', '2');
click('[data-v=")"]', ')');
document.getElementById('equals').click();
assertEq(result(), '100', '10^n');

// Shift ln -> e^x: e^1 = e.
reset();
document.getElementById('shift').click();
click('[data-action="ln"]', 'Shift ln / e^n');
click('[data-v="1"]', '1');
click('[data-v=")"]', ')');
document.getElementById('equals').click();
assertClose(result(), Math.E, 1e-10, 'e^n');

// 10P3 = 720 using Shift on the physical multiplication key.
reset();
click('[data-v="1"]', '1');
click('[data-v="0"]', '0');
document.getElementById('shift').click();
click('[data-v="×"]', 'Shift × / nPr');
click('[data-v="3"]', '3');
document.getElementById('equals').click();
assertEq(result(), '720', 'nPr');

// 5C2 = 10 using Shift on the physical division key.
reset();
click('[data-v="5"]', '5');
document.getElementById('shift').click();
click('[data-v="÷"]', 'Shift ÷ / nCr');
click('[data-v="2"]', '2');
document.getElementById('equals').click();
assertEq(result(), '10', 'nCr');

// Alpha + EXP inserts e, while Shift + EXP remains π/Σ according to the key layer.
reset();
document.getElementById('alpha').click();
click('[data-alpha="e"]', 'Alpha e');
assertEq(expr(), 'e', 'Alpha e insertion');
document.getElementById('equals').click();
assertClose(result(), Math.E, 1e-10, 'Euler constant');

dom.window.close();
console.log('F-789SGA Batch 2 runtime tests passed');
