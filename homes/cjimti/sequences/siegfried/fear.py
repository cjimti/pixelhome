"""Fear: the Wanderer has gone, and Mime is alone at the anvil, shaking. The flickering of Loge's fire (Donington
20a) runs through the violins and piccolos, and with every phrase of it tongues of fire leap up somewhere on the
house: a burst of red, orange and amber here, then there, then everywhere at once, more and bigger each time,
while Mime, sulphur yellow beside the anvil, twitches from side to side. The dragon he fears (Fafner, 57) growls
in the tubas, and two walls of blood red close in on him from the front corners of the porch, a lurch with every
note, until the whole house goes up in flame for a moment and he dives behind the anvil.

Siegfried's horn call (48) sounds from the forest and he bursts in at the free end of Right, an emerald comet
with a white-hot head, and a green wave sweeps the fire off the house from end to end. Mime tries to teach him
fear: he tells of the fire round a sleeping bride (the magic sleep, 16), and a ring of flame rises round the
porch with a violet glow on its summit while Siegfried brightens at every note. Fear? He wants to learn it, now:
his audacity (55) on the horns, each note an emerald blast out to one end of the house or the other. The fire
sinks; Mime is back by the anvil and Siegfried stands at the forge, ready for the next scene.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF08'
TITLE = 'Fear'
KIND = 'show'
DESCRIPTION = ('Alone in the cave, the dwarf sees fire leaping everywhere and a dragon closing in. Siegfried bursts '
               'back in and sweeps it all away: he has never been afraid, and wants to learn how.')
VOICEOVER = ('Alone in the dark, Mime sees fire everywhere. '
             'Then Siegfried bursts in, and asks what fear is.')

K = 7                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.5
T_LOGE = [2.0, 6.5, 11.0, 15.5, 20.0, 24.0, 28.0]     # the flickering fire, each phrase bigger
T_DRAGON = 21.0                             # Fafner in the tubas: the walls of red close in
T_PANIC = 30.5                              # the whole house in flame; he dives behind the anvil
T_HORN = 33.5                               # Siegfried's horn call from the forest
T_BURST = 36.0                              # he bursts in at the free end of Right
T_ARRIVE = 38.5                             # at the forge
T_SLEEP = [43.0, 54.0]                      # the fire round the sleeping bride
T_AUD = 65.0                                # his audacity: he wants to learn fear
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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_BURST, 'D2', 60, 'trem')
    for k, t0 in enumerate(T_LOGE):
        for t, m, v, d in play('loge_flicker', t0, 0.42 - 0.03 * min(k, 4), 0, 70 + 8 * k):
            add(t, d, m, v, 'loge', k)
    for t, m, v, d in play('fafner', T_DRAGON, 0.55, 0, 104):
        add(t, d, m, v, 'dragon')
    add(T_PANIC, 0.1, 'C1', 122, 'panic')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.4, 0, 100):
        add(t, d, m, v, 'horn')
    add(T_BURST, 0.1, 'C1', 120, 'burst')
    for k, t0 in enumerate(T_SLEEP):
        for t, m, v, d in play('sleep', t0, 0.5, 0, 70 + 10 * k):
            add(t, d, m, v, 'sleep', k)
    for t, m, v, d in play('siegfried_audacity', T_AUD, 0.45, 0, 112):
        add(t, d, m, v, 'audacity')
    for m in ('G2', 'D3', 'G3'):
        add(T_AUD + 7.0, D - T_AUD - 7.0, m, 60, 'glow')
    return sorted(N, key=lambda e: e[0])


def tongues(G):
    """Every tongue of fire Mime sees: [(time, where, width, strength)], one per note of the flicker."""
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
    sleep_on = [e for e in N if e[4] == 'sleep']
    aud = [e for e in N if e[4] == 'audacity']
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
            ring = sum(smoothstep(t0, t0 + 2.0, t) * (1 - smoothstep(t0 + 9.0, t0 + 11.5, t)) * (0.8 + 0.2 * k)
                       for k, t0 in enumerate(T_SLEEP))
            if ring > 0:
                fr += light(ORANGE, 0.75 * ring * porch * (1 - sleeper) * (0.7 + 0.3 * fl))
                fr += light(RED, 0.5 * ring * porch * np.clip(-fl, 0, 1))
                fr += light(VIOLET, 0.8 * ring * sleeper)
            glow = 0.0
            for t0, dd, m, v, part, k in sleep_on:
                if 0 <= t - t0 < 1.0 and m >= note('Eb4'):
                    glow = max(glow, np.exp(-(t - t0) / 0.35))

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
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.32, 0.22), ('strings', 0.26, 0.3), ('winds', 0.26, 0.32), ('brass', 0.3, 0.3),
                            ('perc', 0.3, 0.25), ('fx', 0.14, 0.3), ('harp', 0.22, 0.4), ('warm', 0.26, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
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
    S = stage(G)
    L = S['d'].max()
    mime = pan_at(at(G, 'Porch Front', MIME_AT))
    home = pan_at(at(G, 'Porch Front', SIEG_AT))
    mouth = pan_at(L)
    rng = np.random.default_rng(81)
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('low', ctrem, m, t, t + d, v, mime, rise=3.0, fall=1.0, gain=0.55)
        elif part == 'loge':
            pa = float(rng.uniform(-0.8, 0.8))
            M.add('strings', vln.play(m, v), t, 0.8, pa)
            M.add('winds', picc.play(m, v - 15), t, 0.5, pa)
            if k >= 3:
                M.add('harp', glock.play(m + 12, v - 25), t, 0.5, pa)
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.25), t, 0.95, mime)
            M.add('low', cb.play(m, v - 10, dur=d * 1.1, release=0.25), t, 0.7, mime)
            M.add('perc', timp.play(v - 20, pitch=-6), t, 0.6, mime)
        elif part == 'panic':
            M.add('perc', crash.play(v), t, 1.0)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9)
            M.add('perc', roll.play(110, dur=2.0), t, 0.7)
            M.add('fx', whoosh(1.5, 300, 4000, 0.8, seed=8), t - 0.2, 1.0)
        elif part == 'horn':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, mouth)
        elif part == 'burst':
            M.add('perc', crash.play(v), t + 2.5, 0.9, home)
            M.add('perc', timp.play(v, pitch=-3), t + 2.5, 0.9, home)
            M.add('fx', whoosh(2.5, 600, 5000, 0.8, seed=9), t, 1.0, mouth * 0.5)
        elif part == 'sleep':
            if m >= note('C4'):
                if d > 1.0:
                    hold('winds', flute if k else clar, m, t, t + d, v, 0.0, rise=0.3, fall=1.2, gain=0.8)
                else:
                    M.add('winds', clar.play(m, v, dur=d * 1.1, release=0.3), t, 0.9)
            else:
                M.add('harp', harp.play(m, v), t, 0.9)
                M.add('strings', vc.play(m, v - 10, dur=d * 1.1, release=0.4), t, 0.6)
        elif part == 'audacity':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.25), t, 0.95, home)
            M.add('strings', vc.play(m - 12, v - 10, dur=d * 1.1, release=0.25), t, 0.6, home)
            M.add('perc', timp.play(v - 25, pitch=-4), t, 0.4, home)
        elif part == 'glow':
            hold('warm', vc, m, t, t + d, v, home * 0.5, rise=3.0, fall=1.5, gain=0.55)
