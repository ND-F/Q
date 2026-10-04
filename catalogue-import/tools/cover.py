import json,re
txt=open('idx.txt').read(); idx=set(re.findall(r'(\d+(?:/\d+)?)\s*\.{3,}', txt))
D=json.load(open('sides.json'))
def expand(inv):
    out=set(); base=None
    for part in re.split(r',|،| and | و', inv.replace('و',' و')):
        part=part.strip()
        m=re.match(r'^(\d+)/(\d+)(?:-(\d+))?$',part)
        if m:
            base=m.group(1); a=int(m.group(2)); b=int(m.group(3) or a); out|={f"{base}/{i}" for i in range(a,b+1)}; continue
        m=re.match(r'^(\d+)(?:-(\d+))?$',part)
        if m and base and len(m.group(1))<=2:
            a=int(m.group(1)); b=int(m.group(2) or a); out|={f"{base}/{i}" for i in range(a,b+1)}; continue
        if m: out.add(m.group(1)); base=None
    return out
have=set()
for k,r in D['EN'].items(): have|=expand(r['inv'])
print('index',len(idx),'missing:', sorted(idx-have), 'extra:', sorted(have-idx))
