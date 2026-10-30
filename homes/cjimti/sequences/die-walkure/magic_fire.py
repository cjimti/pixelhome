"""Magic Fire: the end of the opera. Loge's flames, already round the porch, run on out along both wings and
down the Side until the whole house is ringed with fire: red at the roots, orange to gold at the tips, licking
both ways, every climbing figure of Loge's fire (Donington 20) in the violins and harp throwing a tongue of
flame leaping along the roofline, and his flickering (Donington 20a) on piccolo and glockenspiel scattering
sparks of white-gold over it.

Over the fire, in E major, the magic sleep (Donington 16) shimmers in the woodwinds and high strings: every
chord a soft violet ripple out from the sleeper through the flames, and her glow lifting with it. Then
Wotan proclaims the hero in the brass, Siegfried's strength (Donington 53), twice, the second time with the
trombones, timpani and cymbals: "whoever fears my spear shall never pass this fire." Each time the fire leaps
up, the house flashes gold, and a white-gold streak runs in from the free end of Right toward her.

Wotan looks back at her one last time, to the first bars of his grief (Donington 82) on the trombones: his
blue brightens and a thin line of it reaches toward her and falls back. Then he walks away through the fire,
along Porch Left and Left and out along the Side to its far end, the flames parting round him and closing
behind. The sleep shimmers once more as the fire settles, the power of fate (Donington 84) sounds softly on
the Wagner tubas, and the opera ends on a glowing bed of fire all round the house, and in the middle of it, at
the summit of the rock, the sleeping Brünnhilde.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK30'
TITLE = 'Magic Fire'
KIND = 'show'
DESCRIPTION = ('Fire rings the rock and then the whole house, and over it the music of sleep shimmers while '
               'Wotan swears that no one who fears his spear will ever pass. He looks back once, walks out '
               'through the flames, and leaves his daughter sleeping in a ring of fire.')
VOICEOVER = ('The fire spreads until it surrounds everything. '
             'Only a hero who knows no fear will ever walk through it.')

LOGES = [0.9 + 1.6 * k for k in range(50)]  # Loge's figure, on the grid WK29 began
T_SLEEP = 8.0                               # the magic sleep, shimmering
SBEAT = 1.0
SIEGS = [(30.0, 0.8, 0), (35.0, 1.0, 1)]    # Siegfried proclaimed
T_LOOK = 42.0                               # Wotan looks back
T_LEAVE = 49.0                              # and walks out through the fire
T_GONE = 63.0
T_SLEEP2 = 56.0
T_FATE = 66.0                               # the power of fate, softly
FBEAT = 1.4
D = 80.0
T0 = 80.0 * 29                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
VIOLET = hexc('#7a6aff')
SHIELD = hexc('#c8d8ff')
HERO = hexc('#fff0a0')
GOLD = hexc('#ffd060')
SPARK = hexc('#fff0b0')
FATE_HI = hexc('#4a2ab8')
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
    """The fire's state on the opera's clock (shared with WK29): (reach from the rock, level)."""
    bt = ta - 1920.0
    reach = np.interp(bt, [343.3, 346, 352, 365, 380, 400, 410, 422], [0, 90, 200, 380, 560, 680, 1000, 1500])
    level = np.interp(bt, [343.3, 344, 360, 400, 425, 440, 470, 480], [0, .95, .8, .82, .92, .9, .72, .64])
    return float(reach), float(level)


def flames(d, ta, ds, db, fl, boost=0.0, settle=0.0):
    """Light of the fire at clock ta: ds = distance from where the spear struck, db = from the sleeper."""
    reach, level = blaze(ta)
    on = smoothstep(reach + 70, reach - 70, ds)
    front = np.exp(-((ds - reach) / 60) ** 2) * smoothstep(0, 60, reach)
    q = np.clip((heat(d, ta) + 0.18 * fl(ta) + 0.25 * front + 0.3 * boost) * (1 - 0.12 * settle) + 0.05 * settle, 0, 1)
    ring = 1 - 0.75 * np.exp(-(db / 42) ** 2)
    lvl = (level + 0.15 * boost - 0.04 * settle) * on * ring
    return light(FIRE(q), lvl * (0.45 + 0.7 * q)) + light(AMBER, 0.35 * front * ring), lvl


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for j, t0 in enumerate(LOGES):                          # Loge's fire, on and on
        if t0 > D - 3.0:
            break
        k = j + 36
        tr = (0, 3, 7, 12)[k % 4] + 17 - 5 * (t0 > T_LOOK) - 3 * (t0 > T_SLEEP2 + 6)
        v = 96 - 14 * smoothstep(SIEGS[0][0] - 3, SIEGS[0][0], t0) * (1 - smoothstep(SIEGS[1][0] + 4, T_LOOK, t0)) \
            - 38 * smoothstep(T_LOOK, D - 6, t0)
        for t, m, vv, d in play('loge', t0, 0.2, tr, int(v)):
            add(t, d, m, vv, 'loge', j)
        for t, m, vv, d in play('loge_flicker', t0 + 0.8, 0.12, 12, int(v - 8)):
            add(t, d, m, vv, 'flicker', j)
    for m in ('E1', 'B1', 'E3', 'Ab3', 'B3', 'E4'):        # E major under the fire
        add(0.0, SIEGS[0][0] - 0.5, m, 66, 'firebed')
    for t, m, v, d in play('sleep', T_SLEEP, SBEAT, -4, 86):
        add(t, d, m, v, 'sleep', 1)
    for k, (t0, beat, big) in enumerate(SIEGS):
        for t, m, v, d in play('siegfried', t0, beat, -10, 116 + 6 * k):
            add(t, d, m, v, 'sieg', k)
        for m in ('E1', 'E2', 'B2', 'E3', 'Ab3'):
            add(t0, 4 * beat + 0.8, m, 100 + 8 * k, 'siegbed', k)
        add(t0, 1.5, 'E2', 112 + 10 * k, 'hit', k)
        if big:
            add(t0 + 2 * beat, 1.5, 'B1', 116, 'hit', k)
    for m in ('E1', 'B1', 'E3', 'Gb3', 'B3', 'Eb4'):
        add(T_LOOK - 1.5, T_SLEEP2 - T_LOOK + 1.5, m, 60, 'firebed')
    for t, m, v, d in play('wotan_grief', T_LOOK, 0.6, 0, 92):
        if t < T_LOOK + 12 * 0.6:
            add(t, d, m, v, 'grief')
    for t, m, v, d in play('sleep', T_SLEEP2, SBEAT, -4, 66):
        add(t, d, m, v, 'sleep', 2)
    for t, m, v, d in play('fate', T_FATE, FBEAT, 0, 72):
        add(t, d, m, v, 'fate')
    for m in ('E1', 'B1', 'E3', 'Ab3', 'B3', 'E4'):
        add(T_SLEEP2 + 20 * SBEAT - 0.5, D - 0.6 - T_SLEEP2 - 20 * SBEAT + 0.5, m, 48, 'firebed')
    add(D - 4.0, 0.0, 'E2', 70, 'arp')
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
    """Per frame: where Wotan is (path distance) as he walks out through the fire; Brünnhilde sleeps at the summit."""
    F = nframes(D)
    t = np.arange(F) * DT
    p0 = at(G, 'Porch Front', 0.25)
    u = np.clip((t - T_LEAVE) / (T_GONE - T_LEAVE), 0, 1)
    w = p0 + (-30.0 - p0) * (u * u * (3 - 2 * u)) ** 0.9
    look = 6 * np.sin(np.pi * np.clip((t - T_LOOK) / 6, 0, 1))          # a step toward her as he looks back
    return dict(t=t, w=follow(w + look, np.full(F, 4.0)), b=np.full(F, at(G, 'Porch Front', 0.5)))


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)            # the shield's shimmer
    fl = Flicker(np.random.default_rng(2901), G.N, 4.0, 11.0)           # flame flicker, shared with WK29
    pb = at(G, 'Porch Front', 0.5)
    sp = at(G, 'Porch Front', 0.25)
    ds = np.abs(d - sp)
    db = np.abs(d - pb)
    sleeps = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    sieg = [np.array([e[0] for e in N if e[4] == 'sieg' and e[5] == k]) for k in range(2)]
    hits = np.array([e[0] for e in N if e[4] == 'hit'])
    glocks = np.array([e[0] for e in N if e[4] == 'flicker' and e[1] >= 0.2])
    grief = np.array([e[0] for e in N if e[4] == 'grief'])
    fates = np.array(sorted({e[0] for e in N if e[4] == 'fate'}))
    # a leaping tongue for each of Loge's figures: (start, from, direction)
    leaps = [(t0, rng.uniform(0, L), rng.choice([-1, 1])) for t0 in LOGES if t0 < D - 3]
    sparks_at = rng.uniform(0, L, len(glocks))

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw = C['w'][f]
        dw = np.abs(d - pw)
        boost = sum(np.exp(-(t - s[0]) / 1.2) * (t >= s[0]) for s in sieg if len(s)) * (t < T_LOOK)
        gone = smoothstep(T_GONE - 1.5, T_GONE + 0.5, t)

        # the fire, parting round Wotan as he walks through it
        fire, lvl = flames(d, ta, ds, db, fl, min(boost, 1.0), smoothstep(T_FATE - 4, D - 3, t))
        part = 1 - 0.85 * np.exp(-(dw / 45) ** 2) * (1 - gone) * smoothstep(T_LEAVE - 1, T_LEAVE + 1, t)
        fr *= (1 - 0.6 * np.clip(lvl / 0.7, 0, 1))[:, None]
        fr += fire * part[:, None]

        # leaping tongues and glockenspiel sparks
        for t0, x0, sd in leaps:
            if t0 <= t < t0 + 0.9:
                age = t - t0
                q = x0 + sd * 260 * (age / 0.9) ** 0.6
                fr += light(AMBER, 1.0 * (1 - age / 0.9) * np.exp(-((d - q) / 40) ** 2) * (lvl > 0.05))
                fr += light(SPARK, 0.85 * (1 - age / 0.9) * np.exp(-((d - q) / 14) ** 2) * (lvl > 0.05))
        i = int(np.searchsorted(glocks, t, side='right')) - 1
        for j in range(max(0, i - 3), i + 1):
            if 0 <= t - glocks[j] < 0.5:
                fr += light(SPARK, 0.9 * np.exp(-(t - glocks[j]) / 0.15) * np.exp(-((d - sparks_at[j]) / 8) ** 2))

        # the sleep: violet ripples through the flames from her
        i = int(np.searchsorted(sleeps, t, side='right')) - 1
        sp_ = recent(sleeps, t, 0.9)
        if i >= 0 and t - sleeps[i] < 2.2:
            age = t - sleeps[i]
            band = np.exp(-((db - 1100 * age / 2.2) / 150) ** 2) * (1 - age / 2.2)
            fr += light(VIOLET, (0.55 if sleeps[i] < T_SLEEP2 else 0.4) * band)

        # Siegfried proclaimed: the house flashes gold, a white-gold streak runs in from the free end of Right
        hp = recent(hits, t, 0.3)
        fr += light(GOLD, 0.75 * hp * np.ones(G.N)) + light(SPARK, 0.4 * hp ** 2 * np.ones(G.N))
        for k in range(2):
            t0 = SIEGS[k][0]
            t1 = t0 + 4 * SIEGS[k][1]
            if t0 <= t < t1 + 1.5:
                u = np.clip((t - t0) / (t1 - t0), 0, 1)
                q = L + (pb + 60 - L) * u ** 0.8
                fade = 1 - smoothstep(t1, t1 + 1.5, t)
                n = recent(sieg[k], t, 0.15)
                fr += light(HERO, fade * ((0.95 + 0.05 * n) * np.exp(-((d - q) / 26) ** 2)
                                          + (0.5 + 0.3 * n) * (d > q) * np.exp(-(d - q) / 300)))

        # fate: soft indigo shadows passing over the fire
        fl_ = smoothstep(T_FATE - 0.5, T_FATE + 1, t)
        if fl_ > 0:
            fp = recent(fates, t, 1.8, 7.0)
            tex = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 260 + 0.04 * ta)) * np.sin(2 * np.pi * (d / 610 - 0.03 * ta))
            fr *= 1 - 0.22 * fl_ * fp
            fr += light(FATE_HI, fl_ * 0.28 * fp * tex * (1 - np.exp(-(db / 60) ** 2)))

        # Wotan: looks back (a thin line of blue toward her), then walks out along the Side
        gp = recent(grief, t, 0.6)
        lk = smoothstep(T_LOOK, T_LOOK + 1.5, t) * (1 - smoothstep(T_LOOK + 4.5, T_LEAVE, t))
        if lk > 0:
            reach = (pb - pw) * lk
            line = ((d > pw) & (d < pw + reach)) * (0.5 + 0.2 * np.sin(2 * np.pi * (d / 30 - 1.5 * ta)))
            fr += light(WOTAN_SOFT, 0.75 * lk * line)
        wc = mix(WOTAN, WOTAN_SOFT, 0.2 + 0.4 * lk)
        fr += light(wc, (1 - gone) * ((0.85 + 0.15 * gp + 0.1 * lk) * np.exp(-(dw / 24) ** 2)
                                     + 0.375 * np.exp(-(dw / 120) ** 2)))

        # Brünnhilde asleep under her shield, glowing up with each chord of the sleep
        fr += light(SLEEP_C, (0.53 + 0.15 * sp_) * np.exp(-(db / 26) ** 2) + (0.28 + 0.1 * sp_) * np.exp(-(db / 70) ** 2))
        arc = np.exp(-(db / 34) ** 4)
        fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * (rng.random(G.N) < 0.06) * arc)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    rend = pan_at(G.length)
    rng = np.random.default_rng(3001)

    def pan_of(t):
        return pan_at(np.interp(t, C['t'], C['w']))

    for name, gain, rev in (('strings', 0.15, 0.42), ('low', 0.17, 0.25), ('brass', 0.26, 0.38), ('winds', 0.13, 0.42),
                            ('harp', 0.15, 0.48), ('perc', 0.17, 0.38)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    cym = M.hits('Percussion/susCymb1-cresc-Median_v1.wav')

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
        if part == 'loge':
            p = float(rng.uniform(-0.8, 0.8))
            M.add('strings', vns.play(m, v, dur=d, release=0.08), t, 0.6, p)
            M.add('harp', harp.play(m + 12, v - 10), t, 0.55, -p)
        elif part == 'flicker':
            p = float(rng.uniform(-0.8, 0.8))
            M.add('winds', pic.play(m, v), t, 0.5, p)
            if d >= 0.2:
                M.add('perc', glock.play(m, v - 6), t, 0.55, -p)
        elif part == 'firebed':
            s = cb if m < note('C3') else vtrem if m >= note('E4') else va
            hold('strings', s, m + 12 * (m < note('E2')), t, t + d, v, -0.4 + 0.8 * ((m * 7) % 12) / 11,
                 rise=1.0, fall=1.5, gain=0.5)
        elif part == 'sleep':
            g = 1.0 if who == 1 else 0.8
            if m >= note('Ab4'):
                M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.7), t, g, pf - 0.15)
                M.add('strings', vn.play(m, v - 16, dur=d * 1.05, release=0.7), t, 0.6 * g, pf + 0.2)
            elif m >= note('C4'):
                M.add('winds', (ob if m % 2 else cl).play(m, v - 6, dur=d * 1.05, release=0.7), t, 0.8 * g, pf + 0.15)
            elif m >= note('C3'):
                M.add('brass', horn.play(m, v - 14, dur=d * 1.05, release=0.7), t, 0.3 * g, pf)
        elif part == 'sieg':
            q = rend + (pf - rend) * min(1.0, (t - SIEGS[who][0]) / (4 * SIEGS[who][1]))
            M.add('brass', tpt.play(m, v, dur=d * 1.15, release=0.4), t, 1.1, q)
            M.add('brass', horn.play(m, v - 6, dur=d * 1.15, release=0.4), t, 0.9, q - 0.2)
            if who == 1:
                M.add('brass', tbn.play(m - 12, v - 4, dur=d * 1.15, release=0.4), t, 0.9, q + 0.1)
        elif part == 'siegbed':
            if m < note('C2'):
                hold('low', cb, m + 12, t, t + d, v - 10, pf, rise=0.1, fall=1.5, gain=0.8)
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.8), t, 0.8, pf)
            elif m < note('C3'):
                M.add('brass', tbn.play(m, v - 6, dur=d, release=0.8), t, 0.8, pf)
            else:
                hold('strings', vtrem, m + 12, t, t + d, v - 10, -0.3 + 0.3 * (m % 3), rise=0.1, fall=1.0, gain=0.7)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-2 if m == note('E2') else -7), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 0.55 + 0.25 * who, pf)
            if who == 1 and m == note('E2'):
                M.add('perc', cym.play(90), t - 2.0, 0.5, pf)
        elif part == 'grief':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.6), t, 0.95, pan_of(t))
            M.add('low', vc.play(m, v - 10, dur=d * 1.05, release=0.6), t, 0.7, pan_of(t))
        elif part == 'fate':
            if m >= note('F3'):
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=1.2), t, 0.4, pf + 0.1 * ((m % 5) - 2))
            elif m >= note('C3'):
                M.add('brass', horn.play(m, v - 4, dur=d * 1.05, release=1.2), t, 0.35, pf)
            else:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=1.4), t, 0.6, pf)
        elif part == 'arp':
            for i, x in enumerate((m, m + 7, m + 12, m + 16, m + 19, m + 24, m + 28, m + 31)):
                M.add('harp', harp.play(x + 12, v - 2 * i), t + 0.14 * i, 0.9, -0.6 + 0.17 * i)
            M.add('perc', glock.play(note('E5'), 70), t + 1.4, 0.5, pf)
            M.add('perc', glock.play(note('B5'), 64), t + 1.75, 0.45, pf)
