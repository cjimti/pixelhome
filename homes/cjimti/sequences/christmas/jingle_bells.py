"""Jingle Bells: The six roof runs are the bars of a glockenspiel and the house plays the chorus of
Jingle Bells. Each note strikes its run with a mallet spark, and the run rings in a standing-wave
mode of a free bar: the higher the note, the more nodes (dark points) along it. Rings decay and
overlap; sleigh-bell sparkles shake on the off-beats. Second time through the mirror-image run
answers each note in harmony, and the last chord rings the whole house."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'CH06'
TITLE = 'Jingle Bells'
KIND = 'show'
DESCRIPTION = ('The roof runs are glockenspiel bars and the house plays Jingle Bells: every note rings its '
               'run in a standing wave, more nodes for higher notes, sleigh bells on the off-beats.')
VOICEOVER = 'Every run on the roof is a bell, and tonight the house plays Jingle Bells.'

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


BEAT = 0.5                                         # 120 bpm
T0 = 4.0                                           # the first note of the chorus
SEED = 26


def strikes_of(G, rng):
    """Every strike, in order: (time, run, mode, colour, amplitude, where along the run 0..1), and when the last
    chord rings. Draws the mallet ends from rng, so render() and score() share them."""
    strikes = []
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
    return strikes, t_end


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    strikes, t_end = strikes_of(G, rng)
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


# ---- music: the chorus as the lights play it, in C at 120 bpm, two bars of sleigh bells in front ----
D = T0 + 2 * sum(float(tok[1:]) for tok in CHORUS.split()) * BEAT + 7.0
OCTAVE = {'C': 'C5', 'D': 'D5', 'E': 'E5', 'F': 'F5', 'G': 'G5'}      # the tune as the glockenspiel sounds it
HARMONY = ['C', 'C', 'C', 'C', 'F', 'C', 'D7', 'G7', 'C', 'C', 'C', 'C', 'F', 'C', 'G7', 'C']   # a chord per bar
TONES = {'C': ('C', 'E', 'G'), 'F': ('F', 'A', 'C'), 'D7': ('D', 'F#', 'A', 'C'), 'G7': ('G', 'B', 'D', 'F')}
ROOTS = {'C': ('C2', 'G2'), 'F': ('F2', 'C2'), 'D7': ('D2', 'A2'), 'G7': ('G2', 'D2')}


def score(M, G):
    from pixelhome.audio import note
    n = note
    rng = np.random.default_rng(SEED)
    strikes, t_end = strikes_of(G, rng)

    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    glock2 = M.sampler('Percussion/Glock/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    flute_s = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_s = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    sleigh_m = M.hits('Miscellania Raw/Misc 2/sleighbell1_hit_[0-9].wav')
    sleigh_shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    cym = M.hits('Percussion/susCymb1-hit_f_*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    block = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')

    for name, gain, rev in (('tune', 0.4, 0.18), ('harm', 0.3, 0.2), ('accomp', 0.34, 0.12), ('bass', 0.48, 0.06),
                            ('bells', 0.3, 0.15), ('ring', 0.36, 0.3)):
        M.bus(name, gain=0.76 * gain, reverb=rev)

    def pan_run(run, u):                         # where a strike lands on the house, left/right from the street
        idx = G.seg[run]
        order = np.argsort(G.pi[idx])
        x = G.pos[idx[order], 0]
        xx = np.interp(u, np.linspace(0, 1, len(idx)), x)
        lo, hi = G.pos[:, 0].min(), G.pos[:, 0].max()
        return float(0.85 * (2 * (xx - lo) / (hi - lo) - 1))

    def bar_of(t):
        return int((t - T0 + 1e-6) // (4 * BEAT)) % 16

    def below(m, chord):                         # the nearest chord tone at least a third under m
        pcs = [n(p + '4') % 12 for p in TONES[chord]]
        k = m - 3
        while k % 12 not in pcs:
            k -= 1
        return k

    # the melody and its answer, from the strikes themselves: each lead strike rings its note where it lands
    lead = [s for s in strikes if s[4] == 1.0]
    half = len(CHORUS.split())
    durs = [float(tok[1:]) * BEAT for tok in CHORUS.split()] * 2
    letters = [tok[0] for tok in CHORUS.split()] * 2
    for i, ((t, run, _, _, _, hit), d, p) in enumerate(zip(lead, durs, letters)):
        rep = i // half
        m = n(OCTAVE[p])
        pan = pan_run(run, hit)
        M.add('tune', glock.play(m, 104), t, 1.0, pan)
        if rep == 0:
            pl = flute_s if d >= 1.0 else flute
            M.add('tune', pl.play(m, 98, dur=d * 0.92), t, 0.75, 0.6 * pan)
            M.add('tune', clar.play(m - 12, 90, dur=d * 0.9), t, 0.45, 0.6 * pan)
        else:
            pl = tpt_s if d >= 1.0 else tpt
            M.add('tune', pl.play(m - 12, 104, dur=d * 0.92), t, 0.85, 0.5 * pan)
            M.add('tune', flute.play(m, 92, dur=d * 0.9), t, 0.45, 0.5 * pan)
    answers = [s for s in strikes if s[4] == 0.6]
    for (t, run, _, _, _, hit), p, d in zip(answers, letters[half:], durs[half:]):
        # the mirror run answers a hair later: the harmony
        h = below(n(OCTAVE[p]), HARMONY[bar_of(t)])
        pan = pan_run(run, hit)
        M.add('harm', glock2.play(h, 88), t, 0.8, pan)
        pl = horn_s if d >= 1.0 else horn
        M.add('harm', pl.play(h - 12, 96, dur=d * 0.92), t, 0.8, 0.5 * pan)
        M.add('harm', clar_s.play(h, 80, dur=d * 0.92), t, 0.35, 0.5 * pan)

    # the band: bass on one and three, chords on two and four; tuba and horns join the second time
    for k in range(-1, 32):
        rep = 0 if k < 16 else 1
        c = 'C' if k < 0 else HARMONY[k % 16]
        t = T0 + 4 * k * BEAT
        lo, fifth = ROOTS[c]
        for b, m in ((0, lo), (2, fifth)):
            if k == -1 and b == 2:
                m = 'G2'
            M.add('bass', bass.play(n(m), 100), t + b * BEAT, 0.9)
            if rep:
                M.add('bass', tuba.play(n(m), 96), t + b * BEAT, 0.7)
        for b in (1, 3):
            for p in TONES[c][:3] if c not in ('D7', 'G7') else TONES[c][1:]:
                m = n(p + '4')
                m = m - 12 if m > n('G4') else m
                M.add('accomp', vla.play(m, 86), t + b * BEAT, 0.4, 0.2)
                if rep:
                    M.add('accomp', horn.play(m, 90, dur=0.2), t + b * BEAT, 0.35, -0.2)
        if k >= 0 and k % 4 == 0:
            M.add('bells', block.play(70), t, 0.25)

    # sleigh bells: a shake that swells in over the first two bars (four a second, as the sparkles pulse), then
    # a hit on every off-beat while the tune plays, scattered over the house as the sparkles are
    t = T0 - 3 + 1 / 16
    while t < T0:
        lvl = (t - (T0 - 3)) / 3
        M.add('bells', sleigh.play(int(60 + 50 * lvl)), t, 0.3 + 0.7 * lvl, float(M.rng.uniform(-0.6, 0.6)))
        t += 0.25
    M.add('bells', sleigh_shake.play(90), T0 - 1.0, 0.5, 0.0)
    t = T0 + BEAT / 2
    while t < t_end + 2:
        lvl = 1.0 if t < t_end else max(0.0, 1 - (t - t_end) / 2)
        M.add('bells', (sleigh if int((t - T0) / BEAT) % 2 else sleigh_m).play(100), t, 0.75 * lvl,
              float(M.rng.uniform(-0.7, 0.7)))
        t += BEAT
    for i, m in enumerate(('C4', 'E4', 'G4', 'C5', 'E5', 'G5')):          # the pickup into the tune
        M.add('accomp', harp.play(n(m), 84), T0 - 0.6 + 0.09 * i, 0.7, -0.5 + 0.2 * i)

    # the last chord rings the whole house
    for m in ('C5', 'E5', 'G5', 'C6'):
        M.add('ring', glock.play(n(m), 110), t_end, 0.8)
    for m in ('C4', 'E4', 'G4', 'C5'):
        M.add('ring', tpt_s.play(n(m), 104, dur=4.5), t_end, 0.4, -0.3)
        M.add('ring', horn_s.play(n(m) - 12, 100, dur=5.0), t_end, 0.5, 0.3)
        M.add('ring', flute_s.play(n(m) + 12, 90, dur=4.5), t_end, 0.25)
    M.add('bass', tuba.play(n('C2'), 110), t_end, 1.0)
    M.add('bass', bass.play(n('C2'), 110), t_end, 1.0)
    M.add('bass', timp.play(110), t_end, 0.7)
    M.add('ring', cym.play(100), t_end, 0.45)
    M.add('ring', chimes.play(100), t_end + 0.1, 0.5)
    M.add('bells', sleigh_shake.play(110), t_end, 0.8)
    for i, m in enumerate(('C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'C5', 'E5', 'G5', 'C6')):
        M.add('accomp', harp.play(n(m), 90), t_end - 0.35 + 0.035 * i, 0.6, -0.6 + 0.13 * i)
