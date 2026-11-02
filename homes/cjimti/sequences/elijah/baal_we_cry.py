"""Baal, We Cry to Thee: the priests of Baal call on their god around his bronze altar on Left, two choirs answering.

The scene opens where the last one ended: Baal's burnished altar on Left, Elijah's amber on Right beside his unlit
wood, the people's candles on Porch Left and Porch Right, the last of Ahab's grey fading. Then the priests begin, a
double chorus calling in turn. The tenors and basses are the half of Left toward the Side corner, the trebles and
altos the half toward the porch, and every syllable a choir sings flares its half bronze. On every accented "Baal!"
the whole run flashes, a brass glint is flung from the altar up Left toward the porch (higher for a higher note) and
falls back, and the people's candles flinch.

At each fortissimo "hear and answer us!" the two choirs sing together, the whole of Left blazes and a bronze reach
pushes out along Porch Left toward heaven, and dies before it gets there. Porch Front, heaven, stays dark through
all of it. The Allegro's first bars close the scene: a glint racing up Left with every note of the orchestra's
figure, the priests working themselves up for what comes next.

The music is Mendelssohn's own: the Andante grave of No. 11 and the first bars of its Allegro, transcribed from the
Novello octavo vocal score into baal_we_cry.musicxml and timed by scripts/score_excerpt.py at the marked tempos,
four bars of the repeated "Heed the sacrifice" left out. The priests are played on brass, as in Hear and Answer:
trebles on trumpets, altos on horns, tenors on trombones, basses on tuba, with woodwinds doubling; timpani with
every accented "Baal!", and a bass drum and cymbal under the fortissimo cries.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL07'
TITLE = 'Baal, We Cry to Thee'
KIND = 'show'
DESCRIPTION = ("The priests of Baal call on their god in two choirs around his bronze altar on Left, every cry "
               "flaring the run and flinging brass glints toward heaven. Heaven stays dark.")
VOICEOVER = 'Baal, we cry to thee. Hear and answer us.'

EX = excerpt(__file__)                      # No. 11 bars 1-21 and 25-35
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
UPPER = ('S1', 'S2', 'A1', 'A2')           # the trebles and altos
LOWER = ('T1', 'T2', 'B1', 'B2')           # the tenors and basses
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in UPPER + LOWER]
T_ALLEGRO = BAR[33]


def onsets(parts, vmin=0):
    return np.array(sorted({round(n[0], 3) for n in SUNG if n[5] in parts and n[3] >= vmin}))


UP_ON = onsets(UPPER)
LO_ON = onsets(LOWER)
ACCENT = onsets(UPPER + LOWER, vmin=112)    # the sforzando "Baal!"s and the fortissimo cries
LEAD = [n for n in SUNG if n[5] in ('S1', 'T1')]
CRIES = [n[0] for n in SUNG if n[5] == 'S1' and n[3] >= 105 and n[1] >= 1.0]   # the held ff "an-swer"
FIG = [n for n in ORCH if n[0] >= T_ALLEGRO - 0.01 and n[1] < 0.3 and n[4] == 0]

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
GREY = hexc('#8a8f98')                      # Ahab, leaving
BRONZE = hexc('#b06a10')                    # Baal's altar and priests
GLINT = hexc('#ffcc55')
WOOD = hexc('#5a3a1e')                      # Elijah's altar, unlit


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    pr0, pr1 = span(G, 'Porch Right')
    return dict(home=r0 + 0.35 * (r1 - r0), baal=(l0 + 0.15 * (l1 - l0), l0 + 0.55 * (l1 - l0)),
                wood=(r0 + 0.6 * (r1 - r0), r0 + 0.85 * (r1 - r0)), ahab=pr0 + 0.4 * (pr1 - pr0),
                mid=l0 + 0.5 * (l1 - l0))


def last(arr, t, tau, span_=2.0):
    i = int(np.searchsorted(arr, t, side='right')) - 1
    return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p = places(G)
    l0, l1 = span(G, 'Left')
    pf0, pf1 = span(G, 'Porch Front')
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    lower_half = left * (1 - smoothstep(p['mid'] - 25, p['mid'] + 25, d))      # the tenors and basses, toward Side
    upper_half = left * smoothstep(p['mid'] - 25, p['mid'] + 25, d)            # the trebles and altos, toward the porch
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    seethe = Flicker(rng, G.N, 2.5, 8.0)
    glint = Flicker(rng, G.N, 3.0, 9.0)
    b0, b1 = p['baal']
    w0, w1 = p['wood']
    baal = smoothstep(b0, b0 + 12, d) * (1 - smoothstep(b1 - 12, b1, d))
    wood = smoothstep(w0, w0 + 10, d) * (1 - smoothstep(w1 - 10, w1, d))
    altar = 0.5 * (b0 + b1)
    lead = [(n[0], n[1], n[2]) for n in LEAD]
    lead_on = np.array([n[0] for n in lead])
    fig = np.array([n[0] for n in FIG])
    figpos = np.array([altar + np.clip((n[2] - 53) / (77 - 53), 0, 1) * (l1 - altar) for n in FIG])

    def blob(c, w):
        return np.exp(-((d - c) / w) ** 2)

    for f in range(F):
        t = f * DT
        fr = light(DUST, 0.28 * (1 - 0.4 * heaven) * np.ones(G.N))
        intro = smoothstep(0, 0.5, t)                               # the first call grows out of EL06's last frame
        ak = intro * last(ACCENT, t, 0.35)
        heat = smoothstep(0, T_ALLEGRO, t)

        # the people, watching from both porch runs; they flinch at every accented cry
        fr += light(CANDLE, cand * people * 0.7 * (0.75 + 0.25 * flick(t)) * (1 - 0.5 * ak))

        # the last of Ahab's grey, leaving by Porch Right
        g = 0.13 * (1 - smoothstep(0, 2.5, t))
        if g > 0:
            fr += light(GREY, g * (blob(p['ahab'], 22) + 0.3 * blob(p['ahab'], 70)))

        # Elijah and his unlit wood, steady on Right
        fr += light(AMBER, (0.7 + 0.04 * np.sin(2 * np.pi * t / 5)) * blob(p['home'], 16) + 0.15 * blob(p['home'], 60))
        fr += light(CORE, 0.45 * blob(p['home'], 5))
        fr += light(WOOD, 0.75 * wood)

        # Baal's altar, and his priests on Left: each choir's half flares with its syllables
        settle = 0.75 - 0.35 * smoothstep(0.5, 3.0, t)              # EL06's altar, settling under the priests
        fr += light(BRONZE, settle * baal + left * (0.1 + 0.08 * heat + 0.05 * seethe(t)))
        fr += light(GLINT, 0.45 * baal * np.maximum(glint(t) - 0.6, 0) * 2.5)
        uk, lk = intro * last(UP_ON, t, 0.55), intro * last(LO_ON, t, 0.55)
        fr += light(BRONZE, 1.0 * uk * upper_half + 1.0 * lk * lower_half)
        fr += light(GLINT, 0.35 * (uk * upper_half + lk * lower_half) * np.maximum(seethe(t) - 0.4, 0) * 2)
        fr += light(BRONZE, 0.6 * ak * left)
        fr += light(GLINT, 0.9 * ak * left * (0.5 + 0.5 * glint(t)))

        # the accented calls fling a glint from the altar up Left, higher for a higher note, and it falls back
        i0 = int(np.searchsorted(lead_on, t - 1.6))
        i1 = int(np.searchsorted(lead_on, t, side='right'))
        for k in range(i0, i1):
            tc, dc, m = lead[k]
            a = t - tc
            top = altar + np.clip((m - 52) / (77 - 52), 0.15, 1.0) * (l1 + 20 - altar)
            arc = np.sin(np.pi * min(a / 1.6, 1.0))          # up and back down
            pos = altar + (top - altar) * arc
            fr += light(GLINT, intro * np.exp(-a / 1.0) * blob(pos, 14))

        # the fortissimo cries: Left blazes and a bronze reach pushes out toward heaven, dying before it arrives
        for tc in CRIES:
            if tc <= t < tc + 3.2:
                grow = min(1.0, (t - tc) / 1.4)
                fade = 1 - smoothstep(tc + 1.4, tc + 3.2, t)
                head = l1 + 0.65 * grow * (pf0 - l1)
                body = smoothstep(l1 - 60, l1, d) * smoothstep(head + 20, head - 40, d)
                strain = 0.8 + 0.2 * np.sin(2 * np.pi * 6 * t)
                fr += light(BRONZE, fade * (0.9 * body * strain + 0.6 * left))
                fr += light(GLINT, fade * 0.5 * left)
                fr += light(GLINT, fade * 0.8 * np.exp(-((d - head) / 14) ** 2) * strain)

        # the Allegro's figure: each note a glint racing up Left toward the porch
        lo = int(np.searchsorted(fig, t - 0.3))
        hi = int(np.searchsorted(fig, t, side='right'))
        for k in range(lo, hi):
            a = t - fig[k]
            fr += light(GLINT, 0.9 * np.exp(-a / 0.15) * blob(figpos[k] + 120 * a, 12))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The priests' two choirs on brass with woodwinds doubling, each choir panned to its half of Left; the
    accompaniment's bass and the Allegro on the orchestra; timpani with the accented calls, bass drum and cymbal under
    the fortissimo cries."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    l0, l1 = span(G, 'Left')

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    lower_pan = pan_at(l0 + 0.25 * (l1 - l0))
    upper_pan = pan_at(l0 + 0.75 * (l1 - l0))
    baal = pan_at(l0 + 0.5 * (l1 - l0))
    o = Orchestra(M, level=1.25)
    o.tutti(ORCH, size=lambda t: 0.9, pan=lambda t, m: 0.4 * baal)
    parts = {'S1': [('trumpets', 0, -2, 0.45), ('oboes', 0, -12, 0.3)], 'S2': [('trumpets', 0, -6, 0.35)],
             'A1': [('horns', 0, 2, 0.5), ('clarinets', 0, -12, 0.3)], 'A2': [('horns', 0, -2, 0.4)],
             'T1': [('trombones', 0, 2, 0.5), ('bassoons', 0, -10, 0.3)], 'T2': [('trombones', 0, -2, 0.4)],
             'B1': [('tuba', 0, 2, 0.45), ('cellos', 0, -8, 0.35)], 'B2': [('tuba', 0, -2, 0.4), ('basses', -12, -6, 0.4)]}
    for t, d, m, v, h, who in SUNG:
        pan = upper_pan if who in UPPER else lower_pan
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pan, g)
    for t in ACCENT:
        o.hit('timpani', t, 112, pitch=-5, gain=0.4, pan=baal)
    for t in CRIES:
        o.hit('bass drum', t, 110, gain=0.35, pan=baal)
        o.hit('crash', t, 96, gain=0.18, pan=baal)
    o.hit('timpani roll', T_ALLEGRO - 2.2, 96, pitch=-5, gain=0.3, pan=baal)
