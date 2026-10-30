"""Heil, Brünnhilde!: the farewell on the summit, and it is ecstatic. They answer each other faster and faster,
and every note of either slams a whole run into its colour, silver for her, emerald for him, and sends a sweep the
length of the house, the runs taking turns until the two colours are tumbling over each other.

The music is Wagner's own: the climax of the duet (bars 573 to 595, "ich bin nur Brünnhildes Arm" to "Vereint faßt
er uns zwei!") and its last pages (bars 622 to 639, the Heils and the start of the orchestra's leave-taking), as
Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py), orchestrated by hand and register. Their voices are not in the reduction, so the
Heils are played from the printed vocal score (Schirmer, archive.org ringofnibelungen00wagn2, pp. 36-37) as
written: hers on trumpets doubled by oboes, his (a tenor, an octave below the page) on horns, answering line by
line, "Heil, strahlende Liebe! Heil, strahlendes Leben!", into the four Heils together and her held high C. A
timpani roll and cymbal swell carry them to it; then, as he leads Grane down off the rock, the horse's hooves go
with him, louder as the effects take over from the voices.

Then the unison: one huge flash of white and gold over every run on her high C, and the two colours burst out
from it, emerald racing over the Side and Left, silver over Right. Then he goes: down off the summit along Porch
Front and out along Porch Right toward the river, emerald streaks shooting out along Right ahead of him to the
free end on the orchestra's accents, while Brünnhilde stays on the summit waving, every wave a pulse of silver
over the house, fainter as he goes.

compose() tags every note of the excerpt; stage(), heat(), fire(), scene(), strand() and figure() are shared word
for word by the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD05'
TITLE = 'Heil, Brünnhilde!'
KIND = 'show'
DESCRIPTION = ('The lovers say goodbye in a blaze of emerald and silver, answering faster and faster until they '
               'sing as one. Then his horn rings out and he leaves the mountain while she waves him away.')
VOICEOVER = ('Hail, Brünnhilde! Hail, Siegfried! One last embrace, and he sets off down the mountain.')

K = 4                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # bars 573-595 and 622-639, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
WHO = {'Siegfried': 's', 'Brünnhilde': 'b'}
LINES = [(t0, t1, WHO[w]) for t0, t1, w, _ in EX['singing'] if w in WHO]
# The Heils, from the vocal score: (who, bar, beat, beats, note), 4/4, sounding pitch (his an octave below the page).
_T = 1 / 3
VOICE = ([('s', 622, 0, 4, 'C4'), ('s', 623, 0, 2, 'C4'), ('s', 623, 2, 1.5, 'F4'), ('s', 623, 3.5, 0.5, 'G4'),
          ('s', 624, 0, 3.5, 'Ab4'), ('s', 624, 3.5, 0.5, 'D4')] +
         [('b', 625, x, n, m) for x, n, m in ((0, 1.5, 'Bb5'), (1.5, .5, 'A5'), (2, .5, 'Ab5'), (2.5, .5, 'G5'),
                                               (3, _T, 'F5'), (3 + _T, _T, 'Eb5'), (3 + 2 * _T, _T, 'D5'))] +
         [('b', 626, 0, 2, 'C5'), ('b', 626, 2, 1, 'Db5')] +
         [('s', 626, x, n, m) for x, n, m in ((0, 2, 'Ab4'), (2, .5, 'G4'), (2.5, .5, 'F4'), (3, .5, 'Eb4'),
                                               (3.5, .5, 'D4'))] + [('s', 627, 0, 2, 'Db4')] +
         [('b', 627, x, n, m) for x, n, m in ((0, 1.5, 'Bb5'), (1.5, .5, 'A5'), (2, .5, 'Ab5'), (2.5, .5, 'G5'),
                                               (3, _T, 'F5'), (3 + _T, _T, 'E5'), (3 + 2 * _T, _T, 'Db5'))] +
         [('b', 628, 0, 2, 'C5'), ('s', 628, 0, 1.5, 'Ab4'), ('s', 628, 1.5, .5, 'G4'), ('s', 628, 2, 1, 'G4'),
          ('s', 628, 3, 1, 'C4')] +
         [('b', 629, 1, 3, 'Eb5'), ('b', 630, 1, 3, 'E5'), ('b', 631, 1, 3, 'Ab5'), ('b', 632, 1, 11, 'C6'),
          ('s', 629, 1, 3, 'G4'), ('s', 630, 1, 3, 'G4'), ('s', 631, 1, 3, 'F4'), ('s', 632, 1, 11, 'Ab4')])
T_TOGETHER = BAR[629]                       # the four Heils together
T_UNISON = BAR[632] + 0.25 * (BAR[633] - BAR[632])   # her high C
T_HORN = [BAR[635], BAR[636], BAR[637], BAR[638], BAR[639]]   # streaks ahead of him as he goes
T_GO = BAR[635]                             # he leads Grane down off the summit
T_THERE = EX['seconds'] - 1.5               # at the head of Porch Right
T_SETTLE = EX['seconds'] - 3.0
D = EX['seconds']

NIGHT = hexc('#1a1070')
NIGHT2 = hexc('#3a1a9a')
STAR = hexc('#e0e8ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
EAST = hexc('#ff2a10')
DAWN = colormap([(0.0, hexc('#ff1040')), (0.35, hexc('#ff6a10')), (0.7, hexc('#ffc020')), (1.0, hexc('#fff4d0'))])
DAY = hexc('#40b0ff')
SUN = hexc('#fff0a0')
NORN = hexc('#c8c8d8')
ROPE = hexc('#ffcc40')
HOT = hexc('#fff4c0')
VALHALLA = hexc('#fff0a0')
GODS = hexc('#1a3cff')
CHORD = hexc('#6a20ff')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BRUNNHILDE = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffaa00')

START = dict(night=0.0, stars=0.0, rock=0.35, fire=0.15, east=0.0, dawn=0.75, hue=0.62, day=0.3, rope=0.0)
END = dict(START)                           # where GD06 picks the morning up
SIEGFRIED_START = ('Porch Front', 0.35, 0.85)   # (segment, u, level)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.9)
SIEGFRIED_END = ('Porch Right', 0.8, 0.85)
BRUNNHILDE_END = BRUNNHILDE_START
RING_ON_HER = 0.55                          # the Ring's glint on her hand: level, 9 units left of her


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky, the east at the free end of Right. The Norns' three places."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same stars, clouds and flames in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, L=float(d.max()), summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        east=(~porch) * np.exp(-((d.max() - d) / 650) ** 2),
        twinkle=Flicker(rng, G.N, 0.3, 2.5),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        fray=Flicker(rng, G.N, 1.5, 6.0),
        norns=[at(G, 'Left', 0.5), summit, at(G, 'Right', 0.5)],
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide=0.0, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def scene(S, T, lv):
    """The sky, the rock, the fire and the standing rope at shared time T with levels lv (night, stars, rock, fire,
    east, dawn, hue, day, rope)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.04 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.07 * T) + 1.1)
    sk = NIGHT + (NIGHT2 - NIGHT) * u[:, None]
    fr = light(sk, lv['night'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(STAR, lv['stars'] * S['sky'] * np.clip(S['twinkle'](T) - 0.9, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(EAST, lv['east'] * S['east'] * (0.8 + 0.2 * u))
    fr += light(DAWN(np.clip(lv['hue'] + 0.2 * (u - 0.5), 0, 1)), lv['dawn'] * (0.8 + 0.2 * u))
    fr += light(DAY + (SUN - DAY) * (0.4 * u)[:, None], lv['day'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'])
    if lv['rope'] > 0:
        a, b = S['norns'][0], S['norns'][2]
        fr += strand(S, a, b, 1.0, lv['rope'], T)
    return fr


def strand(S, a, b, u, lvl, T, fray=0.0):
    """The rope from path distance a toward b, laid u of the way (0..1), shimmering; a white-hot head while it
    flies. fray (0..1) breaks it into flickering gaps."""
    d = S['d']
    head = a + (b - a) * u
    lo, hi = min(a, head), max(a, head)
    on = smoothstep(lo - 8, lo + 8, d) * smoothstep(hi + 8, hi - 8, d)
    shimmer = 0.72 + 0.28 * np.sin(2 * np.pi * (d / 55 - 1.4 * T))
    gaps = np.clip(1 - fray * (0.55 + 0.7 * S['fray'](T)), 0, 1)
    fr = light(ROPE, lvl * on * shimmer * gaps)
    if u < 1:
        fr += light(HOT, min(1.0, 1.3 * lvl + 0.3) * np.exp(-((d - head) / 12) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


PAIRS = [(0, 1), (1, 2), (2, 0)]            # who throws to whom, round and round


def bar_of(t):
    return max([m for m, bt in BAR.items() if bt <= t + 1e-6] or [573])


def voice():
    """The Heils in seconds: (time, seconds, midi, who)."""
    bars = [(m, t) for m, t in EX['bars'] if m >= 622]
    when = lambda pos: float(np.interp(pos, [x[0] for x in bars], [x[1] for x in bars]))
    out = []
    for who, b, x, n, name in VOICE:
        t0, t1 = when(b + x / 4), when(min(b + (x + n) / 4, bars[-1][0]))
        out.append((t0, t1 - t0, note(name), who))
    return out


def compose():
    """Every note, tagged: (time, seconds, midi, velocity, part, k). In the exchange the accompaniment's notes under
    each line are its singer's ('b' or 's', k = the line; k >= 100 from the climax on); the Heils are the voices
    from the vocal score ('b' or 's', k = 'voice'); the rest 'orch'."""
    N = []
    for n in tidy(EX['notes']):
        t, d, m, v, h = n[:5]
        line = next((j for j, (t0, t1, w) in enumerate(LINES) if t0 - 0.1 <= t < t1 and t < BAR[622]), None)
        if line is not None and d >= 0.2 and not n[5]:
            N.append((t, d, m, v, LINES[line][2], line + (100 if bar_of(t) >= 589 else 0)))
        elif bar_of(t) >= 589 and t < BAR[622] and d >= 0.3 and not n[5]:
            N.append((t, d, m, v, 'b' if h == 0 else 's', 100))
        else:
            N.append((t, d, m, v, 'orch', n[5]))
    for t, d, m, who in voice():
        N.append((t, d, m, 104, who, 'voice'))
    return sorted(N, key=lambda e: e[0])


def runs_by_order():
    """The six runs, in path order."""
    return ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']


def walk(G, t):
    """Where Siegfried is: on the summit, then down along Porch Front and out along Porch Right."""
    a, b = at(G, *SIEGFRIED_START[:2]), at(G, *SIEGFRIED_END[:2])
    return a + (b - a) * smoothstep(T_GO, T_THERE, t)


def render(G, seed=5):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_b = at(G, *BRUNNHILDE_START[:2])
    runs = runs_by_order()
    masks = {r: (G.seg_of == r) for r in runs}
    notes = [e for e in N if e[4] in ('b', 's')]
    notes = [(t0, dur, m, v, who, k if isinstance(k, int) else 200) for t0, dur, m, v, who, k in notes]
    horn = sorted({e[0] for e in N if e[4] == 'horn'})
    waves = np.arange(T_GO, T_SETTLE + 4, 1.25)          # her waving

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        dim = keys(t, [(0, 1.0), (2.5, 0.4), (T_TOGETHER, 0.32), (T_UNISON - 0.5, 0.55), (T_UNISON + 2, 0.4),
                       (T_SETTLE, 0.45), (D - 1.0, 1.0)])
        lv = dict(START)
        lv['dawn'] = START['dawn'] * dim
        lv['day'] = START['day'] * dim
        fr = scene(S, T, lv)
        p_s = walk(G, t)

        # every note of either: its whole run slams into the colour, and a sweep runs the length of the house
        for i, (t0, dur, m, v, who, k) in enumerate(notes):
            a = t - t0
            if not 0 <= a < 1.6:
                continue
            col = BRUNNHILDE if who == 'b' else SIEGFRIED
            src = p_b if who == 'b' else p_s
            together = k >= 100
            run = runs[(m + (3 if who == 'b' else 0) + (k % 6)) % 6]
            g = 0.8 + 0.2 * together
            fr += light(col, g * np.exp(-a / (0.3 + 0.2 * min(dur, 1.0))) * masks[run])
            sgn = 1 if (i % 2 == 0) == (who == 'b') else -1
            q = src + sgn * 1800 * a
            fr += light(col, 0.9 * np.exp(-a / 0.7) * np.exp(-((d - q) / 130) ** 2))
            fr += light(WHITE, 0.45 * np.exp(-a / 0.4) * np.exp(-((d - q) / 25) ** 2))

        # together: the house swelling gold-white over the roll
        if T_TOGETHER <= t < T_UNISON:
            u = smoothstep(T_TOGETHER, T_UNISON, t)
            fr += light(SUN, 0.45 * u * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 1.5 * t))))

        # the unison: one huge flash, then emerald bursting over the Side and Left, silver over Right
        if T_UNISON <= t < T_UNISON + 5:
            a = t - T_UNISON
            fr += light(WHITE, 0.95 * np.exp(-a / 0.12))
            fr += light(GOLD, 0.9 * np.exp(-a / 0.6))
            front = 1700 * (1 - np.exp(-a / 0.8))
            left = smoothstep(p_b - front - 80, p_b - front + 80, d) * (d < p_b)
            right = smoothstep(p_b + front + 80, p_b + front - 80, d) * (d >= p_b)
            fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.8) * left)
            fr += light(BRUNNHILDE, 0.95 * np.exp(-a / 1.8) * right)

        # his horn: emerald streaks shooting ahead of him along Right to the free end
        for j, t0 in enumerate(horn):
            a = t - t0
            if 0 <= a < 1.2:
                q = p_s + 1500 * a
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.6) * np.exp(-((d - q) / 60) ** 2) * (d >= p_s - 20))
                fr += light(HEAD, 0.6 * np.exp(-a / 0.4) * np.exp(-((d - q) / 15) ** 2))

        # she waves: a silver pulse out over the house, fainter as he goes
        for j, t0 in enumerate(waves):
            a = t - t0
            if 0 <= a < 1.5:
                g = 0.5 * (1 - smoothstep(T_GO, T_SETTLE + 4, t0)) + 0.45
                g *= 1 - smoothstep(D - 6, D - 2, t)
                r = 1300 * (1 - np.exp(-a / 0.6))
                fr += light(BRUNNHILDE, g * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 140) ** 2))

        # the two of them
        last = max([e[0] for e in notes if e[4] == 's' and e[0] <= t], default=-9)
        ls = SIEGFRIED_START[2] * (1 + 0.25 * np.exp(-(t - last) / 0.2))
        fr = figure(fr, S, p_s, SIEGFRIED, ls)
        fr += light(HEAD, 0.7 * ls * np.exp(-((d - p_s) / 6) ** 2))
        lastb = max([t0 for t0 in waves if t0 <= t], default=-9)
        lb = BRUNNHILDE_START[2] * (1 + 0.15 * np.exp(-(t - lastb) / 0.25) * (t < D - 4))
        fr = figure(fr, S, p_b, BRUNNHILDE, lb)
        fr += light(GLINT, 0.5 * BRUNNHILDE_START[2] * np.exp(-((d - p_b - 9) / 5) ** 2))
        fr += light(GOLD, RING_ON_HER * np.exp(-((d - p_b + 9) / 4) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, the Heils from the vocal score on trumpets, oboes and
    horns, and Grane's hooves as he goes."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    sb = pan_at(at(G, *BRUNNHILDE_START[:2]))
    o = Orchestra(M, level=1.4)

    def size(t):
        return 0.7 if t < BAR[584] else 1.0 if t < BAR[622] else 0.5 if t < T_TOGETHER else 1.0

    o.tutti(tidy(EX['notes']), size=size)
    for t, d, m, who in voice():                                    # the Heils
        if who == 'b':
            o.play('trumpets', m, t, d, 112, sb, 0.85)
            o.play('oboes', m, t, d, 100, sb, 0.45)
        else:
            ps = pan_at(walk(G, t))
            o.play('horns', m, t, d, 112, ps, 0.9)
            o.play('cellos', m, t, d, 90, ps, 0.35)
    o.hit('timpani roll', T_TOGETHER, 100, pitch=-3, gain=0.5)      # carried to her high C
    o.hit('cymbal swell', T_UNISON - 3.8, 100, gain=0.5)
    o.hit('crash', T_UNISON, 120, gain=0.7)
    o.hit('timpani', T_UNISON, 120, pitch=-3, gain=0.8)
    o.hit('crash', BAR[595], 110, gain=0.5)                         # "Vereint faßt er uns zwei!"
    o.hit('timpani', BAR[595], 112, pitch=-3, gain=0.6)
    # Grane's hooves: down off the summit along Porch Front and out along Porch Right with him
    o.gallop(T_GO, D - 0.3, beat=(BAR[636] - BAR[635]) / 2, pan=lambda t: pan_at(walk(G, t)), v=100, gain=0.85)
    # the fader: the voices are the scene; the hooves take over as he goes
    o.effects([(0.0, -16.0), (T_GO - 0.5, -16.0), (T_GO + 0.5, 0.0), (D, 0.0)])
