"""Alberich's Watch: night outside Fafner's cave. Alberich, red in his muddy halo, keeps watch at Right 0.3, and
his curse (Donington 13) mutters in the basses, each phrase a red pulse rolling out from him. Then the wind
rises: a rush of blue storm-light tears in at the free end of Right and races the whole length of the house past
him, out to the far end of Left, where it bursts in a blue-white flash. The Wanderer is there, at Left 0.7.

His motif (17) in the trombones and tubas: every chord rolls a wide blue wave out from him over the house.
Alberich answers with the curse, a red wave from Right, and where the two fronts meet over the cave mouth they
crack white. Alberich gloats over the Ring (8): gold glints flare in the cave, each one with a red throb from
him. The Wanderer answers with his spear (73), a pale steel streak that shoots down the front of the house to
the porch with a thump. They end in a stand-off: the left half of the house blue, the right half red, pulsing
in turn, and the forest dark between them.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF12'
TITLE = "Alberich's Watch"
KIND = 'show'
DESCRIPTION = ('A dwarf keeps watch outside the cave in the dark. A rush of blue storm-light brings the Wanderer, '
               'and blue and red fight for the house.')
VOICEOVER = ('Alberich is waiting for the dragon to die, so the gold can be his again. '
             'Then the wind brings an old enemy.')

K = 1                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_MUTTER = [1.5, 7.5]                       # Alberich's curse, low in the basses
T_WIND = 13.0                               # the storm-light rushes in
T_ARRIVE = 15.5                             # the Wanderer appears in a flash at Left 0.7
T_WANDER = [18.0, 30.0]                     # his motif, trombones and tubas
T_CURSE = [21.0, 33.0]                      # Alberich answers
T_RING = 42.0                               # Alberich gloats over the Ring
T_SPEAR = 52.0                              # the Wanderer's spear
T_STANDOFF = 60.0
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
WANDERER = hexc('#1a3cff')
WANDER_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF11 left the forest
END = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)         # where SF13 picks it up
ALB_AT = 0.3                                # Alberich's watch, on Right
WAN_AT = 0.7                                # the Wanderer, on Left


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

    add(0.0, D, 'F1', 58, 'pedal')
    for k, t0 in enumerate(T_MUTTER):
        for t, m, v, d in play('curse', t0, 0.75, -12, 76 + 6 * k):
            add(t, d, m, v, 'mutter', k)
    add(T_WIND - 0.8, 3.2, 'C1', 110, 'wind')
    add(T_ARRIVE, 0.1, 'C1', 118, 'arrive')
    for k, t0 in enumerate(T_WANDER):
        for t, m, v, d in play('wanderer', t0, 0.55, 0, 104 + 6 * k):
            add(t, d, m, v, 'wanderer', k)
    for k, t0 in enumerate(T_CURSE):
        for t, m, v, d in play('curse', t0, 0.5, 0, 106 + 6 * k):
            add(t, d, m, v, 'curse', k)
    for t, m, v, d in play('ring', T_RING, 0.6, -12, 92):
        add(t, d, m, v, 'ring')
    for t, m, v, d in play('spear', T_SPEAR, 0.42, -12, 112):
        add(t, d, m, v, 'spear')
    for k in range(4):
        add(T_STANDOFF + 4.5 * k, 2.0, ('F2', 'B1')[k % 2], 96 + 4 * (k % 2), 'stand', k % 2)
    for m in ('F2', 'Ab2', 'B2'):
        add(T_STANDOFF, D - T_STANDOFF, m, 56, 'dark')
    return sorted(N, key=lambda e: e[0])


def render(G, seed=12):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    p_alb, p_wan = at(G, 'Right', ALB_AT), at(G, 'Left', WAN_AT)
    mutter = sorted({e[0] for e in N if e[4] == 'mutter'})
    wan = np.array(sorted({e[0] for e in N if e[4] == 'wanderer'}))
    cur = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    ring = [e for e in N if e[4] == 'ring']
    spear_on = np.array(sorted({e[0] for e in N if e[4] == 'spear'}))
    glint_at = np.random.default_rng(seed).uniform(at(G, 'Porch Left', 0.2), at(G, 'Porch Right', 0.8), len(ring))
    gust = Flicker(np.random.default_rng(seed + 1), G.N, 2.0, 6.0)

    def wave(t0s, t, p, speed, width, life):
        """Fronts rolling out from p for each onset in t0s, -> perceptual."""
        w = np.zeros_like(d)
        for t0 in t0s[(t0s <= t) & (t0s > t - life * 3)]:
            a = t - t0
            w += np.exp(-a / life) * np.exp(-((np.abs(d - p) - speed * a) / width) ** 2)
        return w

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_STANDOFF, START[k]), (D, END[k])]) for k in START}
        fr = forest(S, T, lv)

        # Alberich's muttered curse: a red pulse rolling out from him on each note
        for t0 in mutter:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.75 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_alb) - 500 * a) / 90) ** 2))

        # the storm-light: a blue rush from the free end of Right the whole length of the house
        if T_WIND <= t < T_ARRIVE + 3:
            a = t - T_WIND
            front = L - L * smoothstep(0, T_ARRIVE - T_WIND, a)
            body = smoothstep(front - 40, front + 120, d) * smoothstep(L + 400, front, d)
            fade = 1 - smoothstep(T_ARRIVE, T_ARRIVE + 3, t)
            fr += light(WANDER_SOFT, 1.0 * fade * body * (0.8 + 0.2 * gust(T)))
            fr += light(WANDERER, 0.5 * fade * body)
            fr += light(SPEAR, 0.8 * fade * np.exp(-((d - front) / 40) ** 2))
        if T_ARRIVE <= t < T_ARRIVE + 1.5:
            a = t - T_ARRIVE
            fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * np.exp(-((d - p_wan) / 260) ** 2))
            fr += light(WANDERER, 0.6 * np.exp(-a / 0.5))

        # his chords: wide blue waves out from him; the curse: red waves out from Alberich; they crack white
        blue = wave(wan, t, p_wan, 600, 200, 1.0)
        red = wave(cur, t, p_alb, 650, 180, 0.9)
        fr += light(WANDERER, 0.95 * np.clip(blue, 0, 1.2))
        fr += light(BLOOD, 0.95 * np.clip(red, 0, 1.2))
        fr += light(WHITE, np.clip(blue * red * 4, 0, 1))

        # the Ring: gold flares in the cave, each with a red throb from Alberich
        for j, (t0, dur, m, v, part, k) in enumerate(ring):
            a = t - t0
            if 0 <= a < dur + 1.2:
                g = np.exp(-a / (dur + 0.5)) * smoothstep(0, 0.06, a)
                fr += light(GOLD, 0.95 * g * np.exp(-((d - glint_at[j]) / (25 + 30 * a)) ** 2))
                fr += light(ALBERICH, 0.4 * g * np.exp(-((d - p_alb) / 120) ** 2))

        # the spear: a pale steel streak down the front of the house to the porch, one surge per note
        if T_SPEAR <= t < T_STANDOFF:
            j = int(np.searchsorted(spear_on, t, side='right')) - 1
            a = t - spear_on[j]
            reach = p_wan + (mid - p_wan) * smoothstep(T_SPEAR, T_SPEAR + 3.0, t)
            shaft = (d >= p_wan) * (d <= reach) * 1.0
            fr += light(SPEAR, (0.55 + 0.4 * np.exp(-a / 0.2)) * shaft * (1 - smoothstep(T_STANDOFF - 2, T_STANDOFF, t)))
            fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * np.exp(-((d - reach) / 30) ** 2))

        # the stand-off: left half blue, right half red, pulsing in turn
        if t >= T_STANDOFF:
            u = smoothstep(T_STANDOFF, T_STANDOFF + 2, t)
            k = int((t - T_STANDOFF) / 4.5)
            a = (t - T_STANDOFF) % 4.5
            beat = np.exp(-a / 0.8)
            side = smoothstep(mid + 200, mid - 200, d)
            lb = 0.5 + (0.5 * beat if k % 2 == 0 else 0.0)
            lr = 0.5 + (0.5 * beat if k % 2 == 1 else 0.0)
            fade = 1 - smoothstep(D - 6, D, t)
            fr += light(WANDERER, u * fade * lb * side * np.exp(-((d - p_wan) / 900) ** 2))
            fr += light(BLOOD, u * fade * lr * (1 - side) * np.exp(-((d - p_alb) / 900) ** 2))

        # Alberich, and the Wanderer from his arrival
        alvl = keys(t, [(0, 0.7), (T_WIND, 0.7), (T_WIND + 1, 0.45), (T_ARRIVE + 2, 0.7)])
        for t0 in cur:
            if 0 <= t - t0 < 0.6:
                alvl += 0.3 * np.exp(-(t - t0) / 0.2)
        fr += light(MUD, 0.6 * alvl * np.exp(-((d - p_alb) / 70) ** 2))
        fr = figure(fr, S, p_alb, ALBERICH, min(alvl, 1.0))
        if t >= T_ARRIVE:
            wl = keys(t, [(T_ARRIVE, 1.0), (T_ARRIVE + 2, 0.8)])
            for t0 in wan:
                if 0 <= t - t0 < 0.6:
                    wl += 0.2 * np.exp(-(t - t0) / 0.25)
            fr = figure(fr, S, p_wan, WANDERER, min(wl, 1.0), 18.0)
            fr += light(SPEAR, 0.5 * min(wl, 1.0) * np.exp(-((d - p_wan - 22) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.31, 0.25), ('brass', 0.28, 0.3), ('perc', 0.28, 0.3), ('winds', 0.24, 0.32),
                            ('dark', 0.22, 0.4), ('fx', 0.13, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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

    alb = pan_at(at(G, 'Right', ALB_AT))
    wan = pan_at(at(G, 'Left', WAN_AT))
    cave = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, cave, rise=3.0, fall=2.0, gain=0.45)
        elif part == 'mutter':
            M.add('low', vc.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, alb)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.6, alb)
        elif part == 'wind':
            M.add('fx', whoosh(d, 400, 4500, 0.8, seed=12), t, 1.0, 0.6)
            M.add('fx', whoosh(d, 3000, 300, 0.6, seed=13), t + 0.6, 1.0, -0.6)
            M.add('perc', roll.play(v, dur=d), t, 0.7, 0.0)
        elif part == 'arrive':
            M.add('perc', crash.play(v), t, 0.9, wan)
            M.add('perc', timp.play(v, pitch=-5), t, 0.9, wan)
        elif part == 'wanderer':
            if m < note('C3'):
                M.add('low', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 0.85, wan)
            elif m < note('C4'):
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.8, wan)
            else:
                M.add('brass', horn.play(m - 12, v - 6, dur=d * 1.05, release=0.3), t, 0.7, wan)
        elif part == 'curse':
            if d > 1.2:
                hold('brass', tbn, m, t, t + d, v, alb, rise=0.15, fall=1.0, gain=0.85)
            else:
                M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, alb)
            M.add('low', cbs.play(m - 12, v - 10), t, 0.7, alb)
        elif part == 'ring':
            if d > 1.2:
                hold('winds', bsn, m, t, t + d, v, cave, rise=0.3, fall=0.8, gain=0.8)
            else:
                M.add('winds', bsn.play(m, v, dur=d * 1.05, release=0.25), t, 0.9, cave)
        elif part == 'spear':
            M.add('low', tbn.play(m, v, dur=d * 1.05, release=0.2), t, 0.9, wan)
            M.add('low', tuba.play(m - 12, v - 12, dur=d * 1.05, release=0.2), t, 0.6, wan)
        elif part == 'stand':
            M.add('perc', timp.play(v, pitch=-2 if k == 0 else -6), t, 0.9, wan if k == 0 else alb)
        elif part == 'dark':
            hold('dark', vc, m, t, t + d, v, 0.0, rise=4.0, fall=1.5, gain=0.5)
    M.add('perc', timp.play(120, pitch=-3), T_SPEAR + 3.0, 0.9, cave)
