"""Entry into Valhalla: the end of the opera. Donner gathers the storm and splits it with his hammer, Froh lays
down the rainbow bridge, and the gods walk into their castle to Valhalla in the full orchestra.

The music is Wagner's own: bars 3690-3712 and the last eight bars (3889-3896) of Das Rheingold, as Solti's 1958
Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py).
Donner's call, "Donner, der Herr, ruft euch zu Heer! Heda! Heda! Hedo!", is played on trombones doubled by horns,
from the printed vocal score (Schott, archive.org dasrheingold00wagn2, pp. 205-206), over the swirling figures of
the gathering mist in the strings and woodwinds; the crescendo builds to the hammer stroke, the storm discharges
in the low strings and timpani, "Bruder, hierher!" and the first shimmer of the rainbow; then Valhalla,
thunderous, in the full brass over the rainbow's arpeggios in the harps and violins, to the last D flat chord.
The staging's sounds: wind gathering with the mist and distant thunder, then the hammer itself, a crack of
thunder, a boom and steel on rock; two smaller bolts on the far runs, rain, a cymbal swell into the rainbow, and
a gong and crash under the last chord. The effects stay low under Donner's call and the finale's brass.

Heavy grey-blue storm air hangs over the mountain until Donner calls to it from Left; the mist swirls in toward
him from all over the house, thickening round his white light while steel-blue sparks crackle in it. A breath;
then he strikes: two flashes of the whole house and jagged white bolts racing from him to both ends of the
roofline; the storm rumbles, rain glitters everywhere, two smaller bolts flicker on the far runs, and then the
air clears from Donner outward into a still evening sky and the castle stands revealed on the porch. Froh lays
down the rainbow, running out along the whole house until every run is banded in colour. Then Valhalla: the
battlements blaze white-gold on every chord, the gods walk the bridge into the castle one by one, Donner and Froh
in from the wings, then Freia, Fricka and last of all Wotan, each a flare of white-gold at the gate, white-gold
blades flash out along the house on the top notes, and the last chord is one flash of the whole house, then the
castle blazing over its rainbow as the light settles.

compose() tags the music's moments, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG24'
TITLE = 'Entry into Valhalla'
KIND = 'show'
DESCRIPTION = ('Donner gathers the storm and splits it with one blow of his hammer, Froh lays a rainbow bridge '
               'across the whole house, and the gods march into their gleaming new castle, Valhalla.')
VOICEOVER = ('Donner calls the storm to him and splits it with one blow of his hammer. '
             'Then a rainbow leads the gods home to Valhalla.')

EX = excerpt(__file__)                      # bars 3690-3712 and 3889-3896, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [g['start'] for g in EX['segments']] + [EX['seconds']]
T_HEDA = [0.0, 5.83]                        # "Donner, der Herr, ruft euch zu Heer!", "Heda! Heda! Hedo!"
T_BREATH = 41.3
STRIKE = [42.25, 42.6]                      # the hammer: two flashes
T_STORM = 42.9
SMALL = [(45.0, 'Right'), (BAR[3708], 'Side')]   # two smaller bolts on the far runs
T_CLEAR = 51.0
T_BOW = BAR[3712]                           # the rainbow bridge
T_VAL = [SEG[1], BAR[3892]]                 # Valhalla
T_LAMENT = 70.0                             # (the Rhinemaidens' lament is not in these bars)
T_CRY = 70.0
T_LOGE = SEG[1]
T_MARCH = SEG[1]                            # the gods walk the bridge
T_FINALE = BAR[3892]
T_LAST = BAR[3894]
T_CHORD = BAR[3896]                         # the last chord
D = EX['seconds']
T0 = 240.0                                  # the opera's clock at our start: steady motion carries across the cuts

# Donner's call, from the vocal score: (bar, beat, beats, note), 4/4
VOICE = [(3690, 0, 0.5, 'F4'), (3690, 0.5, 1 / 6, 'F3'), (3690, 2 / 3, 1 / 3, 'F3'), (3690, 1, 2, 'Bb3'),
         (3690, 3, 0.5, 'C4'), (3690, 3.5, 1 / 6, 'F3'), (3690, 11 / 3, 1 / 3, 'C4'), (3691, 0, 2, 'D4'),
         (3691, 3.75, 0.25, 'F3'), (3692, 0, 3, 'Bb3'), (3692, 3.75, 0.25, 'F3'),
         (3693, 0, 0.75, 'D4'), (3693, 0.75, 0.25, 'F3'), (3693, 1, 3, 'Bb3')]

WOG, WELL, FLO = 0, 1, 2
MAIDENS = [('Right', 0.93), ('Right', 0.8), ('Left', 0.12)]
MCOL = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
GODS = ['donner', 'froh', 'freia', 'fricka', 'wotan']

FREIA = hexc('#ff5a9a')
APPLE = hexc('#ffd040')
LEAF = hexc('#60d020')
WOTAN = hexc('#1a3cff')
FRICKA = hexc('#ff9ad0')
DONNER = hexc('#ffffff')
BOLT = hexc('#a0c0ff')
LOGE0, LOGE1 = hexc('#ff5000'), hexc('#ffb020')
CASTLE = hexc('#fff0c0')
BLAZE = hexc('#ffe8a0')
DAWN0, DAWN1 = hexc('#2a3a6a'), hexc('#6a5a8a')
MIST0, MIST1 = hexc('#2a3650'), hexc('#5a6a88')
SKY0, SKY1 = hexc('#24306a'), hexc('#7a5a8a')
SUNSET = hexc('#ff8a40')
RHINE = hexc('#065c70')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, g):
    """A god's colour drained toward grey by g (0 = full colour, 1 = stone)."""
    lum = float(c @ np.array([0.3, 0.59, 0.11]))
    return c + (np.full(3, 0.15 + 0.75 * lum) - c) * g


def hue(h):
    """Rainbow colours for hue h (any shape, 0..1 wraps) -> (..., 3)."""
    h = np.asarray(h) % 1.0
    return np.stack([np.clip(np.abs(h * 6 - 3) - 1, 0, 1), np.clip(2 - np.abs(h * 6 - 2), 0, 1),
                     np.clip(2 - np.abs(h * 6 - 4), 0, 1)], -1)


def faded(t):
    """The gods' colour comes back as the storm clears."""
    return 0.35 * (1 - smoothstep(T_CLEAR, T_BOW + 2, t))


def mist(t):
    return 1 - smoothstep(T_CLEAR - 0.5, T_BOW + 1, t)


def castle(t):
    """How bright the battlements are."""
    return (0.26 + 0.24 * smoothstep(T_CLEAR, T_BOW + 2, t) + 0.35 * smoothstep(T_VAL[0] - 0.5, T_VAL[0] + 1, t)
            - 0.3 * smoothstep(T_LAMENT - 1, T_LAMENT + 1.5, t) + 0.4 * smoothstep(T_MARCH - 1, T_MARCH + 1, t)
            + 0.1 * smoothstep(T_FINALE, T_FINALE + 2, t) - 0.25 * smoothstep(D - 4, D, t))


def bow(t):
    """How strong the rainbow is."""
    return (0.7 * smoothstep(T_BOW, T_BOW + 1, t)
            + 0.57 * smoothstep(T_MARCH - 1, T_MARCH + 1, t) - 0.25 * smoothstep(D - 4, D, t))


def billow(d, t):
    """Storm air: slow, smooth banks of mist drifting along the roofline (t: seconds since it began to gather)."""
    return (0.5 + 0.3 * np.sin(2 * np.pi * (d / 330 - 0.035 * t)) + 0.2 * np.sin(2 * np.pi * (d / 140 + 0.06 * t) + 1.3))


def voice():
    """Donner's call in seconds: (time, seconds, midi)."""
    bars = [(m, t) for m, t in EX['bars'] if m <= 3713]
    when = lambda pos: float(np.interp(pos, [q[0] for q in bars], [q[1] for q in bars]))
    out = []
    for b, x, n, name in VOICE:
        t0 = when(b + x / 4)
        out.append((t0, when(b + (x + n) / 4) - t0, note(name)))
    return out


def compose():
    """The music's moments, from the excerpt's real notes and Donner's voice: (time, seconds, midi, velocity, part,
    who). 'donner' a note of his call, 'harp' the rainbow's arpeggios, 'valhalla' a chord of Valhalla, 'vhit' its
    bar lines, 'sword' a blade of light on the finale's top notes."""
    N = []
    seen = set()
    for t, d, m, v, h in EX['notes']:
        key = round(t, 2)
        if T_BOW <= t < SEG[1] and h == 0:
            N.append((t, d, m, v, 'harp', None))
        elif t >= SEG[1]:
            if h == 1 and d >= 0.3 and (key, 'v') not in seen:
                seen.add((key, 'v'))
                N.append((t, d, m, v, 'valhalla', 2))
            elif h == 0 and d < 0.3 and m >= 72 and t < T_CHORD:
                N.append((t, d, m, v, 'harp', None))
    for t, d, m in voice():
        N.append((t, d, m, 100, 'donner', None))
    for b in range(3889, 3897):
        N.append((BAR[b], 1.0, 37, 0, 'vhit', None))
        if b in (3890, 3892, 3894):
            N.append((BAR[b], 0.5, 84, 0, 'sword', None))
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: where everyone is (path distance), and when each god passes through the castle gate."""
    F = nframes(D)
    t = np.arange(F) * DT
    hc = at(G, 'Porch Front', 0.5)
    who = GODS + ['loge']
    tgt = {k: np.zeros(F) for k in who}
    rate = {k: np.full(F, 3.0) for k in who}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('wotan', 0, D, at(G, 'Porch Front', 0.4), 3.0)
    set_('fricka', 0, D, at(G, 'Porch Front', 0.25), 3.0)
    set_('freia', 0, D, at(G, 'Porch Front', 0.6), 3.0)
    set_('donner', 0, D, at(G, 'Left', 0.5), 3.0)
    set_('froh', 0, D, at(G, 'Right', 0.6), 3.0)
    jit = 8 * np.sin(2 * np.pi * (t + T0) * 1.7) + 5 * np.sin(2 * np.pi * (t + T0) * 3.1)
    set_('loge', 0, D, at(G, 'Porch Left', 0.75), 3.0)
    set_('loge', T_LOGE, D, at(G, 'Porch Left', 0.12), 2.2)
    set_('donner', T_HEDA[0], STRIKE[0], at(G, 'Left', 0.5) + 6 * np.sin(2 * np.pi * t * 0.8), 2.0)
    for k, ta, r in (('donner', T_MARCH, 0.8), ('froh', T_MARCH, 0.8), ('freia', T_MARCH + 5.5, 1.2),
                     ('fricka', T_MARCH + 6.5, 1.2), ('wotan', T_MARCH + 8.0, 1.2)):
        set_(k, ta, D, hc, r)
    pos = {k: follow(tgt[k], rate[k]) for k in who}
    enter = {}
    for k in GODS:
        near = np.where((t > T_MARCH) & (np.abs(pos[k] - hc) < 18))[0]
        enter[k] = float(t[near[0]]) if len(near) else D
    pos['loge'] = pos['loge'] + jit * (1 + 0.6 * smoothstep(T_LOGE, T_LOGE + 1, t))
    pos['t'] = t
    pos['enter'] = enter
    return pos


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    hc = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    side = G.seg_of == 'Side'
    block = np.floor(d / 34).astype(int)
    mason = np.where((d % 34) < 22, 1.0, 0.35) * (0.8 + 0.2 * rng.random(block.max() + 1)[block])
    tw = Flicker(np.random.default_rng(2101), G.N, 2.0, 7.0)    # shared by RG21-24
    fl = Flicker(np.random.default_rng(2102), G.N, 4.0, 11.0)
    slow = Flicker(np.random.default_rng(2103), G.N, 0.1, 0.4)
    calls = np.array([e[0] for e in N if e[4] == 'donner'])
    vch = np.array(sorted({e[0] for e in N if e[4] == 'valhalla'}))
    harps = np.array([e[0] for e in N if e[4] == 'harp'])
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    swords = [e[0] for e in N if e[4] == 'sword' and e[2] >= note('C5')]
    hits = np.array([e[0] for e in N if e[4] == 'vhit'])
    mpos = [at(G, *m) for m in MAIDENS]
    pD0 = at(G, 'Left', 0.5)
    pF0 = at(G, 'Right', 0.6)
    jag = [rng.random(G.N) for _ in range(4)]

    def recent(ts, t, tau, span=2.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        g = faded(t)
        ms = mist(t)
        cs = castle(t)
        bw = bow(t)
        sky = smoothstep(T_CLEAR, T_BOW + 2, t)
        lament = smoothstep(T_LAMENT - 1, T_LAMENT + 1.5, t) * (1 - smoothstep(T_MARCH - 1.5, T_MARCH + 0.5, t))

        # the sky: storm air pulled in toward Donner, then a clear evening with a last glow of sunset
        pD = C['donner'][f]
        gather = smoothstep(T_HEDA[0], T_BREATH, t)
        dD = np.abs(d - pD)
        u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 700 - 0.02 * (t + T0)))
        fr += light(DAWN0 + (DAWN1 - DAWN0) * u[:, None], 0.4 * (1 - sky) * wings)
        if ms > 0:
            m_ = billow(d, t + 17.0) * (1 - gather) + gather * (0.5 + 0.5 * np.sin(2 * np.pi * (dD / 200 + 0.6 * t)))
            thick = (1 - gather * 0.55) + gather * 1.0 * np.exp(-(dD / 450) ** 2)
            clearing = smoothstep(1200 * (1 - ms) - 150, 1200 * (1 - ms) + 150, dD) if t > T_CLEAR - 0.5 else 1.0
            col = MIST0 + (MIST1 - MIST0) * m_[:, None]
            fr += light(col, (0.6 + 0.3 * m_) * (0.75 + 0.25 * wings) * thick * clearing)
        if sky > 0:
            fr += light(SKY0 + (SKY1 - SKY0) * u[:, None], 0.5 * sky * wings * (1 - 0.3 * bw))
            far = np.clip(np.abs(d - hc) / (L / 2), 0, 1) ** 2
            fr += light(SUNSET, 0.32 * sky * far * wings * (1 - 0.5 * smoothstep(T_MARCH, D, t)))

        # the castle: battlements across the porch, every Valhalla chord a wave of light over them
        vp = recent(vch, t, 0.5)
        hp = recent(hits, t, 0.4)
        wave = 0.0
        i = int(np.searchsorted(vch, t, side='right')) - 1
        if i >= 0 and t - vch[i] < 1.2:
            r = 400 * (t - vch[i]) / 1.2
            wave = np.exp(-((np.abs(d - hc) - r) / 70) ** 2) * (1 - (t - vch[i]) / 1.2)
        fr += light(CASTLE, (cs + 0.06 * slow(t + T0)) * mason * porch + 0.45 * wave * porch)
        fr += light(BLAZE, (0.25 * vp + 0.35 * hp) * porch * mason * smoothstep(T_VAL[0] - 1, T_VAL[0], t))

        # the rainbow bridge: runs out from Froh to both ends, banded across the whole house, glitter flowing in
        if t >= T_BOW:
            reach = 2700 * smoothstep(T_BOW, T_BOW + 4.0, t)
            on = smoothstep(reach + 60, reach - 60, np.abs(d - pF0))
            hp_ = recent(harps, t, 0.15, 0.6)
            h = 0.82 * (1 - d / L)
            glit = 0.75 + 0.25 * np.sin(2 * np.pi * (np.abs(d - hc) / 140 + 1.3 * t))
            over = 1 - 0.65 * smoothstep(T_VAL[0] - 0.5, T_VAL[0] + 1.5, t) * porch
            fr += light(hue(h), (bw * glit + 0.12 * hp_) * on * over * (1 - 0.8 * lament * side))
            front = np.exp(-((np.abs(d - pF0) - reach) / 40) ** 2) * (t < T_BOW + 4.5)
            fr += light(WHITE, 0.8 * front)

        # the Rhine, far below, and the three maidens' lights rising faintly at the ends of the wings
        if lament > 0:
            w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 200 - 0.25 * t))
            fr += light(RHINE, lament * (0.35 + 0.25 * w1) * side)
            for k in range(3):
                i = int(np.searchsorted(sung[k], t, side='right')) - 1
                flare = np.exp(-(t - sung[k][i]) / 0.3) if i >= 0 and t - sung[k][i] < 1.5 else 0.0
                rise_ = smoothstep(T_LAMENT - 1 + 0.6 * k, T_LAMENT + 2 + 0.6 * k, t)
                p = mpos[k] + 14 * np.sin(2 * np.pi * t / 1.8 + k)
                fr += light(MCOL[k], lament * rise_ * ((0.62 + 0.3 * flare) * np.exp(-((d - p) / 24) ** 2)
                                                        + 0.3 * np.exp(-((d - p) / 100) ** 2)))

        # the gods; each fades into the castle as it passes through the gate, in a flare of white-gold
        for k, col in (('donner', DONNER), ('fricka', FRICKA), ('freia', FREIA), ('wotan', WOTAN)):
            p = C[k][f]
            gone = smoothstep(C['enter'][k], C['enter'][k] + 0.6, t)
            c = grey(col, g) if k != 'wotan' else col
            core = {'wotan': 0.95, 'freia': 0.95 - 0.2 * g}.get(k, 0.8)
            halo = 0.35 * np.exp(-((d - p) / 80) ** 2) if k == 'freia' else 0.3 * np.exp(-((d - p) / 90) ** 2)
            wash = (0.46 - 0.2 * g) * np.exp(-((d - p) / 170) ** 2) if k in ('donner', 'fricka') else 0.0
            fr += light(c, (1 - gone) * (core * np.exp(-((d - p) / 24) ** 2) + halo + wash))
            if k == 'freia':
                for off, cc in ((-16, APPLE), (14, LEAF)):
                    fr += light(cc, (1 - gone) * 0.6 * (1 - g) * np.exp(-((d - p - off) / 6) ** 2))
            te = C['enter'][k]
            if te <= t < te + 1.5:
                a = np.exp(-(t - te) / 0.35)
                fr += light(BLAZE, 0.95 * a * np.exp(-((d - hc) / 90) ** 2) + 0.45 * a * porch)
        p = C['froh'][f]
        gone = smoothstep(C['enter']['froh'], C['enter']['froh'] + 0.6, t)
        bw_ = hue((d - p) / 90 + 0.15 * (t + T0)) * (1 - g) + np.full((G.N, 3), 0.55) * g
        fr += light(bw_, (1 - gone) * (0.8 * np.exp(-((d - p) / 28) ** 2) + 0.3 * np.exp(-((d - p) / 90) ** 2)
                                       + (0.49 - 0.2 * g) * (1 - smoothstep(T_BOW, T_BOW + 3, t))
                                       * np.exp(-((d - p) / 200) ** 2)))

        # Donner: the steel-blue halo and its sparks grow as the mist gathers to him, with every note of his call
        cp = recent(calls, t, 0.3)
        gone = smoothstep(C['enter']['donner'], C['enter']['donner'] + 0.6, t)
        big = gather * (1 - smoothstep(STRIKE[0], STRIKE[0] + 3, t))
        fr += light(grey(BOLT, g), (1 - gone) * (0.55 - 0.2 * g + 0.35 * big + 0.3 * cp) * np.exp(-((dD) / (60 + 90 * big)) ** 2))
        fr += light(WHITE, (0.4 * cp + 0.3 * big) * np.exp(-(dD / 30) ** 2))
        if big > 0:
            spark = (rng.random(G.N) < 0.06 * big) * np.exp(-(dD / 220) ** 2)
            fr += light(BOLT, 0.9 * spark)
        breath = smoothstep(T_BREATH, STRIKE[0] - 0.1, t) * (t < STRIKE[0])
        fr *= 1 - 0.45 * breath

        # the hammer: lightning across the whole house, bolts racing out to both ends; then the storm and rain
        for j, ts in enumerate(STRIKE):
            if ts <= t < ts + 1.2:
                a = np.exp(-(t - ts) / 0.12)
                fr += light(WHITE, (0.95 if j == 0 else 0.75) * a * np.ones(G.N))
                r = 3000 * min(1.0, (t - ts) / 0.3)
                jg = (jag[j] > 0.45 + 0.4 * (t - ts)) * (dD < r)
                flick = 0.6 + 0.4 * (np.sin(2 * np.pi * 9 * (t - ts)) > 0)
                fr += light(BOLT, flick * (1 - (t - ts) / 1.2) * jg) + light(WHITE, 0.8 * a * jg)
        for j, (ts, seg) in enumerate(SMALL):
            if ts <= t < ts + 0.6:
                a = np.exp(-(t - ts) / 0.1)
                sel = (G.seg_of == seg) * (jag[2 + j] > 0.35)
                fr += light(WHITE, 0.9 * a * sel) + light(BOLT, 0.7 * (1 - (t - ts) / 0.6) * sel)
        if T_STORM - 0.5 <= t < T_CLEAR + 2:
            rain = (rng.random(G.N) < 0.05) * (1 - smoothstep(T_CLEAR, T_CLEAR + 2, t))
            fr += light(BOLT, 0.55 * rain)

        # Loge, flickering aside
        p = C['loge'][f]
        flick = 0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * (t + T0)) * np.sin(2 * np.pi * 1.3 * (t + T0) + 1)
        lc = LOGE0 + (LOGE1 - LOGE0) * np.clip(0.5 + 0.4 * fl(t + T0), 0, 1)[:, None]
        fr += light(lc, (0.8 + 0.2 * flick) * np.exp(-((d - p) / 32) ** 2) * (0.75 + 0.25 * fl(t + T0))
                    + 0.25 * np.exp(-((d - p) / 100) ** 2))

        # the Sword: each high note a white-gold blade flashing out from Wotan along the whole house
        pw = C['wotan'][f]
        for ts in swords:
            if ts <= t < ts + 1.0:
                r = 2600 * ((t - ts) / 0.8) ** 0.8
                blade = np.maximum(np.exp(-((np.abs(d - pw) - r) / 130) ** 2), 0.5 * (np.abs(d - pw) < r)) * (1 - (t - ts))
                fr += light(BLAZE, 1.0 * blade) + light(WHITE, 0.7 * blade * np.exp(-(t - ts) / 0.3))

        # the last chord: one flash of the whole house, then the castle blazing over its rainbow
        if t >= T_CHORD:
            a = np.exp(-(t - T_CHORD) / 0.3)
            fr += light(BLAZE, 0.95 * a * np.ones(G.N)) + light(WHITE, 0.6 * a * np.exp(-((d - hc) / 300) ** 2))
            fr += light(BLAZE, 0.3 * np.exp(-(t - T_CHORD) / 2.5) * porch)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, Donner's call on trombones and horns, the storm's
    sounds over it."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    pD = pan_at(at(G, 'Left', 0.5))
    hc = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=1.6)

    def role(t, d, m, v, h):
        if T_BOW - 0.05 <= t < SEG[1] and h == 0:      # the rainbow: harps and violins
            return [('harp', 0, 0, 0.5), ('violins', 0, -6, 0.4), ('flutes', 0, -10, 0.3 if m >= 72 else 0.0)]
        if t >= SEG[1]:                                 # Valhalla, thunderous
            if h == 1:
                return [('trombones', 0, 0, 0.75), ('tuba', 0, 0, 0.6 if m < 50 else 0.0),
                        ('horns', 12 if m < 50 else 0, -4, 0.55), ('basses', 0, -6, 0.4 if m < 45 else 0.0)]
            if d < 0.3:
                return [('harp', 0, 0, 0.45), ('violins', 0, -6, 0.4)]
            return [('trumpets', 0, -2, 0.6), ('violins', 0, 0, 0.5)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t >= STRIKE[0] - 6 else 0.6, role=role)
    for t, d, m in voice():                             # Donner: trombones, horns with them
        o.play('trombones', m, t, d, 116, pD, 0.85)
        o.play('horns', m, t, d, 104, pD, 0.55)

    o.effects([(0.0, -14.0), (11.5, -14.0), (13.0, -4.0), (STRIKE[0] - 1.0, 0.0), (T_CLEAR + 2.0, -2.0),
               (SEG[1] - 0.5, -6.0), (SEG[1] + 1.0, -16.0)])
    o.wind(0.0, STRIKE[0] + 6.0, level=lambda tt: 0.25 + 0.75 * np.clip(tt / STRIKE[0], 0, 1) ** 1.5, pan=pD)
    o.thunder(18.0, near=0.1, pan=0.5, gain=0.7)       # the storm gathering, far off
    o.thunder(29.0, near=0.25, pan=-0.6, gain=0.8)
    o.thunder(37.0, near=0.4, pan=0.2, gain=0.9)
    o.hit('timpani roll', T_BREATH - 2.0, 100, pitch=-5, gain=0.5, pan=pD)
    o.thunder(STRIKE[0], near=1.0, pan=0.0, gain=1.3)   # the hammer
    o.boom(STRIKE[0], pD, 1.2)
    o.clash(STRIKE[0], pD, 124, 0.8)
    o.hit('crash', STRIKE[1], 120, gain=0.6, pan=0.0)
    for ts, seg in SMALL:                               # two smaller bolts on the far runs
        o.thunder(ts, near=0.6, pan=pan_at(at(G, seg, 0.5)), gain=0.9)
    from pixelhome.audio import SR
    n = int((T_CLEAR + 2.5 - T_STORM) * SR)             # the rain
    tt = np.arange(n) / SR
    env = np.clip(tt / 0.6, 0, 1) * np.clip((T_CLEAR + 2.5 - T_STORM - tt) / 2.5, 0, 1)
    o._sfx(o._noise(0, 2500, 9000, 24, n=n) * env * o._wobble(n, 2, 25, 0.4), T_STORM, 0.35, 0.0)
    o.hit('cymbal swell', T_BOW - 2.6, 96, gain=0.45, pan=pan_at(at(G, 'Right', 0.6)))   # into the rainbow
    o.hit('triangle', T_BOW, 90, gain=0.35, pan=pan_at(at(G, 'Right', 0.6)))
    o.hit('cymbal swell', T_CHORD - 2.6, 110, gain=0.5, pan=hc)   # the last chord
    o.hit('crash', T_CHORD, 124, gain=0.75, pan=hc)
    o.hit('gong', T_CHORD, 120, gain=0.6, pan=hc)
    o.hit('bass drum', T_CHORD, 124, gain=0.7, pan=hc)
    o.hit('timpani roll', T_CHORD, 110, pitch=-3, gain=0.5, pan=hc)
