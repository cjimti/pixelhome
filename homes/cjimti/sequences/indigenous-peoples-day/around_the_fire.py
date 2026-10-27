"""Around the Fire: A fire is lit in the middle of the porch courtyard, the open U between the wings.
The roofline does not show the fire itself but the light it throws: bright on the three porch walls
that ring it, falling off toward the wing ends, colour following the flame's temperature. People
walk in from the street and sit around it, and their shadows sweep along the walls and settle. The
storyteller sits at the back; when she raises her hands near the fire, hand shadows play across the
porch walls: a bird that flaps and flies around the courtyard, a rabbit that hops and twitches its
ears. She leans in close for the big moment (her shadow swallows the porch front), the fire flares,
sparks fly, everyone's shadow shakes with laughter. The fire burns down and the listeners leave."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes, colormap

CODE = 'IP05'
TITLE = 'Around the Fire'
KIND = 'show'
DESCRIPTION = ('A fire in the porch courtyard lights the walls around it. Listeners gather and their '
               'shadows settle; the storyteller makes hand shadows (a bird, a rabbit) dance across the porch.')

NIGHT = hexc('#0a1030')
SPARK = hexc('#ffd080')
FIRE = colormap([(0.0, (0.35, 0.02, 0.0)), (0.35, (1.0, 0.14, 0.0)), (0.7, (1.0, 0.36, 0.04)),
                 (1.0, (1.0, 0.6, 0.2)), (1.3, (1.0, 0.78, 0.45))])


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 82.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x, z = G.pos[:, 0], G.pos[:, 2]
    FX, FZ = -22.0, -380.0
    dx, dz = x - FX, z - FZ
    r_p = np.hypot(dx, dz)
    phi = np.arctan2(dz, dx)                     # angle of each pixel seen from the fire
    falloff = (190 / r_p) ** 1.25
    fl_slow = Flicker(rng, 1, 0.3, 1.1, k=4)
    fl_fast = Flicker(rng, 1, 3.0, 8.0, k=4)
    tongues = Flicker(rng, 1, 0.4, 1.6, k=3)
    BACK = -np.pi / 2                             # straight back, the middle of the porch front

    # listeners: (seat angle, seat radius, arrival time, leave time, which side they enter from)
    seats = [(-2.75, 95, 6.0, 66.0), (-2.2, 85, 7.5, 70.5), (-0.95, 85, 8.2, 68.5), (-0.4, 95, 9.4, 72.5),
             (2.55, 110, 10.5, 64.0), (0.6, 110, 11.2, 74.5)]
    teller = (BACK, 95)

    def seat_pos(a, r):
        return FX + r * np.cos(a), FZ + r * np.sin(a)

    def walk(t, a, r, t_in, t_out):
        """Position of a listener: walks in from the street, sits, walks out again."""
        sx, sz = seat_pos(a, r)
        ex = sx * 0.6 + (FX + (260 if sx > FX else -260)) * 0.4
        ez = 60.0
        if t < t_in:
            return None
        u_in = smoothstep(t_in, t_in + 4.5, t)
        u_out = smoothstep(t_out, t_out + 5, t)
        if u_out >= 1:
            return None
        k = u_in * (1 - u_out)
        return lerp(ex, sx, k), lerp(ez, sz, k)

    sparks = []
    for f in range(F):
        t = f * DT
        fr = out[f]
        # -- the fire's strength over the story
        base = keys(t, [(0, 0), (2.5, 0.0), (5, 0.55), (10, 0.9), (44, 0.9), (46.5, 1.25), (49, 1.0),
                        (60, 0.95), (68, 0.7), (76, 0.32), (82, 0.2)])
        flare = np.exp(-((t - 46.6) / 0.7) ** 2) * 0.35
        flick = 1 + 0.12 * fl_slow(t)[0] + 0.045 * fl_fast(t)[0]
        lean = 0.45 * tongues(t)[0]
        I_f = (base + flare) * flick
        strike = 0.0
        for ts in (1.2, 1.9, 2.4, 2.75):
            strike += np.exp(-((t - ts) / 0.05) ** 2)
        direction = 1 + 0.18 * np.cos(phi - (BACK + lean))
        light_I = I_f * falloff * direction + 0.5 * strike * falloff ** 2

        # -- shadows
        shade = np.ones(G.N)
        pen = 0.05 + 0.12 * (1 - min(base, 1))        # softer edges when the flame is small and low

        def occlude(cx, cz, radius, strength=0.82):
            nonlocal shade
            ddx, ddz = cx - FX, cz - FZ
            rr = np.hypot(ddx, ddz)
            if rr < 8:
                return
            a = np.arctan2(ddz, ddx)
            w = np.arcsin(min(radius / rr, 0.95))
            dphi = np.abs(wrap(phi - a))
            behind = smoothstep(rr - 10, rr + 25, r_p)
            shade *= 1 - strength * smoothstep(w + pen, w - pen, dphi) * behind

        for i, (a, r, t_in, t_out) in enumerate(seats):
            p = walk(t, a, r, t_in, t_out)
            if p is None:
                continue
            px, pz = p
            rad = 12.0
            # leaning back at the big moment, shaking with laughter after it
            back_off = 14 * np.exp(-((t - 47.5) / 1.4) ** 2)
            laugh = smoothstep(50, 51, t) * (1 - smoothstep(56, 58, t))
            shake = laugh * 0.025 * np.sin(2 * np.pi * (5.5 + 0.4 * i) * t + i)
            rr = np.hypot(px - FX, pz - FZ) + back_off
            aa = np.arctan2(pz - FZ, px - FX) + shake
            occlude(FX + rr * np.cos(aa), FZ + rr * np.sin(aa), rad, 0.75)

        # the storyteller at the back, swaying as she speaks; she leans in for the big moment
        if 3 < t < 79:
            ta, tr = teller
            tr = keys(t, [(42, 95), (45.5, 26), (48.5, 26), (51, 95)])
            sway = 0.06 * np.sin(2 * np.pi * 0.23 * t) + 0.03 * np.sin(2 * np.pi * 0.61 * t)
            arrive = smoothstep(3, 5, t) * (1 - smoothstep(77, 79, t))
            occlude(FX + tr * np.cos(ta + sway), FZ + tr * np.sin(ta + sway), 13, 0.85 * arrive)

        # hand shadows: occluders held close to the flame make big shapes on the walls
        # a bird: body and two wings that flap, flying across the porch walls and back
        if 18 < t < 33:
            u = (t - 18) / 15
            amp = smoothstep(0, 0.06, u) * (1 - smoothstep(0.94, 1, u))
            ca = BACK + 1.15 * np.sin(2 * np.pi * u * 1.0) * smoothstep(0, 0.2, u)
            flap = np.sin(2 * np.pi * 1.4 * t)
            hand_r = 34
            for side in (-1, 1):
                wa = ca + side * (0.16 + 0.07 * flap)
                occlude(FX + hand_r * np.cos(wa), FZ + hand_r * np.sin(wa), 4.5 + 2.5 * (1 + flap), 0.8 * amp)
            occlude(FX + hand_r * np.cos(ca), FZ + hand_r * np.sin(ca), 3.5, 0.8 * amp)
        # a rabbit: head and two tall ears that twitch; it hops along the porch front
        if 33.5 < t < 43:
            u = t - 33.5
            amp = smoothstep(0, 0.6, u) * (1 - smoothstep(8.6, 9.5, u))
            hops = [(0.8, 0.0), (2.0, 0.22), (3.1, 0.44), (5.6, 0.2), (6.6, -0.1), (7.6, -0.35)]
            pos = -0.45
            lift = 0.0
            for th, dpos in hops:
                k = smoothstep(th, th + 0.45, u)
                pos += (dpos - pos) * k if k > 0 else 0
                lift = max(lift, np.sin(np.pi * np.clip((u - th) / 0.45, 0, 1)))
            ca = BACK + pos
            hand_r = 32 - 6 * lift
            twitch = 0.04 * np.exp(-((u - 4.3) / 0.12) ** 2) + 0.04 * np.exp(-((u - 4.7) / 0.12) ** 2)
            occlude(FX + hand_r * np.cos(ca), FZ + hand_r * np.sin(ca), 6.5, 0.85 * amp)
            for side, tw in ((-1, twitch), (1, 0)):
                ea = ca + side * 0.12 + tw * side - 0.04
                occlude(FX + (hand_r - 3) * np.cos(ea), FZ + (hand_r - 3) * np.sin(ea), 2.2, 0.85 * amp)

        I = light_I * shade
        hue = FIRE(np.clip(I * (0.75 + 0.35 * base), 0, 1.3))     # hotter where brighter
        hue = hue / np.maximum(hue.max(1, keepdims=True), 1e-6)
        col = light(hue, np.clip(I, 0, 1.1)) + light(NIGHT, 0.06)

        # sparks at the flare: tiny embers flung outward that light the walls they pass
        if 46.4 < t < 47.4 and rng.random() < 0.7:
            a = rng.uniform(-np.pi, np.pi)
            sparks.append((t, a, rng.uniform(150, 320)))
        if 58 < t < 66 and rng.random() < 0.05:
            sparks.append((t, rng.uniform(-np.pi, np.pi), rng.uniform(120, 220)))
        alive = []
        sp = np.zeros(G.N)
        for (t0, a, v) in sparks:
            u = t - t0
            if u < 2.2:
                rr = v * u * np.exp(-0.35 * u)
                sx, sz = FX + rr * np.cos(a), FZ + rr * np.sin(a)
                dd = np.hypot(x - sx, z - sz)
                sp = np.maximum(sp, np.exp(-(dd / 14) ** 2) * np.exp(-u / 0.9))
                alive.append((t0, a, v))
        sparks = alive
        col += light(SPARK, 0.9 * sp)
        fr[:] = col * keys(t, [(0, 0), (1.0, 1), (80, 1), (82, 0)])
    return out
