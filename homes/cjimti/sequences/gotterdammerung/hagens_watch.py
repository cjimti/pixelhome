"""Hagen's Watch: the hall of the Gibichungs after the boat has gone. Gutrune goes in, a last ripple of rose, and
Hagen comes out of the shadows of Porch Left to the middle of Porch Front, the hall's door, to keep watch: "Hier
sitz' ich zur Wacht."

The music is Wagner's own, Hagen's watch from Act I as Solti's 1958 Vienna Philharmonic recording takes it: the
night coming on and "Hier sitz' ich zur Wacht" (bars 869-879), "mir aber bringt er den Ring!" (903-906), and the
swell to "dünkt er euch niedrig, ihr dient ihm doch, des Niblungen Sohn" (918-921). The notes come from the Wagner
Ring Dataset's piano reduction (pixelhome/ring.py): the dark hall on clarinets, bassoons, cellos and basses; his
falling tritone on tubas, trombones and basses with timpani and gong; the Ring on clarinets and oboes over horns;
the swell on string tremolo into the full brass. The stage adds the Rhine running past in the dark, harp glints on
the water, and a great blow as the fortissimo lands; the river backs off under his lines.

The hall darkens round him as the night comes on, the torches sinking, the drapes going black, and his tritone
lands on the real strokes, each a blow: the house knocked dark, a violet flash, and a black-violet shock running out
from the door to both ends. "Mir aber bringt er den Ring!": gold streaks race in from both ends of the house into
him and a ring of gold whirls round the whole roofline. Then the tremolo swells and the dark gathers in on him from
both ends until the fortissimo hits, two blows heavier than any before; under "des Niblungen Sohn" the conspiracy
creeps out from him in black and violet, the Rhine glints white at the free end of Right, and he sits on in a
darkened hall, the only bright thing his spear.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by Act
I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD12'
TITLE = "Hagen's Watch"
KIND = 'show'
DESCRIPTION = ('Hagen sits alone at the door of the darkening hall, waiting for the Ring. His blows knock the house '
               'dark, a gold vision of the Ring sweeps round it, and the night gathers in on him.')
VOICEOVER = ('Hagen keeps watch at the door, alone in the dark. '
             'He is waiting for the Ring.')

K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 869-879, 903-906 and 918-921, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SEG = [s['start'] for s in EX['segments']] + [D]
T_GUT = 0.3                                 # Gutrune goes in
T_STEP = (1.0, 4.5)                         # Hagen comes to the door
T_RING = [56.7, 61.9]                       # "mir aber bringt er den Ring!": the Ring, what he waits for
T_SURGE = (72.6, 75.5)                      # the tremolo swelling to the fortissimo
T_GLINT = [10.5, 24.5, 37.0, 46.0, 68.0]
T_DARK = (8.0, 50.0)                        # the night coming on

AMBER = hexc('#ff8a20')
PURPLE = hexc('#6a10c0')
TORCH = hexc('#ffb040')
HEAT = hexc('#fff0a0')
REED = hexc('#2a6a20')
RIVER = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
FOAM = hexc('#14c080')
HAGEN = hexc('#7a00ff')
SPEAR = hexc('#c8d8ff')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
POTION = hexc('#a050ff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
WHITE = hexc('#ffffff')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD11 left the hall
END = dict(hall=0.42, drapes=0.3, torches=0.45, bank=0.3, river=0.55, gloom=0.4)     # the hall dark round him
GUTRUNE_AT = ('Porch Front', 0.5)
HAGEN_FROM = ('Porch Left', 0.35)
HAGEN_AT = ('Porch Front', 0.5)             # the door
FIGS_END = dict(hagen=(*HAGEN_AT, 0.8))


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


RUNS = ['Left', 'Right', 'Side', 'Right', 'Left']
TORCHES = [('Left', 0.2), ('Left', 0.55), ('Left', 0.88), ('Porch Left', 0.2), ('Porch Left', 0.7),
           ('Porch Front', 0.15), ('Porch Front', 0.5), ('Porch Front', 0.85), ('Porch Right', 0.3),
           ('Porch Right', 0.8), ('Side', 0.6)]


def stage(G):
    """The hall of the Gibichungs as profiles over the house: the hall on the porch, its far walls on Left and the
    Side, torches along them, the riverbank on Right with the Rhine running past its free end."""
    d = G.pd
    rng = np.random.default_rng(1848)       # the same torches, drapes and river in every scene, so the cuts match
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    walls = np.isin(seg, ['Left', 'Side'])
    mid = at(G, 'Porch Front', 0.5)
    river = smoothstep(at(G, 'Right', 0.55), at(G, 'Right', 1.0), d)
    tp = np.array([at(G, s, u) for s, u in TORCHES])
    return dict(
        d=d, mid=mid, porch=porch, walls=walls, torch_at=tp,
        hall=porch * (0.6 + 0.4 * np.exp(-((d - mid) / 200) ** 2)) + walls * (0.45 + 0.2 * smooth_noise(rng, d, 50.0)),
        drape=(porch | walls) * (0.5 + 0.5 * np.sin(2 * np.pi * d / 140)) ** 2,
        torch=np.exp(-((d[None, :] - tp[:, None]) / 9) ** 2).sum(0),
        glow=np.exp(-((d[None, :] - tp[:, None]) / 45) ** 2).sum(0),
        bank=(seg == 'Right') * (1 - river) * (0.7 + 0.3 * smooth_noise(rng, d, 30.0)),
        river=river,
        fl=Flicker(rng, G.N, 3.0, 9.0),
        sway=Flicker(rng, G.N, 0.2, 0.7),
    )


def hall(S, T, lv):
    """The hall at shared time T with levels lv (hall, drapes, torches, bank, river, gloom)."""
    d, fl = S['d'], S['fl'](T)
    fr = light(AMBER, lv['hall'] * S['hall'] * (0.85 + 0.15 * fl))
    fr += light(PURPLE, lv['drapes'] * S['drape'] * (0.85 + 0.15 * S['sway'](T)))
    fr += light(TORCH, lv['torches'] * np.clip(S['torch'], 0, 1) * (0.75 + 0.25 * fl))
    fr += light(AMBER, 0.6 * lv['torches'] * np.clip(S['glow'], 0, 1) * (0.8 + 0.2 * fl))
    fr += light(REED, lv['bank'] * S['bank'])
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 90 - 0.55 * T)) * np.sin(2 * np.pi * (d / 230 - 0.2 * T) + 1.0)
    fr += light(RIVER + (TEAL - RIVER) * u[:, None], lv['river'] * S['river'])
    fr += light(FOAM, lv['river'] * S['river'] * np.clip(u - 0.75, 0, None) * 3)
    return fr * (1 - lv['gloom'])


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the hall, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def wave(S, p, a, speed=1200.0, width=90.0, life=0.9):
    """A ring running out both ways from p, a seconds after it starts -> perceptual."""
    return np.exp(-a / life) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2) * (a >= 0)


def blow(fr, S, p, a, s=1.0):
    """Hagen's blow, a seconds after it lands at p: the house knocked dark and a black-violet shock out from him."""
    if not 0 <= a < 2.5:
        return fr
    fr = fr * (1 - 0.9 * s * np.exp(-a / 0.9))
    fr = fr + light(HAGEN, 0.5 * s * np.exp(-a / 0.35))
    fr = fr + light(HAGEN, s * wave(S, p, a, 1100.0, 230.0, 1.2))
    fr = fr + light(SPEAR, 0.9 * s * np.exp(-a / 0.12) * np.exp(-((S['d'] - p + 18) / 8) ** 2))
    return fr


def part_of(t, d, m, v, h):
    """What a note of the excerpt is: its part, see compose()."""
    if t < BAR[870] and h == 0:
        return 'gutrune'
    if h == 1 and v >= 113 and d >= 0.3 and (t < SEG[1] or 57.0 <= t < 59.0 or 75.0 <= t < 77.5):
        return 'hagen'
    if 55.5 <= t < 66.0 and h == 0 and v >= 96:
        return 'ring'
    if t >= BAR[920] and d >= 0.6:
        return 'plot'
    return 'music'


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The held chord as the scene opens
    is Gutrune going in ('gutrune'); the left hand's loud strokes are Hagen's tritone and the fortissimo's blows
    ('hagen', k = which, one per stroke); the rising run and the chords of "mir aber bringt er den Ring!" are the
    Ring ('ring'); the long notes of "des Niblungen Sohn" the conspiracy creeping out of him ('plot'). Everything
    else is 'music'."""
    N = [(float(t), float(d), int(m), int(v), part_of(t, d, m, v, h), int(t >= T_RING[1]))
         for t, d, m, v, h, _ in tidy(EX['notes'])]
    hag = [e for e in N if e[4] == 'hagen']
    keep = [e for i, e in enumerate(hag) if i == 0 or e[0] - hag[i - 1][0] > 0.2]
    N = [e for e in N if e[4] != 'hagen'] + [e[:5] + (k,) for k, e in enumerate(keep)]
    N += [e[:4] + ('music', None) for e in hag if e not in keep]
    return sorted(N, key=lambda e: e[0])


def render(G, seed=12):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    gut = [e for e in N if e[4] == 'gutrune']
    hag = [e for e in N if e[4] == 'hagen']
    ring = [e for e in N if e[4] == 'ring']
    plot = [e for e in N if e[4] == 'plot']
    h0, h1 = at(G, *HAGEN_FROM), at(G, *HAGEN_AT)
    p_gut = at(G, *GUTRUNE_AT)
    rng = np.random.default_rng(seed)
    foam = Flicker(rng, G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        u = smoothstep(*T_DARK, t)
        lv = {k: START[k] + (END[k] - START[k]) * u for k in START}
        fr = hall(S, T, lv)
        p = h0 + (h1 - h0) * smoothstep(*T_STEP, t)

        # Gutrune goes in: one last ripple of rose
        for t0, dur, m, v, part, k in gut:
            a = t - t0
            if 0 <= a < 1.5 and m >= note('C3'):
                fr += light(GUTRUNE, 0.6 * wave(S, p_gut, a, 1100.0, 140.0, 0.8))

        # the Ring: gold streaks race in from both ends into him, and a ring of gold whirls round the house
        for i, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < 1.4:
                r = max(0.0, 1 - a / 0.9) * max(p, L - p)
                fr += light(GOLD, (0.9 + 0.1 * k) * np.exp(-((np.abs(d - p) - r) / 45) ** 2) * (a < 0.9))
                fr += light(HEAT, 0.8 * np.exp(-((a - 0.9) / 0.08) ** 2) * np.exp(-((d - p) / 30) ** 2))
        for k, t0 in enumerate(T_RING):
            a = t - t0
            span = 4.5
            if 0 <= a < span:
                g = smoothstep(0, 1.0, a) * (1 - smoothstep(span - 2.0, span, a))
                c = (p + 900 * a * (1 if k == 0 else -1)) % L
                dist = np.minimum(np.abs(d - c), L - np.abs(d - c))
                fr += light(GOLD, 0.85 * g * np.exp(-(dist / 260) ** 2))
                fr += light(HEAT, 0.5 * g * np.exp(-(dist / 50) ** 2))
                fr += light(GOLD, 0.25 * g)

        # the tremolo swelling: the dark gathers in on him from both ends of the house
        if T_SURGE[0] <= t < T_SURGE[1] + 0.3:
            g = smoothstep(*T_SURGE, t)
            r = (1 - g) * max(p, L - p)
            fr = fr * (1 - 0.5 * g)
            fr += light(HAGEN, (0.4 + 0.6 * g) * smoothstep(r - 200, r + 40, np.abs(d - p)))
            fr += light(SPEAR, 0.8 * g * np.exp(-((d - p + 18) / 8) ** 2))

        # the conspiracy creeping out of him in black and violet
        for t0, dur, m, v, part, k in plot:
            a = t - t0
            if 0 <= a < dur + 2.0:
                reach = min(1.0, a / 2.5) * L
                seep = smoothstep(reach + 120, reach - 120, np.abs(d - p)) * np.exp(-max(a - dur, 0) / 0.8)
                fr = fr * (1 - 0.4 * seep)[:, None]
                fr += light(HAGEN, 0.55 * seep * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 140 - 0.6 * t))))

        # his brooding: a slow violet pulse out of him between the blows, deeper as the night comes on
        if t >= T_STEP[1]:
            a = (t - T_STEP[1]) % 2.4
            g = smoothstep(T_STEP[1], T_STEP[1] + 4, t) * (1 - smoothstep(D - 3.0, D - 0.5, t))
            fr += light(HAGEN, (0.45 + 0.35 * u) * g * wave(S, p, a, 700.0, 180.0, 1.3))
            fr += light(HAGEN, 0.3 * g * np.exp(-a / 0.4) * S['porch'])

        # the Rhine glinting white at the free end of Right
        for t0 in T_GLINT:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.35) * S['river'] * np.clip(foam(T) + 0.2, 0, 1))
                fr += light(FOAM, 0.6 * np.exp(-a / 0.6) * S['river'])

        # Gutrune going in; Hagen at the door, his spear the brightest thing in the hall
        g_in = 1 - smoothstep(T_GUT + 1.0, T_GUT + 5.5, t)
        if g_in > 0:
            fr = figure(fr, S, p_gut, GUTRUNE, 0.8 * g_in)
        lvl = 0.75 + 0.05 * smoothstep(*T_STEP, t)
        fr = fr * (1 - 0.45 * np.exp(-((d - p) / 70) ** 2))[:, None]
        fr = figure(fr, S, p, HAGEN, lvl)
        fr += light(SPEAR, (0.45 + 0.2 * u) * np.exp(-((d - p + 18) / 6) ** 2))
        for i, (t0, dur, m, v, part, k) in enumerate(hag):
            fr = blow(fr, S, p, t - t0, (1.0 if m < note('C3') else 0.6) * (0.85 + 0.15 * (t0 > T_SURGE[0])))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the Rhine running past in the dark."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.6)
    door = pan_at(at(G, *HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.95))

    def role(t, d, m, v, h):
        part = part_of(t, d, m, v, h)
        if part == 'hagen':                                 # his tritone: tubas, trombones, basses
            return [('tuba', 0 if m >= 33 else 12, 4, 0.95), ('trombones', 12, -4, 0.6),
                    ('basses', 0 if m < 40 else -12, 0, 0.6)]
        if part == 'ring':                                  # the Ring: clarinets and oboes, horns beneath
            return [('clarinets', 0, 0, 0.7), ('oboes', 0, -8, 0.45), ('horns', -12, -10, 0.5)]
        if part == 'gutrune':
            return [('oboes', 0, -6, 0.55), ('violas', 0, -10, 0.4)]
        if t < SEG[1]:                                      # the dark hall: low winds and low strings
            if h == 0:
                return [('clarinets' if m >= 50 else 'bassoons', 0, -4, 0.5), ('violas', 0, -12, 0.35)]
            return [('cellos', 0, 0, 0.6), ('basses', -12 if m >= 40 else 0, -6, 0.5)] + (
                [('tuba', 0, -14, 0.4)] if d > 1.5 else [])
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t >= T_SURGE[0] else 0.6, role=role,
            pan=lambda t, m: door * 0.6)
    for t, d, m, v, part, k in compose():
        if part == 'hagen':
            o.hit('timpani', t, min(127, v), pitch=-8 if m < note('C3') else -4, gain=0.85, pan=door)
            if m < note('F2') or t > T_SURGE[0]:
                o.hit('gong', t, 104, gain=0.45, pan=door)
    o.hit('timpani roll', T_SURGE[0], 100, pitch=-6, gain=0.6, pan=door)
    o.hit('cymbal swell', T_SURGE[1] - 3.0, 96, gain=0.4)
    o.hit('crash', T_SURGE[1], 124, gain=0.8)
    o.boom(T_SURGE[1], door, 0.9)                           # the fortissimo lands on him
    for t0 in T_GLINT:                                      # the Rhine glinting at the free end of Right
        o.play('harp', 83, t0, 0.5, 52, river, 0.5)
        o.play('harp', 90, t0 + 0.12, 0.5, 44, river, 0.4)
    o.wind(0.0, D, level=0.3, pan=river, seed=12)           # the river running past in the dark
    # the river leads in the quiet of the night, and backs right off under his lines, the Ring and the fortissimo
    o.effects([(0, -2), (19.5, -2), (20.5, -12), (41, -12), (43, -3), (50, -3), (51.5, -14), (70, -14), (72, -6),
               (75, -6), (75.6, -16), (D, -16)])
