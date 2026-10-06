---
name: mia-site
description: How the NADIM × Museum of Islamic Art QR site (ND-F/Q, mia.nadimfoundation.org) works and how to change it safely — short-link routing in 404.html, the c.html / scan-b.html piece pages, artworks.json synced from the Google Sheet, the downloaded PDF layout, and how to test. Use for any change to the piece pages, links, QR targets, or the sheet columns.
---

# MIA QR site (ND-F/Q)

Static site on Vercel at **https://mia.nadimfoundation.org** (also GitHub Pages under `/Q`).
`vercel.json` rewrites every path except `/api/*` to `404.html`, which routes short links.

## Data flow
- Source of truth is the Google Sheet **"QR"** (`1HWtUoPtuSHi8XwwvxRrCXHycdeM7M1jsYj_5OIsatF8`, tab `data`).
- An external automation commits it to `data/artworks.json` ("update artworks.json with exact descriptions …" commits). **Never hand-edit artworks.json** — change the sheet.
- Sheet columns (in order): `id inventory_number title_en title_ar from_en from_ar desc_en desc_ar date_en date_ar dimensions_en dimensions_ar section_en section_ar hall_en hall_ar material_en material_ar info_en1 info_ar1 … info_en5 info_ar5 video_url dsc_en1 dsc_ar1 … dsc_en5 dsc_ar5 reel_url reel_url2 reel_url3 video_url2 video_url3 LINK QR registered_en registered_ar acquisition_en acquisition_ar catalogue_no catalogue_page`. `LINK` is column **AS**.
- The pages render `dsc_*` paragraphs when any exist, otherwise `desc_*`. `dsc_N` pairs with `imageN` (image before paragraph for N≥2). Images live at `images/<id>…` (`image1..5` in the JSON).

## Routing (`404.html`, last path segment)
| prefix | page | id passed |
|---|---|---|
| `VM…` / `M…` | `scan.html` | `V`+rest / rest |
| `VN…` / `N…` | `n.html` | `V`+rest / rest |
| `VQ…` / `Q…` (case-insensitive) | `scan-b.html` | `V`+rest / rest |
| anything else | `c.html` | whole segment |

- **Printed QR codes use `mia.nadimfoundation.org/<id>` → `c.html`.**
- `scan-b.html` (`/q<id>`) looks up by `id`, then falls back to `inventory_number` (whole value or any number in a `;`/`,` list; `Inv` prefix optional; `/` written as `-`). It rewrites the URL to `q<id>` so reload/share stay on scan-b.
- `c.html` looks up by `id` only.

## Rules that must not break
- **IDs printed on QR stickers are permanent.** Old pieces keep 0, aq, gw, ha, gn, 1–77 (74/75 unused). Catalogue pieces: 2801/4155 = 80, then 81–178 in catalogue order (`catalogue-import/tools/final-ids.json`). Never renumber existing rows; new pieces get the next free number. Old group codes 67/70/71/72/73 open the first piece of their old group.
- **No previous/next piece navigation** on either page (removed from both c.html and scan-b.html on purpose).
- c.html and scan-b.html share the same design and PDF code — apply visual/PDF fixes to **both**.

## Downloaded PDF
`downloadPDF()` builds a standalone HTML (`prDoc` + `prDocCSS`) and posts it to `/api/pdf` (PDFShift, A4, margin 0, needs `PDFSHIFT_API_KEY` on Vercel). Page margins come from `#w { padding; box-decoration-break: clone }` (repeats on every page with the beige background — real PDF margins would be white). Figures/videos/captions use `break-inside: avoid`, images are capped at `max-height: 470px`.

## Testing (Playwright + Chromium are preinstalled)
- `python3 -m http.server` does not route; use a tiny node server that serves files and falls back to `404.html` to test short links end to end, including a reload.
- Run a device × language matrix (`devices['iPhone SE'|'iPhone 13'|'Pixel 7'|'iPad Mini'|'Desktop Chrome']`, `localStorage.nadim_lang = 'ar'|'en'`), checking page errors and `scrollWidth - innerWidth == 0`.
- PDF: call the page's own `prDoc(...)` from Playwright, `setContent` it with `emulateMedia({media:'screen'})`, `page.pdf({format:'A4', margin:0, printBackground:true})`, then rasterize with `pdftoppm` to look at every page.
- `let` globals (`artwork`, `allArtworks`) are not on `window`: wait with `typeof artwork !== 'undefined' && artwork`.
- Safari: avoid `inset:` without top/right/bottom/left fallbacks and always pair `backdrop-filter` with `-webkit-backdrop-filter`.
