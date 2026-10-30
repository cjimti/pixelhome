"""Nothung! Nothung!: Siegfried takes the anvil and Mime scuttles back down the porch to the far end of Left to
brew a sleeping draught. The trumpets name the sword (Donington 43), and with every note the shards on the anvil
flash steel white. Siegfried files them to dust: white streaks rasp back and forth across Porch Front, two strokes
a second, throwing grey-white grit.

Then the bellows: the forging motif (52) in the low brass, and with every breath of the bellows the fire surges
up the chimney walls and floods out across the whole house in orange, sparks flying to both ends. The steel melts
under his heroism (78) on the horns, the blade on the anvil glowing red, then orange, then white-hot, and the
hammer song begins: the forging motif again, faster, every low note a blow that flashes white on the anvil, sends
a shockwave and sparks to both ends of the roof. Between the blows, Mime's motif (50) bubbles in the bassoons at
the end of Left, where his poison seethes sickly green. The forge ends roaring, the blade red on the anvil.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF09'
TITLE = 'Nothung! Nothung!'
KIND = 'show'
DESCRIPTION = ('Siegfried files the broken sword to dust, works the bellows until the forge roars across the whole '
               'house, and melts and hammers the steel himself, while the dwarf brews poison in the corner.')
VOICEOVER = ('Nobody can mend the sword, so Siegfried makes it new himself. '
             'Nothung! Nothung!')

K = 8                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_MOVE = 0.5                                # Siegfried to the anvil, Mime off down the porch
T_NAME = 3.0                                # the trumpets name the sword
T_FILE = (9.5, 20.0)                        # filing the shards to dust
T_BELLOWS = [20.5, 24.0, 27.5, 31.0]        # the forging motif: one breath of the bellows per two beats
T_MELT = 35.5                               # his heroism on the horns; the steel melts
T_HAMMER = [48.5, 51.5, 54.5, 57.5, 60.5, 63.5]   # the hammer song: the forging motif, faster
T_MIME = [52.0, 58.0, 64.0]                 # Mime's motif bubbling at his poison between the blows
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
STEEL = hexc('#e8f8ff')
GRIT = hexc('#a8b0b8')
REDHOT = hexc('#ff3000')
POISON = hexc('#a0d000')

START = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)        # where SF08 left the cave
END = dict(bed=0.28, forge=0.8, walls=0.7, mouth=0.55)            # where SF10 picks it up
MIME_FROM, SIEG_FROM = 0.32, 0.7            # on Porch Front, where SF08 left them
MIME_AT = 0.7                               # Mime's place on Left, at his pot


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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'F1', 62, 'pedal')
    for t, m, v, d in play('nothung', T_NAME, BEAT, 0, 108):
        add(t, d, m, v, 'name')
    t = T_FILE[0]
    k = 0
    while t < T_FILE[1]:
        add(t, 0.4, 'C3', 80 + 3 * (k % 4), 'file', k)
        t += 0.45
        k += 1
    for k, t0 in enumerate(T_BELLOWS):
        for t, m, v, d in play('forging', t0, 0.52, 0, 96 + 6 * k):
            add(t, d, m, v, 'forging', k)
        for b in range(3):
            add(t0 + b * 1.04, 1.0, 'C1', 80 + 6 * k, 'breath', k)
    for t, m, v, d in play('siegfried_heroism', T_MELT, BEAT, 0, 112):
        add(t, d, m, v, 'melt')
    for k, t0 in enumerate(T_HAMMER):
        for t, m, v, d in play('forging', t0, 0.44, 0, 108 + 3 * k):
            add(t, d, m, v, 'hammer', k)
    for k, t0 in enumerate(T_MIME):
        for t, m, v, d in play('mime', t0, 0.32, -12, 70):
            add(t, d, m, v, 'mime', k)
    for m in ('F2', 'C3', 'F3', 'A3'):
        add(T_HAMMER[-1] + 3.5, D - T_HAMMER[-1] - 3.5, m, 74, 'blaze')
    add(T_HAMMER[-1] + 3.0, 0.1, 'C1', 124, 'last')
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """Every hammer blow and bellows breath on the anvil: [(time, strength, where)]."""
    hits = [(t, 0.9, S['anvil']) for t, _, m, v, part, k in compose() if part == 'forging' and m < note('C3')]
    hits += [(t, 1.2, S['anvil']) for t, _, m, v, part, k in compose() if part == 'hammer' and m < note('C3')]
    return sorted(hits)


def render(G, seed=9):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    N = compose()
    hits = blows(S)
    hit_t = np.array([h[0] for h in hits])
    names = np.array([e[0] for e in N if e[4] == 'name'])
    files = [e for e in N if e[4] == 'file']
    breaths = np.array([e[0] for e in N if e[4] == 'breath'])
    melt_on = np.array(sorted({e[0] for e in N if e[4] == 'melt'}))
    mimes = np.array([e[0] for e in N if e[4] == 'mime'])
    rng = np.random.default_rng(seed)
    bubble = Flicker(rng, G.N, 1.5, 4.0)
    pf = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    blade = np.exp(-((d - anvil) / 55) ** 6)
    p_pot = at(G, 'Left', MIME_AT)
    pot = np.exp(-((d - p_pot) / 60) ** 2)
    m0, s0 = at(G, 'Porch Front', MIME_FROM), at(G, 'Porch Front', SIEG_FROM)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_BELLOWS[0], START[k]), (T_MELT, END[k])]) for k in START}

        # the bellows: every breath the fire surges up the chimney and floods the house in orange
        j = int(np.searchsorted(breaths, t, side='right')) - 1
        surge = 0.0
        if j >= 0 and t - breaths[j] < 1.04:
            surge = np.sin(np.pi * (t - breaths[j]) / 1.04) ** 2 * (0.8 + 0.07 * (j // 3))
        lv['forge'] += 0.3 * surge
        lv['walls'] += 0.35 * surge
        hammering = smoothstep(T_HAMMER[0] - 1, T_HAMMER[0], t)
        fr = cave(S, T, lv)
        fr += light(FORGE, 0.85 * surge * S['spill'])
        fr += light(SPARK, 0.4 * surge * S['spill'] ** 3 * np.clip(S['lick'](T), 0, 1))
        fr += light(FORGE, 0.3 * hammering * S['spill'] * (1 - smoothstep(T_HAMMER[-1] + 4, D, t) * 0.4))

        # the sword named: the shards flash steel white with every note, a white sweep across the porch
        i = int(np.searchsorted(names, t, side='right')) - 1
        if i >= 0 and t - names[i] < 1.0 and t < T_FILE[0]:
            a = t - names[i]
            fr += light(STEEL, 0.95 * np.exp(-a / 0.2) * blade)
            fr += light(STEEL, 0.85 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - anvil) - 1400 * a) / 120) ** 2))

        # the file: white streaks rasping back and forth across Porch Front, grit thrown off
        for t0, dd, m, v, part, k in files:
            a = t - t0
            if 0 <= a < 0.6:
                u = min(1.0, a / 0.4)
                x = pf[0] + 30 + (pf[1] - pf[0] - 60) * (u if k % 2 == 0 else 1 - u)
                fr += light(STEEL, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - x) / 18) ** 2))
                fr += light(GRIT, 0.45 * np.exp(-a / 0.2) * ((d > pf[0]) & (d < pf[1])))
                fr += light(GRIT, 0.6 * np.exp(-a / 0.3) * ((d - x) * (1 if k % 2 == 0 else -1) < 0) *
                            np.exp(-np.abs(d - x) / 70))

        # the blade: red-hot, orange, white-hot while it melts and is hammered; red on the anvil at the end
        heat = keys(t, [(T_MELT, 0.0), (T_MELT + 4, 0.35), (T_MELT + 12, 1.0), (T_HAMMER[-1] + 2, 0.75),
                        (D, 0.45)])
        if heat > 0:
            col = REDHOT * (1 - heat) + HEAT * heat if heat < 0.8 else HEAT
            k = int(np.searchsorted(melt_on, t, side='right')) - 1
            flare = np.exp(-(t - melt_on[k]) / 0.3) if k >= 0 and t < T_MELT + 13 else 0.0
            fr = fr * (1 - 0.8 * min(1, heat * 3) * blade)[:, None]
            fr += light(col, (0.6 + 0.4 * heat + 0.2 * flare) * blade)
            fr += light(REDHOT, 0.5 * (heat + flare) * np.exp(-((d - anvil) / 260) ** 2))
            fr += light(FORGE, 0.75 * flare * S['spill'])

        # every blow: a white-hot flash on the anvil, a shockwave and sparks to both ends of the house
        i = int(np.searchsorted(hit_t, t, side='right')) - 1
        if i >= 0 and t - hit_t[i] < 1.2:
            a, s = t - hit_t[i], hits[i][1]
            fr += light(HEAT, min(1.0, s * np.exp(-a / 0.1)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.75 * s * np.exp(-a / 0.5) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 90) ** 2))
        fr += light(SPARK, np.clip(sparks(S, hits, t, 90, n=18), 0, 1.0))

        # Mime at his pot at the end of Left: the poison seethes sickly green, bubbling with his motif
        k = int(np.searchsorted(mimes, t, side='right')) - 1
        bub = np.exp(-(t - mimes[k]) / 0.15) if k >= 0 else 0.0
        brew = smoothstep(T_MOVE + 4, T_MOVE + 8, t)
        fr += light(POISON, brew * (0.45 + 0.2 * np.clip(bubble(T), 0, 1) + 0.45 * bub) * pot)
        u = smoothstep(T_MOVE, T_MOVE + 5, t)
        pm = m0 + u * (p_pot - m0) + 10 * bub * np.sin(2 * np.pi * 5 * t)
        fr = figure(fr, S, pm, MIME, 0.6 + 0.15 * bub)

        # Siegfried at the anvil, flaring with each blow
        ps = s0 + smoothstep(T_MOVE, T_MOVE + 3, t) * (anvil + 4 - s0)
        blow = np.exp(-(t - hit_t[i]) / 0.2) if i >= 0 else 0.0
        lvl = 0.8 * (1 + 0.3 * blow)
        fr = figure(fr, S, ps, SIEGFRIED, lvl, 18.0)
        fr += light(HEAD, lvl * np.exp(-((d - ps) / 6) ** 2))
        if T_HAMMER[-1] + 3.0 <= t < T_HAMMER[-1] + 5.0:
            a = t - T_HAMMER[-1] - 3.0
            fr += light(WHITE, 0.5 * np.exp(-a / 0.15))
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

    for name, gain, rev in (('low', 0.32, 0.22), ('strings', 0.26, 0.3), ('winds', 0.26, 0.3), ('brass', 0.3, 0.3),
                            ('perc', 0.3, 0.25), ('fx', 0.16, 0.25), ('warm', 0.26, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    guiro = M.hits('Percussion/Guiro-Hit*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
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
    pot = pan_at(at(G, 'Left', MIME_AT))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.55)
        elif part == 'name':
            if d > 1.0:
                hold('brass', tpt, m - 12, t, t + d, v, forge, rise=0.1, fall=0.8, gain=0.9)
            else:
                M.add('brass', tpt.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.95, forge)
        elif part == 'file':
            M.add('perc', guiro.play(v), t, 0.9, forge + (0.15 if k % 2 else -0.15))
            M.add('strings', vla.play(note('F3') + (k % 4 == 3) * 5, v - 15), t, 0.6, forge)
        elif part == 'breath':
            M.add('fx', whoosh(1.0, 200, 1400, 0.7, seed=90 + k), t, 0.9, forge)
        elif part in ('forging', 'hammer'):
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.2), t, 0.9, forge)
                M.add('perc', anvil.play(min(127, v + 10)), t, 1.0 if part == 'hammer' else 0.8, forge)
                M.add('perc', timp.play(v - 10, pitch=-3), t, 0.6, forge)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, forge)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, forge)
        elif part == 'melt':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, forge, rise=0.2, fall=0.8, gain=0.85)
                hold('strings', vc, m, t, t + d, v - 10, forge, rise=0.2, fall=0.8, gain=0.5)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, forge)
        elif part == 'mime':
            M.add('winds', bsn.play(m, v), t, 0.9, pot)
        elif part == 'blaze':
            hold('warm', horn if m >= note('C3') else tbn, m, t, t + d, v, forge * 0.4, rise=0.3, fall=2.0, gain=0.5)
        elif part == 'last':
            M.add('perc', crash.play(v), t, 1.0, forge)
            M.add('perc', anvil.play(v), t, 1.0, forge)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, forge)
