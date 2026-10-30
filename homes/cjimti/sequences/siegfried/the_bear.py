"""The Bear: Mime is tapping at the anvil, sulphur yellow beside the forge, when a horn call (Donington 48) rings
out of the forest: the cave mouth at the free end of Right flares green and the whole of Right flashes emerald
with each note. Then Siegfried bursts in, electric emerald with a white-hot head, driving a bear on a rope: a
great brown-black mass that rolls in along Right ahead of him and goes straight for Mime.

Mime flees round the forge (Porch Left, across the anvil to Porch Right, out onto Left and back) with the bear
lunging after him; every lunge is a roar in the tubas and the run under the bear flashes red-brown. Siegfried's
audacity (55) bustles along in horns and violins, and each of its notes throws an emerald shockwave out from him
to both ends of the house. He laughs at Mime ("Hoho!", stopped horns, the house rippling green), then sends the
bear back out the way it came. His horn call sounds again in full, his strength (53) blazes in emerald sweeps end
to end, and the cave settles with Siegfried at the anvil's right hand and Mime cowering at its left.

compose() holds every note, choreography() every chase; stage(), cave(), figure() and sparks() are the cave,
shared word for word by Act I's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF02'
TITLE = 'The Bear'
KIND = 'show'
DESCRIPTION = ('A horn rings out of the forest and young Siegfried storms in driving a bear, which chases the dwarf '
               'round and round the forge until Siegfried laughs and sends it back to the woods.')
VOICEOVER = ('A horn in the forest, and here comes Siegfried, with a bear on a rope. '
             'Poor Mime runs for his life.')

K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_SMITH = [1.0, 5.5]                        # Mime tapping at the anvil
T_HORN = 10.5                               # the horn call from the forest
T_IN = 14.0                                 # Siegfried and the bear burst in
T_AUD = [17.0, 25.0, 33.0]                  # Siegfried's audacity
T_HO = 41.5                                 # he laughs
T_OUT = 46.0                                # the bear sent back to the woods
T_HORN2 = 53.0                              # the horn call in full
T_STR = [57.0, 61.0]                        # his strength
T_REST = 66.0
D = 80.0

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BEAR = hexc('#a04a10')
BEAR_HOT = hexc('#c83010')
EYE = hexc('#ff6000')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # the cave at every Act I cut
MIME_AT, HERO_AT = 0.32, 0.7                                       # their places on Porch Front at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
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


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: an emerald figure with a white-hot head."""
    fr = figure(fr, S, p, SIEGFRIED, lvl, w)
    return fr + light(HEAD, 0.9 * lvl * np.exp(-((S['d'] - p) / 5) ** 2))


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        v += (rate * rate * (target[f] - x[f - 1]) - 2 * rate * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def marks(G):
    """Named places as path distances."""
    return {
        'off': float(G.pd.max() + 90), 'R6': at(G, 'Right', 0.6), 'R2': at(G, 'Right', 0.2),
        'PR8': at(G, 'Porch Right', 0.8), 'PR5': at(G, 'Porch Right', 0.5), 'PR3': at(G, 'Porch Right', 0.3),
        'PF2': at(G, 'Porch Front', 0.2), 'PF5': at(G, 'Porch Front', 0.5), 'PF6': at(G, 'Porch Front', 0.6),
        'mime': at(G, 'Porch Front', MIME_AT), 'hero': at(G, 'Porch Front', HERO_AT),
        'PL7': at(G, 'Porch Left', 0.7), 'PL4': at(G, 'Porch Left', 0.4), 'PL2': at(G, 'Porch Left', 0.2),
        'L8': at(G, 'Left', 0.8), 'L5': at(G, 'Left', 0.5),
    }


LUNGES = [19.5, 23.0, 27.0, 30.5, 34.5, 38.0]                      # the bear's roars


def choreography(G):
    """Per frame: where Mime, the bear and Siegfried are."""
    m = marks(G)
    F = nframes(D)
    t = np.arange(F) * DT

    def track(pts):
        tgt = np.empty(F)
        for i, x in enumerate(t):
            tgt[i] = [m[k] for tk, k in pts if tk <= x][-1]
        return tgt

    mime = track([(0, 'mime'), (18.5, 'PL7'), (22.0, 'PL2'), (26.0, 'PR3'), (29.5, 'PR8'), (33.5, 'L8'),
                  (37.0, 'L5'), (40.0, 'mime')])
    bear = track([(0, 'off'), (T_IN, 'PF6'), (LUNGES[0], 'PL7'), (LUNGES[1], 'PL2'), (LUNGES[2], 'PR3'),
                  (LUNGES[3], 'PR8'), (LUNGES[4], 'L8'), (LUNGES[5], 'PL4'), (40.5, 'PF5'), (T_OUT, 'off')])
    sieg = track([(0, 'off'), (T_IN + 0.8, 'R6'), (20.0, 'R2'), (28.0, 'PR5'), (36.0, 'PR3'), (T_OUT - 0.5, 'PR8'),
                  (T_OUT + 2.5, 'R2'), (T_HORN2 - 2, 'hero')])
    return dict(t=t, mime=follow(mime, 5.0) + 3 * np.sin(2 * np.pi * 7 * t) * ((t > 18) & (t < 41)),
                bear=follow(bear, 3.6), sieg=follow(sieg, 3.0))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_SMITH):
        for t, m, v, d in play('mime', t0, BEAT, -12, 58 + 6 * k):
            add(t, d, m, v, 'smith', k)
    add(0.0, T_HORN, 'F1', 50, 'pedal')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.42, 0, 104):
        add(t, d, m, v, 'horn', 0)
    add(T_IN, 0.1, 'C1', 124, 'burst')
    for k, t0 in enumerate(T_AUD):
        for t, m, v, d in play('siegfried_audacity', t0, 0.5, 0, 96 + 6 * k):
            add(t, d, m, v, 'aud', k)
            add(t, d, m - 24, v - 16, 'aud_bass', k)
    for k, t0 in enumerate(LUNGES):
        add(t0, 1.0, 'D1', 110, 'roar', k)
    for j in range(12):                     # "Hoho!": stopped horns laughing
        add(T_HO + j * 0.3, 0.2, ('G4', 'D5')[j % 2], 100 - 2 * j, 'laugh')
    add(T_OUT, 0.1, 'C1', 120, 'out')
    for t, m, v, d in play('siegfried_horn', T_HORN2, 0.5, 0, 118):
        add(t, d, m, v, 'horn', 1)
    for k, t0 in enumerate(T_STR):
        for t, m, v, d in play('siegfried', t0, 0.9, -12, 112):
            add(t, d, m, v, 'strength', k)
    for m in ('G2', 'D3', 'G3', 'B3'):
        add(T_REST, D - T_REST, m, 66, 'glow')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=2):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    C = choreography(G)
    N = compose()
    smith = [(t, 0.4, anvil) for t, _, m, v, part, k in N if part == 'smith']
    smith_t = np.array([h[0] for h in smith])
    horn = [e for e in N if e[4] == 'horn']
    aud_on = np.array(sorted({e[0] for e in N if e[4] == 'aud'}))
    str_on = np.array(sorted({e[0] for e in N if e[4] == 'strength'}))
    seg = G.seg_of
    right = seg == 'Right'
    jag = np.random.default_rng(seed).uniform(0.3, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        pm, pb, ps = C['mime'][f], C['bear'][f], C['sieg'][f]
        lv = dict(LV)
        lv['mouth'] += 0.4 * smoothstep(T_HORN - 0.3, T_HORN + 0.5, t) * (1 - smoothstep(T_IN + 1, T_IN + 6, t))
        fr = cave(S, T, lv)

        # Mime tapping at the anvil
        i = int(np.searchsorted(smith_t, t, side='right')) - 1
        if i >= 0 and t - smith_t[i] < 0.8:
            fr += light(HEAT, 0.7 * np.exp(-(t - smith_t[i]) / 0.08) * S['heat'] ** 0.5)
        fr += light(SPARK, np.clip(sparks(S, smith, t, 20, n=8, reach=0.6), 0, 1))

        # the horn call from the forest: every note flashes all of Right emerald, brightest at the mouth
        for t0, dur, m, v, part, k in horn:
            a = t - t0
            if 0 <= a < dur + 0.6:
                s = 0.95 * np.exp(-a / (dur + 0.25)) * (1.0 if k == 0 else 0.7)
                if k == 0:
                    fr += light(SIEGFRIED, 1.1 * s * right * (0.6 + 0.4 * S['mouth']))
                    fr += light(HEAD, 0.6 * np.exp(-a / 0.1) * S['mouth'])
                else:
                    fr += light(SIEGFRIED, s * np.exp(-((d - ps) / 380) ** 2))

        # the bear bursts in: a gust of green through the mouth, then the brown-black mass
        if T_IN <= t < T_IN + 1.5:
            a = t - T_IN
            fr += light(SIEGFRIED, 0.8 * np.exp(-a / 0.3) * np.exp(-((d - (L - 700 * a)) / 120) ** 2))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12) * right * jag)
            fr += light(SIEGFRIED, 0.5 * np.exp(-a / 0.4))
        if pb < L + 40:
            roar = max([np.exp(-(t - r) / 0.5) for r in LUNGES if r <= t], default=0.0)
            w = 55 * (1 + 0.4 * roar)
            body = np.exp(-((d - pb) / w) ** 6)
            rim = np.exp(-((np.abs(d - pb) - w) / 12) ** 2)
            fr = fr * (1 - body)[:, None]   # a black mass with a bristling brown rim
            fr += light(BEAR, (0.9 + 0.1 * np.sin(2 * np.pi * 2.2 * t)) * rim)
            fr += light(BEAR_HOT, roar * (0.6 * body + rim))
            if roar > 0.05:                 # the run under the bear flashes red-brown
                fr += light(BEAR_HOT, 0.8 * roar * (seg == seg[np.argmin(np.abs(d - pb))]))
            for e in (-9, 9):
                fr += light(EYE, 1.0 * np.exp(-((d - pb - e - 20) / 4) ** 2))

        # Siegfried's audacity: an emerald shockwave out from him at every note
        j = int(np.searchsorted(aud_on, t, side='right')) - 1
        if j >= 0 and t - aud_on[j] < 1.2:
            a = t - aud_on[j]
            fr += light(SIEGFRIED, 1.0 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - ps) - 1400 * a) / 110) ** 2))
            fr += light(SIEGFRIED, 0.5 * np.exp(-a / 0.2) * np.exp(-((d - ps) / 150) ** 2))

        # "Hoho!": the whole house ripples green
        if T_HO <= t < T_OUT:
            a = t - T_HO
            fr += light(SIEGFRIED, 0.55 * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 240 - a * 3.3))) ** 3)

        # the bear sent out: a whoosh of green chasing it to the free end
        if T_OUT <= t < T_OUT + 3:
            a = t - T_OUT
            fr += light(SIEGFRIED, 0.7 * np.exp(-a / 1.0) * smoothstep(pb - 300, pb, d) * (d < pb + 60))

        # his strength: emerald sweeps end to end and back
        k = int(np.searchsorted(str_on, t, side='right')) - 1
        if T_STR[0] <= t < T_REST + 2 and k >= 0:
            a = t - T_STR[0]
            front = (a / 2.4) % 2
            front = (front if front < 1 else 2 - front) * L
            fade = 1 - smoothstep(T_REST - 0.5, T_REST + 2, t)
            fr += light(SIEGFRIED, fade * (0.95 * np.exp(-((d - front) / 90) ** 2) + 0.3 * (d < front)))
            fr += light(HEAD, fade * 0.6 * np.exp(-(t - str_on[k]) / 0.12) * np.exp(-((d - front) / 40) ** 2))

        mlvl = keys(t, [(0, 0.5), (14, 0.6), (18, 0.85), (40, 0.85), (41.5, 0.35), (T_HORN2, 0.35), (D - 8, 0.6)])
        fr = figure(fr, S, pm, MIME, mlvl)
        if ps < L + 40:
            slvl = keys(t, [(T_IN, 0.9), (T_REST, 0.9), (D - 6, 0.8)])
            fr = hero(fr, S, ps, slvl)
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

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('low', 0.4, 0.22), ('winds', 0.32, 0.3), ('brass', 0.38, 0.3), ('strings', 0.34, 0.3),
                            ('perc', 0.36, 0.25), ('mallet', 0.22, 0.3), ('fx', 0.15, 0.3), ('warm', 0.34, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tuba_st = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
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

    forge = pan_at(at(G, 'Porch Front', 0.5))
    mouth = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        if part == 'smith':
            M.add('perc', anvil.play(v), t, 0.6, forge)
            M.add('mallet', xylo.play(m + 12, v - 10), t, 0.6, forge)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.5)
        elif part == 'horn':
            pa = mouth if k == 0 else pan_of('sieg', t)
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v, pa, rise=0.08, fall=0.6, gain=0.95)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.15), t, 0.95, pa)
        elif part == 'burst':
            M.add('perc', crash.play(v), t, 0.9, mouth)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, mouth)
            M.add('fx', whoosh(1.4, 4000, 500, 0.8, seed=2), t - 0.2, 1.0, mouth)
        elif part == 'aud':
            pa = pan_of('sieg', t)
            M.add('strings', vln.play(m + 12, v, dur=d, release=0.1), t, 0.8, pa)
            M.add('brass', horn_st.play(m, v - 6), t, 0.7, pa)
        elif part == 'aud_bass':
            M.add('low', tuba_st.play(m, v), t, 0.6, pan_of('sieg', t))
        elif part == 'roar':
            pa = pan_of('bear', t)
            for mm in (m, m + 1, m + 6):
                M.add('low', tuba.play(mm + 12, v, dur=0.9, release=0.3), t, 0.7, pa)
            M.add('low', bsn.play(m + 12, v, dur=0.8, release=0.3), t, 0.6, pa)
            M.add('perc', timp.play(v, pitch=-6), t, 0.8, pa)
            M.add('perc', roll.play(90, dur=0.9), t, 0.5, pa)
        elif part == 'laugh':
            M.add('brass', mute.play(m, v, dur=d, release=0.08), t, 0.9, pan_of('sieg', t))
        elif part == 'out':
            pa = pan_of('bear', t)
            M.add('fx', whoosh(2.2, 600, 5000, 0.8, seed=5), t, 1.0, mouth)
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, pa)
            M.add('perc', crash.play(100), t + 1.5, 0.5, mouth)
        elif part == 'strength':
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.08, fall=0.5, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.15), t, 0.9)
            M.add('strings', vln.play(m + 12, v - 10, dur=d, release=0.1), t, 0.6)
            if k == 0 and abs(t - T_STR[0]) < 0.01:
                M.add('perc', crash.play(110), t, 0.7)
        elif part == 'glow':
            hold('warm', vc if m < note('C3') else horn, m, t, t + d, v, pan_at(at(G, 'Porch Front', HERO_AT)) * 0.5,
                 rise=2.5, fall=2.0, gain=0.55)
