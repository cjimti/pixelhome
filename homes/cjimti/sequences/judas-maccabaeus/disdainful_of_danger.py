"""Disdainful of Danger: the Maccabees go out to fight, rank after rank off Left, round the corner and down Porch Left.

The scene opens where Call Forth Thy Powers (JM05) ended, and over the first seconds the rank on Left becomes the
army drawn up in the hills (CARRY, from JM05's last frame: change both together): ranks of small blue and white lights along Left, Judas's brass gold
in the middle of them, Seleucid purple on Right and Side, the Temple grey with its idols over the glow of the lights.
The ritornello is the march's call: every sixteenth of the first violins lifts the white ranks, every note of the
second violins the blue, and the scales that climb at its end run up the ranks toward the corner.

Then the trio, "Disdainful of danger, we'll rush on the foe", three voices stepping out ahead of the ranks near the
corner of Left, each a small light that flares on its notes, the tenor first, then the bass, then the alto; Judas
walks up through the ranks to the front of them. "That thy pow'r, O Jehovah, all nations may know": on each "-ho-"
a white call runs from the front of the ranks down Porch Left to the Temple.

Then the chorus takes it up, forte, and the army moves: on every bar the whole column steps forward, Judas leading,
round the corner and down Porch Left, the ranks flaring on the chorus's notes, a surge on each "we'll rush on the
foe". By the closing ritornello Left is empty but for a trace of blue, and the ranks fill Porch Left, marching in
place on the beat with Judas at their head by the Temple, facing the purple waiting on Right; on the last chord they
stand. That is where Fall'n Is the Foe (JM07) begins: change both together.

The music is Handel's own: No. 22, "generally sung as a Trio, and repeated in Chorus", as the score says: the opening
ritornello, the trio's first entries to "rush on the foe" and its "That thy pow'r, O Jehovah", then the end of the
number as the chorus repeats it, and the closing ritornello's last eight bars, transcribed from the Novello vocal
score into disdainful_of_danger.musicxml and timed by scripts/score_excerpt.py at a quaver of 144 (the score marks
Allegro). The trio is played on flute, clarinet and bassoon over a harpsichord continuo; the chorus on strings with
oboes and bassoons doubling and horns on the long notes; the ritornellos on the strings with the oboes on the top
line. Marching feet under the chorus, the column's own sound.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM06'
TITLE = 'Disdainful of Danger'
KIND = 'show'
DESCRIPTION = ("The Maccabees go out to fight: three voices step out ahead of the ranks on Left, then the chorus "
               "takes it up and the whole column marches round the corner and down Porch Left, Judas leading.")
VOICEOVER = 'Disdainful of danger, the Maccabees march out of the hills to meet the enemy.'

EX = excerpt(__file__)              # the ritornello 1-13, the trio 13-31, the chorus 32-55, the ritornello's end 56-64
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
D = round(END + 2.0, 2)
BARLEN = BAR[3] - BAR[2]
T_TRIO = BAR[13] + 2 * BARLEN / 3   # the tenor's upbeat
T_POWR = BAR[23]                    # "That thy pow'r"
T_CHORUS = BAR[32]                  # the orchestra's link into the chorus
T_MARCH = BAR[33]
T_STAND = BAR[56]                   # the closing ritornello: the column stands on Porch Left
T_LAST = BAR[64]
NOTES = EX['notes']
SUNG = [n for n in NOTES if n[5] in ('A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
TRIO = {p: np.array(sorted(n[0] for n in SUNG if n[5] == p and n[0] < T_CHORUS - 0.1)) for p in ('A', 'T', 'B')}
CHORUS = np.array(sorted({round(n[0], 3) for n in SUNG if n[0] >= T_CHORUS - 0.1}))
VN1 = np.array(sorted({round(n[0], 3) for n in ORCH if n[4] == 0 and n[0] < T_TRIO}))
VN2 = np.array(sorted({round(n[0], 3) for n in ORCH if n[4] == 1 and n[0] < T_TRIO}))
HOVAH = [BAR[25], BAR[29]]          # the trio's "-ho-vah"
RUSH = [BAR[34] + k * BARLEN / 6 for k in range(6)]     # the chorus's sixteenths: "-dain-ful we'll rush on the"
SCALES = [BAR[8], BAR[9], BAR[10]]  # the ritornello's climbing scales

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
GLINT = hexc('#c08a40')
STONE = hexc('#6a6a6a')             # the idols
BLUE = hexc('#1e5bd8')              # the Maccabees
WHITE = hexc('#f2f6ff')
GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')

STEP = 21.0                         # between ranks, layout units along the path
SHIFT = 412.0                       # how far the column marches: off Left, onto Porch Left
JUDAS0 = 700.0                      # Judas's place in the ranks at the start (path distance, the middle of Left)


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def ranks(G):
    """The ranks' path distances at the start (along Left) and which are white."""
    l0, l1 = span(G, 'Left')
    pos = np.arange(l0 + 14, l1 - 6, STEP)
    return pos, (np.arange(len(pos)) % 2 == 1)


def march(t):
    """How far the column has marched along the path at t: a step on every bar of the chorus, none before or after."""
    if t <= T_MARCH:
        return 0.0
    n = (T_STAND - T_MARCH) / BARLEN
    u = min((t - T_MARCH) / BARLEN, n)
    k = np.floor(u)
    return SHIFT * (k + smoothstep(0.0, 0.5, u - k)) / n


def judas(G, t):
    """Judas's path distance: in the middle of the ranks, up to their head during the trio, then leading the march."""
    l0, l1 = span(G, 'Left')
    head = l1 - 8
    walk = smoothstep(T_TRIO, T_POWR, t)
    return JUDAS0 + (head - JUDAS0) * walk + march(t)


def last(onsets, t):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    return t - onsets[i] if i >= 0 else 1e9


SIMON_C = hexc('#2850c8')           # Simon, in Call Forth Thy Powers' (JM05) last frame
CARRY = 3.0                         # seconds JM05's last frame takes to give way to this scene's ranks
JM05_END = 83.0                     # JM05's length: its Glow is carried on from there (change with JM05)


def jm05_end(G, glow5, t):
    """Call Forth Thy Powers' last frame (JM05's Stage.end): purple on Right and Side, faint on the porch runs with the
    people over it, the idols over the glow, a blue bed on Left with its rank of twelve lights at full, Simon's deep
    blue and Judas's gold among them. Change it with JM05."""
    d, seg = G.pd, G.seg_of
    left = (seg == 'Left').astype(float)
    right = (seg == 'Right').astype(float)
    right_side = np.isin(seg, ['Right', 'Side']).astype(float)
    porch = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    L = l1 - l0
    bp, wp = np.zeros(G.N), np.zeros(G.N)
    for a, b in ((pl0, pl1), (pr0, pr1)):
        for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
            g = np.exp(-((d - c) / 4.0) ** 2)
            if k % 2:
                wp += g
            else:
                bp += g
    bp, wp = np.minimum(bp, 1) * porch, np.minimum(wp, 1) * porch
    idols = np.zeros(G.N)
    for k in range(4):
        idols += smoothstep(14, 9, np.abs(d - (pf0 + (0.14 + 0.24 * k) * (pf1 - pf0))))
    idols = np.minimum(idols, 1) * (seg == 'Porch Front')
    sc, jc = l0 + 0.43 * L, l0 + 0.59 * L
    simon = (1.3 * np.exp(-((d - sc) / 7) ** 2) + 0.5 * np.exp(-((d - sc) / 24) ** 2)) * left
    pos = l0 + np.linspace(0.06, 0.94, 12) * L
    shape = np.exp(-((d[None, :] - pos[:, None]) / 6.0) ** 2) * left
    white = np.arange(12) % 2 == 1
    fr = light(PURPLE, 0.42 * right + 0.42 * (right_side - right) + 0.14 * porch)
    fr += light(BLUE, 0.2 * left)
    fr += light(STONE, 0.5 * idols) + glow5.frame(JM05_END + t, 0.55)
    fr += light(BLUE, 0.66 * bp) + light(WHITE, 0.8 * 0.66 * wp)
    fr += light(SIMON_C, 0.5 * simon)
    fr += light(BLUE, (~white * 1.0) @ shape) + light(WHITE, 0.8 * (white * 1.0) @ shape)
    fr += (light(GOLD, 1.4 * 0.85 * np.exp(-((d - jc) / 9) ** 2) * left)
           + light(GOLD, 0.18 * np.exp(-((d - jc) / 34) ** 2) * left))
    return fr


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    glow5 = Glow(G, 5)
    l0, l1 = span(G, 'Left')
    p0, p1 = span(G, 'Porch Left')
    f0, f1 = span(G, 'Porch Front')
    left = (seg == 'Left').astype(float)
    runL = (seg == 'Porch Left').astype(float)
    runR = (seg == 'Porch Right').astype(float)
    enemy = np.isin(seg, ['Right', 'Side']).astype(float)
    front = (seg == 'Porch Front').astype(float)
    idols = np.zeros(G.N)
    for k in range(4):
        c = f0 + (0.14 + 0.24 * k) * (f1 - f0)
        idols += smoothstep(14, 9, np.abs(d - c))
    idols = np.minimum(idols, 1) * front
    base, white = ranks(G)
    slow = Flicker(rng, G.N, 0.1, 0.4)
    glints = Flicker(rng, G.N, 0.3, 1.2)
    trio_at = {'T': l1 - 30, 'B': l1 - 44, 'A': l1 - 58}        # the three voices, ahead of the ranks near the corner
    for f in range(F):
        t = f * DT
        live = smoothstep(2.5, 4.5, t) * (1 - smoothstep(D - 2.5, D - 0.5, t))   # steady at the start and the end
        fr = np.zeros((G.N, 3))
        # the purple holding Right and Side, the porch runs dim, the Temple grey with idols over the lights' glow
        fr += light(PURPLE, 0.42 * enemy * (1 + 0.1 * live * (slow(t) - 0.5)))
        fr += light(GLINT, 0.18 * live * enemy * np.maximum(glints(t), 0) ** 4)
        fr += light(PURPLE, 0.14 * (runL + runR))
        fr += light(STONE, 0.5 * idols) + glow.frame(t, 0.55)
        # where the ranks are now
        off = march(t)
        pos = base + off
        fade = smoothstep(p1 - 4, p1 - 30, pos)                 # a rank fades as it reaches the back of Porch Left
        lvl = np.full(len(pos), 0.34 + 0.14 * smoothstep(T_CHORUS, T_MARCH, t)) * fade
        # the ritornello: the first violins lift the white ranks, the second the blue; the scales run up the ranks
        if t < T_TRIO + 0.5:
            a1, a2 = last(VN1, t), last(VN2, t)
            lvl = lvl + live * np.where(white, 0.6 * np.exp(-a1 / 0.12), 0.6 * np.exp(-a2 / 0.12))
            for ts in SCALES:
                a = t - ts
                if 0 <= a < BARLEN:
                    run = l0 + (l1 - l0) * a / BARLEN
                    lvl = lvl + 0.45 * np.exp(-((pos - run) / 40.0) ** 2)
        # the trio: the ranks in place, a pulse on each bar; the chorus: a flare on its notes, a surge on "rush"
        elif t < T_CHORUS:
            ph = ((t - BAR[13]) / BARLEN) % 1.0
            lvl = lvl + 0.12 * np.exp(-ph / 0.2)
            a = min(last(TRIO[p], t) for p in TRIO)
            lvl = lvl + 0.14 * np.exp(-a / 0.25)
        else:
            a = last(CHORUS, t)
            lvl = lvl + 0.3 * np.exp(-a / 0.18)
            for k, tr in enumerate(RUSH):
                a = t - tr
                if 0 <= a < 0.4:
                    lvl = lvl + 0.35 * np.exp(-a / 0.12) * (white if k % 2 else ~white)
            if t >= T_STAND:                                    # standing on Porch Left, stepping in place
                ph = ((t - T_STAND) / BARLEN) % 1.0
                lvl = lvl + 0.15 * live * np.exp(-ph / 0.25)
            if t >= T_LAST:
                lvl = lvl + 0.35 * np.exp(-(t - T_LAST) / 0.5)
        shape = np.exp(-((d[None, :] - pos[:, None]) / 4.0) ** 2)
        fr += light(WHITE, (lvl * white) @ shape)
        fr += light(BLUE, 1.25 * (lvl * ~white) @ shape)
        # the trace the column leaves on Left
        gone = smoothstep(T_MARCH, T_STAND, t)
        fr += light(BLUE, 0.12 * gone * left)
        # the trio's three voices, ahead of the ranks, each flaring on its notes
        if T_TRIO - 0.3 <= t < T_CHORUS + 1.0:
            out_ = smoothstep(T_TRIO - 0.3, T_TRIO + 0.3, t) * (1 - smoothstep(T_CHORUS, T_CHORUS + 1.0, t))
            for p, c in trio_at.items():
                a = last(TRIO[p], t)
                v = 0.45 + 0.8 * np.exp(-a / 0.22) if a < 1e8 else 0.3
                fr += light(WHITE if p != 'B' else BLUE, out_ * v * np.exp(-((d - c) / 4.5) ** 2))
        # "-ho-vah": a white call from the head of the ranks down Porch Left to the Temple
        for th in HOVAH:
            a = t - th
            if 0 <= a < 2.0:
                x = l1 + (p1 + 20 - l1) * smoothstep(0, 1.6, a)
                fr += light(WHITE, 0.55 * (1 - smoothstep(1.4, 2.0, a)) * np.exp(-((d - x) / 18.0) ** 2) * (runL + left))
                fr += light(WHITE, 0.25 * np.exp(-a / 0.5) * front * smoothstep(1.0, 1.4, a))
        # Judas: brass gold among the ranks, then at their head
        j = judas(G, t)
        flare = 0.5 * np.exp(-(t - T_LAST) / 0.6) if t >= T_LAST else 0.0
        fr += light(GOLD, (0.95 + flare) * np.exp(-((d - j) / 6.0) ** 2))
        fr += light(CORE, 0.6 * np.exp(-((d - j) / 2.5) ** 2))
        fr += light(GOLD, (0.15 + 0.3 * flare) * np.exp(-((d - j) / 30.0) ** 2))
        # the opening carries Call Forth Thy Powers' last frame (JM05) and gives way to the ranks drawn up for the march
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * jm05_end(G, glow5, t)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The ritornellos on strings, oboes on the top line; the trio on flute, clarinet and bassoon from the corner of
    Left; the chorus on strings with oboes and bassoons doubling and horns on the long notes, moving with the column;
    a harpsichord continuo throughout; marching feet under the chorus."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    l0, l1 = span(G, 'Left')
    o = Orchestra(M, level=2.3)
    pl = pan_at(l1 - 40)
    trio = {'A': ('flutes', 0), 'T': ('clarinets', -2), 'B': ('bassoons', 0)}
    for t, dur, m, v, h, part in NOTES:
        if part == 'Orch':
            big = t >= T_STAND - 0.01
            if h == 0:
                o.play('violins', m, t, dur * 0.95, v - 4, None, 0.55)
                if m >= 64 and (t < T_TRIO or big):
                    o.play('oboes', m, t, dur * 0.9, v - 14, None, 0.3)
                if big and m < 64:
                    o.play('violas', m, t, dur * 0.95, v - 10, None, 0.35)
            elif m >= 55:
                o.play('violins' if m >= 62 else 'violas', m, t, dur * 0.95, v - 8, None, 0.45)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, dur * 0.95, v - 4, None, 0.5)
                o.play('basses', m - 12 if m >= 40 else m, t, dur * 0.95, v - 10, None, 0.35)
                if big:
                    o.play('bassoons', m, t, dur * 0.9, v - 12, None, 0.3)
        elif t < T_CHORUS - 0.1:
            sec, dv = trio[part]
            o.play(sec, m, t, dur * 0.95, v + dv, pl + {'A': -0.08, 'T': 0.0, 'B': 0.08}[part], 0.8)
        else:
            pan = pan_at(judas(G, t) - 60)
            if part == 'A':
                o.play('violins', m, t, dur * 0.97, v, pan - 0.1, 0.55)
                o.play('oboes', m, t, dur * 0.95, v - 10, pan - 0.1, 0.35)
            elif part == 'T':
                o.play('violas', m, t, dur * 0.97, v, pan, 0.55)
            else:
                o.play('cellos', m, t, dur * 0.97, v, pan + 0.1, 0.6)
                o.play('basses', m - 12 if m >= 40 else m, t, dur * 0.97, v - 8, pan + 0.1, 0.4)
                o.play('bassoons', m, t, dur * 0.95, v - 12, pan + 0.1, 0.3)
            if dur >= BARLEN * 0.6 and part in ('A', 'T'):
                o.play('horns', m - 12 if m > 67 else m, t, dur * 0.95, v - 14, pan, 0.35)
    # the continuo: the bass line with the chord above it, plucked short
    cont = []
    for t, dur, m, v, h, part in NOTES:
        if part == 'B' or (part == 'Orch' and h == 1 and m < 55):
            cont.append((t, m, 76, min(dur, BARLEN / 3)))
            for cm in sorted({n[2] for n in SUNG if abs(n[0] - t) < 0.02 and n[5] in ('A', 'T')}):
                cont.append((t, cm, 66, min(dur, BARLEN / 3)))
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, D + 2.0), 0.0, 0.4, 0.0)
    # marching feet: a tread on every beat of every bar the column marches, panned with it
    o.effects([(0.0, -4.0), (T_MARCH - 0.5, -4.0), (T_MARCH, 0.0), (T_STAND, -2.0), (D, -2.0)])
    t = T_MARCH
    while t < T_LAST:
        for k, (dt, vv) in enumerate(((0.0, 96), (BARLEN / 3, 70), (2 * BARLEN / 3, 74))):
            o.hit('hoof soft', t + dt, vv, pitch=-6, gain=0.35, pan=pan_at(judas(G, t) - 80), fx=True)
        t += BARLEN
    o.hit('bass drum', T_LAST, 90, gain=0.25, pan=pan_at(span(G, 'Porch Left')[1]), fx=True)
