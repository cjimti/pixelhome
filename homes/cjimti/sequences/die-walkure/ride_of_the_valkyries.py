"""Ride of the Valkyries: Act III, the Valkyries' rock. The porch is the rock, still and dark; the wings and
Side are the storm clouds the sisters ride through, slate billowing over navy, lit from inside by lightning.

It opens with the trilling cries (Donington 22a) shivering across the clouds in flutes, piccolo and violins, and
string runs flying up in B minor. Then the Ride (47) in 6/8, the horns first over galloping cellos and basses:
four phrases to a period (B minor, D major, B minor, A), every long note a gust through the clouds, and
between the periods the descending chords (22b) pour down the whole house from the free end of Right to the
far end of Side while the trills flicker. Each period the orchestra grows: trumpets join, then trombones,
then tubas and timpani.

The sisters arrive one by one through the storm, each in her own colour, each with a fallen hero slung over
her saddle (a small dim light riding just behind her): Gerhilde (red) bursting out of the clouds on the Left
wing, Helmwige (sky blue) galloping in from the free end of Right, Waltraute (yellow) out of the Left wing's
clouds, Schwertleite (green) from the free end, Ortlinde (orange) out of the clouds on the Left, Siegrune
(violet blue) out of the clouds on the Right wing, and last Grimgerde (purple) and Rossweisse (pink) riding
in together from the free end. Each one cries "Hojotoho!" as she comes (a trumpet call, every note a flash of
her colour and a ring flying out from her), and "Heiaha!" as she lands on the rock with a burst of light; then
she wheels there in her place, her hero laid beside her, flaring with every note of the Ride. By the end all
eight ride in a rainbow across the rock.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK20'
TITLE = 'Ride of the Valkyries'
KIND = 'show'
DESCRIPTION = ('The Valkyries, the eight warrior daughters of Wotan, come galloping one by one through the storm '
               'clouds to their mountain rock, each in her own colour, each carrying a fallen hero over her '
               'saddle and shouting her battle cry as she lands.')
VOICEOVER = ('High on a mountain, above the clouds, Wotan\'s warrior daughters are coming home. '
             'Hold on to something.')

RB = 0.3                                    # a quarter note of the Ride (a bar of 6/8 is 0.9 s)
C0 = 4.0                                    # the first period of the Ride
CYCLE = 36 * RB                             # a period (four phrases, 24 beats) and an interlude (12 beats)
NCYC = 7
DB = 0.5                                    # the descending chords, a little broader
TRANS = [0, 3, 0, -2]                       # the four phrases: B minor, D major, B minor, A
ROOTS = ['B1', 'D2', 'B1', 'A1']
D = 80.0
CLOCK = 80.0 * 19

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
# who arrives in each cycle, and how: out of the clouds at a point on a front run, or in from the free end of Right
ARRIVALS = [([0], ('Left', 0.45)), ([4], 'end'), ([2], ('Left', 0.7)), ([3], 'end'), ([1], ('Left', 0.25)),
            ([5], ('Right', 0.55)), ([6, 7], 'end')]
STRIKES = [(1.6, 'Right'), (8.6, 'Side'), (17.0, 'Right'), (27.4, 'Left'), (38.2, 'Side'), (49.6, 'Right'),
           (60.2, 'Left'), (70.4, 'Side'), (76.8, 'Right')]
HOJO = [(0, 0.25, 'F#4'), (0.25, 0.75, 'B4'), (1, 0.5, 'B4'), (1.5, 1.5, 'D5')]      # "Ho-jo-to-ho!" (after Wagner)
HEIA = [(0, 0.5, 'D5'), (0.5, 0.5, 'B4'), (1, 2.0, 'F#4')]                         # "Hei-a-ha!"
CBEAT = 0.26
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
PALE = hexc('#a0b0c0')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def cyc(c):
    """Start of cycle c, when its sister appears, and when she lands (the interlude)."""
    t0 = C0 + c * CYCLE
    return t0, t0 + 12 * RB, t0 + 24 * RB


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who is a sister for her cries and hooves."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    def trills(t0, beats, vel):
        for t, m, v, d in play('valkyrie_cry', t0, RB, 0, vel):
            if t < t0 + beats * RB:
                add(t, d, m, v, 'trill')

    add(0.0, C0 + 0.2, 'B2', 70, 'pedal')
    trills(0.2, 4, 84)
    for k in range(3):                                                          # string runs flying up
        for j in range(8):
            add(0.4 + k * 1.2 + j * 0.06, 0.1, note('B2') + (0, 2, 3, 5, 7, 9, 10, 12)[j] + 12 * (k % 2), 90, 'run')
    add(C0 - 1.2, 1.2, 'B1', 96, 'roll')
    for c in range(NCYC):
        t0, ta, tl = cyc(c)
        lvl = min(c, 4)                                                         # the orchestra grows
        for p, (tr, root) in enumerate(zip(TRANS, ROOTS)):
            tp = t0 + p * 6 * RB
            for t, m, v, d in play('ride', tp, RB, tr, 84 + 8 * lvl):
                add(t, d * 1.6, m, v, 'ride', lvl)
            for bar in range(2):                                                # the gallop underneath
                for b, dd in ((0, 1.0), (1.0, 0.5), (1.5, 1.0), (2.5, 0.5)):
                    add(tp + (bar * 3 + b) * RB, dd * RB * 0.9, note(root) + (12 if b else 0), 82 + 7 * lvl - 6 * (b > 0),
                        'gallop', lvl)
            if lvl >= 3:
                add(tp, 0.4, root, 100, 'timp')
        ti = tl                                                                 # the interlude: chords pouring down
        for t, m, v, d in play('valkyries_descent', ti + 0.3, DB, 0, 100 + 3 * lvl):
            add(t, d * 1.1, m, v, 'descent', lvl)
        trills(ti + 0.3, 8, 80 + 3 * lvl)
        add(ti, 0.3, 'B1', 110, 'crash')
        who, how = ARRIVALS[c]
        for j, k in enumerate(who):                                             # her cries
            for b, dd, n in HOJO:
                add(ta + 0.4 + 0.5 * j + b * CBEAT, dd * CBEAT * 1.2, note(n) + 2 * j, 108, 'cry', k)
            for b, dd, n in HEIA:
                add(tl + 0.6 + 0.6 * j + b * CBEAT, dd * CBEAT * 1.2, note(n) + 2 * j, 112, 'cry', k)
            add(tl, 0.5, 'B1', 116, 'land', k)
            for h in range(int(12 * RB / (1.5 * RB))):                          # hooves while she rides in
                add(ta + h * 1.5 * RB, 0.1, 'B1', 84 + h, 'hoof', k)
        if how != 'end':
            add(ta - 0.4, 0.8, 'B2', 100, 'burst', who[0])
    for m in ('B1', 'F#2', 'B2', 'D3'):                                         # the last chord, held over the cut
        add(cyc(NCYC - 1)[2] + 0.3, D - cyc(NCYC - 1)[2] - 0.3, m, 84, 'hold')
    for ts, where in STRIKES:
        add(ts, 2.0, 'B0', 104, 'thunder', where)
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
    """Where a sister wheels on the rock, in her place (shared with the next scenes)."""
    return at(G, *SPOTS[k]) + 9 * np.sin(2 * np.pi * (0.31 * tt + k / 8)) + 4 * np.sin(2 * np.pi * (0.73 * tt + k / 3))


def choreography(G):
    """Per frame: each sister's position (path distance; off the house before she comes), and how far in she is."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    pos = np.full((8, F), L + 400.0)
    seen = np.zeros((8, F))
    land = np.full(8, np.inf)
    for c, (who, how) in enumerate(ARRIVALS):
        t0, ta, tl = cyc(c)
        for j, k in enumerate(who):
            spot = at(G, *SPOTS[k])
            if how == 'end':                    # in from the free end, sweeping past her place and wheeling back
                marks = [(0.0, L + 60 + 70 * j), (ta, L + 60 + 70 * j), (tl - 0.1, spot - 170 - 40 * j), (tl + 0.9, spot)]
            else:                               # out of the clouds, away along the wing, then back across to the rock
                start = at(G, *how)
                turn = at(G, how[0], 0.04 if how[0] == 'Left' else 0.96)
                over = spot + (170 if how[0] == 'Left' else -170)
                marks = [(0.0, start), (ta, start), (ta + 1.2, turn), (tl - 0.1, over), (tl + 0.9, spot)]
            ts, ds = zip(*marks)
            path = follow(np.interp(t, ts, ds), np.full(F, 7.0))
            rest = sway(G, k, t + CLOCK)
            blend = smoothstep(tl + 0.3, tl + 2.2, t)
            pos[k] = np.where(t < ta - 0.6, L + 400.0, path * (1 - blend) + rest * blend)
            if how == 'end':
                seen[k] = smoothstep(ta - 0.2, ta + 0.3, t)
            else:
                seen[k] = smoothstep(ta - 0.15, ta + 0.1, t)
            land[k] = tl
    return dict(t=t, pos=pos, seen=seen, land=land)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def render(G, seed=20):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    wing = 1 - porch
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}
    ride = np.array([e[0] for e in N if e[4] == 'ride'])
    longs = np.array([e[0] for e in N if e[4] == 'ride' and e[1] >= 0.5 * RB * 1.5])
    desc = [e[0] for e in N if e[4] == 'descent' and e[2] >= note('B4')]
    trill = np.array([e[0] for e in N if e[4] == 'trill' and e[2] >= note('B4')])
    cries = [np.array([e[0] for e in N if e[4] == 'cry' and e[5] == k]) for k in range(8)]
    bursts = [(e[0] + 0.4, e[5]) for e in N if e[4] == 'burst']
    tw = Flicker(rng, G.N, 3.0, 9.0)
    sp = rng.random(G.N)

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

        # the Ride: every long note a gust of light through the clouds, rolling the way the riders go
        g = last(longs, t, 0.35)
        gust = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.9 * tt))
        fr += light(STORM, 0.55 * g * gust ** 2 * wing)
        on = smoothstep(C0 - 0.5, C0 + 2, t)
        fr += light(FLASH, 0.12 * on * last(ride, t, 0.12) * gust ** 4 * wing)

        # the trilling cries: glitter flickering over the clouds
        tr = last(trill, t, 0.12, 0.5)
        if tr > 0:
            fr += light(FLASH, 0.6 * tr * (sp > 0.86) * (0.5 + 0.5 * tw(t)) * wing)

        # the descending chords: bands of light pouring down the house from the free end of Right to Side
        for i, td in enumerate(desc):
            if td <= t < td + 0.9:
                age = t - td
                j = desc.index(td) % 9
                q = L - (j + 0.5) * L / 9
                fr += light(FLASH * 0.6 + STORM * 0.4, 0.95 * np.exp(-age / 0.35) * blob(q, 200))

        # bursts out of the clouds: the cloud bulges bright, tears open, and she is through
        for tb, k in bursts:
            age = t - tb
            p0 = C['pos'][k][min(int((tb + 0.3) / DT), F - 1)]
            if -0.5 <= age < 0:
                fr += light(STORM * 0.6 + FLASH * 0.4, 0.8 * (1 + age / 0.5) * blob(p0, 60))
            elif 0 <= age < 1.0:
                r = 20 + 300 * age ** 0.6
                fr += light(COLS[k], 0.9 * (1 - age) * np.exp(-((np.abs(d - p0) - r) / 30) ** 2))
                fr += light(WHITE, 0.9 * np.exp(-age / 0.1) * blob(p0, 30))

        # the sisters, each in her colour with a fallen hero over her saddle; a comet behind her while she rides
        for k in range(8):
            s = C['seen'][k][f]
            if s <= 0:
                continue
            p = C['pos'][k][f]
            vis = s * smoothstep(L + 40, L - 20, p)
            landed = t >= C['land'][k] + 1.0
            fl = last(cries[k], t, 0.18, 1.0)
            pulse = last(ride, t, 0.2, 0.6) * landed
            gal = 0.88 + 0.12 * np.cos(2 * np.pi * t / (1.5 * RB))
            b = vis * (0.85 + 0.35 * fl + 0.15 * pulse) * (gal if not landed else 1.0)
            fr += light(COLS[k], b * blob(p, 16 + 5 * fl) + 0.35 * b * blob(p, 75 + 30 * fl))
            fr += light(WHITE, 0.55 * vis * fl * blob(p, 8))
            back = C['pos'][k][max(f - 4, 0)]
            dirn = np.sign(back - p) if abs(back - p) > 1 else 1.0
            if abs(p - back) > 8:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 30, 2)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, blob(q, 22) * (1 - j / 14.5))
                fr += light(COLS[k], 0.8 * vis * trail + 0.3 * vis * blob(p, 220))      # lighting up the clouds
                fr += light(PALE, 0.45 * vis * blob(p + 22 * dirn, 6))           # the hero, slung behind her
            else:
                fr += light(PALE, 0.3 * vis * blob(at(G, *SPOTS[k]) + 15, 6))   # laid on the rock beside her
            for tc in cries[k]:                                                 # every cry a ring flying out from her
                if tc <= t < tc + 0.9:
                    age = t - tc
                    r = 15 + 340 * age ** 0.7
                    fr += light(COLS[k], 0.75 * (1 - age / 0.9) * np.exp(-((np.abs(d - p) - r) / 26) ** 2))
            tl = C['land'][k]
            if tl <= t < tl + 1.2:                                              # landing on the rock
                age = t - tl
                fr += light(COLS[k], 0.8 * np.exp(-age / 0.35) * porch * blob(p, 260))
                fr += light(COLS[k], 0.55 * np.exp(-age / 0.5) * wing * (0.6 + 0.4 * gust))
                fr += light(WHITE, 0.6 * np.exp(-age / 0.12) * blob(p, 25))

        # lightning in the clouds
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if 0 <= age < 1.0:
                a, b = seg_d[where]
                mid = 0.5 * (a + b)
                fr += light(WHITE, 0.95 * bolt(age, b if i % 2 else a, mid, i))
                fr += light(FLASH, 0.4 * np.exp(-age / 0.2) * blob(mid, 0.7 * (b - a)))
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

    def pan_of(k, t):
        return pan_at(min(np.interp(t, C['t'], C['pos'][k]), G.length))

    for name, gain, rev in (('brass', 0.14, 0.28), ('low', 0.14, 0.18), ('strings', 0.12, 0.3), ('winds', 0.1, 0.3),
                            ('cries', 0.14, 0.35), ('perc', 0.15, 0.25), ('fx', 0.07, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    snare = M.hits('Percussion/Snare2-taps_v[2-4]*.wav')

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
    rock = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, who in compose():
        if part == 'pedal':
            hold('low', trem, m, t, t + d, v, rock, rise=0.05, fall=0.6, gain=0.7)
        elif part == 'trill':
            hi = m >= note('B4')
            M.add('winds', (pic if hi else cl).play(m if hi else m + 12, v), t, 0.7 if hi else 0.5, -0.4 if hi else 0.4)
            if hi:
                M.add('strings', vns.play(m - 12, v - 10), t, 0.4, 0.3)
        elif part == 'run':
            M.add('strings', vns.play(m + 12, v), t, 0.6, -0.6 + 1.2 * ((t * 5) % 1))
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d + 0.3), t, 0.7, rock)
        elif part == 'ride':
            lvl = who
            sp = -0.35 + 0.7 * ((t / 3.6) % 1)                                  # the horns sweep across the stage
            M.add('brass', horn.play(m, v, dur=d, release=0.15), t, 0.85, sp)
            M.add('brass', horn.play(m, v - 8, dur=d, release=0.15), t, 0.5, -sp)
            if lvl >= 1:
                M.add('brass', tpt.play(m + 12, v - 18, dur=d, release=0.15), t, 0.35, sp * 0.6)
            if lvl >= 2:
                M.add('brass', tbn.play(m - 12, v - 6, dur=d, release=0.15), t, 0.6, 0.0)
            if lvl >= 4:
                M.add('low', tuba.play(m - 24, v - 10, dur=d, release=0.15), t, 0.5, 0.0)
        elif part == 'gallop':
            M.add('low', cbs.play(m + 12, v), t, 0.7, -0.25)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.6, 0.25)
            if who >= 2:
                M.add('low', bsn.play(m + 12, v - 12), t, 0.4, 0.0)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-4), t, 0.6, rock)
        elif part == 'descent':
            if m >= note('B4'):
                M.add('strings', vn.play(m - 12, v, dur=d, release=0.2), t, 0.5, 0.2)
                M.add('brass', tpt.play(m - 12, v - 20, dur=d, release=0.2), t, 0.35, -0.2)
            elif m >= note('A3'):
                M.add('brass', horn.play(m, v - 6, dur=d, release=0.2), t, 0.6, 0.0)
            else:
                M.add('brass', tbn.play(m, v - 6, dur=d, release=0.3), t, 0.7, 0.0)
                M.add('low', tuba.play(m - 12, v - 12, dur=d, release=0.3), t, 0.5, 0.0)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.7, rock)
            M.add('perc', timp.play(v, pitch=-4), t, 0.7, rock)
        elif part == 'cry':
            pa = pan_of(who, t)
            M.add('cries', tpt.play(m, v, dur=d, release=0.2), t, 0.9, pa)
            M.add('cries', horn.play(m, v - 14, dur=d, release=0.2), t, 0.5, pa)
        elif part == 'land':
            pa = pan_of(who, t)
            M.add('perc', bd.play(v), t, 0.8, pa)
            M.add('perc', timp.play(v, pitch=-6), t, 0.7, pa)
            M.add('fx', whoosh(0.7, 3500, 500, 0.6, seed=int(t * 10)), t - 0.6, 0.8, pa)
        elif part == 'hoof':
            M.add('perc', snare.play(v), t, 0.55, pan_of(who, t))
        elif part == 'burst':
            pa = pan_of(who, t + 0.5)
            M.add('fx', whoosh(0.8, 300, 4000, 0.7, seed=int(t * 10)), t, 1.0, pa)
            M.add('perc', crash.play(90), t + 0.4, 0.5, pa)
        elif part == 'hold':
            s = tuba if m < note('F#2') else (tbn if m < note('B2') else horn)
            hold('brass', s, m + (12 if s is tuba else 0), t, t + d, v, 0.0, rise=0.1, fall=1.0, gain=0.5)
            hold('strings', vtrem, m + 24, t, t + d, v - 10, 0.0, rise=0.1, fall=1.0, gain=0.3)
        elif part == 'thunder':
            pt = pan_at(seg_mid[who])
            M.add('perc', bd.play(v), t, 0.6, pt)
            M.add('perc', roll.play(v - 40, dur=d), t + 0.1, 0.4, pt)
            M.add('fx', whoosh(1.0, 2500, 200, 0.5, seed=int(t * 10) + 3), t, 0.5, pt)
