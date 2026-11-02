"""Help, Lord!: the people cry out in the drought, the harvest falls away, and they lift their prayer to a silent sky.

The house is the drought EL01 left: dry ochre dust on every run, Porch Front (heaven) dark, the people's candles low
on Porch Left and Porch Right. The chorus cries "Help, Lord!" three times: on each cry every candle flares and the
flare runs up both porch runs toward heaven, then gutters back, lower each time. Under them the orchestra's chords
rush down and up the scale, and a hot wind of ochre sweeps the wings with them, out to the ends of Left and Right
and back. "Wilt thou quite destroy us?": the candles shrink from the back of the porch toward the street.

Then "The harvest now is over, the summer days are gone": the voices enter one after another, and every note they
sing lets fall a band of harvest gold from the back of the porch, down the porch runs toward the street and out
along the wings, fading as it goes, a slow downward wave for each voice. Last the chorus in unison, "Lord, bow thine
ear to our pray'r!": the candles lift, light climbing both porch runs to the very edge of heaven, and Porch Front
stays dark.

The music is Mendelssohn's own: No. 1's first fourteen bars and the unison chorus that opens No. 2, transcribed
from the Novello octavo vocal score into help_lord.musicxml and timed by scripts/score_excerpt.py at the marked
tempos (Andante lento at crotchet 76; Sostenuto, quaver 100). The people are on strings with woodwinds doubling, the
rushing chords on the strings with the brass under the cries; a production adds the dry wind.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL02'
TITLE = 'Help, Lord!'
KIND = 'show'
DESCRIPTION = ("The people cry out in the drought, their candles flaring up the porch toward heaven and guttering back. "
               "The harvest falls away in slow golden waves, and their prayer climbs to a sky that stays dark.")
VOICEOVER = 'Three years without rain. The people cried out: help, Lord.'

EX = excerpt(__file__)                      # No. 1 bars 1-14, No. 2 bars 0-4 (15-19)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
CRIES = [BAR[1], BAR[3], BAR[5]]            # "Help, Lord!"
T_DESTROY = BAR[6]                          # "wilt thou quite destroy us?"
T_HARVEST = BAR[9] + 0.75 * (BAR[10] - BAR[9])   # the tenors' "The harvest now is over"
T_PRAYER = BAR[15]                          # No. 2: "Lord, bow thine ear to our pray'r!"
# the rushing chords: the right hand's eighth-note chords in bars 1-9, one sweep a half bar
SWEEPS = sorted({round(n[0], 3) for n in ORCH if n[4] == 0 and n[0] < BAR[9] + 0.5 * (BAR[10] - BAR[9])})
# every note of "The harvest now is over" in the voices
HARVEST = [(n[0], n[5]) for n in SUNG if T_HARVEST - 0.05 <= n[0] < T_PRAYER]
PRAYER = [n[0] for n in SUNG if n[0] >= T_PRAYER - 0.05]

DUST = hexc('#3a2008')                      # the drought
OCHRE = hexc('#a06018')                     # the hot wind
CANDLE = hexc('#ffcf8a')                    # the people
FLAME = hexc('#ffe2b0')
GOLD = hexc('#c89030')                      # the harvest
AMBER = hexc('#ffb040')                     # Elijah's ember, gone at the start


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pl0, pl1 = span(G, 'Porch Left')            # front (street) -> back
    pf0, pf1 = span(G, 'Porch Front')
    pr0, pr1 = span(G, 'Porch Right')           # back -> front (street)
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    wings = np.isin(G.seg_of, ['Left', 'Right', 'Side'])
    # height on the porch: 0 at the street end of a porch run, 1 at its back corner by heaven
    up = np.zeros(G.N)
    m = G.seg_of == 'Porch Left'
    up[m] = (d[m] - pl0) / (pl1 - pl0)
    m = G.seg_of == 'Porch Right'
    up[m] = (pr1 - d[m]) / (pr1 - pr0)
    # distance out from the porch along the wings (0 at the porch corners, 1 at the ends), for the hot wind
    out_w = np.zeros(G.N)
    m = G.seg_of == 'Left'
    out_w[m] = (l1 - d[m]) / (l1 - l0)
    m = G.seg_of == 'Side'
    out_w[m] = 1.0 + (span(G, 'Side')[1] - d[m]) / 600
    m = G.seg_of == 'Right'
    out_w[m] = (d[m] - r0) / (r1 - r0)
    # how far a falling harvest band has come: 0 at heaven's corners, 1 at the porch's street ends, 2 at the wing ends
    fall = np.where(people, 1 - up, 1 + np.clip(out_w, 0, 1.3))
    fall[heaven] = -0.2

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    gutter = Flicker(rng, G.N, 0.6, 3.0)
    cries = np.array(CRIES)
    sweeps = np.array(SWEEPS)
    harvest = np.array([t for t, _ in HARVEST])
    prayer = np.array(PRAYER)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))

        # the drought on every run, heaven darker
        fr += light(DUST, (0.3 - 0.14 * heaven) * np.ones(G.N))
        # Elijah's ember on Right from the last scene, fading
        if t < 4:
            fr += light(AMBER, 0.25 * (1 - t / 4) * np.exp(-((d - (r0 + 0.3 * (r1 - r0))) / 60) ** 2))

        # the hot wind: every rushing chord pushes a front of ochre out along the wings and back
        if len(sweeps) and sweeps[0] <= t < BAR[10]:
            i = int(np.searchsorted(sweeps, t, side='right')) - 1
            k = i % 8                                   # eight chords a bar: four down, four up
            pos = (k + (t - sweeps[i]) / max(sweeps[min(i + 1, len(sweeps) - 1)] - sweeps[i], 0.1)) / 4
            front = pos if pos <= 1 else 2 - pos        # out to the ends, then back
            strength = 0.75 * (1 - smoothstep(BAR[8], BAR[10], t))
            fr += light(OCHRE, strength * wings * np.exp(-((out_w - front) / 0.25) ** 2))

        # the people: candles on the porch runs; each cry flares them and runs the flare up toward heaven
        level = 0.55
        k = int(np.searchsorted(cries, t, side='right')) - 1
        if k >= 0:
            a = t - cries[k]
            level = 0.55 + (0.9 - 0.15 * k) * np.exp(-a / 2.2)
            run = smoothstep(0, 1.2, a)
            fr += light(FLAME, (1.0 - 0.15 * k) * np.exp(-a / 1.6) * people * np.exp(-((up - run) / 0.3) ** 2))
        if t >= T_DESTROY:                              # "destroy us?": the candles shrink from the back
            shrink = smoothstep(T_DESTROY, BAR[8], t)
            level *= 1 - 0.45 * shrink * smoothstep(0.2, 0.9, up)
            level = level * (1 - 0.25 * smoothstep(T_DESTROY, BAR[8], t))
        if t >= T_PRAYER:                               # the prayer: they lift again
            level = level + 0.35 * smoothstep(T_PRAYER, T_PRAYER + 2, t)
        g = 0.7 + 0.3 * flick(t) - 0.25 * np.clip(gutter(t) - 0.6, 0, 1)
        fr += light(CANDLE, cand * people * level * g)

        # the harvest falls: a band of gold from heaven's corners down the porch and out the wings, one for each note
        if len(harvest):
            j0 = np.searchsorted(harvest, t - 6.0)
            j1 = np.searchsorted(harvest, t, side='right')
            for j in range(j0, j1):
                a = t - harvest[j]
                pos = a / 2.6                              # how far it has fallen
                fade = np.exp(-a / 2.4)
                fr += light(GOLD, 0.7 * fade * np.exp(-((fall - pos) / 0.12) ** 2) * (~heaven))

        # the prayer climbs: light up both porch runs to the edge of heaven, and heaven gives nothing back
        if len(prayer) and t >= prayer[0]:
            i = int(np.searchsorted(prayer, t, side='right')) - 1
            a = t - prayer[i]
            climb = smoothstep(T_PRAYER, D - 1.5, t)
            fr += light(FLAME, (0.25 + 0.35 * np.exp(-a / 0.6)) * people * smoothstep(climb - 0.35, climb, up)
                        * (up <= climb + 0.02))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The people on strings with woodwinds doubling, the brass under the cries; the rushing chords on the strings;
    a dry wind."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.6)
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))

    # the orchestra: the rushing chords on violins and violas, the bass on cellos and basses
    def role(t, d, m, v, hand):
        if hand == 0:
            if t < BAR[9] + 0.5 * (BAR[10] - BAR[9]):
                return [('violins' if m >= 60 else 'violas', 0, -8, 0.45)]
            return [('violins' if m >= 60 else 'violas', 0, -12, 0.3)]
        return [('cellos', 0, -4, 0.55), ('basses', -12 if m >= 40 else 0, -8, 0.45)]
    o.tutti(ORCH, role=role)

    # the people: strings with woodwinds doubling, the brass under the cries of "Help, Lord!"
    parts = {'S': [('violins', 0, -4, 0.5), ('oboes', 0, -10, 0.3), ('flutes', 0, -12, 0.25)],
             'A': [('violas', 0, -4, 0.5), ('clarinets', 0, -10, 0.3)],
             'T': [('cellos', 0, -4, 0.5), ('bassoons', 0, -10, 0.3)],
             'B': [('cellos', 0, -4, 0.45), ('basses', -12, -8, 0.4)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
        if t < BAR[8] and d > 1.5:                       # the cries: horns and trombones under them
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 6, 0.6 * side[who], 0.45)
            if who in ('T', 'B'):
                o.play('trombones', m, t, d, v - 8, 0.6 * side[who], 0.4)
    for t in CRIES:
        o.hit('timpani roll', t, 104, pitch=-2, gain=0.35)
        o.hit('cymbal swell', t - 1.2, 80, gain=0.2)

    # the drought: a dry wind that follows the rushing chords, then drops away for the prayer
    o.effects([(0, -10), (BAR[9], -14), (T_PRAYER, -18)])
    o.wind(0, D + 1, level=lambda tt: 0.45 - 0.3 * smoothstep(BAR[8], T_PRAYER, tt), seed=22)
