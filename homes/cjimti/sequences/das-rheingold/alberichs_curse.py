"""Alberich's Curse: free, and with nothing left, Alberich stands on the porch while the grey morning drains
away into red and black, Valhalla and the meadow sinking out of sight. He swears that the ring will bring ruin and
death to whoever holds it.

"Wie durch Fluch er mir geriet, verflucht sei dieser Ring!": his line climbs to its top on "verflucht" and falls an
octave, every note a red ring out from him, wider as it rises, the ring's red glint on Wotan's hand pulsing with
each; on "Ring!" a muddy wash drops over the whole house. "Dem Tode verfallen, feßle den Feigen die Furcht":
the curse climbs again over the strings' tremolo, higher, louder, to a scream on the top of "des Ringes Herr als
des Ringes Knecht!", and the orchestra crashes down. Then the curse at full force in the whole orchestra, "So segnet
in höchster Not der Nibelung seinen Ring", the red-black churning; a mocking "behalt ihn nun, hüte ihn wohl!",
and the last: "Meinem Fluch fliehest du nicht!". And he is gone, fast, back along Porch Left, the length of Left
and out along Side into the dark, his red trailing mud, as the orchestra rushes after him. The red-black lifts
as the music settles, the grey dawn and the dim battlements of Valhalla come back, the gods appear on the wings,
faded toward grey, and Wotan gazes at the ring on his hand, its red glint pulsing.

The music is Wagner's own: Scene 4, bars 3126 to 3130, 3156 to 3163 and 3172 to 3200, as Solti's 1958 Vienna
Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py). Alberich's curse itself, which the reduction leaves out, is sung by trombones and bassoons
as written in the vocal score (Schott, Mainz: archive.org dasrheingold00wagn2, pp. 175-177): "Wie durch Fluch
er mir geriet, verflucht sei dieser Ring!", "Dem Tode verfallen ... des Ringes Herr als des Ringes Knecht!" and
"behalt' ihn nun, hüte ihn wohl! Meinem Fluch fliehest du nicht!". Under it, the tremolo on the strings', the
chords on horns and tubas, the curse's full force on the brass, the rush after him on strings and woodwinds. On top,
as a staged production would, and kept out of the way of his words: a gong and thunder as each curse falls,
cymbals at the climax, and a rush of wind as he vanishes into the cleft.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt

CODE = 'RG20'
TITLE = "Alberich's Curse"
KIND = 'show'
DESCRIPTION = ("Robbed of everything, Alberich swears that the ring will bring ruin and death to whoever "
               "holds it, and the whole house turns red and black. Then he vanishes into the dark, and the grey "
               "morning slowly comes back.")
VOICEOVER = ('They took his gold, his helmet, and his ring. '
             'So before he goes, he makes them a promise.')

EX = excerpt(__file__)                      # bars 3126-3130, 3156-3163, 3172-3200, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
BAR[3126] = -BAR[3127]                      # the first range starts half way through bar 3126...
BAR[3131] = BAR[3130] + (EX['segments'][0]['seconds'] - BAR[3130]) / 0.6     # ...and ends 0.6 into bar 3130
T_UNTIE = -20.0                             # (already free)
T_LAUGH = -15.0
T_DARK = 0.0                                # red and black
# His curse, from the vocal score: (bar, start, length in quarters, note). 4/4; from bar 3180, 2/2.
VOICE = [(3126, 3, 0.5, 'F#3'), (3126, 3.5, 0.5, 'F#3'),
         (3127, 0, 2, 'A3'), (3127, 2, 1, 'A3'), (3127, 3, 0.75, 'A3'), (3127, 3.75, 0.25, 'A3'),
         (3128, 0, 3, 'C4'), (3128, 3.5, 0.5, 'C4'),
         (3129, 0, 2, 'E4'), (3129, 2, 1, 'E3'), (3129, 3, 0.5, 'E3'), (3129, 3.5, 0.5, 'C3'), (3130, 0, 2, 'G3'),
         (3156, 0, 1.25, 'Db3'), (3156, 1.25, 0.25, 'Db3'), (3156, 1.5, 0.5, 'Db3'), (3156, 2, 1, 'F3'),
         (3156, 3, 0.5, 'F3'),
         (3157, 0, 1.25, 'Ab3'), (3157, 1.25, 0.25, 'Ab3'), (3157, 1.5, 0.5, 'Ab3'), (3157, 2, 1, 'Db4'),
         (3157, 3, 0.5, 'Db4'), (3157, 3.5, 0.5, 'Db4'),
         (3158, 0, 2, 'D4'), (3158, 3.5, 0.5, 'B2'),
         (3159, 0, 1.5, 'Eb3'), (3159, 1.5, 0.5, 'Eb3'), (3159, 2, 2, 'G3'),
         (3160, 0, 1.5, 'Bb3'), (3160, 1.5, 0.5, 'Bb3'), (3160, 2, 1, 'Eb4'), (3160, 3, 0.75, 'Eb4'),
         (3160, 3.75, 0.25, 'D4'),
         (3161, 0, 1, 'Db4'), (3161, 1.5, 0.5, 'Bb3'), (3161, 2, 1.5, 'Bb3'), (3161, 3.5, 0.5, 'Bb3'),
         (3162, 0, 1, 'Db4'), (3162, 1.5, 0.25, 'Bb3'), (3162, 1.75, 0.25, 'Bb3'), (3162, 2, 1.5, 'Db4'),
         (3162, 3.5, 0.5, 'Bb3'), (3163, 0, 1, 'F4'),
         (3175, 3.5, 0.5, 'F#3'), (3176, 0, 0.75, 'G3'), (3176, 0.75, 0.25, 'E3'), (3176, 1, 1, 'B3'),
         (3177, 0, 1, 'C4'), (3177, 1, 0.5, 'C4'), (3177, 1.5, 0.5, 'G3'), (3177, 2, 1.5, 'E4'),
         (3178, 3, 0.5, 'G3'), (3178, 3.5, 0.5, 'G3'),
         (3179, 0, 1.5, 'F#4'), (3179, 2, 1.5, 'D4'), (3179, 3.5, 0.25, 'C#4'), (3179, 3.75, 0.25, 'C#4'),
         (3180, 0, 1, 'B3')]
CURSES = [(BAR[3127] - 0.8, 0, 0)]          # (when it begins, ...)
FALLS = [BAR[3130], BAR[3163], BAR[3172], BAR[3180]]     # "Ring!", "Knecht!", the full force, "nicht!"
T_OATH = 1e9
T_EXIT = BAR[3180]                          # "Sehr schnell": he vanishes into the cleft
STEPS = 14
T_GONE = BAR[3184]
T_CLEAR = BAR[3188]                         # the mist begins to clear
T_GAZE = BAR[3194]                          # Wotan gazes at the ring
T_LOGE = 1e9
T_GIANTS = 1e9
D = EX['seconds']

ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
BLOOD = hexc('#ff0800')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
STEEL = hexc('#5a88d0')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')
FRICKA = hexc('#ff9ad0')
DONNER = hexc('#a0c0ff')
FASOLT = hexc('#8090a0')
FAFNER = hexc('#c07a10')
FREIA = hexc('#ff5a9a')
WHITE = hexc('#ffffff')
GODS = [('Left', 0.6, 'fricka'), ('Left', 0.3, 'donner'), ('Right', 0.3, 'froh')]
GIANTS = [('Right', 0.78, FASOLT, 20), ('Right', 0.865, FREIA, 13), ('Right', 0.95, FAFNER, 20)]


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def voice():
    """His curse in seconds: (time, seconds, midi, which statement)."""
    out = []
    for b, x, n, name in VOICE:
        per = 2.0 if b >= 3180 else 4.0
        tb, tn = BAR[b], BAR.get(b + 1, D)
        t0 = tb + (tn - tb) * x / per
        out.append((t0, (tn - tb) * n / per, note(name), 0 if b < 3150 else 1 if b < 3170 else 2))
    return out


def compose():
    """Every note, tagged: (time, seconds, midi, velocity, part, who). His curse ('curse', who = (statement, step));
    under it the orchestra: the left hand's low notes the pedal ('pedal'), the rest 'orch'; from his exit on, the
    rush after him ('rush') and the music settling ('settle'), Wotan's gaze on its last notes ('gaze'); 'fall'
    marks where each curse falls."""
    N = []
    for i, (t, d, m, which) in enumerate(voice()):
        N.append((t, d, m, 112 + 6 * which, 'curse', (which, i)))
    for t, d, m, v, h in EX['notes']:
        if t < T_EXIT - 0.01:
            part = 'pedal' if h == 1 and m < note('C3') else 'orch'
        elif t < T_CLEAR:
            part = 'rush'
        else:
            part = 'gaze' if t >= T_GAZE and h == 0 else 'settle'
        N.append((t, d, m, v, part, None))
    for tf in FALLS:
        N.append((tf, 2.0, note('C2'), 0, 'fall', (0, -1)))
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
    """Per frame: Alberich, Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    A = at(G, 'Porch Front', 0.2) - 14
    set_(0, 0, D, A, 2.0)
    set_(0, T_LAUGH, T_EXIT, A + 8 + 4 * np.sin(2 * np.pi * t / 2.0), 3.0)
    for k in range(STEPS):                                  # halting steps out to the far end of Side
        ts = T_EXIT + k * (T_GONE - T_EXIT) / STEPS
        set_(0, ts, D, A + (-60 - A) * (k + 1) / STEPS, 6.0)
    W, Lg = at(G, 'Porch Front', 0.4), at(G, 'Porch Front', 0.75)
    set_(1, 0, D, W + 6 * np.sin(2 * np.pi * t / 3.1), 2.0)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(2, 0, D, Lg + jit, 4.0)
    set_(2, T_UNTIE - 0.5, T_LAUGH, A + 40 + 25 * np.sin(2 * np.pi * t / 0.8), 8.0)      # untying him
    set_(2, T_LAUGH, D, Lg + jit, 1.5)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def render(G, seed=20):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    curse = [(e[0], e[2], e[5]) for e in N if e[4] == 'curse']
    falls = sorted({e[0] for e in N if e[4] == 'fall'})
    pedals = np.array(sorted({e[0] for e in N if e[4] == 'pedal'}))
    cnotes = np.array([e[0] for e in N if e[4] == 'curse'])
    gaze = np.array([e[0] for e in N if e[4] == 'gaze'])
    oath = np.array([e[0] for e in N if e[4] == 'oath'])
    tread = np.array([e[0] for e in N if e[4] == 'tread'])
    steps = np.array([e[0] for e in N if e[4] == 'slink'])
    laugh = np.array([e[0] for e in N if e[4] == 'laugh'])
    force = accents(EX['notes'], BAR[3172], BAR[3175], 90, 3, 0.25)      # the curse at full force
    rush = accents(EX['notes'], T_EXIT, T_CLEAR + 8, 80, 2, 0.35)        # the orchestra rushing after him
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    churn = Flicker(rng, G.N, 0.15, 0.6)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)
    dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
    dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
    wc = grey(WOTAN, 0.4)
    side = G.seg_of == 'Side'
    gpos = [at(G, s, u) for s, u, _ in GODS]
    hw = 22.0                                               # the heap, full

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        dark = smoothstep(T_DARK, T_DARK + 2.5, t) * (1 - smoothstep(T_CLEAR, T_CLEAR + 9, t))
        clear = 1 - dark
        pd_ = last(pedals, t, 0.4, 3.0)
        cn = last(cnotes, t, 0.3)

        # the grey morning and Valhalla, sinking under red and black, coming back as the mist clears
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t + 54)))
        lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * (wings + 0.5 * porch) * (0.12 + 0.88 * clear)
        fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
        fr += light(grey(VAL, 0.15), 0.34 * merlon * (0.1 + 0.9 * clear))
        if dark > 0:
            gaps = np.clip(0.55 + 0.45 * churn(t), 0, 1) ** 2
            fr += light(BLOOD, dark * (0.26 + 0.06 * pd_) * gaps)
            fr += light(MUD, dark * 0.3 * (1 - gaps))
        for tc, m, (which, i) in curse:                     # each climbing note: a red ring out from him
            if tc <= t < tc + 2.5:
                a = t - tc
                k = max(m - 45, 2)                          # higher notes, wider rings
                rr = (220 + 30 * k) * a ** 0.6 * (1 + 0.2 * which)
                fr += light(BLOOD, (0.6 + 0.15 * which) * (1 - a / 2.5) * np.exp(-((np.abs(d - ap) - rr) / (50 + 4 * k)) ** 2))
        for tf in falls:                                    # the fall: a muddy wash sinking over the house
            if tf <= t < tf + 3.5:
                a = t - tf
                fr += light(MUD, 0.75 * np.exp(-a / 1.2) * np.ones(G.N))
                fr += light(BLOOD, 0.5 * np.exp(-a / 0.3) * np.ones(G.N))

        for ta in force:                                    # each blow of the full force: the house flares blood red
            if ta <= t < ta + 1.0:
                a = t - ta
                fr += light(BLOOD, 0.55 * np.exp(-a / 0.25) * np.ones(G.N))
                fr += light(ALB, 0.6 * np.exp(-a / 0.4) * blob(ap, 120))
        for ta in rush:                                     # red streaks racing out after him toward Side
            if ta <= t < ta + 1.2:
                a = t - ta
                q = pf + 200 - 1300 * a
                fr += light(BLOOD, 0.9 * (1 - a / 1.2) * smoothstep(q - 10, q + 10, d) * smoothstep(q + 320, q, d))
                fr += light(HOT, 0.5 * (1 - a / 1.2) * np.exp(-((d - q) / 14) ** 2))

        # the hoard, helmet on top
        fr += light(GOLD, 0.9 * blob(pf, hw) + 0.25 * blob(pf, 2 * hw))
        fr += light(HOT, 0.6 * blob(pf, 0.5 * hw) * (0.5 + 0.5 * tw(t)) * (tw(t) > 0))
        fr += light(TARN, 0.55 * blob(pf, hw + 8) * (0.6 + 0.4 * tw(t)))

        # Loge, untying him, then back by the heap
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)

        # Wotan, with the ring: its red glint pulsing with every note of the curse, gold point steady
        fr += light(wc, 0.85 * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3), 0.25 * blob(wp, 7))
        gz = last(gaze, t, 0.4)
        glint = 0.6 + 0.9 * cn + 0.5 * last(oath, t, 0.4) + 0.4 * gz + 0.3 * dark
        fr += light(GOLD, (0.95 + 0.3 * gz) * blob(wp, 6))
        fr += light(RED, glint * blob(wp + 9, 6 + 6 * cn) * (0.6 + 0.4 * tw(t)))

        # Alberich: unbound, laughing, swelling with every note of the curse; then slinking off into the dark
        free = smoothstep(T_UNTIE, T_UNTIE + 3.5, t)
        if t < T_UNTIE + 4.5:
            wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
            fr += light(STEEL, 0.8 * (1 - free) * wrap)
            R = 30 + 320 * free
            th = 2 * np.pi * (np.arange(6) / 6 - 0.8 * (t - T_UNTIE))
            q, depth = ap + R * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 14) ** 2) * (0.5 + 0.5 * depth)[None, :]
            fr += light(STEEL, 0.8 * free * (1 - smoothstep(T_UNTIE + 3, T_UNTIE + 4.5, t)) * g.max(axis=1))
        lg = last(laugh, t, 0.15, 0.5)
        oathing = smoothstep(CURSES[0][0] - 1, CURSES[0][0], t) * (1 - smoothstep(T_EXIT - 1, T_EXIT + 1, t))
        gone = smoothstep(T_GONE - 4, T_GONE + 0.5, t)
        st = last(steps, t, 0.2, 1.0)
        ab = (0.45 + 0.25 * free + 0.25 * lg + 0.25 * oathing + 0.45 * cn * oathing + 0.15 * st) * (1 - gone)
        if ab > 0.01:
            fr += light(MUD, (0.35 + 0.15 * oathing) * (1 - gone) * blob(ap, 90 + 60 * oathing) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, ab * blob(ap, 24 + 14 * oathing * cn) * (1 + 0.2 * smoulder(t)))
            if T_EXIT <= t < T_GONE + 1:                    # trailing mud as he goes
                trail = smoothstep(ap + 200, ap, d) * (d > ap)
                fr += light(MUD, 0.4 * (1 - gone) * trail)
        if T_EXIT <= t:                                     # Side darkens behind him as he disappears
            fr *= 1 - 0.3 * (side * smoothstep(T_GONE - 3, T_GONE, t) * (1 - smoothstep(T_GONE + 2, T_GONE + 6, t)))[:, None]

        # the gods, greyed, on the wings as the mist clears
        gods = smoothstep(T_CLEAR + 1, T_CLEAR + 6, t)
        if gods > 0:
            for (s, u, who), gp in zip(GODS, gpos):
                if who == 'froh':
                    hue = (0.1 * t + d / 400) % 1.0
                    c = np.stack([np.clip(np.abs(hue * 6 - 3) - 1, 0, 1), np.clip(2 - np.abs(hue * 6 - 2), 0, 1),
                                  np.clip(2 - np.abs(hue * 6 - 4), 0, 1)], -1)
                    c = c * 0.45 + (c @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.55
                    fr += (np.clip(gods * 0.6 * blob(gp, 26), 0, None) ** 2.2)[:, None] * c
                else:
                    c = grey(FRICKA if who == 'fricka' else DONNER, 0.55)
                    fr += light(c, gods * (0.6 * blob(gp, 20) + 0.15 * blob(gp, 70)))

        # the giants and Freia, appearing at the free end of Right; every tread a thud of their colour
        gi = smoothstep(T_GIANTS + 1, D - 1.5, t) if T_GIANTS < D else 0.0
        if gi > 0:
            tr = last(tread, t, 0.25, 1.0)
            for s, u, col, w in GIANTS:
                p = at(G, s, u)
                b = gi * (0.75 + (0.3 * tr if col is not FREIA else 0.0))
                fr += light(col, b * blob(p, w) + 0.2 * gi * blob(p, 2.5 * w))
            fr += light(FASOLT, 0.25 * tr * gi * smoothstep(at(G, 'Right', 0.7), L, d))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, Alberich's curse from the vocal score on trombones and
    bassoons, and the curse's sounds on top."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C[k]))

    o = Orchestra(M, level=1.55)
    N = compose()
    part = {(e[0], e[2], e[3]): e[4] for e in N if e[4] not in ('curse', 'fall')}

    def role(t, d, m, v, h):
        p = part.get((t, m, v))
        if p in ('orch', 'pedal') and t < T_EXIT:
            if BAR[3172] - 0.01 <= t < BAR[3175]:           # the curse at full force: brass
                if h == 1:
                    return [('tuba', 0, 20, 0.55), ('trombones', 12, 14, 0.45), ('basses', 0, 20, 0.5)]
                return [('horns', 0, 6, 0.5), ('trumpets', 0, -8, 0.35), ('violins', 0, 0, 0.4)]
            if h == 1 and m < note('C3'):                   # the pedal: basses, timpani-dark tuba
                return [('basses', 0, 20, 0.55), ('tuba', 12, 6, 0.4)]
            if d < 0.25:                                    # the tremolo
                return [('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', 0, 6, 0.4)]
            return [('horns', 0, 0, 0.45), ('cellos', 0, 0, 0.4)] if m < note('C5') else [('violins', 0, -4, 0.4)]
        if p == 'rush':                                     # the rush after him
            return [('violins', 0, 0, 0.5), ('flutes', 0, -10, 0.3)] if h == 0 else \
                [('cellos', 0, 10, 0.55), ('basses', -12 if m >= 40 else 0, 6, 0.45)]
        if p in ('settle', 'gaze'):
            return [('clarinets', 0, 0, 0.45), ('violins', 0, -10, 0.3)] if h == 0 else [('cellos', 0, 6, 0.5)]
        return None

    o.tutti(EX['notes'], role=role, pan=lambda t, m: pan_of('alb', t) * 0.4)
    for t, d, m, which in voice():                          # the curse: trombones, doubled by bassoons
        p = pan_of('alb', t)
        o.play('trombones', m, t, max(d, 0.15), 118 + 4 * which, p, 0.8)
        o.play('bassoons', m, t, max(d, 0.15), 108, p, 0.45)
        if m >= note('D4'):                                 # its top notes ring out on the horns too
            o.play('horns', m, t, max(d, 0.15), 110, p, 0.45)
    # the stage, ridden: out of the way of his words, up where each curse falls and as he vanishes
    o.effects([(0, -10), (FALLS[0] - 0.2, -2), (FALLS[0] + 2.5, -10), (FALLS[1] - 0.2, -1), (FALLS[2] + 3, -6),
               (BAR[3175], -12), (T_EXIT - 0.2, 0), (T_CLEAR, -6)])
    for k, tf in enumerate(FALLS):                          # each curse falls: a gong, and thunder deep in the rock
        o.hit('gong', tf, 108 + 5 * k, gain=0.5 + 0.1 * k)
        o.thunder(tf + 0.05, 0.35 + 0.15 * k, 0.0, 0.8 + 0.1 * k)
    o.hit('crash', BAR[3172], 124, gain=0.6)                # the full force
    o.hit('bass drum', BAR[3172], 124, gain=0.7)
    M.add('fx', whoosh(2.5, 400, 3000, 0.6, seed=20), T_EXIT, 0.8, pan_at(at(G, 'Left', 0.3)))   # into the cleft
    o.wind(T_EXIT, T_CLEAR + 4, lambda tt: 0.6 * (1 - np.clip((tt - T_EXIT) / (T_CLEAR + 4 - T_EXIT), 0, 1)),
           pan_at(at(G, 'Left', 0.2)))
