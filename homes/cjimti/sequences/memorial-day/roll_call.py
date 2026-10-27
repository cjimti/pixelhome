"""Roll Call: The final roll call. A caller stands at the middle of the far Porch Front; the company
stands in two ranks along the wing fronts, thirteen dim points of silver. For each name the caller's
voice is a narrow ray of light from the porch to that soldier, crossing whatever roof lies between, and
the soldier answers with a quick double pulse: "Here." Three names get no answer. The ray stays on the
empty place; the name is called a second time, brighter, and a third; in the silence the point that
stood there fades away, and a small gold star takes its place. At the end the ranks dim and only the
three stars are left."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, smoothstep, keys, lerp, nframes

CODE = 'MM07'
TITLE = 'Roll Call'
KIND = 'show'
DESCRIPTION = ('The final roll call: a ray of light calls each soldier in the ranks along the wings, and each '
               'answers. Three names are called three times into silence, and gold stars take their places.')

SILVER = hexc('#d6e0f2')
WHITE = hexc('#fff6e8')
GOLD = hexc('#ffc058')
NAVY = hexc('#0b1d4a')
RAY = hexc('#c9d4e8')


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    P = G.pos
    x, z = P[:, 0], P[:, 2]
    C = np.array([-22.0, -560.0])                       # the caller, middle of the porch front
    ang = np.arctan2(x - C[0], z - C[1])                # bearing of every pixel from the caller
    dist = np.hypot(x - C[0], z - C[1])
    L, R = G.seg['Left'], G.seg['Right']
    wings = np.concatenate([L, R])
    # thirteen soldiers in two ranks
    sx = np.concatenate([np.linspace(-560, -240, 6), np.linspace(200, 590, 7)])
    sz = np.where(sx < 0, -148.0, -191.0)
    S = len(sx)
    s_ang = np.arctan2(sx - C[0], sz - C[1])
    fallen = {2, 7, 11}
    order = list(rng.permutation(S))
    # schedule: (time of call, soldier, call number); answers for those present
    calls, answers, silence = [], {}, {}
    t = 6.0
    for k in order:
        if k in fallen:
            for n in range(3):
                calls.append((t, k, n))
                t += 2.6 + 0.4 * n
            silence[k] = t                               # the place empties, a star appears
            t += 4.0
        else:
            calls.append((t, k, 0))
            answers[k] = t + 1.1
            t += 3.2
    T_END = t + 2.0
    D = T_END + 9.0
    out = np.zeros((nframes(D), G.N, 3))
    theta = s_ang[order[0]]
    ray_I = 0.0

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        env = keys(t, [(0, 0), (3, 1), (D - 2, 1), (D, 0)])
        fr += perc(0.07 * env) * NAVY
        # which call is current; the ray slews to it like a turned head
        cur = None
        for c in calls:
            if c[0] - 0.6 <= t:
                cur = c
        bead = np.zeros(G.N)
        halo_k, halo = None, 0.0
        if cur is not None and t < T_END:
            theta += (s_ang[cur[1]] - theta) * (1 - np.exp(-DT / 0.18))
            settled = np.exp(-((s_ang[cur[1]] - theta) / 0.04) ** 2)   # dark while the head turns
            u = t - cur[0]
            k = cur[1]
            sd = np.hypot(sx[k] - C[0], sz[k] - C[1])
            loud = 0.6 + 0.15 * cur[2]
            # the call travels out along the ray as a bright bead; an answer travels back
            r_out = u * sd / 1.1
            bead = loud * np.exp(-((dist - r_out) / 34.0) ** 2) * np.sin(np.pi * np.clip(u / 1.25, 0, 1)) ** 0.7
            if k in answers:
                a = t - answers[k] - 0.4
                bead = bead + 0.45 * np.exp(-((dist - sd * (1 - a / 1.1)) / 34.0) ** 2) * \
                    np.sin(np.pi * np.clip(a / 1.2, 0, 1)) ** 0.7
            # where the call lands: a soft halo on the named place
            halo_k, halo = k, loud * 0.75 * np.exp(-((u - 1.15) / 0.3) ** 2) * settled
            wait = 0.12 if k in fallen else 0.05
            ray_I = settled * wait * smoothstep(-0.6, 0, u)
            bead = bead * settled
        else:
            ray_I *= np.exp(-DT / 0.8)
        # the ray: a narrow wedge from the caller
        width = 0.02 + 5.0 / np.maximum(dist, 60)
        ray = np.exp(-((ang - theta) / width) ** 2) * (dist > 15)
        fr += perc(np.clip(ray_I + bead, 0, 1) * ray * env)[:, None] * RAY
        # the caller
        fr += perc(env * (0.32 + 0.5 * bead.max()) * np.exp(-(dist / 9.0) ** 2))[:, None] * WHITE
        if halo_k is not None:
            dh = np.abs(x[wings] - sx[halo_k]) + 1000 * (np.abs(z[wings] - sz[halo_k]) > 5)
            fr[wings] += perc(env * halo * np.exp(-(dh / 14.0) ** 2))[:, None] * RAY
        # the soldiers
        rank_fade = 1 - smoothstep(T_END, T_END + 5, t)
        for k in range(S):
            d = np.abs(x[wings] - sx[k]) + 1000 * (np.abs(z[wings] - sz[k]) > 5)
            g = np.exp(-(d / 5.5) ** 2)
            if k in fallen:
                stand = 0.22 * (1 - smoothstep(silence[k] - 4.5, silence[k] - 0.5, t))
                star = smoothstep(silence[k], silence[k] + 2.0, t) * (1 - smoothstep(D - 4, D - 0.5, t))
                tw = 1 + 0.06 * np.sin(2 * np.pi * 0.25 * t + k)
                fr[wings] += perc(env * stand * g)[:, None] * SILVER
                fr[wings] += perc(0.6 * star * tw * np.exp(-(d / 8.0) ** 2))[:, None] * GOLD
            else:
                a = t - answers[k]
                here = 0.6 * (np.exp(-((a - 0.0) / 0.1) ** 2) + 0.75 * np.exp(-((a - 0.32) / 0.13) ** 2))
                g = np.exp(-(d / (5.5 + 5.0 * min(1, here))) ** 2)
                after = 0.08 * smoothstep(0, 0.6, a)      # a soldier who has answered stands a little brighter
                fr[wings] += perc(env * ((0.22 + after) * rank_fade + here) * g)[:, None] * lerp(SILVER, WHITE, min(1, here))
    return out
