"""O Rest in the Lord: the angel wakes Elijah for the journey to Horeb, sings him the stillest light in the set, and
the people's warmth comes back around him before night falls on the mountain.

The scene opens where the last one ended: Elijah's amber low at the free end of Side, three silver angels beside
him, the house keeping an even silver watch over the dust of the wilderness. The Angel sings, "Arise, Elijah, for
thou hast a long journey before thee": the middle of the three lights grows and flares on every word while the other
two fade, and Elijah's amber rises from sleep. "Forty days and forty nights shalt thou go to Horeb, the mount of
God": the Angel goes ahead and Elijah walks after it, a step on every word, up Side toward the front of the house,
while days and nights pass over the roofline, a warm wash on "days", a blue one on "nights", and far off on Porch
Front the mount of God glimmers on "God".

"O rest in the Lord, wait patiently for Him, and He shall give thee thy heart's desires": the stillest light in the
set. A soft rose-gold settles over the whole house and holds, with almost no motion: it breathes a little with the
Angel's phrases, and Elijah's amber and the Angel's silver rest together on Side.

"He that shall endure to the end, shall be saved": the people's candles come back on Porch Left and Porch Right and
spread outward along Left and Side until they stand around him, swelling with the chorus to the forte "end" and
quieting for "shall be saved". Then night falls: the candles, the angel and Elijah himself fade into a dark slate
over every run with heaven darker still, and a dry wind stirs the dust, which is how EL20 (The Lord Passed By)
begins.

The music is Mendelssohn's own: the Angel's recitative No. 30 to "the mount of God", the first nine bars of the aria
No. 31 and the first eight of the chorus No. 32, transcribed from the Novello octavo vocal score (the 1870 printing)
into o_rest_in_the_lord.musicxml and timed by scripts/score_excerpt.py at the marked tempos. The Angel is played on
oboe with violas under her, the people on strings with woodwinds doubling and horns on the held notes, the
accompaniment orchestrated from the piano reduction; a production adds a soft timpani roll under the crescendo to
"end" and nothing else.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL19'
TITLE = 'O Rest in the Lord'
KIND = 'show'
DESCRIPTION = ("The angel wakes Elijah for the road to Horeb and sings him the stillest light in the set: O rest in "
               "the Lord. The people's candles return around him, and night falls on the mountain.")
VOICEOVER = 'Arise, and eat. For the journey is too great for thee.'

EX = excerpt(__file__)                      # No. 30 bars 1-6, No. 31 bars 1-9, No. 32 bars 1-8
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
NOTES = EX['notes']
ANGEL = [n for n in NOTES if n[5] == 'Angel']
CHOIR = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_FORTY = BAR[3] + 1.25                     # "For-ty days", Tempo Adagio
T_GOD = BAR[6]
T_ARIA = BAR[34]
T_CHORUS = BAR[68]
T_CRES = BAR[72]
T_END = BAR[73] + 60.0 / 66 * 2             # the forte "end"
T_SAVED = BAR[74]
T_NIGHT = BAR[75] - 0.6                     # night falls through the last "shall be saved"
AN_ON = np.array([n[0] for n in ANGEL])
WALK_ON = AN_ON[(AN_ON >= T_FORTY - 0.01) & (AN_ON < T_ARIA)]
CH_ON = np.array(sorted({round(n[0], 3) for n in CHOIR}))
DAYS = [n[0] for n in ANGEL if T_FORTY - 0.01 <= n[0] < BAR[4]]

DUST = hexc('#3a2008')
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
SILVER = hexc('#d8ecff')                    # the Angel
WATCH = hexc('#b8d0f0')                     # EL18's watch, fading
REST = hexc('#ffc4a0')                      # O rest in the Lord: a soft rose-gold
CANDLE = hexc('#ffcf8a')                    # the people
DAY = hexc('#ffd890')
NIGHTWASH = hexc('#2040a0')
NIGHT = hexc('#3a4c80')                     # EL20's opening: the night on Horeb,
WIND = hexc('#cfe2ff')                      # the first breath of its wind
GRIT = hexc('#6a6058')                      # and the dust it lifts
WIND0 = 0.15 + 0.35 * 0.2756                # EL20's wind level at its first frame (its orchestra's loudness there)

ELIJAH0, ELIJAH1 = 12.0, 330.0              # asleep at the free end of Side; where the walk ends
RESTS = (44.0, 74.0, 104.0)                 # EL18's three angels; the middle one is the Angel


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def elijah_at(t):
    """He walks after the Angel up Side, a step on every word of "Forty days ... the mount of God"."""
    k = np.searchsorted(WALK_ON, t, side='right')
    step = (k - 1 + min((t - WALK_ON[k - 1]) / 0.8, 1.0)) / len(WALK_ON) if k else 0.0
    return ELIJAH0 + (ELIJAH1 - ELIJAH0) * smoothstep(0, 1, step)


def angel_at(t):
    return RESTS[1] + (elijah_at(t) + 45.0 - RESTS[1]) * smoothstep(T_FORTY - 1.0, T_FORTY + 1.0, t)


def phrase(t):
    """The Angel's line in the aria, smoothed: 0..1, slow."""
    on = [(n[0], n[0] + n[1]) for n in ANGEL if n[0] >= T_ARIA - 0.01]
    v = 0.0
    for a, b in on:
        if a - 1.5 <= t <= b + 2.5:
            v = max(v, smoothstep(a - 1.5, a + 0.5, t) * (1 - smoothstep(b, b + 2.5, t)))
    return v


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    heaven = (G.seg_of == 'Porch Front').astype(float)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    l0 = span(G, 'Left')[0]
    flick = Flicker(rng, G.N, 1.5, 5.0)
    cand = np.zeros(G.N)                        # many small lights, every 24 units
    for c in np.arange(20.0, G.length, 24.0):
        cand += np.exp(-((d - c) / 4.5) ** 2)
    pf0, pf1 = span(G, 'Porch Front')
    s_out = np.abs(d - 0.5 * (pf0 + pf1))
    air = 0.5 + 0.5 * np.sin(0.018 * s_out) * np.sin(0.007 * s_out + 1.0)
    porch = ((G.seg_of == 'Porch Left') | (G.seg_of == 'Porch Right'))
    # how far the people's warmth must spread from the porch runs to reach a pixel (0 on the porch)
    reach = np.where(porch, 0.0, np.where(d < pl0, pl0 - d, np.where(d > pr1, d - pr1, 0.0)))
    reach[G.seg_of == 'Porch Front'] = 120.0

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def swell(t0, t, tau):
        """A swell that rises over a quarter of a second to t0 and dies away with tau: no flash."""
        return float(smoothstep(t0 - 0.25, t0, t) * np.exp(-max(t - t0, 0.0) / tau))

    def last(arr, t, tau, span_=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0

    for f in range(F):
        t = f * DT
        night = smoothstep(T_NIGHT, D - 0.15, t)       # 1 at the last frame: EL20's opening
        day = 1 - night
        fr = light(DUST, 0.15 * day * np.ones(G.N))
        fr += light(NIGHT, 0.3 * night * (1 - 0.4 * heaven))
        fr += light(WIND, night * WIND0 * air * (1 - 0.6 * heaven)) + light(GRIT, 0.3 * night * (1 - heaven))

        # EL18's watch fades as he wakes
        fr += light(WATCH, 0.12 * (1 - smoothstep(0.5, 6.0, t)) * np.ones(G.N))

        # days and nights pass over the house on "Forty days and forty nights"
        if T_FORTY - 0.2 <= t < BAR[5]:
            for k, td in enumerate(DAYS):
                a = t - td
                if 0 <= a < 2.0:
                    wash = smoothstep(0, 0.35, a) * (1 - smoothstep(0.5, 2.0, a))
                    col = DAY if k % 2 == 0 else NIGHTWASH
                    fr += light(col, 0.32 * wash * np.ones(G.N))

        # the mount of God, far off on "God"
        if t >= T_GOD - 0.3:
            fr += light(SILVER, 0.3 * smoothstep(T_GOD - 0.3, T_GOD + 1.0, t) * (1 - smoothstep(T_ARIA, T_ARIA + 3, t))
                        * heaven * day)

        # O rest in the Lord: the stillest light, a rose-gold hold that breathes a little with the phrases
        if t >= T_ARIA - 2.0:
            hold = smoothstep(T_ARIA - 2.0, T_ARIA + 3.0, t) * (1 - 0.35 * smoothstep(T_CHORUS - 1, T_CHORUS + 4, t))
            fr += light(REST, hold * (0.34 + 0.035 * phrase(t)) * day * np.ones(G.N))

        # the people's candles: back on the porch runs, spreading out round him, swelling to "end"
        if t >= T_CHORUS - 1.0:
            spread = 60 + 900 * smoothstep(T_CHORUS, T_END, t)
            front = smoothstep(spread, spread - 80, reach)
            loud = (0.35 + 0.15 * smoothstep(T_CRES, T_END, t) + 0.3 * swell(T_END, t, 1.5)
                    - 0.12 * smoothstep(BAR[70], BAR[70] + 1, t) * (1 - smoothstep(T_CRES - 1, T_CRES, t))
                    - 0.1 * smoothstep(T_SAVED, T_SAVED + 1.5, t))
            sung = last(CH_ON, t, 0.6)
            lvl = smoothstep(T_CHORUS - 1.0, T_CHORUS + 1.5, t) * day * front * (loud + 0.12 * sung)
            fr += light(CANDLE, lvl * cand * (0.8 + 0.2 * flick(t)))
            fr += light(CANDLE, 0.4 * swell(T_END, t, 1.0) * day * front * np.ones(G.N))

        # the Angel: the middle light grows on "Arise", the other two fade; it rests by him through the aria
        word = last(AN_ON, t, 0.5)
        sing = 1.0 if t < T_CHORUS else 1 - smoothstep(T_CHORUS, T_CHORUS + 4, t)
        a = angel_at(t)
        fr += light(SILVER, day * sing * (0.35 + 0.3 * word * (t < T_ARIA) + 0.06 * phrase(t)) * blob(a, 9 + 6 * word))
        others = (1 - smoothstep(0.5, 5.0, t)) * 0.35
        for p in (RESTS[0], RESTS[2]):
            fr += light(SILVER, others * blob(p, 9))

        # Elijah: rising from sleep, walking, then still
        e = elijah_at(t)
        wake = smoothstep(0.3, BAR[3], t)
        amb = (0.25 + 0.45 * wake + 0.1 * last(WALK_ON, t, 0.6)) * day
        fr += light(AMBER, amb * blob(e, 24 + 8 * wake) + 0.15 * wake * day * blob(e, 80))
        fr += light(CORE, (0.08 + 0.4 * wake) * day * blob(e, 6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The Angel on oboe with violas under her, Elijah's walk unsounded; the aria's accompaniment on soft strings; the
    people on strings with woodwinds doubling and horns on held notes; a timpani roll under the crescendo to "end"."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.6)
    for t, d, m, v, h, who in ANGEL:
        o.play('oboes', m, t, d, v + 4, pan_at(angel_at(t)), 0.65)
        o.play('violas', m, t, d, v - 12, pan_at(angel_at(t)), 0.25)

    def size(t):
        return 0.6 if t >= T_CHORUS else 0.25

    def role(t, d, m, v, hand):
        if T_ARIA - 0.5 <= t < T_CHORUS - 0.5:          # the aria: soft strings only
            if hand == 0:
                return [('violins' if m >= 55 else 'violas', 0, -14, 0.4)]
            return [('cellos', 0, -10, 0.45)] + ([('basses', -12, -14, 0.3)] if m < 48 else [])
        return None
    o.tutti(ORCH, size=size, role=role)
    parts = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -8, 0.3)], 'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)], 'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4)]}
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in CHOIR:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
        if d >= 0.9:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 10, 0.6 * side[who], 0.3)
    o.hit('timpani roll', T_CRES, 80, pitch=-7, gain=0.25)
    o.hit('timpani', T_END, 100, pitch=-7, gain=0.3)
