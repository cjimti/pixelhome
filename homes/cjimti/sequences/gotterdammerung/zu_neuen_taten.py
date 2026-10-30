"""Zu neuen Taten: full morning on Brünnhilde's rock, and Siegfried must go out to new deeds. Brünnhilde sends him
with her song, "Zu neuen Taten, teurer Helde": each long note of it swells a whole run silver, the short ones throw
gold glints, and her silver rolls out over the house.

The music is Wagner's own: the start of the duet (bars 362 to 373) and the exchange of the Ring for her horse
(bars 501 to 529), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and register. Her voice is not in the
reduction, so the line she sings, "Zu neuen Taten, teurer Helde, wie liebt' ich dich, ließ' ich dich nicht?",
comes from the printed vocal score (Schirmer, archive.org ringofnibelungen00wagn2, p. 21) and is played as written
on oboes doubled by violins. Under the Ring the woodwinds glint; his dragon-slaying pounds on horns, trombones and
tuba; when she gives him Grane her horse is heard, galloping off along the house, with a cymbal and gong as the
Ring reaches her. The effects keep clear of her song.

Then the gift. "Zum Tausche deiner Runen reich' ich dir diesen Ring": a ring of gold light leaves Siegfried's hand
and travels across the summit to her, pulsing on every note; when it reaches her the whole house flashes gold, and
a gold loop races round the roofline both ways and meets itself. He tells of the dragon he killed for it, and every
pounding note of it is an emerald wave out from him, one run after another flashing green, then emerald and
silver trading whole runs. In return she gives him her horse Grane: the gallop is light, great rhythmic sweeps of
silver and white thundering along the house on every beat, faster and wider each time, from her end out to the free
end of Right and back, and it settles into the bright morning with the two of them on the summit, the Ring
glinting on her hand.

compose() tags every note of the excerpt; stage(), heat(), fire(), scene(), strand() and figure() are shared word
for word by the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD04'
TITLE = 'Zu neuen Taten'
KIND = 'show'
DESCRIPTION = ('Siegfried must ride out to new adventures. He gives Brünnhilde the Ring as a pledge, a gold flash '
               'that races round the house, and she gives him her horse Grane, galloping in silver sweeps.')
VOICEOVER = ('A hero has to go out into the world. He leaves her the Ring, and she gives him her horse.')

K = 3                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # bars 362-373 and 501-529, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
# Her song, from the vocal score: (bar, beat, beats, note), 4/4.
VOICE = [(362, 1, 1, 'Ab4'), (362, 2, 1.5, 'F5'), (362, 3.5, 0.5, 'C5'), (363, 0, 2, 'Eb5'), (363, 2, 1, 'F4'),
         (364, 1, 2.5, 'C5'), (364, 3.5, 0.5, 'Bb4'), (365, 0, 2, 'Ab4'), (365, 2, 1, 'G4'), (366, 1, 3, 'C5'),
         (367, 0, 1.5, 'C5'), (367, 1.5, 0.5, 'Eb4'), (367, 2, 2, 'Eb4'), (368, 1, 2, 'G4'), (368, 3, 0.5, 'F4'),
         (368, 3.5, 0.5, 'Eb4'), (369, 0, 2, 'F4')]
T_RING = BAR[501]                           # "reich' ich dir diesen Ring": the gift leaves his hand
T_GIVEN = BAR[504]                          # it reaches her: the gold flash
HERO_BARS = [range(504, 517), range(517, 524)]   # his deeds and the dragon he killed; then the full brass
GALLOP_BARS = range(524, 530)               # Grane
T_GRANE = [BAR[b] for b in (524, 526, 528)]
T_SETTLE = BAR[528]
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
END = dict(START)                           # where GD05 picks the morning up
SIEGFRIED_START = ('Porch Front', 0.35, 0.85)   # (segment, u, level)
BRUNNHILDE_START = ('Porch Front', 0.6, 0.9)
SIEGFRIED_END = SIEGFRIED_START
BRUNNHILDE_END = BRUNNHILDE_START
RING_ON_HER = 0.55                          # the Ring's glint on her hand at the end: level, 9 units left of her


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
    return max([m for m, bt in BAR.items() if bt <= t + 1e-6] or [362])


def voice():
    """Her song in seconds: (time, seconds, midi)."""
    out = []
    for b, x, n, name in VOICE:
        t0 = float(np.interp(b + x / 4, [m for m, _ in EX['bars'][:13]], [t for _, t in EX['bars'][:13]]))
        t1 = float(np.interp(b + (x + n) / 4, [m for m, _ in EX['bars'][:13]], [t for _, t in EX['bars'][:13]]))
        out.append((t0, t1 - t0, note(name)))
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Her song ('love', from the vocal
    score); the right hand as the Ring passes to her ('ring'); the left hand's pounding as he tells of the dragon
    and then the full brass ('hero', k = which); Grane's gallop in the left hand ('gallop') and the right hand over
    it ('grane'); the rest 'orch'."""
    N = [(t, d, m, 100, 'love', 'song') for t, d, m in voice()]
    for n in tidy(EX['notes']):
        t, d, m, v, h = n[:5]
        b = bar_of(t)
        if 370 <= b < 374 and h == 0 and d >= 0.3:                 # her next line: its accompaniment carries it
            N.append((t, d, m, v, 'love', 'orch'))
            part, k = 'orch', n[5]
        elif 501 <= b < 504 and h == 0:
            part, k = 'ring', None
        elif b in HERO_BARS[0] and (h == 1 or d >= 0.3):
            part, k = 'hero', 0
        elif b in HERO_BARS[1] and h == 1 and d >= 0.3:
            part, k = 'hero', 1
        elif b in GALLOP_BARS and h == 1:
            part, k = 'gallop', None
        elif b in GALLOP_BARS:
            part, k = 'grane', None
        else:
            part, k = 'orch', n[5]
        N.append((t, d, m, v, part, k))
    return sorted(N, key=lambda e: e[0])


def runs_by_order():
    """The six runs, in path order."""
    return ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']


def render(G, seed=4):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_s, p_b = at(G, *SIEGFRIED_START[:2]), at(G, *BRUNNHILDE_START[:2])
    hero = [e for e in N if e[4] == 'hero']
    love = [e for e in N if e[4] == 'love']
    ring_on = sorted({e[0] for e in N if e[4] == 'ring'})
    gallop = sorted({round(e[0], 2) for e in N if e[4] == 'gallop'})
    grane = [e for e in N if e[4] == 'grane']
    runs = runs_by_order()
    masks = {r: (G.seg_of == r) for r in runs}
    hero_on = [sorted({e[0] for e in hero if e[5] == k}) for k in range(2)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        dim = keys(t, [(0, 1.0), (3.0, 0.42), (T_RING - 0.5, 0.42), (T_RING + 1, 0.22), (T_GIVEN, 0.22),
                       (T_GIVEN + 1.5, 0.45), (T_SETTLE, 0.45), (D - 1.0, 1.0)])
        lv = dict(START)
        lv['dawn'] = START['dawn'] * dim
        lv['day'] = START['day'] * dim
        fr = scene(S, T, lv)

        # his heroism: an emerald wave out from him on every note, and the runs flashing green one after another
        for k in range(2):
            for j, t0 in enumerate(hero_on[k]):
                a = t - t0
                if not 0 <= a < 2.0:
                    continue
                r = 1500 * (1 - np.exp(-a / 0.7))
                g = 0.95 + 0.15 * k
                fr += light(SIEGFRIED, g * np.exp(-a / 0.9) * np.exp(-((np.abs(d - p_s) - r) / 170) ** 2))
                run = runs[(j * (2 + k)) % 6]
                col = SIEGFRIED if (k == 0 or j % 2 == 0) else BRUNNHILDE
                fr += light(col, (0.8 + 0.2 * k) * np.exp(-a / 0.4) * masks[run])

        # her love: each long note swells a whole run silver, the short ones throw gold glints, silver rolls out
        for j, (t0, dur, m, v, part, k) in enumerate(love):
            a = t - t0
            if not 0 <= a < dur + 1.5:
                continue
            env = smoothstep(0, 0.12, a) * np.exp(-max(a - dur, 0) / 0.5)
            if dur >= 0.9:
                fr += light(BRUNNHILDE, 0.9 * env * masks[runs[(m * 5) % 6]] * (0.8 + 0.2 * np.sin(4 * a)))
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(BRUNNHILDE, 0.85 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_b) - r) / 150) ** 2))
            else:
                q = p_b + ((m * 97) % 900 - 450)
                fr += light(GLINT, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - q) / 45) ** 2))

        # the gift: a ring of gold light travelling from his hand to hers, on every note of the Ring a pulse
        if T_RING <= t < T_GIVEN + 0.2:
            u = smoothstep(T_RING, T_GIVEN, t)
            q = p_s + (p_b - p_s) * u
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.25) if j >= 0 else 0.0
            ring = np.exp(-((np.abs(d - q) - 10 - 6 * pulse) / 4) ** 2)
            fr += light(GOLD, (0.9 + 0.3 * pulse) * ring)
            fr += light(GOLD, 0.35 * pulse * np.exp(-((d - q) / 220) ** 2))
            fr += light(RED, 0.2 * pulse * np.exp(-((d - q) / 40) ** 2))
        # it reaches her: the whole house flashes gold, a gold loop races round both ways
        if T_GIVEN <= t < T_GIVEN + 4.0:
            a = t - T_GIVEN
            fr += light(GOLD, 0.95 * np.exp(-a / 0.6))
            fr += light(SUN, 0.7 * np.exp(-a / 0.15))
            for sgn in (-1, 1):
                q = p_b + sgn * 900 * a
                fr += light(GOLD, np.exp(-a / 1.6) * np.exp(-((d - q) / 90) ** 2))
                fr += light(HOT, 0.8 * np.exp(-a / 1.6) * np.exp(-((d - q) / 18) ** 2))

        # Grane: the gallop, every hoofbeat a sweep of silver and white thundering along the house
        for i, t0 in enumerate(gallop):
            a = t - t0
            if not 0 <= a < 1.3:
                continue
            k = min(3, int(np.searchsorted(T_GRANE, t0, side='right')))
            sgn = 1 if i % 2 == 0 else -1
            start = p_b if sgn > 0 else L
            q = start + sgn * (1300 + 300 * k) * a
            w = 110 + 50 * k
            fr += light(BRUNNHILDE, (0.95 + 0.1 * k) * np.exp(-a / 0.6) * np.exp(-((d - q) / w) ** 2))
            fr += light(WHITE, 0.55 * np.exp(-a / 0.3) * np.exp(-((d - q) / (w / 3)) ** 2))
            fr += light(DAY, 0.35 * np.exp(-a / 0.2) * masks[runs[(i + 3) % 6]])
        for t0, dur, m, v, part, k in grane:
            a = t - t0
            if 0 <= a < 0.5 and dur >= 0.5:
                fr += light(GLINT, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - p_b) / 160) ** 2))

        # settling: the two answer each other in great breaths of emerald and silver over the house, and the
        # Ring glints chase out from her hand
        for j, t0 in enumerate(np.arange(T_SETTLE, D - 3.0, 2.4)):
            a = t - t0
            if 0 <= a < 2.4:
                p, col = (p_s, SIEGFRIED) if j % 2 == 0 else (p_b, BRUNNHILDE)
                g = 0.85 * (1 - smoothstep(D - 6, D - 2, t))
                r = 1400 * (1 - np.exp(-a / 0.9))
                fr += light(col, g * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p) - r) / 220) ** 2))
                fr += light(GOLD, g * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - 1.3 * r) / 30) ** 2))

        # the two of them on the summit; she wears the Ring from the moment it reaches her
        hit = max([t0 for t0 in hero_on[0] + hero_on[1] if t0 <= t], default=-9)
        ls = SIEGFRIED_START[2] * (1 + 0.25 * np.exp(-(t - hit) / 0.2))
        fr = figure(fr, S, p_s, SIEGFRIED, ls)
        fr += light(HEAD, 0.7 * ls * np.exp(-((d - p_s) / 6) ** 2))
        lb = BRUNNHILDE_START[2]
        fr = figure(fr, S, p_b, BRUNNHILDE, lb)
        fr += light(GLINT, 0.5 * lb * np.exp(-((d - p_b - 9) / 5) ** 2))
        if t >= T_GIVEN:
            fr += light(GOLD, RING_ON_HER * smoothstep(T_GIVEN, T_GIVEN + 0.5, t) * np.exp(-((d - p_b + 9) / 4) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, her song from the vocal score on oboes and violins, and
    Grane's hooves as she gives him her horse."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    sb = pan_at(at(G, *BRUNNHILDE_START[:2]))
    ss = pan_at(at(G, *SIEGFRIED_START[:2]))
    o = Orchestra(M, level=2.25)
    N = compose()
    tag = {(round(e[0], 4), e[2]): e[4] for e in N}

    def size(t):
        return 0.4 if t < T_RING else 0.75 if t < BAR[509] else 1.0

    def role(t, d, m, v, h):
        part = tag.get((round(t, 4), m), 'orch')
        if t < T_RING:                                              # under her song: strings, softly
            return [('violins' if m >= 55 else 'violas' if m >= 48 else 'cellos', 0, -10, 0.45)]
        if part == 'ring':                                          # the Ring: woodwinds glinting
            return [('flutes' if m >= 67 else 'clarinets', 0, 0, 0.5), ('violins', 0, -12, 0.3)]
        if part == 'hero' and t >= BAR[509]:                        # the dragon he killed: horns, trombones, tuba
            if m < 45:
                return [('tuba', 0, 0, 0.6), ('basses', 0, -4, 0.5), ('trombones', 12, -6, 0.5)]
            return [('horns', 0, 4, 0.8), ('trombones', 0, -4, 0.55)]
        if part == 'gallop':                                        # Grane's gallop: low strings and bassoons
            return [('cellos', 0, 4, 0.6), ('bassoons', 0, -6, 0.4)]
        return None

    o.tutti(tidy(EX['notes']), size=size, role=role)
    for t, d, m, v, part, k in N:                                   # her song: oboes doubled by violins
        if part == 'love' and k == 'song':
            o.play('oboes', m, t, d, 104, sb, 0.8)
            o.play('violins', m, t, d, 92, sb, 0.45)
    for k, (t0, t1) in enumerate(((BAR[501], BAR[502]), (BAR[502], BAR[504]))):   # the ring passing: glints
        o.hit('triangle', t0 + 0.2, 80 + 10 * k, gain=0.3, pan=ss + (sb - ss) * (0.3 + 0.4 * k))
    o.hit('crash', T_GIVEN, 112, gain=0.6, pan=sb)                  # it reaches her
    o.hit('gong', T_GIVEN + 0.02, 100, gain=0.4, pan=sb)
    # Grane: his hooves, galloping out from her end to the free end of Right and back
    beat = (BAR[525] - BAR[524]) / 4                                 # a hoofbeat a quarter note
    for j, t0 in enumerate(T_GRANE):
        t1 = T_GRANE[j + 1] if j + 1 < len(T_GRANE) else D
        a, b = (sb, 0.85) if j % 2 == 0 else (0.85, sb)
        o.gallop(t0, t1 - 0.2, beat=beat, pan=lambda t, t0=t0, t1=t1, a=a, b=b: a + (b - a) * (t - t0) / (t1 - t0),
                 v=104 + 6 * j, gain=0.9)
    # the fader: well down under her song and his telling; up for the gift and for Grane
    o.effects([(0.0, -14.0), (T_RING - 0.5, -14.0), (T_RING, -6.0), (T_GIVEN + 2.0, -6.0), (BAR[509], -12.0),
               (T_GRANE[0] - 0.5, -12.0), (T_GRANE[0], 0.0), (D, 0.0)])
