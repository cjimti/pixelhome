"""The Pieces of Nothung: in Mime's cave, Siegfried, emerald with a white-hot head, waits on the right of the anvil
and Mime crouches on its left. Mime brings out what is left of the sword his mother kept: the trumpet gives
Nothung's motif (Donington 43) and with every note one of seven white steel shards flashes on the anvil, the whole
porch cracking white with it, the gold hilt glinting in the middle. Siegfried seizes on it: the Sword (45) rings out
on the trumpet twice, and each time a white streak of steel races from the anvil to both ends of the house.

"Mend it for me today!" His audacity (55) strides down the horns, and each note is an emerald burst rolling out
from him over the roofline, the forge leaping with it. Then his freedom motif (56) cries out high: he bolts down
Porch Right and along Right and out of the cave mouth, an emerald comet pulling a green flood of forest light
behind it across the whole house. The flood drains away, and Mime is left alone at the anvil with the shards,
whining (his lament, 72) and grumbling (71), the steel fading into the forge glow.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF05'
TITLE = 'The Pieces of Nothung'
KIND = 'show'
DESCRIPTION = ('The dwarf shows the boy the shattered pieces of his father\'s sword. Siegfried orders it mended by '
               'nightfall and storms out of the cave into the forest.')
VOICEOVER = ('Here are the pieces of your father\'s sword. '
             'Mend it, says Siegfried, and he is gone into the forest.')

K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_SHARDS = [3.0, 11.0]                      # Nothung's motif on the trumpet: a shard flashes on every note
T_SWORD = [19.5, 25.5]                      # the Sword: steel races from the anvil to both ends
T_AUDACITY = 32.0                           # "Mend it for me today!"
T_FREE = [46.0, 50.0]                       # his freedom motif; he bolts on the second
T_RUN = 50.0
T_OUT = 55.5                                # he is out of the cave mouth
T_LAMENT = 60.0
T_GRUMBLE = 70.0
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
HILT = hexc('#ffcc40')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
SIEG_AT = 0.7
SHARDS = [-70, -44, -20, 4, 26, 50, 76]     # the seven pieces, path distance from the anvil

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

    add(0.0, T_RUN, 'F1', 60, 'pedal')
    for k, t0 in enumerate(T_SHARDS):
        for t, m, v, d in play('nothung', t0, 0.62, -12, 96 + 10 * k):
            add(t, d, m, v, 'nothung', k)
    for k, t0 in enumerate(T_SWORD):
        for t, m, v, d in play('sword', t0, 0.62, 0, 108 + 8 * k):
            add(t, d, m, v, 'sword', k)
    for t, m, v, d in play('siegfried_audacity', T_AUDACITY, 0.85, 0, 112):
        add(t, d, m, v, 'audacity')
    for k, t0 in enumerate(T_FREE):
        for t, m, v, d in play('siegfried_freedom', t0, 0.5, -12, 112 + 8 * k):
            add(t, d, m, v, 'freedom', k)
    add(T_RUN, 0.1, 'C1', 118, 'dash')
    add(T_OUT, 0.1, 'C1', 110, 'out')
    for t, m, v, d in play('mime_lament', T_LAMENT, 0.75, 0, 84):
        add(t, d, m, v, 'lament')
    for k in range(2):
        for t, m, v, d in play('mime_frustrated', T_GRUMBLE + 3.5 * k, 0.8, -12 * k, 92 - 10 * k):
            add(t, d, m, v, 'grumble', k)
    for m in ('F2', 'Ab2', 'C3'):
        add(T_LAMENT, D - T_LAMENT, m, 52, 'glow')
    return sorted(N, key=lambda e: e[0])


def where_siegfried(G, t):
    """Siegfried's path distance at time t: by the anvil, then out along Porch Right and Right."""
    return keys(t, [(T_RUN, at(G, 'Porch Front', SIEG_AT)), (T_RUN + 1.5, at(G, 'Porch Right', 0.6)),
                    (T_OUT, G.pd.max() + 60)])


def render(G, seed=5):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    shard_on = [e for e in N if e[4] == 'nothung' and e[2] >= note('C4')]
    sword_on = np.array(sorted({e[0] for e in N if e[4] == 'sword'}))
    burst = [e for e in N if e[4] == 'audacity']
    free_on = np.array(sorted({e[0] for e in N if e[4] == 'freedom'}))
    p_mime = at(G, 'Porch Front', MIME_AT)
    lament = [e for e in N if e[4] in ('lament', 'grumble')]
    hits = [(e[0], 0.8, anvil + SHARDS[j % 7]) for j, e in enumerate(shard_on)]
    hits += [(e[0], 0.7, where_siegfried(G, e[0])) for e in burst]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        p = where_siegfried(G, t)
        aud = smoothstep(T_AUDACITY - 0.5, T_AUDACITY + 1, t) * (1 - smoothstep(T_FREE[0], T_RUN, t))
        lv['forge'] += 0.3 * aud
        lv['walls'] += 0.3 * aud
        fr = cave(S, T, lv)

        # the shards: seven pieces of white steel on the anvil, each flashing on its note, the porch cracking white
        shown = smoothstep(T_SHARDS[0] - 1.5, T_SHARDS[0], t) * (1 - smoothstep(T_LAMENT + 6, D - 2, t))
        for j, sx in enumerate(SHARDS):
            fr += light(STEEL, 0.4 * shown * np.exp(-((d - anvil - sx) / 6) ** 2))
        fr += light(HILT, 0.7 * shown * np.exp(-((d - anvil - 4) / 5) ** 2))
        for j, (t0, dur, m, v, part, k) in enumerate(shard_on):
            a = t - t0
            if 0 <= a < 1.2:
                sx = SHARDS[j % 7]
                fr += light(STEEL, min(1.0, 1.2 * np.exp(-a / 0.3)) * np.exp(-((d - anvil - sx) / 12) ** 2))
                fr += light(STEEL, np.exp(-a / 0.14) * (S['forge'] > 0) + 0.7 * np.exp(-a / 0.22) * S['walls'])

        # the Sword: a white streak of steel from the anvil out to both ends of the house on every note
        i = int(np.searchsorted(sword_on, t, side='right')) - 1
        if i >= 0 and t - sword_on[i] < 1.4:
            a = t - sword_on[i]
            r = 1900 * a
            fr += light(STEEL, np.exp(-a / 0.6) * np.exp(-((np.abs(d - anvil) - r) / 90) ** 2))
            fr += light(STEEL, 0.45 * np.exp(-a / 0.35) * (np.abs(d - anvil) < r))
            fr += light(WHITE, 0.4 * np.exp(-a / 0.08) * S['heat'] ** 0.4)

        # his audacity: an emerald burst rolling out from him on every note
        for t0, dur, m, v, part, k in burst:
            a = t - t0
            if 0 <= a < 1.5:
                r = 60 + 1300 * a
                ring = np.exp(-((np.abs(d - p) - r) / 150) ** 2) + 0.45 * (np.abs(d - p) < r)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.55) * ring)
        fr += light(SIEGFRIED, 0.3 * aud)
        fr += light(SPARK, np.clip(sparks(S, hits, t, 55, n=10), 0, 1.0))

        # the run: an emerald comet out of the cave mouth with a flood of forest green behind it
        if T_RUN - 0.2 <= t < T_OUT + 9:
            a = t - T_RUN
            behind = smoothstep(p - 900, p - 50, d) * (d < p + 30) if t < T_OUT else 1.0
            flood = 0.75 * behind * smoothstep(-0.2, 0.4, a) * (1 - smoothstep(T_OUT + 1, T_OUT + 8, t))
            fr += light(FOREST, flood * (0.8 + 0.2 * S['leaf'](T)))
            fr += light(SIEGFRIED, 0.5 * flood * np.exp(-((d - p) / 260) ** 2))
        j = int(np.searchsorted(free_on, t, side='right')) - 1
        if j >= 0 and t - free_on[j] < 0.8 and t < T_OUT:
            a = t - free_on[j]
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 0.25) * np.exp(-((d - p) / 140) ** 2))
        if T_OUT <= t < T_OUT + 2.5:
            a = t - T_OUT
            fr += light(FOREST, 0.9 * np.exp(-a / 0.5) * S['mouth'])
            fr += light(WHITE, 0.5 * np.exp(-a / 0.15) * S['mouth'] ** 3)

        for t0, dur, m, v, part, k in lament:
            a = t - t0
            if 0 <= a < 1.2:
                r = 40 + 700 * a
                fr += light(MIME, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - r) / 60) ** 2))

        # Mime at the anvil, shrinking when the boy roars, whining alone after
        lam = smoothstep(T_LAMENT - 1, T_LAMENT, t)
        mlvl = keys(t, [(0, 0.6), (T_AUDACITY, 0.6), (T_AUDACITY + 1, 0.38), (T_OUT, 0.38), (T_LAMENT, 0.75),
                        (D - 4, 0.6)])
        wob = 0.15 * lam * np.sin(2 * np.pi * 1.3 * t) * (t < D - 4)
        fr = figure(fr, S, p_mime, MIME, mlvl + wob)

        # Siegfried: emerald, a white-hot head on the side he faces
        if t < T_OUT + 0.3:
            lvl = 0.8 + 0.2 * aud
            fr = figure(fr, S, p, SIEGFRIED, lvl, 18.0)
            ahead = 8 if t >= T_RUN else 0
            fr += light(HEAD, lvl * np.exp(-((d - p - ahead) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(min(dd, ds.max()), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.32, 0.22), ('winds', 0.28, 0.3), ('brass', 0.3, 0.3), ('perc', 0.3, 0.25),
                            ('mallet', 0.2, 0.3), ('warm', 0.26, 0.35), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
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
    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    mouth = pan_at(G.pd.max())
    for t, d, m, v, part, k in compose():
        sp = pan_at(where_siegfried(G, t))
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.6)
        elif part == 'nothung':
            if m >= note('C4'):
                if d > 1.0:
                    hold('brass', tpt, m, t, t + d, v, forge, rise=0.1, fall=0.6, gain=0.85)
                else:
                    M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, forge)
                M.add('mallet', glock.play(m + 12, v - 20), t, 0.6, forge)
                M.add('perc', anvil.play(v - 20), t, 0.5, forge)
            else:
                M.add('low', tbn.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.8, forge)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.3), t, 0.95)
            M.add('brass', horn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6)
            if d > 0.6:
                M.add('perc', crash.play(v - 30), t, 0.4)
        elif part == 'audacity':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sp, rise=0.08, fall=0.6, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.25), t, 0.95, sp)
            M.add('low', vc.play(m - 12, v - 10, dur=d * 1.05, release=0.25), t, 0.7, sp)
            M.add('perc', timp.play(v - 25, pitch=(m % 12) - 6), t, 0.4, sp)
        elif part == 'freedom':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, sp)
            M.add('winds', vln.play(m + 12, v - 15, dur=d * 1.05, release=0.3), t, 0.6, sp)
        elif part == 'dash':
            M.add('perc', timp.play(v, pitch=-3), t, 0.8, sp)
            M.add('fx', whoosh(T_OUT - T_RUN, 300, 4000, 0.8, seed=6), t, 1.0, (sp + mouth) / 2)
        elif part == 'out':
            M.add('perc', crash.play(v), t, 0.7, mouth)
        elif part == 'lament':
            M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.25), t, 0.85, mime)
            M.add('winds', bsn.play(m - 12, v - 15, dur=d * 1.1, release=0.25), t, 0.6, mime)
        elif part == 'grumble':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, mime)
            M.add('low', vc.play(m, v - 12, dur=d * 1.1, release=0.25), t, 0.6, mime)
        elif part == 'glow':
            hold('warm', vc, m, t, t + d, v, forge * 0.5, rise=4.0, fall=1.5, gain=0.5)
