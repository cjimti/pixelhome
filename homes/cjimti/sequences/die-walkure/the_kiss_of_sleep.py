"""The Kiss of Sleep: the farewell's last great surge, then Wotan bends over his daughter and kisses her eyes.

The music is Wagner's own: Act III, bars 1568 to 1576, the orchestral climax of the farewell, then bars 1613 to
1621, "so küßt er die Gottheit von dir", the kiss and the magic sleep sinking chord by chord, as Solti's 1958
Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction of the
score (pixelhome/ring.py), orchestrated by hand and register: the climax on the full orchestra (violins, flutes and
piccolo above, horns, trombones and trumpets in the middle, cellos, basses and tuba below, timpani on the bass
accents); the kiss on a glockenspiel and the harp over soft strings; the sleep's chords on the woodwinds, flutes
over oboes over clarinets over bassoons, with the harp. Over it the stage adds what the house shows: the mountain
wind and cymbals in the climax; at the kiss a shimmer of bell tree and glockenspiel over a soft gong; a chime for
each glint of her godhood drifting away, toward the end it drifts to; a bowed cymbal under the violet tide; a soft
gong under each ripple of the sleep; a thud as he lays her down; the shield scraping over her and ringing as it
settles. The effects sit back under the climax and leave Wotan's line clear; the kiss's shimmer and the shield are
the staged moments, and even they stay gentle under the sleep's chords; the effects come forward only for her
being laid down and the shield.

The lights follow the real notes. Through the climax the whole house surges blue and silver with the orchestra,
every loud high note a silver-white flash, every bass accent a wave of his blue rolling out to both ends. As Wotan
sings the glow draws in round the two of them; at the kiss a white spark at her face, and with each soft note
after it a gold glint, her godhood, comes loose and drifts away along the roofline to an end of the house while a
slow violet tide washes out across the house and back. Then the sleep: with every chord a violet ripple runs out
from her, her light dims a step and turns from silver toward a sleeping violet. Wotan lays her down, her light
sinking and spreading at the summit, the very middle of Porch Front, and covers her with her shield, a cool
steel-silver arc that glides over her and settles, glinting.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK28'
TITLE = 'The Kiss of Sleep'
KIND = 'show'
DESCRIPTION = ('Wotan kisses his daughter\'s eyes, and her godhood leaves her. Her bright silver fades to a '
               'sleeping violet, he lays her down on the summit of the rock and covers her with her shield.')
VOICEOVER = ('One kiss on each eye, and the warrior becomes a sleeper. '
             'Watch her light change, and her gold drift away.')

EX = excerpt(__file__)                      # Act III, bars 1568-1576 and 1613-1621, Solti 1958
BAR = {}
for m, t in EX['bars']:
    BAR.setdefault(int(m), t)
T_SPLICE = EX['segments'][1]['start']       # "so küßt er die Gottheit von dir"
T_KISS = BAR[1614]                          # the kiss
T_SLEEP = BAR[1617]                         # the magic sleep, chord by chord
T_LAY = BAR[1619]                           # he lays her down
T_SHIELD = BAR[1620]                        # and covers her with her shield
D = EX['seconds']
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
    s = smoothstep(T_KISS, T_SLEEP, t) * 0.4 + smoothstep(T_SLEEP, T_LAY + 2, t) * 0.6
    lay = smoothstep(T_LAY, T_LAY + 4, t)
    c = mix(mix(SILVER, WARM, 0.7 * (1 - s)), mix(VIOLET, SILVER, 0.2), s)
    return c, 0.85 - 0.2 * s - 0.12 * lay, 20 + 6 * lay, 0.32 - 0.04 * lay, 80 - 10 * lay, 0.45 * (1 - s)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). In the climax 'bass' is the
    left hand below C3, 'high' the right hand from C#6 up, 'line' the rest of the right hand, 'mid' the rest of the
    left; then 'sing' under Wotan's line, 'kiss' the soft notes after the kiss, 'sleep' the sleep's chords."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_SPLICE - 0.01:
            part = ('high' if m >= 85 else 'line') if h == 0 else ('bass' if m < 48 else 'mid')
        else:
            part = 'sing' if t < T_KISS - 0.01 else 'kiss' if t < T_SLEEP - 0.01 else 'sleep'
        N.append((t, d, m, v, part, h))
    return N


def energy(N, F):
    """Per frame: how loud and busy the orchestra is, 0..1 (velocity-weighted notes, smoothed)."""
    e = np.zeros(F)
    for t, d, m, v, part, h in N:
        f0, f1 = int(t / DT), int(min(t + max(d, 0.15), D) / DT) + 1
        e[f0:f1] += (v / 127) ** 2 / max(1, f1 - f0) ** 0.5
    k = np.exp(-np.arange(-40, 41) ** 2 / (2 * 14 ** 2))
    e = np.convolve(e, k / k.sum(), 'same')
    return np.clip(e / np.percentile(e, 97), 0, 1)


def accents(ts, gap):
    """Onsets at least gap seconds apart."""
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


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
    set_('w', T_SPLICE, D, at(G, 'Porch Front', 0.47), 0.8)
    set_('w', T_SLEEP, D, at(G, 'Porch Front', 0.4), 0.5)
    set_('w', T_SHIELD + 2, D, at(G, 'Porch Front', 0.3), 0.8)
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
    E = energy(N, F)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    tw = Flicker(np.random.default_rng(2701), G.N, 1.0, 4.0)            # shared with WK27
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)
    waves = accents([e[0] for e in N if e[4] == 'bass' and e[3] >= 80], 0.9)
    peaks = accents([e[0] for e in N if e[4] == 'high' and e[3] >= 95], 0.45)
    onsets = np.array(sorted({round(e[0], 2) for e in N if e[0] < T_SPLICE}))
    chords = np.array(accents([e[0] for e in N if e[4] == 'sleep'], 0.4))
    # her godhood: a gold glint leaves her with each soft note after the kiss (and each chord of the sleep)
    loose = accents([e[0] for e in N if e[4] in ('kiss', 'sleep')], 0.3)
    gd = [(tc, (-1) ** i, 0.6 + 0.35 * rng.random()) for i, tc in enumerate(loose)]

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        e = E[f]
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        mid = 0.5 * (pw + pb)
        dm = np.abs(d - mid)
        db = np.abs(d - pb)

        # the climax: the embrace over the whole house, as wide and bright as the orchestra is loud
        cl = 1 - smoothstep(T_SPLICE - 3, T_KISS, t)
        if cl > 0:
            hit = recent(onsets, t, 0.18, 1.0)
            wide = 500 + 1600 * e
            g = np.exp(-(dm / wide) ** 2)
            emb = cl * (0.2 + 0.6 * e)
            fr *= (1 - 0.45 * emb * g)[:, None]
            wv = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 - (0.2 + 0.4 * e) * ta))
            fr += light(EMBRACE, emb * (0.5 + 0.15 * hit) * g * wv)
            fr += light(SILVER, emb * 0.35 * np.exp(-(dm / (70 + 200 * e)) ** 2))
            r = 1700 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.7 - np.pi / 2))
            fill = smoothstep(r + 250, r - 250, dm)
            fr += light(SILVER, cl * e * (0.25 + 0.3 * hit) * fill) + light(WOTAN, cl * e * 0.4 * (1 - fill))
            br = 0.5 + 0.5 * np.sin(2 * np.pi * (dm / 900 - 0.07 * ta))
            fr += light(WOTAN, cl * 0.3 * (1 - br) * (0.6 + 0.4 * tw(ta)))
        for ts in waves:
            if ts <= t < ts + 3.0:
                age = t - ts
                r = 1600 * smoothstep(0, 2.6, age)
                band = np.exp(-((dm - r) / 180) ** 2) * (1 - age / 3.0)
                fr += light(WOTAN, 0.8 * band) + light(WOTAN_SOFT, 0.3 * band ** 2)
        for ts in peaks:
            if ts <= t < ts + 1.2:
                a = np.exp(-(t - ts) / 0.25)
                fr += light(WHITE, 0.8 * a * np.exp(-(dm / 900) ** 2)) + light(SILVER, 0.4 * np.exp(-(t - ts) / 0.7) * np.ones(G.N))

        # Wotan's line: the glow draws in round the two of them
        if T_SPLICE - 3 <= t < T_KISS + 3:
            u = smoothstep(T_SPLICE - 3, T_SPLICE + 2, t) * (1 - smoothstep(T_KISS, T_KISS + 3, t))
            g = np.exp(-(dm / (900 - 500 * smoothstep(T_SPLICE, T_KISS, t))) ** 2)
            fr += light(EMBRACE, u * 0.8 * g * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 300 - 0.15 * ta))))

        # after the kiss: a slow violet tide out across the house and back, until the sleep
        trl = smoothstep(T_KISS, T_KISS + 2, t) * (1 - smoothstep(T_SLEEP + 2, T_LAY, t))
        if trl > 0:
            u = np.clip((t - T_KISS) / (T_SLEEP - T_KISS), 0, 1)
            r = 1700 * np.sin(np.pi * u)
            tide = smoothstep(r + 250, r - 250, db)
            fr *= (1 - 0.35 * trl * tide)[:, None]
            fr += light(VIOLET, trl * 0.5 * tide * (0.75 + 0.25 * np.sin(2 * np.pi * (db / 160 - 0.5 * ta))))
            fr += light(SILVER, trl * 0.55 * np.exp(-((db - r) / 60) ** 2))

        # the sleep: each chord a violet ripple out from her
        cp = recent(chords, t, 0.8)
        i = int(np.searchsorted(chords, t, side='right')) - 1
        if i >= 0 and t - chords[i] < 3.0:
            age = t - chords[i]
            band = np.exp(-((db - 1100 * age / 3.0) / 200) ** 2) * (1 - age / 3.0)
            fr += light(VIOLET, 0.6 * band) + light(FATE_HI, 0.3 * band * (1 - porch))
        for tg, side, sp in gd:
            if tg <= t < tg + 4.0:
                age = t - tg
                q = pb + side * (L * 0.62) * sp * (age / 4.0) ** 0.7
                fr += light(GLINT, 0.95 * (1 - age / 4.0) * np.exp(-((d - q) / 15) ** 2))

        # the kiss
        if T_KISS <= t < T_KISS + 2.5:
            a = np.exp(-(t - T_KISS) / 0.6)
            fr += light(WHITE, 0.95 * a * np.exp(-(db / 12) ** 2)) + light(SILVER, 0.35 * a * np.exp(-(db / 300) ** 2))

        # the shield: a steel-silver arc that glides over her from Wotan and settles, glinting
        shl = smoothstep(T_SHIELD, T_SHIELD + 2.0, t)
        if t >= T_SHIELD:
            c = pw + (pb - pw) * shl
            arc = np.exp(-((d - c) / (34 * (0.6 + 0.4 * shl))) ** 4)
            glint = (rng.random(G.N) < 0.06) * arc
            fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * glint)
            if t < T_SHIELD + 3:
                fr += light(SHIELD, 0.5 * np.exp(-(t - T_SHIELD - 2.0) ** 2 / 0.1) * np.exp(-(db / 200) ** 2))

        # Wotan
        wc = mix(WOTAN, WOTAN_SOFT, 0.75 - 0.25 * smoothstep(T_SLEEP, D, t))
        fr += light(wc, 0.85 * np.exp(-((d - pw) / 24) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))

        # Brünnhilde, falling asleep
        bc, core, cw, halo, hw, glv = sleeper(t)
        fr += light(bc, (core + 0.1 * cp) * np.exp(-(db / cw) ** 2) + halo * np.exp(-(db / hw) ** 2))
        if glv > 0.01:
            gl = (rng.random(G.N) < 0.09) * np.exp(-(db / 40) ** 2)
            fr += light(GLINT, glv * gl)
        out[f] = fr
    return np.clip(out, 0, 1)


def house_pan(G):
    """Path distance -> left/right across the facade, as heard from the street."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    return lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the full orchestra for the climax, then the kiss on
    glockenspiel and harp over soft strings, and the sleep's chords on the woodwinds and harp. Over it, what the house
    shows: wind, swells and crashes in the climax, the kiss's shimmer, a chime for every glint of her godhood
    drifting away, a soft gong under each ripple of sleep, and the shield sliding over her and settling."""
    o = Orchestra(M, level=3.2)
    pan_at = house_pan(G)
    C = choreography(G)
    N = compose()
    L = G.length
    pb = at(G, 'Porch Front', 0.5)
    bp = pan_at(pb)

    def role(t, d, m, v, h):
        if t < T_SPLICE - 0.01:
            return None
        if t < T_SLEEP - 0.01:                                  # Wotan's line and the kiss: strings, harp, glock
            parts = [('violins' if m >= 55 else 'violas' if m >= 48 else 'cellos', 0, 10, 0.6)]
            if h == 0 and t >= T_KISS - 0.01:
                parts += [('harp', 0, 30, 0.6), ('glock', 0, 20, 0.35) if m >= 60 else ('harp', 12, 20, 0.4)]
            return parts
        sec = 'flutes' if m >= 72 else 'oboes' if m >= 64 else 'clarinets' if m >= 55 else 'bassoons' if m >= 46 else 'cellos'
        return [(sec, 0, 22, 0.6), ('harp', 0, 20, 0.3)]

    o.tutti(EX['notes'], size=lambda t: 1.0, role=role)
    for t, d, m, v, part, h in N:
        if part == 'bass' and v >= 110:
            o.hit('timpani', t, v - 15, pitch=(m - 40) * 0.5, gain=0.4)
    o.hit('crash', BAR[1571], 105, gain=0.4)
    o.hit('timpani roll', T_SPLICE - 4, 70, gain=0.25)

    # the climax's wind sits back under the orchestra and is gone by Wotan's line, which must be clear; the kiss's
    # shimmer and the shield are the staged moments, kept gentle
    o.effects([(0, -9), (T_SPLICE - 3, -12), (T_SPLICE, -20), (T_LAY - 0.5, -20), (T_LAY, -4), (T_SHIELD + 3, -4),
               (T_SHIELD + 5, -20), (D, -20)])
    # the climax: the mountain wind, a timpani roll under each wave of blue, a crash on each white flash
    o.wind(0, T_KISS + 4, level=lambda tt: 0.7 - 0.5 * smoothstep(T_SPLICE - 3, T_KISS + 4, tt), pan=-0.3)
    for ts in accents([e[0] for e in N if e[4] == 'bass' and e[3] >= 80], 0.9):
        o.hit('timpani roll', ts, 82, pitch=-3, gain=0.35, pan=bp)
    for ts in accents([e[0] for e in N if e[4] == 'high' and e[3] >= 95], 0.45):
        o.hit('crash', ts, 96, gain=0.22, pan=bp)
    o.hit('cymbal swell', T_SPLICE - 4.5, 86, gain=0.25)

    # the kiss: a shimmer of bell tree and glockenspiel at her face, a soft gong under it
    tree = M.hits('Percussion/BellTree_Stroke*_v1_Sum.wav')
    M.add('perc', tree.play(110), T_KISS - 0.4, 0.6, bp)
    for k, m in enumerate((88, 91, 95)):
        o.play('glock', m, T_KISS + 0.07 * k, 0.4, 96, bp, 0.45)
    M.add('perc', M.hits('Percussion/gongHit_p.wav').play(100), T_KISS, 0.5, bp)
    # each glint of her godhood drifting away: a chime moving out toward its end of the house
    tri = M.hits('Percussion/Triangle6-Hit_v1*.wav')
    rng = np.random.default_rng(28)                             # the same draws render() makes
    loose = accents([e[0] for e in N if e[4] in ('kiss', 'sleep')], 0.3)
    for i, tc in enumerate(loose):
        side, sp = (-1) ** i, 0.6 + 0.35 * rng.random()
        pp = pan_at(pb + side * L * 0.62 * sp * 0.5)
        M.add('perc', tri.play(70 + 30 * (i % 3 == 0)), tc, 0.35, pp)
        o.play('glock', 84 + (i * 5) % 12, tc + 0.05, 0.3, 70, pp, 0.25)
    # the violet tide after the kiss: a bowed cymbal breathing out and back
    bow = M.hits('Percussion/susCymb1-bow-*.wav')
    M.add('perc', bow.play(100), T_KISS + 1.0, 0.45, bp - 0.3)
    M.add('perc', bow.play(90), 0.5 * (T_KISS + T_SLEEP), 0.4, bp + 0.3)
    # the sleep: a soft gong and a low timpani under each chord's ripple
    for tc in accents([e[0] for e in N if e[4] == 'sleep'], 0.4):
        M.add('perc', M.hits('Percussion/gongHit_p.wav').play(72), tc, 0.22, bp)
        o.hit('timpani', tc, 56, pitch=-7, gain=0.2, pan=bp)
    # he lays her down: a soft thud; the shield slides over her (a cymbal scrape) and settles (a ringing clang)
    o.hit('bass drum', T_LAY, 90, gain=0.45, pan=bp, fx=True)
    o.hit('timpani', T_LAY, 80, pitch=-8, gain=0.4, pan=bp, fx=True)
    o.hit('scrape', T_SHIELD, 100, gain=0.55, pan=pan_at(np.interp(T_SHIELD, C['t'], C['w'])), fx=True)
    o.hit('metal', T_SHIELD + 2.0, 96, gain=0.45, pan=bp, fx=True)
    o.hit('brake drum', T_SHIELD + 2.0, 80, gain=0.25, pan=bp, fx=True)
    M.add('perc', tri.play(110), T_SHIELD + 2.05, 0.4, bp)
