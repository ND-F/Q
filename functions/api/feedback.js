// Cloudflare Pages Function: /api/feedback
// صفحة الاستاف بتبعت هنا ملاحظات المراجعة، والفانكشن بتوصّلها لـ Apps Script بتاع شيت QR (doPost في feedback.gs).
// رابط السكريبت والمفتاح متخزنين في Cloudflare (Settings > Variables and Secrets)، مش في الريبو لأنه public:
//   FEEDBACK_URL = رابط الـ Web app (.../exec)      FEEDBACK_KEY = نفس قيمة FEEDBACK_KEY في Script Properties

const ORIGINS = /^https:\/\/((mia\.nadimfoundation\.org)|(([\w-]+\.)?ndf-mia-site\.pages\.dev))$|^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/;
const TYPES = ["correction", "suggestion", "comment"];

function json(o, status) {
  return new Response(JSON.stringify(o), { status: status || 200, headers: { "Content-Type": "application/json", "Cache-Control": "no-store" } });
}
const cut = (v, n) => String(v == null ? "" : v).slice(0, n);

export async function onRequestPost({ request, env }) {
  if (!env.FEEDBACK_URL || !env.FEEDBACK_KEY) return json({ ok: false, error: "not configured" }, 503);
  const origin = request.headers.get("Origin") || "";
  if (origin && !ORIGINS.test(origin)) return json({ ok: false, error: "origin" }, 403);
  if (Number(request.headers.get("Content-Length") || 0) > 40000) return json({ ok: false, error: "too large" }, 413);

  let b;
  try { b = await request.json(); } catch (e) { return json({ ok: false, error: "bad json" }, 400); }

  let payload;
  if (b.action === "list") payload = { action: "list" };
  else if (b.action === "add") {
    payload = {
      action: "add", id: cut(b.id, 40), field: cut(b.field, 120), type: TYPES.includes(b.type) ? b.type : "comment",
      current: cut(b.current, 5000), proposed: cut(b.proposed, 5000), comment: cut(b.comment, 5000), reviewer: cut(b.reviewer, 80)
    };
    if (!payload.id || !payload.field) return json({ ok: false, error: "missing id/field" }, 400);
    if (!payload.proposed.trim() && !payload.comment.trim()) return json({ ok: false, error: "empty" }, 400);
  } else return json({ ok: false, error: "action" }, 400);
  payload.key = env.FEEDBACK_KEY;

  try {
    // Apps Script بيرد بـ 302 لصفحة النتيجة؛ fetch بيتبعها لوحده
    const r = await fetch(env.FEEDBACK_URL, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload), redirect: "follow" });
    const txt = await r.text();
    let out;
    try { out = JSON.parse(txt); } catch (e) { return json({ ok: false, error: "script reply not JSON (check the Web app deploy: Execute as Me, Anyone)" }, 502); }
    return json(out, out.ok ? 200 : (out.error === "key" ? 401 : 400));
  } catch (e) {
    return json({ ok: false, error: "script unreachable" }, 502);
  }
}

export function onRequest() {
  return json({ ok: false, error: "POST only" }, 405);
}
