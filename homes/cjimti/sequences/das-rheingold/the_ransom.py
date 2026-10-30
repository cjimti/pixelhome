"""The Ransom: grey morning on the mountain, Valhalla dim across the porch, and Wotan wants the hoard. Alberich,
bound, raises the ring to his lips and orders his Nibelungs up out of the earth: a red pulse races from him all
the way to the free end of Right. They come: wave after wave of orange sparks rushes in from the end of Right,
along Right and up Porch Right, each carrying a fleck of gold, to the middle of Porch Front, where they drop it
with a ring of anvils and scurry back the way they came. The Nibelung rhythm drives in the strings, violins
scurry down the house with every wave, and the heap grows, wider and brighter, while trumpets give the Gold's
call (Donington 44) three times as it piles up. Alberich's red shrinks with shame at being seen tied up by his
own slaves, and at his word they flee.

Loge tosses the helmet onto the heap: a violet arc from his hand, the Tarnhelm's chords (Donington 18) on
muted horns, and a violet shimmer crowns the gold. Then Wotan demands the ring as well. Wotan's spear motif
(Donington 73) begins in the trombones; Alberich refuses with everything he has left (his red swelling, the
ring flaring, a frantic bassoon and trombone), and Wotan closes in three times to a rising tremolo and a
timpani roll.

He tears it from his finger: the Ring motif (Donington 8) at full force in trumpets, horns, trombones and tubas
over the G in the basses, a scream, the whole house flashing red. The gold point and its red glint burst out
from Alberich in a ring of beads that sweeps over the entire house, then swirl back in from both ends, gold
toward the street and red turned away, and close onto Wotan's blue as a hard gold point with a red glint.
Alberich sinks to a dim, muddy red. The Ring motif sounds again, softly, in the clarinets, each note a red
glint on Wotan's hand, and the Valhalla motif answers on a muted horn.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG19'
TITLE = 'The Ransom'
KIND = 'show'
DESCRIPTION = ('To buy his freedom, Alberich orders his Nibelungs to carry the whole hoard up to the mountain, '
               'and they pile it up in front of him, helmet and all. Then Wotan wants the ring too, and when '
               'Alberich will not give it, Wotan tears it off his finger.')
VOICEOVER = ('Every scrap of gold he ever made, carried up and heaped at the feet of the gods. '
             'But the god wants one thing more.')

BEAT = 0.5
T_DEMAND = 1.0                              # Wotan: the hoard
T_CALL = 4.5                                # Alberich lifts the ring and orders them up
WAVES = [8.0, 11.5, 15.0, 18.5, 22.0, 25.5, 29.0, 32.5]
PER = 8                                     # Nibelungs in a wave
T_FLEE = 36.0                               # at his word they flee
T_HELM = 40.0                               # Loge tosses the helmet on the heap
T_RINGDEM = 44.5                            # Wotan demands the ring
T_REFUSE = 48.0                             # "my life, but not the ring!"
PUSHES = [51.0, 52.6, 54.2]
T_TEAR = 56.0                               # torn from his finger
RB = 0.55
T_SWIRL = 57.2                              # the beads swirl back in onto Wotan
T_ON = 61.0                                 # the ring is his
T_SOFT = 64.0                               # the Ring again, softly
T_VALH = 72.5
NB = 0.45
D = 80.0

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
STEEL = hexc('#5a88d0')
FORGE = hexc('#ff7a10')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')
WHITE = hexc('#ffffff')

NIB = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
       ('Gb4', 'F4', 'Gb4'), ('F4', 'E4', 'F4'), ('Db4', 'C4', 'Bb3')]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def nibelung(t0, t1, beat, v0, v1):
    out, k = [], 0
    while t0 + k * beat < t1:
        for j, (off, dur) in enumerate(((0, 0.5), (0.5, 1 / 6), (2 / 3, 1 / 3))):
            t = t0 + (k + off) * beat
            u = (t - t0) / (t1 - t0)
            out.append((t, dur * beat * 0.85, note(NIB[k % 6][j]), int(v0 + (v1 - v0) * max(np.sin(np.pi * u), 0) ** 0.5), k, j))
        k += 1
    return out


def nibelungs(G):
    """Each Nibelung of each wave: launch time, speed in, arrival, offset on the heap -> arrays (W, PER)."""
    rng = np.random.default_rng(19)
    launch = np.array(WAVES)[:, None] + np.arange(PER)[None, :] * 0.13 + rng.uniform(0, 0.06, (len(WAVES), PER))
    speed = rng.uniform(560, 760, (len(WAVES), PER))
    off = rng.uniform(-30, 30, (len(WAVES), PER))
    dist = G.length - at(G, 'Porch Front', 0.5) - off
    return launch, speed, off, launch + dist / speed


def compose(G=None):
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Db3', 'Ab3', 'F4'):                          # the grey morning, still hanging
        add(0.0, WAVES[0] - 1.0, m, 62, 'pad')
    for m in ('G2', 'D3', 'Bb3'):                           # the hush before he asks for the ring
        add(T_HELM + 3.0, T_REFUSE + 2.5 - T_HELM - 3.0, m, 66, 'pad')
    for b, d, m in ((0, .5, 'Bb2'), (.5, .5, 'D3'), (1, 1, 'F3'), (2, 1.5, 'Bb2')):
        add(T_DEMAND + b * BEAT, d * BEAT, m, 104, 'wotan')
    for b, d, m in ((0, .5, 'F2'), (.5, .5, 'Bb2'), (1, .5, 'Db3'), (1.5, 1.5, 'F3')):
        add(T_CALL + b * BEAT, d * BEAT, m, 112, 'command')
    for t, m, v, d in play('ring', T_CALL + 1.0, 0.35, 0, 100):
        if t < T_CALL + 1.0 + 4.5 * 0.35 and m > note('C3'):
            add(t, d, m, v, 'ringcall')

    for t, d, m, v, k, j in nibelung(WAVES[0] - 1.0, T_FLEE, NB, 70, 102):
        add(t, d, m, v, 'nib')
        if j == 0:
            add(t, d, m - 24, v - 6, 'nibbass')
    if G is not None:
        launch, speed, off, arrive = nibelungs(G)
        for w, t0 in enumerate(WAVES):
            for j in range(8):
                add(t0 + j * 0.12, 0.08, note('Bb5') - (0, 1, 3, 5, 6, 8, 10, 12)[j], 80, 'scurry', w)
            for k in range(PER):
                add(arrive[w, k], 0.1, 0, 96 + (k == 0) * 20, 'drop', k)
    for i, w in enumerate((2, 5, 7)):
        for t, m, v, d in play('gold', WAVES[w] + 2.0, 0.4, 3, 96 + 8 * i):
            add(t, d, m, v, 'gold')
    for t0 in (13.0, 20.5, 27.5):                           # his shame
        for b, d, m in ((0, 1.5, 'Db3'), (1.5, 1, 'C3'), (2.5, 2.5, 'Bb2')):
            add(t0 + b * BEAT, d * BEAT, m, 82, 'shame')
    for b, d, m in ((0, .5, 'Bb2'), (.5, .5, 'Bb2'), (1, 2, 'Gb2')):
        add(T_FLEE + b * BEAT, d * BEAT, m, 116, 'command')
    add(T_FLEE + 0.2, 1.2, 'C6', 70, 'flee')

    for t, m, v, d in play('tarnhelm', T_HELM + 0.6, 0.4, 0, 76):
        if t < T_HELM + 0.6 + 8 * 0.4:
            add(t, d, m, v, 'tarnhelm')
    add(T_HELM, 0.6, 'Eb5', 80, 'toss')

    for t, m, v, d in play('spear', T_RINGDEM, BEAT, 0, 108):
        if t < T_RINGDEM + 3 * BEAT:
            add(t, d, m, v, 'spear')
    for b, d, m in ((0, .5, 'Gb3'), (.5, .5, 'F3'), (1, .5, 'Gb3'), (1.5, .5, 'A3'), (2, 1.5, 'Bb3'),
                    (4, .5, 'Bb3'), (4.5, .5, 'A3'), (5, 2, 'Gb3')):
        add(T_REFUSE + b * 0.4, d * 0.4, m, 112, 'refuse')
    add(T_REFUSE + 2.5, T_TEAR - T_REFUSE - 2.5, 'G2', 70, 'tension')
    add(T_REFUSE + 2.5, T_TEAR - T_REFUSE - 2.5, 'G1', 80, 'roll')
    for tp in PUSHES:
        add(tp, 0.5, 'G1', 116, 'push')
        for m in ('G2', 'D3', 'G3'):
            add(tp, 0.45, m, 108, 'pushbrass')

    for t, m, v, d in play('ring', T_TEAR, RB, 0, 124):    # full force
        add(t, d, m, v, 'ringtutti')
    add(T_TEAR, 1.4, 'G1', 127, 'tear')
    add(T_TEAR + 0.05, 1.6, 'C6', 120, 'scream')
    add(T_TEAR + 0.05, 1.6, 'B3', 120, 'screambrass')
    for b, d, m in ((0, 1.5, 'Eb3'), (1.5, 1.5, 'D3'), (3, 2, 'C3'), (5, 3, 'B2')):
        add(T_ON + 1.0 + b * 0.45, d * 0.45, m, 84, 'moan')
    for t, m, v, d in play('ring', T_SOFT, 0.75, 0, 76):
        if m > note('C3'):
            add(t, d, m, v, 'ringsoft')
        else:
            add(t, d, m, v - 10, 'ringbass')
    for t, m, v, d in play('valhalla', T_VALH, 0.8, 0, 72, line='melody'):
        add(t, d, m, v, 'valh')
    add(T_VALH, D - T_VALH, 'Db2', 60, 'valhbass')
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
    """Per frame: bound Alberich, Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    A, W, Lg = at(G, 'Porch Front', 0.2), at(G, 'Porch Front', 0.4), at(G, 'Porch Front', 0.75)
    set_(0, 0, D, A + 3 * np.sin(2 * np.pi * t / 2.3), 3.0)
    set_(0, T_REFUSE, T_TEAR + 0.3, A - 8 + 6 * np.sin(2 * np.pi * t / 0.5), 8.0)
    set_(0, T_TEAR + 0.3, D, A - 14, 1.5)
    set_(1, 0, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 2.0)
    set_(1, T_RINGDEM, PUSHES[0], W - 12, 2.0)
    for i, tp in enumerate(PUSHES):
        set_(1, tp, T_TEAR, W - 25 - 18 * i, 10.0)
    set_(1, T_TEAR, T_TEAR + 0.6, A + 30, 16.0)
    set_(1, T_TEAR + 0.6, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 1.2)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(2, 0, D, Lg + jit, 4.0)
    set_(2, T_HELM - 0.6, T_HELM + 0.8, Lg - 20 + jit, 10.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose(G)
    launch, speed, off, arrive = nibelungs(G)
    back = rng.uniform(900, 1200, launch.shape)
    nibs = np.array([e[0] for e in N if e[4] == 'nib'])
    drops = np.array(sorted(arrive.ravel()))
    golds = np.array([e[0] for e in N if e[4] == 'gold'])
    soft = np.array([e[0] for e in N if e[4] == 'ringsoft'])
    tutti = np.array([e[0] for e in N if e[4] == 'ringtutti'])
    refuse = np.array([e[0] for e in N if e[4] == 'refuse'])
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)
    dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
    dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
    wc = grey(WOTAN, 0.4)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def beads(c, R, spin, n, b_front, b_back, w=20):
        th = 2 * np.pi * (np.arange(n) / n + spin)
        q, depth = c + R * np.cos(th), np.sin(th)
        g = np.exp(-((d[:, None] - q[None, :]) / w) ** 2)
        return (light(GOLD, b_front * (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)) +
                light(RED, b_back * (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)))

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        torn = smoothstep(T_TEAR, T_TEAR + 0.05, t)
        tf = last(tutti, t, 0.35)

        # grey dawn on the meadow, Valhalla dim across the porch
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t + 27)))
        lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * (wings + 0.5 * porch)
        fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
        fr += light(grey(VAL, 0.15), 0.34 * merlon)

        # the command: a red pulse racing from Alberich to the free end of Right
        if T_CALL + 0.8 <= t < T_CALL + 3.5:
            a = t - (T_CALL + 0.8)
            q = ap + (L - ap) * smoothstep(0, 1.6, a)
            tail = smoothstep(q - 260, q, d) * (d <= q + 10) * (d >= ap)
            fr += light(ALB, (0.75 * np.exp(-((d - q) / 30) ** 2) + 0.3 * tail) * (1 - smoothstep(1.8, 2.7, a)))
        if T_CALL + 2.4 <= t < WAVES[0] + 1:     # the free end of Right stirring, waiting
            fr += light(FORGE, 0.5 * smoothstep(T_CALL + 2.4, WAVES[0], t) * (0.7 + 0.3 * tw(t)) * blob(L, 60))

        # the Nibelungs: sparks rushing in from the end of Right with gold, dropping it, scurrying back
        route = smoothstep(WAVES[0] - 0.5, WAVES[0] + 1, t) * (1 - smoothstep(T_FLEE + 0.5, T_FLEE + 3, t))
        if route > 0:                                       # their road glows warm while they come and go
            fr += light(FORGE, route * (0.2 + 0.08 * np.cos(2 * np.pi * (d / 120 + 1.5 * t))) * smoothstep(pf + 40, pf + 160, d))
        live = (t >= launch - 0.1) & (t < arrive + 0.15 + (L - pf) / back + 0.2)
        if live.any():
            tin = np.clip(t - launch, 0, None)
            q = np.where(t < arrive, L - speed * tin, pf + off)
            out_ = t >= arrive + 0.15
            q = np.where(out_, pf + off + back * (t - arrive - 0.15), q)
            fleeing = t >= T_FLEE
            q = q[live]
            carry = (t < arrive)[live]
            g = np.exp(-((d[:, None] - q[None, :]) / 11) ** 2)
            fr += light(FORGE, (0.95 * g).max(axis=1) * (1 - 0.35 * fleeing))
            if carry.any():
                fr += light(GOLD, 0.8 * (g[:, carry]).max(axis=1)) + light(HOT, 0.4 * (np.exp(-((d[:, None] - q[carry][None, :]) / 4) ** 2)).max(axis=1))
            trail = np.exp(-((d[:, None] - (q + np.where(carry, 30, -30))[None, :]) / 20) ** 2)
            fr += light(FORGE, 0.4 * trail.max(axis=1))
        if T_FLEE <= t < T_FLEE + 2.0:                       # they flee: a rush of orange out to the end
            a = t - T_FLEE
            qq = pf + (L - pf) * smoothstep(0, 1.2, a)
            fr += light(FORGE, 0.6 * (1 - a / 2.0) * smoothstep(qq - 400, qq, d) * (d <= qq) * (d > pf))

        # the heap: wider and brighter with every Nibelung's drop; the gold call flashes it
        h = np.searchsorted(drops, t) / len(drops)
        dp = last(drops, t, 0.15, 0.6)
        gp = last(golds, t, 0.3)
        hw = 8 + 14 * h
        fr += light(GOLD, (0.3 + 0.6 * h + 0.3 * dp + 0.25 * gp) * blob(pf, hw) + (0.1 + 0.15 * h) * blob(pf, 2 * hw))
        fr += light(HOT, (0.2 + 0.4 * h) * blob(pf, 0.5 * hw) * (0.5 + 0.5 * tw(t)) * (tw(t) > 0))
        if gp > 0.05:
            fr += light(GOLD, 0.4 * gp * np.exp(-((np.abs(d - pf) - 500 * (1 - gp)) / 120) ** 2))
        crown = smoothstep(T_HELM + 0.5, T_HELM + 0.7, t)
        if crown > 0:
            fr += light(TARN, 0.55 * crown * blob(pf, hw + 8) * (0.6 + 0.4 * tw(t)))
        if T_HELM <= t < T_HELM + 0.8:                       # the helmet tossed: a violet arc
            u = smoothstep(T_HELM, T_HELM + 0.6, t)
            q = lp + (pf - lp) * u
            fr += light(TARN, 1.0 * blob(q, 16) + 0.5 * blob(q + 25, 18))

        # Loge; the helmet in his hand until he tosses it
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)
        if t < T_HELM:
            fr += light(TARN, 0.6 * blob(lp, 34) * (0.7 + 0.3 * tw(t)))

        # Wotan: greyed blue; his demand swells him and points a steel line at Alberich
        dem = smoothstep(T_RINGDEM, T_RINGDEM + 1, t) * (1 - smoothstep(T_TEAR, T_TEAR + 1, t))
        pp = sum(np.exp(-(t - tp) / 0.25) for tp in PUSHES if tp <= t < tp + 1.5)
        fr += light(wc, (0.85 + 0.2 * dem + 0.35 * pp) * blob(wp, 22 + 8 * pp) + (0.3 + 0.2 * dem) * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3), 0.25 * blob(wp, 7))
        if dem > 0:
            line = (d < wp) & (d > ap)
            fr += light(SPEAR, 0.45 * dem * line * (0.7 + 0.3 * np.cos(2 * np.pi * (d / 40 + 2 * t))))

        # Alberich: bound; proud as he commands, shrinking with shame, flaring as he refuses, crushed after
        cmd = smoothstep(T_CALL, T_CALL + 0.5, t) * (1 - smoothstep(T_CALL + 2.5, T_CALL + 4, t))
        shame = smoothstep(WAVES[0], WAVES[2], t) * (1 - smoothstep(T_FLEE - 1, T_FLEE + 1, t))
        rf = last(refuse, t, 0.25)
        fight = smoothstep(T_REFUSE, T_REFUSE + 0.5, t) * (1 - torn)
        crushed = smoothstep(T_TEAR + 0.5, T_ON, t)
        ab = (0.72 + 0.3 * cmd - 0.25 * shame + 0.2 * fight + 0.3 * rf) * (1 - 0.45 * crushed)
        fr += light(MUD, (0.32 + 0.12 * crushed) * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
        fr += light(ALB, ab * blob(ap, 24 + 10 * cmd + 8 * fight - 6 * shame) * (1 + 0.2 * smoulder(t)))
        wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
        fr += light(STEEL, (0.8 + 0.3 * pp) * (1 - 0.3 * crushed) * wrap)
        if torn < 1:                                        # the ring still his
            rb = 1 + 0.8 * cmd + 0.6 * rf + 0.4 * fight
            fr += light(GOLD, 0.9 * rb * blob(ap, 6)) + light(RED, 0.7 * rb * blob(ap + 9, 6 + 4 * fight) * (0.6 + 0.4 * tw(t)))

        # torn away: a red flash, a ring of beads bursting over the house, then swirling in onto Wotan
        if T_TEAR <= t < T_TEAR + 1.5:
            a = t - T_TEAR
            fr += light(RED, 0.95 * np.exp(-a / 0.4) * np.ones(G.N))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.08) * blob(ap, 60))
        if T_TEAR <= t < T_SWIRL:
            a = (t - T_TEAR) / (T_SWIRL - T_TEAR)
            fr += beads(ap, 40 + 1500 * a ** 0.6, 0.5 * a, 18, 1.0, 0.8, 26)
        if T_SWIRL <= t < T_ON + 0.6:
            a = smoothstep(T_SWIRL, T_ON, t)
            fr += beads(wp, 1540 * (1 - a) + 10, 0.5 + 1.6 * a ** 1.5, 18, 0.95 + 0.4 * tf, 0.7 + 0.3 * tf, 26 - 12 * a)
        if torn > 0:                                        # on Wotan's hand, its red glint pulsing to the motif
            on = smoothstep(T_ON - 0.5, T_ON + 0.3, t)
            sp = last(soft, t, 0.4) + tf
            fr += light(GOLD, on * (0.95 + 0.3 * sp) * blob(wp, 6))
            fr += light(RED, on * (0.6 + 0.5 * sp) * blob(wp + 9, 6 + 3 * sp) * (0.6 + 0.4 * tw(t)))
            if T_ON <= t < T_ON + 1.0:
                fr += light(HOT, 0.8 * np.exp(-(t - T_ON) / 0.2) * blob(wp, 30))
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
    L = G.length
    pf = at(G, 'Porch Front', 0.5)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C[k]))

    for name, gain, rev in (('winds', 0.18, 0.35), ('strings', 0.15, 0.3), ('low', 0.18, 0.18), ('brass', 0.17, 0.3),
                            ('perc', 0.2, 0.22), ('anvil', 0.14, 0.25), ('fx', 0.08, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
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

    pitch = np.random.default_rng(4).uniform(-6, 4, 8)
    for t, d, m, v, part, who in compose(G):
        pa, pw = pan_of('alb', t), pan_of('wot', t)
        if part == 'wotan':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.9, pw)
            M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.3), t, 0.7, pw)
        elif part == 'command':
            M.add('brass', tbn.play(m, v, dur=d, release=0.2), t, 1.0, pa)
            M.add('winds', bsus.play(m, v - 10, dur=d, release=0.2), t, 0.7, pa)
        elif part == 'ringcall':
            M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.8, pa)
            M.add('fx', whoosh(1.6, 600, 3000, 0.4, seed=7), t, 0.5, 0.6)
        elif part == 'nib':
            M.add('strings', vas.play(m, v), t, 1.0, 0.3)
            M.add('strings', vn.play(m + 12, v - 18), t, 0.6, 0.5)
        elif part == 'nibbass':
            M.add('low', cbs.play(m + 12, v), t, 1.0, 0.1)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.8, 0.1)
        elif part == 'scurry':
            M.add('strings', vn.play(m, v), t, 0.7, pan_at(L - 650 * (t - WAVES[who] + 0.2)))
        elif part == 'drop':
            M.add('anvil', anvil.play(v, pitch=pitch[who]), t, 1.0, pan_at(pf) + 0.05 * (who - 3.5))
        elif part == 'gold':
            M.add('brass', tpt.play(m, v, dur=d, release=0.4), t, 1.0, pan_at(pf) + 0.1)
            M.add('brass', horn.play(m - 12, v - 12, dur=d, release=0.4), t, 0.6, pan_at(pf) - 0.1)
        elif part == 'shame':
            M.add('winds', bsus.play(m, v, dur=d, release=0.3), t, 0.9, pa)
        elif part == 'flee':
            for k in range(10):
                M.add('winds', pic.play(m - 2 * k, v), t + k * 0.06, 0.6, pan_at(pf + (L - pf) * k / 10))
        elif part == 'tarnhelm':
            M.add('brass', mute.play(m, v, dur=d, release=0.6), t, 0.8, pan_at(pf))
        elif part == 'toss':
            for k in range(8):
                M.add('fx', harp.play(note('Eb4') + (0, 3, 7, 11, 12, 15, 19, 23)[k], 90), t + k * 0.06, 1.6,
                      pan_of('loge', t) + (pan_at(pf) - pan_of('loge', t)) * k / 8)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, pw)
            M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.3), t, 0.8, pw)
        elif part == 'refuse':
            M.add('winds', bsus.play(m - 12, v, dur=d, release=0.15), t, 1.0, pa)
            M.add('brass', tbn.play(m - 12, v - 6, dur=d, release=0.15), t, 0.8, pa)
        elif part == 'tension':
            for k, mm in enumerate((m, m + 6, m + 12)):
                hold('strings', vtrem, mm + 12, t, t + d, v + 10 * k, pa + 0.2 * (k - 1), rise=d, fall=0.1, gain=0.6)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, 0.0)
        elif part == 'push':
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, pw)
        elif part == 'pushbrass':
            M.add('brass', (tuba if m < note('D3') else tbn).play(m, v, dur=d, release=0.2), t, 0.7, pw)
        elif part == 'ringtutti':
            if m >= note('E4'):
                M.add('brass', tpt.play(m, v, dur=d, release=0.4), t, 1.0, pw + 0.15)
                M.add('strings', vtrem.play(m + 12, v, dur=d, release=0.4), t, 0.5, pw - 0.2)
            elif m >= note('C4'):
                M.add('brass', horn.play(m, v, dur=d, release=0.4), t, 0.9, pw - 0.15)
                M.add('brass', tpt.play(m, v - 10, dur=d, release=0.4), t, 0.5, pw + 0.15)
            elif m >= note('C3'):
                M.add('brass', horn.play(m, v, dur=d, release=0.4), t, 0.9, pw - 0.1)
                M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 0.8, pw + 0.1)
            else:
                M.add('low', tuba.play(m, v, dur=d, release=0.4), t, 1.0, 0.0)
                hold('low', cb, m, t, t + d, v, 0.0, rise=0.05, fall=1.0, gain=0.8)
        elif part == 'tear':
            M.add('perc', timp.play(v, pitch=-3), t, 1.0, pa)
            M.add('perc', crash.play(124), t, 1.0, 0.0)
            M.add('perc', bd.play(v), t, 0.9, pa)
            M.add('fx', whoosh(1.2, 5000, 300, 0.6, seed=11), t, 0.8, 0.0)
        elif part == 'scream':
            hold('strings', vtrem, m, t, t + d, v, pa, rise=0.05, fall=0.6, gain=0.5)
            for k in range(6):
                M.add('winds', pic.play(m - 1 - 2 * k, v - 6 * k), t + 0.05 * k, 0.6, pa)
        elif part == 'screambrass':
            M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 1.0, pa)
        elif part == 'moan':
            M.add('winds', bsus.play(m - 12, v, dur=d, release=0.3), t, 1.0, pa)
        elif part == 'ringsoft':
            M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, pw)
        elif part == 'ringbass':
            hold('low', vc, m, t, t + d, v, 0.0, rise=0.5, fall=1.5, gain=0.7)
        elif part == 'valh':
            M.add('brass', mute.play(m, v, dur=d * 1.05, release=0.6), t, 0.9, pan_at(pf))
        elif part == 'pad':
            hold('strings', vtrem if m >= note('C4') else trem, m, t, t + d, v, 0.3 * ((m % 3) - 1), rise=1.5, fall=1.5, gain=0.6)
        elif part == 'valhbass':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=1.0, gain=0.6)
