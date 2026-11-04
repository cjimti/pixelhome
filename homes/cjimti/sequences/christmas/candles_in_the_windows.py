"""Candles in the Windows: A candle stands in each front window, two under the Left wing, three
under the Right and one either side of the front door on the porch, and each one throws a warm pool
of light up onto the roofline above it, with its own flicker and slow sway, into the deep blue night
between. A wreath hangs over the door. Now and then the front door opens: lamplight spills out on
the porch, and the draught travels out along the house so each candle bows in turn by its distance
from the door. Once in a while a candle gutters out and is relit with the flare of a match."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'XM10'
TITLE = 'Candles in the Windows'
KIND = 'ambient'
DESCRIPTION = ('A candle in every front window throws a warm pool onto the roof above it. Now and then '
               'the front door opens and the draught makes each candle bow in turn.')

NIGHT = hexc('#0c1a5a')
FLAME = hexc('#ff7a18')
FLAME_HOT = hexc('#ffb050')
DOOR = hexc('#ffa040')
WREATH = hexc('#10a030')
BOW = hexc('#e01010')
MATCH = hexc('#fff0c0')
FLOOR = 0.1
LOOP = 170.0
WINDOWS = [('Left', -480), ('Left', -310), ('Porch Front', -95), ('Porch Front', 55),
           ('Right', 270), ('Right', 420), ('Right', 560)]
SEED = 30
DOOR_X = -20.0
LOOP_FADE = 12.0                    # looped()'s default head/tail blend


def candles(G):
    """Node of each window's candle, and the door's distance along the path."""
    P = G.pos
    pf = G.seg['Porch Front']
    door_pd = G.pd[pf[np.argmin(np.abs(P[pf, 0] - DOOR_X))]]
    cand = []
    for name, wx in WINDOWS:
        idx = G.seg[name]
        k = idx[np.argmin(np.abs(P[idx, 0] - wx))]
        cand.append(k)
    return np.array(cand), door_pd


def events(rng, D, nc):
    """The door opening [(time, seconds open)] and the candles that gutter out [(candle, time)]."""
    doors, t = [], rng.uniform(20, 35)
    while t < D:
        doors.append((t, rng.uniform(6, 10)))
        t += rng.uniform(45, 70)
    outs = [(int(rng.integers(nc)), rng.uniform(5, D - 15)) for _ in range(max(1, int(D / 55)))]
    return doors, outs


def draught_at(cpd, door_pd, ts):
    """When the draught from a door opened at ts reaches each candle."""
    return ts + 0.6 + np.abs(cpd - door_pd) / 260


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    n = G.N
    P = G.pos
    pd = G.pd
    cand, door_pd = candles(G)
    nc = len(cand)
    cpd = pd[cand]
    pool_w = rng.uniform(46, 60, nc)
    on_pf = G.seg_of == 'Porch Front'
    xpf = P[:, 0] - DOOR_X

    def draw(D):
        out = np.zeros((nframes(D), n, 3), np.float32)
        slow = Flicker(rng, nc, 0.08, 0.4)
        mid = Flicker(rng, nc, 0.7, 2.0)
        sway = Flicker(rng, nc, 0.05, 0.15)
        night = Flicker(rng, n, 0.02, 0.08)
        doors, outs = events(rng, D, nc)
        for f in range(len(out)):
            t = f * DT
            fl = 1 + 0.08 * slow(t) + 0.03 * mid(t)
            shift = 4 * sway(t)                                # the flame leans, the pool slides
            door_open = 0.0
            for ts, dur in doors:
                door_open = max(door_open, smoothstep(ts, ts + 1.2, t) * (1 - smoothstep(ts + dur, ts + dur + 1.5, t)))
                # the draught: reaches each candle by distance from the door, dips it, recovers
                for c in range(nc):
                    ta = ts + 0.6 + abs(cpd[c] - door_pd) / 260
                    u = t - ta
                    if -0.5 < u < 4:
                        fl[c] *= 1 - 0.45 * np.exp(-((u - 0.4) / 0.5) ** 2) + 0.06 * np.sin(6 * u) * np.exp(-u)
                        shift[c] += 10 * np.sign(cpd[c] - door_pd) * np.exp(-((u - 0.4) / 0.7) ** 2)
            match = np.zeros(nc)
            for c, ts in outs:
                u = t - ts
                if 0 < u < 9:
                    # gutters out over a second, stays dark, a match flares and the wick catches
                    fl[c] *= keys_out(u)
                    match[c] = np.exp(-((u - 6.2) / 0.25) ** 2)
            I_c = np.clip(fl, 0, None)
            # the pool follows the roof (path distance), so light spills round a corner
            pool = np.exp(-(np.abs(pd[:, None] - (cpd + shift)[None]) / pool_w[None]) ** 2)
            core = np.exp(-((pd[:, None] - (cpd + shift)[None]) / 5) ** 2)
            I = (pool * (0.27 * I_c)[None]).sum(1) + (core * (0.12 * I_c)[None]).sum(1)
            hot = np.clip((core * I_c[None]).sum(1), 0, 1)
            col = lerp(FLAME, FLAME_HOT, hot[:, None] * 0.7)
            buf = light(NIGHT, 0.12 * (1 + 0.1 * night(t)) * (1 - smoothstep(0.05, 0.3, I)))
            buf += perc(np.clip(I, 0, 0.42))[:, None] * col
            buf += light(MATCH, ((core * (0.4 * match)[None]).sum(1)))
            # wreath over the door, and the door's lamplight when it opens
            ring = np.exp(-((np.abs(xpf) - 14) / 6) ** 2) * on_pf
            bow = np.exp(-((xpf + 0) / 3.5) ** 2) * on_pf
            buf = buf * (1 - 0.8 * np.clip(ring + bow, 0, 1))[:, None]
            buf += light(WREATH, 0.3 * ring) + light(BOW, 0.32 * bow)
            spill = door_open * np.exp(-(np.abs(pd - door_pd) / 90) ** 2) * (1 - 0.6 * bow)
            buf += light(DOOR, 0.3 * spill)
            out[f] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, NIGHT))


def keys_out(u):
    if u < 1.2:
        return 1 - smoothstep(0, 1.2, u) * 0.97
    if u < 6.2:
        return 0.03
    return 0.03 + 0.97 * smoothstep(6.2, 7.6, u)


# ---- music: an all-night loop in G, soft, with no beat ----
# A warm pad holds slow chords over a faint organ pedal, one voice moving at a time; the chord turns each time the
# front door opens and once between. When the door opens the wreath's bells stir and a harp rolls up a chord from the
# porch; the draught is a breath of air travelling out both ways along the roof, and as it reaches each candle and
# bows it, a celesta note sounds at that window, pitched from the chord by where the window is. When the door closes
# a low harp note settles. A guttering candle is a soft puff and a falling harp note; five seconds later a match is
# struck and the wick catches on a celesta. Twice a loop, in the long quiet, a far music box plays a few slow notes.

MUSIC_SEED = 47
PAD = (                             # pedal, low, three pad voices: one chord per turn
    ('G2', 'D3', 'B3', 'D4', 'G4'),         # G               (from the start)
    ('C2', 'G2', 'B3', 'E4', 'G4'),         # C maj7           (the first door)
    ('E2', 'B2', 'B3', 'D4', 'G4'),         # E m7
    ('A1', 'E2', 'C4', 'E4', 'G4'),         # A m7             (the second door)
    ('D2', 'A2', 'A3', 'D4', 'G4'),         # D sus4
    ('D2', 'A2', 'A3', 'D4', 'F#4'),        # D                (the third door), home to G across the seam
)
TONES = ({7, 11, 2}, {0, 4, 7, 11}, {4, 7, 11, 2}, {9, 0, 4, 7}, {2, 7, 9}, {2, 6, 9})
BOX = ((70.0, ('B4', 'D5', 'G5', 'F#5', 'E5')),       # (when, notes): the music box, far off
       (132.0, ('A4', 'D5', 'E5', 'D5', 'A4', 'G4')))


def light_events(G):
    """The doors and gutterings render() draws, by replaying its random stream."""
    cand, door_pd = candles(G)
    nc = len(cand)
    rng = np.random.default_rng(SEED)
    rng.uniform(46, 60, nc)
    Flicker(rng, nc, 0.08, 0.4)
    Flicker(rng, nc, 0.7, 2.0)
    Flicker(rng, nc, 0.05, 0.15)
    Flicker(rng, G.N, 0.02, 0.08)
    doors, outs = events(rng, LOOP + LOOP_FADE, nc)
    return G.pd[cand], door_pd, doors, outs


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.36, 0.3), ('air', 0.35, 0.15), ('bells', 1.0, 0.45), ('harp', 0.3, 0.4),
                            ('box', 0.35, 0.55), ('fx', 0.4, 0.25)):
        M.bus(name, gain=gain, reverb=rev)
    cpd, door_pd, doors, outs = light_events(G)
    harp = M.sampler('Strings/Harp/*.wav')
    cel = M.synth('Plucks/Fantasy Bell')
    box = M.synth('Plucks/Magic Music Box')
    shake = M.hits('Miscellania Raw/Misc 2/sleighbell1_shake1.wav')
    soft = pb.Pedalboard([pb.LowpassFilter(2600), pb.HighpassFilter(150)])

    pdp = G.pd[G.path]
    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_pd(p):                          # distance along the path -> left/right from the street
        return 0.85 * (2 * (np.interp(p, pdp, xs) - x0) / (x1 - x0) - 1)

    def panned(mono, pan):                  # constant power; pan may be a per-sample array
        a = (np.asarray(pan) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def put(bus, sig, t, gain=1.0):         # add around the loop: whatever passes the end comes in at the start
        s = int(round((t % LOOP) * SR))
        while sig.shape[1]:
            k = min(sig.shape[1], N - s)
            M.add(bus, sig[:, :k], s / SR, gain)
            sig, s = sig[:, k:], 0

    def ramp(n, up):
        u = np.linspace(0, 1, max(n, 1)) if up else np.linspace(1, 0, max(n, 1))
        return np.sin(u * np.pi / 2) ** 2

    def noise(seconds, lo, hi, seed):
        x = np.random.default_rng(seed).normal(0, 1, (1, int(seconds * SR))).astype(np.float32)
        x = pb.Pedalboard([pb.HighpassFilter(lo), pb.LowpassFilter(hi), pb.LowpassFilter(hi * 1.3)])(x, SR)[0]
        return x / (np.abs(x).max() + 1e-9)

    def chord_at(t):
        i = np.searchsorted(turns, t % LOOP, side='right') - 1
        return i % len(PAD)

    def from_chord(i, lo, hi, x):           # a chord tone in [lo, hi], higher the farther right x (0..1)
        pool = [m for m in range(note(lo), note(hi) + 1) if m % 12 in TONES[i]]
        return pool[min(len(pool) - 1, int(x * len(pool)))]

    def bell(inst, m, vel, t, pan, gain, length=0.5, ring=4.0):
        a = inst.render([(0.0, m, vel, length)], ring).astype(np.float32)
        put('bells', panned(soft(a, SR).mean(0), pan), t, gain)

    # ---- the pad: a turn at each door and one between; each voice moves on its own, staggered ----
    d = [ts for ts, _ in doors]
    turns = np.array([5.0, d[0], (d[0] + d[1]) / 2, d[1], (d[1] + d[2]) / 2, d[2]])
    pad = np.zeros((2, N), np.float32)
    voices = [
        (M.synth('Keys/House Organ'), 0, 28, 0.3, 0.0, 0.0),   # (instrument, chord voice, velocity, gain, pan, lag)
        (M.synth('Pads/MKS-70 Warm Pad'), 1, 48, 0.9, 0.25, 3.0),
        (M.synth('Pads/MKS-70 Warm Pad'), 2, 44, 1.0, -0.4, 6.0),
        (M.synth('Pads/MKS-70 Warm Pad'), 3, 42, 1.0, 0.45, 1.5),
        (M.synth('Pads/MKS-70 Warm Pad'), 4, 38, 0.9, -0.1, 9.0),
    ]
    XF = 6.0                                # seconds each note change takes
    for inst, vi, vel, gain, pan, lag in voices:
        merged = []
        for t, m in ((s + lag, c[vi]) for s, c in zip(turns, PAD)):
            if not merged or merged[-1][1] != m:
                merged.append((t, m))
        if len(merged) > 1 and merged[0][1] == merged[-1][1]:   # same note across the seam: one long note
            merged[0] = (merged[-1][0], merged[0][1])
            merged.pop()
        for i, (t, m) in enumerate(merged):
            dur = (merged[(i + 1) % len(merged)][0] - t) % LOOP or LOOP
            length = dur + XF
            a = inst.render([(0.0, note(m), vel, length)], length + 0.5).astype(np.float32)
            k, f = a.shape[1], int(XF * SR)
            env = np.ones(k, np.float32)
            env[:f] = ramp(f, True)
            e = int(length * SR)
            env[e - f:e] = ramp(f, False)
            env[e:] = 0
            idx = (int(round(((t - XF / 2) % LOOP) * SR)) + np.arange(k)) % N
            pad[:, idx] += panned(a.mean(0) * env * gain, pan)
    M.add('pad', pad, 0.0)
    del pad

    # ---- the door opens: the wreath's bells stir, the harp rolls up from the porch, the draught goes out ----
    door_pan = float(pan_pd(door_pd))
    for k, (ts, dur) in enumerate(doors):
        i = chord_at(ts + 0.5)
        sh = shake.play(70)
        put('fx', panned(soft(sh.astype(np.float32), SR).mean(0), door_pan), ts + 0.2, 0.25)
        roll = [m for m in range(note('G2'), note('D5') + 1) if m % 12 in TONES[i]]
        for j, m in enumerate(roll):
            put('harp', panned(harp.play(m, 58 + 2 * j).mean(0), door_pan + 0.03 * (j - len(roll) / 2)),
                ts + 0.3 + 0.11 * j, 0.35)
        low = [m for m in range(note('G1'), note('G2')) if m % 12 == min(TONES[i], key=lambda p: (p - 7) % 12)]
        put('harp', panned(harp.play(low[0] + 12, 52).mean(0), door_pan), ts + dur + 0.6, 0.6)   # it closes
        # the draught: two fronts of air from the door, out along the roof at the speed render() uses
        L = 5.5
        n = int(L * SR)
        tt = np.arange(n) / SR
        for side, sgn in enumerate((-1, 1)):
            air = noise(L, 180, float(rng.uniform(550, 800)), MUSIC_SEED * 100 + 10 * k + side)
            p = np.clip(door_pd + sgn * 260 * np.clip(tt - 0.6, 0, None), 0, G.length)
            env = np.clip((tt - 0.3) / 0.8, 0, 1) ** 2 * np.exp(-np.clip(tt - 1.1, 0, None) / 1.6)
            env *= np.clip((L - tt) / 1.0, 0, 1)
            put('air', panned(air * env, pan_pd(p)), ts, 0.35)
        # each candle bows as the draught reaches it: a celesta note at its window
        for c, ta in enumerate(draught_at(cpd, door_pd, ts)):
            x = (np.interp(cpd[c], pdp, xs) - x0) / (x1 - x0)
            bell(cel, from_chord(chord_at(ta), 'G4', 'D6', x), int(rng.integers(42, 54)), ta + 0.4,
                 float(pan_pd(cpd[c])), 0.5)

    # ---- a candle gutters out, and is relit with a match ----
    for k, (c, ts) in enumerate(outs):
        pan = float(pan_pd(cpd[c]))
        i = chord_at(ts)
        n = int(1.4 * SR)
        tt = np.arange(n) / SR
        puff = noise(1.4, 120, 500, MUSIC_SEED * 7 + k) * np.clip(tt / 0.15, 0, 1) * np.exp(-tt / 0.45)
        put('fx', panned(puff, pan), ts + 0.2, 0.35)
        m = from_chord(i, 'D3', 'D4', 0.5)
        put('harp', panned(harp.play(m, 48).mean(0), pan), ts + 0.3, 0.5)
        fall = max([x for x in range(m - 5, m) if x % 12 in TONES[i]] or [m - 12])     # and falls to the next
        put('harp', panned(harp.play(fall, 42).mean(0), pan), ts + 1.1, 0.4)
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        strike = noise(0.5, 1800, 5000, MUSIC_SEED * 11 + k) * np.exp(-tt / 0.05)
        flare = noise(0.5, 300, 1600, MUSIC_SEED * 13 + k) * np.clip((tt - 0.03) / 0.05, 0, 1) * np.exp(-tt / 0.18)
        put('fx', panned(0.5 * strike + 0.6 * flare, pan), ts + 6.2 - 0.03, 0.3)
        j = chord_at(ts + 6.5)
        root = [mm for mm in range(note('G4'), note('G5')) if mm % 12 == sorted(TONES[j])[0]][0]
        bell(cel, root, 50, ts + 6.5, pan, 0.55)
        bell(cel, root + 7 if (root + 7) % 12 in TONES[j] else root + 12, 40, ts + 7.3, pan, 0.4)

    # ---- the music box, far off in the house ----
    for t0, frag in BOX:
        gaps = rng.uniform(1.6, 2.2, len(frag)) * (1 + 0.1 * np.arange(len(frag)))
        times = np.concatenate([[0], np.cumsum(gaps[:-1])])
        notes = [(float(t), note(m), int(rng.integers(40, 52)), 0.8) for t, m in zip(times, frag)]
        a = box.render(notes, float(times[-1]) + 6.0).astype(np.float32)
        a = pb.Pedalboard([pb.LowpassFilter(2200), pb.HighpassFilter(200)])(a, SR)
        put('box', panned(a.mean(0), float(pan_pd(door_pd + rng.uniform(-150, 150)))), t0)
