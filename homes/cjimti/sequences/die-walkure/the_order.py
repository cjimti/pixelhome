"""The Order: Wotan rises out of his grief and gives the command Fricka has forced on him. Brünnhilde is to fight
for Hunding, and Siegmund must fall.

The music is Wagner's own: Act II, bars 1056 to 1103, from "Kennst du, Kind, meinen Zorn?" through "Siegmund
falle! Dies sei der Walküre Werk!" to the storm in the orchestra as he rushes away, as Solti's 1958 Vienna
Philharmonic recording takes it. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py):
the striding octaves of his threat on trombones, tuba and basses, the right hand on violins with flutes and
piccolo on top, his lines on trombones while he sings, and in the storm the left hand's surging chords on horns,
trombones and trumpets over cellos, basses and tuba; timpani, cymbals and a drum on its real accents. On top, the
stage's sounds: steel ringing on every step of the line he drives out, Hunding's smoulder crackling at the end
of Right, a thunderclap for every bolt of lightning, a blow and a shattering as the Wälsung's spark goes out,
the storm wind of his fury, and the wind and thunder of his going, corner by corner. While he sings the effects
keep low (the steel steps of his threat just under the brass), rise for the lightning of his hammer-blows, strike
with "Siegmund falle!", and from the storm on they lead.

"Kennst du, Kind, meinen Zorn?": with every striding octave of his threat a steel line drives out from him across
the porch toward Right, where a lone Wälsung blue spark flickers, and it stops just short. Hunding's blood red
smoulders at the free end of Right, and Brünnhilde's silver presses in along Porch Front against his blue, the
light of the porch split between them, pushing on every note. On each of his hammer-blows, "Wehe dem, den er
trifft!", blue lightning cracks from him out to the end of the house. "Siegmund falle!": the line thrusts home,
and the spark goes out in a flash of white. Then his fury: a storm of blue. Blue waves sweep the roof, lightning
runs from him out to both ends on every downbeat while she is driven back, and as the strings shriek he storms
off, a streak of blue with a long trail back along Porch Left, the length of Left and out along Side to its far
end, thunder at every corner, leaving her alone and dimmed, drawing back toward the heights of Porch Right.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK14'
TITLE = 'The Order'
KIND = 'show'
DESCRIPTION = ('Wotan gives the order: Brünnhilde must fight for Hunding, and Siegmund must die. '
               'When she pushes back, his fury breaks over the whole house like a storm, and he storms away '
               'and leaves her alone.')
VOICEOVER = ('He gives the order that breaks his own heart. '
             'And for the first time in her life, his daughter says no.')

EX = excerpt(__file__)                      # Act II, bars 1056-1103, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SUNG = [(t0, t1, who.lower()) for t0, t1, who, _ in EX['singing']]
T_SPEAR = BAR[1057]                         # "Kennst du, Kind, meinen Zorn?": the striding octaves
T_HUND = BAR[1063]                          # Hunding smoulders at the end of Right
T_PROTEST = [BAR[1063], BAR[1073]]          # her silver presses in against him
T_SNUFF = BAR[1081]                         # "Siegmund falle!"
T_FURY = BAR[1084]                          # the storm of blue
BOLTS = [BAR[b] for b in (1069, 1070, 1072, 1076)] + [BAR[b] for b in range(1088, 1097)]
T_OFF = BAR[1097]                           # he storms off along Side
T_GONE = BAR[1101]
K = 13
GLINTS = (-24, -9, 10, 23)

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
HUNDC = hexc('#8a0020')
BOLT = hexc('#6080ff')
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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The left hand's octaves of the
    threat are the spear's steps ('spear'); the right hand while she presses against him her pushes ('brunn'); the
    left hand in the storm 'storm'; every other note 'note'. who is whoever is singing."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if T_SPEAR <= t < BAR[1061] and hand == 1 and m < 48:
            part = 'spear'
        elif hand == 0 and (T_PROTEST[0] <= t < BAR[1068] or T_PROTEST[1] <= t < T_SNUFF):
            part = 'brunn'
        elif hand == 1 and T_FURY <= t < T_GONE:
            part = 'storm'
        else:
            part = 'note'
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
    """Per frame: Wotan, Brünnhilde (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    w0 = at(G, 'Porch Front', 0.4)
    wot = np.full(F, w0)
    run = (t >= T_OFF) & (t < T_GONE)
    u = smoothstep(T_OFF, T_GONE - 0.5, t)
    wot = np.where(t >= T_OFF, w0 * (1 - u ** 1.3) - 60 * smoothstep(T_GONE - 1.0, T_GONE, t), wot)
    tb = np.full(F, at(G, 'Porch Front', 0.62))
    tb[(t >= T_PROTEST[0])] = at(G, 'Porch Front', 0.55)
    tb[(t >= BAR[1068])] = at(G, 'Porch Front', 0.66)
    tb[(t >= T_PROTEST[1])] = at(G, 'Porch Front', 0.5)
    tb[(t >= T_SNUFF)] = at(G, 'Porch Front', 0.6)
    tb[(t >= T_FURY)] = at(G, 'Porch Front', 0.72)
    tb[(t >= T_GONE)] = at(G, 'Porch Right', 0.85)                          # she withdraws to the heights
    rate = np.where((t >= T_FURY) & (t < T_FURY + 3), 4.0, np.where(t >= T_GONE, 2.2, 1.5))
    br = follow(tb, rate)
    shake = np.where((t > T_FURY) & (t < T_OFF), 6 * np.sin(2 * np.pi * 7 * t), 0.0)
    return dict(t=t, wotan=wot, brunn=br + shake, run=run)


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    bed = pass_bed(G)
    C = choreography(G)
    N = compose()
    w0 = at(G, 'Porch Front', 0.4)
    hero = at(G, 'Right', 0.55)
    rend = at(G, 'Right', 1.0)

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def last(ev, t):
        i = int(np.searchsorted([e[0] for e in ev], t, side='right')) - 1
        return (ev[i], t - ev[i][0]) if i >= 0 else (None, 99.0)

    spear_ev = ons('spear')
    hund_ev = [e for e in N if e[4] == 'note' and e[2] < 48 and T_HUND <= e[0] < BAR[1068]]
    brunn_ev = ons('brunn')
    wot_ev = [e for e in N if e[5] == 'wotan']
    storm_ev = ons('storm')
    boil = np.array([(e[0], e[3]) for e in N if e[4] == 'note' and T_HUND <= e[0] < T_FURY and e[2] < 60])
    targets = []                            # each bolt runs out to a different place on the house
    for k in range(len(BOLTS)):
        targets.append([at(G, 'Side', 0.1 + 0.1 * (k % 3)), at(G, 'Right', 0.95 - 0.08 * (k % 4))][k % 2])
    jag = rng.uniform(-1, 1, (len(BOLTS), 64))

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = np.zeros((G.N, 3))
        fury = smoothstep(T_FURY - 0.5, T_FURY + 0.5, t) * (1 - smoothstep(T_GONE - 1.5, D - 0.5, t))
        order = smoothstep(T_SPEAR - 0.5, T_SPEAR + 1.0, t) * (1 - smoothstep(T_PROTEST[0], T_PROTEST[0] + 3, t))
        lone = smoothstep(T_GONE - 1, D, t)
        fr += bed(T, 1 - 0.55 * fury - 0.25 * order - 0.3 * lone, 1 - 0.6 * fury - 0.2 * order - 0.4 * lone)
        wp = C['wotan'][f]

        # the order: a steel line out from him, a step for every note of the spear's descent
        if T_SPEAR <= t < T_SNUFF + 2.5:
            e, age = last(spear_ev, t)
            k = spear_ev.index(e) + smoothstep(0, 0.25, age) if e is not None else 0.0
            reach = (hero - w0) * 0.82 * min(k / len(spear_ev), 1.0)
            if t >= T_SNUFF - 0.3:                                              # "Siegmund falle!": home
                age = t - T_SNUFF + 0.3
                reach = (hero - w0) * (0.82 + 0.18 * smoothstep(T_SNUFF - 0.3, T_SNUFF, t))
            elif age > 1.5:
                age = 1.5
            fade = 1 - smoothstep(T_SNUFF + 0.3, T_SNUFF + 2.5, t)
            span = smoothstep(w0 - 5, w0 + 10, d) * smoothstep(w0 + reach + 15, w0 + reach - 15, d)
            fr += light(SPEAR, fade * (0.3 + 0.3 * np.exp(-age / 0.25)) * span * np.exp(-np.clip(d - w0 - reach + 60, 0, None) / 400))
            fr += light(WHITE, fade * 0.7 * np.exp(-age / 0.2) * np.exp(-((d - w0 - reach) / 18) ** 2))
            # the Wälsung spark, until the spear reaches it
            alive = 1 - smoothstep(T_SNUFF, T_SNUFF + 0.15, t)
            sp = hero + 15 * np.sin(2 * np.pi * t / 1.7)
            fr += light(SIEGMUND, 0.75 * alive * smoothstep(T_SPEAR, T_SPEAR + 1, t) * np.exp(-((d - sp) / 16) ** 2))
            snuff = T_SNUFF
            if t >= snuff:
                fr += light(WHITE, 0.8 * np.exp(-(t - snuff) / 0.2) * np.exp(-((d - hero) / 50) ** 2))
        # Hunding smoulders at the free end of Right
        if T_HUND - 0.5 <= t < T_SNUFF:
            e, age = last(hund_ev, t)
            pulse = np.exp(-age / 0.3) if e is not None else 0.0
            h = smoothstep(T_HUND - 0.5, T_HUND + 0.5, t) * (1 - smoothstep(T_SNUFF - 2, T_SNUFF, t))
            fr = fr * (1 - 0.6 * h * np.exp(-((d - rend) / 160) ** 2))[:, None]
            fr += light(HUNDC, h * (0.6 + 0.5 * pulse) * np.exp(-((d - rend) / (50 + 30 * pulse)) ** 2))

        # her protest: the porch split between her silver and his blue, the line between them pushed toward him
        argue = smoothstep(T_PROTEST[0] - 0.5, T_PROTEST[0] + 1.0, t) * (1 - smoothstep(T_FURY - 0.5, T_FURY + 0.3, t))
        if argue > 0:
            bp = C['brunn'][f]
            mid = 0.5 * (bp + wp)
            e, age = last(brunn_ev, t)
            push = np.exp(-age / 0.4) if e is not None else 0.0
            side = 1 / (1 + np.exp(-(d - mid) / 18))
            fr += light(BRUNN, argue * (0.22 + 0.15 * push) * side * porch)
            fr += light(WOTAN, argue * 0.45 * (1 - side) * porch)
            fr += light(WHITE, argue * 0.5 * push * np.exp(-((d - mid) / 10) ** 2))

        # his rage boiling in him: a ripple of blue runs out from him both ways on every note of the left hand
        lo = int(np.searchsorted(boil[:, 0], t - 3.0))
        hi = int(np.searchsorted(boil[:, 0], t, side='right'))
        if hi > lo:
            age = t - boil[lo:hi, 0]
            amp = np.clip(boil[lo:hi, 1] / 90, 0, 1.3) * np.exp(-age / 1.1)
            rad = 380 * age
            g = np.exp(-((np.abs(d[:, None] - wp) - rad[None, :]) / 70) ** 2) * amp[None, :]
            fr += light(WOTAN, 0.6 * np.clip(g.sum(axis=1), 0, 1.4))

        # the fury: blue waves over the whole house, bolts out to both ends (his hammer-blows before it)
        if fury > 0:
            e, age = last(storm_ev, t)
            surge = np.exp(-age / 0.15) if e is not None else 0.0
            wave = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - wp) / 260 - 1.1 * T))) ** 2
            fr += light(WOTAN, fury * (0.35 + 0.35 * wave + 0.2 * surge))
        bf = max(fury, 0.9 * (t < T_FURY))
        for k, tb in enumerate(BOLTS):
            if tb <= t < tb + 0.7:
                a = np.exp(-(t - tb) / 0.18)
                tgt = targets[k]
                lo, hi = min(wp, tgt), max(wp, tgt)
                u = np.clip((d - lo) / (hi - lo), 0, 1)
                zig = np.interp(u * 63, np.arange(64), jag[k])
                inside = (d >= lo) & (d <= hi)
                fr += light(BOLT, bf * a * (0.7 + 0.3 * zig) * inside)
                fr += light(WHITE, bf * a * 0.8 * inside * (zig > 0.55))
                if t < tb + 0.08:
                    fr += light(WOTAN, 0.6)

        # storming off: his trail and thunder at each corner
        if T_OFF <= t < T_GONE + 2.0:
            for j, lag in enumerate(range(3, 45, 3)):
                q = C['wotan'][max(f - lag, 0)]
                fr += light(WOTAN, 0.8 * (1 - j / 14) * np.exp(-((d - q) / 30) ** 2) * (t - lag * DT < T_GONE))
            for k, tc in enumerate((T_OFF, T_OFF + 1.5, T_OFF + 3.4)):
                if tc <= t < tc + 1.0:
                    seg = ('Porch Left', 'Left', 'Side')[k]
                    fr += light(BOLT, 0.55 * np.exp(-(t - tc) / 0.3) * (G.seg_of == seg))

        # Wotan: risen, blazing in the fury, gone after he storms off
        e, age = last(wot_ev, t)
        voice = np.exp(-age / 0.4) if e is not None and age < 2 else 0.0
        lvl = 0.52 + 0.4 * smoothstep(0.0, T_SPEAR, t) + 0.15 * voice + 0.15 * fury
        lvl *= 1 - smoothstep(T_GONE - 0.8, T_GONE, t)
        if lvl > 0.01:
            fr += light(WOTAN, lvl * np.exp(-((d - wp) / 22) ** 2) + 0.3 * lvl * np.exp(-((d - wp) / 80) ** 2))

        # Brünnhilde: alone, the weapons gather to her on the Valkyries' chords
        e, age = last(brunn_ev, t)
        flare = np.exp(-age / 0.35) if e is not None and age < 2 else 0.0
        b = C['brunn'][f]
        sad = smoothstep(T_GONE, D, t)
        bl = 0.66 + 0.25 * flare - 0.2 * sad - 0.1 * fury
        fr += light(BRUNN, bl * np.exp(-((d - b) / 16) ** 2) + 0.22 * bl * np.exp(-((d - b) / 60) ** 2))
        for j, o in enumerate(GLINTS):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: the full brass for his threat and his storm."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    o = Orchestra(M, level=1.8)

    def size(t):
        return 1.0 if t < BAR[1063] or t >= T_FURY or BAR[1068] <= t < BAR[1073] else 0.55

    def role(t, d, m, v, hand):
        if T_SPEAR <= t < BAR[1061] and hand == 1:                             # the striding octaves
            return [('trombones', 12 if m < 48 else 0, 6, 0.85), ('tuba', 0 if m < 48 else -12, 0, 0.6),
                    ('basses', 0 if m < 48 else -12, 0, 0.5)]
        if singer(t) == 'wotan' and hand == 1 and t < T_FURY and m >= 48 and d >= 0.3:
            return [('trombones', 0, 0, 0.8), ('horns', 0, -6, 0.5)]
        return None

    def pan(t, m):
        return pan_at(np.interp(t, C['t'], C['wotan'])) * 0.7

    o.tutti(EX['notes'], size=size, role=role, pan=pan)
    for k, tb in enumerate(BOLTS):
        o.hit('timpani', tb, 112, pitch=-4, gain=0.5)
        if k in (1, 4, 8):
            o.hit('crash', tb, 108, gain=0.5)
    o.hit('crash', T_SNUFF, 110, gain=0.5, pan=pan_at(at(G, 'Right', 0.55)))
    o.hit('timpani roll', T_FURY, 100, gain=0.5)
    for k, tc in enumerate((T_OFF, T_OFF + 1.5, T_OFF + 3.4)):                 # thunder at every corner
        p = pan_at(at(G, ('Porch Left', 'Left', 'Side')[k], 0.5))
        o.hit('bass drum', tc, 115 - 8 * k, gain=0.6, pan=p)
        o.hit('timpani', tc, 110 - 8 * k, pitch=-7, gain=0.5, pan=p)

    # the stage: what the lights show, heard
    N = compose()
    fxhit = lambda name, t, v, g, p: o.hit(name, t, v, gain=g, pan=p, fx=True)       # a stage hit, on the fader
    pr = pan_at(at(G, 'Right', 0.55))
    for k, t in enumerate(e[0] for e in N if e[4] == 'spear'):                  # each step of the steel line
        p = pan(t, 0) + (pr - pan(t, 0)) * min(1.0, k / 12)
        fxhit('metal', t, 110, 0.7, p)
        fxhit('anvil', t, 104, 0.5, p)
    o.fire(T_HUND, T_FURY, 0.25, pan=0.85, crackle=4)                          # Hunding's smoulder at the end of Right
    for k, tb in enumerate(BOLTS):                                              # every bolt cracks and rolls
        tgt = [at(G, 'Side', 0.1 + 0.1 * (k % 3)), at(G, 'Right', 0.95 - 0.08 * (k % 4))][k % 2]
        o.thunder(tb, 0.9 if tb < T_FURY else 0.7 + 0.3 * (k % 2), pan_at(tgt), 0.7 if tb >= T_FURY else 0.85)
    o.boom(T_SNUFF, pr, 0.9)                                                    # "Siegmund falle!": the line thrusts home
    o.shatter(T_SNUFF + 0.05, pr, 0.6)
    o.wind(T_FURY, T_GONE + 1.0, lambda tt: 0.6 + 0.4 * smoothstep(T_FURY, T_OFF, tt), pan=0.0)   # the storm of blue
    wpan = lambda t: pan_at(np.clip(np.interp(t, C['t'], C['wotan']), 0, G.length))
    o.wind(T_OFF - 0.3, T_GONE + 0.8, 1.0, pan=wpan, seed=21)                   # he rushes away along Side
    for k, tc in enumerate((T_OFF, T_OFF + 1.5, T_OFF + 3.4)):
        o.thunder(tc, 0.95 - 0.25 * k, pan_at(at(G, ('Porch Left', 'Left', 'Side')[k], 0.5)), 1.0 - 0.15 * k)
    # he sings almost without a break until the storm: the effects keep low under his threat, rise for his
    # hammer-blows ("Wehe dem, den er trifft!"), drop again, strike with "Siegmund falle!" (the blow and the
    # shattering cut through), and from the storm on they lead
    o.effects([(0.0, -9), (9.7, -9), (10.4, -5), (12.8, -5), (13.2, -12), (26.4, -12), (26.9, -4), (35.0, -4),
               (35.5, -12), (45.8, -12), (46.1, -1), (47.4, -1),
               (47.9, -12), (50.5, -12), (51.4, 0)])
