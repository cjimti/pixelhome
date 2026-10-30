"""A Drink of Water: Siegmund lies spent by the hearth when Sieglinde comes out of the inner room: a light of
hearth amber pops up at the corner of Left and Side where the inner door is, sees a stranger on her floor and
creeps toward him while the cellos sing her motif of sympathy, the line that falls and the chords that lift. "Who
has come into the house and lies there by the hearth?" He stirs and asks for water, and she runs for it on the
strings' rushing figure, out through the main door at the free end of Right and back again with a cool glint of
water beside her, a dash the whole length of the house that sets the tree's hilt glinting as she passes. She
gives it to him; he drinks, shimmering, and for the first time they look at each other. The cellos play the love
of the twins: their two lights swell and pulse together, ripples of blue and amber run back and forth between
them, and as the melody climbs to its height the whole house warms.

Then he rises to go, misfortune follows him and he would not bring it on her, and moves toward the door under a
creeping shadow; the orchestra swells, "So bleibe hier!" she cries, misfortune already lives in this house, and
her cry rings out across the house. He comes back and sits by the fire beside her.

The music is Wagner's own: Act I, bars 157 to 161, Sieglinde finding the stranger; bars 184 to 199, the water and
the love of the twins; and bars 337 to 346, his farewell and her "So bleibe hier!", as Solti's 1958 Vienna
Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction of the score
(pixelhome/ring.py): her sympathy motif and the love of the twins on the cellos, with violins doubling the love
melody an octave up, the rushing figure on violins, the harmony on violas over the basses, and the last swell on
the full orchestra. Around the score, as a staging would: the hearth crackles and the storm blows outside, her
feet creep and then run the length of the house, the door lets in a gust and a far rumble, the water splashes as
she draws it and pours it, a dark scrape as his shadow falls, his slow steps toward the door, and a cymbal on
her cry. The effects stay well back in this tender scene; they come forward only for her dash out of the door
into the storm, and all but vanish under the love of the twins.

compose() tags every note of the excerpt, choreography() every move; stage(), room() and figure() are the hut and
the people in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK03'
TITLE = 'A Drink of Water'
KIND = 'show'
DESCRIPTION = ('A woman finds the stranger by her fire. She runs for water, and when their eyes meet the music '
               'knows something they do not. He tries to leave; she begs him to stay.')
VOICEOVER = ('Sieglinde finds a stranger asleep by her fire. She brings him water, '
             'and when he looks up at her, neither of them can look away.')

EX = excerpt(__file__)                      # Act I, bars 157-161, 184-199 and 337-346, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_POP = 0.4                                 # she comes out of the inner room, on her motif
T_WAKE = BAR[161]                           # he stirs and asks for water
T_GO = BAR[184] + 0.3                       # "Erquickung schaff' ich": she runs for water, out the door
T_OUT = BAR[187]
T_GIVE = BAR[189]                           # she gives it to him: the love of the twins begins
T_PEAK = BAR[192]                           # the melody climbs to its height
T_LEAVE = BAR[337] + 0.3                    # he rises to go
T_STAY = BAR[343]                           # "So bleibe hier!"
T_SIT = BAR[345]

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
WATER = hexc('#b0e8ff')
MEAD = hexc('#ffc040')
FATE = hexc('#2a1a5a')
WHITE = hexc('#ffffff')

START = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.38)    # where WK02 left the hut
END = dict(bed=0.22, hearth=0.66, trunk=0.95, leaves=0.62, hilt=0.45, door=0.34)
SM_START = (0.42, 26.0)                     # Siegmund lying by the fire: level, width
SM_END = (0.5, 18.0)                        # sitting up
SL_END = (0.55, 16.0)                       # Sieglinde beside him at Left 0.3


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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Her motif of sympathy ('sym',
    k = 0, and her cry, k = 1), the rushing figure as she runs for the water ('run'), the love of the twins ('love'
    in the right hand, 'love_lo' in the left) and his farewell ('leave'); 'bass' is the left hand elsewhere."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        b = bar_of(t)
        if b < 185:
            part, k = ('sym', 0) if h == 0 else ('bass', None)
        elif b < 189:
            part, k = ('run', None) if h == 0 else ('bass', None)
        elif b < 200:
            part, k = ('love', None) if h == 0 else ('love_lo', None)
        elif b < 344:
            part, k = 'leave', h
        else:
            part, k = ('sym', 1) if h == 0 else ('bass', None)
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
    """Per frame: where Siegmund (0) and Sieglinde (1) are, how bright and how wide."""
    F = nframes(D)
    t = np.arange(F) * DT
    inner, home, near = at(G, 'Left', 0.03), at(G, 'Left', 0.5), at(G, 'Left', 0.38)
    seat, door = at(G, 'Left', 0.3), G.pd.max() + 30
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where
        rate[k][m] = r

    set_(0, 0, D, home, 3.0)
    set_(0, T_LEAVE + 0.5, T_STAY + 0.6, at(G, 'Left', 0.78), 1.6)
    set_(1, 0, D, inner, 3.0)
    set_(1, T_POP + 1.0, T_GO, near, 0.9)
    set_(1, T_GO, T_OUT + 0.6, door, 2.6)
    set_(1, T_OUT + 0.6, T_LEAVE + 1.5, near, 2.0)
    set_(1, T_LEAVE + 1.5, T_STAY + 1.0, at(G, 'Left', 0.6), 1.5)
    set_(1, T_STAY + 1.0, D, seat, 1.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    looks = np.array([keys(x, [(T_GIVE, 0.0), (T_GIVE + 1.5, 0.8), (T_PEAK, 0.9), (T_PEAK + 2, 1.3), (BAR[197], 1.2),
                               (BAR[199], 0.6), (T_LEAVE, 0.0)]) for x in t])
    sm_lvl = np.array([keys(x, [(T_WAKE - 0.5, SM_START[0]), (T_WAKE + 1.0, 0.58), (T_SIT, 0.58), (D - 2, SM_END[0])])
                       for x in t]) + 0.15 * looks
    sm_w = np.array([keys(x, [(T_WAKE, SM_START[1]), (T_WAKE + 1.5, SM_END[1])]) for x in t])
    sl_lvl = np.array([keys(x, [(T_POP, 0.0), (T_POP + 0.6, 0.62), (T_SIT, 0.62), (D - 2, SL_END[0])]) for x in t])
    sl_lvl = sl_lvl + 0.15 * looks
    return dict(t=t, pos=pos, lvl=np.array([sm_lvl, sl_lvl]), w=np.array([sm_w, np.full(F, SL_END[1])]), looks=looks)


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    love_on = np.array([e[0] for e in N if e[4] == 'love'])
    sym_on = np.array(sorted({e[0] for e in N if e[4] == 'sym'}))
    leave_on = np.array(sorted({e[0] for e in N if e[4] == 'leave'}))
    run_on = np.array([e[0] for e in N if e[4] == 'run'])
    tw = Flicker(rng, G.N, 3.0, 8.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sm, sl = C['pos'][0][f], C['pos'][1][f]
        lk = C['looks'][f]
        lv = {k: keys(t, [(0, START[k]), (T_SIT, START[k]), (D - 1, END[k])]) for k in START}
        lv['bed'] += 0.12 * lk
        lv['hearth'] += 0.1 * lk
        near = np.exp(-((sl - pf) / 160) ** 2)
        lv['leaves'] += 0.2 * near
        lv['hilt'] += 0.45 * near
        fr = room(S, T, lv)

        # their looks: the whole house warms in both their colours, ripples run back and forth between them
        if lk > 0:
            i = int(np.searchsorted(love_on, t, side='right')) - 1
            note_on = np.exp(-(t - love_on[i]) / 0.5) if i >= 0 else 0.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.06 * T))
            fr += light(SIEGMUND, lk * 0.24 * wave ** 4) + light(SIEGLINDE, lk * 0.24 * (1 - wave) ** 4)
            lo, hi = min(sm, sl) - 40, max(sm, sl) + 40
            span = smoothstep(lo - 60, lo, d) * smoothstep(hi + 60, hi, d)
            rip = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 50 - 0.7 * T))
            fr += light(SIEGMUND, lk * (0.35 + 0.25 * note_on) * span * rip)
            fr += light(SIEGLINDE, lk * (0.35 + 0.25 * note_on) * span * (1 - rip))
            ring = np.exp(-((np.abs(d - 0.5 * (sm + sl)) - 120 - 500 * (t - love_on[max(i, 0)])) / 80) ** 2)
            fr += light(WHITE, 0.25 * lk * note_on * ring)

        # he rises to go and a shadow creeps after him
        if T_LEAVE <= t < T_STAY + 3:
            g = smoothstep(T_LEAVE, T_LEAVE + 2, t) * (1 - smoothstep(T_STAY, T_STAY + 1.5, t))
            sh = np.exp(-((d - sm - 60) / 200) ** 2)
            fr = fr * (1 - 0.5 * g * sh)[:, None] + light(FATE, 0.5 * g * sh)
            # the orchestra swells under his farewell: each chord throws the shadow wider over the house
            j = int(np.searchsorted(leave_on, t, side='right')) - 1
            if j >= 0:
                a = t - leave_on[j]
                swell = smoothstep(BAR[339], T_STAY, t)
                fr += light(FATE, g * (0.2 + 0.5 * swell) * np.exp(-a / 0.4) * np.exp(-((d - sm) / (300 + 900 * swell)) ** 2))

        # her run for the water: each note of the strings' figure a spark in her wake
        j = int(np.searchsorted(run_on, t, side='right')) - 1 if len(run_on) else -1
        if j >= 0 and t - run_on[j] < 0.5 and t < T_GIVE:
            a = t - run_on[j]
            fr += light(WATER, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - sl + 40) / 70) ** 2))

        # the people
        fr = figure(fr, S, sm, SIEGMUND, C['lvl'][0][f], C['w'][0][f])
        j = int(np.searchsorted(sym_on, t, side='right')) - 1
        sing = 0.2 * np.exp(-(t - sym_on[j]) / 0.3) if j >= 0 else 0.0
        if C['lvl'][1][f] > 0:
            fr = figure(fr, S, sl, SIEGLINDE, C['lvl'][1][f] * (1 + sing), C['w'][1][f])
            if j >= 0 and t - sym_on[j] < 2.5:   # every note of her motif sends a wave of amber over the house
                a = t - sym_on[j]
                fr += light(SIEGLINDE, 0.5 * np.exp(-a / 0.9) * np.exp(-((np.abs(d - sl) - 60 - 420 * a) / 110) ** 2))
        if T_POP <= t < T_POP + 1.2:        # she appears in the inner doorway
            a = t - T_POP
            fr += light(SIEGLINDE, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - sl) - 150 * a) / 30) ** 2))
        for ts in (T_STAY, BAR[345], BAR[346]):    # "So bleibe hier!": her cry rings out across the house
            a = t - ts
            if 0 <= a < 2.5:
                fr += light(SIEGLINDE, 0.8 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - sl) - 520 * a) / 90) ** 2))
                fr += light(SIEGLINDE, 0.25 * np.exp(-a / 0.4))

        # the water and the mead she carries, and what they do when he drinks
        if T_OUT + 0.4 <= t < T_GIVE + 0.6:
            q = sl + 22 if t < T_GIVE else sl + 22 + (sm - sl - 22) * smoothstep(T_GIVE, T_GIVE + 0.6, t)
            fr += light(WATER, 0.75 * np.exp(-((d - q) / 9) ** 2) * (0.8 + 0.2 * tw(T)))
        if T_OUT - 0.2 <= t < T_OUT + 1.5:  # out at the door, the rain; she dips the horn
            a = t - T_OUT + 0.2
            fr += light(WATER, 0.6 * np.exp(-a / 0.5) * S['door'] * np.clip(tw(T), 0, None))
        if T_GIVE + 0.5 <= t < T_GIVE + 4:
            a = t - T_GIVE - 0.5
            fr += light(WATER, 0.5 * np.exp(-a / 1.2) * np.exp(-((d - sm) / 45) ** 2) * np.clip(0.5 + tw(T), 0, None))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: her motif and the love of the twins on the cellos (the
    love melody doubled an octave up by the violins as it climbs), the rushing figure on violins, the harmony on
    violas over the basses, and the last swell on the full orchestra."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C['pos'][k]))

    o = Orchestra(M, level=3.6)
    for t, d, m, v, part, k in compose():
        sm, sl = pan_of(0, t), pan_of(1, t)
        mid = 0.5 * (sm + sl)
        if part == 'sym':
            o.play('cellos', m - 12 if m >= 67 else m, t, d, v + 14, sl, 0.9)
            o.play('violas', m, t, d, v - 4, sl, 0.4)
            if k == 1:
                o.play('horns', m - 12, t, d, v - 10, sl, 0.5)
                o.play('violins', m, t, d, v - 6, sl, 0.5)
        elif part == 'run':
            o.play('violins', m, t, d, v + 6, sl, 0.6)
            if m >= 74:
                o.play('flutes', m, t, d, v - 10, sl, 0.35)
        elif part == 'love':
            o.play('cellos', m - 12, t, d, v + 10, mid, 0.85)
            o.play('violins', m, t, d, v - 12, mid, 0.4)
            if v >= 90:
                o.play('oboes', m, t, d, v - 20, sl, 0.3)
        elif part == 'love_lo':
            o.play('violas', m, t, d, v, mid, 0.5)
            if m < 52:
                o.play('basses', m - 12, t, d, v - 10, -0.2, 0.4)
        elif part == 'leave':
            if k == 0:
                o.play('violins', m, t, d, v, sm, 0.5)
                if v >= 98:
                    o.play('horns', m - 12, t, d, v - 14, sm, 0.45)
            else:
                o.play('cellos', m, t, d, v, sm, 0.6)
                o.play('basses', m - 12, t, d, v - 10, -0.2, 0.45)
        elif part == 'bass':
            o.play('cellos' if m >= 48 else 'basses', m, t, d, v + 6, -0.2, 0.6)
            if v >= 100:
                o.play('trombones', m, t, d, v - 16, 0.0, 0.4)
    o.hit('timpani', T_STAY, 104, pitch=-5, gain=0.5)
    o.hit('cymbal swell', T_STAY - 2.2, 80, gain=0.35)
    # the stage: the hearth crackles, the storm is outside, her feet run for water
    hearth, door = pan_at(at(G, 'Left', 0.5)), pan_at(at(G, 'Right', 0.95))
    o.fire(0.0, D, 0.28, hearth, crackle=13, seed=70)
    o.wind(0.0, D, 0.25, door, seed=71)
    o.hits['water'] = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    o.hit('hoof soft', T_POP, 70, pitch=4, gain=0.35, pan=pan_of(1, T_POP), fx=True)       # the inner door
    t = T_POP + 1.0
    while t < T_GO - 0.3:                   # she creeps toward him
        o.hit('hoof soft', t, 60, pitch=7, gain=0.3, pan=pan_of(1, t), fx=True)
        t += 0.75
    t = T_GO
    while t < T_OUT + 0.6 + (T_OUT - T_GO):  # she runs the length of the house and back
        o.hit('hoof soft', t, 84, pitch=8, gain=0.4, pan=pan_of(1, t), fx=True)
        t += 0.24
    o.boom(T_OUT + 0.4, door, 0.35)         # the main door: a gust and the storm's far rumble
    o.wind(T_OUT + 0.2, T_OUT + 3.5, 0.9, door, seed=72)
    o.thunder(T_OUT + 0.6, 0.15, door, gain=0.7, seed=73)
    for tw in (T_OUT + 0.5, T_GIVE + 0.2):  # water drawn, then poured for him to drink
        o.M.add('fx', o.hits['water'].play(90), tw, 0.6, pan_of(1, tw))
    # a tender scene: the effects stay back, lead only for her dash out of the door, and all but vanish for the
    # love of the twins
    o.effects([(0.0, -7.0), (T_GO - 0.5, -7.0), (T_GO, -2.0), (T_OUT + 3.5, 0.0), (T_GIVE - 0.5, -6.0),
               (T_GIVE + 1.5, -13.0), (BAR[199], -13.0), (T_LEAVE, -6.0), (T_STAY - 1.0, -8.0), (D, -9.0)])
    o.hit('gong scrape', T_LEAVE, 80, gain=0.4, pan=pan_of(0, T_LEAVE + 1), fx=True)      # the creeping shadow
    t = T_LEAVE + 0.5
    while t < T_STAY:                       # his slow steps toward the door
        o.hit('hoof', t, 70, pitch=-6, gain=0.4, pan=pan_of(0, t), fx=True)
        t += 1.1
    o.hit('crash', T_STAY, 96, gain=0.4, pan=pan_of(1, T_STAY))
