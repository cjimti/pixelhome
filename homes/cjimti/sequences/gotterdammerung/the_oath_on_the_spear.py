"""The Oath on the Spear: the shore as the last scene left it, the torches low, Brünnhilde blazing silver at the
corner of Right, Siegfried emerald at the corner of the porch with the Ring glinting on his hand. The crowd
mutters: torches flicker, the low strings churn. Hagen raises his spear in the middle of Porch Front and its point
flares white; a steel line runs the length of the porch.

Siegfried strides to it and swears he is innocent, his hand on the point ("Helle Wehr! Heilige Waffe!"): the oath
(Donington 42) and the spear (73) in the brass, and every note an emerald strike that shoots up the porch to the
spear point and bursts over a whole run, round the house. Then Brünnhilde storms across, a silver streak from the
corner of Right, tears his hand away and swears on the same point that he lies: the oath's second form (42a) and
her own motif (88) fortissimo, silver strikes bigger than his, one run after another and then every run at once,
gold glints flying. The men roar for Donner's help: their call (54) in the trombones, every torch flaring, the
stomp thumping orange round the house.

Siegfried laughs it off (his motif, 53, light and staccato, emerald sparkling), takes Gutrune by the hand and leads
her into the hall: the two of them cross to the doors and vanish in an amber flare. The torches sink; Brünnhilde
stands by the spear, Gunther shamed on Right, Hagen watching.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'GD19'
TITLE = 'The Oath on the Spear'
KIND = 'show'
DESCRIPTION = ("Siegfried swears on Hagen's spear that he is innocent, emerald strikes flying up it. Brünnhilde "
               'seizes the same spear and swears he lies, in bigger silver strikes over every run, and the men roar.')
VOICEOVER = ("Two oaths on one spear. He swears he is innocent. She swears he is lying. Only one of them can be "
             'telling the truth.')

K = 4                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_MUTTER = (0.0, 8.0)                       # the crowd mutters
T_SPEAR = 7.0                               # Hagen raises the spear
T_WALK = (9.0, 12.5)                        # Siegfried strides to it
T_HIS = [13.5, 19.5]                        # his oath: the oath motif, then the spear
T_STORM = (25.5, 28.5)                      # Brünnhilde storms across
T_HERS = [29.5, 35.5, 40.5]                 # her oath: the second form, her motif, the spear
T_ROAR = [45.5, 48.5]                       # "Hilf, Donner!"
T_STOMP = (45.0, 54.0)
T_LAUGH = 55.0                              # he laughs it off
T_LEAD = (61.0, 67.0)                       # he leads Gutrune into the hall
BEAT = 0.5
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

START = dict(night=0.28, moon=0.0, dawn=0.55, hall=0.65, spear=0.7)     # where GD18 left the shore
END = dict(night=0.3, moon=0.0, dawn=0.5, hall=0.6, spear=0.8)          # where GD20 picks it up
HAGEN_AT = ('Porch Front', 0.35)
GUNTHER_AT, GUTRUNE_AT = ('Right', 0.25), ('Right', 0.4)
BRUNN_FROM, BRUNN_AT = ('Right', 0.12), ('Porch Front', 0.44)
SIEG_FROM, SIEG_AT = ('Porch Right', 0.8), ('Porch Front', 0.62)
DOOR = ('Porch Front', 0.75)
CROWD = dict(n=140, seed=1717, lvl=0.4)     # as GD18 left it
CLEAR_AT = [('Porch Front', 0.35), ('Right', 0.25), ('Right', 0.4), ('Right', 0.12), ('Porch Right', 0.8)]
CLEAR = 30.0                                # torches this close to where GD18 left the people stay out
FIGS_END = dict(hagen=(*HAGEN_AT, 0.85), gunther=(*GUNTHER_AT, 0.6), brunnhilde=(*BRUNN_AT, 0.85), crowd=0.32)
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

    for j in range(16):                     # the crowd mutters: a churning figure in the low strings
        add(T_MUTTER[0] + j * 0.5, 0.45, ('C2', 'Db2', 'C2', 'B1')[j % 4], 78 + j, 'mutter')
    add(T_SPEAR, 1.0, 'C2', 120, 'spearhit')
    for t, m, v, d in play('oath', T_HIS[0], 0.55, -12, 108):
        add(t, d, m, v, 'his', 0)
    for t, m, v, d in play('spear', T_HIS[1], 0.38, 0, 110):
        add(t, d, m, v, 'his', 1)
    for t, m, v, d in play('oath_b', T_HERS[0], 0.42, -12, 112):
        add(t, d, m, v, 'hers', 0)
    for t, m, v, d in play('brunnhilde', T_HERS[1], 0.42, -12, 118):
        add(t, d, m, v, 'hers', 1)
    for t, m, v, d in play('spear', T_HERS[2], 0.34, 0, 122):
        add(t, d, m, v, 'hers', 2)
    for k, t0 in enumerate(T_ROAR):
        for t, m, v, d in play('vassals', t0, 0.36, 0, 110 + 4 * k):
            add(t, d, m, v, 'roar', k)
    t, j = T_STOMP[0], 0
    while t < T_STOMP[1] - 1e-6:
        add(t, 0.2, 'C2', 100 + 16 * (j % 4 == 0), 'stomp', j)
        t += BEAT
        j += 1
    for t, m, v, d in play('siegfried', T_LAUGH, 0.42, -12, 96):
        add(t, d, m, v, 'laugh', 0)
    for t, m, v, d in play('siegfried', T_LAUGH + 2.6, 0.36, -7, 92):
        add(t, d, m, v, 'laugh', 1)
    for t, m, v, d in play('gutrune', T_LEAD[0], 0.5, -5, 90):
        add(t, d, m, v, 'gutrune')
    for m in ('C3', 'Eb3', 'G3'):
        add(T_LEAD[1] + 1, D - T_LEAD[1] - 1, m, 64, 'after')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=19):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    seg = G.seg_of
    homes = crowd(S, CROWD['n'], CROWD['seed'])
    keep = np.min([np.abs(homes - at(G, *c)) for c in CLEAR_AT], axis=0) >= CLEAR   # out since GD18
    p_h, p_gn, p_gt = at(G, *HAGEN_AT), at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT)
    b0, b1 = at(G, *BRUNN_FROM), at(G, *BRUNN_AT)
    s0, s1 = at(G, *SIEG_FROM), at(G, *SIEG_AT)
    door, spear = at(G, *DOOR), S['spear']
    his = [e for e in N if e[4] == 'his']
    hers = [e for e in N if e[4] == 'hers']
    hers_first = min(e[0] for e in hers if e[5] == 2)
    roar = [e for e in N if e[4] == 'roar']
    laugh = np.array(sorted({e[0] for e in N if e[4] == 'laugh'}))
    stomps = [(e[0], e[5]) for e in N if e[4] == 'stomp']
    st_t = np.array([x[0] for x in stomps])
    rng = np.random.default_rng(seed)
    jit = rng.uniform(0, 2 * np.pi, len(homes))
    sp_pos = rng.uniform(at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0), 200)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_LEAD[0], START[k]), (D - 4, END[k])]) for k in START}
        lv['spear'] += 0.3 * smoothstep(T_SPEAR, T_SPEAR + 0.4, t) * (1 - smoothstep(T_HERS[2] + 4, T_LAUGH, t))
        fr = shore(S, T, lv)

        # Hagen raises the spear: its point flares white, a steel line runs the length of the porch
        if T_SPEAR <= t < T_SPEAR + 3:
            a = t - T_SPEAR
            fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S['tip'] ** 0.3)
            reach = 500 * (1 - np.exp(-a / 0.3))
            fr += light(SPEAR, 0.8 * np.exp(-a / 1.2) * S['porch'] * smoothstep(reach + 30, reach - 30, np.abs(d - spear)))

        # the crowd: muttering at first, roaring and stomping later, sinking at the end
        lvl = np.full(len(homes), CROWD['lvl']) * keep
        mut = smoothstep(0, 2.0, t) * (1 - smoothstep(T_MUTTER[1] - 1, T_MUTTER[1] + 1, t))
        lvl = lvl * (1 + 0.5 * mut * np.sin(9 * t + jit))
        i = int(np.searchsorted(st_t, t, side='right')) - 1
        if i >= 0 and t - st_t[i] < BEAT and T_STOMP[0] <= t < T_STOMP[1]:
            a, j = t - st_t[i], stomps[i][1]
            acc = 1.0 + 0.6 * (j % 4 == 0)
            lvl = lvl * (1 + 1.2 * acc * np.exp(-a / 0.12))
            fr += light(TORCH, 0.9 * acc * np.exp(-a / 0.16) * (seg == RUNS[j % len(RUNS)]))
        roaring = smoothstep(T_ROAR[0] - 0.5, T_ROAR[0], t) * (1 - smoothstep(T_STOMP[1], T_STOMP[1] + 1, t))
        lvl = lvl * (1 + 0.9 * roaring) * keys(t, [(0, 1.0), (T_LEAD[0], 1.0), (D - 4, FIGS_END['crowd'] / CROWD['lvl'])])
        fr += torches(S, T, homes, lvl, seed=7)

        # his oath: each note an emerald strike shooting up the porch to the point, bursting over a whole run
        ps = s0 + (s1 - s0) * smoothstep(*T_WALK, t)
        for j, (t0, dur, m, v, part, k) in enumerate(his):
            a = t - t0
            if 0 <= a < 1.0:
                head = ps + (spear - ps) * min(1.0, a / 0.12)
                fr += light(SIEG, np.exp(-a / 0.2) * np.exp(-((d - head) / 25) ** 2))
                run = seg == RUNS[(2 * j + k) % len(RUNS)]
                b = max(a - 0.12, 0.0)
                fr = fr * (1 - 0.7 * smoothstep(0.1, 0.14, a) * np.exp(-b / 0.3) * run)[:, None]
                fr += light(SIEG, 0.9 * smoothstep(0.1, 0.14, a) * np.exp(-b / 0.3) * run)
                fr += light(WHITE, 0.7 * np.exp(-b / 0.08) * S['tip'] ** 0.4 * (a > 0.1))

        # her oath: bigger silver strikes, one run after another, then every run at once on the spear
        pb = b0 + (b1 - b0) * smoothstep(*T_STORM, t)
        if T_STORM[0] <= t < T_STORM[1] + 0.5:
            u = smoothstep(*T_STORM, t)
            trail = (d - pb) * np.sign(b0 - b1)
            fr += light(BRUNN, 0.8 * (1 - u) * (trail >= 0) * np.exp(-np.clip(trail, 0, None) / 120))
        for j, (t0, dur, m, v, part, k) in enumerate(hers):
            a = t - t0
            if 0 <= a < 1.0:
                if k < 2:
                    run = seg == RUNS[(j + 3) % len(RUNS)]
                elif t0 == hers_first:
                    run = np.ones(G.N)
                else:
                    run = S['porch'] if j % 2 else S['shore']
                tau = 0.25 if k < 2 else 0.2
                fr = fr * (1 - 0.8 * np.exp(-a / tau) * run)[:, None]
                fr += light(BRUNN, 0.9 * np.exp(-a / tau) * run)
                fr += light(GLINT, 0.8 * np.exp(-a / 0.2) * run * (np.abs(np.sin(d * 0.37 + 11 * j)) > 0.93))
                if k < 2:
                    fr += light(BRUNN, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - pb) - 2400 * a) / 70) ** 2))

        # "Hilf, Donner!": every note of their call flares a run of the crowd gold
        for j, (t0, dur, m, v, part, k) in enumerate(roar):
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(FLAME, 0.7 * np.exp(-a / 0.15) * (seg == RUNS[(j + 2 * k) % len(RUNS)]))

        # he laughs it off: emerald sparkles thrown up from him on each phrase
        a, i = recent(laugh, t, 1.0)
        if a is not None:
            hits = [(laugh[i], 0.8, ps)]
            fr += light(SIEG, np.clip(sparks(S, hits, t, 19 + i, n=18, reach=0.6), 0, 1))
            fr += light(HEAD, 0.4 * np.exp(-a / 0.2) * np.exp(-((d - ps) / 40) ** 2))

        # he leads Gutrune into the hall; they vanish into the doors in an amber flare
        pg = p_gt
        if t >= T_LEAD[0]:
            u = smoothstep(*T_LEAD, t)
            ps = s1 + (door - s1) * u
            pg = p_gt + (door + 8 - p_gt) * smoothstep(T_LEAD[0] - 1.5, T_LEAD[1], t)
        elif t >= T_LEAD[0] - 1.5:
            pg = p_gt + (door + 8 - p_gt) * smoothstep(T_LEAD[0] - 1.5, T_LEAD[1], t)
        gone = smoothstep(T_LEAD[1] - 0.4, T_LEAD[1] + 0.4, t)
        if T_LEAD[1] - 0.4 <= t < T_LEAD[1] + 2.0:
            a = t - T_LEAD[1] + 0.4
            fr += light(HALL, 0.9 * np.exp(-a / 0.5) * S['porch'])
            fr += light(WHITE, 0.5 * np.exp(-a / 0.15) * np.exp(-((d - door) / 60) ** 2))

        # the people
        fr = figure(fr, S, p_h, HAGEN, 0.85)
        fr = figure(fr, S, p_gn, GUNTHER, keys(t, [(0, 0.8), (T_HERS[0], 0.8), (T_LEAD[1], 0.6)]), w=22.0)
        if gone < 1:
            fr = figure(fr, S, pg, GUTRUNE, 0.8 * (1 - gone), w=22.0)
            sl = 0.85 * (1 - gone)
            fr = siegfried(fr, S, ps, sl)
            fr += light(GOLD, 0.7 * (1 - gone) * np.exp(-((d - ps - 10) / 5) ** 2) * (0.75 + 0.25 * np.sin(2 * np.pi * 1.1 * T)))
        bl = keys(t, [(0, 0.9), (T_STORM[0], 0.9), (T_STORM[1], 1.0), (T_HERS[2] + 3, 1.0), (D - 4, FIGS_END['brunnhilde'][2])])
        fr = brunnhilde(fr, S, pb, bl, T)
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

    for name, gain, rev in (('low', 0.37, 0.25), ('brass', 0.37, 0.3), ('perc', 0.34, 0.25), ('winds', 0.33, 0.35),
                            ('strings', 0.33, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbn_st = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vlns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v6*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')

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

    pspear = pan_at(at(G, 'Porch Front', 0.5))
    pb = pan_at(at(G, *BRUNN_AT))
    psg = pan_at(at(G, *SIEG_AT))
    pgt = pan_at(at(G, *GUTRUNE_AT))
    pans = [pan_at(at(G, r, 0.5)) for r in RUNS]
    for t, d, m, v, part, k in compose():
        if part == 'mutter':
            M.add('low', cbs.play(m, v), t, 0.8, 0.0)
            M.add('strings', vcs.play(m + 12, v - 10), t, 0.5, 0.0)
        elif part == 'spearhit':
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, pspear)
            M.add('perc', crash.play(100), t, 0.6, pspear)
            hold('brass', tbn, m + 12, t, t + d, v - 10, pspear, rise=0.05, fall=1.0, gain=0.7)
        elif part == 'his':
            if d > 0.8:
                hold('brass', horn, m + (12 if k == 0 else 0), t, t + d, v, psg, rise=0.05, fall=0.7, gain=0.8)
            else:
                M.add('brass', horn.play(m + (12 if k == 0 else 0), v, dur=d * 1.05, release=0.25), t, 0.9, psg)
            M.add('brass', tbn.play(m - (0 if k == 0 else 12), v - 12, dur=d * 1.05, release=0.25), t, 0.6, psg)
            M.add('perc', timp.play(v - 20, pitch=-3), t, 0.4, psg)
        elif part == 'hers':
            if d > 0.8:
                hold('brass', tpt, m + (12 if k < 2 else 0), t, t + d, v, pb, rise=0.05, fall=0.7, gain=0.75)
            else:
                M.add('brass', tpt.play(m + (12 if k < 2 else 0), v, dur=d * 1.05, release=0.25), t, 0.85, pb)
            M.add('strings', vln.play(m + (12 if k < 2 else 0), v - 10, dur=d * 1.05, release=0.25), t, 0.6, pb)
            M.add('perc', timp.play(v - 10, pitch=-2), t, 0.5, pb)
            if k == 2 and t == min(e[0] for e in compose() if e[4] == 'hers' and e[5] == 2):
                M.add('perc', crash.play(118), t, 0.8, 0.0)
        elif part == 'roar':
            M.add('brass', tbn_st.play(m, v), t, 0.9, 0.0)
            M.add('brass', tbn_st.play(m - 12, v - 6), t, 0.7, 0.0)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.1, release=0.15), t, 0.6, 0.0)
        elif part == 'stomp':
            p = pans[k % len(pans)]
            M.add('perc', bd.play(v), t, 0.8, p)
            if k % 4 == 0:
                M.add('perc', timp.play(v, pitch=-4), t, 0.7, p)
            else:
                M.add('perc', snare.play(v - 30), t + 0.25, 0.3, p)
        elif part == 'laugh':
            M.add('brass', horn_st.play(m + 12, v), t, 0.8, psg)
            M.add('strings', vlns.play(m + 24, v - 20), t, 0.4, psg)
        elif part == 'gutrune':
            if m >= note('C5'):
                M.add('strings', vln.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.6, pgt)
            else:
                M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, pgt)
        elif part == 'after':
            hold('strings', vln, m + 12, t, t + d, v, pb * 0.5, rise=3.0, fall=1.5, gain=0.4)
            hold('low', tbn, m - 12, t, t + d, v - 10, pspear, rise=3.0, fall=1.5, gain=0.4)
