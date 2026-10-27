// Lê os calendários (iCal) dos dois anúncios do Airbnb e devolve as datas ocupadas em JSON.
// O site chama /.netlify/functions/disponibilidade. A resposta fica em cache por 1 hora,
// então o calendário do site se atualiza sozinho várias vezes por dia.
//
// Cole aqui os links "Exportar calendário" de cada anúncio (Airbnb > Calendário > Disponibilidade
// > Sincronizar calendários > Exportar calendário). Também podem ser definidos nas variáveis de
// ambiente do Netlify: ICAL_CASA e ICAL_VILLA.
const ICAL = {
  casa: process.env.ICAL_CASA || "https://www.airbnb.com.br/calendar/ical/1660888966401908771.ics?t=53451db43c414e2f808229b8cbd663de",
  villa: process.env.ICAL_VILLA || "https://www.airbnb.com.br/calendar/ical/1762494515905389616.ics?t=31b5454173b244e388780e21221ac400",
};

// "20260112" ou "20260112T150000Z" -> "2026-01-12"
const day = v => `${v.slice(0, 4)}-${v.slice(4, 6)}-${v.slice(6, 8)}`;

export function parseIcal(text) {
  const lines = text.replace(/\r?\n[ \t]/g, "").split(/\r?\n/);
  const out = [];
  let ev = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") ev = {};
    else if (line === "END:VEVENT") { if (ev && ev.start && ev.end) out.push([ev.start, ev.end]); ev = null; }
    else if (ev) {
      const m = line.match(/^(DTSTART|DTEND)[^:]*:(\d{8})/);
      if (m) ev[m[1] === "DTSTART" ? "start" : "end"] = day(m[2]);
    }
  }
  return out;
}

// junta intervalos [início, fim) que se sobrepõem ou encostam
export function merge(ranges) {
  const sorted = ranges.filter(([a, b]) => a < b).sort((x, y) => x[0].localeCompare(y[0]));
  const out = [];
  for (const [a, b] of sorted) {
    const last = out[out.length - 1];
    if (last && a <= last[1]) { if (b > last[1]) last[1] = b; } else out.push([a, b]);
  }
  return out;
}

export default async () => {
  const sources = Object.entries(ICAL).filter(([, url]) => url);
  const results = await Promise.allSettled(sources.map(async ([name, url]) => {
    const r = await fetch(url, { headers: { "User-Agent": "MansaoResortBarra/1.0" } });
    if (!r.ok) throw new Error(`${name}: HTTP ${r.status}`);
    return parseIcal(await r.text());
  }));
  const ok = results.filter(r => r.status === "fulfilled");
  // As duas acomodações dividem a mesma casa: uma reserva em qualquer anúncio bloqueia as duas.
  const busy = merge(ok.flatMap(r => r.value));
  const body = {
    updated: new Date().toISOString(),
    complete: sources.length > 0 && ok.length === sources.length,
    busy,
  };
  return new Response(JSON.stringify(body), {
    status: sources.length ? 200 : 503,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=300",
      "Netlify-CDN-Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
    },
  });
};
