"""The Watcher: The house wakes up: wing fronts are eyes, the porch is a toothy mouth."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, heartbeat, Flicker, nframes

CODE = 'SC1'
TITLE = 'The Watcher'
KIND = 'show'
DESCRIPTION = 'The house wakes up. The wing fronts are eyes that look around and blink; the porch is a toothy mouth that talks, laughs and lunges.'

AMBER = hexc('#ffa000')
EYE_RED = hexc('#ff0800')
TOXIC = hexc('#30ff10')
ORANGE = hexc('#ff3000')
PALE = hexc('#ffd070')
DEEP_RED = hexc('#a00000')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')
RED = hexc('#ff0000')


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    D = 66.0
    out = np.zeros((nframes(D), G.N, 3))


    eyes = [(G.seg['Left'], G.span_u(G.seg['Left'])), (G.seg['Right'], G.span_u(G.seg['Right']))]
    M, uM = G.seg['Porch Front'], G.span_u(G.seg['Porch Front'])
    O = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    flick = Flicker(rng, G.N, 0.3, 1.5)
    ember = Flicker(rng, G.N, 1.0, 4.0)

    blinks = [9.0, 16.5, 24.2, 31.0, 35.6]
    syl, t = [], 28.3
    while t < 37.5:
        d = rng.uniform(0.12, 0.3)
        syl.append((t, d, rng.uniform(0.5, 1.0)))
        t += d + rng.uniform(0.05, 0.22)
    for k in range(4):                       # MUA-HA-HA-HA
        for j in range(4):
            syl.append((38.3 + k * 1.35 + j * 0.2, 0.15 if j else 0.3, 1.0))

    def talk(t):
        e = 0.0
        for s, d, a in syl:
            if s <= t <= s + d:
                e = max(e, a * np.sin(np.pi * (t - s) / d) ** 2)
        return e

    teeth = 1 - np.abs(2 * (((uM + 1) / 2 * 9) % 1) - 1)   # 9 pointed teeth
    teeth = teeth ** 1.3
    corners = 1 - 0.6 * np.abs(uM) ** 4

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fl = 1 + 0.04 * flick(t)
        o = keys(t, [(3, 0), (5.5, 1), (44, 1), (46, 0.4), (49, 0.35), (49.5, 1.05), (50, 1.05), (50.01, 0),
                     (57.5, 0), (59, 0.2), (62, 0.2), (62.5, 0)])
        o *= 1 - max([max(0.0, 1 - abs(t - b) / 0.13) for b in blinks])
        gaze = keys(t, [(5, 0), (6.5, -0.9), (10, -0.9), (11.3, 0.85), (14.5, 0.85), (15.3, 0.3), (17.3, -0.45),
                        (19.8, -0.45), (20.0, 0), (28, 0), (30, 0.15), (32, -0.1), (44, 0), (57.5, -0.9), (62.5, 0.9)])
        pw = keys(t, [(5, 0.06), (19.9, 0.06), (20.2, 0.14), (24, 0.08), (44, 0.05), (49.4, 0.03)])
        anger = keys(t, [(28, 0), (38, 0.35), (44, 0.7), (46, 1.0)])
        eI = keys(t, [(3, 0), (5.5, 0.85), (44, 0.9), (49, 0.8), (49.5, 1.0), (50, 1.0), (50.01, 0), (57.5, 0),
                      (59, 0.5), (62.5, 0.5)])
        ecol = TOXIC if t > 55 else lerp(AMBER, EYE_RED, anger)
        for idx, u in eyes:
            lid = np.clip((o - np.abs(u)) / 0.08, 0, 1)
            shape = 0.55 + 0.45 * (1 - u ** 2)
            pupil = np.clip((np.abs(u - gaze * 0.55) - pw) / 0.04, 0, 1)
            fr[idx] += light(ecol, eI * lid * shape * (0.03 + 0.97 * pupil) * fl[idx])

        # mouth
        grin = keys(t, [(20.5, 0), (23, 0.7), (44, 0.7), (46, 0.35), (49, 0.35), (49.4, 0)])
        mo = grin + (0.4 * talk(t) if 28 < t < 44 else 0.0)
        reveal = keys(t, [(20.5, 0), (22.5, 1.1)])
        rmask = np.clip((reveal - np.abs(uM)) / 0.1, 0, 1)
        mcol = lerp(lerp(ORANGE, PALE, teeth[:, None] * min(1, mo * 1.5)), EYE_RED, anger * 0.6)
        fr[M] += perc(mo * corners * (0.25 + 0.75 * teeth) * rmask)[:, None] * mcol
        fr[M] += light(DEEP_RED, 0.45 * mo * (1 - teeth) * rmask)

        # head outline
        oI = keys(t, [(2, 0), (5, 0.18), (44, 0.18), (49.4, 0.18), (49.5, 0)])
        if 44 < t < 49.5:
            oI += 0.4 * heartbeat(t, 44, keys(t, [(44, 1.0), (49.5, 0.45)]))
        ocol = lerp(PURPLE, RED, anger)
        fr[O] += light(ocol, oI * (1 + 0.15 * np.sin(2 * np.pi * t / 4)) * fl[O])

        # the lunge
        if 50 <= t < 50.45:
            strobe = any(s <= t < s + 0.06 for s in (50.0, 50.16, 50.32))
            fr[:] = WHITE * (1.0 if strobe else 0.15)
        elif t >= 50.45:
            e = 0.35 * np.exp(-(t - 50.45) / 1.8) * np.clip(ember(t), 0, 1) ** 2
            fr[:] += light(RED, e)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A horror cue in E minor that wakes up with the house. The eyelids creak at the speed they move; a pair of theremins,
# one behind each eye, sing the Watcher's theme and glide exactly as the pupils do, panned to where the pupils are; each
# blink is a soft thup and a harp note. When it sees you, a stinger. The porch mouth has a voice (formant synthesis
# over the mouth's own syllable envelopes): gibberish over an E pedal ostinato, then MUA-HA-HA-HA climbing a semitone a
# laugh with trombones falling under every HA. The heartbeat drum hits on the outline's lub-dubs, everything stops when
# the eyes snap open, and the lunge is three hits on the three strobes, then embers and the dark. render() must stay
# byte-identical, so its keyframes are restated here.

O_KEYS = [(3, 0), (5.5, 1), (44, 1), (46, 0.4), (49, 0.35), (49.5, 1.05), (50, 1.05), (50.01, 0),
          (57.5, 0), (59, 0.2), (62, 0.2), (62.5, 0)]
EI_KEYS = [(3, 0), (5.5, 0.85), (44, 0.9), (49, 0.8), (49.5, 1.0), (50, 1.0), (50.01, 0), (57.5, 0),
           (59, 0.5), (62.5, 0.5)]
GAZE_KEYS = [(5, 0), (6.5, -0.9), (10, -0.9), (11.3, 0.85), (14.5, 0.85), (15.3, 0.3), (17.3, -0.45),
             (19.8, -0.45), (20.0, 0), (28, 0), (30, 0.15), (32, -0.1), (44, 0), (57.5, -0.9), (62.5, 0.9)]
ANGER_KEYS = [(28, 0), (38, 0.35), (44, 0.7), (46, 1.0)]
BLINKS = [9.0, 16.5, 24.2, 31.0, 35.6]
SEES = 20.0                                  # gaze snaps to centre, pupils dilate (19.9-20.2)
REVEAL = (20.5, 22.5)                        # the mouth opens from the middle out
LAUGH, LAUGH_GAP, HA = 38.3, 1.35, 0.2       # MUA-HA-HA-HA x4
HEART = (44.0, 49.5)                         # lub-dub on the outline, period 1.0 -> 0.45 s
HUSH = 49.4                                  # the mouth shuts, the eyes go wide: silence
STROBES = (50.0, 50.16, 50.32)               # the lunge
EMBER, TAU = 50.45, 1.8                      # the red afterglow decays with this time constant
BEAT = LAUGH_GAP / 2                         # 88.9 BPM: one laugh every two beats
P0 = LAUGH - 16 * BEAT                       # 27.5: the ostinato starts four bars before the first laugh
THEME = [(5, 'B4'), (6.5, 'G4'), (10, 'G4'), (11.3, 'C5'), (14.5, 'C5'), (15.3, 'A4'), (17.3, 'D#5'),
         (19.8, 'D#5'), (20.0, 'E5')]        # one note per gaze hold, gliding on the gaze's own keyframes
CODA = [(57.5, 'E4'), (62.5, 'A#4')]         # green eyes sweep left to right: a tritone, unresolved
BARS = ['Em', 'F', 'Em', 'Am']               # the four talking bars from P0
CHORDS = {'Em': (52, 55, 59), 'F': (53, 57, 60), 'Am': (57, 60, 64), 'B7': (47, 51, 54, 57)}
ROOTS = {'Em': 28, 'F': 29, 'Am': 33}
VOWELS = {'a': (730, 1090, 2440), 'o': (570, 840, 2410), 'u': (300, 870, 2240), 'e': (530, 1840, 2480),
          'i': (390, 1990, 2550), 'ae': (660, 1720, 2410)}


def _syllables(G, seed=1):
    """The mouth's talking syllables (start, duration, amplitude), drawn exactly as render() draws them."""
    from pixelhome.fx import Flicker
    rng = np.random.default_rng(seed)
    Flicker(rng, G.N, 0.3, 1.5)
    Flicker(rng, G.N, 1.0, 4.0)
    syl, t = [], 28.3
    while t < 37.5:
        d = rng.uniform(0.12, 0.3)
        syl.append((t, d, rng.uniform(0.5, 1.0)))
        t += d + rng.uniform(0.05, 0.22)
    return syl


def _ma(x, w):
    """Centred moving average over w samples."""
    c = np.concatenate([[0.0], np.cumsum(np.concatenate([np.full(w // 2, x[0]), x, np.full(w - w // 2, x[-1])]))])
    return (c[w:w + len(x)] - c[:len(x)]) / w


def _kv(ts, pts):
    return np.array([keys(t, pts) for t in ts], float)


def _lid(ts, blinks=True):
    """render()'s eye openness o(t), with or without the blink dips."""
    o = _kv(ts, O_KEYS)
    if blinks:
        o *= 1 - np.max([np.clip(1 - np.abs(ts - b) / 0.13, 0, None) for b in BLINKS], axis=0)
    return o


def _stereo(sig, pan):
    """Constant-power pan with a per-sample pan array."""
    a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)


def _creak(rate, amp, rng, res=(430.0, 980.0, 1900.0)):
    """Stick-slip creak: a click train at `rate` Hz (per sample), each click ringing a few wooden resonances."""
    from pixelhome.audio import SR
    n = len(rate)
    ph = np.cumsum(rate * (1 + 0.25 * rng.normal(0, 1, n).clip(-2, 2))) / SR
    ticks = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    tt = np.arange(int(0.04 * SR)) / SR
    r = np.array(res) * rng.uniform(0.93, 1.07, len(res))
    ping = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / (0.009 - 0.002 * i)) / (i + 1) for i, f in enumerate(r))
    ping += 0.6 * np.sin(2 * np.pi * 170 * tt) * np.exp(-tt / 0.02)
    out = np.zeros(n + len(tt))
    for i in ticks:
        out[i:i + len(tt)] += amp[i] * rng.uniform(0.5, 1.0) * ping
    return out[:n] / 2.5


def _voice(f0, F, amp, rng, growl=0.0):
    """Formant voice by additive synthesis: harmonics of f0 weighted by three resonances F (3, n)."""
    from pixelhome.audio import SR
    n = len(f0)
    jit = np.convolve(rng.normal(0, 1, n), np.ones(400) / 400, 'same') * 0.6
    f = f0 * (1 + 0.02 * jit)
    ph = 2 * np.pi * np.cumsum(f) / SR
    out = np.zeros(n)
    for k in range(1, int(min(60, 5500 / f0.min())) + 1):
        fk = k * f
        a = sum(g / (1 + ((fk - F[i]) / bw) ** 2) for i, (g, bw) in enumerate(((1.0, 90), (0.55, 110), (0.3, 160))))
        out += a * (fk < 6000) * np.sin(k * ph) / k ** 0.3
    if growl:
        out *= 1 + growl * np.sin(ph / 2 + 0.3 * np.sin(ph / 3))
    return out * amp


def _shaped_noise(n, rng, F, width=3.0):
    """Noise through the same resonances: breath for an H, or a hiss for consonants when F is high."""
    x = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1 / 48000)
    h = sum(g / (1 + ((f - F[i]) / (bw * width)) ** 2) for i, (g, bw) in enumerate(((1.0, 90), (0.55, 110), (0.3, 160))))
    y = np.fft.irfft(x * h, n)
    return y / (np.abs(y).max() + 1e-9)


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    vrng = np.random.default_rng(66)
    D = M.seconds
    harp = M.sampler('Strings/Harp/*.wav')
    cb_sus = M.sampler('Strings/Solo Contrabass/SusNV/*.wav')
    cb_pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav')
    spic = M.sampler('Strings/Cello Section/spic/*.wav')
    c_trem = M.sampler('Strings/Cello Section/trem/*.wav')
    va_trem = M.sampler('Strings/Viola Section/trem/*.wav')
    v_trem = M.sampler('Strings/Violin Section/Trem/*.wav')
    horn_m = M.sampler('Brass/F Horn/mute/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav')
    horn_s = M.sampler('Brass/F Horn/stac/*.wav')
    tbn = M.sampler('Brass/OldTrombone/Short/*.wav')
    tbn_b = M.sampler('Brass/OldTrombone/Buzz/*.wav')
    tpt = M.sampler('Brass/Trumpet/sus/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3*.wav')
    bd_hb = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_ff*.wav')
    bd_dub = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_mp*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    scrape = M.hits('Percussion/gongscrape_pp.wav')
    cymb = M.hits('Percussion/susCymb1-hit_fff*.wav')
    cresc = M.hits('Percussion/susCymb1-cresc-Short_v1.wav')
    bow = M.hits('Percussion/susCymb1-bow-3.wav')
    glass = M.hits('Miscellania Raw/Misc 1/glass_break*.wav')
    thup = M.hits('Percussion/Tumba-Tap1*.wav')

    for name, gain, rev in (('pad', 0.2, 0.35), ('theremin', 0.03, 0.35), ('creak', 0.3, 0.15), ('voice', 0.2, 0.1),
                            ('strings', 0.2, 0.3), ('ostinato', 0.22, 0.12), ('brass', 0.3, 0.2), ('perc', 0.3, 0.18),
                            ('heart', 0.4, 0.04), ('riser', 0.22, 0.05), ('lunge', 0.6, 0.25), ('fx', 0.22, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()

    def pan_x(x):                            # x across the facade -> left/right as seen from the street
        return 0.85 * (2 * (np.asarray(x, float) - x0) / (x1 - x0) - 1)

    span = {k: float(pan_x(G.pos[G.seg[k], 0].mean())) for k in G.seg}
    mouth = span['Porch Front']
    outline = float(pan_x(G.pos[np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']]), 0].mean()))
    eyes = []
    for k in ('Left', 'Right'):
        ex = G.pos[G.seg[k], 0]
        eyes.append(((ex.max() + ex.min()) / 2, (ex.max() - ex.min()) / 2))

    cr = 200                                 # control rate for the light curves
    tc = np.arange(0, D + 1, 1 / cr)
    ts = np.arange(M.n) / SR

    def at(curve, t0, t1):                   # a control curve resampled to audio for [t0, t1)
        tt = ts[int(t0 * SR):int(t1 * SR)]
        return tt, np.interp(tt, tc, curve)

    def gate(sig, t0, cuts):                 # multiply a signal starting at t0 by a piecewise-linear gain
        tt = t0 + np.arange(sig.shape[-1]) / SR
        g = np.interp(tt, [c[0] for c in cuts], [c[1] for c in cuts])
        return sig * g

    def chord_at(t):
        return BARS[min(3, max(0, int((t - P0) // (4 * BEAT))))]

    anger = _kv(tc, ANGER_KEYS)
    o_lid = _lid(tc)
    o_raw = _lid(tc, blinks=False)
    eI = _kv(tc, EI_KEYS)
    gaze = _kv(tc, GAZE_KEYS)

    # ---- the eyelids creak at the speed they move (opening, squinting, snapping wide, the green ones) ----
    speed = np.abs(np.gradient(o_raw, 1 / cr))
    speed[(tc > 49.98) & (tc < 50.2)] = 0    # the instant blackout at 50.01 is the lunge, not a lid
    s = np.clip(speed / 1.5, 0, 1)
    lit = np.maximum(eI, 0.5 * (tc < 50))
    for i, (cx, hw) in enumerate(eyes):
        tt, si = at(s, 2.8, 63.0)
        _, li = at(lit, 2.8, 63.0)
        rate = 14 + 150 * si
        amp = np.sqrt(si) * (si > 0.02) * (0.4 + 0.6 * li)
        M.add('creak', _stereo(_creak(rate, amp, vrng), np.full(len(tt), span[('Left', 'Right')[i]])), 2.8)

    # ---- 0-5.5: the house stirs; the timbers groan before the eyes open ----
    pad = []
    pad += [(0.4, n('E2'), 70, 5.0), (0.4, n('B2'), 60, 5.0)]
    M.add('strings', cb_sus.play(n('E1'), 70, dur=6.0, release=1.0), 0.6, 0.35, -0.1)
    M.add('fx', scrape.play(100, pitch=-5, dur=5.0), 1.0, 0.7, span['Side'])
    for k, (t0, t1) in (('Side', (2.0, 5.0)), ('Porch Right', (2.6, 5.4))):
        nn = int((t1 - t0) * SR)
        u = np.arange(nn) / nn
        rate = 6 + 14 * np.sin(np.pi * u) + 4 * np.sin(2 * np.pi * 1.3 * u * (t1 - t0))
        amp = np.sin(np.pi * u) ** 1.5
        M.add('creak', _creak(rate, amp, vrng, res=(260.0, 610.0, 1400.0))[None].repeat(2, 0), t0, 0.8, span[k])
    for m, v in (('E3', 50), ('B3', 46), ('G4', 40)):
        M.add('strings', va_trem.play(n(m), v, dur=2.6, release=0.6), 3.0, 0.35, 0.0)
    M.add('perc', harp.play(n('E2'), 90), 5.5, 0.9, span['Left'])
    M.add('perc', harp.play(n('B2'), 90), 5.5, 0.9, span['Right'])

    # ---- 4-20: the watcher's theme on two theremins, one per eye, gliding on the gaze ----
    def theremin(pts, t0, t1, cut, detune):
        pitch = _kv(tc, [(t, n(m) if isinstance(m, str) else m) for t, m in pts])
        tt, mp = at(pitch, t0, t1)
        _, a = at(np.clip(o_lid, 0, 1) * eI, t0, t1)
        _, g = at(gaze, t0, t1)
        a = _ma(a, 480) * np.clip((tt - t0) / 0.3, 0, 1) * np.clip((cut - tt) / 0.025, 0, 1)
        vib = 0.12 + 0.18 * _ma((np.abs(np.gradient(mp)) < 1e-6).astype(float), SR)   # deeper on held notes
        out = np.zeros((2, len(tt)))
        for (cx, hw), dt in zip(eyes, (-detune, detune)):
            f = 440 * 2 ** ((mp + dt + vib * np.sin(2 * np.pi * 5.6 * tt)) / 12 - 69 / 12)
            ph = 2 * np.pi * np.cumsum(f) / SR
            sig = a * (np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph))
            out += _stereo(sig, pan_x(cx + g * 0.55 * hw))
        return out

    M.add('theremin', theremin(THEME, 4.0, 20.1, SEES - 0.03, 0.04), 4.0)
    pad += [(5.5, n('E3'), 64, 5.8), (5.5, n('G3'), 58, 5.8), (5.5, n('B3'), 58, 5.8)]
    pad += [(11.3, n('F3'), 62, 4.0), (11.3, n('A3'), 58, 4.0), (11.3, n('C4'), 56, 4.0)]
    pad += [(15.3, n('A2'), 60, 2.0), (15.3, n('C4'), 56, 2.0), (15.3, n('E4'), 54, 2.0)]
    pad += [(17.3, m, 64, 2.6) for m in CHORDS['B7']]
    M.add('strings', cb_sus.play(n('E1'), 64, dur=13.5, release=1.0), 6.0, 0.7, -0.1)

    # ---- blinks: lid shuts with a soft thup on both eyes, opens on a harp note from the chord of the moment ----
    for b, m in zip(BLINKS, ('E4', 'A3', 'E4', 'F3', 'A3')):
        for k in ('Left', 'Right'):
            M.add('perc', thup.play(80, pitch=-4), b - 0.03, 0.8, span[k])
        M.add('perc', harp.play(n(m), 80), b + 0.1, 0.7, span['Left'])
        M.add('perc', harp.play(n(m) + 7, 70), b + 0.16, 0.6, span['Right'])

    # ---- 20: it sees you. Gaze snaps to the middle, pupils dilate: stinger ----
    for m in ('E3', 'F3', 'Bb3'):
        M.add('brass', horn_m.play(n(m), 120, dur=0.9, release=0.4), SEES, 0.7, 0.0)
    M.add('perc', timp.play(120, pitch=-3), SEES, 0.7)
    M.add('perc', bd.play(100), SEES, 0.4)
    M.add('strings', cb_pizz.play(n('E1'), 127), SEES, 1.0)
    for m in ('E6', 'F6'):
        M.add('strings', v_trem.play(n(m), 90, dur=1.2, release=0.6), SEES, 0.5, 0.0)
    nn = int(0.4 * SR)                       # the pupils open: a falling sine, 19.9-20.2
    tt = np.arange(nn) / SR
    f = 180 * 2 ** (-tt / 0.15)
    M.add('fx', np.vstack([np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.12)] * 2) * 0.8, 19.9, 1.0)

    # ---- 20.5-27.5: the mouth opens from the middle out; the grin holds; a music box plays the theme ----
    choir = [(0.5 * i, n(m), 70 + 6 * i, 7.0 - 0.5 * i) for i, m in enumerate(('E3', 'B3', 'E4', 'G4', 'B4'))]
    M.add('pad', M.synth('Pads/Synth Choir MW O-Ah').render(choir, 9.0), REVEAL[0], 0.55)
    M.add('fx', bow.play(90, dur=6.0), REVEAL[0] - 0.4, 0.8, mouth)
    pad += [(22.5, n('E2'), 60, 5.0), (22.5, n('B2'), 54, 5.0)]
    box = ['G5', 'C6', 'A5', 'D#6', 'E6', None, 'B5', None]
    for i, m in enumerate(box):
        if m:
            M.add('perc', glock.play(n(m), 58), P0 - 7 * BEAT + i * BEAT * 0.75, 0.55, mouth)

    # ---- 27.5-38.3: it talks. E pedal ostinato in eighths, getting angrier; four bars Em F Em Am ----
    syl = _syllables(G)
    ang = lambda t: float(np.interp(t, tc, anger))
    for e in range(int((HEART[0] - P0) / (BEAT / 2))):
        t = P0 + e * BEAT / 2
        if t >= HEART[0]:
            break
        k = min(3, int((t - LAUGH) // LAUGH_GAP)) if t >= LAUGH else -1
        root = n('E2') + max(0, k)
        off = (0, 0, 12, 0, 1, 0, 7, 0)[e % 8]
        M.add('ostinato', spic.play(root + off, int(60 + 60 * ang(t))), t, 1.0, -0.3)
        if e % 8 == 0 and t < LAUGH:
            c = chord_at(t)
            M.add('ostinato', cb_pizz.play(ROOTS[c], 110), t, 1.0, -0.1)
            pad += [(t, m, 58 + int(30 * ang(t)), 4 * BEAT) for m in CHORDS[c]]
            if t >= P0 + 8 * BEAT:          # violas join on bar 3
                for m in CHORDS[c][1:]:
                    M.add('strings', va_trem.play(m - 12, 70 + int(40 * ang(t)), dur=4 * BEAT), t, 0.6, 0.35)
    for i, (s0, d, a) in enumerate(syl):
        v0, v1 = vrng.choice(list(VOWELS), 2)
        p0 = vrng.uniform(-1, 3)
        say = dict(v0=v0, v1=v1, p0=p0, p1=p0 + vrng.uniform(-4, 2), fric=vrng.uniform() < 0.35)
        _say(M, s0, d, a, base=92 * 2 ** (3 * ang(s0) / 12), growl=0.15 + 0.4 * ang(s0), pan=mouth, rng=vrng, **say)

    # ---- 38.3-43.7: MUA-HA-HA-HA, a semitone higher each time; trombones fall under the HAs ----
    for k in range(4):
        t = LAUGH + k * LAUGH_GAP
        root = n('E2') + k
        _say(M, t, 0.3, 1.0, 'u', 'a', 4 + k, 7 + k, base=100, growl=0.35 + 0.1 * k, pan=mouth, rng=vrng, h=0.4)
        for j in range(1, 4):
            _say(M, t + j * HA, 0.15, 1.0, 'a', 'a', 7 + k - 1.5 * j, 6 + k - 1.5 * j, base=100,
                  growl=0.4 + 0.1 * k, pan=mouth, rng=vrng, h=1.0)
            M.add('brass', tbn.play(root + 19 - j, 105 + 5 * k), t + j * HA, 0.7, mouth + 0.2)
        M.add('perc', timp.play(105 + 6 * k, pitch=k - 3), t, 0.9)
        M.add('ostinato', cb_pizz.play(n('E1') + k, 120), t, 1.0, -0.1)
        for m in (root + 12, root + 15, root + 19):
            M.add('brass', horn_s.play(m, 110 + 4 * k), t, 0.8, -0.2)
        pad += [(t, root + 12, 80, LAUGH_GAP), (t, root + 15, 76, LAUGH_GAP), (t, root + 19, 76, LAUGH_GAP)]

    # ---- 44-49.4: the heartbeat on the outline, the eyes narrow, everything rises... and stops ----
    th = np.arange(HEART[0], HEART[1], 0.001)
    per = _kv(th, [(44, 1.0), (49.5, 0.45)])
    ph = (th - HEART[0]) % per
    hb = np.exp(-((ph - 0.03) / 0.05) ** 2) + 0.7 * np.exp(-((ph - 0.25) / 0.06) ** 2)
    pk = [i for i in range(1, len(th) - 1) if hb[i] >= hb[i - 1] and hb[i] > hb[i + 1] and hb[i] > 0.45]
    beats = []
    for i in pk:
        if not beats or th[i] - beats[-1][0] > 0.08:
            beats.append((float(th[i]), float(hb[i])))
    for t, v in beats:
        if t >= HUSH:
            continue
        lub = v > 0.85
        u = (t - HEART[0]) / (HUSH - HEART[0])
        hush = [(0, 1), (HUSH - t + 0.02, 1), (HUSH - t + 0.06, 0), (99, 0)]
        M.add('heart', gate((bd_hb if lub else bd_dub).play(100 if lub else 85), 0, hush), t - 0.02, 0.7 + 0.3 * u, outline)
        if lub:
            M.add('heart', gate(timp.play(80 + int(40 * u), pitch=-7), 0, hush), t - 0.02, 0.4 + 0.4 * u, outline)
    up = lambda sig, t0, g0=0.15: gate(sig, t0, [(t0, g0), (HUSH, 1.0), (HUSH + 0.04, 0), (99, 0)])
    rs = M.synth('FX/Unsettler').render([(0.0, n('E2'), 100, 6.0)], 6.0)
    M.add('riser', up(rs, HEART[0]), HEART[0])
    for m, smp, v in (('E5', v_trem, 90), ('F5', v_trem, 90), ('Bb2', c_trem, 100), ('E2', c_trem, 100)):
        M.add('riser', up(smp.play(n(m), v, dur=6.0), HEART[0]), HEART[0], 1.6, 0.0)
    cz = cresc.play(110)
    env = np.abs(cz).max(0)
    peak = int(np.argmax(_ma(env, 2400))) / SR
    M.add('riser', gate(cz, HUSH - peak, [(0, 1), (peak, 1), (peak + 0.03, 0), (99, 0)]), HUSH - peak, 0.8)
    pad += [(HEART[0], n('Bb2'), 80, HUSH - HEART[0]), (HEART[0], n('E3'), 80, HUSH - HEART[0])]
    # the house draws a breath in the silence
    M.add('fx', whoosh(0.42, 250, 1800, 0.5, seed=5), HUSH + 0.12, 0.6, mouth)

    # ---- 50.0: the lunge. Three hits on the three strobes, then the red embers decay ----
    for i, t in enumerate(STROBES):
        g = (1.0, 0.75, 0.85)[i]
        M.add('lunge', bd.play(127), t, g)
        M.add('lunge', timp.play(127, pitch=-5 + i), t, g)
        M.add('lunge', cymb.play(127), t, 0.7 * g)
        for m in ('E2', 'Bb2'):
            M.add('brass', tbn.play(n(m), 127), t, 1.2 * g, -0.3)
            M.add('brass', tbn.play(n(m) + 12, 127), t, 0.9 * g, 0.3)
    M.add('lunge', glass.play(120), STROBES[0] + 0.02, 0.6, span['Left'])
    M.add('lunge', glass.play(120), STROBES[1] + 0.02, 0.6, span['Right'])
    M.add('fx', whoosh(0.3, 200, 4000, 0.6, seed=9), STROBES[0] - 0.22, 0.9)
    ember = lambda sig, t0, k=1.0: gate(sig, t0, [(0, 1), (EMBER, 1)] + [(EMBER + x, np.exp(-x / (k * TAU)))
                                                                          for x in (1, 2, 3, 4, 6, 9, 14)])
    M.add('lunge', ember(gong.play(127), STROBES[0], 1.6), STROBES[0], 0.9)
    for m, smp, p in (('E3', horn, -0.4), ('F4', horn, 0.4), ('Bb4', tpt, -0.2), ('E5', tpt, 0.2),
                      ('E2', tbn_b, -0.3), ('Bb2', tbn_b, 0.3)):
        M.add('brass', ember(smp.play(n(m), 127, dur=4.0, release=1.5), STROBES[0], 0.75), STROBES[0], 1.1, p)
    for m in ('E6', 'F6', 'Bb5'):
        M.add('strings', ember(v_trem.play(n(m), 127, dur=4.0, release=1.5), STROBES[0], 0.75), STROBES[0], 1.6, 0.0)
    M.add('strings', ember(cb_sus.play(n('E1'), 110, dur=8.0, release=3.0), STROBES[0]), STROBES[0], 1.5, -0.1)
    for p, dt in ((-0.55, -0.15), (0.55, 0.15)):
        _say(M, STROBES[0], 1.9, 1.0, 'a', 'ae', 0 + dt, -7 + dt, base=220, growl=0.6, pan=p, rng=vrng,
              scream=True, gain=1.2)

    # ---- 57.5-62.5: dark, then green eyes open and sweep left to right; they close; something chuckles ----
    M.add('theremin', theremin(CODA, 57.0, 63.0, 62.55, 0.09), 57.0, 0.8)
    pad += [(57.5, n('E3'), 50, 5.0), (57.5, n('Bb3'), 46, 5.0)]
    M.add('strings', cb_sus.play(n('E1'), 50, dur=5.0, release=1.0), 57.5, 0.6, -0.1)
    for k in ('Left', 'Right'):
        M.add('perc', thup.play(90, pitch=-6), 62.45, 0.6, span[k])
    M.add('strings', cb_pizz.play(n('E1'), 100), 62.5, 0.8)
    M.add('perc', harp.play(n('E2'), 70), 62.55, 0.8)
    for j in range(2):
        _say(M, 63.2 + 0.2 * j, 0.12, 0.6, 'e', 'e', 0 - 1.5 * j, -1 - 1.5 * j, base=85, growl=0.3, pan=mouth,
              rng=vrng, h=1.0, gain=0.6)

    padsig = M.synth('Pads/Ghost Pad').render(pad, D)
    M.add('pad', gate(padsig, 0, [(0, 1), (SEES - 0.05, 1), (SEES, 0.15), (REVEAL[0], 0.15), (REVEAL[1], 1),
                                  (HUSH, 1), (HUSH + 0.04, 0), (57.0, 0), (57.5, 1), (99, 1)]), 0.0)


def _say(M, t0, d, a, v0='a', v1='a', p0=0.0, p1=0.0, base=100.0, growl=0.2, pan=0.0, rng=None, h=0.0, fric=False,
          scream=False, gain=1.0):
    """One syllable from the mouth: d seconds starting at t0, peak a, vowel v0 -> v1, pitch p0 -> p1 semitones over
    `base` Hz, with a demon an octave below. h adds breath at the onset (an H), fric a hiss (a consonant)."""
    from pixelhome.audio import SR
    nn = int((d + (0.0 if scream else 0.03)) * SR)
    tt = np.arange(nn) / SR
    u = np.clip(tt / d, 0, 1)
    if scream:                               # attack, then the ember's decay
        env = np.clip(tt / 0.03, 0, 1) * np.exp(-np.clip(tt - (EMBER - STROBES[0]), 0, None) / (TAU * 0.5))
        env *= np.clip((d - tt) / 0.2, 0, 1)
        p = p0 + 5 * np.clip(tt / 0.25, 0, 1) - (5 - (p1 - p0)) * np.clip((tt - 0.25) / (d - 0.25), 0, 1)
    else:                                    # the mouth's own envelope: sin^2 in the lights, a little sharper here
        env = np.sin(np.pi * u) ** 0.8
        p = p0 + (p1 - p0) * u
    F = np.array(VOWELS[v0])[:, None] * (1 - u) + np.array(VOWELS[v1])[:, None] * u
    F = F * (1.08 if scream else 0.88)
    f0 = base * 2 ** (p / 12)
    sig = _voice(f0, F, env * a, rng, growl) + 0.45 * _voice(f0 / 2, F * 0.8, env * a, rng, growl * 0.5)
    if h:
        br = _shaped_noise(nn, rng, F[:, 0]) * np.exp(-tt / 0.05) * np.clip(tt / 0.005, 0, 1)
        sig += h * 0.6 * a * br * np.abs(sig).max()
    if fric:
        hs = _shaped_noise(nn, rng, (2600.0, 3800.0, 5200.0), 6.0) * np.exp(-tt / 0.025)
        sig += 0.35 * a * hs * np.abs(sig).max()
    if scream:
        sig += 0.25 * _shaped_noise(nn, rng, F[:, 0] * 1.2, 4.0) * env * np.abs(sig).max()
    M.add('voice', np.vstack([sig, sig]), t0, gain, pan)
