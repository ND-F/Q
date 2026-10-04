import pymupdf, re, json, unicodedata
ALEFS='اأإآ'
def is_ar(ch): return '؀'<=ch<='ۿ' or 'ﭐ'<=ch<='﻿'
def is_mark(ch): return unicodedata.category(ch)=='Mn'
def is_ltr(ch): return ch.isdigit() or ('A'<=ch<='Z') or ('a'<=ch<='z')
MIRROR={}
def visual_to_logical(chars):
    # chars: list of (ch, x0, x1) for one Arabic line
    items=[]
    chars=[c for c in chars if not is_mark(c[0])]
    for i,(ch,x0,x1) in enumerate(chars):
        key=x0
        if x1-x0<0.05:
            if ch in ALEFS:
                # ألف الـ lam-alef: عرضها صفر على الحافة اليمين للام → حطها شمال اللام
                lam=[c for c in chars if c[0]=='ل' and abs(c[2]-x0)<0.05]
                key=(lam[0][1] if lam else x0)-0.002
            else:
                key=x0-0.001
        items.append((key,i,ch))
    items.sort()
    vis=[ch for _,_,ch in items]
    rev=vis[::-1]
    # رجّع الأرقام/اللاتيني لاتجاهها (مع الفواصل اللي بينهم)
    out=[];i=0;n=len(rev)
    while i<n:
        if is_ltr(rev[i]):
            j=i
            while j+1<n and (is_ltr(rev[j+1]) or (rev[j+1] in '.,' and j+2<n and is_ltr(rev[j+2])) or (rev[j+1]==' ' and j+2<n and is_ltr(rev[j+2]) and not rev[j+2].isdigit() and not rev[i].isdigit())):
                j+=1
            out.extend(rev[i:j+1][::-1]); i=j+1
        else:
            out.append(MIRROR.get(rev[i],rev[i])); i+=1
    s=''.join(out)
    s=''.join(ch for ch in s if not is_mark(ch) and ord(ch) not in (0xfffd,) and unicodedata.category(ch) not in ('Co','Cn','Cf'))
    return re.sub(r'\s+',' ',s).strip()
def page_lines(pg):
    d=pg.get_text('rawdict'); res=[]
    for b in d['blocks']:
        for l in b.get('lines',[]):
            chars=[]
            for s in l['spans']:
                bold=s['font'].endswith('Bold')
                for c in s['chars']: chars.append((c['c'],c['bbox'][0],c['bbox'][2],bold))
            if not chars: continue
            # قسّم السطر عند فجوة أفقية كبيرة (عمودين نص على نفس الارتفاع)
            order=sorted(range(len(chars)), key=lambda i:chars[i][1])
            groups=[[order[0]]]; right=chars[order[0]][2]
            for i in order[1:]:
                if chars[i][1]-right>14 and chars[i][0].strip(): groups.append([i])
                else: groups[-1].append(i)
                right=max(right, chars[i][2])
            for g in groups:
                g=sorted(g)  # ترتيب mupdf الأصلى
                seg=[chars[i] for i in g]
                txt=''.join(c[0] for c in seg)
                if not txt.strip(): continue
                na=sum(1 for c in txt if is_ar(c)); nl=sum(1 for c in txt if ('A'<=c<='Z') or ('a'<=c<='z'))
                ar=na>0 and na>=nl   # لغة السطر بالأغلبية (سطر إنجليزى فيه كلمة عربى يفضل إنجليزى)
                t=visual_to_logical([c[:3] for c in seg]) if ar else re.sub(r'\s+',' ',txt).strip()
                nb=sum(1 for c in seg if c[0].strip() and c[3]); nt=sum(1 for c in seg if c[0].strip())
                xs=[c[1] for c in seg]+[c[2] for c in seg]
                if t: res.append(dict(t=t, ar=ar, x0=min(xs), x1=max(xs), y=round(l['bbox'][1],1), bold=nt>0 and nb>=0.6*nt))
    return res
if __name__=='__main__':
    import sys
    doc=pymupdf.open('cat.pdf')
    if len(sys.argv)>1:
        for pn in map(int,sys.argv[1:]):
            for l in sorted(page_lines(doc[pn-1]), key=lambda l:(l['y'],l['x0'])):
                if l['ar']: print(f"{l['y']:6} {'B' if l['bold'] else ' '} {l['t']}")
    else:
        allp=[dict(page=i+1, lines=page_lines(pg)) for i,pg in enumerate(doc)]
        json.dump(allp, open('pages2.json','w'), ensure_ascii=False); print(len(allp))
