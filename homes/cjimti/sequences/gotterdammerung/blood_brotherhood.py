"""Blood Brotherhood: the hall of the Gibichungs, Gutrune at Siegfried's side. Siegfried, who no longer remembers
the bride asleep behind the fire, scorns it ("Ich fürchte kein Feuer") and offers to fetch her for Gunther: on the
music's leaping figures tongues of orange fire lick round the whole house, and Gunther comes down from his throne.

The music is Wagner's own, four passages of Act I as Solti's 1958 Vienna Philharmonic recording takes them: "Ich
fürchte kein Feuer" (bars 601-611), the oath of blood brotherhood (640-660), the drink (723-730) and "Frisch auf
die Fahrt!" (772-785). The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): the fire
on violins, piccolo and harp; the oath's descending octaves on trumpets, its answer on trombones, the great falling
line of its fortissimo on the whole brass with tuba, basses and timpani; the conspiracy creeping on tuba and cello
tremolo; Hagen's falling octaves on tuba, trombones, timpani and gong; Siegfried's horn call on horns and trumpets.
The stage adds the fire's roar under Siegfried's boast, a blade whistling across each arm, and the wind in the sail.

On the oath's octaves every note strikes a whole run emerald, with rings out from Siegfried; each cuts his arm on
its climaxes, two blood red flashes, and their blood runs out along the roofline to both ends and back into the
drinking horn between them. Gunther's answer strikes the runs gold, the conspiracy seeps out of Hagen in black and
violet under the build, and the fortissimo's falling line hurls emerald runs against gold. "Trink' ich dir Treu'":
a white flash in the horn, and the three colours burst out together. Then Hagen's falling octaves land, each a blow
that knocks the hall dark.

Siegfried's horn rings out in great chords and the two of them go down to the river, along Porch Right and Right,
and are gone up the Rhine in a wake of teal and white, leaving Gutrune in the hall and Hagen in the shadows.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by Act
I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD11'
TITLE = 'Blood Brotherhood'
KIND = 'show'
DESCRIPTION = ('Siegfried and Gunther cut their arms, mix their blood in a horn and swear brotherhood, emerald and '
               'gold across the house. Hagen refuses to drink, and the two of them sail off for the fire rock.')
VOICEOVER = ('Siegfried and Gunther mix their blood and swear to be brothers. '
             'Hagen will not drink.')

K = 4                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 601-611, 640-660, 723-730 and 772-785, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SEG = [s['start'] for s in EX['segments']] + [D]
T_COME = (BAR[607], BAR[610])               # Gunther comes down to him
T_CUT = [BAR[652], BAR[656]]                # Siegfried's arm on the oath's first climax, Gunther's on the fortissimo
T_DRINK = 59.7                              # "trink' ich dir Treu'": the chord as he drinks
T_GO = (BAR[776], BAR[780])                 # down to the river
T_BOAT = (BAR[780], BAR[785] + 0.6)         # up the Rhine and gone

AMBER = hexc('#ff8a20')
PURPLE = hexc('#6a10c0')
TORCH = hexc('#ffb040')
HEAT = hexc('#fff0a0')
REED = hexc('#2a6a20')
RIVER = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
FOAM = hexc('#14c080')
HAGEN = hexc('#7a00ff')
SPEAR = hexc('#c8d8ff')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
POTION = hexc('#a050ff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
WHITE = hexc('#ffffff')
ORANGE = hexc('#ff5000')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD10 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD12 picks it up
GUNTHER_FROM = ('Porch Front', 0.62)
GUNTHER_AT = ('Porch Front', 0.7)           # beside Siegfried for the oath
GUTRUNE_FROM = ('Porch Front', 0.75)
GUTRUNE_AT = ('Porch Front', 0.5)           # steps back for the oath, and stays
HAGEN_AT = ('Porch Left', 0.35)
SIEGFRIED_AT = ('Porch Front', 0.85)
HORN_AT = ('Porch Front', 0.775)            # the drinking horn between them
FIGS_END = dict(gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75))


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


RUNS = ['Left', 'Right', 'Side', 'Right', 'Left']
TORCHES = [('Left', 0.2), ('Left', 0.55), ('Left', 0.88), ('Porch Left', 0.2), ('Porch Left', 0.7),
           ('Porch Front', 0.15), ('Porch Front', 0.5), ('Porch Front', 0.85), ('Porch Right', 0.3),
           ('Porch Right', 0.8), ('Side', 0.6)]


def stage(G):
    """The hall of the Gibichungs as profiles over the house: the hall on the porch, its far walls on Left and the
    Side, torches along them, the riverbank on Right with the Rhine running past its free end."""
    d = G.pd
    rng = np.random.default_rng(1848)       # the same torches, drapes and river in every scene, so the cuts match
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    walls = np.isin(seg, ['Left', 'Side'])
    mid = at(G, 'Porch Front', 0.5)
    river = smoothstep(at(G, 'Right', 0.55), at(G, 'Right', 1.0), d)
    tp = np.array([at(G, s, u) for s, u in TORCHES])
    return dict(
        d=d, mid=mid, porch=porch, walls=walls, torch_at=tp,
        hall=porch * (0.6 + 0.4 * np.exp(-((d - mid) / 200) ** 2)) + walls * (0.45 + 0.2 * smooth_noise(rng, d, 50.0)),
        drape=(porch | walls) * (0.5 + 0.5 * np.sin(2 * np.pi * d / 140)) ** 2,
        torch=np.exp(-((d[None, :] - tp[:, None]) / 9) ** 2).sum(0),
        glow=np.exp(-((d[None, :] - tp[:, None]) / 45) ** 2).sum(0),
        bank=(seg == 'Right') * (1 - river) * (0.7 + 0.3 * smooth_noise(rng, d, 30.0)),
        river=river,
        fl=Flicker(rng, G.N, 3.0, 9.0),
        sway=Flicker(rng, G.N, 0.2, 0.7),
    )


def hall(S, T, lv):
    """The hall at shared time T with levels lv (hall, drapes, torches, bank, river, gloom)."""
    d, fl = S['d'], S['fl'](T)
    fr = light(AMBER, lv['hall'] * S['hall'] * (0.85 + 0.15 * fl))
    fr += light(PURPLE, lv['drapes'] * S['drape'] * (0.85 + 0.15 * S['sway'](T)))
    fr += light(TORCH, lv['torches'] * np.clip(S['torch'], 0, 1) * (0.75 + 0.25 * fl))
    fr += light(AMBER, 0.6 * lv['torches'] * np.clip(S['glow'], 0, 1) * (0.8 + 0.2 * fl))
    fr += light(REED, lv['bank'] * S['bank'])
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 90 - 0.55 * T)) * np.sin(2 * np.pi * (d / 230 - 0.2 * T) + 1.0)
    fr += light(RIVER + (TEAL - RIVER) * u[:, None], lv['river'] * S['river'])
    fr += light(FOAM, lv['river'] * S['river'] * np.clip(u - 0.75, 0, None) * 3)
    return fr * (1 - lv['gloom'])


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the hall, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def wave(S, p, a, speed=1200.0, width=90.0, life=0.9):
    """A ring running out both ways from p, a seconds after it starts -> perceptual."""
    return np.exp(-a / life) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2) * (a >= 0)


def blow(fr, S, p, a, s=1.0):
    """Hagen's blow, a seconds after it lands at p: the house knocked dark and a black-violet shock out from him."""
    if not 0 <= a < 2.5:
        return fr
    fr = fr * (1 - 0.9 * s * np.exp(-a / 0.9))
    fr = fr + light(HAGEN, 0.5 * s * np.exp(-a / 0.35))
    fr = fr + light(HAGEN, s * wave(S, p, a, 1100.0, 230.0, 1.2))
    fr = fr + light(SPEAR, 0.9 * s * np.exp(-a / 0.12) * np.exp(-((S['d'] - p + 18) / 8) ** 2))
    return fr


def part_of(t, d, m, v, h):
    """What a note of the excerpt is: (part, k), see compose()."""
    if t < SEG[1] and h == 0 and v >= 90 and (t < 5.5 or 8.8 <= t < 10.5):
        return 'loge', int(t >= 5.5)
    if BAR[640] <= t < BAR[642] and h == 0 and d >= 0.3 and v >= 98:
        return 'oath', 0
    if BAR[652] <= t < BAR[656] and h == 1 and v >= 100 and d >= 0.25:
        return 'oath', 1
    if 41.5 <= t < 48.0 and d >= 0.25 and v >= 100:
        return 'oathb', 0
    if BAR[642] <= t < BAR[651] and h == 1 and d >= 0.25:
        return 'plot', None
    if 62.5 <= t < 70.0 and d >= 1.0 and v >= 110:
        return 'hagen', None
    if t >= SEG[3] and h == 0 and d >= 0.5 and v >= 110:
        return 'horn', 0
    return 'music', None


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). Over Siegfried's "Ich fürchte
    kein Feuer" the right hand's loud figures are Loge's fire ('loge', k = which half); the descending octaves that
    open the oath are the oath ('oath', k 0, emerald), the left hand's rising arpeggio between the cuts its answer
    ('oath', k 1, gold), the great falling line of the fortissimo its second form ('oathb'); the bass under the
    oath's build is the conspiracy ('plot'); the falling octaves after the drink are Hagen's blows ('hagen'); the
    loud chords of "Frisch auf die Fahrt!" are Siegfried's horn ('horn'). Everything else is 'music'."""
    N = [(float(t), float(d), int(m), int(v)) + part_of(t, d, m, v, h) for t, d, m, v, h, _ in tidy(EX['notes'])]
    for part in ('hagen', 'horn'):                          # one blow, one call, per chord: the lights' cue
        cue = [e for e in N if e[4] == part]
        keep = [e for i, e in enumerate(cue) if i == 0 or e[0] - cue[i - 1][0] > 0.2]
        N = [e for e in N if e[4] != part] + keep + [e[:4] + ('music', None) for e in cue if e not in keep]
    return sorted(N, key=lambda e: e[0])


def where(G, t):
    """Siegfried and Gunther: by the throne, then down Porch Right and Right to the river and away up it."""
    L = G.pd.max()
    sf, gun0, gun1 = at(G, *SIEGFRIED_AT), at(G, *GUNTHER_FROM), at(G, *GUNTHER_AT)
    shore = at(G, 'Right', 0.55)
    gun = gun0 + (gun1 - gun0) * smoothstep(*T_COME, t)
    go = smoothstep(*T_GO, t)
    sf, gun = sf + (shore - sf) * go, gun + (shore - 25 - gun) * go
    up = smoothstep(*T_BOAT, t) ** 1.3
    return sf + (L + 60 - shore) * up, gun + (L + 60 - shore) * up


def render(G, seed=11):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    loge = [e for e in N if e[4] == 'loge']
    oath = [e for e in N if e[4] == 'oath']
    oathb = [e for e in N if e[4] == 'oathb']
    plot = [e for e in N if e[4] == 'plot']
    horn = [e for e in N if e[4] == 'horn']
    hag = [e for e in N if e[4] == 'hagen']
    p_hag, p_horn = at(G, *HAGEN_AT), at(G, *HORN_AT)
    g0, g1 = at(G, *GUTRUNE_FROM), at(G, *GUTRUNE_AT)
    runs = ['Porch Front', 'Right', 'Porch Left', 'Left', 'Porch Right', 'Side']
    right = G.seg_of == 'Right'
    foam = Flicker(np.random.default_rng(seed), G.N, 3.0, 9.0)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(START)
        lv['river'] += 0.3 * smoothstep(T_BOAT[0] - 2, T_BOAT[0], t) * (1 - smoothstep(T_BOAT[1], D - 1, t))
        fr = hall(S, T, lv)
        p_sf, p_gun = where(G, t)
        p_gut = g0 + (g1 - g0) * smoothstep(*T_COME, t)

        # the bride behind the fire: tongues of Loge's fire licking round the whole house
        for t0, dur, m, v, part, k in loge:
            a = t - t0
            if 0 <= a < 1.4:
                u = float(np.clip((m - 60) / 22, 0, 1))
                c = L * (0.05 + 0.9 * u) if k == 0 else L * (0.95 - 0.9 * u)
                tongue = np.exp(-((d - c) / (120 + 220 * a)) ** 2) * np.exp(-a / 0.55)
                fr += light(ORANGE, 1.0 * tongue)
                fr += light(TORCH, 0.9 * tongue * np.exp(-a / 0.18))

        # Gunther comes down from the throne: two gold surges out over the house
        for j in range(2):
            a = t - T_COME[0] - 2.0 * j
            if 0 <= a < 1.6:
                fr += light(GUNTHER, 0.85 * wave(S, p_gun, a, 1200.0, 200.0, 0.8))
                fr += light(GUNTHER, 0.5 * np.exp(-a / 0.3) * S['porch'])

        # the cuts: a red flash at each arm, and the blood runs out to both ends and back into the horn
        for k, t0 in enumerate(T_CUT):
            a = t - t0
            p = p_sf if k == 0 else p_gun
            if 0 <= a < 0.6:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.08) * np.exp(-((d - p) / 12) ** 2))
            if 0 <= a < 5.0:
                r = L * (a / 1.6 if a < 1.6 else max(0.0, 1 - (a - 1.6) / 1.8))
                g = np.exp(-max(a - 3.4, 0) / 0.5)
                fr += light(BLOOD, g * np.exp(-((np.abs(d - p) - r) / 70) ** 2))
                fr += light(BLOOD, 0.45 * g * smoothstep(r + 40, r - 40, np.abs(d - p)) * (a < 1.6))
        bowl = smoothstep(T_CUT[1] + 3.0, T_CUT[1] + 4.0, t) * (1 - smoothstep(T_DRINK, T_DRINK + 0.5, t))
        fr += light(BLOOD, 0.8 * bowl * np.exp(-((d - p_horn) / 9) ** 2))

        # the oath: every note strikes a whole run, emerald then gold, rings out from the two of them
        for i, (t0, dur, m, v, part, k) in enumerate(oath):
            a = t - t0
            if 0 <= a < 2.0:
                run = G.seg_of == runs[i % len(runs)]
                col = SIEGFRIED if k == 0 else GUNTHER
                fr = fr * (1 - 0.6 * np.exp(-a / 0.5) * run)[:, None]
                fr += light(col, np.exp(-a / (0.3 + dur)) * run)
                fr += light(HEAD if k == 0 else HEAT, 0.6 * np.exp(-a / 0.1) * run)
                fr += light(col, 0.8 * wave(S, p_sf if k == 0 else p_gun, a, 1500.0, 130.0, 0.7))
        # its second form: great falling octaves, emerald runs against gold runs
        for i, (t0, dur, m, v, part, k) in enumerate(oathb):
            a = t - t0
            if 0 <= a < 2.5:
                hiq = m >= note('C4') - 12
                rs = ['Left', 'Side', 'Porch Left'] if hiq else ['Right', 'Porch Right', 'Porch Front']
                run = np.isin(G.seg_of, rs)
                col = SIEGFRIED if (i + k) % 2 == 0 else GUNTHER
                fr = fr * (1 - 0.55 * np.exp(-a / 0.6) * run)[:, None]
                fr += light(col, 1.0 * np.exp(-a / (0.4 + 0.6 * dur)) * run)
                fr += light(WHITE, 0.5 * np.exp(-a / 0.08) * run)

        # the conspiracy beneath: a slow seep of black and violet out from Hagen
        for t0, dur, m, v, part, k in plot:
            a = t - t0
            if 0 <= a < dur + 2.0:
                reach = min(1.0, a / 3.0) * 900
                seep = smoothstep(reach + 120, reach - 120, np.abs(d - p_hag)) * np.exp(-max(a - dur, 0) / 0.8)
                fr = fr * (1 - 0.45 * seep)[:, None]
                fr += light(HAGEN, 0.55 * seep * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 150 + 0.5 * t))))

        # they drink: a white flash in the horn and the three colours burst out together
        if T_DRINK <= t < T_DRINK + 4.0:
            a = t - T_DRINK
            fr += light(WHITE, min(1.0, 1.2 * np.exp(-a / 0.12)) * np.exp(-((d - p_horn) / 40) ** 2))
            fr += light(HEAT, 0.6 * np.exp(-a / 0.15))
            for j, col in enumerate((SIEGFRIED, GUNTHER, BLOOD)):
                b = a - 0.3 * j
                if b > 0:
                    r = 650 * b
                    fr += light(col, 0.95 * np.exp(-b / 2.2) * smoothstep(r + 60, r - 200, np.abs(d - p_horn))
                                * smoothstep(r - 520, r - 220, np.abs(d - p_horn)))

        # the horn call, and the boat up the Rhine with its wake
        for t0, dur, m, v, part, k in horn:
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(SIEGFRIED, (0.85 - 0.3 * k) * np.exp(-a / 0.3) * right)
                fr += light(SIEGFRIED, (0.7 - 0.3 * k) * wave(S, p_sf, a, 1400.0, 150.0, 0.7))
        if T_BOAT[0] - 0.5 <= t < T_BOAT[1] + 1.5:
            fade = 1 - smoothstep(T_BOAT[1], T_BOAT[1] + 1.5, t)
            wake = (d < p_sf) * (d > at(G, 'Right', 0.5)) * np.exp(-(p_sf - d) / 240) * right * fade
            fr += light(TEAL, 0.9 * wake)
            fr += light(WHITE, 0.7 * wake * np.clip(foam(T) - 0.3, 0, 1))

        # left behind: Gutrune's rose rolls out once over the empty hall
        if T_BOAT[1] <= t < D:
            a = t - T_BOAT[1] - 0.5
            fr += light(GUTRUNE, 0.6 * wave(S, p_gut, a, 900.0, 160.0, 1.4) * (1 - smoothstep(D - 2.5, D - 0.5, t)))

        # the people
        gone = 1 - smoothstep(T_BOAT[1] - 2.0, T_BOAT[1], t)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        if gone > 0:
            fr = figure(fr, S, p_gun, GUNTHER, 0.8 * gone)
            fr = figure(fr, S, p_sf, SIEGFRIED, 0.85 * gone)
            fr += light(HEAD, 0.8 * 0.85 * gone * np.exp(-((d - p_sf) / 6) ** 2))
        for t0, dur, m, v, part, k in hag:
            fr = blow(fr, S, p_hag, t - t0, 1.0 if m < note('C3') else 0.6)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, and the stage's sounds: the fire Siegfried scorns, the
    blades drawn across their arms, the sail filling as they go."""
    from pixelhome.audio import whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.2)
    hag = pan_at(at(G, *HAGEN_AT))
    sfp, gunp = pan_at(at(G, *SIEGFRIED_AT)), pan_at(at(G, *GUNTHER_AT))
    N = compose()

    def role(t, d, m, v, h):
        part, k = part_of(t, d, m, v, h)
        if part == 'loge':                                  # the fire: violins, piccolo, harp
            return [('violins', 0, 0, 0.6), ('piccolo' if m >= 79 else 'flutes', 12 if m < 67 else 0, -10, 0.4),
                    ('harp', 0, -20, 0.35)]
        if part == 'oath':                                  # the oath: trumpets for him, trombones for Gunther
            return [('trumpets' if k == 0 else 'trombones', 0, 0, 0.85), ('horns', 0, -6, 0.5),
                    ('tuba', -12 if m >= 48 else 0, -12, 0.45)]
        if part == 'oathb':                                 # its second form: the whole brass, falling
            return [('trombones', 0, 4, 0.9), ('horns', 12, -4, 0.6), ('tuba', 0 if m < 40 else -12, 0, 0.7),
                    ('basses', -12 if m >= 40 else 0, 0, 0.5)]
        if part == 'plot':                                  # the conspiracy creeping in the bass
            return [('tuba', 12 if m < 36 else 0, -6, 0.55), ('cellos trem', 12, -10, 0.45)]
        if part == 'hagen':
            return [('tuba', 0 if m >= 33 else 12, 4, 0.9), ('trombones', 12, -6, 0.6), ('basses', 0, 0, 0.6)]
        if part == 'horn':                                  # his horn call, in full brass
            return [('horns', 0, 0, 0.8), ('trumpets', 0, -10, 0.45)]
        return None

    def pan(t, m):
        if t < SEG[1]:
            return -0.5 + float(np.clip(t / SEG[1], 0, 1))
        if t >= T_GO[0]:
            return pan_at(where(G, t)[0]) * 0.7
        return 0.0

    o.tutti(tidy(EX['notes']), size=lambda t: 0.6 if t < SEG[1] else 1.0, role=role, pan=pan)
    for t, d, m, v, part, k in N:
        if part == 'oathb' and m < 48:
            o.hit('timpani', t, min(127, v), pitch=-5, gain=0.6)
        elif part == 'hagen':
            o.hit('timpani', t, 120, pitch=-7, gain=0.8, pan=hag)
            o.hit('gong', t, 100, gain=0.4, pan=hag)
    o.hit('crash', BAR[640], 110, gain=0.6)                 # the oath begins
    o.hit('crash', T_CUT[1], 124, gain=0.8)
    o.hit('crash', T_DRINK, 118, gain=0.7)
    o.hit('timpani roll', BAR[654], 110, pitch=-4, gain=0.6)

    # the stage: the fire Siegfried scorns, the blades, the sail
    o.fire(0.3, 10.5, level=lambda tt: 0.35 + 0.4 * np.exp(-((tt - 3.0) / 1.5) ** 2), pan=lambda t: -0.6 + 0.11 * t)
    for k, t0 in enumerate(T_CUT):                          # a blade drawn across each arm
        p = sfp if k == 0 else gunp
        M.add('fx', whoosh(0.3, 2500, 7000, 0.7, seed=31 + k), t0 - 0.12, 0.9, p)
        o.hit('metal', t0, 96, gain=0.35, pan=p)
    # the fire and the blades lead; the effects keep out of the oath, the drink and the horn call
    o.effects([(0, 0), (10.0, 0), (11.5, -10), (T_CUT[0] - 1.0, -10), (T_CUT[0] - 0.3, 0), (T_CUT[1] + 1.0, 0),
               (T_CUT[1] + 2.0, -12), (T_GO[1] - 1.5, -12), (T_GO[1], -2), (D, -2)])
    o.wind(T_GO[1] - 1.0, D, level=lambda tt: 0.5 + 0.3 * smoothstep(T_BOAT[0], T_BOAT[0] + 3, tt),
           pan=pan_at(at(G, 'Right', 0.8)))
