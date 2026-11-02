"""Holy, Holy, Holy: above the still small voice the Seraphim cry to one another; silver rises across heaven in
layers, the whole house answers, glory fills all the earth, and at the end the light gathers into Elijah on Right.

The scene opens where EL20 ended: calm silver lying over the whole house, brightest on Porch Front. "Above Him stood
the Seraphim": the silver draws back off the wings into heaven, over a night-blue bed, and on "and one cried to
another" two lights call from the two ends of Porch Front. The quartet sings "Holy, holy, holy is God the Lord",
pianissimo: each of the four voices is a layer of silver across Porch Front, the first treble alone at first, then
all four, wider and wider, every note swelling its layer.

The chorus answers, forte, "Holy, holy, holy is God the Lord": the whole house rises with it, full and bright, each
chord a slow swell of white over every run and none of them a flash. Then "Now His glory hath filled all the earth",
quiet, the quartet and the chorus overlapping: gold spreads out from heaven along the roofline, run by run, to both
free ends, with a sparkle on every sung note inside it, until the whole house is filled on "all the earth". Over the
gold the quartet's layers rise again on Porch Front for its second "Holy, holy, holy", the chorus murmuring "Now His
glory" under it; then the chorus's own "Holy is God the Lord" lifts the whole house once more. On the last "Lord" all
the light gathers along the roofline into one place on Right, where Elijah stands in white-hot amber over a dark
night, heaven a faint warm glow: which is how EL22 (The Fiery Chariot) begins.

The music is Mendelssohn's own: No. 35, transcribed from the Novello octavo vocal score (the 1870 printing) into
holy_holy_holy.musicxml and timed by scripts/score_excerpt.py at the marked Adagio non troppo (crotchet 72): the
recitative and both "Holy"s (bars 1-11) and "Now His glory hath filled all the earth" to the chorus's "Holy is God
the Lord" (17-30). The recitative is played on violas and a clarinet, the quartet on flute, oboe, clarinet and horn,
the chorus on strings with woodwinds doubling, horns and trombones in its fortes; a production adds a cymbal swell
into each forte, timpani under its chords, and a glockenspiel glint as the glory fills the house.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL21'
TITLE = 'Holy, Holy, Holy'
KIND = 'show'
DESCRIPTION = ("The Seraphim cry Holy, holy, holy: silver rises across heaven in layers, the whole house answers, and "
               "glory fills all the earth, run by run, until the light gathers into Elijah on Right.")
VOICEOVER = 'Holy, holy, holy is God the Lord. The whole earth is full of His glory.'

EX = excerpt(__file__)                      # No. 35 bars 1-11, 17-30
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
NOTES = EX['notes']
QUARTET = ('S1', 'S2', 'A1', 'A2')
QUART = {q: [n for n in NOTES if n[5] == q] for q in QUARTET}
CHOIR = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ALTO = [n for n in NOTES if n[5] == 'Alto']
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_QUARTET = BAR[4]
T_CHORUS = BAR[8]
T_GLORY = BAR[17]
T_EARTH = BAR[24]                           # "all the earth": the house is filled
T_HOLY2 = BAR[25]
T_FORTE = BAR[29]
T_LORD = BAR[30] + 1.0 * 60 / 72 * 2        # the last "Lord"
CRIED = np.array([n[0] for n in ALTO if n[0] >= BAR[2]])
CHORDS = np.array(sorted({round(n[0], 3) for n in CHOIR if (T_CHORUS - 0.01 <= n[0] < T_GLORY) or n[0] >= T_FORTE - 0.01}))
SPARK = [n for n in NOTES if n[5] in QUARTET + ('S', 'A', 'T', 'B') and T_GLORY - 0.01 <= n[0] < T_FORTE]

NIGHT20 = hexc('#3a4c80')                   # EL20's last frame: night, and calm silver over everything
SILVER = hexc('#d8ecff')
WHITE = hexc('#f4f8ff')
GLORY = hexc('#ffc860')
AMBER = hexc('#ffb040')                     # Elijah, as EL22 opens
CORE = hexc('#fff4d0')
NIGHT22 = hexc('#0c1430')
HEAVEN = hexc('#fff0c8')

LAYER = {'S1': 40.0, 'S2': 85.0, 'A1': 125.0, 'A2': 165.0}     # each quartet voice's half-width across Porch Front


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def env(notes, t, attack=0.3, sustain=0.6, release=0.8):
    """How strongly a voice sounds at t: swells on each note, holds a little while it is held, dies after it."""
    v = 0.0
    for n in notes:
        a, b = n[0], n[0] + n[1]
        if a <= t < b + release:
            rise = smoothstep(a, a + attack, t)
            held = sustain + (1 - sustain) * np.exp(-(t - a) / 0.7)
            v = max(v, rise * held * (1 - smoothstep(b, b + release, t)))
    return v


def render(G, seed=35):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    heaven = (G.seg_of == 'Porch Front').astype(float)
    pf0, pf1 = span(G, 'Porch Front')
    centre = 0.5 * (pf0 + pf1)
    s_out = np.abs(d - centre)
    far = s_out.max()
    r0, r1 = span(G, 'Right')
    elijah = r0 + 0.45 * (r1 - r0)               # where EL22's Elijah stands
    tw = Flicker(rng, G.N, 0.8, 3.0)
    silver20 = np.clip(0.45 * np.exp(-(s_out / 272.0) ** 2) + 0.42, 0, 0.55)
    sparks = [(n[0], float(rng.uniform(0, far)) * rng.choice([-1, 1]), n[1]) for n in SPARK]

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span_=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0

    for f in range(F):
        t = f * DT
        k = smoothstep(T_LORD - 0.3, D - 0.1, t)         # the gathering into Elijah: 1 at the last frame
        keep = 1 - k
        fr = light(NIGHT20, 0.22 * keep * np.ones(G.N))

        # EL20's silver draws back into heaven through the recitative
        back = smoothstep(0.5, BAR[3], t)
        wings = silver20 * (1 - back) + 0.12 * back
        sky = silver20 * (1 - back) + 0.16 * back             # heaven too, so the quartet's layers can rise on it
        fr += light(SILVER, keep * np.where(heaven > 0, sky, wings) * (1 - 0.5 * smoothstep(T_CHORUS, T_CHORUS + 1, t)))

        # "and one cried to another": the two ends of Porch Front call in turn
        if BAR[2] <= t < T_QUARTET + 1.0:
            for j, tc in enumerate(CRIED):
                a = t - tc
                if 0 <= a < 1.2:
                    p = pf0 + 25 if j % 2 == 0 else pf1 - 25
                    fr += light(WHITE, 0.6 * np.exp(-a / 0.4) * blob(p, 16))

        # the quartet: four layers of silver across heaven
        for q in QUARTET:
            e = env(QUART[q], t)
            if e > 0.001:
                w = LAYER[q]
                band = smoothstep(w + 20, w - 10, s_out) * heaven
                fr += light(SILVER, keep * e * (0.42 + 0.1 * (q == 'S1')) * band)
                fr += light(WHITE, keep * 0.55 * e * (blob(centre - w, 6) + blob(centre + w, 6)))

        # the chorus's fortes: the whole house answers, a slow swell on each chord, never a flash
        forte = ((t >= T_CHORUS - 0.3) & (t < T_GLORY)) or t >= T_FORTE - 0.3
        if forte:
            i = int(np.searchsorted(CHORDS, t, side='right')) - 1
            sw = 0.0
            if i >= 0:
                a = t - CHORDS[i]
                sw = smoothstep(0, 0.3, a) * (0.75 + 0.25 * np.exp(-a / 0.6))
                if i > 0 and a < 0.3:                    # carry over from the previous chord: no dip to dark
                    sw = max(sw, 0.75)
            tail = 1 - smoothstep(BAR[11] + 1.0, T_GLORY + 0.5, t) if t < T_GLORY + 1 else 1.0
            t0 = T_CHORUS if t < T_GLORY else T_FORTE
            lvl = (0.45 + 0.4 * sw) * tail * smoothstep(t0 - 0.3, t0 + 0.3, t)
            fr += light(WHITE, keep * lvl * (1 - 0.35 * np.clip(s_out / far, 0, 1)))
            fr += light(SILVER, keep * 0.4 * lvl * heaven)

        # Now His glory hath filled all the earth: gold out from heaven to both free ends, sparkling on every note
        if t >= T_GLORY - 0.5:
            reach = 40 + (far + 40) * smoothstep(T_GLORY, T_EARTH, t) ** 1.2
            filled = smoothstep(reach, reach - 120, s_out)
            g = 0.5 * smoothstep(T_GLORY - 0.5, T_GLORY + 2.0, t) * (1 - 0.2 * smoothstep(T_HOLY2, T_HOLY2 + 2, t))
            fr += light(GLORY, keep * g * filled * (0.9 + 0.1 * tw(t)))
            for t0, p, dur in sparks:
                a = t - t0
                if 0 <= a < 1.5:
                    pp = centre + p
                    fr += light(WHITE, keep * 0.5 * np.exp(-a / 0.5) * blob(pp, 5) * filled)

        # the gathering: all the light along the roofline draws into Elijah on Right, as EL22 opens
        if k > 0:
            w = 90 + 2400 * (1 - k) ** 2
            fr += light(NIGHT22, 0.32 * k * np.ones(G.N))
            fr += light(HEAVEN, 0.12 * k * heaven)
            fr += light(AMBER, 0.85 * k * blob(elijah, 18) + (0.3 + 0.5 * (1 - k)) * min(1.0, 3 * k) * blob(elijah, w))
            fr += light(CORE, 0.45 * k * blob(elijah, 6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The recitative on violas and a clarinet; the quartet on flute, oboe, clarinet and horn, from heaven; the chorus on
    strings with woodwinds doubling, horns and trombones in its fortes, the accompaniment from the reduction. A cymbal
    swell into each forte, timpani under its chords, a glockenspiel glint as the glory fills the house."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.85)
    for t, d, m, v, h, who in ALTO:
        o.play('violas', m, t, d, v, 0.0, 0.5)
        o.play('clarinets', m, t, d, v - 8, 0.0, 0.35)
    voice = {'S1': ('flutes', 0.7, -0.2), 'S2': ('oboes', 0.55, 0.2), 'A1': ('clarinets', 0.6, -0.1),
             'A2': ('horns', 0.45, 0.1)}
    for q in QUARTET:
        section, g, p = voice[q]
        for t, d, m, v, h, who in QUART[q]:
            o.play(section, m, t, d, v + 6, p, g)

    def forte(t):
        return (T_CHORUS - 0.1 <= t < T_GLORY) or t >= T_FORTE - 0.1

    def size(t):
        return 1.0 if forte(t) else 0.3
    o.tutti(ORCH, size=size)
    parts = {'S': [('violins', 0, -2, 0.5), ('flutes', 0, -8, 0.3)], 'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.3)], 'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4)]}
    for t, d, m, v, h, who in CHOIR:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.0, g)
        if forte(t) and d >= 0.5:
            o.play('horns', m - (12 if m > 67 else 0), t, d, v - 6, 0.0, 0.35)
            if who in ('T', 'B'):
                o.play('trombones', m, t, d, v - 8, 0.0, 0.3)
    for tc in (T_CHORUS, T_FORTE):
        o.hit('cymbal swell', tc - 1.6, 90, gain=0.22)
    for tc in CHORDS[::2]:
        o.hit('timpani', tc, 92, pitch=-5, gain=0.22)
    for k, (t, d, m, v, h, who) in enumerate(SPARK[::3]):
        o.play('glock', 72 + (m % 12), t, 0.3, 40, pan_at(G.length * ((k * 0.37) % 1.0)), 0.18)
