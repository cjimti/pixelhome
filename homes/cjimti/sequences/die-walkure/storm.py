"""Storm: the prelude to Die Walküre, a storm in D minor. Out of near darkness the violins' tremolo D starts to
hiss like rain and the cellos and basses take up the storm motif (Donington 74), the five-note run that rears up
and the plodding steps down and back: each statement is a gust that tears along the roofline from the free end
of Right to the back of Side, its steps pulsing in the cloud, over and over, louder each time and climbing to F
and G before it falls back to D. Rain flies along every run in wind-driven drops; lightning forks crawl along one
run after another and the thunder answers late and then sooner; the horns call out the first leap of Donner's
call to the thunder twice. At the height of it the trombones and tubas hurl Wotan's spear motif (73) down
through the storm: a pale line of light shoots out from the middle of the porch to both ends of the house, one
note at a time, over a wash of Wotan's blue, and two great flashes light the whole house.

Then the storm passes. The gusts weaken, the rain draws back across the house toward the door at the free end
of Right, and inside Hunding's hut is lit for the first time: a spark in the hearth on Left catches and glows,
the great ash tree takes shape in the middle of Porch Front, its trunk and then its leaves spreading over the
porch, and for a moment the gold hilt of a sword buried in the trunk glints. At the end the storm is only
outside the door, and the room waits for someone to come in out of it.

compose() holds every note; stage() and room() are the hut, shared word for word by Act I's first scenes, on a
clock that runs on from scene to scene; render() and score() read the same timings."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, MOTIFS

CODE = 'WK01'
TITLE = 'Storm'
KIND = 'show'
DESCRIPTION = ('Die Walküre begins in a storm. Rain lashes the house, lightning crawls along the roof, and the '
               "low strings drive the storm on until Wotan's spear cuts through it; then it passes, and a fire "
               'glows in a hut built round a great ash tree.')
VOICEOVER = ('Die Walküre. A storm in the forest, and a man running from it, with nothing left but his life. '
             'Somewhere ahead there is a fire.')

K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.28                                 # a quarter note of the storm figure
STATE = 12 * BEAT                           # one statement of it, run and steps
STORMS = [(1.5 + STATE * i, tr, 58 + 5 * i) for i, tr in enumerate([0, 0, 0, 0, 0, 0, 3, 3, 5, 5, 0, 0, 0, 0])]
SUBSIDE = [(50.0, 0, 88), (55.0, 0, 72), (60.5, 0, 60), (67.0, 0, 48)]
DONNER = [(18.0, ('Porch Left', 0.5)), (27.4, ('Right', 0.35))]
T_SPEAR = 38.0                              # Wotan's spear motif in the trombones and tubas
SPEAR_BEAT = 0.34
T_CLIMAX = 42.6
BOLTS = [(6.2, 'Right', 0.7, 0), (10.4, 'Porch Left', 0.4, 0), (14.6, 'Left', 0.3, 0), (19.8, 'Porch Front', 0.6, 0),
         (23.1, 'Right', 0.3, 0), (26.6, 'Side', 0.6, 0), (29.9, 'Porch Right', 0.5, 0), (33.0, 'Left', 0.7, 0),
         (35.6, 'Porch Front', 0.3, 0), (T_CLIMAX, 'Porch Front', 0.5, 1), (46.0, 'Left', 0.5, 1),
         (49.2, 'Right', 0.55, 0), (53.4, 'Right', 0.8, 0), (59.0, 'Right', 0.92, 0)]
T_HUT = 50.0                                # the hut begins to appear
D = 80.0

HUT = hexc('#3a1a0a')                       # the room, warm and dark
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
GLOW = hexc('#7080ff')                      # the fork's afterimage
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
WHITE = hexc('#ffffff')

# the hut at the end, as WK02 begins: perceptual levels of each part of room()
END = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.5)


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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). k is the statement, the bolt, or the call."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.4, 66.0, 'D4', 70, 'trem')
    add(14.0, 36.0, 'D5', 72, 'trem')
    add(0.0, 77.0, 'D1', 80, 'pedal')
    for i, (t0, tr, v) in enumerate(STORMS + SUBSIDE):
        for t, m, vv, d in play('storm', t0, BEAT, tr, min(v, 124)):
            add(t, d, m, vv, 'storm', i)
    for k, (t0, _) in enumerate(DONNER):
        notes = MOTIFS['donner']['notes']
        for b, d, m in notes[:2] + notes[4:]:
            add(t0 + b * 0.3, d * 0.3, note(m) + 4, 104 + 8 * k, 'donner', k)
    for t, m, v, d in play('spear', T_SPEAR, SPEAR_BEAT, 0, 120):
        add(t, d, m, v, 'spear')
    for i, (t, seg, u, big) in enumerate(BOLTS):
        near = 1.0 if big else (0.5 if t < 50 else 0.2)
        add(t, 0.3, 'D1', 90 + 34 * near, 'bolt', i)
        add(t + 0.25 + 1.2 * (1 - near), 1.6 + 1.4 * near, 'D1', 70 + 50 * near, 'thunder', i)
    add(30.0, 4.0, 'D1', 90, 'roll')
    add(T_CLIMAX - 3.0, 3.0, 'D1', 116, 'roll')
    for m in ('D3', 'F3', 'A3'):                 # inside: a dim warm chord as the hearth catches
        add(T_HUT + 6.0, D - T_HUT - 6.0, m, 62, 'warm')
    add(T_HUT + 4.0, D - T_HUT - 4.0, 'D2', 64, 'warm')
    add(T_HUT + 18.0, 0.8, 'A4', 50, 'glint')
    add(T_HUT + 18.5, 1.6, 'D5', 46, 'glint')
    return sorted(N, key=lambda e: e[0])


def gust_pos(S, t0, t):
    """Where a statement's gust front is: from the free end of Right to the back of Side."""
    return S['d'].max() + 150 - (S['d'].max() + 300) * (t - t0) / STATE


def storm_level(t):
    return keys(t, [(0, 0.05), (4, 0.35), (20, 0.7), (36, 0.9), (46, 1.0), (52, 0.65), (62, 0.25), (72, 0.0)])


def retreat(S, t):
    """After the climax the storm draws back toward the door."""
    edge = keys(t, [(47, -600.0), (74, 2420.0)])
    return smoothstep(edge - 350, edge + 80, S['d'])


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    order = G.path
    ds = d[order]
    N = compose()
    storm_on = [np.array([e[0] for e in N if e[4] == 'storm' and e[5] == i]) for i in range(len(STORMS + SUBSIDE))]
    spear = [e for e in N if e[4] == 'spear']
    bolt_fx = []
    for t, seg, u, big in BOLTS:
        mask = (G.seg_of == seg) | (big and np.ones(G.N, bool))
        bolt_fx.append(dict(t=t, c=at(G, seg, u), mask=mask, big=big, jag=rng.uniform(0.25, 1.0, G.N),
                            half=0.5 * (G.pd[G.seg[seg]].max() - G.pd[G.seg[seg]].min())))
    drops = dict(p=np.zeros(0), v=np.zeros(0), age=np.zeros(0), life=np.ones(0), b=np.zeros(0))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sl = storm_level(t)
        rm = retreat(S, t)
        lv = {k: keys(t, pts) for k, pts in (
            ('bed', [(T_HUT, 0.0), (T_HUT + 16, END['bed'])]),
            ('hearth', [(T_HUT, 0.0), (T_HUT + 1.5, 0.25), (T_HUT + 6, 0.3), (T_HUT + 16, END['hearth'])]),
            ('trunk', [(T_HUT + 4, 0.0), (T_HUT + 14, END['trunk'])]),
            ('leaves', [(T_HUT + 7, 0.0), (T_HUT + 18, END['leaves'])]),
            ('hilt', [(T_HUT + 17.5, 0.0), (T_HUT + 18.2, 1.0), (T_HUT + 22, END['hilt'])]),
            ('door', [(T_HUT + 2, 0.0), (T_HUT + 18, END['door'])]))}
        fr = room(S, T, lv)

        # the storm cloud, rolling with the wind toward the back of Side
        cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 820 + 0.13 * T))
        cloud2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.31 * T) + 1.3)
        fr += light(STORM, sl * rm * (0.07 + 0.22 * cloud * (0.4 + 0.6 * cloud2)))

        # the gusts: one per statement, its steps pulsing as it tears along the house
        for i, (t0, tr, v) in enumerate(STORMS + SUBSIDE):
            if not t0 <= t < t0 + STATE + 0.6:
                continue
            on = storm_on[i]
            j = int(np.searchsorted(on, t, side='right')) - 1
            pulse = 0.65 + 0.35 * np.exp(-(t - on[j]) / 0.12)
            p = gust_pos(S, t0, t)
            band = np.exp(-((d - p) / 240) ** 2) + 0.5 * smoothstep(p, p + 600, d) * smoothstep(p + 1200, p + 600, d)
            amp = min(v, 124) / 124 * (1 - smoothstep(t0 + STATE, t0 + STATE + 0.6, t))
            fr += light(STORM, 0.85 * amp * pulse * band * np.maximum(rm, 0.25 * (t < 47)))
            fr += light(RAIN, 0.45 * amp * pulse * np.exp(-((d - p) / 60) ** 2) * rm)

        # rain: wind-driven drops flying along every run
        n_new = rng.poisson(160 * sl * DT * (1 + 0.6 * (t > 30)))
        if n_new:
            p = rng.uniform(0, d.max(), n_new)
            keep = rng.uniform(size=n_new) < np.interp(p, ds, rm[order])
            p = p[keep]
            k = len(p)
            drops = {key: np.concatenate([drops[key], val]) for key, val in (
                ('p', p), ('v', -rng.uniform(250, 520, k)), ('age', np.zeros(k)), ('life', rng.uniform(0.2, 0.55, k)),
                ('b', rng.uniform(0.45, 0.95, k)))}
        drops['age'] += DT
        drops['p'] += drops['v'] * DT
        alive = (drops['age'] < drops['life']) & (drops['p'] > 0)
        drops = {key: val[alive] for key, val in drops.items()}
        if len(drops['p']):
            idx = order[np.clip(np.searchsorted(ds, drops['p']), 0, G.N - 1)]
            b = np.zeros(G.N)
            np.maximum.at(b, idx, drops['b'] * (1 - drops['age'] / drops['life']))
            fr = fr * (1 - 0.5 * b[:, None]) + light(RAIN, b)

        # the spear motif: a pale line shoots out from the middle of the porch, one note at a time
        if T_SPEAR - 0.2 <= t < T_SPEAR + 6.5:
            j = max([i for i, e in enumerate(spear) if e[0] <= t], default=-1)
            wash = smoothstep(T_SPEAR - 0.2, T_SPEAR + 0.4, t) * (1 - smoothstep(T_SPEAR + 4.5, T_SPEAR + 6.5, t))
            fr += light(WOTAN, 0.42 * wash * np.exp(-((d - pf) / 700) ** 2))
            if j >= 0:
                tj = spear[j][0]
                r = 90 + 115 * j + 115 * smoothstep(tj, tj + 0.18, t)
                u = np.abs(d - pf)
                line = smoothstep(r + 10, r - 30, u) * (0.55 + 0.45 * np.exp(-((u - r) / 40) ** 2))
                hit = 0.55 + 0.45 * np.exp(-(t - tj) / 0.2)
                fr += light(SPEAR, 0.85 * hit * wash * line)

        # lightning: a fork crawls along a run and flickers; the near ones light the whole house a little
        for bf in bolt_fx:
            a = t - bf['t']
            if not 0 <= a < 1.4:
                continue
            env = np.exp(-a / 0.05) + 0.8 * np.exp(-((a - 0.14) / 0.03) ** 2) + 0.5 * np.exp(-((a - 0.27) / 0.04) ** 2)
            reach = (bf['half'] * 1.1 + (1500 if bf['big'] else 0)) * smoothstep(0, 0.08, a)
            fork = bf['mask'] * smoothstep(reach, reach - 60, np.abs(d - bf['c'])) * bf['jag']
            far = 0.5 if bf['t'] >= 50 else 1.0
            fr += light(BOLT, min(1.0, env) * fork * far)
            fr += light(STORM, 0.45 * min(1.0, env) * far * (0.6 + 0.4 * rm))
            fr += light(GLOW, 0.5 * far * np.exp(-a / 0.4) * smoothstep(0.05, 0.15, a) * fork)
            if bf['big'] and a < 0.18:
                fr += light(WHITE, 0.85 * np.exp(-a / 0.07))
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

    for name, gain, rev in (('low', 0.22, 0.22), ('strings', 0.15, 0.3), ('brass', 0.2, 0.3), ('perc', 0.24, 0.28),
                            ('fx', 0.11, 0.3), ('warm', 0.2, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crash1_mp*.wav')

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

    S = {'d': G.pd}                         # gust_pos() wants the stage's path distances only
    door = pan_at(at(G, 'Right', 0.92))
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('strings', vtrem, m, t, t + d, v, -0.15 if m < 70 else 0.15, rise=10.0, fall=6.0, gain=0.7)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=6.0, fall=3.0, gain=0.7)
        elif part == 'storm':
            t0 = (STORMS + SUBSIDE)[k][0]
            late = k >= len(STORMS)
            pa = pan_at(gust_pos(S, t0, t)) if not late else door
            M.add('low', vc.play(m, v, dur=d * 1.2, release=0.08), t, 0.9, pa)
            M.add('low', cbs.play(m - 12, v), t, 0.8, pa)
            if v > 90:
                M.add('low', vcs.play(m + 12, v - 16), t, 0.4, pa)
        elif part == 'donner':
            pa = pan_at(at(G, *DONNER[k][1]))
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pa)
            M.add('brass', horn.play(m - 12, v - 12, dur=d * 1.05, release=0.5), t, 0.6, pa)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, -0.25)
            M.add('brass', tbn.play(m + 12, v - 8, dur=d * 1.05, release=0.3), t, 0.6, 0.25)
            M.add('brass', tuba.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.9, 0.0)
        elif part == 'bolt':
            bt, seg, u, big = BOLTS[k]
            pa = 0.0 if big else pan_at(at(G, seg, u))
            g = 1.0 if big else (0.65 if t < 50 else 0.3)
            M.add('perc', (crash if big or t < 50 else crash_s).play(min(127, v)), t, 0.8 * g, pa)
            M.add('fx', whoosh(0.5, 6000, 900, 0.6, seed=k + 3), t - 0.05, 0.8 * g, pa)
            if big:
                M.add('perc', bd.play(124), t, 1.0, 0.0)
                M.add('perc', timp.play(124, pitch=-5), t, 1.0, 0.0)
        elif part == 'thunder':
            bt, seg, u, big = BOLTS[k]
            pa = 0.0 if big else pan_at(at(G, seg, u))
            M.add('perc', roll.play(min(127, v), dur=d), t, 0.8 if t < 50 else 0.45, pa)
            M.add('perc', timp.play(min(127, v), pitch=-7), t, 0.6, pa)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.8, 0.0)
        elif part == 'warm':
            s = vc if m >= note('D3') else bsn
            hold('warm', s, m, t, t + d, v, pan_at(at(G, 'Left', 0.4)) * 0.8, rise=5.0, fall=1.5, gain=0.7)
        elif part == 'glint':
            M.add('warm', harp.play(m, v), t, 0.8, pan_at(at(G, 'Porch Front', 0.5)))
    hold('low', ctrem, note('D2'), 58.0, D, 60, door, rise=4.0, fall=1.5, gain=0.5)
