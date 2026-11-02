"""Intermission: five minutes before Elijah begins again. The house is in the drought, a dust ochre, and the rain
fills it from both wings toward the middle of the porch, so the street can see how long is left; motes of dust drift
over the dry part still waiting, and drops glint in the rain that has come. Each minute a wave runs over the rain and
a harp marks it; when the rain meets in the middle the whole house swells and gives the drought back for the
Introduction, where Elijah calls it down.

The music is Mendelssohn's own, as at a concert hall: the waiting music is the quiet numbers of the oratorio, played
softly from the set's own transcriptions (WAITING), each scene's notes as its excerpt has them. Each minute a harp
spreads the chord sounding under it. Then the call back, as Bayreuth calls its audience with a motif from the
coming act: the four chords of Elijah's curse, the first thing the oratorio plays, on trombones and tuba, twice, from
far then near, the last landing as the rain meets in the middle."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.intermission import MARKS, SECONDS, countdown, order, reach
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL24'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house waits in the drought, dust ochre, and the rain fills it from both wings toward the porch '
               'over five minutes, until it meets in the middle and Elijah begins again.')

D = SECONDS
FULL = MARKS['full']
DUST = hexc('#a8641c')                      # the drought, as a bed bright enough to read
RAIN = hexc('#2060ff')                      # rain
SPRAY = hexc('#80c8ff')                     # its bright front and its drops
MOTE = hexc('#ffb860')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=DUST, fill=RAIN, edge=SPRAY, seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t = np.arange(F) * DT
    reach_t = reach(t)
    # dust: slow motes drifting along the dry part, rising and fading over a few seconds
    n = 90
    born = np.sort(rng.uniform(0, FULL - 6, n))
    where = rng.uniform(0, 1, n)
    drift = rng.choice([-1.0, 1.0], n) * rng.uniform(3, 8, n)
    for k in range(n):
        f0, f1 = int(born[k] / DT), min(F, int((born[k] + 5.0) / DT))
        dry = np.where(v < reach_t[f0] - 0.05)[0]
        if not len(dry):
            continue
        c0 = d[dry[int(where[k] * (len(dry) - 1))]]
        tt = t[f0:f1, None] - born[k]
        c = c0 + drift[k] * tt
        env = np.sin(np.pi * np.clip(tt / 5.0, 0, 1)) ** 2
        out[f0:f1] += light(MOTE, 0.5 * env * np.exp(-((d[None] - c) / 5.0) ** 2) * (v[None] < reach_t[f0:f1, None] - 0.02))
    # rain: drops glinting on the filled part, a few each second, quick
    drops = np.sort(rng.uniform(4, FULL, 520))
    at = rng.integers(0, G.N, len(drops))
    for k, tg in enumerate(drops):
        f0, f1 = int(tg / DT), min(F, int((tg + 0.6) / DT))
        if v[at[k]] < reach_t[f0] + 0.02:            # only where the rain has come
            continue
        tt = t[f0:f1, None] - tg
        out[f0:f1] += light(SPRAY, 0.7 * np.exp(-tt / 0.18) * np.exp(-((d[None] - d[at[k]]) / 2.5) ** 2))
    return np.clip(out, 0, 1)


# the waiting music: the quiet numbers, from the set's own excerpts, as (scene file, from seconds, to seconds, what)
WAITING = [('lift_thine_eyes', 25.1, 63.5, 'No. 28, Lift thine eyes'),
           ('lord_god_of_abraham', 10.5, 34.3, 'No. 14, Lord God of Abraham'),
           ('lord_god_of_abraham', 34.3, 83.9, 'No. 15, Cast thy burden upon the Lord'),
           ('o_rest_in_the_lord', 23.4, 51.7, 'No. 31, O rest in the Lord'),
           ('o_rest_in_the_lord', 52.7, 81.8, 'No. 32, He that shall endure to the end'),
           ('your_light_break_forth', 0.0, 18.0, 'No. 39, Then shall the righteous shine forth'),
           ('lift_thine_eyes', 65.0, 81.2, 'No. 29, He, watching over Israel')]
START, GAP = 5.0, 4.5


def waiting():
    """Every note of the waiting music, placed end to end: [t, d, midi, vel, hand, part]."""
    import os
    here = os.path.dirname(__file__)
    out, t0 = [], START
    for name, a, b, _ in WAITING:
        ex = excerpt(os.path.join(here, name + '.py'))
        for n in ex['notes']:
            if a - 0.01 <= n[0] < b - 0.05:
                out.append([n[0] - a + t0, min(n[1], b - n[0]), n[2], n[3], n[4], n[5]])
        t0 += (b - a) + GAP
    return out


def curse():
    """The four chords of Elijah's curse, the Introduction's first bars (EL01), as [t, d, midi, vel]."""
    import os
    ex = excerpt(os.path.join(os.path.dirname(__file__), 'the_curse.py'))
    return [n[:4] for n in ex['notes'] if n[5] == 'Orch' and n[0] < 4.9]


def score(M, G):
    """The waiting music softly on a chamber orchestra; a harp on each minute; rain coming in under the last minutes;
    the curse chords on trombones and tuba for the call back."""
    o = Orchestra(M, level=3.9)
    notes = waiting()
    end = max(n[0] + n[1] for n in notes)
    soft = lambda v: 50 + 0.35 * v
    voice = {'S': ('flutes', -4), 'S1': ('flutes', -4), 'S2': ('oboes', -6), 'A': ('clarinets', -4),
             'A1': ('clarinets', -4), 'T': ('violas', -2), 'Tenor': ('horns', -2), 'B': ('cellos', -2),
             'Elijah': ('cellos', 0), 'Angel': ('oboes', -4)}
    for t, d, m, v, h, who in notes:
        if who == 'Orch':
            sec = 'violins' if m >= 67 else 'violas' if m >= 55 else 'cellos' if m >= 40 else 'basses'
            o.play(sec, m + (12 if sec == 'basses' and m < 40 else 0), t, max(d * 1.1, 0.3), soft(v) - 6, None, 0.35)
        else:
            sec, dv = voice.get(who, ('violas', -4))
            o.play(sec, m, t, max(d, 0.25), soft(v) + dv, None, 0.5)

    # each minute, a harp spreads the chord sounding under it
    for tm in MARKS['minutes']:
        pcs = sorted({n[2] % 12 for n in notes if n[0] <= tm + 0.3 and n[0] + n[1] >= tm - 0.3}) or [2, 5, 9]
        ks = [m for m in range(50, 84) if m % 12 in pcs][:9]
        for i, m in enumerate(ks):
            side = -1 if i % 2 == 0 else 1
            o.play('harp', m, tm + 0.12 * i, 0.5, 74, side * 0.7 * (1 - i / len(ks)), 0.85)

    # the rain coming in as the house fills with it
    o.fire(180.0, FULL + 6, level=lambda tt: 0.1 * np.clip((tt - 180.0) / 90.0, 0, 1), crackle=30.0, seed=24)

    # the call back: Elijah's curse, from far then near, the last chord landing as the rain meets in the middle
    ch = curse()
    last = max(n[0] for n in ch)
    for t0, vel, g, pan in ((FULL - 11.0 - last, 70, 0.18, -0.5), (FULL - last, 90, 0.3, 0.3)):
        for t, d, m, v in ch:
            dd = d if t < last else 7.0
            if m < 45:
                parts = [('tuba', 0, 0.6), ('trombones', 12, 0.3)]
            elif m < 57:
                parts = [('trombones', 0, 0.55)]
            else:
                parts = [('horns', 0, 0.5)]
            for sec, tr, gg in parts:
                o.play(sec, m + tr, t0 + t, dd, vel, pan, g * gg / 0.55)
    o.hit('timpani roll', FULL - 3.0, 70, pitch=-2, gain=0.2)
    o.hit('timpani', FULL, 96, pitch=-2, gain=0.3)
    assert end < FULL - 12, f'the waiting music runs to {end:.0f} s'
