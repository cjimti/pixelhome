"""Lift Thine Eyes: Elijah asleep under the juniper at the far end of Side; the angels of the Lord encamp around him,
three of them cross the house to his side, and a wave of light runs the whole roofline, watching over him.

The scene opens where the last one ended: Elijah's amber sunk low at the free end of Side, the wilderness a dim dust
over every run, nothing else lit. He breathes in his sleep. The tenor tells it, "See, now he sleepeth beneath a
juniper tree in the wilderness", and on "and there the angels of the Lord encamp round about all them that fear Him"
small silver lights are born one by one in heaven, on Porch Front, and drift out to camp all round the house, a ring
of watch-fires along every run.

Then the three angels sing, unaccompanied, "Lift thine eyes to the mountains, whence cometh help": three silver
lights set out from Porch Front, a little apart, each flaring on its own notes, and cross the house to him, down Porch
Left, along Left and out along Side, arriving at his side as the trio closes on "the maker of heaven and earth". On
the forte "lift" all three blaze and heaven glows behind them.

The chorus: "He, watching over Israel, slumbers not, nor sleeps". Over the running triplets a slow, steady wave of
silver travels the whole roofline from the free end of Right toward him, crest after crest, never a gap, brightening
as the sopranos and then the tenors take up the tune; as the last "sleeps" dies it settles into an even glow that
keeps watch over every run, which is how EL19 (O Rest in the Lord) begins.

The music is Mendelssohn's own: No. 27's recitative, the first sixteen bars of the trio No. 28 and the first nine of
the chorus No. 29, transcribed from the Novello octavo vocal score (the 1870 printing) into lift_thine_eyes.musicxml
and timed by scripts/score_excerpt.py at the marked tempos. The tenor is played on violas and a horn, the three
angels on flute, oboe and clarinet as the plan has them, the chorus on strings with woodwinds doubling, its
accompaniment orchestrated from the piano reduction; a production adds a dry desert air under the recitative and
a glint of glockenspiel as each angel comes into the camp.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL18'
TITLE = 'Lift Thine Eyes'
KIND = 'show'
DESCRIPTION = ("Elijah sleeps at the far end of Side. Angels camp around him, three cross the house to his side "
               "singing, and a wave of silver runs the whole roofline: He slumbers not, nor sleeps.")
VOICEOVER = 'He lay down under a juniper tree, and slept. And an angel touched him.'

EX = excerpt(__file__)                      # No. 27 bars 1-7, No. 28 bars 1-16, No. 29 bars 1-9
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
NOTES = EX['notes']
TENOR = [n for n in NOTES if n[5] == 'Tenor']
ANGELS = ('S1', 'S2', 'A1')
TRIO = {a: [n for n in NOTES if n[5] == a] for a in ANGELS}
CHOIR = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_ANGELS = BAR[4]                           # "an-gels of the Lord, encamp round about"
T_TRIO = BAR[9]
T_LIFT = BAR[10]                            # the sforzando "lift"
T_CHORUS = BAR[48]
T_SOP = BAR[49]
T_TEN = BAR[53]
T_SLEEPS = BAR[56]
TEN_ON = np.array([n[0] for n in TENOR])
CAMP_ON = TEN_ON[TEN_ON >= T_ANGELS - 0.01][:12]     # a light is born on each of the first twelve syllables
TRIO_ON = {a: np.array([n[0] for n in TRIO[a]]) for a in ANGELS}
CHOIR_ON = np.array(sorted({round(n[0], 3) for n in CHOIR}))
PULSE = np.array(sorted({round(n[0], 3) for n in ORCH if n[0] >= T_CHORUS - 0.01}))

DUST = hexc('#3a2008')                      # the wilderness
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
SILVER = hexc('#d8ecff')                    # the angels
WHITE = hexc('#ffffff')
WATCH = hexc('#b8d0f0')                     # the wave that keeps watch

ELIJAH = 12.0                               # the free end of Side, the farthest pixel from the street
BED = 0.15
SLEEP = 0.25
WATCH_FLOOR = 0.12                          # the even glow the wave settles into; EL19 opens on it
RESTS = (44.0, 74.0, 104.0)                 # where the three angels come to rest beside him (S1, S2, A1)


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def camp_spots(G):
    """Twelve camp lights spread round the house, Side included (they travel there; nothing starts there)."""
    return np.linspace(150.0, G.length - 30.0, 12)


def angel_at(G, a, t):
    """Each angel crosses from Porch Front to Elijah through the trio, a little apart, easing in at the end."""
    pf0, pf1 = span(G, 'Porch Front')
    start = {'S1': pf0 + 0.45 * (pf1 - pf0), 'S2': pf0 + 0.6 * (pf1 - pf0), 'A1': pf0 + 0.75 * (pf1 - pf0)}[a]
    lag = {'S1': 0.0, 'S2': 1.5, 'A1': 3.0}[a]
    u = smoothstep(T_TRIO + 1.0 + lag, T_CHORUS - 3.0 + 0.5 * lag, t)
    return start + (RESTS[ANGELS.index(a)] - start) * u


def elijah(G, t):
    """(amber level, core level): low, breathing slowly in his sleep, still at the scene's edges."""
    breath = 0.04 * np.sin(2 * np.pi * t / 5.2) * smoothstep(0, 4, t) * (1 - smoothstep(D - 4, D - 0.5, t))
    return SLEEP + breath, 0.08 + 0.5 * breath


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    heaven = (G.seg_of == 'Porch Front').astype(float)
    spots = camp_spots(G)
    pf0, pf1 = span(G, 'Porch Front')
    centre = 0.5 * (pf0 + pf1)
    tw = Flicker(rng, G.N, 0.6, 1.6)
    lam, per = 600.0, 60.0 / 126 * 4             # the wave: 600 units long, one crest a bar

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span_=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0

    for f in range(F):
        t = f * DT
        fr = light(DUST, BED * np.ones(G.N))

        # Elijah asleep
        amb, core = elijah(G, t)
        fr += light(AMBER, amb * blob(ELIJAH, 24))
        fr += light(CORE, core * blob(ELIJAH, 6))

        # the camp: lights born in heaven on the tenor's words, drifting out round the house, fading as the three come
        camp_fade = 1 - smoothstep(T_TRIO + 6, T_CHORUS - 2, t)
        twv = tw(t) if camp_fade > 0 and t >= CAMP_ON[0] else None
        for k, t0 in enumerate(CAMP_ON):
            if t < t0 or camp_fade <= 0:
                continue
            u = smoothstep(t0, t0 + 3.5, t)
            p = centre + (spots[k] - centre) * u
            born = np.exp(-(t - t0) / 0.5)
            lvl = (0.42 + 0.45 * born) * camp_fade * (0.9 + 0.1 * twv[int(np.argmin(np.abs(d - p)))])
            fr += light(SILVER, lvl * blob(p, 9 + 6 * born))

        # the three angels crossing to him
        if t >= T_TRIO - 1.0:
            arrive = smoothstep(T_TRIO - 1.0, T_TRIO + 0.5, t)
            lift = last(np.array([T_LIFT]), t, 1.2, 4.0)
            fr += light(SILVER, 0.35 * lift * heaven)
            for a in ANGELS:
                p = angel_at(G, a, t)
                sung = last(TRIO_ON[a], t, 0.6) if t < T_CHORUS else 0.0
                lvl = arrive * (0.4 + 0.35 * sung + 0.4 * lift)
                if t >= T_CHORUS:
                    lvl = 0.35 + 0.05 * (1 - smoothstep(T_CHORUS, T_CHORUS + 3, t))
                fr += light(SILVER, lvl * blob(p, 9 + 5 * sung))
                fr += light(WHITE, 0.4 * lvl * (sung + lift) * blob(p, 3))

        # He, watching over Israel: a wave along the whole roofline, toward him, never a gap, settling to an even glow
        if t >= T_CHORUS - 0.5:
            come = smoothstep(T_CHORUS - 0.5, T_CHORUS + 2.0, t)
            settle = smoothstep(T_SLEEPS, D - 0.3, t)
            voices = last(CHOIR_ON, t, 0.9)
            beat = last(PULSE, t, 0.3, 0.6)
            crest = 0.5 + 0.5 * np.sin(2 * np.pi * (d / lam + t / per))
            amp = come * (1 - settle) * (0.26 + 0.1 * voices + 0.04 * beat)
            floor = WATCH_FLOOR * smoothstep(T_CHORUS - 0.5, T_CHORUS + 4.0, t)
            fr += light(WATCH, floor + amp * crest)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The tenor on violas with a horn; the trio unaccompanied on flute, oboe and clarinet, each panned where its light
    is; the chorus on strings with woodwinds doubling over the orchestrated triplets. A dry air under the recitative,
    a glint of glockenspiel as each camp light settles."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=3.4)
    for t, d, m, v, h, who in TENOR:
        o.play('violas', m, t, d, v, 0.0, 0.55)
        o.play('horns', m, t, d, v - 10, 0.0, 0.3)
    for k, t0 in enumerate(CAMP_ON):
        o.play('glock', 72 + (k * 5) % 12, t0 + 3.4, 0.3, 46, pan_at(camp_spots(G)[k]), 0.25)
    voice = {'S1': ('flutes', 0, 0.75), 'S2': ('oboes', 0, 0.6), 'A1': ('clarinets', 0, 0.7)}
    for a in ANGELS:
        section, tr, g = voice[a]
        for t, d, m, v, h, who in TRIO[a]:
            o.play(section, m + tr, t, d, v + 4, pan_at(angel_at(G, a, t)), g)

    def role(t, d, m, v, hand):
        if hand == 0:
            return [('violins' if m >= 55 else 'violas', 0, -16, 0.4)]
        return [('cellos', 0, -10, 0.5), ('basses', -12, -14, 0.35)] if m < 52 else [('violas', 0, -14, 0.4)]
    o.tutti(ORCH, role=role)
    parts = {'S': [('violins', 0, -4, 0.5), ('flutes', 0, -8, 0.35)], 'A': [('violas', 0, -4, 0.5)],
             'T': [('cellos', 0, -2, 0.55), ('clarinets', 0, -8, 0.3)], 'B': [('cellos', 0, -2, 0.5)]}
    for t, d, m, v, h, who in CHOIR:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.0, g)
        if d >= 0.9:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 14, 0.0, 0.25)
    o.wind(0.0, T_TRIO - 0.5, level=lambda tt: 0.12 + 0.06 * np.sin(tt * 0.7), pan=pan_at(ELIJAH))
    o.effects([(0.0, -6.0), (T_TRIO - 1.0, -6.0)])
