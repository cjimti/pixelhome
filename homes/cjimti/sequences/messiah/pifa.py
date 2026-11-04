"""Pifa: the Pastoral Symphony, a siciliano over a drone, night fields with small soft lights swaying.

Night over the fields. Left and Right are the fields, a deep blue-green that stirs slowly like grass in a light wind,
and on each of them a handful of small soft lights, the shepherds' lanterns among the flock, sway gently to the
siciliano's lilt, back and forth once a bar. The porch holds the drone: a low warm glow on the three porch
runs that swells softly each time the basses' long note changes, warm on the C drone, a little brighter when it moves
to G. The tune plays over the fields: each note of the first violins brightens a lantern on Left, the one its pitch
points to, each note of the seconds one on Right.

In the middle section, over the G drone, the lanterns swell with the crescendo and the swaying widens; when the music
turns to the minor and fades, they dim and sway close, and the drone moves on. At the close the music goes very
quiet, the lanterns settle and stop swaying, and the drone glows on, warm, under a still field: the calmest scene of
the set.

The music is Handel's own: Messiah No. 13, the opening phrase over the C drone (bars 1-4), the middle section over
the G drone to its half close (bars 12 and 14-21; bar 13, a repeat of 14, left out), and the da capo's last two bars
(31-32) with their fermata, transcribed from Prout's full score (Novello, 1902) into pifa.musicxml and timed by
scripts/score_excerpt.py at Prout's Larghetto, quaver 132. Strings only, as Handel scored it, the violas doubling the
violins an octave below as Prout prints them, the drone on cellos and basses.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, smooth_noise, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS10'
TITLE = 'Pifa'
KIND = 'show'
DESCRIPTION = ("The Pastoral Symphony: night fields on Left and Right, small soft lanterns swaying to the siciliano, "
               "and a low warm drone glowing on the porch.")
VOICEOVER = ('Handel called this music Pifa, after the shepherds who came down from the hills to play their pipes '
             'at Christmas.')

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.0
D = round(END + HOLD, 2)
PARTS = ('Vn1', 'Vn2', 'Va', 'Bassi')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in PARTS}
ONSET = {p: np.array([n[0] for n in PART[p]]) for p in ('Vn1', 'Vn2')}
BASS = PART['Bassi']
DRONE = [n for n in BASS if n[1] >= 1.0]                        # the long drone notes, not the bass's moving quavers
BEAT = BAR[2] - BAR[1]                                          # one 12/8 bar
T_MID = BAR[12]                                                 # the middle section, over the G drone
T_CRESC, T_PIU = BAR[15], BAR[16]
T_MINOR, T_DIM = BAR[17], BAR[19]
T_CLOSE = BAR[31]
LANTERNS = (0.12, 0.27, 0.41, 0.58, 0.72, 0.88)                 # places along each field, from the porch outward

FIELD = hexc('#0c2a3a')
GRASS = hexc('#14402a')
NIGHT = hexc('#0a1440')
LANTERN = hexc('#ffe2b0')
DRONE_C = hexc('#ff8a30')


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    front = seg == 'Porch Front'
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    fields = {}
    for nm in ('Left', 'Right'):
        idx = G.seg[nm]
        s = G.pd[idx]
        lo, hi = float(s.min()), float(s.max())
        # from the porch outward: Left runs toward the porch, Right away from it
        if nm == 'Left':
            place = (lambda u, lo=lo, hi=hi: hi - u * (hi - lo))
        else:
            place = (lambda u, lo=lo, hi=hi: lo + u * (hi - lo))
        fields[nm] = (seg == nm, place)
    wind = [smooth_noise(rng, d, 90.0) for _ in range(2)]
    phase = rng.uniform(0, 2 * np.pi, (2, len(LANTERNS)))
    sway_w = rng.uniform(0.8, 1.2, (2, len(LANTERNS)))
    lo_p = {p: min(n[2] for n in PART[p]) for p in ('Vn1', 'Vn2')}
    hi_p = {p: max(n[2] for n in PART[p]) for p in ('Vn1', 'Vn2')}
    d_on = np.array([n[0] for n in DRONE])
    for f in range(F):
        t = f * DT
        cresc = smoothstep(T_CRESC, T_PIU + BEAT, t) * (1 - smoothstep(T_MINOR, T_DIM, t))
        dim = smoothstep(T_MINOR, T_DIM + BEAT, t) * (1 - smoothstep(T_CLOSE - 1.0, T_CLOSE, t))
        rest = smoothstep(T_CLOSE, END, t)
        # the fields: deep blue-green, stirring slowly like grass in a light wind
        u = 0.5 + 0.5 * (np.cos(2 * np.pi * t / 23.0) * wind[0] + np.sin(2 * np.pi * t / 31.0) * wind[1])
        fld = (0.26 + 0.08 * u + 0.04 * cresc) * (1 - 0.15 * rest)
        fr = light(FIELD, fld * ~(porch | side)) + light(GRASS, 0.75 * fld * u * ~(porch | side))
        fr += light(NIGHT, 0.14 * side)
        # the drone: a low warm glow on the porch, swelling softly each time the long note changes
        k = int(np.searchsorted(d_on, t, side='right')) - 1
        if k >= 0:
            n = DRONE[k]
            a = t - n[0]
            swell = 0.06 * smoothstep(0.0, 1.2, a) * np.exp(-max(0.0, a - 1.2) / 3.0)
            bright = 0.27 + 0.05 * (n[2] - 48) / 7 + swell + 0.06 * cresc - 0.04 * dim
        else:
            bright = 0.24
        fr += light(DRONE_C, bright * (porch & ~front) + 0.8 * bright * front)
        # the lanterns: small soft lights on each field, swaying to the lilt, each melody note brightening one
        width = 1.0 + 0.5 * cresc - 0.4 * dim - 0.8 * rest
        for s_i, (nm, p) in enumerate((('Left', 'Vn1'), ('Right', 'Vn2'))):
            mask, place = fields[nm]
            i = int(np.searchsorted(ONSET[p], t, side='right')) - 1
            near, hit = -1, 0.0
            if i >= 0:
                n = PART[p][i]
                a = t - n[0]
                hit = np.exp(-a / 0.7)
                near = int(round((1 - (n[2] - lo_p[p]) / max(1, hi_p[p] - lo_p[p])) * (len(LANTERNS) - 1)))
            for j, c in enumerate(LANTERNS):
                sway = 12.0 * width * sway_w[s_i, j] * np.sin(2 * np.pi * t / BEAT + phase[s_i, j])
                x = place(c) + sway
                lv = 0.42 + 0.12 * cresc - 0.08 * dim + (0.22 * hit if j == near else 0.04 * hit)
                fr += light(LANTERN, lv * np.exp(-((d - x) / 9.0) ** 2) * mask)
        if t > END:
            fr = fr * (1 - 0.1 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The strings as Handel scored them, quietly: first violins and the upper violas left with the Left field,
    seconds and the lower violas right, the drone on cellos and basses from the porch."""
    o = Orchestra(M, level=5.0)
    for p in PARTS:
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (6 if dd < 0.2 else 2)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.16), vel, -0.4, 0.45)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.16), vel - 3, 0.4, 0.42)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.16), vel - 4, -0.25 if h == 0 else 0.25, 0.35)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.2), vel, 0.0, 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.25), vel - 8, 0.0, 0.34)
