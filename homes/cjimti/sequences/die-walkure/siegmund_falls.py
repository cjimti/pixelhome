"""Siegmund Falls: the instant after Nothung shatters on Wotan's spear. Siegmund (Wälsung blue) stands
disarmed at the left of the porch, the white shards of his sword glinting round his feet; Hunding (blood red in
black) has his spear up; Wotan towers between them in deep blue with a red storm glow, his spear a steel line
across the porch; Brünnhilde (silver, gold glints) recoils on Porch Right and Sieglinde lies where she fell on
the Left wing.

Hunding lunges and drives his spear into Siegmund: a red streak, a white-red flash, a gong and a crash. Then a
terrible quiet: the storm drops, the lightning stops, and over a hushed cello pedal the Wagner tubas (horns and
tubas, pianissimo) play the tragic destiny of the Volsungs (Donington 66) while Siegmund's blue gutters,
flickers and goes out. Brünnhilde darts across the porch gathering the shards (each a harp note as it leaves
the ground and joins the glints circling her), runs to Sieglinde, lifts her onto her horse, and gallops away
along the Left wing and out along Side to the Ride (47) on the horns, the shards and the amber of Sieglinde
riding with her silver.

Wotan is left alone over the body: the fate motif again, slow, on trombones, a pale glow where Siegmund lay.
"Geh hin, Knecht!": a trombone declamation, a sweep of his hand (a blue wave rolling out over the porch, a
whoosh of strings), and Hunding's red flares and collapses to an ember as his own heavy tuba figure dies under
him. Silence; then Wotan's fury breaks: "Doch Brünnhilde! Weh der Verbrecherin!" His red glow blazes, the
storm (74) roars up in the low strings, his spear (73) slams down twice in trombones and tubas, a steel line
striking across the porch with each note walking down it, and lightning cracks over the house. He mounts and
rides after her, a blue-black storm with his spear streaking out the way she went, a third spear call
thundering after him. What is left is the storm alone, rolling and flickering, settling into the slate clouds
of the Valkyries' rock.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK19'
TITLE = 'Siegmund Falls'
KIND = 'show'
DESCRIPTION = ('Hunding drives his spear into the disarmed Siegmund, and the hero\'s blue light goes out. '
               'Brünnhilde gathers up the pieces of the sword and gallops away with Sieglinde, and Wotan, '
               'after striking Hunding dead with a wave of his hand, rides after her in a fury.')
VOICEOVER = ('The sword is broken, and the god who gave it has let his son die. '
             'Now watch the god turn his anger on the one who tried to save him.')

T_THRUST = 1.0                              # Hunding lunges
T_STAB = 1.6                                # the spear goes in
T_OUT = 8.6                                 # Siegmund's light is gone
T_FATE = 2.4                                # the Volsungs' destiny, Wagner tubas
FBEAT = 0.56
T_GATHER = 3.6                              # Brünnhilde gathers the shards
T_TO_SL = 7.4                               # runs to Sieglinde
T_LIFT = 9.6                                # lifts her onto the horse
T_GALLOP = 11.2                             # and away
RBEAT = 0.28
T_GONE = 14.8
T_GRIEF = 15.8                              # Wotan over the body
GBEAT = 0.8
T_GEH = 21.6                                # "Geh hin, Knecht!"
T_WAVE = 23.0                               # the wave of his hand
T_DEAD = 23.4                               # Hunding falls
T_FURY = 29.0                               # "Doch Brünnhilde!"
SPEARS = [29.2, 35.0, 48.0]                 # his spear motif, each a line across the porch
SBEAT = 0.42
T_RIDE = 48.4                               # he rides after her
T_AWAY = 53.6
T_CLEAR = 58.0                              # the storm settles into the clouds of the Valkyries' rock
D = 80.0
CLOCK = 80.0 * 18                           # shared clock: this is the 19th scene

SIEG, HUND, WOTAN, BRUNN, SL = range(5)
BLUE = hexc('#30a8ff')
AMBER = hexc('#ffa860')
HRED = hexc('#8a0020')
WBLUE = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
REDGLOW = hexc('#ff2010')
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
STEEL = hexc('#e8f8ff')
STORM = hexc('#5a6a8a')
CLOUD = hexc('#2a3448')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
PALE = hexc('#a0b0c0')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')

STRIKES = [(29.0, 'all'), (30.8, 'Right'), (32.6, 'Left'), (35.0, 'Porch'), (37.4, 'Side'), (39.2, 'Right'),
           (41.6, 'Left'), (43.2, 'Porch'), (45.6, 'Right'), (47.0, 'Left'), (49.2, 'Left'), (51.0, 'Side'),
           (52.4, 'Side'), (55.6, 'Right'), (59.0, 'Left'), (62.6, 'Right'), (66.4, 'Side'), (70.6, 'Right'),
           (74.2, 'Left')]
HUNDING = [(0, 0.75, 'D2'), (0.75, 0.25, 'D2'), (1, 1, 'F2'), (2, 0.75, 'E2'), (2.75, 0.25, 'C2'),
           (3, 2, 'D2')]                    # Hunding's motif (composed): low, heavy, rhythmic


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_STAB, 'D2', 96, 'trem')                                          # the fight's last roar
    for j in range(8):                                                          # Hunding's lunge
        add(T_THRUST + j * 0.07, 0.1, note('D2') + (0, 2, 3, 5, 7, 8, 10, 12)[j], 100 + 3 * j, 'rip', HUND)
    add(T_STAB, 2.5, 'D2', 124, 'stab', SIEG)
    for m in ('D2', 'A2', 'D3', 'F3', 'Bb3'):
        add(T_STAB, 1.2, m, 116, 'stabchord', SIEG)
    add(T_STAB + 0.35, 0.5, 'D5', 92, 'cry', SL)                                # Sieglinde's cry, far off
    add(T_STAB + 0.85, 1.0, 'A4', 80, 'cry', SL)
    add(T_STAB + 0.5, T_GRIEF - T_STAB + 4.0, 'C2', 62, 'pedal')
    for t, m, v, d in play('volsung_fate', T_FATE, FBEAT, 0, 66):              # the Volsungs' destiny
        add(t, d, m, v - (8 if m < note('G2') else 0), 'fate', SIEG)
    for k in range(10):                                                         # the shards, gathered
        add(T_GATHER + 0.3 + k * 0.33, 1.2, ('E5', 'A5', 'D5', 'F5', 'E5', 'A4', 'D6', 'Bb5', 'A5', 'F5')[k], 74,
            'shard', BRUNN)
    add(T_TO_SL, 0.6, 'A4', 96, 'call', BRUNN)                                  # she runs to Sieglinde
    add(T_TO_SL + 0.6, 0.9, 'D5', 100, 'call', BRUNN)
    for k in range(2):                                                          # the Ride: away with her
        for t, m, v, d in play('ride', T_GALLOP + k * 6 * RBEAT, RBEAT, 0, 104):
            add(t, d * 1.15, m, v, 'ride', BRUNN)
    for j in range(int((T_GONE + 1.0 - T_GALLOP) / (RBEAT * 1.5))):            # hooves, in 6/8
        add(T_GALLOP + j * RBEAT * 1.5, 0.12, 'D2', 92 - 2 * j, 'hoof', BRUNN)
        add(T_GALLOP + j * RBEAT * 1.5 + RBEAT, 0.08, 'A2', 80 - 2 * j, 'hoof', BRUNN)
    for t, m, v, d in play('volsung_fate', T_GRIEF, GBEAT, 0, 70):             # Wotan's grief over the body
        if t < T_GRIEF + 8 * GBEAT - 0.01:
            add(t, d, m, v, 'grief', WOTAN)
    for b, d, n in ((0, .5, 'D3'), (.5, .5, 'D3'), (1, 1, 'A2'), (2, .5, 'F3'), (2.5, 1.5, 'D3')):
        add(T_GEH + b * 0.32, d * 0.32 * 1.2, n, 110, 'geh', WOTAN)            # "Geh hin, Knecht!"
    add(T_WAVE - 0.4, 0.9, 'D4', 100, 'wave', WOTAN)
    add(T_DEAD, 1.2, 'D2', 116, 'dead', HUND)
    for b, d, n in HUNDING:                                                     # his motif, dying under him
        add(T_DEAD + 0.3 + b * 0.5, d * 0.5 * 1.1, note(n) - (2 if b >= 2 else 0), 100 - int(10 * b), 'hunding', HUND)
    add(T_DEAD + 1.0, 3.0, 'D1', 70, 'roll')
    add(T_DEAD + 2.5, T_FURY - T_DEAD - 2.5, 'D2', 56, 'trem')                 # silence, then a stirring
    add(T_FURY, 3.0, 'D2', 124, 'crash')
    add(T_FURY - 0.6, 0.6, 'D2', 110, 'surge')
    for k, ts in enumerate(SPEARS):                                             # the spear, three times
        for t, m, v, d in play('spear', ts, SBEAT, 0, 120 - 4 * k):
            add(t, d * 1.1, m, v, 'spear', WOTAN)
    for k in range(int((D - 2 - T_FURY) / (12 * 0.3))):                  # the storm in the low strings
        t0 = T_FURY + 0.4 + k * 12 * 0.3
        vel = int(112 - max(0, t0 - T_AWAY) * 1.0)
        for t, m, v, d in play('storm', t0, 0.3, 0, vel):
            add(t, d * 1.05, m, v, 'storm')
    add(T_FURY, D - T_FURY, 'D3', 90, 'vtrem')
    for ts, where in STRIKES:
        add(ts, 2.0, 'D1', 120 if ts < T_AWAY else 96, 'thunder', where)
    for m in ('D2', 'A2', 'D3'):                                                # the storm, left to itself
        add(T_CLEAR, D - T_CLEAR, m, 70, 'drone')
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
    """Per frame: where Siegmund, Hunding, Wotan, Brünnhilde and Sieglinde are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 4.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    S0, H0, W0 = at(G, 'Porch Front', 0.35), at(G, 'Porch Front', 0.62), at(G, 'Porch Front', 0.5)
    B0, L0 = at(G, 'Porch Right', 0.3), at(G, 'Left', 0.7)
    set_(SIEG, 0, D, S0, 6.0)
    set_(SIEG, T_STAB, T_OUT, S0 - 10, 2.0)                                     # staggering back as he falls
    set_(HUND, 0, D, H0, 6.0)
    set_(HUND, T_THRUST, T_STAB + 0.4, S0 + 30, 9.0)
    set_(HUND, T_STAB + 0.4, D, S0 + 60, 2.0)
    set_(WOTAN, 0, D, W0, 6.0)
    set_(WOTAN, T_GRIEF, T_WAVE, S0 + 32, 0.9)                                  # bending over the body
    set_(WOTAN, T_WAVE, T_RIDE, W0 - 10, 2.0)
    # Brünnhilde: across the shards, to Sieglinde, and away along Left and Side
    marks = [(0.0, B0), (T_GATHER, B0), (T_GATHER + 1.2, at(G, 'Porch Front', 0.56)),
             (T_TO_SL - 0.2, at(G, 'Porch Front', 0.28)), (T_LIFT - 0.2, L0 + 4), (T_GALLOP, L0 + 4),
             (T_GALLOP + 1.6, at(G, 'Left', 0.15)), (T_GONE, -140.0), (D, -140.0)]
    ts, ds = zip(*marks)
    set_(BRUNN, 0, D, np.interp(t, ts, ds), 8.0)
    set_(SL, 0, D, L0, 6.0)
    set_(SL, T_LIFT + 0.3, D, np.interp(t, ts, ds) + 16, 9.0)                   # on the horse, just behind her
    # Wotan rides after her
    set_(WOTAN, T_RIDE, D, np.interp(t, (T_RIDE, T_AWAY), (W0 - 10, -260.0)), 7.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(5)])
    return dict(t=t, pos=pos)


def storm_bed(d, tt, porch, wild):
    """Act II's storm: dark slate and navy, rolling with grey-blue billows; wilder and brighter in his fury."""
    r1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.05 * tt))
    r2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 150 + 0.09 * tt) + 2)
    r3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 - 0.32 * tt) + 1)          # the gale, racing over in his fury
    return (light(CLOUD, 0.38 + 0.55 * r1 ** 1.5) + light(NAVY, 0.4)
            + light(STORM, (0.08 + 0.6 * (r1 * r2) ** 2) * (0.7 + 0.5 * wild) + 0.45 * wild * r3 ** 3))


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def fight_end(G):
    """The last frame of The Fight (WK18), carried on in time, so this scene can start exactly where it ended
    and dissolve into its own look: the same storm, figures, glints and shards (its seeded draws replayed).
    Returns f(t) -> (N,3) for our t."""
    d = G.pd
    L = G.length
    rng = np.random.default_rng(18)
    tw = Flicker(rng, G.N, 2.0, 8.0)
    for _ in range(19):
        rng.uniform(at(G, 'Porch Left', 0.3), at(G, 'Porch Right', 0.7))
    rng.uniform(120, 300, 19)
    srest = np.sort(np.random.default_rng(1800).uniform(at(G, 'Porch Left', 0.55), at(G, 'Porch Right', 0.45), 18))
    rng.uniform(0, L, 42)
    sv = rng.uniform(0.5, 1.0, 60)[:18]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    heights = smoothstep(-200, -560, G.pos[:, 2]) * porch
    pf0, pf1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    sm, hd, wp = at(G, 'Porch Front', 0.35), at(G, 'Porch Front', 0.622), at(G, 'Porch Front', 0.5)
    b, ln = at(G, 'Porch Right', 0.3), at(G, 'Left', 0.7)
    hd = 1528.0 if abs(hd - 1528.0) < 2 else hd
    hs = smoothstep(hd + 12, hd + 16, d) * smoothstep(hd + 40, hd + 34, d)
    span = smoothstep(wp - 166, wp - 154, d) * smoothstep(wp + 166, wp + 154, d) * (d >= pf0) * (d <= pf1)
    dark = hexc('#2a2e38')

    def f(t):
        T = t + CLOCK
        age = t + 5.0
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - T / 9))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 + T / 13) + 1.3)
        fr = light(dark, 0.45) + light(STORM, 0.1 + 0.42 * c1 ** 2 * (0.5 + 0.5 * c2))
        pulse = 0.85 + 0.15 * np.sin(2 * np.pi * T / 2.3)
        fr += light(hexc('#ff2000'), pulse * (0.7 * np.exp(-((d - wp) / 110) ** 2) + 0.25 * heights))
        fr = fr * (1 - 0.5 * np.exp(-((d - wp) / 40) ** 2))[:, None]
        fr += light(WBLUE, 1.1 * np.exp(-((d - wp) / 26) ** 2)) + light(WBLUE, 0.35 * np.exp(-((d - wp) / 90) ** 2))
        fr += light(SPEAR, 0.3 * span)
        fr = fr * (1 - 0.75 * np.exp(-((d - hd) / 38) ** 2))[:, None]
        fr += light(HRED, np.exp(-((d - hd) / 15) ** 2)) + light(hexc('#a07070'), 0.7 * hs)
        fr += light(SILVER, 0.6 * np.exp(-((d - b) / 16) ** 2) + 0.22 * 0.6 * np.exp(-((d - b) / 60) ** 2))
        for j, o in enumerate((-24, -9, 10, 23)):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(GOLD, 0.6 * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        fr += light(GOLD, 0.55 * np.exp(-((d - b - 16) / 7) ** 2))
        fr += light(BLUE, 0.8 * np.exp(-((d - sm) / 16) ** 2) + 0.2 * np.exp(-((d - sm) / 60) ** 2))
        fr += light(hexc('#ffcc40'), 0.56 * np.exp(-((d - sm - 12) / 3.5) ** 2))
        fr += light(WHITE, np.exp(-age / 0.12) + 0.8 * np.exp(-age / 0.6) * np.exp(-((d - wp) / (60 + 500 * age)) ** 2))
        g = (((0.6 + 0.4 * np.exp(-age / 0.8)) * sv)[None, :] * np.exp(-((d[:, None] - srest[None, :]) / 6) ** 2)).max(axis=1)
        fr += light(STEEL, g * (0.75 + 0.25 * tw(t + 80.0)))
        fr += light(AMBER, 0.299 * np.exp(-((d - ln) / 15) ** 2) + 0.25 * 0.299 * np.exp(-((d - ln) / 55) ** 2))
        return fr
    return f


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    pfm = (G.seg_of == 'Porch Front').astype(float)
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))       # the rock's stones, every scene
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    S0 = at(G, 'Porch Front', 0.35)
    p0, p1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    shards = np.sort(rng.uniform(at(G, 'Porch Front', 0.27), at(G, 'Porch Front', 0.57), 10))
    sh_ph = rng.uniform(0, 2 * np.pi, 10)
    fate = np.array([e[0] for e in N if e[4] == 'fate' and e[2] >= note('C3')])
    spear_n = [(e[0], e[2]) for e in N if e[4] == 'spear']
    gut = Flicker(rng, 1, 1.5, 6.0)
    rain_f = Flicker(rng, G.N, 4.0, 11.0)
    tw = Flicker(rng, G.N, 2.0, 6.0)
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}

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

    def span_of(where):
        if where == 'all':
            return 0.0, L
        if where == 'Porch':
            return seg_d['Porch Left'][0], seg_d['Porch Right'][1]
        return seg_d[where]

    tail = fight_end(G)
    picked = np.full(10, np.inf)
    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        fr = np.zeros((G.N, 3))
        P = C['pos'][:, f]

        # the storm: roaring as the fight ends, hushed while Siegmund dies, wild in Wotan's fury, then settling
        wild = (0.6 * (1 - smoothstep(T_STAB, T_STAB + 2.5, t)) + smoothstep(T_FURY - 0.3, T_FURY + 1.5, t)
                - 0.55 * smoothstep(T_AWAY, T_CLEAR + 8, t))
        hush = 1 - 0.35 * smoothstep(T_STAB, T_STAB + 3, t) * (1 - smoothstep(T_FURY - 3, T_FURY, t))
        clear = smoothstep(T_CLEAR, D - 3.0, t)
        bed = storm_bed(d, tt, porch, max(wild, 0)) * hush
        fr += bed * (1 - clear) + rock_bed(d, tt, porch, stone) * clear
        rain = max(wild, 0) * (1 - smoothstep(66, 77, t))
        if rain > 0:
            fr += light(FLASH, 0.32 * rain * smoothstep(0.9, 1.0, rain_f(t)))

        # the spear's steel line across the porch: held at the start, struck again with each spear call
        line = 0.42 * (1 - smoothstep(T_STAB + 0.5, T_STAB + 2.8, t))
        for ts in SPEARS[:2]:
            if ts <= t < ts + 12 * SBEAT:
                line = max(line, 0.75 * np.exp(-(t - ts) / 0.25) + 0.38 * (1 - smoothstep(ts + 9 * SBEAT, ts + 12 * SBEAT, t)))
        if line > 0:
            fr += light(SPEAR, line * pfm * smoothstep(p0 - 5, p0 + 25, d) * smoothstep(p1 + 5, p1 - 25, d))
        for tn, m in spear_n:                               # each note of it a bright step walking down the line
            if tn <= t < tn + 0.6 and tn < SPEARS[2]:
                q = p1 - (p1 - p0) * np.clip((note('Bb3') - m) / 18, 0, 1)
                fr += light(WHITE, 0.8 * np.exp(-(t - tn) / 0.18) * blob(q, 14))

        # Siegmund: struck, guttering, out; a pale glow where he lies, until Wotan turns away
        ps = P[SIEG]
        if t < T_OUT + 0.5:
            g = 1 - smoothstep(T_STAB + 0.2, T_OUT, t)
            sputter = 1 - 0.55 * smoothstep(T_STAB, T_STAB + 1.5, t) * max(0.0, float(gut(t)[0])) ** 2
            b = 0.85 * g * sputter
            fr += light(BLUE, b * blob(ps, 22) + 0.4 * b * blob(ps, 110))
        ghost = smoothstep(T_STAB + 1.0, T_OUT, t) * (1 - smoothstep(T_WAVE, T_WAVE + 3, t))
        if ghost > 0:
            fr += light(PALE, 0.32 * ghost * blob(S0 - 10, 26) * (0.8 + 0.2 * last(fate, t, 0.5)))
        if T_STAB <= t < T_STAB + 1.2:                      # the blow
            age = t - T_STAB
            fr += light(WHITE, 1.1 * np.exp(-age / 0.1) * blob(S0 + 4, 30))
            fr += light(HRED, 1.0 * np.exp(-age / 0.3) * blob(S0 + 4, 120))
            r = 40 + 500 * age ** 0.6
            fr += light(BLUE, 0.7 * (1 - age / 1.2) * np.exp(-((np.abs(d - S0) - r) / 35) ** 2))

        # Hunding: red in his own shadow, the spear point ahead of him; struck down by a wave of Wotan's hand
        ph = P[HUND]
        hb = 0.85 * (1 + 0.6 * np.exp(-max(t - T_DEAD, 0) / 0.2) * (t >= T_DEAD)) * (1 - smoothstep(T_DEAD + 0.2, T_DEAD + 1.8, t))
        ember = 0.3 * smoothstep(T_DEAD + 0.8, T_DEAD + 1.8, t) * (1 - smoothstep(T_DEAD + 2, T_FURY, t))
        hw = 22 * (1 - 0.5 * smoothstep(T_DEAD, T_DEAD + 1.6, t))
        if hb > 0.01 or ember > 0:
            fr *= 1 - 0.65 * (hb / 0.85) * blob(ph, 70)[:, None] * (1 - blob(ph, hw))[:, None]
            fr += light(HRED, 1.1 * hb * blob(ph, hw) + 0.45 * hb * blob(ph, 90) + ember * blob(ph, 14))
            tip = ph - 28 if t < T_THRUST else ph - 28 - 30 * smoothstep(T_THRUST, T_STAB, t)
            fr += light(HRED * 0.6 + SPEAR * 0.4, 0.7 * (hb / 0.85) * (1 - smoothstep(T_STAB, T_STAB + 1, t)) * blob(tip, 8))
        if T_THRUST <= t < T_STAB + 0.3:                    # the lunge, a red streak
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(1, 13, 2)):
                q = C['pos'][HUND][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 18) * (1 - j / 6.5))
            fr += light(HRED, 0.9 * trail)

        # Wotan: towering, red storm glow; bowed in grief; the wave; fury; riding off as a storm
        pw = P[WOTAN]
        vis = smoothstep(-200, 40, pw)
        grief = smoothstep(T_GRIEF - 1, T_GRIEF + 2, t) * (1 - smoothstep(T_WAVE - 0.5, T_WAVE, t))
        fury = smoothstep(T_FURY - 0.2, T_FURY + 0.6, t)
        riding = smoothstep(T_RIDE, T_RIDE + 1.0, t)
        quiet = smoothstep(T_STAB, T_STAB + 3, t) * (1 - fury)
        wb = vis * (0.75 - 0.2 * grief + 0.2 * fury)
        ww = 34 + 10 * fury - 6 * grief
        fr += light(WBLUE, wb * blob(pw, ww) + 0.3 * wb * blob(pw, 170 + 80 * fury))
        red = vis * (0.32 * (1 - quiet) + 0.35 * fury * (0.8 + 0.2 * np.sin(2 * np.pi * 1.7 * t)))
        fr += light(REDGLOW, red * blob(pw, 230 + 120 * fury))
        rage = fury * (1 - smoothstep(T_AWAY, T_CLEAR, t))
        if rage > 0:                                        # his wrath: surges of blue and red rolling out over the house
            ph_ = ((t - T_FURY) / 2.4) % 1.0
            for k in range(2):
                r = 1300 * ((ph_ + 0.5 * k) % 1.0)
                env = 1 - ((ph_ + 0.5 * k) % 1.0)
                band = np.exp(-((np.abs(d - pw) - r) / 200) ** 2) * env
                fr += light(WBLUE, 0.7 * rage * band) + light(REDGLOW, 0.4 * rage * band ** 2)
            fr += light(WBLUE, 0.3 * rage * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 300 - 0.4 * tt))))
        if riding > 0:                                      # the spear streaking ahead of him, his storm behind
            fr += light(SPEAR, 0.7 * riding * vis * smoothstep(pw - 140, pw - 20, d) * smoothstep(pw + 10, pw - 20, d))
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 40, 3)):
                q = C['pos'][WOTAN][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 45) * (1 - j / 13.5))
            fr += light(WBLUE, 0.75 * trail * riding) + light(REDGLOW, 0.35 * trail * riding)
        if T_WAVE <= t < T_WAVE + 1.4:                      # "Geh hin!": a wave of blue rolling out over the porch
            age = t - T_WAVE
            r = 20 + 380 * smoothstep(0, 1.0, age)
            fr += light(WBLUE, 0.95 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 40) ** 2))
            fr += light(SPEAR, 0.6 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 12) ** 2))

        # Brünnhilde: gathering the shards, lifting Sieglinde, galloping away with both
        pb = P[BRUNN]
        bvis = smoothstep(-120, 30, pb)
        recoil = 1 - 0.25 * smoothstep(T_STAB, T_STAB + 0.3, t) * (1 - smoothstep(T_GATHER - 0.6, T_GATHER, t))
        gallop = 0.85 + 0.15 * np.cos(2 * np.pi * (t - T_GALLOP) / (1.5 * RBEAT)) if t >= T_GALLOP else 1.0
        bb = bvis * 0.82 * recoil * gallop
        fr += light(SILVER, bb * blob(pb, 20) + 0.35 * bb * blob(pb, 100))
        for k in range(3):
            q = pb + 20 * np.sin(2 * np.pi * (0.8 * tt + k / 3))
            fr += light(GOLD, 0.75 * bvis * (0.7 + 0.3 * np.sin(2 * np.pi * (3.1 * tt + k))) * blob(q, 5))
        if abs(pb - C['pos'][BRUNN][max(f - 6, 0)]) > 18:   # a silver comet when she moves fast
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 26, 2)):
                q = C['pos'][BRUNN][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 22) * (1 - j / 12.5))
            fr += light(SILVER, 0.55 * bvis * trail)
        newly = (picked == np.inf) & (np.abs(shards - pb) < 12) & (t >= T_GATHER)
        picked[newly] = t
        for k in range(10):                                 # the shards: on the porch, then flying with her
            if t < picked[k]:
                tws = 0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t + sh_ph[k])
                fr += light(STEEL, 0.75 * tws * blob(shards[k], 4.5))
            elif t < picked[k] + 0.5:
                fr += light(WHITE, 0.9 * np.exp(-(t - picked[k]) / 0.15) * blob(shards[k], 10))
        ng = int((picked <= t).sum())
        for k in range(min(ng, 4)):
            q = pb + 30 * np.sin(2 * np.pi * (1.3 * tt + k / 4 + 0.1))
            fr += light(STEEL, 0.65 * bvis * blob(q, 4))

        # Sieglinde: collapsed and dim; then up on the horse, amber close behind the silver
        pl = P[SL]
        lift = smoothstep(T_LIFT, T_LIFT + 1.0, t)
        lb = smoothstep(-120, 30, pl) * (0.52 + 0.2 * lift) * (0.92 + 0.08 * np.sin(2 * np.pi * 0.3 * tt))
        fr += light(AMBER, lb * blob(pl, 18 + 4 * lift) + 0.4 * lb * blob(pl, 100))
        if T_LIFT <= t < T_LIFT + 1.2:
            age = t - T_LIFT
            fr += light(WHITE * 0.5 + AMBER * 0.5, 0.7 * np.exp(-age / 0.3) * blob(pl, 40))

        # lightning: in his fury, and on in the storm after he has gone
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if not 0 <= age < 1.0:
                continue
            a, b = span_of(where)
            if where == 'all':
                fr += light(FLASH, 0.85 * np.exp(-age / 0.12) * np.ones(G.N))
                fr += light(WHITE, bolt(age, pw, 0.0, i) + bolt(age, pw, L, i + 1))
            else:
                mid = 0.5 * (a + b)
                fr += light(WHITE, 0.9 * bolt(age, mid, (a if i % 2 else b), i))
                fr += light(FLASH, 0.35 * np.exp(-age / 0.2) * blob(mid, 0.6 * (b - a)))
        if t < 1.0:                                         # dissolving out of the last frame of The Fight
            w = smoothstep(0.0, 1.0, t)
            fr = tail(t) * (1 - w) + fr * w
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

    def pan_of(who, t):
        return pan_at(max(np.interp(t, C['t'], C['pos'][who]), 0.0))

    for name, gain, rev in (('strings', 0.16, 0.3), ('low', 0.2, 0.18), ('brass', 0.19, 0.28), ('winds', 0.15, 0.32),
                            ('perc', 0.2, 0.25), ('harp', 0.14, 0.45), ('fx', 0.09, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
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
    centre = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, who in compose():
        pa = pan_of(who, t) if who is not None and isinstance(who, int) else centre
        if part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, centre, rise=0.05 if t == 0 else 2.0, fall=0.4, gain=0.8)
        elif part == 'rip':
            M.add('low', vcs.play(m + 12, v), t, 0.9, pa)
            M.add('low', cbs.play(m, v), t, 0.7, pa)
        elif part == 'stab':
            M.add('perc', gong.play(v), t, 1.0, pa)
            M.add('perc', crash.play(v), t, 0.8, pa)
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, pa)
            M.add('fx', whoosh(0.5, 400, 3500, 0.6, seed=19), t - 0.5, 0.8, pa)
        elif part == 'stabchord':
            s = tuba if m < note('A2') else (tbn if m < note('D3') else horn)
            M.add('brass', s.play(m, v, dur=d, release=0.5), t, 0.9, pa)
        elif part == 'cry':
            M.add('winds', ob.play(m, v, dur=d, release=0.3), t, 0.9, pa)
        elif part == 'pedal':
            hold('low', trem, m + 12, t, t + d, v, centre, rise=1.5, fall=2.0, gain=0.5)
            hold('low', cb, m + 12, t, t + d, v - 6, centre, rise=1.5, fall=2.0, gain=0.4)
        elif part == 'fate':
            s = horn if m >= note('G3') else (tbn if m >= note('C3') else tuba)
            M.add('brass', s.play(m, v, dur=d * 1.05, release=0.5), t, 0.6, pa)
        elif part == 'shard':
            M.add('harp', harp.play(m, v), t, 1.0, pa)
        elif part == 'call':
            M.add('brass', horn.play(m, v, dur=d, release=0.3), t, 0.8, pa)
            M.add('brass', tpt.play(m, v - 16, dur=d, release=0.3), t, 0.5, pa)
        elif part == 'ride':
            M.add('brass', horn.play(m, v, dur=d, release=0.15), t, 0.9, pa)
            M.add('brass', tpt.play(m + 12, v - 20, dur=d, release=0.15), t, 0.35, pa)
            M.add('strings', vc.play(m - 12, v - 10, dur=d, release=0.15), t, 0.5, pa)
        elif part == 'hoof':
            M.add('perc', snare.play(v), t, 0.7, pa)
            M.add('low', cbs.play(m + 12, v), t, 0.6, pa)
        elif part == 'grief':
            s = tbn if m >= note('C3') else tuba
            M.add('brass', s.play(m, v, dur=d * 1.05, release=0.6), t, 0.7, pa)
        elif part == 'geh':
            M.add('brass', tbn.play(m, v, dur=d, release=0.25), t, 1.0, pa)
            M.add('low', tuba.play(m - 12, v - 16, dur=d, release=0.25), t, 0.6, pa)
        elif part == 'wave':
            for j in range(10):
                M.add('strings', vn.play(note('D4') + (0, 2, 4, 5, 7, 9, 10, 12, 14, 15)[j], 92, dur=0.12, release=0.1),
                      t + j * 0.04, 0.6, pa)
            M.add('fx', whoosh(1.0, 600, 4500, 0.7, seed=23), t, 0.9, pa)
        elif part == 'dead':
            M.add('perc', timp.play(v, pitch=-7), t, 1.0, pan_of(HUND, t))
            M.add('perc', bd.play(v), t, 0.8, pan_of(HUND, t))
        elif part == 'hunding':
            M.add('low', tuba.play(m, v, dur=d, release=0.3), t, 1.0, pan_of(HUND, t))
            M.add('brass', tbn.play(m + 12, v - 20, dur=d, release=0.3), t, 0.5, pan_of(HUND, t))
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.5, pan_of(HUND, t))
        elif part == 'surge':
            M.add('perc', roll.play(v, dur=d + 0.3), t, 0.8, centre)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 1.0, centre)
            M.add('perc', gong.play(v), t, 0.8, centre)
            M.add('perc', timp.play(v, pitch=-5), t, 1.0, centre)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, pa)
            M.add('low', tuba.play(m - 12, v - 6, dur=d, release=0.3), t, 0.85, pa)
            M.add('brass', horn.play(m, v - 16, dur=d, release=0.3), t, 0.5, pa)
        elif part == 'storm':
            M.add('low', vcs.play(m + 12, v), t, 0.8, -0.2)
            M.add('low', cbs.play(m + 12, v - 6), t, 0.7, 0.2)
            if d > 0.15:
                M.add('low', vc.play(m + 12, v - 14, dur=d, release=0.2), t, 0.4, 0.0)
        elif part == 'vtrem':
            hold('strings', vtrem, m, t, t + d, v, 0.0, rise=0.3, fall=3.0, gain=0.35)
            hold('strings', vtrem, m + 5, t, t + d, v - 6, 0.0, rise=0.3, fall=3.0, gain=0.25)
        elif part == 'thunder':
            pt = 0.0 if who in ('all', 'Porch') else pan_at(seg_mid[who])
            M.add('perc', timp.play(v, pitch=-9), t, 1.0, pt)
            M.add('perc', bd.play(v), t, 0.9, pt)
            M.add('perc', roll.play(v - 30, dur=d), t + 0.1, 0.5, pt)
            M.add('fx', whoosh(1.2, 2500, 200, 0.6, seed=int(t * 10)), t, 0.6, pt)
        elif part == 'drone':
            hold('low', trem if m >= note('A2') else cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=1.0, gain=0.8)
