"""Nothung!: the moonlit spring night, the lovers beside the ash tree on Porch Front. Sieglinde knows him at last:
"Siegmund: so nenn' ich dich!" Her amber flares and sends a wave of recognition over the house, and the orchestra
blazes up in B major: his blue blazes, a ring of blue and amber runs out over the whole roof and sparks of both fly
on every note of the strings' arpeggios. "Siegmund heiss' ich, und Siegmund bin ich!"

He springs to the trunk and lays his hand on the hilt: "ich fass' es nun!", and the hilt jolts white-gold up out of
the trunk while the spring dims around the tree and the strings tremble. "Nothung! Nothung!": each phrase flares the
hilt and the porch while the strings climb beneath; then three heaves on "Heraus aus der Scheide zu mir!", three
jolts of white-gold, each wider than the last, and the sword comes out. The Sword blazes in C major on the trumpets
and a flash of white steel bursts out of the trunk and races to both ends of the house, the whole roof white for an
instant, then steel-blue light shivering everywhere. He holds Nothung up: a blade of white steel beside his blue,
flaring with every note of the Sword. The tree is left with a gash, dark with pale edges where the hilt was.

Then the act's last pages break loose, and the house goes wild: blue and amber and steel bands chasing each other
round the roof while the blossoms pour down. They run: along Porch Right and Right, trailing light, and out through
the open door at the free end of Right, into the spring night, with racing strings and blaring brass. The act ends
on two huge chords, two flashes of the whole house, and the hut is left empty in the moonlight: the gashed tree,
the open door, the embers.

The music is Wagner's own: Act I, bars 1375-1383, 1392-1399, 1417-1443 and 1504 to the end, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The naming's
arpeggios are violins, flutes and harp over horns and trombones; "Nothung!" is horns and a trumpet over climbing
violas and cellos; the Sword is the trumpets and trombones under the violins and harp; the ending is the full
orchestra; the rest is the reduction orchestrated by hand and register. The stage adds its sounds: the spring breeze
through the open door, sparks crackling with the blaze of the naming, steel grinding in the wood as he grips the hilt
and at every heave, the sword wrenched out with a shriek of steel racing to both ends of the house and a great blow,
their running feet and the rush of the night as they flee, and a blow on each of the last chords. The effects keep
back through the naming, lead from the grip to the drawing of the sword, ease off under the Sword's melody, and lead
again for the flight through the door before settling under the last chords.

compose() tags every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK10'
TITLE = 'Nothung!'
KIND = 'show'
DESCRIPTION = ('Sieglinde knows him at last and names him Siegmund. He takes hold of the sword in the tree, '
               'names it Nothung, and pulls it out in a blaze of white steel. Then the two of them run out into '
               'the spring night together.')
VOICEOVER = ('She knows who he is now, and he knows what is waiting for him in that tree. '
             'This is the moment the whole act has been building to.')

EX = excerpt(__file__)                      # Act I, bars 1375-1383, 1392-1399, 1417-1443, 1504-1524, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
K = 9                                       # this scene's place in the shared clock (t + 80 * K)
T_NAME = BAR[1376]                          # "Siegmund: so nenn' ich dich!"
T_BLAZE = BAR[1378]                         # the orchestra blazes up in B major
T_REPLY = BAR[1380]                         # "Siegmund heiss' ich"
T_SPRING = BAR[1392]                        # he springs to the tree
T_GRASP = BAR[1395]                         # the chord after "ich fass' es nun!"
T_NOTHUNG = BAR[1417]                       # "Nothung! Nothung!"
HEAVES = [T_GRASP, BAR[1396], BAR[1433], BAR[1435], BAR[1436]]   # jolts of the hilt, each wider
T_DRAW = BAR[1437]                          # the sword comes out
T_BRIDE = BAR[1504]                         # the act's last pages: the house goes wild
T_RUN = BAR[1510]                           # out into the night
T_OUT = BAR[1518]
CHORDS = sorted({n[0] for n in EX['notes'] if n[0] >= BAR[1521] - 0.01})   # the act's last two chords
D = EX['seconds'] + 2.0                     # the last chord rings on past the recording's end

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). 'name' and 'name_low' the
    naming; 'tension' and 'grip' at the hilt; 'nothung' the right hand's long notes as he names the sword, 'climb'
    the left hand under them, 'heave' the left hand's tremolo as he pulls; 'sword' the left hand once it is out,
    'blaze' the right hand over it; 'race' and 'drive' the ending, 'final' its last chords."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_SPRING:
            part = 'name' if h == 0 else 'name_low'
        elif t < T_NOTHUNG:
            part = 'tension' if h == 0 else 'grip'
        elif t < HEAVES[2]:
            part = ('nothung' if d >= 0.4 else 'note') if h == 0 else 'climb'
        elif t < T_DRAW:
            part = 'note' if h == 0 else 'heave'
        elif t < T_BRIDE:
            part = 'blaze' if h == 0 else 'sword' if d >= 0.4 else 'note'
        elif t >= CHORDS[0] - 0.05:
            part = 'final'
        else:
            part = 'race' if h == 0 else 'drive'
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
    sung = np.array([e[0] for e in N if (e[4] == 'nothung') or (e[4] == 'name' and e[0] >= T_REPLY and e[1] >= 0.3)])
    linde_n = np.array([T_NAME] + [e[0] for e in N if e[4] == 'name' and e[0] < T_BLAZE and e[1] >= 0.3])
    nth = np.array([e[0] for e in N if e[4] == 'nothung'])
    swd = np.array([e[0] for e in N if e[4] == 'sword'])
    spark = [e for e in N if e[4] == 'name' and T_BLAZE <= e[0] < T_SPRING]
    spark_t = np.array([e[0] for e in spark])
    spark_p = np.random.default_rng(10).normal(0, 1, len(spark))
    climb = [e for e in N if e[4] in ('climb', 'heave', 'grip') and e[1] < 0.4]
    climb_t = np.array([e[0] for e in climb])
    climb_s = np.where(np.arange(len(climb)) % 2, 1.0, -1.0)     # alternate sides of the trunk

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        sp, lp = C['sieg'][f], C['linde'][f]
        focus = (0.6 * smoothstep(T_GRASP - 0.5, T_GRASP + 1, t) + 0.4 * smoothstep(T_NOTHUNG, T_DRAW - 0.5, t)) * \
            (1 - smoothstep(T_DRAW, T_DRAW + 1.5, t))
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
        for t0 in (0.0, T_NAME):
            if t0 <= t < t0 + 3.5:
                a = t - t0
                r = 30 + 700 * a ** 0.7
                dist = np.abs(d - lp)
                fr += light(AMBER, (1 - a / 3.5) * (0.7 * np.exp(-((dist - r) / 120) ** 2) +
                                                    0.25 * smoothstep(r + 60, r - 60, dist)))
        if T_BLAZE <= t < T_BLAZE + 3.5:
            a = t - T_BLAZE
            r = 30 + 1500 * a ** 0.6
            ring = np.exp(-((np.abs(d - sp) - r) / 110) ** 2) * (1 - a / 3.5)
            fill = smoothstep(r + 80, r - 80, np.abs(d - sp)) * (1 - a / 3.5)
            fr += light(BLUE, 0.9 * ring + 0.4 * fill) + light(AMBER, 0.6 * np.exp(-((np.abs(d - lp) - r * 0.92) / 60) ** 2) * (1 - a / 3.5))
            fr += light(WHITE, 0.5 * np.exp(-a / 0.25) * np.exp(-((d - sp) / 120) ** 2))

        ks = int(np.searchsorted(spark_t, t, side='right'))                     # the arpeggios: sparks of both
        for j in range(max(0, ks - 8), ks):
            a = t - spark_t[j]
            if a < 0.45:
                c = (sp + lp) / 2 + 420 * spark_p[j]
                fr += light(BLUE if j % 2 else AMBER, 0.8 * np.exp(-a / 0.14) * np.exp(-((d - c) / 16) ** 2))

        kc = int(np.searchsorted(climb_t, t, side='right'))                     # the strings climb: sparks fly
        for j in range(max(0, kc - 6), kc):                                     # out of the trunk, higher notes
            a = t - climb_t[j]                                                  # farther
            if a < 0.35:
                q = pf + climb_s[j] * (40 + 14 * (climb[j][2] - 40))
                fr += light(HILT, 0.95 * min(1.0, focus + 0.3) * np.exp(-a / 0.14) * np.exp(-((d - q) / 14) ** 2))

        # the heaves: white-gold jolts up out of the trunk, each wider
        for j, th in enumerate(HEAVES):
            if th <= t < th + 1.5:
                a = t - th
                fr += light(HILT, (0.6 + 0.1 * j) * np.exp(-a / 0.35) * np.exp(-((d - pf) / (70 + 55 * j)) ** 2))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - pf) / (20 + 12 * j)) ** 2))
        if nf > 0:                                                              # each "Nothung!" flares the porch
            fr += light(HILT, 0.6 * nf * np.exp(-((d - pf) / 300) ** 2))
            fr += light(BLUE, 0.4 * nf * np.exp(-((np.abs(d - pf) - 120 - 900 * (t - nth[k])) / 80) ** 2))
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
                fr += light(WARM, (0.9 - 0.1 * j) * np.exp(-a / (0.25 + 0.3 * (j == len(CHORDS) - 1))) * np.ones(G.N))
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
    """Wagner's notes from the piano reduction: the naming on violins, flutes and harp over horns and trombones,
    "Nothung!" on horns and a trumpet, the Sword on trumpets and trombones, the ending on the full orchestra."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=2.0)

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    def size(t):
        return 0.5 if T_SPRING <= t < HEAVES[2] else 1.0

    for t, d, m, v, part, h in compose():
        if part == 'name':
            o.play('violins', m, t, d, v - 6, None, 0.45)
            if m >= 74:
                o.play('flutes', m, t, d, v - 14, None, 0.35)
            if d >= 0.3 or m in (71, 74, 83, 86):
                o.play('harp', m - 12, t, d, v - 10, 0.3, 0.3)
        elif part == 'name_low':
            o.play('horns', m if m >= 50 else m + 12, t, d, v, pt('sieg', t), 0.7)
            o.play('trombones', m, t, d, v - 6, pt('sieg', t), 0.5)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, None, 0.4)
        elif part == 'tension':
            o.play('violins trem', m, t, max(d, 0.4), v, pf, 0.4)
        elif part == 'grip' and d >= 1.0:
            o.play('tuba', m + 12, t, d, v, pf, 0.7)
            o.play('basses', m + 12, t, d, v, pf, 0.5)
            o.play('trombones', m + 24, t, d, v - 6, pf, 0.5)
        elif part == 'nothung':
            o.play('horns', m - 12, t, d, v + 6, pt('sieg', t), 0.75)
            o.play('trumpets', m, t, d, v - 4, pf, 0.5)
            o.play('cellos', m - 24, t, d, v - 8, pt('sieg', t), 0.4)
        elif part == 'heave':
            o.play('cellos trem', m, t, max(d, 0.4), v + 10, pf, 0.4)
            o.play('basses', m, t, d, v, pf, 0.35)
        elif part == 'sword':
            o.play('trumpets', m if m >= 55 else m + 12, t, d, v + 10, pt('sieg', t), 0.8)
            o.play('trombones', m if m < 60 else m - 12, t, d, v, pt('sieg', t), 0.55)
        elif part == 'blaze':
            o.play('violins', m, t, 0.1, v - 8, None, 0.4)
            if m in (72, 76, 79, 84):
                o.play('harp', m - 12, t, d, v - 10, 0.3, 0.3)
        elif part == 'final':
            o.tutti([(t, d, m, v, h)], size=size)
            o.play('trombones', m if m < 60 else m - 12, t, d, v, 0.0, 0.5)
            o.play('trumpets', m if m >= 60 else m + 12, t, d, v - 6, 0.0, 0.4)
        else:
            o.tutti([(t, d, m, v, h)], size=size, pan=lambda t, m: pt('sieg', t) if t >= T_RUN else None)
    o.hit('crash', T_BLAZE, 105, gain=0.45)
    o.hit('timpani', T_BLAZE, 105, pitch=-3, gain=0.5)
    o.hit('timpani', T_GRASP, 115, pitch=-6, gain=0.7, pan=pf)
    o.hit('gong', T_GRASP, 90, gain=0.35, pan=pf)
    for th in HEAVES[1:]:
        o.hit('timpani', th, 100, pitch=-4, gain=0.5, pan=pf)
    o.hit('timpani roll', HEAVES[2], 100, gain=0.4, pan=pf)
    o.hit('crash', T_DRAW, 120, gain=0.6, pan=-0.4)
    o.hit('crash', T_DRAW + 0.02, 120, gain=0.6, pan=0.4)
    o.hit('gong', T_DRAW, 110, gain=0.45, pan=pf)
    o.hit('timpani', T_DRAW, 120, pitch=-5, gain=0.7, pan=pf)
    o.hit('crash', T_BRIDE, 110, gain=0.45)
    for tc in CHORDS:
        o.hit('timpani', tc, 120, pitch=-5, gain=0.7)
        o.hit('crash', tc, 115, gain=0.5)
        o.boom(tc, 0.0, gain=0.8)
    # the stage: the breeze, the sparks, the grip and the heaves, the drawing, the flight
    from pixelhome.audio import whoosh
    pdoor = pan_at(G.length)
    o.wind(0.0, D, lambda tt: 0.4 + 0.3 * smoothstep(T_RUN, T_OUT, tt), pan=pdoor, seed=101)
    o.fire(0.0, D, 0.15, pan=pan_at(at(G, 'Left', 0.6)), crackle=4, seed=102)
    o.fire(T_BLAZE, T_REPLY + 1.0, 0.1, pan=0.0, crackle=50, seed=103)
    o.clash(T_GRASP, pf, 110, gain=0.7)
    o.hit('scrape', T_GRASP, 105, gain=0.5, pan=pf, fx=True)
    for k, th in enumerate(HEAVES[1:]):
        o.hit('gong scrape', th, 80 + 12 * k, gain=0.3 + 0.1 * k, pan=pf, fx=True)
        o.hit('scrape', th, 90 + 8 * k, gain=0.35 + 0.08 * k, pan=pf, fx=True)
        if k >= 1:
            o.hit('bass drum', th, 105 + 7 * k, gain=0.4 + 0.1 * k, pan=pf, fx=True)
    o.clash(T_DRAW, pf, 127, gain=1.2)
    o.boom(T_DRAW, pf, gain=1.0)
    o.hit('scrape', T_DRAW, 120, gain=0.6, pan=pf, fx=True)
    for k, pp in enumerate((-0.75, 0.75)):                                      # steel racing to both ends
        M.add('fx', whoosh(1.4, 900, 9000, 0.8, seed=104 + k), T_DRAW, 0.8, pp)
    ts, k = T_RUN, 0
    while ts < T_OUT + 0.4:                                                     # running feet
        o.M.add('fx', o.hits['hoof soft'].play(90 if k % 2 else 80), ts, 0.2, pt('sieg', ts))
        ts, k = ts + 0.22, k + 1
    M.add('fx', whoosh(T_OUT - T_RUN + 1.0, 300, 2800, 0.7, seed=106), T_RUN, 0.7, pdoor)
    o.effects([(0, -8), (T_BLAZE - 0.3, -8), (T_BLAZE, -4), (T_REPLY + 1.0, -8), (T_SPRING - 0.5, -8),
               (T_GRASP, 0), (T_DRAW, 2), (T_DRAW + 2.5, 1), (T_DRAW + 4.0, -6), (T_BRIDE, -4), (T_RUN - 0.5, -4),
               (T_RUN, 1), (T_OUT + 1.0, 0), (CHORDS[0] - 0.5, -5), (D, -5)])
