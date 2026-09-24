import fs from 'node:fs';
import { JSDOM, VirtualConsole } from 'jsdom';

const html = fs.readFileSync('index.html', 'utf8');
const virtualConsole = new VirtualConsole();
virtualConsole.on('jsdomError', error => console.error('JSDOM error:', error.stack || error.message));
const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'http://localhost/', virtualConsole });
const { document } = dom.window;

const click = (selector, label) => {
  const b = document.querySelector(selector);
  if (!b) throw new Error(`Button not found: ${label}`);
  if (typeof b.onclick !== 'function') throw new Error(`No click handler installed: ${label}`);
  b.click();
};
const result = () => document.getElementById('result').textContent;
const expression = () => document.getElementById('expr').textContent;
const assertEq = (actual, expected, label) => {
  if (String(actual) !== String(expected)) throw new Error(`${label}: expected ${expected}, got ${actual}`);
};

console.log('2-key handler:', typeof document.querySelector('[data-v="2"]')?.onclick);
console.log('equals handler:', typeof document.getElementById('equals')?.onclick);

// Basic arithmetic: verify the expression itself before evaluating 2 + 3.
click('[data-v="2"]', '2');
click('[data-v="+"]', '+');
click('[data-v="3"]', '3');
console.log('Basic expression before equals:', JSON.stringify(expression()));
document.getElementById('equals').click();
console.log('Basic result after equals:', JSON.stringify(result()));
assertEq(result(), '5', 'basic 2+3');

// Shift x!: 5! = 120.
document.getElementById('on').click();
document.getElementById('shift').click();
click('[data-action="inv"]', 'x^-1 / x!');
click('[data-v="5"]', '5');
document.getElementById('equals').click();
assertEq(result(), '120', 'Shift x!');

// Shift inverse sine in DEG: sin^-1(0.5) = 30.
document.getElementById('on').click();
document.getElementById('shift').click();
click('[data-action="sin"]', 'sin / sin^-1');
click('[data-v="0"]', '0');
click('[data-v="."]', '.');
click('[data-v="5"]', '5');
document.getElementById('equals').click();
assertEq(result(), '30', 'Shift sin^-1 in DEG');

// Alpha X variable is consumed by the next key and leaves X in the expression.
document.getElementById('on').click();
document.getElementById('alpha').click();
click('[data-alpha="X"]', 'Alpha X');
assertEq(expression(), 'X', 'Alpha X insertion');

// Memory: 2+3 -> M+, RCL -> 5.
document.getElementById('on').click();
click('[data-v="2"]', '2');
click('[data-v="+"]', '+');
click('[data-v="3"]', '3');
document.getElementById('equals').click();
click('[data-action="mplus"]', 'M+');
click('[data-action="rcl"]', 'RCL');
document.getElementById('equals').click();
assertEq(result(), '5', 'M+/RCL');

dom.window.close();
console.log('F-789SGA Batch 1 runtime smoke tests passed');
