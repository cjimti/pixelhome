"""Brünnhilde Relents: the indigo of the Annunciation still holds the pass, her silver over Porch Front and her
pale gaze lying along Left. Siegmund will not leave Sieglinde behind: he raises Nothung over her, to kill them
both, and the white steel blade lengthens over her amber, hotter with every note of the orchestra's frenzy, the
indigo shuddering around it. "Halt ein! Wälsung!": a silver blast tears from Brünnhilde down the porch to him,
the indigo shatters with a crash, and she breaks. Sieglinde shall live, and Siegmund with her: her silver blazes,
the slate and the dawn of the pass come flooding back under a shower of gold, and the house gallops with her
silver and gold on every accent. Then the orchestra surges up in great rising runs, each one a streak of light
racing out along the house, and at its peak she is gone, a streak of silver with a long trail along the porch
and out at the free end of Right. Siegmund bends to Sieglinde, his blue brushing her amber, as the light greys
and the storm gathers for his fight.

The music is Wagner's own: Act II, scene 4, bars 1768 to 1799 (Siegmund's despair, "Zwei Leben lachen dir hier",
Brünnhilde's "Halt ein! Wälsung!" and her promise) and bars 1816 to 1837 (the orchestral surge as she rushes off to
the battle), spliced, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring
Dataset's piano reduction of the score (pixelhome/ring.py): the sword's line rings out on trumpets over the strings,
"Halt!" is the full brass with cymbal and timpani, and the rest is the full orchestra, the right hand's runs on
violins, flutes and piccolo, the left hand on horns, trombones, cellos and basses. Over the score, as a staging
would: the blade scraping from its sheath and ringing on each note of its line, thuds under the frenzy, a shattering
crash, boom and rush of air for "Halt!", triangles for the gold showering down, hoofbeats galloping under her
promise, a rush of air with each rising run of the surge, her horse racing off along the house into the wind, and
far thunder as the storm gathers for the fight. The effects sit under the sword's frenzy, lead the shattering of
"Halt!", back well off for her promise so the music sings, and lead again for the surge and her flight.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK17'
TITLE = 'Brünnhilde Relents'
KIND = 'show'
DESCRIPTION = ('Siegmund will not go to Valhalla without Sieglinde, and he would rather kill them both than leave '
               'her behind. Moved by his love, Brünnhilde breaks her father\'s order and promises him victory.')
VOICEOVER = ('Heaven is offered to him, and he turns it down for her. '
             'And the goddess who came to take him is moved to tears.')

EX = excerpt(__file__)                      # Act II, bars 1768-1799 + 1816-1837, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_RAISE = BAR[1771]                         # "Zwei Leben lachen dir hier": Nothung over her
T_HALT = BAR[1776]                          # "Halt ein! Wälsung!"
T_LIVE = BAR[1782]                          # "Sieglinde lebe"
T_SURGE = BAR[1816]                         # the orchestra surges: she makes ready to go
T_FLY = BAR[1825]                           # at its peak she flies off to the battle
T_GONE = BAR[1828]
T_BEND = BAR[1829]                          # he bends to Sieglinde
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
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). Before "Halt!" the notes are
    the sword raised ('sword'); the first chord of bar 1776 is 'halt'; from there to the splice Brünnhilde's
    promise ('promise'); from T_SURGE the surge ('surge'), and from T_BEND the stillness after she has gone
    ('after')."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if t < T_HALT - 0.01:
            part = 'sword'
        elif t < T_HALT + 0.3:
            part = 'halt'
        elif t < T_SURGE - 0.01:
            part = 'promise'
        elif t < T_BEND - 0.01:
            part = 'surge'
        else:
            part = 'after'
        N.append((t, d, m, v, part, hand))
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

    def onsets(part, hand=None, vmin=0, dmin=0.0):
        return np.array(sorted({round(e[0], 3) for e in N if e[4] == part and (hand is None or e[5] == hand)
                                and e[3] >= vmin and e[1] >= dmin}))

    def last(on, t):
        i = int(np.searchsorted(on, t, side='right')) - 1
        return t - on[i] if i >= 0 else 99.0

    def accents(part, vmin=90, n=3):
        """Times where n or more notes strike together, loud: the orchestra's accents."""
        c = {}
        for e in N:
            if e[4] == part and e[3] >= vmin:
                c[round(e[0], 2)] = c.get(round(e[0], 2), 0) + 1
        return np.array(sorted(k for k, v in c.items() if v >= n))

    sword_on = onsets('sword', 0, dmin=0.3)            # the sword's line, in the right hand's long notes
    stab_on = accents('sword', 90, 2)                   # the frenzy under it
    prom_on = accents('promise', 80, 2)
    bass_on = onsets('promise', 1, vmin=80, dmin=0.3)
    runs = [(e[0], e[2]) for e in N if e[4] == 'surge' and e[5] == 0 and e[3] >= 100]
    surge_on = onsets('surge', 1)
    after_on = onsets('after', 1)
    gold = rng.uniform(0, L, 90)
    gold_t = rng.uniform(T_HALT + 0.5, T_FLY, 90)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lift = smoothstep(T_HALT - 0.05, T_HALT + 2.0, t)            # the indigo shatters; the pass floods back
        grey = smoothstep(T_BEND, D, t) * 0.5                         # storm clouds begin to gather
        fr = ind(T, 1 - lift) + bed(T, lift * (1 - grey), lift * (1 - grey)) + storm(T, grey)
        b = C['brunn'][f]

        # before Halt: her pale gaze along Left, the indigo shuddering with the frenzy
        if t < T_HALT + 2.0:
            st = np.exp(-last(stab_on, t) / 0.2)
            span = smoothstep(mn - 10, mn + 20, d) * smoothstep(b0 + 10, b0 - 30, d)
            ripple = 0.75 + 0.25 * np.cos(2 * np.pi * ((b0 - d) / 160 - T / 4))
            fr += light(PALE, (1 - lift) * (0.3 + 0.2 * st) * span * ripple)
            fr += light(PALE, (1 - lift) * (0.25 + 0.15 * st) * np.exp(-((d - b0) / 150) ** 2))
            fr += light(SPEAR, (1 - lift) * 0.45 * st * (1 - porch) * (0.7 + 0.3 * tw(t)))

        # the sword raised: the blade lengthens over her, hotter with every note of its line
        raise_ = smoothstep(T_RAISE - 2.0, T_RAISE, t) * (1 - smoothstep(T_HALT, T_HALT + 1.0, t))
        if raise_ > 0:
            n = np.searchsorted(sword_on, t, side='right')
            heat = n / max(len(sword_on), 1)
            ping = np.exp(-last(sword_on, t) / 0.25)
            tip = mn + 20 + (ln - mn + 25) * smoothstep(T_RAISE - 2.0, T_HALT - 1, t)
            blade = smoothstep(mn + 4, mn + 10, d) * smoothstep(tip + 6, tip - 6, d)
            fr += light(STEEL, raise_ * (0.55 + 0.3 * heat + 0.35 * ping) * blade)
            fr += light(WHITE, raise_ * (0.3 * heat + 0.6 * ping) * np.exp(-((d - tip) / 12) ** 2))
            fr = fr * (1 - 0.4 * raise_ * heat * np.exp(-((d - ln) / 300) ** 2) * (1 - blade))[:, None]

        # Halt! a silver blast down the porch to him, and the indigo shatters
        if T_HALT <= t < T_HALT + 2.5:
            u = (t - T_HALT) / 0.6
            front = b0 + (mn - b0) * min(u, 1.0)
            lo, hi = min(front, b0), max(front, b0)
            fr += light(BRUNN, 0.9 * np.exp(-(t - T_HALT) / 0.5) * ((d >= lo) & (d <= hi)))
            fr += light(WHITE, 0.7 * np.exp(-(t - T_HALT) / 0.12))

        # the promise: gold showers over the returning pass, silver and gold gallop along the house on the accents
        if T_HALT < t < T_FLY + 1.5:
            age = t - gold_t
            on = (age > 0) & (age < 1.5)
            if on.any():
                g = (np.exp(-age[on] / 0.4)[None, :] * np.exp(-((d[:, None] - gold[on][None, :]) / 8) ** 2)).max(axis=1)
                fr += light(BGOLD, 0.9 * g)
        if T_HALT + 0.5 < t < T_SURGE + 0.5:
            pb = np.exp(-last(prom_on, t) / 0.25)
            bb = np.exp(-last(bass_on, t) / 0.3)
            stripes = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - b0) / 140 - 2.5 * T))) ** 3
            fr += light(BRUNN, (0.25 + 0.35 * pb) * stripes)
            fr += light(BGOLD, (0.15 + 0.3 * bb) * (1 - stripes))
            fr += light(BRUNN, 0.45 * pb * (1 - porch))
            live = smoothstep(T_LIVE - 0.5, T_LIVE + 1.5, t)
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * ((d - mn) / 600 - 0.3 * T))
            fr += light(SIEGLINDE, live * (0.35 + 0.3 * bb) * wave ** 2 * (1 - porch))
            fr += light(SIEGMUND, live * (0.35 + 0.3 * bb) * (1 - wave) ** 2 * (1 - porch))

        # the surge: each rising run a streak racing out along the house, higher notes farther
        if T_SURGE - 0.2 < t < T_BEND + 1.0:
            sb = np.exp(-last(surge_on, t) / 0.3)
            fr += light(BRUNN, 0.2 * sb * (1 - porch))
            for tt, m in runs:
                a = t - tt
                if 0 <= a < 1.0:
                    off = (60 + 20 * (m - 60)) * (0.6 + 0.8 * a)
                    for sgn in (-1, 1):
                        fr += light(WHITE if m >= 84 else BGOLD, 0.9 * np.exp(-a / 0.4)
                                    * np.exp(-((d - b0 - sgn * off) / 45) ** 2))

        # Brünnhilde: silver over the porch, blazing when she relents, a streak when she flies
        if t < T_GONE + 0.5:
            pf = np.exp(-last(prom_on, t) / 0.3) * lift
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

        # Siegmund and Nothung (the glint is the raised blade while he holds it up)
        bend = smoothstep(T_BEND, T_BEND + 2.0, t)
        sm = 0.76 + 0.06 * bend
        fr += light(SIEGMUND, sm * np.exp(-((d - mn) / 16) ** 2) + 0.25 * sm * np.exp(-((d - mn) / 60) ** 2))
        blade = smoothstep(mn - 32, mn - 29, d) * smoothstep(mn - 15, mn - 18, d)
        fr += light(STEEL, sm * 0.7 * (1 - raise_) * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, sm * 0.7 * np.exp(-((d - mn + 12) / 3.5) ** 2))
        # he bends to her: his blue brushes her amber on each of the last chords
        ab = np.exp(-last(after_on, t) / 0.5) * bend
        between = smoothstep(mn, mn + 8, d) * smoothstep(ln, ln - 8, d)
        fr += light(SIEGMUND, bend * (0.3 + 0.25 * ab) * between)
        sl = 0.3 + 0.12 * ab + 0.08 * smoothstep(T_LIVE, T_LIVE + 2, t)
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))
        # the storm gathering: flickers on the wings with the last chords
        fr += light(STORM, 0.6 * ab * (1 - porch) * (0.6 + 0.4 * tw(t)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes: the full orchestra, the sword's line on trumpets, "Halt!" on the full brass with a crash."""
    o = Orchestra(M, level=1.6)
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    C = choreography(G)

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def role(t, d, m, v, hand):
        if T_RAISE - 0.01 <= t < T_HALT - 0.01 and hand == 0 and d >= 0.3:
            return [('trumpets', 0, 0, 0.6), ('violins', 0, -6, 0.5)]
        return None

    size = lambda t: 0.6 if t < T_HALT else (0.85 if t < T_SURGE else 1.0)
    o.tutti(EX['notes'], size=size, role=role)
    o.effects([(0.0, -5), (T_HALT - 1.0, -4), (T_HALT - 0.2, 0), (T_HALT + 2.0, 0), (T_HALT + 3.5, -10),
               (T_SURGE - 0.5, -10), (T_SURGE + 0.5, -3), (T_FLY - 0.5, -2), (T_FLY, 1), (T_GONE + 1.0, 0),
               (T_BEND + 1.0, -4), (D, -4)])
    pb = pan_at(C['brunn'][0])
    pm, pl = pan_at(C['mund'][0]), pan_at(C['linde'][0])
    pfly = lambda t: pan_at(np.interp(t, C['t'], C['brunn']))
    from pixelhome.audio import whoosh
    from pixelhome.ring import accents
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    N = compose()
    part = lambda p, h=None, vmin=0, dmin=0.0: sorted({round(e[0], 3) for e in N if e[4] == p and (h is None or
                                                       e[5] == h) and e[3] >= vmin and e[1] >= dmin})
    notes = lambda p: [e for e in N if e[4] == p]
    # the sword raised: the blade drawn, a steel ring on each note of its line, the frenzy thudding under it
    o.hit('scrape', T_RAISE - 2.0, 100, gain=0.6, pan=pm, fx=True)
    for t in part('sword', 0, dmin=0.3):
        o.hit('metal', t, 70, gain=0.22, pan=0.5 * (pm + pl), fx=True)
    for t in accents(notes('sword'), vmin=90, n=2, space=0.2):
        o.hit('timpani', t, 100, pitch=-5, gain=0.35, pan=pm)
    # Halt! the silver blast and the indigo shattering
    o.hit('timpani roll', T_HALT - 2.0, 96, gain=0.5)
    o.hit('cymbal swell', T_HALT - 2.4, 96, gain=0.4, pan=pb)
    o.shatter(T_HALT, pb, 1.0)
    o.boom(T_HALT, 0.5 * (pb + pm), 1.0)
    o.M.add('fx', whoosh(0.7, 5000, 400, 0.8, seed=31), T_HALT - 0.05, 0.9, 0.5 * (pb + pm))
    o.hit('crash', T_HALT, 127, gain=0.7, pan=pb)
    o.hit('timpani', T_HALT, 127, pitch=-2, gain=0.7, pan=pb)
    # the gold showering over the pass: the same sparks render() draws
    rng = np.random.default_rng(17)
    Flicker(rng, G.N, 2.0, 7.0)
    gold, gold_t = rng.uniform(0, G.length, 90), rng.uniform(T_HALT + 0.5, T_FLY, 90)
    for k in range(0, 90, 2):
        o.M.add('fx', tri.play(60 + (k * 7) % 40), gold_t[k], 0.1, pan_at(gold[k]))
    # the house galloping with her on the promise's accents, and the hoofbeats under it
    o.gallop(T_LIVE, T_SURGE, beat=0.48, pan=lambda t: 0.6 * np.sin(1.3 * t), v=84, gain=0.8)
    for t in accents(notes('promise'), vmin=80, n=2, space=0.25):
        o.hit('hoof', t, 110, gain=0.6, pan=pb, fx=True)
        o.hit('bass drum', t, 96, gain=0.3, pan=pb, fx=True)
    # the surge: a rush of air with every rising run, out along the house
    last = -9.0
    for e in N:
        if e[4] == 'surge' and e[5] == 0 and e[3] >= 100 and e[0] - last > 0.45:
            last = e[0]
            sgn = 1 if int(e[0] * 10) % 2 else -1
            o.M.add('fx', whoosh(0.8, 500, 4000, 0.6, seed=int(e[0] * 100)), e[0], 0.55, pb + sgn * 0.5)
    for t in (T_SURGE, T_FLY):
        o.hit('crash', t, 110, gain=0.5)
    # she flies: hoofbeats racing off along the porch and out at the end of Right, wind behind her
    o.gallop(T_FLY - 1.5, T_GONE, beat=0.36, pan=pfly, v=118, gain=1.1)
    o.M.add('fx', whoosh(T_GONE - T_FLY + 0.8, 300, 3500, 0.9, seed=77), T_FLY, 1.0, 0.6)
    o.wind(T_FLY - 1.0, D, level=lambda tt: 0.4 + 0.6 * smoothstep(T_BEND, D, tt), pan=0.3)
    o.boom(T_FLY, pb, 0.7)
    o.hit('crash', BAR[1827], 120, gain=0.5, pan=pfly(BAR[1827]))
    # the storm gathering for his fight: far thunder with the last chords' flickers
    for i, t in enumerate(part('after', 1)[::2][:4]):
        o.thunder(t, near=0.15 + 0.12 * i, pan=-0.6 + 0.4 * i, gain=0.9)
