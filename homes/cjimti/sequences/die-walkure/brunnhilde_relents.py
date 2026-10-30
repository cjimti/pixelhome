"""Brünnhilde Relents: the indigo of the Annunciation still holds the pass, her silver over Porch Front and her
pale gaze lying along Left. Siegmund asks if Sieglinde will come with him to Valhalla. His question rises in
the cellos to the love of the twins (Donington 37) and his blue reaches out to her amber; the answer is the
power of fate (Donington 84) low in the tubas, and a cold pale wave runs down her gaze: no. Then let Valhalla
keep its joys: Siegmund's own motif (Donington 35) swells in the horns and his blue pushes the indigo back off
Left and up Porch Left. She warns him: his sword will fail him. The fate chords fall again, lower, and Nothung's
glint dims.

He raises Nothung over Sieglinde, to kill them both rather than leave her: the sword's motif (Donington 43)
shrieks on the trumpet over trembling violins and a timpani roll, and the white steel blade lengthens over her
amber, hotter with every note. "Halt!": a silver blast tears from Brünnhilde down the porch to him, the indigo
shatters with a crash, and she breaks. She will give him victory. The Ride (Donington 47) bursts out in the
horns, twice, the love of the twins sweeps up in the strings, the slate and the dawn of the pass come flooding
back under a shower of gold, and her silver blazes. Then she is gone, a streak of silver with a long trail along
the porch and out at the free end of Right, the Ride whirling after her. Siegmund bends to Sieglinde, his blue
brushing her amber, and goes to meet his fight as the light greys and the first thunder rolls far off.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody

CODE = 'WK17'
TITLE = 'Brünnhilde Relents'
KIND = 'show'
DESCRIPTION = ('Siegmund will not go to Valhalla without Sieglinde, and he would rather kill them both than leave '
               'her behind. Moved by his love, Brünnhilde breaks her father\'s order and promises him victory.')
VOICEOVER = ('Heaven is offered to him, and he turns it down for her. '
             'And the goddess who came to take him is moved to tears.')

BEAT = 0.75
T_ASK = 1.0                                 # will she come?
T_NO = 6.5                                  # fate, low: no
T_DEFY = 12.5                               # then let Valhalla keep its joys
T_WARN = 22.0                               # your sword will fail you
T_RAISE = 29.5                              # he raises Nothung over her
T_HALT = 40.0                               # "Halt!"
T_RIDE = [41.0, 44.6]                       # she promises victory: the Ride, twice
RBEAT = 0.4
T_LOVE = 48.5                               # the twins' love, broad
T_FLY = 60.5                                # she flies off to the battle
T_GONE = 64.5
T_BEND = 67.0                               # he bends to Sieglinde, then goes
T_THUNDER = [71.5, 76.0]
D = 80.0
K = 16
GLINTS = (-24, -9, 10, 23)

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
INDIGO = hexc('#2a1a5a')
PALE = hexc('#a0b0c0')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
STORMDARK = hexc('#2a2e38')
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


def indigo_bed(G):
    """The hush of fate: indigo over the whole house, slow swells, pale motes drifting. f(T, level) -> (N,3)."""
    d = G.pd
    rng = np.random.default_rng(160)
    motes = rng.uniform(0, G.length, 26)
    speed = rng.uniform(-9, 9, 26)
    phase = rng.uniform(0, 2 * np.pi, 26)

    def f(T, lvl=1.0):
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 700 - T / 30))
        fr = light(INDIGO, lvl * (0.66 + 0.2 * swell))
        q = (motes + speed * T) % G.length
        a = (0.5 + 0.5 * np.sin(2 * np.pi * T / 5.0 + phase)) ** 2
        g = (a[None, :] * np.exp(-((d[:, None] - q[None, :]) / 9) ** 2)).max(axis=1)
        return fr + light(PALE, lvl * 0.5 * g)
    return f


def storm_bed(G):
    """Storm clouds over the pass: dark grey with grey-blue cloud banks rolling along. f(T, level) -> (N,3)."""
    d = G.pd

    def f(T, lvl=1.0):
        c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - T / 9))
        c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 + T / 13) + 1.3)
        return light(STORMDARK, lvl * 0.45) + light(STORM, lvl * (0.1 + 0.42 * c1 ** 2 * (0.5 + 0.5 * c2)))
    return f


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    # will she come? the twins' love in the cellos; fate answers, low
    add(0.0, T_DEFY, 'D1', 70, 'pedal')
    for t, m, v, d in play('twins_love', T_ASK, 0.5, -12, 92, 'melody'):
        if t < T_NO:
            add(t, d, m, v, 'ask')
    for t, m, v, d in play('fate', T_NO, 1.0, -2, 92):
        add(t, d * 1.02, m, v, 'fate', 0)
    # defiance: Siegmund's motif in the horns, full
    for t, m, v, d in play('siegmund', T_DEFY, 0.5, 0, 108):
        add(t, d, m, v, 'defy' if m >= note('C3') else 'defybass')
    # her warning: fate, lower
    for t, m, v, d in play('fate', T_WARN, 1.0, -5, 88):
        add(t, d * 1.02, m, v, 'fate', 1)
    # he raises Nothung: the sword's motif on the trumpet, trembling violins, a timpani roll
    for i, (t, m, v, d) in enumerate(play('nothung', T_RAISE + 1.0, 0.7, -12, 100)):
        add(t, d, m, v + 2 * i, 'nothung', i)
    add(T_RAISE, T_HALT - T_RAISE, 'D4', 84, 'vtrem')
    add(T_RAISE + 0.5, T_HALT - T_RAISE - 0.5, 'Ab4', 80, 'vtrem')
    add(T_HALT - 4.0, 4.0, 'D2', 110, 'roll')
    # Halt!
    for m in ('D2', 'D3', 'A3', 'D4', 'F#4', 'A4'):
        add(T_HALT, 1.0, m, 124, 'halt')
    # the Ride, twice, rising; the twins' love sweeps up
    for j, t0 in enumerate(T_RIDE):
        for t, m, v, d in play('ride', t0, RBEAT, 0 + 3 * j, 112):
            add(t, d * 1.2, m, v, 'ride', j)
    for i, t in enumerate(np.arange(T_RIDE[0], T_LOVE, RBEAT / 2)):
        add(t, RBEAT / 2, note(('B1', 'B2', 'F#2', 'B2')[i % 4]) + 3 * (t >= T_RIDE[1]), 100, 'gallop', i)
    for t, m, v, d in play('twins_love', T_LOVE, 0.55, 0, 104, 'melody'):
        add(t, d * 1.05, m, v, 'love')
    for b0, ch in ((0, ('Bb1', 'F2', 'D3', 'F3')), (3, ('F1', 'C3', 'Eb3', 'A3')), (6, ('Bb1', 'F2', 'D3', 'Bb3')),
                   (9, ('F1', 'C3', 'Eb3', 'A3')), (12, ('Eb2', 'Bb2', 'G3', 'Eb4'))):
        for m in ch:
            add(T_LOVE + b0 * 0.55, 3 * 0.55 * 1.08 if b0 < 12 else T_FLY - T_LOVE - b0 * 0.55 + 0.5, m, 78, 'pad')
    # she flies off, the Ride whirling after her
    for t, m, v, d in play('ride', T_FLY, 0.3, 3, 104):
        add(t, d * 1.1, m, v, 'ride', 2)
    add(T_FLY, 1.0, 'C2', 100, 'fly')
    # he bends to her; thunder far off
    for t, m, v, d in play('twins_love', T_BEND, 0.6, -12, 96, 'melody'):
        if t < T_THUNDER[0]:
            add(t, d, m, v, 'ask')
    add(T_BEND, D - T_BEND, 'D1', 84, 'pedal')
    for m in ('Bb1', 'F2', 'D3'):
        add(T_GONE, T_THUNDER[0] - T_GONE + 1.0, m, 72, 'pad')
    add(T_THUNDER[0] - 1, D - T_THUNDER[0] + 1, 'D2', 74, 'trem')
    for k, tt in enumerate(T_THUNDER):
        add(tt, 2.0, 'D1', 86 + 10 * k, 'thunder', k)
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
    """Per frame: Brünnhilde (she flies off along the porch and out at the end of Right); the lovers stay put."""
    F = nframes(D)
    t = np.arange(F) * DT
    b0, b1 = at(G, 'Porch Front', 0.5), at(G, 'Right', 1.0) + 60
    u = smoothstep(T_FLY, T_GONE, t)
    br = b0 + (b1 - b0) * u ** 1.6
    return dict(t=t, brunn=br, mund=np.full(F, at(G, 'Left', 0.55)), linde=np.full(F, at(G, 'Left', 0.7)))


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    bed = pass_bed(G)
    ind = indigo_bed(G)
    storm = storm_bed(G)
    C = choreography(G)
    N = compose()
    b0, mn, ln = C['brunn'][0], C['mund'][0], C['linde'][0]
    tw = Flicker(rng, G.N, 2.0, 7.0)

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def chords(*parts):
        return sorted({e[0] for e in ons(*parts)})

    def last(on, t):
        i = int(np.searchsorted(on, t, side='right')) - 1
        return t - on[i] if i >= 0 else 99.0

    fate_on = chords('fate')
    ask_on = chords('ask')
    defy_on = chords('defy')
    sword_on = chords('nothung')
    ride_on = chords('ride')
    love_on = chords('love')
    gold = rng.uniform(0, L, 70)
    gold_t = rng.uniform(T_HALT + 0.5, T_FLY - 2, 70)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lift = smoothstep(T_HALT - 0.05, T_HALT + 3.0, t)            # the indigo shatters; the pass floods back
        grey = smoothstep(T_BEND, D, t) * 0.4                         # storm clouds begin to gather
        fr = ind(T, 1 - lift) + bed(T, lift * (1 - grey), lift * (1 - grey)) + storm(T, grey)
        b = C['brunn'][f]

        # fate: each chord a pulse of her silver; on "no", a cold pale wave runs down her gaze to him
        pf = np.exp(-last(fate_on, t) / 1.2)
        gaze = (1 - smoothstep(T_DEFY, T_DEFY + 4, t)) + smoothstep(T_WARN, T_WARN + 2, t) * (1 - lift)
        span = smoothstep(mn - 10, mn + 20, d) * smoothstep(b0 + 10, b0 - 30, d)
        ripple = 0.75 + 0.25 * np.cos(2 * np.pi * ((b0 - d) / 160 - T / 4))
        fr += light(PALE, (1 - lift) * min(gaze, 1.0) * (0.3 + 0.15 * pf) * span * ripple)
        fr += light(PALE, (1 - lift) * (0.275 + 0.2 * pf) * np.exp(-((d - b0) / 150) ** 2))
        for tf in (T_NO, T_WARN):
            if tf <= t < tf + 3.0:
                u = (t - tf) / 2.2
                q = b0 + (mn - b0) * min(u, 1.0)
                fr += light(PALE, 0.7 * (1 - smoothstep(0.9, 1.3, u)) * np.exp(-((d - q) / 50) ** 2))

        # his question: his blue reaches to her amber
        ask = np.exp(-last(ask_on, t) / 0.6)
        reach = smoothstep(T_ASK, T_ASK + 2, t) * (1 - smoothstep(T_NO, T_NO + 2, t))
        reach += smoothstep(T_BEND, T_BEND + 1.5, t) * (1 - smoothstep(T_THUNDER[0], T_THUNDER[0] + 3, t))
        if reach > 0:
            between = smoothstep(mn, mn + 8, d) * smoothstep(ln, ln - 8, d)
            fr += light(SIEGMUND, reach * (0.3 + 0.2 * ask) * between)
        # defiance: his blue pushes the indigo off Left and up Porch Left
        defy = smoothstep(T_DEFY, T_DEFY + 2, t) * (1 - smoothstep(T_WARN, T_WARN + 3, t))
        if defy > 0:
            push = 180 + 500 * smoothstep(T_DEFY, T_DEFY + 7, t)
            beat = np.exp(-last(defy_on, t) / 0.4)
            zone = smoothstep(push, push - 120, np.abs(d - mn))
            fr = fr * (1 - 0.6 * defy * zone)[:, None]
            surf = 0.75 + 0.25 * np.cos(2 * np.pi * (np.abs(d - mn) / 110 - 1.2 * T))
            fr += light(SIEGMUND, defy * (0.45 + 0.3 * beat) * zone * surf)

        # the sword raised: the blade lengthens over her, hotter with every note
        raise_ = smoothstep(T_RAISE, T_RAISE + 2, t) * (1 - smoothstep(T_HALT, T_HALT + 1.5, t))
        heat = 0.0
        if raise_ > 0:
            n = np.searchsorted(sword_on, t, side='right')
            heat = n / len(sword_on)
            ping = np.exp(-last(sword_on, t) / 0.25) if n else 0.0
            tip = mn + 20 + (ln - mn + 25) * smoothstep(T_RAISE, T_HALT - 1, t)
            blade = smoothstep(mn + 4, mn + 10, d) * smoothstep(tip + 6, tip - 6, d)
            fr += light(STEEL, raise_ * (0.55 + 0.3 * heat + 0.3 * ping) * blade)
            fr += light(WHITE, raise_ * (0.3 * heat + 0.5 * ping) * np.exp(-((d - tip) / 10) ** 2))
            fr = fr * (1 - 0.35 * raise_ * heat * np.exp(-((d - ln) / 300) ** 2) * (1 - blade))[:, None]

        # Halt! a silver blast down the porch to him, and the indigo shatters
        if T_HALT <= t < T_HALT + 2.5:
            u = (t - T_HALT) / 0.6
            front = b0 + (mn - b0) * min(u, 1.0)
            lo, hi = min(front, b0), max(front, b0)
            fr += light(BRUNN, 0.9 * np.exp(-(t - T_HALT) / 0.5) * ((d >= lo) & (d <= hi)))
            fr += light(WHITE, 0.7 * np.exp(-(t - T_HALT) / 0.12))
        # the promise: gold showers over the returning pass; the ride gallops along the house
        if T_HALT < t < T_FLY + 2:
            age = t - gold_t
            on = (age > 0) & (age < 1.5)
            if on.any():
                g = (np.exp(-age[on] / 0.4)[None, :] * np.exp(-((d[:, None] - gold[on][None, :]) / 8) ** 2)).max(axis=1)
                fr += light(BGOLD, 0.9 * g)
            ride = smoothstep(T_RIDE[0], T_RIDE[0] + 0.5, t) * (1 - smoothstep(T_LOVE - 1, T_LOVE + 1, t))
            if ride > 0:
                rb = np.exp(-last(ride_on, t) / 0.15)
                stripes = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - b0) / 140 - 2.5 * T))) ** 3
                fr += light(BRUNN, ride * (0.3 + 0.3 * rb) * stripes)
                fr += light(BGOLD, ride * 0.3 * rb * (1 - stripes))
            love = smoothstep(T_LOVE - 0.5, T_LOVE + 1, t) * (1 - smoothstep(T_FLY - 1, T_FLY + 1, t))
            if love > 0:
                lb = np.exp(-last(love_on, t) / 0.5)
                wave = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - mn) / 600 - 0.3 * T))
                fr += light(SIEGLINDE, love * (0.35 + 0.2 * lb) * wave)
                fr += light(SIEGMUND, love * (0.3 + 0.15 * lb) * (1 - wave))

        # Brünnhilde: silver over the porch, blazing when she relents, a streak when she flies
        if t < T_GONE + 0.5:
            bl = 0.78 + 0.18 * pf + 0.25 * lift * (1 - smoothstep(T_FLY, T_GONE, t))
            vis = 1 - smoothstep(T_GONE - 0.6, T_GONE, t)
            bl *= vis
            fr += light(BRUNN, bl * np.exp(-((d - b) / 18) ** 2) + 0.3 * bl * np.exp(-((d - b) / 90) ** 2))
            fr += light(BRUNN, 0.14 * bl * porch * (0.85 + 0.15 * np.cos(2 * np.pi * T / 8)) * (1 - lift))
            for j, o in enumerate(GLINTS):
                g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
                fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
            fr += light(BGOLD, 0.55 * vis * np.exp(-((d - b - 16) / 7) ** 2))
            line = smoothstep(b - 46, b - 40, d) * smoothstep(b - 12, b - 18, d)
            fr += light(SPEAR, 0.45 * vis * line)
        if T_FLY <= t < T_GONE + 2.0:
            for j, lag in enumerate(range(2, 40, 2)):
                q = C['brunn'][max(f - lag, 0)]
                fr += light(BRUNN, 0.75 * (1 - j / 19) * np.exp(-((d - q) / 28) ** 2) * (t - lag * DT < T_GONE))

        # Siegmund and Nothung; the glint dims at her warning, burns while he holds it up
        dim = smoothstep(T_WARN, T_WARN + 3, t) * (1 - smoothstep(T_RAISE, T_RAISE + 1, t))
        sm = 0.76 + 0.15 * np.exp(-last(defy_on, t) / 0.4) * defy + 0.04 * smoothstep(T_BEND, D, t)
        fr += light(SIEGMUND, sm * np.exp(-((d - mn) / 16) ** 2) + 0.25 * sm * np.exp(-((d - mn) / 60) ** 2))
        blade = smoothstep(mn - 32, mn - 29, d) * smoothstep(mn - 15, mn - 18, d)
        fr += light(STEEL, sm * 0.7 * (1 - 0.6 * dim) * (1 - raise_) * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, sm * 0.7 * np.exp(-((d - mn + 12) / 3.5) ** 2))
        # Sieglinde, senseless; his love lifts her a little
        sl = 0.299 + 0.08 * ask * reach
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))

        # far thunder: a faint flicker on the wings
        for k, tt in enumerate(T_THUNDER):
            if tt <= t < tt + 0.8:
                fl = np.exp(-(t - tt) / 0.12) + 0.6 * np.exp(-max(t - tt - 0.25, 0) / 0.1) * (t > tt + 0.25)
                fr += light(STORM, (0.3 + 0.15 * k) * fl * (1 - porch))
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
    for name, gain, rev in (('low', 0.18, 0.22), ('tubas', 0.15, 0.45), ('horns', 0.16, 0.38),
                            ('brass', 0.16, 0.32), ('strings', 0.16, 0.32), ('perc', 0.19, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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

    def pb(t):
        return pan_at(np.interp(t, C['t'], C['brunn']))

    pm = pan_at(C['mund'][0])
    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.0, fall=1.5)
        elif part == 'ask':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pm)
        elif part == 'fate':
            if m < note('C3'):
                hold('tubas', tuba, m + (12 if m < note('E2') else 0), t, t + d, v, pb(t), rise=0.25, fall=1.2, gain=0.9)
            elif m < note('G3'):
                hold('tubas', tbn, m, t, t + d, v - 6, pb(t), rise=0.25, fall=1.2, gain=0.7)
            else:
                hold('tubas', horn, m, t, t + d, v, pb(t), rise=0.25, fall=1.2, gain=0.8)
        elif part == 'defy':
            M.add('horns', horn.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pm)
            M.add('strings', vc.play(m - 12 if m > note('C4') else m, v - 16, dur=d * 1.05, release=0.5), t, 0.6, pm)
        elif part == 'defybass':
            hold('low', cb, m + 12, t, t + d, v - 20, pm, rise=0.3, fall=0.8, gain=0.8)
        elif part == 'nothung':
            M.add('horns', tpt.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, pm)
        elif part == 'vtrem':
            hold('strings', vtrem, m, t, t + d, v, pm * 0.6, rise=3.0, fall=0.3, gain=0.6)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.8, pm)
        elif part == 'halt':
            s = tuba if m < note('C3') else (tbn if m < note('C4') else horn)
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d, release=0.8), t, 0.9, pb(t))
            if m == note('D2'):
                M.add('perc', crash.play(127), t, 1.0, pb(t))
                M.add('perc', timp.play(127, pitch=-2), t, 1.0, pb(t))
                M.add('perc', whoosh(0.7, 5000, 900, 0.5, seed=4), t - 0.1, 0.7, 0.5 * (pb(t) + pm))
        elif part == 'ride':
            M.add('horns', horn.play(m, v, dur=d, release=0.3), t, 1.0, pb(t))
            M.add('brass', tbn.play(m - 12, v - 12, dur=d, release=0.3), t, 0.5, pb(t))
        elif part == 'gallop':
            M.add('low', (cbs if k % 2 == 0 else vcs).play(m + 12, v), t, 0.7, -0.2 + 0.4 * (k % 2))
        elif part == 'love':
            M.add('strings', vn.play(m, v, dur=d, release=0.4), t, 0.9, -0.3)
            M.add('strings', vc.play(m - 12, v - 10, dur=d, release=0.4), t, 0.7, 0.3)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.4, fall=0.8, gain=0.7)
        elif part == 'fly':
            M.add('perc', whoosh(3.5, 500, 5000, 0.55, seed=7), t, 0.9, pb(t + 2))
            M.add('perc', crash.play(100), t + 3.6, 0.5, pan_at(at(G, 'Right', 1.0)))
        elif part == 'trem':
            hold('low', trem, m, t, t + d, v, 0.0, rise=3.0, fall=1.0, gain=0.7)
        elif part == 'thunder':
            M.add('perc', roll.play(v, dur=d), t, 0.6, -0.4 if k == 0 else 0.5)
            M.add('perc', timp.play(v - 10, pitch=-8), t + 0.1, 0.6, -0.4 if k == 0 else 0.5)
