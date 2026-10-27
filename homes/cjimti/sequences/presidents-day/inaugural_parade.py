"""Inaugural Parade: The continuous roofline is Pennsylvania Avenue, entering at the back free end of
Side and leaving at the free end of Right, with the reviewing stand on the Porch Front. Outriders,
a drum major twirling (and tossing) his baton, a marching band whose ranks step and surge on the
beat, a colour guard, two horses at a clip-clop, then the motorcade, which stops at the stand for a
confetti burst while the crowd's cameras flash along the street-side runs. Last of all comes the
street sweeper, who pushes every scrap of confetti into a pile and shoves it off the end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'PR06'
TITLE = 'Inaugural Parade'
KIND = 'show'
DESCRIPTION = ('A parade along the whole roofline: outriders, a baton-twirling drum major, a marching band '
               'on the beat, horses, the motorcade and confetti at the stand, and finally the street sweeper.')

NAVY = hexc('#2440b8')
CREAM = hexc('#ffe4b8')
BRICK = hexc('#c82010')
BRASS = hexc('#ffa030')
HORSE = hexc('#a04a10')
FLASH = hexc('#fff4e8')
CONF = [hexc('#2a4ad0'), hexc('#ffe8c8'), hexc('#d02414'), hexc('#ffb040')]


def render(G, seed=26):
    rng = np.random.default_rng(seed)
    D = 84.0
    out = np.zeros((nframes(D), G.N, 3))
    s = G.pd[G.path]
    z = G.pos[G.path, 2]
    s_end = s[-1]
    s_stand = 0.5 * (s[261] + s[331])
    street = smoothstep(-260, -170, z)            # the street-facing runs: where the crowd stands
    shim = Flicker(rng, G.N, 0.2, 1.0)
    V = 78.0
    BEAT = 2.0                                    # steps per second

    def blob(c, w):
        return np.exp(-((s - c) / w) ** 2)

    def bar(c, half, soft=2.5):
        return smoothstep(-half - soft, -half + soft, s - c) * smoothstep(half + soft, half - soft, s - c)

    def march(t0, v=V, stop=None):
        """Head position of a unit that entered at t0; optional (t_stop, t_go) halt at the stand."""
        tt = t - t0
        if stop is not None:
            ts, tg = stop
            tt = min(tt, ts - t0) + max(0.0, t - tg) if t > ts else tt
        return v * tt

    # confetti pieces: launched from the stand while the motorcade halts
    T_STOP, T_GO = 41.0, 49.0
    NC = 220
    c_t0 = T_STOP + 0.4 + rng.uniform(0, 2.5, NC)
    c_v = rng.normal(0, 260, NC)
    c_rest = s_stand + c_v * 0.9
    c_col = np.array([CONF[k] for k in rng.integers(0, 4, NC)])
    c_tum = rng.uniform(1.0, 3.0, NC)
    c_ph = rng.uniform(0, 2 * np.pi, NC)
    pushed = np.full(NC, -1e9)
    T_SWEEP, V_SWEEP = 54.0, 105.0
    flashes = np.zeros(G.N)

    for f in range(len(out)):
        t = f * DT
        buf = light(NAVY, 0.07 * keys(t, [(0, 0), (2, 1), (D - 3, 1), (D, 0)]) * (0.85 + 0.15 * shim(t)))
        stand = bar(s_stand, 90, 30)
        buf += light(BRASS, stand * keys(t, [(0, 0), (3, 0.16), (T_STOP, 0.16), (T_STOP + 0.5, 0.4),
                                                (T_GO + 2, 0.4), (T_GO + 5, 0.16), (D - 3, 0.16), (D, 0)]))
        beat_ph = (t * BEAT) % 1
        crowd_at = []

        # outriders: two headlights, fast
        h = march(1.0, 125)
        if -20 < h < s_end + 40:
            for k in range(2):
                buf += light(CREAM, 0.85 * blob(h - k * 34, 4)) + light(BRASS, 0.3 * blob(h - k * 34 - 8, 8))

        # drum major with a twirling baton (and one toss)
        h = march(4.0)
        if -20 < h < s_end + 40:
            buf += light(CREAM, 0.75 * blob(h, 3.5))
            tl = t - 4.0
            toss = 14.0 < tl < 15.4
            if not toss:
                half = 9 * abs(np.cos(2 * np.pi * 1.6 * t)) + 1.5
                buf += light(BRASS, 0.7 * bar(h + 9, half, 1.5))
            if 15.4 <= tl < 15.9:
                buf += light(FLASH, 0.8 * np.exp(-(tl - 15.4) / 0.12) * blob(h + 9, 10))
            if 13.6 < tl < 14.2:                           # the toss, a streak upward (out of the roof)
                buf += light(BRASS, 0.8 * (1 - (tl - 13.6) / 0.6) * blob(h + 9, 4))
            crowd_at.append((h, 0.3))

        # marching band: eight ranks of brass, alternate feet, surging on each step, bass drum at the back
        h = march(6.5) - (V / (2 * np.pi * BEAT)) * np.sin(2 * np.pi * BEAT * (t - 6.5))
        if -150 < h < s_end + 160:
            for k in range(8):
                ph = (beat_ph + 0.5 * (k % 2)) % 1
                buf += light(BRASS, (0.42 + 0.4 * np.exp(-ph / 0.09)) * blob(h - 20 - k * 14, 3.5))
            drum = np.exp(-beat_ph / 0.12) if int(t * BEAT) % 2 == 0 else 0.4 * np.exp(-beat_ph / 0.1)
            buf += light(NAVY, (0.45 + 0.5 * drum) * blob(h - 145, 9))
            if int(t * BEAT) % 8 == 0:                     # cymbal on every eighth step
                buf += light(FLASH, 0.6 * np.exp(-beat_ph / 0.08) * blob(h - 132, 7))
            crowd_at.append((h - 70, 0.5))

        # colour guard: three flags rippling on their poles
        h = march(11.5)
        if -100 < h < s_end + 100:
            for k, col in enumerate((NAVY, CREAM, BRICK)):
                c0 = h - k * 30
                rip = 0.75 + 0.25 * np.sin((s - c0) * 0.5 - t * 9)
                buf += light(col, 0.6 * bar(c0 - 7, 7, 2) * rip) + light(BRASS, 0.6 * blob(c0 + 1, 2))
            crowd_at.append((h - 30, 0.3))

        # two horses at a walk: bodies and four hoof-falls per stride
        h = march(15.0)
        if -100 < h < s_end + 100:
            for k in range(2):
                c0 = h - k * 45
                buf += light(HORSE, 0.45 * blob(c0, 11))
                for j, off in enumerate((-9, 6, -6, 9)):
                    ph = (t * 1.5 + j / 4 + 0.13 * k) % 1
                    buf += light(CREAM, 0.6 * np.exp(-ph / 0.07) * blob(c0 + off, 2.5))
            crowd_at.append((h - 20, 0.3))

        # the motorcade, which halts at the stand
        h = march(22.0, stop=(T_STOP, T_GO))
        if T_STOP <= t < T_GO:
            h = V * (T_STOP - 22.0)
        car_c = h
        if -100 < h < s_end + 100:
            body = bar(h - 30, 30, 3)
            buf += light(NAVY, 0.7 * body) + light(BRASS, 0.5 * (blob(h - 60, 2.5) + blob(h, 2.5)))
            buf += light(CREAM, 0.9 * (blob(h + 3, 2.5)))
            for k, col in enumerate((BRICK, CREAM)):
                buf += light(col, 0.55 * (0.7 + 0.3 * np.sin(t * 13 + k)) * blob(h - 6 - 6 * k, 2.2))
            crowd_at.append((h - 30, 1.0 if not (T_STOP <= t < T_GO) else 1.4))

        # crowd: camera flashes along the street-side runs near whatever is passing
        flashes *= 0.72
        for c0, rate in crowd_at:
            near = street * np.exp(-((s - c0) / 180) ** 2)
            hit = rng.random(G.N) < near * rate * 0.035
            flashes[hit] = rng.uniform(0.5, 0.9, hit.sum())
        buf += light(FLASH, flashes)

        # confetti
        if t > T_STOP:
            tau = np.clip(t - c_t0, 0, None)
            pos = s_stand + c_v * 0.9 * (1 - np.exp(-tau / 0.9))
            sw = (t - T_SWEEP) * V_SWEEP
            if t > T_SWEEP:
                rank = np.argsort(np.argsort(pos))
                push = sw + 6 + 0.14 * rank          # piled up ahead of the broom
                pushed = np.where(pos < push, np.maximum(pushed, push), pushed)
            pos = np.maximum(pos, pushed)
            live = (t > c_t0) & (pos < s_end + 5)
            if live.any():
                tum = 0.55 + 0.45 * np.cos(2 * np.pi * c_tum[live] * t + c_ph[live])
                I = 0.5 * tum * smoothstep(0, 0.2, tau[live])
                I *= np.where(pushed[live] > -1e8, 0.7, 1.0)
                w = np.exp(-((s[None, :] - pos[live][:, None]) / 3) ** 2)
                buf += np.einsum('kn,kc->nc', w * (I ** 2.2)[:, None], c_col[live])
            if t > T_SWEEP and sw < s_end + 30:            # the sweeper and his broom
                buf += light(CREAM, 0.6 * blob(sw - 6, 3.5))
                buf += light(BRASS, 0.5 * (0.6 + 0.4 * abs(np.sin(t * 7))) * blob(sw + 2 * np.sin(t * 7), 3))
            if sw > s_end and sw < s_end + 60:               # the pile goes over the edge: one last flash
                buf += light(FLASH, 0.5 * np.exp(-((sw - s_end) / 25)) * blob(s_end, 10))
        out[f][G.path] = buf
    return out
