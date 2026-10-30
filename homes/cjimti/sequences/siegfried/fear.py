"""Fear: the Wanderer has gone, and Mime is alone at the anvil, shaking. "Verfluchtes Licht!": the flickering of
Loge's fire runs through the violins, and with every flicker tongues of fire leap up somewhere on the house, a
burst of red, orange and amber here, then there, then everywhere at once, more and bigger as it grows, while
Mime, sulphur yellow beside the anvil, twitches from side to side. "Dort bricht's durch den Wald": the dragon he
fears is coming, and two walls of blood red close in on him from the front corners of the porch, a lurch with
every stride of the bass, until "Fafner! Fafner!" the whole house goes up in flame and he dives behind the anvil.

"Heda! Du Fauler!": Siegfried bursts in at the free end of Right, an emerald comet with a white-hot head, and a
green wave sweeps the fire off the house from end to end. Mime tries to teach him fear: the shudder in the dark
forest, the heart hammering in the breast, and as the orchestra surges a ring of flame rises round the porch
with a violet glow on its summit, the fire round a sleeping bride, every surge of it leaping up while Siegfried,
who has never been afraid, brightens with each one.

The music is Wagner's own: Act I, bars 1916 to 1955 (Mime's terror and Siegfried's return) and 2130 to 2141
(Mime's description of fear), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the
Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and register: the flickering on
violins and piccolo, the dragon's strides on tuba, cellos and basses, the tremolos on the strings' tremolo. On
stage: the crackle and roar of the fire Mime sees, growing with his terror, the dragon's growl, a crash as he
dives behind the anvil, a blow and a rush of air as Siegfried bursts in, and the fire roaring up round the porch;
the effects stand back under the orchestra's surges.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'SF08'
TITLE = 'Fear'
KIND = 'show'
DESCRIPTION = ('Alone in the cave, the dwarf sees fire leaping everywhere and a dragon closing in. Siegfried bursts '
               'back in and sweeps it all away: he has never been afraid, and wants to learn how.')
VOICEOVER = ('Alone in the dark, Mime sees fire everywhere. '
             'Then Siegfried bursts in, and asks what fear is.')

K = 7                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1916-1955 and 2130-2141, Solti 1958
D = EX['seconds']
SEG = [(g['start'], g['start'] + g['seconds']) for g in EX['segments']]
_M = np.array([m for m, _ in EX['bars']], float)
_T = np.array([t for _, t in EX['bars']])


def bt(m):
    """Seconds into the scene of measure position m (bar plus fraction)."""
    return float(np.interp(m, _M, _T))


T_DRAGON = bt(1938)                         # "Dort bricht's durch den Wald": the walls of red close in
T_PANIC = bt(1948)                          # "Fafner!": the whole house in flame; he dives behind the anvil
T_BURST = bt(1950)                          # "Heda! Du Fauler!": he bursts in at the free end of Right
T_ARRIVE = bt(1953)                         # at the forge
T_SLEEP = [SEG[1][0]]                       # the fire round the sleeping bride
T_END = D

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
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
BLOOD = hexc('#8a0010')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
VIOLET = hexc('#7a6aff')

START = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)        # where SF07 left the cave
END = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # where SF09 picks it up
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
SIEG_AT = 0.7                               # Siegfried's, at the end


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
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'orch' (k the hand, or 'trem');
    'loge' marks each flicker of the fire (k how far into his terror), 'dragon' each stride of the bass, 'surge'
    each surge of the fire round the bride."""
    N = []
    for n in tidy(EX['notes']):
        N.append((n[0], n[1], n[2], n[3], 'orch', 'trem' if n[5] else n[4]))
    for j, t in enumerate(accents([n for n in EX['notes'] if n[4] == 0], 0.0, T_PANIC, n=1, space=0.55)):
        N.append((t, 0.3, 0, 90, 'loge', min(6, int(7 * t / T_PANIC))))
    last = -9.0
    for t, d, m, v, hand in sorted(EX['notes']):
        if T_DRAGON <= t < T_PANIC + 0.2 and hand == 1 and t - last > 0.45:
            N.append((t, max(d, 0.3), m, v, 'dragon', None))
            last = t
    for t in accents(EX['notes'], SEG[1][0], D - 0.5, vmin=90, n=2, space=0.45):
        N.append((t, 0.5, 0, 100, 'surge', None))
    return sorted(N, key=lambda e: e[0])


def tongues(G):
    """Every tongue of fire Mime sees: [(time, where, width, strength)], one or more per flicker."""
    rng = np.random.default_rng(208)
    out = []
    for t, d, m, v, part, k in compose():
        if part == 'loge':
            for _ in range(2 + k // 2):
                out.append((t, float(rng.uniform(at(G, 'Left', 0.0), G.pd.max())), float(rng.uniform(50, 90 + 20 * k)),
                            0.8 + 0.05 * k))
    return out


def render(G, seed=8):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    tg = tongues(G)
    dragon = np.array([e[0] for e in N if e[4] == 'dragon'])
    aud = []
    surges = np.array([e[0] for e in N if e[4] == 'surge'])
    lick = Flicker(np.random.default_rng(seed), G.N, 3.0, 9.0)
    p_mime = at(G, 'Porch Front', MIME_AT)
    p_home = at(G, 'Porch Front', SIEG_AT)
    pl0, pr1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    sleeper = np.exp(-((d - anvil) / 40) ** 2)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        fear = smoothstep(0, T_PANIC, t) * (1 - smoothstep(T_BURST, T_BURST + 1.2, t))
        lv['forge'] *= 1 - 0.4 * fear
        fr = cave(S, T, lv)
        fl = np.clip(lick(T), -1, 1)

        # the fire he sees: the whole house flickering more and more, and tongues leaping up all over it
        fr += light(RED, 0.62 * fear * (0.65 + 0.35 * fl))
        fr += light(ORANGE, 0.45 * fear ** 2 * np.clip(fl, 0, 1))
        for th, p, w, s in tg:
            a = t - th
            if 0 <= a < 1.4:
                env = s * smoothstep(0, 0.04, a) * np.exp(-a / 0.45) * (1 - smoothstep(T_BURST, T_BURST + 0.5, t))
                shape = np.exp(-((d - p) / w) ** 2)
                fr += light(ORANGE, env * shape * (0.8 + 0.2 * fl))
                fr += light(AMBER, 1.0 * env * shape ** 2)
                fr += light(HEAT, 0.6 * env * shape ** 6)
        if T_PANIC <= t < T_PANIC + 2.5:
            a = t - T_PANIC
            env = smoothstep(0, 0.08, a) * np.exp(-a / 0.7)
            fr += light(ORANGE, 0.95 * env * (0.75 + 0.25 * fl))
            fr += light(AMBER, 0.6 * env * np.clip(fl, 0, 1))

        # Fafner in his mind: walls of blood red close in from the front corners of the porch, a lurch per note
        n = int(np.searchsorted(dragon, t, side='right'))
        if n and t < T_PANIC + 0.5:
            u = n / len(dragon)
            lurch = np.exp(-(t - dragon[n - 1]) / 0.2)
            left_wall = pl0 - 300 + u * (p_mime - 30 - pl0 + 300)
            right_wall = pr1 + 400 - u * (pr1 + 400 - p_mime - 30)
            walls = smoothstep(left_wall - 120, left_wall, d) * (d < left_wall + 10) + \
                (d > right_wall - 10) * (1 - smoothstep(right_wall, right_wall + 120, d))
            jaws = np.exp(-((d - left_wall) / 25) ** 2) + np.exp(-((d - right_wall) / 25) ** 2)
            fr += light(BLOOD, 0.9 * walls)
            fr += light(RED, 0.45 * walls * (0.7 + 0.3 * lurch))
            fr += light(RED, (0.6 + 0.4 * lurch) * jaws)

        # Mime: twitching from side to side, diving behind the anvil, creeping back out
        twitch = fear * (30 * np.sin(2 * np.pi * 0.7 * t) + 6 * np.sin(2 * np.pi * 7 * t))
        pm = p_mime + twitch + keys(t, [(T_PANIC, 0.0), (T_PANIC + 0.3, 50.0), (T_BURST + 3, 50.0), (T_BURST + 6, 0.0)])
        lm = keys(t, [(0, 0.6), (T_PANIC, 0.75), (T_PANIC + 0.3, 0.22), (T_BURST + 3, 0.22), (T_BURST + 6, 0.6)])
        lm *= 1 + 0.25 * fear * np.sin(2 * np.pi * 9 * t)
        fr = figure(fr, S, pm, MIME, lm)

        # Siegfried bursts in at the free end of Right: an emerald comet, then a green wave sweeps the fire away
        if t >= T_BURST:
            u = smoothstep(T_BURST, T_ARRIVE, t)
            ps = L + 30 + u * (p_home - L - 30)
            a = t - T_BURST
            if a < 3.0:
                trail = (d > ps) * np.exp(-(d - ps) / 450)
                fr += light(SIEGFRIED, 1.0 * trail * np.exp(-a / 1.6))
            if T_ARRIVE <= t < T_ARRIVE + 4.5:
                b = t - T_ARRIVE
                r = 750 * b
                fr += light(SIEGFRIED, 1.0 * np.exp(-b / 2.0) * np.exp(-((np.abs(d - ps) - r) / 200) ** 2))
                fr += light(SIEGFRIED, 0.55 * np.exp(-b / 1.6) * (np.abs(d - ps) < r))

            # the fire round the sleeping bride: a ring of flame on the porch, violet on its summit
            ring = smoothstep(T_SLEEP[0], T_SLEEP[0] + 3.0, t) * (0.75 + 0.25 * smoothstep(T_SLEEP[0], D - 6, t))
            q = int(np.searchsorted(surges, t, side='right')) - 1
            leap = np.exp(-(t - surges[q]) / 0.35) if q >= 0 else 0.0
            ring *= 1 + 0.45 * leap
            if ring > 0:
                fr += light(ORANGE, 0.75 * ring * porch * (1 - sleeper) * (0.7 + 0.3 * fl))
                fr += light(RED, 0.5 * ring * porch * np.clip(-fl, 0, 1))
                fr += light(VIOLET, 0.8 * ring * sleeper)
                for tq in surges[max(0, q - 3):q + 1]:          # each surge throws a tongue up somewhere on the ring
                    a = t - tq
                    if 0 <= a < 1.0:
                        pq = pl0 + (pr1 - pl0) * ((tq * 7.31) % 1)
                        shape = np.exp(-((d - pq) / 70) ** 2) * porch * (1 - sleeper)
                        fr += light(AMBER, 0.9 * np.exp(-a / 0.35) * shape)
                        fr += light(HEAT, 0.5 * np.exp(-a / 0.2) * shape ** 4)
            glow = 0.0
            if ring > 0:
                glow = max(glow, leap)

            # his audacity: each note an emerald blast out to one end of the house or the other
            for j, (t0, dd, m, v, part, k) in enumerate(aud):
                b = t - t0
                if 0 <= b < 2.2:
                    r = 1000 * b
                    side = (d - ps) * (1 if j % 2 else -1) > 0
                    env = np.exp(-b / 0.8) * side
                    fr += light(SIEGFRIED, 1.0 * env * np.exp(-((np.abs(d - ps) - r) / 160) ** 2))
                    fr += light(SIEGFRIED, 0.5 * env * (np.abs(d - ps) < r))
                    glow = max(glow, np.exp(-b / 0.25))
            lvl = keys(t, [(T_BURST, 0.9), (T_ARRIVE + 3, 0.8)]) * (1 + 0.35 * glow)
            fr = figure(fr, S, ps, SIEGFRIED, lvl, 18.0)
            fr += light(HEAD, lvl * (0.7 + 0.3 * glow) * np.exp(-((d - ps) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The real music: the excerpt orchestrated from the piano reduction, and the staging: the fire Mime sees, the
    dragon's growl, his dive behind the anvil, Siegfried bursting in, the fire round the porch."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    forge = pan_at(S['anvil'])
    end = pan_at(G.pd.max())
    o = Orchestra(M, level=1.8)
    N = compose()

    def role(t, d, m, v, hand):
        if T_DRAGON <= t < T_PANIC + 0.5 and hand == 1 and m < 55:             # the dragon: tuba, cellos, basses
            return [('tuba', 0, 0, 0.7), ('cellos', 0, -4, 0.5), ('basses', -12 if m >= 40 else 0, -6, 0.45)]
        if t < T_BURST and hand == 0 and d < 0.25 and m >= 72:                  # the flicker: violins and piccolo
            return [('violins', 0, -4, 0.5), ('piccolo', 0, -16, 0.3)]
        return None

    o.tutti([e[:4] + (e[5] if e[5] in (0, 1) else 0, e[5] == 'trem') for e in N if e[4] == 'orch'],
            size=lambda t: 0.7 if t < T_DRAGON else 1.0, role=role)
    rng = np.random.default_rng(8)
    strides = [e for e in N if e[4] == 'dragon']
    for t, d, m, v, part, k in strides[::3]:
        o.thunder(t, 0.15 + 0.08 * min(5, int(4 * (t - T_DRAGON) / (T_PANIC - T_DRAGON + 1e-9))),
                  float(rng.choice([-0.7, 0.7])), 0.45)
    fear = lambda tt: 0.1 + 0.6 * smoothstep(0.0, T_PANIC, tt) * (1 - smoothstep(T_BURST, T_BURST + 1.0, tt))
    o.fire(0.0, T_BURST + 1.5, fear, 0.0, crackle=16, seed=808)
    o.hit('crash', T_PANIC, 120, gain=0.55, pan=forge)                          # he dives behind the anvil
    o.hit('anvil', T_PANIC + 0.25, 100, gain=0.35, pan=forge)
    o.boom(T_BURST, end, 0.8)                                                   # Siegfried bursts in
    M.add('fx', whoosh(1.6, 300, 3000, 0.7, seed=81), T_BURST, 0.9, end)
    o.wind(T_BURST, T_ARRIVE + 3, 0.6, lambda tt: end + (forge - end) * smoothstep(T_BURST, T_ARRIVE, tt))
    o.fire(T_SLEEP[0], D + 0.5, lambda tt: 0.3 + 0.4 * smoothstep(T_SLEEP[0], D - 4, tt), forge, crackle=10,
           seed=809)
    o.effects([(0, -4), (T_DRAGON, -4), (T_PANIC, 0), (T_BURST + 2, 0), (T_BURST + 4, -6), (T_SLEEP[0], -6),
               (T_SLEEP[0] + 8, -9), (D, -7)])
