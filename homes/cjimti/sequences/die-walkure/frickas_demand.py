"""Fricka's Demand: the rocky pass at dawn, Wotan alone on Porch Left, and the rose glimmer at the free end of Right
growing. Fricka comes on in her chariot drawn by rams: a rushing rose streak with two pale lights pulling ahead of
it, tearing along Right to the porch, and she pulls up on Porch Right on the orchestra's great chord. Wotan comes
forward onto Porch Front to meet her: "Der alte Sturm, die alte Müh'!", the same old storm.

The music is Wagner's own: Act II, bars 151 to 165 (her approach and arrival, Wotan's sigh, the orchestra boiling
up as she comes at him) and bars 320 to 341 (her fury: "jetzt, da zu niedrigster Schmach du dich neigtest ... So
führ es denn aus; fülle das Maß! Die Betrogne laß auch zertreten!"), as Solti's 1958 Vienna Philharmonic recording
takes them. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the left hand's
galloping as she drives in on cellos and bassoons, the right hand on violins doubled by oboes while she sings,
the left hand on trombones and tuba while he does, and the great descending octaves of "So führ es denn aus" on
the full brass with a timpani stroke on every step; cymbals as she arrives and as she wins. The stage has its
sounds too: the rams' hooves and the chariot's rumble as she drives in, a crash as she pulls up, steel sparking
where her rose meets his blue, a clang for every step of the law she draws out against him, a gong as he gives
in, and hooves again as she sweeps out and Brünnhilde gallops back. The effects lead the drive in, the surges
between the lines, his giving in and the departures; they back well off for Wotan's sigh and for every line of
Fricka's fury, and sit just under the brass of the law's descending octaves.

She is the goddess of marriage, and she has come for Siegmund. The argument takes the whole house: her rose
floods in from the right, his deep blue holds from the left, and the front between them surges back and forth
over the porch, sparking where they meet, jolting on every downbeat. Then she turns his own law against him: a
steel line drawn out from her toward him, one step for every note of the descending octaves, runes carved on it
by the right hand. On the last fortissimo chords his blue drains away to almost nothing and he slumps in the
middle of the porch. Fricka, triumphant, sweeps back out the way she came, out the free end of Right with her
rams, the rose ebbing from the house, and Brünnhilde comes galloping back in through the same gap and stops on
Porch Right when she sees her father's face.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK12'
TITLE = "Fricka's Demand"
KIND = 'show'
DESCRIPTION = ('Fricka, goddess of marriage, arrives in her chariot pulled by rams, and she wants Siegmund dead. '
               'Watch their colours fight over the house until Wotan, bound by his own laws, gives in.')
VOICEOVER = ('Here comes Fricka, and she is furious. Her husband has been breaking his own rules, '
             'and she is about to make him pay for it.')

K = 11                                      # this scene's place in the shared clock (t + 80 * K)
EX = excerpt(__file__)                      # Act II, bars 151-165 and 320-341, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SUNG = [(t0, t1, who.lower()) for t0, t1, who, _ in EX['singing']]
T_DRIVE = BAR[152]                          # the rams gallop in
T_ARRIVE = BAR[158]                         # she pulls up on Porch Right
REPROACH = [BAR[163], BAR[164], BAR[165]]   # the orchestra boils up as she comes at him
T_SHAME = BAR[320]                          # "jetzt, da zu niedrigster Schmach"
T_RUSH = BAR[328]                           # the rising runs
T_SPEAR = BAR[330]                          # "So führ es denn aus": his own law
T_YIELD = BAR[337]                          # "Die Betrogne laß auch zertreten!": he gives in
T_TRIUMPH = BAR[339]
T_LEAVE = BAR[339] + 0.4                    # she sweeps out the free end of Right
T_BRUNN = BAR[340] + 0.2                    # Brünnhilde gallops back in
T_STOP = D - 0.5

SLATE = hexc('#3a3a4a')
RIDGE = hexc('#5a5a70')
DAWN = hexc('#ff7a3a')
GLOW = hexc('#ffb070')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
ROSE = hexc('#ff9ad0')
RAM = hexc('#f0e4c8')
MAUVE = hexc('#a050e0')
WHITE = hexc('#ffffff')

SLATE_L, RIDGE_L, DAWN_L, GLOW_L = 0.5, 0.3, 0.55, 0.3
WOTAN_L, BRUNN_L, FRICKA_L, ROSE_END = 0.75, 0.75, 0.78, 0.42
CRUSHED = 0.6                               # what is left of Wotan at the end


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def singer(t):
    for t0, t1, who in SUNG:
        if t0 <= t < t1 + 0.3:
            return who
    return None


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The left hand as she drives
    in is the rams ('rams'); the left hand's long notes from "So führ es denn aus" on are the spear ('spear'), the
    right hand's notes over them its runes ('carved'); the rest are 'note'. who is whoever is singing."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if t < T_ARRIVE and hand == 1:
            part = 'rams'
        elif T_SPEAR <= t < T_YIELD and hand == 1 and d >= 0.6:
            part = 'spear'
        elif T_SPEAR <= t < T_YIELD and hand == 0:
            part = 'carved'
        else:
            part = 'note'
        who = 'brunn' if t >= T_BRUNN else 'fricka' if t < T_ARRIVE else singer(t)
        N.append((t, d, m, v, part, who))
    return N


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def front_marks(G):
    """Where the front between her rose (to its right) and his blue (to its left) stands, over time."""
    L = G.length
    P = lambda seg, u: at(G, seg, u)                                            # noqa: E731
    return [(0.0, L + 200), (T_ARRIVE - 1.0, L + 200), (T_ARRIVE + 0.5, P('Right', 0.3)),
            (BAR[160], P('Porch Front', 0.55)), (BAR[162], P('Porch Front', 0.45)),
            (REPROACH[0] + 1.5, P('Porch Front', 0.3)), (REPROACH[1] + 1.5, P('Porch Right', 0.4)),
            (REPROACH[2] + 1.5, P('Porch Left', 0.75)), (T_SHAME + 1.0, P('Porch Front', 0.5)),
            (BAR[324], P('Porch Front', 0.65)), (BAR[326], P('Porch Left', 0.7)),
            (T_RUSH, P('Porch Front', 0.4)), (T_SPEAR, P('Porch Left', 0.75)), (BAR[334], P('Left', 0.9)),
            (T_YIELD + 3.0, P('Left', 0.45)), (T_LEAVE, P('Left', 0.4)), (T_LEAVE + 3.0, L + 200)]


def choreography(G):
    """Per frame: Wotan, Fricka, Brünnhilde (path distance), and the front of the argument."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    W0 = at(G, 'Porch Left', 0.5)
    sway = 5 * np.sin(2 * np.pi * (t + 80 * K) / 6.0)
    w_t = W0 + sway
    for t0, u in ((T_ARRIVE, 0.25), (REPROACH[0], 0.33), (T_SHAME, 0.28), (T_RUSH, 0.36), (T_SPEAR, 0.3),
                  (T_YIELD, 0.4)):
        w_t = np.where(t >= t0, at(G, 'Porch Front', u), w_t)
    wot = follow(w_t, np.where(t < T_YIELD, 2.0, 0.8))
    f_t = np.full(F, L + 150)
    arr = (t >= T_DRIVE) & (t < T_ARRIVE + 1)
    f_t[arr] = L + 150 + (at(G, 'Porch Right', 0.3) - L - 150) * smoothstep(T_DRIVE, T_ARRIVE, t[arr]) ** 1.6
    f_t[t >= T_ARRIVE + 1] = at(G, 'Porch Right', 0.3)
    for t0, u in ((REPROACH[0], 0.85), (REPROACH[1], 0.75), (REPROACH[2], 0.68), (T_SHAME, 0.7), (T_RUSH, 0.62)):
        f_t[(t >= t0) & (t < t0 + 3.0)] = at(G, 'Porch Front', u)
    f_t[(t >= T_SPEAR) & (t < T_TRIUMPH)] = at(G, 'Porch Front', 0.72)
    f_t[(t >= T_TRIUMPH) & (t < T_LEAVE)] = at(G, 'Porch Front', 0.8)
    lv = t >= T_LEAVE
    f_t[lv] = at(G, 'Porch Front', 0.8) + (L + 200 - at(G, 'Porch Front', 0.8)) * smoothstep(T_LEAVE, T_BRUNN, t[lv]) ** 1.4
    fri = follow(f_t, np.where((t < T_ARRIVE + 1) | (t >= T_LEAVE), 8.0, 3.0))
    b_t = np.full(F, L + 150)
    bi = t >= T_BRUNN
    b_t[bi] = L + 150 + (at(G, 'Porch Right', 0.6) - L - 150) * smoothstep(T_BRUNN, T_STOP, t[bi]) ** 0.7
    br = follow(b_t, np.full(F, 8.0))
    ts, us = zip(*front_marks(G))
    front = follow(np.interp(t, ts, us), np.full(F, 3.0))
    crush = 1 - (1 - CRUSHED) * smoothstep(T_YIELD, T_TRIUMPH + 1, t)
    return dict(t=t, wotan=wot, fricka=fri, brunn=br, front=front, crush=crush)


def rocks(G):
    """The pass's fixed parts: jagged ridges on the wings, the heights of the porch (shared with WK11)."""
    rng = np.random.default_rng(1111)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    lat = rng.uniform(0, 1, 80)
    xs = np.linspace(d.min() - 50, d.max() + 50, 80)
    jag = np.interp(d, xs, lat)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    return dict(pf=pf, jag=jag, height=np.exp(-((d - pf) / 430) ** 2), porch=porch,
                drift=Flicker(rng, G.N, 0.05, 0.2), shim=Flicker(rng, G.N, 0.3, 1.0))


def draw_pass(G, P, tt, level=1.0):
    d = G.pd
    cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - 0.025 * tt))
    fr = light(SLATE, level * SLATE_L * (0.75 + 0.25 * cloud) * (1 - 0.4 * P['height']))
    fr += light(RIDGE, level * RIDGE_L * P['jag'] ** 2 * (0.8 + 0.2 * P['drift'](tt)) * (1 - 0.5 * P['height']))
    fr += light(DAWN, level * DAWN_L * P['height'] * (0.88 + 0.12 * P['shim'](tt)))
    fr += light(GLOW, level * GLOW_L * P['height'] ** 3 * (0.8 + 0.2 * cloud))
    return fr


def draw_wotan(G, p, b, spear=0.35):
    d = G.pd
    fr = light(WOTAN, b * np.exp(-((d - p) / 30) ** 2) + 0.35 * b * np.exp(-((d - p) / 140) ** 2))
    shaft = smoothstep(p + 15, p + 30, d) * smoothstep(p + 110, p + 95, d)
    fr += light(SPEAR, spear * (b / WOTAN_L) * shaft)
    return fr


def draw_brunn(G, p, b, tt):
    d = G.pd
    fr = light(BRUNN, b * np.exp(-((d - p) / 24) ** 2) + 0.3 * b * np.exp(-((d - p) / 120) ** 2))
    fr += light(GOLD, (b / BRUNN_L) * 0.6 * (0.75 + 0.25 * np.sin(2 * np.pi * tt / 1.7)) * np.exp(-((d - p - 14) / 7) ** 2))
    return fr


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, L = G.pd, G.length
    P = rocks(G)
    C = choreography(G)
    N = compose()
    wsung = np.array([e[0] for e in N if e[5] == 'wotan'])
    fsung = np.array([e[0] for e in N if e[5] == 'fricka' and e[4] != 'rams'])
    rams = np.array([e[0] for e in N if e[4] == 'rams'])
    bsung = np.array([e[0] for e in N if e[5] == 'brunn'])
    shoves = np.array(sorted({round(e[0], 2) for e in N if e[3] >= 100 and e[4] != 'rams'}
                             | {BAR[b] for b in list(range(159, 166)) + list(range(320, 342))}))
    spear = np.array([e[0] for e in N if e[4] == 'spear'])
    carved = np.array([e[0] for e in N if e[4] == 'carved'])
    tw = Flicker(rng, G.N, 0.3, 1.2)
    edge_n = Flicker(rng, G.N, 1.5, 4.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        wp, fp, bp = C['wotan'][f], C['fricka'][f], C['brunn'][f]
        crush = C['crush'][f]
        argue = smoothstep(T_ARRIVE - 0.5, T_ARRIVE + 1.0, t) * (1 - smoothstep(T_LEAVE, T_LEAVE + 3.0, t))
        fr = draw_pass(G, P, tt, 1 - 0.55 * argue)

        # the rose glimmer at the door grows into her chariot; it streaks in along Right
        if t < T_ARRIVE + 1.5:
            g = ROSE_END * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 1.3)) * (1 - smoothstep(T_DRIVE - 0.8, T_DRIVE + 0.6, t))
            g *= 1 + 0.8 * smoothstep(0.0, T_DRIVE, t)
            fr += light(ROSE, g * np.exp(-((L - d) / 90) ** 2))

        # the argument: her rose from the right, his blue from the left, the front surging over the porch
        if argue > 0:
            u = C['front'][f] + 25 * edge_n(t)
            edge = 40
            rose = smoothstep(u - edge, u + edge, d)
            blue = 1 - rose
            seam = np.exp(-((d - u) / 45) ** 2)
            si = int(np.searchsorted(shoves, t, side='right')) - 1
            jolt = np.exp(-(t - shoves[si]) / 0.2) if si >= 0 and t - shoves[si] < 1 else 0.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.7 * t))
            fr += light(ROSE, argue * (0.46 + 0.12 * wave + 0.15 * jolt) * rose)
            fr += light(WOTAN, argue * crush * (0.48 + 0.12 * (1 - wave)) * blue)
            fr += light(WHITE, argue * (0.3 + 0.45 * jolt) * seam ** 3 * (0.6 + 0.4 * tw(t)))
            fr += light(MAUVE, argue * 0.35 * seam)

        # as she comes, a wave of rose rolls down the house ahead of her on every bar
        for b in range(152, 158):
            if BAR[b] <= t < BAR[b] + 2.5:
                a = t - BAR[b]
                q = L - 700 * a
                fr += light(ROSE, (0.3 + 0.1 * (b - 152)) * (1 - a / 2.5) * np.exp(-((d - q) / 90) ** 2))

        # she pulls up: a burst of rose and white from Porch Right
        if T_ARRIVE <= t < T_ARRIVE + 2.0:
            a = t - T_ARRIVE
            r = 20 + 600 * a ** 0.6
            fr += light(ROSE, 0.8 * (1 - a / 2) * np.exp(-((np.abs(d - fp) - r) / 60) ** 2))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.25) * np.exp(-((d - fp) / 160) ** 2))

        # his own law turned on him: a steel line drawn from her toward him, a step for every note
        if T_SPEAR - 0.1 <= t < T_TRIUMPH + 2:
            n = int(np.searchsorted(spear, t, side='right'))
            if n > 0:
                grown = (n - 1 + smoothstep(spear[n - 1], spear[n - 1] + 0.25, t)) / len(spear)
                tip = fp + (wp + 40 - fp) * grown
                fade = 1 - smoothstep(T_YIELD + 3, T_TRIUMPH + 2, t)
                shaft = smoothstep(tip - 12, tip + 12, d) * smoothstep(fp + 10, fp - 10, d)
                ci = int(np.searchsorted(carved, t, side='right')) - 1
                rune = 0.0
                if ci >= 0 and t - carved[ci] < 1.2:
                    q = fp + (tip - fp) * ((ci * 0.37) % 1)
                    rune = np.exp(-((d - q) / 18) ** 2) * np.exp(-(t - carved[ci]) / 0.35)
                hit = np.exp(-(t - spear[n - 1]) / 0.25)
                fr += light(SPEAR, fade * (0.8 * shaft + 0.7 * hit * np.exp(-((d - tip) / 18) ** 2)))
                fr += light(WHITE, fade * (0.8 * rune + 0.3 * hit * shaft))
                if t < T_SPEAR + 1.0:
                    fr += light(SPEAR, 0.5 * np.exp(-(t - T_SPEAR) / 0.3) * np.ones(G.N))

        # he gives in: the blue drains out of the wings toward him and goes out
        if T_YIELD <= t < T_TRIUMPH + 3:
            a = (t - T_YIELD) / (T_TRIUMPH + 3 - T_YIELD)
            r = 1400 * (1 - a)
            fr += light(WOTAN, 0.35 * (1 - a) * np.exp(-((np.abs(d - wp) - r) / 80) ** 2))

        # Wotan
        i = int(np.searchsorted(wsung, t, side='right')) - 1
        wf = np.exp(-(t - wsung[i]) / 0.3) if i >= 0 and t - wsung[i] < 1.2 else 0.0
        fr += draw_wotan(G, wp, WOTAN_L * crush * (1 + 0.3 * wf))

        # Fricka and her rams, with a rose train behind her when she drives
        if -200 < fp < L + 120:
            i = int(np.searchsorted(fsung, t, side='right')) - 1
            ff = np.exp(-(t - fsung[i]) / 0.25) if i >= 0 and t - fsung[i] < 1.2 else 0.0
            b = FRICKA_L * (1 + 0.3 * ff)
            fr += light(ROSE, b * np.exp(-((d - fp) / 28) ** 2) + 0.35 * b * np.exp(-((d - fp) / 130) ** 2))
            fr += light(WHITE, 0.35 * ff * np.exp(-((d - fp) / 11) ** 2))
            drive = (1 - smoothstep(T_ARRIVE, T_ARRIVE + 1.2, t)) + smoothstep(T_LEAVE - 0.3, T_LEAVE + 0.5, t)
            if drive > 0:
                ri = int(np.searchsorted(rams, t, side='right')) - 1
                hoof = np.exp(-(t - rams[ri]) / 0.12) if ri >= 0 and t < T_ARRIVE else 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)
                ahead = -1 if t < T_LEAVE else 1                                # the rams pull ahead of her
                for k, off in enumerate((45, 75)):
                    q = fp + ahead * off + 4 * np.sin(2 * np.pi * 5 * t + k)
                    fr += light(RAM, drive * (0.5 + 0.5 * hoof) * np.exp(-((d - q) / 11) ** 2))
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 26, 2)):
                    q = C['fricka'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 34) ** 2) * (1 - n_ / 12.5))
                fr += light(ROSE, 0.65 * drive * trail)

        # Brünnhilde, galloping back in by the same gap
        if bp < L + 120:
            i = int(np.searchsorted(bsung, t, side='right')) - 1
            bf = np.exp(-(t - bsung[i]) / 0.25) if i >= 0 and t - bsung[i] < 1.0 else 0.0
            if abs(bp - C['brunn'][max(f - 4, 0)]) > 6:
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 20, 2)):
                    q = C['brunn'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 26) ** 2) * (1 - n_ / 9.5))
                fr += light(BRUNN, 0.5 * trail)
            fr += draw_brunn(G, bp, BRUNN_L * (1 + 0.3 * bf * (t < T_STOP)), tt)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction for who is singing; brass for his law."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    o = Orchestra(M, level=2.3)

    def size(t):
        if t < T_ARRIVE:
            return 0.3 + 0.7 * smoothstep(T_DRIVE, T_ARRIVE, t)
        return 1.0 if t >= T_RUSH or t < BAR[161] else 0.6

    def role(t, d, m, v, hand):
        who = singer(t)
        if t < T_ARRIVE and hand == 1:                                          # the rams gallop in
            return [('cellos', 0, 0, 0.7), ('bassoons', 12 if m < 46 else 0, -6, 0.5)]
        if T_SPEAR <= t < T_YIELD and hand == 1 and d >= 0.6:                   # his own law: the full brass
            return [('trombones', 0, 4, 0.9), ('horns', 12, -2, 0.7), ('tuba', -12 if m >= 40 else 0, 0, 0.6)]
        if who == 'wotan' and hand == 1 and m >= 48:
            return [('trombones', 0, 0, 0.75), ('tuba', -12, -10, 0.4)]
        if who == 'fricka' and hand == 0:
            return [('violins', 0, -4, 0.55), ('oboes', 0, -8, 0.45)]
        return None

    def pan(t, m):
        if t < T_ARRIVE + 1 or t >= T_LEAVE:
            return pan_at(np.clip(np.interp(t, C['t'], C['fricka']), 0, G.length)) * 0.8
        return pan_at(np.interp(t, C['t'], C['front'])) * 0.6

    o.tutti(EX['notes'], size=size, role=role, pan=pan)
    pr = pan_at(at(G, 'Porch Right', 0.3))
    o.hit('crash', T_ARRIVE, 110, gain=0.6, pan=pr)
    o.hit('timpani', T_ARRIVE, 112, pitch=-3, gain=0.6, pan=pr)
    for b in range(330, 337):                                                   # a stroke on every step of the law
        o.hit('timpani', BAR[b], 110, pitch=-3, gain=0.5)
    o.hit('crash', T_YIELD, 112, gain=0.55)
    o.hit('timpani', BAR[338], 110, pitch=-4, gain=0.55)
    o.hit('crash', T_TRIUMPH, 105, gain=0.5, pan=pr)

    # the stage: what the lights show, heard
    N = compose()
    fxhit = lambda name, t, v, g, p: o.hit(name, t, v, gain=g, pan=p, fx=True)       # a stage hit, on the fader
    fpan = lambda t: pan_at(np.clip(np.interp(t, C['t'], C['fricka']), 0, G.length))
    seam = lambda t: pan_at(np.interp(t, C['t'], C['front']))
    for t in [e[0] for e in N if e[4] == 'rams']:                               # the rams' hooves as she drives in
        fxhit('hoof', t, 116, 0.6, fpan(t))
    o.wind(T_DRIVE - 0.5, T_ARRIVE + 1.0, lambda tt: 0.4 + 0.6 * smoothstep(T_DRIVE, T_ARRIVE, tt), pan=fpan)
    o.hit('timpani roll', T_DRIVE, 96, pitch=-5, gain=0.45, pan=0.7, fx=True)            # and the chariot's wheels
    o.boom(T_ARRIVE, pr, 0.9)                                                   # she pulls up on Porch Right
    fxhit('scrape', T_ARRIVE - 0.3, 115, 0.6, pr)
    for b in list(range(159, 166)) + list(range(320, 342)):                     # where rose meets blue, it sparks
        fxhit('metal', BAR[b], 100, 0.3, seam(BAR[b]))
    for k, t in enumerate(e[0] for e in N if e[4] == 'spear'):                  # his own law, drawn out step by step
        fxhit('metal', t, 116, 0.8, fpan(t) * (1 - 0.15 * k))
        fxhit('anvil', t, 112, 0.6, fpan(t) * (1 - 0.15 * k))
    for t in [e[0] for e in N if e[4] == 'carved']:                             # runes cut into it
        fxhit('brake drum', t, 80, 0.25, fpan(t))
    fxhit('gong scrape', T_YIELD, 115, 0.9, -0.3)                     # he gives in, his blue draining away
    o.boom(T_YIELD + 0.2, -0.2, 0.6)
    o.gallop(T_LEAVE, T_BRUNN + 0.8, 0.36, pan=fpan, v=112, gain=1.0)           # she sweeps out with her rams
    o.gallop(T_BRUNN, T_STOP, 0.42, pan=lambda t: pan_at(np.clip(np.interp(t, C['t'], C['brunn']), 0, G.length)),
             v=116, gain=1.1)                                                   # Brünnhilde gallops back in
    # the effects lead the chariot's drive in, back off for Wotan's sigh and for Fricka's lines, come forward in
    # the gaps where the front surges, sit just under the law's steel steps, lead his collapse and the departure
    o.effects([(0.0, 0), (17.5, 0), (18.4, -11), (28.2, -11), (29.2, -3), (37.4, -3), (38.2, -10), (52.0, -10),
               (52.8, -4), (60.0, -4), (60.6, -7), (67.6, -7), (68.4, -2), (69.6, -2), (70.4, -9), (73.6, -9),
               (74.4, 0)])
