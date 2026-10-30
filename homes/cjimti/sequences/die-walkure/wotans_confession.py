"""Wotan's Confession: alone on the rocky pass with the one daughter who is his will, Wotan tells everything,
and the house becomes his memory. Brünnhilde (silver, gold glints) kneels at his side to her own horn motif
(Donington 88) while his blue spreads out from the porch and gathers at both free ends of the roofline: a frame
for what he remembers.

First the Rhinegold: the river's teal waves roll along the whole house and the gold kindles on the rock at the
back of the porch, swelling note by note to its horn call (Donington 44) and then, on the trumpet, throwing
glittering rays out to both ends. The gold draws itself into the Ring (Donington 8): ten gold beads circling the
house, flaring on every chord of the clarinets and bassoons, faster on the second time round until they close
on one point. Then Alberich's Curse (Donington 13) in trombones and tubas over a hammering F sharp: the house
goes red-black, each note of the climb sends a red ring out from the Ring wider than the last, and the fall
drops a blood wash with black crawling through it. Erda rises out of the porch in moss green to her own motif
(Donington 3) in the low strings and bassoon, and her warning, the Twilight of the Gods (Donington 4), falls in
horns and trombones as the castle's gold fades away from the porch in steps. Valhalla (Donington 63) sounds
soft in the brass while the eight Valkyries streak in from the ends of the house, each bringing a hero's white
spark to the heights. And the need he cannot meet: a lone Wälsung blue spark wanders on Right to the Sword
(Donington 45) on a muted trumpet; Wotan's blue reaches out along Porch Right toward it and his own spear's
steel line slams down across the corner. "Das Ende!": one blue blaze of the whole house and a crash, and then
Wotan's grief (Donington 82) in trombones and cellos as the memories drain out of the house, the slate and the
dawn come back, and he sinks, dim, with Brünnhilde silver beside him.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody, bass

CODE = 'WK13'
TITLE = "Wotan's Confession"
KIND = 'show'
DESCRIPTION = ('Wotan tells Brünnhilde everything: the stolen gold, the Ring and its curse, Erda\'s warning, '
               'the heroes gathered to defend Valhalla, and the free hero he needs but cannot make. '
               'His memories fill the house, and then he wants only one thing: the end.')
VOICEOVER = ('Wotan has never told anyone the whole truth. Tonight he tells his daughter, '
             'and every memory is worse than the last.')

BEAT = 0.75                                 # a quarter note at 80
T_ASK = 1.0                                 # Brünnhilde kneels by him, to her motif
T_TELL = 6.5                                # his blue spreads to frame the memories
T_GOLD = [9.0, 13.2]                        # the Gold's call: horn, then trumpet
GBEAT = 0.6
T_RING = [18.0, 23.4]                       # the Ring, twice
RBEAT = 0.45
T_CURSE = 29.0
CBEAT = 0.5
T_ERDA = 39.5
T_DOWN = 45.5
T_HEROES = 51.5                             # Valhalla; the Valkyries bring the fallen
T_HERO = 59.5                               # the free hero he cannot make
T_BLOCK = 63.6                              # his spear bars the way
T_ENDE = 66.6                               # "Das Ende!"
T_GRIEF = 67.6
GRBEAT = 0.6
T_HOME = 70.0                               # the pass comes back
D = 80.0
K = 12                                      # the shared clock: T = t + 80*K lines the beds up across the cuts
GLINTS = (-24, -9, 10, 23)                  # where Brünnhilde's gold glints sit about her

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
DEEP = hexc('#065c70')
GREEN = hexc('#14c080')
GOLD = hexc('#ffaa00')
HOT = hexc('#fff0a0')
RED = hexc('#ff1800')
BLOOD = hexc('#5a0000')
ERDA = hexc('#3a8a20')
MOSS = hexc('#1a5010')
CASTLE = hexc('#fff0c0')
HERO = hexc('#ffffff')
SIEGMUND = hexc('#30a8ff')
VALK = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
VFROM = [('Right', 1.0), ('Left', 0.0), ('Right', 0.8), ('Left', 0.25), ('Right', 0.6), ('Left', 0.5),
         ('Right', 0.4), ('Left', 0.7)]


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def pass_bed(G):
    """The rocky pass at dawn: slate ridges on the wings and Side, warm light on the porch heights.
    Returns f(T, wings, porch) -> (N,3), T on the shared clock."""
    d, z = G.pd, G.pos[:, 2]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.35 * np.sin(d / 430)))
    crag = 0.5 + 0.5 * np.cos(2 * np.pi * d / 61 + 2.0 * np.sin(d / 97))
    height = 0.55 + 0.45 * smoothstep(-160, -560, z)

    def f(T, wings=1.0, porch_lvl=1.0):
        cloud = 0.85 + 0.15 * np.cos(2 * np.pi * (d / 900 - T / 40))
        sl = (0.62 + 0.22 * ridge + 0.1 * crag) * cloud * ~porch * wings
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - T / 25))
        dw = (0.44 + 0.08 * glow) * height * porch * porch_lvl
        return light(SLATE, sl) + light(DAWN, dw) + light(DAWNHI, 0.2 * glow * height * porch * porch_lvl)
    return f


def handover(G):
    """Fricka's Demand's last look (its pass, its slumped Wotan, its Brünnhilde), for our opening to grow out of.
    f(T, wotan, brunn) -> (N,3). The fixed parts are drawn with the same seeds, so the first frame is its last."""
    rng = np.random.default_rng(1111)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    lat = rng.uniform(0, 1, 80)
    jag = np.interp(d, np.linspace(d.min() - 50, d.max() + 50, 80), lat)
    height = np.exp(-((d - pf) / 430) ** 2)
    drift = Flicker(rng, G.N, 0.05, 0.2)
    shim = Flicker(rng, G.N, 0.3, 1.0)
    RIDGE, DAWN12, GLOW12 = hexc('#5a5a70'), hexc('#ff7a3a'), hexc('#ffb070')

    def f(T, w, b):
        cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - 0.025 * T))
        fr = light(SLATE, 0.5 * (0.75 + 0.25 * cloud) * (1 - 0.4 * height))
        fr += light(RIDGE, 0.3 * jag ** 2 * (0.8 + 0.2 * drift(T)) * (1 - 0.5 * height))
        fr += light(DAWN12, 0.55 * height * (0.88 + 0.12 * shim(T)))
        fr += light(GLOW12, 0.3 * height ** 3 * (0.8 + 0.2 * cloud))
        fr += light(WOTAN, 0.45 * np.exp(-((d - w) / 30) ** 2) + 0.35 * 0.45 * np.exp(-((d - w) / 140) ** 2))
        fr += light(SPEAR, 0.35 * 0.6 * smoothstep(w + 15, w + 30, d) * smoothstep(w + 110, w + 95, d))
        fr += light(BRUNN, 0.75 * np.exp(-((d - b) / 24) ** 2) + 0.3 * 0.75 * np.exp(-((d - b) / 120) ** 2))
        fr += light(BGOLD, 0.6 * (0.75 + 0.25 * np.sin(2 * np.pi * T / 1.7)) * np.exp(-((d - b - 14) / 7) ** 2))
        return fr
    return f


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    def motif(key, t0, beat, part, tr=0, vel=96, line=None, k=0, legato=1.0):
        for t, m, v, d in play(key, t0, beat, tr, vel, line, legato):
            add(t, d, m, v, part, k)

    # Brünnhilde at his feet: what troubles you?
    add(0.0, T_TELL + 1.0, 'E1', 70, 'pedal')
    add(0.0, T_TELL + 1.0, 'E2', 56, 'pedal')
    motif('brunnhilde', T_ASK, BEAT, 'brunn', -5, 70, 'melody')
    for t0, ch in ((T_ASK, ('B2', 'E3', 'G3')), (T_ASK + 3, ('C3', 'E3', 'A3'))):
        for m in ch:
            add(t0, 3.2, m, 56, 'pad')
    for i, m in enumerate(('E2', 'G2', 'B2', 'E3')):            # his blue spreads: trombones, low and slow
        add(T_TELL + 0.4 * i, T_GOLD[0] - T_TELL - 0.4 * i + 0.4, m, 66 + 6 * i, 'wotan')

    # the Rhinegold: river waves, the Gold's call twice
    for i, t in enumerate(np.arange(T_GOLD[0], T_RING[0], GBEAT / 2)):
        m = (note('G3'), note('B3'), note('D4'), note('G4'), note('D4'), note('B3'))[i % 6]
        add(t, GBEAT / 2, m, 48 + int(26 * (t - T_GOLD[0]) / 9), 'river', i)
    for m in ('G1', 'G2', 'D3'):
        add(T_GOLD[0], T_RING[0] - T_GOLD[0] + 0.5, m, 64, 'pedal')
    motif('gold', T_GOLD[0], GBEAT, 'gold', 0, 92, k=0)
    motif('gold', T_GOLD[1], GBEAT, 'gold', 12, 104, k=1)

    # the Ring, twice, the second louder
    for j, t0 in enumerate(T_RING):
        for t, m, v, d in play('ring', t0, RBEAT, 0, 84 + 16 * j):
            add(t, d, m, v, 'ring' if m > note('C3') else 'ringbass', j)
    for i, t in enumerate(np.arange(T_RING[1], T_CURSE - 0.6, RBEAT / 2)):     # it tightens: a harp murmur
        add(t, RBEAT, note('G4') + (0, 4, 7, 4)[i % 4], 60 + i, 'harp')

    # the Curse: melody in the trombones, F sharp hammered underneath
    for t, m, v, d in play('curse', T_CURSE, CBEAT, 0, 112):
        add(t, d, m, v, 'curse' if m >= note('C3') else 'cursebass')
    for i in range(int(20 / 1)):
        add(T_CURSE + i * CBEAT, 0.3, 'Gb2', 118 if i % 4 == 0 else 96, 'timp')

    # Erda rises; the Twilight of the Gods falls
    for t, m, v, d in play('erda', T_ERDA, BEAT, -12, 92):
        add(t, d, m, v, 'erda' if m >= note('C3') else 'erdabass')
    for t, m, v, d in play('downfall', T_DOWN, BEAT, -12, 100):
        add(t, d, m, v, 'down' if m >= note('C3') else 'downbass')

    # Valhalla, soft; the Valkyries come in with the fallen
    for t, m, v, d in play('valhalla', T_HEROES, BEAT, 0, 74):
        add(t, d, m, v, 'valhalla')
    for k in range(8):
        tk = T_HEROES + 0.85 * k
        for j in range(6):
            add(tk + j * 0.07, 0.07, note('B5') + (0, 2)[j % 2] - (k % 3), 62, 'trill', k)

    # the free hero: the Sword on a muted trumpet, far off on Right; the spear bars the way
    for m in ('C2', 'G2', 'E3'):
        add(T_HERO, T_BLOCK - T_HERO + 0.4, m, 60, 'pad')
    motif('sword', T_HERO, 0.52, 'sword', 0, 86)
    for t, m, v, d in play('spear', T_BLOCK, 0.42, 0, 116):
        if t < T_BLOCK + 2.4:
            add(t, d, m, v, 'spear')
    add(T_BLOCK, 0.6, 'G1', 118, 'stroke')

    # "Das Ende!"
    for m in ('E1', 'E2', 'B2', 'E3', 'G3', 'B3', 'E4'):
        add(T_ENDE, 1.4, m, 124, 'ende')

    # Wotan's grief
    for b, d, m in melody('wotan_grief'):
        if b < 16:
            add(T_GRIEF + b * GRBEAT, min(d, 16 - b) * GRBEAT * (1.0 if b < 15 else 3.5), m, 92, 'grief')
    for b0, ch in ((0, ('E2', 'B2', 'G3')), (4, ('D2', 'A2', 'Gb3')), (8, ('C2', 'G2', 'E3')), (12, ('E2', 'B2', 'G3'))):
        for m in ch:
            add(T_GRIEF + b0 * GRBEAT, (4 if b0 < 12 else 8.5) * GRBEAT, m, 70 - 4 * (b0 == 12), 'griefpad')
    add(T_GRIEF, D - T_GRIEF, 'E1', 72, 'pedal')
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
    """Per frame: Wotan, Brünnhilde, the lone hero and the reach of Wotan's blue (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    wot = np.full(F, at(G, 'Porch Front', 0.4))
    tb = np.full(F, at(G, 'Porch Right', 0.6))
    tb[t >= T_ASK] = at(G, 'Porch Front', 0.64)
    tb[t >= T_HOME] = at(G, 'Porch Front', 0.62)
    br = follow(tb, np.full(F, 1.3))
    hero = at(G, 'Right', 0.72) + 40 * np.sin(2 * np.pi * t / 3.1) + 18 * np.sin(2 * np.pi * t / 1.3)
    reach = np.zeros(F)
    pr0, pr1 = at(G, 'Porch Front', 0.4), at(G, 'Right', 0.15)
    reach_t = np.where((t > T_HERO + 1.5) & (t < T_BLOCK), pr1 - pr0, 0.0)
    reach = follow(reach_t, np.where(t < T_BLOCK, 1.2, 5.0))
    return dict(t=t, wotan=wot, brunn=br, hero=hero, reach=np.clip(reach, 0, None))


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    pf = at(G, 'Porch Front', 0.5)
    rock = at(G, 'Porch Front', 0.6)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    bed = pass_bed(G)
    prev = handover(G)
    C = choreography(G)
    N = compose()

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def last(ev, t):
        i = int(np.searchsorted([e[0] for e in ev], t, side='right')) - 1
        return (ev[i], t - ev[i][0]) if i >= 0 else (None, 99.0)

    brunn_ev = ons('brunn')
    wot_ev = ons('wotan', 'curse', 'grief', 'spear', 'ende')
    gold_ev = ons('gold')
    ring_ev = sorted({e[0] for e in ons('ring')})
    curse_ev = [e for e in ons('curse')]
    timp_ev = [e[0] for e in ons('timp')]
    erda_ev = ons('erda')
    erda_top = {}
    for e in erda_ev:
        erda_top[e[0]] = max(erda_top.get(e[0], 0), e[2])
    erda_on = sorted(erda_top)
    down_on = sorted({e[0] for e in ons('down')})
    sword_ev = ons('sword')
    grief_ev = ons('grief')
    gp = [e[0] for e in gold_ev]

    tw = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.3, 1.2)
    crawl = 0.3 * np.sin(G.pd / 97 + rng.uniform(0, 6))
    rays = rng.uniform(0, 1, G.N)
    heroes = []                                 # where each Valkyrie leaves her hero on the heights
    for k in range(8):
        heroes.append(at(G, ('Porch Left', 'Porch Front', 'Porch Right')[k % 3], (0.25, 0.5, 0.75, 0.4)[k % 4] + 0.07 * (k // 4)))
    hero_from = [at(G, s, u) for s, u in VFROM]
    endfrom = np.minimum(d, L - d)              # distance in from the nearer free end

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = np.zeros((G.N, 3))
        mem = smoothstep(T_TELL, T_GOLD[0], t) * (1 - smoothstep(T_ENDE + 0.4, T_HOME + 3, t))

        # the pass, dimmed while he remembers
        fr += bed(T, 1 - 0.75 * mem, 1 - 0.8 * mem)

        # his blue frame: out from him and gathered at both free ends of the house
        if mem > 0:
            e, age = last(wot_ev, t)
            voice = np.exp(-age / 0.6) if e is not None else 0.0
            frame = np.exp(-endfrom / 260) + 0.35 * np.exp(-((d - C['wotan'][f]) / 330) ** 2)
            fr += light(WOTAN, mem * (0.42 + 0.14 * voice + 0.06 * np.sin(2 * np.pi * T / 6)) * frame)
            fr += light(WOTAN, 0.12 * mem * (1 - porch))

        # the Rhinegold: the river and the gold on the rock
        g_in = smoothstep(T_GOLD[0] - 0.5, T_GOLD[0] + 1.0, t) * (1 - smoothstep(T_RING[0] - 0.5, T_RING[0] + 1.5, t))
        if g_in > 0:
            w1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 340 - 0.2 * T))
            w2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 130 + 0.4 * T) + 1)
            fr += light(DEEP, g_in * (0.62 + 0.25 * w1)) + light(GREEN, g_in * (0.14 + 0.3 * w1 * w2))
            j = int(np.searchsorted(gp, t, side='right'))
            grow = smoothstep(T_GOLD[0], T_GOLD[1] + 4.2, t)
            r = 40 + 260 * grow + 20 * j / len(gp)
            e, age = last(gold_ev, t)
            flare = np.exp(-age / 0.3) if e is not None else 0.0
            core = np.exp(-((d - rock) / r) ** 2)
            fr += light(GOLD, g_in * (0.3 + 0.55 * grow + 0.25 * flare) * core)
            fr += light(HOT, g_in * (0.4 * grow + 0.3 * flare) * np.exp(-((d - rock) / (0.3 * r)) ** 2))
            if t > T_GOLD[1]:                    # the trumpet: rays of glitter out to both ends
                ray = smoothstep(T_GOLD[1], T_GOLD[1] + 3.0, t)
                lit = (rays < 0.16) * smoothstep(1600 * ray, 1600 * ray - 300, np.abs(d - rock))
                fr += light(GOLD, g_in * 0.9 * lit * (0.5 + 0.5 * tw(t)))

        # the Ring: ten gold beads circling the house, flaring on each chord, closing on one point
        r_in = smoothstep(T_RING[0] - 1.0, T_RING[0] + 0.5, t) * (1 - smoothstep(T_CURSE - 0.2, T_CURSE + 0.6, t))
        if r_in > 0:
            i = int(np.searchsorted(ring_ev, t, side='right')) - 1
            flare = np.exp(-(t - ring_ev[i]) / 0.22) if i >= 0 else 0.0
            u = t - T_RING[0]
            spin = 0.07 * u + 0.012 * max(u - 5.4, 0) ** 2
            close = smoothstep(T_CURSE - 3.0, T_CURSE - 0.3, t)
            fr += light(DEEP, 0.4 * r_in * (1 - close))
            for k in range(10):
                p = ((k / 10 + spin) % 1.0) * L
                p = p + (rock - p) * close
                dd = np.minimum(np.abs(d - p), L - np.abs(d - p))
                fr += light(GOLD, r_in * (0.7 + 0.45 * flare) * np.exp(-(dd / (16 + 10 * flare)) ** 2))
                fr += light(HOT, r_in * 0.5 * flare * np.exp(-(dd / 9) ** 2))
            ripple = 1600 * (t - ring_ev[i]) if i >= 0 else 0
            fr += light(GOLD, r_in * 0.45 * flare * np.exp(-((np.abs(d - rock) - ripple) / 60) ** 2))

        # the Curse: red-black, a red ring for each note of the climb, a blood wash for the fall
        c_in = smoothstep(T_CURSE - 0.3, T_CURSE + 0.3, t) * (1 - smoothstep(T_ERDA - 1.0, T_ERDA + 0.8, t))
        if c_in > 0:
            k = int(np.searchsorted(timp_ev, t, side='right')) - 1
            hit = np.exp(-(t - timp_ev[k]) / 0.18) if k >= 0 else 0.0
            fr += light(BLOOD, c_in * (0.45 + 0.35 * hit))
            for tn, dn, m, v, _, _ in curse_ev:
                if tn <= t < tn + 1.6:
                    rad = (80 + 45 * (m - note('Gb3'))) * smoothstep(tn, tn + 1.2, t) * 3
                    a = np.exp(-(t - tn) / 0.8)
                    fr += light(RED, c_in * 1.1 * a * np.exp(-((np.abs(d - rock) - rad) / 55) ** 2))
            fall = smoothstep(T_CURSE + 13.5 * CBEAT, T_CURSE + 16 * CBEAT, t)
            black = smoothstep(0.1, 0.5, np.sin(2 * np.pi * (crawl + d / 230 - 0.25 * T)))
            fr = fr * (1 - 0.8 * fall * black[:, None] * c_in) + light(RED, c_in * fall * 0.5 * (1 - black))
            fr += light(RED, c_in * 0.6 * np.exp(-((d - rock) / 20) ** 2))

        # Erda rises out of the porch; the Twilight falls
        e_in = smoothstep(T_ERDA - 0.5, T_ERDA + 2.0, t) * (1 - smoothstep(T_DOWN + 2.0, T_HEROES, t))
        if e_in > 0:
            j = int(np.searchsorted(erda_on, t, side='right')) - 1
            h = (erda_top[erda_on[j]] - note('Db3')) / 15 if j >= 0 else 0.0
            pulse = np.exp(-(t - erda_on[j]) / 0.5) if j >= 0 else 0.0
            z = G.pos[:, 2]
            rise = smoothstep(-150, -570, z) * porch
            fr += light(MOSS, e_in * (0.75 + 0.25 * shimmer(t)) * (0.3 + 0.7 * porch))
            fr += light(ERDA, e_in * (0.35 + 0.55 * h + 0.2 * pulse) * (0.25 + 0.75 * rise))
            fr += light(hexc('#a0e070'), e_in * 0.4 * pulse * np.exp(-((d - pf) / 60) ** 2))
        dn_in = smoothstep(T_DOWN - 0.4, T_DOWN + 0.4, t) * (1 - smoothstep(T_HEROES - 0.5, T_HEROES + 1.0, t))
        if dn_in > 0:
            j = int(np.searchsorted(down_on, t, side='right'))
            step = 1 - j / (len(down_on) + 1)
            reach = 200 + 1100 * step
            fr += light(CASTLE, dn_in * (0.25 + 0.5 * step) * smoothstep(reach, reach - 250, np.abs(d - pf)))
            fr = fr * (1 - 0.4 * dn_in * (1 - step))

        # Valhalla: the eight Valkyries bring their heroes to the heights
        h_in = smoothstep(T_HEROES - 0.5, T_HEROES + 1.0, t) * (1 - smoothstep(T_HERO - 0.5, T_HERO + 1.5, t))
        if h_in > 0:
            fr += light(CASTLE, h_in * (0.3 + 0.08 * np.sin(2 * np.pi * T / 3)) * porch)
            for k in range(8):
                tk = T_HEROES + 0.85 * k
                if t < tk:
                    continue
                u = smoothstep(tk, tk + 1.6, t)
                p = hero_from[k] + (heroes[k] - hero_from[k]) * u
                lead = 1 - smoothstep(tk + 1.6, tk + 2.4, t)
                fr += light(VALK[k], h_in * (0.95 * lead + 0.25) * np.exp(-((d - p) / 18) ** 2))
                if lead > 0 and u < 1:
                    q = hero_from[k] + (heroes[k] - hero_from[k]) * smoothstep(tk, tk + 1.6, t - 0.15)
                    fr += light(VALK[k], h_in * 0.5 * lead * np.exp(-((d - q) / 35) ** 2))
                fr += light(HERO, h_in * (0.35 + 0.35 * np.exp(-(t - tk - 1.6) / 0.4) * (t > tk + 1.6))
                            * np.exp(-((d - p) / 9) ** 2))

        # the free hero: a lone blue spark far off; Wotan reaches, his spear bars the way
        f_in = smoothstep(T_HERO - 0.5, T_HERO + 1.0, t) * (1 - smoothstep(T_ENDE - 0.3, T_ENDE + 0.1, t))
        if f_in > 0:
            e, age = last(sword_ev, t)
            flare = np.exp(-age / 0.35) if e is not None else 0.0
            hp = C['hero'][f]
            fr += light(SIEGMUND, f_in * (0.6 + 0.35 * flare) * np.exp(-((d - hp) / (18 + 6 * flare)) ** 2))
            fr += light(SIEGMUND, f_in * 0.18 * np.exp(-((d - hp) / 110) ** 2))
            w0 = C['wotan'][f]
            rr = C['reach'][f]
            span = (d > w0) & (d < w0 + rr)
            tip = np.exp(-((d - (w0 + rr)) / 25) ** 2)
            fr += light(WOTAN, f_in * (0.4 * span + 0.7 * tip * (rr > 5)))
            if t >= T_BLOCK:
                bar = at(G, 'Porch Right', 0.9)
                s = np.exp(-(t - T_BLOCK) / 1.2)
                fr += light(SPEAR, f_in * (0.4 + 0.6 * s) * np.exp(-((d - bar) / 70) ** 4))
                fr += light(HERO, f_in * 0.8 * np.exp(-(t - T_BLOCK) / 0.15) * np.exp(-((d - bar) / 140) ** 2))

        # "Das Ende!": a blaze of blue over the whole house
        if T_ENDE <= t < T_ENDE + 3.0:
            a = np.exp(-(t - T_ENDE) / 0.5)
            fr += light(WOTAN, 1.05 * a) + light(SPEAR, 0.5 * np.exp(-(t - T_ENDE) / 0.12))

        # his grief: each note a slow blue wave drawn in from both ends of the house to him
        for tn, dn, m, v, part, _ in grief_ev:
            if tn <= t < tn + 3.0:
                u = (t - tn) / 3.0
                w0 = C['wotan'][f]
                rad = (1 - u) * 1400
                fr += light(WOTAN, 0.5 * np.sin(np.pi * u) * np.exp(-((np.abs(d - w0) - rad) / 120) ** 2))

        # Wotan himself: slumped, his blue breathing with his voice; brighter while he tells
        e, age = last(wot_ev, t)
        voice = np.exp(-age / 0.5) if e is not None and age < 2 else 0.0
        grief = smoothstep(T_GRIEF, T_HOME + 4, t)
        lvl = 0.62 + 0.25 * smoothstep(T_TELL - 1, T_TELL + 1, t) * (1 - grief) - 0.1 * grief + 0.12 * voice
        w = C['wotan'][f]
        fr += light(WOTAN, lvl * np.exp(-((d - w) / 22) ** 2) + 0.3 * lvl * np.exp(-((d - w) / 80) ** 2))

        # Brünnhilde: silver with gold glints, brighter on her horn
        e, age = last(brunn_ev, t)
        flare = np.exp(-age / 0.35) if e is not None and age < 2 else 0.0
        b = C['brunn'][f]
        bl = (0.66 + 0.25 * flare) * (1 - 0.25 * mem)
        fr += light(BRUNN, bl * np.exp(-((d - b) / 16) ** 2) + 0.22 * bl * np.exp(-((d - b) / 60) ** 2))
        for j, o in enumerate(GLINTS):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        x = smoothstep(0.0, T_TELL - 1.5, t)        # out of Fricka's Demand's last frame
        if x < 1:
            fr = prev(T, C['wotan'][f], b) * (1 - x) + fr * x
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
    for name, gain, rev in (('low', 0.19, 0.2), ('brass', 0.18, 0.32), ('horns', 0.17, 0.38),
                            ('strings', 0.16, 0.32), ('winds', 0.16, 0.38), ('harp', 0.2, 0.45),
                            ('perc', 0.2, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    mtpt = M.sampler('Brass/Trumpet/straightM-sus/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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

    pw = pan_at(C['wotan'][0])
    rock = at(G, 'Porch Front', 0.6)
    VF = [pan_at(at(G, s, u)) for s, u in VFROM]
    for t, d, m, v, part, k in compose():
        pb = pan_at(np.interp(t, C['t'], C['brunn']))
        if part == 'pedal':
            hold('low', cb, m, t, t + d, v, 0.0, rise=2.0, fall=1.5)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.6, fall=0.8, gain=0.7)
        elif part == 'brunn':
            M.add('horns', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pb)
        elif part == 'wotan':
            hold('brass', tbn, m, t, t + d, v, pw, rise=1.2, fall=0.8, gain=0.8)
        elif part == 'river':
            M.add('strings', vn.play(m, v, dur=d * 1.5, release=0.15), t, 0.5, -0.6 + 1.2 * ((k * 7) % 11) / 10)
            if k % 3 == 0:
                M.add('harp', harp.play(m - 12, v), t, 0.6, 0.0)
        elif part == 'gold':
            s = horn if k == 0 else tpt
            M.add('horns', s.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pan_at(rock))
        elif part == 'ring':
            M.add('winds', cl.play(m, v, dur=d, release=0.3), t, 0.9, -0.3)
            M.add('winds', bsn.play(m - 12, v - 8, dur=d, release=0.3), t, 0.6, 0.3)
        elif part == 'ringbass':
            hold('low', cb, m, t, t + d, v, 0.0, rise=0.3, fall=0.8, gain=0.8)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.8, 0.5 * np.sin(t * 3))
        elif part == 'curse':
            M.add('brass', tbn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pan_at(rock))
            M.add('winds', cl.play(m - 12, v - 20, dur=d, release=0.3), t, 0.5, 0.0)
        elif part == 'cursebass':
            M.add('brass', tuba.play(m + 12, v, dur=d, release=0.5), t, 0.8, 0.0)
            hold('low', cb, m + 12, t, t + d, v - 10, 0.0, rise=0.2, fall=0.5, gain=0.7)
        elif part == 'timp':
            M.add('perc', timp.play(v, pitch=-3), t, 0.9, pan_at(rock))
        elif part == 'erda':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.5), t, 0.9, -0.15)
            M.add('winds', bsn.play(m, v - 15, dur=d, release=0.4), t, 0.6, 0.15)
        elif part == 'erdabass':
            hold('low', cb, m + 12, t, t + d, v - 10, 0.0, rise=1.0, fall=1.0, gain=0.8)
        elif part == 'down':
            s = horn if m >= note('D4') else tbn
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d * 1.05, release=0.6), t, 0.8, 0.0)
        elif part == 'downbass':
            hold('low', tuba, m + 12, t, t + d, v - 10, 0.0, rise=0.5, fall=1.0, gain=0.7)
        elif part == 'valhalla':
            s = tuba if m < note('C3') else (tbn if m < note('C4') else horn)
            M.add('brass' if s is not horn else 'horns', s.play(m, v, dur=d * 1.05, release=0.6), t, 0.6, 0.0)
        elif part == 'trill':
            M.add('winds', fl.play(m, v, dur=0.1, release=0.06), t, 0.5, VF[k])
            if t - T_HEROES - 0.85 * k < 0.01:
                M.add('perc', whoosh(1.4, 600, 3500, 0.35, seed=k), t, 0.5, VF[k])
        elif part == 'sword':
            M.add('horns', mtpt.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pan_at(at(G, 'Right', 0.72)))
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d * 1.1, release=0.3), t, 1.0, pan_at(at(G, 'Porch Right', 0.9)))
            M.add('brass', tuba.play(m - 12, v - 10, dur=d * 1.1, release=0.3), t, 0.6, 0.3)
        elif part == 'stroke':
            M.add('perc', timp.play(v, pitch=-6), t, 1.0, pan_at(at(G, 'Porch Right', 0.9)))
            M.add('perc', whoosh(0.5, 4000, 400, 0.4, seed=3), t - 0.35, 0.6, 0.4)
        elif part == 'ende':
            s = tuba if m < note('E2') else (tbn if m < note('E3') else horn)
            M.add('horns' if s is horn else 'brass', s.play(m, v, dur=d, release=0.8), t, 0.9, pw)
            if m == note('E1'):
                M.add('perc', crash.play(124), t, 1.0, 0.0)
                M.add('perc', gong.play(120), t, 0.8, 0.0)
                M.add('perc', timp.play(127, pitch=-7), t, 1.0, 0.0)
                hold('strings', trem, note('E4'), t, t + 1.6, 100, 0.0, rise=0.05, fall=1.5, gain=0.6)
        elif part == 'grief':
            M.add('brass', tbn.play(m - 12, v, dur=d * 1.05, release=0.6), t, 0.9, pw)
            M.add('strings', vc.play(m - 12, v - 10, dur=d * 1.05, release=0.6), t, 0.8, -0.2)
        elif part == 'griefpad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=0.8, fall=1.5, gain=0.7)
    M.add('perc', roll.play(96, dur=1.4), T_CURSE + 14.4 * CBEAT, 0.7, 0.0)
