"""O hehrstes Wunder!: Brünnhilde rides in from the free end of Right, silver with gold glints, Sieglinde's
amber held close beside her, to a breathless Ride (Donington 47) on the horns, and comes down on the summit of
the rock in the middle of Porch Front. The sisters flare to greet her; the fallen heroes fade from the rock.

She begs them for help, her own motif (88) on horn and trumpet, and her silver reaches out toward each of
them in turn. But far off to the right the sky growls, a dark blue flicker and a low spear call in the
trombones: Wotan is coming. The sisters refuse, one after another, each a little falling cry on a trumpet as
her light jerks back and dims, until all eight have shrunk away to the edges of the rock, shivering.

Sieglinde wants only to die: her motif (36) on the oboe over the cellos, and her amber sinks, flickers and
shrinks under a wash of indigo. Then Brünnhilde tells her she carries Siegmund's son, the hero to come, and
Siegfried's motif (53) rings out on the horns, three times and growing: with each note a seed of gold-white
light pulses inside her amber. Sieglinde rises, and sings "O hehrstes Wunder!" (90b), the violins and oboe
soaring over a harp and a glowing chorus of strings and horns: a golden-amber blaze rolls out from her in
waves over the whole house and holds it, warm, at its height. Brünnhilde gives her the pieces of Nothung,
the sword's motif (43) on a trumpet, each note a white steel glint flying from the silver into the amber.
Sieglinde flees east toward the forest, out along the Left wing and Side with the glints round her, the
Siegfried motif going with her in the cellos. The sisters creep back to their places, and at the free end
of Right a blue-black storm begins to gather and flicker: the timpani roll, the storm stirs in the basses.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK22'
TITLE = 'O hehrstes Wunder!'
KIND = 'show'
DESCRIPTION = ('Brünnhilde arrives with Sieglinde, but her sisters are too afraid of Wotan to help. Sieglinde '
               'wants to die, until Brünnhilde tells her she is carrying Siegmund\'s child, and her cry of joy '
               'turns the whole house to gold.')
VOICEOVER = ('A woman who has lost everything learns that she is going to have a child. '
             'Listen to her answer.')

RB = 0.3
T_LAND = 5.4                                # Brünnhilde lands on the summit
T_PLEA = 6.4                                # "Schützt mich!" (her motif)
PBEAT = 0.55
FAR = [9.0, 15.6, 21.6]                     # Wotan, far off
REFUSE = [12.4 + 1.25 * i for i in range(8)]    # one by one the sisters refuse
T_DIE = 23.6                                # Sieglinde's lament
LBEAT = 0.7
T_SON = [34.6, 37.8, 41.0]                  # Siegfried's motif: the son she carries
SBEAT = 0.6
T_WUNDER = 45.0                             # "O hehrstes Wunder!"
WBEAT = 0.75
T_SHARDS = 58.6                             # the pieces of Nothung
NBEAT = 0.55
T_FLEE = 66.0                               # Sieglinde flees east
T_GONE = 73.0
T_STORM = 74.0                              # Wotan's storm gathering at the free end of Right
D = 80.0
CLOCK = 80.0 * 21

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
SPOTS = [('Porch Left', 0.25), ('Porch Left', 0.65), ('Porch Front', 0.12), ('Porch Front', 0.37),
         ('Porch Front', 0.63), ('Porch Front', 0.88), ('Porch Right', 0.35), ('Porch Right', 0.75)]
BACK = [('Porch Left', 0.12), ('Porch Left', 0.45), ('Porch Left', 0.8), ('Porch Front', 0.13),
        ('Porch Front', 0.9), ('Porch Right', 0.2), ('Porch Right', 0.55), ('Porch Right', 0.85)]
ORDER = [4, 3, 6, 2, 7, 1, 5, 0]            # who refuses when
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
AMBER = hexc('#ffa860')
BLAZE = hexc('#ffb030')
STEEL = hexc('#e8f8ff')
FATE = hexc('#2a1a5a')
WBLUE = hexc('#1a3cff')
THUNDER = hexc('#060a24')
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


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). who: 0-7 a sister, 'b' Brünnhilde, 's' Sieglinde."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for p, tr in enumerate((0, 3)):                                             # the Ride, breathless
        for t, m, v, d in play('ride', 0.2 + p * 6 * RB, RB, tr, 104):
            add(t, d * 1.5, m, v, 'ride', 'b')
        for bar in range(2):
            for b, dd in ((0, 1.0), (1.0, 0.5), (1.5, 1.0), (2.5, 0.5)):
                add(0.2 + p * 6 * RB + (bar * 3 + b) * RB, dd * RB * 0.9, note(('B1', 'D2')[p]) + (12 if b else 0),
                    96, 'gallop')
    for h in range(int((T_LAND - 0.2) / (1.5 * RB))):
        add(0.2 + h * 1.5 * RB, 0.1, 'B1', 86, 'hoof', 'b')
    for m in ('B1', 'F#2', 'D3', 'B3'):
        add(T_LAND, 1.4, m, 104, 'arrive')
    for t, m, v, d in play('brunnhilde', T_PLEA, PBEAT, 0, 100):                # "Schützt mich und helft!"
        add(t, d, m, v, 'plea', 'b')
    for tf in FAR:                                                              # Wotan, far off
        add(tf, 2.0, 'D1', 90, 'far')
        for t, m, v, d in play('spear', tf + 0.3, 0.45, 0, 76):
            if t < tf + 0.3 + 3 * 0.45:
                add(t, d, m, v, 'farspear')
    for i, (tr, k) in enumerate(zip(REFUSE, ORDER)):                            # they refuse, one by one
        top = note('D5') - (i % 4)
        add(tr, 0.25, top, 104, 'nein', k)
        add(tr + 0.25, 0.6, top - 1, 98, 'nein', k)
        if i % 2 == 0:
            for t, m, v, d in play('valkyrie_cry', tr + 0.1, RB, 0, 70):
                if t < tr + 0.1 + 2 * RB and m >= note('B4'):
                    add(t, d, m, v, 'shiver')
    add(REFUSE[0], T_DIE - REFUSE[0], 'B1', 72, 'dread')
    for t, m, v, d in play('sieglinde', T_DIE, LBEAT, 0, 88):                   # she wants to die
        add(t, d * 1.05, m, v, 'lament' if m >= note('D4') else 'lamentlow', 's')
    for k, ts in enumerate(T_SON):                                              # the son she carries
        for t, m, v, d in play('siegfried', ts, SBEAT, -12 + 2 * k, 96 + 8 * k):
            add(t, d * 1.2, m, v, 'son', 'b')
        add(ts, 4 * SBEAT, ('G2', 'A2', 'B2')[k], 80 + 6 * k, 'sonpad')
    for j in range(14):                                                         # up to the wonder
        add(T_WUNDER - 1.5 + j * 0.1, 0.8, note('A2') + (0, 4, 7, 9, 12, 16, 19, 21, 24, 28, 31, 33, 36, 40)[j], 80, 'harp')
    add(T_WUNDER - 2.5, 2.5, 'A3', 84, 'swell')
    for t, m, v, d in play('redemption', T_WUNDER, WBEAT, -12, 112):            # O hehrstes Wunder!
        add(t, d * 1.08, m, v, 'wunder', 's')
    for b, ch in ((0, ('A2', 'E3', 'C#4', 'A4')), (3, ('C#3', 'G#3', 'E4')), (6, ('E2', 'B3', 'G#4', 'D4')),
                  (9, ('D2', 'A3', 'F#4', 'D4'))):
        for m in ch:
            add(T_WUNDER + b * WBEAT, (3 if b < 9 else 6) * WBEAT * 1.05, m, 92, 'glow')
    for j in range(8):
        add(T_WUNDER + 9 * WBEAT + j * 0.14, 1.5, note('D3') + (0, 4, 7, 12, 16, 19, 24, 28)[j], 80, 'harp')
    for t, m, v, d in play('nothung', T_SHARDS, NBEAT, -12, 104):               # the pieces of Nothung
        add(t, d * 1.1, m, v, 'nothung', 'b')
    for m in ('D3', 'F3', 'A3'):
        add(T_SHARDS, 12 * NBEAT, m, 66, 'glow')
    for k in range(2):                                                          # she flees, the hero's motif with her
        for t, m, v, d in play('siegfried', T_FLEE + 0.3 + k * 2.6, 0.5, -24 + 3 * k, 96):
            add(t, d * 1.1, m, v, 'flight', 's')
    for j in range(int((T_GONE + 1 - T_FLEE) / 0.15)):
        add(T_FLEE + j * 0.15, 0.1, note('D3') + (0, 2, 4, 5, 7, 5, 4, 2)[j % 8], 84, 'hurry', 's')
    add(T_STORM - 1.0, D - T_STORM + 1.0, 'D1', 80, 'roll')                     # the storm gathers
    add(T_STORM, D - T_STORM, 'D2', 74, 'stir')
    for t, m, v, d in play('storm', T_STORM + 1.5, 0.3, 0, 90):
        if t < T_STORM + 1.5 + 6 * 0.3:
            add(t, d, m, v, 'storm')
    for t, m, v, d in play('valkyrie_cry', T_STORM + 2.0, RB, 0, 76):
        if t < D - 1.0 and m >= note('B4'):
            add(t, d, m, v, 'shiver')
    add(77.2, 2.0, 'D1', 96, 'thunder')
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


def choreography(G):
    """Per frame: the sisters, Brünnhilde and Sieglinde (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    home = np.array([sway(G, k, t + CLOCK) for k in range(8)])
    pos = home.copy()
    for i, k in enumerate(ORDER):                                               # shrinking back, then creeping home
        back = at(G, *BACK[k]) + 6 * np.sin(2 * np.pi * (4.0 * t + k))          # shivering
        w = smoothstep(REFUSE[i], REFUSE[i] + 0.6, t) * (1 - smoothstep(T_FLEE + 1, T_STORM, t))
        pos[k] = home[k] + (back - home[k]) * w
    B = at(G, 'Porch Front', 0.55)
    S = at(G, 'Porch Front', 0.4)
    b0 = at(G, 'Right', 1.0) + 40 - 120                                         # where the last scene saw her
    marks = [(0.0, b0), (T_LAND - 0.3, B - 25), (T_LAND + 1.0, B), (D, B)]
    ts, ds = zip(*marks)
    bpos = follow(np.interp(t, ts, ds), np.full(F, 7.0))
    bpos[:3] = b0 - np.arange(3) * 3.0
    reach = np.zeros(F)
    for i, k in enumerate(ORDER):                                               # she turns to each sister as she asks
        reach += 30 * np.sign(at(G, *SPOTS[k]) - B) * np.exp(-((t - REFUSE[i] + 0.4) / 0.5) ** 2)
    bpos = bpos + reach
    smarks = [(0.0, b0 + 18), (T_LAND - 0.3, B - 7), (T_LAND + 1.4, S), (T_FLEE, S), (T_FLEE + 1.5, at(G, 'Porch Left', 0.6)),
              (T_FLEE + 3.8, at(G, 'Left', 0.4)), (T_GONE, -140.0), (D, -140.0)]
    ts, ds = zip(*smarks)
    spos = follow(np.interp(t, ts, ds), np.full(F, 8.0))
    spos[:3] = b0 + 18 - np.arange(3) * 3.0
    return dict(t=t, pos=pos, bpos=bpos, spos=spos)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def thunderhead(fr, d, tt, front, amt):
    """Wotan's storm: a blue-black mass rolling in past `front` (path distance), a roaring blue edge (WK22-WK24)."""
    if amt <= 0:
        return fr
    inside = 1 / (1 + np.exp(-(d - front) / 45))
    churn = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.17 * tt))) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 140 - 0.29 * tt)))
    edge = np.exp(-((d - front) / 70) ** 2)
    fr = fr * (1 - 0.75 * amt * inside)[:, None]
    return (fr + light(THUNDER, 0.9 * amt * inside) + light(WBLUE, amt * (0.1 + 0.55 * churn ** 2) * inside)
            + light(WBLUE, 0.7 * amt * edge * (0.7 + 0.3 * churn)))


def render(G, seed=22):
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
    plea = np.array([e[0] for e in N if e[4] == 'plea'])
    nein = [np.array([e[0] for e in N if e[4] == 'nein' and e[5] == k]) for k in range(8)]
    lament = np.array([e[0] for e in N if e[4] == 'lament'])
    son = np.array([e[0] for e in N if e[4] == 'son'])
    wunder = [(e[0], e[2]) for e in N if e[4] == 'wunder']
    wt = np.array([w[0] for w in wunder])
    shard_t = [e[0] for e in N if e[4] == 'nothung']
    tw = Flicker(rng, G.N, 2.0, 6.0)
    sh_off = rng.uniform(-26, 26, len(shard_t))
    sh_ph = rng.uniform(0, 1, len(shard_t))

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
        pb, ps = C['bpos'][f], C['spos'][f]

        # despair: indigo settling over everything while Sieglinde wants to die
        dark = smoothstep(T_DIE - 1, T_DIE + 3, t) * (1 - smoothstep(T_SON[0], T_SON[1], t))
        if dark > 0:
            fr = fr * (1 - 0.35 * dark) + light(FATE, 0.6 * dark * (0.7 + 0.3 * np.cos(2 * np.pi * (d / 400 - 0.05 * tt))))

        # O hehrstes Wunder: golden-amber waves rolling out from her over the whole house, holding at the height
        blaze = smoothstep(T_WUNDER - 0.5, T_WUNDER + 3.0, t) * (1 - smoothstep(T_WUNDER + 10, T_SHARDS + 2, t))
        if blaze > 0:
            i = int(np.searchsorted(wt, t, side='right')) - 1
            hi = (wunder[i][1] - note('Gb3')) / 15.0 if i >= 0 else 0.0
            wav = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - ps) / 380 - 0.45 * tt))
            fr = fr * (1 - 0.8 * blaze)
            fr += light(BLAZE, blaze * (0.6 + 0.25 * np.clip(hi, 0, 1)) * (0.6 + 0.4 * wav))
            fr += light(AMBER, blaze * 0.35 * (1 - wav))
            fr += light(GOLD, blaze * 0.6 * wav ** 4 * (0.7 + 0.3 * tw(t)))
            fr += light(WHITE * 0.4 + GOLD * 0.6, 0.4 * blaze * last(wt, t, 0.3) * blob(ps, 200))

        # Wotan, far off: a dark flicker at the free end of Right
        for tf in FAR:
            if tf <= t < tf + 2.0:
                age = t - tf
                g = np.exp(-age / 0.6) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * age))
                fr = fr * (1 - 0.4 * g * smoothstep(L - 300, L, d))[:, None] + light(WBLUE, 0.6 * g * smoothstep(L - 260, L, d))
        # and at the end his storm begins to gather there
        amt = 0.6 * smoothstep(T_STORM - 1, D - 1.0, t)
        fr = thunderhead(fr, d, tt, L - 60 - 60 * smoothstep(T_STORM - 1, D - 1.0, t), amt)
        if 77.2 <= t < 78.2:
            fr += light(WHITE, 0.8 * bolt(t - 77.2, L, L - 260, 3))

        # the sisters: greeting her, shrinking back one by one, dimmed and shivering; home again at the end
        heroes = 1 - smoothstep(0.5, 6.0, t)
        for k in range(8):
            p = C['pos'][k][f]
            i = ORDER.index(k)
            fear = smoothstep(REFUSE[i], REFUSE[i] + 0.5, t) * (1 - 0.6 * smoothstep(T_WUNDER - 1, T_WUNDER + 3, t))
            fear = max(fear, 0.0) * (1 - smoothstep(T_FLEE + 1, T_STORM, t)) + 0.3 * smoothstep(T_STORM - 1, D - 1, t)
            hail = last(np.array([T_LAND]), t, 0.6, 2.0)
            nn = last(nein[k], t, 0.2, 1.0)
            b = 0.85 - 0.3 * fear + 0.35 * hail + 0.3 * nn
            fr += light(COLS[k], b * blob(p, 16) + 0.35 * b * blob(p, 75))
            fr += light(PALE, 0.3 * heroes * blob(at(G, *SPOTS[k]) + 15, 6))
            for tc in nein[k]:
                if tc <= t < tc + 0.8:
                    age = t - tc
                    r = 15 + 220 * age ** 0.7
                    fr += light(COLS[k], 0.55 * (1 - age / 0.8) * np.exp(-((np.abs(d - p) - r) / 22) ** 2))
            if T_LAND <= t < T_LAND + 1.2:
                fr += light(COLS[k], 0.5 * np.exp(-(t - T_LAND) / 0.4) * blob(p, 60))

        # Brünnhilde: riding in, landing on the summit, pleading with each sister in turn
        riding = t < T_LAND + 0.5
        gal = 0.85 + 0.15 * np.cos(2 * np.pi * tt / (1.5 * RB)) if riding else 1.0
        pl = last(plea, t, 0.3, 1.5)
        bb = (0.55 + 0.25 * smoothstep(T_LAND - 1.5, T_LAND + 0.5, t)) * gal + 0.2 * pl
        fr += light(SILVER, bb * blob(pb, 16 + 2 * smoothstep(0, T_LAND, t)) + 0.3 * bb * blob(pb, 70 + 10 * smoothstep(0, T_LAND, t)))
        for kg in range(3):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, (0.5 + 0.15 * smoothstep(T_LAND, T_LAND + 2, t)) * blob(q, 5) * (kg < 2 or t > T_LAND))
        if riding and abs(pb - C['bpos'][max(f - 4, 0)]) > 8:
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 26, 2)):
                trail = np.maximum(trail, blob(C['bpos'][max(f - lag, 0)], 20) * (1 - j / 12.5))
            fr += light(SILVER, 0.55 * trail)
        if T_LAND <= t < T_LAND + 1.4:
            age = t - T_LAND
            fr += light(SILVER, 0.7 * np.exp(-age / 0.4) * porch * blob(pb, 300))
        for i, k in enumerate(ORDER):                                           # her plea reaching toward each sister
            tr = REFUSE[i] - 0.5
            if tr <= t < tr + 0.6:
                u = (t - tr) / 0.6
                q = pb + (C['pos'][k][f] - pb) * u
                fr += light(SILVER, 0.6 * (1 - u) * blob(q, 12))

        # Sieglinde: on the horse, set down, sinking toward death; the child; the wonder; fleeing with the shards
        sv = smoothstep(-120, 20, ps)
        seed_ = smoothstep(T_SON[0], T_SON[0] + 0.4, t)
        die = dark
        sb = sv * (0.45 + 0.15 * smoothstep(T_LAND, T_LAND + 2, t) - 0.3 * die + 0.35 * blaze + 0.15 * seed_)
        sb *= 1 - 0.35 * die * max(0.0, np.sin(2 * np.pi * 1.3 * t)) ** 4
        lm = last(lament, t, 0.5, 2.0)
        fr += light(AMBER, (sb + 0.1 * lm) * blob(ps, 15 + 3 * blaze) + 0.35 * sb * blob(ps, 70))
        if seed_ > 0:                                                           # the child: a gold-white seed in her light
            sn = last(son, t, 0.25, 1.0)
            fr += light(GOLD * 0.6 + WHITE * 0.4, sv * seed_ * (0.4 + 0.5 * sn) * blob(ps, 5 + 3 * sn))
        given = [ts_ for ts_ in shard_t if ts_ <= t]
        for j, ts_ in enumerate(shard_t):                                       # the shards: flying from her to Sieglinde
            if ts_ <= t < ts_ + 0.5:
                u = (t - ts_) / 0.5
                q = pb + (ps - pb) * u
                fr += light(STEEL, 0.9 * blob(q, 7)) + light(WHITE, 0.5 * blob(q, 3))
            elif t >= ts_ + 0.5:
                q = ps + sh_off[j] * np.sin(2 * np.pi * (0.6 * tt + sh_ph[j]))
                fr += light(STEEL, 0.6 * sv * blob(q, 4) * (0.7 + 0.3 * np.sin(2 * np.pi * (2.1 * tt + sh_ph[j]))))
        if T_FLEE <= t and abs(ps - C['spos'][max(f - 4, 0)]) > 8:
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 26, 2)):
                trail = np.maximum(trail, blob(C['spos'][max(f - lag, 0)], 20) * (1 - j / 12.5))
            fr += light(AMBER, 0.8 * sv * trail + 0.25 * sv * blob(ps, 150))
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
        tr = C['bpos'] if who == 'b' else C['spos'] if who == 's' else C['pos'][who]
        return pan_at(float(np.clip(np.interp(t, C['t'], tr), 0, G.length)))

    for name, gain, rev in (('brass', 0.22, 0.3), ('low', 0.22, 0.2), ('strings', 0.21, 0.35), ('winds', 0.2, 0.35),
                            ('perc', 0.2, 0.28), ('harp', 0.18, 0.45), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
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

    rock = pan_at(at(G, 'Porch Front', 0.5))
    right = pan_at(G.length)
    for t, d, m, v, part, who in compose():
        pa = pan_of(who, t) if who is not None else rock
        if part == 'ride':
            M.add('brass', horn.play(m, v, dur=d, release=0.15), t, 0.85, pa)
            M.add('brass', tpt.play(m + 12, v - 22, dur=d, release=0.15), t, 0.3, pa)
        elif part == 'gallop':
            M.add('low', cbs.play(m + 12, v), t, 0.6, -0.2)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.5, 0.2)
        elif part == 'hoof':
            M.add('perc', snare.play(v), t, 0.55, pa)
        elif part == 'arrive':
            hold('brass', tuba if m < note('F#2') else horn, m + (12 if m < note('F#2') else 0), t, t + d, v, rock,
                 rise=0.05, fall=0.8, gain=0.5)
            if m == note('B1'):
                M.add('perc', crash.play(100), t, 0.6, rock)
                M.add('perc', timp.play(110, pitch=-4), t, 0.7, rock)
        elif part == 'plea':
            if m >= note('Eb4'):
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pa)
                M.add('brass', tpt.play(m, v - 24, dur=d * 1.05, release=0.3), t, 0.3, pa)
            else:
                hold('strings', va if m >= note('C3') else vc, m, t, t + d, v - 26, pa, rise=0.3, fall=0.8, gain=0.4)
        elif part == 'far':
            M.add('perc', roll.play(v, dur=d), t, 0.6, right)
            M.add('perc', timp.play(v, pitch=-8), t, 0.5, right)
        elif part == 'farspear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 0.6, right)
        elif part == 'nein':
            M.add('brass', tpt.play(m - 12, v, dur=d, release=0.15), t, 0.7, pa)
            M.add('brass', horn.play(m - 12, v - 16, dur=d, release=0.15), t, 0.4, pa)
        elif part == 'shiver':
            M.add('winds', pic.play(m, v), t, 0.5, -0.3 + 0.6 * ((t * 3) % 1))
        elif part == 'dread':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.6)
        elif part == 'lament':
            M.add('winds', ob.play(m, v, dur=d, release=0.35), t, 0.95, pa)
        elif part == 'lamentlow':
            M.add('strings', vc.play(m + 12 if m < note('C3') else m, v - 12, dur=d, release=0.35), t, 0.65, pa)
        elif part == 'son':
            M.add('brass', horn.play(m, v, dur=d, release=0.25), t, 0.9, pa)
            if v > 100:
                M.add('brass', tpt.play(m, v - 16, dur=d, release=0.25), t, 0.5, pa)
        elif part == 'sonpad':
            hold('strings', trem, m + 12, t, t + d, v, rock, rise=0.3, fall=0.8, gain=0.5)
            M.add('perc', timp.play(v, pitch=-3), t, 0.4, rock)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 1.0, pan_of('s', t) + 0.3 * (m - 57) / 24)
        elif part == 'swell':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.0, rise=2.0, fall=0.3, gain=0.5)
            M.add('perc', roll.play(v, dur=d), t, 0.5, rock)
        elif part == 'wunder':
            ps_ = pan_of('s', t)
            M.add('strings', vn.play(m, v, dur=d, release=0.5), t, 1.0, ps_ - 0.15)
            M.add('strings', vn.play(m, v - 6, dur=d, release=0.5), t, 0.6, ps_ + 0.15)
            M.add('winds', ob.play(m, v - 10, dur=d, release=0.5), t, 0.7, ps_)
            M.add('strings', vc.play(m - 12, v - 14, dur=d, release=0.5), t, 0.5, ps_)
            if t < T_WUNDER + 0.05:
                M.add('perc', crash.play(104), t, 0.7, ps_)
        elif part == 'glow':
            s = horn if note('C3') <= m < note('F4') else (va if m >= note('F4') else vc)
            hold('brass' if s is horn else 'strings', s, m, t, t + d, v, rock, rise=0.4, fall=1.2, gain=0.45)
        elif part == 'nothung':
            M.add('brass', tpt.play(m, v, dur=d, release=0.3), t, 0.85, pan_of('b', t))
            M.add('harp', harp.play(m + 12, 84), t + 0.45, 0.6, pan_of('s', t))
        elif part == 'flight':
            M.add('strings', vc.play(m + 12, v, dur=d, release=0.2), t, 0.8, pa)
            M.add('brass', horn.play(m + 12, v - 14, dur=d, release=0.2), t, 0.5, pa)
        elif part == 'hurry':
            M.add('strings', vns.play(m + 12, v), t, 0.4, pa)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, right)
        elif part == 'stir':
            hold('low', trem, m + 12, t, t + d, v, right * 0.7, rise=2.0, fall=0.5, gain=0.7)
            hold('low', cb, m + 12, t, t + d, v, right * 0.7, rise=2.0, fall=0.5, gain=0.4)
        elif part == 'storm':
            M.add('low', cbs.play(m + 12, v), t, 0.7, right * 0.7)
            M.add('low', vcs.play(m + 12, v - 8), t, 0.6, right * 0.7)
        elif part == 'thunder':
            M.add('perc', bd.play(v), t, 0.7, right)
            M.add('perc', timp.play(v, pitch=-9), t, 0.7, right)
            M.add('fx', whoosh(1.2, 2500, 200, 0.6, seed=77), t, 0.6, right)
