"""Hunding: Siegmund and Sieglinde sit by the fire when she hears her husband's horse; she starts up and hurries
across the house to the door at the free end of Right. Hunding comes in out of the night, and his motif (composed:
the Commons example is empty) comes with him: a heavy, dotted tread in the tubas and trombones, timpani on every
step. He is blood red wrapped in black, a light with a darkness round it that dims the room wherever he stands, and
each step of his entrance sends a wave of dark red rolling through the house. He stops in the doorway and his
glare crosses the whole house to the stranger by the fire. Sieglinde explains to her motif of sympathy (Donington
36): she found him exhausted and gave him a drink. "Heilig ist mein Herd": hospitality is sacred, he answers, to
his motif again, and takes his seat on Right, across the room from the hearth, while she serves the meal to a
plucked version of his tread.

Then he looks from one to the other. "Wie gleicht er dem Weibe!" How like the woman he is; the same gleaming
serpent shines in his eyes. Three times his red gaze sweeps over the house from Siegmund to Sieglinde and back,
and each time it passes, the two of them flash with the same pale glint at the same instant, while a cello and an
oboe play the same phrase of her motif together. He asks the guest who he is, and where he comes from; his motif
is quiet now, the room darker, and the cellos begin the stranger's answer.

compose() holds every note, choreography() every move; stage(), room() and figure() are the hut and the people
in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'WK04'
TITLE = 'Hunding'
KIND = 'show'
DESCRIPTION = ('The master of the house comes home: Hunding, heavy and dark, with the tubas treading under every '
               'step. He welcomes the guest because the law says he must, and then he notices how much the stranger '
               'looks like his wife.')
VOICEOVER = ('Hoofbeats outside. Hunding is home, and there is a stranger at his fire. '
             'He welcomes him, because the law says he must.')

K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
HBEAT = 0.6                                 # a quarter of Hunding's tread
T_HEAR = 3.5                                # she hears the horse
T_ENTER = 10.0                              # Hunding in the doorway, his motif twice over
T_EXPLAIN = 21.0                            # her motif of sympathy
T_HEILIG = 29.0                             # "Heilig ist mein Herd", his motif again; he takes his seat
T_MEAL = 34.0                               # she serves him
T_LIKE = [43.0, 47.0, 51.0]                 # "Wie gleicht er dem Weibe!": his gaze sweeps from one to the other
T_ASK = 58.0                                # who are you?
T_ANSWER = 67.0                             # the cellos begin Siegmund's answer
D = 80.0

HUT = hexc('#3a1a0a')
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
HUNDING = hexc('#8a0020')
GLEAM = hexc('#fff0c0')
WHITE = hexc('#ffffff')

START = dict(bed=0.22, hearth=0.66, trunk=0.95, leaves=0.62, hilt=0.45, door=0.34)    # where WK03 left the hut
END = dict(bed=0.18, hearth=0.6, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)
SM_REST = (0.5, 18.0)                       # Siegmund at Left 0.5: level, width
SL_START = (0.55, 16.0)                     # Sieglinde at Left 0.3
SL_END = (0.52, 16.0)                       # Sieglinde at Left 0.22
HU_END = (0.6, 20.0)                        # Hunding at Right 0.3

HUNDING_MOTIF = [(0, 1.5, 'D2'), (1.5, 0.5, 'D2'), (2, 1, 'F2'), (3, 0.75, 'E2'), (3.75, 0.25, 'C#2'),
                 (4, 1.5, 'D2'), (5.5, 0.5, 'A1'), (6, 2, 'D2')]     # composed: the tubas' heavy tread


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Hunding's hut as profiles over the house: the hearth on Left, the ash tree in the middle of Porch Front with
    its leaves over the porch and the sword's hilt in its trunk, the door at the free end of Right."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)       # the same fire, leaves and rain in every scene, so the cuts match
    trunk = np.exp(-((d - pf) / 16) ** 2)
    clumps = 0.55 + 0.45 * smooth_noise(rng, d, 45.0)
    return dict(
        d=d, pf=pf,
        hearth=np.exp(-((d - at(G, 'Left', 0.4)) / 125) ** 2),
        trunk=trunk,
        hilt=np.exp(-((d - pf) / 5) ** 2),
        canopy=porch * np.exp(-((d - pf) / 310) ** 2) * clumps * (1 - trunk),
        door=smoothstep(at(G, 'Right', 0.7), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.2),
        stir=Flicker(rng, G.N, 0.08, 0.35),
        rain=Flicker(rng, G.N, 4.0, 11.0),
    )


def room(S, T, lv):
    """The hut at shared time T with levels lv (bed, hearth, trunk, leaves, hilt, door)."""
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(HUT, lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(HEARTH, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(EMBER, 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAVES, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def figure(fr, S, p, col, lvl, w=18.0):
    """A person at path distance p: a body that stands in front of the room, and a soft halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.8 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.4 * lvl * np.exp(-((S['d'] - p) / (3.2 * w)) ** 2))


def brute(fr, S, p, lvl, w=20.0, dark=0.75):
    """Hunding: blood red in black. The room dims round him wherever he stands."""
    halo = np.exp(-((S['d'] - p) / (4.5 * w)) ** 2)
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - dark * min(1.0, lvl / 0.3) * np.maximum(halo, body))[:, None]
    return fr + light(HUNDING, lvl * body) + light(HUNDING, 0.3 * lvl * halo)


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    def hunding(t0, v, k):
        for b, d, m in HUNDING_MOTIF:
            add(t0 + b * HBEAT, d * HBEAT, m, v, 'hunding', k)

    add(0.0, T_HEAR, 'Bb2', 56, 'rest')
    add(0.0, T_HEAR, 'F3', 54, 'rest')
    add(0.0, D, 'D1', 62, 'pedal')
    for i in range(10):                     # hoofbeats outside, nearer and nearer
        add(T_HEAR + 0.6 * i, 0.2, 'D1', 50 + 6 * i, 'hoof')
        add(T_HEAR + 0.6 * i + 0.18, 0.2, 'A1', 46 + 6 * i, 'hoof')
    add(T_HEAR, 0.4, 'F5', 90, 'start')
    hunding(T_ENTER, 118, 0)
    hunding(T_ENTER + 8 * HBEAT, 112, 1)
    for t, m, v, d in play('sieglinde', T_EXPLAIN, 0.5, 0, 82):
        add(t, d, m, v, 'sym_hi' if m >= note('C4') else 'sym_lo')
    hunding(T_HEILIG, 96, 2)
    for i in range(int((T_LIKE[0] - T_MEAL) / HBEAT)):     # the meal: his tread, plucked
        b, d, m = HUNDING_MOTIF[i % len(HUNDING_MOTIF)]
        add(T_MEAL + i * HBEAT, HBEAT, m, 70, 'meal')
    phrase = [(b - 3.5, d, m) for b, d, m in melody('sieglinde') if m >= 60 and 3.5 <= b <= 6]
    for k, t0 in enumerate(T_LIKE):
        for b, d, m in phrase:
            add(t0 + 0.6 + b * 0.42, d * 0.42, m - 12 * (k == 2), 84 + 4 * k, 'like', k)
        add(t0, 2.6, 'D2', 92, 'glare', k)
    hunding(T_ASK, 80, 3)
    for m in ('D2', 'A2', 'F3'):
        add(T_ASK, D - T_ASK, m, 58, 'tense')
    for t, m, v, d in play('siegmund', T_ANSWER, 0.45, 0, 80):
        if m < note('D4'):
            add(t, d, m, v, 'answer')
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
    """Per frame: where Siegmund (0), Sieglinde (1) and Hunding (2) are, and Hunding's steps."""
    F = nframes(D)
    t = np.arange(F) * DT
    home, seat = at(G, 'Left', 0.5), at(G, 'Left', 0.22)
    hseat, door = at(G, 'Right', 0.3), G.pd.max() + 40
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where
        rate[k][m] = r

    set_(0, 0, D, home, 3.0)
    set_(1, 0, D, at(G, 'Left', 0.3), 3.0)
    set_(1, T_HEAR + 0.8, T_EXPLAIN + 6, at(G, 'Right', 0.45), 1.5)
    set_(1, T_EXPLAIN + 6, T_MEAL, at(G, 'Porch Right', 0.6), 1.2)
    set_(1, T_MEAL, T_MEAL + 4, hseat - 45, 1.6)
    set_(1, T_MEAL + 4, D, seat, 1.1)
    set_(2, 0, D, door, 3.0)
    steps = [T_ENTER + b * HBEAT for b, _, _ in HUNDING_MOTIF] + [T_ENTER + (8 + b) * HBEAT for b, _, _ in HUNDING_MOTIF]
    p = door
    for i, ts in enumerate(steps[:9]):
        p -= 25
        set_(2, ts, D, p, 6.0)
    walk = [T_HEILIG + b * HBEAT for b, _, _ in HUNDING_MOTIF]
    for i, ts in enumerate(walk):
        set_(2, ts, D, p + (hseat - p) * (i + 1) / len(walk), 5.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    hu = np.array([keys(x, [(T_ENTER - 0.3, 0.0), (T_ENTER + 0.3, 0.68), (T_ASK, 0.68), (D - 2, HU_END[0])]) for x in t])
    sl = np.array([keys(x, [(0, SL_START[0]), (D - 4, SL_END[0])]) for x in t])
    return dict(t=t, pos=pos, hu=hu, sl=sl, steps=steps + walk)


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    stomp = np.array([e[0] for e in N if e[4] == 'hunding'])
    like = [np.array([e[0] for e in N if e[4] == 'like' and e[5] == k]) for k in range(3)]
    sym_on = np.array(sorted({e[0] for e in N if e[4] in ('sym_hi', 'sym_lo')}))
    door_d = at(G, 'Right', 0.95)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sm, sl, hu = C['pos'][0][f], C['pos'][1][f], C['pos'][2][f]
        lv = {k: keys(t, [(0, START[k]), (T_ASK, START[k]), (D - 2, END[k])]) for k in START}
        entering = smoothstep(T_ENTER - 1, T_ENTER, t) * (1 - smoothstep(T_ENTER + 3, T_ENTER + 8, t))
        lv['door'] += 0.3 * entering
        lv['leaves'] += 0.15 * np.exp(-((sl - pf) / 160) ** 2)
        fr = room(S, T, lv)

        # each stamp of his tread: a wave of dark red rolls out from him through the house
        i = int(np.searchsorted(stomp, t, side='right')) - 1
        if i >= 0 and t - stomp[i] < 2.0:
            a = t - stomp[i]
            big = 1.0 if stomp[i] < T_HEILIG else 0.55
            r = 30 + 650 * a
            band = np.exp(-((np.abs(d - hu) - r) / 110) ** 2) * np.exp(-a / 0.6) * big
            fr = fr * (1 - 0.6 * band)[:, None] + light(HUNDING, 0.4 * band)

        # his glare: a red line crossing the house to the stranger by the fire
        if T_ENTER + 2 <= t < T_EXPLAIN + 2:
            g = smoothstep(T_ENTER + 2, T_ENTER + 4, t) * (1 - smoothstep(T_EXPLAIN, T_EXPLAIN + 2, t))
            head = hu + (sm - hu) * smoothstep(T_ENTER + 2, T_ENTER + 5, t)
            lo, hi = min(head, hu), max(head, hu)
            beam = smoothstep(lo - 20, lo + 20, d) * smoothstep(hi + 20, hi - 20, d)
            fr += light(HUNDING, 0.4 * g * beam * (0.7 + 0.3 * np.cos(2 * np.pi * (d / 80 + 0.8 * T))))

        # "wie gleicht er dem Weibe": his gaze sweeps from one to the other; they glint alike
        for k, t0 in enumerate(T_LIKE):
            if not t0 <= t < t0 + 4.0:
                continue
            a = t0 + 0.6
            u = smoothstep(t0, t0 + 2.6, t)
            head = hu + (min(sm, sl) - 60 - hu) * u
            g = smoothstep(t0, t0 + 0.3, t) * (1 - smoothstep(t0 + 2.6, t0 + 3.6, t))
            fr += light(HUNDING, 0.7 * g * np.exp(-((d - head) / 70) ** 2))
            fr += light(HUNDING, 0.25 * g * smoothstep(head - 20, head + 20, d) * smoothstep(hu + 20, hu - 20, d))
            j = int(np.searchsorted(like[k], t, side='right')) - 1
            if j >= 0:
                gl = np.exp(-(t - like[k][j]) / 0.25)
                for p in (sm, sl):
                    fr += light(GLEAM, 0.85 * gl * np.exp(-((d - p) / 9) ** 2))
                    fr += light(GLEAM, 0.3 * gl * np.exp(-((np.abs(d - p) - 40 - 300 * (t - like[k][j])) / 25) ** 2))

        # the people
        fr = figure(fr, S, sm, SIEGMUND, SM_REST[0], SM_REST[1])
        j = int(np.searchsorted(sym_on, t, side='right')) - 1
        sing = 0.25 * np.exp(-(t - sym_on[j]) / 0.3) if j >= 0 else 0.0
        fr = figure(fr, S, sl, SIEGLINDE, C['sl'][f] * (1 + sing), SL_START[1])
        if T_HEAR <= t < T_HEAR + 1.5:      # she starts up at the sound of the horse
            a = t - T_HEAR
            fr += light(SIEGLINDE, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - sl) - 250 * a) / 40) ** 2))
        lvl = C['hu'][f]
        if lvl > 0:
            fr = brute(fr, S, hu, lvl * (1 + 0.25 * (np.exp(-(t - stomp[i]) / 0.2) if i >= 0 else 0)), HU_END[1])
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

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C['pos'][k]))

    for name, gain, rev in (('low', 0.42, 0.22), ('strings', 0.36, 0.32), ('winds', 0.3, 0.35), ('brass', 0.33, 0.28),
                            ('harp', 0.3, 0.4), ('perc', 0.33, 0.26)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    tumba = M.hits('Percussion/Tumba-HitN_v[2-3]*.wav')

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

    door = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        sm, sl, hu = pan_of(0, t), pan_of(1, t), pan_of(2, t)
        if part == 'rest':
            hold('strings', vc if m < note('C3') else va, m, t, t + d, v, -0.4, rise=0.5, fall=1.5, gain=0.6)
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'hoof':
            M.add('perc', tumba.play(v), t, 0.7, door)
            M.add('low', pizz.play(m + 12, v), t, 0.5, door)
        elif part == 'start':
            M.add('winds', fl.play(m, v, dur=d, release=0.2), t, 0.6, sl)
        elif part == 'hunding':
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, hu)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, hu)
            if k < 2:
                M.add('brass', tbn.play(m + 19, v - 18, dur=d * 1.05, release=0.3), t, 0.5, hu)
            M.add('perc', timp.play(v, pitch=-4 if m % 12 == 2 else -9), t, 0.8, hu)
        elif part == 'sym_lo':
            M.add('strings', vc.play(m, v, dur=d * 1.1, release=0.35), t, 1.0, sl)
        elif part == 'sym_hi':
            M.add('winds', ob.play(m, v - 6, dur=d * 1.1, release=0.3), t, 0.7, sl)
        elif part == 'meal':
            M.add('low', pizz.play(m + 12, v), t, 0.9, hu)
        elif part == 'like':
            M.add('strings', vc.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.9, sm)
            M.add('winds', ob.play(m, v - 4, dur=d * 1.1, release=0.3), t, 0.8, sl)
            M.add('harp', harp.play(m, v - 10), t, 0.7, 0.5 * (sm + sl))
        elif part == 'glare':
            M.add('brass', tuba.play(m, v, dur=d, release=0.6), t, 0.8, hu)
            M.add('perc', roll.play(80, dur=d), t, 0.5, hu)
        elif part == 'tense':
            hold('low', ctrem if m > note('D2') else cb, m, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.6)
        elif part == 'answer':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, sm)
