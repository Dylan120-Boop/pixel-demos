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
