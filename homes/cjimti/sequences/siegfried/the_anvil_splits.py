"""The Anvil Splits: the blade lies red on the anvil and the forge is roaring. Siegfried plunges it into the
water: a hiss, and a cloud of white steam bursts out from the anvil and rolls away down both sides of the house,
and when it clears the blade is steel. He hammers it on the forging motif (Donington 52), every low note a blow
that flashes white and throws sparks to both ends of the roof, the steel growing longer and brighter with each
phrase, until the gold hilt gleams. The trumpets name it, Nothung (43), a steel flash at every note.

At the end of Left Mime gloats over his poison, his motif (50) bubbling and the sickly green flooding his corner.
Then the sword motif (45) blazes on trumpets and horns and Siegfried raises the blade: steel all along Porch
Front. Timpani roll; streaks of white rush in from both ends of the house to gather on the sword; and he brings it
down. The anvil splits: one white flash over the whole house, a black crack where the anvil was, and two fronts
of white and gold racing out from it to both ends. Nothung in full on the brass and his horn call (48) twice
over: emerald and steel waves roll end to end across the house, while Siegfried holds the sword aloft, blazing,
and Mime cowers, trembling, at the end of Left.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF10'
TITLE = 'The Anvil Splits'
KIND = 'show'
DESCRIPTION = ('The red-hot blade hisses in the water and is hammered into Nothung. Siegfried raises the new sword '
               'and brings it down on the anvil, which splits in two from end to end of the house.')
VOICEOVER = ('The sword is forged. Siegfried raises it high, and strikes the anvil, '
             'and the anvil splits in two.')

K = 9                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_QUENCH = 2.0                              # into the water: the hiss and the steam
T_HAMMER = [6.5, 10.0, 13.5, 17.0]          # the forging motif, the blade beaten out
T_HILT = 20.0                               # the gold hilt
T_NAME = 21.5                               # the trumpets name it
T_MIME = [29.5, 32.5]                       # Mime gloating over his poison
T_RAISE = 36.0                              # the sword motif: he raises it
T_ROLL = 40.5                               # the timpani roll, the light gathering on the sword
T_SPLIT = 48.0                              # the blow: the anvil splits
T_TRIUMPH = 50.0                            # Nothung in full on the brass
T_HORN = [58.0, 62.0]                       # his horn call, twice over
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
REDHOT = hexc('#ff3000')
POISON = hexc('#a0d000')
STEAM = hexc('#d8e0e8')

START = dict(bed=0.28, forge=0.8, walls=0.7, mouth=0.55)          # where SF09 left the cave
MIME_AT = 0.7                               # Mime's place on Left, at his pot


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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_SPLIT, 'F1', 62, 'pedal')
    add(T_QUENCH, 3.0, 'C1', 110, 'hiss')
    for k, t0 in enumerate(T_HAMMER):
        for t, m, v, d in play('forging', t0, 0.52, 0, 100 + 5 * k):
            add(t, d, m, v, 'hammer', k)
    add(T_HILT, 2.0, 'C5', 70, 'hilt')
    for t, m, v, d in play('nothung', T_NAME, 0.55, 0, 110):
        add(t, d, m, v, 'name')
    for k, t0 in enumerate(T_MIME):
        for t, m, v, d in play('mime', t0, 0.34, -12, 74):
            add(t, d, m, v, 'mime', k)
    for t, m, v, d in play('sword', T_RAISE, 0.55, 0, 116):
        add(t, d, m, v, 'sword')
    add(T_ROLL, T_SPLIT - T_ROLL, 'C1', 120, 'roll')
    add(T_SPLIT, 0.1, 'C1', 127, 'split')
    for t, m, v, d in play('nothung', T_TRIUMPH, 0.6, -12, 122):
        add(t, d, m, v, 'triumph')
    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, 0.42, 5 * k, 118):
            add(t, d, m, v, 'horn', k)
    for m in ('F2', 'C3', 'F3', 'A3', 'C4'):
        add(T_HORN[-1] + 3.0, D - T_HORN[-1] - 3.0, m, 84, 'blaze')
    add(T_HORN[-1] + 3.0, 0.1, 'C1', 118, 'cadence')
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """Every hammer blow on the anvil: [(time, strength, where)]."""
    return sorted((t, 1.1, S['anvil']) for t, _, m, v, part, k in compose() if part == 'hammer' and m < note('C3'))


def render(G, seed=10):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    hits = blows(S)
    hit_t = np.array([h[0] for h in hits])
    names = np.array(sorted({e[0] for e in N if e[4] in ('name', 'sword')}))
    mimes = np.array([e[0] for e in N if e[4] == 'mime'])
    waves = np.array(sorted({e[0] for e in N if e[4] in ('triumph', 'horn')}))
    rng = np.random.default_rng(seed)
    bubble = Flicker(rng, G.N, 1.5, 4.0)
    shimmer = Flicker(rng, G.N, 4.0, 10.0)
    pf0, pf1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    p_pot = at(G, 'Left', MIME_AT)
    pot = np.exp(-((d - p_pot) / 60) ** 2)
    left = d < at(G, 'Porch Left', 0.0)
    streak_at = rng.uniform(0, L, 40)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lull = smoothstep(T_MIME[0] - 1, T_MIME[0], t) * (1 - smoothstep(T_RAISE - 1, T_RAISE, t))
        lv['forge'] -= 0.25 * lull
        lv['walls'] -= 0.25 * lull
        fr = cave(S, T, lv)
        sh = np.clip(shimmer(T), -1, 1)

        # the blade: red at first, steel after the quench, longer with every phrase, raised along Porch Front
        heat = keys(t, [(0, 0.45), (T_QUENCH, 0.45), (T_QUENCH + 0.8, 0.0)])
        half = keys(t, [(0, 55.0), (T_HAMMER[0], 55.0), (T_HILT, 110.0), (T_RAISE, 110.0), (T_RAISE + 3.0, 175.0)])
        bright = keys(t, [(T_QUENCH, 0.0), (T_QUENCH + 1.5, 0.55), (T_HILT, 0.8), (T_RAISE, 0.8), (T_RAISE + 3, 1.0)])
        if t >= T_SPLIT:
            half, bright = keys(t, [(T_SPLIT, 175.0), (T_SPLIT + 2, 70.0)]), 1.0
        blade = np.exp(-((d - anvil) / half) ** 6)
        i = int(np.searchsorted(names, t, side='right')) - 1
        flash = np.exp(-(t - names[i]) / 0.25) if i >= 0 and t < T_RAISE + 5 else 0.0
        if heat > 0:
            fr = fr * (1 - 0.7 * blade)[:, None]
            fr += light(REDHOT * (1 - heat) + HEAT * heat, 0.8 * blade)
        fr = fr * (1 - 0.8 * min(1.0, bright * 2) * blade)[:, None]
        fr += light(STEEL, (bright * (0.85 + 0.15 * sh) + 0.3 * flash) * blade)
        if flash:
            fr += light(STEEL, 0.8 * flash * np.exp(-((np.abs(d - anvil) - 1500 * (t - names[i])) / 130) ** 2))
        if t >= T_HILT:
            hilt_at = anvil - half - 8
            fr += light(HILT, smoothstep(T_HILT, T_HILT + 1, t) * np.exp(-((d - hilt_at) / 9) ** 2))

        # the quench: a hiss and a cloud of white steam rolling away down both sides of the house
        if T_QUENCH <= t < T_QUENCH + 5:
            a = t - T_QUENCH
            r = 700 * (1 - np.exp(-a / 1.2)) * 1.6
            cloud = np.exp(-((np.abs(d - anvil) - r) / (80 + 150 * a)) ** 2) + (np.abs(d - anvil) < r)
            fr += light(STEAM, 1.0 * np.exp(-a / 1.6) * np.clip(cloud, 0, 1) * (0.8 + 0.2 * sh))

        # every hammer blow: a white flash, a shockwave and sparks to both ends
        j = int(np.searchsorted(hit_t, t, side='right')) - 1
        if j >= 0 and t - hit_t[j] < 1.2:
            a = t - hit_t[j]
            fr += light(HEAT, min(1.0, 1.1 * np.exp(-a / 0.1)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.8 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 90) ** 2))
        fr += light(SPARK, np.clip(sparks(S, hits, t, 100, n=18), 0, 1.0))

        # Mime gloating at his pot: the sickly green floods his corner with each bubble of his motif
        k = int(np.searchsorted(mimes, t, side='right')) - 1
        bub = np.exp(-(t - mimes[k]) / 0.2) if k >= 0 and t < T_RAISE else 0.0
        brew = 1 - smoothstep(T_SPLIT, T_SPLIT + 2, t)
        fr += light(POISON, brew * (0.4 + 0.15 * np.clip(bubble(T), 0, 1)) * pot)
        fr += light(POISON, 0.75 * bub * left * np.exp(-np.abs(d - p_pot) / 250))

        # the gathering: streaks of white rush in from both ends to the sword
        if T_ROLL <= t < T_SPLIT:
            u = (t - T_ROLL) / (T_SPLIT - T_ROLL)
            for q, p0 in enumerate(streak_at):
                ph = (u * 3 + q / len(streak_at)) % 1
                p = p0 + (anvil - p0) * ph ** 2
                fr += light(STEEL, 0.7 * u * np.sin(np.pi * ph) * np.exp(-((d - p) / 12) ** 2))
            fr += light(STEEL, 0.4 * u ** 2 * np.exp(-((d - anvil) / 400) ** 2))

        # the split: one white flash, a black crack at the anvil, white and gold racing out to both ends
        if t >= T_SPLIT:
            a = t - T_SPLIT
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12))
            r = 2000 * a
            if a < 2.5:
                front = np.exp(-((np.abs(d - anvil) - r) / 70) ** 2)
                fr += light(WHITE, 1.0 * front)
                fr += light(GOLD, 0.9 * np.exp(-((np.abs(d - anvil) - r + 120) / 120) ** 2))
            fr += light(STEEL, 0.45 * np.exp(-a / 3.0) * (np.abs(d - anvil) < r))
            crack = np.exp(-((d - anvil) / 10) ** 2) * (1 - smoothstep(T_SPLIT + 1.5, T_SPLIT + 3, t))
            fr = fr * (1 - crack)[:, None]

        # the triumph: every note an emerald and steel wave rolling end to end across the house
        if t >= T_TRIUMPH:
            glow = smoothstep(T_TRIUMPH, T_TRIUMPH + 3, t)
            wings = S['spill'] * (1 - S['forge'] - S['walls']).clip(0)
            fr = fr * (1 - 0.7 * glow * wings)[:, None]
            fr += light(SIEGFRIED, 0.55 * glow * wings * (0.85 + 0.15 * sh))
            w = int(np.searchsorted(waves, t, side='right')) - 1
            for q in range(max(0, w - 6), w + 1):
                b = t - waves[q]
                if b < 3.0:
                    x = anvil + (1 if q % 2 else -1) * 800 * b
                    behind = ((d - anvil) * (1 if q % 2 else -1) > 0) * ((d - x) * (1 if q % 2 else -1) < 0)
                    fr += light(SIEGFRIED, 0.95 * np.exp(-b / 1.0) * np.exp(-((d - x) / 220) ** 2))
                    fr += light(SIEGFRIED, 0.35 * np.exp(-b / 0.8) * behind)
                    fr += light(STEEL, 0.7 * np.exp(-b / 0.7) * np.exp(-((d - x) / 60) ** 2))
            fr += light(STEEL, 0.35 * glow * np.exp(-((d - anvil) / 220) ** 2) * (0.8 + 0.2 * sh))

        # Mime: at his pot; trembling and dim after the split
        trem = smoothstep(T_SPLIT, T_SPLIT + 0.5, t)
        lm = (0.6 + 0.15 * bub) * (1 - 0.45 * trem) * (1 + 0.3 * trem * np.sin(2 * np.pi * 8 * t))
        fr = figure(fr, S, p_pot - 30 * trem + 5 * trem * np.sin(2 * np.pi * 6 * t), MIME, lm)

        # Siegfried at the anvil, flaring with each blow, blazing with the sword aloft
        blow = np.exp(-(t - hit_t[j]) / 0.2) if j >= 0 else 0.0
        lvl = keys(t, [(0, 0.8), (T_RAISE, 0.8), (T_RAISE + 3, 0.95)]) * (1 + 0.3 * blow + 0.2 * flash)
        ps = anvil + 4
        fr = figure(fr, S, ps, SIEGFRIED, lvl * (1 - 0.5 * min(1, bright) * (t > T_RAISE)), 20.0)
        fr += light(HEAD, lvl * np.exp(-((d - ps) / 6) ** 2))
        if t > T_RAISE:
            fr += light(SIEGFRIED, 0.75 * lvl * smoothstep(T_RAISE, T_RAISE + 2, t) *
                        np.exp(-((np.abs(d - anvil) - half - 22) / 16) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.32, 0.22), ('strings', 0.26, 0.3), ('winds', 0.26, 0.3), ('brass', 0.3, 0.3),
                            ('perc', 0.3, 0.25), ('fx', 0.16, 0.25), ('harp', 0.2, 0.4), ('warm', 0.26, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Median*.wav')

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
    pot = pan_at(at(G, 'Left', MIME_AT))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=3.0, fall=1.0, gain=0.55)
        elif part == 'hiss':
            M.add('fx', whoosh(d, 6000, 2500, 0.9, seed=10), t, 1.0, forge)
            M.add('perc', swell.play(80, dur=d), t - 0.2, 0.5, forge)
        elif part == 'hammer':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.2), t, 0.9, forge)
                M.add('perc', anvil.play(min(127, v + 12)), t, 1.0, forge)
                M.add('perc', timp.play(v - 10, pitch=-3), t, 0.6, forge)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, forge)
            else:
                M.add('brass', horn.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.85, forge)
        elif part == 'hilt':
            for q, mm in enumerate((m, m + 4, m + 7)):
                M.add('harp', glock.play(mm, v), t + 0.12 * q, 0.7, forge)
        elif part in ('name', 'sword'):
            s = tpt if m >= note('C4') else horn
            if d > 1.0:
                hold('brass', s, m - 12, t, t + d, v, forge, rise=0.1, fall=0.8, gain=0.9)
            else:
                M.add('brass', s.play(m - 12, v, dur=d * 1.05, release=0.25), t, 0.95, forge)
            if part == 'sword':
                M.add('brass', horn.play(m - 12, v - 10, dur=d * 1.05, release=0.3), t, 0.6, forge)
        elif part == 'mime':
            M.add('winds', bsn.play(m, v), t, 0.9, pot)
        elif part == 'roll':
            r = 0.0
            while r < d:
                M.add('perc', roll.play(min(127, 80 + int(6 * r)), pitch=-3, dur=2.6), t + r, 0.5 + 0.06 * r, forge)
                r += 2.4
            M.add('perc', swell.play(110, dur=d), t + d - 4.0, 0.7)
        elif part == 'split':
            M.add('perc', anvil.play(v), t, 1.0, forge)
            M.add('perc', crash.play(v), t, 1.0)
            M.add('perc', gong.play(v), t, 0.9)
            M.add('perc', timp.play(v, pitch=-6), t, 1.0)
            M.add('fx', whoosh(2.0, 300, 6000, 0.9, seed=11), t, 1.0, -0.6)
            M.add('fx', whoosh(2.0, 300, 6000, 0.9, seed=12), t, 1.0, 0.6)
        elif part == 'triumph':
            if d > 1.0:
                hold('brass', tpt, m, t, t + d, v, 0.0, rise=0.1, fall=0.8, gain=0.85)
            else:
                M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.25), t, 0.95)
            M.add('low', tbn.play(m - 12, v - 10, dur=d * 1.05, release=0.25), t, 0.7)
            M.add('perc', timp.play(v - 30, pitch=-4), t, 0.4)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, -0.4 if k == 0 else 0.4)
            M.add('strings', vc.play(m - 12, v - 15, dur=d * 1.05, release=0.3), t, 0.6)
        elif part == 'blaze':
            hold('warm', horn if m >= note('C3') else tbn, m, t, t + d, v, 0.0, rise=0.2, fall=2.5, gain=0.55)
        elif part == 'cadence':
            M.add('perc', crash.play(v), t, 0.9)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9)
