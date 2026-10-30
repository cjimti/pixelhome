"""The Wanderer: Mime alone in his cave, sulphur yellow at the anvil, hammering in a fury at a sword he knows he
cannot make whole ("Des Niblungen Neid, Not und Schweiss"), every blow throwing sparks. The orchestra sinks, and
the cave mouth at the free end of Right floods deep blue: a stranger stands in it. "Heil dir, weiser Schmied!":
the Wanderer's great slow chords sound on the trombones and tubas, and with every chord a wave of deep blue rolls
in from the mouth over the whole house to the end of Side, while he comes in step by step, a tall figure of
Wotan's blue, to the middle of Right.

Mime tries to drive him out, shaking and flaring yellow, but the Wanderer sits down by the hearth and wagers his
head: his spear's motif strides down the bass and a pale steel shaft grows from him toward the anvil note by
note, then strikes the floor, a blue-white flash over the whole house and a shock running out both ways that
knocks the forge down to embers. Mime cowers, trembling, while the Wanderer's chords sound on, and a blue tint
stays in the walls of the cave.

The music is Wagner's own: Act I, bars 1282 to 1299 (Mime's fury and the Wanderer's arrival) and 1366 to 1379
(Mime's dismissal, the spear's descent and the wager), as Solti's 1958 Vienna Philharmonic recording takes them.
The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py), orchestrated by hand and
register: the Wanderer's chords on trombones, tubas and horns, the spear's descent on trombones, tuba and basses,
Mime's agitation on violins and woodwinds. On stage: Mime's hammer ringing on the anvil, a drum roll as the
stranger appears, a steady tread under the Wanderer's steps, and the spear striking the floor with a great blow and
a roll of thunder; the effects stand back under the chords.

compose() holds every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF06'
TITLE = 'The Wanderer'
KIND = 'show'
DESCRIPTION = ('A stranger in a deep blue cloak walks into the dwarf\'s cave with a spear in his hand, and every step '
               'he takes washes the house in blue. He strikes the spear down and the forge cowers.')
VOICEOVER = ('A stranger in a blue cloak walks into the cave, leaning on a spear. '
             'He calls himself the Wanderer.')

K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1282-1299 and 1366-1379, Solti 1958
D = EX['seconds']
_M = np.array([m for m, _ in EX['bars']], float)
_T = np.array([t for _, t in EX['bars']])


def bt(m):
    """Seconds into the scene of measure position m (bar plus fraction)."""
    return float(np.interp(m, _M, _T))


T_ROLL = bt(1289)                           # the orchestra sinks; the mouth floods blue
T_IN = bt(1290)                             # he starts in from the mouth
T_STAND = bt(1298)                          # he has reached the middle of Right
T_SHOO = bt(1366)                           # Mime tries to drive him out
T_SPEAR = bt(1371.6)                        # the spear motif strides down the bass
T_STRIKE = bt(1374)                         # it strikes the floor
T_WAND = [T_IN, T_STRIKE]                   # the two runs of his chords

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
WAND_AT = 0.4                               # where the Wanderer stands, on Right

def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes, tagged: Mime's fury ('fury'),
    the Wanderer's chords ('wanderer', k = which run), Mime's agitation ('shoo'), the spear's descent ('spear') and
    the rest ('orch'); 'tap' and 'strike' mark the lights' moments."""
    N = []
    for n in tidy(EX['notes']):
        t, d, m, v, hand, trem = n
        if t < T_ROLL:
            part, k = 'fury', hand
        elif T_SHOO <= t < T_SPEAR - 0.05:
            part, k = 'shoo', hand
        elif T_SPEAR - 0.05 <= t < T_STRIKE - 0.05 and hand == 1:
            part, k = 'spear', None
        elif d >= 0.8:
            part, k = 'wanderer', 0 if t < T_SHOO else 1
        else:
            part, k = 'orch', hand
        N.append((t, d, m, v, part, 'trem' if trem and part == 'orch' else k))
    last = -9.0
    for t, d, m, v, part, k in sorted(N):
        if part == 'fury' and v >= 110 and t - last > 0.6:
            N.append((t, 0.2, m, v, 'tap', None))
            last = t
    N.append((T_STRIKE, 0.1, 35, 127, 'strike', None))
    return sorted(N, key=lambda e: e[0])


def chords():
    """When each of the Wanderer's chords lands (at least three long notes together): [(time, which run)]."""
    on = {}
    for e in compose():
        if e[4] == 'wanderer':
            on.setdefault((round(e[0], 2), e[5]), []).append(e)
    out, last = [], -9.0
    for (t, k), es in sorted(on.items()):
        if len(es) >= 2 and t - last > 2.2:
            out.append((t, k))
            last = t
    return out


def where_wanderer(G, t):
    """His path distance: in from beyond the mouth, a step on each chord of the first statement."""
    far, stand = G.pd.max() + 50, at(G, 'Right', WAND_AT)
    steps = [c for c, k in chords() if k == 0]
    pts = [(T_IN - 0.5, far)] + [(c + 0.9, far + (stand - far) * (j + 1) / len(steps)) for j, c in enumerate(steps)]
    return keys(t, pts)


def render(G, seed=6):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    ch = chords()
    spear_on = [e for e in N if e[4] == 'spear']
    t_strike = T_STRIKE
    cringe = [e for e in N if e[4] == 'shoo' and e[3] >= 110 and e[5] == 0][::2]
    taps = [(e[0], 0.7, anvil) for e in N if e[4] == 'tap']
    p_mime = at(G, 'Porch Front', MIME_AT)
    tap_t = np.array([h[0] for h in taps])
    stand = at(G, 'Right', WAND_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        cow = smoothstep(t_strike, t_strike + 0.2, t) * (1 - smoothstep(t_strike + 3, t_strike + 14, t))
        lv['forge'] -= 0.3 * cow
        lv['walls'] -= 0.25 * cow
        fr = cave(S, T, lv)
        p = where_wanderer(G, t)
        present = smoothstep(T_ROLL, T_IN, t)

        # the mouth floods deep blue at the drum roll; a blue tint settles into the walls while he is there
        gone = 0.0
        fr += light(WOTAN, 0.85 * present * S['mouth'] * (1 - 0.4 * smoothstep(T_STAND, T_STAND + 6, t)) * (1 - gone))
        tint = smoothstep(T_STAND - 4, T_STAND + 4, t) * (1 - gone)
        fr += light(WOTAN, 0.35 * tint * (S['walls'] + 0.6 * (S['forge'] == 0) * (1 - S['mouth'])))

        # every chord: a wave of blue rolling in from the mouth over the whole house to the end of Side
        for c, k in ch:
            a = t - c
            if 0 <= a < 4.0:
                g = (1.0, 0.8)[k]
                front = L - 750 * a
                wave = np.exp(-((d - front) / 260) ** 2) + 0.55 * (d > front) * np.exp(-a / 1.1)
                fr += light(WOTAN, g * np.exp(-a / 2.0) * wave)
                fr += light(WOTAN_SOFT, 0.6 * g * np.exp(-a / 0.25) * np.exp(-((d - p) / 60) ** 2))

        # the spear: a pale shaft growing from him toward the anvil, a step on every note, then the strike
        if T_SPEAR <= t < t_strike + 3:
            n = sum(1 for e in spear_on if e[0] <= t)
            tip = stand - min(n, 12) * (stand - anvil) / 12
            shaft = (d <= stand) * (d >= tip) * (1 - smoothstep(t_strike + 0.5, t_strike + 3, t))
            j = n - 1
            hit = np.exp(-(t - spear_on[j][0]) / 0.18) if j >= 0 else 0.0
            fr += light(SPEAR, (0.6 + 0.4 * hit) * shaft)
            fr += light(WHITE, 0.8 * hit * np.exp(-((d - tip) / 10) ** 2) * (t < t_strike))
        if t_strike <= t < t_strike + 2.5:
            a = t - t_strike
            fr += light(SPEAR, min(1.0, 1.1 * np.exp(-a / 0.15)))
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - stand) - 1600 * a) / 120) ** 2))
        fr += light(SPARK, np.clip(sparks(S, taps, t, 60, n=12, reach=0.8), 0, 1.0))
        k = int(np.searchsorted(tap_t, t, side='right')) - 1
        if k >= 0 and t - tap_t[k] < 0.8:                       # each of Mime's blows: a flash on the anvil
            fr += light(HEAT, 0.9 * np.exp(-(t - tap_t[k]) / 0.1) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.6 * np.exp(-(t - tap_t[k]) / 0.4) *
                        np.exp(-((np.abs(d - anvil) - 1200 * (t - tap_t[k])) / 80) ** 2))

        # Mime: tapping at first, then cowering and trembling when the spear comes down
        tremble = smoothstep(t_strike, t_strike + 0.5, t) * (0.12 + 0.08 * np.sin(2 * np.pi * 7 * t))
        for t0, dur, m, v, part, k in cringe:
            a = t - t0
            if 0 <= a < 1.2:                                    # Mime in a flap: yellow bursts out from him
                fr += light(MIME, 0.9 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - 700 * a) / 90) ** 2))
                fr += light(FORGE, 0.4 * np.exp(-a / 0.3) * S['forge'])
        mlvl = keys(t, [(0, 0.6), (T_ROLL, 0.6), (T_ROLL + 1, 0.45), (T_SHOO, 0.45), (T_SHOO + 0.5, 0.65),
                        (t_strike, 0.65), (t_strike + 0.4, 0.3), (D, 0.35)])
        fr = figure(fr, S, p_mime + 8 * cow, MIME, mlvl + tremble * (t < D - 4))

        # the Wanderer: deep blue, tall (wide) and steady, a pale glint at the spear hand
        if t >= T_IN - 1:
            lvl = 0.8 * smoothstep(T_IN - 1, T_IN + 1, t)
            fr = figure(fr, S, p, WOTAN, lvl, 22.0)
            fr += light(SPEAR, 0.6 * lvl * np.exp(-((d - p + 24) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The real music: the excerpt orchestrated from the piano reduction, and the staging: Mime's hammer, the
    stranger's arrival and tread, the spear striking the floor."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    forge = pan_at(S['anvil'])
    stand = pan_at(at(G, 'Right', WAND_AT))
    o = Orchestra(M, level=1.6)
    N = compose()
    for t, d, m, v, part, k in N:
        if part == 'wanderer':                                                  # his chords: trombones, tubas, horns
            o.play('trombones' if m >= 48 else 'tuba', m, t, d, v, stand, 0.75)
            if m >= 55:
                o.play('horns', m, t, d, v - 8, stand, 0.5)
            if m < 48:
                o.play('basses', m, t, d, v - 10, stand, 0.4)
        elif part == 'spear':                                                   # the spear strides down the bass
            o.play('trombones', m, t, d, v, stand, 0.8)
            o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 6, stand, 0.6)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 10, stand, 0.45)
        elif part == 'shoo':                                                    # Mime in a flap: strings, woodwinds
            o.play('violins' if m >= 55 else 'violas', m, t, d, v - 12, forge, 0.5)
            if m >= 72:
                o.play('flutes' if d < 0.25 else 'oboes', m, t, d, v - 20, forge, 0.3)
    o.tutti([e[:4] + (e[5] if e[5] in (0, 1) else 0, e[5] == 'trem') for e in N if e[4] in ('orch', 'fury')],
            size=lambda t: 0.9 if t < T_ROLL else 0.6)
    for t, d, m, v, part, k in N:
        if part == 'tap':                                                       # Mime's hammer on the anvil
            o.hit('anvil', t, min(127, v), gain=0.55, pan=forge)
    o.hit('timpani roll', T_ROLL, 80, pitch=-6, gain=0.5, pan=pan_at(G.pd.max()))
    for c, k in chords():
        if k == 0 and c < T_STAND + 1:                                          # his tread, a step on each chord
            o.hit('bass drum', c + 0.9, 70, gain=0.35, pan=stand)
    o.boom(T_STRIKE, stand, 1.0)                                                # the spear strikes the floor
    o.hit('metal', T_STRIKE, 110, gain=0.35, pan=stand)
    o.thunder(T_STRIKE + 0.1, 0.55, stand, 0.8)
    o.fire(0.0, D + 0.5, lambda tt: 0.4 - 0.25 * smoothstep(T_STRIKE, T_STRIKE + 1, tt) +
           0.15 * smoothstep(T_STRIKE + 4, D, tt), forge, crackle=8, seed=606)
    o.effects([(0, -3), (T_ROLL, -3), (T_IN + 1, -9), (T_SHOO, -9), (T_STRIKE - 0.3, -1), (T_STRIKE + 3, -1),
               (T_STRIKE + 5, -9), (D, -9)])
