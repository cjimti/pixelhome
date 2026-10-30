"""Magic Fire: the end of the opera. Loge's flames, already round the porch, run on out along both wings and
down the Side until the whole house is ringed with fire: red at the roots, orange to gold at the tips, licking both
ways.

The music is Wagner's own: Act III, bars 1696 to 1716, then the last three bars of the opera, 1730 to 1733, as
Solti's 1958 Vienna Philharmonic recording takes them: Wotan's "durchschreite das Feuer nie!" on the hero's motif in
the brass over the fire music, the blaze in E major and its climax, the magic sleep sinking through the fire, and
the final chord. The notes come from the Wagner Ring Dataset's piano reduction of the score (pixelhome/ring.py),
orchestrated by hand and register: the left hand's long notes at the start (the hero's motif) on trumpets, horns
and trombones; the right hand's long notes, the sleep descending through the fire, on flutes, oboes and violins;
its glittering figuration on harp, violins and glockenspiel; the rest of the left hand on the full orchestra,
fullest at the climax with timpani and cymbals on its downbeats; and the last bars softly on strings, harp, flutes
and glockenspiel. Over it the stage adds what the house shows: the fire roaring and crackling the whole time,
spreading from the rock across the house, flaring with a roar and a boom at the blaze and each beat of the climax,
a whoosh for every tongue of flame that leaps, Wotan's heavy steps as he walks out through it, and the fire
settling to crackling embers under the last chord. The fire sits under the music: back under the hero's motif
and the sleep sinking through the flames, leading only at the blaze and the climax, back again as Wotan looks back
(his footsteps through the flames a little forward as he leaves), and down to a few embers under the final chord.

The lights follow the real notes. Each note of the hero's motif flashes the house gold and a white-gold streak runs
in from the free end of Right toward the sleeper, once for each of its two phrases. Every long note of the sleep is a
violet ripple out from her through the flames and a tongue of fire leaping along the roofline; every glittering note
a spark of white-gold. At the climax the fire leaps up on each downbeat and the house flashes gold. Then Wotan looks
back at her one last time (a thin line of his blue reaches toward her and falls back) and walks away through the
fire, along Porch Left and Left and out along the Side to its far end, the flames parting round him and closing
behind. In the last bars the fire settles, the sleep's last arpeggio shimmers down from her, and the opera ends on
the final chord: a glowing bed of fire all round the house, and in the middle of it, at the summit of the rock, the
sleeping Brünnhilde.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK30'
TITLE = 'Magic Fire'
KIND = 'show'
DESCRIPTION = ('Fire rings the rock and then the whole house, and over it the music of sleep shimmers while '
               'Wotan swears that no one who fears his spear will ever pass. He looks back once, walks out '
               'through the flames, and leaves his daughter sleeping in a ring of fire.')
VOICEOVER = ('The fire spreads until it surrounds everything. '
             'Only a hero who knows no fear will ever walk through it.')

EX = excerpt(__file__)                      # Act III, bars 1696-1716 and 1730-1733, Solti 1958
BAR = {}
for m, t in EX['bars']:
    BAR.setdefault(int(m), t)
SIEGS = [BAR[1696], BAR[1698]]              # the hero's motif, two phrases
SIEG_END = BAR[1700]
T_BLAZE = BAR[1700]                         # the blaze in E major
CLIMAX = [BAR[1709], BAR[1710], BAR[1711]]  # its climax
T_LOOK = BAR[1712]                          # Wotan looks back
T_LEAVE = BAR[1713] + 0.5                   # and walks out through the fire
T_GONE = BAR[1716] - 0.5
T_END = EX['segments'][1]['start']          # the last bars
T_CASCADE = BAR[1731]                       # the sleep's last arpeggio
T_CHORD = BAR[1732]                         # the final chord
D = EX['seconds']
T0 = 80.0 * 29                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
VIOLET = hexc('#7a6aff')
SHIELD = hexc('#c8d8ff')
HERO = hexc('#fff0a0')
GOLD = hexc('#ffd060')
SPARK = hexc('#fff0b0')
FATE_HI = hexc('#4a2ab8')
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
    """The fire's state at our time t: (reach from the rock, level), picking up where WK29 leaves it."""
    reach = np.interp(t, [0, 6, 14, 22], [700, 1000, 1500, 2600])
    level = np.interp(t, [0, T_BLAZE, CLIMAX[0], T_LOOK, T_END, D], [.85, .9, .95, .9, .72, .64])
    return float(reach), float(level)


def flames(d, t, ta, ds, db, fl, boost=0.0, settle=0.0):
    """Light of the fire at time t (clock ta): ds = distance from where the spear struck, db = from the sleeper."""
    reach, level = blaze(t)
    on = smoothstep(reach + 70, reach - 70, ds)
    front = np.exp(-((ds - reach) / 60) ** 2) * smoothstep(0, 60, reach)
    q = np.clip((heat(d, ta) + 0.18 * fl(ta) + 0.25 * front + 0.3 * boost) * (1 - 0.12 * settle) + 0.05 * settle, 0, 1)
    ring = 1 - 0.75 * np.exp(-(db / 42) ** 2)
    lvl = (level + 0.15 * boost - 0.04 * settle) * on * ring
    return light(FIRE(q), lvl * (0.45 + 0.7 * q)) + light(AMBER, 0.35 * front * ring), lvl


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand): 'sieg' the hero's motif (the
    left hand's long notes at the start), 'sleep' the right hand's long notes, 'spark' its glittering figuration,
    'mid' the rest of the left hand, and 'end' the last bars."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t >= T_END - 0.01:
            part = 'end'
        elif h == 1:
            part = 'sieg' if t < SIEG_END - 0.01 and d >= 0.6 else 'mid'
        else:
            part = 'sleep' if d >= 0.6 else 'spark'
        N.append((t, d, m, v, part, h))
    return N


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
    """Per frame: where Wotan is (path distance) as he walks out through the fire; Brünnhilde sleeps at the summit."""
    F = nframes(D)
    t = np.arange(F) * DT
    p0 = at(G, 'Porch Front', 0.25)
    u = np.clip((t - T_LEAVE) / (T_GONE - T_LEAVE), 0, 1)
    w = p0 + (-30.0 - p0) * (u * u * (3 - 2 * u)) ** 0.9
    look = 6 * np.sin(np.pi * np.clip((t - T_LOOK) / 6, 0, 1))          # a step toward her as he looks back
    return dict(t=t, w=follow(w + look, np.full(F, 4.0)), b=np.full(F, at(G, 'Porch Front', 0.5)))


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sh = Flicker(np.random.default_rng(2801), G.N, 0.3, 1.2)            # the shield's shimmer
    fl = Flicker(np.random.default_rng(2901), G.N, 4.0, 11.0)           # flame flicker, shared with WK29
    pb = at(G, 'Porch Front', 0.5)
    sp = at(G, 'Porch Front', 0.25)
    ds = np.abs(d - sp)
    db = np.abs(d - pb)
    sleeps = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    sieg = np.array(sorted({e[0] for e in N if e[4] == 'sieg'}))
    hits = np.array(sorted(set(sieg) | set(CLIMAX) | {T_BLAZE}))
    glints = np.array(sorted({e[0] for e in N if e[4] == 'spark' and e[3] >= 60}))
    ends = np.array(sorted({e[0] for e in N if e[4] == 'end'}))
    # a leaping tongue for each long note of the sleep: (start, from, direction)
    leaps = [(t0, rng.uniform(0, L), rng.choice([-1, 1])) for t0 in sleeps]
    glint_at = rng.uniform(0, L, len(glints))

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw = C['w'][f]
        dw = np.abs(d - pw)
        boost = recent(np.array(CLIMAX + [T_BLAZE]), t, 1.2) + 0.5 * recent(sieg, t, 0.8)
        gone = smoothstep(T_GONE - 1.5, T_GONE + 0.5, t)
        settle = smoothstep(T_END - 2, D - 3, t)

        # the fire, parting round Wotan as he walks through it
        fire, lvl = flames(d, t, ta, ds, db, fl, min(boost, 1.0), settle)
        part = 1 - 0.85 * np.exp(-(dw / 45) ** 2) * (1 - gone) * smoothstep(T_LEAVE - 1, T_LEAVE + 1, t)
        fr *= (1 - 0.6 * np.clip(lvl / 0.7, 0, 1))[:, None]
        fr += fire * part[:, None]

        # leaping tongues and glittering sparks
        for t0, x0, sd in leaps:
            if t0 <= t < t0 + 0.9:
                age = t - t0
                q = x0 + sd * 300 * (age / 0.9) ** 0.6
                fr += light(AMBER, 1.0 * (1 - age / 0.9) * np.exp(-((d - q) / 40) ** 2) * (lvl > 0.05))
                fr += light(SPARK, 0.85 * (1 - age / 0.9) * np.exp(-((d - q) / 14) ** 2) * (lvl > 0.05))
        i = int(np.searchsorted(glints, t, side='right')) - 1
        for j in range(max(0, i - 4), i + 1):
            if 0 <= t - glints[j] < 0.5:
                fr += light(SPARK, 0.9 * np.exp(-(t - glints[j]) / 0.15) * np.exp(-((d - glint_at[j]) / 8) ** 2))

        # the sleep: violet ripples through the flames from her
        i = int(np.searchsorted(sleeps, t, side='right')) - 1
        sp_ = recent(sleeps, t, 0.9)
        if i >= 0 and t - sleeps[i] < 2.2:
            age = t - sleeps[i]
            band = np.exp(-((db - 1100 * age / 2.2) / 150) ** 2) * (1 - age / 2.2)
            fr *= (1 - 0.4 * band)[:, None]
            fr += light(VIOLET, 0.8 * band)

        # the hero's motif and the climax: the house flashes gold; a white-gold streak runs in from the free end
        hp = recent(hits, t, 0.3)
        fr += light(GOLD, 0.75 * hp * np.ones(G.N)) + light(SPARK, 0.4 * hp ** 2 * np.ones(G.N))
        for k, t0 in enumerate(SIEGS):
            t1 = SIEGS[k + 1] if k + 1 < len(SIEGS) else SIEG_END
            if t0 <= t < t1 + 1.5:
                u = np.clip((t - t0) / (t1 - t0 - 0.5), 0, 1)
                q = L + (pb + 60 - L) * u ** 0.8
                fade = 1 - smoothstep(t1, t1 + 1.5, t)
                n = recent(sieg, t, 0.15)
                fr += light(HERO, fade * ((0.95 + 0.05 * n) * np.exp(-((d - q) / 26) ** 2)
                                          + (0.5 + 0.3 * n) * (d > q) * np.exp(-(d - q) / 300)))

        # the last bars: the sleep's last arpeggio shimmers down from her, and the final chord glows
        if t >= T_END:
            ep = recent(ends, t, 0.5)
            if T_CASCADE <= t < T_CHORD + 3:
                u = np.clip((t - T_CASCADE) / (T_CHORD - T_CASCADE), 0, 1)
                r = 1500 * u
                fr += light(mix(VIOLET, SILVER, 0.4), 0.55 * (1 - 0.5 * u) * np.exp(-((db - r) / 160) ** 2) * (1 - smoothstep(T_CHORD, T_CHORD + 3, t)))
            chord = smoothstep(T_CHORD - 0.3, T_CHORD + 1.5, t)
            fr += light(VIOLET, chord * (0.25 + 0.1 * ep) * np.exp(-(db / 260) ** 2))

        # Wotan: looks back (a thin line of blue toward her), then walks out along the Side
        lk = smoothstep(T_LOOK, T_LOOK + 1.0, t) * (1 - smoothstep(T_LEAVE - 1.5, T_LEAVE, t))
        if lk > 0:
            reach = (pb - pw) * lk
            line = ((d > pw) & (d < pw + reach)) * (0.5 + 0.2 * np.sin(2 * np.pi * (d / 30 - 1.5 * ta)))
            fr += light(WOTAN_SOFT, 0.85 * lk * line)
        wc = mix(WOTAN, WOTAN_SOFT, 0.2 + 0.4 * lk)
        fr += light(wc, (1 - gone) * ((0.9 + 0.1 * lk) * np.exp(-(dw / 24) ** 2) + 0.375 * np.exp(-(dw / 120) ** 2)))

        # Brünnhilde asleep under her shield, glowing up with each note of the sleep
        fr += light(SLEEP_C, (0.53 + 0.15 * sp_) * np.exp(-(db / 26) ** 2) + (0.28 + 0.1 * sp_) * np.exp(-(db / 70) ** 2))
        arc = np.exp(-(db / 34) ** 4)
        fr += light(SHIELD, (0.32 + 0.08 * sh(ta)) * arc + 0.4 * (rng.random(G.N) < 0.06) * arc)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, the hero's motif on the brass."""
    o = Orchestra(M, level=1.7)

    def role(t, d, m, v, h):
        if t >= T_END - 0.01:                                   # the last bars, softly
            if h == 0:
                return [('harp', -12, 45, 0.8), ('flutes', -12, 35, 0.5)] + ([('glock', -24, 35, 0.35)] if d > 1 else [])
            return [('violas' if m >= 48 else 'cellos', 0, 45, 0.8), ('horns', 0, 35, 0.5), ('harp', 0, 35, 0.45)]
        if h == 1 and t < SIEG_END - 0.01 and d >= 0.6:          # the hero's motif
            return [('trumpets', 0, 8, 0.5), ('horns', 0, 8, 0.6), ('trombones', -12, 4, 0.45)]
        if h == 0 and d >= 0.6:                                 # the sleep, sinking through the fire
            return [('flutes', -12, 6, 0.5), ('oboes', -12, 0, 0.35), ('violins', -12, 0, 0.45)]
        if h == 0:                                              # the fire's glitter
            parts = [('harp', -12, 0, 0.45), ('violins', -12, -10, 0.3)]
            if m >= 84 and v >= 90:
                parts.append(('glock', -24, -10, 0.25))
            return parts
        return None

    o.tutti(EX['notes'], size=lambda t: 1.0 if CLIMAX[0] - 2 <= t < T_LOOK + 2 else 0.6, role=role)
    for t in CLIMAX + [T_BLAZE]:
        o.hit('timpani', t, 118, pitch=-2, gain=0.55)
        o.hit('crash', t, 112, gain=0.4)
    o.hit('cymbal swell', CLIMAX[0] - 2.5, 95, gain=0.35)
    o.hit('timpani roll', T_CHORD, 50, gain=0.2)

    pan_at = house_pan(G)
    C = choreography(G)
    N = compose()
    L = G.length
    sp = pan_at(at(G, 'Porch Front', 0.25))
    # the fire sits under the music: the hero's motif and the sleep sinking through the flames must be clear, so its
    # roar stays back, lifting at the blaze and the climax, back again as Wotan looks and leaves, embers at the end
    o.effects([(0, -7), (T_BLAZE - 1, -7), (T_BLAZE, -3), (T_BLAZE + 3, -8), (CLIMAX[0] - 0.5, -2),
               (CLIMAX[-1] + 2, -2), (T_LOOK, -9), (T_LEAVE, -6), (T_GONE, -9), (T_END, -14), (D, -16)])
    # the fire: a roar and crackle the whole scene, spreading from the rock to the whole house (the sound widens to
    # the middle of the street), flaring with the climax, settling to embers on the last bars
    climax = np.array(CLIMAX + [T_BLAZE])

    def level(tt):
        reach = np.interp(tt, [0, 6, 14, 22], [700, 1000, 1500, 2600])
        lv = np.interp(tt, [0, T_BLAZE, CLIMAX[0], T_LOOK, T_END, D], [.85, .9, .95, .9, .72, .64])
        boost = sum(np.exp(-np.clip(tt - c, 0, None) / 1.2) * (tt >= c) for c in climax)
        settle = smoothstep(T_END - 2, D - 3, tt)
        return np.clip(lv * (0.65 + 0.35 * np.clip(reach / 2600, 0, 1)) + 0.25 * np.minimum(boost, 1), 0, 1.2) \
            * (1 - 0.8 * settle)
    o.fire(0, D, level=lambda tt: 0.5 * level(tt), pan=lambda t: sp * (1 - smoothstep(0, 22, t)), crackle=22, seed=300)
    o.fire(0, D, level=lambda tt: 0.3 * level(tt), pan=lambda t: -0.5 * smoothstep(4, 22, t), crackle=10, seed=301)
    # the leaping tongues of flame: each a whoosh where it leaps
    rng = np.random.default_rng(30)                             # the same draws render() makes
    sleeps = np.array(sorted({e[0] for e in N if e[4] == 'sleep'}))
    leaps = [(t0, rng.uniform(0, L), rng.choice([-1, 1])) for t0 in sleeps]
    for k, (t0, x0, sd) in enumerate(leaps):
        if t0 < T_END:
            o.M.add('fx', whoosh(0.9, 250, 2200, 0.55, seed=3000 + k), t0, 0.6, pan_at(x0 + sd * 150))
    # the blaze and the climax: the fire flaring up with a roar and a boom
    for k, t0 in enumerate(climax):
        o.M.add('fx', whoosh(1.6, 150, 3000, 0.8, seed=3100 + k), t0 - 0.3, 0.8, 0.0)
        o.boom(t0, 0.0, gain=0.6)
    # Wotan walks out through the fire: heavy steps parting the flames, going off along the Side
    wp = lambda t: pan_at(np.interp(t, C['t'], C['w']))
    t = T_LEAVE
    while t < T_GONE:
        o.hit('timpani', t, 84, pitch=-9, gain=0.35, pan=wp(t), fx=True)
        o.hit('bass drum', t, 80, gain=0.3, pan=wp(t), fx=True)
        t += 0.95
    # the final chord: a last ember cracks and a soft gong glows with her
    o.M.add('perc', o.M.hits('Percussion/gongHit_p.wav').play(90), T_CHORD, 0.4, pan_at(at(G, 'Porch Front', 0.5)))


def house_pan(G):
    """Path distance -> left/right across the facade, as heard from the street."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    return lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))
