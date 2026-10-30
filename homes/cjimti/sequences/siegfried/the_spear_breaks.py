"""The Spear Breaks: still the storm at the foot of the rock, the Wanderer waiting in deep blue at Right 0.6 with
the fire burning round the porch above.

The music is Wagner's own: the Woodbird's flight to the rock (bars 454 to 461), the quarrel at the foot of the fire
"Zurück denn, rasendes Kind!" to "so sperre mein Speer dir den Weg!" (bars 714 to 722), and "noch einmal denn
zerspring' es am ew'gen Speer!", "Schwing deinen Speer: in Stücken spalt' ihn mein Schwert!", the stroke and the
spear's collapse (bars 728 to 746), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from
the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the Woodbird's figures on flutes and oboes over
trembling violas, the fire's flicker on the strings, the spear's motif crashing down on trombones, tuba and basses,
the fortissimo of the stroke on the full orchestra with trumpets on top, and the falling chords of the broken spear
on trombones over the basses' low C. Like a staged production it adds the stage's sounds: the storm (pulled down
under the quarrel so the words' music is clear), Siegfried's running feet, the fire roaring up as the Wanderer
calls it, a great blow as the spear comes down, and at the stroke steel on steel, a shatter and a thunderclap, the
broken spear clattering down, and the fire's roar as Siegfried turns to it.

The Woodbird darts in from the free end of Right, a hot magenta spark, hops toward the old man, sees the spear and
flees back the way it came; Siegfried runs in after it and pulls up short in front of him. They have it out: each
line of the Wanderer's floods the house deep blue out from him, each of Siegfried's throws it back in emerald, the
line between them swinging across the whole roofline, while the fire on the rock leaps up as the Wanderer warns of
it. "So sperre mein Speer dir den Weg!": the spear's motif crashes down and its pale shaft runs out toward the boy
note by note, each step lighting a run. Siegfried draws Nothung: white steel growing out from him, gold at the
hilt, the fortissimo hammering. One stroke: the house flashes blue-white, the shards of the spear fly out to both
ends of the roofline, and the Wanderer's blue collapses in on itself and is gone; each falling chord of the broken
spear is a last blue ripple sinking away, the storm thins, the fire round the rock flares, and Siegfried walks up
to where the old god stood, his green reaching up toward the flames.

compose() tags every note of the excerpt; stage(), sky(), figure() and fire() are the rock and the sky, shared
word for word by Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF25'
TITLE = 'The Spear Breaks'
KIND = 'show'
DESCRIPTION = ('The Woodbird leads Siegfried to the foot of the rock, where the Wanderer bars the way. Blue and '
               'green fight for the house until one stroke of the sword shatters the spear and the old god is gone.')
VOICEOVER = ('An old man with a spear blocks the path to the fire. '
             'Siegfried draws his sword, and the spear breaks in two.')

K = 2                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 454-462, 714-723 and 728-747, Solti 1958
NOTES = tidy(EX['notes'])
D = EX['seconds']
T_QUARREL = EX['segments'][1]['start']      # "Zurück denn, rasendes Kind!"
T_BIRD = 0.4                                # the Woodbird darts in
T_FLEE = 9.4                                # sees the spear, flees
T_IN = 10.8                                 # Siegfried runs in
T_HALT = T_QUARREL - 0.3
DUEL = [(s[0], 'w' if s[2] == 'Der Wanderer' else 's') for s in EX['singing']]   # each line, whose
T_SPEAR = accents(EX['notes'], 31.5, 33.5, vmin=110, n=2, space=1.0)[0]           # the spear's motif crashes down
T_SWORD = accents(EX['notes'], 57.5, 59.0, vmin=110, n=2, space=1.0)[0]           # Nothung drawn: the fortissimo
T_STRIKE = max(n[0] for n in EX['notes'] if 61.5 <= n[0] < 62.5 and n[2] >= 90)   # the top of the sword's slash
SPEARS = sorted({n[0] for n in EX['notes'] if n[4] == 1 and n[1] >= 0.3 and (T_SPEAR <= n[0] < T_SPEAR + 5 or
                                                                            39.0 <= n[0] < 50.5)})
SWORDS = accents(EX['notes'], T_SWORD, T_STRIKE - 0.3, vmin=110, n=3, space=0.25)
FALLS = accents(EX['notes'], T_STRIKE + 0.3, 75.0, vmin=100, n=2, space=0.9)       # the broken spear falling
T_WALK = (T_STRIKE + 7.0, D - 3.0)
PULSES = sorted({n[0] for n in EX['notes'] if n[0] >= 75.0})      # the soft pulsing chords as he turns to the fire
CHIRPS = [n[0] for n in EX['notes'] if n[4] == 0 and n[0] < T_FLEE + 0.5]   # the Woodbird's notes
FIRE_UP = (17.0, T_SPEAR)                   # the fire leaps up as he warns of it

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
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
BIRD = hexc('#ff30d0')
WHITE = hexc('#ffffff')

START = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF24 left it
END = dict(storm=0.4, rock=0.3, fire=0.6, wide=0.0, dawn=0.0, sleeper=0.0)          # where SF26 picks it up
WAND_AT = ('Right', 0.6)
HALT_AT = ('Right', 0.85)                   # where Siegfried pulls up in front of him


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
    """Every note of the excerpt, tagged (time, seconds, midi, velocity, part, tremolo): the Woodbird's flight
    ('bird'), the quarrel's flicker ('flicker'), the spear's motif ('spear'), the stroke's fortissimo ('stroke'),
    the broken spear falling ('fall'), the bass under it all ('bass')."""
    N = []
    for t, d, m, v, h, trem in NOTES:
        if t < T_QUARREL:
            part = 'bird' if h == 0 else 'bass'
        elif t < T_SWORD - 0.05:
            part = 'spear' if h == 1 and d >= 0.3 and m < 60 else 'flicker'
        elif t < T_STRIKE + 0.3:
            part = 'stroke'
        else:
            part = 'fall' if m >= 38 else 'bass'
        N.append((t, d, m, v, part, trem))
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength, near)]: the storm round the quarrel, the stroke, then thinning."""
    rng = np.random.default_rng(25)
    runs = ['Side', 'Left', 'Side', 'Left', 'Right', 'Side']
    ts = [(1.2, 0.5), (5.5, 0.4), (T_QUARREL + 0.3, 0.8), (T_SPEAR, 1.0), (T_SPEAR + 6.0, 0.8), (46.0, 0.6),
          (52.0, 0.6), (T_SWORD, 0.9), (T_STRIKE, 1.0), (T_STRIKE + 6, 0.4), (D - 10, 0.25)]
    return [(float(t), runs[i % len(runs)], float(rng.uniform(0.75, 1.0)) * (0.5 + 0.5 * n), n)
            for i, (t, n) in enumerate(ts)]


def bird(G, t):
    """Where the Woodbird is at time t, in quick eased hops, and how bright."""
    L = G.pd.max()
    hops = [(T_BIRD, L + 20), (T_BIRD + 1.6, at(G, 'Right', 0.92)), (T_BIRD + 3.4, at(G, 'Right', 0.82)),
            (T_BIRD + 5.2, at(G, 'Right', 0.76)), (T_BIRD + 7.0, at(G, 'Right', 0.7)), (T_FLEE, at(G, 'Right', 0.71)),
            (T_FLEE + 0.6, L + 40)]
    p = hops[-1][1]
    for (t0, p0), (t1, p1) in zip(hops, hops[1:]):
        if t < t1:
            p = p0 + (p1 - p0) * smoothstep(max(t0, t1 - 0.25), t1, t)
            break
    lvl = smoothstep(T_BIRD, T_BIRD + 0.3, t) * (1 - smoothstep(T_FLEE + 0.4, T_FLEE + 0.7, t))
    return p, lvl


def hero(G, t):
    """Where Siegfried is at time t."""
    L = G.pd.max()
    p = L + 30 + (at(G, *HALT_AT) - L - 30) * smoothstep(T_IN, T_HALT, t)
    return p + (at(G, *WAND_AT) - at(G, *HALT_AT)) * smoothstep(T_WALK[0], T_WALK[1], t)


def render(G, seed=25):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    pw = at(G, *WAND_AT)
    B = bolts()
    rng = np.random.default_rng(seed)
    shard_v = rng.uniform(600, 2800, 28) * rng.choice([-1, 1], 28)
    shard_life = rng.uniform(0.5, 1.4, 28)
    chirp_off = rng.uniform(-160, 160, 37)
    trail = []

    # the line between blue and green across the house: each line of theirs drives it toward the other's end
    line_pts = [(0.0, L + 200), (T_QUARREL, L + 200)]
    for t0, who in DUEL:
        if t0 < T_SWORD:
            line_pts += [(t0, line_pts[-1][1]), (t0 + 1.4, at(G, 'Right', 0.98) if who == 'w' else at(G, 'Left', 0.15))]
    line_pts += [(T_SWORD, line_pts[-1][1])]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_STRIKE, START[k]), (T_WALK[1], END[k])]) for k in START}
        flare = smoothstep(FIRE_UP[0], FIRE_UP[1], t) * (1 - smoothstep(T_STRIKE, T_STRIKE + 2, t))
        lv['fire'] += 0.35 * flare + 0.3 * smoothstep(T_WALK[0], T_WALK[1], t)
        fr = sky(S, T, lv)
        ps = hero(G, t)

        for tb, run, s, near in B:
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * s * np.exp(-a / 0.4) * (G.seg_of == run))

        # the quarrel: blue floods out from him, emerald from the boy, the line between swinging over the house
        if T_QUARREL <= t < T_STRIKE:
            b = keys(t, line_pts)
            fade = smoothstep(T_QUARREL, T_QUARREL + 1.0, t) * (1 - smoothstep(T_SWORD - 0.5, T_SWORD + 1.0, t))
            blue = smoothstep(b + 70, b - 70, d)
            fr += light(WOTAN, 0.7 * fade * blue)
            fr += light(EMERALD, 0.65 * fade * (1 - blue))
            fr += light(WHITE, 0.55 * fade * np.exp(-((d - b) / 18) ** 2))
            for t0, who in DUEL:
                a = t - t0
                if 0 <= a < 0.8:
                    col = WOTAN if who == 'w' else EMERALD
                    src = pw if who == 'w' else ps
                    fr += light(col, 0.8 * np.exp(-a / 0.25) * np.exp(-((np.abs(d - src) - 900 * a) / 60) ** 2))

        # the Woodbird: a hot magenta spark in hops, white at the heart, a short trail; it flees from the spear
        pb, lb = bird(G, t)
        trail = (trail + [pb])[-6:]
        if lb > 0:
            for j, q in enumerate(trail):
                fr += light(BIRD, lb * (0.25 + 0.12 * j) * np.exp(-((d - q) / 8) ** 2))
            flap = 0.8 + 0.2 * np.sin(2 * np.pi * 9 * t)
            fr += light(BIRD, lb * flap * np.exp(-((d - pb) / 8) ** 2))
            fr += light(WHITE, 0.8 * lb * np.exp(-((d - pb) / 3) ** 2))
            for k, t0 in enumerate(CHIRPS):     # each of its notes a magenta twinkle shed round it
                a = t - t0
                if 0 <= a < 0.5:
                    q = pb + chirp_off[k % len(chirp_off)]
                    fr += light(BIRD, 0.8 * np.exp(-a / 0.15) * np.exp(-((d - q) / 6) ** 2))

        # the spear's shaft running out toward him note by note, each step lighting a run
        if T_SPEAR <= t < T_STRIKE + 0.1:
            n = sum(1 for x in SPEARS if x <= t)
            reach = (ps - pw) * 0.5 * n / len(SPEARS)
            lo, hi = sorted((pw, pw + reach))
            fr += light(SPEAR, 0.95 * ((d >= lo) & (d <= hi)))
            j = n - 1
            if j >= 0:
                a = t - SPEARS[j]
                run = ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right'][j % 6]
                fr += light(SPEAR, 1.0 * np.exp(-a / 0.5) * (G.seg_of == run))
                fr += light(WOTAN, 0.6 * np.exp(-a / 0.9) * (G.seg_of == run))
        # Nothung: white steel growing out from him on the fortissimo's hammering chords
        if T_SWORD <= t < T_STRIKE + 0.1:
            n = sum(1 for x in SWORDS if x <= t)
            reach = (pw - ps) * 0.48 * n / max(1, len(SWORDS))
            lo, hi = sorted((ps, ps + reach))
            fr += light(STEEL, 1.0 * ((d >= lo) & (d <= hi)))
            fr += light(HILT, 1.0 * np.exp(-((d - ps) / 6) ** 2))
            for x in SWORDS:
                a = t - x
                if 0 <= a < 1.0:
                    fr += light(STEEL, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - ps) - 2000 * a) / 90) ** 2))

        # the stroke: the whole house blue-white for a moment, shards out to both ends, his blue imploding
        a = t - T_STRIKE
        if 0 <= a < 0.5:
            fr += light(BOLT, 0.9 * np.exp(-a / 0.12))
        if 0 <= a < 2.0:
            mid = (pw + ps) / 2
            q = mid + shard_v * (1 - np.exp(-a / 0.6)) * 0.6
            life = np.exp(-a / shard_life)
            fr += light(SPEAR, np.clip((life[:, None] * np.exp(-((d[None, :] - q[:, None]) / 9) ** 2)).sum(0), 0, 1))
            fr += light(STEEL, 0.8 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - mid) - 1600 * a) / 80) ** 2))
        for k, t0 in enumerate(FALLS):          # each falling chord of the broken spear: a last blue ripple sinking
            a = t - t0
            if 0 <= a < 1.8:
                g = 1.0 * (1 - 0.5 * k / max(1, len(FALLS)))
                fr += light(WOTAN, g * np.exp(-a / 0.7) * np.exp(-((np.abs(d - pw) - 600 * a) / 110) ** 2))
                fr += light(SPEAR, 0.4 * g * np.exp(-a / 0.3) * np.exp(-((d - pw) / 30) ** 2))

        # the Wanderer, until the stroke; then his blue collapses in on itself
        gone = smoothstep(T_STRIKE, T_STRIKE + 2.5, t)
        if gone < 1:
            fr = figure(fr, S, pw, WOTAN, 0.85 * (1 - gone), w=16 * (1 - 0.7 * gone))
            if t < T_STRIKE:
                fr += light(SPEAR, 0.6 * np.exp(-((d - pw + 14) / 6) ** 2))
            if gone > 0:
                r = 500 * (1 - gone)
                fr += light(WOTAN, 0.9 * (1 - gone) * np.exp(-((np.abs(d - pw) - r) / 50) ** 2))

        # the soft pulsing chords as he turns to the fire: the flames round the rock leap with each one
        j = int(np.searchsorted(PULSES, t, side='right')) - 1
        if j >= 0 and t - PULSES[j] < 0.4:
            a = t - PULSES[j]
            fr += fire(S, T, 0.45 * np.exp(-a / 0.2) * smoothstep(PULSES[0], PULSES[0] + 3, t), 0.0, boost=1.0)

        # Siegfried, and alone at the end his green reaching up toward the fire
        if t >= T_IN - 0.3:
            lvl = 0.85 * smoothstep(T_IN - 0.3, T_IN + 0.3, t)
            fr = figure(fr, S, ps, EMERALD, lvl)
            fr += light(HERO_HEAD, 0.7 * lvl * np.exp(-((d - ps) / 5) ** 2))
            if t > T_STRIKE:
                g = smoothstep(T_STRIKE + 2, T_STRIKE + 8, t) * (1 + 0.6 * smoothstep(PULSES[0], D - 2, t))
                fr += light(EMERALD, 0.45 * g * np.exp(-np.clip(ps - d, 0, None) / 300) * (d <= ps)
                            * (0.7 + 0.3 * np.sin(2 * np.pi * ((ps - d) / 200 + 0.8 * t))))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the stage's sounds ridden round the music."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    pw = pan_at(at(G, *WAND_AT))
    o = Orchestra(M, level=2.2)
    N = {(e[0], e[2]): e[4] for e in compose()}

    def role(t, d, m, v, h):
        part = N.get((t, m))
        if part == 'bird':                                  # the Woodbird: flutes and oboes
            return [('flutes', 0, 10, 0.55), ('oboes', 0, 0, 0.35)]
        if part == 'spear':                                 # the spear: trombones, tuba, basses
            return [('trombones', 0, 6, 0.85), ('tuba', 0 if m < 48 else -12, 0, 0.6), ('basses', -12 if m >= 40 else 0, -4, 0.5)]
        if part == 'stroke' and h == 0 and v >= 100:        # the stroke: full orchestra, trumpets on top
            return [('violins', 0, 0, 0.55), ('trumpets', 0, -8, 0.45), ('horns', -12, -6, 0.5)]
        if part == 'fall' and d >= 0.3:                     # the broken spear falling: trombones over the low C
            return [('trombones', 0, -4, 0.7), ('horns', 0, -10, 0.4)]
        return None

    def size(t):
        return 1.0 if T_SPEAR - 0.5 <= t < T_STRIKE + 6 else 0.7

    o.tutti(NOTES, size=size, role=role)

    # the stage, ridden round the music: low under the Woodbird, up for his running feet, down under the quarrel,
    # leading at the spear and the stroke, back under the falling chords, and the fire's roar rising at the end
    o.effects([(0.0, -9), (T_IN - 0.5, -9), (T_IN, -3), (T_QUARREL, -3), (T_QUARREL + 1.5, -10),
               (T_SPEAR - 0.5, -10), (T_SPEAR, -1), (T_SPEAR + 4, -8), (T_SWORD - 0.5, -8), (T_SWORD, -3),
               (T_STRIKE - 0.1, 2), (T_STRIKE + 4, 0), (T_STRIKE + 7, -8), (D - 14, -8), (D - 6, -3), (D, -3)])
    o.wind(0.0, T_STRIKE + 10, level=0.7, pan=0.0, seed=31)
    for tb, run, s, near in bolts():
        o.thunder(tb, near=near, pan=pan_at(at(G, run, 0.5)), gain=0.8 * s, seed=int(tb * 100) + 5)
    o.gallop(T_IN, T_HALT, beat=0.3, pan=lambda tt: pan_at(hero(G, tt)), v=92, gain=0.7)       # his running feet
    o.fire(FIRE_UP[0], T_STRIKE + 3, level=lambda tt: 0.25 + 0.55 * smoothstep(FIRE_UP[0], FIRE_UP[1], tt),
           pan=pan_at(at(G, 'Porch Front', 0.5)), crackle=8, seed=11)
    o.boom(T_SPEAR, pw, 0.9)                                                    # the spear comes down
    o.hit('scrape', T_SPEAR + 0.1, 100, gain=0.4, pan=pw)
    mid = pan_at((at(G, *WAND_AT) + at(G, *HALT_AT)) / 2)
    o.hit('cymbal swell', T_STRIKE - 3.2, 100, gain=0.45, pan=mid)
    o.clash(T_STRIKE, mid, 127, 1.2)                                            # the stroke: steel on steel
    o.shatter(T_STRIKE + 0.02, mid, 1.2)
    o.boom(T_STRIKE + 0.03, mid, 1.0)
    for k, t0 in enumerate(FALLS[:6]):                                          # the pieces clattering down
        o.hit('metal', t0 + 0.05, 100 - 6 * k, gain=0.3, pan=(-1) ** k * 0.6)
    o.fire(T_STRIKE + 2, D, level=lambda tt: 0.3 + 0.6 * smoothstep(T_WALK[0], T_WALK[1], tt),
           pan=pan_at(at(G, 'Porch Right', 0.5)), crackle=10, seed=13)
