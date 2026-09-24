from pathlib import Path

# Batch 4: Base-n physical-key layer. The Canon manual defines DEC/HEX/BIN/OCT
# as radix selectors in BASE mode. This patch preserves the physical keypad and
# earlier batches, changing only the existing radix-key behavior.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Tag the four exact physical radix buttons. Exact replacement avoids touching
# any Apps-menu text with the same labels.
keys = {
    '<button class="k fn" data-v="÷"><span class="sub g">DEC</span>÷</button>':
    '<button class="k fn" data-v="÷" data-base="DEC"><span class="sub g">DEC</span>÷</button>',
    '<button class="k fn" data-action="sqrt"><span class="sub g">HEX</span>√</button>':
    '<button class="k fn" data-action="sqrt" data-base="HEX"><span class="sub g">HEX</span>√</button>',
    '<button class="k fn" data-action="square"><span class="sub g">BIN</span>x²</button>':
    '<button class="k fn" data-action="square" data-base="BIN"><span class="sub g">BIN</span>x²</button>',
    '<button class="k fn" data-action="cube"><span class="sub g">OCT</span>x³</button>':
    '<button class="k fn" data-action="cube" data-base="OCT"><span class="sub g">OCT</span>x³</button>'
}
for old, new in keys.items():
    if new not in s:
        if old not in s:
            raise SystemExit('missing expected physical radix key: ' + old)
        s = s.replace(old, new, 1)

old = 'let expr="",ans=0,memory=0,shift=false,alpha=false,mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",history=[],histPos=-1;'
new = 'let expr="",ans=0,memory=0,shift=false,alpha=false,mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",history=[],histPos=-1,baseMode="DEC";'
if old in s:
    s = s.replace(old, new, 1)
elif 'baseMode="DEC"' not in s:
    raise SystemExit('missing calculator state anchor')

old = '$("status").textContent=(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+mode+" "+angle+(io==="LINE"?" LINE":"")+" "+(display==="FIX"?" FIX":display==="SCI"?" SCI":"");'
new = '$("status").textContent=(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+mode+(mode==="BASE"?" "+baseMode:" "+angle)+(io==="LINE"?" LINE":"")+" "+(display==="FIX"?" FIX":display==="SCI"?" SCI":"");'
if old in s:
    s = s.replace(old, new, 1)

if 'function baseRadix()' not in s:
    anchor = 'function calculate(){'
    block = '''function baseRadix(){return baseMode==="HEX"?16:baseMode==="BIN"?2:baseMode==="OCT"?8:10}
function baseFormat(v){
 const neg=v<0;let n=Math.abs(Math.trunc(v));
 let out=baseMode==="HEX"?n.toString(16).toUpperCase():baseMode==="BIN"?n.toString(2):baseMode==="OCT"?n.toString(8):String(n);
 return neg?"−"+out:out;
}
function baseCalculate(){
 try{
   if(!expr.trim())return;
   const radix=baseRadix();
   const js=expr.replace(/×/g,"*").replace(/÷/g,"/").replace(/−/g,"-")
     .replace(/([0-9A-F]+)/gi,m=>String(parseInt(m,radix)));
   if(!/^[0-9+*/%().\\s-]+$/.test(js))throw Error();
   const v=Function("return ("+js+")")();
   if(typeof v!=="number"||!Number.isFinite(v)||!Number.isInteger(v))throw Error();
   ans=v;history.unshift({e:expr,r:v});history=history.slice(0,20);histPos=-1;
   $("result").textContent=baseFormat(v);expr="";render();
 }catch(e){$("result").textContent="Math ERROR"}
}
function selectBase(next){
 baseMode=next;if(mode!=="BASE")mode="BASE";
 if(Number.isFinite(ans))$("result").textContent=baseFormat(ans);
 expr="";render();
}
'''
    if anchor not in s: raise SystemExit('calculate anchor missing')
    s=s.replace(anchor, block+anchor, 1)

old = 'function calculate(){\n try{'
new = 'function calculate(){\n if(mode==="BASE")return baseCalculate();\n try{'
if old in s:
    s=s.replace(old,new,1)
elif 'if(mode==="BASE")return baseCalculate();' not in s:
    raise SystemExit('BASE calculate dispatch missing')

old = 'function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;'
new = 'function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;\n if(mode==="BASE" && b.dataset.base){selectBase(b.dataset.base);return;}'
if old in s:
    s=s.replace(old,new,1)
elif 'b.dataset.base' not in s:
    raise SystemExit('BASE key dispatch missing')

old = 'if(alpha && alphaVal!==undefined){add(alphaVal);alpha=false;render();return}'
new = 'if(alpha && alphaVal!==undefined){if(mode==="BASE" && /^[A-F]$/.test(alphaVal)){add(alphaVal);alpha=false;render();return}add(alphaVal);alpha=false;render();return}'
if old in s:s=s.replace(old,new,1)

old = 'if(i===17)allClear(),mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c";'
new = 'if(i===17)allClear(),mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",baseMode="DEC";'
if old in s:s=s.replace(old,new,1)

old = 'function base(n){if(["DEC","HEX","BIN","OCT"].includes(n))return $("result").textContent=n;'
new = 'function base(n){if(["DEC","HEX","BIN","OCT"].includes(n))return selectBase(n);'
if old in s:s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('F-789SGA Batch 4 BASE-n patch prepared')
