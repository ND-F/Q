import json, re
from collections import defaultdict
S=json.load(open('streams.json'))
EXCLUDE={'1066','560','3553','596','4615','1065'}
def digits_key(h): return ''.join(re.findall(r'\d', re.sub(r'^\s*\d+\.\s*','',h)))
def is_titled(h, ar):
    h=re.sub(r'^\s*\d+\.\s*','',h).strip()
    return not (re.match(r'^(Inv\.|No\.)',h) or re.match(r'^(رقما|رقم|أرقام)',h))
# ---------- تقسيم السطور لفقرات وحقول ----------
EN_START=[('dims',r'^(?:[\d/\-, ]+\s*[–-]\s*)?(?:W|H|D|L|Th|Diam|Max\.?\s*\w*|Length|Width|Height|Depth|Thickness)\s*[\.:]'),
          ('from',r'^(?:From|Found|Probably from|Possibly from|Likely from|Said to|Recovered|Originally from|Excavated)'),
          ('reg',r'^Registered'),
          ('acq',r'^(?:Submitted|Purchased|Gift|Donated|Acquired|Transferred|Bequeathed|Confiscated|Bought|Presented)')]
AR_START=[('dims',r'^(?:[\d/\-، ]+\s*[–-]\s*)?(?:العرض|عرض|الطول|الارتفاع|العمق|القطر|السمك|السُمك|أقصى)'),
          ('from',r'^(?:من |عثر|يحتمل(?! أن يرجع)|ربما من|غالبا من|يرجح أنه من|استخرج|مستخرج|أصله من)'),
          ('reg',r'^(?:سجل|سجلت|سجلا|مسجل|مسجلة)'),
          ('acq',r'^(?:مقدم|مقدمة|اقتن|اشتر|مشتر|مشترا|نقلت|منقولة|إهداء|هدية|منقول|نقل|أهدى|أهديت|مهداة|مهدى)')]
def paragraphs(lines, ar=False):
    paras=[];cur=[];prev=None
    for l in lines:
        if prev is not None and ((l['page']==prev['page'] and l['y']-prev['y']>14.5) or (l['page']==prev['page'] and l['y']<prev['y']) or (l['page']!=prev['page'] and abs(l['x0']-prev['x0'])>20 and abs(l['x1']-prev['x1'])>20)):
            paras.append(cur);cur=[]
        cur.append(l);prev=l
    if cur: paras.append(cur)
    return paras
def join_lines(ls):
    s=''
    for l in ls:
        t=l['t'].strip()
        if not s: s=t
        elif s.endswith('-') and re.match(r'[a-z]',t) and not re.search(r'\d-$',s): s=s+t   # كلمة مكسورة بشرطة
        elif re.search(r'\d[-–]$',s) and re.match(r'\d',t): s=s+t   # مدى أرقام مكسور: 1284- 85
        else: s=s+' '+t
    return re.sub(r'\s+',' ',s).strip()
DATE_EN=re.compile(r'^(?:(?:probably|possibly|likely|late|early|mid|c\.)\s+)?(?:Fatimid|Mamluk|Bahri|Burji|Ottoman|Ayyubid|Tulunid|Abbasid|Umayyad|Byzantine|Coptic|Khedival|Early Islamic|Islamic|Obverse|Reverse|Ikhshidid|Circassian|Mamluk|Modern|Pre-Islamic|\d+(?:st|nd|rd|th)\b|\d{3,4}\s*(?:AH|CE))', re.I)
DATE_AR=re.compile(r'^(?:يحتمل أن يرجع|فاطمى|مملوكى|عثمانى|أيوبى|طولونى|عباسى|أموى|بيزنطى|قبطى|خديوى|إخشيدى|الإخشيدى|العصر|القرن|حوالى|أواخر|بداية|بدايات|منتصف|الوجه|مؤرخ|مؤرخة|ربما|يرجح|غالبا)')
def classify(para, ar):
    starts=AR_START if ar else EN_START
    fields=[]  # [kind, [lines]]
    for i,l in enumerate(para):
        t=l['t'].strip(); kind=None
        for k,rx in starts:
            if re.match(rx,t): kind=k;break
        prev=para[i-1] if i else None
        if kind is None and fields:
            cur=fields[-1][0]; pt=prev['t'].rstrip()
            if cur=='desc':
                fields[-1][1].append(l); continue
            if not ar:
                if DATE_EN.match(t) and not re.match(r'^\d',t): fields.append(['date',[l]]); continue
                if re.match(r'^(A|An|The|This|These|Part|Section|Fragment)\s+[a-z]',t) and len(t)>25 and cur!='from':
                    fields.append(['desc',[l]]); continue
                if re.match(r'^(AH|CE|BH|BCE|[a-z0-9(\[“"‘])',t):   # تكملة سطر
                    fields[-1][1].append(l); continue
                if DATE_EN.match(t): fields.append(['date',[l]]); continue
                if pt.endswith('.') and re.match(r'^[A-Z]',t) and len(t)>25:
                    fields.append(['desc',[l]]); continue
                fields[-1][1].append(l); continue
            else:
                if DATE_AR.match(t) and cur!='date': fields.append(['date',[l]]); continue
                if cur=='date' and re.match(r'^الوجه',t): fields.append(['date',[l]]); continue
                fields[-1][1].append(l); continue
        fields.append([kind or 'date',[l]])
    return [(k,join_lines(ls)) for k,ls in fields]
def is_meta_para(para, ar):
    starts=AR_START if ar else EN_START
    return any(re.match(rx,para[0]['t'].strip()) for _,rx in starts)
def parse_entry(e, ar):
    global EDGE
    lines=e['lines']
    if lines:
        # شيل التعليقات اللى برا عمود المدخل (تعليقات الصور والرسومات)
        from collections import Counter
        kept=[]
        for pg in sorted({l['page'] for l in lines}):
            pl=[l for l in lines if l['page']==pg]
            # تجميع السطور فى أعمدة حسب بداية السطر (x0 للإنجليزى، x1 للعربى)
            cols=[]
            for l in sorted(pl, key=lambda l:(-(l['x1']) if ar else l['x0'])):
                a=l['x1'] if ar else l['x0']
                for c in cols:
                    if abs(c['a']-a)<20: c['ls'].append(l); break
                else: cols.append(dict(a=a, ls=[l]))
            main=max(cols, key=lambda c:len(c['ls']))
            body=[c for c in cols if c is main or len(c['ls'])>=3]
            body.sort(key=lambda c:(-c['a'] if ar else c['a']))   # العمود الأول: شمال للإنجليزى، يمين للعربى
            for c in body: kept.extend(sorted(c['ls'], key=lambda l:l['y']))
        lines=kept
        lines=[l for l in lines if not re.match(r'^(Line drawing|Top view|Detail|Drawing|Schematic|Left:|Right:|رسم|منظر علوى|تفصيل|تفصيلة)',l['t'].strip())]
    if lines: EDGE=min(l['x0'] for l in lines) if ar else max(l['x1'] for l in lines)
    paras=paragraphs(lines, ar)
    out=defaultdict(list); desc=[]
    for i,p in enumerate(paras):
        if i==0 and is_meta_para(p, ar):
            for k,v in classify(p, ar):
                if k=='desc': desc.append(v)
                else: out[k].append(v)
        else:
            t=join_lines(p)
            if desc and not re.search(r'[.!?»”"\)]$', desc[-1]): desc[-1]=desc[-1]+' '+t   # جملة مكملة فى العمود التالى
            elif re.match(r'^[“"«]|^\(\)', t): continue          # نص نقش (ترجمة كتابة على قطعة تانية جنبها)
            elif ar and len(t)<90 and (re.search(r'رقم تسجيل|تسجيل \d|^(صورة|رسم|تفصيلة|منظر)', t) or re.fullmatch(r'[\d٠-٩,.،\s]+', t)): continue   # تعليق صورة
            elif not ar and (re.fullmatch(r'[\d,.\s]+', t) or re.match(r'^(Black-and-white photograph|Photograph|Image courtesy|Line drawing|Detail|Top view|Drawing)', t)): continue
            elif not ar and re.match(r'^[a-z]', t): continue      # بقية تعليق صورة
            else: desc.append(t)
    out['desc']=desc
    return out
def split_head(h, ar):
    h=re.sub(r'^\s*(\d+)\.\s*','',h).strip()
    if ar:
        m=re.match(r'^(.*?)[،,]?\s*(?:رقما|رقم|أرقام)\s*التسجيل\s*[:.]?\s*(.*)$',h)
    else:
        m=re.match(r'^(.*?)[,]?\s*(?:Inv\.)?\s*Nos?\.\s*(.*)$',h)
    if not m: return h,''
    title=m.group(1).strip().rstrip('،,').strip(); inv=m.group(2).strip().rstrip('.').strip()
    if title.endswith('Inv.'): title=title[:-4].rstrip(', ')
    return title, inv
def catno(h):
    m=re.match(r'^\s*(\d+)\.',h); return m.group(1) if m else ''
# ---------- الربط وتمرير السياق للمجموعات ----------
def richness(r): return sum(len(x) for v in r['f'].values() for x in v)
def put(res, k, r):
    # الكتالوج بيكرر القطعة (تعليق جنب الصورة + المدخل الكامل) → خلّى الأغنى، واحتفظ برقم الكتالوج والمجموعة
    old=res.get(k)
    if old is None: res[k]=r; return
    keep, other = (r, old) if richness(r) > richness(old) else (old, r)
    keep['catno']=keep['catno'] or other['catno']; keep['group']=keep['group'] or other['group']
    keep['is_parent']=keep.get('is_parent') or other.get('is_parent')
    if not keep['title']: keep['title']=other['title']
    res[k]=keep
def build_side(E, ar):
    res={}; ctx=None; parent=None
    for e in E:
        has_num=bool(re.search(r'\d',e['head']))
        if not has_num:
            ctx=dict(title=e['head'], fields=parse_entry(e, ar), sec=e['sec']); parent=None; continue
        titled=is_titled(e['head'], ar)
        f=parse_entry(e, ar); title,inv=split_head(e['head'], ar)
        if titled:
            parent=dict(title=title, fields=f, key=digits_key(e['head']))
            put(res, digits_key(e['head']), dict(title=title, inv=inv, f=f, sec=e['sec'], page=e['page'], catno=catno(e['head']), group=None))
        else:
            g=parent or ctx
            if parent: res.get(parent['key'],{})['is_parent']=True
            put(res, digits_key(e['head']), dict(title=(g or {}).get('title',''), inv=inv, f=f, sec=e['sec'], page=e['page'], catno=catno(e['head']), group=g))
    return res
EN=build_side(S['EN'],False); AR=build_side(S['AR'],True)
print(len(EN),len(AR), set(EN)-set(AR), set(AR)-set(EN))
json.dump(dict(EN=EN,AR=AR), open('sides.json','w'), ensure_ascii=False)
