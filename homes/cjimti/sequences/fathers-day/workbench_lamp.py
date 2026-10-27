"""Workbench Lamp: late in the garage. A shaded work lamp hangs on a long cord above the porch notch
and swings: a real 2-D pendulum (slightly different stiffness each way, so the swing slowly turns
from a line into an ellipse and back), with damping, and now and then Dad bumps it with his head.
The shade follows the cord, so its warm cone of light slides over the roof by more than the bulb
moves. Between the bulb and the roof hang the slats of a storage shelf; their shadows are projected
from the bulb's real position, so they slide across the runs the opposite way, with parallax.
Sawdust drifts down through the beam and glints only while it is inside the cone."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'FA10'
TITLE = 'Workbench Lamp'
KIND = 'ambient'
DESCRIPTION = ('A work lamp swinging on its cord over the garage: its warm cone slides across the roof, shelf '
               'shadows slide the other way, sawdust glints in the beam, and now and then Dad bumps it.')

DARK = hexc('#1a2238')
TUNGSTEN = hexc('#ffb868')
EDGE = hexc('#ff8a38')
DUST = hexc('#fff0d0')
FLOOR = 0.1
LOOP = 160.0
CAP = 0.43


def render(G, seed=33):
    rng = np.random.default_rng(seed)
    n = G.N
    P = G.pos
    pivot = np.array([-20.0, 1330.0, -380.0])
    cord = 900.0
    w = 2 * np.pi / 7.5                                  # ~7.5 s swing (a long cord)
    wx, wz = w, w * 1.035                                # a little anisotropy: the orbit precesses
    gamma = 0.035
    # head bumps: (time, impulse vx, vz) - spread through the loop
    bumps = [(6.0, 110, 30), (52.0, -50, 120), (98.0, 120, -70), (131.0, -100, -30)]
    slats_x = np.arange(-700, 701, 150.0)                # shelf slats run front-to-back at y = 400
    slat_y, slat_w = 300.0, 14.0
    M = 70

    def draw(D):
        F = nframes(D)
        out = np.zeros((F, n, 3), np.float32)
        # pendulum, integrated once (small-angle, horizontal offsets of the bulb)
        sx, sz, vx, vz = 60.0, 0.0, 0.0, 30.0
        ox = np.zeros(F); oz = np.zeros(F)
        for f in range(F):
            t = f * DT
            tl = t % LOOP
            for tb, ix, iz in bumps:
                if tb <= tl < tb + DT:
                    vx += ix; vz += iz
            ax = -wx ** 2 * sx - 2 * gamma * vx
            az = -wz ** 2 * sz - 2 * gamma * vz
            vx += ax * DT; vz += az * DT
            sx += vx * DT; sz += vz * DT
            ox[f], oz[f] = sx, sz
        # sawdust motes: drift down slowly through the space under the lamp, wrapping to the top
        m0 = np.column_stack([rng.uniform(-650, 650, M), rng.uniform(0, 1, M), rng.uniform(-680, -80, M)])
        fall = rng.uniform(6, 14, M)
        drift = rng.uniform(-6, 6, (M, 2))
        spin = rng.uniform(0.3, 1.2, M)
        sph = rng.uniform(0, 2 * np.pi, M)
        hum = Flicker(rng, n, 0.05, 0.2)

        for f in range(F):
            t = f * DT
            bulb = pivot + np.array([ox[f], -np.sqrt(max(cord ** 2 - ox[f] ** 2 - oz[f] ** 2, 1.0)), oz[f]])
            axis = (bulb - pivot) / cord                 # the shade points along the cord
            v = P - bulb
            dist = np.linalg.norm(v, axis=1)
            cosang = (v @ axis) / dist
            cone = smoothstep(np.cos(np.radians(62)), np.cos(np.radians(12)), cosang) ** 1.5
            fall_off = 1 / (1 + (dist / 1100) ** 2)
            I = 0.36 * cone * fall_off / (1 / (1 + (750 / 1100) ** 2))
            # shelf slat shadows, projected from the bulb onto each pixel
            u = (slat_y - bulb[1]) / (P[:, 1] - bulb[1])
            qx = bulb[0] + (P[:, 0] - bulb[0]) * u
            dq = np.min(np.abs(qx[:, None] - slats_x[None]), axis=1)
            shade = 1 - 0.55 * smoothstep(slat_w * 1.6, 0.0, dq)
            I = I * shade
            col = lerp(EDGE, TUNGSTEN, cone[:, None])
            buf = light(DARK, (0.13 + 0.01 * hum(t)) * np.ones(n))
            buf += light(col, np.clip(I, 0, CAP))
            # sawdust glinting in the cone
            yy = 300 - ((m0[:, 1] * 300 + fall * t) % 300)
            mp = np.column_stack([m0[:, 0] + drift[:, 0] * np.sin(0.03 * t + sph) * 8 + 40 * np.sin(0.05 * t + sph),
                                  yy, m0[:, 2] + 40 * np.cos(0.04 * t + sph)])
            mv = mp - bulb
            mcos = (mv @ axis) / np.linalg.norm(mv, axis=1)
            inbeam = smoothstep(np.cos(np.radians(50)), np.cos(np.radians(30)), mcos)
            glint = inbeam * (0.5 + 0.5 * np.sin(2 * np.pi * spin * t + sph)) ** 3
            d2 = (P[:, None, 0] - mp[None, :, 0]) ** 2 + (P[:, None, 2] - mp[None, :, 2]) ** 2
            buf += light(DUST, np.clip((glint[None] * np.exp(-d2 / 14 ** 2)).sum(1) * 0.3, 0, 0.3))
            out[f] = np.minimum(buf, perc(CAP))
        return out

    return looped(draw, LOOP, floor=(FLOOR, DARK))
