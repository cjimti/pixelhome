"""The King in the Cemetery: the Pumpkin King, fallen, despairs in a stone angel's arms, then catches fire again.

A cold grey night in the cemetery: fog drifting along the wings, grey headstones, and on the porch a stone angel,
her pale wings spread across Porch Front. The Pumpkin King lies in her arms, dim, red tatters of his stolen suit
fluttering round him. His theme comes slowly in A minor on a solo cello over a low choir, and every phrase sighs
out from the porch in a cold blue wave. Then a spark: an ember glows in his skull and his theme turns to A major on
celesta and harp, sparks flicking round him as the grey warms. The waltz builds, flames climb out from the porch
along the roof as he rises, the angel fades into the firelight, and on the crash of the full band the whole house
roars orange: he leaps up and races off along the left wing and out along Side, a white streak with a gold wake,
to put things right, while the house blazes behind him.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() both read its events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, drift, ORANGE, PUMPKIN, FLAME, WHITE, GOLD, ICE, GREY, RED,
                                 NIGHT, MOON)

CODE = 'NM17'
TITLE = 'The King in the Cemetery'
KIND = 'show'
DESCRIPTION = ('The fallen Pumpkin King lies in a stone angel\'s arms on the porch while the house stays cold and '
               'grey. Then a spark catches, fire climbs out along the roof, and he races off with the whole house '
               'blazing orange.')
VOICEOVER = ('In a lonely cemetery, a fallen king wondered what he had done. And then he remembered who he was.')

STONE = hexc('#a8b0c0')
COLD = hexc('#5070a0')


def compose():
    C = Chart()
    C.rest(2.5)                                                                     # the cold cemetery
    C.mark('lament')
    C.play('king', style='hold', bars=(0, 8), bpm=66, tag='lament')                 # despair, a solo cello
    C.mark('turn')
    C.play('king', style='arp', bars=(8, 12), bpm=80, major=True, tag='turn')       # a spark: he remembers
    C.mark('rise')
    C.play('king', style='waltz', bars=(12, 16), bpm=100, major=True, tag='rise')   # the fire climbs
    C.mark('blaze')
    C.play('king', style='drive', bars=(0, 8), bpm=132, major=True, tag='blaze')    # he leaps up and races off
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def run_path(S):
    """Where he runs in the blaze: from the angel's arms on the porch along Porch Left, Left and out along Side."""
    t0 = M['blaze'] + 2.4
    return [(M['blaze'], S.mid - 40), (t0, S.mid - 40), (t0 + 5.5, -60)]


def render(G, seed=17):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    t_la, t_tu, t_ri, t_bl = M['lament'], M['turn'], M['rise'], M['blaze']
    lament = np.array([n[0] for n in C.tunes('lament')])
    turn = np.array([e[0] for e in C.events if e[5] == 'turn' and e[4] in ('arp', 'tune')])
    downs = np.array(C.downbeats('blaze') + C.downbeats('rise'))
    stones = (G.pi % 19 == 5) & ~S.porch
    tat = mid + rng.uniform(-90, 90, 14)
    tat_ph = rng.uniform(0, 2 * np.pi, 14)
    rpath = run_path(S)
    t_go = rpath[1][0]
    wings = S.wings | S.run['Side']

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 2.0, t)
        warm = smoothstep(t_tu, t_bl, t)                    # grey to orange
        fire = smoothstep(t_ri, t_bl, t)
        blaze = smoothstep(t_bl - 0.1, t_bl + 0.3, t)
        # the cold cemetery: night blue going grey, fog on the wings, headstones
        cold = up * (1 - 0.6 * warm)
        fr = light(NIGHT, 0.26 * cold * np.ones(G.N))
        m = 0.5 + 0.5 * drift(5, d - 35 * t, 110.0)
        fr += light(GREY, 0.6 * cold * (0.1 + 0.9 * m ** 2) * (0.4 + 0.6 * wings))
        fr += light(STONE, 0.5 * cold * stones)
        fr += light(PUMPKIN, 0.3 * warm * (1 - blaze) * np.ones(G.N))
        # the stone angel: pale wings spread over the porch front, her head over him
        ang = up * (1 - smoothstep(t_ri, t_bl, t))
        breathe = 0.9 + 0.1 * np.sin(2 * np.pi * t / 6.0)
        fr += light(STONE, 0.55 * ang * breathe * (S.blob(mid - 120, 70) + S.blob(mid + 120, 70)))
        fr += light(MOON, 0.35 * ang * S.blob(mid + 60, 22))
        # each phrase of his lament sighs out from the porch in a cold wave
        for tn in lament[(lament <= t) & (lament > t - 4)]:
            a = t - tn
            fr += light(COLD, 0.75 * np.exp(-a / 1.6) * np.exp(-((np.abs(d - mid) - 70 - 260 * a) / 80) ** 2))
        # sparks when he remembers: orange flicks round him on each note
        for i, tn in enumerate(turn[(turn <= t) & (turn > t - 0.8)]):
            a = t - tn
            k = int(tn * 100)
            off = ((k * 37) % 300) - 150
            fr += light(ORANGE if k % 2 else GOLD, 1.0 * np.exp(-a / 0.35) * S.blob(mid + off * 1.6, 25 + 80 * a))
        # the fire climbs out from the porch as the waltz builds
        flick = 0.72 + 0.28 * np.sin(19 * t + d / 7) * np.sin(4.3 * t - d / 17)
        if fire > 0:
            reach = 40 + 1000 * fire ** 1.4
            fr += light(FLAME, 0.85 * fire * smoothstep(reach + 60, reach - 60, np.abs(d - mid)) * flick)
            fr += light(GOLD, 0.4 * fire * smoothstep(reach * 0.5 + 40, reach * 0.5 - 40, np.abs(d - mid)) * flick)
        # the blaze: the whole house roaring orange, gold on each downbeat
        if t >= t_bl - 0.1:
            a = t - t_bl
            fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * np.ones(G.N)) if a >= 0 else 0
            beat = pulse(t, downs, 0.25)
            fr += light(ORANGE, (0.7 + 0.2 * flick) * blaze * np.ones(G.N))
            fr += light(FLAME, 0.6 * blaze * flick)
            fr += light(GOLD, 0.35 * beat * blaze * np.ones(G.N))
            tongue = np.clip(np.sin((np.abs(d - mid) - 420 * a) / 45) * np.sin(d / 23 + 3 * t), 0, 1) ** 2
            fr += light(GOLD, 0.7 * blaze * tongue)
            fr *= (1 - 0.35 * blaze * np.clip(np.sin(d / 31 - 2.6 * t) * np.sin(d / 57 + 1.7 * t), 0, 1))[:, None]
            fr += S.burst([(t_bl, 1.0, mid - 40), (t_bl + 0.15, 0.8, mid - 200), (t_bl + 0.3, 0.8, mid + 160)],
                          t, seed=7, n=18, colors=(WHITE, GOLD))
        # the Pumpkin King: dim in her arms, an ember in his skull, rising, then racing off
        p = keys(t, rpath) if t >= t_bl else mid - 40
        lvl = up * (0.65 + 0.1 * warm + 0.3 * fire)
        if t >= t_go:
            trail = smoothstep(p - 20, p + 30, d) * np.exp(-np.clip(d - p, 0, None) / 220) * (t < D - 1)
            fr += light(GOLD, 0.8 * trail)
            fr += light(WHITE, 0.6 * S.blob(p, 30))
        if p > -30:
            # his stolen suit in tatters, fluttering red round him until the fire takes it
            tl = up * (1 - fire)
            for x, ph in zip(tat, tat_ph):
                fr += light(RED, 0.55 * tl * (0.5 + 0.5 * np.sin(5 * t + ph)) * S.blob(x, 6))
            ember = warm * (0.7 + 0.3 * np.sin(11 * t))
            fr = S.jack(fr, p, lvl, facing=-1, glow=0.45 + 0.5 * fire)
            fr += light(ORANGE, 0.8 * ember * S.blob(p - 4, 12) * (t < t_go + 0.5))
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.4)
    parts = {
        ('lament', 'tune'): [('cellos', 0, 4, 0.85), ('oboes', 12, -14, 0.25)],
        ('lament', 'hold'): [('choir', -12, -24, 0.4), ('violas', 0, -18, 0.3)],
        ('lament', 'pedal'): [('basses', -12, -12, 0.45)],
        ('turn', 'tune'): [('clarinets', 0, 0, 0.6), ('horns', 0, -10, 0.4)],
        ('turn', 'arp'): [('celesta', 12, -6, 0.5), ('harp', 0, -6, 0.5)],
        ('turn', 'pedal'): [('cellos', 0, -12, 0.45)],
        ('rise', 'tune'): [('horns', 0, 6, 0.8), ('violins', 12, -2, 0.55), ('choir', 0, -10, 0.5)],
        ('rise', 'bass'): [('tuba', -12, 0, 0.65), ('basses', 0, -6, 0.5)],
        ('rise', 'chord'): [('violas', 0, -8, 0.4), ('pizz', 0, -6, 0.4)],
        ('blaze', 'tune'): [('trumpets', 0, 8, 0.75), ('horns', 0, 8, 0.75), ('violins', 12, 0, 0.6),
                            ('choir', 0, 0, 0.7)],
        ('blaze', 'bass'): [('tuba', -12, 4, 0.7), ('cellos', 0, -2, 0.5)],
        ('blaze', 'chord'): [('trombones', 0, -6, 0.45), ('violas', 0, -8, 0.4)],
        ('blaze', 'snare'): [('snare', 0, -2, 0.5)],
    }
    B.perform(C.events, parts)
    t_la, t_tu, t_ri, t_bl = M['lament'], M['turn'], M['rise'], M['blaze']
    rpath = run_path(S)
    # the cold: a low ghostly pad under the opening
    for m in (45, 52, 57):
        B.play('ghost', m, 0.0, t_tu - 0.5, 60, gain=0.25)
    B.hit('triangle', t_tu, 80, gain=0.4)
    B.hit('timpani roll', t_ri, 90, pitch=-3, gain=0.4)
    B.hit('timpani roll', t_ri + 3.5, 110, pitch=-3, gain=0.5)
    B.hit('cymbal swell', t_bl - 1.6, 110, gain=0.6)
    B.hit('crash', t_bl, 124, gain=0.7)
    B.hit('bass drum', t_bl, 124, gain=0.7)
    for t, k, g in C.beats:
        if g == 'blaze' and k == 0:
            B.hit('timpani', t, 112, pitch=-5, gain=0.45)
    B.hit('crash', C.marks['end'] - 2.0, 124, gain=0.6)
    B.hit('bass drum', C.marks['end'] - 2.0, 124, gain=0.7)
    for m in (45, 57, 61, 64, 69):
        B.play('horns' if m < 60 else 'trumpets', m, C.marks['end'] - 2.0, 1.8, 110, gain=0.6)
    # the stage: cold wind, then the fire catching and roaring, and the whoosh as he races off
    B.effects([(0, -4), (t_tu, -8), (t_ri, -4), (t_bl, 0), (t_bl + 3, -6)])
    B.wind(0.0, t_tu + 2, level=0.5, pan=-0.2)
    B.fire(t_ri, C.marks['end'], level=lambda tt: np.clip(0.2 + 0.8 * (tt - t_ri) / (t_bl - t_ri), 0.2, 1.0),
           pan=0.0)
    B.boom(t_bl, pan=S.pan(S.mid), gain=0.8)
    B.whoosh(rpath[1][0], seconds=1.6, up=True, pan=S.pan(S.mid), gain=0.8)
    B.whoosh(rpath[1][0] + 2.0, seconds=2.0, up=False, pan=-0.8, gain=0.7)
    B.finish()
