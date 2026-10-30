"""The Potion: the hall of the Gibichungs, the four of them in it as Siegfried's arrival left them. Gutrune comes
down from beside the throne with the drinking horn to Siegfried, her motif (Donington 40) sending waves of rose
out over the whole house.

He lifts it to Brünnhilde: "Vergäss' ich alles, was du mir gabst" — the first thing he drinks to is her, and her
motif (88) on the horns floods the house silver, a field of silver points standing over every run. Then he
drinks. The potion of forgetting (19) sounds in the clarinets and low strings, slow chords, and with each a tide
of sickly violet pours out of him along the roofline, and the silver points go out one after another under it
until there is nothing left of her.

He looks at Gutrune, and the love potion (39) takes him: every note of its long climbing line slams a whole run
alternately emerald and rose, rings of both colours running out from the two of them, faster and brighter, until
her motif comes back in full and the whole house surges rose and emerald together. In the shadows Hagen's tritone
lands twice, the hall knocked dark and a black-violet shock out from him; then the hall settles, Gutrune at
Siegfried's side.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD10'
TITLE = 'The Potion'
KIND = 'show'
DESCRIPTION = ('Gutrune offers Siegfried a drink. He drinks to Brunnhilde, the potion wipes her from his memory in '
               'a tide of violet, and he burns for Gutrune instead.')
VOICEOVER = ('Siegfried raises the cup to Brunnhilde, and drinks. '
             'In one swallow he forgets her completely.')

K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_GUT = [1.0, 7.5]                          # Gutrune brings the horn
T_WALK = (2.0, 9.0)
T_TOAST = 11.0                              # he drinks to Brunnhilde: her motif, silver
T_DRINK = 17.5                              # the potion
PBEAT = 0.7
T_LOVE = 30.5                               # the love potion takes him
LBEAT = 0.36
T_GUT2 = 47.5                               # her motif in full, rose and emerald together
T_HAGEN = [57.0, 63.5]
T_SETTLE = 68.0
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
SILVER = hexc('#f4f8ff')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD09 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD11 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_FROM = ('Porch Front', 0.38)
GUTRUNE_AT = ('Porch Front', 0.75)          # at Siegfried's side
HAGEN_AT = ('Porch Left', 0.35)
SIEGFRIED_AT = ('Porch Front', 0.85)
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

    add(0.0, D, 'Bb1', 56, 'pedal')
    for k, t0 in enumerate(T_GUT):
        for t, m, v, d in play('gutrune', t0, 0.5, -12, 90 + 6 * k):
            add(t, d, m, v, 'gutrune', k)
    for t, m, v, d in play('brunnhilde', T_TOAST, 0.62, 0, 100):
        add(t, d, m, v, 'toast')
    for t, m, v, d in play('potion', T_DRINK, PBEAT, -12, 92):
        add(t, d, m, v, 'potion')
    for t, m, v, d in play('love_potion', T_LOVE, LBEAT, 0, 104):
        add(t, d, m, v, 'love')
    for t, m, v, d in play('gutrune', T_GUT2, 0.55, -12, 112):
        add(t, d, m, v, 'gutrune', 2)
    for m in ('Bb2', 'D3', 'F3', 'Bb3'):
        add(T_GUT2, 6.6, m, 92, 'swell')
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.7, 0, 118 - 6 * k):
            add(t, d, m, v, 'hagen', k)
    for t, m, v, d in play('gutrune', T_SETTLE + 1.0, 0.75, -24, 74):
        add(t, d, m, v, 'gutrune', 3)
    return sorted(N, key=lambda e: e[0])


def render(G, seed=10):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    gut = [e for e in N if e[4] == 'gutrune']
    toast = [e for e in N if e[4] == 'toast']
    pot = sorted({e[0] for e in N if e[4] == 'potion'})
    love = melody('love_potion')
    love_t = [T_LOVE + b * LBEAT for b, _, _ in love]
    lo, hi = min(m for _, _, m in love), max(m for _, _, m in love)
    hag = [e for e in N if e[4] == 'hagen']
    p_gun, p_hag, p_sf = at(G, *GUNTHER_AT), at(G, *HAGEN_AT), at(G, *SIEGFRIED_AT)
    g0, g1 = at(G, *GUTRUNE_FROM), at(G, *GUTRUNE_AT)
    runs = ['Porch Front', 'Right', 'Left', 'Porch Right', 'Side', 'Porch Left']
    rng = np.random.default_rng(seed)
    pts = rng.uniform(0, L, 70)                     # the silver of her memory, point by point
    out_at = T_DRINK + 0.6 + np.sort(rng.uniform(0, 10.5, 70))[rng.permutation(70)]
    tw = rng.uniform(0, 2 * np.pi, 70)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = hall(S, T, START)
        p_gut = g0 + (g1 - g0) * smoothstep(*T_WALK, t)

        # Gutrune's motif: rose waves out from her over the whole house
        for t0, dur, m, v, part, k in gut:
            a = t - t0
            if 0 <= a < 1.5 and (m >= note('C4') or k == 3):
                fr += light(GUTRUNE, (0.7 + 0.15 * (k == 2)) * wave(S, p_gut, a, 1300.0, 140.0, 0.7))
                fr += light(GUTRUNE, 0.35 * np.exp(-a / 0.3) * S['porch'] * (k < 3))

        # the toast to Brunnhilde: silver floods the house, a field of silver points over every run
        mem = smoothstep(T_TOAST, T_TOAST + 1.5, t)
        for t0, dur, m, v, part, k in toast:
            a = t - t0
            if 0 <= a < 1.6:
                fr += light(SILVER, 0.75 * wave(S, p_sf, a, 1500.0, 160.0, 0.8))
        if mem > 0:
            alive = (t < out_at).astype(float)
            dying = np.exp(-np.clip(t - out_at, 0, None) / 0.15) * (t >= out_at)
            g = mem * (alive * (0.65 + 0.35 * np.sin(7.0 * t + tw)) + 1.6 * dying)
            pts_l = (g[:, None] * np.exp(-((d[None, :] - pts[:, None]) / 7) ** 2)).sum(0)
            fr += light(SILVER, np.clip(pts_l, 0, 1.1))
            fr += light(SILVER, 0.25 * mem * (1 - smoothstep(T_DRINK, T_DRINK + 8, t)))

        # the potion: each chord a tide of sickly violet pouring out of him along the roofline
        for i, t0 in enumerate(pot):
            a = t - t0
            if 0 <= a < 6.0:
                reach = min(1.0, a / 2.2) * L
                tide = smoothstep(reach + 120, reach - 120, np.abs(d - p_sf))
                g = (0.6 + 0.12 * i) * np.exp(-max(a - 2.5, 0) / 1.4)
                fr = fr * (1 - 0.5 * g * tide)[:, None]
                fr += light(POTION, g * tide * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 120 - 1.2 * t))))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.1) * np.exp(-((d - p_sf) / 25) ** 2))
        if T_DRINK <= t < T_LOVE:
            fr += light(POTION, 0.35 * smoothstep(T_DRINK, T_DRINK + 3, t) * (1 - smoothstep(T_LOVE - 2, T_LOVE, t)))

        # the love potion: every note slams a whole run, emerald and rose by turns, rings out from both of them
        for i, ((b, dur, m), t0) in enumerate(zip(love, love_t)):
            a = t - t0
            if 0 <= a < 2.0:
                u = (m - lo) / (hi - lo)
                run = G.seg_of == runs[i % len(runs)]
                col = SIEGFRIED if i % 2 == 0 else GUTRUNE
                g = (0.7 + 0.3 * u) * np.exp(-a / (0.35 + dur * LBEAT))
                fr = fr * (1 - 0.6 * np.exp(-a / 0.4) * run)[:, None]
                fr += light(col, g * run)
                fr += light(col, 0.75 * wave(S, p_sf if i % 2 == 0 else p_gut, a, 1500.0, 110.0, 0.6))

        # her motif in full: the whole house surges rose and emerald together, the two colours chasing
        if T_GUT2 <= t < T_GUT2 + 9.0:
            a = t - T_GUT2
            g = smoothstep(0, 0.5, a) * (1 - smoothstep(6.0, 9.0, a))
            ph = np.sin(2 * np.pi * (d / 300 - 0.9 * a))
            fr += light(GUTRUNE, 0.9 * g * np.clip(ph, 0, 1))
            fr += light(SIEGFRIED, 0.9 * g * np.clip(-ph, 0, 1))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12))

        # settled at her side: the two of them keep throwing rings of emerald and rose round the house
        if t >= T_SETTLE:
            g = smoothstep(T_SETTLE, T_SETTLE + 1.5, t) * (1 - smoothstep(D - 3.5, D - 0.5, t))
            for j in range(3):
                a = (t - T_SETTLE - 1.3 * j) % 3.9
                fr += light(SIEGFRIED if j % 2 == 0 else GUTRUNE, 0.6 * g * wave(S, (p_sf + p_gut) / 2, a, 900.0, 120.0, 1.0))

        # the four of them; Siegfried burns brighter once the potion has him
        burn = smoothstep(T_LOVE, T_LOVE + 2, t) * (1 - smoothstep(T_SETTLE, D - 2, t))
        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8 + 0.15 * burn)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        fr = figure(fr, S, p_sf, SIEGFRIED, 0.85 + 0.15 * burn)
        fr += light(HEAD, 0.8 * (0.85 + 0.15 * burn) * np.exp(-((d - p_sf) / 6) ** 2))
        if T_DRINK - 0.5 <= t < T_LOVE:          # the memory leaving him: a violet veil over his head
            fr += light(POTION, 0.5 * np.exp(-((d - p_sf) / 30) ** 2) * smoothstep(T_DRINK - 0.5, T_DRINK, t))
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

    for name, gain, rev in (('low', 0.34, 0.25), ('brass', 0.32, 0.3), ('strings', 0.3, 0.35), ('winds', 0.3, 0.35),
                            ('perc', 0.32, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    tri = M.hits('Percussion/Triangle3-Hit*.wav')

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

    sf, hag = pan_at(at(G, *SIEGFRIED_AT)), pan_at(at(G, *HAGEN_AT))
    gut = pan_at(at(G, *GUTRUNE_AT))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=4.0, fall=2.0, gain=0.5)
        elif part == 'gutrune':
            if m >= note('C4'):
                M.add('winds', oboe.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.85, gut)
            else:
                M.add('strings', vc.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.6, gut)
        elif part == 'toast':
            if d > 1.0:
                hold('brass', horn, m, t, t + d, v, sf, rise=0.2, fall=1.0, gain=0.8)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, sf)
            M.add('strings', harp.play(m + 12, 70), t, 0.5, sf)
            if t == T_TOAST:
                M.add('perc', tri.play(90), t, 0.6, sf)
        elif part == 'potion':
            hold('winds', clar, m, t, t + d, v, sf, rise=0.6, fall=1.5, gain=0.7)
            hold('low', vc, m - 12, t, t + d, v - 8, sf, rise=0.8, fall=1.5, gain=0.6)
            if m == min(e[2] for e in compose() if e[4] == 'potion' and e[0] == t):
                M.add('perc', gong.play(70), t, 0.5, sf)
        elif part == 'love':
            M.add('strings', vln.play(m, v, dur=d * 1.2, release=0.3), t, 0.8, sf)
            M.add('winds', oboe.play(m - 12, v - 14, dur=d * 1.1, release=0.3), t, 0.45, gut)
        elif part == 'swell':
            hold('brass', horn, m, t, t + d, v, 0.0, rise=0.3, fall=2.0, gain=0.55)
            if m == note('Bb2'):
                M.add('perc', crash.play(110), t, 0.7)
                M.add('perc', timp.play(110, pitch=-4), t, 0.8)
        elif part == 'hagen':
            M.add('low', tuba.play(m - 12, v, dur=d * 1.2, release=0.4), t, 1.0, hag)
            M.add('low', tbn.play(m, v - 10, dur=d * 1.2, release=0.4), t, 0.7, hag)
            M.add('perc', timp.play(v, pitch=-7 if m < note('C3') else -3), t, 0.9, hag)
