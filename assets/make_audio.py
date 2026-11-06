import numpy as np, wave, struct, sys

SR = 44100

def t(dur): return np.arange(int(SR*dur))/SR

def env(n, a, r, total):
    """attack/release envelope over n samples within total length"""
    e = np.ones(n)
    an = max(1, int(a*SR)); rn = max(1, int(r*SR))
    an = min(an, n); rn = min(rn, n)
    e[:an] = np.linspace(0,1,an)
    if rn < n: e[-rn:] *= np.linspace(1,0,rn)
    return e

def osc(kind, f, n, detune=0.0):
    tt = t(n/SR)
    if kind == 'saw':
        x = 2*((f*(1+detune)*tt) % 1.0) - 1
    elif kind == 'square':
        x = np.sign(np.sin(2*np.pi*f*(1+detune)*tt))
    else:  # sine
        x = np.sin(2*np.pi*f*(1+detune)*tt)
    return x

def note(freq, dur, kind='saw', a=0.01, r=0.3, vol=0.22, detunes=(0,0.004,-0.004), sub=0.0, lp=0.5):
    n = int(dur*SR)
    x = np.zeros(n)
    for d in detunes:
        x += osc(kind, freq, n, d)
    x /= max(1,len(detunes))
    if sub > 0:
        x += sub*np.sin(2*np.pi*freq/2*t(dur))
    # simple one-pole lowpass
    if lp < 1:
        alpha = min(0.999, lp)
        out = np.zeros(n); acc = 0.0
        for i in range(n):
            acc += alpha*(x[i]-acc); out[i] = acc
        x = out
    x *= env(n, a, r, dur) * vol
    return x

def place(buf, snd, at):
    i = int(at*SR)
    j = min(len(buf), i+len(snd))
    if i < len(buf): buf[i:j] += snd[:j-i]

def noise_sweep(dur, f_start, f_end, vol=0.08, q=8):
    n = int(dur*SR)
    rng = np.random.default_rng(7)
    x = rng.standard_normal(n)*0.3
    # time-varying resonant filter via short segments
    segs = 24
    out = np.zeros(n)
    step = n//segs
    for s in range(segs):
        fc = f_start + (f_end-f_start)*s/(segs-1)
        seg = x[s*step:(s+1)*step]
        if len(seg)==0: continue
        # biquad bandpass approximation: two one-poles
        w = 2*np.pi*min(fc, SR/2-100)/SR
        al = (1-np.cos(w))/ (1+np.cos(w)) * q if q>0 else 0
        y = np.zeros_like(seg); v1=v2=0.0
        a1 = 2*al/(1+al); a2 = (1-al)/(1+al)
        for i in range(len(seg)):
            v = a1*(seg[i] - v2) - a2*v1
            v2 = v1; v1 = v
            y[i] = v2 + al*seg[i]
        out[s*step:s*step+len(seg)] = y
    out *= env(n, dur*0.4, dur*0.5, dur) * vol
    m = np.max(np.abs(out)) or 1
    return out/m

def kick(dur=0.42, f0=150, vol=0.85):
    n = int(dur*SR); tt = t(dur)
    f = f0*np.exp(-tt*22)+42
    ph = 2*np.pi*np.cumsum(f)/SR
    x = np.sin(ph)*np.exp(-tt*9)
    click = rng_click(n)
    x += 0.25*click*np.exp(-tt*180)
    return x*vol

def rng_click(n):
    rng = np.random.default_rng(3)
    return rng.standard_normal(n)

def snare(dur=0.28, vol=0.5):
    n = int(dur*SR); tt = t(dur)
    rng = np.random.default_rng(11)
    x = rng.standard_normal(n)*np.exp(-tt*22)
    x += 0.4*np.sin(2*np.pi*185*tt)*np.exp(-tt*30)
    return x*vol

def hat(dur=0.09, vol=0.22, open_=False):
    dur = dur if not open_ else 0.24
    n = int(dur*SR); tt = t(dur)
    rng = np.random.default_rng(5)
    x = rng.standard_normal(n)
    # highpass approx: difference
    x = np.diff(x, prepend=0)
    x *= np.exp(-tt*(18 if not open_ else 7))
    return x*vol

# ---- Arrangement: 110 BPM, Am - F - C - G progression, moody synthwave
BPM = 110
B = 60/BPM  # bar beat = one beat; bar = 4 beats

TOTAL = 44.0
buf = np.zeros(int(TOTAL*SR))

# Chords (Am, F, C, G) as midi notes
A3,F3,C3,G3 = 220.00, 174.61, 130.81, 196.00
C4,E4,A4 = 261.63, 329.63, 440.00
F4,A4b = 349.23, 440.00
E4,G4,C5 = 329.63, 392.00, 523.25
D4,G4b,B4 = 293.66, 369.99, 493.88
B3,D4f,F4f = 246.94, 293.66, 349.23

chords = [
    [A3, C4, E4],        # Am
    [F3, A4b, C4*2/1],   # F  (A4b = A4)
    [C3*2, E4, G4],      # C
    [G3, B3, D4f],       # G
]
chords[1] = [F3, 220.00, 261.63]     # F: F A C
chords[3] = [196.00, 246.94, 293.66] # G: G B D

bar_len = 4*B
# Pad layer: full length, evolves
pos = 0.0
ci = 0
while pos < TOTAL-0.5:
    ch = chords[ci % 4]
    dur = min(bar_len*2, TOTAL-pos)
    for k, f in enumerate(ch):
        snd = note(f, dur, kind='saw', a=0.9, r=1.4, vol=0.055, detunes=(0, 0.006, -0.006), sub=0.25, lp=0.28)
        place(buf, snd, pos + k*0.03)
    pos += bar_len*2
    ci += 1

# Bass line: eighth-note pulse entering at 4s
pos = 4.0
ci = 0
roots = [A3/2, F3/2, C3, G3/2]
while pos < TOTAL-1:
    root = roots[ci % 4]
    for e in range(8):
        at = pos + e*B/2
        if at >= TOTAL-0.6: break
        dur = B/2*0.9
        accent = 1.0 if e % 2 == 0 else 0.62
        snd = note(root, dur, kind='saw', a=0.005, r=0.12, vol=0.30*accent, detunes=(0,), sub=0.9, lp=0.42)
        place(buf, snd, at)
    pos += bar_len; ci += 1

# Lead arp: 16th-note sparkle entering at 12s
arp_notes = [440.00, 523.25, 659.26, 880.00, 659.26, 523.25]
pos = 12.0
ci = 0
while pos < TOTAL-1:
    root_oct = [220, 174.61, 261.63, 196][ci % 4]
    seq = [n*2 for n in arp_notes]
    for e in range(16):
        at = pos + e*B/4
        if at >= TOTAL-0.7: break
        f = seq[e % len(seq)] * (2 if (ci % 4) in (2,) else 1)
        if e % 8 in (3, 6): continue  # syncopation gaps
        snd = note(f, B/4*1.6, kind='square', a=0.004, r=0.18, vol=0.075, detunes=(0, 0.003), lp=0.75)
        place(buf, snd, at)
    pos += bar_len; ci += 1

# Drums
pos = 8.0; ci = 0
while pos < TOTAL-1:
    # kick on 1 and 3 (+ syncopation)
    for beat in (0, 1.5, 2, 3.5):
        at = pos + beat*B
        if at < TOTAL-0.5: place(buf, kick(), at)
    # snare on 2 and 4
    for beat in (1, 3):
        at = pos + beat*B
        if at < TOTAL-0.5: place(buf, snare(), at)
    # hats 8ths
    for e in range(8):
        at = pos + e*B/2
        if at < TOTAL-0.4: place(buf, hat(open_=(e==7)), at, ) if False else place(buf, hat(open_=(e==6)), at)
    pos += bar_len; ci += 1

# Risers + impacts at section boundaries
for at in (12.0, 28.0):
    place(buf, noise_sweep(3.0, 300, 6000, vol=0.10), at-3.0)
# Final hit
place(buf, kick(0.9, 120, 0.9), TOTAL-1.2)
place(buf, noise_sweep(1.2, 2000, 100, vol=0.12), TOTAL-1.2)

# Gentle master fade in/out
n = len(buf)
buf[:int(0.8*SR)] *= np.linspace(0,1,int(0.8*SR))
buf[int((TOTAL-2.0)*SR):] *= np.linspace(1,0,n-int((TOTAL-2.0)*SR))

# Soft clip + normalize
buf = np.tanh(buf*1.4)*0.92
peak = np.max(np.abs(buf)); buf = buf/peak*0.95

pcm = (buf*32767).astype('<i2')
with wave.open(r"C:\Users\bobyr\Documents\Clouder Ripple\gmi-showcase\assets\soundtrack.wav", 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("OK", len(buf)/SR, "seconds")
