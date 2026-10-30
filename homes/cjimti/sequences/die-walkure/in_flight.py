"""In Flight: Brünnhilde draws back out of sight up Porch Right, her silver and gold fading into the heights,
and the lovers stagger in from the free end of Right: Sieglinde (hearth amber) lurching ahead, Siegmund (Wälsung
blue) behind her with Nothung at his side, a white steel glint on a gold hilt. The orchestra runs with them:
violas and cellos in a breathless D minor gallop, the love of the twins (Donington 37) torn along in the violins
and oboe, and they come on in stops and starts, along Right and up to the back of the porch.

There she breaks from him in guilt and horror: her amber flickers wildly, splitting with dark gaps, and she pulls
away along Porch Front while the twins' love sinks to a tender cello and his blue reaches after her. Then she
hears horns. Hunding's horn calls (composed, on muted horns) sound from far off at the free end of Right, each a
red flash there, his heavy dotted motif growls in the tubas, and she runs on round the porch and down onto Left.
Her visions take her: the hounds, six snarling red-black sparks racing the length of the house toward her to
shrieking piccolos and trilling low strings, and Siegmund dying, the house drowning in dark red as the tragic
destiny of the Volsungs (Donington 66) tolls in the brass and his blue bursts apart into sparks and gathers again.

She faints. Her amber slides down and collapses at Left 0.7, dimming, to a falling clarinet; the house quiets
to the slate and dawn of the pass, and Siegmund kneels and watches over her at Left 0.55 to the twins' love on a
solo cello, Nothung's glint steady beside him, while one last horn call sounds faintly from far away.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody

CODE = 'WK15'
TITLE = 'In Flight'
KIND = 'show'
DESCRIPTION = ('Siegmund and Sieglinde run for their lives. She is wild with guilt and terror, hears '
               'Hunding\'s horns and his hounds coming, sees Siegmund dead, and faints in his arms.')
VOICEOVER = ('They have been running all night. Behind them, getting closer, '
             'are the hunting horns of the man she left.')

T_HIDE = 0.0                                # Brünnhilde withdraws out of sight
T_ENTER = 3.0                               # the lovers come in from the end of Right
T_LOVE = [4.0, 10.5]                        # the twins' love, torn along, twice
LBEAT = 0.42
T_GUILT = 19.5                              # she breaks from him
T_TENDER = 21.5
TBEAT = 0.6
HORNS = [30.5, 33.8, 37.4, 40.6]            # Hunding's horn calls from the end of Right
T_HUND = 35.0
T_DOGS = 44.5                               # the hounds
T_DEATH = 52.0                              # Siegmund dying: the Volsungs' fate
FBEAT = 0.5
T_FAINT = 60.5
T_WATCH = 66.0
T_LAST = 74.0                               # one last horn call, far off
D = 80.0
K = 14

HUNDING = [(0, .75, 'D2'), (.75, .25, 'D2'), (1, 1, 'F2'), (2, .75, 'E2'), (2.75, .25, 'E2'), (3, 1, 'Db2'),
           (4, 2, 'D2')]                     # composed: Hunding, a heavy dotted tuba figure
HORN_CALL = [(0, .5, 'A3'), (.5, .25, 'A3'), (.75, 1.0, 'D4'), (1.75, .25, 'C4'), (2, 1.5, 'A3')]
GALLOP = ['D3', 'F3', 'A3', 'D4', 'A3', 'F3']
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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    # the flight: a breathless gallop in the violas and cellos, the twins' love torn along over it
    step = 0.14
    for i, t in enumerate(np.arange(T_ENTER - 1.5, T_GUILT, step)):
        m = note(GALLOP[i % 6]) + (0, 0, -2, -4)[(i // 24) % 4]
        add(t, step, m, 70 + int(30 * smoothstep(T_ENTER - 1.5, T_ENTER + 3, t)) + 10 * (i % 3 == 0), 'gallop', i)
    for j, t0 in enumerate(T_LOVE):
        for t, m, v, d in play('twins_love', t0, LBEAT, -12 + 2 * j, 98, 'melody'):
            add(t, d, m + 12, v, 'love', j)
        for t, m, v, d in play('twins_love', t0, LBEAT, -12 + 2 * j, 80, 'bass'):
            add(t, d, m, v, 'lovebass', j)
    for t in (T_ENTER + 2.2, T_ENTER + 5.6, T_ENTER + 9.4, T_ENTER + 13.0):     # her stumbles
        add(t, 0.4, 'D2', 104, 'stumble')
    # guilt: she tears away; the love sinks to a tender cello
    for j, m in enumerate(('A5', 'Bb5', 'A5', 'Ab5', 'G5')):
        add(T_GUILT + 0.12 * j, 0.15, m, 104 - 4 * j, 'shriek')
    add(T_GUILT, 0.5, 'D2', 116, 'stumble')
    for t, m, v, d in play('twins_love', T_TENDER, TBEAT, -12, 86, 'melody'):
        add(t, d, m, v, 'tender')
    for b0, ch in ((0, ('F2', 'C3', 'A3')), (6, ('Bb1', 'F2', 'D3')), (12, ('Eb2', 'Bb2', 'G3'))):
        for m in ch:
            add(T_TENDER + b0 * TBEAT, 6 * TBEAT * 1.05, m, 60, 'pad')
    add(T_GUILT, HORNS[0] - T_GUILT, 'D1', 64, 'pedal')

    # Hunding's horns, far off at the end of Right; his motif in the tubas; she runs again
    for k, th in enumerate(HORNS + [T_LAST]):
        for b, d, m in HORN_CALL:
            add(th + b * 0.32, d * 0.32, m, (78 + 8 * k) if th < T_LAST else 62, 'call', k)
    for b, d, m in HUNDING:
        add(T_HUND + b * 0.55, d * 0.55, m, 108, 'hunding')
        add(T_HUND + 3.3 + b * 0.5, d * 0.5, m, 116, 'hunding')
    for i, t in enumerate(np.arange(HORNS[0] + 1.5, T_DOGS, 0.14)):
        add(t, 0.14, note(GALLOP[i % 6]) - 2 + 3 * (i // 36), 80 + int(26 * (t - HORNS[0]) / 14), 'gallop', i)
    add(HORNS[0], T_DEATH - HORNS[0], 'D2', 76, 'trem')
    add(0.0, T_ENTER + 2.0, 'D2', 80, 'trem')

    # the hounds: six of them, each a shriek and a snarl
    for k in range(6):
        td = T_DOGS + 0.9 * k
        add(td, 0.2, note('Eb6') - k, 108, 'yelp', k)
        add(td + 0.05, 0.6, note('D2') + (k % 3), 104, 'snarl', k)
    add(T_DOGS, T_DEATH - T_DOGS, 'D3', 92, 'trill')
    # Siegmund dying, in her vision: the Volsungs' fate in the brass
    for t, m, v, d in play('volsung_fate', T_DEATH, FBEAT, 0, 112):
        add(t, d, m, v, 'fate' if m >= note('C3') else 'fatebass')
    add(T_DEATH, 0.8, 'C2', 124, 'crash')
    # she faints: a falling clarinet; he watches over her
    for j, m in enumerate(('E5', 'D5', 'C5', 'A4', 'F4', 'D4', 'A3')):
        add(T_FAINT + 0.32 * j, 0.6, m, 86 - 5 * j, 'fall')
    add(T_FAINT + 2.4, 1.4, 'D2', 90, 'thud')
    for t, m, v, d in play('twins_love', T_WATCH + 0.5, 0.75, -12, 92, 'melody'):
        if t < D - 1.5:
            add(t, d, m - 12, v, 'solo')
    for m in ('F1', 'C2', 'A2', 'F3'):
        add(T_WATCH, D - T_WATCH, m, 66, 'pad')
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
    """Per frame: Sieglinde, Siegmund and Brünnhilde (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    rend = at(G, 'Right', 1.0) + 30
    keys_l = [(0, rend), (T_ENTER, rend), (T_ENTER + 2.2, at(G, 'Right', 0.7)), (T_ENTER + 3.4, at(G, 'Right', 0.62)),
              (T_ENTER + 5.6, at(G, 'Right', 0.3)), (T_ENTER + 7.0, at(G, 'Right', 0.25)),
              (T_ENTER + 9.4, at(G, 'Porch Right', 0.7)), (T_ENTER + 10.8, at(G, 'Porch Right', 0.62)),
              (T_ENTER + 13.0, at(G, 'Porch Right', 0.1)), (T_GUILT, at(G, 'Porch Front', 0.75)),
              (T_GUILT + 1.0, at(G, 'Porch Front', 0.5)), (HORNS[0], at(G, 'Porch Front', 0.35)),
              (HORNS[1], at(G, 'Porch Front', 0.1)), (HORNS[2], at(G, 'Porch Left', 0.5)),
              (HORNS[3], at(G, 'Left', 0.95)), (T_DOGS, at(G, 'Left', 0.85)), (T_FAINT, at(G, 'Left', 0.82)),
              (T_FAINT + 2.4, at(G, 'Left', 0.7)), (D, at(G, 'Left', 0.7))]
    keys_m = [(0, rend), (T_ENTER + 1.2, rend), (T_ENTER + 3.0, at(G, 'Right', 0.8)),
              (T_ENTER + 6.5, at(G, 'Right', 0.4)), (T_ENTER + 10.5, at(G, 'Right', 0.05)),
              (T_ENTER + 14.0, at(G, 'Porch Right', 0.35)), (T_GUILT + 1.0, at(G, 'Porch Front', 0.85)),
              (T_TENDER + 6.0, at(G, 'Porch Front', 0.65)), (HORNS[1], at(G, 'Porch Front', 0.3)),
              (HORNS[3], at(G, 'Porch Left', 0.3)), (T_DOGS, at(G, 'Left', 0.95)), (T_FAINT, at(G, 'Left', 0.9)),
              (T_FAINT + 2.4, at(G, 'Left', 0.72)), (T_WATCH + 2, at(G, 'Left', 0.55)), (D, at(G, 'Left', 0.55))]

    def track(keys):
        ts = [k[0] for k in keys]
        vs = [k[1] for k in keys]
        return np.interp(t, ts, vs)
    sl = follow(track(keys_l), np.full(F, 3.0))
    lurch = np.where((t > T_GUILT) & (t < T_TENDER + 8), 10 * np.sin(2 * np.pi * 2.3 * t) * np.sin(2 * np.pi * 0.37 * t), 0.0)
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
    L = G.length
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    bed = pass_bed(G)
    C = choreography(G)
    N = compose()
    rend = at(G, 'Right', 1.0)

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def last(ev, t):
        i = int(np.searchsorted([e[0] for e in ev], t, side='right')) - 1
        return (ev[i], t - ev[i][0]) if i >= 0 else (None, 99.0)

    love_ev = ons('love', 'tender', 'solo')
    gallop_ev = ons('gallop')
    call_on = HORNS + [T_LAST]
    hund_ev = ons('hunding')
    fate_on = sorted({e[0] for e in ons('fate')})
    flick = Flicker(rng, G.N, 3.0, 9.0)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    gap = rng.uniform(0, 1, 64)
    shards = rng.uniform(-1, 1, 24)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = np.zeros((G.N, 3))
        fear = smoothstep(HORNS[0] - 1, HORNS[0] + 2, t) * (1 - smoothstep(T_FAINT, T_WATCH, t))
        vision = smoothstep(T_DOGS - 0.5, T_DOGS + 1.0, t) * (1 - smoothstep(T_FAINT - 0.5, T_FAINT + 2.0, t))
        fr += bed(T, 1 - 0.25 * fear - 0.35 * vision, 1 - 0.2 * fear - 0.4 * vision)
        ln, mn = C['linde'][f], C['mund'][f]

        # the flight: the gallop as a run of pulses racing along the house ahead of them
        flight = smoothstep(T_ENTER - 1, T_ENTER + 1, t) * (1 - smoothstep(T_GUILT, T_GUILT + 1.5, t))
        flight += smoothstep(HORNS[0] + 1.5, HORNS[0] + 3, t) * (1 - smoothstep(T_DOGS, T_DOGS + 1, t))
        if flight > 0:
            e, age = last(gallop_ev, t)
            beat = np.exp(-age / 0.1) if e is not None else 0.0
            stripes = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 120 + 2.2 * T))) ** 4
            near = np.exp(-((d - ln) / 400) ** 2)
            fr += light(SIEGLINDE, flight * (0.3 + 0.2 * beat) * stripes * near)
            fr += light(SIEGMUND, flight * (0.25 + 0.15 * beat) * stripes * np.exp(-((d - mn) / 400) ** 2))

        # Hunding's horns: red flashes at the end of Right, nearer each time; his motif darkens Right
        for k, th in enumerate(call_on):
            if th <= t < th + 2.5:
                a = np.exp(-(t - th) / 0.6) * (0.6 if th == T_LAST else 1.0)
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
            for k in range(6):
                td = T_DOGS + 0.9 * k
                if td <= t < td + 4.0:
                    u = (t - td) / 3.0
                    p = rend + (ln + 30 - rend) * min(u, 1.0) ** 0.8 + 8 * np.sin(2 * np.pi * 6 * t + k)
                    a = 1 - smoothstep(0.9, 1.25, u)
                    fr += light(DOG, a * np.exp(-((d - p) / 14) ** 2))
                    fr += light(WHITE, 0.35 * a * np.exp(-((d - p + 6) / 4) ** 2))
                    wake = (d > p) & (d < p + 160)
                    fr = fr * (1 - 0.5 * a * wake)[:, None]
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

        # Sieglinde: wild flicker in her guilt and terror; she falls and lies dim
        e, age = last(love_ev, t)
        sing = np.exp(-age / 0.3) if e is not None and age < 2 else 0.0
        entered = smoothstep(T_ENTER - 0.2, T_ENTER + 0.8, t)
        wild = smoothstep(T_GUILT - 0.3, T_GUILT + 0.3, t) * (1 - smoothstep(T_TENDER + 4, T_TENDER + 8, t)) + 0.7 * fear
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
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    for name, gain, rev in (('low', 0.18, 0.2), ('brass', 0.17, 0.3), ('horns', 0.15, 0.5),
                            ('strings', 0.16, 0.3), ('winds', 0.15, 0.35), ('perc', 0.2, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vas = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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

    def pl(t):
        return pan_at(np.interp(t, C['t'], C['linde']))

    def pm(t):
        return pan_at(np.interp(t, C['t'], C['mund']))

    rend = pan_at(at(G, 'Right', 1.0))
    for t, d, m, v, part, k in compose():
        if part == 'gallop':
            M.add('strings', (vas if k % 2 else vcs).play(m, v), t, 0.7, 0.5 * (pl(t) + pm(t)) + (0.15 if k % 2 else -0.15))
        elif part == 'love':
            M.add('strings', vn.play(m, v, dur=d * 1.05, release=0.2), t, 0.8, pl(t))
            M.add('winds', ob.play(m, v - 12, dur=d * 1.05, release=0.2), t, 0.6, pl(t))
        elif part == 'lovebass':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.7, pm(t))
        elif part == 'stumble':
            M.add('perc', timp.play(v, pitch=-2), t, 0.8, pl(t))
            M.add('low', cb.play(m, v, dur=d, release=0.2), t, 0.6, pl(t))
        elif part == 'shriek':
            M.add('winds', ob.play(m - 12, v, dur=d, release=0.1), t, 0.9, pl(t))
        elif part == 'tender':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pm(t))
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.8, fall=1.2, gain=0.65)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.5, fall=1.0)
        elif part == 'call':
            M.add('horns', mute.play(m, v, dur=d * 1.05, release=0.5), t, 0.9 if k < 4 else 0.5, rend)
        elif part == 'hunding':
            M.add('brass', tuba.play(m + 12, v, dur=d * 1.05, release=0.2), t, 1.0, rend)
            M.add('brass', tbn.play(m + 12, v - 14, dur=d * 1.05, release=0.2), t, 0.5, rend)
            if d >= 0.5:
                M.add('perc', timp.play(v - 10, pitch=-2), t, 0.6, rend)
        elif part == 'trem':
            hold('low', trem, m, t, t + d, v, 0.0, rise=2.0, fall=1.0, gain=0.7)
        elif part == 'yelp':
            p = pan_at(np.interp(t + 1.2, [T_DOGS, T_DOGS + 3], [at(G, 'Right', 1.0), np.interp(t, C['t'], C['linde'])]))
            M.add('winds', pic.play(m - 12, v), t, 1.0, p)
            M.add('winds', pic.play(m - 13, v - 10), t + 0.1, 0.8, p)
        elif part == 'snarl':
            M.add('brass', tbn.play(m + 12, v, dur=d, release=0.1), t, 0.6, rend * 0.7)
            M.add('perc', whoosh(2.4, 2500, 600, 0.3, seed=20 + k), t, 0.5, rend * (1 - 0.3 * k))
        elif part == 'trill':
            for i, tt in enumerate(np.arange(t, t + d, 0.09)):
                M.add('low', vcs.play(m - 12 + (i % 2), 92), tt, 0.5, -0.2 + 0.4 * (i % 2))
        elif part == 'fate':
            s = horn if m >= note('G3') else tbn
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d * 1.05, release=0.5), t, 0.8, pm(t))
        elif part == 'fatebass':
            M.add('brass', tuba.play(m + (12 if m < note('E2') else 0), v, dur=d * 1.05, release=0.5), t, 0.8, pm(t))
        elif part == 'crash':
            M.add('perc', crash.play(120), t, 0.9, pm(t))
            M.add('perc', gong.play(116), t, 0.8, pm(t))
        elif part == 'fall':
            M.add('winds', cl.play(m - 12, v, dur=d, release=0.3), t, 0.9, pl(t))
        elif part == 'thud':
            M.add('perc', roll.play(v, dur=d), t - 0.8, 0.5, pl(t))
            M.add('low', cb.play(m + 12, v, dur=d, release=0.6), t, 0.8, pl(t))
        elif part == 'solo':
            M.add('strings', vc.play(m + 12, v, dur=d * 1.05, release=0.5), t, 1.1, pm(t))
