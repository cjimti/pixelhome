"""Wälse! Wälse!: night in Hunding's hut. Siegmund (Wälsung blue) sits alone by the hearth on Left, the embers
breathing beside him, the ash tree dark at the middle of Porch Front with a faint gold glint in its trunk, and the
storm muttering grey-blue at the door, the free end of Right. He thinks of the woman who held him with her eyes and
the man who holds her: the strings' restless figure climbs and grows louder, an amber glow pulses at the inner door
where she went out with every note of it, and each step of the bass sends a blue ripple out from him.

Then he cries out for his father: "Wälse! Wälse!", the orchestra holding a huge trembling chord under each cry. His
blue swells out from him, the first time to the porch, the second time over the whole house, while the basses and
timpani roll. Nothing answers. "Wo ist dein Schwert?": with each note a thread of gold runs between him and the tree
and the glint stirs, as if answering, and his light rises with "bricht mir hervor aus der Brust". Then the embers
flare, a streak of fire light runs from the hearth along the roof to the tree, and the hilt blazes up gold-white in
the trunk, rays of it over the porch, as the Sword sounds in the orchestra and the violins shimmer high in C major;
sparks of gold and white fly up through the leaves on every note of the shimmer. He sings of the gleam as the light
of her eyes; it fades with the fire, the embers sink, and the night closes in.

The music is Wagner's own: Act I, bars 832-864, as Solti's 1958 Vienna Philharmonic recording takes them, from the
Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The held chords under the cries are horns and trombones
over tremolo cellos and basses; the Sword, in the left hand, is the trumpets; the shimmer above it violins and harp;
the rest is the reduction orchestrated by hand and register. The stage adds its sounds: the embers crackling at
the hearth and dying with it, the storm's wind gusting at the door, far-off thunder answering nothing after the
second cry, the fire roaring up and rushing along the roof when it flares, the hilt ringing out like struck steel
as it blazes, and sparks crackling round the tree with the shimmer. The effects keep low under the night, back right off for
the two cries and the vow that follows so his voice and the orchestra's held chords are clear, come up for the far
thunder, lead when the fire flares and the hilt blazes, and recede again as he sings of the gleam.

compose() tags every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK07'
TITLE = 'Wälse! Wälse!'
KIND = 'show'
DESCRIPTION = ('Alone by the dying fire, Siegmund remembers the sword his father promised him and cries out '
               'his father\'s name, twice, with everything he has. Then the embers flare, and something in the '
               'old ash tree flashes gold.')
VOICEOVER = ('The house is asleep, and Siegmund has no weapon. His father once promised him a sword. '
             'Tonight, he calls for it.')

EX = excerpt(__file__)                      # Act I, bars 832-864, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
K = 6                                       # this scene's place in the shared clock (t + 80 * K)
T_LINDE = BAR[832]                          # the woman, held by the man who mocks him
T_ROLL = BAR[839]                           # the orchestra gathers for the cry
CRIES = [(BAR[840], BAR[841] - BAR[840] - 1.5), (BAR[841], BAR[842] - BAR[841] - 1.5)]   # "Wälse!": start, held
T_SWORD = BAR[842]                          # "Wo ist dein Schwert? das starke Schwert"
T_RISE = BAR[846]                           # "bricht mir hervor aus der Brust"
T_FLARE = BAR[849]                          # the embers flare
T_HILT = T_FLARE + 0.8                      # the hilt blazes in the tree
T_GLEAM = BAR[852] + 1.4                    # "Was gleisst dort hell im Glimmerschein?"
T_DIE = BAR[859]                            # the fire dies
D = EX['seconds']

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). 'linde' is the strings'
    figure while he thinks of her, 'step' its bass; 'roll' the trembling bass under the cries and 'swell' the chord
    held over it; 'promise' the line of "Wo ist dein Schwert?"; 'sword' the Sword in the left hand once the hilt
    blazes, 'shimmer' the violins above it; everything else is 'note'."""
    N = []
    for t, d, m, v, h in EX['notes']:
        part = 'note'
        if t < T_ROLL:
            part = 'linde' if h == 0 else 'step' if d >= 0.3 else 'note'
        elif t < T_SWORD:
            part = 'roll' if h == 1 and m < 48 else 'swell'
        elif t < T_RISE:
            part = 'promise' if h == 0 else 'note'
        elif t >= T_FLARE:
            part = 'shimmer' if h == 0 else 'sword' if m >= 55 and d >= 0.3 else 'note'
        N.append((t, d, m, v, part, h))
    return N


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
    for t0, hd in CRIES:                                                        # he turns toward the tree
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
    sw = np.array([e[0] for e in N if e[4] == 'promise'])
    hilt = np.array([e[0] for e in N if e[4] == 'sword'])
    linde = np.array([e[0] for e in N if e[4] == 'linde'])
    lvel = np.array([e[3] for e in N if e[4] == 'linde'])
    weary = np.array([e[0] for e in N if e[4] == 'step'])
    shim = [e for e in N if e[4] == 'shimmer']
    shim_t = np.array([e[0] for e in shim])
    shim_p = rng.normal(0, 1, len(shim))     # where each spark flies up through the leaves
    rise = np.array([e[0] for e in N if T_RISE <= e[0] < T_FLARE and e[5] == 1 and e[1] >= 0.3])
    tw = Flicker(rng, G.N, 3.0, 7.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        p = C['sieg'][f]
        dying = smoothstep(T_DIE, D - 2.0, t)
        ember = EMBER_IN * (1 - 0.25 * smoothstep(CRIES[0][0], T_FLARE, t)) * (1 - dying) + EMBER_OUT * dying
        ember *= 1 - 0.3 * smoothstep(T_HILT + 2, T_DIE, t) * (1 - dying)
        flare = np.exp(-(t - T_FLARE) / 1.2) if t >= T_FLARE else 0.0
        ember += 0.75 * flare
        blaze = smoothstep(T_HILT - 0.05, T_HILT + 0.1, t) * (1 - smoothstep(T_GLEAM, D - 1.0, t))
        glint = GLINT_IN + (GLINT_OUT - GLINT_IN) * smoothstep(T_GLEAM, D, t)
        i = int(np.searchsorted(sw, t, side='right')) - 1
        stir = np.exp(-(t - sw[i]) / 0.4) if i >= 0 and t - sw[i] < 2 else 0.0
        glint += 0.35 * stir + 0.9 * blaze
        swell = 0.0
        for t0, hd in CRIES:
            swell = max(swell, smoothstep(t0 - 0.3, t0 + 1.5, t) * (1 - smoothstep(t0 + hd, t0 + hd + 2.5, t)))
        fr = draw_room(G, R, tt, BED * (1 + 0.5 * swell + 0.4 * blaze), ember, glint, STORM_L)
        x = smoothstep(0.0, T_WAKE, t)
        if x < 1:
            fr = x * fr + (1 - x) * room06(S6, tt, WK06_END)

        # the promise: a thread of gold between him and the tree, a spark running along it with each note
        if i >= 0 and t - sw[i] < 2 and t < T_RISE + 1:
            lo, hi = min(p, pf), max(p, pf)
            line = smoothstep(lo - 10, lo + 10, d) * smoothstep(hi + 10, hi - 10, d)
            q = pf + (p - pf) * min(1.0, (t - sw[i]) / 0.9)
            fr += light(HILT, 0.3 * stir * line + 0.7 * stir * np.exp(-((d - q) / 25) ** 2))

        # her memory: an amber glow at the inner door, pulsing with her notes
        mem = smoothstep(T_LINDE, T_LINDE + 1.5, t) * (1 - smoothstep(T_ROLL, T_ROLL + 2.5, t))
        mem += 0.7 * smoothstep(T_GLEAM - 0.5, T_GLEAM + 1, t) * (1 - smoothstep(T_DIE - 1, T_DIE + 2, t))
        if mem > 0:
            j = int(np.searchsorted(linde, t, side='right')) - 1
            pl = np.exp(-(t - linde[j]) / 0.18) * (lvel[j] / 110) ** 2 if j >= 0 and t < T_ROLL + 2 else 0.0
            grow = 1 + smoothstep(T_LINDE, T_ROLL, t)
            fr += light(AMBER, mem * (0.4 + 0.5 * pl) * np.exp(-((d - door) / (70 * grow)) ** 2))
            fr += light(AMBER, 0.45 * mem * pl * np.exp(-((d - door - 160 * grow) / 50) ** 2))

        # the cries: his blue swells out from him with the held note, to the porch, then over the whole house
        for k, (t0, hd) in enumerate(CRIES):
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
        # the shimmer: a spark of gold or white flies up through the leaves on every note
        k = int(np.searchsorted(shim_t, t, side='right'))
        for j in range(max(0, k - 8), k):
            a = t - shim_t[j]
            if a < 0.45:
                c = pf + 230 * shim_p[j]
                amp = (0.5 + 0.5 * blaze) * (shim[j][3] / 100)
                fr += light(WHITE if shim[j][2] >= 84 else HILT, amp * np.exp(-a / 0.13) * np.exp(-((d - c) / 13) ** 2))

        # his brooding: each weary step a slow blue ripple out from him
        j = int(np.searchsorted(weary, t, side='right')) - 1
        if j >= 0 and t - weary[j] < 3.0 and t < T_ROLL + 2:
            a = t - weary[j]
            r = 30 + 260 * a ** 0.7
            fr += light(BLUE, 0.4 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 60) ** 2))

        # Siegmund
        lift = 0.0
        for t0, hd in CRIES:
            lift = max(lift, smoothstep(t0 - 1.0, t0, t) * (1 - smoothstep(t0 + hd, t0 + hd + 1.5, t)))
        lift = max(lift, 0.8 * smoothstep(T_RISE, T_FLARE, t) * (1 - smoothstep(T_FLARE, T_FLARE + 2, t)))
        j = int(np.searchsorted(rise, t, side='right')) - 1
        if j >= 0 and t - rise[j] < 1.5 and t < T_FLARE:     # "bricht mir hervor": each chord a pulse of blue
            a = t - rise[j]
            fr += light(BLUE, 0.6 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p) - 40 - 500 * a) / 70) ** 2))
        b = SIEG_L * (1 + 0.8 * lift + 0.3 * blaze) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
        new = fr + light(BLUE, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
        fr = new if x >= 1 else x * new + (1 - x) * figure06(fr, S6, p, BLUE, WK06_SIEG[0], WK06_SIEG[1])
        fr += light(WHITE, 0.4 * lift * np.exp(-((d - p) / 10) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction: horns and trombones holding the chords under the cries over
    tremolo cellos and basses, the Sword on the trumpets, the shimmer on violins and harp."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    pd_ = pan_at(at(G, 'Left', 0.0))
    o = Orchestra(M, level=2.6)

    def ps(t):
        return pan_at(np.interp(t, C['t'], C['sieg']))

    def size(t):
        return 0.4 + 0.6 * smoothstep(T_LINDE, T_ROLL, t) if t < T_FLARE else 0.6

    for t, d, m, v, part, h in compose():
        if part == 'linde':
            o.play('violins' if m >= 55 else 'violas', m, t, d, v - 4, pd_, 0.5)
            if v >= 90:
                o.play('oboes', m + 12, t, d, v - 16, pd_, 0.3)
        elif part == 'roll':
            o.play('cellos trem', m + 12 if m < 36 else m, t, max(d, 0.4), v, ps(t), 0.35)
            o.play('basses', m, t, d, v - 10, ps(t), 0.35)
        elif part == 'swell':
            o.play('horns', m, t, d, v, ps(t), 0.75)
            o.play('trombones', m - 12, t, d, v - 8, ps(t), 0.5)
            o.play('violins trem', m + 12, t, d, v - 12, pf, 0.35)
        elif part == 'sword':
            o.play('trumpets', m, t, d, v + 10, pf, 0.75)
            o.play('horns', m - 12, t, d, v - 6, pf, 0.4)
        elif part == 'shimmer':
            o.play('violins', m, t, 0.1, v - 10, pf + 0.2, 0.3)
            if m in (72, 84):
                o.play('harp', m - 12, t, d, v - 10, pf - 0.2, 0.3)
        else:
            o.tutti([(t, d, m, v, h)], size=size, pan=lambda t, m: ps(t))
    for t0, hd in CRIES:
        o.hit('timpani roll', t0 - 0.2, 100, gain=0.5, pan=ps(t0))
        o.hit('timpani', t0, 110, pitch=-4, gain=0.6, pan=ps(t0))
    o.hit('timpani roll', T_ROLL, 90, gain=0.4)
    o.hit('crash', T_FLARE, 110, gain=0.5, pan=pf)
    o.hit('timpani', T_FLARE, 110, pitch=-6, gain=0.6)
    # the stage: the hearth, the storm, the far thunder, the flare, the hilt, the sparks
    from pixelhome.audio import whoosh
    hc = pan_at(at(G, 'Left', 0.6))
    door = pan_at(G.length)

    def ember(tt):
        base = 0.35 * (1 - 0.3 * smoothstep(CRIES[0][0], T_FLARE, tt))
        flare = 1.1 * np.exp(-np.clip(tt - T_FLARE, 0, None) / 1.4) * (tt >= T_FLARE)
        return (base + flare) * (1 - 0.7 * smoothstep(T_DIE, D - 2.0, tt))
    o.fire(0.0, D, ember, pan=hc, crackle=10)
    o.wind(0.0, D, lambda tt: 0.45 - 0.2 * smoothstep(T_DIE, D, tt), pan=door)
    o.thunder(CRIES[1][0] + CRIES[1][1] + 1.2, near=0.25, pan=door, gain=0.9)
    for k, pp in enumerate((hc, 0.5 * (hc + pf), pf)):                         # the fire runs along the roof
        M.add('fx', whoosh(1.0, 300 + 400 * k, 3500, 0.7, seed=70 + k), T_FLARE + 0.25 * k, 0.8, pp)
    o.hit('metal', T_HILT, 120, gain=0.7, pan=pf, fx=True)
    o.hit('scrape', T_HILT, 110, gain=0.5, pan=pf, fx=True)
    o.hit('gong scrape', T_HILT + 0.1, 100, gain=0.4, pan=pf, fx=True)
    o.fire(T_HILT, T_GLEAM + 3.0, 0.12, pan=pf, crackle=45, seed=17)
    t_th = CRIES[1][0] + CRIES[1][1] + 1.2
    o.effects([(0, -3), (T_ROLL - 1.0, -3), (T_ROLL, -14), (t_th - 0.6, -14), (t_th - 0.2, 0), (t_th + 3.0, 0),
               (t_th + 4.5, -9), (T_FLARE - 0.6, -9), (T_FLARE - 0.1, 2), (T_HILT + 2.0, 1), (T_GLEAM - 0.5, -8),
               (D, -6)])
