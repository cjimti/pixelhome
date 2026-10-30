"""Neidhöhle: the deep forest at night outside Fafner's cave. The porch is the cave mouth, black with a smoulder far
inside; Left, Right and Side are the forest, deep teal under moonlight, with pale blue shafts of moon drifting
slowly through the trees.

The Act II prelude: the dragon's motif (Donington 57) crawls up out of the tubas and basses in its chromatic
climb, and every note of it heaves a dark ochre wave out of the cave mouth over the whole house, each bigger
than the last as the motif climbs. Between the phrases the timpani beat their two notes a tritone apart (F and
B), and each pair thumps the cave mouth red. The giants' motif (58) answers in the trombones with the porch
stamping in stone and ochre, and then the Curse (13) cuts across the house in a blood red slash from the cave
out to both ends. Over it the Ring (8) glints gold in the bassoons, the hoard asleep in the dark.

At the end Alberich, red in his muddy halo, creeps in from the free end of Right and settles at Right 0.3 to
keep watch on the cave, his own curse grumbling in the basses, while the forest breathes in the moonlight.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF11'
TITLE = 'Neidhöhle'
KIND = 'show'
DESCRIPTION = ("Night in the forest outside a dragon's cave. The dragon's music crawls out of the dark in great "
               'heaving waves, a curse slashes across the house, and a dwarf creeps up to keep watch.')
VOICEOVER = ('Deep in the forest there is a cave, and in the cave a dragon sleeps on a heap of gold. '
             'Someone is watching.')

K = 0                                       # this scene's place on Act II's shared clock: T = t + 80 K
BEAT = 0.5
T_DRAGON = [2.0, 15.0]                      # the dragon's motif crawling up from the bass
T_TIMP = [11.0, 12.6, 23.5, 25.1, 27.0]     # the timpani's tritone pairs
T_GIANTS = 30.0
T_CURSE = 40.0
T_RING = 47.0
T_ALB = 55.0                                # Alberich creeps in
T_CURSE2 = 64.0
D = 80.0

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
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, D, 'F1', 60, 'pedal')
    for k, t0 in enumerate(T_DRAGON):
        for t, m, v, d in play('fafner', t0, 0.55, 0, 88 + 12 * k):
            add(t, d, m, v, 'dragon', k)
    for i, t0 in enumerate(T_TIMP):
        add(t0, 0.5, 'F2', 104 + 4 * (i % 2), 'timp', 0)
        add(t0 + 0.55, 0.5, 'B1', 110, 'timp', 1)
    for t, m, v, d in play('giants', T_GIANTS, 0.6, 0, 108):
        add(t, d, m, v, 'giants')
    for t, m, v, d in play('curse', T_CURSE, 0.55, 0, 112):
        add(t, d, m, v, 'curse', 0)
    for t, m, v, d in play('ring', T_RING, 0.62, -12, 82):
        add(t, d, m, v, 'ring')
    for j in range(8):
        add(T_ALB + j * 1.1, 0.3, ('F2', 'Gb2')[j % 2], 64 + 3 * j, 'creep')
    for t, m, v, d in play('curse', T_CURSE2, 0.8, -12, 84):
        add(t, d, m, v, 'curse', 1)
    for m in ('F2', 'Ab2', 'C3'):
        add(T_CURSE2 + 6, D - T_CURSE2 - 6, m, 54, 'dark')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=11):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    dragon = [e for e in N if e[4] == 'dragon']
    timp = [e for e in N if e[4] == 'timp']
    giants = [e for e in N if e[4] == 'giants']
    ring = [e for e in N if e[4] == 'ring']
    gstep = np.array(sorted({e[0] for e in giants}))
    runs = ['Porch Left', 'Porch Front', 'Porch Right']
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Porch Left', 0.1), at(G, 'Porch Right', 0.9), len(ring))
    alb_from, alb_to = L + 30, at(G, 'Right', ALB_AT)
    lo, hi = note('Eb2'), note('Gb3')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_CURSE2, START[k]), (D, END[k])]) for k in START}
        heave = smoothstep(T_DRAGON[0], T_DRAGON[1] + 8, t) * (1 - smoothstep(T_GIANTS + 6, T_CURSE + 4, t))
        lv['cave'] += 0.35 * heave
        fr = forest(S, T, lv)

        # every note of the dragon's crawl: a dark ochre wave heaving out of the cave mouth, bigger as it climbs
        for t0, dur, m, v, part, k in dragon:
            a = t - t0
            if 0 <= a < 2.6:
                u = (m - lo) / (hi - lo)
                r = (400 + 1100 * u) * (1 - np.exp(-a / 0.7))
                g = (0.75 + 0.35 * u) * (0.8 + 0.2 * k) * np.exp(-a / 1.0)
                fr += light(SCALE, g * np.exp(-((np.abs(d - mid) - r) / (110 + 90 * u)) ** 2))
                fr += light(CAVE, 1.4 * g * S['mouth'] * np.exp(-a / 0.4))

        # the timpani's tritone: each stroke thumps the whole cave mouth red
        for t0, dur, m, v, part, k in timp:
            a = t - t0
            if 0 <= a < 0.8:
                fr += light(BLOOD, (0.7 + 0.25 * k) * np.exp(-a / 0.18) * S['mouth'])

        # the giants' motif: the porch runs stamp in stone and ochre, one run per step
        if T_GIANTS <= t < T_GIANTS + 10:
            j = int(np.searchsorted(gstep, t, side='right')) - 1
            if j >= 0:
                a = t - gstep[j]
                run = G.seg_of == runs[j % 3]
                fr += light(STONE, 0.75 * np.exp(-a / 0.35) * run)
                fr += light(SCALE, 0.5 * np.exp(-a / 0.6) * run)

        # the Curse: a blood red slash from the cave out to both ends of the house, held, then bleeding away
        if T_CURSE <= t < T_RING + 2:
            a = t - T_CURSE
            front = min(1.0, a / 1.4) * max(mid, L - mid)
            slash = smoothstep(front + 60, front - 60, np.abs(d - mid))
            fr += light(BLOOD, 0.95 * slash * np.exp(-max(a - 2.5, 0) / 2.0))
            fr += light(WHITE, 0.6 * np.exp(-((np.abs(d - mid) - front) / 25) ** 2) * (a < 1.6))

        # the Ring in the bassoons: gold glints in the cave, the hoard asleep
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.2:
                fr += light(GOLD, 0.95 * np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.06, a)
                            * np.exp(-((d - glint_at[j]) / (25 + 30 * a)) ** 2))

        # Alberich creeps in from the free end of Right, one step at a time, and keeps watch
        if t >= T_ALB:
            u = smoothstep(T_ALB, T_ALB + 8.8, t)
            step = 0.5 + 0.5 * np.cos(2 * np.pi * (t - T_ALB) / 1.1)
            p = alb_from + (alb_to - alb_from) * u
            lvl = keys(t, [(T_ALB, 0.0), (T_ALB + 1.0, 0.7), (T_CURSE2, 0.7), (T_CURSE2 + 1, 0.95), (T_CURSE2 + 6, 0.7)])
            fr += light(MUD, 0.6 * lvl * np.exp(-((d - p) / 70) ** 2))
            fr = figure(fr, S, p, ALBERICH, lvl * (0.85 + 0.15 * step * (u < 1)))
        if T_CURSE2 <= t < T_CURSE2 + 4:
            a = t - T_CURSE2
            fr += light(BLOOD, 0.95 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - alb_to) - 900 * a) / 140) ** 2))
            fr += light(BLOOD, 0.5 * np.exp(-a / 0.5) * S['mouth'])
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

    for name, gain, rev in (('low', 0.34, 0.25), ('brass', 0.3, 0.3), ('perc', 0.3, 0.3), ('winds', 0.26, 0.32),
                            ('dark', 0.24, 0.4)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    gong = M.hits('Percussion/gongHit_f.wav')

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

    cave = pan_at(at(G, 'Porch Front', 0.5))
    alb = pan_at(at(G, 'Right', ALB_AT))
    door = pan_at(at(G, 'Right', 0.95))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, cave, rise=3.0, fall=2.0, gain=0.45)
        elif part == 'dragon':
            M.add('low', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 0.95, cave)
            M.add('low', cb.play(m, v - 8, dur=d * 1.1, release=0.3), t, 0.7, cave)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-6 if k else -2), t, 0.95, cave)
        elif part == 'giants':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, cave)
            M.add('low', tuba.play(m - 12, v - 10, dur=d * 1.05, release=0.2), t, 0.7, cave)
            M.add('perc', timp.play(v - 10, pitch=-4), t, 0.6, cave)
        elif part == 'curse':
            if k == 0 and t == T_CURSE:
                M.add('perc', gong.play(110), t, 0.7, cave)
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, cave if k == 0 else alb, rise=0.15, fall=1.0, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, cave if k == 0 else alb)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.7, cave if k == 0 else alb)
        elif part == 'ring':
            if d > 1.2:
                hold('winds', bsn, m, t, t + d, v, cave, rise=0.3, fall=0.8, gain=0.8)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, cave)
        elif part == 'creep':
            M.add('low', cbs.play(m, v), t, 0.8, door + (alb - door) * min(1.0, (t - T_ALB) / 8.8))
        elif part == 'dark':
            hold('dark', vc, m, t, t + d, v, alb * 0.5, rise=4.0, fall=1.5, gain=0.55)
