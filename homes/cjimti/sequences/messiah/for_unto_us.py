"""For Unto Us a Child Is Born: light running figures, then the five great names, each a full blaze on its own run.

The violins' last bars of the ritornello run as quick gold lights along the wings. The sopranos sing "For unto us a
Child is born" alone, and a soft white-gold glow grows in the middle of Porch Front, the far light, a little brighter
with every note, while the strings' answering figures hop gold along Left and Right.

"And the government shall be upon His shoulder": the sopranos' line on Porch Front, the altos and basses joining on
the porch runs, the whole chorus building, the house warming toward gold. On "and His Name shall be called" the violins
rush upward and a gold streak runs the length of the house from Left to Right.

Then the five names, each a full white-gold blaze on its own run, left to right: "Wonderful" on Left, "Counsellor"
on Porch Left, "The Mighty God" on Porch Front, "The Everlasting Father" on Porch Right, "The Prince of Peace" on
Right. Each blaze settles to a glow that stays, so by the Prince of Peace the whole front of the house is lit, while
the violins' running semiquavers chase a gold light back and forth across it.

The names come back at the end, and the same runs answer them in the same order, Left round to Right, with
"The Everlasting Father, the Prince of Peace" answered once more by Porch Right and Right at the cadence. In the
strings' last bars the whole house, Side included, settles into one warm gold and holds.

The music is Handel's own: Messiah No. 12, the ritornello's last bar and the sopranos' first "For unto us a Child is
born, unto us a Son is given" (bars 6-10), "upon His shoulder" to the first names (29-37), the last names to the
final cadence (83-91) and the strings' last two bars (98-99), transcribed from Prout's full score (Novello, 1902)
into for_unto_us.musicxml and timed by scripts/score_excerpt.py at Prout's Andante allegro. Handel's strings and
the chorus; the chorus sung on strings with oboes and a bassoon doubling, the organ under the names.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS09'
TITLE = 'For Unto Us a Child Is Born'
KIND = 'show'
DESCRIPTION = ("Light running figures for \"unto us a Child is born\", then the five great names, each a full blaze "
               "on its own run, Wonderful on Left round to the Prince of Peace on Right, and the same runs answer "
               "every time the names return.")
VOICEOVER = 'For unto us a Child is born, unto us a Son is given.'

EX = excerpt(__file__)
BAR = {}
for _m, _t in EX['bars']:
    BAR.setdefault(int(_m), _t)
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
VOICES = ('S', 'A', 'T', 'B')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in VOICES + ('Vn1', 'Vn2', 'Va', 'Bassi')}
ON = {p: np.array([n[0] for n in PART[p]]) for p in PART}
BEAT = BAR[7] - BAR[6]
BEAT = BEAT / 4
SEG = EX['segments']
T_SOP = BAR[7]                              # "For unto us a Child is born"
T_GOV = SEG[1]['start']                     # "upon His shoulder"
T_RUSH = BAR[32] + 2 * BEAT                 # the violins rush up: "and His Name shall be called"
T_GAP = BAR[37] + 3 * BEAT                  # the first names are over
T_GOV2 = SEG[2]['start']
T_CODA = SEG[3]['start']
RUNS = ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')
# the names: (time of the name's first strong syllable, its run, the beat of its last syllable)
NAMES = [(BAR[33], 0), (BAR[34], 1), (BAR[35] + BEAT, 2), (BAR[36], 3), (BAR[37], 4),
         (BAR[85], 0), (BAR[86], 1), (BAR[87] + BEAT, 2), (BAR[88], 3), (BAR[89], 4),
         (BAR[90], 3), (BAR[91], 4)]
SURGE = [BAR[35] + 2 * BEAT, BAR[87] + 2 * BEAT]  # "God"

NIGHT = hexc('#0a1030')
GLORY = hexc('#fff2c8')                     # the chorus
GOLD = hexc('#ffb020')
WHITE = hexc('#ffffff')


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    seg = G.seg_of
    d = G.pd
    run = {s: (seg == s).astype(float) for s in RUNS}
    side = (seg == 'Side').astype(float)
    front = run['Porch Front']
    wings = run['Left'] + run['Right']
    porch = run['Porch Left'] + run['Porch Right']
    pf = G.pd[G.seg['Porch Front']]
    mid = 0.5 * (pf.min() + pf.max())
    half = 0.5 * (pf.max() - pf.min())
    d0, d1 = float(G.pd[G.seg['Left']].min()), float(G.length)
    shimmer = Flicker(rng, G.N, 0.4, 1.5)
    # the violins' running figure: a gold light chasing back and forth, one step a note
    v1 = PART['Vn1']
    chase = np.zeros(len(v1))
    x, s = 0.1, 1
    for k in range(1, len(v1)):
        x += s * (0.012 + 0.004 * abs(v1[k][2] - v1[k - 1][2]))
        if x > 1 or x < 0:
            s = -s
            x = 2 - x if x > 1 else -x
        chase[k] = x
    for f in range(F):
        t = f * DT
        fr = light(NIGHT, (0.07 + 0.02 * shimmer(t)) * (1 - side * 0.3))
        # the house warms as the chorus builds, and cools in the gap before the names return
        warm = (smoothstep(T_GOV, BAR[33], t) * (1 - smoothstep(T_GAP, T_GOV2, t)) + smoothstep(T_GOV2, BAR[85], t))
        fr += light(GOLD, 0.06 * warm * (1 - side))
        # the sopranos' first line: a glow growing in the middle of Porch Front with every note
        if T_SOP - 0.2 <= t < T_GOV + 0.5:
            k = int(np.searchsorted(ON['S'], t, side='right')) - 1
            if k >= 0:
                n = PART['S'][k]
                a = t - n[0]
                grow = smoothstep(T_SOP, T_GOV - 1.0, t)
                lvl = (0.25 + 0.3 * grow) * (0.7 + 0.3 * np.exp(-a / 0.25)) * (1 if a < n[1] + 0.2 else
                                                                                 np.exp(-(a - n[1] - 0.2) / 0.5))
                w = 0.35 + 0.45 * grow
                fr += light(GLORY, lvl * np.exp(-(np.abs(d - mid) / half / w) ** 2) * front)
        # the government: the voices on the porch, building
        if T_GOV <= t < BAR[33]:
            for p, where, wt in (('S', front, 1.0), ('A', run['Porch Left'], 0.8), ('B', run['Porch Right'], 0.8),
                                 ('T', porch, 0.5)):
                k = int(np.searchsorted(ON[p], t, side='right')) - 1
                if k >= 0 and ON[p][k] >= T_GOV - 0.01:
                    n = PART[p][k]
                    a = t - n[0]
                    env = (0.55 + 0.45 * np.exp(-a / 0.2)) if a < n[1] else 0.55 * np.exp(-(a - n[1]) / 0.3)
                    fr += light(GLORY, 0.42 * wt * env * where)
        # the strings' figures: quick gold lights hopping on the wings (the opening) or chasing across the house
        k = int(np.searchsorted(ON['Vn1'], t, side='right')) - 1
        if k >= 0:
            n = v1[k]
            a = t - n[0]
            if t < T_GOV:
                pos = (n[2] - 62) / 26
                cl = float(G.pd[G.seg['Left']].min()) + pos * 380
                cr = float(G.pd[G.seg['Right']].max()) - pos * 450
                g = 0.6 * np.exp(-a / 0.16)
                fr += light(GOLD, g * (np.exp(-((d - cl) / 18) ** 2) + np.exp(-((d - cr) / 18) ** 2)) * wings)
            else:
                prev = chase[max(0, k - 1)]
                x = prev + (chase[k] - prev) * min(1.0, a / 0.05)
                c = d0 + x * (d1 - d0)
                g = 0.7 * (0.6 + 0.4 * np.exp(-a / 0.1)) * (a < n[1] + 0.15)
                fr += light(GOLD, g * np.exp(-((d - c) / 22) ** 2) * (1 - side))
        # the rush: a gold streak the length of the house
        a = t - T_RUSH
        if 0 <= a < 2.2:
            c = d0 + (d1 - d0) * min(1.0, a / 1.5)
            fr += light(GOLD, 0.7 * np.exp(-((d - c) / 40) ** 2) * (1 - side) * (a < 1.6))
            fr += light(GOLD, 0.2 * smoothstep(c + 10, c - 200, d) * np.exp(-a / 1.0) * (1 - side))
        # the names: a full blaze on each run, settling to a glow that stays until the names are done
        for i, (tn, r) in enumerate(NAMES):
            a = t - tn
            if a < -0.03:
                continue
            first = i < 5
            gone = T_GAP if first else D + 1
            fade = 1 - smoothstep(gone, gone + 1.6, t) if first else 1.0
            later = [b for b, rr in NAMES[i + 1:] if rr == r and (b < T_GAP) == first]
            if later and t >= later[0] - 0.03:
                continue                    # a later blaze on the same run takes over
            blaze = 0.95 * np.exp(-a / 0.45) + 0.32
            core = np.exp(-a / 0.12)
            fr += light(GLORY, blaze * fade * run[RUNS[r]]) + light(WHITE, 0.35 * core * fade * run[RUNS[r]])
        for ts in SURGE:
            a = t - ts
            if 0 <= a < 1.0:
                fr += light(WHITE, 0.3 * np.exp(-a / 0.2) * front)
        # the close: the whole house settles into one warm gold, Side included
        if t >= BAR[91]:
            settle = smoothstep(BAR[91], T_CODA + 2.0, t)
            fr = fr * (1 - 0.35 * settle) + light(GOLD, 0.32 * settle) + light(GLORY, 0.12 * settle)
            if t > END:
                fr = fr * (1 - 0.15 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Handel's strings as written, first violins left to basses right; the chorus on strings with oboes doubling the
    upper voices and a bassoon the bass; the organ under the names and the close; each name struck with a timpani
    stroke and panned to its run."""
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, _Voice, _load, _fade_out

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

    x = G.pos[:, 0]
    x0, x1 = x.min(), x.max()

    def pan_of(s):
        return float(0.8 * (2 * (x[G.seg[s]].mean() - x0) / (x1 - x0) - 1))
    o = Orchestra(M, level=2.05)

    def last(t, dd):
        return dd + HOLD if abs(t + dd - END) < 0.05 else dd
    span = {'Vn1': -0.45, 'Vn2': -0.2, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            vel = v - 8 - (4 if dd < 0.2 else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.1), vel, span[p], 0.36)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.1), vel - 2, span[p], 0.32)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.1), vel, span[p], 0.36)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.12), vel + 2, span[p], 0.45)
                o.play('basses', m - 12 if m >= 48 else m, t, max(dd, 0.15), vel - 6, span[p], 0.35)
    vpan = {'S': 0.0, 'A': pan_of('Porch Left'), 'T': 0.0, 'B': pan_of('Porch Right')}
    sec = {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -10, 0.3)],
           'A': [('violins', 0, -6, 0.42), ('oboes', 0, -14, 0.2)],
           'T': [('violas', 0, -2, 0.48), ('cellos', 0, -10, 0.22)],
           'B': [('cellos', 0, -2, 0.48), ('bassoons', 0, -8, 0.32), ('basses', -12, -10, 0.28)]}

    def name_pan(t):
        """Under the names, the chorus sounds from the run that is blazing."""
        cur = None
        for tn, r in NAMES:
            if tn - 0.6 <= t:
                cur = r
        if cur is None or not (BAR[33] - 0.1 <= t < T_GAP or BAR[85] - 0.1 <= t < BAR[92]):
            return None
        return pan_of(RUNS[cur]) * 0.7
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            np_ = name_pan(t)
            for s, tr, dv, g in sec[p]:
                o.play(s, m + tr, t, max(dd * 0.97, 0.11), v + dv, vpan[p] if np_ is None else np_, g)
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.06, reverb=0.45)
    M.bus('pedal', gain=0.084, reverb=0.35)
    for p in VOICES:
        for t, dd, m, v, h, _ in PART[p]:
            if BAR[33] - 0.05 <= t < T_GAP or t >= BAR[85] - 0.05:
                dd = last(t, dd)
                if p == 'B':
                    M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
                else:
                    M.add('organ', man.play(m, v - 10, dd), t - 0.03, 1.0, 0.0)
    # a production's touch: a timpani stroke with each name, from its run; a cymbal swell into each first name
    for tn, r in NAMES:
        o.hit('timpani', tn, 100, pitch=-5 if r % 2 else 0, gain=0.24, pan=pan_of(RUNS[r]) * 0.6)
    for tw in (BAR[33], BAR[85]):
        o.hit('cymbal swell', tw - 1.3, 76, gain=0.14, pan=0.0)
    o.hit('timpani roll', BAR[99] - 0.1, 70, pitch=0, gain=0.16, pan=0.1)
