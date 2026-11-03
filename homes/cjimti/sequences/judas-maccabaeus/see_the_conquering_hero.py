"""See, the Conqu'ring Hero Comes: Judas returns, and the chorus that greets him grows from three voices to everyone.

It opens where Father of Heav'n (JM11) ended, the Temple full of its light and the people's blue and white bands over
the house, and over the first bars that gives way to the night Judas comes home through (CARRY, from JM11's last
frame: change both together). A few voices first, the Chorus of Youths, three high voices over the organ. Judas's
brass gold comes along Left from near the corner of the house, a step on every beat, with three small white lights
beside him, one for each voice, each flaring as it sings; at "comes" he turns up Porch Left, the road to the Temple,
and walks it to the back of the porch by "beat the drums".

Then the Full Chorus: "See, the conqu'ring hero comes" again, forte, sopranos, altos, tenors and basses. Judas goes
into the Temple on Porch Front, where the olive-oil glow brightens round him, and the people come out to line the
road: blue and white lights appear along Porch Left and Porch Right, then out along Left and Right, each one on a
chorus note, more with every bar. "Sports prepare, the laurel bring": the whole road is lined, every light stepping on
the beat, and gold runs out from the Temple along the runs on each run of eighths. The last "See, the conqu'ring hero
comes", with the trumpets and drums the words call for: the whole house in blue, white and gold, a wave of gold from
the Temple on every bar, a flare on "Sound the trumpets", a white flash on each drum stroke at "beat the drums", and
the last chord held, Judas's gold at the heart of the Temple.

The music is Handel's own: No. 58 (its page misprints it No. 59), the Chorus of Youths (its first eight bars) and the
whole Full Chorus, transcribed from the Novello vocal score into see_the_conquering_hero.musicxml and timed by
scripts/score_excerpt.py at crotchet 100 (the score has no marking). The youths are played on oboe, flute and clarinet
over the organ's line on a harpsichord and soft cellos; the Full Chorus on strings with oboes and bassoons doubling
and horns on the long notes, and its last statement adds trumpets on the tune and timpani. render() and score() both
read the notes from the excerpt."""
import numpy as np
from pixelhome.audio import Synth
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM12'
TITLE = "See, the Conqu'ring Hero Comes"
KIND = 'show'
DESCRIPTION = ("Judas's gold walks up the road to the Temple with three voices beside him; then the people line the "
               "road, the whole chorus greets him, and the trumpets and drums light the whole house.")

EX = excerpt(__file__)              # No. 58: the trio (bars 1-8), the Full Chorus (9-32)
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 2.5, 2)  # the show's length: the music and its last chord held
END = D
BEAT = BAR[2] - BAR[1]
QUARTER = BEAT / 4
T_CHORUS = BAR[9]
T_SPORTS = BAR[17]
T_LAST = BAR[25]
T_TRUMPETS = BAR[29]
T_DRUMS = BAR[31]
T_FINAL = BAR[32]
NOTES = EX['notes']
TRIO = {p: [n for n in NOTES if n[5] == p] for p in ('S1', 'S2', 'A')}
CHORUS = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ONSETS = np.array(sorted({round(n[0], 3) for n in CHORUS}))
EIGHTHS = sorted({round(n[0], 3) for n in NOTES if n[5] in ('S', 'S1') and n[1] < QUARTER * 0.75})

GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')
BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')
NIGHT = hexc('#0a1a4a')
OIL = hexc('#ffb33a')
TIP = hexc('#fff1c0')
CARRY = 4.0                         # seconds the Temple full of light from Father of Heav'n (JM11) takes to give way


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def route(G):
    """Judas's way: (times, path distances) along Left to the corner, up Porch Left, into the middle of the Temple."""
    l0, l1 = span(G, 'Left')
    p0, p1 = span(G, 'Porch Left')
    f0, f1 = span(G, 'Porch Front')
    start = l0 + 0.25 * (l1 - l0)
    pts = [(0.0, start), (BAR[4], l1), (BAR[8] + 3 * QUARTER, p1), (BAR[11], 0.5 * (f0 + f1)), (END, 0.5 * (f0 + f1))]
    return pts


def where(pts, t):
    """Judas's distance at t: a step on every beat between the route's points."""
    for (ta, da), (tb, db) in zip(pts, pts[1:]):
        if t <= tb:
            u = (t - ta) / max(tb - ta, 1e-6)
            steps = max(1, round((tb - ta) / QUARTER))
            k = np.floor(u * steps)
            frac = u * steps - k
            return da + (db - da) * (k + smoothstep(0.0, 0.45, frac)) / steps
    return pts[-1][1]


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(END)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    glow = Glow(G, seed)
    temple = (seg == 'Porch Front').astype(float)
    road = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    wings = np.isin(seg, ['Left', 'Right']).astype(float)
    side = (seg == 'Side').astype(float)
    f0, f1 = span(G, 'Porch Front')
    mid = 0.5 * (f0 + f1)
    flick = Flicker(rng, G.N, 0.5, 2.0)
    pts = route(G)
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)     # JM11's blue and white bands

    # the people: small lights along the road, then the wings, each with the chorus onset it appears on
    lights = []
    for s, a, b in (('Porch Left', 0.0, 0.3), ('Porch Right', 0.0, 0.3), ('Left', 0.25, 0.75), ('Right', 0.25, 0.75)):
        s0, s1 = span(G, s)
        for c in np.arange(s0 + 6, s1 - 4, 15.0):
            lights.append((c, rng.uniform(a, b), rng.random() < 0.5))
    lights = np.array([(c, u, w) for c, u, w in lights], float)
    appear = np.interp(lights[:, 1], [0, 1], [T_CHORUS, T_SPORTS])
    appear = ONSETS[np.clip(np.searchsorted(ONSETS, appear), 0, len(ONSETS) - 1)]
    shape = np.exp(-((d[None, :] - lights[:, :1]) / 4.0) ** 2)             # (L, N)
    white_l, blue_l = lights[:, 2] > 0.5, lights[:, 2] < 0.5

    def onset_pulse(notes, t, tau=0.3):
        v = 0.0
        for n in notes:
            if n[0] <= t < n[0] + 1.2:
                v = max(v, np.exp(-(t - n[0]) / tau))
        return v

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        # the bed: night blue everywhere, warming to the people's blue as the chorus comes out
        crowd = smoothstep(T_CHORUS - 1.0, T_SPORTS, t)
        fr += light(NIGHT, (0.24 + 0.04 * flick(t)) * (1 - temple) * (1 - 0.5 * crowd))
        fr += light(BLUE, (0.05 + 0.25 * crowd) * (road + wings + 0.5 * side))
        # the Temple's glow, brightening when Judas comes into it
        inside = smoothstep(BAR[9], BAR[11], t)
        fr += glow.frame(t, 1.0 + 1.2 * inside)
        # the people's lights, each appearing on its note and stepping on the beat once the road is lined
        on = smoothstep(0.0, 0.25, t - appear)
        beat = 0.0
        if t >= T_SPORTS:
            ph = ((t - T_SPORTS) / QUARTER) % 1.0
            beat = np.exp(-ph / 0.25)
        lvl = on * (0.45 + 0.5 * beat)
        if t >= T_CHORUS:
            fr += light(WHITE, (lvl * white_l) @ shape)
            fr += light(BLUE, 1.3 * (lvl * blue_l) @ shape)
        # gold running out from the Temple on each run of eighths (Sports prepare, Songs of triumph, Sound the)
        if t >= T_CHORUS:
            for te in EIGHTHS:
                a = t - te
                if 0 <= a < 1.6 and te >= T_CHORUS:
                    front = 40 + 260 * a
                    band = np.exp(-((np.abs(d - mid) - front) / 22.0) ** 2) * (1 - temple)
                    fr += light(GOLD, 0.7 * np.exp(-a / 0.8) * band)
        # the last statement: a wave of gold from the Temple on every bar, the trumpets' flare, the drum strokes
        if t >= T_LAST:
            fill = smoothstep(T_LAST, T_LAST + 2 * BEAT, t)
            fr += light(GOLD, 0.3 * fill * (road + wings + side))
            for b in range(25, 33):
                a = t - BAR[b]
                if 0 <= a < 2.5:
                    front = 300 * a
                    band = np.exp(-((np.abs(d - mid) - front) / 30.0) ** 2)
                    fr += light(GOLD, 0.55 * np.exp(-a / 1.2) * band)
            a = t - T_TRUMPETS
            if 0 <= a < 2 * BEAT:
                fr += light(GOLD, 0.6 * np.exp(-a / 1.0) * np.ones(G.N))
            for k in range(4):
                a = t - (T_DRUMS + k * QUARTER)
                if 0 <= a < 0.6:
                    fr += light(WHITE, 0.55 * np.exp(-a / 0.12) * (road + wings))
            if t >= T_FINAL:
                a = t - T_FINAL
                fr += light(WHITE, 0.3 * np.exp(-a / 0.4) * np.ones(G.N))
                fr += light(GOLD, 0.15 * smoothstep(0, 0.5, a) * np.ones(G.N))
        # Judas: brass gold walking on the beat, a step at a time; at the heart of the Temple from bar 11
        p = where(pts, t)
        warm = 1.0 + 0.4 * smoothstep(T_LAST, T_LAST + BEAT, t)
        fr += light(GOLD, 0.95 * warm * np.exp(-((d - p) / 9.0) ** 2))
        fr += light(CORE, 0.7 * np.exp(-((d - p) / 3.5) ** 2))
        fr += light(GOLD, 0.2 * np.exp(-((d - p) / 40.0) ** 2))
        # the three youths beside him, a little behind, each flaring as it sings
        if t < T_CHORUS + 2 * BEAT:
            fade = 1 - smoothstep(T_CHORUS, T_CHORUS + 2 * BEAT, t)
            for k, part in enumerate(('S1', 'S2', 'A')):
                q = p - (14 + 11 * k)
                v = onset_pulse(TRIO[part], t)
                fr += light(WHITE, fade * (0.35 + 0.55 * v) * np.exp(-((d - q) / 3.0) ** 2))
        # the opening carries Father of Heav'n's last frame (JM11) and gives way to this scene over the first bars
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            jm11 = (light(BLUE, 0.33 * band * (1 - temple)) + light(WHITE, 0.33 * (1 - band) * (1 - temple))
                    + light(OIL, 0.85 * temple) + light(TIP, 0.08 * temple) + glow.frame(t, 0.8))
            fr = (1 - carry) * fr + carry * jm11
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The youths on oboe, flute and clarinet with the organ line on a harpsichord and cellos, moving with Judas; the
    Full Chorus on strings, oboes and bassoons doubling, horns on the long notes; the last statement with trumpets on
    the tune and timpani, and the drums the words call for."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pts = route(G)
    o = Orchestra(M, level=1.5)
    trio_inst = {'S1': ('oboes', 0), 'S2': ('flutes', -2), 'A': ('clarinets', -2)}
    for t, dur, m, v, h, part in NOTES:
        if part in trio_inst:
            sec, dv = trio_inst[part]
            o.play(sec, m, t, dur * 0.95, 62 + 0.3 * v + dv, pan_at(where(pts, t)), 0.85)
        elif part == 'Orch':
            o.play('cellos', m - 12, t, dur * 0.95, 55, pan_at(where(pts, t)), 0.35)
        else:
            last = t >= T_LAST - 0.01
            pan = {'S': -0.35, 'A': -0.15, 'T': 0.15, 'B': 0.35}[part]
            vel = 70 + 0.3 * v + (8 if last else 0)
            if part == 'S':
                o.play('violins', m, t, dur * 0.97, vel, pan, 0.8)
                o.play('oboes', m, t, dur * 0.95, vel - 6, pan, 0.55)
                if last:
                    o.play('trumpets', m, t, dur * 0.9, vel, -0.1, 0.55)
            elif part == 'A':
                o.play('violins', m, t, dur * 0.97, vel - 4, pan, 0.6)
                if dur >= BEAT / 2:
                    o.play('horns', m, t, dur * 0.95, vel - 10, pan, 0.4)
            elif part == 'T':
                o.play('violas', m, t, dur * 0.97, vel, pan, 0.75)
                if dur >= BEAT / 2:
                    o.play('horns', m, t, dur * 0.95, vel - 10, pan, 0.4)
            else:
                o.play('cellos', m, t, dur * 0.97, vel, pan, 0.8)
                o.play('basses', m - 12 if m >= 52 else m, t, dur * 0.97, vel - 4, pan, 0.6)
                o.play('bassoons', m, t, dur * 0.95, vel - 10, pan, 0.45)
    # the harpsichord continuo: the organ's line under the youths, the bass's notes under the chorus
    cont = []
    for t, dur, m, v, h, part in NOTES:
        if part in ('Orch', 'B'):
            cont.append((t, m if part == 'Orch' else m, 70 if part == 'Orch' else 82, min(dur, BEAT / 2)))
            if part == 'B':
                ch = sorted({n[2] for n in CHORUS if abs(n[0] - t) < 0.02 and n[5] in ('A', 'T')})
                for cm in ch:
                    cont.append((t, cm, 66, min(dur, BEAT / 2)))
    harp = Synth('Keys/Digi Harpsi').render(cont, END + 2)
    M.add('harp', harp, 0.0, 0.5, 0.0)
    # timpani: each bar of the last statement, the strokes "beat the drums" calls for, a roll on the last chord
    for b in range(25, 33):
        o.hit('timpani', BAR[b], 100, pitch=-5 if b % 2 else 0, gain=0.35, pan=0.2)
    for k in range(4):
        o.hit('timpani', T_DRUMS + k * QUARTER, 110, pitch=0, gain=0.4, pan=0.2)
    o.hit('timpani roll', T_FINAL, 96, pitch=0, gain=0.3, pan=0.2)
    o.hit('timpani', END - 0.2, 105, pitch=-5, gain=0.35, pan=0.2)
