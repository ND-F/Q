import json, re
from collections import defaultdict
P=json.load(open('pages2.json'))
FOOT_Y=565
NUM_ONLY=re.compile(r'^(\d+[a-z]?\.|\.\d+[a-z]?|\d{2})$')
def has_letters(t): return re.search(r'[A-Za-z؀-ۿ]',t) is not None
def section(page):
    # الفوتر: سطر إنجليزى + سطر عربى (بعد تقسيم الفجوات بقوا سطرين منفصلين)
    foot=[l for l in page['lines'] if l['y']>FOOT_Y and re.search(r'[A-Za-z\u0600-\u06ff]',l['t'])]
    en=' '.join(l['t'] for l in sorted(foot,key=lambda l:l['x0']) if not l['ar']).strip()
    ar=' '.join(l['t'] for l in sorted(foot,key=lambda l:-l['x1']) if l['ar']).strip()
    # لو اتجمعوا فى سطر واحد مختلط
    if not en or not ar:
        for l in foot:
            if re.search('[A-Za-z]',l['t']) and re.search('[\u0600-\u06ff]',l['t']):
                en=en or ''.join(re.findall(r"[A-Za-z][A-Za-z ,&\-’'—]*",l['t'])).strip()
                ar=ar or re.sub(r"[A-Za-z][A-Za-z ,&\-’'—]*",'',l['t']).strip()
    return re.sub(r'\s+',' ',en), re.sub(r'\s+',' ',ar)
def join_fragments(ls):
    # أجزاء نفس السطر (نص مضبوط justified) → سطر واحد
    ls=sorted(ls, key=lambda l:(round(l['y']), l['x0']))
    out=[]
    for l in ls:
        o=out[-1] if out else None
        if o and abs(o['y']-l['y'])<1 and o['ar']==l['ar'] and o['bold']==l['bold'] and 0<=l['x0']-o['x1']<15 and (o['bold'] or min(o['x1']-o['x0'], l['x1']-l['x0'])<120):
            if l['ar']: o['t']=l['t']+' '+o['t']
            else: o['t']=o['t']+' '+l['t']
            o['x1']=l['x1']; continue
        out.append(dict(l))
    return out
def page_streams(p):
    ls=[dict(l) for l in join_fragments(p['lines']) if l['y']<=FOOT_Y and not NUM_ONLY.match(l['t'].strip())]
    heads=[l for l in ls if l['bold'] and has_letters(l['t'])]
    out={True:[],False:[]}
    for l in ls:
        if not has_letters(l['t']):
            # سطر أرقام بس: ألحقه بأقرب عنوان بولد فوقه في نفس العمود
            cand=[h for h in heads if 0<l['y']-h['y']<16 and min(h['x1'],l['x1'])-max(h['x0'],l['x0'])>-5]
            if l['bold'] and cand:
                h=max(cand,key=lambda h:h['y']); nt=l['t'].strip()
                if h['ar']: nt=re.sub(r'(\d+)/(\d+)', lambda m: m.group(2)+'/'+m.group(1), nt)
                h['t']=h['t']+' '+nt; continue
            l['ar']= l['x0'] > (p.get('mid') or 290)
        out[l['ar']].append(l)
    return out
def stream(lang_ar, pages):
    entries=[]; cur=None
    for p in pages:
        sec=section(p); ls=page_streams(p)[lang_ar]
        bh=[l for l in ls if l['bold']]
        split=None
        for a in bh:
            for b in bh:
                if abs(a['y']-b['y'])<6 and b['x0']-a['x0']>80:
                    split=(a['x0']+b['x0'])/2; sy=min(a['y'],b['y']) if split is None or 'sy' not in dir() else min(sy,a['y'],b['y'])
        if split is None:
            ls.sort(key=lambda l:(l['y'], -l['x1'] if lang_ar else l['x0']))
        else:  # عمودين جنب بعض: اقرا كل عمود لوحده (الإنجليزى شمال الأول، العربى يمين الأول)
            ls.sort(key=lambda l:((0 if l['y']<sy-2 else (1 if ((l['x0']>=split) if lang_ar else (l['x0']<split)) else 2)), l['y']))
        for l in ls:
            t=l['t'].strip()
            if l['bold']:
                if cur is not None and not cur['lines'] and cur['page']==p['page'] and not re.search(r'\d',cur['head']) :
                    pass
                cur=dict(page=p['page'], head=t, lines=[], sec=sec, y=l['y']); entries.append(cur); continue
            if cur is not None and cur['page']>=p['page']-1:
                cur['lines'].append(dict(t=t,y=l['y'],x0=l['x0'],x1=l['x1'],page=p['page']))
    return entries
def merge_split_heads(E, ar):
    # عنوان مكسور على كذا سطر بولد ورا بعض (من غير سطور بينهم) → عنوان واحد، والأرقام في الآخر
    out=[]
    for e in E:
        if out and not out[-1]['lines'] and out[-1]['page']==e['page'] and e.get('y',0)-out[-1].get('y',0)>2:
            parts=(out[-1]['head']+' '+e['head']).split()
            nums=[t for t in parts if re.fullmatch(r'[\d/\-–]+[،,]?',t)]
            words=[t for t in parts if t not in nums]
            out[-1]['head']=' '.join(words+nums); out[-1]['lines']=e['lines']; continue
        out.append(e)
    return out
pages=[p for p in P if 38<=p['page']<=285]
EN=merge_split_heads(stream(False,pages),False); AR=merge_split_heads(stream(True,pages),True)
def inv_tokens(h):
    h=re.sub(r'^\s*\d+\.\s*','',h)
    return ''.join(re.findall(r'\d',h))
ar=defaultdict(list)
for e in AR:
    if re.search(r'\d',e['head']): ar[inv_tokens(e['head'])].append(e)
pairs=[];un=[]
for e in EN:
    if not re.search(r'\d',e['head']): continue
    k=inv_tokens(e['head'])
    if ar.get(k): pairs.append((e,ar[k].pop(0)))
    else: un.append(e)
print('EN heads',len(EN),'AR heads',len(AR),'pairs',len(pairs),'unmatched EN',len(un),'unmatched AR',sum(len(v) for v in ar.values()))
for e in un: print(' EN',e['page'],e['head'][:80])
for v in ar.values():
    for e in v: print(' AR',e['page'],e['head'][:80])
json.dump(dict(EN=EN,AR=AR,pairs=pairs), open('streams.json','w'), ensure_ascii=False)
