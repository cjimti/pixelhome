"""Intermission: five minutes of purple house filling with jack-o'-lantern orange before Halloween's own set.

The shared countdown (pixelhome/intermission.py) does the telling: a purple bed holds the house and orange fills it
toward the middle of Porch Front over 285 s. On top of it the orange flickers like candles in carved pumpkins, two
bats flit over whatever is still purple (black cut-outs with hot yellow eyes, wings beating) and get squeezed toward
the porch as the orange closes in, and on every minute a church bell tolls the minutes left, each stroke a pale ring
out from the porch. When the fill meets in the middle the house swells, a flock of bats bursts out of the porch and
flies off both free ends, and the house settles back to purple for the show.

The music is a little D minor waltz for a music box, 96 to the minute, so each 16-bar strain is 30 s and every
minute starts on its first bar: the tune passes from the music box to cellos, clarinet, bassoon, violins and horns
over pizzicato oom-pah-pah and low strings, the tubular bell tolls 4, 3, 2, 1 on the minutes, the last strain
grows into a timpani roll, and at the full house the brass play the tune's head with a slide whistle, a bassoon
cackle and one last chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, smoothstep, Flicker
from pixelhome.intermission import SECONDS, MARKS, countdown, order, reach

CODE = 'HW19'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house glows purple and fills with candlelit orange toward the porch over five minutes while two '
               'bats flit ahead of it and a bell tolls the minutes. When it is full, the bats burst out and the show '
               'begins.')
D = SECONDS

BED = hexc('#4c0c9c')
FILL = hexc('#ff5a00')
EYE = hexc('#ffd000')
RING = hexc('#ffe8c0')

BEAT = 60 / 96                          # a waltz at 96: a bar is 1.875 s, a 16-bar strain 30 s
BAR = 3 * BEAT
STRAIN = 16 * BAR
FULL = MARKS['full']                    # 285: the fill meets in the middle; the call-back lands here
TOLLS = [(m, 4 - i) for i, m in enumerate(MARKS['minutes'])]   # (minute, strokes): 4 left, 3, 2, 1


def toll_times():
    return [m + k * BAR for m, n in TOLLS for k in range(n)]


def burst_bats():
    """The finale's flock: (launch time, direction along the path, speed in units/s)."""
    rng = np.random.default_rng(13)
    return [(FULL + 0.15 * i + rng.uniform(0, 0.1), (-1) ** i, rng.uniform(330, 470)) for i in range(10)]


def render(G, seed=1):
    out = countdown(G, bed=BED, fill=FILL, seed=seed)
    F = len(out)
    rng = np.random.default_rng(seed)
    v = order(G)
    d = G.pd
    pp = G.pd[G.path]
    side = np.zeros(G.N, bool)
    side[G.seg['Side']] = True
    pf = G.seg['Porch Front']
    mid = float((d[pf].min() + d[pf].max()) / 2)
    reach_t = reach(np.arange(F) * DT)
    fin_settle = smoothstep(FULL + 0.85 * 15, FULL + 15, np.arange(F) * DT)
    fl = Flicker(rng, G.N, 0.3, 1.4)
    tolls = np.array(toll_times())
    flock = burst_bats()
    phase = rng.uniform(0, 2 * np.pi, (2, 3))

    def sprite(fr, p, px, lvl, facing):
        """px [(offset, colour or None, level)] along the path from distance p; None cuts what is behind."""
        if lvl <= 0 or p < -40 or p > G.length + 40:
            return
        k0 = int(np.searchsorted(pp, p))
        for o, col, a in px:
            k = k0 + facing * o
            if 0 <= k < G.N:
                n = G.path[k]
                fr[n] *= 1 - 0.92 * min(1.0, lvl * 1.4)
                if col is not None:
                    fr[n] += light(col, a * lvl)

    def bat(t, flap):
        tip = 0.5 + 0.5 * np.sin(2 * np.pi * flap * t)   # wingtips come and go as it beats
        px = [(-1, EYE, 0.9), (0, None, 0), (1, EYE, 0.9), (-2, None, 0), (2, None, 0)]
        if tip > 0.35:
            px += [(-3, None, 0), (3, None, 0)]
        if tip > 0.75:
            px += [(-4, None, 0), (4, None, 0)]
        return px

    for f in range(F):
        t = f * DT
        fr = out[f].astype(np.float64)
        filled = smoothstep(-0.012, 0.012, v - reach_t[f]) * (1 - fin_settle[f])
        # candlelight in the pumpkins: the orange breathes, never dark
        fr *= (1 + 0.16 * fl(t) * filled)[:, None]

        # each stroke of the bell: a pale ring out from the porch
        for tb in tolls[(tolls <= t) & (tolls > t - 2.0)]:
            a = t - tb
            ring = np.exp(-((np.abs(d - mid) - 700 * a) / 80) ** 2) * np.exp(-a / 0.8)
            fr += light(RING, 0.42 * ring)

        # two bats over what is still purple, squeezed toward the porch as the orange closes in
        open_ = (v < reach_t[f]) & ~side
        if t < FULL and open_.any():
            lo, hi = d[open_].min(), d[open_].max()
            room = hi - lo
            for i in range(2):
                ph = phase[i]
                s = 0.65 * np.sin(2 * np.pi * t / 13.0 + ph[0]) + 0.35 * np.sin(2 * np.pi * t / 5.3 + ph[1])
                vel = (0.65 / 13.0 * np.cos(2 * np.pi * t / 13.0 + ph[0])
                       + 0.35 / 5.3 * np.cos(2 * np.pi * t / 5.3 + ph[1]))
                amp = min(320.0, max(0.0, room / 2 - 30))
                centre = (lo + hi) / 2 + (-90 if i == 0 else 90) * min(1.0, room / 600)
                p = float(np.clip(centre + amp * s, lo + 25, hi - 25)) if room > 50 else mid
                lvl = smoothstep(20, 90, room) * smoothstep(0, 4, t)
                sprite(fr, p, bat(t + i * 0.13, 2.2), lvl, 1 if vel >= 0 else -1)

        # the finale: the flock bursts out of the porch and away off both free ends
        for t0, dirn, speed in flock:
            a = t - t0
            if 0 <= a < 6:
                p = mid + dirn * speed * a * (0.6 + 0.4 * min(1.0, a))
                sprite(fr, p, bat(t + t0, 3.0), smoothstep(0, 0.3, a), int(dirn))
        out[f] = np.clip(fr, 0, 1)
    return out


# ---------------------------------------------------------------------------------------------------- music

# The waltz: (beat, beats, note) over a 16-bar strain (beats from its first bar) and one chord a bar. Original.
TUNE = [(0, 2, 'D5'), (2, 1, 'A4'), (3, 1, 'F5'), (4, 1, 'E5'), (5, 1, 'D5'), (6, 2, 'C#5'), (8, 1, 'A4'),
        (9, 3, 'E5'), (12, 2, 'G5'), (14, 1, 'Bb4'), (15, 1, 'A5'), (16, 1, 'G5'), (17, 1, 'F5'), (18, 1, 'E5'),
        (19, 1, 'D5'), (20, 1, 'C#5'), (21, 3, 'D5'),
        (24, 1, 'F4'), (25, 1, 'A4'), (26, 1, 'C5'), (27, 2, 'F5'), (29, 1, 'E5'), (30, 2, 'Db5'), (32, 1, 'C5'),
        (33, 3, 'Bb4'), (36, 1, 'A4'), (37, 1, 'D5'), (38, 1, 'F5'), (39, 2, 'G5'), (41, 1, 'E5'), (42, 1, 'E5'),
        (43, 1, 'A4'), (44, 1, 'C#5'), (45, 3, 'D5')]
CHORDS = ['Dm', 'Dm', 'A7', 'A7', 'Gm', 'Dm', 'A7', 'Dm', 'F', 'F', 'Bbm', 'Bbm', 'Dm', 'A7', 'A7', 'Dm']
ROOT = {'Dm': 'D2', 'A7': 'A1', 'Gm': 'G1', 'F': 'F1', 'Bbm': 'Bb1'}
TONES = {'Dm': ('D4', 'F4', 'A4'), 'A7': ('C#4', 'E4', 'G4'), 'Gm': ('D4', 'G4', 'Bb4'), 'F': ('C4', 'F4', 'A4'),
         'Bbm': ('Db4', 'F4', 'Bb4')}

# who plays what in each strain: tune (instrument, octave shift, velocity, gain), and what goes under it
PLAN = [
    dict(tune=('box', 0, 70, 1.0), bass=0.7),
    dict(tune=('box', 0, 76, 1.0), bass=1.0, chords=1.0),
    dict(tune=('cellos', -12, 76, 1.1), bass=0.9, chords=0.8, arp=0.7),
    dict(tune=('clarinets', -12, 74, 0.9), bass=1.0, chords=0.9, arp=0.6, low=0.6),
    dict(tune=('box', 0, 78, 1.0), bass=1.0, chords=1.0, harp=0.8, low=0.5),
    dict(tune=('bassoons', -12, 74, 0.85), bass=1.0, chords=1.0, arp=0.6),
    dict(tune=('violins', -12, 76, 1.0), bass=1.0, chords=0.8, low=0.8),
    dict(tune=('box', 0, 72, 1.0), bass=0.7, low=0.9),
    dict(tune=('horns', -12, 70, 0.45), bass=1.1, chords=1.1, arp=0.6, low=0.7),
    dict(tune=('violins', -12, 82, 0.8), double=('box', 0, 80, 0.9), bass=1.2, chords=1.2, arp=0.7, low=0.9,
         bars=8),
]


def score(M, G):
    from pixelhome.audio import note
    from pixelhome.ring import Orchestra
    n = note
    O = Orchestra(M, level=1.48)
    box = M.synth('Plucks/Magic Music Box')
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bpizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav')
    bell = M.sampler('Percussion/TB_hit*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    for name, gain, rev in (('box', 0.48, 0.4), ('pizz', 0.25, 0.25), ('bell', 0.4, 0.45), ('xylo', 0.33, 0.25),
                            ('sfx', 0.2, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    xs = G.pos[:, 0]
    x0, x1 = xs.min(), xs.max()
    porch = float(0.85 * (2 * (G.pos[G.seg['Porch Front'], 0].mean() - x0) / (x1 - x0) - 1))
    boxed = []

    def tune(inst, t0, bars, shift, vel, gain, pan=0.05):
        for b, l, m in TUNE:
            if b >= 3 * bars:
                continue
            t, dur = t0 + b * BEAT, l * BEAT
            if inst == 'box':
                boxed.append((t, n(m) + shift, vel, dur * 0.95))
            else:
                O.play(inst, n(m) + shift, t, dur * 0.95, vel, gain=gain)

    def strain(k, p):
        t0 = k * STRAIN
        bars = p.get('bars', 16)
        tune(*p['tune'][:1], t0, bars, *p['tune'][1:])
        if 'double' in p:
            tune(*p['double'][:1], t0, bars, *p['double'][1:])
        for j in range(bars):
            c = CHORDS[j]
            tb = t0 + j * BAR
            g = 1 + 0.25 * (j / bars) * (k == len(PLAN) - 1)          # the last strain grows
            # oom-pah-pah: the bass on one, the chord on two and three
            M.add('pizz', bpizz.play(n(ROOT[c]) + 12, 84), tb, 0.8 * p['bass'] * g, 0.2)
            M.add('pizz', cpizz.play(n(ROOT[c]) + 12, 70), tb, 0.45 * p['bass'] * g, -0.25)
            if 'chords' in p:
                for beat in (1, 2):
                    for m in TONES[c]:
                        M.add('pizz', pizz.play(n(m), 64 + 6 * (beat == 1)), tb + beat * BEAT,
                              0.3 * p['chords'] * g, 0.3)
            if 'arp' in p:                                      # the music box turns chord tones in eighths
                tones = [n(m) + 12 for m in TONES[c]]
                for e in range(6):
                    boxed.append((tb + e * BEAT / 2, tones[(e if e < 3 else 5 - e) % 3], int(50 * p['arp']) + 10,
                                  BEAT / 2))
            if 'harp' in p:
                for e, m in enumerate(TONES[c]):
                    O.play('harp', n(m), tb + e * BEAT, BEAT, 62, gain=0.6 * p['harp'])
            if 'low' in p and j % 2 == 0:                      # low strings hold the root under two bars
                O.play('cellos', n(ROOT[c]) + 12, tb, 2 * BAR * 0.98, 54, gain=0.55 * p['low'])
                O.play('basses', n(ROOT[c]) + 12, tb, 2 * BAR * 0.98, 50, gain=0.45 * p['low'])

    for k, p in enumerate(PLAN):
        strain(k, p)

    # the bell tolls the minutes left: D, an octave below to give it a tower's weight
    for m, count in TOLLS:
        for i in range(count):
            t = m + i * BAR
            M.add('bell', bell.play(n('D4'), 96), t, 1.0, porch)
            M.add('bell', bell.play(n('D3'), 80), t, 0.4, porch)

    # into the finale: a timpani roll and a cymbal swell under the last two bars, a slide whistle up to the hit
    from pixelhome.audio import slide
    O.hit('timpani roll', FULL - 2 * BAR, 70, gain=0.35)
    O.hit('timpani roll', FULL - BAR, 90, gain=0.4)
    O.hit('cymbal swell', FULL - 1.7, 100, gain=0.45)
    M.add('sfx', slide(0.0, 0.8, 380, 1500, 0.9, 0.5, 0.6), FULL - 0.9, 1.0, porch)

    # the call-back: the waltz's head on the whole band, then a bassoon cackle and one last chord
    O.hit('crash', FULL, 112, gain=0.5)
    O.hit('bass drum', FULL, 110, gain=0.55)
    O.hit('timpani', FULL, 110, pitch=-2, gain=0.5)
    for b, l, m in TUNE:
        if b >= 12:
            break
        t, dur = FULL + b * BEAT, l * BEAT * 0.95
        O.play('trumpets', n(m) - 12, t, dur, 92, gain=0.55)
        O.play('horns', n(m) - 12, t, dur, 90, gain=0.6)
        M.add('xylo', xylo.play(n(m), 100), t, 0.8, 0.1)
        boxed.append((t, n(m), 96, dur))
    for j in range(4):
        c = CHORDS[j]
        tb = FULL + j * BAR
        O.play('tuba', n(ROOT[c]), tb, BEAT * 0.8, 96, gain=0.6)
        M.add('pizz', bpizz.play(n(ROOT[c]) + 12, 100), tb, 0.9, 0.2)
        for beat in (1, 2):
            for m in TONES[c]:
                O.play('trombones', n(m) - 12, tb + beat * BEAT, BEAT * 0.5, 82, gain=0.45)
                M.add('pizz', pizz.play(n(m), 84), tb + beat * BEAT, 0.4, 0.3)
        M.add('pizz', wood.play(80), tb, 0.5, porch)
    cackle = FULL + 4 * BAR                                     # ha-ha-ha-haaa, down by semitones
    for i, m in enumerate(('A3', 'Ab3', 'G3', 'F#3', 'F3')):
        O.play('bassoons', n(m), cackle + i * 0.16, 0.12 if i < 4 else 0.5, 96, gain=0.9)
    last = cackle + 1.35
    O.hit('timpani', last, 112, gain=0.55)
    O.hit('crash', last, 100, gain=0.35)
    O.play('tuba', n('D1') + 12, last, 1.2, 104, gain=0.6)
    for m in ('D3', 'F3', 'A3', 'D4'):
        O.play('trombones', n(m), last, 1.4, 92, gain=0.4)
        M.add('pizz', pizz.play(n(m) + 12, 110), last, 0.5, 0.3)
    M.add('xylo', xylo.play(n('D5'), 110), last, 0.8, 0.1)
    M.add('xylo', xylo.play(n('D6'), 100), last, 0.5, 0.1)
    boxed.append((last, n('D5'), 100, 1.5))

    M.add('box', box.render(sorted(boxed), M.seconds + 3), 0.0, 1.0, 0.0)
