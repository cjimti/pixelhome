"""The Spear Breaks: still the storm at the foot of the rock, the Wanderer waiting in deep blue at Right 0.6 with
the fire burning round the porch above. The Woodbird darts in from the free end of Right, a hot magenta spark,
hops toward him, sees the spear and flees back the way it came in a streak (its call, Donington 27a, squawking
on the piccolo). Behind it Siegfried's horn call (48) sounds from off, each note an emerald flash at the end of
Right, and he runs in after it and pulls up short in front of the old man.

They have it out. Each phrase of the Wanderer's chords (17) floods the house deep blue out from him, pushing
toward the free end of Right; each burst of Siegfried's audacity (55) throws it back in emerald, the line between
them swinging across the whole roofline. Then the Wanderer raises his spear (73): its pale shaft runs out
toward the boy note by note down the scale and the fire on the rock leaps up behind him. Siegfried draws
Nothung (43): white steel growing out from him to meet it, gold at the hilt. One stroke. The whole house
flashes blue-white, the shards of the spear fly out to both ends of the roofline, and the Wanderer's blue
collapses in on itself and is gone, the Twilight of the Gods (4) falling softly on the trombones.

Siegfried's strength (53) blazes out twice on the horns, emerald sweeping over the house toward the fire; the
storm thins, the fire round the rock flares, and he walks up to where the old god stood, alone, his horn call
ringing toward the flames.

compose() holds every note; stage(), sky(), figure() and fire() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF25'
TITLE = 'The Spear Breaks'
KIND = 'show'
DESCRIPTION = ('The Woodbird leads Siegfried to the foot of the rock, where the Wanderer bars the way. Blue and '
               'green fight for the house until one stroke of the sword shatters the spear and the old god is gone.')
VOICEOVER = ('An old man with a spear blocks the path to the fire. '
             'Siegfried draws his sword, and the spear breaks in two.')

K = 2                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_BIRD = 2.5                                # the Woodbird darts in
T_FLEE = 8.5                                # sees the spear, flees
T_HORN = 6.0                                # Siegfried's horn call from off
T_IN = 10.5                                 # he runs in
T_HALT = 13.0
DUEL = [(14.0, 'w', 0.5), (22.5, 's', 0.4), (29.0, 'w', 0.4), (35.5, 's', 0.35)]     # the argument
T_SPEAR = 41.0
T_SWORD = 46.5
T_STRIKE = 52.0
T_DOWN = 54.0
T_SIEG = [59.0, 63.5]
T_HORN2 = 68.0
T_WALK = (60.0, 72.0)
D = 80.0

STORM = hexc('#1a2ab0')
CLOUD = hexc('#4a6aff')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
SUNRISE = colormap([(0.0, hexc('#ff4080')), (0.5, hexc('#ffc020')), (1.0, hexc('#40a0ff'))])
SILVER = hexc('#f4f8ff')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
MOSS = hexc('#30c020')
EARTH = hexc('#3a2410')
ERDA_HI = hexc('#60ff30')
TWILIGHT = hexc('#a0207a')
EMERALD = hexc('#00ff40')
HERO_HEAD = hexc('#e8ffe8')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
BIRD = hexc('#ff30d0')
WHITE = hexc('#ffffff')

START = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF24 left it
END = dict(storm=0.4, rock=0.3, fire=0.6, wide=0.0, dawn=0.0, sleeper=0.0)          # where SF26 picks it up
WAND_AT = ('Right', 0.6)
HALT_AT = ('Right', 0.85)                   # where Siegfried pulls up in front of him


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky."""
    d = G.pd
    rng = np.random.default_rng(1871)       # the same clouds and rain in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        rain=Flicker(rng, G.N, 4.0, 11.0),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        jag=rng.uniform(0.3, 1.0, G.N),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def sky(S, T, lv):
    """The sky and the rock at shared time T with levels lv (storm, rock, fire, wide, dawn, sleeper)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.05 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.09 * T) + 1.1)
    st = STORM + (CLOUD - STORM) * u[:, None]
    fr = light(st, lv['storm'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(RAIN, 0.6 * lv['storm'] * S['sky'] * np.clip(S['rain'](T) - 1.0, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(SUNRISE(np.clip(0.15 + 0.7 * u + 0.15 * np.sin(0.2 * T), 0, 1)), lv['dawn'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'], lv['wide'])
    fr += light(SILVER, lv['sleeper'] * np.exp(-(S['db'] / 22) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))

def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_STRIKE, 'G1', 64, 'pedal')
    for t, m, v, d in play('woodbird', T_BIRD, 0.3, 0, 84):
        if t < T_FLEE:
            add(t, d, m, v, 'bird')
    for t, m, v, d in play('woodbird_call', T_FLEE, 0.18, 12, 104):
        add(t, d, m, v, 'squawk')
    for t, m, v, d in play('siegfried_horn', T_HORN, 0.32, 5, 96):
        add(t, d, m, v, 'horn', 0)
    for k, (t0, who, beat) in enumerate(DUEL):
        key = 'wanderer' if who == 'w' else 'siegfried_audacity'
        for t, m, v, d in play(key, t0, beat, 0 if who == 'w' else 3, 104 + 4 * k):
            add(t, d, m, v, who, k)
    for t, m, v, d in play('spear', T_SPEAR, 0.45, -12, 116):
        add(t, d, m, v, 'spear')
    for t, m, v, d in play('nothung', T_SWORD, 0.4, -5, 116):
        add(t, d, m, v, 'sword')
    add(T_STRIKE, 0.1, 'C1', 127, 'strike')
    for t, m, v, d in play('downfall', T_DOWN, 0.85, -12, 76):
        add(t, d, m, v, 'down')
    for k, t0 in enumerate(T_SIEG):
        for t, m, v, d in play('siegfried', t0, 0.5, -10, 112 + 6 * k):
            add(t, d, m, v, 'sieg', k)
    for t, m, v, d in play('siegfried_horn', T_HORN2, 0.34, 5, 108):
        add(t, d, m, v, 'horn', 1)
    for m in ('Eb2', 'Bb2', 'Eb3', 'G3'):
        add(T_SIEG[0], D - T_SIEG[0], m, 64, 'glow')
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength)]."""
    rng = np.random.default_rng(25)
    runs = ['Side', 'Left', 'Side', 'Left', 'Right', 'Side']
    ts = [1.0, 4.5, 9.5, 16.0, 24.0, 31.0, 37.0, 44.0, 49.5, 56.0, 62.0, 70.0]
    return [(float(t), runs[i % len(runs)], float(rng.uniform(0.75, 1.0)) * (1 - 0.4 * (t > T_STRIKE)))
            for i, t in enumerate(ts)]


def bird(G, t):
    """Where the Woodbird is at time t, in quick eased hops, and how bright."""
    L = G.pd.max()
    hops = [(T_BIRD, L + 20), (T_BIRD + 1.0, at(G, 'Right', 0.92)), (T_BIRD + 2.2, at(G, 'Right', 0.82)),
            (T_BIRD + 3.4, at(G, 'Right', 0.76)), (T_BIRD + 4.6, at(G, 'Right', 0.7)), (T_FLEE, at(G, 'Right', 0.71)),
            (T_FLEE + 0.6, L + 40)]
    p = hops[-1][1]
    for (t0, p0), (t1, p1) in zip(hops, hops[1:]):
        if t < t1:
            p = p0 + (p1 - p0) * smoothstep(max(t0, t1 - 0.25), t1, t)
            break
    lvl = smoothstep(T_BIRD, T_BIRD + 0.3, t) * (1 - smoothstep(T_FLEE + 0.4, T_FLEE + 0.7, t))
    return p, lvl


def hero(G, t):
    """Where Siegfried is at time t."""
    L = G.pd.max()
    p = L + 30 + (at(G, *HALT_AT) - L - 30) * smoothstep(T_IN, T_HALT, t)
    return p + (at(G, *WAND_AT) - at(G, *HALT_AT)) * smoothstep(T_WALK[0], T_WALK[1], t)


def render(G, seed=25):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    pw = at(G, *WAND_AT)
    horns = [e for e in N if e[4] == 'horn']
    duel = {k: sorted({e[0] for e in N if e[4] in 'ws' and e[5] == k}) for k in range(len(DUEL))}
    spear = [e[0] for e in N if e[4] == 'spear']
    sword = [e[0] for e in N if e[4] == 'sword']
    sieg = [sorted({e[0] for e in N if e[4] == 'sieg' and e[5] == k}) for k in range(2)]
    rng = np.random.default_rng(seed)
    shard_v = rng.uniform(600, 2800, 28) * rng.choice([-1, 1], 28)
    shard_life = rng.uniform(0.5, 1.4, 28)
    trail = []

    # the line between blue and green across the house: each phrase drives it toward the other's end
    line_pts = [(0.0, L + 200)]
    for k, (t0, who, beat) in enumerate(DUEL):
        line_pts += [(t0, line_pts[-1][1]), (t0 + 1.6, at(G, 'Right', 0.98) if who == 'w' else at(G, 'Left', 0.15))]
    line_pts += [(T_SPEAR, at(G, 'Right', 0.98))]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_STRIKE, START[k]), (T_WALK[1], END[k])]) for k in START}
        raise_ = smoothstep(T_SPEAR, T_SPEAR + 3, t) * (1 - smoothstep(T_STRIKE, T_STRIKE + 1.5, t))
        lv['fire'] += 0.35 * raise_
        fr = sky(S, T, lv)
        ps = hero(G, t)

        for tb, run, s in bolts():
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * s * np.exp(-a / 0.4) * (G.seg_of == run))

        # the argument: blue floods out from him, emerald from the boy, the line between swinging over the house
        if DUEL[0][0] <= t < T_STRIKE:
            b = keys(t, line_pts)
            fade = smoothstep(DUEL[0][0], DUEL[0][0] + 1.0, t) * (1 - smoothstep(T_SPEAR - 0.5, T_SPEAR + 1.5, t))
            blue = smoothstep(b + 70, b - 70, d)
            fr += light(WOTAN, 0.7 * fade * blue)
            fr += light(EMERALD, 0.65 * fade * (1 - blue))
            fr += light(WHITE, 0.55 * fade * np.exp(-((d - b) / 18) ** 2))
            for k, ons in duel.items():
                for t0 in ons:
                    a = t - t0
                    if 0 <= a < 0.6:
                        col = WOTAN if DUEL[k][1] == 'w' else EMERALD
                        src = pw if DUEL[k][1] == 'w' else ps
                        fr += light(col, 0.6 * np.exp(-a / 0.2) * np.exp(-((np.abs(d - src) - 900 * a) / 60) ** 2))

        # the Woodbird: a hot magenta spark in hops, white at the heart, a short trail; it flees from the spear
        pb, lb = bird(G, t)
        trail = (trail + [pb])[-6:]
        if lb > 0:
            for j, q in enumerate(trail):
                fr += light(BIRD, lb * (0.25 + 0.12 * j) * np.exp(-((d - q) / 8) ** 2))
            flap = 0.8 + 0.2 * np.sin(2 * np.pi * 9 * t)
            fr += light(BIRD, lb * flap * np.exp(-((d - pb) / 8) ** 2))
            fr += light(WHITE, 0.8 * lb * np.exp(-((d - pb) / 3) ** 2))

        # his horn call from off, and later on the way to the fire: emerald flashes at him on every note
        for t0, dur, m, v, part, k in horns:
            a = t - t0
            if 0 <= a < 0.9:
                src = L if k == 0 else ps
                fr += light(EMERALD, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - src) / (90 + 50 * k)) ** 2))
                if k == 1:
                    fr += light(EMERALD, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - src) - 1300 * a) / 90) ** 2))

        # the spear's shaft running out toward him note by note; Nothung's blade growing out to meet it
        if T_SPEAR <= t < T_STRIKE + 0.1:
            n = sum(1 for x in spear if x <= t)
            reach = (ps - pw) * 0.5 * n / len(spear)
            lo, hi = sorted((pw, pw + reach))
            fr += light(SPEAR, 0.95 * ((d >= lo) & (d <= hi)))
            j = n - 1                           # each step of the spear's descent lights one run, marching at him
            if j >= 0:
                a = t - spear[j]
                run = ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right'][min(5, j // 2)]
                fr += light(SPEAR, 1.0 * np.exp(-a / 0.5) * (G.seg_of == run))
                fr += light(WOTAN, 0.6 * np.exp(-a / 0.9) * (G.seg_of == run))
            fr += light(WOTAN, 0.35 * raise_ * S['sky'])
        if T_SWORD <= t < T_STRIKE + 0.1:
            n = sum(1 for x in sword if x <= t)
            reach = (pw - ps) * 0.48 * n / len(sword)
            lo, hi = sorted((ps, ps + reach))
            fr += light(STEEL, 1.0 * ((d >= lo) & (d <= hi)))
            fr += light(HILT, 1.0 * np.exp(-((d - ps) / 6) ** 2))
            for x in sword:                     # each note of Nothung: white steel streaking out to both ends
                a = t - x
                if 0 <= a < 1.2:
                    fr += light(STEEL, 1.0 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - ps) - 2000 * a) / 90) ** 2))

        # the stroke: the whole house blue-white for a moment, shards out to both ends, his blue imploding
        a = t - T_STRIKE
        if 0 <= a < 0.5:
            fr += light(BOLT, 0.9 * np.exp(-a / 0.12))
        if 0 <= a < 2.0:
            mid = (pw + ps) / 2
            q = mid + shard_v * (1 - np.exp(-a / 0.6)) * 0.6
            life = np.exp(-a / shard_life)
            fr += light(SPEAR, np.clip((life[:, None] * np.exp(-((d[None, :] - q[:, None]) / 9) ** 2)).sum(0), 0, 1))
            fr += light(STEEL, 0.8 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - mid) - 1600 * a) / 80) ** 2))

        # the Wanderer, until the stroke; then his blue collapses in on itself
        gone = smoothstep(T_STRIKE, T_STRIKE + 2.5, t)
        if gone < 1:
            fr = figure(fr, S, pw, WOTAN, 0.85 * (1 - gone), w=16 * (1 - 0.7 * gone))
            if t < T_STRIKE:
                fr += light(SPEAR, 0.6 * np.exp(-((d - pw + 14) / 6) ** 2))
            if gone > 0:
                r = 500 * (1 - gone)
                fr += light(WOTAN, 0.9 * (1 - gone) * np.exp(-((np.abs(d - pw) - r) / 50) ** 2))

        # his strength: emerald sweeping out over the house toward the fire on every note
        for k, ons in enumerate(sieg):
            for t0 in ons:
                a = t - t0
                if 0 <= a < 1.4:
                    front = ps - 2200 * a
                    fr += light(EMERALD, (0.8 + 0.2 * k) * np.exp(-a / 0.7) * np.exp(-((d - front) / 220) ** 2))
                    fr += light(EMERALD, 0.5 * np.exp(-a / 0.5) * smoothstep(front - 60, front + 60, d))
                    fr += fire(S, T, 0.5 * np.exp(-a / 0.6), 0.0, boost=1.0)
            if ons and ons[0] <= t < ons[-1] + 1.0:
                fr += light(S['porch'][:, None] * FIRE(np.full(G.N, 0.9)), 0.3 * (1 - smoothstep(ons[-1], ons[-1] + 1, t)))

        # Siegfried
        if t >= T_IN - 0.3:
            lvl = 0.85 * smoothstep(T_IN - 0.3, T_IN + 0.3, t)
            fr = figure(fr, S, ps, EMERALD, lvl)
            fr += light(HERO_HEAD, 0.7 * lvl * np.exp(-((d - ps) / 5) ** 2))
            if t > T_STRIKE:                    # alone now: his green reaching up toward the fire
                g = smoothstep(T_STRIKE + 2, T_STRIKE + 6, t) * (1 - smoothstep(D - 5, D - 0.5, t))
                fr += light(EMERALD, 0.35 * g * np.exp(-np.clip(ps - d, 0, None) / 300) * (d <= ps)
                            * (0.75 + 0.25 * np.sin(2 * np.pi * ((ps - d) / 200 + 0.8 * t))))
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

    for name, gain, rev in (('low', 0.3, 0.25), ('strings', 0.24, 0.3), ('brass', 0.29, 0.3), ('perc', 0.28, 0.3),
                            ('winds', 0.24, 0.35), ('fx', 0.09, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vcs = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    pw = pan_at(at(G, *WAND_AT))
    for t, d, m, v, part, k in compose():
        ph = pan_at(hero(G, t))
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, pw, rise=2.0, fall=1.0, gain=0.4)
        elif part == 'bird':
            if m >= note('E5'):
                M.add('winds', flute.play(m - 12, v, dur=d * 1.05, release=0.15), t, 0.8, pan_at(bird(G, t)[0]))
        elif part == 'squawk':
            M.add('winds', picc.play(m - 12, v), t, 0.8, pan_at(bird(G, t)[0]))
        elif part == 'horn':
            src = 0.85 if k == 0 else ph
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9 if k else 0.6, src)
        elif part in 'ws':
            if part == 'w':
                if m >= note('Gb4'):
                    hold('brass', horn, m - 12, t, t + d, v - 6, pw, rise=0.15, fall=0.8, gain=0.7)
                elif m >= note('A3'):
                    hold('brass', tbn, m, t, t + d, v, pw, rise=0.12, fall=0.8, gain=0.8)
                else:
                    hold('low', tuba, m, t, t + d, v, pw, rise=0.12, fall=0.8, gain=0.85)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, ph)
                M.add('strings', vcs.play(m - 12, v - 10, dur=d * 1.05, release=0.25), t, 0.6, ph)
        elif part == 'spear':
            M.add('brass', tbn.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.9, pw)
            M.add('low', tuba.play(m, v - 6, dur=d * 1.05, release=0.3), t, 0.8, pw)
        elif part == 'sword':
            if d > 1.0:
                hold('brass', tpt, m, t, t + d, v, ph, rise=0.1, fall=0.6, gain=0.8)
            else:
                M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, ph)
        elif part == 'strike':
            mid = (pw + ph) / 2
            M.add('perc', crash.play(v), t, 1.0, mid)
            M.add('perc', gong.play(v), t, 0.9, mid)
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, mid)
            M.add('perc', timp.play(110, pitch=-9), t + 0.18, 0.9, mid)
            M.add('perc', roll.play(100, pitch=-5, dur=3.0), t + 0.3, 0.7, mid)
            M.add('fx', whoosh(1.8, 6000, 300, 0.9, seed=52), t - 0.05, 1.0, -0.4)
            M.add('fx', whoosh(1.8, 6000, 300, 0.9, seed=53), t - 0.05, 1.0, 0.85)
        elif part == 'down':
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, pw, rise=0.3, fall=1.2, gain=0.7)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.75, pw)
        elif part == 'sieg':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, ph)
            M.add('brass', tpt.play(m, v - 20, dur=d * 1.1, release=0.3), t, 0.4, ph)
            if t == T_SIEG[k]:
                M.add('perc', timp.play(v, pitch=-4), t, 0.8, ph)
                M.add('perc', crash.play(96 + 10 * k), t, 0.6, ph)
        elif part == 'glow':
            hold('strings', vcs, m, t, t + d, v, ph * 0.5, rise=3.0, fall=1.5, gain=0.5)
    for tb, run, s in bolts():
        M.add('perc', roll.play(int(70 + 30 * s), pitch=-3, dur=1.6), tb, 0.45, pan_at(at(G, run, 0.5)))
