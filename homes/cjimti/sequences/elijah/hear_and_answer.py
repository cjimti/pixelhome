"""Hear and Answer: the priests of Baal on Left call on their god louder and wilder, and nothing answers.

Baal's altar is the middle of Left, its priests the whole run in burnished bronze. Every note of the orchestra's
frantic figure is a brass glint flung up Left toward the porch (higher notes nearer heaven) and falling back;
every "Baal!" the chorus holds sends a bronze reach out of Left along Porch Left toward Porch Front, which dies
before it gets there. Each syllable scatters glints over Left, more and wider as the frenzy grows, and each
hammered chord flares the whole run and makes the people's candles on Porch Left and Porch Right flinch. Elijah
waits on Right, steady amber beside his unlit altar. Porch Front, heaven, does nothing at all.

Then Mendelssohn's silences. The orchestra stops under the held "an-swer!", the chorus calls alone, and when
the music stops entirely the house freezes: every pixel holds exactly where it was, bronze, waiting, until the
priests call again. The scene ends in the last of these silences, frozen.

The music is Mendelssohn's own: the chorus of No. 13, all 77 bars, transcribed from the Novello octavo vocal
score (1881) into hear_and_answer.musicxml and timed by scripts/score_excerpt.py at the marked Presto (dotted
crotchet 126), its fermatas held twice as long and its two SILENT bars held longer, as a conductor would. The
chorus is played on the priests' brass (sopranos on trumpets, altos on horns, tenors on trombones, basses on tuba)
with woodwinds doubling, the accompaniment orchestrated from the piano reduction; a production would add the
priests' stamping as they leap on the altar, and timpani with their cries. The silences stay silent.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt

CODE = 'EL09'
TITLE = 'Hear and Answer'
KIND = 'show'
DESCRIPTION = ("The priests of Baal call on their god, louder and wilder, flinging bronze light toward heaven. "
               "Nothing answers. When the music stops, the whole house freezes and waits.")
VOICEOVER = 'They called from morning until noon. And there was no voice, and no one answered.'

EX = excerpt(__file__)                      # No. 13, bars 1-77
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
CALLS = [n for n in SUNG if n[5] == 'S' and n[1] >= 0.9]      # the held cries: "Baal!", "us!", "an-swer!"
SYLL = sorted({round(n[0], 3) for n in SUNG})                  # every sung syllable
HITS = accents(ORCH, vmin=100, n=3, space=0.25)                # the orchestra's hammered chords
FIG = [n for n in ORCH if n[1] < 0.2]                          # the frantic figure, note by note
T_FRENZY = BAR[56]                                              # the frenzy at its height, the orchestra cut off


def silences(notes, least=0.5):
    """Where nothing at all sounds: [(t0, t1)], the end of the piece included."""
    end, out = 0.0, []
    for t, d, *_ in sorted(notes):
        if t - end >= least:
            out.append((end, t))
        end = max(end, t + d)
    if D - end >= least:
        out.append((end, D))
    return out


FROZEN = silences(EX['notes'])

DUST = hexc('#3a2008')                      # the drought
BRONZE = hexc('#b06a10')                    # Baal's priests
GLINT = hexc('#ffcc55')
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
WOOD = hexc('#4a2a10')                      # his altar, unlit
CANDLE = hexc('#ffcf8a')                    # the people


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    l0, l1 = span(G, 'Left')                # from the Side corner to the porch
    p0, p1 = span(G, 'Porch Front')
    r0, r1 = span(G, 'Right')
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    altar = l0 + 0.5 * (l1 - l0)
    elijah = r0 + 0.22 * (r1 - r0)
    wood = r0 + 0.5 * (r1 - r0)
    # the people: small candles along both porch runs
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 18, b - 10, 34):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 1.5, 6.0)
    seethe = Flicker(rng, G.N, 2.5, 9.0)
    fig = np.array([n[0] for n in FIG])
    figpos = np.array([l0 + np.clip((n[2] - 42) / (80 - 42), 0, 1) * (l1 - l0) for n in FIG])
    calls = [(n[0], n[1], n[3]) for n in CALLS]
    syll = np.array(SYLL)
    hits = np.array(HITS)
    lpix = np.flatnonzero(left)
    scatter = [rng.choice(lpix, 6 + int(14 * min(1.0, t / T_FRENZY)), replace=False) for t in syll]

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span_=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return (float(np.exp(-(t - arr[i]) / tau)), i) if i >= 0 and t - arr[i] < span_ else (0.0, -1)

    frozen_at = None
    for f in range(F):
        t = f * DT
        held = next((a for a, b in FROZEN if a <= t < b), None)
        if held is not None:                # the silence: everything holds exactly where it was
            if frozen_at is None:
                frozen_at = out[max(f - 1, 0)].copy()
            out[f] = frozen_at
            continue
        frozen_at = None
        fr = np.zeros((G.N, 3))
        heat = smoothstep(0, T_FRENZY, t)
        hk, _ = last(hits, t, 0.3)

        # the drought over everything; heaven darker still, and empty
        fr += light(DUST, 0.3 * (1 - 0.4 * heaven) * np.ones(G.N))

        # Baal's priests: the whole of Left seething bronze, hotter as they work themselves up; the altar in the middle
        sk, si = last(syll, t, 0.22, 0.6)
        fr += light(BRONZE, left * (0.22 + 0.16 * heat + 0.06 * seethe(t) + (0.25 + 0.2 * heat) * sk + 0.5 * hk))
        fr += light(BRONZE, 0.55 * blob(altar, 40))
        fr += light(GLINT, 0.75 * hk * left)

        # the figure: each note a glint flung up Left toward heaven, falling back
        lo = int(np.searchsorted(fig, t - 0.3))
        hi = int(np.searchsorted(fig, t, side='right'))
        for k in range(lo, hi):
            a = t - fig[k]
            fr += light(GLINT, 0.95 * np.exp(-a / 0.15) * blob(figpos[k] - 150 * a, 14))

        # every syllable: glints scattered over Left, more and wider as the frenzy grows
        if si >= 0:
            sp = np.zeros(G.N)
            sp[scatter[si]] = sk
            fr += light(GLINT, 0.85 * sp)

        # the held cries: a bronze reach out of Left along Porch Left toward heaven, dying before it arrives
        for tc, dc, v in calls:
            if tc <= t < tc + dc + 1.2:
                grow = min(1.0, (t - tc) / max(0.35, 0.7 * dc))
                fade = 1 - smoothstep(tc + dc, tc + dc + 1.2, t)
                head = l1 + (0.5 + 0.4 * heat) * grow * (p0 - l1)
                body = smoothstep(l1 - 60, l1, d) * smoothstep(head + 20, head - 40, d)
                strain = 0.75 + 0.25 * np.sin(2 * np.pi * 7 * t)
                fr += light(BRONZE, fade * (v / 110) * 0.85 * body * strain)
                fr += light(GLINT, fade * (v / 110) * 0.7 * np.exp(-((d - head) / 14) ** 2) * strain)

        # the people of Israel, watching from both porch runs; they flinch at every blow
        fr += light(CANDLE, cand * (0.6 + 0.1 * flick(t)) * (1 - 0.45 * hk) * people)

        # Elijah, steady, beside his unlit altar
        fr += light(WOOD, 0.55 * blob(wood, 60))
        breathe = 0.04 * np.sin(2 * np.pi * t / 5.0)
        fr += light(AMBER, (0.8 + breathe) * blob(elijah, 20) + 0.38 * blob(elijah, 110))
        fr += light(CORE, 0.45 * blob(elijah, 6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Mendelssohn's chorus on the priests' brass with woodwinds doubling, the accompaniment orchestrated from the
    piano reduction, the priests' stamping and timpani on top; the silences left silent."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    l0, l1 = span(G, 'Left')
    baal = pan_at(0.5 * (l0 + l1))
    o = Orchestra(M, level=1.3)
    o.tutti(ORCH, pan=lambda t, m: 0.3 * baal)
    parts = {'S': [('trumpets', 0, 0, 0.5), ('oboes', 0, -12, 0.3)],
             'A': [('horns', 0, 4, 0.55), ('clarinets', 0, -12, 0.3)],
             'T': [('trombones', 0, 4, 0.55)],
             'B': [('tuba', 0, 4, 0.5), ('bassoons', 0, -6, 0.35)]}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, baal * 0.8, g)
    for tc, dc, v in [(n[0], n[1], n[3]) for n in CALLS]:     # their cries: timpani
        o.hit('timpani', tc, min(127, v + 10), pitch=-5, gain=0.45, pan=baal)
    for ta in HITS:
        o.hit('timpani', ta, 118, pitch=-5, gain=0.5, pan=baal * 0.5)
    # the priests stamping as they leap on the altar, a stamp on each beat while the figure drives
    o.effects([(0, -9), (T_FRENZY, -9)])
    beat = BAR[2] - BAR[1]
    for a, b in ((BAR[1], BAR[13]), (BAR[21], BAR[36]), (BAR[61], BAR[66])):
        t = a
        while t < b - 0.05:
            o.hoof(t, pan=baal, v=92)
            o.hoof(t + beat / 2, pan=baal, v=80, gain=0.8)
            t += beat
