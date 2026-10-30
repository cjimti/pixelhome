"""Vengeance: the shore emptied of the wedding, the torches low and turning blood red, Brünnhilde by Hagen's spear,
Gunther shamed on Right, Hagen at the doors. She grieves first ("Wer bietet mir nun das Schwert?"): her silver
shudders and drips down to the ground in falling ripples. Hagen offers her his help ("Vertraue mir, betrog'ne
Frau!"), violet shocks knocking through the dark, and Gunther comes over from Right, gold, to the corner of the
porch.

"So soll es sein! Siegfried falle!": Gunther, then Brünnhilde, and every long note is a deep red swell over the
whole house. Then the three of them swear together, and their three colours, silver, gold and violet-black, break
from where they stand and run round the house in bands, braiding back and forth end to end, faster and faster on
the pounding bass, flashing white wherever two cross, Hagen's calls on Alberich cutting through in violet, the
Curse slashing red, until "Wotan! Wende dich her!" and the braid becomes one: three great chords, each a whole house
of one colour, silver, gold, violet; then a black slam, and blood red floods out from the spear to both ends of
the house.

The music is Wagner's own: Act II, scene 5, her grief and Hagen's offer (bars 1386 to 1393), "So soll es sein"
(1619 to 1623) and the oath of vengeance to its end (1640 to 1671), as Solti's 1958 Vienna Philharmonic recording
takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py) orchestrated by hand and register.
The stage adds a gong and timpani under Hagen's shocks, a deep drum under each red swell, a cymbal swell into the
three chords and a gong and thunder on the slam; it keeps out of the way of the trio itself.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD20'
TITLE = 'Vengeance'
KIND = 'show'
DESCRIPTION = ('Brünnhilde, Gunther and Hagen swear Siegfried\'s death. Silver, gold and violet run round the house '
               'faster and faster, braiding together until they become one, and blood red floods out to both ends.')
VOICEOVER = ('Betrayed, Brünnhilde joins Hagen and Gunther. Together, they swear that Siegfried must die.')

K = 5                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1386-1393, 1619-1623 and 1640-1671, Solti 1958
D = EX['seconds']
_SEG = [(g['start'], g['start'] + g['seconds']) for g in EX['segments']]


def _sung(who, text):
    """When the first sung line by who beginning with text starts."""
    return next(t0 for t0, t1, w, x in EX['singing'] if w.startswith(who) and x.startswith(text))


_LATE = accents(EX['notes'], _SEG[2][1] - 10, D, vmin=95, n=4, space=0.8)
T_GRIEF = 0.3                               # her grief
T_TRITONE = [_sung('Hagen', 'Vertraue'), _sung('Hagen', 'Wer dich')]    # "Vertraue mir"
T_GUNTHER = (_sung('Hagen', 'Wer dich') - 1.0, _SEG[1][0])              # Gunther crosses to the corner of the porch
T_PLOT = [_sung('Gunther', 'So soll'), _sung('Brünnhilde', 'So soll')]  # "So soll es sein! Siegfried falle!"
T_BRAID = (_SEG[2][0], _LATE[0])            # the three colours braid round the house
T_BRAID_TRI = [t0 for t0, t1, w, x in EX['singing'] if w == 'Hagen' and t0 >= _SEG[2][0]]   # his calls on Alberich
T_CURSE = _sung('Brünnhilde', 'Allrauner')
T_PLOT2 = _sung('Gunther', 'Wotan! Wende')
T_CHORDS = _LATE[:3]                        # silver, gold, violet
T_SLAM = _LATE[3]                           # the black slam

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

START = dict(night=0.3, moon=0.0, dawn=0.5, hall=0.6, spear=0.8)        # where GD19 left the shore
END = dict(night=0.4, moon=0.0, dawn=0.35, hall=0.4, spear=0.75)        # where GD21 picks it up
HAGEN_AT = ('Porch Front', 0.35)
GUNTHER_FROM, GUNTHER_AT = ('Right', 0.25), ('Porch Right', 0.55)
BRUNN_AT = ('Porch Front', 0.44)
CROWD = dict(n=140, seed=1717, lvl=0.32)    # as GD19 left it
CLEAR_AT = [('Porch Front', 0.35), ('Right', 0.25), ('Right', 0.4), ('Right', 0.12), ('Porch Right', 0.8)]
CLEAR = 30.0
RED = 0.75                                  # how far the torches have turned blood red at the end
FIGS_END = dict(hagen=(*HAGEN_AT, 0.85), gunther=(*GUNTHER_AT, 0.75), brunnhilde=(*BRUNN_AT, 0.85), crowd=0.28)


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


def red_torches(S, T, ps, lvl, red):
    """The torches, turned towards blood red by `red` (0..1)."""
    tf = torches(S, T, ps, lvl, seed=7)
    v = tf.max(1)
    return tf * (1 - red) + BLOOD[None, :] * (v * red * 1.6)[:, None]


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'score'. The right hand under
    her grief is 'grief', the bass's long notes under "So soll es sein" 'plot', the bass under the oath 'ost';
    'tritone', 'curse', 'chord', 'chordhit', 'slam' and 'slamhit' mark moments. Only 'score' sounds."""
    N = [(t, d, m, v, 'score', h) for t, d, m, v, h in EX['notes']]
    for t0 in accents([n for n in EX['notes'] if n[4] == 0], T_GRIEF, T_TRITONE[0], vmin=1, n=1, space=0.35):
        N.append((t0, 0.6, 72, 70, 'grief', None))
    for k, t0 in enumerate(T_TRITONE + T_BRAID_TRI):
        N.append((t0, 1.0, 36, 0, 'tritone', k))
    lh = [n for n in EX['notes'] if n[4] == 1]
    for k, t0 in enumerate(T_PLOT + [T_PLOT2]):
        N.append((t0, 2.5, 41, 100, 'plot', k))
    for j, t0 in enumerate(accents(lh, T_BRAID[0], T_BRAID[1], vmin=1, n=1, space=0.2)):
        N.append((t0, 0.2, 41, 100, 'ost', j))
    N.append((T_CURSE, 1.0, 48, 0, 'curse', None))
    for k, t0 in enumerate(T_CHORDS):
        N.append((t0, 1.0, 60, 0, 'chord', k))
        N.append((t0, 0.5, 29, 0, 'chordhit', k))
    N.append((T_SLAM, 2.5, 41, 0, 'slam', None))
    N.append((T_SLAM, 0.5, 29, 0, 'slamhit', None))
    return sorted(N, key=lambda e: e[0])


def bounce(s, L):
    """A position that runs 0..L and back, for travelled distance s."""
    s = s % (2 * L)
    return s if s < L else 2 * L - s


def render(G, seed=20):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    homes = crowd(S, CROWD['n'], CROWD['seed'])
    keep = np.min([np.abs(homes - at(G, *c)) for c in CLEAR_AT], axis=0) >= CLEAR   # out since GD18
    p_h, p_b = at(G, *HAGEN_AT), at(G, *BRUNN_AT)
    g0, g1 = at(G, *GUNTHER_FROM), at(G, *GUNTHER_AT)
    grief = [e for e in N if e[4] == 'grief']
    tri = sorted({e[0] for e in N if e[4] == 'tritone'})
    plot = [e for e in N if e[4] == 'plot']
    ost = np.array(sorted({e[0] for e in N if e[4] == 'ost'}))
    curse_on = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    thumps = np.array(sorted({e[0] for e in N if e[4] == 'thump'}))
    tt = np.arange(F) * DT
    speed = np.where((tt >= T_BRAID[0]) & (tt < T_BRAID[1]),
                     250 + 2300 * smoothstep(T_BRAID[0], T_BRAID[1], tt) ** 1.6, 0.0)
    travel = np.cumsum(speed) * DT
    bands = [(p_b, 1.0, BRUNN), (g1, -0.82, GUNTHER), (p_h, -1.21, HAGEN)]     # each its own way and speed

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_BRAID[0], START[k]), (D, END[k])]) for k in START}
        braid = smoothstep(T_BRAID[0], T_BRAID[0] + 1, t) * (1 - smoothstep(T_CHORDS[0], T_CHORDS[0] + 0.2, t))
        lv['dawn'] *= 1 - 0.5 * braid
        fr = shore(S, T, lv)

        # the torches: sinking and turning blood red
        red = RED * smoothstep(0, 14, t)
        lvl = CROWD['lvl'] * keys(t, [(0, 1.0), (14, 0.85), (T_BRAID[0], 0.85), (D, FIGS_END['crowd'] / CROWD['lvl'])])
        a, i = recent(ost, t, 0.5)
        if a is not None:
            lvl = lvl * (1 + 0.8 * braid * np.exp(-a / 0.08))
        fr += red_torches(S, T, homes, lvl * keep, red)

        # her grief: silver dripping down out of her in falling ripples
        for t0, dur, m, v, part, k in grief:
            b = t - t0
            if 0 <= b < 1.8:
                r = 900 * b
                fr += light(BRUNN, 0.75 * np.exp(-b / 0.7) * np.exp(-((np.abs(d - p_b) - r) / 80) ** 2))

        # Hagen's tritone: violet shocks, the house knocked dark behind them
        for t0 in tri:
            b = t - t0
            if 0 <= b < 2.5:
                r = 1900 * (1 - np.exp(-b / 0.5))
                fr = fr * (1 - 0.55 * np.exp(-b / 0.25))
                fr += light(HAGEN, 0.95 * np.exp(-b / 0.9) * smoothstep(r + 40, r - 200, np.abs(d - p_h)))

        # the conspiracy: every long note a deep red swell over the whole house
        for t0, dur, m, v, part, k in plot:
            b = t - t0
            if 0 <= b < dur + 1.0:
                g = smoothstep(0, 0.25, b) * np.exp(-b / (dur + 0.4))
                fr += light(BLOOD, 0.7 * g * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 400 - 0.4 * t))))
                fr += light(HAGEN, 0.4 * g * S['porch'])

        # the braid: silver, gold and violet bands running round the house, faster and faster, white where they cross
        if braid > 0:
            heads = []
            for p0, sgn, col in bands:
                c = bounce(p0 + sgn * travel[f], L)
                heads.append(c)
                prev = bounce(p0 + sgn * travel[max(f - 6, 0)], L)
                tail = np.clip(1 - np.abs(d - (c + prev) / 2) / (np.abs(c - prev) / 2 + 60), 0, 1)
                fr = fr * (1 - 0.7 * braid * np.exp(-((d - c) / 90) ** 2))[:, None]
                fr += light(col, braid * (np.exp(-((d - c) / 70) ** 2) + 0.7 * tail))
            for x in range(3):
                for y in range(x + 1, 3):
                    if abs(heads[x] - heads[y]) < 120:
                        m_ = (heads[x] + heads[y]) / 2
                        fr += light(WHITE, braid * (1 - abs(heads[x] - heads[y]) / 120)
                                    * np.exp(-((d - m_) / 50) ** 2))

        # the Curse cuts through: blood red slashing out from the spear
        a, i = recent(curse_on, t, 2.5)
        if a is not None:
            front = min(1.0, (t - curse_on[0]) / 0.8) * max(S['spear'], L - S['spear'])
            fr += light(BLOOD, 0.9 * smoothstep(front + 50, front - 50, np.abs(d - S['spear'])) * np.exp(-a / 0.8))

        # the oath in unison: three chords, a whole house of each colour; then the slam and the flood of blood
        for k, t0 in enumerate(T_CHORDS):
            b = t - t0
            if 0 <= b < 1.2:
                col = (BRUNN, GUNTHER, HAGEN)[k]
                fr = fr * (1 - 0.85 * np.exp(-b / 0.4))
                fr += light(col, (0.8 if k == 0 else 1.0) * np.exp(-b / 0.4))
        if T_SLAM - 0.25 <= t < T_SLAM:
            fr = fr * 0.1
        if T_SLAM <= t < T_SLAM + 6:
            b = t - T_SLAM
            front = (max(S['spear'], L - S['spear']) + 100) * min(1.0, b / 0.9)
            flood = smoothstep(front + 80, front - 80, np.abs(d - S['spear']))
            fr = fr * (1 - 0.5 * np.exp(-b / 1.5))
            fr += light(BLOOD, (0.95 * np.exp(-b / 2.5) + 0.05) * flood)
            fr += light(WHITE, 0.8 * np.exp(-b / 0.1) * np.exp(-((d - S['spear']) / 60) ** 2))
            fr += light(BLOOD, 0.9 * np.exp(-((np.abs(d - S['spear']) - front) / 40) ** 2) * (b < 1.2))

        # the three of them; after the oath they breathe red
        pg = g0 + (g1 - g0) * smoothstep(*T_GUNTHER, t)
        after = smoothstep(T_SLAM + 2, T_SLAM + 6, t)
        breath = after * (0.5 + 0.5 * np.sin(2 * np.pi * (t - T_SLAM) / 3.0))
        fr += light(BLOOD, 0.3 * breath * S['shore'])
        a, i = recent(thumps, t, 1.8)
        if a is not None:                   # the heartbeat: a blood ring out from the spear, lub and dub
            for lag, s_ in ((0.0, 0.85), (0.28, 0.55)):
                b = a - lag
                if b >= 0:
                    r = 1500 * (1 - np.exp(-b / 0.5))
                    fr += light(BLOOD, s_ * np.exp(-b / 0.7) * np.exp(-((np.abs(d - S['spear']) - r) / 120) ** 2))
            fr = fr * (1 - 0.25 * np.exp(-a / 0.15))
        fr = figure(fr, S, p_h, HAGEN, 0.85)
        fr = figure(fr, S, pg, GUNTHER, keys(t, [(0, 0.6), (T_GUNTHER[1], 0.8), (D - 6, FIGS_END['gunther'][2])]), w=22.0)
        fr = brunnhilde(fr, S, p_b, 0.85 * (1 - 0.25 * (t < 6) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t))), T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the stage's gong, drums and thunder."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.35)
    # the stage keeps out of the trio's way and comes in with the slam
    o.effects([(0, -6), (T_SLAM - 0.5, -6), (T_SLAM, 0), (D, 0)])
    o.tutti(tidy(EX['notes']), size=lambda t: 0.6 if t < T_PLOT[0] else 1.0)
    ph, psp = pan_at(at(G, *HAGEN_AT)), pan_at(at(G, 'Porch Front', 0.5))
    for k, t0 in enumerate(T_TRITONE):
        o.hit('gong', t0, 100, gain=0.35, pan=ph)
        o.hit('timpani', t0, 116, pitch=-6, gain=0.6, pan=ph)
    for t0 in T_PLOT:
        o.hit('timpani roll', t0, 104, pitch=-5, gain=0.45)
        o.hit('bass drum', t0, 118, gain=0.5)
    o.hit('cymbal swell', T_CHORDS[0] - 3.0, 104, gain=0.45)
    for k, t0 in enumerate(T_CHORDS):
        o.hit('crash', t0, 112 + 4 * k, gain=0.45)
    o.boom(T_SLAM, psp, 1.0)
    o.thunder(T_SLAM + 0.05, 1.0, psp, 0.8)
