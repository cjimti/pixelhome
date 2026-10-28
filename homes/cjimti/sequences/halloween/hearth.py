"""Hearth: Every pixel a candle. Slow gusts of wind roll along the roof, flames dip and recover."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, lerp, Flicker, nframes, looped, candle_bed

CODE = 'NT1'
TITLE = 'Hearth'
KIND = 'ambient'
DESCRIPTION = 'Every pixel a candle. Slow gusts roll along the roof; now and then a flame nearly goes out.'
VOICEOVER = 'The fire is lit, and the night is long. Pull up close to the hearth, and stay as long as you like.'

DEEP_ORANGE = hexc('#ff2800')
AMBER = hexc('#ff7010')
FLOOR_COLOR = hexc('#ff4a08')
FLOOR = 0.13
LOOP = 300.0


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    def draw(D):
        n = G.N
        out = np.zeros((nframes(D), n, 3), np.float32)
        pdp = G.pd[G.path]
        bed = candle_bed(rng, n, 0.3)
        flutter = Flicker(rng, n, 1.5, 3.0)
        gusts = []
        t = rng.uniform(5, 15)
        while t < D:
            gusts.append((t, rng.choice([-1, 1]), rng.uniform(70, 130), rng.uniform(0.25, 0.45)))
            t += rng.uniform(18, 40)
        gutters = [(rng.uniform(0, D), rng.integers(n)) for _ in range(int(D / 6))]
        for f in range(len(out)):
            t = f * DT
            I = bed(t)
            gust = np.zeros(n)
            for tg, d, v, a in gusts:
                front = (t - tg) * v
                x = pdp if d > 0 else G.length - pdp
                gust = np.maximum(gust, a * np.exp(-((x - front) / 220) ** 2))
            I = I * (1 - gust) + 0.04 * gust * flutter(t)
            for tg, k in gutters:
                u = t - tg
                if -0.8 < u < 2.5:
                    I[k] *= 1 - 0.65 * (smoothstep(-0.8, 0, u) if u < 0 else 1 - smoothstep(0, 2.5, u))
            col = lerp(DEEP_ORANGE, AMBER, np.clip((I - 0.15) / 0.2, 0, 1)[:, None])
            out[f][G.path] = perc(I)[:, None] * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: an all-night loop, soft and low ----
# A reed-organ drone (harmonium voices over a soft house-organ pedal) moves through seven slow chords in D
# minor, one voice at a time, each change setting off as a gust arrives on the roof. Every gust is a breath of
# wind that travels across the speakers with the dimming front, and the drone sinks a little under it, the way
# the flames dip. Each guttering candle sputters with a few faint crackles from where it is on the house, over a
# bed of hearth crackle. Five times a loop, from a candle that nearly goes out, a far music box plays a
# fragment, a little flat, winding down and sagging in pitch, and stops before it resolves.

MUSIC_SEED = 23
GUST_WIDTH = 220.0                  # the gust's width along the path, as in render()
LOOP_FADE = 12.0                    # looped()'s default head/tail blend
CHANGES = (303.6, 58.8, 94.5, 133.3, 169.1, 218.7, 260.5)   # gusts that carry the harmony on (times in render)
CHORDS = (                          # pedal, low, three reeds
    ('D2', 'A2', 'F3', 'A3', 'E4'),         # Dm add9
    ('D2', 'A2', 'F3', 'Bb3', 'D4'),        # Bb over D
    ('D2', 'G2', 'F3', 'Bb3', 'D4'),        # Gm7 over D
    ('Bb1', 'F2', 'F3', 'A3', 'D4'),        # Bb maj7
    ('A1', 'E2', 'E3', 'G3', 'C4'),         # Am7: the dominant without its leading note
    ('Bb1', 'F2', 'D3', 'G3', 'C4'),        # Bb add9, a shadow of Gm
    ('D2', 'A2', 'E3', 'G3', 'C4'),         # D with no third, hanging, back into Dm
)
FRAGMENTS = (                       # music-box fragments; none comes home
    ('A4', 'D5', 'E5', 'F5', 'E5'),
    ('D5', 'F5', 'A5', 'G5', 'F5', 'E5'),
    ('A4', 'D5', 'F5', 'E5', 'D5', 'C#5'),
    ('F5', 'E5', 'D5', 'A4', 'Bb4'),
    ('D5', 'E5', 'F5', 'G5', 'A5', 'G5'),
)
BOX_AT = (34.0, 92.0, 151.0, 205.0, 266.0)  # roughly when; each plays at the nearest guttering candle


def _light_events(G, seed=11):
    """The gusts and gutters render() draws, by replaying its random stream."""
    rng = np.random.default_rng(seed)
    n, D = G.N, LOOP + LOOP_FADE
    candle_bed(rng, n, 0.3)
    Flicker(rng, n, 1.5, 3.0)
    gusts = []
    t = rng.uniform(5, 15)
    while t < D:
        gusts.append((t, rng.choice([-1, 1]), rng.uniform(70, 130), rng.uniform(0.25, 0.45)))
        t += rng.uniform(18, 40)
    gutters = [(rng.uniform(0, D), rng.integers(n)) for _ in range(int(D / 6))]
    return gusts, gutters


def _shown(T):
    """How much of render time T reaches the loop (looped() blends 300..312 s into the first 12 s)."""
    T = np.asarray(T, float)
    return np.where(T < LOOP_FADE, np.clip(T / LOOP_FADE, 0, 1), np.where(T < LOOP, 1.0, np.clip(1 - (T - LOOP) / LOOP_FADE, 0, 1)))


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('drone', 0.6, 0.3), ('wind', 0.5, 0.12), ('crackle', 1.5, 0.08), ('box', 0.85, 0.55)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]

    def pan_x(x):
        return 0.85 * (2 * (np.asarray(x, float) - x0) / (x1 - x0) - 1)

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

    def at_rate(ctl, rate, n):              # control signal -> sample rate
        return np.interp(np.arange(n) / SR, np.arange(len(ctl)) / rate, ctl)

    gusts, gutters = _light_events(G)

    # ---- the gusts: how much of the house each one dims, and where it is, 20 times a second ----
    CR = 20
    cover_total = np.zeros(int(LOOP * CR))
    winds = []
    for tg, d, v, a in gusts:
        T = tg + np.arange(int((G.length + 4 * GUST_WIDTH) / v * CR)) / CR
        front = (T - tg) * v
        x = pdp if d > 0 else G.length - pdp
        g = a * np.exp(-((x[None, :] - front[:, None]) / GUST_WIDTH) ** 2)
        cover = g.mean(1) * _shown(T)
        where = (g * xs[None, :]).sum(1) / (g.sum(1) + 1e-9)
        winds.append((tg, cover, pan_x(where)))
        np.add.at(cover_total, (np.round(T * CR).astype(int)) % len(cover_total), cover)
    cmax = max(c.max() for _, c, _ in winds)

    # ---- wind: soft band-passed air that crosses the house with each gust ----
    for i, (tg, cover, pan) in enumerate(winds):
        n = int(len(cover) / CR * SR)
        wr = np.random.default_rng(MUSIC_SEED * 100 + i)
        air = wr.normal(0, 1, (1, n)).astype(np.float32)
        lo = float(wr.uniform(380, 620))
        air = pb.Pedalboard([pb.HighpassFilter(140), pb.LowpassFilter(lo), pb.LowpassFilter(lo * 1.6),
                             pb.LadderFilter(pb.LadderFilter.Mode.BPF12, cutoff_hz=lo * 0.8, resonance=0.25)])(air, SR)[0]
        sway = 1 + 0.35 * np.sin(2 * np.pi * np.cumsum(at_rate(wr.uniform(0.08, 0.2, 8), 8 / (n / SR), n)) / SR
                                 + wr.uniform(0, 6.3))
        env = at_rate((cover / cmax) ** 1.3, CR, n) * sway
        sig = panned(air / (np.abs(air).max() + 1e-9) * env, at_rate(pan, CR, n))
        put('wind', sig, tg, 0.2)

    # ---- the drone: each voice changes note on its own, staggered after the gust that brings a new chord ----
    seq = sorted(zip((float(c % LOOP) for c in CHANGES), CHORDS))
    drone = np.zeros((2, N), np.float32)
    voices = [
        (M.synth('Keys/House Organ'), 0, 34, 0.4, -0.15, 0.0),  # (instrument, chord voice, velocity, gain, pan, stagger)
        (M.synth('Winds/Low'), 1, 44, 0.8, 0.2, 4.0),
        (M.synth('Winds/Low'), 2, 40, 1.0, -0.35, 9.0),
        (M.synth('Winds/Low'), 3, 36, 1.0, 0.4, 2.0),
        (M.synth('Winds/Low'), 4, 30, 0.9, -0.05, 13.0),
    ]
    halo = M.synth('Pads/Ghost Pad')
    XF = 6.0                                # seconds each note change takes
    for inst, vi, vel, gain, pan, lag in voices:
        notes = [(s + lag, c[vi]) for s, c in seq]
        merged = []
        for t, m in notes:
            if merged and merged[-1][1] == m:
                continue
            merged.append((t, m))
        if len(merged) > 1 and merged[0][1] == merged[-1][1]:   # same note across the seam: one long note
            merged[0] = (merged[-1][0], merged[0][1])
            merged.pop()
        for i, (t, m) in enumerate(merged):
            nxt = merged[(i + 1) % len(merged)][0]
            dur = (nxt - t) % LOOP or LOOP
            on, length = t - XF / 2, dur + XF
            a = inst.render([(0.0, note(m), vel, length)], length + 0.5).astype(np.float32)
            k, f = a.shape[1], int(XF * SR)
            env = np.ones(k, np.float32)
            env[:f] = ramp(f, True)
            e = int(length * SR)
            env[e - f:e] = ramp(f, False)
            env[e:] = 0
            sig = panned(a.mean(0) * env * gain, pan)
            s = int(round((on % LOOP) * SR))
            idx = (s + np.arange(k)) % N
            drone[:, idx] += sig
    # the halo: a ghostly pad over the upper reeds, swelling up in the middle of each chord and away again
    for i, (s, c) in enumerate(seq):
        nxt = seq[(i + 1) % len(seq)][0]
        dur = (nxt - s) % LOOP
        on, length = s + 0.2 * dur, 0.6 * dur
        for m, p in ((c[3], 0.5), (c[4], -0.5)):
            a = halo.render([(0.0, note(m) + 12, 40, length)], length + 4).mean(0).astype(np.float32)
            k = len(a)
            u = np.arange(k) / SR / length
            env = (np.sin(np.pi * np.clip(u, 0, 1)) ** 2).astype(np.float32)
            idx = (int(round((on % LOOP) * SR)) + np.arange(k)) % N
            drone[:, idx] += panned(a * env, p) * 0.55
    # the flames dip under the wind, and so does the drone
    dip = cover_total / (cover_total.max() + 1e-9)
    dip = np.convolve(np.concatenate([dip[-40:], dip, dip[:40]]), np.hanning(81) / np.hanning(81).sum(), 'same')[40:-40]
    drone *= at_rate(1 - 0.28 * dip, CR, N).astype(np.float32)
    M.add('drone', drone, 0.0)
    del drone

    # ---- crackle: a faint bed, and a sputter from each candle that gutters ----
    crack = np.zeros((2, N), np.float32)

    def click(amp, pos, pan):
        L = int(rng.uniform(0.0015, 0.005) * SR)
        b = np.clip(rng.normal(0, 1, L), -2, 2) * np.exp(-np.arange(L) / (rng.uniform(0.0006, 0.002) * SR))
        idx = (pos + np.arange(L)) % N
        crack[:, idx] += panned(b * amp, pan)

    rate = 1 + 0.8 * np.sin(2 * np.pi * np.arange(N // SR) / LOOP * 3 + 1.3) * np.sin(2 * np.pi * np.arange(N // SR) / LOOP * 7)
    for sec in range(N // SR):
        for _ in range(rng.poisson(2.2 * rate[sec])):
            click(0.03 * min(3.0, rng.lognormal(0, 0.5)), int((sec + rng.uniform()) * SR), rng.uniform(-0.8, 0.8))
    for tg, k in gutters:
        w = float(_shown(tg))
        if w < 0.05:
            continue
        p = float(pan_x(xs[k]))
        for _ in range(int(rng.integers(4, 9))):
            click(0.06 * w * min(2.5, rng.lognormal(0, 0.4)), int(((tg + rng.uniform(-0.7, 1.2)) % LOOP) * SR), p)
        hl = int(0.6 * SR)                  # the wick's little hiss as it nearly goes out
        hiss = rng.normal(0, 1, hl) * np.sin(np.pi * np.arange(hl) / hl) ** 2 * 0.025 * w
        idx = (int(((tg - 0.5) % LOOP) * SR) + np.arange(hl)) % N
        crack[:, idx] += panned(hiss, p)
    crack = pb.Pedalboard([pb.HighpassFilter(500), pb.LowpassFilter(3200)])(crack, SR)
    M.add('crackle', crack, 0.0)
    del crack

    # ---- the music box: far off, a little flat, winding down; it never reaches the tonic ----
    box = M.synth('Plucks/Magic Music Box')
    soften = pb.Pedalboard([pb.LowpassFilter(3000), pb.HighpassFilter(250)])
    for j, (want, frag) in enumerate(zip(BOX_AT, FRAGMENTS)):
        tg, k = min(gutters, key=lambda g: abs((g[0] % LOOP) - want))
        t0 = tg % LOOP + 1.5
        gaps = 0.62 * (1 + 0.16 * np.arange(len(frag))) ** 1.6 * rng.uniform(0.9, 1.1, len(frag))
        times = np.concatenate([[0], np.cumsum(gaps[:-1])])
        notes = [(float(t), note(m), int(rng.integers(44, 56)), 0.4) for t, m in zip(times, frag)]
        span = float(times[-1]) + 9.0
        a = box.render(notes, span).mean(0)
        u = np.arange(len(a)) / SR
        cents = -22 - 12 * j % 17 - 28 * np.clip(u / times[-1], 0, 1) ** 2 + 6 * np.sin(2 * np.pi * 0.37 * u)
        pos = np.cumsum(2 ** (cents / 1200))
        pos = pos[pos < len(a) - 1]
        a = np.interp(pos, np.arange(len(a)), a).astype(np.float32)
        a = soften(a[None, :], SR)[0]
        put('box', panned(a, 0.8 * float(pan_x(xs[k]))), t0)
