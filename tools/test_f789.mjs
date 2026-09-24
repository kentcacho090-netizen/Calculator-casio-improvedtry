import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync('index.html', 'utf8');
const script = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].at(-1)?.[1];
if (!script) throw new Error('Calculator script not found');

class Element {
  constructor(attrs = {}) {
    this.id = attrs.id || '';
    this.dataset = {};
    for (const [k, v] of Object.entries(attrs)) {
      if (k.startsWith('data-')) this.dataset[k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = v;
    }
    this.textContent = '';
    this.innerHTML = '';
    this.children = [];
    this.onclick = null;
    this.value = '';
    this.classList = { toggle(){}, add(){}, remove(){} };
  }
  click() { if (typeof this.onclick === 'function') this.onclick(); }
  querySelectorAll() { return []; }
}

const ids = ['shift','alpha','up','mode','on','apps','left','right','down','convt','status','expr','result','overlay','title','choices','cancel','del','ca','ansTop','ans','equals'];
const byId = new Map(ids.map(id => [id, new Element({id})]));
const buttons = [];
const buttonRe = /<button\b([^>]*)>([\s\S]*?)<\/button>/gi;
for (const m of html.matchAll(buttonRe)) {
  const attrs = {};
  const idm = m[1].match(/\bid="([^"]+)"/); if (idm) attrs.id = idm[1];
  for (const a of m[1].matchAll(/\b(data-[\w-]+)="([^"]*)"/g)) attrs[a[1]] = a[2];
  const b = new Element(attrs);
  if (attrs.id) byId.set(attrs.id, b);
  buttons.push(b);
}
const document = {
  getElementById(id) { return byId.get(id) || new Element({id}); },
  querySelectorAll(sel) {
    if (sel === '[data-v]') return buttons.filter(b => b.dataset.v !== undefined);
    if (sel === '[data-action]') return buttons.filter(b => b.dataset.action !== undefined);
    return [];
  }
};
byId.get('choices').querySelectorAll = () => [];

const context = { document, window: {}, console, Math, Number, String, Object, Array, RegExp, Error, Function, parseInt, parseFloat, isNaN, isFinite };
vm.createContext(context);
vm.runInContext(script, context, { timeout: 1000 });

const click = (predicate, label) => {
  const b = buttons.find(predicate);
  if (!b) throw new Error(`Button not found: ${label}`);
  b.click();
  return b;
};
const text = () => byId.get('result').textContent;
const expr = () => byId.get('expr').textContent;
const assertEq = (actual, expected, label) => {
  if (String(actual) !== String(expected)) throw new Error(`${label}: expected ${expected}, got ${actual}`);
};

// Basic arithmetic: 2 + 3 = 5.
click(b => b.dataset.v === '2', '2');
click(b => b.dataset.v === '+', '+');
click(b => b.dataset.v === '3', '3');
byId.get('equals').click();
assertEq(text(), '5', 'basic 2+3');

// Shift x!: 5! = 120.
byId.get('shift').click();
click(b => b.dataset.action === 'inv', 'x^-1 / x!');
click(b => b.dataset.v === '5', '5');
byId.get('equals').click();
assertEq(text(), '120', 'Shift x!');

// Shift inverse sine in DEG: sin^-1(0.5) = 30.
byId.get('shift').click();
click(b => b.dataset.action === 'sin', 'sin / sin^-1');
click(b => b.dataset.v === '0.5', '0.5');
byId.get('equals').click();
assertEq(text(), '30', 'Shift sin^-1 in DEG');

// Alpha X variable is consumed by the next key and leaves X in the expression.
byId.get('alpha').click();
click(b => b.dataset.alpha === 'X', 'Alpha X');
assertEq(expr(), 'X', 'Alpha X insertion');

// Memory: 2+3 -> M+, RCL -> 5.
byId.get('on').click();
click(b => b.dataset.v === '2', '2');
click(b => b.dataset.v === '+', '+');
click(b => b.dataset.v === '3', '3');
byId.get('equals').click();
click(b => b.dataset.action === 'mplus', 'M+');
click(b => b.dataset.action === 'rcl', 'RCL');
byId.get('equals').click();
assertEq(text(), '5', 'M+/RCL');

console.log('F-789SGA Batch 1 runtime smoke tests passed');
