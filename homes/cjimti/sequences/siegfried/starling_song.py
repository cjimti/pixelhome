"""The Starling Song: Mime whines his nursery song of how he raised the boy (Mime's lament, Donington 72), oboe
and bassoon over a rocking pizzicato, and a broad wash of sulphur yellow rocks back and forth across the whole
house like a cradle, pulsing on every note. Three times Siegfried cuts him off: a horn stab, and an emerald slash
runs out from him to both ends of the roofline and snuffs the yellow out. The birds have mothers and fathers, he
says; where are mine?

Then he seizes Mime by the throat: his strength (53) on the horns, emerald closing round the yellow, Mime
shaking. Mime gives in. Siegmund's motif (35) rises in the cellos and horns, and Wälsung blue rolls out from the
porch over Left and Side: the father. Sieglinde's (36) follows on cellos and oboe, and hearth amber floods Right:
the mother, who died giving him birth, so it fades as her phrase sinks. Siegfried lets Mime go; blue and amber
run back together onto the porch and flare there as emerald, and the cave settles with him at the anvil's right
hand and Mime at its left.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF04'
TITLE = 'The Starling Song'
KIND = 'show'
DESCRIPTION = ('Mime whines about how he raised the boy, and Siegfried will not hear it. He wants to know who '
               'his parents were, and at last the dwarf tells him: Siegmund and Sieglinde.')
VOICEOVER = ('Every bird in the forest has a mother and a father. '
             'Siegfried wants to know: where are mine?')

K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
LAMENT_BEAT = 0.7
T_LAMENT = [1.5, 8.6, 15.7]                 # Mime's nursery song
T_CUT = [7.4, 14.5, 21.6]                   # Siegfried cuts him off
T_GRAB = 23.5                               # he seizes Mime
T_SM = [29.0, 39.5]                         # Siegmund's motif: the father
T_SL = [50.5, 59.5]                         # Sieglinde's: the mother
T_LET = 68.5                                # he lets Mime go
D = 80.0

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # the cave at every Act I cut
MIME_AT, HERO_AT = 0.32, 0.7                                       # their places on Porch Front


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: an emerald figure with a white-hot head."""
    fr = figure(fr, S, p, SIEGFRIED, lvl, w)
    return fr + light(HEAD, 0.9 * lvl * np.exp(-((S['d'] - p) / 5) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_LAMENT):
        for t, m, v, d in play('mime_lament', t0, LAMENT_BEAT, 0, 86 + 4 * k):
            add(t, d, m, v, 'lament', k)
        for j in range(8):                  # the cradle: a rocking pizzicato under it
            add(t0 + j * 2 * LAMENT_BEAT, 0.3, ('F2', 'C3')[j % 2], 72, 'rock', k)
    for k, t0 in enumerate(T_CUT):
        add(t0, 0.5, ('G3', 'A3', 'B3')[k], 112 + 4 * k, 'cut', k)
    for t, m, v, d in play('siegfried', T_GRAB, 0.75, -12, 120):
        add(t, d, m, v, 'grab')
    add(T_GRAB, 0.1, 'C1', 122, 'crash')
    add(T_GRAB + 2.5, T_SM[0] - T_GRAB - 2.5, 'A2', 70, 'trem')
    for k, t0 in enumerate(T_SM):
        for t, m, v, d in play('siegmund', t0, 0.55, 0, 96 - 6 * k):
            add(t, d, m, v, 'siegmund', k)
    for k, t0 in enumerate(T_SL):
        for t, m, v, d in play('sieglinde', t0, 0.6, 0, 92 - 10 * k):
            add(t, d, m, v, 'sieglinde', k)
    for t, m, v, d in play('siegfried_horn', T_LET + 1.0, 0.55, 0, 96):
        add(t, d, m, v, 'horn')
    for m in ('G2', 'D3', 'G3', 'B3'):
        add(T_LET + 4.5, D - T_LET - 4.5, m, 62, 'glow')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=4):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    p_mime, p_hero = at(G, 'Porch Front', MIME_AT), at(G, 'Porch Front', HERO_AT)
    p_grab = at(G, 'Porch Front', 0.42)
    lam_on = np.array(sorted({e[0] for e in N if e[4] == 'lament'}))
    sm_on = np.array(sorted({e[0] for e in N if e[4] == 'siegmund'}))
    sl_on = np.array(sorted({e[0] for e in N if e[4] == 'sieglinde'}))
    pl0, pr1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    father = np.clip((pl0 - d) / pl0, 0, 1)                    # 0 at the porch, 1 at the back of Side
    mother = np.clip((d - pr1) / (L - pr1), 0, 1)              # 0 at the porch, 1 at the free end of Right
    sm_end = T_SM[1] + 18 * 0.55
    sl_end = T_SL[1] + 15 * 0.6

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = cave(S, T, dict(LV))

        # the cradle: a wide yellow wash rocking across the house, pulsing on every note, snuffed at each cut
        song = 0.0
        for t0, tc in zip(T_LAMENT, T_CUT):
            song = max(song, smoothstep(t0 - 0.2, t0 + 0.8, t) * (1 - smoothstep(tc, tc + 0.15, t)))
        if song > 0:
            i = int(np.searchsorted(lam_on, t, side='right')) - 1
            pulse = np.exp(-(t - lam_on[i]) / 0.3) if i >= 0 else 0.0
            sway = np.sin(2 * np.pi * t / (4 * LAMENT_BEAT))
            centre = anvil + sway * 0.55 * L
            fr = fr * (1 - 0.4 * song)
            fr += light(MIME, song * (0.7 + 0.3 * pulse) * np.exp(-((d - centre) / 600) ** 2))

        # each cut: a horn stab, an emerald slash out from him to both ends
        for tc in T_CUT:
            a = t - tc
            if 0 <= a < 1.0:
                front = 2600 * a
                fr += light(SIEGFRIED, (np.abs(d - p_hero) < front) * np.exp(-a / 0.35) * 0.9)
                fr += light(HEAD, np.exp(-((np.abs(d - p_hero) - front) / 40) ** 2) * np.exp(-a / 0.5))

        # he seizes Mime: emerald closing round the yellow, Mime shaking
        held = smoothstep(T_GRAB - 0.5, T_GRAB, t) * (1 - smoothstep(T_LET, T_LET + 1.5, t))
        ps = p_hero + (p_grab - p_hero) * held
        if T_GRAB <= t < T_GRAB + 2.5:
            a = t - T_GRAB
            fr += light(WHITE, 0.6 * np.exp(-a / 0.1))
            fr += light(SIEGFRIED, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_mime) - 1200 * a) / 120) ** 2))
        if held > 0:
            r = 140 - 80 * smoothstep(T_GRAB, T_GRAB + 4, t)
            ring = np.exp(-((np.abs(d - p_mime) - r) / 18) ** 2)
            fr += light(SIEGFRIED, 0.7 * held * ring * (0.75 + 0.25 * np.sin(2 * np.pi * 3 * t)))

        # the father: Wälsung blue rolling out from the porch over Left and Side, a wave on every note
        blue = smoothstep(T_SM[0], T_SM[0] + 3, t) * (1 - smoothstep(T_LET, T_LET + 3, t))
        if blue > 0:
            reach = smoothstep(T_SM[0], T_SM[0] + 8, t)
            fr = fr * (1 - 0.5 * blue * (d < pl0))[:, None]
            fr += light(SIEGMUND, 0.75 * blue * (father <= reach + 0.02) * (d < pl0 + 30))
            i = int(np.searchsorted(sm_on, t, side='right')) - 1
            if i >= 0 and t - sm_on[i] < 1.5:
                a = t - sm_on[i]
                fr += light(SIEGMUND, 0.7 * np.exp(-a / 0.5) * np.exp(-((pl0 - d - 1300 * a) / 70) ** 2))
        # the mother: hearth amber flooding Right, fading as her phrase sinks
        amber = smoothstep(T_SL[0], T_SL[0] + 3, t) * (1 - 0.6 * smoothstep(T_SL[1] + 3, sl_end, t)) \
            * (1 - smoothstep(T_LET, T_LET + 3, t))
        if amber > 0:
            reach = smoothstep(T_SL[0], T_SL[0] + 7, t)
            fr = fr * (1 - 0.5 * amber * (d > pr1))[:, None]
            fr += light(SIEGLINDE, 0.75 * amber * (mother <= reach + 0.02) * (d > pr1 - 30))
            i = int(np.searchsorted(sl_on, t, side='right')) - 1
            if i >= 0 and t - sl_on[i] < 1.5:
                a = t - sl_on[i]
                fr += light(SIEGLINDE, 0.7 * np.exp(-a / 0.5) * np.exp(-((d - pr1 - 1300 * a) / 70) ** 2))
        # he lets go: blue and amber run back onto the porch and flare there as emerald
        if T_LET <= t < T_LET + 5:
            a = t - T_LET
            u = smoothstep(0, 1.8, a)
            fr += light(SIEGMUND, 0.8 * (1 - u) * np.exp(-((d - (pl0 - (1 - u) * pl0)) / 80) ** 2))
            fr += light(SIEGLINDE, 0.8 * (1 - u) * np.exp(-((d - (pr1 + (1 - u) * (L - pr1))) / 80) ** 2))
            fl = smoothstep(1.6, 2.0, a) * np.exp(-max(a - 2.0, 0) / 1.2)
            fr += light(SIEGFRIED, 0.95 * fl * np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']))
            fr += light(SIEGFRIED, 0.5 * fl)

        shake = 5 * held * np.sin(2 * np.pi * 11 * t)
        mlvl = keys(t, [(0, 0.65), (T_LAMENT[0], 0.85), (T_GRAB, 0.85), (T_GRAB + 1, 0.5), (T_LET, 0.5),
                        (D - 5, 0.6)])
        fr = figure(fr, S, p_mime + shake, MIME, mlvl)
        fr = hero(fr, S, ps, keys(t, [(0, 0.8), (T_GRAB - 0.5, 1.0), (T_LET + 3, 1.0), (D - 4, 0.8)]))
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

    for name, gain, rev in (('low', 0.4, 0.22), ('winds', 0.34, 0.3), ('brass', 0.38, 0.3), ('strings', 0.36, 0.32),
                            ('perc', 0.36, 0.25), ('warm', 0.34, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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

    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    hero = pan_at(at(G, 'Porch Front', HERO_AT))
    left = pan_at(at(G, 'Left', 0.4))
    right = pan_at(at(G, 'Right', 0.6))
    for t, d, m, v, part, k in compose():
        if part == 'lament':
            M.add('winds', oboe.play(m + 12, v, dur=d * 1.1, release=0.2), t, 0.8, mime)
            M.add('winds', bsn.play(m, v - 10, dur=d * 1.1, release=0.2), t, 0.6, mime)
        elif part == 'rock':
            M.add('low', pizz.play(m, v), t, 0.8, mime * 0.5)
        elif part == 'cut':
            for mm in (m, m + 7, m + 12):
                M.add('brass', horn_st.play(mm, v), t, 0.7, hero)
            M.add('perc', timp.play(v, pitch=-2), t, 0.8, hero)
        elif part == 'grab':
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v, hero, rise=0.05, fall=0.4, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.15), t, 0.9, hero)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, mime)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, mime)
        elif part == 'trem':
            hold('low', ctrem, m, t, t + d, v, mime, rise=0.3, fall=1.5, gain=0.5)
        elif part == 'siegmund':
            if m >= note('D4'):
                hold('brass', horn, m - 12, t, t + d, v - 6, left, rise=1.0, fall=1.5, gain=0.7)
            elif m >= note('D3'):
                hold('strings', vc, m, t, t + d, v, left, rise=0.3, fall=1.2, gain=0.9)
            else:
                M.add('low', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, left)
                M.add('low', cb.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, left)
        elif part == 'sieglinde':
            if d > 1.0:
                hold('strings', vc, m, t, t + d, v, right, rise=0.25, fall=1.0, gain=0.85)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, right)
            M.add('winds', oboe.play(m + 12, v - 16, dur=d * 1.1, release=0.25), t, 0.5, right)
        elif part == 'horn':
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v, hero, rise=0.06, fall=0.6, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.15), t, 0.85, hero)
        elif part == 'glow':
            hold('warm', vc if m < note('C3') else horn, m, t, t + d, v, hero * 0.5, rise=2.5, fall=2.0, gain=0.5)
