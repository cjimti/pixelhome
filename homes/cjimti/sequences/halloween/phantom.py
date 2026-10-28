"""Phantom: True 3-D: a ghost flies around (and into) the house, searchlights sweep from the street,
scanning planes reveal the depth of the roof, three spirits spiral in and burst."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes, catmull_closed

CODE = 'SC3'
TITLE = 'Phantom'
KIND = 'show'
DESCRIPTION = 'A ghost flies in and out of the porch, searchlights sweep from the street, scanning planes reveal the depth of the roof.'
VOICEOVER = "Something drifts through the porch after dark. Sweep the lights. Search the roof. It's here somewhere."

ORANGE = hexc('#ff3000')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')
GHOST = hexc('#80ffd0')
ICE = hexc('#c0d8ff')
RED = hexc('#ff0000')


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    D = 70.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    xz = P[:, [0, 2]]
    fog = Flicker(rng, G.N, 0.05, 0.3)
    route = np.array([(-700, 150, -80), (-400, 150, -100), (-250, 150, -300), (-20, 150, -510), (110, 150, -400),
                      (230, 150, -130), (550, 150, -120), (720, 150, -230), (320, 150, -40), (-300, 150, -40),
                      (-660, 150, -300), (-640, 150, -660), (-720, 150, -260)], float)
    trail = np.zeros(G.N)
    lights = [np.array([-350.0, 700.0]), np.array([350.0, 700.0])]
    centre = np.array([0.0, 150.0, -390.0])
    spirits = [(GHOST, 0.0), (hexc('#b000ff'), 2 * np.pi / 3), (hexc('#ff4000'), 4 * np.pi / 3)]

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        bg = keys(t, [(0, 0), (2, 0.1), (24, 0.1), (25, 0.04), (55, 0.04), (56, 0.1), (66, 0.1), (70, 0)])
        fr += light(PURPLE, bg * (0.7 + 0.3 * fog(t)))

        if t < 25.5:                                         # the ghost
            g = catmull_closed(route, t / 25.0)
            d = np.linalg.norm(P - g, axis=1)
            cur = np.exp(-(d / 120) ** 2) * keys(t, [(0, 0), (1.5, 1), (24, 1), (25.5, 0)])
            trail = np.maximum(trail * 0.94, cur * 0.6)
            fr += light(GHOST, np.maximum(cur, trail))
        elif t < 40:                                         # searchlights from the street
            k = keys(t, [(25.5, 0), (26.5, 1), (39, 1), (40, 0)])
            for j, s in enumerate(lights):
                ang = np.arctan2(xz[:, 0] - s[0], s[1] - xz[:, 1])
                sweep = 0.75 * np.sin(2 * np.pi * (t - 25.5) / (6.5 + j * 1.7) + j * 2.1)
                fr += light(ICE, k * np.exp(-((ang - sweep) / 0.035) ** 2))
        elif t < 55:                                         # scanning planes
            lt = t - 40
            for t0, dur, axis, a, b, col in [(0, 4, 2, -100, -680, hexc('#20ff60')), (4, 4, 2, -680, -100, RED),
                                             (8.5, 3, 0, -640, 670, hexc('#9000ff')),
                                             (11.5, 3, 0, 670, -640, ORANGE)]:
                if t0 <= lt < t0 + dur + 0.8:
                    plane = lerp(a, b, smoothstep(0, 1, (lt - t0) / dur))
                    sgn = np.sign(b - a)
                    behind = (plane - P[:, axis]) * sgn
                    band = np.exp(-(behind / 22) ** 2) + np.where(behind > 0, 0.35 * np.exp(-behind / 90), 0)
                    fr += light(col, band * min(1, (t0 + dur + 0.8 - lt) / 0.8))
        else:                                                # three spirits spiral in
            lt = t - 55
            if lt < 11:
                r = lerp(750, 0, smoothstep(0, 11, lt) ** 0.8)
                spin = 0.6 * lt + 0.06 * lt ** 2.4
                for col, ph in spirits:
                    a = spin * 2 * np.pi / 3 + ph
                    c = centre + np.array([r * np.sin(a), 0, r * np.cos(a)])
                    d = np.linalg.norm(P - c, axis=1)
                    fr += light(col, 0.9 * np.exp(-(d / 100) ** 2))
            else:
                tb = lt - 11
                d = np.linalg.norm(P - centre, axis=1)
                fr += light(WHITE, np.exp(-((d - tb * 1300) / 90) ** 2) * np.exp(-tb / 1.2) + np.exp(-tb / 0.2))
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A theremin ghost story in C minor on a 120 BPM grid. The ghost IS the theremin: it sings a tune whose notes sit on
# the ghost's route waypoints and glide along the same spline, panned to where the ghost is and swelling as it
# brushes the roof. Under the searchlights the band drops to a tremolo drone and a heartbeat, and each beam whistles,
# rising and falling with its own sweep, swelling when it lands on the house and chiming when it flares down a run.
# The scanning planes run on a pulsing bass with a sonar tone that steps through the chord as the plane moves, and
# a bell and zap where a plane sweeps over a whole run at once. Three spirits spiral in on a choir with a rising
# harp under them; the burst is a gong, and the theremin sighs at the end. Everything is read off render()'s
# constants (copied below where render keeps them local) and panned to where it happens, as seen from the street.

ROUTE = np.array([(-700, 150, -80), (-400, 150, -100), (-250, 150, -300), (-20, 150, -510), (110, 150, -400),
                  (230, 150, -130), (550, 150, -120), (720, 150, -230), (320, 150, -40), (-300, 150, -40),
                  (-660, 150, -300), (-640, 150, -660), (-720, 150, -260)], float)   # render()'s ghost route
TUNE = [67, 72, 75, 79, 77, 72, 74, 77, 74, 75, 79, 84, 75]   # the theremin's note at each waypoint
LIGHTS = [(-350.0, 700.0), (350.0, 700.0)]                   # searchlights; sweep period 6.5 + 1.7 j, phase 2.1 j
PLANES = [(40.0, 4, 2, -100, -680, 'Cm'), (44.0, 4, 2, -680, -100, 'Ab'), (48.5, 3, 0, -640, 670, 'Fm'),
          (51.5, 3, 0, 670, -640, 'G')]                      # (start, duration, axis, from, to, chord)
CENTRE = np.array([0.0, 150.0, -390.0])
T_BURST = 66.0
PAD = {'Cm': (48, 55, 63, 67), 'Ab': (44, 56, 60, 63), 'Fm': (41, 56, 60, 65), 'G': (43, 55, 59, 62),
       'Db': (49, 56, 61, 65)}
ROOT = {'Cm': 36, 'Ab': 32, 'Fm': 29, 'G': 31, 'Db': 37}
GHOST_PROG = [(0, 'Cm'), (4, 'Ab'), (8, 'Fm'), (12, 'G'), (16, 'Cm'), (20, 'Ab'), (24, 'G')]
SPIRIT_PROG = [(55, 'Ab'), (58, 'Fm'), (61, 'Db'), (63, 'G')]
SPIRIT_NOTES = {'Ab': (72, 68, 63), 'Fm': (72, 68, 65), 'Db': (73, 68, 65), 'G': (74, 71, 67)}  # ghost, purple, orange


def score(M, G):
    from pixelhome.audio import SR, note
    n = note
    D = M.seconds
    ts = np.arange(M.n) / SR
    F = nframes(D)
    tf = np.arange(F) * DT
    P = G.pos
    xz = P[:, [0, 2]]
    x0, x1 = P[:, 0].min(), P[:, 0].max()

    def pan_x(x):                           # layout x -> left/right as seen from the street
        return np.clip(0.85 * (2 * (np.asarray(x, float) - x0) / (x1 - x0) - 1), -0.95, 0.95)

    def up(v):                              # per-frame curve -> per-sample
        return np.interp(ts, tf, v)

    def put(bus, mono, pan_f, gain=1.0):    # full-length mono with a moving pan (per-frame)
        a = (up(pan_f) + 1) * np.pi / 4
        M.add(bus, np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2), 0.0, gain)

    def mono_at(sig, t0):                   # a rendered stereo clip placed into a full-length mono buffer
        out = np.zeros(M.n)
        s = int(t0 * SR)
        m = sig.mean(0)[:M.n - s]
        out[s:s + len(m)] = m
        return out

    def tone(midi, amp, partials=(1.0,)):   # per-sample pitch and amplitude -> sine stack
        ph = 2 * np.pi * np.cumsum(440 * 2 ** ((midi - 69) / 12)) / SR
        return amp * sum(a * np.sin((k + 1) * ph) for k, a in enumerate(partials))

    def band_noise(lo, hi, seed):
        X = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, M.n))
        f = np.fft.rfftfreq(M.n, 1 / SR)
        X *= np.exp(-((np.log(f + 1) - np.log(np.sqrt(lo * hi))) / (0.5 * np.log(hi / lo))) ** 2)
        y = np.fft.irfft(X, M.n)
        return y / (np.abs(y).max() + 1e-9)

    def chord_at(t, prog):
        return [c for t0, c in prog if t0 <= t][-1]

    seg_x = {k: float(P[G.seg[k], 0].mean()) for k in G.seg}

    harp = M.sampler('Strings/Harp/*.wav')
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav')
    btrem = M.sampler('Strings/Solo Contrabass/Trem/*.wav')
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    heart = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_m*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_fff*.wav')
    cresc_s = M.hits('Percussion/susCymb1-cresc-Short_v1.wav')
    cresc_l = M.hits('Percussion/susCymb1-cresc-Long_v1.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3*.wav')
    zap = M.hits('Percussion/zap*.wav')
    shaker = M.hits('VSCO 1 Percussion/varWood/maraca[1-5].wav')
    bell = M.synth('Plucks/Bell 1')
    chime = M.synth('Plucks/Fantasy Bell')

    for name, gain, rev in (('theremin', 0.065, 0.35), ('pad', 0.26, 0.3), ('harp', 0.2, 0.3), ('bass', 0.22, 0.05),
                            ('strings', 0.18, 0.25), ('drums', 0.5, 0.15), ('bells', 0.3, 0.4), ('beams', 0.05, 0.4),
                            ('scan', 0.3, 0.2), ('choir', 0.6, 0.35), ('fx', 0.3, 0.3), ('wind', 0.13, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    pad, sub = [], []
    th_pitch, th_amp, th_pan = np.zeros(F), np.zeros(F), np.zeros(F)
    th_vib = np.full(F, 0.15)

    # ---- fog: a low wind that follows render()'s background level all show ----
    bg = np.array([keys(t, [(0, 0), (2, 0.1), (24, 0.1), (25, 0.04), (55, 0.04), (56, 0.1), (66, 0.1), (70, 0)])
                   for t in tf])
    wobble = 0.7 + 0.3 * np.sin(2 * np.pi * ts / 7.3) * np.sin(2 * np.pi * ts / 3.1)
    M.add('wind', np.vstack([band_noise(80, 500, 1), band_noise(80, 500, 2)]) * up(bg / 0.1) * wobble, 0.0)

    # ---- 0-25.5: the ghost flies the route; the theremin sings one note per waypoint, gliding on its spline ----
    K = len(ROUTE)
    trail = np.zeros(G.N)
    for f in range(F):
        t = tf[f]
        if t >= 25.5:
            break
        g = catmull_closed(ROUTE, t / 25.0)
        cur = np.exp(-(np.linalg.norm(P - g, axis=1) / 120) ** 2) * keys(t, [(0, 0), (1.5, 1), (24, 1), (25.5, 0)])
        trail = np.maximum(trail * 0.94, cur * 0.6)
        lit = float(np.maximum(cur, trail).max())       # how bright the ghost is on the roof
        s = (t / 25.0 % 1) * K
        i, u = int(s), s - int(s)
        w = float(smoothstep(0.3, 0.8, u))              # hold the note round each waypoint, glide between
        p0, p1, p2, p3 = (TUNE[(i + k) % K] for k in (-1, 0, 1, 2))
        th_pitch[f] = 0.5 * ((2 * p1) + (-p0 + p2) * w + (2 * p0 - 5 * p1 + 4 * p2 - p3) * w ** 2 +
                             (-p0 + 3 * p1 - 3 * p2 + p3) * w ** 3)
        th_amp[f] = keys(t, [(0, 0), (1.5, 1), (24, 1), (25.5, 0)]) * (0.2 + 0.8 * lit)
        th_pan[f] = pan_x(g[0])
        th_vib[f] = 0.1 + 0.3 * (1 - 4 * w * (1 - w))   # vibrato blooms on held notes
    for t0, c in GHOST_PROG:
        d = 4.0 if t0 < 24 else 1.8
        pad += [(t0, m, 62, d) for m in PAD[c]]
        sub.append((t0, ROOT[c], 80, d))
        for b in range(int(d / 0.5)):                   # harp walks the chord in quarter notes
            m = PAD[c][[0, 1, 2, 1, 3, 2, 1, 2][b % 8]] - (12 if b % 8 == 0 else 0)
            M.add('harp', harp.play(m, 60 + 14 * (b % 2 == 0)), t0 + 0.5 * b, 0.8, -0.3)

    # ---- 25.5-40: searchlights from the street; tremolo drone, a heartbeat, each beam whistles its sweep ----
    M.add('strings', btrem.play(n('C1'), 90), 25.5, 0.9)
    M.add('strings', btrem.play(n('C1'), 90), 32.5, 0.9)
    for t0, m, d in ((25.5, 'C3', 8.0), (33.5, 'Db3', 4.0), (37.5, 'B2', 2.5)):
        M.add('strings', ctrem.play(n(m), 80, dur=d), t0, 0.8, -0.2)
        M.add('strings', ctrem.play(n(m) + 7, 70, dur=d), t0, 0.5, 0.2)
    for i, t in enumerate(np.arange(26.0, 39.5, 1.0)):  # lub-dub, building
        v = 60 + 3 * i
        M.add('drums', heart.play(v), t, 0.6)
        M.add('drums', heart.play(v - 15), t + 0.25, 0.45)
    M.add('drums', cresc_s.play(90, dur=1.45), 40.0 - 1.4, 0.6)
    air = [band_noise(1500, 6000, 10), band_noise(1500, 6000, 11)]
    for j, (sx, sz) in enumerate(LIGHTS):
        ang = np.arctan2(xz[:, 0] - sx, sz - xz[:, 1])
        lit, xm, sw = np.zeros(F), np.zeros(F), np.zeros(F)
        for f in range(F):
            t = tf[f]
            if 25.5 <= t < 40:
                k = keys(t, [(25.5, 0), (26.5, 1), (39, 1), (40, 0)])
                sw[f] = 0.75 * np.sin(2 * np.pi * (t - 25.5) / (6.5 + j * 1.7) + j * 2.1)
                b = k * np.exp(-((ang - sw[f]) / 0.035) ** 2)
                lit[f] = b.sum()
                xm[f] = (b * xz[:, 0]).sum() / (b.sum() + 1e-9) if b.sum() > 0.05 else np.interp(sw[f], [-0.75, 0.75],
                                                                                                    [-700, 700])
        env = np.tanh(lit / 30)
        base = (79, 75)[j]
        whistle = tone(up(base + 4 * sw / 0.75) + 0.08 * np.sin(2 * np.pi * 4.5 * ts), up(env), (1.0, 0.25, 0.08))
        put('beams', whistle + 0.6 * air[j] * up(env), pan_x(xm))
        last = -9.0
        for f in range(1, F - 1):                       # a chime where the beam flares down a run toward us
            if lit[f] > 35 and lit[f] >= lit[f - 1] and lit[f] > lit[f + 1] and tf[f] - last > 0.6:
                t = last = tf[f]
                m = base + 12 + (1 if 33.5 <= t < 37.5 else 0) * (1 if j == 0 else 2)
                M.add('bells', chime.render([(0.0, m, 100, 0.3)], 2.5), t, min(1.0, lit[f] / 60), float(pan_x(xm[f])))

    # ---- 40-55: scanning planes; pulsing bass, a sonar that steps through the chord as the plane moves ----
    bass = []
    sc_pitch, sc_amp, sc_pan = np.full(F, 72.0), np.zeros(F), np.zeros(F)
    flat = {}                               # each run lies at one x (Side, Porch sides) or one z (the fronts)
    for k in G.seg:
        ax = 0 if np.ptp(P[G.seg[k], 0]) < np.ptp(P[G.seg[k], 2]) else 2
        flat[k] = (ax, float(P[G.seg[k], ax].mean()))
    for i, (t0, dur, axis, a, b, c) in enumerate(PLANES):
        end = t0 + dur + 0.8
        nxt = PLANES[i + 1][0] if i + 1 < len(PLANES) else 55.0
        for e in range(round((nxt - t0) / 0.25)):      # eighths until the next plane takes over
            t = t0 + 0.25 * e
            m = ROOT[c] + (0, 12, 0, 7, 0, 12, 10, 12)[e % 8]
            bass.append((t, m, 100 if e % 2 == 0 else 80, 0.2))
            M.add('drums', shaker.play(50 + 20 * (e % 2 == 1)), t, 0.4, 0.3)
        M.add('drums', bd.play(105), t0, 0.8)
        M.add('fx', zap.play(100), t0, 0.7, float(pan_x(a if axis == 0 else 16)))
        tones = sorted({m + 12 * o for m in PAD[c] for o in range(-2, 4)})
        for f in range(F):
            t = tf[f]
            if t0 <= t < end:
                u = smoothstep(0, 1, (t - t0) / dur)
                plane = lerp(a, b, u)
                behind = (plane - P[:, axis]) * np.sign(b - a)
                band = (np.exp(-(behind / 22) ** 2) + np.where(behind > 0, 0.35 * np.exp(-behind / 90), 0)) * \
                    min(1, (end - t) / 0.8)
                want = 72 + 12 * (u if (axis == 0 or b > a) else 1 - u)
                sc_pitch[f] = min(tones, key=lambda q: abs(q - want))
                sc_amp[f] = max(sc_amp[f], np.tanh(band.sum() / 25))
                sc_pan[f] = pan_x((band * P[:, 0]).sum() / (band.sum() + 1e-9))
        for k, (ax, v) in flat.items():                 # the plane sweeps a whole run at once: bell and thump
            if ax != axis or not (min(a, b) <= v <= max(a, b)):
                continue
            tt = np.arange(0, dur, 0.001)
            th = t0 + tt[np.argmin(np.abs(lerp(a, b, smoothstep(0, 1, tt / dur)) - v))]
            M.add('bells', bell.render([(0.0, ROOT[c] + 48, 110, 0.4), (0.0, ROOT[c] + 55, 90, 0.4)], 3.0), th, 1.0,
                  float(pan_x(seg_x[k])))
            M.add('drums', timp.play(100, pitch=ROOT[c] - 43), th, 0.6, float(pan_x(seg_x[k])))
        pad += [(t0, m, 54, dur + 0.5) for m in PAD[c]]
    gate = np.exp(-((ts - 40.0) % 0.125) / 0.035)       # sixteenth-note sonar pulses
    put('scan', tone(up(sc_pitch), up(sc_amp) * gate, (1.0, 0.0, 0.3, 0.0, 0.1)), sc_pan)

    # ---- 55-66: three spirits spiral in; the ghost one is the theremin again, the others a choir; harp climbs ----
    lt_f = tf - 55
    voices = [np.zeros(F) for _ in range(3)]
    pans = [np.zeros(F) for _ in range(3)]
    for f in np.nonzero((lt_f >= 0) & (lt_f < 11))[0]:
        lt = lt_f[f]
        r = lerp(750, 0, smoothstep(0, 11, lt) ** 0.8)
        spin = 0.6 * lt + 0.06 * lt ** 2.4
        for s, ph in enumerate((0.0, 2 * np.pi / 3, 4 * np.pi / 3)):
            a = spin * 2 * np.pi / 3 + ph
            c = CENTRE + np.array([r * np.sin(a), 0, r * np.cos(a)])
            voices[s][f] = 0.9 * np.exp(-(np.linalg.norm(P - c, axis=1) / 100) ** 2).max()
            pans[s][f] = pan_x(c[0])
    cres = np.clip((tf - 55) / 11, 0, 1)
    sel = (tf >= 55) & (tf < T_BURST)
    th_pitch[sel] = [SPIRIT_NOTES[chord_at(t, SPIRIT_PROG)][0] for t in tf[sel]]
    th_amp[sel] = (0.35 + 0.65 * cres[sel]) * (0.45 + 0.55 * voices[0][sel])
    th_pan[sel] = pans[0][sel]
    th_vib[sel] = 0.2 + 0.2 * cres[sel]
    ooh = M.synth('Pads/Ooh')
    for s in (1, 2):
        notes = [(t0 - 55, SPIRIT_NOTES[c][s], 90, (SPIRIT_PROG + [(T_BURST, None)])[i + 1][0] - t0)
                 for i, (t0, c) in enumerate(SPIRIT_PROG)]
        sig = mono_at(ooh.render(notes, 12.5), 55.0)
        put('choir', sig * up((0.3 + 0.7 * cres) * (0.4 + 0.6 * voices[s])), pans[s])
    for i, (t0, c) in enumerate(SPIRIT_PROG):
        d = (SPIRIT_PROG + [(T_BURST, None)])[i + 1][0] - t0
        pad += [(t0, m, 60 + 4 * i, d) for m in PAD[c]]
        sub.append((t0, ROOT[c], 90, d))
    prev = 0
    for f in np.nonzero(sel)[0]:                        # a harp note each time a spirit swings past the front
        lt = lt_f[f]
        k = int((0.6 * lt + 0.06 * lt ** 2.4) // 1)
        if k > prev:
            r = lerp(750, 0, smoothstep(0, 11, lt) ** 0.8)
            want = 55 + 36 * (1 - r / 750)
            tones = sorted({m + 12 * o for m in PAD[chord_at(tf[f], SPIRIT_PROG)] for o in range(-2, 4)})
            m = min((q for q in tones if q >= want), default=tones[-1])
            M.add('harp', harp.play(m, 70 + int(40 * lt / 11)), tf[f], 0.9, float(0.3 * np.sin(k * 2.1)))
        prev = k
    M.add('drums', cresc_l.play(100, dur=7.25), T_BURST - 7.2, 0.7)
    roll = troll.play(100, dur=5.0)
    roll *= np.linspace(0.15, 1, roll.shape[1]) ** 2
    M.add('drums', roll, T_BURST - 5.0, 0.8)

    # ---- 66: the burst; a ring of white races out, then the theremin sighs and fades with the fog ----
    tb = T_BURST
    M.add('drums', gong.play(127), tb, 1.0)
    M.add('drums', bd.play(127), tb, 1.0)
    M.add('drums', clash.play(120), tb, 0.7)
    M.add('drums', timp.play(120, pitch=-7), tb, 0.8)
    for m in ('C1', 'C2', 'G2'):
        M.add('strings', piano.play(n(m), 120), tb, 1.2)
    M.add('choir', ooh.render([(0.0, m, 110, 1.2) for m in (60, 63, 67, 72)], D - tb), tb, 0.35)
    pad += [(tb, m, 80, D - tb) for m in PAD['Cm']]
    sub.append((tb, 36, 110, D - tb))
    for k in G.seg:                                     # the ring reaches each run in turn
        dmin = float(np.linalg.norm(P[G.seg[k]] - CENTRE, axis=1).min())
        m = {'Porch Front': 84, 'Porch Left': 79, 'Porch Right': 79, 'Left': 75, 'Right': 75, 'Side': 72}[k]
        M.add('bells', bell.render([(0.0, m + 12, 100, 0.5)], 3.0), tb + dmin / 1300, 0.8, float(pan_x(seg_x[k])))
    sel = tf >= tb
    th_pitch[sel] = np.interp(tf[sel], [tb, tb + 2.0, tb + 3.2], [75, 75, 72])
    th_amp[sel] = np.interp(tf[sel], [tb, tb + 0.8, tb + 1.5, tb + 2.5, D - 0.3], [0.0, 0.0, 0.8, 0.7, 0.0])
    th_pan[sel] = np.interp(tf[sel], [tb, D], [0.0, -0.6])
    th_vib[sel] = 0.3

    # ---- the theremin itself: one voice for the whole show ----
    sm = np.ones(6) / 6
    pitch = up(np.convolve(th_pitch, sm, 'same'))
    rate = 5.2 + 1.2 * up(cres)
    vib = up(th_vib) * np.sin(2 * np.pi * np.cumsum(rate) / SR)
    sig = tone(pitch + vib, up(np.convolve(th_amp, sm, 'same')), (1.0, 0.18, 0.06))
    put('theremin', np.tanh(1.4 * sig) / np.tanh(1.4), th_pan)

    M.add('pad', M.synth('Pads/Ghost Pad').render(pad, D), 0.0)
    M.add('bass', M.synth('Basses/Sub 1').render(sub, D), 0.0)
    M.add('bass', M.synth('Basses/FM Bass 1').render(bass, D), 0.0, 0.8)
