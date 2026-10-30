"""Prelude: Mime's cave in the forest, in the dark. The forge is the porch, the anvil the middle of Porch Front,
the chimney walls Porch Left and Porch Right; the rest of the house is the rock of the cave, and the free end of
Right its mouth, where the forest shows green. A timpani roll on a low B flat and two bassoons in thirds brood
over the Ring as an undercurrent (Donington 8a): gold glints chase round the porch, the hoard Mime dreams of.

Then Mime's smithing motif (50) starts on the anvil, and every note of it is a hammer blow: a white-hot flash on
the anvil and a spray of sparks flying out both ways along the roofline. Four phrases, each louder; the chimney
walls blaze, and the forging motif (52) comes up in the low brass with the whole porch roaring orange. At the top
the Ring (8) sounds in full on the horns and a gold wave sweeps the whole house from end to end and back. Then
Mime, sulphur yellow at the anvil, throws down his hammer (Mime frustrated, 71): the sparks die, the forge sinks
to a glow and he crouches by it, while a green light waits at the cave mouth for the next scene.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF01'
TITLE = 'Prelude'
KIND = 'show'
DESCRIPTION = ('Deep in a forest cave a dwarf smith dreams of a golden Ring. His hammer starts on the anvil, sparks '
               'fly along the whole roof, and the forge roars until he throws the hammer down.')
VOICEOVER = ('In a cave in the forest, a dwarf hammers at his forge, and dreams of a golden ring. '
             'This is Siegfried.')

K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_ROLL = 0.5
T_UNDER = [3.0, 13.0]                       # the Ring as an undercurrent, bassoons in thirds
T_MIME = [23.0, 28.5, 34.0, 39.5]           # Mime's smithing motif, four phrases, each louder
T_FORGE = [45.0, 49.0]                      # the forging motif in the low brass
T_RING = 54.0                               # the Ring in full on the horns, the gold wave
T_THROW = 66.0                              # he throws the hammer down
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

START = dict(bed=0.24, forge=0.32, walls=0.25, mouth=0.4)
END = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # where SF02 picks the cave up
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil


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

    add(T_ROLL, 21.0, 'Bb1', 70, 'roll')
    add(0.0, D, 'Bb0', 64, 'pedal')
    for k, t0 in enumerate(T_UNDER):
        for t, m, v, d in play('ring_under', t0, 0.9, 3, 74 + 6 * k):
            add(t, d, m, v, 'under', k)
    for k, t0 in enumerate(T_MIME):
        for t, m, v, d in play('mime', t0, BEAT, -12, 78 + 12 * k):
            add(t, d, m, v, 'mime', k)
    for k, t0 in enumerate(T_FORGE):
        for t, m, v, d in play('forging', t0, BEAT, 0, 100 + 10 * k):
            add(t, d, m, v, 'forging', k)
    for t, m, v, d in play('ring', T_RING, 0.62, -5, 118):
        add(t, d, m, v, 'ring')
    add(T_RING, 0.1, 'C1', 125, 'crash')
    add(T_THROW, 0.1, 'C1', 120, 'throw')
    for t, m, v, d in play('mime_frustrated', T_THROW + 0.6, 0.7, 0, 96):
        add(t, d, m, v, 'grumble', 0)
    for t, m, v, d in play('mime_frustrated', T_THROW + 4.0, 0.9, -12, 80):
        add(t, d, m, v, 'grumble', 1)
    for m in ('Bb2', 'Db3', 'F3'):
        add(T_THROW + 6.0, D - T_THROW - 6.0, m, 56, 'glow')
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """Every hammer blow on the anvil: [(time, strength, where)]."""
    hits = [(t, 0.6 + 0.12 * k, S['anvil']) for t, _, m, v, part, k in compose() if part == 'mime']
    hits += [(t, 1.0, S['anvil']) for t, _, m, v, part, k in compose() if part == 'forging' and m < note('C3')]
    return sorted(hits)


def render(G, seed=1):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    N = compose()
    hits = blows(S)
    L = d.max()
    hit_t = np.array([h[0] for h in hits])
    under = [e for e in N if e[4] == 'under']
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Left', 0.1), L - 40, len(under))
    p_mime = at(G, 'Porch Front', MIME_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        build = smoothstep(T_MIME[0], T_FORGE[0], t) * (1 - smoothstep(T_THROW, T_THROW + 6, t))
        roar = smoothstep(T_FORGE[0] - 1, T_FORGE[0] + 1, t) * (1 - smoothstep(T_THROW, T_THROW + 4, t))
        lv = {k: keys(t, [(0, START[k]), (T_THROW + 2, START[k] + (END[k] - START[k]) * 0.5),
                          (T_THROW + 10, END[k])]) for k in START}
        lv['forge'] += 0.35 * build + 0.35 * roar
        lv['walls'] += 0.3 * build + 0.45 * roar
        fr = cave(S, T, lv)

        # the hoard he dreams of: gold glints chasing round the porch with each note of the undercurrent
        for j, (t0, dur, m, v, part, k) in enumerate(under):
            a = t - t0
            if 0 <= a < dur + 1.5:
                p = glint_at[j]
                g = 0.9 * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.06, a)
                fr += light(GOLD, g * np.exp(-((d - p) / (30 + 40 * a)) ** 2))
                fr += light(HEAT, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - p) / 10) ** 2))

        # each hammer blow: a white-hot flash on the anvil, a flare of the forge, and sparks both ways
        i = int(np.searchsorted(hit_t, t, side='right')) - 1
        if i >= 0 and t - hit_t[i] < 1.0:
            a, s = t - hit_t[i], hits[i][1]
            fr += light(HEAT, min(1.0, 1.1 * s * np.exp(-a / 0.09)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.45 * s * np.exp(-a / 0.25) * (S['forge'] + S['walls']))
            fr += light(FORGE, 0.7 * s * np.exp(-a / 0.45) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 70) ** 2))
        fr += light(SPARK, np.clip(sparks(S, hits, t, 50), 0, 1.0))

        # the Ring in full: a gold wave sweeps the whole house out to both ends and back, one surge per note
        if T_RING <= t < T_THROW:
            a = t - T_RING
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.35) if j >= 0 else 0.0
            front = (a / 3.2) % 2
            front = front if front < 1 else 2 - front
            dist = np.abs(d - anvil) / max(anvil, L - anvil)
            wave = np.exp(-((dist - front) / 0.12) ** 2)
            wave = np.exp(-((dist - front) / 0.16) ** 2) + 0.35 * (dist < front)
            fr += light(GOLD, (1.0 * wave + 0.35 * pulse * (1 - dist)) * (1 - smoothstep(T_THROW - 1.5, T_THROW, t)))
        if T_RING <= t < T_RING + 0.6:
            fr += light(WHITE, 0.55 * np.exp(-(t - T_RING) / 0.12))

        # Mime at the anvil, from the first blow; he slumps when he throws the hammer down
        if t >= T_MIME[0] - 2:
            lvl = keys(t, [(T_MIME[0] - 2, 0.0), (T_MIME[0] - 0.5, 0.75), (T_THROW, 0.85), (T_THROW + 1.0, 0.5)])
            col = MIME if t < T_THROW + 2 else MIME * 0.8 + MIME_DIM * 0.2
            bob = 6 * np.exp(-(t - hit_t[i]) / 0.15) if i >= 0 and t < T_THROW else 0.0
            fr = figure(fr, S, p_mime - bob, col, lvl)
        if T_THROW <= t < T_THROW + 1.5:
            a = t - T_THROW
            fr += light(HEAT, 0.9 * np.exp(-a / 0.12) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - anvil) - 500 * a) / 50) ** 2))
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

    for name, gain, rev in (('low', 0.32, 0.22), ('winds', 0.28, 0.3), ('brass', 0.3, 0.3), ('perc', 0.3, 0.25),
                            ('mallet', 0.2, 0.3), ('warm', 0.26, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    bsn_st = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
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
    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    for t, d, m, v, part, k in compose():
        if part == 'roll':
            r = 0.0
            while r < d:
                M.add('perc', roll.play(v, pitch=-4, dur=3.2), t + r, 0.6, forge)
                r += 3.0
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=6.0, fall=2.0, gain=0.6)
        elif part == 'under':
            if d > 1.2:
                hold('winds', bsn, m, t, t + d, v, forge * 0.6, rise=0.3, fall=0.8, gain=0.8)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, forge * 0.6)
        elif part == 'mime':
            M.add('perc', anvil.play(v), t, 0.8, forge)
            M.add('mallet', xylo.play(m + 12, v - 10), t, 0.7, mime)
            M.add('winds', bsn_st.play(m, v - 6), t, 0.8, mime)
        elif part == 'forging':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.2), t, 0.9, forge)
                M.add('perc', anvil.play(min(127, v + 10)), t, 0.9, forge)
                M.add('perc', timp.play(v, pitch=-3), t, 0.7, forge)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, forge)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, forge)
        elif part == 'ring':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.15, fall=1.0, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95)
            M.add('low', tbn.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9)
        elif part == 'throw':
            M.add('perc', anvil.play(v), t, 1.0, forge)
            M.add('perc', timp.play(v, pitch=-7), t, 0.8, forge)
            M.add('perc', crash.play(90), t + 0.05, 0.5, forge)
        elif part == 'grumble':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, mime)
            M.add('low', vc.play(m, v - 12, dur=d * 1.1, release=0.25), t, 0.6, mime)
        elif part == 'glow':
            hold('warm', vc, m, t, t + d, v, forge * 0.5, rise=4.0, fall=1.5, gain=0.55)
