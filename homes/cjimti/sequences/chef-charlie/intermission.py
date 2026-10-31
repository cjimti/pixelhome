"""Intermission: five minutes of an autumn-rust house filling with Charlie Brown's yellow and black zigzag.

The shared countdown (pixelhome/intermission.py) does the telling: a deep rust bed holds the house and his shirt's
yellow fills it toward the middle of Porch Front over 285 s. Black zigzag bands are cut into the yellow as it comes,
so the filled part of the house reads as his shirt, the bands zigging one way and zagging back slowly, once every two
bars of the music. Autumn leaves keep drifting over whatever is still rust. On every minute a little bell-and-
piano figure counts the minutes left, each note a soft yellow ring out from the porch. When the fill meets in the
middle the trio strikes up the main title as the call-back: the zigzags snap to its beat across the whole house, a
run flashes white on every beat, leaves fly out of the porch on every bar, and on the last chord the house settles
back to rust for the show.

The music is a cool jazz trio to wait by, built from the set's own themes (pixelhome/chef_charlie.py), each section
exactly 30 s so every minute starts a new one: Linus's waltz at 96, Charlie Brown's theme as a
ballad, Grandma's tune in two, the main title as an easy swing at 128 (twice through), the waltz again on muted
trumpet, Snoopy's strut slowed to a stroll, the feast as a ballad, Grandma's again swinging softly, and the waltz
on celesta and harp. The last 15 s are the main title gathering on a brush roll, and on the full house the whole band
plays its head and lands on F6, then quiet for the show."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.intermission import SECONDS, MARKS, FINALE, countdown, order, reach
from pixelhome.chef_charlie import Chart, Band, Stage, pulse, tri, YELLOW, WHITE, GOLD, LEAVES

CODE = 'CC14'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ("The house glows autumn rust and fills toward the porch with Charlie Brown's yellow and black zigzag "
               'while leaves drift and a little bell figure counts the minutes. When it is full, the trio swings the '
               'main title.')
D = SECONDS

BED = hexc('#b02a00')                   # deep autumn rust
FILL = YELLOW                           # his shirt
FULL = MARKS['full']                    # 285: the fill meets in the middle; the call-back lands here
COUNT = [(m, 4 - i) for i, m in enumerate(MARKS['minutes'])]    # (minute, notes): 4 left, 3, 2, 1
CHIME = ('F5', 'A5', 'C6', 'E6')        # the counting figure, F major seventh, as many notes as minutes left
CHIME_STEP = 0.32


def compose():
    C = Chart()
    for theme, style, bpm, tag, bars in (('blanket', 'waltz', 96, 's1', None), ('boy', 'ballad', 64, 's2', None),
                                         ('grandma', 'two', 64, 's3', None), ('title', 'swing', 128, 's4a', None),
                                         ('title', 'swing', 128, 's4b', None), ('blanket', 'waltz', 96, 's5', None),
                                         ('beagle', 'two', 64, 's6', None), ('feast', 'ballad', 64, 's7', None),
                                         ('grandma', 'swing', 64, 's8', None), ('blanket', 'arp', 96, 's9', None)):
        C.play(theme, style=style, bpm=bpm, tag=tag, bars=bars)    # each exactly 30 s (s4 twice through, 15 s each)
    C.mark('gather')
    C.play('title', style='swing', bpm=128, tag='gather')          # 15 s, gathering toward the full house
    C.mark('full')
    C.play('title', style='swing', bars=(0, 4), bpm=152, tag='cheer')
    C.mark('button')
    C.button('F6', bpm=152, beats=3)
    C.rest(SECONDS - C.t)
    C.mark('end')
    return C


C = compose()
M = C.marks
assert abs(M['full'] - FULL) < 1e-6, M['full']


def count_times():
    return [(m + k * CHIME_STEP, k) for m, n in COUNT for k in range(n)]


def render(G, seed=1):
    out = countdown(G, bed=BED, fill=FILL, seed=seed)
    F = len(out)
    S = Stage(G)
    d, mid = S.d, S.mid
    v = order(G)
    t_all = np.arange(F) * DT
    reach_t = reach(t_all)
    settle = smoothstep(FULL + 0.85 * FINALE, FULL + FINALE, t_all)
    rings = np.array([t for t, k in count_times()])
    bar2 = 2 * 3 * 60 / 96                                          # a zig every two bars of the waltz (3.75 s)
    cheer_beats = np.array(C.beat_times('cheer'))
    cheer_downs = C.downbeats('cheer')
    b_title = 60 / 152

    for f in range(F):
        t = f * DT
        fr = out[f].astype(np.float64)
        filled = smoothstep(-0.012, 0.012, v - reach_t[f]) * (1 - settle[f])

        # the black zigzag cut into the yellow: slow while waiting, on the title's beat for the finale
        if t < FULL:
            phase = t / bar2
            travel = 0.0
        else:
            phase = FULL / bar2 + (t - FULL) / b_title
            travel = 0.25
        off = 0.5 * (2 * tri(phase / 2.0) - 1) + travel * (phase - FULL / bar2) * (t >= FULL)
        u = (d / 56.0 - off) % 1.0
        band = smoothstep(0.2, 0.14, np.abs(u - 0.5))
        fr *= (1 - 0.9 * band * filled)[:, None]

        # leaves drifting over whatever is still rust
        if t < FULL + 1:
            fr += 0.85 * S.leaves(t, 0.9, wind=-18, n=60, seed=4) * (1 - filled)[:, None] * (1 - S.run['Side'])[:, None]

        # each counting note: a soft yellow ring out from the porch
        for tb in rings[(rings <= t) & (rings > t - 2.5)]:
            a = t - tb
            fr += light(GOLD, 0.45 * np.exp(-((np.abs(d - mid) - 500 * a) / 70) ** 2) * np.exp(-a / 0.9))

        # the finale: a run flashes white on every beat, leaves fly out of the porch on every bar, a burst on the chord
        if t >= FULL:
            fade = float(smoothstep(FULL + FINALE - 1.0, FULL + FINALE - 3.0, t))
            fr += S.run_flash(t, cheer_beats, cols=(WHITE, GOLD), lv=0.45 * fade, decay=0.15)
            fr += S.confetti([(tb, 0.9, mid) for tb in cheer_downs], t, colors=LEAVES, n=26, seed=6) * fade
            a = t - M['button']
            if a >= 0:
                fr += light(WHITE, 0.6 * np.exp(-a / 0.15) * np.ones(S.N))
                fr += S.burst([(M['button'], 0.9, mid)], t, seed=7, n=18, colors=(YELLOW, WHITE, GOLD))
        out[f] = np.clip(fr, 0, 1)
    return out


def score(M_, G):
    from pixelhome.audio import note
    S = Stage(G)
    B = Band(M_, level=1.07)
    soft_comp = [('piano', 0, -18, 0.4)]
    parts = {
        ('s1', 'tune'): [('piano', 0, -14, 0.8)], ('s1', 'comp'): soft_comp,
        ('s2', 'tune'): [('piano', 0, -12, 0.8), ('celesta', 12, -30, 0.2)], ('s2', 'comp'): soft_comp,
        ('s3', 'tune'): [('clarinets', 0, -18, 0.5)], ('s3', 'comp'): soft_comp,
        ('s4a', 'tune'): [('piano', 0, -10, 0.8)], ('s4a', 'comp'): soft_comp,
        ('s4b', 'tune'): [('flutes', 0, -16, 0.45), ('piano', 0, -24, 0.35)], ('s4b', 'comp'): soft_comp,
        ('s5', 'tune'): [('harmon trumpet', 0, -12, 0.7)], ('s5', 'comp'): soft_comp,
        ('s6', 'tune'): [('piano', 0, -12, 0.8)], ('s6', 'comp'): soft_comp,
        ('s7', 'tune'): [('muted horn', 0, -14, 0.5), ('piano', 0, -26, 0.3)], ('s7', 'comp'): soft_comp,
        ('s8', 'tune'): [('piano', 0, -10, 0.8)], ('s8', 'comp'): soft_comp,
        ('s9', 'tune'): [('celesta', 0, -10, 1.0), ('piano', 0, -24, 0.35)],
        ('s9', 'arp'): [('harp', 0, -22, 0.5)], ('s9', 'pedal'): [('bass', 0, -16, 0.6)],
        ('gather', 'tune'): [('piano', 0, -4, 0.8), ('harmon trumpet', 0, -12, 0.45)],
        ('gather', 'comp'): [('piano', 0, -12, 0.45)],
        ('cheer', 'tune'): [('piano', 0, 8, 0.85), ('harmon trumpet', 0, 0, 0.6), ('choir', 0, -8, 0.4),
                            ('xylo', 12, -12, 0.25)],
        ('cheer', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -12, 0.3)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.45)],
    }
    # a gentle trio: softer drums and bass while waiting, full for the call-back
    for tag in ('s1', 's2', 's3', 's4a', 's4b', 's5', 's6', 's7', 's8', 's9', 'gather'):
        parts[(tag, 'brush')] = [('brush', 0, -10, 0.35)]
        parts[(tag, 'tap')] = [('tap', 0, -12, 0.35)]
        parts[(tag, 'ride')] = [('ride', 0, -14, 0.25)]
        parts[(tag, 'kick')] = []
        parts[(tag, 'bass')] = [('bass', 0, -8, 0.7)]
    B.perform(C.events, parts)
    # the minutes left: a bell-and-piano figure, a note for each minute, from the porch
    porch = S.pan(S.mid)
    for t, k in count_times():
        B.play('glock', note(CHIME[k]) - 12, t, 0.9, 74, pan=porch, gain=0.35)
        B.play('piano', note(CHIME[k]), t, 0.9, 70, pan=porch, gain=0.5)
    # into the full house: a brush roll and a swell, a crash on it, the kids cheer
    B.roll(FULL - 3.0, FULL, pan=porch, gain=0.6)
    B.hit('cymbal swell', FULL - 1.8, 96, gain=0.4)
    B.hit('crash', FULL, 112, gain=0.45)
    B.kids(FULL + 0.1, FULL + 2.2, 'cheer', level=0.45, pan=porch, voices=6, seed=14)
    B.hit('crash', M['button'], 112, gain=0.4)
    B.effects([(0, -4)])
    B.finish()
