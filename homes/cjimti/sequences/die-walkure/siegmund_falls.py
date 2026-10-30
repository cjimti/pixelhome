"""Siegmund Falls: the fight on the heights at its fiercest, in the storm. Siegmund (Wälsung blue) and Hunding
(blood red in black) clash on Porch Front, and Brünnhilde (silver, gold glints) streaks in over Siegmund to
shield him: "Triff ihn, Siegmund! Traue dem Schwert!" Then a red glow swells in the storm over the middle of the
porch and Wotan towers out of it in deep blue: "Zurück vor dem Speer!" The steel line of his spear stretches
across the porch, and Nothung shatters on it: one white burst over the whole house, white shards flung out
along the roofline and falling back to lie glinting on the porch. Brünnhilde recoils to Porch Right. Hunding
lunges and drives his spear into the disarmed Siegmund: a red streak, a white-red flash. The storm drops, and
over the orchestra's dying fall Siegmund's blue gutters, flickers and goes out; a pale glow stays where he lay.

Brünnhilde darts across the porch gathering the shards, runs to Sieglinde ("Zu Roß, daß ich dich rette!"),
lifts her onto her horse and gallops away along the Left wing and out along Side, the shards and Sieglinde's
amber riding with her silver. "Geh! Geh!": Wotan sweeps his hand, a blue wave rolls out over the porch, and
Hunding's red flares and collapses to an ember. Then Wotan's fury breaks: "Doch Brünnhilde! Weh der
Verbrecherin!" His red glow blazes, the storm roars up, surges of blue and red roll out over the house, the
spear's steel line strikes across the porch with each falling step of the orchestra, lightning cracks, and he
rides after her as a blue-black storm, leaving the storm alone, rolling and flickering, settling into the slate
clouds of the Valkyries' rock as the act's last chords crash out.

The music is Wagner's own: Act II, scene 5, bars 1981 to 1993 (Brünnhilde's "Triff ihn!", Wotan's spear, Nothung
shattered and Siegmund's death), 2004 to 2011 (Brünnhilde's flight with Sieglinde), 2033 to 2035 (Hunding struck
dead) and 2041 to the end of the act (Wotan's fury), spliced, as Solti's 1958 Vienna Philharmonic recording takes
them. The notes come from the Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py), played by the
full orchestra; the tremolos of the storm and of Siegmund's death on tremolo strings. Over the score, as a staging
would: storm wind all through, roaring up in his fury, a rush of air as she streaks in and steel on steel at the
last blows, a boom as Wotan towers up, the sword shattering with cymbal and gong and its shards tinkling down, the
spear's thrust and Siegmund's fall, her horse galloping away with Sieglinde, a rush of air for the wave of Wotan's
hand and a boom as Hunding drops, the spear striking with boom and steel, thunder with every bolt where it strikes,
and Wotan's horse thundering after her. The effects lead the fight, the spear and the shattering, back far off for
the dying fall, come halfway back for her flight and "Geh!", and let the storm lead Wotan's fury until it settles.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK19'
TITLE = 'Siegmund Falls'
KIND = 'show'
DESCRIPTION = ('Brünnhilde shields Siegmund in the fight, until Wotan appears in the storm and Siegmund\'s sword '
               'shatters on his spear. Hunding kills the disarmed hero, Brünnhilde gallops away with Sieglinde '
               'and the pieces of the sword, and Wotan rides after her in a fury.')
VOICEOVER = ('The sword is broken, and the god who gave it has let his son die. '
             'Now watch the god turn his anger on the one who tried to save him.')

EX = excerpt(__file__)                      # Act II, bars 1981-1993 + 2004-2011 + 2033-2035 + 2041-end, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']


def loudest(t0, t1):
    """The onset in [t0, t1) where the most loud notes strike together."""
    c = {}
    for t, d, m, v, h in EX['notes']:
        if t0 <= t < t1 and v >= 100:
            c[t] = c.get(t, 0) + 1
    return max(c, key=lambda k: (c[k], -k)) if c else t0


T_WOTAN = BAR[1986]                         # "Zurück vor dem Speer!": the red glow, Wotan
T_SHATTER = BAR[1987]                       # "In Stücken das Schwert!": Nothung shatters on the spear
T_STAB = loudest(BAR[1988] - 0.3, BAR[1989])            # the spear goes in
T_THRUST = T_STAB - 0.6                     # Hunding lunges
T_FATE = BAR[1989]                          # the orchestra's dying fall
T_OUT = BAR[1993]                           # Siegmund's light is gone
T_GATHER = BAR[2004]                        # Brünnhilde gathers the shards
T_TO_SL = BAR[2006]                         # runs to Sieglinde
T_LIFT = BAR[2007]                          # lifts her onto the horse
T_GALLOP = BAR[2008]                        # and away
RBEAT = 0.3
T_GONE = BAR[2011] + 1.0
T_GRIEF = BAR[1991]                         # Wotan over the body
T_GEH = BAR[2033]                           # "Geh! Geh!"
T_WAVE = BAR[2033] + 1.0                    # the wave of his hand
T_DEAD = BAR[2034]                          # Hunding falls
T_FURY = BAR[2041]                          # "Doch Brünnhilde!"
SPEARS = [BAR[2049], BAR[2053]]             # the spear striking across the porch
SBEAT = 0.42
T_RIDE = BAR[2056]                          # he rides after her
T_AWAY = BAR[2061]
T_CLEAR = BAR[2062]                         # the storm settles into the clouds of the Valkyries' rock
CLOCK = 80.0 * 18                           # shared clock: this is the 19th scene

SIEG, HUND, WOTAN, BRUNN, SL = range(5)
BLUE = hexc('#30a8ff')
AMBER = hexc('#ffa860')
HRED = hexc('#8a0020')
WBLUE = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
REDGLOW = hexc('#ff2010')
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
STEEL = hexc('#e8f8ff')
STORM = hexc('#5a6a8a')
CLOUD = hexc('#2a3448')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
PALE = hexc('#a0b0c0')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')



def tremolos(notes, gap=0.09, short=0.12):
    """Merge the piano reduction's repeated-note tremolos (the same note struck again and again, each shorter than
    `short`) into single long notes: [t, d, midi, vel, hand, n] with n the number of strokes merged."""
    out, runs = [], {}
    for t, d, m, v, h in sorted(notes):
        r = runs.get((h, m))
        if r and d < short and r[1] < short * r[5] and t - (r[0] + r[1]) < gap:
            r[1] = t + d - r[0]
            r[3] = max(r[3], v)
            r[5] += 1
            continue
        r = [t, d, m, v, h, 1]
        runs[(h, m)] = r
        out.append(r)
    return out


def accents(t0, t1, vmin, n, space):
    """Times in [t0, t1) where n or more notes louder than vmin strike together, at least `space` apart."""
    c = {}
    for t, d, m, v, h in EX['notes']:
        if t0 <= t < t1 and v >= vmin:
            c[round(t, 2)] = c.get(round(t, 2), 0) + 1
    out = []
    for k in sorted(k for k, v in c.items() if v >= n):
        if not out or k - out[-1] >= space:
            out.append(k)
    return out


CLASHES = accents(0.3, T_WOTAN - 0.3, 100, 3, 0.8)      # the last blows of the fight
WHERE = ['Right', 'Left', 'Porch', 'Side', 'Right', 'Porch', 'Left', 'Side']
STRIKES = ([(t, WHERE[k % 8]) for k, t in enumerate(accents(0.5, T_WOTAN - 0.5, 110, 4, 2.5))]
           + [(T_FURY + 0.6, 'all')]
           + [(t, WHERE[k % 8]) for k, t in enumerate(accents(T_FURY + 1.5, D - 1.0, 113, 4, 1.6))])


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note of the excerpt (tremolos merged), tagged: (time, seconds, midi, velocity, part, n), n the strokes
    of a merged tremolo. Parts: 'fate' the dying fall after the blow, 'spear' the left hand's falling steps from
    SPEARS[1], otherwise the stretch of the story it falls in ('fight', 'flight', 'geh', 'fury')."""
    N = []
    for t, d, m, v, h, n in tremolos(EX['notes']):
        if t < T_FATE - 0.01:
            part = 'fight'
        elif t < T_GATHER - 0.01:
            part = 'fate'
        elif t < T_GEH - 0.01:
            part = 'flight'
        elif t < T_FURY - 0.01:
            part = 'geh'
        elif SPEARS[1] - 0.01 <= t < T_RIDE and h == 1:
            part = 'spear'
        else:
            part = 'fury'
        N.append((t, d, m, v, part, n))
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
    """Per frame: where Siegmund, Hunding, Wotan, Brünnhilde and Sieglinde are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((5, F))
    rate = np.full((5, F), 4.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    S0, H0, W0 = at(G, 'Porch Front', 0.35), at(G, 'Porch Front', 0.62), at(G, 'Porch Front', 0.5)
    B0, L0 = at(G, 'Porch Right', 0.3), at(G, 'Left', 0.7)
    set_(SIEG, 0, D, S0, 6.0)
    set_(SIEG, T_STAB, T_OUT, S0 - 10, 2.0)                                     # staggering back as he falls
    set_(HUND, 0, D, H0, 6.0)
    set_(HUND, T_THRUST, T_STAB + 0.4, S0 + 30, 9.0)
    set_(HUND, T_STAB + 0.4, D, S0 + 60, 2.0)
    set_(WOTAN, 0, D, W0, 6.0)
    set_(WOTAN, T_GRIEF, T_WAVE, S0 + 32, 0.9)                                  # bending over the body
    set_(WOTAN, T_WAVE, T_RIDE, W0 - 10, 2.0)
    # Brünnhilde: across the shards, to Sieglinde, and away along Left and Side
    marks = [(0.0, B0 + 140), (1.2, S0 + 5), (T_SHATTER, S0 + 5), (T_SHATTER + 0.9, B0), (T_GATHER, B0),
             (T_GATHER + 1.2, at(G, 'Porch Front', 0.56)),
             (T_TO_SL - 0.2, at(G, 'Porch Front', 0.28)), (T_LIFT - 0.2, L0 + 4), (T_GALLOP, L0 + 4),
             (T_GALLOP + 1.6, at(G, 'Left', 0.15)), (T_GONE, -140.0), (D, -140.0)]
    ts, ds = zip(*marks)
    set_(BRUNN, 0, D, np.interp(t, ts, ds), 8.0)
    set_(SL, 0, D, L0, 6.0)
    set_(SL, T_LIFT + 0.3, D, np.interp(t, ts, ds) + 16, 9.0)                   # on the horse, just behind her
    # Wotan rides after her
    set_(WOTAN, T_RIDE, D, np.interp(t, (T_RIDE, T_AWAY), (W0 - 10, -260.0)), 7.0)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(5)])
    mid = 0.5 * (pos[SIEG] + pos[HUND])
    for tc in CLASHES:                         # the last blows: both lunge to the middle and spring back
        a = np.exp(-((t - tc) / 0.12) ** 2)
        pos[SIEG] = pos[SIEG] + (mid - 6 - pos[SIEG]) * a
        pos[HUND] = pos[HUND] + (mid + 6 - pos[HUND]) * a
    return dict(t=t, pos=pos)


def storm_bed(d, tt, porch, wild):
    """Act II's storm: dark slate and navy, rolling with grey-blue billows; wilder and brighter in his fury."""
    r1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 380 - 0.05 * tt))
    r2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 150 + 0.09 * tt) + 2)
    r3 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 - 0.32 * tt) + 1)          # the gale, racing over in his fury
    return (light(CLOUD, 0.38 + 0.55 * r1 ** 1.5) + light(NAVY, 0.4)
            + light(STORM, (0.08 + 0.6 * (r1 * r2) ** 2) * (0.7 + 0.5 * wild) + 0.45 * wild * r3 ** 3))


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def render(G, seed=19):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    pfm = (G.seg_of == 'Porch Front').astype(float)
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))       # the rock's stones, every scene
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    S0 = at(G, 'Porch Front', 0.35)
    p0, p1 = at(G, 'Porch Front', 0.0), at(G, 'Porch Front', 1.0)
    shards = np.sort(rng.uniform(at(G, 'Porch Front', 0.27), at(G, 'Porch Front', 0.57), 10))
    sh_ph = rng.uniform(0, 2 * np.pi, 10)
    fate = np.array(sorted({e[0] for e in N if e[4] == 'fate' and e[2] >= 48}))
    spear_n = [(e[0], e[2]) for e in N if e[4] == 'spear']
    gut = Flicker(rng, 1, 1.5, 6.0)
    rain_f = Flicker(rng, G.N, 4.0, 11.0)
    tw = Flicker(rng, G.N, 2.0, 6.0)
    seg_d = {s: (G.pd[G.seg[s]].min(), G.pd[G.seg[s]].max()) for s in G.seg}

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def bolt(age, a, b, k):
        """A fork of lightning from a to b: grows in 60 ms, flickers three times, gone in a second."""
        if not 0 <= age < 1.0:
            return np.zeros(G.N)
        reach = a + (b - a) * min(1.0, age / 0.06)
        lo, hi = min(a, reach), max(a, reach)
        fl = sum(np.exp(-((age - s) / 0.04) ** 2) for s in (0.0, 0.12, 0.3)) + 0.45 * np.exp(-age / 0.3)
        return ((d >= lo) & (d <= hi)) * jag[k % len(jag)] * min(fl, 1.2)

    def span_of(where):
        if where == 'all':
            return 0.0, L
        if where == 'Porch':
            return seg_d['Porch Left'][0], seg_d['Porch Right'][1]
        return seg_d[where]

    picked = np.full(10, np.inf)
    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        fr = np.zeros((G.N, 3))
        P = C['pos'][:, f]

        # the storm: roaring as the fight ends, hushed while Siegmund dies, wild in Wotan's fury, then settling
        wild = (0.6 * (1 - smoothstep(T_STAB, T_STAB + 2.5, t)) + smoothstep(T_FURY - 0.3, T_FURY + 1.5, t)
                - 0.55 * smoothstep(T_AWAY, T_CLEAR + 8, t))
        hush = 1 - 0.35 * smoothstep(T_STAB, T_STAB + 3, t) * (1 - smoothstep(T_FURY - 3, T_FURY, t))
        clear = smoothstep(T_CLEAR, D - 3.0, t)
        bed = storm_bed(d, tt, porch, max(wild, 0)) * hush
        fr += bed * (1 - clear) + rock_bed(d, tt, porch, stone) * clear
        rain = max(wild, 0) * (1 - smoothstep(66, 77, t))
        if rain > 0:
            fr += light(FLASH, 0.32 * rain * smoothstep(0.9, 1.0, rain_f(t)))

        # the spear's steel line across the porch: held at the start, struck again with each spear call
        line = 0.42 * smoothstep(T_WOTAN + 0.4, T_SHATTER - 0.2, t) * (1 - smoothstep(T_STAB + 0.5, T_STAB + 2.8, t))
        for ts in SPEARS[:2]:
            if ts <= t < ts + 12 * SBEAT:
                line = max(line, 0.75 * np.exp(-(t - ts) / 0.25) + 0.38 * (1 - smoothstep(ts + 9 * SBEAT, ts + 12 * SBEAT, t)))
        if line > 0:
            fr += light(SPEAR, line * pfm * smoothstep(p0 - 5, p0 + 25, d) * smoothstep(p1 + 5, p1 - 25, d))
        for tn, m in spear_n:                               # each note of it a bright step walking down the line
            if tn <= t < tn + 0.6 and tn < T_RIDE:
                q = p1 - (p1 - p0) * np.clip((58 - m) / 18, 0, 1)
                fr += light(WHITE, 0.8 * np.exp(-(t - tn) / 0.18) * blob(q, 14))

        # the last blows of the fight: a blue-white spark where they meet
        for tc in CLASHES:
            if tc <= t < tc + 0.8:
                age = t - tc
                c = np.interp(tc, C['t'], 0.5 * (C['pos'][SIEG] + C['pos'][HUND]))
                fr += light(WHITE, 0.95 * np.exp(-age / 0.1) * blob(c, 14))
                r = 30 + 450 * age
                fr += light(BLUE, 0.65 * np.exp(-age / 0.25) * np.exp(-((np.abs(d - c) - r) / 28) ** 2))
                fr += light(SILVER, 0.4 * np.exp(-age / 0.3) * np.exp(-((np.abs(d - c) - 0.7 * r) / 25) ** 2))
        # Nothung in his hand until it shatters; then one white burst and the shards flung out and falling back
        if t < T_SHATTER:
            ps0 = P[SIEG]
            blade = smoothstep(ps0 - 34, ps0 - 30, d) * smoothstep(ps0 - 12, ps0 - 16, d)
            fr += light(STEEL, (0.8 + 0.2 * tw(t)) * blade)
        if T_SHATTER <= t < T_SHATTER + 2.5:
            age = t - T_SHATTER
            fr += light(WHITE, 1.0 * np.exp(-age / 0.15) + 0.8 * np.exp(-age / 0.6) * blob(S0, 60 + 600 * age))
            for k in range(10):
                land = shards[k]
                fly = S0 + (land - S0 + (k - 4.5) * 120) * np.sin(np.pi * min(age / 0.8, 1.0) * 0.5) * (1 - smoothstep(0.8, 1.6, age)) \
                    + (land - S0) * smoothstep(0.8, 1.6, age)
                fr += light(STEEL, 0.9 * blob(fly, 7))

        # Siegmund: struck, guttering, out; a pale glow where he lies, until Wotan turns away
        ps = P[SIEG]
        if t < T_OUT + 0.5:
            g = 1 - smoothstep(T_STAB + 0.2, T_OUT, t)
            sputter = 1 - 0.55 * smoothstep(T_STAB, T_STAB + 1.5, t) * max(0.0, float(gut(t)[0])) ** 2
            b = 0.85 * g * sputter
            fr += light(BLUE, b * blob(ps, 22) + 0.4 * b * blob(ps, 110))
        ghost = smoothstep(T_STAB + 1.0, T_OUT, t) * (1 - smoothstep(T_WAVE, T_WAVE + 3, t))
        if ghost > 0:
            fr += light(PALE, 0.32 * ghost * blob(S0 - 10, 26) * (0.8 + 0.2 * last(fate, t, 0.5)))
        if T_STAB <= t < T_STAB + 1.2:                      # the blow
            age = t - T_STAB
            fr += light(WHITE, 1.1 * np.exp(-age / 0.1) * blob(S0 + 4, 30))
            fr += light(HRED, 1.0 * np.exp(-age / 0.3) * blob(S0 + 4, 120))
            r = 40 + 500 * age ** 0.6
            fr += light(BLUE, 0.7 * (1 - age / 1.2) * np.exp(-((np.abs(d - S0) - r) / 35) ** 2))

        # Hunding: red in his own shadow, the spear point ahead of him; struck down by a wave of Wotan's hand
        ph = P[HUND]
        hb = 0.85 * (1 + 0.6 * np.exp(-max(t - T_DEAD, 0) / 0.2) * (t >= T_DEAD)) * (1 - smoothstep(T_DEAD + 0.2, T_DEAD + 1.8, t))
        ember = 0.3 * smoothstep(T_DEAD + 0.8, T_DEAD + 1.8, t) * (1 - smoothstep(T_DEAD + 2, T_FURY, t))
        hw = 22 * (1 - 0.5 * smoothstep(T_DEAD, T_DEAD + 1.6, t))
        if hb > 0.01 or ember > 0:
            fr *= 1 - 0.65 * (hb / 0.85) * blob(ph, 70)[:, None] * (1 - blob(ph, hw))[:, None]
            fr += light(HRED, 1.1 * hb * blob(ph, hw) + 0.45 * hb * blob(ph, 90) + ember * blob(ph, 14))
            tip = ph - 28 if t < T_THRUST else ph - 28 - 30 * smoothstep(T_THRUST, T_STAB, t)
            fr += light(HRED * 0.6 + SPEAR * 0.4, 0.7 * (hb / 0.85) * (1 - smoothstep(T_STAB, T_STAB + 1, t)) * blob(tip, 8))
        if T_THRUST <= t < T_STAB + 0.3:                    # the lunge, a red streak
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(1, 13, 2)):
                q = C['pos'][HUND][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 18) * (1 - j / 6.5))
            fr += light(HRED, 0.9 * trail)

        # Wotan: towering, red storm glow; bowed in grief; the wave; fury; riding off as a storm
        pw = P[WOTAN]
        vis = smoothstep(-200, 40, pw) * smoothstep(T_WOTAN - 0.3, T_WOTAN + 1.2, t)
        grief = smoothstep(T_GRIEF - 1, T_GRIEF + 2, t) * (1 - smoothstep(T_WAVE - 0.5, T_WAVE, t))
        fury = smoothstep(T_FURY - 0.2, T_FURY + 0.6, t)
        riding = smoothstep(T_RIDE, T_RIDE + 1.0, t)
        quiet = smoothstep(T_STAB, T_STAB + 3, t) * (1 - fury)
        wb = vis * (0.75 - 0.2 * grief + 0.2 * fury)
        ww = 34 + 10 * fury - 6 * grief
        fr += light(WBLUE, wb * blob(pw, ww) + 0.3 * wb * blob(pw, 170 + 80 * fury))
        red = vis * (0.32 * (1 - quiet) + 0.35 * fury * (0.8 + 0.2 * np.sin(2 * np.pi * 1.7 * t)))
        fr += light(REDGLOW, red * blob(pw, 230 + 120 * fury))
        rage = fury * (1 - smoothstep(T_AWAY, T_CLEAR, t))
        if rage > 0:                                        # his wrath: surges of blue and red rolling out over the house
            ph_ = ((t - T_FURY) / 2.4) % 1.0
            for k in range(2):
                r = 1300 * ((ph_ + 0.5 * k) % 1.0)
                env = 1 - ((ph_ + 0.5 * k) % 1.0)
                band = np.exp(-((np.abs(d - pw) - r) / 200) ** 2) * env
                fr += light(WBLUE, 0.7 * rage * band) + light(REDGLOW, 0.4 * rage * band ** 2)
            fr += light(WBLUE, 0.3 * rage * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 300 - 0.4 * tt))))
        if riding > 0:                                      # the spear streaking ahead of him, his storm behind
            fr += light(SPEAR, 0.7 * riding * vis * smoothstep(pw - 140, pw - 20, d) * smoothstep(pw + 10, pw - 20, d))
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 40, 3)):
                q = C['pos'][WOTAN][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 45) * (1 - j / 13.5))
            fr += light(WBLUE, 0.75 * trail * riding) + light(REDGLOW, 0.35 * trail * riding)
        if T_WAVE <= t < T_WAVE + 1.4:                      # "Geh hin!": a wave of blue rolling out over the porch
            age = t - T_WAVE
            r = 20 + 380 * smoothstep(0, 1.0, age)
            fr += light(WBLUE, 0.95 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 40) ** 2))
            fr += light(SPEAR, 0.6 * (1 - age / 1.4) * np.exp(-((np.abs(d - pw) - r) / 12) ** 2))

        # Brünnhilde: gathering the shards, lifting Sieglinde, galloping away with both
        pb = P[BRUNN]
        bvis = smoothstep(-120, 30, pb)
        recoil = 1 - 0.25 * smoothstep(T_STAB, T_STAB + 0.3, t) * (1 - smoothstep(T_GATHER - 0.6, T_GATHER, t))
        gallop = 0.85 + 0.15 * np.cos(2 * np.pi * (t - T_GALLOP) / (1.5 * RBEAT)) if t >= T_GALLOP else 1.0
        shield = smoothstep(0.8, 1.6, t) * (1 - smoothstep(T_SHATTER, T_SHATTER + 0.4, t))
        bb = bvis * 0.82 * recoil * gallop
        if shield > 0:
            fr += light(SILVER, 0.35 * shield * blob(P[SIEG], 70) * (0.8 + 0.2 * np.sin(2 * np.pi * 1.5 * t)))
        fr += light(SILVER, bb * blob(pb, 20) + 0.35 * bb * blob(pb, 100))
        for k in range(3):
            q = pb + 20 * np.sin(2 * np.pi * (0.8 * tt + k / 3))
            fr += light(GOLD, 0.75 * bvis * (0.7 + 0.3 * np.sin(2 * np.pi * (3.1 * tt + k))) * blob(q, 5))
        if abs(pb - C['pos'][BRUNN][max(f - 6, 0)]) > 18:   # a silver comet when she moves fast
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 26, 2)):
                q = C['pos'][BRUNN][max(f - lag, 0)]
                trail = np.maximum(trail, blob(q, 22) * (1 - j / 12.5))
            fr += light(SILVER, 0.55 * bvis * trail)
        newly = (picked == np.inf) & (np.abs(shards - pb) < 12) & (t >= T_GATHER)
        picked[newly] = t
        for k in range(10):                                 # the shards: on the porch, then flying with her
            if t < T_SHATTER + 0.8:
                continue
            if t < picked[k]:
                tws = 0.6 + 0.4 * np.sin(2 * np.pi * 2.3 * t + sh_ph[k])
                fr += light(STEEL, 0.75 * tws * blob(shards[k], 4.5))
            elif t < picked[k] + 0.5:
                fr += light(WHITE, 0.9 * np.exp(-(t - picked[k]) / 0.15) * blob(shards[k], 10))
        ng = int((picked <= t).sum())
        for k in range(min(ng, 4)):
            q = pb + 30 * np.sin(2 * np.pi * (1.3 * tt + k / 4 + 0.1))
            fr += light(STEEL, 0.65 * bvis * blob(q, 4))

        # Sieglinde: collapsed and dim; then up on the horse, amber close behind the silver
        pl = P[SL]
        lift = smoothstep(T_LIFT, T_LIFT + 1.0, t)
        lb = smoothstep(-120, 30, pl) * (0.52 + 0.2 * lift) * (0.92 + 0.08 * np.sin(2 * np.pi * 0.3 * tt))
        fr += light(AMBER, lb * blob(pl, 18 + 4 * lift) + 0.4 * lb * blob(pl, 100))
        if T_LIFT <= t < T_LIFT + 1.2:
            age = t - T_LIFT
            fr += light(WHITE * 0.5 + AMBER * 0.5, 0.7 * np.exp(-age / 0.3) * blob(pl, 40))

        # lightning: in his fury, and on in the storm after he has gone
        for i, (ts, where) in enumerate(STRIKES):
            age = t - ts
            if not 0 <= age < 1.0:
                continue
            a, b = span_of(where)
            if where == 'all':
                fr += light(FLASH, 0.85 * np.exp(-age / 0.12) * np.ones(G.N))
                fr += light(WHITE, bolt(age, pw, 0.0, i) + bolt(age, pw, L, i + 1))
            else:
                mid = 0.5 * (a + b)
                fr += light(WHITE, 0.9 * bolt(age, mid, (a if i % 2 else b), i))
                fr += light(FLASH, 0.35 * np.exp(-age / 0.2) * blob(mid, 0.6 * (b - a)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the full orchestra; the tremolos on tremolo strings; cymbal, gong and timpani on the
    shattering, the blow, Hunding's fall and the lightning."""
    o = Orchestra(M, level=1.85)
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    S0 = pan_at(at(G, 'Porch Front', 0.35))
    plain = []
    for t, d, m, v, part, n in compose():
        if n >= 3:
            o.play('cellos trem' if m < 55 else 'violins trem', m, t, d, v, gain=0.7)
            if m < 43:
                o.play('basses', m + (12 if m < 28 else 0), t, d, v - 10, gain=0.5)
        elif part == 'spear':
            o.play('trombones', m, t, d, v, gain=0.7)
            o.play('tuba', m - 12 if m >= 40 else m, t, d, v - 6, gain=0.5)
        else:
            plain.append([t, d, m, v, 0 if m >= 60 else 1])
    o.tutti(plain, size=lambda t: 0.6 if T_FATE <= t < T_FURY else 1.0)
    o.effects([(0.0, 0), (T_SHATTER + 2.0, 0), (T_FATE, -4), (T_FATE + 1.5, -12), (T_GATHER - 0.5, -12),
               (T_GATHER + 0.5, -4), (T_GONE, -4), (T_GEH - 0.5, -5), (T_DEAD + 1.0, -3), (T_FURY - 0.3, 0),
               (T_CLEAR, 0), (D, -6)])
    from pixelhome.audio import whoosh
    C = choreography(G)
    pp = lambda k: (lambda t: pan_at(np.interp(t, C['t'], C['pos'][k])))
    WH = {'Right': 0.8, 'Left': -0.7, 'Porch': 0.0, 'Side': -0.9, 'all': 0.0}
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    # the storm over the whole scene, roaring up in his fury and settling at the end
    o.wind(0.0, D, level=lambda tt: 0.45 + 0.55 * smoothstep(T_FURY, T_FURY + 3, tt) * (1 - smoothstep(T_CLEAR, D, tt))
           - 0.25 * smoothstep(T_FATE, T_FATE + 2, tt) * (1 - smoothstep(T_FURY - 1, T_FURY, tt)), pan=0.0)
    # Brünnhilde streaks in over him; the last blows of the fight
    o.M.add('fx', whoosh(1.3, 4000, 600, 0.7, seed=19), 0.0, 0.7, pp(BRUNN)(0.6))
    for tc in CLASHES:
        o.clash(tc, pp(SIEG)(tc) * 0.5 + pp(HUND)(tc) * 0.5, 120, 1.1)
        o.hit('timpani', tc, 100, pitch=-1, gain=0.4, pan=S0)
    # Wotan towers out of the red glow
    o.hit('cymbal swell', T_WOTAN - 2.2, 100, gain=0.45, pan=pp(WOTAN)(T_WOTAN))
    o.boom(T_WOTAN, pp(WOTAN)(T_WOTAN), 0.9)
    # Nothung shatters on the spear: the burst, then the shards falling back to lie on the porch
    o.shatter(T_SHATTER, S0, 1.3)
    o.hit('crash', T_SHATTER, 127, gain=0.7, pan=S0)
    o.hit('gong', T_SHATTER, 120, gain=0.6, pan=S0)
    o.hit('timpani', T_SHATTER, 127, pitch=-2, gain=0.6, pan=S0)
    for k in range(10):
        o.M.add('fx', tri.play(90 - 4 * k), T_SHATTER + 0.35 + 0.16 * k, 0.135, S0 + 0.7 * ((k * 0.37) % 1 - 0.5))
    # Hunding lunges and drives the spear in; Siegmund falls
    o.M.add('fx', whoosh(0.5, 900, 5000, 0.8, seed=29), T_THRUST, 0.9, pp(HUND)(T_THRUST))
    o.hit('crash', T_STAB, 115, gain=0.5, pan=S0)
    o.hit('bass drum', T_STAB, 124, gain=0.8, pan=S0, fx=True)
    o.hit('brake drum', T_STAB, 110, gain=0.4, pan=S0, fx=True)
    o.boom(T_STAB + 1.6, S0, 0.6)                                            # he falls
    o.hit('gong scrape', T_FATE, 90, gain=0.4, pan=S0, fx=True)             # his light gutters out
    # she gathers the shards, lifts Sieglinde and gallops away along Left and Side
    for k in range(6):
        o.M.add('fx', tri.play(80), T_GATHER + 0.25 * k, 0.126, pp(BRUNN)(T_GATHER + 0.25 * k))
    o.hit('bass drum', T_LIFT, 100, gain=0.4, pan=pp(SL)(T_LIFT), fx=True)
    o.gallop(T_GALLOP - 0.4, T_GONE, beat=1.5 * RBEAT, pan=pp(BRUNN), v=116, gain=1.1)
    o.M.add('fx', whoosh(T_GONE - T_GALLOP, 300, 2500, 0.7, seed=39), T_GALLOP, 0.7, -0.7)
    # "Geh!": the wave of his hand, Hunding falls dead
    o.M.add('fx', whoosh(1.0, 300, 3000, 0.8, seed=49), T_WAVE - 0.3, 0.9, pp(WOTAN)(T_WAVE))
    o.boom(T_DEAD, pp(HUND)(T_DEAD), 0.8)
    o.hit('timpani', T_DEAD, 120, pitch=-4, gain=0.6)
    o.hit('gong', T_DEAD, 100, gain=0.4)
    # his fury: the spear striking across the porch, thunder with every bolt, and he rides after her
    for ts in SPEARS:
        o.boom(ts, pp(WOTAN)(ts), 0.8)
        o.clash(ts, pp(WOTAN)(ts), 112, 0.8)
    for ts, where in STRIKES:
        o.thunder(ts, near=1.0 if where in ('all', 'Porch') else 0.7, pan=WH[where],
                  gain=1.1 if where == 'all' else 0.85)
    o.gallop(T_RIDE, T_AWAY, beat=0.34, pan=pp(WOTAN), v=124, gain=1.2)
    o.M.add('fx', whoosh(T_AWAY - T_RIDE + 1.0, 200, 2000, 0.9, seed=59), T_RIDE, 0.9, -0.6)
