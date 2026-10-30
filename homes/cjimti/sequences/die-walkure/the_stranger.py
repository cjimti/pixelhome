"""The Stranger: the storm is still raging outside the door of Hunding's hut. Thunder rolls in the basses and
grumbles away, flashes crack over the doorway at the free end of Right, and the storm motif sinks lower and
softer at the door. Then the door bursts open: a gust of grey rain floods in across Right and the porch, lightning
cracks over the doorway, and a man stumbles in out of it: Siegmund, a light of Wälsung blue, streaming rain. He
has run all night from his enemies with no weapon left, and he staggers through the room toward the fire on Left,
one lurch to a bar, stopping to sway, twice falling back a step. The cellos sing his motif, the long held D over
a bass that sinks and sinks, and each time a wave of blue rolls out from him over the house. He passes under the
great ash tree in the middle of the porch without seeing it, though its leaves stir and the hilt in the trunk
glints as he goes by. His weariness swells through the orchestra in four great heaves, and each one throws a
wave of blue over the whole house.

At the hearth he sways. "Whoever owns this hearth, here I must rest": he flares once and collapses beside the
fire, a low dim blue lying at the middle of Left, while the hearth glows over him and the storm keeps on faintly
at the open door.

The music is Wagner's own: Act I, bars 91 to 104, the storm's last thunder, and then bars 122 to 145, Siegmund's
entrance to his first words, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the
Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py): the thunder on cellos and basses with the
timpani rolling under it, the storm's falling chords on trombones and horns, Siegmund's motif on the cellos
over the basses, and the four heaves on the full strings with horns. Around the score, as a staging would: rain
and wind beyond the door, thunder after every flash, the door flung open with a blow and a gust, his heavy
stumbling footfalls, the fall by the fire, and the hearth crackling throughout. The storm's thunder and the door
lead; once he is inside they recede so his motif on the cellos is clear, the storm only a murmur at the door.

compose() tags every note of the excerpt, choreography() his every lurch; stage(), room() and figure() are the hut
and the people in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK02'
TITLE = 'The Stranger'
KIND = 'show'
DESCRIPTION = ('A stranger bursts in out of the storm, soaked and unarmed, and staggers across the house toward '
               'the fire. He passes under a great ash tree without noticing it, and collapses at the hearth.')
VOICEOVER = ('The door flies open, and a stranger falls in out of the storm. '
             'Whoever owns this fire, he says, here I must rest.')

EX = excerpt(__file__)                      # Act I, bars 91-104 and 122-145, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
K = 1                                       # this scene's place on Act I's shared clock: T = t + 80 K
THUNDER = [92, 93, 96, 97]                  # the basses roll on a low A
CRACKS = [91, 94, 95]                       # the storm's falling chords: lightning over the doorway
T_DOOR = BAR[122]                           # the door bursts open on his motif's first note
T_IN = T_DOOR + 0.6                         # he is in the doorway
HEAVES = [138, 139, 140, 141]               # his weariness swells through the orchestra
T_ARRIVE = BAR[142]                         # at the hearth
T_FALL = BAR[144] + 0.2                     # "hier muss ich rasten"

HUT = hexc('#3a1a0a')
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
SIEGMUND = hexc('#30a8ff')
WHITE = hexc('#ffffff')

START = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.5)     # where WK01 left the hut
END = dict(bed=0.20, hearth=0.62, trunk=0.95, leaves=0.62, hilt=0.45, door=0.38)
LYING = (0.42, 26.0)                        # Siegmund at the end: level, width


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Before the door opens the left
    hand is the thunder ('thunder') or the storm motif ('storm') and the chords are 'crack' (k = the bar); after it
    the right hand's long notes are Siegmund's motif ('siegmund'), the rest of the right hand 'inner' and the left
    hand 'bass'; in the four heaves everything is 'heave' (k = which heave)."""
    bar_of = lambda t: max(m for m, bt in EX['bars'] if bt <= t + 1e-6)
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        b = bar_of(t)
        if b in HEAVES:
            N.append((t, d, m, v, 'heave', HEAVES.index(b)))
        elif b >= 122:
            N.append((t, d, m, v, 'siegmund' if h == 0 and d >= 0.8 else ('inner' if h == 0 else 'bass'), b))
        elif b in THUNDER:
            N.append((t, d, m, v, 'thunder', b))
        elif b in CRACKS:
            N.append((t, d, m, v, 'crack', b))
        else:
            N.append((t, d, m, v, 'storm', b))
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


def lurches():
    """When he lurches forward: [(time, share of the way)]. Twice he falls back a step."""
    rng = np.random.default_rng(35)
    ts = [BAR[b] + 0.05 for b in range(123, 142)]          # one lurch on each bar of his motif
    share = rng.uniform(0.7, 1.3, len(ts))
    share[[6, 13]] = -0.8
    share[[5, 12]] += 0.8
    return [(float(t), float(s)) for t, s in zip(ts, share / share.sum())]


def choreography(G):
    """Per frame: where Siegmund is, how bright and how wide."""
    F = nframes(D)
    t = np.arange(F) * DT
    door, home = G.pd.max() + 20, at(G, 'Left', 0.5)
    tgt = np.full(F, door)
    p = door
    for tl, s in lurches():
        p -= s * (door - home)
        tgt[t >= tl] = p
    tgt[t >= T_ARRIVE - 1.0] = home
    sway = 9 * np.sin(2 * np.pi * t / 1.7) * smoothstep(T_IN, T_IN + 2, t) * (1 - smoothstep(T_FALL, T_FALL + 1, t))
    pos = follow(tgt, np.full(F, 4.5)) + sway
    lvl = np.array([keys(x, [(T_IN - 0.4, 0.0), (T_IN + 0.4, 0.85), (T_ARRIVE, 0.62), (T_FALL - 0.2, 0.62),
                             (T_FALL + 0.3, 0.95), (T_FALL + 2.0, LYING[0])]) for x in t])
    wid = np.array([keys(x, [(T_FALL, 18.0), (T_FALL + 1.8, LYING[1])]) for x in t])
    return dict(t=t, pos=pos, lvl=lvl, w=wid)


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    sm_on = np.array(sorted({e[0] for e in N if e[4] == 'siegmund'}))
    sm_held = [(e[0], e[0] + e[1]) for e in N if e[4] == 'siegmund' and e[1] >= 2.0]
    thunder = np.array([(e[0], e[3]) for e in N if e[4] == 'thunder'])
    storm_on = np.array([(e[0], e[3]) for e in N if e[4] == 'storm' and e[2] < 50])
    cracks = [BAR[b] for b in CRACKS] + [T_DOOR, T_DOOR + 0.35]
    heaves = [BAR[b] for b in HEAVES]
    steps = [tl for tl, _ in lurches()]
    drip = Flicker(rng, G.N, 3.0, 9.0)
    jag = rng.uniform(0.25, 1.0, G.N)
    right = G.seg_of == 'Right'
    door_c = at(G, 'Right', 0.9)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        p = C['pos'][f]
        lv = {k: keys(t, [(0, START[k]), (T_ARRIVE, START[k]), (D - 0.5, END[k])]) for k in START}
        burst = smoothstep(T_DOOR - 0.1, T_DOOR + 0.3, t) * (1 - smoothstep(T_DOOR + 1.5, T_DOOR + 7, t))
        lv['door'] += 0.35 * burst + 0.25 * (t < T_DOOR)
        # he stirs the leaves and wakes the hilt as he passes under the tree
        near = np.exp(-((p - pf) / 160) ** 2) * (t > T_IN)
        lv['leaves'] += 0.2 * near
        lv['hilt'] += 0.4 * near
        fr = room(S, T, lv)

        # the storm outside: thunder rumbles through the cloud over the whole house, fainter each time
        if len(thunder):
            hit = thunder[(thunder[:, 0] <= t) & (thunder[:, 0] > t - 0.15)]
            if len(hit):
                v = hit[:, 1].max() / 127
                c = keys(t, [(0, d.max() * 0.45), (T_DOOR, door_c)])
                fr += light(STORM, 0.8 * v * np.exp(-((d - c) / 900) ** 2) * (0.55 + 0.45 * rng.uniform(size=G.N)))
        # the storm motif grumbling away at the door: a gust from the door with every note
        j = int(np.searchsorted(storm_on[:, 0], t, side='right')) - 1 if len(storm_on) else -1
        if j >= 0 and t - storm_on[j, 0] < 1.2 and t < T_DOOR:
            a = t - storm_on[j, 0]
            v = storm_on[j, 1] / 127
            front = d.max() - 1100 * a
            fr += light(STORM, v * np.exp(-a / 0.45) * smoothstep(front - 400, front, d))
            fr += light(RAIN, 0.6 * v * np.exp(-a / 0.3) * np.exp(-((d - front) / 50) ** 2))
        # the cloud rolling outside until the door opens: over Side, Right and the door
        out_l = 1 - smoothstep(T_DOOR, T_DOOR + 6, t)
        cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 600 + 0.2 * T))
        outside = np.isin(G.seg_of, ['Side', 'Right'])
        fr += light(STORM, 0.3 * out_l * cloud * outside)

        # the gust through the open door: grey rain flooding in over Right and the porch
        if T_DOOR <= t < T_DOOR + 9:
            a = t - T_DOOR
            front = d.max() - 900 * (1 - np.exp(-a / 1.2))
            flood = smoothstep(front - 250, front + 50, d) * np.exp(-a / 3.0)
            fr += light(STORM, 0.7 * flood * (0.7 + 0.3 * np.clip(drip(T), 0, None)))
            fr += light(RAIN, 0.8 * flood * np.clip(drip(T) - 0.8, 0, None))
        for tb in cracks:
            a = t - tb
            if 0 <= a < 1.0:
                env = np.exp(-a / 0.05) + 0.7 * np.exp(-((a - 0.13) / 0.03) ** 2)
                fr += light(BOLT, min(1.0, env) * (right | (G.seg_of == 'Side')) * jag)
                fr += light(STORM, 0.4 * min(1.0, env))

        # each phrase of his motif: a wave of blue rolls out from him over the house
        i = int(np.searchsorted(sm_on, t, side='right')) - 1
        if i >= 0 and t - sm_on[i] < 3.0:
            a = t - sm_on[i]
            r = 40 + 420 * a
            fr += light(SIEGMUND, 0.6 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p) - r) / 90) ** 2))
        held = sum(smoothstep(t0, t0 + 1.0, t) * (1 - smoothstep(t1, t1 + 1.5, t)) for t0, t1 in sm_held)
        fr += light(SIEGMUND, 0.22 * min(held, 1.0) * np.exp(-((d - p) / 260) ** 2))
        # the four heaves of his weariness: a great wave of blue over the whole house
        for th in heaves:
            a = t - th
            if 0 <= a < 2.2:
                fr += light(SIEGMUND, 0.55 * np.exp(-a / 0.7) * (0.5 + 0.5 * np.exp(-((np.abs(d - p) - 700 * a) / 300) ** 2)))

        # Siegmund, dripping rain at first; a thump of light at each lurch
        lvl = C['lvl'][f]
        j = max([s for s in steps if s <= t], default=-9)
        lurch = 0.25 * np.exp(-(t - j) / 0.25)
        fr = figure(fr, S, p, SIEGMUND, lvl * (1 + lurch), C['w'][f])
        wet = np.exp(-max(t - T_IN, 0) / 14.0) * (t > T_IN)
        fr += light(RAIN, 0.7 * wet * np.exp(-((d - p) / 60) ** 2) * np.clip(drip(T), 0, None) ** 2 / 2)
        if T_FALL - 0.2 <= t < T_FALL + 2.0:
            a = t - T_FALL + 0.2
            fr += light(WHITE, 0.35 * np.exp(-a / 0.35) * np.exp(-((d - p) / 30) ** 2))
            fr += light(SIEGMUND, 0.4 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p) - 200 * a) / 60) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the thunder on cellos and basses with the timpani
    rolling under it, the falling chords on trombones and horns, Siegmund's motif on the cellos over the basses,
    the four heaves on the full strings with horns; a crash where the door bursts open."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_him(t):
        return pan_at(np.interp(t, C['t'], C['pos']))

    o = Orchestra(M, level=3.0)
    door = pan_at(at(G, 'Right', 0.92))
    for t, d, m, v, part, k in compose():
        if part == 'thunder':
            o.play('cellos', m + 12 if m < 36 else m, t, 0.1, v, door * 0.5, 0.6)
            o.play('basses', m + 12 if m < 28 else m, t, 0.1, v - 6, door * 0.5, 0.5)
        elif part == 'storm':
            o.play('cellos', m, t, max(d, 0.1), v, door, 0.8)
            o.play('basses', m - 12 if m >= 40 else m, t, 0.1, v - 6, door, 0.6)
        elif part == 'crack':
            if m >= 55:
                o.play('horns', m - 12, t, d, v, door * 0.6, 0.6)
            else:
                o.play('trombones', m, t, d, v, door * 0.6, 0.6)
                o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 10, 0.0, 0.4)
        elif part == 'siegmund':
            o.play('cellos', m, t, d, v + 10, pan_him(t), 0.9)
            if d >= 2.0:
                o.play('horns', m, t, d, v - 14, pan_him(t), 0.35)
        elif part == 'inner':
            o.play('violas', m, t, d, v, pan_him(t), 0.55)
        elif part == 'bass':
            o.play('basses', m, t, d, v, -0.1, 0.6)
            o.play('cellos', m, t, d, v - 12, -0.1, 0.35)
        elif part == 'heave':
            if m >= 55:
                o.play('violins', m, t, d, v, 0.3, 0.55)
                o.play('violas', m - 12, t, d, v - 10, -0.2, 0.35)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.7)
                o.play('horns', m + 12 if m < 48 else m, t, d, v - 16, 0.0, 0.4)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 10, 0.2, 0.5)
    for b in (92, 96):                      # the timpani roll under the thunder
        o.hit('timpani roll', BAR[b], 100 - 20 * (b == 96), gain=0.6, pan=door * 0.5)
    for i, b in enumerate(CRACKS):          # lightning over the doorway, and its thunder
        o.thunder(BAR[b], 0.55 - 0.1 * i, door, gain=0.9, seed=40 + i)
    for i, b in enumerate(THUNDER[::2]):    # the basses' rolls: thunder grumbling away outside
        o.thunder(BAR[b] + 0.3, 0.2, door * 0.8, gain=0.7, seed=50 + i)
    o.boom(T_DOOR, door, 1.0)               # the door bursts open, the storm floods in, lightning cracks
    o.hit('crash', T_DOOR, 112, gain=0.6, pan=door, fx=True)
    o.thunder(T_DOOR + 0.35, 0.9, door, gain=1.1, seed=60)
    o.wind(T_DOOR - 0.5, T_DOOR + 7.0, lambda tt: np.exp(-np.maximum(tt - T_DOOR, 0) / 2.5), door, seed=61)
    for b in HEAVES:
        o.hit('timpani', BAR[b], 96, pitch=-7, gain=0.5)
    for i, (tl, sh) in enumerate(lurches()):    # his steps: a heavy footfall on each lurch, a stumble back
        pa = pan_him(tl)
        o.hit('hoof', tl, 92 if sh > 0 else 110, pitch=-6, gain=0.55, pan=pa, fx=True)
        o.hit('timpani', tl, 50, pitch=-8, gain=0.3, pan=pa, fx=True)
        if sh < 0:
            o.hit('hoof soft', tl + 0.18, 100, pitch=-5, gain=0.5, pan=pa, fx=True)
    pl = pan_at(at(G, 'Left', 0.5))
    # the storm and the door lead; once he is in, his motif on the cellos is clear and the storm is only at the door
    o.effects([(0.0, 0.0), (T_DOOR + 2.5, 0.0), (T_DOOR + 6.0, -6.0), (BAR[HEAVES[0]], -6.0), (T_FALL - 0.5, -7.0),
               (T_FALL + 0.2, -5.0), (D, -8.0)])
    o.boom(T_FALL + 0.15, pl, 0.55)         # he collapses by the fire
    o.hit('hoof soft', T_FALL + 0.4, 90, pitch=-8, gain=0.5, pan=pl, fx=True)
    o.fire(0.0, D, 0.22, pl, crackle=12, seed=62)   # the hearth crackles all through
    o.wind(0.0, T_DOOR + 1.0, 0.45, door, seed=63)  # the storm outside the door, and after it faintly
    o.wind(T_DOOR + 5.0, D, 0.22, door, seed=64)
    rain(M, o, door)


def rain(M, o, door):
    """Rain beyond the door: hissing, a burst of it when the door flies open, then faint."""
    from pixelhome.audio import SR
    n = int(D * SR)
    tt = np.arange(n) / SR
    lv = np.where(tt < T_DOOR, 0.5, 0.35 + 0.65 * np.exp(-np.maximum(tt - T_DOOR, 0) / 3.0))
    hiss = o._noise(0, 2500, 11000, 65, n=n) * (0.4 + 0.6 * o._wobble(n, 12, 66, 0.6)) * lv
    hiss *= np.clip(tt / 1.0, 0, 1) * np.clip((D - tt) / 1.5, 0, 1)
    M.add('fx', np.vstack([hiss, hiss]), 0.0, 0.3, door)
