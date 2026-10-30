"""The Broken Sword: Mime has made Siegfried a new sword. He holds it out, and a white steel blade grows along
Porch Front from his hands toward the anvil while the trumpet gives the Sword motif (Donington 45), the blade
flashing on every note. Siegfried strides to the anvil and smashes it there: a white flash over the whole house,
and steel shards fly out in both directions to the ends of the roofline, chased by an orange flare of the
forge. Mime cringes (Mime frustrated, 71, in the bassoons), dim and shaking.

Twice he goes back to the anvil and hammers out another (Mime, obstinate, 51: every blow sparks to both ends of
the house), and twice Siegfried breaks it, each time harder. After the third the whole house burns emerald with
his scorn while his audacity (55) storms through the horns and violins, a green shockwave out from him at every
note, until he flings himself down at the anvil's right hand and Mime creeps back to its left.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF03'
TITLE = 'The Broken Sword'
KIND = 'show'
DESCRIPTION = ('The dwarf holds out a gleaming new sword, and Siegfried shatters it on the anvil. Mime makes '
               'another, and another, and each one breaks harder than the last.')
VOICEOVER = ('Mime forges sword after sword. '
             'And Siegfried smashes every one of them to pieces.')

K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_SWORD = [2.0, 24.0, 46.0]                 # Mime holds out a sword: the Sword motif on the trumpet
SMASH_AFTER = 6.5                           # Siegfried breaks it on the anvil
T_HAM = [13.0, 35.0]                        # Mime hammers out another
T_AUD = [57.0, 64.5]                        # Siegfried's scorn
T_REST = 71.0
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
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')

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


def smashes():
    return [t0 + SMASH_AFTER for t0 in T_SWORD]


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'C1', 60, 'pedal')
    for k, t0 in enumerate(T_SWORD):
        for t, m, v, d in play('sword', t0, 0.62, 0, 96 + 6 * k, line='melody'):
            add(t, d, m, v, 'sword', k)
    for k, ts in enumerate(smashes()):
        add(ts, 0.1, 'C1', 110 + 7 * k, 'smash', k)
        for t, m, v, d in play('mime_frustrated', ts + 1.0, 0.7 - 0.08 * k, 0, 90 + 6 * k):
            add(t, d, m, v, 'grumble', k)
        for t, m, v, d in play('mime_frustrated', ts + 2.6, 0.9, -12, 80):
            add(t, d, m, v, 'grumble', k)
    for k, t0 in enumerate(T_HAM):
        for r in range(3):
            for t, m, v, d in play('mime_obstinate', t0 + r * 2.0, BEAT, -12, 82 + 8 * r + 6 * k):
                add(t, d, m, v, 'ham', k)
    for k, t0 in enumerate(T_AUD):
        for t, m, v, d in play('siegfried_audacity', t0, 0.48, 0, 108 + 6 * k):
            add(t, d, m, v, 'aud', k)
            add(t, d, m - 24, v - 14, 'aud_bass', k)
    for m in ('C3', 'G3', 'C4', 'E4'):
        add(T_REST, D - T_REST, m, 62, 'glow')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=3):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    p_mime, p_hero = at(G, 'Porch Front', MIME_AT), at(G, 'Porch Front', HERO_AT)
    p_strike = at(G, 'Porch Front', 0.56)
    ham = [(t, 0.85, anvil) for t, _, m, v, part, k in N if part == 'ham']
    ham_t = np.array([h[0] for h in ham])
    sm = smashes()
    shards = [(ts, 1.0 + 0.3 * k, anvil) for k, ts in enumerate(sm)]
    sword = [e for e in N if e[4] == 'sword']
    grumble = [e for e in N if e[4] == 'grumble']
    aud_on = np.array(sorted({e[0] for e in N if e[4] == 'aud'}))
    jag = np.random.default_rng(seed).uniform(0.4, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        fury = smoothstep(sm[2], sm[2] + 0.5, t) * (1 - smoothstep(T_REST - 1, T_REST + 3, t))
        fr = cave(S, T, lv)

        # the blade held out: white steel growing from Mime's hands to the anvil, flashing at each note
        for k, t0 in enumerate(T_SWORD):
            ts = t0 + SMASH_AFTER
            if t0 <= t < ts + 0.05:
                grow = smoothstep(t0, t0 + 1.5, t)
                tip = p_mime + 10 + grow * (anvil - p_mime + 15)
                notes = [e for e in sword if e[5] == k and e[0] <= t]
                glint = np.exp(-(t - notes[-1][0]) / 0.25) if notes else 0.0
                blade = (d > p_mime + 8) * (d < tip) * 1.0
                fr = fr * (1 - 0.9 * blade)[:, None]
                fr += light(STEEL, (0.7 + 0.3 * glint) * blade)
                fr += light(STEEL, 0.5 * glint * np.exp(-((d - tip) / 60) ** 2))
                if notes:                   # each note of the Sword sends a steel gleam out to both ends
                    a = t - notes[-1][0]
                    fr += light(STEEL, 0.75 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 1100 * a) / 80) ** 2))
                fr += light(HILT, 0.9 * np.exp(-((d - p_mime - 9) / 4) ** 2))
                sweep = p_mime + ((t - t0) * 160) % (tip - p_mime + 1)
                fr += light(WHITE, 0.6 * blade * np.exp(-((d - sweep) / 8) ** 2))

        # the smash: a white flash over the whole house, steel shards to both ends, the forge flaring orange
        for k, ts in enumerate(sm):
            a = t - ts
            if 0 <= a < 3.0:
                s = 0.55 + 0.2 * k
                fr += light(WHITE, min(1.0, s * np.exp(-a / 0.08)) * (0.5 + 0.5 * jag))
                fr += light(FORGE, (0.9 + 0.1 * k) * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 1300 * a) / 200) ** 2))
                fr += light(FORGE, 0.55 * np.exp(-a / 0.9))
                fr += light(STEEL, 0.35 * np.exp(-a / 0.4) * jag)
                fr += light(HEAT, np.exp(-a / 0.2) * S['heat'] ** 0.4)
        fr += light(STEEL, np.clip(sparks(S, shards, t, 31, n=40, reach=1.3) + sparks(S, shards, t, 33, n=40), 0, 1.0))
        for t0, dur, m, v, part, k in grumble:  # every grumble a yellow shudder out from Mime
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(MIME, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - 900 * a) / 70) ** 2))

        # Mime hammers another: every blow a white-hot flash and sparks to both ends
        i = int(np.searchsorted(ham_t, t, side='right')) - 1
        if i >= 0 and t - ham_t[i] < 1.0:
            a = t - ham_t[i]
            fr += light(HEAT, min(1.0, 1.1 * np.exp(-a / 0.09)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.5 * np.exp(-a / 0.3) * (S['forge'] + S['walls']))
        fr += light(SPARK, np.clip(sparks(S, ham, t, 32), 0, 1.0))

        # his scorn: the whole house burns emerald, a shockwave out from him on every note
        if fury > 0:
            fr = fr * (1 - 0.6 * fury)
            fr += light(SIEGFRIED, fury * (0.45 + 0.15 * np.sin(2 * np.pi * (d / 300 - 1.4 * t))))
        j = int(np.searchsorted(aud_on, t, side='right')) - 1
        if j >= 0 and t - aud_on[j] < 1.2:
            a = t - aud_on[j]
            fr += light(HEAD, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_hero) - 1500 * a) / 90) ** 2))

        # Siegfried strides to the anvil for each smash and back; Mime cringes after each
        ps = p_hero
        for ts in sm:
            ps += (p_strike - p_hero) * smoothstep(ts - 1.6, ts - 0.4, t) * (1 - smoothstep(ts + 1.0, ts + 3.0, t))
        cringe = max([np.exp(-(t - ts) / 4.0) for ts in sm if ts <= t], default=0.0)
        shake = 4 * cringe * np.sin(2 * np.pi * 9 * t)
        mlvl = 0.75 - 0.4 * cringe
        if t > T_REST:
            mlvl = keys(t, [(T_REST, mlvl), (D - 4, 0.6)])
        fr = figure(fr, S, p_mime - 12 * cringe + shake, MIME, mlvl)
        fr = hero(fr, S, ps, keys(t, [(0, 0.8), (T_AUD[0], 1.0), (T_REST, 1.0), (D - 4, 0.8)]))
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

    for name, gain, rev in (('low', 0.4, 0.22), ('winds', 0.32, 0.3), ('brass', 0.38, 0.3), ('strings', 0.34, 0.3),
                            ('perc', 0.36, 0.25), ('mallet', 0.22, 0.32), ('warm', 0.34, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tuba_st = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    bsn_st = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
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

    forge = pan_at(at(G, 'Porch Front', 0.5))
    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    hero = pan_at(at(G, 'Porch Front', HERO_AT))
    rng = np.random.default_rng(45)
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.45)
        elif part == 'sword':
            if d > 0.6:
                hold('brass', tpt, m, t, t + d, v, mime, rise=0.06, fall=0.5, gain=0.85)
            else:
                M.add('brass', tpt.play(m, v, dur=d * 1.1, release=0.15), t, 0.85, mime)
        elif part == 'smash':
            M.add('perc', crash.play(v), t, 1.0, forge)
            M.add('perc', anvil.play(v), t, 1.0, forge)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, forge)
            for j in range(10 + 4 * k):     # the shards: glockenspiel notes scattering out both ways
                pa = float(np.clip(forge + rng.uniform(-1, 1), -0.9, 0.9))
                M.add('mallet', glock.play(note('C5') + int(rng.integers(0, 24)), 90 - 3 * j), t + 0.03 + 0.07 * j,
                      0.6, pa)
        elif part == 'grumble':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.25), t, 0.9, mime)
            M.add('low', vc.play(m, v - 12, dur=d * 1.1, release=0.25), t, 0.6, mime)
        elif part == 'ham':
            M.add('perc', anvil.play(v), t, 0.75, forge)
            M.add('mallet', xylo.play(m + 12, v - 10), t, 0.6, mime)
            M.add('winds', bsn_st.play(m, v - 6), t, 0.8, mime)
        elif part == 'aud':
            M.add('strings', vln.play(m + 12, v, dur=d, release=0.1), t, 0.8, hero)
            M.add('brass', horn_st.play(m, v - 6), t, 0.8, hero)
            if d > 0.6:
                hold('brass', horn, m, t, t + d, v - 14, hero, rise=0.05, fall=0.3, gain=0.5)
        elif part == 'aud_bass':
            M.add('low', tuba_st.play(m, v), t, 0.6, hero)
            if t in T_AUD:
                M.add('perc', crash.play(105), t, 0.6, hero)
        elif part == 'glow':
            hold('warm', vc if m < note('C4') else horn, m, t, t + d, v, hero * 0.5, rise=2.5, fall=2.0, gain=0.5)
