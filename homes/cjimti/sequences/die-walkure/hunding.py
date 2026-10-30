"""Hunding: Siegmund and Sieglinde sit by the fire when she hears her husband's horse; she starts up and hurries
across the house to the door at the free end of Right. The basses rush up and the door crashes open: Hunding comes
in out of the night, and his motif comes with him, a heavy tread in the tubas and trombones, timpani on every step.
He is blood red wrapped in black, a light with a darkness round it that dims the room wherever he stands, and each
step of his entrance sends a wave of dark red rolling through the house. He stops in the doorway and his glare
crosses the whole house to the stranger by the fire. "Heilig ist mein Herd": hospitality is sacred, he answers,
and his motif treads again as he takes his seat on Right, across the room from the hearth. "Rüst uns Männern das
Mahl!" and she hurries to serve the meal while the strings bustle round her.

Then he looks from one to the other. "Wie gleicht er dem Weibe!" How like the woman he is; the same gleaming
serpent shines in his eyes. Three times his red gaze sweeps over the house from Siegmund to Sieglinde and back,
and each time it passes, the two of them flash with the same pale glint at the same instant, on the cellos'
quiet notes, while the room darkens round them.

The music is Wagner's own: Act I, bars 384 to 393, Hunding's arrival; bars 408 to 418, "Heilig ist mein Herd",
his motif and the meal; and bars 428 to 432, "Wie gleicht er dem Weibe!", as Solti's 1958 Vienna Philharmonic
recording takes them. The notes come from the Wagner Ring Dataset's piano reduction of the score
(pixelhome/ring.py): Hunding's motif on tubas and trombones with timpani, the upper parts on horns and violas,
the meal's bustle on the strings, and the glances on cellos and oboe. Around the score, as a staging would: the
hearth crackles; his horse gallops up outside; the door crashes open on a blast of night wind. His boots fall
heavy on every step, she hurries to the door, cups and plates clatter at the meal, a dark scrape goes with each
sweep of his gaze, and the storm rumbles far off as the room darkens. The horse and the door lead the entrance;
the effects recede under "Heilig ist mein Herd", come up a little for the meal, and are almost silent for the
glances, until the far thunder.

compose() tags every note of the excerpt, choreography() every move; stage(), room() and figure() are the hut and
the people in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK04'
TITLE = 'Hunding'
KIND = 'show'
DESCRIPTION = ('The master of the house comes home: Hunding, heavy and dark, with the tubas treading under every '
               'step. He welcomes the guest because the law says he must, and then he notices how much the stranger '
               'looks like his wife.')
VOICEOVER = ('Hoofbeats outside. Hunding is home, and there is a stranger at his fire. '
             'He welcomes him, because the law says he must.')

EX = excerpt(__file__)                      # Act I, bars 384-393, 408-418 and 428-432, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
ENTRANCE = range(386, 394)                  # his arrival: the motif's tread in the left hand, loud
SEATING = range(412, 415)                   # his motif again as he takes his seat
T_HEAR = BAR[385] + 0.3                     # she hears the horse, as the music stirs
T_ENTER = BAR[386] + 1.57                   # the basses' rush lands: Hunding in the doorway
T_EXPLAIN = BAR[393]                        # his glare holds until the great chord
T_HEILIG = BAR[408]                         # "Heilig ist mein Herd"
T_MEAL = BAR[415]                           # "Rüst uns Männern das Mahl!": she serves him
T_LIKE = [BAR[428] + 1.15, BAR[429] + 1.0, BAR[430] + 1.3]     # "Wie gleicht er dem Weibe!": his gaze sweeps
T_DARK = BAR[431]                           # the room darkens

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
CRIMSON = hexc('#ff1030')
WHITE = hexc('#ffffff')

START = dict(bed=0.22, hearth=0.66, trunk=0.95, leaves=0.62, hilt=0.45, door=0.34)    # where WK03 left the hut
END = dict(bed=0.18, hearth=0.6, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)
SM_REST = (0.5, 18.0)                       # Siegmund at Left 0.5: level, width
SL_START = (0.55, 16.0)                     # Sieglinde at Left 0.3
SL_END = (0.52, 16.0)                       # Sieglinde at Left 0.22
HU_END = (0.6, 20.0)                        # Hunding at Right 0.3


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). In his arrival and as he takes his
    seat the loud left hand is his motif ('hunding', k = 0 arriving, 2 seating); Sieglinde starting up ('start')
    and the bars round his words ('sym') are hers; the meal is 'meal'; the quiet notes under "Wie gleicht er dem
    Weibe!" are 'like' (k = which sweep of his gaze); the rest is 'upper' or 'bass'."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        b = bar_of(t)
        if b == 385:
            part, k = ('start' if h == 0 else 'bass'), None
        elif (b in ENTRANCE or b in SEATING) and h == 1 and v >= 85:
            part, k = 'hunding', 0 if b in ENTRANCE else 2
        elif b in (391, 392, 410):
            part, k = ('sym' if h == 0 else 'bass'), None
        elif 415 <= b <= 418:
            part, k = 'meal', h
        elif b >= 428:
            part, k = 'like', int(np.searchsorted(T_LIKE, t + 0.6) - 1) if t + 0.6 >= T_LIKE[0] else None
        else:
            part, k = ('upper' if h == 0 else 'bass'), None
        N.append((t, d, m, v, part, k))
    return N


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
    set_(1, T_HEAR + 0.8, T_EXPLAIN + 2, at(G, 'Right', 0.45), 1.5)
    set_(1, T_EXPLAIN + 2, T_MEAL, at(G, 'Porch Right', 0.6), 1.2)
    set_(1, T_MEAL, T_MEAL + 4, hseat - 45, 1.6)
    set_(1, T_MEAL + 4, D, seat, 1.1)
    set_(2, 0, D, door, 3.0)
    N = compose()
    steps = sorted({round(e[0], 2) for e in N if e[4] == 'hunding' and e[5] == 0})
    p = door
    for i, ts in enumerate(steps[:12]):
        p -= 25
        set_(2, ts, D, p, 6.0)
    walk = sorted({round(e[0], 2) for e in N if e[4] == 'hunding' and e[5] == 2})
    for i, ts in enumerate(walk):
        set_(2, ts, D, p + (hseat - p) * (i + 1) / len(walk), 5.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    hu = np.array([keys(x, [(T_ENTER - 0.3, 0.0), (T_ENTER + 0.3, 0.68), (T_DARK, 0.68), (D - 2, HU_END[0])]) for x in t])
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
    sym_on = np.array(sorted({e[0] for e in N if e[4] in ('sym', 'start')}))
    meal_on = np.array(sorted({e[0] for e in N if e[4] == 'meal'}))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sm, sl, hu = C['pos'][0][f], C['pos'][1][f], C['pos'][2][f]
        lv = {k: keys(t, [(0, START[k]), (T_DARK, START[k]), (D - 2, END[k])]) for k in START}
        entering = smoothstep(T_ENTER - 1, T_ENTER, t) * (1 - smoothstep(T_ENTER + 3, T_ENTER + 8, t))
        lv['door'] += 0.3 * entering
        lv['leaves'] += 0.15 * np.exp(-((sl - pf) / 160) ** 2)
        fr = room(S, T, lv)

        # each stamp of his tread: a wave of dark red rolls out from him through the house
        i = int(np.searchsorted(stomp, t, side='right')) - 1
        if i >= 0 and t - stomp[i] < 2.0:
            a = t - stomp[i]
            big = 1.0 if stomp[i] < T_HEILIG else 0.75
            r = 30 + 1400 * a
            band = np.exp(-((np.abs(d - hu) - r) / 140) ** 2) * np.exp(-a / 1.1) * big
            crest = np.exp(-((np.abs(d - hu) - r) / 45) ** 2) * np.exp(-a / 0.9) * big
            fr = fr * (1 - 0.6 * band)[:, None] + light(HUNDING, 0.7 * band) + light(CRIMSON, 0.75 * crest)

        # the meal: each note of the strings' bustle a spark round her as she hurries
        j = int(np.searchsorted(meal_on, t, side='right')) - 1
        if j >= 0 and t - meal_on[j] < 0.4 and T_MEAL <= t < T_LIKE[0] - 1:
            a = t - meal_on[j]
            off = 60 * np.sin(7.3 * meal_on[j])
            fr += light(SIEGLINDE, 0.8 * np.exp(-a / 0.15) * np.exp(-((d - sl - off) / 45) ** 2))
            fr += light(HEARTH, 0.25 * np.exp(-a / 0.2) * np.exp(-((d - sl) / 250) ** 2))

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
        if any(w == 'Hunding' and t0 <= t < t1 for t0, t1, w, _ in EX['singing']):     # he speaks: his light swells
            lvl *= 1.35
            fr += light(CRIMSON, 0.2 * (0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * t)) * np.exp(-((d - hu) / 400) ** 2))
        if lvl > 0:
            fr = brute(fr, S, hu, lvl * (1 + 0.25 * (np.exp(-(t - stomp[i]) / 0.2) if i >= 0 else 0)), HU_END[1])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: Hunding's motif on tubas and trombones with timpani on
    every step, the upper parts on horns and violas, Sieglinde's lines on cellos and oboe, the meal's bustle on the
    strings and bassoons, and the glances on cellos and oboe together."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C['pos'][k]))

    o = Orchestra(M, level=3.3)
    door = pan_at(at(G, 'Right', 0.95))
    stamps = set()
    for t, d, m, v, part, k in compose():
        sm, sl, hu = pan_of(0, t), pan_of(1, t), pan_of(2, t)
        if part == 'hunding':
            o.play('tuba', m - 12 if m >= 40 else m, t, d, v + 10, hu, 0.9)
            o.play('trombones', m if m >= 40 else m + 12, t, d, v, hu, 0.7)
            if k == 0:
                o.play('horns', m + 12, t, d, v - 12, hu, 0.4)
            if round(t, 2) not in stamps:
                stamps.add(round(t, 2))
                o.hit('timpani', t, v + 10, pitch=-4, gain=0.6, pan=hu)
        elif part in ('start', 'sym'):
            o.play('cellos' if m < 60 else 'oboes', m, t, d, v + 10, sl, 0.7)
            o.play('violas', m, t, d, v - 6, sl, 0.4)
        elif part == 'upper':
            o.play('horns' if v >= 85 else 'violas', m if m < 67 else m - 12, t, d, v, hu if t > T_ENTER else door, 0.6)
            if v >= 95:
                o.play('violins', m, t, d, v - 8, 0.3, 0.5)
        elif part == 'bass':
            o.play('cellos', m, t, d, v + 6, -0.2, 0.6)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v, 0.2, 0.5)
            if v >= 100:
                o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 6, hu, 0.6)
        elif part == 'meal':
            o.play('violins' if k == 0 else 'cellos', m, t, min(d, 0.2), v + 10, sl if k == 0 else hu, 0.55)
            if k == 1 and m < 48:
                o.play('bassoons', m, t, d, v, hu, 0.4)
        elif part == 'like':
            o.play('cellos', m, t, d, v + 24, sm, 0.8)
            o.play('oboes', m + 12, t, d, v + 14, sl, 0.35)
    o.hit('crash', T_ENTER, 104, gain=0.5, pan=door)
    o.hit('bass drum', T_ENTER, 112, gain=0.6, pan=door)
    o.hit('timpani roll', BAR[393], 90, gain=0.5, pan=0.4)
    # the stage: his horse outside, the door, his boots, the meal, the fire
    hearth = pan_at(at(G, 'Left', 0.5))
    o.fire(0.0, D, 0.28, hearth, crackle=13, seed=80)
    o.gallop(0.0, T_ENTER - 1.4, 0.44, door, v=110, gain=1.0)                    # his horse, coming up the path
    o.wind(T_ENTER - 0.3, T_ENTER + 3.0, 0.8, door, seed=81)                     # the night blows in
    o.boom(T_ENTER, door, 0.9)                                                    # the door crashes open
    for ts in C['steps']:                                                         # his heavy boots
        o.hit('hoof', ts, 118, pitch=-9, gain=0.6, pan=pan_of(2, ts), fx=True)
        o.hit('bass drum', ts, 80, gain=0.35, pan=pan_of(2, ts), fx=True)
    t = T_HEAR + 0.8
    while t < T_HEAR + 4.5:                                                       # she hurries to the door
        o.hit('hoof soft', t, 78, pitch=8, gain=0.35, pan=pan_of(1, t), fx=True)
        t += 0.3
    rng = np.random.default_rng(82)
    t = T_MEAL + 0.3
    while t < T_MEAL + 4.5:                                                       # the meal: cups and plates
        o.hit('metal', t, int(rng.uniform(50, 75)), pitch=float(rng.uniform(3, 9)), gain=0.25, pan=pan_of(1, t), fx=True)
        o.hit('hoof soft', t + 0.15, 70, pitch=8, gain=0.3, pan=pan_of(1, t), fx=True)
        t += float(rng.uniform(0.35, 0.7))
    # his horse and the door lead; his motif and "Heilig ist mein Herd" are clear; the glances are almost silent
    o.effects([(0.0, 0.0), (T_ENTER + 3.0, 0.0), (T_EXPLAIN, -5.0), (T_HEILIG, -9.0), (T_MEAL - 0.5, -9.0),
               (T_MEAL, -3.0), (T_MEAL + 5.0, -5.0), (T_LIKE[0] - 1.0, -11.0), (T_DARK, -11.0), (T_DARK + 0.3, -4.0),
               (D, -6.0)])
    for tl in T_LIKE:                                                             # his gaze sweeps the room
        o.hit('gong scrape', tl - 0.2, 70, gain=0.35, pan=0.0, fx=True)
    o.thunder(T_DARK, 0.15, door, gain=0.6, seed=83)                              # the storm still out there
