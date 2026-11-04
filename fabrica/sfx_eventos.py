#!/usr/bin/env python3
"""Efectos de sonido a partir de una lista de eventos.
Uso: python3 sfx_eventos.py eventos.json sfx.wav
eventos.json: {"dur": 55.0, "ev": [["whoosh", 1.2, 0.5], ["pop", 2.0, 0.4, 900], ["tick", 3.1, 0.3], ["ding", 4, 0.8], ["thump", 4, 0.7], ["click", 5, 0.3]]}
"""
import json, sys, wave, numpy as np
SR = 44100
cfg = json.load(open(sys.argv[1])); N = int((cfg["dur"] + 1.5) * SR); out = np.zeros(N); rng = np.random.default_rng(3)
def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / r)
def whoosh(d=0.5, up=True):
    n = int(d * SR); x = rng.standard_normal(n); t = np.linspace(0, 1, n); y = np.zeros(n); acc = 0
    for k in range(n):
        a = 0.02 + 0.25 * (t[k] if up else 1 - t[k]); acc += a * (x[k] - acc); y[k] = acc
    return y * np.sin(np.pi * t) ** 2 * 2.2
def pop(f=900, d=0.12):
    n = int(d * SR); t = np.arange(n) / SR; fr = f * (1 + 1.5 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.002, 0.04)
def click():
    n = int(0.03 * SR); return rng.standard_normal(n) * env(n, 0.0005, 0.006) * 0.5
def tick():
    n = int(0.04 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2400 * t) * 0.6 + rng.standard_normal(n) * 0.4) * env(n, 0.0005, 0.008)
def ding():
    n = int(1.2 * SR); t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * t) * g for f, g in [(1318, 1), (1976, .5), (2637, .25)]) * env(n, 0.003, 0.4) * 0.35
def thump():
    n = int(0.35 * SR); t = np.arange(n) / SR; fr = 50 + 120 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.002, 0.12) * 1.2
G = {"whoosh": lambda e: whoosh(e[3] if len(e) > 3 else 0.5), "pop": lambda e: pop(e[3] if len(e) > 3 else 900), "click": lambda e: click(),
     "tick": lambda e: tick(), "ding": lambda e: ding(), "thump": lambda e: thump()}
for e in cfg["ev"]:
    s = G[e[0]](e); i = int(e[1] * SR)
    if 0 <= i < N: j = min(N, i + len(s)); out[i:j] += s[:j - i] * e[2]
out = out / max(1e-9, np.abs(out).max()) * 0.6
with wave.open(sys.argv[2], "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
print("ok", len(cfg["ev"]), "eventos")
