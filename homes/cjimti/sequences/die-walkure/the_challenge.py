"""The Challenge: Hunding has heard enough. His house shelters the Wölfing tonight; tomorrow, with a strong weapon,
let him defend himself, and pay for the dead. Every low octave of his tread in the bass rolls dark red out from him
across the house; he rises, a flare of blood red in its black halo, and the red floods to a line by the hearth where
Siegmund's blue holds, the line pulsing between them. On the chromatic climb to "für Tote zahlst du mir Zoll" three
red and blue clashes flash on the porch, a glimpse of the fight at dawn, and the toll itself lands as a blast of red.

Sieglinde rises with the violins' climbing line, the hearth flaring as it peaks, and Hunding drives her from the room:
"Fort aus dem Saal!". She mixes his night drink at the corner of the porch over long held chords, and something else
goes in with the spices, a slow murky violet swirl; she carries it to him and he drinks. Then, as the orchestra swells,
she stops under the great ash tree and looks hard at one spot in the trunk: a line of amber runs from her to the tree
and the gold hilt of the buried sword blazes up on every note, and through the strings' trembling B and D that
follows it glitters and sparks among the leaves. His motif returns fortissimo: he drives her out through the inner
door at the corner of Left and Side and follows her away down Side, red pounding across the house on every chord,
and Siegmund is alone. The fire sinks to embers, the storm at the door quiets, and only the hilt keeps shining.

The music is Wagner's own: Act I, bars 696-712 and 756-772, as Solti's 1958 Vienna Philharmonic recording takes
them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). Hunding's low octaves are tubas, trombones,
basses and timpani; the chords of his motif trombones and horns; the swell under her look puts the trumpet on top;
the shimmer is violins and harp; the rest is the reduction orchestrated by hand and register. The stage adds its
sounds: the hearth crackling on Left and roaring up as she rises, the storm's wind at the door dying away, a thud
under every heavy step of his tread, steel clashing for the three glimpses of the fight, a great blow for the toll,
the drug's swirl as a scraped gong, and the inner door booming shut behind them. The effects lead through the
standoff and the toll and roar up with the hearth as she rises; they back well off when she looks at the tree, so
the Sword's swell is clear, return as he drives her out, and sink with the embers.

compose() tags every note, choreography() every move; stage(), room() and figure() are the hut and the people
in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK06'
TITLE = 'The Challenge'
KIND = 'show'
DESCRIPTION = ('Hunding realises his guest is the very man his kinsmen were hunting. Tonight the law protects him; '
               'at dawn they fight. His wife mixes his night drink with something extra, and on her way out she '
               'looks hard at one spot in the trunk of the old ash tree.')
VOICEOVER = ('Hunding knows exactly who his guest is. Tonight, the law protects him. '
             'In the morning, they fight, and the stranger has no weapon.')

EX = excerpt(__file__)                      # Act I, bars 696-712 and 756-772, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_KNOW = [BAR[696], BAR[697]]               # "Mein Haus hütet, Wölfing, dich heut'": he rises
T_ANSWER = BAR[700]                         # "mit starker Waffe doch wehre dich morgen": Siegmund's blue holds
T_DAWN = [next(n[0] for n in EX['notes'] if BAR[704] <= n[0] < BAR[705] and n[4] == 1 and n[2] == m)
          for m in (35, 36, 37)]            # the chromatic climb B, C, C#: a glimpse of tomorrow's fight
T_TOLL = BAR[705]                           # the held A after "für Tote zahlst du mir Zoll"
T_RISE = BAR[707]                           # she rises with the violins' climbing line
T_PEAK = BAR[710]
T_WEIB = BAR[710]                           # "Fort aus dem Saal!"
T_MIX = BAR[756]                            # the night drink, and the drug in it
T_DRINK = BAR[760] + 1.0                    # he drinks
T_LOOK = BAR[761]                           # she looks at the tree as the orchestra swells
T_GLINT = BAR[764]                          # the strings tremble: the hilt glitters
T_FORT = BAR[768]                           # his motif, fortissimo: he drives her out
T_ALONE = BAR[770]
D = EX['seconds']

HUT = hexc('#3a1a0a')
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
HUNDING = hexc('#8a0020')
STEEL = hexc('#e8f8ff')
DRUG = hexc('#6a4a90')
WHITE = hexc('#ffffff')

START = dict(bed=0.18, hearth=0.58, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)      # where WK05 left the hut
END = dict(bed=0.13, hearth=0.38, trunk=0.7, leaves=0.38, hilt=0.3, door=0.18)        # night: WK07 begins here
SM_START, SM_END = (0.5, 18.0), (0.36, 18.0)                     # Siegmund at Left 0.5: level, width
SL = (0.52, 16.0)                           # Sieglinde, from Left 0.22
HU = (0.66, 20.0)                           # Hunding, from Right 0.3

def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Hunding's hut as profiles over the house: the hearth on Left, the ash tree in the middle of Porch Front with
    its leaves over the porch and the sword's hilt in its trunk, the door at the free end of Right."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)       # the same fire, leaves and rain in every scene, so the cuts match
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


def room(S, T, lv):
    """The hut at shared time T with levels lv (bed, hearth, trunk, leaves, hilt, door)."""
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(HUT, lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(HEARTH, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(EMBER, 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAVES, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def figure(fr, S, p, col, lvl, w=18.0):
    """A person at path distance p: a body that stands in front of the room, and a soft halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.8 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.4 * lvl * np.exp(-((S['d'] - p) / (3.2 * w)) ** 2))


def brute(fr, S, p, lvl, w=20.0, dark=0.75):
    """Hunding: blood red in black. The room dims round him wherever he stands."""
    halo = np.exp(-((S['d'] - p) / (4.5 * w)) ** 2)
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - dark * min(1.0, lvl / 0.3) * np.maximum(halo, body))[:, None]
    return fr + light(HUNDING, lvl * body) + light(HUNDING, 0.3 * lvl * halo)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). 'tread' is Hunding's low
    octaves (at most one every 0.45 s; the rest are 'bass'), 'clash' the climb to the toll, 'toll' the toll itself,
    'climb' the violins' line as she rises, 'chord' his motif's chords, 'sword' the melody of the swell under her look,
    'glint' the strings' trembling; everything else is 'note'."""
    N, last = [], -9.0
    for t, d, m, v, h in EX['notes']:
        part = 'note'
        if h == 1 and m <= 47 and (t < T_MIX or t >= T_FORT):
            part = 'bass'
            if t - last >= 0.45:
                part, last = 'tread', t
        if h == 1 and any(abs(t - c) < 1e-6 for c in T_DAWN) and m in (35, 36, 37):
            part = 'clash'
        elif h == 1 and BAR[705] <= t < BAR[706]:
            part = 'toll'
        elif h == 0 and T_RISE <= t < T_WEIB:
            part = 'climb'
        elif h == 0 and T_FORT <= t < T_ALONE:
            part = 'chord'
        elif h == 0 and T_LOOK <= t < T_GLINT:
            part = 'sword'
        elif h == 0 and T_GLINT <= t < T_FORT:
            part = 'glint'
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
    """Per frame: where Sieglinde (0) and Hunding (1) are, and how bright; Siegmund stays at the hearth."""
    F = nframes(D)
    t = np.arange(F) * DT
    inner, hseat = at(G, 'Left', 0.03), at(G, 'Right', 0.3)
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where
        rate[k][m] = r

    set_(0, 0, D, at(G, 'Left', 0.22), 3.0)
    set_(0, T_RISE, T_MIX + 4.5, at(G, 'Porch Left', 0.25), 1.2)
    set_(0, T_MIX + 4.5, T_DRINK + 1.5, hseat - 40, 2.0)
    set_(0, T_DRINK + 1.5, T_FORT + 1, at(G, 'Porch Front', 0.32), 1.0)
    set_(0, T_FORT + 1, T_FORT + 5.5, inner, 1.4)
    set_(0, T_FORT + 5.5, D, -60.0, 0.9)
    set_(1, 0, D, hseat, 3.0)
    set_(1, T_KNOW[1], T_WEIB, hseat - 60, 2.0)
    set_(1, T_WEIB, T_FORT + 2, hseat, 1.5)
    set_(1, T_FORT + 2, T_FORT + 8.5, inner + 10, 0.9)
    set_(1, T_FORT + 8.5, D, -60.0, 0.9)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    sl = np.array([keys(x, [(T_FORT + 7, SL[0]), (T_FORT + 10.5, 0.0)]) for x in t])
    hu = np.array([keys(x, [(0, HU[0]), (T_KNOW[0], 0.8), (T_WEIB, 0.8), (T_WEIB + 3, HU[0]), (T_DRINK + 1, HU[0]),
                            (T_DRINK + 3, 0.6), (T_FORT + 10, 0.6), (T_FORT + 14, 0.0)]) for x in t])
    sm = np.array([keys(x, [(0, SM_START[0]), (T_ANSWER, SM_START[0]), (T_ANSWER + 1, 0.68), (T_TOLL, 0.62),
                            (T_TOLL + 0.4, 0.75), (T_WEIB, SM_START[0]), (T_ALONE, SM_START[0]),
                            (D - 2, SM_END[0])]) for x in t])
    return dict(t=t, pos=pos, sl=sl, hu=hu, sm=sm)


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    sm = at(G, 'Left', 0.5)
    tread = [e for e in N if e[4] in ('tread', 'toll')]
    stomp = np.array([e[0] for e in tread])
    stomp_big = np.array([1.0 if e[3] >= 80 or e[4] == 'toll' else 0.6 for e in tread])
    sword_on = np.array([e[0] for e in N if e[4] == 'sword'])
    glint = [(e[0], e[2]) for e in N if e[4] == 'glint']
    glint_t = np.array([g[0] for g in glint])
    glint_p = rng.normal(0, 1, len(glint))       # where each glitter lands in the canopy round the hilt
    climb = [(e[0], e[2]) for e in N if e[4] == 'climb']
    climb_t = np.array([c[0] for c in climb])
    swirl = Flicker(rng, G.N, 0.6, 2.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sl, hu = C['pos'][0][f], C['pos'][1][f]
        lv = {k: keys(t, [(0, START[k]), (T_FORT + 6, START[k]), (D - 3, END[k])]) for k in START}
        look = smoothstep(T_LOOK, T_LOOK + 1.0, t) * (1 - smoothstep(T_FORT - 1.5, T_FORT + 1.5, t))
        si = int(np.searchsorted(sword_on, t, side='right')) - 1
        ring = np.exp(-(t - sword_on[si]) / 0.4) if si >= 0 and t - sword_on[si] < 2 else 0.0
        lv['hilt'] += look * (0.5 + 0.4 * ring)
        lv['trunk'] += 0.1 * look
        # her rising line: the hearth leaps with every note, highest at the peak
        j = int(np.searchsorted(climb_t, t, side='right')) - 1
        if j >= 0 and t - climb_t[j] < 1.5:
            lv['hearth'] += 0.5 * np.clip((climb[j][1] - 55) / 30, 0.1, 1.0) * np.exp(-(t - climb_t[j]) / 0.35)
        fr = room(S, T, lv)
        if T_PEAK <= t < T_PEAK + 2.5:
            a = t - T_PEAK
            fr += light(HEARTH, 0.8 * np.exp(-a / 0.5) * np.exp(-((d - at(G, 'Left', 0.4)) / (80 + 500 * a)) ** 2))

        # his tread: dark red rolls across the house on every low octave, the loud ones all the way
        i = int(np.searchsorted(stomp, t, side='right')) - 1
        if i >= 0 and t - stomp[i] < 2.2:
            a = t - stomp[i]
            big = stomp_big[i]
            r = 30 + 800 * a
            band = np.exp(-((np.abs(d - hu) - r) / 170) ** 2) * np.exp(-a / (0.45 + 0.45 * big)) * big
            fr = fr * (1 - 0.6 * band)[:, None] + light(HUNDING, 0.95 * band)
        # the standoff: red floods from Hunding to a line by the hearth where Siegmund's blue holds
        war = smoothstep(T_KNOW[0] + 1, T_KNOW[1], t) * (1 - smoothstep(T_TOLL + 2, T_RISE + 2, t))
        if war > 0:
            line = sm + 150 + 50 * smoothstep(T_ANSWER, T_ANSWER + 3, t) - 50 * smoothstep(T_KNOW[1], T_ANSWER, t) \
                - 70 * smoothstep(T_TOLL - 0.3, T_TOLL + 0.3, t)
            red = smoothstep(line - 10, line + 60, d) * smoothstep(hu + 200, hu - 50, d)
            blue = smoothstep(line + 10, line - 60, d) * smoothstep(sm - 150, sm, d)
            fr = fr * (1 - 0.45 * war * red)[:, None] + light(HUNDING, 0.4 * war * red)
            fr += light(SIEGMUND, 0.45 * war * blue)
            fr += light(WHITE, 0.4 * war * np.exp(-((d - line) / 14) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * 1.2 * t)))
        # a glimpse of the fight at dawn: red and blue clash on the porch
        for j, tk in enumerate(T_DAWN):
            a = t - tk
            if 0 <= a < 0.9:
                c = at(G, 'Porch Front', 0.3 + 0.2 * j)
                fr += light(STEEL, 0.9 * np.exp(-a / 0.1) * np.exp(-((d - c) / 30) ** 2))
                fr += light(HUNDING, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - c - 60 - 200 * a) / 40) ** 2))
                fr += light(SIEGMUND, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - c + 60 + 200 * a) / 40) ** 2))
        # the toll: a blast of red from Hunding over the whole porch
        if T_TOLL <= t < T_TOLL + 3:
            a = t - T_TOLL
            fr += light(HUNDING, 0.7 * np.exp(-a / 0.6) * np.exp(-((d - hu) / (60 + 500 * a)) ** 2))

        # the drug: a slow murky swirl round her as she mixes, a glint carried to him
        mix = smoothstep(T_MIX, T_MIX + 1.5, t) * (1 - smoothstep(T_MIX + 4.5, T_MIX + 6, t))
        if mix > 0:
            sw = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - sl) / 70 - 0.5 * T))
            fr += light(DRUG, 0.95 * mix * sw * np.exp(-((d - sl) / 170) ** 2) * np.clip(0.6 + 0.4 * swirl(T), 0, None))
        if T_MIX + 4.5 <= t < T_DRINK + 3:
            q = sl - 25 if t < T_DRINK else sl - 25 + (hu - sl + 25) * smoothstep(T_DRINK, T_DRINK + 0.5, t)
            g = 1 - smoothstep(T_DRINK + 0.5, T_DRINK + 1.0, t)
            fr += light(DRUG, 0.7 * g * np.exp(-((d - q) / 10) ** 2))
            if t >= T_DRINK + 0.5:
                a = t - T_DRINK - 0.5
                fr += light(DRUG, 0.45 * np.exp(-a / 1.0) * np.exp(-((d - hu) / 60) ** 2))

        # her look at the tree: a line of amber from her to the trunk, and the hilt answers
        if look > 0:
            lo, hi = min(sl, pf), max(sl, pf)
            beam = smoothstep(lo - 5, lo + 25, d) * smoothstep(hi + 5, hi - 15, d)
            fr += light(SIEGLINDE, 0.45 * look * beam * (0.75 + 0.25 * np.cos(2 * np.pi * (d / 40 - 0.6 * T))))
            fr += light(HILT, look * (0.45 + 0.4 * ring) * np.exp(-((d - pf) / 25) ** 2))
            fr += light(STEEL, 0.5 * look * ring * np.exp(-((d - pf) / 6) ** 2))
            if si >= 0 and t - sword_on[si] < 1.5:    # every note of the swell rings out from the hilt
                a = t - sword_on[si]
                fr += light(HILT, 0.7 * look * np.exp(-a / 0.5) * np.exp(-((np.abs(d - pf) - 20 - 320 * a) / 40) ** 2))
        # the strings tremble: the hilt glitters and sparks fly up into the leaves
        k = int(np.searchsorted(glint_t, t, side='right'))
        for j in range(max(0, k - 6), k):
            a = t - glint_t[j]
            if a < 0.5:
                c = pf + 180 * glint_p[j]
                fr += light(HILT if glint[j][1] < 74 else STEEL, 1.0 * np.exp(-a / 0.15) * np.exp(-((d - c) / 14) ** 2))

        # the people
        fr = figure(fr, S, sm, SIEGMUND, C['sm'][f], SM_START[1])
        if C['sl'][f] > 0:
            fr = figure(fr, S, sl, SIEGLINDE, C['sl'][f], SL[1])
        if C['hu'][f] > 0:
            boost = 0.4 * stomp_big[i] * np.exp(-(t - stomp[i]) / 0.2) if i >= 0 else 0.0
            fr = brute(fr, S, hu, C['hu'][f] * (1 + boost), HU[1])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction: Hunding's tread on tubas, trombones, basses and timpani, his chords on
    trombones and horns, the trumpet on top of the swell under her look, violins and harp in the shimmer."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    o = Orchestra(M, level=2.6)
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def size(t):
        return 0.3 if T_MIX <= t < T_LOOK or T_GLINT <= t < T_FORT or t >= T_ALONE else 0.8

    for t, d, m, v, part, h in compose():
        hu = pan_at(np.interp(t, C['t'], C['pos'][1]))
        if part in ('tread', 'bass', 'toll', 'clash'):
            o.play('tuba', m, t, d, v, hu, 0.7 if part != 'bass' else 0.4)
            o.play('basses', m + 12 if m < 28 else m, t, d, v - 6, hu, 0.5)
            o.play('trombones', m + 12, t, d, v - 10, hu, 0.5 if part != 'bass' else 0.3)
            if part == 'tread':                                     # his heavy step
                o.hit('bass drum', t, min(127, v + 10), gain=0.5, pan=hu, fx=True)
            if part != 'bass' and (v >= 80 or part != 'tread'):
                o.hit('timpani', t, v, pitch=-4, gain=0.55, pan=hu)
            if part == 'clash':
                c = pan_at(at(G, 'Porch Front', 0.3 + 0.2 * T_DAWN.index(t)))
                o.clash(t, c, v, gain=1.0)
                o.hit('crash', t, v - 20, gain=0.3, pan=c)
            if part == 'toll' and d > 1:
                o.hit('crash', t, 110, gain=0.5, pan=hu)
        elif part == 'chord':
            o.play('trombones', m, t, d, v, hu, 0.6)
            o.play('horns', m + 12, t, d, v - 8, hu, 0.5)
        elif part == 'sword':
            o.play('trumpets', m, t, d, v, pf, 0.6)
            o.play('violins', m, t, d, v - 8, pf, 0.5)
        elif part == 'glint':
            o.play('violins', m, t, min(d, 0.2), v, pf, 0.45)
            o.play('harp', m, t, d, v - 10, pf + 0.2, 0.35)
        elif part == 'climb':
            o.play('violins', m, t, d, v, -0.2, 0.6)
            if m >= 72:
                o.play('flutes', m, t, d, v - 10, -0.3, 0.4)
        else:
            o.tutti([(t, d, m, v, h)], size=size)
    # the stage: the hearth, the storm at the door, the toll, the drug, the door shutting behind them
    lvl = lambda key: (lambda tt: np.interp(tt, [0, T_FORT + 6, D - 3], [START[key], START[key], END[key]]))
    flare = lambda tt: 0.9 * np.exp(-np.clip(tt - T_PEAK, 0, None) / 0.9) * (tt >= T_PEAK)
    o.fire(0.0, D, lambda tt: 0.7 * lvl('hearth')(tt) + flare(tt), pan=pan_at(at(G, 'Left', 0.4)), crackle=10)
    o.wind(0.0, D, lambda tt: 0.9 * lvl('door')(tt), pan=pan_at(G.length))
    o.boom(T_TOLL, pan_at(np.interp(T_TOLL, C['t'], C['pos'][1])), gain=0.9)
    p_mix = pan_at(np.interp(T_MIX, C['t'], C['pos'][0]))
    o.hit('gong scrape', T_MIX + 0.5, 100, gain=0.6, pan=p_mix, fx=True)
    o.hit('scrape', T_LOOK, 100, gain=0.4, pan=pf, fx=True)
    o.effects([(0, 0), (T_RISE, 0), (T_PEAK, 2), (T_PEAK + 2.5, 0), (T_LOOK - 1.0, 0), (T_LOOK, -10),
               (T_FORT - 0.5, -10), (T_FORT + 0.5, -2), (T_ALONE, -2), (D, -5)])
    shut = pan_at(at(G, 'Left', 0.03))
    o.boom(T_FORT + 9.0, shut, gain=0.55)
