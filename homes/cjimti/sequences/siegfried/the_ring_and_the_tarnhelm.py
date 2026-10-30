"""The Ring and the Tarnhelm: broad day in the forest, the dragon dead. The Woodbird, a hot magenta point on Right,
sings on, every note a hop and a flash: "Wollt' er den Tarnhelm gewinnen... doch wollt' er den Ring sich erraten,
der macht' ihn zum Walter der Welt!" Siegfried, emerald on Porch Front, walks into the dark middle of the cave
and is swallowed; the cave mouth flares with the gold of the hoard, and the bird flies off out of the free end
of Right on its last trill.

While he is inside, Alberich (red in his muddy halo) and Mime (sulphur yellow) come running in from the free end
of Right and fight over the spoils: the whole of Right splits into a red half and a yellow half whose border
lurches with every blow of their quarrel, toward Mime when Alberich is snarling and back when Mime whines, white
sparks flying where they clash, up to the frenzy of "Weder Ring noch Tarnhelm soll dir denn taugen!"

"Aus der Höhle kommt er daher": Siegfried comes out with the Ring; on every note of its motif a gold wave sweeps
the house, Alberich and Mime shrinking back. "Den Tarnhelm hält er": the whole house shimmers and thins into a
grey-green mist, Siegfried flickering in and out of sight. Alberich slinks off out of the free end of Right with a
red ripple of his curse, Mime is left plotting on Right ("Ich will ihn mir schon gewinnen"), and Siegfried's
strength surges out of him in emerald.

The music is Wagner's own: Act II, bars 1202 to 1207, 1240 to 1255 and 1318 to 1349, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
birdsong on flutes and violins, the dwarfs' quarrel with Alberich's snarls on bassoons, trombones and cellos and
Mime's whining on oboes and clarinets, the Ring and the Tarnhelm on horns over murmuring strings. The end of the
Woodbird's song comes from the printed vocal score (Breitkopf & Härtel, archive.org 31761034115105, pp. 210-211),
played as written on flute. The stage adds every blow of the dwarfs' scuffle, the glitter of the hoard, the
Tarnhelm's shimmer and Alberich's sneer; the effects keep out of the bird's way and the Ring's, and lead the
fight.

compose() holds every note; stage(), forest(), figure() and sparks() are Act II's forest and cave, shared word
for word with SF11 on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF20'
TITLE = 'The Ring and the Tarnhelm'
KIND = 'show'
DESCRIPTION = ('The bird tells Siegfried to take the Ring and the magic helmet from the hoard. While he is in the '
               'cave, two dwarfs fight over the treasure, and he comes out with the Ring shining gold.')
VOICEOVER = ('The little bird sings: take the Ring, and the magic helmet. '
             'But two greedy dwarfs are already fighting over the gold.')

K = 9                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1202-1207, 1240-1255 and 1318-1349, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
BEAT = 0.5
T_IN = BAR[1206]                            # "...Walter der Welt!": Siegfried walks into the cave
T_HOARD = BAR[1207]                         # the hoard flaring
T_FLY = BAR[1207] + 0.8                     # the bird flies off on its trill
T_RUSH = BAR[1240]                          # Alberich and Mime run in
T_FIGHT = BAR[1241]                         # the quarrel, blow by blow
T_OUT = BAR[1341]                           # "Aus der Höhle kommt er daher": the Ring
T_HELM = [BAR[1344], BAR[1346]]             # "Den Tarnhelm hält er"
T_SLINK = BAR[1348]                         # Alberich slinks off
T_HERO = BAR[1349] + 0.4


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


_T = 2 / 3
# The end of the Woodbird's first song, from the vocal score (Breitkopf & Härtel, pp. 210-211).
WOODBIRD = (_four(1202, [('E5', 4, 4 + _T), ('C#5', 4 + _T, 4 + 2 * _T), ('E5', 4 + 2 * _T, 6), ('A5', 6, 6 + _T),
                         ('G#5', 6 + _T, 7.5), ('E5', 7.5, 8)]) +
            _nine(1203, [(n, 1) for n in ('E5', 'C#5', 'B4', 'A4', 'F#4', 'A4', 'C#5', 'A4', 'C#5')], ('E5', 1.0)) +
            _four(1204, [('E5', 3, 4), ('E5', 4, 6 + _T), ('C#5', 6 + _T, 6 + 2 * _T), ('E5', 6 + 2 * _T, 8)]) +
            _four(1205, [(n, j * _T, (j + 1) * _T) for j, n in enumerate(
                ('A5', 'G#5', 'E5', 'E5', 'C#5', 'B4', 'E5', 'A4', 'C#5', 'E5', 'C#5', 'E5'))]) +
            [(1206, 0, 2 / 3, 'A5')])


def sung(lines):
    """A sung line [(bar, from, to, note)] -> [(time, seconds, midi)] on the excerpt's clock."""
    out = []
    for b, f0, f1, name in lines:
        seg = next(s['measures'] for s in EX['segments'] if s['measures'][0] <= b < s['measures'][1])
        ms, ts = zip(*sorted((m, t) for m, t in EX['bars'] if seg[0] <= m <= seg[1]))
        t0, t1 = float(np.interp(b + f0, ms, ts)), float(np.interp(b + f1, ms, ts))
        out.append((t0, t1 - t0, note(name)))
    return out


def singer(t):
    """Who of the two dwarfs is singing at t (0 Alberich, 1 Mime, None)."""
    for t0, t1, who, _ in EX['singing']:
        if t0 - 0.2 <= t < t1 + 0.4:
            return 0 if who == 'Alberich' else 1 if who == 'Mime' else None
    return None

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
MIME = hexc('#e0c800')
MIST = hexc('#50c0a8')
SPARK = hexc('#ffb020')

DAY_LV = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)
MIME_AT, ALB_AT = 0.4, 0.25                 # their places on Right at the end and in the quarrel


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
    """Every note, tagged: (time, seconds, midi, velocity, part, k, tremolo). The Woodbird's line ('bird') over the
    orchestra's birdsong ('birdbed'); the hoard's glitter ('hoard'); in the quarrel the low line is Alberich's
    ('alb'), the high Mime's ('mime'), and its accents are the blows ('blow', k 0 Alberich's, 1 Mime's); then the
    Ring ('ring'), the Tarnhelm ('helm'), Alberich's parting sneer ('laugh') and Siegfried ('hero')."""
    N = []
    notes = tidy(EX['notes'])
    for t, d, m, v, h, *tr in notes:
        tr, k = bool(tr and tr[0]), None
        if t < T_IN - 0.01:
            part = 'birdbed'
        elif t < T_RUSH - 0.01:
            part = 'hoard' if h == 0 else 'birdbed'
        elif t < T_OUT - 0.01:
            part = 'alb' if (h == 1 or m < 58) else 'mime'
        elif t < T_HELM[0] - 0.01:
            part = 'ring' if h == 0 else 'murmur'
        elif t < T_SLINK - 0.01:
            part, k = ('helm' if h == 0 else 'murmur'), int(t >= T_HELM[1] - 0.01)
        elif t < T_HERO - 0.01:
            part = 'laugh' if h == 0 else 'murmur'
        else:
            part = 'hero' if h == 0 else 'murmur'
        N.append((float(t), float(d), int(m), int(v), part, k, tr))
    for t, d, m in sung(WOODBIRD):
        N.append((t, d, m, 104, 'bird', 0, False))
    last = None
    for j, t in enumerate(accents([n for n in notes if T_FIGHT - 0.01 <= n[0] < T_OUT - 0.5], vmin=72, n=2, space=0.55)):
        who = singer(t)
        last = (1 - last if last is not None else 0) if who is None else who
        N.append((t, 0.4, 24, 100, 'blow', last, False))
    return sorted(N, key=lambda e: e[0])


def bird_track(G):
    """Where the bird is: hops among the trees on Right on its song, then off out of the free end."""
    N = [e[:6] for e in compose()]
    rng = np.random.default_rng(27)
    home = at(G, 'Right', 0.3)
    pts, p = [(0.0, home)], home
    for e in N:
        if e[4] == 'bird':
            p = float(np.clip(p + rng.uniform(-45, 45), at(G, 'Right', 0.08), at(G, 'Right', 0.55)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    pts += [(T_FLY, p), (T_FLY + 1.6, G.pd.max() + 60)]
    return lambda t: keys(t, pts)


def fighters(G, t, blows):
    """Where the border between Alberich's red and Mime's yellow is on Right, shoved by each blow."""
    lo, hi = at(G, 'Right', 0.12), at(G, 'Right', 0.7)
    shove = sum((1 if k == 0 else -1) * smoothstep(t0, t0 + 0.2, t) for t0, _, _, _, _, k in blows)
    return lo + (hi - lo) * (0.5 + 0.12 * shove)


def render(G, seed=20):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = [e[:6] for e in compose()]
    bird = bird_track(G)
    bird_on = np.array([e[0] for e in N if e[4] == 'bird'])
    blows = [e for e in N if e[4] == 'blow']
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    helm = [e for e in N if e[4] == 'helm']
    right = G.seg_of == 'Right'
    lo, hi = at(G, 'Right', 0.12), at(G, 'Right', 0.7)
    rng = np.random.default_rng(seed)
    gold_at = rng.uniform(at(G, 'Porch Left', 0.3), at(G, 'Porch Right', 0.7), 24)
    mist = Flicker(rng, G.N, 3.0, 9.0)
    p_start, p_end = at(G, 'Porch Front', 0.3), at(G, 'Porch Front', 0.5)
    p_mime, p_alb = at(G, 'Right', MIME_AT), at(G, 'Right', ALB_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(DAY_LV)
        hoard = smoothstep(T_IN + 1, T_HOARD + 1, t) * (1 - smoothstep(T_OUT + 1, T_OUT + 5, t))
        lv['cave'] += 0.45 * hoard
        helmed = sum(smoothstep(t0, t0 + 0.6, t) * (1 - smoothstep(t0 + 3.6, t0 + 4.6, t)) for t0 in T_HELM)
        lv['day'] *= 1 - 0.55 * helmed
        lv['shafts'] *= 1 - 0.7 * helmed
        fr = forest(S, T, lv)

        # the hoard in the cave: gold heaped on the porch, glinting on each note of the Ring
        if hoard > 0:
            fr += light(GOLD, 0.7 * hoard * S['mouth'] ** 1.5)
            for j, g in enumerate(gold_at):
                tw = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.13 * j) * t + j)
                fr += light(HOT, 0.6 * hoard * tw ** 6 * np.exp(-((d - g) / 6) ** 2))

        # the bird's song: each note a hop and a magenta flash rippling out over Right
        if t < T_FLY + 2:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.95, T)

        # Siegfried: into the cave and swallowed by the dark, out again with the Ring
        p = keys(t, [(T_IN, p_start), (T_IN + 2.5, p_end)])
        lvl = keys(t, [(T_IN + 1.5, 0.8), (T_IN + 3.5, 0.0), (T_OUT - 0.5, 0.0), (T_OUT + 0.4, 1.0), (T_OUT + 6, 0.8)])
        if helmed > 0:
            lvl *= 1 - helmed * (0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * t)) ** 2
        if lvl > 0.01:
            fr = figure(fr, S, p, SIEGFRIED, lvl)
            fr += light(HEAD, 0.6 * lvl * np.exp(-((d - p) / 4) ** 2))
        if t >= T_OUT:
            fr += light(GOLD, min(1.0, 1.2 * lvl) * np.exp(-((d - p - 9) / 4) ** 2))

        # the Ring in full: a gold wave from the cave out to both ends, one surge per note
        if T_OUT <= t < T_HELM[0]:
            a = t - T_OUT
            front = min(1.0, a / 2.0) * max(mid, L - mid)
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.35) if j >= 0 else 0.0
            fade = 1 - smoothstep(T_HELM[0] - 2, T_HELM[0], t)
            fr += light(GOLD, fade * (1.0 * np.exp(-((np.abs(d - mid) - front) / 160) ** 2)
                                      + (0.4 + 0.35 * pulse) * (np.abs(d - mid) < front)))
            if a < 0.5:
                fr += light(WHITE, 0.5 * np.exp(-a / 0.12))

        # the Tarnhelm: the house shimmers and thins into a grey-green mist on each note
        for t0, dur, m, v, part, k in helm:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(MIST, 0.8 * helmed * np.exp(-a / 0.5) * np.clip(mist(T + 7 * k), 0, None) ** 2)
        if helmed > 0:
            fr += light(MIST, 0.45 * helmed)
        if helmed > 0:
            fr *= (1 - 0.5 * helmed * (np.clip(mist(T), -1, 1) * 0.5 + 0.5))[:, None]

        # Alberich and Mime: rush in, then the whole of Right split red against yellow, the border lurching
        if t >= T_RUSH:
            share = smoothstep(T_RUSH, T_FIGHT, t)
            if t < T_OUT + 2:
                border = fighters(G, t, blows)
                split = right * (d > lo - 60) * (1 - smoothstep(T_OUT, T_OUT + 2, t)) * share
                fr += light(ALBERICH, 0.85 * split * smoothstep(border + 15, border - 15, d))
                fr += light(MIME, 0.85 * split * smoothstep(border - 15, border + 15, d))
                for t0, _, _, v, _, k in blows:
                    a = t - t0
                    if 0 <= a < 0.6:
                        fr += light(WHITE, 0.9 * np.exp(-a / 0.08) * np.exp(-((d - border) / 14) ** 2))
                        fr += light(ALBERICH if k == 0 else MIME, 0.6 * np.exp(-a / 0.2) * right)
                fr += light(SPARK, np.clip(sparks(S, [(e[0], 0.8, fighters(G, e[0] + 0.2, blows)) for e in blows], t, 21,
                                                  n=10, reach=0.35), 0, 1) * right)
            # after the quarrel: Alberich at his place, then slinking off; Mime to his
            a_pos = keys(t, [(T_RUSH, L + 30), (T_FIGHT, p_alb), (T_SLINK, p_alb), (T_SLINK + 5, L + 40)])
            m_pos = keys(t, [(T_RUSH + 1, L + 30), (T_FIGHT + 1, at(G, 'Right', 0.6)), (T_OUT, at(G, 'Right', 0.6)),
                             (T_OUT + 3, p_mime)])
            cower = 1 - 0.35 * smoothstep(T_OUT, T_OUT + 1.5, t) * (1 - smoothstep(T_HELM[1] + 4, T_HERO, t))
            alb_lvl = 0.8 * cower * (1 - smoothstep(T_SLINK + 3.5, T_SLINK + 5, t))
            if alb_lvl > 0.01:
                fr += light(MUD, 0.5 * alb_lvl * np.exp(-((d - a_pos) / 60) ** 2))
                fr = figure(fr, S, a_pos, ALBERICH, alb_lvl)
            fr = figure(fr, S, m_pos, MIME, keys(t, [(T_RUSH + 1, 0.0), (T_RUSH + 2, 0.8), (T_HERO, 0.8),
                                                    (D, 0.7)]) * cower)
        if T_SLINK <= t < T_SLINK + 4:
            a = t - T_SLINK
            fr += light(BLOOD, 0.8 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - p_alb) - 800 * a) / 110) ** 2))

        # his strength: emerald surges out from him on each phrase
        if t >= T_HERO:
            for t0 in (T_HERO, T_HERO + 2.4):
                a = t - t0
                if 0 <= a < 2.5:
                    fr += light(SIEGFRIED, 0.95 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_end) - 800 * a) / 170) ** 2))
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

    bird = bird_track(G)
    bp = lambda t: pan_at(min(bird(t), G.pd.max()))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    alb, mime = pan_at(at(G, 'Right', ALB_AT)), pan_at(at(G, 'Right', MIME_AT))
    o = Orchestra(M, level=2.6)
    for t, d, m, v, part, k, trem in compose():
        if part == 'bird':                                              # the Woodbird sings
            o.play('flutes', m, t, max(d, 0.15), v, bp(t), 0.95)
            o.play('piccolo', m + 12, t, max(d, 0.15), v - 30, bp(t), 0.2)
        elif part in ('birdbed', 'hoard'):
            if m >= 72:
                o.play('flutes' if m < 86 else 'piccolo', m, t, d, v, bp(t) if part == 'birdbed' else cave, 0.45)
                o.play('violins', m, t, d, v - 14, bp(t), 0.25)
            else:
                o.play('violas trem' if trem else 'violas', m, t, d, v - 8, 0.0, 0.35)
        elif part == 'alb':
            o.play('bassoons' if m >= 46 else 'cellos', m, t, d, v, alb, 0.6)
            if v >= 85 and d >= 0.2:
                o.play('trombones', m, t, d, v - 8, alb, 0.45)
        elif part == 'mime':
            o.play('oboes' if m < 80 else 'flutes', m, t, d, v, mime, 0.55)
            o.play('clarinets', m - 12, t, d, v - 12, mime, 0.3)
        elif part in ('ring', 'helm', 'laugh', 'hero'):
            o.play('horns', m, t, d, v + 4, cave, 0.8)
            if part == 'laugh':
                o.play('bassoons', m, t, d, v - 6, alb, 0.4)
        elif part == 'murmur':
            o.play('cellos trem' if trem and m < 60 else 'violas trem' if trem else 'cellos', m, t, d, v - 6, 0.0, 0.45)
        elif part == 'blow':                                            # the dwarfs' scuffle
            where = alb if k == 0 else mime
            o.hit('brake drum', t, 100, gain=0.35, pan=where)
            o.hit('timpani', t, 96, pitch=-1, gain=0.3, pan=where)
            o.hit('metal', t + 0.02, 80, gain=0.18, pan=where)
    o.hit('cymbal swell', T_HOARD - 1.8, 80, gain=0.25, pan=cave)        # the hoard glitters
    for j in range(6):
        o.hit('triangle', T_HOARD + 0.6 * j, 70 + 4 * j, gain=0.2, pan=cave)
    o.hit('crash', T_OUT, 104, gain=0.4, pan=cave)
    for t0 in T_HELM:                                                   # the Tarnhelm's shimmer
        o.hit('scrape', t0, 90, gain=0.35, pan=cave)
        o.hit('gong scrape', t0 + 0.4, 80, gain=0.3, pan=cave)
    o.hit('gong', T_SLINK, 80, gain=0.3, pan=alb)
    o.effects([(0, -18), (T_IN, -18), (T_HOARD, -8), (T_RUSH, -2), (T_OUT - 0.5, -2), (T_OUT, -9)])
