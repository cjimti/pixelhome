"""Through the Fire: the storm is thinning; the fire rings the rock on the porch and Siegfried stands at Right 0.6
looking up at it.

The music is Wagner's own: "Jetzt lock' ich ein liebes Gesell!" and his horn call (bars 768 to 771), the fire music
of the transformation as he plunges through the flames (bars 778 to 793), and the calm at the summit where the
magic sleep sounds (bars 822 to 825), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from
the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): his horn call on the horns, the fire's racing
figures on violins and harp with flutes and piccolo flickering on top, his motifs blazing through it on horns,
trombones and trumpets, the bass on cellos, basses and tuba, and the sleep's chords on clarinets, flutes and
bassoons. Like a staged production it adds the fire itself: a low crackle round the rock, a roaring rush as he
plunges in, the blaze's roar and crackle riding under the orchestra (pulled back so the music leads), and only
embers under the sleep.

He puts his horn to his lips and every note of the call throws an emerald sweep out to both ends of the house.
Then he plunges in, and the fire comes out to meet him: the flames roar out from the porch along both wings and
down the Side until every run is burning, red at the roots, orange and gold at the tips, licking both ways; each
of the fire's racing figures throws a white-gold tongue leaping along the roofline and its high flicker scatters
sparks. Through it Siegfried runs as an emerald comet with a white-hot head, the flames parting round him and
closing behind, up round the porch toward the summit; every time his motif blazes in the brass the whole fire
leaps gold. He comes out at the top. The fire sinks back to a ring round the rock, the storm is gone and the sky
calms to a deep still blue, and at the summit a silver glow wakes in the middle of the flames: every chord of the
magic sleep a violet ripple out from the sleeper, and Siegfried stands beside her.

compose() tags every note of the excerpt; stage(), sky(), figure() and fire() are the rock and the sky, shared
word for word by Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF26'
TITLE = 'Through the Fire'
KIND = 'show'
DESCRIPTION = ('Siegfried blows his horn and plunges into the magic fire. The flames roar out over the whole house '
               'as he runs through them, and when they sink back he is standing at the top beside a sleeping figure.')
VOICEOVER = ('He knows no fear, so he walks straight into the fire. '
             'And at the top of the mountain, someone is sleeping.')

K = 3                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 768-772, 778-794 and 822-826, Solti 1958
NOTES = tidy(EX['notes'])
D = EX['seconds']
T_PLUNGE = EX['segments'][1]['start']       # into the fire
T_SLEEP = EX['segments'][2]['start']        # the summit: the magic sleep
HORN = [n for n in EX['notes'] if n[4] == 0 and 6.5 <= n[0] < T_PLUNGE - 0.05]    # his horn call
T_ROAR = (T_PLUNGE, T_PLUNGE + 6.0)         # the fire spreading out over the house
LOGES = accents(EX['notes'], T_PLUNGE, T_SLEEP - 0.5, vmin=110, n=2, space=0.7)   # the fire's racing figures
FLICKS = [n[0] for n in EX['notes'] if n[4] == 0 and n[2] >= 84 and T_PLUNGE <= n[0] < T_SLEEP]
SIEG = accents([n for n in EX['notes'] if n[4] == 1 and n[1] >= 1.0], T_PLUNGE, T_SLEEP, vmin=100, n=2,
               space=1.5)                   # his motif blazing in the brass
T_TOP = T_SLEEP - 3.0                       # he comes out at the summit
T_SINK = (T_SLEEP - 6.0, T_SLEEP + 3.0)     # the fire sinking back to a ring
SLEEPS = accents(EX['notes'], T_SLEEP, D, vmin=1, n=1, space=1.2)     # the magic sleep's chords

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
GOLD = hexc('#ffd060')
SPARK = hexc('#fff0b0')
VIOLET = hexc('#7a6aff')

START = dict(storm=0.4, rock=0.3, fire=0.6, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF25 left it
END = dict(storm=0.25, rock=0.35, fire=0.4, wide=0.0, dawn=0.0, sleeper=0.7)        # SUMMIT, where SF27 begins
FROM = ('Right', 0.6)
TOP = ('Porch Front', 0.35)


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
    """Every note of the excerpt, tagged (time, seconds, midi, velocity, part, tremolo): his horn call ('horn'), the
    fire's figures ('fire'), his motif in the brass ('sieg'), the bass ('bass') and the magic sleep ('sleep')."""
    N = []
    for t, d, m, v, h, trem in NOTES:
        if t >= T_SLEEP - 0.01:
            part = 'sleep'
        elif t < T_PLUNGE - 0.01:
            part = 'horn' if h == 0 else 'bass'
        elif h == 0:
            part = 'fire'
        else:
            part = 'sieg' if d >= 1.0 and m >= 48 else 'bass'
        N.append((t, d, m, v, part, trem))
    return sorted(N, key=lambda e: e[0])


def hero(G, t):
    """Where Siegfried is at time t: from the foot of the rock up round the porch to the summit."""
    a, b = at(G, *FROM), at(G, *TOP)
    return a + (b - a) * smoothstep(T_PLUNGE, T_TOP, t)


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    leaps = [(t0, rng.uniform(0, L), rng.choice([-1, 1])) for t0 in LOGES]
    spark_at = rng.uniform(0, L, len(FLICKS))
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    from_porch = np.clip(np.maximum(p0 - d, d - p1), 0, None)
    summit = S['summit']

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_SINK[0], START[k]), (T_SINK[1], END[k])]) for k in START}
        lv['storm'] = keys(t, [(0, START['storm']), (T_PLUNGE, 0.3), (T_SINK[1], END['storm'])])
        lv['sleeper'] = END['sleeper'] * smoothstep(T_TOP + 1, T_SLEEP + 6, t)
        roar = smoothstep(T_ROAR[0], T_ROAR[1], t) * (1 - smoothstep(T_SINK[0], T_SINK[1], t))
        lv['fire'] += 0.35 * roar + 0.2 * (t < T_PLUNGE) * smoothstep(6.5, T_PLUNGE, t)
        fr = sky(S, T, lv)
        ps = hero(G, t)

        # the fire roars out from the porch over every run, then sinks back to the ring
        reach = 1700 * smoothstep(T_ROAR[0], T_ROAR[1], t) * (1 - smoothstep(T_SINK[0], T_SINK[1], t))
        if reach > 1:
            mask = smoothstep(reach + 80, reach - 80, from_porch) * S['sky']
            boost = sum(np.exp(-(t - x) / 0.5) for x in SIEG if 0 <= t - x < 2.5)
            flame = fire(S, T, 0.0, 1.0, boost=0.35 + boost)
            fr += flame * mask[:, None]
            front = np.exp(-((from_porch - reach) / 60) ** 2) * S['sky'] * (reach < 1650)
            fr += light(AMBER, 0.8 * front)

        # each of the fire's racing figures: a white-gold tongue leaping along the roofline
        for t0, x0, sgn in leaps:
            a = t - t0
            if 0 <= a < 1.2:
                c = x0 + sgn * 700 * a
                fr += light(SPARK, 1.0 * roar * np.exp(-a / 0.5) * np.exp(-((d - c) / 45) ** 2))
                fr += light(AMBER, 0.85 * roar * np.exp(-a / 0.6) * np.exp(-((d - c + sgn * 90) / 110) ** 2))
        for j, x in enumerate(FLICKS):          # its high flicker: sparks of white-gold
            a = t - x
            if 0 <= a < 0.4:
                fr += light(SPARK, 0.8 * roar * np.exp(-a / 0.1) * np.exp(-((d - spark_at[j]) / 6) ** 2))

        # his motif in the brass: the whole fire leaps gold
        for k, x in enumerate(SIEG):
            a = t - x
            if 0 <= a < 0.9:
                fr += light(GOLD, 1.0 * np.exp(-a / 0.4) * (0.6 + 0.4 * heat(d, T)))
                fr += light(SPARK, 0.6 * np.exp(-a / 0.15))
                fr += light(EMERALD, 0.8 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - ps) - 1800 * a) / 120) ** 2))

        # his horn call: emerald sweeps out to both ends on every note
        for t0, dur, m, v, h in HORN:
            a = t - t0
            if 0 <= a < 1.2:
                src = hero(G, t0)
                fr += light(EMERALD, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - src) - 1800 * a) / 110) ** 2))
                fr += light(EMERALD, 0.8 * np.exp(-a / 0.25) * np.exp(-((d - src) / 70) ** 2))

        # the magic sleep: violet ripples out from the sleeper on every chord
        for t0 in SLEEPS:
            a = t - t0
            if 0 <= a < 3.0:
                fr += light(VIOLET, 0.75 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - summit) - 450 * a) / 90) ** 2))

        # Siegfried: an emerald comet with a white-hot head; the flames part round him
        if T_PLUNGE <= t < T_TOP + 1:
            near = np.exp(-((d - ps) / 60) ** 2)
            fr = fr * (1 - 0.6 * near)[:, None]
            tail = np.exp(-np.clip(d - ps, 0, None) / 120) * (d >= ps)
            fr += light(EMERALD, 0.7 * tail)
        fr = figure(fr, S, ps, EMERALD, 0.85)
        fr += light(HERO_HEAD, 0.8 * np.exp(-((d - ps) / 5) ** 2))
        if T_PLUNGE <= t < T_PLUNGE + 0.8:
            a = t - T_PLUNGE
            fr += light(SPARK, 0.9 * np.exp(-a / 0.15) * np.exp(-((d - ps) / 80) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the fire's own sound ridden under the music."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.4)
    part = {(e[0], e[2]): e[4] for e in compose()}

    def role(t, d, m, v, h):
        p = part.get((t, m))
        if p == 'horn':                                     # his horn call, on the horns
            return [('horns', -12, 6, 0.95), ('horns', -24, -6, 0.4)]
        if p == 'fire' and d < 0.3:                         # the fire's racing figures: violins and harp
            out = [('violins', 0, -4, 0.5), ('harp', -12, 0, 0.35)]
            if m >= 84:
                out.append(('piccolo', -12, -10, 0.35))
            return out
        if p == 'sleep':                                    # the magic sleep: clarinets, flutes, bassoons
            return ([('clarinets', 0, 18, 0.65), ('flutes', 0, 10, 0.4)] if m >= 55 else
                    [('bassoons', 0, 18, 0.55), ('cellos', 0, 10, 0.4)])
        return None

    o.tutti(NOTES, size=lambda t: 1.0 if T_PLUNGE <= t < T_SINK[1] else 0.6, role=role,
            pan=lambda t, m: pan_at(hero(G, t)) * 0.6)

    # the fire's own sound: a low crackle round the rock, a rush as he plunges in, the blaze riding under the
    # orchestra so the music leads, and embers under the sleep
    o.effects([(0.0, -12), (T_PLUNGE - 0.4, -12), (T_PLUNGE, 1), (T_PLUNGE + 2.5, -5), (T_SINK[0], -5),
               (T_SLEEP, -12), (D, -15)])
    blaze = lambda tt: 0.25 + 0.75 * smoothstep(T_ROAR[0], T_ROAR[1], tt) * (1 - 0.75 * smoothstep(T_SINK[0], T_SINK[1], tt))
    o.fire(0.0, D, level=blaze, pan=-0.5, crackle=14, seed=21)
    o.fire(0.0, D, level=blaze, pan=0.5, crackle=14, seed=23)
    from pixelhome.audio import whoosh
    pp = pan_at(hero(G, T_PLUNGE))
    o.M.add('fx', whoosh(1.6, 200, 3000, 0.9, seed=4), T_PLUNGE - 0.3, 1.0, pp)    # he plunges in: a roaring rush
    o.boom(T_PLUNGE, pp, 0.9)
    o.hit('crash', T_PLUNGE, 118, gain=0.5, pan=pp)
    for x in SIEG:                                         # the fire leaping gold with his motif
        o.hit('cymbal swell', x - 1.8, 90, gain=0.25)
    o.hit('triangle', T_SLEEP + 0.3, 70, gain=0.3, pan=pan_at(at(G, *TOP)))     # the sleeper
