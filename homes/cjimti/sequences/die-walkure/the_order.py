"""The Order: Wotan rises out of his grief and gives the command Fricka has forced on him. Brünnhilde is to
fight for Hunding, and Siegmund must fall. His spear motif (Donington 73) strides down in trombones and tubas,
and with every step of it a steel line drives out from him across the porch toward Right, where a lone Wälsung
blue spark flickers; at the bottom of the scale the line reaches it and the spark goes out, while Hunding's
heavy motif (composed: dotted tubas on D) smoulders blood red at the free end of Right.

Brünnhilde protests: her own motif (Donington 88) rises twice in the horns, faster and higher, and her silver
presses in along Porch Front against his blue, the light of the porch split between them. His answer is his
grief (Donington 82) on the trombones, and then his fury: a storm of blue. The storm figure (Donington 74) tears
up through the low strings, the spear motif hammers in the tubas, timpani roll and cymbals crash, blue lightning
runs from him out to both ends of the house and blue waves sweep the roof while she is driven back. Then he
storms off, a streak of blue with a long trail back along Porch Left, the length of Left and out along Side to
its far end, thunder at every corner.

She is left alone. The Valkyries' motif (Donington 22), which should gallop, comes heavy and slow in low horns
and trombones, and on each of its chords a weapon gathers to her: gold glints, a gold shield at her side, the
steel of her spear. She takes them up to one last high horn, and withdraws slowly to watch from the heights at
the front of Porch Right, the dawn and the slate of the pass settling round her.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody

CODE = 'WK14'
TITLE = 'The Order'
KIND = 'show'
DESCRIPTION = ('Wotan gives the order: Brünnhilde must fight for Hunding, and Siegmund must die. '
               'She refuses, and his fury breaks over the whole house like a storm before he storms away. '
               'Alone, she takes up her weapons, slowly, and goes to watch.')
VOICEOVER = ('He gives the order that breaks his own heart. '
             'And for the first time in her life, his daughter says no.')

BEAT = 0.75
T_RISE = 0.5                                # he rises out of his grief
T_SPEAR = 3.5                               # the order: the spear motif
SBEAT = 0.6
T_HUND = 8.8                                # Hunding's motif at the end of Right
T_PROTEST = [12.5, 16.8]                    # her motif, twice
T_GRIEF = 21.0                              # his grief, briefly
T_FURY = 25.5                               # the storm of blue
BOLTS = [26.0, 27.6, 29.0, 30.6, 32.0, 33.4, 35.0]
T_OFF = 38.0                                # he storms off along Side
T_GONE = 44.5
T_ALONE = 46.0                              # the Valkyries' motif, slow and heavy
VBEAT = 0.95
T_ARMED = 58.0
T_WITHDRAW = 66.0
T_SETTLE = 74.0
D = 80.0
K = 13
GLINTS = (-24, -9, 10, 23)

HUNDING = [(0, .75, 'D2'), (.75, .25, 'D2'), (1, 1, 'F2'), (2, .75, 'E2'), (2.75, .25, 'E2'), (3, 1, 'Db2'),
           (4, 2, 'D2')]                     # composed: Hunding, a heavy dotted tuba figure

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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    # he rises: a low swell under him
    for i, m in enumerate(('Bb1', 'F2', 'Bb2')):
        add(T_RISE + 0.3 * i, T_SPEAR - T_RISE + 0.2, m, 70 + 10 * i, 'swell')
    # the order: the spear motif, full
    for i, (t, m, v, d) in enumerate(play('spear', T_SPEAR, SBEAT, 0, 118)):
        add(t, d, m, v, 'spear', i)
    for m in ('Bb1', 'Bb2', 'D3', 'F3'):
        add(T_SPEAR, 2 * SBEAT, m, 100, 'chord')
    for m in ('E1', 'E2', 'B2', 'G3'):
        add(T_SPEAR + 9 * SBEAT, 3 * SBEAT, m, 96, 'chord')
    for b, d, m in HUNDING:
        add(T_HUND + b * 0.5, d * 0.5, m, 104, 'hunding')
    add(T_HUND, 0.5, 'D2', 100, 'timp')
    add(T_HUND + 2.0, 0.5, 'D2', 104, 'timp')

    # her protest, twice, higher and faster
    for j, t0 in enumerate(T_PROTEST):
        for t, m, v, d in play('brunnhilde', t0, 0.5 - 0.05 * j, 2 * j, 92 + 10 * j, 'melody'):
            add(t, d, m, v, 'brunn', j)
        for m in (('F2', 'C3', 'A3', 'Eb4'), ('G2', 'D3', 'B3', 'F4'))[j]:
            add(t0, 4.0 - 0.3 * j, m, 70, 'pad')
    # his grief
    for b, d, m in melody('wotan_grief'):
        if b < 11:
            add(T_GRIEF + b * 0.4, min(d, 11 - b) * 0.4, m - 12, 90, 'grief')
    for m in ('E2', 'B2', 'G3'):
        add(T_GRIEF, 4.4, m, 64, 'pad')

    # the fury: storm figure in the low strings, the spear in the tubas, bolts with timpani and cymbal
    for r in range(4):
        for t, m, v, d in play('storm', T_FURY + r * 3.2, 0.27, 0, 104 + 4 * r):
            if t < T_OFF:
                add(t, d, m, v, 'storm')
    for t, m, v, d in play('spear', T_FURY + 1.0, 0.75, -12, 124):
        add(t, d, m, v, 'spearlow')
    for t, m, v, d in play('spear', T_FURY + 1.0, 0.75, 0, 116):
        add(t, d, m, v, 'spearhi')
    for k, tb in enumerate(BOLTS):
        add(tb, 1.0, 'D2', 120, 'bolt', k)
    for k, (s, _) in enumerate(((T_OFF + 0.0, 'Porch Left'), (T_OFF + 1.5, 'Left'), (T_OFF + 3.4, 'Side'))):
        add(s, 2.0, 'D1', 110 - 12 * k, 'thunder', k)

    # alone: the Valkyries' motif, heavy and slow; one last high horn as she takes up her arms
    for t, m, v, d in play('valkyries', T_ALONE, VBEAT, -12, 88):
        add(t, d * 1.1, m, v, 'valk' if m >= note('G3') else 'valklow')
    add(T_GONE - 2.0, T_ALONE - T_GONE + 2.0 + 12 * VBEAT, 'B1', 80, 'pedal')
    add(T_GONE - 1.0, T_ALONE - T_GONE + 1.0 + 4 * VBEAT, 'B2', 66, 'pedal')
    for t, m, v, d in play('brunnhilde', T_ARMED, 0.75, 0, 96, 'melody'):
        add(t, d, m, v, 'brunn', 2)
    for m in ('F2', 'C3', 'Eb3', 'A3'):
        add(T_ARMED, 6.0, m, 66, 'pad')
    # she withdraws: a single horn, far off, and the pass settles
    for t, m, v, d in play('brunnhilde', T_WITHDRAW + 1.0, 1.0, -5, 70, 'melody'):
        if t < T_WITHDRAW + 6.0:
            add(t, d, m, v, 'brunn', 3)
    for m in ('C2', 'G2', 'Eb3'):
        add(T_WITHDRAW, D - T_WITHDRAW, m, 56, 'pad')
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
    """Per frame: Wotan, Brünnhilde (path distance), and how far the spear's line reaches."""
    F = nframes(D)
    t = np.arange(F) * DT
    w0 = at(G, 'Porch Front', 0.4)
    wot = np.full(F, w0)
    run = (t >= T_OFF) & (t < T_GONE)
    u = smoothstep(T_OFF, T_GONE - 0.5, t)
    wot = np.where(t >= T_OFF, w0 * (1 - u ** 1.3) - 60 * smoothstep(T_GONE - 1.0, T_GONE, t), wot)
    tb = np.full(F, at(G, 'Porch Front', 0.62))
    tb[(t >= T_PROTEST[0])] = at(G, 'Porch Front', 0.55)
    tb[(t >= T_PROTEST[1])] = at(G, 'Porch Front', 0.5)
    tb[(t >= T_FURY)] = at(G, 'Porch Front', 0.72)
    tb[(t >= T_ALONE)] = at(G, 'Porch Front', 0.62)
    tb[(t >= T_WITHDRAW)] = at(G, 'Porch Right', 0.85)
    rate = np.where(t >= T_WITHDRAW, 0.55, np.where((t >= T_FURY) & (t < T_FURY + 3), 4.0, 1.5))
    br = follow(tb, rate)
    shake = np.where((t > T_FURY) & (t < T_OFF), 6 * np.sin(2 * np.pi * 7 * t), 0.0)
    return dict(t=t, wotan=wot, brunn=br + shake, run=run)


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
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
    hund_ev = ons('hunding')
    brunn_ev = ons('brunn')
    wot_ev = ons('spear', 'grief', 'spearhi')
    valk_on = sorted({e[0] for e in ons('valk')})
    storm_ev = ons('storm')
    tw = Flicker(rng, G.N, 2.0, 7.0)
    targets = []                            # each bolt runs out to a different place on the house
    for k in range(len(BOLTS)):
        targets.append([at(G, 'Side', 0.1 + 0.1 * (k % 3)), at(G, 'Right', 0.95 - 0.08 * (k % 4))][k % 2])
    jag = rng.uniform(-1, 1, (len(BOLTS), 64))
    sparks = rng.uniform(0, L, 40)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = np.zeros((G.N, 3))
        fury = smoothstep(T_FURY - 0.5, T_FURY + 0.5, t) * (1 - smoothstep(T_GONE - 1.5, T_ALONE + 2.0, t))
        order = smoothstep(T_SPEAR - 0.5, T_SPEAR + 1.0, t) * (1 - smoothstep(T_PROTEST[0], T_PROTEST[0] + 3, t))
        lone = smoothstep(T_GONE - 1, T_ALONE + 2, t) * (1 - smoothstep(T_ARMED + 2, T_SETTLE, t))
        fr += bed(T, 1 - 0.55 * fury - 0.25 * order - 0.3 * lone, 1 - 0.6 * fury - 0.2 * order - 0.4 * lone)
        wp = C['wotan'][f]

        # the order: a steel line out from him, a step for every note of the spear's descent
        if T_SPEAR <= t < T_PROTEST[0] + 2.0:
            e, age = last(spear_ev, t)
            k = e[5] + smoothstep(0, 0.25, age)
            reach = (hero - w0) * min(k / 11, 1.0)
            fade = 1 - smoothstep(T_SPEAR + 10 * SBEAT + 0.3, T_SPEAR + 10 * SBEAT + 2.5, t)
            span = smoothstep(w0 - 5, w0 + 10, d) * smoothstep(w0 + reach + 15, w0 + reach - 15, d)
            fr += light(SPEAR, fade * (0.3 + 0.3 * np.exp(-age / 0.25)) * span * np.exp(-np.clip(d - w0 - reach + 60, 0, None) / 400))
            fr += light(WHITE, fade * 0.7 * np.exp(-age / 0.2) * np.exp(-((d - w0 - reach) / 18) ** 2))
            # the Wälsung spark, until the spear reaches it
            alive = 1 - smoothstep(T_SPEAR + 10 * SBEAT, T_SPEAR + 10 * SBEAT + 0.15, t)
            sp = hero + 15 * np.sin(2 * np.pi * t / 1.7)
            fr += light(SIEGMUND, 0.75 * alive * smoothstep(T_SPEAR, T_SPEAR + 1, t) * np.exp(-((d - sp) / 16) ** 2))
            snuff = T_SPEAR + 10 * SBEAT
            if t >= snuff:
                fr += light(WHITE, 0.8 * np.exp(-(t - snuff) / 0.2) * np.exp(-((d - hero) / 50) ** 2))
        # Hunding smoulders at the free end of Right
        if T_HUND - 0.5 <= t < T_PROTEST[1]:
            e, age = last(hund_ev, t)
            pulse = np.exp(-age / 0.3) if e is not None else 0.0
            h = smoothstep(T_HUND - 0.5, T_HUND + 0.5, t) * (1 - smoothstep(T_PROTEST[0], T_PROTEST[1], t))
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

        # the fury: blue waves over the whole house, bolts out to both ends
        if fury > 0:
            e, age = last(storm_ev, t)
            surge = np.exp(-age / 0.15) if e is not None else 0.0
            wave = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - wp) / 260 - 1.1 * T))) ** 2
            fr += light(WOTAN, fury * (0.35 + 0.35 * wave + 0.12 * surge))
            for k, tb in enumerate(BOLTS):
                if tb <= t < tb + 0.7:
                    a = np.exp(-(t - tb) / 0.18)
                    tgt = targets[k]
                    lo, hi = min(wp, tgt), max(wp, tgt)
                    u = np.clip((d - lo) / (hi - lo), 0, 1)
                    zig = np.interp(u * 63, np.arange(64), jag[k])
                    inside = (d >= lo) & (d <= hi)
                    fr += light(BOLT, fury * a * (0.7 + 0.3 * zig) * inside)
                    fr += light(WHITE, fury * a * 0.8 * inside * (zig > 0.55))
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
        lvl = 0.52 + 0.4 * smoothstep(T_RISE, T_SPEAR, t) + 0.15 * voice + 0.15 * fury
        lvl *= 1 - smoothstep(T_GONE - 0.8, T_GONE, t)
        if lvl > 0.01:
            fr += light(WOTAN, lvl * np.exp(-((d - wp) / 22) ** 2) + 0.3 * lvl * np.exp(-((d - wp) / 80) ** 2))

        # Brünnhilde: alone, the weapons gather to her on the Valkyries' chords
        e, age = last(brunn_ev, t)
        flare = np.exp(-age / 0.35) if e is not None and age < 2 else 0.0
        b = C['brunn'][f]
        sad = smoothstep(T_GONE, T_ALONE, t) * (1 - smoothstep(T_ARMED, T_ARMED + 4, t))
        bl = 0.66 + 0.25 * flare - 0.2 * sad - 0.1 * fury
        fr += light(BRUNN, bl * np.exp(-((d - b) / 16) ** 2) + 0.22 * bl * np.exp(-((d - b) / 60) ** 2))
        for j, o in enumerate(GLINTS):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        if t >= T_ALONE:
            j = int(np.searchsorted(valk_on, t, side='right'))
            arms = min(j / len(valk_on), 1.0)
            hit = np.exp(-(t - valk_on[j - 1]) / 0.4) if j else 0.0
            shield = smoothstep(0.15, 0.5, arms)
            spear = smoothstep(0.55, 0.95, arms)
            fr += light(BGOLD, (0.55 * shield + 0.35 * hit) * np.exp(-((d - b - 16) / 7) ** 2))
            line = smoothstep(b - 46, b - 40, d) * smoothstep(b - 12, b - 18, d)
            fr += light(SPEAR, (0.45 * spear + 0.2 * hit * spear) * line)
            if 0 < j:                         # each heavy chord: a slow wave of weight out from her over the house
                age = t - valk_on[j - 1]
                rad = 700 * age ** 0.7
                fr += light(BRUNN, 0.55 * np.exp(-age / 1.2) * np.exp(-((np.abs(d - b) - rad) / 90) ** 2))
                fr += light(BGOLD, 0.45 * np.exp(-age / 0.6) * np.exp(-((d - b) / 60) ** 2))
        if T_ARMED <= t < T_WITHDRAW + 1:     # she takes them up: gold sparks fly in to her from the whole house
            u = smoothstep(T_ARMED, T_ARMED + 5.0, t)
            q = sparks + (b - sparks) * u ** 1.5
            fade = 1 - smoothstep(T_ARMED + 4.5, T_ARMED + 5.5, t)
            g = np.exp(-((d[:, None] - q[None, :]) / 10) ** 2).max(axis=1)
            fr += light(BGOLD, 0.85 * fade * smoothstep(T_ARMED, T_ARMED + 0.5, t) * g * (0.6 + 0.4 * tw(t)))
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
    for name, gain, rev in (('low', 0.19, 0.2), ('brass', 0.18, 0.3), ('horns', 0.17, 0.38),
                            ('strings', 0.16, 0.3), ('perc', 0.21, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
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

    def pw(t):
        return pan_at(np.interp(t, C['t'], C['wotan']))

    def pb(t):
        return pan_at(np.interp(t, C['t'], C['brunn']))

    rend = pan_at(at(G, 'Right', 1.0))
    hold('strings', trem, note('Bb1'), T_FURY - 1.0, T_OFF + 2.0, 100, -0.2, rise=1.0, fall=2.0, gain=0.8)
    hold('strings', vtrem, note('D4'), T_FURY, T_OFF + 1.0, 90, 0.2, rise=0.5, fall=2.0, gain=0.5)
    M.add('perc', roll.play(110, dur=3.0), T_FURY - 1.0, 0.8, 0.0)
    for t, d, m, v, part, k in compose():
        if part == 'swell':
            hold('low', cb, m, t, t + d, v, pw(t), rise=1.5, fall=0.6, gain=0.9)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pw(t))
            M.add('brass', tuba.play(m - 12, v - 6, dur=d * 1.1, release=0.3), t, 0.8, pw(t))
        elif part == 'chord':
            s = tuba if m < note('C2') else (tbn if m < note('C3') else horn)
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d, release=0.6), t, 0.7, pw(t))
        elif part == 'hunding':
            M.add('brass', tuba.play(m + 12, v, dur=d * 1.05, release=0.2), t, 1.0, rend)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d * 1.05, release=0.2), t, 0.6, rend)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-2), t, 0.9, rend)
        elif part == 'brunn':
            M.add('horns', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pb(t))
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.6, fall=1.2, gain=0.7)
        elif part == 'grief':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pw(t))
        elif part == 'storm':
            M.add('low', cbs.play(m + 12, v), t, 0.9, -0.3)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.8, 0.3)
        elif part == 'spearlow':
            M.add('brass', tuba.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pw(t))
        elif part == 'spearhi':
            M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, pw(t))
            M.add('horns', horn.play(m + 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, pw(t))
        elif part == 'bolt':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, 0.0)
            if k % 2 == 0:
                M.add('perc', crash.play(118), t, 0.8, 0.6 * (-1) ** (k // 2))
            M.add('perc', whoosh(0.5, 3500, 600, 0.45, seed=k), t, 0.6, 0.6 * (-1) ** k)
        elif part == 'thunder':
            M.add('perc', gong.play(v) if k == 0 else timp.play(v, pitch=-7), t, 0.8, pw(t + 0.5))
            M.add('perc', roll.play(v - 10, dur=d), t, 0.6, pw(t + 0.5))
            M.add('perc', whoosh(1.2, 1500, 200, 0.4, seed=10 + k), t, 0.6, pw(t + 0.5))
        elif part == 'valk':
            M.add('horns', horn.play(m, v, dur=d, release=0.6), t, 0.8, pb(t))
            M.add('brass', tbn.play(m - 12, v - 10, dur=d, release=0.6), t, 0.6, pb(t))
        elif part == 'valklow':
            M.add('brass', tuba.play(m, v, dur=d, release=0.6), t, 0.7, pb(t))
        elif part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=1.5, fall=1.5)
    for t, d, m, v, part, k in compose():
        if part == 'brunn' and k == 3:
            M.add('horns', mute.play(m, v, dur=d, release=0.8), t + 0.02, 0.4, pb(t))
