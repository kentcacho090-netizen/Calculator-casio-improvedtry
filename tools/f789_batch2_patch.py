from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def add_attr_to_button(marker: str, attr: str):
    global s
    pat = re.compile(r'(<button\b(?=[^>]*' + re.escape(marker) + r')[^>]*)(>)')
    m = pat.search(s)
    if not m:
        raise SystemExit(f'missing expected button: {marker}')
    tag = m.group(1)
    if attr not in tag:
        s = s[:m.start(1)] + tag + ' ' + attr + s[m.end(1):]

for marker, attr in [
    ('data-action="log"', 'data-shift="pow10"'),
    ('data-action="ln"', 'data-shift="powe"'),
    ('class="k num op" data-v="×"', 'data-shift="npr"'),
    ('class="k num op" data-v="÷"', 'data-shift="ncr"'),
]:
    add_attr_to_button(marker, attr)

# Normal EXP is scientific-notation entry. Alpha+EXP remains the constant e.
s = s.replace('class="k fn" data-v="e" data-shift="sum"><span class="sub g">Σ</span>EXP',
              'class="k fn" data-action="exp" data-shift="sum"><span class="sub g">Σ</span>EXP', 1)
s = s.replace('class="k num" data-v="e" data-shift="pi" data-alpha="e"><span class="sub o">π</span>',
              'class="k num" data-action="exp" data-shift="pi" data-alpha="e"><span class="sub o">π</span>', 1)

anchor = 'else if(a==="neg")add("−");else if(a==="dms")add("°′″");'
replacement = 'else if(a==="neg")add("−");else if(a==="exp")add("E");else if(a==="dms")add("°′″");'
if anchor in s and 'else if(a==="exp")add("E")' not in s:
    s = s.replace(anchor, replacement, 1)

# Shift 10^n/e^n and the infix nPr/nCr operators shown on the physical keys.
anchor = 'else if(action==="fraction")$("result").textContent=fraction(ans);'
replacement = '''else if(action==="fraction")$("result").textContent=fraction(ans);
 else if(action==="pow10")add("10^(");else if(action==="powe")add("e^(");
 else if(action==="npr")add("P");else if(action==="ncr")add("C");'''
if anchor in s and 'action==="pow10"' not in s:
    s = s.replace(anchor, replacement, 1)

# EXP input such as 4 EXP 75 becomes 4*10^75 during evaluation; the Alpha e
# constant is mapped to Math.E.
old = 's=s.replace(/E/g,"e");'
new = 's=s.replace(/(\\d+(?:\\.\\d+)?)[Ee]([+\\-]?\\d+)/g,"($1*10**($2))");s=s.replace(/\\be\\b/g,"Math.E");'
if old in s and '10**($2)' not in s:
    s = s.replace(old, new, 1)

# Convert 10P3 and 5C2 to the existing npr/ncr helpers.
old = 's=s.replace(/(\\d+(?:\\.\\d+)?)!/g,(m,n)=>"fact("+n+")");'
new = '''s=s.replace(/(\\d+(?:\\.\\d+)?)P(\\d+(?:\\.\\d+)?)/g,(m,n,r)=>"npr("+n+","+r+")");
 s=s.replace(/(\\d+(?:\\.\\d+)?)C(\\d+(?:\\.\\d+)?)/g,(m,n,r)=>"ncr("+n+","+r+")");
 s=s.replace(/(\\d+(?:\\.\\d+)?)!/g,(m,n)=>"fact("+n+")");'''
if old in s and '?)P(\\d+' not in s:
    s = s.replace(old, new, 1)

old = 'return Function("fact","Math","return ("+js+")")(fact,Math);'
new = 'return Function("fact","Math","npr","ncr","return ("+js+")")(fact,Math,npr,ncr);'
if old in s and '"npr","ncr"' not in s:
    s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
print('F-789SGA Batch 2 patch applied')
