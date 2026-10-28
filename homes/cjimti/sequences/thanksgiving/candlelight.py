"""Candlelight: An all-night table of real candles, not a string of flickering pixels. Each candle is a
small flame with a halo of light scattered onto the pixels around it: a row of them close together
down the Porch Front (the table), pairs in the wing fronts like windows, a few spread along the porch
sides and the Side. Each flame is a little damped pendulum: it breathes on its own, and when someone
walks past, the draft travels along the roof, and each flame in turn leans away, sways and settles,
its light sliding sub-pixel to one side and back."""
import numpy as np
from pixelhome.fx import DT, hexc, light, Flicker, nframes, looped

CODE = 'TG07'
TITLE = 'Candlelight'
KIND = 'ambient'
DESCRIPTION = ('A long table of candles down the porch and in the windows, each with its own halo. When someone '
               'walks past, the draft reaches each flame in turn and it leans, sways and settles.')

CORE = hexc('#ffb060')
HALO = hexc('#ff6a10')
FLOOR_COLOR = hexc('#ff4206')
FLOOR = 0.1
LOOP = 160.0
LOOP_FADE = 12.0                    # looped()'s default head/tail blend
TABLE = list(1335 + 39 * np.arange(9))                                      # Porch Front: the table
WINDOWS = [560, 600, 760, 800, 2120, 2160, 2330, 2370, 2470]               # wing fronts, in pairs
SIDES = [960, 1120, 1250, 1720, 1860, 1990, 90, 230, 370]                   # porch sides and the Side


def _drafts(rng, G, Dt):
    """Someone walks past: (time, start pd, direction, strength); direction 0 is the porch door, both ways."""
    drafts = []
    t = rng.uniform(6, 14)
    while t < Dt:
        kind = rng.integers(0, 3)
        start, d = [(0.0, 1), (G.length, -1), (1486.0, 0)][kind]
        drafts.append((t, start, d, rng.uniform(0.6, 1.0)))
        t += rng.uniform(16, 30)
    return drafts


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N
    C = np.array(sorted(TABLE + WINDOWS + SIDES), float)                   # candle positions along the path
    M = len(C)
    is_table = np.isin(C, TABLE)
    size = np.where(is_table, 1.0, 0.85)

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        breath = Flicker(rng, M, 0.05, 0.3)
        nerve = Flicker(rng, M, 0.4, 0.9)
        x = np.zeros(M)
        v = np.zeros(M)
        w0 = 2 * np.pi * rng.uniform(0.55, 0.8, M)                         # each flame's sway frequency
        zeta = 0.22
        drafts = _drafts(rng, G, Dt)
        dist = np.abs(pdp[None, :] - C[:, None])
        halo_k = np.exp(-dist / 16) * 0.55 + np.exp(-dist / 55) * 0.12
        for f in range(len(out)):
            t = f * DT
            force = np.zeros(M)
            for td, s0, d, a in drafts:
                u = t - td
                if 0 < u < 25:
                    if d == 0:                                               # porch door: spreads both ways
                        front = np.abs(C - s0) - 120 * u
                        sgn = np.sign(C - s0)
                    else:
                        front = (C - s0) * d - 120 * u
                        sgn = d
                    force += a * sgn * np.exp(-(front / 90) ** 2) * np.exp(-u / 14)
            acc = -w0 ** 2 * x - 2 * zeta * w0 * v + 34.0 * force
            v += acc * DT
            x += v * DT
            sway = np.clip(x, -1.5, 1.5)
            I = 0.34 * size * (1 + 0.1 * breath(t) + 0.03 * nerve(t)) * (1 - 0.35 * np.abs(sway) / 1.5)
            lean = 5.0 * sway                                                # sub-pixel lean of the flame
            core = np.exp(-((pdp[None, :] - (C + lean)[:, None]) / 3.0) ** 2)
            flame = (I[:, None] * core).max(0)
            glow = (I[:, None] * halo_k).sum(0)
            col = HALO + (CORE - HALO) * np.clip(flame / 0.34, 0, 1)[:, None]
            out[f][G.path] = light(1.0, np.maximum(flame, glow)) * col
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: an all-night loop, soft and warm ----
# A warm pad holds a slow chord in F under the candles, over a faint reed-organ pedal, and moves on one voice
# at a time each time someone walks past. Each draft is a breath of air that travels across the speakers with
# the front, swelling a little wherever it reaches a run of flames. Three times a loop, between drafts, a far
# upright piano plays a few slow notes from the dinner table.

MUSIC_SEED = 41
CHORDS = (                          # one per draft that starts inside the loop: pedal, low, three pad voices
    ('F2', 'C3', 'A3', 'C4', 'F4'),         # F
    ('F2', 'C3', 'Bb3', 'D4', 'F4'),        # Bb over F
    ('D2', 'A2', 'A3', 'C4', 'F4'),         # Dm7
    ('Bb1', 'F2', 'A3', 'D4', 'F4'),        # Bb maj7
    ('C2', 'G2', 'G3', 'Bb3', 'E4'),        # C7, open
    ('F2', 'C3', 'A3', 'C4', 'E4'),         # F maj7
    ('G2', 'D3', 'Bb3', 'D4', 'F4'),        # Gm7
    ('Bb1', 'F2', 'A3', 'C4', 'F4'),        # Bb maj9 with no third, settling back to F
)
PIANO = (                           # (when, notes): far-off fragments over the chord of the moment
    (49.0, ('A4', 'C5', 'F5', 'E5', 'D5')),
    (107.0, ('C5', 'A4', 'G4', 'A4', 'E5')),
    (134.5, ('G4', 'Bb4', 'D5', 'C5')),
)


def _light_events(G, seed=27):
    """The drafts render() draws, by replaying its random stream."""
    rng = np.random.default_rng(seed)
    M = len(TABLE + WINDOWS + SIDES)
    Flicker(rng, M, 0.05, 0.3)
    Flicker(rng, M, 0.4, 0.9)
    rng.uniform(0.55, 0.8, M)
    return _drafts(rng, G, LOOP + LOOP_FADE)


def _shown(T):
    """How much of render time T reaches the loop (looped() blends 160..172 s into the first 12 s)."""
    T = np.asarray(T, float)
    return np.where(T < LOOP_FADE, np.clip(T / LOOP_FADE, 0, 1),
                    np.where(T < LOOP, 1.0, np.clip(1 - (T - LOOP) / LOOP_FADE, 0, 1)))


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.4, 0.3), ('air', 0.4, 0.15), ('piano', 0.4, 0.55)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]
    C = np.array(sorted(TABLE + WINDOWS + SIDES), float)

    def pan_x(x):
        return 0.85 * (2 * (np.asarray(x, float) - x0) / (x1 - x0) - 1)

    def pan_pd(p):                          # distance along the path -> left/right from the street
        return pan_x(np.interp(p, pdp, xs))

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

    drafts = _light_events(G)

    # ---- the drafts: a front of air along the roof, as in render(), louder where it meets the flames ----
    CR, LIFE = 40, 25.0
    u = np.arange(int(LIFE * CR)) / CR
    fronts = []
    for td, s0, d, a in drafts:
        for sgn in ((1, -1) if d == 0 else (d,)):
            on = (C - s0) * sgn > 0 if d == 0 else np.ones(len(C), bool)
            gap = np.abs(C[on] - s0)[None, :] - 120 * u[:, None]
            flames = np.exp(-(gap / 90) ** 2).sum(1)
            p = s0 + sgn * 120 * u
            inside = np.clip(np.minimum(p, G.length - p) / 250 + 0.4, 0, 1)
            level = a * np.exp(-u / 14) * (0.45 * inside + 0.55 * np.minimum(flames, 2.5) / 2.5)
            level *= np.clip(u / 2.5, 0, 1) ** 2 * (1 - np.clip((u - 19) / 6, 0, 1)) ** 2   # in and out softly
            fronts.append((td, level * _shown(td + u), pan_pd(np.clip(p, 0, G.length))))
    for i, (td, level, pan) in enumerate(fronts):
        n = int(LIFE * SR)
        wr = np.random.default_rng(MUSIC_SEED * 100 + i)
        air = wr.normal(0, 1, (1, n)).astype(np.float32)
        lo = float(wr.uniform(500, 800))
        air = pb.Pedalboard([pb.HighpassFilter(160), pb.LowpassFilter(lo), pb.LowpassFilter(lo * 1.5),
                             pb.LadderFilter(pb.LadderFilter.Mode.BPF12, cutoff_hz=lo * 0.8, resonance=0.2)])(air, SR)[0]
        env = at_rate(np.convolve(level, np.hanning(21) / np.hanning(21).sum(), 'same'), CR, n)
        put('air', panned(air / (np.abs(air).max() + 1e-9) * env, at_rate(pan, CR, n)), td, 0.3)

    # ---- the pad: each voice changes note on its own, staggered after the draft that brings a new chord ----
    seq = sorted(zip((td for td, *_ in drafts if td < LOOP), CHORDS))
    pad = np.zeros((2, N), np.float32)
    voices = [
        (M.synth('Keys/House Organ'), 0, 30, 0.35, 0.0, 0.0),  # (instrument, chord voice, velocity, gain, pan, stagger)
        (M.synth('Pads/MKS-70 Warm Pad'), 1, 50, 0.9, 0.25, 3.0),
        (M.synth('Pads/MKS-70 Warm Pad'), 2, 46, 1.0, -0.4, 7.0),
        (M.synth('Pads/MKS-70 Warm Pad'), 3, 44, 1.0, 0.45, 1.5),
        (M.synth('Pads/MKS-70 Warm Pad'), 4, 40, 0.9, -0.1, 10.0),
    ]
    XF = 6.0                                # seconds each note change takes
    for inst, vi, vel, gain, pan, lag in voices:
        merged = []
        for t, m in ((s + lag, c[vi]) for s, c in seq):
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
    # the flames lean and dim as the air goes by, and the pad sinks with them a little
    stir = np.zeros(int(LOOP * CR))
    for td, level, _ in fronts:
        np.add.at(stir, np.round((td + u) * CR).astype(int) % len(stir), level)
    stir = np.convolve(np.concatenate([stir[-80:], stir, stir[:80]]), np.hanning(161) / np.hanning(161).sum(), 'same')[80:-80]
    pad *= at_rate(1 - 0.2 * stir / (stir.max() + 1e-9), CR, N).astype(np.float32)
    M.add('pad', pad, 0.0)
    del pad

    # ---- the piano: far off at the table, a few slow notes now and then ----
    piano = M.sampler('Keys/Upright Nr1/*_pp_*.wav')
    soften = pb.Pedalboard([pb.LowpassFilter(2200), pb.HighpassFilter(120)])
    for t0, frag in PIANO:
        gaps = rng.uniform(1.5, 2.1, len(frag)) * (1 + 0.12 * np.arange(len(frag)))
        times = np.concatenate([[0], np.cumsum(gaps[:-1])])
        span = float(times[-1]) + 8.0
        buf = np.zeros((2, int(span * SR)))
        for t, m in zip(times, frag):
            a = piano.play(note(m), int(rng.integers(60, 80)), dur=6.5, release=1.5)
            s = int(t * SR)
            k = min(a.shape[1], buf.shape[1] - s)
            buf[:, s:s + k] += a[:, :k]
        buf = soften(buf.astype(np.float32), SR)
        put('piano', panned(buf.mean(0), float(pan_pd(1486 + rng.uniform(-120, 120)))), t0)

