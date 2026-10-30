"""The Serpent: Alberich (red, the ring a gold point with a red glint) stands by his glowing hoard in the middle
of Porch Front, Wotan (blue) and Loge (fire) on Porch Left. Loge slides up to him, sly and admiring, to his
ambivalent figure (Donington 21a) on violins and harp: that helmet, can it really do all that? Alberich laughs
and shows him. The Tarnhelm motif (18) sounds on muted horns, its violet-grey shimmer swirls round him, and he
dissolves into it.

Out of the porch rises a giant serpent, the biggest thing on the house so far: a green-black body, scaled, with
coils of bright green rolling down it, that stretches from the middle of the porch out over Porch Right and all
of Right, while its head rears at Loge. Its music is a coiling, rising chromatic line, three steps up and one
back, in the tubas, a low bassoon and the double basses. Its jaws open and snap shut, a burst of green-white and
a brass stab with every bite; the head lashes along Porch Left and out over Left, the tail whips at the end of
Right, and at its height the whole body heaves and the serpent roars with a gong and the full brass, three bites
flashing the whole house green. Loge plays the coward: his flame shrinks to a flicker and backs away from every
bite, cowering near the corner of Left. Wotan stands his ground, blue, even when the coils pass over him.

Then the Tarnhelm's chords again and the serpent shrinks back down its own length into Alberich, who stands red
by his gold again and laughs: bassoon and trombone, "ha, ha, ha", his light jumping with each one. Loge drifts
back to Porch Front and wonders aloud, to his flicker (20a) and his sly figure, whether the helmet could make
him small as well. It ends as it began, quieter: Alberich and the ring by the hoard, Wotan on Porch Left, Loge on
Porch Front, the caverns glowing red-orange with dim forge sparks and a faint stir of the Nibelung rhythm.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG16'
TITLE = 'The Serpent'
KIND = 'show'
DESCRIPTION = ('Loge asks Alberich to show what his helmet can do, and Alberich turns himself into a giant '
               'serpent that coils over the whole house, snapping its jaws. Loge pretends to be terrified, and '
               'then, very innocently, asks whether it could make him small as well.')
VOICEOVER = ('Loge has a question for Alberich, and he asks it very politely. '
             'Alberich is only too happy to show off.')

NB = 0.6                                    # a dotted quarter of the Nibelung 9/8
RHY = (0.0, 0.5, 2 / 3)
TB = 0.4                                    # a quarter note of the Tarnhelm motif
T_ASK = 0.8                                 # Loge asks
T_BOAST = 5.4                               # Alberich: you'll see
T_TARN = 9.0                                # the Tarnhelm
T_EMERGE = 20.4                             # the serpent rises
COILS = [20.4, 26.8, 33.2]                  # its coiling line, three times, each higher
SNAPS = [25.4, 27.9, 30.4, 32.6, 35.0, 37.4, 39.6, 42.2, 44.6, 46.8]
BIG = [42.2, 44.6, 46.8]                    # the bites that flash the whole house
T_ROAR = 47.6
T_SHRINK = 49.0
T_BACK = 54.8                               # Alberich again
LAUGHS = [56.4, 58.6, 60.8]
T_WONDER = 65.0                             # Loge: could it make you small?
T_STIR = 74.6
D = 80.0
HEAP = 0.8876                               # the hoard as RG15 left it

EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
SPARK = hexc('#ff7a10')
HOT = hexc('#fff0a0')
GOLD = hexc('#ffaa00')
GLINT = hexc('#ffd860')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
TARN = hexc('#5a4a8a')
TARN_HI = hexc('#9a88d0')
SCALE = hexc('#063010')
COIL = hexc('#10b02a')
SHEEN = hexc('#90ff60')
JAW = hexc('#d0ff80')
EYE = hexc('#f0ff20')
WOTAN = hexc('#1a3cff')
LOGE_A = hexc('#ff5000')
LOGE_B = hexc('#ffb020')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def coil_line(start):
    """The serpent's line: three semitones up, one back, rising (in quarter beats)."""
    m, out = note(start), []
    for k in range(16):
        out.append((k, 1.0, m))
        m += (1, 1, 1, -1)[k % 4]
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_TARN + 1.0, 'Bb1', 76, 'trem')
    for t, m, v, d in play('loge_ambivalent', T_ASK, 0.5, -12, 84):
        add(t, d, m, v, 'sly')
    for t, m, v, d in play('loge_flicker', T_ASK + 3.0, 0.16, 0, 86):
        add(t, d, m, v, 'loge')
    for j, (b, d, m) in enumerate([(0, .5, 'F3'), (.5, .5, 'Bb3'), (1, .5, 'F3'), (1.5, .5, 'Db3'), (2, 1, 'Bb2'),
                                   (3, .3, 'F3'), (3.3, .3, 'F3'), (3.6, .6, 'Bb2')]):
        add(T_BOAST + b * 0.5, d * 0.5, m, 96, 'alb')
    for t, m, v, d in play('tarnhelm', T_TARN, TB, 0, 74):
        add(t, d, m, v, 'tarn')
    for m in ('B5', 'Eb6'):
        add(T_TARN, T_EMERGE - T_TARN, m, 46, 'mist')
    add(T_EMERGE - 1.6, 1.6, 'Bb1', 100, 'rise')
    add(T_EMERGE, 1.5, 'Bb0', 120, 'emerge')

    for k, tc in enumerate(COILS):                          # the coiling line in tubas, bassoon, basses
        for b, d, m in coil_line(('Bb1', 'Db2', 'E2')[k]):
            add(tc + b * 0.4, d * 0.4 * 1.05, m, 96 + 6 * k, 'coil')
        add(tc, 6.4, ('Bb1', 'Db2', 'E2')[k], 70 + 8 * k, 'trem')
    for b, d, m in coil_line('G2'):                         # at its height, in the trombones too
        add(39.6 + b * 0.5, d * 0.5 * 1.05, m, 112, 'coil')
        add(39.6 + b * 0.5, d * 0.5 * 1.05, m + 12, 104, 'coilhi')
    add(39.6, T_ROAR - 39.6, 'G1', 92, 'trem')
    for i, ts in enumerate(SNAPS):                          # jaws open (a hiss), snap (a stab)
        add(ts - 0.45, 0.45, 'C4', 80, 'hiss')
        big = ts in BIG
        for m in (('Bb2', 'Db3', 'E3', 'G3') if big else ('Bb2', 'E3')):
            add(ts, 0.35, note(m) + (i % 3), 116 if big else 106, 'snap')
        add(ts, 0.3, 'Bb1', 124 if big else 108, 'bite')
        add(ts + 0.25, 0.3, note('D5') - i % 4, 80, 'cower')           # Loge, feigning terror
        add(ts + 0.45, 0.3, note('A4') - i % 4, 74, 'cower')
    add(T_ROAR, 2.0, 'Bb1', 126, 'roar')
    for m in ('Bb1', 'E2', 'Bb2', 'Db3', 'E3', 'G3'):
        add(T_ROAR, 2.2, m, 116, 'tutti')

    for t, m, v, d in play('tarnhelm', T_SHRINK, TB * 0.8, 0, 72):     # back into Alberich
        if t < T_BACK + 0.6:
            add(t, d, m, v, 'tarn')
    for b, d, m in coil_line('E2'):
        add(T_SHRINK + b * 0.35, 0.37, note('E2') + note('E2') - m, 84 - 2 * b, 'coil')
    add(T_BACK, 0.5, 'Bb1', 106, 'appear')
    add(T_BACK, D - T_BACK, 'Bb1', 70, 'trem')
    for k, tl in enumerate(LAUGHS):                         # "ha, ha, ha!"
        for j, m in enumerate(('F3', 'Db3', 'Bb2', 'F2')[: 3 + (k == 2)]):
            add(tl + j * 0.32, 0.22, note(m) + (2 if k == 1 else 0), 104 - 4 * j, 'laugh')
    for t, m, v, d in play('loge_flicker', T_WONDER - 1.4, 0.2, 0, 82):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('loge_ambivalent', T_WONDER, 0.62, -12, 76):
        add(t, d, m, v, 'sly')
    for t, m, v, d in play('ring', T_STIR, 0.5, 3, 66):
        if m > note('C3') and t < D - 0.4:
            add(t, d, m, v, 'stir')
    for bar in range(2):                                    # the forges, faintly
        t0 = T_STIR + 0.6 + bar * 3 * NB
        for b in range(3):
            for k, off in enumerate(RHY):
                add(t0 + (b + off) * NB, NB * (0.45, 0.15, 0.3)[k], 'Bb2' if k != 1 else 'F2', 70 - 6 * bar, 'pluck')
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


def choreography(G):
    """Per frame: Alberich, Wotan, Loge, the serpent's head and tail (path distance), and its size 0..1."""
    F = nframes(D)
    t = np.arange(F) * DT
    A = at(G, 'Porch Front', 0.5)
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_(0, 0, D, A, 4.0)
    set_(0, T_BOAST, T_BOAST + 2.0, A + 8 * np.sin(2 * np.pi * t / 0.5), 12.0)
    for tl in LAUGHS:
        set_(0, tl, tl + 1.2, A + 7 * np.sin(2 * np.pi * t / 0.32), 14.0)
    set_(1, 0, D, at(G, 'Porch Left', 0.7), 3.0)
    wob = 10 * np.sin(2 * np.pi * t / 1.1)
    set_(2, 0, D, at(G, 'Porch Left', 0.55) + wob, 1.0)
    set_(2, T_ASK, T_TARN, at(G, 'Porch Front', 0.32) + 0.6 * wob, 1.0)
    set_(2, T_TARN, T_EMERGE, at(G, 'Porch Front', 0.25) + 0.6 * wob, 1.0)
    # feigning terror: backing off from the head at every bite, to cower near the corner of Left
    set_(2, T_EMERGE, T_SHRINK, at(G, 'Porch Left', 0.1) + 0.4 * wob, 1.6)
    for ts in SNAPS:
        set_(2, ts, ts + 0.6, at(G, 'Porch Left', 0.03) - 25, 8.0)
    set_(2, T_SHRINK + 2.0, T_WONDER - 1.5, at(G, 'Porch Left', 0.5) + wob, 0.8)
    set_(2, T_WONDER - 1.5, D, at(G, 'Porch Front', 0.25) + 0.6 * wob, 0.9)
    # the serpent: head rearing toward Loge and lashing out over Left, tail out over Right
    hp = [(T_EMERGE, A), (T_EMERGE + 3.5, at(G, 'Porch Front', 0.15)), (28.5, at(G, 'Porch Left', 0.55)),
          (33.0, at(G, 'Porch Left', 0.25)), (37.0, at(G, 'Porch Left', 0.5)), (41.0, at(G, 'Left', 0.75)),
          (45.0, at(G, 'Porch Left', 0.3)), (T_ROAR, at(G, 'Left', 0.85)), (T_SHRINK, at(G, 'Porch Left', 0.4)),
          (T_BACK - 0.6, A - 12)]
    tp = [(T_EMERGE, A), (T_EMERGE + 4.0, at(G, 'Right', 0.35)), (30.0, at(G, 'Right', 0.97)),
          (34.0, at(G, 'Right', 0.7)), (38.0, at(G, 'Right', 0.98)), (43.0, at(G, 'Right', 0.8)),
          (T_ROAR, at(G, 'Right', 0.99)), (T_SHRINK, at(G, 'Right', 0.95)), (T_BACK - 0.6, A + 12)]
    m = (t >= T_EMERGE) & (t < T_BACK)
    tgt[3][:] = A
    tgt[4][:] = A
    tgt[3][m] = np.interp(t[m], *zip(*hp))
    tgt[4][m] = np.interp(t[m], *zip(*tp)) + 30 * np.sin(2 * np.pi * t[m] / 0.9)
    rate[3][:] = 3.0
    rate[4][:] = 2.5
    for ts in SNAPS:                                        # the head lunges at each bite, then recoils
        mm = (t >= ts - 0.2) & (t < ts + 0.15)
        tgt[3][mm] -= 70
        rate[3][mm] = 14.0
    pos = np.array([follow(tgt[k], rate[k]) for k in range(5)])
    size = smoothstep(T_EMERGE - 0.2, T_EMERGE + 1.0, t) * (1 - smoothstep(T_BACK - 1.2, T_BACK, t))
    return dict(t=t, apos=pos[0], wpos=pos[1], lpos=pos[2], head=pos[3], tail=pos[4], size=size,
                heap=at(G, 'Porch Front', 0.68))


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    H = C['heap']
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    fl = Flicker(rng, G.N, 4.0, 11.0)
    cave = 0.5 + 0.5 * smooth_noise(rng, d, 160)
    pockets = rng.uniform(80, L - 80, 13)
    pw = rng.uniform(35, 90, 13)
    pocket = np.exp(-((d[:, None] - pockets[None, :]) / pw[None, :]) ** 2)
    pf_rate = rng.uniform(0.3, 0.9, 13)
    mist = 0.5 + 0.5 * smooth_noise(rng, d, 90)

    tarn = np.array([e[0] for e in N if e[4] == 'tarn'])
    loge = np.array([e[0] for e in N if e[4] in ('loge', 'sly')])
    laughs = np.array([e[0] for e in N if e[4] == 'laugh'])
    snaps = np.array(SNAPS)
    coils = np.array([e[0] for e in N if e[4] == 'coil'])

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['apos'][f], C['wpos'][f], C['lpos'][f]
        hd, tl, sz = C['head'][f], C['tail'][f], C['size'][f]
        I = keys(t, [(0, 0.44), (T_TARN, 0.4), (T_EMERGE, 0.36), (T_ROAR, 0.5), (T_BACK, 0.44), (D, 0.44)])
        vis = 1 - smoothstep(T_EMERGE - 2.0, T_EMERGE, t) + smoothstep(T_BACK - 0.8, T_BACK + 0.3, t)

        # the caverns
        bed = light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
        pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
        bed += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)))
        bed += light(SPARK, 0.65 * (rng.random(G.N) < 0.005 * (0.5 + I)))

        # the hoard
        w = 8 + 50 * HEAP
        shape = np.clip(1 - ((d - H) / w) ** 2, 0, 1) ** 0.6
        bed += light(GOLD, (0.4 + 0.5 * HEAP) * shape * (0.9 + 0.1 * smoulder(t)))
        bed += light(GLINT, 0.8 * shape * (tw(t) > 1.1)) + light(HOT, 0.4 * HEAP * shape ** 4)
        bed += light(GOLD, 0.25 * HEAP * np.exp(-((d - H) / (w + 120)) ** 2))

        # the Tarnhelm's shimmer, swirling round him as he changes (and changes back)
        sh = smoothstep(T_TARN - 0.5, T_TARN + 2, t) * (1 - smoothstep(T_EMERGE, T_EMERGE + 1.5, t))
        sh += smoothstep(T_SHRINK - 0.5, T_SHRINK + 1.0, t) * (1 - smoothstep(T_BACK, T_BACK + 2.0, t))
        if sh > 0:
            ti = int(np.searchsorted(tarn, t, side='right')) - 1
            pulse = np.exp(-(t - tarn[ti]) / 0.8) if ti >= 0 and t - tarn[ti] < 3 else 0.0
            reach = 100 + 500 * smoothstep(T_TARN, T_EMERGE, t) if t < T_EMERGE + 2 else 450.0
            swirl = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - ap) / 110 - 0.6 * t) + 4 * mist)
            env = smoothstep(reach, reach - 200, np.abs(d - ap))
            bed = bed * (1 - 0.5 * (sh * env)[:, None]) + light(TARN, sh * env * (0.22 + 0.2 * swirl + 0.15 * pulse))
            bed += light(TARN_HI, sh * env * 0.35 * swirl ** 6 * (0.5 + 0.5 * tw(t)))

        # the serpent: a green-black scaled body from head to tail, coils of green rolling down it
        if sz > 0:
            s = np.clip((d - hd) / (tl - hd if abs(tl - hd) > 1 else 1.0), -0.2, 1.2)    # 0 at the head, 1 the tail
            body = smoothstep(-0.02, 0.02, s) * (1 - smoothstep(0.96, 1.02, s)) * sz
            taper = 1 - 0.55 * smoothstep(0.55, 1.0, s)
            ci = int(np.searchsorted(coils, t, side='right')) - 1
            cp = np.exp(-(t - coils[ci]) / 0.3) if ci >= 0 and t - coils[ci] < 1 else 0.0
            heave = smoothstep(39.0, 42.0, t) * (1 - smoothstep(T_ROAR + 0.5, T_SHRINK + 1, t))
            coil = 0.5 + 0.5 * np.sin(2 * np.pi * (np.abs(d - hd) / 150 - (1.3 + 0.8 * heave) * t))
            scales = (np.sin(d / 3.2) > 0.3) * (0.5 + 0.5 * tw(t))
            bed = bed * (1 - 0.88 * body)[:, None]
            fr += light(SCALE, body * (0.3 + 0.2 * scales * (1 - coil)))
            fr += light(COIL, body * taper * (0.08 + 0.12 * heave + 0.12 * cp + (0.8 + 0.15 * heave) * coil ** 4))
            fr += light(SHEEN, body * taper * 0.6 * scales * coil ** 8)
            # the head: an eye, and jaws that open before each bite and snap shut
            si = int(np.searchsorted(snaps, t + 0.5, side='right')) - 1
            gap, bite = 0.0, 0.0
            if si >= 0:
                ts = snaps[si]
                gap = 26 * smoothstep(ts - 0.5, ts - 0.1, t) * (1 - smoothstep(ts - 0.05, ts, t))
                bite = np.exp(-(t - ts) / 0.15) if t >= ts else 0.0
            dirn = -np.sign(tl - hd) if abs(tl - hd) > 1 else -1.0
            jaw_at = hd + dirn * 6
            jaws = np.exp(-((d - (jaw_at - gap)) / 6) ** 2) + np.exp(-((d - (jaw_at + gap)) / 6) ** 2) * (gap > 2)
            fr += light(JAW, sz * (0.75 * jaws + 0.9 * bite * np.exp(-((d - jaw_at) / (20 + 40 * bite)) ** 2)))
            fr += light(WHITE, sz * 0.6 * bite * np.exp(-((d - jaw_at) / 14) ** 2))
            fr += light(EYE, sz * 0.9 * np.exp(-((d - (hd - dirn * 18)) / 4) ** 2))
            if gap > 2:
                fr += light(RED, sz * 0.5 * (np.abs(d - jaw_at) < gap - 4))                 # inside the mouth
            if si >= 0 and snaps[si] in BIG and 0 <= t - snaps[si] < 0.6:
                age = t - snaps[si]
                fr += light(COIL, 0.6 * np.exp(-age / 0.15) * np.ones(G.N))
                fr += light(SHEEN, 0.3 * np.exp(-age / 0.08) * np.ones(G.N))
            if T_ROAR <= t < T_ROAR + 2.0:
                age = t - T_ROAR
                r = 1400 * (1 - np.exp(-age / 0.6))
                fr += light(SHEEN, 0.8 * np.exp(-age / 0.9) * np.exp(-((np.abs(d - hd) - r) / 90) ** 2))
                fr += light(COIL, 0.5 * np.exp(-age / 0.5) * np.ones(G.N))
        fr += bed

        # Alberich and the ring, while he is himself
        if vis > 0:
            li_ = int(np.searchsorted(laughs, t, side='right')) - 1
            ha = np.exp(-(t - laughs[li_]) / 0.15) if li_ >= 0 and t - laughs[li_] < 1 else 0.0
            pop = np.exp(-max(t - T_BACK, 0) / 0.4) * (t > T_BACK)
            fr += light(MUD, vis * 0.38 * np.exp(-((d - ap) / 120) ** 2) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, vis * (0.8 + 0.25 * ha + 0.3 * pop) * np.exp(-((d - ap) / (24 + 10 * ha + 20 * pop)) ** 2)
                        * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, vis * 0.35 * ha * np.exp(-((d - ap) / 220) ** 2))
            rr = ap + 10
            fr += light(GOLD, vis * 0.95 * np.exp(-((d - rr) / 5) ** 2))
            fr += light(RED, vis * 0.75 * np.exp(-((d - (rr + 6 * np.sin(2 * np.pi * 0.8 * t))) / 3) ** 2))

        # Wotan, standing his ground; Loge, shrinking from every bite
        under = sz * (wp > min(hd, tl)) * (wp < max(hd, tl))
        fr += light(WOTAN, (0.85 - 0.25 * under) * np.exp(-((d - wp) / 22) ** 2) + 0.25 * np.exp(-((d - wp) / 80) ** 2))
        si = int(np.searchsorted(snaps, t, side='right')) - 1
        flinch = np.exp(-(t - snaps[si]) / 0.4) if si >= 0 and t - snaps[si] < 2 else 0.0
        afraid = smoothstep(T_EMERGE, T_EMERGE + 1.0, t) * (1 - smoothstep(T_SHRINK + 1, T_BACK + 1, t))
        li = int(np.searchsorted(loge, t, side='right')) - 1
        lf = np.exp(-(t - loge[li]) / 0.15) if li >= 0 and t - loge[li] < 1 else 0.0
        small = smoothstep(T_WONDER + 2.0, T_WONDER + 3.0, t) * (1 - smoothstep(T_WONDER + 6.5, T_WONDER + 7.5, t))
        width = (18 + 8 * lf) * (1 - 0.55 * afraid) * (1 - 0.4 * small) * (1 - 0.3 * flinch)
        bright = (0.72 + 0.28 * lf) * (1 - 0.35 * afraid) * (1 - 0.2 * small)
        lc = LOGE_A + (LOGE_B - LOGE_A) * (0.5 + 0.5 * fl(t))[:, None]
        jitter = 6 * afraid * np.sin(2 * np.pi * 9 * t)
        ls = (bright * np.exp(-((d - lp - jitter) / width) ** 2) * (0.75 + 0.25 * fl(t))
              + 0.25 * (1 - 0.6 * afraid) * np.exp(-((d - lp) / 60) ** 2))
        fr += perc(ls)[:, None] * lc
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    def pan_body(t):
        return 0.5 * (pan_of('head', t) + pan_of('tail', t))

    for name, gain, rev in (('strings', 0.18, 0.3), ('low', 0.21, 0.15), ('brass', 0.19, 0.32), ('winds', 0.17, 0.3),
                            ('perc', 0.2, 0.25), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vcp = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    bst = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbst = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crashshort*.wav')
    bigcrash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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

    for t, d, m, v, part, who in compose():
        pa = pan_of('apos', t)
        if part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.55)
            hold('low', cb, m, t, t + d, v - 10, 0.0, rise=1.0, fall=1.5, gain=0.45)
        elif part == 'sly':
            p = pan_of('lpos', t)
            if m >= note('C4'):
                M.add('strings', vn.play(m, v, dur=d, release=0.15), t, 0.6, p)
            else:
                M.add('strings', harp.play(m + 12, v), t, 0.9, p)
                M.add('winds', cl.play(m + 12, v - 10, dur=d, release=0.15), t, 0.5, p)
        elif part == 'loge':
            p = pan_of('lpos', t)
            M.add('winds', pic.play(m, v), t, 0.9, p)
            M.add('strings', harp.play(m - 12, v - 10), t, 0.8, p)
        elif part == 'alb':
            M.add('low', bsus.play(m - 12, v, dur=d, release=0.1), t, 0.9, pa)
            M.add('brass', tbst.play(m, v - 14), t, 0.5, pa)
        elif part == 'tarn':
            M.add('brass', mute.play(m, v, dur=d * 1.02, release=0.8), t, 0.8, pa + 0.1 * np.sign(m - 60))
        elif part == 'mist':
            hold('strings', vtrem, m - 12, t, t + d, v, 0.0, rise=3.0, fall=1.0, gain=0.4)
        elif part == 'rise':
            M.add('perc', roll.play(v, dur=d + 0.3), t, 0.7, pa)
            M.add('fx', whoosh(d, 200, 2500, 0.4, seed=5), t, 0.6, pa)
        elif part == 'emerge':
            M.add('perc', gong.play(v), t, 0.8, pa)
            M.add('perc', bd.play(v), t, 0.9, pa)
            M.add('low', tuba.play(m + 12, v, dur=d, release=0.6), t, 1.0, pa)
        elif part == 'coil':
            p = pan_body(t)
            M.add('low', tuba.play(m + 12 if m < note('E1') else m, v, dur=d, release=0.15), t, 0.9, p - 0.15)
            M.add('low', bsus.play(m, v - 8, dur=d, release=0.15), t, 0.7, p + 0.15)
            M.add('low', cb.play(m, v - 10, dur=d, release=0.15), t, 0.5, p)
        elif part == 'coilhi':
            M.add('brass', tbn.play(m, v, dur=d, release=0.15), t, 0.7, pan_body(t))
        elif part == 'hiss':
            M.add('fx', whoosh(d, 6000, 2500, 0.35, seed=int(t * 10)), t, 0.6, pan_of('head', t))
        elif part == 'snap':
            p = pan_of('head', t)
            M.add('brass', (tbn if m >= note('Bb2') else tuba).play(m, v, dur=d, release=0.15), t, 0.75, p)
            M.add('brass', horn.play(m + 12, v - 10, dur=d, release=0.15), t, 0.45, p)
        elif part == 'bite':
            p = pan_of('head', t)
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, p)
            M.add('perc', (bigcrash if v >= 120 else crash).play(v), t, 0.7, p)
        elif part == 'cower':
            M.add('winds', pic.play(m, v), t, 0.7, pan_of('lpos', t))
        elif part == 'roar':
            M.add('perc', gong.play(v), t, 1.0, 0.0)
            M.add('perc', bigcrash.play(v), t, 0.9, 0.0)
            M.add('perc', bd.play(v), t, 0.9, 0.0)
            M.add('perc', roll.play(v, dur=d), t, 0.8, 0.0)
        elif part == 'tutti':
            if m < note('Bb2'):
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.6), t, 0.8, 0.0)
            else:
                M.add('brass', tbn.play(m, v, dur=d, release=0.6), t, 0.6, 0.0)
                M.add('brass', horn.play(m + 12, v, dur=d, release=0.6), t, 0.5, 0.0)
        elif part == 'appear':
            M.add('brass', tbn.play(m + 12, v, dur=0.8, release=0.3), t, 0.8, pa)
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, pa)
            gl = [x for x in range(note('Ab4'), note('Eb6') + 1) if x % 12 in (8, 11, 3)]
            for i, x in enumerate(reversed(gl)):
                M.add('strings', harp.play(x, 80), t - 1.4 + i * 1.4 / len(gl), 0.8, pa)
        elif part == 'laugh':
            M.add('low', bst.play(m, v), t, 0.9, pa)
            M.add('brass', tbst.play(m, v - 12), t, 0.6, pa)
        elif part == 'stir':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.8, pa)
        elif part == 'pluck':
            M.add('low', pizz.play(m, v), t, 0.7, -0.15)
            M.add('strings', vcp.play(m, v - 10), t, 0.5, 0.15)
