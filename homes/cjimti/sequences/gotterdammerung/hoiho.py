"""Hoiho!: a red dawn on the shore. Hagen, ultraviolet by his spear at the hall doors, puts the great cowhorn to
his lips and calls the Gibichung vassals to arms: "Hoiho! Hoihohoho!" Each blast is a shock of violet out of him
with an orange front racing to both ends of the house in a second, the doors flaring, the whole shore jolting
awake. His cries ("Wehe! Wehe! Waffen!") wake the runs one by one in torch orange, and the cowhorns answer from
far off, a semitone higher each time, from the left and then from the river end of Right, each flashing its end
of the house. He knocks the house violet with "Not ist da! Not!", and blows his last great "Hoiho!".

Then the men answer from every side: "Was tost das Horn? Wir kommen mit Waffen!", every entry a run thrown into
torch orange, round the house, faster and faster as they run up, while the first torches catch here and there in
sprays of sparks, until they hail him all together, "Hoiho! Hagen!", and the shore stands in full red dawn.

The music is Wagner's own: the start of Act II, scene 3 (bars 389 to 406, 419 to 431 and 437 to 457), as Solti's
1958 Vienna Philharmonic recording takes it, from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py),
orchestrated by hand and register: the cowhorn's C on horns and trombones, the bass on cellos, basses and tuba,
the upper parts on strings and woodwinds. Hagen's own line is not in the reduction; it comes from the printed
vocal score (Klindworth, Schott 1900, archive.org gtterdmmerungerl00wagn, pp. 150-152) and is played as written on
trombones and bassoons. So are the stage cowhorns that answer him (D flat on the left, D on the right), which
the reduction leaves out. Each blast of his horn lands with a drum and timpani blow, his men's weapons clatter
and their feet come running as they muster.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD16'
TITLE = 'Hoiho!'
KIND = 'show'
DESCRIPTION = ('At dawn Hagen blows the great cowhorn and calls his men to arms. Every blast shakes the whole house, '
               'horns answer from every side, and the vassals come running.')
VOICEOVER = ('Hagen blows the war horn. Hoiho! Hoiho! From every side, the men come running.')

K = 1                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 389-406, 419-431 and 437-457, Solti 1958
D = EX['seconds']
_BARS = [(m, t) for m, t in EX['bars']]


def bar(pos):
    """Seconds into the excerpt of a (fractional) bar position."""
    seg = [b for b in _BARS if abs(b[0] - pos) < 20]
    return float(np.interp(pos, [b[0] for b in seg], [b[1] for b in seg]))


T_CALL = [bar(389), bar(393.333), bar(395.333), bar(427.333)]   # his cowhorn, then "Hoiho!", twice, and again
ANSWERS = [(bar(401), 'Right', 1.0), (bar(403.333), 'Side', 0.0), (bar(405.25), 'Left', 0.15),
           (bar(421), 'Left', 0.6), (bar(425), 'Right', 0.55), (bar(437.75), 'Side', 0.4)]
STAGE_HORNS = [(bar(421), bar(423), 'Db3', 3), (bar(425), bar(427), 'D3', 4)]   # the cowhorns on the stage: (t0, t1, note, answer)
T_TRITONE = [bar(419.333), bar(423.333)]    # "Not ist da!", "Not!": the house knocked violet
T_LAST = bar(429.333)                       # one last great blast
T_MEN = bar(437)                            # the men answer from every side
# Hagen's line, from the vocal score: (bar, beat, beats, note); 3/4 except 397-398 and 405-406 in 4/4
VOICE = [(393, 1, 1, 'Bb3'), (393, 2, 4, 'C4'), (395, 1, 1, 'Bb3'), (395, 2, 1.5, 'C4'), (396, 0.5, 0.5, 'C4'),
         (396, 1, 2, 'C4'),
         (397, 1, 1, 'C4'), (397, 2, 1.5, 'C4'), (397, 3.5, 0.5, 'C4'), (398, 0, 0.5, 'C4'), (398, 0.5, 0.5, 'C4'),
         (398, 1.5, 0.75, 'C4'), (398, 2.25, 0.25, 'C4'), (398, 2.5, 1.5, 'C4'), (399, 0, 3, 'C4'),
         (401, 0, 2, 'D4'), (401, 2, 1, 'C4'), (403, 1, 3, 'D4'), (404, 1, 1, 'C4'),
         (405, 1, 2, 'C4'), (405, 3, 1, 'C4'), (406, 1, 2, 'C4'), (406, 3, 1, 'C4'),
         (419, 1, 6, 'Db4'), (421, 1, 1, 'Ab3'), (421, 2, 2, 'Ab3'),
         (423, 1, 4.5, 'D4'), (425, 0, 2, 'D4'), (425, 2, 0.5, 'C#4'), (426, 0, 1.5, 'B3'), (426, 1.5, 0.5, 'C#4'),
         (427, 1, 1, 'Bb3'), (427, 2, 4, 'C4'), (429, 1, 1, 'Bb3'), (429, 2, 1.5, 'C4'), (430, 0.5, 0.5, 'C4'),
         (430, 1, 2, 'C4')]
FOUR = (397, 398, 405, 406)

NIGHT = hexc('#1a2ab0')
MOON = hexc('#80a0ff')
RED_DAWN = hexc('#ff1030')
ORANGE_DAWN = hexc('#ff6a10')
WOOD = hexc('#5a2008')
HALL = hexc('#ff8a20')
SPEAR = hexc('#c8d8ff')
TORCH = hexc('#ff6a10')
FLAME = hexc('#ffd060')
HAGEN = hexc('#7a00ff')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
GOLD = hexc('#ffaa00')
BLOOD = hexc('#c00010')
WHITE = hexc('#ffffff')

START = dict(night=0.3, moon=0.1, dawn=0.6, hall=0.5, spear=0.6)      # where GD15 left the shore
END = dict(night=0.2, moon=0.0, dawn=0.7, hall=0.65, spear=0.7)        # where GD17 picks it up
HAGEN_AT = ('Porch Front', 0.35)
HAGEN_LVL = (0.8, 0.85)
RUNS = ['Right', 'Left', 'Porch Right', 'Side', 'Porch Left', 'Porch Front']


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The shore before the hall as profiles over the house: the porch is the hall's doors, its seams lit from
    inside, the spear upright in the middle of Porch Front; the wings and Side are the shore, the river beyond the
    free end of Right."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same shore, moonlight and torches in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    spear = at(G, 'Porch Front', 0.5)
    L = d.max()
    return dict(
        d=d, L=L, porch=porch, shore=~porch, spear=spear,
        doors=porch * (0.65 + 0.35 * smooth_noise(rng, d, 30.0)),
        seams=porch * np.clip(np.sin(2 * np.pi * (d - at(G, 'Porch Left', 0.0)) / 95) * 3 - 2.2, 0, 1),
        tip=np.exp(-((d - spear) / 7) ** 2),
        river=smoothstep(L - 600, L, d),      # the dawn comes up from the river end
        sand=~porch * (0.7 + 0.3 * smooth_noise(rng, d, 70.0)),
        flick=Flicker(rng, G.N, 3.0, 9.0),
        glow=Flicker(rng, G.N, 0.6, 2.0),
    )


def shore(S, T, lv):
    """The shore at shared time T with levels lv (night, moon, dawn, hall, spear)."""
    d = S['d']
    drift = np.sin(2 * np.pi * (d / 310 + 0.07 * T)) * np.sin(2 * np.pi * (d / 170 - 0.05 * T) + 0.6)
    fr = light(NIGHT, lv['night'] * S['sand'] * (0.85 + 0.15 * drift))
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 600 - 0.03 * T))
    fr += light(MOON, lv['moon'] * S['shore'] * (0.4 + 0.6 * u) ** 2)
    sky = RED_DAWN + (ORANGE_DAWN - RED_DAWN) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 450 + 0.05 * T)))[:, None]
    fr += light(sky, lv['dawn'] * S['shore'] * (0.75 + 0.25 * drift) * (0.7 + 0.3 * S['river']))
    fr += light(WOOD, (0.4 + 0.6 * lv['hall']) * S['doors'])
    fr += light(HALL, lv['hall'] * S['seams'] * (0.8 + 0.2 * S['glow'](T)))
    fr += light(SPEAR, lv['spear'] * S['tip'] * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the shore, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def crowd(S, n, seed=1717):
    """Where n vassals stand with their torches, spread over the shore and the porch runs (not on the spear)."""
    rng = np.random.default_rng(seed)
    p = np.sort(rng.uniform(20, S['L'] - 15, n))
    return p[np.abs(p - S['spear']) > 30]


def torches(S, T, ps, lvl, seed=7):
    """Torches at path distances ps (lvl a scalar or one per torch): orange flames with a flickering gold core."""
    d = S['d']
    lvl = np.broadcast_to(np.asarray(lvl, float), np.shape(ps))
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, len(ps))
    fq = rng.uniform(5, 11, len(ps))
    fl = 0.8 + 0.2 * np.sin(fq * T + ph)
    g = np.exp(-((d[None, :] - np.asarray(ps)[:, None]) / 7) ** 2)
    out = light(TORCH, np.clip((lvl * fl)[:, None] * g, 0, None).sum(0).clip(0, 1.2))
    return out + light(FLAME, np.clip((0.6 * lvl * fl ** 3)[:, None] * g ** 4, 0, None).sum(0).clip(0, 1))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def voice():
    """Hagen's line in seconds: (time, seconds, midi)."""
    out = []
    for b, x, n, name in VOICE:
        per = 4 if b in FOUR else 3
        t0 = bar(b + x / per)
        b1, x1 = b, x + n
        while x1 > (4 if b1 in FOUR else 3) + 1e-9:
            x1 -= 4 if b1 in FOUR else 3
            b1 += 1
        out.append((t0, bar(b1 + x1 / (4 if b1 in FOUR else 3)) - t0, note(name)))
    return out


def compose():
    """Every note: (time, seconds, midi, velocity, part, k). The excerpt's notes are 'score'; Hagen's line is
    'voice', the stage cowhorns 'answer'. 'boom' (each blast of his horn), 'vassals' (each entry of his men) and
    'tritone' (his "Not!") mark moments for the lights and the stage; they make no sound."""
    N = [(t, d, m, v, 'score', h) for t, d, m, v, h in EX['notes']]
    N += [(t, d, m, 112, 'voice', None) for t, d, m in voice()]
    for t0, t1, m, k in STAGE_HORNS:
        N.append((t0, t1 - t0, note(m), 104, 'answer', k))
    for k, t0 in enumerate(T_CALL):
        N.append((t0, 0.5, 36, 0, 'boom', k))
    N.append((T_LAST, 0.5, 36, 0, 'boom', len(T_CALL)))
    for k, (t0, t1, who, text) in enumerate(s for s in EX['singing'] if s[2] != 'Hagen'):
        N.append((t0, t1 - t0, 48, 0, 'vassals', k))
    for k, t0 in enumerate(T_TRITONE):
        N.append((t0, 1.0, 36, 0, 'tritone', k))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=16):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_h = at(G, *HAGEN_AT)
    blasts = sorted({e[0] for e in N if e[4] == 'boom'})
    vas = [e for e in N if e[4] == 'vassals']
    tri = sorted({e[0] for e in N if e[4] == 'tritone'})
    sung = [e[0] for e in N if e[4] == 'voice']
    acc = accents(EX['notes'], vmin=88, n=3, space=0.25)
    rng = np.random.default_rng(seed)
    catches = [(float(t), float(rng.uniform(0.9, 1.2)), float(rng.uniform(40, L - 40)))
               for t in np.sort(rng.uniform(T_LAST, D, 26))]
    seg = G.seg_of

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_LAST, START[k] + 0.5 * (END[k] - START[k])), (T_LAST + 8, END[k])])
              for k in START}
        fr = shore(S, T, lv)

        # the runs the answering horns have woken stay lit in torch orange, and pulse with the vassals' call
        for t0, run, u in ANSWERS:
            if t >= t0:
                a = t - t0
                woke = 0.5 * smoothstep(0, 1.5, a) * (1 - smoothstep(T_LAST + 2, T_LAST + 10, t))
                fr += light(TORCH, woke * (seg == run) * (0.8 + 0.2 * np.sin(2 * np.pi * (d / 160 - 0.4 * t))))
                if a < 1.6:
                    src = at(G, run, u)
                    fr += light(TORCH, 1.0 * np.exp(-a / 0.35) * np.exp(-((d - src) / (120 + 500 * a)) ** 2))
                    fr += light(FLAME, 0.9 * np.exp(-a / 0.12) * np.exp(-((d - src) / 30) ** 2))

        # each blast of the cowhorn: a violet shock out of Hagen with an orange front racing to both ends
        for k, t0 in enumerate(blasts):
            a = t - t0
            if 0 <= a < 2.6:
                s = 0.85 + 0.15 * (k == len(blasts) - 1)
                r = 2000 * (1 - np.exp(-a / 0.9))
                fr += light(HAGEN, s * np.exp(-a / 1.3) * smoothstep(r + 40, r - 160, np.abs(d - p_h)))
                fr += light(TORCH, s * np.exp(-a / 1.1) * np.exp(-((np.abs(d - p_h) - r) / 70) ** 2))
                fr += light(FLAME, 0.7 * s * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_h) - r) / 25) ** 2))
                fr += light(HALL, 0.8 * s * np.exp(-a / 0.4) * S['porch'])

        # the vassals' call: every note throws one whole run into torch orange, round the house
        for j, (t0, dur, m, v, part, k) in enumerate(vas):
            a = t - t0
            if 0 <= a < 0.9:
                run = RUNS[j % len(RUNS)]
                fr += light(TORCH, 0.95 * np.exp(-a / 0.4) * (seg == run))
                fr += light(FLAME, 0.6 * np.exp(-a / 0.15) * (seg == run))

        # the first torches catching: sprays of sparks here and there
        fr += light(FLAME, np.clip(sparks(S, catches, t, 16, n=10, reach=0.4), 0, 1))

        # Hagen answers on his tritone: the house flashes violet from the doors
        for t0 in tri:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(HAGEN, 0.85 * np.exp(-a / 0.7) * smoothstep(1500 * a + 80, 1500 * a - 80, np.abs(d - p_h)))

        # every note he sings rolls a violet ripple out of him; the orchestra's hits flare the doors and the shore
        for t0 in sung:
            a = t - t0
            if 0 <= a < 1.4:
                r = 1300 * a
                fr += light(HAGEN, 0.95 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_h) - r) / 140) ** 2))
        for t0 in acc:
            a = t - t0
            if 0 <= a < 0.6:
                fr += light(HALL, 0.9 * np.exp(-a / 0.2) * S['porch'] * S['doors'])
                fr += light(TORCH, 0.4 * np.exp(-a / 0.22) * S['shore'])

        # Hagen at the doors, swelling with each blast
        swell = sum(np.exp(-(t - t0) / 0.8) for t0 in blasts if 0 <= t - t0 < 4)
        lvl = HAGEN_LVL[0] + (HAGEN_LVL[1] - HAGEN_LVL[0]) * smoothstep(T_LAST, T_LAST + 8, t)
        fr = figure(fr, S, p_h, HAGEN, min(1.0, lvl + 0.25 * swell))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, Hagen's line and the stage cowhorns from the vocal
    score, and the stage: his horn's blows, the men's feet and weapons."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.85)
    # the stage backs off under his calls and comes up as his men come running; it dips again as they hail him
    o.effects([(0, -10), (T_MEN, -10), (T_MEN + 1.0, 0), (bar(454), 0), (bar(456), -5), (D, -5)])
    ph = pan_at(at(G, *HAGEN_AT))

    def role(t, d, m, v, h):
        if t < T_CALL[1] and h == 1 and d > 0.6 and m in (48, 60):          # his cowhorn's C
            return [('horns', 0, 10, 0.9), ('trombones', 0, 4, 0.6)]
        return None

    o.tutti(tidy(EX['notes']), size=lambda t: 0.75 if t >= T_MEN else 1.0, role=role)
    N = compose()
    for t, d, m, v, part, k in N:
        if part == 'voice':                 # Hagen: trombones and bassoons, where he stands
            o.play('trombones', m, t, max(d, 0.15), v, ph, 0.85)
            o.play('bassoons', m, t, max(d, 0.15), v - 8, ph, 0.5)
        elif part == 'answer':              # the stage cowhorns, far off at their end of the house
            p = pan_at(at(G, ANSWERS[k][1], ANSWERS[k][2]))
            for oct_ in (0, 12):
                o.play('horns', m + oct_, t, d, v - 6 * (oct_ > 0), p, 0.7)
            o.play('trombones', m, t, d, v - 10, p, 0.4)
        elif part == 'boom':                # each blast of his horn: a blow at the doors
            o.boom(t, ph, 0.75 if k < len(T_CALL) else 1.0)
            if k >= len(T_CALL) - 1:
                o.hit('crash', t, 118, gain=0.6, pan=ph)
        elif part == 'tritone':
            o.hit('timpani', t, 120, pitch=-6, gain=0.8, pan=ph)
            o.hit('gong', t, 100, gain=0.4, pan=ph)
    # the men come running from every side, weapons clattering as they muster
    rng = np.random.default_rng(16)
    ends = [pan_at(at(G, 'Right', 1.0)), pan_at(at(G, 'Side', 0.0)), pan_at(at(G, 'Left', 0.15))]
    for k, e in enumerate(ends):
        t0 = T_MEN + 0.6 + 3.5 * k
        o.gallop(t0, D - 0.5, 0.30, pan=lambda t, e=e, t0=t0: e * (1 - 0.6 * smoothstep(t0, D, t)), v=80 + 6 * k,
                 gain=0.45)
    for t, d, m, v, part, k in N:
        if part == 'vassals' and k % 2 == 0:
            o.clash(t + 0.05, float(rng.uniform(-0.8, 0.8)), 96 + int(rng.integers(0, 16)), 0.35)
    o.hit('cymbal swell', D - 4.5, 100, gain=0.45)
