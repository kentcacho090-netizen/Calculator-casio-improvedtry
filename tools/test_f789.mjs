import fs from 'node:fs';
import { JSDOM } from 'jsdom';

const html = fs.readFileSync('index.html', 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'http://localhost/' });
const { document } = dom.window;

const click = (selector, label) => {
  const b = document.querySelector(selector);
  if (!b) throw new Error(`Button not found: ${label}`);
  b.click();
};
const result = () => document.getElementById('result').textContent;
const expression = () => document.getElementById('expr').textContent;
const assertEq = (actual, expected, label) => {
  if (String(actual) !== String(expected)) throw new Error(`${label}: expected ${expected}, got ${actual}`);
};

// Basic arithmetic: 2 + 3 = 5.
click('[data-v="2"]', '2');
click('[data-v="+"]', '+');
click('[data-v="3"]', '3');
document.getElementById('equals').click();
assertEq(result(), '5', 'basic 2+3');

// Shift x!: 5! = 120.
document.getElementById('shift').click();
click('[data-action="inv"]', 'x^-1 / x!');
click('[data-v="5"]', '5');
document.getElementById('equals').click();
assertEq(result(), '120', 'Shift x!');

// Shift inverse sine in DEG: sin^-1(0.5) = 30.
document.getElementById('shift').click();
click('[data-action="sin"]', 'sin / sin^-1');
click('[data-v="0"]', '0');
click('[data-v="."]', '.');
click('[data-v="5"]', '5');
document.getElementById('equals').click();
assertEq(result(), '30', 'Shift sin^-1 in DEG');

// Alpha X variable is consumed by the next key and leaves X in the expression.
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
