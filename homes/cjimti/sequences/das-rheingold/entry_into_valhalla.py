"""Entry into Valhalla: the end of the opera. Heavy grey-blue storm air hangs over the mountain after the
killing, until Donner climbs up on Left and calls to it: "Heda! Hedo!" (Donington 46) on the horns, twice,
in B flat. The mist swirls in toward him from all over the house, thickening round his white light while
steel-blue sparks crackle in it and the timpani roll. A breath; then he strikes with his hammer. Lightning: two
flashes of the whole house and jagged white bolts racing from him to both ends of the roofline, with a gong,
cymbals, bass drum and the brass crashing in. The storm (Donington 74) rumbles down through the low strings,
rain glitters everywhere and two smaller bolts flicker on the far runs, and then the air clears from Donner
outward into a still evening sky, and the castle stands revealed on the porch.

Froh lays down the rainbow bridge (Donington 64): six harps' worth of shimmering G flat arpeggios, and the
rainbow runs out from him along the whole house in both directions until every run is banded in colour, its
glitter flowing toward the castle. Valhalla (Donington 63) in the full brass, twice, the second time with
trumpets: the battlements across Porch Left, Porch Front and Porch Right blaze white-gold, every chord a wave
of light across the porch.

From far below, the Rhinemaidens lament their stolen gold: their song (Donington 26) and their cry "Rheingold!"
(Donington 31) turned into the minor on flute, oboe and clarinet, while the rainbow and the castle dim and three
faint lights, silver, green and violet, rise at the far ends of the wings, and the Rhine shimmers once more
down the Side. Loge flickers off to the front of Porch Left to his own restless motif, wanting no part of what
comes next. Then the march: the Sword (Donington 45) on a trumpet in C, each high note a white-gold blade of
light flashing out from Wotan along the whole house, and the gods walk the bridge into the castle one by one,
Donner and Froh in from the wings, then Freia, Fricka and last of all Wotan, each one a flare of white-gold as
they pass through the gate. Valhalla once more, thunderous, with cymbals and timpani, the rainbow at full
strength on the wings, and a last huge D flat chord: one flash of the whole house, then the castle blazing
over its rainbow as the light slowly settles.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG24'
TITLE = 'Entry into Valhalla'
KIND = 'show'
DESCRIPTION = ('Donner gathers the storm and splits it with one blow of his hammer, Froh lays a rainbow bridge '
               'across the whole house, and the gods march into their gleaming new castle. Far below, the '
               'Rhinemaidens are still crying for their gold.')
VOICEOVER = ('The storm breaks, the sky clears, and a rainbow leads the gods home to Valhalla. '
             'Listen closely, though. Down in the river, someone is still crying.')

HBEAT = 0.6
T_HEDA = [2.5, 8.5]                         # "Heda! Hedo!"
T_BREATH = 14.0
STRIKE = [15.0, 15.35]                      # the hammer: two flashes
T_STORM = 15.6
SMALL = [(17.6, 'Right'), (19.8, 'Side')]   # two smaller bolts on the far runs
T_CLEAR = 21.5
T_BOW = 25.0                                # the rainbow bridge
T_VAL = [31.5, 38.2]                        # Valhalla, twice
VBEAT = 0.8
T_LAMENT = 44.8                             # the Rhinemaidens' lament
T_CRY = 50.8
T_LOGE = 55.6
T_MARCH = 57.0                              # the Sword; the gods walk the bridge
T_FINALE = 61.2                             # Valhalla, thunderous
T_LAST = 67.6
T_CHORD = 74.0                              # the last chord
D = 80.0
T0 = 240.0                                  # the opera's clock at our start: steady motion carries across the cuts

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
    return (0.7 * smoothstep(T_BOW, T_BOW + 1, t) - 0.42 * smoothstep(T_LAMENT - 1, T_LAMENT + 1.5, t)
            + 0.57 * smoothstep(T_MARCH - 1, T_MARCH + 1, t) - 0.25 * smoothstep(D - 4, D, t))


def sad(m):
    """The maidens' song in the minor: every C becomes C flat."""
    return m - 1 if m % 12 == 0 else m


def billow(d, t):
    """Storm air: slow, smooth banks of mist drifting along the roofline (t: seconds since it began to gather)."""
    return (0.5 + 0.3 * np.sin(2 * np.pi * (d / 330 - 0.035 * t)) + 0.2 * np.sin(2 * np.pi * (d / 140 + 0.06 * t) + 1.3))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Bb1', 'Bb2', 'Db3', 'F3'):                   # the storm air, still hanging
        add(0.0, STRIKE[0], m, 62, 'mist')
    for i, t0 in enumerate(T_HEDA):                         # Donner calls the mists to him
        for t, m, v, d in play('donner', t0, HBEAT, 0, 100 + 10 * i):
            add(t, d, m, v, 'donner')
            add(t, d, m - 12, v - 10, 'donner')
        add(t0 + 0.2, 4.6, 'Bb1', 80 + 10 * i, 'roll')
    add(T_BREATH, STRIKE[0] - T_BREATH, 'F2', 100, 'roll')
    add(STRIKE[0], 3.0, 'Bb1', 127, 'thunder')
    add(STRIKE[1], 2.0, 'F2', 116, 'crack')
    for t, m, v, d in play('storm', T_STORM, 0.5, 0, 112):
        add(t, d, m, v, 'storm')
    for ts, _ in SMALL:
        add(ts, 1.5, 'Bb1', 96, 'crack')
    add(T_STORM, T_CLEAR - T_STORM + 1, 'D5', 60, 'rain')

    # the air clears; the rainbow bridge in G flat over D flat; Valhalla
    for i, m in enumerate(('Db3', 'F3', 'Ab3', 'Db4', 'F4', 'Ab4')):
        add(T_CLEAR + 0.4 * i, T_VAL[0] - T_CLEAR - 0.4 * i, m, 64, 'clear')
    add(T_CLEAR, T_VAL[0] - T_CLEAR, 'Db2', 70, 'clearbass')
    for k in range(2):
        for t, m, v, d in play('rainbow', T_BOW + k * 6.0, 0.5, 0, 90 if k == 0 else 80):
            add(t, d, m, v, 'harp' if m >= note('C5') else 'bowbass')
    for k, t0 in enumerate(T_VAL):
        for t, m, v, d in play('valhalla', t0, VBEAT, 0, 104 + 8 * k):
            add(t, d, m, v, 'valhalla', k)
        add(t0, 1.0, 'Db2', 110 + 8 * k, 'vhit')
    for t, m, v, d in play('rainbow', T_VAL[1], 0.4, 0, 70):
        if m >= note('C5') and t < T_LAMENT - 0.5:
            add(t, d, m - 12, v, 'harp')

    # far below, the Rhinemaidens' lament: their song and their cry, in the minor
    song = [(b, d, note(n)) for b, d, n in MOTIFS['rhinemaidens']['notes']]
    who_at = lambda b: (WOG, WELL, FLO)[int(b // 4) % 3]
    for b, d, m in song:
        if b >= 12:
            continue
        t = T_LAMENT + b * 0.5
        if d >= 0.5:
            add(t, d * 0.5, sad(m), 88, 'sing', who_at(b))
        else:
            add(t, d * 0.5, sad(m), 62, 'rock')
    ev = {}
    for b, d, n in MOTIFS['rheingold']['notes']:
        ev.setdefault(b, []).append((d, note(n)))
    for b in sorted(ev):
        ms = sorted(m for _, m in ev[b])
        ms = [m - 1 if m % 12 == 4 and b in (2, 5) else m for m in ms]           # "-gold!" in C minor
        ms = [m - 1 if m % 12 == 9 else m for m in ms]                             # A to A flat: the longing darker
        dd = max(d for d, _ in ev[b]) * 0.55
        top = [m for m in ms if m >= note('G4')][-3:]
        for k, m in enumerate(top):
            add(T_CRY + b * 0.55, dd, m, 92, 'sing', (FLO, WELL, WOG)[k % 3])
        for m in ms:
            if m < note('G4'):
                add(T_CRY + b * 0.55, dd, m, 70, 'lamentlow')
    for t, m, v, d in play('loge_flicker', T_LOGE, 0.35, 0, 88):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('loge', T_LOGE + 1.4, 0.3, 12, 70):
        add(t, d, m, v, 'logeharp')

    # the march: the Sword in C on a trumpet; Valhalla, thunderous; the last chord
    for t, m, v, d in play('sword', T_MARCH, 0.5, 0, 116):
        add(t, d, m, v, 'sword')
    for m in ('C2', 'C3', 'G3', 'E4'):
        add(T_MARCH, 4.0, m, 84, 'swordbed')
    for t, m, v, d in play('valhalla', T_FINALE, 0.75, 0, 120):
        add(t, d, m, v, 'valhalla', 2)
    for b in (0, 4, 6.6667):
        add(T_FINALE + b * 0.75, 1.0, 'Db2', 124, 'vhit')
    for t, m, v, d in play('rainbow', T_FINALE, 0.375, 0, 80):
        if m >= note('C5') and t < T_CHORD - 0.3:
            add(t, d, m, v, 'harp')
    for t, m, v, d in play('valhalla', T_LAST, 0.9, 0, 122):
        if t < T_LAST + 5.3 * 0.9:
            add(t, d, m, v, 'valhalla', 3)
    add(T_LAST + 5.3 * 0.9, T_CHORD - T_LAST - 5.3 * 0.9, 'Db2', 110, 'roll')
    for m in ('Db2', 'Ab2', 'Db3', 'F3', 'Ab3', 'Db4', 'F4', 'Ab4', 'Db5'):
        add(T_CHORD, D - T_CHORD - 0.6, m, 124, 'chord')
    add(T_CHORD, 4.0, 'Db2', 127, 'final')
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
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    hc = pan_at(at(G, 'Porch Front', 0.5))
    pD = pan_at(at(G, 'Left', 0.5))
    pF = pan_at(at(G, 'Right', 0.6))
    mp = [pan_at(at(G, *m)) for m in MAIDENS]

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    for name, gain, rev in (('strings', 0.12, 0.35), ('low', 0.125, 0.2), ('brass', 0.12, 0.32), ('winds', 0.13, 0.38),
                            ('voices', 0.11, 0.45), ('harp', 0.12, 0.45), ('perc', 0.15, 0.3), ('fx', 0.07, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    voice = [M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12), M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12),
             M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)]
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    cym = M.hits('Percussion/susCymb1-cresc-Median_v1.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    for t, d, m, v, part, who in compose():
        if part == 'mist':
            s = trem if m <= note('Bb2') else vatrem
            hold('strings', s, m + 12 * (m == note('Bb1')), t, t + d, v, -0.3 + 0.2 * (m % 4), rise=0.05, fall=0.3,
                 gain=1.4)
        elif part == 'donner':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.1, pD)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.2), t, 0.9, pD if t < 20 else 0.0)
        elif part == 'thunder':
            M.add('perc', gong.play(127), t, 1.0, pD)
            M.add('perc', crash.play(127), t, 1.0, pD)
            M.add('perc', bd.play(127), t, 1.0, pD)
            M.add('perc', timp.play(127, pitch=-5), t, 1.0, pD)
            for mm in ('Bb1', 'F2', 'Bb2', 'D3', 'F3'):
                M.add('brass', (tuba if note(mm) < note('Bb2') else tbn).play(note(mm), 124, dur=d, release=0.8),
                      t, 1.0, 0.0)
            M.add('fx', whoosh(2.5, 3000, 120, 0.8, seed=11), t, 1.0, 0.0)
        elif part == 'crack':
            M.add('perc', crash.play(v), t, 0.8, pan_at(at(G, 'Right', 0.5)) if 17 < t < 18 else -0.6)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, 0.0)
            M.add('fx', whoosh(d, 2500, 150, 0.6, seed=int(t * 10)), t, 0.8, 0.0)
        elif part == 'storm':
            M.add('low', vc.play(m + 12, v, dur=d * 1.05, release=0.2), t, 1.0, -0.2)
            M.add('low', cbs.play(m + 12, v, dur=d, release=0.1), t, 0.9, 0.2)
            M.add('brass', tbn.play(m + 12, v - 14, dur=d * 1.05, release=0.2), t, 0.6, 0.0)
            M.add('low', bsn.play(m + 12, v - 10, dur=d, release=0.2), t, 0.6, 0.0)
        elif part == 'rain':
            hold('strings', vtrem, m, t, t + d, v, 0.3, rise=1.0, fall=2.0, gain=0.5)
            M.add('perc', cym.play(80), t + d - 4.0, 0.5, 0.0)
        elif part == 'clear':
            hold('strings', vn if m >= note('Db4') else va, m, t, t + d, v, -0.4 + 0.15 * (m % 6), rise=2.5, fall=1.5,
                 gain=0.7)
        elif part == 'clearbass':
            hold('low', cb, m, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.8)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, pF if t < T_VAL[0] else -0.5 + 1.0 * ((m * 7) % 12) / 11)
            if t < T_VAL[0]:
                M.add('harp', harp.play(m - 12, v - 10), t, 0.6, -pF)
        elif part == 'bowbass':
            M.add('brass', horn.play(m + 12, v, dur=d * 1.05, release=0.5), t, 0.8, pF)
            hold('low', cb, m, t, t + d, v, 0.0, rise=0.2, fall=1.0, gain=0.6)
        elif part == 'valhalla':
            g = 0.9 + 0.15 * who
            if m >= note('Ab3'):
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, g, hc - 0.25)
                if who >= 1:
                    M.add('brass', tpt.play(m, v - 8, dur=d * 1.05, release=0.5), t, 0.8 * g, hc + 0.25)
                if who >= 2:
                    M.add('strings', vn.play(m + 12, v - 10, dur=d * 1.05, release=0.5), t, 0.8, -0.4)
            elif m >= note('Db3'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.5), t, g, hc)
            else:
                M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.5), t, g, hc)
                hold('low', cb, m + 12, t, t + d, v - 10, hc, rise=0.2, fall=0.6, gain=0.7)
        elif part == 'vhit':
            M.add('perc', timp.play(v, pitch=-3), t, 0.9, hc)
            if v >= 118:
                M.add('perc', crash.play(v - 10), t, 0.7, hc)
        elif part == 'sing':
            M.add('voices', voice[who].play(m, v, dur=d * 1.05, release=0.3), t, 1.0, mp[who])
        elif part == 'rock':
            M.add('harp', harp.play(m, v), t, 0.6, -0.2)
        elif part == 'lamentlow':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.3, fall=0.8, gain=0.35)
        elif part == 'loge':
            M.add('winds', pic.play(m, v), t, 1.0, pan_of('loge', t))
        elif part == 'logeharp':
            M.add('harp', harp.play(m, v), t, 0.7, pan_of('loge', t))
        elif part == 'sword':
            p = pan_of('wotan', t)
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.4), t, 1.2, p)
            M.add('brass', horn.play(m - 12, v - 10, dur=d * 1.05, release=0.4), t, 0.6, p)
        elif part == 'swordbed':
            hold('strings', vn if m >= note('C4') else va if m >= note('C3') else cb, m, t, t + d, v, 0.0,
                 rise=0.3, fall=0.8, gain=0.6)
        elif part == 'chord':
            if m >= note('Db4'):
                M.add('brass', tpt.play(m, v, dur=d, release=1.5), t, 0.8, 0.2)
                hold('strings', vn, m, t, t + d, v - 8, -0.2, rise=0.05, fall=2.5, gain=0.7)
            elif m >= note('Db3'):
                M.add('brass', horn.play(m, v, dur=d, release=1.5), t, 1.0, -0.2)
                M.add('brass', tbn.play(m, v - 6, dur=d, release=1.5), t, 0.8, 0.2)
            else:
                M.add('brass', tuba.play(m, v, dur=d, release=1.5), t, 1.0, 0.0)
                hold('low', cb, m + (12 if m < note('E2') else 0), t, t + d, v, 0.0, rise=0.05, fall=2.5, gain=0.9)
        elif part == 'final':
            M.add('perc', gong.play(127), t, 1.0, 0.0)
            M.add('perc', crash.play(127), t, 1.0, -0.3)
            M.add('perc', crash.play(124), t + 0.02, 0.9, 0.3)
            M.add('perc', bd.play(127), t, 1.0, 0.0)
            M.add('perc', timp.play(127, pitch=-1), t, 1.0, 0.0)
            M.add('perc', roll.play(110, dur=d), t + 0.3, 0.7, 0.0)
