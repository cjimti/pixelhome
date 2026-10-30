"""Hagen's Watch: the hall of the Gibichungs after the boat has gone. Gutrune goes in, a last ripple of rose, and
Hagen comes out of the shadows of Porch Left to the middle of Porch Front, the hall's door, to keep watch: "Hier
sitz' ich zur Wacht."

The hall darkens round him as the night comes on, the torches sinking, the drapes going black, and his falling
tritone (Donington 61a) lands again and again on the tubas and timpani, each a blow: the house knocked dark, a
violet flash, and a black-violet shock running out from the door to both ends, heavier as the night goes on. Twice
the Ring (8) rises in the woodwinds and horns, the thing he waits for: gold streaks race in from both ends of the
house into him and a ring of gold whirls round the whole roofline. Far off, his vassals' call (54) answers on a
muted horn, torch-orange points flaring up and running along the far walls and the Side. Under the last blows the
conspiracy (75) creeps out from him in black and violet, the Rhine glints white at the free end of Right, and he
sits on in a darkened hall, the only bright thing his spear.

compose() holds every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play, melody

CODE = 'GD12'
TITLE = "Hagen's Watch"
KIND = 'show'
DESCRIPTION = ('Hagen sits alone at the door of the darkening hall, waiting for the Ring. His blows knock the house '
               'dark, gold visions of the Ring sweep round it, and his men answer from far off.')
VOICEOVER = ('Hagen keeps watch at the door, alone in the dark. '
             'He is waiting for the Ring.')

K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
T_GUT = 0.8                                 # Gutrune goes in
T_STEP = (4.0, 11.0)                        # Hagen comes to the door
T_HAGEN = [9.5, 17.0, 25.0, 36.5, 48.0, 59.0, 66.0, 71.5]
T_RING = [13.0, 40.0]                       # the Ring, what he waits for
RBEAT = 0.62
T_VASSALS = [30.0, 53.0]                    # his men, far off
T_PLOT = 62.0
T_GLINT = [6.0, 21.5, 34.0, 46.5, 57.0, 69.0, 76.0]
D = 80.0

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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'B0', 60, 'pedal')
    for t, m, v, d in play('gutrune', T_GUT, 0.6, -24, 72):
        add(t, d, m, v, 'gutrune')
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 0.75, -1, 104 + 2 * k):
            add(t, d, m, v, 'hagen', k)
    for k, t0 in enumerate(T_RING):
        for t, m, v, d in play('ring', t0, RBEAT, -1, 92 + 8 * k):
            add(t, d, m, v, 'ring', k)
    for k, t0 in enumerate(T_VASSALS):
        for t, m, v, d in play('vassals', t0, 0.55, 0, 80 + 8 * k):
            add(t, d, m, v, 'vassals', k)
    for t, m, v, d in play('plot', T_PLOT, 0.6, -24, 92):
        add(t, d, m, v, 'plot')
    for t0 in T_GLINT:
        add(t0, 0.5, 'B5', 52, 'glint')
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
    vas = [e for e in N if e[4] == 'vassals']
    plot = [e for e in N if e[4] == 'plot']
    h0, h1 = at(G, *HAGEN_FROM), at(G, *HAGEN_AT)
    p_gut = at(G, *GUTRUNE_AT)
    rng = np.random.default_rng(seed)
    far = np.isin(G.seg_of, ['Left', 'Side'])
    vpts = [rng.uniform(at(G, 'Side', 0.05), at(G, 'Left', 0.95), 14) for _ in vas]
    foam = Flicker(rng, G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        u = smoothstep(8.0, 32.0, t)
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
            span = 12 * RBEAT + 1.5
            if 0 <= a < span:
                g = smoothstep(0, 1.0, a) * (1 - smoothstep(span - 2.0, span, a))
                c = (p + 900 * a * (1 if k == 0 else -1)) % L
                dist = np.minimum(np.abs(d - c), L - np.abs(d - c))
                fr += light(GOLD, 0.85 * g * np.exp(-(dist / 260) ** 2))
                fr += light(HEAT, 0.5 * g * np.exp(-(dist / 50) ** 2))
                fr += light(GOLD, 0.25 * g)

        # his men, far off: torch points flaring up and running along the far walls and the Side
        for k, (t0) in enumerate(T_VASSALS):
            a = t - t0
            if 0 <= a < 5.0:
                g = smoothstep(0, 0.3, a) * (1 - smoothstep(3.5, 5.0, a))
                ps = vpts[k] + 160 * a * np.where(np.arange(14) % 2 == 0, 1, -1)
                pts = np.exp(-((d[None, :] - ps[:, None]) / 9) ** 2).sum(0)
                fr += light(TORCH, 1.0 * g * np.clip(pts, 0, 1) * far * (0.75 + 0.25 * S['fl'](T)))
                fr += light(AMBER, 0.75 * g * far * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 120 - 1.5 * t))))
        for t0, dur, m, v, part, k in vas:
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(TORCH, 0.5 * np.exp(-a / 0.2) * far)

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
            fr = blow(fr, S, p, t - t0, (1.0 if m < note('C3') else 0.6) * (0.85 + 0.03 * k))
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

    for name, gain, rev in (('low', 0.36, 0.28), ('brass', 0.3, 0.32), ('winds', 0.28, 0.35), ('strings', 0.26, 0.35),
                            ('perc', 0.32, 0.3), ('far', 0.22, 0.6)):
        M.bus(name, gain=gain, reverb=rev)
    oboe = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    door = pan_at(at(G, *HAGEN_AT))
    far = pan_at(at(G, 'Left', 0.2))
    river = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 24, t, t + d, v, door, rise=4.0, fall=2.0, gain=0.4)
            hold('low', cb, m + 12, t, t + d, v, door, rise=4.0, fall=2.0, gain=0.45)
        elif part == 'gutrune':
            if m >= note('C3'):
                M.add('winds', oboe.play(m, v, dur=d * 1.1, release=0.3), t, 0.7, door)
        elif part == 'hagen':
            M.add('low', tuba.play(m - 12, v, dur=d * 1.2, release=0.4), t, 1.0, door)
            M.add('low', tbn.play(m, v - 10, dur=d * 1.2, release=0.4), t, 0.7, door)
            M.add('perc', timp.play(v, pitch=-8 if m < note('C3') else -4), t, 0.9, door)
            if m < note('C3') and k in (3, 5, 7):
                M.add('perc', gong.play(100), t, 0.55, door)
        elif part == 'ring':
            if d > 1.0:
                hold('winds', clar, m, t, t + d, v, door, rise=0.2, fall=1.0, gain=0.7)
            else:
                M.add('winds', clar.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, door)
            M.add('brass', horn.play(m - 12, v - 12, dur=d * 1.05, release=0.3), t, 0.55, door)
        elif part == 'vassals':
            M.add('far', mute.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, far)
            M.add('far', bsn.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.5, far)
        elif part == 'plot':
            hold('low', tuba, m + 12, t, t + d, v, door, rise=0.5, fall=1.0, gain=0.6)
            hold('strings', ctrem, m + 12, t, t + d, v - 10, door, rise=0.5, fall=1.0, gain=0.45)
        elif part == 'glint':
            M.add('strings', harp.play(m, v), t, 0.5, river)
            M.add('strings', harp.play(m + 7, v - 8), t + 0.12, 0.4, river)
