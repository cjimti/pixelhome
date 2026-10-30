"""Wälse! Wälse!: night in Hunding's hut. Siegmund (Wälsung blue) sits alone by the hearth on Left, the embers
breathing low beside him, the ash tree dark at the middle of Porch Front with a faint gold glint in its trunk,
and the storm muttering grey-blue at the door, the free end of Right. He broods to his own weary motif
(Donington 35a) in the cellos over a low pedal: unarmed, in his enemy's house.

He remembers: a sword, his father promised him, for his hour of need. The Sword (Donington 45) sounds softly on
a trumpet, and with each note a thread of gold runs between him and the tree and the glint stirs, as if
answering. He thinks of the woman who held him with her eyes (Sieglinde's motif, Donington 36, on oboe and
cello), and a warm amber glow lingers at the inner door where she went out.

Then he cries out for his father: "Wälse! Wälse!", two huge held notes on the horns and cellos, the orchestra
swelling under each. His blue swells out from him with the note, the first time to the porch, the second time
over the whole house, while the timpani roll and the strings tremble. Nothing answers. But a log falls in the
hearth: the embers flare, a streak of fire light runs from the hearth along the roof to the tree, and the hilt
blazes up gold-white in the trunk, rays of it over the porch, as the Sword rings out on the trumpet. He sings of
the gleam as the light of her eyes; it fades with the fire, the embers sink to almost nothing, and the night
closes in.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'WK07'
TITLE = 'Wälse! Wälse!'
KIND = 'show'
DESCRIPTION = ('Alone by the dying fire, Siegmund remembers the sword his father promised him and cries out '
               'his father\'s name, twice, with everything he has. Then the embers flare, and something in the '
               'old ash tree flashes gold.')
VOICEOVER = ('The house is asleep, and Siegmund has no weapon. His father once promised him a sword. '
             'Tonight, he calls for it.')

K = 6                                       # this scene's place in the shared clock (t + 80 * K)
BEAT = 0.75
T_BROOD = 1.0                               # Siegmund, weary
T_BROOD2 = 9.0
T_SWORD = 17.5                              # "Ein Schwert verhiess mir der Vater"
SWBEAT = 0.55
T_SWORD2 = 23.0
T_LINDE = 28.0                              # the woman who held him with her eyes
LBEAT = 0.5
CRIES = [(36.5, 5.5, 'Gb3'), (45.5, 6.5, 'G3')]   # "Wälse! Wälse!": start, held seconds, the note
T_FLARE = 55.5                              # a log falls; the embers flare
T_HILT = 56.3                               # the hilt blazes in the tree
T_GLEAM = 63.0                              # "Was gleisst dort hell im Glimmerschein?"
T_DIE = 70.0                                # the fire dies
D = 80.0

BLUE = hexc('#30a8ff')
AMBER = hexc('#ffa860')
EMBER = hexc('#ff6a10')
HOT = hexc('#ffb040')
HUT = hexc('#a05a28')
TRUNK = hexc('#5a3010')
LEAF = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
WHITE = hexc('#ffffff')

# the room's levels (perceptual), shared with the scenes either side
BED, TRUNK_L, LEAF_L, STORM_L, SIEG_L = 0.26, 0.55, 0.3, 0.32, 0.5
EMBER_IN, EMBER_OUT = 0.5, 0.18
GLINT_IN, GLINT_OUT = 0.25, 0.22


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_SWORD, 'D2', 66, 'pedal')
    for t, m, v, d in play('siegmund_weary', T_BROOD, BEAT, 0, 84):           # brooding, in the cellos
        add(t, d, m, v, 'weary')
    for t, m, v, d in play('siegmund_weary', T_BROOD2, BEAT, -2, 78, line='bass'):
        add(t, d, m, v, 'weary')
    for m in ('F3', 'A3'):
        add(T_BROOD + 1.0, T_BROOD2 - T_BROOD, m, 58, 'shade')
    for m in ('Eb3', 'G3'):
        add(T_BROOD2 + 1.0, T_SWORD - T_BROOD2 - 0.5, m, 58, 'shade')
    add(T_SWORD - 0.5, T_LINDE - T_SWORD + 0.5, 'C2', 64, 'pedal')
    for m in ('C3', 'G3', 'E4'):                                                # a C major glow under the promise
        add(T_SWORD - 0.3, T_LINDE - T_SWORD, m, 54, 'glow')
    for t, m, v, d in play('sword', T_SWORD, SWBEAT, 0, 82):                    # the Sword, softly, far off
        add(t, d, m, v, 'sword_soft')
    for t, m, v, d in play('sword', T_SWORD2, SWBEAT, -12, 78):
        add(t, d, m, v, 'sword_horn')
    for t, m, v, d in play('sieglinde', T_LINDE, LBEAT, 0, 80):                 # her eyes
        add(t, d, m, v, 'linde' if m >= note('C4') else 'linde_low')

    for k, (t0, hd, m) in enumerate(CRIES):                                     # "Wälse!"
        add(t0 - 2.6, 2.6, 'Gb1' if k == 0 else 'G1', 84 + 10 * k, 'roll')
        add(t0 - 1.0, 0.25, 'Db3' if k == 0 else 'D3', 96, 'pickup')           # "Wäl-"
        add(t0, hd, m, 110 + 8 * k, 'cry')
        add(t0, hd, note(m) - 12, 104 + 8 * k, 'cry_low')
        chord = ('Gb2', 'Db3', 'Gb3', 'Bb3', 'Db4') if k == 0 else ('C2', 'G2', 'C3', 'Eb3', 'G3', 'C4')
        for c in chord:
            add(t0, hd + 0.6, c, 90 + 10 * k, 'swell')
        add(t0, 0.9, 'Gb1' if k == 0 else 'C2', 110 + 8 * k, 'hit')
        fall = (('Gb3', 'F3', 'Eb3', 'Db3') if k == 0 else ('G3', 'F3', 'Eb3', 'D3', 'C3'))
        for j, f_ in enumerate(fall):                                           # the echo falls away
            add(t0 + hd + 0.2 + 0.45 * j, 0.6, f_, 86 - 6 * j, 'echo')
    add(CRIES[1][0] + CRIES[1][1] + 0.5, T_FLARE - CRIES[1][0] - CRIES[1][1] - 0.5, 'C2', 60, 'pedal')

    add(T_FLARE, 0.8, 'C2', 112, 'log')                                         # the log falls
    for j in range(10):
        add(T_FLARE + 0.06 * j, 0.5, note('G3') + (0, 4, 7, 12, 16, 19, 24, 28, 31, 36)[j], 84 + 2 * j, 'harp')
    add(T_HILT, 0.9, 'C5', 112, 'crash')
    for t, m, v, d in play('sword', T_HILT + 0.2, 0.6, 0, 116):                # the Sword, blazing
        add(t, d, m, v, 'sword')
        add(t, d, m - 12, v - 10, 'sword_horn')
    for m in ('C3', 'E3', 'G3', 'C4', 'E4'):
        add(T_HILT, T_GLEAM - T_HILT + 0.5, m, 86, 'blaze')
    add(T_HILT, T_DIE - T_HILT, 'C2', 80, 'pedal')
    for t, m, v, d in play('sieglinde', T_GLEAM, 0.55, -12, 76, line='melody'):  # the gleam of her eyes
        add(t, d, m, v, 'gleam')
    for m in ('A2', 'E3', 'C4'):
        add(T_GLEAM, 4.5, m, 62, 'shade')
    for m in ('F2', 'C3', 'A3'):
        add(T_GLEAM + 4.5, 4.0, m, 60, 'shade')
    for t, m, v, d in play('sword', T_DIE + 1.5, 0.8, -12, 66):                # the fire dies: a muted memory
        if t < D - 2.5:
            add(t, d, m, v, 'sword_mute')
    for m in ('C2', 'G2', 'Eb3'):
        add(T_DIE + 1.0, D - T_DIE - 1.0, m, 62, 'dark')
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
    """Per frame: where Siegmund is (he barely moves: he rises for the cries and sinks back)."""
    F = nframes(D)
    t = np.arange(F) * DT
    S = at(G, 'Left', 0.5)
    tgt = np.full(F, S)
    rate = np.full(F, 2.0)
    for t0, hd, _ in CRIES:                                                     # he turns toward the tree
        m = (t >= t0 - 0.5) & (t < t0 + hd)
        tgt[m] = S + 30
    m = (t >= T_HILT) & (t < T_GLEAM + 6)
    tgt[m] = S + 22
    return dict(t=t, sieg=follow(tgt, rate))


def room(G):
    """The hut's fixed parts: the same flicker for every scene of the act, so the cuts line up."""
    rng = np.random.default_rng(606)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    hc = at(G, 'Left', 0.6)
    return dict(
        pf=pf, hc=hc, door=G.length,
        trunk=np.exp(-((d - pf) / 20) ** 2),
        canopy=np.clip(np.exp(-((d - pf) / 300) ** 2) - 0.8 * np.exp(-((d - pf) / 26) ** 2), 0, 1),
        hearth=np.exp(-((d - hc) / 120) ** 2),
        coals=np.exp(-((d - hc) / 45) ** 2),
        cast=np.exp(-np.abs(d - hc) / 700),
        storm=np.exp(-((G.length - d) / 110) ** 2),
        fl=Flicker(rng, G.N, 0.6, 2.2), fast=Flicker(rng, G.N, 2.5, 6.0), leaf=Flicker(rng, G.N, 0.1, 0.5),
        gust=Flicker(rng, G.N, 0.2, 0.9))


T_WAKE = 8.0                                # the night room as WK06 left it warms into this scene's over this long
WK06_END = dict(bed=0.13, hearth=0.38, trunk=0.7, leaves=0.38, hilt=0.3, door=0.18)
WK06_SIEG = (0.36, 18.0)                    # Siegmund at Left 0.5 as WK06 leaves him: level, width


def stage06(G):
    """WK06's hut model (its stage()), so the first frame is exactly its last."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)
    trunk = np.exp(-((d - pf) / 16) ** 2)
    clumps = 0.55 + 0.45 * smooth_noise(rng, d, 45.0)
    return dict(
        d=d, pf=pf,
        hearth=np.exp(-((d - at(G, 'Left', 0.4)) / 125) ** 2),
        trunk=trunk,
        hilt=np.exp(-((d - pf) / 5) ** 2),
        canopy=porch * np.exp(-((d - pf) / 310) ** 2) * clumps * (1 - trunk),
        door=smoothstep(at(G, 'Right', 0.7), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.2),
        stir=Flicker(rng, G.N, 0.08, 0.35),
        rain=Flicker(rng, G.N, 4.0, 11.0),
    )


def room06(S, T, lv):
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(hexc('#3a1a0a'), lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(EMBER, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(hexc('#ff3000'), 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAF, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def figure06(fr, S, p, col, lvl, w=18.0):
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.8 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.4 * lvl * np.exp(-((S['d'] - p) / (3.2 * w)) ** 2))


def draw_room(G, R, tt, bed, ember, glint, storm, trunk=TRUNK_L, leaves=LEAF_L):
    d = G.pd
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 420 - 0.03 * tt))
    fr = light(HUT, bed * (0.85 + 0.15 * roll))
    fr += light(EMBER, ember * R['hearth'] * (0.8 + 0.12 * R['fl'](tt) + 0.06 * R['fast'](tt)))
    dance = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.11 * tt) + 1.5 * np.sin(2 * np.pi * 0.07 * tt))
    fr += light(EMBER, 0.55 * ember * R['cast'] * (0.3 + 0.7 * dance) * (0.85 + 0.15 * R['fl'](tt)))
    fr += light(HOT, 0.8 * ember * R['coals'] * (0.7 + 0.2 * R['fast'](tt)))
    fr += light(TRUNK, trunk * R['trunk'])
    fr += light(LEAF, leaves * R['canopy'] * (0.85 + 0.15 * R['leaf'](tt)))
    fr += light(HILT, glint * np.exp(-((d - R['pf']) / 9) ** 2))
    fr += light(STORM, storm * R['storm'] * (0.85 + 0.15 * R['gust'](tt)))
    return fr


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    R = room(G)
    S6 = stage06(G)
    pf, hc = R['pf'], R['hc']
    C = choreography(G)
    N = compose()
    door = at(G, 'Left', 0.0)
    sw = np.array([e[0] for e in N if e[4] in ('sword_soft', 'sword_horn') and e[0] < T_LINDE])
    hilt = np.array([e[0] for e in N if e[4] == 'sword'])
    linde = np.array([e[0] for e in N if e[4] in ('linde', 'gleam')])
    weary = np.array([e[0] for e in N if e[4] == 'weary' and e[1] >= 0.3])
    tw = Flicker(rng, G.N, 3.0, 7.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        p = C['sieg'][f]
        dying = smoothstep(T_DIE, D - 2.0, t)
        ember = EMBER_IN * (1 - 0.25 * smoothstep(30, 50, t)) * (1 - dying) + EMBER_OUT * dying
        ember *= 1 - 0.3 * smoothstep(T_HILT + 2, T_DIE, t) * (1 - dying)
        flare = np.exp(-(t - T_FLARE) / 1.2) if t >= T_FLARE else 0.0
        ember += 0.75 * flare
        blaze = smoothstep(T_HILT - 0.05, T_HILT + 0.1, t) * (1 - smoothstep(T_GLEAM, T_DIE + 4, t))
        glint = GLINT_IN + (GLINT_OUT - GLINT_IN) * smoothstep(60, D, t)
        i = int(np.searchsorted(sw, t, side='right')) - 1
        stir = np.exp(-(t - sw[i]) / 0.4) if i >= 0 and t - sw[i] < 2 else 0.0
        glint += 0.35 * stir + 0.9 * blaze
        swell = 0.0
        for t0, hd, _ in CRIES:
            swell = max(swell, smoothstep(t0 - 0.3, t0 + 1.5, t) * (1 - smoothstep(t0 + hd, t0 + hd + 2.5, t)))
        fr = draw_room(G, R, tt, BED * (1 + 0.5 * swell + 0.4 * blaze), ember, glint, STORM_L)
        x = smoothstep(0.0, T_WAKE, t)
        if x < 1:
            fr = x * fr + (1 - x) * room06(S6, tt, WK06_END)

        # the promise: a thread of gold between him and the tree, a spark running along it with each note
        if i >= 0 and t - sw[i] < 2 and t < T_LINDE + 1:
            lo, hi = min(p, pf), max(p, pf)
            line = smoothstep(lo - 10, lo + 10, d) * smoothstep(hi + 10, hi - 10, d)
            q = pf + (p - pf) * min(1.0, (t - sw[i]) / 0.9)
            fr += light(HILT, 0.3 * stir * line + 0.7 * stir * np.exp(-((d - q) / 25) ** 2))

        # her memory: an amber glow at the inner door, pulsing with her notes
        mem = smoothstep(T_LINDE - 1, T_LINDE + 1.5, t) * (1 - smoothstep(T_LINDE + 7, T_LINDE + 9.5, t))
        mem += 0.7 * smoothstep(T_GLEAM - 0.5, T_GLEAM + 1, t) * (1 - smoothstep(T_DIE - 1, T_DIE + 2, t))
        if mem > 0:
            j = int(np.searchsorted(linde, t, side='right')) - 1
            pl = np.exp(-(t - linde[j]) / 0.35) if j >= 0 else 0.0
            fr += light(AMBER, mem * (0.4 + 0.25 * pl) * np.exp(-((d - door) / 70) ** 2))

        # the cries: his blue swells out from him with the held note, to the porch, then over the whole house
        for k, (t0, hd, _) in enumerate(CRIES):
            if t0 - 0.5 <= t < t0 + hd + 3.5:
                g = smoothstep(t0 - 0.2, t0 + hd * 0.85, t)
                r = 40 + (1100 if k == 0 else 2100) * g ** 0.8
                env = smoothstep(t0 - 0.3, t0 + 0.6, t) * (1 - smoothstep(t0 + hd, t0 + hd + 3.0, t))
                dist = np.abs(d - p)
                fill = smoothstep(r + 80, r - 80, dist)
                edge = np.exp(-((dist - r) / 55) ** 2)
                shimmer = 0.85 + 0.15 * np.sin(2 * np.pi * (dist / 90 - 2.2 * t))
                fr += light(BLUE, env * ((0.42 + 0.12 * k) * fill * shimmer + (0.55 + 0.15 * k) * edge))
                fr += light(WHITE, env * 0.35 * edge * (0.6 + 0.4 * tw(t)))

        # the log falls: the hearth bursts, a streak of fire runs to the tree, the hilt blazes
        if T_FLARE <= t < T_FLARE + 1.5:
            u = max(smoothstep(T_FLARE + 0.05, T_HILT, t), 0.01)
            head = hc + (pf - hc) * u
            trail = smoothstep(hc, head, d) * smoothstep(head + 20, head - 20, d) * (d > hc - 20)
            fade = 1 - smoothstep(T_HILT, T_HILT + 0.6, t)
            fr += light(HOT, fade * (0.35 * trail * smoothstep(head - 400, head, d) + 0.9 * np.exp(-((d - head) / 28) ** 2)))
        if blaze > 0:
            k = int(np.searchsorted(hilt, t, side='right')) - 1
            hit = np.exp(-(t - hilt[k]) / 0.3) if k >= 0 else 0.0
            dist = np.abs(d - pf)
            rays = 0.5 + 0.5 * np.cos(2 * np.pi * dist / 70 - 6 * t)
            burst = np.exp(-(t - T_HILT) / 0.35)
            fr += light(HILT, blaze * (0.75 * np.exp(-(dist / 190) ** 2) * (0.7 + 0.3 * rays) +
                                       0.3 * np.exp(-(dist / 650) ** 2) + 0.3 * hit * np.exp(-(dist / 400) ** 2)))
            fr += light(WHITE, blaze * (0.9 * np.exp(-(dist / 14) ** 2) + 0.5 * hit * np.exp(-(dist / 40) ** 2)))
            fr += light(WHITE, 0.55 * burst * np.exp(-(dist / 900) ** 2))

        # his brooding: each weary step a slow blue ripple out from him
        j = int(np.searchsorted(weary, t, side='right')) - 1
        if j >= 0 and t - weary[j] < 3.0 and t < T_SWORD:
            a = t - weary[j]
            r = 30 + 260 * a ** 0.7
            fr += light(BLUE, 0.4 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 60) ** 2))

        # Siegmund
        lift = 0.0
        for t0, hd, _ in CRIES:
            lift = max(lift, smoothstep(t0 - 1.0, t0, t) * (1 - smoothstep(t0 + hd, t0 + hd + 1.5, t)))
        b = SIEG_L * (1 + 0.8 * lift + 0.3 * blaze) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
        new = fr + light(BLUE, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
        fr = new if x >= 1 else x * new + (1 - x) * figure06(fr, S6, p, BLUE, WK06_SIEG[0], WK06_SIEG[1])
        fr += light(WHITE, 0.4 * lift * np.exp(-((d - p) / 10) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    ph = pan_at(at(G, 'Left', 0.6))
    pd_ = pan_at(at(G, 'Left', 0.0))

    def ps(t):
        return pan_at(np.interp(t, C['t'], C['sieg']))

    for name, gain, rev in (('strings', 0.22, 0.32), ('low', 0.25, 0.2), ('brass', 0.24, 0.32), ('winds', 0.24, 0.32),
                            ('perc', 0.24, 0.3), ('harp', 0.2, 0.45)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*_v5_*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('Percussion/gongHit_f.wav')

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
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, ph, rise=1.5, fall=1.5, gain=0.8)
            hold('low', vctrem, m + 12, t, t + d, v - 10, ph, rise=2.0, fall=1.5, gain=0.4)
        elif part == 'weary':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, ps(t))
        elif part == 'shade':
            hold('strings', va, m, t, t + d, v, 0.15 if m % 2 else -0.15, rise=1.2, fall=1.2, gain=0.5)
        elif part == 'glow':
            hold('strings', vtrem if m >= note('C4') else vatrem, m, t, t + d, v, pf, rise=2.0, fall=1.5, gain=0.5)
        elif part == 'sword_soft':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.5), t, 0.7, pf)
        elif part == 'sword_horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 0.8, (pf + ps(t)) / 2)
        elif part == 'linde':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pd_)
        elif part == 'linde_low':
            M.add('strings', vc.play(m, v - 6, dur=d * 1.05, release=0.3), t, 0.8, pd_ + 0.1)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.3), t, 0.7, ps(t))
            hold('strings', vctrem, m + 24, t, t + d, v - 10, ps(t), rise=d, fall=0.3, gain=0.5)
        elif part == 'pickup':
            M.add('brass', horn.play(m, v, dur=d * 1.2, release=0.15), t, 0.9, ps(t))
            M.add('strings', vc.play(m - 12, v, dur=d * 1.2, release=0.15), t, 0.7, ps(t))
        elif part == 'cry':
            hold('brass', horn, m, t, t + d, v, ps(t), rise=0.15, fall=1.2, gain=1.1)
            hold('strings', vc, m, t, t + d, v - 4, ps(t) + 0.1, rise=0.15, fall=1.2, gain=0.9)
        elif part == 'cry_low':
            hold('brass', tbn, m, t, t + d, v, ps(t) - 0.05, rise=0.2, fall=1.2, gain=0.8)
        elif part == 'swell':
            s = vtrem if m >= note('Bb3') else vatrem if m >= note('C3') else cb
            hold('strings', s, m + (12 if s is cb else 0), t, t + d, v, -0.5 + (m % 7) / 6, rise=d * 0.6, fall=1.5,
                 gain=0.55)
            if m < note('G3'):
                hold('brass', tbn if m >= note('C2') else tuba, m + (12 if m < note('Bb1') else 0), t, t + d, v - 12,
                     0.0, rise=d * 0.6, fall=1.5, gain=0.5)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-3), t, 1.0, ps(t))
            M.add('perc', gong.play(v - 20), t, 0.4, 0.0)
        elif part == 'echo':
            M.add('strings', vc.play(m, v, dur=d, release=0.4), t, 0.7, ps(t))
            M.add('brass', mute.play(m, v - 10, dur=d, release=0.4), t, 0.5, pf)
        elif part == 'log':
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, ph)
            M.add('low', tuba.play(m + 12, v, dur=d, release=0.3), t, 0.7, ph)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, ph + (pf - ph) * (m - 55) / 36)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.8, pf)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pf)
        elif part == 'blaze':
            hold('strings', vtrem if m >= note('C4') else vatrem, m, t, t + d, v, pf + (m % 5 - 2) * 0.12, rise=0.2,
                 fall=2.5, gain=0.6)
            if m <= note('G3'):
                hold('brass', horn, m + 12, t, t + d - 3, v - 16, pf, rise=0.3, fall=2.0, gain=0.4)
        elif part == 'gleam':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, ps(t))
            M.add('winds', ob.play(m + 12, v - 14, dur=d * 1.05, release=0.4), t, 0.5, pd_)
        elif part == 'sword_mute':
            M.add('brass', mute.play(m, v, dur=d * 1.05, release=0.6), t, 0.9, pf)
        elif part == 'dark':
            hold('low', cb if m < note('C3') else vatrem, m + (12 if m < note('C3') else 0), t, t + d, v, ph, rise=2.0,
                 fall=2.0, gain=0.6)
