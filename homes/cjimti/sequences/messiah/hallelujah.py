"""Hallelujah: the set's finale, the whole house answering the chorus, the sopranos climbing round it, the grand pause.

The first Hallelujahs are full-house bursts of white-gold, one on each strong beat where the chorus strikes, short and
falling back to a warm floor between, with every syllable a smaller flash on the far porch, so the house pulses with
the words without strobing. "For the Lord God omnipotent reigneth", which Handel sets with everyone in unison, is one
steady line: the whole roofline lit evenly, rising and falling with the single tune, dipping with its octave drop on
"Om-". Then the trumpets and timpani enter on the answering Hallelujahs: gold flares from Porch Front, a low amber
thump at the ends of the house on each drum stroke.

"The kingdom of this world" is hushed: the house sinks to a dim blue with a faint warm line, and through "is become"
the warmth swells back. "King of Kings": the sopranos climb on held notes while everyone else answers "for ever and
ever, Hallelujah", and each held step lights the next run of the house and keeps it lit, climbing from Left round
through Porch Left, Porch Front and Porch Right to Right, the answers shimmering over what is already lit, the trumpets
flaring gold on the porch.

The last Hallelujahs burst again, and then Handel's grand pause: the house holds still and dim, nothing moving, for the
whole length of the silence. The Adagio "Hal-le-lu-jah" brightens with each syllable, and the final chord lands at full
warm gold and holds.

The music is Handel's own: Messiah No. 44, bars 4-7, 12-14 and 16, 33-37, 51-54, 57-60 and 63-69 (the three held steps
of "King of Kings" and the fortissimo "and Lord of Lords") and 90-94, transcribed from Prout's full score (Novello,
1902) into hallelujah.musicxml and timed by scripts/score_excerpt.py at crotchet 84 (Prout marks 72; a little quicker
to fit), the grand pause held 1.5 s longer and the last Hallelujah taken Adagio as Handel's autograph marks it.
Strings, voices, two trumpets and timpani as Handel scored them; the chorus on strings with oboes and bassoons
doubling, and the organ under the chorus throughout.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS15'
TITLE = 'Hallelujah'
KIND = 'show'
DESCRIPTION = ("The finale: full-house bursts on every Hallelujah, the unison \"For the Lord God omnipotent reigneth\" "
               "as one steady line, the sopranos' King of Kings climbing round the house run by run, and after Handel's "
               "grand pause the last chord in full warm gold.")
VOICEOVER = 'Hallelujah.'

EX = excerpt(__file__)
BAR = {}
for m, t in EX['bars']:
    BAR.setdefault(int(m), t)
SEG = EX['segments']
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p)
        for p in ('S', 'A', 'T', 'B', 'Tr1', 'Tr2', 'Timp', 'Vn1', 'Vn2', 'Va', 'Bassi')}
CHORUS = PART['S'] + PART['A'] + PART['T'] + PART['B']


def seg_start(m):
    return next(s['start'] for s in SEG if abs(s['measures'][0] - m) < 0.01)


def seg_end(m):
    return next(s['start'] + s['seconds'] for s in SEG if abs(s['measures'][0] - m) < 0.01)


T_UNISON, T_UNISON_END = BAR[12], BAR[14]
T_KINGDOM, T_KINGDOM_END = seg_start(33.75), seg_end(33.75)
T_BECOME = BAR[36]
# the held steps of King of Kings, each lighting the next run
STEPS = [seg_start(51.5), seg_start(57.5), seg_start(63.5), BAR[67], BAR[68]]
RUNS = ['Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']
T_KINGS_END = seg_end(63.5)
_rests = [(PART['S'][i][0] + PART['S'][i][1], PART['S'][i + 1][0]) for i in range(len(PART['S']) - 1)]
T_PAUSE, T_PAUSE_END = max(_rests, key=lambda r: r[1] - r[0])        # the grand pause: the longest silence
T_LAST = PART['S'][-1][0]                                             # the final chord
HALLELUJAHS = [(0.0, T_UNISON), (T_UNISON_END - 0.4, T_KINGDOM), (seg_start(90.25), T_PAUSE)]

GLORY = hexc('#fff2c8')                            # the chorus, the whole house
GOLD = hexc('#ffd040')                             # the trumpets
WARM = hexc('#ffb040')                             # warm gold
AMBER = hexc('#e08a20')
NIGHT = hexc('#14204a')
BED = hexc('#06081a')


def onsets(notes):
    return np.array(sorted({round(n[0], 3) for n in notes}))


def burst(t, ons, tau, attack=0.03):
    e = np.zeros_like(t)
    for o in ons:
        a = t - o
        e = np.maximum(e, np.where(a >= 0, smoothstep(0, attack, a) * np.exp(-np.maximum(a, 0) / tau), 0))
    return e


def sounding(t, notes, release=0.25):
    e = np.zeros_like(t)
    for n in notes:
        a = t - n[0]
        e = np.maximum(e, np.where(a >= 0, np.where(a < n[1], 1.0, np.exp(-(a - n[1]) / release)), 0))
    return e


def in_spans(t, spans):
    return any(a <= t < b for a, b in spans)


def render(G, seed=15):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    t = np.arange(F) * DT
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    front = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    pf = G.pd[G.seg['Porch Front']]
    mid, half = 0.5 * (pf.min() + pf.max()), 0.5 * (pf.max() - pf.min())
    off = np.abs(d - mid)
    ends = np.exp(-np.minimum(d, G.length - d) / 120.0)            # the two free ends of the house
    run_u = np.zeros(G.N)                                            # 0..1 along each run, in path order
    for name in RUNS + ['Side']:
        idx = G.seg[name]
        a, b = G.pd[idx].min(), G.pd[idx].max()
        run_u[idx] = (G.pd[idx] - a) / (b - a)
    shimmer = Flicker(rng, G.N, 2.0, 6.0)
    breathe = Flicker(rng, G.N, 0.1, 0.4)

    s_notes = PART['S']
    s_on = onsets(s_notes)
    # full-house bursts: the chorus's strokes on the strong beats (one and three), in the Hallelujah sections
    beat = 60 / 84
    strong = []
    for o in s_on:
        if not any(a <= o < b for a, b in HALLELUJAHS):
            continue
        nxt = min([tb for tb in BAR.values() if tb > o + 1e-3] or [o + 4 * beat])
        pos = (o - (nxt - 4 * beat)) / beat                          # beat position in its bar
        if min(abs(pos - 0), abs(pos - 2)) < 0.05:
            strong.append(o)
    strong = np.array(sorted(strong))
    full = burst(t, strong, 0.45)
    syl = burst(t, s_on, 0.18)
    choir = sounding(t, CHORUS, 0.3)
    tr_on = onsets(PART['Tr1'] + PART['Tr2'])
    tr = burst(t, tr_on, 0.3)
    ti = burst(t, onsets(PART['Timp']), 0.22)
    s_pitch = np.zeros(F)
    for n in s_notes:
        s_pitch = np.where(t >= n[0] - 0.02, n[2], s_pitch)
    answers = onsets([n for n in PART['T'] + PART['B'] if STEPS[0] <= n[0] < T_KINGS_END])
    ans = burst(t, answers, 0.2)
    adagio = onsets([n for n in s_notes if n[0] >= T_PAUSE_END - 0.05])

    for f in range(F):
        tt = t[f]
        fr = np.zeros((G.N, 3))
        hal = any(a <= tt < b + 0.3 for a, b in HALLELUJAHS)
        if hal and not (T_PAUSE - 0.05 <= tt):
            # floor, the strong-beat bursts over the whole house, every syllable on the far porch
            fr += light(WARM, 0.2 * choir[f] + 0.08)
            fr += light(GLORY, 1.0 * full[f] * (0.85 + 0.15 * np.exp(-(off / (2 * half)) ** 2)))
            fr += light(GLORY, 0.4 * syl[f] * front)
            fr += light(GOLD, 0.45 * tr[f] * (front * (0.6 + 0.4 * np.exp(-(off / half) ** 2))
                                               + 0.5 * np.exp(-(off / 400.0) ** 2) * (1 - front)))
            fr += light(AMBER, 0.45 * ti[f] * ends)
        elif T_UNISON <= tt < T_UNISON_END:
            # the unison: one steady line along the whole roofline, rising and falling with the tune
            u = smoothstep(T_UNISON - 0.1, T_UNISON + 0.3, tt)
            lvl = 0.3 + 0.32 * np.clip((s_pitch[f] - 62) / 12.0, 0, 1)
            fr += light(GLORY, u * lvl * (0.95 + 0.05 * breathe(tt)))
        elif T_KINGDOM - 0.3 <= tt < STEPS[0]:
            # hushed: down to a dim blue with a faint warm line; it swells back through "is become"
            fall = smoothstep(T_KINGDOM - 0.3, T_KINGDOM + 0.4, tt)
            rise = smoothstep(T_BECOME, STEPS[0], tt)
            fr += light(NIGHT, 0.14 * (0.85 + 0.15 * breathe(tt)))
            fr += light(WARM, (0.12 + 0.12 * choir[f] + 0.35 * rise ** 1.5) * (0.6 + 0.4 * front) * fall)
            if tt < T_KINGDOM + 0.4:
                fr += light(WARM, 0.35 * (1 - fall))
        elif STEPS[0] <= tt < T_KINGS_END:
            # King of Kings: each held step lights the next run and it stays lit
            fr += light(NIGHT, 0.1)
            fr += light(WARM, 0.16 + 0.22 * ans[f])                   # the answers: for ever and ever
            for k, (t0, name) in enumerate(zip(STEPS, RUNS)):
                if tt < t0 - 0.05:
                    continue
                a = tt - t0
                mask = (seg == name).astype(float)
                fill = smoothstep(-0.05, 0.05, a / 0.7 - run_u) * mask            # sweeps along the run
                cur = k == max(j for j, s in enumerate(STEPS) if s <= tt + 0.05)
                lvl = (0.78 if cur else 0.52) + 0.25 * np.exp(-a / 0.4)
                fr += light(GLORY, lvl * fill)
                lit = mask
                fr += light(GLORY, 0.3 * ans[f] * np.maximum(shimmer(tt), 0) * lit)
            fr += light(GOLD, 0.5 * tr[f] * front * (0.5 + 0.5 * np.exp(-(off / half) ** 2)))
            fr += light(AMBER, 0.35 * ti[f] * (ends + 0.5 * side))
        elif T_PAUSE - 0.05 <= tt < T_PAUSE_END:
            # the grand pause: still and dim, nothing moving
            a = smoothstep(T_PAUSE - 0.05, T_PAUSE + 0.25, tt)
            fr += light(WARM, 0.5 * (1 - a) + 0.07 * a)
            fr += light(BED, 0.05 * a)
        else:
            # the Adagio, and the final chord in full warm gold
            k = int(np.searchsorted(adagio, tt, side='right'))
            step = k / max(len(adagio), 1)
            fin = smoothstep(T_LAST - 0.05, T_LAST + 0.5, tt)
            hit = burst(np.array([tt]), adagio, 0.4)[0]
            lvl = 0.25 + 0.4 * step + 0.15 * hit
            lvl = lvl * (1 - fin) + 0.92 * fin
            fr += light(WARM, lvl)
            fr += light(GLORY, (0.2 * hit * (1 - fin) + 0.35 * fin) * front)
            if tt >= T_LAST:
                fr += light(GOLD, 0.3 * np.exp(-(tt - T_LAST) / 0.6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings with oboes and bassoons doubling and the organ under it; Handel's strings, trumpets and
    timpani; timpani rolls under the last Hallelujah and its chord."""
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

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pfd = G.pd[G.seg['Porch Front']]
    porch = pan_at(0.5 * (pfd.min() + pfd.max()))

    def last(t, dd):
        return dd + HOLD if abs(t + dd - END) < 0.05 else dd

    LV = 1.5
    o = Orchestra(M, level=LV)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.12), v - 4, pan[p], 0.42)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.12), v - 6, pan[p], 0.38)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), v - 4, pan[p], 0.42)
            else:
                o.play('cellos', m if m < 60 else m - 12, t, max(dd, 0.15), v - 2, pan[p], 0.5)
                o.play('basses', m - 12 if m >= 48 else m, t, max(dd, 0.2), v - 8, pan[p], 0.36)
    parts = {'S': [('violins', 0, -6, 0.45), ('oboes', 0, -10, 0.32)],
             'A': [('violins', 0, -8, 0.35), ('violas', 0, -8, 0.3)],
             'T': [('violas', 0, -6, 0.42), ('bassoons', 0, -12, 0.25)],
             'B': [('cellos', 0, -6, 0.42), ('basses', -12, -8, 0.36), ('bassoons', 0, -10, 0.3)]}
    pan_of = {'S': -0.3, 'A': -0.1, 'T': 0.1, 'B': 0.3}
    for who in ('S', 'A', 'T', 'B'):
        for t, dd, m, v, h, _ in PART[who]:
            dd = last(t, dd)
            for section, trn, dv, g in parts[who]:
                o.play(section, m + trn, t, max(dd, 0.14), v + dv, pan_of[who], g)
    # the organ under the chorus: its longer notes on the manual, the basses on the pedal
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.11 * LV / 3.5, reverb=0.45)
    M.bus('pedal', gain=0.15 * LV / 3.5, reverb=0.35)
    for who in ('S', 'A', 'T', 'B'):
        for t, dd, m, v, h, _ in PART[who]:
            if dd < 0.3:
                continue
            dd = last(t, dd)
            if who == 'B':
                M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
            else:
                M.add('organ', man.play(m, v - 6, dd), t - 0.03, 1.0, pan_of[who] * 0.5)
    # the trumpets, from the porch
    for p, g in (('Tr1', 0.55), ('Tr2', 0.42)):
        for t, dd, m, v, h, _ in PART[p]:
            dd = last(t, dd)
            o.play('trumpets', m, t, max(dd * 0.92, 0.14), v - 2, porch + (0.1 if p == 'Tr2' else -0.1), g)
    # the timpani in D and A; rolls on the held notes of the end
    for t, dd, m, v, h, _ in PART['Timp']:
        pitch = 0 if m % 12 == 2 else -5
        if dd > 1.0:
            o.hit('timpani roll', t, min(110, v), pitch=pitch, gain=0.3, pan=0.15)
            o.hit('timpani', t, min(118, v + 8), pitch=pitch, gain=0.3, pan=0.15)
        else:
            o.hit('timpani', t, min(118, v + 4), pitch=pitch, gain=0.32, pan=0.15)
    # the last chord: a timpani roll under the hold, struck at its end
    o.hit('timpani roll', T_LAST + 1.5, 100, pitch=0, gain=0.25, pan=0.15)
    o.hit('timpani', END + HOLD - 0.6, 112, pitch=0, gain=0.3, pan=0.15)
