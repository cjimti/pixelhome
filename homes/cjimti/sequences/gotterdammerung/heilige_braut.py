"""Heilige Braut: the valley at dusk as GD24 left it, Siegfried dying in the middle of Porch Front with the vassals'
torches drawn in round him, Gunther beside him. His heartbeat is still going, faint. Then the harp begins, and the
music of Brünnhilde's awakening comes back to him: rising chords, E minor into C major, the harp running up through
each one. Every chord blooms a wave out of him over the whole house, silver white in front and gold behind, and with
each one the vision holds a little more of the house, until every run shimmers silver with gold glinting all through
it and his emerald burns bright again. "Brünnhilde! Heilige Braut!": his voice sends emerald surging through the
silver; violet ripples shimmer after it, and on "da lacht ihm Brünnhildes Lust" the climax surges emerald end to end.
"Brünnhild' bietet mir Gruß!": on its last note he dies, one white flash over the whole house, his emerald goes out,
the vision falls back into him from both ends like a tide running out, and the night comes down.

The music is Wagner's own, Act III, bars 866 to 869, 872 to 874, 898 to 900 and 909 to 912 as Solti's 1958 Vienna
Philharmonic recording takes them, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): harp and the
violins' shimmer for the arpeggios, soft strings and winds for the held chords. His lines are not in the reduction,
so they are taken from the Schott vocal score (archive.org gtterdmmerung1900wagn, pp. 297 to 301) and played on the
horn, his own instrument, doubled by the cellos. Nothing else is added but the last of his heartbeat on the timpani
and a soft gong as he dies.

compose() holds every note; stage(), scene(), water(), figure(), torches(), sparks() and ring() are the valley,
shared word for word by Act III's scenes (GD22 to GD30) on a clock that runs on from scene to scene: T = t + 80 K."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise, colormap
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD25'
TITLE = 'Heilige Braut'
KIND = 'show'
DESCRIPTION = ('Dying, Siegfried remembers the morning he woke Brünnhilde, and the whole house fills with her '
               'silver and gold. He greets her one last time, and dies.')
VOICEOVER = ('At the very end, his memory comes back. With his last breath, Siegfried greets Brünnhilde.')

K = 3                                       # this scene's place on Act III's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act III, bars 866-870, 872-875, 898-901 and 909-913, Solti 1958
D = EX['seconds']
SEG = [s_['start'] for s_ in EX['segments']] + [D]


def when(m):
    """Bar position m (as in the dataset) -> seconds into the excerpt."""
    for s_ in EX['segments']:
        a, b = s_['measures']
        if a <= m <= b:
            bars = [(x, y) for x, y in EX['bars'] if a <= x <= b]
            return float(np.interp(m, [x for x, _ in bars], [y for _, y in bars]))
    raise ValueError(m)


CHORDS = [(when(866), 'E minor'), (when(867), 'C major'), (when(872), 'E minor'), (when(873), 'D minor')]
T_SLEEP = when(874.67)                      # after "Heilige Braut!": the magic sleep, shimmering
T_LOVE = SEG[2]                             # "da lacht ihm Brünnhildes Lust"
T_DEATH = when(912.3)                       # "... bietet mir Gruß!": he dies
T_FATE = []
# His lines, from the vocal score (tenor, sounding an octave below the written treble): (bar, start, length in
# beats, note); 3/4 to bar 910, 4/4 from 911
VOICE = [(868, 0, 1, 'C4'), (868, 1, 1.5, 'G3'), (868, 2.5, 0.5, 'G3'),
         (873, 1, 1, 'B3'), (873, 2, 0.75, 'B3'), (873, 2.75, 0.25, 'B3'), (874, 0, 2, 'D4'),
         (910, 1, 1, 'B3'), (910, 2, 1, 'E3'), (911, 2, 0.75, 'B3'), (911, 2.75, 0.25, 'B3'), (911, 3, 0.5, 'A#3'),
         (912, 0, 1, 'C#4')]

SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GOLD = hexc('#ffaa00')
SILVER = hexc('#f4f8ff')
GLINT = hexc('#ffd060')
VIOLET = hexc('#a090ff')
GUNTHER = hexc('#ffb020')
BLOOD = hexc('#d00010')
FATE_C = hexc('#5a30ff')

START = dict(river=0.55, forest=0.4, sun=0.0, night=0.25, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
END = dict(river=0.4, forest=0.25, sun=0.0, night=0.45, pyre=0.0, blaze=0.0, valhalla=0.0, flood=0.0)
SIEG_AT = ('Porch Front', 0.65)             # 0.45 * (0.8 + 0.2 sin(2 pi (t + 80) / 0.7)) at the start; the body 0.3 at the end
GUNTHER_AT = ('Porch Front', 0.3, 0.6)      # 0.6 at the start, 0.55 at the end
TORCHES = (0.45, 0.6, 0.3, 0.6)             # torch level at the start and end, how far drawn in to him at the start, end
BODY = 0.3                                  # the body's level at the end (no head; the gold glint 0.4)

RIVER_DEEP = hexc('#0c1c8c')
RIVER_TEAL = hexc('#0a7c8a')
RIVER_GREEN = hexc('#14c080')
FOAM = hexc('#c0f4ff')
FOREST = hexc('#18a020')
SUN = hexc('#ffd040')
NIGHT = hexc('#1a2a90')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
VALHALLA = hexc('#fff0a0')
VBLUE = hexc('#1a3cff')
TORCH = hexc('#ff6a10')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The Rhine valley as profiles over the house: the river along Right and the Side (flowing out toward the free
    end of Right, and back along the Side), the forest over Left and the porch, the porch also the pyre to come."""
    d = G.pd
    rng = np.random.default_rng(1876)       # the same river, trees and torches in every scene, so the cuts match
    river = np.isin(G.seg_of, ['Right', 'Side'])
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    pf = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, L=float(d.max()), pf=pf, river=river, porch=porch, land=~river,
        flow=np.where(G.seg_of == 'Side', -1.0, 1.0),
        trees=(~river) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        pyre=porch * (0.45 + 0.55 * np.exp(-((d - pf) / 170) ** 2)),
        torch_at=np.sort(rng.uniform(at(G, 'Left', 0.05), at(G, 'Right', 0.6), 28)),
        torch_ph=rng.uniform(0, 2 * np.pi, 28),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        sparkle=Flicker(rng, G.N, 1.5, 4.0),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def water(S, T, lvl, where):
    """The Rhine's colour at level lvl over the pixels in `where` (0..1): currents in indigo, teal and green."""
    d, fw = S['d'], S['flow']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 230 - fw * 0.45 * T)) + 0.2 * np.sin(2 * np.pi * (d / 97 - fw * 0.8 * T) + 1.0)
    col = np.where((u < 0.5)[:, None], RIVER_DEEP + (RIVER_TEAL - RIVER_DEEP) * (2 * u)[:, None],
                   RIVER_TEAL + (RIVER_GREEN - RIVER_TEAL) * (2 * u - 1).clip(0, 1)[:, None])
    fr = light(col, lvl * where * (0.65 + 0.35 * u))
    return fr + light(FOAM, 0.5 * lvl * where * np.clip(S['sparkle'](T) - 1.1, 0, None))


def scene(S, T, lv):
    """The valley at shared time T with levels lv: river, forest, sun (shafts through the trees), night (a dark blue
    over everything), pyre (fire on the porch), blaze (fire on every run), valhalla (gold-white burning on the
    porch), flood (0..1, the Rhine's reach in from the free end of Right over everything)."""
    d, L = S['d'], S['L']
    front = L - lv['flood'] * (L + 60)
    wet = smoothstep(front - 40, front + 40, d) if lv['flood'] > 0 else np.zeros_like(d)
    dry = 1 - wet
    fr = water(S, T, lv['river'], S['river'] * dry)
    fr += light(FOREST, lv['forest'] * S['trees'] * (0.8 + 0.2 * S['leaf'](T)) * dry)
    shafts = np.clip(np.sin(2 * np.pi * (d / 330 + 0.04 * T)) * np.sin(2 * np.pi * (d / 127 - 0.07 * T) + 0.5), 0, 1)
    fr += light(SUN, lv['sun'] * S['land'] * shafts * dry)
    fr += light(NIGHT, lv['night'] * dry)
    q = np.clip(heat(d, T) + 0.18 * S['fl'](T), 0, 1)
    flames = (lv['pyre'] * S['pyre'] + lv['blaze'] * (1 - S['porch'] * (1 - S['pyre']))) * dry
    fr += light(FIRE(q), flames * (0.45 + 0.7 * q))
    fr += light(VALHALLA, lv['valhalla'] * S['pyre'] * (0.75 + 0.25 * q) * dry)
    fr += water(S, T, 0.9, wet) + light(FOAM, 0.9 * np.exp(-((d - front) / 30) ** 2) * (lv['flood'] > 0))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the scene, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def torches(fr, S, T, lvl, n=28, pull=None, k=0.0):
    """The vassals: n flickering torch points (pulled a share k of the way toward path distance `pull`)."""
    d = S['d']
    for p, ph in zip(S['torch_at'][:n], S['torch_ph'][:n]):
        if pull is not None:
            p = p + (pull - p) * k
        f = 0.8 + 0.2 * np.sin(7.3 * T + ph) * np.sin(3.1 * T + 2 * ph)
        fr = fr + light(TORCH, lvl * f * np.exp(-((d - p) / 6) ** 2)) + light(TORCH, 0.3 * lvl * np.exp(-((d - p) / 22) ** 2))
    return fr


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


def ring(fr, S, t, t0, p, col, lvl, speed=1400.0, width=90.0, tau=0.9):
    """A shockwave from path distance p started at t0, out to both ends."""
    a = t - t0
    if a < 0 or a > 4 * tau:
        return fr
    return fr + light(col, lvl * np.exp(-a / tau) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2))


def hold_factory(M, SR):
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
    return hold


def panner(G):
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))
    return pan_at


def thin(ts, gap):
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


def voice():
    """His lines in seconds: (time, seconds, midi)."""
    out = []
    for b, x, n, m in VOICE:
        per = 3 if b <= 910 else 4
        t0, t1 = when(b + x / per), when(b + (x + n) / per)
        out.append((t0, t1 - t0, note(m)))
    return out


def compose():
    """Every event for the lights: (time, seconds, midi, velocity, part, k). The heartbeat ('heart'), the awakening
    chords ('chord'), the harp's notes as gold glints ('harp'), the shimmer after "Heilige Braut!" ('sleep'), the
    climax's long notes ('love') and his own lines ('voice', also surging emerald)."""
    N = []
    notes = EX['notes']
    for j, tb in enumerate(heart()):
        N.append((tb, 0.3, note('E1'), 60 - 4 * j, 'heart', None))
    for k, (t0, name) in enumerate(CHORDS):
        N.append((t0, 5.0, note('E3'), 90, 'chord', k))
    for t in thin([n[0] for n in notes if n[4] == 0 and n[2] >= note('B4') and n[0] < T_LOVE], 0.12):
        N.append((t, 0.6, note('E5'), 80, 'harp', None))
    for t in thin([n[0] for n in notes if T_SLEEP <= n[0] < SEG[2]], 0.7):
        N.append((t, 1.0, note('E4'), 80, 'sleep', None))
    for t, d, m, v, h in notes:
        if T_LOVE <= t < SEG[3] and d >= 0.6:
            N.append((t, d, m, v, 'love', None))
    for t, d, m in voice():
        N.append((t, d, m, 100, 'voice', None))
        if d >= 0.6:
            N.append((t, d, m, 100, 'love', None))
    return sorted(N, key=lambda e: e[0])


def heart():
    """The last of his heartbeat, going on from GD24 until the harp takes over."""
    return [0.9, 3.4]


def levels(t):
    """Siegfried's level, his head's, and how much of the vision holds the house, at time t."""
    flick = 0.8 + 0.2 * np.sin(2 * np.pi * (t + 80) / 0.7)
    dying = 0.45 * flick
    rise = smoothstep(CHORDS[0][0], CHORDS[-1][0] + 2, t)
    bright = 0.85 + 0.1 * smoothstep(T_LOVE, T_DEATH - 1, t)
    alive = dying + (bright - dying) * rise
    gone = smoothstep(T_DEATH, T_DEATH + 2.0, t)
    lvl = alive * (1 - gone) + BODY * gone
    head = 0.8 * alive * (1 - gone)
    vision = smoothstep(CHORDS[0][0], CHORDS[-1][0] + 4, t) * (1 - smoothstep(T_DEATH, T_DEATH + 3.0, t))
    return lvl, head, vision


def render(G, seed=25):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_sf = at(G, *SIEG_AT)
    p_gu = at(G, *GUNTHER_AT[:2])
    reach = max(p_sf, L - p_sf)
    rng = np.random.default_rng(seed)
    harp = [e for e in N if e[4] == 'harp']
    glint_at = rng.uniform(0, L, len(harp))
    sleep = sorted({e[0] for e in N if e[4] == 'sleep'})
    love = [e for e in N if e[4] == 'love']
    fate = [e for e in N if e[4] == 'fate' and e[2] >= note('Ab3')]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        night = smoothstep(T_DEATH, D, t)
        lv = {k: START[k] + (END[k] - START[k]) * night for k in START}
        ls, lh, vis = levels(t)
        dim = 1 - 0.55 * vis
        fr = scene(S, T, {k: v * dim for k, v in lv.items()})

        # the vision: silver over the house, held a little wider with every chord, gold glinting all through it
        if vis > 0:
            dist = np.abs(d - p_sf) / reach
            held = smoothstep(vis + 0.08, vis - 0.08, dist)
            shim = 0.55 + 0.45 * np.sin(2 * np.pi * (d / 260 - 0.9 * t)) * np.sin(2 * np.pi * (d / 90 + 1.4 * t))
            fr += light(SILVER, 0.7 * held * shim * min(1.0, 1.4 * vis))
            # gold bands sweeping end to end through it, turning each bar
            for j in range(2):
                u = ((t + 1.6 * j) / 3.2) % 2
                u = u if u < 1 else 2 - u
                fr += light(GLINT, 0.95 * held * np.exp(-((d - u * L) / 90) ** 2) * min(1.0, 2 * vis))
            fr += light(GLINT, 0.9 * held * np.clip(S['sparkle'](T) - 0.9, 0, None) * min(1.0, 1.4 * vis))
        for k, (t0, chord) in enumerate(CHORDS):
            fr = ring(fr, S, t, t0, p_sf, SILVER, 1.0, speed=900, width=150, tau=1.6)
            fr = ring(fr, S, t, t0 + 0.25, p_sf, GLINT, 0.9, speed=800, width=220, tau=1.8)
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(WHITE, 0.45 * np.exp(-a / 0.12) * np.exp(-((d - p_sf) / 200) ** 2))
        for j, (t0, dur, m, v, _, k) in enumerate(harp):
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(GLINT, 0.95 * np.exp(-a / 0.3) * np.exp(-((d - glint_at[j]) / 12) ** 2))

        # the magic sleep: violet-silver ripples over the vision
        for t0 in sleep:
            fr = ring(fr, S, t, t0, p_sf, VIOLET, 1.0, speed=700, width=200, tau=1.4)

        # his love on the horn: every long note an emerald surge through the silver to both ends
        for t0, dur, m, v, _, k in love:
            if dur >= 0.6:
                fr = ring(fr, S, t, t0, p_sf, SIEGFRIED, 1.0, speed=1300, width=260, tau=1.4)
                fr = ring(fr, S, t, t0 + 0.12, p_sf, HEAD, 0.7, speed=1300, width=60, tau=1.0)

        # his death: one white flash, the vision falls back into him from both ends like a tide going out
        a = t - T_DEATH
        if 0 <= a < 0.6:
            fr += light(WHITE, 0.9 * np.exp(-a / 0.12))
        if 0 <= a < 3.0:
            r = reach * (1 - a / 3.0)
            fr += light(SILVER, 0.9 * np.exp(-((np.abs(d - p_sf) - r) / 70) ** 2) * (1 - a / 3.0))
            fr += light(SIEGFRIED, 0.6 * np.exp(-a / 0.7) * np.exp(-((d - p_sf) / 120) ** 2))
        for j, tb in enumerate(heart()):
            fr = ring(fr, S, t, tb, p_sf, BLOOD, 0.55 - 0.15 * j, speed=800, width=140, tau=0.7)

        # fate, twice
        for t0, dur, m, v, _, k in fate:
            fr = ring(fr, S, t, t0, p_sf, FATE_C, 0.95, speed=850, width=240, tau=1.5)

        # the torches gather close round the body and lift
        g = smoothstep(T_DEATH, D, t)
        tl = TORCHES[0] + (TORCHES[1] - TORCHES[0]) * g
        fr = torches(fr, S, T, tl, pull=p_sf, k=TORCHES[2] + (TORCHES[3] - TORCHES[2]) * g)

        # the people
        fr = figure(fr, S, p_gu, GUNTHER, GUNTHER_AT[2] - 0.05 * night)
        fr = figure(fr, S, p_sf, SIEGFRIED, ls, w=12 + 4 * smoothstep(CHORDS[0][0], CHORDS[-1][0], t)
                    * (1 - smoothstep(T_DEATH, T_DEATH + 2, t)))
        fr += light(HEAD, lh * np.exp(-((d - p_sf) / 6) ** 2))
        fr += light(GOLD, (0.6 - 0.2 * smoothstep(T_DEATH, T_DEATH + 3, t)) * np.exp(-((d - p_sf - 14) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes from the piano reduction, with his lines from the vocal score on the horn, his own instrument;
    nothing added but the last of his heartbeat and a gong as he dies."""
    pan_at = panner(G)
    o = Orchestra(M, level=2.85)
    sf = pan_at(at(G, *SIEG_AT))

    def role(t, d, m, v, h):
        if h == 0 and d < 0.4 and m >= 60:                  # the harp's arpeggios, with the violins' shimmer
            return [('harp', 0, 0, 0.6), ('violins', 0, -16, 0.25)]
        if d >= 0.4 and t < SEG[2]:                         # the held chords: strings and winds, soft
            return [('violins' if m >= 55 else 'cellos', 0, -10, 0.45), ('clarinets' if m >= 50 else 'bassoons', 0, -14, 0.35)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if SEG[2] <= t < SEG[3] else 0.5, role=role, pan=lambda t, m: sf * 0.5)
    for t, d, m in voice():                                 # his lines: horn, doubled by the cellos
        o.play('horns', m, t, max(d, 0.2), 104, sf, 0.9)
        o.play('cellos', m, t, max(d, 0.2), 90, sf, 0.4)
    for j, tb in enumerate(heart()):
        o.hit('timpani', tb, 78, pitch=-9, gain=0.3 - 0.08 * j, pan=sf)
    o.hit('cymbal swell', T_LOVE - 1.5, 90, gain=0.3, pan=sf)
    o.hit('gong', T_DEATH, 96, gain=0.45, pan=sf)
    o.effects([(0.0, -18), (D, -18)])
