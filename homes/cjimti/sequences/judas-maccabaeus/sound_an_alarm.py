"""Sound an Alarm!: new Seleucid armies come in on the road from Antioch, Judas calls the brave, and the people charge
the whole length of the house to meet them.

It opens on the warm tableau Sion Now Her Head Shall Raise (JM08) ended on (TABLEAU, from JM08: change both
together). Judas, alone: "Sound an alarm!", and his brass gold kindles on Left, in the hills, flaring on every note.
The orchestra answers with its fanfare and the warmth drains from the house: at the free end of Right, the road
from Antioch, the Seleucid purple starts to pour in, helmet glints sparking in it, and it comes on all through the
air, the length of Right and round the corner onto Porch Right, with hoofbeats under the music. Judas calls again,
"your silver trumpets sound!", gold rays running from him along Left on each stroke of the orchestra, and on "And
call the brave, and only brave around" the blue and white lights of the brave kindle round him on Left, one with
each run of his voice. His last "Sound an alarm!", alone, held: his gold flares the length of Left.

Then the chorus answers, "We hear, we hear the pleasing dreadful call", and the blue and white ranks charge: a step
along the house on every "hear", led by Judas's gold, up Porch Left, across the Temple and down Porch Right, until
they meet the purple at the corner of Right. From then on every stroke of "And follow thee to conquest" and "If to
fall, for laws, religion, liberty we fall!" is a clash where the colours meet, white sparks thrown both ways, and the
purple is driven back down Right a little with each, until on the last "fall." it is gone off the free end. The
orchestra's close holds the house in the people's blue and white, and in the last seconds it settles into the
tableau We Never Will Bow Down (JM10) opens on: blue and white bands the length of the house, the grey idols standing
in the Temple over the faint glow of the lights.

The music is Handel's own: No. 45, the Allegro with full orchestra from "Sound an alarm!" to Judas's last "Sound an
alarm!" before the da capo, and No. 46, the chorus from "We hear" to "and follow thee to conquest" and its last page,
"If to fall" to the end, transcribed from the Novello vocal score into sound_an_alarm.musicxml and timed by
scripts/score_excerpt.py at dotted crotchet 72. Judas plays on trumpets and a horn; the orchestra's fanfares on
strings, trumpets and timpani; the chorus on strings with oboes and bassoons doubling, trumpets on the sopranos in the
last page, the orchestra's repeated chords under it; a harpsichord plays the continuo. The battle gets hoofbeats as
the armies come in and a clash of steel at the front on every stroke, under the music. render() and score() both read
the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM09'
TITLE = 'Sound an Alarm!'
KIND = 'show'
DESCRIPTION = ("Purple armies pour in from the end of Right while Judas's gold calls the brave on Left; the chorus "
               "answers and the blue and white ranks charge across the house to meet them, steel clashing at the front.")
VOICEOVER = 'A new army is coming from Antioch. Judas sounds the alarm, and the people answer: we hear.'

EX = excerpt(__file__)              # No. 45's Allegro (compact 1-18), No. 46 bars 2-16 (19-33) and its last page (34-47)
BAR = {int(m): t for m, t in EX['bars']}
END = round(EX['seconds'] + 2.5, 2)  # the last chord held
D = END
BARLEN = BAR[2] - BAR[1]
EIGHTH = BARLEN / 6
NOTES = EX['notes']
JUDAS = [n for n in NOTES if n[5] == 'Judas']
CHORUS = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_CHORUS = BAR[19]                  # the orchestra's bar under the chorus's "We"
T_WE = BAR[19] + 5 * EIGHTH         # "We"
T_LAST_CALL = BAR[18]               # Judas's last "Sound an alarm!", alone
T_BRAVE = BAR[12] + 5 * EIGHTH      # "And call the brave"
HEARS = [BAR[b] for b in (20, 21, 22, 23)]
T_MEET = BAR[25]                    # "call,": the ranks meet the purple at the corner of Right
T_IF = BAR[34]                      # "If to fall" (p. 121)
T_FALL = BAR[43]                    # "fall.": the purple is gone
T_CLOSE = BAR[44]                   # the orchestra's close
JUDAS_ON = np.array(sorted(n[0] for n in JUDAS))
CH_ON = np.array(sorted({round(n[0], 3) for n in CHORUS}))
# the strokes at the front: every long chorus note (a dotted crotchet or more) after the ranks meet the purple
STROKES = sorted({round(n[0], 3) for n in CHORUS if n[0] >= T_MEET - 0.01 and n[1] >= 3 * EIGHTH - 0.01})
FANFARE = [b for b in (2, 3, 4, 5, 16, 17, 19)]

GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')
BLUE = hexc('#1e5bd8')              # the Maccabees and the people
WHITE = hexc('#f2f6ff')
PURPLE = hexc('#6a2ca0')            # the Seleucid armies
GLINT = hexc('#c08a40')             # their helmets
NIGHT = hexc('#0a1a4a')
OIL = hexc('#ffb33a')
TIP = hexc('#fff1c0')
STONE = hexc('#6a6a6a')             # the idols
IDOLS = (0.13, 0.37, 0.63, 0.87)
WIDE = 0.09


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def tableau(G):
    """Sion Now Her Head Shall Raise's (JM08) last frame: warm gold on the porch runs, blue and white bands on the
    wings and Side, the Temple glowing round its idols."""
    d, seg = G.pd, G.seg_of
    pf0, pf1 = span(G, 'Porch Front')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    temple = (seg == 'Porch Front').astype(float)
    runs = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    wings = np.isin(seg, ['Left', 'Right']).astype(float) + 0.6 * (seg == 'Side')
    up = np.zeros(G.N)
    m = seg == 'Porch Left'
    up[m] = (d[m] - pl0) / (pl1 - pl0)
    m = seg == 'Porch Right'
    up[m] = (pr1 - d[m]) / (pr1 - pr0)
    u = np.clip((d - pf0) / (pf1 - pf0), -1, 2)
    idol = np.max([np.clip(1 - np.abs(u - c) / WIDE, 0, 1) ** 0.4 for c in IDOLS], 0) * temple
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
    return (light(NIGHT, 0.12 * (1 - temple)) + light(OIL, 0.5 * runs * (0.75 + 0.25 * up))
            + light(BLUE, 0.42 * band * wings) + light(WHITE, 0.32 * (1 - band) * wings)
            + light(OIL, 0.22 * 1.6 * temple) + light(TIP, 0.05 * temple) + light(STONE, 0.5 * idol))


def bow_down(G):
    """We Never Will Bow Down's (JM10) first frame: the people's bands over the house, the idols in the Temple."""
    rng = np.random.default_rng(10)
    glow = Glow(G, 10)
    shimmer = Flicker(rng, G.N, 0.2, 0.6)
    d, seg = G.pd, G.seg_of
    temple = seg == 'Porch Front'
    house = ~temple
    pf0, pf1 = span(G, 'Porch Front')
    u = np.clip((d - pf0) / (pf1 - pf0), -1, 2)
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
    lvl = 0.4 * (0.95 + 0.05 * shimmer(0.0))
    fr = light(BLUE, lvl * band * house) + light(WHITE, lvl * (1 - band) * 0.7 * house)
    fr += light(BLUE, 0.6 * lvl * (1 - band) * 0.3 * house)
    fr += glow.frame(0.0, 0.8)
    for c in IDOLS:
        idol = np.clip(1 - np.abs(u - c) / WIDE, 0, 1) ** 0.4 * temple
        fr += light(STONE, 0.8 * idol * (0.97 + 0.03 * shimmer(0.0)))
    return np.clip(fr, 0, 1)


def charge(G):
    """The ranks' front along the path, by time: on Left until the chorus, a step on every "hear" and phrase after,
    meeting the purple at the corner of Right."""
    l0, l1 = span(G, 'Left')
    pl0, pl1 = span(G, 'Porch Left')
    pf0, pf1 = span(G, 'Porch Front')
    pr0, pr1 = span(G, 'Porch Right')
    r0, r1 = span(G, 'Right')
    pts = [(0.0, l1 - 40), (HEARS[0], l1 - 40), (HEARS[0] + 0.6, pl0 + 0.4 * (pl1 - pl0)),
           (HEARS[1], pl0 + 0.4 * (pl1 - pl0)), (HEARS[1] + 0.6, pl1), (HEARS[2], pl1),
           (HEARS[2] + 0.6, pf0 + 0.6 * (pf1 - pf0)), (HEARS[3], pf0 + 0.6 * (pf1 - pf0)),
           (HEARS[3] + 0.6, pr0 + 0.25 * (pr1 - pr0)), (BAR[24], pr0 + 0.25 * (pr1 - pr0)), (T_MEET, meet(G) - 14)]
    return pts


def meet(G):
    """Where the ranks meet the purple: on Porch Right, near the corner of Right."""
    pr0, pr1 = span(G, 'Porch Right')
    return pr1 - 0.4 * (pr1 - pr0)


def at(pts, t):
    ts = [p[0] for p in pts]
    vs = [p[1] for p in pts]
    if t <= ts[0]:
        return vs[0]
    for (ta, va), (tb, vb) in zip(pts, pts[1:]):
        if t <= tb:
            return va + (vb - va) * smoothstep(ta, tb, t)
    return vs[-1]


def enemy(G, t):
    """Where the purple's front is: from the free end of Right (none) along Right and onto Porch Right in the air,
    held at the corner where the ranks meet it, then driven back to the free end, a little on every stroke."""
    r0, r1 = span(G, 'Right')
    pr0, pr1 = span(G, 'Porch Right')
    if t < T_MEET:
        pts = [(BAR[2], r1 + 15), (BAR[8], r1 - 0.45 * (r1 - r0)), (BAR[13], r0 + 20), (BAR[18], meet(G))]
        return at(pts, t)
    done = sum(smoothstep(s, s + 0.5, t) for s in STROKES) / max(1, len(STROKES))
    gone = smoothstep(T_FALL - 0.5, T_FALL + 1.0, t)
    return meet(G) + (r1 + 40 - meet(G)) * min(1.0, 0.85 * done + gone)


def render(G, seed=9):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    flick = Flicker(rng, G.N, 0.6, 2.4)
    slow = Flicker(rng, G.N, 0.15, 0.5)
    l0, l1 = span(G, 'Left')
    pf0, pf1 = span(G, 'Porch Front')
    temple = (seg == 'Porch Front').astype(float)
    left = (seg == 'Left').astype(float)
    side = (seg == 'Side').astype(float)
    u = np.clip((d - pf0) / (pf1 - pf0), -1, 2)
    idol = np.max([np.clip(1 - np.abs(u - c) / WIDE, 0, 1) ** 0.4 for c in IDOLS], 0) * temple
    first, last = tableau(G), bow_down(G)
    jx = l0 + 0.62 * (l1 - l0)                              # Judas, on Left in the hills of Modein
    pts = charge(G)
    # the brave on Left: a light kindled on each of Judas's runs ("call the brave, and only brave around")
    runs = [t for t in JUDAS_ON if T_BRAVE <= t < BAR[17] and
            not any(0 < t - s < 2.5 * EIGHTH / 3 for s in JUDAS_ON if s < t)]
    brave_t = runs + [BAR[16] + k * EIGHTH for k in range(6)]
    brave_x = l0 + np.linspace(0.12, 0.95, len(brave_t)) * (l1 - l0)
    brave_x = brave_x[np.argsort(np.abs(brave_x - jx))]  # nearest Judas first
    brave_w = np.array([k % 2 for k in range(len(brave_t))])
    for f in range(F):
        t = f * DT
        sh = 0.9 + 0.1 * slow(t)
        # the warmth drains as the alarm sounds; the night comes back
        drain = smoothstep(BAR[2] - 0.2, BAR[6], t)
        fr = light(NIGHT, (0.12 + 0.12 * drain) * (1 - temple) * sh)
        # the Temple: the idols over the faint glow of the lights
        fr += glow.frame(t, 0.8 + 0.8 * (1 - drain)) + light(STONE, (0.5 + 0.3 * smoothstep(T_FALL, END - 3, t)) * idol)
        # the purple, from the free end of Right, with its helmet glints
        e = enemy(G, t)
        occ = smoothstep(e - 12, e + 12, d) * (1 - temple)
        fr += light(PURPLE, 0.62 * occ * (0.85 + 0.15 * flick(t)))
        fr += light(GLINT, 0.35 * occ * np.maximum(flick(t * 0.7), 0) ** 10)
        # the ranks: blue and white blocks from the start of Left to their front, marching as they charge
        front = at(pts, t)
        if t >= T_MEET:
            front = max(front, e - 14)
        if t >= HEARS[0] - 0.5:
            march = 60.0 * smoothstep(HEARS[0], T_MEET, t) + 0.8 * max(0.0, t - T_MEET) * 10
            band = (np.sin(2 * np.pi * (d - march) / 110.0) > 0.25).astype(float)
            i = int(np.searchsorted(CH_ON, t, side='right')) - 1
            beat = np.exp(-(t - CH_ON[i]) / 0.3) if i >= 0 else 0.0
            ranks = smoothstep(l0 - 1, l0 + 20, d) * smoothstep(front + 8, front - 8, d)
            ranks = ranks * (1 - 0.55 * temple) * (1 - side)
            lv = (0.42 + 0.25 * beat) * smoothstep(HEARS[0] - 0.5, HEARS[0] + 0.3, t)
            fr += light(BLUE, lv * band * ranks) + light(WHITE, 0.85 * lv * (1 - band) * ranks)
        # the brave kindling round Judas on Left before the charge
        if T_BRAVE - 0.1 <= t < HEARS[0] + 0.6:
            fade = 1 - smoothstep(HEARS[0] - 0.4, HEARS[0] + 0.6, t)
            for tb, xb, wb in zip(brave_t, brave_x, brave_w):
                a = t - tb
                if a >= 0:
                    lv = fade * (0.55 + 0.6 * np.exp(-a / 0.3))
                    fr += light(WHITE if wb else BLUE, (0.9 if wb else 1.2) * lv * np.exp(-((d - xb) / 9.0) ** 2) * left)
        # Judas: gold on Left, flaring on each note he sings; at the head of the charge once the chorus answers
        k = int(np.searchsorted(JUDAS_ON, t, side='right')) - 1
        note = np.exp(-(t - JUDAS_ON[k]) / 0.35) if k >= 0 and t < T_CHORUS + 0.5 else 0.0
        jp = jx if t < HEARS[0] else front - 6
        on = smoothstep(0.0, 0.4, t)
        held = np.exp(-(t - T_LAST_CALL - 4 * EIGHTH) / 1.5) if t >= T_LAST_CALL + 4 * EIGHTH else 0.0
        jl = on * (0.75 + 0.5 * note + 0.3 * held)
        fr += light(GOLD, jl * np.exp(-((d - jp) / 8.0) ** 2) + 0.3 * jl * np.exp(-((d - jp) / 30.0) ** 2))
        fr += light(CORE, 0.6 * jl * np.exp(-((d - jp) / 3.0) ** 2))
        # the fanfares: gold rays running out from Judas along Left on each half bar
        for b in FANFARE:
            for h in (0, 1):
                a = t - (BAR[b] + 3 * EIGHTH * h)
                if 0 <= a < 1.2:
                    r = 220 * a
                    ray = np.exp(-((np.abs(d - jx) - r) / 14.0) ** 2) * left
                    fr += light(GOLD, 0.6 * np.exp(-a / 0.6) * ray)
        # his last call, held: a flare the length of Left
        a = t - T_LAST_CALL - 6 * EIGHTH
        if 0 <= a < 2.5:
            fr += light(GOLD, 0.55 * np.exp(-a / 0.9) * smoothstep(l0, l0 + 30, d) * left)
        # the clashes at the front: a white flash, sparks thrown both ways
        if t >= T_MEET - 0.05:
            mx = front + 7
            for s in STROKES + [T_MEET]:
                a = t - s
                if 0 <= a < 0.8:
                    fr += light(WHITE, 0.95 * np.exp(-a / 0.12) * np.exp(-((d - mx) / 6.0) ** 2))
                    sp = 90 * a
                    fr += light(TIP, 0.6 * np.exp(-a / 0.25) * (np.exp(-((d - mx - sp) / 4.0) ** 2)
                                                               + np.exp(-((d - mx + sp) / 4.0) ** 2)))
        # the close: the people's blue and white everywhere, and the last seconds settle into JM10's first frame
        if t >= T_FALL:
            hold = smoothstep(T_FALL, T_CLOSE, t)
            band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
            fr += light(BLUE, 0.25 * hold * band * (1 - temple)) + light(WHITE, 0.2 * hold * (1 - band) * (1 - temple))
        settle = smoothstep(END - 3.2, END - 0.05, t)
        if settle > 0:
            fr = (1 - settle) * np.clip(fr, 0, 1) + settle * last
        carry = 1 - smoothstep(0.0, 2.5, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * first
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Judas on trumpets and a horn from Left; the orchestra's fanfares on strings, trumpets and timpani; the chorus on
    strings with oboes and bassoons doubling, sopranos and altos from Left, tenors and basses from Right, trumpets on
    the sopranos in the last page, the orchestra's repeated chords under it; a harpsichord continuo. Hoofbeats from the
    road from Antioch as the armies come in, a clash of steel at the front on every stroke."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    jpan = pan_at(l0 + 0.62 * (l1 - l0))
    o = Orchestra(M, level=2.0)
    o.effects([(0.0, -16.0), (BAR[2], -12.0), (T_CHORUS, -14.0), (T_MEET, -9.0), (T_FALL + 1.0, -12.0)])
    for t, dur, m, v, h, who in JUDAS:
        o.play('trumpets', m, t, dur * 0.95, 82 + 0.2 * v, jpan, 0.75)
        o.play('horns', m, t, dur * 0.95, 70 + 0.2 * v, jpan, 0.35)
    chorus_parts = {'S': [('violins', 0, 0, 0.5), ('oboes', 0, -8, 0.28)],
                    'A': [('violins', 0, -4, 0.35), ('violas', 0, -2, 0.35)],
                    'T': [('violas', 0, -2, 0.45), ('bassoons', 0, -8, 0.25)],
                    'B': [('cellos', 0, -2, 0.5), ('bassoons', 0, -6, 0.3)]}
    side = {'S': pan_at(sum(span(G, 'Left')) / 2), 'A': pan_at(sum(span(G, 'Porch Left')) / 2),
            'T': pan_at(sum(span(G, 'Porch Right')) / 2), 'B': pan_at(sum(span(G, 'Right')) / 2)}
    for t, dur, m, v, h, who in CHORUS:
        for sec, tr, dv, g in chorus_parts[who]:
            o.play(sec, m + tr, t, dur * 0.95, 66 + 0.35 * v + dv, 0.55 * side[who], g)
        if who == 'S' and t >= T_IF - 0.01:
            o.play('trumpets', m, t, dur * 0.9, 72 + 0.3 * v, -0.1, 0.4)
        if who == 'B':
            o.play('basses', m - 12 if m >= 50 else m, t, dur * 0.95, 62 + 0.3 * v, 0.0, 0.35)
    # the orchestra: its chords on strings (the fanfares with trumpets), its bass on cellos and basses
    for t, dur, m, v, h, who in ORCH:
        loud = v >= 100
        if h == 0:
            sec = 'violins' if m >= 62 else 'violas'
            o.play(sec, m, t, max(dur * 0.8, 0.18), 58 + 0.3 * v, None, 0.3)
            if loud and m >= 62:
                o.play('trumpets', m, t, max(dur * 0.8, 0.18), 50 + 0.4 * v, 0.1, 0.22)
        else:
            o.play('cellos', m if m >= 36 else m + 12, t, max(dur * 0.85, 0.2), 60 + 0.3 * v, None, 0.4)
            if m < 48:
                o.play('basses', m + 12 if m < 28 else m, t, max(dur * 0.85, 0.2), 56 + 0.3 * v, None, 0.3)
    # under the chorus, the orchestra's repeated quavers: the sounding chord on short strings, every quaver
    t = T_WE
    while t < BAR[44] - 0.01:
        snd = sorted({n[2] for n in CHORUS if n[0] <= t + 0.01 < n[0] + n[1] + EIGHTH * 2.5})
        if snd:
            for m in snd[-3:]:
                o.play('violins' if m >= 62 else 'violas', m, t, 0.18, 70, None, 0.14)
        t += EIGHTH
    # the continuo: a harpsichord on the accompaniment's bass and the chorus's basses with the inner voices
    cont = [(t, m, int(min(100, 56 + 0.35 * v)), min(dur, 0.3)) for t, dur, m, v, h, who in ORCH if h == 1]
    for t, dur, m, v, h, who in JUDAS:
        cont.append((t, m - 12, 64, min(dur, 0.3)))
    for t, dur, m, v, h, who in CHORUS:
        if who == 'B':
            cont.append((t, m, 76, min(dur, 0.3)))
            for cm in sorted({n[2] for n in CHORUS if abs(n[0] - t) < 0.02 and n[5] in ('A', 'T')}):
                cont.append((t, cm, 66, min(dur, 0.3)))
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, END + 2.0), 0.0, 0.4, 0.0)
    # timpani: the fanfares' downbeats, the chorus's strokes, a roll into the last chord
    for b in FANFARE + [8, 16, 44, 45, 46]:
        o.hit('timpani', BAR[b], 104, pitch=0, gain=0.32, pan=0.15)
        o.hit('timpani', BAR[b] + 3 * EIGHTH, 92, pitch=-5, gain=0.25, pan=0.15)
    for s in STROKES:
        o.hit('timpani', s, 96, pitch=0 if int(s / BARLEN) % 2 else -5, gain=0.22, pan=0.15)
    # the last chord held under the settling: strings, horns and trumpets
    for m, sec, g in ((38, 'basses', 0.4), (50, 'cellos', 0.45), (57, 'violas', 0.4), (62, 'violins', 0.4),
                      (66, 'violins', 0.35), (69, 'violins', 0.3), (62, 'horns', 0.3), (69, 'trumpets', 0.25)):
        o.play(sec, m, BAR[47], END - BAR[47] - 0.3, 84, None, g)
    o.hit('timpani roll', BAR[46], 100, pitch=0, gain=0.3, pan=0.15)
    o.hit('timpani roll', BAR[47] + 0.1, 90, pitch=0, gain=0.22, pan=0.15)
    o.hit('timpani', BAR[47], 112, pitch=0, gain=0.4, pan=0.15)
    # the armies coming in on the road from Antioch: hoofbeats from the free end of Right, nearer as they come
    o.gallop(BAR[2], T_MEET, beat=0.44, pan=lambda tt: pan_at(enemy(G, tt) + 40), v=92, gain=0.7)
    # steel at the front: a clash on every stroke, where the colours meet
    for s in [T_MEET] + STROKES:
        o.clash(s + 0.02, pan=pan_at(enemy(G, s)), v=112, gain=0.6)
