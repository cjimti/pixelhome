"""The Tarnhelm: in the red-orange caverns of Nibelheim, Alberich (red) still has Mime (sickly yellow-green) by the
ear on Porch Front. He shakes him three times for the helmet he made him forge; Mime whimpers and lets it drop,
and a little violet-grey glint lies between them. Alberich picks it up and the Tarnhelm motif (Donington 18)
sounds on muted horns, soft and strange, while a dark violet shimmer spreads from the helmet over the porch and
out along the wings, swelling with each of its slow chords.

He puts it on and is gone: where he stood there is only a hole in the glow of the caverns, darker than anything
round it, with a faint violet shimmer at its edges. The hole goes for Mime. Every crack of the invisible whip
(a slapstick and a swish) lands as a stinging red flash on Mime and a red slash across the gap, and Mime yelps
on the xylophone and piccolo and scrambles away down Porch Front and up Porch Left until he drops. Then the
hole goes off to drive the Nibelungs: the Nibelung rhythm starts up again with six anvils, and the hole races
out along Left, back across the whole house to the far end of Right, and back to Porch Right, and the forges it
passes flare up with sparks behind it.

When it is quiet, Wotan (blue) and Loge (fire) come down into the middle of Porch Front with a puff of vapour,
to a soft Valhalla in the tubas and Loge's flicker in the piccolo. They find Mime moaning on Porch Left, his
light sagging with each bassoon sigh. Loge goes over to him. At the end the Tarnhelm's last chords sound again
and the hole on Porch Right fills back in with red: Alberich is back, and the rhythm stirs.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.leitmotifs import play

CODE = 'RG14'
TITLE = 'The Tarnhelm'
KIND = 'show'
DESCRIPTION = ('Alberich takes the helmet his brother Mime was made to forge, and when he puts it on, he vanishes. '
               'Unseen, he whips Mime and drives his workers back to their anvils, just as Wotan and Loge arrive.')
VOICEOVER = ('Mime has made his brother a helmet, and it does something no helmet should. '
             'Put it on, and you disappear.')

NB = 0.6                                    # a dotted quarter of the Nibelung 9/8
BAR = 3 * NB
RHY = (0.0, 0.5, 2 / 3)                     # long-short-long in each beat
TB = 0.45                                   # a quarter note of the Tarnhelm motif
SHAKES = [1.0, 2.6, 4.2]                    # Alberich shakes Mime for the helmet
T_DROP = 7.0                                # Mime lets it fall
T_TAKE = 8.4                                # Alberich picks it up
T_TARN = 9.0                                # the Tarnhelm motif
T_ON = 21.6                                 # he puts it on
T_GONE = 23.4
WHIPS = [25.0, 26.3, 27.4, 28.8, 30.0, 31.4, 32.5, 34.0, 35.2, 36.6]
T_WORK = 38.4                               # the Nibelung rhythm again
WBARS = 9
T_QUIET = T_WORK + WBARS * BAR
T_GODS = 58.0                               # Wotan and Loge come down
T_LOGE = 60.6
MOANS = [63.0, 65.4, 67.8]
T_BACK = 72.0                               # Alberich visible again
D = 80.0

FIGURE = [('Bb3', 'A3', 'Bb3'), ('Db4', 'C4', 'Db4'), ('F4', 'E4', 'F4'),
          ('Gb4', 'F4', 'Eb4'), ('Db4', 'C4', 'Bb3'), ('C4', 'A3', 'F3')]
NANV = 6

EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
SPARK = hexc('#ff7a10')
HOT = hexc('#fff0a0')
TARN = hexc('#5a4a8a')
TARN_HI = hexc('#9a88d0')
ALB = hexc('#ff1000')
RED = hexc('#ff1800')
MUD = hexc('#5a1200')
MIME = hexc('#b0d020')
WOTAN = hexc('#1a3cff')
LOGE_A = hexc('#ff5000')
LOGE_B = hexc('#ffb020')
VAPOUR = hexc('#8a6a1c')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_TARN + 1.0, 'Bb1', 80, 'trem')
    for i, ts in enumerate(SHAKES):                         # "Hehe! Hehe! Hierher!" and a shake each time
        for j, m in enumerate(('Bb2', 'Bb2', 'Db3', 'F3')[: 3 + (i == 2)]):
            add(ts - 0.6 + j * 0.15, 0.14, note(m) + i, 100, 'alb')
        add(ts, 0.3, 'Bb1', 100 + 6 * i, 'shake')
        for j in range(3):
            add(ts + 0.25 + j * 0.13, 0.1, note('A5') - j + i, 92, 'yelp')
        add(ts + 0.75, 0.4, note('E4') - i, 78, 'whine')
    add(T_DROP, 0.5, 'E6', 90, 'clink')
    add(T_DROP + 0.25, 0.5, 'B5', 70, 'clink')
    for t, m, v, d in play('tarnhelm', T_TARN, TB, 0, 70):
        add(t, d, m, v, 'tarn')
    for m in ('B5', 'Eb6'):
        add(T_TARN, T_ON - T_TARN + 1.0, m, 44, 'mist')
    add(T_ON, T_GONE - T_ON, 'Ab3', 80, 'vanish')
    for t, m, v, d in play('tarnhelm', T_ON + 0.4, TB * 0.8, 0, 64):
        if t < T_ON + 0.4 + 8 * TB * 0.8:
            add(t, d, m, v, 'tarn')

    add(WHIPS[0] - 1.0, T_WORK - WHIPS[0] + 1.0, 'Bb1', 96, 'agit')
    for i, tw in enumerate(WHIPS):                          # the invisible whip; Mime yelps
        add(tw, 0.2, 'C4', 110 + 4 * (i % 3 == 0), 'whip')
        top = note('C6') - (i % 4)
        for j in range(4):
            add(tw + 0.08 + j * 0.055, 0.08, top - 3 * j, 110 - 5 * j, 'squeal')
        add(tw + 0.08, 0.45, top - 12, 96, 'yelp')
        if i % 3 == 1:
            for j, m in enumerate(('F3', 'F3', 'Bb3')):
                add(tw + 0.5 + j * 0.13, 0.12, m, 88, 'cackle')

    for bar in range(WBARS):                                # driving them back to work
        t0 = T_WORK + bar * BAR
        grow = min(1.0, (bar + 2) / 5) * (1 - smoothstep(WBARS - 3, WBARS, bar))
        if bar % 2 == 0:
            add(t0, BAR * 2, 'Bb1', int(84 + 26 * grow), 'pedal')
        for b in range(3):
            fig = FIGURE[(bar % 2) * 3 + b]
            for k, off in enumerate(RHY):
                t = t0 + (b + off) * NB
                acc = b == 0 and k == 0
                dd = NB * (0.45, 0.15, 0.3)[k]
                add(t, dd, 'Bb2' if k != 1 else 'F2', int(72 + 34 * grow) + 8 * acc, 'pluck')
                add(t, dd, fig[k], int(60 + 46 * grow) + 8 * acc, 'nib', b)
                if 2 <= bar <= 6:
                    add(t, dd, note(fig[k]) - 12, int(70 + 30 * grow), 'brassnib', b)
                for a in range(NANV if 1 <= bar <= 7 else 0):
                    add(t, 0.1, 'C4', int(82 + 20 * grow) + 8 * acc, 'anvil', a)
        if 2 <= bar <= 6:
            add(t0, 0.3, 'Bb1', 104, 'timp')

    add(T_GODS - 0.2, 4.0, 'F1', 72, 'puff')
    for t, m, v, d in play('valhalla', T_GODS + 0.3, 0.6, 0, 78):
        add(t, d, m, v, 'valhalla')
    for t, m, v, d in play('loge_flicker', T_LOGE, 0.18, 0, 92):
        add(t, d, m, v, 'loge')
    for t, m, v, d in play('loge', T_LOGE + 1.0, 0.4, 12, 74):
        add(t, d, m, v, 'logefire')
    add(MOANS[0] - 0.5, D - MOANS[0] + 0.5, 'Bb1', 74, 'trem')
    for i, tm in enumerate(MOANS):                          # Mime moaning: "Ohe! Ohe! Au! Au!"
        for j, m in enumerate(('Bb3', 'A3', 'Ab3', 'G3', 'Gb3')[: 3 + (i % 2) * 2]):
            add(tm + j * 0.42, 0.5, note(m) - i, 86 - 4 * j, 'moan')
        add(tm + 0.1, 1.6, note('Db3') - i, 60, 'moanlow')
    add(MOANS[1] + 1.2, 0.3, 'D5', 82, 'loge')
    add(MOANS[1] + 1.4, 0.3, 'F4', 78, 'loge')
    for t, m, v, d in play('tarnhelm', T_BACK - 16 * TB * 0.8, TB * 0.8, 0, 68):
        if t >= T_BACK - 0.01:
            add(t, d, m, v, 'tarn')
    add(T_BACK + 2.6, 0.5, 'Bb1', 108, 'appear')
    for bar in range(3):                                    # the rhythm stirs
        t0 = T_BACK + 3.2 + bar * BAR
        for b in range(3):
            for k, off in enumerate(RHY):
                add(t0 + (b + off) * NB, NB * (0.45, 0.15, 0.3)[k], 'Bb2' if k != 1 else 'F2', 76 + 8 * bar, 'pluck')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: Alberich (or the hole where he is), Mime, Wotan, Loge (path distance); the helmet; anvils."""
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    A0, M0 = at(G, 'Porch Front', 0.6), at(G, 'Porch Front', 0.6) + 57.0
    helm = 0.5 * (A0 + M0) + 8
    tgt = np.zeros((4, F))
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_(0, 0, D, A0, 6.0)
    set_(1, 0, D, M0, 6.0)
    for ts in SHAKES:                                       # shaken: Mime yanked to and fro
        set_(1, ts, ts + 0.12, M0 - 22, 30.0)
        set_(1, ts + 0.12, ts + 0.24, M0 + 14, 30.0)
        set_(1, ts + 0.24, ts + 0.5, M0, 12.0)
    set_(1, T_DROP, T_ON, M0 + 30, 4.0)                    # he lets go; Mime backs off
    set_(0, T_TAKE, T_ON, helm, 3.0)
    # the hole whips Mime down Porch Front and up Porch Left
    flee = np.linspace(M0 + 30, at(G, 'Porch Left', 0.4), len(WHIPS) + 1)
    for i, tw in enumerate(WHIPS):
        nxt = WHIPS[i + 1] if i + 1 < len(WHIPS) else T_WORK
        set_(1, tw + 0.05, nxt, flee[i + 1], 9.0)
        set_(0, tw - 0.5, nxt, flee[i + 1] + (70 if i % 2 else 110), 7.0)
    set_(1, T_WORK, D, at(G, 'Porch Left', 0.4), 4.0)
    # off to drive the Nibelungs: out along Left, back across to the end of Right, back to Porch Right
    route = [(T_WORK, at(G, 'Porch Left', 0.4) - 60), (T_WORK + 4.0, at(G, 'Side', 0.35)),
             (T_WORK + 12.5, at(G, 'Right', 0.92)), (T_QUIET + 1.0, at(G, 'Porch Right', 0.55))]
    m = (t >= T_WORK) & (t < D)
    tgt[0][m] = np.interp(t[m], [r[0] for r in route], [r[1] for r in route])
    rate[0][m] = 6.0
    # Wotan and Loge come down into the middle of Porch Front; Loge goes over toward Mime
    far = -400.0
    set_(2, 0, T_GODS, pf - 10, 3.0)
    set_(3, 0, T_GODS, pf + 10, 3.0)
    set_(2, T_GODS, T_GODS + 1.5, pf - 10, 3.0)
    set_(3, T_GODS, T_LOGE, pf + 10 + 15 * np.sin(2 * np.pi * t / 0.9), 3.0)
    set_(2, T_GODS + 1.5, D, at(G, 'Porch Front', 0.35), 0.9)
    set_(3, T_LOGE, MOANS[1], at(G, 'Porch Front', 0.4) + 25 * np.sin(2 * np.pi * t / 1.3), 2.0)
    set_(3, MOANS[1], D, at(G, 'Porch Front', 0.2) + 10 * np.sin(2 * np.pi * t / 1.1), 1.4)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    anv = np.array([at(G, s, u) for s, u in (('Left', 0.3), ('Porch Left', 0.7), ('Porch Front', 0.15),
                                               ('Porch Right', 0.6), ('Right', 0.35), ('Right', 0.8))])
    return dict(t=t, apos=pos[0], mpos=pos[1], wpos=pos[2], lpos=pos[3], helm=helm, anvil=anv, far=far)


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    fl = Flicker(rng, G.N, 4.0, 11.0)
    cave = 0.5 + 0.5 * smooth_noise(rng, d, 160)
    pockets = rng.uniform(80, L - 80, 13)
    pw = rng.uniform(35, 90, 13)
    pocket = np.exp(-((d[:, None] - pockets[None, :]) / pw[None, :]) ** 2)
    pf_rate = rng.uniform(0.3, 0.9, 13)
    mist = 0.5 + 0.5 * smooth_noise(rng, d, 90)

    shakes, whips, moans = np.array(SHAKES), np.array(WHIPS), np.array(MOANS)
    tarn = np.array([e[0] for e in N if e[4] == 'tarn'])
    loge = np.array([e[0] for e in N if e[4] in ('loge', 'logefire')])
    hits = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    hit_t = np.array([h[0] for h in hits])
    hit_a = np.array([h[1] for h in hits])
    # forges flare behind the hole as it passes: when the hole last passed each pixel
    passed = np.full(G.N, -99.0)

    # sparks from the anvils, and a shower wherever the hole goes past while they work
    births, p0, vel, life = [], [], [], []
    for th, a, v in hits:
        births += [th] * 4
        p0 += [C['anvil'][a]] * 4
        vel += list(rng.choice([-1, 1], 4) * rng.uniform(80, 380, 4))
        life += list(rng.uniform(0.35, 0.8, 4))
    for tt in np.arange(T_WORK, T_QUIET, 0.05):
        births += [tt] * 2
        p0 += [float(np.interp(tt, C['t'], C['apos']))] * 2
        vel += list(rng.uniform(-300, 300, 2))
        life += list(rng.uniform(0.4, 0.9, 2))
    o = np.argsort(births)
    births, p0, vel, life = (np.array(a)[o] for a in (births, p0, vel, life))

    def intensity(t):
        return keys(t, [(0, 0.44), (T_TARN, 0.38), (T_GONE, 0.4), (T_WORK, 0.44), (T_WORK + 3 * BAR, 0.62),
                        (T_QUIET - 2 * BAR, 0.6), (T_QUIET + 1.5, 0.44), (D, 0.44)])

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        I = intensity(t)
        ap, mp, wp, lp = C['apos'][f], C['mpos'][f], C['wpos'][f], C['lpos'][f]
        vis = 1 - smoothstep(T_ON + 0.4, T_GONE, t) + smoothstep(T_BACK + 1.0, T_BACK + 2.8, t)
        hole = smoothstep(T_ON + 0.8, T_GONE, t) * (1 - smoothstep(T_BACK + 1.0, T_BACK + 2.8, t))
        if hole > 0:
            passed[np.abs(d - ap) < 40] = t

        # the caverns, with the forges flaring where the hole has just driven past
        bed = light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
        pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
        drive = np.exp(-np.clip(t - passed, 0, None) / 1.2) * (T_WORK - 1 < t < T_QUIET + 1)
        bed += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)) + 0.55 * drive * (0.6 + 0.4 * cave))
        if T_WORK <= t < T_QUIET:
            bi = int((t - T_WORK) / BAR)
            age = t - T_WORK - bi * BAR
            if 2 <= bi <= 6:
                bed += light(FORGE, 0.3 * np.exp(-age / 0.2) * (0.5 + 0.5 * cave))

        # the Tarnhelm's shimmer: spreading from the helmet while its motif sounds
        sh = smoothstep(T_TARN - 0.5, T_TARN + 3, t) * (1 - smoothstep(T_ON + 0.5, T_GONE + 1.5, t))
        sh += 0.6 * smoothstep(T_BACK - 0.3, T_BACK + 1.0, t) * (1 - smoothstep(T_BACK + 2.5, T_BACK + 5.0, t))
        if sh > 0:
            ti = int(np.searchsorted(tarn, t, side='right')) - 1
            pulse = np.exp(-(t - tarn[ti]) / 0.8) if ti >= 0 and t - tarn[ti] < 3 else 0.0
            src = C['helm'] if t < T_BACK - 1 else ap
            reach = 120 + 900 * smoothstep(T_TARN, T_ON, t) if t < T_BACK - 1 else 300.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - src) / 150 - 0.25 * t) + 4 * mist)
            env = smoothstep(reach, reach - 250, np.abs(d - src))
            amt = sh * env * (0.22 + 0.18 * wave + 0.15 * pulse)
            bed = bed * (1 - 0.5 * (sh * env)[:, None]) + light(TARN, amt)
            bed += light(TARN_HI, sh * env * 0.3 * (wave ** 6) * (0.5 + 0.5 * tw(t)))
        # the hole: darkness where Alberich is, a faint violet shimmer at its edges
        if hole > 0:
            r = np.abs(d - ap)
            dark = hole * np.exp(-(r / 46) ** 4)
            bed = bed * (1 - 0.94 * dark)[:, None]
            edge = hole * np.exp(-((r - 52) / 10) ** 2)
            bed += light(TARN_HI, 0.4 * edge * (0.6 + 0.4 * tw(t)))
        fr += bed

        # anvil strokes and sparks
        lo, hi = np.searchsorted(hit_t, t - 0.25), np.searchsorted(hit_t, t, side='right')
        if hi > lo:
            ages = t - hit_t[lo:hi]
            g = (np.exp(-((d[:, None] - C['anvil'][hit_a[lo:hi]][None, :]) / 13) ** 2)
                 * np.exp(-ages / 0.07)[None, :]).max(axis=1)
            fr += light(HOT, 0.9 * g)
        lo, hi = np.searchsorted(births, t - 0.95), np.searchsorted(births, t, side='right')
        if hi > lo:
            age = t - births[lo:hi]
            alive = age < life[lo:hi]
            if alive.any():
                age = age[alive]
                q = p0[lo:hi][alive] + vel[lo:hi][alive] * 0.35 * (1 - np.exp(-age / 0.35))
                heat = np.clip(1 - age / life[lo:hi][alive], 0, 1)
                g = np.exp(-((d[:, None] - q[None, :]) / 7) ** 2)
                fr += light(SPARK, (g * heat[None, :]).max(axis=1)) + light(HOT, 0.6 * (g * (heat ** 3)[None, :]).max(axis=1))
        sp = rng.random(G.N) < 0.006 * (0.5 + I)
        fr += light(SPARK, 0.65 * sp)

        # the helmet on the ground, then in his hands
        if T_DROP <= t < T_ON + 1.0:
            hp = C['helm'] if t < T_TAKE else ap
            g = smoothstep(T_DROP, T_DROP + 0.3, t) * (1 - smoothstep(T_ON, T_ON + 1.0, t))
            fr += light(TARN_HI, 0.85 * g * np.exp(-((d - hp) / 9) ** 2) * (0.75 + 0.25 * tw(t)))

        # Alberich (while he can be seen)
        if vis > 0:
            si = int(np.searchsorted(shakes, t, side='right')) - 1
            jolt = np.exp(-(t - shakes[si]) / 0.25) if si >= 0 and t - shakes[si] < 1.5 else 0.0
            pop = np.exp(-max(t - T_BACK - 2.6, 0) / 0.4) * (t > T_BACK + 2.6)
            fr += light(MUD, vis * 0.38 * np.exp(-((d - ap) / 120) ** 2))
            fr += light(ALB, vis * (0.78 + 0.22 * jolt + 0.3 * pop) * np.exp(-((d - ap) / (24 + 8 * jolt + 20 * pop)) ** 2)
                        * (1 + 0.15 * smoulder(t)))
            if t < T_DROP:
                fr += light(ALB, 0.3 * ((d > ap) & (d < mp)))

        # Mime: yelping at every shake and lash, sagging with every moan
        wi = int(np.searchsorted(whips, t, side='right')) - 1
        lash = np.exp(-(t - whips[wi]) / 0.18) if wi >= 0 and t - whips[wi] < 1.2 else 0.0
        si = int(np.searchsorted(shakes, t, side='right')) - 1
        yelp = np.exp(-(t - shakes[si] - 0.25) / 0.3) if si >= 0 and 0 <= t - shakes[si] - 0.25 < 1.5 else 0.0
        mi = int(np.searchsorted(moans, t, side='right')) - 1
        moan = np.exp(-(t - moans[mi]) / 1.2) if mi >= 0 and t - moans[mi] < 3 else 0.0
        mb = 0.7 + 0.3 * max(yelp, lash) - (0.2 * smoothstep(T_WORK, T_WORK + 2, t)) * (1 - moan) + 0.15 * moan
        body = np.exp(-((d - mp) / (15 + 6 * yelp + 4 * moan)) ** 2)
        fr += light(MIME, mb * body + 0.22 * np.exp(-((d - mp) / 60) ** 2))
        fr += light(WHITE, 0.5 * yelp * body * (tw(t) > 0))
        if lash > 0:
            fr += light(RED, 1.0 * lash * np.exp(-((d - mp) / 22) ** 2))
            a0, a1 = sorted((ap, mp))
            fr += light(RED, 0.75 * lash * ((d > a0) & (d < a1)))

        # Wotan and Loge, coming down with a puff of vapour
        if t >= T_GODS - 0.3:
            arr = smoothstep(T_GODS - 0.3, T_GODS + 1.2, t)
            if t < T_GODS + 3.5:
                pu = np.exp(-(t - T_GODS) / 1.0) * smoothstep(T_GODS - 0.3, T_GODS, t)
                fr += light(VAPOUR, 0.6 * pu * np.exp(-(np.abs(d - pf) / (40 + 120 * (t - T_GODS + 0.3))) ** 2))
            fr += light(WOTAN, arr * 0.85 * np.exp(-((d - wp) / 22) ** 2) + arr * 0.25 * np.exp(-((d - wp) / 80) ** 2))
            li = int(np.searchsorted(loge, t, side='right')) - 1
            lf = np.exp(-(t - loge[li]) / 0.15) if li >= 0 and t - loge[li] < 1 else 0.0
            lc = LOGE_A + (LOGE_B - LOGE_A) * (0.5 + 0.5 * fl(t))[:, None]
            ls = arr * ((0.7 + 0.3 * lf) * np.exp(-((d - lp) / (18 + 8 * lf)) ** 2) * (0.75 + 0.25 * fl(t))
                        + 0.25 * np.exp(-((d - lp) / 60) ** 2))
            fr += perc(ls)[:, None] * lc
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    apan = [pan_at(p) for p in C['anvil']]

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    for name, gain, rev in (('strings', 0.17, 0.3), ('low', 0.22, 0.15), ('brass', 0.2, 0.35), ('winds', 0.17, 0.3),
                            ('anvil', 0.08, 0.2), ('perc', 0.2, 0.25), ('fx', 0.12, 0.3), ('mime', 0.2, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vcp = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    bst = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    hst = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tbst = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    obs = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    anvil = M.hits('Percussion/Anvil_Hit*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    gong = M.hits('Percussion/gongscrape_pp.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Short*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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

    jit = np.random.default_rng(6)
    for t, d, m, v, part, who in compose():
        if part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.55)
            hold('low', cb, m, t, t + d, v - 10, 0.0, rise=1.0, fall=1.5, gain=0.45)
        elif part == 'alb':
            p = pan_of('apos', t)
            M.add('low', bsus.play(m, v, dur=d, release=0.1), t, 0.9, p)
            M.add('low', tbst.play(m + 12, v - 18), t, 0.45, p)
        elif part == 'shake':
            p = pan_of('mpos', t)
            M.add('perc', timp.play(v, pitch=-5), t, 0.7, p)
            M.add('low', pizz.play(m + 12, v), t, 0.9, p)
        elif part in ('yelp',):
            M.add('mime', ob.play(m - 12 if m > note('C5') else m, v), t, 0.8, pan_of('mpos', t))
            if m > note('C5'):
                M.add('mime', xylo.play(m - 12, v), t, 0.7, pan_of('mpos', t))
        elif part == 'whine':
            M.add('mime', bst.play(m - 12, v), t, 0.8, pan_of('mpos', t))
        elif part == 'clink':
            M.add('mime', glock.play(m, v), t, 0.8, pan_at(C['helm']))
        elif part == 'tarn':
            M.add('brass', mute.play(m, v, dur=d * 1.02, release=0.8), t, 0.75, pf + 0.1 * np.sign(m - 60))
        elif part == 'mist':
            hold('strings', vtrem, m - 12, t, t + d, v, 0.0, rise=3.0, fall=1.5, gain=0.4)
        elif part == 'vanish':
            gl = [x for x in range(note('Ab4'), note('Eb6') + 1) if x % 12 in (8, 11, 3)]
            for i, x in enumerate(reversed(gl)):
                M.add('strings', harp.play(x, 80), t + i * 1.4 / len(gl), 0.9, pan_of('apos', t))
            M.add('fx', whoosh(1.4, 3000, 400, 0.35, seed=3), t, 0.7, pan_of('apos', t))
            M.add('perc', gong.play(80), t, 0.6, pan_of('apos', t))
        elif part == 'agit':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=0.5, fall=1.0, gain=0.7)
            hold('strings', vtrem, note('F3'), t, t + d, v - 14, 0.0, rise=1.5, fall=1.0, gain=0.4)
        elif part == 'whip':
            p = pan_of('mpos', t)
            M.add('fx', whoosh(0.3, 900, 5000, 0.5, seed=int(t * 10)), t - 0.26, 0.7, pan_of('apos', t))
            M.add('perc', slap.play(v), t, 0.9, p)
        elif part == 'squeal':
            p = pan_of('mpos', t)
            M.add('mime', xylo.play(m - 12, v), t, 0.8, p)
            M.add('mime', pic.play(m, v - 18), t, 0.4, p)
        elif part == 'cackle':
            M.add('low', bst.play(m - 12, v), t, 0.8, pan_of('apos', t))
        elif part == 'pedal':
            M.add('low', pizz.play(m + 12, v), t, 1.0, 0.0)
            hold('low', cb, m, t, t + d, max(40, v - 40), 0.0, rise=0.3, fall=0.4, gain=0.45)
        elif part == 'pluck':
            M.add('low', pizz.play(m, v), t, 0.7, -0.15)
            M.add('strings', vcp.play(m, v - 10), t, 0.5, 0.15)
        elif part == 'nib':
            M.add('winds', bst.play(m - 12, v), t, 0.8, pan_of('apos', t) * 0.5 - 0.15)
            M.add('strings', vas.play(m, v - 6, dur=d, release=0.05), t, 0.5, 0.25)
        elif part == 'brassnib':
            M.add('brass', (hst if m >= note('F3') else tbst).play(m + 12, v), t, 0.5, -0.1)
            M.add('brass', tbst.play(m, v - 8), t, 0.45, 0.1)
        elif part == 'anvil':
            M.add('anvil', anvil.play(v, pitch=(-4, 0, 3)[who % 3]), t + jit.uniform(0, 0.012), 1.0, apan[who])
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, pf)
        elif part == 'puff':
            M.add('perc', swell.play(90), t - 1.2, 0.6, pf)
            M.add('fx', whoosh(1.2, 2500, 300, 0.4, seed=11), t, 0.6, pf)
            hold('low', trem, m + 12, t, t + d, v, pf, rise=0.3, fall=1.5, gain=0.5)
        elif part == 'valhalla':
            p = pan_of('wpos', t)
            if m < note('Db3'):
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.5), t, 0.8, p)
            else:
                M.add('brass', tbn.play(m - 12 if m > note('F4') else m, v, dur=d, release=0.5), t, 0.6, p)
        elif part == 'loge':
            p = pan_of('lpos', t)
            M.add('winds', pic.play(m, v), t, 0.8, p)
            M.add('strings', harp.play(m - 12, v - 10), t, 0.6, p)
        elif part == 'logefire':
            M.add('strings', vn.play(m, v, dur=d, release=0.1), t, 0.45, pan_of('lpos', t))
        elif part == 'moan':
            p = pan_of('mpos', t)
            M.add('mime', obs.play(m, v, dur=d, release=0.2), t, 0.55, p)
            M.add('mime', bsus.play(m - 12, v - 10, dur=d, release=0.2), t, 0.8, p)
        elif part == 'moanlow':
            hold('low', bsus, m, t, t + d, v, pan_of('mpos', t), rise=0.3, fall=0.6, gain=0.5)
        elif part == 'appear':
            p = pan_of('apos', t)
            M.add('brass', tbn.play(m + 12, v, dur=0.8, release=0.3), t, 0.9, p)
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, p)
