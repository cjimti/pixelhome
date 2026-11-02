"""Before Ahab: after three years of drought Elijah faces the king, and sets the challenge of the two altars.

The scene opens where the last one ended, the widow and her son on Left, and they fade as Elijah's amber sets out:
"As God the Lord of Sabaoth liveth, before whom I stand". With every word he takes he travels the roofline, across
the porch, back to his place on Right, where he waits in the dust of the third year.

The orchestra breaks into the Allegro vivace and Ahab comes: an iron grey that pulses with every throb of the strings
and advances along the roofline from Left, over the porch, louder and nearer, until it stands at the corner of
Right facing the amber, and flashes with the orchestra's last chords. "Art thou Elijah? art thou he that troubleth
Israel?": the grey flares with every word. The people take it up, "Thou art Elijah, thou he that troubleth Israel":
their candles on Porch Left and Porch Right go grey and beat toward Right. "I never troubled Israel's peace: it is
thou, Ahab, and all thy father's house": the amber blazes, the grey falls back up Porch Right and the candles warm
again.

Then the challenge. "Rise then, ye priests of Baal; select and slay a bullock, and put no fire": a burnished bronze
altar rises on Left, glinting brass, a little more with every word. "And the God who by fire shall answer, let Him be
God": at the far end of Right, by Elijah, the other altar appears, unlit wood, dark. The people answer, "Yea, and the
God who by fire shall answer, let Him be God", their candles swelling between the two altars, while the grey fades.
Porch Front, heaven, stays dark.

The music is Mendelssohn's own: six passages of No. 10, transcribed from the Novello octavo vocal score into
before_ahab.musicxml and timed by scripts/score_excerpt.py at the marked tempos. Elijah is played on cellos and
horns, Ahab on bassoons, the people on strings with woodwinds doubling.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL06'
TITLE = 'Before Ahab'
KIND = 'show'
DESCRIPTION = ("Ahab's iron grey comes at Elijah's amber: thou art he that troubleth Israel. Elijah throws it back and "
               "sets the challenge, and two altars appear: bronze for Baal on Left, unlit wood on Right.")
VOICEOVER = 'And the God who answers by fire, let Him be God.'

EX = excerpt(__file__)                      # No. 10 bars 2-5, 14-35, 63-65, 71-84
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
AHAB = [n for n in EX['notes'] if n[5] == 'Ahab']
T_ALLEGRO = BAR[14]
T_AHAB = BAR[22]
T_PEOPLE = BAR[27]
T_REPLY = BAR[32]
T_RISE = BAR[63]
T_FIRE = BAR[71]                            # "and the God who by fire shall answer"
T_YEA = BAR[78]
EL_ON = np.array([n[0] for n in ELIJAH])
AH_ON = np.array([n[0] for n in AHAB])
PULSE = np.array(sorted({round(n[0], 3) for n in ORCH if T_ALLEGRO - 0.01 <= n[0] < T_AHAB}))
CHORUS1 = np.array(sorted({round(n[0], 3) for n in SUNG if T_PEOPLE - 0.01 <= n[0] < T_REPLY}))
CHORUS2 = np.array(sorted({round(n[0], 3) for n in SUNG if n[0] >= T_YEA - 0.01}))
RISE_ON = EL_ON[(EL_ON >= T_RISE - 0.01) & (EL_ON < T_FIRE)]

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
ROSE = hexc('#e07a8a')                      # the widow, fading
SON = hexc('#ffd8a0')
GREY = hexc('#8a8f98')                      # Ahab
STEEL = hexc('#d0d6e0')
BRONZE = hexc('#b06a10')                    # Baal's altar
GLINT = hexc('#ffcc55')
WOOD = hexc('#5a3a1e')                      # Elijah's altar, unlit


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    return dict(left_start=l0 + 0.2 * (l1 - l0), son=l0 + 0.58 * (l1 - l0), widow=l0 + 0.8 * (l1 - l0),
                home=r0 + 0.35 * (r1 - r0), ahab_from=l0 + 0.35 * (l1 - l0), ahab_at=r0 + 0.08 * (r1 - r0),
                baal=(l0 + 0.15 * (l1 - l0), l0 + 0.55 * (l1 - l0)), wood=(r0 + 0.6 * (r1 - r0), r0 + 0.85 * (r1 - r0)))


def elijah_at(G, t):
    """Elijah walks back from Left to his place on Right, a step with every word of the oath."""
    p = places(G)
    oath = EL_ON[EL_ON < T_ALLEGRO]
    k = np.searchsorted(oath, t, side='right')
    step = (k - 1 + min((t - oath[k - 1]) / 0.9, 1.0)) / len(oath) if k else 0.0
    return p['left_start'] + (p['home'] - p['left_start']) * smoothstep(0, 1, step)


def ahab_at(G, t):
    """Ahab advances with the Allegro, falls back at Elijah's answer."""
    p = places(G)
    come = smoothstep(T_ALLEGRO, T_AHAB - 1.0, t)
    pr0, pr1 = span(G, 'Porch Right')
    back = smoothstep(T_REPLY, T_REPLY + 4.0, t) * (p['ahab_at'] - (pr0 + 0.4 * (pr1 - pr0)))
    return p['ahab_from'] + (p['ahab_at'] - p['ahab_from']) * come - back


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    p = places(G)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    up = np.zeros(G.N)                           # 0 at a porch run's street end, 1 at its back corner
    m = G.seg_of == 'Porch Left'
    up[m] = (d[m] - pl0) / (pl1 - pl0)
    m = G.seg_of == 'Porch Right'
    up[m] = (pr1 - d[m]) / (pr1 - pr0)
    rightward = np.where(G.seg_of == 'Porch Left', 1 - up, up)      # toward Right along each porch run

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    glint = Flicker(rng, G.N, 3.0, 9.0)
    b0, b1 = p['baal']
    w0, w1 = p['wood']
    baal = smoothstep(b0, b0 + 12, d) * (1 - smoothstep(b1 - 12, b1, d))
    wood = smoothstep(w0, w0 + 10, d) * (1 - smoothstep(w1 - 10, w1, d))

    for f in range(F):
        t = f * DT
        fr = light(DUST, 0.28 * np.ones(G.N))

        # the people: candles, gone grey and beating toward Right in "Thou art Elijah", swelling in "Yea"
        grey = smoothstep(T_PEOPLE - 0.5, T_PEOPLE + 0.5, t) * (1 - smoothstep(T_REPLY + 1.0, T_REPLY + 4.0, t))
        lvl = 0.4 + 0.3 * smoothstep(T_YEA - 1.0, T_YEA + 2.0, t)
        i = int(np.searchsorted(CHORUS2, t, side='right')) - 1
        if i >= 0:
            lvl = lvl + 0.25 * np.exp(-(t - CHORUS2[i]) / 0.5)
        flame = cand * people * lvl * (0.75 + 0.25 * flick(t))
        fr += light(CANDLE, flame * (1 - 0.8 * grey)) + light(GREY, flame * 1.3 * grey)
        if grey > 0.01:
            i0 = int(np.searchsorted(CHORUS1, t - 1.0))
            i1 = int(np.searchsorted(CHORUS1, t, side='right'))
            for k in range(i0, i1):
                a = t - CHORUS1[k]
                band = np.exp(-((rightward - min(a / 0.7, 1.0)) / 0.12) ** 2)
                fr += light(GREY, 0.9 * grey * np.exp(-a / 0.6) * band * people)

        # the widow and her son, fading as the scene changes
        fade = 1 - smoothstep(0.5, 3.5, t)
        if fade > 0:
            fr += light(ROSE, 0.7 * fade * np.exp(-((d - p['widow']) / 24) ** 2))
            fr += light(SON, 0.85 * fade * np.exp(-((d - p['son']) / 6) ** 2))

        # Elijah
        e = elijah_at(G, t)
        j = int(np.searchsorted(EL_ON, t, side='right')) - 1
        voice = float(np.exp(-(t - EL_ON[j]) / 0.5)) if j >= 0 else 0.0
        blaze = smoothstep(T_REPLY - 0.2, T_REPLY + 0.4, t) * (1 - smoothstep(T_REPLY + 6, T_RISE, t))
        size = 16 * (1 + 0.6 * blaze)
        fr += light(AMBER, (0.7 + 0.3 * voice + 0.25 * blaze) * np.exp(-((d - e) / size) ** 2)
                    + (0.15 + 0.25 * blaze) * np.exp(-((d - e) / 60) ** 2))
        fr += light(CORE, (0.45 + 0.4 * voice) * np.exp(-((d - e) / 5) ** 2))

        # Ahab: iron grey, pulsing with the Allegro, flaring with his words, fading through the challenge
        if t >= T_ALLEGRO:
            a = ahab_at(G, t)
            i = int(np.searchsorted(PULSE, t, side='right')) - 1
            beat = float(np.exp(-(t - PULSE[i]) / 0.12)) if i >= 0 and t < T_AHAB + 0.3 else 0.0
            j = int(np.searchsorted(AH_ON, t, side='right')) - 1
            word = float(np.exp(-(t - AH_ON[j]) / 0.45)) if j >= 0 else 0.0
            loud = 0.45 + 0.4 * smoothstep(T_ALLEGRO, BAR[20], t)
            gone = 1 - 0.85 * smoothstep(T_FIRE, D - 1.0, t)
            g = (loud + 0.35 * beat + 0.45 * word) * gone * smoothstep(T_ALLEGRO, T_ALLEGRO + 1.0, t)
            fr += light(GREY, g * (np.exp(-((d - a) / 22) ** 2) + 0.3 * np.exp(-((d - a) / 70) ** 2)))
            fr += light(STEEL, (0.3 * beat + 0.5 * word) * gone * np.exp(-((d - a) / 6) ** 2))
            if BAR[20] <= t < T_AHAB:                    # the orchestra's last chords: the grey flashes wide
                for tc in (BAR[20] + 0.83, BAR[21], BAR[21] + 0.83):
                    if 0 <= t - tc < 0.8:
                        fr += light(GREY, 0.6 * np.exp(-(t - tc) / 0.25) * np.exp(-((d - a) / 120) ** 2))

        # the altars: Baal's bronze rising word by word, then the unlit wood on Right
        if t >= T_RISE:
            k = int(np.searchsorted(RISE_ON, t, side='right'))
            grow = min(k / max(len(RISE_ON), 1), 1.0)
            fr += light(BRONZE, (0.2 + 0.55 * grow) * baal)
            fr += light(GLINT, 0.45 * grow * baal * np.maximum(glint(t) - 0.6, 0) * 2.5)
        if t >= T_FIRE:
            fr += light(WOOD, 0.75 * smoothstep(T_FIRE, T_FIRE + 2.0, t) * wood)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Elijah on cellos and horns, Ahab on bassoons, the people on strings with woodwinds doubling, the Allegro on the
    full strings with brass and timpani on its last chords."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    p = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.7)
    loud = lambda t: 0.4 + 0.6 * smoothstep(T_ALLEGRO, BAR[20], t) if T_ALLEGRO <= t < T_AHAB else (
        1.0 if T_PEOPLE <= t < T_REPLY or t >= T_YEA else 0.4)
    o.tutti(ORCH, size=loud, pan=lambda t, m: 0.5 * pan_at(ahab_at(G, t)) if T_ALLEGRO <= t < T_REPLY else 0.0)

    for t, d, m, v, h, who in ELIJAH:
        e = elijah_at(G, t)
        o.play('cellos', m, t, d, v + 2, pan_at(e), 0.6)
        o.play('horns', m, t, d, v - 6, pan_at(e), 0.4)
    for t, d, m, v, h, who in AHAB:
        o.play('bassoons', m, t, d, v + 4, pan_at(ahab_at(G, t)), 0.65)
        o.play('violas', m, t, d, v - 10, pan_at(ahab_at(G, t)), 0.25)

    parts = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -8, 0.3)],
             'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)],
             'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4)]}
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
        if d >= 0.5:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 8, 0.6 * side[who], 0.35)
    for tc in (BAR[20] + 0.83, BAR[21], BAR[21] + 0.83):
        o.hit('timpani', tc, 112, pitch=-5, gain=0.4, pan=pan_at(p['ahab_at']))
    o.hit('timpani roll', BAR[19], 96, pitch=-5, gain=0.3)
    for t in RISE_ON[::3]:
        o.hit('anvil', t, 70, gain=0.08, pan=pan_at(0.5 * sum(p['baal'])))
    o.hit('cymbal swell', BAR[82] - 1.0, 96, gain=0.25)
    o.hit('timpani', BAR[82], 110, pitch=-5, gain=0.35)
