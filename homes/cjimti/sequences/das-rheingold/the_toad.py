"""The Toad: down in Nibelheim, among the red-orange glow of the forges, Loge flickers round Alberich and
needles him (the flickering fire, Donington 20a, on piccolo): a serpent is all very well, but could the helmet
make him something small? Alberich, puffed up, puts the helmet Mime forged back on. The Tarnhelm's two chords
(Donington 18) sound on muted horns, a violet-grey shimmer closes round him and his red drains into a hole of
darkness in the cavern's glow, until, plip, a tiny dull-green light sits where he stood.

The toad hops about the middle of Porch Front, over and around the glowing hoard: every hop a bassoon leap and
a clarinet bounce that climbs as it hops right and sinks as it hops left, a little splash of green on every
landing, and now and then a croak. Wotan creeps in from Porch Left on pizzicato tiptoe. Then his foot comes
down: a blue slam, tubas, trombones, timpani and cymbal, a blue shockwave over the whole house. Loge darts in
and snatches the helmet (a violet streak to his hand, where it stays), and Alberich pops back to his own shape,
caught: the house flashes red, the Ring motif (Donington 8) blares in the brass, and Loge whirls round him as
steel-blue bindings wind in tighter and tighter over his red, to a rising chromatic rope in the strings.

He struggles six times (a red jolt through the porch each time, timpani and a trombone grunt) while Loge
laughs, until Wotan's spear motif (Donington 73) strides down in the trombones and a steel line steps out from
Wotan across the porch with each note. Then they haul him off. The ascent begins: the Nibelung rhythm starts up
in the strings, stripes of forge glow run down and away from the porch, and the first anvils ring out across
the house, hand over hand toward the climb.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG17'
TITLE = 'The Toad'
KIND = 'show'
DESCRIPTION = ('Loge dares Alberich to make himself small, and the helmet turns him into a tiny hopping toad. '
               'Wotan puts his foot on it, Loge grabs the helmet, and Alberich is caught and tied up tight. '
               'Then they drag him up out of the dark.')
VOICEOVER = ('A giant serpent is very impressive. But could you make yourself small? '
             'Alberich, never one to turn down a chance to show off, falls right into it.')

BEAT = 0.5                                  # a quarter note
TAUNT = [2.5, 4.6]                          # Loge's flicker: could you make yourself small?
T_BOAST = 7.0                               # Alberich: watch this!
T_HELM = 9.5                                # the helmet on: the Tarnhelm's chords
HB = 0.45                                   # their beat
T_TOAD = 17.0                               # plip
HOPS = [(18.2, 0.56), (19.3, 0.61), (20.1, 0.55), (21.6, 0.48), (22.4, 0.43), (24.0, 0.5), (25.1, 0.57),
        (25.9, 0.63), (27.4, 0.56), (28.2, 0.5), (29.7, 0.44), (30.8, 0.49), (32.2, 0.46)]
HOP = 0.32                                  # seconds in the air
CROAKS = [21.0, 23.3, 26.7, 31.5]
T_CREEP = 18.0                              # Wotan tiptoes in
T_SLAM = 34.0                               # his foot comes down
T_SNATCH = 35.5                             # Loge takes the helmet
T_POP = 37.0                                # Alberich back in his own shape, caught
T_BOUND = 41.0                              # the last knot
JOLTS = [42.0, 43.5, 44.8, 46.3, 47.5, 49.2]
LAUGHS = [44.2, 48.4]
T_SPEAR = 51.5                              # Wotan's spear: the treaty's authority
SB = 0.55
T_HAUL = 59.0                               # they drag him off
T_ASCENT = 63.0                             # the Nibelung rhythm starts: up and out
NB = 0.45                                   # a dotted-quarter beat of the 9/8
T_ANVILS = 70.0
D = 80.0

CAVE = hexc('#b01c00')
EMBER = hexc('#ff5a10')
FORGE = hexc('#ff7a10')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
TOAD = hexc('#6a8a10')
STEEL = hexc('#5a88d0')
WHITE = hexc('#ffffff')

NIB = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
       ('Gb4', 'F4', 'Gb4'), ('F4', 'E4', 'F4'), ('Db4', 'C4', 'Bb3')]    # the Nibelung rhythm: two bars of 9/8
NANVIL = 18


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def nibelung(t0, t1, beat, v0, v1, tr=0):
    """The Nibelung rhythm from t0 to t1: each dotted-quarter beat long-short-long (dotted eighth, sixteenth,
    eighth) -> [(t, seconds, midi, velocity, beat index, j)]."""
    out, k = [], 0
    while t0 + k * beat < t1:
        for j, (off, dur) in enumerate(((0, 0.5), (0.5, 1 / 6), (2 / 3, 1 / 3))):
            t = t0 + (k + off) * beat
            u = (t - t0) / max(t1 - t0, 1e-6)
            out.append((t, dur * beat * 0.85, note(NIB[k % 6][j]) + tr, int(v0 + (v1 - v0) * u), k, j))
        k += 1
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    rng = np.random.default_rng(17)
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_HELM + 1.0, 'Bb1', 64, 'cave')
    for t0 in TAUNT:
        for t, m, v, d in play('loge_flicker', t0, 0.22, 0, 92):
            add(t, d, m, v, 'loge')
    for b, d, m in ((0, .5, 'Bb2'), (.5, .5, 'F3'), (1, 1, 'Bb3'), (2, .5, 'Db4'), (2.5, 1.5, 'Bb3')):
        add(T_BOAST + b * BEAT, d * BEAT, m, 100, 'boast')
    for t, m, v, d in play('tarnhelm', T_HELM, HB, 0, 70):
        if t < T_HELM + 16 * HB:
            add(t, d, m, v, 'tarnhelm')
    add(T_HELM + 2.0, T_TOAD - T_HELM - 2.0, 'Eb6', 50, 'glass')
    add(T_TOAD, 0.15, 'Bb6', 96, 'plip')
    add(T_TOAD + 0.08, 0.3, 'F5', 90, 'plipm')

    prev = 0.5
    for th, u in HOPS:                                      # each hop: pitch follows where it lands
        m = note('Bb2') + int(round((u - 0.43) * 40))
        add(th, 0.1, m, 96, 'hop')
        add(th + 0.12, 0.1, m + (7 if u > prev else 5) + 12, 90, 'bounce')
        add(th + HOP, 0.12, m - 5, 88, 'land')
        prev = u
    for tc in CROAKS:
        add(tc, 0.09, 'Bb1', 100, 'croak')
        add(tc + 0.14, 0.09, 'Bb1', 92, 'croak')
    for k in range(int((T_SLAM - 0.5 - T_CREEP) / 0.75)):   # Wotan on tiptoe
        add(T_CREEP + 0.75 * k, 0.2, ('F2', 'Bb2', 'Db3', 'C3')[k % 4], 60 + 2 * k, 'tiptoe')
    for m in ('Bb1', 'Bb2', 'F3', 'Bb3', 'D4', 'F4'):
        add(T_SLAM, 1.4, m, 124, 'slam')
    add(T_SLAM, 1.0, 'Bb1', 127, 'boom')
    for j in range(10):
        add(T_SNATCH - 0.15 + j * 0.03, 0.08, note('Bb5') + (0, 2, 4, 5, 7, 9, 11, 12, 14, 16)[j], 100, 'snatch')
    add(T_SNATCH + 0.25, 0.6, 'Eb5', 80, 'snatchtarn')

    add(T_POP, 1.6, 'Bb1', 127, 'pop')
    for m in ('B2', 'Gb3', 'B3', 'Gb4'):                    # the Tarnhelm's last chord, torn open
        add(T_POP, 1.2, m, 118, 'popchord')
    add(T_POP + 0.1, 1.4, 'G4', 120, 'scream')
    for t, m, v, d in play('ring', T_POP + 0.6, 0.38, 0, 116):
        add(t, d, m, v, 'ringbrass')
    for k in range(24):                                     # the rope, wound tighter
        add(T_POP + 0.5 + k * (T_BOUND - T_POP - 0.5) / 24, 0.12, note('Bb2') + k, 80 + k, 'rope')
    add(T_POP + 0.5, T_BOUND - T_POP - 0.5, 'Bb2', 80, 'snare')
    for m in ('Bb1', 'F2', 'Bb2', 'Db3', 'F3'):
        add(T_BOUND, 0.9, m, 112, 'knot')

    for k in range(int((T_SPEAR - 0.5 - T_BOUND) / (BEAT / 2))):      # his struggling, in B flat minor
        m = ('Bb1', 'Bb1', 'Db2', 'Bb1', 'F1', 'Bb1', 'Gb1', 'F1')[k % 8]
        add(T_BOUND + k * BEAT / 2, BEAT / 2 * 0.8, m, 88 + 8 * (k % 4 == 0), 'drive')
    for i, tj in enumerate(JOLTS):
        add(tj, 0.5, ('Bb2', 'Db3', 'C3', 'Eb3', 'Db3', 'F3')[i], 108, 'grunt')
        add(tj, 0.6, 'Bb1', 112, 'jolt')
    for tl in LAUGHS:
        for j, (hi, lo) in enumerate((('Db6', 'Bb5'), ('C6', 'A5'), ('Bb5', 'Gb5'), ('A5', 'F5'))):
            for k, m in enumerate((hi, lo)):
                add(tl + j * 0.18 + k * 0.09, 0.08, m, 98 - 4 * j, 'laugh')
    for t, m, v, d in play('spear', T_SPEAR, SB, 0, 112):
        add(t, d, m, v, 'spear')
    for m in ('Bb1', 'F2', 'Bb2'):
        add(T_SPEAR, 10 * SB, m, 80, 'spearpad')
    for b, d, m in ((0, 1.5, 'Db3'), (1.5, 1, 'C3'), (2.5, 1.5, 'Bb2'), (4, 3, 'A2')):
        add(T_HAUL + b * BEAT, d * BEAT, m, 90, 'woe')

    for t, d, m, v, k, j in nibelung(T_ASCENT, D, NB, 64, 112):   # the climb begins
        add(t, d, m, v, 'nib')
        if j == 0:
            add(t, d, m - 24, v - 6, 'nibbass')
        if t >= T_ANVILS:
            u = (t - T_ANVILS) / (D - T_ANVILS)
            n = int(1 + 5 * u ** 1.3) if j != 1 else int(4 * u)
            for a in rng.choice(NANVIL, size=n, replace=False):
                add(t, 0.1, 0, int(70 + 40 * u), 'anvil', int(a))
    add(T_ASCENT, D - T_ASCENT, 'Bb1', 60, 'climb')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def toad_track(G, t):
    """The toad's path distance at times t: still between hops, a quick eased hop to each landing."""
    p = np.full_like(t, at(G, 'Porch Front', 0.5))
    prev = at(G, 'Porch Front', 0.5)
    for th, u in HOPS:
        q = at(G, 'Porch Front', u)
        m = t >= th
        p[m] = prev + (q - prev) * smoothstep(th, th + HOP, t[m])
        prev = q
    return p


def choreography(G):
    """Per frame: Alberich (or the toad), Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    ALB_, WOT, LOG = 0, 1, 2
    toad = toad_track(G, t)
    pT = at(G, 'Porch Front', HOPS[-1][1])
    set_(ALB_, 0, D, at(G, 'Porch Front', 0.5), 4.0)
    set_(ALB_, T_POP, T_HAUL, pT + 6 * np.sin(2 * np.pi * t / 2.3), 6.0)
    set_(ALB_, T_HAUL, D, at(G, 'Porch Front', 0.2), 0.9)
    wob = 6 * np.sin(2 * np.pi * t / 3.1)
    set_(WOT, 0, D, at(G, 'Porch Left', 0.7) + wob, 2.0)
    for k, s in enumerate(np.arange(T_CREEP, T_SLAM - 0.6, 0.75)):   # tiptoe steps
        u = (k + 1) / len(np.arange(T_CREEP, T_SLAM - 0.6, 0.75))
        set_(WOT, s, D, at(G, 'Porch Left', 0.7) + (at(G, 'Porch Front', 0.3) - at(G, 'Porch Left', 0.7)) * u, 7.0)
    set_(WOT, T_SLAM - 0.2, T_POP, pT, 18.0)
    set_(WOT, T_POP, T_HAUL, pT + 45, 5.0)
    set_(WOT, T_HAUL, D, at(G, 'Porch Front', 0.4) + wob, 0.9)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(LOG, 0, D, at(G, 'Porch Front', 0.25) + jit, 4.0)
    for t0 in TAUNT:                                        # darting round Alberich as he needles him
        set_(LOG, t0, t0 + 1.8, at(G, 'Porch Front', 0.5) - 40 + 30 * np.sin(2 * np.pi * (t - t0) / 0.9), 9.0)
    set_(LOG, T_SNATCH - 0.3, T_SNATCH + 0.2, pT - 12, 18.0)
    set_(LOG, T_SNATCH + 0.2, T_POP + 0.4, at(G, 'Porch Front', 0.3) + jit, 14.0)
    set_(LOG, T_POP + 0.4, T_BOUND, pT + 70 * np.sin(2 * np.pi * (t - T_POP) / 0.9), 18.0)   # winding the rope
    set_(LOG, T_BOUND, T_HAUL, pT - 60 + jit, 6.0)
    set_(LOG, T_HAUL, D, at(G, 'Porch Front', 0.75) + jit, 0.9)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    m = (t >= T_TOAD) & (t < T_POP)
    pos[0][m] = toad[m]                                     # the toad hops exactly
    m = (t >= T_POP) & (t < T_POP + 1.0)
    pos[0][m] = pT
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def anvil_spots(G):
    """Where the eighteen anvils ring: spread over every run of the house."""
    L = G.length
    return np.linspace(0.04 * L, 0.97 * L, NANVIL)[np.random.default_rng(5).permutation(NANVIL)]


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    ph = at(G, 'Porch Front', 0.65)
    C = choreography(G)
    N = compose()
    hops = np.array([th for th, _ in HOPS])
    jolts = np.array(JOLTS)
    spear = [e[0] for e in N if e[4] == 'spear']
    nibs = np.array([e[0] for e in N if e[4] == 'nib' and e[5] is None])
    anvils = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    spots = anvil_spots(G)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    spark = np.zeros(G.N)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]

        # the cavern: a red-orange glow that breathes, forge sparks; in the ascent stripes run down and away
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 320 - 0.07 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 130 + 0.21 * t) + 1)
        asc = smoothstep(T_ASCENT - 1, T_ASCENT + 6, t)
        helm = smoothstep(T_HELM + 1.5, T_TOAD - 0.5, t) * (1 - smoothstep(T_TOAD, T_TOAD + 0.4, t))
        hole = helm * np.exp(-((d - ap) / 60) ** 2)
        bed = (0.27 + 0.1 * w1) * (1 - 0.9 * hole)
        fr += light(CAVE, bed) + light(EMBER, (0.05 + 0.14 * w1 * w2) * (1 - hole))
        if asc > 0:
            ni = int(np.searchsorted(nibs, t, side='right')) - 1
            beatp = np.exp(-(t - nibs[ni]) / 0.12) if ni >= 0 else 0.0
            stripe = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - pf) / 170 - 0.9 * (t - T_ASCENT)))) ** 3
            fr += light(FORGE, asc * (0.28 + 0.12 * beatp) * stripe)
        spark *= np.exp(-DT / 0.12)
        spark[rng.random(G.N) < 0.004 + 0.01 * asc] = 1.0
        fr += light(FORGE, 0.75 * spark)
        for ta, a, v in anvils:                             # the anvils, each a white-hot burst where it rings
            if ta <= t < ta + 0.5:
                fr += light(HOT, (v / 110) * np.exp(-(t - ta) / 0.09) * blob(spots[a], 16))
                fr += light(FORGE, 0.7 * (v / 110) * np.exp(-(t - ta) / 0.25) * blob(spots[a], 45))

        # the hoard beside him
        fr += light(GOLD, 0.62 * blob(ph, 30) + 0.2 * blob(ph, 80))
        fr += light(HOT, 0.45 * blob(ph, 14) * (0.6 + 0.4 * tw(t)) * (tw(t) > 0.3))

        # Loge: a restless flicker, brighter as he needles; the helmet's violet in his hand once he has it
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        tease = sum(smoothstep(t0, t0 + 0.2, t) * (1 - smoothstep(t0 + 1.6, t0 + 2.0, t)) for t0 in TAUNT)
        lb = blob(lp, 22 + 6 * tease)
        fr += light(LOGE1, (0.7 + 0.2 * tease) * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, (0.55 + 0.35 * tease) * lb * fk)
        held = smoothstep(T_SNATCH + 0.15, T_SNATCH + 0.4, t)
        if held > 0:
            fr += light(TARN, 0.6 * held * blob(lp, 34) * (0.7 + 0.3 * tw(t)))
        if T_POP + 0.4 <= t < T_BOUND:                      # his flame trailing as he winds the rope
            for j, lag in enumerate(range(2, 14, 2)):
                q = C['loge'][max(f - lag, 0)]
                fr += light(LOGE2, 0.45 * (1 - j / 6.5) * blob(q, 18))

        # Wotan: deep blue, a step at a time
        fr += light(WOTAN, 0.85 * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(SPEAR, 0.25 * blob(wp, 7))

        # Alberich: red with the ring's gold point and red glint; the helmet, the toad, the capture
        alb = 1 - smoothstep(T_HELM + 1.0, T_TOAD - 1.0, t)
        back = smoothstep(T_POP, T_POP + 0.1, t)
        vis = max(alb, back)
        if vis > 0:
            fr += light(MUD, 0.32 * vis * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, 0.75 * vis * blob(ap, 24) * (1 + 0.2 * smoulder(t)))
            fr += light(GOLD, 0.9 * vis * blob(ap, 6)) + light(RED, 0.7 * vis * blob(ap + 9, 6) * (0.6 + 0.4 * tw(t)))
        if T_HELM <= t < T_TOAD + 0.4:                      # the shimmer closing in round him
            r = 80 - 30 * smoothstep(T_HELM, T_TOAD, t)
            edge = np.exp(-((np.abs(d - ap) - r) / 14) ** 2)
            fr += light(TARN, 0.85 * smoothstep(T_HELM, T_HELM + 1.5, t) * (1 - smoothstep(T_TOAD, T_TOAD + 0.4, t))
                        * edge * (0.6 + 0.4 * tw(t)))
        if T_TOAD <= t < T_POP:                             # the toad
            i = int(np.searchsorted(hops, t, side='right')) - 1
            air = (i >= 0) and (t - hops[i] < HOP)
            land = np.exp(-(t - hops[i] - HOP) / 0.15) if i >= 0 and t >= hops[i] + HOP else 0.0
            pinned = smoothstep(T_SLAM, T_SLAM + 0.05, t)
            b = (0.8 + 0.25 * air + 0.3 * land) * (1 - 0.5 * pinned * (tw(t)[0] > 0))
            if t < T_TOAD + 0.3:
                fr += light(WHITE, 0.8 * np.exp(-(t - T_TOAD) / 0.1) * blob(ap, 14))
            fr += light(TOAD, b * blob(ap, 9 + 5 * air) + 0.25 * blob(ap, 30))
            fr += light(TARN, 0.35 * (1 - smoothstep(T_SNATCH, T_SNATCH + 0.2, t)) * blob(ap, 26))
            if air:
                q = C['alb'][max(f - 4, 0)]
                fr += light(TOAD, 0.5 * blob(q, 12))
            if land > 0.05:
                rr = 12 + 40 * (1 - land)
                fr += light(TOAD, 0.6 * land * np.exp(-((np.abs(d - ap) - rr) / 8) ** 2))
            for tc in CROAKS:
                if tc <= t < tc + 0.5:
                    fr += light(TOAD, 0.5 * np.exp(-(t - tc) / 0.15) * blob(ap, 40))

        # the slam: blue on the toad, a shockwave out over the whole house
        if T_SLAM <= t < T_SLAM + 2.0:
            a = t - T_SLAM
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.4) * np.ones(G.N))
            fr += light(WHITE, 0.8 * np.exp(-a / 0.08) * blob(wp, 40))
            rr = 1400 * a ** 0.7
            fr += light(SPEAR, 0.7 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - wp) - rr) / 60) ** 2))
        if T_SNATCH - 0.2 <= t < T_SNATCH + 0.6:            # the helmet snatched: a violet streak
            a = t - (T_SNATCH - 0.2)
            for j, lag in enumerate(range(0, 12, 2)):
                q = C['loge'][max(f - lag, 0)]
                fr += light(TARN, 1.0 * (1 - j / 6.5) * (1 - a / 0.8) * blob(q, 16))

        # caught: a red burst, the bindings wound in, the struggle
        if T_POP <= t < T_POP + 2.0:
            a = t - T_POP
            fr += light(ALB, 0.9 * np.exp(-a / 0.35) * np.ones(G.N))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.1) * blob(ap, 50))
            rr = 1500 * a ** 0.6
            fr += light(RED, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - ap) - rr) / 70) ** 2))
        if t >= T_POP + 0.4:
            u = smoothstep(T_POP + 0.4, T_BOUND, t)
            if t < T_BOUND + 0.5:                           # the rope winds in round him
                R = 260 * (1 - u) + 30
                th = 2 * np.pi * (np.arange(6) / 6 + 1.1 * (t - T_POP))
                q, depth = ap + R * np.cos(th), np.sin(th)
                g = np.exp(-((d[:, None] - q[None, :]) / 14) ** 2) * (0.5 + 0.5 * depth)[None, :]
                fr += light(STEEL, 0.9 * (1 - smoothstep(T_BOUND, T_BOUND + 0.5, t)) * g.max(axis=1))
            j = int(np.searchsorted(jolts, t, side='right')) - 1
            jolt = np.exp(-(t - jolts[j]) / 0.25) if j >= 0 and t - jolts[j] < 1.5 else 0.0
            wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
            fr += light(STEEL, (0.3 + 0.55 * u + 0.4 * jolt) * wrap)
            fr += light(ALB, 0.5 * jolt * blob(ap, 60))
            if jolt > 0.05:
                porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
                fr += light(ALB, 0.4 * jolt * porch)
            if T_BOUND <= t < T_BOUND + 0.8:
                fr += light(STEEL, 0.7 * np.exp(-(t - T_BOUND) / 0.2) * blob(ap, 70))

        # the spear: a steel line steps out from Wotan across the porch with each note
        for i, ts in enumerate(spear):
            if ts <= t < T_SPEAR + 12 * SB + 1.5:
                reach = 30 * (i + 1)
                fade = np.exp(-(t - ts) / 0.4)
                line = smoothstep(reach + 10, reach - 10, np.abs(d - wp)) * (np.abs(d - wp) > reach - 30)
                fr += light(SPEAR, (0.25 + 0.6 * fade) * line * (1 - smoothstep(T_SPEAR + 10 * SB, T_SPEAR + 12 * SB + 1.5, t)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    spots = anvil_spots(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C[k]))

    for name, gain, rev in (('winds', 0.2, 0.3), ('strings', 0.13, 0.3), ('low', 0.19, 0.15), ('brass', 0.17, 0.28),
                            ('perc', 0.2, 0.22), ('anvil', 0.18, 0.25), ('harp', 0.16, 0.4), ('fx', 0.08, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flst = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    snare = M.hits('Percussion/Snare2-rollNS_v3*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    pitch = np.random.default_rng(3).uniform(-7, 5, NANVIL)
    for t, d, m, v, part, who in compose():
        pa = pan_of('alb', t)
        if part == 'cave':
            hold('low', trem, m + 12, t, t + d, v, -0.1, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'loge':
            M.add('winds', pic.play(m, v), t, 0.9, pan_of('loge', t))
            M.add('strings', vn.play(m - 12, v - 15), t, 0.5, pan_of('loge', t))
        elif part == 'boast':
            M.add('brass', tbn.play(m, v, dur=d, release=0.15), t, 0.9, pa)
            M.add('low', bsus.play(m - 12, v - 10, dur=d, release=0.15), t, 0.6, pa)
        elif part == 'tarnhelm':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.8, pa)
        elif part == 'glass':
            hold('strings', vtrem, m - 12, t, t + d, v, pa, rise=2.0, fall=0.4, gain=0.35)
        elif part == 'plip':
            M.add('winds', pic.play(m - 12, v), t, 1.0, pa)
        elif part == 'plipm':
            M.add('harp', mar.play(m, v), t, 1.0, pa)
        elif part in ('hop', 'land'):
            M.add('winds', bsn.play(m, v), t, 1.0, pa)
            if part == 'land':
                M.add('low', pizz.play(m + 12, v - 10), t, 0.6, pa)
        elif part == 'bounce':
            M.add('winds', cl.play(m, v), t, 0.9, pa)
        elif part == 'croak':
            M.add('winds', bsn.play(m, v), t, 1.1, pa)
            M.add('low', cbs.play(m + 12, v - 10), t, 0.6, pa)
        elif part == 'tiptoe':
            M.add('low', pizz.play(m + 12, v), t, 0.9, pan_of('wot', t))
        elif part == 'slam':
            s = tuba if m < note('F2') else tbn if m < note('Bb3') else horn
            M.add('brass', s.play(m, v, dur=d, release=0.4), t, 1.0, pan_of('wot', t))
        elif part == 'boom':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, pan_of('wot', t))
            M.add('perc', bd.play(v), t, 0.9, pan_of('wot', t))
            M.add('perc', crash.play(118), t, 0.8, 0.0)
            M.add('fx', whoosh(0.5, 4000, 400, 0.6, seed=4), t - 0.4, 0.8, pan_of('wot', t))
        elif part == 'snatch':
            M.add('winds', pic.play(m - 12, v), t, 0.8, pan_of('loge', t))
            M.add('harp', harp.play(m - 24, v), t, 0.8, pan_of('loge', t))
        elif part == 'snatchtarn':
            M.add('brass', mute.play(m - 12, v, dur=d, release=0.4), t, 0.7, pan_of('loge', t))
        elif part == 'pop':
            M.add('perc', timp.play(v, pitch=-2), t, 1.0, pa)
            M.add('perc', crash.play(124), t, 1.0, pa)
            M.add('perc', bd.play(v), t, 0.8, pa)
        elif part == 'popchord':
            M.add('brass', (tbn if m < note('B3') else horn).play(m, v, dur=d, release=0.3), t, 0.9, pa)
        elif part == 'scream':
            M.add('brass', tbn.play(m - 12, v, dur=d, release=0.3), t, 1.0, pa)
            hold('strings', vtrem, m + 5, t, t + d, v, pa, rise=0.05, fall=0.4, gain=0.6)
        elif part == 'ringbrass':
            if m >= note('E4'):
                M.add('brass', tpt.play(m, v, dur=d, release=0.3), t, 0.8, pa + 0.15)
            elif m >= note('C3'):
                M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.8, pa - 0.15)
            else:
                M.add('low', tuba.play(m, v, dur=d, release=0.3), t, 0.9, 0.0)
        elif part == 'rope':
            M.add('strings', vcs.play(m, v), t, 0.8, pan_of('loge', t))
            M.add('strings', vas.play(m + 12, v - 10), t, 0.5, pan_of('loge', t))
        elif part == 'snare':
            M.add('perc', snare.play(v, dur=d), t, 0.5, pa)
        elif part == 'knot':
            M.add('brass', (tuba if m < note('Bb2') else tbn).play(m, v, dur=d, release=0.3), t, 0.9, pa)
            if m == note('Bb1'):
                M.add('perc', timp.play(v, pitch=-4), t, 0.9, pa)
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.8, pa - 0.2)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, pa + 0.2)
        elif part == 'grunt':
            M.add('brass', tbn.play(m, v, dur=d, release=0.15), t, 0.9, pa)
        elif part == 'jolt':
            M.add('perc', timp.play(v, pitch=-6), t, 0.9, pa)
        elif part == 'laugh':
            M.add('winds', (pic if m >= note('Ab5') else flst).play(m, v), t, 0.9, pan_of('loge', t))
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, pan_of('wot', t))
            M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.3), t, 0.8, pan_of('wot', t))
        elif part == 'spearpad':
            hold('low', vc, m + 12, t, t + d, v, 0.0, rise=0.5, fall=1.5, gain=0.5)
        elif part == 'woe':
            M.add('low', bsus.play(m, v, dur=d, release=0.2), t, 1.0, pa)
        elif part == 'nib':
            M.add('strings', vas.play(m, v), t, 1.1, -0.3)
            M.add('strings', vn.play(m + 12, v - 20), t, 0.7, 0.3)
        elif part == 'nibbass':
            M.add('low', cbs.play(m + 12, v), t, 1.0, 0.0)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.8, 0.0)
        elif part == 'anvil':
            M.add('anvil', anvil.play(v, pitch=pitch[who]), t, 1.0, pan_at(spots[who]))
        elif part == 'climb':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=6.0, fall=0.3, gain=1.0)
