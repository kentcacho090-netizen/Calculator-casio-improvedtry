import fs from 'node:fs';
import vm from 'node:vm';
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
if(!script) throw new Error('Calculator script not found');
class El{constructor(tag='button',attrs=''){this.tagName=tag.toUpperCase();this.textContent='';this.innerHTML='';this.onclick=null;this.children=[];this.dataset={};this.classList={toggle(){}};for(const m of attrs.matchAll(/data-([a-zA-Z0-9-]+)="([^"]*)"/g))this.dataset[m[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase())]=m[2];const id=attrs.match(/\bid="([^"]+)"/);if(id)this.id=id[1]}click(){if(typeof this.onclick!=='function')throw new Error(`No click handler for ${this.id||this.dataset.action||this.dataset.v||this.tagName}`);this.onclick()}}
const buttons=[];for(const m of html.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/g))buttons.push(new El('button',m[1]));
const byId=new Map(buttons.filter(b=>b.id).map(b=>[b.id,b]));
const nodes={status:new El('div'),expr:new El('div'),result:new El('div'),shift:byId.get('shift'),alpha:byId.get('alpha'),choices:new El('div'),title:new El('div'),overlay:new El('div'),cancel:byId.get('cancel')||new El('button')};
const matches=selector=>{const m=selector.match(/^\[data-([\w-]+)(?:="([^"]*)")?\]$/);if(!m)return[];const key=m[1].replace(/-([a-z])/g,(_,c)=>c.toUpperCase());return buttons.filter(b=>b.dataset[key]!==undefined&&(m[2]===undefined||b.dataset[key]===m[2]))};
const document={getElementById:id=>nodes[id]||byId.get(id),querySelector:selector=>matches(selector)[0]||null,querySelectorAll:selector=>matches(selector)};
const window={document};
vm.runInNewContext(script,{document,window,console,Math,Number,String,Object,Array,RegExp,Error,Function,parseInt,parseFloat,isFinite,Infinity,NaN});
const click=(selector,label)=>{const b=document.querySelector(selector);if(!b)throw new Error(`Button not found: ${label}`);b.click()};
const clickNth=(selector,index,label)=>{const b=matches(selector)[index];if(!b)throw new Error(`Button not found: ${label}`);b.click()};
const result=()=>nodes.result.textContent;const expr=()=>nodes.expr.textContent;
const eq=(a,b,l)=>{if(String(a)!==String(b))throw new Error(`${l}: expected ${b}, got ${a}`)};
const close=(a,b,e,l)=>{const n=Number(a);if(!Number.isFinite(n)||Math.abs(n-b)>e)throw new Error(`${l}: expected ${b}, got ${a}`)};
const reset=()=>byId.get('on').click();

// DMS: 12°30′0″ = 12.5°
reset();click('[data-v="1"]','1');click('[data-v="2"]','2');click('[data-action="dms"]','DMS °');click('[data-v="3"]','3');click('[data-v="0"]','0');click('[data-action="dms"]','DMS ′');click('[data-v="0"]','0');click('[data-action="dms"]','DMS ″');byId.get('equals').click();close(result(),12.5,1e-12,'DMS conversion');

// STO A then RCL A.
reset();click('[data-v="7"]','7');byId.get('equals').click();byId.get('shift').click();click('[data-action="rcl"]','STO');byId.get('alpha').click();click('[data-alpha="A"]','Alpha A');reset();byId.get('alpha').click();click('[data-alpha="A"]','Alpha A');byId.get('equals').click();eq(result(),'7','stored variable A recall');

// Pol(3,4) = 5. The physical comma is SHIFT + right parenthesis.
reset();byId.get('shift').click();click('[data-v="+"]','Shift + / Pol');click('[data-v="3"]','3');byId.get('shift').click();click('[data-v=")"]','Shift ) / comma');click('[data-v="4"]','4');click('[data-v=")"]',')');byId.get('equals').click();close(result(),5,1e-12,'Pol(3,4)');

// Rec(5,53.130102354...) ≈ 3.
reset();byId.get('shift').click();click('[data-v="−"]','Shift - / Rec');click('[data-v="5"]','5');byId.get('shift').click();click('[data-v=")"]','Shift ) / comma');for(const ch of '53.13010235415598')click(`[data-v="${ch}"]`,ch);click('[data-v=")"]',')');byId.get('equals').click();close(result(),3,1e-9,'Rec(r,theta)');

// DRG▶ converts 180 degrees to π radians and changes the angle mode.
reset();click('[data-v="1"]','1');click('[data-v="8"]','8');click('[data-v="0"]','0');byId.get('equals').click();byId.get('shift').click();click('[data-action="drg"]','Shift Ans / DRG');close(result(),Math.PI,1e-12,'DRG degree-to-radian');

console.log('F-789SGA Batch 3 runtime tests passed');
