// api/pdf.js  —  Vercel Serverless Function
// بيولّد PDF من صفحة القطعة باستخدام Chrome (عربي مثالي، بدون نافذة Print)
// الاستدعاء من الصفحة:  /api/pdf?id=4&lang=ar

const chromium = require("@sparticuz/chromium");
const puppeteer = require("puppeteer-core");

module.exports = async (req, res) => {
  try {
    const id = String((req.query && req.query.id) || "").replace(/[^A-Za-z0-9_-]/g, "");
    const lang = ((req.query && req.query.lang) === "en") ? "en" : "ar";
    if (!id) { res.status(400).send("missing id"); return; }

    const host = req.headers["x-forwarded-host"] || req.headers.host;
    const proto = req.headers["x-forwarded-proto"] || "https";
    const url = proto + "://" + host + "/c.html?id=" + encodeURIComponent(id) + "&pdfmode=1";

    const browser = await puppeteer.launch({
      args: chromium.args,
      executablePath: await chromium.executablePath(),
      headless: chromium.headless,
      defaultViewport: { width: 900, height: 1200 }
    });

    const page = await browser.newPage();
    // اضبط اللغة والثيم الفاتح قبل تحميل الصفحة
    await page.evaluateOnNewDocument((lng) => {
      try { localStorage.setItem("nadim_lang", lng); localStorage.setItem("nadim_theme", "light"); } catch (e) {}
    }, lang);

    await page.goto(url, { waitUntil: "networkidle0", timeout: 45000 });
    // استنى صفحة الطباعة (#printRoot) تجهز
    await page.waitForFunction("window.__printReady === true", { timeout: 45000 }).catch(() => {});
    await page.emulateMediaType("print");

    const pdf = await page.pdf({
      format: "A4",
      printBackground: true,
      preferCSSPageSize: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 }
    });

    await browser.close();

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", 'attachment; filename="' + id + '.pdf"');
    res.setHeader("Cache-Control", "public, max-age=3600");
    res.status(200).send(pdf);
  } catch (e) {
    res.status(500).send("PDF error: " + (e && e.message ? e.message : String(e)));
  }
};
