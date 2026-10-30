"""The Theft: Alberich stands at the rock with his red reaching for the hard point of gold, the Ring's beads
still circling it, the Rhinemaidens frozen on the far side. He swears off love for ever: the Renunciation of
Love (Donington 76) in his own low voice, bassoon and cellos, each note a pulse of red out of him while the
cold indigo shadow closes in from both ends of the house; then the horns take it up, broad (76b), and his
red crawls over the gold until it flickers.

He tears it from the rock. The Gold's call (Donington 44) is wrenched into the minor on trumpets and
trombones, a string rush up to it, and on its last note the whole house flashes gold and white; then darkness
floods out from the rock to both ends while the low strings wriggle down the Darkness motif (24). He runs with
the glow of the gold in his arms, along the porch and the left wing and down the Side into the depths, a hot
red trail behind him, and his laugh comes back up from below.

The maidens chase into the dark crying "Hold the thief!" and "Save the gold!", and stop at the edge. They
drift back to the empty rock and lament: their falling step in the minor, each sigh a tear of colour sliding
away from them, and the cry "Rheingold! Rheingold!" (31) turned sad, its sunlit C major resolution sinking to
C minor, its sweeps of gold now cold grey-blue. The water turns to rising mist and the maidens sink away into
it. In the last seconds the Ring motif (8) begins, softly, on the horns, and a faint ring of beads starts to
turn over the porch: the transformation that will become Valhalla.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'RG05'
TITLE = 'The Theft'
KIND = 'show'
DESCRIPTION = ('Alberich swears off love for ever, tears the gold from its rock and runs with it down into the '
               'dark. The Rhinemaidens chase him, too late, and their joyful cry turns into a lament as the river '
               'fills with mist.')
VOICEOVER = ('Only someone who gives up love can take the gold. Alberich decides that is a fair price. '
             'The river is about to go dark.')

T_VOW = 3.0                                 # "the love I curse": the renunciation, in his voice
VB = 0.62
T_HORNS = 9.0                               # the horns take it up, broad
HB = 0.42
T_TEAR = 16.0                               # the Gold's call, wrenched into the minor
TB = 0.2
T_RIP = T_TEAR + 4 * TB                     # its last note: the gold comes away
T_FLEE = T_RIP + 0.6
T_OUT = 25.5                                # he is gone down the Side into the depths
CRIES = [19.0, 21.6]                        # "Haltet den Räuber!"
T_SAVE = 24.2                               # "Rettet das Gold!"
T_LAUGH = 27.0                              # his laugh, from below
T_LAMENT = 30.0
SIGHS = [31.0, 33.0, 35.0, 37.0]
LCRY = [40.0, 47.5]                         # "Rheingold!", turned sad
CB = 0.75
T_MIST = 55.0
T_SINK = 59.0
T_XFORM = 68.0                              # the Ring motif begins the transformation
D = 80.0

WOG, WELL, FLO = 0, 1, 2
COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
DEPTHS = hexc('#0c1c8c')
SHADOW = hexc('#1c1880')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
EMBER = hexc('#ff8a20')
MUD = hexc('#5a1200')
COLD = hexc('#7090d0')
MIST = hexc('#6c70b8')
DUSK = hexc('#1c1c70')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def minor(m):
    """E -> E flat, B -> B flat: the major third of C and G turned minor."""
    return m - 1 if m % 12 in (4, 11) else m


def sad_cry(t0):
    """The cry "Rheingold! Rheingold!" (31) with its resolutions in C minor: (time, seconds, [midi], kind)."""
    out, ev = [], {}
    for b, d, n in MOTIFS['rheingold']['notes']:
        ev.setdefault(b, []).append((d, note(n)))
    for b in sorted(ev):
        ms = [m for _, m in ev[b]]
        kind = 'yearn' if note('B4') in ms else 'res' if set(ms) == {note('C5'), note('E5'), note('G5')} else 'tail'
        if kind != 'yearn':
            ms = [m - 1 if m % 12 == 4 else m for m in ms]
        out.append((t0 + b * CB, max(d for d, _ in ev[b]) * CB, ms, kind))
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, 2.5, 'G3', 64, 'stir')                         # the last of the Ring's stirring
    add(0.0, T_TEAR, 'C2', 66, 'trem')
    for t, m, v, d in play('renunciation', T_VOW, VB, -12, 100):
        add(t, d, m, v, 'vow')
    for t0, ch in ((T_VOW, ('C3', 'G3')), (T_VOW + 4 * VB, ('Ab2', 'Eb3')), (T_VOW + 6 * VB, ('F2', 'C3'))):
        for m in ch:
            add(t0, 2 * VB * 1.2 if t0 < T_VOW + 6 * VB else 3.2 * VB, m, 70, 'vowpad')
    for t, m, v, d in play('renunciation_broad', T_HORNS, HB, 0, 104):
        add(t, d, m, v, 'horns')
        add(t, d, m - 12, v - 6, 'tbn')
    for t0, ch in ((0, ('C2', 'G2', 'Eb3')), (4, ('Ab1', 'Eb2', 'C3')), (8, ('F1', 'C2', 'Ab2')),
                   (12, ('G1', 'D2', 'B2'))):
        for m in ch:
            add(T_HORNS + t0 * HB, 4 * HB * 1.05, m, 84 + 4 * (t0 // 4), 'lowpad')
    add(T_HORNS + 8 * HB, T_TEAR - T_HORNS - 8 * HB, 'G4', 70, 'swell')
    add(T_HORNS + 8 * HB, T_TEAR - T_HORNS - 8 * HB, 'D5', 66, 'swell')
    for j in range(14):                                     # the grab: a string rush up to the gold
        add(T_TEAR - 0.7 + j * 0.05, 0.1, note('G3') + j * 2 - (j > 6), 96 + j, 'rush')
    for t, m, v, d in play('gold', T_TEAR, TB, 0, 120):
        add(t, d + (0.8 if t >= T_RIP - 1e-6 else 0), minor(m), v, 'wrench')
    add(T_RIP, 1.5, 'C2', 127, 'hit')
    add(T_RIP, 2.5, 'C3', 116, 'blare')
    dk = [(b, d, n) for b, d, n in MOTIFS['darkness']['notes'] if note(n) < note('Eb4') and b >= 6]
    for b, d, n in dk:                                      # the Darkness motif (24), wriggling down below
        add(T_RIP + 0.4 + (b - 6) * 0.3, d * 0.3, note(n) - 12 + 1, 96, 'dark')
    add(T_RIP + 0.3, T_LAMENT - T_RIP, 'C1', 80, 'abyss')
    for k in range(7):                                      # his flight: runs tumbling down in the low strings
        t0 = T_FLEE + k * 1.0
        for j in range(8):
            add(t0 + j * 0.06, 0.09, note('G3') - k - j * 2, 98 - 2 * k, 'run')
    for t0, vel in ((T_FLEE + 0.3, 104), (T_LAUGH, 84)):
        for j, m in enumerate(('G3', 'Eb3', 'C3', 'G2', 'C2')):
            add(t0 + j * 0.2, 0.15, m, vel - 3 * j, 'laugh')
    thief = [(0, .25, 'D5'), (.25, .25, 'D5'), (.5, .5, 'Eb5'), (1, 1, 'D5'), (2, 1.2, 'G4')]
    for k, tc in enumerate(CRIES):
        for who, dt, tr in ((WOG, 0.0, 0), (WELL, 0.22, -4), (FLO, 0.44, -12)):
            for b, d, n in thief:
                add(tc + dt + b * 0.42, d * 0.42, note(n) + tr + 2 * k, 120, 'sing', who)
        add(tc, 1.0, 'G2', 100, 'stab')
    for who, dt in ((WOG, 0.0), (WELL, 0.3), (FLO, 0.6)):
        for b, d, n in ((0, .5, 'Bb4'), (.5, 1, 'G4'), (2, .5, 'Bb4'), (2.5, 1.5, 'G4')):
            add(T_SAVE + dt + b * 0.42, d * 0.42, note(n) - 12 * (who == FLO), 100, 'sing', who)

    for t0, ch in ((T_LAMENT, ('C3', 'G3', 'Eb4')), (T_LAMENT + 4, ('Ab2', 'Eb3', 'C4')),
                   (T_LAMENT + 8, ('F2', 'C3', 'Ab3')), (T_LAMENT + 12, ('G2', 'D3', 'B3')),
                   (LCRY[1] + 6, ('C3', 'G3', 'Eb4'))):
        for m in ch:
            add(t0, 4.4 if t0 < LCRY[1] else T_MIST + 2 - t0, m, 62, 'pad')
    falls = (('Ab4', 'G4'), ('Eb4', 'D4'), ('C4', 'B3'), ('F4', 'Eb4'))
    for i, (ts, (hi, lo)) in enumerate(zip(SIGHS, falls)):  # their falling step, in the minor
        who = (WOG, WELL, FLO, WOG)[i]
        add(ts, 0.9, hi, 76, 'sing', who)
        add(ts + 0.9, 1.0, lo, 70, 'sing', who)
    for k, tc in enumerate(LCRY):
        for t, d, ms, kind in sad_cry(tc):
            top = sorted(ms)[-3:]
            for who, m in zip((FLO, WELL, WOG), top):
                add(t, d, m - 12 * (who == FLO and k == 1), 64 - 6 * k, 'sing', who)
            for m in ms:
                add(t, d, m, 62 - 6 * k, 'lament')
        for j, m in enumerate((note('C3'), note('Eb3'), note('G3'), note('C4'), note('Eb4'), note('G4'))):
            add(tc - 0.8 + j * 0.12, 1.5, m, 68, 'harp')
    add(T_MIST, T_XFORM + 2 - T_MIST, 'Eb1', 70, 'mistlow')
    for k in range(8):                                      # the mist rising: harp arpeggios climbing, in D flat
        for j, m in enumerate(('Db3', 'Ab3', 'Db4', 'F4', 'Ab4', 'Db5')):
            add(T_MIST + 1.5 + k * 1.6 + j * 0.13, 1.2, note(m) - 2 * (k < 4), 64 + 2 * k, 'harp')
    for m in ('Db4', 'F4', 'Ab4'):
        add(T_MIST + 7.0, D - T_MIST - 7.0, m, 52, 'mist')
    for who, ts, hi, lo in ((FLO, T_SINK, 'C4', 'B3'), (WELL, T_SINK + 1.6, 'Eb4', 'D4'), (WOG, T_SINK + 3.2, 'Ab4', 'G4')):
        add(ts, 1.1, hi, 70, 'sing', who)
        add(ts + 1.1, 1.6, lo, 62, 'sing', who)
    for t, m, v, d in play('ring', T_XFORM, 0.78, -6, 92):  # the Ring, beginning to turn into something else
        if t < D - 0.6:
            add(t, min(d, D - t), m, v, 'ring' if m > note('C3') else 'ringbass')
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
    """Per frame: where each maiden and Alberich are (path distance), and where the gold is."""
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
    for k, off in ((WOG, 150), (WELL, 330), (FLO, 240)):
        set_(k, 0, D, pf + off, 2.0)
    for k, off in ((WOG, 135), (WELL, 315), (FLO, 225)):    # flinching back as he swears
        set_(k, T_VOW, T_RIP, pf + off + 0.4 * bob[k], 2.0)
    for k, dest in ((WOG, at(G, 'Left', 0.3)), (FLO, at(G, 'Left', 0.55)), (WELL, at(G, 'Left', 0.85))):
        set_(k, T_RIP + 1.2, T_LAMENT, dest + bob[k], 2.2 + 0.4 * k)
    for k, off in ((WOG, -150), (WELL, 140), (FLO, -10)):   # back to the empty rock, swaying round it
        set_(k, T_LAMENT, D, pf + off + 1.5 * bob[k], 0.7)
    A = pf - 45
    set_(3, 0, D, A + 4 * np.sin(2 * np.pi * t / 0.7), 6.0)
    set_(3, T_TEAR - 0.6, T_RIP, pf - 12, 14.0)             # the lunge for it
    u = smoothstep(T_FLEE, T_OUT, t)
    set_(3, T_RIP, D, (pf - 12) + (-120 - (pf - 12)) * u, 9.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, pos=pos[:3], apos=pos[3])


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    vow = np.array([e[0] for e in N if e[4] == 'vow'])
    horns = np.array([e[0] for e in N if e[4] == 'horns'])
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    sighs = [(e[0], e[5]) for e in N if e[4] == 'sing' and T_LAMENT < e[0] < LCRY[0] and e[1] < 0.95]
    cries = [(t, kind, k) for k, tc in enumerate(LCRY) for t, _, _, kind in sad_cry(tc)]
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    flick = Flicker(rng, 1, 5.0, 11.0)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap = C['apos'][f]

        # the river: RG04's cold shade at the ends, closing in as he swears; then darkness from the rock
        cold = 0.45 + 0.4 * smoothstep(T_VOW, T_HORNS + 4, t)
        reach = (661 + 820 * smoothstep(T_VOW, T_TEAR, t))
        shade = np.clip(np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d))
                        * cold, 0, 1)
        rd = 1800 * smoothstep(T_RIP + 0.1, T_RIP + 2.0, t) ** 0.8
        dark = smoothstep(rd, rd - 160, np.abs(d - pf)) if t > T_RIP else np.zeros(G.N)
        mist = smoothstep(T_MIST, T_MIST + 9, t)
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        water = (1 - 0.7 * shade) * (1 - 0.72 * dark) * (1 - mist)
        warm = 0.12 * (1 - smoothstep(T_VOW, T_HORNS, t))   # the gold's warmth still on the water, draining away
        fr += light(DEEP, (0.2 + 0.1 * w1) * water * (1 - 0.4 * warm))
        fr += light(GREEN, (0.07 + 0.18 * w1 * w2) * water * (1 - 0.6 * dark) * (1 - 0.5 * warm))
        fr += light(GOLD, (0.06 + 0.22 * w1 * w2) * warm * water)
        fr += light(hexc('#ffc840'), 1.0 * warm * (w1 * w2) ** 3 * (0.5 + 0.5 * tw(t)) * water)
        fr += light(SHADOW, 0.3 * shade * (1 - dark) * (1 - mist))
        churn = np.exp(-max(0.0, t - T_OUT) / 8.0)          # black water heaving out from the robbed rock
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - pf) / 420 - 0.45 * t))
        fr += light(DEPTHS, (0.16 + 0.1 * w1 + 0.22 * churn * swell ** 3) * dark * (1 - mist))
        if mist > 0:                                        # mist: slow grey-violet wisps rising off the water
            m1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.05 * t))
            m2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.09 * t) + 2)
            m3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.03 * t) + 4)
            fr += light(DUSK, (0.2 + 0.06 * m3) * mist)
            fr += light(MIST, (0.04 + 0.26 * (m1 * m2) ** 1.5 + 0.08 * m3) * mist)

        # the vow: every note a pulse of red out of him; the horns drag his red over the gold
        for arr, w in ((vow, 1.0), (horns, 0.7)):
            i = int(np.searchsorted(arr, t, side='right')) - 1
            if i >= 0 and t - arr[i] < 1.2:
                age = t - arr[i]
                r = 20 + 700 * age ** 0.6
                fr += light(ALB, 0.85 * w * (1 - age / 1.2) * np.exp(-((np.abs(d - ap) - r) / 50) ** 2))
                fr += light(MUD, 0.5 * w * np.exp(-age / 0.5) * np.exp(-((d - ap) / 300) ** 2))
        lust = 1.0 + 0.6 * smoothstep(T_HORNS, T_TEAR, t)
        gold_on = 1 - smoothstep(T_RIP, T_RIP + 0.05, t)

        # the gold on its rock: hard, then frightened, flickering under his red
        if gold_on > 0:
            fear = smoothstep(T_HORNS, T_TEAR, t)
            fl = 1 - 0.45 * fear * (0.5 + 0.5 * flick(t)[0])
            core = np.exp(-((d - pf) / 36.5) ** 2)
            fr += light(GOLD, gold_on * fl * (0.9 * core + 0.09 * np.exp(-((d - pf) / 264) ** 2) * (1 - 0.7 * shade)))
            fr += light(HOT, gold_on * fl * 0.75 * np.exp(-((d - pf) / 16.4) ** 2))
            # the Ring's beads, spinning faster and redder as he swears, gone when the gold goes
            ring = 0.5 * (1 + 0.6 * smoothstep(T_VOW, T_TEAR, t)) * gold_on
            ph = 0.28 * (t + 31) + 0.25 * max(0.0, t - T_VOW) ** 2 / (T_TEAR - T_VOW)
            th = 2 * np.pi * (np.arange(14) / 14 + ph)
            q, depth = pf + 300 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 24) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            redder = smoothstep(T_HORNS, T_TEAR, t)
            fr += light(GOLD, ring * (0.95 - 0.4 * redder) * front) + light(RED, ring * (0.6 + 0.4 * redder) * back)
        if T_TEAR - 0.7 <= t < T_RIP:                       # the grab: red and gold wrestle on the porch
            u = smoothstep(T_TEAR - 0.7, T_RIP, t)
            fr += light(ALB, 0.5 * u * np.exp(-((d - pf) / (120 + 200 * u)) ** 2) * (0.6 + 0.4 * tw(t)))

        # the theft: a flash over the whole house, a burst out of the rock, then he runs with the glow
        if T_RIP <= t < T_RIP + 2.0:
            age = t - T_RIP
            fr += light(GOLD, 1.0 * np.exp(-age / 0.3) * np.ones(G.N))
            fr += light(WHITE, 0.8 * np.exp(-age / 0.12) * np.ones(G.N))
            r = 1800 * smoothstep(0, 1.6, age)
            fr += light(HOT, 0.9 * np.exp(-((np.abs(d - pf) - r) / 110) ** 2) * (1 - smoothstep(1.0, 2.0, age)))
        gone = smoothstep(380, -60, ap) if t > T_RIP else 0.0
        vis = 1 - gone
        murk = np.exp(-((d - ap) / 220) ** 2)
        fr += light(MUD, 0.3 * murk * (1 + 0.15 * smoulder(t)) * vis)
        fr += light(ALB, 0.85 * np.exp(-((d - ap) / (28 + 6 * (t > T_RIP))) ** 2) * (1 + 0.2 * smoulder(t)) * vis)
        if t < T_RIP:
            ahead = np.clip((d - ap) / max(pf - ap, 1), 0, 1)
            fr += light(ALB, 0.55 * lust * (d > ap) * np.exp(-((d - ap) / (180 + 60 * lust))) * (1 - ahead) ** 0.5
                        * (d < pf + 60))
        else:                                               # the stolen glow in his arms, a hot trail behind
            fr += light(GOLD, 0.85 * vis * np.exp(-((d - ap + 8) / 22) ** 2) * (0.8 + 0.2 * tw(t)))
            fr += light(HOT, 0.5 * vis * np.exp(-((d - ap + 8) / 10) ** 2))
            if t < T_OUT + 1:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 26, 2)):
                    q = C['apos'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 30) ** 2) * (1 - j / 12.5))
                fr += light(EMBER, 0.7 * trail * vis)
        if T_LAUGH <= t < T_LAUGH + 2.0:                    # his laugh, coming up out of the depths
            age = t - T_LAUGH
            pulse = sum(np.exp(-(age - 0.2 * j) / 0.12) for j in range(5) if age >= 0.2 * j)
            fr += light(ALB, 0.35 * pulse * np.exp(-(d / 140) ** 2) * (1 - age / 2))

        # the sad cry: cold sweeps out from the empty rock; the minor resolutions sag the whole house
        sag = 0.0
        for tc, kind, k in cries:
            if not tc <= t < tc + 2.2:
                continue
            age = t - tc
            if kind == 'yearn':
                rf = 1600 * smoothstep(0, 1.4, age)
                band = np.exp(-((np.abs(d - pf) - rf) / 240) ** 2) * (1 - smoothstep(1.2, 2.2, age))
                fr += light(COLD, (0.7 - 0.1 * k) * band)
            elif kind == 'res':
                sag = max(sag, np.exp(-age / 0.9) * (1 - np.exp(-age / 0.1)))
                fr += light(SHADOW, 0.35 * np.exp(-age / 1.2) * np.ones(G.N))
        fr *= 1 - 0.45 * sag

        # the maidens: frozen at first, then crying out into the dark, then lamenting, then sinking into the mist
        thaw = smoothstep(T_RIP, T_RIP + 0.5, t)
        sink = smoothstep(T_SINK, T_SINK + 6, t)
        for k in range(3):
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = np.exp(-(t - sung[k][i]) / 0.2) if i >= 0 and t - sung[k][i] < 1.0 else 0.0
            b = (0.62 + 0.38 * flare) * (0.594 * (1 - thaw) + thaw) * (1 - smoothstep(k * 1.6, k * 1.6 + 5, t - T_SINK))
            trail = np.zeros(G.N)
            if abs(p - C['pos'][k][max(f - 8, 0)]) > 25:
                for j, lag in enumerate((3, 6, 9, 12, 15)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 24) ** 2) * (1 - j / 5.5))
            wide = 1 + 2.5 * sink
            body = np.exp(-((d - p) / ((20 + 10 * flare) * wide)) ** 2)
            fr += light(COLOR[k], b * body + 0.3 * b * np.exp(-((d - p) / 90) ** 2) + 0.45 * b * trail)
            fr += light(WHITE, 0.4 * b * flare * body)
        for ts, who in sighs:                               # each sigh a tear of colour sliding away
            if ts <= t < ts + 2.0:
                age = t - ts
                p0 = np.interp(ts, C['t'], C['pos'][who])
                for sgn in (-1, 1):
                    q = p0 + sgn * 260 * smoothstep(0, 2.0, age)
                    fr += light(COLOR[who], 0.55 * (1 - age / 2.0) * np.exp(-((d - q) / 30) ** 2))

        # the Ring begins to turn into something else: a faint circle of beads over the porch
        rs = 0.32 * smoothstep(T_XFORM - 2, T_XFORM + 4, t)
        if rs > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.5) if ri >= 0 and t - rings[ri] < 2.5 else 0.0
            th = 2 * np.pi * (np.arange(14) / 14 + 0.12 * (t - T_XFORM))
            q, depth = pf + 420 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 26) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            fr += light(GOLD, rs * (1 + 0.5 * rp) * front) + light(RED, 0.6 * rs * (1 + 0.4 * rp) * back)
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
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C['pos'][who] if who is not None else C['apos']))

    for name, gain, rev in (('voices', 0.2, 0.38), ('choir', 0.1, 0.45), ('strings', 0.13, 0.32), ('low', 0.16, 0.15),
                            ('brass', 0.17, 0.3), ('winds', 0.16, 0.35), ('perc', 0.2, 0.25), ('harp', 0.18, 0.45),
                            ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    voice = [M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12), M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12),
             M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)]
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbt = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    bst = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit*.wav')
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
        pa = pan_of(None, t)
        if part == 'sing':
            g = 0.45 if LCRY[0] - 1 < t < T_MIST else 0.75 if t > T_LAMENT else 1.0     # the lament, hushed
            M.add('voices', voice[who].play(m, v, dur=d * 1.05, release=0.25), t, g, pan_of(who, t))
            choir[who].append((t, m, v - 30, d))
        elif part == 'stir':
            M.add('brass', mute.play(m, v, dur=d, release=0.8), t, 0.8, pf)
        elif part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, -0.1, rise=2.0, fall=0.6, gain=0.7)
            hold('low', cbt, m, t, t + d, v, 0.1, rise=3.0, fall=0.6, gain=0.5)
        elif part == 'vow':
            M.add('low', bsn.play(m, v, dur=d, release=0.3), t, 1.0, pa)
            M.add('strings', vc.play(m, v - 8, dur=d, release=0.3), t, 0.8, pa)
        elif part == 'vowpad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.5, fall=0.8, gain=0.6)
        elif part == 'horns':
            M.add('brass', horn.play(m, v, dur=d, release=0.4), t, 1.0, pf - 0.15)
        elif part == 'tbn':
            M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 0.8, pf + 0.15)
        elif part == 'lowpad':
            if m < note('C2'):
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.4), t, 0.7, 0.0)
            hold('low', vc if m >= note('C2') else cb, m + (12 if m < note('C2') else 0), t, t + d, v, 0.0,
                 rise=0.3, fall=0.6, gain=0.6)
        elif part == 'swell':
            hold('strings', vtrem, m, t, t + d, v, -0.3 if m < 70 else 0.3, rise=d * 0.9, fall=0.15, gain=0.7)
            M.add('perc', roll.play(v + 20, dur=d), t, 0.5, pf)
        elif part == 'rush':
            M.add('strings', vn.play(m, v, dur=d * 2, release=0.05), t, 0.7, pf)
        elif part == 'wrench':
            M.add('brass', tpt.play(m + 12, v, dur=d, release=0.3), t, 0.9, pf + 0.1)
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.9, pf - 0.1)
            M.add('brass', horn.play(m + 12, v - 10, dur=d, release=0.3), t, 0.6, pf)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-2), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 1.0, 0.0)
            M.add('perc', gong.play(v), t, 0.9, pf)
            M.add('perc', bd.play(v), t, 0.8, 0.0)
            M.add('low', tuba.play(m, v, dur=d, release=0.6), t, 0.9, 0.0)
            M.add('fx', whoosh(1.4, 3500, 200, 0.6, seed=5), t, 0.9, 0.0)
        elif part == 'blare':
            for x in (0, 3, 7, 12):
                M.add('brass', (tbn if x < 7 else horn).play(m + x, v, dur=d, release=0.8), t, 0.8, pf)
        elif part == 'dark':
            M.add('low', (bsn if m >= note('Bb1') else cb).play(m, v, dur=d, release=0.2), t, 0.9, pa)
            M.add('strings', vc.play(m + 12, v - 14, dur=d, release=0.2), t, 0.5, pa)
        elif part == 'abyss':
            hold('low', cb, m + 12, t, t + d, v, -0.2, rise=1.5, fall=2.0, gain=0.7)
        elif part == 'run':
            M.add('strings', vcs.play(m, v), t, 0.8, pa)
        elif part == 'laugh':
            M.add('low', bst.play(m, v), t, 1.0, pa if t < T_LAUGH else -0.85)
            M.add('brass', tbn.play(m, v - 20, dur=d, release=0.1), t, 0.4, pa if t < T_LAUGH else -0.85)
        elif part == 'stab':
            M.add('perc', timp.play(v, pitch=-5), t, 0.8, -0.3)
            M.add('low', tbn.play(m + 12, v, dur=d, release=0.3), t, 0.6, -0.2)
        elif part == 'pad':
            hold('strings', va if m >= note('G3') else vc, m, t, t + d, v, 0.0, rise=1.0, fall=1.2, gain=0.42)
        elif part == 'lament':
            if m >= note('E4'):
                M.add('strings', vn.play(m, v, dur=d, release=0.5), t, 0.5, 0.2)
            else:
                M.add('low', vc.play(m, v, dur=d, release=0.5), t, 0.6, 0.0)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, -0.6 + 1.2 * (m - 48) / 30)
        elif part == 'mistlow':
            hold('low', trem, m + 24, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.5)
        elif part == 'mist':
            hold('strings', vtrem, m, t, t + d, v, {61: -0.4, 65: 0.0, 68: 0.4}.get(m, 0.0), rise=5.0, fall=0.6,
                 gain=0.45)
        elif part == 'ring':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 0.85, pf)
            M.add('winds', cl.play(m, v - 16, dur=d * 1.05, release=0.5), t, 0.5, pf + 0.2)
        elif part == 'ringbass':
            hold('low', vc, m, t, t + d, v, 0.0, rise=1.0, fall=1.0, gain=0.7)
    for who in range(3):
        M.add('choir', M.synth('Pads/Ooh').render(choir[who], D + 2), 0.0, 1.0, (0.0, 0.5, -0.5)[who])
