"""Rheingold!: sunlight finds its way down through the river. Motes of it drift in from every run of the house
to the rock at the back of the porch, and the gold wakes to its own call in the horns, each note a pulse of gold
that grows, while Alberich, on Porch Left, catches glints of it. The Rhinemaidens break into their jubilation:
"Heiajaheia!" in three parts, and then the cry "Rheingold! Rheingold!", where each yearning chord sends a sweep of
gold out from the rock to both ends of the house and each resolution flashes the whole roof gold; the second
time, at the height of it, with cymbals and sparks, they spin round the gold and swing wide over the wings.

Wellgunde lets the secret out ("Der Welt Erbe gewänne zu eigen, wer aus dem Rheingold schüfe den Ring"): the
Ring motif sounds and the gold draws in to a hard point with a ring of beads circling it, bright gold where it
turns toward the street and dull red where it turns away. Woglinde adds the condition ("Nur wer der Minne Macht
entsagt, nur wer der Liebe Lust verjagt"): only one who renounces love can forge it. A cold indigo shadow drains
in from both ends of the house, the maidens freeze, and Alberich creeps along the porch toward the gold, his red
reaching out ahead of him.

The music is Wagner's own: bars 527-532, 536-542, 556-564, 599-605 and 617-621 of Scene 1, timed bar by bar like
Barenboim's 1991 Bayreuth recording. The orchestra is the Wagner Ring Dataset's piano reduction (pixelhome/ring.py):
the gold's call on horns and trumpets, the shimmering water on violins and harp-like violins, the jubilation in
full orchestra, the Ring motif in the woodwinds, the renunciation's chords on trombones. The Rhinemaidens' lines
are from the printed vocal score (Klindworth, Schott; archive.org dasrheingold00wagn2, pp. 33-36, 41-43), each
on her own instrument: Woglinde oboe, Wellgunde flute, Flosshilde clarinet, trumpets doubling the "Rheingold!"
cry. A cymbal swell and crashes carry the gold's blaze; under the secret and the renunciation the stage is quiet.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG04'
TITLE = 'Rheingold!'
KIND = 'show'
DESCRIPTION = ('Sunlight wakes the gold on its rock and the whole house blazes as the Rhinemaidens cry out its '
               'name. Then they let slip its secret: forge a ring from it and the world is yours, if you give up '
               'love. Alberich is listening.')
VOICEOVER = ('The sun reaches the bottom of the river, and on the rock, something wakes. '
             'Watch the gold. And watch who is watching it.')

EX = excerpt(__file__)                      # bars 527-532, 536-542, 556-564, 599-605, 617-621.5, Barenboim 1991
D = EX['seconds']
SEG = [x['start'] for x in EX['segments']] + [D]


def bt(pos):
    """The time of a (fractional) bar position; the five passages share no bar numbers."""
    seg = next(x for x in EX['segments'] if x['measures'][0] <= pos <= x['measures'][1])
    bars = [(b, t) for b, t in EX['bars'] if seg['measures'][0] <= b <= seg['measures'][1]]
    return float(np.interp(pos, [b for b, _ in bars], [t for _, t in bars]))


def per(b):
    """Eighths in bar b: 9/8 until the renunciation's common time."""
    return 8 if b >= 617 else 9


CRIES = [bt(540), bt(556)]                  # "Rheingold! Rheingold!"
T_DANCE = bt(558)
T_ASK = SEG[3]                              # Alberich, all ears
T_RING = bt(599.889)                        # Wellgunde: whoever forges a ring...
T_RENOUNCE = bt(617.5)                      # Woglinde: only one who renounces love
T_LAUGH = D + 10.0
T_STARE = bt(618.5)
CREEP = [bt(618), bt(619), bt(620), bt(621)]    # a lurch toward the gold on each bar
T_STIR = bt(620.9)

WOG, WELL, FLO = 0, 1, 2
_HEIA = {WOG: [(0, 1.5, 'G5'), (1.5, .5, 'E5'), (2, 1, 'F5'), (3, 3, 'G5'), (6, 2, 'E5')],
         WELL: [(0, 1.5, 'E5'), (1.5, .5, 'C5'), (2, 1, 'D5'), (3, 3, 'E5'), (6, 2, 'C5')],
         FLO: [(0, 1.5, 'C5'), (1.5, .5, 'G4'), (2, 1, 'G4'), (3, 3, 'C5'), (6, 2, 'G4')]}
_CRY = {WOG: [(0, 6, 'A5'), (6, 2, 'G5')], WELL: [(0, 6, 'F5'), (6, 2, 'E5')], FLO: [(0, 6, 'B4'), (6, 2, 'C5')]}
_WALLA = {WOG: [(0, 1.5, 'G5'), (1.5, .5, 'E5'), (2, 1, 'C5'), (3, 1, 'G4'), (4, 1, 'C5'), (5, 1, 'D5'),
                (6, 1.5, 'E5'), (7.5, .5, 'C5'), (8, 1, 'E5')],
          WELL: [(0, 1.5, 'E5'), (1.5, .5, 'C5'), (2, 1, 'G4'), (3, 1, 'E4'), (4, 1, 'G4'), (5, 1, 'G4'),
                 (6, 1.5, 'C5'), (7.5, .5, 'G4'), (8, 1, 'C5')],
          FLO: [(0, 1.5, 'C5'), (1.5, .5, 'G4'), (2, 1, 'E4'), (3, 1, 'C4'), (4, 1, 'E4'), (5, 1, 'F4'),
                (6, 1.5, 'G4'), (7.5, .5, 'E4'), (8, 1, 'G4')]}
_WALLA2 = {WOG: [(0, 1.5, 'G4'), (1.5, .5, 'C5'), (2, 1, 'D5'), (3, 1.5, 'E5'), (4.5, .5, 'C5'), (5, 1, 'E5'),
                 (6, 1.5, 'G5'), (7.5, .5, 'E5'), (8, 1, 'G5')],
           WELL: [(0, 1.5, 'E4'), (1.5, .5, 'G4'), (2, 1, 'G4'), (3, 1.5, 'C5'), (4.5, .5, 'G4'), (5, 1, 'C5'),
                  (6, 1.5, 'E5'), (7.5, .5, 'C5'), (8, 1, 'E5')],
           FLO: [(0, 1.5, 'C4'), (1.5, .5, 'E4'), (2, 1, 'F4'), (3, 1.5, 'G4'), (4.5, .5, 'E4'), (5, 1, 'G4'),
                 (6, 1.5, 'C5'), (7.5, .5, 'G4'), (8, 1, 'C5')]}
# The Rhinemaidens' lines, from the vocal score: (bar, start, length in eighths, note, who)
VOICE = []
for _k in (WOG, WELL, FLO):
    for _b, _bar in ((536, _HEIA), (537, _HEIA), (538, _WALLA), (540, _CRY), (541, _CRY), (556, _CRY), (557, _CRY),
                     (558, _HEIA), (559, _HEIA), (560, _WALLA2)):
        VOICE += [(_b, x, n, m, _k) for x, n, m in _bar[_k]]
    VOICE += [(539, 0, 4, {WOG: 'G5', WELL: 'E5', FLO: 'C5'}[_k], _k), (561, 0, 6, {WOG: 'C6', WELL: 'G5', FLO: 'E5'}[_k], _k)]
VOICE += [(599, 0, 6, 'C#5', WOG), (599, 6, 2, 'B4', WOG)]
VOICE += [(b, x, n, m, WELL) for b, x, n, m in [
    (599, 8, 1, 'B4'), (600, 0, 3, 'E5'), (600, 3, 4, 'C#5'), (600, 7, 1, 'A4'), (600, 8, 1, 'G#4'),
    (601, 0, 1, 'F#4'), (601, 1, 1, 'G#4'), (601, 2, 1, 'A4'), (601, 3, 2, 'B4'), (601, 5, 1, 'E4'), (601, 6, 1, 'C5'),
    (601, 7, 1, 'B4'), (601, 8, 1, 'A4'), (602, 0, 3, 'E5'), (602, 3, 3, 'C5'), (602, 6, 1, 'F#4'), (602, 7, 1, 'A4'),
    (602, 8, 1, 'C5'), (603, 0, 1, 'E5'), (603, 2, 1, 'G4'), (603, 3, 4, 'A4'), (603, 7, 1, 'G#4'), (603, 8, 1, 'A4'),
    (604, 0, 1, 'C5'), (604, 1, 1.5, 'B4'), (604, 2.5, .5, 'C5'), (604, 3, 3, 'D5'), (617, 0, 2, 'D5')]]
VOICE += [(b, x, n, m, WOG) for b, x, n, m in [
    (617, 4, 2, 'G4'), (617, 6, 1, 'G4'), (617, 7, 1, 'G4'), (618, 0, 3, 'Eb5'), (618, 3, 1, 'D5'), (618, 4, 2, 'C5'),
    (618, 7, 1, 'G4'), (619, 0, 4, 'Ab4'), (619, 4, 2, 'G4'), (619, 6, 1, 'G4'), (619, 7, 1, 'G4'), (620, 0, 3, 'Eb5'),
    (620, 3, 1, 'D5'), (620, 4, 2, 'C5'), (620, 7, 1, 'Ab4'), (621, 0, 2, 'Bb4')]]

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


def cry_chords(t0):
    """The cry's chords: the yearning 'Rhein-' and the resolving 'gold!', in both bars: (time, seconds, midi, kind)."""
    b = max(m for m, t in EX['bars'] if abs(t - t0) < 1e-3)
    out = []
    for bar in (b, b + 1):
        out.append((bt(bar), bt(bar + 6 / 9) - bt(bar), 0, 'yearn'))
        out.append((bt(bar + 6 / 9), bt(bar + 8 / 9) - bt(bar + 6 / 9), 0, 'res'))
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). 'sing' is a maiden's line (who: which one); the gold's
    call is 'horn' (the left hand's long notes as it wakes), the Ring motif 'ring' (the right hand under the
    secret); every note of the excerpt is also 'orch' (who: the hand)."""
    N = []
    for b, x, n, name, who in VOICE:
        t0 = bt(b + x / per(b))
        N.append((t0, bt(b + (x + n) / per(b)) - t0, note(name), 100, 'sing', who))
    for t, d, m, v, h in EX['notes']:
        N.append((t, d, m, v, 'orch', h))
        if t < SEG[1] and h == 1 and d >= 0.5:
            N.append((t, d, m, v, 'horn', None))
        if SEG[3] <= t < SEG[4] and h == 0 and d >= 0.24:
            N.append((t, d, m, v, 'ring', None))
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
    bt0 = rng.uniform(0.0, 10.0, nb)
    btau = rng.uniform(1.2, 3.0, nb)

    def env(t):
        """How awake the gold is (0..1), how wide its light spreads, how hard and small it is."""
        wake = 0.25 + 0.5 * smoothstep(0, SEG[1] - 2, t) + 0.25 * smoothstep(SEG[1] - 2, SEG[1] + 3, t)
        spread = smoothstep(SEG[1] - 3, SEG[1] + 4, t) * (1 - 0.8 * smoothstep(T_RING - 1, T_RING + 2, t))
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
        if t < SEG[1]:
            q = pf + (b0 - pf) * np.exp(-np.clip(t - bt0, 0, None) / btau)
            vis = smoothstep(bt0, bt0 + 0.6, t) * (np.abs(q - pf) > 25) * (1 - smoothstep(SEG[1] - 3, SEG[1], t))
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
    """Wagner's notes on the orchestra, the Rhinemaidens' lines on woodwinds (trumpets doubling the cry), and the
    stage: the gold's blaze carried by cymbals."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    where = lambda k, t: pan_at(np.interp(t, C['t'], C['pos'][k]))
    o = Orchestra(M, level=2.4)

    def role(t, d, m, v, h):
        if t < SEG[1]:                                                  # the gold wakes: its call in the horns
            if h == 1 and d >= 0.5:
                return [('horns', 0, 10, 0.9), ('trumpets', 0, -4, 0.45 * (t > 5.5))]
            return [('violins', 0, -6, 0.5), ('harp', 0, -12, 0.3)] if h == 0 else [('cellos', 0, -6, 0.5)]
        if t < SEG[3]:                                                  # the jubilation: full orchestra
            return None
        if t < SEG[4]:                                                  # the secret: the Ring motif in the woodwinds
            if h == 0:
                return [('clarinets', 0, 0, 0.55), ('oboes', 0, -8, 0.35), ('horns', -12, -14, 0.25)]
            return [('cellos', 0, -4, 0.5), ('bassoons', 0, -6, 0.35)]
        if h == 0:                                                      # the renunciation: dark brass chords
            return [('trombones', -12 if m >= 62 else 0, 0, 0.6), ('horns', 0, -4, 0.5), ('violas', 0, -6, 0.35)]
        return [('tuba', 0, 0, 0.5), ('basses', 12 if m < 40 else 0, -4, 0.5)]

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if CRIES[1] - 1 <= t < SEG[3] else 0.75, role=role)
    inst = {WOG: [('oboes', 0.85), ('flutes', 0.25)], WELL: [('flutes', 0.85), ('clarinets', 0.25)],
            FLO: [('clarinets', 0.9), ('violas', 0.3)]}
    cry = [(tc, tc + 4.3) for tc in CRIES]
    for t, d, m, v, part, who in compose():
        if part != 'sing':
            continue
        for name, g in inst[who]:
            o.play(name, m, t, max(d, 0.12), v, where(who, t), g)
        if who == WOG and any(a <= t < b for a, b in cry):              # the cry rings out on trumpets too
            o.play('trumpets', m - 12, t, d, 104, where(who, t), 0.4)
    # the stage: the gold blazes with the cry
    o.hit('cymbal swell', CRIES[0] - 2.4, 90, gain=0.45)
    for tc in CRIES:
        for tt, _, _, kind in cry_chords(tc):
            if kind == 'res':
                o.hit('crash', tt, 96 + 12 * (tc == CRIES[1]), gain=0.35 + 0.15 * (tc == CRIES[1]))
    o.hit('timpani roll', CRIES[1] - 1.5, 100, pitch=-2, gain=0.4)
    o.hit('triangle', SEG[1] - 0.5, 80, gain=0.2)
    o.hit('gong scrape', T_RENOUNCE - 0.3, 70, gain=0.25)
    o.effects([(0.0, -10), (SEG[1] - 3, -4), (CRIES[0] + 2, -6), (SEG[2], -4), (SEG[3] - 0.5, -8),
               (T_RING, -18), (D, -14)])
