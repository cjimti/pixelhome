"""A Wall of Fire: the rose-gold glow of her devotion still hangs over the rock as Brünnhilde makes her last
request. If she must sleep defenceless on the mountain for any man who finds her, then let terror guard her:
let fire ring the rock, so that only a hero who knows no fear can pass.

The music is Wagner's own: Act III, bars 1446 to 1488, as Solti's 1958 Vienna Philharmonic recording takes them.
Wotan refuses ("Zuviel begehrst du, zu viel der Gunst!"); she insists ("Dies eine mußt du gewähren!"), offers
herself to his spear rather than to shame, and then asks for the fire: "Auf dein Gebot entbrenne ein Feuer; den
Felsen umglühe lodernde Glut; es leck' ihre Zung', es fresse ihr Zahn den Zagen, der frech sich wagte dem
freislichen Felsen zu nahn!" The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py):
his refusal in trombones and tuba over the low strings, her plea in violins with horns under its long notes,
and the fire's flickering figures on harp, violins and piccolo over horns and cellos. The stage is heard too: his
refusal thuds, her accents ring like bells; then the fire catches with a whoomph and a boom, roars and crackles
round the rock, flares with a rush at whichever porch corner leaps on each flicker, rushes out along both wings
with their own roaring, and sinks to crackling embers. The effects back off for his refusal and her plea, lead as
the fire catches and rings the rock, then sit under the music, rising once as it licks out along the wings.

His refusal is a slow wave of hard blue rolling out from him on every heavy chord. Her plea: every long note a
pulse of her silver swelling out over the house, every accent a ring of it with gold glints flying toward him.
Then the fire she asks for answers her words: flames leap up at the corners of the porch on every flicker of
the music, ring the whole rock, lick out along the wings to the ends of the house to devour the coward, and sink
back to a glowing ring of embers round the rock as her phrase ends.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, colormap
from pixelhome.audio import whoosh
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK26'
TITLE = 'A Wall of Fire'
KIND = 'show'
DESCRIPTION = ('Brünnhilde makes one last request: if she must sleep on the mountain, let a wall of fire guard '
               'her, so that only a true hero can ever reach her. As she sings of it, the fire leaps up around '
               'the whole house.')
VOICEOVER = ('If she must sleep, she will not sleep unguarded. '
             'Listen to what she asks her father for: a wall of fire.')

EX = excerpt(__file__)                      # Act III, bars 1446-1488, Solti 1958
SING = EX['singing']
D = EX['seconds']
line = lambda w: next(x for x in SING if x[3].startswith(w))
T_NO = line('Zuviel')[0]                    # Wotan refuses
T_PLEA = line('Dies eine')[0]               # she insists
T_FIRE = line('Auf dein Gebot')[0]          # the fire
T_RING = line('den Felsen')[0]              # it rings the rock
T_LICK = line('es leck')[0]                 # it licks out to the ends of the house
T_LAST = line('dem freislichen')[0]         # and sinks back
T0 = 80.0 * 25                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
HERO = hexc('#fff0a0')
ROSE = hexc('#ff5a8a')
EMBRACE = hexc('#3050ff')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
CLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
ROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')


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
    """Flame heat along the roofline (about 0..1): tongues running both ways at different speeds."""
    return (0.5 + 0.22 * np.sin(2 * np.pi * (d / 97 - 1.9 * ta)) + 0.18 * np.sin(2 * np.pi * (d / 53 + 2.7 * ta) + 1.3)
            + 0.1 * np.sin(2 * np.pi * (d / 31 - 4.3 * ta) + 2.1))


def onsets(notes, win=0.06):
    """Chords: (time, weight) where weight is the summed velocity of the notes struck together."""
    out = []
    for t, d, m, v, h in notes:
        if out and t - out[-1][0] < win:
            out[-1][1] += v / 127
        else:
            out.append([t, v / 127])
    return np.array(out)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand): 'no' (his refusal), 'plea'
    (her plea; the right hand's long notes are 'long'), 'flick' (the fire's high figures, right hand from E5) and
    'fire' (the rest of the fire). Silent markers (velocity 0): 'chord' on his heavy chords, 'accent' on hers."""
    N = []
    for t, d, m, v, h in EX['notes']:
        if t < T_PLEA:
            part = 'no'
        elif t < T_FIRE - 1.0:
            part = 'long' if h == 0 and d >= 0.4 else 'plea'
        else:
            part = 'flick' if h == 0 and m >= 76 else 'fire'
        N.append((t, d, m, v, part, h))
    ons = onsets(EX['notes'])
    med = np.median(ons[:, 1])
    last = -9.0
    for t, w in ons:
        if t < T_PLEA and w > med and t - last > 0.8:
            N.append((float(t), 3.0, 40, 0, 'chord', None))
            last = t
        elif T_PLEA <= t < T_FIRE - 1.0 and w > 1.2 * med and t - last > 0.6:
            N.append((float(t), 1.0, 70, 0, 'accent', None))
            last = t
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

    set_('w', 0, D, at(G, 'Porch Front', 0.36), 2.0)
    set_('b', 0, D, at(G, 'Porch Front', 0.47), 2.0)
    set_('b', T_PLEA, T_FIRE, at(G, 'Porch Front', 0.42), 0.8)                # pressing close to him
    set_('b', T_FIRE, D, at(G, 'Porch Front', 0.5), 0.5)                      # turning to the fire
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    corners = np.array([d[G.path[i]] for i in (179, 260, 331, 380)])
    dc = np.min(np.abs(d[:, None] - corners[None, :]), axis=1)                 # distance to the nearest porch corner
    p0, p1 = d[G.seg['Porch Left']].min(), d[G.seg['Porch Right']].max()
    tw = Flicker(np.random.default_rng(2501), G.N, 1.5, 5.0)            # shared with WK25
    fl = Flicker(np.random.default_rng(2601), G.N, 4.0, 11.0)
    chords = [e[0] for e in N if e[4] == 'chord']
    accents = [e[0] for e in N if e[4] == 'accent']
    longs = sorted({e[0] for e in N if e[4] == 'long'})
    flick = np.array(sorted({e[0] for e in N if e[4] == 'flick'}))
    ons = onsets(EX['notes'])                                                   # the music's loudness, 0..1
    env = np.zeros(F)
    for t0, w in ons:
        f0 = int(t0 / DT)
        n = min(F - f0, nframes(1.5))
        env[f0:f0 + n] += w * np.exp(-np.arange(n) * DT / 0.4)
    env = np.clip(env / np.percentile(env, 95), 0, 1.2)
    cflash = rng.integers(0, 4, len(flick))

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        devo = 1 - smoothstep(0, 8, t)                    # the devotion glow from WK25, fading
        mid = 0.5 * (pw + pb)
        if devo > 0:
            br = 0.55 + 0.45 * np.sin(2 * np.pi * (np.abs(d - mid) / 700 - 0.11 * ta))
            fr *= 1 - 0.45 * 0.65 * devo
            fr += light(ROSE, 0.65 * devo * 0.3 * br)
            fr += light(GLINT, 0.65 * devo * 0.2 * br ** 3 * (0.7 + 0.3 * tw(ta)))

        # his refusal: slow waves of hard blue rolling out from him
        for tc in chords:
            if tc <= t < tc + 3.0:
                age = t - tc
                r = 40 + 900 * smoothstep(0, 2.6, age)
                fr += light(WOTAN, 0.8 * (1 - age / 3.0) * np.exp(-((np.abs(d - pw) - r) / 150) ** 2))

        # her plea: long notes swell silver out over the house, accents ring out with gold glints toward him
        for ts in longs:
            if ts <= t < ts + 2.5:
                age = t - ts
                r = 800 * smoothstep(0, 2.0, age)
                fr += light(SILVER, 0.5 * (1 - age / 2.5) * np.exp(-((np.abs(d - pb) - r) / 200) ** 2))
        for ts in accents:
            if ts <= t < ts + 1.4:
                age = t - ts
                r = 20 + 600 * age ** 0.7
                fr += light(WARM, 0.7 * (1 - age / 1.4) * np.exp(-((np.abs(d - pb) - r) / 40) ** 2))
                q = pb + (pw - pb) * min(1.0, age / 0.8)
                fr += light(GLINT, 0.8 * (1 - age / 1.4) * np.exp(-((d - q) / 12) ** 2))

        # the fire: leaping at the corners of the porch on every flicker, ringing the rock, licking out along the
        # wings to the ends of the house, sinking back to embers round the rock
        grow = smoothstep(T_FIRE - 1, T_RING, t)
        reach = (60 + 140 * smoothstep(T_FIRE, T_RING, t) + 260 * smoothstep(T_RING, T_LICK, t))
        out_ = smoothstep(T_LICK - 1, T_LICK + 6, t) * (1 - smoothstep(T_LAST - 2, D - 1.0, t))
        if grow > 0:
            hh = heat(d, ta)
            q = np.clip(hh + 0.12 * fl(ta) - 0.1 + 0.25 * env[f], 0, 1)
            rock = smoothstep(reach + 60, reach - 60, dc) * porch
            wing_out = np.where(d < p0, p0 - d, np.where(d > p1, d - p1, 0.0))
            span = 1400 * out_
            licks = (1 - porch) * smoothstep(span + 80, span - 80, wing_out) * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 150 + 1.3 * ta)))
            embers = 0.35 * smoothstep(T_LAST - 2, D - 1, t)
            amt = grow * (0.75 + 0.4 * env[f]) * np.maximum(rock * (1 - embers), licks)
            fr = fr * (1 - 0.6 * np.clip(amt, 0, 1))[:, None] + light(FIRE(q * (1 - 0.4 * embers)), amt * (0.6 + 0.8 * q))
            i = int(np.searchsorted(flick, t, side='right')) - 1                 # each flicker: a flame leaping up
            if i >= 0 and t - flick[i] < 0.7:
                age = t - flick[i]
                c = corners[cflash[i]]
                tongue = np.exp(-((d - c) / (40 + 200 * age)) ** 2) * (1 - age / 0.7)
                fr += light(FIRE(np.clip(q + 0.35, 0, 1)), 1.0 * grow * tongue)

        # Wotan
        wc = mix(WOTAN, WOTAN_SOFT, 0.55 + 0.25 * smoothstep(T_FIRE, D, t))
        wl = 0.85 + 0.25 * recent(np.array(chords), t, 0.4)
        fr += light(wc, wl * np.exp(-((d - pw) / 24) ** 2) + 0.4 * np.exp(-((d - pw) / 110) ** 2))

        # Brünnhilde: flaring with her plea, warm in the firelight
        bf = recent(np.array(accents), t, 0.3)
        bc = mix(SILVER, WARM, 0.6 + 0.3 * grow)
        fr += light(bc, (0.85 + 0.25 * bf) * np.exp(-((d - pb) / 20) ** 2) + 0.32 * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.1) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, 0.5 * gl)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: his refusal in trombones and tuba, her plea in violins
    with horns under its long notes, the fire's flickering figures on harp, violins and piccolo over horns."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))
    pl, pr = pan_at(at(G, 'Porch Left', 0.9)), pan_at(at(G, 'Porch Right', 0.1))

    def pan_of(who, t):
        return pan_at(np.interp(t, C['t'], C[who]))

    o = Orchestra(M, level=LEVEL)
    k = 0
    for t, d, m, v, part, h in compose():
        if v == 0:
            continue
        pw, pb = pan_of('w', t), pan_of('b', t)
        if part == 'no':
            if h == 1 and m < 52:
                o.play('cellos', m, t, d, v, pw, 0.7)
                o.play('basses', m, t, d, v - 8, pw, 0.5)
                if d >= 0.4:
                    o.play('tuba', m, t, d, v - 6, pw, 0.5)
            elif h == 1:
                o.play('trombones', m, t, d, v, pw, 0.7)
                o.play('horns', m, t, d, v - 10, pw, 0.4)
            else:
                o.play('violins', m, t, d, v - 6, pw, 0.5)
        elif part == 'long':
            o.play('violins', m, t, d, v, pb, 0.65)
            o.play('horns', m - 12, t, d, v - 6, pb, 0.6)
        elif part == 'plea':
            if h == 0:
                o.play('violins', m, t, d, v - 4, pb, 0.55)
            elif m >= 52:
                o.play('violas' if d < 0.3 else 'horns', m, t, d, v - 4, pf, 0.55)
            else:
                o.play('cellos', m, t, d, v, pf, 0.65)
                o.play('basses', m, t, d, v - 8, pf, 0.45)
        elif part == 'flick':
            side = (pl, pr)[k % 2]
            k += 1
            o.play('harp', m, t, d, v, side, 0.8)
            o.play('violins', m, t, d, v - 8, -side, 0.5)
            if m >= 84:
                o.play('piccolo', m, t, 0.1, v - 14, side, 0.35)
        else:
            if h == 0:
                o.play('violins', m, t, d, v - 4, pb, 0.55)
                if d >= 0.4:
                    o.play('clarinets', m - 12, t, d, v - 12, pb, 0.4)
            elif m >= 52:
                if d >= 0.3:
                    o.play('horns', m, t, d, v, pf, 0.65)
                    o.play('trombones', m, t, d, v - 10, pf, 0.4)
                else:
                    o.play('violas', m, t, d, v - 4, pf, 0.5)
            else:
                o.play('cellos', m, t, d, v, pf, 0.7)
                o.play('basses', m, t, d, v - 8, pf, 0.5)
                if d >= 0.5:
                    o.play('tuba', m, t, d, v - 12, pf, 0.4)
    o.hit('cymbal swell', T_FIRE - 2.0, 90, gain=0.35, pan=pf)
    o.hit('timpani roll', T_RING - 1.0, 90, gain=0.4, pan=pf)
    # the stage: his refusal thuds, her accents ring; then the fire roars up, flares at the corners, rings the rock,
    # licks out along the wings and sinks to embers
    N = compose()
    pw0 = pan_of('w', 0.0)
    for t in [e[0] for e in N if e[4] == 'chord']:
        o.hit('bass drum', t, 92, gain=0.3, pan=pw0, fx=True)
    for j, t in enumerate(e[0] for e in N if e[4] == 'accent'):
        o.play('glock', (86, 89, 91, 93)[j % 4], t, 0.4, 70, pan_of('b', t), 0.16)
    o.M.add('fx', whoosh(1.6, 90, 900, 0.9, seed=26), T_FIRE - 0.3, 0.9, pf)       # the fire catches: a whoomph
    o.boom(T_FIRE + 0.2, pf, gain=0.7)
    rock = lambda tt: (smoothstep(T_FIRE - 1, T_RING, tt) * (0.6 + 0.4 * smoothstep(T_FIRE, T_RING, tt))
                       * (1 - 0.5 * smoothstep(T_LAST - 2, D - 1.0, tt)))
    wings = lambda tt: (smoothstep(T_LICK - 1, T_LICK + 6, tt) * (1 - smoothstep(T_LAST - 2, D - 1.0, tt)))
    o.fire(T_FIRE - 1.0, D, level=rock, pan=pf, crackle=14, seed=261)
    o.fire(T_LICK - 1.0, D, level=wings, pan=-0.85, crackle=10, seed=262)
    o.fire(T_LICK - 1.0, D, level=wings, pan=0.85, crackle=10, seed=263)
    o.M.add('fx', whoosh(2.5, 200, 2200, 0.8, seed=27), T_LICK - 0.5, 0.5, -0.6)    # licking out along the wings
    o.M.add('fx', whoosh(2.5, 200, 2200, 0.8, seed=28), T_LICK - 0.3, 0.5, 0.6)
    flick = np.array(sorted({e[0] for e in N if e[4] == 'flick'}))
    cflash = np.random.default_rng(26).integers(0, 4, len(flick))              # the same corners render() lights
    cpan = [pan_at(G.pd[G.path[i]]) for i in (179, 260, 331, 380)]
    last = -9.0
    for i, t in enumerate(flick):                                              # each flame leaping at a corner
        if t - last >= 0.25:
            o.M.add('fx', whoosh(0.5, 400, 3000, 0.7, seed=300 + i), t - 0.05, 0.3, cpan[cflash[i]])
            last = t
    # the fader: back off for the refusal and her plea; the fire leads as it catches and rings the rock, then
    # sits under the music, rising once as it licks out along the wings, and sinks with the embers
    o.effects([(0.0, -12), (T_FIRE - 1.5, -12), (T_FIRE - 0.4, 3), (T_RING + 2.0, 1), (T_RING + 5.0, -8),
               (T_LICK - 1.0, -8), (T_LICK + 0.5, -2), (T_LICK + 4.0, -9), (D, -10)])


LEVEL = 1.6
