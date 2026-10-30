"""Leuchtende Liebe: the end of the opera, on the summit in the full sunrise, Siegfried emerald at Porch Front 0.42
and Brünnhilde silver with gold glints at 0.55.

The music is Wagner's own: the last 53 bars of Siegfried (Act III, bars 1738-1790), as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py), to the
opera's last chord. The two of them throw their lines at each other ("Götterdämm'rung, dunkle herauf!", "Heil der
Welt, da Brünnhilde lebt!", "Sie ist mir ewig, ist mir immer, Erb' und Eigen, Ein' und All'!"), and then laugh at
death together, "leuchtende Liebe, lachender Tod!", four times, the last up to her high C; then the orchestra
races to the end. The voices are not in the reduction, so Brünnhilde's "leuchtende Liebe, lachender Tod!" comes
from the printed vocal score (Breitkopf & Härtel, 1914, archive.org 31761034115105, pp. 364-365), checked against
the orchestra doubling it, and is played as written on a trumpet doubled by violins. The orchestra is full from
the start and fuller as it goes, trumpets on top in the coda. The staging adds what a production would for the
final blaze: timpani driving the coda, cymbal swells into the great chords and a crash and a gong on the last; it
keeps out of the way while they sing.

Every line they throw at each other sends a wave out across the house, emerald from him, silver and gold from
her, and the orchestra's big chords swell whole runs between them. "Leuchtende Liebe, lachender Tod!": every note
of her line slams a whole run of the house in silver-gold, every chord under it a run in emerald, run after run
round the roofline, and on her high C the whole house flashes white gold. The coda builds the light beneath them
to full strength, emerald on the wings, silver and gold on the rock, every accent a flash; the four great chords
at the end are each a whole-house hit of white gold, and on the last the house blazes emerald and silver and gold
on every run and holds it to the end.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF30'
TITLE = 'Leuchtende Liebe'
KIND = 'show'
DESCRIPTION = ('The end of the opera. Siegfried and Brünnhilde sing faster and faster, laughing at death, until '
               'the whole house blazes emerald, silver and gold on four great chords.')
VOICEOVER = ('Shining love, and laughing death! '
             'The end of Siegfried.')

K = 7                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 1738-1790, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds'] + 2.4                     # the last chord rings on and the blaze holds
LINES = sorted((s[0], s[2][:2]) for s in EX['singing'] if s[0] < BAR[1761])   # their lines: (time, 'Si'/'Br')
T_LAUGH = BAR[1761]                         # "leuchtende Liebe, lachender Tod!"
# Her line, from the vocal score: (bar, beat, beats, note), 4/4.
VOICE = [(1761, 2, 4, 'A5'), (1762, 2, 1.5, 'C#5'), (1762, 3.5, 0.5, 'D5'), (1763, 0, 1.5, 'D#5'),
         (1763, 1.5, 0.5, 'E5'), (1763, 2, 2, 'E5'), (1764, 1, 2, 'F5'), (1764, 3, 0.5, 'D5'), (1764, 3.5, 0.5, 'B4'),
         (1765, 0, 2.5, 'G5'),
         (1767, 2, 4, 'F5'), (1768, 2, 1.5, 'E5'), (1768, 3.5, 0.5, 'D5'), (1769, 0, 1, 'G5'),
         (1769, 1, 1 / 3, 'G5'), (1769, 4 / 3, 1 / 3, 'F5'), (1769, 5 / 3, 1 / 3, 'E5'), (1769, 2, 1, 'E5'),
         (1771, 0, 4 / 3, 'D5'), (1771, 4 / 3, 1 / 3, 'C#5'), (1771, 5 / 3, 1 / 3, 'D5'), (1771, 2, 4, 'A5'),
         (1772, 2, 1, 'G#5'),
         (1773, 0, 4 / 3, 'E5'), (1773, 4 / 3, 1 / 3, 'A5'), (1773, 5 / 3, 1 / 3, 'G5'), (1773, 2, 4, 'G5'),
         (1774, 2, 2, 'E5'),
         (1776, 0, 3, 'G5'), (1776, 3, 0.5, 'A5'), (1776, 3.5, 0.5, 'G5'), (1777, 0, 2, 'C6')]
T_HIGH_C = BAR[1777]                        # her high C: the whole house flashes
T_CODA = BAR[1778]                          # the orchestra races to the end
CHORDS = accents(EX['notes'], BAR[1786] + 1, EX['seconds'], 60, 4, 0.8)[-4:]     # the four great chords
CODA = accents(EX['notes'], T_CODA, CHORDS[0] - 0.3, 80, 3, 0.3)

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
HEAD = hexc('#e8ffe8')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffc020')
WHITEGOLD = hexc('#fff0b0')

DAWN = dict(storm=0.0, rock=0.35, fire=0.15, wide=0.0, dawn=0.75, sleeper=0.0)
SIEG_AT, BRUNN_AT = 0.42, 0.55
RUNS = ['Left', 'Porch Front', 'Right', 'Side', 'Porch Left', 'Porch Right']


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


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: emerald, with a white-hot head."""
    fr = figure(fr, S, p, EMERALD, lvl, w)
    return fr + light(HEAD, 0.8 * lvl * np.exp(-((S['d'] - p) / (0.35 * w)) ** 2))


def heroine(fr, S, p, lvl, T, w=16.0):
    """Brünnhilde awake: silver white, with gold glints round her."""
    fr = figure(fr, S, p, SILVER, lvl, w)
    tw = 0.5 + 0.5 * np.sin(2 * np.pi * (S['d'] / 23 + 1.3 * T)) * np.sin(2 * np.pi * (S['d'] / 37 - 0.9 * T))
    return fr + light(GLINT, 0.8 * lvl * tw ** 3 * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def when(bar, beat):
    """Excerpt time of a beat in a 4/4 bar."""
    return float(np.interp(bar + beat / 4, [b[0] for b in EX['bars']], [b[1] for b in EX['bars']]))


def voice():
    """Her line in seconds: (time, seconds, midi)."""
    return [(when(b, x), when(b, x + n) - when(b, x), note(name)) for b, x, n, name in VOICE]


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, hand, part, trem). 'lines' while they
    throw their lines at each other, 'laugh' under "leuchtende Liebe", 'coda' after; 'voice' is her line."""
    N = []
    for t, d, m, v, h, tr in tidy(EX['notes']):
        part = 'lines' if t < T_LAUGH - 0.01 else 'laugh' if t < T_CODA - 0.01 else 'coda'
        N.append((t, d, m, v, h, part, tr))
    for t, d, m in voice():
        N.append((t, d, m, 110, 0, 'voice', False))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=30):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    N = compose()
    ps, pb = at(G, 'Porch Front', SIEG_AT), at(G, 'Porch Front', BRUNN_AT)
    runs = {r: (G.seg_of == r) for r in RUNS}
    wings = np.isin(G.seg_of, ['Side', 'Left', 'Right'])
    big = np.array(accents(EX['notes'], 0, T_LAUGH, 90, 4, 0.9))
    sung = np.array(sorted({e[0] for e in N if e[5] == 'voice'}))
    under = np.array(accents([e[:5] for e in N if e[5] == 'laugh' and e[4] == 1], T_LAUGH, T_CODA, 70, 2, 0.35))
    slam = sorted([(t0, 'B') for t0 in sung] + [(t0, 'S') for t0 in under])
    coda = np.array(CODA)

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        build = smoothstep(T_CODA - 2, CHORDS[-1], t)
        blaze = smoothstep(CHORDS[-1], CHORDS[-1] + 0.6, t)
        lv = dict(DAWN)
        lv['dawn'] = DAWN['dawn'] * (1 - 0.45 * smoothstep(1, 3, t)) * (1 - 0.6 * blaze)
        fr = sky(S, T, lv)

        # the light building beneath them: emerald on the wings, silver and gold on the rock
        base = 0.12 * smoothstep(T_LAUGH - 4, T_LAUGH, t) + 0.6 * build + 0.3 * blaze
        shimmer = 0.85 + 0.15 * np.sin(2 * np.pi * (d / 260 - 0.6 * t))
        fr += light(EMERALD, base * wings * shimmer)
        fr += light(SILVER, 0.85 * base * S['porch'] * shimmer)
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 31 + 1.7 * T)) * np.sin(2 * np.pi * (d / 19 - 1.1 * T))
        fr += light(GOLD, (0.4 * build + 0.6 * blaze) * tw ** 2)

        # their lines thrown at each other: a wave out from whoever sings, emerald from him, silver and gold from her
        for t0, who in LINES:
            a = t - t0
            if 0 <= a < 2.2:
                p, c1, c2 = (ps, EMERALD, HEAD) if who == 'Si' else (pb, SILVER, GLINT)
                r = 1500 * (1 - np.exp(-a / 0.55))
                fr += light(c1, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p) - r) / 240) ** 2))
                fr += light(c2, 0.5 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p) - 0.8 * r) / 80) ** 2))
        # the orchestra's big chords between them swell whole runs
        a = recent(big, t, 2.0)
        if a is not None:
            j = int(np.searchsorted(big, t, side='right')) - 1
            fr += light(EMERALD if j % 2 == 0 else SILVER, 0.8 * smoothstep(0, 0.15, a) * np.exp(-a / 0.9)
                        * runs[RUNS[j % len(RUNS)]])

        # laughing at death: every note of hers slams a run in silver-gold, every chord under it a run in emerald
        for j, (t0, who) in enumerate(slam):
            a = t - t0
            if 0 <= a < 0.9:
                run = runs[RUNS[j % len(RUNS)]]
                if who == 'S':
                    fr += light(EMERALD, np.exp(-a / 0.45) * run) + light(HEAD, 0.5 * np.exp(-a / 0.08) * run)
                else:
                    fr += light(SILVER, np.exp(-a / 0.45) * run) + light(GLINT, 0.6 * np.exp(-a / 0.3) * run)
        if T_HIGH_C <= t < T_HIGH_C + 2.0:
            a = t - T_HIGH_C
            fr += light(WHITEGOLD, 0.85 * np.exp(-a / 0.45))

        # the coda: every accent a flash over the building light, from both ends in turn
        a = recent(coda, t, 0.6)
        if a is not None:
            j = int(np.searchsorted(coda, t, side='right')) - 1
            fr += light(WHITEGOLD if j % 2 else EMERALD, 0.7 * np.exp(-a / 0.22) * (S['porch'] if j % 2 else wings))

        # the four great chords: each a whole-house hit of white gold; the last becomes the blaze
        for k, t0 in enumerate(CHORDS):
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(WHITEGOLD, (0.75 + 0.08 * k) * np.exp(-a / (0.35 + 0.25 * (k == 3))))
        if blaze > 0:
            fr += light(EMERALD, 0.25 * blaze * wings)
            fr += light(GOLD, 0.3 * blaze * S['porch'] * (0.7 + 0.3 * tw))

        fr = hero(fr, S, ps, 0.85 + 0.15 * build)
        fr = heroine(fr, S, pb, 0.9 + 0.1 * build, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with her line from the vocal score on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    her = pan_at(at(G, 'Porch Front', BRUNN_AT))
    him = pan_at(at(G, 'Porch Front', SIEG_AT))
    mid = (her + him) / 2
    o = Orchestra(M, level=1.7)
    notes = [(t, d, m, v, h, tr) for t, d, m, v, h, part, tr in compose() if part != 'voice']
    o.tutti(notes, size=lambda t: 0.7 if t < T_LAUGH else 0.85 if t < T_CODA else 1.0,
            pan=lambda t, m: mid * 0.6)
    for t, d, m in voice():                  # her line: a trumpet, doubled by violins
        o.play('trumpets', m, t, d, 112, her, 0.9)
        o.play('violins', m, t, d, 98, her, 0.4)

    # the staging for the final blaze: timpani driving the coda, cymbals into the great chords, a gong at the last
    o.hit('crash', T_HIGH_C, 112, gain=0.5, pan=her)
    o.hit('timpani roll', T_CODA, 100, pitch=-5, gain=0.45, pan=mid)
    for t0 in CODA:
        o.hit('timpani', t0, 112, pitch=-5, gain=0.45, pan=mid)
    o.hit('cymbal swell', CHORDS[0] - 2.6, 100, gain=0.45, pan=mid)
    for k, t0 in enumerate(CHORDS):
        o.hit('crash', t0, 110 + 4 * k, gain=0.4 + 0.08 * k, pan=mid)
        o.hit('bass drum', t0, 120, gain=0.5, pan=mid)
    o.hit('gong', CHORDS[-1], 120, gain=0.5, pan=mid)
    o.effects([(0.0, -6), (T_LAUGH - 1, -12), (T_HIGH_C - 0.5, -12), (T_HIGH_C, -3), (T_CODA, 0), (D, 0)])
