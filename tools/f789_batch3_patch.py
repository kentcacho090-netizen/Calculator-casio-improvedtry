from pathlib import Path

p = Path('index.html')
s = p.read_text()

def rep(old, new):
    global s
    if old not in s:
        raise SystemExit(f'missing expected source fragment: {old[:100]}')
    s = s.replace(old, new, 1)

rep('data-action="rcl"><span class="sub o">STO</span>RCL',
    'data-action="rcl" data-shift="sto"><span class="sub o">STO</span>RCL')
rep('data-v="+"><span class="sub o">Pol(</span>+',
    'data-v="+" data-shift="pol"><span class="sub o">Pol(</span>+')
rep('data-v="−"><span class="sub o">Rec(</span>−',
    'data-v="−" data-shift="rec"><span class="sub o">Rec(</span>−')
rep('let expr="",ans=0,memory=0,shift=false,alpha=false,mode="COMP",',
    'let expr="",ans=0,memory=0,shift=false,alpha=false,storePending=false,rclPending=false,dmsStage=0,mode="COMP",')
rep('$("status").textContent=(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+',
    '$("status").textContent=(storePending?"STO ":"")+(rclPending?"RCL ":"")+(shift?"S ":"")+(alpha?"A ":"")+(memory!==0?"M ":"")+')
rep('function transform(s){\n s=s.replace(/(\\d+(?:\\.\\d+)?)P',
    'function dmsToDecimal(s){return s.replace(/(\\d+(?:\\.\\d+)?)°(?:\\s*(\\d+(?:\\.\\d+)?)′)?(?:\\s*(\\d+(?:\\.\\d+)?)″)?/g,(m,d,mi="0",se="0")=>String(+d+(+mi)/60+(+se)/3600))}\nfunction transform(s){\n s=dmsToDecimal(s);\n s=s.replace(/(\\d+(?:\\.\\d+)?)P')
rep('else if(action==="npr")add("P");else if(action==="ncr")add("C");else if(action==="x!")',
    'else if(action==="npr")add("P");else if(action==="ncr")add("C");else if(action==="sto"){storePending=true;rclPending=false;render()}else if(action==="pol")add("Pol(");else if(action==="rec")add("Rec(");else if(action==="x!")')
rep('else if(action==="sum")$("result").textContent="Σ";else if(action==="drg")$("result").textContent="DRG▶";',
    'else if(action==="sum")$("result").textContent="Σ";else if(action==="drg"){const v=ans,old=angle,next=old==="DEG"?"RAD":old==="RAD"?"GRAD":"DEG";const conv=old==="DEG"?v*Math.PI/180:old==="RAD"?v*200/Math.PI:v*180/200;angle=next;ans=conv;$("result").textContent=formatNumber(conv);render()};')
rep('else if(a==="exp")add("E");else if(a==="dms")add("°′″");',
    'else if(a==="exp")add("E");else if(a==="dms"){const mark=dmsStage===0?"°":dmsStage===1?"′":"″";add(mark);dmsStage=(dmsStage+1)%3;}')
rep('function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;',
    'function pressButton(b){\n const alphaVal=b.dataset.alpha, shiftVal=b.dataset.shift;\n if(storePending){if(alphaVal!==undefined){V[alphaVal]=ans;storePending=false;alpha=false;render();return}storePending=false;render()}\n if(rclPending){if(alphaVal!==undefined){const v=V[alphaVal]??0;rclPending=false;alpha=false;add(String(v));return}rclPending=false;render()}')
rep('else if(a==="rcl")add(String(memory));',
    'else if(a==="rcl"){rclPending=true;render()}')
rep('s=s.replace(/(\\d+(?:\\.\\d+)?)C(\\d+(?:\\.\\d+)?)/g,(m,n,r)=>"ncr("+n+","+r+")");',
    's=s.replace(/(\\d+(?:\\.\\d+)?)C(\\d+(?:\\.\\d+)?)/g,(m,n,r)=>"ncr("+n+","+r+")).replace(/Pol\\(([^,]+),([^\\)]+)\\)/g,(m,x,y)=>"Math.hypot("+x+","+y+")).replace(/Rec\\(([^,]+),([^\\)]+)\\)/g,(m,r,t)=>"("+r+"*Math.cos("+toRadExpr(t)+"))");')
p.write_text(s)
print('Batch 3 patch applied')
