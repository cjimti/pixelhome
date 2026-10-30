"""The Sword in the Tree: Sieglinde (hearth amber) slips back in through the inner door at the corner of Left,
Hunding drugged asleep behind her, and comes to Siegmund at the dead hearth (her own motif, Donington 36, on
the cellos). She has a weapon to show him, and a story.

The story takes the house. Hunding's kinsmen sat in this hall at her wedding feast, a wedding she never wanted:
torches flare along every run and the guests are small warm lights all over the roof while a heavy, joyless
drinking tune plods in the bassoons and low strings. Then a stranger came in, an old man in grey, his hat pulled
down over one eye: a blue-grey figure under a dark brim with a single bright eye, walking in slowly from the
door at the free end of Right to the Wanderer's chords (Donington 17) on trombones and tubas. The guests' lights
shrink from him as he passes; his one eye finds her, and Valhalla (Donington 63) sounds in the horns, for she
knows that look. He swings a sword, the Sword (Donington 45) on a trumpet, and drives it into the ash to the
hilt: a long white blade of light slams into the trunk with one flash over the house, and the hilt is left
blazing gold.

He walks out the way he came. The guests try their strength one after another: each light rushes to the tree
and strains at the hilt, swelling and trembling while the strings climb, and is thrown back sliding down a
chromatic scale; the last time all of them heave together and fail. The torches fade back into the dark hut
and she turns to Siegmund: then she knew whom the sword was waiting for. The love of the twins (Donington 37)
rises on the cellos and oboe as the two lights draw together, and the wind starts to press at the door.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK08'
TITLE = 'The Sword in the Tree'
KIND = 'show'
DESCRIPTION = ('Sieglinde tells of her wedding feast, when a stranger in grey with one eye hidden under his hat '
               'drove a sword into the ash tree up to the hilt. Every man in the hall tried to pull it out, and '
               'every one of them failed.')
VOICEOVER = ('Sieglinde has a secret to tell. On her wedding day, a stranger left something in that tree, '
             'and nobody has been strong enough to take it out.')

K = 7                                       # this scene's place in the shared clock (t + 80 * K)
T_ENTER = 0.6                               # she comes back in through the inner door
T_FEAST = 7.0                               # the wedding feast
FBEAT = 0.55
T_STRANGER = 16.0                           # the stranger comes in at the door
WBEAT = 0.6
T_VALHALLA = 26.0                           # his eye finds her
VBEAT = 0.7
T_SWING = 31.6
T_PLUNGE = 33.0                             # into the ash, to the hilt
T_LEAVE = 35.5
TRIES = [42.0, 46.0, 50.0, 54.0]            # one by one they try
T_ALL = 58.0                                # all together
T_KNEW = 63.5                               # then she knew whom it waited for
T_LOVE = 70.0
LBEAT = 0.6
D = 80.0

BLUE = hexc('#30a8ff')
AMBER = hexc('#ffa860')
EMBER = hexc('#ff6a10')
HOT = hexc('#ffb040')
HUT = hexc('#a05a28')
TRUNK = hexc('#5a3010')
LEAF = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
STEEL = hexc('#e8f8ff')
GREY = hexc('#5878b8')
BRIM = hexc('#2a3450')
EYE = hexc('#d8ecff')
TORCH = hexc('#ffa040')
KIN = [hexc(c) for c in ('#ff7a30', '#ffb050', '#e05020', '#ffd080', '#c84018', '#ff9a50', '#e8a040')]
WHITE = hexc('#ffffff')

BED, TRUNK_L, LEAF_L, STORM_L, SIEG_L, LINDE_L = 0.26, 0.55, 0.3, 0.32, 0.5, 0.55
EMBER_L = 0.18
GLINT_IN, GLINT_OUT = 0.22, 0.42
NG = 12                                     # guests


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for t, m, v, d in play('sieglinde', T_ENTER + 0.3, 0.45, 0, 76):          # she slips back in
        if m < note('C4'):
            add(t, d, m, v, 'linde_low')
        else:
            add(t, d, m, v - 8, 'linde')
    add(0.0, T_FEAST, 'D2', 60, 'pedal')

    tune = [('E3', 'G3'), ('B2', 'D3'), ('C3', 'E3'), ('B2', 'D#3')]           # the joyless feast
    for k in range(int((T_STRANGER - T_FEAST) / (3 * FBEAT))):
        lo, hi = tune[k % 4]
        add(T_FEAST + k * 3 * FBEAT, FBEAT * 0.9, note(lo) - 12, 88, 'oom')
        add(T_FEAST + (k * 3 + 1) * FBEAT, FBEAT * 0.6, hi, 70, 'pah')
        add(T_FEAST + (k * 3 + 2) * FBEAT, FBEAT * 0.6, hi, 66, 'pah')
    tale = [(0, 1.5, 'B4'), (1.5, .5, 'A4'), (2, 1, 'G4'), (3, 1, 'E4'), (4, 2, 'F#4'), (6, 1, 'G4'), (7, 1, 'A4'),
            (8, 1.5, 'B4'), (9.5, .5, 'C5'), (10, 2, 'B4'), (12, 1, 'A4'), (13, 1, 'G4'), (14, 2, 'E4')]
    for b, d, n in tale:                                                        # "Der Männer Sippe sass hier im Saal"
        add(T_FEAST + 0.5 + b * FBEAT, d * FBEAT, n, 88, 'tale', 'linde')

    for t, m, v, d in play('wanderer', T_STRANGER, WBEAT, 0, 86):              # the stranger in grey
        add(t, d, m, v, 'wanderer')
    add(T_STRANGER, T_SWING - T_STRANGER, 'Eb1', 60, 'deep')
    for t, m, v, d in play('valhalla', T_VALHALLA, VBEAT, 0, 92):              # his eye: Valhalla
        add(t, d, m, v, 'valhalla')

    add(T_SWING, T_PLUNGE - T_SWING, 'C3', 90, 'rush')
    for t, m, v, d in play('sword', T_SWING, 0.18, 0, 112):                    # the Sword, driven home
        add(t, d * 1.2, m, v, 'sword')
    add(T_PLUNGE, 1.0, 'C2', 124, 'plunge')
    for m in ('C3', 'G3', 'C4', 'E4', 'G4'):
        add(T_PLUNGE, T_LEAVE + 4 - T_PLUNGE, m, 92, 'blaze')
    for t, m, v, d in play('wanderer', T_LEAVE + 0.5, WBEAT * 0.8, 0, 88, line='bass'):
        if t < TRIES[0] - 0.5:
            add(t, d, m, v, 'wander_out')

    for k, t0 in enumerate(TRIES + [T_ALL]):                                    # they strain, and fail
        big = t0 == T_ALL
        root = note('E2') + 2 * k
        add(t0, 1.2, root, 80, 'run_in')
        for j in range(10 if big else 8):
            add(t0 + 1.2 + 0.18 * j, 0.25, root + 12 + j, 86 + 3 * j, 'strain')
        add(t0 + 1.2, 1.8, root, 90 + 10 * big, 'heave')
        for j in range(8):
            add(t0 + 3.1 + 0.07 * j, 0.12, root + 24 + 8 - 2 * j, 96 - 3 * j, 'fail')
        add(t0 + 3.1, 0.6, root - 12, 104 + 14 * big, 'thud')
    for m in ('E3', 'B3', 'G3'):
        add(T_LEAVE + 1.5, TRIES[0] - T_LEAVE + 1.0, m, 64, 'shade')
        if big:
            add(t0 + 3.1, 1.0, 'C5', 110, 'crash')
    for m in ('E2', 'B2'):
        add(TRIES[0], T_KNEW - TRIES[0], m, 62, 'pedal')

    for t, m, v, d in play('valhalla', T_KNEW, VBEAT * 1.1, 0, 70, line='melody'):   # then she knew
        add(t, d, m, v, 'knew')
    for m in ('Db3', 'F3', 'Ab3'):
        add(T_KNEW, T_LOVE - T_KNEW, m, 60, 'shade')
    add(T_KNEW, T_LOVE - T_KNEW, 'Db2', 60, 'pedal')
    for t, m, v, d in play('twins_love', T_LOVE, LBEAT, 0, 86):                 # the love of the twins
        if t < D - 1.0:
            add(t, min(d, D - t), m, v, 'love' if m >= note('Eb4') else 'love_low')
    add(T_LOVE - 1.0, D - T_LOVE + 1.0, 'F1', 66, 'wind')
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


def guests(G):
    """Where the wedding guests sit (path distance), and their colours."""
    rng = np.random.default_rng(88)
    pf = at(G, 'Porch Front', 0.5)
    spots = []
    while len(spots) < NG:
        q = rng.uniform(at(G, 'Left', 0.15), at(G, 'Right', 0.85))
        if abs(q - pf) > 160 and all(abs(q - s) > 90 for s in spots):
            spots.append(q)
    return np.array(spots), rng.integers(len(KIN), size=NG)


def choreography(G):
    """Per frame: Siegmund, Sieglinde, the stranger (path distance), and each guest's pull toward the tree."""
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    S, L0 = at(G, 'Left', 0.5), at(G, 'Left', 0.03)
    s_t = np.full(F, S)
    l_t = np.full(F, L0)
    s_t[t >= 3.0] = S - 8
    l_t[t >= T_ENTER + 0.8] = at(G, 'Left', 0.36)
    s_t[t >= T_LOVE - 2] = at(G, 'Left', 0.48)
    l_t[t >= T_LOVE - 2] = at(G, 'Left', 0.4)
    sieg = follow(s_t, np.full(F, 1.5))
    linde = follow(l_t, np.where(t < 6, 1.4, 1.0))
    linde[t < T_ENTER] = L0
    w_t = np.full(F, G.length + 40)                                             # the stranger
    walk = (t >= T_STRANGER) & (t < T_SWING)
    w_t[walk] = G.length + 40 + (pf + 30 - G.length - 40) * smoothstep(T_STRANGER, T_VALHALLA, t[walk])
    w_t[(t >= T_SWING) & (t < T_LEAVE)] = pf + 30
    out = t >= T_LEAVE
    w_t[out] = pf + 30 + (G.length + 40 - pf - 30) * smoothstep(T_LEAVE, T_LEAVE + 6.5, t[out])
    spots, _ = guests(G)
    pull = np.zeros((NG, F))
    rng = np.random.default_rng(89)
    order = rng.permutation(NG)
    for k, t0 in enumerate(TRIES):
        g = order[k]
        pull[g] = np.maximum(pull[g], smoothstep(t0, t0 + 1.1, t) * (1 - smoothstep(t0 + 3.1, t0 + 3.8, t)))
    for g in range(NG):
        pull[g] = np.maximum(pull[g], 0.93 * smoothstep(T_ALL, T_ALL + 1.2, t) * (1 - smoothstep(T_ALL + 3.1, T_ALL + 4.0, t)))
    gpos = spots[:, None] + (pf - spots[:, None]) * pull * (1 - 0.08 * np.sign(pf - spots[:, None]) * 0)
    gpos += np.sign(spots - pf)[:, None] * 18 * pull                            # stop just short of the trunk
    return dict(t=t, sieg=sieg, linde=linde, wand=w_t, gpos=gpos, pull=pull)


def room(G):
    """The hut's fixed parts: the same flicker for every scene of the act, so the cuts line up."""
    rng = np.random.default_rng(606)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    hc = at(G, 'Left', 0.6)
    return dict(
        pf=pf, hc=hc, door=G.length,
        trunk=np.exp(-((d - pf) / 20) ** 2),
        canopy=np.clip(np.exp(-((d - pf) / 300) ** 2) - 0.8 * np.exp(-((d - pf) / 26) ** 2), 0, 1),
        hearth=np.exp(-((d - hc) / 120) ** 2),
        coals=np.exp(-((d - hc) / 45) ** 2),
        cast=np.exp(-np.abs(d - hc) / 700),
        storm=np.exp(-((G.length - d) / 110) ** 2),
        fl=Flicker(rng, G.N, 0.6, 2.2), fast=Flicker(rng, G.N, 2.5, 6.0), leaf=Flicker(rng, G.N, 0.1, 0.5),
        gust=Flicker(rng, G.N, 0.2, 0.9))


def draw_room(G, R, tt, bed, ember, glint, storm, trunk=TRUNK_L, leaves=LEAF_L):
    d = G.pd
    roll = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 420 - 0.03 * tt))
    fr = light(HUT, bed * (0.85 + 0.15 * roll))
    fr += light(EMBER, ember * R['hearth'] * (0.8 + 0.12 * R['fl'](tt) + 0.06 * R['fast'](tt)))
    dance = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.11 * tt) + 1.5 * np.sin(2 * np.pi * 0.07 * tt))
    fr += light(EMBER, 0.55 * ember * R['cast'] * (0.3 + 0.7 * dance) * (0.85 + 0.15 * R['fl'](tt)))
    fr += light(HOT, 0.8 * ember * R['coals'] * (0.7 + 0.2 * R['fast'](tt)))
    fr += light(TRUNK, trunk * R['trunk'])
    fr += light(LEAF, leaves * R['canopy'] * (0.85 + 0.15 * R['leaf'](tt)))
    fr += light(HILT, glint * np.exp(-((d - R['pf']) / 9) ** 2))
    fr += light(STORM, storm * R['storm'] * (0.85 + 0.15 * R['gust'](tt)))
    return fr


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    R = room(G)
    pf = R['pf']
    C = choreography(G)
    N = compose()
    spots, gcol = guests(G)
    torches = np.arange(at(G, 'Left', 0.1), at(G, 'Right', 0.95), 190.0)
    torches = torches[np.abs(torches - pf) > 120]
    tmask = np.exp(-((d[:, None] - torches[None, :]) / 22) ** 2).max(axis=1)
    linde_n = np.array([e[0] for e in N if e[4] in ('linde', 'linde_low', 'tale', 'love', 'knew') and e[1] >= 0.2])
    wsteps = np.array([e[0] for e in N if e[4] == 'wanderer'])
    strains = np.array([e[0] for e in N if e[4] == 'strain'])
    fails = np.array([e[0] for e in N if e[4] == 'thud'])
    oom = np.array([e[0] for e in N if e[4] == 'oom'])
    tw = Flicker(rng, G.N, 3.0, 7.0)
    tflick = Flicker(rng, G.N, 1.5, 5.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        feast = smoothstep(T_FEAST - 1, T_FEAST + 2, t) * (1 - smoothstep(T_KNEW, T_LOVE, t))
        awe = smoothstep(T_STRANGER + 1, T_STRANGER + 4, t) * (1 - smoothstep(T_LEAVE + 2, T_LEAVE + 6, t))
        hilt = smoothstep(T_PLUNGE - 0.02, T_PLUNGE + 0.05, t)
        glint = GLINT_IN + (GLINT_OUT - GLINT_IN) * smoothstep(T_KNEW, T_LOVE + 3, t)
        glint += hilt * 0.6 * feast
        gust = smoothstep(T_LOVE, D, t)
        fr = draw_room(G, R, tt, BED * (1 + 0.25 * feast), EMBER_L, glint, STORM_L * (1 + 0.5 * gust))

        # the feast: torches along every run, guests round the hall, a slow sway to the plodding tune
        if feast > 0:
            k = int(np.searchsorted(oom, t, side='right')) - 1
            thump = np.exp(-(t - oom[k]) / 0.25) if k >= 0 and t - oom[k] < 1 else 0.0
            fr += light(TORCH, feast * (1 - 0.35 * awe) * tmask * (0.62 + 0.12 * tflick(t) + 0.1 * thump))
            fr += light(TORCH, feast * (1 - 0.5 * awe) * 0.2 * (0.8 + 0.2 * thump) * np.ones(G.N))
            for g in range(NG):
                q = C['gpos'][g][f]
                pl = C['pull'][g][f]
                sway = 6 * np.sin(2 * np.pi * (t / (6 * FBEAT)) + g)
                ks = int(np.searchsorted(strains, t, side='right')) - 1
                tremble = (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)) if pl > 0.85 else 0.0
                b = feast * (0.6 - 0.25 * awe + 0.4 * pl + 0.2 * tremble * pl)
                w = 14 + 12 * pl
                fr += light(KIN[gcol[g]], b * np.exp(-((d - q - sway * (1 - pl)) / w) ** 2))
                if pl > 0.5:
                    trail = smoothstep(min(q, spots[g]), max(q, spots[g]), d) * \
                        smoothstep(max(q, spots[g]) + 5, max(q, spots[g]) - 5, d) * (d > min(q, spots[g]) - 5)
                    fr += light(KIN[gcol[g]], 0.18 * feast * pl * trail)
            for k, tf in enumerate(fails):                                     # thrown back
                if tf <= t < tf + 1.0:
                    a = t - tf
                    r = 25 + 300 * a ** 0.6
                    fr += light(HOT, (0.5 + 0.3 * (k == len(fails) - 1)) * (1 - a) *
                                np.exp(-((np.abs(d - pf) - r) / 35) ** 2))
            if T_ALL + 1.2 <= t < T_ALL + 3.1:                                  # the whole hall heaves
                fr += light(TORCH, 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.5 * t)) * np.exp(-((d - pf) / 500) ** 2))

        # the stranger: a blue-grey figure under a dark brim, one bright eye
        wp = C['wand'][f]
        if T_STRANGER - 0.2 <= t < T_LEAVE + 7:
            i = int(np.searchsorted(wsteps, t, side='right')) - 1
            step = np.exp(-(t - wsteps[i]) / 0.5) if i >= 0 and t - wsteps[i] < 2 else 0.0
            vis = smoothstep(T_STRANGER - 0.2, T_STRANGER + 1.0, t)
            fr *= 1 - 0.5 * vis * np.exp(-((d - wp) / 60) ** 2)[:, None]            # his shadow
            fr += light(GREY, vis * (0.7 + 0.2 * step) * np.exp(-((d - wp) / 36) ** 2))
            fr += light(GREY, vis * (0.3 + 0.1 * step) * np.exp(-((d - wp) / 170) ** 2))
            fr += light(BRIM, vis * 0.5 * np.exp(-((d - wp + 34) / 14) ** 2))
            look = smoothstep(T_VALHALLA - 0.5, T_VALHALLA + 1.0, t) * (1 - smoothstep(T_SWING - 0.6, T_SWING, t))
            eye = wp - 12
            fr += light(EYE, vis * (0.75 + 0.25 * look) * np.exp(-((d - eye) / 6) ** 2))
            if look > 0:                                                        # his eye finds her
                lp = C['linde'][f]
                beam = smoothstep(lp - 10, lp + 10, d) * smoothstep(eye + 10, eye - 10, d)
                ripple = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 120 + 0.8 * t))
                fr += light(EYE, look * 0.25 * beam * (0.6 + 0.4 * ripple))

        # the sword: a long white blade of light slams into the trunk, one flash, the hilt left blazing
        if T_SWING <= t < T_PLUNGE:
            u = smoothstep(T_SWING, T_PLUNGE, t)
            half = 900 * (1 - u) ** 1.5 + 12
            blade = smoothstep(half + 15, half - 15, np.abs(d - pf))
            fr += light(STEEL, (0.35 + 0.5 * u) * blade)
            fr += light(WHITE, 0.6 * u * np.exp(-((np.abs(d - pf) - half) / 20) ** 2))
        if T_PLUNGE <= t < T_PLUNGE + 2.0:
            a = t - T_PLUNGE
            fr += light(WHITE, 0.9 * np.exp(-a / 0.18) * np.ones(G.N))
            r = 20 + 900 * a ** 0.6
            fr += light(HILT, 0.8 * (1 - a / 2) * np.exp(-((np.abs(d - pf) - r) / 50) ** 2))
        if hilt > 0 and feast > 0:
            fr += light(HILT, hilt * feast * (0.5 * np.exp(-((d - pf) / 60) ** 2) + 0.2 * np.exp(-((d - pf) / 220) ** 2)))
            fr += light(WHITE, hilt * feast * 0.5 * np.exp(-((d - pf) / 10) ** 2) * (0.8 + 0.2 * tw(t)))

        # the two of them
        for p, col, base, arr in ((C['sieg'][f], BLUE, SIEG_L, None), (C['linde'][f], AMBER, LINDE_L, linde_n)):
            vis = 1.0 if arr is None else smoothstep(T_ENTER, T_ENTER + 0.5, t)
            flare = 0.0
            if arr is not None:
                i = int(np.searchsorted(arr, t, side='right')) - 1
                flare = np.exp(-(t - arr[i]) / 0.3) if i >= 0 and t - arr[i] < 1.2 else 0.0
            pop = 0.6 * np.exp(-(t - T_ENTER) / 0.4) if arr is not None and t >= T_ENTER else 0.0
            love = smoothstep(T_LOVE - 2, T_LOVE + 2, t)
            b = vis * base * (1 + 0.25 * flare + pop + 0.25 * love) * (0.96 + 0.04 * np.sin(2 * np.pi * tt / 4.0))
            fr += light(col, b * np.exp(-((d - p) / 26) ** 2) + 0.3 * b * np.exp(-((d - p) / 110) ** 2))
        lv = [e for e in linde_n if e >= T_LOVE]
        j = int(np.searchsorted(lv, t, side='right')) - 1
        if j >= 0 and t - lv[j] < 3.0:                                          # each note of their love, a ripple
            a = t - lv[j]
            mid = (C['sieg'][f] + C['linde'][f]) / 2
            r = 30 + 380 * a ** 0.7
            fr += light(hexc('#ffc0a0'), 0.35 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - mid) - r) / 70) ** 2))
        if t >= T_LOVE - 2:                                                     # drawing together
            a, b_ = sorted((C['sieg'][f], C['linde'][f]))
            between = smoothstep(a - 5, a + 15, d) * smoothstep(b_ + 5, b_ - 15, d)
            fr += light(hexc('#a0a8ff'), 0.3 * smoothstep(T_LOVE - 2, T_LOVE + 3, t) * between)
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
    spots, _ = guests(G)

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.22, 0.32), ('low', 0.24, 0.2), ('brass', 0.22, 0.32), ('winds', 0.22, 0.3),
                            ('perc', 0.22, 0.3), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v3_Sum.wav')

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

    rng = np.random.default_rng(89)
    order_g = rng.permutation(NG)
    tries = TRIES + [T_ALL]
    for t, d, m, v, part, who in compose():
        pl = pt('linde', t)
        if part == 'linde':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, pl)
        elif part == 'linde_low':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pl)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, -0.3, rise=1.5, fall=1.5, gain=0.7)
        elif part == 'oom':
            M.add('low', bsn.play(m + 12, v), t, 0.9, -0.1)
            M.add('low', pizz.play(m + 12, v), t, 0.8, 0.1)
        elif part == 'pah':
            M.add('winds', cl.play(m, v), t, 0.6, -0.3 + 0.6 * ((t * 7) % 1))
            M.add('strings', vcs.play(m, v - 10), t, 0.5, 0.0)
        elif part == 'tale':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pl)
            M.add('strings', vc.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, pl)
        elif part == 'wanderer':
            pw = pt('wand', t)
            s = tuba if m < note('Ab2') else tbn if m < note('Gb4') else horn
            M.add('brass', s.play(m + (12 if s is tuba and m < note('Eb2') else 0), v, dur=d * 1.02, release=0.6),
                  t, 0.5, pw)
        elif part == 'deep':
            hold('low', cb, m + 24, t, t + d, v, pf, rise=3.0, fall=1.0, gain=0.6)
        elif part == 'valhalla':
            s = tuba if m < note('Ab2') else tbn if m < note('Db4') else horn
            M.add('brass', s.play(m + (12 if m < note('Db2') else 0), v, dur=d * 1.02, release=0.6), t, 0.6,
                  pt('wand', t) + (0.15 if s is horn else 0))
        elif part == 'rush':
            M.add('fx', whoosh(d + 0.2, 300, 4000, 0.7, seed=31), t, 1.0, pf)
            hold('strings', vtrem, m + 12, t, t + d, v, pf, rise=d, fall=0.2, gain=0.5)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d, release=0.3), t, 1.0, pf)
        elif part == 'plunge':
            M.add('perc', timp.play(v, pitch=-5), t, 1.3, pf)
            M.add('perc', crash.play(v), t, 1.2, pf)
            M.add('perc', anvil.play(110), t, 0.5, pf)
            M.add('low', tuba.play(m + 12, v, dur=d, release=0.4), t, 0.8, pf)
        elif part == 'blaze':
            hold('strings', vtrem if m >= note('C4') else vatrem, m, t, t + d, v, pf, rise=0.1, fall=2.0, gain=0.5)
            if m < note('C4'):
                hold('brass', horn, m + 12, t, t + 2.5, v - 10, pf, rise=0.1, fall=1.5, gain=0.5)
        elif part == 'wander_out':
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.6), t, 0.7, pt('wand', t))
        elif part in ('run_in', 'strain', 'heave', 'fail', 'thud'):
            k = min(range(len(tries)), key=lambda i: abs(tries[i] - t + 1.5))
            pg = pf if tries[k] == T_ALL else pan_at(spots[order_g[k]])
            pa = pg + (pf - pg) * np.clip((t - tries[k]) / 1.1, 0, 1)
            if part == 'run_in':
                M.add('fx', whoosh(1.1, 400, 2500, 0.5, seed=int(t * 10)), t, 0.8, pa)
            elif part == 'strain':
                M.add('strings', vtrem.play(m + 12, v, dur=d * 1.2, release=0.1), t, 0.55, pa)
                M.add('brass', horn.play(m, v - 12, dur=d * 1.2, release=0.1), t, 0.5, pa)
            elif part == 'heave':
                hold('low', vatrem, m + 12, t, t + d, v, pa, rise=d, fall=0.2, gain=0.6)
                M.add('low', tbn.play(m + 12, v - 8, dur=d, release=0.2), t, 0.6, pa)
            elif part == 'fail':
                M.add('strings', vc.play(m - 12, v, dur=d * 1.5, release=0.05), t, 0.7, pa)
            else:
                M.add('perc', timp.play(v, pitch=-4), t, 0.9, pa)
                M.add('low', pizz.play(m + 12, v), t, 0.9, pa)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.7, pf)
        elif part == 'knew':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.6), t, 0.6, pf)
            M.add('strings', vc.play(m - 12, v - 6, dur=d * 1.05, release=0.4), t, 0.6, pl)
        elif part == 'shade':
            hold('strings', va, m, t, t + d, v, -0.4 + 0.4 * (m % 3), rise=1.5, fall=1.5, gain=0.5)
        elif part == 'love':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.4), t, 0.8, pl)
            M.add('strings', vn.play(m, v - 14, dur=d * 1.05, release=0.4), t, 0.4, pl)
        elif part == 'love_low':
            M.add('strings', (vc if m < note('C3') or m >= note('F3') else va).play(m, v - 10, dur=d * 1.02,
                  release=0.4), t, 0.6, pt('sieg', t))
        elif part == 'wind':
            hold('low', vatrem, m + 24, t, t + d, v, pan_at(G.length), rise=4.0, fall=1.0, gain=0.5)
            M.add('fx', whoosh(d, 200, 900, 0.5, seed=77), t, 0.8, pan_at(G.length))
