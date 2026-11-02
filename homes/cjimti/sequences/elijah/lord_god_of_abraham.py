"""Lord God of Abraham: Elijah calls the people near and prays, calm and steady, and the house fills with warmth.

The scene opens where Hear and Answer ended: the priests of Baal frozen in their bronze on Left, the people's candles
on the porch runs, Elijah's amber on Right beside his unlit wood, Porch Front dark. The priests' bronze cools and
settles. "Draw near, all ye people, come to me!": the people's candles drift along both porch runs toward Elijah's
corner and brighten on "come to me!".

Then his prayer, "Lord God of Abraham, Isaac, and Israel; this day let it be known that Thou art God, and I am Thy
servant!": a slow amber breathing on Right, swelling with each phrase he sings and settling as it ends, wider as the
prayer grows, and the people's candles steady, their flicker stilled. "Lord God of Abraham!" blazes once, then
quiets on the held note.

"Cast thy burden upon the Lord": the quartet, almost unaccompanied, and warmth spreads evenly across the house, from
Elijah's corner over the porch runs and out along the roofline, a soft wave with every chord, while at each pause
the harp's rising arpeggio sends a ripple of light from Right along the porch. "Let none be made ashamed, that wait
upon Thee": the warmth holds, and on the last chord draws back, leaving the people standing, Elijah beside his wood,
and heaven still dark, waiting.

The music is Mendelssohn's own: the end of No. 13, Elijah's first phrase from No. 14 and the outer phrases of No. 15,
transcribed from the Novello octavo vocal score into lord_god_of_abraham.musicxml and timed by
scripts/score_excerpt.py at the marked Adagio (crotchet 63) and Più adagio (crotchet 52), its fermatas held twice as
long. Elijah is played on cellos and horns; the quartet on soft strings, a clarinet and a horn; its arpeggios on the
harp. Nothing is added: the prayer is left to the music.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL10'
TITLE = 'Lord God of Abraham'
KIND = 'show'
DESCRIPTION = ("Elijah calls the people near and prays, his amber breathing slow and steady on Right. Then "
               "\"Cast thy burden upon the Lord\", and warmth spreads evenly across the house.")
VOICEOVER = 'Lord God of Abraham, let it be known this day that You are God.'

EX = excerpt(__file__)                      # the end of No. 13, No. 14 bars 7-12, No. 15 bars 1-5 and 13-17
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_ARIA = BAR[10]                            # "Lord God of Abraham"
T_QUARTET = min(n[0] for n in SUNG)         # "Cast thy burden"
T_LAST = max(n[0] for n in SUNG)            # "Thee!"
EL_ON = np.array([n[0] for n in ELIJAH])
CHORDS = np.array(sorted({round(n[0], 3) for n in SUNG}))
ARPS = sorted({round(n[0], 2) for n in ORCH if n[0] >= T_QUARTET - 0.5 and n[1] < 0.2})
ARP_START = [t for i, t in enumerate(ARPS) if i == 0 or t - ARPS[i - 1] > 1.0]   # the first note of each arpeggio


def phrases(notes, gap=0.6):
    """Elijah's sung phrases: (t0, t1), split where he rests gap seconds or more."""
    out = []
    for t, d, *_ in sorted(notes):
        if out and t - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], t + d)
        else:
            out.append([t, t + d])
    return out


PHRASES = phrases([n for n in ELIJAH if n[0] >= T_ARIA])

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
BRONZE = hexc('#b06a10')                    # Baal's altar
WOOD = hexc('#4a2a10')                      # Elijah's altar, unlit
GOLD = hexc('#ffc040')
WARM = hexc('#ffa030')                      # the warmth of "Cast thy burden"


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def last(arr, t, tau, span_=3.0):
    i = int(np.searchsorted(arr, t, side='right')) - 1
    return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0


def render(G, seed=10):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    baal = l0 + 0.5 * (l1 - l0)
    elijah = r0 + 0.22 * (r1 - r0)
    altar = r0 + 0.5 * (r1 - r0)
    runs = {s: span(G, s) for s in ('Porch Left', 'Porch Right')}
    flick = Flicker(rng, G.N, 1.5, 6.0)
    seethe = Flicker(rng, G.N, 2.5, 9.0)
    # distance from Elijah's corner along the roofline, for the warmth spreading out from him
    far = np.abs(d - elijah)
    reach = far[~heaven].max()

    def blob(c, w):
        return np.exp(-((d - c) / w) ** 2)

    def candles(shift):
        """The people's candles, every 34 along both porch runs, moved shift toward Right (they draw near)."""
        c = np.zeros(G.N)
        for seg, (a, b) in runs.items():
            for p in np.arange(a + 18, b - 10, 34):
                q = min(p + shift, b - 6)
                c += np.exp(-((d - q) / 5.0) ** 2) * ((d >= a) & (d <= b))
        return c

    for f in range(F):
        t = f * DT
        fr = light(DUST, (0.3 - 0.02 * smoothstep(0, 6, t)) * (1 - heaven) + 0.18 * heaven)

        # Baal's priests, frozen bronze from Hear and Answer, cooling to the cold altar the fire scene finds
        cool = smoothstep(0.3, 6.0, t)
        fr += light(BRONZE, left * ((0.22 + 0.06 * seethe(t)) * (1 - cool) + 0.18 * cool)
                    + (0.55 - 0.13 * cool) * blob(baal, 40))

        # the people draw near on "Draw near, all ye people, come to me!", then stand steady through the prayer
        near = smoothstep(0.5, T_ARIA - 1.5, t) * (1 - smoothstep(T_ARIA, T_ARIA + 4, t))
        come = smoothstep(EL_ON[6] - 0.2, EL_ON[6] + 0.6, t) * (1 - smoothstep(T_ARIA, T_ARIA + 3, t))
        still = smoothstep(T_ARIA, T_ARIA + 4, t)
        level = 0.6 + 0.26 * smoothstep(0, T_ARIA, t) + 0.35 * come
        fr += light(CANDLE, candles(14 * near) * people * level * (0.8 + (0.12 + 0.1 * (1 - still)) * flick(t)))

        # the unlit wood beside him
        fr += light(WOOD, 0.55 * blob(altar, 60))

        # Elijah: the recitative a pulse with each word; the prayer a slow breath that swells with every phrase
        k = int(np.searchsorted(EL_ON, t, side='right')) - 1
        word = float(np.exp(-(t - EL_ON[k]) / 0.45)) * smoothstep(0, 0.4, t) if k >= 0 and t < T_ARIA else 0.0
        breath = 0.0
        for i, (a, b) in enumerate(PHRASES):
            if a - 0.3 <= t < b + 3.0:
                rise = smoothstep(a - 0.3, a + 0.4 * (b - a), t) * (1 - smoothstep(b, b + 3.0, t))
                breath = max(breath, rise * (0.55 + 0.45 * i / max(len(PHRASES) - 1, 1)))
        quartet = smoothstep(T_QUARTET - 1, T_QUARTET + 2, t)
        size = 20 * (1 + 1.6 * breath)
        fr += light(AMBER, (0.8 + 0.15 * word + 0.2 * breath) * blob(elijah, size)
                    + (0.38 + 0.3 * breath) * blob(elijah, 110 * (1 + 0.8 * breath)))
        fr += light(CORE, (0.45 + 0.3 * word + 0.25 * breath) * blob(elijah, 6 + 6 * breath))

        # "Cast thy burden upon the Lord": warmth spreading evenly over the house from Elijah, a soft wave each chord
        if t >= T_QUARTET - 1:
            spread = smoothstep(T_QUARTET - 1, T_QUARTET + 14, t)
            leave = smoothstep(T_LAST + 1.0, D - 0.2, t)
            ck = last(CHORDS, t, 1.2)
            front = smoothstep(0, 0.25, spread * 1.25 - far / reach)
            depth = 0.36 + 0.16 * ck
            fr += light(WARM, (1 - leave) * depth * front * (1 - heaven) * (1 - 0.5 * left))
            for ta in ARP_START:             # the harp: a ripple of light from Right along the porch
                a = t - ta
                if 0 <= a < 3.0:
                    head = elijah - (elijah - runs['Porch Left'][0]) * min(a / 1.4, 1.0)
                    fr += light(GOLD, (1 - leave) * 0.85 * np.exp(-a / 1.1) * blob(head, 26) * (1 - heaven))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Elijah on cellos and horns; the accompaniment on the orchestra, its arpeggios on the harp; the quartet on soft
    strings with a clarinet and a horn."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    r0, r1 = span(G, 'Right')

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    e = pan_at(r0 + 0.22 * (r1 - r0))
    o = Orchestra(M, level=2.4)

    def role(t, d, m, v, hand):
        if t >= T_QUARTET - 0.5 and d < 0.2:
            return [('harp', 0, 4, 0.7)]
        if t >= T_QUARTET - 0.5 and hand == 0:
            return [('harp', 0, 0, 0.6), ('violins', 0, -14, 0.3)]
        return None

    o.tutti(ORCH, size=lambda t: 0.5, role=role, pan=lambda t, m: 0.3 * e)
    for t, d, m, v, h, who in ELIJAH:
        o.play('cellos', m, t, d, v + 4, e, 0.65)
        o.play('horns', m, t, d, v - 6, e, 0.4)
    parts = {'S': [('violins', 0, 4, 0.5), ('clarinets', 0, -4, 0.3)],
             'A': [('violas', 0, 4, 0.5)],
             'T': [('cellos', 0, 2, 0.45), ('horns', 0, -6, 0.3)],
             'B': [('cellos', 0, 0, 0.4), ('basses', -12, -2, 0.4)]}
    pans = {'S': -0.3, 'A': 0.0, 'T': 0.3, 'B': 0.5}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pans[who], g)
