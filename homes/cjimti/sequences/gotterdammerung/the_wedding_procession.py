"""The Wedding Procession: the shore still red from the oath, the torches low and bloody, Hagen, Gunther and
Brünnhilde where they swore. Then the hall bursts into Siegfried's wedding music, the doors swing open in a flood
of amber, the red drains out of the torches and they blaze up orange again, and the double wedding sweeps out.

Siegfried, emerald, and Gutrune, rose, come out of the doors and process along Right to the river and back;
Gunther, gold, leads Brünnhilde, silver, the other way along Porch Left and Left toward the Side and back. On every
beat of the procession banners of their colours fly out ahead of them along the roofline, every bar a whole run
flashes rose or gold, and the vassals' torches sway in step and flare on the beat over the whole house. Gutrune's
rose sings out over it, and the cowhorns call from the hall. But when the music darkens, slow pulses of Hagen's
violet-black roll out from the doors.

The couples go into the hall in a last amber flare. Then the plot breaks through the last bars: a violet-black
slam that knocks the whole house dark, blood seeping out from Hagen, the torches cowering, and two more shocks as
the act ends on a low, dark chord. He is left alone at the doors in the settling dark.

The music is Wagner's own: the end of Act II, scene 4 (bars 1282 to 1295), as Siegfried leads the wedding party
into the hall, and the wedding procession that ends the act (1672 to its last bar), as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py)
orchestrated by hand and register. The stage adds the doors flung open, the crowd's feet in step with the
procession, a cymbal on each banner bar, and a gong and drums on the final slam.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD21'
TITLE = 'The Wedding Procession'
KIND = 'show'
DESCRIPTION = ('The cowhorns blast, the hall doors open, and the double wedding sweeps out round the whole house in '
               'rose, gold, emerald and silver over a sea of swaying torches. Then the murder plot breaks through.')
VOICEOVER = ('A double wedding, with horns and torches. But under the music, the plot is already moving.')

K = 6                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1282-1295 and 1672-1704, Solti 1958
D = EX['seconds']
_BARS = [(m, t) for m, t in EX['bars']]


def bar(pos):
    """Seconds into the excerpt of a (fractional) bar position."""
    seg = [b for b in _BARS if abs(b[0] - pos) < 40]
    return float(np.interp(pos, [b[0] for b in seg], [b[1] for b in seg]))


T_HORNS = [0.3, bar(1283)]                  # the wedding music bursts from the hall
T_OPEN = bar(1283)                          # the doors swing open
BEAT = 0.5
T_MARCH = (T_OPEN + 1.0, bar(1700))         # the procession
T_OUT = (bar(1284), bar(1294))              # the couples process out
T_BACK = (bar(1674), bar(1690))             # and back
T_IN = (bar(1690), bar(1693))               # into the hall
T_GUT = [bar(1676), bar(1680), bar(1684), bar(1694)]   # Gutrune's rose over the procession
T_CALL = [bar(1672), bar(1678), bar(1696)]  # the cowhorns again
T_PULSE = [bar(1687), bar(1689), bar(1691)]  # Hagen beneath, as the music darkens
T_PLOT = bar(1701)                          # the plot breaks through
T_TRITONE = [bar(1702), bar(1703)]

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

START = dict(night=0.4, moon=0.0, dawn=0.35, hall=0.4, spear=0.75)      # where GD20 left the shore
END = dict(night=0.5, moon=0.25, dawn=0.15, hall=0.55, spear=0.7)       # the shore at the end of Act II
HAGEN_AT = ('Porch Front', 0.35)
GUNTHER_AT = ('Porch Right', 0.55)
BRUNN_AT = ('Porch Front', 0.44)
DOOR = ('Porch Front', 0.75)
A_TO = ('Right', 0.75)                      # Siegfried and Gutrune go out along Right
B_TO = ('Left', 0.3)                        # Gunther and Brünnhilde along Left
CROWD = dict(n=140, seed=1717, lvl=0.28)    # as GD20 left it
CLEAR_AT = [('Porch Front', 0.35), ('Right', 0.25), ('Right', 0.4), ('Right', 0.12), ('Porch Right', 0.8)]
CLEAR = 30.0
RED = 0.75                                  # the torches' blood red, as GD20 left them
SLAM = 61.3                                 # GD20's oath, on its own clock: its red breath carries on for a moment
FIGS_END = dict(hagen=(*HAGEN_AT, 0.85), crowd=0.35)
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


def red_torches(S, T, ps, lvl, red):
    """The torches, turned towards blood red by `red` (0..1)."""
    tf = torches(S, T, ps, lvl, seed=7)
    v = tf.max(1)
    return tf * (1 - red) + BLOOD[None, :] * (v * red * 1.6)[:, None]


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'score'. 'horns', 'open',
    'bass' (each beat of the procession, from the bass), 'gutrune' (the right hand where her rose sings), 'pulse',
    'plot' (the bass after the slam), 'slam' and 'tritone' mark moments for the lights. Only 'score' sounds."""
    N = [(t, d, m, v, 'score', h) for t, d, m, v, h in EX['notes']]
    for k, t0 in enumerate(T_HORNS + T_CALL):
        N.append((t0, 1.0, 60, 0, 'horns', k))
    N.append((T_OPEN, 1.0, 36, 0, 'open', None))
    lh = [n for n in EX['notes'] if n[4] == 1]
    for j, t0 in enumerate(accents(lh, T_MARCH[0], T_MARCH[1], vmin=1, n=1, space=0.42)):
        N.append((t0, 0.25, 36, 0, 'bass', j))
    for k, t0 in enumerate(T_GUT):
        for t, d, m, v, h in EX['notes']:
            if h == 0 and t0 <= t < t0 + 2.4:
                N.append((t, d, m, v, 'gutrune', k))
    for k, t0 in enumerate(T_PULSE):
        N.append((t0, 1.5, 36, 0, 'pulse', k))
    for t, d, m, v, h in lh:
        if t >= T_PLOT:
            N.append((t, d, m, v, 'plot', None))
    N.append((T_PLOT, 0.5, 24, 0, 'slam', None))
    for k, t0 in enumerate(T_TRITONE):
        N.append((t0, 1.0, 36, 0, 'tritone', k))
    return sorted(N, key=lambda e: e[0])


def procession(p0, p1, t):
    """Where a couple is: out from p0 to p1, back, and still from then on."""
    if t < T_BACK[0]:
        return p0 + (p1 - p0) * smoothstep(*T_OUT, t)
    return p1 + (p0 - p1) * smoothstep(*T_BACK, t)


def render(G, seed=21):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    seg = G.seg_of
    homes = crowd(S, CROWD['n'], CROWD['seed'])
    keep = np.min([np.abs(homes - at(G, *c)) for c in CLEAR_AT], axis=0) >= CLEAR   # out since GD18
    p_h, p_b, g0 = at(G, *HAGEN_AT), at(G, *BRUNN_AT), at(G, *GUNTHER_AT)
    door, a1, b1 = at(G, *DOOR), at(G, *A_TO), at(G, *B_TO)
    horns = np.array(sorted({e[0] for e in N if e[4] == 'horns' and e[5] < 2}))
    beats = [(e[0], e[5]) for e in N if e[4] == 'bass']
    bt = np.array([b[0] for b in beats])
    gut = [e for e in N if e[4] == 'gutrune']
    pulses = sorted({e[0] for e in N if e[4] == 'pulse'})
    tri = sorted({e[0] for e in N if e[4] == 'tritone'})
    plot = [e for e in N if e[4] == 'plot']
    sway = np.where(np.arange(len(homes)) % 2 == 0, 1.0, -1.0)
    bands = (GUTRUNE, SIEG, GUNTHER, BRUNN)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_OPEN, START[k]), (T_OPEN + 3, 0.5 * (START[k] + END[k]))]) for k in START}
        lv['hall'] = keys(t, [(0, START['hall']), (T_OPEN, START['hall']), (T_OPEN + 1.0, 0.95), (T_IN[1] + 1, 0.95),
                              (T_PLOT, 0.5), (D - 4, END['hall'])])
        lv['dawn'] = keys(t, [(0, START['dawn']), (T_OPEN + 3, 0.45), (T_PLOT, 0.45), (D - 4, END['dawn'])])
        lv['night'] = keys(t, [(0, START['night']), (T_OPEN + 3, 0.3), (T_PLOT, 0.3), (D - 4, END['night'])])
        lv['moon'] = keys(t, [(0, START['moon']), (T_PLOT, 0.0), (D - 4, END['moon'])])
        fr = shore(S, T, lv)

        # the oath's red breath, carried over from the last scene for a moment
        breath = 0.5 + 0.5 * np.sin(2 * np.pi * (t + 80 - SLAM) / 3.0)
        fr += light(BLOOD, 0.3 * breath * (1 - smoothstep(0, 4.0, t)) * S['shore'])

        # the cowhorns: orange blasts out of the doors; the doors swing open in a flood of amber
        a, i = recent(horns, t, 1.5)
        if a is not None:
            r = 2000 * (1 - np.exp(-a / 0.5))
            fr += light(TORCH, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - door) - r) / 150) ** 2))
        if T_OPEN <= t < T_OPEN + 3:
            a = t - T_OPEN
            fr += light(HALL, 1.0 * np.exp(-a / 0.7) * S['porch'])
            fr += light(WHITE, 0.6 * np.exp(-a / 0.12) * np.exp(-((d - door) / 80) ** 2))

        # the torches: the red drains out and they blaze up, swaying in step and flaring on the beat
        red = RED * (1 - smoothstep(T_OPEN, T_OPEN + 3, t))
        lvl = CROWD['lvl'] * keys(t, [(0, 1.0), (T_OPEN, 1.0), (T_OPEN + 3, 1.7), (T_PLOT, 1.7), (T_PLOT + 0.3, 0.6),
                                      (D - 4, FIGS_END['crowd'] / CROWD['lvl'])])
        pos = homes.copy()
        i = int(np.searchsorted(bt, t, side='right')) - 1
        marching = T_MARCH[0] <= t < T_MARCH[1]
        if i >= 0 and marching:
            a, j = t - bt[i], beats[i][1]
            step = np.sin(np.pi * (j % 2 + a / BEAT))
            pos = pos + 9 * sway * step
            lvl = lvl * (1 + 0.35 * np.exp(-a / 0.1) * (1 + (j % 4 == 0)))
            if j % 4 == 0:                  # every bar a whole run flashes rose or gold
                run = seg == RUNS[(j // 4) % len(RUNS)]
                col = GUTRUNE if (j // 4) % 2 == 0 else GUNTHER
                fr = fr * (1 - 0.8 * np.exp(-a / 0.35) * run)[:, None]
                fr += light(col, 1.0 * np.exp(-a / 0.35) * run)
        fr += red_torches(S, T, pos, lvl * keep, red)

        # the couples, with banners of their colours flying out ahead of them on every beat
        pa = procession(door, a1, t) if T_OUT[0] - 1 <= t else door
        pb = procession(p_b, b1, t)
        if T_IN[0] <= t:
            u = smoothstep(*T_IN, t)
            pa = door + (door - door) * u
            pb = p_b + (door - 14 - p_b) * u
        gone = smoothstep(T_IN[1] - 0.5, T_IN[1] + 0.3, t)
        if i >= 0 and marching:
            a, j = t - bt[i], beats[i][1]
            for src, sgn, cols in ((pa, 1, (GUTRUNE, SIEG)), (pb, -1, (GUNTHER, BRUNN))):
                head = src + sgn * 1600 * (1 - np.exp(-a / 0.35))
                ban = np.exp(-((d - head) / 110) ** 2) * (np.sign(d - src) == sgn) * np.exp(-a / 0.5)
                fr = fr * (1 - 0.7 * ban)[:, None]
                fr += light(cols[j % 2], 1.0 * ban)
        for t0, dur, m, v, part, k in gut:
            b = t - t0
            if 0 <= b < 1.0:
                fr += light(GUTRUNE, 0.55 * np.exp(-b / 0.4) * np.exp(-((d - pa) / (60 + 500 * b)) ** 2))
        if T_IN[1] - 0.5 <= t < T_IN[1] + 2.5:
            a = t - T_IN[1] + 0.5
            fr += light(HALL, 0.9 * np.exp(-a / 0.6) * S['porch'])

        # Hagen beneath: a slow violet-black pulse out from the doors every few bars
        for t0 in pulses:
            b = t - t0
            if 0 <= b < 3.0:
                r = 1600 * (1 - np.exp(-b / 0.9))
                fr = fr * (1 - 0.3 * np.exp(-b / 0.8) * np.exp(-((np.abs(d - p_h) - r) / 200) ** 2))[:, None]
                fr += light(HAGEN, 0.5 * np.exp(-b / 1.1) * np.exp(-((np.abs(d - p_h) - r) / 200) ** 2))

        # the conspiracy breaks through: a violet-black slam, blood seeping out from Hagen
        if T_PLOT <= t:
            b = t - T_PLOT
            fr = fr * (1 - 0.8 * np.exp(-b / 0.6))
            fr += light(HAGEN, 0.95 * np.exp(-b / 0.5) * (b < 3))
            seep = 1200 * (1 - np.exp(-b / 2.0))
            fr += light(BLOOD, 0.7 * np.exp(-b / 6.0) * smoothstep(seep + 80, seep - 80, np.abs(d - p_h)))
        for t0, dur, m, v, part, k in plot:
            b = t - t0
            if 0 <= b < dur + 0.8:
                fr += light(HAGEN, 0.6 * smoothstep(0, 0.2, b) * np.exp(-b / (dur + 0.3)) * S['porch'])
        for t0 in tri:
            b = t - t0
            if 0 <= b < 2.5:
                r = 1800 * (1 - np.exp(-b / 0.5))
                fr = fr * (1 - 0.5 * np.exp(-b / 0.25))
                fr += light(HAGEN, 0.9 * np.exp(-b / 0.9) * smoothstep(r + 40, r - 200, np.abs(d - p_h)))

        # the people
        fr = figure(fr, S, p_h, HAGEN, 0.85)
        if gone < 1:
            pg = g0 + (pb + 14 - g0) * smoothstep(T_OPEN, T_OUT[0], t)
            fr = figure(fr, S, pg if t < T_OUT[0] else pb + 14, GUNTHER, 0.85 * (1 - gone), w=22.0)
            fr = brunnhilde(fr, S, pb, 0.85 * (1 - gone), T)
            if t >= T_OUT[0] - 1:
                al = (1 - gone) * smoothstep(T_OUT[0] - 1, T_OUT[0], t)
                fr = figure(fr, S, pa + 14, GUTRUNE, 0.85 * al, w=22.0)
                fr = siegfried(fr, S, pa, 0.85 * al)
                fr += light(GOLD, 0.7 * al * np.exp(-((d - pa - 10) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the stage adds the doors, the crowd's feet, the
    banners' cymbals and the final slam."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.8)
    # the crowd's feet sit under the procession, well back; the stage leads only at the doors and the slam
    o.effects([(0, -2), (T_OPEN + 2, -2), (T_OPEN + 3, -9), (T_PLOT - 0.3, -9), (T_PLOT, 0), (D, 0)])
    o.tutti(tidy(EX['notes']), size=lambda t: 1.0)
    pd_, ph = pan_at(at(G, *DOOR)), pan_at(at(G, *HAGEN_AT))
    o.boom(T_OPEN, pd_, 0.6)
    o.hit('crash', T_OPEN, 112, gain=0.45, pan=pd_)
    pans = [pan_at(at(G, r, 0.5)) for r in RUNS]
    for t, d, m, v, part, k in compose():
        if part == 'bass':                  # the crowd stepping with the procession
            o.M.add('fx', o.hits['hoof soft'].play(84 + 12 * (k % 4 == 0)), t, 0.4, pans[k % len(pans)])
            if k % 8 == 0:
                o.hit('crash', t, 92, gain=0.22, pan=pans[(k // 4) % len(pans)])
        elif part == 'pulse':
            o.hit('gong', t, 96, gain=0.3, pan=ph)
    o.boom(T_PLOT, ph, 1.0)                 # the plot breaks through
    o.hit('gong', T_PLOT + 0.02, 124, gain=0.6, pan=ph)
    for t0 in T_TRITONE:
        o.hit('timpani', t0, 120, pitch=-7, gain=0.7, pan=ph)
