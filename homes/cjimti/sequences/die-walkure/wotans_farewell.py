"""Wotan's Farewell: "Leb wohl, du kühnes, herrliches Kind!" The orchestra blazes up and the house flares blue and
silver: Wotan takes his daughter in his arms for the last time.

The music is Wagner's own: Act III, bars 1492 to 1530, as Solti's 1958 Vienna Philharmonic recording takes it, from
the great orchestral climax before the farewell, through "Leb wohl", the three cries of "Leb wohl! Leb wohl! Leb
wohl!" over the falling bass, the tender "Muß ich dich meiden" and the second surge ("noch Met beim Mahl"), to the
hush before "du lachende Lust meines Auges". The notes come from the Wagner Ring Dataset's piano reduction of the
score (pixelhome/ring.py), orchestrated by hand and register: the right hand's soaring octaves on violins with
flutes and piccolo on top, the left hand's harmony on horns, trombones and, at the climaxes, trumpets, the bass on
cellos, basses and tuba, the timpani and cymbals on the loudest bass accents. Over it the stage adds what the
house shows: the wind on the mountain top, a cymbal swell rising into each flare and a crash, gong and drum as it
breaks, a timpani roll under each wave of blue, and a glint of glockenspiel and triangle on each white flash. Here
the music leads: the effects stay well back throughout, lifting a little only with the flares and the climaxes, and
all but vanishing under "Muß ich dich meiden" and the hush.

The lights follow the real notes. While the orchestra blazes the whole house surges with his blue and her silver,
and every loud high note of the violins flashes the roof silver-white. "Leb wohl!" is one flare across the house.
Through the farewell every accent of the bass rolls a wave of his deep blue out from the two of them to both ends of
the roofline, the violins' line filling the house as far as it climbs; each "Leb wohl!" of the three is a flare.
Tenderly ("Muß ich dich meiden") his blue folds round her silver and the house breathes slow blue and silver round
them; then the second surge floods the house again, and it sinks back to the two figures holding each other on the
rock at evening.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK27'
TITLE = "Wotan's Farewell"
KIND = 'show'
DESCRIPTION = ('Wotan takes his daughter in his arms for the last time and says goodbye. His deep blue folds '
               'around her silver and the whole house glows with the two of them: the great farewell, the heart '
               'of the whole opera.')
VOICEOVER = ('Farewell, you brave and glorious child. '
             'A father holds his daughter one last time.')

EX = excerpt(__file__)                      # Act III, bars 1492-1530, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
T_LEB = BAR[1497]                           # "Leb wohl, du kühnes, herrliches Kind!"
T_FARE = BAR[1498]                          # the farewell theme, the violins' octaves soaring
T_THREE = BAR[1506]                         # "Leb wohl! Leb wohl! Leb wohl!"
LEBS = [BAR[1506], BAR[1508], BAR[1510]]
T_TENDER = BAR[1512]                        # "Muß ich dich meiden"
T_SURGE = BAR[1519]                         # the second surge, up to "noch Met beim Mahl"
T_PEAK = BAR[1524]
T_HUSH = BAR[1527]
D = EX['seconds']
T0 = 80.0 * 26                              # the opera's clock at our start

WOTAN = hexc('#1a3cff')
WOTAN_SOFT = hexc('#5a78ff')
SILVER = hexc('#f4f8ff')
WARM = hexc('#fff0cc')
GLINT = hexc('#ffd060')
EMBRACE = hexc('#3050ff')
WHITE = hexc('#ffffff')
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


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand). 'bass' is the left hand below
    C3, 'high' the right hand from C#6 up, 'line' the rest of the right hand, 'mid' the rest of the left."""
    N = []
    for t, d, m, v, h in EX['notes']:
        part = ('high' if m >= 85 else 'line') if h == 0 else ('bass' if m < 48 else 'mid')
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


def accents(ts, gap):
    """Onsets at least gap seconds apart."""
    out = []
    for t in sorted(ts):
        if not out or t - out[-1] >= gap:
            out.append(t)
    return out


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
    set_('w', T_LEB, T_TENDER, at(G, 'Porch Front', 0.4), 1.0)
    set_('w', T_TENDER, D, at(G, 'Porch Front', 0.45), 0.45)
    set_('b', 0, D, at(G, 'Porch Front', 0.47), 2.0)
    set_('b', T_TENDER, D, at(G, 'Porch Front', 0.5), 0.45)
    pos = {k: follow(tgt[k], rate[k]) for k in 'wb'}
    pos['t'] = t
    return pos


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    C = choreography(G)
    N = compose()
    E = energy(N, F)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    tw = Flicker(np.random.default_rng(2701), G.N, 1.0, 4.0)
    waves = accents([e[0] for e in N if e[4] == 'bass' and e[3] >= 80 and T_FARE - 0.5 <= e[0] < T_HUSH], 0.9)
    peaks = accents([e[0] for e in N if e[4] == 'high' and e[3] >= 95], 0.45)
    line = sorted((e[0], e[2]) for e in N if e[4] in ('line', 'high'))
    lt = np.array([x[0] for x in line])
    lm = np.array([x[1] for x in line])
    onsets = np.array(sorted({round(e[0], 2) for e in N}))
    flares = [T_LEB] + LEBS + [T_PEAK]

    def recent(ts, t, tau, span=3.0):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return float(np.exp(-(t - ts[i]) / tau)) if i >= 0 and t - ts[i] < span else 0.0

    for f in range(F):
        t = f * DT
        ta = t + T0
        e = E[f]
        fr = stage(d, ta, porch)
        pw, pb = C['w'][f], C['b'][f]
        mid = 0.5 * (pw + pb)
        dm = np.abs(d - mid)
        hit = recent(onsets, t, 0.18, 1.0)

        # the embrace: his blue over the whole house, as wide and bright as the orchestra is loud
        hush = smoothstep(T_HUSH - 1, D - 1, t)
        wide = 500 + 1500 * e * (1 - 0.5 * hush)
        g = np.exp(-(dm / wide) ** 2)
        emb = (0.2 + 0.6 * e) * (1 - 0.4 * hush)
        fr *= (1 - 0.45 * emb * g)[:, None]
        wv = 0.6 + 0.4 * np.sin(2 * np.pi * (d / 300 - (0.2 + 0.4 * e) * ta))
        fr += light(EMBRACE, emb * (0.5 + 0.15 * hit) * g * wv)
        fr += light(SILVER, emb * 0.35 * np.exp(-(dm / (70 + 200 * e)) ** 2))

        # the opening blaze: silver surging out and back across the house with the chords
        blaze = 1 - smoothstep(T_LEB - 1, T_LEB + 2, t)
        if blaze > 0:
            r = 1700 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.2 - np.pi / 2))
            fill = smoothstep(r + 250, r - 250, dm)
            fr += light(SILVER, blaze * e * (0.35 + 0.3 * hit) * fill) + light(WOTAN, blaze * e * 0.5 * (1 - fill))

        # "Leb wohl!" (and each of the three, and the peak of the second surge): a flare across the house
        for tf in flares:
            if tf <= t < tf + 3:
                a = 0.6 * np.exp(-(t - tf) / 0.35) + 0.4 * np.exp(-(t - tf) / 1.2)
                fr += light(EMBRACE, 0.85 * a * np.ones(G.N)) + light(SILVER, 0.75 * a * np.exp(-(dm / 600) ** 2))

        # the bass: each accent a wave of deep blue rolling out to both ends
        for ts in waves:
            if ts <= t < ts + 3.0:
                age = t - ts
                r = 1600 * smoothstep(0, 2.6, age)
                band = np.exp(-((dm - r) / 180) ** 2) * (1 - age / 3.0)
                fr += light(WOTAN, 0.8 * band) + light(WOTAN_SOFT, 0.3 * band ** 2)

        # the violins' line: the glow fills the house as far as the line climbs
        sing = smoothstep(T_FARE - 1, T_FARE + 1, t) * (1 - smoothstep(T_TENDER - 1, T_TENDER + 2, t)) \
            + smoothstep(T_SURGE - 1, T_SURGE + 2, t) * (1 - smoothstep(T_HUSH - 1, T_HUSH + 2, t))
        if sing > 0 and len(lt):
            i = max(int(np.searchsorted(lt, t, side='right')) - 1, 0)
            reach = 250 + 1500 * np.clip((lm[max(0, i - 6):i + 1].max() - 64) / (88 - 64), 0, 1)
            fill = smoothstep(reach + 200, reach - 200, dm)
            sw = 0.6 + 0.4 * np.sin(2 * np.pi * (dm / 500 - 0.35 * ta))
            fr *= (1 - 0.4 * sing * fill)[:, None]
            fr += light(SILVER, sing * (0.3 + 0.35 * e) * sw ** 2 * fill) + light(EMBRACE, sing * 0.55 * (1 - sw ** 2) * fill)
            fr += light(GLINT, sing * 0.5 * (rng.random(G.N) < 0.04 + 0.04 * e) * fill)
        for ts in peaks:
            if ts <= t < ts + 1.2:
                a = np.exp(-(t - ts) / 0.25)
                fr += light(WHITE, 0.8 * a * np.exp(-(dm / 900) ** 2)) + light(SILVER, 0.4 * np.exp(-(t - ts) / 0.7) * np.ones(G.N))

        # tender: the house breathing slow blue and silver round them
        tender = smoothstep(T_TENDER - 1, T_TENDER + 2, t) * (1 - smoothstep(T_SURGE, T_SURGE + 4, t)) + 0.8 * hush
        if tender > 0:
            br = 0.5 + 0.5 * np.sin(2 * np.pi * (dm / 900 - 0.09 * ta))
            fr += light(mix(SILVER, WARM, 0.4), tender * (0.26 + 0.15 * hit) * br ** 2 * (1 - 0.4 * porch))
            fr += light(WOTAN, tender * 0.6 * (1 - br) * (0.6 + 0.4 * tw(ta)))

        # Wotan and Brünnhilde
        wc = mix(WOTAN, WOTAN_SOFT, 0.75)
        fr += light(wc, (0.85 + 0.15 * hit) * np.exp(-((d - pw) / (24 + 10 * hit)) ** 2) + 0.375 * np.exp(-((d - pw) / 120) ** 2))
        bc = mix(SILVER, WARM, 0.7)
        fr += light(bc, 0.85 * np.exp(-((d - pb) / 20) ** 2) + 0.32 * np.exp(-((d - pb) / 80) ** 2))
        gl = (rng.random(G.N) < 0.09) * np.exp(-((d - pb) / 40) ** 2)
        fr += light(GLINT, 0.45 * gl)
        out[f] = fr
    return np.clip(out, 0, 1)


def house_pan(G):
    """Path distance -> left/right across the facade, as heard from the street."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    return lambda dd: float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; fullest in the two climaxes. Over it, what the house
    shows: the mountain wind round the rock, a cymbal swell rising into every flare and a crash, gong and drum as it
    breaks, a rolling timpani under each wave of blue, and a glint of glockenspiel and triangle on each white flash."""
    o = Orchestra(M, level=2.3)
    pan_at = house_pan(G)
    C = choreography(G)
    N = compose()
    mid = lambda t: pan_at(0.5 * (np.interp(t, C['t'], C['w']) + np.interp(t, C['t'], C['b'])))
    big = lambda t: t < T_LEB + 1 or T_THREE <= t < T_TENDER or T_PEAK - 2 <= t < T_HUSH
    o.tutti(EX['notes'], size=lambda t: 1.0 if big(t) else 0.3 if T_TENDER <= t < T_SURGE or t >= T_HUSH else 0.65)
    for t, d, m, v, part, h in N:
        if part == 'bass' and v >= 110 and big(t):
            o.hit('timpani', t, v - 10, pitch=(m - 40) * 0.5, gain=0.45)
    for t in (BAR[1495], T_LEB, T_PEAK):
        o.hit('crash', t, 110, gain=0.45)
    o.hit('cymbal swell', BAR[1494] - 1.5, 90, gain=0.35)

    # the Farewell's music must be clear: the wind stays well back, lifting a little into the opening blaze and
    # the second surge, almost gone under "Muß ich dich meiden" and in the hush
    o.effects([(0, -8), (T_LEB + 1, -8), (T_FARE, -14), (T_TENDER, -18), (T_SURGE, -14), (T_PEAK, -10),
               (T_HUSH, -18), (D, -20)])
    # the wind on the mountain top, gusting harder in the climaxes, dying to a breath in the hush
    o.wind(0, D, level=lambda tt: 0.45 + 0.35 * np.array([big(x) for x in tt]) - 0.25 * smoothstep(T_HUSH, D, tt),
           pan=-0.3)
    # every flare: a swell rising into it, then crash, gong and drum where the two of them stand
    for k, tf in enumerate([T_LEB] + LEBS + [T_PEAK]):
        o.hit('cymbal swell', tf - 2.2, 90, gain=0.3, pan=mid(tf))
        o.hit('crash', tf, 108, gain=0.35, pan=mid(tf))
        o.hit('gong', tf + 0.02, 96 + 4 * k, gain=0.25)
        o.hit('bass drum', tf, 110, gain=0.4)
    # the waves of blue rolling out to both ends: a timpani roll each
    waves = accents([e[0] for e in N if e[4] == 'bass' and e[3] >= 80 and T_FARE - 0.5 <= e[0] < T_HUSH], 0.9)
    for ts in waves:
        o.hit('timpani roll', ts, 74, pitch=-3, gain=0.22, pan=mid(ts))
    # the white flashes: a glint of glockenspiel and triangle
    tri = M.hits('Percussion/Triangle3-Hit_v2*.wav')
    for ts in accents([e[0] for e in N if e[4] == 'high' and e[3] >= 95], 0.45):
        o.play('glock', 84, ts, 0.3, 90, mid(ts) + 0.3, 0.3)
        M.add('perc', tri.play(90), ts, 0.3, mid(ts) - 0.3)
