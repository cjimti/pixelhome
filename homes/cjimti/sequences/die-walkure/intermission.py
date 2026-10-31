"""Intermission: five minutes before Die Walküre starts again. The house is a stormy night, deep blue with slow
clouds drifting through it, and Loge's fire closes in from both wings toward the middle of the porch, so the street
can see how long is left; the burnt part flickers like the ring of fire around Brünnhilde's rock. Each minute a
wave runs over the fire and a harp marks it; when the fire meets in the middle the whole house swells and gives the
night back for the storm the opera opens with.

The music is Wagner's own, as at an opera house: the waiting music is the end of Die Walküre played softly, Act III
bars 1619-1642 (after Wotan's kiss, the magic sleep motif as he lays Brünnhilde down) and 1698-1733 (the Magic Fire
music, to the last chord), timed bar by bar like Keilberth's 1952 Bayreuth recording, its notes from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the fire's figuration on harp and violins, the sleep motif on
woodwinds, the fate motif on horns. Each minute a harp spreads the chord sounding under it. Then the call back, as
Bayreuth calls its audience from the balcony with a brass fanfare of a motif from the coming act: the Sword motif on
trumpets (pixelhome/leitmotifs.py), from far then near, the second time over the brass choir's held C major chord,
landing as the fire meets in the middle."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, smooth_noise
from pixelhome.intermission import MARKS, SECONDS, countdown, order, reach
from pixelhome.leitmotifs import play as motif
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'WK31'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house becomes a stormy night, deep blue with drifting clouds, and the magic fire closes in '
               'from both wings toward the porch over five minutes, flickering as it comes, until it meets in the '
               'middle and the opera begins again.')

D = SECONDS
EX = excerpt(__file__)                      # Act III bars 1619-1642, 1698-1733, Keilberth 1952
BED_END = EX['seconds']                     # 275 s: the last chord dies away
FULL = MARKS['full']

NIGHT = hexc('#1b2ea8')                     # storm-night blue
FIRE = hexc('#e2502c')                      # Loge's fire
EDGE = hexc('#ffc46a')                      # its bright front
FLAME = hexc('#ff6a00')
CLOUD = hexc('#6a78d8')


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=NIGHT, fill=FIRE, edge=EDGE, seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t = np.arange(F) * DT
    reach_t = reach(t)
    # two noise fields for the fire's tongues and the clouds' shapes, slid along the roofline over time
    span = np.arange(0.0, 40000.0, 4.0)
    P = 40000.0
    tongue = smooth_noise(rng, span, 60.0, octaves=3)
    cloud = smooth_noise(rng, span, 420.0, octaves=2)
    for f0 in range(0, F, 400):
        tt = t[f0:f0 + 400, None]
        rr = reach_t[f0:f0 + 400, None]
        live = 1 - smoothstep(FULL - 2, FULL + 1, tt)          # the finale belongs to the countdown
        burnt = smoothstep(-0.01, 0.02, v[None] - rr)
        # the fire flickers: two sets of tongues running opposite ways, so the burnt part licks and dips in place
        a = np.interp(d[None] + 70 * tt, span, tongue, period=P)
        b = np.interp(1.7 * d[None] - 110 * tt + 900, span, tongue, period=P)
        lick = 1.3 * (a + b)
        out[f0:f0 + 400] *= (1 - 0.3 * np.clip(-lick, 0, 1) * burnt * live)[..., None]
        out[f0:f0 + 400] += light(FLAME, 0.5 * np.clip(lick, 0, 1.2) * burnt * live)
        # clouds drift slowly through the night still waiting for the fire: lighter patches over the blue
        c = np.clip(np.interp(d[None] + 22 * tt, span, cloud, period=P), 0, None)
        out[f0:f0 + 400] += light(CLOUD, 0.42 * c * (1 - burnt) * live)
    return np.clip(out, 0, 1)


def score(M, G):
    """The end of the opera on a soft orchestra; a harp on each minute; the Sword on trumpets for the call back."""
    o = Orchestra(M, level=2.4)
    soft = lambda v: 50 + 0.2 * v

    for t, d, m, v, h, trem in tidy(EX['notes']):
        if t + d > BED_END - 0.5:                              # the last chord dies away
            d = BED_END + 2.0 - t
        dd = max(d * 1.1, 0.27)
        vv = soft(v)
        if trem:                                               # the strings' shimmer under the fire
            parts = [('violins trem' if m >= 60 else 'violas trem' if m >= 50 else 'cellos trem', 0, -6, 0.35)]
        elif h == 0 and d < 0.25:                              # the fire's figuration: harp, violins over it
            parts = [('harp', 0, 0, 0.45)]
            if m >= 64:
                parts.append(('violins', 0, -8, 0.22))
        elif h == 0:
            if m >= 60:                                        # the sleep motif's chords: woodwinds
                parts = [('clarinets' if m < 72 else 'flutes', 0, 0, 0.45), ('oboes', 0, -10, 0.18)]
            else:
                parts = [('horns', 0, -2, 0.45)]
        else:
            if d >= 0.8:
                if m < 48:
                    parts = [('cellos', 0, 0, 0.5), ('basses', 12 if m < 40 else 0, -4, 0.45)]
                else:
                    parts = [('horns', 0, -4, 0.45), ('bassoons', 0, -8, 0.25)]
            else:
                parts = [('cellos' if m < 55 else 'violas', 0, 0, 0.42)]
        for sec, tr, dv, gg in parts:
            o.play(sec, m + tr, t, dd, vv + dv, None, gg)

    # each minute, a harp spreads the chord sounding under it, from both sides in toward the porch
    for tm in MARKS['minutes']:
        pcs = sorted({n[2] % 12 for n in EX['notes'] if n[0] <= tm + 0.3 and n[0] + n[1] >= tm - 0.3}) or [4, 8, 11]
        notes = [m for m in range(52, 84) if m % 12 in pcs][:9]
        for i, m in enumerate(notes):
            side = -1 if i % 2 == 0 else 1
            o.play('harp', m, tm + 0.12 * i, 0.5, 80, side * 0.7 * (1 - i / len(notes)), 0.95)
        o.play('glock', notes[-1], tm + 0.12 * len(notes), 0.5, 50, 0.0, 0.25)

    # the call back: the Sword on trumpets, from far, then near over the brass choir's C major, landing on 'full'
    beat = 0.5
    t2 = FULL - 6.5 * beat                                      # its last note (E5) lands on MARKS['full']
    for t0, vel, g, pan in ((t2 - 5.0, 66, 0.35, -0.5), (t2, 84, 0.6, 0.3)):
        for t, m, vv, dur in motif('sword', t0, beat):
            if t0 == t2 and t >= FULL - 0.01:
                dur = 8.0
            o.play('trumpets', m, t, max(dur, 0.2), vel, pan, g)
    for m, sec, g in ((36, 'tuba', 0.55), (48, 'trombones', 0.5), (55, 'trombones', 0.45), (60, 'horns', 0.5),
                      (64, 'horns', 0.45), (67, 'horns', 0.4)):
        o.play(sec, m, t2 - 0.6, FULL + 8.0 - (t2 - 0.6), 78, 0.0, g)
    o.hit('cymbal swell', FULL - 2.4, 80, gain=0.25)
    o.hit('timpani roll', FULL, 70, gain=0.2)
