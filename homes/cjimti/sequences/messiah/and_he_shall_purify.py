"""And He Shall Purify: the chorus's running semiquavers as bright lines tracing the roofline, burning off the dross.

The house starts dull and dirty: a murky ember glow, scattered with darker red blotches, the impurities. Every sung
line is a fine white-gold tracer on the roofline: each note carries its head on along the house, a little farther up
or back with every interval the voice sings, turning back at the ends, so the long semiquaver runs of "purify" are
quick bright lines racing and zig-zagging along the roofline, a fading trail behind each. Wherever a
tracer's head passes over an impurity, it burns off in a spark of gold, and the house beneath it is cleaner.

The sopranos give the subject alone, over the basses; then the basses take it up, the altos, the tenors, and at last
the whole chorus is running at once, the strings with them, the lines crossing, sparks flying all along the house, the
glow beneath turning from murk to gold as the dross burns away.

Then the close: "that they may offer unto the Lord an offering in righteousness", the chorus together, fortissimo.
On its first chord the last impurities flash off together, and the house is clean gold from end to end, Side included,
surging with every chord while the violins' semiquavers still trace across it. On "righteousness" it settles into one
steady, clean gold, and holds through the strings' last bars.

The music is Handel's own: Messiah No. 7, the opening to the full chorus's "and He shall purify" (bars 1-16) and the
close from "of Levi" to the end (51-58), transcribed from Prout's full score (Novello, 1902) into
and_he_shall_purify.musicxml and timed by scripts/score_excerpt.py at Prout's Allegro. Handel's strings and the
chorus; the chorus sung on strings with oboes and a bassoon doubling, the organ under the close.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS06'
TITLE = 'And He Shall Purify'
KIND = 'show'
DESCRIPTION = ("The chorus's running semiquavers race along the roofline as fine bright lines, burning off the dark "
               "impurities in sparks, until the whole house shines clean gold.")
VOICEOVER = 'And He shall purify the sons of Levi.'

EX = excerpt(__file__)
BAR = {}
for _m, _t in EX['bars']:
    BAR.setdefault(int(_m), _t)
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
VOICES = ('S', 'A', 'T', 'B')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in VOICES + ('Vn1', 'Vn2', 'Va', 'Bassi')}
TRACE = VOICES + ('Vn1',)
ON = {p: np.array([n[0] for n in PART[p]]) for p in PART}
NUM = {p: np.array([n[:4] for n in PART[p]], float) for p in PART}
T_CLOSE = EX['segments'][1]['start']        # "of Levi", then the close
T_CLEAN = BAR[52] + (BAR[53] - BAR[52]) / 8  # "that they may offer", fortissimo: the last dross burns off
T_NESS = BAR[56]                            # "righteousness."

MURK = hexc('#3a1806')
DROSS = hexc('#8a2a06')
GOLD = hexc('#ffb020')
WHITE = hexc('#ffffff')
CLEAN = hexc('#fff2c8')


START = {'S': 0.55, 'A': 0.85, 'T': 0.3, 'B': 0.12, 'Vn1': 0.7}       # where each line's tracer sets out
DIR = {'S': 1, 'A': -1, 'T': 1, 'B': 1, 'Vn1': -1}


def walk(p):
    """Each note of line p moves its tracer on along the house (0..1): onward with the time it takes, up or back
    with the interval sung, turning back at the ends."""
    n = NUM[p]
    pos = np.zeros(len(n))
    x, s = START[p], DIR[p]
    for k in range(len(n)):
        if k:
            x += s * 0.06 * min(n[k - 1, 1], 0.6) + 0.006 * (n[k, 2] - n[k - 1, 2])
            if x > 1.0 or x < 0.0:
                s = -s
                x = min(1.0, max(0.0, x)) * 2 - x if x > 1.0 else -x
        pos[k] = x
    return pos


POS = {p: walk(p) for p in ('S', 'A', 'T', 'B', 'Vn1')}


def heads(p, t):
    """Where line p's tracer head is at time(s) t (0..1 along the house) and how lit it is."""
    t = np.atleast_1d(t)
    k = np.searchsorted(ON[p], t, side='right') - 1
    ok = k >= 0
    kk = np.clip(k, 0, len(PART[p]) - 1)
    n = NUM[p]
    a = t - n[kk, 0]
    glide = np.clip(a / 0.06, 0, 1)
    prev = POS[p][np.clip(kk - 1, 0, None)]
    pos = prev + (POS[p][kk] - prev) * glide
    dur = n[kk, 1]
    lit = np.where(a < dur, 0.8 + 0.2 * np.exp(-a / 0.08), np.exp(-(a - dur) / 0.15))
    return pos, np.where(ok, lit, 0.0)


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    side = (G.seg_of == 'Side').astype(float)
    d0 = float(G.pd[G.seg['Left']].min())
    d1 = float(G.length)
    span = d1 - d0
    # the impurities: blotches all along the house, Side too
    nd = 64
    spots = np.sort(np.concatenate([rng.uniform(d0, d1, nd - 10), rng.uniform(0, d0, 10)]))
    flick = Flicker(rng, nd, 0.5, 2.0)
    glow = Flicker(rng, G.N, 0.3, 1.2)
    # each impurity burns when a tracer's head first passes over it (or on the close's first chord)
    burn = np.full(nd, T_CLEAN)
    ts = np.arange(F) * DT
    for p in TRACE:
        pos, lit = heads(p, ts)
        hd = d0 + pos * span
        for i in range(nd):
            hit = np.where((np.abs(hd - spots[i]) < 20) & (lit > 0.5) & (ts < burn[i]))[0]
            if len(hit):
                burn[i] = min(burn[i], ts[hit[0]])
    sparks = [(burn[i], spots[i], rng.uniform(-1, 1)) for i in range(nd)]
    lag = np.arange(18) * DT
    for f in range(F):
        t = f * DT
        clean = float(np.mean(burn <= t))
        clean = clean * (1 - smoothstep(T_CLEAN, T_CLEAN + 0.4, t)) + smoothstep(T_CLEAN, T_CLEAN + 0.4, t)
        # the glow beneath: murk turning to clean gold as the dross burns off
        col = (1 - clean) * MURK + clean * GOLD
        base = 0.12 + 0.18 * clean + 0.03 * glow(t)
        fr = light(col, base * (0.75 + 0.25 * side) * np.ones(G.N))
        # the impurities still there: dark red blotches that seethe
        fl = flick(t)
        for i in range(nd):
            if t < burn[i]:
                fr += light(DROSS, (0.22 + 0.08 * fl[i]) * np.exp(-((d - spots[i]) / 11.0) ** 2))
        # sparks where they burn off: a white flash, and two embers flying apart
        for tb, x, u in sparks:
            a = t - tb
            if 0 <= a < 0.7:
                fr += light(WHITE, 0.95 * np.exp(-a / 0.15) * np.exp(-((d - x) / 12.0) ** 2))
                for s in (-1, 1):
                    xe = x + s * (60 + 30 * u) * a / 0.7
                    fr += light(GOLD, 0.6 * (1 - a / 0.7) * np.exp(-((d - xe) / 6.0) ** 2))
        # the tracers: each line's head riding its pitch, a fading trail behind it
        for p in TRACE:
            pos, lit = heads(p, t - lag)
            w = 0.55 if p == 'Vn1' else 1.0
            for j in range(len(lag)):
                if lit[j] < 0.02:
                    continue
                g = lit[j] * np.exp(-j / 6.0) * w
                x = d0 + pos[j] * span
                core = np.exp(-((d - x) / (9.0 + j * 0.8)) ** 2)
                fr += light(CLEAN if j else WHITE, 0.75 * g * core)
        # the close: the whole house surging with every chord, Side included
        if t >= T_CLEAN - 0.05:
            k = int(np.searchsorted(ON['S'], t, side='right')) - 1
            a = t - ON['S'][k]
            surge = 0.18 * np.exp(-a / 0.25) * (t < T_NESS + 0.5)
            settle = smoothstep(T_NESS, T_NESS + 2.0, t)
            fr += light(GOLD, (0.22 + surge) * (1 - 0.3 * settle)) + light(CLEAN, 0.18 * settle)
        if t > END:
            fr = fr * (1 - 0.2 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Handel's strings as written, first violins left to basses right; the chorus on strings with oboes doubling the
    upper voices and a bassoon the bass, each voice panned to where its tracer runs; the organ under the close; a soft
    cymbal swell into it and a timpani stroke on its first chord."""
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, _Voice, _load, _fade_out

    class Pipes(_Voice):
        """The VSCO2 pipe organ: samples are numbered, every third key."""

        def __init__(self, pattern, first):
            self.zones = {}
            for path in sorted(glob.glob(os.path.join(VSCO, pattern))):
                self.zones[first + int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', path).group(1))] = path
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.3):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]
            idx = np.arange(int((dur + release) * SR)) * 2 ** ((n - k) / 12)
            idx = idx[idx < a.shape[1] - 1]
            res = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            return _fade_out(res * (vel / 127) ** 1.3, dur, release)

    o = Orchestra(M, level=2.8)

    def last(t, dd):
        return dd + HOLD if abs(t + dd - END) < 0.05 else dd

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    d0, d1 = float(G.pd[G.seg['Left']].min()), float(G.length)
    x0, x1 = xs.min(), xs.max()

    def pan_at(p, t):                                      # where the line's tracer is on the house
        pos, _ = heads(p, t)
        x = np.interp(d0 + pos[0] * (d1 - d0), ds, xs)
        return float(0.8 * (2 * (x - x0) / (x1 - x0) - 1))
    span = {'Vn1': -0.45, 'Vn2': -0.2, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            vel = v - 8 - (4 if dd < 0.2 else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.1), vel, span[p], 0.36)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.1), vel - 2, span[p], 0.32)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.1), vel, span[p], 0.36)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.12), vel + 2, span[p], 0.45)
                o.play('basses', m - 12 if m >= 48 else m, t, max(dd, 0.15), vel - 6, span[p], 0.35)
    sec = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -10, 0.3)],
           'A': [('violins', 0, -6, 0.42), ('oboes', 0, -14, 0.2)],
           'T': [('violas', 0, -2, 0.48), ('cellos', 0, -10, 0.22)],
           'B': [('cellos', 0, -2, 0.48), ('bassoons', 0, -8, 0.32), ('basses', -12, -10, 0.28)]}
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            for s, tr, dv, g in sec[p]:
                o.play(s, m + tr, t, max(dd * 0.97, 0.11), v + dv, pan_at(p, t + 0.07), g)
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.084, reverb=0.45)
    M.bus('pedal', gain=0.118, reverb=0.35)
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            if t >= T_CLOSE - 0.01:
                dd = last(t, dd)
                if p == 'B':
                    M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
                else:
                    M.add('organ', man.play(m, v - 10, dd), t - 0.03, 1.0, pan_at(p, t + 0.07) * 0.5)
    o.hit('cymbal swell', T_CLEAN - 1.5, 80, gain=0.16, pan=0.0)
    o.hit('timpani', T_CLEAN, 108, pitch=-5, gain=0.3, pan=0.1)
    o.hit('timpani roll', BAR[58] - 0.2, 70, pitch=-5, gain=0.16, pan=0.1)
