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

The music is Wagner's own, from Scene 3 of Das Rheingold as Solti's 1958 Vienna Philharmonic recording takes it:
"Her das Geschmeid'!" (bars 1928-1929), the Tarnhelm put on and "Nacht und Nebel, Niemand gleich!" (1953-1965),
"Siehst du mich, Bruder?" and the invisible beating (1967-1980), "Hoho! Hört ihn, er naht: der Niblungen Herr!"
as he drives them to work (2004-2015), and Loge and Wotan arriving ("Nibelheim hier", 2033-2041). The notes come
from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py); the Tarnhelm's chords are on muted horns,
Alberich on bassoons and low brass, the drive on the full orchestra with six real anvils on its rhythm, Loge's
flicker on flutes and harp. Like a staged production it adds a thud with each shake, the helmet's clink as it
falls, a cold shimmer as Alberich vanishes, and a swish and a crack for every stroke of the invisible whip.
Alberich does not come back into view in these bars: the scene ends with Wotan and Loge finding Mime.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, smoothstep, nframes, keys, smooth_noise, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'RG14'
TITLE = 'The Tarnhelm'
KIND = 'show'
DESCRIPTION = ('Alberich takes the helmet his brother Mime was made to forge, and when he puts it on, he vanishes. '
               'Unseen, he whips Mime and drives his workers back to their anvils, just as Wotan and Loge arrive.')
VOICEOVER = ('Mime has made his brother a helmet, and it does something no helmet should. '
             'Put it on, and you disappear.')

EX = excerpt(__file__)                      # bars 1928-1929, 1953-1965, 1967-1980, 2004-2015, 2033-2041
BARS_ = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SHAKES = [0.4, 2.0, 3.6]                    # "Her das Geschmeid'!": Alberich shakes Mime for the helmet
T_DROP = 4.4                                # Mime lets it fall
T_TAKE = 5.4                                # Alberich picks it up
T_TARN = BARS_[1953]                        # the Tarnhelm's chords
T_ON = 21.8                                 # "Nacht und Nebel, Niemand gleich!"
T_GONE = 28.0
T_BEAT = BARS_[1967]                        # "Siehst du mich, Bruder?"
T_WORK = BARS_[2004]                        # "Hoho! Hört ihn, er naht": he drives them to work
T_QUIET = BARS_[2033]
T_GODS = T_QUIET + 0.6                      # Wotan and Loge come down
T_LOGE = 73.1                               # "Nibelheim hier"
MOANS = [78.5, 79.9, 81.3]                  # Mime: "Au! Au! Au!"
T_BACK = D + 30.0                           # (Alberich stays unseen in these bars)
WORK_BARS = [t for m, t in sorted(BARS_.items()) if T_WORK <= t < T_QUIET]
NANV = 6


def whips():
    """The invisible whip: on the accents of the beating."""
    return accents(EX['notes'], T_BEAT + 1.0, T_WORK - 1.0, 60, 2, 1.0)[:10]


WHIPS = whips()

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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who, tremolo). Alberich's bars are
    'alb'; the Tarnhelm's chords 'tarn' (right hand) and 'tarnlow'; the beating 'agit'; the drive 'nib' (right hand)
    and 'pluck', with six anvils on the right hand's rhythm ('anvil', who = the anvil); the gods' arrival 'loge'
    (quick notes) and 'gods'. 'shake', 'clink', 'whip' and 'moan' mark moments for the lights and the stage."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t < T_TARN:
            part = 'alb'
        elif t < T_BEAT:
            part = 'tarn' if h == 0 else 'tarnlow'
        elif t < T_WORK:
            part = 'agit'
        elif t < T_QUIET:
            part = 'nib' if h == 0 else 'pluck'
        else:
            part = 'loge' if d < 0.25 and h == 0 else 'gods'
        N.append((t, d, m, v, part, None, trem))
    strokes = []
    for t in sorted({round(n[0], 3) for n in EX['notes'] if n[4] == 0 and n[1] <= 0.35}):
        if T_WORK + 1.5 <= t < T_QUIET - 1.5 and (not strokes or t - strokes[-1] >= 0.12):
            strokes.append(t)
    for t in strokes:
        for a in range(NANV):
            N.append((t, 0.1, 72, 104, 'anvil', a, False))
    for ts in SHAKES:
        N.append((ts, 0.3, 34, 0, 'shake', None, False))
    N.append((T_DROP, 0.5, 88, 0, 'clink', None, False))
    for tw in WHIPS:
        N.append((tw, 0.2, 60, 0, 'whip', None, False))
    for tm in MOANS:
        N.append((tm, 0.5, 58, 0, 'moan', None, False))
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
    set_(0, T_GONE, WHIPS[0] - 0.5, helm + 70 * np.sin(2 * np.pi * (t - T_GONE) / 2.6), 4.0)   # the hole prowls
    # the hole whips Mime down Porch Front and up Porch Left
    flee = np.linspace(M0 + 30, at(G, 'Porch Left', 0.4), len(WHIPS) + 1)
    for i, tw in enumerate(WHIPS):
        nxt = WHIPS[i + 1] if i + 1 < len(WHIPS) else T_WORK
        set_(1, tw + 0.05, nxt, flee[i + 1], 9.0)
        set_(0, tw - 0.5, nxt, flee[i + 1] + (70 if i % 2 else 110), 7.0)
    set_(1, T_WORK, D, at(G, 'Porch Left', 0.4), 4.0)
    # off to drive the Nibelungs: out along Left, back across to the end of Right, back to Porch Right
    route = [(T_WORK, at(G, 'Porch Left', 0.4) - 60), (T_WORK + 4.0, at(G, 'Side', 0.35)),
             (T_WORK + 10.0, at(G, 'Right', 0.92)), (T_QUIET + 1.0, at(G, 'Porch Right', 0.55))]
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
        return keys(t, [(0, 0.62), (T_TARN, 0.5), (T_GONE, 0.55), (T_BEAT, 0.62), (T_WORK, 0.66), (T_WORK + 4.0, 0.85),
                        (T_QUIET - 3.0, 0.82), (T_QUIET + 1.5, 0.6), (D, 0.6)])

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
            bi = int(np.searchsorted(WORK_BARS, t, side='right')) - 1
            age = t - WORK_BARS[bi]
            if 1 <= bi <= len(WORK_BARS) - 2:
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
    """Wagner's notes, orchestrated from the piano reduction (the Tarnhelm on muted horns), six anvils on the
    drive, and the shakes, the helmet's fall, the vanishing and the invisible whip on the stage."""
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(min(max(dd, 0), G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    o = Orchestra(M, level=3.0)
    # the shakes and the whip lead; the Tarnhelm's spell and the gods' arrival are the music's
    o.effects([(0.0, 0.0), (T_TARN, -10.0), (T_ON - 0.5, -10.0), (T_ON, -3.0), (T_GONE + 1.0, -6.0),
               (T_BEAT + 1.0, 0.0), (T_WORK, 0.0), (T_QUIET, -6.0), (D, -6.0)])
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    snare = M.hits('Percussion/Snare2-HitSN_v[79]*.wav')
    rng = np.random.default_rng(14)
    N = compose()
    for t, d, m, v, part, who, trem in N:
        if v == 0 or part == 'anvil':
            continue
        ap = pan_at(np.interp(t, C['t'], C['apos']))
        if trem:
            o.play('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', m, t, d, v, None, 0.5)
        elif part == 'alb':
            if m >= 55:
                o.play('violas', m, t, d, v, ap, 0.5)
            else:
                o.play('bassoons', m, t, d, v, ap, 0.55)
                o.play('cellos', m, t, d, v - 4, ap, 0.45)
        elif part in ('tarn', 'tarnlow'):                       # the Tarnhelm: muted horns, soft and strange
            if part == 'tarn' and m >= 52:
                if d > 1.2:
                    o.hold('brass', mute, m, t, t + d, v + 10, pf, 0.9)
                else:
                    M.add('brass', mute.play(m, v + 10, dur=d, release=0.3), t, 0.9, pf)
            else:
                o.play('cellos', m, t, d, v - 6, -0.2, 0.4)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 10, 0.2, 0.3)
        elif part == 'agit':
            mp = pan_at(np.interp(t, C['t'], C['mpos']))
            if m >= 60:
                o.play('violins', m, t, d, v, mp, 0.55)
                if m >= 76:
                    o.play('piccolo', m, t, 0.1, v - 10, mp, 0.35)
            elif m >= 48:
                o.play('violas', m, t, d, v, ap, 0.5)
            else:
                o.play('bassoons', m, t, d, v, ap, 0.5)
                o.play('cellos', m, t, d, v - 4, ap, 0.45)
        elif part in ('nib', 'pluck'):                          # the drive back to work: the full orchestra
            if m >= 60:
                o.play('violins', m, t, d, v, ap, 0.55)
                if d >= 0.3:
                    o.play('trumpets', m, t, d, v - 8, ap, 0.4)
            elif m >= 48:
                o.play('horns', m, t, d, v, -0.25, 0.55)
                if d >= 0.3:
                    o.play('trombones', m, t, d, v - 6, 0.1, 0.45)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.55)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.45)
                if d >= 0.5:
                    o.play('tuba', m, t, d, v - 8, 0.0, 0.45)
        elif part == 'loge':
            lp = pan_at(np.interp(t, C['t'], C['lpos']))
            o.play('flutes' if m < 79 else 'piccolo', m, t, 0.1, v, lp, 0.45)
            o.play('harp', m, t, d, v - 8, lp, 0.35)
        else:                                                   # the gods come down
            wp = pan_at(np.interp(t, C['t'], C['wpos']))
            if m >= 60:
                o.play('clarinets' if d >= 0.3 else 'violins', m, t, d, v, wp, 0.45)
            elif m >= 48:
                o.play('horns', m, t, d, v, wp, 0.5)
            else:
                o.play('tuba' if d >= 0.5 else 'cellos', m, t, d, v - 4, wp, 0.5)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 8, 0.2, 0.4)

    # six anvils on the rhythm, panned to their forges
    strokes = sorted({round(e[0], 3) for e in N if e[4] == 'anvil'})
    for t in strokes:
        for a in rng.choice(NANV, 3, replace=False):
            o.hit('anvil', t + rng.uniform(0, 0.01), 100, pitch=float(rng.uniform(-1.5, 1.5)), gain=0.3,
                  pan=pan_at(C['anvil'][a]))
    # the stage
    for ts in SHAKES:                                           # Mime shaken
        mp = pan_at(np.interp(ts, C['t'], C['mpos']))
        o.hit('timpani', ts, 96, pitch=-3, gain=0.35, pan=mp)
        o.hoof(ts + 0.12, mp, 92, 0.7)
    o.hit('metal', T_DROP, 70, gain=0.3, pan=pan_at(C['helm']))  # the helmet falls
    o.hit('triangle', T_DROP + 0.25, 80, gain=0.35, pan=pan_at(C['helm']))
    o.hit('cymbal swell', T_ON - 1.5, 84, gain=0.4, pan=pf)      # he vanishes
    o.hit('gong scrape', T_ON + 0.8, 96, gain=0.45, pan=pf)
    for k, tw in enumerate(WHIPS):                              # the invisible whip: a swish and a crack on Mime
        mp = pan_at(np.interp(tw, C['t'], C['mpos']))
        o._sfx(whoosh(0.35, 800, 6000, 0.9, seed=60 + k)[0], tw - 0.3, 0.6, mp)
        n = int(0.06 * SR)
        o._sfx(o._noise(0, 2000, 10000, 70 + k, n=n) * np.exp(-np.arange(n) / (0.008 * SR)), tw, 0.9, mp)
        M.add('perc', snare.play(118), tw, 0.45, mp)
    o.hit('crash', T_WORK + 0.1, 110, gain=0.45)                 # he drives them to work
    o._sfx(o._noise(0, 900, 6000, 81, n=int(3 * SR)) * np.sin(np.linspace(0, np.pi, int(3 * SR))) ** 2,
           T_GODS - 0.4, 0.3, pf)                                # a puff of vapour as the gods come down
