"""Blood Brotherhood: the hall of the Gibichungs, Gutrune at Siegfried's side. Gunther tells of the bride he
wants, asleep on a rock behind a wall of fire, and Loge's fire (Donington 20) licks once round the whole house in
tongues of orange: Siegfried, who no longer remembers her, offers to fetch her for him.

Gunther comes down from his throne to stand with him. Each cuts his arm, two blood red flashes, and their blood
runs out along the roofline to both ends and back into the drinking horn between them. Then the oath (42) on the
brass: every note strikes a whole run, emerald for Siegfried and gold for Gunther, round the house, with rings
out from the two of them, and its second form (42a) answers in great falling octaves, run against run. Under it
the conspiracy (75) creeps in the bass, a slow seep of black and violet from Hagen in the shadows. They drink: a
white flash in the horn, and the three colours burst out together. Hagen will not drink; his tritone lands, the
hall knocked dark.

Siegfried's horn call (48) rings out and the two of them go down to the river, along Porch Right and Right, and
are gone up the Rhine in a wake of teal and white, leaving Gutrune in the hall and Hagen in the shadows.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD11'
TITLE = 'Blood Brotherhood'
KIND = 'show'
DESCRIPTION = ('Siegfried and Gunther cut their arms, mix their blood in a horn and swear brotherhood, emerald and '
               'gold across the house. Hagen refuses to drink, and the two of them sail off for the fire rock.')
VOICEOVER = ('Siegfried and Gunther mix their blood and swear to be brothers. '
             'Hagen will not drink.')

K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_LOGE = [1.5, 4.5]                         # the bride behind the fire
T_COME = (7.0, 11.0)                        # Gunther comes down to him
T_CUT = [12.5, 14.0]                        # Siegfried's arm, then Gunther's
T_OATH = [18.0, 24.5]                       # the oath, emerald then gold
OBEAT = 0.75
T_OATHB = [31.0, 39.5]                      # its second form, run against run
T_PLOT = [19.0, 41.0]                       # the conspiracy beneath
T_DRINK = 48.0
T_HAGEN = [51.0, 54.0]
T_HORN = 58.0
T_GO = (60.5, 66.0)                         # down to the river
T_BOAT = (66.0, 73.5)                       # up the Rhine and gone
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
ORANGE = hexc('#ff5000')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD10 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD12 picks it up
GUNTHER_FROM = ('Porch Front', 0.62)
GUNTHER_AT = ('Porch Front', 0.7)           # beside Siegfried for the oath
GUTRUNE_FROM = ('Porch Front', 0.75)
GUTRUNE_AT = ('Porch Front', 0.5)           # steps back for the oath, and stays
HAGEN_AT = ('Porch Left', 0.35)
SIEGFRIED_AT = ('Porch Front', 0.85)
HORN_AT = ('Porch Front', 0.775)            # the drinking horn between them
FIGS_END = dict(gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75))


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

    add(0.0, D, 'Bb1', 56, 'pedal')
    for k, t0 in enumerate(T_LOGE):
        for t, m, v, d in play('loge', t0, 0.22, 12, 92):
            add(t, d, m, v, 'loge', k)
    for k, t0 in enumerate(T_CUT):
        add(t0, 0.4, 'G2', 112, 'cut', k)
    for k, t0 in enumerate(T_OATH):
        for t, m, v, d in play('oath', t0, OBEAT, -12, 108 + 6 * k):
            add(t, d, m, v, 'oath', k)
    for k, t0 in enumerate(T_OATHB):
        for t, m, v, d in play('oath_b', t0, 0.62, -12, 110 + 6 * k):
            add(t, d, m, v, 'oathb', k)
    for k, t0 in enumerate(T_PLOT):
        for t, m, v, d in play('plot', t0, 0.62, -24, 88):
            add(t, d, m, v, 'plot', k)
    add(T_DRINK, 0.3, 'Bb1', 120, 'drink')
    for m in ('Bb2', 'D3', 'F3', 'Bb3', 'D4'):
        add(T_DRINK, 3.0, m, 98, 'chord')
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.7, 0, 118):
            add(t, d, m, v, 'hagen', k)
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.42, 0, 108):
        add(t, d, m, v, 'horn', 0)
    for t, m, v, d in play('siegfried_horn', T_BOAT[0] + 1.5, 0.5, 0, 80):
        add(t, d, m, v, 'horn', 1)
    add(T_BOAT[0], T_BOAT[1] - T_BOAT[0] + 2, 'F2', 74, 'river')
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """Siegfried and Gunther: by the throne, then down Porch Right and Right to the river and away up it."""
    L = G.pd.max()
    sf, gun0, gun1 = at(G, *SIEGFRIED_AT), at(G, *GUNTHER_FROM), at(G, *GUNTHER_AT)
    shore = at(G, 'Right', 0.55)
    gun = gun0 + (gun1 - gun0) * smoothstep(*T_COME, t)
    go = smoothstep(*T_GO, t)
    sf, gun = sf + (shore - sf) * go, gun + (shore - 25 - gun) * go
    up = smoothstep(*T_BOAT, t) ** 1.3
    return sf + (L + 60 - shore) * up, gun + (L + 60 - shore) * up


def render(G, seed=11):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    loge = [e for e in N if e[4] == 'loge']
    oath = [e for e in N if e[4] == 'oath']
    oathb = [e for e in N if e[4] == 'oathb']
    plot = [e for e in N if e[4] == 'plot']
    horn = [e for e in N if e[4] == 'horn']
    hag = [e for e in N if e[4] == 'hagen']
    p_hag, p_horn = at(G, *HAGEN_AT), at(G, *HORN_AT)
    g0, g1 = at(G, *GUTRUNE_FROM), at(G, *GUTRUNE_AT)
    runs = ['Porch Front', 'Right', 'Porch Left', 'Left', 'Porch Right', 'Side']
    right = G.seg_of == 'Right'
    foam = Flicker(np.random.default_rng(seed), G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['river'] += 0.3 * smoothstep(T_BOAT[0] - 2, T_BOAT[0], t) * (1 - smoothstep(T_BOAT[1], D - 1, t))
        fr = hall(S, T, lv)
        p_sf, p_gun = where(G, t)
        p_gut = g0 + (g1 - g0) * smoothstep(*T_COME, t)

        # the bride behind the fire: tongues of Loge's fire licking round the whole house
        for t0, dur, m, v, part, k in loge:
            a = t - t0
            if 0 <= a < 1.2:
                u = float(np.clip((m - 58) / 14, 0, 1))
                c = L * (0.05 + 0.9 * u) if k == 0 else L * (0.95 - 0.9 * u)
                tongue = np.exp(-((d - c) / (90 + 140 * a)) ** 2) * np.exp(-a / 0.45)
                fr += light(ORANGE, 0.95 * tongue)
                fr += light(TORCH, 0.8 * tongue * np.exp(-a / 0.15))

        # Gunther comes down from the throne: two gold surges out over the house
        for j in range(2):
            a = t - T_COME[0] - 2.0 * j
            if 0 <= a < 1.6:
                fr += light(GUNTHER, 0.85 * wave(S, p_gun, a, 1200.0, 200.0, 0.8))
                fr += light(GUNTHER, 0.5 * np.exp(-a / 0.3) * S['porch'])

        # the cuts: a red flash at each arm, and the blood runs out to both ends and back into the horn
        for k, t0 in enumerate(T_CUT):
            a = t - t0
            p = p_sf if k == 0 else p_gun
            if 0 <= a < 0.6:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.08) * np.exp(-((d - p) / 12) ** 2))
            if 0 <= a < 5.0:
                r = L * (a / 1.6 if a < 1.6 else max(0.0, 1 - (a - 1.6) / 1.8))
                g = np.exp(-max(a - 3.4, 0) / 0.5)
                fr += light(BLOOD, g * np.exp(-((np.abs(d - p) - r) / 70) ** 2))
                fr += light(BLOOD, 0.45 * g * smoothstep(r + 40, r - 40, np.abs(d - p)) * (a < 1.6))
        bowl = smoothstep(T_CUT[1] + 3.0, T_CUT[1] + 4.0, t) * (1 - smoothstep(T_DRINK, T_DRINK + 0.5, t))
        fr += light(BLOOD, 0.8 * bowl * np.exp(-((d - p_horn) / 9) ** 2))

        # the oath: every note strikes a whole run, emerald then gold, rings out from the two of them
        for i, (t0, dur, m, v, part, k) in enumerate(oath):
            a = t - t0
            if 0 <= a < 2.0:
                run = G.seg_of == runs[i % len(runs)]
                col = SIEGFRIED if k == 0 else GUNTHER
                fr = fr * (1 - 0.6 * np.exp(-a / 0.5) * run)[:, None]
                fr += light(col, np.exp(-a / (0.3 + dur)) * run)
                fr += light(HEAD if k == 0 else HEAT, 0.6 * np.exp(-a / 0.1) * run)
                fr += light(col, 0.8 * wave(S, p_sf if k == 0 else p_gun, a, 1500.0, 130.0, 0.7))
        # its second form: great falling octaves, emerald runs against gold runs
        for i, (t0, dur, m, v, part, k) in enumerate(oathb):
            a = t - t0
            if 0 <= a < 2.5:
                hiq = m >= note('C4') - 12
                rs = ['Left', 'Side', 'Porch Left'] if hiq else ['Right', 'Porch Right', 'Porch Front']
                run = np.isin(G.seg_of, rs)
                col = SIEGFRIED if (i + k) % 2 == 0 else GUNTHER
                fr = fr * (1 - 0.55 * np.exp(-a / 0.6) * run)[:, None]
                fr += light(col, 1.0 * np.exp(-a / (0.4 + 0.6 * dur)) * run)
                fr += light(WHITE, 0.5 * np.exp(-a / 0.08) * run)

        # the conspiracy beneath: a slow seep of black and violet out from Hagen
        for t0, dur, m, v, part, k in plot:
            a = t - t0
            if 0 <= a < dur + 2.0:
                reach = min(1.0, a / 3.0) * 900
                seep = smoothstep(reach + 120, reach - 120, np.abs(d - p_hag)) * np.exp(-max(a - dur, 0) / 0.8)
                fr = fr * (1 - 0.45 * seep)[:, None]
                fr += light(HAGEN, 0.55 * seep * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 150 + 0.5 * t))))

        # they drink: a white flash in the horn and the three colours burst out together
        if T_DRINK <= t < T_DRINK + 4.0:
            a = t - T_DRINK
            fr += light(WHITE, min(1.0, 1.2 * np.exp(-a / 0.12)) * np.exp(-((d - p_horn) / 40) ** 2))
            fr += light(HEAT, 0.6 * np.exp(-a / 0.15))
            for j, col in enumerate((SIEGFRIED, GUNTHER, BLOOD)):
                b = a - 0.3 * j
                if b > 0:
                    r = 650 * b
                    fr += light(col, 0.95 * np.exp(-b / 2.2) * smoothstep(r + 60, r - 200, np.abs(d - p_horn))
                                * smoothstep(r - 520, r - 220, np.abs(d - p_horn)))

        # the horn call, and the boat up the Rhine with its wake
        for t0, dur, m, v, part, k in horn:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SIEGFRIED, (0.85 - 0.3 * k) * np.exp(-a / 0.3) * right)
                fr += light(SIEGFRIED, (0.7 - 0.3 * k) * wave(S, p_sf, a, 1400.0, 150.0, 0.7))
        if T_BOAT[0] - 0.5 <= t < T_BOAT[1] + 1.5:
            fade = 1 - smoothstep(T_BOAT[1], T_BOAT[1] + 1.5, t)
            wake = (d < p_sf) * (d > at(G, 'Right', 0.5)) * np.exp(-(p_sf - d) / 240) * right * fade
            fr += light(TEAL, 0.9 * wake)
            fr += light(WHITE, 0.7 * wake * np.clip(foam(T) - 0.3, 0, 1))

        # left behind: Gutrune's rose rolls out once over the empty hall
        if T_BOAT[1] <= t < D:
            a = t - T_BOAT[1] - 0.5
            fr += light(GUTRUNE, 0.6 * wave(S, p_gut, a, 900.0, 160.0, 1.4) * (1 - smoothstep(D - 2.5, D - 0.5, t)))

        # the people
        gone = 1 - smoothstep(T_BOAT[1] - 2.0, T_BOAT[1], t)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        if gone > 0:
            fr = figure(fr, S, p_gun, GUNTHER, 0.8 * gone)
            fr = figure(fr, S, p_sf, SIEGFRIED, 0.85 * gone)
            fr += light(HEAD, 0.8 * 0.85 * gone * np.exp(-((d - p_sf) / 6) ** 2))
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

    for name, gain, rev in (('low', 0.34, 0.25), ('brass', 0.32, 0.3), ('strings', 0.28, 0.35), ('winds', 0.26, 0.35),
                            ('perc', 0.32, 0.3), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    picc = M.sampler('Woodwinds/Piccolo/Sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
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

    hag = pan_at(at(G, *HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))
    sfp = pan_at(at(G, *SIEGFRIED_AT))
    gunp = pan_at(at(G, *GUNTHER_AT))
    for t, d, m, v, part, k in compose():
        here = pan_at(where(G, t)[0])
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.5)
        elif part == 'loge':
            M.add('winds', picc.play(m, v - 10, dur=d * 1.2, release=0.15), t, 0.6, -0.6 + 1.2 * k)
            M.add('strings', vln.play(m - 12, v), t, 0.6, -0.6 + 1.2 * k)
            M.add('strings', harp.play(m, 70), t, 0.5, -0.6 + 1.2 * k)
        elif part == 'cut':
            p = sfp if k == 0 else gunp
            M.add('perc', timp.play(v, pitch=-2), t, 0.7, p)
            M.add('fx', whoosh(0.35, 3000, 6000, 0.6, seed=11 + k), t - 0.1, 0.8, p)
        elif part == 'oath':
            if d > 1.0:
                hold('brass', tpt if k == 0 else tbn, m, t, t + d, v, sfp if k == 0 else gunp, rise=0.08, fall=0.6,
                     gain=0.8)
            else:
                M.add('brass', (tpt if k == 0 else tbn).play(m, v, dur=d * 1.05, release=0.25), t, 0.9,
                      sfp if k == 0 else gunp)
            M.add('low', tuba.play(m - 24, v - 16, dur=d * 1.05, release=0.25), t, 0.5)
            if t == T_OATH[k]:
                M.add('perc', crash.play(110), t, 0.7)
                M.add('perc', timp.play(112, pitch=-4), t, 0.8)
        elif part == 'oathb':
            hold('brass', horn, m, t, t + d, v, -0.5 if m >= note('C3') else 0.5, rise=0.08, fall=0.6, gain=0.8)
            M.add('perc', timp.play(v - 6, pitch=-5), t, 0.6, -0.5 if m >= note('C3') else 0.5)
        elif part == 'plot':
            hold('low', tuba, m + 12, t, t + d, v, hag, rise=0.5, fall=1.0, gain=0.6)
            hold('strings', ctrem, m + 12, t, t + d, v - 10, hag, rise=0.5, fall=1.0, gain=0.4)
        elif part == 'drink':
            M.add('perc', crash.play(120), t, 0.9)
            M.add('perc', timp.play(120, pitch=-5), t, 0.9)
        elif part == 'chord':
            hold('brass', horn, m, t, t + d, v, 0.0, rise=0.05, fall=1.0, gain=0.55)
        elif part == 'hagen':
            M.add('low', tuba.play(m - 12, v, dur=d * 1.2, release=0.4), t, 1.0, hag)
            M.add('low', tbn.play(m, v - 10, dur=d * 1.2, release=0.4), t, 0.7, hag)
            M.add('perc', timp.play(v, pitch=-7 if m < note('C3') else -3), t, 0.9, hag)
            if m < note('C3'):
                M.add('perc', gong.play(96), t, 0.5, hag)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.4), t, 0.9, here if k == 0 else river)
        elif part == 'river':
            hold('strings', ctrem, m + 12, t, t + d, v, river, rise=1.0, fall=1.5, gain=0.55)
            hold('strings', vtrem, m + 24, t, t + d, v - 10, river, rise=1.0, fall=1.5, gain=0.35)
