"""In Flight: Brünnhilde draws back out of sight up Porch Right, her silver and gold fading into the heights,
and the lovers stagger in from the free end of Right: Sieglinde (hearth amber) lurching ahead, Siegmund (Wälsung
blue) behind her with Nothung at his side, a white steel glint on a gold hilt.

The music is Wagner's own: Act II, bars 1174 to 1193 (the lovers' flight, rising to its fortissimo, and
"Raste nun hier ... Weiter! Weiter!") and bars 1392 to 1434 (Sieglinde's terror and vision: "Horch! O horch! Das
ist Hundings Horn! ... Rüden fletschen die Zähne nach Fleisch ... die Esche stürzt, es bricht der Stamm! Bruder!
Mein Bruder! Siegmund! Ha!", and her faint), as Solti's 1958 Vienna Philharmonic recording takes them. The notes
come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the flight on the full orchestra, violins
doubled by oboes while she sings, the horn calls on the horns, the hounds' yelps on piccolo and flutes over
churning low strings, her vision of his death on the full brass, and her faint on clarinets over soft strings;
timpani, cymbals and a gong on its real accents. Over the score, the stage's sounds: their running feet on the
gallop, a thud on every stumble, the hunt's hooves nearing from the end of Right, each hound's yelp and its paws
racing at her, teeth snapping, the sword shattering and thunder as he falls in her vision, the ash tree crashing
down on "es bricht der Stamm", and her body falling as she faints. The effects lead the flight, the hounds, the
sword's shattering and the ash tree's crash; they back off for the lovers' words, further for Hunding's horns so
the horns are clear, and all but disappear for Siegmund's "Schwester! Geliebte!".

The orchestra runs with them: they come on in stops and starts, stumbling on its accents, along Right and up to
the back of the porch, the gallop racing along the house ahead of them in pulses. There she breaks from him in
guilt and horror: her amber flickers wildly, splitting with dark gaps, and she pulls away along Porch Front while
his blue reaches after her. Then she hears horns: Hunding's horn calls, each a red flash at the free end of
Right, nearer each time, and the hunt darkens Right as she runs on round the porch and down onto Left. Her
visions take her: the hounds, six snarling red-black sparks racing the length of the house toward her, one on
each yelp of the orchestra, and Siegmund dying, the house drowning in dark red as the orchestra tolls and his blue
bursts apart into sparks and gathers again. She faints: her amber slides down and collapses at Left 0.7, dimming,
as the chords fall away; the house quiets to the slate and dawn of the pass, and Siegmund kneels and watches over
her at Left 0.55, "Schwester! Geliebte!", Nothung's glint steady beside him.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK15'
TITLE = 'In Flight'
KIND = 'show'
DESCRIPTION = ('Siegmund and Sieglinde run for their lives. She is wild with guilt and terror, hears '
               'Hunding\'s horns and his hounds coming, sees Siegmund dead, and faints in his arms.')
VOICEOVER = ('They have been running all night. Behind them, getting closer, '
             'are the hunting horns of the man she left.')

EX = excerpt(__file__)                      # Act II, bars 1174-1193 and 1392-1434, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
BAR[1194] = BAR[1392] = EX['segments'][1]['start']
D = EX['seconds']
SUNG = [(t0, t1, who.lower()) for t0, t1, who, _ in EX['singing']]
T_ENTER = 0.3                               # the lovers come in from the end of Right
STUMBLES = [BAR[b] for b in (1182, 1184, 1186, 1188)]
T_GUILT = BAR[1189]                         # she breaks from him
T_HORN = BAR[1392]                          # "Horch! O horch!"
HORNS = [BAR[1392], BAR[1394], BAR[1395], BAR[1396]]   # Hunding's horn calls from the end of Right
T_HUND = BAR[1396]                          # the hunt darkens Right
DOGS = [BAR[b] for b in range(1402, 1408)]  # the hounds, one on each yelp
T_DEATH = BAR[1423]                         # "du fällst": Siegmund dying
T_FAINT = BAR[1431]                         # she faints
T_WATCH = BAR[1433]                         # "Schwester! Geliebte!"
K = 14
GLINTS = (-24, -9, 10, 23)

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
HUNDC = hexc('#8a0020')
DOG = hexc('#c01000')
DARKRED = hexc('#3a0006')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def pass_bed(G):
    """The rocky pass at dawn: slate ridges on the wings and Side, warm light on the porch heights.
    Returns f(T, wings, porch) -> (N,3), T on the shared clock."""
    d, z = G.pd, G.pos[:, 2]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.35 * np.sin(d / 430)))
    crag = 0.5 + 0.5 * np.cos(2 * np.pi * d / 61 + 2.0 * np.sin(d / 97))
    height = 0.55 + 0.45 * smoothstep(-160, -560, z)

    def f(T, wings=1.0, porch_lvl=1.0):
        cloud = 0.85 + 0.15 * np.cos(2 * np.pi * (d / 900 - T / 40))
        sl = (0.62 + 0.22 * ridge + 0.1 * crag) * cloud * ~porch * wings
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - T / 25))
        dw = (0.44 + 0.08 * glow) * height * porch * porch_lvl
        return light(SLATE, sl) + light(DAWN, dw) + light(DAWNHI, 0.2 * glow * height * porch * porch_lvl)
    return f


def singer(t):
    for t0, t1, who in SUNG:
        if t0 <= t < t1 + 0.3:
            return who
    return None


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The flight's left hand is the
    gallop ('gallop'), its right hand the twins running ('love'); the left hand of the hunt is 'hunt', the right
    hand of the hounds 'yelp', the vision of his death 'fate', the faint 'fall'; the rest 'note'."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if t < T_HORN:
            part = 'gallop' if hand == 1 else 'love'
        elif t >= T_FAINT - 2.8:
            part = 'fall'
        elif t >= T_DEATH:
            part = 'fate'
        elif DOGS[0] <= t < BAR[1406] and hand == 0:
            part = 'yelp'
        elif T_HUND <= t < BAR[1406] and hand == 1:
            part = 'hunt'
        else:
            part = 'love' if hand == 0 and singer(t) == 'sieglinde' else 'note'
        N.append((t, d, m, v, part, singer(t)))
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


def choreography(G):
    """Per frame: Sieglinde, Siegmund and Brünnhilde (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    rend = at(G, 'Right', 1.0) + 30
    keys_l = [(0, rend), (T_ENTER, rend), (BAR[1176], at(G, 'Right', 0.7)), (BAR[1178], at(G, 'Right', 0.6)),
              (STUMBLES[0], at(G, 'Right', 0.3)), (STUMBLES[1], at(G, 'Right', 0.25)),
              (STUMBLES[2], at(G, 'Porch Right', 0.7)), (BAR[1187], at(G, 'Porch Right', 0.62)),
              (STUMBLES[3], at(G, 'Porch Right', 0.1)), (T_GUILT, at(G, 'Porch Front', 0.75)),
              (T_GUILT + 1.0, at(G, 'Porch Front', 0.5)), (HORNS[0], at(G, 'Porch Front', 0.35)),
              (HORNS[1], at(G, 'Porch Front', 0.1)), (HORNS[2], at(G, 'Porch Left', 0.5)),
              (HORNS[3], at(G, 'Left', 0.95)), (DOGS[0], at(G, 'Left', 0.85)), (T_FAINT, at(G, 'Left', 0.82)),
              (T_FAINT + 2.4, at(G, 'Left', 0.7)), (D, at(G, 'Left', 0.7))]
    keys_m = [(0, rend), (T_ENTER + 1.2, rend), (BAR[1177], at(G, 'Right', 0.8)),
              (BAR[1181], at(G, 'Right', 0.4)), (BAR[1185], at(G, 'Right', 0.05)),
              (STUMBLES[3] + 0.5, at(G, 'Porch Right', 0.35)), (T_GUILT + 1.0, at(G, 'Porch Front', 0.85)),
              (BAR[1192], at(G, 'Porch Front', 0.65)), (HORNS[1], at(G, 'Porch Front', 0.3)),
              (HORNS[3], at(G, 'Porch Left', 0.3)), (DOGS[0], at(G, 'Left', 0.95)), (T_FAINT, at(G, 'Left', 0.9)),
              (T_FAINT + 2.4, at(G, 'Left', 0.72)), (T_WATCH + 2, at(G, 'Left', 0.55)), (D, at(G, 'Left', 0.55))]

    def track(keys):
        ts = [k[0] for k in keys]
        vs = [k[1] for k in keys]
        return np.interp(t, ts, vs)
    sl = follow(track(keys_l), np.full(F, 3.0))
    lurch = np.where((t > T_GUILT) & (t < T_HORN + 2), 10 * np.sin(2 * np.pi * 2.3 * t) * np.sin(2 * np.pi * 0.37 * t), 0.0)
    sm = follow(track(keys_m), np.full(F, 2.2))
    tb = np.full(F, at(G, 'Porch Right', 0.85))
    tb[t > 0.5] = at(G, 'Porch Right', 0.3)
    br = follow(tb, np.full(F, 0.8))
    return dict(t=t, linde=sl + lurch, mund=sm, brunn=br)


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    bed = pass_bed(G)
    C = choreography(G)
    N = compose()
    rend = at(G, 'Right', 1.0)

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def last(ev, t):
        i = int(np.searchsorted([e[0] for e in ev], t, side='right')) - 1
        return (ev[i], t - ev[i][0]) if i >= 0 else (None, 99.0)

    love_ev = ons('love')
    gallop_ev = ons('gallop')
    call_on = HORNS
    hund_ev = ons('hunt')
    fate_on = sorted({e[0] for e in ons('fate') if e[3] >= 95})
    terror = np.array([(e[0], e[3]) for e in N if e[4] == 'note' and BAR[1406] <= e[0] < T_DEATH], float).reshape(-1, 2)
    lh_t = {round(e[0], 3) for e in N if e[4] == 'note' and e[2] < 60}
    close = terror[[round(x, 3) in lh_t for x in terror[:, 0]]] if len(terror) else terror
    snaps = terror[(terror[:, 1] >= 80) & ~np.isin(np.round(terror[:, 0], 3), list(lh_t))]
    snap_side = rng.uniform(0, 1, len(snaps)) < 0.5
    flick = Flicker(rng, G.N, 3.0, 9.0)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    gap = rng.uniform(0, 1, 64)
    shards = rng.uniform(-1, 1, 24)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = np.zeros((G.N, 3))
        fear = smoothstep(HORNS[0] - 1, HORNS[0] + 2, t) * (1 - smoothstep(T_FAINT, T_WATCH, t))
        vision = smoothstep(DOGS[0] - 0.5, DOGS[0] + 1.0, t) * (1 - smoothstep(T_FAINT - 0.5, T_FAINT + 2.0, t))
        fr += bed(T, 1 - 0.25 * fear - 0.35 * vision, 1 - 0.2 * fear - 0.4 * vision)
        ln, mn = C['linde'][f], C['mund'][f]

        # the flight: the gallop as a run of pulses racing along the house ahead of them
        flight = smoothstep(T_ENTER - 1, T_ENTER + 1, t) * (1 - smoothstep(T_GUILT, T_GUILT + 1.5, t))
        flight += smoothstep(HORNS[0] + 1.5, HORNS[0] + 3, t) * (1 - smoothstep(DOGS[0], DOGS[0] + 1, t))
        if flight > 0:
            e, age = last(gallop_ev, t)
            beat = np.exp(-age / 0.1) if e is not None else 0.0
            stripes = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 120 + 2.2 * T))) ** 4
            near = np.exp(-((d - ln) / 650) ** 2)
            fr += light(SIEGLINDE, flight * (0.4 + 0.4 * beat) * stripes * near)
            fr += light(SIEGMUND, flight * (0.35 + 0.3 * beat) * stripes * np.exp(-((d - mn) / 650) ** 2))

        # each stumble on the orchestra's accents: a jolt of amber and blue thrown out along the house
        for ts in STUMBLES:
            if ts <= t < ts + 1.5:
                a = t - ts
                r = 30 + 700 * a ** 0.7
                fr += light(SIEGLINDE, 1.0 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - ln) - r) / 90) ** 2))
                fr += light(WHITE, 0.4 * np.exp(-a / 0.15) * np.exp(-((d - ln) / 50) ** 2))

        # Hunding's horns: red flashes at the end of Right, nearer each time; his motif darkens Right
        for k, th in enumerate(call_on):
            if th <= t < th + 2.5:
                a = np.exp(-(t - th) / 0.6)
                reach = 90 + 70 * k
                fr += light(HUNDC, a * (0.9 + 0.1 * k) * np.exp(-((d - rend) / reach) ** 2))
                fr += light(WHITE, 0.25 * a * np.exp(-(t - th) / 0.15) * np.exp(-((d - rend) / 30) ** 2))
        if T_HUND <= t < T_HUND + 8:
            e, age = last(hund_ev, t)
            a = np.exp(-age / 0.35) * (1 - smoothstep(T_HUND + 6, T_HUND + 8, t))
            fr = fr * (1 - 0.5 * (G.seg_of == 'Right'))[:, None] * 1.0
            fr += light(HUNDC, (0.25 + 0.45 * a) * (G.seg_of == 'Right') * (0.5 + 0.5 * np.exp(-((d - rend) / 200) ** 2)))

        # the hounds: six red-black sparks racing along the house toward her, each with a dark wake
        if vision > 0:
            fr = fr * (1 - 0.45 * vision) + light(DARKRED, 0.9 * vision)
            for k, td in enumerate(DOGS):
                if td <= t < td + 4.0:
                    u = (t - td) / 3.0
                    p = rend + (ln + 30 - rend) * min(u, 1.0) ** 0.8 + 8 * np.sin(2 * np.pi * 6 * t + k)
                    a = 1 - smoothstep(0.9, 1.25, u)
                    fr += light(DOG, a * np.exp(-((d - p) / 14) ** 2))
                    fr += light(WHITE, 0.35 * a * np.exp(-((d - p + 6) / 4) ** 2))
                    wake = (d > p) & (d < p + 160)
                    fr = fr * (1 - 0.5 * a * wake)[:, None]
            # the hunt closing in: red waves converge on her on every note of the left hand, teeth snap at her
            lo = int(np.searchsorted(close[:, 0], t - 1.2))
            hi = int(np.searchsorted(close[:, 0], t, side='right'))
            for tn, vn in close[lo:hi]:
                age = t - tn
                rad = 1500 * (1 - age / 1.2)
                fr += light(DOG, vision * 0.7 * (vn / 100) * np.sin(np.pi * age / 1.2)
                            * np.exp(-((np.abs(d - ln) - rad) / 70) ** 2))
            lo = int(np.searchsorted(snaps[:, 0], t - 0.4))
            hi = int(np.searchsorted(snaps[:, 0], t, side='right'))
            for j in range(lo, hi):
                age = t - snaps[j, 0]
                q = ln + (1 if snap_side[j] else -1) * (40 + 220 * (1 - age / 0.4))
                fr += light(WHITE, vision * 0.8 * (1 - age / 0.4) * np.exp(-((d - q) / 10) ** 2))
                fr += light(DOG, vision * 0.9 * (1 - age / 0.4) * np.exp(-((d - q) / 30) ** 2))
            # his death, in her mind: the house drowns in dark red and his blue bursts apart, then gathers
            if t >= T_DEATH:
                i = int(np.searchsorted(fate_on, t, side='right')) - 1
                toll = np.exp(-(t - fate_on[i]) / 0.5) if i >= 0 else 0.0
                fr += light(HUNDC, vision * (0.3 + 0.3 * toll))
                burst = np.exp(-(t - T_DEATH) / 1.5)
                for j, s in enumerate(shards):
                    q = mn + s * 400 * (1 - np.exp(-(t - T_DEATH) / 0.6)) * (1 - smoothstep(T_DEATH + 3, T_FAINT, t))
                    fr += light(SIEGMUND, vision * 0.8 * burst * np.exp(-((d - q) / 8) ** 2))
                fr += light(WHITE, 0.8 * np.exp(-(t - T_DEATH) / 0.2) * np.exp(-((d - mn) / 120) ** 2))
                for b in range(1423, 1429):                                     # each toll: a ring out from him
                    if BAR[b] <= t < BAR[b] + 1.5:
                        a = t - BAR[b]
                        r = 40 + 900 * a ** 0.7
                        fr += light(HUNDC, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - mn) - r) / 80) ** 2))
                        fr += light(WHITE, 0.5 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - mn) - r) / 20) ** 2))

        # Sieglinde: wild flicker in her guilt and terror; she falls and lies dim
        e, age = last(love_ev, t)
        sing = np.exp(-age / 0.3) if e is not None and age < 2 else 0.0
        entered = smoothstep(T_ENTER - 0.2, T_ENTER + 0.8, t)
        wild = smoothstep(T_GUILT - 0.3, T_GUILT + 0.3, t) * (1 - smoothstep(T_HORN, T_HORN + 2, t)) + 0.7 * fear
        faint = smoothstep(T_FAINT, T_FAINT + 2.6, t)
        jitter = 1 + 0.5 * wild * (flick(t)[:1].item() - 0.5) * 2
        sl = entered * (0.8 + 0.15 * sing) * (1 - 0.56 * faint) * max(jitter, 0.3)
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))
        if wild > 0.05:                         # her guilt: shards of her amber torn off round her
            near = np.exp(-((d - ln) / 120) ** 2)
            cut = np.interp((d - ln) / 8 + 3 * T, np.arange(64), gap, period=64) > 0.55
            fr += light(SIEGLINDE, wild * 0.55 * near * cut * (0.5 + 0.5 * flick(t)))
        if T_FAINT <= t < T_FAINT + 3.5:        # the fall: an amber streak down to where she lies
            a = np.exp(-(t - T_FAINT - 2.4) ** 2 / 0.3)
            fr += light(SIEGLINDE, 0.6 * a * np.exp(-((d - ln) / 80) ** 2))

        # Siegmund: steady blue, Nothung at his side
        sm = smoothstep(T_ENTER + 1.0, T_ENTER + 2.0, t) * (0.78 - 0.12 * smoothstep(T_WATCH, T_WATCH + 3, t))
        fr += light(SIEGMUND, sm * np.exp(-((d - mn) / 16) ** 2) + 0.25 * sm * np.exp(-((d - mn) / 60) ** 2))
        blade = smoothstep(mn - 32, mn - 29, d) * smoothstep(mn - 15, mn - 18, d)
        fr += light(STEEL, sm * 0.7 * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, sm * 0.7 * np.exp(-((d - mn + 12) / 3.5) ** 2))

        # Brünnhilde, withdrawing up into the heights
        hide = 1 - smoothstep(0.3, 5.5, t)
        if hide > 0:
            b = C['brunn'][f]
            bl = 0.66 * hide
            fr += light(BRUNN, bl * np.exp(-((d - b) / 16) ** 2) + 0.22 * bl * np.exp(-((d - b) / 60) ** 2))
            for j, o in enumerate(GLINTS):
                g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
                fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
            fr += light(BGOLD, 0.55 * hide * np.exp(-((d - b - 16) / 7) ** 2))
            line = smoothstep(b - 46, b - 40, d) * smoothstep(b - 12, b - 18, d)
            fr += light(SPEAR, 0.45 * hide * line)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction scene by scene: the flight, the horns, the hounds,
    the vision, the faint."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    o = Orchestra(M, level=1.8)
    rend = pan_at(at(G, 'Right', 1.0))

    def pl(t):
        return pan_at(np.interp(t, C['t'], C['linde']))

    def pm(t):
        return pan_at(np.interp(t, C['t'], C['mund']))

    def size(t):
        if t < T_HORN:
            return 0.5 + 0.5 * smoothstep(BAR[1178], STUMBLES[0], t)
        return 1.0 if t >= T_DEATH else 0.7

    def role(t, d, m, v, hand):
        if t >= T_FAINT - 2.8:                                                  # the faint: falling chords
            return [('clarinets', 0, 0, 0.7)] if hand == 0 else [('cellos', 0, 0, 0.55), ('violas', 12, -8, 0.35)]
        if T_HORN <= t < T_HUND + 1.2 and d >= 0.3:                             # Hunding's horns, far off
            return [('horns', 12 if m < 48 else 0, 0, 0.8)]
        if DOGS[0] <= t < BAR[1406] and hand == 0:                              # the hounds' yelps
            return [('piccolo', 12 if m < 72 else 0, 4, 0.5), ('violins', 0, 0, 0.5)]
        if T_DEATH <= t and hand == 1:                                          # his death: the brass tolls
            return [('trombones', 12 if m < 48 else 0, 6, 0.85), ('tuba', 0 if m < 48 else -12, 0, 0.6),
                    ('horns', 12, -4, 0.5)]
        if hand == 0 and singer(t) == 'sieglinde':
            return [('violins', 0, -4, 0.55), ('oboes', 0, -8, 0.45)]
        return None

    def pan(t, m):
        if t < T_HORN:
            return 0.5 * (pl(t) + pm(t))
        if T_HORN <= t < T_HUND + 1.2:
            return rend
        return pl(t) * 0.7

    o.tutti(EX['notes'], size=size, role=role, pan=pan)
    for k, ts in enumerate(STUMBLES):
        o.hit('timpani', ts, 108 + 2 * k, pitch=-2, gain=0.55, pan=pl(ts))
    o.hit('crash', STUMBLES[0], 108, gain=0.5)
    o.hit('timpani roll', T_HUND, 96, gain=0.4, pan=rend)
    for td in DOGS:
        o.hit('timpani', td, 96, pitch=1, gain=0.35, pan=rend * 0.6)
    o.hit('crash', T_DEATH, 116, gain=0.6, pan=pm(T_DEATH))
    for b in (1424, 1425):
        o.hit('timpani', BAR[b], 112, pitch=-3, gain=0.55)
    o.hit('gong', BAR[1426], 116, gain=0.55, pan=pm(BAR[1426]))
    o.hit('crash', BAR[1426], 110, gain=0.45)
    o.hit('timpani roll', T_FAINT + 1.6, 80, gain=0.35, pan=pl(T_FAINT + 2.4))

    # the stage: what the lights show, heard
    N = compose()
    fxhit = lambda name, t, v, g, p: o.hit(name, t, v, gain=g, pan=p, fx=True)       # a stage hit, on the fader
    last = -1.0
    for t, d, m, v, part, who in N:                                             # their running feet on the gallop
        if part == 'gallop' and t - last >= 0.16 and (t < T_GUILT + 1.0):
            fxhit('hoof soft', t, min(127, v + 10), 0.55, pl(t) if int(t * 7) % 2 else pm(t))
            last = t
    for k, ts in enumerate(STUMBLES):                                           # each stumble
        o.hit('bass drum', ts, 112, gain=0.5, pan=pl(ts), fx=True)
        fxhit('scrape', ts + 0.04, 96, 0.4, pl(ts))
    o.gallop(T_HUND, DOGS[0] + 2.0, 0.42, pan=rend, v=84, gain=0.6)             # the hunt riding nearer
    for k, td in enumerate(DOGS):                                               # each hound: a yelp, paws racing at her
        fxhit('brake drum', td, 118, 0.8, rend)
        fxhit('metal', td + 0.02, 100, 0.35, rend)
        o.gallop(td, td + 3.0, 0.24, v=100, gain=0.55,
                 pan=lambda t, td=td: rend + (pl(td + 3) - rend) * min((t - td) / 3.0, 1.0) ** 0.8)
    for t, d, m, v, part, who in N:                                             # teeth snapping at her
        if part == 'note' and BAR[1406] <= t < T_DEATH and v >= 95:
            fxhit('brake drum', t, 105, 0.45, float(np.clip(pl(t) + (0.25 if int(t * 13) % 2 else -0.25), -1, 1)))
    o.shatter(T_DEATH, pm(T_DEATH), 1.0)                                        # "du fällst": the sword in pieces
    o.thunder(T_DEATH + 0.05, 0.9, pm(T_DEATH), 0.8)
    o.boom(BAR[1426], pm(BAR[1426]), 1.0)                                       # "die Esche stürzt": the ash crashes down
    fxhit('scrape', BAR[1426] - 0.4, 120, 1.0, pm(BAR[1426]))
    o.thunder(BAR[1426] + 0.05, 1.0, pm(BAR[1426]), 0.9)
    o.boom(T_FAINT + 1.2, pl(T_FAINT + 1.2), 0.45)                              # she falls
    # the flight's feet and stumbles lead; they back off for the lovers' words and further for Hunding's horns, so
    # the horns are clear; the hunt comes forward as it nears, the hounds lead, the snapping stays up, the sword's
    # shattering and the ash tree's crash lead hardest; then they recede for "Bruder!" and all but go for his
    # "Schwester! Geliebte!"
    o.effects([(0.0, 0), (22.8, 0), (23.4, -8), (30.4, -8), (30.8, -13), (35.8, -13), (36.4, -6), (43.0, -6),
               (43.4, 1), (51.0, 1), (51.6, -6), (55.6, -6), (56.2, -3), (68.6, -3), (69.0, 1), (70.4, 0),
               (72.2, 3), (75.2, 3), (76.0, -8), (81.0, -8), (81.6, -15)])
