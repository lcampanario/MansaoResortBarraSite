// Lê os preços por noite que o Beyond Pricing publica nos dois anúncios e devolve em JSON.
// O site chama /.netlify/functions/precos. A resposta fica no cache do Netlify por 24 horas
// (cache "durable", compartilhado por todos os visitantes), então o Beyond é consultado
// cerca de uma vez por dia: 1 chamada para achar os anúncios + 1 por anúncio.
//
// Variáveis de ambiente no Netlify (Project configuration > Environment variables):
//   BEYOND_TOKEN      obrigatória: o token pessoal (bpat_...) criado no Beyond. Nunca colocar no GitHub.
//   BEYOND_CASA_ID    opcional: id do anúncio da casa no Beyond (economiza a chamada de busca)
//   BEYOND_VILLA_ID   opcional: id do anúncio da Villa no Beyond
// Sem BEYOND_TOKEN a função responde 503 e o site usa os valores do precos.json.
const BASE = (process.env.BEYOND_BASE_URL || "https://developers.beyondpricing.com/api/v1").replace(/\/$/, "");
const AIRBNB = { casa: "1660888966401908771", villa: "1762494515905389616" };
const DAY = 864e5;

const headers = () => ({ Authorization: `Bearer ${process.env.BEYOND_TOKEN}`, Accept: "application/vnd.api+json" });

async function get(path) {
  const r = await fetch(BASE + path, { headers: headers() });
  if (!r.ok) throw new Error(`${path.split("?")[0]}: HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
  return r.json();
}

const attrs = e => ({ ...(e.attributes || {}), ...e });
const ymdOf = v => (typeof v === "string" && /^\d{4}-\d{2}-\d{2}/.test(v) ? v.slice(0, 10) : null);

// Acha o id do Beyond de cada anúncio pelo id do Airbnb em channel-listings.
async function findIds() {
  const ids = { casa: process.env.BEYOND_CASA_ID, villa: process.env.BEYOND_VILLA_ID };
  if (ids.casa && ids.villa) return { ids, listings: null };
  const res = await get("/listings/?page[size]=100");
  const listings = (res.data || []).map(e => {
    const a = attrs(e);
    const channels = (a["channel-listings"] || []).map(c => String(c["channel-id"] ?? c.channelId ?? c.id ?? ""));
    return { id: String(e.id), title: a.title || a.name || a.nickname || "", channels };
  });
  for (const [k, airbnb] of Object.entries(AIRBNB)) {
    if (ids[k]) continue;
    const hit = listings.find(l => l.channels.some(c => c.includes(airbnb)) || JSON.stringify(l).includes(airbnb));
    if (hit) ids[k] = hit.id;
  }
  return { ids, listings };
}

// Calendário de um anúncio: { "2026-11-12": { p: 7500, m: 2 } }, só noites disponíveis.
async function calendar(id) {
  const start = new Date(), end = new Date(Date.now() + 365 * DAY);
  const q = `?filter[start-date]=${start.toISOString().slice(0, 10)}&filter[end-date]=${end.toISOString().slice(0, 10)}&page[size]=400`;
  const res = await get(`/listings/${encodeURIComponent(id)}/calendar/${q}`);
  const out = {};
  for (const e of res.data || []) {
    const a = attrs(e);
    const d = ymdOf(a.date) || ymdOf(a["calendar-date"]) || ymdOf(a.day) || ymdOf(a.night) || ymdOf(String(e.id));
    const p = Number(a["price-posted"] ?? a.price);
    if (!d || !(p > 0)) continue;
    const st = String(a.availability ?? a.status ?? "available").toLowerCase();
    if (st !== "available") continue;
    const m = Number(a["min-stay"] ?? a["min-nights"]);
    out[d] = m > 0 ? { p: Math.round(p), m } : { p: Math.round(p) };
  }
  return out;
}

export default async req => {
  const json = (body, status, maxAge) => new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=600",
      "Netlify-CDN-Cache-Control": `public, s-maxage=${maxAge}, durable`,
      // só o parâmetro "diag" muda o cache: outros parâmetros não geram chamadas extras ao Beyond
      "Netlify-Vary": "query=diag",
    },
  });
  if (!process.env.BEYOND_TOKEN) return json({ error: "BEYOND_TOKEN não configurado" }, 503, 3600);
  const diag = new URL(req.url).searchParams.has("diag");
  try {
    const { ids, listings } = await findIds();
    const body = { updated: new Date().toISOString(), source: "beyond" };
    const results = await Promise.allSettled(["casa", "villa"].map(async k => {
      if (!ids[k]) throw new Error(`${k}: anúncio do Airbnb ${AIRBNB[k]} não encontrado no Beyond`);
      body[k] = await calendar(ids[k]);
    }));
    const errors = results.filter(r => r.status === "rejected").map(r => r.reason.message);
    if (errors.length) body.errors = errors;
    // diagnóstico: /.netlify/functions/precos?diag mostra os anúncios encontrados (sem preços)
    if (diag) return json({ ids, listings, errors, days: { casa: Object.keys(body.casa || {}).length, villa: Object.keys(body.villa || {}).length } }, 200, 60);
    const ok = errors.length < 2;
    return json(body, ok ? 200 : 502, ok ? 86400 : 900);
  } catch (e) {
    return json({ error: e.message }, 502, 900);
  }
};
