"""The Vassals: the Gibichung men answer Hagen's horn. They come running with torches, first a few racing in along
Right from the river end, then more and more, popping up on every front run, until the whole shore in red dawn is
a sea of torch points, a hundred and more flames over every run of the house. Their call (Donington 54) rings out
in the trombones again and again, "Hoiho! Hoiho!", and the crowd stomps on the beat: every beat all the torches
flare at once and one whole run thumps orange, round the house.

Hagen, ultraviolet at the doors by his spear, commands them on his falling tritone (61a): each time a violet shock
runs out from him, the torches duck and blaze back up. He tells them to slaughter for the gods and drink till they
drop, and the men burst out laughing, every torch on the house flickering wildly. Then a boat comes up the
river: Gunther, royal gold, and Gutrune in rose come in along Right from its free end, and the men hail them, gold
and rose waves rolling over the sea of torches to Gutrune's motif (40).

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'GD17'
TITLE = 'The Vassals'
KIND = 'show'
DESCRIPTION = ('The men come running with torches from every side until the whole house is a sea of flames, stamping '
               'on the beat. Hagen commands them, they roar with laughter, and Gunther arrives with his bride-to-be.')
VOICEOVER = ('Torches everywhere! The men pour in from every side, a hundred flames, stamping and shouting.')

K = 2                                       # this scene's place on Act II's shared clock: T = t + 80 K
BEAT = 0.5
T_STOMP = (8.0, 58.0)                       # the crowd stomps on the beat
T_VASSALS = [4.0, 14.0, 22.0, 34.0, 42.0]   # their call
T_TRITONE = [29.0, 49.0]                    # Hagen commands
T_LAUGH = (53.0, 58.0)                      # they laugh
T_BOAT = 60.0                               # Gunther and Gutrune come up the river
T_THERE = 70.0
T_HAIL = [63.0, 67.0, 71.0]                 # "Heil dir, Gunther!"
T_GUTRUNE = 72.0
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

START = dict(night=0.2, moon=0.0, dawn=0.7, hall=0.65, spear=0.7)       # where GD16 left the shore
END = dict(night=0.2, moon=0.0, dawn=0.7, hall=0.65, spear=0.7)         # where GD18 picks it up
HAGEN_AT = ('Porch Front', 0.35)
HAGEN_LVL = 0.85
GUNTHER_AT = ('Right', 0.25)
GUTRUNE_AT = ('Right', 0.4)
COUPLE_LVL = 0.85
CROWD = dict(n=140, seed=1717, lvl=0.7)     # every vassal's torch at the end: crowd(S, n, seed) at level lvl
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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'Eb2', 64, 'pedal')
    t = T_STOMP[0]
    j = 0
    while t < T_STOMP[1] - 1e-6:            # the stomp: a heavy beat, an accent every bar
        add(t, 0.2, 'C2', 96 + 18 * (j % 4 == 0), 'stomp', j)
        t += BEAT
        j += 1
    for k, t0 in enumerate(T_VASSALS):
        for tt, m, v, d in play('vassals', t0, 0.38, 0, 104 + 3 * k):
            add(tt, d, m, v, 'vassals', k)
    for k, t0 in enumerate(T_TRITONE):
        for tt, m, v, d in play('hagen', t0, 0.9, -12, 116):
            add(tt, d, m, v, 'tritone', k)
    for j, tt in enumerate(np.arange(T_LAUGH[0], T_LAUGH[1], 0.16)):     # "Ha ha ha!" in staccato brass
        add(tt, 0.12, ('C4', 'Eb4', 'G4', 'Eb4')[j % 4], 92 + (j % 3) * 6, 'laugh', j)
    for k, t0 in enumerate(T_HAIL):         # "Heil dir, Gunther!": three great chords
        for m in ('Eb3', 'G3', 'Bb3', 'Eb4'):
            add(t0, 1.6, m, 112, 'hail', k)
        add(t0, 0.5, 'Eb2', 118, 'hailboom', k)
    for tt, m, v, d in play('gutrune', T_GUTRUNE, 0.5, -5, 92):
        add(tt, d, m, v, 'gutrune')
    return sorted(N, key=lambda e: e[0])


def arrivals(S):
    """Each vassal: (home, arrival time, runs in from the river end?)."""
    homes = crowd(S, CROWD['n'], CROWD['seed'])
    rng = np.random.default_rng(171)
    ta = np.sort(3.0 + 52.0 * rng.uniform(0, 1, len(homes)) ** 0.8)
    rng.shuffle(ta)
    runner = rng.uniform(0, 1, len(homes)) < 0.35
    return homes, ta, runner


def render(G, seed=17):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_h = at(G, *HAGEN_AT)
    homes, ta, runner = arrivals(S)
    stomps = [(e[0], e[5]) for e in N if e[4] == 'stomp']
    st_t = np.array([s[0] for s in stomps])
    vas = [e for e in N if e[4] == 'vassals']
    tri = sorted({e[0] for e in N if e[4] == 'tritone'})
    hails = sorted({e[0] for e in N if e[4] == 'hailboom'})
    gut = sorted({e[0] for e in N if e[4] == 'gutrune'})
    rng = np.random.default_rng(seed)
    wild = rng.uniform(0, 2 * np.pi, len(homes))
    seg = G.seg_of
    p_gn, p_gt = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['dawn'] = keys(t, [(0, START['dawn']), (8, 0.4), (56, 0.4), (66, 0.55), (76, END['dawn'])])
        lv['night'] = keys(t, [(0, START['night']), (8, 0.32), (56, 0.32), (76, END['night'])])
        fr = shore(S, T, lv)

        # where every vassal is: running in from the river end, popping up where he stands, or there already
        here = t >= ta
        pos = homes.copy()
        run = here & runner & (t - ta < 2.5)
        u = smoothstep(0, 2.5, t - ta[run])
        pos[run] = L + 30 + (homes[run] - L - 30) * u
        lvl = np.where(here, CROWD['lvl'], 0.0)
        pop = here & ~runner & (t - ta < 0.6)
        lvl = lvl + np.where(pop, 0.8 * np.exp(-(t - ta) / 0.15), 0.0)

        # the stomp: every beat all the torches flare and one whole run thumps orange
        i = int(np.searchsorted(st_t, t, side='right')) - 1
        if i >= 0 and t - st_t[i] < BEAT and T_STOMP[0] <= t < T_STOMP[1]:
            a, j = t - st_t[i], stomps[i][1]
            acc = 1.0 + 0.6 * (j % 4 == 0)
            lvl = lvl * (1 + 0.45 * acc * np.exp(-a / 0.12))
            fr += light(TORCH, 0.85 * acc * np.exp(-a / 0.16) * (seg == RUNS[j % len(RUNS)]))

        # Hagen's command: a violet shock out of him; the torches duck and blaze back
        for t0 in tri:
            a = t - t0
            if 0 <= a < 3.0:
                r = 1700 * (1 - np.exp(-a / 0.6))
                fr += light(HAGEN, 0.95 * np.exp(-a / 1.0) * smoothstep(r + 40, r - 160, np.abs(d - p_h)))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.08) * np.exp(-((d - p_h) / 30) ** 2))
                behind = np.abs(homes - p_h) < r
                lvl = np.where(behind, lvl * (0.25 + 0.75 * smoothstep(0.3, 2.5, a)) * (1 + 0.6 * np.exp(-(a - 0.3) ** 2 / 0.2)), lvl)

        # the laughter: every torch flickering wildly
        if T_LAUGH[0] <= t < T_LAUGH[1] + 0.5:
            g = smoothstep(T_LAUGH[0], T_LAUGH[0] + 0.3, t) * (1 - smoothstep(T_LAUGH[1], T_LAUGH[1] + 0.5, t))
            lvl = lvl * (1 + g * 0.8 * np.sin(31 * t + wild) ** 2 - 0.3 * g)

        fr += torches(S, T, pos[lvl > 0], lvl[lvl > 0], seed=7)

        # the vassals' call: every note a burst of sparks from a run of the crowd
        for j, (t0, dur, m, v, part, k) in enumerate(vas):
            a = t - t0
            if 0 <= a < 0.6:
                r_ = RUNS[(j + k) % len(RUNS)]
                fr += light(FLAME, 0.6 * np.exp(-a / 0.15) * (seg == r_))

        # the boat: Gunther and Gutrune come up the river along Right
        if t >= T_BOAT:
            u = smoothstep(T_BOAT, T_THERE, t)
            for p_end, col, lag in ((p_gn, GUNTHER, 0.0), (p_gt, GUTRUNE, 1.2)):
                uu = smoothstep(T_BOAT + lag, T_THERE, t)
                p = L + 30 + (p_end - L - 30) * uu
                fr = figure(fr, S, p, col, COUPLE_LVL * smoothstep(T_BOAT + lag, T_BOAT + lag + 0.8, t), w=22.0)
                if uu < 1:
                    wake = smoothstep(p + 220, p, d) * (d >= p)
                    fr += light(col, 0.45 * wake * (1 - uu))

        # "Heil dir, Gunther!": gold and rose waves rolling over the torches from the couple
        for k, t0 in enumerate(hails):
            a = t - t0
            if 0 <= a < 3.0:
                src = L + 30 + (p_gn - L - 30) * smoothstep(T_BOAT, T_THERE, t0)
                r = 2400 * (1 - np.exp(-a / 0.9))
                col = GUNTHER if k % 2 == 0 else GUTRUNE
                fr += light(col, 1.0 * np.exp(-a / 1.3) * smoothstep(r + 60, r - 260, np.abs(d - src)) * smoothstep(r - 700, r - 260, np.abs(d - src)))
                fr += light(WHITE, 0.5 * np.exp(-a / 0.1) * np.exp(-((d - src) / 40) ** 2))
        for t0 in gut:
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(GUTRUNE, 0.5 * np.exp(-a / 0.4) * np.exp(-((d - p_gt) / (60 + 400 * a)) ** 2))

        fr = figure(fr, S, p_h, HAGEN, HAGEN_LVL)
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

    for name, gain, rev in (('low', 0.4, 0.25), ('brass', 0.42, 0.3), ('perc', 0.38, 0.25), ('winds', 0.34, 0.35),
                            ('strings', 0.34, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbn_st = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tpt_st = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v6*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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
    gn = pan_at(at(G, *GUNTHER_AT))
    river = pan_at(at(G, 'Right', 0.95))
    pans = [pan_at(at(G, r, 0.5)) for r in RUNS]
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v + 10, 0.0, rise=2.0, fall=2.0, gain=0.6)
        elif part == 'stomp':
            p = pans[k % len(pans)]
            M.add('perc', bd.play(v), t, 0.8, p)
            if k % 4 == 0:
                M.add('perc', timp.play(v, pitch=-4), t, 0.7, p)
            else:
                M.add('perc', snare.play(v - 30), t + 0.25, 0.3, p)
        elif part == 'vassals':
            M.add('brass', tbn_st.play(m, v), t, 0.9, 0.0)
            M.add('brass', tbn_st.play(m - 12, v - 6), t, 0.7, 0.0)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.1, release=0.15), t, 0.6, 0.0)
        elif part == 'tritone':
            hold('low', tuba, m, t, t + d, v, ph, rise=0.1, fall=1.0, gain=0.9)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d, release=0.5), t, 0.7, ph)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, ph)
        elif part == 'laugh':
            M.add('brass', tbn_st.play(m - 12, v), t, 0.6, pans[k % len(pans)])
            M.add('brass', tpt_st.play(m, v - 20), t, 0.3, pans[(k + 3) % len(pans)])
        elif part == 'hail':
            hold('brass', horn, m, t, t + d, v, gn * 0.5, rise=0.08, fall=0.8, gain=0.6)
            hold('brass', tbn, m - 12, t, t + d, v - 6, gn * 0.5, rise=0.08, fall=0.8, gain=0.55)
        elif part == 'hailboom':
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, gn)
            M.add('perc', crash.play(110), t, 0.6, gn)
        elif part == 'gutrune':
            if m >= note('C5'):
                M.add('strings', vln.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.6, gn)
            else:
                M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.8, gn)
