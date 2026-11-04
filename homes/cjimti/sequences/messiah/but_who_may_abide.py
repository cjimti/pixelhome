"""But Who May Abide: the bass's amber shakes the house, then the alto's calm rose light and the refiner's white-hot fire.

"Thus saith the Lord, the Lord of Hosts": the bass's deep amber voice speaks from the back of the porch, and the
strings' dotted figures strike amber across the wings, one blow a note. "And I will shake": on the long run of
"shake" the whole house trembles, its light jolting sideways on every semiquaver and shaking harder as the run
climbs, until "the heav'ns and the earth" lands it.

Then the alto's air, and the contrast is the scene. The Larghetto is calm: the house a soft rose-violet, swaying on
the air's lilt, the alto's rose voice at the back of the porch asking "But who may abide the day of His coming?", the
strings' echo warming the wings. The Prestissimo breaks in: "For He is like a refiner's fire." The house becomes a
furnace, gold flickering with every semiquaver and burning hotter with the strings' crescendos, a white-hot core
riding the voice and racing along the roofline on the long runs of "refiner's", sparks thrown off it on every beat,
and each "fire" bursting white. The Adagio stops it dead: rose again, slow, "for He is like a refiner's", the rose
warming toward gold as the cadence comes, and "fire." blazes white-hot for the closing ritornello, its last four
hammered chords striking the whole house, the last left glowing gold.

The music is Handel's own: Messiah No. 5, the accompagnato from the start to "the heav'ns and the earth," and No. 6,
the ritornello's last chord and "But who may abide the day of His coming?" with the strings' echo, the Prestissimo's
first fourteen bars (two "refiner's fire"s), and the Adagio with the last Prestissimo to the end, transcribed from
Prout's full score (Novello, 1902) into but_who_may_abide.musicxml (No. 6 numbered on from No. 5: its bar n is bar
40 + n) and timed by scripts/score_excerpt.py, each tempo a little quicker than Prout's mark. Strings only, as Handel
scored them; the bass's line on cellos and a bassoon, the alto's on violas and a clarinet, a harpsichord continuo.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, colormap, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS05'
TITLE = 'But Who May Abide'
KIND = 'show'
DESCRIPTION = ("\"I will shake the heavens\": the bass's amber makes the house tremble. Then the alto's calm rose light "
               "alternates with the refiner's fire, white-hot and fast, sparks thrown off along the roofline.")
VOICEOVER = 'But who may abide the day of His coming? For He is like a refiner\'s fire.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Bass', 'Alto', 'Vn1', 'Vn2', 'Va', 'Bassi')}
BASS, ALTO = PART['Bass'], PART['Alto']
SEG = EX['segments']
T_LARGO = SEG[1]['start']                   # No. 6, the Larghetto
T_FIRE = SEG[2]['start']                    # the Prestissimo
T_ADAGIO = SEG[3]['start']
T_FIRE2 = BAR[191]                          # "fire." and the closing ritornello
T_SHAKE0, T_SHAKE1 = BAR[6], BAR[7] + 0.5 * (BAR[8] - BAR[7])       # the run on "shake"
T_ECHO = BAR[56] + 2 / 3 * (BAR[57] - BAR[56])                      # the strings' echo, forte
T_HAMMER = BAR[197]                         # the four hammered chords
T_LAST = BAR[198]
FIRE_WORDS = [BAR[106], BAR[112]]           # "fire," in the Prestissimo
SHAKE = [n for n in BASS if T_SHAKE0 - 0.01 <= n[0] < T_SHAKE1 - 0.01]
B_ON = np.array([n[0] for n in BASS])
A_ON = np.array([n[0] for n in ALTO])
V1 = PART['Vn1']
V1_ON = np.array([n[0] for n in V1])
LOW_ON = np.array([n[0] for n in PART['Bassi']])
RUNS = [(BAR[105], BAR[106]), (BAR[109], BAR[112])]                # the runs of "refi---ner's"

AMBER = hexc('#e08a20')                     # the bass
EMBER = hexc('#5a2408')
ROSE = hexc('#c890d8')                      # the alto
DUSK_ROSE = hexc('#3a2050')
WHITE = hexc('#ffffff')                     # the refiner's fire
GOLD = hexc('#ffb020')
DEEP = hexc('#ff6a10')
FLAME = colormap([(0.0, hexc('#ff3a00')), (0.35, hexc('#ff7a10')), (0.6, GOLD), (0.85, hexc('#fff0c0')),
                  (1.0, WHITE)])


def heat_at(t):
    """How hot the fire burns, 0..1: the strings' dynamics in the Prestissimo (p, the crescendo, f, p again)."""
    pts = [(T_FIRE, 0.45), (BAR[101], 0.5), (BAR[102] - 0.05, 0.75), (BAR[102] + 0.6, 0.95), (BAR[103], 0.6),
           (BAR[106] - 0.05, 0.68), (BAR[106] + 0.3, 1.0), (BAR[107], 0.62), (BAR[111], 0.75), (BAR[112] + 0.3, 1.0),
           (BAR[113], 0.95)]
    if T_FIRE2 <= t:
        pts = [(T_FIRE2, 1.0), (T_FIRE2 + 1.6, 0.8), (BAR[193], 0.75), (T_HAMMER, 0.85), (T_LAST, 0.9), (END, 0.8)]
    xs, ys = zip(*pts)
    return float(np.interp(t, xs, ys))


def burning(t):
    return T_FIRE <= t < T_ADAGIO or t >= T_FIRE2


def note_at(onsets, notes, t):
    j = int(np.searchsorted(onsets, t, side='right')) - 1
    return (j, notes[j]) if j >= 0 else (-1, None)


def sparks(rng, G):
    """Sparks thrown off the fire: [t0, d0, speed, life, size], a drizzle as hot as the fire, a few on every beat of
    the bass, and bursts on every "fire"."""
    wings = np.concatenate([G.pd[G.seg[s]] for s in ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')])
    lo, hi = float(wings.min()), float(wings.max())
    ev = []
    t = T_FIRE
    while t < END:
        if burning(t):
            for _ in range(rng.poisson(9.0 * heat_at(t) * DT * 2)):
                ev.append([t, rng.uniform(lo, hi), rng.uniform(-650, 650), rng.uniform(0.3, 0.8), rng.uniform(7, 12)])
        t += DT * 2
    for tb in LOW_ON:
        if burning(tb) and heat_at(tb) > 0.55:
            for _ in range(2):
                ev.append([tb, rng.uniform(lo, hi), rng.uniform(-800, 800), rng.uniform(0.35, 0.7), rng.uniform(8, 13)])
    for tw in FIRE_WORDS + [T_FIRE2] + [BAR[197] + k * (BAR[198] - BAR[197]) / 4 for k in range(4)]:
        big = 34 if tw in FIRE_WORDS + [T_FIRE2] else 12
        for _ in range(big):
            ev.append([tw + rng.uniform(0, 0.15), rng.uniform(lo, hi), rng.uniform(-1100, 1100), rng.uniform(0.4, 1.1),
                       rng.uniform(9, 15)])
    return np.array(ev)


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    wings = np.isin(seg, ['Left', 'Right'])
    front = seg == 'Porch Front'
    pf = G.pd[G.seg['Porch Front']]
    mid, half = 0.5 * (float(pf.min()) + float(pf.max())), 0.5 * (float(pf.max()) - float(pf.min()))
    l0 = float(G.pd[G.seg['Left']].min())
    r1 = float(G.pd[G.seg['Right']].max())
    off = np.abs(d - mid) / half
    flick = Flicker(rng, G.N, 1.5, 6.0)
    sway = Flicker(rng, G.N, 0.1, 0.35)
    SP = sparks(rng, G)
    shake_off = rng.uniform(-1, 1, len(SHAKE)) * 1.0
    run_dir = [1.0, -1.0]                                   # first run to the right, the second to the left
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        if t < T_LARGO:
            # ---- No. 5: the bass's amber ----
            fr += light(EMBER, 0.1 + 0.05 * smoothstep(0, 2.0, t))
            # the strings' dotted figures strike amber across the wings and the porch's sides, a blow a note
            i, n = note_at(V1_ON, V1, t)
            if n is not None and t - n[0] < 0.5:
                a = t - n[0]
                k = sum(1 for m in V1[max(0, i - 3):i + 1] if n[0] - m[0] < 0.45)          # the figure's notes so far
                hit = (0.45 + 0.1 * k) * np.exp(-a / (0.45 if n[1] > 0.3 else 0.2))
                fr += light(AMBER, hit * (wings + 0.6 * np.isin(seg, ['Porch Left', 'Porch Right'])))
            # the bass's voice: a deep amber glow at the back of the porch, wider for lower notes
            _, n = note_at(B_ON, BASS, t)
            if n is not None:
                a = t - n[0]
                on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.35)
                w = 0.35 + 0.25 * (50 - n[2]) / 14
                g = np.exp(-(off / max(0.25, w)) ** 2) * front
                fr += light(AMBER, (0.5 + 0.35 * smoothstep(0, 0.08, a)) * on * g)
                fr += light(AMBER, 0.22 * on * wings)
            # "and I will shake": the whole house trembles, jolting sideways on every semiquaver, harder as it climbs
            if T_SHAKE0 - 0.05 <= t < T_SHAKE1 + 0.8:
                k = int(np.searchsorted([n[0] for n in SHAKE], t, side='right')) - 1
                grow = np.clip((t - T_SHAKE0) / (T_SHAKE1 - T_SHAKE0), 0, 1)
                amp = (0.5 + 0.5 * grow) * (1 - smoothstep(T_SHAKE1, T_SHAKE1 + 0.8, t)) * smoothstep(
                    T_SHAKE0 - 0.05, T_SHAKE0 + 0.05, t)
                jolt = shake_off[max(k, 0)] * (12 + 26 * grow)
                bands = 0.5 + 0.5 * np.cos(2 * np.pi * (d + jolt) / (46 - 10 * grow))
                tw = np.exp(-(t - SHAKE[max(k, 0)][0]) / 0.07)
                lvl = (0.4 + 0.3 * grow) * (0.4 + 0.6 * bands) * (0.85 + 0.15 * tw) * (0.85 + 0.15 * flick(t))
                fr = fr * (1 - 0.6 * amp) + light(AMBER, amp * lvl) + light(GOLD, 0.3 * amp * tw * bands * grow)
        elif t < T_FIRE:
            # ---- the Larghetto: calm rose, swaying on the lilt ----
            u = t - T_LARGO
            lilt = 0.5 + 0.5 * np.cos(2 * np.pi * (u / (BAR[53] - BAR[52]) - (off * 0.35 + wings * 0.2)))
            base = 0.26 + 0.1 * lilt + 0.03 * sway(t)
            fr += light(ROSE, base * (1 - 0.45 * side)) + light(DUSK_ROSE, 0.08)
            _, n = note_at(A_ON, ALTO, t)
            if n is not None and n[0] < T_FIRE:
                a = t - n[0]
                on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.4)
                g = np.exp(-(off / (0.5 + 0.15 * (n[2] - 62) / 7)) ** 2) * front
                fr += light(ROSE, (0.3 + 0.2 * smoothstep(0, 0.15, a)) * on * g)
                fr += light(hexc('#f0d8ff'), 0.12 * on * g * np.exp(-a / 0.3))
            if t >= T_ECHO - 0.05:                                  # the strings' echo warms the wings
                e = smoothstep(T_ECHO - 0.05, T_ECHO + 0.2, t) * np.exp(-max(0.0, t - BAR[58]) / 0.8)
                fr += light(ROSE, 0.22 * e * wings) + light(hexc('#ffe0f0'), 0.12 * e * wings)
            fr *= smoothstep(T_LARGO - 0.4, T_LARGO + 0.6, t) * 0.3 + 0.7
        elif t < T_ADAGIO or t >= T_FIRE2:
            # ---- the refiner's fire ----
            h = heat_at(t)
            i, n = note_at(V1_ON, V1, t)
            a = t - n[0] if n is not None else 1.0
            # the bed: tongues of flame licking both ways along the roofline, re-kindled on every semiquaver, deep
            # orange in the troughs, gold, and white at the tips as the fire burns hotter
            rnd = np.random.default_rng(1000 + max(i, 0)).uniform(0, 1, G.N)      # a fresh flicker each semiquaver
            w1 = np.sin(2 * np.pi * (d / 120.0 + t * (1.6 + 1.2 * h)) + 2.0 * np.sin(d / 37.0))
            w2 = np.sin(2 * np.pi * (d / 75.0 - t * (2.1 + 1.4 * h)) + 1.5 * np.sin(d / 53.0 + 1.0))
            flames = np.clip(0.5 + 0.28 * (w1 + w2) + 0.35 * (rnd - 0.5) + 0.12 * flick(t), 0, 1)
            pulse = 0.85 + 0.15 * np.exp(-a / 0.08)
            temp = np.clip(h * (0.1 + 1.05 * flames) * pulse, 0, 1)
            lvl = (0.06 + 0.85 * temp ** 1.2) * np.where(side, 0.5, 1.0)
            temp = np.where(side, 0.5 * temp, temp)
            fr += light(FLAME(temp), lvl)
            # the voice: a white-hot core, at the back of the porch on held notes, racing along the house on the runs
            _, n = note_at(A_ON, ALTO, t)
            if n is not None and n[0] >= T_FIRE:
                a = t - n[0]
                on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.3)
                c, w = mid, 0.45 * half
                for r, (r0, r1_) in enumerate(RUNS):
                    if r0 - 0.01 <= n[0] < r1_:
                        idx = [m for m in ALTO if r0 - 0.01 <= m[0] < r1_]
                        k = idx.index(n)
                        prog = (k + smoothstep(0, 0.12, a)) / len(idx)
                        reach = (r1 - mid) if run_dir[r] > 0 else (mid - l0)
                        c, w = mid + run_dir[r] * prog * reach * 0.92, 38.0
                g = np.exp(-((d - c) / w) ** 2)
                fr = fr * (1 - 0.5 * on * g[:, None]) + light(WHITE, (0.55 + 0.35 * smoothstep(0, 0.05, a)) * on * g)
            # "fire": a burst of white across the house
            for tw in FIRE_WORDS + [T_FIRE2]:
                if 0 <= t - tw < 1.5:
                    b = np.exp(-(t - tw) / 0.35) * smoothstep(0, 0.04, t - tw)
                    fr += light(WHITE, 0.6 * b * (1 - 0.4 * side)) + light(GOLD, 0.3 * b)
            # the four hammered chords: the whole house struck, each beat
            if T_HAMMER <= t < T_LAST:
                q = (t - T_HAMMER) / ((T_LAST - T_HAMMER) / 4)
                b = np.exp(-(q - np.floor(q)) * (T_LAST - T_HAMMER) / 4 / 0.18)
                fr = fr * (1 - 0.5 * b) + light(WHITE, 0.55 * b) + light(GOLD, 0.35 * b)
            # the last chord: the house left glowing gold, the fire settling
            if t >= T_LAST:
                s = smoothstep(T_LAST, D, t)
                fr = fr * (1 - 0.7 * s) + light(GOLD, (0.55 - 0.15 * s) * s * (1 - 0.4 * side))
        else:
            # ---- the Adagio: rose again, slow, warming toward gold as the cadence comes ----
            warm = smoothstep(BAR[189] + 1.0, T_FIRE2, t)
            col = (1 - warm) * ROSE + warm * GOLD
            ember = np.exp(-(t - T_ADAGIO) / 1.2) * 0.25
            base = 0.17 + 0.05 * sway(t) + 0.1 * warm
            fr += light(col, base * (1 - 0.45 * side)) + light(DEEP, ember * (1 - side) * (0.6 + 0.4 * flick(t)))
            _, n = note_at(A_ON, ALTO, t)
            if n is not None and n[0] >= T_ADAGIO - 0.01:
                a = t - n[0]
                on = smoothstep(0, 0.5, a) * (1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.6))
                g = np.exp(-(off / (0.55 + 0.25 * warm)) ** 2) * front
                fr += light(col, 0.42 * on * g) + light(WHITE, 0.1 * on * g * warm)
            k, n = note_at(LOW_ON, PART['Bassi'], t)
            if n is not None and T_ADAGIO <= n[0] < T_FIRE2:
                a = t - n[0]
                fr += light(col, 0.12 * np.exp(-a / 0.8) * smoothstep(0, 0.2, a) * wings)
        # the sparks thrown off the fire
        if len(SP) and burning(t):
            act = SP[(SP[:, 0] <= t) & (t < SP[:, 0] + SP[:, 3])]
            if len(act):
                age = (t - act[:, 0]) / act[:, 3]
                pos = act[:, 1] + act[:, 2] * (t - act[:, 0]) * (1 - 0.4 * age)
                amp = (1 - age) ** 1.5
                g = np.exp(-((d[None, :] - pos[:, None]) / act[:, 4:5]) ** 2) * amp[:, None]
                hot = (g * (1 - age[:, None]) ** 2).sum(0)
                fr += light(GOLD, np.clip(g.sum(0), 0, 1) * 0.6) + light(WHITE, np.clip(hot, 0, 1) * 0.9)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them, first violins left to basses right; the bass's line on cellos and a bassoon from
    the porch, the alto's on violas and a clarinet; a harpsichord continuo. Thunder under "I will shake", and the
    refiner's fire roaring and crackling under the Prestissimo."""
    o = Orchestra(M, level=2.9)
    o.effects([(0.0, -14.0), (T_LARGO, -40.0), (T_FIRE, -15.0), (T_ADAGIO, -40.0), (T_FIRE2, -13.0), (D, -16.0)])
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            fast = dd < 0.12
            vel = v - (6 if fast else 0)
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.1), vel - (4 if p == 'Vn1' else 7), pan[p], 0.38 if fast else 0.45)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.1), vel - 5, pan[p], 0.38 if fast else 0.45)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel - 2, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 10, pan[p], 0.34)
    for t, dd, m, v, h, _ in BASS:                                      # the bass, from the porch
        o.play('cellos', m, t, max(dd, 0.14), v + 10, 0.0, 0.6)
        o.play('bassoons', m, t, max(dd, 0.14), v - 2, 0.0, 0.32)
    for t, dd, m, v, h, _ in ALTO:                                      # the alto, from the porch
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('violas', m, t, max(dd, 0.14), v + 10, 0.05, 0.6)
        o.play('clarinets', m, t, max(dd, 0.14), v - 4, 0.05, 0.3)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(92, v - 6)), min(dd, 0.4)) for t, dd, m, v, h, _ in PART['Bassi']
             if not burning(t)]
    chords = [(BAR[188] + 1.0, (55, 58, 62)), (BAR[188] + 2.0, (57, 62, 65)), (BAR[188] + 3.0, (55, 60, 64)),
              (BAR[189], (57, 62, 65)), (BAR[189] + 2.0, (55, 58, 62)), (BAR[190], (57, 62, 65)),
              (BAR[190] + 2.0, (57, 61, 64))]
    for tc, ms in chords:                                               # the Adagio's chords under the voice
        notes += [(tc + 0.02 * k, m, 62, 1.6) for k, m in enumerate(ms)]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.42, 0.0)
    # the staging: thunder and a timpani roll under "shake"; the fire's roar; a cymbal on each "fire"
    o.thunder(T_SHAKE0 + 0.1, near=0.5, pan=0.0, gain=0.7)
    o.hit('timpani roll', T_SHAKE0, 96, pitch=-5, gain=0.4)
    o.fire(T_FIRE, T_ADAGIO + 0.4, level=lambda tt: np.interp(tt, [T_FIRE, BAR[102], BAR[103], BAR[112], T_ADAGIO],
                                                               [0.25, 0.7, 0.4, 0.8, 0.6]), pan=0.0, crackle=14.0)
    o.fire(T_FIRE2, D, level=lambda tt: np.interp(tt, [T_FIRE2, T_LAST, D], [0.9, 0.7, 0.2]), pan=0.0, crackle=16.0,
           seed=11)
    for tw in FIRE_WORDS + [T_FIRE2]:
        o.hit('crash', tw, 92, gain=0.22, pan=0.0)
