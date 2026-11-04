# Apartado: serie «Día X de 30»

Variante de la receta (INSTRUCCIONES.md) para negocios **sin WhatsApp** en Google Maps (solo teléfono fijo o sin redes).
La idea: que el negocio (y otros dueños) lo descubran por nuestro TikTok/Instagram.

Diferencias con la receta normal:
- **Contador:** `fabrica/serie.json` guarda el último día. Suma 1 en cada video.
- **Guion:** la frase 1 empieza con «Día <n>.». Tono positivo («todavía no tiene página web»).
  La frase 7 dice «y un botón para llamar y reservar directo» (sin WhatsApp).
- **Demo:** el CTA es `tel:` (llamar), no wa.me. Si no hay fotos, la galería muestra marcos «aquí irán las fotos»
  y las reseñas muestran solo el promedio real con link a Google Maps (nunca inventar textos de reseñas).
- **Video:** en cfg.json usar `"day":"DÍA <n>"`, `"q":[3 preguntas del rubro]` y `"tags":[4 etiquetas]`
  (`video_template.html` ya las acepta; sin esas claves se ve igual que antes).
- **Contacto:** en el plan, en vez del mensaje de WhatsApp: guion de llamada corta, mención en TikTok/IG si tienen,
  y etiquetar la ubicación del negocio en TikTok.
- **Portada:** tarjeta en la sección «Serie Día X» de index.html.

## Formato «ruleta» (desde el Día 2)
Intro «Día X» → ruleta de precios (cae en 1.500 Bs) → antes (grabaciones de sus redes) → problema/solución → panel → dominio (opcional) → cierre.
- Plantilla: `fabrica/video_dia_ruleta.html` · render: `fabrica/render_dia.js` (render asíncrono, espera a que carguen las imágenes).
- Grabaciones de pantalla: fotogramas en `W/rec1/0001.jpg…` y `W/rec2/…` (`ffmpeg -i rec.mp4 -vf fps=30,scale=520:-2 rec1/%04d.jpg`).
- Guion de 12 frases; `seg.json` con 12 segmentos (revisar silencios a mano: hay pausas dentro de las frases).
- `cfg.json`: day, name, rating, reviews, category, address, img, demo, website (el link actual), domain, features, k (spin0, sol1, sol2),
  bubbles, tags, taps (toques sobre el demo: requiere `window.demo` con pick/menu/reset), lines.
- Efectos: `fabrica/sfx_eventos.py eventos.json sfx.wav` (lista de eventos: whoosh, pop, tick, ding, thump, click).
- La demo de 1.500 Bs lleva: menú de precios por categoría, reservas en 4 pasos que confirman por WhatsApp, y vista del panel con «datos de ejemplo».
