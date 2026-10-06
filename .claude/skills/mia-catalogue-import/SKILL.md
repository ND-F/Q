---
name: mia-catalogue-import
description: Extract museum pieces from the bilingual NF-MIA catalogue PDF (English + Arabic) into rows for the QR Google Sheet, assign permanent ids/links, and generate branded QR codes. Use when adding pieces from a catalogue/PDF to the MIA sheet, regenerating QR codes, or fixing Arabic text pulled from a PDF.
---

# Catalogue → sheet rows → QR codes

Pipeline lives in `catalogue-import/tools/` (run from a scratch dir holding `cat.pdf`), outputs in `catalogue-import/`.

## Getting the PDF
The catalogue is on Google Drive (`NF-MIA catalogue.pdf`, ~270 MB). Drive's text reader returns nothing for files this big; download directly:
`curl -L -o cat.pdf "https://drive.usercontent.google.com/download?id=<FILE_ID>&export=download&confirm=t"` — needs `drive.google.com` and `drive.usercontent.google.com` in the environment's allowed domains.

## Steps
1. `ext2.py` — PyMuPDF `rawdict` → lines per page (`pages2.json`).
2. `parse.py` — English and Arabic streams of entries (`streams.json`), paired by inventory digits.
3. `build.py` — split each entry into fields (`sides.json`).
4. `rows.py` — sheet rows (`rows.json`) + manual fixes; `cover.py` checks every number in the catalogue's inventory index is covered.
5. `export.py` — xlsx/csv + QR codes.

## Arabic extraction gotchas (all handled in ext2.py — keep them)
- **lam-alef ligatures come out reversed** (`قالوون`, `األمامى`). Signature: the alef has **zero width** at the right edge of the `ل`. Reorder only those glyphs; never do a blind text replace (it breaks real words like `والذى`).
- Rebuild Arabic lines from glyph x-positions (right→left), then re-reverse digit/Latin runs. Joiners inside a number are only `.` and `,` — `-` and `/` are separators (gives `683-684`, `18858/2`). Don't mirror brackets.
- Strip diacritics (they land on the wrong letter) but keep tatweel (`هـ`). Arabic digits → Arabic-Indic in `*_ar` fields, decimal point → `٫`.
- Line language = majority script (an English line containing an Arabic word stays English).
- Split a PDF line at horizontal gaps > 14pt (two text columns share one PDF line); re-join same-line fragments only when one side is a single word (< 120pt) or both are bold (justified headings).

## Catalogue layout gotchas
- English and Arabic are side by side **or on facing pages** → pair entries by inventory digits, never by page.
- Headings can wrap over 2–4 bold lines; the number may sit on its own line (Arabic: visually reversed `3/18764`).
- Group headings ("Double-Sided Combs") carry from/registered/description for untitled sub-items (`142. Inv. No. 4938`); sub-item titles are singularised. Two-column sub-item lists: read each column separately.
- Entries repeat (plate caption + full entry) → keep the richest copy.
- Drop figure captions / inscription translations: lines outside the entry's column, paragraphs starting with `“`/`«`/`()`, `Line drawing…`, `رقم تسجيل …`, figure numbers.
- Footer = section: chapter on one page, sub-section on the facing page → prefer the sub-section.
- Dates/provenance are genuinely missing for many entries (combs especially) — leave them empty, don't invent.
- Field rules: meta paragraph lines start a new field only on a recognised start (dims / From / Registered / Submitted…) or a date-like start (dynasty, century); everything else is a continuation.

## Rows
- Description paragraphs go to `desc_*` **and** `dsc_*1..5`.
- `material_*` only when the description's first sentence states it.
- Skip pieces already in the sheet (1066, 560, 3553, 596, 4615, 1065).
- Ids/links follow the permanent numbering in the `mia-site` skill (`final-ids.json`); `LINK = https://mia.nadimfoundation.org/<id>`.
- Always verify: every index number covered, EN/AR field presence matches, no duplicate ids.

## QR codes
`segno`, error level H, dark `#06444C` on `#EAE8D8`, finder eyes `#4A121C` (same palette as `qr.html`), SVG + PNG named `<id>`. Decode every PNG with OpenCV and compare to the link; if one fails, regenerate with another mask. Only generate for **new** ids — old ones are already printed.
