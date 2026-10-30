"""Winterstürme: the wind presses at the door, and the great door of the hut (the free end of Right) bursts open by
itself on two huge arpeggios that sweep up and down the orchestra, a spark racing along the roof with every note
of them. The storm's grey is simply gone, and moonlight pours in: a cool white front of it runs from the door
across the whole house, and behind it everything turns to a spring night, moon-white over fresh green that
ripples like grass in the wind, the ash tree's leaves coming out on the porch, and blossoms drifting in on the
breeze, pale pink sparks floating along the roof toward the hearth. "Ha, wer ging?" "Keiner ging; doch Einer kam:
siehe, der Lenz lacht in den Saal!"

Then spring itself breaks over the house in the orchestra, B flat major in full, the violins' arpeggios high over
a bass striding down: wave after wave of green and moonlight runs in from the door, the blossoms fall thick, and
the two lights, Siegmund's blue and Sieglinde's amber, walk together along Left and up Porch Left to the ash tree,
a warm glow growing between them and rippling out over the house, her amber flaring on every phrase. And he sings
his love song, "Winterstürme wichen dem Wonnemond", over the lilting harp and strings: every phrase sends another
wave of green and blossom in from the door, and his blue brightens on every note of it. It settles into the
moonlit spring night with the lovers beside the tree, its hidden hilt glowing.

The music is Wagner's own: Act I, bars 1088-1120, as Solti's 1958 Vienna Philharmonic recording takes them, from
the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The door's arpeggios are harp and violins over
tremolo cellos; the lilt under "Keiner ging" and the song is harp; the spring is the full orchestra; the rest is
the reduction orchestrated by hand and register. The reduction leaves out the voices, so the song's first two
lines, Siegmund's melody (Donington 86, pixelhome/leitmotifs.py), are laid on the recording's bars on horn and
cellos. The stage adds its sounds: the door bursting open with a great blow and a rush of wind, the moonlight
sweeping across the house from the door, a spring breeze that swells with every wave of green, and the hearth's
embers crackling. The effects lead for the door and the moonlight flooding in, ease back under "Keiner ging",
breathe with the waves of spring, and back well off for the love song so his melody is clear.

compose() tags every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK09'
TITLE = 'Winterstürme'
KIND = 'show'
DESCRIPTION = ('The door of the hut swings open by itself and moonlight and spring pour in across the whole house. '
               'Siegmund sings his love song, Sieglinde answers, and the two of them find each other at last.')
VOICEOVER = ('A gust of wind, and the door swings open. Outside, winter is over. '
             'And inside, two people are falling in love.')

EX = excerpt(__file__)                      # Act I, bars 1088-1120, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
K = 8                                       # this scene's place in the shared clock (t + 80 * K)
T_DOOR = 0.0                                # the door bursts open
T_FLOOD = 0.8                               # moonlight runs in from the door
FLOOD_S = 9.0
T_CALM = BAR[1091]                          # "Keiner ging; doch Einer kam"
T_SAAL = BAR[1094]                          # "Siehe, der Lenz lacht in den Saal!"
T_SPRING = BAR[1099]                        # spring breaks over the house in the orchestra
T_SONG = BAR[1107]                          # "Winterstürme wichen dem Wonnemond"
VERSES = [x[0] for x in EX['singing'] if x[0] >= T_SONG - 0.1]     # every sung line of it
BLISS = [BAR[b] for b in (1099, 1101, 1103, 1105)]                 # the glow between them swells, every two bars
T_SETTLE = EX['seconds'] - 6.0
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
MOON = hexc('#c8dcff')
GREEN = hexc('#80ff60')
BLOSSOM = hexc('#ffa8d8')
WARM = hexc('#ffc0a0')
TOGETHER = hexc('#a0a8ff')
WHITE = hexc('#ffffff')

BED, TRUNK_L, LEAF_L, STORM_L, SIEG_L, LINDE_L = 0.26, 0.55, 0.3, 0.32, 0.5, 0.55
EMBER_L = 0.18
GLINT_IN, GLINT_OUT = 0.42, 0.5
# the spring night, as WK10 picks it up
HUT_S, MOON_S, GREEN_S, LEAF_S, DOOR_S, BLOSSOM_S = 0.12, 0.2, 0.34, 0.5, 0.55, 1.0


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def measure_time(m):
    """Seconds into the excerpt at fractional measure m."""
    bars = np.array(EX['bars'], float)
    return float(np.interp(m, bars[:, 0], bars[:, 1]))


def compose():
    """Every note, tagged: (time, seconds, midi, velocity, part, hand). The door's arpeggios are 'burst' (right
    hand) and 'burst_low'; then 'call' and 'lilt'; the spring 'surge' and 'surge_low'; under the song 'acc' and
    'acc_low'. 'song' (hand 2) is Siegmund's melody for the song's first two lines, three beats to a bar from 1107."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_CALM:
            part = 'burst' if h == 0 else 'burst_low'
        elif t < T_SPRING:
            part = 'call' if h == 0 else 'lilt'
        elif t < T_SONG:
            part = 'surge' if h == 0 else 'surge_low'
        else:
            part = 'acc' if h == 0 else 'acc_low'
        N.append((t, d, m, v, part, h))
    for b, m, v, d in play('spring_song', 0.0, 1.0, 0, 96):
        t0, t1 = measure_time(1107 + b / 3), measure_time(1107 + (b + d) / 3)
        N.append((t0, t1 - t0, m, v, 'song', 2))
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
    """Per frame: Siegmund and Sieglinde (path distance). They walk together to the tree."""
    F = nframes(D)
    t = np.arange(F) * DT
    s0, l0 = at(G, 'Left', 0.48), at(G, 'Left', 0.4)
    s1, l1 = at(G, 'Porch Front', 0.3), at(G, 'Porch Front', 0.2)
    u = smoothstep(T_SPRING, BAR[1106], t)
    s_t = s0 + (s1 - s0) * u
    l_t = l0 + (l1 - l0) * u
    s_t = s_t + 14 * smoothstep(T_CALM, T_CALM + 2, t) * (1 - u)               # he turns to the open door
    sieg = follow(s_t, np.full(F, 2.5))
    linde = follow(l_t, np.full(F, 2.5))
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


def blossoms(G):
    """Petals on the breeze, on the shared clock so they carry across the cut into WK10: (birth, start, speed,
    life, width) for each, drifting from the door end toward the hearth."""
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


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    R = room(G)
    pf, L = R['pf'], G.length
    C = choreography(G)
    N = compose()
    B = blossoms(G)
    song = np.array([e[0] for e in N if e[4] == 'song' or (e[4] in ('call', 'acc') and e[1] >= 0.4)])
    linde_n = np.array([0.47] + [e[0] for e in N if e[4] == 'surge' and e[1] >= 0.25])
    verses = [T_SAAL] + [BAR[b] for b in range(1099, 1106, 2)] + VERSES
    bliss = BLISS
    burst = [(e[0], e[2]) for e in N if e[4] == 'burst']
    burst_t = np.array([b[0] for b in burst])
    tw = Flicker(rng, G.N, 2.0, 6.0)
    grass = Flicker(rng, G.N, 0.1, 0.4)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        # the moonlight's front, running in from the door; everything behind it is spring
        front = L - (L + 300) * smoothstep(T_FLOOD, T_FLOOD + FLOOD_S, t) ** 0.8
        spring = smoothstep(front - 150, front + 150, d)
        sp_all = smoothstep(T_FLOOD, T_FLOOD + FLOOD_S, t)
        opened = smoothstep(T_DOOR, T_DOOR + 1.2, t)
        hut = BED + (HUT_S - BED) * spring
        glint = GLINT_IN + (GLINT_OUT - GLINT_IN) * smoothstep(T_SPRING, T_SETTLE, t)
        fr = draw_room(G, R, tt, hut, EMBER_L, glint, STORM_L * 1.5 * (1 - opened),
                       leaves=LEAF_L + (LEAF_S - LEAF_L) * spring)

        # the spring night: moon over rippling green, and the open door at the end of Right
        wind = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 + 0.09 * tt))
        wind2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 110 + 0.21 * tt) + 2)
        fr += light(MOON, MOON_S * spring * (0.85 + 0.15 * wind2))
        fr += light(GREEN, GREEN_S * spring * (0.55 + 0.45 * wind * (0.7 + 0.3 * wind2)) * (0.9 + 0.1 * grass(tt)))
        fr += light(MOON, DOOR_S * opened * np.exp(-((L - d) / 200) ** 2))
        if T_DOOR <= t < T_DOOR + 1.6:                                          # the door swinging round
            u = smoothstep(T_DOOR, T_DOOR + 1.2, t)
            e = L - 260 * u
            fr += light(WHITE, 0.9 * (1 - smoothstep(T_DOOR + 1.0, T_DOOR + 1.6, t)) * np.exp(-((d - e) / 18) ** 2))
            fr += light(MOON, 0.6 * smoothstep(e - 10, e + 10, d))
        k = int(np.searchsorted(burst_t, t, side='right'))                      # the arpeggios: a spark a note,
        for j in range(max(0, k - 8), k):                                       # high notes far down the roof
            a = t - burst_t[j]
            if a < 0.5:
                q = L * (1 - np.clip((burst[j][1] - 55) / 38, 0, 1))
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * np.exp(-((d - q) / 30) ** 2))
                fr += light(MOON, 0.4 * np.exp(-a / 0.3) * np.exp(-((d - q) / 120) ** 2))
        if T_FLOOD <= t < T_FLOOD + FLOOD_S + 1.5:                               # the edge of the flood
            fr += light(MOON, 0.55 * (1 - smoothstep(T_FLOOD + FLOOD_S - 1, T_FLOOD + FLOOD_S + 1.5, t)) *
                        np.exp(-((d - front) / 60) ** 2))

        # every phrase a wave of green and blossom in from the door
        for t0 in verses:
            if t0 <= t < t0 + 6:
                a = t0 + 0.0
                q = L - 520 * (t - a)
                fr += light(GREEN, 0.65 * (1 - (t - a) / 6) * np.exp(-((d - q) / 190) ** 2))
                fr += light(MOON, 0.3 * (1 - (t - a) / 6) * np.exp(-((d - q - 150) / 60) ** 2))

        # blossoms on the breeze
        density = BLOSSOM_S * smoothstep(T_FLOOD + 1, T_FLOOD + 6, t) * (1 + 0.8 * smoothstep(T_SPRING, T_SPRING + 4, t)
                                                                       * (1 - smoothstep(T_SETTLE - 2, T_SETTLE + 3, t)))
        if density > 0:
            fr += light(BLOSSOM, 0.45 * density * spring * draw_blossoms(G, B, tt) * (0.8 + 0.2 * tw(tt)))

        # the lovers
        sp, lp = C['sieg'][f], C['linde'][f]
        mid = (sp + lp) / 2
        i = int(np.searchsorted(song, t, side='right')) - 1
        sf = np.exp(-(t - song[i]) / 0.3) if i >= 0 and t - song[i] < 1.2 else 0.0
        j = int(np.searchsorted(linde_n, t, side='right')) - 1
        lf = np.exp(-(t - linde_n[j]) / 0.3) if j >= 0 and t - linde_n[j] < 1.2 else 0.0
        singing = smoothstep(T_SONG - 1, T_SONG + 1, t)
        height = smoothstep(T_SPRING - 1, T_SPRING + 2, t) * (1 - 0.5 * smoothstep(BAR[1105], T_SONG + 2, t)) * \
            (1 - smoothstep(T_SETTLE - 2, D - 2, t))
        for p, col, base, fl in ((sp, BLUE, SIEG_L, sf), (lp, AMBER, LINDE_L, lf)):
            b = base * (1.25 + 0.15 * singing + 0.3 * fl + 0.25 * height) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
            fr += light(col, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
        a, b_ = sorted((sp, lp))
        between = smoothstep(a - 5, a + 15, d) * smoothstep(b_ + 5, b_ - 15, d)
        warmth = smoothstep(BLISS[0] - 1, BLISS[-1] + 2, t)
        fr += light(TOGETHER, 0.3 * (1 - warmth) * between)
        k = int(np.searchsorted(bliss, t, side='right')) - 1
        bl = np.exp(-(t - bliss[k]) / 0.8) if k >= 0 and t - bliss[k] < 3 else 0.0
        fr += light(WARM, (0.45 * warmth + 0.25 * bl) * between + (0.3 * warmth + 0.4 * bl + 0.25 * height) *
                    np.exp(-((d - mid) / (60 + 40 * bl + 80 * height)) ** 2))
        if height > 0:                                                          # one light, rippling over the house
            r = (t - T_SPRING) * 320 % 1100
            ring = np.exp(-((np.abs(d - mid) - r) / 100) ** 2) * (1 - r / 1100)
            fr += light(WARM, 0.6 * height * ring)
            fr += light(WHITE, 0.25 * height * np.exp(-((d - mid) / 14) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction: the door's arpeggios on harp and violins over tremolo cellos, the lilt
    on harp, the spring on the full orchestra, and the song's first two lines on horn and cellos."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pdoor = pan_at(G.length)
    o = Orchestra(M, level=3.0)

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    def size(t):
        return 1.0 if t < T_CALM or T_SPRING <= t < T_SONG else 0.45

    for t, d, m, v, part, h in compose():
        if part == 'burst':
            o.play('harp', m, t, d, v, pan_at(G.length * (1 - np.clip((m - 55) / 38, 0, 1))), 0.6)
            o.play('violins', m, t, 0.1, v - 10, None, 0.4)
        elif part == 'burst_low':
            o.play('cellos trem', m if m >= 36 else m + 12, t, max(d, 1.0), v, pdoor, 0.5)
            o.play('basses', m, t, d, v - 8, pdoor, 0.4)
        elif part in ('lilt', 'acc_low') and d < 0.4:
            o.play('harp', m, t, d, v + 6, pdoor * 0.4, 0.55)
            if part == 'acc_low':
                o.play('cellos', m, t, 0.1, v - 14, None, 0.3)
        elif part == 'acc':
            o.play('harp', m, t, d, v, 0.3, 0.4)
            o.play('violins' if m >= 55 else 'violas', m, t, d, v - 16, None, 0.35)
        elif part == 'song':
            o.play('horns', m, t, d, v, pt('sieg', t), 0.8)
            o.play('cellos', m, t, d, v - 8, pt('sieg', t), 0.6)
        elif part == 'surge':
            o.tutti([(t, d, m, v, h)], size=size)
            o.play('harp', m - 12, t, d, v - 14, 0.4, 0.3)
        else:
            o.tutti([(t, d, m, v, h)], size=size)
    o.hit('crash', 0.02, 110, gain=0.5, pan=pdoor)
    o.hit('timpani', 0.02, 110, pitch=-4, gain=0.6, pan=pdoor)
    o.hit('timpani roll', T_SPRING - 1.5, 90, gain=0.35)
    o.hit('crash', T_SPRING, 100, gain=0.4)
    # the stage: the door, the rush of wind, the moonlight sweeping in, the spring breeze, the hearth
    from pixelhome.audio import whoosh
    o.boom(0.02, pdoor, gain=1.0)
    o.hit('gong scrape', 0.1, 100, gain=0.4, pan=pdoor, fx=True)
    o.wind(0.0, FLOOD_S + 3.0, lambda tt: 1.4 * np.exp(-tt / 3.0) + 0.3, pan=pdoor, seed=91)
    for k, (tw, pp) in enumerate(((T_FLOOD, pdoor), (T_FLOOD + 2.5, pan_at(at(G, 'Porch Front', 0.5))),
                                  (T_FLOOD + 5.0, pan_at(at(G, 'Left', 0.4))))):
        M.add('fx', whoosh(3.0, 2500, 400, 0.6, seed=92 + k), tw, 0.8, pp)

    def breeze(tt):
        w = 0.25 + 0.15 * smoothstep(T_SPRING - 2, T_SPRING, tt) - 0.15 * smoothstep(T_SETTLE, D, tt)
        for tb in BLISS:
            w = w + 0.45 * np.exp(-((tt - tb - 0.6) / 0.9) ** 2)
        return w
    o.wind(FLOOD_S - 1.0, D, breeze, pan=0.2, seed=95)
    o.fire(0.0, D, 0.2, pan=pan_at(at(G, 'Left', 0.6)), crackle=4, seed=96)
    o.effects([(0, 2), (FLOOD_S - 1.0, 1), (T_CALM + 1.0, -6), (T_SPRING - 1.0, -6), (T_SPRING, -4),
               (T_SONG - 1.0, -5), (T_SONG, -14), (D, -12)])
