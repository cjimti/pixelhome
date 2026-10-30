"""The Gibichungs: the hall of the Gibichungs on the Rhine. The porch is the hall, torchlit amber under royal
purple drapes, its torches burning along the porch and the far walls (Left and the Side); Right is the
riverbank, reeds and wet stone, and at its free end the Rhine runs past in indigo and teal.

The music is Wagner's own, Act I as Solti's 1958 recording takes it: the opening of the act, the Gibichungs'
music and Gunther asking Hagen whether he sits on the Rhine in glory (bars 1-16), then Gutrune asking what deed
made Siegfried the greatest of heroes and Hagen's tale of the dragon he slew and the hoard he won (112-131). The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated on the brass for the
Gibichungs, oboe for Gutrune, tuba and basses under the dragon tale, horns and trumpets for the hero's fame.
Each torch catches with a crackle, the hall's fire burns low under the voices, Hagen's blows land on timpani and
gong, and the river rushes at Siegfried's name.

The torches catch one by one, each a white-hot pop and a spray of sparks, and the hall fills with light; every
long note of the Gibichungs' music sends a gold surge over the porch and out along a wing, and while Gunther
speaks each bar swells gold out from his throne. Hagen's blows knock the house dark, a black-violet shock out
from the shadows on Porch Left. Gutrune's question sends rose ripples out from her. For the dragon tale the hall
dims and a dark green coil shudders along the riverbank, gold glinting round Hagen as he names the hoard; at
"Siegfried" an emerald streak races in along the river; Hagen's blow falls again on "Solch' ungeheurer Tat", and
on the hero's fame emerald and gold sweep the house end to end on every accent, brighter each time.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD07'
TITLE = 'The Gibichungs'
KIND = 'show'
DESCRIPTION = ('A torchlit hall on the Rhine: King Gunther in gold, his sister Gutrune in rose, and in the shadows '
               'their half-brother Hagen, whose every word lands like a blow.')
VOICEOVER = ('On the banks of the Rhine stands the hall of the Gibichungs. '
             'And in its shadows, Hagen is waiting.')

K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1-16 and 112-131, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_TORCH = [0.3 + 0.5 * i for i in range(11)]        # the torches catch one by one, over the opening bars
FANFARE_BARS = (2, 3, 13, 14, 15)           # the Gibichungs' music, Gunther's gold
T_HAGEN = [BAR[4], BAR[15], BAR[126]]       # Hagen's blows: named, speaking, scheming
T_GUT = (BAR[112], BAR[118])                # Gutrune asks what deed made Siegfried the greatest hero
T_TALE = (BAR[118], BAR[125])               # Hagen tells of the dragon and the hoard
T_HORN = BAR[122]                           # "Siegfried": an emerald streak races in along the river
T_FAME = (BAR[125], D)               # "enttagte des Helden Ruhm": the hero's fame, blazing

AMBER = hexc('#ff8a20')
PURPLE = hexc('#6a10c0')
TORCH = hexc('#ffb040')
HEAT = hexc('#fff0a0')
REED = hexc('#2a6a20')
RIVER = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
FOAM = hexc('#14c080')
HAGEN = hexc('#7a00ff')
SPEAR = hexc('#c8d8ff')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
POTION = hexc('#a050ff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
WHITE = hexc('#ffffff')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)     # where GD08 picks it up
GUNTHER_AT = ('Porch Front', 0.62)          # on his throne
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)             # in the shadows
FIGS_END = dict(gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75))


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


RUNS = ['Left', 'Right', 'Side', 'Right', 'Left']
TORCHES = [('Left', 0.2), ('Left', 0.55), ('Left', 0.88), ('Porch Left', 0.2), ('Porch Left', 0.7),
           ('Porch Front', 0.15), ('Porch Front', 0.5), ('Porch Front', 0.85), ('Porch Right', 0.3),
           ('Porch Right', 0.8), ('Side', 0.6)]


def stage(G):
    """The hall of the Gibichungs as profiles over the house: the hall on the porch, its far walls on Left and the
    Side, torches along them, the riverbank on Right with the Rhine running past its free end."""
    d = G.pd
    rng = np.random.default_rng(1848)       # the same torches, drapes and river in every scene, so the cuts match
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    walls = np.isin(seg, ['Left', 'Side'])
    mid = at(G, 'Porch Front', 0.5)
    river = smoothstep(at(G, 'Right', 0.55), at(G, 'Right', 1.0), d)
    tp = np.array([at(G, s, u) for s, u in TORCHES])
    return dict(
        d=d, mid=mid, porch=porch, walls=walls, torch_at=tp,
        hall=porch * (0.6 + 0.4 * np.exp(-((d - mid) / 200) ** 2)) + walls * (0.45 + 0.2 * smooth_noise(rng, d, 50.0)),
        drape=(porch | walls) * (0.5 + 0.5 * np.sin(2 * np.pi * d / 140)) ** 2,
        torch=np.exp(-((d[None, :] - tp[:, None]) / 9) ** 2).sum(0),
        glow=np.exp(-((d[None, :] - tp[:, None]) / 45) ** 2).sum(0),
        bank=(seg == 'Right') * (1 - river) * (0.7 + 0.3 * smooth_noise(rng, d, 30.0)),
        river=river,
        fl=Flicker(rng, G.N, 3.0, 9.0),
        sway=Flicker(rng, G.N, 0.2, 0.7),
    )


def hall(S, T, lv):
    """The hall at shared time T with levels lv (hall, drapes, torches, bank, river, gloom)."""
    d, fl = S['d'], S['fl'](T)
    fr = light(AMBER, lv['hall'] * S['hall'] * (0.85 + 0.15 * fl))
    fr += light(PURPLE, lv['drapes'] * S['drape'] * (0.85 + 0.15 * S['sway'](T)))
    fr += light(TORCH, lv['torches'] * np.clip(S['torch'], 0, 1) * (0.75 + 0.25 * fl))
    fr += light(AMBER, 0.6 * lv['torches'] * np.clip(S['glow'], 0, 1) * (0.8 + 0.2 * fl))
    fr += light(REED, lv['bank'] * S['bank'])
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 90 - 0.55 * T)) * np.sin(2 * np.pi * (d / 230 - 0.2 * T) + 1.0)
    fr += light(RIVER + (TEAL - RIVER) * u[:, None], lv['river'] * S['river'])
    fr += light(FOAM, lv['river'] * S['river'] * np.clip(u - 0.75, 0, None) * 3)
    return fr * (1 - lv['gloom'])


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the hall, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def wave(S, p, a, speed=1200.0, width=90.0, life=0.9):
    """A ring running out both ways from p, a seconds after it starts -> perceptual."""
    return np.exp(-a / life) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2) * (a >= 0)


def blow(fr, S, p, a, s=1.0):
    """Hagen's blow, a seconds after it lands at p: the house knocked dark and a black-violet shock out from him."""
    if not 0 <= a < 2.5:
        return fr
    fr = fr * (1 - 0.9 * s * np.exp(-a / 0.9))
    fr = fr + light(HAGEN, 0.5 * s * np.exp(-a / 0.35))
    fr = fr + light(HAGEN, s * wave(S, p, a, 1100.0, 230.0, 1.2))
    fr = fr + light(SPEAR, 0.9 * s * np.exp(-a / 0.12) * np.exp(-((S['d'] - p + 18) / 8) ** 2))
    return fr


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k, trem). The opening and the
    swell before Hagen speaks are the Gibichungs' music ('fanfare'); Gutrune's question is hers ('gutrune'); the
    dragon tale's shuddering figures are 'tale', its low notes the hoard ('ring'); the hero's fame is 'fame'; the
    rest is 'hall'. 'torch' marks each torch catching; it makes no sound of its own."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        b = bar_of(t)
        if b in FANFARE_BARS:
            part = 'fanfare'
        elif T_GUT[0] <= t < T_GUT[1]:
            part = 'gutrune' if h == 0 else 'hall'
        elif T_TALE[0] <= t < T_TALE[1]:
            part = 'tale' if h == 0 else 'ring'
        elif T_FAME[0] <= t < T_FAME[1]:
            part = 'fame'
        else:
            part = 'hall'
        N.append((t, d, m, v, part, b, trem))
    for i, t0 in enumerate(T_TORCH):
        N.append((t0, 0.4, 60, 0, 'torch', i, False))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=7):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    fan = [e for e in N if e[4] == 'fanfare' and e[1] >= 0.2]
    gut = [e for e in N if e[4] == 'gutrune']
    ring = [e for e in N if e[4] == 'ring' and e[1] >= 0.3]
    fame = accents([e for e in N if e[4] == 'fame'], n=3, space=0.35)
    tale = [e for e in N if e[4] == 'tale']
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    order = np.random.default_rng(seed).permutation(len(TORCHES))
    glint_at = np.random.default_rng(seed + 1).uniform(p_hag - 220, p_hag + 260, len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lit = smoothstep(0.0, T_TORCH[-1] + 0.8, t)
        lv['hall'] *= 0.25 + 0.75 * lit
        lv['drapes'] *= 0.2 + 0.8 * lit
        lv['torches'] *= lit
        fr = hall(S, T, lv)

        # the torches catch one by one: a white-hot pop and a spray of sparks at each
        for i, t0 in enumerate(T_TORCH):
            a = t - t0
            if 0 <= a < 1.2:
                p = S['torch_at'][order[i]]
                fr += light(HEAT, min(1.0, 1.2 * np.exp(-a / 0.12)) * np.exp(-((d - p) / 14) ** 2))
                fr += light(TORCH, 0.8 * wave(S, p, a, 700.0, 40.0, 0.35))

        # the Gibichungs' music: every long note a gold surge over the porch and out along a wing
        for j, (t0, dur, m, v, part, b, _) in enumerate(fan):
            a = t - t0
            if 0 <= a < 1.6:
                s = (v / 127) ** 1.5
                run = G.seg_of == RUNS[j % len(RUNS)]
                fr += light(GUNTHER, 0.85 * s * np.exp(-a / 0.35) * (S['porch'] | run))
                fr += light(GUNTHER, s * wave(S, p_gun, a, 1300.0, 200.0, 0.8))

        # Gunther speaking: each bar a slow gold swell out from his throne
        for b in range(4, 13):
            a = t - BAR[b]
            if 0 <= a < 2.4:
                fr += light(GUNTHER, 0.6 * wave(S, p_gun, a, 650.0, 160.0, 1.0))

        # Gutrune's question: every note of her line a rose ripple from her; the long ones tint every run
        for tn, dn, m, v, part, b, _ in gut:
            a = t - tn
            if 0 <= a < 2.0:
                fr += light(GUTRUNE, 0.95 * wave(S, p_gut, a, 800.0, 200.0, 0.9))
                if dn > 0.6:
                    fr += light(GUTRUNE, 0.55 * np.exp(-a / (dn + 0.3)) * smoothstep(0, 0.1, a))

        # the dragon tale: the hall dims, and a dark green coil shudders along the river bank with the strings
        if T_TALE[0] - 1 <= t < T_TALE[1] + 1:
            g = smoothstep(T_TALE[0] - 1, T_TALE[0] + 1, t) * (1 - smoothstep(T_TALE[1], T_TALE[1] + 1, t))
            fr = fr * (1 - 0.45 * g)
            coil = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 120 - 1.6 * t))
            fr += light(REED, 0.9 * g * coil * (0.6 + 0.4 * (G.seg_of == 'Right')))
            for tn, dn, m, v, part, b, _ in tale[::4]:
                a = t - tn
                if 0 <= a < 0.5:
                    fr += light(FOAM, 0.5 * g * np.exp(-a / 0.15) * np.exp(-((d - (L - (tn * 487) % L)) / 25) ** 2))

        # the hero's fame: emerald and gold sweeping the house end to end on every accent, brighter each time
        for j, t0 in enumerate(fame):
            a = t - t0
            if 0 <= a < 1.4:
                g = 0.6 + 0.4 * min(1.0, j / 8)
                fr += light(SIEGFRIED if j % 2 == 0 else GOLD, g * wave(S, S['mid'], a, 1500.0, 280.0, 0.8))
                fr += light(SIEGFRIED if j % 2 == 0 else GOLD, 0.55 * g * np.exp(-a / 0.3) * (G.seg_of == RUNS[j % 5]))

        # Siegfried's horn far down the river: an emerald streak racing in from the free end of Right, fading
        if T_HORN <= t < T_HORN + 4.0:
            a = t - T_HORN
            p = L + 20 - 520 * a
            fr += light(SIEGFRIED, np.exp(-a / 1.6) * np.exp(-((d - p) / 70) ** 2))
            fr += light(SIEGFRIED, 0.7 * np.exp(-a / 0.3) * (G.seg_of == 'Right'))
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 1.6) * smoothstep(p, p + 300, d) * (d > p) * np.exp(-(d - p) / 300))
            fr += light(HEAD, 0.8 * np.exp(-a / 1.6) * np.exp(-((d - p) / 8) ** 2))

        # the Ring: gold glints swirling round Hagen
        for j, (t0, dur, m, v, part, k, _) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.2:
                fr += light(GOLD, 0.95 * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.05, a)
                            * np.exp(-((d - glint_at[j]) / (35 + 45 * a)) ** 2))

        # the three of them: Gunther from the start, Gutrune with her motif, Hagen from his first blow
        fr = figure(fr, S, p_gun, GUNTHER, 0.8 * smoothstep(2.0, 5.0, t))
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8 * smoothstep(T_GUT[0] - 1.5, T_GUT[0] + 0.5, t))
        if t >= T_HAGEN[0]:
            fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
            fr = figure(fr, S, p_hag, HAGEN, 0.75)
            fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))

        # Hagen's blows
        for k, t0 in enumerate(T_HAGEN):
            fr = blow(fr, S, p_hag, t - t0, 1.0 if k == 1 else 0.7)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the torches and the river."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.1)
    gun, gut, hag = (pan_at(at(G, *x)) for x in (GUNTHER_AT, GUTRUNE_AT, HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))

    def role(t, d, m, v, h):
        if T_GUT[0] <= t < T_GUT[1] and h == 0:             # Gutrune's line: oboe over the violins
            return [('oboes', 0, 6, 0.75), ('violins', 0, -10, 0.35)]
        if T_TALE[0] <= t < T_TALE[1] and h == 1:           # the dragon and the hoard: tuba and basses
            return [('tuba', 0, 0, 0.7), ('basses', 0, -6, 0.55)] if m < 50 else [('bassoons', 0, 0, 0.6)]
        if T_FAME[0] <= t < T_FAME[1] and h == 0:           # the hero's fame: horns and trumpets
            return [('horns', 0, 0, 0.6), ('trumpets', 0, -12, 0.35), ('violins', 0, -8, 0.4)]
        return None

    def size(t):
        if T_GUT[0] <= t < T_GUT[1]:
            return 0.4
        return 0.9 if t < BAR[4] or BAR[13] <= t < BAR[16] or t >= T_FAME[0] else 0.6

    notes = [[t, d, m, v, h, trem] for t, d, m, v, h, trem in tidy(EX['notes'])]
    o.tutti(notes, size=size, role=role, pan=lambda t, m: gut if T_GUT[0] <= t < T_GUT[1] else hag if
            T_TALE[0] <= t < T_TALE[1] and m < 50 else 0.0)
    # the stage: the torches catching, the hall's fire, Hagen's blows, the river at Siegfried's name
    for i, t0 in enumerate(T_TORCH):
        tp = pan_at(at(G, *TORCHES[i % len(TORCHES)]))
        o.fire(t0, t0 + 0.6, level=1.0, pan=tp, crackle=40, seed=30 + i)
    o.fire(T_TORCH[-1], D, level=0.25, pan=gun, crackle=5, seed=50)
    for k, t0 in enumerate(T_HAGEN):
        o.hit('timpani', t0, 120, pitch=-7, gain=0.7, pan=hag)
        o.hit('gong', t0 + 0.02, 100 + 10 * (k == 1), gain=0.45, pan=hag)
    o.wind(T_HORN - 0.5, T_HORN + 4.0, level=0.8, pan=river, seed=61)
    o.hit('cymbal swell', T_FAME[0] - 1.6, 96, gain=0.35)
    o.hit('crash', BAR[129], 116, gain=0.45)
    # the torches lead the opening; the hall's fire backs right off under the voices and Gutrune's line
    o.effects([(0, 0), (BAR[4] - 0.3, 0), (BAR[4] + 0.5, -10), (T_HORN - 0.5, -10), (T_HORN, -2),
               (T_HORN + 4.0, -2), (T_HORN + 5.0, -10), (D, -10)])
