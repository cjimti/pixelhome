"""Rheingold!: sunlight finds its way down through the river. Motes of it drift in from every run of the house
to the rock at the back of the porch while the violins shimmer in C, and the gold wakes to its own call
(Donington 44), first on a muted horn, then an open one, each note a pulse of gold that grows. Alberich, on
Porch Left, catches glints of it. Trumpets take up the call and the gold floods the porch; its reflections
start to glitter on the water everywhere.

The Rhinemaidens gather round it and break into their jubilation: "Heiajaheia!" in three parts, and then the
cry "Rheingold! Rheingold!" (Donington 31), where each yearning chord sends a sweep of gold out from the rock
to both ends of the house and each resolution flashes the whole roof gold, twice, the second time with
cymbals and sparks. They dance round the gold, swinging wide over the wings, until Alberich asks what it is.

Wellgunde lets the secret out: whoever forges a ring from this gold wins the world. The Ring motif (Donington
8) sounds in the woodwinds and the gold draws in to a hard point with a ring of beads circling it, bright gold
where it turns toward the street and dull red where it turns away. Woglinde adds the condition, the
Renunciation of Love (Donington 76): only one who gives up love can forge it. A cold indigo shadow drains in
from both ends of the house while it sounds, under trombones. The maidens laugh it off (who would ever give up
love?) but Alberich has heard. As the renunciation rises once more in the bassoons he creeps along the porch
toward the gold, his red reaching out ahead of him, the maidens frozen on the far side, and the Ring motif
stirs one last time on a muted horn.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG04'
TITLE = 'Rheingold!'
KIND = 'show'
DESCRIPTION = ('Sunlight wakes the gold on its rock and the whole house blazes as the Rhinemaidens cry out its '
               'name. Then they let slip its secret: forge a ring from it and the world is yours, if you give up '
               'love. Alberich is listening.')
VOICEOVER = ('The sun reaches the bottom of the river, and on the rock, something wakes. '
             'Watch the gold. And watch who is watching it.')

BEAT = 0.5                                  # a quarter note
GOLD_CALLS = [(2.0, 'mute'), (6.5, 'horn'), (12.0, 'trumpet'), (15.5, 'trumpet')]
T_HEIA = 20.0                               # "Heiajaheia!"
CRIES = [24.0, 30.0]                        # "Rheingold! Rheingold!"
T_DANCE = 34.5
T_ASK = 46.0                                # Alberich: what is it that gleams so?
T_RING = 49.0                               # Wellgunde: whoever forges a ring...
T_RING2 = 55.5
T_RENOUNCE = 61.0                           # Woglinde: only one who renounces love
T_LAUGH = 66.0
T_STARE = 70.0
CREEP = [71.0, 73.0, 75.0, 77.0]
T_STIR = 76.0
D = 80.0

WOG, WELL, FLO = 0, 1, 2
SONG = [(b, d, note(n)) for b, d, n in MOTIFS['rhinemaidens']['notes'] if d >= 0.5]
C_MAJOR = (0, 2, 4, 5, 7, 9, 11)

COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
BEAM = hexc('#fff4c8')
GLINT = hexc('#ffc840')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
SHADOW = hexc('#1c1880')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def third_below(m, scale=C_MAJOR):
    i = scale.index(m % 12)
    return m - ((scale[i] - scale[(i - 2) % 7]) % 12)


def cry_chords(t0):
    """The cry's chords: (time, seconds, [midi], kind). kind: 'yearn' (the B-F-A chord over C, "Rhein-"),
    'res' (its resolution to C major, "-gold!") or 'tail' (the phrase that winds down after)."""
    out, ev = [], {}
    for b, d, n in MOTIFS['rheingold']['notes']:
        ev.setdefault(b, []).append((d, note(n)))
    for b in sorted(ev):
        ms = [m for _, m in ev[b]]
        kind = 'yearn' if note('B4') in ms else 'res' if set(ms) == {note('C5'), note('E5'), note('G5')} else 'tail'
        out.append((t0 + b * BEAT, max(d for d, _ in ev[b]) * BEAT, ms, kind))
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('C5', 'E5', 'G5'):
        add(0.0, CRIES[0] - 0.5, m, 56, 'shimmer')
    add(0.0, T_RING, 'C2', 60, 'pedal')
    for t0, inst in GOLD_CALLS:
        for t, m, v, d in play('gold', t0, BEAT, 5, {'mute': 78, 'horn': 92, 'trumpet': 106}[inst]):
            add(t, d, m + (12 if inst == 'trumpet' and t0 > 15 else 0), v, inst)
            if inst == 'trumpet':
                add(t, d, m - 12, v - 10, 'horn')

    half = [x for x in SONG if x[0] < 6]
    for b, d, m in half:                                    # "Heiajaheia!" in three parts, in C
        add(T_HEIA + b * BEAT * 2 / 3, d * BEAT * 2 / 3, m + 4, 100, 'sing', WOG)
        add(T_HEIA + b * BEAT * 2 / 3, d * BEAT * 2 / 3, third_below(m + 4), 96, 'sing', WELL)
        add(T_HEIA + b * BEAT * 2 / 3, d * BEAT * 2 / 3, m + 4 - 12, 96, 'sing', FLO)
    for k, tc in enumerate(CRIES):
        for t, d, ms, kind in cry_chords(tc):
            top = sorted(ms)[-3:]
            for who, m in zip((FLO, WELL, WOG), top):
                add(t, d, m, 104 + 8 * k, 'sing', who)
            for m in ms:
                add(t, d, m, 100 + 10 * k, 'tutti')
            if kind == 'res':
                add(t, 0.8, 'C2', 116 + 6 * k, 'hit')
        add(tc - 0.9, 0.9, 'C4', 90, 'gliss')
    for k in range(int((T_ASK - T_DANCE) / (3 * BEAT))):    # the dance: the rocking figure, in C
        for j, m in enumerate(('G3', 'C4', 'E4', 'G4', 'E4', 'C4')):
            add(T_DANCE + k * 3 * BEAT + j * BEAT / 2, BEAT * 0.75, m, 72 + 10 * (j == 0), 'rock')
        add(T_DANCE + k * 3 * BEAT, 3 * BEAT, 'C2' if k % 2 == 0 else 'G1', 84, 'bass')
    for b, d, m in SONG:
        add(T_DANCE + b * BEAT, d * BEAT, m + 4, 98, 'sing', WOG)
    for b, d, m in SONG[:12]:
        add(T_DANCE + 6.0 + b * BEAT, d * BEAT, third_below(m + 4), 94, 'sing', WELL)
        add(T_DANCE + 6.0 + b * BEAT, d * BEAT, m + 4 - 12, 94, 'sing', FLO)
    for b, d, m in ((0, .5, 'C3'), (.5, .5, 'Eb3'), (1, 1, 'D3'), (2, .5, 'Bb2'), (2.5, 1.5, 'G2')):
        add(T_ASK + b * BEAT, d * BEAT, m, 96, 'alb')

    ring = play('ring', T_RING, BEAT, 0, 88)                # the Ring, in the woodwinds, over a G pedal
    top = {}
    for t, m, v, d in ring:
        top[t] = max(top.get(t, 0), m)
    for t, m, v, d in ring:                                 # Wellgunde has the top line
        add(t, d, m, v, 'ring' if m > note('C3') else 'ringbass', WELL if m == top[t] else None)
    for t, m, v, d in play('ring_under_eb', T_RING2, BEAT * 0.75, 0, 80):
        add(t, d, m, v, 'ringlow')
    for t, m, v, d in play('renunciation', T_RENOUNCE, BEAT, 0, 100):
        add(t, d, m, v, 'sing', WOG)
    for t, m, v, d in play('renunciation_broad', T_RENOUNCE, BEAT * 0.5, -12, 104):
        add(t, d, m, v, 'renounce')
    add(T_RENOUNCE, T_STARE + 9.0 - T_RENOUNCE, 'C1', 70, 'dark')
    for k, tl in enumerate((T_LAUGH, T_LAUGH + 1.5)):
        for j, (hi, lo) in enumerate((('E6', 'C6'), ('D6', 'B5'), ('C6', 'A5'), ('B5', 'G5'))):
            for m in (hi, lo):
                add(tl + j * 0.18, 0.13, m, 96 - 4 * j, 'laugh', (k + j) % 3)
    add(T_LAUGH + 3.0, 0.5, 'A5', 92, 'sing', WOG)
    add(T_LAUGH + 3.5, 0.75, 'G5', 88, 'sing', WOG)
    for t, m, v, d in play('renunciation_low', T_STARE + 1.0, BEAT * 1.2, -12, 92):
        add(t, d, m, v, 'alb')
    for t, m, v, d in play('ring', T_STIR, BEAT * 1.4, 0, 70):
        if t < D - 1.0 and m > note('C3'):
            add(t, d, m, v, 'stir')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    tgt = np.zeros((4, F))
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    bob = [12 * np.sin(2 * np.pi * t / 1.4 + k) for k in range(3)]
    set_(WOG, 0, D, at(G, 'Porch Right', 0.7) + bob[0], 3.0)
    set_(WELL, 0, D, at(G, 'Left', 0.55) + bob[1], 3.0)
    set_(FLO, 0, D, at(G, 'Right', 0.6) + bob[2], 3.0)
    for k, off in ((WOG, 160), (WELL, -200), (FLO, 280)):
        set_(k, 4.0, CRIES[0], pf + off + bob[k], 0.9)
    for tc in CRIES:                                        # spinning round the gold at each cry
        m = (t >= tc) & (t < tc + 4.3)
        ph = 2 * np.pi * 0.7 * (t - tc)
        for k in range(3):
            set_(k, tc, tc + 4.3, pf + 220 * np.sin(ph + 2 * np.pi * k / 3), 20.0)
    for k, off in ((WOG, 160), (WELL, -200), (FLO, 280)):
        set_(k, CRIES[0] + 4.3, CRIES[1], pf + off + bob[k], 3.0)
    u = np.clip((t - T_DANCE) / (T_RING - T_DANCE), 0, 1)
    r = 220 + 700 * np.sin(np.pi * u) ** 0.8
    for k in range(3):
        set_(k, CRIES[1] + 4.3, T_RING, pf + r * np.sin(2 * np.pi * 0.22 * (t - T_DANCE) + 2 * np.pi * k / 3), 20.0)
    for k, off in ((WOG, 110), (WELL, -130), (FLO, 190)):
        set_(k, T_RING, T_RENOUNCE, pf + off + 0.5 * bob[k], 2.5)
    for k, off in ((WOG, 200), (WELL, -240), (FLO, 300)):
        set_(k, T_RENOUNCE, T_STARE, pf + off + bob[k], 1.5)
    for k, off in ((WOG, 150), (WELL, 330), (FLO, 240)):
        set_(k, T_STARE, D, pf + off, 2.0)
    A = at(G, 'Porch Left', 0.75)
    set_(3, 0, D, A + 10 * np.sin(2 * np.pi * t / 3.0), 3.0)
    for i, c in enumerate(CREEP):
        set_(3, c, D, A + (pf - 45 - A) * (i + 1) / len(CREEP), 7.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, pos=pos[:3], apos=pos[3])


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    calls = np.array([e[0] for e in N if e[4] in ('mute', 'horn', 'trumpet')])
    rings = np.array([e[0] for e in N if e[4] == 'ring'] + [e[0] for e in N if e[4] == 'ringlow'])
    cries = [(t, kind, k) for k, tc in enumerate(CRIES) for t, _, _, kind in cry_chords(tc)]
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    nb = 46                                                 # motes of sunlight drifting to the rock
    b0 = rng.uniform(0, L, nb)
    bt = rng.uniform(0.0, 10.0, nb)
    btau = rng.uniform(1.2, 3.0, nb)

    def env(t):
        """How awake the gold is (0..1), how wide its light spreads, how hard and small it is."""
        wake = 0.25 + 0.5 * smoothstep(0, 12, t) + 0.25 * smoothstep(12, 18, t)
        spread = smoothstep(11, 19, t) * (1 - 0.8 * smoothstep(T_RING - 1, T_RING + 2, t))
        hard = smoothstep(T_RING - 1, T_RING + 2, t)
        return wake, spread, hard

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        wake, spread, hard = env(t)
        ap = C['apos'][f]
        cold = smoothstep(T_RENOUNCE, T_RENOUNCE + 3.5, t) * (1 - 0.55 * smoothstep(T_LAUGH, T_LAUGH + 2, t))
        reach = smoothstep(0, 1, cold) * (L / 2 + 300) * 1.0
        shade = np.clip(np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d))
                        * cold, 0, 1) if cold > 0 else np.zeros(G.N)

        # the river, turning golden as the gold's light spreads; glints on the crests
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        warm = 0.6 * spread
        base = (1 - 0.7 * shade)
        fr += light(DEEP, (0.2 + 0.1 * w1) * base * (1 - 0.4 * warm))
        fr += light(GREEN, (0.07 + 0.18 * w1 * w2) * base * (1 - 0.5 * warm))
        fr += light(GOLD, (0.06 + 0.22 * w1 * w2) * warm * base)
        crest = (w1 * w2) ** 3
        fr += light(GLINT, 0.6 * spread * crest * (0.5 + 0.5 * tw(t)) * base)
        fr += light(SHADOW, 0.3 * shade)

        # sunlight drifting down to the rock
        if t < 14:
            q = pf + (b0 - pf) * np.exp(-np.clip(t - bt, 0, None) / btau)
            vis = smoothstep(bt, bt + 0.6, t) * (np.abs(q - pf) > 25) * (1 - smoothstep(11, 14, t))
            g = (np.exp(-((d[:, None] - q[None, :]) / 10) ** 2) * vis[None, :]).max(axis=1)
            fr += light(BEAM, 0.7 * g * (0.6 + 0.4 * tw(t)))

        # the gold: a glow on the rock that pulses with every note of its call
        ci = int(np.searchsorted(calls, t, side='right')) - 1
        pulse = np.exp(-(t - calls[ci]) / 0.3) if ci >= 0 and t - calls[ci] < 2 else 0.0
        width = (30 + 60 * wake) * (1 - 0.75 * hard) + 14 * hard
        core = np.exp(-((d - pf) / width) ** 2)
        glow = np.exp(-((d - pf) / (180 + 420 * spread)) ** 2)
        fr += light(GOLD, (0.55 + 0.35 * wake + 0.3 * pulse) * core + 0.45 * spread * glow * base)
        fr += light(HOT, (0.25 * wake + 0.4 * pulse + 0.5 * hard) * np.exp(-((d - pf) / (0.45 * width)) ** 2))

        # the cry: yearning chords sweep gold out to both ends; resolutions flash the whole roof
        for tc, kind, k in cries:
            if not tc <= t < tc + 1.6:
                continue
            age = t - tc
            if kind == 'res':
                fr += light(GOLD, (0.6 + 0.2 * k) * np.exp(-age / 0.35) * np.ones(G.N))
                fr += light(HOT, (0.35 + 0.2 * k) * np.exp(-age / 0.18) * np.ones(G.N))
            elif kind == 'tail':
                fr += light(GOLD, 0.45 * np.exp(-age / 0.4) * np.exp(-((d - pf) / 500) ** 2))
            else:
                rf = 1600 * smoothstep(0, 0.8, age)
                band = np.exp(-((np.abs(d - pf) - rf) / 140) ** 2) * (1 - smoothstep(0.8, 1.6, age))
                fr += light(GOLD, 0.8 * band + 0.3 * smoothstep(rf, rf - 300, np.abs(d - pf)) * np.exp(-age / 0.8))
        if CRIES[1] <= t < CRIES[1] + 6:
            sp = (rng.random(G.N) < 0.04) * np.exp(-(t - CRIES[1]) / 2.0)
            fr += light(WHITE, 0.8 * sp)

        # the Ring: beads circling the hard point of gold, gold toward the street, red turned away
        ring = smoothstep(T_RING - 0.5, T_RING + 1.5, t) * (1 - smoothstep(T_RENOUNCE - 0.5, T_RENOUNCE + 1.5, t))
        ring += 0.5 * smoothstep(T_STIR, T_STIR + 1.5, t)
        if ring > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.35) if ri >= 0 and t - rings[ri] < 2 else 0.0
            R = 420 - 120 * smoothstep(T_RING, T_RENOUNCE, t)
            th = 2 * np.pi * (np.arange(14) / 14 + 0.28 * (t - T_RING))
            q, depth = pf + R * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 24) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            fr += light(GOLD, ring * (0.95 + 0.4 * rp) * front) + light(RED, ring * (0.6 + 0.25 * rp) * back)

        # the maidens
        frozen = smoothstep(T_STARE + 1, T_STARE + 2, t)
        for k in range(3):
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = np.exp(-(t - sung[k][i]) / 0.2) if i >= 0 and t - sung[k][i] < 1.0 else 0.0
            b = (0.62 + 0.38 * flare) * (1 - 0.35 * cold) * (1 - 0.3 * frozen)
            trail = np.zeros(G.N)
            if abs(p - C['pos'][k][max(f - 8, 0)]) > 25:
                for j, lag in enumerate((3, 6, 9, 12, 15)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 24) ** 2) * (1 - j / 5.5))
            body = np.exp(-((d - p) / (20 + 10 * flare)) ** 2)
            fr += light(COLOR[k], b * body + 0.3 * b * np.exp(-((d - p) / 90) ** 2) + 0.45 * trail)
            fr += light(WHITE, 0.4 * b * flare * body)

        # Alberich: dazzled at first (gold flecks on him), then creeping, his red reaching for the gold
        murk = np.exp(-((d - ap) / 220) ** 2)
        fr += light(MUD, 0.3 * murk * (1 + 0.15 * smoulder(t)))
        jolt = sum(np.exp(-(t - c - 0.2) / 0.25) for c in CREEP + [T_ASK] if c + 0.2 <= t < c + 1.5)
        lust = smoothstep(T_STARE, D, t)
        fr += light(ALB, (0.6 + 0.3 * jolt + 0.25 * lust) * np.exp(-((d - ap) / (28 + 8 * jolt)) ** 2)
                    * (1 + 0.2 * smoulder(t)))
        fr += light(GLINT, 0.5 * spread * (1 - hard) * np.exp(-((d - ap) / 30) ** 2) * (tw(t) > 0.8))
        if lust > 0:
            ahead = np.clip((d - ap) / max(pf - ap, 1), 0, 1)
            fr += light(ALB, 0.55 * lust * (d > ap) * np.exp(-((d - ap) / (60 + 180 * lust))) * (1 - ahead) ** 0.5)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who] if who is not None else C['apos']))

    for name, gain, rev in (('voices', 0.2, 0.35), ('choir', 0.1, 0.45), ('strings', 0.13, 0.32), ('low', 0.16, 0.15),
                            ('brass', 0.17, 0.3), ('winds', 0.17, 0.35), ('perc', 0.2, 0.25), ('harp', 0.2, 0.4),
                            ('laugh', 0.11, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    voice = [M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12), M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12),
             M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)]
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flst = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')

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

    choir = [[], [], []]
    for t, d, m, v, part, who in compose():
        if part == 'sing':
            M.add('voices', voice[who].play(m, v, dur=d * 1.05, release=0.2), t, 1.0, pan_of(who, t))
            choir[who].append((t, m, v - 28, d))
        elif part == 'shimmer':
            hold('strings', vtrem, m, t, t + d, v, {72: -0.4, 76: 0.0, 79: 0.4}.get(m, 0.0), rise=6.0, fall=0.5, gain=0.6)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.8)
        elif part == 'mute':
            M.add('brass', mute.play(m, v, dur=d, release=0.4), t, 1.0, pf)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d, release=0.4), t, 0.9, pf - 0.2)
        elif part == 'trumpet':
            M.add('brass', tpt.play(m, v, dur=d, release=0.4), t, 1.0, pf + 0.15)
        elif part == 'tutti':
            if m >= note('G4'):
                M.add('brass', tpt.play(m - 12, v, dur=d, release=0.3), t, 0.55, 0.3)
                M.add('strings', vn.play(m, v, dur=d, release=0.3), t, 0.6, -0.3)
            elif m >= note('C4'):
                M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.6, -0.2)
            else:
                M.add('low', tuba.play(m, v, dur=d, release=0.3), t, 0.8, 0.0)
                M.add('low', cb.play(m, v - 10, dur=d, release=0.3), t, 0.6, 0.0)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-2), t, 0.9, 0.0)
            M.add('perc', crash.play(v), t, 0.7 if v < 120 else 0.95, 0.0)
            if v >= 120:
                M.add('perc', bd.play(v), t, 0.7, 0.0)
        elif part == 'gliss':
            gl = [x for x in range(note('C3'), note('G5') + 1) if x % 12 in (0, 4, 7)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 90 + i), t + i * d / len(gl), 1.0, -0.7 + 1.4 * i / len(gl))
        elif part == 'rock':
            M.add('harp', harp.play(m, v), t, 1.0, -0.3 + 0.6 * (m - 55) / 12)
        elif part == 'bass':
            M.add('low', pizz.play(m + 12, v), t, 0.9, 0.0)
        elif part == 'alb':
            M.add('low', bsn.play(m, v, dur=d, release=0.2), t, 1.0, pan_of(None, t))
        elif part == 'ring':
            M.add('winds', (ob if who == WELL else cl).play(m, v, dur=d * 1.05, release=0.3), t, 1.0,
                  pan_of(WELL, t) if who == WELL else pf)
        elif part == 'ringbass':
            hold('low', vc, m, t, t + d, v, 0.0, rise=0.5, fall=1.0, gain=0.8)
        elif part == 'ringlow':
            M.add('low', (bsn if m < note('C3') else horn).play(m, v, dur=d, release=0.4), t, 0.8, -0.2)
        elif part == 'renounce':
            M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.9, -0.1)
            M.add('low', vc.play(m, v - 10, dur=d, release=0.5), t, 0.6, 0.2)
        elif part == 'dark':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=2.0, fall=1.5, gain=0.7)
        elif part == 'laugh':
            M.add('laugh', (pic if m >= note('Ab5') else flst).play(m, v), t, 1.0, pan_of(who, t))
        elif part == 'stir':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.9, pf)
    for who in range(3):
        M.add('choir', M.synth('Pads/Ooh').render(choir[who], D + 2), 0.0, 1.0, (0.0, 0.5, -0.5)[who])
