"""Dawn in the Forest: the last of the night outside Fafner's cave. Alberich, hiding at Right 0.3, slips away.

The music is Wagner's own, from Act II as Solti's 1958 Vienna Philharmonic recording takes it: day breaking as
Mime leads Siegfried to the cave (bars 528 to 547), Mime's tale of the dragon's heart and Siegfried's answer,
"Nothung stoß' ich dem Stolzen ins Herz!" (603 to 610), and Mime's chattering retreat into the hush where the
Forest Murmurs begin (700 to 715). The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py): the dawn's long lines on clarinets, oboes and violins over the low strings, the dragon's
tritone tremolo (A flat and D) on cellos and basses, Siegfried's rising resolve on horns and violins, and Mime's
falling chromatic scales on bassoons and violas. A production adds the morning: the first birds as the light
comes, Mime's scuttling steps and Siegfried's stride, and a rustle of leaves as the forest wakes.

The sun comes up: every long note of the dawn breaks a gold shaft through the trees, bursting white where it
lands and spreading, and the forest turns from night teal to hard green. Mime, sulphur yellow, scuttles in from
the free end of Right with Siegfried, emerald with his white-hot head, striding behind him, Mime hopping on every
note; on the orchestra's two forte chords an emerald streak races ahead of Siegfried. At the cave Mime tells him
of the dragon: the cave mouth throbs ochre on every note of the tritone tremolo. Siegfried answers him: three
emerald blasts out to both ends of the house on his last chords. Mime bolts on the falling scales, a yellow
streak back out the free end of Right, and in the hush the Forest Murmurs begin to ripple green and gold while
Siegfried walks to the lime tree at Left 0.5 and lies down under it.

compose() tags every note of the excerpt; stage(), forest(), figure() and sparks() are the forest and the cave,
shared word for word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF14'
TITLE = 'Dawn in the Forest'
KIND = 'show'
DESCRIPTION = ('The sun comes up through the trees in great gold shafts as the dwarf leads Siegfried to the cave. '
               'He tells him about the dragon, until Siegfried chases him off.')
VOICEOVER = ('Mime brings the boy to the dragon\'s cave, hoping he will learn what fear is. '
             'And the sun comes up.')

K = 3                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 528-547, 603-610 and 700-715, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_SUN = BAR[529]                            # day breaks
T_SHAFTS = [n[0] for n in EX['notes'] if n[4] == 0 and n[1] >= 0.7 and T_SUN <= n[0] < BAR[542]]
T_IN = BAR[533]                             # they come in at the free end of Right
T_HORN = [BAR[542], BAR[545]]               # the forte chords: an emerald streak ahead of him
T_CAVE = BAR[543]                           # they reach the cave mouth
T_DRAGON = BAR[603]                         # the dragon's heart
T_STR = accents([n for n in EX['notes'] if BAR[609] <= n[0] < BAR[611]], n=2, space=0.9)[:3]   # his answer
T_FLEE = BAR[700]                           # Mime bolts
T_WALK = BAR[707]                           # Siegfried walks to the lime tree
T_LIE = BAR[713]
T_MURMUR = [BAR[712], BAR[713] + 1.0, BAR[714] + 1.5]   # the Forest Murmurs begin

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
MIME = hexc('#e0c800')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF13 left the forest: night
END = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)          # where SF15 picks it up: day
ALB_AT = 0.3
TREE_AT = 0.5                               # the lime tree, on Left


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). 'sun' is a long note of the dawn,
    'mime' a hop as they come in, 'horn' a forte chord, 'dragon' a note of the tritone tremolo, 'strength' his
    answer, 'flee' Mime's falling scales, 'murmur' the hush where the Forest Murmurs begin."""
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        if t < T_DRAGON:
            if any(abs(t - x) < 0.3 for x in T_HORN) and v >= 80:
                part = 'horn'
            elif t >= T_IN and t < T_CAVE and d < 0.7:
                part = 'mime'
            else:
                part = 'sun'
        elif t < T_FLEE:
            part = 'dragon' if h == 1 and m < 52 and t < T_STR[0] else 'strength' if t >= T_STR[0] - 0.05 else 'rise'
        elif t < T_WALK + 2:
            part = 'flee'
        else:
            part = 'murmur'
        N.append((t, d, m, v, part, None))
    return N


def tracks(G):
    """Per frame: where Mime and Siegfried are, and how bright."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.pd.max()
    door = L + 40
    cave_m, cave_s = at(G, 'Porch Front', 0.62), at(G, 'Porch Right', 0.2)
    tree = at(G, 'Left', TREE_AT)
    hop = np.abs(np.sin(np.pi * t / 0.34)) * 10
    pm = np.array([keys(x, [(T_IN, door), (T_CAVE, cave_m), (T_FLEE + 0.8, cave_m), (T_FLEE + 4.5, door + 200)]) for x in t])
    pm = pm - hop * ((t > T_IN) & (t < T_CAVE))
    ps = np.array([keys(x, [(T_IN + 1.5, door), (T_CAVE + 1.5, cave_s), (T_WALK, cave_s), (T_LIE - 2, tree)])
                   for x in t])
    lm = np.array([keys(x, [(T_IN, 0.0), (T_IN + 0.6, 0.8), (T_FLEE + 3.5, 0.8), (T_FLEE + 4.5, 0.0)]) for x in t])
    ls = np.array([keys(x, [(T_IN + 1.5, 0.0), (T_IN + 2.2, 0.85), (T_LIE, 0.85), (T_LIE + 3, 0.8)]) for x in t])
    return dict(t=t, pm=pm, ps=ps, lm=lm, ls=ls)


def render(G, seed=14):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    C = tracks(G)
    p_alb = at(G, 'Right', ALB_AT)
    mime_on = np.array(sorted({round(e[0], 2) for e in N if e[4] in ('mime', 'flee')}))
    dragon = [e for e in N if e[4] == 'dragon']
    strength = sorted({e[0] for e in N if e[4] == 'strength'})
    flee = accents([(e[0], e[1], e[2], e[3]) for e in N if e[4] == 'flee'], n=1, space=0.55)
    gloat = [(sg[0], sg[1]) for sg in EX['singing'] if sg[2] == 'Mime' and sg[0] > T_FLEE + 5]
    rng = np.random.default_rng(seed)
    land = rng.uniform(at(G, 'Left', 0.05), L - 60, len(T_SHAFTS))
    land[0] = at(G, 'Right', 0.55)
    T_SUN_FULL = T_CAVE

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_SUN, START[k]), (T_SUN_FULL, END[k])]) for k in START}
        fr = forest(S, T, lv)
        pm, ps = C['pm'][f], C['ps'][f]

        # Alberich, still hiding at the start, slips away
        if t < 5:
            al = 0.3 * (1 - smoothstep(1, 4.5, t))
            fr += light(MUD, 0.6 * al * np.exp(-((d - p_alb) / 70) ** 2))
            fr = figure(fr, S, p_alb, ALBERICH, al)

        # Mime's motif: a yellow blip under him on every hop, a little ripple out
        i = int(np.searchsorted(mime_on, t, side='right')) - 1
        if i >= 0 and t - mime_on[i] < 0.6 and (t < T_CAVE + 1 or T_FLEE <= t < T_FLEE + 5):
            a = t - mime_on[i]
            fr += light(MIME, 0.6 * np.exp(-a / 0.15) * np.exp(-((np.abs(d - pm) - 300 * a) / 40) ** 2))

        # the horn call: an emerald streak racing ahead of him, the whole way along the front
        for t0 in T_HORN:
            a = t - t0
            if 0 <= a < 2.4:
                front = ps - 1100 * a
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.0) * smoothstep(front - 30, front + 30, d)
                            * smoothstep(ps + 10, ps - 120, d) * smoothstep(front + 500, front, d))
                fr += light(HEAD, 0.9 * np.exp(-a / 0.8) * np.exp(-((d - front) / 22) ** 2))

        # the dragon told of: the cave mouth throbs ochre on every note of Fafner's motif
        for t0, dur, m, v, part, k in dragon:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SCALE, 0.85 * np.exp(-a / 0.35) * S['mouth'])
                fr += light(CAVE, 0.6 * np.exp(-a / 0.5) * S['porch'])

        # his strength: emerald blasts out to both ends of the house
        for t0 in T_STR:
            a = t - t0
            if 0 <= a < 2.0:
                r = 1600 * min(1.0, a / 0.6)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.7) * smoothstep(r + 80, r - 80, np.abs(d - ps)))
                fr += light(HEAD, 0.8 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - ps) - r) / 40) ** 2))
        if T_FLEE <= t < T_FLEE + 4.5:                      # the yellow streak he leaves behind him
            a = t - T_FLEE
            fr += light(MIME, 0.8 * smoothstep(pm - 500, pm, d) * smoothstep(pm + 20, pm - 10, d) * (1 - a / 4.5))

        # Mime's falling scales: yellow cascades pouring out toward the free end of Right; then, gone, his gloating
        # voice flickers there among the trees ("Fafner und Siegfried, Siegfried und Fafner")
        for t0 in flee:
            a = t - t0
            if 0 <= a < 1.4:
                front = pm + 900 * a
                fr += light(MIME, 0.8 * np.exp(-a / 0.5) * np.exp(-((d - front) / 90) ** 2) * (d < L + 50))
        for t0, t1 in gloat:
            if t0 <= t < t1 + 0.8:
                flick = 0.5 + 0.5 * np.sin(2 * np.pi * 3.0 * (t - t0)) ** 2
                g = smoothstep(t0, t0 + 0.3, t) * (1 - smoothstep(t1, t1 + 0.8, t))
                fr += light(MIME, 0.7 * g * flick * smoothstep(at(G, 'Right', 0.6), L, d))

        # the sunrise: gold shafts breaking through, each bursting white where it lands and spreading
        for k, t0 in enumerate(T_SHAFTS):
            a = t - t0
            if 0 <= a < 7:
                w = 30 + 220 * (1 - np.exp(-a / 1.5))
                g = smoothstep(0, 0.25, a) * (1 - 0.6 * smoothstep(2, 7, a))
                fr += light(SUN, 1.0 * g * np.exp(-((d - land[k]) / w) ** 2))
                fr += light(WHITE, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - land[k]) / 25) ** 2))
                fr += light(SUN, 0.6 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - land[k]) - 900 * a) / 80) ** 2))
        if T_SUN <= t < T_SUN + 2:
            fr += light(SUN, 0.5 * np.exp(-(t - T_SUN) / 0.5))

        # the Forest Murmurs: green-gold ripples rolling end to end, alternating direction
        for k, t0 in enumerate(T_MURMUR):
            a = t - t0
            if 0 <= a < 5:
                front = (a / 4.5) * L if k % 2 == 0 else L - (a / 4.5) * L
                g = smoothstep(0, 0.5, a) * (1 - smoothstep(4.2, 5, a))
                fr += light(DAY, 0.85 * g * np.exp(-((d - front) / 220) ** 2))
                fr += light(SUN, 0.7 * g * np.exp(-((d - front) / 45) ** 2))

        # Mime, and Siegfried
        if C['lm'][f] > 0:
            fr = figure(fr, S, pm, MIME, C['lm'][f], 14.0)
        if C['ls'][f] > 0:
            ls = C['ls'][f]
            for t0 in strength:
                if 0 <= t - t0 < 0.5:
                    ls += 0.15 * np.exp(-(t - t0) / 0.15)
            fr = figure(fr, S, ps, SIEGFRIED, min(ls, 1.0), 16.0)
            fr += light(HEAD, 0.7 * min(ls, 1.0) * np.exp(-((d - ps) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, and the morning around them."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = tracks(G)
    pm = lambda tt: pan_at(C['pm'][min(len(C['pm']) - 1, int(tt / DT))])
    ps = lambda tt: pan_at(C['ps'][min(len(C['ps']) - 1, int(tt / DT))])
    cave = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=2.8)
    parts = {(round(t, 4), m): part for t, d, m, v, part, k in compose()}

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m))
        if part == 'sun' and h == 0:
            return [('clarinets', 0, 4, 0.6), ('violins', 0, -4, 0.45)] + ([('oboes', 0, -6, 0.35)] if d >= 1.0 else [])
        if part == 'mime':
            return [('bassoons', 0, 4, 0.6), ('violas', 0, -6, 0.35)]
        if part == 'horn':
            return [('horns', 0, 6, 0.75), ('trombones', -12, -4, 0.45)]
        if part == 'dragon':
            return [('cellos trem', 0, 4, 0.6), ('basses', -12 if m >= 40 else 0, 0, 0.45)]
        if part in ('rise', 'strength') and h == 0:
            return [('violins', 0, 2, 0.55), ('horns', -12, 0, 0.6 if part == 'strength' else 0.35)]
        if part == 'strength' and h == 1:
            return [('horns', 0, 6, 0.75), ('trombones', 0, 0, 0.55), ('tuba', -12, -6, 0.4)]
        if part == 'flee':
            return [('bassoons', 0, 2, 0.55), ('violas', 0, -4, 0.4)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 0.4 if t < T_IN else 0.75, role=role,
            pan=lambda t, m: cave * 0.5 if T_CAVE <= t < T_FLEE else 0.0)
    # the morning: birds come with the light and fall quiet under the talk; their steps; the forest waking
    o.effects([(0.0, -6), (T_SUN, -2), (T_IN, 0), (T_CAVE, -2), (T_CAVE + 1.5, -9), (T_FLEE - 0.5, -9),
               (T_FLEE, -2), (T_WALK + 2, -4)])
    rng = np.random.default_rng(14)
    for t0 in np.sort(rng.uniform(T_SUN + 1, T_CAVE + 2, 16)):          # the first birds
        o.hit('triangle', t0, int(rng.uniform(40, 70)), pitch=float(rng.uniform(10, 19)), gain=0.25,
              pan=float(rng.uniform(-0.9, 0.9)))
    for t0 in np.sort(rng.uniform(T_WALK, D, 8)):
        o.hit('triangle', t0, int(rng.uniform(35, 55)), pitch=float(rng.uniform(12, 20)), gain=0.2,
              pan=float(rng.uniform(-0.9, 0.9)))
    t = T_IN                                                            # Mime scuttling, Siegfried striding
    while t < T_CAVE:
        o.M.add('fx', o.hits['hoof soft'].play(52), t, 0.18, pm(t))
        t += 0.34
    t = T_IN + 1.5
    while t < T_CAVE + 1.5:
        o.M.add('fx', o.hits['hoof'].play(70), t, 0.2, ps(t))
        t += 0.6
    t = T_FLEE + 0.8
    while t < T_FLEE + 4.5:
        o.M.add('fx', o.hits['hoof soft'].play(60), t, 0.2, pm(t))
        t += 0.2
    o.wind(T_SUN, T_CAVE + 3, level=0.35, pan=0.2, seed=15)            # leaves stirring as the light comes
    for t0 in T_STR:
        o.hit('timpani', t0, 112, pitch=-4, gain=0.55, pan=ps(t0))
    o.hit('crash', T_STR[0], 104, gain=0.35, pan=ps(T_STR[0]))
