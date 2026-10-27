"""Colonnade: The Lincoln Memorial at night. Thirty-six virtual columns stand in plan: a row along
the street side of the wings and an arc around the court in front of the porch. Two lights cast
their shadows onto the roofline by ray tests against every column: a slow-swinging moon (parallel
light, soft-edged shadows that widen with distance, sliding across the wing fronts), and the warm
glow of the seated statue in the court, whose column shadows fan out as spokes over the porch U."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, Flicker, nframes, looped

CODE = 'PR09'
TITLE = 'Colonnade'
KIND = 'ambient'
DESCRIPTION = ('The Lincoln Memorial at night: thirty-six columns cast moonlight shadows that slide slowly '
               'across the wings, while the statue\'s warm glow fans column shadows over the porch.')

MOON = hexc('#b4c2ff')
WARM = hexc('#ffa850')
MARBLE = hexc('#ffe4c4')
FLOOR_COLOR = hexc('#26349a')
FLOOR = 0.09
LOOP = 170.0


def _shadow(px, pz, cx, cz, r, dx, dz, soft0, soft_k):
    """Light reaching each pixel past discs (cx, cz, r) along unit direction (dx, dz) toward the light.
    dx, dz may be per pixel (point light) or scalars (parallel light)."""
    vx = cx[:, None] - px[None, :]
    vz = cz[:, None] - pz[None, :]
    along = vx * dx + vz * dz                       # distance toward the light
    perp = np.abs(vx * dz - vz * dx)
    soft = soft0 + soft_k * np.clip(along, 0, None)
    block = smoothstep(r[:, None] + soft, r[:, None] - soft, perp) * smoothstep(5, 25, along)
    return np.prod(1 - 0.85 * block, axis=0)


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    px, pz = G.pos[:, 0], G.pos[:, 2]
    # columns: a row in front of each wing, and an arc around the court
    row = np.concatenate([np.linspace(-560, -240, 9), np.linspace(190, 600, 11)])
    rz = np.where(row < 0, -10.0, -50.0)
    statue = np.array([-22.0, -330.0])
    ang = np.linspace(np.pi * 0.08, np.pi * 0.92, 16)
    ax = statue[0] + 135 * np.cos(ang)
    az = statue[1] - 135 * np.sin(ang) + 40
    cx = np.concatenate([row, ax])
    cz = np.concatenate([rz, az])
    cr = np.concatenate([np.full(len(row), 11.0), np.full(16, 9.0)])
    tw = Flicker(rng, G.N, 0.02, 0.08)
    sx, sz = px - statue[0], pz - statue[1]
    dist = np.hypot(sx, sz)
    ldx, ldz = -sx / dist, -sz / dist                # toward the statue

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        # the statue's light does not move: its spokes are fixed, so compute once, then let it breathe
        warm_sh = _shadow(px, pz, cx, cz, cr, ldx, ldz, 2.0, 0.035)
        warm_fall = np.exp(-(dist / 650) ** 2)
        for f in range(len(out)):
            t = f * DT
            # the moon swings slowly from street-left to street-right and back over the loop
            th = np.pi / 2 + 0.75 * np.sin(2 * np.pi * t / LOOP) + 0.12 * np.sin(2 * np.pi * t / 47)
            mdx, mdz = np.cos(th), np.sin(th)        # +z is toward the street, where the moon is
            moon_sh = _shadow(px, pz, cx, cz, cr, mdx, mdz, 1.5, 0.02)
            # walls facing the moon catch more of it (run direction vs light direction)
            mI = 0.22 * moon_sh * (0.9 + 0.1 * tw(t))
            breathe = 1 + 0.06 * np.sin(2 * np.pi * t / 19)
            wI = 0.42 * warm_fall * warm_sh * breathe
            buf = light(MOON, mI) + light(WARM, wI)
            # where both lights land, the marble reads warm white
            buf += light(MARBLE, 0.12 * np.sqrt(np.clip(mI * wI, 0, None)) * 2)
            out[f] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
