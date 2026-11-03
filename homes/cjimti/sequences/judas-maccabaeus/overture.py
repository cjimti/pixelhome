"""Overture: the Seleucids hold the land and the Temple; in the hills, the fugue wakes the Maccabees one voice at a time.

The house is in Seleucid purple, and the Temple on Porch Front is grey with four idols standing in it, the glow of the
lights dim beneath them. In the Grave the armies march in from the road from Antioch, the free end of Right: every
dotted step of the bass sends a wave of heavier purple rolling up Right toward the porch, the upper strings' quick
upbeats glint on the helmets, and each bar lands on the idols. On Left, in the hills of Modein, a few blue lights
are barely there.

Then the Allegro, a fugue, and each of its voices enters as its own light. The first violins alone: two blue lights
on Left flicker with every sixteenth of the subject. The second violins answer, and the people on Porch Left and Porch
Right wake, small blue and white lights brightening note by note, with a third blue light on Left. The basses take
the subject in the purple, which pulses heavier on Right and Side with every note; the violas join with the last two
blue lights on Left. On the cadence the music holds an F major chord, and Mattathias, the old priest whose refusal
starts the revolt, appears as a white light among the blue on Left: that is where Mourn, Ye Afflicted Children
(JM02) begins.

The music is Handel's own, every part note for note: the Grave's first four bars, bars 18-19 and its second-time
chord, then the Allegro's first 29 bars, cut on the F chord halfway through bar 29, transcribed from the 1769 full
score (London: William Randall, successor to J. Walsh) into overture.musicxml, numbered straight through (the Grave
1-7, the Allegro 8-36), and timed by scripts/score_excerpt.py at a Grave of crotchet 60 and an Allegro of quaver 112.
The first violins are doubled by oboes in the Grave, as the score marks, and the Allegro is for strings alone; a
harpsichord plays the continuo with the basses. The last chord is held for a stage pause.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, keys, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM01'
TITLE = 'Overture'
KIND = 'show'
DESCRIPTION = ("The house in Seleucid purple, the Temple grey with idols; the armies march in from the road from "
               "Antioch, and in the hills the fugue wakes the Maccabees' blue lights one voice at a time.")
VOICEOVER = ('Long ago a foreign king ruled Judea, and set up idols in the Temple in Jerusalem. In the hills, one '
             'family of priests would not bow.')

EX = excerpt(__file__)              # Grave bars 1-4, 18, 19, 21 (here 1-7); Allegro bars 1-29.5 (here 8-36.5)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 3.0                          # the last chord held
D = round(END + HOLD, 2)
T_ALLEGRO = BAR[8]
T_CHORD = BAR[7]                    # the Grave's last chord
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Vn1', 'Vn2', 'Va', 'Bassi')}
ONSET = {p: np.array([n[0] for n in ns]) for p, ns in PART.items()}
ENTRY = {p: float(ONSET[p][ONSET[p] >= T_ALLEGRO - 0.01][0]) for p in PART}   # each voice's entry in the fugue

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
GLINT = hexc('#c08a40')
STONE = hexc('#6a6a6a')             # the idols
BLUE = hexc('#1e5bd8')              # the Maccabees and the people
WHITE = hexc('#f2f6ff')
HIDDEN = (0.18, 0.33, 0.47, 0.75, 0.88)     # the blue lights in the hills, as fractions of Left
VOICE_OF = {0: 'Vn1', 1: 'Vn1', 2: 'Vn2', 3: 'Va', 4: 'Va'}


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def last(p, t):
    """Seconds since part p's latest onset at or before t (a large number if none)."""
    i = int(np.searchsorted(ONSET[p], t, side='right')) - 1
    return t - ONSET[p][i] if i >= 0 else 99.0


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, 2)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    runL, runR = seg == 'Porch Left', seg == 'Porch Right'
    porch = runL | runR
    front = seg == 'Porch Front'
    left = seg == 'Left'
    right = seg == 'Right'
    wings = np.isin(seg, ['Left', 'Right', 'Side'])
    enemy = np.isin(seg, ['Right', 'Side'])
    up_right = np.where(right, (r1 - d) / (r1 - r0), -1.0)       # 0 at the road from Antioch, 1 at the porch
    # the people: small lights along both porch runs, blue and white in turn (as JM02 has them)
    blue_p, white_p = np.zeros(G.N), np.zeros(G.N)
    for a, b in ((pl0, pl1), (pr0, pr1)):
        for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
            g = np.exp(-((d - c) / 4.0) ** 2)
            if k % 2:
                white_p += g
            else:
                blue_p += g
    blue_p, white_p = np.minimum(blue_p, 1) * porch, np.minimum(white_p, 1) * porch
    # the idols: four grey blocks on Porch Front
    idols = np.zeros(G.N)
    for k in range(4):
        c = pf0 + (0.14 + 0.24 * k) * (pf1 - pf0)
        idols += smoothstep(14, 9, np.abs(d - c))
    idols = np.minimum(idols, 1) * front
    hid = [np.exp(-((d - (l0 + f * (l1 - l0))) / 3.5) ** 2) * left for f in HIDDEN]
    matt_c = l0 + 0.62 * (l1 - l0)
    matt = np.exp(-((d - matt_c) / 4.0) ** 2) * left
    flick = Flicker(rng, G.N, 0.6, 2.2)
    slow = Flicker(rng, G.N, 0.1, 0.4)
    glints = rng.uniform(0.05, 0.95, 400)
    grave_bass = ONSET['Bassi'][ONSET['Bassi'] < T_ALLEGRO]
    downbeats = [BAR[m] for m in range(1, 8)]
    for f in range(F):
        t = f * DT
        settle = smoothstep(END - 0.5, END + 1.5, t)                 # into JM02's opening
        # the purple: heavy over the wings, faint on the porch; in the fugue it pulses with the basses
        heavy = 0.3 + 0.06 * smoothstep(0, END, t)
        if t >= ENTRY['Bassi'] - 0.05:
            heavy_e = 0.22 * np.exp(-last('Bassi', t) / 0.22) * (1 - settle)
        else:
            heavy_e = 0.0
        fr = light(PURPLE, heavy * wings * (0.9 + 0.1 * slow(t)) + heavy_e * enemy + 0.14 * porch)
        fr += light(GLINT, 0.18 * wings * np.maximum(flick(t * 0.5), 0) ** 4)
        # the Grave: every bass step sends a wave of heavier purple up Right from the road from Antioch
        if t < T_ALLEGRO + 2.0:
            wave = np.zeros(G.N)
            for tb in grave_bass[(grave_bass <= t) & (grave_bass > t - 2.2)]:
                a = t - tb
                front_pos = a / 1.6
                wave += np.exp(-((up_right - front_pos) / 0.13) ** 2) * np.exp(-a / 1.4)
            fr += light(PURPLE, 1.0 * np.minimum(wave, 1.2) * right)
            # quick upbeats glint on the helmets
            if last('Vn1', t) < 0.25 and t < T_ALLEGRO:
                i = int(np.searchsorted(ONSET['Vn1'], t, side='right')) - 1
                g = glints[i % len(glints)]
                c = r0 + g * (r1 - r0)
                fr += light(GLINT, 0.8 * np.exp(-last('Vn1', t) / 0.08) * np.exp(-((d - c) / 5.0) ** 2) * right)
        # the Temple: grey idols over a dim glow; each Grave bar lands on them
        stone = 0.5
        for tb in downbeats:
            if 0 <= t - tb < 1.2:
                stone += 0.25 * np.exp(-(t - tb) / 0.35)
        fr += light(STONE, stone * idols) + glow.frame(t, 0.3 + 0.25 * smoothstep(T_ALLEGRO, END, t))
        # the hills: hidden blue, each light woken by its voice in the fugue and flickering with its notes
        for k, h in enumerate(hid):
            p = VOICE_OF[k]
            lv = 0.12 + 0.08 * smoothstep(T_CHORD, T_ALLEGRO, t)
            if t >= ENTRY[p] - 0.05:
                lv = 0.38 + 0.5 * np.exp(-last(p, t) / 0.12) * (1 - settle)
            lv = lv * (1 - settle) + 0.5 * settle
            fr += light(BLUE, lv * h * (0.85 + 0.15 * slow(t)))
            if t >= ENTRY[p] - 0.05:                                 # a halo on each note, gone by the end
                c = l0 + HIDDEN[k] * (l1 - l0)
                halo = 0.45 * (0.4 + np.exp(-last(p, t) / 0.15)) * smoothstep(ENTRY[p], ENTRY[p] + 0.3, t)
                fr += light(BLUE, halo * (1 - settle) * np.exp(-((d - c) / 11.0) ** 2) * left)
        # the people on the porch wake with the second violins
        woke = smoothstep(ENTRY['Vn2'] - 0.5, ENTRY['Vn2'] + 6.0, t)
        lev = 0.15 + 0.65 * woke
        lift = 0.35 * np.exp(-last('Vn2', t) / 0.15) * woke * (1 - settle)
        lev = lev * (0.88 + 0.12 * flick(t))
        fr += light(BLUE, (lev + lift) * blue_p) + light(WHITE, (0.7 * lev + lift) * white_p)
        # the cadence: Mattathias appears among the blue on Left
        m = smoothstep(END - 1.0, END + 1.5, t)
        fr += light(WHITE, m * matt) + light(WHITE, 0.4 * m * np.exp(-((d - matt_c) / 18) ** 2) * left)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The strings as Handel scored them, first violins left to basses right, oboes doubling the first violins in the
    Grave; a harpsichord continuo with the basses; a soft drum under each of the Grave's bars for the march; the last
    chord held."""
    o = Orchestra(M, level=3.4)
    pan = {'Vn1': -0.5, 'Vn2': -0.15, 'Va': 0.2, 'Bassi': 0.45}
    for p, ns in PART.items():
        for t, dd, m, v, h, _ in ns:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd     # notes sounding at the cut hold the chord
            grave = t < T_ALLEGRO - 0.01
            short = dd < 0.2
            vel = v - (4 if short else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), vel, pan[p], 0.5)
                if grave:
                    o.play('oboes', m, t, max(dd, 0.12), vel - 10, pan[p], 0.22)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), vel - 2, pan[p], 0.45)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel, pan[p], 0.5)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 8, pan[p], 0.35)
                if grave:
                    o.play('bassoons', m + 12 if m < 41 else m, t, max(dd, 0.15), vel - 14, pan[p], 0.2)
    # the continuo: the bass line, and in the Grave the chord on each beat from the parts sounding then
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(96, v)), min(dd, 0.35)) for t, dd, m, v, h, _ in PART['Bassi']]
    beat = 60.0 / 60
    upper = PART['Vn2'] + PART['Va']
    tb = 0.0
    while tb < T_ALLEGRO - 0.1:
        ch = sorted({n[2] for n in upper if n[0] <= tb + 0.02 < n[0] + n[1]})
        notes += [(tb, m, 62, 0.4) for m in ch if 52 <= m <= 76]
        tb += beat
    notes += [(END + 0.05 + 0.06 * i, m, 64, HOLD - 0.3) for i, m in enumerate((53, 57, 60, 65))]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.5, 0.0)
    # the march: a soft drum on each of the Grave's bars
    for m in range(1, 8):
        o.hit('timpani', BAR[m], 58, pitch=-5, gain=0.1, pan=0.45)
