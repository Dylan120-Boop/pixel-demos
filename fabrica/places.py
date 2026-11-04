#!/usr/bin/env python3
"""Busca negocios en Santa Cruz SIN página web usando Google Places API (New).
Uso: python3 places.py <API_KEY> <N> <excluir.txt> <salida_dir>
Escribe <salida_dir>/candidatos.json y descarga hasta 6 fotos por negocio en <salida_dir>/<slug>/img/.
"""
import sys, json, os, re, random, unicodedata, urllib.request

KEY, N, EXCL, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
RUBROS = ["salón de eventos", "restaurante", "pizzería", "hamburguesería", "cafetería", "pastelería",
          "barbería", "salón de belleza", "spa", "uñas nail bar", "gimnasio", "veterinaria",
          "tienda de ropa", "boutique", "perfumería", "florería", "lavadero de autos", "taller mecánico",
          "consultorio dental", "óptica", "ferretería", "cancha sintética", "hotel boutique", "heladería"]
ZONAS = ["Equipetrol", "Zona Norte", "Urubó", "centro", "Av. Banzer", "Av. Beni", "Av. Alemana",
         "Av. Santos Dumont", "Av. Piraí", "Plan 3000", "Villa 1ro de Mayo", "Av. Cristo Redentor"]

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40]

def post(url, body, mask):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
        headers={"Content-Type": "application/json", "X-Goog-Api-Key": KEY, "X-Goog-FieldMask": mask})
    return json.load(urllib.request.urlopen(req, timeout=30))

excl = set()
if os.path.exists(EXCL):
    excl = {l.strip() for l in open(EXCL, encoding="utf-8") if l.strip()}

MASK = ("places.id,places.displayName,places.rating,places.userRatingCount,places.websiteUri,"
        "places.nationalPhoneNumber,places.internationalPhoneNumber,places.formattedAddress,"
        "places.primaryTypeDisplayName,places.photos,places.reviews,places.googleMapsUri,places.businessStatus")
random.seed()
found, tried = [], 0
combos = [(r, z) for r in RUBROS for z in ZONAS]
random.shuffle(combos)
seen_rubros = set()
for rubro, zona in combos:
    if len(found) >= N or tried > 40:
        break
    if rubro in seen_rubros:  # variedad: 1 negocio por rubro por día
        continue
    tried += 1
    try:
        res = post("https://places.googleapis.com/v1/places:searchText",
                   {"textQuery": f"{rubro} {zona} Santa Cruz de la Sierra Bolivia", "languageCode": "es",
                    "maxResultCount": 20}, MASK)
    except Exception as e:
        print("error búsqueda", rubro, zona, e); continue
    for p in res.get("places", []):
        name = p.get("displayName", {}).get("text", "")
        s = slug(name)
        if (p.get("websiteUri") or not p.get("nationalPhoneNumber") or p.get("businessStatus") not in (None, "OPERATIONAL")
                or (p.get("rating") or 0) < 4.3 or (p.get("userRatingCount") or 0) < 15
                or len(p.get("photos", [])) < 4 or s in excl or p["id"] in excl):
            continue
        d = os.path.join(OUT, s, "img"); os.makedirs(d, exist_ok=True)
        imgs = []
        for i, ph in enumerate(p["photos"][:6]):
            try:
                u = f"https://places.googleapis.com/v1/{ph['name']}/media?maxWidthPx=1200&key={KEY}"
                data = urllib.request.urlopen(u, timeout=30).read()
                fn = f"f{i}.jpg"; open(os.path.join(d, fn), "wb").write(data); imgs.append(fn)
            except Exception as e:
                print("foto falló", name, e)
        if len(imgs) < 4:
            continue
        revs = [{"autor": (r.get("authorAttribution", {}).get("displayName", "Cliente").split(" ")[0] + " " +
                           (r.get("authorAttribution", {}).get("displayName", " ").split(" ")[-1][:1] + ".")).strip(),
                 "estrellas": r.get("rating"), "texto": (r.get("text") or {}).get("text", "")}
                for r in p.get("reviews", []) if (r.get("rating") or 0) >= 4 and (r.get("text") or {}).get("text")][:4]
        found.append({"id": p["id"], "slug": s, "nombre": name, "rubro": rubro,
                      "categoria": p.get("primaryTypeDisplayName", {}).get("text", rubro),
                      "rating": p.get("rating"), "resenas": p.get("userRatingCount"),
                      "telefono": p.get("nationalPhoneNumber"), "telefono_int": p.get("internationalPhoneNumber"),
                      "direccion": p.get("formattedAddress"), "maps": p.get("googleMapsUri"),
                      "fotos": imgs, "resenas_texto": revs})
        seen_rubros.add(rubro)
        print("OK", name, p.get("rating"), p.get("userRatingCount"))
        break
json.dump(found, open(os.path.join(OUT, "candidatos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total", len(found))
