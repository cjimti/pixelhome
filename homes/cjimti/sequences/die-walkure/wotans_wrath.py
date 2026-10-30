"""Wotan's Wrath: the storm that gathered at the free end of Right comes on. A roaring blue-black thunderhead
churns in along the Right wing, over the rock and on across the Left wing and Side until it holds the whole
house, its leading edge a seething band of deep blue, lightning forking through it; the storm (Donington 74)
races in the cellos and basses, and Wotan frustrated (70) groans in the trombones and tubas.

The terrified sisters hide Brünnhilde among them: they rush together on Porch Front and close round her, a
huddled, trembling knot of eight colours with her silver dimmed at its heart, crying out in panic (scraps of
the trilling cry, 22a, on piccolo and trumpets).

Then a stroke of lightning across the whole house and Wotan is there, rising out of the left of the rock in
deep blue, his spear a steel line beside him, the spear motif (73) slamming down in the trombones. "Where is
Brünnhilde?" A declamation in trombones and tubas, every word a fork of lightning and a surge of blue rolling
out from him over the knot; the sisters cry out, shiver, try to soothe him with the descending chords (22b),
hushed; he rages again in his frustrated motif while the storm roars on. Three times he calls her name, each
a thunderclap and a wave of blue breaking over the knot so that the silver inside it flickers. At the end the
storm holds, roaring, and the knot trembles before him, waiting.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK23'
TITLE = "Wotan's Wrath"
KIND = 'show'
DESCRIPTION = ('Wotan comes in a storm that swallows the whole house. The terrified Valkyries hide Brünnhilde in '
               'the middle of a huddle on their rock, and three times, each with a crack of thunder, their father '
               'calls her name.')
VOICEOVER = ('Here comes the storm, and the god inside it is furious. '
             'Her sisters have hidden her, but they cannot hide her for long.')

T_SWEEP = 11.0                              # the thunderhead has the whole house
T_HUDDLE = 1.2                              # the sisters close round her
T_WOTAN = 11.6                              # he is there, in a stroke of lightning
WO = [15.0, 17.6, 20.2]                     # "Wo ist Brünnhild'?"
T_FRUST = [4.0, 26.0]                       # Wotan frustrated
FBEAT = 0.5
T_SOOTHE = 34.0                             # the sisters try to soothe him
CALLS = [41.0, 48.0, 55.0]                  # "Brünnhilde!"
T_HOLD = 62.0
D = 80.0
CLOCK = 80.0 * 22

COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
KNOT = ('Porch Front', 0.66)                # where they hide her
RING = [-60, -44, -28, -12, 12, 28, 44, 60]  # each sister's place in the knot, in path order
STRIKES = [(2.5, 'Right'), (5.0, 'Porch Right'), (7.6, 'Left'), (9.6, 'Side'), (T_WOTAN, 'all'), (24.0, 'Right'),
           (30.0, 'Left'), (36.4, 'Side'), (44.2, 'Right'), (51.2, 'Left'), (58.6, 'Side'), (65.0, 'Right'),
           (70.6, 'Left'), (75.4, 'Side')]
WOTAN_LINE = [(0, 0.5, 'D3'), (0.5, 0.5, 'D3'), (1, 1.5, 'F3'), (2.5, 1.5, 'A2')]  # "Wo ist Brünn-hild'?" (composed)
NAME = [(0, 0.75, 'D3'), (0.75, 0.75, 'A3'), (1.5, 2.5, 'F3')]                    # "Brünn-hil-de!" (composed)
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
WBLUE = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
THUNDER = hexc('#060a24')
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    def panic(t0, beats, vel, k):
        for t, m, v, d in play('valkyrie_cry', t0, 0.3, 0, vel):
            if t < t0 + beats * 0.3:
                add(t, d, m, v, 'panic', k)

    add(0.0, T_SWEEP + 1.0, 'D1', 96, 'roll')
    add(0.0, D, 'D2', 90, 'trem')
    for k in range(int((D - 1.0) / 3.6)):                                       # the storm, racing in the low strings
        t0 = k * 3.6 + 0.2
        vel = 108 if t0 < T_SWEEP + 2 else (100 if t0 < T_HOLD else 94)
        for t, m, v, d in play('storm', t0, 0.3, 0, vel):
            add(t, d * 1.05, m, v, 'storm')
    for k, tf in enumerate(T_FRUST):                                            # Wotan frustrated
        for t, m, v, d in play('wotan_frustrated', tf, FBEAT, 0, 108 + 6 * k):
            add(t, d * 1.05, m, v, 'frust')
    for j, tp in enumerate((T_HUDDLE, 3.6, 6.2, 8.4)):                          # the sisters, panicking
        panic(tp, 3, 90, (4, 0, 7, 2)[j])
    add(T_WOTAN - 1.2, 1.2, 'D1', 110, 'surge')
    add(T_WOTAN, 3.0, 'D1', 124, 'crash')
    for t, m, v, d in play('spear', T_WOTAN + 0.2, 0.36, 0, 124):               # his spear
        add(t, d * 1.1, m, v, 'spear')
    for tw in WO:                                                               # "Wo ist Brünnhild'?"
        for b, dd, n in WOTAN_LINE:
            add(tw + b * 0.32, dd * 0.32 * 1.15, n, 116, 'wotan')
        panic(tw + 1.5, 2, 84, int(tw) % 8)
    for t, m, v, d in play('valkyries_descent', T_SOOTHE, 0.7, -12, 80):        # the sisters, soothing him
        add(t, d * 1.2, m, v, 'soothe')
    add(T_SOOTHE, 3.5, 'E2', 70, 'soothepad')
    for i, tc in enumerate(CALLS):                                              # "Brünnhilde!"
        add(tc - 0.8, 0.8, 'D1', 104 + 6 * i, 'surge')
        for b, dd, n in NAME:
            add(tc + b * 0.4, dd * 0.4 * 1.15, note(n) + i, 118 + 3 * i, 'call')
        add(tc, 2.5, 'D1', 120, 'crash')
        panic(tc + 1.8, 4, 92, (3, 6, 1)[i])
    for t, m, v, d in play('wotan_frustrated', T_HOLD + 2.0, 0.65, 0, 100):
        if t < D - 3.0:
            add(t, d * 1.05, m, v, 'frust')
    for m in ('D2', 'A2', 'F3'):                                                # the storm holds, waiting
        add(T_HOLD, D - T_HOLD, m, 82, 'menace')
    for ts, where in STRIKES:
        add(ts, 2.0, 'D1', 124 if where == 'all' else 104, 'thunder', where)
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def sway(G, k, tt):
    """Where a sister wheels on the rock, in her place (shared with the scenes either side)."""
    return at(G, *SPOTS[k]) + 9 * np.sin(2 * np.pi * (0.31 * tt + k / 8)) + 4 * np.sin(2 * np.pi * (0.73 * tt + k / 3))


def tremble(k, tt):
    """A sister shaking in the knot (shared with the next scene)."""
    return 3.5 * np.sin(2 * np.pi * (5.3 * tt + k / 8)) + 2.0 * np.sin(2 * np.pi * (8.1 * tt + k / 3))


def choreography(G):
    """Per frame: the sisters, Brünnhilde, Wotan, and the storm's leading edge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    tt = t + CLOCK
    K = at(G, *KNOT)
    pos = np.zeros((8, F))
    for k in range(8):
        go = T_HUDDLE + 0.25 * abs(k - 3.5)
        knot = K + RING[k] + tremble(k, tt)
        w = smoothstep(go, go + 2.2, t)
        pos[k] = sway(G, k, tt) + (knot - sway(G, k, tt)) * w
    B0 = at(G, 'Porch Front', 0.55)
    bpos = B0 + (K - B0) * smoothstep(T_HUDDLE + 0.5, T_HUDDLE + 3.0, t)
    wpos = np.full(F, at(G, 'Porch Front', 0.3))
    front = np.interp(t, (0.0, 4.5, T_SWEEP), (L - 120, at(G, 'Porch Right', 0.2), -120.0))
    return dict(t=t, pos=pos, bpos=bpos, wpos=wpos, front=front)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def thunderhead(fr, d, tt, front, amt):
    """Wotan's storm: a blue-black mass rolling in past `front` (path distance), a roaring blue edge (WK22-WK24).
    amt may be per pixel."""
    inside = 1 / (1 + np.exp(-(d - front) / 45))
    churn = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.17 * tt))) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 140 - 0.29 * tt)))
    edge = np.exp(-((d - front) / 70) ** 2)
    fr = fr * (1 - 0.75 * amt * inside)[:, None]
    return (fr + light(THUNDER, 0.9 * amt * inside) + light(WBLUE, amt * (0.1 + 0.55 * churn ** 2) * inside)
            + light(WBLUE, 0.7 * amt * edge * (0.7 + 0.3 * churn)))


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}
    K = at(G, *KNOT)
    words = np.array([e[0] for e in N if e[4] in ('wotan', 'call', 'spear')])
    calls = np.array([e[0] for e in N if e[4] == 'call'])
    panic = [np.array([e[0] for e in N if e[4] == 'panic' and e[5] == k and e[2] >= note('B4')]) for k in range(8)]
    soothe = np.array([e[0] for e in N if e[4] == 'soothe'])
    fl_ = Flicker(rng, 1, 4.0, 9.0)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def bolt(age, a, b, k):
        """A fork of lightning from a to b: grows in 60 ms, flickers three times, gone in a second."""
        if not 0 <= age < 1.0:
            return np.zeros(G.N)
        reach = a + (b - a) * min(1.0, age / 0.06)
        lo, hi = min(a, reach), max(a, reach)
        fl = sum(np.exp(-((age - s) / 0.04) ** 2) for s in (0.0, 0.12, 0.3)) + 0.45 * np.exp(-age / 0.3)
        return ((d >= lo) & (d <= hi)) * jag[k % len(jag)] * min(fl, 1.2)

    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        fr = rock_bed(d, tt, porch, stone)
        pw, pb = C['wpos'][f], C['bpos'][f]

        # the thunderhead: rolling in from the free end of Right until it has the whole house, lighter on the rock
        amt = (0.6 + 0.4 * smoothstep(0, T_SWEEP, t)) * (1 - 0.5 * porch * smoothstep(3.0, 7.0, t))
        fr = thunderhead(fr, d, tt, C['front'][f], amt)

        # Wotan: rising out of the rock in lightning; every word a surge of blue rolling out over the knot
        wv = smoothstep(T_WOTAN - 0.1, T_WOTAN + 0.4, t)
        if wv > 0:
            wd = last(words, t, 0.3, 1.5)
            wb = wv * (0.85 + 0.25 * wd)
            fr += light(WBLUE, wb * blob(pw, 34 + 8 * wd) + 0.35 * wb * blob(pw, 180))
            fr += light(SPEAR, wv * (0.55 + 0.35 * wd) * smoothstep(pw + 20, pw + 40, d) * smoothstep(pw + 150, pw + 120, d))
            fr += light(WHITE, 0.3 * wd * wv * blob(pw, 10))
            for tw_ in words:
                if tw_ <= t < tw_ + 1.4 and tw_ >= T_WOTAN:
                    age = t - tw_
                    r = 30 + 700 * smoothstep(0, 1.2, age)
                    fr += light(WBLUE, 0.6 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 80) ** 2))
        if T_WOTAN <= t < T_WOTAN + 1.5:                                        # his arrival
            age = t - T_WOTAN
            fr += light(WHITE, 1.0 * np.exp(-age / 0.15) * blob(pw, 60)) + light(FLASH, 0.5 * np.exp(-age / 0.2) * np.ones(G.N))

        # the knot: eight colours closed round her silver, trembling; her silver dimmed, flickering when he calls
        cl = last(calls, t, 0.6, 3.0)
        hide = smoothstep(T_HUDDLE + 0.5, T_HUDDLE + 3.0, t)
        bb = 0.8 - 0.35 * hide - 0.15 * cl * max(0.0, float(fl_(t)[0]))
        fr += light(SILVER, bb * blob(pb, 18 - 9 * hide) + 0.3 * bb * blob(pb, 80 - 50 * hide))
        for kg in range(3):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, (0.65 - 0.35 * hide) * blob(q, 5))
        sh = last(soothe, t, 0.5, 1.5)
        for k in range(8):
            p = C['pos'][k][f]
            pn = last(panic[k], t, 0.15, 0.6)
            b = 0.76 + 0.04 * hide + 0.3 * pn + 0.1 * sh - 0.15 * cl
            fr += light(COLS[k], b * blob(p, 16 - 8 * hide) + (0.35 - 0.2 * hide) * b * blob(p, 75 - 45 * hide))
            fr += light(WHITE, 0.4 * pn * blob(p, 6))
        if hide > 0.5:                                                          # the knot's glow on the rock round it
            fr += light(SILVER * 0.4 + WBLUE * 0.2, 0.2 * hide * blob(K, 90) * (1 - 0.5 * cl))
        sw = ((t - 0.2) / 3.6) % 1.0                                            # swells of the storm rolling out from him
        src = pw if wv > 0 else C['front'][f]
        fr += light(WBLUE, 0.5 * (1 - sw) * np.exp(-((np.abs(d - src) - 1600 * sw) / 160) ** 2) * (1 - 0.6 * porch))

        # lightning
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if not 0 <= age < 1.0:
                continue
            if where == 'all':
                fr += light(WHITE, 0.8 * bolt(age, pw, 0.0, i) + 0.8 * bolt(age, pw, L, i + 1))
                continue
            a, b = seg_d[where]
            mid = 0.5 * (a + b)
            fr += light(WHITE, 0.95 * bolt(age, b if i % 2 else a, mid, i))
            fr += light(FLASH * 0.5 + WBLUE * 0.5, 0.45 * np.exp(-age / 0.2) * blob(mid, 0.7 * (b - a)))
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

    def front_pan(t):
        return pan_at(float(np.clip(np.interp(t, C['t'], C['front']), 0, G.length)))

    for name, gain, rev in (('brass', 0.21, 0.3), ('low', 0.21, 0.2), ('strings', 0.16, 0.3), ('winds', 0.14, 0.3),
                            ('perc', 0.2, 0.28), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    seg_mid = {s: float(G.pd[G.seg[s]].mean()) for s in G.seg}
    wp = pan_at(at(G, 'Porch Front', 0.3))
    kp = pan_at(at(G, *KNOT))
    for t, d, m, v, part, who in compose():
        if part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, front_pan(t))
        elif part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=0.05, fall=1.5, gain=0.55)
            hold('strings', vtrem, m + 24, t, t + d, v - 14, 0.0, rise=0.05, fall=1.5, gain=0.3)
        elif part == 'storm':
            pa = front_pan(t) if t < T_SWEEP else 0.0
            M.add('low', cbs.play(m + 12, v), t, 0.8, pa - 0.15)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.7, pa + 0.15)
            if d > 0.15:
                M.add('low', vc.play(m + 12, v - 16, dur=d, release=0.2), t, 0.4, pa)
        elif part == 'frust':
            pa = wp if t > T_WOTAN else front_pan(t)
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.95, pa)
            M.add('low', tuba.play(m - 12, v - 8, dur=d, release=0.3), t, 0.75, pa)
        elif part == 'panic':
            pa = pan_at(np.interp(t, C['t'], C['pos'][who]))
            if m >= note('B4'):
                M.add('winds', pic.play(m, v), t, 0.6, pa)
                M.add('winds', fl.play(m - 12, v - 10), t, 0.4, pa)
            else:
                M.add('brass', tpt.play(m + 12, v - 16, dur=d, release=0.1), t, 0.4, pa)
        elif part == 'surge':
            M.add('perc', roll.play(v, dur=d + 0.2), t, 0.8, wp)
            M.add('fx', whoosh(d + 0.2, 300, 3000, 0.6, seed=int(t * 10)), t, 0.7, wp)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, wp)
            M.add('perc', gong.play(v), t, 0.7, wp)
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, wp)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, wp)
            M.add('low', tuba.play(m - 12, v - 6, dur=d, release=0.3), t, 0.85, wp)
            M.add('brass', horn.play(m, v - 16, dur=d, release=0.3), t, 0.5, wp)
        elif part in ('wotan', 'call'):
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, wp)
            M.add('low', tuba.play(m - 12, v - 10, dur=d, release=0.3), t, 0.7, wp)
            if part == 'call':
                M.add('brass', horn.play(m + 12, v - 12, dur=d, release=0.3), t, 0.6, wp)
                if t == min(abs(t - c) for c in CALLS) or any(abs(t - c) < 0.01 for c in CALLS):
                    M.add('perc', timp.play(v, pitch=-6), t, 0.9, wp)
        elif part == 'soothe':
            if m >= note('B3'):
                M.add('strings', vn.play(m, v, dur=d, release=0.4), t, 0.6, kp)
                M.add('brass', horn.play(m - 12 if m >= note('F4') else m, v - 10, dur=d, release=0.4), t, 0.5, kp)
            else:
                M.add('strings', va.play(m + 12, v - 10, dur=d, release=0.4), t, 0.5, kp)
        elif part == 'soothepad':
            hold('strings', vc, m + 12, t, t + d, v, kp, rise=0.5, fall=1.0, gain=0.5)
        elif part == 'menace':
            s = tbn if m >= note('A2') else tuba
            hold('brass', s, m + (12 if s is tuba else 0), t, t + d, v, wp, rise=3.0, fall=1.0, gain=0.5)
            hold('low', cb, m + 12, t, t + d, v - 10, 0.0, rise=3.0, fall=1.0, gain=0.3)
        elif part == 'thunder':
            pt = wp if who == 'all' else pan_at(seg_mid[who])
            M.add('perc', bd.play(v), t, 0.8, pt)
            M.add('perc', timp.play(v, pitch=-9), t, 0.7, pt)
            M.add('perc', roll.play(v - 36, dur=d), t + 0.1, 0.4, pt)
            M.add('fx', whoosh(1.2, 2500, 200, 0.6, seed=int(t * 10) + 5), t, 0.6, pt)
