"""The Curse: Elijah swears there will be no dew nor rain, and the drought spreads over the house with the overture.

The house begins alive: soft green with blue dew glinting along every run, the people's candles on Porch Left and
Porch Right. Elijah stands on Right in amber. Before any overture, the brass chords sound and he swears: "As God the
Lord of Israel liveth, before whom I stand, there shall not be dew nor rain these years, but according to my word."
Every chord under him burns his amber one notch further outward along the roofline, scorching the green; on the
fortissimo before "but according to my word" it flares across the whole of Right and into the porch, and on the
held last chord it stays.

Then the overture's fugue, the drought itself: the subject creeps up from the bass, and with every note of it the
dust front moves one step from Right toward the far end of Side, the colour draining out behind it to dry ochre.
When the answer comes in a fifth higher the front speeds up, faster as the music tightens, until the whole house is
dust and only the people's candles are left, guttering low, where Help, Lord! begins.

The music is Mendelssohn's own: the Introduction and the overture's first nine bars, transcribed from the Novello
octavo vocal score into the_curse.musicxml and timed by scripts/score_excerpt.py at the marked tempos (Grave at
crotchet 60, the overture at crotchet 92), the fermatas held twice as long. The chords are on trombones and tuba,
Elijah on cellos and horns, the fugue subject on cellos and basses and the answer on violas. A production adds a
dry wind that rises as the drought spreads.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL01'
TITLE = 'The Curse'
KIND = 'show'
DESCRIPTION = ("Elijah swears there will be no dew nor rain, and every chord burns his amber further along the roof. "
               "Then the overture's fugue drains the colour out of the house, run by run, into dust.")
VOICEOVER = 'A king and queen who worshipped an idol, and a prophet who said: there will be no rain, until I say so.'

EX = excerpt(__file__)                      # Introduction (bars 1-12) and the overture's bars 1-9 (13-22)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_OVER = BAR[13]                            # the overture's upbeat
T_ANSWER = BAR[19]                          # the answer, a fifth higher
T_FF = BAR[9]                               # the fortissimo before "but according to my word"
# the chords under the curse: every distinct onset in the accompaniment before the overture
CHORDS = sorted({round(n[0], 3) for n in ORCH if n[0] < T_OVER - 0.01})
# the fugue: every note onset in the overture, bass and answer together
FUGUE = np.array(sorted({round(n[0], 3) for n in ORCH if n[0] >= T_OVER - 0.01}))

GREEN = hexc('#3c9a48')                     # the living land
DEW = hexc('#58b8ff')                       # dew glinting
DUST = hexc('#3a2008')                      # the drought
OCHRE = hexc('#8a5418')                     # the dust front, still hot
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
CANDLE = hexc('#ffcf8a')                    # the people


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    r0, r1 = span(G, 'Right')
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    elijah = r0 + 0.3 * (r1 - r0)
    far = 0.0                                                  # the free end of Side, where the drought ends

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 18, b - 10, 34):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 1.5, 6.0)
    dew_phase = rng.uniform(0, 2 * np.pi, G.N)
    dew_rate = rng.uniform(0.25, 0.7, G.N)
    el_on = np.array([n[0] for n in ELIJAH])

    # the scorch: Elijah's amber reaches one notch further on every chord (both ways from him, more toward the house)
    notch = 23.0
    reach_at = np.array([notch * (k + 1) for k in range(len(CHORDS))])
    chords = np.array(CHORDS)
    # the dust front: from the far end of Right to the far end of Side, one step on every note of the fugue,
    # the steps longer once the answer comes in, so it speeds up as the music tightens
    steps = np.where(FUGUE < T_ANSWER, 1.0, 2.2)
    front_at = d.max() - (d.max() - far) * np.cumsum(steps) / steps.sum()

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))

        # how far the curse has burned, and the ff flare
        k = int(np.searchsorted(chords, t, side='right')) - 1
        reach = reach_at[k] if k >= 0 else 0.0
        hit = float(np.exp(-(t - chords[k]) / 0.35)) if k >= 0 else 0.0
        flare = float(np.exp(-max(t - T_FF, 0) / 1.6)) * (t >= T_FF) if t < T_OVER else 0.0
        reach += 260 * flare
        dist = np.abs(d - elijah) * np.where(d > elijah, 1.6, 1.0)     # toward the free end it burns slower
        scorch = smoothstep(reach + 20, reach - 10, dist)

        # the dust front in the overture
        if t >= T_OVER:
            j = int(np.searchsorted(FUGUE, t, side='right')) - 1
            front = front_at[j] if j >= 0 else d.max()
            step = float(np.exp(-(t - FUGUE[j]) / 0.18)) if j >= 0 else 0.0
            dry = smoothstep(front - 12, front + 12, d)
        else:
            front, step, dry = d.max() + 50, 0.0, np.zeros(G.N)
        drought = np.maximum(scorch * smoothstep(T_OVER - 2, T_OVER + 3, t), dry)

        # the living house: green with dew glinting, where the curse has not reached
        alive = 1 - np.maximum(scorch, dry)
        glint = np.clip(np.sin(2 * np.pi * dew_rate * t + dew_phase), 0, 1) ** 6
        fr += light(GREEN, 0.42 * alive)
        fr += light(DEW, 0.55 * glint * alive)

        # the drought: dust ochre, the front itself still hot as it moves
        fr += light(DUST, 0.3 * drought)
        if t >= T_OVER:
            fr += light(OCHRE, (0.35 + 0.35 * step) * blob(front, 18) * (front > far + 5))

        # the scorch before the overture: amber burned into the roofline, flaring on each chord
        if t < T_OVER + 3:
            fade = 1 - smoothstep(T_OVER, T_OVER + 3, t)
            edge = smoothstep(reach + 20, reach - 10, dist) - smoothstep(reach - 10, reach - 40, dist)
            fr += light(AMBER, fade * (0.38 * scorch + (0.45 + 0.4 * hit) * np.clip(edge, 0, 1)))
            fr += light(AMBER, fade * 0.6 * flare * scorch)

        # the people: candles on both porch runs, guttering lower as the drought takes the house
        low = 1 - 0.6 * smoothstep(T_OVER, D, t)
        fr += light(CANDLE, cand * people * (0.75 + 0.2 * flick(t)) * low * (0.7 + 0.3 * alive))

        # Elijah on Right, his amber pulsing with his own voice; he withdraws into an ember as the overture runs
        i = int(np.searchsorted(el_on, t, side='right')) - 1
        voice = float(np.exp(-(t - el_on[i]) / 0.4)) if i >= 0 and t < T_OVER else 0.0
        stay = 1 - 0.75 * smoothstep(T_OVER, T_OVER + 10, t)
        fr += light(AMBER, stay * ((0.8 + 0.15 * voice + 0.1 * hit) * blob(elijah, 20) + 0.3 * blob(elijah, 90)))
        fr += light(CORE, stay * (0.45 + 0.35 * voice) * blob(elijah, 6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The curse's chords on trombones and tuba, Elijah on cellos and horns; the fugue on cellos and basses with the
    answer on violas; a dry wind rising as the drought spreads."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    r0, r1 = span(G, 'Right')
    elijah = pan_at(r0 + 0.3 * (r1 - r0))
    o = Orchestra(M, level=2.0)

    # the Introduction: the chords on the brass, as Mendelssohn scores them
    for t, d, m, v, h, who in ORCH:
        if t < T_OVER - 0.01:
            if m < 45:
                o.play('tuba', m, t, d, v, 0.3 * elijah, 0.6)
                o.play('basses', m, t, d, v - 10, 0.3 * elijah, 0.4)
            elif m < 62:
                o.play('trombones', m, t, d, v, 0.4 * elijah, 0.6)
                o.play('bassoons', m, t, d, v - 12, 0.4 * elijah, 0.3)
            else:
                o.play('horns', m, t, d, v - 4, 0.4 * elijah, 0.5)
                o.play('clarinets', m, t, d, v - 14, 0.4 * elijah, 0.3)
    # Elijah: cellos and horns, the held last word on low brass too
    for t, d, m, v, h, who in ELIJAH:
        o.play('cellos', m, t, d, v - 2, elijah, 0.7)
        o.play('horns', m, t, d, v - 10, elijah, 0.5)
        if d > 3:
            o.play('trombones', m, t, d, v - 14, elijah, 0.35)
    o.hit('timpani roll', BAR[9], 110, pitch=-2, gain=0.4, pan=0.3 * elijah)
    o.hit('timpani roll', BAR[12], 80, pitch=-5, gain=0.3, pan=0.3 * elijah)

    # the overture: the subject on cellos and basses, the answer on violas, growing as it goes
    for t, d, m, v, h, who in ORCH:
        if t >= T_OVER - 0.01:
            grow = 8 * smoothstep(T_OVER, D, t)
            if h == 1 or t < T_ANSWER:
                o.play('cellos', m + (12 if m < 40 else 0), t, d, v + grow, -0.1, 0.6)
                if m < 52:
                    o.play('basses', m, t, d, v + grow - 6, -0.1, 0.45)
            else:
                o.play('violas', m, t, d, v + grow, 0.15, 0.6)

    # the drought: a dry wind that rises as the dust spreads, from Right toward Side
    o.effects([(0, -14), (T_OVER, -10), (D - 4, -6)])
    o.wind(T_OVER - 1, D + 1.5, level=lambda tt: 0.15 + 0.5 * smoothstep(T_OVER, D, tt),
           pan=lambda tt: 0.7 - 1.5 * smoothstep(T_OVER, D, tt), seed=21)
