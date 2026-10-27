"""Night Light: A star-projector night light sits in the child's room, inside the house below the
roofline. Its shade is a 2-D sheet of cut-out shapes (stars, a crescent moon, hearts) and it turns
slowly. Every pixel looks back at the lamp: its azimuth picks the column of the shade and its
elevation (which depends on how far that wall is from the lamp) picks the row, so the roofline
slices through the projected shapes. Near walls cut high rows, far wing ends cut low ones; the
same star throws a different slice on each wall, and the lamp's slow wobble slides the shapes
up and down between walls. Light falls off with distance from the lamp."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, looped

CODE = 'MO08'
TITLE = 'Night Light'
KIND = 'ambient'
DESCRIPTION = 'A turning star-projector inside the house throws stars, a moon and hearts onto the roofline; each wall slices the shapes at its own distance, so they change shape as they travel.'

FLOOR_COLOR = hexc('#ffa070')
FLOOR = 0.09
LOOP = 160.0
LAMP = np.array([0.0, 60.0, -380.0])


def star(a, b, R):
    rho = np.hypot(a, b)
    ang = np.arctan2(b, a)
    edge = R * (0.45 + 0.55 * np.abs(np.cos(2.5 * ang)) ** 4)
    return smoothstep(edge + 0.025, edge - 0.025, rho)


def moon(a, b, R):
    outer = smoothstep(R + 0.025, R - 0.025, np.hypot(a, b))
    bite = smoothstep(0.8 * R - 0.025, 0.8 * R + 0.025, np.hypot(a - 0.45 * R, b + 0.15 * R))
    return outer * bite


def heart(a, b, R):
    x, y = a / R * 1.25, b / R * 1.25 + 0.25
    f = (x * x + y * y - 1) ** 3 - x * x * y ** 3
    return smoothstep(0.12, -0.12, f)


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    P = G.pos
    rel = P - LAMP
    horiz = np.hypot(rel[:, 0], rel[:, 2])
    phi = np.arctan2(rel[:, 0], rel[:, 2])                 # azimuth round the lamp
    theta = np.arctan2(rel[:, 1], horiz)                  # elevation: high for near walls
    dist = np.linalg.norm(rel, axis=1)
    falloff = np.clip(330.0 / dist, 0.45, 1.0)
    lo, hi = theta.min(), theta.max()
    # the shade: shapes placed round the circle at rows spanning the walls' elevations
    kinds = [star, moon, star, heart, star, star, heart, star, star, moon, star, heart, star, star, heart, star]
    cols = {star: [hexc('#d8b0ff'), hexc('#ffc8e0'), hexc('#fff0e0')], moon: [hexc('#ffe0a8')],
            heart: [hexc('#ff6aa0')]}
    shapes = []
    for k, fn in enumerate(kinds):
        psi = 2 * np.pi * k / len(kinds) + rng.uniform(-0.12, 0.12)
        row = lo + (hi - lo) * rng.uniform(0.15, 0.85)
        R = {star: 0.12, moon: 0.15, heart: 0.12}[fn] * rng.uniform(0.85, 1.15)
        c = cols[fn][rng.integers(len(cols[fn]))]
        shapes.append((fn, psi, row, R, c))
    warm = hexc('#ff9a68')

    def draw(D):
        out = np.zeros((nframes(D), G.N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            spin = 2 * np.pi * t / LOOP                      # one turn per loop
            tilt = 0.06 * np.sin(2 * np.pi * 2 * t / LOOP) + 0.03 * np.sin(2 * np.pi * 3 * t / LOOP + 1)
            fr = light(warm, 0.07 * falloff)                 # glow through the shade
            for fn, psi, row, R, c in shapes:
                a = np.angle(np.exp(1j * (phi - psi - spin)))
                b = theta - row - tilt * np.cos(psi + spin)
                m = fn(a, b, R)
                fr += light(c, 0.34 * m * falloff)
            out[f] = fr
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
