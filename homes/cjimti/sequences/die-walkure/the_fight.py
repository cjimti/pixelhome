"""The Fight: storm clouds roll in over the pass, dark grey with grey-blue banks driving along the roofline,
and lightning flickers on the heights of the porch while the storm (Donington 74) churns in the low strings and
the timpani rumble. Sieglinde sleeps on Left. From the free end of Right come Hunding's horn calls (composed, on
horns) with a red flash each time, his heavy dotted motif in the tubas, and Hunding himself, blood red in a
pool of black, climbing along Right and up onto the porch. Siegmund answers with the sword's motif (Donington
43) on horn and trumpet and strides up from Left onto Porch Front, Nothung's white steel at his side.

They fight on the porch in thunder and lightning. Driving D minor in the low strings; at every clash the two
lights lunge together and a blue-white spark bursts where they meet, with timpani, cymbal and brass, and the sky
cracks over the porch again and again. Brünnhilde streaks back in from the end of Right to the Ride (Donington
47) and spreads her silver over Siegmund's blue, shielding him, and he drives Hunding back. Then a red glow
swells in the storm over the middle of the porch: Wotan, towering, his blue rising out of the red, and his spear
motif (Donington 73) strides down in trombones and tubas as the steel line of the spear stretches across the
whole porch between them. Brünnhilde recoils to Porch Right. The violins tremble, the timpani roll, Siegmund
strikes, and Nothung shatters on the spear: one white burst over the whole house, a crash and a gong, and white
shards fly out across the roofline to a cascade of glockenspiel and harp, falling back to lie glinting on the
porch. The last frame is the instant after: Siegmund disarmed, Hunding with his spear raised, Wotan between them
with his spear held out in his red glow, Brünnhilde shrinking back, Sieglinde dim on Left, the storm flickering.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody

CODE = 'WK18'
TITLE = 'The Fight'
KIND = 'show'
DESCRIPTION = ('In a storm on the mountain pass, Hunding\'s horns call and Siegmund answers, and they fight on '
               'the heights. Brünnhilde shields Siegmund, until Wotan himself appears in the storm and holds out '
               'his spear, and Siegmund\'s sword shatters against it.')
VOICEOVER = ('Thunder, horns, and two men with swords on a mountain top. '
             'One of them has a goddess on his side. The other has her father.')

T_ROLL = 0.0                                # the storm rolls in
HORNS = [5.0, 8.4]                          # Hunding's horn calls
T_HUND = [10.2, 13.6]                       # his motif in the tubas
T_ANSWER = 12.0                             # Siegmund answers: the sword's motif
T_MEET = 19.0                               # on the porch
CLASHES = [20.0, 21.6, 23.0, 25.2, 26.4, 28.6, 30.8, 32.0, 34.2, 36.6, 38.0, 40.2, 42.4, 43.6, 45.8]
T_BRUNN = 46.5                              # she streaks in to shield him
CLASH2 = [50.4, 52.0, 53.6, 55.4]           # under her shield he drives Hunding back
T_RED = 57.0                                # the red glow in the storm
T_WOTAN = 60.0                              # Wotan rises out of it
T_SPEAR = 61.5                              # his spear motif
T_RECOIL = 64.0                             # Brünnhilde recoils
T_TENSE = 68.0
T_SHATTER = 75.0                            # Nothung shatters on the spear
D = 80.0
K = 17
GLINTS = (-24, -9, 10, 23)
LIGHTNING = [2.6, 6.9, 11.3, 16.0, 21.6, 25.2, 28.6, 32.0, 36.6, 40.2, 43.6, 49.0, 53.6, 57.0, 60.0, 66.5,
             71.2, 75.0, 77.2]

HUNDING = [(0, .75, 'D2'), (.75, .25, 'D2'), (1, 1, 'F2'), (2, .75, 'E2'), (2.75, .25, 'E2'), (3, 1, 'Db2'),
           (4, 2, 'D2')]                     # composed: Hunding, a heavy dotted tuba figure
HORN_CALL = [(0, .5, 'A3'), (.5, .25, 'A3'), (.75, 1.0, 'D4'), (1.75, .25, 'C4'), (2, 1.5, 'A3')]

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
STORM = hexc('#5a6a8a')
STORMDARK = hexc('#2a2e38')
BOLT = hexc('#c8d8ff')
WHITE = hexc('#ffffff')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
REDGLOW = hexc('#ff2000')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
HUNDC = hexc('#8a0020')
HSPEAR = hexc('#a07070')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def pass_bed(G):
    """The rocky pass at dawn: slate ridges on the wings and Side, warm light on the porch heights.
    Returns f(T, wings, porch) -> (N,3), T on the shared clock."""
    d, z = G.pd, G.pos[:, 2]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.35 * np.sin(d / 430)))
    crag = 0.5 + 0.5 * np.cos(2 * np.pi * d / 61 + 2.0 * np.sin(d / 97))
    height = 0.55 + 0.45 * smoothstep(-160, -560, z)

    def f(T, wings=1.0, porch_lvl=1.0):
        cloud = 0.85 + 0.15 * np.cos(2 * np.pi * (d / 900 - T / 40))
        sl = (0.62 + 0.22 * ridge + 0.1 * crag) * cloud * ~porch * wings
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - T / 25))
        dw = (0.44 + 0.08 * glow) * height * porch * porch_lvl
        return light(SLATE, sl) + light(DAWN, dw) + light(DAWNHI, 0.2 * glow * height * porch * porch_lvl)
    return f


def storm_bed(G):
    """Storm clouds over the pass: dark grey with grey-blue cloud banks rolling along. f(T, level) -> (N,3)."""
    d = G.pd

    def f(T, lvl=1.0):
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - T / 9))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 + T / 13) + 1.3)
        return light(STORMDARK, lvl * 0.45) + light(STORM, lvl * (0.1 + 0.42 * c1 ** 2 * (0.5 + 0.5 * c2)))
    return f


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    # the storm: its motif round and round in the low strings, thunder with the lightning
    for r in range(5):
        for t, m, v, d in play('storm', 0.4 + r * 3.6, 0.3, 0, 84 + 6 * r):
            if t < T_MEET:
                add(t, d, m, v, 'storm')
    for k, tl in enumerate(LIGHTNING):
        add(tl, 1.5, 'D1', 96 + (k % 3) * 8, 'thunder', k)
    add(0.0, T_MEET, 'D1', 76, 'pedal')
    # Hunding's horns and motif from the end of Right; Siegmund answers with the sword
    for k, th in enumerate(HORNS):
        for b, d, m in HORN_CALL:
            add(th + b * 0.32, d * 0.32, m, 92 + 10 * k, 'call', k)
    for j, t0 in enumerate(T_HUND):
        for b, d, m in HUNDING:
            add(t0 + b * 0.5, d * 0.5, m, 108 + 6 * j, 'hunding', j)
    for t, m, v, d in play('nothung', T_ANSWER, 0.45, -12, 110):
        add(t, d, m, v, 'answer')
    # the fight: driving eighths, a stab at every clash, the two motifs trading blows
    step = 0.21
    for i, t in enumerate(np.arange(T_MEET, T_RED + 1.0, step)):
        m = ('D2', 'D2', 'F2', 'D2', 'A1', 'D2', 'Bb1', 'A1')[i % 8]
        add(t, step * 0.8, m, 96 + 10 * (i % 4 == 0), 'drive', i)
    for k, tc in enumerate(CLASHES + CLASH2):
        add(tc, 0.5, 'D3', 116, 'clash', k)
    for j, t0 in enumerate((22.0, 30.0, 38.0)):
        for b, d, m in HUNDING:
            add(t0 + b * 0.42, d * 0.42, m, 112, 'hunding', 2 + j)
    for j, t0 in enumerate((26.0, 34.0, 42.0)):
        for t, m, v, d in play('nothung', t0, 0.36, -12, 106):
            if t < t0 + 3.0:
                add(t, d, m, v, 'answer')
    # Brünnhilde: the Ride as she streaks in; "Hau' ihn!"
    for j, t0 in enumerate((T_BRUNN, T_BRUNN + 2.6)):
        for t, m, v, d in play('ride', t0, 0.36, 3 * j, 112):
            add(t, d * 1.2, m, v, 'ride', j)
    # the red glow, Wotan; his spear
    add(T_RED, T_SPEAR - T_RED, 'Db2', 90, 'trem')
    add(T_RED + 1.0, T_SPEAR - T_RED - 1.0, 'Ab2', 84, 'trem')
    add(T_WOTAN, 0.8, 'D1', 120, 'gong')
    for t, m, v, d in play('spear', T_SPEAR, 0.6, 0, 122):
        add(t, d * 1.1, m, v, 'spear')
    for m in ('Bb1', 'Bb2', 'D3', 'F3'):
        add(T_SPEAR, 1.2, m, 110, 'chord')
    # the tension: the violins tremble, the timpani roll, then the sword shatters on the spear
    add(T_TENSE, T_SHATTER - T_TENSE, 'E4', 104, 'vtrem')
    add(T_TENSE + 1.5, T_SHATTER - T_TENSE - 1.5, 'Bb4', 100, 'vtrem')
    add(T_TENSE, T_SHATTER - T_TENSE, 'E2', 104, 'trem')
    add(T_TENSE - 1.0, T_SHATTER - T_TENSE + 1.0, 'E1', 96, 'pedal')
    add(T_RED, T_SPEAR - T_RED, 'Db1', 90, 'pedal')
    add(T_SHATTER - 5.0, 2.5, 'D2', 100, 'roll')
    add(T_SHATTER - 2.5, 2.5, 'D2', 120, 'roll')
    for m in ('E1', 'E2', 'Bb2', 'E3', 'G3', 'Db4', 'E4'):
        add(T_SHATTER, 1.6, m, 127, 'shatter')
    rng = np.random.default_rng(18)
    for i in range(22):
        add(T_SHATTER + 0.05 + 0.11 * i + rng.uniform(0, 0.04), 0.4, note('E6') - int(1.3 * i) - rng.integers(0, 3),
            110 - 3 * i, 'shard', i)
    add(T_SHATTER + 0.3, D - T_SHATTER - 0.3, 'E1', 90, 'pedal')
    add(T_SHATTER + 0.6, D - T_SHATTER - 0.6, 'Bb1', 70, 'trem')
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


def choreography(G):
    """Per frame: Siegmund, Hunding, Brünnhilde (path distance); Wotan stands at the middle of Porch Front."""
    F = nframes(D)
    t = np.arange(F) * DT
    P = lambda s, u: at(G, s, u)
    rend = P('Right', 1.0) + 40

    def track(keys):
        return np.interp(t, [k[0] for k in keys], [k[1] for k in keys])

    sm_t = track([(0, P('Left', 0.55)), (T_ANSWER - 0.5, P('Left', 0.55)), (T_ANSWER + 2.0, P('Porch Left', 0.2)),
                  (T_MEET - 0.5, P('Porch Front', 0.3)), (T_BRUNN, P('Porch Front', 0.34)),
                  (CLASH2[-1] + 0.8, P('Porch Front', 0.46)), (T_RED + 1, P('Porch Front', 0.38)),
                  (T_SHATTER - 0.6, P('Porch Front', 0.38)), (T_SHATTER - 0.05, P('Porch Front', 0.46)),
                  (T_SHATTER + 1.2, P('Porch Front', 0.35)), (D, P('Porch Front', 0.35))])
    hd_t = track([(0, rend), (HORNS[1] + 1.0, rend), (HORNS[1] + 3.5, P('Right', 0.6)),
                  (T_HUND[1] + 2.0, P('Porch Right', 0.6)), (T_MEET - 0.5, P('Porch Front', 0.7)),
                  (T_BRUNN, P('Porch Front', 0.66)), (CLASH2[-1] + 0.8, P('Porch Front', 0.8)),
                  (T_RED + 1, P('Porch Front', 0.68)), (T_SHATTER, P('Porch Front', 0.64)), (D, P('Porch Front', 0.62))])
    sm = follow(sm_t, np.full(F, 4.0))
    hd = follow(hd_t, np.full(F, 4.0))
    mid = 0.5 * (sm + hd)
    for k, tc in enumerate(CLASHES + CLASH2):  # each clash: both lunge to the middle and spring back
        a = np.exp(-((t - tc) / 0.12) ** 2)
        sm = sm + (mid - 6 - sm) * a
        hd = hd + (mid + 6 - hd) * a
    br_t = track([(0, rend + 200), (T_BRUNN, rend + 60), (T_BRUNN + 2.2, P('Porch Right', 0.5)),
                  (T_BRUNN + 3.4, P('Porch Front', 0.42)), (T_RECOIL, P('Porch Front', 0.45)),
                  (T_RECOIL + 1.6, P('Porch Right', 0.3)), (D, P('Porch Right', 0.3))])
    br = follow(br_t, np.full(F, 3.0))
    br = np.where(t < T_RECOIL + 0.5, np.where(t > T_BRUNN + 3.4, sm + 3, br), br)
    br = follow(br, np.full(F, 6.0))
    return dict(t=t, mund=sm, hund=hd, brunn=br, wotan=np.full(F, P('Porch Front', 0.5)),
                linde=np.full(F, P('Left', 0.7)))


def shard_rest(G):
    """Where the pieces of Nothung come to rest on the porch (path distances), fixed so the next scene can find them."""
    rng = np.random.default_rng(1800)
    pf0, pf1 = at(G, 'Porch Left', 0.55), at(G, 'Porch Right', 0.45)
    return np.sort(rng.uniform(pf0, pf1, 18))


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    z = G.pos[:, 2]
    heights = smoothstep(-200, -560, z) * porch
    bed = pass_bed(G)
    storm = storm_bed(G)
    C = choreography(G)
    N = compose()
    wp = C['wotan'][0]
    ln = C['linde'][0]
    rend = at(G, 'Right', 1.0)
    pf0, pf1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)

    def ons(*parts):
        return sorted({e[0] for e in N if e[4] in parts})

    def last(on, t):
        i = int(np.searchsorted(on, t, side='right')) - 1
        return t - on[i] if i >= 0 else 99.0

    hund_on = ons('hunding')
    answer_on = ons('answer')
    spear_ev = [e for e in N if e[4] == 'spear']
    ride_on = ons('ride')
    tw = Flicker(rng, G.N, 2.0, 8.0)
    bolt_at = [rng.uniform(at(G, 'Porch Left', 0.3), at(G, 'Porch Right', 0.7)) for _ in LIGHTNING]
    bolt_w = rng.uniform(120, 300, len(LIGHTNING))
    rest = shard_rest(G)
    fly = np.concatenate([rest, rng.uniform(0, L, 42)])
    fly_v = rng.uniform(0.5, 1.0, len(fly))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        s = 0.4 + 0.6 * smoothstep(T_ROLL, 6.0, t)
        fr = bed(T, 1 - s, 1 - s) + storm(T, s)
        sm, hd, b = C['mund'][f], C['hund'][f], C['brunn'][f]

        # lightning over the heights: a double flicker, a bolt along the porch, a glow on the wings
        for k, tl in enumerate(LIGHTNING):
            if tl <= t < tl + 0.6:
                a = np.exp(-(t - tl) / 0.07) + 0.7 * np.exp(-max(t - tl - 0.18, 0) / 0.08) * (t > tl + 0.18)
                if tl == T_SHATTER:
                    continue
                fr += light(BOLT, a * (0.85 * heights * np.exp(-((d - bolt_at[k]) / bolt_w[k]) ** 2) + 0.25 * (1 - porch)))
                fr += light(WHITE, 0.6 * a * np.exp(-((d - bolt_at[k]) / 25) ** 2) * porch)

        # Hunding's horns: red at the free end of Right
        for k, th in enumerate(HORNS):
            if th <= t < th + 2.5:
                a = np.exp(-(t - th) / 0.6)
                fr += light(HUNDC, a * np.exp(-((d - rend) / (110 + 80 * k)) ** 2))

        # the clashes: a blue-white spark where they meet, flung out along the porch
        for tc in CLASHES + CLASH2:
            if tc <= t < tc + 0.8:
                age = t - tc
                c = np.interp(tc, C['t'], 0.5 * (C['mund'] + C['hund']))
                fr += light(WHITE, 0.9 * np.exp(-age / 0.1) * np.exp(-((d - c) / 12) ** 2))
                r = 30 + 400 * age
                fr += light(SIEGMUND, 0.6 * np.exp(-age / 0.25) * np.exp(-((np.abs(d - c) - r) / 25) ** 2))

        # the red glow in the storm, and Wotan rising out of it
        red = smoothstep(T_RED, T_WOTAN + 1, t)
        if red > 0:
            pulse = 0.85 + 0.15 * np.sin(2 * np.pi * T / 2.3)
            fr += light(REDGLOW, red * pulse * (0.7 * np.exp(-((d - wp) / 110) ** 2) + 0.25 * heights))
        wot = smoothstep(T_WOTAN, T_WOTAN + 2.5, t)
        if wot > 0:
            n = [e for e in spear_ev if e[0] <= t]
            hit = np.exp(-(t - n[-1][0]) / 0.3) if n else 0.0
            fr = fr * (1 - 0.5 * wot * np.exp(-((d - wp) / 40) ** 2))[:, None]
            fr += light(WOTAN, wot * (1.1 + 0.15 * hit) * np.exp(-((d - wp) / 26) ** 2))
            fr += light(WOTAN, wot * 0.35 * np.exp(-((d - wp) / 90) ** 2))
            # the spear: its steel line stretching out across the porch, a step for every note
            reach = min(len(n) / len(spear_ev), 1.0) if n else 0.0
            half = 160 * smoothstep(0, 1, reach)
            span = smoothstep(wp - half - 6, wp - half + 6, d) * smoothstep(wp + half + 6, wp + half - 6, d)
            fr += light(SPEAR, (0.3 + 0.2 * hit) * span * (d >= pf0) * (d <= pf1))

        # Hunding: blood red in a pool of black; his spear raised after the sword breaks
        on = smoothstep(HORNS[1] + 0.8, HORNS[1] + 1.6, t)
        hp = np.exp(-last(hund_on, t) / 0.3) if t < T_RED else 0.0
        fr = fr * (1 - 0.75 * on * np.exp(-((d - hd) / 38) ** 2))[:, None]
        fr += light(HUNDC, on * (1.0 + 0.25 * hp) * np.exp(-((d - hd) / 15) ** 2))
        raised = smoothstep(T_SHATTER + 0.3, T_SHATTER + 1.5, t)
        hs = smoothstep(hd + 12, hd + 16, d) * smoothstep(hd + 40, hd + 34, d)
        fr += light(HSPEAR, on * (0.35 + 0.35 * raised) * hs)

        # Brünnhilde: in from the end of Right, her silver spread over him; recoiling from her father
        if t >= T_BRUNN:
            vis = smoothstep(T_BRUNN, T_BRUNN + 0.4, t)
            shield = smoothstep(T_BRUNN + 3.0, T_BRUNN + 4.0, t) * (1 - smoothstep(T_RECOIL, T_RECOIL + 1.0, t))
            rp = np.exp(-last(ride_on, t) / 0.25) if t < T_RED else 0.0
            recoil = smoothstep(T_RECOIL, T_RECOIL + 1.6, t)
            bl = vis * (0.85 + 0.2 * rp - 0.25 * recoil) * (1 - 0.45 * shield)
            fr += light(BRUNN, bl * np.exp(-((d - b) / 16) ** 2) + 0.22 * bl * np.exp(-((d - b) / 60) ** 2))
            fr += light(BRUNN, 0.6 * shield * np.exp(-((np.abs(d - sm) - 24) / 12) ** 2))
            for j, o in enumerate(GLINTS):
                g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
                fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
            fr += light(BGOLD, 0.55 * vis * np.exp(-((d - b - 16) / 7) ** 2))
            if t < T_BRUNN + 3.5:
                for j, lag in enumerate(range(2, 30, 2)):
                    q = C['brunn'][max(f - lag, 0)]
                    fr += light(BRUNN, 0.6 * vis * (1 - j / 14) * np.exp(-((d - q) / 26) ** 2))

        # Siegmund and Nothung; the sword gone after it breaks
        ap = np.exp(-last(answer_on, t) / 0.3)
        smv = 0.8 + 0.15 * ap
        fr += light(SIEGMUND, smv * np.exp(-((d - sm) / 16) ** 2) + 0.25 * smv * np.exp(-((d - sm) / 60) ** 2))
        whole = 1 - smoothstep(T_SHATTER - 0.02, T_SHATTER, t)
        side = 1 if t < T_MEET else -1                      # on the porch he holds it out toward Hunding
        if side > 0:
            blade = smoothstep(sm - 32, sm - 29, d) * smoothstep(sm - 15, sm - 18, d)
            hilt = np.exp(-((d - sm + 12) / 3.5) ** 2)
        else:
            blade = smoothstep(sm + 15, sm + 18, d) * smoothstep(sm + 34, sm + 31, d)
            hilt = np.exp(-((d - sm - 12) / 3.5) ** 2)
        tense = smoothstep(T_TENSE, T_SHATTER, t)
        fr += light(STEEL, smv * (0.7 + 0.3 * tense) * whole * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, smv * 0.7 * hilt)

        # the shattering: one white burst over the whole house, shards flying out and falling back to the porch
        if t >= T_SHATTER:
            age = t - T_SHATTER
            fr += light(WHITE, 1.0 * np.exp(-age / 0.12))
            fr += light(WHITE, 0.8 * np.exp(-age / 0.6) * np.exp(-((d - wp) / (60 + 500 * age)) ** 2))
            c0 = 0.5 * (sm + wp)
            q = c0 + (fly - c0) * np.minimum(age / 0.8, 1.0) ** 0.6
            kept = np.arange(len(fly)) < len(rest)          # the pieces that land on the porch stay
            fade = np.where(kept, 1.0, 1 - smoothstep(1.0, 3.5, age))
            g = ((fade * (0.6 + 0.4 * np.exp(-age / 0.8)) * fly_v)[None, :] *
                 np.exp(-((d[:, None] - q[None, :]) / 6) ** 2)).max(axis=1)
            fr += light(STEEL, g * (0.75 + 0.25 * tw(t)))

        # Sieglinde, asleep on Left
        fr += light(SIEGLINDE, 0.299 * np.exp(-((d - ln) / 15) ** 2) + 0.25 * 0.299 * np.exp(-((d - ln) / 55) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    for name, gain, rev in (('low', 0.17, 0.2), ('brass', 0.16, 0.3), ('horns', 0.15, 0.4),
                            ('strings', 0.15, 0.3), ('perc', 0.19, 0.3), ('shards', 0.14, 0.5)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tstac = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    def p(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    rend = pan_at(at(G, 'Right', 1.0))
    pw = pan_at(C['wotan'][0])
    for t, d, m, v, part, k in compose():
        if part == 'storm':
            M.add('low', cbs.play(m + 12, v), t, 0.8, -0.3)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.7, 0.3)
        elif part == 'thunder':
            if abs(t - T_SHATTER) > 0.01:
                M.add('perc', roll.play(v - 10, dur=d), t + 0.1, 0.5, 0.3 * np.sin(k))
                M.add('perc', timp.play(v, pitch=-7), t + 0.05, 0.6, 0.3 * np.sin(k))
                if k % 3 == 1:
                    M.add('perc', crash.play(96), t, 0.4, 0.3 * np.sin(k))
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5)
        elif part == 'call':
            M.add('horns', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, rend)
        elif part == 'hunding':
            ph = p('hund', t)
            M.add('brass', tuba.play(m + 12, v, dur=d * 1.05, release=0.2), t, 1.0, ph)
            M.add('brass', tbn.play(m + 12, v - 14, dur=d * 1.05, release=0.2), t, 0.5, ph)
            if d >= 0.4:
                M.add('perc', timp.play(v - 10, pitch=-2), t, 0.6, ph)
        elif part == 'answer':
            ps = p('mund', t)
            M.add('horns', tpt.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, ps)
            M.add('horns', horn.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.6, ps)
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.9, -0.2)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, 0.2)
        elif part == 'clash':
            c = pan_at(np.interp(t, C['t'], 0.5 * (C['mund'] + C['hund'])))
            M.add('perc', timp.play(v, pitch=-1), t, 0.9, c)
            M.add('perc', crash.play(104 + 8 * (k % 2)), t, 0.5, c)
            M.add('brass', tstac.play(note('D3') + (0, 3, 5)[k % 3], 112), t, 0.7, c)
            M.add('perc', whoosh(0.3, 4000, 1500, 0.3, seed=30 + k), t - 0.2, 0.4, c)
        elif part == 'ride':
            M.add('horns', horn.play(m, v, dur=d, release=0.3), t, 1.0, p('brunn', t))
            M.add('brass', tbn.play(m - 12, v - 12, dur=d, release=0.3), t, 0.5, p('brunn', t))
        elif part == 'trem':
            hold('low', trem, m, t, t + d, v, pw, rise=2.0, fall=1.0, gain=0.8)
        elif part == 'gong':
            M.add('perc', gong.play(v), t, 0.9, pw)
            M.add('perc', timp.play(v, pitch=-8), t, 0.9, pw)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, pw)
            M.add('brass', tuba.play(m - 12, v - 6, dur=d, release=0.3), t, 0.8, pw)
        elif part == 'chord':
            s = tuba if m < note('C2') else (tbn if m < note('C3') else horn)
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d, release=0.6), t, 0.7, pw)
        elif part == 'vtrem':
            hold('strings', vtrem, m, t, t + d, v, 0.0, rise=3.0, fall=0.1, gain=0.9)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.9, pw)
        elif part == 'shatter':
            s = tuba if m < note('E2') else (tbn if m < note('E3') else horn)
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d, release=1.0), t, 0.9, pw)
            if m == note('E1'):
                M.add('perc', crash.play(127), t, 1.0, -0.3)
                M.add('perc', crash.play(127), t + 0.02, 1.0, 0.3)
                M.add('perc', gong.play(127), t, 1.0, pw)
                M.add('perc', timp.play(127, pitch=-5), t, 1.0, pw)
                M.add('perc', whoosh(1.2, 6000, 800, 0.5, seed=99), t, 0.8, 0.0)
        elif part == 'shard':
            pp = -0.8 + 1.6 * ((k * 7) % 22) / 21
            M.add('shards', glock.play(m, v), t, 0.9, pp)
            M.add('shards', harp.play(m - 12, v - 10), t, 0.5, -pp)
