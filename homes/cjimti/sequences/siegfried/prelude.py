"""Prelude: Mime's cave in the forest, in the dark. The forge is the porch, the anvil the middle of Porch Front,
the chimney walls Porch Left and Porch Right; the rest of the house is the rock of the cave, and the free end of
Right its mouth, where the forest shows green.

The music is Wagner's own: the opening of the prelude to Siegfried (bars 0 to 5), its climax (bars 98 to 124) and
Mime at his anvil (bars 136 to 155), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from
the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the timpani's roll on the low F and the two bassoons
brooding in thirds over it; the hoard motif's long notes on bassoons and clarinets, its churning bass as string
tremolo; the hammering in octaves fortissimo on cellos, basses and tuba; the Sword motif on the trumpet; Mime's
smithing motif on bassoons and violas; and his grumbling after he throws the hammer down on cellos, basses and
bassoons. The staging adds what a production would: the anvil rings under every hammer blow, the forge fire
crackles and roars with the music, and the hammer clatters off the anvil when he throws it down.

In the dark the hoard Mime dreams of glints round the porch, gold on each note of the bassoons. Then his hammer
starts on the anvil, every blow a white-hot flash and a spray of sparks flying out both ways along the roofline,
each bar harder, until the hammering roars in octaves and the whole porch blazes orange. At the top the trumpet
gives the Sword he cannot forge, and a white-gold wave sweeps the house from end to end and back. Mime taps on,
then hammers in a frenzy ("Zwangvolle Plage!"), sparks flying on every stroke, and throws the hammer down: the
sparks die, the forge sinks to a glow and he crouches by it, while a green light waits at the cave mouth.

compose() tags every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF01'
TITLE = 'Prelude'
KIND = 'show'
DESCRIPTION = ('Deep in a forest cave a dwarf smith dreams of a golden Ring. His hammer starts on the anvil, sparks '
               'fly along the whole roof, and the forge roars until he throws the hammer down.')
VOICEOVER = ('In a cave in the forest, a dwarf hammers at his forge, and dreams of a golden ring. '
             'This is Siegfried.')

K = 0                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 0-5, 98-124 and 136-155, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_SEG2, T_SEG3 = EX['segments'][1]['start'], EX['segments'][2]['start']
T_MIME = [BAR[103]]                         # his hammer starts on the anvil
T_FORGE = [BAR[111]]                        # the forge roars: the hammering in octaves, fortissimo
T_RING = BAR[117]                           # the Sword motif on the trumpet: the white wave
T_RING_END = BAR[121]                       # Mime's tapping again
T_THROW = BAR[152]                          # he throws the hammer down

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

START = dict(bed=0.24, forge=0.32, walls=0.25, mouth=0.4)
END = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # where SF02 picks the cave up
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil


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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The opening's left hand is the
    timpani's roll ('roll'), its right hand the bassoons brooding in thirds ('under', a glint of the hoard each), as
    are the long notes of the brooding hoard motif after it; 'blow' is a hammer blow (k its strength: the first note
    of each bar of the rising sequence, every low G of the fortissimo hammering, Mime's tapping, the repeated notes
    of his smithing motif and the accents under "Zwangvolle Plage"); 'sword' is the Sword motif on the trumpet;
    'throw' marks the hammer thrown down (silent) and 'grumble' the low strings after it; everything else 'orch'."""
    N = []
    first = {}
    for t, d, m, v, h in EX['notes']:
        b = max(mm for mm, bt in EX['bars'] if bt <= t + 1e-6)
        part, k = 'orch', None
        if t < T_SEG2:
            part = 'roll' if h == 1 else 'under'
        elif b < 103 and h == 0 and d >= 0.5:
            part = 'under'
        elif 103 <= b < 111 and h == 1 and b not in first:
            first[b] = t
            part, k = 'blow', 0.55 + 0.05 * (b - 103)
        elif 111 <= b < 117 and h == 1 and m < note('C2'):
            part, k = 'blow', 1.0
        elif 117 <= b < 121 and h == 0:
            part = 'sword'
        elif 121 <= b < 124 and h == 0 and m < note('D4'):
            part, k = 'blow', 0.45
        elif 136 <= b < 140 and h == 0 and m == note('F4'):
            part, k = 'blow', 0.8
        elif 140 <= b < 152 and h == 1 and d >= 0.8:
            part, k = 'blow', 0.9
        elif b >= 152:
            part = 'grumble'
        N.append((t, d, m, v, part, k))
    N.append((T_THROW, 0.1, 30, 0, 'throw', None))
    return sorted(N, key=lambda e: e[0])


def blows(S):
    """Every hammer blow on the anvil: [(time, strength, where)]."""
    return sorted((t, k, S['anvil']) for t, _, m, v, part, k in compose() if part == 'blow')


def render(G, seed=1):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    N = compose()
    hits = blows(S)
    L = d.max()
    hit_t = np.array([h[0] for h in hits])
    under = [e for e in N if e[4] == 'under']
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'sword'}))
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Left', 0.1), L - 40, len(under))
    p_mime = at(G, 'Porch Front', MIME_AT)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        build = smoothstep(T_MIME[0], T_FORGE[0], t) * (1 - smoothstep(T_THROW, T_THROW + 4, t))
        roar = (smoothstep(T_FORGE[0] - 1, T_FORGE[0] + 0.5, t) * (1 - smoothstep(T_RING_END, T_RING_END + 2, t)) +
                smoothstep(T_SEG3 - 0.3, T_SEG3 + 0.3, t) * (1 - smoothstep(T_THROW, T_THROW + 3, t)))
        lv = {k: keys(t, [(0, START[k]), (T_THROW, START[k] + (END[k] - START[k]) * 0.5),
                          (D, END[k])]) for k in START}
        lv['forge'] += 0.35 * build + 0.35 * roar
        lv['walls'] += 0.3 * build + 0.45 * roar
        fr = cave(S, T, lv)

        # the hoard he dreams of: gold glints chasing round the porch with each note of the undercurrent
        for j, (t0, dur, m, v, part, k) in enumerate(under):
            a = t - t0
            if 0 <= a < dur + 1.5:
                p = glint_at[j]
                g = 0.9 * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.06, a)
                fr += light(GOLD, g * np.exp(-((d - p) / (30 + 40 * a)) ** 2))
                fr += light(HEAT, 0.6 * np.exp(-a / 0.15) * np.exp(-((d - p) / 10) ** 2))

        # each hammer blow: a white-hot flash on the anvil, a flare of the forge, and sparks both ways
        i = int(np.searchsorted(hit_t, t, side='right')) - 1
        if i >= 0 and t - hit_t[i] < 1.0:
            a, s = t - hit_t[i], hits[i][1]
            fr += light(HEAT, min(1.0, 1.1 * s * np.exp(-a / 0.09)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.45 * s * np.exp(-a / 0.25) * (S['forge'] + S['walls']))
            fr += light(FORGE, 0.7 * s * np.exp(-a / 0.45) * np.exp(-((np.abs(d - anvil) - 1500 * a) / 70) ** 2))
        fr += light(SPARK, np.clip(sparks(S, hits, t, 50), 0, 1.0))

        # the Sword he cannot forge: a white-gold wave sweeps the whole house out to both ends and back
        if T_RING <= t < T_RING_END:
            a = t - T_RING
            j = int(np.searchsorted(ring_on, t, side='right')) - 1
            pulse = np.exp(-(t - ring_on[j]) / 0.35) if j >= 0 else 0.0
            front = (a / 3.2) % 2
            front = front if front < 1 else 2 - front
            dist = np.abs(d - anvil) / max(anvil, L - anvil)
            wave = np.exp(-((dist - front) / 0.12) ** 2)
            wave = np.exp(-((dist - front) / 0.16) ** 2) + 0.35 * (dist < front)
            fade = 1 - smoothstep(T_RING_END - 1.5, T_RING_END, t)
            fr += light(GOLD, (1.0 * wave + 0.35 * pulse * (1 - dist)) * fade)
            fr += light(WHITE, 0.5 * pulse * np.exp(-((dist - front) / 0.08) ** 2) * fade)
        if T_RING <= t < T_RING + 0.6:
            fr += light(WHITE, 0.55 * np.exp(-(t - T_RING) / 0.12))

        # Mime at the anvil, from the first blow; he slumps when he throws the hammer down
        if t >= T_MIME[0] - 2:
            lvl = keys(t, [(T_MIME[0] - 2, 0.0), (T_MIME[0] - 0.5, 0.75), (T_THROW, 0.85), (T_THROW + 1.0, 0.5)])
            col = MIME if t < T_THROW + 2 else MIME * 0.8 + MIME_DIM * 0.2
            bob = 6 * np.exp(-(t - hit_t[i]) / 0.15) if i >= 0 and t < T_THROW else 0.0
            fr = figure(fr, S, p_mime - bob, col, lvl)
        if T_THROW <= t < T_THROW + 1.5:
            a = t - T_THROW
            fr += light(HEAT, 0.9 * np.exp(-a / 0.12) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - anvil) - 500 * a) / 50) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the anvil rings under every hammer blow."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    forge = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=2.2)
    N = compose()
    tag = {(round(e[0], 4), e[2]): (e[4], e[5]) for e in N}

    def size(t):
        return 0.4 if t < T_MIME[0] else 0.7 if t < T_FORGE[0] else 1.0 if t < T_RING_END else \
            0.5 if t < T_SEG3 else 0.9

    def role(t, d, m, v, h):
        p, k = tag.get((round(t, 4), m), ('orch', None))
        if p == 'roll':
            return []
        if p == 'under':
            return [('bassoons', 0, 0, 0.8), ('clarinets', 0, -10, 0.4)]
        if p == 'sword':
            return [('trumpets', 0, 4, 0.95), ('horns', -12, -6, 0.5)]
        if p == 'grumble':
            return [('cellos', 0, 0, 0.8), ('basses', -12, -6, 0.6), ('bassoons', 0, -8, 0.5)]
        if p == 'blow' and h == 0 and t >= T_SEG3:          # his smithing motif: bassoons and violas, staccato
            return [('bassoons', 0, 0, 0.7), ('violas', 0, -6, 0.5)]
        if p == 'blow' and t >= T_RING_END and t < T_SEG3:  # his tapping
            return [('bassoons', 0, 0, 0.7), ('violas', 0, -8, 0.4)]
        return None

    early = [n for n in EX['notes'] if n[4] == 1 and T_SEG2 <= n[0] < T_SEG3]
    rest = [n for n in EX['notes'] if not (n[4] == 1 and T_SEG2 <= n[0] < T_SEG3)]
    o.tutti(sorted(rest + tidy(early)), size=size, role=role, pan=lambda t, m: forge * 0.5)
    # the opening: a timpani roll on the low F, under the bassoons
    for r in np.arange(0.0, T_SEG2 - 0.5, 3.0):
        o.hit('timpani roll', r, 70, pitch=-4, gain=0.55, pan=forge)
    o.hit('crash', T_SEG2, 100, gain=0.4)
    o.hit('timpani', T_SEG2, 110, pitch=-4, gain=0.6)
    for t, d, m, v, p, k in N:              # the anvil under every hammer blow, harder as the forge roars
        if p == 'blow':
            o.hit('anvil', t, int(70 + 55 * k), gain=0.25 + 0.45 * k, pan=forge)
            if k >= 0.9:
                o.hit('timpani', t, 100, pitch=-3, gain=0.3, pan=forge)
    o.hit('cymbal swell', T_RING - 2.8, 90, gain=0.35)
    o.hit('crash', T_RING, 118, gain=0.6)
    o.hit('crash', T_SEG3, 110, gain=0.45, pan=forge)
    o.hit('anvil', T_THROW, 127, gain=1.0, pan=forge)          # the hammer flung down: it clatters off the anvil
    o.hit('metal', T_THROW + 0.04, 115, gain=0.6, pan=forge)
    o.hit('metal', T_THROW + 0.33, 90, gain=0.35, pan=forge + 0.1)
    o.boom(T_THROW, forge, 0.6)
    o.effects([(0.0, 0.0), (T_RING - 1.0, 0.0), (T_RING, -9.0), (T_RING_END, -9.0), (T_RING_END + 1.0, -3.0),
               (T_SEG3, -3.0), (BAR[141], -7.0), (T_THROW - 0.5, -7.0), (T_THROW, 0.0), (D, 0.0)])
    o.fire(0.0, D, level=lambda tt: 0.25 + 0.35 * ((tt > T_FORGE[0]) & (tt < T_RING_END)) +
           0.3 * ((tt > T_SEG3) & (tt < T_THROW)), pan=forge, crackle=6.0)
