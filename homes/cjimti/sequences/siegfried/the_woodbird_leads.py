"""The Woodbird Leads: day in the forest, Mime dead. Siegfried stands at the middle of Porch Front with the Ring's
glint on him; the Woodbird on Right sings, every note a hop and a flash: "Hei! Siegfried erschlug nun den
schlimmen Zwerg! Jetzt wüßt' ich ihm noch das herrlichste Weib: auf hohem Felsen sie schläft, Feuer umbrennt
ihren Saal..." and the house shows him: fire leaps up all over the porch with a silver sleeper burning at its
heart; "durchschritt' er die Brunst, weckt' er die Braut": the vision blazes out over the whole house.
"Brünnhilde wäre dann sein!"

Siegfried's freedom bursts out of him, emerald surging to both ends on every note. "So wird mir der Weg
gewiesen": the bird darts to him and away, again: follow me. "Wohin du flatterst folg' ich dir nach!" And the
race is on: the bird streaks out along Right in quick hops and Siegfried charges after it, an emerald comet with
a long wake sweeping the house green behind him, out of the free end of Right and gone, while the orchestra
storms to the end of the act; far off at the free end of Right the fire on the rock pulses and grows, licking
back along Right on every blow, and blazes up on the last chord: the way to the rock.

The music is Wagner's own: Act II, bars 1797 to 1810 and 1878 to the last chord, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
birdsong on flutes and violins over murmuring violas, Siegfried's freedom and the race on horns, trumpets and
violins over cellos, basses and timpani. The Woodbird's song comes from the printed vocal score (Breitkopf &
Härtel, archive.org 31761034115105, p. 245), played as written on flute. The stage adds the roar of the vision's
fire, Siegfried's running feet and the wind of his going, and crashes on the final chords; the effects stay
far down under the bird's song and come up for the race.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF22'
TITLE = 'The Woodbird Leads'
KIND = 'show'
DESCRIPTION = ('The bird sings of a bride asleep on a mountain inside a ring of fire. Siegfried has to find her, '
               'and he races after the bird across the whole house and away.')
VOICEOVER = ('The little bird sings of a bride, asleep on a mountain, inside a ring of fire. '
             'Siegfried runs after it.')

K = 11                                      # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1797-1810 and 1878 to the end, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
RING = 2.5                                  # the last chord rings on past the excerpt
D = EX['seconds'] + RING
BEAT = 0.5
T_SONG = [BAR[1797], BAR[1803]]             # the bird's song
T_VISION = [BAR[1801], BAR[1804]]           # "auf hohem Felsen sie schläft"; "durchschritt' er die Brunst"
T_FREE = BAR[1810]                          # Siegfried's freedom
T_DELIGHT = [BAR[1878] + 0.3, BAR[1879] + 0.3]   # "So wird mir der Weg gewiesen": the bird darts to him and away
T_HORN = BAR[1880]                          # "wohin du flatterst folg' ich dir nach!"
T_RUN = BAR[1881]                           # the race begins
T_FREE2 = BAR[1883]
T_GONE = BAR[1893]                          # both out of the free end of Right
T_FAR = BAR[1895]                           # the far fire
T_LAST = BAR[1910]                          # the last chord


def _nine(b, notes, last):
    """A 9-in-6 bar of the Woodbird's song: nine quavers as triplets over the first two beats, the last note on the
    third (Wagner's footnote) -> [(bar, from, to, note)]."""
    out, x = [], 0.0
    for name, u in notes:
        out.append((b, x * 2 / 27, (x + u) * 2 / 27, name))
        x += u
    return out + [(b, 2 / 3, last[1], last[0])]


_RUN = [('E5', 1), ('C#5', 1.5), ('B4', 0.5), ('A4', 1), ('F#4', 1), ('A4', 1), ('C#5', 1), ('A4', 1), ('C#5', 1)]
# The Woodbird's third song, from the vocal score (Breitkopf & Härtel, p. 245): (bar, from, to, note) in bars.
WOODBIRD = ([(1797, 1 / 3, 8 / 9, 'F#5')] + _nine(1798, _RUN, ('E5', 8 / 9)) + [(1799, 1 / 3, 8 / 9, 'F#5')] +
            _nine(1800, [('E5', 1), ('C#5', 1), ('B4', 1), ('A4', 2), ('C#5', 1), ('E5', 1), ('C#5', 1), ('E5', 1)],
                  ('A5', 1.0)) +
            [(1801, 1 / 6, 1 / 2, 'E5'), (1801, 1 / 2, 5 / 6, 'E5'), (1801, 5 / 6, 7 / 6, 'E5'),
             (1802, 1 / 6, 4 / 9, 'E5'), (1802, 4 / 9, 5 / 9, 'C#5'), (1802, 5 / 9, 2 / 3, 'F#5'), (1802, 2 / 3, 1, 'E5'),
             (1803, 1 / 6, 4 / 9, 'A5'), (1803, 4 / 9, 5 / 9, 'G#5'), (1803, 5 / 9, 2 / 3, 'E5'),
             (1803, 2 / 3, 7 / 9, 'C#5'), (1803, 7 / 9, 8 / 9, 'A4'), (1803, 8 / 9, 1, 'C#5'),
             (1804, 0, 1 / 3, 'E5'), (1804, 1 / 2, 2 / 3, 'E5'), (1804, 2 / 3, 5 / 6, 'B4'), (1804, 5 / 6, 11 / 12, 'E5'),
             (1804, 11 / 12, 1, 'G#5'), (1805, 0, 0.95, 'F#5'),
             (1806, 2 / 3, 5 / 6, 'B4'), (1806, 5 / 6, 11 / 12, 'E5'), (1806, 11 / 12, 1, 'G#5'), (1807, 0, 0.95, 'F#5'),
             (1808, 1 / 6, 1 / 2, 'E5'), (1808, 1 / 2, 5 / 6, 'E5'), (1808, 5 / 6, 7 / 6, 'E5'),
             (1809, 1 / 6, 4 / 9, 'E5'), (1809, 4 / 9, 5 / 9, 'C#5'), (1809, 5 / 9, 2 / 3, 'E5'), (1809, 2 / 3, 1, 'A5')])


def sung(lines):
    """A sung line [(bar, from, to, note)] -> [(time, seconds, midi)] on the excerpt's clock."""
    out = []
    for b, f0, f1, name in lines:
        seg = next(s['measures'] for s in EX['segments'] if s['measures'][0] <= b < s['measures'][1])
        ms, ts = zip(*sorted((m, t) for m, t in EX['bars'] if seg[0] <= m <= seg[1]))
        t0, t1 = float(np.interp(b + f0, ms, ts)), float(np.interp(b + f1, ms, ts))
        out.append((t0, t1 - t0, note(name)))
    return out

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
HOT = hexc('#fff0ff')
SILVER = hexc('#f4f8ff')
FIRE_R = hexc('#ff2000')
FIRE_O = hexc('#ff5000')
FIRE_A = hexc('#ffb020')

DAY_LV = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)


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



def woodbird(fr, S, pos, t, lvl, T):
    """The Woodbird: a hot magenta point with a white-hot centre, its wings flickering, a short comet trail."""
    d = S['d']
    flick = 0.78 + 0.22 * np.sin(2 * np.pi * 11 * T)
    for k, lag in enumerate((0.24, 0.16, 0.08)):
        fr = fr + light(BIRD, 0.35 * (k + 1) / 3 * lvl * np.exp(-((d - pos(t - lag)) / 9) ** 2))
    p = pos(t)
    fr = fr + light(BIRD, lvl * flick * np.exp(-((d - p) / 8) ** 2))
    fr = fr + light(BIRD, 0.35 * lvl * np.exp(-((d - p) / 30) ** 2))
    return fr + light(HOT, 0.8 * lvl * np.exp(-((d - p) / 3) ** 2))


def compose():
    """Every note, tagged: (time, seconds, midi, velocity, part, k, tremolo). The Woodbird's song ('bird') over the
    orchestra's birdsong ('birdbed') and the forest ('murmur'); Siegfried's freedom ('free', k = which burst); the bird
    darting ('delight'); "folg' ich dir nach" ('horn'); the race ('race' high, 'drive' low); at the end the far fire
    licks back on the orchestra's blows ('farfire'). The last chord rings on (RING seconds)."""
    N = []
    notes = tidy(EX['notes'])
    for t, d, m, v, h, *tr in notes:
        tr, k = bool(tr and tr[0]), None
        if t >= T_LAST - 0.01:
            d = d + RING
        if t < T_FREE - 0.01:
            part = 'birdbed' if h == 0 and m >= 72 else 'murmur'
        elif t < T_DELIGHT[0] - 0.31:
            part, k = ('free', 0) if h == 0 else ('drive', None)
        elif t < T_HORN - 0.01:
            part, k = ('delight', int(t >= T_DELIGHT[1] - 0.01)) if h == 0 else ('murmur', None)
        elif t < T_RUN - 0.01:
            part = 'horn' if h == 0 else 'drive'
        elif T_FREE2 - 0.01 <= t < BAR[1885] - 0.01 and h == 0:
            part, k = 'free', 1
        else:
            part = 'race' if h == 0 else 'drive'
        N.append((float(t), float(d), int(m), int(v), part, k, tr))
    for t, d, m in sung(WOODBIRD):
        N.append((t, d, m, 104, 'bird', 0, False))
    for t in accents([n for n in notes if n[0] >= T_FAR - 0.01], vmin=95, n=3, space=0.8):
        N.append((t, 0.4, 76, 100, 'farfire', 0, False))
    return sorted(N, key=lambda e: e[0])


def tracks(G):
    """Where the bird and Siegfried are: hops on Right, darting to him and away, then the race out of the free end."""
    N = [e[:6] for e in compose()]
    rng = np.random.default_rng(272)
    L = G.pd.max()
    home, him = at(G, 'Right', 0.3), at(G, 'Porch Front', 0.5)
    pts, p = [(0.0, home)], home
    for e in N:
        if e[4] == 'bird':
            p = float(np.clip(p + rng.uniform(-45, 45), at(G, 'Right', 0.08), at(G, 'Right', 0.55)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    dl = [e for e in N if e[4] == 'delight']
    for k, t0 in enumerate(T_DELIGHT):        # to him and away
        pts += [(t0, pts[-1][1]), (t0 + 0.9, him + 70), (t0 + 2.2, at(G, 'Right', 0.15 + 0.1 * k))]
    hop = np.linspace(pts[-1][1], L + 80, 9)
    for j, q in enumerate(hop[1:]):
        tj = T_RUN + 0.2 + 1.3 * j
        pts += [(tj, pts[-1][1]), (tj + 0.25, float(q))]
    bird = sorted(pts, key=lambda e: e[0])
    man = [(0.0, him), (T_RUN, him), (T_GONE, L + 120)]
    return (lambda t: keys(t, bird)), (lambda t: keys(t, man)), len(dl)


def render(G, seed=22):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = [e[:6] for e in compose()]
    bird, man, _ = tracks(G)
    bird_on = np.array([e[0] for e in N if e[4] in ('bird', 'delight')])
    free = [e for e in N if e[4] == 'free']
    porch = S['porch']
    pc = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(seed)
    flame = Flicker(rng, G.N, 2.5, 8.0)
    tongue = Flicker(rng, G.N, 0.6, 2.0)
    far = np.exp(-np.clip(L - d, 0, None) / 300)
    tongues = [e for e in N if e[4] in ('farfire', 'farsleep')]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = forest(S, T, DAY_LV)

        # the vision: fire leaping up all over the porch with a silver sleeper at its heart; the second time the
        # fire runs out over the whole house
        for k, t0 in enumerate(T_VISION):
            a = t - t0
            if 0 <= a < 8.5:
                env = smoothstep(0, 0.8, a) * (1 - smoothstep(6.5, 8.5, a))
                reach = porch if k == 0 else porch + (1 - porch) * smoothstep(1.0, 3.5, a) * (1 - smoothstep(5.0, 7.5, a))
                heat = np.clip(0.55 + 0.45 * flame(T) + 0.3 * tongue(T), 0, 1.3)
                fr *= (1 - 0.6 * env * reach)[:, None]
                fr += light(FIRE_R, 0.7 * env * reach * heat)
                fr += light(FIRE_O, 0.75 * env * reach * np.clip(heat - 0.3, 0, None))
                fr += light(FIRE_A, 0.8 * env * reach * np.clip(heat - 0.75, 0, None) * 2)
                sleeper = np.exp(-((d - pc) / (14 + 6 * k)) ** 2)
                fr += light(SILVER, env * (0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * a)) * sleeper)

        # his freedom: emerald surging out of him to both ends on every note; the top note turns the house emerald
        for t0, dur, m, v, part, k in free:
            a = t - t0
            if 0 <= a < 1.8:
                p = man(t0)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.8) * np.exp(-((np.abs(d - p) - 1100 * a) / 240) ** 2))
        for t0 in (T_FREE, T_FREE2):
            a = t - t0
            if 0 <= a < 2.5:
                fr += light(SIEGFRIED, 0.75 * np.exp(-a / 0.7) * smoothstep(0, 0.1, a))

        # Siegfried, standing, then charging out along Right as an emerald comet with a long green wake
        pm = man(t)
        if pm < L + 100:
            run = smoothstep(T_RUN, T_RUN + 1, t)
            for j in range(8):
                q = man(t - 0.06 * (j + 1))
                fr += light(SIEGFRIED, run * 0.7 * (1 - j / 8) * np.exp(-((d - q) / 22) ** 2))
            fr = figure(fr, S, pm, SIEGFRIED, 0.8 + 0.2 * run)
            fr += light(HEAD, 0.7 * np.exp(-((d - pm) / 4) ** 2))
            fr += light(GOLD, 0.8 * np.exp(-((d - pm - 9) / 4) ** 2))
        if T_RUN <= t < T_GONE + 4:              # the wake: the house swept green behind him, then settling
            behind = smoothstep(pm + 30, pm - 200, d) * (d > pc - 200)
            fr += light(SIEGFRIED, 0.5 * behind * (1 - smoothstep(T_GONE, T_GONE + 4, t)))

        # the bird: flashes rippling out on each note
        if bird(t) < L + 70:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.95, T)

        # far off at the free end of Right: the fire on the rock, pulsing and growing
        if t >= T_FAR - 2:
            grow = smoothstep(T_FAR - 2, D - 6, t)
            pulse = 0.75 + 0.25 * np.sin(2 * np.pi * 0.6 * t)
            heat = np.clip(0.6 + 0.4 * flame(T), 0, 1)
            fr += light(FIRE_O, (0.6 + 0.4 * grow) * pulse * far * heat)
            fr += light(FIRE_A, (0.4 + 0.5 * grow) * pulse * far ** 3 * heat)
            fr += light(FIRE_R, (0.3 + 0.4 * grow) * far ** 0.4 * (G.seg_of == 'Right'))
            # the fire licking back along Right toward the porch on every note of Loge's flicker
            for t0, dur, m, v, part, k in tongues:
                a = t - t0
                if 0 <= a < 2.2:
                    fr += light(FIRE_O, (0.7 + 0.2 * grow) * np.exp(-a / 0.6)
                                * np.exp(-((d - (L - 700 * a)) / 90) ** 2))
                    # and a wave of fire-gold rolls from the far end over the whole house, calling him on
                    fr += light(FIRE_A, (0.8 + 0.2 * grow) * np.exp(-a / 1.0)
                                * np.exp(-((d - (L - 1500 * a)) / (140 + 160 * a)) ** 2))
        # the last chord: the far fire blazes up over the whole of Right and the house flashes gold
        if t >= T_LAST:
            a = t - T_LAST
            fr += light(FIRE_A, 0.9 * np.exp(-a / 0.4) * far ** 0.3)
            fr += light(FIRE_O, 0.7 * np.exp(-a / 1.2) * np.clip(far ** 0.15, 0.4, 1))
            fr += light(GOLD, 0.6 * np.exp(-a / 0.35))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, the Woodbird's song on flute, and the stage's sounds."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    bird, man, _ = tracks(G)
    bp = lambda t: pan_at(min(bird(t), G.pd.max()))
    mp = lambda t: pan_at(min(man(t), G.pd.max()))
    pc = pan_at(at(G, 'Porch Front', 0.5))
    far = pan_at(G.pd.max())
    o = Orchestra(M, level=2.3)
    for t, d, m, v, part, k, trem in compose():
        if part == 'bird':                                              # the Woodbird sings
            o.play('flutes', m, t, max(d, 0.15), v, bp(t), 0.95)
            o.play('piccolo', m + 12, t, max(d, 0.15), v - 30, bp(t), 0.2)
        elif part in ('birdbed', 'delight'):
            o.play('flutes' if m < 86 else 'piccolo', m, t, d, v + 4, bp(t), 0.4)
            o.play('violins', m, t, d, v - 10, bp(t), 0.25)
        elif part == 'murmur':
            o.play('violas trem' if trem and m >= 48 else 'cellos trem' if trem else 'violas' if m >= 48 else 'cellos',
                   m, t, d, v - 6, 0.0, 0.4)
        elif part in ('free', 'horn'):
            o.play('horns', m - 12 if m >= 79 else m, t, d, v + 4, mp(t), 0.8)
            o.play('violins', m, t, d, v - 6, mp(t), 0.45)
            if part == 'free' and k == 1:
                o.play('trumpets', m - 12 if m >= 79 else m, t, d, v - 8, mp(t), 0.4)
        elif part == 'race':
            o.play('violins', m, t, d, v - 4, mp(t), 0.55)
            if d >= 0.3:
                o.play('horns', m - 12 if m >= 72 else m, t, d, v, mp(t), 0.6)
                if v >= 108:
                    o.play('trumpets', m - 12 if m >= 79 else m, t, d, v - 10, mp(t), 0.4)
            elif m >= 76 and v >= 100:
                o.play('flutes' if m < 86 else 'piccolo', m, t, d, v - 14, mp(t), 0.25)
        elif part == 'drive':
            o.play('cellos trem' if trem else 'cellos', m, t, d, v, pc, 0.55)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, pc, 0.45)
            if d >= 0.4 and v >= 100:
                o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 10, pc, 0.4)
        elif part == 'farfire':
            o.hit('timpani', t, 110, pitch=-4, gain=0.4, pan=far)
    # the stage: the vision's fire, his running feet and the wind of his going, the final chords
    for k, t0 in enumerate(T_VISION):
        o.fire(t0, t0 + 8.0, level=lambda tt, t0=t0: np.clip((tt - t0) / 0.8, 0, 1) * np.clip((t0 + 8.0 - tt) / 1.5, 0, 1),
               pan=pc, crackle=14, seed=220 + k)
    o.gallop(T_RUN, T_GONE, beat=0.36, pan=mp, v=100, gain=0.8)
    o.wind(T_RUN - 0.3, T_GONE + 2, lambda tt: 0.6 + 0.4 * np.clip((tt - T_RUN) / 3, 0, 1), pan=mp, seed=223)
    o.fire(T_FAR, D, level=lambda tt: 0.3 + 0.7 * np.clip((tt - T_FAR) / (D - T_FAR - 2), 0, 1), pan=far, seed=224)
    o.hit('crash', T_RUN, 110, gain=0.45, pan=pc)
    o.hit('crash', T_LAST, 124, gain=0.7, pan=far)
    o.hit('gong', T_LAST, 110, gain=0.45, pan=far)
    o.hit('timpani roll', T_LAST - 1.2, 110, pitch=-4, gain=0.5, pan=far)
    o.effects([(0, -16), (T_FREE - 0.3, -16), (T_FREE, -8), (T_RUN - 0.5, -8), (T_RUN, -1), (T_GONE + 2, -4)])
