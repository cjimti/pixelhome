"""Was It So Shameful?: the sisters have fled and the storm has blown itself out. On the rock (the porch, dark
slate washed with dusk violet) Wotan stands in his deep blue at the left of Porch Front and Brünnhilde kneels a
little way off, her silver dimmed, while the clouds over the wings turn slowly toward evening.

The music is Wagner's own: Act III, bars 1032 to 1040 and 1132 to 1163, as Solti's 1958 Vienna Philharmonic
recording takes them. She pleads ("O sag, Vater! Sieh mir ins Auge; schweige den Zorn"), then tells him what she
saw when she went to Siegmund to announce his death ("Tod kündend trat ich vor ihn"): his need, his lament, his
love and his defiance, swelling to "Meinem Ohr erscholl, mein Aug' erschaute, was tief im Busen das Herz zu
heil'gem Beben mir traf!" The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): her
plea on horns and violins over violas and cellos, the death-announcement's heavy chords on trombones and tuba,
the great swell on doubled violins and clarinets over horns and the low strings. The stage is heard too: the last
of the storm's wind sighs away, each gold glint toward him is a harp note, a gong opens the memory of Siegmund's
death and every wash of indigo is a muffled timpani stroke, and a cymbal swell, cymbals and drum carry the blaze. Throughout, the effects stay well back: the scene is her
plea, and her music must be clear.

Her plea: every long note a pulse of her silver that swells out across the porch and onto the wings, every
quick note below it a gold glint running from her toward him, and her light breathes with the music. Then the
memory of Siegmund: each heavy chord a wash of indigo over the whole roof, and a ghost of Siegmund's blue on
Right where his story began; Wotan's light shrinks under it. As she sings of the hero's love a warm rose-gold
breathes across the house, she rises and moves toward him, a bridge of light grows between them, and on the
climax it blazes in waves out from the two of them, his hard blue softening and her silver warming toward gold.
It settles as her phrase ends, the two lights a hand's breadth apart.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK25'
TITLE = 'Was It So Shameful?'
KIND = 'show'
DESCRIPTION = ('Alone on the rock with her angry father, Brünnhilde pleads her case. She tells him what she saw '
               'in Siegmund\'s heart, and slowly his hard blue light begins to soften.')
VOICEOVER = ('The storm is over. Now it is just a father and his daughter on a mountain, '
             'and she has one chance to make him understand.')

EX = excerpt(__file__)                      # Act III, bars 1032-1040 and 1132-1163, Solti 1958
SING = EX['singing']
D = EX['seconds']
line = lambda w: next(x for x in SING if x[3].startswith(w))
T_PLEA = 0.0                                # "O sag, Vater!"
T_VF = line('Tod kündend')[0]               # the memory of Siegmund's death
T_DEV = line('tönend')[0]                   # his lament, his love: devotion
T_CODA = line('traurigsten')[0]             # the great swell
T_END = line('zu heil')[0]                  # settling
T0 = 80.0 * 24                              # the opera's clock at our start: steady motion carries across the cuts

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
FATE = hexc('#2a1a5a')
FATE_HI = hexc('#5a30d0')
ROSE = hexc('#ff5a8a')
CLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
ROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def onsets(notes, win=0.06):
    """Chords: (time, weight) where weight is the summed velocity of the notes struck together."""
    out = []
    for t, d, m, v, h in notes:
        if out and t - out[-1][0] < win:
            out[-1][1] += v / 127
        else:
            out.append([t, v / 127])
    return np.array(out)


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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). Before the memory of Siegmund
    the right hand's long notes are her plea ('plea'), the rest 'bed'; then 'vf' (the death-announcement), 'dev'
    (devotion) and 'swell' (the climax and its close). Silent markers (velocity 0): 'pick' (a glint toward him) on
    quick left-hand notes of the plea, 'chord' on the heavy chords of the memory, 'surge' on the climax's accents."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_VF:
            part = 'plea' if h == 0 and d >= 0.6 else 'bed'
        elif t < T_DEV:
            part = 'vf'
        elif t < T_CODA:
            part = 'dev'
        else:
            part = 'swell'
        N.append((t, d, m, v, part, h))
    last = -9.0
    for t, d, m, v, h in EX['notes']:
        if t < T_VF and h == 1 and d < 0.6 and t - last > 0.35:
            N.append((t, 0.3, m, 0, 'pick', None))
            last = t
    ons = onsets(EX['notes'])
    med = np.median(ons[:, 1])
    for t, w in ons:
        if T_VF <= t < T_DEV and w > med:
            N.append((float(t), 1.0, 40, 0, 'chord', None))
        if T_CODA <= t < T_END and w > 1.3 * med:
            N.append((float(t), 1.0, 60, 0, 'surge', None))
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
    """Per frame: where Wotan and Brünnhilde are (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    tgt = {k: np.zeros(F) for k in 'wb'}
    rate = {k: np.full(F, 2.0) for k in 'wb'}

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where if np.ndim(where) == 0 else where[m]
        rate[k][m] = r

    set_('w', 0, D, at(G, 'Porch Front', 0.3), 2.0)
    set_('w', T_DEV + 4, D, at(G, 'Porch Front', 0.36), 0.5)
    set_('b', 0, D, at(G, 'Porch Front', 0.55), 2.0)
    set_('b', T_PLEA + 6, T_VF, at(G, 'Porch Front', 0.52), 0.6)
    set_('b', T_VF, T_DEV, at(G, 'Porch Front', 0.54), 0.5)
    set_('b', T_DEV, D, at(G, 'Porch Front', 0.47), 0.4)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    sig = d[G.seg['Right']].min() + 0.35 * (d[G.seg['Right']].max() - d[G.seg['Right']].min())
    tw = Flicker(np.random.default_rng(2501), G.N, 1.5, 5.0)
    plea = sorted({(e[0], e[1]) for e in N if e[4] == 'plea'})
    pt = np.array(sorted({e[0] for e in N if e[3] > 0 and e[5] == 0}))
    longs = [p[0] for p in plea]
    picks = [e[0] for e in N if e[4] == 'pick']
    vch = np.array([e[0] for e in N if e[4] == 'chord'])
    dev = np.array(sorted({e[0] for e in N if e[4] in ('dev', 'swell') and e[3] > 0}))
    surge = [e[0] for e in N if e[4] == 'surge']
    peaks = sorted(plea, key=lambda p: -p[1])[:2]
    peaks = [p[0] for p in peaks]
    ons = onsets(EX['notes'])                                                   # the music's loudness, 0..1
    env = np.zeros(F)
    for t0, w in ons:
        f0 = int(t0 / DT)
        n = min(F - f0, nframes(2.0))
        env[f0:f0 + n] += w * np.exp(-np.arange(n) * DT / 0.6)
    env = np.clip(env / np.percentile(env, 95), 0, 1.2)

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        fate = smoothstep(T_VF - 1, T_VF + 1, t) * (1 - smoothstep(T_DEV - 3, T_DEV, t))
        devo = smoothstep(T_DEV - 1, T_DEV + 4, t)
        warmth = 0.15 * smoothstep(T_PLEA, T_VF, t) + 0.45 * smoothstep(T_DEV, T_CODA, t)
        lvl = 0.5 + 0.2 * smoothstep(T_PLEA, T_PLEA + 8, t) + 0.15 * devo - 0.1 * fate + 0.2 * env[f]
        soft = 0.55 * smoothstep(T_DEV + 2, T_END, t)
        peak = smoothstep(T_CODA, T_CODA + 3, t) * (1 - smoothstep(T_END, D - 1, t))

        # her plea: long notes swell silver out over the house, pickups ripple gold toward him
        for ts in longs:
            if ts <= t < ts + 3.0:
                age = t - ts
                r = 700 * smoothstep(0, 2.2, age) + 1500 * any(abs(ts - p) < 0.05 for p in peaks) * smoothstep(0, 2.2, age)
                band = np.exp(-((np.abs(d - pb) - r) / 220) ** 2) * (1 - age / 3.0)
                fr += light(mix(SILVER, WARM, warmth), 0.7 * band)
        for ts in picks:
            if ts <= t < ts + 1.2:
                age = t - ts
                q = pb + (pw - pb) * min(1.0, age / 0.9)
                fr += light(GLINT, 0.7 * (1 - age / 1.2) * np.exp(-((d - q) / 14) ** 2))
        if devo > 0:                                    # devotion: rose-gold breathing out from the two of them
            mid = 0.5 * (pw + pb)
            dp = recent(dev, t, 1.2, 6.0)
            br = 0.55 + 0.45 * np.sin(2 * np.pi * (np.abs(d - mid) / 700 - 0.11 * ta))
            fall = 1 - 0.35 * smoothstep(T_END, D, t)
            fr *= 1 - 0.45 * devo * fall
            fr += light(ROSE, devo * fall * (0.25 + 0.16 * dp + 0.25 * env[f]) * br)
            fr += light(GLINT, devo * fall * (0.2 + 0.2 * dp + 0.2 * peak) * br ** 3 * (0.7 + 0.3 * tw(ta)))
        for ts in surge:                                # the climax: blazing waves out from the two of them
            if ts <= t < ts + 2.0:
                age = t - ts
                r = 30 + 1200 * smoothstep(0, 1.8, age)
                mid = 0.5 * (pw + pb)
                fr += light(mix(ROSE, GLINT, 0.5), 0.75 * (1 - age / 2.0) * np.exp(-((np.abs(d - mid) - r) / 160) ** 2))

        # the destiny of the Volsungs: indigo over everything, and Siegmund's ghost on Right
        vp = recent(vch, t, 0.6)
        if fate > 0:
            fr *= 1 - 0.5 * fate
            i = int(np.searchsorted(vch, t, side='right')) - 1
            wave = 0.0
            if i >= 0 and t - vch[i] < 1.6:
                age = t - vch[i]
                wave = np.exp(-((np.abs(d - pw) - 1500 * age / 1.6) / 220) ** 2) * (1 - age / 1.6)
            tex = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 260 + 0.04 * ta)) * np.sin(2 * np.pi * (d / 610 - 0.03 * ta))
            fr += light(FATE_HI, fate * (0.22 * tex + 0.3 * vp * tex + 0.6 * wave))
            fr += light(SIEGMUND, fate * (0.35 + 0.3 * vp) * np.exp(-((d - sig) / 40) ** 2))

        # the bridge between them
        lo, hi = min(pw, pb), max(pw, pb)
        bridge = ((d > lo) & (d < hi)) * devo * (0.25 + 0.15 * np.sin(2 * np.pi * (d / 40 - 0.6 * ta)))
        fr += light(mix(WOTAN_SOFT, WARM, 0.5), bridge)

        # Wotan
        wl = 0.85 - 0.2 * fate
        wc = mix(WOTAN, WOTAN_SOFT, soft)
        fr += light(wc, wl * np.exp(-((d - pw) / 24) ** 2) + (0.3 + 0.1 * soft) * np.exp(-((d - pw) / (90 + 40 * soft)) ** 2))

        # Brünnhilde: silver, warming, flaring with each of her notes; gold glints round her
        fl = recent(pt, t, 0.35)
        bc = mix(SILVER, WARM, warmth)
        fr += light(bc, (lvl + 0.2 * fl) * np.exp(-((d - pb) / (20 + 6 * fl)) ** 2)
                    + (0.22 + 0.1 * devo) * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.05 + 0.08 * devo) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, (0.25 + 0.35 * devo + 0.3 * fl) * gl)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: her plea on horns and violins over violas and cellos,
    the memory of Siegmund's death on trombones and tuba, the swell on doubled violins and clarinets over horns."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    sig = pan_at(at(G, 'Right', 0.35))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    o = Orchestra(M, level=LEVEL)
    for t, d, m, v, part, h in compose():
        if part == 'pick':                                                 # a gold glint running toward him
            o.play('harp', m + 12, t, 0.3, 76, pan_of('b', t), 0.25)
            continue
        if part == 'chord':                                                # each wash of indigo: a muffled stroke
            o.hit('timpani', t, 92, pitch=-7, gain=0.45, pan=pf, fx=True)
            continue
        if part == 'surge':                                                # the blaze: cymbal and drum
            o.hit('crash', t, 90, gain=0.22, pan=pf)
            o.hit('bass drum', t, 96, gain=0.3, pan=pf)
            continue
        if v == 0:
            continue
        pb, pw = pan_of('b', t), pan_of('w', t)
        if part == 'plea':
            o.play('horns', m, t, d, v + 6, pb, 0.9)
            o.play('violins', m, t, d, v - 10, pb, 0.4)
        elif part == 'bed':
            if h == 0:
                o.play('violins', m, t, d, v - 4, pb, 0.55)
            elif m >= 48:
                o.play('violas' if m >= 55 else 'cellos', m, t, d, v - 2, pf, 0.6)
            else:
                o.play('cellos', m, t, d, v, pf, 0.6)
                o.play('basses', m, t, d, v - 8, pf, 0.4)
        elif part == 'vf':
            if h == 1 and d >= 0.4:
                o.play('trombones', m, t, d, v + 4, pf, 0.75)
                o.play('tuba' if m < 48 else 'horns', m, t, d, v - 4, pw, 0.55)
                if m < 50:
                    o.play('cellos', m, t, d, v - 10, sig, 0.45)
            elif h == 1:
                o.play('cellos', m, t, d, v, pf, 0.55)
            else:
                o.play('violins', m, t, d, v - 4, pb, 0.55)
                o.play('clarinets', m - 12, t, d, v - 14, pw, 0.35)
        else:
            if h == 0:
                o.play('violins', m, t, d, v, pb - 0.1, 0.65)
                o.play('violins', m, t, d, v - 8, pb + 0.15, 0.4)
                if d >= 0.4:
                    o.play('clarinets', m - 12, t, d, v - 12, pw, 0.45)
            elif m >= 50:
                if d >= 0.4:
                    o.play('horns', m, t, d, v - 2, pw, 0.6 + 0.2 * (part == 'swell'))
                else:
                    o.play('violas', m, t, d, v - 4, pf, 0.5)
            else:
                o.play('cellos', m, t, d, v, pf, 0.65)
                o.play('basses', m, t, d, v - 8, pf, 0.45)
                if part == 'swell' and d >= 0.6:
                    o.play('tuba', m, t, d, v - 12, pf, 0.35)
    o.hit('timpani roll', T_CODA - 1.0, 84, gain=0.35, pan=pf)
    # the stage: the last of the storm's wind sighing away over the wings; a gong under the memory of his death
    o.wind(0.0, T_DEV + 4.0, level=lambda tt: 0.35 * (1 - smoothstep(T_VF, T_DEV + 3.0, tt)), pan=-0.3)
    o.hit('gong', T_VF, 90, gain=0.4, pan=sig, fx=True)
    o.hit('cymbal swell', T_CODA - 2.5, 96, gain=0.4, pan=pf)
    # the fader: this is her plea; the effects stay far back, a breath of wind and no more
    o.effects([(0.0, -6), (3.0, -14), (D, -14)])


LEVEL = 2.4
