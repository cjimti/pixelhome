"""Gettysburg Dawn: A quiet sunrise over the field, computed rather than painted. The sun's colour
comes from its path length through the air (blue scattered out first, so the first light is deep red
and warms to cream as it climbs). A ridge to the east holds the shadow back, so first light lands on
the right free end and the terminator walks west. Ground mist drifts in the hollows and glows by
forward scattering where the street looks toward the sun, then burns off. Around the porch U, the
semicircle of the cemetery, small marble markers catch the light one by one; at the end they are
all that stays lit."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'PR07'
TITLE = 'Gettysburg Dawn'
KIND = 'show'
DESCRIPTION = ('A sunrise over the field: first light deep red at the east end, the shadow line walking west, '
               'mist glowing and burning off, and marble markers around the porch catching the light.')

NIGHT = hexc('#0c1650')
BLUE = hexc('#3048b8')
DAWNSKY = hexc('#6a78d0')
ROSE = hexc('#d04050')
MARBLE = hexc('#fff0dc')
STAR = hexc('#c8d4ff')


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 80.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    x, z = P[:, 0], P[:, 2]
    beta = np.array([1.0, 1.95, 4.3]) * 0.06               # ~ wavelength^-4 for R, G, B
    az = np.array([1.0, -0.45]) / np.hypot(1.0, 0.45)       # sun bearing in plan: east and a little back
    viewer = np.array([0.0, 150.0, 1300.0])
    vdir = P - viewer
    vdir /= np.linalg.norm(vdir, axis=1, keepdims=True)
    # eastern ridge: the horizon angle each pixel has to clear (lower toward the east), slightly rough
    k = rng.uniform(0.004, 0.012, 4)
    ph = rng.uniform(0, 6.3, 4)
    rough = sum(np.sin(x * k[i] + z * k[i] * 0.6 + ph[i]) for i in range(4)) / 4
    horizon = 0.13 * smoothstep(700, -650, x) + 0.012 * rough
    # mist: drifting density in plan
    mk = rng.uniform(0.004, 0.011, (5, 2)) * rng.choice([-1, 1], (5, 2))
    mph = rng.uniform(0, 6.3, 5)
    mv = rng.uniform(0.08, 0.2, 5) * rng.choice([-1, 1], 5)
    # markers: every third pixel around the porch U
    pidx = np.arange(G.N)
    marker = np.zeros(G.N)
    for i in range(184, 377, 3):
        marker[G.path[i]] = 1.0
    m_h = horizon + marker * rng.uniform(0.0, 0.05, G.N)    # each marker clears the ridge on its own
    ck = rng.uniform(0.003, 0.006, (3, 2)) * rng.choice([-1, 1], (3, 2))
    cph = rng.uniform(0, 6.3, 3)
    stars = np.zeros(G.N)
    sp = rng.choice(G.N, 26, replace=False)
    stars[sp] = rng.uniform(0.3, 0.6, 26)
    twinkle = Flicker(rng, G.N, 0.1, 0.4)
    shim = Flicker(rng, G.N, 0.05, 0.2)

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        el = keys(t, [(0, -0.2), (22, 0.0), (70, 0.36)]) if t < 22 else -0.0 + 0.36 * ((t - 22) / 48) ** 0.85
        el = float(min(el, 0.4))
        fade = keys(t, [(0, 0), (3, 1), (D, 1)])
        # skylight (scattered blue), brightening through the blue hour
        u = smoothstep(-0.2, 0.3, el)
        sky_col = lerp(lerp(NIGHT, BLUE, smoothstep(0, 0.4, u)), DAWNSKY, smoothstep(0.4, 1, u))
        sky = (0.1 + 0.18 * u) * (0.93 + 0.07 * shim(t))
        late = keys(t, [(64, 1), (76, 0.0)])                 # at the end only the markers keep the light
        fr += light(sky_col, sky * fade * (0.25 + 0.75 * late))
        # stars fade as the sky brightens
        fr += light(STAR, fade * stars * smoothstep(-0.05, -0.18, el) * np.clip(0.7 + 0.3 * twinkle(t), 0, 1))
        # twilight glow low in the east before sunrise
        glow = smoothstep(-0.2, 0.0, el) * smoothstep(0.12, 0.0, el) * smoothstep(-300, 650, x)
        fr += light(ROSE, 0.35 * glow * fade)

        # direct sun: colour from transmission through the air, gated by the eastern ridge
        if el > -0.02:
            e = max(el, 0.0)
            m = 1.0 / (np.sin(e) + 0.50572 * (np.degrees(e) + 6.07995) ** -1.6364)
            T = np.exp(-beta * m)
            col = T / T.max()
            sunI = 0.62 * T.max() ** 0.45 * smoothstep(-0.02, 0.03, el)
            lit = smoothstep(horizon - 0.012, horizon + 0.012, el)
            dens = sum(np.sin(x * mk[i, 0] + z * mk[i, 1] + mph[i] + t * mv[i]) for i in range(5)) / 5
            dens = smoothstep(-0.1, 0.45, dens) * (1 - smoothstep(0.14, 0.3, el))
            # clouds drift over in the morning and their shadows cross the field
            cl = sum(np.sin(x * ck[i, 0] + z * ck[i, 1] + cph[i] - t * 0.25) for i in range(3)) / 3
            cloud = smoothstep(0.1, 0.6, cl) * smoothstep(36, 46, t)
            direct = sunI * lit * (1 - 0.55 * dens) * (1 - 0.6 * cloud)
            fr += light(col, direct * (0.35 + 0.65 * late) * (1 - 0.7 * marker))
            # markers: marble catches it brighter, with a glint as the sun first clears the ridge, and
            # keeps it at the end
            lm = smoothstep(m_h - 0.008, m_h + 0.008, el)
            glint = np.exp(-((el - m_h - 0.01) / 0.008) ** 2)
            fr += light(lerp(col, MARBLE, 0.5), ((0.8 * sunI + 0.15) * lm * (1 - 0.4 * cloud) + 0.5 * glint) * marker)
            # mist in the hollows, lit by forward scattering toward the street
            L = np.array([az[0] * np.cos(e), np.sin(e), az[1] * np.cos(e)])
            cth = -(vdir @ L)
            g = 0.6
            phase = (1 - g * g) / (1 + g * g - 2 * g * cth) ** 1.5 / 4
            mist = dens * smoothstep(-0.05, 0.02, el)
            fr += light(lerp(col, ROSE, 0.3), mist * (0.2 + 0.9 * np.clip(phase, 0, 1.2)) * (0.4 + 0.6 * lit))
        pre = smoothstep(0.03, -0.02, el)
        if pre > 0:                                           # pre-dawn: mist lit only by the sky
            fr += light(BLUE, 0.06 * marker * fade * pre)
            dens0 = sum(np.sin(x * mk[i, 0] + z * mk[i, 1] + mph[i] + t * mv[i]) for i in range(5)) / 5
            fr += light(DAWNSKY, 0.22 * smoothstep(-0.1, 0.45, dens0) * smoothstep(-0.2, -0.1, el) * pre)
        fr *= keys(t, [(D - 3, 1), (D, 0)])
    return out
