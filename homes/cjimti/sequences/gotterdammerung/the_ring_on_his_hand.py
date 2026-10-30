"""The Ring on His Hand: the shore in a red morning, a sea of the vassals' torches over every run, Hagen
ultraviolet at the doors by his spear, Gunther and Gutrune on Right. A boat comes up the river: Gunther leads in
his bride. Brünnhilde comes in from the free end of Right pale and dimmed, a faint silver with her eyes down,
while the men hail them: three great chords, and each sends gold and silver waves over the torches.

Then the hall's doors open and Siegfried comes out of them, emerald, and crosses to the corner of the porch.
She sees him: her silver shudders, the torches flicker. Then she sees the Ring on his hand. The Ring (Donington 8)
cracks out in the brass and the whole house flashes blinding gold; gold rings race out from his hand to both
ends; the Curse (13) follows in blood red the length of the roofline, and every torch on the house recoils,
ducking and scattering away from him. Twice more the Ring flares on his hand, and Hagen's tritone (61a) knocks
violet shocks through the crowd: "mark well what she says."

Her fury breaks: Brünnhilde's motif (88) on the horns, fortissimo, and every note a silver strike that fills a
whole run, round and round the house, faster, with gold glints flying, until she stands blazing silver at the
corner of Right facing the man who betrayed her.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'GD18'
TITLE = 'The Ring on His Hand'
KIND = 'show'
DESCRIPTION = ('Gunther leads in his bride, pale and silent. Then she sees Siegfried, and the Ring on his hand: a '
               'blinding gold flash, a blood red curse to both ends, and her silver blazing up in fury.')
VOICEOVER = ('Brünnhilde is brought to the wedding as a prize. Then she sees the Ring, on Siegfried\'s hand.')

K = 3                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_BOAT = 2.0                                # she is led in from the river end
T_THERE = 12.0
T_HAIL = [6.0, 9.0, 12.0]                   # "Heil dir, Gunther! Heil dir und deiner Braut!"
T_BRUNN = 14.5                              # her motif, softly: she does not look up
T_SIEG = 19.0                               # Siegfried comes out of the doors
T_SIEG_THERE = 24.0
T_SEES = 25.5                               # she sees him: "Siegfried ... hier? Gutrune?"
T_RING = [31.0, 41.0, 47.0]                 # the Ring on his hand
T_CURSE = 34.0
T_TRITONE = [44.0, 50.0]                    # "merket wohl"
T_FURY = [54.0, 59.5, 64.0]                 # her fury: her motif, fortissimo
D = 80.0

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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_RING[0], 'Eb2', 62, 'pedal')
    for k, t0 in enumerate(T_HAIL):
        for m in ('Eb3', 'G3', 'Bb3', 'Eb4'):
            add(t0, 1.5, m, 104 + 4 * k, 'hail', k)
        add(t0, 0.5, 'Eb2', 112, 'boom', k)
    for t, m, v, d in play('brunnhilde', T_BRUNN, 0.55, -12, 70):
        add(t, d, m, v, 'brunn_soft')
    for t, m, v, d in play('siegfried', T_SIEG, 0.6, -12, 92):
        add(t, d, m, v, 'sieg')
    add(T_SEES, 5.0, 'D3', 84, 'trem')
    add(T_SEES, 5.0, 'Ab3', 84, 'trem')
    for k, t0 in enumerate(T_RING):
        for t, m, v, d in play('ring', t0, 0.42 if k == 0 else 0.3, 0, 120 - 4 * k):
            add(t, d, m, v, 'ring', k)
        add(t0, 0.5, 'C2', 124, 'ringhit', k)
    for t, m, v, d in play('curse', T_CURSE, 0.5, -12, 116):
        add(t, d, m, v, 'curse')
    for k, t0 in enumerate(T_TRITONE):
        for t, m, v, d in play('hagen', t0, 0.8, -12, 112):
            add(t, d, m, v, 'tritone', k)
    for k, t0 in enumerate(T_FURY):
        for t, m, v, d in play('brunnhilde', t0, 0.48 - 0.06 * k, -12, 112 + 4 * k):
            add(t, d, m, v, 'fury', k)
        add(t0, 0.5, 'Bb1', 118, 'furyhit', k)
    for m in ('Bb2', 'D3', 'F3', 'Bb3'):
        add(T_FURY[-1] + 6.0, D - T_FURY[-1] - 6.0, m, 72, 'blaze')
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
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.31, 0.25), ('brass', 0.31, 0.3), ('perc', 0.29, 0.25), ('winds', 0.28, 0.35),
                            ('strings', 0.28, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    ph = pan_at(at(G, *HAGEN_AT))
    pg = pan_at(at(G, *GUNTHER_AT))
    pb = pan_at(at(G, *BRUNN_AT))
    ps = pan_at(at(G, *SIEG_AT))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v + 8, 0.0, rise=2.0, fall=1.0, gain=0.55)
        elif part == 'hail':
            hold('brass', horn, m, t, t + d, v, pg * 0.5, rise=0.08, fall=0.8, gain=0.6)
            hold('brass', tbn, m - 12, t, t + d, v - 6, pg * 0.5, rise=0.08, fall=0.8, gain=0.55)
        elif part == 'boom':
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, pg)
            M.add('perc', crash.play(100), t, 0.5, pg)
        elif part == 'brunn_soft':
            M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, pb)
        elif part == 'sieg':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, ps)
        elif part == 'trem':
            hold('strings', vtrem, m + 12, t, t + d, v, pb, rise=0.3, fall=0.6, gain=0.6)
        elif part == 'ring':
            if d > 0.9:
                hold('brass', tpt, m, t, t + d, v, ps, rise=0.05, fall=0.8, gain=0.75)
            else:
                M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.25), t, 0.85, ps)
            M.add('brass', tbn.play(m - 12, v - 10, dur=d * 1.05, release=0.25), t, 0.7, ps)
            M.add('winds', clar.play(m + 12, v - 20, dur=d * 1.05, release=0.25), t, 0.5, ps)
        elif part == 'ringhit':
            M.add('perc', crash.play(v), t, 0.9, ps)
            M.add('perc', timp.play(v, pitch=-3), t, 0.9, ps)
        elif part == 'curse':
            if d > 1.2:
                hold('brass', tbn, m + 12, t, t + d, v, ps, rise=0.1, fall=1.0, gain=0.9)
            else:
                M.add('brass', tbn.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.9, ps)
            if t == T_CURSE:
                M.add('perc', gong.play(110), t, 0.7, ps)
        elif part == 'tritone':
            hold('low', tuba, m, t, t + d, v, ph, rise=0.08, fall=1.0, gain=0.9)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, ph)
        elif part == 'fury':
            if d > 0.8:
                hold('brass', horn, m + 12, t, t + d, v, pb, rise=0.05, fall=0.6, gain=0.8)
            else:
                M.add('brass', horn.play(m + 12, v, dur=d * 1.05, release=0.25), t, 0.9, pb)
            M.add('strings', vln.play(m + 12, v - 10, dur=d * 1.05, release=0.25), t, 0.6, pb)
        elif part == 'furyhit':
            M.add('perc', timp.play(v, pitch=-2), t, 0.9, pb)
            M.add('perc', crash.play(v - 10), t, 0.6, pb)
        elif part == 'blaze':
            hold('strings', vtrem, m + 12, t, t + d, v, pb * 0.5, rise=1.0, fall=1.5, gain=0.5)
