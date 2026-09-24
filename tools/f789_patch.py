from pathlib import Path
import re

# Batch 1: repair only already-present Shift dispatch and the existing key-input
# path. Do not add a new calculator feature until these basic mappings are valid.
p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Make Shift mappings idempotently, without depending on the exact span layout.
def ensure_action_shift(action, shift_value):
    pat = re.compile(r'(<button\b(?=[^>]*\bdata-action="' + re.escape(action) + r'")[^>]*)(>)')
    def repl(m):
        tag = m.group(1)
        if 'data-shift=' in tag:
            return m.group(0)
        return tag + f' data-shift="{shift_value}"' + m.group(2)
    out, n = pat.subn(repl, s, count=1)
    if n == 0:
        raise SystemExit(f'missing expected data-action button: {action}')
    return out

for action, shift_value in [('inv','x!'), ('abs','percent'), ('sin','asin'), ('cos','acos'), ('tan','atan')]:
    s = ensure_action_shift(action, shift_value)

# The first parenthesis key is the physical Shift-percent key.
paren = re.compile(r'(<button\b(?=[^>]*\bdata-v="\(")[^>]*)(>)')
def paren_repl(m):
    tag = m.group(1)
    if 'data-shift=' in tag:
        return m.group(0)
    return tag + ' data-shift="percent"' + m.group(2)
s, n = paren.subn(paren_repl, s, count=1)
if n == 0:
    raise SystemExit('missing expected opening-parenthesis key')

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
# but never consumed ordinary data-v buttons (digits/operators). Preserve
# Shift/Alpha dispatch first, then add the button's normal value.
old = 'else if(a==="rcl")add(String(memory));else if(a==="abs")add("Abs(");else if(a==="mplus"){memory+=ans;render()}\n}'
new = 'else if(a==="rcl")add(String(memory));else if(a==="abs")add("Abs(");else if(a==="mplus"){memory+=ans;render()}\n else if(a===undefined && b.dataset.v!==undefined)add(b.dataset.v);\n}'
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('missing data-v dispatch anchor and patched form')

p.write_text(s, encoding='utf-8')
print('F-789SGA Batch 1 patch is applied/idempotent')
