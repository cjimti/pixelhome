"""The Night of Nights: Halloween Town shows off, and its king rises out of the fountain in fire.

The town comes up out of the dark: a violet sky, orange windows, green mist creeping in from both ends, a bell
tolling twice. The citizens' march starts quietly (bassoon and pizzicato) and the town turns up a run at a time
on the downbeats: a jack-o'-lantern over the porch, two ghosts on the porch sides, a bat on each wing, a black cat
out at the end of the right wing. The march comes round again full (trombones, horns, choir) and the citizens
sing it between them, a note each in turn. A scarecrow rides in from the free end of Right on a galloping
skeleton horse, and at the porch it bursts into flame: the fire pours down into the fountain over the porch, a
pillar of flame climbs, and out of it rises the Pumpkin King, bright white skull and pinstripes, to his own
theme in A major on the whole band. The town cheers him on the last bars of the march, the wings flashing orange
and green.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events, so every
pop, note and flame lands on the music."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, BONE, WHITE,
                                 GOLD, MOON)

CODE = 'NM01'
TITLE = 'The Night of Nights'
KIND = 'show'
DESCRIPTION = ('Halloween Town turns up a run at a time and sings its march, a note each. A scarecrow rides in and '
               'bursts into flame, and out of the fountain rises the Pumpkin King.')
VOICEOVER = ('Every year, one town waits all year for a single night. Tonight is that night.')

STRAW = hexc('#e8c040')
CAT = hexc('#40ff20')


def compose():
    C = Chart()
    C.rest(3.5)                                             # the town comes up out of the dark, a bell tolls twice
    C.mark('march')
    C.play('town', style='march', bpm=120, tag='gather')    # quietly: the citizens turn up a bar at a time
    C.mark('sing')
    C.play('town', style='march', bpm=120, tag='sing')      # full: they sing it between them
    C.mark('ride')
    C.play('town', style='drive', bars=(4, 8), bpm=132, tune=False, tag='ride')   # the scarecrow gallops in
    C.mark('fire')
    C.rest(2.4)                                             # he bursts into flame; the fire climbs the fountain
    C.mark('king')
    C.play('king', style='waltz', bars=(8, 16), bpm=92, major=True, tag='king')
    C.mark('cheer')
    C.play('town', style='march', bars=(4, 8), bpm=126, tag='cheer')
    C.rest(2.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def citizens(S):
    """Where each citizen stands and how it is drawn: (name, path distance, pixels)."""
    pumpkin = [(2, PUMPKIN, 1.0), (1, None, 0), (0, ORANGE, 1.0), (-1, None, 0), (-2, PUMPKIN, 1.0)]
    ghost = [(1, WHITE, 0.9), (0, MOON, 0.8), (-1, MOON, 0.5), (-2, MOON, 0.25)]
    bat = [(2, VIOLET, 0.9), (1, VIOLET, 0.5), (0, BONE, 0.3), (-1, VIOLET, 0.5), (-2, VIOLET, 0.9)]
    cat = [(2, CAT, 1.0), (1, None, 0), (0, CAT, 1.0), (-1, VIOLET, 0.2), (-2, VIOLET, 0.2)]
    return [('pumpkin', S.mid, pumpkin), ('ghost', S.at('Porch Left', 0.55), ghost),
            ('ghost', S.at('Porch Right', 0.45), ghost), ('bat', S.at('Left', 0.5), bat),
            ('bat', S.at('Right', 0.35), bat), ('cat', S.at('Right', 0.85), cat)]


def render(G, seed=1):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    cast = citizens(S)
    gather = C.downbeats('gather')
    arrive = [gather[min(i + 1, len(gather) - 1)] for i in range(len(cast))]     # one per bar, after the first
    sung = C.tunes('sing') + C.tunes('cheer')
    sung_t = np.array([n[0] for n in sung])
    king = C.tunes('king')
    king_t = np.array([n[0] for n in king])
    beats = np.array([b[0] for b in C.beats])
    downs = np.array(C.downbeats())
    t_ride, t_fire, t_king, t_cheer = M['ride'], M['fire'], M['king'], M['cheer']
    p_right = S.L + 40
    p_burn = S.at('Porch Right', 0.5)

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 3.0, t)
        beat = pulse(t, beats, 0.15)
        fr = S.town(t, lv=up * (0.9 + 0.15 * beat), mist=keys(t, [(0, 0.3), (3, 1.0), (t_fire, 1.0),
                                                                     (t_king + 4, 0.5)]))
        # the bell tolls twice: a pale wash out from the porch
        for tb in (0.6, 2.0):
            a = t - tb
            if 0 <= a < 1.5:
                fr += light(MOON, 0.6 * np.exp(-a / 0.5) * smoothstep(900 * a + 60, 900 * a - 60, np.abs(d - mid)))

        # the citizens: each pops up on its downbeat with a flash, then sings its notes in turn
        k = int(np.searchsorted(sung_t, t, side='right')) - 1
        singer = k % len(cast) if k >= 0 and t - sung_t[k] < 0.6 else -1
        for i, (name, p, px) in enumerate(cast):
            if t < arrive[i] or (t_fire <= t < t_cheer and name != 'pumpkin'):
                continue
            a = t - arrive[i]
            lvl = 0.75 * smoothstep(0, 0.12, a) + 0.6 * np.exp(-a / 0.3)
            if name == 'bat':
                px = [(o, c, v * (0.5 + 0.5 * abs(np.sin(2 * np.pi * 2.5 * t))) if abs(o) == 2 else v)
                      for o, c, v in px]
            if i == singer:
                s = np.exp(-(t - sung_t[k]) / 0.25)
                lvl += 0.5 * s
                fr += light(px[0][1], 0.7 * s * S.run_at(p) * (0.4 + 0.6 * S.blob(p, 160)))
            if a < 0.8:
                fr += light(px[0][1], 0.9 * np.exp(-a / 0.25) * S.run_at(p))
            fr = S.sprite(fr, p, px, min(lvl, 1.3))

        # the bridge of the sung march: a wave runs out from the porch on each downbeat
        if M['sing'] <= t < t_ride:
            for t0 in downs[(downs <= t) & (downs > t - 1.2)]:
                a = t - t0
                fr += light(SLIME, 0.55 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - mid) - 1200 * a) / 70) ** 2))

        # the scarecrow on his skeleton horse, galloping in from the free end of Right to the porch
        if t_ride <= t < t_fire + 0.4:
            u = smoothstep(t_ride, t_fire, t)
            p = p_right + (p_burn - p_right) * u
            hop = 0.8 + 0.2 * abs(np.sin(2 * np.pi * 2.2 * t))
            fr = S.sprite(fr, p, [(2, STRAW, 1.0), (1, STRAW, 0.9), (0, ORANGE, 0.6), (-1, STRAW, 0.7),
                                  (-3, BONE, 0.8 * hop), (-4, BONE, 0.6), (-5, BONE, 0.8 * hop), (-6, BONE, 0.4)],
                          1.0, -1)
            fr += light(GOLD, 0.25 * S.blob(p, 60))
        # he bursts into flame: fire runs down Porch Right into the fountain, and a pillar climbs there
        if t_fire <= t < t_king + 6:
            a = t - t_fire
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * S.blob(p_burn, 80))
            front = p_burn + (mid - p_burn) * smoothstep(0, 1.2, a)
            fr += light(FLAME, 0.9 * S.span(min(front, p_burn), max(front, p_burn)) * (a < 3.0) *
                        (0.7 + 0.3 * np.sin(23 * t + d / 9)))
            h = smoothstep(0.8, t_king - t_fire, a) * (1 - smoothstep(4, 6, t - t_king))
            reach = 30 + 330 * h
            flick = 0.75 + 0.25 * np.sin(17 * t + d / 7) * np.sin(5 * t - d / 13)
            fr += light(FLAME, 1.0 * h * smoothstep(reach + 30, reach - 30, np.abs(d - mid)) * flick)
            fr += light(GOLD, 0.8 * h * smoothstep(reach * 0.5 + 20, reach * 0.5 - 20, np.abs(d - mid)))

        # the Pumpkin King rises: each note of his theme throws flame out along the roof; then he stands and bows
        if t >= t_king:
            a = t - t_king
            lvl = smoothstep(0.0, 1.2, a)
            for j in np.flatnonzero((king_t <= t) & (king_t > t - 1.0)):
                b = t - king_t[j]
                side = 1 if j % 2 else -1
                front = mid + side * (300 + 900 * b)
                fr += light(FLAME, 0.9 * np.exp(-b / 0.4) * np.exp(-((d - front) / 90) ** 2))
            if t >= t_cheer:                        # the town cheers: wings flash orange and green on the beat
                wing = S.wings | S.run['Side']
                c = PUMPKIN if int((t - t_cheer) / (60 / 126)) % 2 else SLIME
                fr += light(c, 0.6 * beat * wing)
            bow = 1.0 - 0.3 * smoothstep(D - 2.5, D - 1.5, t) + 0.3 * smoothstep(D - 1.2, D - 0.6, t)
            fr = S.jack(fr, mid + 9, lvl * bow, facing=-1, glow=0.6 * lvl)
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.4)
    p_burn = S.at('Porch Right', 0.5)
    parts = {
        ('gather', 'tune'): [('bassoons', 0, 4, 0.7), ('pizz', 12, -4, 0.5)],
        ('gather', 'bass'): [('basses pizz', 0, 0, 0.6), ('cellos pizz', 12, -8, 0.4)],
        ('gather', 'chord'): [('pizz', 0, -10, 0.35)],
        ('sing', 'tune'): [('trombones', 0, 6, 0.75), ('horns', 0, 0, 0.6), ('choir', 0, 0, 0.8),
                           ('xylo', 12, -6, 0.35)],
        ('sing', 'chord'): [('horns', 0, -12, 0.35), ('pizz', 0, -6, 0.4)],
        ('ride', 'bass'): [('tuba', -12, 4, 0.8), ('cellos', 0, -4, 0.5)],
        ('ride', 'chord'): [('trumpets', 0, -10, 0.35), ('violins', 12, -8, 0.4)],
        ('king', 'tune'): [('horns', 0, 10, 0.9), ('trumpets', 0, 0, 0.55), ('violins', 12, 0, 0.6),
                           ('choir', 0, 4, 0.9)],
        ('king', 'bass'): [('tuba', -12, 6, 0.8), ('basses', 0, 0, 0.55), ('timpani', 0, 8, 0.4)],
        ('king', 'chord'): [('trombones', 0, -8, 0.45), ('violas', 0, -8, 0.4)],
        ('cheer', 'tune'): [('trumpets', 0, 8, 0.7), ('trombones', 0, 6, 0.6), ('violins', 12, 0, 0.55),
                            ('choir', 0, 4, 0.8), ('xylo', 12, 0, 0.4)],
        ('cheer', 'chord'): [('horns', 0, -6, 0.5)],
    }
    B.perform(C.events, parts)
    # the town comes up: a long low chord and a bell
    for m in (40, 52, 55, 59):
        B.play('choir', m + 12, 0.0, 3.6, 70, gain=0.3)
    B.play('cellos trem', 40, 0.0, 3.6, 70, gain=0.5)
    for tb in (0.6, 2.0):
        B.hit('gong', tb, 100, pitch=-3, gain=0.5)
    # every citizen arrives with a pop of its own
    gather = C.downbeats('gather')
    pans = [0.0, -0.35, 0.35, -0.7, 0.55, 0.85]
    for i, pp in enumerate(pans):
        t = gather[min(i + 1, len(gather) - 1)]
        B.hit('slapstick' if i % 2 else 'wood', t, 110, gain=0.7, pan=pp)
    # the ride: hooves from the right end to the porch, then the fire and the king's pillar of flame
    B.effects([(0, -2), (M['ride'], 0), (M['fire'], 2), (M['king'] + 1, -6)])
    B.gallop(M['ride'], M['fire'], beat=60 / 132 * 1.0, pan=lambda tt: 0.9 - 0.75 * (tt - M['ride']) / (M['fire'] - M['ride']))
    B.boom(M['fire'], pan=S.pan(p_burn))
    B.fire(M['fire'], M['king'] + 5.0, level=lambda tt: np.clip(1.2 - 0.12 * (tt - M['fire']), 0.3, 1.0), pan=0.0)
    B.hit('cymbal swell', M['king'] - 1.6, 110, gain=0.6)
    B.hit('crash', M['king'], 120, gain=0.6)
    B.hit('timpani roll', M['fire'] + 0.2, 100, gain=0.5)
    B.hit('crash', M['cheer'], 118, gain=0.5)
    B.hit('crash', M['end'] - 2.5, 124, gain=0.6)
    B.hit('bass drum', M['end'] - 2.5, 124, gain=0.7)
    B.finish()
