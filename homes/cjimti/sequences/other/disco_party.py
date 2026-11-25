"""Disco Party: a 120 BPM disco loop in black, white and silver. The five corners are disco stars that flash white on
every bar and pulse on every beat; around them the house takes turns being a light-up dance floor, a mirror ball's
roaming beams, bursts ringing out from the corners, a chase round every turn, checkerboard tiles, spotlights sweeping
the facade, waves and a stars finale, with silver sparkle throughout. Each port is held to a small power budget (port
1 has no working far-end injection), so white is never on many pixels at once. The score is original ballroom-disco:
a brass fanfare over four-on-the-floor, octave bass and strings, every hit taken from the same grid as the lights."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, nframes

CODE = 'OT31'
TITLE = 'Disco Party'
KIND = 'show'
DESCRIPTION = ('Dancing with the stars on the roofline: the corners flash like disco stars on every beat, under '
               'mirror-ball beams, a light-up dance floor and silver sparkle.')

BPM = 120
BEAT = 60 / BPM
BAR = 4 * BEAT
SECTION = 8 * BAR                    # 16 s
SECTIONS = ('floor', 'mirror_ball', 'bursts', 'chase', 'squares', 'sweep', 'waves', 'stars')
ORDER = list(range(8)) + [1, 4, 1, 6, 2, 1, 5, 7]     # the mirror ball comes round most in the second half
PAL = [hexc(h) for h in ('#ffffff', '#b8c4e0', '#ffffff', '#7d8aa8', '#ffffff', '#c8d4ff', '#e8ecf5', '#9aa6c4')]
WHITE = np.ones(3)
SILVER = hexc('#b8c4e8')
PORT_BUDGET = 0.10                   # mean channel level per port
PORT1 = ('Porch Left', 'Left', 'Side')


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    N, L = G.N, G.length
    d = G.pd.astype(float)
    x = G.pos[:, 0].astype(float)
    x0 = (x.max() + x.min()) / 2
    names = [n for n, _ in G.path_order]
    seg = np.array([names.index(G.seg_of[i]) for i in range(N)])
    cd = np.array([(G.pd[G.path[c]] + G.pd[G.path[c + 1]]) / 2 for c in G.corners])
    near = np.abs(d[:, None] - cd[None, :]).min(1)                 # distance to the nearest corner
    corner = np.exp(-(near / 10) ** 2)
    ends = np.exp(-(np.minimum(d, L - d) / 10) ** 2)
    tile = (d // 48).astype(int)
    P = len(PAL)
    pal = np.array(PAL)

    p1 = np.concatenate([G.seg[n] for n in PORT1])
    ports = [p1, np.setdiff1d(np.arange(N), p1)]
    beams = [(rng.uniform(0.04, 0.12), rng.uniform(0, 2 * np.pi), rng.uniform(30, 45)) for _ in range(8)]

    def pulse(tl, decay=0.12):
        return np.exp(-(tl % BEAT) / decay)

    def floor(tl, k):
        b = int(tl / BEAT)
        c = pal[(seg * 3 + b + k) % P]
        lit = (seg + b) % 2 == 0                       # half the runs light on each beat, the others go dark
        return perc(np.where(lit, 0.2 + 0.8 * pulse(tl, 0.22), 0.0))[:, None] * c

    def squares(tl, k):
        b = int(tl / BEAT)
        on = (tile + b) % 3 == 0
        c = pal[(tile * 3 + b + k) % P]
        return perc(np.where(on, 0.55 + 0.45 * pulse(tl), 0.0))[:, None] * c

    def mirror_ball(tl, k):
        out = np.zeros((N, 3))
        for j, (f, ph, w) in enumerate(beams):
            p = L * (0.5 + 0.5 * np.sin(2 * np.pi * f * tl + ph))
            out += perc(np.exp(-((d - p) / (0.6 * w)) ** 4))[:, None] * (SILVER if j % 3 == 0 else PAL[(j + k) % P])
        return out

    def bursts(tl, k):
        out = np.zeros((N, 3))
        for back, c, amp in ((0, PAL[(int(tl / BAR) + k) % P], 1.0), (BAR / 2, PAL[(int(tl / BAR) + k + 3) % P], 0.7)):
            age = (tl - back) % BAR
            r = 260 * age
            ring = np.exp(-((near - r) / 24) ** 2) + 0.15 * np.exp(-np.clip(r - near, 0, None) / 50) * (near < r)
            out += perc(amp * np.clip(ring, 0, 1) * np.exp(-age / 2.5))[:, None] * c
        return out

    def chase(tl, k):
        ph = (tl * 420 - d) % 280                      # comets every 280 units, tails behind them
        tail = np.where(ph < 90, np.exp(-ph / 25), 0.0)
        c = pal[((tl * 420 - d) // 280).astype(int) % P]
        return perc(tail)[:, None] * c

    def sweep(tl, k):
        off = 650 * np.abs(np.sin(np.pi * tl / (2 * BAR)))
        a, b = PAL[(int(tl / (2 * BAR)) + k) % P], PAL[(int(tl / (2 * BAR)) + k + 4) % P]
        out = perc(np.exp(-((x - (x0 - off)) / 50) ** 4))[:, None] * a
        out += perc(np.exp(-((x - (x0 + off)) / 50) ** 4))[:, None] * b
        return out

    def waves(tl, k):
        band = np.floor((np.abs(x - x0) - 240 * tl) / 110).astype(int)
        c = pal[(band + k) % P]
        return perc(np.where(band % 2 == 0, 0.6 + 0.4 * pulse(tl), 0.0))[:, None] * c

    def stars(tl, k):
        b = int(tl / BEAT)
        r = 300 * (tl % BEAT)
        return perc(0.8 * np.exp(-((np.abs(x - x0) - r) / 25) ** 2))[:, None] * PAL[(b + k) % P]

    # by SECTIONS: (draw, sparkle density per pixel per frame, corner strength, gain)
    plan = [(floor, 0.012, 1.0, 0.45), (mirror_ball, 0.03, 0.9, 1.0), (bursts, 0.02, 1.0, 0.7), (chase, 0.015, 0.9, 0.8),
            (squares, 0.012, 1.0, 0.6), (sweep, 0.025, 0.9, 0.9), (waves, 0.012, 0.9, 0.5), (stars, 0.04, 1.2, 0.8)]
    F = nframes(len(ORDER) * SECTION)
    out = np.zeros((F, N, 3))
    glint = np.zeros(N)
    gcol = np.zeros((N, 3))
    for f in range(F):
        t = f * DT
        si = int(t / SECTION)
        tl = t - si * SECTION
        fn, dens, cs, gain = plan[ORDER[si]]
        k = si * 3
        frame = gain * fn(tl, k)
        # corner stars: a shade per bar, a hit on every beat, a white flare on the downbeat of each bar
        bar = int(tl / BAR)
        cc = PAL[(bar + k + 2) % P] if bar % 2 else WHITE
        down = np.exp(-(tl % BAR) / 0.2)
        frame += perc(cs * (0.35 + 0.65 * pulse(tl, 0.18)) * corner)[:, None] * cc
        frame += perc(cs * 0.9 * down * corner)[:, None] * WHITE
        frame += perc(0.7 * ends * (0.5 + 0.5 * pulse(tl)))[:, None] * cc
        # mirror-ball glints, mostly silver
        glint *= 0.7
        new = rng.random(N) < dens
        glint[new] = 1.0
        gcol[new] = np.where(rng.random((new.sum(), 1)) < 0.85, WHITE if fn is stars else SILVER,
                             pal[rng.integers(0, P, new.sum())])
        frame += perc(glint)[:, None] * gcol
        frame = np.clip(frame, 0, 1)
        for idx in ports:                      # hold each port to its budget, dimming the whole port evenly
            level = frame[idx].mean()
            if level > PORT_BUDGET:
                frame[idx] *= PORT_BUDGET / level
        out[f] = frame
    return out


# ---------------------------------------------------------------------------------------------------------- music

# C minor, a bar each, every section: Cm9 Fm9 Bb13 Ebmaj9 Abmaj7 Dm7b5 G7b9 Cm9
PROG = ['Cm9', 'Fm9', 'Bb13', 'Ebmaj9', 'Abmaj7', 'Dm7b5', 'G7b9', 'Cm9']
ROOT = {'Cm9': 36, 'Fm9': 41, 'Bb13': 34, 'Ebmaj9': 39, 'Abmaj7': 44, 'Dm7b5': 38, 'G7b9': 43}
VOICE = {'Cm9': (63, 67, 70, 74), 'Fm9': (63, 67, 68, 72), 'Bb13': (62, 67, 68, 72), 'Ebmaj9': (62, 65, 67, 70),
         'Abmaj7': (60, 63, 67, 68), 'Dm7b5': (60, 62, 65, 68), 'G7b9': (59, 62, 65, 68)}
SCALE = [60, 62, 63, 65, 67, 68, 70, 72, 74, 75, 77, 79]           # C natural minor, for the string runs
# the hook: (bar, beat, note, beats), original
MELODY = [(0, 0, 67, 1.5), (0, 1.5, 70, .5), (0, 2, 74, 1.5), (0, 3.5, 72, .5),
          (1, 0, 72, 1), (1, 1, 68, .5), (1, 1.5, 67, 2.5),
          (2, 0, 65, .5), (2, .5, 67, .5), (2, 1, 70, 1), (2, 2, 74, 1.5), (2, 3.5, 72, .5),
          (3, 0, 70, 1), (3, 1, 67, 3),
          (4, 0, 67, 1.5), (4, 1.5, 70, .5), (4, 2, 75, 1.5), (4, 3.5, 74, .5),
          (5, 0, 72, 1), (5, 1, 68, .5), (5, 1.5, 65, 2.5),
          (6, 0, 68, .5), (6, .5, 68, .5), (6, 1, 72, 1), (6, 2, 71, 1), (6, 3, 74, 1),
          (7, 0, 72, 3)]
# the bass in each bar: (beat, interval over the root); the last eighth walks to the next root
BASSLINE = [(0, 0), (.5, 12), (1, 0), (1.5, 12), (2, 0), (2.5, 12), (3, 7), (3.5, 12)]
STABS = [(0, 0.22, 112), (1.5, 0.18, 96), (2.5, 0.18, 100), (3.5, 0.3, 108)]     # the horn section's push


def score(M, G):
    from pixelhome.audio import SR
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    spic = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bass = M.synth('Basses/Fingered')
    ep = M.synth('Keys/EP 2')
    kick = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum1/snare1_f_*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    crash_m = M.hits('Percussion/cymbal-crash1_mp*.wav')
    for name, gain, rev in (('drums', 0.55, 0.05), ('hats', 0.16, 0.04), ('bass', 0.5, 0.03), ('horns', 0.3, 0.16),
                            ('strings', 0.3, 0.4), ('lead', 0.34, 0.32), ('keys', 0.2, 0.18), ('harp', 0.3, 0.45)):
        M.bus(name, gain=gain, reverb=rev)

    hrng = np.random.default_rng(31)

    def hat(seconds, decay):
        n = int(seconds * SR)
        z = np.diff(hrng.standard_normal(n + 3), 3) * np.exp(-np.arange(n) / (decay * SR))
        return np.vstack([z, z]) * 0.12

    bass_notes, ep_notes = [], []
    kinds = [SECTIONS[i] for i in ORDER]
    for si, kind in enumerate(kinds):
        s0 = si * SECTION
        nxt = kinds[(si + 1) % len(kinds)]
        breakdown = kind == 'mirror_ball'
        big = kind in ('floor', 'stars', 'bursts')
        M.add('drums', (crash if big else crash_m).play(110 if big else 90), s0, 0.6 if big else 0.4)
        for bar in range(8):
            t0 = s0 + bar * BAR
            ch = PROG[bar]
            nroot = ROOT[PROG[(bar + 1) % 8]]
            # drums: four on the floor, backbeat, sixteenth hats with an open hat on every off-beat
            for b in range(4):
                tb = t0 + b * BEAT
                if not (breakdown and bar < 4):
                    M.add('drums', kick.play(100 if breakdown else 116), tb, 0.9)
                if b % 2 == 1 and not breakdown:
                    M.add('drums', snare.play(104), tb, 0.55)
                    M.add('drums', tamb.play(80), tb, 0.25, 0.2)
                for q, acc in enumerate((0.7, 0.35, 1.0, 0.35)):
                    if q == 2:
                        M.add('hats', hat(0.22, 0.07), tb + q * BEAT / 4, acc, 0.25)
                    elif not breakdown:
                        M.add('hats', hat(0.05, 0.010), tb + q * BEAT / 4, acc, -0.2)
            # bass: octaves with a fifth on four and a walk into the next chord
            if not (breakdown and bar < 4):
                for beat, iv in BASSLINE:
                    bass_notes.append((t0 + beat * BEAT, ROOT[ch] + iv, 104 if iv == 0 else 90, BEAT * 0.4))
                bass_notes.append((t0 + 3.75 * BEAT, nroot + (1 if nroot < ROOT[ch] else -1), 84, BEAT * 0.2))
            # Rhodes comping on the off-beats
            for off in (0.5, 2.5) if breakdown else (1.5, 3.5):
                for nn in VOICE[ch]:
                    ep_notes.append((t0 + off * BEAT, nn, 64 if breakdown else 76, BEAT * (1.2 if breakdown else 0.35)))
            # strings: a sustained chord, an octave apart at the top
            if kind in ('mirror_ball', 'chase', 'sweep', 'waves', 'stars'):
                for nn in VOICE[ch][1:]:
                    M.add('strings', vln.play(nn, 70, dur=BAR, release=0.4), t0, 0.5)
                M.add('strings', vln.play(VOICE[ch][-1] + 12, 62, dur=BAR, release=0.4), t0, 0.35)
            if kind in ('floor', 'squares'):            # spiccato eighths under the dance floor
                for e in range(8):
                    M.add('strings', spic.play(VOICE[ch][e % 2 + 2], 84 if e % 2 == 0 else 70), t0 + e * BEAT / 2, 0.5)
            # horn section stabs: the floor, the tiles, the bursts and the spotlights
            if kind in ('floor', 'squares', 'bursts', 'sweep'):
                for beat, dur, vel in STABS:
                    for nn in VOICE[ch][1:]:
                        M.add('horns', tpt.play(nn, vel, dur=dur * BEAT * 2, release=0.05), t0 + beat * BEAT, 0.5)
                    M.add('horns', tbn.play(ROOT[ch] + 12, vel, dur=dur * BEAT * 2, release=0.05), t0 + beat * BEAT, 0.6)
            # harp ripples up the chord with the mirror ball's beams
            if kind == 'mirror_ball' and bar % 2 == 0:
                for e in range(10):
                    nn = VOICE[ch][e % 4] + 12 * (e // 4)
                    M.add('harp', harp.play(nn, 70 + 3 * e), t0 + e * 0.07, 0.8, -0.5 + e * 0.1)
        # the hook: violins in octaves with a horn under them
        if kind in ('floor', 'waves', 'stars'):
            for bar, beat, nn, beats in MELODY:
                t = s0 + bar * BAR + beat * BEAT
                dur = beats * BEAT * 0.95
                M.add('lead', vln.play(nn + 12, 92, dur=dur, release=0.15), t, 0.55)
                M.add('lead', vln.play(nn, 92, dur=dur, release=0.15), t, 0.55)
                M.add('lead', horn.play(nn - 12, 84, dur=dur, release=0.15), t, 0.5)
        # a string run up into the next section
        if nxt in ('floor', 'stars', 'bursts', 'waves'):
            run = SCALE[:8] if nxt != 'stars' else SCALE[2:12]
            for e, nn in enumerate(run):
                M.add('strings', spic.play(nn + 12, 70 + 4 * e), s0 + SECTION - BEAT + e * BEAT / len(run), 0.5)
    M.add('bass', bass.render(bass_notes, M.seconds), 0.0, 1.0)
    M.add('keys', ep.render(ep_notes, M.seconds), 0.0, 1.0)
