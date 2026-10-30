"""The Annunciation of Death: while Sieglinde lies senseless on Left and Siegmund keeps watch over her, the
whole pass falls silent. The slate and the dawn drain away into indigo, pale motes drift through it. Then the
Wagner tubas sound the power of fate, the chords of the Annunciation: on the first a pale light gathers over the
middle of Porch Front, on the next Brünnhilde is there, her silver glowing wide over the porch with her gold
glints, shield and spear. Only those about to die can see her. The fate motif's knocking rhythm sends pale
shocks down her gaze to him on Left; the chords come again a tone higher, each one a pulse of her silver, and
the beam of her gaze settles on him. Then she tells him where he is going: Valhalla rises out of the depths of
the orchestra, climbing and swelling chord by chord, and over the porch the battlements of the gods' castle
blaze white-gold in the indigo with the fallen heroes glinting along them, brighter with every step of the
climb, until the whole house flares at its summit and settles into the castle's glow.

The music is Wagner's own: Act II, scene 4, bars 1474 to 1481 (the Annunciation's fate chords, twice) and bars 1565
to 1576 (Brünnhilde's Valhalla, from its first rising figure to its summit and cadence), spliced, as Solti's 1958
Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction of the score
(pixelhome/ring.py): the fate chords are played by Wagner tubas (tubas, trombones and horns), the knocking rhythm by
the timpani and cellos, and Valhalla by the full orchestra, its brass growing with the climb. Over the score, as a
staging would: the hush is a gong scrape, a cymbal swell as she gathers out of the light, a deep gong and timpani
roll on every fate chord, a thud reaching Siegmund with each knock, a timpani stroke on every chord of the climb
with triangles for the sparks up the battlements, and a boom, gong and cymbals at Valhalla's summit. The effects
stay hushed throughout, recede further under Valhalla's climb and open up only at its summit.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK16'
TITLE = 'The Annunciation of Death'
KIND = 'show'
DESCRIPTION = ('Brünnhilde appears to Siegmund, and only a man who is about to die can see her. '
               'Slowly and gravely she tells him that tomorrow he will fall, and go with her to Valhalla.')
VOICEOVER = ('Everything goes quiet. Siegmund looks up, and sees someone who should not be there. '
             'She has come to tell him he is going to die.')

EX = excerpt(__file__)                      # Act II, bars 1474-1481 + 1565-1576, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_FATE = [BAR[1474], BAR[1478]]             # the Annunciation, twice
T_HERE = BAR[1475]                          # she is there
T_VAL = BAR[1565]                           # Valhalla begins to rise
T_TOP = BAR[1575]                           # its summit
T_CAD = BAR[1576]                           # the cadence
K = 15
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
CASTLE = hexc('#fff0c0')
BLAZE = hexc('#ffe8a0')
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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Before Valhalla the long notes
    are the fate chords ('fate', k = which statement) and the short ones their knocking rhythm ('knock'); from
    T_VAL on everything is Valhalla ('valhalla', k = 1 for the right hand's top line from C5 up)."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if t < T_VAL - 0.01:
            part = 'fate' if d >= 1.0 else 'knock'
            N.append((t, d, m, v, part, int(t >= T_FATE[1] - 0.01)))
        else:
            N.append((t, d, m, v, 'valhalla', int(hand == 0 and m >= 72)))
    return sorted(N, key=lambda e: e[0])


def choreography(G):
    """Fixed places: Brünnhilde over the middle of Porch Front, Siegmund and Sieglinde on Left."""
    F = nframes(D)
    t = np.arange(F) * DT
    return dict(t=t, brunn=np.full(F, at(G, 'Porch Front', 0.5)), mund=np.full(F, at(G, 'Left', 0.55)),
                linde=np.full(F, at(G, 'Left', 0.7)))


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    z = G.pos[:, 2]
    bed = pass_bed(G)
    ind = indigo_bed(G)
    C = choreography(G)
    N = compose()
    b, mn, ln = C['brunn'][0], C['mund'][0], C['linde'][0]
    tw = Flicker(rng, G.N, 2.0, 6.0)
    heights = smoothstep(-200, -560, z) * porch
    heroes = rng.uniform(0, 1, G.N) < 0.09

    def onsets(part, k=None, vmin=0):
        return np.array(sorted({e[0] for e in N if e[4] == part and (k is None or e[5] == k) and e[3] >= vmin}))

    def last(on, t):
        i = int(np.searchsorted(on, t, side='right')) - 1
        return (t - on[i], i) if i >= 0 else (99.0, -1)

    fate_on = onsets('fate')
    knock_on = onsets('knock')
    val_on = onsets('valhalla')
    top = [(e[0], e[2]) for e in N if e[4] == 'valhalla' and e[5] == 1]
    top_t = np.array([x[0] for x in top])
    top_m = np.array([x[1] for x in top], float)
    crenel = (np.cos(2 * np.pi * d / 46) > -0.1)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        hush = smoothstep(0.0, 3.0, t)
        fr = bed(T, 1 - hush, 1 - hush) + ind(T, hush)

        # her coming: the pale gathers on the first chord, she is there on the next
        appear = smoothstep(0.0, 3.0, t)
        here = smoothstep(T_HERE - 0.5, T_HERE + 1.0, t)
        age, _ = last(fate_on, t)
        pulse = np.exp(-age / 0.9)
        fr += light(PALE, (0.55 * appear * (1 - 0.5 * here) + 0.3 * pulse * appear) * np.exp(-((d - b) / 150) ** 2))
        bl = here * (0.78 + 0.22 * pulse)
        fr += light(BRUNN, bl * np.exp(-((d - b) / 18) ** 2) + 0.3 * bl * np.exp(-((d - b) / 90) ** 2))
        fr += light(BRUNN, 0.16 * bl * porch * (0.85 + 0.15 * np.cos(2 * np.pi * T / 8)))
        for j, o in enumerate(GLINTS):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        fr += light(BGOLD, 0.55 * here * np.exp(-((d - b - 16) / 7) ** 2))
        line = smoothstep(b - 46, b - 40, d) * smoothstep(b - 12, b - 18, d)
        fr += light(SPEAR, 0.45 * here * line)

        # the knocking rhythm: pale shocks race down her gaze from her to him
        span = smoothstep(mn - 10, mn + 20, d) * smoothstep(b + 10, b - 30, d)
        if t < T_VAL + 1.0:
            for tk in knock_on[(knock_on <= t) & (knock_on > t - 2.0)]:
                u = (t - tk) / 1.4
                q = b + (mn - b) * min(u, 1.0)
                fr += light(PALE, 0.8 * (1 - smoothstep(0.85, 1.4, u)) * np.exp(-((d - q) / 70) ** 2))
            # each fate chord: a ring of pale violet spreads from her over the whole house
            for tf in fate_on[(fate_on <= t) & (fate_on > t - 3.0)]:
                r = 700 * (t - tf)
                ring = np.exp(-((np.abs(d - b) - r) / 120) ** 2)
                fr += light(SPEAR, 0.55 * np.exp(-(t - tf) / 1.2) * ring)
            gaze = smoothstep(T_FATE[1] - 1.0, T_FATE[1] + 2.0, t)
            ripple = 0.75 + 0.25 * np.cos(2 * np.pi * ((b - d) / 160 - T / 4))
            fr += light(PALE, gaze * (0.3 + 0.2 * pulse) * span * ripple)

        # Valhalla: the battlements rise and blaze over the porch, chord by chord, higher with the climb
        vin = smoothstep(T_VAL - 0.3, T_VAL + 1.0, t)
        if vin > 0:
            age, _ = last(val_on, t)
            chord = np.exp(-age / 0.35)
            climb = smoothstep(T_VAL, T_TOP, t)
            k = int(np.searchsorted(top_t, t, side='right')) - 1
            hm = (top_m[k] - 72) / 32 if k >= 0 else 0.0                # the top line's height, 0..1
            reach = 200 + 900 * climb + 500 * hm
            wall = np.exp(-((d - b) / reach) ** 2)
            fr += light(CASTLE, vin * (0.35 + 0.45 * climb + 0.25 * chord) * (0.45 + 0.55 * heights)
                        * (0.5 + 0.5 * crenel) * wall)
            fr += light(BLAZE, vin * (0.25 + 0.4 * climb) * chord * wall * (1 - porch))
            fr += light(BGOLD, vin * 0.8 * heroes * wall * (0.4 + 0.6 * tw(t)) * (0.4 + 0.6 * climb))
            # sparks fly up along the house from her with the top line
            for tt, m in top[max(k - 6, 0):k + 1]:
                a = t - tt
                if 0 <= a < 0.9:
                    off = (120 + 14 * (m - 72)) * (0.5 + a)
                    for sgn in (-1, 1):
                        fr += light(WHITE, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - b - sgn * off) / 14) ** 2))
            summit = np.exp(-max(t - T_TOP, 0) / 1.2) * (t >= T_TOP - 0.05)
            fr += light(BLAZE, 0.5 * summit * (1 - 0.4 * porch))
            fr += light(WHITE, 0.35 * summit * np.exp(-((d - b) / 300) ** 2))

        # Siegmund, looking up: his blue lifts toward her
        sm = 0.66 + 0.12 * smoothstep(T_FATE[1], T_FATE[1] + 6, t) + 0.12 * pulse * (t < T_VAL)
        fr += light(SIEGMUND, sm * np.exp(-((d - mn) / 16) ** 2) + 0.25 * sm * np.exp(-((d - mn) / 60) ** 2))
        blade = smoothstep(mn - 32, mn - 29, d) * smoothstep(mn - 15, mn - 18, d)
        fr += light(STEEL, sm * 0.7 * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, sm * 0.7 * np.exp(-((d - mn + 12) / 3.5) ** 2))
        # Sieglinde, senseless
        sl = 0.352 * (1 - 0.15 * hush)
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes: the fate chords on Wagner tubas, the knocking on timpani and cellos, Valhalla on the full
    orchestra, fuller with the climb."""
    o = Orchestra(M, level=2.7)

    def role(t, d, m, v, hand):
        if t < T_VAL - 0.01:
            if d >= 1.0:                                    # the Wagner tubas: tubas, trombones, horns
                if m < 48:
                    return [('tuba', 12 if m < 40 else 0, 8, 0.9), ('basses', 0, 0, 0.4)]
                if m < 55:
                    return [('trombones', 0, 6, 0.7)]
                return [('horns', 0, 10, 0.8)]
            return [('cellos', 0, 10, 0.6)]
        return None

    o.tutti(EX['notes'], size=lambda t: 0.45 + 0.55 * smoothstep(T_VAL, T_TOP, t), role=role)
    # the effects stay hushed under the fate chords and back right off for Valhalla's climb; only the summit opens up
    o.effects([(0.0, -5), (T_VAL - 0.5, -5), (T_VAL + 1.0, -10), (T_TOP - 2.5, -10), (T_TOP - 0.3, -3), (D, -4)])
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    pan_at = lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - xs.min()) / (xs.max() - xs.min()) - 1))
    C = choreography(G)
    pb, pm = pan_at(C['brunn'][0]), pan_at(C['mund'][0])
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    N = compose()
    o.hit('gong scrape', 0.2, 90, gain=0.5, pan=pb)                         # the pass falls silent
    o.hit('cymbal swell', T_HERE - 2.6, 80, gain=0.4, pan=pb)              # she gathers out of the light
    for i, t in enumerate(T_FATE):                                          # fate: deep gongs, a roll under them
        o.hit('gong', t, 118, gain=0.75, pan=pb, fx=True)
        o.hit('timpani roll', t, 92, pitch=-6, gain=0.45, pan=pb)
        o.hit('bass drum', t, 110, gain=0.5, pan=pb)
    o.hit('scrape', T_HERE, 90, gain=0.35, pan=pb)                          # she is there
    for t, d, m, v, part, k in N:
        if part == 'knock':                                                 # each knock races down her gaze to him
            o.hit('timpani', t, v + 15, pitch=(m - 51) * 0.5, gain=0.55, pan=0.5 * (pb + pm), fx=True)
            o.M.add('fx', o.hits['bass drum'].play(min(127, v + 10)), t + 0.05, 0.11, pm)
    o.hit('timpani roll', T_VAL - 0.4, 90, gain=0.5)                        # Valhalla rises out of the depths
    val = sorted({round(e[0], 2) for e in N if e[4] == 'valhalla' and e[3] >= 70})
    for t in val:                                                           # every chord of the climb a stone set
        o.hit('timpani', t, 80 + int(40 * smoothstep(T_VAL, T_TOP, t)), pitch=-3, gain=0.35, pan=pb)
    for t, d, m, v, part, k in N:                                           # sparks up the battlements
        if part == 'valhalla' and k == 1 and v >= 60:
            o.M.add('fx', tri.play(80), t, 0.135, pb + 0.4 * np.sin(7 * t))
    o.hit('cymbal swell', T_TOP - 2.4, 100, gain=0.5)
    o.boom(T_TOP, pb, 1.0)                                                  # its summit
    o.hit('crash', T_TOP, 120, gain=0.65)
    o.hit('crash', T_CAD, 100, gain=0.4)
