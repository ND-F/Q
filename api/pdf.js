// api/pdf.js  —  Vercel Serverless Function (خفيفة، بدون أي مكتبات)
// بتاخد HTML من الصفحة وتبعته لخدمة PDFShift وترجّع PDF (تحميل صامت، اللينكات شغّالة).
// محتاج Environment Variable في Vercel اسمه: PDFSHIFT_API_KEY

module.exports = async (req, res) => {
  try {
    if (req.method !== "POST") { res.status(405).send("POST only"); return; }

    const key = process.env.PDFSHIFT_API_KEY;
    if (!key) { res.status(500).send("PDFSHIFT_API_KEY is not set in Vercel env vars"); return; }

    let body = req.body;
    if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
    const html = body && body.html;
    let filename = (body && body.filename) ? String(body.filename) : "artefact";
    filename = filename.replace(/[\/\\:*?"<>|]+/g, "-").slice(0, 120) || "artefact";
    if (!html) { res.status(400).send("missing html"); return; }

    const api = await fetch("https://api.pdfshift.io/v3/convert/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": key },
      body: JSON.stringify({
        source: html,
        format: "A4",
        margin: "0",
        use_print: false,
        sandbox: false
      })
    });

    if (!api.ok) {
      const t = await api.text();
      res.status(502).send("PDF service error (" + api.status + "): " + t.slice(0, 500));
      return;
    }

    const buf = Buffer.from(await api.arrayBuffer());
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", 'attachment; filename="' + filename + '.pdf"');
    res.status(200).send(buf);
  } catch (e) {
    res.status(500).send("PDF error: " + (e && e.message ? e.message : String(e)));
  }
};
