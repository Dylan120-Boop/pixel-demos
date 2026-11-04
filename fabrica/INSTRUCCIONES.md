# Fábrica de demos — Pixel Studio Bolivia

Receta diaria. Dueño: Dylan (Pixel Studio Bolivia, Santa Cruz, Bolivia). Todo en español.
WhatsApp de Pixel Studio: 7611 3430 (wa.me/59176113430). TikTok: @pb.pixel.studio / @ia.webs.
Precios: informativa desde 400 Bs, con catálogo desde 700 Bs, con reservas y panel desde 1.500 Bs.

## 0. Preparar
```
git clone https://github.com/Dylan120-Boop/pixel-demos.git repo && cd repo
ls -d */ | sed 's#/##' > /tmp/excluir.txt     # negocios ya hechos
```
Para publicar necesitas permiso de escritura: llama `add_repo` (owner Dylan120-Boop, repo pixel-demos, access push)
y usa el comando de clonado que devuelva. Si falla, sigue igual y entrega las demos como archivos HTML (paso 6).

## 1. Buscar 3 negocios sin página web
```
python3 fabrica/places.py "$PLACES_KEY" 3 /tmp/excluir.txt /tmp/hoy
```
Filtra: sin sitio web, con teléfono, ≥4.3★, ≥15 reseñas, ≥4 fotos, rubros distintos. Lee /tmp/hoy/candidatos.json.
Mira las fotos (Read) y descarta las que muestren caras de personas en primer plano o sean de mala calidad.

## 2. Demo por negocio  → repo/<slug>/index.html + repo/<slug>/img/
- Copia las fotos de /tmp/hoy/<slug>/img/ a repo/<slug>/img/ (redúcelas a ~1000px, calidad 80).
- Escribe la página tomando como base de estilo `fabrica/demo_referencia.html` (Botania) pero adaptada al rubro:
  paleta y tipografía acordes al negocio, textos y servicios propios del rubro (sin inventar precios),
  reseñas reales (nombre + inicial), botón de WhatsApp al teléfono DEL NEGOCIO (wa.me/591XXXXXXXX).
- OBLIGATORIO para el video: `<section id="espacios">` como 1ª sección, la galería como 3ª `<section>`,
  las reseñas como 4ª `<section>`, y `<section id="reservar">` con el CTA de WhatsApp.
- Franja fija arriba: «Demo de propuesta para <Negocio> · hecha por Pixel Studio Bolivia».
- Pie: «Página demo creada por Pixel Studio Bolivia».
- Revisa con Playwright a 390x844 que se vea bien.

## 3. Voz (ElevenLabs, conector)
Guion de 9 frases separadas por [pause] (estructura fija, adapta rubro y datos):
1 «Este/a <rubro> tiene <rating dicho en palabras> estrellas...» 2 «pero no tiene página web.»
3 «Si alguien lo busca, no encuentra <2-3 cosas del rubro>, ni cómo <reservar/pedir/comprar>.»
4 «Así que le hice una. Con inteligencia artificial.» 5 «Mira cómo quedó.»
6 «<3 secciones de su demo>...» 7 «y un botón para <acción> directo por WhatsApp.»
8 «¿Tu negocio tampoco tiene página web?» 9 «Escríbeme, y te muestro cómo quedaría el tuyo.»
`creative_generate_speech` con model_id eleven_v4, voice_id `nZDJE2daaH0meWHbWbxh` (Nico), generations_count 1,
etiquetas [curious] al inicio y [excited] en la frase 4. Espera con `creative_get_flow_run_status`, toma el
full_res_url con `creative_get_generations` y descárgalo con curl a /tmp/hoy/<slug>/voz.mp3.
Luego: `python3 fabrica/segs.py voz.mp3 > seg.json` (9 segmentos).

## 4. Video (1080x1920, 30 fps)
En una carpeta de trabajo W: copia fabrica/video_template.html → W/video.html, la demo → W/demo/ (index.html + img/),
y escribe W/cfg.json:
`{"name","rating","reviews","category","address"(corta),"phone","extra"(ej. "Abierto hoy"),"img":"demo/img/f0.jpg","demo":"demo/index.html","prompt":"Crea una página web elegante para <Negocio>: …","lines":[las 9 frases sin etiquetas]}`
Sirve W con `python3 -m http.server 8765` y renderiza:
`cd W && CFG=cfg.json SEG=seg.json PAGE=/video.html OUT=silent.mp4 node ../repo/fabrica/render.js video`
(render.js usa http://127.0.0.1:8765). Efectos: `python3 ../repo/fabrica/sfx.py` (lee seg.json, crea sfx.wav).
Mezcla: `ffmpeg -i silent.mp4 -i voz.mp3 -i sfx.wav -filter_complex "[1:a]aresample=44100[v];[2:a]volume=0.45[s];[v][s]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest <slug>.mp4`
Revisa 6 fotogramas en una hoja de contacto antes de entregar.

## 5. Publicar demos
En repo: agrega cada <slug>/ y una tarjeta por negocio en la lista de index.html (portada). Commit y push a main.
Link: https://dylan120-boop.github.io/pixel-demos/<slug>/

## 6. Entregar a Dylan (SendUserFile, status proactive)
- Los 3 videos .mp4.
- `plan_del_dia.md` con, por negocio: nombre, rubro, rating, teléfono, link de la demo, link de Maps,
  hora sugerida de publicación (12:30, 18:30 y 21:00 hora Bolivia, uno por horario), descripción para TikTok
  (gancho + CTA WhatsApp 7611 3430 + 5 hashtags: #paginasweb #santacruzbolivia #emprendedoresbolivia + 2 del rubro),
  y el mensaje de WhatsApp para el negocio (humano, corto, menciona sus reseñas, link de su demo, sin precios,
  pregunta abierta al final) con link wa.me/591XXXXXXXX?text=... ya codificado.
- Recordatorios: activar etiqueta de contenido IA en TikTok, música de la biblioteca comercial, y pedir permiso
  al negocio antes de pagar publicidad con su video.
Si no hubo 3 negocios válidos, entrega los que haya y dilo.
