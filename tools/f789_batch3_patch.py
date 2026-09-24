from pathlib import Path

p = Path('index.html')
s = p.read_text()

def rep(old, new):
    global s
    if old not in s:
        raise SystemExit(f'missing expected source fragment: {old[:100]}')
    s = s.replace(old, new, 1)

# Correct the physical secondary-key metadata.
rep('data-action="rcl"><span class="sub o">STO</span>RCL',
    'data-action="rcl" data-shift="sto"><span class="sub o">STO</span>RCL')
rep('data-v="+"><span class="sub o">Pol(</span>+',
    'data-v="+" data-shift="pol"><span class="sub o">Pol(</span>+')
rep('data-v="−"><span class="sub o">Rec(</span>−',
    'data-v="−" data-shift="rec"><span class="sub o">Rec(</span>−')
rep('data-v=")" data-shift=", " data-alpha="X"',
    'data-v=")" data-shift="," data-alpha="X"')

# Inject a small, isolated Batch 3 compatibility layer before the existing IIFE closes.
# This avoids rewriting the already-verified calculation engine.
snippet = r'''
let b3Store=false,b3Recall=false,b3DmsStage=0;
function b3DmsToDecimal(s){return s.replace(/(\d+(?:\.\d+)?)°(?:\s*(\d+(?:\.\d+)?)′)?(?:\s*(\d+(?:\.\d+)?)″)?/g,(m,d,mi='0',se='0')=>String(+d+(+mi)/60+(+se)/3600));}
function b3Pol(x,y){return Math.hypot(x,y);}
function b3Rec(r,t){return r*Math.cos(rad(t));}
function b3Calculate(){
 try{let source=b3DmsToDecimal(expr).replace(/Pol\(([^,]+),([^\)]+)\)/g,(m,x,y)=>String(b3Pol(evalExpr(x),evalExpr(y)))).replace(/Rec\(([^,]+),([^\)]+)\)/g,(m,r,t)=>String(b3Rec(evalExpr(r),evalExpr(t))));expr=source;calculate();}
 catch(e){$("result").textContent="Math ERROR"}
}
function b3VariableButton(b){
 const old=b.onclick;
 b.onclick=()=>{const k=b.dataset.alpha;if(b3Store){V[k]=ans;b3Store=false;alpha=false;render();return}if(b3Recall){add(String(V[k]??0));b3Recall=false;alpha=false;render();return}old();};
}
const b3Rcl=document.querySelector('[data-action="rcl"]');
if(b3Rcl){b3Rcl.onclick=()=>{if(shift){b3Store=true;b3Recall=false;shift=false;render();return}b3Recall=true;render();};}
for(const b of document.querySelectorAll('[data-alpha]')) b3VariableButton(b);
const b3Plus=document.querySelector('[data-v="+"]');
if(b3Plus){const old=b3Plus.onclick;b3Plus.onclick=()=>{if(shift){add('Pol(');shift=false;render();return}old();};}
const b3Minus=document.querySelector('[data-v="−"]');
if(b3Minus){const old=b3Minus.onclick;b3Minus.onclick=()=>{if(shift){add('Rec(');shift=false;render();return}old();};}
const b3Paren=document.querySelector('[data-v=")"]');
if(b3Paren){const old=b3Paren.onclick;b3Paren.onclick=()=>{if(shift){add(',');shift=false;render();return}old();};}
const b3Dms=document.querySelector('[data-action="dms"]');
if(b3Dms){b3Dms.onclick=()=>{const mark=b3DmsStage===0?'°':b3DmsStage===1?'′':'″';add(mark);b3DmsStage=(b3DmsStage+1)%3;};}
for(const id of ['ans','ansTop']){const b=$(id);if(b){b.onclick=()=>{if(shift){const old=angle;const v=ans;const next=old==='DEG'?'RAD':old==='RAD'?'GRAD':'DEG';ans=old==='DEG'?v*Math.PI/180:old==='RAD'?v*200/Math.PI:v*180/200;angle=next;shift=false;$("result").textContent=formatNumber(ans);render();return}add('Ans');};}}
$("equals").onclick=b3Calculate;
'''
marker='\n})();'
if marker not in s:
    raise SystemExit('IIFE closing marker not found')
s=s.replace(marker,'\n'+snippet+marker,1)
p.write_text(s)
print('Batch 3 patch applied')
