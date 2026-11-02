"""Call Him Louder: the priests' cries die away, Elijah mocks them, and they cry out to Baal louder than before.

The scene opens where the last one ended, the priests of Baal on Left around their bronze altar, Elijah's amber
on Right beside his unlit wood, the people's candles on the porch runs. The priests are tiring. The trebles hold
one long "Baal, . . . hear . . . us!" and it pushes a bronze reach out of Left toward heaven again and again, each
time shorter, while the other voices' "Hear us!" flare the run more weakly, until everything sinks to the quiet
fermata. Porch Front, heaven, stays dark.

Then Elijah. "Call him louder! for he is a god": every word he says is a quick amber flick from him toward Left,
reaching across Porch Right, and where the priests stand the bronze shrinks back at each one. "He talketh; or, he is
pursuing; or, he is in a journey": the flicks reach a little farther each time, and he steps closer to the porch.
"Or, peradventure, he sleepeth": the bronze droops, almost out. "So awaken him. Call him louder, call him louder!":
two hard flicks that cross to the corner of Left.

The priests answer, louder and brighter and more scattered than ever: "Hear our cry, O Baal! now arise!" comes in
voice after voice, each one entering higher (basses near the Side corner of Left, then tenors, altos, trebles
toward the porch), every syllable a surge of bronze where its voice stands, the orchestra's tremolo glinting all
over the run. "Wherefore slumber?": all four together, the whole run blazing, and the reach toward heaven, which
again dies before it gets there. It ends on their unanswered question, held, and the priests waiting.

The music is Mendelssohn's own: the close of No. 11 and all of No. 12, transcribed from the Novello octavo vocal
score into call_him_louder.musicxml and timed by scripts/score_excerpt.py at the marked tempos. The priests are on
brass with woodwinds doubling, as in Baal, We Cry to Thee; Elijah on cellos and horns. Added: timpani with the
priests' accented calls, a dry stamp under Elijah's "Call him louder!", a snare-like brake drum rattle and cymbal
swell into the chorus, and the priests stamping through it.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL08'
TITLE = 'Call Him Louder'
KIND = 'show'
DESCRIPTION = ("Elijah mocks the priests of Baal: call him louder, perhaps he is asleep. Each taunt is a flick of "
               "amber from Right; the priests cry out again, louder and wilder, and nothing answers.")
VOICEOVER = 'Cry aloud, for he is a god. Perhaps he is asleep, and must be woken.'

EX = excerpt(__file__)                      # No. 11 bars 117-141, No. 12 bars 142-174
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_RECIT = min(n[0] for n in ELIJAH)
T_CHORUS = BAR[155]                        # the basses' first "Hear our cry"
T_ORCH = BAR[153]                          # the chorus's ff octaves
T_WHEREFORE = BAR[165]
T_LAST = BAR[174]                          # the held "-ber?"
EL_ON = np.array([n[0] for n in ELIJAH])
TAUNT = [n[0] for n in ELIJAH if n[3] >= 90 and n[0] >= BAR[150]]    # the forte "Call him louder"s
PLACE = {'B': 0.15, 'T': 0.38, 'A': 0.62, 'S': 0.85}                # where each voice stands along Left


def onsets(parts, t0=0.0, t1=1e9):
    return np.array(sorted({round(n[0], 3) for n in SUNG if n[5] in parts and t0 <= n[0] < t1}))


CLOSE = {v: onsets(v, 0, T_RECIT) for v in VOICES}
CHOR = {v: onsets(v, T_ORCH) for v in VOICES}
HELD = [n for n in SUNG if n[5] == 'S' and n[0] < T_RECIT and n[1] >= 1.0]    # the trebles' long "Baal . . ."
TOGETHER = onsets(VOICES, T_WHEREFORE)
TREM = np.array(sorted({round(n[0], 3) for n in ORCH if n[0] >= T_ORCH}))
FIG = [n for n in ORCH if n[0] < T_RECIT and n[1] < 0.3 and n[4] == 0]

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
BRONZE = hexc('#b06a10')                    # Baal's altar and priests
GLINT = hexc('#ffcc55')
WOOD = hexc('#5a3a1e')                      # Elijah's altar, unlit (EL07's)
WOOD9 = hexc('#4a2a10')                     # as Hear and Answer has it


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def last(arr, t, tau, span_=2.0):
    i = int(np.searchsorted(arr, t, side='right')) - 1
    return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0


def elijah_at(G, t):
    """From his place on Right (EL07) to the place Hear and Answer has him, a step toward the porch as he taunts."""
    r0, r1 = span(G, 'Right')
    return r0 + (0.35 - 0.13 * smoothstep(T_RECIT, BAR[150], t)) * (r1 - r0)


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    mid = l0 + 0.5 * (l1 - l0)
    lower_half = left * (1 - smoothstep(mid - 25, mid + 25, d))
    upper_half = left * smoothstep(mid - 25, mid + 25, d)
    cand7, cand9 = np.zeros(G.N), np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand7 += np.exp(-((d - c) / 5.0) ** 2)
        for c in np.arange(a + 18, b - 10, 34):
            cand9 += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 1.5, 6.0)
    seethe = Flicker(rng, G.N, 2.5, 9.0)
    glint = Flicker(rng, G.N, 3.0, 9.0)
    b0, b1 = l0 + 0.15 * (l1 - l0), l0 + 0.55 * (l1 - l0)
    w0, w1 = r0 + 0.6 * (r1 - r0), r0 + 0.85 * (r1 - r0)
    band = smoothstep(b0, b0 + 12, d) * (1 - smoothstep(b1 - 12, b1, d))
    wood7 = smoothstep(w0, w0 + 10, d) * (1 - smoothstep(w1 - 10, w1, d))
    altar9 = mid
    lpix = np.flatnonzero(left)
    fig = np.array([n[0] for n in FIG])
    figpos = np.array([mid + np.clip((n[2] - 53) / (77 - 53), 0, 1) * (l1 - mid) for n in FIG])
    ell = [(n[0], n[1], n[3]) for n in ELIJAH]

    def blob(c, w):
        return np.exp(-((d - c) / w) ** 2)

    for f in range(F):
        t = f * DT
        # EL07's look gives way to Hear and Answer's through Elijah's recitative
        mix = smoothstep(T_RECIT, BAR[150], t)
        end = smoothstep(T_LAST + 1.2, D - 0.1, t)                 # the last moment settles to EL09's first frame
        fr = light(DUST, (0.28 + 0.02 * mix) * (1 - 0.4 * heaven) * np.ones(G.N))
        e = elijah_at(G, t)

        # the people, watching; they flinch at the priests' loudest cries
        cand = (1 - mix) * cand7 * 0.7 + mix * cand9 * 0.6
        loud = last(TOGETHER, t, 0.35) if t >= T_WHEREFORE else 0.0
        fr += light(CANDLE, cand * people * (0.75 + 0.25 * flick(t)) * (1 - 0.45 * loud * (1 - end)))

        # Elijah's wood: EL07's band becoming EL09's
        fr += light(WOOD, 0.75 * (1 - mix) * wood7)
        fr += light(WOOD9, 0.55 * mix * blob(r0 + 0.5 * (r1 - r0), 60))

        # the altar: EL07's settled band becoming EL09's blob at the middle of Left
        fr += light(BRONZE, 0.4 * (1 - mix) * band + 0.55 * mix * blob(altar9, 40))
        fr += light(GLINT, 0.45 * (1 - mix) * band * np.maximum(glint(t) - 0.6, 0) * 2.5)

        # the priests
        if t < T_RECIT:                     # dying away
            tire = (1 - 0.6 * smoothstep(0, T_RECIT - 3, t)) * smoothstep(0, 0.5, t)
            base = 0.12 + 0.06 * seethe(t)
            hits = sum(last(CLOSE[v], t, 0.5) for v in ('A', 'T', 'B'))
            fr += light(BRONZE, left * (base + 0.55 * tire * min(hits, 1.0)))
            for tc, dc, m, v, h, who in [n for n in HELD if n[0] <= t < n[0] + n[1] + 1.0]:
                grow = min(1.0, (t - tc) / max(0.6, 0.6 * dc))
                fade = 1 - smoothstep(tc + dc, tc + dc + 1.0, t)
                reach = (0.15 + 0.5 * tire) * grow
                head = l1 + reach * (pf0 - l1)
                body = smoothstep(l1 - 70, l1, d) * smoothstep(head + 20, head - 40, d)
                fr += light(BRONZE, fade * tire * (0.9 * body + 0.35 * upper_half))
                fr += light(GLINT, fade * tire * 0.7 * np.exp(-((d - head) / 14) ** 2))
            lo = int(np.searchsorted(fig, t - 0.3))
            hi = int(np.searchsorted(fig, t, side='right'))
            for k in range(lo, hi):         # the orchestra's running figure, fainter as they tire
                a = t - fig[k]
                fr += light(GLINT, 0.75 * tire * np.exp(-a / 0.15) * blob(figpos[k] + 100 * a, 12))
        elif t < T_ORCH:                    # Elijah mocks them: the bronze shrinks back from every word
            quiet = 0.12 + 0.05 * seethe(t)
            sleep = smoothstep(BAR[148], BAR[149] + 1.0, t) * (1 - smoothstep(BAR[150], BAR[150] + 0.6, t))
            shrink = last(EL_ON, t - 0.25, 0.4)
            fr += light(BRONZE, left * np.maximum(quiet * (1 - 0.6 * sleep) - 0.08 * shrink, 0.03))
        else:                               # louder: the chorus
            heat = smoothstep(T_ORCH, T_LAST, t) * (1 - end)
            tk = last(TREM, t, 0.12) * (1 - end)
            fr += light(BRONZE, left * (0.22 + 0.15 * heat + 0.06 * seethe(t)) * (1 - 0.0 * end))
            fr += light(GLINT, left * (0.35 + 0.3 * heat) * tk * np.maximum(glint(t) - 0.45, 0) * 1.8)
            for v in VOICES:
                k = last(CHOR[v], t, 0.45) * (1 - end)
                if k > 0:
                    c = l0 + PLACE[v] * (l1 - l0)
                    fr += light(BRONZE, 1.0 * k * blob(c, 34))
                    fr += light(GLINT, 0.8 * k * blob(c, 10))
            if t >= T_WHEREFORE:            # all four together: the whole run blazes and reaches for heaven
                k = last(TOGETHER, t, 0.6) * (1 - end)
                fr += light(BRONZE, 0.75 * k * left)
                fr += light(GLINT, 0.55 * k * left * (0.5 + 0.5 * glint(t)))
                sp = np.zeros(G.N)
                sp[rng.choice(lpix, 18, replace=False)] = k
                fr += light(GLINT, 0.8 * sp)
                for tc in (BAR[165] + 0.75 * 2, BAR[169] + 0.75 * 2, BAR[172]):
                    if tc <= t < tc + 2.6:
                        grow = min(1.0, (t - tc) / 1.2)
                        fade = 1 - smoothstep(tc + 1.2, tc + 2.6, t)
                        head = l1 + 0.6 * grow * (pf0 - l1)
                        body = smoothstep(l1 - 60, l1, d) * smoothstep(head + 20, head - 40, d)
                        fr += light(BRONZE, fade * (1 - end) * 0.9 * body)
                        fr += light(GLINT, fade * (1 - end) * 0.8 * np.exp(-((d - head) / 14) ** 2))
            # the last frame: Hear and Answer's priests, seething low
            fr += light(BRONZE, end * left * (0.22 + 0.06 * seethe(t)))

        # Elijah: steady amber; in the recitative every word a flick toward Left across Porch Right
        j = int(np.searchsorted(EL_ON, t, side='right')) - 1
        voice = float(np.exp(-(t - EL_ON[j]) / 0.4)) if j >= 0 and T_RECIT <= t < T_ORCH + 1 else 0.0
        size = (1 - mix) * 16 + mix * 20
        wide = (1 - mix) * (0.15 * blob(e, 60)) + mix * (0.38 * blob(e, 110))
        fr += light(AMBER, ((1 - mix) * 0.7 + mix * 0.8 + 0.5 * voice) * blob(e, size * (1 + 0.4 * voice)) + wide)
        fr += light(CORE, (0.45 + 0.35 * voice) * blob(e, (1 - mix) * 5 + mix * 6))
        for tc, dc, v in ell:
            a = t - tc
            if 0 <= a < 0.9:
                k = np.searchsorted(EL_ON, tc)
                hard = tc in TAUNT
                reach = 0.4 + 0.6 * min(k / len(EL_ON), 1.0)        # farther each time
                far = l1 if hard else e - reach * (e - pr0)          # the last taunts cross to the corner of Left
                pos = e + (far - e) * min(a / (0.55 if hard else 0.4), 1.0)
                fr += light(AMBER, (1.0 if hard else 0.85) * np.exp(-a / 0.35) * blob(pos, 14))
                fr += light(CORE, 0.6 * np.exp(-a / 0.25) * blob(pos, 5))
                trail = smoothstep(pos - 6, pos + 6, d) * (1 - smoothstep(e - 10, e, d))     # the streak behind it
                fr += light(AMBER, 0.45 * np.exp(-a / 0.3) * trail)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The priests on brass with woodwinds doubling, panned where they stand on Left; Elijah on cellos and horns; the
    accompaniment on the orchestra; timpani, stamps and the rest of the production on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    l0, l1 = span(G, 'Left')

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    baal = pan_at(l0 + 0.5 * (l1 - l0))
    where = {v: pan_at(l0 + PLACE[v] * (l1 - l0)) for v in VOICES}
    o = Orchestra(M, level=1.25)
    size = lambda t: 0.55 if t < T_RECIT else (0.6 if t < T_ORCH else 1.0)
    o.tutti(ORCH, size=size, pan=lambda t, m: 0.4 * baal if t < T_RECIT or t >= T_ORCH else 0.0)
    parts = {'S': [('trumpets', 0, -2, 0.45), ('oboes', 0, -12, 0.3)],
             'A': [('horns', 0, 2, 0.5), ('clarinets', 0, -12, 0.3)],
             'T': [('trombones', 0, 2, 0.5), ('bassoons', 0, -10, 0.3)],
             'B': [('tuba', 0, 2, 0.45), ('cellos', 0, -8, 0.35), ('basses', -12, -8, 0.3)]}
    for t, d, m, v, h, who in SUNG:
        pan = where[who] if t >= T_ORCH else baal
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pan, g)
    for t, d, m, v, h, who in ELIJAH:
        e = pan_at(elijah_at(G, t))
        o.play('cellos', m, t, d, v + 2, e, 0.6)
        o.play('horns', m, t, d, v - 6, e, 0.4)
    for v in VOICES:                        # each voice's entry in the chorus: timpani
        o.hit('timpani', CHOR[v][0], 112, pitch=-5, gain=0.4, pan=where[v])
    for t in onsets(VOICES, T_WHEREFORE):
        o.hit('timpani', t, 104, pitch=-5, gain=0.25, pan=baal)
    o.effects([(0, -10), (T_RECIT, -8), (T_ORCH, -6)])
    for t in TAUNT:
        o.hoof(t, pan=pan_at(elijah_at(G, t)), v=100)
    o.hit('cymbal swell', T_ORCH - 1.4, 96, gain=0.25, pan=baal)
    o.hit('crash', T_ORCH, 104, gain=0.2, pan=baal)
    beat = 60 / 160
    t = T_CHORUS
    while t < T_LAST - 0.05:                # the priests stamping on the beat, as at the altar in Hear and Answer
        o.hoof(t, pan=baal, v=90, gain=0.8)
        t += 2 * beat
    o.hit('timpani roll', T_LAST, 96, pitch=-5, gain=0.3, pan=baal)
