"""The Norns: night on Brünnhilde's rock. The porch is the rock, its summit the middle of Porch Front, with the
magic fire burning low round it; the wings and the Side are the night sky, deep indigo and violet, alive with
stars. Three great chords in E flat minor slam over the whole house, violet, blue, violet.

The music is Wagner's own: the three awakening chords that open the Prologue (bars 1, 9 and 17, each held as long
as Solti holds it) spliced to the third Norn's prophecy (bars 157 to 176), as Solti's 1958 Vienna Philharmonic
recording takes them. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
chords on the full brass over the basses, with a timpani stroke, a gong and a deep blow under each; Valhalla's
long notes on horns, trombones and tuba; the rushing figures of the fire on violins and flutes, glockenspiel on
their peaks; the rest on the strings. As she sings of the logs piled round the hall and of the fire that will
burn it, the fire round the rock is heard as well as seen, roaring up to the end; it backs off under her lines.

Then the three Norns rise out of the dark, grey white, on the middle of Left, the summit and the middle of Right,
and begin to throw the golden rope of fate between them, one throw on every bar: a white-hot head races from one
Norn to the next, laying a fresh strand of gold the whole way, and when it is caught a gold whip cracks on past
the catcher out to the end of the house. Strand on strand, the rope comes to span the house, shimmering.

The third Norn sings: on every line she flares and grey white rings roll out from her over the house. She sings
of the gods' castle, and every long note of Valhalla slams one whole run in gold white over deep blue; she sings
of the logs heaped round it, of the fire, and every rushing figure of the fire throws a tongue of flame racing out
along the roofline from the rock, left and right in turn, faster and brighter to the end: "der ewigen Götter Ende".

compose() tags every note of the excerpt; stage(), heat(), fire(), scene(), strand() and figure() are the rock,
the sky and the rope, shared word for word by the Prologue's scenes (and GD13-GD14, which come back to the rock)
on a clock T = t + 80 K that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD01'
TITLE = 'The Norns'
KIND = 'show'
DESCRIPTION = ('Night on the rock. Three grey sisters, the Norns, throw a golden rope of fate back and forth across '
               'the whole house, singing of the gods, their castle and the fire.')
VOICEOVER = ('Night, on the mountain. Three sisters spin the rope of fate, and throw it from hand to hand. '
             'This is the Twilight of the Gods.')

K = 0                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # bars 1, 9, 17 and 157-176, Solti 1958
BAR = {int(m): t for m, t in EX['bars'] if m >= 157}
T_CHORDS = [0.0, EX['segments'][1]['start'], EX['segments'][2]['start']]   # the awakening chords
T_PROPHECY = EX['segments'][3]['start']    # the third Norn's prophecy
T_RISE = [16.0, 17.4, 18.8]                 # the Norns rise under the third chord
T_THROWS = [BAR[b] for b in range(157, 177)]   # a throw of the rope on every bar
VALHALLA_BARS = (157, 158, 159, 165, 166, 168)
FIRE_BARS = set(range(160, 165)) | set(range(169, 177))
T_LOGE = sorted([BAR[b] for b in range(160, 165)] + [BAR[b] + 0.5 * (BAR[b + 1] - BAR[b]) for b in range(160, 165)]
                + [BAR[b] for b in range(169, 177)] + [BAR[b] + 0.5 * (BAR[b + 1] - BAR[b]) for b in range(172, 177)])
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

START = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
END = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.5)
NORNS_END = (0.8, 0.8, 0.8)                 # the three Norns' levels at the end (Left 0.5, Porch Front 0.5, Right 0.5)


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
    return max([m for m, bt in BAR.items() if bt <= t + 1e-6] or [0])


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The three chords ('chord', k);
    then Valhalla's long notes ('valhalla'), the fire's rushing figures ('loge'), the rest ('orch'); 'sing' marks
    each of the third Norn's lines (k = 2, the Norn) for the lights and makes no sound."""
    N = []
    for n in tidy(EX['notes']):
        t, d, m, v, h = n[:5]
        if t < T_PROPHECY - 0.01:
            N.append((t, d, m, v, 'chord', min(2, sum(t >= tc - 0.01 for tc in T_CHORDS) - 1)))
            continue
        b = bar_of(t)
        if b in VALHALLA_BARS and d >= 0.5:
            part = 'valhalla'
        elif b in FIRE_BARS and d < 0.25:
            part = 'loge'
        else:
            part = 'orch'
        N.append((t, d, m, v, part, n[5]))
    for t0, t1, who, text in EX['singing']:
        N.append((t0, t1 - t0, 0, 0, 'sing', 2))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=1):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, nn = S['d'], S['L'], S['norns']
    N = compose()
    throws = [t0 for t0 in T_THROWS if t0 <= D - 2.5]
    sing = [e for e in N if e[4] == 'sing']
    vnotes = sorted({e[0] for e in N if e[4] == 'valhalla'})
    runs = ['Porch Front', 'Left', 'Right', 'Porch Left', 'Porch Right', 'Side', 'Left', 'Right']

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['rope'] = 0.5 * smoothstep(throws[0] + 1.0, throws[3] + 1.0, t)
        lv['fire'] += 0.35 * sum(np.exp(-max(t - t0, 0) / 0.8) * (t >= t0) for t0 in T_LOGE)
        fr = scene(S, T, lv)

        # the awakening chords: the whole house slams violet, blue, violet
        for k, t0 in enumerate(T_CHORDS):
            a = t - t0
            if 0 <= a < 2.4:
                col = CHORD if k != 1 else GODS
                fr += light(col, 0.95 * smoothstep(0, 0.05, a) * (1 - smoothstep(1.4, 2.4, a)) * (0.75 + 0.25 * np.exp(-a / 0.4)))
                fr += light(WHITE, 0.5 * np.exp(-a / 0.1))

        # every figure of the rope is a throw: a white-hot head laying fresh gold, then a whip past the catcher
        for j, t0 in enumerate(throws):
            a = t - t0
            if not 0 <= a < 3.0:
                continue
            i, k = PAIRS[j % 3]
            fly = 0.9 + 0.5 * (abs(i - k) == 2)
            u = smoothstep(0, fly, a)
            lvl = 1.0 * np.exp(-max(a - fly, 0) / 0.9)
            fr += strand(S, nn[i], nn[k], u, lvl, T)
            if a >= fly:
                w = a - fly
                out_dir = 1 if nn[k] >= nn[i] else -1
                pos = nn[k] + out_dir * 1900 * w
                past = (out_dir * (d - nn[k]) > 0) * (out_dir * (pos - d) > 0)
                fr += light(ROPE, 1.0 * np.exp(-w / 0.7) * np.exp(-((d - pos) / 110) ** 2))
                fr += light(ROPE, 0.8 * np.exp(-w / 0.9) * past * (0.4 + 0.6 * np.exp(-(out_dir * (pos - d)) / 700)))
                fr += light(HOT, 0.8 * np.exp(-w / 0.12) * np.exp(-((d - nn[k]) / 25) ** 2))

        # Valhalla: every note slams one whole run gold white over deep blue
        for j, t0 in enumerate(vnotes):
            a = t - t0
            if 0 <= a < 1.6:
                run = G.seg_of == runs[j % len(runs)]
                fr += light(GODS, 0.75 * np.exp(-a / 0.9) * S['sky'])
                fr += light(VALHALLA, 1.0 * np.exp(-a / 0.55) * run)

        # Loge: a tongue of flame racing out along the roofline from the rock, left and right in turn
        for j, t0 in enumerate(T_LOGE):
            a = t - t0
            if 0 <= a < 1.8:
                side = -1 if j % 2 == 0 else 1
                start = at(G, 'Porch Left', 0.0) if side < 0 else at(G, 'Porch Right', 1.0)
                pos = start + side * 1300 * (1 - np.exp(-a / 0.5))
                q = np.clip(0.6 + 0.4 * S['fl'](T), 0, 1)
                fr += light(FIRE(q), 1.2 * np.exp(-a / 1.0) * np.exp(-((d - pos) / 220) ** 2))
                fr += fire(S, T, 0.0, 1.0 * np.exp(-a / 0.8), boost=0.6)
                fr += light(AMBER, 0.6 * np.exp(-a / 0.6) * smoothstep(0, 1, side * (d - start) / 50)
                            * smoothstep(pos + side * 40, pos - side * 400, d) * (side * (pos - d) > 0))

        # the Norns: rising, standing, and flaring as each sings, grey white rings rolling out from her
        for n in range(3):
            lvl = 0.8 * smoothstep(T_RISE[n], T_RISE[n] + 1.2, t)
            for t0, dur, m, v, part, who in sing:
                if who == n and 0 <= t - t0 < dur + 0.8:
                    a = t - t0
                    lvl += 0.35 * np.exp(-a / (dur + 0.3))
                    if a < 2.0:
                        r = 900 * (1 - np.exp(-a / 0.6))
                        fr += light(NORN, 0.7 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - nn[n]) - r) / 70) ** 2))
            a = t - T_RISE[n]
            if 0 <= a < 1.5:
                fr += light(NORN, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - nn[n]) - 500 * a) / 50) ** 2))
            if lvl > 0:
                fr = figure(fr, S, nn[n], NORN, min(lvl, 1.1))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the chords' blows and the fire as a production
    would stage them."""
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    nn = [pan_at(p) for p in S['norns']]
    o = Orchestra(M, level=1.15)
    played = set()

    def role(t, d, m, v, h):
        b = bar_of(t)
        if t < T_PROPHECY - 0.01:                                   # the awakening chords: the full brass
            dv = 114 - v                                            # the chords are fortissimo, whatever the reduction says
            return [('horns', 0, dv, 0.8), ('trombones', -12, dv, 0.7), ('tuba', -24, dv, 0.7),
                    ('trumpets', 0, dv - 10, 0.35)] if h == 0 else [('basses', -12, dv, 0.6), ('cellos', -12, dv, 0.5)]
        if b in VALHALLA_BARS and d >= 0.5:                         # Valhalla: horns, trombones, tuba
            return [('horns', 0, 8, 0.8), ('trombones', 0, 0, 0.55), ('tuba', -12, -6, 0.45)]
        if b in FIRE_BARS and d < 0.25:                             # the fire's rushing figures
            parts = [('violins' if m >= 55 else 'violas', 0, 0, 0.55)]
            if m >= 72:
                parts.append(('flutes', 0, -10, 0.35))
            if m >= 79 and (t, m) not in played:
                played.add((t, m))
                parts.append(('glock', -12, -16, 0.25))
            return parts
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 0.8 if t >= BAR[170] else 0.55,
            role=role)
    for k, t0 in enumerate(T_CHORDS):                               # each chord: timpani, gong, a deep blow
        o.hit('timpani', t0, 120, pitch=-5, gain=0.8)
        o.hit('gong', t0 + 0.02, 100 + 8 * k, gain=0.45)
        o.boom(t0, 0.0, 0.7)
    for n, t0 in enumerate(T_RISE):                                 # the Norns rising: a roll under each
        o.hit('timpani roll', t0 - 0.6, 80, pitch=-6, gain=0.35, pan=nn[n])
    # the fire round the rock: low under the prophecy, leaping with each tongue of flame, roaring to the end
    leap = np.array(T_LOGE)
    o.fire(BAR[160] - 1.0, D, level=lambda tt: np.clip(0.25 + 0.45 * smoothstep(BAR[169], D - 2, tt) + 0.5 * np.sum(
        np.exp(-np.clip(tt[:, None] - leap[None, :], 0, None) / 0.5) * (tt[:, None] >= leap[None, :]), axis=1)
        * 0.6, 0, 1), pan=0.0, crackle=14.0)
    for j, t0 in enumerate(T_LOGE):                                 # each tongue of flame: a rush out from the rock
        side = -0.7 if j % 2 == 0 else 0.7
        n = int(0.7 * SR)
        o._sfx(o._noise(0, 200, 3000, 77 + j, n=n) * np.exp(-np.arange(n) / (0.18 * SR)), t0, 0.35, side)
    # the fader: the chords' blows lead; under her lines the fire backs off; it takes the stage at the end
    o.effects([(0.0, 0.0), (T_PROPHECY - 1.0, 0.0), (T_PROPHECY + 1.0, -12.0), (BAR[169], -10.0),
               (BAR[173], -5.0), (D - 3.0, -2.0), (D, -2.0)])
