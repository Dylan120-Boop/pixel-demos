#!/usr/bin/env python3
"""Barrido grande de prospectos: negocios de Santa Cruz sin página web (o solo con redes).
Uso: python3 prospectar.py <API_KEY> <salida.json> [excluir.txt]
Recorre todos los rubros x zonas de places.py, deduplica, filtra y puntúa.
"""
import sys, json, os, re, unicodedata, urllib.request, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "fabrica"))
KEY, OUT = sys.argv[1], sys.argv[2]
EXCL = sys.argv[3] if len(sys.argv) > 3 else ""
RUBROS = ["salón de eventos", "restaurante", "pizzería", "hamburguesería", "cafetería", "pastelería",
          "barbería", "salón de belleza", "spa", "uñas nail bar", "gimnasio", "veterinaria",
          "tienda de ropa", "boutique", "perfumería", "florería", "lavadero de autos", "taller mecánico",
          "consultorio dental", "óptica", "ferretería", "cancha sintética", "hotel boutique", "heladería"]
ZONAS = ["Equipetrol", "Zona Norte", "Urubó", "centro", "Av. Banzer", "Av. Beni", "Av. Alemana",
         "Av. Santos Dumont", "Av. Piraí", "Plan 3000", "Villa 1ro de Mayo", "Av. Cristo Redentor"]
REDES = ("instagram.com", "facebook.com", "fb.com", "linktr.ee", "wa.me", "whatsapp", "tiktok.com", "linkin.bio", "beacons.ai")
MASK = ("places.id,places.displayName,places.rating,places.userRatingCount,places.websiteUri,"
        "places.nationalPhoneNumber,places.internationalPhoneNumber,places.formattedAddress,"
        "places.primaryTypeDisplayName,places.photos,places.googleMapsUri,places.businessStatus")

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40]

def buscar(rz):
    rubro, zona = rz
    req = urllib.request.Request("https://places.googleapis.com/v1/places:searchText", method="POST",
        data=json.dumps({"textQuery": f"{rubro} {zona} Santa Cruz de la Sierra Bolivia", "languageCode": "es",
                         "maxResultCount": 20}).encode(),
        headers={"Content-Type": "application/json", "X-Goog-Api-Key": KEY, "X-Goog-FieldMask": MASK})
    try:
        return rubro, zona, json.load(urllib.request.urlopen(req, timeout=30)).get("places", [])
    except Exception as e:
        print("error", rubro, zona, e, file=sys.stderr); return rubro, zona, []

excl = {l.strip() for l in open(EXCL, encoding="utf-8")} if EXCL and os.path.exists(EXCL) else set()
leads = {}
with cf.ThreadPoolExecutor(8) as ex:
    for rubro, zona, places in ex.map(buscar, [(r, z) for r in RUBROS for z in ZONAS]):
        for p in places:
            web = (p.get("websiteUri") or "").lower()
            redes = web if any(r in web for r in REDES) else ""
            if web and not redes: continue                       # ya tiene web propia
            if not p.get("nationalPhoneNumber"): continue
            if p.get("businessStatus") not in (None, "OPERATIONAL"): continue
            rating, n = p.get("rating") or 0, p.get("userRatingCount") or 0
            if rating < 4.2 or n < 10: continue
            name = p.get("displayName", {}).get("text", "")
            s = slug(name)
            if s in excl or p["id"] in excl or p["id"] in leads: continue
            fotos = len(p.get("photos", []))
            tel = re.sub(r"\D", "", p.get("internationalPhoneNumber") or "")
            movil = tel.startswith("5916") or tel.startswith("5917")   # celulares bolivianos -> WhatsApp
            ig = re.search(r"instagram\.com/([A-Za-z0-9_.]+)", web)
            score = round(rating * 10 + min(n, 400) / 10 + (8 if redes else 0) + (10 if movil else -15), 1)
            leads[p["id"]] = {"id": p["id"], "slug": s, "nombre": name, "rubro": rubro, "zona": zona,
                "categoria": p.get("primaryTypeDisplayName", {}).get("text", rubro), "rating": rating, "resenas": n,
                "fotos": fotos, "telefono": p.get("nationalPhoneNumber"), "wa": tel if movil else "",
                "redes": redes, "instagram": ig.group(1) if ig else "", "direccion": p.get("formattedAddress"),
                "maps": p.get("googleMapsUri"), "score": score}
out = sorted(leads.values(), key=lambda x: -x["score"])
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("prospectos:", len(out), "| con WhatsApp:", sum(1 for x in out if x["wa"]), "| solo redes:", sum(1 for x in out if x["redes"]))
