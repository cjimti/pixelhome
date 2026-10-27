"""Three Sisters: A seed is planted in a mound at each of the five corners of the roof. Corn rises
first along both runs of its corner, beans twine outward along the corn (never past it), squash
unrolls broad leaves on the ground beyond and between them, flowers open and fruit swells. At the
harvest a warm pulse passes between neighbouring mounds; then the plants return to the soil and only
the five seeds stay glowing."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'OT21'
TITLE = 'Three Sisters'
KIND = 'show'
DESCRIPTION = ('Corn, beans and squash grow together from a mound at each corner of the roof: the corn '
               'stands, the beans climb it, the squash shades the ground, and the harvest comes in.')

SOIL = hexc('#5a2e12')
SEED = hexc('#ffb84a')
STALK = hexc('#a8a83a')
CORN_GOLD = hexc('#f2c040')
TASSEL = hexc('#ffd88a')
BEAN = hexc('#3fd060')
POD = hexc('#7a2a58')
LEAF = hexc('#2f8a3a')
FLOWER = hexc('#ffc21a')
SQUASH = hexc('#e8701c')
WARM = hexc('#ffcf80')


def over(base, pwm, alpha):
    a = np.clip(alpha, 0, 1)[:, None]
    return base * (1 - a) + pwm * a


def render(G, seed=21):
    rng = np.random.default_rng(seed)
    D = 70.0
    out = np.zeros((nframes(D), G.N, 3))
    d = G.pd
    pp = G.pd[G.path]
    mounds = np.array([(pp[k] + pp[k + 1]) / 2 for k in (80, 178, 260, 331, 380)])
    # nearest mound, signed offset, and room to spread on that side
    j = np.argmin(np.abs(d[:, None] - mounds[None, :]), axis=1)
    s = d - mounds[j]
    a = np.abs(s)
    bounds = np.concatenate([[-1e9], (mounds[1:] + mounds[:-1]) / 2, [1e9]])
    room = np.where(s < 0, mounds[j] - np.maximum(bounds[j], 0), np.minimum(bounds[j + 1], G.length) - mounds[j])
    # planting order: from the porch outward, mirrored
    t_plant = np.array([5.4, 4.2, 3.0, 3.0, 4.2])
    tj = t_plant[j]
    jit = rng.uniform(-0.6, 0.6, 5)[j]

    flick = Flicker(rng, G.N, 0.1, 0.5)
    sway = rng.uniform(0, 2 * np.pi, G.N)
    leaf_k = np.floor((a - 14) / 30)
    leaf_u = ((a - 14) / 30) % 1
    leaf_shape = np.where(a > 14, np.sin(np.pi * leaf_u) ** 1.5, 0)
    flower_here = (leaf_k % 2 == 0) & (a > 30)
    flower_c = 14 + 30 * (leaf_k + 0.5)                     # flower at the middle of every other leaf
    flower_d = np.abs(a - flower_c)
    pod_spot = (np.abs(((a / 22) % 1) - 0.5) < 0.12)

    for f in range(len(out)):
        t = f * DT
        fade_all = keys(t, [(0, 0), (2, 1), (68, 1), (70, 0)])
        col = light(SOIL, 0.14 * fade_all * (1 + 0.1 * flick(t)))

        # the seed: drops in, flares, settles to a warm ember in the mound
        u = t - tj
        seed_I = (smoothstep(-1.2, 0, u) * (0.45 + 0.5 * np.exp(-np.clip(u, 0, None) / 1.2))
                  * (0.9 + 0.1 * np.sin(2.1 * t))) * np.exp(-(a / 8) ** 2)

        # corn
        g_c = smoothstep(3, 21, u + jit) ** 0.8
        Lc = 115 * g_c
        stalk = smoothstep(Lc + 4, Lc - 4, a) * (Lc > 1)
        joints = 1 + 0.35 * np.exp(-(((a % 26) - 13) / 3.5) ** 2)
        ripen = smoothstep(44, 52, t)
        stalk_col = lerp(STALK, CORN_GOLD, (0.25 * (a / 115) + 0.75 * ripen)[:, None])
        tassel = np.exp(-((a - Lc) / 6) ** 2) * (Lc > 5) * (0.8 + 0.2 * np.sin(2.3 * t + sway))
        corn_I = 0.46 * stalk * joints
        col = over(col, light(stalk_col, corn_I), stalk)
        col = over(col, light(TASSEL, 0.75 * tassel), np.clip(tassel * 1.4, 0, 1))

        # squash: spreads on the ground, beyond the corn and into the gaps
        g_s = smoothstep(11, 33, u + jit)
        Ls = room * 0.96 * g_s
        front = smoothstep(Ls + 10, Ls - 10, a)
        unfurl = smoothstep(Ls, Ls - 40, a)                   # a leaf opens once the front has passed it
        leaves = front * (0.35 + 0.65 * leaf_shape * unfurl)
        leaf_I = 0.46 * leaves * (1 + 0.08 * np.sin(0.7 * t + sway))
        col = over(col, light(LEAF, leaf_I), front * (1 - stalk) * 0.95)
        # squash also shades the ground under the corn: a dark green floor
        col = col + light(LEAF, 0.12 * front * stalk)

        # beans: climb along the corn, never past it, twining (a helix seen from the side)
        g_b = smoothstep(9, 31, u + jit)
        Lb = np.minimum(Lc - 6, 125 * g_b)
        bean_m = smoothstep(Lb + 5, Lb - 5, a) * (Lb > 1)
        helix = 0.5 + 0.5 * np.cos(2 * np.pi * a / 21 - 2.0 * t)
        helix = smoothstep(0.45, 0.95, helix)
        tip = np.exp(-((a - Lb) / 5) ** 2) * (Lb > 3)
        bean_I = 0.55 * bean_m * helix + 0.6 * tip
        pods = smoothstep(46, 54, t) * bean_m * pod_spot
        bean_col = BEAN
        col = over(col, light(bean_col, bean_I), np.clip(bean_m * helix + tip, 0, 1) * (1 - 0.8 * ripen))
        col = over(col, light(POD, 0.55 * pods), pods)

        # flowers open on the squash, then swell into fruit
        bloom = smoothstep(30, 37, u + jit) * (1 - smoothstep(42, 47, t))
        fruit = smoothstep(43, 50, t) * (1 - smoothstep(58, 62, t))
        on_leaf = smoothstep(Lc + 4, Lc + 12, a) * flower_here * smoothstep(0.3, 0.8, unfurl)
        fw = np.exp(-(flower_d / 4) ** 2) * on_leaf * bloom
        fr_ = np.exp(-(flower_d / (5 + 5 * fruit)) ** 2) * on_leaf * fruit
        col = over(col, light(FLOWER, 0.75 * fw), np.clip(fw * 1.5, 0, 1))
        col = over(col, light(SQUASH, 0.7 * fr_), np.clip(fr_ * 1.3, 0, 1))

        # harvest: a warm pulse leaves every mound and meets its neighbours half way
        hp = t - 51.0
        if 0 < hp < 7:
            ring = (np.exp(-((a - 95 * hp) / 18) ** 2) * smoothstep(room + 15, room - 5, a)
                    * np.exp(-hp / 3) * smoothstep(0, 0.3, hp))
            meet = np.exp(-((a - room) / 14) ** 2) * np.exp(-((hp - room / 95) / 0.5) ** 2) * (room < 450)
            col = col + light(WARM, 0.55 * ring + 0.6 * meet)

        # return to the soil: everything recedes toward the mounds, the seeds stay
        back = smoothstep(57, 65, t)
        keep = smoothstep(room * (1 - back) + 6, room * (1 - back) - 6, a) if back > 0 else 1
        col = col * (keep if np.ndim(keep) == 0 else keep[:, None])
        rest = smoothstep(58, 64, t) * (1 - smoothstep(67, 70, t))
        seed_I = seed_I * (1 - smoothstep(20, 30, u)) + rest * (0.4 + 0.06 * np.sin(1.3 * t)) * np.exp(-(a / 7) ** 2)
        col = over(col, light(SEED, seed_I), np.clip(seed_I * 2, 0, 1))
        out[f] = col * fade_all
    return out
