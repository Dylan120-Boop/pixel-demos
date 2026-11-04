import json, numpy as np, wave, sys
SR = 44100
seg = json.load(open('seg.json'))
END = seg[8][1] + 1.2
N = int(END * SR) + SR
out = np.zeros(N)
rng = np.random.default_rng(3)

def add(sig, t, gain=1.0):
    i = int(t * SR)
    if i < 0: return
    j = min(N, i + len(sig))
    out[i:j] += sig[:j - i] * gain

def env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a) * np.exp(-t / r)
    return e

def whoosh(d=0.5, up=True):
    n = int(d * SR); x = rng.standard_normal(n)
    # simple moving-average lowpass with varying window -> sweep
    t = np.linspace(0, 1, n)
    y = np.zeros(n); acc = 0
    for k in range(n):
        a = 0.02 + 0.25 * (t[k] if up else 1 - t[k])
        acc += a * (x[k] - acc); y[k] = acc
    e = np.sin(np.pi * t) ** 2
    return y * e * 2.2

def pop(f=900, d=0.12):
    n = int(d * SR); t = np.arange(n) / SR
    fr = f * (1 + 1.5 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.002, 0.04)

def click():
    n = int(0.03 * SR); return rng.standard_normal(n) * env(n, 0.0005, 0.006) * 0.5

def ding():
    n = int(1.0 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) * g for f, g in [(1318, 1), (1976, .5), (2637, .25)])
    return s * env(n, 0.003, 0.35) * 0.35

def thump():
    n = int(0.35 * SR); t = np.arange(n) / SR
    fr = 50 + 120 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * env(n, 0.002, 0.12) * 1.2

S = seg; L4, L5, L8 = S[3][0], S[4][0], S[7][0]
add(whoosh(0.6), 0.0, 0.5)
add(pop(1200), 0.55, 0.5)
add(whoosh(0.4), S[1][0] - 0.2, 0.5)
add(thump(), S[1][0] + 0.4, 0.9)          # sello SIN PÁGINA WEB
qa = S[2][0] + 0.4; qs = S[2][1] - S[2][0]
for d in (0, .18, .36): add(pop(700 + d * 900), qa + d * qs * 1.5, 0.55)
add(whoosh(0.5), L4 - 0.25, 0.55)
ts, te = L4 + 0.3, L4 + 0.3 + (L5 - L4) * 0.6
for t in np.arange(ts, te, 0.065): add(click(), t + rng.uniform(-.01, .01), 0.35)
add(ding(), L5 - 0.1, 0.8)
add(whoosh(0.7, False), L5 - 0.1, 0.6)
for a in (S[5][0] + 0.1, S[5][0] + 1.8, S[5][0] + 3.3, S[6][0] + 0.7): add(pop(1000), a, 0.4)
add(pop(1500, 0.08), S[6][0] + 1.3, 0.6)   # tap
add(whoosh(0.6), L8 - 0.2, 0.55)
add(thump(), L8 + 0.1, 0.5)
add(pop(1300), S[8][0] + 1.0, 0.5)

out = out / max(1e-9, np.abs(out).max()) * 0.6
with wave.open('sfx.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print('ok', END)
