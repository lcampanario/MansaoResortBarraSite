// Tag do Google Ads + conversão "Contato pelo WhatsApp".
// Quando o Google Ads mostrar o rótulo da conversão (o texto depois da barra em send_to:
// "AW-875463976/XXXXXXXX"), cole só o rótulo em LABEL abaixo e salve no GitHub.
var ADS_ID = "AW-875463976";
var LABEL = "";

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }
gtag("js", new Date());
gtag("config", ADS_ID);

function contatoWhatsApp(origem) {
  gtag("event", "contato_whatsapp", { origem: origem, transport_type: "beacon" });
  if (LABEL) gtag("event", "conversion", { send_to: ADS_ID + "/" + LABEL, value: 500, currency: "BRL", transport_type: "beacon" });
}

// Botão verde, rodapé, "Abrir no WhatsApp" e o número no formulário
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest('a[href*="api.whatsapp.com"], a[href*="wa.me"]');
  if (a) contatoWhatsApp(a.id || a.className || "link");
}, true);

// "Enviar pelo WhatsApp": conta quando o formulário passa na validação e abre o WhatsApp
document.addEventListener("submit", function (e) {
  if (e.target.id !== "book") return;
  setTimeout(function () {
    var out = document.getElementById("out");
    if (out && !out.hidden) contatoWhatsApp("formulario");
  }, 0);
}, true);
