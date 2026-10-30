"""Nothung!: the moonlit spring night, the lovers beside the ash tree on Porch Front. Sieglinde asks him: was his
father truly Wälse? The love of the twins in its second form (Donington 37a) on the oboe; then the Wälsungs'
own music, Siegmund's motif (Donington 35) and their tragic destiny (Donington 66), deep in the cellos and horns,
and her amber flares and sends two waves of recognition over the house. She knows him. "Siegmund: so nenn ich
dich!" One great chord: his blue blazes and a ring of blue and amber runs out over the whole roof.

He springs to the trunk and lays his hand on the hilt. "Nothung! Nothung!" (Donington 43) on horns and cellos
with a trumpet over them, each note flaring the hilt, while the spring dims around the tree and the strings
tremble and climb. Three heaves, three jolts of white-gold up out of the trunk, each wider than the last; and on
the fourth the sword comes out. The Sword (Donington 45) on the trumpets, fortissimo, and a flash of white steel
bursts out of the trunk and races to both ends of the house, the whole roof white for an instant, cymbals and
gong and timpani, then steel-blue light shivering everywhere. He holds Nothung up: a blade of white steel beside
his blue. The tree is left with a gash, dark with pale edges where the hilt was.

She is his sister and his bride: the love of the twins (37) at full strength, and the house goes wild, blue
and amber and steel bands chasing each other round the roof while the blossoms pour down. They run: along
Porch Right and Right, trailing light, and out through the open door at the free end of Right, into the spring
night, with racing strings and blaring brass. The act ends on three huge G major chords, three flashes of
the whole house, and the hut is left empty in the moonlight: the gashed tree, the open door, the embers.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK10'
TITLE = 'Nothung!'
KIND = 'show'
DESCRIPTION = ('Sieglinde knows him at last and names him Siegmund. He takes hold of the sword in the tree, '
               'names it Nothung, and pulls it out in a blaze of white steel. Then the two of them run out into '
               'the spring night together.')
VOICEOVER = ('She knows who he is now, and he knows what is waiting for him in that tree. '
             'This is the moment the whole act has been building to.')

K = 9                                       # this scene's place in the shared clock (t + 80 * K)
T_ASK = 1.0                                 # was Wälse your father?
T_WALSUNG = 6.5                             # the Wälsungs' music
T_FATE = 11.0
T_NAME = 15.0                               # "Siegmund: so nenn ich dich!"
T_SPRING = 17.5                             # he springs to the tree
T_NOTHUNG = 19.0
NBEAT = 0.6
HEAVES = [27.2, 29.2, 31.2]
T_DRAW = 33.2                               # the sword comes out
T_SWORD2 = 38.0
T_BRIDE = 45.5                              # bride and sister
T_RUN = 60.0                                # out into the night
T_OUT = 69.5
CHORDS = [70.4, 71.5, 72.9]                 # the act's last chords
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
MOON = hexc('#c8dcff')
GREEN = hexc('#80ff60')
BLOSSOM = hexc('#ffa8d8')
WARM = hexc('#ffc0a0')
STEEL = hexc('#e8f8ff')
PALE = hexc('#d0b080')
WHITE = hexc('#ffffff')

TRUNK_L, SIEG_L, LINDE_L, EMBER_L = 0.55, 0.5, 0.55, 0.18
HUT_S, MOON_S, GREEN_S, LEAF_S, DOOR_S, BLOSSOM_S = 0.12, 0.2, 0.34, 0.5, 0.55, 1.0
GLINT_IN = 0.5


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Bb2', 'F3', 'D4', 'F4'):                                         # WK09's last chord, still ringing
        add(0.0, 3.0, m, 62, 'pad')
    for t, m, v, d in play('twins_love_b', T_ASK, 0.55, 0, 90):                # "Wälse your father?"
        add(t, d, m, v, 'ask' if m >= note('Eb4') else 'ask_low', 'linde')
    for t, m, v, d in play('siegmund', T_WALSUNG, 0.3, 0, 92):                 # the Wälsungs
        add(t, d, m, v, 'walsung', 'sieg')
    for t, m, v, d in play('volsung_fate', T_FATE, 0.5, 0, 88):
        add(t, d, m, v, 'fate')

    for m in ('Bb1', 'F2', 'Bb2', 'D3', 'F3', 'Bb3', 'D4', 'F4'):               # "Siegmund: so nenn ich dich!"
        add(T_NAME, 2.4, m, 112, 'name')
    add(T_NAME, 1.0, 'Bb1', 118, 'hit')
    for b, d, n in ((0, .5, 'F4'), (.5, .5, 'Bb4'), (1, 1, 'D5'), (2, 1.5, 'Bb4')):
        add(T_NAME + b * 0.6, d * 0.6, n, 106, 'cry', 'linde')

    add(T_SPRING, T_DRAW - T_SPRING, 'D2', 80, 'tension')
    for t, m, v, d in play('nothung', T_NOTHUNG, NBEAT, -12, 110):            # "Nothung! Nothung!"
        add(t, d, m, v, 'nothung', 'sieg')
        add(t, d, m + 12, v - 16, 'nothung_tpt')
    for j in range(24):                                                         # the strings climb
        add(T_NOTHUNG + 6.0 + j * (T_DRAW - T_NOTHUNG - 6.0) / 24, 0.4, note('D3') + j, 70 + j, 'climb')
    for k, th in enumerate(HEAVES):
        add(th, 0.6, note('D2') + 3 * k, 104 + 6 * k, 'heave')
        for m in ('D3', 'A3', 'D4'):
            add(th, 0.7, note(m) + 3 * k, 96 + 6 * k, 'jolt')

    add(T_DRAW, 2.0, 'C2', 127, 'draw')
    for t, m, v, d in play('sword', T_DRAW, 0.45, 0, 124):                     # the Sword, drawn
        add(t, d, m, v, 'sword')
        add(t, d, m - 12, v - 6, 'sword_horn')
    for m in ('C2', 'G2', 'C3', 'E3', 'G3', 'C4', 'E4', 'G4'):
        add(T_DRAW, T_SWORD2 - T_DRAW + 0.5, m, 104, 'blaze')
    for t, m, v, d in play('sword', T_SWORD2, 0.5, 0, 112):                    # held aloft
        add(t, d, m, v, 'sword')
        add(t, d, m - 12, v - 10, 'sword_horn')
    for t, m, v, d in play('nothung', T_SWORD2 + 4.2, 0.45, -12, 100, line='melody'):
        add(t, d, m, v, 'nothung', 'sieg')

    for t, m, v, d in play('twins_love', T_BRIDE, 0.5, -3, 112):              # bride and sister, in G
        if m >= note('C4'):
            add(t, d, m, v, 'bride', 'linde')
            add(t, d, m - 12, v - 6, 'bride_horn', 'sieg')
        else:
            add(t, d, m, v - 4, 'bride_low')
    for t, m, v, d in play('twins_love_b', T_BRIDE + 8.0, 0.42, -3, 108):
        add(t, d, m, v, 'bride' if m >= note('C4') else 'bride_low', 'linde')
    for k in range(int((T_RUN - T_BRIDE) / 0.25)):                              # frenzied: the bass drives
        m = ('G1', 'G2', 'D2', 'G2', 'B1', 'G2', 'D2', 'G2')[k % 8]
        add(T_BRIDE + k * 0.25, 0.2, m, 92 + 10 * (k % 4 == 0), 'drive')

    for k in range(int((T_OUT - T_RUN) / 1.0)):                                 # the run: racing scales
        base = note('G3') + (0, 2, 4, 5)[k % 4]
        for j in range(8):
            add(T_RUN + k * 1.0 + j * 0.0625 * 2, 0.15, base + (0, 2, 4, 5, 7, 9, 11, 12)[j], 92 + 2 * j, 'race')
        add(T_RUN + k * 1.0, 0.9, ('G1', 'D2', 'E2', 'B1')[k % 4], 100, 'drive')
    for t, m, v, d in play('twins_love', T_RUN + 0.5, 0.35, -3, 112, line='melody'):
        add(t, d, m, v, 'bride_horn', 'sieg')
    add(T_OUT - 2.5, CHORDS[0] - T_OUT + 2.5, 'G1', 100, 'roll')
    for k, tc in enumerate(CHORDS):                                             # the curtain
        dur = 0.9 if k < 2 else D - tc - 0.6
        for m in ('G1', 'G2', 'D3', 'G3', 'B3', 'D4', 'G4'):
            add(tc, dur, m, 118 - 2 * k, 'final')
        add(tc, 1.0, 'G1', 124, 'hit')
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
    """Per frame: Siegmund and Sieglinde (path distance); they leave by the door at the free end of Right."""
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    s_t = np.full(F, at(G, 'Porch Front', 0.3))
    l_t = np.full(F, at(G, 'Porch Front', 0.2))
    rs = np.full(F, 2.5)
    s_t[t >= T_SPRING] = pf - 14                                                # at the hilt
    rs[(t >= T_SPRING) & (t < T_SPRING + 1.5)] = 6.0
    l_t[t >= T_SPRING + 1.0] = at(G, 'Porch Front', 0.32)
    s_t[t >= T_DRAW + 0.3] = pf - 40                                            # stepping back with the blade
    l_t[t >= T_BRIDE] = pf - 75
    run = t >= T_RUN
    u = smoothstep(T_RUN, T_OUT, t[run])
    exit_ = G.length + 120
    l_t[run] = pf - 75 + (exit_ + 60 - pf + 75) * u
    s_t[run] = pf - 40 + (exit_ - pf + 40) * smoothstep(T_RUN + 0.6, T_OUT + 0.4, t[run])
    rs[run] = 3.5
    sieg = follow(s_t, rs)
    linde = follow(l_t, np.where(run, 3.5, 2.5))
    return dict(t=t, sieg=sieg, linde=linde)


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


def draw_room(G, R, tt, bed, ember, glint, storm, trunk=TRUNK_L, leaves=LEAF_S, gash=0.0):
    d = G.pd
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 420 - 0.03 * tt))
    fr = light(HUT, bed * (0.85 + 0.15 * roll))
    fr += light(EMBER, ember * R['hearth'] * (0.8 + 0.12 * R['fl'](tt) + 0.06 * R['fast'](tt)))
    dance = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.11 * tt) + 1.5 * np.sin(2 * np.pi * 0.07 * tt))
    fr += light(EMBER, 0.55 * ember * R['cast'] * (0.3 + 0.7 * dance) * (0.85 + 0.15 * R['fl'](tt)))
    fr += light(HOT, 0.8 * ember * R['coals'] * (0.7 + 0.2 * R['fast'](tt)))
    cut = np.exp(-((d - R['pf']) / 8) ** 2)
    fr += light(TRUNK, trunk * R['trunk'] * (1 - gash * cut))
    fr += light(PALE, 0.42 * gash * (np.exp(-((d - R['pf'] - 11) / 5) ** 2) + np.exp(-((d - R['pf'] + 11) / 5) ** 2)))
    fr += light(LEAF, leaves * R['canopy'] * (0.85 + 0.15 * R['leaf'](tt)))
    fr += light(HILT, glint * np.exp(-((d - R['pf']) / 9) ** 2))
    fr += light(STORM, storm * R['storm'] * (0.85 + 0.15 * R['gust'](tt)))
    return fr


def draw_spring(G, tt, level, grass):
    """The moonlit spring night as WK09 leaves it: moon over rippling green, the open door bright."""
    d, L = G.pd, G.length
    wind = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 + 0.09 * tt))
    wind2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 110 + 0.21 * tt) + 2)
    fr = light(MOON, MOON_S * level * (0.85 + 0.15 * wind2))
    fr += light(GREEN, GREEN_S * level * (0.55 + 0.45 * wind * (0.7 + 0.3 * wind2)) * (0.9 + 0.1 * grass(tt)))
    fr += light(MOON, DOOR_S * np.exp(-((L - d) / 200) ** 2))
    return fr


def blossoms(G):
    """Petals on the breeze, on the shared clock (the same petals as WK09)."""
    rng = np.random.default_rng(909)
    n = 2400
    birth = np.sort(rng.uniform(80 * 8, 80 * 10 + 5, n))
    start = G.length - rng.exponential(700, n)
    speed = rng.uniform(40, 140, n)
    life = rng.uniform(3.0, 7.0, n)
    width = rng.uniform(7, 14, n)
    return birth, start, speed, life, width


def draw_blossoms(G, B, tt):
    birth, start, speed, life, width = B
    lo = int(np.searchsorted(birth, tt - 7.0))
    hi = int(np.searchsorted(birth, tt))
    if hi <= lo:
        return np.zeros(G.N)
    age = tt - birth[lo:hi]
    ok = age < life[lo:hi]
    a, l_ = age[ok], life[lo:hi][ok]
    q = start[lo:hi][ok] - speed[lo:hi][ok] * a + 20 * np.sin(2 * np.pi * a / 2.3)
    env = np.sin(np.pi * a / l_) ** 2
    g = np.exp(-((G.pd[:, None] - q[None, :]) / width[lo:hi][ok][None, :]) ** 2) * env[None, :]
    return g.max(axis=1)


def render(G, seed=10):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    R = room(G)
    pf, L = R['pf'], G.length
    C = choreography(G)
    N = compose()
    B = blossoms(G)
    rng_g = np.random.default_rng(9)                                            # WK09's flickers, in its order
    tw = Flicker(rng_g, G.N, 2.0, 6.0)
    grass = Flicker(rng_g, G.N, 0.1, 0.4)
    sung = np.array([e[0] for e in N if e[5] == 'sieg' and e[1] >= 0.2])
    linde_n = np.array([e[0] for e in N if e[5] == 'linde' and e[1] >= 0.2])
    nth = np.array([e[0] for e in N if e[4] == 'nothung' and e[0] < T_DRAW])
    swd = np.array([e[0] for e in N if e[4] == 'sword'])

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        sp, lp = C['sieg'][f], C['linde'][f]
        focus = smoothstep(T_NOTHUNG, T_DRAW - 0.5, t) * (1 - smoothstep(T_DRAW, T_DRAW + 1.5, t))
        frenzy = smoothstep(T_BRIDE - 0.5, T_BRIDE + 1.5, t) * (1 - smoothstep(T_OUT, T_OUT + 2, t))
        drawn = smoothstep(T_DRAW - 0.02, T_DRAW + 0.02, t)
        k = int(np.searchsorted(nth, t, side='right')) - 1
        nf = np.exp(-(t - nth[k]) / 0.3) if k >= 0 and t - nth[k] < 1.5 else 0.0
        glint = (GLINT_IN + 0.3 * smoothstep(T_SPRING, T_DRAW, t) + 0.6 * nf) * (1 - drawn)
        level = 1 - 0.5 * focus
        fr = draw_room(G, R, tt, HUT_S, EMBER_L, glint, 0.0, gash=drawn)
        fr += draw_spring(G, tt, level, grass)
        dens = BLOSSOM_S * (1 - 0.6 * focus) * (1 + 1.0 * frenzy)
        fr += light(BLOSSOM, 0.45 * dens * draw_blossoms(G, B, tt) * (0.8 + 0.2 * tw(tt)))

        # recognition: two amber waves out from her; the naming: a ring of blue and amber over the whole house
        for t0 in (T_WALSUNG, T_FATE):
            if t0 <= t < t0 + 3.5:
                a = t - t0
                r = 30 + 700 * a ** 0.7
                dist = np.abs(d - lp)
                fr += light(AMBER, (1 - a / 3.5) * (0.7 * np.exp(-((dist - r) / 120) ** 2) +
                                                    0.25 * smoothstep(r + 60, r - 60, dist)))
        if T_NAME <= t < T_NAME + 3.5:
            a = t - T_NAME
            r = 30 + 1500 * a ** 0.6
            ring = np.exp(-((np.abs(d - sp) - r) / 110) ** 2) * (1 - a / 3.5)
            fill = smoothstep(r + 80, r - 80, np.abs(d - sp)) * (1 - a / 3.5)
            fr += light(BLUE, 0.9 * ring + 0.4 * fill) + light(AMBER, 0.6 * np.exp(-((np.abs(d - lp) - r * 0.92) / 60) ** 2) * (1 - a / 3.5))
            fr += light(WHITE, 0.5 * np.exp(-a / 0.25) * np.exp(-((d - sp) / 120) ** 2))

        # the heaves: white-gold jolts up out of the trunk, each wider
        for j, th in enumerate(HEAVES):
            if th <= t < th + 1.5:
                a = t - th
                fr += light(HILT, (0.6 + 0.15 * j) * np.exp(-a / 0.35) * np.exp(-((d - pf) / (70 + 70 * j)) ** 2))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - pf) / (20 + 15 * j)) ** 2))
        if nf > 0:                                                              # each "Nothung!" flares the porch
            fr += light(HILT, 0.45 * nf * np.exp(-((d - pf) / 260) ** 2))
        if focus > 0:                                                           # the strain round the hilt
            fr += light(HILT, focus * 0.35 * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)) * np.exp(-((d - pf) / 45) ** 2))

        # the draw: white steel bursts out of the trunk to both ends; the whole house white for an instant
        if T_DRAW <= t < T_DRAW + 4.0:
            a = t - T_DRAW
            r = 1700 * a ** 0.8
            front = np.exp(-((np.abs(d - pf) - r) / 110) ** 2)
            inside = smoothstep(r + 40, r - 40, np.abs(d - pf))
            fr += light(WHITE, 1.0 * np.exp(-a / 0.22) * np.ones(G.N))
            fr += light(STEEL, (1.0 * front + 0.8 * inside * np.exp(-a / 2.0)) * (1 - a / 4.0))
            shiver = 0.5 + 0.5 * np.sin(2 * np.pi * (np.abs(d - pf) / 80 - 4 * a))
            fr += light(BLUE, 0.6 * inside * shiver * np.exp(-a / 1.8))

        # Nothung, held up: a white steel blade beside him, flaring with every note of the Sword
        if drawn > 0 and t < T_OUT + 1.0:
            j = int(np.searchsorted(swd, t, side='right')) - 1
            hit = np.exp(-(t - swd[j]) / 0.3) if j >= 0 and t - swd[j] < 1.5 else 0.0
            tip = sp + 130
            blade = smoothstep(sp + 10, sp + 25, d) * smoothstep(tip + 10, tip - 10, d)
            fr += light(STEEL, (0.65 + 0.35 * hit) * blade)
            fr += light(WHITE, 0.4 * hit * np.exp(-((d - tip) / 25) ** 2) + 0.2 * hit * blade)

        # bride and sister: blue, amber and steel bands chase each other round the house
        if frenzy > 0:
            b1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 200 - 1.4 * t))
            b2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 + 1.1 * t) + 1)
            b3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 90 - 2.5 * t) + 2)
            fr += light(BLUE, frenzy * 0.62 * b1 ** 2)
            fr += light(AMBER, frenzy * 0.58 * b2 ** 2)
            fr += light(STEEL, frenzy * 0.4 * b3 ** 6)

        # the act's last chords: three flashes of the whole house
        for j, tc in enumerate(CHORDS):
            if tc <= t < tc + 2.5:
                a = t - tc
                fr += light(WARM, (0.9 - 0.1 * j) * np.exp(-a / (0.25 + 0.3 * (j == 2))) * np.ones(G.N))
                fr += light(WHITE, 0.5 * np.exp(-a / 0.12) * np.ones(G.N))

        # the lovers, and the trails they leave as they run
        i = int(np.searchsorted(sung, t, side='right')) - 1
        sf = np.exp(-(t - sung[i]) / 0.3) if i >= 0 and t - sung[i] < 1.2 else 0.0
        j = int(np.searchsorted(linde_n, t, side='right')) - 1
        lf = np.exp(-(t - linde_n[j]) / 0.3) if j >= 0 and t - linde_n[j] < 1.2 else 0.0
        named = smoothstep(T_NAME, T_NAME + 0.3, t)
        for p, col, base, fl, key in ((sp, BLUE, SIEG_L, sf, 'sieg'), (lp, AMBER, LINDE_L, lf, 'linde')):
            b = base * (1.4 + 0.3 * fl + 0.3 * named + 0.2 * frenzy) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
            fr += light(col, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
            if t >= T_RUN:
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 24, 2)):
                    q = C[key][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 30) ** 2) * (1 - n_ / 11.5))
                fr += light(col, 0.6 * trail)
        warm = 1 - smoothstep(T_NAME - 1, T_NAME + 1, t)
        a, b_ = sorted((sp, lp))
        between = smoothstep(a - 5, a + 15, d) * smoothstep(b_ + 5, b_ - 15, d)
        fr += light(WARM, warm * (0.45 * between + 0.3 * np.exp(-((d - (sp + lp) / 2) / 60) ** 2)))
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
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.19, 0.32), ('low', 0.2, 0.2), ('brass', 0.2, 0.3), ('winds', 0.2, 0.3),
                            ('perc', 0.2, 0.3), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*_v5_*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')

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

    def chord_inst(m):
        if m < note('C2'):
            return 'low', tuba, m + 12
        if m < note('C3'):
            return 'brass', tbn, m
        if m < note('C4'):
            return 'brass', horn, m
        return 'brass', tpt, m

    for t, d, m, v, part, who in compose():
        if part == 'pad':
            hold('strings', vn if m >= note('D4') else va, m, t, t + d, v, -0.3 + 0.2 * (m % 4), rise=0.05, fall=2.0,
                 gain=0.45)
        elif part == 'ask':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, pt('linde', t))
        elif part == 'ask_low':
            M.add('strings', (vc if m < note('C3') else va).play(m, v - 12, dur=d * 1.02, release=0.4), t, 0.6, pf)
        elif part == 'walsung':
            pa = pt('sieg', t)
            if m >= note('D3') and d > 0.3:
                hold('brass', horn, m, t, t + d, v, pa, rise=0.2, fall=0.8, gain=0.5)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.7, pa)
                M.add('low', cb.play(m + 12, v - 10, dur=d * 1.05, release=0.4), t, 0.45, pa)
        elif part == 'fate':
            s = tuba if m < note('G2') else tbn if m < note('G3') else horn
            M.add('brass', s.play(m + (12 if s is tuba and m < note('C2') else 0), v, dur=d * 1.02, release=0.5), t,
                  0.42, pf)
        elif part == 'name':
            bus, s, mm = chord_inst(m)
            hold(bus, s, mm, t, t + d, v, -0.4 + 0.1 * (m % 9), rise=0.05, fall=1.5, gain=0.38)
            hold('strings', vtrem if m >= note('F3') else vatrem, m, t, t + d, v, 0.0, rise=0.05, fall=1.5, gain=0.3)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-3), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 0.8, pf)
        elif part == 'cry':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pt('linde', t))
            M.add('strings', vn.play(m, v - 6, dur=d * 1.05, release=0.3), t, 0.8, pt('linde', t))
        elif part == 'tension':
            hold('strings', vatrem, m + 12, t, t + d, v, pf, rise=d * 0.9, fall=0.3, gain=0.6)
            hold('low', cb, m + 12, t, t + d, v, pf, rise=2.0, fall=0.3, gain=0.6)
        elif part == 'nothung':
            pa = pt('sieg', t)
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.7, pa)
            M.add('strings', vc.play(m - 12, v - 8, dur=d * 1.05, release=0.4), t, 0.55, pa)
        elif part == 'nothung_tpt':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.4), t, 0.6, pf)
        elif part == 'climb':
            M.add('strings', vtrem.play(m + 12, v, dur=d * 1.3, release=0.1), t, 0.5, pf)
        elif part == 'heave':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, pf)
            M.add('low', tuba.play(m + 12, v, dur=d, release=0.2), t, 0.8, pf)
            M.add('fx', whoosh(0.6, 400, 3000, 0.5, seed=int(t * 10)), t - 0.3, 0.6, pf)
        elif part == 'jolt':
            M.add('brass', tbn.play(m, v, dur=d, release=0.2), t, 0.6, pf)
        elif part == 'draw':
            M.add('perc', timp.play(v, pitch=-5), t, 1.4, pf)
            M.add('perc', crash.play(v), t, 1.3, -0.4)
            M.add('perc', crash.play(v), t + 0.02, 1.3, 0.4)
            M.add('perc', gong.play(v), t, 0.8, pf)
            M.add('fx', whoosh(1.4, 600, 6000, 0.9, seed=101), t - 0.2, 1.0, pf)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.5), t, 1.4, pt('sieg', t))
        elif part == 'sword_horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 0.8, pt('sieg', t))
        elif part == 'blaze':
            bus, s, mm = chord_inst(m)
            hold(bus, s, mm, t, t + d, v - 14, -0.5 + 0.12 * (m % 9), rise=0.05, fall=1.5, gain=0.4)
            hold('strings', vtrem if m >= note('C3') else vatrem, m + (12 if m < note('C3') else 0), t, t + d, v,
                 -0.4 + 0.1 * (m % 9), rise=0.05, fall=1.5, gain=0.45)
        elif part == 'bride':
            pa = pt('linde', t)
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, pa)
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pa)
        elif part == 'bride_horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pt('sieg', t))
        elif part == 'bride_low':
            s = vc if m < note('C3') or m >= note('F3') else va
            M.add('strings', s.play(m, v - 6, dur=d * 1.02, release=0.3), t, 0.7, -0.2 + 0.4 * (m % 2))
            if d >= 2:
                M.add('brass', tbn.play(m if m >= note('E2') else m + 12, v - 16, dur=d, release=0.4), t, 0.5, 0.0)
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.8, -0.2)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, 0.2)
        elif part == 'race':
            pa = pt('linde', t)
            M.add('strings', vns.play(m, v), t, 0.7, pa)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.2), t, 0.8, 0.0)
        elif part == 'final':
            bus, s, mm = chord_inst(m)
            hold(bus, s, mm, t, t + d, v, -0.5 + 0.15 * (m % 7), rise=0.03, fall=0.5 if d < 1 else 2.0, gain=0.5)
            hold('strings', vtrem if m >= note('G3') else vatrem, m + (12 if m < note('C3') else 0), t, t + d, v,
                 -0.4 + 0.12 * (m % 7), rise=0.03, fall=0.5 if d < 1 else 2.0, gain=0.45)
