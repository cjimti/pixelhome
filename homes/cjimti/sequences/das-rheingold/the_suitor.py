"""The Suitor from Below: Alberich (a smouldering red lump with a muddy halo) tries to climb Porch Left to the
Rhinemaidens and slides back down the slimy stones three times, each slip a splash of mud ("Garstig glatter
glitschiger Glimmer! Wie gleit' ich aus!"). Then the wet gets up his nose: three wheezing swells and a sneeze
that sprays the porch with green-brown muck. Woglinde (silver) teases him and slips away from his lunges;
Wellgunde (green) lets him close, then bursts out "Pfui! du haariger, höckriger Geck!" and zips off. Flosshilde
(violet), cruellest because sweetest, has him in her arms in the middle of the porch, the whole porch glowing rose,
until she slips out and her sisters burst out laughing: the rose shatters into glitter of their three colours over
the entire house ("Wie billig am Ende vom Lied!"), and they laugh again. Then his rage ("Wehe! ach wehe!"): he
streaks after them across the house, each time the maiden leaps away and the run he lands on flashes red, until
he is spent and shakes his fist at them ("Fing' eine diese Faust!"), as a faint gold light begins to glimmer on
the rock behind him.

The music is Wagner's own: bars 233-245, 304-309, 399-409 and 480-506 of Scene 1, timed bar by bar like Barenboim's
1991 Bayreuth recording. The orchestra comes from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py):
his slithering on bassoons, clarinets and low strings, the maidens' mockery light in the strings and woodwinds,
his rage in the full orchestra. The maidens' lines are from the printed vocal score (Klindworth, Schott;
archive.org dasrheingold00wagn2, pp. 17, 23-24): Wellgunde's insult on flute, the laughter on oboe and flute,
Flosshilde on clarinet; Alberich's lines stay in the orchestra. The stage sounds lead where they tell the story
(the slithering and splashing, the sneeze, the thuds of his lunges) and drop away under the singing.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG03'
TITLE = 'The Suitor from Below'
KIND = 'show'
DESCRIPTION = ('Alberich the dwarf slips and slides, sneezes, and tries his luck with each Rhinemaiden in turn. '
               'They lead him on, laugh in his face, and leave him raging, just as something starts to glow on '
               'the rock behind him.')
VOICEOVER = ('Up from the dark comes Alberich, wet, clumsy, and in love with all three of them at once. '
             'The river daughters think this is the funniest thing that has ever happened.')

EX = excerpt(__file__)                      # bars 233-245, 304-309, 399-409, 480-506, Barenboim 1991
D = EX['seconds']
SEG = [x['start'] for x in EX['segments']] + [D]


def bt(pos):
    """The time of a (fractional) bar position; the four passages share no bar numbers."""
    bars = [(b, t) for b, t in EX['bars'] if any(x['measures'][0] <= b <= x['measures'][1] for x in EX['segments']
                                                  if x['measures'][0] <= pos <= x['measures'][1])]
    return float(np.interp(pos, [b for b, _ in bars], [t for _, t in bars]))


BEAT = (bt(492) - bt(491)) / 3              # a quarter note of the rage's 6/8
SLIPS = [bt(234.4) - 1.8, bt(236.1) - 1.8, bt(238.3) - 1.8]     # three tries at the rock, each sliding back
AH = [bt(239.25), bt(239.75), bt(240.25)]  # "Feuchtes Naß füllt mir die Nase"
CHOO = bt(241.25)                           # the sneeze
T_WOG = bt(242.0)                           # Woglinde comes down to tease him
LUNGE_W = [bt(243.6), bt(244.7)]            # he lunges at her, twice
T_WELL = bt(243.0)                          # Wellgunde drifts in close
T_INSULT = bt(305)                          # "Pfui! du haariger, höckriger Geck!"
T_FLO = SEG[1] + 2.0                        # Flosshilde glides to meet him
T_MERGE = SEG[2]                            # in her arms
T_BREAK = bt(401.17)                        # she slips out; they laugh
T_RAGE = bt(408)                            # "Wehe! ach wehe!"
LUNGES = [SEG[3] + 0.2, bt(484), bt(488), bt(492), bt(496), bt(500)]     # every four bars of the rage
T_SPENT = bt(502.5)
FIST = bt(504.333)                          # "Fing' eine diese Faust!"
T_GLIMMER = D - 6.0

WOG, WELL, FLO = 0, 1, 2
CHASE = [(FLO, ('Porch Right', 0.5)), (WOG, ('Left', 0.3)), (WELL, ('Porch Left', 0.4)), (FLO, ('Right', 0.6)),
         (WOG, ('Porch Front', 0.5)), (WELL, ('Right', 0.3))]     # whom he lunges at, and where she leaps to

# The maidens' lines, from the vocal score: (bar, start, length in eighths of 6/8, note, who)
VOICE = ([(305, 0, 1, 'G5', 1), (305, 2, 1, 'Eb5', 1), (305, 3, 1.5, 'D5', 1), (305, 4.5, .5, 'Bb4', 1),
          (305, 5, 1, 'G4', 1), (306, 0, 1.5, 'Eb5', 1), (306, 1.5, .5, 'C5', 1), (306, 2, 1, 'A4', 1),
          (306, 3, 2, 'E5', 1), (307, 0, 2, 'Eb5', 1), (307, 2, 1, 'C5', 1), (307, 3, 1.5, 'E5', 1),
          (307, 4.5, .5, 'C5', 1), (307, 5, 1, 'A4', 1), (308, 0, 1.5, 'F5', 1), (308, 1.5, .5, 'D5', 1),
          (308, 2, 1, 'C5', 1), (308, 3, 2, 'B4', 1)] +
         [(401, k, 1, 'E5', 0) for k in range(1, 6)] + [(402, 0, 1, 'E5', 0)] +
         [(401, k, 1, 'D5', 1) for k in range(1, 6)] + [(402, 0, 1, 'Db5', 1)] +
         [(404, 1, 1, 'C5', 2), (404, 2, 1, 'F5', 2), (404, 3, 1, 'D5', 2), (404, 4, 1, 'C5', 2),
          (404, 5, 1, 'Ab4', 2), (405, 0, 4, 'Eb5', 2), (405, 4, 1, 'C5', 2), (405, 5, 1, 'D5', 2),
          (406, 0, 1, 'Eb5', 2)] +
         [(407, k, 1, 'F5', 0) for k in range(1, 6)] + [(408, 0, 1, 'Gb5', 0)] +
         [(407, k, 1, 'Eb5', 1) for k in range(1, 6)] + [(408, 0, 1, 'Eb5', 1)])
COLOR = [hexc('#c0f4ff'), hexc('#20ff90'), hexc('#8c60ff')]
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
ALB = hexc('#ff1000')
HOT = hexc('#ff8a20')
MUD = hexc('#5a1200')
MUCK = hexc('#7a9010')
ROSE = hexc('#ff2a80')
GOLD = hexc('#ffb000')
WHITE = hexc('#ffffff')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who). 'sing' is a maiden's line (who: which one); the
    excerpt's notes are 'orch'."""
    N = []
    for b, x, n, name, who in VOICE:
        t0 = bt(b + x / 6)
        N.append((t0, bt(b + (x + n) / 6) - t0, note(name), 100, 'sing', who))
    for t, d, m, v, h in EX['notes']:
        N.append((t, d, m, v, 'orch', h))
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
    """Per frame: where each maiden and Alberich are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    P = {k: at(G, *k) for k in [('Porch Front', 0.55), ('Right', 0.45), ('Porch Right', 0.45), ('Porch Left', 0.42),
                                ('Porch Right', 0.5), ('Right', 0.5), ('Right', 0.85), ('Porch Front', 0.35),
                                ('Porch Front', 0.7), ('Left', 0.5), ('Porch Left', 0.75), ('Porch Front', 0.4),
                                ('Left', 0.55), ('Porch Right', 0.7)]}
    tgt = np.zeros((4, F))                  # three maidens, then Alberich
    rate = np.full((4, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    bob = [12 * np.sin(2 * np.pi * t / 1.4 + k) for k in range(3)]
    set_(WOG, 0, D, P['Porch Front', 0.55] + bob[0], 3.0)
    set_(WELL, 0, D, P['Right', 0.45] + bob[1], 3.0)
    set_(FLO, 0, D, P['Porch Right', 0.45] + bob[2], 3.0)
    A = P['Porch Left', 0.42]
    set_(3, 0, D, A, 6.0)
    for ta in SLIPS:
        for k in range(3):
            set_(3, ta + 0.6 * k, ta + 0.6 * (k + 1), A + 45 * (k + 1), 9.0)
        set_(3, ta + 1.8, ta + 2.5, A, 16.0)

    # Woglinde comes down to him, twice; he lunges, twice; she is gone
    set_(WOG, T_WOG, LUNGE_W[0], A + 180 + bob[0], 1.6)
    set_(3, T_WOG + 1.5, LUNGE_W[0], A + 90, 2.0)
    set_(3, LUNGE_W[0], LUNGE_W[0] + 0.5, A + 230, 18.0)
    set_(WOG, LUNGE_W[0] + 0.05, LUNGE_W[1], P['Porch Front', 0.4] + bob[0], 12.0)
    set_(3, LUNGE_W[0] + 0.5, LUNGE_W[0] + 2.0, A + 60, 7.0)
    set_(3, LUNGE_W[0] + 2.0, LUNGE_W[1], A + 170, 1.4)
    set_(3, LUNGE_W[1], LUNGE_W[1] + 0.5, P['Porch Front', 0.4] + 10, 18.0)
    set_(WOG, LUNGE_W[1] + 0.05, T_BREAK, P['Right', 0.5] + bob[0], 12.0)
    set_(3, LUNGE_W[1] + 0.5, T_WELL, A + 120, 6.0)

    # Wellgunde's lure; the insult
    set_(WELL, T_WELL - 1.0, T_INSULT, P['Porch Front', 0.35] - 30, 0.9)
    set_(3, T_WELL + 3.0, T_INSULT, P['Porch Left', 0.75] + 20, 1.1)
    set_(WELL, T_INSULT, D, P['Right', 0.85] + bob[1], 14.0)

    # Flosshilde's serenade: they meet in the middle of the porch and sway together
    sway = 25 * np.sin(2 * np.pi * t / 2.0)
    set_(FLO, T_FLO - 1.0, T_MERGE, P['Porch Front', 0.4] + 15, 1.0)
    set_(3, T_FLO + 1.0, T_MERGE, P['Porch Front', 0.4] - 15, 1.0)
    set_(FLO, T_MERGE, T_BREAK, P['Porch Front', 0.4] + 8 + sway, 4.0)
    set_(3, T_MERGE, T_BREAK, P['Porch Front', 0.4] - 8 + sway, 4.0)
    set_(FLO, T_BREAK, LUNGES[0], P['Left', 0.5] + bob[2], 14.0)
    set_(WOG, T_BREAK, LUNGES[1], P['Porch Front', 0.7] + bob[0], 6.0)
    set_(3, T_BREAK, LUNGES[0], P['Porch Front', 0.4], 4.0)

    # the rage: he streaks at one, she leaps away just before he arrives
    here = {WOG: P['Porch Front', 0.7], WELL: P['Right', 0.85], FLO: P['Left', 0.5]}
    for i, (tl, (who, dest)) in enumerate(zip(LUNGES, CHASE)):
        nxt = LUNGES[i + 1] if i + 1 < len(LUNGES) else T_SPENT
        set_(3, tl, nxt, here[who], 11.0)
        here[who] = at(G, *dest)
        set_(who, tl + 0.35, D, here[who] + bob[who], 13.0)
    set_(3, T_SPENT, T_SPENT + 2.0, tgt[3][int(T_SPENT / DT) - 1], 3.0)
    set_(3, T_SPENT + 2.0, D, P['Porch Left', 0.75], 0.8)
    set_(WELL, T_SPENT + 1.0, D, P['Left', 0.55] + bob[1], 1.2)
    set_(WOG, T_SPENT + 1.0, D, P['Porch Right', 0.7] + bob[0], 1.2)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(4)])
    return dict(t=t, pos=pos[:3], apos=pos[3])


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    C = choreography(G)
    N = compose()
    sung = [np.array([e[0] for e in N if e[4] == 'sing' and e[5] == k]) for k in range(3)]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    jolts = sorted([ta + 1.8 for ta in SLIPS] + [tl + 0.5 for tl in LUNGE_W] + [T_INSULT + 0.8] +
                   [tl + 0.45 for tl in LUNGES] + [FIST])
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    tw = Flicker(rng, G.N, 3.0, 8.0)

    def spray(n, t0, at_, vmin, vmax, cols):
        return dict(t0=t0, p=np.full(n, at_), v=rng.choice([-1, 1], n) * rng.uniform(vmin, vmax, n),
                    c=rng.integers(len(cols), size=n), cols=cols, w=rng.uniform(12, 24, n))
    sprays = []
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap = C['apos'][f]

        # the river, muddy round Alberich
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.16 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 140 + 0.33 * t) + 1)
        rage = smoothstep(T_RAGE - 0.5, T_RAGE + 0.5, t) * (1 - smoothstep(T_SPENT, T_SPENT + 3, t))
        murk = np.exp(-((d - ap) / (240 + 200 * rage)) ** 2)
        clean = (1 - 0.7 * murk) * (0.8 - 0.25 * rage)
        fr += light(DEEP, (0.2 + 0.1 * w1) * clean) + light(GREEN, (0.07 + 0.18 * w1 * w2) * clean)
        fr += light(MUD, 0.34 * murk * (1 + 0.15 * smoulder(t)))

        # mud from each slip; the sneeze, inflating him and spraying the porch with muck
        for ta in SLIPS:
            ts = ta + 1.8
            if ts <= t < ts + 1.0:
                r = 30 + 220 * (t - ts) ** 0.6
                fr += light(MUD, 0.9 * (1 - (t - ts)) * np.exp(-((np.abs(d - ap) - r) / 30) ** 2))
        if abs(t - CHOO) < DT / 2:
            sprays.append(spray(60, t, ap, 150, 900, [MUCK, MUD, HOT]))
        if abs(t - T_BREAK) < DT / 2:
            sprays.append(spray(120, t, ap, 150, 1500, COLOR))
        puff = sum(0.35 * smoothstep(a, a + 0.4, t) for a in AH) * (t < CHOO)
        if CHOO <= t < CHOO + 0.8:
            fr += light(MUCK, 0.6 * np.exp(-(t - CHOO) / 0.25) * np.exp(-((d - ap) / 400) ** 2))

        # Flosshilde's embrace: the porch glows rose and pulses, the wings a little too
        love = smoothstep(T_MERGE - 1.5, T_MERGE + 2.0, t) * (1 - smoothstep(T_BREAK - 0.1, T_BREAK + 0.15, t))
        if love > 0:
            beat = 0.75 + 0.25 * np.cos(2 * np.pi * (t - T_MERGE) / (4 * BEAT * 0.75))
            swell = 0.5 + 0.5 * smoothstep(T_MERGE + 3, T_BREAK, t)
            fr += light(ROSE, love * beat * swell * (0.85 * porch + 0.22 * ~porch) *
                        (0.7 + 0.3 * np.exp(-((d - ap) / 250) ** 2)))

        # the maidens
        for k in range(3):
            p = C['pos'][k][f]
            i = int(np.searchsorted(sung[k], t, side='right')) - 1
            flare = np.exp(-(t - sung[k][i]) / 0.2) if i >= 0 and t - sung[k][i] < 1.0 else 0.0
            b = 0.62 + 0.38 * flare
            trail = np.zeros(G.N)
            moving = abs(p - C['pos'][k][max(f - 8, 0)]) > 25
            if moving:
                for j, lag in enumerate((3, 6, 9, 12, 15)):
                    q = C['pos'][k][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 24) ** 2) * (1 - j / 5.5))
            body = np.exp(-((d - p) / (20 + 10 * flare)) ** 2)
            fr += light(COLOR[k], b * body + 0.3 * b * np.exp(-((d - p) / 90) ** 2) + 0.45 * trail)
            fr += light(WHITE, 0.4 * b * flare * body)
        for tl, (who, _) in zip(LUNGES + LUNGE_W, CHASE + [(WOG, None)] * 2):      # where she leapt from
            ts = tl + 0.35
            if ts <= t < ts + 0.8:
                p0 = np.interp(ts, C['t'], C['pos'][who])
                r = 30 + 260 * (t - ts) ** 0.6
                fr += light(COLOR[who], 0.8 * (1 - (t - ts) / 0.8) * np.exp(-((np.abs(d - p0) - r) / 30) ** 2))

        # Alberich: smouldering, jolting at every slip, thud and stamp; hot and trailing in his rage
        jolt = sum(np.exp(-(t - j) / 0.22) for j in jolts if j <= t < j + 1.5)
        width = 28 + 10 * jolt + 45 * puff + 20 * rage
        hue = ALB * (1 - 0.4 * love) + HOT * 0.4 * love
        fr += light(hue, (0.6 + 0.35 * jolt + 0.3 * puff + 0.2 * love) * np.exp(-((d - ap) / width) ** 2)
                    * (1 + 0.2 * smoulder(t)))
        if rage > 0:
            trail = np.zeros(G.N)
            for j, lag in enumerate(range(2, 22, 2)):
                q = C['apos'][max(f - lag, 0)]
                trail = np.maximum(trail, np.exp(-((d - q) / 30) ** 2) * (1 - j / 10.5))
            fr += light(HOT, 0.7 * rage * trail)
        for tl in LUNGES:                                   # the run he lands on flashes red
            tland = tl + 0.45
            if tland <= t < tland + 1.2:
                seg = G.seg_of[np.argmin(np.abs(d - np.interp(tland, C['t'], C['apos'])))]
                fr += light(ALB, 0.5 * np.exp(-(t - tland) / 0.35) * (G.seg_of == seg))

        # sprays of particles: muck from the sneeze, glitter from the laughter
        for s in sprays:
            age = t - s['t0']
            if age > 3.5:
                continue
            q = s['p'] + s['v'] * (1 - np.exp(-age / 0.7)) * 0.7
            fade = np.exp(-age / 1.4)
            for c, col in enumerate(s['cols']):
                sel = s['c'] == c
                if sel.any():
                    g = np.exp(-((d[:, None] - q[sel][None, :]) / s['w'][sel][None, :]) ** 2).max(axis=1)
                    fr += light(col, 1.0 * fade * g * (0.7 + 0.3 * tw(t)))

        # the first glimmer on the rock
        if t >= T_GLIMMER:
            g = smoothstep(T_GLIMMER, D, t)
            fr += light(GOLD, 0.8 * g * (0.75 + 0.25 * np.sin(2 * np.pi * 0.7 * t)) * np.exp(-((d - pf) / 40) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes on the orchestra, the maidens' lines on woodwinds, and the stage: mud and splashes as he slips,
    the sneeze, the thuds of his lunges and the splash of each maiden leaping clear."""
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
    o = Orchestra(M, level=3.0)
    splash = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')

    def role(t, d, m, v, h):
        if t < SEG[1]:                                                  # his slithering: bassoons, clarinets, strings
            if h == 0:
                return [('clarinets', 0, 0, 0.5), ('violas', 0, -4, 0.45)]
            return [('bassoons', 0, 6, 0.6), ('cellos', 0, 0, 0.5), ('basses', -12 if m >= 40 else 0, -6, 0.35)]
        if t < SEG[3] and t < T_RAGE:                                   # the mockery: light strings and winds
            if h == 0:
                return [('violins', 0, 0, 0.55), ('flutes', 0, -10, 0.3 * (m >= 72))]
            return [('cellos', 0, 0, 0.55), ('bassoons', 0, -6, 0.35)]
        if h == 0:                                                      # his rage: the full orchestra
            return [('violins', 0, 8, 0.8), ('flutes', 0, -2, 0.45 * (m >= 77)), ('oboes', 0, -6, 0.3 * (m >= 70))]
        if d >= 0.3:
            return [('horns', 0, 8, 0.9), ('trombones', 0, 4, 0.6), ('tuba', 0, 0, 0.5 * (m < 50))]
        return [('cellos' if m < 55 else 'violas', 0, 8, 0.8), ('bassoons', 0, 0, 0.4),
                ('basses', -12 if m >= 40 else 0, 0, 0.5 * (m < 50))]

    o.tutti(tidy(EX['notes']), size=lambda t: 1.0 if t >= SEG[3] else 0.7, role=role,
            pan=lambda t, m: alb(t) * 0.6)
    inst = {WOG: [('oboes', 0.85), ('flutes', 0.3)], WELL: [('flutes', 0.9), ('clarinets', 0.25)],
            FLO: [('clarinets', 0.95), ('violas', 0.3)]}
    for t, d, m, v, part, who in compose():
        if part == 'sing':
            for name, g in inst[who]:
                o.play(name, m, t, max(d, 0.12), v, where(who, t), g)
    # the stage
    for ta in SLIPS:                                                    # he hauls himself up and slides back down
        for k in range(3):
            o.hit('hoof soft', ta + 0.6 * k, 70, gain=0.3, pan=alb(ta))
        o.hit('scrape', ta + 1.8, 100, gain=0.45, pan=alb(ta + 1.8))
        M.add('fx', splash.play(110), ta + 2.1, 0.6, alb(ta + 2.1))
    M.add('fx', whoosh(0.35, 5000, 1200, 0.9, seed=11), CHOO, 0.9, alb(CHOO))      # the sneeze
    o.hit('bass drum', CHOO + 0.05, 110, gain=0.5, pan=alb(CHOO))
    for tl in LUNGE_W + LUNGES:                                         # each lunge lands with a thud, she splashes away
        o.hit('bass drum', tl + 0.45, 116, gain=0.55, pan=alb(tl + 0.45))
        M.add('fx', splash.play(105), tl + 0.3, 0.5, alb(tl + 0.3))
    for k in range(3):                                                  # the rose shatters: they scatter
        M.add('fx', splash.play(115), T_BREAK + 0.15 * k, 0.6, where(k, T_BREAK + 0.3))
    o.hit('crash', T_BREAK, 100, gain=0.35)
    o.hit('bass drum', FIST, 120, gain=0.6, pan=alb(FIST))
    o.hit('timpani', FIST, 116, pitch=-5, gain=0.5, pan=alb(FIST))
    o.effects([(0.0, -3), (AH[0] - 0.5, -6), (CHOO - 0.2, 0), (CHOO + 1.5, -6), (T_INSULT - 0.4, -14),
               (SEG[2] - 0.2, -14), (T_BREAK - 0.2, -2), (T_BREAK + 1.2, -12), (T_RAGE, -8), (SEG[3], -2),
               (T_SPENT + 2, -8), (FIST - 0.3, -2), (D, -8)])
