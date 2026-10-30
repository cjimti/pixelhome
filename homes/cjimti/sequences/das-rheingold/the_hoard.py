"""The Hoard: Alberich (red), visible again on Porch Right, cracks his whip, and the Nibelungs come hauling his
treasure up out of the mines: two streams of orange sparks pour in, one from the free end of Right and one from
the corner of Left, each spark carrying a speck of gold to the middle of Porch Front, where the hoard piles up
(gold #ffaa00, glinting) and grows with every load, to the Nibelung rhythm in the low strings and bassoons and the
Gold's call (Donington 44) on horns and trumpets. Mime is swept away with the others down Left and out along
Side; Wotan (blue) and Loge (fire) step back up Porch Left to watch.

Alberich takes his place beside the heap and draws the Ring (8): the motif in the woodwinds, the ring a hard
gold point on him with a red glint turning in it. The streams falter. Then he brandishes it, and the Nibelungs
scatter in terror: a blast of red tears outward from him to both ends of the house, the whole roof flashes red,
and every spark flies for the ends with shrieks of piccolo and xylophone.

He turns on the gods and boasts that the world will be his: the Valhalla motif (63) comes out twisted into the
minor in trombones and tubas while a sick red ghost of the battlements flickers on the porch and every boast
reaches a red arm up Porch Left that makes Wotan's blue flinch; the Ring and the Gold again, darker. Loge
flatters him: the flicker of his fire (20a) and his sly, ambivalent figure (21a) on piccolo, violins and harp,
the flame dancing up close to Alberich and back. It ends with Alberich at the middle of Porch Front, the ring on
him, the hoard glowing beside him, Wotan and Loge on Porch Left, a muted horn stirring the Ring.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG15'
TITLE = 'The Hoard'
KIND = 'show'
DESCRIPTION = ('Alberich drives his slaves in with their treasure, and the gold piles up in the middle of the '
               'porch. He holds up the ring and they flee in terror, then he turns to Wotan and boasts that one day '
               'the whole world, and the gods with it, will be his.')
VOICEOVER = ('Watch the gold pile up. Everything the Nibelungs dig out of the earth, they bring to him. '
             'And with that ring on his finger, he thinks the gods will be next.')

NB = 0.6                                    # a dotted quarter of the Nibelung 9/8
BAR = 3 * NB
RHY = (0.0, 0.5, 2 / 3)
CRACKS = [1.5, 9.6, 17.7, 23.1]             # his whip
T_HAUL = 2.4                                # the streams of the hoard
HBARS = 13
T_STOP = T_HAUL + HBARS * BAR               # the hauling stops
T_RING = 27.8                               # he draws the Ring
T_BLAST = 33.4                              # brandishes it: they scatter
BOASTS = [38.6, 44.6]                       # Valhalla in the minor
T_RING2 = 50.8
T_GOLD2 = 55.6
T_LOGE = 61.0                               # Loge flatters
T_SLY = 65.8
T_STIR = 75.0
D = 80.0

FIGURE = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
          ('Gb4', 'F4', 'Eb4'), ('Db4', 'C4', 'Bb3'), ('C4', 'A3', 'F3')]

EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
SPARK = hexc('#ff7a10')
HOT = hexc('#fff0a0')
GOLD = hexc('#ffaa00')
GLINT = hexc('#ffd860')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
MIME = hexc('#b0d020')
WOTAN = hexc('#1a3cff')
LOGE_A = hexc('#ff5000')
LOGE_B = hexc('#ffb020')
GHOST = hexc('#d04030')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_HAUL + 1.0, 'Bb1', 76, 'trem')
    for i, tc in enumerate(CRACKS):                         # "Hierher! Hehe!" and the whip
        for j, m in enumerate(('F3', 'Bb3', 'Bb3')):
            add(tc - 0.5 + j * 0.15, 0.14, m, 104, 'alb')
        add(tc, 0.2, 'C4', 114, 'crack')
    for bar in range(HBARS):                                # hauling the hoard
        t0 = T_HAUL + bar * BAR
        grow = min(1.0, (bar + 3) / 7) * (1 - 0.5 * smoothstep(HBARS - 3, HBARS, bar))
        if bar % 2 == 0:
            add(t0, BAR * 2, 'Bb1', int(86 + 24 * grow), 'pedal')
        for b in range(3):
            fig = FIGURE[(bar % 2) * 3 + b]
            for k, off in enumerate(RHY):
                t = t0 + (b + off) * NB
                acc = b == 0 and k == 0
                dd = NB * (0.45, 0.15, 0.3)[k]
                add(t, dd, 'Bb2' if k != 1 else 'F2', int(76 + 30 * grow) + 8 * acc, 'pluck')
                add(t, dd, fig[k], int(66 + 40 * grow) + 8 * acc, 'nib')
                if acc and bar % 2 == 0:
                    add(t, 0.1, 'C4', int(90 + 20 * grow), 'anvil')
    for i, t0 in enumerate((T_HAUL + 5.4, T_HAUL + 12.6)):  # the Gold's call, as it piles up
        for t, m, v, d in play('gold', t0, 0.4, 3 + 5 * i, 96 + 8 * i):
            add(t, d, m, v, 'gold')
    rng = np.random.default_rng(15)
    pent = [note(n) for n in ('Bb4', 'Db5', 'Eb5', 'F5', 'Ab5', 'Bb5')]
    for t in np.arange(T_HAUL + 2.0, T_STOP, 0.45):         # each load landing on the heap
        add(t + rng.uniform(0, 0.15), 0.4, int(rng.choice(pent)), int(rng.uniform(60, 84)), 'clink')

    add(T_STOP, T_BLAST - T_STOP, 'Bb1', 70, 'trem')
    for j, (b, d, m) in enumerate([(0, .5, 'Bb2'), (.5, .5, 'Db3'), (1, 1, 'F3'), (2, 1, 'E3'), (3, 2, 'F3')]):
        add(T_STOP + 0.3 + b * 0.32, d * 0.32, m, 92, 'grumble')
    for t, m, v, d in play('ring', T_RING, 0.5, 3, 92):
        add(t, d, m, v, 'ring' if m > note('C3') else 'ringbass')
    add(T_BLAST - 1.6, 1.6, 'Bb1', 100, 'rise')
    add(T_BLAST, 2.4, 'Bb1', 124, 'blast')
    for m in ('Bb2', 'Db3', 'F3', 'Bb3', 'Db4', 'F4'):
        add(T_BLAST, 2.0, m, 118, 'tutti')
    for i in range(14):                                     # the Nibelungs' shrieks, flying to both ends
        add(T_BLAST + 0.1 + i * 0.12, 0.1, note('F5') + (i * 5) % 12, 108 - 3 * i, 'shriek', i % 2)

    add(BOASTS[0] - 1.0, T_LOGE - BOASTS[0] + 1.0, 'Bb1', 72, 'trem')
    for k, tb in enumerate(BOASTS):                         # "Die in linden Lüften ihr lebt...": Valhalla, twisted
        for t, m, v, d in play('valhalla', tb, 0.6, -3 + 2 * k, 104 + 6 * k):     # its thirds and sixths flattened
            m2 = m - 1 if (m % 12) in ((note('F2') - 3 + 2 * k) % 12, (note('Bb2') - 3 + 2 * k) % 12) else m
            add(t, d, m2, v, 'boast')
        add(tb, 0.5, 'Bb1', 108, 'thump')
    for t, m, v, d in play('ring', T_RING2, 0.45, -9, 100):
        add(t, d, m, v, 'ringlow')
    for t, m, v, d in play('gold', T_GOLD2, 0.45, 2, 100):
        add(t, d, m, v, 'goldlow')
        add(t, d, m - 12, v - 6, 'goldlow')
    for j, (b, d, m) in enumerate([(0, .3, 'F3'), (.5, .3, 'F3'), (1, .3, 'Db3'), (1.5, .3, 'Bb2'), (2, .5, 'F2')]):
        add(T_GOLD2 + 3.4 + b * 0.4, d * 0.4, m, 96 - 4 * j, 'laugh')

    for t, m, v, d in play('loge_flicker', T_LOGE, 0.2, 0, 92):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('loge', T_LOGE + 2.2, 0.38, 12, 80):
        add(t, d, m, v, 'logefire')
    for t, m, v, d in play('loge_ambivalent', T_SLY, 0.55, -12, 82):
        add(t, d, m, v, 'sly')
    for t, m, v, d in play('loge_flicker', T_SLY + 5.0, 0.2, 0, 84):
        add(t, d, m, v, 'loge')
    add(T_LOGE, D - T_LOGE, 'Bb1', 78, 'trem')
    for t, m, v, d in play('ring', T_STIR, 0.55, 3, 70):
        if m > note('C3') and t < D - 0.5:
            add(t, d, m, v, 'stir')
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
    """Per frame: Alberich, Mime, Wotan, Loge (path distance); where the heap is."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((4, F))
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    A = at(G, 'Porch Front', 0.5)
    set_(0, 0, D, at(G, 'Porch Right', 0.55), 6.0)
    set_(0, 3.0, T_STOP, at(G, 'Porch Front', 0.88) + 30 * np.sin(2 * np.pi * t / 5.0), 1.0)
    set_(0, T_STOP, D, A, 1.2)
    for tc in CRACKS[1:]:                                   # a lunge with each crack of the whip
        set_(0, tc - 0.3, tc + 0.2, at(G, 'Porch Front', 0.88) + 45, 10.0)
    set_(0, T_BLAST - 0.25, T_BLAST + 0.4, A - 25, 12.0)
    for tb in BOASTS:                                       # leaning toward the gods at every boast
        set_(0, tb, tb + 1.0, A - 30, 5.0)
    set_(0, T_GOLD2 + 3.4, T_GOLD2 + 5.4, A + 6 * np.sin(2 * np.pi * t / 0.4), 12.0)
    set_(1, 0, D, at(G, 'Porch Left', 0.4), 4.0)
    m = t >= 2.0
    tgt[1][m] = np.interp(t[m], [2.0, 4.0, 8.0], [at(G, 'Porch Left', 0.4), at(G, 'Porch Left', 0.0) - 20, -120])
    rate[1][m] = 6.0
    set_(2, 0, D, at(G, 'Porch Front', 0.35), 2.0)
    set_(2, 4.0, D, at(G, 'Porch Left', 0.7), 0.9)
    for tb in BOASTS:
        set_(2, tb + 0.2, tb + 1.4, at(G, 'Porch Left', 0.62), 3.0)
    wob = 10 * np.sin(2 * np.pi * t / 1.1)
    set_(3, 0, D, at(G, 'Porch Front', 0.2) + wob, 2.0)
    set_(3, 5.0, T_LOGE, at(G, 'Porch Left', 0.5) + wob, 1.0)
    set_(3, T_LOGE, T_SLY + 4.0, at(G, 'Porch Front', 0.32) + 40 * np.sin(2 * np.pi * t / 1.7), 2.2)
    set_(3, T_SLY + 4.0, T_SLY + 7.5, at(G, 'Porch Front', 0.4) + 25 * np.sin(2 * np.pi * t / 0.9), 3.0)
    set_(3, T_SLY + 7.5, D, at(G, 'Porch Left', 0.55) + 0.6 * wob, 1.2)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, apos=pos[0], mpos=pos[1], wpos=pos[2], lpos=pos[3], heap=at(G, 'Porch Front', 0.68),
                src=[G.length + 30, at(G, 'Left', 0.0)])


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    H = C['heap']
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    fl = Flicker(rng, G.N, 4.0, 11.0)
    cave = 0.5 + 0.5 * smooth_noise(rng, d, 160)
    pockets = rng.uniform(80, L - 80, 13)
    pw = rng.uniform(35, 90, 13)
    pocket = np.exp(-((d[:, None] - pockets[None, :]) / pw[None, :]) ** 2)
    pf_rate = rng.uniform(0.3, 0.9, 13)

    cracks = np.array(CRACKS)
    rings = np.array([e[0] for e in N if e[4] in ('ring', 'ringlow')])
    boast = np.array([e[0] for e in N if e[4] == 'boast'])
    loge = np.array([e[0] for e in N if e[4] in ('loge', 'logefire', 'sly')])
    hits = np.array([e[0] for e in N if e[4] == 'anvil'])
    anv = np.array([at(G, 'Porch Left', 0.75), at(G, 'Porch Right', 0.4)])

    # the haul: sparks leave the two sources at steady intervals and run to the heap; some stay, milling about
    # in a crowd round it until the blast sends every one flying for the ends
    ns = 260
    side = np.arange(ns) % 2
    start = T_HAUL + np.sort(rng.uniform(0, T_STOP - T_HAUL - 2.0, ns))
    src = np.array(C['src'])[side]
    speed = rng.uniform(260, 380, ns)
    arrive = start + np.abs(H - src) / speed
    gold = rng.random(ns) < 0.6
    stay = rng.random(ns) < 0.35
    home = np.clip(H + rng.normal(0, 330, ns), 520, L - 60)
    flee_to = np.where(home < at(G, 'Porch Front', 0.5), -80.0, L + 80)
    jig = rng.uniform(0, 2 * np.pi, ns)

    def spark_pos(t):
        """Where each spark is at time t (before the blast), and whether it is to be seen."""
        run = src + np.sign(H - src) * speed * (t - start)
        back = home + (H - home) * np.exp(-np.clip(t - arrive, 0, None) / 0.6) + 8 * np.sin(5 * t + jig)
        p = np.where(t < arrive, run, np.where(stay, back, H + 25 * np.sin(jig + 3 * t)))
        vis = (t >= start) & ((t < arrive + 0.3) | stay)
        return p, vis

    def heap_size(t):
        landed = (arrive <= t) & gold & (arrive < T_BLAST)
        return 1 - np.exp(-landed.sum() / 70)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        I = keys(t, [(0, 0.44), (T_HAUL + 4, 0.54), (T_STOP, 0.5), (T_BLAST, 0.42), (T_BLAST + 3, 0.34),
                     (BOASTS[0], 0.4), (T_LOGE, 0.44), (D, 0.44)])
        ap, mp, wp, lp = C['apos'][f], C['mpos'][f], C['wpos'][f], C['lpos'][f]

        # the caverns
        fr += light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
        pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
        fr += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)))
        fr += light(SPARK, 0.65 * (rng.random(G.N) < 0.005 * (0.5 + I)))
        hi = int(np.searchsorted(hits, t, side='right')) - 1
        if hi >= 0 and t - hits[hi] < 0.3:
            g = np.exp(-((d[:, None] - anv[None, :]) / 13) ** 2).max(axis=1)
            fr += light(HOT, 0.8 * np.exp(-(t - hits[hi]) / 0.07) * g)

        # the haul: sparks running in to the heap, carrying gold; the crowd scattering at the blast
        if t < T_BLAST:
            p, live = spark_pos(t)
            fade = np.where(t < arrive, 0.95, 0.55 + 0.25 * (t >= T_STOP) * np.sin(9 * t + jig) ** 2)
        else:
            age = t - T_BLAST
            p0, live = spark_pos(T_BLAST)
            p = p0 + (flee_to - p0) * (1 - np.exp(-age / 0.8))
            live = live & (age < 3.2)
            fade = np.full(ns, np.exp(-age / 1.8))
        if live.any():
            q = p[live]
            g = np.exp(-((d[:, None] - q[None, :]) / 9) ** 2)
            fr += light(SPARK, (g * fade[live][None, :]).max(axis=1))
            gl = gold[live] & (t < arrive[live])
            if gl.any():
                fr += light(GOLD, 0.85 * np.exp(-((d[:, None] - q[gl][None, :]) / 4) ** 2).max(axis=1))

        # the hoard: a heap of gold that grows with every load, glinting
        hs = heap_size(t)
        if hs > 0:
            w = 8 + 50 * hs
            shape = np.clip(1 - ((d - H) / w) ** 2, 0, 1) ** 0.6
            fr += light(GOLD, (0.4 + 0.5 * hs) * shape * (0.9 + 0.1 * smoulder(t)))
            fr += light(GLINT, 0.8 * shape * (tw(t) > 1.1)) + light(HOT, 0.4 * hs * shape ** 4)
            fr += light(GOLD, 0.25 * hs * np.exp(-((d - H) / (w + 120)) ** 2))

        # the blast of red outward from him, and the red ghost of Valhalla while he boasts
        if T_BLAST <= t < T_BLAST + 3.0:
            age = t - T_BLAST
            r = 1500 * (1 - np.exp(-age / 0.8))
            band = np.exp(-((np.abs(d - ap) - r) / (70 + 90 * age)) ** 2)
            fr += light(RED, 1.0 * band * np.exp(-age / 1.6))
            fr += light(RED, 0.85 * np.exp(-age / 1.1) * smoothstep(r + 100, r - 250, np.abs(d - ap)))
            fr += light(HOT, 0.4 * np.exp(-age / 0.1) * np.exp(-((d - ap) / 80) ** 2))
        ghost = smoothstep(BOASTS[0] - 0.5, BOASTS[0] + 1.0, t) * (1 - smoothstep(T_RING2 + 3, T_LOGE, t))
        if ghost > 0:
            bi = int(np.searchsorted(boast, t, side='right')) - 1
            bp = np.exp(-(t - boast[bi]) / 0.35) if bi >= 0 and t - boast[bi] < 2 else 0.0
            crenel = (np.sin(d / 9.0) > -0.2) * porch
            fr += light(GHOST, ghost * (0.28 + 0.32 * bp) * crenel * (0.8 + 0.2 * fl(t)))
            lo, hi = np.searchsorted(boast, t - 1.8), np.searchsorted(boast, t, side='right')
            for tb in np.unique(boast[lo:hi]):              # every chord echoes out through the caverns
                age = t - tb
                fr += light(RED, 0.5 * np.exp(-age / 0.7) * np.exp(-((np.abs(d - ap) - 60 - 850 * age) / 70) ** 2))
            fr += light(ALB, ghost * 0.35 * bp * np.exp(-((d - ap) / 300) ** 2))
        for tb in BOASTS:                                   # a red arm reaching up Porch Left at the gods
            if tb <= t < tb + 2.5:
                age = t - tb
                reach = ap - (ap - wp) * smoothstep(0, 0.8, age)
                arm = (d <= ap) & (d >= reach)
                fr += light(ALB, 0.6 * np.exp(-age / 1.0) * arm * (0.7 + 0.3 * fl(t)))

        # Alberich, and the Ring on him: a hard gold point with a red glint turning in it
        ci = int(np.searchsorted(cracks, t, side='right')) - 1
        jolt = np.exp(-(t - cracks[ci]) / 0.2) if ci >= 0 and t - cracks[ci] < 1.2 else 0.0
        swell = smoothstep(T_BLAST - 1.6, T_BLAST, t) * np.exp(-max(t - T_BLAST, 0) / 2.0)
        fr += light(MUD, 0.38 * np.exp(-((d - ap) / 120) ** 2) * (1 + 0.15 * smoulder(t)))
        fr += light(ALB, (0.8 + 0.2 * jolt + 0.2 * swell) * np.exp(-((d - ap) / (24 + 8 * jolt + 22 * swell)) ** 2)
                    * (1 + 0.15 * smoulder(t)))
        if jolt > 0:                                        # the lash out at the streams
            fr += light(RED, 0.6 * jolt * ((d > ap) & (d < ap + 160)) * np.exp(-((d - ap) / 120) ** 2))
        ring = smoothstep(T_RING - 0.3, T_RING + 1.5, t)
        if ring > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.3) if ri >= 0 and t - rings[ri] < 2 else 0.0
            rp = max(rp, swell)
            rr = ap + 10
            fr += light(GOLD, ring * (0.95 + 0.3 * rp) * np.exp(-((d - rr) / 5) ** 2))
            glint = rr + 6 * np.sin(2 * np.pi * 0.8 * t)
            fr += light(RED, ring * (0.75 + 0.25 * rp) * np.exp(-((d - glint) / 3) ** 2))
            fr += light(HOT, ring * 0.5 * rp * np.exp(-((d - rr) / 12) ** 2))

        # Mime swept away; Wotan; Loge's fire, dancing in close to flatter
        if t < 12.0:
            fr += light(MIME, 0.7 * np.exp(-((d - mp) / 15) ** 2) + 0.2 * np.exp(-((d - mp) / 60) ** 2))
        bi = int(np.searchsorted(boast, t, side='right')) - 1
        flinch = np.exp(-(t - boast[bi]) / 0.5) if bi >= 0 and t - boast[bi] < 2 and t < T_LOGE else 0.0
        fr += light(WOTAN, (0.85 - 0.3 * flinch) * np.exp(-((d - wp) / 22) ** 2) + 0.25 * np.exp(-((d - wp) / 80) ** 2))
        li = int(np.searchsorted(loge, t, side='right')) - 1
        lf = np.exp(-(t - loge[li]) / 0.15) if li >= 0 and t - loge[li] < 1 else 0.0
        lc = LOGE_A + (LOGE_B - LOGE_A) * (0.5 + 0.5 * fl(t))[:, None]
        dance = smoothstep(T_LOGE, T_LOGE + 1, t) * (1 - smoothstep(T_SLY + 7.5, T_SLY + 9, t))
        ls = ((0.72 + 0.28 * lf + 0.15 * dance) * np.exp(-((d - lp) / (18 + 8 * lf + 14 * dance)) ** 2)
              * (0.75 + 0.25 * fl(t)) + 0.25 * np.exp(-((d - lp) / 60) ** 2))
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
    hp = pan_at(C['heap'])

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.17, 0.3), ('low', 0.21, 0.15), ('brass', 0.19, 0.32), ('winds', 0.17, 0.3),
                            ('anvil', 0.08, 0.2), ('perc', 0.2, 0.25), ('fx', 0.12, 0.3), ('bells', 0.12, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vcp = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    bst = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbst = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    anvil = M.hits('Percussion/Anvil_Hit*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('Percussion/gongHit_f.wav')
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

    anv = [pan_at(at(G, 'Porch Left', 0.75)), pan_at(at(G, 'Porch Right', 0.4))]
    for t, d, m, v, part, who in compose():
        pa = pan_of('apos', t)
        if part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.55)
            hold('low', cb, m, t, t + d, v - 10, 0.0, rise=1.0, fall=1.5, gain=0.45)
        elif part == 'alb':
            M.add('low', bsus.play(m - 12, v, dur=d, release=0.1), t, 0.9, pa)
            M.add('brass', tbst.play(m, v - 14), t, 0.5, pa)
        elif part == 'crack':
            M.add('fx', whoosh(0.3, 900, 5000, 0.5, seed=int(t * 10)), t - 0.26, 0.7, pa)
            M.add('perc', slap.play(v), t, 1.0, pa)
        elif part == 'pedal':
            M.add('low', pizz.play(m + 12, v), t, 1.0, 0.0)
            hold('low', cb, m, t, t + d, max(40, v - 40), 0.0, rise=0.3, fall=0.4, gain=0.45)
        elif part == 'pluck':
            M.add('low', pizz.play(m, v), t, 0.7, -0.15)
            M.add('strings', vcp.play(m, v - 10), t, 0.5, 0.15)
        elif part == 'nib':
            M.add('winds', bst.play(m - 12, v), t, 0.8, -0.2)
            M.add('strings', vas.play(m, v - 6, dur=d, release=0.05), t, 0.5, 0.25)
        elif part == 'anvil':
            for k in range(2):
                M.add('anvil', anvil.play(v, pitch=(-3, 2)[k]), t + 0.01 * k, 1.0, anv[k])
        elif part == 'gold':
            M.add('brass', (tpt if t > T_HAUL + 10 else horn).play(m, v, dur=d, release=0.3), t, 0.85, hp)
        elif part == 'clink':
            M.add('bells', glock.play(m, v), t, 0.8, hp + 0.1 * np.sin(t * 7))
        elif part == 'grumble':
            M.add('low', bsus.play(m, v, dur=d, release=0.15), t, 0.9, pa)
        elif part == 'ring':
            s = ob if m >= note('E4') else cl
            M.add('winds', s.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pa + (0.1 if s is ob else -0.1))
            M.add('brass', horn.play(m - 12, v - 16, dur=d, release=0.3), t, 0.5, pa)
        elif part == 'ringbass':
            hold('low', vc, m + 12, t, t + d, v, pa, rise=0.4, fall=0.8, gain=0.7)
        elif part == 'rise':
            M.add('perc', roll.play(v, dur=d), t, 0.7, pa)
            hold('strings', vtrem, note('F4'), t, t + d, v, 0.0, rise=d, fall=0.05, gain=0.5)
        elif part == 'blast':
            M.add('perc', crash.play(v), t, 1.0, 0.0)
            M.add('perc', gong.play(v), t, 0.8, pa)
            M.add('perc', bd.play(v), t, 0.9, pa)
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, pa)
            M.add('fx', whoosh(1.4, 400, 5000, 0.6, seed=33), t, 0.8, 0.0)
        elif part == 'tutti':
            if m < note('Bb3'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.6), t, 0.7, 0.0)
                M.add('low', tuba.play(m - 12, v, dur=d, release=0.6), t, 0.6, 0.0)
            else:
                M.add('brass', horn.play(m, v, dur=d, release=0.6), t, 0.6, 0.0)
                M.add('strings', vn.play(m + 12, v, dur=d, release=0.6), t, 0.5, 0.0)
        elif part == 'shriek':
            p = -0.6 - 0.25 * (t - T_BLAST) / 1.8 if who == 0 else 0.6 + 0.25 * (t - T_BLAST) / 1.8
            M.add('winds', pic.play(m, v), t, 0.8, p)
            M.add('bells', xylo.play(m - 12, v), t, 0.8, p)
        elif part == 'boast':
            if m < note('C3'):
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.5), t, 0.8, pa)
            elif m < note('F3'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.7, pa - 0.1)
            else:
                M.add('brass', tbn.play(m, v - 6, dur=d, release=0.5), t, 0.6, pa + 0.1)
                M.add('low', bsus.play(m - 12, v - 16, dur=d, release=0.5), t, 0.4, pa)
        elif part == 'thump':
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, pa)
        elif part == 'ringlow':
            if m > note('C2'):
                M.add('brass', tbn.play(m + 12, v, dur=d, release=0.3), t, 0.75, pa)
            else:
                hold('low', cb, m + 12, t, t + d, v, pa, rise=0.4, fall=0.8, gain=0.7)
        elif part == 'goldlow':
            M.add('brass', (horn if m >= note('F3') else tbn).play(m, v, dur=d, release=0.3), t, 0.7, hp)
        elif part == 'laugh':
            M.add('low', bst.play(m, v), t, 0.9, pa)
            M.add('brass', tbst.play(m, v - 16), t, 0.5, pa)
        elif part == 'loge':
            p = pan_of('lpos', t)
            M.add('winds', pic.play(m, v), t, 0.9, p)
            M.add('strings', harp.play(m - 12, v - 10), t, 0.8, p)
        elif part == 'logefire':
            M.add('strings', vn.play(m, v, dur=d, release=0.1), t, 0.45, pan_of('lpos', t))
        elif part == 'sly':
            p = pan_of('lpos', t)
            if m >= note('C4'):
                M.add('strings', vn.play(m, v, dur=d, release=0.15), t, 0.6, p)
            else:
                M.add('strings', harp.play(m + 12, v), t, 0.9, p)
                M.add('winds', cl.play(m + 12, v - 10, dur=d, release=0.15), t, 0.5, p)
        elif part == 'stir':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.85, pa)
