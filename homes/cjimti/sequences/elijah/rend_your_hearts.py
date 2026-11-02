"""Rend Your Hearts: Obadiah moves among the people with a promise, and then the chorus cries that God does not see.

The house is still the drought: dust on every run, Porch Front (heaven) dark, the people's candles on Porch Left and
Porch Right. Obadiah's teal light appears at the street end of Porch Left: "Ye people, rend your hearts", each word a
flare. Then his air, "If with all your hearts ye truly seek me, ye shall ever surely find me": with every note he
sings he moves among the people, up Porch Left toward the back of the porch the first time and down Porch Right the
second, and the candles he passes warm and steady. "Thus saith our God": a soft warmth gathers at the porch's back
corners, at the very edge of heaven, and goes no further.

Then the chorus, "Yet doth the Lord see it not: He mocketh at us": hard, low pulses of burnt red beat out of Porch
Front with the orchestra's tremolo and every shout, and run down the porch runs toward the people, and never quite
reach them; the candles shrink from each one. "His curse hath fallen down upon us": the last pulses are the biggest,
falling halfway down the porch and stopping there, and the teal is gone.

The music is Mendelssohn's own: the first bars of No. 3, the first nineteen bars of No. 4 and the first eighteen of
No. 5, transcribed from the Novello octavo vocal score into rend_your_hearts.musicxml and timed by
scripts/score_excerpt.py at the marked tempos. Obadiah is played on violas and clarinet, the people on strings with
woodwinds doubling, and the chorus's tremolo on the strings' tremolo with the brass and timpani on its shouts.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL03'
TITLE = 'Rend Your Hearts'
KIND = 'show'
DESCRIPTION = ("Obadiah's teal light moves among the people with a promise: seek, and ye shall find. "
               "Then the chorus cries that God does not see, and hard red pulses beat from heaven and never reach them.")
VOICEOVER = 'If with all your hearts ye truly seek me, ye shall ever surely find me.'

EX = excerpt(__file__)                      # No. 3 bars 1-2, No. 4 bars 1-19 (3-21), No. 5 bars 1-18 (22-39)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
OBADIAH = [n for n in EX['notes'] if n[5] == 'Obadiah']
T_AIR = BAR[3]
T_SECOND = BAR[12]                          # the air's second "If with all your hearts"
T_THUS = BAR[18]                            # "Thus saith our God"
T_CHORUS = BAR[22]                          # "Yet doth the Lord see it not"
T_CURSE = BAR[36]                           # "His curse hath fallen down upon us"
OB_ON = np.array([n[0] for n in OBADIAH])
# the pulses: every bar of the chorus, and every shout held a beat or longer
PULSES = sorted({round(BAR[m], 2) for m in range(22, 40)} | {round(n[0], 2) for n in SUNG if n[1] >= 0.3})
BEATS = np.array([t for t in PULSES if t >= T_CHORUS - 0.01])

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
TEAL = hexc('#20b0a0')                      # Obadiah
TEAL_CORE = hexc('#b0fff0')
WARM = hexc('#ffd8a0')                      # the promise at heaven's edge
BURNT = hexc('#c03010')                     # the pulses that do not reach


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    up = np.zeros(G.N)                           # 0 at a porch run's street end, 1 at its back corner
    m = G.seg_of == 'Porch Left'
    up[m] = (d[m] - pl0) / (pl1 - pl0)
    m = G.seg_of == 'Porch Right'
    up[m] = (pr1 - d[m]) / (pr1 - pr0)

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)

    # Obadiah's walk: one step for every note he sings; up Porch Left, then down Porch Right
    first = OB_ON[OB_ON < T_SECOND]
    second = OB_ON[OB_ON >= T_SECOND]
    path_t = np.concatenate([[0.0], first, second])
    pos1 = pl0 + 12 + (pl1 - pl0 - 30) * np.linspace(0, 1, len(first) + 1)
    pos2 = pr0 + 12 + (pr1 - pr0 - 30) * np.linspace(0, 1, len(second))
    path_d = np.concatenate([pos1, pos2])
    warmed = np.zeros(G.N)                       # how much the candles he has passed are warmed

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        fr += light(DUST, (0.3 - 0.14 * heaven) * np.ones(G.N))

        # Obadiah: where he is (gliding to each new note's place), flaring on every note
        if t < T_CHORUS + 3:
            k = max(int(np.searchsorted(path_t, t, side='right')) - 1, 0)
            prev = path_d[k] if k in (0, len(first) + 1) else path_d[k - 1]   # he crosses behind heaven unseen
            here = prev + (path_d[k] - prev) * smoothstep(path_t[k], path_t[k] + 0.35, t)
            j = int(np.searchsorted(OB_ON, t, side='right')) - 1
            voice = float(np.exp(-(t - OB_ON[j]) / 0.45)) if j >= 0 else 0.0
            show = smoothstep(0, 1.0, t) * (1 - smoothstep(T_CHORUS, T_CHORUS + 3, t))
            blob = np.exp(-((d - here) / 28) ** 2)
            fr += light(TEAL, show * ((0.75 + 0.25 * voice) * blob + 0.35 * np.exp(-((d - here) / 90) ** 2)))
            fr += light(TEAL_CORE, show * (0.3 + 0.4 * voice) * np.exp(-((d - here) / 5) ** 2))
            warmed = np.maximum(warmed * (1 - DT / 25), np.exp(-((d - here) / 40) ** 2) * people * show)

        # the people: candles, warmed where Obadiah has passed, shrinking from the pulses in the chorus
        lvl = 0.5 + 0.45 * warmed
        if t >= T_CHORUS:
            i = int(np.searchsorted(BEATS, t, side='right')) - 1
            hit = float(np.exp(-(t - BEATS[i]) / 0.25)) if i >= 0 else 0.0
            lvl = lvl * (1 - 0.3 * smoothstep(T_CHORUS, D, t)) * (1 - 0.35 * hit)
        fr += light(CANDLE, cand * people * lvl * (0.75 + 0.25 * flick(t)))

        # "Thus saith our God": warmth at the porch's back corners, at heaven's edge, and no further
        if T_THUS <= t < T_CHORUS + 2:
            g = smoothstep(T_THUS, T_THUS + 2, t) * (1 - smoothstep(T_CHORUS - 0.5, T_CHORUS + 1.5, t))
            fr += light(WARM, 0.55 * g * people * smoothstep(0.7, 1.0, up))

        # the pulses: out of heaven, down the porch runs, stopping short of the people
        if t >= T_CHORUS:
            i0 = int(np.searchsorted(BEATS, t - 1.2))
            i1 = int(np.searchsorted(BEATS, t, side='right'))
            curse = smoothstep(T_CURSE - 0.5, T_CURSE + 0.5, t)
            reach = 0.4 + 0.25 * curse                 # how far down the porch a pulse gets (from the back)
            for i in range(i0, i1):
                a = t - BEATS[i]
                size = 0.85 + 0.4 * curse
                fr += light(BURNT, size * np.exp(-a / 0.3) * heaven)
                front = min(a / 0.45, 1.0) * reach
                band = np.exp(-(((1 - up) - front) / 0.12) ** 2) * ((1 - up) <= reach + 0.02)
                fr += light(BURNT, 0.9 * size * np.exp(-a / 0.7) * band * people)
            fr += light(BURNT, 0.22 * smoothstep(T_CHORUS, T_CHORUS + 1, t) * heaven)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Obadiah on violas and clarinet; the people on strings and woodwinds; the chorus's tremolo on the strings'
    tremolo, with brass and timpani on its shouts."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.6)
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))

    def ob_pan(t):
        return 0.6 * (pl if t < T_SECOND else pr)

    # the accompaniment: strings in the recitative and the air, tremolo strings in the chorus
    def role(t, d, m, v, hand):
        if t >= T_CHORUS - 0.01:
            if d <= 0.07:
                return [('violins trem' if m >= 55 else 'violas trem', 0, -6, 0.35)]
            if hand == 0:
                return [('violins' if m >= 60 else 'violas', 0, -2, 0.5), ('horns', 0, -8, 0.35)]
            return [('cellos', 0, 0, 0.6), ('basses', -12 if m >= 40 else 0, -4, 0.5), ('trombones', 0, -10, 0.35)]
        if hand == 0:
            return [('violins' if m >= 60 else 'violas', 0, -10, 0.4)]
        return [('cellos', 0, -6, 0.5), ('basses', -12 if m >= 40 else 0, -10, 0.35)]
    o.tutti(ORCH, role=role, pan=lambda t, m: 0.0)

    # Obadiah: violas and clarinet
    for t, d, m, v, h, who in OBADIAH:
        o.play('violas', m, t, d, v + 2, ob_pan(t), 0.6)
        o.play('clarinets', m, t, d, v - 6, ob_pan(t), 0.4)

    # the people: strings with woodwinds doubling, brass under the shouts
    parts = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -8, 0.3)],
             'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)],
             'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
        if d >= 0.5:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 8, 0.6 * side[who], 0.35)

    # the pulses: timpani and low brass on each shout, a roll under the curse
    for t in BEATS:
        if any(abs(t - s[0]) < 0.02 for s in SUNG):
            o.hit('timpani', t, 104, pitch=-5, gain=0.3)
    o.hit('timpani roll', T_CURSE, 112, pitch=-5, gain=0.45)
    o.hit('cymbal swell', T_CURSE + 1.5, 96, gain=0.3)
    o.boom(BAR[39], gain=0.6)
