"""The Last Question: the storm at the foot of the rock goes on. Erda stands green at the middle of Left, the
Wanderer in deep blue at the front of it, and he asks her how to stop the turning wheel. Her motif (Donington 3)
answers on the clarinets and bassoons, but each phrase breathes her green a little narrower and dimmer: she has
no answer. Each of his questions is a blue pulse thrown at her.

So he answers himself. The need of the gods (5a) beats on the brass and every chord flashes the sky violet; the
Twilight of the Gods (4) comes up on the trombones and the whole sky drains to a deep red-violet while his blue
grows round him: he wills the end. Then the vision: Siegfried's heroism (78) on the horns over the full
orchestra, and the house blazes with it, an emerald front running in from the free end of Right across every
run to the end of the Side, each phrase a gold surge after it, the world handed on to the hero.

"Hinab!" One thrust of the spear and Erda's green collapses into the ground at the middle of Left, a dark gulp
of earth and gone. The Wanderer's chords (17) sound again as he crosses round the rock to Right 0.6, and the
storm closes back in on him there, waiting for the boy.

compose() holds every note; stage(), sky(), figure() and fire() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF24'
TITLE = 'The Last Question'
KIND = 'show'
DESCRIPTION = ('Erda has no answer for the Wanderer. He wills the end of the gods himself, sees the world pass to '
               'a young hero in a blaze of green and gold, and sends the earth mother back into the ground.')
VOICEOVER = ('Even the earth mother has no answer. So the old god chooses the end, '
             'and gives the world to the hero.')

K = 1                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_ASK = [1.0, 5.5, 10.0]                    # his questions
T_ERDA = [2.5, 7.0, 11.5]                   # her answers, each weaker
T_NEED = 15.5                               # the need of the gods
T_DOWN = 23.0                               # the Twilight of the Gods
T_HERO = 34.0                               # the vision: Siegfried's heroism
HBEAT = 0.5
T_SINK = 48.5                               # "Hinab!"
T_WAND = 54.0                               # his chords as he crosses
T_WALK = (55.0, 69.0)
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
GOLD = hexc('#ffc020')

START = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)        # where SF23 left it
END = dict(storm=0.6, rock=0.3, fire=0.5, wide=0.0, dawn=0.0, sleeper=0.0)
WAND_FROM = ('Left', 0.8)
WAND_TO = ('Right', 0.6)                    # where he waits for Siegfried
ERDA_AT = ('Left', 0.35)


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

    add(0.0, T_SINK + 1, 'Db2', 66, 'earth')
    for k, t0 in enumerate(T_ASK):
        for t, m, v, d in play('wanderer', t0, 0.5, 0, 100 - 4 * k):
            if t < t0 + 1.0:
                add(t, d, m, v, 'ask', k)
    for k, t0 in enumerate(T_ERDA):
        for t, m, v, d in play('erda', t0, 0.55, 0, 84 - 10 * k):
            if t < t0 + 3.0:
                add(t, d, m, v, 'erda', k)
    for t, m, v, d in play('gotternoth', T_NEED, 0.62, 0, 104):
        add(t, d, m, v, 'need')
    for t, m, v, d in play('downfall', T_DOWN, 0.95, -12, 112):
        add(t, d, m, v, 'down')
    add(T_HERO, 0.1, 'C1', 125, 'crash')
    for t, m, v, d in play('siegfried_heroism', T_HERO, HBEAT, 2, 118):
        add(t, d, m, v, 'hero')
    for m in ('Bb1', 'F2', 'Bb2', 'D3', 'F3'):
        add(T_HERO, 12.0, m, 92, 'herobed')
    add(T_SINK, 0.5, 'Db1', 124, 'sink')
    for t, m, v, d in play('wanderer', T_WAND, 1.0, 0, 102):
        add(t, d, m, v, 'wanderer')
    for m in ('G1', 'D2', 'G2'):
        add(T_WALK[1], D - T_WALK[1], m, 62, 'dark')
    return sorted(N, key=lambda e: e[0])


def bolts():
    """Lightning: [(time, run, strength)]."""
    rng = np.random.default_rng(24)
    runs = ['Right', 'Side', 'Left', 'Right', 'Side', 'Left']
    ts = [0.2, 3.4, 8.8, 13.0, 19.0, 21.4, 30.5, 49.0, 52.0, 58.0, 62.5, 66.0, 70.0, 73.5, 77.0]
    return [(float(t), runs[i % len(runs)], float(rng.uniform(0.8, 1.0))) for i, t in enumerate(ts)]


def walk(G, t):
    """Where the Wanderer is at time t: round the rock from Left to Right."""
    a, b = at(G, *WAND_FROM), at(G, *WAND_TO)
    return a + (b - a) * smoothstep(T_WALK[0], T_WALK[1], t)


def render(G, seed=24):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    asks = [e for e in N if e[4] == 'ask']
    erda = [e for e in N if e[4] == 'erda']
    need = np.array(sorted({e[0] for e in N if e[4] == 'need'}))
    hero = [e for e in N if e[4] == 'hero']
    chords = sorted({e[0] for e in N if e[4] == 'wanderer'})
    p_erda = at(G, *ERDA_AT)
    lo_h = min(e[2] for e in hero)
    hi_h = max(e[2] for e in hero)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        down = smoothstep(T_DOWN, T_DOWN + 3, t) * (1 - smoothstep(T_HERO - 1, T_HERO + 1, t))
        vis = smoothstep(T_HERO - 0.2, T_HERO + 0.3, t) * (1 - smoothstep(T_SINK - 2, T_SINK, t))
        lv['storm'] = START['storm'] * (1 - 0.5 * down - 0.6 * vis)
        fr = sky(S, T, lv)
        p = walk(G, t)

        # lightning: a whole run cracks white
        for tb, run, s in bolts():
            a = t - tb
            if 0 <= a < 1.2:
                env = min(1.0, np.exp(-a / 0.1) + 0.8 * np.exp(-((a - 0.16) / 0.05) ** 2))
                fr += light(BOLT, s * env * (G.seg_of == run) * (0.5 + 0.5 * S['jag']))
                fr += light(CLOUD, 0.6 * np.exp(-a / 0.4) * (G.seg_of == run))

        # Erda: green that narrows and dims with each answer she cannot give; then she collapses into the ground
        weak = sum(smoothstep(t0 + 1.0, t0 + 3.0, t) for t0 in T_ERDA) / 3
        breath = 0.0
        for t0, dur, m, v, part, k in erda:
            a = t - t0
            if 0 <= a < dur + 1.2:
                breath = max(breath, (1 - 0.25 * k) * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.1, a))
        sink = smoothstep(T_SINK, T_SINK + 2.2, t)
        g = (1 - 0.35 * weak) * (1 - sink)
        w = (320 - 120 * weak) * (1 + 0.4 * breath) * (1 - 0.9 * sink) + 8
        if g > 0.005:
            fr += light(EARTH, 0.7 * g * np.exp(-((d - p_erda) / (w * 1.4)) ** 2))
            fr += light(MOSS, (0.8 + 0.3 * breath) * g * np.exp(-((d - p_erda) / w) ** 2))
            fr = figure(fr, S, p_erda, ERDA_HI, (0.6 + 0.3 * breath) * g, w=20)
        if T_SINK <= t < T_SINK + 3:            # the gulp of earth where she went down
            a = t - T_SINK
            fr += light(EARTH, 0.9 * np.exp(-a / 0.8) * np.exp(-((d - p_erda) / 120) ** 2))
            fr += light(MOSS, 0.8 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_erda) - 600 * a) / 60) ** 2))

        # his questions: blue pulses thrown at her
        for t0, dur, m, v, part, k in asks:
            a = t - t0
            if 0 <= a < 1.2:
                c = p + (p_erda - p) * min(1.0, a / 0.5)
                fr += light(WOTAN, 0.95 * np.exp(-a / 0.6) * np.exp(-((d - c) / 45) ** 2))

        # the need of the gods: each chord flashes the sky violet
        j = int(np.searchsorted(need, t, side='right')) - 1
        if j >= 0 and t - need[j] < 1.0 and t < T_DOWN:
            fr += light(DUSK, 0.75 * np.exp(-(t - need[j]) / 0.3) * S['sky'])

        # the Twilight of the Gods: the sky drains to red-violet, his blue grows round him
        fr += light(TWILIGHT, 0.85 * down * S['sky'] * (0.75 + 0.25 * np.sin(2 * np.pi * (d / 380 - 0.15 * t))))
        fr += light(WOTAN, 0.7 * down * np.exp(-((d - p) / (120 + 260 * down)) ** 2))

        # the vision: an emerald front from the free end of Right over every run, a gold surge on each note
        if T_HERO <= t < T_SINK:
            a = t - T_HERO
            front = L - min(1.0, a / 3.0) * (L + 60)
            fr += light(EMERALD, 0.85 * vis * smoothstep(front - 60, front + 60, d))
            fr += light(HERO_HEAD, 1.0 * np.exp(-((d - front) / 22) ** 2) * (a < 3.2))
            for t0, dur, m, v, part, k in hero:
                b = t - t0
                if 0 <= b < 1.6:
                    u = (m - lo_h) / max(1, hi_h - lo_h)
                    r = (L + 100) * (1 - np.exp(-b / 0.5))
                    fr += light(GOLD, (0.75 + 0.3 * u) * np.exp(-b / 0.8) * np.exp(-(((L - d) - r) / 150) ** 2))
            fr += light(GOLD, 0.25 * vis * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 + 0.4 * t))))

        # the Wanderer, and the spear thrust that sends Erda down
        fr = figure(fr, S, p, WOTAN, 0.85)
        fr += light(SPEAR, 0.6 * np.exp(-((d - p + 14) / 6) ** 2))
        if T_SINK <= t < T_SINK + 1.5:
            a = t - T_SINK
            fr += light(BOLT, min(1.0, 1.2 * np.exp(-a / 0.08)) * np.exp(-((d - p) / 50) ** 2))
            fr += light(SPEAR, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - (p + (p_erda - p) * min(1.0, a / 0.25))) / 30) ** 2))
            fr += light(WOTAN, 0.6 * np.exp(-a / 0.3))
        for t0 in chords:
            a = t - t0
            if 0 <= a < 2.5:
                r = 1300 * (1 - np.exp(-a / 0.8))
                fr += light(WOTAN, 1.0 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - walk(G, t0)) - r) / 200) ** 2))
                fr += light(CLOUD, 0.5 * np.exp(-a / 0.5) * S['sky'])
        if t >= T_WALK[0]:                      # his cloak trailing blue behind him round the rock, then his wait
            fr += light(WOTAN, 0.55 * np.exp(-np.clip(d - p, 0, None) / 160) * (d >= at(G, *WAND_FROM)) * (d <= p + 20)
                        * (1 - smoothstep(T_WALK[1], T_WALK[1] + 3, t)))
            wait = smoothstep(T_WALK[1], T_WALK[1] + 2, t) * (1 - smoothstep(D - 4, D - 0.5, t)) * (0.5 + 0.5 * np.cos(2 * np.pi * (t - T_WALK[1]) / 3.2))
            fr += light(WOTAN, 0.6 * wait * np.exp(-((d - p) / 260) ** 2))
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

    for name, gain, rev in (('low', 0.26, 0.25), ('strings', 0.2, 0.3), ('brass', 0.24, 0.3), ('perc', 0.24, 0.3),
                            ('winds', 0.22, 0.35), ('fx', 0.08, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vcs = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
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

    erda_p = pan_at(at(G, *ERDA_AT))
    for t, d, m, v, part, k in compose():
        pw = pan_at(walk(G, t))
        if part == 'earth':
            hold('low', cb, m, t, t + d, v, erda_p, rise=1.0, fall=2.0, gain=0.55)
        elif part == 'ask':
            if m >= note('Gb4'):
                M.add('brass', horn.play(m - 12, v - 6, dur=d * 1.05, release=0.3), t, 0.7, pw)
            elif m >= note('A3'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, pw)
            else:
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, pw)
        elif part == 'erda':
            if m >= note('Db4'):
                hold('winds', clar, m - 12, t, t + d, v, erda_p, rise=0.3, fall=1.0, gain=0.8)
            elif m >= note('E3'):
                hold('winds', bsn, m, t, t + d, v, erda_p, rise=0.3, fall=1.0, gain=0.8)
            else:
                hold('low', vcs, m, t, t + d, v - 10, erda_p, rise=0.5, fall=1.0, gain=0.6)
        elif part == 'need':
            if m >= note('Db4'):
                M.add('brass', horn.play(m - 12, v - 6, dur=d * 1.1, release=0.3), t, 0.7, 0.0)
            else:
                M.add('brass', tbn.play(m, v - 6, dur=d * 1.1, release=0.3), t, 0.8, 0.0)
            if m < note('B2'):
                M.add('perc', timp.play(v - 10, pitch=-4), t, 0.6, 0.0)
        elif part == 'down':
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, 0.0, rise=0.2, fall=1.2, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, 0.0)
            M.add('low', tuba.play(m - 12, v - 16, dur=d * 1.05, release=0.3), t, 0.6, 0.0)
        elif part == 'crash':
            M.add('perc', crash.play(v), t, 0.9, 0.0)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, 0.0)
            M.add('fx', whoosh(2.5, 300, 5000, 0.8, seed=24), t - 0.3, 0.9, 0.8)
        elif part == 'hero':
            if d > 1.2:
                hold('brass', horn, m, t, t + d, v, 0.0, rise=0.12, fall=0.9, gain=0.9)
                hold('brass', tpt, m, t, t + d, v - 18, 0.0, rise=0.12, fall=0.9, gain=0.45)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.3), t, 0.95, 0.0)
            M.add('low', tbn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.6, 0.0)
        elif part == 'herobed':
            hold('strings', vln if m >= note('D3') else vcs, m + 12, t, t + d, v, 0.0, rise=0.5, fall=2.0, gain=0.5)
        elif part == 'sink':
            M.add('perc', gong.play(v), t, 0.9, erda_p)
            M.add('perc', timp.play(v, pitch=-9), t, 1.0, erda_p)
            M.add('low', cbs.play(m + 12, v), t, 0.8, erda_p)
            M.add('fx', whoosh(1.2, 2500, 150, 0.8, seed=48), t, 0.9, erda_p)
        elif part == 'wanderer':
            if m >= note('Gb4'):
                hold('brass', horn, m - 12, t, t + d, v - 6, pw, rise=0.2, fall=1.0, gain=0.7)
            elif m >= note('A3'):
                hold('brass', tbn, m, t, t + d, v, pw, rise=0.15, fall=1.0, gain=0.8)
            else:
                hold('low', tuba, m, t, t + d, v, pw, rise=0.15, fall=1.0, gain=0.85)
        elif part == 'dark':
            hold('low', vcs, m + 12, t, t + d, v, pan_at(at(G, *WAND_TO)), rise=3.0, fall=1.5, gain=0.5)
    for tb, run, s in bolts():
        M.add('perc', roll.play(int(70 + 30 * s), pitch=-3, dur=1.6), tb, 0.45, pan_at(at(G, run, 0.5)))
