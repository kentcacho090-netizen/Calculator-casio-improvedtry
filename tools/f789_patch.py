from pathlib import Path
import re

# Batch 4: Base-n physical-key layer. This patch deliberately changes only the
# existing DEC/HEX/BIN/OCT keys and the calculator's calculation path when the
# user is in BASE mode. It preserves the physical keypad and all earlier fixes.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Tag the four physical radix keys without changing their visible labels.
for marker, radix in [('class="sub g">DEC', 'DEC'), ('class="sub g">HEX', 'HEX'), ('class="sub g">BIN', 'BIN'), ('class="sub g">OCT', 'OCT')]:
    pat = re.compile(r'(<button\\b(?=[^>]*' + re.escape(marker) + r')[^>]*)(>)')
    def repl(m, radix=radix):
        tag=m.group(1)
        if 'data-base=' in tag:
            return m.group(0)
        return tag + f' data-base="{radix}"' + m.group(2)
    s, n = pat.subn(repl, s, count=1)
    if n == 0:
        raise SystemExit(f'missing physical {radix} key')

# Add BASE state alongside the existing mode/angle state.
old = 'let expr="",ans=0,memory=0,shift=false,alpha=false,mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",history=[],histPos=-1;'
new = 'let expr="",ans=0,memory=0,shift=false,alpha=false,mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",history=[],histPos=-1,baseMode="DEC";'
if old in s:
    s=s.replace(old,new,1)
elif 'baseMode="DEC"' not in s:
    raise SystemExit('missing calculator state anchor')

# BASE mode status indicator: show the selected radix like the real calculator.
old = '$("status").textContent=(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+mode+" "+angle+(io==="LINE"?" LINE":"")+" "+(display==="FIX"?" FIX":display==="SCI"?" SCI":"");'
new = '$("status").textContent=(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+mode+(mode==="BASE"?" "+baseMode:" "+angle)+(io==="LINE"?" LINE":"")+" "+(display==="FIX"?" FIX":display==="SCI"?" SCI":"");'
if old in s:s=s.replace(old,new,1)

# Insert the BASE evaluator immediately before calculate().
anchor='function calculate(){'
if 'function baseDigitValue' not in s:
    block=r'''function baseDigitValue(ch){return parseInt(ch,16)}
function baseRadix(){return baseMode==="HEX"?16:baseMode==="BIN"?2:baseMode==="OCT"?8:10}
function baseCalculate(){
 try{
   if(!expr.trim()) return;
   const radix=baseRadix();
   const js=expr.replace(/×/g,"*").replace(/÷/g,"/").replace(/−/g,"-")
     .replace(/([0-9A-F]+)/gi,m=>String(parseInt(m,radix)));
   if(!/^[0-9+*/%().\\s-]+$/.test(js))throw Error();
   const v=Function("return ("+js+")")();
   if(typeof v!=="number"||!Number.isFinite(v)||!Number.isInteger(v))throw Error();
   ans=v;
   history.unshift({e:expr,r:v});history=history.slice(0,20);histPos=-1;
   $("result").textContent=baseFormat(v);
   expr="";render();
 }catch(e){$("result").textContent="Math ERROR"}
}
function baseFormat(v){
 const neg=v<0;let n=Math.abs(Math.trunc(v)),out=baseMode==="HEX"?n.toString(16).toUpperCase():baseMode==="BIN"?n.toString(2):baseMode==="OCT"?n.toString(8):String(n);
 return neg?"−"+out:out;
}
function selectBase(next){
 baseMode=next;
 if(mode!=="BASE")mode="BASE";
 if(Number.isFinite(ans))$("result").textContent=baseFormat(ans);
 expr="";render();
}
'''
    s=s.replace(anchor,block+anchor,1)

# Ensure calculate delegates to the real BASE evaluator before the general evaluator.
old='function calculate(){\n try{'
new='function calculate(){\n if(mode==="BASE")return baseCalculate();\n try{'
if old in s:s=s.replace(old,new,1)
elif 'if(mode==="BASE")return baseCalculate();' not in s:raise SystemExit('calculate anchor missing')

# Physical radix keys now select a number system when BASE mode is active.
old='function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;'
new='function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;\n if(mode==="BASE" && b.dataset.base){selectBase(b.dataset.base);return;}'
if old in s:s=s.replace(old,new,1)
elif 'b.dataset.base' not in s:raise SystemExit('pressButton anchor missing')

# In BASE mode Alpha+A..F are hexadecimal digits rather than stored variables.
old='if(alpha && alphaVal!==undefined){add(alphaVal);alpha=false;render();return}'
new='if(alpha && alphaVal!==undefined){if(mode==="BASE" && /^[A-F]$/.test(alphaVal)){add(alphaVal);alpha=false;render();return}add(alphaVal);alpha=false;render();return}'
if old in s:s=s.replace(old,new,1)

# Reset radix on calculator reset.
old='if(i===17)allClear(),mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c";'
new='if(i===17)allClear(),mode="COMP",angle="DEG",io="MATH",display="NORM1",fractionMode="d/c",baseMode="DEC";'
if old in s:s=s.replace(old,new,1)

# The existing BASE Apps DEC/HEX/BIN/OCT entries must use the same state,
# rather than merely printing their names.
old='function base(n){if(["DEC","HEX","BIN","OCT"].includes(n))return $("result").textContent=n;'
new='function base(n){if(["DEC","HEX","BIN","OCT"].includes(n))return selectBase(n);'
if old in s:s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('F-789SGA Batch 4 BASE-n patch applied')
