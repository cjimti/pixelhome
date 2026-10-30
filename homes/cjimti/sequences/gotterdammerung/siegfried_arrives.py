"""Siegfried Arrives: the hall of the Gibichungs, and a horn on the river.

The music is Wagner's own, Act I as Solti's 1958 recording takes it: "Vom Rhein her tönt das Horn", Siegfried's
horn call ringing up the river and his boat coming into sight, "in einem Nachen Held und Roß" (bars 262-278);
then the boat driving against the stream, Hagen's "Hoiho!", Siegfried's answer, "Hieher! Hier lege an!", and the
fortissimo "Heil! Siegfried, teurer Held!" with the Curse beneath it (309-340). The notes come from the Wagner
Ring Dataset's piano reduction (pixelhome/ring.py): the horn call on horns, echoing off the far bank; harp and
violins for his answer; the brass for the greeting; tuba and trombones for the Curse. The river rushes, the oars
splash on every stroke, the keel grounds with a boom and Grane leaps ashore; the effects lead the arrival and
drop away under the voices and the greeting.

Every note of the horn call flashes the riverbank emerald and sends a wave of it through the house. His boat
comes up the river, an emerald comet with a wake of teal and white foam, and every stroke of the oars throws a
burst of foam and a ripple of river light across the whole hall. Hagen hails him in violet, he answers in
emerald, and he leaps ashore at the hall's door in a white-hot flash; on "Heil! Siegfried!" his emerald sweeps
the runs one by one until the house is green, and under it the Curse seeps up blood red from Hagen in the
shadows, out to both ends, his blow falling as the act darkens.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD09'
TITLE = 'Siegfried Arrives'
KIND = 'show'
DESCRIPTION = ("A horn on the river, and Siegfried's boat lands at the hall. Hagen hails him by name, and under "
               'the welcome a curse seeps up blood red.')
VOICEOVER = ('A horn sounds on the Rhine. Siegfried has come to the hall of the Gibichungs, '
             'and Hagen greets him by name.')

K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 262-278 and 309-340, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_BOAT = (BAR[270], BAR[330])               # the boat comes up the river; he leaps ashore on "Hier lege an!"
T_HOIHO = (BAR[313], BAR[319])              # Hagen hails him: "Hoiho! Wohin, du heit'rer Held?"
T_ANSWER = (BAR[319], BAR[326])             # "Zu Gibich's starkem Sohne"
T_WALK = (BAR[330] + 1.0, BAR[335])         # he walks up into the hall
T_HEIL = BAR[333]                           # "Heil! Siegfried, teurer Held!"
T_CURSE = [BAR[335], BAR[339]]              # the Curse beneath it
T_HAGEN = [BAR[339]]

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

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD08 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD10 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)
ASHORE_AT = ('Right', 0.15)                 # where he lands
SIEGFRIED_AT = ('Porch Front', 0.85)        # beside the throne
FIGS_END = dict(gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75),
                siegfried=(*SIEGFRIED_AT, 0.85))


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand, trem). The horn's loud notes
    before the boat are his horn call ('horn'); the boat's music is 'row'; Hagen's hail 'hoiho'; Siegfried's answer
    'answer'; the landing and the greeting 'heil', its low notes from the Curse on 'curse'."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        b = bar_of(t)
        if b <= 267:
            part = 'horn' if v >= 100 else 'row'
        elif t < T_HOIHO[0]:
            part = 'row'
        elif t < T_ANSWER[0]:
            part = 'hoiho'
        elif t < T_ANSWER[1]:
            part = 'answer'
        elif t >= T_CURSE[0] and h == 1 and m < 43:
            part = 'curse'
        else:
            part = 'heil'
        N.append((t, d, m, v, part, h, trem))
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """Siegfried's place at time t: up the river, ashore, then up into the hall."""
    L = G.pd.max()
    shore, home = at(G, *ASHORE_AT), at(G, *SIEGFRIED_AT)
    if t < T_BOAT[1]:
        return L + 40 + (shore - L - 40) * smoothstep(T_BOAT[0], T_BOAT[1], t) ** 0.8
    return shore + (home - shore) * smoothstep(*T_WALK, t)


def render(G, seed=9):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    horn = accents([e for e in N if e[4] == 'horn'], n=1, space=0.35)
    heil = accents([e for e in N if e[4] == 'heil' and e[0] >= T_HEIL], n=3, space=0.5)
    curse = [(T_CURSE[0], T_CURSE[1] - T_CURSE[0], 0), (T_CURSE[1], D - T_CURSE[1], 1)]
    rows = [BAR[b] for b in list(range(271, 278)) + [310, 311, 312] + list(range(326, 331))]
    hail = [BAR[b] for b in range(313, 318)]
    answer = accents([e for e in N if e[4] == 'answer'], n=2, space=0.9)
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    right = G.seg_of == 'Right'
    runs = ['Right', 'Porch Right', 'Porch Front', 'Porch Left', 'Left', 'Side']
    foam = Flicker(np.random.default_rng(seed), G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['river'] += 0.3 * smoothstep(0, 2, t) * (1 - smoothstep(T_BOAT[1], T_BOAT[1] + 4, t))
        fr = hall(S, T, lv)
        p = where(G, t)

        # the horn call: every note flashes the whole riverbank emerald and foams the river
        for t0 in horn:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SIEGFRIED, 0.85 * np.exp(-a / 0.3) * right)
                fr += light(WHITE, 0.5 * np.exp(-a / 0.2) * S['river'] * np.clip(foam(T), 0, 1))
                fr += light(SIEGFRIED, wave(S, L, a, 1400.0, 260.0, 0.9))

        # the boat: an emerald comet up the river with a wake of teal and white foam behind it
        if T_BOAT[0] - 0.5 <= t < T_BOAT[1] + 0.5:
            wake = (d > p) * np.exp(-(d - p) / 260) * right
            fr += light(TEAL, 0.9 * wake)
            fr += light(WHITE, 0.7 * wake * np.clip(foam(T) - 0.3, 0, 1))
        for t0 in rows:                     # each stroke of the oars: a burst of white foam at the boat
            a = t - t0
            if 0 <= a < 0.9 and t < T_BOAT[1]:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.25) * np.exp(-((d - p - 25) / 30) ** 2))
                fr += light(TEAL, 0.7 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p) - 260 * a) / 40) ** 2) * right)
            if 0 <= a < 1.6 and t < T_BOAT[1]:
                fr += light(TEAL, 0.65 * wave(S, p, a, 1000.0, 200.0, 0.9))
                fr += light(FOAM, 0.4 * wave(S, p, a - 0.1, 1000.0, 60.0, 0.6))
        for t0 in hail:                     # "Hoiho!": Hagen's call reaching out to the boat in violet
            a = t - t0
            if 0 <= a < 1.6:
                fr += light(HAGEN, 0.9 * wave(S, p_hag, a, 1100.0, 120.0, 0.8))
        for t0 in answer:                   # Siegfried answers from the boat: emerald rings out over the house
            a = t - t0
            if 0 <= a < 1.6:
                fr += light(SIEGFRIED, wave(S, p, a, 1200.0, 220.0, 0.9))
        if T_BOAT[1] <= t < T_BOAT[1] + 1.5:
            a = t - T_BOAT[1]
            fr += light(HEAD, min(1.0, 1.3 * np.exp(-a / 0.15)) * np.exp(-((d - p) / 30) ** 2))
            fr += light(SIEGFRIED, wave(S, p, a, 1600.0, 130.0, 0.6))

        # "Heil, Siegfried!": each note of his motif sweeps one more run emerald until the house is green
        for i, t0 in enumerate(heil):
            a = t - t0
            if 0 <= a < 6.0:
                run = G.seg_of == runs[i % len(runs)]
                fr += light(SIEGFRIED, (0.95 * np.exp(-a / 0.5) + 0.6 * (1 - smoothstep(3.0, 6.0, a))) * run)
                fr += light(HEAD, 0.6 * np.exp(-a / 0.15) * run)

        # the Curse beneath: blood red seeping up through everything from Hagen, out to both ends
        for t0, dur, k in curse:
            a = t - t0
            if 0 <= a < dur + 2.5:
                reach = min(1.0, a / 2.0) * L
                seep = smoothstep(reach + 80, reach - 80, np.abs(d - p_hag))
                g = (0.55 + 0.25 * k) * np.exp(-max(a - dur, 0) / 1.0) * smoothstep(0, 0.2, a)
                fr += light(BLOOD, g * seep * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 160 - 0.8 * t))))

        # the four of them
        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        if t >= T_BOAT[0] - 0.5:
            lvl = 0.85 * smoothstep(T_BOAT[0] - 0.5, T_BOAT[0] + 0.5, t)
            fr = figure(fr, S, p, SIEGFRIED, lvl)
            fr += light(HEAD, 0.8 * lvl * np.exp(-((d - p) / 6) ** 2))
        for t0 in T_HAGEN:
            fr = blow(fr, S, p_hag, t - t0, 1.0)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the river, the oars and the landing."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.9)
    hag = pan_at(at(G, *HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))
    boat = lambda t: pan_at(where(G, t))

    def role(t, d, m, v, h):
        b = max(mm for mm, bt in EX['bars'] if bt <= t + 1e-6)
        if b <= 267 and v >= 100:                           # his horn call from the river, and its echo
            return [('horns', 0, 4, 0.9)]
        if T_ANSWER[0] <= t < T_ANSWER[1] and h == 0:       # his answer: harp and violins glinting
            return [('violins', 0, -8, 0.45), ('harp', 0, 0, 0.45)]
        if t >= T_CURSE[0] and h == 1 and m < 43:           # the Curse under the greeting
            return [('tuba', 0, 0, 0.7), ('trombones', 12, -4, 0.6), ('basses', 12, -4, 0.5)]
        if t >= T_HEIL and h == 0 and d >= 0.3:
            return [('horns', 0, 0, 0.65), ('trumpets', 0, -10, 0.4), ('violins', 0, -6, 0.45)]
        return None

    notes = [[t, d, m, v, h, tr] for t, d, m, v, part, h, tr in compose()]
    o.tutti(notes, size=lambda t: 1.0 if t >= T_HEIL else 0.7, role=role,
            pan=lambda t, m: boat(t) if t < T_BOAT[1] else 0.0)
    for t, d, m, v, part, h, tr in compose():
        if part == 'horn':
            o.play('horns', m, t + 0.35, d, v - 30, -river * 0.6, 0.3)     # the echo off the far bank
    # the stage: the river, the oars, the landing, the greeting
    o.wind(0.5, T_BOAT[1] + 3.0, level=lambda tt: 0.35 + 0.25 * (tt >= T_BOAT[0]), pan=river, seed=91)
    for t0 in [BAR[b] for b in list(range(271, 278)) + [310, 311, 312] + list(range(326, 331))]:
        M.add('fx', np.vstack([whoosh(0.45, 2200, 500, 0.5, seed=int(t0 * 10))[0]] * 2), t0, 0.7, boat(t0))
    o.boom(T_BOAT[1], boat(T_BOAT[1] - 0.1), 0.6)                       # the keel grounding on the bank
    o.hoof(T_BOAT[1] + 0.25, boat(T_BOAT[1]), 118)                       # Grane leaps ashore
    o.hoof(T_BOAT[1] + 0.45, boat(T_BOAT[1]), 110)
    o.gallop(T_WALK[0], T_WALK[1], beat=0.6, pan=lambda tt: pan_at(where(G, tt)), v=80, gain=0.6)
    o.hit('cymbal swell', T_HEIL - 1.5, 100, gain=0.4)
    o.hit('crash', BAR[335], 122, gain=0.55)
    o.hit('timpani roll', T_CURSE[1], 110, pitch=-6, gain=0.6, pan=hag)
    o.hit('gong', T_HAGEN[0] + 0.02, 112, gain=0.55, pan=hag)
    o.hit('timpani', T_HAGEN[0], 124, pitch=-7, gain=0.7, pan=hag)
    # the river and the oars lead the arrival; they drop under the voices and right away under the greeting
    o.effects([(0, -4), (T_BOAT[0], -1), (T_HOIHO[0] - 0.3, -1), (T_HOIHO[0] + 0.5, -8), (T_ANSWER[1], -8),
               (T_ANSWER[1] + 1, -2), (T_BOAT[1] + 1.0, -2), (T_HEIL - 0.5, -12), (D, -12)])
