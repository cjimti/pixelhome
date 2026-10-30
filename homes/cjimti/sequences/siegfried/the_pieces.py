"""The Pieces of Nothung: in Mime's cave, Siegfried, emerald with a white-hot head, waits on the right of the anvil
and Mime crouches on its left. "Sieh' her, ein zerbroch'nes Schwert": Mime brings out what is left of the sword
his mother kept, and with every note one of seven white steel shards flashes on the anvil, the porch cracking
white, the gold hilt glinting in the middle. Siegfried seizes on it, the strings rushing upward, and a white
streak of steel races from the anvil to both ends of the house on every bar: "dann schwing' ich mein rechtes
Schwert!"

The music is Wagner's own: Act I, bars 1114 to 1132 and 1188 to 1250, as Solti's 1958 Vienna Philharmonic recording
takes them, from Mime's "für Mühe, Kost und Pflege" to Siegfried's song of freedom ("Aus dem Wald fort in die Welt
ziehn ... dich, Mime, nie wieder zu sehn!"), his dash out and the orchestra storming after him, to Mime's "Da
stürmt er hin!". The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Mime's chords
on clarinets, bassoons and a horn, Siegfried's song on the full orchestra, his dash on violins and flutes. The
staging adds a ring of steel on every shard and streak, running feet and a rush of air as he bolts, a boom at the
cave mouth and the forest wind roaring in after him.

"Aus dem Wald fort in die Welt!" Each of his phrases is an emerald burst rolling out from him over the roofline,
the forge leaping with it; then the scales rush up and he bolts down Porch Right and along Right and out of the
cave mouth, an emerald comet pulling a green flood of forest light behind it across the whole house. The
orchestra storms after him, green gusts rolling in from the mouth on every bar, until the flood drains away and
Mime is left alone at the anvil with the shards.

compose() tags every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'SF05'
TITLE = 'The Pieces of Nothung'
KIND = 'show'
DESCRIPTION = ('The dwarf shows the boy the shattered pieces of his father\'s sword. Siegfried orders it mended by '
               'nightfall and storms out of the cave into the forest.')
VOICEOVER = ('Here are the pieces of your father\'s sword. '
             'Mend it, says Siegfried, and he is gone into the forest.')

K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 1114-1132 and 1188-1250, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_SHARDS = [BAR[1118]]                      # "Sieh' her, ein zerbroch'nes Schwert": the shards flash on its notes
T_SWORD = [BAR[1125]]                       # the strings rush up: steel races from the anvil to both ends
T_AUDACITY = EX['segments'][1]['start']     # "Aus dem Wald fort in die Welt ziehn!"
T_FREE = [BAR[1220]]                        # the scales rushing up; he bolts
T_RUN = BAR[1222]
T_OUT = BAR[1225]                           # he is out of the cave mouth
T_STORM = BAR[1230]                         # the orchestra storms after him
T_LAMENT = BAR[1247]                        # "Da stürmt er hin!": Mime alone
T_GRUMBLE = BAR[1249]

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
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)     # the cave at every cut in Act I
MIME_AT = 0.32                              # Mime's place on Porch Front, beside the anvil
SIEG_AT = 0.7
SHARDS = [-70, -44, -20, 4, 26, 50, 76]     # the seven pieces, path distance from the anvil

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Under "Sieh' her" the right hand's
    notes each flash a shard ('nothung'); the first note of each bar of the rush up is the Sword's streak ('sword');
    the loud right-hand notes of his song of freedom are his audacity ('audacity'); the scales of his dash are
    'freedom'; the first note of each bar of the storm after him is 'storm'; Mime's cries after him and his last
    grumble are 'lament' (silent marks); everything else 'orch'."""
    N = []
    seen = set()
    for t, d, m, v, h in EX['notes']:
        b = max(mm for mm, bt in EX['bars'] if bt <= t + 1e-6)
        part = 'orch'
        if 1118 <= b < 1125 and h == 0:
            part = 'nothung'
        elif 1125 <= b < 1131 and h == 0 and b not in seen:
            seen.add(b)
            part = 'sword'
        elif T_AUDACITY <= t < T_FREE[0] and h == 0 and v >= 80:
            part = 'audacity'
        elif T_FREE[0] <= t < T_OUT and h == 0:
            part = 'freedom'
        elif T_STORM <= t < T_LAMENT and b not in seen:
            seen.add(b)
            part = 'storm'
        N.append((t, d, m, v, part, 0))
    for b in (1222, 1226, 1249):
        N.append((BAR[b], 1.0, 60, 0, 'lament', 0))
    return sorted(N, key=lambda e: e[0])


def where_siegfried(G, t):
    """Siegfried's path distance at time t: by the anvil, then out along Porch Right and Right."""
    return keys(t, [(T_RUN, at(G, 'Porch Front', SIEG_AT)), (T_RUN + 1.5, at(G, 'Porch Right', 0.6)),
                    (T_OUT, G.pd.max() + 60)])


def render(G, seed=5):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    shard_on = [e for e in N if e[4] == 'nothung']
    storm_on = [(e[0], e[3]) for e in N if e[4] == 'storm']
    sword_on = np.array(sorted({e[0] for e in N if e[4] == 'sword'}))
    burst = [e for e in N if e[4] == 'audacity']
    free_on = np.array(sorted({e[0] for e in N if e[4] == 'freedom'}))
    p_mime = at(G, 'Porch Front', MIME_AT)
    lament = [e for e in N if e[4] in ('lament', 'grumble')]
    hits = [(e[0], 0.8, anvil + SHARDS[j % 7]) for j, e in enumerate(shard_on)]
    hits += [(e[0], 0.7, where_siegfried(G, e[0])) for e in burst]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        p = where_siegfried(G, t)
        aud = smoothstep(T_AUDACITY - 0.5, T_AUDACITY + 1, t) * (1 - smoothstep(T_FREE[0], T_RUN, t))
        lv['forge'] += 0.3 * aud
        lv['walls'] += 0.3 * aud
        fr = cave(S, T, lv)

        # the shards: seven pieces of white steel on the anvil, each flashing on its note, the porch cracking white
        shown = smoothstep(T_SHARDS[0] - 1.5, T_SHARDS[0], t)
        for j, sx in enumerate(SHARDS):
            fr += light(STEEL, 0.4 * shown * np.exp(-((d - anvil - sx) / 6) ** 2))
        fr += light(HILT, 0.7 * shown * np.exp(-((d - anvil - 4) / 5) ** 2))
        for j, (t0, dur, m, v, part, k) in enumerate(shard_on):
            a = t - t0
            if 0 <= a < 1.2:
                sx = SHARDS[j % 7]
                fr += light(STEEL, min(1.0, 1.2 * np.exp(-a / 0.3)) * np.exp(-((d - anvil - sx) / 12) ** 2))
                fr += light(STEEL, np.exp(-a / 0.14) * (S['forge'] > 0) + 0.7 * np.exp(-a / 0.22) * S['walls'])

        # the Sword: a white streak of steel from the anvil out to both ends of the house on every note
        i = int(np.searchsorted(sword_on, t, side='right')) - 1
        if i >= 0 and t - sword_on[i] < 1.4:
            a = t - sword_on[i]
            r = 1900 * a
            fr += light(STEEL, np.exp(-a / 0.6) * np.exp(-((np.abs(d - anvil) - r) / 90) ** 2))
            fr += light(STEEL, 0.45 * np.exp(-a / 0.35) * (np.abs(d - anvil) < r))
            fr += light(WHITE, 0.4 * np.exp(-a / 0.08) * S['heat'] ** 0.4)

        # his audacity: an emerald burst rolling out from him on every note
        for t0, dur, m, v, part, k in burst:
            a = t - t0
            if 0 <= a < 1.5:
                r = 60 + 1300 * a
                ring = np.exp(-((np.abs(d - p) - r) / 150) ** 2) + 0.45 * (np.abs(d - p) < r)
                fr += light(SIEGFRIED, 0.95 * np.exp(-a / 0.55) * ring)
        fr += light(SIEGFRIED, 0.12 * aud)
        fr += light(SPARK, np.clip(sparks(S, hits, t, 55, n=10), 0, 1.0))

        # the run: an emerald comet out of the cave mouth with a flood of forest green behind it
        for ts, sv in storm_on:             # the storm after him: green gusts roll in from the mouth on every bar
            a = t - ts
            if 0 <= a < 1.6:
                fr += light(FOREST, 1.1 * (sv / 127) ** 2 * np.exp(-a / 0.6) *
                            np.exp(-(((L - d) - 1800 * a) / 220) ** 2))
                fr += light(SIEGFRIED, 0.35 * (sv / 127) ** 2 * np.exp(-a / 0.3) * S['mouth'])
        if T_RUN - 0.2 <= t < T_LAMENT + 2:
            a = t - T_RUN
            behind = smoothstep(p - 900, p - 50, d) * (d < p + 30) if t < T_OUT else 1.0
            flood = 0.75 * behind * smoothstep(-0.2, 0.4, a) * (1 - 0.55 * smoothstep(T_OUT + 1, T_OUT + 4, t)) * \
                (1 - smoothstep(T_LAMENT - 1, T_LAMENT + 1.5, t))
            fr += light(FOREST, flood * (0.8 + 0.2 * S['leaf'](T)))
            fr += light(SIEGFRIED, 0.5 * flood * np.exp(-((d - p) / 260) ** 2))
        j = int(np.searchsorted(free_on, t, side='right')) - 1
        if j >= 0 and t - free_on[j] < 0.8 and t < T_OUT:
            a = t - free_on[j]
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 0.25) * np.exp(-((d - p) / 140) ** 2))
        if T_OUT <= t < T_OUT + 2.5:
            a = t - T_OUT
            fr += light(FOREST, 0.9 * np.exp(-a / 0.5) * S['mouth'])
            fr += light(WHITE, 0.5 * np.exp(-a / 0.15) * S['mouth'] ** 3)

        for t0, dur, m, v, part, k in lament:
            a = t - t0
            if 0 <= a < 1.2:
                r = 40 + 700 * a
                fr += light(MIME, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - r) / 60) ** 2))

        # Mime at the anvil, shrinking when the boy roars, whining alone after
        lam = smoothstep(T_LAMENT - 1, T_LAMENT, t)
        mlvl = keys(t, [(0, 0.6), (T_AUDACITY, 0.6), (T_AUDACITY + 1, 0.38), (T_OUT, 0.38), (T_LAMENT, 0.75),
                        (D - 4, 0.6)])
        wob = 0.15 * lam * np.sin(2 * np.pi * 1.3 * t) * (t < D - 4)
        fr = figure(fr, S, p_mime, MIME, mlvl + wob)

        # Siegfried: emerald, a white-hot head on the side he faces
        if t < T_OUT + 0.3:
            lvl = 0.8 + 0.2 * aud
            fr = figure(fr, S, p, SIEGFRIED, lvl, 18.0)
            ahead = 8 if t >= T_RUN else 0
            fr += light(HEAD, lvl * np.exp(-((d - p - ahead) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the shards ring, and the forest roars in after him."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    forge = pan_at(at(G, 'Porch Front', 0.5))
    mouth = pan_at(at(G, 'Right', 0.95))
    o = Orchestra(M, level=2.35)
    N = compose()
    tag = {(round(e[0], 4), e[2]): e[4] for e in N}

    def role(t, d, m, v, h):
        p = tag.get((round(t, 4), m), 'orch')
        if t < T_SWORD[0] and h == 0:       # Mime's sad chords as he shows the pieces: clarinets, bassoons, horn
            return [('clarinets', 0, 30, 0.6), ('bassoons', -12, 26, 0.4), ('horns', 0, 20, 0.3)]
        if t < T_SWORD[0] and h == 1:
            return [('cellos', 0, 30, 0.5), ('basses', -12, 24, 0.4)]
        if p == 'freedom':                  # the dash: violins and flutes racing up
            return [('violins', 0, 0, 0.6), ('flutes', 0, -8, 0.4)]
        return None

    def pan(t, m):
        if t < T_RUN:
            return forge * 0.5
        return float(np.clip(pan_at(where_siegfried(G, min(t, T_OUT))) * 0.8, -0.9, 0.9))

    o.tutti(EX['notes'], size=lambda t: 0.6 if t < T_AUDACITY else 1.0, role=role, pan=pan)
    for t, d, m, v, p, k in N:
        if p == 'nothung':                  # each shard rings as it flashes on the anvil
            o.hit('triangle', t, 70, gain=0.25, pan=forge)
        elif p == 'sword':
            o.hit('metal', t, 90, gain=0.25, pan=forge)
    o.hit('crash', BAR[1130], 110, gain=0.5, pan=forge)   # "mein rechtes Schwert!"
    o.hit('crash', T_AUDACITY, 115, gain=0.5)
    # he bolts out of the cave: running feet, a rush of air, the forest roaring in after him
    o.gallop(T_RUN, T_OUT, 0.3, pan=lambda t: pan_at(where_siegfried(G, t)), v=110, gain=0.9)
    M.add('fx', whoosh(1.4, 400, 4000, 0.7, seed=12), T_RUN, 0.9, mouth)
    o.boom(T_OUT, mouth, 0.6)
    o.wind(T_OUT - 0.5, T_LAMENT + 1.5, lambda tt: 0.4 + 0.6 * ((tt > T_STORM) & (tt < T_LAMENT - 1)), pan=mouth)
    o.hit('timpani roll', T_STORM, 110, pitch=-4, gain=0.5)
    o.fire(0.0, D, 0.22, pan=forge, crackle=4.0)
    o.effects([(0.0, -10.0), (T_RUN - 0.5, -10.0), (T_RUN, 0.0), (T_LAMENT, 0.0), (T_LAMENT + 1.5, -8.0), (D, -8.0)])
