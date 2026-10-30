"""Three Riddles: the Wanderer, deep blue on Right, wagers his head that he can answer any three questions Mime
puts to him, and Mime, yellow at the anvil, asks. Who lives in the depths of the earth? The Nibelungs: the whole
house drops into the red dark of Nibelheim in a wipe out from the Wanderer, and anvils ring in their dotted
rhythm all over it, every blow a red flash and a spray of red sparks on a different part of the roofline, while
the Ring (Donington 8) groans under it in the bassoons and tubas.

Who lives on the face of the earth? The giants: a wipe to stone and ochre, and their motif (58) stamps in on the
tubas and timpani, every stamp lighting one whole run of the house as a block of stone in turn. Who lives on the
cloudy heights? The gods: a wipe to sky blue, and Valhalla (63) rises in the brass while gold climbs from both
ends of the house to the castle in the middle of Porch Front; the spear (73) strikes, a blue-white flash.

Now the Wanderer asks. Who will forge Nothung anew? The sword's motif (43) sounds on a quiet trumpet, Mime
flickers in panic, and the Wanderer's blue swells over the whole house until the answer crashes out on the full
brass: one who has never known fear. Mime's head is forfeit to him. The Wanderer goes, a blue sweep out through
the cave mouth, and Mime is left shaking at the anvil.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF07'
TITLE = 'Three Riddles'
KIND = 'show'
DESCRIPTION = ('A wager of heads: the dwarf asks the stranger three riddles, and the house becomes the dark '
               'Nibelung forges, the giants\' land and the gods\' castle in turn. Then the stranger asks the one '
               'question the dwarf cannot answer.')
VOICEOVER = ('Three riddles, and the loser forfeits his head. '
             'The Wanderer answers them all, and then asks his own.')

K = 6                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_OPEN = 0.5                                # a phrase of the Wanderer's chords: the wager
R = [(5.0, 19.0), (21.0, 36.0), (38.0, 54.0)]   # the three riddles: Nibelungs, giants, gods
NIB_BEAT = 0.42
T_NIB_RING = 6.0
T_GIANTS = [22.0, 29.0]
G_BEAT = 0.55
T_VALHALLA = [39.0, 45.5]
V_BEAT = 0.8
T_STRIKE_SP = 52.0                          # the spear's first steps, then a strike
T_Q = 56.0                                  # who will forge Nothung anew?
T_ANSWER = 63.5                             # one who has never known fear
T_LEAVE = 67.0                              # he goes out through the cave mouth
T_GONE = 72.0
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
DEPTHS = hexc('#5a0800')
RED = hexc('#ff1000')
STONE = hexc('#6a5a48')
OCHRE = hexc('#c88a20')
SKY = hexc('#2050ff')
VALHALLA = hexc('#ffb000')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
WAND_AT = 0.4                               # where the Wanderer stands, on Right
RUNS = ['Left', 'Right', 'Porch Left', 'Porch Right', 'Side', 'Porch Front']    # the giants' stamping order

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

    for t, m, v, d in play('wanderer', T_OPEN, 0.5, 0, 88):
        if t < T_OPEN + 4.0:
            add(t, min(d, T_OPEN + 4.0 - t), m, v, 'wanderer', 0)
    # the Nibelungs: anvils in their dotted rhythm, the Ring underneath
    b, j = R[0][0] + 0.3, 0
    while b < R[0][1] - 1.0:
        for o in (0, 0.75, 1.0, 1.5):
            add(b + o * NIB_BEAT * 2, 0.1, 'C5', 96 + 20 * (o == 0), 'nib', j)
            j += 1
        b += 4 * NIB_BEAT
    for t, m, v, d in play('ring', T_NIB_RING, 0.95, -17, 100):
        add(t, d, m, v, 'ring')
    add(R[0][0], 0.1, 'C1', 110, 'wipe', 0)
    # the giants
    add(R[1][0], 0.1, 'C1', 110, 'wipe', 1)
    for k, t0 in enumerate(T_GIANTS):
        for t, m, v, d in play('giants', t0, G_BEAT, -12, 108 + 8 * k):
            add(t, d, m, v, 'giants', k)
    # the gods
    add(R[2][0], 0.1, 'C1', 110, 'wipe', 2)
    for k, t0 in enumerate(T_VALHALLA):
        for t, m, v, d in play('valhalla', t0, V_BEAT, -12, 100 + 10 * k):
            add(t, d, m, v, 'valhalla', k)
    for t, m, v, d in play('spear', T_STRIKE_SP, 0.4, 0, 112):
        if t < T_STRIKE_SP + 1.2:
            add(t, d * 0.8, m, v, 'spear')
    add(T_STRIKE_SP + 1.25, 0.1, 'C1', 120, 'strike')
    # the question, and the answer
    for t, m, v, d in play('nothung', T_Q, 0.55, -12, 76):
        add(t, d, m, v, 'nothung')
    for t, m, v, d in play('wanderer', T_ANSWER, 0.5, 0, 120):
        if t < T_ANSWER + 2.0:
            add(t, min(d, T_ANSWER + 3.0 - t), m, v, 'wanderer', 1)
    add(T_ANSWER, 0.1, 'C1', 125, 'answer')
    for t, m, v, d in play('wanderer', T_LEAVE + 0.5, 0.5, 0, 74):
        if t < T_LEAVE + 4.5:
            add(t, min(d, T_LEAVE + 4.5 - t), m, v, 'wanderer', 2)
    for k in range(3):
        for t, m, v, d in play('mime_frustrated', T_GONE + 1.0 + 2.2 * k, 0.6, -12 * (k % 2), 92 - 8 * k):
            add(t, d, m, v, 'shake', k)
    add(T_Q, T_ANSWER - T_Q, 'Gb1', 66, 'trem')
    return sorted(N, key=lambda e: e[0])


def where_wanderer(G, t):
    """His path distance: standing on Right, then out through the cave mouth."""
    return keys(t, [(T_LEAVE, at(G, 'Right', WAND_AT)), (T_GONE, G.pd.max() + 60)])


def riddle_weight(i, t):
    """How far the house has turned into riddle i's world, 0..1, before the wipe's spread."""
    t0, t1 = R[i]
    return smoothstep(t0, t0 + 0.2, t) * (1 - smoothstep(t1 - 0.5, t1 + 1.0, t))


def render(G, seed=7):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    seg = G.seg_of
    N = compose()
    stand = at(G, 'Right', WAND_AT)
    p_mime = at(G, 'Porch Front', MIME_AT)
    rng = np.random.default_rng(seed)
    nib = [e for e in N if e[4] == 'nib']
    nib_at = rng.uniform(at(G, 'Side', 0.1), L - 60, len(nib))
    nib_hits = [(e[0], 0.75 + 0.25 * (e[3] > 110), p) for e, p in zip(nib, nib_at)]
    stomps = [e for e in N if e[4] == 'giants' and e[1] >= 0.5 * G_BEAT and e[2] == max(
        x[2] for x in N if x[4] == 'giants' and x[0] == e[0])]
    vh = sorted({e[0] for e in N if e[4] == 'valhalla'})
    t_strike = T_STRIKE_SP + 1.25
    shakes = [e for e in N if e[4] == 'shake']
    mid = at(G, 'Porch Front', 0.5)
    half = max(mid - d.min(), L - mid)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = cave(S, T, dict(LV))
        p = where_wanderer(G, t)

        # the three worlds, each wiping out from the Wanderer over the whole house
        worlds = []
        for i in range(3):
            w = riddle_weight(i, t)
            if w <= 0:
                continue
            spread = smoothstep(0, 1, (1700 * (t - R[i][0]) - np.abs(d - stand)) / 150) if t < R[i][0] + 2 else 1.0
            worlds.append((i, w * spread))
        for i, w in worlds:
            if i == 0:
                world = light(DEPTHS, 0.75 * S['rock'] * (0.85 + 0.15 * S['fire'](T)))
                for th, s, p0 in nib_hits:
                    a = t - th
                    if 0 <= a < 0.6:
                        world += light(RED, min(1.0, 1.2 * s * np.exp(-a / 0.15)) * np.exp(-((d - p0) / 90) ** 2))
                        if s > 0.9:
                            run = seg == seg[np.argmin(np.abs(d - p0))]
                            world += light(RED, 0.75 * np.exp(-a / 0.3) * run)
                world += light(RED, np.clip(sparks(S, [h for h in nib_hits if 0 <= t - h[0] < 1.6], t, 71,
                                                   n=8, reach=0.5), 0, 1.0))
            elif i == 1:
                world = light(STONE, 0.3 * S['rock']) + light(OCHRE, 0.12)
                for j, e in enumerate(stomps):
                    a = t - e[0]
                    if 0 <= a < 1.6:
                        block = seg == RUNS[j % len(RUNS)]
                        world += light(OCHRE, min(1.0, 0.55 + 0.6 * np.exp(-a / 0.25)) * block * np.exp(-a / 1.2))
                        world += light(STONE, 0.35 * np.exp(-a / 0.1))
            else:
                n = sum(1 for c in vh if c <= t)
                c = vh[n - 1] if n else t
                height = min(1.0, n / len(vh) * 1.15)
                rise = (1 - np.abs(d - mid) / half) > 1 - height
                world = light(SKY, 0.5 * (0.9 + 0.1 * S['leaf'](T)) * (1 - rise))
                world += light(VALHALLA, (0.6 + 0.35 * np.exp(-(t - c) / 0.3)) * rise)
                world += light(WHITE, 0.4 * np.exp(-(t - c) / 0.15) * np.exp(-((d - mid) / 25) ** 2) * (n > 0))
            w = (w * np.ones_like(d))[:, None]
            fr = fr * (1 - 0.9 * w) + world * w

        # the spear strikes after Valhalla
        if t_strike <= t < t_strike + 1.5:
            a = t - t_strike
            fr += light(SPEAR, min(1.0, np.exp(-a / 0.15)))
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - stand) - 1600 * a) / 120) ** 2))

        # the question: his blue swells over the house; the answer crashes out
        q = smoothstep(T_Q, T_ANSWER, t) * (1 - smoothstep(T_ANSWER + 0.5, T_LEAVE + 3, t))
        fr += light(WOTAN, 0.85 * q * np.exp(-np.abs(d - p) / (200 + 1400 * q)))
        if T_ANSWER <= t < T_ANSWER + 2.5:
            a = t - T_ANSWER
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12))
            fr += light(WOTAN, np.exp(-a / 0.9) * np.exp(-((np.abs(d - p) - 1800 * a) / 200) ** 2))

        # his going: a blue sweep out through the cave mouth
        if T_LEAVE <= t < T_GONE + 3:
            trail = smoothstep(p - 700, p, d) * (d <= p + 20) * (1 - smoothstep(T_GONE, T_GONE + 3, t))
            fr += light(WOTAN, 0.7 * trail)
        if T_GONE <= t < T_GONE + 2:
            fr += light(WOTAN_SOFT, 0.8 * np.exp(-(t - T_GONE) / 0.4) * S['mouth'])

        # Mime: asking, then flickering in panic, then shaking alone
        panic = smoothstep(T_Q, T_Q + 2, t)
        flick = panic * (0.25 * np.sin(2 * np.pi * 9 * t) + 0.12 * np.sin(2 * np.pi * 13.7 * t))
        for t0, dur, m, v, part, k in shakes:
            a = t - t0
            if 0 <= a < 0.8:
                fr += light(MIME, 0.55 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - p_mime) - 450 * a) / 45) ** 2))
        mlvl = keys(t, [(0, 0.6), (T_Q, 0.6), (T_ANSWER, 0.45), (T_ANSWER + 0.3, 0.3), (T_GONE, 0.5), (D, 0.55)])
        fr = figure(fr, S, p_mime + 5 * np.sin(2 * np.pi * 6 * t) * panic, MIME, mlvl + flick * (t < D - 3))

        # the Wanderer, flaring on the answers
        if t < T_GONE + 0.5:
            lvl = 0.8 + 0.2 * sum(riddle_weight(i, t) for i in range(3)) + 0.2 * q
            fr = figure(fr, S, p, WOTAN, lvl, 22.0)
            fr += light(SPEAR, 0.6 * lvl * np.exp(-((d - p + 24) / 5) ** 2))
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

    for name, gain, rev in (('low', 0.32, 0.22), ('winds', 0.28, 0.3), ('brass', 0.3, 0.32), ('perc', 0.3, 0.25),
                            ('mallet', 0.2, 0.3), ('fx', 0.12, 0.3), ('harp', 0.22, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
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

    rng = np.random.default_rng(7)
    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    mouth = pan_at(G.pd.max())
    for t, d, m, v, part, k in compose():
        wp = pan_at(where_wanderer(G, t))
        if part == 'wanderer':
            if m >= note('E4'):
                hold('brass', horn, m - 12, t, t + d, v, wp, rise=0.15, fall=0.8, gain=0.8)
            elif m >= note('C3'):
                hold('brass', tbn, m, t, t + d, v, wp, rise=0.15, fall=0.8, gain=0.72)
            else:
                hold('low', tuba, m + 12, t, t + d, v, wp, rise=0.15, fall=0.8, gain=0.85)
        elif part == 'nib':
            M.add('perc', anvil.play(v), t, 0.75, float(rng.uniform(-0.8, 0.8)))
        elif part == 'ring':
            M.add('winds', bsn.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.85, 0.0)
            M.add('low', tuba.play(m, v - 8, dur=d * 1.05, release=0.3), t, 0.8, 0.0)
        elif part == 'wipe':
            M.add('fx', whoosh(1.4, (900, 400, 300)[k], (300, 2500, 5000)[k], 0.7, seed=k), t - 0.2, 1.0, wp)
            M.add('perc', timp.play(v, pitch=-4 - 2 * k), t, 0.7, wp)
            if k == 2:
                for i, mm in enumerate(('C4', 'E4', 'G4', 'C5', 'E5')):
                    M.add('harp', harp.play(note(mm), 80), t + 0.07 * i, 0.8, wp)
        elif part == 'giants':
            if d >= 0.5 * G_BEAT:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.25), t, 0.95)
                M.add('perc', timp.play(v - 10, pitch=(m % 12) - 7), t, 0.7)
            else:
                M.add('brass', tbn.play(m, v - 20, dur=d * 1.1, release=0.15), t, 0.6)
        elif part == 'valhalla':
            if m >= note('Ab3'):
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.2, fall=0.8, gain=0.75)
            elif m >= note('C3'):
                hold('brass', tbn, m, t, t + d, v - 8, 0.0, rise=0.2, fall=0.8, gain=0.65)
            else:
                hold('low', tuba, m, t, t + d, v, 0.0, rise=0.2, fall=0.8, gain=0.8)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, wp)
            M.add('low', tuba.play(m, v - 6, dur=d * 1.05, release=0.25), t, 0.8, wp)
        elif part == 'strike':
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, wp)
            M.add('perc', crash.play(v - 10), t, 0.6, wp)
        elif part == 'nothung':
            if m >= note('C4'):
                M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.3), t, 0.75, 0.0)
            else:
                M.add('low', vc.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.7, 0.0)
        elif part == 'trem':
            hold('low', ctrem, m + 12, t, t + d, v, mime, rise=3.0, fall=0.5, gain=0.6)
        elif part == 'answer':
            M.add('perc', crash.play(v), t, 0.9, wp)
            M.add('perc', gong.play(115), t, 0.6, wp)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, wp)
        elif part == 'shake':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, mime)
            M.add('low', vc.play(m, v - 12, dur=d * 1.1, release=0.25), t, 0.6, mime)
    M.add('fx', whoosh(T_GONE - T_LEAVE, 500, 2500, 0.5, seed=9), T_LEAVE, 1.0, (pan_at(at(G, 'Right', WAND_AT))
                                                                              + mouth) / 2)
