"""Fall'n Is the Foe: the first victory. The Maccabees sweep onto the field, and the Seleucid purple breaks and flees.

It opens where Disdainful of Danger (JM06) ended: the column of blue and white ranks filling Porch Left with Judas's
brass gold at its head by the Temple, the purple holding Right and Side (change both together). The ritornello is the
charge: the column pours down the porch, past the Temple, down Porch Right and onto the field at the corner of Right,
Judas in front.

Then the chorus. The purple on Right stands in blocks, and every "Fall'n" breaks one: a white blow at the front, the
block cracks and its pieces scatter back up Right toward the road from Antioch, the free end, and go out, and the
blue and white sweep in to hold the ground. The tenors and basses in unison break the first two, then the altos, the
sopranos, the tenors and the sopranos each break the next, and the whole chorus the last; by "so fall thy foes, O
Lord!" the field is clear and blue and white run the length of Right, and the purple on Side has gone too.

The hammered "Fall'n, Fall'n is the foe": the ranks on the field pound on every chord. "So fall thy foes, O Lord!",
twice: a wave of gold from Judas out along the field. "Where warlike Judas wields his righteous sword": Judas's gold
swings left and right on each word, and on "sword." it flares and settles. The last frame: blue and white ranks over
Porch Right and the whole of Right, Judas in the middle of the field, a soft blue on Left, Porch Left and Side,
the Temple still grey with its idols over the glow of the lights.

The music is Handel's own: No. 27, the ritornello's first four bars, the chorus from its entry to the tutti "O
Lord!" on C, and the last page from the hammered "Fall'n" to the end, transcribed from the Novello vocal score into
fallen_is_the_foe.musicxml and timed by scripts/score_excerpt.py at crotchet 92 (Allegro moderato). The chorus plays
on strings with oboes and bassoons doubling and horns on the long notes; the ritornello on strings with oboes and
bassoons; a harpsichord continuo. The battle gets the sounds a production would give it, under the music: steel on
every block that breaks, hoofbeats as its pieces flee, a drum in the chorus's rests.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM07'
TITLE = "Fall'n Is the Foe"
KIND = 'show'
DESCRIPTION = ("The first victory: the Maccabees' blue and white sweep onto the field on Right, and every 'Fall'n' "
               "breaks a block of Seleucid purple, which scatters back to the road from Antioch.")
VOICEOVER = 'The first battle is won. Fallen is the foe, the people sing, and the enemy runs for home.'

EX = excerpt(__file__)              # ritornello 1-4, the chorus 5-21, p. 75's "Fall'n" 22-26, the end 27-30
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
D = round(END + 3.0, 2)
BEAT = BAR[2] - BAR[1]
BEAT = BEAT / 4
T_CHORUS = BAR[5]
T_TUTTI = BAR[15]
T_CLEAR = BAR[21]                   # "O Lord!" on C: the field is clear
T_HAMMER = BAR[22]
T_SOFALL = [BAR[25], BAR[26]]
T_WHERE = BAR[27] + 10 * BEAT / 4   # "Where warlike Judas"
T_RIGHTEOUS = BAR[29]
T_SWORD = BAR[30]
NOTES = EX['notes']
SUNG = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
# every "Fall'n" that breaks a block: the entries' first beats, in order
BREAKS = [BAR[b] for b in (5, 6, 9, 10, 11, 14, 15, 18)]
HAMMER = sorted({round(n[0], 3) for n in ORCH if T_HAMMER - 0.01 <= n[0] < BAR[25] - 0.01})
STROKES = sorted({round(n[0], 3) for n in SUNG if T_WHERE - 0.05 <= n[0] < T_RIGHTEOUS - 0.01})
RESTS = []                          # the chorus's rests, where the battle is heard
_on = sorted({round(n[0], 3) for n in SUNG if T_CHORUS <= n[0] < T_HAMMER})
for a, b in zip(_on, _on[1:]):
    ends = max(n[0] + n[1] for n in SUNG if abs(n[0] - a) < 0.002)
    if b - ends > 0.5:
        RESTS.append(ends + 0.1)

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
GLINT = hexc('#c08a40')
STONE = hexc('#6a6a6a')             # the idols
BLUE = hexc('#1e5bd8')              # the Maccabees
WHITE = hexc('#f2f6ff')
GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')

STEP = 21.0                         # between ranks: as in Disdainful of Danger (JM06)
SHIFT0 = 412.0                      # where JM06 left the column (its SHIFT)
SHIFT1 = 1162.0                     # the column at the end of the charge: Porch Right and the corner of Right
BLOCKS = 8                          # the purple on Right, in blocks


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def ranks(G):
    """The ranks' path distances before JM06's march (along Left) and which are white: as in JM06."""
    l0, l1 = span(G, 'Left')
    pos = np.arange(l0 + 14, l1 - 6, STEP)
    return pos, (np.arange(len(pos)) % 2 == 1)


def charge(t):
    """How far the column has moved: JM06's end, then a stride on every bar of the ritornello."""
    u = min(max(t / (4 * 4 * BEAT), 0.0), 1.0) * 4
    k = min(np.floor(u), 3)
    return SHIFT0 + (SHIFT1 - SHIFT0) * (k + smoothstep(0.0, 0.8, u - k)) / 4


def blocks(G):
    """The purple blocks' centres along Right and their half width."""
    r0, r1 = span(G, 'Right')
    start = r0 + 2 * STEP + 10
    w = (r1 - start) / BLOCKS
    return start + w * (np.arange(BLOCKS) + 0.5), w / 2


def front(G, t):
    """How far the Maccabees hold Right: up to each broken block's far edge, a moment after it breaks."""
    c, h = blocks(G)
    f = c[0] - h
    for k, tb in enumerate(BREAKS):
        f = f + (c[k] + h - f) * smoothstep(tb + 0.1, tb + 1.0, t) if t > tb else f
    return f


def judas(G, t):
    """Judas's path distance: at the head of the column, then at the front of the fight, then in the middle of the
    field for the last bars."""
    c, h = blocks(G)
    r0, r1 = span(G, 'Right')
    head = span(G, 'Left')[1] - 8 + charge(t)                  # where JM06 left him, at the column's head
    if t < T_CHORUS:
        return head
    j = max(head, front(G, t) - 12)
    return j + (0.5 * (r0 + r1) - j) * smoothstep(T_CLEAR, T_HAMMER, t)


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    p0, p1 = span(G, 'Porch Left')
    q0, q1 = span(G, 'Porch Right')
    f0, f1 = span(G, 'Porch Front')
    r0, r1 = span(G, 'Right')
    left = (seg == 'Left').astype(float)
    side = (seg == 'Side').astype(float)
    right = (seg == 'Right').astype(float)
    runL = (seg == 'Porch Left').astype(float)
    runR = (seg == 'Porch Right').astype(float)
    frontseg = (seg == 'Porch Front').astype(float)
    idols = np.zeros(G.N)
    for k in range(4):
        c = f0 + (0.14 + 0.24 * k) * (f1 - f0)
        idols += smoothstep(14, 9, np.abs(d - c))
    idols = np.minimum(idols, 1) * frontseg
    base, white = ranks(G)
    grid = np.arange(base[0] + SHIFT1, r1 - 4, STEP)           # the ranks on the field, continuing the column
    gwhite = (np.arange(len(grid)) % 2 == 1)
    c, h = blocks(G)
    pieces = rng.uniform(0.6, 1.4, (BLOCKS, 5))
    slow = Flicker(rng, G.N, 0.1, 0.4)
    glints = Flicker(rng, G.N, 0.3, 1.2)
    for f in range(F):
        t = f * DT
        live = smoothstep(0.0, 2.5, t) * (1 - smoothstep(D - 2.5, D - 0.5, t))
        fr = np.zeros((G.N, 3))
        clear = smoothstep(T_TUTTI, T_CLEAR, t)                 # the land freed: Side's purple goes too
        passed = smoothstep(BAR[2], BAR[4], t)                  # the column has left Porch Left
        # the purple: Side, and Right's blocks until each breaks
        fr += light(PURPLE, 0.42 * side * (1 - clear) * (1 + 0.1 * live * (slow(t) - 0.5)))
        fr += light(BLUE, 0.22 * side * clear)
        hold = np.zeros(G.N)
        gap = 10 * smoothstep(BAR[2], BAR[4], t)                # the purple draws up in blocks
        for k in range(BLOCKS):
            tb = BREAKS[k]
            if t < tb:
                hold += np.clip((h + 3 - gap - np.abs(d - c[k])) / 3.0, 0, 1)
        unbroken = np.minimum(hold, 1) * right
        strip = right * (d < c[0] - h) * (1 - smoothstep(BAR[4], T_CHORUS, t))     # where the charge lands
        fr += light(PURPLE, 0.42 * np.minimum(unbroken + strip, 1) * (1 + 0.1 * live * (slow(t) - 0.5)))
        fr += light(GLINT, 0.18 * live * unbroken * np.maximum(glints(t), 0) ** 4)
        # the breaking: a white blow, then the pieces flee to the free end and go out
        for k, tb in enumerate(BREAKS):
            b = t - tb
            if 0 <= b < 0.6:
                fr += light(WHITE, 1.0 * np.exp(-b / 0.25) * np.clip((h - 4 - np.abs(d - c[k])) / 3.0, 0, 1) * right)
            if 0 <= b < 3.5:
                for j in range(5):
                    s = pieces[k, j]
                    x = c[k] + (j - 2) * 0.35 * h + s * 90.0 * b + 40.0 * b * b
                    if x < r1 + 10:
                        fade = np.exp(-b / (1.2 * s)) * (1 - smoothstep(2.6, 3.5, b))
                        fr += light(PURPLE, 1.0 * fade * np.exp(-((d - x) / 6.0) ** 2) * right)
                        fr += light(GLINT, 0.5 * fade * np.exp(-((d - x) / 2.0) ** 2) * right)
        # the porch runs: dim purple, Porch Left blue once the column has passed
        fr += light(PURPLE, 0.14 * (runL * (1 - passed) + runR * (1 - smoothstep(BAR[3], BAR[5], t))))
        fr += light(BLUE, (0.12 + 0.1 * clear) * (runL * passed + left))
        # the Temple: grey idols over the lights' glow
        fr += light(STONE, 0.5 * idols) + glow.frame(t, 0.55)
        # the column: JM06's ranks charging round the porch (out of sight as they pass the Temple), then the field
        off = charge(t)
        pos = base + off
        vis = np.where(pos < p1, smoothstep(p1 - 4, p1 - 30, pos), smoothstep(q0 + 4, q0 + 30, pos))
        lvl = 0.48 * vis
        if t < T_CHORUS:
            ph = (t / BEAT) % 4.0
            lvl = lvl + 0.15 * live * np.exp(-(ph % 1.0) / 0.2) * (ph < 1.0)
        shape = np.exp(-((d[None, :] - pos[:, None]) / 4.0) ** 2)
        fr += light(WHITE, (lvl * white) @ shape)
        fr += light(BLUE, 1.25 * (lvl * ~white) @ shape)
        if t >= T_CHORUS - 0.5:
            fnt = front(G, t)
            on = smoothstep(fnt + 2, fnt - 12, grid) * (grid > pos[-1] + 1)
            g = np.full(len(grid), 0.48) * on
            # the hammered chords: the field pounds on every chord, white and blue in turn
            for k, th in enumerate(HAMMER):
                a = t - th
                if 0 <= a < 0.3:
                    g = g + 0.45 * np.exp(-a / 0.1) * on * (gwhite if k % 2 else ~gwhite)
            gshape = np.exp(-((d[None, :] - grid[:, None]) / 4.0) ** 2)
            fr += light(WHITE, (g * gwhite) @ gshape)
            fr += light(BLUE, 1.25 * (g * ~gwhite) @ gshape)
            if t >= T_HAMMER:                                   # the column's ranks pound too
                for k, th in enumerate(HAMMER):
                    a = t - th
                    if 0 <= a < 0.3:
                        p = 0.3 * np.exp(-a / 0.1) * (white if k % 2 else ~white)
                        fr += light(WHITE, (p * white) @ shape) + light(BLUE, 1.25 * (p * ~white) @ shape)
        # Judas
        j = judas(G, t)
        fr += light(GOLD, 0.95 * np.exp(-((d - j) / 6.0) ** 2))
        fr += light(CORE, 0.6 * np.exp(-((d - j) / 2.5) ** 2))
        fr += light(GOLD, 0.15 * np.exp(-((d - j) / 30.0) ** 2))
        # "so fall thy foes, O Lord!": a gold wave from Judas out along the field
        for ts in T_SOFALL:
            a = t - ts
            if 0 <= a < 2.5:
                r = 25 + 170 * a
                fr += light(GOLD, 0.55 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - j) - r) / 20.0) ** 2) * (right + runR))
        # "Where warlike Judas wields his righteous sword": the sword swings on each word, then flares
        for k, ts in enumerate(STROKES):
            a = t - ts
            if 0 <= a < 0.8:
                x = j + (1 if k % 2 == 0 else -1) * 90 * smoothstep(0, 0.35, a)
                fr += light(GOLD, 0.8 * np.exp(-a / 0.3) * np.exp(-((d - x) / 10.0) ** 2) * right)
                fr += light(CORE, 0.5 * np.exp(-a / 0.2) * np.exp(-((d - x) / 3.0) ** 2) * right)
        if t >= T_RIGHTEOUS:
            grow = smoothstep(T_RIGHTEOUS, T_SWORD, t) * (1 - smoothstep(T_SWORD + 0.5, D - 0.8, t))
            fr += light(GOLD, 0.45 * grow * np.exp(-((d - j) / 60.0) ** 2) * right)
        if t >= T_SWORD:
            a = t - T_SWORD
            fr += light(WHITE, 0.35 * np.exp(-a / 0.5) * (right + runR))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings with oboes and bassoons doubling and horns on the long notes, sopranos and altos toward
    the porch, tenors and basses toward the field; the ritornello on strings, oboes and bassoons; a harpsichord
    continuo; steel on each block that breaks, hoofbeats as it flees, a drum in the rests."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    r0, r1 = span(G, 'Right')
    c, h = blocks(G)
    o = Orchestra(M, level=2.1)
    side = {'S': -0.3, 'A': -0.1, 'T': 0.2, 'B': 0.4}
    for t, dur, m, v, hand, part in NOTES:
        if part == 'Orch':
            if hand == 0:
                o.play('violins', m, t, dur * 0.95, v - 4, None, 0.55)
                if t < T_CHORUS and m >= 62:
                    o.play('oboes', m, t, dur * 0.9, v - 12, None, 0.3)
                if t >= T_HAMMER:
                    o.play('violas', m, t, dur * 0.9, v - 8, None, 0.35)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, dur * 0.95, v - 4, None, 0.5)
                o.play('basses', m - 12 if m >= 40 else m, t, dur * 0.95, v - 10, None, 0.35)
                if t < T_CHORUS:
                    o.play('bassoons', m, t, dur * 0.9, v - 12, None, 0.3)
            continue
        pan = side[part]
        if part == 'S':
            o.play('violins', m, t, dur * 0.97, v, pan, 0.55)
            o.play('oboes', m, t, dur * 0.95, v - 10, pan, 0.35)
        elif part == 'A':
            o.play('violins', m, t, dur * 0.97, v - 4, pan, 0.45)
            o.play('violas', m, t, dur * 0.97, v - 4, pan, 0.3)
        elif part == 'T':
            o.play('violas', m, t, dur * 0.97, v, pan, 0.55)
            o.play('bassoons', m, t, dur * 0.95, v - 12, pan, 0.25)
        else:
            o.play('cellos', m, t, dur * 0.97, v, pan, 0.6)
            o.play('basses', m - 12 if m >= 40 else m, t, dur * 0.97, v - 8, pan, 0.4)
            o.play('bassoons', m, t, dur * 0.95, v - 10, pan, 0.3)
        if BAR[9] - 0.01 <= t < T_TUTTI - 0.01:              # one voice at a time: the strings in octaves under it
            low = m - 12 if m - 12 < 60 else m - 24
            o.play('cellos', low, t, dur * 0.97, v - 2, pan, 0.55)
            o.play('violas', m - 12, t, dur * 0.97, v - 6, pan, 0.35)
            o.play('horns', low + 12 if low < 50 else low, t, dur * 0.95, v - 10, pan, 0.3)
        if dur >= 2 * BEAT * 0.95 and part in ('S', 'A', 'T'):
            o.play('horns', m - 12 if m > 67 else m, t, dur * 0.95, v - 12, 0.0, 0.35)
    # the continuo: the lowest voice singing, with the chord above it, plucked short
    cont = []
    onsets = sorted({round(n[0], 3) for n in SUNG})
    for t in onsets:
        now = [n for n in SUNG if abs(n[0] - t) < 0.002]
        low = min(now, key=lambda n: n[2])
        cont.append((t, low[2] - 12 if low[2] >= 52 else low[2], 80, min(low[1], BEAT)))
        for n in now:
            if n is not low:
                cont.append((t, n[2], 66, min(n[1], BEAT)))
    cont += [(t, m, 76, min(dur, BEAT / 2)) for t, dur, m, v, hand, part in ORCH if hand == 1]
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, D + 2.0), 0.0, 0.4, 0.0)
    # the battle, under the music: steel as each block breaks, its pieces fleeing on hooves to the free end
    o.effects([(0.0, -3.0), (T_CHORUS - 1.0, -1.0), (T_TUTTI, -4.0), (T_HAMMER, -6.0), (D, -6.0)])
    for k, tb in enumerate(BREAKS):
        p = pan_at(c[k])
        o.clash(tb, p, v=118, gain=0.8)
        o.hit('bass drum', tb, 100, gain=0.35, pan=p, fx=True)
        o.gallop(tb + 0.25, tb + 2.6, beat=0.36, pan=lambda tt, k=k, tb=tb: pan_at(min(c[k] + 150 * (tt - tb), r1)),
                 v=90, gain=0.7)
    for tr in RESTS:
        o.hit('bass drum', tr, 92, gain=0.3, pan=pan_at(0.5 * (r0 + r1)), fx=True)
    for k, ts in enumerate(STROKES):
        o.hit('metal', ts, 90, gain=0.2, pan=pan_at(0.5 * (r0 + r1)), fx=True)
    o.hit('cymbal swell', T_SWORD - 1.2, 70, gain=0.15, pan=0.5)
