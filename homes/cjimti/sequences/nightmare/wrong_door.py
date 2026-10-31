"""Bring Him Back: Lock, Shock and Barrel fetch the man in red, and get the wrong one first.

The Halloween town at night. Lock, Shock and Barrel pop up over the porch (the devil, the witch and the skeleton, a
slapstick each) and scamper off along Porch Right and the right wing to their own patter, out of the free end of
Right, through the holiday doors. The far end of Right blooms in pastel stripes (an egg-coloured door) and they
haul a sack back in to the porch. It bursts open with a slide whistle and out hops a big pastel bunny, pink ears
first, lilac body, the porch flooding pink, lemon and lilac on every hop to its own perky tune. The Pumpkin King
flares up on Porch Front in a roar of low brass and the whole house flashes orange: wrong one. The bunny hops off
out of the end of Right and Lock, Shock and Barrel scurry after it.

Second try: the right wing turns into a snowy Christmas town (coloured bulbs, snow, a warm golden door). The
three creep in from the free end; three knocks flash at the door; Santa steps out to the first notes of his own
carol and the sack comes down over him with a whoosh and a thump. They lumber back to the porch in their walking
bathtub (white enamel, gold claw feet stepping), the sack bumping behind, red flashing through it as he
struggles. At the porch the sack falls away: Jack greets Santa grandly to Santa's carol on warm brass, gold
sparks on every note, bows, and takes the red coat himself; his own theme rings out in A major as he orders his
guest taken somewhere comfortable. Lock, Shock and Barrel drag Santa off the other way to Oogie Boogie's shuffle,
down Porch Left and the left wing and away along Side, a green glow of the lair swallowing them.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() read its marks and events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, THEMES, pulse, ORANGE, PUMPKIN, FLAME, SLIME, BONE, WHITE,
                                 GOLD, RED, WARM, MOON, UV, VIOLET)

CODE = 'NM12'
TITLE = 'Bring Him Back'
KIND = 'show'
DESCRIPTION = ('Lock, Shock and Barrel go through the holiday doors and come back with a pastel bunny, so Jack sends '
    'them again: watch the right wing turn to snow, the sack come down over Santa, and the walking bathtub '
    'haul him home.')
VOICEOVER = 'Jack sent Lock, Shock and Barrel to fetch Santa Claus. What could possibly go wrong?'

PINK = hexc('#ff60b8')
LEMON = hexc('#fff040')
LILAC = hexc('#a060ff')
MINT = hexc('#50ffb0')
SACK = hexc('#c08030')
ENAMEL = hexc('#f0f4ff')

# an original perky tune for the bunny, C major (kept here: it belongs to this scene alone)
BUNNY = dict(meter=4, bpm=144, name='The wrong one: a pastel bunny hops in, C major',
             melody=[(0, .5, 'G4'), (.5, .5, 'C5'), (1, .5, 'E5'), (1.5, .5, 'C5'), (2, 1, 'D5'), (3, 1, 'G4'),
                     (4, .5, 'A4'), (4.5, .5, 'C5'), (5, .5, 'F5'), (5.5, .5, 'C5'), (6, 1, 'E5'), (7, 1, 'C5'),
                     (8, .5, 'G4'), (8.5, .5, 'C5'), (9, .5, 'E5'), (9.5, .5, 'G5'), (10, .5, 'F5'),
                     (10.5, .5, 'D5'), (11, 1, 'B4'),
                     (12, .5, 'C5'), (12.5, .5, 'G4'), (13, .5, 'E4'), (13.5, .5, 'G4'), (14, 2, 'C5')],
             chords=[(0, 2, 'C'), (2, 2, 'G7'), (4, 2, 'F'), (6, 2, 'C'), (8, 2, 'C'), (10, 2, 'G7'),
                     (12, 4, 'C')])


def play_local(C, name, theme, **kw):
    """Play a theme that lives in this file through the shared Chart, without leaving it in THEMES."""
    THEMES[name] = theme
    try:
        return C.play(name, **kw)
    finally:
        del THEMES[name]



class Offstage(Stage):
    """The shared Stage, but a sprite whose centre is past either free end is drawn partly or not at all instead of
    being clamped onto the end pixel, so things can walk in and out of the ends."""

    def sprite(self, fr, p, pixels, lvl=1.0, facing=1, cut=True):
        if lvl <= 0:
            return fr
        if p < self.pp[0]:
            k0 = int(np.floor((p - self.pp[0]) / 6.1))
        elif p > self.pp[-1]:
            k0 = self.N - 1 + int(np.ceil((p - self.pp[-1]) / 4.0))
        else:
            k0 = self.k(p)
        offs = [o for o, _, _ in pixels]
        if cut:
            for o in range(min(offs) - 1, max(offs) + 2):
                k = k0 + facing * o
                if 0 <= k < self.N:
                    fr[self.path[k]] *= 1 - min(1.0, lvl * 1.5) * (0.9 if min(offs) <= o <= max(offs) else 0.5)
        for o, col, v in pixels:
            k = k0 + facing * o
            if 0 <= k < self.N and col is not None:
                fr[self.path[k]] += light(col, lvl * v)
        return fr


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the town comes up
    C.mark('out')
    C.play('trio', style='gallop', bpm=360, tag='out')              # they pop up and scamper off to the doors
    C.mark('door1')
    C.rest(1.2)                                                     # the egg door blooms at the end of Right
    C.mark('haul1')
    C.play('trio', style='gallop', bars=(0, 4), bpm=380, tag='haul1')   # they haul a sack back in
    C.mark('bunny')
    play_local(C, 'nm12 bunny', BUNNY, style='march', tag='bunny')
    C.mark('angry')
    C.rest(2.6)                                                     # Jack flares: wrong one
    C.mark('back')
    C.play('trio', style='drive', bars=(4, 8), bpm=400, tag='back')     # the bunny hops off, they scurry after
    C.mark('xmas')
    C.play('wonder', style='arp', bars=(0, 4), bpm=330, tag='xmas')     # the right wing turns to snow
    C.mark('knock')
    C.play('santa', style='hold', bars=(0, 1), bpm=104, tag='ho')   # knock, knock, knock: Santa steps out
    C.mark('grab')
    C.rest(1.2)                                                     # the sack comes down over him
    C.mark('tub')
    C.play('trio', style='drive', bpm=400, tag='tub')               # the walking bathtub lumbers home
    C.mark('greet')
    C.play('santa', style='march', bars=(0, 4), bpm=104, tag='greet')   # Jack greets him grandly
    C.mark('order')
    C.play('king', style='waltz', bars=(0, 2), bpm=100, major=True, tag='order')   # somewhere comfortable...
    C.mark('away')
    C.play('boogey', style='shuffle', bars=(0, 4), bpm=132, tag='away')  # ...Oogie Boogie's
    C.rest(1.8)
    C.mark('end')
    return C


C = compose()
M = C.marks
D = M['end']


def sack(S, fr, p, lvl, t, wriggle=0.0, red=0.0):
    px = []
    for o in range(-3, 4):
        w = 0.75 + 0.25 * np.sin(1.9 * o + 9 * t) * wriggle
        px.append((o, SACK, 0.8 * w))
    px[3] = (0, RED, 0.9 * red) if red > 0.05 else px[3]
    return S.sprite(fr, p, px, lvl, 1)


def bunny(S, fr, p, lvl, facing, hop=0.0):
    px = [(5, PINK, 1.0), (4, None, 0), (3, PINK, 1.0), (2, WHITE, 0.95), (1, WHITE, 0.9), (0, PINK, 0.7)]
    px += [(-o, LILAC, 0.95) for o in range(1, 8)] + [(-8, WHITE, 1.0)]
    fr = S.sprite(fr, p, px, lvl * (0.85 + 0.25 * hop), facing)
    return fr


def tub(S, fr, p, lvl, t, step):
    """The walking bathtub: a white enamel tub, gold claw feet at each end stepping in turn."""
    px = [(o, ENAMEL, 0.75) for o in range(-7, 8)]
    l, r = (1.0, 0.25) if step % 2 else (0.25, 1.0)
    px[0], px[-1] = (-7, GOLD, l), (7, GOLD, r)
    return S.sprite(fr, p, px, lvl, 1)


def trio_glow(S, fr, p, t, downs, lvl=1.0):
    """Lock, Shock and Barrel's colours around them and on their run, cycling devil red, witch violet, skeleton green on
    each bar, and a wash over both wings on every downbeat."""
    k = int(np.searchsorted(downs, t, side='right'))
    col = (RED, VIOLET, SLIME)[k % 3]
    hit = pulse(t, downs, 0.3)
    fr += light(col, lvl * ((0.6 + 0.3 * hit) * S.blob(p, 140) + (0.3 + 0.3 * hit) * S.run_at(p)))
    fr += light(col, lvl * 0.45 * hit * S.wings)
    return fr


def render(G, seed=12):
    S = Offstage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    right = S.run['Right']
    r0, r1 = S.at('Right', 0.0), S.at('Right', 1.0)
    beats = np.array([b[0] for b in C.beats])
    bunny_beats = np.array([b[0] for b in C.beats if b[2] == 'bunny'])
    greet_t = np.array([n[0] for n in C.tunes('greet')])
    order_t = np.array([n[0] for n in C.tunes('order')])
    tub_beats = np.array([b[0] for b in C.beats if b[2] == 'tub' and b[1] in (0, 3)])
    tm = {k: v for k, v in M.items()}
    downs = np.array(C.downbeats('out') + C.downbeats('haul1') + C.downbeats('back') + C.downbeats('tub') +
                     C.downbeats('away'))
    pop_t = tm['bunny'] + 4 * 60 / 144 * 0 + 0.0          # the sack bursts on the bunny's first note
    knocks = [tm['knock'] + 0.15 + 0.38 * i for i in range(3)]
    door = S.at('Right', 0.55)
    p_king = mid - 70
    p_santa = mid + 70

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 2.0, t)
        beat = pulse(t, beats, 0.15)
        fr = S.town(t, lv=up * (0.85 + 0.12 * beat), mist=0.6)

        # ---- Lock, Shock and Barrel pop up and scamper off along Porch Right and the right wing
        if tm['out'] <= t < tm['door1']:
            a = t - tm['out']
            p = keys(t, [(tm['out'] + 2.0, mid + 40), (tm['door1'], L + 60)])
            if a < 0.8:
                fr += light(SLIME, 0.8 * np.exp(-a / 0.25) * S.porch)
            fr = trio_glow(S, fr, min(p, L), t, downs, smoothstep(0, 0.3, a) * smoothstep(L + 60, L - 40, p))
            fr = S.trio(fr, p, smoothstep(0, 0.15, a), 1, t=t, bounce=1.0)

        # ---- the egg door: pastel stripes bloom from the end of Right while it is open
        egg = smoothstep(tm['door1'], tm['door1'] + 0.6, t) * (1 - smoothstep(tm['bunny'] - 1.0, tm['bunny'], t))
        egg += smoothstep(tm['back'] + 1.5, tm['back'] + 2.2, t) * (1 - smoothstep(tm['xmas'] - 0.3, tm['xmas'] + 0.4, t))
        if egg > 0:
            reach = smoothstep(r1 - 80 - 380 * egg, r1 - 380 * egg, d)
            band = (np.floor((d - 30 * t) / 24) % 3).astype(int)
            cols = np.array([PINK, LEMON, LILAC])[band]
            fr = fr * (1 - 0.7 * egg * reach * right)[:, None] + (0.55 * egg * reach * right)[:, None] * cols

        # ---- they haul the sack back in from the end of Right to the porch
        if tm['haul1'] <= t < tm['bunny']:
            p = keys(t, [(tm['haul1'], L + 40), (tm['bunny'] - 0.3, mid + 60)])
            fr = trio_glow(S, fr, min(p, L), t, downs)
            fr = sack(S, fr, p - 20, 1.0, t, wriggle=0.5)
            fr = S.trio(fr, p + 25, 1.0, -1, t=t, bounce=1.0)

        # ---- the sack bursts: a big pastel bunny hops about the porch
        if tm['bunny'] <= t < tm['back'] + 2.6:
            a = t - pop_t
            if a < 0.9:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S.blob(mid + 40, 120))
                fr += S.burst([(pop_t, 0.9, mid + 40)], t, seed=3, colors=(PINK, LEMON, LILAC, MINT))
            hp = pulse(t, bunny_beats, 0.18)
            k = int(np.searchsorted(bunny_beats, t, side='right'))
            if t < tm['angry']:
                p = mid + 40 + 110 * np.sin(k * 1.3)
                facing = 1 if k % 2 else -1
                col = [PINK, LEMON, LILAC][k % 3]
                fr += light(col, 0.55 * hp * S.porch + 0.25 * S.porch)
                fr += light(col, 0.35 * hp * S.wings)
            elif t < tm['back']:                            # cowering under Jack's roar
                p = mid + 40 + 110 * np.sin(len(bunny_beats) * 1.3)
                facing, hp = 1, 0.0
            else:                                           # hops off out of the end of Right
                p = keys(t, [(tm['back'], mid + 40 + 110 * np.sin(len(bunny_beats) * 1.3)), (tm['back'] + 2.4, L + 80)])
                facing = 1
                hp = abs(np.sin(2 * np.pi * 3 * t))
                fr += light(PINK, 0.35 * S.blob(p, 70))
            fr = bunny(S, fr, p, 1.0, facing, hp)
            if tm['haul1'] <= t < tm['angry']:
                fr = S.trio(fr, mid + 260, 0.9, -1, t=t, bounce=0.5)

        # ---- Jack flares: wrong one!
        if tm['angry'] <= t < tm['back'] + 1.5:
            a = t - tm['angry']
            if a < 0.7:
                fr += light(ORANGE, 0.8 * np.exp(-a / 0.2) * np.ones(G.N))
            shake = 6 * np.sin(2 * np.pi * 9 * t) * np.exp(-a / 0.8)
            lvl = smoothstep(0, 0.2, a) * (1 - smoothstep(tm['back'] + 0.6, tm['back'] + 1.5, t))
            flick = 0.75 + 0.25 * np.sin(17 * t + d / 7) * np.sin(5 * t - d / 13)
            fr += light(FLAME, 0.85 * lvl * S.porch * flick)
            fr += light(RED, 0.5 * lvl * (S.wings | S.run['Side']) * (0.6 + 0.4 * np.exp(-a / 0.6)))
            fr = S.jack(fr, p_king + shake, lvl, facing=1, glow=0.4)
        if tm['back'] <= t < tm['xmas']:                    # and they scurry after it
            p = keys(t, [(tm['back'] + 0.4, mid + 240), (tm['back'] + 2.8, L + 60)])
            fr = trio_glow(S, fr, min(p, L), t, downs, smoothstep(L + 60, L - 40, p))
            fr = S.trio(fr, p, 1.0, 1, t=t, bounce=1.0)

        # ---- the Christmas door: the right wing turns to a snowy Christmas town
        xm = smoothstep(tm['xmas'], tm['xmas'] + 1.5, t) * (1 - smoothstep(tm['tub'] + 1.0, tm['tub'] + 4.5, t))
        if xm > 0:
            reach = smoothstep(r1 - (r1 - r0 + 60) * smoothstep(tm['xmas'], tm['xmas'] + 1.5, t) - 40,
                               r1 - (r1 - r0 + 60) * smoothstep(tm['xmas'], tm['xmas'] + 1.5, t), d) * right
            w = xm * reach
            fr = fr * (1 - 0.85 * w)[:, None] + S.christmas(t, lv=1.0) * w[:, None]
            fr += S.snowfall(t, 0.8) * w[:, None]
            fr += light(GOLD, 0.7 * xm * S.blob(door, 22) * (t < tm['tub'] + 0.5))
        if tm['xmas'] + 1.0 <= t < tm['grab']:              # they creep in from the free end to the door
            p = keys(t, [(tm['xmas'] + 1.0, L + 40), (tm['knock'], door + 70)])
            fr = S.trio(fr, p, 1.0, -1, t=t, bounce=0.3)
        for tk in knocks:
            a = t - tk
            if 0 <= a < 0.4:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.08) * S.blob(door, 40))
        if tm['knock'] + 1.3 <= t < tm['grab'] + 0.15:      # Santa steps out
            a = t - tm['knock'] - 1.3
            fr += light(WARM, 0.5 * smoothstep(0, 0.4, a) * S.blob(door, 80))
            fr = S.santa(fr, door + 10, smoothstep(0, 0.3, a), facing=1)
        if tm['grab'] <= t < tm['tub']:                     # the sack comes down over him
            a = t - tm['grab']
            if a < 0.6:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * S.blob(door, 90))
            fr = sack(S, fr, door + 10, smoothstep(0, 0.1, a), t, wriggle=1.0, red=0.5 + 0.5 * np.sin(14 * t))
            fr = S.trio(fr, door + 70, 1.0, -1, t=t, bounce=1.0)

        # ---- the walking bathtub hauls him home to the porch
        if tm['tub'] <= t < tm['greet'] + 0.6:
            p = keys(t, [(tm['tub'] + 0.3, door + 50), (tm['greet'] - 0.2, p_santa + 90)])
            step = int(np.searchsorted(tub_beats, t, side='right'))
            bump = pulse(t, tub_beats, 0.12)
            fr = trio_glow(S, fr, p, t, downs, 0.8)
            fr += light(ENAMEL, 0.35 * S.blob(p, 50))
            fr = sack(S, fr, p - 75 + 6 * bump, 1.0, t, wriggle=1.0, red=0.6 * pulse(t, tub_beats[::2], 0.2))
            fr = tub(S, fr, p, 1.0, t, step)
            fr = S.trio(fr, p + 18, 1.0, -1, gap=3, t=t, bounce=0.6)
            fr += light(ENAMEL, 0.25 * bump * S.blob(p, 60))

        # ---- Jack greets Santa grandly, and takes his job
        if tm['greet'] <= t < tm['away'] + 1.0:
            a = t - tm['greet']
            if a < 0.8:                                     # the sack falls away
                fr += light(GOLD, 0.8 * np.exp(-a / 0.25) * S.porch)
            fr += light(GOLD, 0.4 * S.porch + 0.3 * S.wings)
            for j in np.flatnonzero((greet_t <= t) & (greet_t > t - 1.0)):
                b = t - greet_t[j]
                side = 1 if j % 2 else -1
                front = mid + side * (200 + 900 * b)
                fr += light(WHITE if j % 4 == 0 else GOLD, 0.9 * np.exp(-b / 0.4) * np.exp(-((d - front) / 90) ** 2))
            bow_t = M['greet'] + 4 * 60 / 104 * 2           # a deep bow halfway through the carol
            bow = 1 - 0.5 * smoothstep(bow_t - 0.3, bow_t, t) * (1 - smoothstep(bow_t + 0.6, bow_t + 1.0, t))
            coat = smoothstep(bow_t + 1.0, bow_t + 2.0, t)
            fr = S.jack(fr, p_king, smoothstep(0, 0.4, a) * bow, facing=1, glow=0.4)
            if coat > 0:                                    # the red coat goes on
                for o in range(5, 13):
                    k = S.k(p_king) - o
                    if 0 <= k < G.N:
                        fr[S.path[k]] += light(RED, 0.8 * coat)
            if t < tm['away']:
                fr = S.santa(fr, p_santa, 1.0, facing=-1)
                fr += light(WARM, 0.3 * S.blob(p_santa, 60))
                fr = S.trio(fr, p_santa + 160, 0.9, -1, t=t, bounce=0.5)
        if tm['order'] <= t < tm['away']:                   # his theme in major: he orders his guest taken away
            for j in np.flatnonzero((order_t <= t) & (order_t > t - 1.0)):
                b = t - order_t[j]
                fr += light(FLAME, 0.7 * np.exp(-b / 0.35) * np.exp(-((np.abs(d - p_king) - 150 - 1000 * b) / 80) ** 2))

        # ---- Lock, Shock and Barrel drag Santa off the other way, to Oogie Boogie
        if tm['away'] <= t:
            a = t - tm['away']
            p = keys(t, [(tm['away'], p_santa), (tm['end'] - 1.6, -120)])
            glow = smoothstep(tm['away'], tm['away'] + 2.5, t)
            fr += light(SLIME, 0.45 * glow * (0.6 + 0.4 * beat) * S.run['Side'])
            fr += light(UV, 0.4 * glow * S.run['Side'])
            fr = trio_glow(S, fr, max(p - 40, 0), t, downs)
            fr = S.santa(fr, p, 1.0, facing=-1)
            fr = S.trio(fr, p - 70, 1.0, -1, t=t, bounce=1.0)
            if t > tm['end'] - 1.6:
                b = t - (tm['end'] - 1.6)
                fr += light(SLIME, 0.8 * np.exp(-b / 0.3) * S.run['Side'])
        out[f] = fr * float(smoothstep(D, D - 1.2, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Offstage(G)
    B = Band(M_, level=2.4)
    from pixelhome.audio import slide
    door = S.at('Right', 0.55)
    pR = S.pan(S.at('Right', 0.8))
    parts = {
        ('out', 'tune'): [('clarinets', 0, 4, 0.75), ('bassoons', -12, 0, 0.5), ('xylo', 12, -8, 0.3)],
        ('out', 'bass'): [('tuba', -12, -4, 0.6), ('basses pizz', 0, -6, 0.4)],
        ('out', 'chord'): [('pizz', 0, -6, 0.4)],
        ('haul1', 'tune'): [('bassoons', 0, 4, 0.7), ('clarinets', 12, -4, 0.45)],
        ('haul1', 'bass'): [('tuba', -12, -2, 0.6)],
        ('haul1', 'chord'): [('pizz', 0, -8, 0.35)],
        ('bunny', 'tune'): [('xylo', 12, 0, 0.55), ('flutes', 0, 0, 0.6), ('pizz', 12, -4, 0.4)],
        ('bunny', 'bass'): [('bassoons', -12, 0, 0.6), ('basses pizz', 0, -6, 0.4)],
        ('bunny', 'chord'): [('pizz', 0, -6, 0.4), ('clarinets', 0, -14, 0.25)],
        ('bunny', 'snare'): [('triangle', 0, -20, 0.25)],
        ('back', 'tune'): [('clarinets', 0, 4, 0.7), ('xylo', 12, -6, 0.35), ('violins', 12, -10, 0.3)],
        ('back', 'bass'): [('tuba', -12, 0, 0.6)],
        ('back', 'chord'): [('pizz', 0, -6, 0.35)],
        ('xmas', 'tune'): [('flutes', 0, 0, 0.6), ('glock', 12, -6, 0.35)],
        ('xmas', 'arp'): [('celesta', 12, 0, 0.45), ('harp', 0, -6, 0.4)],
        ('xmas', 'pedal'): [('cellos', 0, -12, 0.4)],
        ('ho', 'tune'): [('horns', 0, 6, 0.8)],
        ('ho', 'hold'): [('horns', 0, -16, 0.3), ('violas', 0, -12, 0.3)],
        ('ho', 'pedal'): [('cellos', 0, -10, 0.4)],
        ('tub', 'tune'): [('bassoons', 0, 6, 0.75), ('clarinets', 0, 0, 0.55), ('xylo', 12, -8, 0.3)],
        ('tub', 'bass'): [('tuba', -12, 0, 0.7)],
        ('tub', 'chord'): [('pizz', 0, -6, 0.35)],
        ('greet', 'tune'): [('horns', 0, 8, 0.85), ('trumpets', 0, -4, 0.4), ('choir', 0, 0, 0.6)],
        ('greet', 'bass'): [('tuba', -12, 0, 0.6), ('basses', 0, -8, 0.45)],
        ('greet', 'chord'): [('trombones', 0, -12, 0.35), ('violas', 0, -10, 0.35)],
        ('greet', 'snare'): [('snare', 0, -20, 0.2)],
        ('order', 'tune'): [('horns', 0, 10, 0.9), ('trumpets', 0, 0, 0.55), ('violins', 12, -4, 0.45)],
        ('order', 'bass'): [('tuba', -12, 4, 0.75), ('timpani', 0, 0, 0.35)],
        ('order', 'chord'): [('trombones', 0, -8, 0.45)],
        ('away', 'tune'): [('buzz trombone', 0, 6, 0.8), ('trombones', 0, -6, 0.4)],
        ('away', 'bass'): [('basses pizz', 0, 0, 0.7), ('cellos pizz', 12, -10, 0.35)],
        ('away', 'chord'): [('muted horn', 0, -12, 0.35)],
        ('away', 'snare'): [('ride', 0, -14, 0.35)], ('away', 'tick'): [('ride', 0, -18, 0.3)],
    }
    B.perform(C.events, parts)
    B.effects([(0, -2), (M['bunny'], 0), (M['xmas'], -6), (M['knock'], 0), (M['greet'], -6), (M['away'], -3)])
    # the town comes up
    for m in (40, 52, 55, 59):
        B.play('choir', m + 12, 0.0, 2.2, 60, gain=0.25)
    # three pops on the porch, scampering feet out along Right
    for i in range(3):
        B.hit('slapstick', M['out'] + 0.05 + 0.18 * i, 110, gain=0.7, pan=-0.1 + 0.1 * i)
    # the egg door: magic and a whoosh at the end of Right
    B.hit('bell tree', M['door1'], 100, gain=0.5, pan=pR)
    B.whoosh(M['door1'] + 0.1, 0.9, True, pan=pR, gain=0.8)
    # the sack bursts: a slide whistle up, a cymbal; a boing on every hop
    M_.add('fx', slide(0, 0.5, 400, 1400, 0.6, amp=0.35), M['bunny'] - 0.45, 1.0, 0.0)
    B.hit('crash', M['bunny'], 100, gain=0.35)
    hops = [b[0] for b in C.beats if b[2] == 'bunny']
    for i, th in enumerate(hops):
        M_.add('fx', slide(0, 0.12, 500, 900 + 60 * (i % 4), 0.16, amp=0.12), th, 1.0, S.pan(S.mid))
    # Jack's roar: wrong one!
    ta = M['angry']
    for m, sec, g in ((45, 'trombones', 0.8), (48, 'trombones', 0.7), (52, 'horns', 0.7), (33, 'tuba', 0.8),
                      (57, 'trumpets', 0.5)):
        B.play(sec, m, ta, 1.6, 118, gain=g)
    B.boom(ta, pan=S.pan(S.mid - 70))
    B.hit('timpani roll', ta + 0.1, 110, gain=0.5)
    B.hit('crash', ta, 120, gain=0.5)
    B.fire(ta, ta + 2.2, level=0.6, pan=S.pan(S.mid - 70))
    # off they hop: boings receding to the right end
    for i in range(7):
        th = M['back'] + 0.34 * i
        M_.add('fx', slide(0, 0.1, 600, 1100, 0.14, amp=0.1), th, 0.8 - 0.08 * i, 0.3 + 0.08 * i)
    # Christmas: sleigh bells soft at the door, three knocks, the sack comes down
    B.sleigh_bells(M['xmas'], M['knock'], beat=60 / 110, pan=pR, v=70, gain=0.6)
    for i in range(3):
        B.hit('wood', M['knock'] + 0.15 + 0.38 * i, 124, gain=1.4, pan=S.pan(door), fx=True)
    B.whoosh(M['grab'] - 0.3, 0.5, False, pan=S.pan(door))
    B.boom(M['grab'], pan=S.pan(door), gain=0.8)
    B.hit('ratchet', M['grab'] + 0.3, 100, gain=0.5, pan=S.pan(door))
    # the tub's claw feet clank on every step; Santa grumbles in the sack
    tb = [b[0] for b in C.beats if b[2] == 'tub' and b[1] in (0, 3)]
    for i, th in enumerate(tb):
        pos = float(keys(th, [(M['tub'] + 0.3, door + 50), (M['greet'] - 0.2, S.mid + 160)]))
        B.hit('brake drum', th, 90 + 10 * (i % 2), gain=0.5, pan=S.pan(pos), fx=True)
        if i % 2 == 0:
            B.play('muted horn', 41 + (i // 2) % 3 * 2, th + 0.1, 0.25, 96, S.pan(pos - 75), 0.5)
            B.hit('hoof soft', th + 0.15, 100, gain=0.6, pan=S.pan(pos - 75), fx=True)
    # the greeting: a cymbal swell into it, a crash on the bow
    B.hit('cymbal swell', M['greet'] - 1.4, 100, gain=0.5)
    B.hit('crash', M['greet'], 110, gain=0.45)
    B.hit('bell tree', M['greet'] + 4 * 60 / 104 * 2 + 1.0, 100, gain=0.5, pan=S.pan(S.mid - 70))
    B.hit('crash', M['order'], 116, gain=0.45)
    # dragged away to the lair: hurried feet, a sly ratchet, a green stab at the end
    B.gallop(M['away'], M['end'] - 1.6, beat=60 / 132 * 2,
             pan=lambda tt: float(np.clip(0.1 - 1.2 * (tt - M['away']) / (M['end'] - M['away']), -0.9, 0.9)),
             v=80, gain=0.6)
    for m, sec in ((43, 'buzz trombone'), (31, 'tuba'), (55, 'muted horn')):
        B.play(sec, m, M['end'] - 1.6, 1.0, 110, pan=-0.8, gain=0.7)
    B.hit('gong', M['end'] - 1.6, 90, gain=0.4, pan=-0.8)
    B.finish()
