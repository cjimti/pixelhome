"""Wehwalt: Hunding has asked the stranger who he is, and Siegmund tells his story while the room darkens round
the three of them and his memories play over the whole house. He may not call himself Friedmund, peaceful, he
says, only Wehwalt, woeful; and the tragic destiny of the Volsungs (Donington 66) sounds low in the horns.

Wolf was his father. A grey wolf-light with a core of deep god's blue runs with a small blue cub over the house,
out hunting through a forest of green dapples, horn calls and galloping basses. They come home to find the hall
burned: fire races out from the middle of the porch over the whole house, his mother, a pale light in the middle
of it, is snuffed out in a collapse of indigo while the Volsung motif breaks out in full, and his twin sister, a
small amber light, is carried off into the dark; by the fire on Left the real Sieglinde's light trembles. Father
and son lived wild in the forest after that, hunted by enemies like red sparks that they turned on and put out
in flashes of blue, until one day the father was gone: the wolf-light runs to the top of the porch and vanishes,
and for a moment a glow of deep blue and gold hangs there with a phrase of Valhalla (63) on the horns, for the
father was more than a wolf, and then only an empty grey pelt is left. He went among men and was hated. He fought
for a girl forced to marry against her will and killed her brothers, but her kinsmen came in their crowds, red
from both sides; she was killed before his eyes, his spear and shield were hacked to pieces in a spray of blue
shards and an anvil's ring, and he fled unarmed into the storm. "Now you know why I am not Friedmund": his weary
motif (35a) in the cellos, Sieglinde's sympathy in the oboe, the room returns, and across it Hunding's light
smoulders darker as his motif begins to stir in the tubas.

compose() holds every note, choreography() every memory; stage(), room() and figure() are the hut and the people
in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'WK05'
TITLE = 'Wehwalt'
KIND = 'show'
DESCRIPTION = ("The stranger tells his story: a wolf for a father, a home burned, a mother killed, a twin sister "
               'lost, a life on the run. He calls himself Woeful, and the woman by the fire listens to every word.')
VOICEOVER = ('Call me Woeful, the stranger says. Then he tells them his story, '
             'and it is one long run from fire, and from grief.')

K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_FATE = 1.0                                # the Volsung motif, low
T_HUNT = 7.0                                # father and son hunting
T_FIRE = 19.0                               # home to find the hall burning
T_SNUFF = 27.5                              # the mother killed; the Volsung motif in full
T_WILD = 31.0                               # living wild, hunted
T_GONE = 40.0                               # the father vanishes: Valhalla
T_BRIDE = 47.0                              # the forced bride; he kills her brothers
KILLS = [49.5, 50.6, 51.7]
T_LOST = 54.5                               # she is killed
T_SHATTER = 55.5                            # his weapons hacked to pieces
T_FLED = 58.0
T_WEARY = 60.0                              # "warum ich Friedmund nicht heisse"
T_SYM = 66.0
T_STIR = 72.0                               # Hunding's motif begins to stir
D = 80.0

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

HUNDING_MOTIF = [(0, 1.5, 'D2'), (1.5, 0.5, 'D2'), (2, 1, 'F2'), (3, 0.75, 'E2'), (3.75, 0.25, 'C#2'),
                 (4, 1.5, 'D2'), (5.5, 0.5, 'A1'), (6, 2, 'D2')]     # composed: the tubas' heavy tread
HUNT_CALL = [(0, 0.5, 'A3'), (0.5, 0.25, 'D4'), (0.75, 0.25, 'D4'), (1, 0.5, 'F4'), (1.5, 0.5, 'A4'), (2, 1, 'D5'),
             (3, 0.5, 'A4'), (3.5, 0.5, 'F4'), (4, 1.5, 'D4')]   # composed: a hunting call in D minor


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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'D1', 62, 'pedal')
    for t, m, v, d in play('volsung_fate', T_FATE, 0.6, 0, 74):
        add(t, d, m, v, 'fate', 0)
    for k, t0 in enumerate((T_HUNT + 0.5, T_HUNT + 4.5, T_HUNT + 8.5)):
        for b, d, m in HUNT_CALL:
            add(t0 + b * 0.32, d * 0.32, note(m) + (0, 3, -2)[k], 98 - 6 * k, 'call', k)
    for i in range(int((T_FIRE - T_HUNT) / 0.27)):   # galloping
        add(T_HUNT + i * 0.27, 0.2, ('D2', 'D2', 'A1')[i % 3], 76 + 10 * (i % 3 == 0), 'gallop')
    add(T_FIRE, T_SNUFF - T_FIRE + 1.0, 'D4', 86, 'blaze')
    add(T_FIRE + 1.0, T_SNUFF - T_FIRE, 'A4', 90, 'blaze')
    add(T_FIRE + 2.5, T_SNUFF - T_FIRE - 1.5, 'D5', 94, 'blaze')
    add(T_FIRE, 4.0, 'D1', 96, 'roll')
    for m in ('D2', 'A2'):
        add(T_FIRE, T_SNUFF - T_FIRE, m, 84, 'ember')
    add(T_FIRE + 3.5, 1.0, 'D1', 112, 'crash')
    add(T_SNUFF - 3.0, 3.0, 'D1', 104, 'roll')
    for t, m, v, d in play('volsung_fate', T_SNUFF, 0.5, 0, 112):
        add(t, d, m, v, 'fate', 1)
    for i in range(int((T_GONE - T_WILD - 1) / 0.25)):   # hunted: the low strings drive
        add(T_WILD + 1 + i * 0.25, 0.2, ('D2', 'F2', 'E2', 'D2', 'A1', 'D2', 'C#2', 'D2')[i % 8], 84, 'drive')
    for j, tk in enumerate((34.0, 35.4, 36.8, 38.2)):
        add(tk, 0.5, 'D2', 104, 'strike', j)
    for t, m, v, d in play('valhalla', T_GONE + 0.8, 0.6, 0, 76):
        add(t, d, m, v, 'valhalla')
    for i, m in enumerate(('Db4', 'F4', 'Ab4', 'Db5', 'F5')):
        add(T_GONE + 0.5 + 0.15 * i, 1.5, m, 66, 'harp')
    for i in range(int((T_LOST - T_BRIDE) / 0.25)):
        add(T_BRIDE + i * 0.25, 0.2, ('D2', 'Eb2', 'D2', 'A1')[i % 4], 88, 'drive')
    for j, tk in enumerate(KILLS):
        add(tk, 0.5, 'D2', 112, 'strike', j)
    add(T_LOST, 2.0, 'C2', 116, 'lost')
    add(T_SHATTER, 1.5, 'D1', 124, 'shatter')
    for t, m, v, d in play('siegmund_weary', T_WEARY, 0.6, 0, 84):
        add(t, d, m, v, 'weary')
    for t, m, v, d in play('sieglinde', T_SYM, 0.5, 0, 70, line='melody'):
        if m >= note('C4'):
            add(t, d, m, v, 'sym')
    for m in ('D3', 'F3', 'A3'):
        add(T_WEARY, T_STIR + 2 - T_WEARY, m, 56, 'pad')
    for b, d, m in HUNDING_MOTIF:
        add(T_STIR + 0.5 + b * 0.6, d * 0.6, m, 74, 'hunding', 0)
        add(T_STIR + 5.3 + b * 0.6, d * 0.6, m, 84, 'hunding', 1)
    return sorted(N, key=lambda e: e[0])


def choreography(G):
    """Per frame: where each memory is and how bright (father, cub, mother, sister, bride), and the foes."""
    F = nframes(D)
    t = np.arange(F) * DT
    A = lambda s, u: at(G, s, u)
    run = [(T_HUNT, A('Left', 0.85)), (T_HUNT + 2.5, A('Porch Left', 0.5)), (T_HUNT + 5, A('Porch Front', 0.75)),
           (T_HUNT + 7.5, A('Right', 0.6)), (T_HUNT + 10, A('Porch Right', 0.4)), (T_FIRE, A('Porch Front', 0.3)),
           (T_WILD, A('Porch Front', 0.3)), (T_WILD + 2.5, A('Right', 0.45)), (T_WILD + 5, A('Porch Left', 0.3)),
           (T_WILD + 7.5, A('Porch Right', 0.35)), (T_GONE, A('Porch Front', 0.5))]
    rt, rp = zip(*run)
    father = np.interp(t, rt, rp)
    cub = np.interp(t - 0.3, rt, rp) - 45
    cub_hero = np.interp(t, [T_GONE + 3, T_BRIDE + 2, T_LOST + 1.5, T_FLED], [A('Porch Front', 0.5),
                                                                            A('Porch Left', 0.6), A('Porch Left', 0.6),
                                                                            G.pd.max() + 40])
    cub = np.where(t > T_GONE + 3, cub_hero, cub)
    lv = lambda pts: np.array([keys(x, pts) for x in t])
    alpha = dict(
        father=lv([(T_HUNT - 1, 0), (T_HUNT + 0.5, 0.7), (T_GONE - 0.5, 0.7), (T_GONE + 0.8, 0)]),
        cub=lv([(T_HUNT - 1, 0), (T_HUNT + 0.5, 0.55), (T_FLED - 1, 0.55), (T_FLED + 0.5, 0)]),
        mother=lv([(T_FIRE - 1, 0), (T_FIRE, 0.6), (T_SNUFF, 0.6), (T_SNUFF + 0.3, 0)]),
        sister=lv([(T_FIRE - 1, 0), (T_FIRE, 0.55), (T_SNUFF + 0.5, 0.45), (T_WILD, 0)]),
        bride=lv([(T_BRIDE - 0.5, 0), (T_BRIDE + 0.5, 0.6), (T_LOST, 0.6), (T_LOST + 0.3, 0)]))
    sister = np.interp(t, [T_SNUFF - 1, T_WILD], [A('Porch Front', 0.62), A('Right', 0.9)])
    # foes: four chasing the wolves, then six closing on the bride from both sides
    foes = []
    for j in range(4):
        p = np.interp(t - 0.9 - 0.25 * j, rt, rp) + 30 * j
        a = lv([(T_WILD + 1, 0), (T_WILD + 2, 0.7), (34.0 + 1.4 * j, 0.7), (34.2 + 1.4 * j, 0)])
        foes.append((p, a, 34.0 + 1.4 * j))
    bride = A('Porch Left', 0.5)
    for j in range(6):
        side = -1 if j % 2 else 1
        p = bride + side * (90 + 40 * (j // 2)) + side * 500 * (1 - smoothstep(T_BRIDE, T_BRIDE + 3, t))
        dies = KILLS[j] if j < 3 else D + 1
        a = lv([(T_BRIDE, 0), (T_BRIDE + 1, 0.7), (dies, 0.7), (dies + 0.2, 0)])
        if j >= 3:                          # the rest of the kin flood in
            p = bride + side * (40 + 300 * (1 - smoothstep(T_LOST - 2, T_LOST, t)))
            a = lv([(T_LOST - 2.5, 0), (T_LOST - 1.5, 0.75), (T_FLED, 0.75), (T_FLED + 1, 0)])
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
    calls = np.array([e[0] for e in N if e[4] == 'call'])
    stomp = np.array([e[0] for e in N if e[4] == 'hunding'])
    strikes = [e for e in N if e[4] == 'strike']
    shards = dict(p=sm + rng.normal(0, 1, 0), v=np.zeros(0))
    sh_v = rng.choice([-1, 1], 60) * rng.uniform(150, 1100, 60)
    sh_w = rng.uniform(8, 18, 60)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        vis = keys(t, [(T_FATE + 3, 0.0), (T_HUNT, 1.0), (T_FLED + 1, 1.0), (T_WEARY + 4, 0.0)])
        lv = {k: keys(t, [(0, START[k]), (T_STIR, START[k]), (D - 1, END[k])]) for k in START}
        lv['door'] += 0.35 * smoothstep(T_SHATTER, T_FLED, t) * (1 - smoothstep(T_FLED + 1, T_WEARY + 3, t))
        fr = room(S, T, lv) * (1 - 0.6 * vis)

        # the Volsung motif: each chord a slow indigo breath from the storyteller
        i = int(np.searchsorted(fate_on, t, side='right')) - 1
        if i >= 0 and t - fate_on[i] < 3:
            a = t - fate_on[i]
            big = 1.0 if fate_on[i] >= T_SNUFF else 0.6
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
            g = smoothstep(T_GONE - 0.5, T_GONE + 1, t) * (1 - smoothstep(T_GONE + 4, T_GONE + 6.5, t))
            glow = np.exp(-((d - pf) / 330) ** 2)
            fr += light(WOTAN, 0.55 * g * glow) + light(GOLD, 0.5 * g * glow ** 3 * (0.8 + 0.2 * np.sin(2 * np.pi * 1.1 * t)))
            pelt = smoothstep(T_GONE + 0.5, T_GONE + 1.5, t) * (1 - smoothstep(T_GONE + 4.5, T_BRIDE, t))
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
        reach = smoothstep(T_SYM, T_SYM + 2, t) * (1 - smoothstep(T_SYM + 5, T_STIR + 1, t))
        fr = figure(fr, S, sl, SIEGLINDE, SL[0] * (1 + trem + 0.25 * reach), SL[1])
        if reach > 0:
            span = smoothstep(sl - 20, sl + 20, d) * smoothstep(sm + 10, sm - 30, d)
            fr += light(SIEGLINDE, 0.35 * reach * span)
        k = int(np.searchsorted(stomp, t, side='right')) - 1
        if k >= 0 and t - stomp[k] < 1.6:   # his motif stirring: dark red ripples from his seat
            a = t - stomp[k]
            band = np.exp(-((np.abs(d - hu) - 30 - 450 * a) / 90) ** 2) * np.exp(-a / 0.5) * (0.5 + 0.1 * (t > T_STIR + 5))
            fr = fr * (1 - 0.6 * band)[:, None] + light(HUNDING, 0.4 * band)
        hl = keys(t, [(0, HU_START[0]), (T_BRIDE, HU_START[0]), (T_BRIDE + 3, 0.72), (T_WEARY, 0.62), (T_STIR, 0.62),
                      (D - 1, HU_END[0])])
        fr = brute(fr, S, hu, hl, HU_END[1])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(track, t):
        return pan_at(np.interp(t, C['t'], C[track]))

    for name, gain, rev in (('low', 0.32, 0.22), ('strings', 0.27, 0.32), ('winds', 0.26, 0.35), ('brass', 0.25, 0.3),
                            ('harp', 0.26, 0.4), ('perc', 0.28, 0.28), ('fx', 0.13, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v3*.wav')
    gong = M.hits('Percussion/gongHit_f.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    sm, sl, hu = (pan_at(at(G, *x)) for x in (('Left', 0.5), ('Left', 0.22), ('Right', 0.3)))
    pf = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'fate':
            g = 1.0 if k == 1 else 0.7
            s = horn if m >= note('G3') else tbn
            M.add('brass', s.play(m, v, dur=d * 1.05, release=0.5), t, 0.7 * g, sm if k == 0 else 0.0)
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.5), t, 0.7 * g, 0.0)
        elif part == 'call':
            pa = pan_of('father', t)
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, pa)
            M.add('brass', horn.play(m - 12, v - 14, dur=d * 1.05, release=0.4), t, 0.5, pa)
        elif part == 'gallop':
            M.add('low', pizz.play(m + 12, v), t, 0.8, pan_of('father', t))
        elif part == 'blaze':
            hold('strings', vtrem, m, t, t + d, v, -0.3 + 0.3 * (m % 3), rise=1.5, fall=1.5, gain=0.8)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.8, pf)
            M.add('fx', whoosh(2.0, 300, 3000, 0.7, seed=19), t - 0.5, 0.9, pf)
        elif part == 'ember':
            hold('low', vc, m, t, t + d, v, pf, rise=1.0, fall=1.0, gain=0.6)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, pf)
        elif part == 'drive':
            pa = pan_of('cub', t)
            M.add('low', cbs.play(m, v), t, 0.8, pa)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, pa)
        elif part == 'strike':
            pa = pan_of('cub', t)
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, pa)
            M.add('brass', tbn.play(m + 12, v, dur=0.3, release=0.2), t, 0.7, pa)
        elif part == 'valhalla':
            M.add('brass', (horn if m >= note('Ab3') else tbn).play(m, v, dur=d * 1.05, release=0.6), t, 0.6, pf)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.9, pf)
        elif part == 'lost':
            M.add('perc', gong.play(v), t, 0.7, pan_at(C['bride']))
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.5), t, 0.8, pan_at(C['bride']))
        elif part == 'shatter':
            pa = pan_at(C['cub'][int(T_SHATTER / DT)])
            M.add('perc', anvil.play(124), t, 0.9, pa)
            M.add('perc', anvil.play(110), t + 0.18, 0.7, pa - 0.2)
            M.add('perc', crash.play(120), t, 0.8, pa)
            M.add('fx', whoosh(0.8, 6000, 800, 0.7, seed=55), t, 0.9, pa)
        elif part == 'weary':
            if d > 2:
                hold('strings', vc, m, t, t + min(d, 4.0), v, sm, rise=0.4, fall=1.5, gain=0.8)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, sm)
        elif part == 'sym':
            M.add('winds', ob.play(m, v, dur=d * 1.1, release=0.4), t, 0.8, sl)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, -0.3, rise=2.0, fall=2.0, gain=0.5)
        elif part == 'hunding':
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, hu)
            M.add('perc', timp.play(v - 10, pitch=-4 if m % 12 == 2 else -9), t, 0.6, hu)
