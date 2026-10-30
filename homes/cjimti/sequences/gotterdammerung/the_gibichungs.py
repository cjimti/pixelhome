"""The Gibichungs: the hall of the Gibichungs on the Rhine. The porch is the hall, torchlit amber under royal
purple drapes, its torches burning along the porch and the far walls (Left and the Side); Right is the
riverbank, reeds and wet stone, and at its free end the Rhine runs past in indigo and teal.

The torches catch one by one, each a white-hot pop and a spray of sparks, and the hall fills with light. Gunther
sits in it in royal gold, and his fanfare (composed: there is no Commons example of Gunther's motif) on the
trombones sends a gold surge over the porch and out along both wings at every note. Then Hagen's falling tritone
(Donington 61a) hits like a blow: the whole house is knocked dark for a moment and a black-violet shock runs out
from the shadows on Porch Left to both ends, and there he is, ultraviolet in black, his spear point glinting.

Gutrune's motif (40) on the oboe and violins answers in rose: every note a rose ripple out from her across the
house, the long ones tinting every run. Hagen tells them of a hero who won the Nibelung hoard: Siegfried's horn
call (48) sounds far off and an emerald streak races in along the river from the free end of Right and fades,
and the Ring (8) glints gold round Hagen in the bassoons. Gunther's fanfare and Gutrune's motif come back,
gold and rose taking whole runs in turn, and Hagen's tritone falls twice more, the last blow leaving the three
of them in the torchlight: Gunther and Gutrune on their thrones on Porch Front, Hagen in the shadows.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD07'
TITLE = 'The Gibichungs'
KIND = 'show'
DESCRIPTION = ('A torchlit hall on the Rhine: King Gunther in gold, his sister Gutrune in rose, and in the shadows '
               'their half-brother Hagen, whose every word lands like a blow.')
VOICEOVER = ('On the banks of the Rhine stands the hall of the Gibichungs. '
             'And in its shadows, Hagen is waiting.')

K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_TORCH = [0.4 + 0.55 * i for i in range(11)]       # the torches catch one by one
FANFARE = [('Bb2', 1.0), ('F3', 0.5), ('Bb3', 0.5), ('D4', 1.0), ('C4', 0.5), ('Bb3', 0.5), ('F3', 2.0)]
T_GUN = [6.5, 56.0]                         # Gunther's fanfare
T_HAGEN = [14.0, 17.0, 52.0, 71.0, 74.5]    # Hagen's tritone, each a blow
T_GUT = [21.5, 30.5, 63.0]                  # Gutrune's motif
T_HORN = 41.0                               # Siegfried's horn call, far off down the river
T_RING = 46.5                               # the Ring, glinting round Hagen
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

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)     # where GD08 picks it up
GUNTHER_AT = ('Porch Front', 0.62)          # on his throne
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)             # in the shadows
FIGS_END = dict(gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75))


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

    add(0.0, D, 'Bb1', 60, 'pedal')
    for i, t0 in enumerate(T_TORCH):
        add(t0, 0.4, ('F4', 'Bb4', 'D5', 'F5')[i % 4], 70 + 3 * i, 'torch', i)
    for k, t0 in enumerate(T_GUN):
        t = t0
        for m, b in FANFARE:
            add(t, b * BEAT * 1.05, m, 104 + 6 * k, 'fanfare', k)
            t += b * BEAT
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.7, 0, 116 + 4 * (k % 2)):
            add(t, d, m, v, 'hagen', k)
    for k, t0 in enumerate(T_GUT):
        for t, m, v, d in play('gutrune', t0, 0.65, 0, 84 + 4 * k):
            add(t, d, m, v, 'gutrune', k)
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.36, 0, 78):
        add(t, d, m, v, 'horn')
    for t, m, v, d in play('ring', T_RING, 0.6, -12, 86):
        add(t, d, m, v, 'ring')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=7):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    fan = [e for e in N if e[4] == 'fanfare']
    hag = [e for e in N if e[4] == 'hagen']
    gut = [e for e in N if e[4] == 'gutrune']
    gut_top = {t0: [(t0 + b * 0.65, dd * 0.65, m) for b, dd, m in melody('gutrune')] for t0 in T_GUT}
    ring = [e for e in N if e[4] == 'ring']
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    order = np.random.default_rng(seed).permutation(len(TORCHES))
    glint_at = np.random.default_rng(seed + 1).uniform(p_hag - 220, p_hag + 260, len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lit = smoothstep(0.0, T_TORCH[-1] + 0.8, t)
        lv['hall'] *= 0.25 + 0.75 * lit
        lv['drapes'] *= 0.2 + 0.8 * lit
        lv['torches'] *= lit
        fr = hall(S, T, lv)

        # the torches catch one by one: a white-hot pop and a spray of sparks at each
        for i, t0 in enumerate(T_TORCH):
            a = t - t0
            if 0 <= a < 1.2:
                p = S['torch_at'][order[i]]
                fr += light(HEAT, min(1.0, 1.2 * np.exp(-a / 0.12)) * np.exp(-((d - p) / 14) ** 2))
                fr += light(TORCH, 0.8 * wave(S, p, a, 700.0, 40.0, 0.35))

        # Gunther's fanfare: every note a gold surge over the porch and out along both wings
        for t0, dur, m, v, part, k in fan:
            a = t - t0
            if 0 <= a < 1.6:
                s = 0.6 + 0.4 * (m - note('Bb2')) / 16
                run = G.seg_of == RUNS[int(round(t0 / BEAT)) % len(RUNS)]
                fr += light(GUNTHER, 0.85 * s * np.exp(-a / 0.35) * (S['porch'] | run))
                fr += light(GUNTHER, s * wave(S, p_gun, a, 1300.0, 200.0, 0.8))

        # Gutrune's motif: every melody note a rose ripple from her; the long ones tint every run
        for t0 in T_GUT:
            for tn, dn, m in gut_top[t0]:
                a = t - tn
                if 0 <= a < 2.0:
                    fr += light(GUTRUNE, 0.95 * wave(S, p_gut, a, 800.0, 200.0, 0.9))
                    if dn > 0.6:
                        fr += light(GUTRUNE, 0.55 * np.exp(-a / (dn + 0.3)) * smoothstep(0, 0.1, a))

        # Siegfried's horn far down the river: an emerald streak racing in from the free end of Right, fading
        if T_HORN <= t < T_HORN + 4.0:
            a = t - T_HORN
            p = L + 20 - 520 * a
            fr += light(SIEGFRIED, np.exp(-a / 1.6) * np.exp(-((d - p) / 70) ** 2))
            fr += light(SIEGFRIED, 0.7 * np.exp(-a / 0.3) * (G.seg_of == 'Right'))
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 1.6) * smoothstep(p, p + 300, d) * (d > p) * np.exp(-(d - p) / 300))
            fr += light(HEAD, 0.8 * np.exp(-a / 1.6) * np.exp(-((d - p) / 8) ** 2))

        # the Ring: gold glints swirling round Hagen
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.2:
                fr += light(GOLD, 0.95 * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.05, a)
                            * np.exp(-((d - glint_at[j]) / (35 + 45 * a)) ** 2))

        # the three of them: Gunther from the start, Gutrune with her motif, Hagen from his first blow
        fr = figure(fr, S, p_gun, GUNTHER, 0.8 * smoothstep(2.0, 5.0, t))
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8 * smoothstep(T_GUT[0] - 1.5, T_GUT[0] + 0.5, t))
        if t >= T_HAGEN[0]:
            fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
            fr = figure(fr, S, p_hag, HAGEN, 0.75)
            fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))

        # Hagen's tritone: every note a blow, the second (the low G flat) the heavier
        for t0, dur, m, v, part, k in hag:
            fr = blow(fr, S, p_hag, t - t0, 1.0 if m < note('C3') else 0.6)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.3, 0.25), ('brass', 0.28, 0.3), ('winds', 0.26, 0.32), ('strings', 0.24, 0.35),
                            ('perc', 0.28, 0.3), ('harp', 0.2, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
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

    gun, gut, hag = (pan_at(at(G, *x)) for x in (GUNTHER_AT, GUTRUNE_AT, HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.55)
        elif part == 'torch':
            M.add('harp', harp.play(m, v), t, 0.8, pan_at(at(G, *TORCHES[k % len(TORCHES)])))
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
        elif part == 'gutrune':
            if m >= note('E5'):
                M.add('strings', vln.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.8, gut)
            elif m >= note('D4'):
                M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, gut)
            else:
                M.add('low', bsn.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.6, gut)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.4), t, 0.6, river)
        elif part == 'ring':
            if d > 1.2:
                hold('winds', bsn, m, t, t + d, v, hag, rise=0.3, fall=0.8, gain=0.8)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, hag)
