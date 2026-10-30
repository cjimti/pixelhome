"""The Dragon's Blood: the dragon lies dying, a dull ochre heap on the porch, Siegfried standing over it with the
sword. "Siegfried bin ich genannt": the red eyes open once more, weakly; on Fafner's last "Siegfried!" the
orchestra heaves and the heap sinks back into the cave mouth, which flushes red as it goes.

"So leite mich denn mein lebendes Schwert!": he pulls the sword out on a great C major chord, hot blood bursts
over his hand in a red splash with a hiss, and it burns like fire ("Wie Feuer brennt das Blut!"); he flares red
and puts his hand to his lips. And the forest comes alive: the Woodbird's music flutters in the woodwinds and
violins, every note a magenta ripple across the whole house as the bird darts in from the free end of Right;
the whole house blushes magenta, Siegfried wonders aloud in emerald ("als sprächen die Vöglein zu mir?"), and
innocent delight sparkles in magenta and green. Then the Woodbird sings, and he understands it: "Hei! Siegfried
gehört nun der Niblungen Hort! O, fänd' in der Höhle den Hort er jetzt!"

The music is Wagner's own: Act II, bars 1162 to 1166 and 1173 to 1201, as Solti's 1958 Vienna Philharmonic
recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Fafner's death on low
strings, bassoons and tuba, the sword's chords on brass and strings, the birdsong and forest on flutes, oboes,
violins and murmuring violas. The Woodbird's own line is not in the reduction, so it comes from the printed
vocal score (Breitkopf & Härtel, archive.org 31761034115105, p. 210) and is played as written on flute with a
breath of piccolo: the free 9-in-6 bars as Wagner's footnote asks, the last note of each phrase on the third
beat. The stage adds a growl of thunder deep in the cave as the dragon dies, the scrape of the sword coming out,
the hiss of the blood and the rush of its burning; the effects drop right away once the bird begins.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene; dragon(), breath(), hero() and bird() are the
dragon fight's own, shared with SF16 to SF19."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF19'
TITLE = "The Dragon's Blood"
KIND = 'show'
DESCRIPTION = ("The dying dragon whispers a warning and sinks into its cave. Siegfried tastes its burning blood, "
               "and suddenly he can understand what the woodbird is singing.")
VOICEOVER = ("A drop of dragon's blood burns Siegfried's hand. He puts it to his lips, "
             "and all at once he understands what the little bird is singing.")

K = 8                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1162-1166 and 1173-1201, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_WORDS = 0.0                               # Fafner's last words
T_EYES = (BAR[1164], BAR[1166])             # the eyes open once more and close
T_SINK = (BAR[1165] + 0.6, BAR[1167])       # "Siegfried!": the heap sinks back into the cave
T_BLOOD = BAR[1174]                         # the sword comes out: blood on his hand
T_BURN = BAR[1177] + 0.5                    # "Wie Feuer brennt das Blut!"
T_LIPS = BAR[1178] + 0.2
T_SONG = [BAR[1179], BAR[1184], BAR[1198]]  # the bird's music; the house blushes; the Woodbird sings
T_ANSWER = BAR[1189]                        # "als sprächen die Vöglein zu mir?"
T_CALL = BAR[1191]
T_DELIGHT = [BAR[1196]]                     # innocent delight


def _nine(b, notes, last):
    """A 9-in-6 bar of the Woodbird's song: nine quavers as triplets over the first two beats, the last note on the
    third (Wagner's footnote) -> [(bar, from, to, note)]."""
    out, x = [], 0.0
    for name, u in notes:
        out.append((b, x * 2 / 27, (x + u) * 2 / 27, name))
        x += u
    return out + [(b, 2 / 3, last[1], last[0])]


def _four(b, notes):
    """A 4/4 bar of the song against the 9/8: its first three crotchets fill the first two beats, the fourth the
    third (Wagner's footnote); notes [(name, from, to)] in quavers -> [(bar, from, to, note)]."""
    q = lambda x: x / 9 if x <= 6 else 2 / 3 + (x - 6) / 6
    return [(b, q(x0), q(x1), name) for name, x0, x1 in notes]


_RUN = [('E5', 1), ('C#5', 1.5), ('B4', 0.5), ('A4', 1), ('F#4', 1), ('A4', 1), ('C#5', 1), ('A4', 1), ('C#5', 1)]
# The Woodbird's first song, from the vocal score (Breitkopf & Härtel, p. 210): (bar, from, to, note) in bars.
WOODBIRD = ([(1198, 1 / 3, 8 / 9, 'F#5')] + _nine(1199, _RUN, ('E5', 8 / 9)) + [(1200, 1 / 3, 8 / 9, 'F#5')] +
            _four(1201, [('E5', 0, 2 / 3), ('C#5', 2 / 3, 4 / 3), ('B4', 4 / 3, 2), ('A4', 2, 2.5), ('F#4', 2.5, 3),
                         ('B4', 3, 4), ('E5', 4, 5), ('E5', 5, 6), ('E5', 6, 7)]))


def sung(lines):
    """A sung line [(bar, from, to, note)] -> [(time, seconds, midi)] on the excerpt's clock."""
    out = []
    for b, f0, f1, name in lines:
        seg = next(s['measures'] for s in EX['segments'] if s['measures'][0] <= b < s['measures'][1])
        ms, ts = zip(*sorted((m, t) for m, t in EX['bars'] if seg[0] <= m <= seg[1]))
        t0, t1 = float(np.interp(b + f0, ms, ts)), float(np.interp(b + f1, ms, ts))
        out.append((t0, t1 - t0, note(name)))
    return out


HEAP = 300.0

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
FIRE = colormap([(0.0, hexc('#300400')), (0.3, hexc('#ff2000')), (0.6, hexc('#ff5000')), (0.85, hexc('#ffb020')),
                 (1.0, hexc('#fff0b0'))])
LONG = 1.7                                  # the dragon spreads LONG times as far toward Right as toward Left
LIT = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)       # Act II by day


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k, tremolo). Fafner's death ('words'),
    the sword's chords ('sword'), the bird's music in the orchestra ('song', k = 0, 1, 2 as it grows, 'call',
    'delight') over the forest ('murmur'), Siegfried's wondering ('answer'), and the Woodbird's own line from the
    vocal score ('voice')."""
    N = []
    for t, d, m, v, h, *tr in tidy(EX['notes']):
        k, tr = None, bool(tr and tr[0])
        if t < BAR[1167] - 0.01:
            part = 'words'
        elif t < T_SONG[0] - 0.01:
            part = 'sword'
        elif h == 1 or m < note('B4'):
            part = 'answer' if T_ANSWER - 0.01 <= t < T_CALL - 0.01 and m >= 55 else 'murmur'
        elif t < T_ANSWER - 0.01:
            part, k = 'song', int(t >= T_SONG[1] - 0.01)
        elif t < T_CALL - 0.01:
            part = 'answer'
        elif t < T_DELIGHT[0] - 0.01:
            part = 'call'
        elif t < T_SONG[2] - 0.01:
            part = 'delight'
        else:
            part, k = 'song', 2
        N.append((float(t), float(d), int(m), int(v), part, k, tr))
    for t, d, m in sung(WOODBIRD):
        N.append((t, d, m, 104, 'voice', None, False))
    return sorted(N, key=lambda e: e[0])


def birdpath(G):
    """The Woodbird's hops: [(time, target)] from the free end of Right, ending on its perch at Right 0.3."""
    perch, L = at(G, 'Right', 0.3), G.pd.max()
    rng = np.random.default_rng(19)
    moves = []
    for t, d, m, v, part, k, tr in compose():
        if part in ('song', 'call', 'delight') and m >= note('B4') and t not in [mv[0] for mv in moves]:
            if part == 'song' and k == 0:
                u = len(moves)
                moves.append((t, L - 40 - (L - 40 - perch) * min(1.0, u / 8)))
            elif part == 'delight':
                moves.append((t, at(G, 'Right', rng.uniform(0.05, 0.6)) if rng.uniform() < 0.7
                              else at(G, 'Porch Right', rng.uniform(0.3, 1.0))))
            else:
                moves.append((t, perch + rng.uniform(-60, 60)))
    moves = [mv for mv in moves if mv[0] < T_SONG[2] + 3] + [(T_SONG[2] + 3.2, perch)]
    return sorted(moves), L + 40


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    N = [e[:6] for e in compose()]
    moves, start = birdpath(G)
    me = at(G, 'Porch Front', 0.3)
    words = [e for e in N if e[4] == 'words']
    song = [e for e in N if e[4] in ('song', 'call', 'voice') and e[2] >= note('B4')]
    answer = [e for e in N if e[4] == 'answer']
    delight = [e for e in N if e[4] == 'delight']
    twinkle = rng.uniform(0, 1, G.N)
    t_in = T_SONG[0] - 0.3

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LIT)
        lv['eyes'] = 0.7 * smoothstep(T_EYES[0], T_EYES[0] + 1, t) * (1 - smoothstep(T_EYES[1] - 1, T_EYES[1], t))
        fr = forest(S, T, lv)

        # the heap, heaving faintly on each of Fafner's last words, then sinking back into the cave
        sink = smoothstep(*T_SINK, t)
        breath_ = sum(np.exp(-max(t - e[0], 0) / 0.6) * (t >= e[0]) for e in words)
        fr = dragon(fr, S, T, HEAP * (1 - sink), (0.25 + 0.4 * min(1.0, breath_)) * (1 - sink), lv['eyes'], mid - 0.9 * HEAP)
        if T_SINK[0] <= t < T_SINK[1] + 3:
            fr += light(BLOOD, 0.8 * np.sin(np.pi * min(1.0, (t - T_SINK[0]) / (T_SINK[1] + 3 - T_SINK[0]))) * S['mouth'])

        # the blood on his hand: a red splash both ways; it burns, a red ring out to both ends; to his lips
        if T_BLOOD <= t < T_BLOOD + 2:
            a = t - T_BLOOD
            fr += light(BLOOD, np.exp(-a / 0.4) * np.exp(-((d - me) / 60) ** 2))
            fr += light(BLOOD, np.clip(sparks(S, [(T_BLOOD, 0.9, me)], t, 19, n=16, reach=0.5), 0, 1))
        if T_BURN <= t < T_BURN + 2.5:
            a = t - T_BURN
            fr += light(BLOOD, np.exp(-a / 0.9) * np.exp(-((np.abs(d - me) - 1300 * a) / (140 + 140 * a)) ** 2))
            fr += light(BLOOD, 0.8 * np.exp(-a / 0.4) * S['porch'])
        if T_LIPS <= t < T_LIPS + 1:
            fr += light(WHITE, 0.9 * np.exp(-(t - T_LIPS) / 0.15) * np.exp(-((d - me) / 12) ** 2))

        # the bird's song, clear at last: magenta ripples across the whole house on every note
        pb = hops(moves, t, start)
        for t0, dur, m, v, part, k in song:
            a = t - t0
            if 0 <= a < 1.4:
                g = (0.7 if part == 'song' else 1.0) * np.exp(-a / (0.6 + 0.4 * (part == 'voice')))
                fr += light(BIRD, g * np.exp(-((np.abs(d - pb) - 1300 * a) / (80 + 100 * a)) ** 2))
                fr += light(BIRD, 0.5 * g * np.exp(-((d - pb) / 50) ** 2))
        blush = smoothstep(T_SONG[1] + 1.5, T_SONG[1] + 2.0, t) * (1 - smoothstep(T_SONG[1] + 2.5, T_SONG[1] + 5.0, t))
        fr += light(BIRD, 0.7 * blush * (0.85 + 0.15 * S['leaf'](T)))

        # he answers in emerald
        for t0, dur, m, v, part, k in answer:
            a = t - t0
            if 0 <= a < 1.4:
                fr += light(SIEGFRIED, 0.85 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - me) - 1200 * a) / (100 + 100 * a)) ** 2))

        # innocent delight: magenta and green points sparkle over the whole house, one set per note
        for t0, dur, m, v, part, k in delight:
            a = t - t0
            if 0 <= a < 0.5:
                pick = (twinkle + 0.37 * (m % 7)) % 1
                g = np.exp(-a / 0.18)
                fr += light(BIRD, 0.95 * g * (pick < 0.08))
                fr += light(SIEGFRIED, 0.85 * g * ((pick > 0.5) & (pick < 0.56)))

        # Siegfried, the sword still shining in his hand at first; he flares red when the blood burns
        burn = np.exp(-max(t - T_BURN, 0) / 0.5) * (t >= T_BURN) * (t < T_BURN + 3)
        fr += light(STEEL, 0.55 * (1 - smoothstep(T_BLOOD, T_BLOOD + 3, t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * T))
                    * np.exp(-((d - me - 18) / 16) ** 2))
        flare = max(0.6 * burn, 0.5 * sum(np.exp(-max(t - e[0], 0) / 0.2) * (t >= e[0]) for e in answer[:1]))
        fr = hero(fr, S, me, 0.8, min(0.8, flare), col=SIEGFRIED * (1 - burn) + BLOOD * burn)

        # the bird, once it has flown in
        if t >= t_in:
            fr = bird(fr, S, pb, hops(moves, t - 0.08, start), 0.9 * smoothstep(t_in, t_in + 0.3, t), T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, the Woodbird's line on flute, and the stage's sounds."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    moves, start = birdpath(G)
    bp = lambda t: pan_at(min(hops(moves, t, start), G.pd.max()))
    me = pan_at(at(G, 'Porch Front', 0.3))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=4.5)
    for t, d, m, v, part, k, trem in compose():
        if part == 'words':
            if m < 55:
                o.play('cellos trem' if trem else 'cellos', m, t, d, v, cave, 0.6)
                o.play('tuba' if m < 48 else 'bassoons', m, t, d, v - 10, cave, 0.45)
            else:
                o.play('violas', m, t, d, v - 6, cave, 0.45)
        elif part == 'sword':
            o.play('trombones' if m < 60 else 'horns', m, t, d, v, me, 0.6)
            o.play('violins' if m >= 55 else 'cellos', m, t, d, v - 6, me, 0.45)
        elif part in ('song', 'call', 'delight'):
            o.play('flutes' if m < 86 else 'piccolo', m, t, d, v + 4, bp(t), 0.55)
            o.play('violins', m, t, d, v - 12, bp(t), 0.3)
        elif part == 'murmur':
            o.play('violas trem' if trem and m >= 48 else 'cellos trem' if trem else 'violas' if m >= 48 else 'cellos',
                   m, t, d, v - 8, 0.0, 0.4)
        elif part == 'answer':
            o.play('horns', m, t, d, v, me, 0.6)
        elif part == 'voice':                                           # the Woodbird sings
            o.play('flutes', m, t, max(d, 0.15), v, bp(t), 0.95)
            o.play('piccolo', m + 12, t, max(d, 0.15), v - 30, bp(t), 0.2)
    # the stage: the dragon dies, the sword comes out, the blood hisses and burns
    o.thunder(T_SINK[0], near=0.35, pan=cave, gain=0.8)
    o.hit('gong scrape', T_SINK[0] + 0.5, 100, gain=0.5, pan=cave)
    o.hit('scrape', T_BLOOD - 0.3, 110, gain=0.5, pan=me)
    o.clash(T_BLOOD, me, 104, 0.5)
    o.fire(T_BLOOD + 0.05, T_BLOOD + 1.8, level=0.7, pan=me, crackle=40, seed=191)
    o.wind(T_BURN - 0.1, T_BURN + 1.4, 1.0, pan=me, seed=192)
    o.hit('timpani', T_BURN, 110, pitch=-3, gain=0.5, pan=me)
    o.hit('triangle', T_LIPS, 90, gain=0.35, pan=me)
    o.effects([(0, -3), (T_LIPS + 1.0, -3), (T_SONG[0], -18)])
