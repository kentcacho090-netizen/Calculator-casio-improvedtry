from pathlib import Path

# Batch 1: repair only already-present Shift dispatch and the existing key-input
# path. Do not add a new calculator feature until these basic mappings are valid.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = {
    '<button class="k fn" data-action="inv"><span class="sub o">x!</span>x⁻¹</button>':
    '<button class="k fn" data-action="inv" data-shift="x!"><span class="sub o">x!</span>x⁻¹</button>',
    '<button class="k fn" data-action="abs"><span class="sub o">%</span>Abs</button>':
    '<button class="k fn" data-action="abs" data-shift="percent"><span class="sub o">%</span>Abs</button>',
    '<button class="k fn" data-v="("><span class="sub o">%</span>(</button>':
    '<button class="k fn" data-v="(" data-shift="percent"><span class="sub o">%</span>(</button>',
    '<button class="k fn" data-action="sin"><span class="sub o">sin⁻¹</span>sin</button>':
    '<button class="k fn" data-action="sin" data-shift="asin"><span class="sub o">sin⁻¹</span>sin</button>',
    '<button class="k fn" data-action="cos"><span class="sub o">cos⁻¹</span>cos</button>':
    '<button class="k fn" data-action="cos" data-shift="acos"><span class="sub o">cos⁻¹</span>cos</button>',
    '<button class="k fn" data-action="tan"><span class="sub o">tan⁻¹</span>tan</button>':
    '<button class="k fn" data-action="tan" data-shift="atan"><span class="sub o">tan⁻¹</span>tan</button>',
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

# Critical existing-key bug: the old pressButton() handled data-action buttons,
# but never consumed ordinary data-v buttons (digits/operators). That made even
# 2+3 appear to do nothing. Preserve Shift/Alpha dispatch first, then add the
# button's normal value when no data-action is present.
old = 'else if(a==="rcl")add(String(memory));else if(a==="abs")add("Abs(");else if(a==="mplus"){memory+=ans;render()}\n}'
new = 'else if(a==="rcl")add(String(memory));else if(a==="abs")add("Abs(");else if(a==="mplus"){memory+=ans;render()}\n else if(a===undefined && b.dataset.v!==undefined)add(b.dataset.v);\n}'
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('missing data-v dispatch anchor and patched form')

p.write_text(s, encoding='utf-8')
print('F-789SGA Batch 1 patch is applied/idempotent')
