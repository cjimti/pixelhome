"""Intermission: five minutes before Judas Maccabaeus begins again. The house waits in the people's blue, and white
fills it from both wings toward the middle of the porch, so the street can see how long is left; the blue and white
of a tallit, with a few white lights stirring in the blue still waiting. Through all of it the lights' glow stays on
the Temple, Porch Front, steady under the fill: the scenes play on every night of Hanukkah, and the glow is the same
on each. Each minute a wave runs over the white and a harp marks it; when the white meets in the middle the whole
house swells and settles back to the blue for the Overture.

The music is Handel's own, as at a concert hall: the waiting music is the quiet numbers of the oratorio, played
softly from the set's own transcriptions (WAITING), each scene's notes as its excerpt has them. Each minute a harp
spreads the chord sounding under it. Then the call back, with the first thing the oratorio plays: the Overture's
opening bars, its dotted Grave, on horns and trumpets over bassoons and timpani, twice, from far then near, the last
chord landing as the white meets in the middle."""
import os

import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.intermission import MARKS, SECONDS, countdown, order, reach
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM16'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house waits in blue, and white fills it from both wings toward the porch over five minutes, the '
               "lights' glow steady on the Temple, until the white meets in the middle and the set begins again.")

D = SECONDS
FULL = MARKS['full']
BLUE = hexc('#1e5bd8')                      # the people, the bed
WHITE = hexc('#f2f6ff')                     # the fill
TIP = hexc('#fff1c0')                       # its bright front: the flame tips' white
PURPLE = hexc('#6a2ca0')                    # the Overture's opening (JM01): the Seleucids hold the land
STONE = hexc('#6a6a6a')
HANDOVER = 2.5                              # seconds at the end that give the house to the Overture's first frame


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def opening(G, glow, t):
    """The Overture's first frame (JM01 at t=0): purple over the wings, faint on the porch runs, the people dim on
    them, four grey idols on the Temple over a dim glow, a few blue lights hidden on Left. Change it with JM01."""
    d, seg = G.pd, G.seg_of
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    pf0, pf1 = span(G, 'Porch Front')
    l0, l1 = span(G, 'Left')
    porch = np.isin(seg, ['Porch Left', 'Porch Right'])
    wings = np.isin(seg, ['Left', 'Right', 'Side'])
    blue_p, white_p = np.zeros(G.N), np.zeros(G.N)
    for a, b in ((pl0, pl1), (pr0, pr1)):
        for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
            g = np.exp(-((d - c) / 4.0) ** 2)
            if k % 2:
                white_p += g
            else:
                blue_p += g
    blue_p, white_p = np.minimum(blue_p, 1) * porch, np.minimum(white_p, 1) * porch
    idols = sum(np.clip((14 - np.abs(d - (pf0 + (0.14 + 0.24 * k) * (pf1 - pf0)))) / 5, 0, 1) for k in range(4))
    idols = np.minimum(idols, 1) * (seg == 'Porch Front')
    hid = sum(np.exp(-((d - (l0 + f * (l1 - l0))) / 3.5) ** 2) for f in (0.18, 0.33, 0.47, 0.75, 0.88))
    fr = light(PURPLE, 0.285 * wings + 0.14 * porch)
    fr += light(STONE, 0.75 * idols) + glow.frame(t, 0.3)
    fr += light(BLUE, 0.11 * hid * (seg == 'Left'))
    fr += light(BLUE, 0.14 * blue_p) + light(WHITE, 0.1 * white_p)
    return fr


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=BLUE, fill=WHITE, edge=TIP, level=(0.34, 0.5), seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t = np.arange(F) * DT
    reach_t = reach(t)
    # white lights stirring in the blue still waiting: slow, a few at a time, rising and fading over a few seconds
    n = 80
    born = np.sort(rng.uniform(0, FULL - 6, n))
    where = rng.uniform(0, 1, n)
    for k in range(n):
        f0, f1 = int(born[k] / DT), min(F, int((born[k] + 5.0) / DT))
        waiting = np.where(v < reach_t[f0] - 0.05)[0]
        if not len(waiting):
            continue
        c = d[waiting[int(where[k] * (len(waiting) - 1))]]
        tt = t[f0:f1, None] - born[k]
        env = np.sin(np.pi * np.clip(tt / 5.0, 0, 1)) ** 2
        out[f0:f1] += light(WHITE, 0.45 * env * np.exp(-((d[None] - c) / 4.0) ** 2)
                            * (v[None] < reach_t[f0:f1, None] - 0.02))
    # the lights' glow on the Temple, steady the whole time, under the fill and over it; the bed eased off it so the
    # glow reads
    glow = Glow(G, seed)
    temple = (G.seg_of == 'Porch Front')[:, None]
    for f in range(F):
        out[f] = out[f] * np.where(temple, 0.55, 1.0) + glow.frame(t[f], 1.6)
    # the last seconds hand the house to the Overture's first frame
    for f in range(int((D - HANDOVER) / DT), F):
        k = smoothstep(D - HANDOVER, D - 0.3, t[f])
        out[f] = (1 - k) * np.clip(out[f], 0, 1) + k * opening(G, glow, t[f])
    return np.clip(out, 0, 1)


# the waiting music: the quiet numbers, from the set's own excerpts, as (scene file, from seconds, to seconds, what)
WAITING = [('o_lovely_peace', 0.0, 58.07, 'No. 66, O lovely peace'),
           ('father_of_heaven', 0.0, 77.1, "No. 53, Father of heav'n"),
           ('mourn_ye_afflicted', 0.0, 29.48, 'No. 2, Mourn, ye afflicted children'),
           ('o_father', 1.2, 37.9, 'No. 8, O Father, whose almighty power'),
           ('we_never_will_bow_down', 0.0, 22.8, 'No. 52, We never will bow down')]
START, GAP = 5.0, 4.5


def waiting():
    """Every note of the waiting music, placed end to end: [t, d, midi, vel, hand, part]."""
    here = os.path.dirname(__file__)
    out, t0 = [], START
    for name, a, b, _ in WAITING:
        ex = excerpt(os.path.join(here, name + '.py'))
        for n in ex['notes']:
            if a - 0.01 <= n[0] < b - 0.05:
                out.append([n[0] - a + t0, min(n[1], b - n[0]), n[2], n[3], n[4], n[5]])
        t0 += (b - a) + GAP
    return out


def grave():
    """The Overture's opening bars (JM01's Grave, its first two bars and the next downbeat) as [t, d, midi, vel, part]."""
    ex = excerpt(os.path.join(os.path.dirname(__file__), 'overture.py'))
    return [n[:4] + [n[5]] for n in ex['notes'] if n[0] < 8.01]


def score(M, G):
    """The waiting music softly on a chamber orchestra; a harp on each minute; the Overture's Grave on horns, trumpets,
    bassoons and timpani for the call back."""
    o = Orchestra(M, level=4.7)
    notes = waiting()
    end = max(n[0] + n[1] for n in notes)
    soft = lambda v: 50 + 0.35 * v
    voice = {'S': ('flutes', -4), 'S1': ('flutes', -4), 'S2': ('oboes', -6), 'A': ('clarinets', -4),
             'T': ('violas', -2), 'B': ('cellos', -2), 'Voice': ('flutes', 0), 'Simon': ('cellos', 0),
             'Woman': ('oboes', -2), 'Man': ('flutes', -2)}
    for t, d, m, v, h, who in notes:
        if who == 'Orch':
            sec = 'violins' if m >= 67 else 'violas' if m >= 55 else 'cellos' if m >= 40 else 'basses'
            o.play(sec, m + (12 if sec == 'basses' and m < 40 else 0), t, max(d * 1.1, 0.3), soft(v) - 6, None, 0.35)
        else:
            sec, dv = voice.get(who, ('violas', -4))
            o.play(sec, m, t, max(d, 0.25), soft(v) + dv, None, 0.5)

    # each minute, a harp spreads the chord sounding under it
    for tm in MARKS['minutes']:
        pcs = sorted({n[2] % 12 for n in notes if n[0] <= tm + 0.3 and n[0] + n[1] >= tm - 0.3}) or [2, 7, 10]
        ks = [m for m in range(50, 84) if m % 12 in pcs][:9]
        for i, m in enumerate(ks):
            side = -1 if i % 2 == 0 else 1
            o.play('harp', m, tm + 0.12 * i, 0.5, 74, side * 0.7 * (1 - i / len(ks)), 0.85)

    # the call back: the Overture's Grave, from far then near, its last chord landing as the white meets in the middle
    gr = grave()
    last = max(n[0] for n in gr)
    for t0, vel, g, pan in ((FULL - 13.0 - last, 70, 0.2, -0.5), (FULL - last, 92, 0.32, 0.3)):
        for t, d, m, v, part in gr:
            dd = d if t < last else 6.0
            if part == 'Bassi':
                parts = [('bassoons', 0, 0.6), ('cellos', 0, 0.4)]
            elif part == 'Vn1':
                parts = [('trumpets', 0, 0.45), ('horns', -12, 0.3)]
            else:
                parts = [('horns', 0, 0.45)]
            for sec, tr, gg in parts:
                o.play(sec, m + tr, t0 + t, dd, vel, pan, g * gg / 0.5)
        o.hit('timpani', t0, vel, pitch=-5, gain=g)
        o.hit('timpani', t0 + last, vel + 6, pitch=0, gain=g)
    o.hit('timpani roll', FULL - 3.0, 70, pitch=0, gain=0.2)
    assert end < FULL - 16, f'the waiting music runs to {end:.0f} s'
