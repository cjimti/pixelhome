"""Intermission: Halloween Town at night fills with ghoulish green before the Pumpkin King's story begins.

The shared countdown (pixelhome/intermission.py) does the telling: a deep purple-blue night holds the house and green
fills it toward the middle of Porch Front over 285 s. On the night that is left, the town's orange windows flicker
and Zero drifts back and forth, nose glowing, herded toward the porch as the green closes in; on every
minute a bell tolls the minutes left, each stroke a pale green ring out from the porch. When the fill meets in the
middle the town's march strikes up: a flame bursts over the porch, each note of the tune throws fire out along the
roof, the Pumpkin King rises in the middle of Porch Front and bows, and the house settles back to night for the show.

The music is a quiet reprise to wait by, built from the scenes' own themes (pixelhome/nightmare.py): Jack's
lament as a waltz at 96 (16 bars, exactly 30 s) and the citizens' march slowed to a nocturne at 64 (also 30 s), so
every minute starts a new section. The lament passes between celesta, clarinet, cellos, oboe and violins; the march
comes back as a ghostly hold for muted horn and bassoon. The last 15 s are the march at full tempo, gathering on
pizzicato and bassoon, and on the full house the whole band plays it as the call-back, ending on an E minor chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, Flicker
from pixelhome.intermission import SECONDS, MARKS, countdown, order, reach
from pixelhome.nightmare import Chart, Band, Stage, pulse, PUMPKIN, FLAME, GOLD

CODE = 'NM23'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('Halloween Town glows purple-blue with flickering orange windows and fills with ghoulish green toward the '
    "porch while Zero drifts ahead of it and a bell tolls the minutes. When it is full, the town's march "
    'plays and Jack rises over the porch.')
D = SECONDS

BED = hexc('#2a0ca8')
FILL = hexc('#7fd13b')
RING = hexc('#d0ffb8')
FULL = MARKS['full']
TOLLS = [(m, 4 - i) for i, m in enumerate(MARKS['minutes'])]   # (minute, strokes): 4 left, 3, 2, 1
BAR = 60 / 96 * 3                                             # strokes a bar of the lament apart


def compose():
    C = Chart()
    for theme, style, bpm, tag in (('king', 'arp', 96, 'k1'), ('king', 'waltz', 96, 'k2'), ('town', 'hold', 64, 't1'),
                                   ('king', 'waltz', 96, 'k3'), ('town', 'arp', 64, 't2'), ('king', 'arp', 96, 'k4'),
                                   ('town', 'hold', 64, 't3'), ('king', 'waltz', 96, 'k5'), ('king', 'arp', 96, 'k6')):
        C.play(theme, style=style, bpm=bpm, tag=tag)          # each exactly 30 s: every minute starts a section
    C.mark('gather')
    C.play('town', style='march', bpm=128, tag='gather')      # 15 s, gathering toward the full house
    C.mark('full')
    C.play('town', style='march', bars=(0, 4), bpm=128, tag='cheer')
    C.mark('sting')
    C.rest(SECONDS - C.t)
    C.mark('end')
    return C


C = compose()
M = C.marks
assert abs(M['full'] - FULL) < 1e-6, M['full']


def toll_times():
    return [m + k * BAR for m, n in TOLLS for k in range(n)]


def render(G, seed=1):
    out = countdown(G, bed=BED, fill=FILL, seed=seed)
    F = len(out)
    S = Stage(G)
    d, mid = S.d, S.mid
    rng = np.random.default_rng(seed)
    v = order(G)
    side = S.run['Side']
    t_all = np.arange(F) * DT
    reach_t = reach(t_all)
    settle = smoothstep(FULL + 0.85 * 15, FULL + 15, t_all)
    windows = (rng.random(G.N) < 0.1) * rng.uniform(0.6, 1.0, G.N)
    fl = Flicker(rng, G.N, 0.3, 2.0)
    tolls = np.array(toll_times())
    cheer = np.array([n[0] for n in C.tunes('cheer')])
    ph = rng.uniform(0, 2 * np.pi, 2)

    for f in range(F):
        t = f * DT
        fr = out[f].astype(np.float64)
        filled = smoothstep(-0.012, 0.012, v - reach_t[f]) * (1 - settle[f])
        # Halloween Town's windows on whatever is still night
        fr += light(PUMPKIN, 0.62 * windows * (1 - filled) * (0.8 + 0.2 * fl(t)))

        # each stroke of the bell: a pale green ring out from the porch
        for tb in tolls[(tolls <= t) & (tolls > t - 2.0)]:
            a = t - tb
            fr += light(RING, 0.42 * np.exp(-((np.abs(d - mid) - 700 * a) / 80) ** 2) * np.exp(-a / 0.8))

        # Zero drifts over the night that is left, herded toward the porch
        open_ = (v < reach_t[f]) & ~side
        if t < FULL and open_.any():
            lo, hi = d[open_].min(), d[open_].max()
            room = hi - lo
            s = 0.7 * np.sin(2 * np.pi * t / 17.0 + ph[0]) + 0.3 * np.sin(2 * np.pi * t / 6.1 + ph[1])
            vel = 0.7 / 17.0 * np.cos(2 * np.pi * t / 17.0 + ph[0]) + 0.3 / 6.1 * np.cos(2 * np.pi * t / 6.1 + ph[1])
            amp = min(340.0, max(0.0, room / 2 - 40))
            p = float(np.clip((lo + hi) / 2 + amp * s, lo + 35, hi - 35)) if room > 70 else mid
            lvl = smoothstep(30, 110, room) * smoothstep(0, 4, t)
            if lvl > 0:
                fr = S.zero(fr, p, lvl, 1 if vel >= 0 else -1, t, nose=0.8 + 0.2 * np.sin(2 * np.pi * t / 2.5))

        # the finale: a flame over the porch, the tune throwing fire along the roof, Jack rising and bowing
        if t >= FULL:
            a = t - FULL
            fr += light(FLAME, 1.1 * np.exp(-a / 0.7) * S.blob(mid, 60 + 300 * min(a, 1.0)))
            for j in np.flatnonzero((cheer <= t) & (cheer > t - 1.0)):
                b = t - cheer[j]
                front = mid + (1 if j % 2 else -1) * (250 + 900 * b)
                fr += light(FLAME, 1.0 * np.exp(-b / 0.45) * np.exp(-((d - front) / 120) ** 2))
            fr += light(GOLD, 0.45 * pulse(t, [M['sting']], 0.5) * S.blob(mid, 400))
            rise = smoothstep(0.3, 2.0, a)
            bow = 1.0 - 0.3 * smoothstep(M['sting'] + 2.0, M['sting'] + 2.8, t) \
                + 0.3 * smoothstep(M['sting'] + 3.2, M['sting'] + 3.8, t)
            gone = 1 - smoothstep(FULL + 12.3, FULL + 14.6, t)
            fr = S.jack(fr, mid + 9, rise * bow * gone, facing=-1, glow=0.5 * rise * gone)
        out[f] = np.clip(fr, 0, 1)
    return out


def score(M_, G):
    from pixelhome.audio import note
    S = Stage(G)
    B = Band(M_, level=3.3)
    bell = M_.sampler('Percussion/TB_hit*.wav', tune=-12)
    M_.bus('bell', gain=0.28, reverb=0.45)
    soft_bass = [('basses pizz', 0, -22, 0.55), ('cellos pizz', 12, -26, 0.35)]
    soft_chord = [('pizz', 0, -24, 0.4)]
    parts = {
        ('k1', 'tune'): [('celesta', 0, -8, 1.3)], ('k1', 'arp'): [('harp', 0, -24, 0.5)],
        ('k1', 'pedal'): [('cellos', 0, -30, 0.35)],
        ('k2', 'tune'): [('clarinets', 0, -16, 0.6)], ('k2', 'bass'): soft_bass, ('k2', 'chord'): soft_chord,
        ('t1', 'tune'): [('muted horn', 0, -18, 0.32)], ('t1', 'hold'): [('choir', 0, -34, 0.35)],
        ('t1', 'pedal'): [('cellos', 0, -30, 0.4)],
        ('k3', 'tune'): [('cellos', 0, -14, 0.65)], ('k3', 'bass'): soft_bass, ('k3', 'chord'): soft_chord,
        ('t2', 'tune'): [('celesta', 0, -8, 1.3)], ('t2', 'arp'): [('harp', 0, -24, 0.45)],
        ('t2', 'pedal'): [('basses', 0, -30, 0.4)],
        ('k4', 'tune'): [('oboes', 0, -18, 0.5)], ('k4', 'arp'): [('celesta', 12, -22, 0.7)],
        ('k4', 'pedal'): [('cellos', 0, -30, 0.35)],
        ('t3', 'tune'): [('bassoons', 0, -14, 0.6)], ('t3', 'hold'): [('violas', 0, -34, 0.35)],
        ('t3', 'pedal'): [('basses', 0, -30, 0.4)],
        ('k5', 'tune'): [('violins', 0, -16, 0.55)], ('k5', 'bass'): soft_bass, ('k5', 'chord'): soft_chord,
        ('k6', 'tune'): [('celesta', 0, -6, 1.3), ('flutes', 0, -22, 0.4)], ('k6', 'arp'): [('harp', 0, -22, 0.5)],
        ('k6', 'pedal'): [('cellos', 0, -28, 0.4)],
        ('gather', 'tune'): [('bassoons', 0, -6, 0.65), ('pizz', 12, -14, 0.4)],
        ('gather', 'bass'): [('basses pizz', 0, -6, 0.6), ('cellos pizz', 12, -12, 0.4)],
        ('gather', 'chord'): [('pizz', 0, -16, 0.35)], ('gather', 'snare'): [('snare', 0, -30, 0.25)],
        ('cheer', 'tune'): [('trombones', 0, 0, 0.38), ('horns', 0, 0, 0.34), ('choir', 0, -4, 0.38),
                            ('xylo', 0, -8, 0.25)],
        ('cheer', 'bass'): [('tuba', -12, 0, 0.42), ('basses pizz', 0, 0, 0.3)],
        ('cheer', 'chord'): [('horns', 0, -14, 0.3), ('pizz', 0, -8, 0.3)], ('cheer', 'snare'): [('snare', 0, -14, 0.25)],
    }
    B.perform(C.events, parts)
    # the bell tolls the minutes left, on E (in both the lament's A minor and the march's E minor)
    porch = S.pan(S.mid)
    for m, count in TOLLS:
        for i in range(count):
            t = m + i * BAR
            M_.add('bell', bell.play(note('E4'), 96), t, 1.0, porch)
            M_.add('bell', bell.play(note('E3'), 80), t, 0.4, porch)
    # into the full house: a roll and a swell, a crash on it, flame for the burst over the porch
    B.effects([(0, -4)])
    B.hit('timpani roll', FULL - 3.0, 80, gain=0.4)
    B.hit('cymbal swell', FULL - 1.6, 104, gain=0.5)
    B.hit('crash', FULL, 116, gain=0.55)
    B.hit('bass drum', FULL, 116, gain=0.6)
    B.boom(FULL, pan=porch, gain=0.6)
    B.fire(FULL, FULL + 2.5, level=0.5, pan=porch)
    # the sting: E minor on the whole band, then quiet before the show
    st = M['sting']
    B.hit('crash', st, 110, gain=0.45)
    B.hit('timpani', st, 112, gain=0.55)
    B.hit('bass drum', st, 112, gain=0.55)
    B.play('tuba', note('E1') + 12, st, 1.4, 104, gain=0.5)
    for m in ('E3', 'G3', 'B3', 'E4'):
        B.play('trombones', note(m), st, 1.6, 96, gain=0.32)
        B.play('horns', note(m), st, 1.6, 90, gain=0.25)
        B.play('choir', note(m), st, 2.0, 80, gain=0.35)
    B.play('xylo', note('E5'), st, 0.3, 110, gain=0.4)
    B.finish()
