"""The Kiss of Sleep: the farewell's glow is still on the house as Wotan bends over his daughter and kisses her
eyes. A soft white spark at her face, and the magic sleep (Donington 16) begins its slow chromatic descent in
the woodwinds, chord by chord, from A flat down to C. With every chord her light dims a step and turns from
silver toward a sleeping violet, and her gold glints, her godhood, come loose one by one and drift away along
the roofline to both ends of the house, where they go out.

Transformation (Donington 91) in the violins over the harp: a slow tide of violet washes out from her across
the whole house and back again, and when it has passed she is no longer a Valkyrie. Wotan lays her down: her
light sinks lower and spreads, a still violet-silver glow at the summit, the very middle of Porch Front. He
covers her with her shield, a cool steel-silver arc that glides over her and settles, glinting.

The power of fate (Donington 84) on Wagner tubas, two long chords, each an indigo shadow passing over the
roof. Wotan steps back from her toward the left of the porch, and the evening deepens into night.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK28'
TITLE = 'The Kiss of Sleep'
KIND = 'show'
DESCRIPTION = ('Wotan kisses his daughter\'s eyes, and her godhood leaves her. Her bright silver fades to a '
               'sleeping violet, he lays her down on the summit of the rock and covers her with her shield.')
VOICEOVER = ('One kiss on each eye, and the warrior becomes a sleeper. '
             'Watch her light change, and her gold drift away.')

T_KISS = 5.0                                # the kiss
T_SLEEP = 6.0                               # the magic sleep, in the woodwinds
SBEAT = 0.9
T_TRANS = 25.5                              # Transformation
TBEAT = 0.8
T_LAY = 38.5                                # he lays her down
T_SHIELD = 51.0                             # and covers her with her shield
T_FATE = 59.0                               # the power of fate
FBEAT = 1.3
T_BACK = 71.0                               # he steps back
D = 80.0
T0 = 80.0 * 27                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
EMBRACE = hexc('#3050ff')
VIOLET = hexc('#7a6aff')
SHIELD = hexc('#c8d8ff')
FATE_HI = hexc('#4a2ab8')
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


def sleeper(t):
    """Brünnhilde's state: (colour, core level, core width, halo level, halo width, glint level)."""
    s = smoothstep(T_SLEEP, T_SLEEP + 20 * SBEAT, t)
    tr = smoothstep(T_TRANS, T_TRANS + 15 * TBEAT, t)
    lay = smoothstep(T_LAY, T_LAY + 6, t)
    c = mix(mix(SILVER, WARM, 0.7 * (1 - s)), mix(VIOLET, SILVER, 0.2), 0.6 * s + 0.4 * tr)
    return c, 0.85 - 0.2 * s - 0.12 * lay, 20 + 6 * lay, 0.32 - 0.04 * lay, 80 - 10 * lay, 0.45 * (1 - s)


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('E2', 'B2', 'E3', 'Ab3'):                     # the farewell, still sounding
        add(0.0, T_SLEEP + 1.0, m, 54, 'bed')
    add(T_KISS, 2.0, 'Ab5', 70, 'kiss')
    for t, m, v, d in play('sleep', T_SLEEP, SBEAT, 0, 84):
        add(t, d, m, v, 'sleep')
    for t, m, v, d in play('transformation', T_TRANS, TBEAT, 0, 88):
        add(t, d, m, v, 'trans')
    for b, ms, dur in ((0, ('G2', 'D3', 'B3'), 3), (3, ('C2', 'G2', 'E3'), 3), (6, ('D2', 'A2', 'Gb3'), 3),
                       (9, ('G2', 'D3', 'B3'), 3), (12, ('D2', 'A2', 'Gb3', 'C4'), 3)):
        for m in ms:
            add(T_TRANS + b * TBEAT, dur * TBEAT, m, 62, 'transbed')
        add(T_TRANS + b * TBEAT, 0.0, ms[0], 74, 'arp')
    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3'):              # laid down: E major, very still
        add(T_LAY, T_FATE - T_LAY + 0.5, m, 56, 'bed')
    for k in range(4):
        add(T_LAY + 3.0 * k, 0.0, 'E2', 66 - 3 * k, 'arp')
    add(T_SHIELD, 2.2, 'C4', 80, 'gliss')
    add(T_SHIELD, 3.0, 'E6', 64, 'kiss')
    for t, m, v, d in play('fate', T_FATE, FBEAT, 0, 92):
        add(t, d, m, v, 'fate')
    add(T_FATE, 9 * FBEAT, 'D2', 60, 'roll')
    for t, m, v, d in play('sleep', T_BACK + 0.5, 0.75, 0, 64, line='melody'):
        if t < D - 1.5:
            add(t, d, m, v, 'sleephi')
    for m in ('Ab2', 'Eb3', 'C4'):
        add(T_BACK + 0.5, D - T_BACK - 1.0, m, 50, 'bed')
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

    set_('w', 0, D, at(G, 'Porch Front', 0.45), 2.0)
    set_('w', T_TRANS, D, at(G, 'Porch Front', 0.38), 0.5)
    set_('w', T_BACK, D, at(G, 'Porch Front', 0.25), 1.0)
    set_('b', 0, D, at(G, 'Porch Front', 0.5), 2.0)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=28):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    tw = Flicker(np.random.default_rng(2701), G.N, 1.0, 4.0)            # shared with WK27
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)
    chords = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    trans = np.array([e[0] for e in N if e[4] == 'trans'])
    fates = np.array(sorted({e[0] for e in N if e[4] == 'fate'}))
    pb0 = at(G, 'Porch Front', 0.5)
    # her godhood: a gold glint leaves her with each chord of the sleep and drifts to an end of the house
    gd = [(tc + 0.15 * j, (-1) ** (i + j), 0.7 + 0.25 * rng.random()) for i, tc in enumerate(chords) for j in range(2)]

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
        db = np.abs(d - pb)

        # the farewell's glow, fading as the sleep comes
        emb = 0.24 * (1 - smoothstep(T_KISS, T_SLEEP + 8, t))
        tender = 0.3 * (1 - smoothstep(T_KISS, T_SLEEP + 6, t))
        if emb > 0:
            g = np.exp(-(dm / 900) ** 2)
            fr *= (1 - 0.3 * emb * g)[:, None]
            fr += light(EMBRACE, emb * 0.45 * g * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 0.2 * ta))))
            fr += light(SILVER, emb * 0.3 * np.exp(-(dm / 70) ** 2))
            br = 0.5 + 0.5 * np.sin(2 * np.pi * (dm / 900 - 0.07 * ta))
            fr += light(mix(SILVER, WARM, 0.4), tender * 0.12 * br ** 2 * (1 - 0.5 * porch))
            fr += light(WOTAN, tender * 0.38 * (1 - br) * (0.6 + 0.4 * tw(ta)))

        # the sleep: each chord a soft violet ripple out from her
        cp = recent(chords, t, 0.8)
        i = int(np.searchsorted(chords, t, side='right')) - 1
        if i >= 0 and t - chords[i] < 2.5:
            age = t - chords[i]
            band = np.exp(-((db - 900 * age / 2.5) / 180) ** 2) * (1 - age / 2.5)
            fr += light(VIOLET, 0.45 * band)
        for tg, side, sp in gd:
            if tg <= t < tg + 4.0:
                age = t - tg
                q = pb + side * (L * 0.62) * sp * (age / 4.0) ** 0.7
                fr += light(GLINT, 0.95 * (1 - age / 4.0) * np.exp(-((d - q) / 15) ** 2))

        # Transformation: a tide of violet out across the house and back
        trl = smoothstep(T_TRANS - 0.5, T_TRANS + 1.5, t) * (1 - smoothstep(T_TRANS + 15 * TBEAT - 1, T_LAY + 3, t))
        if trl > 0:
            u = np.clip((t - T_TRANS) / (15 * TBEAT), 0, 1)
            r = 1700 * np.sin(np.pi * u)
            tide = smoothstep(r + 250, r - 250, db)
            tp = recent(trans, t, 0.6)
            fr *= (1 - 0.35 * trl * tide)[:, None]
            fr += light(VIOLET, trl * (0.42 + 0.15 * tp) * tide * (0.75 + 0.25 * np.sin(2 * np.pi * (db / 160 - 0.5 * ta))))
            fr += light(SILVER, trl * 0.5 * np.exp(-((db - r) / 60) ** 2))

        # the kiss
        if T_KISS <= t < T_KISS + 2.0:
            a = np.exp(-(t - T_KISS) / 0.5)
            fr += light(WHITE, 0.9 * a * np.exp(-(db / 10) ** 2))

        # the shield: a steel-silver arc that glides over her from Wotan and settles, glinting
        shl = smoothstep(T_SHIELD, T_SHIELD + 2.0, t)
        if t >= T_SHIELD:
            c = pw + (pb - pw) * smoothstep(T_SHIELD, T_SHIELD + 2.0, t)
            arc = np.exp(-((d - c) / (34 * (0.6 + 0.4 * shl))) ** 4)
            glint = (rng.random(G.N) < 0.06) * arc
            fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * glint)
            if t < T_SHIELD + 3:
                fr += light(SHIELD, 0.5 * np.exp(-(t - T_SHIELD - 2.0) ** 2 / 0.1) * np.exp(-(db / 200) ** 2))

        # fate: indigo shadows over the roof
        fl = smoothstep(T_FATE - 0.5, T_FATE + 1, t) * (1 - smoothstep(T_FATE + 9 * FBEAT, D, t))
        if fl > 0:
            fp = recent(fates, t, 1.5, 6.0)
            tex = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 260 + 0.04 * ta)) * np.sin(2 * np.pi * (d / 610 - 0.03 * ta))
            fr *= 1 - 0.3 * fl * fp
            fr += light(FATE_HI, fl * (0.2 + 0.4 * fp) * tex * (1 - np.exp(-(db / 60) ** 2)))

        # Wotan
        wc = mix(WOTAN, WOTAN_SOFT, 0.75 - 0.25 * smoothstep(T_FATE, D, t))
        fr += light(wc, 0.85 * np.exp(-((d - pw) / 24) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))

        # Brünnhilde, falling asleep
        bc, core, cw, halo, hw, glv = sleeper(t)
        fr += light(bc, (core + 0.1 * cp) * np.exp(-(db / cw) ** 2) + halo * np.exp(-(db / hw) ** 2))
        if glv > 0.01:
            gl = (rng.random(G.N) < 0.09) * np.exp(-(db / 40) ** 2)
            fr += light(GLINT, glv * gl)
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

    for name, gain, rev in (('strings', 0.18, 0.45), ('low', 0.18, 0.28), ('brass', 0.15, 0.4), ('winds', 0.13, 0.45),
                            ('harp', 0.18, 0.5), ('perc', 0.14, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
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
        if part == 'bed':
            s = cb if m < note('C3') else va if m < note('C4') else vn
            hold('strings', s, m, t, t + d, v, pf + 0.25 * ((m % 3) - 1), rise=1.5, fall=2.0, gain=0.7)
        elif part == 'kiss':
            M.add('perc', glock.play(m, v), t, 0.7, pf)
        elif part == 'sleep':
            if m >= note('C5'):
                M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.6), t, 0.9, pf - 0.15)
            elif m >= note('Gb4'):
                M.add('winds', ob.play(m, v - 6, dur=d * 1.05, release=0.6), t, 0.8, pf + 0.15)
            elif m >= note('C4'):
                M.add('winds', cl.play(m, v - 4, dur=d * 1.05, release=0.6), t, 0.8, pf - 0.3)
            elif m >= note('C3'):
                M.add('winds', bsn.play(m, v - 6, dur=d * 1.05, release=0.6), t, 0.8, pf + 0.3)
            else:
                hold('low', vc, m + 12, t, t + d, v - 10, pf, rise=0.3, fall=0.8, gain=0.6)
        elif part == 'trans':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.7), t, 1.0, pf - 0.2)
            M.add('strings', vn.play(m - 12, v - 14, dur=d * 1.05, release=0.7), t, 0.7, pf + 0.2)
        elif part == 'transbed':
            s = cb if m < note('C3') else va
            hold('strings', s, m, t, t + d, v, pf + 0.25 * ((m % 3) - 1), rise=0.6, fall=1.0, gain=0.7)
        elif part == 'arp':
            for i, x in enumerate((m, m + 7, m + 12, m + 16, m + 19, m + 24, m + 28)):
                M.add('harp', harp.play(x + 12, v), t + 0.11 * i, 0.9, -0.5 + 0.17 * i)
        elif part == 'gliss':
            gl = [x for x in range(note('E4'), note('E6') + 1) if x % 12 in (4, 8, 11)]
            for i, x in enumerate(gl):
                M.add('harp', harp.play(x, 70 + 2 * i), t + i * d / len(gl), 0.8, pan_of('w', t) * (1 - i / len(gl)) + pf * i / len(gl))
            M.add('perc', cym.play(70), t - 1.0, 0.4, pf)
        elif part == 'fate':
            if m >= note('F3'):
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=1.0), t, 0.9, pf + 0.1 * ((m % 5) - 2))
            elif m >= note('C3'):
                M.add('brass', horn.play(m, v - 4, dur=d * 1.05, release=1.0), t, 0.8, pf)
                M.add('low', vc.play(m, v - 16, dur=d * 1.05, release=1.0), t, 0.5, pf)
            else:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=1.2), t, 1.0, pf)
                hold('low', cb, m + 12, t, t + d, v - 14, pf, rise=0.3, fall=1.5, gain=0.6)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.5, pf)
        elif part == 'sleephi':
            M.add('winds', fl.play(m, v, dur=d * 1.05, release=0.8), t, 0.8, pf)
