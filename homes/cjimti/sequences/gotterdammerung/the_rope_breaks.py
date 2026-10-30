"""The Rope Breaks: still night on Brünnhilde's rock, and the three Norns go on throwing the golden rope of fate
between them, a white-hot head racing from one to the next and a gold whip cracking on out to the end of the
house each time it is caught.

The music is Wagner's own: the end of the Norns' scene (bars 269 to 290, and 296 to 298), as Solti's 1958 Vienna
Philharmonic recording takes it, from "das Rheingold raubte Alberich" through the curse, the fraying, "Es riß!"
and the Norns' descent, "Hinab! Zur Mutter!". The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py): the Ring on bassoons and clarinets, the curse's heavy chords on trombones and tuba with the
timpani, the rope's rushing figures on violins and harp, the tremolo under the end on cellos and basses. The rope
creaks as it frays and snaps with a crack, a blow and two lashes flying apart; the Norns go down into the earth
over a timpani roll and a scraped gong; under their singing the effects keep out of the way.

But they sing now of Alberich and the Ring. Every note of the Ring flashes gold along the rope with a red glint
running through it; then the curse sounds and the rope turns blood red, red pulses racing along it and the whole
house throbbing red on its heavy low notes. The rope frays: dark gaps flicker through it, more and more, the throws
come twice a bar and stutter as the third Norn strains to pull it taut, and on "Es riß!" it snaps. One white flash
over the whole house, and the two broken ends whip away to the two ends of the roofline and are gone.

Each Norn flares as she sings; then one after another they sink into the earth, her grey white collapsing inward
in a ring, until the rock is empty. "Hinab! Zur Mutter!" Then only the night, the low fire round the rock, and in
the east, at the free end of Right, the first red of the coming day, red streaks shooting from it along the house.

compose() tags every note of the excerpt; stage(), heat(), fire(), scene(), strand() and figure() are shared word
for word by the Prologue's scenes (see GD01)."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD02'
TITLE = 'The Rope Breaks'
KIND = 'show'
DESCRIPTION = ('The Norns sing of the Ring and its curse, and the golden rope turns red and frays until it snaps. '
               'The broken ends whip away across the house and the Norns sink into the earth.')
VOICEOVER = ('The Norns sing of a ring of gold, and of a curse. '
             'The rope of fate begins to fray, and then it breaks.')

K = 1                                       # this scene's place on the Prologue's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # bars 269-290 and 296-298, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_THROWS = ([BAR[b] for b in range(269, 280)] +                       # a throw every bar, then twice a bar
            [x for b in range(280, 285) for x in (BAR[b], 0.5 * (BAR[b] + BAR[b + 1]))])
T_FAST = BAR[280]                           # the throws quicken and stutter
T_RING = BAR[269]
T_CURSE = BAR[277]                          # "ein rächender Fluch"
T_SNAP = BAR[285]                           # "Es riß!"
T_SINK = [BAR[288], BAR[290], BAR[296] + 3.0]   # a Norn sinks at each
T_HINAB = BAR[297]                          # "Zur Mutter!"
T_EAST = BAR[296]
T_STREAKS = [T_EAST + 1.5 + 2.4 * j for j in range(5)]
NORN_OF = {'Erste Norn': 0, 'Zweite Norn': 1, 'Dritte Norn': 2}
SUNG = [(t0, t1, NORN_OF[w]) for t0, t1, w, _ in EX['singing'] if w in NORN_OF]
D = EX['seconds']

NIGHT = hexc('#1a1070')
NIGHT2 = hexc('#3a1a9a')
STAR = hexc('#e0e8ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
EAST = hexc('#ff2a10')
DAWN = colormap([(0.0, hexc('#ff1040')), (0.35, hexc('#ff6a10')), (0.7, hexc('#ffc020')), (1.0, hexc('#fff4d0'))])
DAY = hexc('#40b0ff')
SUN = hexc('#fff0a0')
NORN = hexc('#c8c8d8')
ROPE = hexc('#ffcc40')
HOT = hexc('#fff4c0')
VALHALLA = hexc('#fff0a0')
GODS = hexc('#1a3cff')
CHORD = hexc('#6a20ff')
WHITE = hexc('#ffffff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
RINGRED = hexc('#ff1800')

START = dict(night=0.55, stars=0.7, rock=0.32, fire=0.4, east=0.0, dawn=0.0, hue=0.0, day=0.0, rope=0.5)
END = dict(night=0.5, stars=0.6, rock=0.32, fire=0.4, east=0.35, dawn=0.0, hue=0.0, day=0.0, rope=0.0)
NORNS_START = (0.8, 0.8, 0.8)               # Left 0.5, Porch Front 0.5, Right 0.5; all gone by the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky, the east at the free end of Right. The Norns' three places."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same stars, clouds and flames in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, L=float(d.max()), summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        east=(~porch) * np.exp(-((d.max() - d) / 650) ** 2),
        twinkle=Flicker(rng, G.N, 0.3, 2.5),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        fray=Flicker(rng, G.N, 1.5, 6.0),
        norns=[at(G, 'Left', 0.5), summit, at(G, 'Right', 0.5)],
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide=0.0, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def scene(S, T, lv):
    """The sky, the rock, the fire and the standing rope at shared time T with levels lv (night, stars, rock, fire,
    east, dawn, hue, day, rope)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.04 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.07 * T) + 1.1)
    sk = NIGHT + (NIGHT2 - NIGHT) * u[:, None]
    fr = light(sk, lv['night'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(STAR, lv['stars'] * S['sky'] * np.clip(S['twinkle'](T) - 0.9, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(EAST, lv['east'] * S['east'] * (0.8 + 0.2 * u))
    fr += light(DAWN(np.clip(lv['hue'] + 0.2 * (u - 0.5), 0, 1)), lv['dawn'] * (0.8 + 0.2 * u))
    fr += light(DAY + (SUN - DAY) * (0.4 * u)[:, None], lv['day'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'])
    if lv['rope'] > 0:
        a, b = S['norns'][0], S['norns'][2]
        fr += strand(S, a, b, 1.0, lv['rope'], T)
    return fr


def strand(S, a, b, u, lvl, T, fray=0.0):
    """The rope from path distance a toward b, laid u of the way (0..1), shimmering; a white-hot head while it
    flies. fray (0..1) breaks it into flickering gaps."""
    d = S['d']
    head = a + (b - a) * u
    lo, hi = min(a, head), max(a, head)
    on = smoothstep(lo - 8, lo + 8, d) * smoothstep(hi + 8, hi - 8, d)
    shimmer = 0.72 + 0.28 * np.sin(2 * np.pi * (d / 55 - 1.4 * T))
    gaps = np.clip(1 - fray * (0.55 + 0.7 * S['fray'](T)), 0, 1)
    fr = light(ROPE, lvl * on * shimmer * gaps)
    if u < 1:
        fr += light(HOT, min(1.0, 1.3 * lvl + 0.3) * np.exp(-((d - head) / 12) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


PAIRS = [(0, 1), (1, 2), (2, 0)]            # who throws to whom, round and round


def bar_of(t):
    return max([m for m, bt in BAR.items() if bt <= t + 1e-6] or [269])


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The right hand's longer notes
    as she sings of the Ring are the Ring ('ring'); bars 277-279 are the curse ('curse'); the rushing figures as the
    rope frays are the rope ('rope'); the rest 'orch'. k is tidy()'s tremolo flag."""
    N = []
    for n in tidy(EX['notes']):
        t, d, m, v, h = n[:5]
        b = bar_of(t)
        if b in (274, 275, 276) and h == 0 and d >= 0.3:
            part = 'ring'
        elif b in (277, 278, 279):
            part = 'curse'
        elif 280 <= b <= 284 and d < 0.25:
            part = 'rope'
        else:
            part = 'orch'
        N.append((t, d, m, v, part, n[5]))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=2):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L, nn = S['d'], S['L'], S['norns']
    N = compose()
    throws = [j for j, t0 in enumerate(T_THROWS) if t0 < T_SNAP - 0.5]
    ring = [e for e in N if e[4] == 'ring']
    curse = [e for e in N if e[4] == 'curse']
    lowc = sorted({e[0] for e in curse if e[2] < note('C3')})
    rng = np.random.default_rng(seed)
    gl_at = rng.uniform(nn[0], nn[2], len(ring))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_HINAB, START[k]), (T_HINAB + 6, END[k])]) for k in START}
        fray = smoothstep(BAR[271], BAR[284], t)
        red = smoothstep(T_CURSE, T_CURSE + 3, t)
        lv['rope'] = START['rope'] * (t < T_SNAP)
        lv['east'] = END['east'] * smoothstep(T_EAST, T_EAST + 10, t)
        fr = scene(S, T, dict(lv, rope=0.0))
        if lv['rope'] > 0:                  # the standing rope, fraying and reddening
            st = strand(S, nn[0], nn[2], 1.0, lv['rope'], T, fray)
            fr += st * (1 - red) + light(BLOOD, 1.2 * red * np.clip(st.max(1), 0, 1) ** (1 / 2.2))

        # throws, faster and stuttering as it frays
        for j in throws:
            t0 = T_THROWS[j]
            a = t - t0
            if not 0 <= a < 3.0 or t >= T_SNAP:
                continue
            i, k = PAIRS[j % 3]
            fly = (0.9 + 0.5 * (abs(i - k) == 2)) * (0.6 if t0 >= T_FAST - 0.01 else 1.0)
            u = smoothstep(0, fly, a)
            if t0 > BAR[279]:
                u *= 0.85 + 0.15 * np.sin(2 * np.pi * 7 * a)
            lvl = 1.0 * np.exp(-max(a - fly, 0) / 0.9)
            st = strand(S, nn[i], nn[k], u, lvl, T, 0.7 * fray)
            fr += st * (1 - 0.6 * red) + light(BLOOD, 0.8 * red * lvl * (st.max(1) > 0.02))
            if a >= fly:
                w = a - fly
                out_dir = 1 if nn[k] >= nn[i] else -1
                pos = nn[k] + out_dir * 1900 * w
                past = (out_dir * (d - nn[k]) > 0) * (out_dir * (pos - d) > 0)
                col = ROPE if red < 0.5 else BLOOD
                fr += light(col, 1.0 * np.exp(-w / 0.7) * np.exp(-((d - pos) / 110) ** 2))
                fr += light(col, 0.8 * np.exp(-w / 0.9) * past * (0.4 + 0.6 * np.exp(-(out_dir * (pos - d)) / 700)))

        # the Ring: gold flashes along the rope, each with a red glint running through it
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.0:
                g = np.exp(-a / (dur + 0.4)) * smoothstep(0, 0.05, a)
                fr += light(GOLD, 1.0 * g * np.exp(-((d - gl_at[j]) / (40 + 80 * a)) ** 2))
                fr += light(RINGRED, 0.9 * g * np.exp(-((d - gl_at[j] - 500 * a) / 18) ** 2))

        # the Curse: red pulses racing along the rope, the whole house throbbing red on its low notes
        for t0, dur, m, v, part, k in curse:
            a = t - t0
            if 0 <= a < 1.6 and m >= note('C3'):
                pos = nn[0] + (nn[2] - nn[0]) * ((a / 1.2 + (m % 5) / 5) % 1)
                fr += light(BLOOD, 0.9 * np.exp(-a / 0.8) * np.exp(-((d - pos) / 50) ** 2))
        for t0 in lowc:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.9 * np.exp(-a / 0.8))

        # the snap: one white flash, and the broken ends whip away to both ends of the house
        a = t - T_SNAP
        if 0 <= a < 3.0:
            fr += light(WHITE, 1.0 * np.exp(-a / 0.25))
            fr += light(ROPE, 0.9 * np.exp(-a / 1.0))
            fr += light(ORANGE, 0.6 * np.exp(-a / 1.8))
            mid = 0.5 * (nn[0] + nn[2])
            for side, lim in ((-1, 0.0), (1, L)):
                pos = mid + side * 1700 * (1 - np.exp(-a / 0.9))
                pos = max(pos, lim) if side < 0 else min(pos, lim)
                tail = (side * (d - mid) > 0) * (side * (pos - d) >= 0) * np.exp(-(side * (pos - d)) / 450)
                fr += light(ROPE, 1.4 * np.exp(-a / 1.5) * (0.35 + tail) * (side * (pos - d) >= 0) * (side * (d - mid) > 0))
                fr += light(HOT, 1.2 * np.exp(-a / 1.2) * np.exp(-((d - pos) / 70) ** 2))

        # the Norns: flaring as they sing, then sinking into the earth one by one, rings collapsing inward
        for n in range(3):
            ts = T_SINK[n]
            lvl = NORNS_START[n] * (1 - smoothstep(ts, ts + 2.5, t))
            if t < ts and any(t0 <= t < t1 + 0.6 for t0, t1, w in SUNG if w == n):   # she sings: she flares
                lvl += 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t))
            if t > BAR[279] and t < ts:
                lvl += 0.15 * fray * np.sin(2 * np.pi * (3 + n) * t)
            a = t - ts
            if 0 <= a < 2.5:
                r = 900 * np.exp(-a / 0.6)
                fr += light(NORN, 1.0 * (1 - a / 2.5) * np.exp(-((np.abs(d - nn[n]) - r) / 130) ** 2))
                fr += light(NORN, 0.45 * np.exp(-a / 0.3))
            if lvl > 0.01:
                fr = figure(fr, S, nn[n], NORN, lvl, w=16.0 * (0.4 + 0.6 * (1 - smoothstep(ts, ts + 2.5, t))))
        a = t - T_HINAB
        if 0 <= a < 3.0:
            for p in nn:
                fr += light(NORN, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p) - 500 * np.exp(-a / 0.5)) / 50) ** 2))

        # the first red of day: streaks shooting from the east along the house
        for j, t0 in enumerate(T_STREAKS):
            a = t - t0
            if 0 <= a < 3.0:
                pos = L - 900 * a
                fr += light(EAST, (0.75 + 0.04 * j) * np.exp(-a / 1.4) * np.exp(-((d - pos) / 260) ** 2))
                fr += light(DAWN(0.2), 0.5 * np.exp(-a / 0.8) * S['east'])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the rope creaking and snapping as a production
    would stage it."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S = stage(G)
    nn = [pan_at(p) for p in S['norns']]
    o = Orchestra(M, level=2.6)
    N = compose()
    tag = {(round(e[0], 4), e[2]): e[4] for e in N}

    def role(t, d, m, v, h):
        part = tag.get((round(t, 4), m), 'orch')
        if part == 'ring':                                          # the Ring: bassoons and clarinets
            return [('bassoons', 0, 6, 0.8), ('clarinets', 0, 0, 0.5)]
        if part == 'curse':                                         # the curse: trombones and tuba
            if h == 1 and m < 48:
                return [('tuba', 0, 4, 0.7), ('basses', 0, 0, 0.5)]
            return [('trombones', 0, 6, 0.75), ('horns', 0, -4, 0.45)]
        if part == 'rope':                                          # the rope's rushing figures
            return [('violins', 0, 0, 0.5)] + ([('harp', -12, -6, 0.4)] if m >= 72 else [])
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 0.85 if T_CURSE <= t < T_SNAP + 8 else 0.5, role=role,
            pan=lambda t, m: 0.6 * float(np.sin(2 * np.pi * t / 3.1)) if T_FAST <= t < T_SNAP else 0.0)
    for e in N:                                                     # the curse's low notes: timpani
        if e[4] == 'curse' and e[2] < 48 and e[1] >= 0.6:
            o.hit('timpani', e[0], 110, pitch=-4, gain=0.6, pan=nn[1])
    for j in range(5):                                              # the rope creaks as it frays
        t0 = BAR[280 + j] + 0.3
        o.hit('scrape', t0, 70 + 10 * j, gain=0.25 + 0.06 * j, pan=nn[j % 3])
    # the snap: a crack, a blow, and two lashes flying apart to the ends of the house
    o.shatter(T_SNAP, 0.0, 1.0)
    o.boom(T_SNAP + 0.02, 0.0, 0.9)
    o.M.add('fx', whoosh(1.4, 6000, 300, 0.8, seed=41), T_SNAP, 0.9, -0.8)
    o.M.add('fx', whoosh(1.4, 6000, 300, 0.8, seed=42), T_SNAP, 0.9, 0.8)
    for n, ts in enumerate(T_SINK):                                 # each Norn sinking into the earth
        o.hit('timpani roll', ts - 0.4, 90, pitch=-7, gain=0.5, pan=nn[n])
        o.hit('gong scrape', ts, 90, gain=0.35, pan=nn[n])
    o.hit('gong', T_HINAB, 96, gain=0.4)
    # the fader: out of the way while they sing; up for the fraying and the snap; down again as they go
    o.effects([(0.0, -14.0), (BAR[279], -14.0), (T_FAST, -6.0), (T_SNAP - 0.3, 0.0), (T_SNAP + 3.0, 0.0),
               (T_SNAP + 6.0, -8.0), (D, -8.0)])
