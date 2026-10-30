"""Loge, Come!: night on the rock. Brünnhilde sleeps at the summit under her shield, a still violet-silver glow
in the middle of Porch Front, and Wotan stands a little way off to her left.

The music is Wagner's own: Act III, bars 1646 to 1680, as Solti's 1958 Vienna Philharmonic recording takes them,
from Wotan gripping his spear, its motif striding down in octaves, through "Loge, hör'! Lausche hieher!" over the
roaring string tremolo, "Herauf, wabernde Lohe" and "Loge! Loge! Hieher!", to the flames rushing up the chromatic
scales and the first bars of the Magic Fire in E major. The notes come from the Wagner Ring Dataset's piano
reduction of the score (pixelhome/ring.py): the spear's octaves on trombones, tuba, horns and basses; the tremolo
on violas and cellos with the brass on its long notes; the rising scales on violins and flutes; the Magic Fire's
glittering arpeggios on harp, glockenspiel and flutes over violins, its middle on violas and clarinets. Over it
the stage adds what the house shows: the night wind rising as he calls; steel ringing on the spear's motif; a
gong and drum on "Loge, hör'!" and the rock rumbling louder on every bar of the call as its embers glow; three
strikes of steel on stone, each a huge boom, the rock cracking and the mountain rumbling; then the flames
bursting out with a rushing roar and burning on, crackling, louder as they spread along the porch. The effects
stay back under the spear's motif and the call, lead at full level for the three strikes and the fire bursting out,
then back off under the Magic Fire's first bars so its music is clear.

He turns away from her and grips his spear: every note of its motif a cold steel pulse running out from him along
the roof while the shaft gleams at his side. "Loge, hör'!": his blue swells with the call, and the rock begins to
glow where the spear will strike, red embers pulsing with the tremolo and a red pulse racing out to both ends of
the house on every bar, wider and brighter as he calls the fire up. Then three huge strikes of the spear on the
rock: a steel-white shock across the whole house and a band of steel light racing out to both ends of the
roofline. With the third the rock answers: flames burst out of it, climb with the scales and begin to spread
along the porch in both directions, red at the roots and orange to gold at the tips, every glittering note of the
Magic Fire a spark in them. By the end they have run the length of the porch, a ring round the sleeper who glows on
untouched in the middle, and the first tongues are reaching for the wings.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'WK29'
TITLE = 'Loge, Come!'
KIND = 'show'
DESCRIPTION = ('Wotan strikes the rock three times with his spear and calls on Loge, the god of fire. The rock '
               'answers: flames burst out and begin to race along the porch around his sleeping daughter.')
VOICEOVER = ('Three blows of the spear on the rock, and a name called into the night. '
             'Loge, come. And the fire comes.')

EX = excerpt(__file__)                      # Act III, bars 1646-1680, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_SPEAR = BAR[1647]                         # the spear's motif, striding down in octaves
T_CALL = BAR[1650]                          # "Loge, hör'!" over the tremolo
T_RISE = BAR[1661]                          # "Herauf, wabernde Lohe"
T_LOGE = BAR[1668]                          # "Loge! Loge! Hieher!"
T_FIRE = BAR[1670]                          # the third strike: flames burst out of the rock and climb the scales
T_MAGIC = BAR[1674]                         # the Magic Fire
D = EX['seconds']
T0 = 80.0 * 28                              # the opera's clock at our start
# three strikes of the spear: on the bass chords of "hieher!", the third as the flames burst out
_bass = sorted({n[0] for n in EX['notes'] if n[4] == 1 and n[2] < 44 and n[1] >= 0.5 and BAR[1669] - 0.1 <= n[0] <= T_FIRE + 0.1})
STRIKES = [_bass[0], _bass[len(_bass) // 2], T_FIRE]

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
VIOLET = hexc('#7a6aff')
SHIELD = hexc('#c8d8ff')
STEEL = hexc('#c8d8ff')
WHITE = hexc('#ffffff')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
CLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
ROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')
SLEEP_C = VIOLET + (SILVER - VIOLET) * 0.2


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def mix(a, b, w):
    return a + (b - a) * w


def stage(d, ta, porch):
    """The rock (porch) and the evening sky over the wings, on the opera's clock ta (shared by WK25-WK30)."""
    bt = ta - 1920.0
    rock = np.interp(bt, [0, 160, 240, 320, 400, 480], [.42, .42, .43, .38, .34, .3])
    sky = np.interp(bt, [0, 80, 160, 240, 320, 480], [.4, .41, .41, .38, .34, .3])
    eve = np.interp(bt, [0, 80, 160, 240], [.45, .85, 1.0, .9])
    night = np.interp(bt, [200, 320, 400], [0.0, .6, .85])
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.011 * ta)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.023 * ta) + 1.1)
    sk = CLOUD + (EVE - CLOUD) * (eve * (0.35 + 0.65 * u))[:, None]
    sk = sk + (NIGHT - sk) * night
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    return light(sk, sky * (0.7 + 0.3 * u) * (1 - porch)) + light(rk, rock * (0.8 + 0.2 * u) * porch)


def heat(d, ta):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways, swelling and sinking
    region by region."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * ta)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * ta) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * ta) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * ta) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * ta)) * np.sin(2 * np.pi * (d / 260 - 0.31 * ta) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def blaze(t):
    """The fire's state at our time t: (reach from the rock, level). WK30 picks it up where this leaves it."""
    reach = np.interp(t, [T_FIRE, T_FIRE + 1.6, T_MAGIC, T_MAGIC + 8, D], [0, 120, 340, 520, 700])
    level = np.interp(t, [T_FIRE, T_FIRE + 0.7, T_MAGIC, T_MAGIC + 1, D], [0, .95, .8, .9, .85])
    return float(reach), float(level) * (t >= T_FIRE)


def flames(d, t, ta, ds, db, fl):
    """Light of the fire at time t (clock ta): ds = distance from where the spear struck, db = from the sleeper."""
    reach, level = blaze(t)
    if level <= 0 or reach <= 0:
        return np.zeros((len(d), 3)), np.zeros(len(d))
    on = smoothstep(reach + 70, reach - 70, ds)
    front = np.exp(-((ds - reach) / 60) ** 2) * smoothstep(0, 60, reach)
    q = np.clip(heat(d, ta) + 0.18 * fl(ta) + 0.25 * front, 0, 1)
    ring = 1 - 0.75 * np.exp(-(db / 42) ** 2)
    lvl = level * on * ring
    return light(FIRE(q), lvl * (0.45 + 0.7 * q)) + light(AMBER, 0.35 * front * ring), lvl


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand): 'spear' the left hand's
    octaves, 'call' everything under the call, 'run' the scales, 'spark' the Magic Fire's right hand and 'glow' its
    left; 'pre' the bar before the spear."""
    N = []
    for t, d, m, v, h in EX['notes']:
        part = ('pre' if t < T_SPEAR - 0.01 else 'spear' if t < T_CALL - 0.01 else 'call' if t < T_FIRE - 0.01
                else 'run' if t < T_MAGIC - 0.01 else 'spark' if h == 0 else 'glow')
        N.append((t, d, m, v, part, h))
    return N


def energy(N, F):
    """Per frame: how loud and busy the orchestra is, 0..1 (velocity-weighted notes, smoothed)."""
    e = np.zeros(F)
    for t, d, m, v, part, h in N:
        f0, f1 = int(t / DT), int(min(t + max(d, 0.15), D) / DT) + 1
        e[f0:f1] += (v / 127) ** 2 / max(1, f1 - f0) ** 0.5
    k = np.exp(-np.arange(-40, 41) ** 2 / (2 * 14 ** 2))
    e = np.convolve(e, k / k.sum(), 'same')
    return np.clip(e / np.percentile(e, 97), 0, 1)


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
    """Per frame: where Wotan is (path distance); Brünnhilde sleeps at the middle of Porch Front."""
    F = nframes(D)
    t = np.arange(F) * DT
    w = np.full(F, at(G, 'Porch Front', 0.25))
    sway = 4 * np.sin(2 * np.pi * (t - T_CALL) / 2.0) * ((t > T_CALL) & (t < STRIKES[0] - 0.5))
    return dict(t=t, w=follow(w + sway, np.full(F, 3.0)), b=np.full(F, at(G, 'Porch Front', 0.5)))


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    E = energy(N, F)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)            # the shield's shimmer, from WK28
    fl = Flicker(np.random.default_rng(2901), G.N, 4.0, 11.0)           # flame flicker, shared with WK30
    spears = np.array(sorted({e[0] for e in N if e[4] == 'spear'}))
    pulses = np.array([BAR[m] for m in range(1650, 1670)])              # a red pulse on every bar of the call
    sparks = np.array(sorted({e[0] for e in N if e[4] == 'spark'}))
    pb = at(G, 'Porch Front', 0.5)
    sp = at(G, 'Porch Front', 0.25)                                       # where the spear strikes the rock
    ds = np.abs(d - sp)
    db = np.abs(d - pb)
    jag = [rng.random(G.N) for _ in range(3)]
    spot = rng.random((len(sparks), 3))

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        e = E[f]
        fr = stage(d, ta, porch)
        pw = C['w'][f]

        # the fire
        fire, lvl = flames(d, t, ta, ds, db, fl)
        fr *= (1 - 0.6 * np.clip(lvl / 0.7, 0, 1))[:, None]
        fr += fire
        # the firelight on the clouds over the wings
        _, level = blaze(t)
        if level > 0:
            glow = level * (1 - porch) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 700 - 0.13 * ta))) * (0.75 + 0.25 * fl(ta))
            fr += light(FIRE(0.3 + 0.25 * glow), 0.3 * glow)
        # every glittering note of the Magic Fire a spark in the flames
        i = int(np.searchsorted(sparks, t, side='right')) - 1
        reach, _ = blaze(t)
        for j in range(max(0, i - 4), i + 1):
            age = t - sparks[j]
            if 0 <= age < 0.5:
                q = sp + (2 * spot[j, 0] - 1) * (reach + 60)
                fr += light(hexc('#fff0b0'), 0.9 * np.exp(-age / 0.15) * np.exp(-((d - q) / (10 + 20 * spot[j, 1])) ** 2))

        # the spear's motif: steel pulses running out from him, the shaft gleaming at his side
        spl = smoothstep(T_SPEAR - 1, T_SPEAR, t) * (1 - smoothstep(STRIKES[2] + 0.5, STRIKES[2] + 3, t))
        if spl > 0:
            i = int(np.searchsorted(spears, t, side='right')) - 1
            if i >= 0 and t - spears[i] < 1.4 and t < T_CALL + 1:
                age = t - spears[i]
                band = np.exp(-((np.abs(d - pw) - 1300 * age / 1.4) / 90) ** 2) * (1 - age / 1.4)
                fr += light(STEEL, 0.7 * band)
            shaft = ((d > pw - 70) & (d < pw - 8)) * (0.45 + 0.4 * recent(spears, t, 0.3))
            fr += light(STEEL, spl * shaft)

        # the call: his blue swells with the orchestra; the rock glows red where the spear will strike, a red pulse
        # racing out to both ends on every bar, wider and brighter as he calls the fire up
        call = smoothstep(T_CALL - 0.3, T_CALL + 0.3, t) * (1 - smoothstep(T_FIRE, T_FIRE + 1, t))
        if call > 0:
            up = 0.5 + 0.5 * smoothstep(T_RISE - 2, T_LOGE, t)
            fr += light(WOTAN, call * (0.3 + 0.45 * e) * np.exp(-((d - pw) / (350 + 900 * e)) ** 2))
            ember = np.exp(-(ds / (140 + 380 * up)) ** 2)
            fr *= (1 - 0.4 * call * ember)[:, None]
            fr += light(FIRE(np.clip(0.35 + 0.4 * fl(ta) * up, 0, 1)), call * (0.45 + 0.5 * e) * up * ember)
            i = int(np.searchsorted(pulses, t, side='right')) - 1
            if i >= 0 and t - pulses[i] < 2.0:
                age = t - pulses[i]
                r = 2400 * up * (age / 2.0) ** 0.7
                band = np.exp(-((ds - r) / 240) ** 2) * (1 - age / 2.0)
                trail = smoothstep(r + 50, r - 300, ds) * (1 - age / 2.0) ** 2
                fr += light(RED, call * (0.55 + 0.3 * up) * band + call * 0.2 * up * trail)
                fr += light(ORANGE, call * 0.45 * up * band ** 3)
        if T_CALL <= t < T_CALL + 2.5:                    # "Loge, hör'!"
            a = np.exp(-(t - T_CALL) / 0.5)
            fr += light(WOTAN, 0.7 * a * np.ones(G.N)) + light(RED, 0.4 * a * np.exp(-(ds / 400) ** 2))

        # three strikes: a steel-white shock across the house and a band racing to both ends
        for k, ts in enumerate(STRIKES):
            if ts <= t < ts + 1.6:
                age = t - ts
                a = np.exp(-age / 0.15)
                fr += light(WHITE, (0.8 + 0.07 * k) * a * np.ones(G.N))
                r = 2600 * (age / 1.2) ** 0.7
                band = np.exp(-((np.abs(d - sp) - r) / 120) ** 2) * (1 - age / 1.6)
                fr += light(STEEL, 0.9 * band) + light(WHITE, 0.6 * band * (jag[k] > 0.5))
                fr += light(STEEL, 0.6 * np.exp(-age / 0.5) * np.exp(-(ds / 120) ** 2))
        if T_FIRE <= t < T_FIRE + 2.5:                   # the burst out of the rock
            a = np.exp(-(t - T_FIRE) / 0.6)
            burst = (rng.random(G.N) < 0.25 * a) * np.exp(-(ds / (200 + 500 * (t - T_FIRE))) ** 2)
            fr += light(AMBER, 0.9 * a * np.exp(-(ds / 80) ** 2)) + light(hexc('#fff0b0'), 0.9 * burst)

        # Wotan
        cp = call * e
        wc = mix(WOTAN, WOTAN_SOFT, 0.5 - 0.3 * smoothstep(T_SPEAR, T_CALL, t))
        fr += light(wc, (0.85 + 0.1 * cp) * np.exp(-((d - pw) / 24) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))

        # Brünnhilde asleep under her shield
        fr += light(SLEEP_C, 0.53 * np.exp(-(db / 26) ** 2) + 0.28 * np.exp(-(db / 70) ** 2))
        arc = np.exp(-(db / 34) ** 4)
        fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * (rng.random(G.N) < 0.06) * arc)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, with the spear's strikes on the percussion."""
    o = Orchestra(M, level=2.15)

    def role(t, d, m, v, h):
        if t < T_SPEAR - 0.01:
            return [('cellos' if m < 48 else 'violas', 0, 0, 0.6), ('horns', 0, -10, 0.4)]
        if t < T_CALL - 0.01:                                   # the spear: brass and basses in octaves
            return ([('trombones', 0, 0, 0.8), ('tuba', 0, -4, 0.7), ('basses', 0, -6, 0.5)] if m < 48 else
                    [('horns', 0, 0, 0.8), ('trombones', 0, -6, 0.5)])
        if t < T_FIRE - 0.01:                                   # the call: string tremolo, brass on the long notes
            return None
        if t < T_MAGIC - 0.01:                                  # the scales: violins and flutes rushing up
            return ([('violins', 0, 0, 0.5), ('flutes', 12, -10, 0.35)] if h == 0 or m >= 55 else None)
        if h == 0:                                              # the Magic Fire's glitter
            parts = [('harp', -12, 0, 0.5), ('flutes', -12, -14, 0.3), ('violins', -12, -16, 0.3)]
            if d >= 0.3 or m in (88, 90, 92, 94):
                parts.append(('glock', -24, -10, 0.3))
            return parts
        return [('violas', 0, -12, 0.45), ('clarinets', 0, -10, 0.4), ('harp', -12, -10, 0.35)]

    call = lambda n: T_CALL - 0.01 <= n[0] < T_FIRE - 0.01
    notes = [n for n in EX['notes'] if not call(n)] + tidy([n for n in EX['notes'] if call(n)])
    o.tutti(sorted(notes), size=lambda t: 1.0 if T_CALL <= t < T_FIRE else 0.7, role=role)

    pan_at = house_pan(G)
    C = choreography(G)
    N = compose()
    sp = pan_at(at(G, 'Porch Front', 0.25))                     # where the spear strikes the rock
    wp = lambda t: pan_at(np.interp(t, C['t'], C['w']))
    # the spear's motif and the call are the music's: the wind and embers stay back (rising as he calls the fire up);
    # the three strikes and the fire bursting out lead at full level; then they back off so the Magic Fire is clear
    o.effects([(0, -10), (T_CALL, -10), (T_LOGE, -6), (STRIKES[0] - 0.3, 0), (T_FIRE + 3, 0), (T_MAGIC, -5),
               (T_MAGIC + 3, -9), (D, -9)])
    # the night wind on the rock, rising as he calls the fire
    o.wind(0, T_FIRE + 3, level=lambda tt: 0.35 + 0.5 * smoothstep(T_CALL, T_LOGE, tt), pan=-0.4)
    # the spear's motif: steel ringing on its loudest octaves
    for ts in accents([e for e in N if e[4] == 'spear'], vmin=70, n=1, space=0.45):
        o.hit('metal', ts, 90, gain=0.3, pan=wp(ts), fx=True)
        o.hit('brake drum', ts, 80, gain=0.2, pan=wp(ts), fx=True)
    # "Loge, hör'!": a gong and drum as his blue swells; then the rock rumbling louder on every bar of the call
    o.boom(T_CALL, wp(T_CALL), gain=0.6)
    o.hit('crash', T_CALL, 110, gain=0.4)
    for m in range(1650, 1670):
        up = 0.5 + 0.5 * smoothstep(T_RISE - 2, T_LOGE, BAR[m])
        o.hit('timpani', BAR[m], int(70 + 40 * up), pitch=-7, gain=0.25 + 0.3 * up, pan=sp, fx=True)
    o.fire(T_CALL, T_FIRE + 0.5, level=lambda tt: 0.15 + 0.35 * smoothstep(T_RISE - 2, T_LOGE, tt), pan=sp,
           crackle=4, seed=29)
    o.hit('cymbal swell', STRIKES[0] - 2.4, 100, gain=0.4, pan=sp)
    # three strikes on the rock: steel on stone, a huge boom, the rock cracking and the mountain rumbling
    for k, ts in enumerate(STRIKES):
        o.hit('timpani', ts, 118, pitch=-4, gain=0.6, fx=True)
        o.hit('crash', ts, 115, gain=0.4, fx=True)
        o.clash(ts, sp, 120, gain=0.8 + 0.1 * k)
        o.boom(ts, sp, gain=1.0 + 0.15 * k)
        o.thunder(ts + 0.03, near=0.7 + 0.15 * k, pan=sp, gain=0.7 + 0.15 * k, seed=290 + k)
    # the flames burst out of the rock with a rushing roar, and burn on, spreading along the porch
    o.M.add('fx', whoosh(1.4, 200, 5000, 0.9, seed=29), T_FIRE - 0.2, 1.0, sp)
    o.M.add('fx', whoosh(2.5, 300, 2500, 0.7, seed=31), T_FIRE + 0.5, 0.8, sp * 0.5)
    o.hit('cymbal swell', T_MAGIC - 3, 90, gain=0.35)
    reach_lv = lambda tt: np.array([blaze(x)[1] * (0.6 + 0.4 * min(blaze(x)[0] / 700, 1)) for x in tt])
    o.fire(T_FIRE, D, level=reach_lv, pan=lambda t: sp * (1 - 0.6 * smoothstep(T_FIRE, D, t)), crackle=18, seed=290)


def house_pan(G):
    """Path distance -> left/right across the facade, as heard from the street."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    return lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))
