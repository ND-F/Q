// tools/pdf/build.js
// بيولّد PDF جاهز لكل قطعة (عربي + إنجليزي) بنفس كود الصفحة (prDoc / prGroupDoc جوه c.html)،
// عشان زرار التحميل يبقى لينك لملف جاهز بدل ما كل زائر يعمل تحويل جديد.
//
// التشغيل:  node tools/pdf/build.js <outDir> [--only=id1,id2] [--force]
//   outDir فيه manifest.json من المرة اللي فاتت؛ أي ملف الـ HTML بتاعه والصور بتاعته ما اتغيروش بيتساب زي ما هو.
//
// الصور: نفس الصورة PNG بشفافيتها، مصغّرة حسب عدد الصور (المحرك بيحفظ الصور الشفافة جوه الـ PDF من غير ضغط تقريبًا).

const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const sharp = require("sharp");
const puppeteer = require("puppeteer");

const ROOT = path.resolve(__dirname, "..", "..");
const PORT = 5391;
const BASE = "http://localhost:" + PORT;

const args = process.argv.slice(2);
const OUT = path.resolve(args.find(a => !a.startsWith("--")) || path.join(ROOT, "pdf-out"));
const ONLY = (args.find(a => a.startsWith("--only=")) || "").replace("--only=", "").split(",").filter(Boolean);
const FORCE = args.includes("--force");

const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml",
  ".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".css": "text/css" };

// ===== سيرفر محلي: ملفات الريبو + /__pdfimg لتصغير الصور (PNG بشفافيتها) =====
const imgCache = new Map();
function startServer() {
  return new Promise(resolve => {
    const srv = http.createServer(async (req, res) => {
      try {
        const url = new URL(req.url, BASE);
        if (url.pathname === "/__pdfimg") {
          const rel = url.searchParams.get("u") || "";
          const px = Math.max(200, Math.min(3000, parseInt(url.searchParams.get("px") || "1400", 10)));
          const file = path.join(ROOT, rel);
          if (!file.startsWith(ROOT) || !fs.existsSync(file)) { res.writeHead(404); return res.end(); }
          const key = rel + "@" + px;
          if (!imgCache.has(key)) {
            imgCache.set(key, await sharp(file).resize({ width: px, height: px, fit: "inside", withoutEnlargement: true })
              .png({ compressionLevel: 9 }).toBuffer());
          }
          res.writeHead(200, { "Content-Type": "image/png" });
          return res.end(imgCache.get(key));
        }
        const file = path.join(ROOT, decodeURIComponent(url.pathname));
        if (file.startsWith(ROOT) && fs.existsSync(file) && fs.statSync(file).isFile()) {
          res.writeHead(200, { "Content-Type": TYPES[path.extname(file).toLowerCase()] || "application/octet-stream" });
          return fs.createReadStream(file).pipe(res);
        }
        res.writeHead(404); res.end();
      } catch (e) { res.writeHead(500); res.end(String(e)); }
    });
    srv.listen(PORT, () => resolve(srv));
  });
}

function sha(s) { return crypto.createHash("sha256").update(s).digest("hex").slice(0, 16); }
function safeName(id) { return String(id).trim().replace(/[^A-Za-z0-9_-]+/g, "_"); }

// بصمة الملف = الـ HTML + محتوى كل صورة محلية بيستخدمها (لو صورة اتغيرت بنفس الاسم، الـ PDF يتعمل تاني)
function fingerprint(html) {
  const parts = [html];
  for (const m of html.matchAll(/__pdfimg\?u=([^&"]+)/g)) {
    const f = path.join(ROOT, decodeURIComponent(m[1]));
    parts.push(fs.existsSync(f) ? crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex") : "missing");
  }
  return sha(parts.join("|"));
}

(async () => {
  fs.mkdirSync(path.join(OUT, "pdf"), { recursive: true });
  const manPath = path.join(OUT, "manifest.json");
  const oldMan = fs.existsSync(manPath) ? JSON.parse(fs.readFileSync(manPath, "utf8")) : { files: {} };
  const artworks = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "artworks.json"), "utf8"));
  const ids = artworks.map(a => String(a.id).trim()).filter(Boolean).filter(id => !ONLY.length || ONLY.includes(id));

  const srv = await startServer();
  const browser = await puppeteer.launch({ headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
  const files = Object.assign({}, oldMan.files);
  let built = 0, kept = 0, removed = 0, failed = [];

  for (const id of ids) {
    for (const lang of ["ar", "en"]) {
      const key = id + "-" + lang;
      try {
        // 1) افتح الصفحة الحقيقية وابني HTML الـ PDF بنفس الكود
        const page = await browser.newPage();
        await page.evaluateOnNewDocument(l => { try { localStorage.setItem("nadim_lang", l); } catch (e) {} }, lang);
        await page.goto(BASE + "/c.html?id=" + encodeURIComponent(id), { waitUntil: "networkidle0", timeout: 60000 });
        await page.waitForFunction(() => typeof artwork !== "undefined" && artwork, { timeout: 30000 });
        const out = await page.evaluate(async (base) => {
          const ar = lang === "ar";
          const isGroup = !!(artwork.pieces && artwork.pieces.length);
          const okSet = isGroup ? await pdfOkPieceImages() : await pdfOkImages();
          const n = Object.keys(okSet).length;
          const px = isGroup ? 700 : (n <= 2 ? 1400 : (n <= 3 ? 1200 : 1000));
          const src = u => isPdfPhoto(u) ? base + "/__pdfimg?u=" + encodeURIComponent(u) + "&px=" + px : absURL(u);
          const imgOk = u => !!okSet[u];
          const html = isGroup ? prGroupDoc(ar, src, absURL("images/pattern-teal.svg"), imgOk)
                               : prDoc(ar, src, absURL("images/pattern-teal.svg"), imgOk);
          return { html, name: isGroup ? groupFilename() : dlFilename(), realId: String(artwork.id).trim() };
        }, BASE);
        await page.close();
        if (out.realId !== id) throw new Error("page opened " + out.realId + " instead of " + id);

        const fp = fingerprint(out.html);
        const file = safeName(id) + "-" + lang + ".pdf";
        if (!FORCE && files[key] && files[key].hash === fp && fs.existsSync(path.join(OUT, "pdf", file))) { kept++; continue; }

        // 2) اطبع الـ PDF (نفس إعدادات PDFShift: A4، هوامش صفر، media=screen، الخلفيات ظاهرة)
        const pdfPage = await browser.newPage();
        await pdfPage.emulateMediaType("screen");
        await pdfPage.setContent(out.html, { waitUntil: "networkidle0", timeout: 90000 });
        await pdfPage.evaluate(() => document.fonts.ready);
        const buf = await pdfPage.pdf({ format: "A4", printBackground: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
        await pdfPage.close();
        fs.writeFileSync(path.join(OUT, "pdf", file), buf);
        files[key] = { file, hash: fp, name: out.name, bytes: buf.length };
        built++;
        console.log("built", key, (buf.length / 1048576).toFixed(1) + "MB");
      } catch (e) {
        failed.push(key + ": " + e.message);
        console.error("FAILED", key, e.message);
      }
    }
  }

  // امسح ملفات القطع اللي اتشالت من الشيت
  const live = new Set(artworks.map(a => String(a.id).trim()));
  if (!ONLY.length) {
    for (const k of Object.keys(files)) {
      const id = k.replace(/-(ar|en)$/, "");
      if (!live.has(id)) { const f = path.join(OUT, "pdf", files[k].file); if (fs.existsSync(f)) fs.unlinkSync(f); delete files[k]; removed++; }
    }
  }

  // الـ sha بيتضاف بعدين من الـ workflow (commit الملفات)، فالمانيفست بيتكتب بس لو فيه تغيير
  const changed = built > 0 || removed > 0 || !fs.existsSync(manPath);
  if (changed) fs.writeFileSync(manPath, JSON.stringify({ built_at: new Date().toISOString(), files }, null, 1));
  fs.writeFileSync(path.join(OUT, ".changed"), changed ? "1" : "0");
  await browser.close(); srv.close();
  console.log(`done: built ${built}, unchanged ${kept}, removed ${removed}, failed ${failed.length}`);
  if (failed.length) { console.log(failed.join("\n")); process.exitCode = 1; }
})();
