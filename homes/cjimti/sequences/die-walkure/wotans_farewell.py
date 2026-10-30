"""Wotan's Farewell: "Leb wohl, du kühnes, herrliches Kind!" A great E major chord from the whole orchestra and
the house flares blue and silver: Wotan takes his daughter in his arms for the last time.

His grief (Donington 82) in the trombones and cellos, in E, the horns under it: every long note a wave of his
deep blue rolling out from the two of them to both ends of the roofline, while her silver burns steady at the
heart of it. Then love as fulfilment (Donington 90c) soars in the violins and horns, up and up to its high E
flat: the glow builds over the whole house, and at each peak of the line the roof flashes silver-white, the
emotional summit of the whole opera, before it settles.

Tenderly, her love in its second form (Donington 87a) on a horn over the strings in G: Wotan moves to her and
his blue folds round her silver until the two lights are one, the house breathing slow blue and silver around
them. To close, love as fulfilment once more on an oboe, softly, and the glow sinks back to the two figures
holding each other on the rock at evening.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK27'
TITLE = "Wotan's Farewell"
KIND = 'show'
DESCRIPTION = ('Wotan takes his daughter in his arms for the last time and says goodbye. His deep blue folds '
               'around her silver and the whole house glows with the two of them: the great farewell, the heart '
               'of the whole opera.')
VOICEOVER = ('Farewell, you brave and glorious child. '
             'A father holds his daughter one last time.')

T_LEB = 2.0                                 # "Leb wohl!"
T_GRIEF = 4.5                               # Wotan's grief
GBEAT = 0.8
T_LFC = 28.0                                # love as fulfilment, soaring
FBEAT = 0.9
T_LOVEB = 42.0                              # her love, second form
LBEAT = 1.0
T_LFC2 = 63.5                               # love as fulfilment, softly
F2BEAT = 1.05
D = 80.0
T0 = 80.0 * 26                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
EMBRACE = hexc('#3050ff')
WHITE = hexc('#ffffff')
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

    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3', 'E4', 'Ab4'):
        add(T_LEB, 2.8, m, 116, 'leb')
    add(T_LEB, 2.0, 'E2', 124, 'hit')
    for t, m, v, d in play('wotan_grief', T_GRIEF, GBEAT, 0, 104):
        add(t, d, m, v, 'grief', 'w')
    for b, ms, dur in ((0, ('E2', 'B2', 'G3'), 4), (4, ('B1', 'Gb2', 'Eb3'), 8), (12, ('C2', 'G2', 'E3'), 4),
                       (16, ('D2', 'A2', 'F3'), 4), (20, ('A1', 'E2', 'C3'), 4), (24, ('E2', 'B2', 'Ab3'), 4.5)):
        for m in ms:
            add(T_GRIEF + b * GBEAT, dur * GBEAT, m, 74, 'griefbed')
    for t, m, v, d in play('love_fulfilled_c', T_LFC, FBEAT, 0, 112):
        add(t, d, m, v, 'soar')
    for b, ms, dur in ((0, ('A1', 'E2', 'A2', 'Db3', 'E3'), 3), (3, ('D2', 'A2', 'D3', 'Gb3'), 2),
                       (5, ('E2', 'B2', 'D3', 'Ab3'), 1), (6, ('B1', 'Gb2', 'A2', 'Eb3'), 2),
                       (8, ('E2', 'B2', 'E3', 'Ab3'), 1), (9, ('B1', 'Gb2', 'A2', 'Eb3'), 4)):
        for m in ms:
            add(T_LFC + b * FBEAT, dur * FBEAT, m, 86, 'soarbed')
    for b in (0, 3, 9):
        add(T_LFC + b * FBEAT, 1.5, 'E2' if b < 9 else 'B1', 108 + 6 * (b == 9), 'hit')
    add(T_LFC + 7 * FBEAT, 2 * FBEAT, 'B1', 96, 'roll')
    for t, m, v, d in play('brunnhilde_love_b', T_LOVEB, LBEAT, 0, 96):
        add(t, d, m, v, 'loveb', 'b')
    for b, ms, dur in ((0, ('Eb2', 'Bb2', 'G3'), 6), (6, ('G2', 'D3', 'B3'), 5), (11, ('C2', 'G2', 'E3'), 3),
                       (14, ('D2', 'A2', 'Gb3'), 2), (16, ('G2', 'D3', 'B3', 'G4'), 4.5)):
        for m in ms:
            add(T_LOVEB + b * LBEAT, dur * LBEAT, m, 66, 'lovebed')
    for t, m, v, d in play('love_fulfilled_c', T_LFC2, F2BEAT, -12, 84):
        add(t, d, m, v, 'soft', 'b')
    for m in ('A1', 'E2', 'A2', 'Db3', 'E3'):
        add(T_LFC2, 9 * F2BEAT, m, 58, 'softbed')
    for m in ('E2', 'B2', 'E3', 'Ab3'):
        add(T_LFC2 + 9 * F2BEAT, D - 0.6 - T_LFC2 - 9 * F2BEAT, m, 56, 'softbed')
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

    set_('w', 0, D, at(G, 'Porch Front', 0.36), 2.0)
    set_('w', T_LEB, T_LOVEB, at(G, 'Porch Front', 0.4), 1.0)
    set_('w', T_LOVEB, D, at(G, 'Porch Front', 0.45), 0.45)
    set_('b', 0, D, at(G, 'Porch Front', 0.47), 2.0)
    set_('b', T_LOVEB, D, at(G, 'Porch Front', 0.5), 0.45)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    tw = Flicker(np.random.default_rng(2701), G.N, 1.0, 4.0)
    grief = [(e[0], e[1]) for e in N if e[4] == 'grief']
    gt = np.array([g[0] for g in grief])
    gl_long = [g[0] for g in grief if g[1] >= 2.5 * GBEAT]
    soar = [(e[0], e[2]) for e in N if e[4] == 'soar']
    st = np.array([s[0] for s in soar])
    peaks = [s[0] for s in soar if s[1] >= note('A5')]
    lb = np.array([e[0] for e in N if e[4] in ('loveb', 'soft')])

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        mid = 0.5 * (pw + pb)
        dm = np.abs(d - mid)

        # the embrace: his blue over the whole house, carried over from WK26 and swelling with the farewell
        emb = (0.24 + 0.5 * smoothstep(T_LEB, T_LEB + 0.6, t) + 0.15 * smoothstep(T_LFC, T_LFC + 9, t)
               - 0.2 * smoothstep(T_LFC + 11, T_LOVEB + 4, t) - 0.45 * smoothstep(T_LFC2, D - 2, t))
        wide = 1800.0 - 900 * smoothstep(T_LFC2, D - 2, t)
        g = np.exp(-(dm / wide) ** 2)
        fr *= (1 - 0.3 * emb * g)[:, None]
        fr += light(EMBRACE, emb * 0.45 * g * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 0.2 * ta))))
        fr += light(SILVER, emb * 0.3 * np.exp(-(dm / 70) ** 2))

        # "Leb wohl!": the flare
        if T_LEB <= t < T_LEB + 3:
            a = 0.6 * np.exp(-(t - T_LEB) / 0.35) + 0.4 * np.exp(-(t - T_LEB) / 1.2)
            fr += light(EMBRACE, 0.85 * a * np.ones(G.N)) + light(SILVER, 0.75 * a * np.exp(-(dm / 600) ** 2))

        # his grief: each long note a wave of deep blue rolling out to both ends
        for ts in gl_long:
            if ts <= t < ts + 3.5:
                age = t - ts
                r = 1500 * smoothstep(0, 3.0, age)
                band = np.exp(-((dm - r) / 200) ** 2) * (1 - age / 3.5)
                fr += light(WOTAN, 0.75 * band) + light(WOTAN_SOFT, 0.3 * band ** 2)
        gp = recent(gt, t, 0.5)

        # the soaring: the glow builds over the whole house; silver-white flashes at the peaks
        soarl = (0.5 + 0.5 * smoothstep(T_LFC + 2, T_LFC + 9, t)) * smoothstep(T_LFC - 0.5, T_LFC + 1.5, t) * (1 - smoothstep(T_LFC + 11, T_LOVEB + 3, t))
        if soarl > 0:
            sp = recent(st, t, 0.4)
            i = max(int(np.searchsorted(st, t, side='right')) - 1, 0)
            reach = 250 + 1500 * np.clip((soar[i][1] - note('B4')) / (note('Eb6') - note('B4')), 0, 1)
            fill = smoothstep(reach + 200, reach - 200, dm)
            wv = 0.6 + 0.4 * np.sin(2 * np.pi * (dm / 500 - 0.35 * ta))
            fr *= (1 - 0.4 * soarl * fill)[:, None]
            fr += light(SILVER, soarl * (0.55 + 0.3 * sp) * wv ** 2 * fill) + light(EMBRACE, soarl * 0.65 * (1 - wv ** 2) * fill)
            fr += light(WOTAN, soarl * 0.35 * (1 - fill))
            fr += light(GLINT, soarl * 0.5 * (rng.random(G.N) < 0.05) * fill)
        for ts in peaks:
            if ts <= t < ts + 1.5:
                a = np.exp(-(t - ts) / 0.3)
                fr += light(WHITE, 0.85 * a * np.ones(G.N)) + light(SILVER, 0.5 * np.exp(-(t - ts) / 0.8) * np.ones(G.N))

        # tender: the house breathing slow blue and silver round them
        tender = smoothstep(T_LOVEB - 2, T_LOVEB + 3, t) * (1 - 0.7 * smoothstep(T_LFC2, D - 2, t))
        if tender > 0:
            lp = recent(lb, t, 0.9)
            br = 0.5 + 0.5 * np.sin(2 * np.pi * (dm / 900 - 0.07 * ta))
            fr += light(mix(SILVER, WARM, 0.4), tender * (0.12 + 0.1 * lp) * br ** 2 * (1 - 0.5 * porch))
            fr += light(WOTAN, tender * 0.38 * (1 - br) * (0.6 + 0.4 * tw(ta)))

        # Wotan and Brünnhilde
        wc = mix(WOTAN, WOTAN_SOFT, 0.75)
        fr += light(wc, (0.85 + 0.15 * gp) * np.exp(-((d - pw) / (24 + 10 * gp)) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))
        bc = mix(SILVER, WARM, 0.7)
        fr += light(bc, 0.85 * np.exp(-((d - pb) / 20) ** 2) + 0.32 * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.09) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, 0.45 * gl)
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

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    for name, gain, rev in (('strings', 0.17, 0.45), ('low', 0.17, 0.28), ('brass', 0.17, 0.4), ('winds', 0.2, 0.45),
                            ('perc', 0.15, 0.38)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
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
        if part == 'leb':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d, release=1.0), t, 1.0, pf)
                hold('low', cb, m + 12 * (m < note('E2')), t, t + d, v - 10, pf, rise=0.05, fall=1.5, gain=0.7)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d, release=1.0), t, 0.9, pf - 0.15)
                M.add('brass', horn.play(m + 12, v - 6, dur=d, release=1.0), t, 0.8, pf + 0.15)
            else:
                M.add('strings', vn.play(m, v, dur=d, release=1.0), t, 0.9, -0.4 + 0.8 * ((m * 7) % 12) / 11)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-2), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 0.8 if v > 115 else 0.5, pf)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, pf)
            M.add('perc', cym.play(84), t - 1.0, 0.5, pf)
        elif part == 'grief':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pan_of('w', t))
            M.add('low', vc.play(m, v - 8, dur=d * 1.05, release=0.6), t, 0.8, pan_of('w', t) - 0.2)
        elif part == 'griefbed':
            if m < note('C3'):
                hold('low', cb, m, t, t + d, v, pf, rise=0.4, fall=1.2, gain=0.8)
                M.add('low', tuba.play(m, v - 14, dur=d, release=0.8), t, 0.5, pf)
            else:
                hold('brass', horn, m, t, t + d, v - 10, pf + 0.3, rise=0.5, fall=1.2, gain=0.55)
                hold('strings', va, m, t, t + d, v - 6, pf - 0.3, rise=0.5, fall=1.2, gain=0.6)
        elif part == 'soar':
            M.add('strings', vn.play(m, v, dur=d * 1.08, release=0.7), t, 1.1, -0.25)
            M.add('strings', vn.play(m - 12, v - 10, dur=d * 1.08, release=0.7), t, 0.8, 0.25)
            M.add('brass', horn.play(m - 12, v - 6, dur=d * 1.05, release=0.6), t, 0.9, pf)
            if m >= note('A5'):
                M.add('brass', tpt.play(m - 12, v - 8, dur=d, release=0.6), t, 0.7, pf + 0.2)
        elif part == 'soarbed':
            if m < note('C3'):
                hold('low', cb, m + 12 * (m < note('C2')), t, t + d, v, pf, rise=0.2, fall=1.0, gain=0.8)
                M.add('low', tuba.play(m, v - 10, dur=d, release=0.6), t, 0.6, pf)
            else:
                hold('strings', va if m < note('A3') else vc, m, t, t + d, v - 4, -0.3 + 0.6 * ((m * 5) % 12) / 11,
                     rise=0.2, fall=1.0, gain=0.6)
                M.add('brass', tbn.play(m, v - 14, dur=d, release=0.6), t, 0.5, pf)
            if m == note('A2') or m == note('Gb2') or m == note('B2'):
                for i, x in enumerate((m, m + 7, m + 12, m + 16, m + 19, m + 24)):
                    M.add('strings', harp.play(x + 12, 84), t + 0.08 * i, 0.9, -0.6 + 0.24 * i)
        elif part == 'loveb':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pan_of('b', t))
            M.add('strings', vn.play(m, v - 22, dur=d * 1.05, release=0.6), t, 0.5, pan_of('w', t))
        elif part == 'lovebed':
            s = cb if m < note('C3') else va if m < note('D4') else vn
            hold('strings', s, m, t, t + d, v, pf + 0.25 * ((m % 3) - 1), rise=1.0, fall=1.4, gain=0.75)
        elif part == 'soft':
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pan_of('b', t))
        elif part == 'softbed':
            s = cb if m < note('C3') else va
            hold('strings', s, m, t, t + d, v, pf + 0.25 * ((m % 3) - 1), rise=1.5, fall=1.5, gain=0.7)
