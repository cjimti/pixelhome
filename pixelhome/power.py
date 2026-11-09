"""Night power: every all-night loop draws half of what it was composed to draw, by moving the light rather than
dimming the house. The porch is the light that matters at night, so it keeps the piece as written. The wings and
Side thin out to one pixel in COMB, which always shows the piece, and to a soft pool on each run that drifts slowly
along it and lets the piece through as it passes. The pools are as wide as the budget allows. A piece that lives
mostly on the porch has too little on the wings to save, so only then does the porch come down as well.

Channels are linear on this controller (gamma 1.0), so the sum of a frame's PWM values is proportional to its draw."""
import zlib
import numpy as np
from .fx import DT

NIGHT_SHARE = 0.49              # of what the loop draws as composed (a hair under half, so 8-bit rounding can't cross it)
DAY_PLAYLIST = 'daytime'        # composed to its own budget (daytime/daylight.py)
PORCH = ('Porch Left', 'Porch Front', 'Porch Right')
WINGS = ('Left', 'Right', 'Side')
COMB = 10                       # every COMB-th wing pixel stays on
POOL_MIN, POOL_MAX = 12.0, 260.0    # pool width, layout units
POOL_TRAVERSE = 40.0            # seconds for a pool to cross its run


def is_night_loop(s):
    return s.kind == 'ambient' and s.playlist != DAY_PLAYLIST


def night(G, frames, key):
    """frames (F, N, 3) -> the same piece at NIGHT_SHARE of its draw. Periodic gate, so a seamless loop stays seamless.
    key (the sequence id) varies the pools from piece to piece, deterministically."""
    if not all(n in G.seg for n in PORCH + WINGS):
        return frames
    frames = np.clip(frames, 0, 1)
    F = len(frames)
    rng = np.random.default_rng(zlib.crc32(key.encode()))
    porch = np.concatenate([G.seg[n] for n in PORCH])
    wings = np.concatenate([G.seg[n] for n in WINGS])
    t = np.arange(F)
    cycles = max(1, round(F * DT / (2 * POOL_TRAVERSE)))         # a whole number of there-and-backs per loop
    runs, offset = [], 0
    for name in WINGS:
        n = len(G.seg[name])
        d = G.pd[G.seg[name]]
        mid, half = (d.min() + d.max()) / 2, (d.max() - d.min()) / 2
        c = mid + half * np.sin(2 * np.pi * cycles * t / F + rng.uniform(0, 2 * np.pi))
        runs.append((offset, offset + n, d, c))
        offset += n
    comb = np.isin(G.pi[wings] % COMB, COMB // 2)

    def gate(width):
        g = np.empty((F, len(wings)), np.float32)
        for a, b, d, c in runs:
            g[:, a:b] = np.exp(-((d[None, :] - c[:, None]) / width) ** 2)
        g[:, comb] = 1
        return g

    draw = frames[:, wings].sum(2, dtype=np.float64)
    wing_draw = lambda width: float((draw * gate(width)).sum())
    porch_draw = float(frames[:, porch].sum())
    room = NIGHT_SHARE * float(frames.sum())

    if porch_draw + wing_draw(POOL_MIN) > room:         # too much of the piece is on the porch: it comes down too
        width = POOL_MIN
        porch_gain = max(0.0, (room - wing_draw(width)) / max(porch_draw, 1e-9))
    else:
        porch_gain, lo, hi = 1.0, POOL_MIN, POOL_MAX
        if porch_draw + wing_draw(hi) <= room:
            lo = hi
        for _ in range(14):
            mid = (lo + hi) / 2
            if porch_draw + wing_draw(mid) <= room:
                lo = mid
            else:
                hi = mid
        width = lo
    out = frames.copy()
    out[:, porch] *= porch_gain
    out[:, wings] *= gate(width)[..., None]
    return out
