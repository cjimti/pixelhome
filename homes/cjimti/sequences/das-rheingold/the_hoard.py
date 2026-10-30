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

The music is Wagner's own, from Scene 3 of Das Rheingold as Solti's 1958 Vienna Philharmonic recording takes it:
Alberich driving the Nibelungs with the hoard ("Hierher! Dorthin! Hehe! Hoho! Träges Heer!", bars 2236-2255),
drawing the Ring on them ("Zittre und zage, gezähmtes Heer! Rasch gehorcht des Ringes Herrn!") and their
terrified flight (2290-2310), his boast at the gods ("Habt acht vor dem nächtlichen Heer, entsteigt des
Niblungen Hort aus stummer Tiefe zu Tag!", 2505-2515), and Loge's flattery ("Gelingt deiner herrlichen List",
2529-2544). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the hauling on
basses, cellos and bassoons with the Gold on horns and trumpets, the Ring on the woodwinds and then the whole
orchestra, the boast on trombones and tubas, Loge on flutes, violins and harp. Like a staged production it adds
the crack of his whip, gold clinking onto the heap and a ring of hammers at the forges, a great blow as the
Ring's power scatters them, a thud under each boast, and a low crackle as Loge's flame dances near him.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'RG15'
TITLE = 'The Hoard'
KIND = 'show'
DESCRIPTION = ('Alberich drives his slaves in with their treasure, and the gold piles up in the middle of the '
               'porch. He holds up the ring and they flee in terror, then he turns to Wotan and boasts that one day '
               'the whole world, and the gods with it, will be his.')
VOICEOVER = ('Watch the gold pile up. Everything the Nibelungs dig out of the earth, they bring to him. '
             'And with that ring on his finger, he thinks the gods will be next.')

EX = excerpt(__file__)                      # bars 2236-2255, 2290-2310, 2505-2515, 2529-2544
BARS_ = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
CRACKS = [1.3, 8.9, 14.8, 19.8]             # his whip, on "Hierher!", "Du da, hinauf!", "Soll ich euch helfen?", "He!"
T_HAUL = 2.0                                # the streams of the hoard
T_STOP = 19.8                               # "He! Wer ist dort?": the hauling stops
T_RING = BARS_[2290]                        # he draws the Ring: "Zittre und zage"
T_BLAST = BARS_[2296]                       # its power: they scatter
BOASTS = [55.7, 63.9]                       # "Habt acht vor dem nächtlichen Heer", "aus stummer Tiefe zu Tag!"
T_RING2 = 60.2
T_GOLD2 = 64.0
T_LOGE = BARS_[2529]                        # Loge flatters
T_SLY = 74.8
T_STIR = D - 1.0

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who, tremolo). The haul is 'nib' (right
    hand; its long notes the Gold's call, 'gold') and 'pluck', with the forges' hammers ('anvil'); the Ring drawn is
    'ring' and 'ringbass'; the flight 'tutti'; the boast 'boast' (left hand's long notes), 'boastharm', the Ring
    and Gold darker ('ringlow', 'goldlow'); Loge 'loge' (quick notes), 'logefire', 'sly' and 'logebass'. 'crack'
    marks the whip."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t < T_RING:
            part = ('gold' if d >= 0.4 else 'nib') if h == 0 else 'pluck'
        elif t < T_BLAST:
            part = 'ring' if h == 0 else 'ringbass'
        elif t < BOASTS[0]:
            part = 'tutti'
        elif t < T_LOGE:
            if h == 1:
                part = 'boast' if d >= 0.4 else 'boastharm'
            else:
                part = 'goldlow' if t >= T_GOLD2 else 'ringlow' if t >= T_RING2 else 'boastharm'
        else:
            part = ('loge' if d < 0.25 else 'sly' if t >= T_SLY else 'logefire') if h == 0 else 'logebass'
        N.append((t, d, m, v, part, None, trem))
    strokes = []
    for t in sorted({round(n[0], 3) for n in EX['notes'] if n[4] == 0 and n[1] <= 0.35}):
        if T_HAUL <= t < T_STOP and (not strokes or t - strokes[-1] >= 0.5):
            strokes.append(t)
    for t in strokes:
        N.append((t, 0.1, 72, 96, 'anvil', None, False))
    for tc in CRACKS:
        N.append((tc, 0.2, 60, 0, 'crack', None, False))
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
    scat = accents(EX['notes'], T_BLAST + 1.0, BOASTS[0] - 0.5, 40, 2, 0.9)

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
        I = keys(t, [(0, 0.55), (T_HAUL + 4, 0.7), (T_STOP, 0.66), (T_BLAST, 0.6), (T_BLAST + 3, 0.5),
                     (BOASTS[0], 0.56), (T_LOGE, 0.58), (D, 0.58)])
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
        for ts in scat:                                     # the Ring's power: red shock waves after the fleeing
            if ts <= t < ts + 1.4:
                age = t - ts
                fr += light(RED, 0.95 * (1 - age / 1.4) * np.exp(-((np.abs(d - ap) - 480 * age) / 120) ** 2))
                fr += light(HOT, 0.6 * np.exp(-age / 0.12) * np.exp(-((d - ap) / 30) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the whip, the gold piling up, the forges, the
    Ring's blast and Loge's flame on the stage."""
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(min(max(dd, 0), G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    hp = pan_at(C['heap'])
    o = Orchestra(M, level=3.8)
    # the whip and the gold lead the haul; the Ring's chord and his boast are the music's; the blast is the stage's
    o.effects([(0.0, 0.0), (T_STOP, 0.0), (T_RING, -8.0), (T_BLAST - 0.3, -8.0), (T_BLAST, 0.0), (T_BLAST + 6.0, -4.0),
               (BOASTS[0], -9.0), (T_LOGE, -6.0), (D, -6.0)])
    snare = M.hits('Percussion/Snare2-HitSN_v[79]*.wav')
    rng = np.random.default_rng(15)
    N = compose()
    for t, d, m, v, part, who, trem in N:
        if v == 0 or part == 'anvil':
            continue
        ap = pan_at(np.interp(t, C['t'], C['apos']))
        if trem:
            o.play('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', m, t, d, v, None, 0.5)
        elif part in ('nib', 'pluck'):                          # hauling the hoard
            if m >= 60:
                o.play('violins' if m >= 67 else 'violas', m, t, d, v, ap, 0.5)
            elif m >= 48:
                o.play('bassoons', m, t, d, v, -0.2, 0.45)
                o.play('violas', m, t, d, v - 6, 0.2, 0.35)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.45)
        elif part == 'gold':                                    # the Gold's call, as it piles up
            o.play('horns', m - 12 if m >= 72 else m, t, d, v + 4, hp, 0.65)
            o.play('trumpets', m, t, d, v - 6, hp, 0.45)
        elif part in ('ring', 'ringbass'):                      # he draws the Ring
            if m >= 60:
                o.play('oboes', m, t, d, v + 4, ap, 0.5)
                o.play('clarinets', m - 12, t, d, v - 4, ap, 0.4)
            else:
                o.play('bassoons', m, t, d, v, ap, 0.5)
                o.play('cellos', m, t, d, v - 4, -0.2, 0.45)
        elif part == 'tutti':                                   # the Nibelungs flee: the whole orchestra
            if m >= 60:
                o.play('violins', m, t, d, v, 0.25, 0.55)
                if m >= 74:
                    o.play('piccolo' if m >= 81 else 'flutes', m, t, 0.1, v - 8, -0.4, 0.4)
            elif m >= 48:
                o.play('horns' if d >= 0.3 else 'violas', m, t, d, v, -0.25, 0.55)
                if d >= 0.3:
                    o.play('trombones', m, t, d, v - 6, 0.1, 0.45)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.45)
                if d >= 0.4:
                    o.play('tuba', m, t, d, v - 6, 0.0, 0.45)
        elif part in ('boast', 'boastharm'):                    # the boast: trombones and tubas
            if part == 'boast':
                o.play('trombones', m if m >= 45 else m + 12, t, d, v + 6, ap, 0.75)
                o.play('tuba', m if m < 50 else m - 12, t, d, v, ap, 0.6)
            elif m >= 55:
                o.play('violins', m, t, d, v, ap, 0.5)
            else:
                o.play('cellos', m, t, d, v, ap, 0.5)
        elif part in ('ringlow', 'goldlow'):
            o.play('horns' if part == 'goldlow' else 'clarinets', m, t, d, v, ap, 0.5)
        elif part in ('loge', 'logefire', 'sly'):               # Loge flatters
            lp = pan_at(np.interp(t, C['t'], C['lpos']))
            if part == 'loge':
                o.play('flutes' if m < 79 else 'piccolo', m, t, 0.1, v, lp, 0.45)
                o.play('harp', m, t, d, v - 8, lp, 0.35)
            else:
                o.play('violins', m, t, d, v, lp, 0.55)
                if part == 'sly':
                    o.play('clarinets', m - 12, t, d, v - 6, lp, 0.35)
        else:
            o.play('cellos', m, t, d, v, -0.2, 0.5)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)

    # the stage: the whip, the forges' hammers, the gold landing on the heap
    for k, tc in enumerate(CRACKS):
        ap = pan_at(np.interp(tc, C['t'], C['apos']))
        o._sfx(whoosh(0.35, 800, 6000, 0.9, seed=90 + k)[0], tc - 0.3, 0.6, ap)
        n = int(0.06 * SR)
        o._sfx(o._noise(0, 2000, 10000, 95 + k, n=n) * np.exp(-np.arange(n) / (0.008 * SR)), tc, 1.0, ap)
        M.add('perc', snare.play(120), tc, 0.5, ap)
    anv = [at(G, 'Porch Left', 0.75), at(G, 'Porch Right', 0.4)]
    for k, t in enumerate(sorted(e[0] for e in N if e[4] == 'anvil')):
        o.hit('anvil', t, 92, pitch=float(rng.uniform(-1, 1)), gain=0.3, pan=pan_at(anv[k % 2]))
    for t in np.arange(T_HAUL + 2.0, T_STOP, 0.6):             # each load clinking onto the heap
        o.hit('metal', t + rng.uniform(0, 0.2), int(rng.uniform(40, 64)), pitch=float(rng.uniform(2, 7)),
              gain=0.18, pan=hp)
    # the Ring's power: a great blow and the Nibelungs flying for both ends
    o.hit('cymbal swell', T_BLAST - 2.4, 100, gain=0.45)
    o.boom(T_BLAST, pan_at(np.interp(T_BLAST, C['t'], C['apos'])), 1.0)
    o.hit('crash', T_BLAST, 124, gain=0.6)
    for side, sd in ((-1, 101), (1, 102)):
        o._sfx(whoosh(1.6, 300, 3500, 0.9, seed=sd)[0], T_BLAST + 0.05, 0.8, lambda t, s=side: s * min(0.9, (t - T_BLAST)))
    for tb in BOASTS:                                           # a thud under each boast
        o.hit('timpani', tb, 112, pitch=-6, gain=0.55, pan=pan_at(np.interp(tb, C['t'], C['apos'])))
    o.fire(T_LOGE, D, 0.22, pan=lambda t: pan_at(np.interp(t, C['t'], C['lpos'])), crackle=10.0, seed=15)
