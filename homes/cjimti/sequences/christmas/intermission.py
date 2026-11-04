"""Intermission: five minutes of pine-green house wrapping up in red ribbon before the Christmas set.

The shared countdown (pixelhome/intermission.py) does the telling: a deep pine-green bed holds the house and a
candy-red ribbon fills it toward the middle of Porch Front over 285 s. On top of it, gold baubles hang on the red
every forty-odd units and shimmer once the ribbon reaches them, and snowflakes keep landing on whatever is still
green, twinkling and drifting a little until the ribbon covers them. On every minute sleigh bells count the minutes
left, each stroke a little flurry of snow. When the fill meets in the middle the house swells, a gold bow bursts out
of the porch in sparks that fly off both free ends, and the house settles back to green for the show.

The music is an original lullaby in D, 6/8 at 64 dotted crotchets to the minute, so each 16-bar strain is 30 s and
every minute starts on its first bar: the tune passes from a music box to flute, clarinet, a celesta, the violins,
oboe, horns and the flutes with the glockenspiel, over a rocking pizzicato bass, a harp rolling each chord and held
low strings; sleigh bells with a tubular bell count 4, 3, 2, 1 on the minutes; the last strain grows into a timpani
roll, and at the full house the sleigh bells ring out while trumpets and horns play the tune's head and land on one
last D major chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep
from pixelhome.intermission import SECONDS, MARKS, FINALE, countdown, order, reach

CODE = 'XM20'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house glows pine green and wraps up in red ribbon toward the porch over five minutes, with gold '
               'baubles on the ribbon, snow landing ahead of it and sleigh bells counting the minutes. When it is '
               'wrapped, a gold bow bursts and the show begins.')
D = SECONDS

BED = hexc('#007a28')                   # pine green
FILL = hexc('#ff1428')                  # candy-red ribbon
GOLD = hexc('#ffb81c')
SNOW = hexc('#e8f4ff')

EIGHTH = 60 / 64 / 3                    # 6/8 at 64 dotted crotchets: a bar is 1.875 s, a 16-bar strain 30 s
BAR = 6 * EIGHTH
STRAIN = 16 * BAR
FULL = MARKS['full']                    # 285: the fill meets in the middle; the call-back lands here
CHIMES = [(m, 4 - i) for i, m in enumerate(MARKS['minutes'])]   # (minute, strokes): 4 left, 3, 2, 1
BAUBLE = 44.0                           # units between baubles along the path


def chime_times():
    return [m + k * BAR for m, n in CHIMES for k in range(n)]


def baubles(G):
    """Path distances of the baubles (not on Side, which few can see) and each one's shimmer phase."""
    rng = np.random.default_rng(12)
    side = G.pd[G.seg['Side']].max()
    p = np.arange(side + BAUBLE / 2, G.length - 6, BAUBLE)
    return p, rng.uniform(0, 2 * np.pi, len(p))


def flakes(G):
    """Every flake: (land time, path distance, drift units/s, life s, twinkle phase). Ordinary flakes every second
    or two, a flurry of six on each sleigh-bell stroke, all landing on what is still green (never on Side), plus the
    finale's gold bow bursting out of the porch both ways (life < 0 marks those)."""
    rng = np.random.default_rng(25)
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
            out.append((t + rng.uniform(0, 0.4 if k > 1 else 0), float(G.pd[n]),
                        rng.choice([-1, 1]) * rng.uniform(4, 14), rng.uniform(5, 9), rng.uniform(0, 6.3)))

    t = 1.5
    while t < FULL - 2:
        land(t, 1)
        t += rng.uniform(0.8, 2.0)
    for tc in chime_times():
        land(tc, 6)
    pf = G.seg['Porch Front']
    mid = float((G.pd[pf].min() + G.pd[pf].max()) / 2)
    for i in range(36):                                         # the bow bursts out of the porch both ways
        out.append((FULL + 0.09 * i + rng.uniform(0, 0.08), mid + rng.uniform(-25, 25),
                    (-1) ** i * rng.uniform(320, 520), -6.0, rng.uniform(0, 6.3)))
    return sorted(out)


def render(G, seed=1):
    out = countdown(G, bed=BED, fill=FILL, seed=seed)
    F = len(out)
    v = order(G)
    d = G.pd
    t_all = np.arange(F) * DT
    reach_t = reach(t_all)
    settle = smoothstep(FULL + 0.85 * FINALE, FULL + FINALE, t_all)
    bp, bph = baubles(G)
    near = np.argmin(np.abs(d[:, None] - bp[None, :]), axis=1)          # each pixel's nearest bauble
    bshape = np.exp(-((d - bp[near]) / 5.5) ** 2)
    L = np.array(flakes(G))
    t0, p0, vel, life, ph = (L[:, k] for k in range(5))
    burst = life < 0
    hue = np.where(np.arange(len(L)) % 3 == 0, 1.0, 0.0)              # a third of the bow's sparks are white

    for f in range(F):
        t = t_all[f]
        fr = out[f].astype(np.float64)
        filled = smoothstep(-0.012, 0.012, v - reach_t[f]) * (1 - settle[f])
        # the baubles: gold on the ribbon, each with its own slow shimmer, brightest just after the ribbon arrives
        shimmer = 0.75 + 0.25 * np.sin(1.7 * t + bph[near])
        g = bshape * filled * shimmer
        fr = fr * (1 - 0.8 * g)[:, None] + light(GOLD, 0.7) * g[:, None]

        # the snow on the roof
        live = (t >= t0) & (t < t0 + np.abs(life))
        for j in np.flatnonzero(live):
            a = t - t0[j]
            if burst[j]:
                p = p0[j] + vel[j] * a * (0.5 + 0.5 * min(1.0, a / 0.8))
                lvl = smoothstep(0, 0.2, a) * (1 - smoothstep(4.0, 6.0, a))
                col = SNOW if hue[j] else GOLD
            else:
                p = p0[j] + vel[j] * a + 6 * np.sin(1.3 * a + ph[j])
                lvl = (smoothstep(0, 0.25, a) * (1 - smoothstep(life[j] - 1.5, life[j], a))
                       * (0.7 + 0.3 * np.sin(6.0 * a + ph[j]) ** 2))
                col = SNOW
            if p < -20 or p > G.length + 20 or lvl <= 0:
                continue
            g = np.exp(-((d - p) / (7.0 if not burst[j] else 12.0)) ** 2)
            if not burst[j]:
                g *= 1 - smoothstep(-0.01, 0.01, v - reach_t[f])       # under the ribbon and gone
            g *= lvl
            drop = 1.0 + 0.7 * np.exp(-a / 0.15) if not burst[j] else 1.1
            fr = fr * (1 - 0.85 * np.clip(g, 0, 1))[:, None] + light(col, 0.8 * drop * g)
        out[f] = np.clip(fr, 0, 1)
    return out


# ---------------------------------------------------------------------------------------------------- music

# The lullaby: (eighth, eighths, note) over a 16-bar strain in 6/8 and one chord a bar, D major. Original.
TUNE = [(0, 2, 'A4'), (2, 1, 'D5'), (3, 2, 'F#5'), (5, 1, 'E5'),
        (6, 3, 'D5'), (9, 3, 'A4'),
        (12, 2, 'B4'), (14, 1, 'C#5'), (15, 2, 'D5'), (17, 1, 'E5'),
        (18, 3, 'F#5'), (21, 3, 'E5'),
        (24, 2, 'G5'), (26, 1, 'F#5'), (27, 2, 'E5'), (29, 1, 'D5'),
        (30, 2, 'C#5'), (32, 1, 'D5'), (33, 3, 'E5'),
        (36, 2, 'A4'), (38, 1, 'B4'), (39, 2, 'C#5'), (41, 1, 'D5'),
        (42, 6, 'E5'),
        (48, 2, 'A4'), (50, 1, 'D5'), (51, 2, 'F#5'), (53, 1, 'A5'),
        (54, 3, 'G5'), (57, 3, 'F#5'),
        (60, 2, 'E5'), (62, 1, 'F#5'), (63, 2, 'G5'), (65, 1, 'E5'),
        (66, 3, 'F#5'), (69, 3, 'D5'),
        (72, 2, 'B4'), (74, 1, 'C#5'), (75, 2, 'D5'), (77, 1, 'B4'),
        (78, 2, 'A4'), (80, 1, 'F#4'), (81, 2, 'A4'), (83, 1, 'D5'),
        (84, 2, 'E5'), (86, 1, 'D5'), (87, 2, 'C#5'), (89, 1, 'E5'),
        (90, 6, 'D5')]
CHORDS = ['D', 'D', 'G', 'D', 'Em', 'A', 'A', 'A7', 'D', 'G', 'Em', 'D', 'G', 'D', 'A7', 'D']
ROOT = {'D': 'D2', 'G': 'G1', 'Em': 'E2', 'A': 'A1', 'A7': 'A1'}
FIFTH = {'D': 'A1', 'G': 'D2', 'Em': 'B1', 'A': 'E2', 'A7': 'E2'}
TONES = {'D': ('D4', 'F#4', 'A4'), 'G': ('D4', 'G4', 'B4'), 'Em': ('E4', 'G4', 'B4'), 'A': ('C#4', 'E4', 'A4'),
         'A7': ('C#4', 'G4', 'A4')}

# who plays what in each strain: tune (instrument, octave shift, velocity, gain), and what goes under it
PLAN = [
    dict(tune=('box', 0, 70, 0.9), bass=0.6),
    dict(tune=('box', 0, 76, 0.9), bass=0.9, harp=0.7),
    dict(tune=('flutes', 0, 72, 0.9), bass=1.0, harp=0.8, low=0.5),
    dict(tune=('clarinets', 0, 74, 0.75), bass=1.0, chords=0.8, low=0.6),
    dict(tune=('celesta', 0, 80, 0.8), bass=0.9, harp=0.6, low=0.5),
    dict(tune=('violins', 0, 74, 0.9), bass=1.0, chords=0.9, low=0.7),
    dict(tune=('oboes', 0, 76, 1.1), bass=1.0, harp=0.8, low=0.7),
    dict(tune=('horns', -12, 74, 0.6), double=('box', 12, 64, 0.5), bass=1.0, chords=0.9, low=0.8),
    dict(tune=('flutes', 0, 80, 0.95), double=('glock', 0, 70, 0.6), bass=1.1, chords=1.0, harp=0.8, low=0.8),
    dict(tune=('violins', 0, 80, 1.0), double=('flutes', 12, 66, 0.5), bass=1.2, chords=1.1, harp=0.8, low=0.9,
         bars=8),
]


def score(M, G):
    from pixelhome.audio import note
    from pixelhome.ring import Orchestra
    n = note
    O = Orchestra(M, level=2.5)
    box = M.synth('Plucks/Magic Music Box')
    cel = M.synth('Plucks/Fantasy Bell')
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bpizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    bell = M.sampler('Percussion/TB_hit*.wav', tune=-12)
    shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake1.wav')
    jingle = M.hits('Percussion/Sleighbells_Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    for name, gain, rev in (('box', 0.34, 0.4), ('pizz', 0.38, 0.25), ('bell', 0.42, 0.45), ('ding', 0.4, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    xs = G.pos[:, 0]
    x0, x1 = xs.min(), xs.max()
    porch = float(0.85 * (2 * (G.pos[G.seg['Porch Front'], 0].mean() - x0) / (x1 - x0) - 1))

    def synth_line(syn, notes, t0, gain, pan):
        """notes (t, midi, vel, dur) relative to t0, rendered in one pass of the synth."""
        if notes:
            M.add('box', syn.render(notes, max(t + d for t, _, _, d in notes) + 3.0), t0, gain, pan)

    def tune(inst, t0, bars, shift, vel, gain):
        line = []
        for e, l, m in TUNE:
            if e >= 6 * bars:
                continue
            accent = 6 if e % 6 == 0 else (3 if e % 3 == 0 else 0)    # lean on the bar, lilt on the half-bar
            t, dur = e * EIGHTH, l * EIGHTH * 0.95
            if inst in ('box', 'celesta'):
                line.append((t, n(m) + shift, vel + accent, dur))
            elif inst == 'glock':
                M.add('bell', glock.play(n(m) + shift, vel + accent), t0 + t, gain, porch)
            else:
                O.play(inst, n(m) + shift, t0 + t, dur, vel + accent, gain=gain)
        if inst == 'box':
            synth_line(box, line, t0, gain, -0.1)
        elif inst == 'celesta':
            synth_line(cel, line, t0, gain, 0.1)

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
            # the rocking bass: root on the bar, fifth on the half-bar
            for h, r in ((0, ROOT[c]), (3, FIFTH[c])):
                M.add('pizz', bpizz.play(n(r) + 12, 80 - 6 * (h > 0)), tb + h * EIGHTH, 0.8 * p['bass'] * g, 0.15)
                M.add('pizz', cpizz.play(n(r) + 12, 64 - 6 * (h > 0)), tb + h * EIGHTH, 0.35 * p['bass'] * g, -0.2)
            if 'chords' in p:                                   # the chord on the second and fifth eighths
                for e in (1, 2, 4, 5):
                    for m in TONES[c]:
                        M.add('pizz', pizz.play(n(m), 56 + 4 * (e in (1, 4))), tb + e * EIGHTH,
                              0.22 * p['chords'] * g, 0.3)
            if 'harp' in p:                                     # the harp rolls the chord up through the bar
                for e, m in enumerate(TONES[c] + (TONES[c][0], TONES[c][1], TONES[c][2])):
                    O.play('harp', n(m) + (12 if e >= 3 else 0), tb + e * EIGHTH, 2 * EIGHTH, 56 - 2 * e,
                           gain=1.0 * p['harp'])
            if 'low' in p and j % 2 == 0:                      # low strings hold the root under two bars
                O.play('cellos', n(ROOT[c]) + 12, tb, 2 * BAR * 0.98, 50, gain=0.5 * p['low'])
                O.play('violas', n(TONES[c][1]) - 12, tb, 2 * BAR * 0.98, 44, gain=0.6 * p['low'])

    for k, p in enumerate(PLAN):
        strain(k, p)

    # sleigh bells count the minutes left: a shake, a tubular bell on D with the glockenspiel above it
    for m, count in CHIMES:
        for i in range(count):
            t = m + i * BAR
            M.add('ding', shake.play(78), t - 0.15, 0.55, porch)
            M.add('bell', bell.play(n('D4'), 80), t, 0.8, porch)
            M.add('bell', glock.play(n('A5'), 70), t + 0.02, 0.35, porch)
            M.add('bell', glock.play(n('D6'), 58), t + 3 * EIGHTH, 0.22, porch)

    # into the finale: a timpani roll and a cymbal swell under the last two bars
    O.hit('timpani roll', FULL - 2 * BAR, 62, pitch=-5, gain=0.3)
    O.hit('timpani roll', FULL - BAR, 82, pitch=-5, gain=0.35)
    O.hit('cymbal swell', FULL - 1.7, 90, gain=0.35)

    # the call-back: sleigh bells ring out as the bow bursts, and the brass play the tune's head
    for i in range(10):
        M.add('ding', jingle.play(104 - 3 * i), FULL + i * EIGHTH, 0.6, porch + (0.5 if i % 2 else -0.5) * min(1, i / 4))
    for i in range(3):
        M.add('ding', shake.play(96), FULL + 0.9 + 1.2 * i, 0.6, (-0.6, 0.6, porch)[i])
    for i in range(5):
        M.add('bell', bell.play(n('A4') if i % 2 else n('D5'), 104 - 6 * i), FULL + 0.18 * i, 0.5, porch)
    O.hit('crash', FULL, 100, gain=0.4)
    O.hit('timpani', FULL, 104, pitch=-7, gain=0.45)
    for e, l, m in TUNE:
        if e >= 24:
            break
        t, dur = FULL + e * EIGHTH, l * EIGHTH * 0.95
        O.play('trumpets', n(m), t, dur, 92, gain=0.5)
        O.play('horns', n(m) - 12, t, dur, 88, gain=0.55)
        O.play('violins', n(m), t, dur, 90, gain=0.6)
    for j in range(4):
        c = CHORDS[j]
        tb = FULL + j * BAR
        O.play('tuba', n(ROOT[c]) + 12, tb, 3 * EIGHTH * 0.8, 92, gain=0.5)
        M.add('pizz', bpizz.play(n(ROOT[c]) + 12, 100), tb, 0.9, 0.15)
        for e in (1, 2, 4, 5):
            for m in TONES[c]:
                O.play('trombones', n(m) - 12, tb + e * EIGHTH, EIGHTH * 0.8, 78, gain=0.35)
                M.add('pizz', pizz.play(n(m), 80), tb + e * EIGHTH, 0.35, 0.3)
        M.add('ding', jingle.play(90), tb + 3 * EIGHTH, 0.45, porch)
    # a little run up on the glockenspiel and the last chord
    last = FULL + 4 * BAR + 3 * EIGHTH
    for i, m in enumerate(('A5', 'B5', 'C#6')):
        M.add('bell', glock.play(n(m), 84), last - 3 * EIGHTH + i * EIGHTH, 0.35, porch)
    O.hit('timpani', last, 108, pitch=-7, gain=0.5)
    O.hit('crash', last, 90, gain=0.3)
    O.play('tuba', n('D1') + 12, last, 1.4, 100, gain=0.55)
    for m in ('D3', 'F#3', 'A3', 'D4'):
        O.play('trombones', n(m) - 12, last, 1.5, 86, gain=0.4)
        O.play('horns', n(m), last, 1.5, 84, gain=0.4)
        M.add('pizz', pizz.play(n(m) + 12, 100), last, 0.4, 0.3)
    O.play('violins', n('D5'), last, 1.6, 94, gain=0.6)
    M.add('bell', glock.play(n('D6'), 96), last, 0.4, 0.1)
    M.add('ding', shake.play(100), last, 0.5, porch)
    M.add('ding', tri.play(100), last, 0.5, porch)
