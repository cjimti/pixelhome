"""The Oath on the Spear: the shore as the last scene left it, the torches low, Brünnhilde blazing silver at the
corner of Right, Siegfried emerald at the corner of the porch with the Ring glinting on his hand. The crowd
mutters: torches flicker. Hagen raises his spear in the middle of Porch Front and its point flares white; a steel
line runs the length of the porch.

Siegfried strides to it and swears he is innocent, his hand on the point ("Helle Wehr, heilige Waffe! Hilf meinem
ewigen Eide!"): every hammering chord an emerald strike that shoots up the porch to the spear point and bursts over
a whole run, round the house. Then Brünnhilde storms across, a silver streak from the corner of Right, tears his
hand away and swears on the same point that he lies: silver strikes bigger than his, one run after another, and
on "Spitze! Achte des Spruchs!" every run at once, gold glints flying. The men roar for Donner's help ("Hilf,
Donner! Tose dein Wetter!"), every torch flaring, the stomp thumping orange round the house.

Siegfried laughs it off ("Folgt mir zum Mahl! Froh zur Hochzeit helfet, ihr Frauen!"), emerald sparkling, takes
Gutrune by the hand and leads her into the hall: the two of them cross to the doors and vanish in an amber flare.
The torches sink; Brünnhilde stands by the spear, Gunther shamed on Right, Hagen watching.

The music is Wagner's own: Act II, scene 4, Hagen's spear (bars 1127 to 1130), Siegfried's oath (1142 to 1150),
Brünnhilde's (1179 to 1195), the men's cry to Donner (1213 to 1221) and Siegfried's "Froh zur Hochzeit" (1264
to 1269), as Solti's 1958 Vienna Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py) orchestrated by hand and register. The stage adds the ring of steel as the spear is raised and
as each of them lays a hand on its point, a blow as she seizes it, thunder answering the men's cry to Donner, and
their stamping; it stays back under both oaths.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD19'
TITLE = 'The Oath on the Spear'
KIND = 'show'
DESCRIPTION = ("Siegfried swears on Hagen's spear that he is innocent, emerald strikes flying up it. Brünnhilde "
               'seizes the same spear and swears he lies, in bigger silver strikes over every run, and the men roar.')
VOICEOVER = ("Two oaths on one spear. He swears he is innocent. She swears he is lying. Only one of them can be "
             'telling the truth.')

K = 4                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1127-1130, 1142-1150, 1179-1195, 1213-1221, 1264-1269
D = EX['seconds']
_SEG = [(g['start'], g['start'] + g['seconds']) for g in EX['segments']]
def _sung(who, text):
    """When the first sung line by who (or a group starting so) beginning with text starts."""
    return next(t0 for t0, t1, w, x in EX['singing'] if w.startswith(who) and x.startswith(text))



T_MUTTER = (0.0, 2.0)                       # the crowd mutters
T_SPEAR = accents(EX['notes'], 0.0, _SEG[0][1], vmin=90, n=3, space=1.0)[0]     # Hagen raises the spear
T_WALK = (_SEG[0][1] - 3.5, _SEG[0][1])     # Siegfried strides to it
T_HIS = [_sung('Siegfried', 'Helle Wehr, '), _sung('Siegfried', 'Hilf meinem ')]   # his oath
T_STORM = (_SEG[2][0], _sung('Brünnhilde', 'Helle Wehr! '))                       # she storms across
T_HERS = [_sung('Brünnhilde', 'Helle Wehr! '), _sung('Brünnhilde', 'Hilf meinem '),
          _sung('Brünnhilde', 'Spitze! Acht')]                                    # her oath; "Spitze!": all at once
T_ROAR = [_sung('Mannen (B2)', 'Hilf, Donner'), _sung('Mannen (T1, T2', 'Hilf, Donner')]   # "Hilf, Donner!"
T_STOMP = (T_ROAR[0], _SEG[3][1] - 0.4)
BEAT = 0.5
T_LAUGH = _SEG[4][0] + 0.2                  # he laughs it off
T_LEAD = (_sung('Siegfried', 'Froh zur Hoch') + 1.0, D - 2.5)   # he leads Gutrune into the hall

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
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'score'. The orchestra's
    hammering chords under his oath are 'his' (k 0, 1), under hers 'hers' (k 2 from "Spitze!"), under the men's cry
    'roar'; 'stomp', 'spearhit' and 'laugh' (each phrase of his) mark moments too. Only 'score' sounds."""
    N = [(t, d, m, v, 'score', h) for t, d, m, v, h in EX['notes']]
    N.append((T_SPEAR, 1.0, 36, 0, 'spearhit', None))
    for t0 in accents(EX['notes'], _SEG[1][0], _SEG[1][1], vmin=55, n=2, space=0.5):
        N.append((t0, 0.3, 60, 0, 'his', int(t0 >= T_HIS[1])))
    for t0 in accents(EX['notes'], _SEG[2][0], _SEG[2][1], vmin=75, n=2, space=0.4):
        N.append((t0, 0.3, 60, 0, 'hers', 2 if t0 >= T_HERS[2] else int(t0 >= T_HERS[1])))
    for t0 in accents(EX['notes'], _SEG[3][0], _SEG[3][1], vmin=80, n=2, space=0.35):
        N.append((t0, 0.3, 60, 0, 'roar', int(t0 >= T_ROAR[1])))
    lh = [n for n in EX['notes'] if n[4] == 1]
    for j, t0 in enumerate(accents(lh, T_STOMP[0], T_STOMP[1], vmin=70, n=1, space=0.45)):
        N.append((t0, 0.2, 36, 0, 'stomp', j))
    for k, (t0, t1, who, text) in enumerate(x for x in EX['singing'] if x[2] == 'Siegfried' and x[0] >= _SEG[4][0]):
        N.append((t0, 1.0, 60, 0, 'laugh', k))
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
    """Wagner's notes, orchestrated from the piano reduction, and the stage: steel on the spear, thunder for Donner."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.75)
    # the stage backs off under both oaths, leads when the men call for the thunder, then steps back again
    o.effects([(0, -2), (T_HIS[0] - 0.5, -2), (T_HIS[0], -10), (T_ROAR[0] - 0.3, -10), (T_ROAR[0], 0),
               (T_STOMP[1], 0), (T_STOMP[1] + 1, -6), (D, -6)])
    o.tutti(tidy(EX['notes']), size=lambda t: 1.0)
    psp = pan_at(at(G, 'Porch Front', 0.5))
    o.clash(T_SPEAR, psp, 120, 0.8)
    o.boom(T_SPEAR + 0.02, psp, 0.6)
    o.hit('metal', T_HIS[0], 100, gain=0.45, pan=psp)       # his hand on the point
    o.hit('scrape', T_STORM[0] + 0.3, 110, gain=0.4, pan=pan_at(at(G, *BRUNN_AT)))
    o.clash(T_HERS[0] - 0.1, psp, 124, 0.9)                 # she tears his hand away and seizes it
    o.boom(T_HERS[2], psp, 0.8)                             # "Spitze! Achte des Spruchs!"
    o.hit('crash', T_HERS[2], 120, gain=0.5, pan=psp)
    for k, t0 in enumerate(T_ROAR):                         # Donner answers the men
        o.thunder(t0 + 0.6, near=0.6 + 0.4 * k, pan=(-0.5, 0.5)[k], gain=1.0)
    pans = [pan_at(at(G, r, 0.5)) for r in RUNS]
    for t, d, m, v, part, k in compose():
        if part == 'stomp':
            o.M.add('fx', o.hits['bass drum'].play(104), t, 0.3, pans[k % len(pans)])
            o.M.add('fx', o.hits['hoof soft'].play(92), t + 0.01, 0.35, -pans[k % len(pans)])
    o.hit('scrape', T_LEAD[1] - 0.4, 96, gain=0.3, pan=pan_at(at(G, *DOOR)))     # the doors close behind them
