"""The Reed Pipe: broad day in the forest outside Fafner's cave, gold shafts of sun moving through the green.
Siegfried lies under the lime tree at the middle of Left; the Woodbird, a hot magenta point, sits on Right and
sings its motif (Donington 27), hopping on every note and throwing magenta ripples out over the house.

He cuts a reed with his sword (a white flick of steel) to answer it. Three times he tries: a feeble sputter of
pale green leaks out of him toward the bird and fizzles halfway, the oboe squawking off key, and each time the
bird hops further off and answers with its own clear call (27a) in a bright magenta ring. He laughs and gives up,
and blows his horn instead: Siegfried's horn call (48), three times, louder each time, every note an emerald
sweep from him to both ends of the house, the last a full emerald blaze. The bird flies away out of the free end
of Right.

The horn has woken something. The dragon's motif (57) stirs in the tubas, slow, and the cave mouth smoulders
redder with each note; the ground heaves ochre, and two red eyes open in the dark of the porch.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF16'
TITLE = 'The Reed Pipe'
KIND = 'show'
DESCRIPTION = ('Siegfried tries to answer a woodbird on a reed pipe and fails, three times. So he blows his horn '
               'instead, loud enough to fill the forest, and something in the cave opens its eyes.')
VOICEOVER = ('A little bird sings to Siegfried. He tries to answer it on a reed pipe, and cannot. '
             'So he blows his horn instead, and wakes the dragon.')

K = 5                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_SONG = [1.5, 6.0]                         # the Woodbird sings
T_CUT = 11.0                                # he cuts the reed
T_TRY = [13.5, 22.5, 31.5]                  # three feeble tries on the reed
T_LAUGH = 40.0
T_HORN = [43.0, 49.0, 55.0]                 # the horn call, three times, louder each time
T_FLY = 50.0                                # the bird flies off
T_STIR = 61.0                               # the dragon's motif stirs
T_EYES = 72.0
D = 80.0

NIGHT = hexc('#14a878')
MOON = hexc('#6080ff')
DAY = hexc('#18a020')
SUN = hexc('#ffd040')
CAVE = hexc('#8a2000')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STONE = hexc('#8a8a80')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BIRD = hexc('#ff30d0')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
REED = hexc('#a0ff60')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, hexc('#ff2000')), (0.6, hexc('#ff5000')), (0.85, hexc('#ffb020')),
                 (1.0, hexc('#fff0b0'))])
LONG = 1.7                                  # the dragon spreads LONG times as far toward Right as toward Left
LIT = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)       # Act II by day
END = dict(LIT, cave=0.6, eyes=0.6)                                    # where SF17 picks it up


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The forest outside Fafner's cave as profiles over the house: the porch is the cave mouth (darkest at the
    back, the middle of Porch Front), Left, Right and Side the trees, with two eyes on Porch Front."""
    d = G.pd
    rng = np.random.default_rng(1857)       # the same trees and light in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    mid = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, mid=mid, porch=porch,
        trees=(~porch) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        mouth=porch * (0.35 + 0.65 * np.exp(-((d - mid) / 160) ** 2)),
        eyes=np.exp(-((d - at(G, 'Porch Front', 0.4)) / 5) ** 2) + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 5) ** 2),
        edge=porch * (1 - np.exp(-((d - mid) / 220) ** 2)),
        shaft_at=rng.uniform(0, d.max(), 9), shaft_v=rng.uniform(-14, 14, 9), shaft_w=rng.uniform(25, 60, 9),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        smoulder=Flicker(rng, G.N, 0.3, 1.5),
    )


def forest(S, T, lv):
    """The forest at shared time T with levels lv (night, day, shafts, cave, eyes)."""
    d, leaf = S['d'], S['leaf'](T)
    fr = light(NIGHT, lv['night'] * S['trees'] * (0.85 + 0.15 * leaf))
    fr += light(DAY, lv['day'] * S['trees'] * (0.8 + 0.2 * leaf))
    fr += light(NIGHT, 0.4 * (lv['night'] + lv['day']) * S['edge'])
    L = d.max()
    shafts = np.zeros_like(d)
    for p, v, w in zip(S['shaft_at'], S['shaft_v'], S['shaft_w']):
        c = (p + v * T) % L
        shafts += np.exp(-((d - c) / w) ** 2)
    shafts *= ~S['porch']
    fr += light(MOON, lv['shafts'] * (1 - min(1.0, 2 * lv['day'])) * shafts)
    fr += light(SUN, lv['shafts'] * min(1.0, 2 * lv['day']) * shafts)
    fr += light(CAVE, lv['cave'] * S['mouth'] * (0.75 + 0.25 * S['smoulder'](T)))
    fr += light(EYE, lv['eyes'] * S['eyes'])
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the forest, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
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


def hero(fr, S, p, lvl, flare=0.0, col=None):
    """Siegfried at path distance p: emerald with a white-hot head; flare brightens him for a moment."""
    fr = figure(fr, S, p, SIEGFRIED if col is None else col, lvl * (1 + flare))
    return fr + light(HEAD, min(1.0, lvl * (0.75 + flare)) * np.exp(-((S['d'] - p) / 5) ** 2))


def hops(moves, t, p0):
    """Where something is at t after quick hops [(time, target)], each eased over a quarter of a second."""
    p = p0
    for th, q in moves:
        if t < th:
            break
        p = p + (q - p) * smoothstep(th, th + 0.25, t)
    return p


def bird(fr, S, p, back, lvl, T):
    """The Woodbird at p (back: where it was a moment ago): hot magenta, a white-hot centre and a comet trail."""
    d = S['d']
    flick = 0.8 + 0.2 * np.sin(2 * np.pi * 9 * T)
    lo, hi = min(p, back), max(p, back)
    trail = ((d >= lo - 4) & (d <= hi + 4)) * np.exp(-np.abs(d - p) / 70)
    fr = fr + light(BIRD, lvl * flick * np.clip(np.exp(-((d - p) / 8) ** 2) + 0.75 * trail, 0, 1))
    return fr + light(WHITE, 0.85 * lvl * np.exp(-((d - p) / 3) ** 2))


def dragon(fr, S, T, ext, lvl, eyes=0.0, head=None, tail=0.0):
    """Fafner: black under a mass of ochre scales spreading ext toward Left from the cave's middle and LONG times
    that toward Right, onto the Right wing; broad bands of scale ripple through it as it breathes, its edges burn
    bright, two red eyes sit either side of its head, and its tail lashes out past the Right edge (tail: reach)."""
    d, c = S['d'], S['mid']
    if ext <= 0 or lvl <= 0:
        return fr
    x = d - c
    edge = np.where(x < 0, ext, LONG * ext)
    body = smoothstep(edge + 50, edge - 70, np.abs(x))
    fr = fr * (1 - 0.95 * min(1.0, lvl / 0.15) * body)[:, None]
    scales = np.clip(0.45 + 0.55 * np.sin(2 * np.pi * d / 55 - 4.0 * T) + 0.3 * np.sin(2 * np.pi * d / 150 + 1.3 * T),
                     0, 1)
    fr = fr + light(SCALE, lvl * body * (0.35 + 0.75 * scales))
    fr = fr + light(SUN, 0.35 * lvl * body * scales ** 6)
    fr = fr + light(SCALE, 0.9 * lvl * np.exp(-((np.abs(x) - edge) / 28) ** 2))
    if tail > 1:
        u = x - LONG * ext
        lash = (u > -40) * smoothstep(tail + 30, tail - 30, u)
        fr = fr * (1 - 0.8 * lash)[:, None] + light(SCALE, 0.95 * lvl * lash * (0.5 + 0.5 * np.clip(u / tail, 0, 1)))
        fr = fr + light(SUN, 0.9 * lvl * np.exp(-((u - tail) / 12) ** 2))
    if eyes > 0:
        h = c if head is None else head
        e = np.clip(np.exp(-((d - h + 13) / 4.5) ** 2) + np.exp(-((d - h - 13) / 4.5) ** 2), 0, 1)
        fr = fr * (1 - min(1.0, eyes) * e)[:, None] + light(EYE, eyes * e)
        fr = fr + light(EYE, 0.6 * eyes * np.exp(-((d - h) / 26) ** 2))
    return fr


def breath(S, flick, src, side, a, reach=1500.0, hold=1.6):
    """A blast of fire from the dragon's mouth at src along the roofline toward side (+1 Right, -1 Left), a seconds
    in: a white-hot front races out, the whole length roars red and orange and flickers, then burns out
    -> (N,3) PWM."""
    d = S['d']
    x = (d - src) * side
    front = reach * min(1.0, a / 0.8)
    body = smoothstep(-30, 20, x) * smoothstep(front + 30, front - 150, x)
    fade = np.exp(-max(a - hold, 0) / 0.5)
    heat = np.clip(1 - x / reach, 0, 1)
    v = np.clip(body * fade * (0.3 + 0.45 * heat) * (0.65 + 0.35 * flick), 0, 1)
    tip = np.exp(-((x - front) / 45) ** 2) * fade * (a < 0.9)
    return light(FIRE(v), np.clip(1.25 * v + 0.15 * body * fade, 0, 1)) + light(WHITE, 0.7 * tip)


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for k, t0 in enumerate(T_SONG):
        for t, m, v, d in play('woodbird', t0, 0.42, 0, 92):
            add(t, d, m, v, 'song', k)
    add(T_CUT, 0.3, 'E6', 90, 'cut')
    tries = [('F5', 'E5', 'Gb5', 'Eb5'), ('B4', 'Db5', 'C5', 'Bb4', 'C5'), ('Ab5', 'G5', 'A5', 'Gb5', 'G5', 'F5')]
    for k, t0 in enumerate(T_TRY):
        for j, m in enumerate(tries[k]):
            add(t0 + j * 0.42 + 0.06 * (j % 2), 0.36, m, 70 + 6 * (j % 3), 'reed', k)
        for t, m, v, d in play('woodbird_call', t0 + 4.2, 0.42, 0, 100):
            add(t, d, m, v, 'call', k)
    for j, m in enumerate(('G4', 'B4', 'D5', 'B4', 'G4')):
        add(T_LAUGH + j * 0.22, 0.2, m, 84, 'laugh')
    for k, t0 in enumerate(T_HORN):
        for t, m, v, d in play('siegfried_horn', t0, 0.5, 5 + 7 * (k == 2), 96 + 10 * k):
            add(t, d, m, v, 'horn', k)
    for t, m, v, d in play('fafner', T_STIR, 0.75, 0, 84):
        add(t, d, m, v, 'dragon')
    add(T_STIR, D - T_STIR, 'Eb1', 70, 'rumble')
    add(T_EYES, 0.5, 'C2', 110, 'eyes')
    return sorted(N, key=lambda e: e[0])


def birdpath(G):
    """The Woodbird's hops: [(time, target)] and when it is there at all."""
    perch = at(G, 'Right', 0.3)
    moves = []
    for t, d, m, v, part, k in compose():
        if part == 'song' and m >= note('B4'):
            moves.append((t, perch + 40 * ((len(moves) % 3) - 1)))
    rng = np.random.default_rng(16)
    p = perch
    for k, t0 in enumerate(T_TRY):
        p = at(G, 'Right', (0.42, 0.58, 0.74)[k])
        moves.append((t0 + 2.4, p))
        moves.append((t0 + 4.2, p + rng.uniform(-30, 30)))
    moves.append((T_FLY, at(G, 'Right', 0.92)))
    moves.append((T_FLY + 0.6, G.pd.max() + 60))
    return sorted(moves), perch


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    moves, perch = birdpath(G)
    me = at(G, 'Left', 0.5)
    notes = {p: [e for e in N if e[4] == p] for p in ('song', 'reed', 'call', 'horn', 'dragon', 'laugh')}
    flick = Flicker(rng, G.N, 3.0, 9.0)
    lo, hi = note('Eb2'), note('Gb3')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, LIT[k]), (T_STIR, LIT[k]), (D - 2, END[k])]) for k in LIT}
        eyes = keys(t, [(T_EYES - 0.1, 0.0), (T_EYES + 0.15, 1.0), (T_EYES + 1.5, END['eyes'])])
        lv['eyes'] = eyes * (0.0 if T_EYES + 3.0 < t < T_EYES + 3.25 else 1.0)
        fr = forest(S, T, lv)

        # the bird's song: magenta ripples out from it on every note
        pb = hops(moves, t, perch)
        for part in ('song', 'call'):
            for t0, dur, m, v, _, k in notes[part]:
                a = t - t0
                if 0 <= a < 1.2 and m >= note('B4'):
                    g = (0.75 if part == 'song' else 1.0) * np.exp(-a / 0.55)
                    fr += light(BIRD, g * np.exp(-((np.abs(d - pb) - 1100 * a) / (70 + 90 * a)) ** 2))
                    fr += light(BIRD, 0.5 * g * np.exp(-((d - pb) / 45) ** 2))

        # the reed: a feeble pale green sputter that fizzles halfway to the bird
        for t0, dur, m, v, _, k in notes['reed']:
            a = t - t0
            if 0 <= a < 0.6:
                reach = 100 + 50 * k + 500 * a
                fr += light(REED, 0.9 * np.exp(-a / 0.22) * np.exp(-((d - me - reach) / 45) ** 2))
                fr += light(REED, 0.5 * np.exp(-a / 0.12) * np.exp(-((d - me) / 40) ** 2))
        if T_CUT <= t < T_CUT + 0.8:
            a = t - T_CUT
            fr += light(STEEL, 0.95 * np.exp(-a / 0.12) * np.exp(-((d - me - 25 + 60 * a) / 10) ** 2))

        # the horn call: every note an emerald sweep from him to both ends; the third a full blaze
        for t0, dur, m, v, _, k in notes['horn']:
            a = t - t0
            if 0 <= a < 2.0:
                g = (0.75 + 0.15 * k) * np.exp(-a / 0.9)
                fr += light(SIEGFRIED, g * np.exp(-((np.abs(d - me) - 1500 * a) / (110 + 120 * a)) ** 2))
                fr += light(SIEGFRIED, 0.3 * g * np.exp(-a / 0.3))
        blaze = smoothstep(T_HORN[2] + 2.0, T_HORN[2] + 2.6, t) * (1 - smoothstep(T_HORN[2] + 3.0, T_HORN[2] + 6.0, t))
        fr += light(SIEGFRIED, 0.75 * blaze * (0.8 + 0.2 * S['leaf'](T)))
        if T_HORN[2] + 2.0 <= t < T_HORN[2] + 2.6:
            fr += light(WHITE, 0.4 * np.exp(-(t - T_HORN[2] - 2.0) / 0.1))

        # the dragon stirs: the cave mouth smoulders redder and the ground heaves ochre on each note
        for t0, dur, m, v, _, k in notes['dragon']:
            a = t - t0
            if 0 <= a < 2.4:
                u = (m - lo) / (hi - lo)
                r = (250 + 700 * u) * (1 - np.exp(-a / 0.8))
                fr += light(SCALE, (0.5 + 0.4 * u) * np.exp(-a / 0.9) * np.exp(-((np.abs(d - mid) - r) / (90 + 60 * u)) ** 2))
                fr += light(CAVE, (0.8 + 0.4 * u) * np.exp(-a / 0.5) * S['mouth'])
        if eyes:
            for u in (0.4, 0.6):
                fr += light(EYE, 0.55 * lv['eyes'] * np.exp(-((d - at(G, 'Porch Front', u)) / 16) ** 2))

        # Siegfried under the lime tree; he flares on the laugh and on every horn note
        flare = 0.0
        for part in ('horn', 'laugh'):
            for t0, dur, m, v, _, k in notes[part]:
                if 0 <= t - t0 < 0.5:
                    flare = max(flare, 0.4 * np.exp(-(t - t0) / 0.15))
        fr = hero(fr, S, me, 0.8, flare)

        # the bird, until it flies off the free end of Right
        if pb < L + 30:
            fr = bird(fr, S, pb, hops(moves, t - 0.08, perch), 0.9, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('winds', 0.4, 0.3), ('brass', 0.42, 0.32), ('strings', 0.3, 0.35), ('low', 0.42, 0.25),
                            ('perc', 0.36, 0.3), ('harp', 0.28, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    fl = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    fls = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    gong = M.hits('Percussion/gongHit_p.wav')

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

    moves, perch = birdpath(G)
    me = pan_at(at(G, 'Left', 0.5))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    for m in ('E3', 'Ab3', 'B3'):           # the forest under it all, murmuring
        hold('strings', va, note(m), 0.0, T_STIR, 50, 0.0, rise=3.0, fall=4.0, gain=0.5)
    for t, d, m, v, part, k in compose():
        pb = pan_at(min(hops(moves, t + 0.1, perch), G.pd.max()))
        if part == 'song':
            if m >= note('B4'):
                M.add('winds', fl.play(m, v), t, 0.9, pb)
            else:
                M.add('harp', harp.play(m + 12, v - 20), t, 0.6, pb)
        elif part == 'call':
            if d > 1:
                hold('winds', fls, m, t, t + d, v, pb, rise=0.05, fall=0.8, gain=0.7)
            else:
                M.add('winds', fl.play(m, v), t, 0.9, pb)
        elif part == 'cut':
            M.add('perc', harp.play(note('E6'), 80), t, 0.5, me)
        elif part == 'reed':
            M.add('winds', ob.play(m - 1 + (k % 2), v), t, 0.8, me)
        elif part == 'laugh':
            M.add('brass', horn.play(m - 12, v, dur=0.2, release=0.1), t, 0.7, me)
        elif part == 'horn':
            if d > 1:
                hold('brass', horn, m, t, t + d, v, me, rise=0.08, fall=0.9, gain=0.9)
            else:
                M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.25), t, 0.95, me)
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.4), t, 0.95, cave)
        elif part == 'rumble':
            hold('low', cb, m + 12, t, t + d, v, cave, rise=3.0, fall=1.5, gain=0.6)
        elif part == 'eyes':
            M.add('perc', timp.play(v, pitch=-6), t, 0.9, cave)
            M.add('perc', gong.play(100), t, 0.7, cave)
            hold('strings', vn, note('Eb4'), t, D, 64, cave, rise=0.5, fall=1.5, gain=0.45)
