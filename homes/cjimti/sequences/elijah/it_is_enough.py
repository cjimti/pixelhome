"""It Is Enough: Obadiah warns Elijah that Jezebel will have his life, and he flees alone into the wilderness.

The scene opens where the last one ended: the people stained with Jezebel's wine, the wine closing on Elijah's small
amber on Right. It ebbs away as Obadiah comes: a teal light from the back of Porch Right that walks down the run and
out along Right to Elijah, flaring with every word of "Man of God, now let my words be precious in thy sight". At
"Elijah is worthy to die" a stab of wine crosses the house; at "that they may slay thee" the teal flashes beside him.

"Arise, then, and hasten for thy life; to the wilderness journey": Elijah goes. His amber leaves its place and walks
the long way round the house, a step with every throb of the aria's quavers, up Porch Right, across Porch Front,
down Porch Left and along Left, leaving a fading glow behind, and on to Side, the wilderness, where he stops at its
far end, the farthest point of the house from the street. Obadiah's teal stays behind on Right and fades.

"It is enough, O Lord; now take away my life, for I am not better than my fathers!": alone at the free end of Side,
his amber flares a little on each word and sinks lower after each phrase, smaller and dimmer, while the line
Mendelssohn gives the cellos under him moves as a slow ember along Side toward him and back. On the last "it is
enough" it settles beside him and goes out, and he is left a small low glow in the dust of the wilderness.

The music is Mendelssohn's own: No. 25, Obadiah's recitative, and the first seventeen bars of No. 26, transcribed
from the Novello octavo vocal score into it_is_enough.musicxml and timed by scripts/score_excerpt.py at the marked
tempos. Obadiah is played on violas and a clarinet, Elijah on cellos and horns, the accompaniment on soft strings.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL17'
TITLE = 'It Is Enough'
KIND = 'show'
DESCRIPTION = ("Obadiah's teal warns him: Jezebel will have his life. Elijah's amber walks the long way round the house "
               "to Side and sinks low at its far end: it is enough, O Lord.")
VOICEOVER = 'He went a day\'s journey into the wilderness, and sat down, and asked that he might die.'

EX = excerpt(__file__)                      # No. 25 bars 1-11, No. 26 bars 1-17 (12-28)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
OBADIAH = [n for n in EX['notes'] if n[5] == 'Obadiah']
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_DIE = BAR[5]                              # "Elijah is worthy to die"
T_SLAY = BAR[9]                             # "that they may slay thee"
T_ARISE = BAR[9] + 0.5 * (BAR[10] - BAR[9])
T_ARIA = BAR[12]
T_SING = BAR[20]                            # "It is enough"
T_LAST = BAR[27]                            # the second "It is enough"
OB_ON = np.array([n[0] for n in OBADIAH])
EL_ON = np.array([n[0] for n in ELIJAH])
THROB = np.array(sorted({round(n[0], 3) for n in ORCH if T_ARISE <= n[0] < T_SING and n[4] == 0}))
CELLO = [n for n in ORCH if n[4] == 1 and 50 <= n[2] <= 64 and n[0] >= T_ARIA]
PHRASE_END = [BAR[22], BAR[24], BAR[26] + 0.5 * (BAR[27] - BAR[26]), D - 5.0]

DUST = hexc('#3a2008')                      # the wilderness
WINE = hexc('#a01860')                      # EL16's last frame
ROSE = hexc('#ff4080')
CANDLE = hexc('#ffcf8a')
TEAL = hexc('#20b0a0')                      # Obadiah
FOAM = hexc('#a0fff0')
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
EMBER = hexc('#ff7020')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    r0, r1 = span(G, 'Right')
    pr0, pr1 = span(G, 'Porch Right')
    s0, s1 = span(G, 'Side')
    return dict(home=r0 + 0.35 * (r1 - r0), ob_from=pr0 + 0.1 * (pr1 - pr0), ob_at=r0 + 0.2 * (r1 - r0),
                end=s0 + 6.0, side=(s0, s1))


def elijah_at(G, t):
    """At his place on Right until he rises; then round the house at a steady walk to the free end of Side, a little
    surge on every throb of the aria's quavers."""
    p = places(G)
    if t < T_ARISE:
        return p['home']
    u = (t - T_ARISE) / (T_SING - 1.0 - T_ARISE)
    k = int(np.searchsorted(THROB, t, side='right')) - 1
    surge = 0.006 * (1 - np.exp(-(t - THROB[k]) / 0.2)) if k >= 0 else 0.0
    u = smoothstep(0, 1, min(u + surge, 1.0)) * 0.35 + 0.65 * min(u + surge, 1.0)
    return p['home'] + (p['end'] - p['home']) * min(u, 1.0)


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    p = places(G)
    people = np.isin(seg, ['Porch Left', 'Porch Right'])
    side = seg == 'Side'
    r0, r1 = span(G, 'Right')
    s0, s1 = p['side']
    stained = np.isin(seg, ['Left', 'Porch Left', 'Porch Right'])
    cand = np.zeros(G.N)
    for s in ('Porch Left', 'Porch Right'):
        a, b = span(G, s)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    cand = np.minimum(cand, 1.0)
    seethe = Flicker(rng, G.N, 4.0, 11.0)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    e_home = p['home']
    trail = np.zeros(G.N)

    for f in range(F):
        t = f * DT
        fr = light(DUST, (0.14 + 0.01 * smoothstep(T_ARIA, D - 4, t)) * np.ones(G.N))

        # EL16's wine ebbing away: on the people and Left, and the walls around Elijah
        ebb = 1 - smoothstep(0.0, BAR[3], t)
        if ebb > 0:
            porch = np.isin(seg, ['Porch Left', 'Porch Right'])
            fr += light(WINE, ebb * (0.75 * porch + 0.55 * (seg == 'Left')) * (0.85 + 0.15 * seethe(t)))
            ring = (seg == 'Right') * (1 - np.exp(-((d - e_home) / 13) ** 4))
            fr += light(WINE, 0.5 * ebb * ring)
        # the people's candles, a low flicker until Elijah has passed them
        gone = smoothstep(T_ARIA, T_SING, t)
        fr += light(CANDLE, 0.22 * (1 - gone) * (1 - 0.5 * ebb) * cand * people * (0.75 + 0.25 * flick(t)))
        # "worthy to die": a stab of wine across the house
        if 0 <= t - T_DIE < 2.0:
            fr += light(WINE, 0.45 * np.exp(-(t - T_DIE) / 0.5) * (1 - side))

        # Obadiah: teal from the back of Porch Right, out along Right to Elijah, flaring on every word
        if t < T_SING + 4.0:
            come = smoothstep(0.3, BAR[4], t)
            ob = p['ob_from'] + (p['ob_at'] - p['ob_from']) * come
            j = int(np.searchsorted(OB_ON, t, side='right')) - 1
            word = float(np.exp(-(t - OB_ON[j]) / 0.4)) if j >= 0 and t < OB_ON[-1] + 1.5 else 0.0
            fade = 1 - smoothstep(T_ARIA, T_SING + 4.0, t)
            lvl = (0.55 + 0.4 * word) * fade * smoothstep(0.0, 1.0, t)
            fr += light(TEAL, lvl * np.exp(-((d - ob) / 14) ** 2))
            fr += light(FOAM, 0.45 * word * fade * np.exp(-((d - ob) / 4) ** 2))
            if 0 <= t - T_SLAY < 1.5:                    # "slay thee": the teal flashes by him
                fr += light(TEAL, 0.6 * np.exp(-(t - T_SLAY) / 0.4) * np.exp(-((d - e_home) / 40) ** 2))

        # Elijah: walking round the house, then sinking at the free end of Side
        e = elijah_at(G, t)
        walking = T_ARISE <= t < T_SING
        trail = trail * np.exp(-DT / 1.2)
        if walking:
            trail = np.maximum(trail, 0.35 * np.exp(-((d - e) / 10) ** 2))
        fr += light(AMBER, trail)
        if t < T_SING:
            lvl, size, core = 0.6, 14.0, 0.4
            k = int(np.searchsorted(THROB, t, side='right')) - 1
            step = float(np.exp(-(t - THROB[k]) / 0.25)) if walking and k >= 0 else 0.0
            lvl += 0.2 * step
        else:
            # sinking after each phrase: lower and smaller, flaring a little on each word
            n_end = sum(1 for te in PHRASE_END if t >= te)
            sink = [0.62, 0.5, 0.4, 0.32, 0.25][n_end]
            prev = [0.62, 0.62, 0.5, 0.4, 0.32][n_end]
            tp = PHRASE_END[n_end - 1] if n_end else T_SING
            base = prev + (sink - prev) * smoothstep(tp, tp + 2.0, t)
            j = int(np.searchsorted(EL_ON, t, side='right')) - 1
            word = float(np.exp(-(t - EL_ON[j]) / 0.6)) if j >= 0 and t < D - 3.0 else 0.0
            lvl = base + 0.15 * word * (1 - smoothstep(D - 5.0, D - 3.0, t))
            size = 8.0 + 8.0 * (base - 0.25) / 0.37
            core = 0.12 + 0.35 * (base - 0.25) / 0.37 + 0.1 * word * (t < D - 3.0)
        fr += light(AMBER, lvl * np.exp(-((d - e) / size) ** 2))
        fr += light(CORE, core * np.exp(-((d - e) / 3) ** 2))

        # the cello line under him: a slow ember on Side, its pitch its distance from him, out by the end
        if t >= T_SING - 1.0:
            on = [n for n in CELLO if n[0] <= t]
            if on:
                n = on[-1]
                where = p['end'] + (s1 - s0) * (0.15 + 0.6 * (n[2] - 50) / 14)
                glow = np.exp(-(t - n[0]) / 1.5) * 0.3 + 0.4
                fr += light(EMBER, glow * (1 - smoothstep(D - 5.0, D - 2.5, t)) * np.exp(-((d - where) / 28) ** 2) * side)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Obadiah on violas and a clarinet from where he stands; Elijah on cellos and horns, following him round the house
    and then from the far end of Side; the accompaniment on soft strings."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    p = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.9)
    o.tutti(ORCH, size=lambda t: 0.3 if t < T_ARIA else 0.2, pan=lambda t, m: 0.5 * pan_at(elijah_at(G, t)))

    for t, d, m, v, h, who in OBADIAH:
        o.play('violas', m, t, d, v + 4, pan_at(p['ob_at']), 0.6)
        o.play('clarinets', m, t, d, v - 4, pan_at(p['ob_at']), 0.35)
    for t, d, m, v, h, who in ELIJAH:
        o.play('cellos', m, t, d, v + 6, pan_at(p['end']), 0.65)
        o.play('horns', m, t, d, v - 6, pan_at(p['end']), 0.35)

    o.hit('timpani', T_SLAY + 0.4, 104, pitch=-6, gain=0.3, pan=pan_at(p['home']))
    o.hit('gong', T_DIE, 70, gain=0.08)
    o.wind(T_ARISE, T_SING + 6.0, level=0.12, pan=-0.5)
