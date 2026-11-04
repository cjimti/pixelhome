"""Star over the Porch: A point of light appears low behind the porch, twinkling. It rises and comes
forward until it hangs in the air over the middle of the U, and its diffraction spikes (four long,
four short, white at the core and fringed gold and blue at the edges) are cast out across the roof by
angle from the star's real 3-D position, so as the star turns each spike sweeps over wings, porch
sides and corners. Three travellers' lanterns set out from the two free ends and follow it along the
roofline to the porch; when they arrive the spikes fold down and the porch fills with light."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'CH04'
TITLE = 'Star over the Porch'
KIND = 'show'
DESCRIPTION = ('A star rises behind the porch and hangs over the house, its eight diffraction spikes sweeping '
               'the roof as it turns. Three lanterns follow it from the far ends to the porch.')
VOICEOVER = 'Follow the star: three lanterns are on their way to the porch.'

NIGHT = hexc('#060c30')
CORE = hexc('#fff4e0')
GOLD = hexc('#ffb030')
GLORY = hexc('#ffc860')
TRAVELLERS = [hexc('#ffb020'), hexc('#ff7010'), hexc('#ff4070')]

D = 64.0
SEED = 24
# the star: low and far behind the porch, rising and coming forward over the U (layout units, keyframes in s)
STAR_Z = [(2, -1150), (9, -1000), (22, -400), (46, -380), (50, -470)]
STAR_Y = [(2, 170), (9, 230), (22, 330), (46, 320), (50, 250)]
STAR_X = [(2, 0), (22, -20), (46, -20), (50, -20)]
BRIGHT = [(2, 0), (4, 0.6), (9, 0.75), (22, 1.0), (55, 1.0), (60, 0.5), (63.5, 0)]
PIN = [(2, 0), (4, 1), (11, 1), (14, 0)]                    # the pin-prick over the porch roof
TURN = [(9, 0), (46, 0.55), (52, 0.625)]                     # turns of the spikes
REACH = [(8, 0), (20, 1.0), (46, 1.0), (49, 1.25), (54, 0.35), (60, 0)]
GLORY_KEYS = [(47.5, 0), (49.5, 1), (55, 0.8), (63.5, 0)]   # the porch fills with light


def star_at(t):
    return np.array([keys(t, STAR_X), keys(t, STAR_Y), keys(t, STAR_Z)])


def theta_at(t):
    """Angle of the first long spike, seen from above."""
    return 0.25 * np.pi + 2 * np.pi * keys(t, TURN) + 0.02 * np.sin(t * 0.7)


def porch_centre(G):
    pf = G.seg['Porch Front']
    return G.pd[pf[len(pf) // 2]]


def trips(G):
    """The three lanterns: (from pd, to pd, set out, arrive): two from the back of Side, one from the end of Right."""
    c = porch_centre(G)
    return [(0.0, c - 26, 14.0, 47.0), (0.0, c - 52, 16.5, 47.5), (G.length, c + 30, 18.0, 47.0)]


def lantern_at(trip, t):
    """Where a lantern is on the path at time t: it eases off and walks on steadily."""
    a0, a1, t0, t1 = trip
    u = smoothstep(t0, t1, t) * 0.25 + 0.75 * np.clip((t - t0) / (t1 - t0), 0, 1)
    return lerp(a0, a1, u)


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    P = G.pos
    x = G.pd
    scint = Flicker(rng, 3, 2.0, 6.0)
    sway = Flicker(rng, 3, 0.8, 1.6)
    fringe = colormap([(0, (1.0, 0.95, 0.85)), (0.5, (1.0, 0.62, 0.18)), (0.85, (0.55, 0.45, 0.6)),
                       (1.2, (0.15, 0.3, 1.0)), (2.0, (0.1, 0.2, 0.8))])
    porch_dist = np.abs(x - porch_centre(G))
    walks = trips(G)

    for f in range(F):
        t = f * DT
        fr = out[f]
        sky = keys(t, [(0, 0), (2, 0.07), (58, 0.07), (63.5, 0)])
        fr += light(NIGHT, np.full(G.N, sky))

        # the star's position: low and far behind the porch, rising and coming forward over the U
        s3 = star_at(t)
        rel = P - s3
        rxz = np.hypot(rel[:, 0], rel[:, 2])
        d3 = np.linalg.norm(rel, axis=1)
        ang = np.arctan2(rel[:, 2], rel[:, 0])
        bright = keys(t, BRIGHT)
        tw = 1 + 0.12 * scint(t)[0]

        # the pin-prick: before the spikes can reach, the star is a point seen just over the porch roof
        if t < 14:
            pin = keys(t, PIN)
            fr += light(CORE, 0.85 * pin * tw * np.exp(-(porch_dist / 4.5) ** 2) * (G.seg_of == 'Porch Front'))
            fr += light(hexc('#a0b8ff'), 0.25 * pin * np.exp(-(porch_dist / 18) ** 2) * (G.seg_of == 'Porch Front'))

        # diffraction spikes cast by angle from the star
        theta = theta_at(t)
        reach = keys(t, REACH)
        spike = np.zeros(G.N)
        off = np.full(G.N, 9.0)
        for k in range(8):
            main = k % 2 == 0
            w = (0.065 if main else 0.04)
            a = wrap(ang - theta - k * np.pi / 4)
            length = (900 if main else 420) * reach
            amp = (1.0 if main else 0.55) * np.exp(-(rxz / max(length, 1)) ** 2)
            s = amp * np.exp(-(a / w) ** 2)
            better = s > spike
            spike = np.where(better, s, spike)
            off = np.where(better, np.abs(a) / w, off)
        I = bright * tw * spike * (0.4 + 0.6 * np.exp(-rxz / 700))
        fr += perc(I)[:, None] * fringe(off)

        # halo: the star's glow on the roof nearest to it, by true 3-D distance
        halo = bright * 0.5 * np.exp(-(d3 / 300) ** 2) * smoothstep(8, 18, t)
        fr += light(GOLD, halo)

        # the travellers' lanterns
        for j, (a0, a1, t0, t1) in enumerate(walks):
            if t < t0 - 1:
                continue
            p = lantern_at(walks[j], t)
            gait = 1 + 0.18 * sway(t)[j]
            e = keys(t, [(t0 - 1, 0), (t0, 0.6), (t1, 0.6), (t1 + 1.5, 0.35), (58, 0.35), (63, 0)])
            bob = 1.5 * np.sin(2 * np.pi * 1.1 * t + j)
            fr += light(TRAVELLERS[j], e * gait * np.exp(-((x - p - bob) / 5) ** 2))
            fr += light(TRAVELLERS[j], 0.35 * e * np.exp(-((x - p) / 22) ** 2))

        # arrival: the porch fills with light that spills round the corners and along the wings
        g = keys(t, GLORY_KEYS)
        if g > 0:
            spread = 60 + 900 * smoothstep(47.5, 56, t)
            fr += light(GLORY, 0.55 * g * np.exp(-(porch_dist / spread) ** 2) *
                        (0.85 + 0.15 * np.cos(porch_dist / 30 - 3 * t)))
    return out


# ---- music: a travellers' march in D, 6/8 ----
# The star appears to a bell tree and twinkles on a celesta over the porch; strings swell as its spikes reach out,
# and every time a spike sweeps over a corner or a free end of the roof a glockenspiel (long spike) or celesta
# (short spike) rings there, pitched from the chord by how far across the house it is. Each lantern brings its own
# woodwind and little bell, and they move across the speakers as the lanterns walk: the clarinet and the bassoon from
# the back of Side, the oboe from the end of Right. Bar 30 is the arrival: horns, trumpet, cymbal and harp as the
# porch fills with light; the spikes fold to a falling harp, and the march slows to a hymn as the star fades.

T0 = 2.0                    # the star appears on the first downbeat
BAR = 45.5 / 30             # 6/8 at 79 dotted-quarter beats a minute; bar 30 lands on the arrival at 47.5 s
EIGHTH = BAR / 6
ARRIVE = 30
CHORDS = ('D D D D G D Bm A '               # 0-7    the star appears, its spikes reach out
          'D D G D Bm Em A A '              # 8-15   the clarinet's lantern sets out; the others join
          'D D G Em Bm G A A7 '             # 16-23  the oboe takes the tune
          'D G Em C Asus A7 '               # 24-29  all three close in on the porch
          'D D G D Bm G Em7 A7 D D D').split()   # 30-40  arrival; the spikes fold; the star fades
TONES = {'D': (2, 6, 9), 'G': (7, 11, 2), 'Bm': (11, 2, 6), 'A': (9, 1, 4), 'Em': (4, 7, 11), 'A7': (9, 1, 4, 7),
         'C': (0, 4, 7), 'Asus': (9, 2, 4), 'Em7': (4, 7, 11, 2)}
# the tune, (eighth, note, eighths) per bar
TUNE = {
    8: [(0, 'F#4', 2), (2, 'A4', 1), (3, 'D5', 3)], 9: [(0, 'C#5', 1), (1, 'B4', 1), (2, 'A4', 1), (3, 'F#4', 3)],
    10: [(0, 'G4', 2), (2, 'B4', 1), (3, 'D5', 2), (5, 'E5', 1)], 11: [(0, 'D5', 3), (3, 'A4', 3)],
    12: [(0, 'B4', 2), (2, 'D5', 1), (3, 'B4', 2), (5, 'A4', 1)], 13: [(0, 'G4', 2), (2, 'B4', 1), (3, 'E5', 3)],
    14: [(0, 'C#5', 1), (1, 'D5', 1), (2, 'C#5', 1), (3, 'B4', 2), (5, 'A4', 1)], 15: [(0, 'A4', 6)],
    16: [(0, 'F#4', 2), (2, 'A4', 1), (3, 'D5', 3)], 17: [(0, 'E5', 1), (1, 'D5', 1), (2, 'C#5', 1), (3, 'D5', 3)],
    18: [(0, 'B4', 2), (2, 'G4', 1), (3, 'B4', 2), (5, 'D5', 1)], 19: [(0, 'E5', 3), (3, 'B4', 3)],
    20: [(0, 'D5', 2), (2, 'C#5', 1), (3, 'B4', 2), (5, 'F#4', 1)], 21: [(0, 'G4', 2), (2, 'A4', 1), (3, 'B4', 2),
                                                                      (5, 'D5', 1)],
    22: [(0, 'C#5', 3), (3, 'E5', 2), (5, 'C#5', 1)], 23: [(0, 'A4', 3), (3, 'G4', 2), (5, 'E4', 1)],
    24: [(0, 'A4', 2), (2, 'D5', 1), (3, 'D5', 2), (5, 'E5', 1)], 25: [(0, 'D5', 3), (3, 'B4', 3)],
    26: [(0, 'B4', 2), (2, 'E5', 1), (3, 'E5', 2), (5, 'D5', 1)], 27: [(0, 'E5', 3), (3, 'C5', 3)],
    28: [(0, 'D5', 3), (3, 'D5', 2), (5, 'E5', 1)], 29: [(0, 'C#5', 2), (2, 'B4', 1), (3, 'A4', 2), (5, 'C#5', 1)],
    30: [(0, 'D5', 12)],
    32: [(0, 'B4', 3), (3, 'D5', 3)], 33: [(0, 'A4', 3), (3, 'F#4', 3)],
    34: [(0, 'F#4', 2), (2, 'A4', 1), (3, 'D5', 3)], 35: [(0, 'D5', 2), (2, 'B4', 1), (3, 'G4', 3)],
    36: [(0, 'G4', 3), (3, 'B4', 2), (5, 'D5', 1)], 37: [(0, 'E5', 3), (3, 'C#5', 3)], 38: [(0, 'D5', 14)],
}
TWINKLE = ('A5', 'F#5', 'D6', 'E6', 'C#6', 'A5')     # the celesta's figure over the pin-prick, one note an eighth
CORNERS = (0, 80, 178, 260, 331, 380, 500)            # path indices of the free ends and the corners


def at(bar, eighth=0.0):
    return T0 + bar * BAR + eighth * EIGHTH


def crossings(G):
    """When a spike sweeps over a corner or free end: [(time, path index, long spike?, strength)], frame by frame
    from the same star, angle and reach render() uses."""
    pts = np.array([G.path[i] for i in CORNERS])
    P = G.pos[pts]
    prev, ev = None, []
    for f in range(nframes(D)):
        t = f * DT
        rel = P - star_at(t)
        ang = np.arctan2(rel[:, 2], rel[:, 0])
        rxz = np.hypot(rel[:, 0], rel[:, 2])
        reach, br = keys(t, REACH), keys(t, BRIGHT)
        a = np.array([wrap(ang - theta_at(t) - k * np.pi / 4) for k in range(8)])
        if prev is not None:
            for k in range(8):
                main = k % 2 == 0
                amp = (1.0 if main else 0.55) * np.exp(-(rxz / max((900 if main else 420) * reach, 1)) ** 2) * br
                hit = (np.sign(a[k]) != np.sign(prev[k])) & (np.abs(a[k] - prev[k]) < 1) & (amp > 0.3)
                ev += [(t, CORNERS[i], main, float(amp[i])) for i in np.flatnonzero(hit)]
        prev = a
    return ev


def score(M, G):
    from pixelhome.audio import note
    n = note
    walks = trips(G)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    cel = M.synth('Plucks/Fantasy Bell')
    belltree = M.hits('Percussion/BellTree_Stroke*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_slowAsc1.wav')
    sleigh = M.hits('Miscellania Raw/Misc 2/sleighbell1_hit_[123].wav')
    sleigh2 = M.hits('Miscellania Raw/Misc 2/sleighbell2_hit_[12].wav')
    shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake1.wav')
    fing = M.hits('VSCO 1 Percussion/varMetal/various/Fing_Cymb.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Median_v1.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    timp = M.hits('Percussion/Timpani/Timpani3_Hit_v3*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v3*.wav')

    for name, gain, rev in (('tune', 0.42, 0.25), ('wind', 0.3, 0.25), ('strings', 0.26, 0.3), ('bass', 0.4, 0.12),
                            ('brass', 0.3, 0.25), ('bells', 0.55, 0.35), ('perc', 0.38, 0.25), ('harp', 0.3, 0.3)):
        M.bus(name, gain=0.6 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    centre = porch_centre(G)

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, G.length), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def chord(bar):
        return CHORDS[min(max(int(bar), 0), len(CHORDS) - 1)]

    def voiced(c, lo, hi):
        return [m for m in range(n(lo), n(hi) + 1) if m % 12 in TONES[c]]

    def below(m, c):                         # the chord tone under a melody note: the second voice
        return max(x for x in range(m - 9, m - 2) if x % 12 in TONES[c]) if any(
            x % 12 in TONES[c] for x in range(m - 9, m - 2)) else m - 12

    def tune(inst, bars, bus, vel, pan, gain=1.0, second=False, shift=0):
        for b in bars:
            for e, m, ln in TUNE.get(b, ()):
                t = at(b, e)
                mm = n(m) + shift
                if second:
                    mm = below(n(m), chord(b + e / 6))
                p = pan(t) if callable(pan) else pan
                M.add(bus, inst.play(mm, vel, dur=ln * EIGHTH * 0.95, release=0.25), t, gain, p)

    def lantern(j):
        return lambda t: pan_at(lantern_at(walks[j], t))

    # ---- strings: a chord a bar from the sky's first light to the end ----
    level = {b: 1.0 for b in range(len(CHORDS))}
    for b in range(4, 8):
        level[b] = 0.7 + 0.1 * (b - 4)
    for b in range(len(CHORDS)):
        c = chord(b)
        if b > 0 and c == chord(b - 1) and b not in (8, 16, 24, ARRIVE, 38):
            continue
        ln = 1
        while b + ln < len(CHORDS) and chord(b + ln) == c and b + ln not in (8, 16, 24, ARRIVE, 38):
            ln += 1
        t = at(b) if b else 0.3
        dur = at(b + ln) - t + (2.0 if b + ln >= len(CHORDS) else 0.15)
        v = 70 if b < 8 else (82 if b < ARRIVE else 92)
        if b >= 32:
            v = 78
        if b == 0:
            v = 55
        lo = voiced(c, 'A3', 'A4')[:3]
        for m in lo:
            M.add('strings', vla.play(m, v, dur=dur, release=0.6), t, 0.6 * level[b], -0.2)
        for m in voiced(c, 'D4', 'D5')[1:3]:
            M.add('strings', vln.play(m, v, dur=dur, release=0.6), t, 0.55 * level[b], 0.25)
        root = [m for m in range(n('D2'), n('D3')) if m % 12 == TONES[c][0]][0]
        M.add('strings', cello.play(root, v, dur=dur, release=0.6), t, 0.8 * level[b], 0.0)
    # the spikes reach out (8-20 s): a tremolo swell, and wind chimes climbing
    for m in voiced('G', 'G4', 'D5'):
        r = trem.play(m, 80, dur=at(8) - at(4), release=0.4)
        M.add('strings', r * np.linspace(0.15, 1, r.shape[1]) ** 2, at(4), 0.5, 0.3)
    M.add('bells', chimes.play(90), 8.0, 0.6, pan_at(centre))

    # ---- the star appears, and twinkles over the porch until the spikes take over ----
    M.add('bells', belltree.play(100), T0 - 0.15, 0.8, pan_at(centre))
    M.add('bells', glock.play(n('D6'), 80), T0, 0.7, pan_at(centre))
    notes = []
    for b in range(0, 8):
        fade = keys(at(b), PIN)
        for e, m in enumerate(TWINKLE):
            if (b + e) % 2 == 0 or e in (0, 2):
                notes.append((at(b, e), n(m) - 12 * (e == 5 and b % 2), int(30 + 50 * fade), EIGHTH * 1.5))
    notes = [x for x in notes if x[2] > 34]
    M.add('bells', cel.render([(t - T0, m, v, d) for t, m, v, d in notes], at(8) - T0 + 3), T0, 0.5, pan_at(centre))
    for b in range(0, 8):                    # the harp rocks under it
        c = chord(b)
        tones = voiced(c, 'D3', 'A4')
        for e in range(6):
            m = tones[[0, 2, 4, 3, 2, 1][e] % len(tones)]
            M.add('harp', harp.play(m, 60 + 4 * e % 3), at(b, e), 0.55, -0.1)

    # ---- a spike sweeps over a corner: a bell there, from the chord, higher the farther right ----
    for t, pi, main, amp in crossings(G):
        c = chord((t - T0) / BAR)
        x = (G.pos[G.path[pi], 0] - x0) / (x1 - x0)
        pool = voiced(c, 'G5', 'F#6') if main else voiced(c, 'D5', 'D6')
        m = pool[min(len(pool) - 1, int(x * len(pool)))]
        p = pan_at(G.pd[G.path[pi]])
        if main:
            M.add('bells', glock.play(m, int(70 + 40 * min(amp, 1))), t, 0.8, p)
            M.add('perc', tri.play(int(60 + 40 * min(amp, 1))), t, 0.25, p)
        else:
            M.add('bells', cel.render([(0.0, m, int(60 + 50 * amp), 0.4)], 3.0), t, 0.45, p)

    # ---- the travellers: each lantern a woodwind and a bell, walking ----
    tune(clar, range(8, 16), 'tune', 88, lantern(0))                     # the first sets out from Side
    tune(oboe, range(12, 16), 'wind', 72, lantern(2), 0.7, second=True)  # the one from Right answers under it
    tune(oboe, range(16, 24), 'tune', 90, lantern(2))                    # and takes the tune
    tune(clar, range(16, 24), 'wind', 74, lantern(0), 0.75, second=True)
    for b in range(8, ARRIVE):               # the bassoon's lantern walks in dotted quarters on the bass
        c = chord(b)
        root = [m for m in range(n('D2'), n('D3')) if m % 12 == TONES[c][0]][0]
        fifth = [m for m in range(n('A2'), n('A3')) if m % 12 == TONES[c][2 if len(TONES[c]) > 2 else 1]][0]
        for e, m in ((0, root), (3, fifth)):
            t = at(b, e)
            if t >= walks[1][2] - 0.2:
                M.add('wind', bsn.play(m + 12, 80, dur=EIGHTH * 2.6, release=0.15), t, 0.75, lantern(1)(t))
            M.add('bass', cb.play(m, 90 if e == 0 else 76, dur=EIGHTH * 2.5), t, 0.9, 0.0)
            for k in voiced(c, 'D4', 'B4')[:3]:
                M.add('strings', pizz.play(k, 66), at(b, e + 2), 0.18, 0.3)
    for j, (inst, beats) in enumerate(((sleigh, (0, 3)), (fing, (0,)), (sleigh2, (3,)))):
        a0, a1, t0, t1 = walks[j]
        for b in range(ARRIVE):
            for e in beats:
                t = at(b, e)
                if t0 - 0.1 <= t < t1:
                    M.add('perc', inst.play(int(M.rng.integers(70, 96))), t, 0.35 if j != 1 else 0.25,
                          lantern(j)(t))
        M.add('perc', fing.play(100), t1, 0.5, pan_at(a1))              # it reaches the porch
    tune(flute, range(24, ARRIVE + 1), 'tune', 90, 0.0, 0.8)            # all three close in on the porch
    tune(oboe, range(24, ARRIVE), 'wind', 84, pan_at(centre + 30), 0.6)
    tune(clar, range(24, ARRIVE), 'wind', 80, pan_at(centre - 30), 0.6, second=True)
    for b in range(24, ARRIVE):
        for m in voiced(chord(b), 'A3', 'F#4')[:3]:
            M.add('brass', horn.play(m, 70 + 3 * (b - 24), dur=BAR * 0.95, release=0.3), at(b), 0.5, 0.0)

    # ---- the arrival: the porch fills with light ----
    r = swell.play(100)
    M.add('perc', r, at(ARRIVE) - r.shape[1] / 48000, 0.4, 0.0)
    r = troll.play(90, dur=at(ARRIVE) - at(28))
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, at(28), 0.6, 0.0)
    M.add('perc', crash.play(110), at(ARRIVE), 0.5, 0.0)
    M.add('perc', timp.play(110, pitch=-2), at(ARRIVE), 0.7, 0.0)
    M.add('bells', belltree.play(110), at(ARRIVE), 0.7, pan_at(centre))
    M.add('perc', shake.play(100), at(ARRIVE), 0.5, pan_at(centre))
    tune(tpt, [ARRIVE], 'brass', 96, 0.0, 0.6)
    for m in voiced('D', 'D3', 'D4'):
        M.add('brass', horn.play(m, 96, dur=2 * BAR, release=0.8), at(ARRIVE), 0.6, 0.0)
    for k, m in enumerate(voiced('D', 'D3', 'A5')):                       # harp sweeps up
        M.add('harp', harp.play(m, 90), at(ARRIVE) + 0.045 * k, 0.6, -0.6 + 0.08 * k)
    # the spikes fold down (49-54 s): the harp falls, the celesta follows
    for k, m in enumerate(voiced('D', 'D3', 'A5')[::-1]):
        M.add('harp', harp.play(m, 80), 49.6 + 0.06 * k, 0.5, 0.6 - 0.08 * k)
    for k, m in enumerate(voiced('G', 'D5', 'D6')[::-1]):
        M.add('bells', cel.render([(0.0, m, 70 - 6 * k, 0.6)], 3.0), 51.0 + 0.5 * k, 0.4, 0.4 - 0.15 * k)

    # ---- the hymn as the star fades ----
    tune(oboe, range(32, 39), 'tune', 78, pan_at(centre))
    tune(flute, range(32, 39), 'wind', 64, pan_at(centre), 0.5, second=True)
    for b in range(32, 39):
        for m in voiced(chord(b), 'A3', 'F#4')[:3]:
            M.add('brass', horn.play(m, 64, dur=BAR * (3 if b == 38 else 0.98), release=0.8), at(b), 0.45, 0.0)
        root = [m for m in range(n('D2'), n('D3')) if m % 12 == TONES[chord(b)][0]][0]
        M.add('bass', cb.play(root, 76, dur=BAR), at(b), 0.8, 0.0)
        for e in range(6):
            tones = voiced(chord(b), 'D3', 'A4')
            M.add('harp', harp.play(tones[[0, 2, 4, 3, 2, 1][e] % len(tones)], 56), at(b, e), 0.45, -0.1)
    M.add('bells', glock.play(n('D6'), 76), at(38), 0.7, pan_at(centre))
    M.add('bells', belltree.play(80), at(38) + 0.1, 0.5, pan_at(centre))
    M.add('perc', timp.play(80, pitch=-2), at(38), 0.4, 0.0)
