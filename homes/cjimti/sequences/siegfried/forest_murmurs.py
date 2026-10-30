"""Forest Murmurs: broad day outside Fafner's cave, and Siegfried lying under the lime tree at Left 0.5.

The music is Wagner's own: the Forest Murmurs from Act II, their beginning (bars 763 to 771) and then the forest
in full voice with the Woodbird singing in it (830 to 855), as Solti's 1958 Vienna Philharmonic recording takes
them. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the murmuring figures on
muted violas and cellos over the horns' low E, the violins' rising delight, the Woodbird's calls on flute, oboe and
clarinet as Wagner gives them, and the forest's great swells on horns and violins. A production adds the
forest's own sound: the leaves stirring, rising with each swell and falling back so the bird is clear.

The whole house is the forest, alive: every bar of the Murmurs sends a green and gold wave rolling the length of
the roofline, one way and then the other, the waves crossing and flashing where they meet, while the sun shafts
drift through the trees. The violins' delight sparkles as gold glitter round him over Left and Side. Then from
the far end of the house a hot magenta point flicks into the trees: the Woodbird. On every note of its song it
darts a hop along the roofline, white at its heart, trailing magenta, wings flickering, and the first note of
each call sends a magenta ring out through the green. Each time the forest swells to fortissimo the whole house
blooms green and gold, and at the end the bird settles at Right 0.3 and looks at him.

compose() tags every note of the excerpt; stage(), forest(), figure() and sparks() are the forest and the cave,
shared word for word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF15'
TITLE = 'Forest Murmurs'
KIND = 'show'
DESCRIPTION = ('Siegfried lies under a tree and the whole forest comes alive in rolling waves of green and gold. '
               'A magenta bird darts through the branches, singing to him.')
VOICEOVER = ('Siegfried lies under a linden tree and listens to the forest. '
             'A little bird is singing to him.')

K = 4                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 763-771 and 830-855, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_MURMUR = [t for m, t in EX['bars'] if t < D - 1.0]    # every bar of the Murmurs rolls a wave
T_DELIGHT = (BAR[770], BAR[772])            # the violins' rising delight
T_BIRD_IN = BAR[833] + 0.6                  # the Woodbird flicks in at the free end of Right
T_SETTLE = D - 1.0

NIGHT = hexc('#14a878')
MOON = hexc('#6080ff')
DAY = hexc('#18a020')
SUN = hexc('#ffd040')
CAVE = hexc('#8a2000')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STONE = hexc('#8a8a80')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BIRD = hexc('#ff30d0')

START = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)        # where SF14 left the forest: day
END = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)          # where SF16 picks it up
TREE_AT = 0.5                               # the lime tree, on Left
BIRD_AT = 0.3                               # where the Woodbird settles, on Right


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The forest outside Fafner's cave as profiles over the house: the porch is the cave mouth (darkest at the
    back, the middle of Porch Front), Left, Right and Side the trees, with two eyes on Porch Front."""
    d = G.pd
    rng = np.random.default_rng(1857)       # the same trees and light in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    mid = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, mid=mid, porch=porch,
        trees=(~porch) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        mouth=porch * (0.35 + 0.65 * np.exp(-((d - mid) / 160) ** 2)),
        eyes=np.exp(-((d - at(G, 'Porch Front', 0.4)) / 5) ** 2) + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 5) ** 2),
        edge=porch * (1 - np.exp(-((d - mid) / 220) ** 2)),
        shaft_at=rng.uniform(0, d.max(), 9), shaft_v=rng.uniform(-14, 14, 9), shaft_w=rng.uniform(25, 60, 9),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        smoulder=Flicker(rng, G.N, 0.3, 1.5),
    )


def forest(S, T, lv):
    """The forest at shared time T with levels lv (night, day, shafts, cave, eyes)."""
    d, leaf = S['d'], S['leaf'](T)
    fr = light(NIGHT, lv['night'] * S['trees'] * (0.85 + 0.15 * leaf))
    fr += light(DAY, lv['day'] * S['trees'] * (0.8 + 0.2 * leaf))
    fr += light(NIGHT, 0.4 * (lv['night'] + lv['day']) * S['edge'])
    L = d.max()
    shafts = np.zeros_like(d)
    for p, v, w in zip(S['shaft_at'], S['shaft_v'], S['shaft_w']):
        c = (p + v * T) % L
        shafts += np.exp(-((d - c) / w) ** 2)
    shafts *= ~S['porch']
    fr += light(MOON, lv['shafts'] * (1 - min(1.0, 2 * lv['day'])) * shafts)
    fr += light(SUN, lv['shafts'] * min(1.0, 2 * lv['day']) * shafts)
    fr += light(CAVE, lv['cave'] * S['mouth'] * (0.75 + 0.25 * S['smoulder'](T)))
    fr += light(EYE, lv['eyes'] * S['eyes'])
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the forest, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). 'delight' is the violins' rising
    figure, 'song' a note of the Woodbird's calls, 'call' the first note of each call, 'swell' a fortissimo surge,
    'murmur' everything else."""
    N = []
    notes = sorted(EX['notes'])
    song = [n for n in notes if n[4] == 0 and n[2] >= 76 and n[1] < 1.0 and n[0] >= T_BIRD_IN - 0.1 and n[3] < 110]
    firsts = accents([(n[0], n[1], n[2], n[3]) for n in song], n=1, space=2.0)
    for t, d, m, v, h in notes:
        if v >= 110:
            part = 'swell'
        elif T_DELIGHT[0] <= t < T_DELIGHT[1] and h == 0 and d < 1.0:
            part = 'delight'
        elif [t, d, m, v, h] in song:
            part = 'call' if any(abs(t - x) < 0.02 for x in firsts) else 'song'
        else:
            part = 'murmur'
        N.append((t, d, m, v, part, None))
    return N


def bird_hops(G):
    """Where the Woodbird lands on each note of its song and call: [(time, place)]."""
    L = G.pd.max()
    rng = np.random.default_rng(27)
    song = sorted({round(t, 2) for t, d, m, v, part, k in compose() if part in ('song', 'call')})
    lo, hi = at(G, 'Porch Left', 0.3), L - 30
    hops, p = [(T_BIRD_IN, L - 10)], L - 10
    for t in song:
        p = float(np.clip(p + rng.choice([-1, 1]) * rng.uniform(160, 460), lo, hi))
        hops.append((t, p))
    hops = [h for h in hops if h[0] < T_SETTLE - 0.5] + [(T_SETTLE, at(G, 'Right', BIRD_AT))]
    return hops


def bird_track(G):
    """Per frame: the Woodbird's place, its speed, and how bright."""
    F = nframes(D)
    t = np.arange(F) * DT
    hops = bird_hops(G)
    p = np.full(F, hops[0][1])
    for (t0, p0), (t1, p1) in zip(hops, hops[1:]):
        u = smoothstep(t1, t1 + 0.25, t)
        p = np.where(t >= t1, p0 + (p1 - p0) * u, p)
    lvl = smoothstep(T_BIRD_IN, T_BIRD_IN + 0.3, t) * 0.9
    return dict(t=t, p=p, v=np.gradient(p, DT), lvl=lvl)


def render(G, seed=15):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    B = bird_track(G)
    p_sf = at(G, 'Left', TREE_AT)
    delight = [e for e in N if e[4] == 'delight']
    calls = sorted({e[0] for e in N if e[4] == 'call'})
    rng = np.random.default_rng(seed)
    glit = rng.uniform(at(G, 'Side', 0.1), at(G, 'Porch Left', 0.5), len(delight))
    swell = sorted({round(e[0], 2) for e in N if e[4] == 'swell'})
    swell = [s for i, s in enumerate(swell) if i == 0 or s - swell[i - 1] > 1.5]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = forest(S, T, START)

        # every bar of the Murmurs: a green-gold wave rolling the length of the roofline, one way then the other;
        # where two waves cross they flash. They soften while the bird sings, so it stands out
        soft = 1.0 - 0.4 * smoothstep(T_BIRD_IN - 1, T_BIRD_IN + 1, t)
        fronts = []
        for k, t0 in enumerate(T_MURMUR):
            a = t - t0
            if 0 <= a < 5.0:
                g = smoothstep(0, 0.5, a) * (1 - smoothstep(4.2, 5.0, a)) * soft
                x = (a / 4.6) * L if k % 2 == 0 else L - (a / 4.6) * L
                fronts.append((x, g))
                fr += light(DAY, 0.9 * g * np.exp(-((d - x) / 340) ** 2))
                fr += light(SUN if k % 4 < 2 else HEAD, 0.85 * g * np.exp(-((d - x) / 70) ** 2))
        for i, (x1, g1) in enumerate(fronts):
            for x2, g2 in fronts[i + 1:]:
                if abs(x1 - x2) < 250:
                    fr += light(WHITE, 0.8 * g1 * g2 * (1 - abs(x1 - x2) / 250) * np.exp(-((d - (x1 + x2) / 2) / 90) ** 2))

        # innocent delight: gold glitter all round him on every note
        for j, (t0, dur, m, v, part, k) in enumerate(delight):
            a = t - t0
            if 0 <= a < 0.8:
                fr += light(SUN, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - glit[j]) / (25 + 60 * a)) ** 2))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.1) * np.exp(-((d - glit[j]) / 10) ** 2))

        # each fortissimo swell: the whole forest blooms green and gold from the tree out, a white flash at its heart
        for t0 in swell:
            a = t - t0
            if 0 <= a < 3.0:
                r = 2200 * (1 - np.exp(-a / 0.5))
                fr += light(SUN, 0.75 * np.exp(-a / 1.0) * smoothstep(r + 200, r - 200, np.abs(d - p_sf)))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_sf) - r) / 110) ** 2))
                fr += light(WHITE, 0.5 * np.exp(-a / 0.15) * S['trees'])

        # the Woodbird: a hot magenta point, white at its heart, a short comet trail, wings flickering;
        # each landing of its call sends a magenta ring out through the green
        bl = B['lvl'][f]
        if bl > 0:
            p, v = B['p'][f], B['v'][f]
            flap = 0.82 + 0.18 * np.sin(2 * np.pi * 11 * t)
            behind = (d - p) * np.sign(v) < 0
            trail = behind * np.exp(-np.abs(d - p) / (18 + 0.08 * abs(v))) * min(1.0, abs(v) / 300)
            fr = fr * (1 - 0.95 * bl * np.exp(-((d - p) / 45) ** 2))[:, None]
            fr += light(BIRD, 1.2 * bl * flap * np.exp(-((d - p) / 16) ** 2))
            fr += light(BIRD, 0.85 * bl * trail)
            fr += light(WHITE, 0.9 * bl * flap * np.exp(-((d - p) / 3) ** 2))
            fr += light(BIRD, 0.6 * bl * np.exp(-((d - p) / 70) ** 2))
        for t0 in calls:
            a = t - t0
            if 0 <= a < 1.5 and bl > 0:
                p = float(np.interp(t0 + 0.25, B['t'], B['p']))
                fr += light(BIRD, 1.1 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p) - 700 * a) / 120) ** 2))

        # Siegfried under the tree, stirring when the bird calls
        sl = 0.8 + 0.15 * sum(np.exp(-(t - t0) / 0.4) for t0 in calls if 0 <= t - t0 < 2)
        fr = figure(fr, S, p_sf, SIEGFRIED, min(sl, 1.0), 16.0)
        fr += light(HEAD, 0.7 * min(sl, 1.0) * np.exp(-((d - p_sf) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, the Woodbird where it sings on the house, the leaves stirring around it."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    B = bird_track(G)
    bird = lambda tt: pan_at(B['p'][min(len(B['p']) - 1, int(tt / DT))])
    tree = pan_at(at(G, 'Left', TREE_AT))
    o = Orchestra(M, level=3.65)
    parts = {(round(t, 4), m): part for t, d, m, v, part, k in compose()}
    k = [0]

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m))
        if part in ('song', 'call'):
            k[0] += 1
            return [(('flutes', 'oboes', 'clarinets')[(k[0] // 6) % 3], -12 if m > 88 else 0, 8, 0.6)]
        if part == 'delight':
            return [('violins', 0, 4, 0.55)]
        if part == 'swell':
            return [('horns', -12, 0, 0.7), ('violins', 0, 0, 0.5), ('flutes', 0, -8, 0.3)]
        if part == 'murmur' and h == 1 and d >= 1.5:
            return [('horns', 0, 4, 0.55), ('cellos', 0, -6, 0.35)]
        return None

    def pan(t, m):
        if t >= T_BIRD_IN and m >= 76:
            return bird(t)
        return tree * 0.5

    o.tutti(tidy(EX['notes']), size=lambda t: 0.6, role=role, pan=pan)
    # the leaves: they rise with each swell and fall back so the bird is clear
    pts = [(0.0, -4), (T_BIRD_IN - 1.0, -4), (T_BIRD_IN, -12)]
    for t0 in sorted({round(e[0], 1) for e in compose() if e[4] == 'swell'}):
        pts += [(t0 - 0.3, -12), (t0 + 0.2, -1), (t0 + 2.5, -12)]
    o.effects(sorted(pts))
    o.wind(0.0, D, level=0.5, pan=tree * 0.3, seed=16)
