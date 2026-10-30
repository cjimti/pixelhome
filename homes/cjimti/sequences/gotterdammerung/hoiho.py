"""Hoiho!: a red dawn on the shore. Hagen, ultraviolet by his spear at the hall doors, puts the great cowhorn to
his lips and calls the Gibichung vassals to arms: "Hoiho! Hoihohoho!" Each blast is a shock of violet out of him
with an orange front racing to both ends of the house in a second, the doors flaring, the whole shore jolting
awake. From far off the cowhorns answer, a semitone apart (C, D flat, D), from the river end of Right, from the
far end of the Side, from the front of Left: each answer flashes its end of the house orange and wakes that run
for good, so the house lights up run by run.

Then the vassals' call (Donington 54) breaks out in the trombones, "Hoiho! Hagen! Welche Not?", every note a hard
hit that throws one whole run into torch orange, round the house, faster and faster as the men run up, while the
first torches catch here and there in sprays of sparks. Hagen answers on his falling tritone (61a), the house
flashing violet from the doors; at the end the shore stands in full red dawn, waiting for its men.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'GD16'
TITLE = 'Hoiho!'
KIND = 'show'
DESCRIPTION = ('At dawn Hagen blows the great cowhorn and calls his men to arms. Every blast shakes the whole house, '
               'horns answer from every side, and the vassals come running.')
VOICEOVER = ('Hagen blows the war horn. Hoiho! Hoiho! From every side, the men come running.')

K = 1                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_CALL = [2.0, 10.5, 19.0, 27.5]            # Hagen's cowhorn blasts
ANSWERS = [(5.0, 'Right', 1.0, 'Db'), (13.5, 'Side', 0.0, 'D'), (22.0, 'Left', 0.15, 'Db'), (30.0, 'Right', 0.55, 'D'),
           (31.2, 'Side', 0.4, 'Db'), (32.4, 'Left', 0.6, 'D')]
T_VASSALS = [35.0, 40.0, 44.5, 48.5, 52.0, 55.0]   # the vassals' call, closer and closer
T_TRITONE = [59.0, 63.0]                    # Hagen answers
T_LAST = 67.0                               # one last great blast
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

START = dict(night=0.3, moon=0.1, dawn=0.6, hall=0.5, spear=0.6)      # where GD15 left the shore
END = dict(night=0.2, moon=0.0, dawn=0.7, hall=0.65, spear=0.7)        # where GD17 picks it up
HAGEN_AT = ('Porch Front', 0.35)
HAGEN_LVL = (0.8, 0.85)
RUNS = ['Right', 'Left', 'Porch Right', 'Side', 'Porch Left', 'Porch Front']


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

    add(0.0, D, 'C2', 60, 'pedal')
    for k, t0 in enumerate(T_CALL):         # "Hoiho! Hoihohoho!" on the cowhorn: a long C, then three short
        add(t0, 1.6, 'C3', 112 + 4 * k, 'horn', k)
        for j in range(3):
            add(t0 + 1.9 + j * 0.35, 0.3, 'C3', 104 + 4 * k, 'horn', k)
        add(t0, 0.5, 'C2', 118, 'boom', k)
    for i, (t0, run, u, pitch) in enumerate(ANSWERS):
        add(t0, 1.2, pitch + '3', 96 + 3 * i, 'answer', i)
    for k, t0 in enumerate(T_VASSALS):
        for t, m, v, d in play('vassals', t0, 0.42 - 0.025 * k, 0, 100 + 4 * k):
            add(t, d, m, v, 'vassals', k)
    for k, t0 in enumerate(T_TRITONE):
        for t, m, v, d in play('hagen', t0, 1.0, -12, 112):
            add(t, d, m, v, 'tritone', k)
    add(T_LAST, 2.4, 'C3', 124, 'horn', 4)
    add(T_LAST, 0.5, 'C2', 124, 'boom', 4)
    for m in ('C3', 'Eb3', 'G3'):
        add(T_LAST + 3.0, D - T_LAST - 3.0, m, 64, 'held')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=16):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_h = at(G, *HAGEN_AT)
    blasts = sorted({e[0] for e in N if e[4] == 'boom'})
    vas = [e for e in N if e[4] == 'vassals']
    tri = sorted({e[0] for e in N if e[4] == 'tritone'})
    rng = np.random.default_rng(seed)
    catches = [(float(t), float(rng.uniform(0.9, 1.2)), float(rng.uniform(40, L - 40)))
               for t in np.sort(rng.uniform(T_VASSALS[1], T_LAST + 4, 26))]
    seg = G.seg_of

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_LAST, START[k] + 0.5 * (END[k] - START[k])), (T_LAST + 8, END[k])])
              for k in START}
        fr = shore(S, T, lv)

        # the runs the answering horns have woken stay lit in torch orange, and pulse with the vassals' call
        for t0, run, u, pitch in ANSWERS:
            if t >= t0:
                a = t - t0
                woke = 0.5 * smoothstep(0, 1.5, a) * (1 - smoothstep(T_LAST + 2, T_LAST + 10, t))
                fr += light(TORCH, woke * (seg == run) * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 160 - 0.4 * t))))
                if a < 1.6:
                    src = at(G, run, u)
                    fr += light(TORCH, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - src) / (120 + 500 * a)) ** 2))
                    fr += light(FLAME, 0.9 * np.exp(-a / 0.12) * np.exp(-((d - src) / 30) ** 2))

        # each blast of the cowhorn: a violet shock out of Hagen with an orange front racing to both ends
        for k, t0 in enumerate(blasts):
            a = t - t0
            if 0 <= a < 2.6:
                s = 0.85 + 0.15 * (k == len(blasts) - 1)
                r = 2000 * (1 - np.exp(-a / 0.9))
                fr += light(HAGEN, s * np.exp(-a / 1.3) * smoothstep(r + 40, r - 160, np.abs(d - p_h)))
                fr += light(TORCH, s * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p_h) - r) / 70) ** 2))
                fr += light(FLAME, 0.7 * s * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_h) - r) / 25) ** 2))
                fr += light(HALL, 0.8 * s * np.exp(-a / 0.4) * S['porch'])

        # the vassals' call: every note throws one whole run into torch orange, round the house
        for j, (t0, dur, m, v, part, k) in enumerate(vas):
            a = t - t0
            if 0 <= a < 0.9:
                run = RUNS[j % len(RUNS)]
                fr += light(TORCH, (0.75 + 0.05 * k) * np.exp(-a / 0.28) * (seg == run))
                fr += light(FLAME, 0.4 * np.exp(-a / 0.1) * (seg == run))

        # the first torches catching: sprays of sparks here and there
        fr += light(FLAME, np.clip(sparks(S, catches, t, 16, n=10, reach=0.4), 0, 1))

        # Hagen answers on his tritone: the house flashes violet from the doors
        for t0 in tri:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(HAGEN, 0.85 * np.exp(-a / 0.7) * smoothstep(1500 * a + 80, 1500 * a - 80, np.abs(d - p_h)))

        # Hagen at the doors, swelling with each blast
        swell = sum(np.exp(-(t - t0) / 0.8) for t0 in blasts if 0 <= t - t0 < 4)
        lvl = HAGEN_LVL[0] + (HAGEN_LVL[1] - HAGEN_LVL[0]) * smoothstep(T_LAST, T_LAST + 8, t)
        fr = figure(fr, S, p_h, HAGEN, min(1.0, lvl + 0.25 * swell))
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

    for name, gain, rev in (('low', 0.48, 0.25), ('brass', 0.48, 0.3), ('horns', 0.45, 0.45), ('perc', 0.42, 0.3),
                            ('strings', 0.4, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbn_st = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v6*.wav')
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
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v + 20, 0.0, rise=2.0, fall=2.0, gain=0.7)
        elif part == 'horn':                # the cowhorn: horn and trombone in unison, rough and loud
            if d > 1.0:
                hold('horns', horn, m, t, t + d, v, ph, rise=0.08, fall=0.4, gain=0.9)
                hold('horns', tbn, m, t, t + d, v - 8, ph, rise=0.08, fall=0.4, gain=0.6)
            else:
                M.add('horns', horn.play(m, v, dur=d, release=0.12), t, 0.9, ph)
                M.add('horns', tbn_st.play(m, v - 8), t, 0.6, ph)
        elif part == 'boom':
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, ph)
            M.add('perc', bd.play(v), t, 0.7, ph)
            if k == 4:
                M.add('perc', crash.play(120), t, 0.8, ph)
        elif part == 'answer':
            run, u = ANSWERS[k][1], ANSWERS[k][2]
            p = pan_at(at(G, run, u))
            hold('horns', horn, m, t, t + d, v, p, rise=0.1, fall=0.6, gain=0.55)
        elif part == 'vassals':
            M.add('brass', tbn_st.play(m, v), t, 0.9, 0.0)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.1, release=0.15), t, 0.7, 0.0)
            if d >= 0.25:
                M.add('perc', timp.play(v - 14, pitch=-3), t, 0.5, 0.0)
        elif part == 'tritone':
            hold('low', tuba, m, t, t + d, v, ph, rise=0.1, fall=1.0, gain=0.9)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d, release=0.5), t, 0.7, ph)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, ph)
        elif part == 'held':
            hold('strings', vc, m, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.5)
