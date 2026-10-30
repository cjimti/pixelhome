"""Up from the Depths: the third interlude, the climb out of Nibelheim with Alberich bound between Wotan and
Loge. The orchestra's lines rush up and pour down while stripes of forge glow run down and away from the porch;
then the Nibelung rhythm hammers out over a pedal deep in the basses, and the anvils join in one by one, each
ringing at its own place on the house in a white-hot burst, until at the top of the climb the Ring motif comes
down in great chords over all eighteen anvils at once, the whole house flaring with each.

Then the caverns fall away beneath them: the music's chromatic waves rise and fall, the red-orange glow drains
outward from the porch to both ends of the house and off the free ends, the hoard left behind in the dark fades,
and in a grey mist, over the strings' tremolo, Alberich's red pulses in its bindings, a red ripple out through
the mist with each surge. Grey dawn on the mountaintop: the wings fill with a dim dawn, every colour faded toward
grey because the gods have grown old while Freia is away, and with the broad chords of the arrival Valhalla rises
dim across the porch, its battlements a row of pale masonry blocks, each chord a breath of light. Wotan's blue has
greyed with it; only Loge's fire is undimmed, the helmet's violet in his hand.

The music is Wagner's own: the interlude from Scene 3 to Scene 4, bars 2744 to 2759, 2770 to 2789 and 2836 to
2856, as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the rushing lines on violins, violas and flutes over horns, the Nibelung
rhythm on violas and cellos over the basses' pedal and the contrabass tuba, the Ring motif's chords on trombones,
horns and trumpets, the chromatic waves on strings and woodwinds, the tremolo on the strings', and the arrival's
chords on horns, trombones and tubas with violins above. The eighteen anvils are Wagner's own, written into the
score; here they ring on the Nibelung rhythm where the reduction leaves them out. On top, as a staged production
would, kept for the moments that need it: a deep rumble as the caverns fall away and a cold mountain wind at dawn.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'RG18'
TITLE = 'Up from the Depths'
KIND = 'show'
DESCRIPTION = ('The long climb out of the caverns, with Alberich tied up and dragged along. Eighteen anvils '
               'hammer as the glow of the forges falls away beneath them, and they come out into a grey dawn '
               'where even the gods look old.')
VOICEOVER = ('Up through the rock, past every forge and every anvil, dragging the dwarf behind them. '
             'And at the top, a cold grey morning.')

EX = excerpt(__file__)                      # bars 2744-2759, 2770-2789, 2836-2856, Solti 1958
BAR = {int(m): t for m, t in EX['bars'] if m not in (2760, 2790)}
NB = 0.45
T_RHYTHM = BAR[2770]                        # the Nibelung rhythm: the anvils start joining in
T_PEAK = BAR[2783]                          # the Ring motif's chords over all eighteen anvils
T_DRAIN = BAR[2836]                         # the caverns fall away
T_WOE = BAR[2843]                           # Alberich's red pulses through the mist
T_QUIET = BAR[2847]                         # the rhythm long gone, the tremolo over
RINGS = []                                  # (the Ring's stirring is not in these bars)
T_REN = 1e9
T_DAWN = BAR[2848]                          # grey dawn
T_VAL = [BAR[2849], BAR[2851], BAR[2853], BAR[2855]]   # the arrival's chords: Valhalla, faded
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
STEEL = hexc('#5a88d0')
MIST = hexc('#3c3c78')
SHADOW = hexc('#1c1880')
DAWN1 = hexc('#2a3a6a')
DAWN2 = hexc('#6a5a8a')
VAL = hexc('#fff0c0')

NANVIL = 18


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def grey(c, k):
    """Colour c faded k of the way to grey (the gods growing old)."""
    return c * (1 - k) + (c @ np.array([0.3, 0.59, 0.11])) * k


def anvils_at(t):
    """How many of the eighteen anvils are ringing at time t."""
    return int(round(2 + 16 * smoothstep(T_RHYTHM, T_PEAK, t))) if T_RHYTHM <= t < T_DRAIN else 0


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The rushing start ('rise'), the
    Nibelung rhythm ('nib', its pedal 'nibbass'), the Ring's chords at the peak ('ringbrass'), the waves as the caverns
    fall away ('waves'), the tremolo ('trem') and the arrival ('valhalla'); 'anvil' (who = which anvil, velocity its
    force) and 'woe' are for the lights and the anvils' sound."""
    rng = np.random.default_rng(18)
    N = []
    order = rng.permutation(NANVIL)
    seen = set()
    for t, d, m, v, h in EX['notes']:
        if t < T_RHYTHM - 0.01:
            part = 'rise'
        elif t < T_DRAIN - 0.01:
            part = ('nib' if t < T_PEAK - 0.01 else 'ringbrass') if h == 0 else 'nibbass'
        elif t < T_WOE + 2.5:
            part = 'waves'
        elif t < T_QUIET - 0.01:
            part = 'trem'
        elif t < T_VAL[0] - 0.01:
            part = 'waves'
        else:
            part = 'valhalla'
        N.append((t, d, m, v, part, None))
        if T_RHYTHM <= t < T_DRAIN and h == 0 and round(t, 2) not in seen:   # the anvils, on the rhythm
            seen.add(round(t, 2))
            n = anvils_at(t) if t < T_PEAK else NANVIL
            for a in order[:n]:
                N.append((t, 0.1, 0, int(min(124, 92 + 22 * (t >= T_PEAK) + rng.integers(-8, 6))), 'anvil', int(a)))
            order = np.roll(order, 3)
    for t in (BAR[2843], BAR[2844], BAR[2845], BAR[2846]):
        N.append((t, 0.5, 0, 0, 'woe', None))
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
    """Per frame: bound Alberich, Wotan, Loge (path distance). The three hold their places as they climb."""
    F = nframes(D)
    t = np.arange(F) * DT
    climb = 1 - smoothstep(T_DRAIN, T_QUIET, t)
    jog = 5 * np.sin(2 * np.pi * t / (6 * NB)) * climb      # jolted along by the climb
    jit = 9 * np.sin(2 * np.pi * t / 0.7) + 6 * np.sin(2 * np.pi * t / 0.37)
    return dict(t=t, alb=at(G, 'Porch Front', 0.2) + jog + 3 * np.sin(2 * np.pi * t / 2.3),
                wot=at(G, 'Porch Front', 0.4) + jog + 6 * np.sin(2 * np.pi * t / 3.1),
                loge=at(G, 'Porch Front', 0.75) + jit)


def anvil_spots(G):
    L = G.length
    return np.linspace(0.04 * L, 0.97 * L, NANVIL)[np.random.default_rng(5).permutation(NANVIL)]


def render(G, seed=18):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    ph = at(G, 'Porch Front', 0.65)
    C = choreography(G)
    N = compose()
    nibs = np.array(sorted({e[0] for e in N if e[4] in ('rise', 'nib', 'ringbrass') and e[1] < 0.6}))
    anvils = [(e[0], e[5], e[3]) for e in N if e[4] == 'anvil']
    woes = np.array([e[0] for e in N if e[4] == 'woe'])
    rings = np.array([e[0] for e in N if e[4] == 'ringwinds'])
    brass = np.array(sorted({e[0] for e in N if e[4] == 'ringbrass' and e[1] >= 0.15}))
    vals = np.array(sorted({e[0] for e in N if e[4] == 'valhalla'}))
    spots = anvil_spots(G)
    tw = Flicker(rng, G.N, 2.0, 7.0)
    fl = Flicker(rng, G.N, 3.0, 11.0)
    smoulder = Flicker(rng, G.N, 0.6, 2.4)
    drift = Flicker(rng, G.N, 0.08, 0.3)
    spark = np.zeros(G.N)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    wings = ~porch
    po = np.zeros(G.N)
    po[porch] = d[porch] - d[porch].min()
    merlon = np.where((po // 24) % 2 == 0, 1.0, 0.3) * porch
    edge = np.abs(d - pf)
    huey = np.clip(1 - np.minimum(d, L - d) / (0.45 * L), 0, 1)       # dawn: violet toward the porch

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        ap, wp, lp = C['alb'][f], C['wot'][f], C['loge'][f]
        old = smoothstep(T_DAWN, T_DAWN + 8, t)
        beat = last(nibs, t, 0.12, 0.5) * (1 - smoothstep(T_DRAIN, T_QUIET, t))

        # the caverns: red-orange, stripes running down and away on the beat, draining out from the porch
        front = (L * 0.62) * smoothstep(T_DRAIN, T_QUIET + 1, t) ** 1.3
        keep = smoothstep(front - 60, front + 160, edge) * (1 - smoothstep(T_QUIET - 1, T_QUIET + 2, t))
        tt = t + 80.0                                       # the cavern's breathing carries on from The Toad
        w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 320 - 0.07 * tt))
        w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 130 + 0.21 * tt) + 1)
        fr += light(CAVE, (0.27 + 0.1 * w1) * keep) + light(EMBER, (0.05 + 0.14 * w1 * w2) * keep)
        speed = 0.9 + 0.8 * smoothstep(0, T_PEAK, t) + 1.2 * smoothstep(T_DRAIN, T_QUIET, t)
        stripe = (0.5 + 0.5 * np.cos(2 * np.pi * (edge / 170 - speed * t + 0.7))) ** 3
        fr += light(FORGE, (0.3 + 0.18 * beat) * stripe * keep)
        rim = np.exp(-((edge - front) / 70) ** 2) * (T_DRAIN < t < T_QUIET + 1)       # the falling edge
        fr += light(EMBER, 0.5 * rim * keep.max(initial=0))
        spark *= np.exp(-DT / 0.12)
        spark[rng.random(G.N) < 0.014 * keep] = 1.0
        fr += light(FORGE, 0.75 * spark)
        for ta, a, v in anvils:
            if ta <= t < ta + 0.5:
                g = (v / 115) * keep[np.argmin(np.abs(d - spots[a]))] ** 0.5
                fr += light(HOT, g * np.exp(-(t - ta) / 0.09) * blob(spots[a], 16))
                fr += light(FORGE, 0.7 * g * np.exp(-(t - ta) / 0.25) * blob(spots[a], 45))
        pk = last(brass, t, 0.3)
        if T_PEAK - 0.6 <= t < T_DRAIN + 1:
            fr += light(FORGE, 0.55 * pk * np.ones(G.N)) + light(GOLD, 0.35 * pk * blob(ap, 200))
        hoard = 1 - smoothstep(T_DRAIN, T_DRAIN + 6, t)
        if hoard > 0:
            fr += light(GOLD, hoard * (0.62 * blob(ph, 30) + 0.2 * blob(ph, 80)))
            fr += light(HOT, 0.45 * hoard * blob(ph, 14) * (0.6 + 0.4 * tw(t)) * (tw(t) > 0.3))

        # the mist between: grey-violet, drifting; a cold shadow while the renunciation passes
        mist = smoothstep(T_DRAIN + 4, T_QUIET, t) * (1 - 0.6 * old)
        fr += light(MIST, mist * (0.22 + 0.1 * drift(t)))
        for tw0 in woes:                                    # each cry of woe a red ripple out through the mist
            if tw0 <= t < tw0 + 2.5:
                rr = 900 * (t - tw0) ** 0.7
                fr += light(ALB, 0.45 * (1 - (t - tw0) / 2.5) * np.exp(-((np.abs(d - ap) - rr) / 90) ** 2))
        stir = sum(smoothstep(r0, r0 + 0.5, t) * (1 - smoothstep(r0 + 2.5, r0 + 4.5, t)) for r0 in RINGS)
        if stir > 0:                                        # the Ring's glints scattered through the mist
            fr += light(GOLD, 0.6 * stir * (rng.random(G.N) < 0.035))
        cold = smoothstep(T_REN, T_REN + 1.5, t) * (1 - smoothstep(T_REN + 4.0, T_REN + 6.5, t))
        if cold > 0:
            reach = (L / 2 + 300) * smoothstep(T_REN, T_REN + 4.5, t)
            shade = np.maximum(smoothstep(reach, reach - 300, d), smoothstep(L - reach, L - reach + 300, d)) * cold
            fr += light(SHADOW, 0.35 * shade)

        # grey dawn on the meadow; Valhalla dim across the porch, each Valhalla chord a breath of light
        if old > 0:
            dc = DAWN1[None, :] * (1 - huey[:, None]) + DAWN2[None, :] * huey[:, None]
            dc = dc * 0.9 + (dc @ np.array([0.3, 0.59, 0.11]))[:, None] * 0.1
            swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 900 - 0.05 * (t - T_DAWN)))
            lev = (0.36 + 0.1 * swell + 0.06 * drift(t)) * old * (wings + 0.5 * porch)
            fr += (np.clip(lev, 0, None) ** 2.2)[:, None] * dc
            vb = last(vals, t, 0.5)
            castle = smoothstep(T_DAWN + 3, T_VAL[0] + 2, t)
            fr += light(grey(VAL, 0.15), castle * (0.34 + 0.1 * vb) * merlon)

        # Loge, undimmed; the helmet's violet in his hand
        fk = 0.5 + 0.5 * np.tanh(fl(t))
        lb = blob(lp, 22)
        fr += light(LOGE1, 0.7 * lb * (1 - 0.5 * fk) + 0.25 * blob(lp, 70))
        fr += light(LOGE2, 0.55 * lb * fk)
        fr += light(TARN, 0.6 * blob(lp, 34) * (0.7 + 0.3 * tw(t)))

        # Wotan, greying with the dawn
        wc = grey(WOTAN, 0.4 * old)
        fr += light(wc, (0.85 + 0.15 * beat) * blob(wp, 22) + 0.3 * blob(wp, 90))
        fr += light(grey(SPEAR, 0.3 * old), 0.25 * blob(wp, 7))

        # Alberich, bound: red under steel-blue bands, his woe pulsing through them; the ring on his finger
        wo = last(woes, t, 0.5)
        fr += light(MUD, 0.32 * blob(ap, 90) * (1 + 0.15 * smoulder(t)))
        fr += light(ALB, (0.72 + 0.35 * wo) * blob(ap, 24 + 10 * wo) * (1 + 0.2 * smoulder(t)))
        wrap = (0.5 + 0.5 * np.cos(2 * np.pi * (d - ap) / 16 + 3 * t)) ** 2 * blob(ap, 34)
        fr += light(STEEL, (0.8 + 0.2 * beat) * wrap)
        rp = last(rings, t, 0.4)
        fr += light(GOLD, (0.9 + 0.4 * rp) * blob(ap, 6)) + light(RED, 0.7 * blob(ap + 9, 6) * (0.6 + 0.4 * tw(t)))
        ring = sum(smoothstep(r0, r0 + 0.5, t) * (1 - smoothstep(r0 + 2.5, r0 + 3.5, t)) for r0 in RINGS)
        if ring > 0:
            th = 2 * np.pi * (np.arange(12) / 12 + 0.3 * t)
            q, depth = ap + 160 * np.cos(th), np.sin(th)
            g = np.exp(-((d[:, None] - q[None, :]) / 18) ** 2)
            fr += light(GOLD, ring * (0.8 + 0.3 * rp) * (g * np.clip(depth, 0, 1)[None, :]).max(axis=1))
            fr += light(RED, ring * 0.55 * (g * np.clip(-depth, 0, 1)[None, :]).max(axis=1))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, the eighteen anvils, and the climb's sounds."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    spots = anvil_spots(G)
    o = Orchestra(M, level=1.6)
    N = compose()
    part = {(e[0], e[2], e[3]): e[4] for e in N if e[4] not in ('anvil', 'woe')}

    def role(t, d, m, v, h):
        p = part.get((t, m, v))
        if p == 'rise':                                     # the rushing lines: strings and flutes over horns
            if h == 0:
                return [('violins', 0, 6, 0.55)] + ([('flutes', 0, -6, 0.4)] if m >= note('C5') else [])
            return [('violas' if m >= 55 else 'cellos', 0, 10, 0.55)] + ([('horns', 0, 4, 0.5)] if d >= 0.3 else [])
        if p == 'nib':                                      # the Nibelung rhythm
            return [('violas', 0, 30, 0.55), ('cellos', 0, 24, 0.45)]
        if p == 'nibbass':                                  # the pedal deep in the basses
            return [('basses', 0, 40, 0.6), ('tuba', 12, 30, 0.5)] + ([('cellos', 12, 24, 0.4)] if d > 0.3 else [])
        if p == 'ringbrass':                                # the Ring motif's chords at the top of the climb
            return [('trombones', 0, 26, 0.6), ('horns', 12, 20, 0.5), ('trumpets', 12, 6, 0.35)]
        if p == 'trem':
            return [('violins trem' if m >= 55 else 'cellos trem', 0, 10, 0.5)]
        if p == 'valhalla':                                 # the arrival: brass chords, violins above
            if m < note('C3'):
                return [('tuba', 0, 20, 0.6), ('basses', 0, 14, 0.45)]
            if m < note('C5'):
                return [('horns', 0, 16, 0.55), ('trombones', 0, 10, 0.45)]
            return [('violins', 0, 10, 0.45)]
        return None                                         # the waves: the orchestra's default

    o.tutti(EX['notes'], size=lambda t: 0.9, role=role)
    for t, d, m, v, p, a in N:                              # the anvils, each at its own place on the house
        if p == 'anvil':
            o.hit('anvil', t, v, gain=0.16, pan=pan_at(spots[a]))
    # the stage: quiet under the anvils (they are the score), up as the caverns fall away, down for Valhalla
    o.effects([(0, -6), (T_DRAIN - 1, 0), (T_DAWN, -4), (T_VAL[0], -9)])
    o.thunder(T_DRAIN + 0.3, 0.25, 0.0, 0.9)                # the caverns falling away below
    o.hit('timpani roll', T_DRAIN, 100, pitch=-5, gain=0.5)
    o.wind(T_DAWN - 1.0, D, lambda tt: 0.5 + 0.2 * np.sin(tt * 0.7), 0.0)    # the cold mountain wind
    o.hit('crash', T_PEAK, 118, gain=0.5)
    o.hit('bass drum', T_PEAK, 124, gain=0.6)
