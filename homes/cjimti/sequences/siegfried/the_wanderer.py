"""The Wanderer: Mime alone in his cave, sulphur yellow at the anvil, tapping at a sword he knows he cannot make
whole, his obstinate little figure (Donington 51) on the bassoons. A drum roll, and the cave mouth at the free end
of Right floods deep blue: a stranger stands in it. The Wanderer's great slow chords (17) sound on the trombones and
tubas, and with every chord a wave of deep blue rolls in from the mouth over the whole house to the end of Side,
while he comes in step by step, a tall figure of Wotan's blue, to the middle of Right.

He grounds his spear: its motif (73) strides down the trombones and a pale steel shaft grows from him toward the
anvil note by note, then strikes the floor, a blue-white flash over the whole house and a shock running out both
ways that knocks the forge down to embers. Mime cowers (71), trembling. The chords come back softer as the
Wanderer settles: a blue tint stays in the walls of the cave, and the stranger stays standing on Right with Mime
shaking at the anvil, ready for the wager of heads.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF06'
TITLE = 'The Wanderer'
KIND = 'show'
DESCRIPTION = ('A stranger in a deep blue cloak walks into the dwarf\'s cave with a spear in his hand, and every step '
               'he takes washes the house in blue. He strikes the spear down and the forge cowers.')
VOICEOVER = ('A stranger in a blue cloak walks into the cave, leaning on a spear. '
             'He calls himself the Wanderer.')

K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_OBST = [1.5, 5.0]                         # Mime's obstinate figure
T_ROLL = 9.0                                # the drum roll; the mouth floods blue
T_WAND = [11.0, 26.0, 55.0]                 # the Wanderer's chords
W_BEAT = 0.55
T_IN = 11.0                                 # he starts in from the mouth
T_STAND = 24.0                              # he has reached the middle of Right
T_SPEAR = 37.0                              # the spear motif; the shaft grows note by note
S_BEAT = 0.45
T_CRINGE = [45.0, 49.0]                     # Mime cowers
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
WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
WAND_AT = 0.4                               # where the Wanderer stands, on Right

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

    for k, t0 in enumerate(T_OBST):
        for t, m, v, d in play('mime_obstinate', t0, 0.8, 0, 80 + 6 * k):
            add(t, d, m, v, 'obstinate', k)
    add(T_ROLL, 2.2, 'C1', 96, 'roll')
    for k, t0 in enumerate(T_WAND):
        for t, m, v, d in play('wanderer', t0, W_BEAT, 0, (112, 104, 84)[k]):
            add(t, d, m, v, 'wanderer', k)
    for t, m, v, d in play('spear', T_SPEAR, S_BEAT, 0, 112):
        add(t, d, m, v, 'spear')
    add(T_SPEAR + 10.0 * S_BEAT, 0.1, 'C1', 124, 'strike')
    for k, t0 in enumerate(T_CRINGE):
        for t, m, v, d in play('mime_frustrated', t0, 0.8, -12 * k, 92 - 8 * k):
            add(t, d, m, v, 'cringe', k)
    add(T_WAND[1] + 9, T_WAND[2] - T_WAND[1] - 9, 'Eb1', 58, 'pedal')
    add(T_WAND[2] + 9, D - T_WAND[2] - 9, 'E1', 54, 'pedal')
    return sorted(N, key=lambda e: e[0])


def chords():
    """When each of the Wanderer's chords lands: [(time, which statement)]."""
    return sorted({(e[0], e[5]) for e in compose() if e[4] == 'wanderer'})


def where_wanderer(G, t):
    """His path distance: in from beyond the mouth, a step on each chord of the first statement."""
    far, stand = G.pd.max() + 50, at(G, 'Right', WAND_AT)
    steps = [c for c, k in chords() if k == 0]
    pts = [(T_IN - 0.5, far)] + [(c + 0.9, far + (stand - far) * (j + 1) / len(steps)) for j, c in enumerate(steps)]
    return keys(t, pts)


def render(G, seed=6):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    ch = chords()
    spear_on = [e for e in N if e[4] == 'spear']
    t_strike = T_SPEAR + 10.0 * S_BEAT
    cringe = [e for e in N if e[4] == 'cringe']
    taps = [(e[0], 0.35, anvil) for e in N if e[4] == 'obstinate']
    p_mime = at(G, 'Porch Front', MIME_AT)
    stand = at(G, 'Right', WAND_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        cow = smoothstep(t_strike, t_strike + 0.2, t) * (1 - smoothstep(t_strike + 3, t_strike + 14, t))
        lv['forge'] -= 0.3 * cow
        lv['walls'] -= 0.25 * cow
        fr = cave(S, T, lv)
        p = where_wanderer(G, t)
        present = smoothstep(T_ROLL, T_IN, t)

        # the mouth floods deep blue at the drum roll; a blue tint settles into the walls while he is there
        gone = smoothstep(T_WAND[2] + 9, D - 1, t)
        fr += light(WOTAN, 0.85 * present * S['mouth'] * (1 - 0.4 * smoothstep(T_STAND, T_STAND + 6, t)) * (1 - gone))
        tint = smoothstep(T_STAND - 4, T_STAND + 4, t) * (1 - gone)
        fr += light(WOTAN, 0.35 * tint * (S['walls'] + 0.6 * (S['forge'] == 0) * (1 - S['mouth'])))

        # every chord: a wave of blue rolling in from the mouth over the whole house to the end of Side
        for c, k in ch:
            a = t - c
            if 0 <= a < 4.0:
                g = (1.0, 0.85, 0.6)[k]
                front = L - 750 * a
                wave = np.exp(-((d - front) / 260) ** 2) + 0.55 * (d > front) * np.exp(-a / 1.1)
                fr += light(WOTAN, g * np.exp(-a / 2.0) * wave)
                fr += light(WOTAN_SOFT, 0.6 * g * np.exp(-a / 0.25) * np.exp(-((d - p) / 60) ** 2))

        # the spear: a pale shaft growing from him toward the anvil, a step on every note, then the strike
        if T_SPEAR <= t < t_strike + 3:
            n = sum(1 for e in spear_on if e[0] <= t)
            tip = stand - min(n, 12) * 95
            shaft = (d <= stand) * (d >= tip) * (1 - smoothstep(t_strike + 0.5, t_strike + 3, t))
            j = n - 1
            hit = np.exp(-(t - spear_on[j][0]) / 0.18) if j >= 0 else 0.0
            fr += light(SPEAR, (0.6 + 0.4 * hit) * shaft)
            fr += light(WHITE, 0.8 * hit * np.exp(-((d - tip) / 10) ** 2) * (t < t_strike))
        if t_strike <= t < t_strike + 2.5:
            a = t - t_strike
            fr += light(SPEAR, min(1.0, 1.1 * np.exp(-a / 0.15)))
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - stand) - 1600 * a) / 120) ** 2))
        fr += light(SPARK, np.clip(sparks(S, taps, t, 60, n=6, reach=0.4), 0, 0.8))

        # Mime: tapping at first, then cowering and trembling when the spear comes down
        tremble = smoothstep(t_strike, t_strike + 0.5, t) * (0.12 + 0.08 * np.sin(2 * np.pi * 7 * t))
        for t0, dur, m, v, part, k in cringe:
            a = t - t0
            if 0 <= a < 0.8:
                fr += light(MIME, 0.5 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - p_mime) - 400 * a) / 40) ** 2))
        mlvl = keys(t, [(0, 0.6), (T_ROLL, 0.6), (T_ROLL + 1, 0.45), (t_strike, 0.45), (t_strike + 0.4, 0.3),
                        (D - 10, 0.5)])
        fr = figure(fr, S, p_mime + 8 * cow, MIME, mlvl + tremble * (t < D - 4))

        # the Wanderer: deep blue, tall (wide) and steady, a pale glint at the spear hand
        if t >= T_IN - 1:
            lvl = 0.8 * smoothstep(T_IN - 1, T_IN + 1, t)
            fr = figure(fr, S, p, WOTAN, lvl, 22.0)
            fr += light(SPEAR, 0.6 * lvl * np.exp(-((d - p + 24) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(min(dd, ds.max()), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.32, 0.22), ('winds', 0.28, 0.3), ('brass', 0.3, 0.32), ('perc', 0.3, 0.25),
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
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    stand = pan_at(at(G, 'Right', WAND_AT))
    mouth = pan_at(G.pd.max())
    for t, d, m, v, part, k in compose():
        wp = pan_at(where_wanderer(G, t))
        if part == 'obstinate':
            M.add('winds', bsn_st.play(m, v), t, 0.9, mime)
            M.add('mallet', xylo.play(m + 12, v - 20), t, 0.5, mime)
            M.add('perc', anvil.play(v - 35), t, 0.4, mime)
        elif part == 'roll':
            M.add('perc', roll.play(v, pitch=-5, dur=d), t, 0.7, mouth)
        elif part == 'wanderer':
            if m >= note('E4'):
                hold('brass', horn, m - 12, t, t + d, v, wp, rise=0.2, fall=0.8, gain=0.8)
            elif m >= note('A3'):
                hold('brass', tbn, m, t, t + d, v, wp, rise=0.2, fall=0.8, gain=0.75)
            elif m >= note('C3'):
                hold('brass', tbn, m, t, t + d, v - 6, wp, rise=0.2, fall=0.8, gain=0.7)
            else:
                hold('low', tuba, m + 12, t, t + d, v, wp, rise=0.2, fall=0.8, gain=0.85)
                if k == 0:
                    M.add('perc', timp.play(v - 30, pitch=(m % 12) - 6), t, 0.5, wp)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, stand)
            M.add('low', tuba.play(m, v - 6, dur=d * 1.05, release=0.3), t, 0.8, stand)
            M.add('low', cb.play(m - 12, v - 15, dur=d * 1.05, release=0.3), t, 0.6, stand)
        elif part == 'strike':
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, stand)
            M.add('perc', gong.play(110), t, 0.6, stand)
            M.add('perc', crash.play(v), t, 0.7, stand)
        elif part == 'cringe':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, mime)
            M.add('low', vc.play(m, v - 12, dur=d * 1.1, release=0.25), t, 0.6, mime)
        elif part == 'pedal':
            hold('warm', cb, m + 12, t, t + d, v, stand * 0.5, rise=3.0, fall=2.0, gain=0.6)
