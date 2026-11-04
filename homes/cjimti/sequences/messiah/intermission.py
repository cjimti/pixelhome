"""Intermission: five minutes before Messiah begins again. The house waits in a deep night blue, and warm gold fills it
from both wings toward the middle of the porch, so the street can see how long is left: the night warming toward
the glory. Above the middle of Porch Front a small star twinkles the whole time, where the Christmas playlist's star
hangs (Star over the Porch). Each minute a wave runs over the gold and a harp marks it; when the gold meets under the
star the whole house swells and settles back to the blue for the Sinfony.

The music is Handel's own, as at a concert hall: the waiting music is the quiet numbers of Part One, played softly
from the set's own transcriptions (WAITING), each scene's notes as its excerpt has them. Each minute a harp spreads
the chord sounding under it. Then the call back, with the first thing the oratorio plays: the Sinfony's dotted
Grave, its opening bars, on strings with oboes and a timpani stroke, twice, from far then near, the last chord
landing as the gold meets in the middle."""
import os

import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, smoothstep
from pixelhome.intermission import MARKS, SECONDS, countdown
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS16'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house waits in night blue under a small star over the porch, and warm gold fills it from both '
               'wings over five minutes, until the gold meets under the star and Messiah begins again.')

D = SECONDS
FULL = MARKS['full']
NIGHT = hexc('#14204a')                     # the bed
GOLD = hexc('#ffb020')                      # the fill
EDGE = hexc('#fff2c8')                      # its bright front, white-gold
STAR = hexc('#fff4e0')


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=NIGHT, fill=GOLD, edge=EDGE, level=(0.3, 0.5), seed=seed)
    F = len(out)
    t = np.arange(F) * DT
    d = G.pd
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    star = np.exp(-((d - c) / 5.0) ** 2)
    halo = np.exp(-((d - c) / 24.0) ** 2) * (G.seg_of == 'Porch Front')
    tw = Flicker(rng, 1, 0.8, 3.0)
    for f in range(F):
        k = float(tw(t[f])[0])
        out[f] = out[f] * (1 - 0.6 * halo[:, None]) + light(STAR, (0.62 + 0.18 * k) * star + 0.12 * halo)
    return np.clip(out, 0, 1)


# the waiting music: the quiet numbers, from the set's own excerpts, as (scene file, from seconds, to seconds, what)
WAITING = [('pifa', 0.0, None, 'No. 13, Pifa (the Pastoral Symphony)'),
           ('he_shall_feed_his_flock', 0.0, None, 'No. 20, He shall feed His flock'),
           ('comfort_ye', 0.0, None, 'No. 2, Comfort ye')]
START, GAP = 5.0, 4.5


def waiting():
    """Every note of the waiting music, placed end to end: [t, d, midi, vel, hand, part]."""
    here = os.path.dirname(__file__)
    out, t0 = [], START
    for name, a, b, _ in WAITING:
        ex = excerpt(os.path.join(here, name + '.py'))
        b = ex['seconds'] if b is None else b
        for n in ex['notes']:
            if a - 0.01 <= n[0] < b - 0.05:
                out.append([n[0] - a + t0, min(n[1], b - n[0]), n[2], n[3], n[4], n[5]])
        t0 += (b - a) + GAP
    return out


def grave():
    """The Sinfony's opening bars (MS01's Grave, its first seconds up to a downbeat) as [t, d, midi, vel, part]."""
    ex = excerpt(os.path.join(os.path.dirname(__file__), 'sinfony.py'))
    bars = [t for m, t in ex['bars'] if t > 6.0]
    cut = bars[0] if bars else 8.0
    return [n[:4] + [n[5]] for n in ex['notes'] if n[0] < cut + 0.01], cut


def score(M, G):
    """The waiting music softly on a chamber orchestra; a harp on each minute; the Sinfony's Grave for the call back."""
    o = Orchestra(M, level=5.5)
    notes = waiting()
    end = max(n[0] + n[1] for n in notes)
    soft = lambda v: 50 + 0.35 * v
    voice = {'Soprano': ('flutes', -2), 'Alto': ('clarinets', -2), 'Tenor': ('oboes', -4), 'Bass': ('cellos', 0),
             'S': ('flutes', -4), 'A': ('clarinets', -4), 'T': ('violas', -2), 'B': ('cellos', -2)}
    strings = {'Vn1': 'violins', 'Vn2': 'violins', 'Va': 'violas', 'Bassi': 'cellos'}
    for t, d, m, v, h, who in notes:
        if who in strings:
            sec = strings[who]
            o.play(sec, m if sec != 'cellos' or m >= 36 else m + 12, t, max(d * 1.1, 0.3), soft(v) - 6, None, 0.35)
        else:
            sec, dv = voice.get(who, ('violas', -4))
            o.play(sec, m, t, max(d, 0.25), soft(v) + dv, None, 0.5)
    # each minute, a harp spreads the chord sounding under it
    for tm in MARKS['minutes']:
        pcs = sorted({n[2] % 12 for n in notes if n[0] <= tm + 0.3 and n[0] + n[1] >= tm - 0.3}) or [2, 6, 9]
        ks = [m for m in range(50, 84) if m % 12 in pcs][:9]
        for i, m in enumerate(ks):
            side = -1 if i % 2 == 0 else 1
            o.play('harp', m, tm + 0.12 * i, 0.5, 74, side * 0.7 * (1 - i / len(ks)), 0.85)
    # the call back: the Sinfony's Grave, from far then near, its last chord landing as the gold meets in the middle
    gr, cut = grave()
    for t0, vel, g, pan in ((FULL - 2 * cut - 4.0, 70, 0.2, -0.5), (FULL - cut, 92, 0.32, 0.3)):
        for t, d, m, v, part in gr:
            dd = d if t < cut - 0.01 else 5.0
            sec = strings.get(part, 'violas')
            o.play(sec, m if sec != 'cellos' or m >= 36 else m + 12, t0 + t, dd, vel, pan, g)
            if part == 'Vn1':
                o.play('oboes', m, t0 + t, dd, vel - 8, pan, g * 0.5)
            if part == 'Bassi':
                o.play('bassoons', m + 12 if m < 41 else m, t0 + t, dd, vel - 8, pan, g * 0.5)
        o.hit('timpani', t0 + cut, vel, pitch=0, gain=g)
    o.hit('timpani roll', FULL - 3.0, 70, pitch=0, gain=0.2)
    assert end < FULL - 2 * cut - 6, f'the waiting music runs to {end:.0f} s'
