"""Meant to Be: on top of the spiral hill under the full moon, the Pumpkin King and Sally find each other.

A deep blue night: a big full moon glowing over Porch Front, the spiral hill curling slowly on the porch sides,
stars twinkling along the wings. Sally waits on the porch beside the moon, her blue on the left wing, to
her own theme on flute and harp. The Pumpkin King walks in from the free end of Right along the wing to his
theme in A minor, his moonlight following him round the porch corner. Then the two themes intertwine: his on horn
and cello, hers on violins and oboe, each note sending a wave of his white or her blue out across the house, the
waves crossing over the porch as the two draw closer. They come together under the moon: the theme turns to A
major on the whole band, the moon blooms, blue and white meet in the middle. Zero flies in from the free
end of Right to the porch and up into the sky, his nose becoming a glowing star over the porch that twinkles on
his little glockenspiel tune with a woof. On the last chord the whole house blazes with every colour of the
story (orange, violet, green, blue, red, gold, white) rippling out from the moon, then settles into moonlight.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() both read its events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc, perc
from pixelhome.audio import note
from pixelhome.nightmare import (Chart, Band, Stage, pulse, THEMES, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, WHITE,
                                 GOLD, ICE, RED, GREEN, MOON, NIGHT, SALLY, NOSE, PINK, BLUE)

CODE = 'NM20'
TITLE = 'Meant to Be'
KIND = 'show'
DESCRIPTION = ('Under a full moon over the porch Sally waits, and Jack walks in along the right wing. Their themes and '
    'colours intertwine until they meet, Zero becomes a star over the porch, and the whole house blazes with '
    'every colour of the story.')
VOICEOVER = 'High on Spiral Hill, under a full moon, Sally was waiting for Jack.'

HILL = hexc('#2c50b0')
STAR = hexc('#b8ccff')
STORY = [ORANGE, VIOLET, SLIME, SALLY, RED, GOLD, MOON, PINK]


def compose():
    C = Chart()
    C.rest(3.0)                                                                       # the moonlit hill
    C.mark('waits')
    C.play('sally', style='arp', bars=(0, 4), bpm=80, tag='waits')                    # Sally waits
    C.mark('comes')
    C.play('king', style='waltz', bars=(12, 16), bpm=88, tag='comes')                 # he comes to her
    C.mark('duet')
    C.play('king', style='waltz', bars=(0, 8), bpm=84, tag='duet')                    # the themes intertwine
    C.t = C.marks['duet']
    C.play('sally', style='none', bars=(0, 8), bpm=84, transpose=-5, tag='duet_s', vel=90)
    C.mark('together')
    C.play('king', style='waltz', bars=(8, 16), bpm=92, major=True, tag='together')   # together
    C.mark('chord')
    C.rest(4.5)                                                                       # every colour
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def dog_times():
    t0 = M['together'] + 5.0
    return t0, t0 + 3.0, t0 + 4.2           # flies in, reaches the porch, up into the sky


def render(G, seed=20):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    t_wa, t_co, t_du, t_to, t_ch = M['waits'], M['comes'], M['duet'], M['together'], M['chord']
    t_d0, t_d1, t_d2 = dog_times()
    hills = [S.at('Porch Left', 0.45), S.at('Porch Right', 0.5)]
    stars = rng.choice(np.flatnonzero(S.wings | S.run['Side']), 40, replace=False)
    st_rate, st_ph = rng.uniform(0.3, 0.8, 40), rng.uniform(0, 2 * np.pi, 40)
    king_n = np.array([n[0] for n in C.tunes('duet')])
    sally_n = np.array([n[0] for n in C.tunes('duet_s')])
    waits_n = np.array([n[0] for n in C.tunes('waits')])
    downs = np.array(C.downbeats('together'))
    zero_n = np.array([t_d2 + n[0] * 60 / 92 for n in THEMES['zero']['melody']])

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 2.5, t)
        tog = smoothstep(t_to, t_to + 2.5, t)
        blaze = smoothstep(t_ch - 0.05, t_ch + 0.2, t) * (1 - 0.7 * smoothstep(t_ch + 1.0, D - 0.5, t))
        # the night: deep blue, a full moon over the porch, the spiral hill curling on the porch sides, stars
        fr = light(NIGHT, 0.3 * up * np.ones(G.N))
        moon = (0.7 + 0.25 * tog) * up
        fr += light(MOON, moon * S.blob(mid, 75 + 30 * tog))
        fr += light(MOON, 0.22 * moon * S.blob(mid, 260 + 120 * tog))
        for h in hills:
            curl = 0.5 + 0.5 * np.cos((d - h) / 13 - 1.2 * t * np.sign(d - h))
            fr += light(HILL, 0.55 * up * S.blob(h, 160) * curl ** 2)
        tw = 0.5 + 0.5 * np.sin(2 * np.pi * st_rate * t + st_ph)
        fr[stars] += light(STAR, 0.55 * up * tw ** 3)
        # Sally waiting, her blue on the left; she sways on each note of her theme
        p_s = keys(t, [(t_du, mid - 55), (t_to, mid - 32), (t_to + 2, mid - 14)])
        sway = 0.85 + 0.15 * pulse(t, waits_n, 0.4)
        blue = up * (0.35 + 0.15 * pulse(t, waits_n, 0.5))
        fr += light(SALLY, blue * (S.run['Left'] | S.run['Porch Left']) * (1 - 0.4 * tog))
        fr += light(SALLY, 0.4 * up * S.blob(p_s, 60))
        # Jack walking in from the free end of Right, his moonlight round him
        if t >= t_co - 0.5:
            p_j = keys(t, [(t_co - 0.5, S.L + 15), (t_du, mid + 55), (t_to, mid + 32), (t_to + 2, mid + 14)])
            lit = smoothstep(t_co - 0.5, t_co + 1.0, t)
            fr += light(MOON, 0.4 * lit * S.span(p_j, S.L + 50) * np.exp(-np.abs(d - p_j) / 400))
            fr += light(WHITE, 0.25 * lit * (S.run['Right'] | S.run['Porch Right']) * smoothstep(t_co, t_du, t) *
                        (1 - 0.4 * tog))
        # the duet: his notes send white waves leftward across the house, hers blue waves rightward; they cross
        for tn in king_n[(king_n <= t) & (king_n > t - 3)]:
            a = t - tn
            fr += light(WHITE, 0.95 * np.exp(-a / 1.1) * np.exp(-((d - (mid + 30 - 520 * a)) / 80) ** 2))
        for tn in sally_n[(sally_n <= t) & (sally_n > t - 3)]:
            a = t - tn
            fr += light(SALLY, 1.0 * np.exp(-a / 1.1) * np.exp(-((d - (mid - 30 + 520 * a)) / 80) ** 2))
        # together: blue and white meet in the middle, a warm bloom under the moon, pulsing on the downbeats
        if t >= t_to:
            beat = pulse(t, downs, 0.5)
            fr += light(PINK, (0.5 + 0.3 * beat) * tog * S.blob(mid, 170))
            fr += light(SALLY, 0.5 * tog * (S.run['Left'] | S.run['Side']))
            fr += light(MOON, 0.45 * tog * S.run['Right'])
            fr += light(VIOLET, (0.4 + 0.25 * beat) * tog * (S.run['Porch Left'] | S.run['Porch Right']))
        fr = S.sally(fr, p_s, up * sway, facing=1)
        if t >= t_co - 0.5:
            fr = S.jack(fr, p_j, lit, facing=-1, glow=0.35)
        # Zero flies in from the free end of Right and up into the sky; his nose becomes a star
        if t_d0 <= t < t_d2 + 0.4:
            pz = keys(t, [(t_d0, S.L + 20), (t_d1, mid + 10)])
            lz = 1.0 - smoothstep(t_d1 + 0.3, t_d2 + 0.4, t)
            fr = S.zero(fr, pz, lz, facing=-1, t=t)
        if t >= t_d1 + 0.3:
            s = smoothstep(t_d1 + 0.3, t_d2 + 0.3, t)
            tw = 0.8 + 0.2 * np.sin(9 * t) + 0.6 * pulse(t, zero_n, 0.2)
            fr += light(NOSE, 1.0 * s * tw * S.blob(mid, 10 + 8 * s))
            fr += light(GOLD, 0.35 * s * tw * S.blob(mid, 40))
            ray = np.exp(-((np.abs(d - mid) - (180 * ((t * 0.8) % 1.0) + 20)) / 25) ** 2)
            fr += light(NOSE, 0.45 * s * ray * (1 - (t * 0.8) % 1.0))
        # building to it: the story's colours creep in from the ends of the house
        pre = smoothstep(t_ch - 6.0, t_ch, t) * (t < t_ch)
        if pre > 0:
            idx = ((np.abs(d - mid) / 140 + 1.2 * t) % len(STORY)).astype(int)
            reach = smoothstep(S.L * 0.62 * (1 - pre) - 60, S.L * 0.62 * (1 - pre) + 60, np.abs(d - mid))
            fr += perc(0.55 * pre * reach)[:, None] * np.array(STORY)[idx]
        # the last chord: every colour of the story rippling out from the moon
        if blaze > 0:
            a = t - t_ch
            idx = ((np.abs(d - mid) / 140 - 1.6 * a) % len(STORY)).astype(int)
            cols = np.array(STORY)[idx]
            fr += perc(0.95 * blaze * np.ones(G.N))[:, None] * cols
            fr += light(WHITE, 0.8 * np.exp(-max(a, 0) / 0.15) * np.ones(G.N))
            fr += S.burst([(t_ch, 1.0, mid), (t_ch + 0.2, 0.8, S.at('Left', 0.5)),
                           (t_ch + 0.35, 0.8, S.at('Right', 0.5))], t, seed=20, n=20, colors=(WHITE, GOLD, PINK))
            fr = S.sally(fr, mid - 14, 1.0, facing=1)
            fr = S.jack(fr, mid + 14, 1.0, facing=-1, glow=0.3)
            fr += light(NOSE, 0.9 * S.blob(mid, 12))
        out[f] = fr * float(smoothstep(D, D - 2.0, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.4)
    parts = {
        ('waits', 'tune'): [('flutes', 0, 0, 0.6), ('violins', 0, -12, 0.35)],
        ('waits', 'arp'): [('harp', 0, -4, 0.5), ('celesta', 12, -10, 0.35)],
        ('waits', 'pedal'): [('cellos', 0, -14, 0.45)],
        ('comes', 'tune'): [('horns', 0, -2, 0.7), ('cellos', 0, -10, 0.35)],
        ('comes', 'bass'): [('basses', -12, -12, 0.45)],
        ('comes', 'chord'): [('violas', 0, -16, 0.35)],
        ('duet', 'tune'): [('horns', 0, -4, 0.55), ('cellos', 0, -4, 0.55)],
        ('duet_s', 'tune'): [('violins', 12, 4, 0.9), ('oboes', 12, 0, 0.6)],
        ('duet', 'bass'): [('basses', -12, -10, 0.45)],
        ('duet', 'chord'): [('harp', 0, -10, 0.4), ('violas', 0, -16, 0.3)],
        ('together', 'tune'): [('horns', 0, 8, 0.85), ('trumpets', 0, -2, 0.5), ('violins', 12, 0, 0.6),
                               ('choir', 0, 0, 0.7)],
        ('together', 'bass'): [('tuba', -12, 2, 0.7), ('basses', 0, -4, 0.55)],
        ('together', 'chord'): [('trombones', 0, -8, 0.4), ('violas', 0, -6, 0.45), ('harp', 0, -6, 0.4)],
    }
    B.perform(C.events, parts)
    t_to, t_ch, t_end = M['together'], M['chord'], M['end']
    t_d0, t_d1, t_d2 = dog_times()
    # the opening: a soft chord on the choir and a harp glissando up to the moon
    for m in (50, 57, 62, 65):
        B.play('choir', m, 0.2, 3.0, 60, gain=0.3)
    for i, m in enumerate((50, 53, 57, 60, 62, 65, 69, 72, 74, 77)):
        B.play('harp', m, 0.6 + 0.09 * i, 0.5, 70 + 3 * i, gain=0.5)
    B.hit('cymbal swell', t_to - 1.8, 100, gain=0.5)
    B.hit('crash', t_to, 112, gain=0.5)
    for t, k, g in C.beats:
        if g == 'together' and k == 0:
            B.hit('timpani', t, 100, pitch=-5, gain=0.35)
    # Zero's star: his little tune on glockenspiel, in A, and a woof as he goes up
    for b, l, n in THEMES['zero']['melody']:
        B.play('glock', note(n) + 5 - 12, t_d2 + b * 60 / 92, l * 60 / 92, 100, gain=0.45, pan=0.0)
    # the last chord: A major on everything
    for m, sec in ((33, 'tuba'), (45, 'basses'), (45, 'cellos'), (57, 'horns'), (61, 'horns'), (64, 'trombones'),
                   (69, 'trumpets'), (73, 'trumpets'), (69, 'violins'), (76, 'violins'), (57, 'violas')):
        B.play(sec, m, t_ch, 3.8, 112, gain=0.55)
    for m in (57, 61, 64, 69):
        B.play('choir', m, t_ch, 3.8, 100, gain=0.45)
    B.play('celesta', 81, t_ch, 2.0, 100, gain=0.4)
    B.hit('crash', t_ch, 124, gain=0.7)
    B.hit('gong', t_ch, 110, gain=0.4)
    B.hit('timpani roll', t_ch - 1.2, 110, pitch=-5, gain=0.5)
    B.hit('bass drum', t_ch, 120, gain=0.6)
    B.hit('triangle', t_ch + 0.1, 110, gain=0.5)
    # the stage: a breath of wind on the hill, the dog flying in, his bark, a shimmer as he becomes a star
    B.effects([(0, -8), (t_d0 - 0.5, -6), (t_d1, -3), (t_d2 + 2, -8)])
    B.wind(0.0, M['comes'], level=0.35, pan=-0.3)
    B.whoosh(t_d0, seconds=3.0, up=False, pan=0.8, gain=0.5)
    B.woof(t_d1 + 0.1, pan=S.pan(S.mid), big=0.9)
    B.whoosh(t_d1 + 0.4, seconds=1.6, up=True, pan=0.0, gain=0.5)
    B.hit('bell tree', t_d1 + 0.5, 100, gain=0.5, fx=True)
    B.finish()
