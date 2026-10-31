"""Popcorn: Snoopy pops the corn, and it doesn't stop popping until it has buried the house.

The kitchen comes up and the brushes count in. Snoopy pops up at the stove on the porch with the bag and pours:
a stream of gold kernels runs in from both ends of the house to the pan, rattling. The heat comes on to a vamp that
climbs a step every two bars: the pan glows, red shimmer spreads out from it along the roof, and a wave of heat runs
out on every beat of the bass. Stop-time: each hit turns the heat up a notch across the whole house; after the second
and third hits a single kernel pops, and nothing follows (false starts), then a held breath, the pan throbbing red.
Pop. Then Snoopy's strut swings while the corn goes off, a few pops at first, then dozens, every one a white-gold
flash that jumps, spreading wider from the pan as the pan fills. The title, double time: the pops become a storm, the
popcorn overflows the pan and spills out along the roof in both directions, a creamy heap with a bright foaming edge,
and the lid bangs up on every beat until it blows off. The house is buried; Woodstock pops up out of the
heap on Right to his twitter, and kernels go off around him on every note while he nibbles his way along. One last
quiet second, one kernel left in the pan... and it goes off like a cannon: a white flash and a wave across the whole
house, and the feast's tune plays out over a popcorn storm with butter drizzling in zigzags down every run, a sweep
from the free end of Right, and the last chord.

compose() lays out the music (pixelhome/chef_charlie.py); popcorn_times() makes the kernels, and render() and score()
share the same lists (pops_*), and where each pop lands (pop_at), so every pop you see is one you hear."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, popcorn_times, drift, WHITE, YELLOW, AMBER, ORANGE,
                                    RED, GOLD, BUTTER, POPCORN, BIRD)

CODE = 'CC06'
TITLE = 'Popcorn'
KIND = 'show'
DESCRIPTION = ('Snoopy pours the kernels and turns up the heat. A pop, then nothing, then a storm of popping that '
    'overflows the pan and buries the whole house, until one last kernel goes off like a cannon.')
VOICEOVER = 'Next on the menu, popcorn, and Snoopy is not taking any chances.'

KERNEL = hexc('#ffa000')
SILVER = hexc('#c8d8ff')

# the heat: a vamp that climbs a step every two bars, ticking like a pan warming; original to this scene
SIMMER = dict(id='simmer', meter=4, bpm=112, swing=True, name='The pan heats: a climbing vamp, D minor to G',
              melody=[(0, .5, 'D4'), (1.5, .5, 'F4'), (2, .5, 'A4'), (3.5, .5, 'C5'),
                      (4, .5, 'B4'), (5.5, .5, 'G4'), (6, 1, 'F4'),
                      (8, .5, 'E4'), (9.5, .5, 'G4'), (10, .5, 'B4'), (11.5, .5, 'D5'),
                      (12, .5, 'C#5'), (13.5, .5, 'A4'), (14, 1, 'G4'),
                      (16, .5, 'F4'), (17.5, .5, 'Ab4'), (18, .5, 'C5'), (19.5, .5, 'Eb5'),
                      (20, .5, 'D5'), (21.5, .5, 'Bb4'), (22, 1, 'Ab4'),
                      (24, .5, 'A4'), (24.5, .5, 'C5'), (25, .5, 'D5'), (25.5, .5, 'F5'), (26, 1, 'E5'), (27, 1, 'D5'),
                      (28, 2, 'B4'), (30, .5, 'G4'), (31, 1, 'F4')],
              chords=[(0, 4, 'Dm7'), (4, 4, 'G7'), (8, 4, 'Em7'), (12, 4, 'A7'), (16, 4, 'Fm7'), (20, 4, 'Bb7'),
                      (24, 4, 'Dm7'), (28, 4, 'G7')])


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the kitchen comes up
    C.mark('count')
    C.play(SIMMER, style='brushes', bars=(0, 1), tune=False, tag='count')
    C.mark('pour')
    C.play('beagle', style='two', bars=(0, 4), bpm=104, tag='pour')  # kernels stream into the pan
    C.mark('heat')
    C.play(SIMMER, style='walk', bars=(0, 4), tag='heat')           # the pan heats
    C.mark('tense')
    C.play(SIMMER, style='stop', bars=(4, 8), tag='tense')          # a notch hotter each hit; two lone pops
    C.mark('breath')
    C.rest(1.2)
    C.mark('popping')
    C.play('beagle', style='swing', bpm=112, tag='popping')         # a few pops, then dozens
    C.mark('fill')
    C.play('title', style='drive', bpm=160, tag='fill')             # it overflows; the lid bangs and blows off
    C.mark('bird')
    C.play('bird', style='two', bars=(0, 4), tag='bird')            # the bird pops out of the heap
    C.mark('bird2')
    C.play('bird', style='swing', bars=(0, 4), tag='bird2')
    C.mark('quiet')
    C.rest(1.0)                                                     # one kernel left
    C.mark('finale')
    C.play('feast', style='swing', bpm=168, tag='finale')           # the cannon, and a popcorn storm
    C.mark('button')
    C.button('D6', bpm=168, beats=2)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def reach(t):
    """How far from the pan the corn is popping (path units each way): the pan, then wider, then the whole house."""
    return float(keys(t, [(M['popping'], 60), (M['fill'], 420), (M['fill'] + 6, 1100), (M['bird'], 1500)]))


def heap(t):
    """How far the overflowing heap has spread each way from the pan."""
    return float(keys(t, [(M['fill'], 70), (M['fill'] + 3, 200), (M['bird'] - 1.5, 1600)]))


pops_early = [C.times('hit', 'tense')[1] + 0.9, C.times('hit', 'tense')[2] + 0.75, M['popping'] - 0.05]
pops_main = popcorn_times(M['popping'], M['fill'], lambda u: 2 + 12 * u ** 1.5, seed=6)
pops_fill = popcorn_times(M['fill'], M['bird'] - 0.6, lambda u: 14 + 22 * u, seed=7)
pops_bird = sorted({round(n[0] + 0.05, 4) for n in C.tunes('bird') + C.tunes('bird2')})
pops_fin = popcorn_times(M['finale'] + 0.3, M['button'] + 0.4, lambda u: 22 - 6 * u, seed=8)


def pop_at(S, i, t, seed, lo, hi):
    """Where pop i of a list lands (the same as Stage.popcorn draws it), for panning its sound."""
    rng = np.random.default_rng(seed * 7919 + i)
    return float(np.clip(rng.uniform(lo, hi), 0, S.L))


def bird_p(S, t):
    """The bird pops up out of the heap on Right and hops along to the porch and back again, a hop a beat."""
    a = S.at('Right', 0.55)
    b = S.mid + 40
    u = float(smoothstep(M['bird'], M['bird2'], t)) - float(smoothstep(M['bird2'], M['quiet'], t))
    hop = abs(np.sin(np.pi * (t - M['bird']) * 168 / 60))
    return a + (b - a) * u + 10 * hop


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The piano plays the roofline: each note of the tune sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def kitchen(S, t, lv, beat=0.0, shift=0.0):
    """The kitchen: gold walls, the checked floor along the wings and Side (brightening on the beat), the stove."""
    floor = S.wings | S.run['Side']
    tile = (np.floor(np.abs(S.d - S.mid) / 18.0 + shift) % 2).astype(float)
    fr = light(GOLD, 0.3 * lv * (1 - 0.6 * floor))
    fr += floor[:, None] * (light(RED, (0.3 + 0.2 * beat) * lv * tile) + light(WHITE, 0.1 * lv * (1 - tile)))
    fr += light(ORANGE, 0.55 * lv * S.blob(S.mid, 110))
    return fr


def render(G, seed=6):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    t_count = C.beat_times('count')
    pour_tune = C.tunes('pour')
    heat_bass = C.times('bass', 'heat')
    hits = C.times('hit', 'tense')
    pop_downs = C.downbeats('popping')
    pop_beats = C.beat_times('popping')
    fill_beats = C.beat_times('fill')
    fill_downs = C.downbeats('fill')
    fin_beats = C.beat_times('finale')
    fin_downs = C.downbeats('finale')
    tunes = {g: C.tunes(g) for g in ('pour', 'heat', 'tense', 'popping', 'fill', 'bird', 'bird2', 'finale')}
    dist = np.abs(d - mid)
    pan_ = S.span(mid - 34, mid + 34)
    lv_kit = [(0, 0.0), (2.0, 1.0), (M['tense'], 1.0), (M['breath'], 0.6), (M['breath'] + 0.3, 0.3),
              (M['popping'], 0.3), (M['popping'] + 0.2, 0.9), (M['bird'], 0.9), (M['bird'] + 1, 0.5),
              (M['quiet'], 0.5), (M['quiet'] + 0.3, 0.3), (M['finale'], 0.3), (M['finale'] + 0.6, 0.8), (D, 0.8)]
    heat_lv = [(0, 0.1), (M['heat'], 0.15), (M['tense'], 0.55), (M['breath'], 1.0), (M['popping'] + 2, 1.0),
               (M['bird'], 0.5), (M['quiet'], 0.3), (M['quiet'] + 0.8, 0.9), (M['finale'] + 0.5, 0.4), (D, 0.4)]

    for f in range(F):
        t = f * DT
        b = pulse(t, beats, 0.15)
        shift = 0.0
        if M['heat'] <= t < M['bird']:                              # the floor marches outward a tile a beat
            nb = np.searchsorted(beats, t)
            shift = -(nb + float(smoothstep(0, 0.25, t - beats[max(nb - 1, 0)])))
        fr = kitchen(S, t, float(keys(t, lv_kit)), b, shift)
        heat = float(keys(t, heat_lv))

        for tc in t_count:
            fr += S.wave(t, tc, AMBER, 0.55, speed=700, width=90, decay=0.35)

        # the pour: a stream of gold kernels running in from both ends of the house to the pan, thicker on each note
        if M['pour'] <= t < M['heat'] + 1.0:
            a = t - M['pour']
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S.run['Porch Front'])
            flow = float(smoothstep(M['pour'] + 0.5, M['pour'] + 1.5, t) * smoothstep(M['heat'] + 1.0, M['heat'] - 0.5, t))
            tail = dist > 300 * float(smoothstep(M['heat'] - 1.5, M['heat'] + 1.0, t))
            kern = smoothstep(0.35, 0.65, drift(17, dist + 330 * t, 9.0, octaves=1)) * (dist > 34) * tail
            notes = pulse(t, [n[0] for n in pour_tune], 0.2)
            fr = fr * (1 - 0.5 * flow * kern[:, None]) + light(KERNEL, flow * (0.7 + 0.3 * notes) * kern)
            fr += keyboard(S, t, tunes['pour'], WHITE, 0.5)
            fr += light(GOLD, 0.6 * float(smoothstep(M['pour'], M['heat'], t)) * pan_)     # the pan filling

        # the heat: red shimmer spreading out from the pan, a wave of heat on every beat of the bass
        if M['heat'] <= t < M['popping'] + 3:
            spread = float(keys(t, [(M['heat'], 120), (M['tense'], 450), (M['breath'], 1300)]))
            fade = float(smoothstep(M['popping'] + 3, M['popping'], t))
            sh = 0.5 + 0.5 * drift(23, d - 90 * t, 25.0)
            fr += light(RED, 0.9 * heat * fade * sh * smoothstep(spread, spread * 0.4, dist))
            fr += light(ORANGE, 0.5 * heat * fade * np.clip(sh - 0.6, 0, 1) * 2.5 * smoothstep(spread, spread * 0.4, dist))
            if t < M['tense'] + 0.5:
                for tb in heat_bass:
                    if tb <= t < tb + 2:
                        fr += S.wave(t, tb, ORANGE, 0.5 + 0.5 * (tb - M['heat']) / (M['tense'] - M['heat']),
                                     speed=800, width=50, decay=0.6)
                fr += keyboard(S, t, tunes['heat'], ORANGE, 0.55, width=30)

        # stop-time: each hit a notch hotter across the house; lone kernels pop and nothing follows
        if M['tense'] <= t < M['popping']:
            for i, th in enumerate(hits):
                a = t - th
                if 0 <= a < 1.2:
                    fr += light(RED, 0.6 * np.exp(-a / 0.3) * np.ones(S.N))
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.1) * pan_)
            fr += keyboard(S, t, tunes['tense'], ORANGE, 0.6, width=30)
            if t >= M['breath']:
                a = t - M['breath']
                fr += light(RED, 0.6 * (0.5 + 0.5 * np.cos(2 * np.pi * 3 * a)) * S.porch)
        for i, tp in enumerate(pops_early):
            a = t - tp
            if 0 <= a < 1.0:
                q = mid + (-60, 50, 0)[i]
                fr += light(POPCORN, (np.exp(-a / 0.25) + 0.6 * np.exp(-a / 0.05)) * S.blob(q + 30 * (1 - np.exp(-a / 0.08)), 10))
                fr += S.wave(t, tp, WHITE, 0.6, origin=q, speed=1200, width=40, decay=0.4)

        # popping: pops spreading from the pan, the heap growing in it, wings flashing on the bar
        if M['popping'] <= t < M['bird']:
            R = reach(t)
            fr += S.popcorn(pops_main, t, lo=mid - R, hi=mid + R, lv=1.0, seed=6)
            fr += S.popcorn(pops_fill, t, lo=mid - R, hi=mid + R, lv=1.0, seed=7)
            if t < M['fill']:
                fr += light(POPCORN, 0.5 * float(smoothstep(M['popping'], M['fill'], t)) * pan_ *
                            (0.75 + 0.25 * np.sin(11 * t + d)))
                fr += S.run_flash(t, pop_downs, cols=(BUTTER, ORANGE), runs=('Left', 'Right', 'Porch Left', 'Porch Right'),
                                  lv=0.6, decay=0.35)
                fr += keyboard(S, t, tunes['popping'], BUTTER, 0.5)
                for tb in pop_beats:
                    if tb <= t < tb + 1.5:
                        fr += S.wave(t, tb, GOLD, 0.6, speed=900, width=45, decay=0.45)

        # the overflow: a creamy heap spilling out both ways with a bright foaming edge; the lid bangs every beat
        if M['fill'] <= t < M['bird'] + 0.5:
            H = heap(t)
            tw = 0.75 + 0.25 * np.sin(13 * t + 1.7 * d) * np.sin(5 * t + 0.31 * d)
            pile = smoothstep(H, H - 25, dist)
            edge = np.exp(-((dist - H) / 18) ** 2) * (H < 1500)
            fr = fr * (1 - 0.55 * pile[:, None]) + light(POPCORN, 0.55 * pile * tw) + light(WHITE, 0.8 * edge)
            if t < M['bird']:
                for tb in fill_beats:
                    a = t - tb
                    if 0 <= a < 0.4:
                        fr += light(SILVER, 0.9 * np.exp(-a / 0.1) * S.blob(mid, 40 + 200 * a))
                fr += S.burst([(tb, 0.8, mid) for tb in fill_downs], t, seed=61, n=10, reach=0.5,
                              colors=(POPCORN, BUTTER, WHITE), life=1.2)
                fr += S.run_flash(t, fill_downs, cols=(WHITE, BUTTER), runs=('Left', 'Right', 'Side'), lv=0.5, decay=0.4)
                fr += keyboard(S, t, tunes['fill'], WHITE, 0.5)
            a = t - (M['bird'] - 0.6)                               # the lid blows off
            if 0 <= a < 2.5:
                fr += S.wave(t, M['bird'] - 0.6, WHITE, 1.0, speed=1500, width=70, decay=0.8)
                fr += S.confetti([(M['bird'] - 0.6, 1.0, mid)], t, colors=(POPCORN, BUTTER, WHITE), n=30, reach=1.4,
                                 seed=62)

        # buried: the whole house a twinkling heap; the bird pops up out of it and kernels go off around him
        if M['bird'] <= t < M['finale']:
            tw = 0.7 + 0.3 * np.sin(9 * t + 1.7 * d) * np.sin(3 * t + 0.23 * d)
            dim = float(keys(t, [(M['bird'], 0.55), (M['quiet'], 0.45), (M['quiet'] + 0.4, 0.15), (M['finale'], 0.15)]))
            fr = fr * 0.5 + light(POPCORN, dim * tw)
            if t < M['quiet']:
                bp = bird_p(S, t)
                fr += S.popcorn(pops_bird, t, lo=bp - 70, hi=bp + 70, lv=0.9, seed=9)
                fr += keyboard(S, t, tunes['bird'] + tunes['bird2'], BUTTER, 0.45, width=22)
                fr += light(YELLOW, 0.35 * S.span(bp, S.at('Right', 0.55)) * (bp < S.at('Right', 0.5)) *
                            np.exp(-np.abs(d - bp) / 120))
                a = t - M['bird']
                if a < 0.8:
                    fr += S.burst([(M['bird'], 0.9, S.at('Right', 0.55))], t, seed=63, n=14, reach=0.4,
                                  colors=(POPCORN, BIRD), life=1.0)
                for tb in C.downbeats('bird') + C.downbeats('bird2'):
                    if tb <= t < tb + 2:
                        fr += S.wave(t, tb, BIRD, 0.9, origin=bird_p(S, tb), speed=900, width=50, decay=0.7)
                fr = S.bird(fr, bp, 1.0, t=t, facing=-1 if t < M['bird2'] else 1)
            else:
                a = t - M['quiet']
                fr += light(RED, 0.7 * float(smoothstep(0.2, 0.9, a)) * (0.6 + 0.4 * np.cos(2 * np.pi * 4 * a)) *
                            S.blob(mid, 12))

        # the cannon, and the popcorn storm with butter drizzling in zigzags
        if t >= M['finale']:
            a = t - M['finale']
            if a < 4:
                fr += light(WHITE, np.exp(-a / 0.15) * np.ones(S.N))
                fr += S.wave(t, M['finale'], POPCORN, 1.0, speed=1400, width=100, decay=1.0)
                fr += S.confetti([(M['finale'], 1.0, mid)], t, colors=(POPCORN, BUTTER, WHITE, GOLD), n=48,
                                 reach=1.8, seed=64)
            ph = (t - M['finale']) / (60 / 168)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.1, t))
            bar = int(ph // 4)
            fr = fr * (1 - 0.3 * fade) + S.zigzag(ph, lv=0.5 * fade, col=BUTTER if bar % 2 == 0 else GOLD, period=80,
                                                  travel=0.3)
            fr += S.popcorn(pops_fin, t, lv=1.0, seed=8)
            fr += S.run_flash(t, fin_beats, cols=(WHITE, BUTTER, POPCORN), lv=0.45 * fade, decay=0.18)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.6)
            fr += S.sweep(t, fin_downs[6], 2.0, WHITE, 0.8, frm='right', width=90, trail=0.5)
            bb = t - M['button']
            if bb >= 0:
                fr += light(BUTTER, np.exp(-bb / 0.5) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-bb / 0.12) * np.ones(S.N))

        # the pan on the porch, the heat under it, and Snoopy beside it
        if t >= M['pour'] - 0.1:
            body = S.span(mid - 34, mid + 34) * (1 - 0.8 * float(smoothstep(M['fill'] + 2, M['fill'] + 4, t)) *
                                                 float(smoothstep(M['quiet'] + 0.2, M['quiet'] - 0.5, t)))
            fr = fr * (1 - 0.35 * body[:, None]) + light(SILVER, 0.3 * body)
            fr += light(RED, 0.7 * heat * np.exp(-((dist - 36) / 6) ** 2))
            jump = 0.0
            for tp in pops_early:
                if 0 <= t - tp < 0.4:
                    jump = 1.0
            lid = 0.0
            if M['fill'] <= t < M['bird'] - 0.6:
                lid = pulse(t, fill_beats, 0.12)
            p = mid + 52 + 14 * jump + 10 * lid
            lvl = 1.0 if not (M['bird'] - 0.6 <= t < M['finale']) else 0.35
            facing = -1 if t < M['finale'] else (1 if int((t - M['finale']) / 1.43) % 2 else -1)
            fr = S.beagle(fr, p, lvl * min(1.2, 0.85 + 0.25 * b + 0.3 * jump), facing=facing, t=t, chef=True)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)



def score(M_, G):
    S = Stage(G)
    mid = S.mid
    B = Band(M_, level=1.0)
    parts = {
        ('pour', 'tune'): [('piano', 0, 4, 0.8), ('marimba', 0, -10, 0.3)],
        ('heat', 'tune'): [('harmon trumpet', 0, 4, 0.9), ('piano', 0, -10, 0.35)],
        ('tense', 'tune'): [('harmon trumpet', 0, 8, 0.95)],
        ('tense', 'hit'): [('piano', 0, 6, 0.8), ('muted horn', 0, -4, 0.45)],
        ('popping', 'tune'): [('piano', 0, 8, 0.85), ('xylo', 12, -12, 0.25)],
        ('fill', 'tune'): [('piano', 0, 12, 0.85), ('xylo', 12, -8, 0.3), ('trumpets', 0, -12, 0.3)],
        ('fill', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -14, 0.3)],
        ('bird', 'tune'): [('xylo', 0, 0, 0.6), ('piano', 0, -6, 0.5)],
        ('bird2', 'tune'): [('xylo', 0, 4, 0.65), ('pizz', 0, -4, 0.5), ('piano', 0, -6, 0.5)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('xylo', 12, -12, 0.2)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4)],
    }
    B.perform(C.events, parts)
    for m in (62, 65, 69, 72):
        B.play('choir', m, 0.2, 1.9, 48, gain=0.3)
    # the pour: Snoopy pops up, and the kernels rattle into the pan
    B.boing(M['pour'], pan=S.pan(mid), gain=0.8)
    B.woof(M['pour'] + 0.3, pan=S.pan(mid))
    rng = np.random.default_rng(66)
    for tt in np.arange(M['pour'] + 0.6, M['heat'] - 0.2, 0.09):
        B.hit('maraca', tt + rng.uniform(0, 0.04), int(rng.uniform(60, 95)), gain=0.35,
              pan=S.pan(mid) + rng.uniform(-0.2, 0.2))
    # the heat: a sizzle that grows; the roll in the held breath
    B.fire(M['heat'], M['bird'], level=lambda tt: np.clip((tt - M['heat']) / (M['breath'] - M['heat']), 0.08, 1) * 0.28,
           pan=S.pan(mid), crackle=10)
    for i, tp in enumerate(pops_early):
        B.pop(tp, pan=S.pan(mid + (-60, 50, 0)[i]), gain=3.0, seed=i)
        if i < 2:
            B.woof(tp + 0.35, pan=S.pan(mid), big=0.6)
    B.roll(M['breath'] - 0.1, M['popping'] - 0.1, pan=S.pan(mid), gain=0.6)
    B.hit('cymbal swell', M['breath'] - 0.5, 85, gain=0.3)
    # the corn: every pop panned where it lights
    for seed, times in ((6, pops_main), (7, pops_fill)):
        for i, tp in enumerate(times):
            R = reach(tp)
            p = pop_at(S, i, tp, seed, mid - R, mid + R)
            B.pop(tp, pan=S.pan(p), gain=1.6 if seed == 6 else 1.1, seed=i)
    # the lid on every beat of the overflow, then it blows off
    for tb in C.beat_times('fill'):
        B.O.hit('brake drum', tb, 90, pitch=4, gain=0.25, pan=S.pan(mid), fx=True)
    tb = M['bird'] - 0.6
    B.whoosh(tb, 0.6, up=True, pan=S.pan(mid), gain=0.9)
    B.boing(tb + 0.05, pan=S.pan(mid), gain=0.9, high=0.8)
    B.hit('crash', tb, 115, gain=0.45)
    B.effects([(0, -3), (M['popping'], -1), (M['bird'], -2), (M['finale'], -1), (M['finale'] + 2, -4)])
    # the bird pops up out of the heap: chirps, kernels going off with his tune, his nibbling
    B.boing(M['bird'], pan=S.pan(S.at('Right', 0.55)), gain=0.6, high=2.0)
    for k, tt in enumerate(C.downbeats('bird') + C.downbeats('bird2')):
        B.chirp(tt + 0.1, n=3 + k % 3, pan=S.pan(bird_p(S, tt)), gain=0.9, seed=k)
    for i, tp in enumerate(pops_bird):
        bp = bird_p(S, tp)
        B.pop(tp, pan=S.pan(pop_at(S, i, tp, 9, bp - 70, bp + 70)), gain=1.0, seed=i)
    for tt in C.downbeats('bird2')[1::2]:
        B.crunch(tt + 0.5, bites=2, pan=S.pan(bird_p(S, tt)), gain=0.5)
    # the last kernel, and the cannon
    for k in range(4):
        B.hit('woodblock', M['quiet'] + 0.2 + 0.18 * k, 70 + 8 * k, pitch=5, gain=0.3, pan=S.pan(mid))
    B.pop(M['finale'], pan=S.pan(mid), gain=4.0, seed=99)
    B.boom(M['finale'], pan=S.pan(mid), gain=0.7)
    B.hit('crash', M['finale'], 122, gain=0.55)
    B.hit('timpani', M['finale'] + 0.02, 120, pitch=-5, gain=0.45)
    B.kids(M['finale'] + 0.4, M['finale'] + 1.8, 'cheer', level=0.35, voices=5, seed=4)
    for i, tp in enumerate(pops_fin):
        B.pop(tp, pan=S.pan(pop_at(S, i, tp, 8, 0.0, S.L)), gain=0.9, seed=i)
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5,
             pan=lambda tt: 0.8 - 1.6 * (tt - C.downbeats('finale')[6]) / 2.0)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.crunch(M['button'] + 0.8, bites=3, pan=S.pan(mid), gain=0.7)
    B.finish()
