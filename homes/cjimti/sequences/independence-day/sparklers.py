"""Sparklers: A kid with a glowing punk walks in from the back of the house and lights a sparkler at
each of the five corners. Every sparkler is a little particle simulation: iron sparks shoot along
the roof with drag, cool through the blackbody colours and fork into smaller sparks as they burn.
The last sparkler will not take, until it does. Then they are waved (with the eye's afterimage
streaking behind them) and burn down one by one to glowing red wires."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, Flicker, colormap, nframes

CODE = 'IN02'
TITLE = 'Sparklers'
KIND = 'show'
DESCRIPTION = ('A kid with a punk lights a sparkler at each corner of the house. Sparks fly and fork along '
               'the roof; the last one is a dud, until it is not. Then they wave, and burn down to red wires.')

NIGHT = hexc('#060c30')
PUNK = hexc('#ff3a06')
# blackbody-ish cooling: white-hot, yellow, orange, cherry, dark
BB = colormap([(0.0, (0.0, 0.0, 0.0)), (0.12, (0.18, 0.005, 0.0)), (0.3, (0.6, 0.06, 0.0)),
               (0.55, (1.0, 0.32, 0.03)), (0.8, (1.0, 0.66, 0.25)), (1.0, (1.0, 0.92, 0.75))])


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 60.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]                           # path distance of each pixel, path order
    L = G.length
    corners = np.array([(x[a] + x[a + 1]) / 2 for a in (80, 178, 260, 331, 380)])

    # the punk's walk: from the free back end, pausing at each corner to light it
    walk, t, here = [(0.0, -40.0), (1.5, -40.0)], 1.5, -40.0
    light_t = []
    for k, c in enumerate(corners):
        t += (c - here) / 260.0
        walk.append((t, c - 6))
        light_t.append(t + 0.5)
        hold = 1.3 if k < 4 else 4.25                    # the dud takes three tries
        t += hold
        walk.append((t, c - 6))
        here = c
    t_exit = t + (L + 60 - here) / 650.0      # and the kid runs for it
    walk.append((t_exit, L + 60))
    dud_tries = [light_t[4], light_t[4] + 1.3, light_t[4] + 2.6]
    light_t[4] = light_t[4] + 3.6                        # ...and then it really goes

    # each sparkler's life: ignition, burn, and the order they go out
    out_t = np.array([47.0, 52.0, 49.0, 54.5, 50.5])
    gain = np.array([1.0, 0.95, 1.0, 0.95, 1.25])
    wave_amp = np.array([70.0, 55.0, 45.0, 55.0, 70.0])
    wave_f = np.array([1.1, 1.6, 0.8, 1.6, 1.1])
    wave_ph = np.array([0.0, np.pi, 0.5, 0.0, np.pi])    # wings mirror each other

    # spark pool
    cap = 6000
    pos = np.zeros(cap); vel = np.zeros(cap); age = np.zeros(cap); life = np.ones(cap)
    heat = np.zeros(cap); split = np.full(cap, 1e9); gen = np.zeros(cap, int); alive = np.zeros(cap, bool)

    def spawn(n, p, v, lf, h, g):
        free = np.flatnonzero(~alive)[:n]
        m = len(free)
        if m == 0:
            return
        pos[free] = p[:m]; vel[free] = v[:m]; age[free] = 0; life[free] = lf[:m]; heat[free] = h[:m]
        gen[free] = g
        will = (rng.random(m) < (0.55 if g == 0 else 0.3)) & (g < 2)
        split[free] = np.where(will, lf[:m] * rng.uniform(0.35, 0.75, m), 1e9)
        alive[free] = True

    core_fl = Flicker(rng, 5, 6, 17)
    after = np.zeros(G.N)
    after_col = np.zeros((G.N, 3))
    sky = Flicker(rng, G.N, 0.05, 0.2)

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        buf += light(NIGHT, keys(t, [(0, 0), (1.5, 0.08), (56, 0.08), (60, 0.0)]) * (1 + 0.1 * sky(t)))

        wave = smoothstep(24, 27, t) * (1 - smoothstep(37, 40, t))
        fl = core_fl(t)
        cores = []
        for k in range(5):
            age_k = t - light_t[k]
            if age_k < 0 or t > out_t[k] + 4:
                continue
            vigor = smoothstep(0, 0.8, age_k) * (1 - smoothstep(out_t[k] - 6, out_t[k], t))
            if k == 4:
                vigor *= 1 + 2.2 * np.exp(-age_k / 1.2)  # catches with a vengeance
            vigor *= gain[k]
            cpos = corners[k] + wave * wave_amp[k] * np.sin(2 * np.pi * wave_f[k] * (t - 24) + wave_ph[k])
            cpos += 2.0 * np.sin(2 * np.pi * 0.7 * t + k)  # a hand is never quite still
            cvel = (wave * wave_amp[k] * 2 * np.pi * wave_f[k] *
                    np.cos(2 * np.pi * wave_f[k] * (t - 24) + wave_ph[k]))
            cores.append((k, cpos, vigor, age_k))
            if vigor > 0.01:
                n = rng.poisson(190 * vigor * DT)
                dirn = rng.choice([-1.0, 1.0], n)
                sp = rng.uniform(120, 650, n) * (0.6 + 0.4 * vigor)
                spawn(n, cpos + rng.normal(0, 2, n), dirn * sp + cvel * 0.6,
                      rng.uniform(0.12, 0.42, n) * (0.5 + 0.5 * min(vigor, 1.2)), rng.uniform(0.85, 1.0, n), 0)
        # the dud's sputters: a few sparks, a puff, nothing
        for td in dud_tries:
            if td <= t < td + 0.35:
                n = rng.poisson(90 * DT)
                spawn(n, corners[4] + rng.normal(0, 2, n), rng.choice([-1.0, 1.0], n) * rng.uniform(60, 200, n),
                      rng.uniform(0.06, 0.18, n), np.full(n, 0.8), 2)

        # sparks: drag, forks, cooling
        a = np.flatnonzero(alive)
        if len(a):
            vel[a] *= np.exp(-5.0 * DT)
            pos[a] += vel[a] * DT
            old = age[a].copy()
            age[a] += DT
            fork = a[(old < split[a]) & (age[a] >= split[a])]
            if len(fork):
                for _ in range(2):
                    m = len(fork)
                    spawn(m, pos[fork], vel[fork] * rng.uniform(0.4, 0.9, m) + rng.normal(0, 160, m),
                          rng.uniform(0.06, 0.2, m), np.full(m, 1.0), int(gen[fork].max()) + 1)
                life[fork] = age[fork] + 0.03                  # the parent bursts into its children
                heat[fork] = 1.15
            dead = a[(age[a] >= life[a]) | (pos[a] < -20) | (pos[a] > L + 20)]
            alive[dead] = False
            a = np.flatnonzero(alive)
            u = np.clip(age[a] / life[a], 0, 1)
            temp = heat[a] * (1 - u) ** 1.3
            w = 2.5 + np.abs(vel[a]) * DT * 0.6                   # motion-blurred streak
            g = np.exp(-((x[:, None] - pos[a][None]) / w[None]) ** 2)
            I = g * (temp[None] ** 1.4) * 0.9
            # colour per spark by temperature, summed
            buf += (I[:, :, None] * BB(np.clip(temp, 0, 1))[None]).sum(1) * 0.75

        # cores, their halos, and the eye's afterimage when they move
        cur = np.zeros(G.N)
        cur_col = np.zeros((G.N, 3))
        for k, cpos, vigor, age_k in cores:
            dk = x - cpos
            burning = smoothstep(0, 0.3, age_k) * (1 - smoothstep(out_t[k] - 0.5, out_t[k] + 0.2, t))
            hot = 0.75 + 0.25 * vigor
            c_I = burning * (0.85 + 0.15 * fl[k]) * np.exp(-(dk / 5.5) ** 2)
            halo = burning * 0.16 * vigor * np.exp(-(dk / 70) ** 2)
            buf += BB(np.full(G.N, hot)) * perc(c_I)[:, None] + light(hexc('#ff9a40'), halo)
            cur = np.maximum(cur, c_I)
            cur_col = np.where((c_I > 0.05)[:, None], BB(np.full(G.N, hot)), cur_col)
            # after it goes out: the wire glows cherry and cools
            if t > out_t[k] - 0.2:
                cool = np.exp(-(t - out_t[k]) / 1.4) * smoothstep(out_t[k] - 0.2, out_t[k] + 0.3, t)
                buf += BB(np.full(G.N, 0.12 + 0.25 * cool)) * (cool * np.exp(-(dk / 6) ** 2))[:, None]
                if out_t[k] < t < out_t[k] + 1.5 and rng.random() < 0.15 * cool:
                    n = 2
                    spawn(n, np.full(n, cpos), rng.choice([-1.0, 1.0], n) * rng.uniform(60, 180, n),
                          np.full(n, 0.15), np.full(n, 0.7), 2)
        decay = np.exp(-DT / 0.18)
        after = np.maximum(after * decay, cur * wave)
        after_col = np.where((cur > after * 0.98)[:, None] & (cur > 0.05)[:, None], cur_col, after_col)
        buf += after_col * perc(0.55 * after * (cur < after * 0.95))[:, None]

        # the punk
        p = keys(t, walk)
        if 0.8 < t < t_exit:
            glow = (0.55 + 0.15 * np.sin(2 * np.pi * 0.9 * t)) * smoothstep(0.8, 1.6, t)
            for td in light_t[:4] + dud_tries + [light_t[4]]:
                glow *= 1 + 0.6 * np.exp(-((t - td + 0.25) / 0.15) ** 2)   # the kid blows on it
            buf += light(PUNK, glow * np.exp(-((x - p) / 5) ** 2)) + light(PUNK, 0.08 * np.exp(-((x - p) / 30) ** 2))

        m = buf.max(1, keepdims=True)
        buf = np.where(m > 1, buf / np.maximum(m, 1e-9), buf)
        out[f][G.path] = buf
    return out
