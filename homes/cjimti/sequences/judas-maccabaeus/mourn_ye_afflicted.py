"""Mourn, Ye Afflicted Children: Mattathias has died, and the people mourn him in long falling phrases.

The scene opens where the Overture left the house: Seleucid purple over Left, Right and Side, the Temple on Porch Front
grey with its idols, and a few blue lights hidden on Left, in the hills of Modein. The people stand on Porch Left and
Porch Right, small blue and white lights. Mattathias is one white light on Left among the hidden blue.

The Largo's ritornello sets the lament going, its bass stepping down. With each "Mourn" a wave runs down a porch run
toward the Temple, the sopranos and altos on Porch Left, the tenors and basses on Porch Right, and leaves the people
a little dimmer behind it; every sung note lifts its run for a moment. Each "your father is no more" takes some of
Mattathias's light away, and with the last, pianissimo, it is gone. Through it all the purple leans in a little
heavier. The last frame, the people dim, the hidden blue on Left, the Temple grey, is where the prayer (JM03) begins.

The music is Handel's own: No. 2 from its upbeat to "mourn in solemn strains" (bars 0-8), bars 17-22, to the
unaccompanied "is no more", and the last six bars, transcribed from the Novello vocal score into
mourn_ye_afflicted.musicxml and timed by scripts/score_excerpt.py at a Largo of 58. The chorus plays on strings with
oboes and bassoons doubling, sopranos and altos to the left and tenors and basses to the right, over a harpsichord
continuo; a muffled drum marks each "no more".

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, keys, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM02'
TITLE = 'Mourn, Ye Afflicted Children'
KIND = 'show'
DESCRIPTION = ("Mattathias has died. The people's blue and white lights on the porch dim in long falling phrases, a "
               "slow lament flowing toward the Temple, and his light on Left goes out.")
VOICEOVER = 'Mattathias, the old priest who began the revolt, is dead, and his people mourn him.'

EX = excerpt(__file__)              # m1 upbeat, m2-m9 bars 1-8, m10-m15 bars 17-22, m16-m21 bars 40-45
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 1.5, 2)
VOICES = ('S', 'A', 'T', 'B')
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']


def at(m, beat):
    """Time of a beat (0-based, in quarters) of compact measure m."""
    nxt = BAR.get(m + 1, EX['seconds'])
    return BAR[m] + (nxt - BAR[m]) * beat / 4.0


T_CHORUS = BAR[4]                   # the first "Mourn"
NO_MORE = [at(10, 2.0), at(11, 2.0), at(12, 0.0), at(15, 1.5), at(17, 1.5), at(20, 0.0)]
T_ALONE = at(15, 0.5)               # "is no more", voices alone, pp


def phrases():
    """(t, voice) for each voice's phrase starts: a note after a rest of 0.3 s or more."""
    out = []
    for v in VOICES:
        ns = sorted(n for n in SUNG if n[5] == v)
        end = -9.0
        for n in ns:
            if n[0] - end > 0.3:
                out.append((n[0], v))
            end = max(end, n[0] + n[1])
    return sorted(out)


PHRASES = phrases()

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
GLINT = hexc('#c08a40')
STONE = hexc('#6a6a6a')             # the idols in the Temple
BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    runL, runR = seg == 'Porch Left', seg == 'Porch Right'
    porch = runL | runR
    front = seg == 'Porch Front'
    wings = np.isin(seg, ['Left', 'Right', 'Side'])
    # how far toward the Temple each porch pixel is: 0 at the street end of its run, 1 at Porch Front
    tow = np.zeros(G.N)
    tow[runL] = (d[runL] - pl0) / (pl1 - pl0)
    tow[runR] = (pr1 - d[runR]) / (pr1 - pr0)
    # the people: small lights along both runs, blue and white in turn
    blue_p, white_p = np.zeros(G.N), np.zeros(G.N)
    for a, b in ((pl0, pl1), (pr0, pr1)):
        for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
            g = np.exp(-((d - c) / 4.0) ** 2)
            if k % 2:
                white_p += g
            else:
                blue_p += g
    blue_p, white_p = np.minimum(blue_p, 1) * porch, np.minimum(white_p, 1) * porch
    # the idols: four grey blocks on Porch Front
    idols = np.zeros(G.N)
    for k in range(4):
        c = pf0 + (0.14 + 0.24 * k) * (pf1 - pf0)
        idols += smoothstep(14, 9, np.abs(d - c))
    idols = np.minimum(idols, 1) * front
    # the hidden blue on Left, and Mattathias among it
    hid = np.zeros(G.N)
    for c in l0 + np.array([0.18, 0.33, 0.47, 0.75, 0.88]) * (l1 - l0):
        hid += np.exp(-((d - c) / 3.5) ** 2)
    hid *= seg == 'Left'
    matt_c = l0 + 0.62 * (l1 - l0)
    matt = np.exp(-((d - matt_c) / 4.0) ** 2) * (seg == 'Left')
    flick = Flicker(rng, G.N, 0.6, 2.2)
    slow = Flicker(rng, G.N, 0.1, 0.4)
    onsets = {v: np.array(sorted(n[0] for n in SUNG if n[5] == v)) for v in VOICES}
    # Mattathias's light: a step down with each "no more", gone with the last
    matt_keys = [(0.0, 1.0)] + [(t + 1.5, 1.0 * (1 - (k + 1) / len(NO_MORE)) ** 1.3) for k, t in enumerate(NO_MORE)]
    # the people dim over the scene, a little more after every wave
    people_keys = [(0.0, 0.8), (T_CHORUS, 0.78), (BAR[10], 0.62), (T_ALONE, 0.5), (BAR[16], 0.44), (D, 0.34)]
    for f in range(F):
        t = f * DT
        heavy = 0.36 + 0.1 * smoothstep(0, D, t)
        fr = light(PURPLE, heavy * wings * (0.9 + 0.1 * slow(t)) + 0.14 * porch)
        fr += light(GLINT, 0.18 * wings * np.maximum(flick(t * 0.5), 0) ** 4)
        fr += light(STONE, 0.5 * idols) + glow.frame(t, 0.55)
        fr += light(BLUE, 0.5 * hid * (0.85 + 0.15 * slow(t)))
        m = keys(t, matt_keys)
        for tn in NO_MORE:                                   # each "no more": a last swell, then the light sinks
            a = t - tn
            if 0 <= a < 1.5:
                m += 0.25 * np.sin(np.pi * a / 1.5) * (m > 0.02)
        fr += light(WHITE, m * matt) + light(WHITE, 0.4 * m * np.exp(-((d - matt_c) / 18) ** 2) * (seg == 'Left'))
        # the people, and the waves of mourning running down to the Temple
        lev = keys(t, people_keys) * (0.88 + 0.12 * flick(t))
        lift = np.zeros(G.N)
        for v, mask in (('S', runL), ('A', runL), ('T', runR), ('B', runR)):
            i = int(np.searchsorted(onsets[v], t, side='right')) - 1
            if i >= 0:
                lift += 0.3 * np.exp(-(t - onsets[v][i]) / 0.5) * mask
        wave = np.zeros(G.N)
        for tp, v in PHRASES:
            a = t - tp
            if 0 <= a < 4.0:
                mask = runL if v in ('S', 'A') else runR
                pos = smoothstep(0, 3.6, a)
                wave += np.exp(-((tow - pos) / 0.12) ** 2) * mask * (1 - 0.6 * smoothstep(2.5, 4.0, a))
        wave = np.minimum(wave, 1.2)
        fr += light(BLUE, (lev + lift + 0.6 * wave) * blue_p)
        fr += light(WHITE, (0.7 * lev + lift + 0.8 * wave) * white_p)
        fr += light(BLUE, 0.5 * wave * porch)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings with oboes and bassoons doubling, sopranos and altos left, tenors and basses right;
    the ritornello on strings, the harpsichord continuo under all of it; a muffled drum on each "no more"."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pl, pr = pan_at(sum(span(G, 'Porch Left')) / 2), pan_at(sum(span(G, 'Porch Right')) / 2)
    o = Orchestra(M, level=3.6)
    parts = {'S': [('violins', 0, 0, 0.5), ('oboes', 0, -10, 0.25)],
             'A': [('violins', 0, -4, 0.35), ('violas', 0, -2, 0.35)],
             'T': [('violas', 0, -2, 0.45), ('bassoons', 0, -10, 0.22)],
             'B': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.28)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, dd, m, v, h, who in SUNG:
        for section, tr, dv, gg in parts[who]:
            o.play(section, m + tr, t, dd * 1.02, v + dv, 0.6 * side[who], gg)
    for t, dd, m, v, h, who in ORCH:                # the ritornello and the close on strings
        if h == 0:
            o.play('violins' if m >= 60 else 'violas', m, t, max(dd, 0.25), v - 8, 0.0, 0.32)
        else:
            o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.25), v - 6, 0.0, 0.4)
            if m < 48:
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.3), v - 10, 0.0, 0.35)
    for t, dd, m, v, h, who in SUNG:                # the basses double the chorus's bass line an octave down
        if who == 'B':
            o.play('basses', m, t, dd, v - 12, 0.0, 0.3)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, int(min(100, v)), min(dd, 0.35)) for t, dd, m, v, h, who in ORCH]
    notes += [(t, m, 70, min(dd, 0.3)) for t, dd, m, v, h, who in SUNG if who == 'B']
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.5, 0.0)
    for k, tn in enumerate(NO_MORE):
        o.hit('timpani', tn, 54 + 4 * k, pitch=-5, gain=0.14)
