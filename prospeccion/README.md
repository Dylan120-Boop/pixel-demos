# Prospección a escala (Pixel Studio)

1. `python3 prospectar.py "$PLACES_KEY" /tmp/leads.json excluir.txt`
   Recorre 24 rubros x 12 zonas de Santa Cruz y guarda los negocios sin web propia (o solo con redes),
   con celular, ≥4,2★ y ≥10 reseñas, ordenados por puntaje.
2. `python3 generar_demos.py "$PLACES_KEY" /tmp/leads.json 15 .. /tmp/lote.json`
   Hace demos automáticas para los mejores (sin cadenas ni sucursales, rubros variados):
   fotos y reseñas reales, y la paleta de colores sacada de sus fotos.
3. El seguimiento (enviado → respondió → llamada → cliente) se lleva en el tablero "Embudo de clientes".

Ojo: la clave de Google Places tiene un tope de 100 búsquedas y 100 fichas por día.
La lista de prospectos no se sube a este repo porque es público.
