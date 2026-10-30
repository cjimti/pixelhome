"""The Serpent: Alberich (red, the ring a gold point with a red glint) stands by his glowing hoard in the middle
of Porch Front, Wotan (blue) on Porch Left, Loge (fire) close by on Porch Front. Loge has asked to see what the
helmet can do; Alberich puts it on. The Tarnhelm's mysterious chords sound, its violet-grey shimmer swirls round
him and spreads, he cries "Riesenwurm winde sich ringelnd!" and dissolves into it.

Out of the porch rises a giant serpent, the biggest thing on the house so far: a green-black body, scaled, with
coils of bright green rolling down it, that stretches from the middle of the porch out over Porch Right and all
of Right, while its head rears at Loge. Its music is the slow, creeping theme of the giant worm in the lowest
octaves, a coil of green rolling down its body with every note; it climbs, swells, and breaks into the
orchestra's fortissimo as Loge shrieks "Ohe! Ohe! Schreckliche Schlange, verschlinge mich nicht!" and Wotan
laughs. Its jaws open and snap shut on the orchestra's hammered chords, a burst of green-white and a stab with
every bite; the head lashes along Porch Left and out over Left, the tail whips at the end of Right, and at its
height the whole body heaves, the last bites flash the whole house green and the serpent roars. Loge plays the
coward: his flame shrinks to a flicker and backs away from every bite, cowering near the corner of Left. Wotan
stands his ground, blue, laughing, even when the coils pass over him.

Then the Tarnhelm's shimmer again and the serpent shrinks back down its own length into Alberich, who stands
red by his gold again: "Hehe! Ihr Klugen! Glaubt ihr mir nun?"

The music is Wagner's own: Scene 3, bars 2657 to 2664 and 2668 to 2679, as Solti's 1958 Vienna Philharmonic
recording takes them (the Tarnhelm chords and the spell, the serpent's emergence and the start of its theme,
then the theme climbing to the fortissimo and Alberich's return). The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the Tarnhelm chords on muted horns over cellos; the serpent's theme in the
low octaves on tubas, contrabassoon-like bassoons and double basses, trombones and horns doubling it as it
climbs; the fortissimo's hammered chords on trombones, horns and trumpets, its rushing bass on cellos and
basses. The dynamics, which the reduction keeps in the right hand only, are carried to the left. On top, as a
staged production would: a boom and a deep rumble as the serpent rears up, a hiss as its jaws open and a crack
of timpani and bass drum on every bite (cymbals on the last, house-flashing ones), a gong-and-cymbal roar at its
height, a gong scrape as it shrinks away, and a sharp pop as Alberich is himself again.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG16'
TITLE = 'The Serpent'
KIND = 'show'
DESCRIPTION = ('Loge asks Alberich to show what his helmet can do, and Alberich turns himself into a giant '
               'serpent that coils over the whole house, snapping its jaws. Loge pretends to be terrified, and '
               'then, very innocently, asks whether it could make him small as well.')
VOICEOVER = ('Loge has a question for Alberich, and he asks it very politely. '
             'Alberich is only too happy to show off.')

EX = excerpt(__file__)                      # Scene 3, bars 2657-2664 and 2668-2679, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_TARN = 0.0                                # the Tarnhelm's chords
T_SPELL = BAR[2660]                         # "Riesenwurm winde sich ringelnd!"
T_EMERGE = BAR[2663]                        # the serpent rises
T_THEME = BAR[2664]                         # its creeping theme in the low octaves
T_SWELL = BAR[2670]                         # the theme swells
T_FF = BAR[2671]                            # the fortissimo: Loge shrieks, Wotan laughs
SNAPS = [55.34, 58.2, 60.09, 61.94, 64.76, 68.45, 72.09, 73.48]     # the hammered chords: its bites
BIG = [68.45, 72.09, 73.48]                 # the bites that flash the whole house
T_ROAR = BAR[2676]
T_SHRINK = BAR[2677]
T_BACK = BAR[2679] - 0.6                    # Alberich again
LAUGHS = [85.87, 86.5]                      # "Hehe!"
D = EX['seconds']
HEAP = 0.8876                               # the hoard as RG15 left it

EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
SPARK = hexc('#ff7a10')
HOT = hexc('#fff0a0')
GOLD = hexc('#ffaa00')
GLINT = hexc('#ffd860')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
TARN = hexc('#5a4a8a')
TARN_HI = hexc('#9a88d0')
SCALE = hexc('#063010')
COIL = hexc('#10b02a')
SHEEN = hexc('#90ff60')
JAW = hexc('#d0ff80')
EYE = hexc('#f0ff20')
WOTAN = hexc('#1a3cff')
LOGE_A = hexc('#ff5000')
LOGE_B = hexc('#ffb020')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def dyn(notes):
    """The reduction keeps the dynamics in the right hand: each note's velocity raised to the right hand's nearby."""
    rh = np.array([(n[0], n[3]) for n in notes if n[4] == 0])
    out = []
    for t, d, m, v, h in notes:
        near = rh[np.abs(rh[:, 0] - t) < 0.7, 1]
        out.append((t, d, m, int(max(v, near.max() - 6)) if len(near) else v, h))
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Before the serpent the notes
    are the Tarnhelm's chords ('tarn'); its emergence is 'emerge'; its theme in the left hand is 'coil' (the right
    hand's octave over it 'coilhi'); in the fortissimo the right hand's chords are 'snap' and the left hand's rushing
    bass 'run'; from the shrinking on, 'tarn' again. 'loge', 'wlaugh', 'laugh' and 'hiss' mark moments for the
    lights and the stage; they make no sound."""
    N = []
    for t, d, m, v, h in dyn(EX['notes']):
        if t < T_EMERGE - 0.01:
            part = 'tarn'
        elif t < T_THEME - 0.01:
            part = 'emerge'
        elif t < T_FF - 0.01:
            part = 'coil' if h == 1 else 'coilhi'
        elif t < T_SHRINK - 0.01:
            part = 'snap' if h == 0 else 'run'
        else:
            part = 'tarn'
        N.append((t, d, m, v, part, None))
    for t0, t1, who, text in EX['singing']:
        if who == 'Loge':
            N.append((t0, t1 - t0, 60, 0, 'loge', None))
        elif who == 'Wotan':
            N.append((t0, t1 - t0, 60, 0, 'wlaugh', None))
    for tl in LAUGHS:
        N.append((tl, 0.3, 60, 0, 'laugh', None))
    for ts in SNAPS:
        N.append((ts - 0.45, 0.45, 60, 0, 'hiss', None))
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
    """Per frame: Alberich, Wotan, Loge, the serpent's head and tail (path distance), and its size 0..1."""
    F = nframes(D)
    t = np.arange(F) * DT
    A = at(G, 'Porch Front', 0.5)
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_(0, 0, D, A, 4.0)
    set_(0, T_SPELL, T_SPELL + 2.0, A + 8 * np.sin(2 * np.pi * t / 0.5), 12.0)
    for tl in LAUGHS:
        set_(0, tl, tl + 1.2, A + 7 * np.sin(2 * np.pi * t / 0.32), 14.0)
    set_(1, 0, D, at(G, 'Porch Left', 0.7), 3.0)
    wob = 10 * np.sin(2 * np.pi * t / 1.1)
    set_(2, 0, D, at(G, 'Porch Front', 0.3) + 0.6 * wob, 1.0)
    set_(2, T_TARN, T_EMERGE, at(G, 'Porch Front', 0.25) + 0.6 * wob, 1.0)
    # feigning terror: backing off from the head at every bite, to cower near the corner of Left
    set_(2, T_EMERGE, T_SHRINK, at(G, 'Porch Left', 0.1) + 0.4 * wob, 1.6)
    for ts in SNAPS:
        set_(2, ts, ts + 0.6, at(G, 'Porch Left', 0.03) - 25, 8.0)
    set_(2, T_SHRINK + 2.0, D, at(G, 'Porch Left', 0.5) + wob, 0.8)
    # the serpent: head rearing toward Loge and lashing out over Left, tail out over Right
    k = (T_SHRINK - T_EMERGE) / 28.6                    # its moves, spread over the real music
    w = lambda x: T_EMERGE + (x - 20.4) * k
    hp = [(T_EMERGE, A), (w(23.9), at(G, 'Porch Front', 0.15)), (w(28.5), at(G, 'Porch Left', 0.55)),
          (w(33.0), at(G, 'Porch Left', 0.25)), (w(37.0), at(G, 'Porch Left', 0.5)), (w(41.0), at(G, 'Left', 0.75)),
          (w(45.0), at(G, 'Porch Left', 0.3)), (T_ROAR, at(G, 'Left', 0.85)), (T_SHRINK, at(G, 'Porch Left', 0.4)),
          (T_BACK - 0.6, A - 12)]
    tp = [(T_EMERGE, A), (w(24.4), at(G, 'Right', 0.35)), (w(30.0), at(G, 'Right', 0.97)),
          (w(34.0), at(G, 'Right', 0.7)), (w(38.0), at(G, 'Right', 0.98)), (w(43.0), at(G, 'Right', 0.8)),
          (T_ROAR, at(G, 'Right', 0.99)), (T_SHRINK, at(G, 'Right', 0.95)), (T_BACK - 0.6, A + 12)]
    m = (t >= T_EMERGE) & (t < T_BACK)
    tgt[3][:] = A
    tgt[4][:] = A
    tgt[3][m] = np.interp(t[m], *zip(*hp))
    tgt[4][m] = np.interp(t[m], *zip(*tp)) + 30 * np.sin(2 * np.pi * t[m] / 0.9)
    rate[3][:] = 3.0
    rate[4][:] = 2.5
    for ts in SNAPS:                                        # the head lunges at each bite, then recoils
        mm = (t >= ts - 0.2) & (t < ts + 0.15)
        tgt[3][mm] -= 70
        rate[3][mm] = 14.0
    pos = np.array([follow(tgt[k], rate[k]) for k in range(5)])
    size = smoothstep(T_EMERGE - 0.2, T_EMERGE + 1.5, t) * (1 - smoothstep(T_SHRINK + 2.0, T_BACK, t))
    return dict(t=t, apos=pos[0], wpos=pos[1], lpos=pos[2], head=pos[3], tail=pos[4], size=size,
                heap=at(G, 'Porch Front', 0.68))


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    H = C['heap']
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    fl = Flicker(rng, G.N, 4.0, 11.0)
    cave = 0.5 + 0.5 * smooth_noise(rng, d, 160)
    pockets = rng.uniform(80, L - 80, 13)
    pw = rng.uniform(35, 90, 13)
    pocket = np.exp(-((d[:, None] - pockets[None, :]) / pw[None, :]) ** 2)
    pf_rate = rng.uniform(0.3, 0.9, 13)
    mist = 0.5 + 0.5 * smooth_noise(rng, d, 90)

    tarn = np.array([e[0] for e in N if e[4] == 'tarn'])
    loge = np.array([e[0] for e in N if e[4] in ('loge', 'snap')])
    laughs = np.array([e[0] for e in N if e[4] == 'laugh'])
    snaps = np.array(SNAPS)
    coils = np.array([e[0] for e in N if e[4] == 'coil'])
    wlaughs = np.array([e[0] for e in N if e[4] == 'wlaugh'])
    wlen = np.array([e[1] for e in N if e[4] == 'wlaugh'])

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['apos'][f], C['wpos'][f], C['lpos'][f]
        hd, tl, sz = C['head'][f], C['tail'][f], C['size'][f]
        I = keys(t, [(0, 0.44), (T_SPELL, 0.4), (T_EMERGE, 0.36), (T_FF, 0.42), (T_ROAR, 0.5), (T_BACK, 0.44), (D, 0.44)])
        vis = 1 - smoothstep(T_EMERGE - 2.0, T_EMERGE, t) + smoothstep(T_BACK - 0.8, T_BACK + 0.3, t)

        # the caverns
        bed = light(EMBER, I * (0.62 + 0.38 * cave) * (1 + 0.12 * smoulder(t)))
        pk = (pocket * (0.65 + 0.35 * np.sin(2 * np.pi * pf_rate * t))[None, :]).max(axis=1)
        bed += light(FORGE, I * 0.9 * pk * (0.85 + 0.15 * fl(t)))
        bed += light(SPARK, 0.65 * (rng.random(G.N) < 0.005 * (0.5 + I)))

        # the hoard
        w = 8 + 50 * HEAP
        shape = np.clip(1 - ((d - H) / w) ** 2, 0, 1) ** 0.6
        bed += light(GOLD, (0.4 + 0.5 * HEAP) * shape * (0.9 + 0.1 * smoulder(t)))
        bed += light(GLINT, 0.8 * shape * (tw(t) > 1.1)) + light(HOT, 0.4 * HEAP * shape ** 4)
        bed += light(GOLD, 0.25 * HEAP * np.exp(-((d - H) / (w + 120)) ** 2))

        # the Tarnhelm's shimmer, swirling round him as he changes (and changes back)
        sh = smoothstep(T_TARN - 0.5, T_TARN + 2, t) * (1 - smoothstep(T_EMERGE, T_EMERGE + 1.5, t))
        sh += smoothstep(T_SHRINK - 0.5, T_SHRINK + 1.0, t) * (1 - smoothstep(T_BACK, T_BACK + 2.0, t))
        if sh > 0:
            ti = int(np.searchsorted(tarn, t, side='right')) - 1
            pulse = np.exp(-(t - tarn[ti]) / 0.8) if ti >= 0 and t - tarn[ti] < 3 else 0.0
            reach = 100 + 500 * smoothstep(T_TARN, T_EMERGE, t) if t < T_EMERGE + 2 else 450.0
            swirl = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - ap) / 110 - 0.6 * t) + 4 * mist)
            env = smoothstep(reach, reach - 200, np.abs(d - ap))
            bed = bed * (1 - 0.5 * (sh * env)[:, None]) + light(TARN, sh * env * (0.22 + 0.2 * swirl + 0.15 * pulse))
            bed += light(TARN_HI, sh * env * 0.35 * swirl ** 6 * (0.5 + 0.5 * tw(t)))

        # the serpent: a green-black scaled body from head to tail, coils of green rolling down it
        if sz > 0:
            s = np.clip((d - hd) / (tl - hd if abs(tl - hd) > 1 else 1.0), -0.2, 1.2)    # 0 at the head, 1 the tail
            body = smoothstep(-0.02, 0.02, s) * (1 - smoothstep(0.96, 1.02, s)) * sz
            taper = 1 - 0.55 * smoothstep(0.55, 1.0, s)
            ci = int(np.searchsorted(coils, t, side='right')) - 1
            cp = np.exp(-(t - coils[ci]) / 0.3) if ci >= 0 and t - coils[ci] < 1 else 0.0
            heave = smoothstep(T_SWELL, T_FF, t) * (1 - smoothstep(T_ROAR + 0.5, T_SHRINK + 1, t))
            coil = 0.5 + 0.5 * np.sin(2 * np.pi * (np.abs(d - hd) / 150 - (1.3 + 0.8 * heave) * t))
            scales = (np.sin(d / 3.2) > 0.3) * (0.5 + 0.5 * tw(t))
            bed = bed * (1 - 0.88 * body)[:, None]
            fr += light(SCALE, body * (0.3 + 0.2 * scales * (1 - coil)))
            fr += light(COIL, body * taper * (0.08 + 0.12 * heave + 0.12 * cp + (0.8 + 0.15 * heave) * coil ** 4))
            fr += light(SHEEN, body * taper * 0.6 * scales * coil ** 8)
            # the head: an eye, and jaws that open before each bite and snap shut
            si = int(np.searchsorted(snaps, t + 0.5, side='right')) - 1
            gap, bite = 0.0, 0.0
            if si >= 0:
                ts = snaps[si]
                gap = 26 * smoothstep(ts - 0.5, ts - 0.1, t) * (1 - smoothstep(ts - 0.05, ts, t))
                bite = np.exp(-(t - ts) / 0.15) if t >= ts else 0.0
            dirn = -np.sign(tl - hd) if abs(tl - hd) > 1 else -1.0
            jaw_at = hd + dirn * 6
            jaws = np.exp(-((d - (jaw_at - gap)) / 6) ** 2) + np.exp(-((d - (jaw_at + gap)) / 6) ** 2) * (gap > 2)
            fr += light(JAW, sz * (0.75 * jaws + 0.9 * bite * np.exp(-((d - jaw_at) / (20 + 40 * bite)) ** 2)))
            fr += light(WHITE, sz * 0.6 * bite * np.exp(-((d - jaw_at) / 14) ** 2))
            fr += light(EYE, sz * 0.9 * np.exp(-((d - (hd - dirn * 18)) / 4) ** 2))
            if gap > 2:
                fr += light(RED, sz * 0.5 * (np.abs(d - jaw_at) < gap - 4))                 # inside the mouth
            if si >= 0 and snaps[si] in BIG and 0 <= t - snaps[si] < 0.6:
                age = t - snaps[si]
                fr += light(COIL, 0.6 * np.exp(-age / 0.15) * np.ones(G.N))
                fr += light(SHEEN, 0.3 * np.exp(-age / 0.08) * np.ones(G.N))
            if T_ROAR <= t < T_ROAR + 2.0:
                age = t - T_ROAR
                r = 1400 * (1 - np.exp(-age / 0.6))
                fr += light(SHEEN, 0.8 * np.exp(-age / 0.9) * np.exp(-((np.abs(d - hd) - r) / 90) ** 2))
                fr += light(COIL, 0.5 * np.exp(-age / 0.5) * np.ones(G.N))
        fr += bed

        # Alberich and the ring, while he is himself
        if vis > 0:
            li_ = int(np.searchsorted(laughs, t, side='right')) - 1
            ha = np.exp(-(t - laughs[li_]) / 0.15) if li_ >= 0 and t - laughs[li_] < 1 else 0.0
            pop = np.exp(-max(t - T_BACK, 0) / 0.4) * (t > T_BACK)
            fr += light(MUD, vis * 0.38 * np.exp(-((d - ap) / 120) ** 2) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, vis * (0.8 + 0.25 * ha + 0.3 * pop) * np.exp(-((d - ap) / (24 + 10 * ha + 20 * pop)) ** 2)
                        * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, vis * 0.35 * ha * np.exp(-((d - ap) / 220) ** 2))
            rr = ap + 10
            fr += light(GOLD, vis * 0.95 * np.exp(-((d - rr) / 5) ** 2))
            fr += light(RED, vis * 0.75 * np.exp(-((d - (rr + 6 * np.sin(2 * np.pi * 0.8 * t))) / 3) ** 2))

        # Wotan, standing his ground; Loge, shrinking from every bite
        under = sz * (wp > min(hd, tl)) * (wp < max(hd, tl))
        wi = int(np.searchsorted(wlaughs, t, side='right')) - 1
        wl = 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)) if wi >= 0 and t - wlaughs[wi] < wlen[wi] else 0.0
        fr += light(WOTAN, (0.85 - 0.25 * under + wl) * np.exp(-((d - wp) / (22 + 14 * wl)) ** 2)
                    + 0.25 * np.exp(-((d - wp) / 80) ** 2))
        si = int(np.searchsorted(snaps, t, side='right')) - 1
        flinch = np.exp(-(t - snaps[si]) / 0.4) if si >= 0 and t - snaps[si] < 2 else 0.0
        afraid = smoothstep(T_EMERGE, T_EMERGE + 1.0, t) * (1 - smoothstep(T_SHRINK + 1, T_BACK + 1, t))
        li = int(np.searchsorted(loge, t, side='right')) - 1
        lf = np.exp(-(t - loge[li]) / 0.15) if li >= 0 and t - loge[li] < 1 else 0.0
        small = 0.0
        width = (18 + 8 * lf) * (1 - 0.55 * afraid) * (1 - 0.4 * small) * (1 - 0.3 * flinch)
        bright = (0.72 + 0.28 * lf) * (1 - 0.35 * afraid) * (1 - 0.2 * small)
        lc = LOGE_A + (LOGE_B - LOGE_A) * (0.5 + 0.5 * fl(t))[:, None]
        jitter = 6 * afraid * np.sin(2 * np.pi * 9 * t)
        ls = (bright * np.exp(-((d - lp - jitter) / width) ** 2) * (0.75 + 0.25 * fl(t))
              + 0.25 * (1 - 0.6 * afraid) * np.exp(-((d - lp) / 60) ** 2))
        fr += perc(ls)[:, None] * lc
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, and the serpent's sounds on top."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(key, t):
        return pan_at(np.interp(t, C['t'], C[key]))

    def pan_body(t):
        return 0.5 * (pan_of('head', t) + pan_of('tail', t))

    o = Orchestra(M, level=1.65)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    for t, d, m, v, part, who in compose():
        pa = pan_of('apos', t)
        if part == 'tarn':                                  # the Tarnhelm: muted horns over cellos
            if m >= note('E3'):
                o.hold('brass', mute, m, t, t + d, v + 10, pa, gain=0.7) if d > 1.2 else \
                    o.M.add('brass', mute.play(m, v + 10, dur=d, release=0.5), t, 0.7, pa)
            else:
                o.play('cellos', m, t, d, v + 6, pa, 0.6)
        elif part == 'emerge':                              # it rears up out of the porch
            if m < note('E3'):
                o.play('tuba', m, t, d, v + 30, pa, 0.8)
                o.play('basses', m - 12, t, d, v + 20, pa, 0.6)
            else:
                o.play('trombones', m, t, d, v + 20, pa, 0.6)
                o.play('horns', m, t, d, v + 10, pa, 0.5)
        elif part == 'coil':                                # its theme in the lowest octaves
            p = pan_body(t)
            o.play('tuba', m + 12 if m < note('E1') else m, t, d, v + 40, p - 0.15, 0.9)
            o.play('bassoons', m + 12, t, d, v + 30, p + 0.15, 0.6)
            o.play('basses', m, t, d, v + 30, p, 0.6)
        elif part == 'coilhi':
            p = pan_body(t)
            o.play('trombones', m, t, d, v, p, 0.7)
            if t >= T_SWELL:
                o.play('horns', m, t, d, v - 6, p, 0.6)
        elif part == 'snap':                                # the hammered chords: brass, its bites
            p = pan_of('head', t)
            if d >= 0.4:
                o.play('trombones', m - 12 if m > note('G4') else m, t, d, v, p, 0.55)
                o.play('horns', m, t, d, v - 6, p, 0.5)
                if m >= note('G4'):
                    o.play('trumpets', m, t, d, v - 12, p, 0.35)
            else:
                o.play('violins', m, t, d, v - 6, p, 0.5)
                if m >= note('F5'):
                    o.play('flutes', m, t, d, v - 14, p, 0.35)
        elif part == 'run':                                 # the rushing bass under them
            p = pan_body(t)
            o.play('cellos', m, t, d, v, p, 0.65)
            o.play('basses', m - 12 if m >= note('E2') else m, t, d, v - 6, p, 0.5)
            if d > 0.5:
                o.play('tuba', m, t, d, v - 6, p, 0.5)
        elif part == 'hiss':                                # the jaws open
            M.add('fx', whoosh(d + 0.1, 7000, 2500, 0.5, seed=int(t * 10)), t, 0.8, pan_of('head', t))
    # the stage, ridden: up for the serpent's rising and its bites, down under its creeping theme and at the end
    o.effects([(0, -6), (T_EMERGE - 0.5, 0), (T_THEME + 2, -5), (T_SWELL, -3), (T_FF - 0.5, 0), (T_SHRINK, -2),
               (T_BACK, -8)])
    pe = pan_of('apos', T_EMERGE)
    o.boom(T_EMERGE, pe, 1.0)
    o.thunder(T_EMERGE + 0.2, 0.3, pe, 0.8)                 # a deep rumble as it rises
    o.hit('timpani roll', T_SPELL + 6.5, 96, pitch=-4, gain=0.5, pan=pe)
    for ts in SNAPS:                                        # the bites
        p = pan_of('head', ts)
        big = ts in BIG
        o.hit('timpani', ts, 124 if big else 110, pitch=-4, gain=0.8, pan=p)
        o.hit('bass drum', ts, 124 if big else 104, gain=0.7 if big else 0.45, pan=p)
        o.hit('brake drum', ts + 0.01, 100, gain=0.25, pan=p)
        if big:
            o.hit('crash', ts, 120, gain=0.6, pan=p)
    o.hit('gong', T_ROAR, 124, gain=0.8)                    # its roar
    o.hit('crash', T_ROAR, 124, gain=0.7)
    o.hit('bass drum', T_ROAR, 126, gain=0.9)
    o.hit('timpani roll', T_ROAR, 118, pitch=-5, gain=0.7)
    o.hit('gong scrape', T_SHRINK + 0.3, 110, gain=0.6, pan=pan_body(T_SHRINK))
    o.hit('timpani', T_BACK + 0.6, 100, pitch=-2, gain=0.5, pan=pan_of('apos', T_BACK + 0.6))
    o.hit('brake drum', T_BACK + 0.6, 96, gain=0.3, pan=pan_of('apos', T_BACK + 0.6))
