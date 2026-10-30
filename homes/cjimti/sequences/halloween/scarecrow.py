"""Scarecrow: a straw man stands in the porch at sundown and a flock of crows decides he's harmless.

The porch notch is the scarecrow, as seen from the street: Porch Front is his patched hat, the back
halves of Porch Left and Porch Right are his straw face with a stitched button eye on each, the front
halves are his plaid shirt, and his arms stick out along the inner ends of Left and Right, ending in
straw hands. The outer wings are a bright, living sunset sky (clouds drifting, colours moving, gusts
of wind sweeping along the roof that ripple his straw and his plaid, loose straw blowing past). Side
is the field behind him: a wheat field rippling in the wind at the front, the sun going down at the
back, and, later, the moon coming up.

A flock streams over the house, and seven crows (big dark silhouettes with sweeping wings and a glint
of an eye) fly in one at a time from the left corner and the free end of Right, land and caw. To a
sneaky tune they hop closer in little sideways hops, one crow per beat; every hop sends a ripple of
light along the roof and the sky pulses on the beat, harder as the tune builds; on every fourth beat
they all look away, innocently. The bravest pecks his right hand and tugs out a straw. Silence; the
house dims; his eyes slowly light up. Ah... ah... AH (light is drawn in from both ends of the house
on each breath)... CHOO: a flash rolls out to both ends, straw dust blows everywhere, every crow and
a storm of others burst off the roof in all directions, and feathers rain down. Then, under the
rising moon, the smallest crow flutters back, along his arm and up his body, and lands right on top
of his hat. He looks up at it, and sighs.

Everything lives in path distance (layout units along the roofline) and is drawn by exact
span-over-pixel coverage, so shapes keep their size on every run."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, colormap, Flicker, nframes

CODE = 'HW15'
TITLE = 'Scarecrow'
KIND = 'show'
DESCRIPTION = ('A flock of crows lands on the roof and creeps up on the scarecrow standing in the porch, '
               'braver with every hop, until one pecks his hand. Then he sneezes.')
VOICEOVER = ("Out in the field at sundown, the scarecrow stands very, very still. "
             "The crows think he's only straw... let's see.")

D = 70.0
B = 0.625                                   # 96 BPM: the tiptoe tune and the hops share this beat
TT0 = 24.0                                  # the hopping starts (beat 0)
FLY = 2.2                                   # arrival flight time
TPECK = [TT0 + B * k for k in (28, 28.5, 29, 29.5)]
TUG = TT0 + B * 30                          # 42.75: the last peck pulls a straw out; the music stops
EYES = (45.0, 47.6)                         # his eyes slowly light up
AHS = [47.9, 48.7, 49.5]                    # ah... ah... AH...
SQUINT = 50.0
CHOO = 50.3
TRET = 55.5                                 # the small crow comes back
THAT = 62.0                                 # ... and lands on his hat
LOOKUP = 62.5                               # his eyes open and look up at it
SIGH = (63.6, 65.8)
FADE = (67.5, 70.0)
MOON = (53.5, 61.0)

ARM, HAND = 150.0, 32.0                     # arm length along each wing (the last HAND units are the hand)
CS = 1.6                                    # crow scale: about 50 units beak to tail, wings sweep ~30 each side

# perching crows: (side, arrival time, landing spot, goal, small), spots in units from the wing's reference
# (Right: from the porch corner dR0; Left: from the left corner dL0). Index 0 pecks; index 4 is the small one.
SPEC = [('R', 6.0, 250.0, 173.0, False),
        ('L', 8.6, 180.0, 300.0, False),
        ('R', 11.0, 330.0, 250.0, False),
        ('L', 13.4, 110.0, 205.0, False),
        ('R', 20.6, 452.0, 390.0, True),
        ('R', 15.8, 395.0, 318.0, False),
        ('L', 18.0, 42.0, 128.0, False)]
NC = len(SPEC)
ARRIVE_CAWS = [(i, SPEC[i][1] + FLY + 0.3, 2 if i in (0, 2) else 1) for i in range(NC)]
BRAVE_CAW = (0, TT0 + B * 27, 2)
CAWS = ARRIVE_CAWS + [BRAVE_CAW, (4, THAT + 0.35, 1), (4, 67.0, 1)]
CAW_LEN, CAW_GAP = 0.3, 0.42
HOP_BARS = [(0, 1, 2)] * 3 + [(0, 1, 2, 2.5)] * 2 + [(0, 0.5, 1, 1.5, 2, 2.5)] * 2
HOP_ORDER = [0, 1, 2, 3, 5, 6, 0, 1, 4, 2, 3, 5, 6, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 5, 6, 4, 0, 1]
HOP_T = 0.24
# flyover flocks: (start, direction, count, speed, spacing s). -1 comes in off the free end of Right and
# leaves over the field (Side); +1 comes in at the left corner and leaves off the end of Right.
FLOCKS = [(1.5, -1, 6, 430.0, 0.32), (9.6, 1, 5, 500.0, 0.28), (19.0, -1, 5, 470.0, 0.3)]
NSTORM = 14

SKY = colormap([(0.0, hexc('#4a10c0')), (0.35, hexc('#c0186a')), (0.7, hexc('#ff4a0a')), (1.0, hexc('#ffb040'))])
STRAW = hexc('#ffa818')
HAIR = hexc('#ffc040')
WHEAT = hexc('#e8a020')
HAT = hexc('#c04a08')
PATCH = hexc('#2850ff')
STITCH = hexc('#ffe0a0')
RED = hexc('#e01008')
LINE = hexc('#ffc030')
EYE = hexc('#ffd27a')
GLINT = hexc('#fff0a0')
DUST = hexc('#ffd060')
FLASH = hexc('#fff0c0')
SUN = hexc('#ffc020')
SUNSET = hexc('#ff3000')
MOONC = hexc('#c8d8ff')
NIGHT = hexc('#2018a0')
FIREFLY = hexc('#c8ff40')


def _geo(G):
    rng = {k: (float(G.pd[v].min()), float(G.pd[v].max())) for k, v in G.seg.items()}
    g = dict(L=float(G.length), dL0=rng['Left'][0], dL1=rng['Left'][1], dR0=rng['Right'][0],
             PL=rng['Porch Left'], PF=rng['Porch Front'], PR=rng['Porch Right'], S=rng['Side'])
    g['eyeL'] = g['PL'][1] - 105.0
    g['eyeR'] = g['PR'][0] + 105.0
    g['hat'] = (g['PF'][0] + g['PF'][1]) / 2
    return g


def _ease_out(u):
    u = np.clip(u, 0, 1)
    return 1 - (1 - u) ** 2.5


class _Crow:
    def __init__(self, i, side, small=False):
        self.i, self.side, self.small = i, side, small
        self.s = CS * (0.72 if small else 1.0)
        self.face = -1 if side == 'R' else 1
        self.seg, self.hops, self.flips = [], [], []
        self.flap_ph = 1.7 * i
        self.rate = 6.0


def _plan(G):
    """Perching crows, flyover flocks and the storm, as segments (t0, t1, kind, xa, xb); shared by render()
    and score()."""
    g = _geo(G)
    L = g['L']
    crows = []
    for i, (side, ta, land, goal, small) in enumerate(SPEC):
        c = _Crow(i, side, small)
        base = g['dR0'] if side == 'R' else g['dL0']
        c.ta, c.land, c.goal = ta, base + land, base + goal
        c.entry = L + 30 if side == 'R' else g['dL0'] - 30
        c.seg = [(ta, ta + FLY, 'fly', c.entry, c.land)]
        crows.append(c)
    beats = [4 * bar + b for bar, bb in enumerate(HOP_BARS) for b in bb]
    size = np.zeros(len(beats))
    for i in range(NC):
        ks = [k for k, c in enumerate(HOP_ORDER) if c == i]
        w = np.array([1 + 0.09 * k for k in ks])           # braver: later hops are bigger
        size[ks] = (crows[i].goal - crows[i].land) * w / w.sum()
    pos = [c.land for c in crows]
    for k, (bt, i) in enumerate(zip(beats, HOP_ORDER)):
        t = TT0 + bt * B
        crows[i].hops.append((t, pos[i], pos[i] + size[k]))
        pos[i] += size[k]
    rng = np.random.default_rng(15)
    flee_delay = rng.uniform(0, 0.12, NC)
    flee_delay[0] = 0.0
    for c in crows:
        t, x = c.ta + FLY, c.land
        for th, xa, xb in c.hops:
            c.seg.append((t, th, 'sit', x, x))
            c.seg.append((th, th + HOP_T, 'hop', xa, xb))
            t, x = th + HOP_T, xb
        c.ts = CHOO + flee_delay[c.i]
        c.seg.append((t, c.ts, 'sit', x, x))
        c.seg.append((c.ts, c.ts + 3.5, 'flee', x, x))
        c.rest = x
        t = c.ta + FLY + rng.uniform(0.6, 1.4)
        while t < TT0 - 0.6:                # idle head turns while they wait for the others
            d = rng.uniform(0.35, 0.8)
            c.flips.append((t, t + d))
            t += d + rng.uniform(1.0, 2.6)
    crows[2].flips.append((46.6, 47.2))     # one glances round while his eyes open; it sees nothing
    sm = crows[4]
    r1, r2 = g['dR0'] + 300, g['dR0'] + 120
    sm.seg += [(TRET, TRET + 1.5, 'fly', L + 30, r1), (TRET + 1.5, 58.0, 'sit', r1, r1),
               (58.0, 59.0, 'fly', r1, r2), (59.0, 59.8, 'sit', r2, r2), (59.8, THAT, 'glide', r2, g['hat']),
               (THAT, D + 1, 'sit', g['hat'], g['hat'])]
    sm.flips += [(57.3, 57.75), (64.4, 65.0)]

    flock = []                              # flyovers: straight across the whole house, flapping
    for fi, (t0, dr, cnt, v, sp) in enumerate(FLOCKS):
        for k in range(cnt):
            c = _Crow(100 + 10 * fi + k, 'R' if dr < 0 else 'L', small=(k % 3 == 2))
            c.face = dr
            xa = L + 30 if dr < 0 else g['dL0'] - 30
            xb = -40.0 if dr < 0 else L + 40
            tk = t0 + k * sp + rng.uniform(-0.06, 0.06)
            c.seg = [(tk, tk + abs(xb - xa) / v, 'line', xa, xb)]
            c.bob = rng.uniform(0, 2 * np.pi)
            c.rate = rng.uniform(5.5, 7.5)
            c.flock = fi
            flock.append(c)
    storm = []                              # blown out of the dust: off to the nearest free end
    mid = (g['dL0'] + L) / 2
    for k in range(NSTORM):
        x = rng.uniform(g['dL0'] + 20, L - 20)
        c = _Crow(200 + k, 'L' if x > mid else 'R', small=bool(rng.uniform() < 0.4))
        c.face = 1 if x < mid else -1       # flee goes -face
        ts = CHOO + rng.uniform(0.0, 0.25)
        c.seg = [(ts, ts + 3.5, 'flee', x, x)]
        c.ts, c.rest = ts, x
        c.rate = 9.0
        storm.append(c)
    return g, crows, flock, storm


def crow_state(c, t, g):
    """(x, dir, flap, visible 0..1) of crow c at time t. flap > 0 flapping, < 0 a single wing flick."""
    for t0, t1, kind, xa, xb in c.seg:
        if t0 <= t < t1:
            break
    else:
        return 0.0, c.face, 0.0, 0.0
    u = (t - t0) / (t1 - t0)
    d = c.face
    flap, vis = 0.0, 1.0
    if kind == 'fly':
        x = lerp(xa, xb, _ease_out(u))
        d = 1 if xb > xa else -1
        flap = 1.0 - 0.6 * smoothstep(0.75, 1.0, u)
    elif kind == 'line':
        x = lerp(xa, xb, u) + 10 * np.sin(2 * np.pi * 0.8 * t + c.bob)
        flap = 1.0
    elif kind == 'glide':
        x = lerp(xa, xb, smoothstep(0, 1, u))
        d = -1
        flap = 0.8
    elif kind == 'hop':
        x = lerp(xa, xb, smoothstep(0, 1, u))
        flap = -np.sin(np.pi * u)
    elif kind == 'flee':
        tt = t - t0
        d = -c.face
        x = xa + d * (180 * tt + 520 * tt * tt)
        flap = 1.0
        if x < -40 or x > g['L'] + 40:
            vis = 0.0
    else:
        x = xa
        if c.small and t >= THAT:           # on the hat: settles its wings, and ruffles once more later
            for r0 in (THAT, THAT + 0.45, 66.6):
                if r0 <= t < r0 + 0.3:
                    flap = -np.sin(np.pi * (t - r0) / 0.3)
    if kind in ('fly', 'line') and d > 0 and xa < g['dL0']:   # come in at the corner, never out of Side
        vis = smoothstep(g['dL0'] - 8, g['dL0'] + 20, x) if t < t0 + 1.0 else 1.0
    if kind in ('sit', 'hop'):
        if TT0 <= t < TPECK[0] - 0.05 and 3.0 <= ((t - TT0) / B) % 4 < 3.85:
            d = -d                          # every fourth beat: look away, innocently
        for f0, f1 in c.flips:
            if f0 <= t < f1:
                d = -d
    return x, d, flap, vis


def cawing(i, t):
    """0..1: crow i is mid-caw."""
    for c, t0, n in CAWS:
        if c != i:
            continue
        for k in range(n):
            s = t0 + k * CAW_GAP
            if s <= t < s + CAW_LEN:
                return float(np.sin(np.pi * (t - s) / CAW_LEN) ** 0.5)
    return 0.0


def _bar(t):
    """Tune bar 0..6 (fractional) while the tune plays, else -1."""
    return (t - TT0) / (4 * B) if TT0 <= t < TUG + 0.3 else -1.0


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    g, crows, flock, storm = _plan(G)
    L = g['L']
    pdp = G.pd[G.path]
    n = G.N
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2

    def cover(spans):
        if len(spans) == 0:
            return np.zeros(n)
        sp = np.asarray(spans, float)
        ov = np.clip(np.minimum(sp[:, 1:2], e1) - np.maximum(sp[:, 0:1], e0), 0, None) / w
        return sp[:, 2] @ ov

    seg = G.seg_of[G.path]
    PL, PF, PR, S = g['PL'], g['PF'], g['PR'], g['S']
    dL0, dL1, dR0 = g['dL0'], g['dL1'], g['dR0']

    # ---- the scarecrow: per-pixel colour and base perceptual intensity (path order) ----
    col = np.zeros((n, 3))
    I0 = np.zeros(n)
    straw = np.zeros(n)
    hat = seg == 'Porch Front'
    col[hat] = HAT
    I0[hat] = 0.5 + 0.06 * np.exp(-((pdp[hat] - g['hat']) / 60) ** 2)
    pc = PF[0] + 0.3 * (PF[1] - PF[0])
    patch = hat & (np.abs(pdp - pc) < 18)
    col[patch], I0[patch] = PATCH, 0.5
    pedge = hat & (np.abs(np.abs(pdp - pc) - 18) < 3)
    col[pedge], I0[pedge] = STITCH, 0.45
    hair = ((seg == 'Porch Left') & (pdp > PL[1] - 26)) | ((seg == 'Porch Right') & (pdp < PR[0] + 26))
    face = (((seg == 'Porch Left') & (pdp > PL[0] + 190)) | ((seg == 'Porch Right') & (pdp < PR[0] + 180))) & ~hair
    col[face] = STRAW
    I0[face] = 0.56 * (1 + 0.1 * rng.uniform(-1, 1, face.sum()))
    straw[face] = 0.5
    col[hair], I0[hair], straw[hair] = HAIR, 0.68, 1.0
    shirt = ((seg == 'Porch Left') & (pdp <= PL[0] + 190)) | ((seg == 'Porch Right') & (pdp >= PR[0] + 180))
    sleeve = ((seg == 'Left') & (pdp > dL1 - ARM + HAND)) | ((seg == 'Right') & (pdp < dR0 + ARM - HAND))
    hands = (((seg == 'Left') & (pdp > dL1 - ARM)) | ((seg == 'Right') & (pdp < dR0 + ARM))) & ~sleeve
    cloth = shirt | sleeve
    ph = (pdp % 30) / 30
    col[cloth], I0[cloth] = RED, 0.55
    I0[cloth & (np.abs(ph - 0.5) < 0.17)] = 0.3
    gl = cloth & (ph < 0.08)
    col[gl], I0[gl] = LINE, 0.5
    col[hands] = STRAW
    I0[hands] = 0.66 * (1 + 0.15 * rng.uniform(-1, 1, hands.sum()))
    straw[hands] = 1.0
    figure = hat | face | hair | cloth | hands
    side = seg == 'Side'
    wheat = side & (pdp > S[0] + 290)
    field_sky = side & ~wheat
    sky = ~figure & ~side
    u_sky = np.zeros(n)                     # 0 by the arms .. 1 at the outer ends
    m = sky & (seg == 'Right')
    u_sky[m] = np.clip((pdp[m] - (dR0 + ARM)) / (L - dR0 - ARM), 0, 1)
    m = sky & (seg == 'Left')
    u_sky[m] = np.clip(((dL1 - ARM) - pdp[m]) / (dL1 - ARM - dL0), 0, 1)
    u_sky[field_sky] = 0.85
    SUNX, MOONX = S[0] + 140.0, S[0] + 200.0

    def lattice(k, spacing):
        lat = rng.uniform(-1, 1, k)
        P = k * spacing

        def f(x):
            q = (np.asarray(x) % P) / spacing
            i = np.floor(q).astype(int)
            fr = q - i
            fr = fr * fr * (3 - 2 * fr)
            return lat[i % k] * (1 - fr) + lat[(i + 1) % k] * fr
        return f
    cloud1, cloud2, cloud3 = lattice(64, 70.0), lattice(64, 160.0), lattice(64, 40.0)
    breeze = Flicker(rng, n, 0.3, 1.6)
    wind_gusts = np.arange(1.0, D, 2.9)     # gusts roll in from the free end of Right toward the field

    # loose straw blowing along the roof the whole time (it goes round and round the house)
    NB = 18
    b_x0 = rng.uniform(0, L, NB)
    b_v = rng.uniform(140, 320, NB)
    b_f = rng.uniform(1.5, 4, NB)
    b_ph = rng.uniform(0, 2 * np.pi, NB)
    # fireflies over the field and the wings as it gets dark
    NF = 22
    f_x = np.concatenate([rng.uniform(S[0] + 20, S[1] - 10, 7), rng.uniform(dL0 + 10, dL1 - ARM - 10, 6),
                          rng.uniform(dR0 + ARM + 10, L - 10, 9)])
    f_ph = rng.uniform(0, 1, NF)
    f_per = rng.uniform(1.6, 3.2, NF)
    f_on = rng.uniform(26, 36, NF)
    f_dr = rng.uniform(-12, 12, NF)
    # the sneeze: straw dust from all of him, and feathers raining down over everything
    P = 260
    src = np.nonzero(figure)[0]
    d_x0 = pdp[rng.choice(src, P)]
    d_v = rng.choice([-1, 1], P) * rng.uniform(150, 1500, P)
    d_t0 = CHOO + rng.uniform(0, 0.12, P)
    d_f = rng.uniform(2, 7, P)
    d_ph = rng.uniform(0, 2 * np.pi, P)
    d_life = rng.uniform(1.8, 4.5, P)
    NFE = 70
    fe_x = rng.uniform(dL0 - 200, L, NFE)
    fe_t0 = CHOO + 0.2 + rng.uniform(0, 1.6, NFE)
    fe_life = rng.uniform(2.0, 4.5, NFE)
    fe_ph = rng.uniform(0, 2 * np.pi, NFE)
    fe_dr = rng.uniform(-25, 25, NFE)

    hop_ev = []                             # (time, place, strength) of every hop and peck: ripples
    for c in crows:
        for th, xa, xb in c.hops:
            bar = (th - TT0) / (4 * B)
            hop_ev.append((th + HOP_T * 0.8, xb, 0.18 + 0.05 * bar))
    for pk in TPECK + [TUG]:
        hop_ev.append((pk + 0.09, crows[0].hops[-1][2] - 20, 0.5))
    beats = [TT0 + k * B for k in range(31)]

    eye_c = {'L': g['eyeL'], 'R': g['eyeR']}
    up_sign = {'L': 1.0, 'R': -1.0}
    EH = 18.0
    straw_x = 0.0

    out = np.zeros((nframes(D), n, 3))
    for fi in range(len(out)):
        t = fi * DT
        on = smoothstep(0.2, 3.0, t) * (1 - smoothstep(*FADE, t))
        dusk = smoothstep(4, 52, t)         # the sun goes down over the show
        night = smoothstep(51, 58, t)
        bar = _bar(t)
        build = max(0.0, bar) / 6.5 if bar >= 0 else 0.0

        # --- wind: gusts sweep along the whole roof from the free end of Right toward the field ---
        gust = np.zeros(n)
        for tg in wind_gusts:
            if tg <= t < tg + 7:
                front = L + 200 - 520 * (t - tg)
                gust += np.exp(-((pdp - front) / 140) ** 2)
        if t >= CHOO:                       # the sneeze blows the other way, out from him
            r = 1500 * (t - CHOO)
            gust += 2.0 * np.exp(-((np.abs(pdp - g['hat']) - r) / 120) ** 2) * np.exp(-(t - CHOO) / 1.2)
        # --- light gathered in on each ah, rolled out on the choo ---
        swell = np.zeros(n)
        for k, ta in enumerate(AHS):
            u = (t - ta) / 0.6
            if 0 <= u < 1.2:
                for e in (0.0, dL0, L):     # bands from both free ends and the left corner, toward him
                    tgt = PL[0] if e < g['hat'] else PR[1]
                    p = lerp(e, tgt, min(u, 1))
                    swell += (0.35 + 0.2 * k) * np.exp(-((pdp - p) / 70) ** 2) * (1 - smoothstep(0.8, 1.2, u))
        if t >= CHOO:
            r = 1300 * (t - CHOO)
            swell += 1.1 * np.exp(-((np.abs(pdp - g['hat']) - r) / 110) ** 2) * np.exp(-(t - CHOO) / 0.9)
        # --- music made visible: ripples from every hop and peck, the sky pulsing on the beat ---
        ripple = np.zeros(n)
        for th, xh, a in hop_ev:
            tt = t - th
            if 0 <= tt < 1.4:
                ripple += a * np.exp(-((np.abs(pdp - xh) - 650 * tt) / 35) ** 2) * np.exp(-tt / 0.55)
        pulse = 0.0
        if bar >= 0:
            k = int((t - TT0) / B)
            if k < len(beats):
                pulse = (0.06 + 0.12 * build) * np.exp(-(t - beats[k]) / 0.16) * (k % 4 != 3)
            if 3.0 <= ((t - TT0) / B) % 4 < 3.85 and t < TPECK[0]:
                pulse -= 0.1                # the house holds its breath while they look away
        tense = 0.3 * smoothstep(TUG + 0.3, EYES[1], t) * (1 - smoothstep(AHS[0], CHOO, t))

        # --- the sky over the wings: drifting sunset clouds, colours moving, darkening into night ---
        drift = (18 + 40 * build) * t
        c1 = cloud1(pdp + drift)
        c2 = cloud2(pdp - 0.4 * drift + 300)
        hue = np.clip(0.25 + 0.55 * u_sky + 0.25 * c2 - 0.35 * dusk + 0.2 * gust, 0, 1)
        sky_col = SKY(hue)
        sky_col = lerp(sky_col, NIGHT, 0.55 * night)
        I_sky = (0.56 + 0.14 * c1 + 0.06 * u_sky) * (1 - 0.18 * night) * (1 + 0.35 * gust + pulse)
        # --- the field: wheat rippling in the wind, the sun going down behind it, then the moon ---
        wave = np.sin(pdp / 17 - 3.1 * t + 0.6 * np.sin(pdp / 80 + 0.3 * t))
        I_wheat = (0.44 + 0.13 * wave + 0.08 * cloud3(pdp + 30 * t)) * (1 + 0.45 * gust + pulse) * (1 - 0.3 * night)
        sun_r = 85 * (1 - 0.85 * smoothstep(8, 52, t))
        sun_k = np.exp(-((pdp - SUNX) / max(sun_r, 1)) ** 2)
        sun_col = lerp(SUN, SUNSET, smoothstep(10, 46, t))
        moon_r = 48 * smoothstep(*MOON, t)
        moon_k = np.clip((moon_r - np.abs(pdp - MOONX)) / 6 + 0.5, 0, 1) if moon_r > 1 else np.zeros(n)
        moon_glow = 0.35 * smoothstep(*MOON, t) * np.exp(-((pdp - MOONX) / 150) ** 2)

        buf = np.zeros((n, 3))
        Isk = np.where(field_sky, I_sky * 0.85, I_sky)
        buf[sky | field_sky] = light(sky_col, Isk)[sky | field_sky]
        buf[wheat] = light(WHEAT, I_wheat)[wheat]
        sunI = (0.95 * sun_k * (1 - smoothstep(48, 53, t))) * side
        buf += light(sun_col, sunI)
        buf[side] *= (1 - moon_k[side, None])
        buf += light(MOONC, (0.75 * moon_k + moon_glow) * side)

        # --- the scarecrow: straw and plaid ripple as each gust goes through ---
        gfig = smoothstep(0.3, 3.5, t)
        ah = 0.0
        for k, ta in enumerate(AHS):
            if t >= ta:
                ah = max(ah, (0.12 + 0.1 * k) * smoothstep(ta, ta + 0.55, t))
        ah *= 1 - smoothstep(CHOO, CHOO + 0.15, t)
        sag = 0.16 * smoothstep(SIGH[0], SIGH[0] + 1.2, t) * (1 - 0.6 * smoothstep(SIGH[0] + 1.4, SIGH[1] + 0.6, t))
        hatdip = 0.14 * np.exp(-((t - THAT - 0.12) / 0.12) ** 2) if t > THAT - 0.3 else 0.0
        settle = 0.08 * np.sin(2 * np.pi * 1.6 * (t - CHOO)) * np.exp(-(t - CHOO - 0.6) / 0.8) if t > CHOO + 0.6 else 0.0
        ruffle = gust * np.sin(pdp / 6 - 22 * t)
        wind = 1 + straw * (0.06 * breeze(t) + 0.35 * ruffle) + cloth * 0.22 * ruffle * np.sin(pdp / 13 + 9 * t)
        # the plaid billows: its checks slide back and forth under each gust; the hat brim flaps
        bil = (pdp + 9 * (gust + 0.25) * np.sin(pdp / 45 - 5 * t)) % 30 / 30
        Icl = np.where(np.abs(bil - 0.5) < 0.17, 0.3, 0.55)
        I0t = np.where(cloth & ~gl, Icl, I0)
        I0t = np.where(hat, I0 * (1 + 0.3 * gust * np.sin(pdp / 11 - 14 * t)), I0t)
        Ifig = I0t * wind * (1 + ah - sag + settle + 0.5 * pulse)
        Ifig = np.where(hat, Ifig * (1 - hatdip), Ifig)
        c_now = col.copy()
        if ah > 0:
            fw = face | hair
            c_now[fw] = lerp(col[fw], FLASH, min(1.0, ah * 1.4))
        buf[figure] = light(c_now, Ifig * gfig)[figure]

        # whole-house effects: ripples and swells add warm light, tension dims, master fade
        buf *= (1 + 1.6 * ripple + 0.8 * swell)[:, None] * (1 - tense)
        buf += light(DUST, 0.6 * np.clip(ripple + 0.6 * swell, 0, 1))
        buf *= on

        # --- the eyes: stitched buttons that light up from the middle out ---
        o = keys(t, [(EYES[0], 0), (EYES[1], 1.0), (SQUINT - 0.05, 1.0), (SQUINT + 0.08, 0.0), (LOOKUP, 0.0),
                     (LOOKUP + 0.5, 0.75), (SIGH[0] + 0.6, 0.75), (SIGH[1], 0.3), (SIGH[1] + 0.6, 0.0)])
        look = keys(t, [(EYES[1], -0.9), (49.0, -0.9), (LOOKUP, 1.0)])
        for sd in ('L', 'R'):
            dd = pdp - eye_c[sd]
            m = np.abs(dd) < EH + 3
            cv = np.clip((EH - np.abs(dd)) / 3 + 0.5, 0, 1) * m
            buf *= 1 - 0.93 * cv[:, None] * gfig
            for hole in (-5.5, 5.5):
                buf += light(STITCH, 0.32 * gfig * on * np.clip(1 - np.abs(dd - hole) / 3.5, 0, 1) * (1 - o))
            if o > 0:
                lid = np.clip((o * EH - np.abs(dd)) / 4 + 0.5, 0, 1) * cv
                pup = np.clip(1 - np.abs(dd - up_sign[sd] * look * 8) / 4.5, 0, 1) * smoothstep(0.5, 0.9, o)
                buf += light(EYE, 0.95 * gfig * lid * (1 - 0.92 * pup))

        # --- crows ---
        dark, glint, gold = [], [], []
        for c in crows + flock + storm:
            x, d, flap, vis = crow_state(c, t, g)
            if vis <= 0:
                continue
            s = c.s
            cw = cawing(c.i, t) if c.i < NC else 0.0
            if c.i == 0:
                for pk in TPECK + [TUG]:
                    if pk <= t < pk + 0.18:
                        x += d * 10 * np.sin(np.pi * (t - pk) / 0.18)
            vis *= 1 - smoothstep(*FADE, t)
            hd = 13 + 3 * cw
            parts = [(x + d * 6 * s, x + d * hd * s, 1.0), (x - 7 * s, x + 6 * s, 1.0),
                     (x - d * 16 * s, x - d * 7 * s, 0.8)]
            if flap > 0:
                wl = 19 * s * flap * (0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * c.rate * t + c.flap_ph)))
            else:
                wl = -13 * s * flap
            if wl > 0.5:
                parts += [(x - 7 * s - wl, x - 7 * s, 0.9), (x + 6 * s, x + 6 * s + wl, 0.9)]
            for a, z, k in parts:
                dark.append((min(a, z), max(a, z), k * vis))
            gx = x + d * 10.5 * s
            blink = 0.15 if ((t + 1.3 * c.i) % 3.7) < 0.12 else 1.0
            glint.append((gx - 3.0, gx + 3.0, (0.85 + 0.15 * cw) * blink * vis * (c.i < NC or 0.7)))
            if c.i == 0:
                if TUG + 0.09 <= t < CHOO:  # the straw it pulled, in its beak
                    a = x + d * (hd * s + 1)
                    gold.append((min(a, a + d * 10), max(a, a + d * 10), 0.8))
                    straw_x = a
                elif CHOO <= t < CHOO + 1.0:
                    a = straw_x
                    gold.append((min(a, a + d * 10), max(a, a + d * 10), 0.8 * (1 - (t - CHOO))))
        # feathers rain down after the sneeze, swaying as they fall
        age = t - fe_t0
        lv = (age > 0) & (age < fe_life)
        if lv.any():
            a = age[lv]
            fx = fe_x[lv] + fe_dr[lv] * a + 14 * np.sin(2 * np.pi * 0.7 * a + fe_ph[lv])
            k = 0.85 * smoothstep(0, 0.2, a) * (1 - (a / fe_life[lv]) ** 2)
            dark += list(np.stack([fx - 3, fx + 3, k], 1))
        Dk = np.clip(cover(dark), 0, 0.97)
        buf *= (1 - Dk)[:, None]
        if glint:
            buf += light(GLINT, np.clip(cover(glint), 0, 1) * on)
        if gold:
            buf += light(STRAW, np.clip(cover(gold), 0, 1))

        # --- loose straw blowing, fireflies, the sneeze flash and dust ---
        bx = (b_x0 - (b_v * (1 + 1.5 * build)) * t + 25 * np.sin(b_f * t + b_ph)) % (L + 60) - 30
        bi = (0.55 + 0.35 * np.sin(2 * np.pi * b_f * t + b_ph)) * on * (1 - 0.6 * night)
        sp = np.stack([bx - 2.5, bx + 2.5, bi], 1)
        if t >= CHOO:                       # the dust storm
            age = t - d_t0
            live = (age > 0) & (age < d_life)
            if live.any():
                a = age[live]
                xp = d_x0[live] + d_v[live] * 0.6 * (1 - np.exp(-a / 0.6)) + 14 * np.sin(d_ph[live] + 1.3 * a)
                it = 0.95 * (1 - a / d_life[live]) ** 1.3 * (0.55 + 0.45 * np.sin(2 * np.pi * d_f[live] * a + d_ph[live]))
                sp = np.concatenate([sp, np.stack([xp - 3, xp + 3, it], 1)])
        buf += light(DUST, np.clip(cover(sp), 0, 1))
        fb = np.clip(((t - f_on) / 3), 0, 1) * (1 - smoothstep(*FADE, t))
        if fb.any():
            ph_ = ((t / f_per + f_ph) % 1)
            env = np.exp(-((ph_ - 0.5) / 0.12) ** 2)
            if 4 * B * 5 + TT0 <= t < TPECK[0]:   # as the tune peaks they blink on the eighths
                q = ((t - TT0) / (B / 2)) % 1
                env = np.maximum(env * 0.4, np.exp(-q / 0.18) * (np.arange(NF) % 2 == int((t - TT0) / (B / 2)) % 2))
            fxp = f_x + f_dr * np.sin(0.2 * t + f_ph * 6)
            buf += light(FIREFLY, np.clip(cover(np.stack([fxp - 3, fxp + 3, 0.8 * env * fb], 1)), 0, 1))
        if t >= CHOO - 0.02:
            tt = t - CHOO
            fl = np.exp(-max(tt, 0) / 0.2) * smoothstep(-0.02, 0.02, tt)
            buf += light(FLASH, 0.95 * fl * figure * gfig)
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A sneaky farmyard number in E minor at the lights' 96 BPM. Dusk: low clarinet and harp, and a flock of wingbeats
# passing over, panned along the house. Each crow arrives on a flutter of wingbeats that travels with it and caws
# where it lands (caws are formant-synthesised, panned to the crow). The tiptoe tune is the hopping: bassoon staccato
# walks the bass, and every hop is a pizzicato melody note panned to the crow that hopped, with a woodblock tick; on
# the fourth beat, when they all look away, a flute whistles innocently. It builds bar by bar (clarinet, snare taps,
# contrabass, shaker) to the pecks on the xylophone and a twang when the straw comes out, then stops dead. A bowed
# cymbal and cello tremolo as his eyes light up, three rising "ah"s with slide whistles, and the CHOO: voice,
# orchestra hit, a storm of caws and wingbeats flying out to both ends, straw dust tinkling. Silence; a lone flute
# for the small crow coming back, a glockenspiel ping as it lands on his hat, a bassoon sigh, a warm last chord,
# one small caw.

TUNE = [['E4', 'G4', 'A4'], ['E4', 'G4', 'Bb4'], ['E4', 'G4', 'A4'], ['B4', 'A4', 'G4', 'E4'],
        ['B4', 'C5', 'B4', 'Bb4'], ['E5', 'D5', 'B4', 'A4', 'G4', 'E4'], ['E4', 'G4', 'A4', 'B4', 'C5', 'C#5']]
BASS = ['E', 'E', 'A', 'E', 'C', 'B', 'E']
ROOTS = {'E': ('E2', 'B2'), 'A': ('A2', 'E2'), 'C': ('C3', 'G2'), 'B': ('B2', 'F#2')}


def _stereo(sig, pan):
    a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)


def _harmonic(f0, F, rng, bws=(110, 140, 200), gains=(1.0, 0.6, 0.35), tilt=0.3):
    """Additive formant synthesis: harmonics of f0 (per sample) weighted by three resonances F."""
    from pixelhome.audio import SR
    nn = len(f0)
    jit = np.convolve(rng.normal(0, 1, nn), np.ones(240) / 240, 'same')
    f = f0 * (1 + 0.03 * jit)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros(nn)
    for k in range(1, int(7000 / f0.min()) + 1):
        fk = k * f
        a = sum(gn / (1 + ((fk - Fi) / bw) ** 2) for Fi, bw, gn in zip(F, bws, gains))
        out += a * (fk < 7500) * np.sin(k * ph) / k ** tilt
    return out, ph


def _noise(nn, rng, lo, hi):
    from pixelhome.audio import SR
    x = np.fft.rfft(rng.normal(0, 1, nn))
    f = np.fft.rfftfreq(nn, 1 / SR)
    y = np.fft.irfft(x * ((f > lo) & (f < hi)), nn)
    return y / (np.abs(y).max() + 1e-9)


def _caw(rng, small=False):
    """A crow's KAAW: a harsh, nasal, slightly falling buzz with a rough subharmonic edge."""
    from pixelhome.audio import SR
    dur = 0.2 if small else CAW_LEN
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    u = t / dur
    f0 = rng.uniform(470, 540) * (1.45 if small else 1.0) * (1 + 0.1 * np.sin(np.pi * np.clip(u * 1.8, 0, 1)) - 0.2 * u)
    sc = 1.2 if small else 1.0
    v, ph = _harmonic(f0, (1250 * sc, 1850 * sc, 2900 * sc), rng, tilt=0.15)
    v *= 1 + 0.6 * np.sin(ph / 2)
    v = v / (np.abs(v).max() + 1e-9) + 0.25 * _noise(nn, rng, 900, 4000)
    env = np.clip(t / 0.015, 0, 1) * np.clip((dur - t) / 0.07, 0, 1) * (1 - 0.35 * u)
    return v * env


def _flaps(dur, rate, rng, fast=False):
    """Wingbeats: soft band-passed whumps at `rate` per second."""
    from pixelhome.audio import SR
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    ph = 2 * np.pi * rate * t + 0.4 * np.sin(2 * np.pi * 0.7 * t)
    env = (0.5 - 0.5 * np.cos(ph)) ** 4
    x = _noise(nn, rng, 250, 2600 if fast else 1600)
    fade = np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.15, 0, 1)
    return x * env * fade


def _voice(f0s, F, dur, rng, breath=0.3, amp=1.0):
    """A short vowel: f0 slides from f0s[0] to f0s[1]."""
    from pixelhome.audio import SR
    nn = int(dur * SR)
    t = np.arange(nn) / SR
    f0 = np.geomspace(f0s[0], f0s[1], nn)
    v, _ = _harmonic(f0, F, rng, bws=(90, 110, 160), tilt=0.5)
    v = v / (np.abs(v).max() + 1e-9) + breath * _noise(nn, rng, 300, 3500)
    env = np.clip(t / 0.06, 0, 1) * np.clip((dur - t) / 0.12, 0, 1)
    return v * env * amp


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    vr = np.random.default_rng(1515)
    g, crows, flock, storm = _plan(G)
    L = g['L']

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def track(c, t0, dur):
        """Per-sample pan following crow c from t0."""
        tt = np.arange(t0, t0 + dur, 0.01)
        px = np.array([crow_state(c, t, g)[0] for t in tt])
        p = pan_at(px)
        return np.interp(np.arange(int(dur * SR)) / SR, tt - t0, p)

    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    vpz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cbz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_l = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    flute_s = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    cello = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    taps = M.hits('Percussion/Snare2-taps*.wav')
    shaker = M.hits('VSCO 1 Percussion/varWood/maraca[0-9].wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bow = M.hits('Percussion/susCymb1-bow-*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_*.wav')

    for name, gain, rev in (('wind', 0.25, 0.3), ('bass', 0.5, 0.12), ('pizz', 0.5, 0.18), ('wood', 0.5, 0.15),
                            ('winds', 0.42, 0.22), ('flute', 0.38, 0.3), ('perc', 0.45, 0.15), ('crow', 0.36, 0.2),
                            ('flap', 0.5, 0.12), ('voice', 0.55, 0.15), ('hit', 0.6, 0.2), ('mallet', 0.36, 0.28),
                            ('strings', 0.32, 0.3), ('harp', 0.4, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    def caw_at(c, tj, gain=1.0):
        x = crow_state(c, tj, g)[0]
        M.add('crow', _caw(vr, c.small)[None, :].repeat(2, 0), tj, gain * (0.7 if c.small else 1.0), pan_at(x))

    def caw(i, t, k=1, gain=1.0):
        for j in range(k):
            caw_at(crows[i], t + j * CAW_GAP, gain)

    def flight(c, t0, dur, rate=6.0, gain=1.0, fast=False):
        sig = _flaps(dur, rate, vr, fast) * gain
        M.add('flap', _stereo(sig, track(c, t0, dur)), t0)

    # ---- 0-6: dusk on the farm; a flock passes over ----
    M.add('wind', whoosh(8.0, 150, 600, 0.5, seed=1), 0.0, 0.35, -0.3)
    M.add('wind', whoosh(9.0, 120, 450, 0.5, seed=2), 3.5, 0.3, 0.4)
    for t, m, d in ((0.4, 'E3', 2.6), (3.0, 'G3', 1.4), (4.4, 'F#3', 1.4)):
        M.add('winds', clar_l.play(n(m), 66, dur=d, release=0.6), t, 0.55, -0.1)
    for k, m in enumerate(('E2', 'B2', 'E3', 'G3', 'B3')):
        M.add('harp', harp.play(n(m), 64), 0.3 + 0.18 * k, 0.5, 0.1)
    for c in flock:                         # every flyover on its own wingbeats; the flock caws far off
        t0, t1 = c.seg[0][:2]
        flight(c, t0, t1 - t0, c.rate, 0.22)
    for fi, (t0, dr, cnt, v, sp) in enumerate(FLOCKS):
        lead = [c for c in flock if c.flock == fi][0]
        for k, dt in enumerate((1.2, 2.4, 3.1)):
            caw_at(lead, t0 + dt, 0.35)

    # ---- 6-23: seven arrivals, each on its own wingbeats, each with a caw where it lands ----
    harp_notes = ['B3', 'G3', 'E4', 'A3', 'B4', 'F#4', 'D4']
    for i, c in enumerate(crows):
        flight(c, c.ta, FLY + 0.1, 5.0 if not c.small else 7.5, 0.8 if c.small else 1.0)
        land = c.ta + FLY
        M.add('bass', bsn.play(n('E2'), 80), land, 0.8, pan_at(c.land))
        M.add('bass', bsn.play(n('F2'), 70), land + 0.3, 0.7, pan_at(c.land))
        M.add('harp', harp.play(n(harp_notes[i]), 60), land, 0.6, pan_at(c.land))
    for i, t, k in ARRIVE_CAWS:
        caw(i, t, k)
    for t in (8.0, 15.0, 19.6):             # low dusk chords under the arrivals
        for m in ('E2', 'B2'):
            M.add('strings', cello.play(n(m), 50, dur=3.0, release=0.8), t, 0.6, 0.0)

    # ---- 24-42.75: the tiptoe tune; every hop a note where it happens ----
    for bar in range(7):
        r, f = ROOTS[BASS[bar]]
        for b in range(4):
            t = TT0 + (4 * bar + b) * B
            M.add('bass', bsn.play(n(r if b % 2 == 0 else f), 92 + 6 * (b == 0)), t, 0.9, -0.15)
            if bar >= 4:
                M.add('bass', cbz.play(n(r if b % 2 == 0 else f) - 12, 100), t, 0.7, 0.0)
            if bar >= 2:
                M.add('perc', taps.play(60 + 6 * bar), t + B / 2, 0.5, 0.25)
            if bar >= 5:
                M.add('perc', shaker.play(70), t + B / 4, 0.35, -0.3)
                M.add('perc', shaker.play(60), t + 3 * B / 4, 0.3, 0.3)
        lb = TT0 + (4 * bar + 3) * B         # the look-away: an innocent whistle
        M.add('flute', flute.play(n('B5'), 84), lb, 0.7, 0.0)
        M.add('flute', flute.play(n('G5'), 80), lb + B / 2, 0.7, 0.0)
    hop_i = 0
    for bar, bb in enumerate(HOP_BARS):
        for j, b in enumerate(bb):
            t = TT0 + (4 * bar + b) * B
            c = crows[HOP_ORDER[hop_i]]
            hop_i += 1
            xb = [h for h in c.hops if abs(h[0] - t) < 1e-6][0][2]
            p = pan_at(xb)
            m = n(TUNE[bar][j])
            M.add('pizz', vpz.play(m, 100 + 3 * bar), t, 1.0, p)
            M.add('wood', wood.play(80), t + HOP_T * 0.9, 0.7, p)
            if bar >= 3:
                M.add('winds', clar.play(m - 12, 88), t, 0.6, p * 0.5)
    caw(*BRAVE_CAW)                         # the brave one, just before it pecks
    xg = crows[0].hops[-1][2]
    for t in TPECK:
        M.add('mallet', xylo.play(n('D5'), 108), t + 0.08, 1.0, pan_at(xg))
        M.add('wood', wood.play(110), t + 0.08, 0.9, pan_at(xg))
        M.add('bass', bsn.play(n('B2'), 88), t, 0.7, -0.15)
    M.add('pizz', vpz.play(n('E5'), 120), TUG + 0.08, 1.0, pan_at(xg))
    M.add('wind', slide(0.0, 0.18, 500, 1100, 0.25, 0.5), TUG + 0.08, 0.9, pan_at(xg))
    M.add('bass', bsn.play(n('E2'), 100), TUG + 0.08, 0.9, -0.15)

    # ---- 42.75-50.3: silence, then his eyes light up, then ah... ah... AH... ----
    M.add('perc', bow.play(80), EYES[0] - 0.2, 0.7, 0.0)
    for m in ('E2', 'B2', 'G3'):
        M.add('strings', cello.play(n(m), 70, dur=EYES[1] - EYES[0] + 0.6, release=0.4), EYES[0], 0.8, 0.0)
    M.add('strings', cello.play(n('A#2'), 80, dur=2.6, release=0.2), EYES[1] + 0.1, 0.9, 0.0)
    M.add('perc', troll.play(60, dur=CHOO - AHS[0]), AHS[0], 0.7, 0.0)
    for k, ta in enumerate(AHS):
        f0 = (150, 172, 205)[k]
        M.add('voice', _voice((f0, f0 * 1.18), (730, 1090, 2440), 0.62, vr, breath=0.5, amp=0.6 + 0.2 * k)
              [None, :].repeat(2, 0), ta, 1.0, 0.0)
        M.add('wind', slide(0.0, 0.55, 400 * 1.26 ** k, 700 * 1.26 ** k, 0.6, 0.35), ta, 0.8, 0.0)
        M.add('wind', whoosh(0.6, 2500, 400, 0.4, seed=60 + k), ta, 0.25 + 0.1 * k, -0.6)   # light drawn in
        M.add('wind', whoosh(0.6, 2500, 400, 0.4, seed=70 + k), ta, 0.25 + 0.1 * k, 0.6)

    # ---- 50.3: CHOO ----
    ch = _noise(int(0.09 * SR), vr, 2500, 9000) * np.clip(np.arange(int(0.09 * SR)) / 300, 0, 1)
    M.add('voice', ch[None, :].repeat(2, 0), CHOO - 0.07, 0.8, 0.0)
    M.add('voice', _voice((300, 175), (300, 870, 2240), 0.4, vr, breath=0.9, amp=1.2)[None, :].repeat(2, 0),
          CHOO, 1.0, 0.0)
    M.add('hit', crash.play(120), CHOO, 0.9, 0.0)
    M.add('hit', bd.play(124), CHOO, 1.0, 0.0)
    M.add('hit', timp.play(120, pitch=-1), CHOO, 0.8, 0.0)
    M.add('wind', whoosh(1.4, 300, 3000, 0.5, seed=80), CHOO, 0.7, -0.7)     # the blast rolling out both ways
    M.add('wind', whoosh(1.4, 300, 3000, 0.5, seed=81), CHOO, 0.7, 0.7)
    for m in ('E2', 'E3'):
        M.add('bass', tuba.play(n(m), 124), CHOO, 0.8, 0.0)
    for m in ('E4', 'G4', 'B4', 'E5'):
        M.add('winds', tpt.play(n(m), 118, dur=0.3), CHOO, 0.8, 0.0)
    for c in crows:                         # everyone, out, at once
        flight(c, c.ts, 1.6, 9.0, 1.2, fast=True)
        for j in range(2):
            caw_at(c, c.ts + 0.06 + j * CAW_GAP, 1.1)
    for k, c in enumerate(storm):           # and the rest of the flock, out of the dust
        if k % 2 == 0:
            flight(c, c.ts, 1.4, 9.0, 0.7, fast=True)
        caw_at(c, c.ts + 0.15 + 0.1 * (k % 4), 0.7)
    for k in range(10):                     # glissando of pizz notes scattering both ways
        M.add('pizz', vpz.play(n('E5') - 2 * k, 105 - 4 * k), CHOO + 0.05 + 0.05 * k, 0.6, (-1) ** k * 0.2 * (1 + k / 3))
    for k in range(18):                     # straw dust and feathers settling
        t = CHOO + 0.3 + k * 0.17 * (1 + k / 10)
        M.add('mallet', glock.play(n('E6') - int(vr.integers(0, 12)), 70 - 3 * k), t, 0.6, float(vr.uniform(-0.8, 0.8)))
    M.add('perc', tri.play(60), CHOO + 1.0, 0.5, 0.3)

    # ---- 53.5-62: the moon comes up; the small one flutters back; a lone flute ----
    for k, m in enumerate(('E3', 'B3', 'E4')):
        M.add('harp', harp.play(n(m), 52), MOON[0] + 0.5 + 0.4 * k, 0.5, pan_at(g['S'][0] + 200))
    sm = crows[4]
    for t0, t1 in ((TRET, TRET + 1.6), (58.0, 59.05), (59.8, THAT + 0.05)):
        flight(sm, t0, t1 - t0, 8.0, 0.75)
    for t, m, d in ((TRET + 0.2, 'E5', 0.3), (TRET + 0.6, 'G5', 0.3), (TRET + 1.0, 'A5', 0.6), (58.2, 'B5', 0.3),
                    (58.6, 'A5', 0.5), (59.9, 'G5', 0.3), (60.4, 'A5', 0.3), (60.9, 'B5', 0.3), (61.4, 'D6', 0.5)):
        M.add('flute', flute_s.play(n(m), 70, dur=d, release=0.15), t, 0.7, 0.2)
    M.add('mallet', glock.play(n('E6'), 90), THAT, 0.9, pan_at(g['hat']))
    M.add('wood', wood.play(60), THAT, 0.6, pan_at(g['hat']))
    caw(4, THAT + 0.35, 1, 0.9)

    # ---- 62.5-70: he looks up at it, sighs, and lets it stay ----
    M.add('flute', flute_s.play(n('B5'), 60, dur=0.5), LOOKUP, 0.5, 0.0)
    sigh = _voice((150, 95), (600, 1000, 2400), 1.8, vr, breath=0.9, amp=0.28)
    M.add('voice', sigh[None, :].repeat(2, 0), SIGH[0], 0.8, 0.0)
    for t, m, d in ((SIGH[0], 'B3', 0.7), (SIGH[0] + 0.7, 'G3', 0.7), (SIGH[0] + 1.4, 'E3', 1.4)):
        M.add('winds', bsn_s.play(n(m), 80, dur=d, release=0.3), t, 0.8, -0.1)
    for k, m in enumerate(('E2', 'B2', 'E3', 'G#3', 'B3', 'E4')):   # E major, for once: he doesn't mind
        M.add('harp', harp.play(n(m), 76), 66.0 + 0.12 * k, 0.9, 0.0)
    M.add('winds', clar_l.play(n('G#3'), 64, dur=2.6, release=0.8), 66.0, 0.7, 0.0)
    M.add('strings', cello.play(n('E2'), 55, dur=2.8, release=1.0), 66.0, 0.7, 0.0)
    caw(4, 67.0, 1, 0.7)
