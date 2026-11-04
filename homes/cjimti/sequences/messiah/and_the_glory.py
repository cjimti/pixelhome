"""And the Glory of the Lord: the first chorus, glory rising from Porch Front and spreading out run by run.

The house waits in a deep blue night, a little gold already on Porch Front, the far light, where the violins' last
bars of the ritornello glint. The altos enter alone, "And the glory, the glory of the Lord", and Porch Front lights
white-gold with every note, a bright point riding out along it as the line climbs. When the whole chorus answers, a
wave of glory runs out from the middle of Porch Front to both ends of the house, and every voice takes its own run:
the altos keep Porch Front, the tenors take Porch Left, the basses Porch Right, and the sopranos the two wings, Left and
Right. "Shall be revealed" comes in one voice at a time, tenors, basses, sopranos, so the light moves outward from the
porch, run by run, each run keeping a glow once it has sung.

"And the glory, the glory of the Lord shall be revealed", the full chorus forte: another wave from Porch Front and the
whole house lit, Side too, every chord a surge. "And all flesh shall see it together": the altos on Porch Front, then
the tenors on Porch Left, the strings' short answers flashing gold between them. "For the mouth of the Lord hath
spoken it": the tenors and basses in unison on one long note each, the porch runs held in a steady gold, while the
sopranos and altos run their figure across the wings and Porch Front.

The close: "the mouth of the Lord" held by the sopranos and altos on the wings and Porch Front, the tenors and basses
moving under it on the porch runs. Then Handel's silence: the house drops to its glow. "Hath spoken it", Adagio: the
whole house rises together into full white-gold, Side included, and holds on the last chord.

The music is Handel's own: Messiah No. 4, the ritornello's last two bars and the altos' entry to the first round of
"shall be revealed" (bars 9-24), the tutti "and the glory" (33-38), "and all flesh shall see it together" to the first
"hath spoken it" (43-56), and the close from "it, for the mouth of the Lord" to the Adagio (129-138), transcribed from
Prout's full score (Novello, 1902) into and_the_glory.musicxml and timed by scripts/score_excerpt.py, the Allegro a
little quicker than Prout's crotchet 100 so the scene fits. Handel's strings and the chorus; the chorus sung on
strings with oboes and a bassoon doubling, as Handel doubled it, and the organ under the full chorus.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS04'
TITLE = 'And the Glory of the Lord'
KIND = 'show'
DESCRIPTION = ("The first chorus: glory rises white-gold on Porch Front and spreads out run by run, each voice of the "
               "choir lighting its own part of the house, until the whole house shines on \"hath spoken it\".")
VOICEOVER = 'And the glory of the Lord shall be revealed, and all flesh shall see it together.'

EX = excerpt(__file__)
BAR = {}
for _m, _t in EX['bars']:
    BAR.setdefault(int(_m), _t)             # a spliced bar's first time is where it starts
END = EX['seconds']
HOLD = 2.0
D = round(END + HOLD, 2)
VOICES = ('S', 'A', 'T', 'B')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in VOICES + ('Vn1', 'Vn2', 'Va', 'Bassi')}
ON = {p: np.array([n[0] for n in PART[p]]) for p in PART}
BEAT = (BAR[10] - BAR[9]) / 3
SEG = EX['segments']
T_TUTTI1 = BAR[14] + BEAT                   # the whole chorus answers the altos
T_TUTTI2 = BAR[33] + BEAT                   # A: "and the glory", forte
T_FLESH = SEG[2]['start']
T_MOUTH = BAR[51]                           # "For the mouth of the Lord", tenors and basses in unison
T_CLOSE = SEG[3]['start']                   # "it, for the mouth of the Lord"
T_PAUSE = BAR[135]                          # the rests before "hath spoken it"
T_HATH = BAR[135] + 2 * (BAR[136] - BAR[135]) / 3
T_ADAGIO = BAR[136]
T_LAST = BAR[138]                           # "it."
FIRST = {p: float(ON[p][0]) for p in VOICES}
RANGE = {p: (min(n[2] for n in PART[p]), max(n[2] for n in PART[p])) for p in VOICES}

NIGHT = hexc('#0a1030')
GLORY = hexc('#fff2c8')                     # the chorus
GOLD = hexc('#ffb020')
DEEP = hexc('#d07a10')
HOME = {'A': ('Porch Front',), 'T': ('Porch Left',), 'B': ('Porch Right',), 'S': ('Left', 'Right')}


def places(G):
    """Each voice's runs as a mask, and every pixel's outwardness: 0 in the middle of Porch Front, rising along the
    porch runs to the wings and out to the wings' far ends (1)."""
    seg = G.seg_of
    x = G.pos[:, 0]
    pf = G.seg['Porch Front']
    mid = float(x[pf].mean())
    half = float(np.abs(x[pf] - mid).max())
    out = np.zeros(G.N)
    out[pf] = 0.25 * np.abs(x[pf] - mid) / half
    for s in ('Porch Left', 'Porch Right'):
        i = G.seg[s]
        z = G.pos[i, 2]
        out[i] = 0.25 + 0.25 * (z - z.min()) / (z.max() - z.min())
    for s in ('Left', 'Right'):
        i = G.seg[s]
        dx = np.abs(x[i] - mid)
        out[i] = 0.5 + 0.5 * (dx - dx.min()) / (dx.max() - dx.min())
    i = G.seg['Side']
    z = G.pos[i, 2]
    out[i] = 1.0 - 0.3 * (z.max() - z) / (z.max() - z.min())
    mask = {p: np.isin(seg, HOME[p]).astype(float) for p in VOICES}
    # within a voice's home, where along it a pitch sits: 0 nearest the porch's middle, 1 farthest out
    u = {}
    for p in VOICES:
        m = mask[p] > 0
        o = out[m]
        u[p] = np.zeros(G.N)
        u[p][m] = (o - o.min()) / max(1e-6, o.max() - o.min())
    return mask, out, u


def sounding(p, t):
    """The note of voice p sounding at t: (note, seconds since it began) or (None, 0)."""
    j = int(np.searchsorted(ON[p], t, side='right')) - 1
    if j < 0:
        return None, 0.0
    return PART[p][j], t - PART[p][j][0]


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    seg = G.seg_of
    side = (seg == 'Side').astype(float)
    front = (seg == 'Porch Front').astype(float)
    mask, outw, u = places(G)
    shimmer = Flicker(rng, G.N, 0.4, 1.6)
    sparkle = Flicker(rng, G.N, 3.0, 8.0)
    waves = [T_TUTTI1, T_TUTTI2, T_CLOSE, T_ADAGIO]
    for f in range(F):
        t = f * DT
        # the night, warming a little as the glory spreads
        warm = smoothstep(0.0, T_TUTTI2, t)
        fr = light(NIGHT, (0.07 + 0.02 * shimmer(t)) * (1 - 0.5 * warm)) + light(DEEP, 0.05 * warm * (1 - side * 0.5))
        # the far light waits on Porch Front from the start
        fr += light(GOLD, 0.1 * front * (1 - smoothstep(FIRST['A'], FIRST['A'] + 1.0, t) * 0.3))
        # the violins: gold glints on Porch Front and its runs, strongest when the voices rest
        k = int(np.searchsorted(ON['Vn1'], t, side='right')) - 1
        if k >= 0:
            a = t - ON['Vn1'][k]
            singing = 0
            for p in VOICES:
                n, b = sounding(p, t)
                singing += n is not None and b < n[1] + 0.1
            quiet = 1.0 - min(1.0, singing / 2)
            g = (0.12 + 0.18 * quiet) * np.exp(-a / 0.18)
            fr += light(GOLD, g * np.exp(-(outw / 0.35) ** 2) * (0.6 + 0.4 * np.maximum(sparkle(t), 0)))
        # each voice in its own runs: a glow once it has sung, a surge on every note, a bright point riding its pitch
        for p in VOICES:
            m = mask[p]
            entered = smoothstep(FIRST[p] - 0.1, FIRST[p] + 1.2, t)
            fr += light(GOLD, 0.16 * entered * m)
            lvl = 0.0
            n, a = sounding(p, t)
            if n is not None:
                held = a < n[1]
                env = (0.5 + 0.5 * np.exp(-a / 0.2)) if held else 0.5 * np.exp(-(a - n[1]) / 0.3)
                env *= smoothstep(0.0, 0.04, a)
                loud = 0.75 + 0.25 * (n[3] - 70) / 40
                lvl = 0.72 * env * loud
                lo, hi = RANGE[p]
                c = (n[2] - lo) / max(1, hi - lo)
                spot = np.exp(-((u[p] - c) / 0.12) ** 2)
                fr += light(GLORY, 0.3 * env * loud * spot * m)
            fr += light(GLORY, lvl * m)
        # the waves of glory: out from the middle of Porch Front to the ends of the house
        for tw in waves:
            a = t - tw
            if 0 <= a < 3.5:
                r = a / 1.6
                front_ = np.exp(-((outw - r) / 0.12) ** 2) * smoothstep(1.25, 1.0, r)
                trail = smoothstep(r + 0.05, r - 0.3, outw) * np.exp(-a / 1.2)
                fr += light(GLORY, 0.65 * front_) + light(GOLD, 0.3 * trail)
        # the tutti forte: the whole house surges with the chords, Side too
        if T_TUTTI2 - 0.3 <= t < T_FLESH + 0.8:
            n, a = sounding('S', t)
            surge = 0.0 if n is None else 0.25 * np.exp(-a / 0.3)
            fade = smoothstep(T_TUTTI2 - 0.3, T_TUTTI2 + 0.4, t) * (1 - smoothstep(T_FLESH - 0.8, T_FLESH + 0.8, t))
            fr += light(GOLD, (0.3 + surge) * fade * (0.6 + 0.4 * side))
        # "For the mouth of the Lord": the porch runs held in a steady gold under the long notes
        if T_MOUTH - 0.1 <= t < T_CLOSE:
            g = smoothstep(T_MOUTH - 0.1, T_MOUTH + 0.6, t)
            fr += light(GOLD, 0.2 * g * (mask['T'] + mask['B']))
        # Handel's silence: everything falls back to the glow
        if T_PAUSE <= t < T_HATH:
            fr = fr * (0.55 + 0.45 * smoothstep(T_PAUSE + 0.5, T_PAUSE, t))
        # "hath spoken it": the whole house rises together into white-gold, Side included, and holds
        if t >= T_HATH:
            rise = smoothstep(T_HATH, T_LAST, t)
            full = (0.35 + 0.45 * rise) * smoothstep(T_HATH - 0.05, T_HATH + 0.35, t)
            fr = fr * (1 - 0.6 * rise) + light(GLORY, full) + light(GOLD, 0.12 * (1 - rise))
            if t > END:
                fr = fr * (1 - 0.15 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Handel's strings as written, first violins left to basses right; the chorus on strings with oboes doubling the
    upper voices and a bassoon the bass, each voice panned to its runs; the organ under the full chorus; a soft cymbal
    swell into each wave of glory and a timpani roll under the last chord."""
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

    x = G.pos[:, 0]
    x0, x1 = x.min(), x.max()

    def pan_of(segs):
        i = np.concatenate([G.seg[s] for s in segs])
        return float(0.8 * (2 * (x[i].mean() - x0) / (x1 - x0) - 1))
    vpan = {p: pan_of(HOME[p]) for p in VOICES}
    vpan['S'] = 0.0                                      # both wings
    o = Orchestra(M, level=1.85)

    def last(t, dd):
        return dd + HOLD if abs(t + dd - END) < 0.05 else dd
    span = {'Vn1': -0.45, 'Vn2': -0.2, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            vel = v - 8 - (4 if dd < 0.2 else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), vel, span[p], 0.38)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), vel - 2, span[p], 0.34)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel, span[p], 0.38)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel + 2, span[p], 0.45)
                o.play('basses', m - 12 if m >= 48 else m, t, max(dd, 0.2), vel - 6, span[p], 0.35)
    sec = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -10, 0.3)],
           'A': [('violins', 0, -6, 0.42), ('oboes', 0, -14, 0.22)],
           'T': [('violas', 0, -2, 0.48), ('cellos', 0, -10, 0.25)],
           'B': [('cellos', 0, -2, 0.48), ('bassoons', 0, -8, 0.32), ('basses', -12, -10, 0.3)]}
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            for s, tr, dv, g in sec[p]:
                o.play(s, m + tr, t, max(dd * 0.97, 0.14), v + dv, vpan[p], g)
    # the organ under the full chorus: the first tutti, A, and the close
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.056, reverb=0.45)
    M.bus('pedal', gain=0.078, reverb=0.35)
    full = [(T_TUTTI1 - 0.05, BAR[17] + BEAT), (BAR[33], T_FLESH), (T_MOUTH, T_FLESH + 30), (T_CLOSE, D)]
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            if any(a <= t < b for a, b in full):
                dd = last(t, dd)
                if p == 'B':
                    M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
                else:
                    M.add('organ', man.play(m, v - 10, dd), t - 0.03, 1.0, vpan[p] * 0.5)
    # the waves of glory: a soft cymbal swell into each; the last chord with a timpani roll
    for tw in (T_TUTTI1, T_TUTTI2, T_CLOSE):
        o.hit('cymbal swell', tw - 1.3, 70, gain=0.12, pan=0.0)
    o.hit('cymbal swell', T_LAST - 2.0, 84, gain=0.18, pan=0.0)
    o.hit('timpani roll', T_LAST - 0.1, 86, pitch=-3, gain=0.22, pan=0.1)
    o.hit('timpani', T_LAST, 104, pitch=-3, gain=0.3, pan=0.1)
