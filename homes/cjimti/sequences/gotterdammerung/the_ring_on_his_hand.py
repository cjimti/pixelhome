"""The Ring on His Hand: the shore in a red morning, a sea of the vassals' torches over every run, Hagen
ultraviolet at the doors by his spear, Gunther and Gutrune on Right. A boat comes up the river: Gunther leads in
his bride. Brünnhilde comes in from the free end of Right pale and dimmed, a faint silver with her eyes down,
while the men hail them ("Willkommen! Heil dir, Gunther!"), every great chord sending gold and silver waves over
the torches.

Then the hall's doors open and Siegfried comes out of them, emerald, and crosses to the corner of the porch.
She sees him ("Siegfried ... hier? Gutrune?"): her silver shudders, the torches flicker. Then she sees the Ring on
his hand ("Ha! Der Ring an seiner Hand!"): the whole house flashes blinding gold on each of her cries, gold rings
race out from his hand to both ends, the Curse follows in blood red the length of the roofline, and every torch
on the house recoils, ducking and scattering away from him. Hagen's violet shocks knock through the crowd.

Her fury breaks: "Betrug! Schändlichster Betrug! Verrat! Wie noch nie er gerächt!" Every hammering chord of the
orchestra is a silver strike that fills a whole run, round and round the house, with gold glints flying, until
she stands blazing silver at the corner of Right facing the man who betrayed her.

The music is Wagner's own: Act II, scene 4, the welcome (bars 728 to 741), her first sight of Siegfried (836 to
839), the Ring on his hand (856 to 865) and her fury (942 to 957), as Solti's 1958 Vienna Philharmonic recording
takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py) orchestrated by hand and register.
The stage adds a cymbal and drum to each hail, a crash and a gong as the Ring flashes on his hand, a timpani roll
under the Curse, and a cymbal on each of her cries of betrayal.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD18'
TITLE = 'The Ring on His Hand'
KIND = 'show'
DESCRIPTION = ('Gunther leads in his bride, pale and silent. Then she sees Siegfried, and the Ring on his hand: a '
               'blinding gold flash, a blood red curse to both ends, and her silver blazing up in fury.')
VOICEOVER = ('Brünnhilde is brought to the wedding as a prize. Then she sees the Ring, on Siegfried\'s hand.')

K = 3                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 728-741, 836-839, 856-865 and 942-957, Solti 1958
D = EX['seconds']
_BARS = [(m, t) for m, t in EX['bars']]


def bar(pos):
    """Seconds into the excerpt of a (fractional) bar position."""
    seg = [b for b in _BARS if abs(b[0] - pos) < 15]
    return float(np.interp(pos, [b[0] for b in seg], [b[1] for b in seg]))


T_BOAT = 0.3                                # she is led in from the river end
T_THERE = bar(736)
T_HAIL = accents(EX['notes'], 0.0, bar(742) - 1.0, vmin=90, n=3, space=2.4)      # "Willkommen! Heil!"
T_SIEG = bar(739)                           # Siegfried comes out of the doors
T_SIEG_THERE = bar(836)
T_SEES = bar(836.625)                       # she sees him: "Siegfried ... hier? Gutrune?"
T_RING = [bar(860.25), bar(862.125), bar(864.25)]   # "Ha! Der Ring ...", "an seiner Hand!", "Er ...? Siegfried ...?"
T_CURSE = bar(862.75)
T_TRITONE = [bar(865.3), bar(942.0)]        # Hagen's shocks
T_FURY = [bar(942.625), bar(944.625), bar(949.625), bar(951.625), bar(955.666)]   # "Betrug!", "Verrat!"

NIGHT = hexc('#1a2ab0')
MOON = hexc('#80a0ff')
RED_DAWN = hexc('#ff1030')
ORANGE_DAWN = hexc('#ff6a10')
WOOD = hexc('#5a2008')
HALL = hexc('#ff8a20')
SPEAR = hexc('#c8d8ff')
TORCH = hexc('#ff6a10')
FLAME = hexc('#ffd060')
HAGEN = hexc('#7a00ff')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
GOLD = hexc('#ffaa00')
BLOOD = hexc('#c00010')
WHITE = hexc('#ffffff')
BRUNN = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
SIEG = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
RING_RED = hexc('#ff1800')

START = dict(night=0.2, moon=0.0, dawn=0.7, hall=0.65, spear=0.7)       # where GD17 left the shore
END = dict(night=0.28, moon=0.0, dawn=0.55, hall=0.65, spear=0.7)       # where GD19 picks it up
HAGEN_AT, HAGEN_LVL = ('Porch Front', 0.35), 0.85
GUNTHER_AT, GUTRUNE_AT = ('Right', 0.25), ('Right', 0.4)
COUPLE_LVL = 0.85                           # Gunther and Gutrune at the start (w=22)
BRUNN_AT = ('Right', 0.12)
SIEG_AT = ('Porch Right', 0.8)
CROWD = dict(n=140, seed=1717, lvl=0.7)     # crowd(S, n, seed) at level lvl, as GD17 left it
FIGS_END = dict(hagen=(*HAGEN_AT, 0.85), gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8),
                brunnhilde=(*BRUNN_AT, 0.9), siegfried=(*SIEG_AT, 0.85), crowd=0.4)
CLEAR = 30.0                                # torches this close to a person go out early in the scene
RUNS = ['Right', 'Porch Right', 'Porch Front', 'Porch Left', 'Left', 'Side']


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The shore before the hall as profiles over the house: the porch is the hall's doors, its seams lit from
    inside, the spear upright in the middle of Porch Front; the wings and Side are the shore, the river beyond the
    free end of Right."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same shore, moonlight and torches in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    spear = at(G, 'Porch Front', 0.5)
    L = d.max()
    return dict(
        d=d, L=L, porch=porch, shore=~porch, spear=spear,
        doors=porch * (0.65 + 0.35 * smooth_noise(rng, d, 30.0)),
        seams=porch * np.clip(np.sin(2 * np.pi * (d - at(G, 'Porch Left', 0.0)) / 95) * 3 - 2.2, 0, 1),
        tip=np.exp(-((d - spear) / 7) ** 2),
        river=smoothstep(L - 600, L, d),      # the dawn comes up from the river end
        sand=~porch * (0.7 + 0.3 * smooth_noise(rng, d, 70.0)),
        flick=Flicker(rng, G.N, 3.0, 9.0),
        glow=Flicker(rng, G.N, 0.6, 2.0),
    )


def shore(S, T, lv):
    """The shore at shared time T with levels lv (night, moon, dawn, hall, spear)."""
    d = S['d']
    drift = np.sin(2 * np.pi * (d / 310 + 0.07 * T)) * np.sin(2 * np.pi * (d / 170 - 0.05 * T) + 0.6)
    fr = light(NIGHT, lv['night'] * S['sand'] * (0.85 + 0.15 * drift))
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 600 - 0.03 * T))
    fr += light(MOON, lv['moon'] * S['shore'] * (0.4 + 0.6 * u) ** 2)
    sky = RED_DAWN + (ORANGE_DAWN - RED_DAWN) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 450 + 0.05 * T)))[:, None]
    fr += light(sky, lv['dawn'] * S['shore'] * (0.75 + 0.25 * drift) * (0.7 + 0.3 * S['river']))
    fr += light(WOOD, (0.4 + 0.6 * lv['hall']) * S['doors'])
    fr += light(HALL, lv['hall'] * S['seams'] * (0.8 + 0.2 * S['glow'](T)))
    fr += light(SPEAR, lv['spear'] * S['tip'] * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the shore, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def crowd(S, n, seed=1717):
    """Where n vassals stand with their torches, spread over the shore and the porch runs (not on the spear)."""
    rng = np.random.default_rng(seed)
    p = np.sort(rng.uniform(20, S['L'] - 15, n))
    return p[np.abs(p - S['spear']) > 30]


def torches(S, T, ps, lvl, seed=7):
    """Torches at path distances ps (lvl a scalar or one per torch): orange flames with a flickering gold core."""
    d = S['d']
    lvl = np.broadcast_to(np.asarray(lvl, float), np.shape(ps))
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, len(ps))
    fq = rng.uniform(5, 11, len(ps))
    fl = 0.8 + 0.2 * np.sin(fq * T + ph)
    g = np.exp(-((d[None, :] - np.asarray(ps)[:, None]) / 7) ** 2)
    out = light(TORCH, np.clip((lvl * fl)[:, None] * g, 0, None).sum(0).clip(0, 1.2))
    return out + light(FLAME, np.clip((0.6 * lvl * fl ** 3)[:, None] * g ** 4, 0, None).sum(0).clip(0, 1))


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


def recent(ts, t, span):
    """(seconds since the latest of ts, its index), or (None, index) if it is older than span."""
    i = int(np.searchsorted(ts, t, side='right')) - 1
    return (t - ts[i], i) if i >= 0 and t - ts[i] < span else (None, i)


def brunnhilde(fr, S, p, lvl, T):
    """Brünnhilde: silver white with gold glints flickering on her armour."""
    fr = figure(fr, S, p, BRUNN, lvl)
    gl = 0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * T + np.array([0.0, 2.1]))
    for k, off in enumerate((-9, 9)):
        fr += light(GLINT, 0.6 * lvl * gl[k] * np.exp(-((S['d'] - p - off) / 4) ** 2))
    return fr


def siegfried(fr, S, p, lvl):
    """Siegfried: emerald with a white-hot head."""
    fr = figure(fr, S, p, SIEG, lvl)
    return fr + light(HEAD, 0.8 * lvl * np.exp(-((S['d'] - p) / 6) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'score'. 'boom' (each hail),
    'brunn_soft' (her first words), 'ring' and 'ringhit', 'curse', 'fury' (every hammering chord of her fury) and
    'furyhit' (each cry) mark moments for the lights and the stage; they make no sound."""
    N = [(t, d, m, v, 'score', h) for t, d, m, v, h in EX['notes']]
    for k, t0 in enumerate(T_HAIL):
        N.append((t0, 0.5, 39, 0, 'boom', k))
    for t0, t1, who, text in EX['singing']:
        if who == 'Brünnhilde' and t0 < T_RING[0]:
            N.append((t0, t1 - t0, 60, 0, 'brunn_soft', None))
    for k, t0 in enumerate(T_RING):
        N.append((t0, 0.5, 72, 0, 'ring', k))
        N.append((t0, 0.5, 36, 0, 'ringhit', k))
    N.append((T_CURSE, 1.0, 48, 0, 'curse', None))
    for j, t0 in enumerate(accents(EX['notes'], T_FURY[0] - 0.2, D - 0.5, vmin=80, n=2, space=0.33)):
        N.append((t0, 0.3, 60, 0, 'fury', min(2, j // 12)))
    for k, t0 in enumerate(T_FURY):
        N.append((t0, 0.5, 34, 0, 'furyhit', k))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=18):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    seg = G.seg_of
    homes = crowd(S, CROWD['n'], CROWD['seed'])
    p_h, p_gn, p_gt = at(G, *HAGEN_AT), at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT)
    p_b, p_s = at(G, *BRUNN_AT), at(G, *SIEG_AT)
    door = at(G, 'Porch Front', 0.75)
    hails = np.array(sorted({e[0] for e in N if e[4] == 'boom'}))
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    curse_on = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    fury = [e for e in N if e[4] == 'fury']
    fury_on = np.array(sorted({e[0] for e in fury}))
    brunn_soft = np.array(sorted({e[0] for e in N if e[4] == 'brunn_soft'}))
    rng = np.random.default_rng(seed)
    jit = rng.uniform(0, 2 * np.pi, len(homes))
    near = np.min([np.abs(homes - p) for p in (p_h, p_gn, p_gt, p_b, p_s)], axis=0) < CLEAR
    clear = lambda t: np.where(near, 1 - smoothstep(0.5, 4.0, t), 1.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_RING[0], START[k]), (T_RING[0] + 6, 0.5 * (START[k] + END[k])),
                          (D - 4, END[k])]) for k in START}
        lv['dawn'] -= 0.25 * smoothstep(T_RING[0], T_RING[0] + 1, t) * (1 - smoothstep(T_FURY[0], T_FURY[0] + 4, t))
        fr = shore(S, T, lv)

        # the crowd: steady, flickering when she sees him, recoiling from the Ring
        lvl = np.full(len(homes), CROWD['lvl']) * clear(t)
        lvl = lvl * keys(t, [(0, 1.0), (7.0, 0.55), (T_FURY[0], 0.5), (D - 4, FIGS_END['crowd'] / CROWD['lvl'])])
        pos = homes.copy()
        g = smoothstep(T_SEES, T_SEES + 0.5, t) * (1 - smoothstep(T_RING[0], T_RING[0] + 0.3, t))
        lvl = lvl * (1 - 0.35 * g * (0.5 + 0.5 * np.sin(23 * t + jit)))
        for k, t0 in enumerate(T_RING):
            a = t - t0
            if 0 <= a < 4.0:
                push = np.sign(homes - p_s) * 140 * np.exp(-np.abs(homes - p_s) / 700)
                pos = pos + push * smoothstep(0, 0.3, a) * np.exp(-max(a - 0.3, 0) / 1.4)
                lvl = lvl * (1 - 0.7 * np.exp(-a / 0.7) * np.exp(-np.abs(homes - p_s) / 900))
        fr += torches(S, T, pos, lvl, seed=7)

        # "Heil dir, Gunther!": gold waves from Gunther, silver from the bride, over the torches
        a, i = recent(hails, t, 3.0)
        if a is not None:
            src = p_gn
            r = 2400 * (1 - np.exp(-a / 0.9))
            band = smoothstep(r + 60, r - 260, np.abs(d - src)) * smoothstep(r - 700, r - 260, np.abs(d - src))
            fr = fr * (1 - 0.5 * np.exp(-a / 1.3) * band)[:, None]
            fr += light(GUNTHER if i % 2 == 0 else BRUNN, 1.0 * np.exp(-a / 1.3) * band)
            fr += light(WHITE, 0.5 * np.exp(-a / 0.1) * np.exp(-((d - src) / 40) ** 2))

        # her motif, softly: a pale silver breath out from her on each note
        a, i = recent(brunn_soft, t, 1.6)
        pb = L + 30 + (p_b - L - 30) * smoothstep(T_BOAT, T_THERE, t)
        if a is not None:
            fr += light(BRUNN, 0.45 * np.exp(-a / 0.6) * np.exp(-((d - pb) / (80 + 300 * a)) ** 2))

        # she sees him: her silver shudders, a grey tremor over the house
        if T_SEES <= t < T_RING[0]:
            a = t - T_SEES
            fr += light(BRUNN, 0.35 * np.exp(-a / 1.5) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) * S['shore'])

        # the Ring on his hand: a blinding gold flash, gold rings racing to both ends, the hand flaring
        a, i = recent(ring_on, t, 3.0)
        for k, t0 in enumerate(T_RING):
            b = t - t0
            if 0 <= b < 1.5:
                fr = fr * (1 - 0.85 * smoothstep(0, 0.05, b) * np.exp(-b / 0.5))
            if 0 <= b < 0.5:
                fr += light(GOLD + (WHITE - GOLD) * 0.3, (1.0 - 0.12 * k) * np.exp(-b / 0.14))
                fr += light(WHITE, 0.9 * np.exp(-b / 0.06) * np.exp(-((d - p_s) / 120) ** 2))
        if a is not None:
            r = 2600 * (1 - np.exp(-a / 0.5))
            fr += light(GOLD, 1.0 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_s) - r) / 140) ** 2))
            fr += light(RING_RED, 0.6 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_s) - 0.8 * r) / 50) ** 2))

        # the Curse: blood red from his hand the length of the roofline
        a, i = recent(curse_on, t, 3.0)
        if a is not None:
            front = min(1.0, (t - curse_on[0]) / 1.2) * max(p_s, L - p_s)
            slash = smoothstep(front + 60, front - 60, np.abs(d - p_s))
            fr += light(BLOOD, 0.95 * slash * np.exp(-a / 1.0))

        # "merket wohl": Hagen's tritone knocks violet shocks through the crowd
        for t0 in T_TRITONE:
            b = t - t0
            if 0 <= b < 3.0:
                r = 1800 * (1 - np.exp(-b / 0.6))
                fr = fr * (1 - 0.6 * np.exp(-b / 0.25))
                fr += light(HAGEN, 0.95 * np.exp(-b / 1.0) * smoothstep(r + 40, r - 180, np.abs(d - p_h)))

        # her fury: every note of her motif a silver strike filling a whole run, round the house
        for j, (t0, dur, m, v, part, k) in enumerate(fury):
            b = t - t0
            if 0 <= b < 0.9:
                run = seg == RUNS[j % len(RUNS)]
                fr = fr * (1 - 0.8 * np.exp(-b / 0.35) * run)[:, None]
                fr += light(BRUNN, (0.85 + 0.1 * k) * np.exp(-b / 0.35) * run)
                fr += light(GLINT, 0.5 * np.exp(-b / 0.15) * run * (rng.uniform(size=G.N) > 0.85))
        a, i = recent(fury_on, t, 2.0)
        if a is not None and t < D - 6:
            r = 2200 * (1 - np.exp(-a / 0.5))
            fr += light(BRUNN, 0.7 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p_b) - r) / 110) ** 2))

        # the people
        fr = figure(fr, S, p_h, HAGEN, HAGEN_LVL)
        fr = figure(fr, S, p_gn, GUNTHER, keys(t, [(0, COUPLE_LVL), (T_RING[0], COUPLE_LVL), (D - 4, 0.8)]), w=22.0)
        fr = figure(fr, S, p_gt, GUTRUNE, keys(t, [(0, COUPLE_LVL), (T_RING[0], COUPLE_LVL), (D - 4, 0.8)]), w=22.0)
        if t >= T_BOAT:
            bl = keys(t, [(T_BOAT, 0.0), (T_BOAT + 0.8, 0.45), (T_SEES, 0.45), (T_RING[0], 0.6), (T_FURY[0], 0.7),
                          (T_FURY[-1] + 3, 1.0), (D - 3, FIGS_END['brunnhilde'][2])])
            fr = brunnhilde(fr, S, pb, bl, T)
            if t < T_THERE:
                wake = smoothstep(pb + 220, pb, d) * (d >= pb)
                fr += light(BRUNN, 0.35 * wake * (1 - smoothstep(T_BOAT, T_THERE, t)))
        if t >= T_SIEG:
            u = smoothstep(T_SIEG, T_SIEG_THERE, t)
            ps = door + (p_s - door) * u
            sl = 0.85 * smoothstep(T_SIEG, T_SIEG + 0.6, t)
            fr = siegfried(fr, S, ps, sl)
            if t < T_SIEG + 0.8:
                fr += light(HALL, 0.8 * np.exp(-(t - T_SIEG) / 0.3) * S['porch'])
            if t >= T_RING[0]:                  # the Ring glints on his hand from now on
                fr += light(GOLD, 0.7 * np.exp(-((d - ps - 10) / 5) ** 2) * (0.75 + 0.25 * np.sin(2 * np.pi * 1.1 * T)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the stage's cymbals, drums and gong."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.6)
    # the stage is felt in the welcome and the fury; it holds back while she sees him and finds the Ring
    o.effects([(0, 0), (T_SIEG, 0), (T_SIEG + 1, -9), (T_RING[0] - 0.5, -9), (T_RING[0], -2), (D, -2)])
    o.tutti(tidy(EX['notes']), size=lambda t: 0.7 if T_SEES <= t < T_RING[0] else 1.0)
    pg, ps, pb = pan_at(at(G, *GUNTHER_AT)), pan_at(at(G, *SIEG_AT)), pan_at(at(G, *BRUNN_AT))
    for k, t0 in enumerate(T_HAIL):
        o.hit('crash', t0, 108, gain=0.45, pan=pg)
        o.hit('bass drum', t0, 116, gain=0.55, pan=pg)
    for k, t0 in enumerate(T_RING):         # the Ring flashes on his hand
        o.hit('crash', t0, 124 - 6 * k, gain=0.6, pan=ps)
        o.hit('gong', t0 + 0.02, 116 - 8 * k, gain=0.45, pan=ps)
    o.hit('timpani roll', T_CURSE, 110, pitch=-4, gain=0.55, pan=ps)
    for t0 in T_TRITONE:
        o.hit('timpani', t0, 118, pitch=-6, gain=0.7, pan=pan_at(at(G, *HAGEN_AT)))
    for k, t0 in enumerate(T_FURY):         # her cries of betrayal
        o.hit('crash', t0, 112 + 3 * k, gain=0.45, pan=pb)
        o.hit('bass drum', t0, 118, gain=0.5, pan=pb)
