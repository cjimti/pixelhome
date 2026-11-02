"""The Fiery Chariot: Elijah breaks forth like a fire on Right; a chariot of fire with horses of fire comes in at the
free end of Right, takes him up, and races the whole roofline right to left into a whirlwind, leaving the house
gold behind it and going out at the free end of Side.

Elijah stands on Right in white-hot amber over a dim night bed. Under "Then did Elijah the prophet break forth like
a fire" his amber kindles: flames lick out of him on the accompaniment's pulse and flare on every sung syllable,
biggest on "fire". Then the orchestra stops and the chorus sings alone, "And when the Lord would take him away to
heaven": the house stills and Porch Front, heaven, begins to glow (God is never a figure, only light).

"There came a fiery chariot": the accompaniment's galloping triplets start, and fire enters at the free end of
Right, the sea end, a white head with gold and red flames streaming behind and a spark struck at its front on
every hoofbeat. It gallops toward Elijah, louder and brighter, and reaches him on the ff "heaven". From there his
amber rides in its head and the chariot races right to left: up Right, along the porch runs and across heaven at the
top of the chorus's "whirl-", down Left, and along Side, the run that leads away from the street. A whirlwind of
white and gold streaks swings through it, wider and faster as the chorus drives. Everything behind it is left
glowing gold. On the last "by a whirlwind went he" it leaves the house at the free end of Side, the farthest pixel
from the street, and on "to heaven" the gold house holds, heaven answering warm on Porch Front.

The music is Mendelssohn's own: the chorus No. 38, transcribed from the Novello octavo vocal score (1881) into
the_fiery_chariot.musicxml and timed by scripts/score_excerpt.py at the marked Moderato maestoso (crotchet 76): bars
1-5 (the opening, to "fire;"), 32-34 ("And when the Lord would take him away to heaven", unaccompanied) and 39-58 (the
second "there came a fiery chariot" to the end). The chorus is played on strings with woodwinds doubling and horns on
the inner voices, the accompaniment orchestrated from the piano reduction (its repeated chords as string tremolo);
a production adds the horses' hoofbeats under the gallop, the fire's roar around the chariot and the whirlwind's
wind as it races, timpani on the ff arrivals.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL22'
TITLE = 'The Fiery Chariot'
KIND = 'show'
DESCRIPTION = ("Elijah breaks forth like a fire. A chariot of fire gallops in, takes him up, and races the whole "
               "house into a whirlwind, leaving it glowing gold.")
VOICEOVER = 'And he went up by a whirlwind into heaven.'

EX = excerpt(__file__)                      # No. 38, bars 1-5.5, 32-35, 39.75-59
D = EX['seconds']
SEG = {tuple(s['measures']): s['start'] for s in EX['segments']}
BAR = {}
for m, t in EX['bars']:
    BAR.setdefault(int(m), t)               # a spliced bar keeps its first time
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
SYLL = sorted({round(n[0], 3) for n in SUNG})                  # every sung syllable
T_ALONE = SEG[(32.0, 35.0)]                                     # "And when the Lord...", unaccompanied
T_CHARIOT = SEG[(39.75, 59.0)]                                  # "there came a fiery chariot"
T_TAKE = BAR[43]                                                # ff "heaven": the chariot reaches him
T_CLIMAX = BAR[48] + 0.5 * (BAR[49] - BAR[48])                  # the ff "whirl-" held high
T_OUT = BAR[57]                                                 # "by a whirlwind went he": gone at the free end
T_LAST = BAR[58]                                                # "to heaven"
HOOVES = sorted({round(n[0], 3) for n in ORCH if n[1] < 0.12 and n[0] >= T_CHARIOT - 0.1})[::3]
HITS = [BAR[43], T_CLIMAX, BAR[52], BAR[55]]                    # the ff arrivals

NIGHT = hexc('#0c1430')                     # the bed: a clear night
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
WHITE = hexc('#ffffff')                     # fire from heaven: white to gold to red
GOLD = hexc('#ffc040')
RED = hexc('#ff3000')
HEAVEN = hexc('#fff0c8')                    # heaven's warm light


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def head_path(G):
    """The chariot's head along the path by time: in at the free end of Right, to Elijah, then right to left round
    the whole house and out past the free end of Side."""
    r0, r1 = span(G, 'Right')
    pr0, _ = span(G, 'Porch Right')
    p0, _ = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    pl0, _ = span(G, 'Porch Left')
    elijah = r0 + 0.45 * (r1 - r0)
    return elijah, [(0.0, r1 + 60), (T_CHARIOT, r1 + 60), (T_TAKE, elijah),
                    (BAR[45], r0 + 0.05 * (r1 - r0)), (BAR[47], pr0 + 10),
                    (T_CLIMAX, 0.5 * (p0 + pr0)), (BAR[50] + 0.4, p0), (BAR[52], pl0 - 5),
                    (BAR[53] + 1.0, 0.45 * (l0 + l1) + 40), (BAR[55], l0 - 10), (T_OUT + 0.6, -80), (D + 1, -400)]


def chariot_at(t, path):
    """The head's place at t: eased as it gallops in and slows to take him up, then a steady race."""
    if t < T_TAKE:
        return float(keys(t, path[:3]))
    ts, ps = zip(*path[2:])
    return float(np.interp(t, ts, ps))


def render(G, seed=38):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    heaven = (G.seg_of == 'Porch Front').astype(float)
    elijah, path = head_path(G)
    flick = Flicker(rng, G.N, 3.0, 11.0)
    shimmer = Flicker(rng, G.N, 1.0, 4.0)
    syll = np.array(SYLL)
    hooves = np.array(HOOVES)
    hits = np.array(HITS)
    pulse = np.array(sorted({round(n[0], 3) for n in ORCH if n[0] < T_ALONE}))     # the opening's chords
    streaks = [(rng.uniform(0, 2 * np.pi), rng.uniform(1.4, 2.4), rng.choice([-1, 1]), rng.uniform(0.6, 1.0))
               for _ in range(7)]
    passed = np.full(G.N, -1.0)                 # when the chariot passed each pixel

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span_=1.5):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        h = chariot_at(t, path)
        racing = t >= T_TAKE
        gone = smoothstep(T_OUT - 0.4, T_OUT + 0.8, t)
        sk = last(syll, t, 0.25, 0.8)

        # the night bed, never dark
        fr += light(NIGHT, 0.32 * np.ones(G.N))

        # heaven: kept dim, then glowing from "would take him away to heaven", warm at the end
        hv = (0.12 + 0.16 * smoothstep(T_ALONE + 3, BAR[34] + 1.0, t) + 0.12 * smoothstep(T_TAKE, T_CLIMAX, t)
              + 0.28 * smoothstep(T_OUT, T_LAST + 2.0, t))
        fr += light(HEAVEN, heaven * hv * (0.9 + 0.1 * shimmer(t)))

        # Elijah on Right until the chariot takes him; he breaks forth like a fire in the opening
        if not racing:
            kindle = smoothstep(1.0, 6.3, t) * (1 - smoothstep(T_ALONE, T_ALONE + 2.0, t))
            pk = last(pulse, t, 0.12, 0.4) if t < T_ALONE else 0.0
            w = 40 + 150 * kindle * (0.6 + 0.4 * pk) + 80 * sk * (t < T_ALONE)
            flame = blob(elijah, w) * kindle * (0.6 + 0.3 * flick(t) + 0.4 * sk)
            fr += light(RED, 0.85 * flame)
            fr += light(GOLD, 0.9 * flame * blob(elijah, 0.55 * w))
            fr += light(AMBER, 0.85 * blob(elijah, 18) + 0.3 * blob(elijah, 90))
            fr += light(CORE, (0.45 + 0.3 * sk * (t < T_ALONE)) * blob(elijah, 6))

        # the chariot: a white head, gold then red flames streaming behind it (toward where it came from)
        if T_CHARIOT <= t and gone < 1:
            arrive = smoothstep(T_CHARIOT, T_TAKE, t)
            power = (0.45 + 0.55 * arrive) * (1 - gone)
            behind = np.clip(d - h, 0, None)
            ahead = np.clip(h - d, 0, None)
            tail = np.exp(-behind / (90 + 160 * racing)) * np.exp(-(ahead / 12) ** 2)
            fl = 0.7 + 0.3 * flick(t)
            fr += light(RED, power * 0.9 * tail * fl)
            fr += light(GOLD, power * 0.95 * np.exp(-behind / (55 + 35 * racing)) * np.exp(-(ahead / 10) ** 2) * fl)
            fr += light(WHITE, power * (0.75 + 0.25 * sk) * blob(h, 14))
            hk = last(hooves, t, 0.1, 0.3)
            fr += light(WHITE, power * 0.8 * hk * blob(h - 22, 10))           # a spark struck at every hoofbeat
            if racing:                                                          # Elijah rides in its head
                fr += light(CORE, power * 0.5 * blob(h + 14, 7))
                fr += light(AMBER, power * 0.6 * blob(h + 14, 20))

            # the whirlwind: streaks swinging through the chariot, wider and faster as the chorus drives
            if racing:
                drive = 0.5 + 0.5 * smoothstep(T_TAKE, T_CLIMAX, t)
                for ph, rate, sgn, g in streaks:
                    p = h + 40 + (90 + 110 * drive) * np.sin(sgn * 2 * np.pi * rate * drive * t + ph)
                    fr += light(GOLD if g < 0.8 else WHITE, power * 0.75 * g * blob(p, 22))

            # it leaves the house gold behind it
            newly = (passed < 0) & (d > h)
            passed[newly] = t
        if t >= T_CHARIOT:
            age = np.where(passed >= 0, t - passed, -1.0)
            glow = np.where(age >= 0, (0.3 + 0.4 * np.exp(-np.clip(age, 0, None) / 2.5)) * smoothstep(0, 1.0, age), 0)
            glow = glow * (0.55 + 0.45 * smoothstep(T_CHARIOT, T_TAKE, t)) + 0.06 * smoothstep(T_OUT, T_LAST + 2, t) * (age >= 0)
            fr += light(GOLD, glow * (0.9 + 0.1 * shimmer(t)))

        # timpani on the ff arrivals: the gold flares a moment
        hk = last(hits, t, 0.25, 0.8) if t < T_OUT else 0.0
        fr += light(GOLD, 0.25 * hk * (passed >= 0))

        # the end: Side's far end, where he went, glows a last ember
        if gone > 0:
            fade = 1 - smoothstep(T_LAST, D, t)
            fr += light(AMBER, 0.6 * gone * (0.4 + 0.6 * fade) * blob(0, 40))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Mendelssohn's chorus on strings with woodwinds doubling and horns inside, the accompaniment orchestrated from the
    piano reduction; hoofbeats under the gallop, the chariot's fire and the whirlwind's wind as it races, timpani on
    the ff arrivals."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    elijah, path = head_path(G)
    chariot = lambda t: pan_at(max(0.0, chariot_at(t, path)))
    o = Orchestra(M, level=1.45)
    size = lambda t: 0.6 if t < T_ALONE else 0.5 + 0.5 * smoothstep(T_CHARIOT, T_CLIMAX, t)
    o.tutti(tidy(ORCH), size=size, pan=lambda t, m: 0.6 * chariot(t) if t >= T_CHARIOT else 0.0)
    parts = {'S': [('violins', 0, -2, 0.5), ('flutes', 0, -10, 0.3), ('oboes', 0, -12, 0.25)],
             'A': [('violins', 0, -6, 0.4), ('horns', 0, -4, 0.4)],
             'T': [('violas', 0, -2, 0.5), ('horns', 0, -6, 0.35)],
             'B': [('cellos', 0, 0, 0.55), ('basses', -12, -6, 0.4), ('bassoons', 0, -10, 0.3)]}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, None, g)
    # Elijah breaking forth like a fire
    o.fire(BAR[3], T_ALONE - 0.3, level=lambda tt: 0.35 + 0.35 * smoothstep(BAR[3], BAR[5], tt), pan=pan_at(elijah),
           seed=3)
    o.hit('timpani', BAR[5], 112, pitch=-5, gain=0.45, pan=pan_at(elijah))
    # the chariot: horses galloping in, fire round it, and the whirlwind as it races
    o.gallop(T_CHARIOT + 0.4, T_OUT, beat=2 * (BAR[41] - BAR[40]) / 4, pan=chariot, v=96, gain=0.9)
    o.fire(T_CHARIOT, T_OUT + 0.8, level=lambda tt: 0.3 + 0.5 * smoothstep(T_CHARIOT, T_TAKE, tt), pan=chariot,
           seed=11)
    o.wind(T_TAKE - 1.0, T_OUT + 1.5, level=lambda tt: 0.4 + 0.6 * smoothstep(T_TAKE, T_CLIMAX, tt), pan=chariot)
    for ta in HITS:
        o.hit('timpani', ta, 118, pitch=-5, gain=0.5, pan=chariot(ta))
    o.hit('timpani roll', T_OUT, 110, gain=0.4, pan=pan_at(0))
    o.hit('crash', T_TAKE, 105, gain=0.3, pan=chariot(T_TAKE))
    # back the effects off where the chorus sings alone, let them lead in the race
    o.effects([(0, -10), (T_ALONE - 0.5, -12), (T_ALONE + 0.5, -40), (T_CHARIOT, -14), (T_TAKE, -9),
               (T_OUT + 1.0, -9), (T_LAST, -16)])
