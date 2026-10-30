"""Siegfried Arrives: the hall of the Gibichungs, and a horn on the river. Siegfried's horn call (Donington 48)
rings out from the free end of Right, and every note of it flashes the whole riverbank emerald while the Rhine
foams white. Twice; then his boat comes up the river, an emerald comet with a white-hot head driving a wake of
teal and white foam down Right, and he leaps ashore at the hall's door.

"Heil, Siegfried!" Hagen greets him with Siegfried's own motif (53) blazing on the brass: every note an emerald
sweep run by run until the whole house is green. But under it the Curse (13) sounds in the trombones and basses,
and blood red seeps up through the green from Hagen in the shadows, out to both ends. Gunther welcomes him in with
his fanfare, gold surging over the porch, and Siegfried walks up along Porch Right into the hall to stand beside
the throne. The Curse comes again with two of Hagen's blows, a red slash and a black-violet shock; then Siegfried's
heroism (78) and Gunther's gold trade runs, friends for now, and the hall settles with the four of them in it.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD09'
TITLE = 'Siegfried Arrives'
KIND = 'show'
DESCRIPTION = ("A horn on the river, and Siegfried's boat lands at the hall. Hagen hails him by name, and under "
               'the welcome a curse seeps up blood red.')
VOICEOVER = ('A horn sounds on the Rhine. Siegfried has come to the hall of the Gibichungs, '
             'and Hagen greets him by name.')

K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
FANFARE = [('Bb2', 1.0), ('F3', 0.5), ('Bb3', 0.5), ('D4', 1.0), ('C4', 0.5), ('Bb3', 0.5), ('F3', 2.0)]
T_HORN = [1.5, 7.5]                         # his horn call from the river
T_BOAT = (12.0, 21.5)                       # the boat comes up the river; he leaps ashore
T_HEIL = 24.0                               # "Heil, Siegfried!": his motif on the brass
T_CURSE = [25.0, 52.5]                      # the Curse beneath
T_GUN = 37.0                                # Gunther's welcome
T_WALK = (40.0, 50.0)                       # he walks up into the hall
T_HAGEN = [51.0, 55.5]
T_HERO = 60.0                               # his heroism against Gunther's gold
D = 80.0

AMBER = hexc('#ff8a20')
PURPLE = hexc('#6a10c0')
TORCH = hexc('#ffb040')
HEAT = hexc('#fff0a0')
REED = hexc('#2a6a20')
RIVER = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
FOAM = hexc('#14c080')
HAGEN = hexc('#7a00ff')
SPEAR = hexc('#c8d8ff')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
POTION = hexc('#a050ff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
WHITE = hexc('#ffffff')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD08 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD10 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)
ASHORE_AT = ('Right', 0.15)                 # where he lands
SIEGFRIED_AT = ('Porch Front', 0.85)        # beside the throne
FIGS_END = dict(gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75),
                siegfried=(*SIEGFRIED_AT, 0.85))


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


RUNS = ['Left', 'Right', 'Side', 'Right', 'Left']
TORCHES = [('Left', 0.2), ('Left', 0.55), ('Left', 0.88), ('Porch Left', 0.2), ('Porch Left', 0.7),
           ('Porch Front', 0.15), ('Porch Front', 0.5), ('Porch Front', 0.85), ('Porch Right', 0.3),
           ('Porch Right', 0.8), ('Side', 0.6)]


def stage(G):
    """The hall of the Gibichungs as profiles over the house: the hall on the porch, its far walls on Left and the
    Side, torches along them, the riverbank on Right with the Rhine running past its free end."""
    d = G.pd
    rng = np.random.default_rng(1848)       # the same torches, drapes and river in every scene, so the cuts match
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    walls = np.isin(seg, ['Left', 'Side'])
    mid = at(G, 'Porch Front', 0.5)
    river = smoothstep(at(G, 'Right', 0.55), at(G, 'Right', 1.0), d)
    tp = np.array([at(G, s, u) for s, u in TORCHES])
    return dict(
        d=d, mid=mid, porch=porch, walls=walls, torch_at=tp,
        hall=porch * (0.6 + 0.4 * np.exp(-((d - mid) / 200) ** 2)) + walls * (0.45 + 0.2 * smooth_noise(rng, d, 50.0)),
        drape=(porch | walls) * (0.5 + 0.5 * np.sin(2 * np.pi * d / 140)) ** 2,
        torch=np.exp(-((d[None, :] - tp[:, None]) / 9) ** 2).sum(0),
        glow=np.exp(-((d[None, :] - tp[:, None]) / 45) ** 2).sum(0),
        bank=(seg == 'Right') * (1 - river) * (0.7 + 0.3 * smooth_noise(rng, d, 30.0)),
        river=river,
        fl=Flicker(rng, G.N, 3.0, 9.0),
        sway=Flicker(rng, G.N, 0.2, 0.7),
    )


def hall(S, T, lv):
    """The hall at shared time T with levels lv (hall, drapes, torches, bank, river, gloom)."""
    d, fl = S['d'], S['fl'](T)
    fr = light(AMBER, lv['hall'] * S['hall'] * (0.85 + 0.15 * fl))
    fr += light(PURPLE, lv['drapes'] * S['drape'] * (0.85 + 0.15 * S['sway'](T)))
    fr += light(TORCH, lv['torches'] * np.clip(S['torch'], 0, 1) * (0.75 + 0.25 * fl))
    fr += light(AMBER, 0.6 * lv['torches'] * np.clip(S['glow'], 0, 1) * (0.8 + 0.2 * fl))
    fr += light(REED, lv['bank'] * S['bank'])
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 90 - 0.55 * T)) * np.sin(2 * np.pi * (d / 230 - 0.2 * T) + 1.0)
    fr += light(RIVER + (TEAL - RIVER) * u[:, None], lv['river'] * S['river'])
    fr += light(FOAM, lv['river'] * S['river'] * np.clip(u - 0.75, 0, None) * 3)
    return fr * (1 - lv['gloom'])


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the hall, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def wave(S, p, a, speed=1200.0, width=90.0, life=0.9):
    """A ring running out both ways from p, a seconds after it starts -> perceptual."""
    return np.exp(-a / life) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2) * (a >= 0)


def blow(fr, S, p, a, s=1.0):
    """Hagen's blow, a seconds after it lands at p: the house knocked dark and a black-violet shock out from him."""
    if not 0 <= a < 2.5:
        return fr
    fr = fr * (1 - 0.9 * s * np.exp(-a / 0.9))
    fr = fr + light(HAGEN, 0.5 * s * np.exp(-a / 0.35))
    fr = fr + light(HAGEN, s * wave(S, p, a, 1100.0, 230.0, 1.2))
    fr = fr + light(SPEAR, 0.9 * s * np.exp(-a / 0.12) * np.exp(-((S['d'] - p + 18) / 8) ** 2))
    return fr


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'Bb1', 58, 'pedal')
    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, 0.42, 0, 100 + 8 * k):
            add(t, d, m, v, 'horn', k)
    add(T_BOAT[0], T_BOAT[1] - T_BOAT[0], 'F2', 76, 'river')
    add(T_BOAT[1], 0.3, 'C1', 118, 'ashore')
    for t, m, v, d in play('siegfried', T_HEIL, 0.6, -12, 118):
        add(t, d, m, v, 'heil')
    for k, t0 in enumerate(T_CURSE):
        for t, m, v, d in play('curse', t0, 0.62, -12, 104 + 8 * k):
            add(t, d, m, v, 'curse', k)
    t = T_GUN
    for m, b in FANFARE:
        add(t, b * BEAT * 1.05, m, 108, 'fanfare')
        t += b * BEAT
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.7, 0, 118):
            add(t, d, m, v, 'hagen', k)
    for t, m, v, d in play('siegfried_heroism', T_HERO, 0.45, 12, 104):
        add(t, d, m, v, 'hero')
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """Siegfried's place at time t: up the river, ashore, then up into the hall."""
    L = G.pd.max()
    shore, home = at(G, *ASHORE_AT), at(G, *SIEGFRIED_AT)
    if t < T_BOAT[1]:
        return L + 40 + (shore - L - 40) * smoothstep(T_BOAT[0], T_BOAT[1], t) ** 0.8
    return shore + (home - shore) * smoothstep(*T_WALK, t)


def render(G, seed=9):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    horn = [e for e in N if e[4] == 'horn']
    heil = [e for e in N if e[4] == 'heil']
    curse = [e for e in N if e[4] == 'curse']
    fan = [e for e in N if e[4] == 'fanfare']
    hag = [e for e in N if e[4] == 'hagen']
    hero = [e for e in N if e[4] == 'hero']
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    right = G.seg_of == 'Right'
    runs = ['Right', 'Porch Right', 'Porch Front', 'Porch Left', 'Left', 'Side']
    foam = Flicker(np.random.default_rng(seed), G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['river'] += 0.3 * smoothstep(0, 2, t) * (1 - smoothstep(T_BOAT[1], T_BOAT[1] + 4, t))
        fr = hall(S, T, lv)
        p = where(G, t)

        # the horn call: every note flashes the whole riverbank emerald and foams the river
        for t0, dur, m, v, part, k in horn:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SIEGFRIED, 0.85 * np.exp(-a / 0.3) * right)
                fr += light(WHITE, 0.5 * np.exp(-a / 0.2) * S['river'] * np.clip(foam(T), 0, 1))
                fr += light(SIEGFRIED, 0.7 * wave(S, L, a, 1400.0, 150.0, 0.7))

        # the boat: an emerald comet up the river with a wake of teal and white foam behind it
        if T_BOAT[0] - 0.5 <= t < T_BOAT[1] + 0.5:
            wake = (d > p) * np.exp(-(d - p) / 260) * right
            fr += light(TEAL, 0.9 * wake)
            fr += light(WHITE, 0.7 * wake * np.clip(foam(T) - 0.3, 0, 1))
        if T_BOAT[1] <= t < T_BOAT[1] + 1.5:
            a = t - T_BOAT[1]
            fr += light(HEAD, min(1.0, 1.3 * np.exp(-a / 0.15)) * np.exp(-((d - p) / 30) ** 2))
            fr += light(SIEGFRIED, wave(S, p, a, 1600.0, 130.0, 0.6))

        # "Heil, Siegfried!": each note of his motif sweeps one more run emerald until the house is green
        for i, (t0, dur, m, v, part, k) in enumerate(heil):
            a = t - t0
            if 0 <= a < 6.0:
                run = G.seg_of == runs[i % len(runs)]
                fr += light(SIEGFRIED, (0.95 * np.exp(-a / 0.5) + 0.6 * (1 - smoothstep(3.0, 6.0, a))) * run)
                fr += light(HEAD, 0.6 * np.exp(-a / 0.15) * run)

        # the Curse beneath: blood red seeping up through everything from Hagen, out to both ends
        for t0, dur, m, v, part, k in curse:
            a = t - t0
            if 0 <= a < dur + 2.5:
                reach = min(1.0, a / 2.0) * L
                seep = smoothstep(reach + 80, reach - 80, np.abs(d - p_hag))
                g = (0.55 + 0.25 * k) * np.exp(-max(a - dur, 0) / 1.0) * smoothstep(0, 0.2, a)
                fr += light(BLOOD, g * seep * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 160 - 0.8 * t))))

        # Gunther's welcome: gold surges over the porch and out
        for t0, dur, m, v, part, k in fan:
            a = t - t0
            if 0 <= a < 1.4:
                fr += light(GUNTHER, 0.85 * np.exp(-a / 0.35) * S['porch'])
                fr += light(GUNTHER, wave(S, p_gun, a, 1300.0, 200.0, 0.8))

        # his heroism against Gunther's gold: whole runs trading emerald and gold note by note
        for i, (t0, dur, m, v, part, k) in enumerate(hero):
            a = t - t0
            if 0 <= a < 3.0:
                run = G.seg_of == runs[(2 * i + 1) % len(runs)]
                col = SIEGFRIED if i % 2 == 0 else GUNTHER
                fr = fr * (1 - 0.5 * np.exp(-a / 0.6) * run)[:, None]
                fr += light(col, 1.0 * np.exp(-a / 0.9) * run * (1 - smoothstep(D - 5, D - 1, t)))
                fr += light(col, 0.8 * wave(S, p, a, 1200.0, 160.0, 0.8) * (1 - smoothstep(D - 5, D - 1, t)))

        # the four of them
        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        if t >= T_BOAT[0] - 0.5:
            lvl = 0.85 * smoothstep(T_BOAT[0] - 0.5, T_BOAT[0] + 0.5, t)
            fr = figure(fr, S, p, SIEGFRIED, lvl)
            fr += light(HEAD, 0.8 * lvl * np.exp(-((d - p) / 6) ** 2))
        for t0, dur, m, v, part, k in hag:
            fr = blow(fr, S, p_hag, t - t0, 1.0 if m < note('C3') else 0.6)
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

    for name, gain, rev in (('low', 0.36, 0.25), ('brass', 0.34, 0.3), ('strings', 0.3, 0.35), ('perc', 0.32, 0.3),
                            ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
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

    gun, hag = pan_at(at(G, *GUNTHER_AT)), pan_at(at(G, *HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        here = pan_at(where(G, t))
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.5)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.4), t, 0.9, river)
        elif part == 'river':
            hold('strings', ctrem, m + 12, t, t + d, v, river, rise=1.0, fall=1.5, gain=0.6)
            hold('strings', vtrem, m + 24, t, t + d, v - 10, river, rise=1.0, fall=1.5, gain=0.4)
        elif part == 'ashore':
            M.add('perc', timp.play(v, pitch=-4), t, 0.9, here)
            M.add('perc', crash.play(100), t, 0.6, here)
            M.add('fx', whoosh(0.8, 600, 3000, 0.7, seed=9), t - 0.5, 0.9, here)
        elif part == 'heil':
            if d > 0.5:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.08, fall=0.5, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9)
            M.add('brass', tpt.play(m, v - 14, dur=d * 1.05, release=0.25), t, 0.55)
            if t == T_HEIL:
                M.add('perc', crash.play(118), t, 0.8)
                M.add('perc', timp.play(118, pitch=-5), t, 0.9)
        elif part == 'curse':
            if d > 1.2:
                hold('low', tbn, m, t, t + d, v, hag, rise=0.15, fall=1.0, gain=0.8)
            else:
                M.add('low', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, hag)
            M.add('low', tuba.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, hag)
        elif part == 'fanfare':
            M.add('brass', tbn.play(m, v, dur=d, release=0.25), t, 0.95, gun)
            if m < note('C3'):
                M.add('perc', timp.play(v, pitch=-2), t, 0.7, gun)
        elif part == 'hagen':
            M.add('low', tuba.play(m - 12, v, dur=d * 1.2, release=0.4), t, 1.0, hag)
            M.add('low', tbn.play(m, v - 10, dur=d * 1.2, release=0.4), t, 0.7, hag)
            M.add('perc', timp.play(v, pitch=-7 if m < note('C3') else -3), t, 0.9, hag)
            if m < note('C3'):
                M.add('perc', gong.play(96), t, 0.5, hag)
        elif part == 'hero':
            M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.85, here)
            M.add('low', tbn.play(m - 24, v - 16, dur=d * 1.05, release=0.3), t, 0.5, gun)
