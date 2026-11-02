"""Hear Ye, Israel: the second part opens with a voice from heaven calling to the people, and the chorus answers.

The scene opens where the first part ended: the rain has come, a calm blue over the whole house, the people's
candles warm on Porch Left and Porch Right, Elijah's amber at his place on Right and a faint silver on Porch Front.
In the Adagio's introduction the rain ebbs to a hush and heaven brightens a little with each of the orchestra's
sforzandos.

Then the soprano: "Hear ye, Israel! Hear what the Lord speaketh". Her voice is silver on Porch Front, a point that
swells with every note and widens as the line climbs, and at the start of each phrase a silver call runs from the
back of the porch down Porch Left and Porch Right toward the street, where the people are; their candles lift as it
reaches them. On "Oh, hadst thou heeded my commandments" the silver dims and the call falls short.

"Be not afraid, saith God the Lord": the chorus breaks in, forte, and warm light fills the house from the porch
outward. The sopranos and altos flare on Porch Left, the tenors and basses on Porch Right, every syllable a beat of
gold, and the warmth spreads out over Left, Right and Side, a little farther with every "thy help is near", until
the whole house stands in full warm light on the last chord, held. Elijah's amber stays on Right through it all.

The music is Mendelssohn's own: No. 21's Adagio to "hear what the Lord speaketh:" and the first twenty bars of No.
22, transcribed from the Novello octavo vocal score into hear_ye_israel.musicxml and timed by
scripts/score_excerpt.py at the marked tempos. The soprano is played on flutes and an oboe, the chorus on strings
with woodwinds doubling and horns on the long notes, over an organ-pedal G on basses and tuba.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL15'
TITLE = 'Hear Ye, Israel'
KIND = 'show'
DESCRIPTION = ("A silver voice on Porch Front calls to the people: Hear ye, Israel. The chorus answers, be not afraid, "
               "and warm light fills the house from the porch outward.")
VOICEOVER = 'Hear ye, Israel. Be not afraid, saith God the Lord: thy help is near.'

EX = excerpt(__file__)                      # No. 21 bars 1-17, No. 22 bars 1-20 (18-37)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SOLO = [n for n in EX['notes'] if n[5] == 'Soprano']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
T_SING = BAR[6]                             # "Hear ye, Israel!"
T_HEED = BAR[10]                            # "Oh, hadst thou heeded"
T_AGAIN = BAR[14]                           # "Hear ye, Israel!" again
T_CHORUS = BAR[18]                          # "Be not afraid"
T_LAST = BAR[37]                            # "near.", the last chord
SOLO_ON = np.array([n[0] for n in SOLO])
PHRASES = [T_SING, BAR[8], T_HEED, T_AGAIN, BAR[16]]
SF = [BAR[2], BAR[3]]
HIGH = np.array(sorted({round(n[0], 3) for n in SUNG if n[5] in ('S', 'A')}))
LOW = np.array(sorted({round(n[0], 3) for n in SUNG if n[5] in ('T', 'B')}))
NEAR = [BAR[22], BAR[29], BAR[35], T_LAST]  # each "thy help is near" lands

RAIN = hexc('#2060ff')                      # the first part's last frame
CANDLE = hexc('#ffcf8a')                    # the people
GOLD = hexc('#ffb860')
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
SILVER = hexc('#d8ecff')                    # the voice from heaven
WHITE = hexc('#ffffff')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def home(G):
    r0, r1 = span(G, 'Right')
    return r0 + 0.35 * (r1 - r0)


def reach(G):
    """How far from the porch each pixel is: 0 on the porch runs and Porch Front, 1 at the free ends of the house."""
    d = G.pd
    l0, l1 = span(G, 'Porch Left')
    r0, r1 = span(G, 'Porch Right')
    out = np.zeros(G.N)
    left = d < l0
    out[left] = (l0 - d[left]) / l0
    right = d > r1
    out[right] = (d[right] - r1) / (d.max() - r1)
    return out


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    people = np.isin(seg, ['Porch Left', 'Porch Right'])
    left_people = seg == 'Porch Left'
    right_people = seg == 'Porch Right'
    heaven = seg == 'Porch Front'
    pf0, pf1 = span(G, 'Porch Front')
    mid = 0.5 * (pf0 + pf1)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    down = np.zeros(G.N)                        # 0 at a porch run's back corner, 1 at its street end
    down[left_people] = (pl1 - d[left_people]) / (pl1 - pl0)
    down[right_people] = (d[right_people] - pr0) / (pr1 - pr0)
    far = reach(G)
    e = home(G)

    cand = np.zeros(G.N)
    for s in ('Porch Left', 'Porch Right'):
        a, b = span(G, s)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    cand = np.minimum(cand, 1.0)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.4, 1.4)
    sparkle = Flicker(rng, G.N, 5.0, 12.0)

    for f in range(F):
        t = f * DT
        # the rain, ebbing in the introduction to a hush that stays under the whole scene
        rain = 0.18 - 0.08 * smoothstep(0.0, T_SING, t)
        edge = np.zeros(G.N)
        if t >= T_CHORUS - 0.05:                    # how far the chorus's warmth has spread from the porch
            spread = keys(t, [(T_CHORUS, 0.05), (T_CHORUS + 2.0, 0.15)]
                          + [(tn, v) for tn, v in zip(NEAR, (0.35, 0.6, 0.85, 1.08))])
            edge = smoothstep(spread + 0.08, spread - 0.08, far)
        fr = light(RAIN, rain * (0.9 + 0.1 * shimmer(t)) * (1 - 0.85 * edge))   # the blue gives way to the warmth

        # the people: candles warm, lifting when the call reaches them, swelling into the chorus
        lift = 0.0
        for tp in PHRASES:
            a = t - tp - 0.9
            if 0 <= a < 3.0:
                lift = max(lift, np.exp(-a / 0.9) * (0.5 if tp == T_HEED else 1.0))
        flame = 0.6 - 0.15 * smoothstep(1.0, T_SING, t) + 0.15 * lift
        fr += light(CANDLE, cand * people * flame * (0.8 + 0.2 * flick(t)))

        # Elijah, steady at his place on Right
        fr += light(AMBER, 0.55 * np.exp(-((d - e) / 16) ** 2) + 0.12 * np.exp(-((d - e) / 60) ** 2))
        fr += light(CORE, 0.4 * np.exp(-((d - e) / 5) ** 2))

        # heaven: the faint silver of the first part's end, brightening at the introduction's sforzandos
        sky = 0.15 + 0.1 * smoothstep(0.0, T_SING, t)
        for ts in SF:
            if t >= ts:
                sky += 0.25 * np.exp(-(t - ts) / 0.8)
        fr += light(SILVER, sky * heaven)

        # the soprano: a silver voice in the middle of Porch Front, swelling with every note, wider as she climbs
        if T_SING - 0.5 <= t < T_CHORUS + 2.0:
            j = int(np.searchsorted(SOLO_ON, t, side='right')) - 1
            if j >= 0:
                n = SOLO[j]
                held = 1.0 if t < n[0] + n[1] else np.exp(-(t - n[0] - n[1]) / 0.5)
                note = np.exp(-(t - n[0]) / 0.6)
                width = 18 + 3.0 * (n[2] - 64)
                fade = 1 - smoothstep(T_CHORUS, T_CHORUS + 2.0, t)
                lvl = (0.45 + 0.4 * note) * held * fade * smoothstep(T_SING - 0.5, T_SING, t)
                fr += light(SILVER, lvl * np.exp(-((d - mid) / width) ** 2) * heaven)
                fr += light(WHITE, 0.5 * note * held * fade * np.exp(-((d - mid) / 5) ** 2))
            # each phrase: a silver call running down the porch runs to the people
            for tp in PHRASES:
                a = t - tp
                if 0 <= a < 2.5:
                    short = 0.55 if tp == T_HEED else 1.0
                    front = min(a / 1.1, short)
                    band = np.exp(-((down - front) / 0.12) ** 2)
                    fr += light(SILVER, 0.85 * np.exp(-a / 1.2) * band * people)

        # the chorus: gold beats on the porch runs, warmth filling the house from the porch outward
        if t >= T_CHORUS - 0.05:
            # the warmth: a step farther out with every "thy help is near", all the way out by the last chord
            warm = 0.35 + 0.35 * smoothstep(T_CHORUS, D - 2.0, t)
            fr += light(GOLD, warm * edge * (0.85 + 0.15 * flick(t)))
            fr += light(GOLD, 0.35 * heaven * smoothstep(T_CHORUS, T_CHORUS + 1.0, t))
            for onsets, mask in ((HIGH, left_people), (LOW, right_people)):
                i = int(np.searchsorted(onsets, t, side='right')) - 1
                if i >= 0:
                    beat = np.exp(-(t - onsets[i]) / 0.35)
                    fr += light(CANDLE, 0.75 * beat * mask * (0.6 + 0.4 * cand))
                    fr += light(WHITE, 0.4 * beat * mask * cand * np.maximum(sparkle(t), 0))
            if t >= T_LAST:                        # the last chord: the whole house, held
                a = t - T_LAST
                fr += light(WHITE, 0.35 * np.exp(-a / 0.5))
                fr += light(GOLD, 0.2 * smoothstep(0.0, 0.4, a))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The soprano on flutes and an oboe in the middle of the porch; the chorus on strings with woodwinds doubling,
    sopranos and altos to the left, tenors and basses to the right; No. 21's accompaniment on soft strings, No. 22's
    doubling on the full orchestra with the organ pedal on basses and tuba."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    mid = 0.5 * sum(span(G, 'Porch Front'))
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))

    o = Orchestra(M, level=1.05)
    adagio = [n for n in ORCH if n[0] < T_CHORUS - 0.01]
    chorus = [n for n in ORCH if n[0] >= T_CHORUS - 0.01]
    o.tutti(adagio, size=lambda t: 0.25)
    pedal = [n for n in chorus if n[2] <= 43]
    o.tutti([n for n in chorus if n[2] > 43], size=lambda t: 0.9, pan=lambda t, m: 0.3 * (pl if m >= 60 else pr))
    for t, d, m, v, h, who in pedal:
        o.play('basses', m + (12 if m < 40 else 0), t, d, v, 0.0, 0.6)
        o.play('tuba', m + 12, t, d, v - 6, 0.0, 0.5)

    for t, d, m, v, h, who in SOLO:
        o.play('flutes', m, t, d, v + 6, pan_at(mid), 0.65)
        o.play('oboes', m, t, d, v - 4, pan_at(mid), 0.35)
        if d >= 0.8:
            o.play('violins', m, t, d, v - 14, pan_at(mid), 0.2)

    parts = {'S': [('violins', 0, -2, 0.5), ('flutes', 0, -10, 0.3), ('oboes', 0, -10, 0.25)],
             'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)],
             'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
        if d >= 0.5:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 8, 0.6 * side[who], 0.35)

    for ts in SF:
        o.hit('timpani', ts, 70, pitch=-1, gain=0.15, pan=pan_at(mid))
    o.hit('cymbal swell', T_CHORUS - 2.2, 80, gain=0.2, pan=pan_at(mid))
    o.hit('timpani roll', T_CHORUS - 1.2, 88, pitch=-5, gain=0.25)
    o.hit('timpani', T_CHORUS, 108, pitch=-5, gain=0.4)
    for tn in NEAR[:-1]:
        o.hit('timpani', tn, 96, pitch=-5, gain=0.25)
    o.hit('timpani roll', T_LAST - 2.0, 100, pitch=-1, gain=0.3)
    o.hit('timpani', T_LAST, 116, pitch=-1, gain=0.45)
    o.hit('crash', T_LAST, 96, gain=0.25)
