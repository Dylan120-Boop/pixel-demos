#!/usr/bin/env python3
"""Genera demos automáticas para los mejores prospectos.
Uso: python3 generar_demos.py <API_KEY> <leads.json> <N> <repo_dir> <salida_lote.json>
Por negocio: baja fotos y reseñas (Place Details), saca su paleta de colores de las fotos ("kit de marca")
y escribe <repo>/<slug>/index.html + img/. Evita cadenas/sucursales y reparte rubros.
"""
import sys, json, os, re, io, html, colorsys, urllib.request, urllib.parse, collections
from PIL import Image
KEY, LEADS, N, REPO, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5]
E = html.escape

R = {  # rubro -> textos y estilo (sin precios inventados)
 "restaurante": ("Restaurante", "Ver la carta", "pedir o reservar", "Reservar mesa", "Sabores que dan ganas de <em>volver</em>",
   [("🍽️","Almuerzos","Platos caseros y del día."),("🥩","A la carta","Lo mejor de la cocina."),("🎉","Grupos","Cumpleaños y reuniones."),("🛵","Para llevar","Pide y pasa a recoger.")], "Lora"),
 "pizzería": ("Pizzería", "Ver pizzas", "pedir", "Pedir ahora", "Pizza recién salida del <em>horno</em>",
   [("🍕","Pizzas","Clásicas y de la casa."),("🧀","Ingredientes","Frescos todos los días."),("🛵","Delivery","Directo a tu puerta."),("👨‍👩‍👧","Para compartir","Ideal para el grupo.")], "Anton"),
 "hamburguesería": ("Hamburguesas", "Ver el menú", "pedir", "Pedir ahora", "Hamburguesas que se <em>notan</em>",
   [("🍔","Burgers","Smash, dobles y de la casa."),("🍟","Acompañantes","Papas y más."),("🥤","Combos","Para cada antojo."),("🛵","Delivery","Pide por WhatsApp.")], "Anton"),
 "cafetería": ("Cafetería", "Ver la carta", "pedir o reservar", "Reservar mesa", "Tu lugar para un buen <em>café</em>",
   [("☕","Café","Espresso, filtrados y fríos."),("🥐","Pastelería","Dulce y salado del día."),("🍳","Desayunos","Para empezar bien."),("💻","Para quedarse","Wifi y buen ambiente.")], "Lora"),
 "pastelería": ("Pastelería", "Ver productos", "encargar", "Encargar ahora", "Dulces hechos con <em>cariño</em>",
   [("🎂","Tortas","Para cumpleaños y eventos."),("🧁","Postres","Del día, en vitrina."),("🎁","Encargos","Personalizados."),("☕","Para acompañar","Café y bebidas.")], "Lora"),
 "heladería": ("Heladería", "Ver sabores", "pedir", "Pedir ahora", "El antojo más <em>fresco</em>",
   [("🍨","Helados","Sabores de la casa."),("🍧","Postres","Copas y especiales."),("🎉","Eventos","Para tus fiestas."),("🛵","Para llevar","Pide por WhatsApp.")], "Lora"),
 "barbería": ("Barbería", "Ver servicios", "reservar un turno", "Reservar turno", "Tu mejor corte, <em>sin esperas</em>",
   [("✂️","Cortes","Clásicos y modernos."),("🧔","Barba","Perfilado y toalla caliente."),("💈","Diseños","Fade, líneas y más."),("📅","Turnos","Reserva por WhatsApp.")], "Anton"),
 "salón de belleza": ("Salón de belleza", "Ver servicios", "reservar", "Reservar cita", "Tu momento para verte <em>increíble</em>",
   [("💇‍♀️","Cabello","Cortes, color y peinados."),("💅","Uñas","Manicure y pedicure."),("✨","Tratamientos","Hidratación y más."),("👰","Eventos","Novias y quinceañeras.")], "Lora"),
 "uñas nail bar": ("Nail bar", "Ver servicios", "reservar", "Reservar cita", "Uñas que <em>enamoran</em>",
   [("💅","Manicure","Semipermanente y gel."),("🦶","Pedicure","Spa de pies."),("🎨","Diseños","Nail art a tu gusto."),("📅","Citas","Reserva por WhatsApp.")], "Lora"),
 "spa": ("Spa", "Ver tratamientos", "reservar", "Reservar cita", "Un respiro para <em>ti</em>",
   [("💆","Masajes","Relajantes y descontracturantes."),("🧖","Faciales","Limpieza e hidratación."),("🌿","Corporales","Tratamientos completos."),("🎁","Regalos","Gift cards para regalar.")], "Lora"),
 "gimnasio": ("Gimnasio", "Ver planes", "inscribirse", "Quiero inscribirme", "Entrena <em>en serio</em>",
   [("🏋️","Musculación","Máquinas y peso libre."),("🏃","Cardio","Cintas y bicis."),("🔥","Funcional","Clases en grupo."),("🧑‍🏫","Instructores","Te guían desde el día uno.")], "Anton"),
 "veterinaria": ("Veterinaria", "Ver servicios", "agendar una consulta", "Agendar consulta", "Cuidamos a tu <em>mejor amigo</em>",
   [("🩺","Consultas","Clínica general."),("💉","Vacunas","Calendario al día."),("🛁","Peluquería","Baño y corte."),("🦴","Pet shop","Alimentos y accesorios.")], "Lora"),
 "salón de eventos": ("Salón de eventos", "Ver espacios", "consultar una fecha", "Consultar fecha", "Celebra en un lugar <em>inolvidable</em>",
   [("💍","Bodas","Ceremonia y fiesta."),("👑","Quinceaños","Una entrada de película."),("🎂","Cumpleaños","Con toda la familia."),("🥂","Corporativos","Cenas y lanzamientos.")], "Lora"),
}
DEF = ("Negocio local", "Ver más", "consultar", "Escribir ahora", "Atención de <em>primera</em> en Santa Cruz",
   [("⭐","Calidad","Lo que dicen las reseñas."),("📍","Ubicación","Fácil de encontrar."),("💬","Atención","Te respondemos rápido."),("📲","WhatsApp","Consulta directo.")], "Lora")

def get(url, headers=None):
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=30).read()

def paleta(imgs):
    """Kit de marca: color de acento (el más vivo y frecuente de sus fotos) + fondo oscuro del mismo tono."""
    cnt = collections.Counter()
    for b in imgs:
        im = Image.open(io.BytesIO(b)).convert("RGB").resize((80, 80)).quantize(8).convert("RGB")
        for c, rgb in im.getcolors(6400): cnt[rgb] += c
    best, bs = (200, 150, 80), -1
    for rgb, c in cnt.items():
        h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in rgb])
        sc = (s ** 1.2) * (0.3 + v) * (c ** 0.5)
        if s > .25 and .25 < v and sc > bs: best, bs = rgb, sc
    h, s, v = colorsys.rgb_to_hsv(*[x / 255 for x in best])
    hx = lambda hh, ll, ss: "#%02x%02x%02x" % tuple(int(x * 255) for x in colorsys.hls_to_rgb(hh, ll, ss))
    return {"acc": hx(h, .62, max(.55, min(s, .85))), "acc2": hx(h, .74, .7), "bg": hx(h, .06, .3),
            "bg2": hx(h, .10, .25), "card": hx(h, .13, .2), "muestra": "#%02x%02x%02x" % best}

def pagina(L, d, pal, fotos, revs):
    cfg = R.get(L["rubro"], DEF); tipo, ver, accion, cta, h1, servs, font = cfg
    wa_neg = re.sub(r"\D", "", d.get("internationalPhoneNumber", "")) or L["wa"]
    q = lambda t: "https://wa.me/%s?text=%s" % (wa_neg, urllib.parse.quote(t))
    n, rat = L["nombre"], ("%.1f" % L["rating"]).replace(".", ",")
    zona = (d.get("shortFormattedAddress") or L["direccion"] or "Santa Cruz").split(",")[0]
    horario = ""
    for t in (d.get("regularOpeningHours") or {}).get("weekdayDescriptions", [])[:7]:
        dia, _, hr = t.partition(": "); horario += f'<div><span>{E(dia.capitalize())}</span><span>{E(hr)}</span></div>'
    img = lambda i: f"img/f{i % len(fotos)}.jpg"
    serif = "'Anton',system-ui,sans-serif" if font == "Anton" else "'Lora',Georgia,serif"
    gal = "".join(f'<div class="{"tall" if i in (0, 3) else ""}"><img src="{img(i+1)}" alt="Foto de {E(n)}" loading="lazy"></div>' for i in range(6))
    rv = "".join(f'<div class="rev"><span class="stars">{"★"*int(r["estrellas"])}</span><q>{E(r["texto"][:220] + ("…" if len(r["texto"])>220 else ""))}</q><div class="who">{E(r["autor"])} · Google</div></div>' for r in revs[:3])
    sv = "".join(f'<div class="ev"><div class="ic">{a}</div><h4>{E(b)}</h4><p>{E(c)}</p></div>' for a, b, c in servs)
    WA = '<svg style="display:none"><symbol id="wa" viewBox="0 0 32 32"><path fill="currentColor" d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3zm6 15.5c-.3-.2-2-1-2.3-1.1-.3-.1-.5-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.3-.7.1-.3-.2-1.4-.5-2.7-1.7-1-.9-1.7-2-1.9-2.3-.2-.3 0-.5.1-.7l.5-.6c.2-.2.2-.4.3-.6.1-.2 0-.4 0-.6l-1-2.5c-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.2-1.2 2.9s1.2 3.4 1.4 3.6c.2.2 2.4 3.6 5.8 5 2.9 1.1 3.4.9 4 .8.6-.1 2-.8 2.3-1.6.3-.8.3-1.5.2-1.6-.1-.2-.3-.3-.6-.4z"/></symbol></svg>'
    return f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(n)} · {E(tipo)} en Santa Cruz</title><meta name="robots" content="noindex">
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Lora:wght@500;600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:{pal["bg"]};--bg2:{pal["bg2"]};--card:{pal["card"]};--ink:#f4f1ea;--muted:#b8b3a8;--acc:{pal["acc"]};--acc2:{pal["acc2"]};--line:rgba(255,255,255,.11)}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:smooth}}body{{background:var(--bg);color:var(--ink);font-family:Inter,system-ui,sans-serif;line-height:1.55;-webkit-font-smoothing:antialiased}}
img{{display:block;width:100%;height:100%;object-fit:cover}}a{{color:inherit;text-decoration:none}}.s{{font-family:{serif};font-weight:500}}
.demo{{position:fixed;top:0;left:0;right:0;z-index:40;background:var(--ink);color:#111;font-size:11px;text-align:center;padding:6px 10px}}
nav{{position:fixed;top:27px;left:0;right:0;z-index:20;display:flex;justify-content:space-between;align-items:center;padding:14px 22px;background:linear-gradient(to bottom,rgba(0,0,0,.6),transparent)}}
.logo{{font-family:{serif};font-size:22px;max-width:60%;line-height:1.1}}.nav-cta{{font-size:13px;font-weight:600;border:1px solid var(--acc2);color:var(--acc2);padding:8px 14px;border-radius:999px;white-space:nowrap}}
.hero{{position:relative;height:100vh;min-height:640px;overflow:hidden}}.hero>img{{position:absolute;inset:0;animation:z 14s ease-out forwards;transform:scale(1.06)}}@keyframes z{{to{{transform:scale(1)}}}}
.hero::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,.3) 30%,var(--bg) 88%)}}
.hc{{position:absolute;left:0;right:0;bottom:0;z-index:2;padding:0 24px 56px}}.eyebrow{{font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:var(--acc2);margin-bottom:14px;font-weight:600}}
.hero h1{{font-family:{serif};font-weight:500;font-size:44px;line-height:1.06;margin-bottom:16px}}.hero h1 em{{color:var(--acc2);font-style:normal}}
.rating{{display:inline-flex;gap:8px;font-size:14px;background:rgba(255,255,255,.1);border:1px solid var(--line);padding:7px 14px;border-radius:999px;margin-bottom:22px;backdrop-filter:blur(6px)}}.stars{{color:#f5c451;letter-spacing:2px}}
.btns{{display:flex;gap:12px;flex-wrap:wrap}}.btn{{display:inline-flex;align-items:center;gap:10px;padding:15px 22px;border-radius:999px;font-weight:600;font-size:15px}}
.btn-wa{{background:#25d366;color:#08210f;box-shadow:0 10px 30px rgba(37,211,102,.35)}}.btn-g{{border:1px solid rgba(255,255,255,.4)}}.wi{{width:20px;height:20px}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:26px 24px;background:var(--bg2);border-block:1px solid var(--line)}}.stat{{text-align:center}}.stat b{{display:block;font-family:{serif};font-size:28px;color:var(--acc)}}.stat span{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.12em}}
section{{padding:72px 24px}}.sh{{margin-bottom:28px}}.sh h2{{font-family:{serif};font-weight:500;font-size:34px;line-height:1.1}}.sh p{{color:var(--muted);margin-top:10px}}
.spaces{{display:grid;gap:14px}}.space{{position:relative;height:360px;border-radius:22px;overflow:hidden}}.space::after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 50%,rgba(0,0,0,.8))}}.space .cap{{position:absolute;left:20px;bottom:18px;z-index:2}}.cap small{{color:var(--acc2);letter-spacing:.2em;text-transform:uppercase;font-size:11px}}.cap h3{{font-family:{serif};font-weight:500;font-size:25px}}
.events{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.ev{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:20px}}.ev .ic{{font-size:26px;margin-bottom:10px}}.ev h4{{font-size:16px}}.ev p{{font-size:13px;color:var(--muted)}}
.gallery{{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:170px;gap:10px}}.gallery div{{border-radius:14px;overflow:hidden}}.gallery .tall{{grid-row:span 2}}
.reviews{{display:grid;gap:14px}}.rev{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:22px}}.rev q{{font-family:Lora,Georgia,serif;font-size:18px;line-height:1.45;display:block;margin:10px 0 12px}}.who{{font-size:13px;color:var(--muted)}}
.hours{{background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin-top:26px;text-align:left}}.hours div{{display:flex;justify-content:space-between;gap:12px;padding:12px 18px;border-bottom:1px solid var(--line);font-size:14px}}.hours div:last-child{{border:0}}
.cta{{position:relative;overflow:hidden;text-align:center;padding:96px 24px}}.cta>img{{position:absolute;inset:0;opacity:.3}}.cta .in{{position:relative;z-index:2;max-width:560px;margin:auto}}.cta h2{{font-family:{serif};font-weight:500;font-size:36px;line-height:1.1;margin-bottom:14px}}.cta p{{color:#e4dfd4;margin-bottom:26px}}
.info{{display:grid;gap:8px;margin-top:28px;font-size:14px;color:#ddd8cb}}footer{{padding:30px 24px 110px;text-align:center;font-size:12px;color:var(--muted);border-top:1px solid var(--line)}}
.fwa{{position:fixed;right:18px;bottom:20px;z-index:30;width:60px;height:60px;border-radius:50%;background:#25d366;display:grid;place-items:center;color:#fff;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
@media(min-width:900px){{.hero h1{{font-size:72px}}.hc{{padding:0 8vw 80px}}section{{padding:110px 8vw}}.spaces{{grid-template-columns:repeat(3,1fr)}}.events{{grid-template-columns:repeat(4,1fr)}}.gallery{{grid-template-columns:repeat(4,1fr);grid-auto-rows:230px}}.reviews{{grid-template-columns:repeat(3,1fr)}}}}
</style></head><body>{WA}
<div class="demo">Demo de propuesta para {E(n)} · hecha por Pixel Studio Bolivia</div>
<nav><div class="logo">{E(n)}</div><a class="nav-cta" href="#reservar">{E(cta)}</a></nav>
<header class="hero"><img src="{img(0)}" alt="{E(n)}"><div class="hc">
<div class="eyebrow">{E(tipo)} · {E(zona)}</div><h1>{h1}</h1>
<div class="rating"><span class="stars">★★★★★</span> {rat} · {L["resenas"]} reseñas en Google</div>
<div class="btns"><a class="btn btn-wa" href="{q(f"Hola {n}, quiero {accion}")}"><svg class="wi"><use href="#wa"/></svg>{E(cta)} por WhatsApp</a><a class="btn btn-g" href="#espacios">{E(ver)}</a></div></div></header>
<div class="stats"><div class="stat"><b>{rat}★</b><span>En Google</span></div><div class="stat"><b>{L["resenas"]}+</b><span>Reseñas</span></div><div class="stat"><b>📍</b><span>{E(zona[:18])}</span></div></div>
<section id="espacios"><div class="sh"><div class="eyebrow">Conócenos</div><h2>Así es {E(n)}</h2></div><div class="spaces">
<div class="space"><img src="{img(1)}" alt="" loading="lazy"><div class="cap"><small>{E(tipo)}</small><h3>Nuestro lugar</h3></div></div>
<div class="space"><img src="{img(2)}" alt="" loading="lazy"><div class="cap"><small>Lo que hacemos</small><h3>Hecho con dedicación</h3></div></div>
<div class="space"><img src="{img(3)}" alt="" loading="lazy"><div class="cap"><small>Te esperamos</small><h3>En {E(zona[:30])}</h3></div></div></div></section>
<section style="background:var(--bg2)"><div class="sh"><div class="eyebrow">Servicios</div><h2>¿Qué encuentras aquí?</h2></div><div class="events">{sv}</div></section>
<section><div class="sh"><div class="eyebrow">Galería</div><h2>Mira por ti mismo</h2></div><div class="gallery">{gal}</div></section>
<section style="background:var(--bg2)"><div class="sh"><div class="eyebrow">Opiniones</div><h2>Lo que dicen nuestros clientes</h2><p>{rat} estrellas con {L["resenas"]} reseñas en Google.</p></div><div class="reviews">{rv}</div></section>
<section class="cta" id="reservar"><img src="{img(4)}" alt=""><div class="in"><div class="eyebrow">Escríbenos</div><h2>{E(cta)} en un minuto</h2><p>Te respondemos por WhatsApp.</p>
<a class="btn btn-wa" href="{q(f"Hola {n}, quiero {accion}")}"><svg class="wi"><use href="#wa"/></svg>{E(cta)} por WhatsApp</a>
<div class="info"><div>📍 {E(L["direccion"] or "")}</div><div>📞 {E(L["telefono"])}</div><div><a href="{E(L["maps"])}" style="color:var(--acc2)">Ver en Google Maps →</a></div></div>
{f'<div class="hours">{horario}</div>' if horario else ""}</div></section>
<footer>© {E(n)} · Página demo creada por Pixel Studio Bolivia</footer>
<a class="fwa" href="{q(f"Hola {n}")}" aria-label="WhatsApp"><svg style="width:30px;height:30px"><use href="#wa"/></svg></a>
</body></html>'''

leads = json.load(open(LEADS, encoding="utf-8"))
CADENA = re.compile(r"(sucursal|suc\.|\bsuc\b| - |ace hardware|burger king|pollos copacabana|subway|mcdonald|kfc|dumbo|la casa del camba)", re.I)
base_vistos, por_rubro, lote = set(), collections.Counter(), []
DET = "id,internationalPhoneNumber,shortFormattedAddress,regularOpeningHours,photos,reviews,websiteUri"
for L in leads:
    if len(lote) >= N: break
    base = re.split(r" - | \| ", L["nombre"])[0].strip().lower()
    if CADENA.search(L["nombre"]) or base in base_vistos or not L["wa"]: continue
    if por_rubro[L["rubro"]] >= max(3, N // 8): continue
    if os.path.exists(os.path.join(REPO, L["slug"])): continue
    base_vistos.add(base)
    try:
        d = json.loads(get(f"https://places.googleapis.com/v1/places/{L['id']}?languageCode=es",
                           {"X-Goog-Api-Key": KEY, "X-Goog-FieldMask": DET}))
        if d.get("websiteUri") and not L["redes"]: continue
        raw = []
        for ph in d.get("photos", [])[:7]:
            try: raw.append(get(f"https://places.googleapis.com/v1/{ph['name']}/media?maxWidthPx=1100&key={KEY}"))
            except Exception: pass
        if len(raw) < 5: continue
        revs = [{"autor": (r.get("authorAttribution", {}).get("displayName", "Cliente").split()[0] + " " +
                           (r.get("authorAttribution", {}).get("displayName", "C").split()[-1][:1] + ".")),
                 "estrellas": r.get("rating", 5), "texto": (r.get("text") or {}).get("text", "")}
                for r in d.get("reviews", []) if (r.get("rating") or 0) >= 4 and len((r.get("text") or {}).get("text", "")) > 25]
        if len(revs) < 2: continue
        pal = paleta(raw)
        dd = os.path.join(REPO, L["slug"], "img"); os.makedirs(dd, exist_ok=True)
        for i, b in enumerate(raw):
            im = Image.open(io.BytesIO(b)).convert("RGB"); im.thumbnail((1000, 1000)); im.save(os.path.join(dd, f"f{i}.jpg"), quality=80)
        open(os.path.join(REPO, L["slug"], "index.html"), "w", encoding="utf-8").write(pagina(L, d, pal, raw, revs))
        L.update({"paleta": pal, "resena_destacada": revs[0]["texto"][:140],
                  "demo": f"https://dylan120-boop.github.io/pixel-demos/{L['slug']}/"})
        lote.append(L); por_rubro[L["rubro"]] += 1
        print("OK", L["nombre"], L["rubro"], pal["acc"], flush=True)
    except Exception as e:
        print("falló", L["nombre"], e, file=sys.stderr)
json.dump(lote, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("demos:", len(lote))
