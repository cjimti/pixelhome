"""The Stranger: the storm is still raging outside the door of Hunding's hut when the door bursts open at the free
end of Right. A gust of grey rain floods in across Right and the porch, lightning cracks over the doorway, and a
man stumbles in out of it: Siegmund, a light of Wälsung blue, streaming rain. He has run all night from his
enemies with no weapon left, and he staggers through the room toward the fire on Left in lurches, stopping to
sway, twice falling back a step, dimmer as he goes. The cellos and basses sing his motif (Donington 35), the long
held D over a bass that sinks and sinks, and each time a wave of blue rolls out from him over the house; the last
of the storm figure (74) grumbles away in the basses at the door. He passes under the great ash tree in the
middle of the porch without seeing it, though its leaves stir and the hilt in the trunk glints as he goes by.

At the hearth his weary motif (35a) sounds in the cellos. "Whoever owns this hearth, here I must rest": he
sways, flares once, and collapses beside the fire, a low dim blue lying at the middle of Left, while the hearth
glows over him, the storm keeps on faintly at the open door, and the weary motif sinks into the bassoons.

compose() holds every note, choreography() his every lurch; stage(), room() and figure() are the hut and the
people in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'WK02'
TITLE = 'The Stranger'
KIND = 'show'
DESCRIPTION = ('A stranger bursts in out of the storm, soaked and unarmed, and staggers across the house toward '
               'the fire. He passes under a great ash tree without noticing it, and collapses at the hearth.')
VOICEOVER = ('The door flies open, and a stranger falls in out of the storm. '
             'Whoever owns this fire, he says, here I must rest.')

K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_DOOR = 3.0                                # the door bursts open
T_IN = 3.6                                  # he is in the doorway
STORM_ECHO = [(0.6, 84), (9.5, 66), (19.0, 50), (31.0, 40)]
T_SM = [9.0, 31.0]                          # his motif, cellos and basses with the horns on the held D
T_WEARY = 46.0
T_ARRIVE = 50.5
T_FALL = 54.0                               # "hier muss ich rasten"
T_WEARY2 = 58.0
D = 80.0

HUT = hexc('#3a1a0a')
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
SIEGMUND = hexc('#30a8ff')
WHITE = hexc('#ffffff')

START = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.5)     # where WK01 left the hut
END = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.38)
LYING = (0.42, 26.0)                        # Siegmund at the end: level, width


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Hunding's hut as profiles over the house: the hearth on Left, the ash tree in the middle of Porch Front with
    its leaves over the porch and the sword's hilt in its trunk, the door at the free end of Right."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)       # the same fire, leaves and rain in every scene, so the cuts match
    trunk = np.exp(-((d - pf) / 16) ** 2)
    clumps = 0.55 + 0.45 * smooth_noise(rng, d, 45.0)
    return dict(
        d=d, pf=pf,
        hearth=np.exp(-((d - at(G, 'Left', 0.4)) / 125) ** 2),
        trunk=trunk,
        hilt=np.exp(-((d - pf) / 5) ** 2),
        canopy=porch * np.exp(-((d - pf) / 310) ** 2) * clumps * (1 - trunk),
        door=smoothstep(at(G, 'Right', 0.7), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.2),
        stir=Flicker(rng, G.N, 0.08, 0.35),
        rain=Flicker(rng, G.N, 4.0, 11.0),
    )


def room(S, T, lv):
    """The hut at shared time T with levels lv (bed, hearth, trunk, leaves, hilt, door)."""
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(HUT, lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(HEARTH, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(EMBER, 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAVES, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def figure(fr, S, p, col, lvl, w=18.0):
    """A person at path distance p: a body that stands in front of the room, and a soft halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.8 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.4 * lvl * np.exp(-((S['d'] - p) / (3.2 * w)) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for t0, v in STORM_ECHO:
        for t, m, vv, d in play('storm', t0, 0.28, 0, v):
            add(t, d, m, vv, 'storm')
    add(0.0, 44.0, 'D2', 62, 'trem')
    add(T_DOOR, 1.2, 'D1', 120, 'burst')
    for k, t0 in enumerate(T_SM):
        for t, m, v, d in play('siegmund', t0, BEAT, 0, 92 - 8 * k):
            add(t, d, m, v, 'siegmund', k)
    for t, m, v, d in play('siegmund_weary', T_WEARY, 0.6, 0, 86):
        add(t, d, m, v, 'weary', 0)
    add(T_FALL - 0.3, 0.6, 'F2', 100, 'fall')
    for j, m in enumerate(('D3', 'C3', 'Bb2', 'A2', 'G2', 'F2', 'E2', 'D2')):
        add(T_FALL + j * 0.16, 0.3, m, 92 - 5 * j, 'sink')
    for t, m, v, d in play('siegmund_weary', T_WEARY2, 0.85, -12, 70):
        add(t, d, m, v, 'weary', 1)
    for m in ('D3', 'F3', 'A3'):
        add(T_ARRIVE, D - T_ARRIVE, m, 58, 'warm')
    add(0.0, D, 'D1', 72, 'pedal')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def lurches():
    """When he lurches forward: [(time, share of the way)]. Twice he falls back a step."""
    rng = np.random.default_rng(35)
    ts = np.linspace(T_IN + 1.0, T_ARRIVE - 1.0, 22) + rng.uniform(-0.4, 0.4, 22)
    share = rng.uniform(0.7, 1.3, 22)
    share[[7, 15]] = -0.8
    share[[6, 14]] += 0.8
    return [(float(t), float(s)) for t, s in zip(ts, share / share.sum())]


def choreography(G):
    """Per frame: where Siegmund is, how bright and how wide."""
    F = nframes(D)
    t = np.arange(F) * DT
    door, home = G.pd.max() + 20, at(G, 'Left', 0.5)
    tgt = np.full(F, door)
    p = door
    for tl, s in lurches():
        p -= s * (door - home)
        tgt[t >= tl] = p
    tgt[t >= T_ARRIVE - 1.0] = home
    sway = 9 * np.sin(2 * np.pi * t / 1.7) * smoothstep(T_IN, T_IN + 2, t) * (1 - smoothstep(T_FALL, T_FALL + 1, t))
    pos = follow(tgt, np.full(F, 4.5)) + sway
    lvl = np.array([keys(x, [(T_IN - 0.4, 0.0), (T_IN + 0.4, 0.85), (T_ARRIVE, 0.62), (T_FALL - 0.2, 0.62),
                             (T_FALL + 0.3, 0.95), (T_FALL + 3.0, LYING[0])]) for x in t])
    wid = np.array([keys(x, [(T_FALL, 18.0), (T_FALL + 2.5, LYING[1])]) for x in t])
    return dict(t=t, pos=pos, lvl=lvl, w=wid)


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    sm = [e for e in N if e[4] == 'siegmund' and e[2] >= note('D3')]
    sm_on = np.array(sorted({e[0] for e in sm}))
    steps = [tl for tl, _ in lurches()]
    drip = Flicker(rng, G.N, 3.0, 9.0)
    jag = rng.uniform(0.25, 1.0, G.N)
    right = G.seg_of == 'Right'

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        p = C['pos'][f]
        lv = {k: keys(t, [(0, START[k]), (T_FALL, START[k]), (T_FALL + 12, END[k])]) for k in START}
        burst = smoothstep(T_DOOR - 0.1, T_DOOR + 0.3, t) * (1 - smoothstep(T_DOOR + 1.5, T_DOOR + 7, t))
        lv['door'] += 0.35 * burst
        # he stirs the leaves and wakes the hilt as he passes under the tree
        near = np.exp(-((p - pf) / 160) ** 2)
        lv['leaves'] += 0.2 * near
        lv['hilt'] += 0.4 * near
        fr = room(S, T, lv)

        # the gust through the open door: grey rain flooding in over Right and the porch
        if T_DOOR <= t < T_DOOR + 9:
            a = t - T_DOOR
            front = d.max() - 900 * (1 - np.exp(-a / 1.2))
            flood = smoothstep(front - 250, front + 50, d) * np.exp(-a / 3.0)
            fr += light(STORM, 0.7 * flood * (0.7 + 0.3 * np.clip(drip(T), 0, None)))
            fr += light(RAIN, 0.8 * flood * np.clip(drip(T) - 0.8, 0, None))
        for tb in (T_DOOR, T_DOOR + 0.35):
            a = t - tb
            if 0 <= a < 1.0:
                env = np.exp(-a / 0.05) + 0.7 * np.exp(-((a - 0.13) / 0.03) ** 2)
                fr += light(BOLT, min(1.0, env) * right * jag * smoothstep(1700, 2300, d))
                fr += light(STORM, 0.4 * min(1.0, env))

        # each phrase of his motif: a wave of blue rolls out from him over the house
        i = int(np.searchsorted(sm_on, t, side='right')) - 1
        if i >= 0 and t - sm_on[i] < 3.0:
            a = t - sm_on[i]
            r = 40 + 420 * a
            fr += light(SIEGMUND, 0.6 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 90) ** 2))
        held = sum(smoothstep(t0 + 1.0, t0 + 2.5, t) * (1 - smoothstep(t0 + 7, t0 + 9.5, t)) for t0 in T_SM)
        fr += light(SIEGMUND, 0.22 * held * np.exp(-((d - p) / 260) ** 2))

        # Siegmund, dripping rain at first; a thump of light at each lurch
        lvl = C['lvl'][f]
        j = max([s for s in steps if s <= t], default=-9)
        lurch = 0.25 * np.exp(-(t - j) / 0.25)
        fr = figure(fr, S, p, SIEGMUND, lvl * (1 + lurch), C['w'][f])
        wet = np.exp(-max(t - T_IN, 0) / 14.0) * (t > T_IN)
        fr += light(RAIN, 0.7 * wet * np.exp(-((d - p) / 60) ** 2) * np.clip(drip(T), 0, None) ** 2 / 2)
        if T_FALL - 0.2 <= t < T_FALL + 2.0:
            a = t - T_FALL + 0.2
            fr += light(WHITE, 0.35 * np.exp(-a / 0.35) * np.exp(-((d - p) / 30) ** 2))
            fr += light(SIEGMUND, 0.4 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p) - 200 * a) / 60) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_him(t):
        return pan_at(np.interp(t, C['t'], C['pos']))

    for name, gain, rev in (('low', 0.32, 0.22), ('strings', 0.26, 0.3), ('brass', 0.26, 0.32), ('perc', 0.28, 0.28),
                            ('fx', 0.12, 0.3), ('warm', 0.32, 0.35), ('harp', 0.24, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
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

    door = pan_at(at(G, 'Right', 0.92))
    hearth = pan_at(at(G, 'Left', 0.45))
    for t, d, m, v, part, k in compose():
        pa = pan_him(t)
        if part == 'storm':
            M.add('low', vc.play(m, v, dur=d * 1.2, release=0.08), t, 0.9, door)
            M.add('low', cbs.play(m - 12, v), t, 0.7, door)
        elif part == 'trem':
            hold('low', ctrem, m, t, t + d, v, door, rise=0.5, fall=5.0, gain=0.6)
        elif part == 'burst':
            M.add('perc', crash.play(v), t, 0.9, door)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, door)
            M.add('perc', roll.play(100, dur=2.5), t + 0.3, 0.7, door)
            M.add('fx', whoosh(1.2, 5000, 600, 0.7, seed=4), t - 0.1, 1.0, door)
        elif part == 'siegmund':
            if m >= note('D4'):
                hold('brass', horn, m - 12, t, t + d, v - 6, pa, rise=1.2, fall=1.5, gain=0.7)
            elif m >= note('D3'):
                hold('strings', vc, m, t, t + d, v, pa, rise=0.4, fall=1.5, gain=0.9)
            else:
                M.add('low', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pa)
                M.add('low', cb.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, pa)
        elif part == 'weary':
            s = vc if k == 0 else bsn
            if d > 3:
                hold('strings', s, m, t, t + d, v, pa, rise=0.5, fall=1.5, gain=0.7)
            else:
                M.add('strings', s.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pa)
        elif part == 'fall':
            M.add('perc', timp.play(v, pitch=-3), t, 0.8, hearth)
            M.add('low', pizz.play(m, v), t, 0.9, hearth)
        elif part == 'sink':
            M.add('strings', vc.play(m, v, dur=0.35, release=0.2), t, 0.8, hearth)
        elif part == 'warm':
            hold('warm', vc, m, t, t + d, v, hearth * 0.8, rise=6.0, fall=1.5, gain=0.6)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=4.0, fall=1.5, gain=0.7)
    for tl, _ in lurches():                 # his steps: a tired pizzicato, a muffled drum
        M.add('low', pizz.play(note('D2') if int(tl * 10) % 2 else note('A1'), 70), tl, 0.8, pan_him(tl))
        M.add('perc', timp.play(56, pitch=-8), tl, 0.4, pan_him(tl))
    t_tree = float(C['t'][np.argmin(np.abs(C['pos'] - at(G, 'Porch Front', 0.5)))])
    for i, m in enumerate(('A4', 'D5', 'F5')):
        M.add('harp', harp.play(note(m), 60 - 6 * i), t_tree + 0.25 * i, 0.9, pan_at(at(G, 'Porch Front', 0.5)))
