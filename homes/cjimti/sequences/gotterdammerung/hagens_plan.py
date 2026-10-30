"""Hagen's Plan: the same torchlit hall. Gunther has no wife and Gutrune no husband, and Hagen has the answer.

The music is Wagner's own, Act I as Solti's 1958 recording takes it: Hagen telling of a woman, the most glorious
in the world, on a rock behind a wall of fire that only the bravest can break through, and Gunther wondering if
he dares (bars 72-89); Hagen reminding Gutrune of the potion in the chest that will bind the hero to her and make
him forget every woman before her, to its fortissimo "Träte nun Siegfried ein" (193-206); and Gunther's "Gepriesen
sei Grimhild'" (227-232). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
fire's shimmer on violins and harp over horns, the potion on clarinets, bassoons and cellos, swelling to the
trombones, Gunther's thanks on violins and trumpets. A roar of fire rises under the fire music, kept under
Hagen's voice; his blows land on timpani and gong, a gong scrape as the potion floods, a crash at the end.

As Hagen tells of the bride, fire licks up over the whole house in moving tongues, rising and falling with the
music, and far off on Left a silver figure sleeps in it; Gunther's doubts flash gold from his throne. Then the
potion seeps out of the shadows: a sickly violet glow creeping out from Hagen with a ragged edge, pulsing on
every chord, while gold streaks race in from both ends and pour into him, the hoard he means to have. Gutrune's
rose pushes it back for a moment; then the violet floods the whole house. Gunther's gold takes the hall back one
run after another and the violet drains back into Hagen, leaving the hall in torchlight and the plan made.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD08'
TITLE = "Hagen's Plan"
KIND = 'show'
DESCRIPTION = ('Hagen has a plan: a bride for Gunther, a husband for Gutrune, and a potion to make it happen. '
               'Its sickly violet seeps out of the shadows until it floods the whole house.')
VOICEOVER = ('A sleeping bride for the king, and a hero for his sister. '
             'All it takes, says Hagen, is a drink.')

K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 72-89, 193-206 and 227-232, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_FIRE = (BAR[72], BAR[88])                 # "Ein Weib weiß ich": the bride on her rock behind the fire
T_ASK = BAR[85]                             # "Vermag das mein Mut zu besteh'n?": Gunther's gold
T_HAGEN = [BAR[88], BAR[193], BAR[204]]     # Hagen's blows
T_POTION = (BAR[193], BAR[206])             # "Gedenk' des Trankes": the potion creeping out, then flooding
T_RING = [BAR[195], BAR[197]]               # gold pouring into Hagen: the hoard he means to have
T_GUT = BAR[201]                            # "bindet er liebend an dich": Gutrune's rose pushes back
T_FLOOD = BAR[203]                          # the potion floods the house
T_GUN = BAR[227]                            # "Gepriesen sei Grimhild'": Gunther's gold takes the hall back

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

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD07 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD09 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)
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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k, trem). Hagen's tale of the fire is
    'fire', the potion 'potion', Gunther's thanks 'fanfare'."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        part = 'fire' if t < T_POTION[0] else 'potion' if t < T_GUN else 'fanfare'
        N.append((t, d, m, v, part, h, trem))
    return sorted(N, key=lambda e: e[0])


def potion_reach(t):
    """How far the violet has crept from Hagen (path units) and how strongly."""
    a0, a1 = T_POTION
    reach = keys(t, [(a0, 0.0), (a0 + 12.0, 700.0), (T_GUT, 700.0), (T_GUT + 2, 150.0), (T_FLOOD, 150.0),
                     (T_FLOOD + 6.0, 2600.0), (T_GUN, 2600.0), (T_GUN + 6.0, 0.0)])
    level = keys(t, [(a0, 0.0), (a0 + 1.0, 0.65), (T_GUT, 0.7), (T_GUT + 2, 0.35), (T_FLOOD, 0.4), (T_FLOOD + 3, 0.9),
                     (T_GUN, 0.85), (T_GUN + 6.5, 0.0)])
    return float(reach), float(level)


def render(G, seed=8):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    pot = np.array(accents([e for e in N if e[4] == 'potion'], n=2, space=0.5))
    gut = [e for e in N if T_GUT <= e[0] < T_FLOOD and e[5] == 0 and e[1] >= 0.3]
    ring = [(t0, 1.0) for t0 in T_RING]
    fan = accents([e for e in N if e[4] == 'fanfare'], n=3, space=0.4)
    ask = accents([e for e in N if T_ASK <= e[0] < T_HAGEN[0]], n=3, space=0.5)
    loud = np.zeros(F)
    for e in N:
        loud[min(F - 1, int(e[0] / DT))] += (e[3] / 127) ** 2
    loud = np.convolve(loud, np.exp(-np.arange(int(1.0 / DT)) * DT / 0.4))[:F]
    loud = np.clip(loud / np.percentile(loud[loud > 0], 97), 0, 1)
    p_bride = at(G, 'Left', 0.2)
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    rng = np.random.default_rng(seed)
    ragged = smooth_noise(rng, d, 25.0)
    tendril = Flicker(rng, G.N, 0.3, 1.1)
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    streak_from = rng.choice([0.0, L], len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = hall(S, T, START)

        # the bride Hagen tells of: fire licking up over the whole house with the strings' shimmer, rising with the
        # music, and in it, far off on Left, a silver figure asleep
        if t < T_FIRE[1] + 2.0:
            g = smoothstep(0.0, 2.5, t) * (1 - smoothstep(T_FIRE[1] - 0.5, T_FIRE[1] + 2.0, t)) * (0.35 + 0.65 * loud[f])
            q = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.9 * t)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 1.2 * t) + 1.3)
                 + 0.13 * np.sin(2 * np.pi * (d / 67 - 2.1 * t) + 2.1) + 0.06 * S['fl'](T))
            q = np.clip((q - 0.2) * 1.6, 0, 1)
            fr = fr * (1 - 0.5 * g)
            fr += light(TORCH + (HEAT - TORCH) * q[:, None], g * (0.35 + 0.75 * q) * (1 - 0.6 * S['porch']))
            fr += light(BLOOD, 0.5 * g * (1 - q) * (1 - S['porch']))
            fr = figure(fr, S, p_bride, WHITE, 0.7 * smoothstep(1.0, 4.0, t) * (1 - smoothstep(T_FIRE[1] - 1, T_FIRE[1] + 1, t)))
        for t0 in ask:                      # Gunther: can I dare it? gold flashes from his throne
            a = t - t0
            if 0 <= a < 1.4:
                fr += light(GUNTHER, 0.9 * wave(S, p_gun, a, 1200.0, 200.0, 0.8))

        # the potion: a sickly violet creeping out from Hagen with a ragged edge, pulsing on every chord
        reach, plev = potion_reach(t)
        if plev > 0.001:
            dist = np.abs(d - p_hag) + 60 * ragged + 40 * tendril(T)
            cover = smoothstep(reach + 40, reach - 80, dist)
            j = int(np.searchsorted(pot, t, side='right')) - 1
            pulse = np.exp(-(t - pot[j]) / 0.4) if j >= 0 and t - pot[j] < 3 else 0.0
            fr = fr * (1 - 0.8 * plev * cover)[:, None]
            fr += light(POTION, plev * cover * (0.55 + 0.45 * pulse + 0.15 * tendril(T)))
            fr += light(WHITE, 0.25 * plev * pulse * np.exp(-((dist - reach) / 30) ** 2))

        # Gutrune pushes back: a rose wave from her driving the violet off, every note a ripple
        for tn, dn, m, v, part, h, _ in gut:
            a = t - tn
            if 0 <= a < 2.0:
                fr += light(GUTRUNE, 0.95 * wave(S, p_gut, a, 800.0, 220.0, 0.9))
                if dn > 0.6:
                    fr += light(GUTRUNE, 0.5 * np.exp(-a / (dn + 0.3)) * smoothstep(0, 0.1, a))

        # the Ring: gold streaks race in from the ends of the house and pour into Hagen
        for j, (t0, dur) in enumerate(ring):
            a = t - t0
            if 0 <= a < 1.4:
                p0 = streak_from[j]
                p = p0 + (p_hag - p0) * min(1.0, a / 1.0) ** 1.5
                tail = np.clip((d - p) / (p0 - p + 1e-6), 0, 1) * (np.sign(p0 - p) * (d - p) > 0)
                fr += light(GOLD, np.exp(-((d - p) / 80) ** 2) * (1 - smoothstep(1.0, 1.4, a)))
                fr += light(GOLD, 0.6 * np.exp(-np.abs(d - p) / 250) * tail * (1 - smoothstep(0.9, 1.4, a)))
                if a >= 1.0:
                    fr += light(HEAT, 0.9 * np.exp(-(a - 1.0) / 0.12) * np.exp(-((d - p_hag) / 25) ** 2))

        # Gunther's fanfare against the violet: gold takes one run after another
        for i, t0 in enumerate(fan):
            a = t - t0
            if 0 <= a < 1.4:
                run = G.seg_of == runs[i % len(runs)]
                fr = fr * (1 - 0.6 * np.exp(-a / 0.45) * run)[:, None]
                fr += light(GUNTHER, 1.0 * np.exp(-a / 0.55) * run)
                fr += light(GUNTHER, 0.8 * wave(S, p_gun, a, 1300.0, 180.0, 0.7))

        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75 + 0.2 * plev)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        for k, t0 in enumerate(T_HAGEN):
            fr = blow(fr, S, p_hag, t - t0, 1.0 if k == 1 else 0.75)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: harp and violins for the fire Hagen describes, clarinets
    and bassoons for the potion, Gunther's brass at the end; Hagen's blows on timpani and gong."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.15)
    gun, hag = pan_at(at(G, *GUNTHER_AT)), pan_at(at(G, *HAGEN_AT))

    def role(t, d, m, v, h):
        if t < T_POTION[0]:
            if h == 0 and d < 0.3:                          # the fire's shimmer: violins and harp
                return [('violins', 0, -10, 0.45), ('harp', 0, -6, 0.35)] + \
                    ([('flutes', 0, -16, 0.3)] if m >= 77 else [])
            if h == 1 and d >= 0.4:                         # under it, the horns
                return [('horns', 0, -4, 0.7)] + ([('trombones', 0, -8, 0.5)] if v >= 110 else [])
        elif t < T_GUN:
            if h == 1:                                      # the potion creeping: bassoons, clarinets, cellos
                return [('bassoons', 0, 0, 0.6), ('cellos', 0, -6, 0.5)] + \
                    ([('trombones', 0, -6, 0.55), ('tuba', -12, -10, 0.4)] if v >= 115 else [])
            return [('clarinets', 0, 0, 0.6), ('violas', 0, -8, 0.4)] + \
                ([('horns', 0, -6, 0.55)] if v >= 115 else [])
        elif h == 0:                                        # Gunther's thanks: violins, trumpets on the top
            return [('violins', 0, -4, 0.55)] + ([('trumpets', 0, -10, 0.4)] if d >= 0.3 else [])
        return None

    o.tutti([[t, d, m, v, h, tr] for t, d, m, v, part, h, tr in compose()], size=lambda t: 0.9, role=role,
            pan=lambda t, m: hag if T_POTION[0] <= t < T_GUN else gun if t >= T_GUN else 0.0)
    # the fire Hagen conjures: a roar that rises with the music, kept under his voice
    o.fire(0.5, T_FIRE[1] + 1.5, level=lambda tt: 0.4 + 0.6 * ((tt > BAR[79]) & (tt < BAR[86])), pan=0.0, crackle=8)
    for k, t0 in enumerate(T_HAGEN):
        o.hit('timpani', t0, 122, pitch=-7, gain=0.75, pan=hag)
        o.hit('gong', t0 + 0.02, 104 + 10 * (k == 1), gain=0.5, pan=hag)
    o.hit('gong scrape', T_FLOOD, 110, gain=0.6, pan=hag)
    o.hit('cymbal swell', T_FLOOD - 1.2, 100, gain=0.4)
    o.hit('crash', BAR[231], 118, gain=0.5, pan=gun)
    o.effects([(0, -10), (BAR[79], -10), (BAR[80], -3), (BAR[85], -3), (BAR[86], -12), (D, -12)])
