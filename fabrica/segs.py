#!/usr/bin/env python3
"""Divide la voz en 9 frases usando los silencios. Uso: python3 segs.py voz.mp3 > seg.json"""
import sys, subprocess, re, json
f = sys.argv[1]
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())
log = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", log)]
en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
gaps = [(s, e) for s, e in zip(st, en) if s > 0.3 and e < dur - 0.2]
start = en[0] if st and st[0] < 0.05 and en else 0.05
end = st[-1] if st and st[-1] > dur - 1.5 and len(st) > len(gaps) else dur
gaps = sorted(sorted(gaps, key=lambda g: g[1] - g[0], reverse=True)[:8])
pts = [start] + [x for g in gaps for x in g] + [end]
seg = [[round(pts[i], 2), round(pts[i + 1], 2)] for i in range(0, len(pts) - 1, 2)]
while len(seg) < 9:  # por si hay pocas pausas: partir el segmento más largo
    i = max(range(len(seg)), key=lambda k: seg[k][1] - seg[k][0]); a, b = seg[i]; m = (a + b) / 2
    seg[i:i + 1] = [[a, round(m - .05, 2)], [round(m + .05, 2), b]]
print(json.dumps(seg[:9]))
