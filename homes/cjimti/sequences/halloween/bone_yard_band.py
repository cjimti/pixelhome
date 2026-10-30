"""Bone Yard Band: the Bone Yard skeletons are back, and they've formed a swing band. One by one they rise
and warm up: a xylophonist on the Left wing who plays his own ribs (seven ribs, seven notes, each rib
lights on its note), a trombonist on the Right whose arm-bone slide follows every pitch, a bassist on
Porch Left plucking a long femur (the fret spot shows the note) and a drummer on the Porch Front with a
skull kick drum, a pelvis snare and a gold cymbal on the porch corners. The drummer taps the count on his
skull, they play the tune, solos pass from the trombone to the bass to the drums, and the drummer goes so
wild that his skull flies off. It bounces round the house on the beat (off the far right end, all the
way back past everyone, off the back end of the Side) while the band vamps and the headless drummer keeps
time, and lands on the xylophonist, who now has two heads. They look at each other; the headless drummer
clicks two, and the big final chord. Then the skull hops home along the roof and lands back on its neck
in time for a ba-dum-tss.

Bones are drawn exactly as in Bone Yard (span-over-pixel coverage in path distance). Every note and drum
hit comes from one plan (_plan) that both render() and score() read, so the lights and the music agree."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, nframes

CODE = 'HW13'
TITLE = 'Bone Yard Band'
KIND = 'show'
DESCRIPTION = ('The Bone Yard skeletons are back as a swing band: a rib xylophone, a femur bass, an '
               'arm-bone trombone and a skull drum kit. The drummer gets carried away in his solo, and '
               'his head goes bouncing round the house.')
VOICEOVER = ('Back by popular demand... the Bone Yard Band! Four skeletons, one roof, and a drummer who '
             'really throws his head into it.')

BONE = hexc('#fff0d6')
GLOW = hexc('#40ff70')
FOG = hexc('#1c9c8c')
GOLD = hexc('#ffa030')

BEAT = 0.4                                  # 150 BPM swing
BAR = 4 * BEAT
SW = BEAT * 2 / 3                           # the swung "and"
K = 1.35
GAP = K * 4.0
R = 16 * K                                  # skull radius when it tumbles
SKL = 32 * K

# ---- the timeline ----
RISE = {'xy': 1.0, 'tb': 2.8, 'bs': 4.6, 'dr': 6.4}   # Left, Right, Porch Left, Porch Front
TCI = 9.6                                   # count-in: the drummer taps his skull
THD = TCI + 2 * BAR                         # the head (tune), 8 bars
TTS = THD + 8 * BAR                         # trombone solo
TBS = TTS + 4 * BAR                         # bass solo
TDS = TBS + 4 * BAR                         # drum solo
TL = TDS + 4 * BAR                          # the skull launches
NB = 24                                     # beats of bouncing
LEGS = (6, 15, 3)                           # beats per leg: to the right end, all the way back, to the xylophonist
TLAND = TL + NB * BEAT
TF = TLAND + BAR                            # final chord
TC2 = TF + 2 * BAR                          # cut-off
TH0 = TC2 + BEAT                            # the skull hops home
NH = 5
TLD = TH0 + NH * BEAT                       # back on his neck
TBA, TDUM, TSS = TLD + BEAT, TLD + BEAT + SW, TLD + 3 * BEAT
D = TSS + 2.7

RIB = ['G4', 'Bb4', 'C5', 'Db5', 'D5', 'F5', 'G5']   # the xylophonist's ribs, top (skull end) to bottom


def e8(t0, e):
    """Time of swung eighth e of the bar starting at t0."""
    return t0 + (e // 2) * BEAT + (e % 2) * SW


def _n(name):
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    acc = {'#': 1, 'b': -1}.get(name[1], 0) if len(name) > 2 else 0
    return 12 * (int(name[-1]) + 1) + names[name[0]] + acc


HEAD_XY = [[(0, 4), (1, 5), (2, 6), (4, 5), (5, 4), (6, 2)],
           [(0, 1), (2, 0), (5, 0), (6, 1), (7, 2)],
           [(0, 2), (1, 1), (2, 2), (4, 5), (5, 4), (6, 3)],
           [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
           [(0, 4), (1, 4), (2, 5), (3, 4), (4, 2), (6, 4)],
           [(0, 2), (2, 1), (4, 4), (5, 3), (6, 2)],
           [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)],
           [(0, 6), (1, 5), (2, 4)]]
HEAD_BS = [['G2', 'A2', 'Bb2', 'D3'], ['G2', 'Bb2', 'D3', 'B2'], ['C3', 'Bb2', 'G2', 'Ab2'],
           ['G2', 'Bb2', 'D3', 'Eb3'], ['D3', 'C3', 'A2', 'F#2'], ['C3', 'Eb3', 'D3', 'F#2'],
           ['G2', 'Bb2', 'D3', 'Bb2'], ['D3', 'C3', 'A2', 'Ab2']]
SOLO_BS = [['G2', 'Bb2', 'D3', 'B2'], ['C3', 'Eb3', 'G2', 'C#3'], ['D3', 'C3', 'A2', 'F#2'], ['G2', 'Bb2', 'D3', 'F#2']]
VAMP_BS = {'Gm': ['G2', 'Bb2', 'D3', 'C#3'], 'D7': ['D3', 'C3', 'A2', 'F#2']}
BASS_SOLO = [[(0, 'G2'), (1, 'G2'), (2, 'Bb2'), (3, 'C3'), (4, 'Db3'), (5, 'D3'), (6, 'F3'), (7, 'D3')],
             [(0, 'C3'), (2, 'G2'), (3, 'Bb2'), (4, 'C3'), (6, 'Eb3'), (7, 'E3')],
             [(0, 'D3'), (1, 'D3'), (2, 'C3'), (3, 'A2'), (4, 'F#2'), (5, 'A2'), (6, 'C3'), (7, 'Eb3')],
             [(0, 'D3'), (1, 'Db3'), (2, 'C3'), (3, 'Bb2'), (4, 'A2'), (5, 'Ab2'), (6, 'G2')]]
# trombone solo: (beat, length in beats, [(beat offset, midi)...] glide keyframes, velocity)
TB_SOLO = [(0, 1.4, [(0, 50), (0.5, 55)], 100), (1 + 2 / 3, 0.3, [(0, 58)], 92), (2, 0.3, [(0, 60)], 95),
           (2 + 2 / 3, 1.2, [(0, 61), (0.3, 62)], 105),
           (4, 1.9, [(0, 63), (0.9, 63), (1.8, 55)], 105), (6 + 2 / 3, 0.3, [(0, 51)], 90),
           (7, 0.9, [(0, 55), (0.85, 60)], 100),
           (8, 0.3, [(0, 62)], 100), (8 + 2 / 3, 0.3, [(0, 60)], 95), (9, 0.3, [(0, 57)], 95),
           (9 + 2 / 3, 0.3, [(0, 54)], 95), (10, 1.9, [(0, 45), (1.6, 57)], 110),
           (12, 1.0, [(0, 55)], 105), (13, 0.6, [(0, 55), (0.55, 50)], 95), (14 + 2 / 3, 1.2, [(0, 50), (1.0, 43)], 100)]
XY_COMP = [(0, 4), (2, 6), (2, 4), (1, 4)]       # rib pairs for the Charleston comp under the trombone
STAB = [('G2', (0, 4), 55), ('C3', (2, 6), 51), ('D3', (2, 4), 54), ('G2', (1, 4), 55)]


def _geo(G):
    s = {n: (float(G.pd[G.seg[n]].min()), float(G.pd[G.seg[n]].max())) for n in G.seg}
    body = K * (32 + 37 + 16 + 26 + 22 + 9) + 5 * GAP
    g = dict(L=float(G.length), s=s, body=body)
    g['xy'] = s['Left'][0] + 75.0           # skull tops; xy and bs face +pd, dr and tb face -pd
    g['bs'] = s['Porch Left'][0] + 22.0
    g['dr'] = s['Porch Front'][1] - 62.0
    g['tb'] = s['Right'][0] + 20.0 + body
    g['kick'] = (s['Porch Front'][0] + 6.0, s['Porch Front'][0] + 46.0)
    g['snare'] = (s['Porch Right'][0] + 10.0, s['Porch Right'][0] + 32.0)
    g['cym'] = (s['Porch Right'][0] + 42.0, s['Porch Right'][0] + 52.0)
    g['fem0'] = g['bs'] + body + 14.0   # the femur bass, beside his feet
    g['fem'] = 125.0
    g['x0'] = g['dr'] - R                    # drummer's skull centre
    g['xl'] = g['xy'] - GAP - R              # where it lands: on top of the xylophonist's skull
    g['centre'] = {'xy': g['xy'] + body / 2 + 8 * K, 'bs': g['bs'] + body / 2, 'dr': g['dr'] - body / 2,
                   'tb': g['tb'] - body / 2}
    A, B = g['L'] - R - 3, R + 3
    g['legs'] = [(g['x0'], A, LEGS[0]), (A, B, LEGS[1]), (B, g['xl'], LEGS[2])]
    return g


def flight(g, t):
    """Flying skull: (centre, height 0..1, contact flash) while it bounces or hops home; None otherwise."""
    if TL <= t < TLAND:
        k = (t - TL) / BEAT
        k0 = 0
        for j, (a, b, n) in enumerate(g['legs']):
            if k < k0 + n or j == len(g['legs']) - 1:
                u = (k - k0) / n
                f = k - int(k)
                return lerp(a, b, u), 4 * f * (1 - f), float(np.exp(-f * BEAT / 0.07))
            k0 += n
    if TH0 <= t < TLD:
        k = (t - TH0) / BEAT
        f = k - int(k)
        return lerp(g['xl'], g['x0'], k / NH), 4 * f * (1 - f), float(np.exp(-f * BEAT / 0.07)) if k >= 1 else 0.0
    return None


def _plan(G):
    g = _geo(G)
    xy, bs, tb, dr, rolls, fx = [], [], [], [], [], []

    def comp(t0, snare=True, skip=None):
        for e in (0, 2, 3, 4, 6, 7):
            dr.append((e8(t0, e), 'ride', 58 if e % 2 else 72))
        for e in (0, 4):
            dr.append((e8(t0, e), 'kick', 58))
        if snare:
            for e in (2, 6):
                if skip is None or not skip(e8(t0, e)):
                    dr.append((e8(t0, e), 'snare', 74))

    def walk(t0, notes, vel=100):
        for i, m in enumerate(notes):
            bs.append((t0 + i * BEAT, _n(m), vel))

    def tbn(t0, dur, kf, vel):
        tb.append((t0, dur, kf, vel))

    # ---- warm-ups: each rises and shows what his instrument does ----
    t = RISE['xy'] + 0.8
    for i, r in enumerate(list(range(7)) + list(range(5, -1, -1))):
        xy.append((t + 0.07 * i, r, 80 + 3 * i if i < 7 else 100 - 4 * (i - 7)))
    tbn(RISE['tb'] + 0.6, 1.0, [(0, 45), (0.9, 62)], 100)
    for i, m in enumerate(('G1', 'D2', 'G2')):
        bs.append((RISE['bs'] + 0.6 + (0, SW, BEAT)[i], _n(m), 110))
    rolls.append((RISE['dr'] + 0.6, 1.0, 'snare'))
    dr += [(RISE['dr'] + 1.6, 'crash', 110), (RISE['dr'] + 1.6, 'kick', 110)]
    for k in (0, 2, 4, 5, 6, 7):            # count-in, tapped on his own skull
        dr.append((TCI + k * BEAT, 'click', 100 if k < 4 else 115))

    # ---- the head: 8 bars, melody on the ribs ----
    for b in range(8):
        t0 = THD + b * BAR
        for e, r in HEAD_XY[b]:
            xy.append((e8(t0, e), r, 104 if e % 2 == 0 else 92))
        walk(t0, HEAD_BS[b])
        comp(t0)
    tbn(THD, 2 * BAR - 0.1, [(0, 49), (0.15, 50)], 62)
    tbn(THD + 2 * BAR, 1.5, [(0, 51)], 62)
    tbn(THD + 3 * BAR + 2 * BEAT, 0.75, [(0, 43), (0.55, 55)], 95)
    tbn(THD + 4 * BAR, 1.5, [(0, 54)], 66)
    tbn(THD + 5 * BAR, 0.75, [(0, 55)], 66)
    tbn(THD + 5 * BAR + 2 * BEAT, 0.75, [(0, 54)], 66)
    tbn(THD + 6 * BAR, 1.5, [(0, 50)], 62)
    tbn(THD + 7 * BAR + BEAT, 1.15, [(0, 50), (1.0, 62)], 100)

    # ---- trombone solo ----
    for b in range(4):
        t0 = TTS + b * BAR
        walk(t0, SOLO_BS[b])
        comp(t0)
        for e in (0, 3):
            for r in XY_COMP[b]:
                xy.append((e8(t0, e), r, 64))
    for bt, ln, kf, v in TB_SOLO:
        tbn(TTS + bt * BEAT, ln * BEAT, [(o * BEAT, m) for o, m in kf], v)

    # ---- bass solo: ride and feathered kick only ----
    for b in range(4):
        t0 = TBS + b * BAR
        for e, m in BASS_SOLO[b]:
            bs.append((e8(t0, e), _n(m), 112 if e % 2 == 0 else 98))
        comp(t0, snare=False)

    # ---- drum solo: the band stabs each downbeat, he gets wilder every bar ----
    for b in range(4):
        t0 = TDS + b * BAR
        m, ribs, tm = STAB[b]
        bs.append((t0, _n(m), 115))
        for r in ribs:
            xy.append((t0, r, 110))
        tbn(t0, 0.2, [(0, tm)], 110)
        dr.append((t0, 'crash', 100 + 6 * b))
        dr.append((t0, 'kick', 110))
    t0 = TDS
    dr += [(t0 + BEAT, 'snare', 90), (t0 + BEAT + SW, 'snare', 80), (t0 + 2 * BEAT, 'kick', 95),
           (t0 + 2 * BEAT + SW, 'snare', 90), (t0 + 3 * BEAT, 'snare', 100), (t0 + 3 * BEAT + SW, 'kick', 90)]
    t0 = TDS + BAR
    for bt in range(4):
        for j in range(3):
            if bt == 0 and j == 0:
                continue
            dr.append((t0 + bt * BEAT + j * BEAT / 3, 'kick' if j == 0 else 'snare', 88 + 4 * bt))
    t0 = TDS + 2 * BAR
    for bt in range(4):
        n6 = 3 if bt < 2 else 6
        for j in range(n6):
            if bt == 0 and j == 0:
                continue
            kind = ('snare', 'snare', 'tom', 'tom', 'kick', 'kick')[j] if n6 == 6 else ('tom', 'snare', 'snare')[j]
            dr.append((t0 + bt * BEAT + j * BEAT / n6, kind, 96 + 3 * bt))
    t0 = TDS + 3 * BAR
    for j in range(24):
        tt = t0 + j * BEAT / 6
        if j == 0:
            continue
        kind = 'kick' if j % 6 == 0 else ('tom' if j >= 18 and j % 2 else 'snare')
        dr.append((tt, kind, int(70 + 55 * j / 23)))
    dr += [(TL, 'crash', 127), (TL, 'kick', 127), (TL, 'snare', 120)]
    bs += [(TL, _n('G1'), 120), (TL, _n('G2'), 110)]
    for r in (0, 4, 6):
        xy.append((TL, r, 122))
    tbn(TL, 0.25, [(0, 55)], 122)

    # ---- the skull bounces round the house; the band vamps, the headless drummer keeps time ----
    ts = np.arange(TL, TLAND - 0.01, 0.005)
    xs = np.array([flight(g, t)[0] for t in ts])

    def crossings(c):
        d = np.sign(xs - c)
        return [float(ts[i]) for i in np.nonzero(np.diff(d) != 0)[0]]

    tb_pass = crossings(g['centre']['tb'])
    dr_pass = [t for t in crossings(g['centre']['dr']) if t > TL + 1.0]
    react = []
    for i, tc in enumerate(tb_pass[:2]):    # the trombonist's whoops as it flies over him
        kf = [(0, 48), (0.5, 62)] if i == 0 else [(0, 62), (0.5, 45)]
        tbn(tc - 0.3, 0.6, kf, 100)
        react.append(tc)
    near_dr = lambda t: any(abs(t - c) < 0.5 for c in dr_pass)
    for b in range(NB // 4):
        t0 = TL + b * BAR
        c = 'Gm' if b % 2 == 0 else 'D7'
        walk(t0, VAMP_BS[c], 98)
        comp(t0, skip=near_dr)
        riff = [(0, 0), (2, 1), (3, 2), (4, 4), (6, 2)] if c == 'Gm' else [(0, 4), (2, 3), (3, 2), (4, 1), (6, 0)]
        for e, r in riff:
            if b == 0 and e == 0:
                continue
            xy.append((e8(t0, e), r, 88))
        ts3 = e8(t0, 3)
        if b > 0 and all(abs(ts3 - c2) > 0.8 for c2 in react):
            tbn(ts3, 0.22, [(0, 55 if c == 'Gm' else 54)], 96)
    for c in dr_pass:                       # he grabs for it and fumbles a crash
        dr.append((c, 'crash', 96))
    k0 = 0
    walls = {LEGS[0], LEGS[0] + LEGS[1]}
    for k in range(1, NB + 1):
        t = TL + k * BEAT
        x = flight(g, t - 1e-6)[0]
        fx.append((t, x, 'wall' if k in walls else ('land' if k == NB else 'bonk'), k))
    fx.append((TL, g['x0'], 'pop', 0))

    # ---- two heads: a stunned bar, two clicks, the final chord, the cut-off ----
    for i in range(6):
        xy.append((TLAND + 0.6 + 0.1 * i, i % 2, 48))
    dr += [(TLAND + 2 * BEAT, 'click', 105), (TLAND + 3 * BEAT, 'click', 115)]
    dr += [(TF, 'crash', 125), (TF, 'kick', 125), (TC2, 'crash', 127), (TC2, 'kick', 127), (TC2, 'snare', 120)]
    rolls += [(TF + 0.2, TC2 - TF - 0.2, 'cym'), (TF + BAR, BAR, 'snare')]
    for r in (0, 4, 6):
        xy.append((TF, r, 122))
        xy.append((TC2, r, 127))
    cyc = [0, 1, 2, 4, 5, 6, 5, 4, 2, 1]
    for i in range(1, 39):
        xy.append((TF + 0.08 * i, cyc[i % len(cyc)], int(78 + 32 * i / 38)))
    bs += [(TF, _n('G1'), 125), (TF + 0.02, _n('G2'), 115), (TC2, _n('G1'), 127), (TC2 + 0.02, _n('G2'), 118)]
    tbn(TF, TC2 - TF - 0.06, [(0, 50), (0.3, 55)], 112)
    tbn(TC2, 0.3, [(0, 55)], 124)

    # ---- hop home, ba-dum-tss ----
    for k in range(1, NH + 1):
        t = TH0 + k * BEAT
        fx.append((t, lerp(g['xl'], g['x0'], k / NH), 'hop' if k < NH else 'home', k))
    fx.append((TH0, g['xl'], 'lift', 0))
    dr += [(TBA, 'snare', 112), (TDUM, 'tom', 112), (TDUM, 'kick', 100), (TSS, 'tss', 118)]

    key = lambda e: e[0]
    return dict(g=g, xy=sorted(xy, key=key), bs=sorted(bs, key=key), tb=sorted(tb, key=key),
                dr=sorted(dr, key=key), rolls=rolls, fx=sorted(fx, key=key), dr_pass=dr_pass)


class _Env:
    """Exponential envelope of the most recent hit (velocity-scaled)."""

    def __init__(self, hits, tau):
        self.t = np.array([h[0] for h in hits]) if hits else np.zeros(0)
        self.v = np.array([h[1] for h in hits]) / 127 if hits else np.zeros(0)
        self.tau = tau

    def __call__(self, t):
        i = int(np.searchsorted(self.t, t, side='right')) - 1
        if i < 0:
            return 0.0
        return float(self.v[i] * np.exp(-(t - self.t[i]) / self.tau))

    def last(self, t):
        return int(np.searchsorted(self.t, t, side='right')) - 1


def tb_state(notes, t):
    """Trombone pitch (midi, held between notes) and how much it is sounding (0..1)."""
    i = int(np.searchsorted([nt[0] for nt in notes], t, side='right')) - 1
    if i < 0:
        return 55.0, 0.0
    t0, dur, kf, vel = notes[i]
    dt = min(t - t0, dur)
    ks = [k[0] for k in kf]
    p = float(np.interp(dt, ks, [k[1] for k in kf]))
    on = smoothstep(0, 0.03, t - t0) * (1.0 if t < t0 + dur else float(np.exp(-(t - t0 - dur) / 0.12)))
    return p, float(on) * (0.55 + 0.45 * vel / 127)


def slide_ext(p):
    return 150.0 * float(np.clip((63 - p) / 20, 0, 1))


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    P = _plan(G)
    g = P['g']
    L = g['L']
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2

    ribs = [_Env([(t, v) for t, r, v in P['xy'] if r == k], 0.16) for k in range(7)]
    xyany = _Env([(t, v) for t, r, v in P['xy']], 0.2)
    bass = _Env([(t, v) for t, m, v in P['bs']], 0.35)
    bpitch = [m for t, m, v in P['bs']]
    drk = {k: _Env([(t, v) for t, kk, v in P['dr'] if kk in ks], tau) for k, ks, tau in
           (('kick', ('kick', 'tom'), 0.12), ('snare', ('snare',), 0.09), ('ride', ('ride',), 0.18),
            ('crash', ('crash', 'tss'), 0.45), ('click', ('click',), 0.12), ('tom', ('tom',), 0.12))}
    fxe = {k: _Env([(t, 127) for t, x, kk, i in P['fx'] if kk in ks], tau) for k, ks, tau in
           (('contact', ('bonk', 'wall', 'land', 'hop', 'home'), 0.14), ('wall', ('wall',), 0.3))}
    wig = rng.uniform(0, 2 * np.pi, 8)
    fade = lambda t: 1 - smoothstep(D - 1.8, D - 0.2, t)

    def spot(name, t):
        sec = None
        if TTS <= t < TBS:
            sec = 'tb'
        elif TBS <= t < TDS:
            sec = 'bs'
        elif TDS <= t < TL:
            sec = 'dr'
        if sec is None:
            return 1.0
        return 1.25 if name == sec else 0.82

    def wild(t):                             # how carried away the drummer is
        if t < TDS:
            return 0.0
        return float(np.clip((t - TDS) / (TL - TDS), 0, 1)) ** 1.5

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        bone, glow, gold = [], [], []
        fog = 0.13 * smoothstep(0, 1.5, t) * fade(t) * np.ones(G.N)
        fog *= 1 + 0.25 * np.sin(pdp / 140 + 0.4 * t) * np.sin(pdp / 61 - 0.27 * t)
        fl = flight(g, t)
        sx = fl[0] if fl else None

        def duck(name):
            if sx is None or t >= TLAND:
                return 0.0
            return float(np.exp(-((sx - g['centre'][name]) / 120) ** 2))

        def sp(lst, head, dr_, u0, u1, wt):
            a, b = head + dr_ * u0, head + dr_ * u1
            lst.append((min(a, b), max(a, b), wt))

        def skull(head, dr_, u, I, eye=1.0, look=0.0, eyecol=None, size=1.0):
            s = K * size
            sp(bone, head, dr_, u, u + 32 * s, 1.3 * I)
            for v0, v1 in ((7, 12), (20, 25)):
                sp(bone, head, dr_, u + v0 * s + look, u + v1 * s + look, -1.3 * I)
                sp(glow if eyecol is None else gold, head, dr_, u + v0 * s + look, u + v1 * s + look,
                   (0.75 * eye * min(I, 1)) if eyecol is None else eyecol)

        def skel(name, head, dr_, I, gj=1.0, hd=0.0, nrib=5, ribI=None, has_skull=True, look=0.0, neck=0.0):
            eye = 0.0 if ((t + 2.7 * wig[len(name)] / (2 * np.pi)) % 2.7) < 0.13 else 1.0
            if has_skull:
                skull(head, dr_, -hd, I, eye, look)
            u = SKL + GAP * gj
            if not has_skull and neck > 0:   # headless: the neck stump flashes
                sp(bone, head, dr_, u - 3 * K, u, neck)
            for r in range(nrib):
                ri = 1.0 if ribI is None else ribI[r]
                sp(bone, head, dr_, u + 8 * K * r, u + 8 * K * r + 5 * K, 0.85 * I * ri)
            u += K * (8 * (nrib - 1) + 5) + GAP * gj
            sp(bone, head, dr_, u, u + 16 * K, 0.85 * I)
            sp(bone, head, dr_, u + 7 * K, u + 9 * K, -0.8 * 0.85 * I)
            u += 16 * K + GAP * gj
            sp(bone, head, dr_, u, u + 26 * K, 0.85 * I)
            sp(bone, head, dr_, u, u + 4 * K, 0.25 * 0.85 * I)
            sp(bone, head, dr_, u + 22 * K, u + 26 * K, 0.25 * 0.85 * I)
            u += 26 * K + GAP * gj
            sp(bone, head, dr_, u, u + 22 * K, 0.85 * I)
            u += 22 * K + GAP * gj
            sp(bone, head, dr_, u, u + 5 * K, 0.85 * I)
            sp(bone, head, dr_, u + 7 * K, u + 9 * K, 0.85 * I)
            return u + 9 * K

        def present(name):
            tr = RISE[name]
            if t < tr - 0.6:
                return 0.0, 0.0
            c = g['centre'][name]
            if t < tr + 0.9:
                nonlocal fog
                fog = fog + 0.25 * np.exp(-((pdp - c) / 50) ** 2) * smoothstep(tr - 0.6, tr, t) * \
                    (1 - smoothstep(tr + 0.3, tr + 0.9, t))
            wob = 2.5 * np.sin(2 * np.pi * 11 * t) * (1 - smoothstep(tr + 0.3, tr + 0.9, t))
            return float(smoothstep(tr, tr + 0.5, t)) * fade(t), wob

        playing = THD <= t < TLAND
        sway = 4.0 * np.sin(np.pi * (t - THD) / BEAT) if playing else 0.0
        final = smoothstep(TF - 0.05, TF + 0.15, t) * (1 - smoothstep(TC2 + 0.2, TC2 + 0.7, t))
        tss = float(np.exp(-max(0.0, t - TSS) / 0.35)) if t >= TSS else 0.0

        # ---- xylophonist, Left: plays his ribs ----
        pr, wob = present('xy')
        if pr > 0:
            dk = duck('xy')
            ribI = [0.8 + 1.0 * ribs[k](t) for k in range(7)]
            I = 0.62 * pr * spot('xy', t) * (1 + 0.25 * final + 0.3 * tss)
            head = g['xy'] + wob + sway * 0.5
            look = 0.0
            if TLAND <= t < TF:              # two heads: his own looks up at the new one, and back
                look = -4.0 * K * np.tanh(3 * np.sin(2 * np.pi * 1.25 * (t - TLAND)))
            skel('xy', head, 1, I, gj=(1 - 0.4 * dk) * (1 + 0.5 * final), nrib=7, ribI=ribI, look=look)
            u = SKL + GAP * (1 - 0.4 * dk) * (1 + 0.5 * final)
            for k in range(7):               # the struck rib flashes gold
                e = ribs[k](t)
                if e > 0.01:
                    sp(gold, head, 1, u + 8 * K * k - 1, u + 8 * K * k + 5 * K + 1, 1.1 * e * pr)

        # ---- trombonist, Right: arm-bone slide follows the pitch ----
        pr, wob = present('tb')
        if pr > 0:
            p, on = tb_state(P['tb'], t)
            dk = duck('tb')
            I = 0.62 * pr * spot('tb', t) * (1 + 0.25 * final + 0.3 * tss)
            head = g['tb'] + wob
            skel('tb', head, -1, I * (1 + 0.15 * on), gj=(1 + 0.12 * on) * (1 - 0.45 * dk) * (1 + 0.5 * final))
            ext = slide_ext(p) * (1 - 0.6 * dk)
            th = head + 4                    # mouthpiece, then the fixed tubes, the slide, its crossbar
            bone.append((th, th + 40, (0.45 + 0.45 * on) * pr))
            gold.append((th + 26, th + 40, 0.95 * on * pr))
            bone.append((th + 40, th + 40 + ext, (0.3 + 0.3 * on) * pr))
            bone.append((th + 40 + ext - 5, th + 40 + ext + 1, (0.9 + 0.3 * on) * pr))

        # ---- bassist, Porch Left: plucks a femur ----
        pr, wob = present('bs')
        if pr > 0:
            env = bass(t)
            i = bass.last(t)
            m = bpitch[i] if i >= 0 else 43
            dk = duck('bs')
            I = 0.62 * pr * spot('bs', t) * (1 + 0.25 * final + 0.3 * tss)
            head = g['bs'] + wob
            skel('bs', head, 1, I, gj=(1 + 0.12 * env) * (1 - 0.4 * dk) * (1 + 0.5 * final))
            f0, fl_ = g['fem0'] + wob, g['fem']
            nsub = 16
            mode = 2 + (m % 3)
            for j in range(nsub):
                u = (j + 0.5) / nsub
                vib = env * (0.3 + 0.35 * np.sin(np.pi * mode * u) ** 2 * (0.6 + 0.4 * np.cos(2 * np.pi * 9 * t)))
                knob = 0.25 if j in (0, nsub - 1) else 0.0
                bone.append((f0 + fl_ * j / nsub, f0 + fl_ * (j + 1) / nsub, (0.45 + knob + vib) * pr))
            fr = f0 + fl_ * (0.92 - 0.8 * np.clip((m - 31) / 22, 0, 1))   # fret spot: low notes at the far end
            gold.append((fr - 5, fr + 5, 1.2 * env * pr))

        # ---- drummer, Porch Front, and the kit on the porch corners ----
        pr, wob = present('dr')
        if pr > 0:
            wd = wild(t)
            kick, snare, click = drk['kick'](t), drk['snare'](t), drk['click'](t)
            I = 0.62 * pr * spot('dr', t) * (1 + 0.25 * final + 0.3 * tss)
            has = not (TL <= t < TLD)
            hd = (5 + 30 * wd) * snare + 10 * click
            gj = (1 - 0.22 * kick * (1 + wd)) * (1 + 0.6 * wd * np.abs(np.sin(2 * np.pi * (t - TDS) / BEAT)))
            gj *= 1 + 0.5 * final
            if TL <= t < TLAND:               # lunges after his head as it goes past
                gj *= 1 + 0.9 * duck('dr')
            head = g['dr'] + wob
            skel('dr', head, -1, I * (1 + 0.3 * click + 0.2 * snare), gj=gj, hd=hd, has_skull=has,
                 neck=(0.4 + 0.8 * click) * pr)
            k0, k1 = g['kick']               # skull kick drum: amber sockets on every kick
            kI = (0.5 + 0.5 * kick) * pr
            ks = (k1 - k0) / 32
            bone.append((k0, k1, 1.2 * kI))
            for v0, v1 in ((8, 13), (19, 24)):
                bone.append((k0 + v0 * ks, k0 + v1 * ks, -1.2 * kI))
                gold.append((k0 + v0 * ks, k0 + v1 * ks, (0.25 + 0.9 * kick) * pr))
            s0, s1 = g['snare']               # pelvis snare
            roll = 0.0
            for rt, rd, kind in P['rolls']:
                if kind == 'snare' and rt <= t < rt + rd:
                    roll = (0.4 + 0.6 * (t - rt) / rd) * abs(np.sin(2 * np.pi * 9 * t))
            sI = (0.5 + 0.6 * max(snare, roll)) * pr
            bone.append((s0, s1, sI))
            bone.append((s0 + 9, s1 - 9, -0.7 * sI))
            c0, c1 = g['cym']                 # gold cymbal; crashes splash outward
            cr = drk['crash'](t)
            croll = 0.0
            for rt, rd, kind in P['rolls']:
                if kind == 'cym' and rt <= t < rt + rd:
                    croll = (0.3 + 0.5 * (t - rt) / rd) * (0.7 + 0.3 * np.sin(2 * np.pi * 13 * t))
            gold.append((c0, c1, (0.35 + 0.6 * drk['ride'](t) + 0.8 * cr + croll) * pr))
            if cr > 0.03:
                sprd = 40 * (1 - cr) + 6
                gold.append((c0 - sprd, c0 - sprd + 6, 0.6 * cr * pr))
                gold.append((c1 + sprd - 6, c1 + sprd, 0.6 * cr * pr))

        # ---- the skull: launched, bouncing, perched on the wrong neck, hopping home ----
        if fl is not None:
            x, h, ce = fl
            th = 2 * np.pi * 1.6 * (t - (TL if t < TLAND else TH0))
            Isk = (0.7 + 0.45 * ce) * fade(t)
            bone.append((x - R * (1 + 0.25 * ce), x + R * (1 + 0.25 * ce), 1.3 * Isk))
            for a in (th - 0.45, th + 0.45):
                if np.cos(a) > 0.05:
                    p = x + R * np.sin(a)
                    hw = 2.5 * K * np.cos(a)
                    bone.append((p - hw, p + hw, -1.3 * Isk))
                    glow.append((p - hw, p + hw, 0.75 * np.cos(a)))
            if ce > 0.02:                    # a puff off the roof where it lands
                fog = fog + 0.35 * ce * np.exp(-((pdp - x) / 30) ** 2)
            v = (x - flight(g, t - DT)[0]) / DT if flight(g, t - DT) else 0.0
            if abs(v) > 200:
                s = -np.sign(v)
                for q, k in enumerate((0.4, 0.22, 0.1)):
                    a, b = x + s * (R + 12 * q), x + s * (R + 12 * (q + 1))
                    bone.append((min(a, b), max(a, b), k * Isk))
        elif TLAND <= t < TH0:               # sitting on the xylophonist's head, looking down at him
            xl = g['xl']
            Iw = 0.62 * (1 + 0.25 * final + 0.6 * np.exp(-(t - TLAND) / 0.15)) * fade(t)
            look = 4.0 * K * np.tanh(3 * np.sin(2 * np.pi * 1.25 * (t - TLAND) + np.pi)) if t < TF else 0.0
            skull(xl - R, 1, 0.0, Iw, 1.0, look)

        sp_ = np.array(bone) if bone else np.zeros((0, 3))
        ov = np.clip(np.minimum(sp_[:, 1:2], e1) - np.maximum(sp_[:, 0:1], e0), 0, None) / w
        Ib = np.clip(sp_[:, 2] @ ov, 0, 1)
        cov = np.clip(np.abs(sp_[:, 2:3] * ov).sum(0), 0, 1)
        Ig, Iy = np.zeros(G.N), np.zeros(G.N)
        if glow:
            gp = np.array(glow)
            gv = np.clip(np.minimum(gp[:, 1:2], e1) - np.maximum(gp[:, 0:1], e0), 0, None) / w
            Ig = np.clip(gp[:, 2] @ gv, 0, 0.9)
        if gold:
            gp = np.array(gold)
            gv = np.clip(np.minimum(gp[:, 1:2], e1) - np.maximum(gp[:, 0:1], e0), 0, None) / w
            Iy = np.clip(gp[:, 2] @ gv, 0, 1)
        buf = light(BONE, Ib) + light(GLOW, Ig) + light(GOLD, Iy) + light(FOG, fog * (1 - cov))
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# An original minor swing in G at 150 BPM. Only what you can see plays: the xylophone is the ribs (a G blues scale,
# one note per rib), the pizzicato double bass is the femur, the trombone glides exactly where the slide goes
# (samples are varispeeded along the same pitch curve), and the kit is the skull kick, pelvis snare and gold cymbal.
# The bouncing skull is a log drum and a marimba knock on every landing, with slide-whistle boings off the ends.

def _gliss(inst, t_kf, vel, dur, SR):
    """A sustained sample bent along keyframes [(seconds, midi)...] by varispeed."""
    nb = int(round(t_kf[0][1]))
    raw = inst.play(nb, vel)
    n = int((dur + 0.15) * SR)
    tt = np.arange(n) / SR
    semis = np.interp(tt, [k[0] for k in t_kf], [k[1] for k in t_kf]) - nb
    idx = np.cumsum(2 ** (semis / 12)) - 1
    idx = idx[idx < raw.shape[1] - 1]
    out = np.vstack([np.interp(idx, np.arange(raw.shape[1]), raw[c]) for c in range(2)])
    s = int(dur * SR)
    if s < out.shape[1]:
        e = min(out.shape[1], s + int(0.12 * SR))
        out = out[:, :e].copy()
        out[:, s:e] *= np.linspace(1, 0, e - s) ** 2
    a = min(out.shape[1], int(0.012 * SR))
    out[:, :a] *= np.linspace(0, 1, a)
    return out


def score(M, G):
    from pixelhome.audio import note, slide, whoosh, SR
    P = _plan(G)
    g = P['g']
    xylo = M.sampler('Percussion/Xylo/*.wav')
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tsus = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tstac = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav')
    kick = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    kick_b = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_f_*.wav')
    snare_s = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_mp_[0-9].wav')
    tom = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    ride = M.hits('VSCO 1 Percussion/varMetal/Cymbals/susp/susp_hit_metal_2_mf.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    sroll = M.hits('Percussion/Snare2-rollNS_v5*.wav')
    croll = M.hits('VSCO 1 Percussion/varMetal/Cymbals/susp/susp_hit_softmall_roll2_cresc.wav')
    logd = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum0_ff_*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/claves_mf*.wav')

    for name, gain, rev in (('xylo', 0.45, 0.2), ('bass', 0.4, 0.08), ('brass', 0.5, 0.18), ('drums', 0.62, 0.14),
                            ('cym', 0.32, 0.2), ('perc', 0.55, 0.15), ('mallet', 0.4, 0.2), ('fx', 0.15, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs_, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs_.min(), xs_.max()

    def pan_at(d):
        x = np.interp(d, ds, xs_)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    p_xy, p_bs, p_tb = pan_at(g['centre']['xy']), pan_at(g['centre']['bs']), pan_at(g['centre']['tb'])
    p_dr, p_kick, p_snare = pan_at(g['centre']['dr']), pan_at(np.mean(g['kick'])), pan_at(np.mean(g['snare']))

    for t, r, v in P['xy']:
        M.add('xylo', xylo.play(note(RIB[r]), v), t, 1.0, p_xy)
    for t, m, v in P['bs']:
        M.add('bass', bass.play(m, v), t, 1.0, p_bs)
    for t0, dur, kf, v in P['tb']:
        if dur < 0.3 and len(kf) == 1:
            M.add('brass', tstac.play(kf[0][1], v, dur=dur + 0.1), t0, 1.0, p_tb)
        else:
            M.add('brass', _gliss(tsus, kf, v, dur, SR), t0, 1.0, p_tb)
    for t, kind, v in P['dr']:
        if kind == 'kick':
            M.add('drums', (kick_b if v > 115 else kick).play(v), t, 1.0, p_kick)
        elif kind == 'snare':
            M.add('drums', (snare if v > 80 else snare_s).play(v), t, 0.9, p_snare)
        elif kind == 'tom':
            M.add('drums', tom.play(v), t, 0.9, p_kick)
        elif kind == 'ride':
            M.add('cym', ride.play(v, dur=0.8), t, 0.7, p_snare)
        elif kind == 'crash':
            M.add('cym', crash.play(v), t, 1.6, p_snare)
        elif kind == 'tss':
            M.add('cym', crash_s.play(v), t, 1.8, p_snare)
        elif kind == 'click':
            M.add('perc', clave.play(v), t, 1.0, p_dr)
    for t0, dur, kind in P['rolls']:
        if kind == 'snare':
            M.add('drums', sroll.play(100, dur=dur), t0, 0.8, p_snare)
        else:
            M.add('cym', croll.play(105, dur=dur), t0, 1.4, p_snare)

    knock = ['G3', 'Bb3', 'C4', 'D4', 'F4', 'G4']
    for t, x, kind, k in P['fx']:
        p = pan_at(np.clip(x, 0, g['L']))
        if kind == 'pop':
            M.add('perc', slap.play(120), t, 1.0, p)
            M.add('fx', slide(0.0, 0.3, 500, 1700, 0.35, 0.6), t, 1.0, p)
        elif kind in ('bonk', 'hop'):
            M.add('perc', logd.play(100), t, 0.8, p)
            m = note(knock[k % len(knock)]) if kind == 'bonk' else note(knock[min(k, 5)])
            M.add('mallet', mar.play(m, 100), t, 0.8, p)
        elif kind == 'wall':
            M.add('perc', logd.play(120), t, 1.0, p)
            M.add('drums', timp.play(110), t, 0.7, p)
            M.add('cym', crash_s.play(100), t, 1.0, p)
            M.add('fx', slide(0.0, 0.35, 400, 1400, 0.4, 0.6), t, 1.0, p)
        elif kind == 'land':
            M.add('perc', logd.play(127), t, 1.0, p)
            M.add('perc', wood.play(120), t, 1.0, p)
            M.add('fx', slide(0.0, 0.25, 1400, 600, 0.3, 0.5), t, 0.8, p)
        elif kind == 'lift':
            M.add('fx', slide(0.0, 0.25, 600, 1300, 0.3, 0.5), t, 0.8, p)
        elif kind == 'home':
            M.add('perc', wood.play(120), t, 1.0, p)
            M.add('perc', logd.play(110), t, 0.8, p)
    M.add('fx', whoosh(3.0, 120, 500, 0.4, seed=13), 0.0, 0.3)
    for name, tr in RISE.items():
        M.add('fx', whoosh(0.8, 200, 1200, 0.3, seed=int(tr * 10)), tr - 0.6, 0.4, pan_at(g['centre'][name]))
