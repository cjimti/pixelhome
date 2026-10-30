"""The Bear: Mime is grumbling at the anvil, sulphur yellow beside the forge and tapping, when the orchestra
bursts out fortissimo and the cave mouth at the free end of Right flares green: Siegfried's horn from the forest.
Then he bursts in, electric emerald with a white-hot head, driving a bear on a rope: a great brown-black mass that
rolls in along Right ahead of him and goes straight for Mime.

The music is Wagner's own: Act I, bars 240 to 310, as Solti's 1958 Vienna Philharmonic recording takes them, from
Mime's "Das beste Schwert, das je ich geschweißt" through Siegfried's "Hoiho! Hau ein!" and the chase to "Aus dem
Busche kam ein Bär". The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Mime's
tapping on bassoons and cellos, the outburst on horns, Siegfried's audacity on horns and violins with a piccolo on
top, the bear's churning bass on cellos, basses and bassoons. The staging adds the bear: a growl in the tubas and
trombones and the thud of its weight on every lunge, its paws padding after Mime between lunges and off to the
woods, a boom and a rush of air as they burst in, the forge crackling.

Mime flees round the forge (Porch Left, across the anvil to Porch Right, out onto Left and back) with the bear
lunging after him on the chase's accents; every lunge flashes the run under it red-brown, and each of Siegfried's
notes throws an emerald shockwave out from him. He laughs ("Ha ha ha!", the house rippling green), then "Lauf,
Brauner!" sends the bear back out the way it came. He tells how he blew his horn for a better friend, each phrase
a soft emerald pulse; his horn call rings out and his strength blazes in emerald sweeps end to end, and the cave
settles with Siegfried at the anvil's right hand and Mime cowering at its left.

compose() tags every note, choreography() every chase; stage(), cave(), figure() and sparks() are the cave,
shared word for word by Act I's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'SF02'
TITLE = 'The Bear'
KIND = 'show'
DESCRIPTION = ('A horn rings out of the forest and young Siegfried storms in driving a bear, which chases the dwarf '
               'round and round the forge until Siegfried laughs and sends it back to the woods.')
VOICEOVER = ('A horn in the forest, and here comes Siegfried, with a bear on a rope. '
             'Poor Mime runs for his life.')

K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 240-310, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_HORN = BAR[248]                           # the horn from the forest, fortissimo
T_IN = BAR[250]                             # Siegfried and the bear burst in, on the bear's music
T_HO = BAR[262]                             # he laughs
T_OUT = BAR[281]                            # "Lauf, Brauner!": the bear sent back to the woods
T_TELL = BAR[285]                           # he tells how he called for a better friend
T_HORN2 = BAR[296]                          # "ließ ich hallend da ertönen": his horn call
T_STR = [BAR[305], BAR[306]]                # the fanfare at its top: his strength
T_REST = BAR[307]

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BEAR = hexc('#a04a10')
BEAR_HOT = hexc('#c83010')
EYE = hexc('#ff6000')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # the cave at every Act I cut
MIME_AT, HERO_AT = 0.32, 0.7                                       # their places on Porch Front at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
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


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: an emerald figure with a white-hot head."""
    fr = figure(fr, S, p, SIEGFRIED, lvl, w)
    return fr + light(HEAD, 0.9 * lvl * np.exp(-((S['d'] - p) / 5) ** 2))


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        v += (rate * rate * (target[f] - x[f - 1]) - 2 * rate * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def marks(G):
    """Named places as path distances."""
    return {
        'off': float(G.pd.max() + 90), 'R6': at(G, 'Right', 0.6), 'R2': at(G, 'Right', 0.2),
        'PR8': at(G, 'Porch Right', 0.8), 'PR5': at(G, 'Porch Right', 0.5), 'PR3': at(G, 'Porch Right', 0.3),
        'PF2': at(G, 'Porch Front', 0.2), 'PF5': at(G, 'Porch Front', 0.5), 'PF6': at(G, 'Porch Front', 0.6),
        'mime': at(G, 'Porch Front', MIME_AT), 'hero': at(G, 'Porch Front', HERO_AT),
        'PL7': at(G, 'Porch Left', 0.7), 'PL4': at(G, 'Porch Left', 0.4), 'PL2': at(G, 'Porch Left', 0.2),
        'L8': at(G, 'Left', 0.8), 'L5': at(G, 'Left', 0.5),
    }


LUNGES = [BAR[b] for b in (258, 260, 262, 265, 273, 276)]          # the bear's roars, on the chase's accents


def choreography(G):
    """Per frame: where Mime, the bear and Siegfried are."""
    m = marks(G)
    F = nframes(D)
    t = np.arange(F) * DT

    def track(pts):
        tgt = np.empty(F)
        for i, x in enumerate(t):
            tgt[i] = [m[k] for tk, k in pts if tk <= x][-1]
        return tgt

    Lg = LUNGES
    mime = track([(0, 'mime'), (Lg[0] - 1.0, 'PL7'), (Lg[1] - 1.0, 'PL2'), (Lg[2] - 1.0, 'PR3'), (Lg[3] - 1.0, 'PR8'),
                  (Lg[4] - 1.0, 'L8'), (Lg[5] - 1.0, 'L5'), (T_OUT - 1.0, 'mime')])
    bear = track([(0, 'off'), (T_IN, 'PF6'), (Lg[0], 'PL7'), (Lg[1], 'PL2'), (Lg[2], 'PR3'), (Lg[3], 'PR8'),
                  (Lg[4], 'L8'), (Lg[5], 'PL4'), (Lg[5] + 2.5, 'PF5'), (T_OUT, 'off')])
    sieg = track([(0, 'off'), (T_IN + 0.8, 'R6'), (Lg[1], 'R2'), (Lg[3], 'PR5'), (Lg[5], 'PR3'), (T_OUT - 0.5, 'PR8'),
                  (T_OUT + 2.5, 'R2'), (T_TELL + 2, 'hero')])
    return dict(t=t, mime=follow(mime, 5.0) + 3 * np.sin(2 * np.pi * 7 * t) * ((t > T_IN) & (t < T_OUT)),
                bear=follow(bear, 3.6), sieg=follow(sieg, 3.0))


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Under Mime's grumbling the left
    hand's repeated notes are his tapping ('smith'); the fortissimo outburst is the horn from the forest ('horn',
    k 0); the right hand of the bear's music and the rising chase is Siegfried's audacity ('aud'), the left hand
    churning under it the bear ('bear'); while he tells his story his phrases glow ('tell'), and the horn call he
    sang for a friend is 'horn' (k 1). 'roar' marks the bear's lunges; everything else 'orch'."""
    N = []
    for t, d, m, v, h in EX['notes']:
        b = max(mm for mm, bt in EX['bars'] if bt <= t + 1e-6)
        part, k = 'orch', None
        if b < 247 and h == 1 and d < 0.4:
            part = 'smith'
        elif 248 <= b < 250 and h == 0:
            part, k = 'horn', 0
        elif T_IN <= t < T_OUT + 1.5 and h == 0 and v >= 75:
            part = 'aud'
        elif T_IN <= t < T_OUT + 1.5 and h == 1:
            part = 'bear'
        elif 296 <= b < 307 and h == 0:
            part, k = 'horn', 1
        elif T_TELL <= t and h == 0:
            part = 'tell'
        N.append((t, d, m, v, part, k))
    for k, t0 in enumerate(LUNGES):
        N.append((t0, 1.0, 26, 0, 'roar', k))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=2):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    C = choreography(G)
    N = compose()
    smith = [(t, 0.4, anvil) for t, _, m, v, part, k in N if part == 'smith']
    smith_t = np.array([h[0] for h in smith])
    horn = [e for e in N if e[4] == 'horn']
    aud_on = np.array(sorted({e[0] for e in N if e[4] == 'aud'}))
    str_on = np.array([T_STR[0], T_STR[1]] + [e[0] for e in N if e[4] == 'horn' and e[5] == 1 and e[0] > T_STR[0]])
    str_on.sort()
    tell_on = np.array(sorted({e[0] for e in N if e[4] == 'tell'}))
    seg = G.seg_of
    right = seg == 'Right'
    jag = np.random.default_rng(seed).uniform(0.3, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        pm, pb, ps = C['mime'][f], C['bear'][f], C['sieg'][f]
        lv = dict(LV)
        lv['mouth'] += 0.4 * smoothstep(T_HORN - 0.3, T_HORN + 0.3, t) * (1 - smoothstep(T_IN + 1, T_IN + 6, t))
        fr = cave(S, T, lv)

        # Mime tapping at the anvil
        i = int(np.searchsorted(smith_t, t, side='right')) - 1
        if i >= 0 and t - smith_t[i] < 0.8:
            fr += light(HEAT, 0.7 * np.exp(-(t - smith_t[i]) / 0.08) * S['heat'] ** 0.5)
        fr += light(SPARK, np.clip(sparks(S, smith, t, 20, n=8, reach=0.6), 0, 1))

        # the horn call from the forest: every note flashes all of Right emerald, brightest at the mouth
        for t0, dur, m, v, part, k in horn:
            a = t - t0
            if 0 <= a < dur + 0.6:
                s = 0.95 * np.exp(-a / (dur + 0.25)) * (1.0 if k == 0 else 0.7)
                if k == 0:
                    fr += light(SIEGFRIED, 1.1 * s * right * (0.6 + 0.4 * S['mouth']))
                    fr += light(HEAD, 0.6 * np.exp(-a / 0.1) * S['mouth'])
                else:
                    fr += light(SIEGFRIED, s * np.exp(-((d - ps) / 380) ** 2))

        # the bear bursts in: a gust of green through the mouth, then the brown-black mass
        if T_IN <= t < T_IN + 1.5:
            a = t - T_IN
            fr += light(SIEGFRIED, 0.8 * np.exp(-a / 0.3) * np.exp(-((d - (L - 700 * a)) / 120) ** 2))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12) * right * jag)
            fr += light(SIEGFRIED, 0.5 * np.exp(-a / 0.4))
        if pb < L + 40:
            roar = max([np.exp(-(t - r) / 0.5) for r in LUNGES if r <= t], default=0.0)
            w = 55 * (1 + 0.4 * roar)
            body = np.exp(-((d - pb) / w) ** 6)
            rim = np.exp(-((np.abs(d - pb) - w) / 12) ** 2)
            fr = fr * (1 - body)[:, None]   # a black mass with a bristling brown rim
            fr += light(BEAR, (0.9 + 0.1 * np.sin(2 * np.pi * 2.2 * t)) * rim)
            fr += light(BEAR_HOT, roar * (0.6 * body + rim))
            if roar > 0.05:                 # the run under the bear flashes red-brown
                fr += light(BEAR_HOT, 0.8 * roar * (seg == seg[np.argmin(np.abs(d - pb))]))
            for e in (-9, 9):
                fr += light(EYE, 1.0 * np.exp(-((d - pb - e - 20) / 4) ** 2))

        # Siegfried's audacity: an emerald shockwave out from him at every note
        j = int(np.searchsorted(aud_on, t, side='right')) - 1
        if j >= 0 and t - aud_on[j] < 1.2:
            a = t - aud_on[j]
            fr += light(SIEGFRIED, 1.0 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - ps) - 1400 * a) / 110) ** 2))
            fr += light(SIEGFRIED, 0.5 * np.exp(-a / 0.2) * np.exp(-((d - ps) / 150) ** 2))

        # "Hoho!": the whole house ripples green
        if T_HO <= t < T_HO + 3.0:
            a = t - T_HO
            fr += light(SIEGFRIED, 0.55 * (1 - smoothstep(2.0, 3.0, a)) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 240 - a * 3.3))) ** 3)

        # the bear sent out: a whoosh of green chasing it to the free end
        if T_OUT <= t < T_OUT + 3:
            a = t - T_OUT
            fr += light(SIEGFRIED, 0.7 * np.exp(-a / 1.0) * smoothstep(pb - 300, pb, d) * (d < pb + 60))

        # his strength: emerald sweeps end to end and back
        k = int(np.searchsorted(str_on, t, side='right')) - 1
        if T_STR[0] <= t < T_REST + 2 and k >= 0:
            a = t - T_STR[0]
            front = (a / 2.4) % 2
            front = (front if front < 1 else 2 - front) * L
            fade = 1 - smoothstep(T_REST - 0.5, T_REST + 2, t)
            fr += light(SIEGFRIED, fade * (0.95 * np.exp(-((d - front) / 90) ** 2) + 0.3 * (d < front)))
            fr += light(HEAD, fade * 0.6 * np.exp(-(t - str_on[k]) / 0.12) * np.exp(-((d - front) / 40) ** 2))

        # his story: each phrase a soft emerald pulse out from him
        jt = int(np.searchsorted(tell_on, t, side='right')) - 1
        if jt >= 0 and t - tell_on[jt] < 1.0 and t < T_HORN2:
            a = t - tell_on[jt]
            fr += light(SIEGFRIED, 0.55 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - ps) - 700 * a) / 90) ** 2))

        mlvl = keys(t, [(0, 0.5), (T_HORN, 0.6), (T_IN + 3, 0.85), (T_OUT - 1, 0.85), (T_OUT, 0.35),
                        (T_HORN2, 0.35), (D - 8, 0.6)])
        fr = figure(fr, S, pm, MIME, mlvl)
        if ps < L + 40:
            slvl = keys(t, [(T_IN, 0.9), (T_REST, 0.9), (D - 6, 0.8)])
            fr = hero(fr, S, ps, slvl)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the bear's roars and Siegfried's entrance."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    S = stage(G)
    forge = pan_at(S['anvil'])
    mouth = pan_at(at(G, 'Right', 0.95))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    o = Orchestra(M, level=2.0)
    tag = {(round(e[0], 4), e[2]): e[4] for e in compose()}

    def role(t, d, m, v, h):
        p = tag.get((round(t, 4), m), 'orch')
        if p == 'smith':
            return [('bassoons', 0, 0, 0.6), ('cellos', 0, -8, 0.4)]
        if p == 'horn':
            return [('horns', 0, 4, 0.95), ('horns', -12, -6, 0.4)]
        if p == 'aud':
            return [('horns', 0, 0, 0.7), ('violins', 0, -4, 0.55)] + \
                ([('piccolo', 0, -14, 0.3)] if m >= note('D5') else [])
        if p == 'bear':
            return [('cellos', 0, 0, 0.7), ('basses', -12 if m >= 40 else 0, -4, 0.55), ('bassoons', 0, -8, 0.45)]
        return None

    def pan(t, m):
        if T_IN <= t < T_OUT:
            return pan_of('bear', t) * 0.6
        if t >= T_OUT:
            return pan_of('sieg', t) * 0.6
        return forge * 0.5

    o.tutti(EX['notes'], role=role, pan=pan)
    for t, d, m, v, p, k in compose():
        if p == 'smith':                    # Mime's little hammer on the anvil
            o.hit('anvil', t, 64, gain=0.25, pan=forge)
        elif p == 'roar':                   # the bear lunges: a growl in the tubas and a thud of its weight
            pb = pan_of('bear', t)
            o.play('tuba', note('D1'), t, 1.0, 120, pb, 0.8)
            o.play('trombones', note('D2'), t + 0.02, 0.8, 112, pb, 0.5)
            o.hit('timpani', t, 112, pitch=-6, gain=0.6, pan=pb)
            o.hit('bass drum', t, 110, gain=0.5, pan=pb)
            o.hit('hoof soft', t - 0.15, 100, gain=0.6, pan=pb)
    o.hit('crash', T_HORN, 110, gain=0.5, pan=mouth)
    o.boom(T_IN, mouth, 0.8)                # he bursts in through the cave mouth
    o.wind(T_IN - 0.3, T_IN + 3.0, 0.9, pan=mouth)
    o.gallop(T_IN, T_IN + 2.5, 0.36, pan=lambda t: pan_of('bear', t), v=104, gain=0.8)
    for a, b in zip(LUNGES, LUNGES[1:] + [T_OUT - 1]):  # the bear's paws between lunges, chasing Mime
        o.gallop(a + 0.5, min(b - 0.3, a + 2.0), 0.34, pan=lambda t: pan_of('bear', t), v=92, gain=0.6)
    o.gallop(T_OUT, T_OUT + 3.5, 0.32, pan=lambda t: pan_of('bear', t), v=104, gain=0.75)   # off to the woods
    o.hit('crash', T_STR[0], 112, gain=0.5, pan=pan_of('sieg', T_STR[0]))
    o.fire(0.0, D, 0.25, pan=forge, crackle=5.0)
    o.effects([(0.0, -4.0), (T_IN - 0.5, -4.0), (T_IN, 0.0), (T_OUT + 3.5, 0.0), (T_TELL, -10.0),
               (T_HORN2, -12.0), (D, -12.0)])     # the chase leads; his story and horn call stand clear
