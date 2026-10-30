"""Down to Nibelheim: Wotan and Loge have gone down into the sulphurous fissure in the middle of Porch Front.
The grey mist, the dimmed battlements of Valhalla and the grey gods on Left fade, and yellow-brown vapour boils
up out of the crack until it fills the house. Then the descent, Wagner's second entr'acte: bands of rock stream outward
from the fissure as if the walls were rushing up past us, the Renunciation of Love (Donington 76) sounds low in
the horns with a red throb from the depths on every note, and Wotan's spear (73) goes down its scale in the
trombones and tubas, each step a pair of steel-blue lines a little farther out.

Below, a red glow grows, and out of it comes the Nibelung rhythm: 9/8 in B flat minor, every beat long-short-
long, first in plucked basses, then bassoons and violas, then horns and trombones, while caverns of red-orange
light open along the roof. Anvils join it, three at the forge in the middle of the porch, then nine, then all
eighteen spread over the house, each one throwing a burst of sparks at every stroke. The Ring motif (8) blares
over them in the trombones, and then the orchestra drops out and the eighteen anvils hammer alone: the whole
house is a glowing forge, sparks flying everywhere, a flash of orange on every bar.

It dies down to a smoulder, and in the last quarter Alberich (red) comes in from the far end of Right, dragging
Mime (sickly yellow-green) along by the ear; at every yank Mime squeals on the xylophone and piccolo and flares,
until they stop on Porch Front, right of centre, the cavern glowing round them.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG13'
TITLE = 'Down to Nibelheim'
KIND = 'show'
DESCRIPTION = ('Wotan and Loge climb down through a crack full of sulphur smoke into the caverns of the '
               'Nibelungs, where eighteen anvils ring out together and sparks fly over the whole house. When the '
               'hammering dies away, Alberich comes dragging his brother Mime by the ear.')
VOICEOVER = ('Down through the smoke, deep under the earth, the hammers never stop. '
             'This is Nibelheim, and Alberich is its master now.')

BEAT = 0.5                                  # a quarter note, for the descent
NB = 0.6                                    # a dotted quarter of the Nibelung 9/8
BAR = 3 * NB
RHY = (0.0, 0.5, 2 / 3)                     # long-short-long in each beat: dotted eighth, sixteenth, eighth
T_RENOUNCE = 3.0
T_SPEAR = 10.6
T_RHY = 15.0                                # the Nibelung rhythm begins
NBARS = 27
T_RING = T_RHY + 12 * BAR                   # bar 12: the Ring over the anvils, twice
T_ALONE = T_RHY + 16 * BAR                  # bar 16: the anvils alone
T_BACK = T_RHY + 20 * BAR                   # bar 20: the orchestra again, falling away
T_ALB = 63.0                                # Alberich drags Mime in
TUGS = [64.0, 66.3, 68.6, 70.9, 73.2, 75.4, 77.2]
D = 80.0

NANV = 18
FIGURE = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
          ('Gb4', 'F4', 'Eb4'), ('Db4', 'C4', 'Bb3'), ('C4', 'A3', 'F3')]      # two bars of the Nibelung figure

EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
SPARK = hexc('#ff7a10')
HOT = hexc('#fff0a0')
ROCK = hexc('#4a2408')
RUST = hexc('#6a1c06')
VAPOUR = hexc('#8a6a1c')
SULPHUR = hexc('#a08a20')
STEEL = hexc('#c8d8ff')
GREY = hexc('#8a8c94')
CASTLE = hexc('#a8a490')
MIST = hexc('#7a8494')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
MIME = hexc('#b0d020')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def anvils_in(bar):
    """How many anvils play in bar `bar` of the rhythm."""
    if bar < 4:
        return 0
    if bar < 8:
        return 3
    if bar < 12:
        return 9
    if bar < 20:
        return NANV
    return (12, 6, 3, 0)[min(bar - 20, 3)]


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who is an anvil for 'anvil', the beat for 'nib'."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, 6.0, 'F1', 70, 'sulphur')
    add(0.0, T_RHY + 2.0, 'Bb1', 62, 'trem')
    for t, m, v, d in play('renunciation_broad', T_RENOUNCE, BEAT, -2, 92):
        add(t, d, m, v, 'renounce')
    for t, m, v, d in play('spear', T_SPEAR, BEAT * 0.9, 0, 100):
        add(t, d, m, v, 'spear')

    for bar in range(NBARS):                                # the Nibelung rhythm
        t0 = T_RHY + bar * BAR
        grow = min(1.0, bar / 15)
        fade = 1 - smoothstep(T_BACK - BAR, T_RHY + NBARS * BAR, t0)
        alone = T_ALONE <= t0 < T_BACK
        if bar % 2 == 0:
            add(t0, BAR * 2, 'Bb1', int(80 + 30 * grow * fade), 'pedal')
        for b in range(3):
            fig = FIGURE[(bar % 2) * 3 + b]
            for k, off in enumerate(RHY):
                t = t0 + (b + off) * NB
                acc = (b == 0 and k == 0)
                if not alone:
                    add(t, NB * (0.45, 0.15, 0.3)[k], 'Bb2' if k != 1 else 'F2',
                        int((70 + 40 * grow) * (0.5 + 0.5 * fade)) + 8 * acc, 'pluck')
                    if bar >= 4 and fade > 0.2:
                        add(t, NB * (0.45, 0.15, 0.3)[k], fig[k], int((64 + 44 * grow) * fade) + 8 * acc, 'nib', b)
                    if bar >= 8 and fade > 0.4:
                        add(t, NB * (0.5, 0.17, 0.33)[k] * 0.95, note(fig[k]) - 12, int((80 + 30 * grow) * fade),
                            'brassnib', b)
                for a in range(anvils_in(bar)):
                    v = 124 if alone else (88 + 10 * acc) if bar >= 8 else 80 + 10 * acc
                    add(t, 0.1, 'C4', min(127, v), 'anvil', a)
        if bar >= 8 and not alone and bar < 21:
            add(t0, 0.3, 'Bb1', 100 + 10 * (bar >= 12), 'timp')
        if alone:
            add(t0, 0.3, 'Bb1', 120, 'timp')
    for k in range(2):                                      # the Ring over the anvils, raised to B flat
        for t, m, v, d in play('ring', T_RING + k * 2 * BAR, NB * 2 / 3, 3, 116):
            if m > note('C3'):
                add(t, d, m, v, 'ring')
    add(T_ALONE - 0.6, 0.6, 'C5', 120, 'crash')
    add(T_ALONE, T_BACK - T_ALONE, 'Bb1', 112, 'roar')            # under the anvils: timpani roll, basses, tubas
    add(T_BACK, 0.6, 'C5', 110, 'crash')
    for t, m, v, d in play('ring', T_BACK + 0.4, NB, 3, 82):
        if m > note('C3'):
            add(t, d, m, v, 'mute')

    add(T_ALB - 1.0, D - T_ALB + 1.0, 'Bb1', 74, 'trem')
    for i, tg in enumerate(TUGS):                           # each yank: his grunt, a thud, Mime squealing
        for j, m in enumerate(('Bb2', 'Db3', 'C3')[: 2 + i % 2]):
            add(tg - 0.45 + j * 0.16, 0.18, m, 100, 'grump')
        add(tg, 0.4, 'Bb1', 104, 'yank')
        top = note('Bb5') + (i % 3)
        for j in range(5):
            add(tg + 0.12 + j * 0.06, 0.08, top - 2 * j - (j > 2) * 3, 108 - 4 * j, 'squeal')
        add(tg + 0.12, 0.5, top - 12, 96, 'yelp')
        add(tg + 0.8, 0.5, note('F4') - i % 2, 86, 'whine')
        add(tg + 1.3, 0.6, note('E4') - i % 2, 80, 'whine')
    for j, (b, d, m) in enumerate([(0, 1, 'Bb2'), (1, .5, 'Db3'), (1.5, .5, 'C3'), (2, 2, 'Bb2'), (4, 1, 'F2'),
                                   (5, 3, 'Bb1')]):
        add(TUGS[-1] + 0.8 + b * 0.3, d * 0.3, m, 90 - 3 * j, 'grump')
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
    """Per frame: Alberich and Mime (path distance), and the eighteen anvils' places."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    far = L + 60
    stops = np.linspace(far - 140, at(G, 'Porch Front', 0.6), len(TUGS))
    tgt = np.full((2, F), far + 60)
    rate = np.full((2, F), 4.0)
    m = t >= T_ALB
    tgt[0][m] = far - 40
    for i, tg in enumerate(TUGS):
        m = t >= tg
        tgt[0][m] = stops[i]
        rate[0][m] = 7.0
    alb = follow(tgt[0], rate[0])
    # Mime trails him by the ear, digging in his heels between yanks
    dig = np.zeros(F)
    for i, tg in enumerate(TUGS):
        nxt = TUGS[i + 1] if i + 1 < len(TUGS) else D + 2
        mm = (t >= tg + 0.5) & (t < nxt)
        dig[mm] = 40 * smoothstep(tg + 0.5, nxt, t[mm])
    tgt[1] = alb + 38 + dig
    rate[1] = 9.0
    mime = follow(tgt[1], rate[1])
    mime[t < T_ALB] = far + 100
    # anvils: spread over the house, the first ones at the forge in the middle of the porch
    pos = (np.arange(NANV) + 0.5) / NANV * (L - 120) + 60
    order = np.argsort(np.abs(pos - pf))
    return dict(t=t, apos=alb, mpos=mime, anvil=pos[order])


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    x = np.abs(d - pf)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    fl = Flicker(rng, G.N, 4.0, 11.0)
    cave = 0.5 + 0.5 * smooth_noise(rng, d, 160)
    cave2 = 0.5 + 0.5 * smooth_noise(rng, d, 60)
    pockets = rng.uniform(80, L - 80, 13)
    pw = rng.uniform(35, 90, 13)
    pocket = np.exp(-((d[:, None] - pockets[None, :]) / pw[None, :]) ** 2)        # (N, 13)
    pf_rate = rng.uniform(0.3, 0.9, 13)
    cloud = 0.5 + 0.5 * smooth_noise(rng, d, 120)
    gods = [at(G, 'Left', 0.45), at(G, 'Left', 0.62), at(G, 'Left', 0.85)]

    renounce = np.array([e[0] for e in N if e[4] == 'renounce'])
    spear = [e[0] for e in N if e[4] == 'spear']
    hits = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    bars = np.array([T_RHY + b * BAR for b in range(NBARS)])
    squeals = np.array([tg + 0.12 for tg in TUGS])
    yanks = np.array(TUGS)

    # sparks: every anvil stroke throws a few, flying out from the anvil and cooling from white to orange
    births, p0, vel, life = [], [], [], []
    for th, a, v in hits:
        n = 3 if v < 100 else 5
        births += [th] * n
        p0 += [C['anvil'][a]] * n
        vel += list(rng.choice([-1, 1], n) * rng.uniform(80, 420, n) * (v / 110))
        life += list(rng.uniform(0.35, 0.9, n))
    births, p0, vel, life = map(np.array, (births, p0, vel, life))
    hit_t = np.array([h[0] for h in hits])
    hit_a = np.array([h[1] for h in hits])

    def intensity(t):
        return keys(t, [(0, 0.0), (8, 0.12), (T_RHY, 0.32), (T_RHY + 4 * BAR, 0.42), (T_RHY + 8 * BAR, 0.56),
                        (T_RING, 0.7), (T_ALONE, 0.88), (T_BACK, 0.92), (T_BACK + 4 * BAR, 0.58),
                        (T_ALB, 0.46), (D, 0.44)])

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        I = intensity(t)

        # what is left of the mountain top: the grey mist, Valhalla dimmed on the porch, the grey gods on Left
        top = 1 - smoothstep(0.5, 5.0, t)
        if top > 0:
            fr += light(MIST, top * (0.24 + 0.04 * cloud) * (1 - 0.3 * porch))
            crenel = (np.sin(d / 9.0) > -0.2) * porch
            fr += light(CASTLE, 0.22 * top * crenel)
            for gp, gb in zip(gods, (0.75, 0.45, 0.45)):
                fr += light(GREY, gb * top * np.exp(-((d - gp) / 22) ** 2))

        # the vapour: boils up out of the crack and fills the house, then thins as we go down
        vap = smoothstep(0.0, 5.5, t) * (1 - smoothstep(9.0, 16.0, t))
        if vap > 0:
            reach = 60 + 1500 * smoothstep(0.0, 6.0, t)
            billow = 0.5 + 0.5 * np.cos(2 * np.pi * (x / 260 - 0.35 * t) + 3 * cloud)
            fr += light(VAPOUR, vap * (0.3 + 0.16 * billow) * smoothstep(reach, reach - 300, x))

        fr += light(SULPHUR, 0.7 * (1 - smoothstep(0, 7, t)) * np.exp(-(x / (80 + 50 * t)) ** 2))

        # the descent: strata streaming outward from the fissure, slowing as we reach the bottom
        desc = smoothstep(3.0, 7.0, t) * (1 - smoothstep(T_RHY + 2, T_RHY + 4 * BAR, t))
        if desc > 0:
            ph = 0.9 * min(t, 17.0) - 0.022 * max(0.0, min(t, 17.0) - 5.0) ** 2
            band = 0.5 + 0.5 * np.cos(2 * np.pi * (x / 170 - ph) + 2 * cave2)
            fr += light(ROCK, desc * (0.2 + 0.26 * band ** 2)) + light(RUST, desc * 0.3 * band ** 6)
        ri = int(np.searchsorted(renounce, t, side='right')) - 1
        if ri >= 0 and t - renounce[ri] < 1.5:
            fr += light(ALB, 0.6 * np.exp(-(t - renounce[ri]) / 0.45) * np.exp(-(x / 110) ** 2))
        for k, ts in enumerate(spear):
            if ts <= t < ts + 2.0:
                r = 60 + 95 * k
                g = 0.9 * np.exp(-(t - ts) / 0.5) * np.exp(-((x - r) / 9) ** 2)
                fr += light(STEEL, g)

        # Nibelheim: red-orange caverns, opening and glowing with the rhythm
        if I > 0:
            fr += light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
            pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
            fr += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)))
            fr += light(FORGE, 0.3 * smoothstep(T_ALONE - 1, T_ALONE, t) * (1 - smoothstep(T_BACK, T_BACK + 3, t)) * (0.7 + 0.3 * cave2))
            bi = int(np.searchsorted(bars, t, side='right')) - 1
            if 0 <= bi < NBARS and t - bars[bi] < 1.0:
                age = t - bars[bi]
                if T_ALONE <= bars[bi] < T_BACK:
                    fr += light(FORGE, 0.62 * np.exp(-age / 0.16) * np.ones(G.N))
                    fr += light(HOT, 0.38 * np.exp(-age / 0.08) * np.ones(G.N))
                elif bars[bi] >= T_RHY + 8 * BAR:
                    fr += light(FORGE, 0.3 * I * np.exp(-age / 0.2) * (0.5 + 0.5 * cave))

        # the anvils: a white-hot point at each stroke
        lo, hi = np.searchsorted(hit_t, t - 0.25), np.searchsorted(hit_t, t, side='right')
        if hi > lo:
            ages = t - hit_t[lo:hi]
            ap_ = C['anvil'][hit_a[lo:hi]]
            g = (np.exp(-((d[:, None] - ap_[None, :]) / 13) ** 2) * np.exp(-ages / 0.07)[None, :]).max(axis=1)
            fr += light(HOT, 0.95 * g)
        # sparks
        lo, hi = np.searchsorted(births, t - 0.95), np.searchsorted(births, t, side='right')
        if hi > lo:
            age = t - births[lo:hi]
            alive = age < life[lo:hi]
            if alive.any():
                age = age[alive]
                q = p0[lo:hi][alive] + vel[lo:hi][alive] * 0.35 * (1 - np.exp(-age / 0.35))
                heat = np.clip(1 - age / life[lo:hi][alive], 0, 1)
                g = np.exp(-((d[:, None] - q[None, :]) / 7) ** 2)
                fr += light(SPARK, (g * heat[None, :]).max(axis=1))
                fr += light(HOT, 0.7 * (g * (heat ** 3)[None, :]).max(axis=1))
        if t > T_RHY:                                       # stray forge sparks, always
            sp = rng.random(G.N) < 0.006 * (0.5 + I)
            fr += light(SPARK, 0.7 * sp)

        # Alberich dragging Mime by the ear
        ap, mp = C['apos'][f], C['mpos'][f]
        if t >= T_ALB - 0.5:
            yi = int(np.searchsorted(yanks, t, side='right')) - 1
            jolt = np.exp(-(t - yanks[yi]) / 0.22) if yi >= 0 and t - yanks[yi] < 1.5 else 0.0
            si = int(np.searchsorted(squeals, t, side='right')) - 1
            sq = np.exp(-(t - squeals[si]) / 0.3) if si >= 0 and t - squeals[si] < 2 else 0.0
            fr += light(MUD, 0.38 * np.exp(-((d - ap) / 120) ** 2) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, (0.75 + 0.25 * jolt) * np.exp(-((d - ap) / (24 + 8 * jolt)) ** 2) * (1 + 0.15 * smoulder(t)))
            body = np.exp(-((d - mp) / (15 + 8 * sq)) ** 2)
            fr += light(MIME, (0.66 + 0.34 * sq) * body + 0.25 * np.exp(-((d - mp) / 60) ** 2))
            fr += light(WHITE, 0.55 * sq * body * (tw(t) > 0))
            grip = (d > min(ap, mp)) & (d < max(ap, mp))
            fr += light(ALB, 0.3 * grip)
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
    pf = pan_at(at(G, 'Porch Front', 0.5))
    apan = [pan_at(p) for p in C['anvil']]
    apitch = [(-5, 0, 4)[a % 3] + 0.3 * (a % 5) for a in range(NANV)]     # three sizes of anvil

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.17, 0.3), ('low', 0.22, 0.15), ('brass', 0.18, 0.3), ('winds', 0.17, 0.3),
                            ('anvil', 0.085, 0.2), ('perc', 0.18, 0.25), ('fx', 0.1, 0.3), ('mime', 0.16, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vcp = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    bst = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    hst = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tbst = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Long*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    gong = M.hits('Percussion/gongscrape_mf.wav')

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

    jit = np.random.default_rng(5)
    for t, d, m, v, part, who in compose():
        if part == 'sulphur':
            M.add('perc', swell.play(80), t, 0.7, pf)
            M.add('perc', gong.play(90), t + 0.5, 0.8, pf)
            hold('low', trem, m + 12, t, t + d, v, pf, rise=0.5, fall=2.0, gain=0.6)
        elif part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=2.0, fall=2.0, gain=0.55)
            hold('low', cb, m, t, t + d, v - 10, 0.0, rise=3.0, fall=2.0, gain=0.5)
        elif part == 'renounce':
            M.add('brass', horn.play(m, v, dur=d, release=0.5), t, 0.9, pf - 0.15)
            M.add('low', bsus.play(m - 12, v - 10, dur=d, release=0.5), t, 0.6, pf + 0.15)
        elif part == 'spear':
            k = int(round((t - T_SPEAR) / (BEAT * 0.9)))
            sp = 0.08 * k
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.9, pf - sp)
            M.add('low', tuba.play(m - 12, v - 6, dur=d, release=0.3), t, 0.8, pf + sp)
        elif part == 'pedal':
            M.add('low', pizz.play(m + 12, v), t, 1.0, 0.0)
            hold('low', cb, m, t, t + d, max(40, v - 40), 0.0, rise=0.3, fall=0.4, gain=0.45)
        elif part == 'pluck':
            M.add('low', pizz.play(m, v), t, 0.7, -0.15)
            M.add('strings', vcp.play(m, v - 10), t, 0.5, 0.15)
        elif part == 'nib':
            M.add('winds', bst.play(m - 12, v), t, 0.8, -0.25)
            M.add('strings', vas.play(m, v - 6, dur=d, release=0.05), t, 0.55, 0.25)
        elif part == 'brassnib':
            M.add('brass', (hst if m >= note('F3') else tbst).play(m + 12, v), t, 0.55, -0.1)
            M.add('brass', tbst.play(m, v - 8), t, 0.5, 0.1)
        elif part == 'anvil':
            M.add('anvil', anvil.play(v, pitch=apitch[who]), t + jit.uniform(0, 0.012), 1.0, apan[who])
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, pf)
        elif part == 'ring':
            M.add('brass', tbn.play(m - 12, v, dur=d, release=0.3), t, 0.8, pf - 0.2)
            M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.8, pf + 0.2)
        elif part == 'mute':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.8, pf)
        elif part == 'roar':
            for k in range(int(d / 1.5) + 1):
                M.add('perc', roll.play(v, dur=1.8), t + 1.5 * k, 0.8, pf)
            hold('low', trem, m + 12, t, t + d, v, -0.2, rise=0.4, fall=0.6, gain=0.9)
            hold('low', tuba, m + 12, t, t + d, v - 10, 0.2, rise=0.4, fall=0.6, gain=0.8)
            hold('low', cb, m, t, t + d, v, 0.0, rise=0.4, fall=0.6, gain=0.7)
            M.add('perc', swell.play(100), t + d - 4.5, 0.7, 0.0)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.8, 0.0)
        elif part == 'grump':
            p = pan_of('apos', t)
            M.add('low', bsus.play(m, v, dur=d, release=0.1), t, 0.9, p)
            M.add('low', tbst.play(m + 12, v - 20), t, 0.4, p)
        elif part == 'yank':
            p = pan_of('apos', t)
            M.add('perc', timp.play(v, pitch=-6), t, 0.7, p)
            M.add('low', pizz.play(m + 12, v), t, 0.9, p)
            M.add('fx', whoosh(0.35, 800, 3000, 0.4, seed=int(t * 10)), t - 0.2, 0.6, p)
        elif part == 'squeal':
            p = pan_of('mpos', t)
            M.add('mime', xylo.play(m - 12, v), t, 0.9, p)
            M.add('mime', pic.play(m, v - 16), t, 0.45, p)
        elif part == 'yelp':
            M.add('mime', ob.play(m, v), t, 0.8, pan_of('mpos', t))
        elif part == 'whine':
            M.add('mime', bst.play(m - 12, v), t, 0.8, pan_of('mpos', t))
