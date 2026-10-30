"""Was It So Shameful?: the sisters have fled and the storm has blown itself out. On the rock (the porch, dark
slate washed with dusk violet) Wotan stands in his deep blue at the left of Porch Front and Brünnhilde kneels a
little way off, her silver dimmed, while the clouds over the wings turn slowly toward evening.

She pleads. Her love (Donington 87) rises on a solo horn in E major over hushed strings: every long note a
pulse of her silver that swells out across the porch and onto the wings, every little triplet pickup a ripple
of gold glints running from her toward him. At the top of each phrase the silver reaches the ends of the house.
Then she reminds him of the Wälsungs: the tragic destiny of the Volsungs (Donington 66) in the trombones and
tubas, in C minor, each heavy chord a wash of indigo over the whole roof, and with it a faint ghost of
Siegmund's blue on Right where his story began. Wotan's light shrinks under it.

She only did what he truly wished in his heart. Devotion (Donington 80) in the violins, in thirds, over a
G flat glow in the violas: a warm rose-gold breathes across the house, she rises and moves toward him, a
bridge of light grows between the two of them, his hard blue softens and her silver warms toward gold. To
close, the opening of her love once more on an oboe, the two lights a hand's breadth apart.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK25'
TITLE = 'Was It So Shameful?'
KIND = 'show'
DESCRIPTION = ('Alone on the rock with her angry father, Brünnhilde pleads her case. She only did what he truly '
               'wanted in his heart, she tells him, and slowly his hard blue light begins to soften.')
VOICEOVER = ('The storm is over. Now it is just a father and his daughter on a mountain, '
             'and she has one chance to make him understand.')

LBEAT = 0.7                                 # a quarter note of her love
T_PLEA = 3.0                                # Brünnhilde's love, on the horn
T_VF = 27.0                                 # the destiny of the Volsungs
VBEAT = 0.95
T_DEV = 45.0                                # Devotion
DBEAT = 0.95
T_CODA = 66.0                               # her love once more, on an oboe
CBEAT = 0.8
D = 80.0
T0 = 80.0 * 24                              # the opera's clock at our start: steady motion carries across the cuts

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
FATE = hexc('#2a1a5a')
FATE_HI = hexc('#5a30d0')
ROSE = hexc('#ff5a8a')
CLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
ROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')


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


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_PLEA + 1.0, 'E2', 52, 'pad')                 # the last of the storm, settling
    add(0.0, T_PLEA + 1.0, 'B2', 48, 'pad')
    for t, m, v, d in play('brunnhilde_love', T_PLEA, LBEAT, 0, 94):
        add(t, d, m, v + 8 * (d >= 2.5 * LBEAT), 'plea', 'b')
    chords = [(0, ('E2', 'B3', 'E4', 'Ab4')), (8, ('E2', 'B3', 'E4', 'Ab4')), (12, ('A2', 'A3', 'Db4', 'E4')),
              (16, ('Gb2', 'A3', 'Db4', 'Gb4')), (20, ('A2', 'A3', 'Db4', 'E4')), (24, ('Ab2', 'B3', 'E4', 'Ab4')),
              (28, ('E2', 'B3', 'E4', 'Ab4'))]
    for i, (b, ms) in enumerate(chords):
        b1 = chords[i + 1][0] if i + 1 < len(chords) else 32.5
        for m in ms:
            add(T_PLEA + b * LBEAT, (b1 - b) * LBEAT, m, 58 if m != ms[0] else 62, 'bed')
    for t, m, v, d in play('volsung_fate', T_VF, VBEAT, 0, 100):
        add(t, d, m, v, 'vf')
    add(T_VF, 16 * VBEAT, 'C2', 70, 'roll')
    for t, m, v, d in play('devotion', T_DEV, DBEAT, 0, 88):
        add(t, d, m, v, 'dev')
    for b, ms in ((0, ('Gb2', 'Db3', 'Bb3')), (6, ('Db2', 'Ab3', 'F3')), (8, ('Eb2', 'Bb2', 'Gb3')),
                  (12, ('B1', 'Gb3', 'Eb3')), (16, ('Gb2', 'Db3', 'Bb3'))):
        dur = {0: 6, 6: 2, 8: 4, 12: 4, 16: 5}[b]
        for m in ms:
            add(T_DEV + b * DBEAT, dur * DBEAT, m, 60, 'devbed')
    for t, m, v, d in play('brunnhilde_love', T_CODA, CBEAT, 0, 80):
        if t < T_CODA + 8 * CBEAT:
            add(t, d, m, v, 'coda', 'b')
    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3'):
        add(T_CODA, D - T_CODA - 0.5, m, 54, 'bed')
    add(72.5, 3.0, 'B1', 70, 'wotan', 'w')                 # Wotan, quietly: he is listening
    add(75.0, 4.0, 'E2', 66, 'wotan', 'w')
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
    """Per frame: where Wotan and Brünnhilde are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = {k: np.zeros(F) for k in 'wb'}
    rate = {k: np.full(F, 2.0) for k in 'wb'}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('w', 0, D, at(G, 'Porch Front', 0.3), 2.0)
    set_('w', T_DEV + 4, D, at(G, 'Porch Front', 0.36), 0.5)
    set_('b', 0, D, at(G, 'Porch Front', 0.55), 2.0)
    set_('b', T_PLEA + 6, T_VF, at(G, 'Porch Front', 0.52), 0.6)
    set_('b', T_VF, T_DEV, at(G, 'Porch Front', 0.54), 0.5)
    set_('b', T_DEV, D, at(G, 'Porch Front', 0.47), 0.4)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sig = d[G.seg['Right']].min() + 0.35 * (d[G.seg['Right']].max() - d[G.seg['Right']].min())
    tw = Flicker(np.random.default_rng(2501), G.N, 1.5, 5.0)
    plea = [(e[0], e[1]) for e in N if e[4] in ('plea', 'coda')]
    pt = np.array([p[0] for p in plea])
    longs = [p[0] for p in plea if p[1] >= 2.0 * LBEAT * 0.9]
    picks = [p[0] for p in plea if p[1] < 0.5]
    vch = np.array(sorted({e[0] for e in N if e[4] == 'vf'}))
    dev = np.array(sorted({e[0] for e in N if e[4] == 'dev'}))
    peaks = [T_PLEA + 15 * LBEAT, T_PLEA + 20 * LBEAT]

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        fate = smoothstep(T_VF - 1, T_VF + 1, t) * (1 - smoothstep(T_DEV - 3, T_DEV, t))
        devo = smoothstep(T_DEV - 1, T_DEV + 4, t)
        warmth = 0.15 * smoothstep(T_PLEA, T_VF, t) + 0.45 * smoothstep(T_DEV, T_CODA, t)
        lvl = 0.5 + 0.2 * smoothstep(T_PLEA, T_PLEA + 8, t) + 0.15 * devo - 0.1 * fate
        soft = 0.55 * smoothstep(T_DEV + 2, T_CODA + 4, t)

        # her plea: long notes swell silver out over the house, pickups ripple gold toward him
        for ts in longs:
            if ts <= t < ts + 3.0:
                age = t - ts
                r = 700 * smoothstep(0, 2.2, age) + 1500 * any(abs(ts - p) < 0.05 for p in peaks) * smoothstep(0, 2.2, age)
                band = np.exp(-((np.abs(d - pb) - r) / 220) ** 2) * (1 - age / 3.0)
                fr += light(mix(SILVER, WARM, warmth), 0.55 * band)
        for ts in picks:
            if ts <= t < ts + 1.2:
                age = t - ts
                q = pb + (pw - pb) * min(1.0, age / 0.9)
                fr += light(GLINT, 0.7 * (1 - age / 1.2) * np.exp(-((d - q) / 14) ** 2))
        if devo > 0:                                    # devotion: rose-gold breathing out from the two of them
            mid = 0.5 * (pw + pb)
            dp = recent(dev, t, 1.2, 6.0)
            br = 0.55 + 0.45 * np.sin(2 * np.pi * (np.abs(d - mid) / 700 - 0.11 * ta))
            fall = 1 - 0.35 * smoothstep(T_CODA + 4, D, t)
            fr *= 1 - 0.45 * devo * fall
            fr += light(ROSE, devo * fall * (0.3 + 0.16 * dp) * br)
            fr += light(GLINT, devo * fall * (0.2 + 0.2 * dp) * br ** 3 * (0.7 + 0.3 * tw(ta)))

        # the destiny of the Volsungs: indigo over everything, and Siegmund's ghost on Right
        vp = recent(vch, t, 0.6)
        if fate > 0:
            fr *= 1 - 0.5 * fate
            i = int(np.searchsorted(vch, t, side='right')) - 1
            wave = 0.0
            if i >= 0 and t - vch[i] < 1.6:
                age = t - vch[i]
                wave = np.exp(-((np.abs(d - pw) - 1500 * age / 1.6) / 220) ** 2) * (1 - age / 1.6)
            tex = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 260 + 0.04 * ta)) * np.sin(2 * np.pi * (d / 610 - 0.03 * ta))
            fr += light(FATE_HI, fate * (0.22 * tex + 0.22 * vp * tex + 0.4 * wave))
            fr += light(SIEGMUND, fate * (0.35 + 0.3 * vp) * np.exp(-((d - sig) / 40) ** 2))

        # the bridge between them
        lo, hi = min(pw, pb), max(pw, pb)
        bridge = ((d > lo) & (d < hi)) * devo * (0.25 + 0.15 * np.sin(2 * np.pi * (d / 40 - 0.6 * ta)))
        fr += light(mix(WOTAN_SOFT, WARM, 0.5), bridge)

        # Wotan
        wl = 0.85 - 0.2 * fate
        wc = mix(WOTAN, WOTAN_SOFT, soft)
        fr += light(wc, wl * np.exp(-((d - pw) / 24) ** 2) + (0.3 + 0.1 * soft) * np.exp(-((d - pw) / (90 + 40 * soft)) ** 2))

        # Brünnhilde: silver, warming, flaring with each of her notes; gold glints round her
        fl = recent(pt, t, 0.35)
        bc = mix(SILVER, WARM, warmth)
        fr += light(bc, (lvl + 0.2 * fl) * np.exp(-((d - pb) / (20 + 6 * fl)) ** 2)
                    + (0.22 + 0.1 * devo) * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.05 + 0.08 * devo) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, (0.25 + 0.35 * devo + 0.3 * fl) * gl)
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
    sig = pan_at(at(G, 'Right', 0.35))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    for name, gain, rev in (('strings', 0.13, 0.42), ('low', 0.14, 0.25), ('brass', 0.15, 0.38), ('winds', 0.15, 0.42),
                            ('perc', 0.12, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')

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
        if part == 'pad':
            hold('low', vc, m, t, t + d, v, pf, rise=0.1, fall=2.0, gain=0.8)
        elif part == 'plea':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.5), t, 1.1, pan_of('b', t))
        elif part == 'bed':
            s = cb if m < note('C3') else va if m < note('D4') else vn
            hold('strings', s, m, t, t + d, v, -0.3 + 0.6 * ((m * 5) % 12) / 11, rise=1.2, fall=1.4, gain=0.7)
        elif part == 'vf':
            if m >= note('C4'):
                M.add('brass', horn.play(m, v - 10, dur=d * 1.05, release=0.5), t, 0.8, pf - 0.1)
            elif m >= note('B2'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.5), t, 0.9, pf + 0.1)
                M.add('low', vc.play(m, v - 14, dur=d * 1.05, release=0.5), t, 0.6, sig)
            else:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pf)
                M.add('low', cb.play(m + 12, v - 10, dur=d, release=0.5), t, 0.6, pf)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, pf)
        elif part == 'dev':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.6), t, 0.9, pan_of('b', t) - 0.1)
            M.add('winds', cl.play(m - 12, v - 16, dur=d * 1.05, release=0.5), t, 0.6, pan_of('w', t))
        elif part == 'devbed':
            hold('strings', va if m >= note('C3') else cb, m, t, t + d, v, pf + 0.2 * ((m % 3) - 1), rise=1.0,
                 fall=1.2, gain=0.75)
        elif part == 'coda':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pan_of('b', t))
        elif part == 'wotan':
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.8), t, 0.9, pan_of('w', t))
            hold('low', tuba, m + 12, t, t + d, v - 6, pan_of('w', t), rise=0.3, fall=1.5, gain=0.6)
