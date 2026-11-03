"""Rejoice, O Judah: Simon calls Judah to rejoice, the chorus answers with Hallelujah, Amen, and the house ends on the
lights of the porch.

The scene opens where O Lovely Peace (JM14) ended, the house in warm gold, and over the first seconds the evening
gives way to the night (CARRY, from JM14's last frame: change both together). Then it is quiet: the house in a low
night blue, the lights' glow on the Temple. Simon's deep blue kindles in the
middle of Left and swells on each note of his phrase, "Rejoice, O Judah, and in songs divine, with Cherubim and
Seraphim, harmonious join", and the blue over the house brightens a little as he sings. The basses answer him alone,
"Hallelujah, Amen": on each of their notes a blue light steps out from Simon along Left toward the porch, and stays.

Then everyone, fortissimo, "O Judah, rejoice!": the whole house bursts into the people's blue and white bands, and gold
fills the Temple and runs out along the porch. Gold glitters over the wings on the long runs of "rejoice"; the bands
breathe with each chord of "in songs divine"; on the quick repeated notes of "with Cherubim and Seraphim" white lights,
the angels, step along the porch runs and the wings, one step a note. Every "Hallelujah" sends a wave of gold out from
the Temple to the ends of the house. The great "Amen."s: on each the whole house flashes white and gold, and the
orchestra's answering runs carry a gold light across the house, left to right. The Adagio, "Amen, Hallelujah, Amen":
the house broad and full in blue, white and gold, slowing with the music; and on the last Amen it all settles, over
the held chord, back to the steady glow of the lights on the porch and a dim night blue, where the next night begins.

The music is Handel's own: No. 67, Simon's first phrase (its bars 14-18), and No. 68, the chorus "Hallelujah, Amen":
its first two bars, the basses alone, then from "O Judah, rejoice" (its bar 14) to the end, transcribed from the
Novello vocal score into rejoice_o_judah.musicxml and timed by scripts/score_excerpt.py at the marked tempos (the air
Andante allegro at crotchet 88, the chorus Allegro at 100, its Adagio at 54). Simon plays on bassoons and cellos over
the air's strings; the chorus on strings with oboes and bassoons doubling, horns on its long notes, the strings'
running semiquavers where the reduction writes them, trumpets on the sopranos' line and timpani from "O Judah" on,
and a harpsichord continuo throughout. render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM15'
TITLE = 'Rejoice, O Judah'
KIND = 'show'
DESCRIPTION = ("Simon's deep blue calls Judah to rejoice; the chorus answers, and the whole house fills with blue, "
               "white and gold through Hallelujah and Amen, then settles back to the lights on the porch.")
VOICEOVER = 'Rejoice, O Judah. Hallelujah, and Amen. And the lights burn on into the night.'

EX = excerpt(__file__)              # No. 67 bars 14-18 (1-5 here), No. 68 bars 1-2 (6-7) and 14-37 (8-31)
BAR = {int(m): t for m, t in EX['bars']}
BAR[1] = 0.0
D = round(EX['seconds'] + 2.5, 2)
NOTES = EX['notes']
VOICES = ('S', 'A', 'T', 'B')
SIMON = [n for n in NOTES if n[5] == 'Simon']
SUNG = [n for n in NOTES if n[5] in VOICES]
ORCH = [n for n in NOTES if n[5] == 'Orch']


def beat(b):
    """A crotchet's length in bar b."""
    return (BAR[b + 1] - BAR[b]) / 4


def at(b, q):
    """The time of beat q (0-based, fractions allowed) of bar b."""
    return BAR[b] + q * beat(b)


T_CHORUS = BAR[6]                   # the basses alone: "Hallelujah, Amen"
T_FULL = at(8, 1)                   # everyone, ff: "O Judah, rejoice"
T_SONGS = BAR[11]                   # "in songs divine"
CHERUBIM = [(12, 13), (14, 15)]     # the bars of "with Cherubim and Seraphim" (quick repeated notes)
RUNS = (9, 10)                      # the semiquaver runs of "rejoice"
HALS = [at(16, 1), at(17, 0), at(22, 1), at(23, 0), at(23, 1)]     # Hallelujahs: gold waves from the Temple
AMENS = [BAR[24], at(25, 3), BAR[26], at(27, 3), BAR[28]]          # the great "Amen."s
ANSWERS = [(at(24, 1), BAR[25] + 3 * beat(25)), (at(26, 1), BAR[27] + 3 * beat(27))]   # the orchestra's runs
T_ADAGIO = at(28, 3)                # "Hallelujah", Adagio
T_LAST = BAR[31]                    # "-men.", the last chord
BASS_ALONE = [n for n in SUNG if n[5] == 'B' and T_CHORUS - 0.01 <= n[0] < T_FULL - 0.7]
SIMON_ON = np.array([n[0] for n in SIMON])
ONSETS = np.array(sorted({round(n[0], 3) for n in SUNG if n[0] >= T_FULL - 0.7}))
CHER_ON = [n[0] for n in SUNG if n[5] == 'S' and any(BAR[a] + 0.5 * beat(a) <= n[0] < BAR[a + 1]
                                                     for a, _ in CHERUBIM)]

NIGHT = hexc('#0a1a4a')
BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')
SIMON_C = hexc('#2850c8')           # Simon
GOLD = hexc('#ffc83c')              # Judas's gold, the victory
OIL = hexc('#ffb33a')               # the Temple light
TIP = hexc('#fff1c0')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def last_pulse(t, onsets, tau):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    return float(np.exp(-(t - onsets[i]) / tau)) if i >= 0 else 0.0


def marched(t):
    """How many beats the bands have stepped by t: a quick step on each beat of the Allegro, none in the Adagio."""
    if t < T_FULL:
        return 0.0
    b = max(k for k in BAR if BAR[k] <= min(t, T_ADAGIO) or k == 8)
    q = (min(t, T_ADAGIO) - BAR[b]) / beat(b)
    n = 4 * (b - 8) + np.floor(q) - 1
    return float(n + smoothstep(0.0, 0.3, q % 1.0))


WARM = hexc('#ffcf8a')              # O Lovely Peace's (JM14) last frame: warm gold over the house
OIL = hexc('#ffb33a')
CARRY = 4.0                         # seconds JM14's last frame takes to give way to the night
JM14_END = 82.225                   # JM14's length: its Glow is carried on from there (change with JM14)


def jm14_end(G, glow14, t):
    """O Lovely Peace's last frame (JM14's last_frame): warm gold over the house, Side a little dimmer, the Temple's
    light on the porch. Change it with JM14."""
    seg = G.seg_of
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    return (light(WARM, 0.34 * (1 - temple) * (1 - 0.3 * side)) + light(OIL, 0.4 * temple)
            + glow14.frame(JM14_END + t, 1.0))


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    glow14 = Glow(G, 14)
    temple = (seg == 'Porch Front').astype(float)
    road = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    wings = np.isin(seg, ['Left', 'Right']).astype(float)
    side = (seg == 'Side').astype(float)
    house = 1 - temple
    l0, l1 = span(G, 'Left')
    p0, p1 = span(G, 'Porch Left')
    f0, f1 = span(G, 'Porch Front')
    mid = 0.5 * (f0 + f1)
    sc = l0 + 0.45 * (l1 - l0)                                     # Simon, in the middle of Left
    out_d = np.abs(d - mid)                                        # distance out from the Temple
    shimmer = Flicker(rng, G.N, 0.2, 0.7)
    glitter = Flicker(rng, G.N, 4.0, 9.0)
    dmin, dmax = float(d.min()), float(d.max())
    # the basses' steps: one light a note, from Simon toward the corner of the porch
    steps = np.linspace(sc + 25, p0 + 0.5 * (p1 - p0), len(BASS_ALONE))
    # the angels: positions stepping along the porch runs and the wings, one step a quick note
    angel_paths = [np.linspace(p1, p0, 40), np.linspace(span(G, 'Porch Right')[0], span(G, 'Porch Right')[1], 40),
                   np.linspace(l1, l0 + 60, 40), np.linspace(*span(G, 'Right'), 40)]
    for f in range(F):
        t = f * DT
        # how full the house is: low before the chorus, full from "O Judah", settling on the last Amen
        burst = smoothstep(T_FULL - 0.05, T_FULL + 0.15, t)
        settle = smoothstep(T_LAST + 0.6, D - 0.6, t)
        full = burst * (1 - settle)
        sing = smoothstep(0.3, 3.0, t) * (1 - burst)                # the blue brightening a little as Simon sings
        fr = light(NIGHT, (0.22 + 0.03 * shimmer(t)) * house * (1 - 0.6 * full) * (1 - 0.15 * settle))
        fr += light(BLUE, 0.1 * sing * (wings + road + 0.5 * side))
        # the Temple: the lights' glow, gold filling it in the full chorus
        fr += glow.frame(t, 1.0 + 1.3 * full)
        fr += light(OIL, 0.55 * full * temple * (0.92 + 0.08 * shimmer(t)))
        # Simon: deep blue in the middle of Left, swelling on each note, fading as the chorus takes over
        if t < T_FULL + 2.0:
            k = last_pulse(t, SIMON_ON, 0.4) if t < T_CHORUS else 0.0
            on = smoothstep(0.4, 1.6, t) * (1 - smoothstep(T_CHORUS, T_FULL + 2.0, t) * 0.7)
            lvl = on * (0.75 + 0.35 * k)
            fr += light(SIMON_C, lvl * (1.3 * np.exp(-((d - sc) / 8) ** 2) + 0.4 * np.exp(-((d - sc) / 30) ** 2)))
            fr += light(WHITE, 0.3 * on * k * np.exp(-((d - sc) / 2.5) ** 2))
        # the basses alone: a blue light steps out on each note and stays
        if T_CHORUS <= t < T_FULL + 1.0:
            fade = 1 - smoothstep(T_FULL, T_FULL + 1.0, t)
            for n, c in zip(BASS_ALONE, steps):
                a = t - n[0]
                if a >= 0:
                    fr += light(BLUE, fade * (0.7 + 0.6 * np.exp(-a / 0.25)) * np.exp(-((d - c) / 4.0) ** 2))
                    fr += light(WHITE, fade * 0.5 * np.exp(-a / 0.2) * np.exp(-((d - c) / 2.0) ** 2))
        if full > 0:
            # the people's bands, lifted by every chord
            p = last_pulse(t, ONSETS, 0.35 if t < T_ADAGIO else 0.9)
            swell = smoothstep(T_SONGS, BAR[12], t) - smoothstep(BAR[13] - 0.5, BAR[14], t) * 0.5
            lvl = full * (0.42 + 0.18 * p + 0.08 * swell + 0.12 * smoothstep(T_ADAGIO - 0.5, T_ADAGIO + 1.5, t))
            lvl = lvl * (0.94 + 0.06 * shimmer(t))
            # the bands step outward from the Temple on every beat, a quarter of a band at a time
            band = (np.sin(2 * np.pi * (out_d - 27.5 * marched(t)) / 110.0) > 0.25).astype(float)
            fr += light(BLUE, lvl * band * house) + light(WHITE, 0.8 * lvl * (1 - band) * house)
            # the burst on "O Judah": gold out of the Temple along the whole house
            a = t - T_FULL
            if 0 <= a < 3.0:
                front = 30 + 420 * a
                fr += light(GOLD, 0.9 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - mid) - front) / 40.0) ** 2) * house)
                fr += light(WHITE, 0.5 * np.exp(-a / 0.25) * np.ones(G.N))
            # gold glitter over the wings on the runs of "rejoice"
            for b in RUNS:
                if at(b, 2) <= t < BAR[b + 1]:
                    g = np.maximum(glitter(t), 0) ** 3
                    fr += light(GOLD, 0.8 * g * (wings + road))
            # the angels: white lights stepping along the runs and the wings on the quick notes
            k = int(np.searchsorted(CHER_ON, t, side='right')) - 1
            if k >= 0 and t - CHER_ON[k] < 1.0:
                a = t - CHER_ON[k]
                for path in angel_paths:
                    for j, tail in enumerate((1.0, 0.45, 0.2)):
                        c = path[(k - j) % len(path)]
                        fr += light(WHITE, 1.4 * tail * np.exp(-a / 0.45) * np.exp(-((d - c) / 5.0) ** 2))
            # Hallelujah: gold waves out from the Temple
            for th in HALS:
                a = t - th
                if 0 <= a < 2.5:
                    front = 20 + 380 * a
                    wave = np.exp(-((out_d - front) / 55.0) ** 2) * house
                    fr += light(GOLD, 1.0 * np.exp(-a / 1.1) * wave)
                    fr += light(TIP, 0.35 * np.exp(-a / 0.6) * np.exp(-((out_d - front) / 12.0) ** 2) * house)
            # the great Amens: the whole house flashes white and gold
            for ta in AMENS:
                a = t - ta
                if 0 <= a < 1.5:
                    fr += light(WHITE, 0.55 * np.exp(-a / 0.2) * house)
                    fr += light(GOLD, 0.5 * np.exp(-a / 0.5) * np.ones(G.N))
            # the orchestra's runs: a gold light carried across the house, left to right
            for ta, tb in ANSWERS:
                if ta <= t < tb + 0.6:
                    u = smoothstep(ta, tb, t)
                    c = dmin + 0.12 * (dmax - dmin) + 0.8 * (dmax - dmin) * u
                    fade = 1 - smoothstep(tb, tb + 0.6, t)
                    fr += light(GOLD, 0.9 * fade * np.exp(-((d - c) / 18.0) ** 2))
                    fr += light(TIP, 0.5 * fade * np.exp(-((d - c) / 5.0) ** 2))
            # the Adagio: the house broad and full, gold over it all, deepest on the last chord
            ad = smoothstep(T_ADAGIO - 0.3, T_ADAGIO + 2.0, t) * (1 - settle)
            fr += light(GOLD, 0.28 * ad * house * (0.9 + 0.1 * shimmer(t)))
            a = t - T_LAST
            if a >= 0:
                fr += light(WHITE, 0.35 * np.exp(-a / 0.5) * house * (1 - settle))
        # the opening carries O Lovely Peace's warm evening (JM14) and gives way to the night over the first seconds
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * jm14_end(G, glow14, t)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Simon on bassoons and cellos from Left over the air's strings; the chorus on strings with oboes and bassoons
    doubling, horns on the long notes and trumpets on the sopranos from "O Judah"; the strings' semiquavers where the
    reduction writes them; the orchestra's answers between the Amens; a harpsichord continuo; timpani for the
    finale, a roll under the last chord."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    l0, l1 = span(G, 'Left')
    psim = pan_at(l0 + 0.45 * (l1 - l0))
    o = Orchestra(M, level=1.35)
    for t, dd, m, v, h, who in SIMON:
        o.play('bassoons', m, t, max(dd, 0.25), v + 4, psim, 1.1)
        o.play('cellos', m, t, max(dd, 0.25), v, psim, 0.8)
    side = {'S': -0.35, 'A': -0.15, 'T': 0.15, 'B': 0.35}
    for t, dd, m, v, h, who in SUNG:
        alone = t < T_FULL - 0.7
        pan = 0.0 if alone else side[who]
        vel = v + (6 if t >= T_FULL - 0.01 else 8)
        if who == 'S':
            o.play('violins', m, t, dd * 0.97, vel, pan, 0.75)
            o.play('oboes', m, t, dd * 0.95, vel - 8, pan, 0.45)
            if dd >= 0.29:
                o.play('trumpets', m, t, dd * 0.9, vel - 6, -0.1, 0.4)
        elif who == 'A':
            o.play('violins', m, t, dd * 0.97, vel - 4, pan, 0.55)
            if dd >= 0.55:
                o.play('horns', m, t, dd * 0.95, vel - 12, pan, 0.35)
        elif who == 'T':
            o.play('violas', m, t, dd * 0.97, vel, pan, 0.7)
            if dd >= 0.55:
                o.play('horns', m, t, dd * 0.95, vel - 12, pan, 0.35)
        else:
            o.play('cellos', m, t, dd * 0.97, vel, pan, 0.8)
            o.play('basses', m - 12 if m >= 52 else m, t, dd * 0.97, vel - 4, pan, 0.6)
            o.play('bassoons', m, t, dd * 0.95, vel - 10, pan, 0.45)
    # the air's strings and the orchestra's answers between the Amens, from the reduction
    for t, dd, m, v, h, who in ORCH:
        if t < T_CHORUS:
            sec = 'violins' if m >= 64 else 'violas' if m >= 55 else 'cellos'
            o.play(sec, m if m >= 36 else m + 12, t, max(dd, 0.25), v - 14, None, 0.45)
            if h == 1:
                o.play('basses', m, t, max(dd, 0.25), v - 18, None, 0.4)
        else:
            sec = 'violins' if m >= 64 else 'violas' if m >= 55 else 'cellos'
            o.play(sec, m if m >= 36 else m + 12, t, max(dd, 0.2), v + 8, None, 0.95)
            if m >= 69:
                o.play('oboes', m, t, max(dd, 0.2), v, None, 0.5)
            if h == 1 and m < 48:
                o.play('basses', m, t, max(dd, 0.2), v, None, 0.5)
    # the strings' running semiquavers: the voices' chord repeated, as the reduction writes it
    for b in (9, 10, 18, 19):
        q = beat(b) / 4
        for k in range(16):
            tk = BAR[b] + k * q
            ch = sorted({n[2] for n in SUNG if n[5] in ('S', 'A') and n[0] <= tk + 0.01 < n[0] + n[1]})
            for m in ch:
                o.play('violins', m, tk, q * 0.9, 74 if k % 4 else 82, -0.2 if m == ch[-1] else 0.2, 0.25)
    # the harpsichord continuo: the air's bass, the chorus basses with their chord
    cont = [(t, m, 72, min(dd, 0.35)) for t, dd, m, v, h, who in ORCH if t < T_CHORUS]
    for t, dd, m, v, h, who in SUNG:
        if who == 'B':
            cont.append((t, m, 82, min(dd, 0.35)))
            for cm in sorted({n[2] for n in SUNG if abs(n[0] - t) < 0.02 and n[5] in ('A', 'T')}):
                cont.append((t, cm, 70, min(dd, 0.35)))
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, D + 2.0), 0.0, 0.4, 0.0)
    # timpani: the burst, the Hallelujahs, each Amen, the Adagio, a roll under the last chord
    o.hit('timpani', T_FULL, 108, pitch=0, gain=0.4, pan=0.2)
    for th in HALS:
        o.hit('timpani', th, 96, pitch=0, gain=0.3, pan=0.2)
    for i, ta in enumerate(AMENS):
        o.hit('timpani', ta, 112, pitch=0 if i % 2 == 0 else -5, gain=0.4, pan=0.2)
    for b in (29, 30):
        o.hit('timpani', BAR[b], 100, pitch=-5 if b == 30 else 0, gain=0.35, pan=0.2)
    o.hit('timpani roll', T_LAST, 96, pitch=0, gain=0.3, pan=0.2)
    o.hit('timpani', T_LAST + 4 * beat(30), 104, pitch=0, gain=0.3, pan=0.2)
