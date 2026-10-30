"""The Theft: Alberich stands at the rock with his red reaching for the hard point of gold, the Ring's beads
still circling it, the Rhinemaidens frozen on the far side. "Das Licht lösch' ich euch aus, entreiße dem Riff
das Gold, schmiede den rächenden Ring": every note of his vow is a pulse of red out of him while the cold indigo
shadow closes in from both ends of the house; then "so verfluch' ich die Liebe!", and his red crawls over the gold
until it flickers.

He tears it from the rock: a string rush up to it and on the chord the whole house flashes gold and white; then
darkness floods out from the rock to both ends. He runs with the glow of the gold in his arms, along the porch
and the left wing and down the Side into the depths, a hot red trail behind him. The maidens cry out into the dark
("Haltet den Räuber!" "Rettet das Gold!" "Hilfe!" "Weh!") and his laugh comes back up from below. Then the black
water heaves as the orchestra plunges after him into the depths, mist rises off the river, the maidens sink away
into it, and a faint ring of beads begins to turn over the porch.

The music is Wagner's own: bars 693-716 and 724-738 of Scene 1, timed bar by bar like Barenboim's 1991 Bayreuth
recording. The orchestra is the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): his vow over dark brass
and low strings, the theft's rush in the full orchestra, the plunge into the depths in churning strings and brass.
Alberich's vow and curse and the maidens' cries are from the printed vocal score (Klindworth, Schott; archive.org
dasrheingold00wagn2, pp. 50-51): Alberich on trombone and bassoon, the maidens each on her own woodwind. On the
stage the gold is wrenched away with a crack and a crash, he splashes off and plunges into the depths with a boom,
and the black water churns; under the vow the stage is silent.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'RG05'
TITLE = 'The Theft'
KIND = 'show'
DESCRIPTION = ('Alberich swears off love for ever, tears the gold from its rock and runs with it down into the '
               'dark. The Rhinemaidens cry out after him, too late, as the river goes black and fills with mist.')
VOICEOVER = ('Only someone who gives up love can take the gold. Alberich decides that is a fair price. '
             'The river is about to go dark.')

EX = excerpt(__file__)                      # bars 693-716 and 724-738, Barenboim 1991
D = EX['seconds']
SEG = [x['start'] for x in EX['segments']] + [D]


def bt(pos):
    """The time of a (fractional) bar position."""
    seg = next(x for x in EX['segments'] if x['measures'][0] <= pos <= x['measures'][1])
    bars = [(b, t) for b, t in EX['bars'] if seg['measures'][0] <= b <= seg['measures'][1]]
    return float(np.interp(pos, [b for b, _ in bars], [t for _, t in bars]))


def per(b):
    """Eighths in bar b: 9/8, but "so verfluch' ich die" is in common time."""
    return 8 if b == 702 else 9


T_VOW = bt(694.33)                          # "Das Licht lösch' ich euch aus"
T_HORNS = bt(702)                           # "so verfluch' ich die Liebe!"
T_TEAR = 28.9                               # the string rush up to the gold
T_RIP = 29.15                               # its chord: the gold comes away
T_FLEE = T_RIP + 0.6
T_OUT = bt(707.3)                           # he is gone down the Side into the depths
CRIES = [bt(707.667), bt(708.667)]          # "Haltet den Räuber!" "Rettet das Gold!"
T_SAVE = bt(709.333)                        # "Hilfe! Hilfe!"
T_LAUGH = bt(713)                           # his laugh, from below
T_LAMENT = bt(711)                          # "Weh!"
T_MIST = SEG[1]                             # the orchestra plunges after him; mist rises
T_SINK = SEG[1] + 6.0
T_XFORM = D - 12.0                          # a faint ring begins to turn

WOG, WELL, FLO = 0, 1, 2
COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
DEPTHS = hexc('#0c1c8c')
SHADOW = hexc('#1c1880')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
ALB = hexc('#ff1000')
EMBER = hexc('#ff8a20')
MUD = hexc('#5a1200')
COLD = hexc('#7090d0')
MIST = hexc('#6c70b8')
DUSK = hexc('#1c1c70')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


# Sung lines from the vocal score: (bar, start, length in eighths, note, who); who 3 is Alberich
VOICE = [(b, x, n, m, 3) for b, x, n, m in [
    (694, 2, 1, 'G3'), (694, 3, 3, 'C4'), (694, 6, 2, 'C4'), (695, 0, 1.5, 'C4'), (695, 1.5, .5, 'B3'),
    (695, 2, 1, 'C4'), (695, 3, 2, 'Eb4'), (696, 2, 1, 'C4'), (696, 3, 3, 'C4'), (696, 6, 1.5, 'C4'),
    (696, 7.5, .5, 'B3'), (696, 8, 1, 'C4'), (697, 0, 2, 'C4'), (697, 2, 1, 'C4'), (697, 3, 3, 'Eb4'),
    (698, 0, 3, 'C4'), (698, 3, 1, 'C4'), (698, 4, 1, 'C4'), (698, 5, 1, 'C4'), (698, 6, 1.5, 'C4'),
    (698, 7.5, .5, 'B3'), (698, 8, 1, 'C4'), (699, 0, 1, 'E4'), (699, 8, 1, 'C4'), (700, 0, 6, 'C4'),
    (700, 6, 2, 'C4'), (700, 8, 1, 'C4'), (701, 0, 6, 'D4'), (702, 0, 3, 'Eb4'), (702, 3, 1, 'D4'),
    (702, 4, 2, 'C4'), (702, 6, 1, 'B3'), (702, 7.5, .5, 'C4'), (703, 0, 3, 'C4'), (703, 3, 1, 'C3')]]
VOICE += [(707, 6, 1.5, 'Eb5', FLO), (707, 7.5, .5, 'Eb5', FLO), (707, 8, 1, 'Eb5', FLO), (708, 0, 2, 'D5', FLO),
          (708, 2, 1, 'B4', FLO), (708, 6, 1.5, 'F5', WELL), (708, 7.5, .5, 'F5', WELL), (708, 8, 1, 'F5', WELL),
          (709, 0, 3, 'D5', WELL), (709, 3, 5, 'F5', WOG), (709, 8, 1, 'D5', WOG), (710, 0, 6, 'Ab5', WOG),
          (710, 6, 2, 'F5', WOG), (710, 0, 6, 'F5', WELL), (710, 6, 2, 'D5', WELL), (711, 0, 6, 'Ab5', WOG),
          (711, 0, 6, 'F5', WELL), (711, 0, 6, 'B4', FLO)]


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). Alberich's vow is 'vow' and his curse 'horns' (who
    3); the maidens' cries 'sing' (who: which one); the right hand in the last bars is 'ring'; every note of the
    excerpt is also 'orch' (who: the hand)."""
    N = []
    for b, x, n, name, who in VOICE:
        t0 = bt(b + x / per(b))
        part = 'sing' if who < 3 else 'horns' if b >= 702 else 'vow'
        N.append((t0, bt(b + (x + n) / per(b)) - t0, note(name), 104, part, who))
    for t, d, m, v, h in EX['notes']:
        N.append((t, d, m, v, 'orch', h))
        if t >= T_XFORM - 2 and h == 0 and d >= 0.2:
            N.append((t, d, m, v, 'ring', None))
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
    """Per frame: where each maiden and Alberich are (path distance), and where the gold is."""
    F = nframes(D)
    t = np.arange(F) * DT
    pf = at(G, 'Porch Front', 0.5)
    tgt = np.zeros((4, F))
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    bob = [12 * np.sin(2 * np.pi * t / 1.4 + k) for k in range(3)]
    for k, off in ((WOG, 150), (WELL, 330), (FLO, 240)):
        set_(k, 0, D, pf + off, 2.0)
    for k, off in ((WOG, 135), (WELL, 315), (FLO, 225)):    # flinching back as he swears
        set_(k, T_VOW, T_RIP, pf + off + 0.4 * bob[k], 2.0)
    for k, dest in ((WOG, at(G, 'Left', 0.3)), (FLO, at(G, 'Left', 0.55)), (WELL, at(G, 'Left', 0.85))):
        set_(k, T_RIP + 1.2, T_LAMENT, dest + bob[k], 2.2 + 0.4 * k)
    for k, off in ((WOG, -150), (WELL, 140), (FLO, -10)):   # back to the empty rock, swaying round it
        set_(k, T_LAMENT, D, pf + off + 1.5 * bob[k], 0.7)
    A = pf - 45
    set_(3, 0, D, A + 4 * np.sin(2 * np.pi * t / 0.7), 6.0)
    set_(3, T_TEAR - 0.6, T_RIP, pf - 12, 14.0)             # the lunge for it
    u = smoothstep(T_FLEE, T_OUT, t)
    set_(3, T_RIP, D, (pf - 12) + (-120 - (pf - 12)) * u, 9.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, pos=pos[:3], apos=pos[3])


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    vow = np.array([e[0] for e in N if e[4] == 'vow'])
    horns = np.array([e[0] for e in N if e[4] == 'horns'])
    rings = np.array([e[0] for e in N if e[4] == 'ring'])
    sighs = [(e[0], e[5]) for e in N if e[4] == 'sing' and e[0] >= T_LAMENT]
    cries = []
    tw = Flicker(rng, G.N, 2.0, 7.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    flick = Flicker(rng, 1, 5.0, 11.0)
    heaves = accents(EX['notes'], SEG[1], D, vmin=0, n=3, space=0.55)    # the plunge's accents

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap = C['apos'][f]

        # the river: RG04's cold shade at the ends, closing in as he swears; then darkness from the rock
        cold = 0.45 + 0.4 * smoothstep(T_VOW, T_HORNS + 4, t)
        reach = (661 + 820 * smoothstep(T_VOW, T_TEAR, t))
        shade = np.clip(np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d))
                        * cold, 0, 1)
        rd = 1800 * smoothstep(T_RIP + 0.1, T_RIP + 2.0, t) ** 0.8
        dark = smoothstep(rd, rd - 160, np.abs(d - pf)) if t > T_RIP else np.zeros(G.N)
        mist = 0.75 * smoothstep(T_MIST + 4, T_MIST + 16, t)
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        water = (1 - 0.7 * shade) * (1 - 0.72 * dark) * (1 - mist)
        warm = 0.12 * (1 - smoothstep(T_VOW, T_HORNS, t))   # the gold's warmth still on the water, draining away
        fr += light(DEEP, (0.2 + 0.1 * w1) * water * (1 - 0.4 * warm))
        fr += light(GREEN, (0.07 + 0.18 * w1 * w2) * water * (1 - 0.6 * dark) * (1 - 0.5 * warm))
        fr += light(GOLD, (0.06 + 0.22 * w1 * w2) * warm * water)
        fr += light(hexc('#ffc840'), 1.0 * warm * (w1 * w2) ** 3 * (0.5 + 0.5 * tw(t)) * water)
        fr += light(SHADOW, 0.3 * shade * (1 - dark) * (1 - mist))
        churn = np.exp(-max(0.0, t - T_OUT) / 8.0) + 0.8 * smoothstep(T_MIST, T_MIST + 2, t)  # black water heaving
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - pf) / 420 - 0.45 * t))
        fr += light(DEPTHS, (0.16 + 0.1 * w1 + 0.22 * churn * swell ** 3) * dark * (1 - mist))
        if mist > 0:                                        # mist: slow grey-violet wisps rising off the water
            m1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 + 0.05 * t))
            m2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 230 - 0.09 * t) + 2)
            m3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.03 * t) + 4)
            fr += light(DUSK, (0.2 + 0.06 * m3) * mist)
            fr += light(MIST, (0.04 + 0.26 * (m1 * m2) ** 1.5 + 0.08 * m3) * mist)

        # the plunge: every accent heaves a wave of black water out from the robbed rock, and far down at the end
        # of Side the depths glint red where he went
        for th in heaves:
            if th <= t < th + 2.6:
                age = t - th
                rf = 1500 * smoothstep(0, 2.6, age)
                band = np.exp(-((np.abs(d - pf) - rf) / 300) ** 2) * (1 - age / 2.6) ** 1.5
                fr += light(COLD, 0.55 * band) + light(DEPTHS, 0.6 * band)
                fr += light(ALB, 0.7 * np.exp(-age / 0.35) * np.exp(-(d / 110) ** 2))

        # the vow: every note a pulse of red out of him; the horns drag his red over the gold
        for arr, w in ((vow, 1.0), (horns, 0.7)):
            i = int(np.searchsorted(arr, t, side='right')) - 1
            if i >= 0 and t - arr[i] < 1.2:
                age = t - arr[i]
                r = 20 + 700 * age ** 0.6
                fr += light(ALB, 0.85 * w * (1 - age / 1.2) * np.exp(-((np.abs(d - ap) - r) / 50) ** 2))
                fr += light(MUD, 0.5 * w * np.exp(-age / 0.5) * np.exp(-((d - ap) / 300) ** 2))
        lust = 1.0 + 0.6 * smoothstep(T_HORNS, T_TEAR, t)
        gold_on = 1 - smoothstep(T_RIP, T_RIP + 0.05, t)

        # the gold on its rock: hard, then frightened, flickering under his red
        if gold_on > 0:
            fear = smoothstep(T_HORNS, T_TEAR, t)
            fl = 1 - 0.45 * fear * (0.5 + 0.5 * flick(t)[0])
            core = np.exp(-((d - pf) / 36.5) ** 2)
            fr += light(GOLD, gold_on * fl * (0.9 * core + 0.09 * np.exp(-((d - pf) / 264) ** 2) * (1 - 0.7 * shade)))
            fr += light(HOT, gold_on * fl * 0.75 * np.exp(-((d - pf) / 16.4) ** 2))
            # the Ring's beads, spinning faster and redder as he swears, gone when the gold goes
            ring = 0.5 * (1 + 0.6 * smoothstep(T_VOW, T_TEAR, t)) * gold_on
            ph = 0.28 * (t + 31) + 0.25 * max(0.0, t - T_VOW) ** 2 / (T_TEAR - T_VOW)
            th = 2 * np.pi * (np.arange(14) / 14 + ph)
            q, depth = pf + 300 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 24) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            redder = smoothstep(T_HORNS, T_TEAR, t)
            fr += light(GOLD, ring * (0.95 - 0.4 * redder) * front) + light(RED, ring * (0.6 + 0.4 * redder) * back)
        if T_TEAR - 0.7 <= t < T_RIP:                       # the grab: red and gold wrestle on the porch
            u = smoothstep(T_TEAR - 0.7, T_RIP, t)
            fr += light(ALB, 0.5 * u * np.exp(-((d - pf) / (120 + 200 * u)) ** 2) * (0.6 + 0.4 * tw(t)))

        # the theft: a flash over the whole house, a burst out of the rock, then he runs with the glow
        if T_RIP <= t < T_RIP + 2.0:
            age = t - T_RIP
            fr += light(GOLD, 1.0 * np.exp(-age / 0.3) * np.ones(G.N))
            fr += light(WHITE, 0.8 * np.exp(-age / 0.12) * np.ones(G.N))
            r = 1800 * smoothstep(0, 1.6, age)
            fr += light(HOT, 0.9 * np.exp(-((np.abs(d - pf) - r) / 110) ** 2) * (1 - smoothstep(1.0, 2.0, age)))
        gone = smoothstep(380, -60, ap) if t > T_RIP else 0.0
        vis = 1 - gone
        murk = np.exp(-((d - ap) / 220) ** 2)
        fr += light(MUD, 0.3 * murk * (1 + 0.15 * smoulder(t)) * vis)
        fr += light(ALB, 0.85 * np.exp(-((d - ap) / (28 + 6 * (t > T_RIP))) ** 2) * (1 + 0.2 * smoulder(t)) * vis)
        if t < T_RIP:
            ahead = np.clip((d - ap) / max(pf - ap, 1), 0, 1)
            fr += light(ALB, 0.55 * lust * (d > ap) * np.exp(-((d - ap) / (180 + 60 * lust))) * (1 - ahead) ** 0.5
                        * (d < pf + 60))
        else:                                               # the stolen glow in his arms, a hot trail behind
            fr += light(GOLD, 0.85 * vis * np.exp(-((d - ap + 8) / 22) ** 2) * (0.8 + 0.2 * tw(t)))
            fr += light(HOT, 0.5 * vis * np.exp(-((d - ap + 8) / 10) ** 2))
            if t < T_OUT + 1:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 26, 2)):
                    q = C['apos'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 30) ** 2) * (1 - j / 12.5))
                fr += light(EMBER, 0.7 * trail * vis)
        if T_LAUGH <= t < T_LAUGH + 2.0:                    # his laugh, coming up out of the depths
            age = t - T_LAUGH
            pulse = sum(np.exp(-(age - 0.2 * j) / 0.12) for j in range(5) if age >= 0.2 * j)
            fr += light(ALB, 0.35 * pulse * np.exp(-(d / 140) ** 2) * (1 - age / 2))

        # the sad cry: cold sweeps out from the empty rock; the minor resolutions sag the whole house
        sag = 0.0
        for tc, kind, k in cries:
            if not tc <= t < tc + 2.2:
                continue
            age = t - tc
            if kind == 'yearn':
                rf = 1600 * smoothstep(0, 1.4, age)
                band = np.exp(-((np.abs(d - pf) - rf) / 240) ** 2) * (1 - smoothstep(1.2, 2.2, age))
                fr += light(COLD, (0.7 - 0.1 * k) * band)
            elif kind == 'res':
                sag = max(sag, np.exp(-age / 0.9) * (1 - np.exp(-age / 0.1)))
                fr += light(SHADOW, 0.35 * np.exp(-age / 1.2) * np.ones(G.N))
        fr *= 1 - 0.45 * sag

        # the maidens: frozen at first, then crying out into the dark, then lamenting, then sinking into the mist
        thaw = smoothstep(T_RIP, T_RIP + 0.5, t)
        sink = smoothstep(T_SINK, T_SINK + 6, t)
        for k in range(3):
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = np.exp(-(t - sung[k][i]) / 0.2) if i >= 0 and t - sung[k][i] < 1.0 else 0.0
            b = (0.62 + 0.38 * flare) * (0.594 * (1 - thaw) + thaw) * (1 - smoothstep(k * 1.6, k * 1.6 + 5, t - T_SINK))
            trail = np.zeros(G.N)
            if abs(p - C['pos'][k][max(f - 8, 0)]) > 25:
                for j, lag in enumerate((3, 6, 9, 12, 15)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 24) ** 2) * (1 - j / 5.5))
            wide = 1 + 2.5 * sink
            body = np.exp(-((d - p) / ((20 + 10 * flare) * wide)) ** 2)
            fr += light(COLOR[k], b * body + 0.3 * b * np.exp(-((d - p) / 90) ** 2) + 0.45 * b * trail)
            fr += light(WHITE, 0.4 * b * flare * body)
        for ts, who in sighs:                               # each sigh a tear of colour sliding away
            if ts <= t < ts + 2.0:
                age = t - ts
                p0 = np.interp(ts, C['t'], C['pos'][who])
                for sgn in (-1, 1):
                    q = p0 + sgn * 260 * smoothstep(0, 2.0, age)
                    fr += light(COLOR[who], 0.55 * (1 - age / 2.0) * np.exp(-((d - q) / 30) ** 2))

        # the Ring begins to turn into something else: a faint circle of beads over the porch
        rs = 0.32 * smoothstep(T_XFORM - 2, T_XFORM + 4, t)
        if rs > 0:
            ri = int(np.searchsorted(rings, t, side='right')) - 1
            rp = np.exp(-(t - rings[ri]) / 0.5) if ri >= 0 and t - rings[ri] < 2.5 else 0.0
            th = 2 * np.pi * (np.arange(14) / 14 + 0.12 * (t - T_XFORM))
            q, depth = pf + 420 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 26) ** 2)
            front = (g * np.clip(depth, 0, 1)[None, :]).max(axis=1)
            back = (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1)
            fr += light(GOLD, rs * (1 + 0.5 * rp) * front) + light(RED, 0.6 * rs * (1 + 0.4 * rp) * back)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, Alberich's vow and curse on trombone and bassoon, the maidens' cries on
    woodwinds, and the stage: the gold wrenched away, his flight and plunge, the churning depths."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    where = lambda k, t: pan_at(np.interp(t, C['t'], C['pos'][k]))
    alb = lambda t: pan_at(np.interp(t, C['t'], C['apos']))
    o = Orchestra(M, level=2.4)
    splash = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')

    def role(t, d, m, v, h):
        if t < T_TEAR - 0.05:                                           # under the vow: dark and held
            if h == 0:
                return [('violas', 0, 0, 0.5), ('horns', 0, -6, 0.4 * (d >= 0.4))]
            return [('cellos', 0, 4, 0.6), ('tuba', 12 if m < 36 else 0, 0, 0.45), ('basses', 12 if m < 40 else 0, 0, 0.5)]
        if t < SEG[1]:
            return None                                                 # the theft and the cries: full orchestra
        if h == 0:                                                      # the plunge: strings and brass churning
            return [('violins', 0, 8, 0.75), ('horns', 0, -2, 0.5 * (d >= 0.3)), ('trumpets', 0, -10, 0.3 * (d >= 0.5))]
        return [('cellos', 0, 8, 0.75), ('basses', -12 if m >= 40 else 0, 0, 0.55), ('trombones', 0, 0, 0.5 * (d >= 0.3)),
                ('tuba', 0, 0, 0.4 * (m < 48))]

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0, role=role)
    inst = {WOG: [('oboes', 0.85), ('flutes', 0.25)], WELL: [('flutes', 0.85), ('clarinets', 0.25)],
            FLO: [('clarinets', 0.9), ('violas', 0.3)]}
    for t, d, m, v, part, who in compose():
        if part in ('vow', 'horns'):
            o.play('trombones', m, t, max(d, 0.15), 100 + 12 * (part == 'horns'), alb(t), 0.8)
            o.play('bassoons', m, t, max(d, 0.15), 96, alb(t), 0.45)
            if part == 'horns':
                o.play('horns', m, t, max(d, 0.15), 104, alb(t), 0.5)
        elif part == 'sing':
            for name, g in inst[who]:
                o.play(name, m, t, max(d, 0.15), 108, where(who, t), g)
    # the stage
    pf = pan_at(at(G, 'Porch Front', 0.5))
    M.add('fx', whoosh(0.4, 900, 6000, 0.8, seed=5), T_TEAR - 0.25, 0.7, pf)       # the wrench
    o.clash(T_RIP, pf, 124, 0.9)
    o.hit('crash', T_RIP, 124, gain=0.7)
    o.boom(T_RIP + 0.02, pf, 0.9)
    M.add('fx', splash.play(115), T_FLEE, 0.6, alb(T_FLEE))
    for k in range(4):                                                  # he scrambles away along the house
        o.hit('scrape', T_FLEE + 0.8 * k, 90, gain=0.3, pan=alb(T_FLEE + 0.8 * k))
    M.add('fx', splash.play(124), T_OUT - 0.3, 0.9, -0.85)
    o.boom(T_OUT, -0.85, 0.7)                                           # down into the depths
    o.thunder(SEG[1], near=0.35, pan=0.0, gain=0.6)                     # the depths heave
    o.wind(SEG[1], D, level=lambda tt: 0.4 + 0.3 * np.clip((tt - SEG[1]) / 8, 0, 1), pan=0.0)
    o.effects([(0.0, -16), (T_TEAR - 0.4, -16), (T_TEAR - 0.1, 0), (T_OUT + 1.0, -2), (CRIES[0] - 0.2, -12),
               (SEG[1] - 0.5, -10), (SEG[1] + 0.3, -3), (SEG[1] + 6, -9), (D, -9)])
