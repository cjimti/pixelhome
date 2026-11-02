"""The Queen: Jezebel stirs the people against Elijah, and the chorus cries woe to him.

The scene opens where the last one ended, the whole house in warm light after "Be not afraid", Elijah's amber on
Right. In the hushed chords before the Queen sings, the warmth drains away and a stain of wine appears in the middle
of Left: Jezebel. "Have ye not heard he hath prophesied against all Israel?": her wine pulses with every word, and
after each of her questions it seeps a little farther, from Left onto Porch Left, over the people. The people answer,
"We heard it with our ears": their candles flicker on the porch runs, tinted wine, more with every answer.

Her oath, "The gods do so to me, and more, if by to-morrow about this time I make not his life as the life of one of
them", swells over a shimmering tremolo, and the wine runs the length of both porch runs; at "the brook of Kishon!"
it flashes. "He shall perish!": the chorus breaks out forte and the porch runs blaze wine-red on every syllable,
while Porch Front, heaven, stays dark.

"Woe to him!": the chorus of No. 24 turns on Elijah. A wall of wine comes down Porch Right and along Right toward
his amber, a step nearer with each "woe" and each "spoken", from both sides, until on "the name of the Lord?" it
rings him close and his light has shrunk to a small glow.

The music is Mendelssohn's own: the Queen's dialogue with the chorus and her oath from No. 23 and the first ten bars
of No. 24, transcribed from the Novello octavo vocal score into the_queen.musicxml and timed by
scripts/score_excerpt.py at the marked tempos. Jezebel is played on a low clarinet with a bassoon under her, the
chorus on strings with trombones under her crowd.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL16'
TITLE = 'The Queen'
KIND = 'show'
DESCRIPTION = ("Jezebel's wine spreads from Left through the people: have ye not heard? The chorus cries he shall "
               "perish, and woe to him closes in on Elijah's amber on Right.")
VOICEOVER = 'Have ye not heard? said the queen. And the people cried: he shall perish.'

EX = excerpt(__file__)                      # No. 23 bars 29-38, 44-55, No. 24 bars 1-10 (56-65)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
QUEEN = [n for n in EX['notes'] if n[5] == 'Jezebel']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
T_QUEEN = BAR[30]
T_OATH = EX['segments'][1]['start']         # "The gods do so to me"
T_KISHON = BAR[52]
T_PERISH = BAR[52] + 0.5 * (BAR[53] - BAR[52])
T_WOE = BAR[56]
Q_ON = np.array([n[0] for n in QUEEN])
ANSWERS = [BAR[33], BAR[37]]                # "We heard it with our ears"
QUESTIONS = [T_QUEEN, BAR[35], T_OATH]
CHORUS = np.array(sorted({round(n[0], 3) for n in SUNG}))
WOE = np.array(sorted({round(n[0], 3) for n in SUNG if n[0] >= T_WOE - 0.01 and n[3] >= 100}))

GOLD = hexc('#ffb860')                      # EL15's last frame
SILVER = hexc('#d8ecff')                    # its heaven
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
WINE = hexc('#a01860')                      # Jezebel
ROSE = hexc('#ff4080')
DUST = hexc('#3a2008')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    return dict(queen=l0 + 0.5 * (l1 - l0), home=r0 + 0.35 * (r1 - r0))


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    p = places(G)
    q, e = p['queen'], p['home']
    people = np.isin(seg, ['Porch Left', 'Porch Right'])
    heaven = seg == 'Porch Front'
    l0, l1 = span(G, 'Left')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    r0, r1 = span(G, 'Right')
    # how far Jezebel's colour has to travel to reach each pixel, along the house from her place on Left,
    # stepping over Porch Front (heaven is never stained)
    reach = np.abs(d - q)
    right_side = d > span(G, 'Porch Front')[1]
    reach[right_side] = (pl1 - q) + (d[right_side] - pr0)
    reach[heaven | (seg == 'Side')] = 1e9      # heaven is never stained, and nothing comes to the wilderness
    cand = np.zeros(G.N)
    for s in ('Porch Left', 'Porch Right'):
        a, b = span(G, s)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    cand = np.minimum(cand, 1.0)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    seethe = Flicker(rng, G.N, 4.0, 11.0)
    # the wine's reach (in path units) over time: a step after each question, the porch runs by the oath's end
    far_pr = (pl1 - q) + (pr1 - pr0)
    seep = [(0.0, 0.0), (T_QUEEN, 10.0), (BAR[33], 0.55 * (l1 - q) + 20), (BAR[35], l1 - q + 40),
            (BAR[37], l1 - q + 0.6 * (pl1 - pl0)), (T_OATH, pl1 - q + 20), (BAR[50], far_pr), (D, far_pr)]

    for f in range(F):
        t = f * DT
        # EL15's warmth, draining in the hushed chords before the Queen
        warm = 0.62 * (1 - smoothstep(0.0, BAR[31], t))
        fr = light(GOLD, warm * np.ones(G.N) * (1 - 0.6 * heaven * smoothstep(0.0, BAR[31], t)))
        fr += light(DUST, 0.14 * smoothstep(0.0, BAR[31], t) * np.ones(G.N))
        # heaven as EL15 left it, a little brighter than the house (its silver and the chorus's gold), fading first
        held = 1 - smoothstep(0.0, 3.0, t)
        if held > 0:
            fr += light(SILVER, 0.25 * held * heaven) + light(GOLD, 0.35 * held * heaven)

        # Jezebel's wine: how far it has seeped, and how strongly
        front = keys(t, seep)
        stained = smoothstep(front + 12, front - 12, reach)
        lvl = 0.25 + 0.15 * smoothstep(T_OATH, BAR[51], t) + 0.25 * smoothstep(T_PERISH - 0.3, T_PERISH, t)
        fr += light(WINE, lvl * stained * (0.8 + 0.2 * seethe(t)))

        # the people: candles, tinted wine as she wins them, flickering hard when they answer, blazing at "perish"
        tint = smoothstep(BAR[32], BAR[38], t) * 0.5 + 0.5 * smoothstep(T_OATH, T_KISHON, t)
        flame = 0.45 * (1 - 0.5 * smoothstep(0.0, T_QUEEN, t))
        i = int(np.searchsorted(CHORUS, t, side='right')) - 1
        beat = float(np.exp(-(t - CHORUS[i]) / 0.3)) if i >= 0 else 0.0
        answering = any(ta - 0.3 <= t < ta + 2 * (BAR[34] - BAR[33]) for ta in ANSWERS)
        shout = smoothstep(T_PERISH - 0.2, T_PERISH, t)
        if answering:
            flame += 0.2 + 0.5 * beat
        lit = cand * people * flame * (0.75 + 0.25 * flick(t))
        fr += light(CANDLE, lit * (1 - tint)) + light(ROSE, lit * tint)
        fr += light(WINE, shout * people * (0.45 + 0.5 * beat) * (0.85 + 0.15 * seethe(t)))

        # Jezebel herself: a wine point in the middle of Left, flaring with her words
        if t >= T_QUEEN - 2.0:
            j = int(np.searchsorted(Q_ON, t, side='right')) - 1
            word = float(np.exp(-(t - Q_ON[j]) / 0.45)) if j >= 0 and t < Q_ON[-1] + 3.0 else 0.0
            come = smoothstep(T_QUEEN - 2.0, T_QUEEN, t)
            size = 14 + 10 * smoothstep(T_OATH, T_KISHON, t)
            fr += light(WINE, come * (0.6 + 0.4 * word) * np.exp(-((d - q) / size) ** 2))
            fr += light(ROSE, come * 0.5 * word * np.exp(-((d - q) / 4) ** 2))
            if T_KISHON - 0.6 <= t < T_KISHON + 1.5:     # "the brook of Kishon!"
                fr += light(ROSE, 0.6 * np.exp(-abs(t - T_KISHON) / 0.35) * stained)

        # "Woe to him!": a wall of wine closing on Elijah from both sides along Right
        ring = keys(t, [(T_WOE, 0.0), (BAR[58], 0.35), (BAR[61], 0.65), (BAR[63], 0.82), (BAR[65], 0.92), (D, 0.94)])
        wall_l = (r0 - 30) + (e - 10 - (r0 - 30)) * ring          # from the porch corner toward him
        wall_r = r1 - (r1 - (e + 10)) * ring                      # from the free end toward him
        if t >= T_WOE - 0.5:
            k = int(np.searchsorted(WOE, t, side='right')) - 1
            hit = float(np.exp(-(t - WOE[k]) / 0.25)) if k >= 0 else 0.0
            body = (smoothstep(wall_l + 6, wall_l - 6, d) * (d > pr0)) + smoothstep(wall_r - 6, wall_r + 6, d)
            body = np.minimum(body, 1.0) * (seg == 'Right') + 0.6 * (seg == 'Porch Right') * smoothstep(T_WOE - 0.5, T_WOE, t)
            edge = np.exp(-((d - wall_l) / 5) ** 2) + np.exp(-((d - wall_r) / 5) ** 2)
            fr += light(WINE, (0.4 + 0.3 * hit) * body * (0.85 + 0.15 * seethe(t)))
            fr += light(ROSE, (0.35 + 0.5 * hit) * edge * (seg == 'Right'))

        # Elijah: his amber on Right, shrinking as the woe closes in
        squeeze = 1 - 0.55 * ring
        fr += light(AMBER, (0.65 - 0.2 * ring) * np.exp(-((d - e) / (16 * squeeze)) ** 2)
                    + 0.15 * (1 - ring) * np.exp(-((d - e) / 50) ** 2))
        fr += light(CORE, (0.45 - 0.15 * ring) * np.exp(-((d - e) / 5) ** 2))

        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Jezebel on a low clarinet with a bassoon under her, from her place on Left; the chorus on strings with
    trombones under her crowd and horns on the long notes, from the porch; the orchestra from the reduction."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    p = places(G)
    pq, pe = pan_at(p['queen']), pan_at(p['home'])
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))

    o = Orchestra(M, level=1.0)
    loud = lambda t: 0.35 if t < T_PERISH else (0.75 if t < T_WOE else 1.0)
    o.tutti(ORCH, size=loud, pan=lambda t, m: 0.4 * pe if t >= T_WOE else 0.3 * pq)

    for t, d, m, v, h, who in QUEEN:
        o.play('clarinets', m, t, d, v + 6, pq, 0.7)
        o.play('bassoons', m - 12, t, d, v - 4, pq, 0.35)

    parts = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -10, 0.25)],
             'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -10, 0.25)],
             'T': [('cellos', 0, -2, 0.5), ('trombones', 0, -6, 0.4)],
             'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4), ('trombones', -12, -6, 0.35)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        pan = 0.6 * side[who] if t < T_WOE else 0.5 * (side[who] + pe)
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pan, g)
        if d >= 0.5:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 8, pan, 0.35)

    o.hit('timpani roll', BAR[51], 90, pitch=-1, gain=0.25, pan=pq)
    o.hit('timpani', T_KISHON, 110, pitch=-1, gain=0.4, pan=pq)
    o.hit('cymbal swell', T_PERISH - 1.6, 90, gain=0.2)
    o.hit('timpani', BAR[54], 112, pitch=-3, gain=0.4)
    o.hit('timpani', T_WOE, 108, pitch=-3, gain=0.35, pan=pe)
    o.hit('crash', BAR[58], 100, gain=0.3, pan=pe)
    o.hit('timpani roll', BAR[58], 100, pitch=-3, gain=0.3, pan=pe)
    for b in (59, 60):                         # the sforzando "clos-ed"
        o.hit('timpani', 0.5 * (BAR[b] + BAR[b + 1]), 96, pitch=-3, gain=0.2, pan=pe)
    o.hit('timpani', BAR[65], 110, pitch=-1, gain=0.35, pan=pe)
