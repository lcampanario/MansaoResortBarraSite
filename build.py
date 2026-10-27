# Gera o site em português (raiz), inglês (en/) e espanhol (es/) a partir de index.html.
# Uso: python3 build.py  ->  escreve publicar/ (para hospedagem) e preview/ (prévia no Claude)
import os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DOMAIN = "https://mansaoresortbarra.netlify.app/"
SEO_TITLE = {
    "pt": "Mansão Resort Barra da Tijuca, Rio de Janeiro | Até 18 hóspedes, 500 m da praia do Posto 6",
    "en": "Mansão Resort Barra da Tijuca, Rio de Janeiro | Up to 18 guests, 500 m from Posto 6 beach",
    "es": "Mansão Resort Barra da Tijuca, Río de Janeiro | Hasta 18 huéspedes, a 500 m de la playa del Posto 6",
}
LANG_ATTR = {"pt": "pt-BR", "en": "en", "es": "es"}
OG_LOCALE = {"pt": "pt_BR", "en": "en_US", "es": "es_ES"}
DIR = {"pt": "", "en": "en/", "es": "es/"}

FLAGS = {
    "pt": '<svg viewBox="0 0 22 15" aria-hidden="true"><rect width="22" height="15" fill="#229e45"/><path d="M11 2 20 7.5 11 13 2 7.5Z" fill="#f8e509"/><circle cx="11" cy="7.5" r="3.3" fill="#2b49a3"/></svg>',
    "en": '<svg viewBox="0 0 22 15" aria-hidden="true"><rect width="22" height="15" fill="#fff"/><g fill="#b22234"><rect width="22" height="1.15"/><rect y="2.3" width="22" height="1.15"/><rect y="4.6" width="22" height="1.15"/><rect y="6.9" width="22" height="1.15"/><rect y="9.2" width="22" height="1.15"/><rect y="11.5" width="22" height="1.15"/><rect y="13.85" width="22" height="1.15"/></g><rect width="9.5" height="8" fill="#3c3b6e"/></svg>',
    "es": '<svg viewBox="0 0 22 15" aria-hidden="true"><rect width="22" height="15" fill="#c60b1e"/><rect y="3.75" width="22" height="7.5" fill="#ffc400"/></svg>',
}
LABEL = {"pt": ("PT", "Português"), "en": ("EN", "English"), "es": ("ES", "Español")}

# (português, inglês, espanhol). Ordem importa: frases longas antes das curtas.
T = [
# ---- head / SEO
('content="Mansão para até 18 hóspedes na Barra da Tijuca, Rio de Janeiro, Brasil. Piscina, spa aquecido, sauna e campo de futebol a 500 m da praia do Posto 6. Casa inteira para até 18 hóspedes ou Villa anexa para até 10. Reserve direto com a anfitriã."',
 'content="Mansion for up to 18 guests in Barra da Tijuca, Rio de Janeiro, Brazil. Pool, heated spa, sauna and football pitch, 500 m from Posto 6 beach. Whole house for up to 18 guests or the Villa annex for up to 10. Book directly with the host."',
 'content="Mansión para hasta 18 huéspedes en Barra da Tijuca, Río de Janeiro, Brasil. Piscina, spa climatizado, sauna y cancha de fútbol a 500 m de la playa del Posto 6. Casa completa para hasta 18 huéspedes o Villa anexa para hasta 10. Reserve directamente con la anfitriona."'),
('content="casa para temporada Barra da Tijuca, mansão aluguel Rio de Janeiro, casa com piscina Barra da Tijuca, casa para 18 pessoas Rio de Janeiro, casa até 18 hóspedes Barra da Tijuca, aluguel temporada Rio de Janeiro Brasil, casa Posto 6 Barra, aluguel por temporada Barra"',
 'content="vacation rental Barra da Tijuca, mansion rental Rio de Janeiro, house with pool Barra da Tijuca, house for 18 people Rio de Janeiro, villa for large groups Rio de Janeiro Brazil, Posto 6 Barra beach house"',
 'content="alquiler temporario Barra da Tijuca, alquiler de mansión Río de Janeiro, casa con piscina Barra da Tijuca, casa para 18 personas Río de Janeiro, alquiler vacacional Río de Janeiro Brasil, casa Posto 6 Barra"'),
('content="Mansão Resort Barra da Tijuca, Rio de Janeiro · Até 18 hóspedes"', 'content="Mansão Resort Barra da Tijuca, Rio de Janeiro · Up to 18 guests"', 'content="Mansão Resort Barra da Tijuca, Río de Janeiro · Hasta 18 huéspedes"'),
('content="Piscina, spa aquecido, sauna e campo de futebol privativos. Até 18 hóspedes. Reserva direta, sem taxas de plataforma."',
 'content="Private pool, heated spa, sauna and football pitch. Up to 18 guests. Direct booking, no platform fees."',
 'content="Piscina, spa climatizado, sauna y cancha de fútbol privados. Hasta 18 huéspedes. Reserva directa, sin comisiones de plataforma."'),
('"alternateName": "Mansão Resort Barra da Tijuca, Rio de Janeiro, Brasil, para até 18 hóspedes"', '"alternateName": "Mansão Resort Barra da Tijuca, Rio de Janeiro, Brazil, for up to 18 guests"', '"alternateName": "Mansão Resort Barra da Tijuca, Río de Janeiro, Brasil, para hasta 18 huéspedes"'),
('"Casa de alto padrão com 590 m² construídos, piscina, spa aquecido para 8 pessoas, sauna a vapor e campo de futebol sintético de 280 m², a cerca de 500 m da praia do Posto 6."',
 '"High-end 590 m² house with pool, heated spa for 8, steam sauna and a 280 m² synthetic football pitch, about 500 m from Posto 6 beach."',
 '"Casa de alto nivel con 590 m² construidos, piscina, spa climatizado para 8 personas, sauna a vapor y cancha de fútbol sintética de 280 m², a unos 500 m de la playa del Posto 6."'),
('"keywords": "Barra da Tijuca, Rio de Janeiro, Brasil, até 18 hóspedes, casa para temporada, mansão com piscina"', '"keywords": "Barra da Tijuca, Rio de Janeiro, Brazil, up to 18 guests, vacation rental, mansion with pool"', '"keywords": "Barra da Tijuca, Río de Janeiro, Brasil, hasta 18 huéspedes, alquiler temporario, mansión con piscina"'),
('"name": "Piscina privativa"', '"name": "Private pool"', '"name": "Piscina privada"'),
('"name": "Spa aquecido"', '"name": "Heated spa"', '"name": "Spa climatizado"'),
('"name": "Sauna a vapor"', '"name": "Steam sauna"', '"name": "Sauna a vapor"'),
('"name": "Campo de futebol sintético"', '"name": "Synthetic football pitch"', '"name": "Cancha de fútbol sintética"'),
('"name": "Churrasqueira"', '"name": "Barbecue grill"', '"name": "Parrilla"'),
('"name": "Estacionamento para 8 carros"', '"name": "Parking for 8 cars"', '"name": "Estacionamiento para 8 autos"'),
('"name": "Ar-condicionado"', '"name": "Air conditioning"', '"name": "Aire acondicionado"'),
('"name": "A casa fica perto da praia?"', '"name": "Is the house close to the beach?"', '"name": "¿La casa está cerca de la playa?"'),
('"text": "Sim. A casa fica a cerca de 500 m da praia do Posto 6 da Barra da Tijuca, com acesso a pé ou de balsa pela Lagoa de Marapendi."',
 '"text": "Yes. The house is about 500 m from Posto 6 beach in Barra da Tijuca, reachable on foot or by ferry across Marapendi Lagoon."',
 '"text": "Sí. La casa está a unos 500 m de la playa del Posto 6 en Barra da Tijuca, con acceso a pie o en balsa por la Laguna de Marapendi."'),
('"name": "Quantas pessoas cabem?"', '"name": "How many people can stay?"', '"name": "¿Cuántas personas caben?"'),
('"text": "A casa inteira recebe até 18 hóspedes em 6 quartos. A Villa, um anexo com entrada independente, recebe até 10 hóspedes em 3 quartos."',
 '"text": "The whole house sleeps up to 18 guests in 6 bedrooms. The Villa, an annex with its own entrance, sleeps up to 10 guests in 3 bedrooms."',
 '"text": "La casa completa recibe hasta 18 huéspedes en 6 habitaciones. La Villa, un anexo con entrada independiente, recibe hasta 10 huéspedes en 3 habitaciones."'),
('"name": "Fica em condomínio?"', '"name": "Is it inside a gated community?"', '"name": "¿Está dentro de un condominio?"'),
('"text": "Não. É um imóvel independente, sem regulamento de condomínio. Pedimos apenas som em volume ambiente na área externa após as 22h."',
 '"text": "No. It is a standalone property with no condominium rules. We only ask for background-level music outdoors after 10 pm."',
 '"text": "No. Es una propiedad independiente, sin reglamento de condominio. Solo pedimos música a volumen ambiente en el área exterior después de las 22 h."'),
('"name": "Como faço a reserva direta?"', '"name": "How do I book directly?"', '"name": "¿Cómo hago la reserva directa?"'),
('"text": "Escolha as datas e a acomodação no formulário do site e envie pelo WhatsApp. A anfitriã responde com disponibilidade e valor, sem taxas de plataforma, e envia um link de pagamento do Mercado Pago, por Pix ou cartão de crédito."',
 '"text": "Choose your dates and stay in the form and send it by WhatsApp. The host replies with availability and price, with no platform fees, and sends a Mercado Pago payment link for Pix or credit card."',
 '"text": "Elija las fechas y el alojamiento en el formulario y envíelo por WhatsApp. La anfitriona responde con disponibilidad y precio, sin comisiones de plataforma, y envía un enlace de pago de Mercado Pago, por Pix o tarjeta de crédito."'),
# ---- header
('<small>Barra da Tijuca · Posto 6</small>', '<small>Barra da Tijuca · Posto 6</small>', '<small>Barra da Tijuca · Posto 6</small>'),
('aria-label="Seções"', 'aria-label="Sections"', 'aria-label="Secciones"'),
('<a href="#acomodacoes">Acomodações</a>', '<a href="#acomodacoes">Stays</a>', '<a href="#acomodacoes">Alojamiento</a>'),
('<a href="#lazer">Lazer</a>', '<a href="#lazer">Leisure</a>', '<a href="#lazer">Ocio</a>'),
('<a href="#fotos">Fotos</a>', '<a href="#fotos">Photos</a>', '<a href="#fotos">Fotos</a>'),
('<a href="#localizacao">Localização</a>', '<a href="#localizacao">Location</a>', '<a href="#localizacao">Ubicación</a>'),
('<a href="#perguntas">Perguntas</a>', '<a href="#perguntas">FAQ</a>', '<a href="#perguntas">Preguntas</a>'),
('>Ver disponibilidade</a>', '>Check availability</a>', '>Ver disponibilidad</a>'),
# ---- hero
('<p class="eyebrow">Barra da Tijuca · Rio de Janeiro · Brasil</p>', '<p class="eyebrow">Barra da Tijuca · Rio de Janeiro · Brazil</p>', '<p class="eyebrow">Barra da Tijuca · Río de Janeiro · Brasil</p>'),
('<h1>Mansão Resort na Barra da Tijuca para <em>até 18 hóspedes</em>, a 500 m da praia do Posto 6</h1>',
 '<h1>Mansão Resort in Barra da Tijuca for <em>up to 18 guests</em>, 500 m from Posto 6 beach</h1>',
 '<h1>Mansão Resort en Barra da Tijuca para <em>hasta 18 huéspedes</em>, a 500 m de la playa del Posto 6</h1>'),
('<p class="lede">Um resort só para o seu grupo no Rio de Janeiro. Piscina, spa aquecido, sauna, espaço gourmet e campo de futebol sintético privativos, em uma casa de 590 m² fora de condomínio. Reserve direto com a anfitriã, sem taxas de plataforma.</p>',
 '<p class="lede">A private resort just for your group in Rio de Janeiro. Pool, heated spa, sauna, gourmet barbecue area and synthetic football pitch, all private, in a 590 m² standalone house. Book directly with the host, with no platform fees.</p>',
 '<p class="lede">Un resort solo para su grupo en Río de Janeiro. Piscina, spa climatizado, sauna, quincho gourmet y cancha de fútbol sintética privados, en una casa de 590 m² fuera de condominio. Reserve directamente con la anfitriona, sin comisiones de plataforma.</p>'),
('>Consultar datas</a>', '>Check dates</a>', '>Consultar fechas</a>'),
('>Ver as acomodações</a>', '>See the stays</a>', '>Ver el alojamiento</a>'),
('<li><b>Até 18</b> hóspedes</li>', '<li><b>Up to 18</b> guests</li>', '<li><b>Hasta 18</b> huéspedes</li>'),
('<li><b>6</b> quartos</li>', '<li><b>6</b> bedrooms</li>', '<li><b>6</b> habitaciones</li>'),
('<li><b>7,5</b> banheiros</li>', '<li><b>7.5</b> bathrooms</li>', '<li><b>7,5</b> baños</li>'),
('<li><b>8</b> vagas</li>', '<li><b>8</b> parking spaces</li>', '<li><b>8</b> cocheras</li>'),
('<li><b>5,0</b> no Airbnb</li>', '<li><b>5.0</b> on Airbnb</li>', '<li><b>5,0</b> en Airbnb</li>'),
('alt="Área da piscina da Mansão Resort Barra"', 'alt="Pool area at Mansão Resort Barra"', 'alt="Área de la piscina de Mansão Resort Barra"'),
('<figcaption>piscina e área externa</figcaption>', '<figcaption>pool and outdoor area</figcaption>', '<figcaption>piscina y área exterior</figcaption>'),
('alt="Spa aquecido para 8 pessoas"', 'alt="Heated spa for 8 people"', 'alt="Spa climatizado para 8 personas"'),
('<figcaption>spa aquecido</figcaption>', '<figcaption>heated spa</figcaption>', '<figcaption>spa climatizado</figcaption>'),
('alt="Campo de futebol sintético de 280 m²"', 'alt="280 m² synthetic football pitch"', 'alt="Cancha de fútbol sintética de 280 m²"'),
('<figcaption>campo de futebol</figcaption>', '<figcaption>football pitch</figcaption>', '<figcaption>cancha de fútbol</figcaption>'),
# ---- distances
('<span>praia do Posto 6</span>', '<span>to Posto 6 beach</span>', '<span>de la playa del Posto 6</span>'),
('<span>a pé do Parque das Rosas</span>', '<span>walk to Parque das Rosas</span>', '<span>a pie del Parque das Rosas</span>'),
('<span>a pé da Lagoa de Marapendi</span>', '<span>walk to Marapendi Lagoon</span>', '<span>a pie de la Laguna de Marapendi</span>'),
('<strong>Perto</strong><span>de shoppings, ciclovia e restaurantes</span>', '<strong>Close</strong><span>to malls, bike path and restaurants</span>', '<strong>Cerca</strong><span>de shoppings, ciclovía y restaurantes</span>'),
# ---- stays
('<p class="eyebrow">Duas formas de se hospedar</p>', '<p class="eyebrow">Two ways to stay</p>', '<p class="eyebrow">Dos formas de hospedarse</p>'),
('<h2>A casa inteira ou a Villa anexa</h2>', '<h2>The whole house or the Villa annex</h2>', '<h2>La casa completa o la Villa anexa</h2>'),
('<p class="lede">Nas duas opções a área de lazer é exclusiva do seu grupo. Escolha pelo tamanho da turma.</p>', '<p class="lede">With either option the leisure area is reserved for your group only. Pick by group size.</p>', '<p class="lede">En las dos opciones el área de ocio es exclusiva de su grupo. Elija según el tamaño del grupo.</p>'),
('<span class="tag">Casa inteira</span>', '<span class="tag">Whole house</span>', '<span class="tag">Casa completa</span>'),
('<h3>Mansão Resort para até 18 hóspedes</h3>', '<h3>Mansão Resort for up to 18 guests</h3>', '<h3>Mansão Resort para hasta 18 huéspedes</h3>'),
('<p>A casa principal e o anexo juntos. Ideal para famílias grandes, aniversários e grupos de amigos.</p>', '<p>The main house and the annex together. Ideal for large families, birthdays and groups of friends.</p>', '<p>La casa principal y el anexo juntos. Ideal para familias grandes, cumpleaños y grupos de amigos.</p>'),
('<span>hóspedes</span>', '<span>guests</span>', '<span>huéspedes</span>'),
('<span>quartos</span>', '<span>bedrooms</span>', '<span>habitaciones</span>'),
('<span>camas</span>', '<span>beds</span>', '<span>camas</span>'),
('<strong>7,5</strong><span>banheiros</span>', '<strong>7.5</strong><span>bathrooms</span>', '<strong>7,5</strong><span>baños</span>'),
('<span>banheiros</span>', '<span>bathrooms</span>', '<span>baños</span>'),
('3 solteiros ou 1 queen + 1 solteiro', '3 singles or 1 queen + 1 single', '3 individuales o 1 queen + 1 individual'),
('4 solteiros ou 1 queen + 2 solteiros', '4 singles or 1 queen + 2 singles', '4 individuales o 1 queen + 2 individuales'),
('<span>Suíte</span>', '<span>Suite</span>', '<span>Suite</span>'),
('<span>Quarto ', '<span>Bedroom ', '<span>Habitación '),
(' + 1 solteiro</span>', ' + 1 single</span>', ' + 1 individual</span>'),
('<span>3 solteiros</span>', '<span>3 singles</span>', '<span>3 individuales</span>'),
('<span>4 solteiros</span>', '<span>4 singles</span>', '<span>4 individuales</span>'),
('<p class="note">Ar-condicionado e Smart TV 43" em todos os quartos. Sala com TV 70" e som Bose.</p>', '<p class="note">Air conditioning and 43" Smart TV in every bedroom. Living room with 70" TV and Bose sound.</p>', '<p class="note">Aire acondicionado y Smart TV de 43" en todas las habitaciones. Sala con TV de 70" y sonido Bose.</p>'),
('>Consultar a casa inteira</a>', '>Ask about the whole house</a>', '>Consultar la casa completa</a>'),
('alt="Piscina em frente à Villa anexa"', 'alt="Pool in front of the Villa annex"', 'alt="Piscina frente a la Villa anexa"'),
('<figcaption>Villa anexa</figcaption>', '<figcaption>Villa annex</figcaption>', '<figcaption>Villa anexa</figcaption>'),
('<span class="tag">Villa anexa</span>', '<span class="tag">Villa annex</span>', '<span class="tag">Villa anexa</span>'),
('<h3>Villa Resort para até 10 hóspedes</h3>', '<h3>Villa Resort for up to 10 guests</h3>', '<h3>Villa Resort para hasta 10 huéspedes</h3>'),
('<p>Anexo térreo com entrada independente. A casa principal fica fechada e desocupada durante a sua estadia.</p>', '<p>Ground-floor annex with its own entrance. The main house stays closed and empty during your stay.</p>', '<p>Anexo en planta baja con entrada independiente. La casa principal queda cerrada y desocupada durante su estadía.</p>'),
('<p class="note">Arrumação em dias alternados, das 9h às 17h, sem custo extra. Aceita animais.</p>', '<p class="note">Housekeeping every other day, 9 am to 5 pm, at no extra cost. Pets welcome.</p>', '<p class="note">Limpieza en días alternos, de 9 a 17 h, sin costo extra. Se aceptan mascotas.</p>'),
('>Consultar a Villa</a>', '>Ask about the Villa</a>', '>Consultar la Villa</a>'),
# ---- leisure
('<p class="eyebrow">Área de lazer privativa</p>', '<p class="eyebrow">Private leisure area</p>', '<p class="eyebrow">Área de ocio privada</p>'),
('<h2>Tudo dentro de casa, só para vocês</h2>', '<h2>Everything at home, just for you</h2>', '<h2>Todo dentro de casa, solo para ustedes</h2>'),
('<p class="lede">Uma área externa pensada para passar o dia inteiro: da piscina ao churrasco, do spa à partida de futebol.</p>', '<p class="lede">An outdoor area made for spending the whole day: from the pool to the barbecue, from the spa to a football match.</p>', '<p class="lede">Un área exterior pensada para pasar el día entero: de la piscina al asado, del spa al partido de fútbol.</p>'),
('alt="Piscina privativa"', 'alt="Private pool"', 'alt="Piscina privada"'),
('<figcaption>piscina</figcaption>', '<figcaption>pool</figcaption>', '<figcaption>piscina</figcaption>'),
('alt="Lounge com piscina e espaço gourmet ao fundo"', 'alt="Lounge with pool and barbecue area behind"', 'alt="Lounge con piscina y quincho al fondo"'),
('<figcaption>espaço gourmet</figcaption>', '<figcaption>barbecue area</figcaption>', '<figcaption>quincho gourmet</figcaption>'),
('alt="Spa aquecido"', 'alt="Heated spa"', 'alt="Spa climatizado"'),
('<figcaption>spa</figcaption>', '<figcaption>spa</figcaption>', '<figcaption>spa</figcaption>'),
('alt="Piscina com ponte e porta da sauna"', 'alt="Pool with bridge and sauna door"', 'alt="Piscina con puente y puerta de la sauna"'),
('<figcaption>piscina e ponte</figcaption>', '<figcaption>pool and bridge</figcaption>', '<figcaption>piscina y puente</figcaption>'),
('alt="Sauna a vapor"', 'alt="Steam sauna"', 'alt="Sauna a vapor"'),
('<figcaption>sauna</figcaption>', '<figcaption>sauna</figcaption>', '<figcaption>sauna</figcaption>'),
('alt="Lounge externo com poltronas"', 'alt="Outdoor lounge with armchairs"', 'alt="Lounge exterior con sillones"'),
('<figcaption>lounge</figcaption>', '<figcaption>lounge</figcaption>', '<figcaption>lounge</figcaption>'),
('alt="Espreguiçadeira ao lado da piscina"', 'alt="Sun lounger by the pool"', 'alt="Reposera junto a la piscina"'),
('<figcaption>espreguiçadeiras</figcaption>', '<figcaption>sun loungers</figcaption>', '<figcaption>reposeras</figcaption>'),
('alt="Guarda-sol e lounge com vista para a piscina"', 'alt="Parasol and lounge overlooking the pool"', 'alt="Sombrilla y lounge con vista a la piscina"'),
('<figcaption>área de estar</figcaption>', '<figcaption>sitting area</figcaption>', '<figcaption>área de estar</figcaption>'),
('alt="Cadeiras de fibra junto à piscina"', 'alt="Wicker chairs by the pool"', 'alt="Sillas de fibra junto a la piscina"'),
('<figcaption>bar da piscina</figcaption>', '<figcaption>pool bar</figcaption>', '<figcaption>bar de la piscina</figcaption>'),
('<h3>Piscina e spa aquecido</h3><p>Piscina disponível 24 horas, spa aquecido para 8 pessoas incluso na diária, rede de vôlei aquático, espreguiçadeiras e chuveirão.</p>',
 '<h3>Pool and heated spa</h3><p>Pool open 24 hours, heated spa for 8 included in the rate, water volleyball net, sun loungers and outdoor shower.</p>',
 '<h3>Piscina y spa climatizado</h3><p>Piscina disponible las 24 horas, spa climatizado para 8 personas incluido en la tarifa, red de vóley acuático, reposeras y ducha exterior.</p>'),
('<h3>Campo sintético de 280 m²</h3><p>Com traves e bola. Uso de tênis obrigatório no campo.</p>', '<h3>280 m² synthetic pitch</h3><p>With goals and a ball. Sneakers required on the pitch.</p>', '<h3>Cancha sintética de 280 m²</h3><p>Con arcos y pelota. Uso obligatorio de zapatillas en la cancha.</p>'),
('<h3>Espaço gourmet</h3><p>Churrasqueira, fogão industrial, freezer e caixa de som JBL de 160 W. Sauna a vapor ao lado.</p>', '<h3>Gourmet barbecue area</h3><p>Barbecue grill, industrial stove, freezer and a 160 W JBL speaker. Steam sauna next door.</p>', '<h3>Quincho gourmet</h3><p>Parrilla, cocina industrial, freezer y parlante JBL de 160 W. Sauna a vapor al lado.</p>'),
# ---- amenities
('<p class="eyebrow">Comodidades</p>', '<p class="eyebrow">Amenities</p>', '<p class="eyebrow">Comodidades</p>'),
('<h2>O que a casa oferece</h2>', '<h2>What the house offers</h2>', '<h2>Lo que ofrece la casa</h2>'),
('<li>Ar-condicionado split nos quartos</li>', '<li>Split air conditioning in bedrooms</li>', '<li>Aire acondicionado split en las habitaciones</li>'),
('<li>Cortinas blackout</li>', '<li>Blackout curtains</li>', '<li>Cortinas blackout</li>'),
('<li>Cozinha completa e equipada</li>', '<li>Fully equipped kitchen</li>', '<li>Cocina completa y equipada</li>'),
('<li>Lavanderia com 2 máquinas</li>', '<li>Laundry with 2 washing machines</li>', '<li>Lavadero con 2 lavarropas</li>'),
('<li>Estacionamento interno para 8 carros</li>', '<li>Private parking for 8 cars</li>', '<li>Estacionamiento interno para 8 autos</li>'),
('<li>Funcionária na casa, das 9h às 17h</li>', '<li>Housekeeper on site, 9 am to 5 pm</li>', '<li>Empleada en la casa, de 9 a 17 h</li>'),
('<li>Fechadura eletrônica (senha ou tag)</li>', '<li>Electronic lock (code or tag)</li>', '<li>Cerradura electrónica (clave o tag)</li>'),
('<li>Monitoramento na área externa</li>', '<li>Outdoor security cameras</li>', '<li>Monitoreo en el área exterior</li>'),
('<li>Secador de cabelo</li>', '<li>Hair dryer</li>', '<li>Secador de pelo</li>'),
('<li>Guarda-sol e espreguiçadeiras</li>', '<li>Parasols and sun loungers</li>', '<li>Sombrillas y reposeras</li>'),
('<li>Aceita animais de estimação</li>', '<li>Pets allowed</li>', '<li>Se aceptan mascotas</li>'),
# ---- gallery
('<p class="eyebrow">Fotos</p>', '<p class="eyebrow">Photos</p>', '<p class="eyebrow">Fotos</p>'),
('<h2>Conheça cada ambiente</h2>', '<h2>See every room</h2>', '<h2>Conozca cada ambiente</h2>'),
('<p class="lede">Sala de jantar ampla, quartos com ar-condicionado, suítes com banheira de hidromassagem e a Villa com entrada independente.</p>', '<p class="lede">A large dining room, air-conditioned bedrooms, suites with jacuzzi tubs and the Villa with its own entrance.</p>', '<p class="lede">Comedor amplio, habitaciones con aire acondicionado, suites con bañera de hidromasaje y la Villa con entrada independiente.</p>'),
('aria-label="Filtrar fotos por ambiente"', 'aria-label="Filter photos by room"', 'aria-label="Filtrar fotos por ambiente"'),
('aria-label="Foto ampliada"', 'aria-label="Enlarged photo"', 'aria-label="Foto ampliada"'),
('id="lb-prev">Anterior</button>', 'id="lb-prev">Previous</button>', 'id="lb-prev">Anterior</button>'),
('id="lb-next">Próxima</button>', 'id="lb-next">Next</button>', 'id="lb-next">Siguiente</button>'),
('id="lb-close">Fechar</button>', 'id="lb-close">Close</button>', 'id="lb-close">Cerrar</button>'),
# ---- booking
('<p class="eyebrow">Reserva direta</p>', '<p class="eyebrow">Direct booking</p>', '<p class="eyebrow">Reserva directa</p>'),
('>Fale direto com a anfitriã</h2>', '>Talk directly with the host</h2>', '>Hable directamente con la anfitriona</h2>'),
('<p class="lede">Informe as datas e o tamanho do grupo. A mensagem chega pronta no WhatsApp e você recebe disponibilidade e valor.</p>', '<p class="lede">Enter your dates and group size. The message opens ready to send in WhatsApp, and you get availability and price back.</p>', '<p class="lede">Indique las fechas y el tamaño del grupo. El mensaje llega listo a WhatsApp y usted recibe disponibilidad y precio.</p>'),
('<b>Sem taxa de serviço da plataforma</b>', '<b>No platform service fee</b>', '<b>Sin comisión de plataforma</b>'),
('>Você paga só a hospedagem combinada.</span>', '>You pay only the agreed rate.</span>', '>Usted paga solo el hospedaje acordado.</span>'),
('<b>Resposta rápida</b>', '<b>Fast replies</b>', '<b>Respuesta rápida</b>'),
('>A anfitriã responde 100% das mensagens, em geral em até 1 hora.</span>', '>The host answers 100% of messages, usually within 1 hour.</span>', '>La anfitriona responde el 100% de los mensajes, en general en menos de 1 hora.</span>'),
('<b>Pagamento online seguro</b>', '<b>Secure online payment</b>', '<b>Pago online seguro</b>'),
('>Depois de confirmar as datas no WhatsApp, você recebe um link do Mercado Pago para pagar por Pix ou cartão de crédito.</span>', '>Once your dates are confirmed on WhatsApp, you get a Mercado Pago link to pay by Pix or credit card.</span>', '>Después de confirmar las fechas por WhatsApp, recibe un enlace de Mercado Pago para pagar por Pix o tarjeta de crédito.</span>'),
('<b>Hóspedes nota 5,0</b>', '<b>Rated 5.0 by guests</b>', '<b>Huéspedes nota 5,0</b>'),
('>Avaliação máxima no Airbnb em limpeza, check-in, comunicação e localização.</span>', '>Top Airbnb ratings for cleanliness, check-in, communication and location.</span>', '>Calificación máxima en Airbnb en limpieza, check-in, comunicación y ubicación.</span>'),
('<legend>Acomodação</legend>', '<legend>Stay</legend>', '<legend>Alojamiento</legend>'),
('<span><b>Casa inteira</b><small>até 18 hóspedes</small></span>', '<span><b>Whole house</b><small>up to 18 guests</small></span>', '<span><b>Casa completa</b><small>hasta 18 huéspedes</small></span>'),
('<span><b>Villa anexa</b><small>até 10 hóspedes</small></span>', '<span><b>Villa annex</b><small>up to 10 guests</small></span>', '<span><b>Villa anexa</b><small>hasta 10 huéspedes</small></span>'),
('<label for="guests">Hóspedes<input', '<label for="guests">Guests<input', '<label for="guests">Huéspedes<input'),
('<label for="name">Seu nome<input', '<label for="name">Your name<input', '<label for="name">Su nombre<input'),
('placeholder="Nome e sobrenome"', 'placeholder="First and last name"', 'placeholder="Nombre y apellido"'),
('<label for="msg">Mensagem (opcional)', '<label for="msg">Message (optional)', '<label for="msg">Mensaje (opcional)'),
('placeholder="Ocasião, pets, horário de chegada..."', 'placeholder="Occasion, pets, arrival time..."', 'placeholder="Ocasión, mascotas, horario de llegada..."'),
('>Montar mensagem para o WhatsApp</button>', '>Create WhatsApp message</button>', '>Armar mensaje para WhatsApp</button>'),
('>Abrir no WhatsApp</a>', '>Open in WhatsApp</a>', '>Abrir en WhatsApp</a>'),
('id="copy">Copiar mensagem</button>', 'id="copy">Copy message</button>', 'id="copy">Copiar mensaje</button>'),
('<p class="note">WhatsApp da anfitriã: ', '<p class="note">Host WhatsApp: ', '<p class="note">WhatsApp de la anfitriona: '),
('<p class="note">Próximo passo: com as datas confirmadas, você recebe o link do Mercado Pago para pagar por Pix ou cartão.</p>', '<p class="note">Next step: once the dates are confirmed, you get the Mercado Pago link to pay by Pix or card.</p>', '<p class="note">Próximo paso: con las fechas confirmadas, recibe el enlace de Mercado Pago para pagar por Pix o tarjeta.</p>'),
# ---- reviews + faq
('<p class="eyebrow">Avaliações dos hóspedes</p>', '<p class="eyebrow">Guest reviews</p>', '<p class="eyebrow">Opiniones de huéspedes</p>'),
('<div class="score"><strong>5,0</strong><span class="lede">de 5 no Airbnb · Preferido dos hóspedes</span></div>', '<div class="score"><strong>5.0</strong><span class="lede">out of 5 on Airbnb · Guest favorite</span></div>', '<div class="score"><strong>5,0</strong><span class="lede">de 5 en Airbnb · Favorito de los huéspedes</span></div>'),
('<span>Limpeza</span><b>5,0</b>', '<span>Cleanliness</span><b>5.0</b>', '<span>Limpieza</span><b>5,0</b>'),
('<span>Exatidão</span><b>4,8</b>', '<span>Accuracy</span><b>4.8</b>', '<span>Exactitud</span><b>4,8</b>'),
('<span>Check-in</span><b>5,0</b>', '<span>Check-in</span><b>5.0</b>', '<span>Check-in</span><b>5,0</b>'),
('<span>Comunicação</span><b>5,0</b>', '<span>Communication</span><b>5.0</b>', '<span>Comunicación</span><b>5,0</b>'),
('<span>Localização</span><b>5,0</b>', '<span>Location</span><b>5.0</b>', '<span>Ubicación</span><b>5,0</b>'),
('<span>Custo-benefício</span><b>5,0</b>', '<span>Value</span><b>5.0</b>', '<span>Precio-calidad</span><b>5,0</b>'),
('<p class="eyebrow">Perguntas frequentes</p><h2>Antes de reservar</h2>', '<p class="eyebrow">Frequently asked questions</p><h2>Before you book</h2>', '<p class="eyebrow">Preguntas frecuentes</p><h2>Antes de reservar</h2>'),
('<summary>A casa fica perto da praia?</summary><p>Sim. A casa fica a cerca de 500 m da praia do Posto 6 da Barra da Tijuca, com acesso a pé ou de balsa pela Lagoa de Marapendi.</p>',
 '<summary>Is the house close to the beach?</summary><p>Yes. The house is about 500 m from Posto 6 beach in Barra da Tijuca, reachable on foot or by ferry across Marapendi Lagoon.</p>',
 '<summary>¿La casa está cerca de la playa?</summary><p>Sí. La casa está a unos 500 m de la playa del Posto 6 en Barra da Tijuca, con acceso a pie o en balsa por la Laguna de Marapendi.</p>'),
('<summary>Qual a diferença entre a casa inteira e a Villa?</summary><p>A casa inteira inclui a casa principal e o anexo, para até 18 pessoas. A Villa é só o anexo térreo com entrada independente, para até 10 pessoas, e a casa principal fica fechada. Em ambas a área de lazer é exclusiva do seu grupo.</p>',
 '<summary>What is the difference between the whole house and the Villa?</summary><p>The whole house includes the main house and the annex, for up to 18 people. The Villa is only the ground-floor annex with its own entrance, for up to 10 people, and the main house stays closed. In both, the leisure area is reserved for your group.</p>',
 '<summary>¿Cuál es la diferencia entre la casa completa y la Villa?</summary><p>La casa completa incluye la casa principal y el anexo, para hasta 18 personas. La Villa es solo el anexo en planta baja con entrada independiente, para hasta 10 personas, y la casa principal queda cerrada. En ambas el área de ocio es exclusiva de su grupo.</p>'),
('<summary>Fica em condomínio? Posso fazer festa?</summary><p>É um imóvel independente, sem regulamento de condomínio. Após as 22h pedimos som em volume ambiente na área externa, por respeito aos vizinhos. Para som mais alto, use a sala com as portas fechadas.</p>',
 '<summary>Is it in a gated community? Can we have a party?</summary><p>It is a standalone property with no condominium rules. After 10 pm we ask for background-level music outdoors, out of respect for the neighbors. For louder music, use the living room with the doors closed.</p>',
 '<summary>¿Está en un condominio? ¿Puedo hacer una fiesta?</summary><p>Es una propiedad independiente, sin reglamento de condominio. Después de las 22 h pedimos música a volumen ambiente en el área exterior, por respeto a los vecinos. Para música más fuerte, use la sala con las puertas cerradas.</p>'),
('<summary>Como funciona o pagamento?</summary><p>Você envia a consulta pelo WhatsApp, a anfitriã confirma disponibilidade e valor e envia um link de pagamento do Mercado Pago. Você pode pagar por Pix ou cartão de crédito, com a segurança do Mercado Pago. A reserva é garantida após a confirmação do pagamento.</p>',
 '<summary>How does payment work?</summary><p>You send your request by WhatsApp, the host confirms availability and price and sends a Mercado Pago payment link. You can pay by Pix or credit card, protected by Mercado Pago. The booking is guaranteed once payment is confirmed.</p>',
 '<summary>¿Cómo funciona el pago?</summary><p>Usted envía la consulta por WhatsApp, la anfitriona confirma disponibilidad y precio y envía un enlace de pago de Mercado Pago. Puede pagar por Pix o tarjeta de crédito, con la seguridad de Mercado Pago. La reserva queda garantizada tras la confirmación del pago.</p>'),
('<summary>Tem estacionamento?</summary><p>Sim, estacionamento interno com 8 vagas.</p>', '<summary>Is there parking?</summary><p>Yes, private parking for 8 cars.</p>', '<summary>¿Hay estacionamiento?</summary><p>Sí, estacionamiento interno con 8 lugares.</p>'),
('<summary>Posso levar meu pet?</summary><p>Sim, animais de estimação são bem-vindos. Avise na mensagem de reserva.</p>', '<summary>Can I bring my pet?</summary><p>Yes, pets are welcome. Just mention it in your booking message.</p>', '<summary>¿Puedo llevar a mi mascota?</summary><p>Sí, las mascotas son bienvenidas. Avise en el mensaje de reserva.</p>'),
# ---- footer
('<span>Mansão Resort Barra · Barra da Tijuca, Rio de Janeiro, RJ, Brasil · Até 18 hóspedes</span>', '<span>Mansão Resort Barra · Barra da Tijuca, Rio de Janeiro, RJ, Brazil · Up to 18 guests</span>', '<span>Mansão Resort Barra · Barra da Tijuca, Río de Janeiro, RJ, Brasil · Hasta 18 huéspedes</span>'),
('<span>Também no <a', '<span>Also on <a', '<span>También en <a'),
('>Airbnb (casa inteira)</a> e <a', '>Airbnb (whole house)</a> and <a', '>Airbnb (casa completa)</a> y <a'),
('<a class="btn fab" href="#reservar">Reservar</a>', '<a class="btn fab" href="#reservar">Book</a>', '<a class="btn fab" href="#reservar">Reservar</a>'),
# ---- script: gallery
('["todas","Todas"],["sala","Sala"],["quartos","Quartos"],["banheiros","Banheiros"],["villa","Villa anexa"],["gourmet","Espaço gourmet"],["externa","Área externa"]',
 '["todas","All"],["sala","Living"],["quartos","Bedrooms"],["banheiros","Bathrooms"],["villa","Villa annex"],["gourmet","Barbecue area"],["externa","Outdoors"]',
 '["todas","Todas"],["sala","Sala"],["quartos","Habitaciones"],["banheiros","Baños"],["villa","Villa anexa"],["gourmet","Quincho"],["externa","Exterior"]'),
('"Sala de jantar e estar integradas"', '"Open-plan dining and living room"', '"Comedor y living integrados"'),
('"Sala com TV de 70 polegadas"', '"Living room with 70-inch TV"', '"Sala con TV de 70 pulgadas"'),
('"Mesa de jantar"', '"Dining table"', '"Mesa de comedor"'),
('"Sala de estar"', '"Living room"', '"Living"'),
('"Mesa redonda com ar-condicionado"', '"Round table with air conditioning"', '"Mesa redonda con aire acondicionado"'),
('"Aparador"', '"Sideboard"', '"Aparador"'),
('"Churrasqueira e fogão industrial"', '"Barbecue grill and industrial stove"', '"Parrilla y cocina industrial"'),
('"Espaço gourmet"]', '"Gourmet barbecue area"]', '"Quincho gourmet"]'),
('"Varanda gourmet com vista para a piscina"', '"Gourmet veranda overlooking the pool"', '"Galería gourmet con vista a la piscina"'),
('"Suíte com cama queen"', '"Suite with queen bed"', '"Suite con cama queen"'),
('"Suíte com escrivaninha"', '"Suite with desk"', '"Suite con escritorio"'),
('"Quarto com cama queen e solteiro"', '"Bedroom with queen and single bed"', '"Habitación con cama queen e individual"'),
('"Quarto com Smart TV"', '"Bedroom with Smart TV"', '"Habitación con Smart TV"'),
('"Suíte ampla"', '"Spacious suite"', '"Suite amplia"'),
('"Suíte com piso de madeira"', '"Suite with wooden floor"', '"Suite con piso de madera"'),
('"Vista da janela para a piscina"', '"Window view of the pool"', '"Vista de la ventana a la piscina"'),
('"Banheiro com hidromassagem"', '"Bathroom with jacuzzi tub"', '"Baño con hidromasaje"'),
('"Banheiro com pia dupla"', '"Bathroom with double sink"', '"Baño con lavabo doble"'),
('"Banheira de hidromassagem"', '"Jacuzzi tub"', '"Bañera de hidromasaje"'),
('"Villa: suíte com queen e solteiro"', '"Villa: suite with queen and single bed"', '"Villa: suite con queen e individual"'),
('"Villa: suíte"', '"Villa: suite"', '"Villa: suite"'),
('"Villa: banheiro da suíte"', '"Villa: suite bathroom"', '"Villa: baño de la suite"'),
('"Villa: quarto 2"', '"Villa: bedroom 2"', '"Villa: habitación 2"'),
('"Villa: quarto 3"', '"Villa: bedroom 3"', '"Villa: habitación 3"'),
('"Villa: quarto 3 com vista para o jardim"', '"Villa: bedroom 3 with garden view"', '"Villa: habitación 3 con vista al jardín"'),
('"Villa: quarto com Smart TV"', '"Villa: bedroom with Smart TV"', '"Villa: habitación con Smart TV"'),
('"Villa: corredor"', '"Villa: hallway"', '"Villa: pasillo"'),
('"Wi-Fi em todos os ambientes"', '"Wi-Fi throughout the house"', '"Wi-Fi en todos los ambientes"'),
('"Lounge ao lado da piscina"', '"Lounge by the pool"', '"Lounge junto a la piscina"'),
('"Piscina vista da varanda"', '"Pool seen from the veranda"', '"Piscina vista desde la galería"'),
('"Área da piscina"', '"Pool area"', '"Área de la piscina"'),
('"Campo de futebol sintético"]', '"Synthetic football pitch"]', '"Cancha de fútbol sintética"]'),
('"Campo com espreguiçadeiras"', '"Pitch with sun loungers"', '"Cancha con reposeras"'),
('"Casa principal"', '"Main house"', '"Casa principal"'),
('"Entrada com estacionamento para 8 carros"', '"Entrance with parking for 8 cars"', '"Entrada con estacionamiento para 8 autos"'),
('"Bolas e cabideiro"', '"Balls and coat rack"', '"Pelotas y perchero"'),
('"Ampliar: "', '"Enlarge: "', '"Ampliar: "'),
('(shown.length === 1 ? " foto" : " fotos")', '(shown.length === 1 ? " photo" : " photos")', '(shown.length === 1 ? " foto" : " fotos")'),
('${idx + 1} de ${shown.length}', '${idx + 1} of ${shown.length}', '${idx + 1} de ${shown.length}'),
# ---- videos
('<a href="#videos">Vídeos</a>', '<a href="#videos">Videos</a>', '<a href="#videos">Videos</a>'),
('<p class="eyebrow">Vídeos</p>', '<p class="eyebrow">Videos</p>', '<p class="eyebrow">Videos</p>'),
('<h2>Veja a casa em movimento</h2>', '<h2>See the house in motion</h2>', '<h2>Vea la casa en movimiento</h2>'),
('<p class="lede">Um passeio pela piscina, pelo campo e pelos ambientes internos, gravado na própria casa.</p>', '<p class="lede">A walk through the pool, the pitch and the indoor rooms, filmed at the house itself.</p>', '<p class="lede">Un recorrido por la piscina, la cancha y los ambientes interiores, grabado en la propia casa.</p>'),
('"Assistir ao vídeo "', '"Watch video "', '"Ver video "'),
# ---- calendar
('aria-label="Calendário de disponibilidade"', 'aria-label="Availability calendar"', 'aria-label="Calendario de disponibilidad"'),
('aria-label="Mês anterior"', 'aria-label="Previous month"', 'aria-label="Mes anterior"'),
('aria-label="Próximo mês"', 'aria-label="Next month"', 'aria-label="Mes siguiente"'),
('<b>Disponibilidade</b>', '<b>Availability</b>', '<b>Disponibilidad</b>'),
('<i class="k-busy"></i>Ocupado</span>', '<i class="k-busy"></i>Booked</span>', '<i class="k-busy"></i>Ocupado</span>'),
('<i class="k-sel"></i>Suas datas</span>', '<i class="k-sel"></i>Your dates</span>', '<i class="k-sel"></i>Sus fechas</span>'),
('<span>Toque no dia de chegada e depois no de saída.</span>', '<span>Tap your arrival day, then your departure day.</span>', '<span>Toque el día de llegada y luego el de salida.</span>'),
('>Carregando disponibilidade...</p>', '>Loading availability...</p>', '>Cargando disponibilidad...</p>'),
('"Atualizado em " : "Atualizado parcialmente em "', '"Updated " : "Partially updated "', '"Actualizado el " : "Actualizado parcialmente el "'),
('"Não foi possível carregar a disponibilidade agora. Envie suas datas pelo WhatsApp e confirmamos."', '"Availability could not be loaded right now. Send your dates on WhatsApp and we will confirm."', '"No fue posible cargar la disponibilidad ahora. Envíe sus fechas por WhatsApp y le confirmamos."'),
('"Parte dessas datas já está ocupada. Escolha outras datas no calendário."', '"Some of these dates are already booked. Please pick other dates on the calendar."', '"Parte de esas fechas ya está ocupada. Elija otras fechas en el calendario."'),
# ---- script: form
('"Escolha as datas de check-in e check-out."', '"Choose your check-in and check-out dates."', '"Elija las fechas de check-in y check-out."'),
('"O check-out precisa ser depois do check-in."', '"Check-out must be after check-in."', '"El check-out debe ser posterior al check-in."'),
('"Informe de 1 a " + capFor() + " hóspedes para essa acomodação."', '"Enter 1 to " + capFor() + " guests for this stay."', '"Indique de 1 a " + capFor() + " huéspedes para este alojamiento."'),
('"Informe seu nome."', '"Enter your name."', '"Indique su nombre."'),
('"Villa anexa (até 10 hóspedes)" : "Casa inteira (até 18 hóspedes)"', '"Villa annex (up to 10 guests)" : "Whole house (up to 18 guests)"', '"Villa anexa (hasta 10 huéspedes)" : "Casa completa (hasta 18 huéspedes)"'),
('`Olá! Vi o site da Mansão Resort Barra e gostaria de consultar disponibilidade.\\n\\n`', '`Hello! I saw the Mansão Resort Barra website and would like to check availability.\\n\\n`', '`¡Hola! Vi el sitio de Mansão Resort Barra y quisiera consultar disponibilidad.\\n\\n`'),
('`Acomodação: ${stay}', '`Stay: ${stay}', '`Alojamiento: ${stay}'),
('${nights === 1 ? "noite" : "noites"}', '${nights === 1 ? "night" : "nights"}', '${nights === 1 ? "noche" : "noches"}'),
('`Hóspedes: ${g}\\nNome: ${form.name.value.trim()}`', '`Guests: ${g}\\nName: ${form.name.value.trim()}`', '`Huéspedes: ${g}\\nNombre: ${form.name.value.trim()}`'),
('"Mensagem copiada"', '"Message copied"', '"Mensaje copiado"'),
('"Texto selecionado, use Ctrl+C"', '"Text selected, press Ctrl+C"', '"Texto seleccionado, use Ctrl+C"'),
]

def langs_nav(lang):
    # links relativos que funcionam na hospedagem e na prévia
    up = "" if lang == "pt" else "../"
    hrefs = {"pt": up + "index.html", "en": up + "en/index.html", "es": up + "es/index.html"}
    items = []
    for l in ("pt", "en", "es"):
        cur = ' aria-current="true"' if l == lang else ""
        items.append(f'<a href="{hrefs[l]}" hreflang="{LANG_ATTR[l]}" lang="{LANG_ATTR[l]}" title="{LABEL[l][1]}"{cur}>{FLAGS[l]}<span>{LABEL[l][0]}</span></a>')
    return '<nav class="langs" aria-label="Idioma / Language / Idioma">' + "".join(items) + "</nav>"

def canon(lang):
    out = [f'<link rel="canonical" href="{DOMAIN}{DIR[lang]}">']
    for l in ("pt", "en", "es"):
        out.append(f'<link rel="alternate" hreflang="{LANG_ATTR[l]}" href="{DOMAIN}{DIR[l]}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}">')
    return "\n".join(out)

def translate(src, lang):
    s = src
    if lang != "pt":
        i = 1 if lang == "en" else 2
        for row in T:
            pt = row[0]
            if pt not in s:
                raise SystemExit(f"[{lang}] texto não encontrado: {pt[:80]}")
            s = s.replace(pt, row[i])
        s = s.replace('src="images/', 'src="../images/').replace('const G = "images/galeria/"', 'const G = "../images/galeria/"').replace('"images/', '"../images/')
        s = s.replace(f'content="{DOMAIN}images/', f'content="{DOMAIN}images/')
    s = s.replace('<meta property="og:locale" content="pt_BR">', f'<meta property="og:locale" content="{OG_LOCALE[lang]}">')
    s = s.replace('"url": "' + DOMAIN + '"', '"url": "' + DOMAIN + DIR[lang] + '"')
    s = s.replace("<!--LANGS-->", langs_nav(lang)).replace("<!--CANON-->", canon(lang))
    return s

def full_doc(s, lang, seo_title=True, embed=True):
    i = s.index('<header class="top">')
    head, body = s[:i], s[i:]
    head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
    if embed:
        body = body.replace('const EMBED = false;', 'const EMBED = true;')
    if seo_title:
        head = re.sub(r"<title>.*?</title>", f"<title>{SEO_TITLE[lang]}</title>", head, count=1)
    return (f'<!doctype html>\n<html lang="{LANG_ATTR[lang]}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head}</head>\n<body>\n{body}\n</body>\n</html>\n')

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)

src = open(os.path.join(HERE, "index.html")).read()
built = {l: translate(src, l) for l in ("pt", "en", "es")}

pub = os.path.join(HERE, "publicar")
write(os.path.join(pub, "index.html"), full_doc(built["pt"], "pt"))
write(os.path.join(pub, "en", "index.html"), full_doc(built["en"], "en"))
write(os.path.join(pub, "es", "index.html"), full_doc(built["es"], "es"))
urls = "".join(f'  <url><loc>{DOMAIN}{DIR[l]}</loc>' + "".join(f'<xhtml:link rel="alternate" hreflang="{LANG_ATTR[k]}" href="{DOMAIN}{DIR[k]}"/>' for k in ("pt", "en", "es")) + '</url>\n' for l in ("pt", "en", "es"))
write(os.path.join(pub, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n')

# prévia: a página principal fica como fragmento (o Claude adiciona o esqueleto); en/ e es/ são documentos completos
prev = os.path.join(HERE, "preview")
write(os.path.join(prev, "index.html"), built["pt"])
write(os.path.join(prev, "en", "index.html"), full_doc(built["en"], "en", seo_title=False, embed=False))
write(os.path.join(prev, "es", "index.html"), full_doc(built["es"], "es", seo_title=False, embed=False))
print("ok: publicar/ e preview/ gerados")
