"""Earth, Stone, Water, Sky: A slow living pattern runs along the whole roofline: a Gray-Scott
reaction-diffusion simulated on the continuous path (one cell every 5 units, so it is even across
runs of different spacing, with closed ends at the two free ends). Bands form, split, drift and fade
like banded sandstone being laid down and worn away. The feed rate changes slowly with time and with
depth into the yard (the porch walls run back into it), so the bands near the porch behave
differently from those on the wings, and now and then a drop of water lands and starts a new band.
Colour follows concentration through the colours of the land: umber earth, ochre, red sandstone,
slate, river teal; on the back of the house the bare ground leans toward a dusk-sky blue.
A seamless all-night loop."""
import numpy as np
from pixelhome.fx import DT, hexc, light, lerp, smoothstep, nframes, looped, colormap

CODE = 'OT30'
TITLE = 'Earth, Stone, Water, Sky'
KIND = 'ambient'
DESCRIPTION = ('A slow reaction-diffusion pattern runs along the roof: bands form, split and fade like '
               'layered sandstone, in umber, ochre, red rock, slate and river teal.')

LAND = colormap([(0.0, hexc('#5a2a12')), (0.06, hexc('#a0581e')), (0.14, hexc('#d08a3a')),
                 (0.22, hexc('#b8482a')), (0.29, hexc('#6a7a8a')), (0.36, hexc('#2a8a9a'))])
SKY = hexc('#2a3a7a')
LOOP = 170.0
CELL = 5.0
STEPS = 4                                   # simulation steps per frame


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    n = int(G.length / CELL) + 2
    cell_d = np.arange(n) * CELL
    # depth of each cell into the yard (0 front .. 1 back), for a feed rate that varies with place
    order = np.argsort(G.pd)
    depth_px = (G.pos[:, 2].max() - G.pos[:, 2]) / (G.pos[:, 2].max() - G.pos[:, 2].min())
    depth = np.interp(cell_d, G.pd[order], depth_px[order])
    back_px = smoothstep(0.55, 1.0, depth_px)
    Du, Dv = 0.4, 0.2

    def draw(Dur):
        out = np.zeros((nframes(Dur), G.N, 3), np.float32)
        u = np.ones(n)
        v = np.zeros(n)
        for c in rng.integers(10, n - 10, 10):
            v[c - 3:c + 3] = 0.5
            u[c - 3:c + 3] = 0.5
        drops = sorted(rng.uniform(0, Dur, int(Dur / 14)))
        drop_at = rng.integers(5, n - 5, len(drops))
        lu = np.empty(n)
        lv = np.empty(n)

        def feed(t):
            ph = 2 * np.pi * t / LOOP
            return (0.035 + 0.008 * np.sin(ph + 2.5 * depth) + 0.004 * np.sin(3 * ph + 1.0)
                    + 0.003 * np.cos(cell_d / 300 + 2 * ph))

        def step(Fr, k):
            nonlocal u, v
            lu[1:-1] = u[2:] + u[:-2] - 2 * u[1:-1]
            lu[0], lu[-1] = u[1] - u[0], u[-2] - u[-1]
            lv[1:-1] = v[2:] + v[:-2] - 2 * v[1:-1]
            lv[0], lv[-1] = v[1] - v[0], v[-2] - v[-1]
            uvv = u * v * v
            u += Du * lu - uvv + Fr * (1 - u)
            v += Dv * lv + uvv - (Fr + k) * v

        for _ in range(6000):                     # let the pattern form before the first frame
            step(feed(0.0), 0.06)
        di = 0
        vs = v.copy()
        for f in range(len(out)):
            t = f * DT
            Fr = feed(t)
            k = 0.06 + 0.0015 * np.sin(2 * np.pi * t / LOOP * 2)
            for _ in range(STEPS):
                step(Fr, k)
            while di < len(drops) and drops[di] <= t:
                c = drop_at[di]
                v[c - 2:c + 3] = np.maximum(v[c - 2:c + 3], 0.45)
                u[c - 2:c + 3] = 0.5
                di += 1
            vs = vs + (v - vs) * 0.08               # a little temporal smoothing, nothing snaps
            vp = np.interp(G.pd, cell_d, vs)
            col = LAND(vp)
            bare = smoothstep(0.05, 0.0, vp) * back_px
            col = lerp(col, SKY, (0.6 * bare)[:, None])
            I = 0.15 + 0.6 * np.clip(vp, 0, 0.4)
            out[f] = light(col, I) / np.maximum(col.max(1, keepdims=True), 1e-6)
        return out
    return looped(draw, LOOP, floor=(0.1, hexc('#5a2a12')))
