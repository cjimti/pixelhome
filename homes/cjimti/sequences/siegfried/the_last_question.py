"""The Last Question: the storm at the foot of the rock goes on. Erda stands green at the middle of Left, the
Wanderer in deep blue at the front of it; she has no answer for him, so he answers himself.

The music is Wagner's own: the Wanderer's "Um der Götter Ende grämt mich die Angst nicht" (bars 360 to 367), the
Ring and the hero who will inherit the world, "Liebesfroh, ledig des Neides" (bars 392 to 401), and "dem ewig
Jungen weicht in Wonne der Gott" to "Hinab! Hinab, zu ew'gem Schlaf!" (bars 424 to 439), as Solti's 1958 Vienna
Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py): the right hand on violins (the world's inheritance warmed by horns), the left hand's long
notes on horns and trombones, the bass on cellos, basses and tuba. Like a staged production it adds the storm, which
backs well off under the vision and comes back to lead when he sends her down: wind and rain, thunder with every
bolt, his spear thrusts as blows with a rush of air, and the earth groaning as she sinks.

He tells her he wills the end, each line a blue pulse thrown at her, and her green narrows and dims: she has no
answer. On the two great chords the sky flashes violet, then drains to a deep red-violet as his blue grows round
him. Then the vision: on "errang des Niblungen Ring" an emerald front runs in from the free end of Right over
every run, and gold surges ride its loudest notes; through "Liebesfroh" the house glows emerald and gold, and on
"dem ewig Jungen weicht in Wonne der Gott" it blazes. "Hinab denn, Erda!": the storm crashes back, his spear
thrusts at her and his chords roll blue over the house while she reels; at the second "Hinab!" her green
collapses down into the ground at the middle of Left, a dark gulp of earth and gone, and he crosses round the
rock to Right 0.6, the storm closing back in on him there, waiting for the boy.

compose() tags every note of the excerpt; stage(), sky(), figure() and fire() are the rock and the sky, shared
word for word by Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF24'
TITLE = 'The Last Question'
KIND = 'show'
DESCRIPTION = ('Erda has no answer for the Wanderer. He wills the end of the gods himself, sees the world pass to '
               'a young hero in a blaze of green and gold, and sends the earth mother back into the ground.')
VOICEOVER = ('Even the earth mother has no answer. So the old god chooses the end, '
             'and gives the world to the hero.')

K = 1                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 360-368, 392-402 and 424-440, Solti 1958
NOTES = tidy(EX['notes'])
D = EX['seconds']
T_ASK = [s[0] for s in EX['singing'][:3]]   # his words thrown at her
T_NEED = accents(EX['notes'], 9.5, 13.5, vmin=110, n=2, space=1.0)    # the two great chords
T_DOWN = T_NEED[-1]                         # the Twilight of the Gods
T_HERO = EX['segments'][1]['start']         # "errang des Niblungen Ring": the vision
T_JUNG = EX['segments'][2]['start'] + 2.4   # "dem ewig Jungen weicht in Wonne der Gott"
T_PEAK = accents(EX['notes'], 54.0, 57.0, vmin=100, n=2, space=1.0)[0]
T_HINAB = [s[0] for s in EX['singing'] if s[3].startswith('Hinab')]   # his two thrusts
T_SINK = T_HINAB[1]
T_WALK = (T_SINK + 5.0, D - 1.5)
GOLDS = [t for t in accents(EX['notes'], T_HERO, T_HINAB[0] - 2, vmin=96, n=2, space=0.6)]
MELODY = [(t, m) for t, d, m, v, h in EX['notes'] if h == 0 and d >= 0.45 and T_HERO <= t < T_HINAB[0] - 2]
CHORDS = accents([n for n in EX['notes'] if n[1] >= 0.8 and n[4] == 1], T_HINAB[0], T_SINK + 1, vmin=60, n=1,
                 space=1.8)

STORM = hexc('#1a2ab0')
CLOUD = hexc('#4a6aff')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
SUNRISE = colormap([(0.0, hexc('#ff4080')), (0.5, hexc('#ffc020')), (1.0, hexc('#40a0ff'))])
SILVER = hexc('#f4f8ff')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
MOSS = hexc('#30c020')
EARTH = hexc('#3a2410')
ERDA_HI = hexc('#60ff30')
TWILIGHT = hexc('#a0207a')
EMERALD = hexc('#00ff40')
HERO_HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffc020')

START = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF23 left it
END = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)
WAND_FROM = ('Left', 0.8)
WAND_TO = ('Right', 0.6)                    # where he waits for Siegfried
ERDA_AT = ('Left', 0.35)


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky."""
    d = G.pd
    rng = np.random.default_rng(1871)       # the same clouds and rain in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        rain=Flicker(rng, G.N, 4.0, 11.0),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        jag=rng.uniform(0.3, 1.0, G.N),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def sky(S, T, lv):
    """The sky and the rock at shared time T with levels lv (storm, rock, fire, wide, dawn, sleeper)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.05 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.09 * T) + 1.1)
    st = STORM + (CLOUD - STORM) * u[:, None]
    fr = light(st, lv['storm'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(RAIN, 0.6 * lv['storm'] * S['sky'] * np.clip(S['rain'](T) - 1.0, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(SUNRISE(np.clip(0.15 + 0.7 * u + 0.15 * np.sin(0.2 * T), 0, 1)), lv['dawn'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'], lv['wide'])
    fr += light(SILVER, lv['sleeper'] * np.exp(-(S['db'] / 22) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def compose():
    """Every note of the excerpt, tagged (time, seconds, midi, velocity, part, tremolo): the right hand ('hi'), the
    left hand's long notes ('chord') and its others ('bass')."""
    N = []
    for t, d, m, v, h, trem in NOTES:
        N.append((t, d, m, v, 'hi' if h == 0 else 'chord' if d >= 0.6 and m >= 48 else 'bass', trem))
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength, near)]: the two great chords, the storm crashing back at "Hinab", and far
    off as it closes in again."""
    rng = np.random.default_rng(24)
    runs = ['Right', 'Side', 'Left', 'Right', 'Side', 'Left']
    ts = [(t, 0.8) for t in T_NEED]
    ts += [(t, 1.0) for t in accents(EX["notes"], T_PEAK - 0.5, T_SINK - 1.0, vmin=94, n=2, space=2.4)]
    ts += [(T_SINK + 0.1, 0.7), (D - 9.0, 0.35), (D - 5.5, 0.45), (D - 2.5, 0.55)]
    return [(float(t), runs[i % len(runs)], float(rng.uniform(0.8, 1.0)) * (0.55 + 0.45 * n), n)
            for i, (t, n) in enumerate(ts)]


def walk(G, t):
    """Where the Wanderer is at time t: round the rock from Left to Right."""
    a, b = at(G, *WAND_FROM), at(G, *WAND_TO)
    return a + (b - a) * smoothstep(T_WALK[0], T_WALK[1], t)


def render(G, seed=24):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    p_erda = at(G, *ERDA_AT)
    B = bolts()
    loud = np.zeros(F)                      # how loud the orchestra is, frame by frame, for the vision to breathe
    for n in EX['notes']:
        i = int(n[0] / DT)
        loud[i:i + max(1, int(min(n[1], 1.0) / DT))] += n[3] / 127
    loud = np.convolve(loud, np.ones(16) / 16, 'same')
    loud = np.clip(loud / np.percentile(loud, 95), 0, 1)
    lo_m, hi_m = min(m for _, m in MELODY), max(m for _, m in MELODY)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        down = smoothstep(T_DOWN, T_DOWN + 3, t) * (1 - smoothstep(T_HERO - 1, T_HERO + 1, t))
        vis = smoothstep(T_HERO - 0.2, T_HERO + 0.4, t) * (1 - smoothstep(T_HINAB[0] - 1.5, T_HINAB[0], t))
        lv['storm'] = START['storm'] * (1 - 0.5 * down - 0.6 * vis)
        fr = sky(S, T, lv)
        p = walk(G, t)

        # lightning: a whole run cracks white
        for tb, run, s, near in B:
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * np.exp(-a / 0.4) * (G.seg_of == run))

        # Erda: green that narrows and dims as he talks and she has no answer; reeling at his first thrust; then
        # she collapses into the ground at the second
        weak = smoothstep(0.0, T_HERO, t)
        reel = sum(np.exp(-max(0.0, t - t0) / 0.5) * (t >= t0) for t0 in T_HINAB[:1])
        sink = smoothstep(T_SINK, T_SINK + 5.0, t)
        g = (1 - 0.4 * weak) * (1 - sink) * (1 - 0.4 * smoothstep(T_HINAB[0], T_SINK, t))
        w = (320 - 140 * weak) * (1 - 0.25 * reel) * (1 - 0.92 * sink) + 8
        wav = 0.15 * np.sin(2 * np.pi * t / 2.4)
        if g > 0.005:
            fr += light(EARTH, 0.7 * g * np.exp(-((d - p_erda) / (w * 1.4)) ** 2))
            fr += light(MOSS, (0.8 + wav) * g * np.exp(-((d - p_erda) / w) ** 2))
            fr = figure(fr, S, p_erda, ERDA_HI, (0.6 + wav) * g, w=20)
        if T_SINK + 4.0 <= t < T_SINK + 8:            # the gulp of earth where she went down
            a = t - T_SINK - 4.0
            fr += light(EARTH, 1.0 * np.exp(-a / 0.8) * np.exp(-((d - p_erda) / 120) ** 2))
            fr += light(MOSS, 0.8 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_erda) - 600 * a) / 60) ** 2))

        # his words: blue pulses thrown at her
        for t0 in T_ASK:
            a = t - t0
            if 0 <= a < 1.4:
                c = p + (p_erda - p) * min(1.0, a / 0.5)
                fr += light(WOTAN, 0.95 * np.exp(-a / 0.7) * np.exp(-((d - c) / 45) ** 2))

        # the two great chords: the sky flashes violet
        for t0 in T_NEED:
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(DUSK, 0.9 * np.exp(-a / 0.35) * S['sky'])

        # the Twilight of the Gods: the sky drains to red-violet, his blue grows round him
        fr += light(TWILIGHT, 0.85 * down * S['sky'] * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 380 - 0.15 * t))))
        fr += light(WOTAN, 0.7 * down * np.exp(-((d - p) / (120 + 260 * down)) ** 2))

        # the vision: an emerald front from the free end of Right over every run, a gold surge on each loud note,
        # and the blaze of "dem ewig Jungen"
        if T_HERO <= t < T_HINAB[0]:
            a = t - T_HERO
            front = L - min(1.0, a / 3.0) * (L + 60)
            blaze = smoothstep(T_JUNG, T_PEAK, t) * (1 - smoothstep(T_PEAK + 1.5, T_HINAB[0], t))
            keep = 1 - 0.8 * np.exp(-((d - p_erda) / 70) ** 2)       # Erda still there, dim, at the middle of Left
            roll = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 340 + 0.45 * t))
            fr += light(EMERALD, (0.35 + 0.5 * loud[f] + 0.3 * blaze) * roll * keep * vis
                        * smoothstep(front - 60, front + 60, d))
            for t0, m in MELODY:                 # each note of the melody a gold pulse running in from Right
                b = t - t0
                if 0 <= b < 2.0:
                    u = (m - lo_m) / max(1, hi_m - lo_m)
                    x = L - (L + 100) * (b / 2.0)
                    fr += light(GOLD, (0.5 + 0.5 * u) * np.exp(-b / 1.2) * np.exp(-((d - x) / (40 + 40 * u)) ** 2))
            fr += light(HERO_HEAD, 1.0 * np.exp(-((d - front) / 22) ** 2) * (a < 3.2))
            for k, t0 in enumerate(GOLDS):
                b = t - t0
                if 0 <= b < 1.6:
                    r = (L + 100) * (1 - np.exp(-b / 0.5))
                    src = (L - d) if k % 2 == 0 else d
                    fr += light(GOLD, 1.2 * np.exp(-b / 0.8) * np.exp(-((src - r) / 90) ** 2))
            fr += light(GOLD, (0.25 + 0.5 * blaze) * vis * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 + 0.4 * t))))
            if 0 <= t - T_PEAK < 1.5:
                fr += light(HERO_HEAD, 0.8 * np.exp(-(t - T_PEAK) / 0.4))

        # the Wanderer, and his spear thrusts that send Erda down
        fr = figure(fr, S, p, WOTAN, 0.85)
        fr += light(SPEAR, 0.6 * np.exp(-((d - p + 14) / 6) ** 2))
        for t0 in T_HINAB:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(BOLT, min(1.0, 1.2 * np.exp(-a / 0.08)) * np.exp(-((d - p) / 50) ** 2))
                fr += light(SPEAR, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - (p + (p_erda - p) * min(1.0, a / 0.25))) / 30) ** 2))
                fr += light(WOTAN, 0.6 * np.exp(-a / 0.3))
        for t0 in CHORDS:                       # his chords roll blue over the house while she reels
            a = t - t0
            if 0 <= a < 2.5:
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(WOTAN, 1.0 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - walk(G, t0)) - r) / 200) ** 2))
                fr += light(CLOUD, 0.5 * np.exp(-a / 0.5) * S['sky'])
        if t >= T_WALK[0]:                      # his cloak trailing blue behind him round the rock, then his wait
            fr += light(WOTAN, 0.55 * np.exp(-np.clip(d - p, 0, None) / 160) * (d >= at(G, *WAND_FROM)) * (d <= p + 20))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the storm ridden under the vision."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    erda_p = pan_at(at(G, *ERDA_AT))
    o = Orchestra(M, level=2.4)

    def size(t):
        if T_HINAB[0] - 4 <= t < T_SINK:
            return 1.0
        if T_HERO <= t < T_HERO + 6:
            return 1.0
        return 0.6

    def role(t, d, m, v, h):
        if T_HERO <= t < T_HINAB[0] and h == 0 and d >= 0.5:      # the world's inheritance: violins, warm horns
            return [('violins', 0, 0, 0.6), ('horns', -12, -4, 0.5), ('violas', -12, -10, 0.3)]
        if t >= T_SINK and h == 1 and m < 48:                     # down into the earth: bassoons and basses
            return [('cellos', 0, 6, 0.6), ('basses', 0, 0, 0.55), ('bassoons', 12, -4, 0.4)]
        return None

    o.tutti(NOTES, size=size, role=role, pan=lambda t, m: pan_at(walk(G, t)) * 0.4 if m >= 48 else 0.0)

    # the storm: a low bed under his words, well away under the vision, leading when he sends her down
    o.effects([(0.0, -7), (T_HERO - 1, -7), (T_HERO + 1, -14), (T_HINAB[0] - 1.5, -14), (T_HINAB[0], 0),
               (T_SINK + 1, 0), (T_SINK + 4, -5), (D, -3)])
    o.wind(0.0, D, level=lambda tt: 0.5 + 0.4 * smoothstep(T_HINAB[0] - 1, T_HINAB[0], tt), pan=0.0, seed=29)
    for tb, run, s, near in bolts():
        o.thunder(tb, near=near, pan=pan_at(at(G, run, 0.5)), gain=0.8 * s, seed=int(tb * 100) + 3)
    for t0 in T_HINAB:                     # the spear thrusts: a blow and a rush of air
        o.boom(t0, pan_at(walk(G, t0)), 0.8)
        o.hit('metal', t0, 110, gain=0.35, pan=pan_at(walk(G, t0)))
    o.hit('timpani roll', T_SINK + 0.5, 100, pitch=-7, gain=0.6, pan=erda_p)   # she sinks: the earth groans
    o.hit('gong scrape', T_SINK + 1.0, 100, gain=0.5, pan=erda_p)
    o.thunder(T_SINK + 1.2, near=0.1, pan=erda_p, gain=0.9, seed=88)
    o.boom(T_SINK + 4.0, erda_p, 0.6)       # the gulp of earth
    o.hit('crash', T_HERO, 104, gain=0.4)    # the vision breaks in
    o.hit('crash', T_PEAK, 116, gain=0.5)
    o.hit('timpani', T_PEAK, 118, pitch=-5, gain=0.6)
