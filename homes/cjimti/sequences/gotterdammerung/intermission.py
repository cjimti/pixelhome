"""Intermission: five minutes of dawn and the Rhine before Götterdämmerung, and the brass calling the street back.

The house is the sky at dusk: a deep purple bed with fire-gold closing in from the wing ends toward the middle of
Porch Front (pixelhome/intermission.py's countdown), so anyone on the street can see how long is left. The part
still to fill follows the music: while the dawn music plays, a rose first light swells and fades along it; while the
Rhine flows, slow blue ripples run through it toward the porch; and in the last quiet minute, as the music turns to
the gold, a few gold glints surface in it like the Rhinegold under the water. On every minute a soft gold ring
opens from the middle of Porch Front with the harp. When the fill meets in the middle the brass call the audience
back: every note of Siegfried's motif flashes white and gold out of the middle of the porch, and the Twilight of
the Gods follows in slow deep-red pulses as the house swells and settles for the show.

The music is Wagner's own, as an opera house's interval would have it: soft music to wait by, then the call-back.
The waiting music is from the Prologue: the daybreak after the Norns vanish (bars 304 to 343), the quiet stretch of
Siegfried's Rhine Journey (670 to 723) and its close as it darkens toward the Gibichungs' hall (880 to 891), timed
like Solti's 1958 Vienna Philharmonic recording; the notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py), orchestrated gently on strings, horns and woodwinds. Each minute a harp rolls the chord the
orchestra is on, with a soft horn under it. Then, as at Bayreuth, where the audience is called back from each
interval by a fanfare of a motif from the coming act played from the balcony: Siegfried the hero on the horns,
again on trumpets landing as the fill meets, and the Twilight of the Gods on trombones and horns as the house
settles."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.intermission import SECONDS, MARKS, countdown, order, reach
from pixelhome.leitmotifs import play as motif
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'GD31'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house glows dusk purple while fire-gold closes in toward the porch, counting down five minutes '
               'through dawn light and Rhine ripples, until a brass fanfare calls everyone back.')

D = SECONDS
FULL = MARKS['full']
EX = excerpt(__file__)                      # Prologue, bars 304-343, 670-723 and 880-891, Solti 1958
T_RHINE = EX['segments'][1]['start']        # the Rhine Journey's quiet stretch
T_GOLD = EX['segments'][2]['start']         # its close: the gold's lament, darkening
T_END = EX['seconds']

BED = hexc('#4a0c90')                       # dusk purple
FILL = hexc('#ff8a14')                      # fire-gold
EDGE = hexc('#fff0c0')
ROSE = hexc('#ff4070')
RHINE = hexc('#2070ff')
GOLD = hexc('#ffb020')
WHITE = hexc('#ffffff')
RED = hexc('#c00818')

# The call-back: Siegfried the hero (Donington 53) on horns, then on trumpets with its peak on FULL; the Twilight
HERO_BEAT = 0.62
HERO_PEAK = 0.5417                          # the beat of the motif's top note, G
T_HERO1 = FULL - 4.9
T_HERO2 = FULL - HERO_PEAK * HERO_BEAT
T_TWILIGHT = FULL + 4.6
TWILIGHT_BEAT = 0.75


def fanfare():
    """[(t, midi, dur, section, strength)] of the call-back's melody."""
    out = [(t, m - 12, d, 'horns', 0.65) for t, m, v, d in motif('siegfried', T_HERO1, HERO_BEAT)]
    out += [(t, m, d, 'trumpets', 1.0) for t, m, v, d in motif('siegfried', T_HERO2, HERO_BEAT)]
    return out


def twilight():
    """[(t, midi, dur)] of the Twilight of the Gods (Donington 4), an octave down, all its notes."""
    return [(t, m - 12, d) for t, m, v, d in motif('downfall', T_TWILIGHT, TWILIGHT_BEAT)]


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    out = countdown(G, bed=BED, fill=FILL, edge=EDGE, level=(0.36, 0.64), seed=seed)
    F = len(out)
    t = np.arange(F) * DT
    d = G.pd
    v = order(G)
    c = np.mean(d[G.seg['Porch Front']])
    reach_t = reach(t)

    # what the part still to fill does, with the music: the first light, the Rhine, the gold under the water
    glints = sorted(zip(rng.uniform(T_GOLD, T_END, 46), rng.uniform(0, 1, 46)))
    for f0 in range(0, F, 400):
        tt = t[f0:f0 + 400, None]
        open_ = (1 - smoothstep(-0.03, 0.03, v[None] - reach_t[f0:f0 + 400, None])) * (1 - smoothstep(FULL - 6, FULL, tt))
        dawn = (smoothstep(0, 8, tt) * (1 - smoothstep(T_RHINE - 6, T_RHINE + 2, tt))
                * (0.55 + 0.45 * np.sin(2 * np.pi * (tt / 26 - 0.25))))
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(d[None] - c) / 1400 - tt / 40))
        rhine = smoothstep(T_RHINE - 4, T_RHINE + 4, tt) * (1 - smoothstep(T_GOLD - 4, T_GOLD + 3, tt))
        ripple = (0.5 + 0.5 * np.sin(2 * np.pi * (np.abs(d[None] - c) / 260 + tt / 6))) ** 3
        out[f0:f0 + 400] += light(ROSE, 0.36 * dawn * glow * open_) + light(RHINE, 0.55 * rhine * ripple * open_)
        for tg, u in glints:                                # a gold glint where the fill has yet to come
            a = tt[:, 0] - tg
            if a.max() < 0 or a.min() > 2.5:
                continue
            vg = u * reach(tg) - 0.02
            side = G.seg['Right'] if u * 1000 % 2 < 1 else G.seg['Left']
            cand = np.concatenate([side, G.seg['Porch Front'], G.seg['Porch Left'], G.seg['Porch Right']])
            pg = d[cand[np.argmin(np.abs(v[cand] - vg))]]
            env = np.where((a >= 0) & (a < 2.5), np.sin(np.pi * np.clip(a / 2.5, 0, 1)) ** 2, 0)
            out[f0:f0 + 400] += light(GOLD, 0.8 * env[:, None] * np.exp(-((d[None] - pg) / 14) ** 2) * open_)

    # each minute, with the harp: a soft gold ring opening from the middle of the porch over the part to fill
    for m in MARKS['minutes']:
        for f in range(int(m / DT), int((m + 3.5) / DT)):
            a = f * DT - m
            r = 1100 * (1 - np.exp(-a / 1.6))
            open_ = 1 - smoothstep(-0.03, 0.03, v - reach_t[f])
            out[f] += light(GOLD, 0.6 * np.exp(-a / 1.5) * np.exp(-((np.abs(d - c) - r) / 100) ** 2) * open_)

    # the fanfare: every note of the hero flashes white and gold out of the middle of the porch, the fire parting
    for tn, mm, dn, sec, s in fanfare():
        for f in range(int(tn / DT), min(F, int((tn + 1.4) / DT))):
            a = f * DT - tn
            r = 30 + 900 * s * (1 - np.exp(-a / 0.45))
            ring = np.exp(-((np.abs(d - c) - r) / (45 + 50 * s)) ** 2)
            e = np.exp(-a / 0.55)
            out[f] *= (1 - 0.45 * e * smoothstep(r + 60, r - 60, np.abs(d - c)))[:, None]
            out[f] += light(WHITE, 0.9 * s * e * ring) + light(GOLD, 0.6 * s * e * ring)
            out[f] += light(WHITE, 0.8 * s * np.exp(-a / 0.15) * np.exp(-((d - c) / (30 + 60 * s)) ** 2))
    # the Twilight: each of its chords a slow deep-red pulse, from the porch outward, as the gods' end is foretold
    for tn in sorted({round(x[0], 3) for x in twilight()}):
        for f in range(int(tn / DT), min(F, int((tn + 2.0) / DT))):
            a = f * DT - tn
            e = smoothstep(0, 0.15, a) * np.exp(-a / 0.8)
            out[f] = out[f] * (1 - 0.55 * e) + light(RED, 0.8 * e * np.exp(-np.abs(d - c) / 1300))
    return np.clip(out, 0, 1)


def chord_at(notes, t0, t1):
    """Pitch-class weights and the lowest note of the excerpt sounding between t0 and t1."""
    w, low = np.zeros(12), 127
    for n in notes:
        ov = min(n[0] + n[1], t1) - max(n[0], t0)
        if ov > 0:
            w[n[2] % 12] += ov * (1.5 if n[4] == 1 else 1.0)
            low = min(low, n[2])
    return w, low


def score(M, G):
    """The daybreak and the Rhine on the orchestra, a harp each minute, the brass to call them back."""
    o = Orchestra(M, level=3.0)
    notes = []
    for n in tidy(EX['notes']):              # gentler than the stage: velocities pulled in, the last bars fading out
        n = list(n)
        n[3] = float(np.clip(0.7 * n[3] + 16, 1, 90)) * float(np.interp(n[0], [T_END - 6, T_END], [1, 0.6]))
        notes.append(n)

    def role(t, d, m, v, h):
        if t < T_RHINE and h == 1 and m >= 45 and d >= 0.8:      # the dawn's long lines: cellos and clarinets
            return [('cellos' if m < 57 else 'violas', 0, 4, 0.65), ('clarinets', 0, -10, 0.3)]
        if T_RHINE <= t < T_GOLD and h == 0 and m >= 74 and d < 0.6:   # the river's figures on the woodwinds
            return [('flutes' if m >= 79 else 'clarinets', 0, -4, 0.45)]
        return None

    o.tutti(notes, size=lambda t: 0.3, role=role, pan=lambda t, m: 0.25 * np.sin(2 * np.pi * t / 41))

    # each minute: a harp rolls the orchestra's chord, a soft horn holding its root under it
    for m in MARKS['minutes']:
        w, low = chord_at(EX['notes'], m - 0.5, m + 2.5)
        pcs = [int(p) for p in np.argsort(w)[::-1][:3] if w[p] > 0]
        root = low - 12 if low >= 48 else low
        roll = [root] + [n for n in range(48, 86) if n % 12 in pcs][:9]
        for j, n in enumerate(roll):
            o.play('harp', n, m + 0.07 * j, 2.2, 80 - 2 * j, pan=0.0, gain=0.85)
        horn = root + 12 * int(np.ceil((41 - root) / 12)) if root < 41 else root
        o.play('horns', horn, m + 0.05, 3.0, 62, pan=-0.2, gain=0.4)

    # the call-back from the balcony: Siegfried the hero on horns, again on trumpets peaking as the fill meets, then the
    # Twilight of the Gods on trombones and horns, a gong under its first chord
    for tn, mm, dn, sec, s in fanfare():
        o.play(sec, mm, tn, dn + 0.1, int(70 + 36 * s), pan=0.0, gain=0.55 + 0.35 * s)
        if sec == 'trumpets':
            o.play('horns', mm - 12, tn, dn + 0.1, 92, pan=-0.1, gain=0.5)
    hero_end = T_HERO2 + 3.8333 * HERO_BEAT
    for n in (38, 45, 50):                   # D major under the trumpets' close
        o.play('trombones', n, hero_end - 1.0, 1.6, 84, pan=0.05, gain=0.45)
    o.hit('timpani roll', FULL - 1.2, 84, pitch=-2, gain=0.35)
    o.hit('timpani', FULL, 100, pitch=-2, gain=0.5)
    for tn, mm, dn in twilight():
        if mm >= 50:
            o.play('horns' if mm >= 62 else 'trombones', mm, tn, dn + 0.2, 76, pan=0.0, gain=0.5)
        else:
            o.play('tuba', mm + 12 if mm < 36 else mm, tn, dn + 0.2, 80, pan=0.0, gain=0.45)
    o.hit('gong', T_TWILIGHT, 70, gain=0.3)
