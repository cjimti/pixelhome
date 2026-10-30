"""A Drink of Water: Siegmund lies spent by the hearth when Sieglinde comes out of the inner room: a light of
hearth amber pops up at the corner of Left and Side where the inner door is, sees a stranger on her floor and
creeps toward him while the cellos sing her motif of sympathy (Donington 36), the line that falls and the
chords that lift. "Ein Quell! Ein Quell!": he stirs and asks for water, and she runs for it, out through the main
door at the free end of Right and back again with a cool glint of water beside her, a dash the whole length of
the house that sets the tree's hilt glinting as she passes. She gives it to him; he drinks, shimmering, and for
the first time they look at each other. A solo cello plays the love of the twins (37): their two lights swell
and pulse together, ripples of blue and amber run back and forth between them, and the whole house warms.

He asks who she is. This house and this woman belong to Hunding, she says, and at the name a dark red shadow
stirs at the door and the tubas mutter. She fetches mead from the storeroom, back through the inner door, and
returns with a glint of gold; she drinks first, then gives it to him, and their second long look is the love
motif again, fuller, with the oboe. Then he rises to go, misfortune follows him and he would not bring it on
her, and moves toward the door under a creeping shadow; "So bleibe hier!" she cries, misfortune already lives in
this house, and her motif rings out. He comes back and sits by the fire beside her.

compose() holds every note, choreography() every move; stage(), room() and figure() are the hut and the people
in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody, bass

CODE = 'WK03'
TITLE = 'A Drink of Water'
KIND = 'show'
DESCRIPTION = ('A woman finds the stranger by her fire. She runs for water, then brings him mead, and each time '
               'their eyes meet the music knows something they do not. He tries to leave; she begs him to stay.')
VOICEOVER = ('Sieglinde finds a stranger asleep by her fire. She brings him water, '
             'and when he looks up at her, neither of them can look away.')

K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
BEAT = 0.55
T_POP = 3.0                                 # she comes out of the inner room
T_SYM = 6.0                                 # her motif of sympathy
T_WAKE = 15.0                               # "Ein Quell!"
T_GO = 17.0                                 # she runs for water, out the door
T_OUT = 21.6
T_GIVE = 28.0
T_LOOK = [31.0, 54.0]                       # their looks: the love of the twins
T_HNAME = 42.0                              # "dies Haus und dies Weib sind Hundings Eigen"
T_MEAD = 46.0
T_TASTE = 51.0
T_LEAVE = 63.0                              # he rises to go
T_STAY = 67.0                               # "So bleibe hier!"
T_SIT = 72.0
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
WATER = hexc('#b0e8ff')
MEAD = hexc('#ffc040')
FATE = hexc('#2a1a5a')
WHITE = hexc('#ffffff')

START = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.38)    # where WK02 left the hut
END = dict(bed=0.22, hearth=0.66, trunk=0.95, leaves=0.62, hilt=0.45, door=0.34)
SM_START = (0.42, 26.0)                     # Siegmund lying by the fire: level, width
SM_END = (0.5, 18.0)                        # sitting up
SL_END = (0.55, 16.0)                       # Sieglinde beside him at Left 0.3

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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'D1', 64, 'pedal')
    for m in ('D2', 'A2'):
        add(0.0, T_SYM + 2.0, m, 60, 'rest')
    for m in ('F3', 'A3', 'C4'):
        add(T_HNAME + 3.0, T_LOOK[1] - T_HNAME - 3.0, m, 56, 'rest')
    for t, m, v, d in play('sieglinde', T_SYM, BEAT, 0, 84):
        add(t, d, m, v, 'sym_hi' if m >= note('C4') else 'sym_lo', 0)
    for i, m in enumerate(('D3', 'F3', 'A3')):
        add(T_WAKE + 0.4 * i, 0.9, m, 80 + 6 * i, 'wake')
    for j in range(16):                     # her run to the door and back
        add(T_GO + j * 0.28, 0.2, note('D4') + (0, 2, 3, 5, 7, 8, 10, 12)[j % 8] + 12 * (j // 8), 74 + j, 'run')
    for i, m in enumerate(('D5', 'F5', 'A5', 'D6')):
        add(T_OUT + 0.12 * i, 1.2, m, 72, 'water')
    for j in range(12):
        add(T_OUT + 1.2 + j * 0.42, 0.3, note('A4') - (0, 2, 4, 5, 7, 9)[j % 6], 66, 'back')
    for i, m in enumerate(('A5', 'F5', 'D5', 'A4')):
        add(T_GIVE + 0.18 * i, 1.4, m, 70, 'water')
    for k, t0 in enumerate(T_LOOK):
        for t, m, v, d in play('twins_love', t0, BEAT * (1 + 0.15 * k), 0, 86 + 6 * k, line='melody'):
            add(t, d, m - 12, v, 'love', k)
        for t, m, v, d in play('twins_love', t0, BEAT * (1 + 0.15 * k), 0, 62):
            if m < note('Bb4') and d >= 3 * BEAT:
                add(t, d, m, v, 'love_pad', k)
    for b, d, m in HUNDING_MOTIF[:3]:
        add(T_HNAME + b * 0.6, d * 0.6, m, 84, 'hunding')
    for i, m in enumerate(('F4', 'A4', 'C5', 'F5')):
        add(T_TASTE - 0.2 + 0.2 * i, 1.5, m, 62, 'mead')
    for t, m, v, d in play('siegmund_weary', T_LEAVE, 0.45, 0, 84):
        add(t, d, m, v, 'weary')
    for t, m, v, d in play('sieglinde', T_STAY, 0.42, 0, 104):
        add(t, d, m, v, 'sym_hi' if m >= note('C4') else 'sym_lo', 1)
    for m in ('Bb2', 'F3', 'D4'):
        add(T_SIT, D - T_SIT, m, 58, 'rest')
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
    set_(1, T_OUT + 0.6, T_MEAD, near, 2.0)
    set_(1, T_MEAD, T_MEAD + 2.6, inner, 3.5)
    set_(1, T_MEAD + 2.6, T_LEAVE + 1.5, near, 2.5)
    set_(1, T_LEAVE + 1.5, T_STAY + 1.0, at(G, 'Left', 0.6), 1.5)
    set_(1, T_STAY + 1.0, D, seat, 1.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    looks = sum(smoothstep(t0, t0 + 1.5, t) * (1 - smoothstep(t0 + 7.5, t0 + 10.5, t)) for t0 in T_LOOK)
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
    sym_on = np.array(sorted({e[0] for e in N if e[4] in ('sym_hi', 'sym_lo')}))
    tw = Flicker(rng, G.N, 3.0, 8.0)
    door_d = at(G, 'Right', 0.95)

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

        # Hunding's name: a dark red shadow stirs at the door
        if T_HNAME <= t < T_HNAME + 5:
            g = smoothstep(T_HNAME, T_HNAME + 0.8, t) * (1 - smoothstep(T_HNAME + 2.5, T_HNAME + 5, t))
            sh = np.exp(-((d - door_d) / 220) ** 2)
            fr = fr * (1 - 0.6 * g * sh)[:, None] + light(HUNDING, 0.45 * g * sh)

        # he rises to go and a shadow creeps after him
        if T_LEAVE <= t < T_STAY + 3:
            g = smoothstep(T_LEAVE, T_LEAVE + 2, t) * (1 - smoothstep(T_STAY, T_STAY + 1.5, t))
            sh = np.exp(-((d - sm - 60) / 200) ** 2)
            fr = fr * (1 - 0.5 * g * sh)[:, None] + light(FATE, 0.5 * g * sh)

        # the people
        fr = figure(fr, S, sm, SIEGMUND, C['lvl'][0][f], C['w'][0][f])
        j = int(np.searchsorted(sym_on, t, side='right')) - 1
        sing = 0.2 * np.exp(-(t - sym_on[j]) / 0.3) if j >= 0 else 0.0
        if C['lvl'][1][f] > 0:
            fr = figure(fr, S, sl, SIEGLINDE, C['lvl'][1][f] * (1 + sing), C['w'][1][f])
        if T_POP <= t < T_POP + 1.2:        # she appears in the inner doorway
            a = t - T_POP
            fr += light(SIEGLINDE, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - sl) - 150 * a) / 30) ** 2))
        if T_STAY <= t < T_STAY + 2.0:      # "So bleibe hier!"
            a = t - T_STAY
            fr += light(SIEGLINDE, 0.7 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - sl) - 380 * a) / 70) ** 2))

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
        if T_MEAD + 2.4 <= t < T_TASTE + 2.0:
            q = sl + 22 if t < T_TASTE + 1.0 else sl + 22 + (sm - sl - 22) * smoothstep(T_TASTE + 1.0, T_TASTE + 1.6, t)
            flare = 0.5 * np.exp(-max(t - T_TASTE, 0) / 0.5) * (t >= T_TASTE)
            fr += light(MEAD, (0.75 + flare) * np.exp(-((d - q) / 10) ** 2))
        if T_TASTE + 1.6 <= t < T_TASTE + 5:
            a = t - T_TASTE - 1.6
            fr += light(MEAD, 0.45 * np.exp(-a / 1.3) * np.exp(-((d - sm) / 50) ** 2))
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

    for name, gain, rev in (('low', 0.4, 0.22), ('strings', 0.32, 0.32), ('winds', 0.28, 0.35), ('brass', 0.3, 0.3),
                            ('harp', 0.3, 0.4), ('perc', 0.28, 0.28)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')

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
        sm, sl = pan_of(0, t), pan_of(1, t)
        mid = 0.5 * (sm + sl)
        if part == 'pedal':
            hold('low', cb, m, t, t + d, v, -0.3, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'sym_lo':
            M.add('strings', vc.play(m, v, dur=d * 1.1, release=0.35), t, 1.0, sl)
        elif part == 'sym_hi':
            M.add('winds' if k == 1 else 'strings', (ob if k == 1 else va).play(m, v - 6, dur=d * 1.1, release=0.3),
                  t, 0.7, sl)
        elif part == 'wake':
            M.add('brass', horn.play(m, v, dur=d, release=0.5), t, 0.8, sm)
        elif part == 'run':
            M.add('strings', vns.play(m, v), t, 0.7, sl)
        elif part == 'water':
            M.add('harp', harp.play(m, v), t, 1.0, door if t < T_GIVE else sm)
            M.add('winds', fl.play(m, v - 14, dur=d, release=0.4), t, 0.5, door if t < T_GIVE else sm)
        elif part == 'back':
            M.add('harp', harp.play(m, v), t, 0.7, sl)
        elif part == 'love':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, mid)
            if k == 1:
                M.add('winds', ob.play(m + 12, v - 14, dur=d * 1.05, release=0.5), t, 0.6, sl)
        elif part == 'love_pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, mid, rise=0.6, fall=1.2, gain=0.45)
        elif part == 'hunding':
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, door)
            M.add('perc', timp.play(70, pitch=-6), t, 0.5, door)
        elif part == 'mead':
            M.add('harp', harp.play(m, v), t, 0.9, sl)
            hold('winds', cl, m - 12, t, t + d, v - 10, sl, rise=0.3, fall=1.0, gain=0.5)
        elif part == 'weary':
            if d > 2:
                hold('brass', horn, m, t, t + min(d, 3.0), v - 10, sm, rise=0.3, fall=1.0, gain=0.6)
            else:
                M.add('brass', horn.play(m, v - 6, dur=d * 1.05, release=0.3), t, 0.8, sm)
        elif part == 'rest':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, mid, rise=2.0, fall=1.5, gain=0.6)
