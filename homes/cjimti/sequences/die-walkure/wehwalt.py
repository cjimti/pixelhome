"""Wehwalt: Hunding has asked the stranger who he is, and Siegmund tells his story while the room darkens round
the three of them and his memories play over the whole house.

Wolf was his father. A grey wolf-light with a core of deep god's blue runs with a small blue cub over the house,
out hunting through a forest of green dapples to the strings' galloping figure. They come home to find the nest
empty and the hall burned: fire races out from the middle of the porch over the whole house, his mother, a pale
light in the middle of it, is snuffed out in a collapse of indigo on the orchestra's great cry, and his twin
sister, a small amber light, is carried off into the dark; by the fire on Left the real Sieglinde's light
trembles. Father and son lived wild in the forest after that, hunted by the Neidings like red sparks that they
turned on and scattered like chaff in flashes of blue, until one day the father was gone: for a moment a glow of
deep blue and gold hangs over the porch, for the father was more than a wolf, and then only an empty grey pelt is
left. Years later he fought for a girl forced to marry against her will and struck down her brothers, one on each
blow of the orchestra; but their kinsmen came storming in their crowds, red from both sides, over the basses'
surging tremolo. He shielded her with spear and shield, parrying blow after blow, until spear and shield were
hacked to pieces in a spray of blue shards, and he fled unarmed out of the door, while across the room Hunding's
light smoulders darker.

The music is Wagner's own: Act I, bars 502 to 513, the hunt and the burned hall; bars 542 to 547, the Neidings'
hunt; bars 612 to 615, the forced bride and her brothers struck down; and bars 633 to 642, the kinsmen's revenge
and the shattered weapons, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the
Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py), orchestrated by hand and register: the
right hand on violins and woodwinds, the left hand's lines on horns, violas and cellos, the bass on cellos, basses
and tuba, the orchestra fuller as the story grows, with timpani and cymbals on its great accents. Around the score,
as a staging would: the hut's hearth crackles; wolf and cub run on padding feet; the burning hall roars, crackles
and falls in on his mother. Steel rings as the wolves turn on the Neidings, a god's shimmer marks the father
vanishing, and each brother falls with a clash and a blow. The kinsmen come running from both ends of the
house, every parry rings, spear and shield shatter, and his feet run for the door. The effects lead with his
story's violent images (the fire, the fights, the kinsmen and the shattering); they recede for the father's
vanishing and the forced bride, and fade back into the hut as he flees.

compose() tags every note of the excerpt, choreography() every memory; stage(), room() and figure() are the hut and
the people in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK05'
TITLE = 'Wehwalt'
KIND = 'show'
DESCRIPTION = ("The stranger tells his story: a wolf for a father, a home burned, a mother killed, a twin sister "
               'lost, a life on the run. He calls himself Woeful, and the woman by the fire listens to every word.')
VOICEOVER = ('Call me Woeful, the stranger says. Then he tells them his story, '
             'and it is one long run from fire, and from grief.')

EX = excerpt(__file__)                      # Act I, bars 502-513, 542-547, 612-615 and 633-642, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_HUNT = 0.0                                # father and son hunting
T_NEST = BAR[504] + 1.2                     # "da lag das Wolfsnest leer"
T_FIRE = BAR[507]                           # "Zu Schutt gebrannt der prangende Saal"
T_SNUFF = BAR[510]                          # the mother killed
T_WILD = BAR[542]                           # living wild, hunted by the Neidings
STRIKES = [BAR[544], BAR[545], BAR[546], BAR[546] + 1.2]   # the wolves turn on them
T_GONE = BAR[547]                           # the father vanishes
T_BRIDE = BAR[612]                          # the forced bride
KILLS = [BAR[613], BAR[614], BAR[615]]      # he strikes down her brothers
T_KIN = BAR[633]                            # "Der Erschlagnen Sippen stürmten daher"
T_SHATTER = BAR[641]                        # spear and shield hacked to pieces
T_LOST = T_SHATTER + 0.8                    # she is lost to him
T_FLED = BAR[642]                           # he flees unarmed
NKIN = 8

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
WOLF = hexc('#a8b0c8')
WOTAN = hexc('#1a3cff')
GOLD = hexc('#ffd060')
MOTHER = hexc('#ffe0d8')
FIRE = hexc('#ff4a08')
FLAME = hexc('#ffa020')
ASH = hexc('#4a4450')
FATE = hexc('#2a1a5a')
FOE = hexc('#ff1a10')
SHARD = hexc('#e8f8ff')

START = dict(bed=0.18, hearth=0.6, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)       # where WK04 left the hut
END = dict(bed=0.18, hearth=0.58, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)
SM = (0.5, 18.0)                            # Siegmund at Left 0.5: level, width
SL = (0.52, 16.0)                           # Sieglinde at Left 0.22
HU_START, HU_END = (0.6, 20.0), (0.66, 20.0)                     # Hunding at Right 0.3

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The orchestra's great accents
    (velocity 105 and up) are 'fate'; in the kinsmen's fight the loud notes are 'parry'; the basses' surging
    tremolo is 'surge'; everything else is 'tutti', orchestrated by hand and register."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        b = bar_of(t)
        if v >= 105:
            part = 'fate'
        elif 637 <= b <= 641 and v >= 95:
            part = 'parry'
        elif 633 <= b <= 636 and h == 1:
            part = 'surge'
        else:
            part = 'tutti'
        N.append((t, d, m, v, part, h))
    return N


def size(t):
    """How full the orchestra is as the story goes."""
    return keys(t, [(0, 0.6), (T_NEST, 0.3), (T_FIRE, 0.6), (T_SNUFF, 1.0), (T_SNUFF + 6, 0.5), (T_WILD, 0.8),
                    (T_BRIDE, 1.0), (T_KIN, 0.6), (T_SHATTER, 1.0), (D, 0.4)])


def choreography(G):
    """Per frame: where each memory is and how bright (father, cub, mother, sister, bride), and the foes."""
    F = nframes(D)
    t = np.arange(F) * DT
    A = lambda s, u: at(G, s, u)
    run = [(T_HUNT, A('Left', 0.85)), (T_HUNT + 2.0, A('Porch Left', 0.5)), (T_HUNT + 4, A('Porch Front', 0.75)),
           (T_HUNT + 6, A('Right', 0.6)), (T_HUNT + 9, A('Porch Right', 0.4)), (T_FIRE, A('Porch Front', 0.3)),
           (T_WILD, A('Porch Front', 0.3)), (T_WILD + 2.5, A('Right', 0.45)), (T_WILD + 5, A('Porch Left', 0.3)),
           (T_WILD + 7.5, A('Porch Right', 0.35)), (T_WILD + 10, A('Right', 0.3)), (T_GONE, A('Porch Front', 0.5))]
    rt, rp = zip(*run)
    father = np.interp(t, rt, rp)
    cub = np.interp(t - 0.3, rt, rp) - 45
    cub_hero = np.interp(t, [T_GONE + 2, T_BRIDE + 2, T_SHATTER + 0.5, T_FLED + 2.5], [A('Porch Front', 0.5),
                                                                                    A('Porch Left', 0.6),
                                                                                    A('Porch Left', 0.6),
                                                                                    G.pd.max() + 40])
    cub = np.where(t > T_GONE + 2, cub_hero, cub)
    lv = lambda pts: np.array([keys(x, pts) for x in t])
    alpha = dict(
        father=lv([(T_HUNT, 0), (T_HUNT + 0.8, 0.7), (T_GONE - 0.5, 0.7), (T_GONE + 0.8, 0)]),
        cub=lv([(T_HUNT, 0), (T_HUNT + 0.8, 0.55), (T_FLED + 1, 0.55), (T_FLED + 2.5, 0)]),
        mother=lv([(T_FIRE - 1, 0), (T_FIRE, 0.6), (T_SNUFF, 0.6), (T_SNUFF + 0.3, 0)]),
        sister=lv([(T_FIRE - 1, 0), (T_FIRE, 0.55), (T_SNUFF + 0.5, 0.45), (T_WILD, 0)]),
        bride=lv([(T_BRIDE - 0.5, 0), (T_BRIDE + 0.5, 0.6), (T_LOST, 0.6), (T_LOST + 0.3, 0)]))
    sister = np.interp(t, [BAR[512], T_WILD], [A('Porch Front', 0.62), A('Right', 0.9)])
    # foes: four chasing the wolves, then six closing on the bride from both sides
    foes = []
    for j in range(4):
        p = np.interp(t - 0.9 - 0.25 * j, rt, rp) + 30 * j
        a = lv([(T_WILD + 0.5, 0), (T_WILD + 1.5, 0.7), (STRIKES[j], 0.7), (STRIKES[j] + 0.2, 0)])
        foes.append((p, a, STRIKES[j]))
    bride = A('Porch Left', 0.5)
    for j in range(3 + NKIN):
        side = -1 if j % 2 else 1
        p = bride + side * (90 + 40 * (j // 2)) + side * 500 * (1 - smoothstep(T_BRIDE, T_BRIDE + 2, t))
        dies = KILLS[j] if j < 3 else D + 1
        a = lv([(T_BRIDE, 0), (T_BRIDE + 0.6, 0.7), (dies, 0.7), (dies + 0.2, 0)])
        if j >= 3:                          # the kinsmen storm in from both ends of the house, wave after wave
            k = j - 3
            t0 = T_KIN + 1.2 * k
            far = G.pd.max() + 60 if side > 0 else -60
            p = far + (bride + side * (60 + 25 * (k // 2)) - far) * smoothstep(t0, t0 + 5.0, t)
            a = lv([(t0, 0), (t0 + 0.8, 0.8), (T_FLED, 0.8), (T_FLED + 1.5, 0)])
        foes.append((p, a, dies))
    return dict(t=t, father=father, cub=cub, sister=sister, alpha=alpha, foes=foes,
                mother=A('Porch Front', 0.42), bride=bride)


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    sm, sl, hu = at(G, 'Left', 0.5), at(G, 'Left', 0.22), at(G, 'Right', 0.3)
    dapple = Flicker(rng, G.N, 0.3, 1.2)
    blaze = Flicker(rng, G.N, 2.0, 7.0)
    fate_on = np.array(sorted({e[0] for e in N if e[4] == 'fate'}))
    calls = np.array(sorted({e[0] for e in N if e[0] < T_NEST and e[5] == 1}))
    surge = np.array([e[0] for e in N if e[4] == 'surge'])
    parry = np.array(sorted({e[0] for e in N if e[4] == 'parry'}))
    sh_v = rng.choice([-1, 1], 60) * rng.uniform(150, 1100, 60)
    sh_w = rng.uniform(8, 18, 60)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        vis = keys(t, [(0, 0.6), (1.5, 1.0), (T_FLED + 1, 1.0), (D, 0.3)])
        lv = {k: keys(t, [(0, START[k]), (T_FLED, START[k]), (D - 0.5, END[k])]) for k in START}
        lv['door'] += 0.35 * smoothstep(T_SHATTER, T_FLED, t) * (1 - smoothstep(D - 1.5, D - 0.2, t))
        fr = room(S, T, lv) * (1 - 0.6 * vis)

        # the Volsung motif: each chord a slow indigo breath from the storyteller
        i = int(np.searchsorted(fate_on, t, side='right')) - 1
        if i >= 0 and t - fate_on[i] < 3:
            a = t - fate_on[i]
            big = 1.0
            fr += light(FATE, 0.55 * big * np.exp(-a / 1.2) * np.exp(-((np.abs(d - sm) - 300 * a) / 200) ** 2))

        # the hunt: a forest of dapples; each horn call flares the wolves
        forest = smoothstep(T_HUNT - 0.5, T_HUNT + 1.5, t) * (1 - smoothstep(T_FIRE - 1, T_FIRE + 1, t))
        forest += 0.6 * smoothstep(T_WILD, T_WILD + 1.5, t) * (1 - smoothstep(T_GONE - 1, T_GONE + 1, t))
        if forest > 0:
            fr += light(LEAVES, forest * 0.34 * np.clip(0.3 + dapple(T), 0, None) * S['stir'](T * 3) ** 2)
            fr += light(LEAVES, forest * 0.1)

        # the hall burning: fire races out from the middle of the porch, then dies to ash
        if T_FIRE <= t < T_WILD + 1:
            a = t - T_FIRE
            r = 2000 * smoothstep(0, 4.5, a)
            burn = smoothstep(r, r - 300, np.abs(d - pf)) * (1 - smoothstep(T_SNUFF + 0.5, T_WILD, t))
            fl = np.clip(blaze(T), 0, None) / 1.7
            fr += light(FIRE, burn * (0.3 + 0.5 * fl)) + light(FLAME, 0.9 * burn * fl ** 3)
            ash = smoothstep(T_SNUFF, T_SNUFF + 1.5, t) * (1 - smoothstep(T_WILD - 0.5, T_WILD + 1, t))
            fr += light(ASH, 0.35 * ash * smoothstep(1400, 900, np.abs(d - pf)))
        if T_SNUFF <= t < T_SNUFF + 2.5:    # the mother: an indigo collapse where she was
            a = t - T_SNUFF
            fr += light(FATE, 0.8 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - C['mother']) - 260 * (1 - a / 2.5)) / 70) ** 2))
            fr += light(MOTHER, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - C['mother']) / 25) ** 2))

        # the father gone: deep blue and gold over the porch, then an empty pelt
        if T_GONE - 0.5 <= t < T_BRIDE:
            g = smoothstep(T_GONE - 0.5, T_GONE + 0.6, t) * (1 - smoothstep(T_GONE + 1.8, T_GONE + 2.9, t))
            glow = np.exp(-((d - pf) / 330) ** 2)
            fr += light(WOTAN, 0.55 * g * glow) + light(GOLD, 0.5 * g * glow ** 3 * (0.8 + 0.2 * np.sin(2 * np.pi * 1.1 * t)))
            pelt = smoothstep(T_GONE + 0.5, T_GONE + 1.2, t) * (1 - smoothstep(T_GONE + 2.0, T_BRIDE, t))
            fr += light(WOLF, 0.3 * pelt * np.exp(-((d - pf) / 40) ** 2))

        # memories as lights
        j = int(np.searchsorted(calls, t, side='right')) - 1
        flare = 0.3 * np.exp(-(t - calls[j]) / 0.25) if j >= 0 and t < T_FIRE else 0.0
        A = C['alpha']
        if A['father'][f] > 0:
            fr = figure(fr, S, C['father'][f], WOLF, A['father'][f] * (1 + flare), 22)
            fr += light(WOTAN, 0.6 * A['father'][f] * np.exp(-((d - C['father'][f]) / 9) ** 2))
        for who, p, col, w in (('cub', C['cub'][f], SIEGMUND, 12), ('mother', C['mother'], MOTHER, 16),
                               ('sister', C['sister'][f], SIEGLINDE, 10), ('bride', C['bride'], MOTHER, 14)):
            if A[who][f] > 0:
                fr = figure(fr, S, p, col, A[who][f] * (1 + (flare if who == 'cub' else 0)), w)
        for p, a, dies in C['foes']:
            if a[f] > 0:
                fr += light(FOE, a[f] * np.exp(-((d - p[f]) / 11) ** 2))
            if dies <= t < dies + 0.6:      # put out in a flash of blue
                k = t - dies
                fr += light(SHARD, 0.8 * np.exp(-k / 0.12) * np.exp(-((d - p[f]) / 30) ** 2))
                fr += light(SIEGMUND, 0.5 * np.exp(-k / 0.25) * np.exp(-((np.abs(d - p[f]) - 220 * k) / 40) ** 2))
        if T_LOST <= t < T_LOST + 2.5:      # the bride killed
            a = t - T_LOST
            fr += light(FATE, 0.8 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - C['bride']) - 200 * (1 - a / 2.5)) / 60) ** 2))
        # the kinsmen's surge: the basses' tremolo pulses red over the whole house, wilder as they close in
        if len(surge) and surge[0] <= t < T_SHATTER:
            j = int(np.searchsorted(surge, t, side='right')) - 1
            gr = smoothstep(T_KIN, BAR[636], t)
            fr += light(FOE, (0.15 + 0.3 * gr) * np.exp(-(t - surge[j]) / 0.1) * (0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 + 2 * t))))
        # his parries: each blow a white flash at his shield and a ring of blue
        j = int(np.searchsorted(parry, t, side='right')) - 1 if len(parry) else -1
        if j >= 0 and t - parry[j] < 0.8 and t < T_SHATTER:
            a = t - parry[j]
            q = C['cub'][f]
            fr += light(SHARD, 0.85 * np.exp(-a / 0.1) * np.exp(-((d - q) / 25) ** 2))
            fr += light(SIEGMUND, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - q) - 40 - 500 * a) / 50) ** 2))
        if T_SHATTER <= t < T_SHATTER + 2.5:    # spear and shield hacked to pieces
            a = t - T_SHATTER
            q = C['cub'][int(T_SHATTER / DT)] + sh_v * (1 - np.exp(-a / 0.5)) * 0.6
            g = np.exp(-((d[:, None] - q[None, :]) / sh_w[None, :]) ** 2).max(axis=1)
            fr += light(SHARD, 0.9 * np.exp(-a / 0.7) * g)
            fr += light(SHARD, 0.4 * np.exp(-a / 0.1))

        # the people in the room: Siegmund telling, Sieglinde trembling at her lost sister, Hunding darkening
        tell = 0.12 * vis
        fr = figure(fr, S, sm, SIEGMUND, SM[0] + tell, SM[1])
        trem = 0.25 * smoothstep(T_SNUFF - 1, T_SNUFF, t) * (1 - smoothstep(T_WILD, T_WILD + 3, t)) * np.sin(2 * np.pi * 5 * t)
        fr = figure(fr, S, sl, SIEGLINDE, SL[0] * (1 + trem), SL[1])
        hl = keys(t, [(0, HU_START[0]), (T_BRIDE, HU_START[0]), (T_BRIDE + 3, 0.72), (T_FLED, 0.72), (D - 0.5, HU_END[0])])
        fr = brute(fr, S, hu, hl, HU_END[1])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction by hand and register, the orchestra fuller as the story
    grows: timpani, cymbals and the brass on its great accents, the basses' tremolo on cellos and basses, the parries
    on the brass with the anvil ringing, and a crash where spear and shield break."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(track, t):
        return pan_at(np.interp(t, C['t'], C[track]))

    o = Orchestra(M, level=2.7)
    notes = compose()
    tutti = [(t, d, m, v, h) for t, d, m, v, part, h in notes if part == 'tutti']
    o.tutti(tutti, size=size, pan=lambda t, m: 0.6 * pan_of('cub', t) if t > T_HUNT + 1 else None)
    hits = set()
    for t, d, m, v, part, h in notes:
        if part == 'fate':
            if h == 0:
                o.play('trumpets' if m >= 60 else 'horns', m - 12 if m >= 72 else m, t, d, v, 0.25, 0.55)
                o.play('violins', m, t, d, v - 6, 0.3, 0.5)
            else:
                o.play('trombones', m if m >= 40 else m + 12, t, d, v, 0.0, 0.7)
                o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 6, 0.0, 0.6)
            if round(t, 1) not in hits:
                hits.add(round(t, 1))
                o.hit('timpani', t, 120, pitch=-5, gain=0.7)
                o.hit('crash', t, 110, gain=0.45)
        elif part == 'parry':
            o.play('horns' if m < 67 else 'trumpets', m if m < 67 else m - 12, t, d, v, 0.6 * pan_of('cub', t), 0.6)
            if round(t, 1) not in hits:
                hits.add(round(t, 1))
                o.clash(t, 0.6 * pan_of('cub', t), 100, 0.55)       # spear and shield take the blows
        elif part == 'surge':
            o.play('cellos', m, t, 0.1, v + 30, -0.3, 0.35)
            o.play('basses', m - 12, t, 0.1, v + 24, 0.3, 0.3)
    o.hit('crash', T_SHATTER, 124, gain=0.7)
    o.hit('gong', T_SHATTER, 110, gain=0.5)
    # the stage: the story's sounds over the score
    # his story's images lead: the burning hall, the fights, the kinsmen; the father's vanishing and the bride are
    # quieter, and his flight fades back into the hut
    o.effects([(0.0, -3.0), (T_FIRE - 0.5, -1.0), (T_FIRE, 1.0), (T_SNUFF + 2.0, -2.0), (T_WILD, -1.0),
               (T_GONE - 1.5, -2.0), (T_GONE, -7.0), (T_BRIDE + 0.5, -7.0), (KILLS[0] - 0.2, 0.0), (T_KIN, 0.0),
               (T_SHATTER, 1.0), (T_FLED + 1.0, -2.0), (D, -7.0)])
    o.fire(0.0, D, 0.2, pan_at(at(G, 'Left', 0.5)), crackle=10, seed=90)          # the hearth in the hut
    o.gallop(T_HUNT + 0.3, T_NEST, 0.36, lambda t: pan_of('father', t), v=96, gain=0.7)     # wolf and cub running
    o.gallop(T_WILD + 0.2, T_GONE, 0.34, lambda t: pan_of('father', t), v=100, gain=0.75)
    fp = pan_at(at(G, 'Porch Front', 0.5))
    o.fire(T_FIRE - 0.3, T_WILD - 1.0, lambda tt: np.clip((tt - T_FIRE + 0.3) / 0.8, 0, 1) *
           (1 - 0.6 * np.clip((tt - T_SNUFF) / 3, 0, 1)), fp, crackle=40, seed=91)       # the hall burning
    o.boom(T_FIRE, fp, 0.6)
    o.boom(T_SNUFF, fp, 0.9)                                                         # the roof falls in on her
    o.hit('glass', T_SNUFF + 0.05, 90, gain=0.3, pan=fp, fx=True)
    for tk in STRIKES:                                                               # the wolves turn on the Neidings
        o.clash(tk, pan_of('father', tk), 108, 0.6)
        o.hit('bass drum', tk, 100, gain=0.45, pan=pan_of('father', tk), fx=True)
    o.hit('cymbal swell', T_GONE - 1.2, 84, gain=0.4, pan=fp)                       # the father vanishes: a god's glow
    o.play('glock', 84, T_GONE, 0.5, 90, fp, 0.35)
    o.play('glock', 91, T_GONE + 0.12, 0.5, 84, fp, 0.3)
    bp = pan_at(C['bride'])
    for tk in KILLS:                                                                 # he strikes down her brothers
        o.clash(tk, bp, 122, 0.85)
        o.boom(tk + 0.05, bp, 0.6)
    lft, rgt = pan_at(-60.0), pan_at(G.pd.max() + 60)
    o.gallop(T_KIN, T_SHATTER, 0.3, lambda t: lft + (bp - lft) * min(1, (t - T_KIN) / 5), v=110, gain=0.6)
    o.gallop(T_KIN + 0.15, T_SHATTER, 0.32, lambda t: rgt + (bp - rgt) * min(1, (t - T_KIN) / 5), v=110, gain=0.6)
    o.shatter(T_SHATTER, bp, 1.0)                                                    # spear and shield in pieces
    t = T_FLED
    while t < T_FLED + 2.6:                                                          # he runs out unarmed
        o.hit('hoof soft', t, 96, pitch=4, gain=0.45, pan=pan_of('cub', t), fx=True)
        t += 0.22
    o.hit('timpani roll', T_FIRE, 96, gain=0.5)
    o.hit('timpani roll', T_KIN, 90, gain=0.5)
