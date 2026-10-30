"""Wotan's Confession: alone on the rocky pass with the one daughter who is his will, Wotan tells everything,
and the house becomes his memory. Brünnhilde (silver, gold glints) kneels at his side, "So sah ich dich nie", while
his blue spreads out from the porch and gathers at both free ends of the roofline: a frame for what he remembers.

The music is Wagner's own: Act II, bars 608 to 631 (Wotan's outburst, "O heilige Schmach! O schmählicher Harm!
Götternot! Götternot! Endloser Grimm! Ewiger Gram!") and bars 920 to 943 (the end of his confession, "Fahre denn
hin, herrische Pracht ... Zusammenbreche, was ich gebaut! Auf geb' ich mein Werk! Nur eines will ich noch: das
Ende!"), as Solti's 1958 Vienna Philharmonic recording takes them. The notes come from the Wagner Ring Dataset's
piano reduction (pixelhome/ring.py): the left hand's churning tremolo on cellos and violas, the right hand by turns
on horns (the gold), clarinets and bassoons (the Ring), trombones, horns and trumpets ("Götternot!"), cellos and
bassoon (Erda), violins with flutes and piccolo for the great upward sweeps, and the descending bass of the
collapse on trombones, tuba and basses; the full brass, a cymbal, a gong and the timpani for the last fortissimo.
The memories have their sounds as on a stage: the river rushing along the house, the gold glinting on the
glockenspiel, a gong as it turns into the Ring and again on the curse, thunder on the blood wash, the earth
groaning as Erda rises, the castle's gold crumbling, the Valkyries' hooves, steel as his spear slams down, the
world falling with every step of the bass, and at the end everything shattering at once. His lines come first:
the effects stay well back while he sings and come forward between his lines (the river and the gold, the blood
wash, the crumbling castle, the Valkyries' ride) and for two strokes inside them (the curse's gong on
"Götternot!", his spear slamming down), lead the last fortissimo's shattering, and leave "das Ende!"
alone.

His memories pass over the house on the real music. As the tremolo starts the river's teal waves roll along the
whole house and the gold kindles on the rock at the back of the porch, swelling note by note and then throwing
glittering rays out to both ends. On the orchestra's first stroke the gold draws itself into the Ring: ten gold
beads circling the house, flaring on every note, faster after the second stroke until they close on one point.
"Götternot!": the house goes red-black, each note of the cry sends a red ring out from the Ring wider than the
last, and the fall drops a blood wash with black crawling through it. Erda rises out of the porch in moss green,
and the castle's gold fades away from the porch in steps. As he bids farewell to his splendour the eight
Valkyries streak in from the ends of the house, each bringing a hero's white spark to the heights. Then the need he
cannot meet: a lone Wälsung blue spark wanders on Right, flaring on every great sweep of the strings; Wotan's blue
reaches out along Porch Right toward it, and his own spear's steel line slams down across the corner. On each step
of the falling bass a slow blue wave draws in from both ends of the house to him as the world he built
collapses, until the last fortissimo: one blue blaze of the whole house and a crash. "Das Ende!": the memories
drain away, the slate and the dawn come back, and he sinks, dim, with Brünnhilde silver beside him.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK13'
TITLE = "Wotan's Confession"
KIND = 'show'
DESCRIPTION = ('Wotan tells Brünnhilde everything: the stolen gold, the Ring and its curse, Erda\'s warning, '
               'the heroes gathered to defend Valhalla, and the free hero he needs but cannot make. '
               'His memories fill the house, and then he wants only one thing: the end.')
VOICEOVER = ('Wotan has never told anyone the whole truth. Tonight he tells his daughter, '
             'and every memory is worse than the last.')

EX = excerpt(__file__)                      # Act II, bars 608-631 and 920-943, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
BAR[632] = BAR[920] = EX['segments'][1]['start']
D = EX['seconds']
SUNG = [(t0, t1, who.lower()) for t0, t1, who, _ in EX['singing']]
T_ASK = 0.5                                 # Brünnhilde kneels by him: "So sah ich dich nie"
T_TELL = BAR[610]                           # the tremolo: his blue spreads to frame the memories
T_GOLD = [BAR[612], BAR[614]]               # the gold kindles, then throws its rays
T_RING = [BAR[616], BAR[622]]               # the orchestra's two strokes: the Ring, then faster
T_CURSE = BAR[626]                          # "Götternot!"
T_FALL = BAR[629]                           # the cry falls: a blood wash
T_ERDA = BAR[630]                           # "Endloser Grimm!": Erda rises
T_DOWN = BAR[920]                           # "Fahre denn hin": the castle's gold fades in steps
T_HEROES = BAR[923]                         # the Valkyries bring the fallen
VGAP = 0.75                                 # between one Valkyrie and the next
T_HERO = BAR[927]                           # the free hero he cannot make, on the great sweeps
T_BLOCK = BAR[931]                          # his spear bars the way
T_GRIEF = BAR[934]                          # "Zusammenbreche, was ich gebaut": the falling bass
T_ENDE = BAR[941]                           # the last fortissimo: a blaze
T_LAST = BAR[943]                           # "das Ende!"
T_HOME = BAR[942]                           # the pass comes back
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


def singer(t):
    for t0, t1, who in SUNG:
        if t0 <= t < t1 + 0.3:
            return who
    return None


WINDOWS = [(0.0, T_TELL, 'brunn'), (T_GOLD[0], T_RING[0], 'gold'), (T_RING[0], T_CURSE, 'ring'),
           (T_CURSE, T_ERDA, 'curse'), (T_ERDA, T_DOWN, 'erda'), (T_DOWN, T_HEROES, 'down'),
           (T_HEROES, T_HERO, 'valhalla'), (T_HERO, T_ENDE, 'sword')]


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The right hand takes the part
    of whichever memory is on the house ('gold', 'ring', 'curse', ...); the left hand's long notes in the collapse
    are 'grief', the last fortissimo 'ende', every other left-hand note 'low'. who is whoever is singing."""
    N = []
    for t, d, m, v, hand in EX['notes']:
        if T_ENDE <= t < T_HOME:
            part = 'ende'
        elif hand == 1:
            part = 'grief' if T_GRIEF <= t and d >= 0.8 else 'low'
        else:
            part = next((p for t0, t1, p in WINDOWS if t0 <= t < t1), 'high')
        N.append((t, d, m, v, part, singer(t)))
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

    brunn_ev = [e for e in N if e[5] == 'brünnhilde']
    wot_ev = [e for e in N if e[5] == 'wotan' or e[4] in ('curse', 'grief', 'ende')]
    gold_ev = ons('gold')
    ring_ev = sorted({e[0] for e in ons('ring')} | set(T_RING))
    curse_ev = [e for e in ons('curse')]
    timp_ev = [e[0] for e in N if e[4] == 'low' and T_CURSE <= e[0] < T_ERDA][::8]
    erda_ev = ons('erda')
    erda_top = {}
    for e in erda_ev:
        erda_top[e[0]] = max(erda_top.get(e[0], 0), e[2])
    erda_on = sorted(erda_top)
    down_on = [BAR[b] for b in range(920, 923)] + [T_HEROES - 0.6]
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
                    rad = (80 + 45 * (m - 54)) * smoothstep(tn, tn + 1.2, t) * 3
                    a = np.exp(-(t - tn) / 0.8)
                    fr += light(RED, c_in * 1.1 * a * np.exp(-((np.abs(d - rock) - rad) / 55) ** 2))
            fall = smoothstep(T_FALL, T_FALL + 1.2, t)
            black = smoothstep(0.1, 0.5, np.sin(2 * np.pi * (crawl + d / 230 - 0.25 * T)))
            fr = fr * (1 - 0.8 * fall * black[:, None] * c_in) + light(RED, c_in * fall * 0.5 * (1 - black))
            fr += light(RED, c_in * 0.6 * np.exp(-((d - rock) / 20) ** 2))

        # Erda rises out of the porch; the Twilight falls
        e_in = smoothstep(T_ERDA - 0.5, T_ERDA + 2.0, t) * (1 - smoothstep(T_DOWN + 2.0, T_HEROES, t))
        if e_in > 0:
            j = int(np.searchsorted(erda_on, t, side='right')) - 1
            h = min(1.0, (erda_top[erda_on[j]] - 61) / 15) if j >= 0 else 0.0
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

        # the farewell to his splendour: the eight Valkyries bring their heroes to the heights
        h_in = smoothstep(T_HEROES - 0.5, T_HEROES + 1.0, t) * (1 - smoothstep(T_HERO - 0.5, T_HERO + 1.5, t))
        if h_in > 0:
            fr += light(CASTLE, h_in * (0.3 + 0.08 * np.sin(2 * np.pi * T / 3)) * porch)
            for k in range(8):
                tk = T_HEROES + VGAP * k
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

        # the last fortissimo: a blaze of blue over the whole house; "das Ende!", a last swell
        if T_ENDE <= t < T_ENDE + 3.0:
            a = np.exp(-(t - T_ENDE) / 0.5)
            fr += light(WOTAN, 1.05 * a) + light(SPEAR, 0.5 * np.exp(-(t - T_ENDE) / 0.12))
        if t >= T_LAST:
            a = np.sin(np.pi * min(1.0, (t - T_LAST) / (D - T_LAST)))
            fr += light(WOTAN, 0.45 * a * np.exp(-((d - C['wotan'][f]) / 500) ** 2))

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
    """Wagner's notes, orchestrated from the piano reduction, the right hand coloured by the memory on the house."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    o = Orchestra(M, level=1.85)
    pw = pan_at(C['wotan'][0])
    pr = pan_at(at(G, 'Porch Front', 0.6))
    ph = pan_at(at(G, 'Right', 0.72))
    COLOUR = {'brunn': [('horns', 0, 0, 0.8)],
              'gold': [('horns', 0, 4, 0.9), ('trumpets', 0, -10, 0.4)],
              'ring': [('clarinets', 0, 4, 0.8), ('bassoons', -12, -4, 0.55)],
              'curse': [('horns', 0, 10, 0.9), ('trombones', -12, 8, 0.8), ('trumpets', 0, 0, 0.5)],
              'erda': [('cellos', -12, 6, 0.8), ('bassoons', -12, 0, 0.55)],
              'down': [('horns', 0, 4, 0.8), ('trombones', -12, 0, 0.6)],
              'valhalla': [('violins', 0, 0, 0.6), ('flutes', 0, -8, 0.4), ('horns', -12, -6, 0.4)],
              'high': [('violins', 0, 0, 0.55)]}

    for t, d, m, v, part, who in compose():
        if part in ('low', 'grief'):
            if part == 'grief':                                                 # the collapse: falling bass
                o.play('trombones', m + 12, t, d, v + 6, pw, 0.8)
                o.play('tuba', m, t, d, v, 0.0, 0.6)
                o.play('basses', m, t, d, v, 0.2, 0.55)
                o.play('cellos', m + 12, t, d, v, -0.2, 0.55)
            elif d < 0.3:                                                       # the churning tremolo
                o.play('cellos' if m < 55 else 'violas', m, t, 0.1, v + 4, -0.2 if m < 55 else 0.2, 0.45)
            else:
                o.play('cellos', m, t, d, v, -0.2, 0.7)
                o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.5)
        elif part == 'ende':                                                    # the last fortissimo: full brass
            for sec, tr, g in (('trombones', 0, 0.9), ('horns', 12, 0.8), ('trumpets', 12, 0.5), ('tuba', -12, 0.6)):
                o.play(sec, m + tr if m + tr >= 36 else m, t, d, v, pw, g)
        elif part == 'sword':                                                   # the great sweeps
            o.play('violins', m, t, d, v, ph, 0.6)
            if m >= 77:
                o.play('piccolo' if m >= 83 else 'flutes', m, t, d, v - 10, ph, 0.45)
            if v >= 100 and d >= 0.3:
                o.play('trumpets', m, t, d, v - 10, ph, 0.4)
        else:
            for sec, tr, dv, g in COLOUR[part]:
                o.play(sec, m + tr, t, d, v + dv, pr if part in ('gold', 'curse') else None, g)
    for t0 in T_RING:                                                           # the orchestra's two strokes
        o.hit('timpani', t0, 112, pitch=-5, gain=0.6, pan=pr)
    o.hit('timpani roll', T_CURSE, 100, gain=0.5, pan=pr)
    o.hit('crash', BAR[628], 104, gain=0.45, pan=pr)
    o.hit('timpani', T_FALL, 110, pitch=-4, gain=0.55, pan=pr)
    for b in (927, 929, 933):
        o.hit('cymbal swell', BAR[b] - 1.4, 90, gain=0.35, pan=ph)
    o.hit('crash', T_BLOCK, 112, gain=0.55, pan=pan_at(at(G, 'Porch Right', 0.9)))
    o.hit('timpani', T_BLOCK, 118, pitch=-6, gain=0.6, pan=pan_at(at(G, 'Porch Right', 0.9)))
    o.hit('crash', T_ENDE, 124, gain=0.7)
    o.hit('gong', T_ENDE, 120, gain=0.6)
    o.hit('timpani', T_ENDE, 127, pitch=-7, gain=0.7)

    # the stage: what the memories on the house show, heard
    N = compose()
    fxhit = lambda name, t, v, g, p: o.hit(name, t, v, gain=g, pan=p, fx=True)       # a stage hit, on the fader
    o.wind(T_TELL, T_RING[0] + 1.0, 0.35, pan=0.0)                               # the river rolling along the house
    for t, d, m, v, part, who in N:
        if part == 'gold':                                                      # the gold glinting, note by note
            o.play('glock', min(m + 12, 96), t, 0.2, v - 10, pr, 0.3)
    o.hit('cymbal swell', T_GOLD[1] - 1.4, 95, gain=0.4, pan=pr, fx=True)                 # its rays thrown out
    o.hit('gong', T_RING[0], 112, gain=0.6, pan=pr, fx=True)                             # the gold becomes the Ring
    o.hit('gong', T_RING[1], 104, gain=0.45, pan=pr, fx=True)
    o.hit('gong', T_CURSE, 120, gain=0.6, pan=pr, fx=True)                               # "Götternot!": the curse
    o.thunder(T_FALL, 0.8, pr, 0.9)                                             # the blood wash
    o.thunder(T_ERDA, 0.15, 0.0, 1.0)                                           # Erda rising out of the earth
    fxhit('gong scrape', T_ERDA + 0.3, 110, 0.8, pr)
    for b in range(920, 923):                                                   # the castle's gold crumbling away
        fxhit('scrape', BAR[b], 100, 0.6, pr)
        o.hit('timpani', BAR[b], 96, pitch=-6, gain=0.35, pan=pr, fx=True)
    hero_from = [pan_at(at(G, sg, u)) for sg, u in VFROM]
    for k in range(8):                                                          # the Valkyries riding in with heroes
        tk = T_HEROES + VGAP * k
        o.gallop(tk, tk + 1.6, 0.34, pan=lambda t, k=k, tk=tk: hero_from[k] * (1 - smoothstep(tk, tk + 1.6, t)),
                 v=108, gain=0.75)
    o.clash(T_BLOCK, pan_at(at(G, 'Porch Right', 0.9)), 124, 0.7)               # his spear slams down
    for t, d, m, v, part, who in N:
        if part == 'grief':                                                     # the world he built collapsing
            o.hit('bass drum', t, min(127, v + 10), gain=0.3, fx=True)
            fxhit('scrape', t + 0.05, 90, 0.3, pw)
    o.shatter(T_ENDE, 0.0, 1.0)                                                 # the last fortissimo: it all breaks
    o.thunder(T_ENDE + 0.05, 1.0, 0.0, 1.0)
    # the effects stay well back under his lines and come forward between them: the river and the gold before he
    # speaks, the blood wash and Erda, the crumbling castle and the Valkyries' ride; under "Fahre denn hin" and the
    # collapse they recede, then the last fortissimo's shattering leads, and "das Ende!" is left alone
    o.effects([(0.0, -12), (5.1, -12), (6.0, -5), (13.2, -5), (13.8, -12), (18.1, -12), (18.8, -4), (24.5, -4),
               (25.1, -12), (29.4, -12), (30.0, -4), (32.6, -4), (33.2, -12), (34.6, -12), (34.8, -3), (36.0, -3),
               (36.5, -12), (40.0, -12), (40.4, 0), (41.6, 0),
               (42.4, -6), (46.0, -6), (46.4, -2), (57.6, -2), (58.3, -12), (65.3, -12), (65.5, -3), (66.6, -3),
               (67.0, -12), (82.2, -12), (82.4, 0), (85.2, 0),
               (85.8, -16)])
