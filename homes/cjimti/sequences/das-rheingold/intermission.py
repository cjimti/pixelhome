"""Intermission: five minutes on the Rhine before Das Rheingold starts again. The house is the river, a deep
blue-green, and the Rhinegold fills it from both wings toward the middle of the porch, so the street can see how
long is left; flecks of gold glint in the water still waiting for it, on the high notes of the music. Each minute
a wave runs over the gold and a harp marks it; when the gold meets in the middle the whole house swells and gives
the river back for the show.

The music is Wagner's own, as at an opera house: the waiting music is the Prelude to Das Rheingold played softly,
bars 1-9 and 13-112 (the low E flat, the eight horns' canon on the Nature motif and the Rhine's flowing figure),
timed bar by bar like Sebastian Weigle's 2010 Frankfurt recording, its notes from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py), dying away before the flood. Each minute a harp spreads the chord sounding under it.
Then the call back, as Bayreuth calls its audience from the balcony with a brass fanfare of a motif from the coming
act: the Gold's horn call on trumpets, twice, from far then near, and the Valhalla motif on the brass choir,
landing as the gold meets in the middle (both from pixelhome/leitmotifs.py, in D flat)."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, smoothstep
from pixelhome.intermission import MARKS, SECONDS, countdown, order, reach
from pixelhome.leitmotifs import play as motif
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'RG25'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house becomes the Rhine, deep blue-green, and the gold fills it from both wings toward the '
               'porch over five minutes, glinting in the water ahead of it, until it meets in the middle and the '
               'opera begins again.')

D = SECONDS
EX = excerpt(__file__)                      # Prelude bars 1-9, 13-112, Weigle 2010
BED_END = EX['seconds']                     # 269 s: the river dies away before the flood
FULL = MARKS['full']

RHINE = hexc('#0b6f78')                     # deep blue-green water
GOLD = hexc('#e8b923')                      # the Rhinegold
EDGE = hexc('#fff3b8')                      # its bright front
GLINT = hexc('#ffd65a')


def glint_times():
    """High notes of the score, thinned: each one puts a fleck of gold in the water."""
    out = []
    for t, d, m, v, h in sorted(EX['notes']):
        if h == 0 and (m >= 63 if t < 140 else m >= 74) and (not out or t - out[-1] >= 0.5):
            out.append(t)
    return out


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=RHINE, fill=GOLD, edge=EDGE, seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t = np.arange(F) * DT
    reach_t = reach(t)
    # the current: slow brighter crests run along the river still waiting for the gold, toward the porch
    crest = hexc('#20c0b0')
    for f0 in range(0, F, 400):
        tt = t[f0:f0 + 400, None]
        free = v[None] < reach_t[f0:f0 + 400, None] - 0.015
        w = (0.5 + 0.5 * np.cos(2 * np.pi * (v[None] * 6 + tt / 7))) ** 3
        live = 1 - smoothstep(FULL - 3, FULL, tt)
        out[f0:f0 + 400] += light(crest, 0.22 * w * free * live)
    # gold in the water: a fleck on the unfilled river for each high note, rising and fading over ~2.5 s
    for tg in glint_times():
        if tg > FULL - 4:
            break
        f0, f1 = int(tg / DT), min(F, int((tg + 2.6) / DT))
        rr = reach_t[f0]
        free = np.where(v < rr - 0.04)[0]                       # only where the gold hasn't reached yet
        if not len(free):
            continue
        c = d[rng.choice(free)]
        shape = np.exp(-((d - c) / 18.0) ** 2)
        tt = t[f0:f1, None] - tg
        env = smoothstep(0, 0.35, tt) * np.exp(-np.clip(tt - 0.35, 0, None) / 0.8)
        out[f0:f1] += light(GLINT, 0.75 * env * shape[None] * (v[None] < reach_t[f0:f1, None] - 0.02))
    return np.clip(out, 0, 1)


def score(M, G):
    """The Prelude on a soft orchestra; a harp on each minute; the Gold and Valhalla on brass for the call back."""
    o = Orchestra(M, level=2.4)
    fade = lambda t: float(np.interp(t, [0, 240, BED_END - 1], [1.0, 1.0, 0.45]))
    soft = lambda v: 50 + 0.25 * v

    # the bed: Wagner's prelude, every note, in the river's own colours (low strings, bassoons, horns, strings)
    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t + d > BED_END - 1.0:                              # the last notes ring on as the river fades
            d = BED_END + 2.5 - t
        dd = max(d * 1.15, 0.27)                               # legato: the river never breaks into spiccato
        g = fade(t)
        vv = soft(v)
        if h == 1:
            if d >= 1.0:                                        # the pedal and the long held notes
                if m <= 34:
                    parts = [('basses', 12, 6, 0.8), ('bassoons', 12, -2, 0.35)]
                elif m < 48:
                    parts = [('bassoons', 0, 0, 0.4), ('cellos', 0, -6, 0.35)]
                else:
                    parts = [('horns', 0, -4, 0.4), ('violas', 0, -8, 0.25)]
            else:
                parts = [('cellos' if m < 55 else 'violas', 0, 0, 0.45)]
        elif d >= 0.6:                                          # the horns' arpeggios
            parts = [('horns', 0, 0, 0.5)]
        else:                                                   # the flowing figure
            parts = [('violins' if m >= 62 else 'violas' if m >= 55 else 'cellos', 0, 0, 0.42)]
            if m >= 79:
                parts.append(('flutes', 0, -10, 0.2))
        for sec, tr, dv, gg in parts:
            o.play(sec, m + tr, t, dd, vv + dv, None, gg * g)

    # each minute, a harp spreads the chord sounding under it, from both sides in toward the porch
    for k, tm in enumerate(MARKS['minutes']):
        pcs = sorted({n[2] % 12 for n in EX['notes'] if n[0] <= tm + 0.3 and n[0] + n[1] >= tm - 0.3}) or [3, 7, 10]
        notes = [m for m in range(51, 84) if m % 12 in pcs][:9]
        for i, m in enumerate(notes):
            side = -1 if i % 2 == 0 else 1
            o.play('harp', m, tm + 0.12 * i, 0.5, 78, side * 0.7 * (1 - i / len(notes)), 0.9)
        o.play('glock', notes[-1], tm + 0.12 * len(notes), 0.5, 50, 0.0, 0.25)

    # the call back: the Gold's horn call on trumpets, from far then near, then Valhalla on the brass choir
    beat = 0.42
    for t0, vel, g, pan in ((272.4, 64, 0.35, -0.5), (276.0, 80, 0.55, 0.4)):
        for t, m, vv, dur in motif('gold', t0, beat, transpose=6):
            o.play('trumpets', m, t, max(dur, 0.2), vel, pan, g)
    vb = 0.8
    v0 = FULL - 6.6667 * vb                                     # its last chord lands on MARKS['full']
    for t, m, vv, dur in motif('valhalla', v0, vb):
        if t >= FULL - 0.01:
            dur = 9.0                                           # the last chord rings through the swell
        if m < 46:
            parts = [('tuba', 0, 0.6), ('trombones', 12, 0.3)]
        elif m < 58:
            parts = [('trombones', 0, 0.55)]
        elif m < 66:
            parts = [('horns', 0, 0.6)]
        else:
            parts = [('trumpets', 0, 0.45), ('horns', -12, 0.3)]
        for sec, tr, g in parts:
            o.play(sec, m + tr, t, dur, 84, 0.0, g)
    o.hit('cymbal swell', FULL - 2.4, 80, gain=0.25)
    o.hit('timpani roll', FULL, 70, pitch=-2, gain=0.2)
