"""The Anvil Splits: the blade lies red on the anvil and the forge is roaring. Siegfried plunges it into the
water: a hiss, and a cloud of white steam bursts out from the anvil and rolls away down both sides of the house,
and when it clears the blade is steel. Then the Forging Song: "Hoho! Hahei! Schmiede, mein Hammer, ein hartes
Schwert!", and every blow of his hammer, as Wagner marks them in the score, flashes white on the anvil and throws
sparks to both ends of the roof, the steel growing longer and brighter with each phrase until the gold hilt
gleams. At the end of Left Mime gloats over his poison, the sickly green bubbling in his corner.

"Schau, Mime, du Schmied": Siegfried raises the blade, steel all along Porch Front, and streaks of white rush in
from both ends of the house to gather on it while he sings "So schneidet Siegfrieds Schwert!", and on "Schwert!"
he brings it down. The anvil splits: one white flash over the whole house, a black crack where the anvil was, and
two fronts of white and gold racing out from it to both ends. The orchestra races to the end of the act, and on
every bar an emerald and steel wave rolls end to end across the house while Siegfried holds the sword aloft,
blazing, and Mime cowers, trembling, at the end of Left.

The music is Wagner's own: Act I, bars 2583 to 2594 (the quenching), 2694 to 2715 (the Forging Song) and 2941 to
the end of the act, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and register. Siegfried's lines are not in
the reduction, so "Hoho! Hahei!", "Schmiede, mein Hammer, ein hartes Schwert!" and "So schneidet Siegfrieds
Schwert!" come from the Breitkopf & Härtel vocal score (Leipzig 1914, archive.org 31761034115105, pp. 128-129 and
144), played as he sings them, a tenor an octave below the written notes, on horns doubled by a trumpet; the
hammer's blows follow the score's own hammer part. On stage: the hiss and steam of the quench, the forge's roar
and crackle, every hammer blow ringing on the anvil, and the anvil splitting with a crash and a great blow.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF10'
TITLE = 'The Anvil Splits'
KIND = 'show'
DESCRIPTION = ('The red-hot blade hisses in the water and is hammered into Nothung to the Forging Song. Siegfried '
               'raises the new sword and brings it down on the anvil, which splits in two from end to end of the '
               'house.')
VOICEOVER = ('The sword is forged. Siegfried raises it high, and strikes the anvil, '
             'and the anvil splits in two.')

K = 9                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 2583-2594, 2694-2715 and 2941 to the end, Solti 1958
D = EX['seconds']
_M = np.array([m for m, _ in EX['bars']], float)
_T = np.array([t for _, t in EX['bars']])


def bt(m):
    """Seconds into the scene of measure position m (bar plus fraction)."""
    return float(np.interp(m, _M, _T))


# Siegfried's lines, from the vocal score: (bar, beat, beats, written note, beats in the bar)
VOICE = ([(2694, 3.5, 0.5, 'C5'), (2695, 0, 1, 'F5'), (2695, 1.5, 0.5, 'A4'), (2695, 2, 1, 'F5'),
          (2695, 3.5, 0.5, 'G5'), (2696, 0, 1, 'C5'),
          (2699, 0, 1, 'G5'), (2699, 1, 0.5, 'E5'), (2699, 1.5, 0.5, 'E5'), (2699, 2, 1, 'G5'), (2699, 3, 0.5, 'C5'),
          (2699, 3.5, 0.5, 'C5'), (2700, 0, 1, 'F5'), (2700, 1, 1, 'D5'), (2700, 2, 2, 'F5'),
          (2701, 1.5, 0.5, 'Bb4'), (2701, 2, 1, 'D5'), (2701, 3.5, 0.5, 'G5'), (2702, 0, 1, 'C5'),
          (2702, 1.5, 0.5, 'Bb4'), (2702, 2, 1, 'D5'), (2702, 3.5, 0.5, 'G5'), (2703, 0, 1, 'C5')],
         [(2949, 0, 3, 'G5'), (2950, 0, 2, 'F#5'), (2950, 2, 1, 'E5'), (2951, 0, 3, 'A5'), (2952, 0, 3, 'C#5'),
          (2953, 0, 3, 'D5')])
# the hammer, as the score marks it: strong blows on the downbeats, one on every beat under his song
_SUNG = {2695, 2699, 2700, 2701, 2702, 2711, 2712, 2713, 2714, 2715}
HAMMER = [(b + x / 4, 1.2 if x == 0 else 0.75) for b in range(2694, 2716) for x in range(4)
          if x == 0 or b in _SUNG]

T_QUENCH = bt(2584)                         # into the water: the hiss and the steam
PUFFS = [t for t in accents(EX['notes'], bt(2584) + 2.5, bt(2694), n=2, space=1.0)]   # steam still hissing off it
T_HAMMER = bt(2694)                         # the Forging Song
T_NAME = bt(2699)                           # "Schmiede, mein Hammer, ein hartes Schwert!"
T_MIME = [bt(b) for b in (2705, 2706.5, 2708, 2709.5)]     # Mime gloating while Siegfried sings his verse
T_HILT = bt(2711)                           # "Heiaho!": the gold hilt
T_RAISE = bt(2941)                          # "Schau, Mime, du Schmied": he raises it
T_ROLL = bt(2949)                           # "So schneidet Siegfrieds Schwert!": the light gathers on it
T_SPLIT = bt(2953)                          # "Schwert!": the blow; the anvil splits
T_TRIUMPH = T_SPLIT + 0.6                   # the orchestra races to the end of the act

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


def voice():
    """Siegfried's lines in seconds: (time, seconds, sounding midi)."""
    out = []
    for part, per in ((VOICE[0], 4), (VOICE[1], 3)):
        for b, x, n, name in part:
            t0 = bt(b + x / per)
            out.append((t0, bt(b + (x + n) / per) - t0, note(name) - 12))
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'orch' (k the hand, or 'trem'
    for a tremolo); Siegfried's lines are 'sing'; 'hammer', 'name', 'mime', 'triumph' mark the lights' moments."""
    N = []
    for n in tidy(EX['notes']):
        N.append((n[0], n[1], n[2], n[3], 'orch', 'trem' if n[5] else n[4]))
    for t, d, m in voice():
        N.append((t, d, m, 112, 'sing', None))
        if T_NAME <= t < bt(2701):
            N.append((t, 0.5, m, 0, 'name', None))
    for k, (pos, s) in enumerate(HAMMER):
        N.append((bt(pos), 0.2, 0, int(80 + 40 * s), 'hammer', k))
    for k, t0 in enumerate(T_MIME):
        N.append((t0, 0.3, 0, 0, 'mime', k))
    for b in range(2955, 2983, 2):
        N.append((bt(b), 0.5, 0, 0, 'triumph', b))
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """Every hammer blow on the anvil: [(time, strength, where)]."""
    return sorted((t, (v - 80) / 40, S['anvil']) for t, _, m, v, part, k in compose() if part == 'hammer')


def render(G, seed=10):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    hits = blows(S)
    hit_t = np.array([h[0] for h in hits])
    names = np.array(sorted({e[0] for e in N if e[4] == 'name'}))
    mimes = np.array([e[0] for e in N if e[4] == 'mime'])
    waves = np.array(sorted({e[0] for e in N if e[4] == 'triumph'}))
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
        lull = smoothstep(T_MIME[0] - 1, T_MIME[0], t) * (1 - smoothstep(T_HILT - 1, T_HILT, t))
        lv['forge'] -= 0.25 * lull
        lv['walls'] -= 0.25 * lull
        fr = cave(S, T, lv)
        sh = np.clip(shimmer(T), -1, 1)

        # the blade: red at first, steel after the quench, longer with every phrase, raised along Porch Front
        heat = keys(t, [(0, 0.45), (T_QUENCH, 0.45), (T_QUENCH + 0.8, 0.0)])
        half = keys(t, [(0, 55.0), (T_HAMMER, 55.0), (T_HILT, 110.0), (T_RAISE, 110.0), (T_RAISE + 3.0, 175.0)])
        bright = keys(t, [(T_QUENCH, 0.0), (T_QUENCH + 1.5, 0.55), (T_HILT, 0.8), (T_RAISE, 0.8), (T_RAISE + 3, 1.0)])
        if t >= T_SPLIT:
            half, bright = keys(t, [(T_SPLIT, 175.0), (T_SPLIT + 2, 70.0)]), 1.0
        blade = np.exp(-((d - anvil) / half) ** 6)
        i = int(np.searchsorted(names, t, side='right')) - 1
        flash = np.exp(-(t - names[i]) / 0.25) if i >= 0 and t < T_RAISE else 0.0
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

        # the steam keeps hissing off the blade: a puff rolling out on each accent as it cools
        for q, tp in enumerate(PUFFS):
            a = t - tp
            if 0 <= a < 3.0:
                fr += light(STEAM, 0.7 * np.exp(-a / 0.9) * (0.8 + 0.2 * sh) *
                            np.exp(-((np.abs(d - anvil) - 450 * a) / (60 + 120 * a)) ** 2))

        # every hammer blow: a white flash, a shockwave and sparks to both ends
        j = int(np.searchsorted(hit_t, t, side='right')) - 1
        if j >= 0 and t - hit_t[j] < 1.2:
            a = t - hit_t[j]
            s = hits[j][1]
            fr += light(HEAT, min(1.0, 1.1 * s * np.exp(-a / 0.1)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.8 * s * np.exp(-a / 0.5) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 90) ** 2))
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
    """The real music: the excerpt orchestrated from the piano reduction, Siegfried's lines on horns and a trumpet,
    and the forge: the quench's hiss, the hammer on the anvil as the score marks it, the anvil splitting."""
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    forge = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=1.95)
    N = compose()

    def size(t):
        if t < T_HAMMER:
            return 1.0 if t < bt(2587) else 0.5
        return 1.0

    o.tutti([e[:4] + (e[5] if e[5] != 'trem' else 0, e[5] == 'trem') for e in N if e[4] == 'orch'], size=size)
    for t, d, m, v, part, k in N:
        if part == 'sing':                                                      # Siegfried: horns and a trumpet
            o.play('horns', m, t, max(d, 0.15), v, forge, 0.95)
            o.play('trumpets', m, t, max(d, 0.15), v - 18, forge, 0.4)
        elif part == 'hammer':                                                  # the hammer on the anvil
            s = (v - 80) / 40
            o.hit('anvil', t, int(90 + 30 * s), gain=0.55 + 0.35 * s, pan=forge)
            if s > 1:
                o.hit('metal', t + 0.01, 100, gain=0.2, pan=forge)
    # the quench: a long hiss of steam out of the water, and the forge roaring and crackling all through
    n = int(4.5 * SR)
    hiss = o._noise(0, 2500, 11000, 2584, n=n) * np.exp(-np.arange(n) / (1.4 * SR)) * np.clip(
        np.arange(n) / (0.04 * SR), 0, 1)
    o._sfx(hiss, T_QUENCH, 0.9, forge)
    for q, tp in enumerate(PUFFS):                                              # the hiss of each puff
        m = int(1.2 * SR)
        o._sfx(o._noise(0, 3000, 11000, 2600 + q, n=m) * np.exp(-np.arange(m) / (0.35 * SR)), tp, 0.35, forge)
    o.hit('timpani roll', T_QUENCH, 90, pitch=-5, gain=0.35, pan=forge)
    o.fire(0.0, T_SPLIT + 3, lambda tt: 0.55 - 0.3 * smoothstep(T_QUENCH, T_QUENCH + 2, tt) +
           0.25 * smoothstep(T_HAMMER - 2, T_HAMMER, tt), forge, crackle=12, seed=1010)
    # the gathering on the sword, then the split: a crash, the halves falling apart, a great blow
    o.hit('cymbal swell', T_SPLIT - 3.6, 100, gain=0.45, pan=forge)
    o.shatter(T_SPLIT, forge, 1.0)
    o.boom(T_SPLIT + 0.02, forge, 1.0)
    o.hit('anvil', T_SPLIT + 0.35, 110, gain=0.6, pan=forge - 0.2)
    o.hit('anvil', T_SPLIT + 0.55, 100, gain=0.5, pan=forge + 0.2)
    o.thunder(T_SPLIT + 0.05, 0.8, forge, 0.7)
    o.effects([(0, -2), (T_QUENCH + 4, -2), (T_QUENCH + 6, -9), (T_HAMMER - 1, -9), (T_HAMMER, -6),
               (T_ROLL - 1, -6), (T_SPLIT - 0.2, 0), (T_SPLIT + 3, 0), (T_SPLIT + 5, -8), (D, -8)])
