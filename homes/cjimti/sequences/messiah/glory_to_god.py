"""Glory to God: the angel speaks from the far porch, silver multiplies across the house, and the heavenly host sings.

"And suddenly there was with the angel": the strings' quick figures shimmer faintly over the night fields, and the
soprano's silver voice is a glow in the middle of Porch Front, the far light where the angel stands. On "a multitude of
the heavenly host" silver sparks start to multiply out from the porch with every semiquaver of the violins, a few, then
dozens, until by "praising God, and saying" the whole house is glittering.

Then the chorus, and the trumpets play for the first time in the work. Handel marks them to sound from a distance, so
they come from Porch Front, the farthest line, in bright gold: every trumpet note is a gold flare spreading out from
the middle of the porch. "Glory to God in the highest" is high and bright on the far porch, the white-gold blazing
brighter the higher the sopranos sing, with the first violins' runs as a silver glint racing along it. "And peace on
earth", the tenors and basses alone, is low and warm on Left and Right, the fields, the porch sinking to an afterglow;
the strings' soft repeated quavers rock the fields gently. The second "Glory", forte, spreads the glory down Porch Left
and Porch Right toward the street; the third, fortissimo, fills the whole house, the trumpet flares running out to
both ends. "Good will towards men" settles the house into warm gold, and the last chord holds it.

The music is Handel's own: Messiah No. 16, the soprano's whole recitative (bars 3-8), and No. 17 bars 1-7, 10-16, 26-28
and 40-42 (here numbered on from No. 16: 9-15, 18-24, 34-36 and 48-50), transcribed from Prout's full score (Novello,
1902) into glory_to_god.musicxml and timed by scripts/score_excerpt.py at Prout's marks (crotchet 72, then 80). Strings,
voices and Handel's two trumpets only; the soprano on flute and oboe, the chorus on strings with oboes and bassoons
doubling and the organ joining for the fortissimo, the trumpets on their own distant, reverberant bus until the last
"Glory" brings them close.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS12'
TITLE = 'Glory to God'
KIND = 'show'
DESCRIPTION = ("A multitude of the heavenly host: silver multiplies across the house, the trumpets sound for the first "
               "time from the far porch in bright gold, and peace on earth glows warm on the fields.")
VOICEOVER = 'And suddenly there was with the angel a multitude of the heavenly host.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 3.0
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p)
        for p in ('Soprano', 'S', 'A', 'T', 'B', 'Tr1', 'Tr2', 'Vn1', 'Vn2', 'Va', 'Bassi')}
CHORUS = PART['S'] + PART['A'] + PART['T'] + PART['B']
T_GLORY = BAR[9]                                   # No. 17
SING = [(p[0], p[1], p[3]) for p in EX['singing'] if p[2] == 'Soprano']
T_MULT = next(a for a, b, w in SING if 'multitude' in w)
T_PRAISE = next(a for a, b, w in SING if 'praising' in w)
T_SUDDEN = PART['Soprano'][0][0]
PEACE = [(next(n[0] for n in PART['T'] if n[0] >= BAR[b] - 0.01), BAR[b + 3]) for b in (13, 22)]
GLORIES = [(BAR[9], PEACE[0][0], 0), (BAR[18], PEACE[1][0], 1), (BAR[34], BAR[48], 2)]
T_GOOD = BAR[48]
T_MEN = PART['S'][-1][0]

NIGHT = hexc('#14204a')
BED = hexc('#06081a')
FIELD = hexc('#c07a30')
SILVER = hexc('#e6f0ff')                           # the soprano, the angel
GLORY = hexc('#fff2c8')                            # the chorus
GOLD = hexc('#ffd040')                             # the trumpets
WARM = hexc('#ffb860')                             # peace on earth


def onsets(notes):
    return np.array(sorted({round(n[0], 3) for n in notes}))


def burst(t, ons, tau, attack=0.03):
    """Per-frame envelope: each onset jumps to 1 and decays with time constant tau (the max over onsets)."""
    e = np.zeros_like(t)
    for o in ons:
        a = t - o
        e = np.maximum(e, np.where(a >= 0, smoothstep(0, attack, a) * np.exp(-np.maximum(a, 0) / tau), 0))
    return e


def sounding(t, notes, release=0.25):
    """Per-frame 0..1: some note of these is sounding (with a short release)."""
    e = np.zeros_like(t)
    for n in notes:
        a = t - n[0]
        e = np.maximum(e, np.where(a >= 0, np.where(a < n[1], 1.0, np.exp(-(a - n[1]) / release)), 0))
    return e


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    t = np.arange(F) * DT
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    front = (seg == 'Porch Front').astype(float)
    runs = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    fields = np.isin(seg, ['Left', 'Right']).astype(float)
    side = (seg == 'Side').astype(float)
    pf = G.pd[G.seg['Porch Front']]
    pf0, pf1 = float(pf.min()), float(pf.max())
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    off = np.abs(d - mid)                                        # along the path from the middle of the porch
    run_dist = np.where(runs > 0, np.minimum(np.abs(d - pf0), np.abs(d - pf1)), 1e9)
    l0, l1 = float(G.pd[G.seg['Left']].min()), float(G.pd[G.seg['Left']].max())
    r0, r1 = float(G.pd[G.seg['Right']].min()), float(G.pd[G.seg['Right']].max())
    # the fields lie toward the street: brightest at their porch ends, fading to the far ends
    field_u = np.where(seg == 'Left', (d - l0) / (l1 - l0), np.where(seg == 'Right', (r1 - d) / (r1 - r0), 0))
    twinkle = Flicker(rng, G.N, 0.15, 0.6)
    shimmer = Flicker(rng, G.N, 4.0, 11.0)

    # sections, as per-frame envelopes
    in_glory = np.zeros(F)
    for g0, g1, _ in GLORIES:
        in_glory = np.maximum(in_glory, smoothstep(g0 - 0.1, g0 + 0.15, t) * (1 - smoothstep(g1 - 0.2, g1 + 1.2, t)))
    spread = np.zeros(F)                                          # how far the glory reaches: 0 porch, 1 runs, 2 house
    for g0, g1, k in GLORIES:
        spread = np.where(t >= g0 - 0.1, float(k), spread)
    peace = np.zeros(F)
    for p0, p1 in PEACE:
        peace = np.maximum(peace, smoothstep(p0 - 0.1, p0 + 0.6, t) * (1 - smoothstep(p1 - 0.4, p1 + 0.4, t)))
    good = smoothstep(T_GOOD - 0.2, T_GOOD + 1.0, t)
    final = smoothstep(T_MEN - 0.05, T_MEN + 0.6, t)
    recit = 1 - smoothstep(T_GLORY - 0.6, T_GLORY + 0.1, t)

    # the angel: the soprano's syllables
    sop = PART['Soprano']
    angel = 0.3 * sounding(t, sop, 0.6) + 0.25 * burst(t, onsets(sop), 0.35)
    angel *= smoothstep(T_SUDDEN - 0.3, T_SUDDEN + 0.2, t)
    # the chorus on the far porch: brighter the higher the sopranos sing
    s_on = onsets(PART['S'])
    s_hit = burst(t, s_on, 0.45)
    s_pitch = np.zeros(F)
    for n in PART['S']:
        s_pitch = np.where(t >= n[0] - 0.02, n[2], s_pitch)
    s_high = np.clip((s_pitch - 69) / 9.0, 0, 1)
    choir = sounding(t, CHORUS, 0.5)
    # the trumpets: each note a gold flare from the middle of the porch
    tr_on = onsets(PART['Tr1'] + PART['Tr2'])
    # peace on earth: the tenors and basses, low and warm
    low = [n for n in PART['T'] + PART['B'] if any(p0 - 0.05 <= n[0] < p1 for p0, p1 in PEACE)]
    low_on = onsets(low)
    low_hold = sounding(t, low, 0.8)
    rock = [n for n in PART['Vn1'] if any(p0 + 2.0 <= n[0] < p1 for p0, p1 in PEACE) and n[1] < 0.3]
    rock_on = onsets(rock)
    # the first violins' runs in the glories: a silver glint along the porch
    v1 = [n for n in PART['Vn1'] if n[0] >= T_GLORY - 0.01]
    v1_on = np.array([n[0] for n in v1])
    v1_m = np.array([n[2] for n in v1])

    # the multitude: silver sparks on the violins' semiquavers, multiplying from the porch outward
    sparks = []
    for n in PART['Vn1']:
        if n[0] < T_SUDDEN or n[0] >= T_GLORY:
            continue
        g = (n[0] - T_MULT) / (T_PRAISE - T_MULT)               # 0 at "a multitude", 1 at "praising God"
        if g < 0 and rng.uniform() > 0.35:
            continue
        k = 1 if g < 0 else int(min(30, round(1 + 2 ** (4.9 * min(g, 1.0)))))
        width = 40.0 + 1300.0 * np.clip(g, 0, 1) ** 1.6       # out from the porch, then over the whole house
        for _ in range(k):
            p = mid + rng.normal(0, width)
            if g > 0.75 and rng.uniform() < 0.4:
                p = rng.uniform(0, G.length)
            p = float(np.clip(p, 0, G.length))
            sparks.append((n[0] + rng.uniform(0, 0.08), int(np.argmin(np.abs(G.pd[G.path] - p))), rng.uniform(0.6, 1.0)))
    sparks.sort()
    sp_t = np.array([s[0] for s in sparks])
    sp_i = np.array([s[1] for s in sparks], int)                # path index
    sp_a = np.array([s[2] for s in sparks])
    host = smoothstep(T_MULT, T_PRAISE + 1.0, t) * (1 - smoothstep(T_GLORY - 0.8, T_GLORY + 0.3, t))
    host_w = 60.0 + 1300.0 * smoothstep(T_MULT, T_PRAISE + 0.5, t) ** 1.6
    LIFE = 0.55

    for f in range(F):
        tt = t[f]
        tw = 0.85 + 0.15 * twinkle(tt)
        # the night: a dim blue bed, the fields faintly warm; it lifts as the glory comes and stays up after
        lift = smoothstep(T_GLORY - 0.5, T_GLORY + 2.0, tt)
        fr = light(NIGHT, (0.11 + 0.04 * lift) * tw) + light(BED, 0.05)
        fr += light(FIELD, (0.11 + 0.05 * field_u + 0.05 * lift) * fields * tw)
        # the strings' figures before the angel speaks, faint shimmer on the porch and fields
        if recit[f] > 0:
            fr += light(SILVER, 0.04 * recit[f] * np.maximum(shimmer(tt), 0) * (front + 0.5 * fields))
        # the angel
        if angel[f] > 0.002:
            g = np.exp(-(off / (0.35 * half)) ** 2) * front
            fr += light(SILVER, angel[f] * recit[f] * g + 0.08 * angel[f] * recit[f] * front)
        # the multitude: sparks, and a silver haze where they are
        if host[f] > 0:
            fr += light(SILVER, 0.2 * host[f] * np.exp(-(off / host_w[f]) ** 2) * tw)
        if len(sp_t) and tt >= sp_t[0] and tt < T_GLORY + LIFE:
            j0, j1 = np.searchsorted(sp_t, tt - LIFE), np.searchsorted(sp_t, tt, side='right')
            if j1 > j0:
                age = tt - sp_t[j0:j1]
                a = sp_a[j0:j1] * np.exp(-age / 0.22) * smoothstep(0, 0.03, age) * 0.8
                buf = np.zeros(G.N)
                pi = sp_i[j0:j1]
                for dk, w in ((-1, 0.45), (0, 1.0), (1, 0.45)):
                    np.add.at(buf, G.path[np.clip(pi + dk, 0, G.N - 1)], a * w)
                fr += light(SILVER, np.minimum(buf, 1.0))
        # the glory on the far porch
        ig = in_glory[f]
        if ig > 0:
            k = spread[f]
            lvl = (0.45 + 0.35 * s_high[f]) * choir[f] + 0.15
            lvl = lvl * (0.8 + 0.1 * k) + 0.35 * s_hit[f] * (0.7 + 0.15 * k)
            core = 0.75 + 0.25 * np.exp(-(off / (0.6 * half)) ** 2)
            fr += light(GLORY, ig * lvl * core * front)
            if k >= 1:                                          # spilling down the porch runs toward the street
                fr += light(GLORY, ig * (0.7 * lvl) * np.exp(-run_dist / (260.0 + 150 * (k - 1))) * runs)
            if k >= 2:                                          # the whole house
                house = fields + 0.6 * side + runs
                fr += light(GLORY, ig * (0.32 * choir[f] + 0.18 * s_hit[f]) * house)
            # the glint of the first violins' runs
            j = int(np.searchsorted(v1_on, tt, side='right')) - 1
            if j >= 0 and tt - v1_on[j] < 0.6:
                p = pf0 + np.clip((v1_m[j] - 62) / 26.0, 0, 1) * (pf1 - pf0)
                fr += light(SILVER, ig * 0.4 * np.exp(-((d - p) / 14.0) ** 2) * front)
        # the trumpets: gold flares spreading from the middle of the porch, farther the louder the glory
        j = int(np.searchsorted(tr_on, tt, side='right')) - 1
        if j >= 0 and tt - tr_on[j] < 1.2:
            a = tt - tr_on[j]
            k = spread[f]
            reach = (0.6 * half) + a * (300.0 + 900.0 * k)
            ring = np.exp(-((off - min(reach, half + 1600 * (k >= 2) + 300 * (k >= 1))) / (40.0 + 60 * a)) ** 2)
            body = np.exp(-(off / (0.45 * half)) ** 2)
            mask = front if k < 1 else (front + runs if k < 2 else np.ones(G.N))
            amp = (0.5 + 0.12 * k) * np.exp(-a / 0.4) * smoothstep(0, 0.03, a)
            fr += light(GOLD, amp * np.maximum(body * front, 0.8 * ring) * mask)
        # peace on earth: Left and Right warm, low
        pc = peace[f]
        if pc > 0:
            jh = low_hold[f]
            hit = 0.0
            jj = int(np.searchsorted(low_on, tt, side='right')) - 1
            if jj >= 0:
                hit = np.exp(-(tt - low_on[jj]) / 0.6)
            glow = pc * (0.28 + 0.2 * jh + 0.12 * hit) * (0.55 + 0.45 * field_u)
            fr += light(WARM, glow * fields)
            jr = int(np.searchsorted(rock_on, tt, side='right')) - 1
            if jr >= 0 and tt - rock_on[jr] < 0.5:
                a = tt - rock_on[jr]
                wave = np.exp(-((field_u - (0.9 - 0.6 * (jr % 2))) / 0.25) ** 2)
                fr += light(WARM, pc * 0.12 * np.exp(-a / 0.2) * wave * fields)
            fr += light(GLORY, pc * 0.1 * front)                # the porch's afterglow
        # good will towards men: the house settles into warm gold; the last chord holds it
        if good[f] > 0:
            hit = s_hit[f] * (1 - final[f])
            fr += light(GOLD, good[f] * (0.18 + 0.1 * hit + 0.2 * final[f]) * (fields + runs + 0.6 * side))
            fr += light(GOLD, good[f] * (0.25 + 0.15 * hit + 0.25 * final[f]) * front)
            fr += light(GLORY, good[f] * (0.12 + 0.08 * final[f]) * fields)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them; the soprano on flute and oboe from the porch, a harpsichord under the recitative;
    the chorus on strings with oboes and bassoons doubling, the organ joining for the fortissimo; the trumpets from far
    away, coming close for the last glory; glockenspiel sparks for the multitude, from Handel's own violin notes."""
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, _Voice, _load, _fade_out

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pfd = G.pd[G.seg['Porch Front']]
    porch = pan_at(0.5 * (pfd.min() + pfd.max()))
    left = pan_at(float(np.mean(G.pd[G.seg['Left']])))
    right = pan_at(float(np.mean(G.pd[G.seg['Right']])))

    def last(t, dd):
        return dd + HOLD if abs(t + dd - END) < 0.05 else dd

    LV = 1.45
    o = Orchestra(M, level=LV)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            vel = v + (2 if t < T_GLORY else -4)                  # senza ripieni in the recitative, but carrying outdoors
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), vel - 4, pan[p], 0.42)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), vel - 6, pan[p], 0.38)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel - 4, pan[p], 0.42)
            else:
                o.play('cellos', m if m < 60 else m - 12, t, max(dd, 0.15), vel - 2, pan[p], 0.5)
                if t >= T_GLORY:
                    o.play('basses', m - 12 if m >= 48 else m, t, max(dd, 0.2), vel - 10, pan[p], 0.32)
    # the angel: the soprano on flute and oboe, from the porch
    for t, dd, m, v, h, _ in PART['Soprano']:
        o.play('flutes', m, t, max(dd, 0.16), v + 16, porch, 0.95)
        o.play('oboes', m, t, max(dd, 0.16), v + 4, porch, 0.5)
    hp = M.synth('Keys/Digi Harpsi')
    beats = sorted({round(n[0], 3) for n in PART['Bassi'] if n[0] < T_GLORY - 0.1
                    and abs(((n[0] - BAR[3]) / (60 / 72)) % 1) < 0.05})
    notes = []
    for tb in beats:
        for p in ('Bassi', 'Va', 'Vn2'):
            ch = [n for n in PART[p] if abs(n[0] - tb) < 0.02]
            if ch:
                notes.append((tb, ch[0][2] - (12 if p == 'Bassi' else 0), 64 if p == 'Bassi' else 54, 0.3))
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.35, 0.0)
    # the chorus: strings with oboes and bassoons doubling; the organ joins in the fortissimo
    parts = {'S': [('violins', 0, -6, 0.45), ('oboes', 0, -10, 0.3)],
             'A': [('violins', 0, -8, 0.35), ('violas', 0, -8, 0.3)],
             'T': [('violas', 0, -6, 0.42), ('bassoons', 0, -12, 0.25)],
             'B': [('cellos', 0, -6, 0.42), ('basses', -12, -8, 0.36), ('bassoons', 0, -10, 0.3)]}
    pan_of = {'S': 0.5 * porch - 0.15, 'A': 0.5 * porch - 0.05, 'T': 0.5 * porch + 0.05, 'B': 0.5 * porch + 0.15}
    for who in ('S', 'A', 'T', 'B'):
        for t, dd, m, v, h, _ in PART[who]:
            dd = last(t, dd)
            pk = pan_of[who]
            if any(p0 - 0.05 <= t < p1 for p0, p1 in PEACE):    # peace on earth: from the fields
                pk = left if who == 'T' else right
                pk *= 0.6
            for section, tr, dv, g in parts[who]:
                o.play(section, m + tr, t, max(dd, 0.14), v + dv, pk, g)
    class Pipes(_Voice):
        """The VSCO2 pipe organ: samples are numbered, every third key."""

        def __init__(self, pattern, first):
            self.zones = {}
            for path in sorted(glob.glob(os.path.join(VSCO, pattern))):
                self.zones[first + int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', path).group(1))] = path
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.3):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]
            idx = np.arange(int((dur + release) * SR)) * 2 ** ((n - k) / 12)
            idx = idx[idx < a.shape[1] - 1]
            res = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            return _fade_out(res * (vel / 127) ** 1.3, dur, release)

    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.11 * LV / 3.5, reverb=0.45)
    M.bus('pedal', gain=0.15 * LV / 3.5, reverb=0.35)
    for who in ('S', 'A', 'T', 'B'):
        for t, dd, m, v, h, _ in PART[who]:
            if t >= BAR[34] - 0.05 and dd >= 0.3:
                dd = last(t, dd)
                if who == 'B':
                    M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
                else:
                    M.add('organ', man.play(m, v - 6, dd), t - 0.03, 1.0, pan_of[who] * 0.5)
    # the trumpets: far away and reverberant (da lontano e un poco piano), close for the last two glories
    M.bus('far', gain=0.12 * LV * 0.8, reverb=0.7)
    s = o.sus['trumpets']
    for p, g in (('Tr1', 1.0), ('Tr2', 0.8)):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            near = t >= BAR[34] - 0.05
            if near:
                o.play('trumpets', m, t, max(dd * 0.92, 0.14), v - 2, porch + (0.08 if p == 'Tr2' else -0.08), 0.5 * g)
            else:
                vel = int(np.clip(v + (6 if t >= BAR[18] - 0.05 else 10), 1, 127))
                if dd > 1.2:
                    o.hold('far', s, m, t, t + dd, vel, porch, 0.55 * g)
                else:
                    M.add('far', s.play(m, vel, dur=max(dd * 0.92, 0.14), release=0.2), t, 0.55 * g, porch)
    # the multitude: glockenspiel sparks on Handel's violin notes, more and more of them
    rng = np.random.default_rng(12)
    for t, dd, m, v, h, _ in PART['Vn1']:
        if T_MULT - 0.3 <= t < T_GLORY:
            g = np.clip((t - T_MULT) / (T_PRAISE - T_MULT), 0.05, 1.0)
            if rng.uniform() < 0.25 + 0.5 * g:
                o.play('glock', m + 12 if m < 76 else m, t, 0.3, 40 + 30 * g, float(rng.uniform(-0.7, 0.7)), 0.18 + 0.1 * g)
    # a soft cymbal swell as the host appears, and into the fortissimo glory
    o.hit('cymbal swell', T_MULT - 0.6, 60, gain=0.1, pan=porch)
    o.hit('cymbal swell', T_GLORY - 1.5, 70, gain=0.12, pan=porch)
    o.hit('cymbal swell', BAR[34] - 1.4, 84, gain=0.16, pan=porch)
