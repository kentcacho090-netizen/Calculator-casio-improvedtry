from pathlib import Path

# Batch 1: repair only already-present Shift dispatch and mappings.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = {
    '<button class="k fn" data-action="inv"><span class="sub o">x!</span>x⁻¹</button>':
    '<button class="k fn" data-action="inv" data-shift="x!"><span class="sub o">x!</span>x⁻¹</button>',
    '<button class="k fn" data-action="abs"><span class="sub o">%</span>Abs</button>':
    '<button class="k fn" data-action="abs" data-shift="percent"><span class="sub o">%</span>Abs</button>',
    '<button class="k fn" data-v="("><span class="sub o">%</span>(</button>':
    '<button class="k fn" data-v="(" data-shift="percent"><span class="sub o">%</span>(</button>',
}

for old, new in replacements.items():
    if old in s:
        s = s.replace(old, new, 1)
    elif new not in s:
        raise SystemExit(f'missing expected markup and patched form: {old}')

old = '''function pressButton(b){
 const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;
 if(alpha && alphaVal!==undefined){add(alphaVal);alpha=false;render();return}
 if(shift && shiftVal!==undefined){shift=false;doShift(shiftVal);render();return}
 const a=b.dataset.action;'''
new = '''function pressButton(b){
 const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;
 if(alpha && alphaVal!==undefined){add(alphaVal);alpha=false;render();return}
 if(shift){
   if(shiftVal!==undefined){const sv=shiftVal;shift=false;doShift(sv);render();return}
   shift=false;render();
 }
 const a=b.dataset.action;'''
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('missing expected pressButton block and patched form')

old = 'else if(a==="hyp")add(shift?"cosh(":"sinh(");else if(a==="sin")add("sin(");'
new = 'else if(a==="hyp")add("sinh(");else if(a==="sin")add("sin(");'
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('missing expected hyp mapping and patched form')

old = 'else if(action==="fraction")$("result").textContent=fraction(ans);else if(action==="mminus")'
new = 'else if(action==="fraction")$("result").textContent=fraction(ans);else if(action==="x!")add("!");else if(action==="percent")add("%");else if(action==="mminus")'
if old in s:
    s = s.replace(old, new, 1)

# Remove only the redundant duplicate x!/percent tail cases if still present.
s = s.replace('else if(action==="x!")add("!");else if(action==="percent")add("%");else if(action==="," )add(",");',
              'else if(action==="," )add(",");', 1)

p.write_text(s, encoding='utf-8')
print('F-789SGA Batch 1 patch is applied/idempotent')
