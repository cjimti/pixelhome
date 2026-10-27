"""Jingle Bells: The six roof runs are the bars of a glockenspiel and the house plays the chorus of
Jingle Bells. Each note strikes its run with a mallet spark, and the run rings in a standing-wave
mode of a free bar: the higher the note, the more nodes (dark points) along it. Rings decay and
overlap; sleigh-bell sparkles shake on the off-beats. Second time through the mirror-image run
answers each note in harmony, and the last chord rings the whole house."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM06'
TITLE = 'Jingle Bells'
KIND = 'show'
DESCRIPTION = ('The roof runs are glockenspiel bars and the house plays Jingle Bells: every note rings its '
               'run in a standing wave, more nodes for higher notes, sleigh bells on the off-beats.')

# pitch -> (run, mode number, colour); E and F, the commonest notes, sit on the two wing fronts
NOTES = {'C': ('Side', 1, '#ff2a18'), 'D': ('Porch Left', 2, '#18c048'), 'E': ('Left', 3, '#ffb028'),
         'F': ('Right', 4, '#ffe8c8'), 'G': ('Porch Front', 5, '#ff4060')}
PARTNER = {'Left': 'Right', 'Right': 'Left', 'Porch Left': 'Porch Right', 'Porch Right': 'Porch Left',
           'Side': 'Porch Front', 'Porch Front': 'Side'}
CHORUS = ('E1 E1 E2 E1 E1 E2 E1 G1 C1.5 D.5 E4 '
          'F1 F1 F1.5 F.5 F1 E1 E1 E.5 E.5 E1 D1 D1 E1 D2 G2 '
          'E1 E1 E2 E1 E1 E2 E1 G1 C1.5 D.5 E4 '
          'F1 F1 F1.5 F.5 F1 E1 E1 E.5 E.5 G1 G1 F1 D1 C4')
GOLD = hexc('#ffb030')
SPARK = hexc('#fff4e0')
BELL = hexc('#ffd890')
NIGHT = hexc('#0c0a30')


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    BEAT = 0.5                                     # 120 bpm
    T0 = 4.0
    strikes = []                                   # (time, run, mode, colour, amplitude, where)
    t = T0
    for rep in range(2):
        for tok in CHORUS.split():
            p, d = tok[0], float(tok[1:])
            run, n, col = NOTES[p]
            hit = rng.choice([0.0, 1.0]) if n % 2 else 0.0
            strikes.append((t, run, n, hexc(col), 1.0, hit))
            if rep == 1:                           # harmony: the mirror run answers a hair later
                strikes.append((t + 0.04, PARTNER[run], n, hexc(col), 0.6, 1.0 - hit))
            t += d * BEAT
    t_end = t
    for run in G.seg:                              # the last chord: everything rings together
        strikes.append((t_end, run, 1, GOLD, 1.1, 0.5))
    D = t_end + 7.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))

    u_of = {}
    for name, idx in G.seg.items():
        pi = G.pi[idx]
        order = np.argsort(pi)
        u = np.empty(len(idx))
        u[order] = np.linspace(0, 1, len(idx))
        u_of[name] = (idx, u)
    by_run = {name: [s for s in strikes if s[1] == name] for name in G.seg}
    shake = Flicker(rng, G.N, 3, 9)
    sparkle_cells = rng.random((F, G.N))

    for f in range(F):
        t = f * DT
        fr = out[f]
        bg = keys(t, [(0, 0), (2, 0.07), (D - 3, 0.07), (D, 0)])
        fr += light(NIGHT, np.full(G.N, bg))
        for name, (idx, u) in u_of.items():
            acc = np.zeros((len(idx), 3))
            for ts, _, n, col, a, hit in by_run[name]:
                age = t - ts
                if age < 0 or age > 4.5:
                    continue
                tau = 0.85 / (1 + 0.1 * n) if ts < t_end else 3.0
                env = a * np.exp(-age / tau) * smoothstep(0, 0.02, age) * (0.62 + 0.38 * np.exp(-age / 0.09))
                shape = np.abs(np.cos(n * np.pi * u))         # free bar: antinodes at the ends
                fvis = 2.5 + 0.6 * n
                ring = 0.78 + 0.22 * np.cos(2 * np.pi * fvis * age)
                I = 1.0 * env * shape ** 1.2 * ring
                acc += perc(I)[:, None] * lerp(col, GOLD, 0.25)
                # the mallet: a white spark at the strike point that splashes a little way along
                sp = np.exp(-age / 0.07) * np.exp(-((u - hit) * len(idx) / 3.5) ** 2)
                acc += light(SPARK, 0.95 * a * sp)
            fr[idx] += acc

        # sleigh bells: a light shake of sparkles on the off-beats while the tune plays
        if T0 - 3 < t < t_end + 2:
            bt = (t - T0) / BEAT
            off = np.exp(-(((bt + 0.5) % 1) / 0.12) ** 2) if t > T0 else 0.5 + 0.5 * np.sin(2 * np.pi * t * 4)
            level = keys(t, [(T0 - 3, 0), (T0, 0.5), (t_end, 0.5), (t_end + 2, 0)])
            pick = sparkle_cells[f] < 0.035
            fr[pick] += light(BELL, level * off * (0.6 + 0.4 * shake(t)[pick]))
    return out
