"""The Reed Pipe: broad day in the forest outside Fafner's cave, gold shafts of sun moving through the green.
Siegfried lies under the lime tree at the middle of Left; the Woodbird, a hot magenta point, sits on Right and
its song flutters in the woodwinds, the bird hopping on every note and throwing magenta ripples over the house.

He cuts a reed with his sword (a white flick of steel) to answer it. Three times he tries, and the cor anglais
squawks out his attempts just as Wagner wrote them, lost and off the mark: each note a feeble sputter of pale
green that leaks out of him toward the bird and fizzles halfway, the last one a strangled high squawk, while the
bird hops further off in the silences. He gives up and blows his horn instead: Siegfried's horn call rings out,
faster and louder, every note an emerald sweep from him to both ends of the house and echoing back off the far
end, the third phrase a full emerald blaze. The bird flies away out of the free end of Right.

The horn has woken something. The dragon's motif climbs out of the depths in the tubas and basses, and the cave
mouth smoulders redder with each note; the ground heaves ochre, and two red eyes open in the dark of the porch.

The music is Wagner's own: Act II, the woodwinds' birdsong in bars 897 to 899, the reed-pipe scene in bars 904
to 914 and the end of the horn call to the dragon's waking in bars 989 to 1015, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
birdsong on flutes and oboes over murmuring strings, the reed on the oboe, the horn call on a solo horn with its
echo thrown back off the free end of Right, the dragon on tubas, trombones and basses over a timpani roll. The
stage adds the sword's flick, a low growl in the earth as the dragon stirs and a gong and thunder of breath as
its eyes open; the effects stay down under the bird and the horn and come up for the dragon.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF16'
TITLE = 'The Reed Pipe'
KIND = 'show'
DESCRIPTION = ('Siegfried tries to answer a woodbird on a reed pipe and fails, three times. So he blows his horn '
               'instead, loud enough to fill the forest, and something in the cave opens its eyes.')
VOICEOVER = ('A little bird sings to Siegfried. He tries to answer it on a reed pipe, and cannot. '
             'So he blows his horn instead, and wakes the dragon.')

K = 5                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 897-899, 904-914 and 989-1015, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_REED = BAR[904]                           # the reed-pipe scene starts where the birdsong breaks off
T_CUT = T_REED - 0.55                       # he cuts the reed
T_TRY = [BAR[904], BAR[907], BAR[911]]      # three tries on the reed
T_LAUGH = BAR[914] + 2.4                    # the last squawk dies: he laughs and gives up
T_HORN = [BAR[989], BAR[993], BAR[998]]     # the horn call's three phrases, faster and louder
T_BLAZE = BAR[1002]                         # its last long notes: a full emerald blaze
T_FLY = BAR[995]                            # the bird flies off
T_WAKE = BAR[1004]                          # the depths answer
T_STIR = BAR[1010]                          # the dragon's motif climbs
T_EYES = BAR[1015]                          # two red eyes open

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Before the reed the right hand is
    the woodwinds' birdsong ('song'), the left the murmur ('murmur'); the cor anglais's tries are the reed ('reed',
    k = which try); then the horn call ('horn', k = its phrase); from the waking the high notes still answer on the
    horn and everything below middle C is the dragon ('dragon'). 'rumble', 'growl' and 'eyes' are the stage."""
    N = []
    for t, d, m, v, h, *tr in tidy(EX['notes']):
        if t < T_REED - 0.01:
            part, k = ('song' if h == 0 else 'murmur'), None
        elif t < T_HORN[0] - 0.01:
            part, k = 'reed', sum(t >= x - 0.01 for x in T_TRY) - 1
        elif t < T_WAKE - 0.01 or (m >= 60 and t < T_STIR - 0.01):
            part, k = 'horn', min(2, sum(t >= x - 0.01 for x in T_HORN) - 1)
        else:
            part, k = 'dragon', None
        N.append((float(t), float(d), int(m), int(v), part, k))
    N.append((T_CUT, 0.3, note('E6'), 90, 'cut', None))
    N.append((T_WAKE, D - T_WAKE, note('Eb1'), 70, 'rumble', None))
    N.append((T_EYES, 0.5, note('C2'), 110, 'eyes', None))
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
    notes['laugh'] = [(T_LAUGH + 0.22 * j, 0.2, 60, 84, 'laugh', None) for j in range(5)]
    # in the silences between his tries the bird mocks him: rings of magenta, no sound
    notes['call'] = [(BAR[b] + 0.45 * j + 0.2, 0.3, note('E6'), 100, 'call', None)
                     for b in (906, 908, 910) for j in range(int((BAR[b + 1] - BAR[b]) / 0.45) - 1)]
    flick = Flicker(rng, G.N, 3.0, 9.0)
    lo, hi = note('F#1'), note('F3')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, LIT[k]), (T_WAKE, LIT[k]), (D - 2, END[k])]) for k in LIT}
        eyes = keys(t, [(T_EYES - 0.1, 0.0), (T_EYES + 0.15, 1.0), (T_EYES + 1.5, END['eyes'])])
        lv['eyes'] = eyes * (0.0 if T_EYES + 3.0 < t < T_EYES + 3.25 else 1.0)
        fr = forest(S, T, lv)

        # the bird's song: magenta ripples out from it on every note
        pb = hops(moves, t, perch)
        for part in ('song', 'call'):
            for t0, dur, m, v, _, k in notes[part]:
                a = t - t0
                if 0 <= a < 1.2 and m >= note('B4'):
                    g = np.exp(-a / 0.55)
                    fr += light(BIRD, g * np.exp(-((np.abs(d - pb) - 1100 * a) / (70 + 90 * a)) ** 2))
                    fr += light(BIRD, 0.5 * g * np.exp(-((d - pb) / 45) ** 2))

        # the reed: a pale green sputter that lurches toward the bird and fizzles halfway, in a puff of dull sparks
        for t0, dur, m, v, _, k in notes['reed']:
            a = t - t0
            if 0 <= a < 1.4:
                reach = (180 + 90 * k + 260 * ((m - 60) % 5) / 4) * min(1.0, a / 0.45)
                g = np.exp(-max(a - 0.45, 0) / 0.25)
                fr += light(REED, g * np.exp(-((d - me - reach) / (40 + 60 * a)) ** 2))
                fr += light(REED, 0.6 * g * ((d > me) & (d < me + reach)) * np.exp(-(me + reach - d) / 120))
                fr += light(REED, 0.7 * np.exp(-a / 0.15) * np.exp(-((d - me) / 40) ** 2))
                if a > 0.45:
                    fr += light(STONE, 0.8 * sparks(S, [(t0 + 0.45, 0.8, me + reach)], t, 160 + int(t0), 8, 0.12))
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
        blaze = smoothstep(T_BLAZE - 0.3, T_BLAZE + 0.3, t) * (1 - smoothstep(T_BLAZE + 1.0, T_BLAZE + 4.0, t))
        fr += light(SIEGFRIED, 0.75 * blaze * (0.8 + 0.2 * S['leaf'](T)))
        if T_BLAZE <= t < T_BLAZE + 0.6:
            fr += light(WHITE, 0.4 * np.exp(-(t - T_BLAZE) / 0.1))

        # the dragon stirs: the cave mouth smoulders redder and the ground heaves ochre on each note
        for t0, dur, m, v, _, k in notes['dragon']:
            a = t - t0
            if 0 <= a < 2.4:
                u = float(np.clip((m - lo) / (hi - lo), 0, 1))
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
    """Wagner's notes, orchestrated from the piano reduction, with the stage's sounds on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    moves, perch = birdpath(G)
    me = pan_at(at(G, 'Left', 0.5))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    far = pan_at(G.pd.max())
    o = Orchestra(M, level=2.8)
    for t, d, m, v, part, k in compose():
        pb = pan_at(min(hops(moves, t + 0.1, perch), G.pd.max()))
        if part == 'song':                                              # the bird in the woodwinds
            o.play('flutes', m, t, d, v + 6, pb, 0.7)
            if d >= 0.25:
                o.play('oboes', m, t, d, v - 8, pb, 0.3)
        elif part == 'murmur':
            o.play('violas trem' if m >= 48 else 'cellos trem', m, t, d, v - 6, 0.0, 0.45)
        elif part == 'reed':                                            # the cor anglais: his reed
            o.play('oboes', m, t, max(d, 0.3), v, me, 0.8)
        elif part == 'horn':                                            # the horn call, echoing off the far end
            o.play('horns', m, t, d, v + 6, me, 0.95)
            o.play('horns', m, t + 0.32, d, v - 22, far, 0.35)
        elif part == 'dragon':
            o.play('tuba', m, t, d, v, cave, 0.8)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 4, cave, 0.55)
            if m >= 43:
                o.play('trombones', m, t, d, v - 10, cave, 0.45)
        elif part == 'cut':                                             # the sword flicks through the reed
            o.hit('metal', t, 70, gain=0.25, pan=me)
            o.hit('triangle', t + 0.02, 80, gain=0.3, pan=me)
        elif part == 'rumble':                                          # the earth growls under the cave
            o.play('basses', m + 12, t, d, v, cave, 0.4)
            o.hit('timpani roll', T_STIR, 90, pitch=-6, gain=0.5, pan=cave)
            o.thunder(T_STIR + 4.0, near=0.25, pan=cave, gain=0.7)
        elif part == 'eyes':                                            # the eyes open
            o.hit('gong', t, 110, gain=0.6, pan=cave)
            o.hit('timpani', t, 120, pitch=-6, gain=0.8, pan=cave)
            o.thunder(t + 0.1, near=0.55, pan=cave, gain=0.8)
    # the effects: well down under the bird and the horn, up for the dragon
    o.effects([(0, -14), (T_WAKE, -14), (T_STIR, -4), (T_EYES - 1, 0)])
