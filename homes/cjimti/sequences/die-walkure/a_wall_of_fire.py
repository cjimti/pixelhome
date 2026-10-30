"""A Wall of Fire: the rose-gold glow of her devotion still hangs over the rock as Brünnhilde makes her last
request. If she must sleep defenceless on the mountain for any man who finds her, then let terror guard her:
let fire ring the rock, so that only a hero who knows no fear can pass.

Loge's fire (Donington 20) answers her words before Wotan does: four quick climbing figures on the harp and the
violins, each one a scatter of little flames that flicker up at the corners of the porch and die away again.
Then she foretells the hero. Siegfried's strength (Donington 53) on a trumpet: a white-gold streak comes in at
the free end of Right and races along the wing toward her, twice, and the third time, broadly, with horns and a
timpani stroke, it reaches the rock and the whole house flashes gold. For a moment the fire she asks for is
sketched all round the porch, a flickering orange outline, and gone.

Wotan is moved. Love as fulfilment (Donington 90) in the cellos and trombones: his blue swells out of him and
across the whole roof like an embrace, silver at its heart; the second time, an octave up in the violins and
horns, it fills the house to the ends. He will do it. The theme a last time on a clarinet, softly, and the two
of them stand together on the darkening rock.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK26'
TITLE = 'A Wall of Fire'
KIND = 'show'
DESCRIPTION = ('Brünnhilde makes one last request: if she must sleep on the mountain, let a wall of fire guard '
               'her, so that only a true hero can ever reach her. She sees that hero coming, and her father, '
               'moved at last, agrees.')
VOICEOVER = ('If she must sleep, she will not sleep unguarded. '
             'Listen to what she asks for, and to the hero she already hears coming.')

LOGES = [(8.0, 0), (12.0, 3), (16.0, 6), (20.0, 9)]         # Loge's figure: (start, transpose)
LGBEAT = 0.3
SIEGS = [(24.0, 0.55, 0), (28.0, 0.55, 5), (33.0, 0.85, 0)]  # Siegfried foretold: (start, beat, transpose)
T_SKETCH = 41.0                                             # the ring of fire, sketched and gone
LOVES = [(47.0, 1.1, 'low'), (55.0, 1.1, 'high'), (64.0, 1.2, 'soft')]   # love as fulfilment
D = 80.0
T0 = 80.0 * 25                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
HERO = hexc('#fff0a0')
ROSE = hexc('#ff5a8a')
EMBRACE = hexc('#3050ff')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
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


def heat(d, ta):
    """Flame heat along the roofline (about 0..1): tongues running both ways at different speeds."""
    return (0.5 + 0.22 * np.sin(2 * np.pi * (d / 97 - 1.9 * ta)) + 0.18 * np.sin(2 * np.pi * (d / 53 + 2.7 * ta) + 1.3)
            + 0.1 * np.sin(2 * np.pi * (d / 31 - 4.3 * ta) + 2.1))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('E2', 'B2', 'E3', 'Ab3', 'B3'):              # the end of her plea, still ringing
        add(0.0, 6.0, m, 52, 'bed')
    for m in ('Bb1', 'F2', 'Bb2', 'D3'):                    # she asks: B flat, uneasy
        add(5.0, 18.5, m, 54, 'bed')
    add(5.0, 18.5, 'E3', 46, 'bed')
    for k, (t0, tr) in enumerate(LOGES):
        for t, m, v, d in play('loge', t0, LGBEAT, tr + 12, 80 + 4 * k):
            add(t, d, m, v, 'loge', k)
        add(t0, 0.15, 'C6', 70 + 4 * k, 'glock', k)
    for k, (t0, beat, tr) in enumerate(SIEGS):
        for t, m, v, d in play('siegfried', t0, beat, tr - 12 * (k == 2), 104 + 8 * k):
            add(t, d, m, v, 'sieg', k)
        root = ('G2', 'C3', 'G2')[k]
        for m in (root, note(root) + 7, note(root) + 12, note(root) + 16):
            add(t0, 4 * beat + 0.6, m, 70 + 10 * k, 'siegbed')
    add(SIEGS[2][0] + 2 * SIEGS[2][1], 2.0, 'G2', 120, 'hit')
    add(SIEGS[2][0], 2 * SIEGS[2][1], 'G2', 92, 'roll')
    for t, m, v, d in play('loge', T_SKETCH, 0.25, 12, 82):
        add(t, d, m, v, 'loge', 4)
    for t, m, v, d in play('loge', T_SKETCH + 0.8, 0.25, 15, 78):
        add(t, d, m, v, 'loge', 4)
    for k, (t0, beat, kind) in enumerate(LOVES):
        tr = 12 if kind == 'high' else 0
        for t, m, v, d in play('love_fulfilled', t0, beat, tr, {'low': 98, 'high': 104, 'soft': 88}[kind]):
            add(t, d, m, v, 'love', kind)
        for b, ms, dur in ((0, ('C2', 'G2', 'E3', 'B3'), 3), (3, ('D2', 'A2', 'Gb3', 'C4'), 3),
                           (6, ('G1', 'G2', 'D3', 'B3'), 2.5 if kind != 'soft' else 8)):
            dur = min(dur, (D - 0.6 - t0) / beat - b)
            for m in ms:
                add(t0 + b * beat, dur * beat, m, {'low': 62, 'high': 72, 'soft': 60}[kind], 'lovebed')
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
    """Per frame: where Wotan, Brünnhilde and the foretold hero's streak are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = {k: np.zeros(F) for k in 'wb'}
    rate = {k: np.full(F, 2.0) for k in 'wb'}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('w', 0, D, at(G, 'Porch Front', 0.36), 2.0)
    set_('b', 0, D, at(G, 'Porch Front', 0.47), 2.0)
    set_('b', SIEGS[0][0] - 1, LOVES[0][0], at(G, 'Porch Front', 0.5), 0.6)
    set_('b', LOVES[0][0], D, at(G, 'Porch Front', 0.47), 0.4)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    corners = [d[G.path[i]] for i in (179, 260, 331, 380)]
    tw = Flicker(np.random.default_rng(2501), G.N, 1.5, 5.0)            # shared with WK25
    fl = Flicker(np.random.default_rng(2601), G.N, 4.0, 11.0)
    loges = [[e[0] for e in N if e[4] == 'loge' and e[5] == k] for k in range(5)]
    sieg = [np.array([e[0] for e in N if e[4] == 'sieg' and e[5] == k]) for k in range(3)]
    lnotes = np.array([e[0] for e in N if e[4] == 'love'])
    t_hit = [e[0] for e in N if e[4] == 'hit'][0]

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        devo = 1 - smoothstep(0, 8, t)                    # the devotion glow from WK25, fading
        emb = smoothstep(LOVES[0][0], LOVES[0][0] + 3, t) * (1 - 0.4 * smoothstep(LOVES[1][0] + 4, LOVES[2][0] + 2, t)
                                                             ) * (1 - 0.6 * smoothstep(70, D, t))
        soft = 0.55 + 0.2 * smoothstep(LOVES[0][0], LOVES[1][0], t)
        warmth = 0.6 + 0.1 * smoothstep(LOVES[0][0], LOVES[1][0], t)

        if devo > 0:
            mid = 0.5 * (pw + pb)
            br = 0.55 + 0.45 * np.sin(2 * np.pi * (np.abs(d - mid) / 700 - 0.11 * ta))
            fr *= 1 - 0.45 * 0.65 * devo
            fr += light(ROSE, 0.65 * devo * 0.3 * br)
            fr += light(GLINT, 0.65 * devo * 0.2 * br ** 3 * (0.7 + 0.3 * tw(ta)))
            lo, hi = min(pw, pb), max(pw, pb)
            fr += light(mix(WOTAN_SOFT, WARM, 0.5),
                        ((d > lo) & (d < hi)) * devo * (0.25 + 0.15 * np.sin(2 * np.pi * (d / 40 - 0.6 * ta))))

        # Loge's flickers: flames that leap up at the corners of the porch and die back
        hh = heat(d, ta)
        cmask = np.clip(sum(np.exp(-((d - c) / 110) ** 2) for c in corners), 0, 1)
        for k, ts in enumerate(loges[:4]):
            if ts and ts[0] <= t < ts[0] + 2.6:
                age = t - ts[0]
                a = smoothstep(0, 0.4, age) * (1 - smoothstep(0.9, 2.6, age)) * (0.6 + 0.12 * k)
                q = np.clip(hh + 0.12 * fl(ta) - 0.1 + 0.2 * smoothstep(0, 0.5, age) * (1 - age / 2.6), 0, 1)
                fr += light(FIRE(q), a * cmask * (0.45 + 0.75 * q))
        if loges[4] and T_SKETCH <= t < T_SKETCH + 4.5:
            age = t - T_SKETCH
            reach = 420 * smoothstep(0, 1.2, age)
            dd = np.min(np.abs(d[:, None] - np.array(corners)[None, :]), axis=1)
            a = smoothstep(reach + 40, reach - 40, dd) * porch * (1 - smoothstep(1.8, 4.5, age))
            q = np.clip(hh + 0.12 * fl(ta) - 0.05, 0, 1)
            fr += light(FIRE(q), 0.8 * a * (0.45 + 0.65 * q))

        # Siegfried foretold: a white-gold streak from the free end of Right toward her
        for k in range(3):
            if not len(sieg[k]):
                continue
            t0, t1 = sieg[k][0], sieg[k][-1] + 0.6
            if t0 <= t < t1 + 1.5:
                u = np.clip((t - t0) / (t1 - t0), 0, 1)
                target = pb if k == 2 else L - 520 * (k + 1)
                q = L + (target - L) * u ** 0.8
                head = np.exp(-((d - q) / 26) ** 2)
                trail = (d > q) * np.exp(-(d - q) / (220 + 160 * k))
                fade = 1 - smoothstep(t1, t1 + 1.5, t)
                n = recent(sieg[k], t, 0.15)
                fr += light(HERO, fade * ((0.95 + 0.1 * n) * head + (0.5 + 0.3 * n) * trail))
                fr += light(GLINT, fade * 0.35 * np.exp(-((d - q) / 160) ** 2))
        if t_hit <= t < t_hit + 2.0:
            a = np.exp(-(t - t_hit) / 0.35)
            fr += light(GLINT, 0.8 * a * np.ones(G.N)) + light(HERO, 0.5 * a * np.exp(-((d - pb) / 300) ** 2))

        # Wotan's embrace: his blue swelling over the house, silver at its heart, pulsing with the theme
        if emb > 0:
            ln = recent(lnotes, t, 0.8)
            wide = 300 + 1500 * smoothstep(LOVES[0][0], LOVES[1][0] + 3, t)
            mid = 0.5 * (pw + pb)
            g = np.exp(-((d - mid) / wide) ** 2)
            fr *= (1 - 0.3 * emb * g)[:, None]
            fr += light(EMBRACE, emb * (0.45 + 0.2 * ln) * g * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 0.2 * ta))))
            fr += light(SILVER, emb * (0.3 + 0.2 * ln) * np.exp(-((d - mid) / 70) ** 2))

        # Wotan
        wc = mix(WOTAN, WOTAN_SOFT, soft)
        fr += light(wc, 0.85 * np.exp(-((d - pw) / 24) ** 2) + (0.3 + 0.1 * soft) * np.exp(-((d - pw) / (90 + 40 * soft)) ** 2))

        # Brünnhilde
        bc = mix(SILVER, WARM, warmth)
        fr += light(bc, 0.85 * np.exp(-((d - pb) / 20) ** 2) + 0.32 * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.13 - 0.04 * (1 - devo)) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, (0.6 - 0.15 * (1 - devo)) * gl)
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
    pl, pr = pan_at(at(G, 'Porch Left', 0.9)), pan_at(at(G, 'Porch Right', 0.1))
    rend = pan_at(G.length)

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    for name, gain, rev in (('strings', 0.19, 0.42), ('low', 0.19, 0.25), ('brass', 0.2, 0.38), ('winds', 0.22, 0.42),
                            ('harp', 0.19, 0.45), ('perc', 0.17, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')

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
            s = cb if m < note('C3') else va if m < note('D4') else vn
            hold('strings', s, m, t, t + d, v, -0.3 + 0.6 * ((m * 5) % 12) / 11, rise=1.5, fall=1.5, gain=0.7)
        elif part == 'loge':
            side = (pl, pr, pl, pr, pf)[who]
            M.add('harp', harp.play(m, v), t, 0.9, side)
            M.add('strings', vns.play(m, v - 12, dur=d, release=0.1), t, 0.6, -side)
        elif part == 'glock':
            M.add('perc', glock.play(m, v), t, 0.6, (pl, pr, pl, pr)[who])
        elif part == 'sieg':
            q = rend + (pf - rend) * min(1.0, (t - SIEGS[who][0]) / (4 * SIEGS[who][1]))
            M.add('brass', tpt.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, q)
            if who == 2:
                M.add('brass', horn.play(m - 12, v - 8, dur=d * 1.1, release=0.4), t, 0.9, q - 0.2)
        elif part == 'siegbed':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d, release=0.6), t, 0.8, 0.0)
            else:
                M.add('brass', horn.play(m, v - 10, dur=d, release=0.6), t, 0.6, 0.2)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-3), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 0.8, pf)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.7, pf)
        elif part == 'love':
            pw = pan_of('w', t)
            if who == 'low':
                M.add('low', vc.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pw)
                M.add('brass', tbn.play(m, v - 10, dur=d * 1.05, release=0.6), t, 0.8, pw)
            elif who == 'high':
                M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.6), t, 1.0, pw - 0.2)
                M.add('brass', horn.play(m - 12, v - 6, dur=d * 1.05, release=0.6), t, 0.9, pw + 0.2)
            else:
                M.add('winds', cl.play(m + 12, v, dur=d * 1.05, release=0.6), t, 1.0, pan_of('b', t))
        elif part == 'lovebed':
            s = cb if m < note('C3') else va if m < note('C4') else vn
            hold('strings', s, m, t, t + d, v, pf + 0.25 * ((m % 3) - 1), rise=0.8, fall=1.5, gain=0.7)
