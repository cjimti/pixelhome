"""We Never Will Bow Down: the people refuse the idols in the Temple, and the idols fall.

Four grey idols stand on Porch Front, the Temple, over the faint glow of the lights. The chorus is the whole house:
blue and white in bands, like a tallit, on Left, Right, the porch runs and Side, holding upright and steady. Every
chord they sing lifts the whole house a step and lets it settle, on the beat; nothing sways, nothing bows.

"We never will bow down to the rude stock or sculptur'd stone": on each "stock" and "stone" a blow lands on an idol.
The first cracks it (a white fissure, and its grey dims), the second breaks it, and its pieces slide off the porch
toward the street and go out, one idol after another, left to right, until the Temple is empty. A held silence, the
house still standing. Then "We worship God, and God alone": C major, the blue and white swell to full on every chord
and the Temple stays dark, empty and clean, only the lights' glow on it, which is where Father of Heav'n begins.

The music is Handel's own: Judas Maccabaeus No. 52, the Andante's opening eight bars, its last eight, and the first
and last phrases of the A tempo giusto, transcribed from the Novello vocal score into we_never_will_bow_down.musicxml
and timed by scripts/score_excerpt.py at the marked tempos. The chorus plays on strings with oboes and bassoons
doubling, as Handel's orchestra doubles it, horns on the long notes of the giusto, the basses in octaves on cellos,
basses and a harpsichord continuo; each blow on an idol is a knock of stone, each fall a heavier one.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, smoothstep, Flicker
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM10'
TITLE = 'We Never Will Bow Down'
KIND = 'show'
DESCRIPTION = ("Grey idols stand in the Temple on the porch. The people, blue and white across the house, refuse to bow, "
               "and on every 'stock' and 'stone' an idol cracks and falls, until the Temple is empty and clean.")

EX = excerpt(__file__)                      # No. 52: Andante bars 1-8 and 9-16 (pp. 133, 136), giusto 17-23, 24-29
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
T_GIUSTO = BAR[17]                          # "We worship God"
T_LAST = BAR[29]                            # "alone.", held
SILENT = (BAR[16] + 0.6, T_GIUSTO + 1.3)    # the held silence before the giusto
ONSETS = np.array(sorted({round(n[0], 3) for n in SUNG}))
VEL = np.array([max(n[3] for n in SUNG if abs(n[0] - t) < 0.002) for t in ONSETS])
# a blow on each "stock" and "stone" (the B naturals on the bar's first beat): crack, then break, idol by idol
BLOWS = [BAR[b] for b in (5, 6, 7, 8, 13, 14, 15, 16)]

BLUE = hexc('#1e5bd8')                      # the Maccabees and the people
WHITE = hexc('#f2f6ff')
STONE = hexc('#6a6a6a')                     # the idols
CRACK = hexc('#ffffff')
IDOLS = (0.13, 0.37, 0.63, 0.87)            # where they stand along Porch Front, as fractions of it
WIDE = 0.09                                # half an idol's width, the same


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def pulse(t, onsets, vel, tau, rise=0.07):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    if i < 0:
        return 0.0
    a = t - onsets[i]
    prev = 0.0 if i == 0 else float(np.exp(-(onsets[i] - onsets[i - 1]) / tau) * vel[i - 1] / 110)
    up = smoothstep(0.0, rise, a)
    return float((1 - up) * prev + up * np.exp(-a / tau) * vel[i] / 110)


def render(G, seed=10):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    temple = seg == 'Porch Front'
    house = ~temple
    pf0, pf1 = span(G, 'Porch Front')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    u = np.clip((d - pf0) / (pf1 - pf0), -1, 2)              # along Porch Front, 0..1
    # the tallit: white with blue bands, about 11 pixels a band
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
    glow = Glow(G, seed)
    shimmer = Flicker(rng, G.N, 0.2, 0.6)
    idol = np.array([np.clip(1 - np.abs(u - c) / WIDE, 0, 1) ** 0.4 * temple for c in IDOLS])   # (4, N)
    fissure = np.array([np.exp(-((u - c - 0.012 * (k % 2 * 2 - 1)) / 0.01) ** 2) * temple for k, c in enumerate(IDOLS)])
    # each idol's pieces: five fragments sliding off its nearer corner and down the porch run toward the street
    left_side = np.array(IDOLS) < 0.5
    pieces = rng.uniform(0.6, 1.4, (4, 5))
    for f in range(F):
        t = f * DT
        giusto = smoothstep(T_GIUSTO - 0.2, T_GIUSTO + 1.5, t)
        quiet = SILENT[0] <= t < SILENT[1]
        # the people: steady, lifted a step by every chord they sing
        p = 0.0 if quiet else pulse(t, ONSETS, VEL, 0.45 if t < T_GIUSTO else 0.9, 0.08 if t < T_GIUSTO else 0.2)
        held = smoothstep(T_LAST, T_LAST + 0.6, t) * (1 - 0.6 * smoothstep(D - 2.5, D - 0.3, t))
        lvl = 0.4 + 0.12 * giusto + (0.2 + 0.08 * giusto) * p + 0.3 * held
        lvl = lvl * (0.95 + 0.05 * shimmer(t))
        white = 0.7 + 0.3 * giusto
        fr = light(BLUE, lvl * band * house) + light(WHITE, lvl * (1 - band) * white * house)
        fr += light(BLUE, 0.6 * lvl * (1 - band) * (1 - white) * house)
        # the Temple: the lights' glow under the idols
        fr += glow.frame(t, 0.8)
        for k in range(4):
            t1, t2 = BLOWS[2 * k], BLOWS[2 * k + 1]
            a = t - t1
            standing = 1.0 if t < t2 else 0.0
            dim = 1.0 if t < t1 else 0.6
            if standing:
                fr += light(STONE, 0.8 * dim * idol[k] * (0.97 + 0.03 * shimmer(t)))
            if a >= 0 and t < t2:                               # the crack, flashing, then a faint seam
                fr += light(CRACK, (0.9 * np.exp(-a / 0.25) + 0.12) * fissure[k])
            b = t - t2
            if 0 <= b < 3.0:                                    # broken: a flash, then the pieces slide away
                fr += light(CRACK, 0.9 * np.exp(-b / 0.2) * idol[k])
                corner = pf0 if left_side[k] else pf1
                start = pf0 + IDOLS[k] * (pf1 - pf0)
                for j in range(5):
                    s = pieces[k, j]
                    x0 = start + (j - 2) * 7.0
                    travel = s * 70.0 * b + 45.0 * b * b
                    pos = x0 - travel if left_side[k] else x0 + travel
                    pos = max(pos, pl0) if left_side[k] else min(pos, pr1)
                    fade = np.exp(-b / (0.9 * s)) * (1 - smoothstep(2.2, 3.0, b))
                    fr += light(STONE, 0.8 * fade * np.exp(-((d - pos) / 3.5) ** 2))
                    fr += light(WHITE, 0.25 * fade * np.exp(-((d - pos) / 1.5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings with oboes and bassoons doubling, sopranos and altos from the left of the house, tenors
    and basses from the right; horns on the giusto's long notes; the basses in octaves on cellos and basses with a
    harpsichord continuo; a stone knock on each blow, a heavier fall when an idol breaks."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pf0, pf1 = span(G, 'Porch Front')
    pl, pr = pan_at(sum(span(G, 'Left')) / 2), pan_at(sum(span(G, 'Right')) / 2)
    o = Orchestra(M, level=2.4)
    parts = {'S': [('violins', 0, 0, 0.5), ('oboes', 0, -8, 0.3)],
             'A': [('violins', 0, -4, 0.35), ('violas', 0, -2, 0.35)],
             'T': [('violas', 0, -2, 0.45), ('bassoons', 0, -10, 0.25)],
             'B': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, dd, m, v, h, who in SUNG:
        g = 1.0 if t < T_GIUSTO else 1.15
        for section, tr, dv, gg in parts[who]:
            o.play(section, m + tr, t, dd, v + dv, 0.55 * side[who], gg * g)
        if t >= T_GIUSTO - 0.01 and dd >= 1.0 and who in ('S', 'A'):
            o.play('horns', m - 12, t, dd, v - 10, 0.0, 0.35)
    for t, dd, m, v, h, who in ORCH:
        if h == 1 and m < 48:
            o.play('basses', m + 12 if m < 36 else m, t, dd, v - 6, 0.0, 0.45)
    # the continuo: a harpsichord playing the reduction, plucked short
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, int(min(110, v)), min(dd, 0.32)) for t, dd, m, v, h, who in ORCH]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.35, 0.0)
    # the blows: stone knocked, then broken
    for k, tb in enumerate(BLOWS):
        idol = k // 2
        pan = pan_at(pf0 + (0.13 + 0.24 * idol + (0.02 if idol > 1 else 0)) * (pf1 - pf0))
        if k % 2 == 0:
            o.hit('hoof', tb, 120, pitch=-5, gain=0.7, pan=pan, fx=True)
            o.hit('bass drum', tb, 96, gain=0.35, pan=pan, fx=True)
            o.hit('scrape', tb + 0.02, 70, gain=0.15, pan=pan, fx=True)
        else:
            o.hit('bass drum', tb, 120, gain=0.6, pan=pan, fx=True)
            o.hit('hoof', tb, 124, pitch=-8, gain=0.8, pan=pan, fx=True)
            for j, dt in enumerate((0.18, 0.37, 0.6, 0.9)):        # the pieces tumbling down the porch
                o.hit('hoof soft', tb + dt, 100 - 12 * j, pitch=-3 + j, gain=0.35, pan=pan * (1 + 0.15 * j), fx=True)
    o.hit('timpani roll', T_LAST - 1.5, 80, pitch=0, gain=0.2)
    o.hit('timpani', T_LAST, 104, pitch=0, gain=0.35)
