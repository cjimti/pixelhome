"""O Father, Whose Almighty Power: the people pray for a leader, and Simon names Judas.

The scene opens where the mourning (JM02) ended: Seleucid purple over the wings, the people dim on the porch runs, the
Temple grey with its idols, and a few blue lights hidden on Left, in the hills of Modein. The chorus prays, Larghetto:
with every chord of "O Father, whose almighty pow'r" the hidden blue lights on Left draw together and steady, and the
people on the porch runs lift with the voices. "The heav'ns and earth and seas adore!": each of the three words sends
a wave of white along the porch and the wings, and the purple gives way on Left. "And grant a leader bold and brave"
(Allegro): the basses alone, and the blue on Left pulses on every beat, a little brighter with each step of the line.

Then Simon, in deep blue, among the blue on Left: "I feel the Deity within". His light swells with each phrase. On "And
points out Maccabaeus" a point of brass gold kindles in the middle of the blue, and on "Judas" it bursts into a
single gold light, the first of the set; on "And lead us on to victory!" the orchestra strikes up and the gold flares,
the blue around it standing bright and steady. The last frame: the gold among the blue on Left, the purple held back
on Right and Side.

The music is Handel's own: No. 8 from the chorus's entry ("O Father") to "and seas adore!", the first bars of its
Allegro ("And grant a leader bold and brave, if not to conquer, born to save"), and the end of No. 9, Simon's
accompanied recitative, from "To Israel's distressful pray'r" to "victory!", transcribed from the Novello vocal score
into o_father.musicxml and timed by scripts/score_excerpt.py at the marked tempos. The chorus plays on strings with
oboes and bassoons doubling, the Allegro's bass line on cellos, bassoons and basses, Simon on bassoons and cellos,
his held chords on strings; a harpsichord plays the continuo.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, keys, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM03'
TITLE = 'O Father, Whose Almighty Power'
KIND = 'show'
DESCRIPTION = ("The people pray for a leader. The blue lights gather on Left and steady; Simon's deep blue names "
               "Judas, and a single brass-gold light appears among them.")
VOICEOVER = 'Who will lead them now? The people pray, and Simon names his brother: Judas, called the Maccabee.'

EX = excerpt(__file__)              # No. 8 bars 1-12 (compact), its Allegro 13-16, No. 9's end 17-25
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 1.5, 2)
VOICES = ('S', 'A', 'T', 'B')
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
SIMON = [n for n in EX['notes'] if n[5] == 'Simon']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']

T_HEAVENS = BAR[7]                  # "The heav'ns and earth"
ADORE = [BAR[7], BAR[8], BAR[11]]   # heav'ns, earth, seas
T_ALLEGRO = BAR[13]                 # "And grant a leader bold and brave"
T_RECIT = BAR[18] - 2.5             # Simon: "To Israel's distressful pray'r"
T_MACC = BAR[20] + 0.75 * (BAR[21] - BAR[20])          # "Maccabaeus"
T_JUDAS = BAR[22]                   # "Judas"
T_VICTORY = BAR[24] + 0.5 * (BAR[25] - BAR[24])        # the orchestra's forte
T_LAST = BAR[25]                    # the last chord
BEATS = np.array([t for t, d, m, v, h, w in SUNG if w == 'B' and T_ALLEGRO - 0.01 <= t < T_RECIT])
CHORDS = np.array(sorted({round(n[0], 3) for n in SUNG if n[0] < T_ALLEGRO}))
SIMON_ON = np.array(sorted(n[0] for n in SIMON))

PURPLE = hexc('#6a2ca0')
GLINT = hexc('#c08a40')
STONE = hexc('#6a6a6a')
BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')
SIMON_C = hexc('#2850c8')           # Simon
GOLD = hexc('#ffc83c')              # Judas


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    left = seg == 'Left'
    runL, runR = seg == 'Porch Left', seg == 'Porch Right'
    porch = runL | runR
    front = seg == 'Porch Front'
    right_side = np.isin(seg, ['Right', 'Side'])
    tow = np.zeros(G.N)                                     # 0 at the street end of a porch run, 1 at the Temple
    tow[runL] = (d[runL] - pl0) / (pl1 - pl0)
    tow[runR] = (pr1 - d[runR]) / (pr1 - pr0)
    blue_p, white_p = np.zeros(G.N), np.zeros(G.N)          # the people, as JM02 left them
    for a, b in ((pl0, pl1), (pr0, pr1)):
        for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
            g = np.exp(-((d - c) / 4.0) ** 2)
            if k % 2:
                white_p += g
            else:
                blue_p += g
    blue_p, white_p = np.minimum(blue_p, 1) * porch, np.minimum(white_p, 1) * porch
    idols = np.zeros(G.N)
    for k in range(4):
        c = pf0 + (0.14 + 0.24 * k) * (pf1 - pf0)
        idols += smoothstep(14, 9, np.abs(d - c))
    idols = np.minimum(idols, 1) * front
    # the hidden blue on Left: scattered as JM02 left them, drawn together round the middle of Left by the prayer
    start = l0 + np.array([0.18, 0.33, 0.47, 0.75, 0.88]) * (l1 - l0)
    mid = l0 + 0.55 * (l1 - l0)
    gather = l0 + np.array([0.31, 0.42, 0.5, 0.68, 0.79]) * (l1 - l0)
    flick = Flicker(rng, G.N, 0.6, 2.2)
    slow = Flicker(rng, G.N, 0.1, 0.4)
    for f in range(F):
        t = f * DT
        g = smoothstep(0.0, T_ALLEGRO, t)                       # how far the blue has gathered
        clear = smoothstep(T_HEAVENS, T_RECIT, t)               # how far the purple has left Left
        purple = 0.42 * right_side + 0.42 * (1 - 0.7 * clear) * left
        fr = light(PURPLE, purple * (0.9 + 0.1 * slow(t)) + 0.14 * porch)
        fr += light(BLUE, 0.16 * clear * left * (0.9 + 0.1 * slow(t)))
        fr += light(GLINT, 0.18 * right_side * np.maximum(flick(t * 0.5), 0) ** 4)
        fr += light(STONE, 0.5 * idols) + glow.frame(t, 0.55)
        # the prayer's chords: each lifts the people and the gathering blue
        i = int(np.searchsorted(CHORDS, t, side='right')) - 1
        chord = np.exp(-(t - CHORDS[i]) / 0.9) if i >= 0 else 0.0
        # the Allegro's beats
        j = int(np.searchsorted(BEATS, t, side='right')) - 1
        beat = np.exp(-(t - BEATS[j]) / 0.25) if j >= 0 and t < T_RECIT else 0.0
        step = smoothstep(T_ALLEGRO, T_RECIT, t)
        pos = start + (gather - start) * g
        blue_l = np.zeros(G.N)
        for c in pos:
            blue_l += np.exp(-((d - c) / (3.5 + 2.5 * g)) ** 2)
        blue_l = np.minimum(blue_l, 1) * left
        lvl = 0.5 + 0.35 * g + 0.25 * chord * (t < T_ALLEGRO) + 0.4 * beat + 0.2 * step + 0.25 * smoothstep(T_VICTORY - 0.3, T_VICTORY + 0.5, t)
        fr += light(BLUE, lvl * blue_l * (0.9 + 0.1 * flick(t)))
        fr += light(BLUE, (0.12 + 0.1 * g + 0.12 * beat) * np.exp(-((d - mid) / 50) ** 2) * left)
        # the people on the porch, lifting with the prayer
        lev = 0.34 + 0.22 * smoothstep(0, T_HEAVENS, t) + 0.15 * chord * (t < T_ALLEGRO) + 0.1 * smoothstep(T_JUDAS, T_JUDAS + 3, t)
        lev *= 0.88 + 0.12 * flick(t)
        fr += light(BLUE, lev * blue_p) + light(WHITE, 0.8 * lev * white_p)
        # "the heav'ns and earth and seas adore!": a white wave along the porch runs and out over the wings
        for k, ta in enumerate(ADORE):
            a = t - ta
            if 0 <= a < 3.0:
                p = smoothstep(0, 2.4, a)
                fade = 1 - smoothstep(1.8, 3.0, a)
                fr += light(WHITE, 0.7 * fade * np.exp(-((tow - p) / 0.15) ** 2) * porch)
                fr += light(WHITE, 0.35 * fade * np.exp(-a / 0.6) * front)
        # Simon: deep blue at the middle of the gathered blue, swelling with each phrase
        if t >= T_RECIT - 1.0:
            k = int(np.searchsorted(SIMON_ON, t, side='right')) - 1
            word = np.exp(-(t - SIMON_ON[k]) / 0.35) if k >= 0 else 0.0
            sim = smoothstep(T_RECIT - 1.0, T_RECIT + 0.5, t) * (0.75 + 0.35 * word)
            sc = mid - 0.12 * (l1 - l0)
            fr += light(SIMON_C, sim * (1.3 * np.exp(-((d - sc) / 7) ** 2) + 0.5 * np.exp(-((d - sc) / 24) ** 2)) * left)
            fr += light(WHITE, 0.35 * sim * word * np.exp(-((d - sc) / 2.5) ** 2) * left)
        # Judas: a point of gold kindled on "Maccabaeus", bursting into his light on "Judas", flaring on "victory"
        if t >= T_MACC:
            jc = mid + 0.04 * (l1 - l0)
            k = smoothstep(T_MACC, T_JUDAS, t)
            burst = np.exp(-(t - T_JUDAS) / 0.6) * (t >= T_JUDAS)
            flare = np.exp(-(t - T_VICTORY) / 0.8) * (t >= T_VICTORY) + 0.6 * np.exp(-(t - T_LAST) / 0.7) * (t >= T_LAST)
            full = smoothstep(T_JUDAS, T_JUDAS + 0.4, t)
            core = 0.25 * k + 0.6 * full + 0.5 * burst + 0.4 * flare
            fr += light(GOLD, 1.4 * core * np.exp(-((d - jc) / (4 + 5 * full)) ** 2) * left)
            fr += light(GOLD, (0.45 * burst + 0.35 * flare + 0.18 * full) * np.exp(-((d - jc) / 34) ** 2) * left)
            fr += light(WHITE, (0.6 * burst + 0.4 * flare) * np.exp(-((d - jc) / 2.5) ** 2) * left)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings with oboes and bassoons doubling, sopranos and altos left, tenors and basses right; the
    Allegro's basses on cellos, bassoons and basses; Simon on bassoons and cellos from Left, his chords on strings;
    a harpsichord continuo; trumpets and drums only for "victory"."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pl, pr = pan_at(sum(span(G, 'Porch Left')) / 2), pan_at(sum(span(G, 'Porch Right')) / 2)
    l0, l1 = span(G, 'Left')
    pleft = pan_at(l0 + 0.55 * (l1 - l0))
    o = Orchestra(M, level=3.8)
    parts = {'S': [('violins', 0, 0, 0.5), ('oboes', 0, -10, 0.25)],
             'A': [('violins', 0, -4, 0.35), ('violas', 0, -2, 0.35)],
             'T': [('violas', 0, -2, 0.45), ('bassoons', 0, -10, 0.22)],
             'B': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.28)]}
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, dd, m, v, h, who in SUNG:
        allegro = t >= T_ALLEGRO - 0.01
        for section, tr, dv, gg in parts[who]:
            o.play(section, m + tr, t, dd * (0.9 if allegro else 1.02), v + dv, (0.3 if allegro else 0.6) * side[who], gg)
        if who == 'B':
            o.play('basses', m + 12 if m < 36 else m, t, dd, v - 10, 0.0, 0.32)
    for t, dd, m, v, h, who in SIMON:
        o.play('bassoons', m, t, max(dd, 0.25), v - 2, pleft, 0.55)
        o.play('cellos', m, t, max(dd, 0.25), v - 6, pleft, 0.4)
    for t, dd, m, v, h, who in ORCH:
        if t < T_RECIT - 0.5:                       # the Allegro's octaves: the bass line doubled
            if h == 1:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.25), v - 4, 0.0, 0.35)
            continue
        if dd >= 1.0:                                # the recitative's held chords
            sec = 'violins' if m >= 64 else 'violas' if m >= 52 else 'cellos' if m >= 40 else 'basses'
            o.play(sec, m + (12 if sec == 'basses' and m < 36 else 0), t, dd, v - 14, None, 0.3)
        else:                                        # the struck chords: strings short, and the forte with trumpets
            sec = 'violins' if m >= 64 else 'violas' if m >= 52 else 'cellos'
            o.play(sec, m if m >= 36 else m + 12, t, max(dd, 0.2), v - 4, None, 0.4)
            if t >= T_VICTORY - 0.05 and m >= 60:
                o.play('trumpets', m, t, max(dd, 0.2), v - 6, 0.0, 0.3)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, 70, min(dd, 0.3)) for t, dd, m, v, h, who in SUNG if who == 'B' and t < T_ALLEGRO]
    notes += [(t, m, int(min(100, v)), min(dd, 0.3)) for t, dd, m, v, h, who in ORCH]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.5, 0.0)
    o.hit('timpani', T_JUDAS, 70, pitch=0, gain=0.15, pan=pleft)
    o.hit('timpani roll', T_VICTORY - 0.6, 74, pitch=0, gain=0.15)
    o.hit('timpani', T_LAST, 100, pitch=0, gain=0.3)
