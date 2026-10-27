# Mansão Resort Barra — site de reservas diretas

- `publicar/` — o site publicado (português na raiz, `en/` e `es/`).
- `index.html` — texto-fonte em português. Depois de editar, rode `python3 build.py` para gerar as três línguas em `publicar/`.
- `publicar/netlify/functions/disponibilidade.mjs` — lê os calendários do Airbnb e alimenta o calendário do site.

O Netlify publica automaticamente a cada atualização deste repositório.
