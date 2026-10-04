import json, re
D=json.load(open('sides.json'))
EXCLUDE={'1066','560','3553','596','4615','1065'}
DOMAIN='https://mia.nadimfoundation.org/q'
COLS="id inventory_number title_en title_ar from_en from_ar desc_en desc_ar date_en date_ar dimensions_en dimensions_ar section_en section_ar hall_en hall_ar material_en material_ar info_en1 info_ar1 info_en2 info_ar2 info_en3 info_ar3 info_en4 info_ar4 info_en5 info_ar5 video_url dsc_en1 dsc_ar1 dsc_en2 dsc_ar2 dsc_en3 dsc_ar3 dsc_en4 dsc_ar4 dsc_en5 dsc_ar5 reel_url reel_url2 reel_url3 video_url2 video_url3 LINK QR".split()
EXTRA="registered_en registered_ar acquisition_en acquisition_ar catalogue_no catalogue_page".split()
AR_DIG=str.maketrans('0123456789','٠١٢٣٤٥٦٧٨٩')
def ar_digits(s): return re.sub(r'(?<=\d)\.(?=\d)','٫',s).translate(AR_DIG) if s else s
SING_EN={'Single-Sided Combs':'Single-Sided Comb','Double-Sided Combs':'Double-Sided Comb','Long Combs':'Long Comb'}
SING_AR={'أمشاط ذات أسنان من جانب واحد':'مشط ذو أسنان من جانب واحد','أمشاط ذات أسنان من الجانبين':'مشط ذو أسنان من الجانبين','أمشاط طويلة':'مشط طويل'}
def make_id(inv):
    return re.sub(r'-+','-',re.sub(r'\s*(?:,|،| and )\s*|/', '-', inv.strip())).strip('-')
def val(r, k, sep='\n'):
    v=r['f'].get(k) or []
    if not v and r.get('group'): v=r['group']['fields'].get(k) or []
    return sep.join(v)
rows=[]; skipped=[]
for key, en in D['EN'].items():
    ar=D['AR'][key]
    if en.get('is_parent') or ar.get('is_parent'): skipped.append((en['inv'],'group heading (its items are separate rows)')); continue
    rid=make_id(en['inv'])
    if rid in EXCLUDE: skipped.append((en['inv'],'already in the sheet (1-6)')); continue
    t_en=SING_EN.get(en['title'],en['title']) if en.get('group') else en['title']
    t_ar=SING_AR.get(ar['title'],ar['title']) if ar.get('group') else ar['title']
    r={c:'' for c in COLS+EXTRA}
    r.update(id=rid, inventory_number='Inv. no. '+en['inv'].replace(' and ',', '),
        title_en=t_en, title_ar=t_ar,
        from_en=val(en,'from'), from_ar=ar_digits(val(ar,'from')),
        desc_en=val(en,'desc','\n\n'), desc_ar=ar_digits(val(ar,'desc','\n\n')),
        date_en=val(en,'date'), date_ar=ar_digits(val(ar,'date')),
        dimensions_en=val(en,'dims'), dimensions_ar=ar_digits(val(ar,'dims')),
        section_en=en['sec'][0], section_ar=en['sec'][1],
        LINK=DOMAIN+rid,
        registered_en=val(en,'reg'), registered_ar=ar_digits(val(ar,'reg')),
        acquisition_en=val(en,'acq'), acquisition_ar=ar_digits(val(ar,'acq')),
        catalogue_no=en['catno'] or ar['catno'], catalogue_page=str(en['page']))
    rows.append(r)
# تصحيحات يدوية من صور الصفحات (تخطيط الصفحة مختلط بنص مقال)
MANUAL={
 '18860-1': dict(title_ar='مشط بجانبين', dimensions_ar='العرض: ٦٫٩ سم، الطول: ١٩٫٧ سم',
    desc_ar='مشط خشبى طويل بنقوش بارزة من زخارف الحلقة والنقطة على أحد الوجهين مرتبة على شكل خماسى متقاطع وتتخللها حلقات ونقاط أصغر حجما، بينما جاء الوجه الآخر خاليا من الزخرفة.'),
 '6120-6': dict(
    desc_en='Convex mirror set within a rounded wooden frame with a small handle at the back; used to make images appear smaller. It was donated alongside Nos. 6120/2, 4-5, by the Makufiyas brothers. Though its findspot remains unknown, its grouping with a set of single-sided combs hints at the lived domestic context these objects once shared.',
    desc_ar='تجعل صورة الناظر إليها تبدو أصغر. أهديت هذه القطعة، إلى جانب القطع أرقام ٦١٢٠/٢، ٤-٥، من قبل الإخوة مكوفياس. وعلى الرغم من أن موقع اكتشافها لا يزال مجهولا، إلا أن وجودها ضمن مجموعة من الأمشاط ذات الأسنان من جهة واحدة يلمح إلى السياق المعيشى المنزلى الذى جمع هذه القطع يوما ما.'),
 '37773': dict(dimensions_en='W: 3.8 cm; H: 6.5 cm', from_en='Recovered from the felonies of el-Nuzha (Case No. 9224/92)',
    registered_en='Registered July 15, 1955',
    desc_en='Section of a wooden comb, partially preserved, decorated with openwork designs in the form of two twin horseshoe arches with a colonette between them.',
    title_ar='مشط ذو أسنان من الجانبين', dimensions_ar='العرض: ٣٫٨ سم، الطول: ٦٫٥ سم', from_ar='مضبوطات قسم النزهة (القضية رقم ٩٢٢٤/٩٢)',
    registered_ar='سجل فى ١٥ يوليو ١٩٥٥', date_en='', date_ar='',
    desc_ar='جزء من مشط خشبى يحتفظ بهيئته، بزخارف مفرغة تتكون من عقدين متجاورين على هيئة حدوة حصان يتوسطهما عمود صغير.'),
}
for x in rows:
    if x['id'] in MANUAL: x.update(MANUAL[x['id']])
rows.sort(key=lambda r:int(r['catalogue_page']))
last=('','')
for x in rows:  # صفحات من غير فوتر → نفس قسم القطعة اللى قبلها
    if x['section_en'] or x['section_ar']: last=(x['section_en'],x['section_ar'])
    else: x['section_en'],x['section_ar']=last
json.dump(dict(cols=COLS, extra=EXTRA, rows=rows, skipped=skipped), open('rows.json','w'), ensure_ascii=False, indent=1)
print('rows',len(rows),'skipped',len(skipped)); [print('  skip',s) for s in skipped]
ids=[r['id'] for r in rows]; print('dup ids', {i for i in ids if ids.count(i)>1})
for f in ['title_ar','from_en','date_en','desc_en','desc_ar','dimensions_en','section_en','section_ar']:
    miss=[r['id'] for r in rows if not r[f]]
    print(f'empty {f}: {len(miss)}', miss[:12])
