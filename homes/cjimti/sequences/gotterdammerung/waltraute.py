"""Waltraute: back on Brünnhilde's rock, a bright afternoon, Brünnhilde in silver on the summit with the Ring
gold on her hand. Thunder rolls far off in the east: "Ein Luftroß jagt im Laufe daher."

The music is Wagner's own, four passages of Act I as Solti's 1958 Vienna Philharmonic recording takes them: the
storm coming on and Waltraute's arrival (bars 1052-1067), "Den Ring - von mir?" (1406-1413), Brünnhilde's refusal,
"stürzt' auch in Trümmern Walhall's strahlende Pracht!" (1489-1494), and Waltraute's flight, "Walhall's Göttern
Weh'!" (1509-1527). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
Valkyries' figures on horns, trumpets and violins, the Ring on flutes and clarinets, the refusal and Valhalla's
glory on the full brass with cymbals and timpani. The stage adds the storm: far thunder, then thunder with every
bolt, the wind, a horse galloping on the clouds, a blow as she lands; and the same storm carrying her off. While
the sisters plead and refuse, the stage keeps quiet.

Out of the east, at the free end of Right, a storm cloud comes on, wave on wave, every loud note an orange Valkyrie
streak racing the length of the house and the runs cracking white with lightning; on "Brünnhilde!" Waltraute
herself lands below the summit in a burst of orange. The cloud thins. She begs for the Ring: gold surges run from
Brünnhilde's hand to her and teal streaks of the Rhine pull at it from the east. Brünnhilde refuses: two silver
shocks over the whole house and the Ring blazing, the sky going deep blue for the Valhalla she would let fall.
Waltraute flees on the storm, every note of her flight an orange streak racing out of the free end of Right, the
clouds roll away behind her, and the afternoon sinks toward a red dusk with Brünnhilde alone on the summit.

compose() tags every note; stage(), heat(), fire(), scene(), strand() and figure() are shared word for word by
the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD13'
TITLE = 'Waltraute'
KIND = 'show'
DESCRIPTION = ('A Valkyrie storms onto the rock out of a thundercloud and begs her sister to give the Ring back to '
               'the Rhine before the gods are destroyed. Brünnhilde refuses, and Waltraute flees in the storm.')
VOICEOVER = ('A storm comes racing over the mountain, and out of it rides a Valkyrie. '
             'She has come to beg her sister for the Ring.')

K = 6                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1052-1067, 1406-1413, 1489-1494 and 1509-1527, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SEG = [s['start'] for s in EX['segments']] + [D]
T_THUNDER = 0.5                             # "Ein Luftroß jagt im Laufe daher": a storm far off in the east
T_RIDE = [BAR[1056], BAR[1059], BAR[1061]]  # the storm comes on, wave on wave
T_CRY = BAR[1062]
T_LAND = BAR[1063]                          # "Brünnhilde!": Waltraute lands
T_CLEAR = BAR[1066]                         # the cloud thins round them
T_RING = SEG[1]                             # "Den Ring - von mir?"
T_REFUSE = [BAR[1491], BAR[1493]]           # "stürzt' auch in Trümmern Walhall's strahlende Pracht!"
T_VAL = [BAR[1493], BAR[1495] - 0.3]        # the glory of Valhalla she will let fall
T_FLEE = SEG[3]                             # "Wehe! Wehe!": Waltraute flees on the storm
T_GONE = BAR[1525]
RBEAT = 0.3                                 # her halo flickers at the gallop

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
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
GOLD = hexc('#ffaa00')
RINGRED = hexc('#ff1800')
WALTRAUTE = hexc('#ff9a20')
CLOUD = hexc('#2a3448')
BOLT = hexc('#e8f0ff')
RHINE = hexc('#0a7c8a')

START = dict(night=0.0, stars=0.0, rock=0.4, fire=0.2, east=0.0, dawn=0.12, hue=0.6, day=0.62, rope=0.0)
END = dict(night=0.15, stars=0.0, rock=0.35, fire=0.35, east=0.0, dawn=0.5, hue=0.22, day=0.15, rope=0.0)
BRUNNHILDE_AT = ('Porch Front', 0.6)
BRUNNHILDE_START = 0.9                      # her level at the start
BRUNNHILDE_END = ('Porch Front', 0.6, 0.85)     # (segment, u, level); the Ring's glint on her hand at 0.7 x level
WALTRAUTE_AT = ('Porch Right', 0.7)         # where she lands


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


def part_of(t, d, m, v, h):
    """What a note of the excerpt is: (part, k), see compose()."""
    if T_RIDE[0] <= t < SEG[1] and h == 0 and v >= 85 and m >= note('B3'):
        return 'ride', sum(t >= r for r in T_RIDE[1:])
    if T_RING <= t < SEG[2] and h == 0 and v >= 85:
        return 'ring', None
    if T_REFUSE[0] <= t < T_VAL[0] and v >= 98:
        return 'refuse', None
    if T_VAL[0] <= t < SEG[3] and v >= 100:
        return 'valhalla', None
    if BAR[1512] <= t < T_GONE and h == 0 and v >= 110 and m >= note('B3'):
        return 'ride', 3
    return 'music', None


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The right hand's loud notes as
    the storm comes on are its waves ('ride', k = which wave), and as Waltraute flees, her flight ('ride', k 3); the
    melody of "Den Ring - von mir?" is the Ring ('ring'); the loud notes of "stürzt' auch in Trümmern" are
    Brünnhilde's refusal ('refuse') and those of "Walhall's strahlende Pracht" Valhalla's glory ('valhalla').
    Everything else is 'music'."""
    return [(float(t), float(d), int(m), int(v)) + part_of(t, d, m, v, h) for t, d, m, v, h, _ in tidy(EX['notes'])]


def bolts():
    """Lightning while the storm is overhead: [(time, run)]."""
    runs = ['Right', 'Porch Right', 'Left', 'Side', 'Porch Left', 'Right', 'Left', 'Side']
    ts = [t0 + 0.05 + 1.2 * j for t0 in T_RIDE for j in range(3)] + [T_CRY + 0.1, T_LAND] \
        + [T_FLEE + 0.05 + 1.2 * j for j in range(4)]
    return [(float(t), runs[i % len(runs)]) for i, t in enumerate(sorted(ts))]


def flight(G, t):
    """Where Waltraute is at time t (None before she arrives or after she has gone)."""
    L, land = G.pd.max(), at(G, *WALTRAUTE_AT)
    if t < T_RIDE[0] + 3.0 or t > T_GONE + 0.5:
        return None
    if t < T_LAND:
        return L + 40 + (land - L - 40) * smoothstep(T_RIDE[0] + 3.0, T_LAND, t) ** 0.7
    if t < T_FLEE + 0.5:
        return land + 6 * np.sin(2 * np.pi * t / 0.9)
    return land + (L + 60 - land) * smoothstep(T_FLEE + 0.5, T_GONE, t) ** 1.6


def render(G, seed=13):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_b = at(G, *BRUNNHILDE_AT)
    love = [e for e in N if e[4] == 'love']
    rides = [e for e in N if e[4] == 'ride']
    val = [e for e in N if e[4] == 'valhalla']
    vstep = sorted({e[0] for e in val})
    grief = [e for e in N if e[4] == 'grief']
    ring = sorted({e[0] for e in N if e[4] == 'ring'})
    refuse = sorted({e[0] for e in N if e[4] == 'refuse'})
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    jag = np.random.default_rng(seed).uniform(0.4, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        storm = smoothstep(T_THUNDER, T_RIDE[2], t) * (1 - smoothstep(T_CLEAR, T_RING, t)) \
            + smoothstep(T_FLEE - 1, T_FLEE + 1, t) * (1 - smoothstep(T_GONE - 1, T_GONE + 4, t))
        gods = smoothstep(T_VAL[0] - 0.4, T_VAL[0] + 0.4, t) * (1 - smoothstep(T_VAL[1], T_VAL[1] + 1.5, t))
        lv = {k: keys(t, [(0, START[k]), (T_GONE, START[k]), (D - 2, END[k])]) for k in START}
        lv['day'] *= 1 - 0.75 * min(1.0, storm + gods)
        lv['dawn'] *= 1 - 0.7 * min(1.0, storm + gods)
        fr = scene(S, T, lv)

        # the storm cloud: dark rolling cloud over the sky, lightning cracking whole runs
        if storm > 0:
            if t < T_RING:
                front = L - (L + 300) * smoothstep(T_THUNDER, T_RIDE[2] + 2, t)
                cover = smoothstep(front - 150, front + 150, d) * storm
            elif t < T_FLEE:
                cover = storm * np.ones_like(d)
            else:
                front = (L + 300) * smoothstep(T_FLEE, T_GONE + 2, t) - 150
                cover = smoothstep(front - 150, front + 150, d) * storm
            u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 300 + 0.6 * t))
            fr = fr * (1 - 0.7 * cover * S['sky'])[:, None]
            fr += light(CLOUD + (BOLT - CLOUD) * 0.2 * u[:, None], 0.85 * cover * (0.7 + 0.3 * u) * S['sky'])
            if t < T_RING and 0 < front < L:
                fr += light(BOLT, 0.5 * storm * np.exp(-((d - front) / 40) ** 2))
        for tb, run in bolts():
            a = t - tb
            if 0 <= a < 0.8:
                env = min(1.0, np.exp(-a / 0.08) + 0.8 * np.exp(-((a - 0.15) / 0.04) ** 2))
                fr += light(BOLT, env * (G.seg_of == run) * jag)

        # the Ride: every note an orange streak racing in from the east with the cloud front behind it
        for t0, dur, m, v, part, k in rides:
            a = t - t0
            if 0 <= a < 2.2 and m >= note('B3'):
                head = L - 1100 * a if k < 3 else at(G, *WALTRAUTE_AT) + 1100 * a
                trail = (d - head) * (1 if k < 3 else -1)
                fr += light(WALTRAUTE, 1.0 * np.exp(-a / 0.9) * np.exp(-((d - head) / 80) ** 2))
                fr += light(WALTRAUTE, 0.7 * np.exp(-a / 0.7) * (trail > 0) * np.exp(-np.clip(trail, 0, None) / 300))

        # Valhalla: the sky goes deep blue, every chord slams one whole run gold-white
        if gods > 0:
            fr += light(GODS, 0.75 * gods * S['sky'] * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 600 - 0.1 * t))))
        for j, t0 in enumerate(vstep):
            a = t - t0
            if 0 <= a < 1.6:
                run = G.seg_of == runs[j % len(runs)]
                fr += light(VALHALLA, 0.95 * np.exp(-a / 0.55) * run)
                fr += light(GODS, 0.5 * np.exp(-a / 0.9) * run)

        # Wotan's grief: slow blue waves breathing out from the summit, one per note
        for t0, dur, m, v, part, k in grief:
            a = t - t0
            if 0 <= a < 3.0:
                r = 1200 * (1 - np.exp(-a / 1.1))
                fr += light(GODS, 0.85 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - S['summit']) - r) / 160) ** 2))

        # the Ring: gold surges from Brünnhilde's hand, and the Rhine pulling at it from the east
        p_w = flight(G, t)
        for t0 in ring:
            a = t - t0
            if 0 <= a < 1.4:
                tgt = p_w if p_w is not None else L
                head = p_b + (tgt - p_b) * min(1.0, a / 0.6)
                lo, hi = min(p_b, head), max(p_b, head)
                fr += light(GOLD, 0.6 * np.exp(-a / 0.6) * smoothstep(lo - 30, lo, d) * smoothstep(hi + 30, hi, d))
                fr += light(GOLD, 1.0 * np.exp(-a / 0.6) * np.exp(-((d - head) / 60) ** 2))
                fr += light(RINGRED, 0.7 * np.exp(-a / 0.3) * np.exp(-((d - p_b) / 35) ** 2))
        if T_RING <= t < T_REFUSE[0]:
            a = t - T_RING
            for j in range(4):
                c = (L - ((a * 900 + j * 420) % 1700))
                fr += light(RHINE, 0.9 * np.exp(-((d - c) / 140) ** 2) * (c > p_b))

        # Brünnhilde refuses: silver shocks over the whole house, the Ring blazing on her hand
        for t0 in refuse:
            a = t - t0
            if 0 <= a < 1.8:
                r = 1600 * (1 - np.exp(-a / 0.5))
                fr += light(SILVER, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - r) / 110) ** 2))
                fr += light(GOLD, 0.8 * np.exp(-a / 0.4) * np.exp(-((d - p_b) / 40) ** 2))
        for t0 in T_REFUSE:
            a = t - t0
            if 0 <= a < 0.5:
                fr += light(SILVER, 0.45 * np.exp(-a / 0.12))

        # Brünnhilde's love: soft silver ripples
        for t0, dur, m, v, part, k in love:
            a = t - t0
            if 0 <= a < 2.2 and dur >= 0.4:
                r = 900 * a
                fr += light(SILVER, 0.8 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_b) - r) / 150) ** 2))
                fr += light(GOLD, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - p_b - 9) / 20) ** 2))

        # Waltraute: a blaze of orange over storm cloud; a burst where she lands
        if p_w is not None:
            fr += light(CLOUD, 0.6 * np.exp(-((d - p_w) / 90) ** 2))
            fr += light(WALTRAUTE, 0.45 * np.exp(-((d - p_w) / 160) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * t / RBEAT / 2)))
            fr = figure(fr, S, p_w, WALTRAUTE, 1.0, w=24)
            fr += light(WHITE, 0.5 * np.exp(-((d - p_w) / 5) ** 2))
        if T_LAND <= t < T_LAND + 1.5:
            a = t - T_LAND
            pl = at(G, *WALTRAUTE_AT)
            fr += light(WALTRAUTE, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - pl) - 1200 * a) / 90) ** 2))

        # Brünnhilde on the summit, the Ring glinting on her hand
        lvl = keys(t, [(0, BRUNNHILDE_START), (T_REFUSE[0], 0.95), (T_GONE, 0.95), (D - 2, BRUNNHILDE_END[2])])
        fr = figure(fr, S, p_b, SILVER, lvl)
        fr += light(GOLD, 0.7 * lvl * np.exp(-((d - p_b - 9) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, and the storm Waltraute rides in on and out on."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    sb = pan_at(at(G, *BRUNNHILDE_AT))
    east = pan_at(S['L'] - 60)
    land = pan_at(at(G, *WALTRAUTE_AT))

    def pan_w(t):
        p = flight(G, t)
        return pan_at(p) if p is not None else east

    o = Orchestra(M, level=1.4)

    def role(t, d, m, v, h):
        part, k = part_of(t, d, m, v, h)
        if part == 'ride':                                  # the Valkyries' figures: horns and trumpets, violins
            return [('horns', 0, 0, 0.75), ('trumpets', 0 if m < 72 else -12, -8, 0.45), ('violins', 0, -6, 0.45)]
        if part == 'ring':                                  # the Ring: flutes and clarinets
            return [('flutes', 0, 0, 0.6), ('clarinets', -12, -6, 0.5)]
        if part in ('refuse', 'valhalla'):                  # her refusal and Valhalla's glory: the full brass
            if m < 55:
                return [('trombones', 0, 0, 0.85), ('tuba', -12 if m >= 40 else 0, -4, 0.7)]
            return [('horns', 0, 0, 0.85), ('trumpets', 0, -6, 0.6)]
        return None

    def pan(t, m):
        if t < T_LAND or t >= T_FLEE:
            return pan_w(t) * 0.6
        return sb * 0.5

    o.tutti(tidy(EX['notes']), size=lambda t: 0.5 if T_RING <= t < T_REFUSE[0] else 1.0, role=role, pan=pan)
    for t0 in T_REFUSE:
        o.hit('crash', t0, 118, gain=0.7, pan=sb)
        o.hit('timpani', t0, 120, pitch=-3, gain=0.8, pan=sb)

    # the storm: far thunder, then a horse galloping on the clouds, a burst as she lands, and the same storm
    # carrying her off; between, while the sisters plead and refuse, the stage keeps quiet
    o.wind(0.0, T_RING + 2.0, level=lambda tt: 0.2 + 0.7 * smoothstep(0, T_LAND, tt), pan=east)
    o.wind(T_FLEE - 1.0, D, level=lambda tt: 0.9 - 0.6 * smoothstep(T_GONE - 3, D, tt), pan=lambda t: pan_w(t))
    o.thunder(T_THUNDER, near=0.1, pan=east, gain=0.8)
    for tb, run in bolts():
        o.thunder(tb, near=0.45 + 0.4 * (T_LAND - 3 < tb < T_FLEE + 3), pan=pan_at(at(G, run, 0.5)), gain=0.7)
    o.gallop(T_RIDE[0] + 3.0, T_LAND, beat=0.36, pan=pan_w, v=104)
    o.boom(T_LAND, land, 0.8)
    o.gallop(T_FLEE + 0.5, T_GONE, beat=0.34, pan=pan_w, v=108)
    o.effects([(0, 0), (T_CLEAR, 0), (T_RING - 0.5, -16), (T_FLEE - 1.5, -16), (T_FLEE, 0), (D, 0)])
