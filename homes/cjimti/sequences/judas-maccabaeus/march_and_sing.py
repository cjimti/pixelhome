"""March, and Sing unto God: the people march home behind Judas, and sing God's praise.

It opens where See, the Conqu'ring Hero Comes (JM12) ended, the whole road lined, Judas's gold in the Temple, and over
the first bars that gives way to the march (JM12_END, rebuilt from JM12's last frame: change both together). The
March plays its first strain twice, as the score's pencilled note asks: the first time piano, the people's blue and
white lights stepping along every run toward the Temple, one pace on each beat, at walking pace; the second time
forte, with gold among them, every pace landing a little brighter, and the march's tread under it.

Then the chorus, "To crown this conquest, this conquest, with unmeasur'd praise": the marching stops, and every chord
the chorus sings lifts the whole house in blue and white bands. "Sing unto God", fortissimo: the bands swell, gold
pours from the Temple along the runs on each beat; under "crown" the basses run in sixteenths and gold races out
along both wings on each run. "With unmeasur'd praise": the house swells to its fullest, and on the last chord it
settles to the people's blue and white bands, steady, round the Temple's warm light, which is where O Lovely Peace
(JM14) begins.

The music is Handel's own: No. 59, the March's first strain, played twice, and from No. 60, the chorus's
homophonic "To crown this conquest", its "Sing unto God" and its last five bars, transcribed from the Novello vocal
score into march_and_sing.musicxml and timed by scripts/score_excerpt.py (the March at crotchet 112, the chorus at
100). The March is played from the keyboard reduction: its tune on violins with oboes, its inner part on violas, its
bass on cellos, basses and bassoons, and the second time horns on the long notes, trumpets on the tune and timpani;
the chorus plays on strings with oboes and bassoons doubling, horns on the long notes, trumpets and drums for "Sing
unto God" and the end; a harpsichord plays the continuo throughout.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM13'
TITLE = 'March, and Sing unto God'
KIND = 'show'
DESCRIPTION = ("The people's blue and white march toward the Temple along every run, a pace on each beat, and gold "
               "joins them; then the chorus sings God's praise and the whole house swells with every chord.")
VOICEOVER = 'The battles are won. Now the people march to the Temple, singing as they go.'

EX = excerpt(__file__)              # the March's first strain twice (bars 1-12), then No. 60 (bars 13-26)
SEG = EX['segments']
T_FORTE = SEG[1]['start']           # the March again, forte
T_CHORUS = SEG[2]['start']          # "To crown this conquest"
BAR = {}
for m, t in EX['bars']:             # the chorus's bars (the March's numbers repeat; keep the chorus's)
    BAR[int(m)] = t
T_SING = BAR[16]                    # "Sing unto God", ff
T_RUN = SEG[3]['start']             # "To crown", the basses' sixteenths
T_WITH = BAR[24]                    # "with unmeasur'd praise"
T_LAST = BAR[26]                    # "praise.", held
D = round(EX['seconds'] + 1.5, 2)
BEAT = 60 / 112                     # the March's crotchet
CBEAT = 60 / 100                    # the chorus's
NOTES = EX['notes']
SUNG = [n for n in NOTES if n[5] in ('S', 'A', 'T', 'B')]
ONSETS = np.array(sorted({round(n[0], 3) for n in SUNG}))
VEL = np.array([max(n[3] for n in SUNG if abs(n[0] - t) < 0.002) for t in ONSETS])
RUNS = [T_RUN + CBEAT * k for k in range(8)]                  # each beat of the basses' sixteenths

BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')
GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')
NIGHT = hexc('#0a1a4a')
OIL = hexc('#ffb33a')
TIP = hexc('#fff1c0')
PACE = 12.0                         # layout units a step
RANK = 45.0                         # layout units from one rank to the next
CARRY = 3.0                         # seconds JM12's last frame takes to give way


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def jm12_end(G):
    """See, the Conqu'ring Hero Comes (JM12)'s last frame, rebuilt from its code at its last frame (t = 79.275): the
    road lined with blue and white lights, gold over the house, Judas's gold in the middle of the Temple."""
    t = 79.275
    rng = np.random.default_rng(12)
    d, seg = G.pd, G.seg_of
    temple = (seg == 'Porch Front').astype(float)
    road = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    wings = np.isin(seg, ['Left', 'Right']).astype(float)
    side = (seg == 'Side').astype(float)
    flick = Flicker(rng, G.N, 0.5, 2.0)
    lights = []
    for s, a, b in (('Porch Left', 0.0, 0.3), ('Porch Right', 0.0, 0.3), ('Left', 0.25, 0.75), ('Right', 0.25, 0.75)):
        s0, s1 = span(G, s)
        for c in np.arange(s0 + 6, s1 - 4, 15.0):
            lights.append((c, rng.uniform(a, b), rng.random() < 0.5))
    lights = np.array(lights, float)
    shape = np.exp(-((d[None, :] - lights[:, :1]) / 4.0) ** 2)
    lvl = 0.45 + 0.5 * 0.6065                                       # JM12's beat at its last frame
    f0, f1 = span(G, 'Porch Front')
    mid = 0.5 * (f0 + f1)
    fr = light(NIGHT, (0.24 + 0.04 * flick(t)) * (1 - temple) * 0.5)
    fr += light(BLUE, 0.3 * (road + wings + 0.5 * side))
    fr += Glow(G, 12).frame(t, 2.2)
    fr += light(WHITE, (lvl * (lights[:, 2] > 0.5)) @ shape)
    fr += light(BLUE, 1.3 * (lvl * (lights[:, 2] < 0.5)) @ shape)
    fr += light(GOLD, 0.3 * (road + wings + side))
    fr += light(GOLD, 0.15 * np.ones(G.N))
    fr += light(GOLD, 0.95 * 1.4 * np.exp(-((d - mid) / 9.0) ** 2))
    fr += light(CORE, 0.7 * np.exp(-((d - mid) / 3.5) ** 2))
    fr += light(GOLD, 0.2 * np.exp(-((d - mid) / 40.0) ** 2))
    return np.clip(fr, 0, 1)


def bands(G):
    """The people's blue and white bands, as in We Never Will Bow Down (JM10): 1 on blue, 0 on white."""
    return (np.sin(2 * np.pi * G.pd / 110.0) > 0.25).astype(float)


def last_frame(G, glow, t):
    """Where the scene settles on its last chord: blue and white bands over the house, the Temple warm."""
    seg = G.seg_of
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    house = (1 - temple) * (1 - 0.4 * side)
    b = bands(G)
    return (light(BLUE, 0.42 * b * house) + light(WHITE, 0.36 * (1 - b) * house)
            + light(OIL, 0.45 * temple) + glow.frame(t, 1.0))


def pulse(t, onsets, vel, tau):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    if i < 0:
        return 0.0
    return float(np.exp(-(t - onsets[i]) / tau) * vel[i] / 110)


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    house = 1 - temple
    f0, f1 = span(G, 'Porch Front')
    mid = 0.5 * (f0 + f1)
    toward = np.abs(d - mid)                                    # distance from the heart of the Temple, along the path
    flick = Flicker(rng, G.N, 0.3, 1.0)
    b = bands(G)
    start = jm12_end(G)
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        marching = t < T_CHORUS
        if marching:
            # the March: ranks of blue, white (and the second time gold) stepping toward the Temple, a pace a beat
            forte = t >= T_FORTE
            k = (t if not forte else t - T_FORTE) / BEAT
            step = np.floor(k) + smoothstep(0.0, 0.35, k % 1.0)
            land = np.exp(-(k % 1.0) / 0.18)                      # each pace landing
            u = (toward + PACE * step) % (3 * RANK if forte else 2 * RANK)
            rank = np.clip(1.6 - np.abs((u % RANK) - RANK / 2) / 9.0, 0, 1)   # a rank about 26 units deep
            which = np.floor(u / RANK)
            into = smoothstep(T_FORTE - 1.0, T_FORTE + 2 * BEAT, t)
            lvl = (0.5 + 0.15 * land) * (1 - into) + (0.62 + 0.25 * land) * into
            lvl = lvl * house * (1 - 0.45 * side) * smoothstep(0.0, 2.0, t)
            fr += light(NIGHT, 0.22 * house * (1 - 0.3 * into))
            fr += light(BLUE, lvl * rank * (which == 0))
            fr += light(WHITE, 0.85 * lvl * rank * (which == 1))
            if forte:
                fr += light(GOLD, 1.05 * lvl * rank * (which == 2))
                fr += light(GOLD, 0.06 * land * house)
            fr += glow.frame(t, 1.0 + 0.4 * into) + light(OIL, (0.15 + 0.15 * into) * temple)
        else:
            # the chorus: every chord lifts the house's blue and white bands; louder from "Sing unto God"
            sing = smoothstep(T_SING - 0.2, T_SING + 0.6, t)
            p = pulse(t, ONSETS, VEL, 0.35 if t < T_SING else 0.5)
            swell = smoothstep(T_WITH, T_LAST, t)
            settle = smoothstep(T_LAST, T_LAST + 2.5, t)
            lvl = (0.32 + 0.12 * sing + (0.25 + 0.1 * sing) * p + 0.2 * swell) * (0.95 + 0.05 * flick(t))
            hs = house * (1 - 0.4 * side)
            live = light(BLUE, b * hs * ((1 - settle) * lvl + settle * 0.42))
            live += light(WHITE, (1 - b) * hs * ((1 - settle) * 0.85 * lvl + settle * 0.36))
            fr += live
            fr += light(OIL, (0.3 + 0.25 * sing * (1 - settle) + 0.15 * settle) * temple) + glow.frame(t, 1.0 + 0.6 * sing * (1 - settle))
            # "Sing unto God": gold poured from the Temple along the runs on each beat
            if T_SING <= t < T_RUN:
                kk = (t - T_SING) / CBEAT
                a = (kk % 1.0) * CBEAT
                front = 30 + 420 * a
                fr += light(GOLD, 0.9 * np.exp(-a / 0.45) * np.exp(-((toward - front) / 40.0) ** 2) * house)
            # the basses' sixteenths: gold racing out along both wings, a run a beat
            for tr in RUNS:
                a = t - tr
                if 0 <= a < 1.0:
                    front = 120 + 1100 * a
                    fr += light(GOLD, 0.95 * np.exp(-a / 0.5) * np.exp(-((toward - front) / 55.0) ** 2) * house)
            # "with unmeasur'd praise": gold rising over the whole house, gone again as the last chord settles
            fr += light(GOLD, 0.22 * swell * (1 - settle) * hs)
            # the last chord: a warm flash from the Temple
            if t >= T_LAST:
                a = t - T_LAST
                fr += light(GOLD, 0.35 * np.exp(-a / 0.8) * np.exp(-((toward) / 200.0) ** 2))
            if t >= T_LAST + 2.5:
                fr = last_frame(G, glow, t)
        # the opening holds JM12's last frame and gives way to the march over the first bars
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * start
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The March on strings, oboes, bassoons, harpsichord (and the second time horns, trumpets and timpani, with the
    tread of the march under it), the chorus on strings with oboes, bassoons and horns doubling, trumpets and timpani
    for "Sing unto God" and the end."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pl, pr = pan_at(sum(span(G, 'Left')) / 2), pan_at(sum(span(G, 'Right')) / 2)
    o = Orchestra(M, level=2.0)
    o.effects([(0.0, -9.0), (T_CHORUS, -14.0)])
    cont = []
    for t, dd, m, v, h, part in NOTES:
        if part == 'Orch':
            if t < T_CHORUS:                                     # the March, from the reduction
                forte = t >= T_FORTE - 0.01
                vv = v - (22 if not forte else 0)
                if h == 0:
                    top = m == max(n[2] for n in NOTES if n[5] == 'Orch' and n[4] == 0 and abs(n[0] - t) < 0.01)
                    if top:
                        o.play('violins', m, t, dd * 0.92, vv, -0.2, 0.55)
                        o.play('oboes', m, t, dd * 0.9, vv - 8, -0.3, 0.35 if forte else 0.2)
                        if forte:
                            o.play('trumpets', m, t, dd * 0.85, vv - 8, 0.1, 0.32)
                    else:
                        o.play('violas', m, t, dd * 0.92, vv - 6, 0.2, 0.4)
                        if forte and dd >= BEAT * 1.5:
                            o.play('horns', m - 12 if m > 67 else m, t, dd * 0.95, vv - 10, 0.0, 0.35)
                else:
                    o.play('cellos', m, t, dd * 0.92, vv - 2, 0.25, 0.55)
                    o.play('basses', m - 12 if m >= 40 else m, t, dd * 0.92, vv - 6, 0.25, 0.4)
                    o.play('bassoons', m, t, dd * 0.9, vv - 12, 0.2, 0.25 if forte else 0.15)
                cont.append((t, m, int(min(100, vv)), min(dd, BEAT * 0.6)))
            else:                                               # the chorus's continuo and basses
                if m < 45:
                    o.play('basses', m if m >= 28 else m + 12, t, dd * 0.95, v - 6, 0.0, 0.4)
                cont.append((t, m, int(min(100, v)), min(dd, CBEAT * 0.6)))
            continue
        loud = t >= T_SING - 0.01
        last = t >= T_WITH - 0.01
        pan = {'S': pl * 0.5, 'A': pl * 0.3, 'T': pr * 0.3, 'B': pr * 0.5}[part]
        vel = v + (6 if loud else 0)
        if part == 'S':
            o.play('violins', m, t, dd * 0.95, vel, pan, 0.6)
            o.play('oboes', m, t, dd * 0.92, vel - 8, pan, 0.4)
            if loud and dd >= CBEAT * 0.4:
                o.play('trumpets', m, t, dd * 0.9, vel - 6, 0.0, 0.35)
        elif part == 'A':
            o.play('violins', m, t, dd * 0.95, vel - 4, pan, 0.45)
            o.play('violas', m, t, dd * 0.95, vel - 4, pan, 0.3)
            if dd >= CBEAT * 0.9:
                o.play('horns', m, t, dd * 0.95, vel - 10, pan, 0.35)
        elif part == 'T':
            o.play('violas', m, t, dd * 0.95, vel - 2, pan, 0.5)
            if dd >= CBEAT * 0.9:
                o.play('horns', m - 12, t, dd * 0.95, vel - 10, pan, 0.3)
        else:
            o.play('cellos', m, t, dd * 0.95, vel, pan, 0.6)
            o.play('bassoons', m, t, dd * 0.92, vel - 10, pan, 0.35)
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, D + 2.0), 0.0, 0.42, 0.0)
    # the second strain's drums: the tonic and dominant on the bar's strong beats; the tread of the march under them
    k = 0
    t = T_FORTE
    while t < T_CHORUS - 0.05:
        if k % 2 == 0:
            o.hit('timpani', t, 92 if k % 4 == 0 else 80, pitch=0 if k % 8 < 4 else -5, gain=0.28, pan=0.15)
        for side, pp in ((0, pl), (1, pr)):
            o.hit('hoof soft', t + 0.012 * side, 70, pitch=-6, gain=0.35, pan=pp, fx=True)
        t += BEAT
        k += 1
    # "Sing unto God": the drums on its chords; a roll into the last chord and its stroke
    for n_t in ONSETS[(ONSETS >= T_SING - 0.01) & (ONSETS < T_RUN)]:
        if abs(((n_t - T_SING) / CBEAT) % 1.0) < 0.05:
            o.hit('timpani', n_t, 96, pitch=0, gain=0.3, pan=0.15)
    o.hit('timpani roll', T_LAST - 1.6, 84, pitch=0, gain=0.22)
    o.hit('timpani', T_LAST, 108, pitch=0, gain=0.38)
