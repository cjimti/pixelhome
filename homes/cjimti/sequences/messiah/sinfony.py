"""Sinfony: the French overture, the Grave's heavy dotted pulses in deep blue, then the fugue's voices of light.

The Grave. The house is deep blue, and every long dotted note of the strings sends a heavy pulse of brighter blue out
from the back of the porch along the whole roofline to both ends; each short upbeat that snaps after it is a quick
glint on Porch Front. The pulses are heaviest where the bass and the first violins climb, and on the second-time chord
the pulses stop and the house holds its breath, dim, waiting.

Then the fugue, and each string part enters as its own light, one run at a time. The first violins alone: the
subject in white-gold on Porch Front, the far light, every note a bright point placed along the run by its pitch. The
second violins answer in silver on Left; the violas and the basses come in together, the violas in gold on Right and
the basses in amber on both porch runs, the way between, until all four voices run at once. At the first cadence the
music leaps to the fugue's last entry, fortissimo: one full-house flash on the chord before it, Side joins in gold,
and the four voices run brighter than before. The Più lento gathers the points into steady light, and the last
E minor chord settles: white-gold on the porch, the wings deep blue, the house still.

The music is Handel's own: Messiah No. 1, the Grave's bars 1-4 and 9-11 with its second-time chord (bar 12), the
fugue's exposition, bars 13-25 to the first cadence, and its end from the fortissimo entry at the letter F, bars
86-97 with the Più lento, transcribed from Prout's full score (Novello, 1902) into sinfony.musicxml and timed by
scripts/score_excerpt.py at Prout's marks, Grave crotchet 60 and Allegro moderato 116, the Più lento at 80. Strings
only, as Handel scored it, with a harpsichord continuo; the last chord is held.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS01'
TITLE = 'Sinfony'
KIND = 'show'
DESCRIPTION = ("The overture: the Grave's heavy dotted pulses roll along the house in deep blue, then the fugue's four "
               "voices enter one run at a time, each string part its own light.")
VOICEOVER = ("Messiah. Handel wrote it in twenty-four days, and its first performance raised money for prisoners "
             "and hospitals.")

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.5                                  # the last chord held
D = round(END + HOLD, 2)
PARTS = ('Vn1', 'Vn2', 'Va', 'Bassi')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in PARTS}
ONSET = {p: np.array([n[0] for n in PART[p]]) for p in PARTS}
T_CHORD = BAR[12]                           # the Grave's second-time chord
T_FUGUE = BAR[13]
T_LAST = BAR[86]                            # the fortissimo entry at the letter F
T_TUTTI = BAR[87]
T_LENTO = BAR[95]
T_FINAL = BAR[97]
ENTRY = {p: float(ONSET[p][ONSET[p] >= T_FUGUE - 0.01][0]) for p in PARTS}

NIGHT = hexc('#0a1450')
BLUE = hexc('#1f44d8')
COLOR = {'Vn1': hexc('#fff2c8'), 'Vn2': hexc('#b0ccff'), 'Va': hexc('#ffb020'), 'Bassi': hexc('#e08a20')}
RUNS = {'Vn1': ('Porch Front',), 'Vn2': ('Left',), 'Va': ('Right',), 'Bassi': ('Porch Left', 'Porch Right')}
GOLD = hexc('#ffb020')
WHITEGOLD = hexc('#fff2c8')


def grave_events():
    """The Grave's rhythm: (t, kind, weight), kind 'long' for the dotted notes, 'short' for the snaps after them."""
    ev = {}
    for p in PARTS:
        for t, d, m, v, h, _ in PART[p]:
            if t >= T_CHORD - 0.01:
                continue
            k = round(t, 2)
            kind = 'long' if d > 0.6 else 'short'
            w = (1.0 if p in ('Vn1', 'Bassi') else 0.6) * (0.7 + 0.3 * (m - 40) / 40)
            if k not in ev or (kind == 'long' and ev[k][0] == 'short'):
                ev[k] = (kind, w)
            elif ev[k][0] == kind:
                ev[k] = (kind, max(ev[k][1], w))
    return sorted((t, k, w) for t, (k, w) in ev.items())


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    front = seg == 'Porch Front'
    pf = G.pd[G.seg['Porch Front']]
    mid = 0.5 * (pf.min() + pf.max())
    far = np.abs(d - mid)                                   # distance from the back of the porch, along the path
    reach = far.max()
    events = grave_events()
    shimmer = Flicker(rng, G.N, 0.2, 0.7)
    # each voice's run: where its pixels are, and a 0..1 place along it for pitch
    run = {}
    for p, names in RUNS.items():
        mask = np.isin(seg, names)
        u = np.zeros(G.N)
        for nm in names:
            idx = G.seg[nm]
            s = G.pd[idx]
            u[idx] = (s - s.min()) / (s.max() - s.min())
            if nm == 'Porch Right':                                  # both porch runs: low notes at the street end
                u[idx] = 1 - u[idx]
        lo = min(n[2] for n in PART[p] if n[0] >= T_FUGUE - 0.01)
        hi = max(n[2] for n in PART[p] if n[0] >= T_FUGUE - 0.01)
        length = sum(float(G.pd[G.seg[nm]].max() - G.pd[G.seg[nm]].min()) for nm in names) / len(names)
        run[p] = (mask, u, lo, hi, length)
    for f in range(F):
        t = f * DT
        fugue = smoothstep(T_FUGUE - 1.0, T_FUGUE + 0.5, t)
        last = smoothstep(T_LAST - 0.1, T_LAST + 0.3, t)
        settle = smoothstep(T_LENTO, T_FINAL + 1.0, t)
        # the bed: deep blue, darker under the fugue's voices, brightening a little for the last entry
        bed = (0.2 - 0.08 * fugue + 0.06 * last) * (0.9 + 0.1 * shimmer(t))
        fr = light(NIGHT, bed + 0.05 * (1 - fugue))
        # the Grave: every long dotted note a heavy pulse from the back of the porch out along the house; every snap a
        # quick glint on Porch Front
        if t < T_FUGUE + 1.5:
            wave = np.zeros(G.N)
            snap = 0.0
            for t0, kind, w in events:
                a = t - t0
                if a < 0:
                    break
                if kind == 'long' and a < 3.2:
                    r = a / 2.0 * reach
                    wave += w * np.exp(-((far - r) / 380.0) ** 2) * np.exp(-a / 1.6) + 0.4 * w * np.exp(-a / 0.4)
                elif kind == 'short' and a < 0.5:
                    snap = max(snap, w * np.exp(-a / 0.09))
            hold = smoothstep(T_CHORD - 0.2, T_CHORD + 1.0, t) * (1 - fugue)       # the second-time chord: waiting
            fr += light(BLUE, (0.8 * np.minimum(wave, 1.2) * (1 - 0.6 * hold) + 0.12 * hold) * (1 - fugue))
            fr += light(WHITEGOLD, 0.7 * snap * front * (1 - fugue))
            fr += light(WHITEGOLD, 0.18 * hold * np.exp(-((d - mid) / 60.0) ** 2) * front)
        # the fugue: each voice on its own run, a base glow once it has entered and a bright point on every note
        if t >= T_FUGUE - 0.5:
            for p in PARTS:
                mask, u, lo, hi, length = run[p]
                if t < ENTRY[p] - 0.05:
                    continue
                woke = smoothstep(ENTRY[p] - 0.05, ENTRY[p] + 0.4, t)
                i = int(np.searchsorted(ONSET[p], t, side='right')) - 1
                n = PART[p][i]
                a = t - n[0]
                sounding = a < n[1] + 0.05
                place = 0.08 + 0.84 * (n[2] - lo) / max(1, hi - lo)
                if i > 0 and PART[p][i - 1][0] >= ENTRY[p] - 0.01:          # glide from the last note's place
                    pp = 0.08 + 0.84 * (PART[p][i - 1][2] - lo) / max(1, hi - lo)
                    place = pp + (place - pp) * smoothstep(0.0, 0.08, a)
                width = 60.0 / length
                spot = np.exp(-((u - place) / width) ** 2) * mask
                hit = np.exp(-a / 0.14) if sounding else 0.0
                lv = (0.5 + 0.5 * hit) * (1.0 if sounding else np.exp(-(a - n[1]) / 0.3))
                strong = 1.0 + 0.25 * last
                base = (0.3 + 0.1 * last) * woke
                calm = 1 - settle
                fr += light(COLOR[p], (base * (1 - 0.3 * settle) + 0.25 * settle) * mask)
                fr += light(COLOR[p], 0.8 * strong * lv * woke * spot * calm)
                fr += light(COLOR[p], 0.2 * hit * woke * mask * calm)
        # the fortissimo entry: one full-house flash on its first chord; Side joins in gold
        if t >= T_LAST - 0.1:
            a = t - T_LAST
            fr += light(WHITEGOLD, 0.65 * np.exp(-max(a, 0) / 0.25) * (a >= 0))
            fr += light(GOLD, (0.24 * last * (1 - 0.4 * settle)) * side)
        # the last chord: white-gold on the porch, the wings deep blue, still
        if settle > 0:
            porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
            wings = np.isin(seg, ['Left', 'Right'])
            fr += light(WHITEGOLD, 0.5 * settle * porch) + light(BLUE, 0.4 * settle * wings)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The strings as Handel scored them, panned to their runs in the fugue: first violins from the porch, seconds
    left, violas right, basses from the porch runs; a harpsichord continuo; the last chord held."""
    o = Orchestra(M, level=2.9)
    pan = {'Vn1': 0.0, 'Vn2': -0.5, 'Va': 0.5, 'Bassi': 0.12}
    for p in PARTS:
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            grave = t < T_FUGUE - 0.01
            vel = v - (4 if dd < 0.2 else 0) - (0 if grave or t >= T_LAST - 0.01 else 4)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), vel, pan[p], 0.5)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), vel - 2, pan[p], 0.45)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel, pan[p], 0.5)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 8, pan[p], 0.35)
    # the continuo: the bass line, and in the Grave and the Più lento a chord on each beat from the parts sounding
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(96, v)), min(dd, 0.35)) for t, dd, m, v, h, _ in PART['Bassi']]
    upper = PART['Vn2'] + PART['Va']
    for t0, t1, beat in ((0.0, T_FUGUE - 0.1, 1.0), (T_LENTO, T_FINAL - 0.1, 0.75)):
        tb = t0
        while tb < t1:
            ch = sorted({n[2] for n in upper if n[0] <= tb + 0.02 < n[0] + n[1]})
            notes += [(tb, m, 62, 0.4) for m in ch if 52 <= m <= 76]
            tb += beat
    notes += [(END - 3.0 + 0.06 * i, m, 64, 3.0 + HOLD - 0.3) for i, m in enumerate((52, 55, 59, 64))]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.45, 0.0)
