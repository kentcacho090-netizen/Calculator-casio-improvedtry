import fs from 'node:fs';
import vm from 'node:vm';

const html = fs.readFileSync('index.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)?.[1];
if (!script) throw new Error('Calculator script not found');

class El {
  constructor(tag = 'button', attrs = '') {
    this.tagName = tag.toUpperCase();
    this.textContent = '';
    this.innerHTML = '';
    this.onclick = null;
    this.children = [];
    this.dataset = {};
    this.classList = { toggle() {} };
    for (const m of attrs.matchAll(/data-([a-zA-Z0-9-]+)="([^"]*)"/g)) {
      this.dataset[m[1].replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = m[2];
    }
    const id = attrs.match(/\bid="([^"]+)"/);
    if (id) this.id = id[1];
  }
  click() { if (typeof this.onclick !== 'function') throw new Error(`No click handler for ${this.id || this.dataset.action || this.dataset.v || this.dataset.alpha || this.tagName}`); this.onclick(); }
}

const buttons = [];
for (const m of html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g)) buttons.push(new El('button', m[1]));
const byId = new Map(buttons.filter(b => b.id).map(b => [b.id, b]));
const nodes = {
  status: new El('div'), expr: new El('div'), result: new El('div'), shift: byId.get('shift'), alpha: byId.get('alpha'),
  choices: new El('div'), title: new El('div'), overlay: new El('div'), cancel: byId.get('cancel') || new El('button')
};
const matches = selector => {
  const m = selector.match(/^\[data-([\w-]+)(?:="([^"]*)")?\]$/);
  if (m) {
    const key = m[1].replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    return buttons.filter(b => b.dataset[key] !== undefined && (m[2] === undefined || b.dataset[key] === m[2]));
  }
  return [];
};
const document = {
  getElementById(id) { return nodes[id] || byId.get(id); },
  querySelector(selector) { return matches(selector)[0] || null; },
  querySelectorAll(selector) { return matches(selector); },
};
const window = { document };

vm.runInNewContext(script, { document, window, console, Math, Number, String, Object, Array, RegExp, Error, Function, parseInt, parseFloat, isFinite, Infinity, NaN });

const click = (selector, label) => { const b = document.querySelector(selector); if (!b) throw new Error(`Button not found: ${label}`); b.click(); };
const result = () => nodes.result.textContent;
const expression = () => nodes.expr.textContent;
const assertEq = (actual, expected, label) => { if (String(actual) !== String(expected)) throw new Error(`${label}: expected ${expected}, got ${actual}`); };
const assertClose = (actual, expected, eps, label) => { const n = Number(actual); if (!Number.isFinite(n) || Math.abs(n - expected) > eps) throw new Error(`${label}: expected ${expected}, got ${actual}`); };
const reset = () => byId.get('on').click();

reset(); click('[data-v="4"]', '4'); click('[data-action="exp"]', 'EXP'); click('[data-v="3"]', '3'); byId.get('equals').click(); assertEq(result(), '4000', 'EXP scientific notation');
reset(); byId.get('shift').click(); click('[data-action="log"]', 'Shift log / 10^n'); click('[data-v="2"]', '2'); click('[data-v=")"]', ')'); byId.get('equals').click(); assertEq(result(), '100', '10^n');
reset(); byId.get('shift').click(); click('[data-action="ln"]', 'Shift ln / e^n'); click('[data-v="1"]', '1'); click('[data-v=")"]', ')'); byId.get('equals').click(); assertClose(result(), Math.E, 1e-10, 'e^n');
reset(); click('[data-v="1"]', '1'); click('[data-v="0"]', '0'); byId.get('shift').click(); click('[data-v="×"]', 'Shift × / nPr'); click('[data-v="3"]', '3'); byId.get('equals').click(); assertEq(result(), '720', 'nPr');
reset(); click('[data-v="5"]', '5'); byId.get('shift').click(); click('[data-v="÷"]', 'Shift ÷ / nCr'); click('[data-v="2"]', '2'); byId.get('equals').click(); assertEq(result(), '10', 'nCr');
reset(); byId.get('alpha').click(); click('[data-alpha="e"]', 'Alpha e'); assertEq(expression(), 'e', 'Alpha e insertion'); byId.get('equals').click(); assertClose(result(), Math.E, 1e-10, 'Euler constant');

console.log('F-789SGA Batch 2 runtime tests passed');
