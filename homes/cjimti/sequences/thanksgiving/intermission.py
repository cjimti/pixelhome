"""Intermission: five minutes of plum house filling with golden wheat before Thanksgiving's own set.

The shared countdown (pixelhome/intermission.py) does the telling: a deep plum bed holds the house and golden wheat
fills it toward the middle of Porch Front over 285 s. On top of it the wheat ripples as a breeze runs through it,
and autumn leaves (orange, red, amber, gold) keep landing on whatever is still plum, skittering along the roof in
the breeze and vanishing into the wheat when they reach it. On every minute a soft chime counts the minutes left,
each stroke a little flurry of leaves. When the fill meets in the middle the house swells, a whole pile of leaves
blows out of the porch and off both free ends, and the house settles back to plum for the show.

The music is a gentle G major country waltz, 96 to the minute, so each 16-bar strain is 30 s and every minute
starts on its first bar: the tune passes from a solo fiddle to clarinet, flute, cellos, oboe and the violins over
pizzicato oom-pah-pah, harp and held low strings; a tubular bell over glockenspiel chimes 4, 3, 2, 1 on the
minutes; the last strain grows into a timpani roll, and at the full house the dinner bell rings (a triangle and a
handbell) while trumpets and horns play the tune's head and land on one last G major chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.intermission import SECONDS, MARKS, FINALE, countdown, order, reach

CODE = 'TG20'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house glows plum and fills with golden wheat toward the porch over five minutes while autumn '
               'leaves land and skitter ahead of it and a chime counts the minutes. When it is full, the dinner bell '
               'rings, the leaves blow away and the show begins.')
D = SECONDS

BED = hexc('#900052')                   # deep plum
FILL = hexc('#ffa414')                  # golden wheat
LEAVES = [hexc(c) for c in ('#ff5a00', '#e01408', '#ff8a18', '#ffc000', '#c83000')]

BEAT = 60 / 96                          # a waltz at 96: a bar is 1.875 s, a 16-bar strain 30 s
BAR = 3 * BEAT
STRAIN = 16 * BAR
FULL = MARKS['full']                    # 285: the fill meets in the middle; the call-back lands here
CHIMES = [(m, 4 - i) for i, m in enumerate(MARKS['minutes'])]   # (minute, strokes): 4 left, 3, 2, 1


def chime_times():
    return [m + k * BAR for m, n in CHIMES for k in range(n)]


def leaves(G):
    """Every leaf: (land time, path distance, colour index, drift units/s, life s, flutter phase).
    Ordinary leaves every couple of seconds, a flurry of five on each chime stroke, all landing on what is still
    plum (never on Side), plus the finale's pile blown out of the porch (life < 0 marks those)."""
    rng = np.random.default_rng(31)
    v = order(G)
    ok = np.ones(G.N, bool)
    ok[G.seg['Side']] = False
    out = []

    def land(t, k):
        r = float(reach(t))
        free = np.flatnonzero(ok & (v < r - 0.03))
        if len(free) < 6:
            return
        for _ in range(k):
            n = free[int(rng.integers(len(free)))]
            out.append((t + rng.uniform(0, 0.35 if k > 1 else 0), float(G.pd[n]), int(rng.integers(len(LEAVES))),
                        rng.choice([-1, 1]) * rng.uniform(12, 40), rng.uniform(4, 8), rng.uniform(0, 6.3)))

    t = 2.0
    while t < FULL - 2:
        land(t, 1)
        t += rng.uniform(1.0, 2.6)
    for tc in chime_times():
        land(tc, 5)
    pf = G.seg['Porch Front']
    mid = float((G.pd[pf].min() + G.pd[pf].max()) / 2)
    for i in range(28):                                         # the pile blows out of the porch both ways
        out.append((FULL + 0.12 * i + rng.uniform(0, 0.1), mid + rng.uniform(-30, 30), int(rng.choice([0, 1, 4])),
                    (-1) ** i * rng.uniform(300, 480), -6.0, rng.uniform(0, 6.3)))
    return sorted(out)


def render(G, seed=1):
    out = countdown(G, bed=BED, fill=FILL, seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t_all = np.arange(F) * DT
    reach_t = reach(t_all)
    settle = smoothstep(FULL + 0.85 * FINALE, FULL + FINALE, t_all)
    L = np.array(leaves(G))
    t0, p0, ci, vel, life, ph = (L[:, k] for k in range(6))
    ci = ci.astype(int)
    burst = life < 0
    cols = np.array(LEAVES)[ci]

    for f in range(F):
        t = t_all[f]
        fr = out[f].astype(np.float64)
        filled = smoothstep(-0.012, 0.012, v - reach_t[f]) * (1 - settle[f])
        # the breeze through the wheat: a slow ripple running along the filled part
        fr *= (1 + 0.14 * np.sin(2 * np.pi * (d / 420 - t / 5.0)) * filled)[:, None]

        # the leaves on the roof
        live = (t >= t0) & (t < t0 + np.abs(life))
        for j in np.flatnonzero(live):
            a = t - t0[j]
            if burst[j]:
                p = p0[j] + vel[j] * a * (0.5 + 0.5 * min(1.0, a / 0.8))
                lvl = smoothstep(0, 0.25, a) * (1 - smoothstep(4.5, 6.0, a))
            else:
                # drift with the breeze, a skitter now and then, and drop in brightly
                p = p0[j] + vel[j] * a + 9 * np.sin(2.3 * a + ph[j])
                lvl = (smoothstep(0, 0.2, a) * (1 - smoothstep(life[j] - 1.2, life[j], a))
                       * (0.85 + 0.15 * np.sin(5.1 * a + ph[j])))
            if p < -20 or p > G.length + 20 or lvl <= 0:
                continue
            g = np.exp(-((d - p) / (10.0 if not burst[j] else 13.0)) ** 2)
            if not burst[j]:
                g *= 1 - smoothstep(-0.01, 0.01, v - reach_t[f])      # into the wheat and gone
            g *= lvl
            drop = 1.0 + 0.6 * np.exp(-a / 0.15) if not burst[j] else 1.0
            fr = fr * (1 - 0.85 * np.clip(g, 0, 1))[:, None] + light(cols[j], 0.85 * drop * g)
        out[f] = np.clip(fr, 0, 1)
    return out


# ---------------------------------------------------------------------------------------------------- music

# The waltz: (beat, beats, note) over a 16-bar strain and one chord a bar, G major. Original.
TUNE = [(0, 1, 'D4'), (1, 1, 'G4'), (2, 1, 'B4'), (3, 2, 'D5'), (5, 1, 'B4'), (6, 1, 'C5'), (7, 1, 'E5'),
        (8, 1, 'D5'), (9, 3, 'B4'), (12, 2, 'E5'), (14, 1, 'D5'), (15, 1, 'C5'), (16, 1, 'B4'), (17, 1, 'A4'),
        (18, 1, 'A4'), (19, 1, 'B4'), (20, 1, 'C5'), (21, 2, 'A4'), (23, 1, 'D4'),
        (24, 1, 'G4'), (25, 1, 'B4'), (26, 1, 'D5'), (27, 2, 'G5'), (29, 1, 'F5'), (30, 1, 'E5'), (31, 1, 'D5'),
        (32, 1, 'C5'), (33, 2, 'A4'), (35, 1, 'C5'), (36, 1, 'B4'), (37, 1, 'D5'), (38, 1, 'G4'), (39, 1, 'A4'),
        (40, 1, 'B4'), (41, 1, 'A4'), (42, 1, 'F#4'), (43, 1, 'A4'), (44, 1, 'C5'), (45, 3, 'G4')]
CHORDS = ['G', 'G', 'C', 'G', 'Em', 'C', 'D', 'D7', 'G', 'G7', 'C', 'Am', 'G', 'D', 'D7', 'G']
ROOT = {'G': 'G1', 'C': 'C2', 'Em': 'E1', 'D': 'D2', 'D7': 'D2', 'G7': 'G1', 'Am': 'A1'}
FIFTH = {'G': 'D2', 'C': 'G1', 'Em': 'B1', 'D': 'A1', 'D7': 'A1', 'G7': 'D2', 'Am': 'E2'}
TONES = {'G': ('D4', 'G4', 'B4'), 'C': ('C4', 'E4', 'G4'), 'Em': ('E4', 'G4', 'B4'), 'D': ('D4', 'F#4', 'A4'),
         'D7': ('C4', 'F#4', 'A4'), 'G7': ('D4', 'F4', 'B4'), 'Am': ('C4', 'E4', 'A4')}

# who plays what in each strain: tune (instrument, octave shift, velocity, gain), and what goes under it
PLAN = [
    dict(tune=('fiddle', 0, 70, 0.8), bass=0.7),
    dict(tune=('fiddle', 0, 76, 0.85), bass=1.0, chords=0.9),
    dict(tune=('clarinets', 0, 74, 0.75), bass=1.0, chords=0.9, low=0.6),
    dict(tune=('flutes', 0, 72, 0.9), bass=1.0, chords=0.7, harp=0.8),
    dict(tune=('cellos', -12, 76, 0.55), bass=0.9, chords=0.8, harp=0.6, low=0.4),
    dict(tune=('fiddle', 0, 80, 0.9), bass=1.0, chords=1.0, harp=0.7, low=0.6),
    dict(tune=('oboes', 0, 76, 1.2), bass=1.0, chords=0.9, low=0.7),
    dict(tune=('violins', 0, 76, 0.9), bass=1.0, chords=0.9, harp=0.7, low=0.8),
    dict(tune=('fiddle', 0, 82, 0.9), double=('flutes', 12, 70, 0.55), bass=1.1, chords=1.0, harp=0.8, low=0.8),
    dict(tune=('horns', 0, 74, 0.55), double=('fiddle', 0, 80, 0.7), bass=1.2, chords=1.1, harp=0.7, low=0.9,
         bars=8),
]


def score(M, G):
    from pixelhome.audio import note
    from pixelhome.ring import Orchestra
    n = note
    O = Orchestra(M, level=2.5)
    fiddle = M.sampler('Strings/Solo Violin/Arco Vib/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bpizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    bell = M.sampler('Percussion/TB_hit*.wav', tune=-12)
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    troll = M.hits('Percussion/Triangle3-Roll*.wav')
    for name, gain, rev in (('fiddle', 0.32, 0.35), ('pizz', 0.38, 0.25), ('bell', 0.42, 0.45), ('ding', 0.45, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    xs = G.pos[:, 0]
    x0, x1 = xs.min(), xs.max()
    porch = float(0.85 * (2 * (G.pos[G.seg['Porch Front'], 0].mean() - x0) / (x1 - x0) - 1))

    def play(inst, m, t, dur, vel, gain, pan=-0.1):
        if inst == 'fiddle':
            if dur > 1.2:
                O.hold('fiddle', fiddle, m, t, t + dur, vel, pan, gain)
            else:
                M.add('fiddle', fiddle.play(m, vel, dur=dur, release=0.2), t, gain, pan)
        else:
            O.play(inst, m, t, dur, vel, gain=gain)

    def tune(inst, t0, bars, shift, vel, gain):
        for b, l, m in TUNE:
            if b >= 3 * bars:
                continue
            accent = 6 if b % 3 == 0 else 0                    # lean on the downbeat, as a fiddler does
            play(inst, n(m) + shift, t0 + b * BEAT, l * BEAT * 0.95, vel + accent, gain)

    def strain(k, p):
        t0 = k * STRAIN
        bars = p.get('bars', 16)
        tune(p['tune'][0], t0, bars, *p['tune'][1:])
        if 'double' in p:
            tune(p['double'][0], t0, bars, *p['double'][1:])
        for j in range(bars):
            c = CHORDS[j]
            tb = t0 + j * BAR
            g = 1 + 0.3 * (j / bars) * (k == len(PLAN) - 1)           # the last strain grows
            # oom-pah-pah: root and fifth on alternate bars, the chord on two and three
            r = ROOT[c] if j % 2 == 0 else FIFTH[c]
            M.add('pizz', bpizz.play(n(r) + 12, 84), tb, 0.8 * p['bass'] * g, 0.15)
            M.add('pizz', cpizz.play(n(r) + 12, 68), tb, 0.4 * p['bass'] * g, -0.2)
            if 'chords' in p:
                for beat in (1, 2):
                    for m in TONES[c]:
                        M.add('pizz', pizz.play(n(m), 60 + 6 * (beat == 1)), tb + beat * BEAT,
                              0.28 * p['chords'] * g, 0.3)
            if 'harp' in p:                                     # the harp rolls the chord up through the bar
                for e, m in enumerate(TONES[c] + (TONES[c][0],)):
                    O.play('harp', n(m) + (12 if e == 3 else 0), tb + e * BEAT * 0.75, BEAT, 58,
                           gain=1.1 * p['harp'])
            if 'low' in p and j % 2 == 0:                      # low strings hold the root under two bars
                O.play('cellos', n(ROOT[c]) + 12, tb, 2 * BAR * 0.98, 52, gain=0.5 * p['low'])
                O.play('violas', n(TONES[c][1]) - 12, tb, 2 * BAR * 0.98, 46, gain=0.6 * p['low'])

    for k, p in enumerate(PLAN):
        strain(k, p)

    # the chime counts the minutes left: a soft tubular bell on G with the glockenspiel above it
    for m, count in CHIMES:
        for i in range(count):
            t = m + i * BAR
            M.add('bell', bell.play(n('G4'), 80), t, 0.8, porch)
            M.add('bell', glock.play(n('D5'), 70), t + 0.02, 0.35, porch)
            M.add('bell', glock.play(n('G5'), 60), t + BEAT, 0.25, porch)

    # into the finale: a timpani roll and a cymbal swell under the last two bars
    O.hit('timpani roll', FULL - 2 * BAR, 64, pitch=-3, gain=0.3)
    O.hit('timpani roll', FULL - BAR, 84, pitch=-3, gain=0.35)
    O.hit('cymbal swell', FULL - 1.7, 92, gain=0.35)

    # the call-back: the dinner bell (a triangle rung round its corners, a handbell) and the brass with the tune's head
    for i in range(2):
        M.add('ding', troll.play(96, dur=1.6), FULL + i * 1.4, 0.7, porch)
    for i in range(6):
        M.add('ding', tri.play(110 - 6 * i), FULL + 2.9 + 0.22 * i, 0.6, porch)
    for i in range(5):
        M.add('bell', bell.play(n('D5') if i % 2 else n('G5'), 104 - 6 * i), FULL + 0.18 * i, 0.55, porch)
    O.hit('crash', FULL, 100, gain=0.4)
    O.hit('timpani', FULL, 104, pitch=-5, gain=0.45)
    for b, l, m in TUNE:
        if b >= 12:
            break
        t, dur = FULL + b * BEAT, l * BEAT * 0.95
        O.play('trumpets', n(m), t, dur, 92, gain=0.5)
        O.play('horns', n(m) - 12, t, dur, 88, gain=0.55)
        play('fiddle', n(m), t, dur, 96, 0.8)
    for j in range(4):
        c = CHORDS[j]
        tb = FULL + j * BAR
        O.play('tuba', n(ROOT[c]) + 12, tb, BEAT * 0.8, 92, gain=0.5)
        M.add('pizz', bpizz.play(n(ROOT[c]) + 12, 100), tb, 0.9, 0.15)
        for beat in (1, 2):
            for m in TONES[c]:
                O.play('trombones', n(m) - 12, tb + beat * BEAT, BEAT * 0.5, 80, gain=0.4)
                M.add('pizz', pizz.play(n(m), 84), tb + beat * BEAT, 0.4, 0.3)
    # a little run up from the fiddle and the last chord
    last = FULL + 4 * BAR + BEAT
    for i, m in enumerate(('D5', 'E5', 'F#5')):
        play('fiddle', n(m), last - BEAT + i * BEAT / 3, BEAT / 3 * 0.9, 90, 0.8)
    O.hit('timpani', last, 108, pitch=-5, gain=0.5)
    O.hit('crash', last, 90, gain=0.3)
    O.play('tuba', n('G1') + 12, last, 1.4, 100, gain=0.55)
    for m in ('G3', 'B3', 'D4', 'G4'):
        O.play('trombones', n(m) - 12, last, 1.5, 88, gain=0.4)
        O.play('horns', n(m), last, 1.5, 86, gain=0.4)
        M.add('pizz', pizz.play(n(m) + 12, 104), last, 0.45, 0.3)
    play('fiddle', n('G5'), last, 1.6, 96, 0.8)
    M.add('bell', glock.play(n('G5'), 96), last, 0.4, 0.1)
    M.add('ding', tri.play(100), last, 0.5, porch)
