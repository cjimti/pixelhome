"""Shared helpers. Colours are PWM values (what the pixel is driven at); intensities are perceptual."""
import numpy as np

FPS = 40
DT = 1.0 / FPS
GAMMA = 2.2


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def perc(i):
    """Perceptual intensity (0..1, may exceed) -> PWM multiplier."""
    return np.clip(i, 0, None) ** GAMMA


def light(color, intensity):
    """(N,3) PWM contribution of `color` at per-pixel perceptual `intensity`."""
    return perc(np.asarray(intensity, float))[..., None] * color


def smoothstep(e0, e1, x):
    u = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0, 1)
    return u * u * (3 - 2 * u)


def keys(t, pts):
    """Eased keyframe interpolation. pts = [(time, value), ...]; values may be arrays."""
    ts = [p[0] for p in pts]
    if t <= ts[0]:
        return pts[0][1]
    if t >= ts[-1]:
        return pts[-1][1]
    i = int(np.searchsorted(ts, t, side='right')) - 1
    u = (t - ts[i]) / (ts[i + 1] - ts[i])
    u = u * u * (3 - 2 * u)
    a, b = np.asarray(pts[i][1], float), np.asarray(pts[i + 1][1], float)
    return a + (b - a) * u


def lerp(a, b, u):
    return a + (b - a) * u


def heartbeat(t, t0, period):
    """Lub-dub envelope, 0..1."""
    if t < t0:
        return 0.0
    ph = (t - t0) % period
    return float(np.exp(-((ph - 0.03) / 0.05) ** 2) + 0.7 * np.exp(-((ph - 0.25) / 0.06) ** 2))


def smooth_noise(rng, coords, scale, octaves=2):
    """Spatially smooth noise in [-1,1] over 1-D coords (interpolated random lattice)."""
    out = np.zeros_like(coords, float)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = scale / (2 ** o)
        lo = coords.min()
        n = int((coords.max() - lo) / s) + 3
        lattice = rng.uniform(-1, 1, n)
        out += amp * np.interp((coords - lo) / s, np.arange(n), lattice)
        total += amp
        amp *= 0.5
    return out / total


class Flicker:
    """Per-pixel flicker: sum of sines with random frequencies/phases, in [-1,1]."""

    def __init__(self, rng, n, fmin, fmax, k=3):
        self.f = rng.uniform(fmin, fmax, (k, n))
        self.p = rng.uniform(0, 2 * np.pi, (k, n))

    def __call__(self, t):
        return np.sin(2 * np.pi * self.f * t + self.p).mean(0) * np.sqrt(self.f.shape[0])


def colormap(stops):
    """stops: [(value, (r,g,b)), ...] -> function(values) -> (N,3) PWM."""
    xs = np.array([s[0] for s in stops], float)
    cs = np.array([s[1] for s in stops], float)

    def f(v):
        v = np.asarray(v, float)
        return np.stack([np.interp(v, xs, cs[:, c]) for c in range(3)], -1)
    return f


def to_bytes(frames):
    """(F,N,3) float PWM -> (F, N*3) uint8 in controller channel order."""
    f = np.clip(frames, 0, 1) * 255 + 0.5
    return f.astype(np.uint8).reshape(frames.shape[0], -1)


def to_bytes_dithered(frames):
    """Like to_bytes, but carries each channel's rounding error into the next frame so very dim
    fades stay smooth instead of stepping between adjacent 8-bit levels."""
    flat = frames.reshape(frames.shape[0], -1)
    out = np.empty(flat.shape, np.uint8)
    err = np.zeros(flat.shape[1])
    for f in range(len(flat)):
        v = np.clip(flat[f], 0, 1) * 255 + err
        q = np.clip(np.floor(v + 0.5), 0, 255)
        err = v - q
        out[f] = q
    return out


def nframes(dur):
    return int(round(dur / DT))


def catmull_closed(points, u):
    """Closed Catmull-Rom spline through points (K,3); u in [0,1)."""
    K = len(points)
    s = (u % 1) * K
    i = int(s)
    f = s - i
    p0, p1, p2, p3 = (points[(i + k) % K] for k in (-1, 0, 1, 2))
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f ** 2 +
                  (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def looped(render, D, fade=12.0, floor=None):
    """Render D+fade seconds and blend the tail into the head so frame D-1 flows into frame 0.
    floor: optional (perceptual level, colour) that every pixel is kept at or above."""
    frames = render(D + fade)
    n, c = nframes(D), nframes(fade)
    w = np.linspace(0, 1, c, endpoint=False)[:, None, None]
    frames[:c] = frames[:c] * w + frames[n:n + c] * (1 - w)
    frames = frames[:n]
    if floor is not None:
        np.maximum(frames, perc(floor[0]) * floor[1], out=frames)
    return frames


def candle_bed(rng, n, level, depth=0.12):
    """Slow candle-like breathing per pixel (mostly < 1 Hz, a touch of 1-2 Hz)."""
    slow = Flicker(rng, n, 0.05, 0.35)
    mid = Flicker(rng, n, 0.6, 1.8)
    return lambda t: level * (1 + depth * slow(t) + 0.3 * depth * mid(t))
