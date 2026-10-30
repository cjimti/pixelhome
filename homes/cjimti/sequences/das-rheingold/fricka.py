"""Fricka: the castle stands gleaming across the porch, the meadow lies in dawn light on the wings, and Wotan
(deep blue) and Fricka (rose silver) stand on Left. She rounds on him: the price of the castle is her own
sister Freia, promised to the giants who built it. The argument takes the whole house. Her rose floods in
from the far ends of both wings and his blue holds the ground by the castle, and the front between them
surges back and forth, sparking where they meet, each of her outbursts shoving the rose toward the porch.

The music is Wagner's own, as Solti's 1958 Vienna Philharmonic recording takes it: Fricka's outburst "O
lachend frevelnder Leichtsinn!" and her reproaches up to "Freia, mein holdes Geschwister" (bars 844-855); her
longing for a home that would keep him by her, "Um des Gatten Treue besorgt" (864-869); and Wotan's answer
over the treaty motif's long scales, "Um dich zum Weib zu gewinnen, mein eines Auge setzt' ich werbend daran"
(902-906). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): her reproaches
on violins over driving cellos and basses, oboes doubling her line; her longing on violas and oboe over a harp
and cellos; the treaty scales on trombones, tuba and basses with the horns above, and a blow of his spear's
shaft as the line strikes out.

While she longs for her home the front melts into a wide mauve blend and she comes close to him; then the
treaty scales draw his spear out from him toward the castle, a steel white-blue line that grows a step for
every note, the treaties glinting along it, and her rose drains back out of the wings while she steps away.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt

CODE = 'RG07'
TITLE = 'Fricka'
KIND = 'show'
DESCRIPTION = ('Fricka reminds Wotan what the castle cost: her sister Freia, promised to the giants as their '
               'wages. Watch their colours fight for the house, his blue against her rose, until he lays down '
               'the law with his spear.')
VOICEOVER = ('Fricka has a question for her husband. The castle is finished, so who exactly is going to pay '
             'for it?')

EX = excerpt(__file__)                      # bars 844-855, 864-869, 902-906, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
SEG = [sg['start'] for sg in EX['segments']] + [EX['seconds']]
BEAT = 0.5
REPROACH = [BAR[844], BAR[849], BAR[853]]   # her outbursts, each a shove of rose
T_HOME = SEG[1]                             # her longing: a home to keep him by her
T_SHRUG = SEG[2] - 1.5
T_SPEAR = SEG[2]                            # the treaties' scales: his spear
T_UNEASE = SEG[3] - 7.0
D = EX['seconds']
LEVEL = 4.0

WOTAN, FRICKA = 0, 1
BLUE = hexc('#1a3cff')
ROSE = hexc('#ff9ad0')
MAUVE = hexc('#a050e0')
STEEL = hexc('#c8d8ff')
STONE = hexc('#fff0c0')
DAWN_HI = hexc('#6a5a8a')
GLOW = hexc('#ff9070')
NEAR = hexc('#a05a96')
FAR = hexc('#2638a0')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Her reproaches are 'fricka'
    (the right hand) over 'drive' (the left); her longing is 'home' over 'hpad'; the treaty scales are 'spear'
    (the left hand, WOTAN) with 'treaty2' above."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_HOME:
            N.append((t, d, m, v, 'fricka' if h == 0 else 'drive', FRICKA if h == 0 else None))
        elif t < T_SPEAR:
            N.append((t, d, m, v, 'home' if h == 0 else 'hpad', FRICKA if h == 0 else None))
        else:
            N.append((t, d, m, v, 'spear' if h == 1 else 'treaty2', WOTAN))
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def push(t):
    """Who holds the wings: 0 all his blue, 1 all her rose (fraction of each wing from its far end)."""
    marks = [(0.0, 0.05)]
    for k, t0 in enumerate(REPROACH):
        marks += [(t0 + 0.2, (0.35, 0.5, 0.7)[k] - 0.1), (t0 + 1.2, (0.35, 0.5, 0.7)[k] + 0.1),
                  (t0 + 4.2, (0.35, 0.5, 0.7)[k])]
    marks += [(T_HOME, 0.68), (T_HOME + 6, 0.55), (T_SHRUG, 0.52), (T_SPEAR, 0.8), (T_SPEAR + 9.0, 0.15),
              (D, 0.12)]
    ts, us = zip(*marks)
    return np.interp(t, ts, us)


def choreography(G):
    """Per frame: where Wotan and Fricka are, and how far her rose has pushed into each wing."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    W, Fr = at(G, 'Left', 0.7), at(G, 'Left', 0.45)
    set_(WOTAN, 0, D, W + 4.3 * np.sin(2 * np.pi * (t + 80) / 5.0 - 1.12), 8.0)     # his sway, as RG06 left it
    set_(FRICKA, 0, D, Fr, 3.0)
    for k, t0 in enumerate(REPROACH):                                           # stepping at him
        set_(FRICKA, t0, t0 + 4.4, Fr + 25 + 12 * k, 4.0)
    set_(FRICKA, T_HOME + 2, T_SHRUG, W - 35, 0.6)                             # close to him
    set_(WOTAN, T_SHRUG, D, at(G, 'Left', 0.75), 1.2)                          # he turns away
    set_(FRICKA, T_SPEAR, D, Fr - 15, 1.0)                                     # and she steps back
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    u = follow(push(t), np.full(F, 4.0))
    return dict(t=t, pos=pos, push=u)


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    p0, p1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    L0, R0 = at(G, 'Left', 1.0), at(G, 'Right', 0.0)
    reach = np.maximum(np.abs(d - pf), 1)
    merlon = smoothstep(0.25, 0.55, 0.5 + 0.5 * np.cos(2 * np.pi * (d - pf) / 46))
    stone = 0.88 + 0.12 * np.random.default_rng(6).uniform(-1, 1, G.N)        # the same stones as RG06
    walls = smoothstep(700, 580, reach) * porch
    far = np.clip(np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0)) / 520, 0, 1)
    sky = 0.4 * DAWN_HI[None, :] + 0.6 * (NEAR[None, :] * (1 - far[:, None]) + FAR[None, :] * far[:, None])
    # each wing as 0 at the castle .. 1 at its far end; her rose holds the far part
    wfrac = np.where(d <= L0, 1 - d / L0, np.where(d >= R0, (d - R0) / (G.length - R0), -1.0))
    who = {'Wotan': WOTAN, 'Fricka': FRICKA}
    sung = {k: np.array(sorted(x[0] for x in EX['singing'] if who.get(x[2]) == k) +
                        accents([e for e in N if e[5] == k], n=2, space=0.6, vmin=80)) for k in (WOTAN, FRICKA)}
    sung = {k: np.sort(v) for k, v in sung.items()}
    shoves = np.array(accents([e for e in N if e[4] in ('fricka', 'drive')], n=3, space=0.8, vmin=85))
    spear = np.array(sorted({round(e[0], 3) for e in N if e[4] == 'spear'}))
    treaty2 = np.array(accents([e for e in N if e[4] == 'treaty2'], n=1, space=0.4))
    tw = Flicker(rng, G.N, 0.3, 1.2)
    grass = Flicker(rng, G.N, 0.1, 0.5)
    edge_n = Flicker(rng, G.N, 1.5, 4.0)

    for f in range(F):
        t = f * DT
        tt = t + 80
        fr = np.zeros((G.N, 3))
        wp = C['pos'][WOTAN][f]
        argue = smoothstep(1.0, 4.0, t) * (1 - smoothstep(T_UNEASE - 2, T_UNEASE + 6, t))
        warmth = smoothstep(T_HOME, T_HOME + 4, t) * (1 - smoothstep(T_SHRUG - 1, T_SHRUG + 1.5, t))

        # the meadow at dawn and the castle behind (as RG06 left them)
        roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.04 * tt))
        bed = (0.34 * (0.85 + 0.1 * roll + 0.05 * grass(t)) * (wing + 0.6 * porch))
        fr += light(sky, bed * (1 - 0.6 * argue * wing))
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.02 * tt))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.035 * tt) + 1)
        cloud = smoothstep(0.35, 1.0, c1 * c2)
        fr += light(DAWN_HI, 0.3 * cloud * wing * (1 - argue))
        fr += light(GLOW, (0.12 + 0.16 * cloud) * np.exp(-((d - pf) / 750) ** 2) * (0.9 + 0.1 * roll))
        gleam = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - p0) / 260 - 0.18 * tt))
        castle = 0.82 - 0.15 * argue + 0.12 * warmth
        fr += light(STONE, castle * walls * stone * (0.42 + 0.58 * merlon) * (0.85 + 0.15 * gleam ** 4))
        fr += light(WHITE, 0.35 * walls * merlon * gleam ** 12 * (0.7 + 0.3 * tw(t)))

        # the argument: her rose from the far ends, his blue from the castle, a sparking front between
        if argue > 0:
            u = C['push'][f]
            edge = 0.035 + 0.1 * warmth
            front = (1 - u) + 0.025 * edge_n(t)
            rose = smoothstep(front - edge, front + edge, wfrac) * (wfrac >= 0)
            blue = (1 - rose) * (wfrac >= 0)
            seam = np.exp(-((wfrac - front) / (0.03 + 0.12 * warmth)) ** 2) * (wfrac >= 0)
            si = int(np.searchsorted(shoves, t, side='right')) - 1
            jolt = np.exp(-(t - shoves[si]) / 0.2) if si >= 0 and t - shoves[si] < 1 else 0.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (wfrac * 6 + 0.6 * t))
            fr += light(ROSE, argue * (0.46 + 0.12 * wave + 0.15 * jolt) * rose * (1 - 0.6 * warmth * seam))
            fr += light(BLUE, argue * (0.42 + 0.1 * (1 - wave)) * blue * (1 - 0.6 * warmth * seam))
            fr += light(MAUVE, argue * 0.6 * warmth * seam)
            fr += light(WHITE, argue * (1 - warmth) * (0.25 + 0.45 * jolt) * seam ** 4 * (0.6 + 0.4 * tw(t)))

        # the spear: a steel line drawn out from him toward the castle, a step for every note
        if t >= T_SPEAR - 0.1:
            n = int(np.searchsorted(spear, t, side='right'))
            if n > 0:
                grown = (n - 1 + smoothstep(spear[n - 1], spear[n - 1] + 0.25, t)) / len(spear)
                tip = wp + (pf - 60 - wp) * grown
                fade = 1 - smoothstep(T_UNEASE, T_UNEASE + 4, t)
                shaft = smoothstep(wp - 10, wp + 10, d) * smoothstep(tip + 12, tip - 12, d)
                ti = int(np.searchsorted(treaty2, t, side='right')) - 1
                rune = 0.0
                if ti >= 0 and t - treaty2[ti] < 1.5:   # the treaties glinting along it
                    q = wp + (tip - wp) * ((ti * 0.37) % 1)
                    rune = np.exp(-((d - q) / 20) ** 2) * np.exp(-(t - treaty2[ti]) / 0.4)
                hit = np.exp(-(t - spear[n - 1]) / 0.25)
                fr += light(STEEL, fade * (0.75 * shaft + 0.6 * hit * np.exp(-((d - tip) / 18) ** 2)))
                fr += light(WHITE, fade * (0.8 * rune + 0.3 * hit * shaft))
                if t < T_SPEAR + 1.2:
                    fr += light(STEEL, 0.5 * np.exp(-(t - T_SPEAR) / 0.3) * np.ones(G.N) * wing)

        # the two of them
        for k, col in ((WOTAN, BLUE), (FRICKA, ROSE)):
            p = C['pos'][k][f]
            arr = sung[k]
            i = int(np.searchsorted(arr, t, side='right')) - 1
            flare = np.exp(-(t - arr[i]) / 0.25) if i >= 0 and t - arr[i] < 1.2 else 0.0
            b = 0.78 + 0.25 * flare
            fr += light(col, b * np.exp(-((d - p) / (28 + 6 * flare)) ** 2) + 0.35 * b * np.exp(-((d - p) / 130) ** 2))
            fr += light(WHITE, 0.35 * flare * np.exp(-((d - p) / 12) ** 2))
        fr += light(BLUE, 0.32 * (1 - argue) * np.exp(-((d - wp) / 260) ** 2) * wing)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes: her reproaches on violins over driving low strings, her longing on violas and oboe over
    harp and cellos, the treaty scales on trombones and tuba; a blow of the spear's shaft as it strikes out."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pfr = lambda t: pan_at(np.interp(t, C['t'], C['pos'][FRICKA]))
    pw = lambda t: pan_at(np.interp(t, C['t'], C['pos'][WOTAN]))
    o = Orchestra(M, level=LEVEL)
    for t, d, m, v, part, who in compose():
        if part == 'fricka':                                # her reproaches: violins, oboe on the top line
            o.play('violins' if m >= 55 else 'violas', m, t, d, v, pfr(t) + 0.2, 0.55)
            if d >= 0.2 and m >= 64:
                o.play('oboes', m, t, d, v - 6, pfr(t), 0.45)
        elif part == 'drive':                               # driving under her
            o.play('cellos', m, t, d, v + 4, -0.2, 0.6)
            if m < 48:
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 4, 0.2, 0.45)
        elif part == 'home':                                # her longing
            o.play('violas', m, t, d, v + 6, pfr(t), 0.7)
            if d >= 0.3:
                o.play('oboes', m, t, d, v, pfr(t), 0.5)
        elif part == 'hpad':
            o.play('harp', m, t, d, v + 4, pfr(t) - 0.3, 0.5)
            o.play('cellos', m, t, max(d, 0.3), v - 6, -0.2, 0.35)
        elif part == 'spear':                               # the treaty scales: his spear
            o.play('trombones', m + 12 if m < 45 else m, t, d, v + 14, pw(t), 0.75)
            o.play('tuba', m, t, d, v + 8, 0.0, 0.55)
            o.play('basses', m, t, d, v, 0.2, 0.4)
        elif part == 'treaty2':
            o.play('horns', m, t, d, v + 8, pw(t), 0.6)
    o.boom(T_SPEAR + 0.02, pw(T_SPEAR), 0.55)
    o.clash(T_SPEAR + 0.02, pw(T_SPEAR), 96, 0.4)
    for k, tc in enumerate(REPROACH):                       # a cymbal on each of her outbursts
        o.hit('crash', tc + 0.02, 90 + 10 * k, gain=0.3, pan=pfr(tc))
