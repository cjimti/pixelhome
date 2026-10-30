"""The Ransom: grey morning on the mountain, Valhalla dim across the porch, and Wotan wants the hoard. Alberich,
bound, raises the ring to his lips and orders his Nibelungs up out of the earth, "Wohlan, die Niblungen rief
ich mir nah": a red pulse races from him all the way to the free end of Right, and their rhythm stirs deep below.
They come: wave after wave of orange sparks rushes in from the end of Right, along Right and up Porch Right, each
carrying a fleck of gold, to the middle of Porch Front, where they drop it and scurry back the way they came,
while Alberich drives them on ("Rasch da! Rasch! ... Fort in die Schachten!"). The procession swells to a
fortissimo and the heap grows, wider and brighter, flashing gold on the orchestra's calls, until it pours
down and away and at his word they flee. Alberich's red shrinks with shame at being seen tied up by his own
slaves. Loge tosses the helmet onto the heap: a violet arc from his hand, and a violet shimmer crowns the gold.

Then Wotan wants the ring as well. Alberich refuses with everything he has left ("frevelst, Ewiger, du,
entreißest du frech mir den Ring!"): his red swelling, the ring flaring, while a steel line points at him from
Wotan. "Her der Ring!": Wotan closes in, three times, as the bass plunges, and at the bottom of its fall he
tears the ring from his finger, the whole house flashing red. The gold point and its red glint burst out from
Alberich in a ring of beads that sweeps over the entire house, then swirl back in from both ends as the music
climbs, and close onto Wotan's blue as a hard gold point with a red glint. Alberich sinks to a dim, muddy red,
and shrieks: "Ha!".

The music is Wagner's own: Scene 4, bars 2927 to 2934, 2961 to 2980 and 3078 to 3092, as Solti's 1958 Vienna
Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py): the Nibelungs' rhythm deep in cellos and basses, the procession on the orchestra with the
Gold's calls on trumpets and horns, Alberich's protest on strings over trombones, the plunge on tubas,
trombones and basses, the climb and the shriek on the full brass. On top, as a staged production would, kept
down under Alberich's lines and Wotan's demand: the Nibelungs' scurrying feet coming and going with each wave
and the clink of each wave's gold on the heap, a rush as they flee, a whoosh as the helmet flies, the blows of
Wotan's struggle, and a crash and a burst of beads as the ring is torn away.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG19'
TITLE = 'The Ransom'
KIND = 'show'
DESCRIPTION = ('To buy his freedom, Alberich orders his Nibelungs to carry the whole hoard up to the mountain, '
               'and they pile it up in front of him, helmet and all. Then Wotan wants the ring too, and when '
               'Alberich will not give it, Wotan tears it off his finger.')
VOICEOVER = ('Every scrap of gold he ever made, carried up and heaped at the feet of the gods. '
             'But the god wants one thing more.')

EX = excerpt(__file__)                      # bars 2927-2934, 2961-2980, 3078-3092, Solti 1958
BAR = {int(m): t for m, t in EX['bars'] if m not in (2935, 2981)}
BEAT = 0.5
T_DEMAND = 0.0                              # Wotan: the hoard
T_CALL = 0.99                               # Alberich lifts the ring and orders them up
WAVES = [5.5, 9.3, 12.7, 16.4, 20.1, 23.7, 27.2, 30.8, 34.8, 38.4]
PER = 8                                     # Nibelungs in a wave
T_FLEE = BAR[2977]                          # the procession pours down and away: they flee
T_HELM = BAR[2980] - 0.6                    # Loge tosses the helmet on the heap
T_RINGDEM = BAR[3078]                       # Wotan wants the ring
T_REFUSE = 52.235                           # "frevelst, Ewiger, du!"
PUSHES = [BAR[3083], BAR[3085], BAR[3086]]  # "Her der Ring!": he closes in as the bass plunges
T_TEAR = BAR[3087]                          # torn from his finger, at the bottom of the plunge
RB = 0.55
T_SWIRL = T_TEAR + 1.2                      # the beads swirl back in onto Wotan as the music climbs
T_ON = BAR[3090]                            # the ring is his
T_SCREAM = 82.243                           # "Ha!"
T_SOFT = 1e9
T_VALH = 1e9
NB = 0.45
D = EX['seconds']

ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
STEEL = hexc('#5a88d0')
FORGE = hexc('#ff7a10')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')
WHITE = hexc('#ffffff')

def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def nibelungs(G):
    """Each Nibelung of each wave: launch time, speed in, arrival, offset on the heap -> arrays (W, PER)."""
    rng = np.random.default_rng(19)
    launch = np.array(WAVES)[:, None] + np.arange(PER)[None, :] * 0.13 + rng.uniform(0, 0.06, (len(WAVES), PER))
    speed = rng.uniform(560, 760, (len(WAVES), PER))
    off = rng.uniform(-30, 30, (len(WAVES), PER))
    dist = G.length - at(G, 'Porch Front', 0.5) - off
    return launch, speed, off, launch + dist / speed


def compose(G=None):
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The Nibelungs' rhythm stirring
    ('nib'), the procession ('proc', with the Gold's calls 'gold'), Alberich's protest ('refuse'), the plunge as
    Wotan closes in ('struggle') and the climb and shriek once the ring is torn away ('ringtutti')."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < BAR[2961] - 0.01:
            part = 'nib'
        elif t < T_RINGDEM - 0.01:
            part = 'gold' if h == 0 and d >= 0.4 and BAR[2966] <= t < BAR[2972] else 'proc'
        elif t < PUSHES[0] - 0.01:
            part = 'refuse'
        elif t < T_TEAR - 0.01:
            part = 'struggle'
        else:
            part = 'ringtutti'
        N.append((t, d, m, v, part, None))
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def choreography(G):
    """Per frame: bound Alberich, Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    A, W, Lg = at(G, 'Porch Front', 0.2), at(G, 'Porch Front', 0.4), at(G, 'Porch Front', 0.75)
    set_(0, 0, D, A + 3 * np.sin(2 * np.pi * t / 2.3), 3.0)
    set_(0, T_REFUSE, T_TEAR + 0.3, A - 8 + 6 * np.sin(2 * np.pi * t / 0.5), 8.0)
    set_(0, T_TEAR + 0.3, D, A - 14, 1.5)
    set_(1, 0, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 2.0)
    set_(1, T_RINGDEM, PUSHES[0], W - 12, 2.0)
    for i, tp in enumerate(PUSHES):
        set_(1, tp, T_TEAR, W - 25 - 18 * i, 10.0)
    set_(1, T_TEAR, T_TEAR + 0.6, A + 30, 16.0)
    set_(1, T_TEAR + 0.6, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 1.2)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(2, 0, D, Lg + jit, 4.0)
    set_(2, T_HELM - 0.6, T_HELM + 0.8, Lg - 20 + jit, 10.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose(G)
    launch, speed, off, arrive = nibelungs(G)
    back = rng.uniform(900, 1200, launch.shape)
    drops = np.array(sorted(arrive.ravel()))
    golds = np.array([e[0] for e in N if e[4] == 'gold'])
    soft = np.array([e[0] for e in N if e[4] == 'ringsoft'])
    tutti = np.array([e[0] for e in N if e[4] == 'ringtutti'])
    refuse = np.array([e[0] for e in N if e[4] == 'refuse'])
    sung = [(t0, who) for t0, t1, who, text in EX['singing'] if T_RINGDEM <= t0 < T_TEAR]
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)
    dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
    dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
    wc = grey(WOTAN, 0.4)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def beads(c, R, spin, n, b_front, b_back, w=20):
        th = 2 * np.pi * (np.arange(n) / n + spin)
        q, depth = c + R * np.cos(th), np.sin(th)
        g = np.exp(-((d[:, None] - q[None, :]) / w) ** 2)
        return (light(GOLD, b_front * (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)) +
                light(RED, b_back * (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)))

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        torn = smoothstep(T_TEAR, T_TEAR + 0.05, t)
        tf = last(tutti, t, 0.35)

        # grey dawn on the meadow, Valhalla dim across the porch
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t + 27)))
        lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * (wings + 0.5 * porch)
        fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
        fr += light(grey(VAL, 0.15), 0.34 * merlon)

        # the command: a red pulse racing from Alberich to the free end of Right
        if T_CALL + 0.8 <= t < T_CALL + 3.5:
            a = t - (T_CALL + 0.8)
            q = ap + (L - ap) * smoothstep(0, 1.6, a)
            tail = smoothstep(q - 260, q, d) * (d <= q + 10) * (d >= ap)
            fr += light(ALB, (0.75 * np.exp(-((d - q) / 30) ** 2) + 0.3 * tail) * (1 - smoothstep(1.8, 2.7, a)))
        if T_CALL + 2.4 <= t < WAVES[0] + 1:     # the free end of Right stirring, waiting
            fr += light(FORGE, 0.5 * smoothstep(T_CALL + 2.4, WAVES[0], t) * (0.7 + 0.3 * tw(t)) * blob(L, 60))

        # the Nibelungs: sparks rushing in from the end of Right with gold, dropping it, scurrying back
        route = smoothstep(WAVES[0] - 0.5, WAVES[0] + 1, t) * (1 - smoothstep(T_FLEE + 0.5, T_FLEE + 3, t))
        if route > 0:                                       # their road glows warm while they come and go
            fr += light(FORGE, route * (0.2 + 0.08 * np.cos(2 * np.pi * (d / 120 + 1.5 * t))) * smoothstep(pf + 40, pf + 160, d))
        live = (t >= launch - 0.1) & (t < arrive + 0.15 + (L - pf) / back + 0.2)
        if live.any():
            tin = np.clip(t - launch, 0, None)
            q = np.where(t < arrive, L - speed * tin, pf + off)
            out_ = t >= arrive + 0.15
            q = np.where(out_, pf + off + back * (t - arrive - 0.15), q)
            fleeing = t >= T_FLEE
            q = q[live]
            carry = (t < arrive)[live]
            g = np.exp(-((d[:, None] - q[None, :]) / 11) ** 2)
            fr += light(FORGE, (0.95 * g).max(axis=1) * (1 - 0.35 * fleeing))
            if carry.any():
                fr += light(GOLD, 0.8 * (g[:, carry]).max(axis=1)) + light(HOT, 0.4 * (np.exp(-((d[:, None] - q[carry][None, :]) / 4) ** 2)).max(axis=1))
            trail = np.exp(-((d[:, None] - (q + np.where(carry, 30, -30))[None, :]) / 20) ** 2)
            fr += light(FORGE, 0.4 * trail.max(axis=1))
        if T_FLEE <= t < T_FLEE + 2.0:                       # they flee: a rush of orange out to the end
            a = t - T_FLEE
            qq = pf + (L - pf) * smoothstep(0, 1.2, a)
            fr += light(FORGE, 0.6 * (1 - a / 2.0) * smoothstep(qq - 400, qq, d) * (d <= qq) * (d > pf))

        # the heap: wider and brighter with every Nibelung's drop; the gold call flashes it
        h = np.searchsorted(drops, t) / len(drops)
        dp = last(drops, t, 0.15, 0.6)
        gp = last(golds, t, 0.3)
        hw = 8 + 14 * h
        fr += light(GOLD, (0.3 + 0.6 * h + 0.3 * dp + 0.25 * gp) * blob(pf, hw) + (0.1 + 0.15 * h) * blob(pf, 2 * hw))
        fr += light(HOT, (0.2 + 0.4 * h) * blob(pf, 0.5 * hw) * (0.5 + 0.5 * tw(t)) * (tw(t) > 0))
        if gp > 0.05:
            fr += light(GOLD, 0.4 * gp * np.exp(-((np.abs(d - pf) - 500 * (1 - gp)) / 120) ** 2))
        crown = smoothstep(T_HELM + 0.5, T_HELM + 0.7, t)
        if crown > 0:
            fr += light(TARN, 0.55 * crown * blob(pf, hw + 8) * (0.6 + 0.4 * tw(t)))
        if T_HELM <= t < T_HELM + 0.8:                       # the helmet tossed: a violet arc
            u = smoothstep(T_HELM, T_HELM + 0.6, t)
            q = lp + (pf - lp) * u
            fr += light(TARN, 1.0 * blob(q, 16) + 0.5 * blob(q + 25, 18))

        # Loge; the helmet in his hand until he tosses it
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)
        if t < T_HELM:
            fr += light(TARN, 0.6 * blob(lp, 34) * (0.7 + 0.3 * tw(t)))

        # Wotan: greyed blue; his demand swells him and points a steel line at Alberich
        dem = smoothstep(T_RINGDEM, T_RINGDEM + 1, t) * (1 - smoothstep(T_TEAR, T_TEAR + 1, t))
        pp = sum(np.exp(-(t - tp) / 0.25) for tp in PUSHES if tp <= t < tp + 1.5)
        fr += light(wc, (0.85 + 0.2 * dem + 0.35 * pp) * blob(wp, 22 + 8 * pp) + (0.3 + 0.2 * dem) * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3), 0.25 * blob(wp, 7))
        if dem > 0:
            line = (d < wp) & (d > ap)
            fr += light(SPEAR, 0.45 * dem * line * (0.7 + 0.3 * np.cos(2 * np.pi * (d / 40 + 2 * t))))

        # Alberich: bound; proud as he commands, shrinking with shame, flaring as he refuses, crushed after
        cmd = smoothstep(T_CALL, T_CALL + 0.5, t) * (1 - smoothstep(T_CALL + 2.5, T_CALL + 4, t))
        shame = smoothstep(WAVES[0], WAVES[2], t) * (1 - smoothstep(T_FLEE - 1, T_FLEE + 1, t))
        rf = last(refuse, t, 0.25)
        fight = smoothstep(T_REFUSE, T_REFUSE + 0.5, t) * (1 - torn)
        crushed = smoothstep(T_TEAR + 0.5, T_ON, t)
        ab = (0.72 + 0.3 * cmd - 0.25 * shame + 0.2 * fight + 0.3 * rf) * (1 - 0.45 * crushed)
        fr += light(MUD, (0.32 + 0.12 * crushed) * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
        fr += light(ALB, ab * blob(ap, 24 + 10 * cmd + 8 * fight - 6 * shame) * (1 + 0.2 * smoulder(t)))
        wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
        fr += light(STEEL, (0.8 + 0.3 * pp) * (1 - 0.3 * crushed) * wrap)
        if torn < 1:                                        # the ring still his
            rb = 1 + 0.8 * cmd + 0.6 * rf + 0.4 * fight
            fr += light(GOLD, 0.9 * rb * blob(ap, 6)) + light(RED, 0.7 * rb * blob(ap + 9, 6 + 4 * fight) * (0.6 + 0.4 * tw(t)))

        # torn away: a red flash, a ring of beads bursting over the house, then swirling in onto Wotan
        if T_TEAR <= t < T_TEAR + 1.5:
            a = t - T_TEAR
            fr += light(RED, 0.95 * np.exp(-a / 0.4) * np.ones(G.N))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.08) * blob(ap, 60))
        if T_TEAR <= t < T_SWIRL:
            a = (t - T_TEAR) / (T_SWIRL - T_TEAR)
            fr += beads(ap, 40 + 1500 * a ** 0.6, 0.5 * a, 18, 1.0, 0.8, 26)
        if T_SWIRL <= t < T_ON + 0.6:
            a = smoothstep(T_SWIRL, T_ON, t)
            fr += beads(wp, 1540 * (1 - a) + 10, 0.5 + 1.6 * a ** 1.5, 18, 0.95 + 0.4 * tf, 0.7 + 0.3 * tf, 26 - 12 * a)
        if torn > 0:                                        # on Wotan's hand, its red glint pulsing to the motif
            on = smoothstep(T_ON - 0.5, T_ON + 0.3, t)
            sp = last(soft, t, 0.4) + tf
            fr += light(GOLD, on * (0.95 + 0.3 * sp) * blob(wp, 6))
            fr += light(RED, on * (0.6 + 0.5 * sp) * blob(wp + 9, 6 + 3 * sp) * (0.6 + 0.4 * tw(t)))
            if T_ON <= t < T_ON + 1.0:
                fr += light(HOT, 0.8 * np.exp(-(t - T_ON) / 0.2) * blob(wp, 30))
        for t0, who in sung:                                # the quarrel: each line a wave out from its singer
            if t0 <= t < t0 + 1.8:
                a = t - t0
                c, src = (ALB, ap) if who == 'Alberich' else (SPEAR, wp)
                fr += light(c, 0.7 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - src) - 600 * a ** 0.7) / 80) ** 2))
        if T_SCREAM <= t < T_SCREAM + 2.0:                  # "Ha!": a last red flare out from him
            a = t - T_SCREAM
            fr += light(ALB, 0.8 * np.exp(-a / 0.4) * blob(ap, 40 + 300 * a))
            fr += light(RED, 0.4 * np.exp(-a / 0.25) * np.ones(G.N))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the ransom's sounds on top."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    L = G.length
    pf = at(G, 'Porch Front', 0.5)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C[k]))

    o = Orchestra(M, level=2.25)
    part = {(e[0], e[2], e[3]): e[4] for e in compose(G)}

    def role(t, d, m, v, h):
        p = part.get((t, m, v))
        if p == 'nib':                                      # their rhythm, deep below
            return [('cellos', 12 if m < 40 else 0, 20, 0.6), ('basses', 0, 20, 0.5)] + \
                ([('tuba', 12, 10, 0.4)] if h == 1 else [])
        if p == 'gold':                                     # the Gold's call
            return [('trumpets', 0, 4, 0.5), ('horns', 0, 0, 0.45)]
        if p == 'struggle':                                 # the plunge
            if h == 1:
                return [('tuba', 0, 0, 0.6), ('trombones', 12, -4, 0.5), ('basses', 0, 0, 0.5)]
            return [('horns', 0, 0, 0.55), ('violins', 0, -6, 0.4)]
        if p == 'ringtutti':                                # the climb and the shriek: full brass
            if h == 1:
                return [('tuba', 0, 0, 0.55), ('trombones', 0, 0, 0.5), ('cellos', 0, 0, 0.45)]
            return [('trumpets', 0, -4, 0.45), ('horns', 0, 0, 0.5), ('violins', 0, 0, 0.45)] + \
                ([('piccolo', 0, -12, 0.3)] if m >= note('C6') else [])
        return None                                         # the procession and the protest: the orchestra's default

    o.tutti(EX['notes'], role=role, pan=lambda t, m: pan_of('alb', t) * 0.5)
    # the stage, ridden: under his commands, up for the procession, well down for the demand, up for the tearing
    o.effects([(0, -10), (WAVES[2], -3), (T_FLEE + 2, -4), (T_RINGDEM, -12), (PUSHES[0] - 0.3, -4), (T_TEAR - 0.2, 0),
               (T_ON + 1, -5)])
    launch, speed, off, arrive = nibelungs(G)
    for w in range(len(WAVES)):                             # each wave: scurrying feet in from the end, gold dropped
        t0, t1 = float(launch[w].min()), float(arrive[w].max())
        o.gallop(t0, t1, 0.22, pan=lambda t, t0=t0, t1=t1: pan_at(L - (L - pf) * (t - t0) / max(t1 - t0, 0.1)),
                 v=70 + 3 * w, gain=0.5)
        o.hit('metal', float(np.median(arrive[w])), 70 + 3 * w, gain=0.25, pan=pan_at(pf))
        o.play('glock', note('E6') - 12 * (w % 2), float(np.median(arrive[w])), 0.2, 80, pan_at(pf), 0.25)
    M.add('fx', whoosh(1.4, 600, 4000, 0.5, seed=19), T_FLEE, 0.6, pan_at(pf + 600))      # they flee
    M.add('fx', whoosh(0.7, 2000, 8000, 0.4, seed=20), T_HELM, 0.5, pan_of('loge', T_HELM))   # the helmet flies
    o.hit('triangle', T_HELM + 0.6, 90, gain=0.3, pan=pan_at(pf))
    for tp in PUSHES:                                       # he closes in
        o.hit('timpani', tp, 116, pitch=-4, gain=0.6, pan=pan_of('wot', tp))
        o.hit('bass drum', tp, 110, gain=0.5, pan=pan_of('wot', tp))
    pa = pan_of('alb', T_TEAR)
    o.hit('crash', T_TEAR, 124, gain=0.7, pan=pa)           # torn away
    o.boom(T_TEAR, pa, 0.9)
    M.add('fx', whoosh(1.2, 800, 6000, 0.5, seed=21), T_TEAR, 0.6, 0.0)       # the beads burst out
    M.add('fx', whoosh(T_ON - T_SWIRL, 6000, 800, 0.4, seed=22), T_SWIRL, 0.5, 0.0)   # and swirl back in
    o.hit('triangle', T_ON, 110, gain=0.4, pan=pan_of('wot', T_ON))
    o.hit('crash', T_SCREAM, 116, gain=0.45, pan=pan_of('alb', T_SCREAM))
