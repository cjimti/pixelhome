"""Loge, Come!: night on the rock. Brünnhilde sleeps at the summit under her shield, a still violet-silver glow
in the middle of Porch Front, and Wotan stands a little way off to her left. He turns away from her and grips
his spear: the spear's motif (Donington 73) strides down through the trombones, tubas and basses, every note a
cold steel pulse running out from him along the roof while the shaft gleams at his side.

"Loge, hör! Lausche hieher!" He calls the fire god on the trombones, his blue swelling. Then three huge strikes
of the spear on the rock, each with timpani, gong and bass drum under a full brass chord: a steel-white shock
across the whole house and a band of steel light racing out from the rock to both ends of the roofline.

After the third, the rock answers. Loge's fire (Donington 20) leaps up in the violins and harp, and his
flickering (Donington 20a) on piccolo and glockenspiel: flames burst out of the rock where the spear struck and
begin to spread along the porch in both directions, red at the roots and orange to gold at the tips, licking
and flickering, while the music grows into the first bars of the Magic Fire in E major. By the end they have
run the length of the porch, a ring round the sleeper who glows on untouched in the middle, and the first
tongues are reaching for the wings.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK29'
TITLE = 'Loge, Come!'
KIND = 'show'
DESCRIPTION = ('Wotan strikes the rock three times with his spear and calls on Loge, the god of fire. The rock '
               'answers: flames burst out and begin to race along the porch around his sleeping daughter.')
VOICEOVER = ('Three blows of the spear on the rock, and a name called into the night. '
             'Loge, come. And the fire comes.')

T_SPEAR = 4.0                               # the spear's motif
PBEAT = 0.65
T_CALL = 12.5                               # "Loge, hör!"
STRIKES = [17.0, 20.0, 23.0]                # three strikes of the spear
T_FIRE = 23.3                               # flames burst out of the rock
LOGES = [23.3 + 1.6 * k for k in range(35)]
D = 80.0
T0 = 80.0 * 28                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
VIOLET = hexc('#7a6aff')
SHIELD = hexc('#c8d8ff')
STEEL = hexc('#c8d8ff')
WHITE = hexc('#ffffff')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
CLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
ROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')
SLEEP_C = VIOLET + (SILVER - VIOLET) * 0.2


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def mix(a, b, w):
    return a + (b - a) * w


def stage(d, ta, porch):
    """The rock (porch) and the evening sky over the wings, on the opera's clock ta (shared by WK25-WK30)."""
    bt = ta - 1920.0
    rock = np.interp(bt, [0, 160, 240, 320, 400, 480], [.42, .42, .43, .38, .34, .3])
    sky = np.interp(bt, [0, 80, 160, 240, 320, 480], [.4, .41, .41, .38, .34, .3])
    eve = np.interp(bt, [0, 80, 160, 240], [.45, .85, 1.0, .9])
    night = np.interp(bt, [200, 320, 400], [0.0, .6, .85])
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.011 * ta)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.023 * ta) + 1.1)
    sk = CLOUD + (EVE - CLOUD) * (eve * (0.35 + 0.65 * u))[:, None]
    sk = sk + (NIGHT - sk) * night
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    return light(sk, sky * (0.7 + 0.3 * u) * (1 - porch)) + light(rk, rock * (0.8 + 0.2 * u) * porch)


def heat(d, ta):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways, swelling and sinking
    region by region."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * ta)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * ta) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * ta) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * ta) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * ta)) * np.sin(2 * np.pi * (d / 260 - 0.31 * ta) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def blaze(ta):
    """The fire's state on the opera's clock (shared with WK30): (reach from the rock, level)."""
    bt = ta - 1920.0
    reach = np.interp(bt, [343.3, 346, 352, 365, 380, 400, 410, 422], [0, 90, 200, 380, 560, 680, 1000, 1500])
    level = np.interp(bt, [343.3, 344, 360, 400, 425, 440, 470, 480], [0, .95, .8, .82, .92, .9, .72, .64])
    return float(reach), float(level)


def flames(d, ta, ds, db, fl):
    """Light of the fire at clock ta: ds = distance from where the spear struck, db = from the sleeper."""
    reach, level = blaze(ta)
    if level <= 0 or reach <= 0:
        return np.zeros((len(d), 3)), np.zeros(len(d))
    on = smoothstep(reach + 70, reach - 70, ds)
    front = np.exp(-((ds - reach) / 60) ** 2) * smoothstep(0, 60, reach)
    q = np.clip(heat(d, ta) + 0.18 * fl(ta) + 0.25 * front, 0, 1)
    ring = 1 - 0.75 * np.exp(-(db / 42) ** 2)
    lvl = level * on * ring
    return light(FIRE(q), lvl * (0.45 + 0.7 * q)) + light(AMBER, 0.35 * front * ring), lvl


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('Ab2', 'Eb3', 'C4'):                          # the end of the sleep, hanging in the air
        add(0.0, 5.0, m, 50, 'bed')
    add(0.0, STRIKES[0], 'E1', 56, 'pedal')
    for t, m, v, d in play('spear', T_SPEAR, PBEAT, 0, 104):
        add(t, d, m, v, 'spear')
    for b, d, m in ((0, 1.0, 'E3'), (1.0, 0.5, 'G3'), (1.5, 2.0, 'B3'), (4.0, 0.5, 'Bb3'), (4.5, 1.5, 'E3')):
        add(T_CALL + b * 0.55, d * 0.55, m, 108, 'call')
    for k, ts in enumerate(STRIKES):
        add(ts, 2.4, 'E1', 118 + 4 * k, 'strike', k)
        for m in ('E2', 'B2', 'E3', 'G3', 'Bb3'):
            add(ts, 1.4 + 0.6 * (k == 2), m, 110 + 4 * k, 'strikechord', k)
    add(STRIKES[1] + 1.2, STRIKES[2] - STRIKES[1] - 1.2, 'E2', 90, 'roll')
    for k, t0 in enumerate(LOGES):                         # the Magic Fire begins
        if t0 > D - 1.2:
            break
        tr = (0, 3, 7, 12)[k % 4] + (12 if k >= 8 else 0) + (5 if k >= 20 else 0)
        for t, m, v, d in play('loge', t0, 0.2 + 0.05 * (k < 4), tr + 12, 82 + min(k, 20)):
            add(t, d, m, v, 'loge', k)
        if k % 2 == 1 or k >= 12:
            for t, m, v, d in play('loge_flicker', t0 + 0.8, 0.12, 12 if k >= 12 else 0, 76 + min(k, 20)):
                if t < D - 0.5:
                    add(t, d, m, v, 'flicker', k)
    add(T_FIRE, D - T_FIRE - 0.3, 'E2', 70, 'firebed')
    add(T_FIRE + 8, D - T_FIRE - 8.3, 'B2', 66, 'firebed')
    add(T_FIRE + 16, D - T_FIRE - 16.3, 'Ab3', 62, 'firebed')
    add(T_FIRE + 24, D - T_FIRE - 24.3, 'E4', 60, 'firebed')
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
    """Per frame: where Wotan is (path distance); Brünnhilde sleeps at the middle of Porch Front."""
    F = nframes(D)
    t = np.arange(F) * DT
    w = np.full(F, at(G, 'Porch Front', 0.25))
    sway = 4 * np.sin(2 * np.pi * (t - T_CALL) / 2.0) * ((t > T_CALL) & (t < STRIKES[0]))
    return dict(t=t, w=follow(w + sway, np.full(F, 3.0)), b=np.full(F, at(G, 'Porch Front', 0.5)))


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)            # the shield's shimmer, from WK28
    fl = Flicker(np.random.default_rng(2901), G.N, 4.0, 11.0)           # flame flicker, shared with WK30
    spears = np.array([e[0] for e in N if e[4] == 'spear'])
    calls = np.array([e[0] for e in N if e[4] == 'call'])
    pb = at(G, 'Porch Front', 0.5)
    sp = at(G, 'Porch Front', 0.25)                                       # where the spear strikes the rock
    ds = np.abs(d - sp)
    db = np.abs(d - pb)
    jag = [rng.random(G.N) for _ in range(3)]

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw = C['w'][f]

        # the fire
        fire, lvl = flames(d, ta, ds, db, fl)
        fr *= (1 - 0.6 * np.clip(lvl / 0.7, 0, 1))[:, None]
        fr += fire

        # the spear's motif: steel pulses running out from him, the shaft gleaming at his side
        spl = smoothstep(T_SPEAR - 1, T_SPEAR, t) * (1 - smoothstep(STRIKES[2] + 0.5, STRIKES[2] + 3, t))
        if spl > 0:
            i = int(np.searchsorted(spears, t, side='right')) - 1
            if i >= 0 and t - spears[i] < 1.4:
                age = t - spears[i]
                band = np.exp(-((np.abs(d - pw) - 1300 * age / 1.4) / 90) ** 2) * (1 - age / 1.4)
                fr += light(STEEL, 0.55 * band)
            shaft = ((d > pw - 70) & (d < pw - 8)) * (0.45 + 0.4 * recent(spears, t, 0.3))
            fr += light(STEEL, spl * shaft)

        # the call: his blue swells
        cp = recent(calls, t, 0.4)
        call = smoothstep(T_CALL - 0.5, T_CALL + 0.5, t) * (1 - smoothstep(STRIKES[0], STRIKES[0] + 1, t))
        fr += light(WOTAN, call * (0.35 + 0.25 * cp) * np.exp(-((d - pw) / 260) ** 2))

        # three strikes: a steel-white shock across the house and a band racing to both ends
        for k, ts in enumerate(STRIKES):
            if ts <= t < ts + 1.6:
                age = t - ts
                a = np.exp(-age / 0.15)
                fr += light(WHITE, (0.8 + 0.07 * k) * a * np.ones(G.N))
                r = 2600 * (age / 1.2) ** 0.7
                band = np.exp(-((np.abs(d - sp) - r) / 120) ** 2) * (1 - age / 1.6)
                fr += light(STEEL, 0.9 * band) + light(WHITE, 0.6 * band * (jag[k] > 0.5))
                fr += light(STEEL, 0.6 * np.exp(-age / 0.5) * np.exp(-(ds / 120) ** 2))
        if T_FIRE <= t < T_FIRE + 2.5:                   # the burst out of the rock
            a = np.exp(-(t - T_FIRE) / 0.6)
            sparks = (rng.random(G.N) < 0.25 * a) * np.exp(-(ds / (200 + 500 * (t - T_FIRE))) ** 2)
            fr += light(AMBER, 0.9 * a * np.exp(-(ds / 80) ** 2)) + light(hexc('#fff0b0'), 0.9 * sparks)

        # Wotan
        wc = mix(WOTAN, WOTAN_SOFT, 0.5 - 0.3 * smoothstep(T_SPEAR, T_CALL, t))
        fr += light(wc, (0.85 + 0.1 * cp) * np.exp(-((d - pw) / 24) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))

        # Brünnhilde asleep under her shield
        fr += light(SLEEP_C, 0.53 * np.exp(-(db / 26) ** 2) + 0.28 * np.exp(-(db / 70) ** 2))
        arc = np.exp(-(db / 34) ** 4)
        fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * (rng.random(G.N) < 0.06) * arc)
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
    sp = at(G, 'Porch Front', 0.25)
    psp = pan_at(sp)

    def fire_pan(k):
        """Each fire figure is heard at the leading edge of the flames, alternating sides."""
        reach, _ = blaze(LOGES[k] + T0)
        return pan_at(sp + (reach if k % 2 else -reach))

    for name, gain, rev in (('strings', 0.15, 0.4), ('low', 0.17, 0.25), ('brass', 0.15, 0.35), ('winds', 0.13, 0.4),
                            ('harp', 0.15, 0.45), ('perc', 0.16, 0.35), ('fx', 0.06, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')

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

    for t, d, m, v, part, who in compose():
        if part == 'bed':
            hold('strings', va if m < note('C4') else vn, m, t, t + d, v, pf, rise=0.1, fall=2.0, gain=0.7)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, psp, rise=2.0, fall=1.0, gain=0.8)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, psp)
            M.add('low', tuba.play(m - 12, v - 6, dur=d * 1.05, release=0.4), t, 0.9, psp)
            M.add('low', cb.play(m, v - 10, dur=d, release=0.3), t, 0.7, psp)
        elif part == 'call':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.5), t, 1.1, psp)
            M.add('brass', horn.play(m, v - 14, dur=d * 1.05, release=0.5), t, 0.6, psp)
        elif part == 'strike':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, psp)
            M.add('perc', bd.play(v), t, 1.0, psp)
            M.add('perc', gong.play(v), t, 0.7 + 0.15 * who, psp)
            M.add('perc', crash.play(v), t, 0.6, psp)
            M.add('fx', whoosh(1.6, 3500, 150, 0.7, seed=290 + who), t, 1.0, psp)
        elif part == 'strikechord':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d, release=0.6), t, 1.0, psp)
            else:
                M.add('brass', tbn.play(m, v, dur=d, release=0.6), t, 0.8, psp - 0.1)
                M.add('brass', horn.play(m + 12, v - 8, dur=d, release=0.6), t, 0.7, psp + 0.1)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.8, psp)
        elif part == 'loge':
            p = fire_pan(who)
            M.add('strings', vns.play(m, v, dur=d, release=0.08), t, 0.9, p)
            M.add('harp', harp.play(m, v - 8), t, 0.8, -p * 0.5)
        elif part == 'flicker':
            p = fire_pan(who)
            M.add('winds', pic.play(m, v), t, 0.8, p)
            if d >= 0.3 or m >= note('C6'):
                M.add('perc', glock.play(m, v - 6), t, 0.6, -p)
        elif part == 'firebed':
            s = cb if m < note('C3') else vtrem if m >= note('E4') else va
            hold('strings', s, m, t, t + d, v, -0.4 + 0.8 * ((m * 7) % 12) / 11, rise=3.0, fall=0.5, gain=0.75)
