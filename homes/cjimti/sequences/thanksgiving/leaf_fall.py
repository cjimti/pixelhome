"""Leaf Fall: Autumn leaves fall through real 3-D space onto the roof. Each one flutters as it drops,
gliding side to side and flipping its bright face and dull back toward the street; its light gathers
and sharpens as it nears the roofline. Leaves that hit the roof skitter along it in the breeze and
drift into piles that grow at the five corners. A gust halfway through sends a flurry across; the
last big gust lifts every pile and blows the whole lot out of the free right end. One last leaf."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG03'
TITLE = 'Leaf Fall'
KIND = 'show'
DESCRIPTION = ('Leaves flutter down through 3-D space, flipping as they fall, land on the roof and drift into piles '
               'at the corners, until a gust blows every pile out the end of the house.')

LEAF = [hexc(c) for c in ('#ff8a18', '#c0102a', '#ffb000', '#ff5200', '#a83a08', '#e06010')]
BROWN = hexc('#5a1c04')
D = 66.0
CORNERS = np.array([491.0, 894.0, 1311.0, 1660.0, 2033.0])
Y_ROOF = 150.0


def render(G, seed=23):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    P = G.pos[G.path]                       # path order
    pdp = G.pd[G.path]
    xz = P[:, [0, 2]]

    # spawn schedule: a trickle that thickens, a flurry with the mid gust, then quiet, then one last leaf
    spawn = list(rng.uniform(1, 12, 10)) + list(rng.uniform(10, 30, 38)) + list(rng.uniform(28, 38, 30)) + \
        list(rng.uniform(38, 47, 18))
    spawn = np.sort(np.array(spawn))
    L = len(spawn) + 1
    spawn = np.append(spawn, 58.5)
    j = rng.integers(0, n, L)
    j[-1] = 296                               # last leaf aims for the middle of the porch
    # offset sideways from the roof, so some miss and fall past
    seg_dir = np.gradient(xz, axis=0)
    seg_dir /= np.linalg.norm(seg_dir, axis=1, keepdims=True) + 1e-9
    normal = np.stack([-seg_dir[:, 1], seg_dir[:, 0]], 1)
    start = xz[j] + normal[j] * rng.normal(0, 18, L)[:, None] - np.array([1.0, 0]) * rng.uniform(0, 30, L)[:, None]
    start[-1] = xz[296]
    h0 = rng.uniform(260, 460, L)
    h0[-1] = 380
    omega = 2 * np.pi * rng.uniform(0.45, 0.8, L)
    phase = rng.uniform(0, 2 * np.pi, L)
    swing = rng.uniform(25, 55, L)
    ang = rng.uniform(0, 2 * np.pi, L)
    sdir = np.stack([np.cos(ang), np.sin(ang)], 1)
    vdesc = rng.uniform(55, 80, L)
    col = np.array([LEAF[k] for k in rng.integers(0, len(LEAF), L)])
    col[-1] = LEAF[2]

    # state
    state = np.zeros(L, int)                  # 0 waiting, 1 falling, 2 on roof, 3 in a pile, 4 gone
    pos = start.copy()
    h = h0.copy()
    lp = np.zeros(L)                          # path position once on the roof
    target = np.zeros(L)
    landed_at = np.zeros(L)
    fade_out = np.zeros(L)
    slots = np.zeros((len(CORNERS), 2), int)
    blow_v = rng.uniform(260, 520, L)
    rustle = Flicker(rng, L, 0.4, 1.6)
    glint = Flicker(rng, n, 0.1, 0.5)

    for f in range(F):
        t = f * DT
        wind = keys(t, [(0, 6), (28, 9), (31, 90), (35, 90), (39, 10), (50, 10), (52, 160), (56.5, 50), (58.5, 0), (66, 0)])
        buf = np.zeros((n, 3))
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.08), (62, 0.08), (66, 0)]) * (1 + 0.2 * glint(t)))

        # start falling
        state[(state == 0) & (spawn <= t)] = 1
        fa = state == 1
        if fa.any():
            th = omega[fa] * t + phase[fa]
            edge = np.abs(np.cos(th))                         # gliding flat falls slowly, edge-on falls fast
            h[fa] -= vdesc[fa] * (0.35 + 1.1 * (1 - edge)) * DT
            glide = swing[fa, None] * omega[fa, None] * np.cos(th)[:, None] * sdir[fa]
            pos[fa] += (glide + np.array([wind, 0.0])) * DT
            # draw: a spot that sharpens and brightens as the leaf comes down to the roof
            hh = np.clip(h[fa] - Y_ROOF, 0, None)
            face = 0.3 + 0.7 * (0.5 + 0.5 * np.cos(th)) ** 2
            amp = face * 1.05 * np.exp(-hh / 320) * smoothstep(0, 0.8, t - spawn[fa])
            rad = 11 + 0.2 * hh
            d2 = ((xz[None, :, :] - pos[fa][:, None, :]) ** 2).sum(-1)
            I = amp[:, None] * np.exp(-d2 / rad[:, None] ** 2)
            buf += np.einsum('ln,lc->nc', I ** 2.2, col[fa])
            # reaching roof height: land on the nearest pixel if close enough, else fall past
            idx = np.where(fa)[0][h[fa] <= Y_ROOF]
            for k in idx:
                dd = ((xz - pos[k]) ** 2).sum(1)
                m = int(np.argmin(dd))
                if dd[m] < 42 ** 2:
                    state[k] = 2
                    lp[k] = pdp[m]
                    landed_at[k] = t
                    c = int(np.argmin(np.abs(CORNERS - lp[k])))
                    s = 0 if lp[k] < CORNERS[c] else 1
                    target[k] = CORNERS[c] + (-1 if s == 0 else 1) * (5 + 7.5 * min(slots[c, s], 16))
                    slots[c, s] += 1
                else:
                    state[k] = 4
                    fade_out[k] = t
        # leaves that missed: a last dim glimpse as they pass the roofline
        for k in np.where((state == 4) & (t - fade_out < 0.5) & (fade_out > 0))[0]:
            d2 = ((xz - pos[k]) ** 2).sum(1)
            buf += light(col[k], 0.5 * (1 - (t - fade_out[k]) / 0.5) * np.exp(-d2 / 16 ** 2))

        # on the roof: skitter toward the corner pile, rustle in the breeze
        roof = (state == 2) | (state == 3)
        if roof.any():
            gust_front = (t - 52.0) * 520
            blown = roof & (t > 52.0) & (gust_front > lp) & (landed_at < 56)
            calm = roof & ~blown
            step = np.where(landed_at > 56, 0, target - lp)
            v = np.clip(step * 1.2, -45, 45) * (1 + wind / 60)
            lp[calm & (state == 2)] += v[calm & (state == 2)] * DT
            state[(state == 2) & (np.abs(target - lp) < 1.0)] = 3
            # the big gust: everything goes, faster the further it has been pushed
            lp[blown] += blow_v[blown] * smoothstep(0, 1.2, t - 52 - lp[blown] / 520) * DT
            state[roof & (lp > G.length + 30)] = 4
            on = np.where((state == 2) | (state == 3))[0]
            jig = rustle(t)[on] * (0.6 + wind / 50) * np.where(state[on] == 3, 0.4, 1.2)
            land = np.exp(-(t - landed_at[on]) / 0.25) * (t > landed_at[on])       # a flash as it lands
            amp = np.where(state[on] == 3, 0.68, 0.6) * (1 + 0.08 * rustle(t)[on]) * (1 + 0.7 * land)
            w = np.where(state[on] == 3, 5.2, 4.5)
            I = amp[:, None] * np.exp(-((pdp[None, :] - (lp[on] + jig)[:, None]) / w[:, None]) ** 2)
            buf += np.einsum('ln,lc->nc', np.clip(I, 0, None) ** 2.2, col[on])
        buf *= keys(t, [(63, 1.0), (66, 0.0)])
        out[f][G.path] = buf
    return out
