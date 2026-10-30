"""The Challenge: Hunding has heard enough. "Ich weiss ein wildes Geschlecht": he knows this wild breed, his kinsmen
were out all night hunting the man who killed theirs, and that man is sitting at his fire. His motif (composed)
pounds in the tubas, trombones and timpani; he rises, a flare of blood red in its black halo, and dark red rolls
out from him across the house on every beat until it meets Siegmund's blue at the hearth, the two colours
pressing at a line that pulses between them. Siegmund's motif (Donington 35) answers low in the horns. His house
shelters the guest tonight, says Hunding; tomorrow, with a strong weapon, let him defend himself. Three red and
blue clashes flash on the porch, a glimpse of the fight to come at dawn, and the trumpet, muted, sounds Nothung
(43): the weapon Siegmund does not have.

"Weib, weiche vom Herd!" Sieglinde must make his night drink. She goes to the corner of the porch and mixes it,
and something else goes in with the spices: a slow murky violet swirl and a woozy chromatic line in the bassoon
and clarinet. She carries it across the room and he drinks. Then, on her way out, she stops under the great ash
tree and looks at it, long and meaningfully, at a spot in the trunk: a line of amber light runs from her to the
tree and the gold hilt of the buried sword blazes up while the trumpet plays the Sword motif (45). Siegmund does
not understand. Hunding drives her out: she goes through the inner door at the corner of Left and Side and away
down Side, and Hunding follows, passing close by the stranger with a last flare of his motif, and is gone. Siegmund
is alone at the fire. It sinks to embers, the storm outside the door quiets to almost nothing, the room goes dark
and warm, and only the faint glint of the hilt keeps shining in the tree.

compose() holds every note, choreography() every move; stage(), room() and figure() are the hut and the people
in it, shared word for word by Act I's first scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'WK06'
TITLE = 'The Challenge'
KIND = 'show'
DESCRIPTION = ('Hunding realises his guest is the very man his kinsmen were hunting. Tonight the law protects him; '
               'at dawn they fight. His wife mixes his night drink with something extra, and on her way out she '
               'looks hard at one spot in the trunk of the old ash tree.')
VOICEOVER = ('Hunding knows exactly who his guest is. Tonight, the law protects him. '
             'In the morning, they fight, and the stranger has no weapon.')

K = 5                                       # this scene's place on Act I's shared clock: T = t + 80 K
HBEAT = 0.6                                 # a quarter of Hunding's tread
T_KNOW = [0.6, 5.4]                         # "Ich weiss ein wildes Geschlecht": his motif, twice, loud
T_ANSWER = 10.5                             # Siegmund's motif in the horns
T_DAWN = [16.0, 17.2, 18.4]                 # a glimpse of tomorrow's fight
T_NOTHUNG = 20.0
T_WEIB = 25.0                               # "Weib, weiche vom Herd!"
T_MIX = 29.0                                # the night drink, and the drug in it
T_DRINK = 37.0                              # he drinks
T_LOOK = 42.0                               # she looks at the tree: the Sword motif
T_FORT = 49.0                               # he drives her out
T_ALONE = 63.0
D = 80.0

HUT = hexc('#3a1a0a')
HEARTH = hexc('#ff6a10')
EMBER = hexc('#ff3000')
TRUNK = hexc('#5a3010')
LEAVES = hexc('#50b030')
HILT = hexc('#ffcc40')
STORM = hexc('#5a6a8a')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
HUNDING = hexc('#8a0020')
STEEL = hexc('#e8f8ff')
DRUG = hexc('#6a4a90')
WHITE = hexc('#ffffff')

START = dict(bed=0.18, hearth=0.58, trunk=0.95, leaves=0.6, hilt=0.45, door=0.3)      # where WK05 left the hut
END = dict(bed=0.13, hearth=0.38, trunk=0.7, leaves=0.38, hilt=0.3, door=0.18)        # night: WK07 begins here
SM_START, SM_END = (0.5, 18.0), (0.36, 18.0)                     # Siegmund at Left 0.5: level, width
SL = (0.52, 16.0)                           # Sieglinde, from Left 0.22
HU = (0.66, 20.0)                           # Hunding, from Right 0.3

HUNDING_MOTIF = [(0, 1.5, 'D2'), (1.5, 0.5, 'D2'), (2, 1, 'F2'), (3, 0.75, 'E2'), (3.75, 0.25, 'C#2'),
                 (4, 1.5, 'D2'), (5.5, 0.5, 'A1'), (6, 2, 'D2')]     # composed: the tubas' heavy tread


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Hunding's hut as profiles over the house: the hearth on Left, the ash tree in the middle of Porch Front with
    its leaves over the porch and the sword's hilt in its trunk, the door at the free end of Right."""
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    rng = np.random.default_rng(1874)       # the same fire, leaves and rain in every scene, so the cuts match
    trunk = np.exp(-((d - pf) / 16) ** 2)
    clumps = 0.55 + 0.45 * smooth_noise(rng, d, 45.0)
    return dict(
        d=d, pf=pf,
        hearth=np.exp(-((d - at(G, 'Left', 0.4)) / 125) ** 2),
        trunk=trunk,
        hilt=np.exp(-((d - pf) / 5) ** 2),
        canopy=porch * np.exp(-((d - pf) / 310) ** 2) * clumps * (1 - trunk),
        door=smoothstep(at(G, 'Right', 0.7), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.2),
        stir=Flicker(rng, G.N, 0.08, 0.35),
        rain=Flicker(rng, G.N, 4.0, 11.0),
    )


def room(S, T, lv):
    """The hut at shared time T with levels lv (bed, hearth, trunk, leaves, hilt, door)."""
    fire = S['fire'](T)
    stir = S['stir'](T)
    fr = light(HUT, lv['bed'] * (0.9 + 0.1 * stir))
    fr += light(HEARTH, lv['hearth'] * S['hearth'] * (0.86 + 0.14 * fire))
    fr += light(EMBER, 0.55 * lv['hearth'] * S['hearth'] ** 3 * (0.7 + 0.3 * fire))
    fr += light(TRUNK, lv['trunk'] * S['trunk'])
    fr += light(LEAVES, lv['leaves'] * S['canopy'] * (0.82 + 0.18 * stir))
    fr += light(HILT, lv['hilt'] * S['hilt'] * (0.8 + 0.2 * np.sin(2 * np.pi * 0.45 * T)))
    rain = np.clip(S['rain'](T), 0, None) ** 2 / 3
    fr += light(STORM, lv['door'] * S['door'] * (0.62 + 0.38 * rain))
    return fr


def figure(fr, S, p, col, lvl, w=18.0):
    """A person at path distance p: a body that stands in front of the room, and a soft halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.8 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.4 * lvl * np.exp(-((S['d'] - p) / (3.2 * w)) ** 2))


def brute(fr, S, p, lvl, w=20.0, dark=0.75):
    """Hunding: blood red in black. The room dims round him wherever he stands."""
    halo = np.exp(-((S['d'] - p) / (4.5 * w)) ** 2)
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - dark * min(1.0, lvl / 0.3) * np.maximum(halo, body))[:, None]
    return fr + light(HUNDING, lvl * body) + light(HUNDING, 0.3 * lvl * halo)


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    def hunding(t0, v, k, beat=HBEAT):
        for b, d, m in HUNDING_MOTIF:
            add(t0 + b * beat, d * beat, m, v, 'hunding', k)

    add(0.0, D, 'D1', 64, 'pedal')
    hunding(T_KNOW[0], 116, 0)
    hunding(T_KNOW[1], 124, 1)
    for t, m, v, d in play('siegmund', T_ANSWER, 0.4, 0, 100):
        add(t, d, m, v, 'siegmund')
    for j, tk in enumerate(T_DAWN):
        add(tk, 0.6, 'D2', 108 + 6 * j, 'clash', j)
    for t, m, v, d in play('nothung', T_NOTHUNG, 0.42, -12, 84):
        add(t, d, m, v, 'nothung')
    hunding(T_WEIB, 100, 2)
    for m in ('D3', 'F3', 'Bb3'):
        add(T_WEIB + 4, T_LOOK - T_WEIB - 4, m, 54, 'pad')
    for j in range(16):                     # the drug: a woozy chromatic line
        add(T_MIX + j * 0.45, 0.5, note('A3') - (0, 1, 2, 1, 3, 2, 4, 3)[j % 8] - (j // 8), 66, 'drug')
    add(T_DRINK, 1.2, 'D2', 80, 'gulp')
    for t, m, v, d in play('sword', T_LOOK + 1.0, 0.5, 0, 92):
        add(t, d, m, v, 'sword')
    for m in ('C3', 'E3', 'G3'):
        add(T_LOOK + 1.0, 5.0, m, 70, 'swordpad')
    hunding(T_FORT, 104, 3)
    hunding(T_FORT + 6.0, 92, 4, 0.7)
    for t, m, v, d in play('siegmund_weary', T_ALONE, 0.8, 0, 72):
        add(t, d, m, v, 'weary')
    for m in ('D3', 'A3'):
        add(T_ALONE, D - T_ALONE, m, 52, 'night')
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
    """Per frame: where Sieglinde (0) and Hunding (1) are, and how bright; Siegmund stays at the hearth."""
    F = nframes(D)
    t = np.arange(F) * DT
    inner, hseat = at(G, 'Left', 0.03), at(G, 'Right', 0.3)
    tgt = np.zeros((2, F))
    rate = np.full((2, F), 3.0)

    def set_(k, a, b, where, r):
        m = (t >= a) & (t < b)
        tgt[k][m] = where
        rate[k][m] = r

    set_(0, 0, D, at(G, 'Left', 0.22), 3.0)
    set_(0, T_WEIB + 1.5, T_MIX + 6, at(G, 'Porch Left', 0.25), 1.2)
    set_(0, T_MIX + 6, T_DRINK + 1.5, hseat - 40, 1.3)
    set_(0, T_DRINK + 1.5, T_FORT + 1, at(G, 'Porch Front', 0.32), 1.0)
    set_(0, T_FORT + 1, T_FORT + 5.5, inner, 1.4)
    set_(0, T_FORT + 5.5, D, -60.0, 0.9)
    set_(1, 0, D, hseat, 3.0)
    set_(1, T_KNOW[1], T_WEIB, hseat - 60, 2.0)
    set_(1, T_WEIB, T_FORT + 2, hseat, 1.5)
    set_(1, T_FORT + 2, T_FORT + 8.5, inner + 10, 0.9)
    set_(1, T_FORT + 8.5, D, -60.0, 0.9)
    pos = np.array([follow(tgt[k], rate[k]) for k in range(2)])
    sl = np.array([keys(x, [(T_FORT + 7, SL[0]), (T_FORT + 10.5, 0.0)]) for x in t])
    hu = np.array([keys(x, [(0, HU[0]), (T_KNOW[0], 0.8), (T_WEIB, 0.8), (T_WEIB + 3, HU[0]), (T_DRINK + 1, HU[0]),
                            (T_DRINK + 3, 0.6), (T_FORT + 10, 0.6), (T_FORT + 14, 0.0)]) for x in t])
    sm = np.array([keys(x, [(0, SM_START[0]), (T_ANSWER, SM_START[0]), (T_ANSWER + 1, 0.68), (T_ANSWER + 7, 0.6),
                            (T_WEIB, SM_START[0]), (T_ALONE, SM_START[0]), (D - 2, SM_END[0])]) for x in t])
    return dict(t=t, pos=pos, sl=sl, hu=hu, sm=sm)


def render(G, seed=6):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, pf = S['d'], S['pf']
    C = choreography(G)
    N = compose()
    sm = at(G, 'Left', 0.5)
    stomp = np.array([e[0] for e in N if e[4] == 'hunding'])
    stomp_k = np.array([e[5] for e in N if e[4] == 'hunding'])
    sword_on = np.array([e[0] for e in N if e[4] == 'sword'])
    swirl = Flicker(rng, G.N, 0.6, 2.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        sl, hu = C['pos'][0][f], C['pos'][1][f]
        lv = {k: keys(t, [(0, START[k]), (T_FORT + 6, START[k]), (D - 3, END[k])]) for k in START}
        look = smoothstep(T_LOOK, T_LOOK + 1.0, t) * (1 - smoothstep(T_LOOK + 6, T_FORT + 1, t))
        i = int(np.searchsorted(sword_on, t, side='right')) - 1
        ring = np.exp(-(t - sword_on[i]) / 0.4) if i >= 0 and t - sword_on[i] < 2 else 0.0
        lv['hilt'] += look * (0.5 + 0.4 * ring)
        lv['trunk'] += 0.1 * look
        fr = room(S, T, lv)

        # his motif: dark red rolls across the house on every beat; the first two statements to the hearth
        i = int(np.searchsorted(stomp, t, side='right')) - 1
        if i >= 0 and t - stomp[i] < 2.2:
            a = t - stomp[i]
            big = 1.0 if stomp_k[i] < 2 else 0.55
            r = 30 + 800 * a
            band = np.exp(-((np.abs(d - hu) - r) / 130) ** 2) * np.exp(-a / 0.7) * big
            fr = fr * (1 - 0.6 * band)[:, None] + light(HUNDING, 0.5 * band)
        # the standoff: red floods from Hunding to a line by the hearth where Siegmund's blue holds
        war = smoothstep(T_KNOW[0] + 1, T_KNOW[1], t) * (1 - smoothstep(T_DAWN[-1] + 1, T_WEIB + 1, t))
        if war > 0:
            line = sm + 150 + 40 * smoothstep(T_ANSWER, T_ANSWER + 2, t) - 40 * smoothstep(T_KNOW[1], T_ANSWER, t)
            red = smoothstep(line - 10, line + 60, d) * smoothstep(hu + 200, hu - 50, d)
            blue = smoothstep(line + 10, line - 60, d) * smoothstep(sm - 150, sm, d)
            fr = fr * (1 - 0.45 * war * red)[:, None] + light(HUNDING, 0.36 * war * red)
            fr += light(SIEGMUND, 0.4 * war * blue)
            fr += light(WHITE, 0.35 * war * np.exp(-((d - line) / 14) ** 2) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.9 * t)))
        # a glimpse of the fight at dawn: red and blue clash on the porch
        for j, tk in enumerate(T_DAWN):
            a = t - tk
            if 0 <= a < 0.9:
                c = at(G, 'Porch Front', 0.3 + 0.2 * j)
                fr += light(STEEL, 0.9 * np.exp(-a / 0.1) * np.exp(-((d - c) / 30) ** 2))
                fr += light(HUNDING, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - c - 60 - 200 * a) / 40) ** 2))
                fr += light(SIEGMUND, 0.6 * np.exp(-a / 0.3) * np.exp(-((d - c + 60 + 200 * a) / 40) ** 2))

        # the drug: a slow murky swirl round her as she mixes, a glint carried to him
        mix = smoothstep(T_MIX, T_MIX + 1.5, t) * (1 - smoothstep(T_MIX + 6, T_MIX + 7.5, t))
        if mix > 0:
            sw = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d - sl) / 70 - 0.5 * T))
            fr += light(DRUG, 0.55 * mix * sw * np.exp(-((d - sl) / 110) ** 2) * np.clip(0.6 + 0.4 * swirl(T), 0, None))
        if T_MIX + 6 <= t < T_DRINK + 3:
            q = sl - 25 if t < T_DRINK else sl - 25 + (hu - sl + 25) * smoothstep(T_DRINK, T_DRINK + 0.5, t)
            g = 1 - smoothstep(T_DRINK + 0.5, T_DRINK + 1.0, t)
            fr += light(DRUG, 0.7 * g * np.exp(-((d - q) / 10) ** 2))
            if t >= T_DRINK + 0.5:
                a = t - T_DRINK - 0.5
                fr += light(DRUG, 0.45 * np.exp(-a / 1.0) * np.exp(-((d - hu) / 60) ** 2))

        # her look at the tree: a line of amber from her to the trunk, and the hilt answers
        if look > 0:
            lo, hi = min(sl, pf), max(sl, pf)
            beam = smoothstep(lo - 5, lo + 25, d) * smoothstep(hi + 5, hi - 15, d)
            fr += light(SIEGLINDE, 0.45 * look * beam * (0.75 + 0.25 * np.cos(2 * np.pi * (d / 40 - 0.6 * T))))
            fr += light(HILT, look * (0.45 + 0.4 * ring) * np.exp(-((d - pf) / 25) ** 2))
            fr += light(STEEL, 0.5 * look * ring * np.exp(-((d - pf) / 6) ** 2))

        # the people
        fr = figure(fr, S, sm, SIEGMUND, C['sm'][f], SM_START[1])
        if C['sl'][f] > 0:
            fr = figure(fr, S, sl, SIEGLINDE, C['sl'][f], SL[1])
        if C['hu'][f] > 0:
            boost = 0.25 * np.exp(-(t - stomp[i]) / 0.2) if i >= 0 else 0.0
            fr = brute(fr, S, hu, C['hu'][f] * (1 + boost), HU[1])
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(np.interp(t, C['t'], C['pos'][k]))

    for name, gain, rev in (('low', 0.36, 0.22), ('strings', 0.3, 0.32), ('winds', 0.28, 0.35), ('brass', 0.28, 0.3),
                            ('harp', 0.26, 0.4), ('perc', 0.3, 0.28), ('fx', 0.12, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tptm = M.sampler('Brass/Trumpet/straightM-sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash_s = M.hits('Percussion/cymbal-crash1_mp*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v2*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    sm = pan_at(at(G, 'Left', 0.5))
    pf = pan_at(at(G, 'Porch Front', 0.5))
    for t, d, m, v, part, k in compose():
        sl, hu = pan_of(0, t), pan_of(1, t)
        if part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'hunding':
            M.add('brass', tuba.play(m, v, dur=d * 1.05, release=0.3), t, 1.0, hu)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d * 1.05, release=0.3), t, 0.7, hu)
            if k < 2:
                M.add('brass', tbn.play(m + 19, v - 16, dur=d * 1.05, release=0.3), t, 0.6, hu)
                M.add('low', cb.play(m - 12, v, dur=d * 1.05, release=0.3), t, 0.6, hu)
            M.add('perc', timp.play(v, pitch=-4 if m % 12 == 2 else -9), t, 0.8, hu)
        elif part == 'siegmund':
            if m >= note('D4'):
                hold('brass', horn, m - 12, t, t + min(d, 5.0), v, sm, rise=0.3, fall=1.5, gain=0.7)
            elif m >= note('D3'):
                hold('brass', horn, m, t, t + min(d, 5.0), v - 8, sm, rise=0.3, fall=1.5, gain=0.6)
            else:
                M.add('low', vc.play(m, v, dur=d * 1.05, release=0.3), t, 0.9, sm)
        elif part == 'clash':
            c = pan_at(at(G, 'Porch Front', 0.3 + 0.2 * k))
            M.add('perc', anvil.play(v), t, 0.6, c)
            M.add('perc', timp.play(v, pitch=-4), t, 0.8, c)
            M.add('perc', crash_s.play(v - 10), t, 0.5, c)
            M.add('brass', tbn.play(m + 12, v, dur=0.4, release=0.2), t, 0.7, c)
        elif part == 'nothung':
            M.add('brass', tptm.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, sm)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, -0.2, rise=2.0, fall=1.5, gain=0.6)
        elif part == 'drug':
            M.add('winds', bsn.play(m - 12, v, dur=d * 1.1, release=0.3), t, 0.8, sl)
            M.add('winds', cl.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.6, sl)
        elif part == 'gulp':
            M.add('low', tuba.play(m, v, dur=d, release=0.5), t, 0.8, hu)
            M.add('harp', harp.play(note('A2'), 70), t + 0.3, 0.7, hu)
        elif part == 'sword':
            M.add('brass', tpt.play(m, v, dur=d * 1.05, release=0.5), t, 0.9, pf)
        elif part == 'swordpad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, pf, rise=0.6, fall=2.0, gain=0.6)
        elif part == 'weary':
            if d > 2:
                hold('strings', vc, m, t, t + min(d, 5.0), v, sm, rise=0.5, fall=2.0, gain=0.7)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, sm)
        elif part == 'night':
            hold('strings', vc, m, t, t + d, v, sm, rise=3.0, fall=1.5, gain=0.5)
    for j, ts in enumerate(np.arange(T_LOOK + 1.0, T_LOOK + 4.5, 0.3)):     # the hilt glints: harp harmonics
        M.add('harp', harp.play(note(('C5', 'E5', 'G5', 'C6')[j % 4]), 60), float(ts), 0.6, pf)
    M.add('perc', roll.play(70, dur=3.0), T_FORT + 10.0, 0.4, pan_at(at(G, 'Side', 0.3)))
