"""Neidhöhle: the deep forest at night outside Fafner's cave. The porch is the cave mouth, black with a smoulder far
inside; Left, Right and Side are the forest, deep teal under moonlight, with pale blue shafts of moon drifting
slowly through the trees.

The music is Wagner's own: the prelude to Act II, its first bars (1 to 3) and then its long build and climax (bars
68 to 96), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the dragon's tremolo in the low strings and the tritone runs in the timpani
and basses, the giants' motif (Donington 58) in paired chords on trombones and horns, the Ring (8) unwinding on
clarinets and violas, the long crescendo on horns and trombones over the basses, and the Curse (13) hurled down
from the top of the orchestra in full brass. A production adds the night: a cold wind in the trees, a low groan
of the earth as the dragon turns over, a gong and a crash on the Curse, and Alberich's creeping footsteps.

Every note sets the lights. Under the opening tremolo the cave mouth smoulders. The long notes of the dragon's
music heave dark ochre waves out of the cave over the whole house, bigger as they climb; the giants' paired
chords stamp the porch runs in stone and ochre; the Ring glints gold in the cave; through the crescendo the cave
blazes hotter with every rising note, until the timpani's tritone runs thump the mouth red and the Curse cuts
across the house in a blood red slash from the cave out to both ends, each chord of its descent a fresh pulse.
At the end Alberich, red in his muddy halo, creeps in from the free end of Right and settles at Right 0.3 to keep
watch on the cave, while the forest breathes in the moonlight.

compose() tags every note of the excerpt; stage(), forest(), figure() and sparks() are the forest and the cave,
shared word for word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF11'
TITLE = 'Neidhöhle'
KIND = 'show'
DESCRIPTION = ("Night in the forest outside a dragon's cave. The dragon's music crawls out of the dark in great "
               'heaving waves, a curse slashes across the house, and a dwarf creeps up to keep watch.')
VOICEOVER = ('Deep in the forest there is a cave, and in the cave a dragon sleeps on a heap of gold. '
             'Someone is watching.')

K = 0                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 1-3 and 68-96, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_CALL = BAR[68]                            # the dragon's long notes over the tremolo
T_GIANTS = BAR[73]                          # the giants' paired chords
T_RING = BAR[81]                            # the Ring unwinds
T_CLIMB = BAR[86]                           # the crescendo
T_TIMP = BAR[91]                            # the tritone runs
T_CURSE = BAR[93]                           # the Curse, fortissimo
T_HUSH = BAR[96]                            # it sinks back into the dark
T_ALB = BAR[95] + 0.4                       # Alberich creeps in

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

START = dict(night=0.62, day=0.0, shafts=0.6, cave=0.35, eyes=0.0)
END = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)          # where SF12 picks the forest up
ALB_AT = 0.3                                # Alberich's watch, on Right


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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). 'rumble' is the low tremolo,
    'dragon' a long note of the dragon's music (k = which statement), 'giants' the paired chords, 'ring' the
    Ring's notes, 'climb' a rising note of the crescendo (k = its step), 'timp' the first note of a tritone run,
    'curse' a chord of the Curse's descent, 'hush' the closing bars."""
    N = []
    climb = 0
    last_run = -9.0
    for t, d, m, v, h in sorted(EX['notes']):
        if t < T_CALL:
            part, k = 'rumble', 0
        elif t < T_GIANTS:
            part, k = ('dragon', 0) if h == 0 and d >= 1.0 else ('rumble', 0)
        elif t < T_RING:
            part, k = ('giants', 0) if h == 0 else ('dragon', 1) if d >= 1.0 else ('rumble', 0)
        elif t < T_CLIMB:
            part, k = ('ring', 0) if h == 0 else ('rumble', 0)
        elif t < T_TIMP:
            if h == 0 and d >= 0.8:
                part, k, climb = 'climb', climb, climb + 1
            else:
                part, k = 'rumble', 0
        elif t < T_CURSE:
            if h == 1 and d < 0.2 and m < 50:
                part, k = ('timp', 0) if t - last_run > 1.0 else ('run', 0)
                last_run = t
            else:
                part, k = ('dragon', 2) if d >= 1.0 else ('rumble', 0)
        elif t < T_HUSH:
            part, k = ('curse', 0) if h == 0 else ('rumble', 0)
        else:
            part, k = 'hush', 0
        N.append((t, d, m, v, part, k))
    return N


def loudness(N, F):
    """How hard the orchestra is playing, frame by frame, 0..1 (velocity-weighted notes per second, smoothed)."""
    e = np.zeros(F)
    for t, d, m, v, part, k in N:
        f = int(t / DT)
        if 0 <= f < F:
            e[f] += (v / 127) ** 2
    w = np.exp(-np.arange(int(1.5 / DT)) / (0.5 / DT))
    e = np.convolve(e, w)[:F]
    return np.clip(e / (np.percentile(e, 98) + 1e-9), 0, 1)


def render(G, seed=11):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    loud = loudness(N, F)
    dragon = [e for e in N if e[4] == 'dragon']
    climb = [e for e in N if e[4] == 'climb']
    timp = [e for e in N if e[4] == 'timp']
    ring = [e for e in N if e[4] == 'ring']
    gstep = np.array(sorted({round(e[0], 2) for e in N if e[4] == 'giants'}))
    cstep = np.array(sorted({round(e[0], 2) for e in N if e[4] == 'curse'}))
    runs = ['Porch Left', 'Porch Front', 'Porch Right']
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Porch Left', 0.1), at(G, 'Porch Right', 0.9), len(ring))
    alb_from, alb_to = L + 30, at(G, 'Right', ALB_AT)
    lo, hi = 38, 66
    nclimb = max(1, len(climb))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_HUSH, START[k]), (D, END[k])]) for k in START}
        lv['cave'] += 0.45 * loud[f] + 0.5 * smoothstep(T_CLIMB, T_CURSE, t) * (1 - smoothstep(T_CURSE, T_HUSH, t))
        fr = forest(S, T, lv)

        # every long note of the dragon's music: a dark ochre wave heaving out of the cave mouth, bigger as it climbs
        for t0, dur, m, v, part, k in dragon:
            a = t - t0
            if 0 <= a < 3.0:
                u = np.clip((m - lo) / (hi - lo), 0, 1)
                r = (400 + 1100 * u) * (1 - np.exp(-a / 0.7))
                g = (0.75 + 0.35 * u) * (0.75 + 0.15 * k) * np.exp(-a / 1.1) * (v / 100)
                fr += light(SCALE, g * np.exp(-((np.abs(d - mid) - r) / (190 + 130 * u)) ** 2))
                fr += light(CAVE, 1.4 * g * S['mouth'] * np.exp(-a / 0.4))

        # the giants' paired chords: the porch runs stamp in stone and ochre, one run per chord
        if T_GIANTS <= t < T_RING:
            j = int(np.searchsorted(gstep, t, side='right')) - 1
            if j >= 0:
                a = t - gstep[j]
                run = G.seg_of == runs[j % 3]
                g = 1.0 - 0.55 * smoothstep(T_GIANTS, T_RING, t)
                fr += light(STONE, 0.8 * g * np.exp(-a / 0.35) * run)
                fr += light(SCALE, 0.55 * g * np.exp(-a / 0.6) * run)

        # the Ring unwinding: gold glints in the cave, the hoard asleep
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.2:
                fr += light(GOLD, 0.95 * (v / 100) * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.06, a)
                            * np.exp(-((d - glint_at[j]) / (25 + 30 * a)) ** 2))

        # the crescendo: every rising note a ring of fire pushing out of the cave, wider and hotter each time
        for t0, dur, m, v, part, k in climb:
            a = t - t0
            if 0 <= a < 2.4:
                s = 0.5 + 0.5 * k / nclimb
                r = (250 + 1300 * s) * (1 - np.exp(-a / 0.6))
                fr += light(SCALE, 1.3 * s * np.exp(-a / 1.0) * smoothstep(r + 200, r - 200, np.abs(d - mid)))
                fr += light(GOLD, 0.8 * s * np.exp(-a / 0.7) * np.exp(-((np.abs(d - mid) - r) / 90) ** 2))
                fr += light(WHITE, 0.4 * s * np.exp(-a / 0.15) * S['mouth'])

        # the timpani's tritone runs: each one thumps the whole cave mouth red and shakes the porch
        for t0, dur, m, v, part, k in timp:
            a = t - t0
            if 0 <= a < 1.2:
                fr += light(BLOOD, 0.95 * np.exp(-a / 0.25) * S['mouth'])
                fr += light(SCALE, 0.5 * np.exp(-a / 0.4) * S['porch'])

        # the Curse: a blood red slash from the cave out to both ends of the house, each chord a fresh pulse
        if T_CURSE <= t < T_HUSH + 3:
            a = t - T_CURSE
            front = min(1.0, a / 1.2) * max(mid, L - mid)
            slash = smoothstep(front + 60, front - 60, np.abs(d - mid))
            fr += light(BLOOD, 0.95 * slash * np.exp(-max(t - T_HUSH, 0) / 1.5))
            fr += light(WHITE, 0.7 * np.exp(-((np.abs(d - mid) - front) / 25) ** 2) * (a < 1.4))
            j = int(np.searchsorted(cstep, t, side='right')) - 1
            if j >= 0 and t < T_HUSH:
                b = t - cstep[j]
                fr += light(EYE, 0.6 * np.exp(-b / 0.3) * np.exp(-((np.abs(d - mid) - 600 * b) / 120) ** 2))

        # Alberich creeps in from the free end of Right, one step at a time, and keeps watch
        if t >= T_ALB:
            u = smoothstep(T_ALB, D - 1.0, t)
            step = 0.5 + 0.5 * np.cos(2 * np.pi * (t - T_ALB) / 0.9)
            p = alb_from + (alb_to - alb_from) * u
            lvl = keys(t, [(T_ALB, 0.0), (T_ALB + 1.0, 0.75), (D, 0.7)])
            fr += light(MUD, 0.6 * lvl * np.exp(-((d - p) / 70) ** 2))
            fr = figure(fr, S, p, ALBERICH, lvl * (0.85 + 0.15 * step * (u < 1)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, recoloured by what each part is, with the night around them."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    cave = pan_at(at(G, 'Porch Front', 0.5))
    L = G.pd.max()
    alb_from, alb_to = L + 30, at(G, 'Right', ALB_AT)
    o = Orchestra(M, level=2.1)
    parts = {(round(t, 4), m): (part, k) for t, d, m, v, part, k in compose()}

    def role(t, d, m, v, h):
        part, k = parts.get((round(t, 4), m), ('rumble', 0))
        if part == 'dragon':
            return [('tuba', 0, 6, 0.8), ('horns', 0, 0, 0.6), ('basses', -12 if m >= 40 else 0, -4, 0.5)]
        if part == 'giants':
            return [('trombones', 0, 4, 0.7), ('horns', 0, -4, 0.45)]
        if part == 'ring':
            return [('clarinets', 0, 0, 0.6), ('violas', 0, -10, 0.35)]
        if part == 'climb':
            return [('horns', 0, 6, 0.8), ('trombones', 0, 0, 0.6)] + ([('trumpets', 0, -12, 0.3)] if k > 4 else [])
        if part in ('timp', 'run'):
            return [('basses', 0, 4, 0.6), ('cellos', 12, -6, 0.4)]
        if part == 'curse':
            return [('trumpets', -12, 4, 0.55), ('trombones', -12, 0, 0.6), ('horns', -12, 0, 0.5),
                    ('violins', 0, -6, 0.4)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 0.5 + 0.5 * smoothstep(T_CLIMB, T_CURSE, t), role=role,
            pan=lambda t, m: cave * 0.6)
    for t, d, m, v, part, k in compose():
        if part == 'timp':
            o.hit('timpani', t, 110, pitch=-2, gain=0.7, pan=cave)
            o.hit('timpani', t + 0.5, 116, pitch=-6, gain=0.75, pan=cave)
    # the night leads at the start and through the crescendo and the Curse; it backs off under the dragon's music
    # and the Ring so their themes are clear, and comes back for Alberich's creeping steps
    o.effects([(0.0, 0), (T_CALL - 1.0, 0), (T_CALL + 0.5, -7), (T_RING, -9), (T_CLIMB - 1.0, -9), (T_CLIMB + 3.0, -3),
               (T_TIMP, 0), (T_HUSH, 0), (T_HUSH + 1.0, 2)])
    # the night around it: wind in the trees, the earth groaning as the dragon turns, the Curse struck, his steps
    o.wind(0.0, D, level=lambda tt: 0.25 + 0.2 * np.sin(tt / 7.0) ** 2, pan=-0.3, seed=11)
    o.thunder(T_TIMP, near=0.1, pan=cave, gain=0.7)
    o.thunder(BAR[92], near=0.15, pan=cave, gain=0.8)
    o.hit('gong', T_CURSE, 118, gain=0.7, pan=cave)
    o.hit('crash', T_CURSE, 120, gain=0.5, pan=cave)
    o.hit('cymbal swell', T_CURSE - 3.0, 100, gain=0.4, pan=cave)
    t = T_ALB
    while t < D - 1.0:
        u = smoothstep(T_ALB, D - 1.0, t)
        o.M.add('fx', o.hits['hoof soft'].play(48), t, 0.2, pan_at(alb_from + (alb_to - alb_from) * u))
        t += 0.9
