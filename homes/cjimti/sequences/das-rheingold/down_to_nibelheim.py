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

The music is Wagner's own, the entr'acte from Scene 2 to Scene 3 of Das Rheingold as Solti's 1958 Vienna
Philharmonic recording takes it: the end of the descent and the Nibelung rhythm emerging (bars 1826-1839), the
Ring over it and the eighteen anvils, alone at their height (1846-1877), the orchestra's return (1888-1893),
and the start of Scene 3, Alberich hauling Mime in ("Hehe! Hehe! Hieher! Tückischer Zwerg!", 1900-1909). The
notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the rhythm in the basses, cellos
and bassoons, the figure in the violas and horns, the Ring blaring in the trombones and trumpets, Alberich on
bassoons and low brass. The anvils are in Wagner's score, and here they are real anvils, three, then nine, then
eighteen, striking the rhythm, panned to their places on the house. Like a staged production it adds sulphur
hissing out of the fissure, a deep rush as the walls stream past, and a thud each time Alberich yanks Mime.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'RG13'
TITLE = 'Down to Nibelheim'
KIND = 'show'
DESCRIPTION = ('Wotan and Loge climb down through a crack full of sulphur smoke into the caverns of the '
               'Nibelungs, where eighteen anvils ring out together and sparks fly over the whole house. When the '
               'hammering dies away, Alberich comes dragging his brother Mime by the ear.')
VOICEOVER = ('Down through the smoke, deep under the earth, the hammers never stop. '
             'This is Nibelheim, and Alberich is its master now.')

EX = excerpt(__file__)                      # bars 1826-1839, 1846-1877, 1888-1893, 1900-1909
BARS_ = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_RHY = BARS_[1830]                         # the Nibelung rhythm begins
T_NINE = BARS_[1846]                        # nine anvils
T_RING = BARS_[1852]                        # the Ring over all eighteen
T_ALONE = BARS_[1862]                       # the anvils alone
T_BACK = BARS_[1878]                        # the orchestra again
T_ALB = BARS_[1900] - 1.0                   # Alberich drags Mime in
BARS = [t for m, t in sorted(BARS_.items()) if T_RHY <= t < T_ALB]   # every bar of the rhythm, for the flashes
NANV = 18

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


def anvils_at(t):
    """How many anvils strike at time t."""
    if t < T_RHY + 3.0:
        return 0
    if t < T_NINE:
        return 3
    if t < T_RING:
        return 9
    if t < T_ALONE + 16.0:
        return NANV
    if t < T_BACK:
        return (12, 6, 3)[min(2, int((t - T_ALONE - 16.0) / 2.5))]
    return 0


def tugs():
    """Each yank of Mime's ear: on Alberich's accents."""
    return accents(EX['notes'], T_ALB + 1.0, D - 0.5, 60, 2, 1.2)[:7]


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who, tremolo). Before the rhythm the
    right hand is the Renunciation's red throb ('renounce'), the left hand's long notes the spear's steps ('spear');
    the rhythm's repeated F's are 'pluck', the anvils strike with them ('anvil', who = the anvil); the right hand
    is the figure ('nib'), the Ring over the anvils 'ring', the left hand 'brassnib'; the orchestra's return is
    'back'; Alberich's bars 'alb'. 'yank' and 'squeal' mark Mime's moments."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes'], least=10 ** 6):    # the rhythm's repeated notes stay notes
        if t < T_RHY:
            part = 'renounce' if h == 0 else ('spear' if d >= 0.4 else 'low')
        elif t >= T_ALB:
            part = 'alb'
        elif t >= T_BACK:
            part = 'back'
        elif h == 1 and d < 0.1:
            part = 'pluck'                                  # the low F's rolling under it all
        elif h == 0:
            part = 'ring' if T_RING <= t < T_ALONE and d >= 0.25 else 'nib'
        else:
            part = 'brassnib'
        N.append((t, d, m, v, part, None, trem))
    # the anvils strike the Nibelung rhythm: the right hand's onsets (in the anvils' bars it is written for them)
    strokes = []
    for t in sorted({round(n[0], 3) for n in EX['notes'] if n[4] == 0 and n[1] <= 0.3}):
        if T_RHY + 3.0 <= t < T_BACK and (not strokes or t - strokes[-1] >= 0.06):
            strokes.append(t)
    for t in strokes:
        alone = T_ALONE <= t < T_BACK
        for a in range(anvils_at(t)):
            N.append((t, 0.1, 72, 124 if alone else 96, 'anvil', a, False))
    for tg in tugs():
        N.append((tg, 0.4, 34, 0, 'yank', None, False))
        N.append((tg + 0.12, 0.5, 82, 0, 'squeal', None, False))
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
    TUGS = tugs()
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
    bars = np.array(BARS)
    squeals = np.array([tg + 0.12 for tg in tugs()])
    yanks = np.array(tugs())

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
        return keys(t, [(0, 0.06), (T_RHY - 2, 0.2), (T_RHY, 0.32), (T_RHY + 8, 0.42), (T_NINE, 0.56),
                        (T_RING, 0.7), (T_ALONE, 0.88), (T_BACK - 6, 0.92), (T_BACK, 0.7), (T_BACK + 4, 0.8),
                        (T_ALB, 0.5), (D, 0.46)])

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        I = intensity(t)

        # what is left of the mountain top: the grey mist, Valhalla dimmed on the porch, the grey gods on Left
        top = 1 - smoothstep(0.2, 2.5, t)
        if top > 0:
            fr += light(MIST, top * (0.24 + 0.04 * cloud) * (1 - 0.3 * porch))
            crenel = (np.sin(d / 9.0) > -0.2) * porch
            fr += light(CASTLE, 0.22 * top * crenel)
            for gp, gb in zip(gods, (0.75, 0.45, 0.45)):
                fr += light(GREY, gb * top * np.exp(-((d - gp) / 22) ** 2))

        # the vapour: boils up out of the crack and fills the house, then thins as we go down
        vap = smoothstep(0.0, 2.5, t) * (1 - smoothstep(6.0, 12.0, t))
        if vap > 0:
            reach = 60 + 1500 * smoothstep(0.0, 3.5, t)
            billow = 0.5 + 0.5 * np.cos(2 * np.pi * (x / 260 - 0.35 * t) + 3 * cloud)
            fr += light(VAPOUR, vap * (0.3 + 0.16 * billow) * smoothstep(reach, reach - 300, x))

        fr += light(SULPHUR, 0.7 * (1 - smoothstep(0, 5, t)) * np.exp(-(x / (80 + 70 * t)) ** 2))

        # the descent: strata streaming outward from the fissure, slowing as we reach the bottom
        desc = smoothstep(1.0, 3.0, t) * (1 - smoothstep(T_RHY + 2, T_RHY + 8, t))
        if desc > 0:
            ph = 0.9 * min(t, 17.0) - 0.022 * max(0.0, min(t, 17.0) - 5.0) ** 2
            band = 0.5 + 0.5 * np.cos(2 * np.pi * (x / 170 - ph) + 2 * cave2)
            fr += light(ROCK, desc * (0.2 + 0.26 * band ** 2)) + light(RUST, desc * 0.3 * band ** 6)
        ri = int(np.searchsorted(renounce, t, side='right')) - 1
        if ri >= 0 and t - renounce[ri] < 1.5:
            fr += light(ALB, 0.6 * np.exp(-(t - renounce[ri]) / 0.45) * np.exp(-(x / 110) ** 2))
        for k, ts in enumerate(spear):
            if ts <= t < ts + 2.0:
                r = 60 + 95 * (k % 8)
                g = 0.9 * np.exp(-(t - ts) / 0.5) * np.exp(-((x - r) / 9) ** 2)
                fr += light(STEEL, g)

        # Nibelheim: red-orange caverns, opening and glowing with the rhythm
        if I > 0:
            fr += light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
            pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
            fr += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)))
            fr += light(FORGE, 0.3 * smoothstep(T_ALONE - 1, T_ALONE, t) * (1 - smoothstep(T_BACK, T_BACK + 3, t)) * (0.7 + 0.3 * cave2))
            bi = int(np.searchsorted(bars, t, side='right')) - 1
            if 0 <= bi < len(bars) and t - bars[bi] < 1.0:
                age = t - bars[bi]
                if T_ALONE <= bars[bi] < T_BACK:
                    fr += light(FORGE, 0.62 * np.exp(-age / 0.16) * np.ones(G.N))
                    fr += light(HOT, 0.38 * np.exp(-age / 0.08) * np.ones(G.N))
                elif bars[bi] >= T_NINE:
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
    """Wagner's notes, orchestrated from the piano reduction, with real anvils striking the rhythm."""
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(min(max(dd, 0), G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=2.6)
    # the sulphur and the rushing walls lead the descent; the effects sit back under the rhythm and the Ring
    o.effects([(0.0, 0.0), (T_RHY, 0.0), (T_RHY + 2.0, -6.0), (T_ALB, -6.0), (T_ALB + 0.5, -2.0), (D, -2.0)])
    N = compose()
    anv = [(t, a, v) for t, d, m, v, part, a, trem in N if part == 'anvil']
    rng = np.random.default_rng(13)
    for t, d, m, v, part, who, trem in N:
        if v == 0 or part == 'anvil':
            continue
        if trem:
            o.play('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', m, t, d, v, None, 0.5)
        elif part == 'renounce':
            o.play('horns', m, t, d, v + 4, -0.2, 0.7)
            o.play('violas', m, t, d, v - 6, 0.2, 0.35)
        elif part in ('spear', 'low'):
            o.play('trombones' if m >= 45 else 'tuba', m, t, d, v + 4, 0.0, 0.7)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.45)
        elif part == 'pluck':                                   # the Nibelung rhythm
            if m < 48:
                o.play('cellos', m, t, 0.1, v + 6, -0.25, 0.55)
                o.play('basses', m if m < 40 else m - 12, t, 0.1, v, 0.25, 0.5)
            else:
                o.play('bassoons', m, t, 0.1, v, 0.2, 0.4)
                o.play('violas', m, t, 0.1, v - 4, -0.2, 0.35)
        elif part == 'nib':
            o.play('violas' if m < 62 else 'violins', m, t, d, v, 0.25, 0.5)
            if d >= 0.3 and t >= T_NINE:
                o.play('horns', m, t, d, v - 6, -0.25, 0.45)
        elif part == 'ring':                                    # the Ring blares over the anvils
            o.play('trombones', m - 12 if m >= 65 else m, t, d, v + 6, 0.1, 0.75)
            o.play('trumpets', m, t, d, v - 4, -0.15, 0.5)
        elif part == 'brassnib':
            o.play('horns' if d >= 0.3 else 'cellos', m if m >= 45 else m + 12, t, d, v, -0.2, 0.55)
            if m < 45 and d >= 0.3:
                o.play('tuba', m, t, d, v - 6, 0.0, 0.5)
        elif part == 'back':                                    # the orchestra returns, full
            if m >= 60:
                o.play('violins', m, t, d, v, 0.25, 0.55)
                o.play('trumpets' if d >= 0.3 else 'flutes', m, t, d, v - 8, -0.2, 0.4)
            elif m >= 48:
                o.play('horns', m, t, d, v, -0.25, 0.6)
                o.play('trombones', m, t, d, v - 6, 0.1, 0.45)
            else:
                o.play('tuba', m, t, d, v, 0.0, 0.6)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.5)
        elif part == 'alb':                                     # Alberich hauling Mime
            ap = pan_at(np.interp(t, C['t'], C['apos']))
            if m >= 55:
                o.play('violas' if d < 0.3 else 'clarinets', m, t, d, v, ap, 0.5)
            else:
                o.play('bassoons', m, t, d, v, ap, 0.55)
                o.play('cellos', m, t, d, v - 4, ap, 0.45)
                if d >= 0.4:
                    o.play('trombones', m, t, d, v - 8, ap, 0.4)

    # the anvils: each stroke rings from the anvils playing, panned to their places; a few samples a stroke
    strokes = {}
    for t, a, v in anv:
        strokes.setdefault(round(t, 3), []).append((a, v))
    for t, who in sorted(strokes.items()):
        n = len(who)
        pick = rng.choice(n, min(n, 4), replace=False)
        for j in pick:
            a, v = who[j]
            o.hit('anvil', t + rng.uniform(0, 0.012), int(min(127, v)), pitch=float(rng.uniform(-1.5, 1.5)),
                  gain=0.32 * np.sqrt(n) / np.sqrt(len(pick)) / np.sqrt(4), pan=pan_at(C['anvil'][a]))
    # the stage: sulphur out of the fissure, the walls rushing past, the yanks
    o._sfx(o._noise(0, 900, 6000, 131, n=int(5 * SR)) * np.sin(np.linspace(0, np.pi, int(5 * SR))) ** 2, 0.0,
           0.35, pf)
    o._sfx(whoosh(6.0, 200, 60, 0.9, seed=132)[0], 0.5, 0.9, pf)
    o.hit('cymbal swell', T_ALONE - 2.2, 96, gain=0.4)
    o.hit('crash', T_ALONE, 118, gain=0.5)
    o.hit('timpani roll', T_ALONE, 110, pitch=-5, gain=0.5)
    o.hit('crash', T_BACK, 112, gain=0.45)
    for tg in tugs():
        mp = pan_at(np.interp(tg, C['t'], C['mpos']))
        o.hit('timpani', tg, 100, pitch=-4, gain=0.35, pan=mp)
        o.hoof(tg + 0.02, mp, 90, 0.8)
