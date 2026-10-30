"""Alberich's Watch: night outside Fafner's cave. Alberich, red in his muddy halo, keeps watch at Right 0.3.

The music is Wagner's own, from Act II as Solti's 1958 Vienna Philharmonic recording takes it: the storm that
brings the Wanderer (bars 118 to 136), his arrival and the quarrel (162 to 177), and Alberich's gloating dream of
the Ring (284 to 292). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
rushing storm figures on violins and woodwinds over the basses, the Wanderer's chords (Donington 17) on
trombones and tuba, Alberich's fury on the strings with stabbing brass, the Ring's chords on horns under the
violins' high tremolo, and his last fortissimo ("der Welt walte dann ich!") on the full brass. A production adds
the storm: wind that rises with each rush of light, a timpani roll and a crack of thunder as the Wanderer
appears, and the timpani on the last two chords of the stand-off.

Twice the wind rises: a rush of blue storm-light tears in at the free end of Right and races along the house,
each rising figure throwing sparks, and Alberich shrinks from it. The second time it races the whole length to
the far end of Left and bursts in a blue-white flash: the Wanderer is there, at Left 0.7. His chords roll wide
blue waves out over the house; Alberich answers with red waves from Right, and where the two fronts meet over
the cave mouth they crack white, hardest on his "Fort, aus dem Weg!". Then Alberich dreams of the Ring: gold
flares in the cave on every chord, each with a red throb from him, and on his last fortissimo red floods the
house from Right while the blue holds at Left, the boundary crackling white. They end in a stand-off: the left
half of the house blue, the right half red, pulsing on the final chords.

compose() tags every note of the excerpt; stage(), forest(), figure() and sparks() are the forest and the cave,
shared word for word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF12'
TITLE = "Alberich's Watch"
KIND = 'show'
DESCRIPTION = ('A dwarf keeps watch outside the cave in the dark. A rush of blue storm-light brings the Wanderer, '
               'and blue and red fight for the house.')
VOICEOVER = ('Alberich is waiting for the dragon to die, so the gold can be his again. '
             'Then the wind brings an old enemy.')

K = 1                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 118-136, 162-177 and 284-292, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
RUSH = [(BAR[118], BAR[128]), (BAR[132], BAR[137])]     # the two rushes of storm-light (start, crest)
T_NEAR = BAR[162]                           # "Wer naht dort schimmernd": the light gathers at Left
T_ARRIVE = BAR[167]                         # the Wanderer appears in a flash at Left 0.7
T_WANDER = BAR[168]                         # his chords
T_FURY = BAR[171]                           # Alberich answers
T_SLAM = BAR[177] + 0.25                    # his fortissimo descent: "Von dannen, schamloser Dieb!"
T_RING = BAR[284]                           # he dreams of the Ring
T_WORLD = BAR[289]                          # "der Welt walte dann ich!"
T_STANDOFF = BAR[292]
D_END = D

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
WANDERER = hexc('#1a3cff')
WANDER_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF11 left the forest
END = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)         # where SF13 picks it up
ALB_AT = 0.3                                # Alberich's watch, on Right
WAN_AT = 0.7                                # the Wanderer, on Left


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). 'storm' is the rushing music
    (k = which rush), 'near' the gathering chords, 'wanderer' his chords, 'fury' Alberich's answer, 'ring' the
    dream of the Ring, 'world' his fortissimo, 'stand' the final chords."""
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        if t < T_NEAR:
            part, k = 'storm', 0 if t < RUSH[1][0] else 1
        elif t < T_WANDER:
            part, k = 'near', 0
        elif t < T_FURY:
            part, k = 'wanderer', 0
        elif t < T_RING:
            part, k = 'fury', 0
        elif t < T_WORLD:
            part, k = 'ring', 0
        elif t < T_STANDOFF:
            part, k = 'world', 0
        else:
            part, k = 'stand', 0
        N.append((t, d, m, v, part, k))
    return N


def hits(N, part, n=2, space=0.35, vmin=0):
    """The onsets where n or more notes of a part strike together."""
    return np.array(accents([(e[0], e[1], e[2], e[3]) for e in N if e[4] == part], vmin=vmin, n=n, space=space))


def render(G, seed=12):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    p_alb, p_wan = at(G, 'Right', ALB_AT), at(G, 'Left', WAN_AT)
    storm = [e for e in N if e[4] == 'storm' and e[3] >= 90]
    near = hits(N, 'near', 2, 0.3)
    wan = hits(N, 'wanderer', 2, 0.5)
    fury = hits(N, 'fury', 3, 0.5)
    ring = hits(N, 'ring', 3, 0.5)
    world = hits(N, 'world', 3, 0.6)
    stand = hits(N, 'stand', 1, 1.5, vmin=110)
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Porch Left', 0.2), at(G, 'Porch Right', 0.8), len(ring))
    gust = Flicker(np.random.default_rng(seed + 1), G.N, 2.0, 6.0)

    def wave(t0s, t, p, speed, width, life):
        """Fronts rolling out from p for each onset in t0s, -> perceptual."""
        w = np.zeros_like(d)
        for t0 in t0s[(t0s <= t) & (t0s > t - life * 3)]:
            a = t - t0
            w += np.exp(-a / life) * np.exp(-((np.abs(d - p) - speed * a) / width) ** 2)
        return w

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_STANDOFF, START[k]), (D, END[k])]) for k in START}
        fr = forest(S, T, lv)

        # the storm-light: two rushes of blue from the free end of Right; the first crests at the porch and falls
        # back, the second races the whole length of the house and gathers at Left
        for k, (t0, t1) in enumerate(RUSH):
            if t0 <= t < (t1 + 3.0 if k == 0 else T_ARRIVE + 1.5):
                reach = (mid if k == 0 else p_wan) - 200
                front = L - (L - reach) * smoothstep(t0, t1, t)
                body = smoothstep(front - 40, front + 160, d) * smoothstep(L + 400, front, d)
                fade = 1 - smoothstep(t1, t1 + 3.0, t) if k == 0 else 1 - smoothstep(T_ARRIVE, T_ARRIVE + 1.5, t)
                fr += light(WANDER_SOFT, (0.75 + 0.25 * k) * fade * body * (0.8 + 0.2 * gust(T)))
                fr += light(WANDERER, 0.5 * fade * body)
                fr += light(SPEAR, 0.85 * fade * np.exp(-((d - front) / 40) ** 2))
        # every loud rising figure of the storm throws a spray of blue-white sparks off the front
        sp = [(e[0], 0.6 * e[3] / 127, L - (L - mid) * smoothstep(*RUSH[e[5]], e[0])) for e in storm]
        fr += light(SPEAR, sparks(S, sp, t, seed, n=6, reach=0.4))

        # the light gathers at Left: each chord a blue pulse there, brighter as it builds
        for t0 in near:
            a = t - t0
            if 0 <= a < 1.2:
                g = 0.4 + 0.6 * smoothstep(T_NEAR, T_ARRIVE, t0)
                fr += light(WANDER_SOFT, g * np.exp(-a / 0.35) * np.exp(-((d - p_wan) / 300) ** 2))
        if T_ARRIVE <= t < T_ARRIVE + 1.5:
            a = t - T_ARRIVE
            fr += light(WHITE, 0.95 * np.exp(-a / 0.15) * np.exp(-((d - p_wan) / 300) ** 2))
            fr += light(WANDERER, 0.7 * np.exp(-a / 0.5))

        # his chords: wide blue waves out from him; Alberich's answer: red waves from Right; they crack white
        blue = wave(wan, t, p_wan, 600, 200, 1.0) + wave(world, t, p_wan, 300, 160, 0.6) * 0.6
        red = wave(fury, t, p_alb, 650, 180, 0.9) + wave(world, t, p_alb, 900, 220, 0.8)
        if T_SLAM <= t < T_SLAM + 2.5:
            a = t - T_SLAM
            red += 1.4 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_alb) - 1100 * a) / 260) ** 2)
        fr += light(WANDERER, 0.95 * np.clip(blue, 0, 1.2))
        fr += light(BLOOD, 0.95 * np.clip(red, 0, 1.2))
        fr += light(WHITE, np.clip(blue * red * 4, 0, 1))

        # the Ring: gold flares in the cave on every chord, each with a red throb from Alberich
        for j, t0 in enumerate(ring):
            a = t - t0
            if 0 <= a < 1.8:
                g = np.exp(-a / 0.8) * smoothstep(0, 0.06, a)
                fr += light(GOLD, 0.95 * g * np.exp(-((d - glint_at[j]) / (35 + 40 * a)) ** 2))
                fr += light(ALBERICH, 0.45 * g * np.exp(-((d - p_alb) / 120) ** 2))
        if T_RING <= t < T_WORLD + 2:                       # the hoard's glow swells under his dream
            fr += light(GOLD, 0.35 * smoothstep(T_RING, T_WORLD, t) * (1 - smoothstep(T_WORLD, T_WORLD + 2, t))
                        * S['mouth'])

        # his fortissimo: red floods the house from Right, the blue holds at Left, the boundary crackles
        if T_WORLD <= t < T_STANDOFF + 1:
            u = smoothstep(T_WORLD, T_STANDOFF, t)
            edge = p_alb - (p_alb - (mid - 300)) * u
            flood = smoothstep(edge - 120, edge + 120, d)
            fr += light(BLOOD, 0.7 * flood * (1 - smoothstep(T_STANDOFF, T_STANDOFF + 1, t)))
            fr += light(WHITE, 0.8 * np.exp(-((d - edge) / 30) ** 2) * (0.6 + 0.4 * gust(T * 3)))

        # the stand-off: left half blue, right half red, pulsing in turn on the last chords
        if t >= T_STANDOFF:
            u = smoothstep(T_STANDOFF, T_STANDOFF + 1, t)
            side = smoothstep(mid + 200, mid - 200, d)
            lb, lr = 0.55, 0.55
            for k, t0 in enumerate(stand):
                if t >= t0:
                    b = np.exp(-(t - t0) / 0.8)
                    lb, lr = (lb + 0.45 * b, lr) if k % 2 else (lb, lr + 0.45 * b)
            fr += light(WANDERER, u * lb * side * np.exp(-((d - p_wan) / 900) ** 2))
            fr += light(BLOOD, u * lr * (1 - side) * np.exp(-((d - p_alb) / 900) ** 2))

        # Alberich, shrinking from the storm; the Wanderer from his arrival
        alvl = 0.7 - 0.3 * sum(smoothstep(t0, t1, t) * (1 - smoothstep(t1, t1 + 2, t)) for t0, t1 in RUSH)
        alvl -= 0.3 * smoothstep(T_NEAR, T_ARRIVE, t) * (1 - smoothstep(T_ARRIVE, T_FURY, t))
        for t0 in np.concatenate([fury, world]):
            if 0 <= t - t0 < 0.6:
                alvl += 0.3 * np.exp(-(t - t0) / 0.2)
        fr += light(MUD, 0.6 * alvl * np.exp(-((d - p_alb) / 70) ** 2))
        fr = figure(fr, S, p_alb, ALBERICH, float(np.clip(alvl, 0.2, 1.0)))
        if t >= T_ARRIVE:
            wl = keys(t, [(T_ARRIVE, 1.0), (T_ARRIVE + 2, 0.8)])
            for t0 in wan:
                if 0 <= t - t0 < 0.6:
                    wl += 0.2 * np.exp(-(t - t0) / 0.25)
            fr = figure(fr, S, p_wan, WANDERER, min(wl, 1.0), 18.0)
            fr += light(SPEAR, 0.5 * min(wl, 1.0) * np.exp(-((d - p_wan - 22) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, each part where it happens on the house, with the storm around them."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    alb = pan_at(at(G, 'Right', ALB_AT))
    wan = pan_at(at(G, 'Left', WAN_AT))
    o = Orchestra(M, level=2.35)
    parts = {(round(t, 4), m): part for t, d, m, v, part, k in compose()}

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m))
        if part == 'wanderer' or (part == 'near' and h == 1):
            return ([('tuba', 0, 4, 0.7), ('trombones', 12, -4, 0.5)] if m < 48 else
                    [('trombones', 0, 2, 0.7), ('horns', 0, -4, 0.5)])
        if part == 'ring' and h == 1:
            return [('horns', 0, 2, 0.75), ('trombones', -12, -6, 0.4)]
        if part in ('world', 'stand') and h == 1 and d >= 0.3:
            return [('trombones', 0, 4, 0.75), ('tuba', -12, 0, 0.5), ('horns', 0, 0, 0.5)]
        if part in ('world', 'stand') and h == 0 and d >= 0.3:
            return [('trumpets', 0, 0, 0.6), ('violins', 0, -6, 0.4)]
        return None

    def pan(t, m):
        if t < T_ARRIVE:
            return 0.6 - 0.9 * smoothstep(0, T_ARRIVE, t)
        if T_FURY <= t < T_STANDOFF:
            return alb * 0.7
        return wan * 0.6

    o.tutti(tidy(EX['notes']), size=lambda t: 0.6 + 0.4 * (t < T_NEAR or t >= T_WORLD), role=role, pan=pan)
    # the storm leads while it brings him; once he is there the quarrel and the Ring must be clear
    o.effects([(0.0, 0), (T_ARRIVE + 1.5, 0), (T_WANDER + 0.5, -10), (T_STANDOFF, -10)])
    # the storm that brings him, and the stand-off's blows
    level = lambda tt: 0.2 + 0.9 * sum(np.clip((tt - a) / (b - a), 0, 1) * np.exp(-np.clip(tt - b, 0, None) / 2.5)
                                       for a, b in RUSH + [(T_NEAR, T_ARRIVE)])
    o.wind(0.0, T_FURY + 4, level=level, pan=lambda tt: 0.6 - 1.2 * min(1.0, tt / T_ARRIVE), seed=12)
    o.hit('timpani roll', T_ARRIVE - 3.0, 100, gain=0.5, pan=wan)
    o.thunder(T_ARRIVE, near=0.7, pan=wan, gain=0.9)
    for k, t0 in enumerate(hits(compose(), 'stand', 1, 1.5, vmin=110)):
        o.hit('timpani', t0, 118, pitch=-3 if k % 2 else -6, gain=0.7, pan=alb if k % 2 == 0 else wan)
