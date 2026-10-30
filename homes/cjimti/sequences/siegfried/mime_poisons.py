"""The Poisoned Drink: day in the forest. Siegfried stands at the middle of Porch Front with the Ring's gold glint
on him; Mime waits on Right. The Woodbird darts back in from the free end of Right and sings its warning, every
note a hop and a magenta flash: "Hei! Siegfried gehört nun der Helm und der Ring! O! traute er Mime, dem
treulosen, nicht!" Since he tasted the dragon's blood, Siegfried will hear what Mime means, not what he says.

Mime creeps up over Porch Right all smiles ("Hei! So trink nur, trau meiner Kunst!"), a soft warm yellow glow
pulsing round him on every sweet note. But as the strings climb and the chromatic runs pour down, his true
thoughts break through ("hau' ich dem Kind den Kopf erst ab"): sickly poison green waves burst out of him over
the whole house, harder and faster, until he giggles with glee. "Sauf', und würg dich zu tot!": he holds out
the drink, a pool of poison green bubbling between them on Porch Front. Nothung's motif rings out on the trumpet
and the sword strikes: one white flash over the house, and Mime's yellow bursts into sparks that fly out to both
ends and are gone. Far off at the free end of Right, Alberich's laugh rolls in as a red ripple; then Siegfried's
horn sounds alone ("Neides Zoll zahlt Nothung"), and the bird flits back to its perch on Right.

The music is Wagner's own: Act II, bars 1386 to 1394, 1569 to 1596 and 1632 to 1644, as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the
birdsong on flutes and violins over murmuring violas, Mime's wheedling on oboes and bassoons and his rising
venom on clarinets, strings and xylophone, the sword on the trumpet, Alberich's laugh on bassoons and tuba,
Siegfried on the horn. The Woodbird's warning comes from the printed vocal score (Breitkopf & Härtel, archive.org
31761034115105, p. 223), played as written on flute. The stage adds the bubbling of the poison, the sword's
stroke and Mime falling, and Alberich's laugh echoing off the far end; the effects keep out of the bird's way
and Mime's patter, and come up for the poison and the blow.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF21'
TITLE = 'The Poisoned Drink'
KIND = 'show'
DESCRIPTION = ('Mime comes to Siegfried all sweetness, but now Siegfried can hear what he really means, in green '
               'flashes of poison. Mime holds out a poisoned drink, and the sword strikes him down.')
VOICEOVER = ('Mime smiles, and offers a drink. But Siegfried can hear what he is really thinking. '
             'The drink is poison.')

K = 10                                      # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1386-1394, 1569-1596 and 1632-1644, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
BEAT = 0.5
T_WARN = BAR[1386] + 1.0                    # the bird's warning
T_CREEP = BAR[1393]                         # Mime creeps up
T_SWEET = [BAR[1569], BAR[1573], BAR[1589]] # his sweet talk
T_LAMENT = [BAR[1581], BAR[1591]]
T_THOUGHT = [BAR[b] for b in (1575, 1577, 1579, 1583, 1584, 1585, 1586, 1593, 1595)]   # his true thoughts
T_DRINK = BAR[1632]                         # "Sauf', und würg dich zu tot!"
T_NOTHUNG = BAR[1636]                       # the sword's motif
T_STRIKE = BAR[1637]                        # the blow
T_LAUGH = 69.5                              # Alberich's laugh, far off (as the dataset has it sung)
T_HERO = BAR[1641]                          # Siegfried's horn
T_SONG = BAR[1643]                          # the bird flits back


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
_RUN = [('E5', 1), ('C#5', 1.5), ('B4', 0.5), ('A4', 1), ('F#4', 1), ('A4', 1), ('C#5', 1), ('A4', 1), ('C#5', 1)]
# The Woodbird's warning, from the vocal score (Breitkopf & Härtel, p. 223): (bar, from, to, note) in bars.
WOODBIRD = ([(1386, 1 / 3, 8 / 9, 'F#5')] + _nine(1387, _RUN, ('E5', 8 / 9)) + [(1388, 1 / 3, 8 / 9, 'F#5')] +
            _four(1389, [('E5', 0, _T), ('C#5', _T, 2 * _T), ('B4', 2 * _T, 2), ('A4', 2, 2.5), ('F#4', 2.5, 3),
                         ('A4', 3, 4), ('C#5', 4, 4.5), ('E5', 4.5, 5), ('F#5', 5, 5.5), ('C#5', 5.5, 6),
                         ('E5', 6, 7)]) +
            _four(1390, [('A5', 3, 4), ('A5', 4, 5.5), ('F#5', 5.5, 6), ('E5', 6, 6 + _T), ('E5', 6 + _T, 6 + 2 * _T),
                         ('C#5', 6 + 2 * _T, 8)]) +
            _four(1391, [('E5', 0, _T), ('C#5', _T, 2 * _T), ('B4', 2 * _T, 2), ('A4', 2, 2.5), ('F#4', 2.5, 3),
                         ('A4', 3, 3.5), ('C#5', 3.5, 4), ('E5', 4, 5), ('C#5', 5, 5.5), ('F#5', 5.5, 6),
                         ('E5', 6, 7)]) +
            [(1392, 1 / 6, 1 / 3, 'E5'), (1392, 1 / 3, 4 / 9, 'E5'), (1392, 4 / 9, 5 / 9, 'A5'),
             (1392, 5 / 9, 2 / 3, 'E5'), (1392, 2 / 3, 0.97, 'F#5'),
             (1393, 1 / 6, 5 / 18, 'E5'), (1393, 5 / 18, 7 / 18, 'E5'), (1393, 7 / 18, 1 / 2, 'A5'),
             (1393, 1 / 2, 7 / 12, 'E5'), (1393, 7 / 12, 2 / 3, 'C#5'), (1393, 2 / 3, 0.97, 'F#5')])


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
MIME = hexc('#e0c800')
SWEET = hexc('#ffd860')
POISON = hexc('#60ff20')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')

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
    """Every note, tagged: (time, seconds, midi, velocity, part, k, tremolo). The Woodbird's warning ('call') over the
    orchestra's birdsong ('birdbed') and the forest ('murmur'); Mime's sweet talk ('sweet') and his venom breaking
    through ('thought'); the drink ('drink'); the sword ('nothung'); Alberich's laugh ('laugh'); Siegfried ('hero')."""
    N = []
    for t, d, m, v, h, *tr in tidy(EX['notes']):
        tr, k = bool(tr and tr[0]), None
        if t < BAR[1569] - 0.01:
            part = 'birdbed' if h == 0 and m >= 72 else 'murmur'
        elif t < T_DRINK - 0.01:
            part = 'sweet' if v < 80 and h == 0 else 'thought'
        elif t < T_NOTHUNG - 0.01:
            part = 'drink'
        elif t < T_STRIKE + 1.5 and h == 0:
            part = 'nothung'
        elif t < T_HERO - 0.01:
            part = 'laugh' if t >= T_STRIKE + 1.5 else 'drink'
        else:
            part = 'hero'
        N.append((float(t), float(d), int(m), int(v), part, k, tr))
    for t, d, m in sung(WOODBIRD):
        N.append((t, d, m, 104, 'call', None, False))
    return sorted(N, key=lambda e: e[0])


def bird_track(G):
    """Where the bird is: back in from the free end of Right, a hop on its warning, hops on its song, home."""
    N = [e[:6] for e in compose()]
    rng = np.random.default_rng(271)
    perch, home = at(G, 'Right', 0.2), at(G, 'Right', 0.3)
    pts = [(0.0, G.pd.max() + 60), (0.4, G.pd.max() + 60), (T_WARN - 0.1, perch)]
    p = perch
    for e in N:
        if e[4] in ('call', 'bird'):
            p = float(np.clip(p + rng.uniform(-40, 40), at(G, 'Right', 0.08), at(G, 'Right', 0.5)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    pts += [(T_CREEP + 1.5, p), (T_CREEP + 2.5, G.pd.max() + 60), (T_SONG, G.pd.max() + 60), (T_SONG + 1.5, home)]
    return lambda t: keys(t, pts)


def render(G, seed=21):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = [e[:6] for e in compose()]
    bird = bird_track(G)
    bird_on = np.array([e[0] for e in N if e[4] in ('call', 'bird')])
    sweet = [e for e in N if e[4] in ('sweet', 'lament')]
    hero_on = (T_HERO, T_HERO + 3.5)
    p_s = at(G, 'Porch Front', 0.5)
    p_cup = at(G, 'Porch Front', 0.62)
    m_from, m_to = at(G, 'Right', 0.4), at(G, 'Porch Front', 0.72)
    rng = np.random.default_rng(seed)
    bubble = Flicker(rng, G.N, 2.0, 6.0)
    scatter = [(T_STRIKE, 1.0, m_to)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(DAY_LV)
        dread = smoothstep(T_THOUGHT[0], T_DRINK, t) * (1 - smoothstep(T_STRIKE, T_STRIKE + 3, t))
        lv['day'] *= 1 - 0.7 * dread
        lv['shafts'] *= 1 - 0.8 * dread
        fr = forest(S, T, lv)

        # Mime: creeping up over Porch Right, a sweet warm glow round him on every sweet phrase
        pm = keys(t, [(T_CREEP, m_from), (T_CREEP + 5, m_to)])
        if t < T_STRIKE:
            for t0, dur, m, v, part, k in sweet:
                a = t - t0
                if 0 <= a < dur + 0.6:
                    fr += light(SWEET, 0.5 * np.exp(-a / (dur + 0.3)) * np.exp(-((d - pm) / 110) ** 2))
            # his true thoughts: a poison green wave bursting out of him over the whole house
            for k, t0 in enumerate(T_THOUGHT):
                a = t - t0
                if 0 <= a < 2.0:
                    g = (0.75 + 0.03 * k) * np.exp(-a / 0.8)
                    fr += light(POISON, (0.55 + 0.04 * k) * np.exp(-a / 0.35))
                    fr += light(POISON, g * np.exp(-((np.abs(d - pm) - 900 * a) / (220 + 15 * k)) ** 2))
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.1) * np.exp(-((d - pm) / 30) ** 2))
            fr = figure(fr, S, pm, MIME, 0.7 + 0.1 * dread)

        # the drink: a pool of poison bubbling between them
        if T_DRINK <= t < T_STRIKE + 0.4:
            grow = smoothstep(T_DRINK, T_DRINK + 2, t)
            pool = np.exp(-((d - p_cup) / 40) ** 2)
            fr += light(POISON, (0.55 + 0.35 * np.clip(bubble(T), 0, None)) * grow * pool)
            fr += light(WHITE, 0.6 * grow * np.clip(bubble(T * 1.7) - 0.85, 0, None) * 4 * pool)

        # Siegfried; Nothung flashing on its motif, then the blow
        fr = figure(fr, S, p_s, SIEGFRIED, 0.8)
        fr += light(HEAD, 0.5 * np.exp(-((d - p_s) / 4) ** 2))
        fr += light(GOLD, 0.8 * np.exp(-((d - p_s - 9) / 4) ** 2))
        if T_NOTHUNG <= t < T_STRIKE:
            a = t - T_NOTHUNG
            blade = smoothstep(p_s + 5, p_s + 15, d) * smoothstep(p_s + 15 + 80 * min(1, a / 1.0) + 5,
                                                                  p_s + 15 + 80 * min(1, a / 1.0) - 5, d)
            fr += light(STEEL, 0.95 * blade)
            fr += light(HILT, 0.9 * np.exp(-((d - p_s - 10) / 4) ** 2))
        if T_STRIKE <= t < T_STRIKE + 2:
            a = t - T_STRIKE
            fr += light(WHITE, 0.9 * np.exp(-a / 0.25))
            fr += light(STEEL, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - m_to) - 1100 * a) / 140) ** 2))
            fr += light(MIME, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - m_to) - 700 * a) / 120) ** 2))
        # Mime scattered: his yellow bursts into sparks to both ends of the house
        fr += light(MIME, np.clip(1.4 * sparks(S, scatter, t, 22, n=70, reach=1.3), 0, 1))

        # Alberich's laugh, far off: a red ripple rolling in from the free end of Right
        if T_LAUGH <= t < T_LAUGH + 5:
            a = t - T_LAUGH
            for j in range(3):
                b = a - 0.9 * j
                if b > 0:
                    fr += light(BLOOD, 0.95 * np.exp(-b / 1.5) * np.exp(-((d - (L - 650 * b)) / 160) ** 2))
            fr += light(ALBERICH, 0.8 * np.exp(-a / 0.8) * np.exp(-((d - L) / 50) ** 2))

        # his strength: emerald surges out from him
        for t0 in hero_on:
            a = t - t0
            if 0 <= a < 2.5:
                fr += light(SIEGFRIED, 0.9 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_s) - 800 * a) / 160) ** 2))

        # the bird: flashes rippling out on each note
        if t >= 2.0:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.9, T)
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
    me = pan_at(at(G, 'Porch Front', 0.5))
    mime = pan_at(at(G, 'Porch Front', 0.72))
    far = pan_at(G.pd.max())
    o = Orchestra(M, level=3.4)
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    for t, d, m, v, part, k, trem in compose():
        if part == 'call':                                              # the Woodbird's warning
            o.play('flutes', m, t, max(d, 0.15), v, bp(t), 0.95)
            o.play('piccolo', m + 12, t, max(d, 0.15), v - 30, bp(t), 0.2)
        elif part == 'birdbed':
            o.play('flutes' if m < 86 else 'piccolo', m, t, d, v + 4, bp(t), 0.4)
            o.play('violins', m, t, d, v - 10, bp(t), 0.25)
        elif part == 'murmur':
            o.play('violas trem' if trem and m >= 48 else 'cellos trem' if trem else 'violas' if m >= 48 else 'cellos',
                   m, t, d, v - 6, 0.0, 0.4)
        elif part == 'sweet':
            o.play('oboes' if m >= 58 else 'bassoons', m, t, d, v + 6, mime, 0.6)
        elif part == 'thought':
            if m >= 60:
                o.play('clarinets', m, t, d, v, mime, 0.5)
                o.play('violins', m, t, d, v - 6, mime, 0.4)
                if v >= 95:
                    o.play('flutes' if m < 86 else 'piccolo', m, t, d, v - 16, mime, 0.25)
            else:
                o.play('cellos trem' if trem else 'cellos', m, t, d, v, mime, 0.55)
                o.play('bassoons', m, t, d, v - 10, mime, 0.35)
        elif part == 'drink':
            o.play('violas trem' if trem else 'violas' if m >= 48 else 'cellos', m, t, d, v - 4, mime, 0.5)
        elif part == 'nothung':
            o.play('trumpets', m, t, d, v + 6, me, 0.9)
            o.play('violins', m, t, d, v - 10, me, 0.35)
        elif part == 'laugh':
            o.play('bassoons', m, t, d, v, far, 0.5)
            o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 10, far, 0.35)
        elif part == 'hero':
            o.play('horns', m, t, d, v + 6, me, 0.85)
    # the stage: the poison bubbles, the blow, Mime falls, Alberich's laugh echoes off the far end
    t = T_DRINK + 0.3
    while t < T_STRIKE:
        M.add('fx', bubbles.play(70), t, 0.25, mime)
        t += 1.3
    o.hit('cymbal swell', T_NOTHUNG - 1.5, 90, gain=0.3, pan=me)
    o.clash(T_STRIKE, mime, 124, 1.0)
    o.boom(T_STRIKE + 0.03, mime, 0.8)
    o.hit('crash', T_STRIKE, 118, gain=0.55, pan=mime)
    for j in range(5):                                                  # his sparks fly out
        o.hit('triangle', T_STRIKE + 0.15 + 0.18 * j, 90 - 6 * j, gain=0.25, pan=mime + (j - 2) * 0.2)
    o.hit('bass drum', T_STRIKE + 1.1, 100, gain=0.5, pan=mime)          # he falls
    o.hit('gong', T_LAUGH, 84, gain=0.3, pan=far)
    o.effects([(0, -18), (BAR[1569], -18), (BAR[1569] + 0.1, -10), (T_THOUGHT[3], -6), (T_DRINK, -2),
               (T_STRIKE + 3, -2), (T_HERO, -12)])
