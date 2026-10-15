---
name: mia-site
description: How the NADIM × Museum of Islamic Art QR site (ND-F/Q, mia.nadimfoundation.org) works and how to change it safely — short-link routing in 404.html, the c.html / scan-b.html piece pages, artworks.json from the Google Sheet, photo file names and photo rules, comb groups, prebuilt PDFs, hosting, and how to test. Use for any change to the piece pages, links, photos, QR targets, or the sheet columns.
---

# MIA QR site (ND-F/Q)

Short copy for claude.ai web sessions. The master is the owner's private skill `NDF-MIA-QR` (updated 2026-10-14).

## Hosting
- **https://mia.nadimfoundation.org** = Cloudflare Pages `ndf-mia-site` (since 2026-10-11, GoDaddy CNAME `mia`). Vercel
  still deploys every push as backup; Cloudflare Worker `ndf-mia` serves JSON + images to the pages.
- Unknown paths render `404.html` (JS router). Cloudflare 308-redirects `c.html` to `/c`: use `curl -L`.
- `_headers`: `/data/*` no-cache, `/images/*` `max-age=300`. A big push can fail the Worker build: retry with an empty commit.
- The owner also uploads files on github.com: always fetch/rebase before pushing.

## Data flow
- Source of truth: Google Sheet **"QR"** (`1HWtUoPtuSHi8XwwvxRrCXHycdeM7M1jsYj_5OIsatF8`), tab `data` (pieces + one row per
  comb group) and tab `combs` (one row per comb). Columns are read **by header name**.
- The Sheet's Apps Script `exportJSON` commits `data/artworks.json` (menu MIA > Publish now, or auto after edits, or
  10:00/15:00 Cairo). **Never hand-edit artworks.json**: change the sheet.
- Keys: `id inventory_number title_* from_* desc_* date_* dimensions_* section_* hall_* material_* info_en1..N info_ar1..N
  dsc_en1..N dsc_ar1..N video_url video_url2 video_url3 reel_url reel_url2 reel_url3 LINK QR registered_* acquisition_*
  catalogue_no catalogue_page image1..N`. N is open-ended (min 5, max 52); pages use `slotCount()`/`imageList()`, never a fixed 5.
- Pages render `dsc_*` paragraphs when any exist, otherwise `desc_*`. Slot N photo goes with `info_<lang>N` (caption) and
  `dsc_<lang>N` (paragraph after it).
- Staff review notes: the staff catalogue (`/staff-ndf-mia-only-7k3q`) posts to `functions/api/feedback.js` (Cloudflare Pages
  Function, env `FEEDBACK_URL` + `FEEDBACK_KEY`) -> the Sheet's Apps Script `doPost` -> tab `feedback`. Notes are never applied
  automatically; the owner edits tab `data` by hand.

## Photo file names (`.webp` INSIDE `images/`, case-sensitive)
| Slot | File (piece `6`) |
|---|---|
| 1 (hero) | `6.webp` |
| 2..26 | `6b.webp` .. `6z.webp` |
| 27..52 | `6aa.webp` .. `6az.webp` (`a` + letter of slot-26) |
- Front + back side by side: hero `6.webp` + `6a.webp`; slot 2..26 `6b.webp` + `6bb.webp`. `b` = a different second photo.
  Pair is `direction: ltr` (front always left, also in Arabic), centred vertically.
- `q6.webp`, `q6b.webp` ... show ONLY on `/q6` (scan-b) as a photo viewer; `/6` never sees them.
- Comb photos: `images/combs/<CODE>/<inventory with / as ->.webp`, extras `...b/c/d.webp`.
- A new slot photo appears after the next exporter run (it lists `images/` to decide which slots exist).

## Photo rules (owner's)
- webp, each <= 1000 KB. **Never crop** without asking. Long side 2048; very elongated pieces (ratio > 3) up to 4096.
- Orientation like the NF-MIA catalogue; front and back same orientation; plain backs are removed; combs teeth UP.
- Visitors can't save photos (right-click / long-press / drag blocked on all pages); the PDF download stays.

## Routing (`404.html`, last path segment)
| prefix | page |
|---|---|
| `Q…`/`VQ…` (any case) | `scan-b.html` (id, then inventory-number fallback; rewrites URL to `q<id>`) |
| `M…`/`VM…` | `scan.html` |
| `N…`/`VN…` | `n.html` |
| anything else | `c.html` (**printed QR stickers**, id only) |
- Comb groups: `/<CODE>` (SSC DSC DLC DEP DRK DGD DGR DGO DVG DZM DAC) = viewer + thumbnails, fields switch per comb.

## Rules that must not break
- **Printed ids are permanent.** Old: 0, aq, gw, ha, gn, 1–77 (74/75 unused); old group codes 67=SSC 69=DSC 70=DLC 71=DEP
  72=DRK 73=DGO 76=DAC redirect in 404.html. Catalogue pieces from 80. Never renumber; new pieces take the next free number.
- **No previous/next piece navigation** (removed on purpose).
- c.html and scan-b.html share design + PDF code: apply visual/PDF fixes to **both**; change only what was asked.
- Door 6: `/6` (normal) and `/q6` (viewer, 17 photos) differ ON PURPOSE until management decides.

## Downloaded PDF
Prebuilt: `.github/workflows/pdfs.yml` runs `tools/pdf/build.js` (headless Chrome per id × ar/en, the page's own
`prDoc`/`prGroupDoc`) and force-pushes to branch `pdfs` (+ `manifest.json`); the button downloads from jsDelivr @sha.
PDFShift (`api/pdf.js`) is retired: never call it.

## Testing
- Use a tiny node server that serves files and falls back to `404.html` (python http.server does not route).
- Device × language matrix (`localStorage.nadim_lang = 'ar'|'en'`): no page errors, `scrollWidth - innerWidth == 0`.
- `let` globals (`artwork`, `allArtworks`) are not on `window`: wait with `typeof artwork !== 'undefined' && artwork`.
- Safari: no bare `inset:`; pair `backdrop-filter` with `-webkit-backdrop-filter`.
