"""Ev'ry Valley: the roofline as a landscape, and the tenor's air levels it, valleys lifted and hills made low.

The house is a country of hills and valleys. Brightness along the roofline rises and falls: white-gold hills on Side,
Left and Right, dark twilight valleys between them, and the porch, which really is set back from the wings, the
deepest valley of all. Through the strings' opening bars the hills shimmer with the violins' figures.

The tenor's warm white voice enters in the porch valley, "Ev'ry valley". On the long run of "exalted" the voice
travels the valley floor from Porch Left round to Porch Right, and the floor rises behind it, note by note: the
porch is the first valley to lift. When the strings answer forte, the valleys on the wings rise too, and by the end
of "exalted" every valley is up. "And ev'ry mountain and hill": the hills flare once, then sink through "made low"
to the level of the valleys. "The crooked": the land zig-zags, its kinks flipping with each crooked note, and on
"straight" the zig-zag pulls out flat. "And the rough places plain": the whole house glitters, rough, and the
glitter dies away through the long held "plain", leaving one level light.

Then the air's Adagio close. "The crooked straight": the strings' two hammered chords kink the land a last time, and
the fermata straightens it. "And the rough places plain", slow and free: the whole house brightens evenly, one level
white-gold from end to end, and the closing ritornello's cadence settles it, even and still.

The music is Handel's own: Messiah No. 3, the ritornello's opening, the tenor's first statement to the first
"exalted" (the second long run left out), "and ev'ry mountain" to the first long "plain", and the Adagio close with
the last bars of the closing ritornello, transcribed from Prout's full score (Novello, 1902) into every_valley.musicxml
and timed by scripts/score_excerpt.py, the Andante a little quicker than Prout's mark. Strings only, as Handel scored
it; the tenor's line on violins and an oboe.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, keys, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS03'
TITLE = "Ev'ry Valley"
KIND = 'show'
DESCRIPTION = ("The roofline as a landscape of bright hills and dark valleys. The tenor sings, and the porch valley "
               "rises behind his voice, the hills sink, the crooked land straightens, until the house is one level "
               "light.")
VOICEOVER = "Ev'ry valley shall be exalted, and ev'ry mountain and hill made low."

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.0                                  # the last chord rings
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Tenor', 'Vn1', 'Vn2', 'Va', 'Bassi')}
TEN = PART['Tenor']
T_ON = np.array([n[0] for n in TEN])
V1_ON = np.array([n[0] for n in PART['Vn1']])
SEG = EX['segments']
T_MELISMA0, T_MELISMA1 = BAR[14] + 0.5 * (BAR[15] - BAR[14]), BAR[19]       # "exalt-----ed"
T_WINGS = BAR[19]                           # the strings' forte answer: the wings' valleys rise
T_MOUNTAIN = SEG[2]['start'] + 0.5 * (BAR[25] - SEG[2]['start'])            # "and ev'ry moun-tain"
T_LOW = BAR[26]                             # "low"
T_CROOK = BAR[27] + 0.5 * (BAR[28] - BAR[27])                               # "the crook-ed"
T_STRAIGHT = BAR[28]
T_ROUGH = BAR[29]
T_PLAIN = BAR[30]
T_SPLICE = SEG[3]['start']                  # the Adagio close
T_CHORDS = BAR[73]                          # "crook-ed straight," the hammered chords and the fermata
T_ADAGIO = BAR[74]
T_LAST = BAR[76]                            # "plain." and the ritornello
T_CODA = SEG[4]['start']

WARM = hexc('#fff0d8')                      # the tenor
WHITEGOLD = hexc('#fff2c8')
GOLD = hexc('#ff9a18')
DUSK = hexc('#1a2a5c')                      # the valleys' twilight


def notes_between(t0, t1):
    return [n for n in TEN if t0 - 0.01 <= n[0] < t1 - 0.01]


def staircase(t, onsets, t1):
    """0..1: the share of onsets passed by t, each step eased, reaching 1 at t1."""
    if t <= onsets[0]:
        return 0.0
    if t >= t1:
        return 1.0
    k = np.searchsorted(onsets, t, side='right')
    a = smoothstep(0.0, 0.25, t - onsets[k - 1])
    return min(1.0, (k - 1 + a) / len(onsets))


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    pl = G.pd[G.seg['Porch Left']]
    pr = G.pd[G.seg['Porch Right']]
    p0, p1 = float(pl.min()), float(pr.max())
    # the land: hills on the wings, a broad valley in the porch; terrain -1 (valley floor) .. +1 (hilltop)
    hills = ((120, 95), (370, 95), (600, 85), (800, 70), (2120, 85), (2300, 80), (2470, 75))
    terr = -0.6 + sum(1.6 * np.exp(-((d - c) / w) ** 2) for c, w in hills)
    terr = np.where(porch, -1.0 + 0.12 * np.cos(2 * np.pi * (d - p0) / (p1 - p0)), terr)
    terr = np.clip(terr, -1, 1)
    hill = np.clip(terr, 0, 1)
    vale = np.clip(-terr, 0, 1)
    crest = smoothstep(0.75, 1.0, terr)
    zig = np.sign(np.sin(2 * np.pi * d / 70.0)) * (1 - np.abs(np.sin(2 * np.pi * d / 70.0)) ** 6)
    rough = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.3, 1.0)
    mel = np.array([n[0] for n in notes_between(T_MELISMA0, T_MELISMA1 + 0.3)])
    crook = np.array([n[0] for n in notes_between(T_CROOK - 0.6, T_STRAIGHT)])
    u_porch = np.clip((d - p0) / (p1 - p0), 0, 1)
    for f in range(F):
        t = f * DT
        # how the land is shaped now
        sweep = staircase(t, mel, T_MELISMA1)                       # the voice's run along the porch valley
        lift_p = np.clip(0.15 * smoothstep(BAR[13], BAR[14], t) + 0.85 * smoothstep(-0.06, 0.0, sweep - u_porch)
                         * smoothstep(T_MELISMA0, T_MELISMA0 + 0.3, t), 0, 1)
        lift_w = smoothstep(T_WINGS, BAR[20], t) * 0.7 + smoothstep(BAR[20], BAR[20] + 2.0, t) * 0.3
        lift = np.where(porch, lift_p, lift_w)
        flare = 0.35 * np.exp(-max(0.0, t - T_MOUNTAIN) / 1.2) * smoothstep(T_MOUNTAIN - 0.3, T_MOUNTAIN, t)
        hs = 1.0 - 0.85 * smoothstep(T_MOUNTAIN + 0.8, T_LOW + 0.6, t)            # hills made low
        floor = 0.03 + 0.5 * lift                                   # a valley floor, lifted toward the hills' foot
        top = 0.5 + 0.35 * hs + flare                                # a hilltop, made low to the lifted floor
        h = np.maximum(floor, 0.03 + hill ** 0.8 * (top - 0.03))
        # the crooked: a zig-zag whose kinks flip with each crooked note, pulled straight on "straight"
        j = 0.0
        if T_CROOK - 0.6 <= t < T_STRAIGHT + 1.2:
            k = int(np.searchsorted(crook, t, side='right'))
            j = 0.28 * (1 - smoothstep(T_STRAIGHT, T_STRAIGHT + 1.0, t)) * smoothstep(T_CROOK - 0.6, T_CROOK - 0.3, t)
            h = h + j * zig * (1 if k % 2 else -1)
        if T_CHORDS - 0.1 <= t < T_ADAGIO:                                         # the hammered chords
            a1, a2 = t - T_CHORDS, t - (T_CHORDS + (T_ADAGIO - T_CHORDS) * 0.4)
            kink = 0.3 * np.exp(-max(a1, 0) / 0.5) * (a1 >= 0) - 0.3 * np.exp(-max(a2, 0) / 0.5) * (a2 >= 0)
            h = h + kink * zig * (1 - smoothstep(T_ADAGIO - 1.0, T_ADAGIO, t))
        # the rough places: glitter that dies through the held "plain"; gone for good in the Adagio
        r = 0.32 * smoothstep(T_ROUGH - 0.4, T_ROUGH, t) * (1 - 0.75 * smoothstep(T_PLAIN, BAR[33], t))
        r *= 1 - smoothstep(T_ADAGIO, T_ADAGIO + 4.0, t)
        h = h + r * rough(t) * (t >= T_ROUGH - 0.4)
        # the plain: one level light, brightening evenly in the Adagio and settling on the cadence
        even = 0.46 + 0.22 * smoothstep(T_ADAGIO, T_LAST, t)
        flat = smoothstep(T_PLAIN, BAR[33], t) * 0.85 + 0.15 * smoothstep(T_SPLICE, T_ADAGIO, t)
        h = (1 - flat) * h + flat * even
        h = np.clip(h, 0.0, 1.1)
        # the strings: the violins' figures glint on the hilltops, while there are hills
        i = int(np.searchsorted(V1_ON, t, side='right')) - 1
        glint = 0.0
        if i >= 0:
            glint = 0.22 * np.exp(-(t - V1_ON[i]) / 0.12) * hs * (1 - flat)
        tone = np.clip((h - 0.03) / 0.85, 0, 1)[:, None]
        lo, hi = np.clip(tone * 2, 0, 1), np.clip(tone * 2 - 1, 0, 1)
        col = np.where(tone < 0.5, (1 - lo) * DUSK + lo * GOLD, (1 - hi) * GOLD + hi * WHITEGOLD)
        lvl = 0.04 + 0.62 * h * (0.93 + 0.07 * shimmer(t))
        fr = light(col, lvl) + light(WHITEGOLD, glint * crest)
        # the tenor: a warm white light in the porch valley, travelling its floor on the long "exalted"
        j = int(np.searchsorted(T_ON, t, side='right')) - 1
        if j >= 0:
            n = TEN[j]
            a = t - n[0]
            on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.35)
            if on > 0.01:
                if T_MELISMA0 - 0.05 <= t < T_MELISMA1 + 0.4:
                    c = p0 + sweep * (p1 - p0)
                    w = 26.0
                elif t >= T_SPLICE:
                    c, w = 0.5 * (p0 + p1), 140.0 + 300 * smoothstep(T_ADAGIO, T_LAST, t)
                else:
                    c, w = 0.5 * (p0 + p1), 60.0 + 20 * (n[2] - 52) / 12
                g = np.exp(-((d - c) / w) ** 2)
                fr += light(WARM, (0.25 + 0.45 * smoothstep(0, 0.08, a)) * on * g * (1 - 0.5 * flat))
        if t > END:                                                    # the last chord rings, then rests
            fr = fr * (1 - 0.25 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The strings as Handel scored them, first violins left to basses right, a harpsichord continuo; the tenor on
    violins with an oboe, from the porch."""
    o = Orchestra(M, level=3.6)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (4 if dd < 0.2 else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), vel - 4, pan[p], 0.45)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), vel - 6, pan[p], 0.4)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel - 4, pan[p], 0.45)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel - 2, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 10, pan[p], 0.32)
    for t, dd, m, v, h, _ in TEN:                                       # the tenor's line, from the porch
        o.play('violins', m + 12, t, max(dd, 0.14), v + 8, 0.0, 0.62)
        o.play('oboes', m + 12, t, max(dd, 0.14), v - 6, 0.0, 0.3)
        if dd >= 0.6:
            o.play('violas', m, t, dd, v - 10, 0.0, 0.25)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(96, v - 6)), min(dd, 0.35)) for t, dd, m, v, h, _ in PART['Bassi']]
    tb = T_ADAGIO
    while tb < T_LAST - 0.1:                                             # the Adagio's chords under the tenor
        notes += [(tb, m, 60, 1.2) for m in (61, 64, 69)] if tb < BAR[75] else [(tb, m, 60, 1.2) for m in (63, 66, 71)]
        tb += 60 / 46 * 2
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.45, 0.0)
