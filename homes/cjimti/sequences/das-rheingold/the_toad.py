"""The Toad: down in Nibelheim, among the red-orange glow of the forges, Loge flickers round Alberich and
needles him, darting in on every line he sings: a serpent is all very well, but could he make himself small?
That would be too hard, surely. "Zu schwer dir, weil du zu dumm!", Alberich snaps, and "Pah! Nichts leichter!".
The Tarnhelm's chords sound, a violet-grey shimmer closes round him, "Krumm und grau krieche Kröte!", his red
drains into a hole of darkness in the cavern's glow, until, plip, a tiny dull-green light sits where he stood.

The toad hops about the middle of Porch Front, over and around the glowing hoard, a hop on every note of the
orchestra's little figures and a croak on its accents, while Wotan creeps in from Porch Left a step at a time.
"Dort, die Kröte! Greife sie rasch!": the bass runs up, and Wotan's foot comes down, a blue slam and a blue
shockwave over the whole house. Loge darts in and snatches the helmet (a violet streak to his hand, where it
stays), and Alberich pops back to his own shape, caught, "Ohe! Verflucht! Ich bin gefangen!": the house flashes
red, and he struggles in a red jolt through the porch on every chord. "Halt' ihn fest, bis ich ihn band": Loge
whirls round him as steel-blue bindings wind in tighter and tighter to the strings' rising chromatic rope, the
knot is tied, and to Loge's "Nun schnell hinauf: dort ist er unser!" they start to haul him off.

The music is Wagner's own: Scene 3, bars 2691 to 2743, as Solti's 1958 Vienna Philharmonic recording takes them.
The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): Loge's quick figures on
violins and flutes, the Tarnhelm's chords on muted horns over cellos, the toad's figures on clarinet and bassoon,
the bass's run on cellos and basses, the struggle's flourishes on violins and piccolo over trombones, the rope on
violins and cellos, the haul on cellos, basses and horns. On top, as a staged production would, and kept down
under the dialogue: a glassy plip as the toad appears, a soft tap on its landings and a guiro croak, the slam as a
great blow, a whoosh as the helmet is snatched, a crash as he is caught, a thud on each struggle and the rope
creaking as it winds.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG17'
TITLE = 'The Toad'
KIND = 'show'
DESCRIPTION = ('Loge dares Alberich to make himself small, and the helmet turns him into a tiny hopping toad. '
               'Wotan puts his foot on it, Loge grabs the helmet, and Alberich is caught and tied up tight. '
               'Then they drag him up out of the dark.')
VOICEOVER = ('A giant serpent is very impressive. But could you make yourself small? '
             'Alberich, never one to turn down a chance to show off, falls right into it.')

EX = excerpt(__file__)                      # Scene 3, bars 2691-2743, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
TAUNT = [6.506, 9.14, 11.025, 12.97, 17.626, 25.506, 28.033]  # Loge's lines: could you make yourself small?
T_BOAST = 20.369                            # "Zu schwer dir, weil du zu dumm!"
T_PAH = 30.441                              # "Pah! Nichts leichter!"
BOASTS = [20.369, 23.19, 30.441, 40.46]       # Alberich's lines: a red flare out from him
T_HELM = 32.84                              # the Tarnhelm's chords
T_SPELL = BAR[2720]                         # "Krumm und grau krieche Kröte!"
T_TOAD = BAR[2723]                          # plip
HOPS = [(51.94, 0.56), (53.78, 0.61), (55.54, 0.55), (56.67, 0.48), (57.78, 0.43), (58.86, 0.5), (60.68, 0.57),
        (62.36, 0.62), (63.36, 0.55), (64.41, 0.48), (65.99, 0.53), (66.49, 0.58), (67.43, 0.52), (67.87, 0.47)]
HOP = 0.32                                  # seconds in the air
CROAKS = [53.78, 60.68]                     # the accents
T_CREEP = 55.0                              # Wotan tiptoes in
T_SLAM = 70.66                              # his foot comes down, at the top of the bass's run
T_SNATCH = 70.95                            # Loge takes the helmet
T_POP = 71.3                                # Alberich back in his own shape, caught
T_BOUND = 78.015                            # the last knot
JOLTS = [71.98, 73.22, 74.435, 78.226, 79.473, 80.653]
T_SPEAR = 1e9                               # (no spear here: its music is in the climb)
SB = 0.55
T_HAUL = 79.86                              # "Nun schnell hinauf!"
T_ASCENT = 1e9                              # the climb is the next scene
NB = 0.45
T_ANVILS = 1e9
D = EX['seconds']

CAVE = hexc('#b01c00')
EMBER = hexc('#ff5a10')
FORGE = hexc('#ff7a10')
ALB = hexc('#ff1000')
MUD = hexc('#5a1200')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
LOGE1 = hexc('#ff5000')
LOGE2 = hexc('#ffb020')
TARN = hexc('#5a4a8a')
TARN_HI = hexc('#9a88d0')
TOAD = hexc('#6a8a10')
STEEL = hexc('#5a88d0')
WHITE = hexc('#ffffff')

NANVIL = 18


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Loge's needling ('talk'), the
    Tarnhelm's chords ('tarnhelm'), the toad's figures ('toad'), the bass's run up to the slam ('run'), the struggle
    ('caught'), the rope ('rope') and the haul ('haul')."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_HELM - 0.01:
            part = 'talk'
        elif t < T_TOAD - 0.01:
            part = 'tarnhelm'
        elif t < BAR[2734] - 1.3:
            part = 'toad'
        elif t < T_SLAM - 0.01:
            part = 'run'
        elif t < BAR[2739]:
            part = 'caught' if t < 75.58 else 'rope'
        else:
            part = 'haul'
        N.append((t, d, m, v, part, None))
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def toad_track(G, t):
    """The toad's path distance at times t: still between hops, a quick eased hop to each landing."""
    p = np.full_like(t, at(G, 'Porch Front', 0.5))
    prev = at(G, 'Porch Front', 0.5)
    for th, u in HOPS:
        q = at(G, 'Porch Front', u)
        m = t >= th
        p[m] = prev + (q - prev) * smoothstep(th, th + HOP, t[m])
        prev = q
    return p


def choreography(G):
    """Per frame: Alberich (or the toad), Wotan, Loge (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = np.zeros((3, F))
    rate = np.full((3, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    ALB_, WOT, LOG = 0, 1, 2
    toad = toad_track(G, t)
    pT = at(G, 'Porch Front', HOPS[-1][1])
    set_(ALB_, 0, D, at(G, 'Porch Front', 0.5), 4.0)
    set_(ALB_, T_POP, T_HAUL, pT + 6 * np.sin(2 * np.pi * t / 2.3), 6.0)
    set_(ALB_, T_HAUL, D, at(G, 'Porch Front', 0.2), 0.9)
    wob = 6 * np.sin(2 * np.pi * t / 3.1)
    set_(WOT, 0, D, at(G, 'Porch Left', 0.7) + wob, 2.0)
    for k, s in enumerate(np.arange(T_CREEP, T_SLAM - 0.6, 0.75)):   # tiptoe steps
        u = (k + 1) / len(np.arange(T_CREEP, T_SLAM - 0.6, 0.75))
        set_(WOT, s, D, at(G, 'Porch Left', 0.7) + (at(G, 'Porch Front', 0.3) - at(G, 'Porch Left', 0.7)) * u, 7.0)
    set_(WOT, T_SLAM - 0.2, T_POP, pT, 18.0)
    set_(WOT, T_POP, T_HAUL, pT + 45, 5.0)
    set_(WOT, T_HAUL, D, at(G, 'Porch Front', 0.4) + wob, 0.9)
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    set_(LOG, 0, D, at(G, 'Porch Front', 0.25) + jit, 4.0)
    for t0 in TAUNT:                                        # darting round Alberich as he needles him
        set_(LOG, t0, t0 + 1.8, at(G, 'Porch Front', 0.5) - 40 + 30 * np.sin(2 * np.pi * (t - t0) / 0.9), 9.0)
    set_(LOG, T_SNATCH - 0.3, T_SNATCH + 0.2, pT - 12, 18.0)
    set_(LOG, T_SNATCH + 0.2, T_POP + 0.4, at(G, 'Porch Front', 0.3) + jit, 14.0)
    set_(LOG, T_POP + 0.4, T_BOUND, pT + 70 * np.sin(2 * np.pi * (t - T_POP) / 0.9), 18.0)   # winding the rope
    set_(LOG, T_BOUND, T_HAUL, pT - 60 + jit, 6.0)
    set_(LOG, T_HAUL, D, at(G, 'Porch Front', 0.75) + jit, 0.9)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(3)])
    m = (t >= T_TOAD) & (t < T_POP)
    pos[0][m] = toad[m]                                     # the toad hops exactly
    m = (t >= T_POP) & (t < T_POP + 1.0)
    pos[0][m] = pT
    return dict(t=t, alb=pos[0], wot=pos[1], loge=pos[2])


def anvil_spots(G):
    """Where the eighteen anvils ring: spread over every run of the house."""
    L = G.length
    return np.linspace(0.04 * L, 0.97 * L, NANVIL)[np.random.default_rng(5).permutation(NANVIL)]


def render(G, seed=17):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    ph = at(G, 'Porch Front', 0.65)
    C = choreography(G)
    N = compose()
    hops = np.array([th for th, _ in HOPS])
    jolts = np.array(JOLTS)
    spear = [e[0] for e in N if e[4] == 'spear']
    chords = np.array(sorted({e[0] for e in N if e[4] == 'tarnhelm' and e[2] >= note('E3')}))
    quick = np.array([e[0] for e in N if e[4] == 'talk' and e[5] is None and e[1] < 0.3])
    nibs = np.array([e[0] for e in N if e[4] == 'nib' and e[5] is None])
    anvils = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    spots = anvil_spots(G)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    spark = np.zeros(G.N)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]

        # the cavern: a red-orange glow that breathes, forge sparks; in the ascent stripes run down and away
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 320 - 0.07 * t))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 130 + 0.21 * t) + 1)
        asc = smoothstep(T_ASCENT - 1, T_ASCENT + 6, t)
        helm = smoothstep(T_HELM + 1.5, T_TOAD - 0.5, t) * (1 - smoothstep(T_TOAD, T_TOAD + 0.4, t))
        hole = helm * np.exp(-((d - ap) / 60) ** 2)
        bed = (0.27 + 0.1 * w1) * (1 - 0.9 * hole)
        fr += light(CAVE, bed) + light(EMBER, (0.05 + 0.14 * w1 * w2) * (1 - hole))
        if asc > 0:
            ni = int(np.searchsorted(nibs, t, side='right')) - 1
            beatp = np.exp(-(t - nibs[ni]) / 0.12) if ni >= 0 else 0.0
            stripe = (0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - pf) / 170 - 0.9 * (t - T_ASCENT)))) ** 3
            fr += light(FORGE, asc * (0.28 + 0.12 * beatp) * stripe)
        spark *= np.exp(-DT / 0.12)
        spark[rng.random(G.N) < 0.004 + 0.01 * asc] = 1.0
        fr += light(FORGE, 0.75 * spark)
        for ta, a, v in anvils:                             # the anvils, each a white-hot burst where it rings
            if ta <= t < ta + 0.5:
                fr += light(HOT, (v / 110) * np.exp(-(t - ta) / 0.09) * blob(spots[a], 16))
                fr += light(FORGE, 0.7 * (v / 110) * np.exp(-(t - ta) / 0.25) * blob(spots[a], 45))

        # the Tarnhelm: a violet wave rolls out from him over the whole house on every chord, the cave darkening
        if T_HELM <= t < T_TOAD + 1.0:
            dim = smoothstep(T_HELM, T_SPELL, t) * (1 - smoothstep(T_TOAD, T_TOAD + 1.0, t))
            fr *= 1 - 0.55 * dim
            for tc in chords[(chords <= t) & (chords > t - 3.0)]:
                a = t - tc
                rr = 420 * a ** 0.8
                fr += light(TARN_HI,
                            0.9 * np.exp(-a / 1.4) * np.exp(-((np.abs(d - ap) - rr) / 150) ** 2))
                fr += light(TARN, 0.45 * np.exp(-a / 0.6) * blob(ap, 160))
        # Alberich's boasts: a red flare rippling out from him
        for tb in BOASTS:
            if tb <= t < tb + 1.6:
                a = t - tb
                rr = 380 * a ** 0.7
                fr += light(ALB, 0.9 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - ap) - rr) / 90) ** 2))
                fr += light(HOT, 0.5 * np.exp(-a / 0.15) * blob(ap, 30))
        # Loge's quick figures: sparks thrown off his flame
        qi = int(np.searchsorted(quick, t, side='right')) - 1
        if qi >= 0 and t - quick[qi] < 0.25:
            a = t - quick[qi]
            sp_at = lp + (-1) ** qi * (30 + 260 * a)
            fr += light(LOGE2, 1.0 * np.exp(-a / 0.15) * blob(sp_at, 16))
            fr += light(LOGE1, 0.5 * np.exp(-a / 0.15) * blob(lp, 60))

        # the hoard beside him
        fr += light(GOLD, 0.62 * blob(ph, 30) + 0.2 * blob(ph, 80))
        fr += light(HOT, 0.45 * blob(ph, 14) * (0.6 + 0.4 * tw(t)) * (tw(t) > 0.3))

        # Loge: a restless flicker, brighter as he needles; the helmet's violet in his hand once he has it
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        tease = sum(smoothstep(t0, t0 + 0.2, t) * (1 - smoothstep(t0 + 1.6, t0 + 2.0, t)) for t0 in TAUNT)
        lb = blob(lp, 22 + 6 * tease)
        fr += light(LOGE1, (0.7 + 0.2 * tease) * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, (0.55 + 0.35 * tease) * lb * fk)
        held = smoothstep(T_SNATCH + 0.15, T_SNATCH + 0.4, t)
        if held > 0:
            fr += light(TARN, 0.6 * held * blob(lp, 34) * (0.7 + 0.3 * tw(t)))
        if T_POP + 0.4 <= t < T_BOUND:                      # his flame trailing as he winds the rope
            for j, lag in enumerate(range(2, 14, 2)):
                q = C['loge'][max(f - lag, 0)]
                fr += light(LOGE2, 0.45 * (1 - j / 6.5) * blob(q, 18))

        # Wotan: deep blue, a step at a time
        fr += light(WOTAN, 0.85 * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(SPEAR, 0.25 * blob(wp, 7))

        # Alberich: red with the ring's gold point and red glint; the helmet, the toad, the capture
        alb = 1 - smoothstep(T_HELM + 1.0, T_TOAD - 1.0, t)
        back = smoothstep(T_POP, T_POP + 0.1, t)
        vis = max(alb, back)
        if vis > 0:
            fr += light(MUD, 0.32 * vis * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
            fr += light(ALB, 0.75 * vis * blob(ap, 24) * (1 + 0.2 * smoulder(t)))
            fr += light(GOLD, 0.9 * vis * blob(ap, 6)) + light(RED, 0.7 * vis * blob(ap + 9, 6) * (0.6 + 0.4 * tw(t)))
        if T_HELM <= t < T_TOAD + 0.4:                      # the shimmer closing in round him
            r = 80 - 30 * smoothstep(T_HELM, T_TOAD, t)
            edge = np.exp(-((np.abs(d - ap) - r) / 14) ** 2)
            fr += light(TARN, 0.85 * smoothstep(T_HELM, T_HELM + 1.5, t) * (1 - smoothstep(T_TOAD, T_TOAD + 0.4, t))
                        * edge * (0.6 + 0.4 * tw(t)))
        if T_TOAD <= t < T_POP:                             # the toad
            i = int(np.searchsorted(hops, t, side='right')) - 1
            air = (i >= 0) and (t - hops[i] < HOP)
            land = np.exp(-(t - hops[i] - HOP) / 0.15) if i >= 0 and t >= hops[i] + HOP else 0.0
            pinned = smoothstep(T_SLAM, T_SLAM + 0.05, t)
            b = (0.8 + 0.25 * air + 0.3 * land) * (1 - 0.5 * pinned * (tw(t)[0] > 0))
            if t < T_TOAD + 0.3:
                fr += light(WHITE, 0.8 * np.exp(-(t - T_TOAD) / 0.1) * blob(ap, 14))
            fr += light(TOAD, b * blob(ap, 9 + 5 * air) + 0.25 * blob(ap, 30))
            fr += light(TARN, 0.35 * (1 - smoothstep(T_SNATCH, T_SNATCH + 0.2, t)) * blob(ap, 26))
            if air:
                q = C['alb'][max(f - 4, 0)]
                fr += light(TOAD, 0.5 * blob(q, 12))
            if land > 0.05:
                rr = 12 + 40 * (1 - land)
                fr += light(TOAD, 0.6 * land * np.exp(-((np.abs(d - ap) - rr) / 8) ** 2))
            for tc in CROAKS:
                if tc <= t < tc + 0.5:
                    fr += light(TOAD, 0.5 * np.exp(-(t - tc) / 0.15) * blob(ap, 40))

        # the slam: blue on the toad, a shockwave out over the whole house
        if T_SLAM <= t < T_SLAM + 2.0:
            a = t - T_SLAM
            fr += light(WOTAN, 0.9 * np.exp(-a / 0.4) * np.ones(G.N))
            fr += light(WHITE, 0.8 * np.exp(-a / 0.08) * blob(wp, 40))
            rr = 1400 * a ** 0.7
            fr += light(SPEAR, 0.7 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - wp) - rr) / 60) ** 2))
        if T_SNATCH - 0.2 <= t < T_SNATCH + 0.6:            # the helmet snatched: a violet streak
            a = t - (T_SNATCH - 0.2)
            for j, lag in enumerate(range(0, 12, 2)):
                q = C['loge'][max(f - lag, 0)]
                fr += light(TARN, 1.0 * (1 - j / 6.5) * (1 - a / 0.8) * blob(q, 16))

        # caught: a red burst, the bindings wound in, the struggle
        if T_POP <= t < T_POP + 2.0:
            a = t - T_POP
            fr += light(ALB, 0.9 * np.exp(-a / 0.35) * np.ones(G.N))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.1) * blob(ap, 50))
            rr = 1500 * a ** 0.6
            fr += light(RED, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - ap) - rr) / 70) ** 2))
        if t >= T_POP + 0.4:
            u = smoothstep(T_POP + 0.4, T_BOUND, t)
            if t < T_BOUND + 0.5:                           # the rope winds in round him
                R = 260 * (1 - u) + 30
                th = 2 * np.pi * (np.arange(6) / 6 + 1.1 * (t - T_POP))
                q, depth = ap + R * np.cos(th), np.sin(th)
                g = np.exp(-((d[:, None] - q[None, :]) / 14) ** 2) * (0.5 + 0.5 * depth)[None, :]
                fr += light(STEEL, 0.9 * (1 - smoothstep(T_BOUND, T_BOUND + 0.5, t)) * g.max(axis=1))
            j = int(np.searchsorted(jolts, t, side='right')) - 1
            jolt = np.exp(-(t - jolts[j]) / 0.25) if j >= 0 and t - jolts[j] < 1.5 else 0.0
            wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
            fr += light(STEEL, (0.3 + 0.55 * u + 0.4 * jolt) * wrap)
            fr += light(ALB, 0.5 * jolt * blob(ap, 60))
            if jolt > 0.05:
                porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
                fr += light(ALB, 0.4 * jolt * porch)
            if T_BOUND <= t < T_BOUND + 0.8:
                fr += light(STEEL, 0.7 * np.exp(-(t - T_BOUND) / 0.2) * blob(ap, 70))

        # the spear: a steel line steps out from Wotan across the porch with each note
        for i, ts in enumerate(spear):
            if ts <= t < T_SPEAR + 12 * SB + 1.5:
                reach = 30 * (i + 1)
                fade = np.exp(-(t - ts) / 0.4)
                line = smoothstep(reach + 10, reach - 10, np.abs(d - wp)) * (np.abs(d - wp) > reach - 30)
                fr += light(SPEAR, (0.25 + 0.6 * fade) * line * (1 - smoothstep(T_SPEAR + 10 * SB, T_SPEAR + 12 * SB + 1.5, t)))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the scene's sounds on top."""
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

    o = Orchestra(M, level=3.0)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    guiro = M.hits('Percussion/Guiro-Hit*.wav')

    def role(t, d, m, v, h):
        part = next(e[4] for e in N if e[0] == t)
        if part == 'talk':                                  # Loge's needling: strings and flutes, quick and light
            if h == 0:
                return [('violins', 0, -2, 0.55)] + ([('flutes', 0, -10, 0.4)] if m >= note('C5') else [])
            return [('cellos', 0, -4, 0.55), ('bassoons', 0, -10, 0.35)]
        if part == 'tarnhelm':                              # muted horns over cellos
            if m >= note('E3'):
                if d > 1.2:
                    o.hold('brass', mute, m, t, t + d, v + 14, pan_of('alb', t), gain=0.7)
                else:
                    M.add('brass', mute.play(m, v + 14, dur=d, release=0.5), t, 0.7, pan_of('alb', t))
                return []
            return [('cellos', 0, 10, 0.55), ('basses', -12, 0, 0.4)]
        if part == 'toad':                                  # its figures: clarinet and bassoon, close to it
            if h == 0:
                return [('clarinets', 0, 14, 0.6)] + ([('piccolo', 12, 0, 0.3)] if d < 0.2 else [])
            return [('bassoons', 0, 20, 0.6), ('cellos', 0, 0, 0.35)]
        if part == 'caught':                                # his struggle: violins and piccolo over trombones
            if h == 0:
                return [('violins', 0, 4, 0.55), ('piccolo', 0, -12, 0.3)] if m >= note('C5') else \
                    [('violins', 0, 4, 0.55)]
            return [('trombones', 0, 30, 0.6), ('tuba', -12, 20, 0.45), ('cellos', 0, 20, 0.5)]
        if part == 'rope':
            return [('violins', 0, 10, 0.5)] if h == 0 else [('cellos', 0, 20, 0.55), ('violas', 12, 10, 0.3)]
        if part == 'haul':
            if h == 0:
                return [('horns', -12, 0, 0.6), ('violins', 0, -6, 0.4)]
            return [('cellos', 0, 20, 0.6), ('basses', 0, 14, 0.5), ('tuba', 0, 6, 0.4)]
        return None                                         # the run up: the orchestra's default

    N = compose()
    o.tutti(EX['notes'], role=role, pan=lambda t, m: pan_of('alb', t) * 0.6)
    # the stage, ridden: down under Loge's needling and the spell, up for the toad, the slam and the capture
    o.effects([(0, -10), (T_TOAD - 0.5, -3), (T_SLAM - 0.4, 0), (T_BOUND, -3), (T_HAUL, -5)])
    pt = pan_of('alb', T_TOAD)
    o.play('glock', note('Bb6') - 24, T_TOAD, 0.2, 96, pt, 0.5)     # plip
    o.hit('triangle', T_TOAD, 90, gain=0.35, pan=pt)
    for th, u in HOPS:                                      # a soft tap as it lands
        o.hoof(th + HOP, pan_of('alb', th + HOP), 60, 0.5)
    for tc in CROAKS:                                       # croak
        p = pan_of('alb', tc)
        M.add('perc', guiro.play(100), tc + 0.1, 0.6, p)
        M.add('perc', guiro.play(92), tc + 0.3, 0.5, p)
    ps = pan_of('wot', T_SLAM)
    o.boom(T_SLAM, ps, 1.0)                                 # his foot comes down
    o.hit('crash', T_SLAM, 118, gain=0.5, pan=ps)
    M.add('fx', whoosh(0.5, 3000, 9000, 0.5, seed=7), T_SNATCH - 0.2, 0.7, pan_of('loge', T_SNATCH))
    pp = pan_of('alb', T_POP)
    o.hit('crash', T_POP, 112, gain=0.45, pan=pp)           # caught
    o.hit('timpani', T_POP, 116, pitch=-3, gain=0.6, pan=pp)
    for tj in JOLTS:                                        # each struggle against the bindings
        p = pan_of('alb', tj)
        o.hit('bass drum', tj, 100, gain=0.4, pan=p)
        o.hit('metal', tj + 0.02, 70, gain=0.2, pan=p)
    for k in range(5):                                      # the rope creaking as it winds
        o.hit('scrape', 75.6 + k * 0.5, 80 + 6 * k, gain=0.2, pan=pan_of('loge', 75.6 + k * 0.5))
    o.hit('bass drum', T_BOUND, 112, gain=0.55, pan=pan_of('alb', T_BOUND))      # the knot
