"""Hagen's Plan: the same torchlit hall. Gunther has no wife and Gutrune no husband, and Hagen has the answer:
Brünnhilde for Gunther, asleep on a rock behind a wall of fire, and for Gutrune the hero who can walk through
it. His tritone (Donington 61a) knocks the hall dark again, and then the potion (19) seeps out of the shadows on
the clarinets and low strings: a sickly violet glow creeping out from Hagen along the roofline both ways, its
edge ragged, every chord of the motif a pulse through everything it has reached.

Gutrune's motif (40) pushes back in rose, a wave that drives the violet into the corners, and for a moment the
hall is warm again. Then Hagen names the Ring (8): gold streaks come racing in from both ends of the house and
pour into him, the hoard he means to have. The potion comes back louder and this time floods the whole house,
Gunther's gold and Gutrune's rose drowning in violet, while Hagen's blows fall twice. Gunther's fanfare tries to
take the hall back and gold and violet fight over the runs, one run after another; Hagen's tritone falls three
times more and the violet drains back into him, leaving the hall in torchlight, the three of them where they
were, and the plan made.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD08'
TITLE = "Hagen's Plan"
KIND = 'show'
DESCRIPTION = ('Hagen has a plan: a bride for Gunther, a husband for Gutrune, and a potion to make it happen. '
               'Its sickly violet seeps out of the shadows until it floods the whole house.')
VOICEOVER = ('A sleeping bride for the king, and a hero for his sister. '
             'All it takes, says Hagen, is a drink.')

K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
FANFARE = [('Bb2', 1.0), ('F3', 0.5), ('Bb3', 0.5), ('D4', 1.0), ('C4', 0.5), ('Bb3', 0.5), ('F3', 2.0)]
T_HAGEN = [1.0, 46.0, 49.0, 66.0, 69.5, 73.0]   # Hagen's tritone, each a blow
T_POTION = [5.0, 37.0]                       # the potion creeping out, then flooding
PBEAT = [0.7, 0.55]
T_GUT = 18.0                                 # Gutrune pushes it back
T_RING = 27.0                                # the Ring: gold pours into Hagen
T_GUN = 55.0                                 # Gunther's fanfare, fighting the violet
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

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD07 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD09 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_AT = ('Porch Front', 0.38)
HAGEN_AT = ('Porch Left', 0.35)
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
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.7, 0, 112 + 4 * (k % 2)):
            add(t, d, m, v, 'hagen', k)
    for k, t0 in enumerate(T_POTION):
        for t, m, v, d in play('potion', t0, PBEAT[k], -12 + 12 * k, 86 + 18 * k):
            add(t, d, m, v, 'potion', k)
    for t, m, v, d in play('gutrune', T_GUT, 0.65, 0, 88):
        add(t, d, m, v, 'gutrune')
    for t, m, v, d in play('ring', T_RING, 0.6, -12, 100):
        add(t, d, m, v, 'ring')
    t = T_GUN
    for m, b in FANFARE * 2:
        add(t, b * BEAT * 1.05, m, 104, 'fanfare')
        t += b * BEAT
    return sorted(N, key=lambda e: e[0])


def potion_reach(t):
    """How far the violet has crept from Hagen (path units) and how strongly."""
    a0, a1 = T_POTION
    reach = keys(t, [(a0, 0.0), (a0 + 11.0, 650.0), (T_GUT, 650.0), (T_GUT + 3, 120.0), (a1, 120.0),
                     (a1 + 8.0, 2600.0), (T_HAGEN[3], 2600.0), (T_HAGEN[5] + 2.0, 0.0)])
    level = keys(t, [(a0, 0.0), (a0 + 1.0, 0.65), (T_GUT, 0.65), (T_GUT + 3, 0.3), (a1, 0.35), (a1 + 4, 0.85),
                     (T_HAGEN[3], 0.85), (T_HAGEN[5] + 2.5, 0.0)])
    return float(reach), float(level)


def render(G, seed=8):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    hag = [e for e in N if e[4] == 'hagen']
    pot = np.array(sorted({e[0] for e in N if e[4] == 'potion'}))
    gut = [(T_GUT + b * 0.65, dd * 0.65, m) for b, dd, m in melody('gutrune')]
    ring = [e for e in N if e[4] == 'ring']
    fan = [e for e in N if e[4] == 'fanfare']
    p_gun, p_gut, p_hag = at(G, *GUNTHER_AT), at(G, *GUTRUNE_AT), at(G, *HAGEN_AT)
    rng = np.random.default_rng(seed)
    ragged = smooth_noise(rng, d, 25.0)
    tendril = Flicker(rng, G.N, 0.3, 1.1)
    runs = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right', 'Side']
    streak_from = rng.choice([0.0, L], len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = hall(S, T, START)

        # the potion: a sickly violet creeping out from Hagen with a ragged edge, pulsing on every chord
        reach, plev = potion_reach(t)
        if plev > 0.001:
            dist = np.abs(d - p_hag) + 60 * ragged + 40 * tendril(T)
            cover = smoothstep(reach + 40, reach - 80, dist)
            j = int(np.searchsorted(pot, t, side='right')) - 1
            pulse = np.exp(-(t - pot[j]) / 0.4) if j >= 0 and t - pot[j] < 3 else 0.0
            fr = fr * (1 - 0.8 * plev * cover)[:, None]
            fr += light(POTION, plev * cover * (0.55 + 0.45 * pulse + 0.15 * tendril(T)))
            fr += light(WHITE, 0.25 * plev * pulse * np.exp(-((dist - reach) / 30) ** 2))

        # Gutrune pushes back: a rose wave from her driving the violet off, every note a ripple
        for tn, dn, m in gut:
            a = t - tn
            if 0 <= a < 2.0:
                fr += light(GUTRUNE, 0.95 * wave(S, p_gut, a, 800.0, 220.0, 0.9))
                if dn > 0.6:
                    fr += light(GUTRUNE, 0.5 * np.exp(-a / (dn + 0.3)) * smoothstep(0, 0.1, a))

        # the Ring: gold streaks race in from the ends of the house and pour into Hagen
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < 1.4:
                p0 = streak_from[j]
                p = p0 + (p_hag - p0) * min(1.0, a / 1.0) ** 1.5
                tail = np.clip((d - p) / (p0 - p + 1e-6), 0, 1) * (np.sign(p0 - p) * (d - p) > 0)
                fr += light(GOLD, np.exp(-((d - p) / 80) ** 2) * (1 - smoothstep(1.0, 1.4, a)))
                fr += light(GOLD, 0.6 * np.exp(-np.abs(d - p) / 250) * tail * (1 - smoothstep(0.9, 1.4, a)))
                if a >= 1.0:
                    fr += light(HEAT, 0.9 * np.exp(-(a - 1.0) / 0.12) * np.exp(-((d - p_hag) / 25) ** 2))

        # Gunther's fanfare against the violet: gold takes one run after another
        for i, (t0, dur, m, v, part, k) in enumerate(fan):
            a = t - t0
            if 0 <= a < 1.4:
                run = G.seg_of == runs[i % len(runs)]
                fr = fr * (1 - 0.6 * np.exp(-a / 0.45) * run)[:, None]
                fr += light(GUNTHER, 1.0 * np.exp(-a / 0.55) * run)
                fr += light(GUNTHER, 0.8 * wave(S, p_gun, a, 1300.0, 180.0, 0.7))

        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75 + 0.2 * plev)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
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
                            ('perc', 0.28, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
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
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.55)
        elif part == 'hagen':
            M.add('low', tuba.play(m - 12, v, dur=d * 1.2, release=0.4), t, 1.0, hag)
            M.add('low', tbn.play(m, v - 10, dur=d * 1.2, release=0.4), t, 0.7, hag)
            M.add('perc', timp.play(v, pitch=-7 if m < note('C3') else -3), t, 0.9, hag)
            if m < note('C3'):
                M.add('perc', gong.play(90), t, 0.45, hag)
        elif part == 'potion':
            if m >= note('C4'):
                hold('winds', clar, m - 12, t, t + d, v, hag * 0.5, rise=0.4, fall=1.0, gain=0.75)
            elif m >= note('E3'):
                hold('strings', vla, m, t, t + d, v - 6, hag * 0.5, rise=0.5, fall=1.0, gain=0.7)
            else:
                hold('low', vc, m, t, t + d, v - 6, hag * 0.5, rise=0.5, fall=1.0, gain=0.7)
        elif part == 'gutrune':
            if m >= note('E5'):
                M.add('strings', vln.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.8, gut)
            elif m >= note('D4'):
                M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, gut)
            else:
                M.add('low', bsn.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.6, gut)
        elif part == 'ring':
            if d > 1.2:
                hold('winds', bsn, m, t, t + d, v, hag, rise=0.3, fall=0.8, gain=0.85)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, hag)
        elif part == 'fanfare':
            M.add('brass', tbn.play(m, v, dur=d, release=0.25), t, 0.95, gun)
            if m < note('C3'):
                M.add('perc', timp.play(v, pitch=-2), t, 0.7, gun)
