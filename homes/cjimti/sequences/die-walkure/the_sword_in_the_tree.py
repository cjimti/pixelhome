"""The Sword in the Tree: Sieglinde (hearth amber) slips back in through the inner door at the corner of Left,
Hunding drugged asleep behind her, and tells Siegmund of her wedding feast. The story takes the house: torches flare
along every run and the guests are small warm lights all over the roof. A stranger came in, an old man in grey, his
hat pulled down over one eye: a blue-grey figure under a dark brim with a single bright eye, walking in from the door
at the free end of Right while the violins climb in C major. His eye finds her; he swings a sword and, on the
orchestra's great C major fanfare, drives it into the ash to the hilt: a long white blade of light slams into the
trunk with one flash over the house, and the hilt is left blazing gold. "Bis zum Heft haftet' es drin."

He walks out the way he came. Then, as her music surges up in rising sequences, the guests try their strength one
after another: each light rushes to the tree and strains at the hilt, swelling and trembling as the strings climb,
and is thrown back; the last time, on a scale rushing up two octaves, all of them heave together and fail as it
plunges down. The torches fade into the dark hut, and her longing takes the house instead: "O fänd' ich ihn hier und
heut, den Freund!" Every phrase of it flares from her and ripples out across the roof. On "umfing' den Helden mein
Arm!" the two lights draw together, the orchestra's climax bursts in waves of amber and blue over the whole house,
and Siegmund answers her, "Dich selige Frau hält nun der Freund", as the wind starts to press at the door.

The music is Wagner's own: Act I, bars 992-1000 and 1024-1060, as Solti's 1958 Vienna Philharmonic recording takes
them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py). The Sword's arpeggios in the left hand are
the trumpets over trombones and tuba; the guests' strain is violins with horns; her lines are violins and oboe; the
rest is the reduction orchestrated by hand and register, the full orchestra at the climax. The stage adds its
sounds: the feast's torches crackling all over the house, the stranger's footsteps coming in and going out, his
sword whistling through the air and slamming into the trunk with a ringing steel blow, each guest's strain grinding
at the hilt and the thud and rattle as he is thrown back, the great heave all together, the hearth, and the wind
starting to press at the door. The effects lead through the tale: the torches, the stranger, his blow, the
guests' struggle; then they back well off for her longing and the love music so it sings out, and only the wind
at the door creeps back under Siegmund's answer.

compose() tags every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK08'
TITLE = 'The Sword in the Tree'
KIND = 'show'
DESCRIPTION = ('Sieglinde tells of her wedding feast, when a stranger in grey with one eye hidden under his hat '
               'drove a sword into the ash tree up to the hilt. Every man in the hall tried to pull it out, and '
               'every one of them failed.')
VOICEOVER = ('Sieglinde has a secret to tell. On her wedding day, a stranger left something in that tree, '
             'and nobody has been strong enough to take it out.')

EX = excerpt(__file__)                      # Act I, bars 992-1000 and 1024-1060, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
K = 7                                       # this scene's place in the shared clock (t + 80 * K)
T_ENTER = 0.3                               # she comes back in through the inner door
T_FEAST = 0.0                               # the wedding feast
T_STRANGER = 0.0                            # the stranger comes in at the door
T_VALHALLA = BAR[995]                       # his eye finds her
T_PLUNGE = BAR[998]                         # the fanfare: into the ash, to the hilt
T_SWING = T_PLUNGE - 1.2
T_LEAVE = BAR[998] + 2.0
TRIES = [BAR[1025], BAR[1027], BAR[1029]]   # one by one they try, on the rising sequences
T_ALL = BAR[1033] - 3.1                     # all together, on the scale rushing up, thrown back as it falls
T_KNEW = BAR[1033]                          # her longing
T_LOVE = BAR[1050]                          # "umfing' den Helden mein Arm!": they draw together
T_CLIMAX = BAR[1054]
T_HIM = BAR[1056]                           # "Dich selige Frau hält nun der Freund"
D = EX['seconds']

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). Before the guests try: the
    right hand is 'tale', the left hand's long notes the Sword ('sword', or 'oom' in the bass); while they try,
    'strain' and 'heave'; then 'linde' (her lines, the right hand) and 'love_low', with 'climax' for the left hand's
    chords at the climax; everything else is 'note'."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < TRIES[0]:
            part = 'tale' if h == 0 else ('sword' if m >= 48 else 'oom') if d >= 0.3 else 'note'
        elif t < T_KNEW:
            part = 'strain' if h == 0 else 'heave'
        elif h == 0:
            part = 'linde'
        else:
            part = 'climax' if T_CLIMAX <= t < T_HIM else 'love_low'
        N.append((t, d, m, v, part, h))
    return N


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
    s_t[t >= T_LOVE - 1] = at(G, 'Left', 0.47)
    l_t[t >= T_LOVE - 1] = at(G, 'Left', 0.41)
    sieg = follow(s_t, np.full(F, 1.5))
    linde = follow(l_t, np.where(t < 6, 1.4, 1.0))
    linde[t < T_ENTER] = L0
    w_t = np.full(F, G.length + 40)                                             # the stranger
    walk = (t >= T_STRANGER) & (t < T_SWING)
    w_t[walk] = G.length + 40 + (pf + 30 - G.length - 40) * smoothstep(T_STRANGER, T_VALHALLA + 1.5, t[walk])
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
    linde_n = np.array([e[0] for e in N if e[4] in ('tale', 'linde') and e[1] >= 0.2])
    linde_v = np.array([e[3] for e in N if e[4] in ('tale', 'linde') and e[1] >= 0.2])
    wsteps = np.array([e[0] for e in N if e[4] in ('sword', 'oom') and e[0] < T_LEAVE + 6])
    fails = np.array([t0 + 3.1 for t0 in TRIES + [T_ALL]])
    oom = np.array([e[0] for e in N if e[4] in ('sword', 'oom', 'heave') and e[1] >= 0.3])
    climax = np.array([e[0] for e in N if e[4] == 'climax'])
    tw = Flicker(rng, G.N, 3.0, 7.0)
    tflick = Flicker(rng, G.N, 1.5, 5.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        feast = smoothstep(T_FEAST, T_FEAST + 2.5, t) * (1 - smoothstep(T_KNEW, T_KNEW + 5, t))
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
                sway = 6 * np.sin(2 * np.pi * (t / 2.0) + g)
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
        j = int(np.searchsorted(linde_n, t, side='right')) - 1
        for jj in range(max(0, j - 4), j + 1):                                  # her longing: ripples from her
            if t < T_KNEW or jj < 0 or linde_n[jj] < T_KNEW or t - linde_n[jj] >= 3.0:
                continue
            a = t - linde_n[jj]
            src = C['linde'][f] if t < T_LOVE else (C['sieg'][f] + C['linde'][f]) / 2
            r = 30 + 750 * a ** 0.8
            amp = 0.7 * min(1.0, (linde_v[jj] / 85) ** 2)
            fr += light(AMBER if t < T_LOVE else hexc('#ffc0a0'),
                        amp * np.exp(-a / 1.3) * np.exp(-((np.abs(d - src) - r) / 110) ** 2))
            fr += light(HILT, 0.6 * amp * np.exp(-a / 0.4) * np.exp(-((d - pf) / 70) ** 2))     # the hilt answers
        j = int(np.searchsorted(climax, t, side='right')) - 1
        if j >= 0 and t - climax[j] < 2.0:                                      # the climax: waves over the house
            a = t - climax[j]
            mid = (C['sieg'][f] + C['linde'][f]) / 2
            r = 30 + 1100 * a ** 0.8
            for col, off in ((AMBER, 0), (BLUE, 120)):
                fr += light(col, 0.9 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - mid) - r + off) / 110) ** 2))
        if t >= T_LOVE - 2:                                                     # drawing together
            a, b_ = sorted((C['sieg'][f], C['linde'][f]))
            between = smoothstep(a - 5, a + 15, d) * smoothstep(b_ + 5, b_ - 15, d)
            fr += light(hexc('#a0a8ff'), 0.3 * smoothstep(T_LOVE - 2, T_LOVE + 3, t) * between)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction: the Sword on the trumpets over trombones and tuba, the guests' strain
    on violins and horns, her lines on violins and oboe, the full orchestra at the climax."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=2.7)

    def pt(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    def size(t):
        if t < TRIES[0]:
            return 0.6
        if t < T_KNEW:
            return 0.85
        if BAR[1043] <= t < BAR[1048]:
            return 0.35
        return 1.0 if T_CLIMAX <= t < T_HIM else 0.7

    for t, d, m, v, part, h in compose():
        if part == 'sword':
            o.play('trumpets', m, t, d, v + 6, pf, 0.7)
            o.play('horns', m - 12, t, d, v - 4, pf, 0.45)
        elif part == 'oom':
            o.play('trombones', m + 12, t, d, v, pf, 0.6)
            o.play('tuba', m, t, d, v - 4, pf, 0.5)
            o.play('basses', m, t, d, v - 8, pf, 0.4)
        elif part == 'strain':
            o.tutti([(t, d, m, v, h)], size=size)
            if d >= 0.25:
                o.play('horns', m - 12, t, d, v - 10, pf, 0.4)
        elif part == 'linde':
            o.tutti([(t, d, m, v, h)], size=size, pan=lambda t, m: pt('linde', t))
            if d >= 0.4:
                o.play('oboes', m, t, d, v - 12, pt('linde', t), 0.35)
        elif part == 'climax':
            o.tutti([(t, d, m, v, h)], size=size)
            o.play('trombones', m, t, d, v - 6, 0.0, 0.45)
        else:
            o.tutti([(t, d, m, v, h)], size=size)
    o.hit('crash', T_PLUNGE, 115, gain=0.6, pan=pf)
    o.hit('timpani', T_PLUNGE, 115, pitch=-5, gain=0.7, pan=pf)
    # the stage: torches, footsteps, the blow, the tries, the wind at the door
    from pixelhome.audio import whoosh
    torches = lambda tt: 0.3 * (1 - smoothstep(T_ALL + 3.5, T_KNEW + 4.0, tt))
    for k, pp in enumerate((-0.65, 0.0, 0.65)):
        o.fire(0.0, T_KNEW + 4.5, torches, pan=pp, crackle=6, seed=30 + k)
    o.fire(0.0, D, 0.15, pan=pan_at(at(G, 'Left', 0.6)), crackle=5, seed=40)
    for a, b in ((T_STRANGER + 0.3, T_SWING - 0.3), (T_LEAVE + 0.3, T_LEAVE + 6.5)):
        ts = a
        while ts < b:
            o.M.add('fx', o.hits['hoof soft'].play(72), ts, 0.2, pt('wand', ts))
            ts += 0.75
    M.add('fx', whoosh(1.2, 500, 6000, 0.8, seed=81), T_PLUNGE - 1.15, 0.9, pf)
    o.clash(T_PLUNGE, pf, 127, gain=1.1)
    o.boom(T_PLUNGE, pf, gain=0.8)
    o.hit('gong scrape', T_PLUNGE + 0.1, 105, gain=0.5, pan=pf, fx=True)
    for k, tf in enumerate(TRIES + [T_ALL]):
        big = tf == T_ALL
        o.hit('scrape', tf + 1.0, 100 if big else 85, gain=0.6 if big else 0.4, pan=pf, fx=True)
        o.hit('bass drum', tf + 3.1, 120 if big else 100, gain=0.8 if big else 0.5, pan=pf, fx=True)
        o.clash(tf + 3.1, pf, 115 if big else 95, gain=0.7 if big else 0.4)
        if big:
            o.boom(tf + 3.1, pf, gain=0.6)
    o.hit('cymbal swell', T_CLIMAX - 2.0, 95, gain=0.4)
    o.effects([(0, 0), (T_PLUNGE - 1.5, 0), (T_PLUNGE - 1.1, 2), (T_PLUNGE + 2.0, 2), (T_PLUNGE + 3.0, 0),
               (T_ALL + 4.0, 0), (T_KNEW + 1.0, -10), (T_LOVE, -12), (T_HIM, -12), (D, -4)])
    o.wind(T_HIM - 1.0, D, lambda tt: 0.2 + 0.7 * smoothstep(T_HIM - 1.0, D, tt), pan=pan_at(G.length))
    for k, tf in enumerate(TRIES + [T_ALL]):                # thrown back
        o.hit('timpani', tf + 3.1, 100 + 8 * (tf == T_ALL), pitch=-4, gain=0.5)
    o.hit('crash', T_ALL + 3.1, 100, gain=0.4, pan=pf)
    o.hit('crash', BAR[1055], 115, gain=0.5)
    o.hit('timpani roll', T_CLIMAX, 100, gain=0.4)
