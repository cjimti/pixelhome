"""Ball Drop: Seen from the street the Porch Front is the far, high top of a tower and the two porch
sides are its poles. A faceted crystal ball (a real sphere in 3-D, spinning) is raised to the top,
then drops toward the street over thirty seconds while the crowd on the wings snaps photos faster
and faster. It lands on the stroke of midnight and the crowd erupts."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'NY02'
TITLE = 'Ball Drop'
KIND = 'show'
DESCRIPTION = 'The porch is the tower: a spinning crystal ball rises to the far Porch Front, then drops toward the street while the crowd on the wings flashes cameras. Midnight.'

GOLD = hexc('#ffb030')
CHAMP = hexc('#ffd890')
SILVER = hexc('#c0d4ff')
ICE = hexc('#80b8ff')
ROSE = hexc('#ff6080')
WHITE = hexc('#fff6ea')
NAVY = hexc('#081440')
FACETS = np.array([hexc(c) for c in ('#fff0d0', '#ffb030', '#c0d4ff', '#80b8ff', '#ffc8b0', '#ffffff', '#ffd890', '#d0e0ff')])

T_RAISE, T_TOP, T_DROP, T_LAND = 10.0, 17.0, 20.0, 50.0
Z_TOP, Z_BOT = -500.0, -175.0


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 66.0
    out = np.zeros((nframes(D), G.N, 3))
    P = G.pos
    PL, PR, PF = G.seg['Porch Left'], G.seg['Porch Right'], G.seg['Porch Front']
    wings = np.concatenate([G.seg['Left'], G.seg['Right']])
    poles = np.concatenate([PL, PR])
    cx = 0.5 * (P[PL, 0].mean() + P[PR, 0].mean())
    R = 205.0
    # pole "height" seen from the street: 0 at the front (bottom), 1 at the back (top)
    h = np.zeros(G.N)
    h[poles] = (P[poles, 2] - (-150)) / (-565 - (-150))
    facet_tw = rng.uniform(0, 2 * np.pi, 96)
    shimmer = Flicker(rng, G.N, 0.3, 1.2)
    # inner ends of the wings: where the crowd presses toward the tower
    wl = G.seg['Left']
    wr = G.seg['Right']
    w_in = np.zeros(G.N)
    w_in[wl] = (P[wl, 0] - P[wl, 0].min()) / np.ptp(P[wl, 0])       # 1 at the porch end
    w_in[wr] = (P[wr, 0].max() - P[wr, 0]) / np.ptp(P[wr, 0])
    wing_dist = np.zeros(G.N)
    wing_dist[wl] = P[wl, 0].max() - P[wl, 0]
    wing_dist[wr] = P[wr, 0] - P[wr, 0].min()

    grp = (wing_dist // 32).astype(int) + np.where(np.isin(np.arange(G.N), wr), 40, 0)
    jump_f = rng.uniform(1.4, 2.2, 80)
    jump_p = rng.uniform(0, 1, 80)
    crowd_col = np.array([GOLD, SILVER, CHAMP, GOLD])[rng.integers(0, 4, 80)]
    murmur = Flicker(rng, G.N, 0.1, 0.6)

    # camera flashes from the crowd: (time, node, strength); rate swells to midnight
    flashes = []
    t = 1.0
    while t < D - 4:
        rate = keys(t, [(0, 0.6), (T_DROP, 2.0), (T_LAND - 10, 6.0), (T_LAND, 26.0), (T_LAND + 2, 30.0), (T_LAND + 10, 4.0), (D, 0.5)])
        t += rng.exponential(1 / rate)
        flashes.append((t, rng.choice(wings), rng.uniform(0.5, 1.0)))
    flashes = np.array(flashes)

    def ball_z(t):
        if t < T_RAISE:
            return Z_BOT - 260
        if t < T_TOP:
            return lerp(Z_BOT - 60, Z_TOP, smoothstep(T_RAISE, T_TOP, t))
        if t < T_DROP:
            return Z_TOP
        if t < T_LAND:
            u = (t - T_DROP) / (T_LAND - T_DROP)
            return lerp(Z_TOP, Z_BOT, u * u * (3 - 2 * u) * 0.25 + u * 0.75)
        return Z_BOT

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fr += light(NAVY, keys(t, [(0, 0), (3, 0.14), (D - 4, 0.14), (D, 0)]))

        # the crowd waiting on the wings: a low warm murmur that grows toward midnight
        crowd = keys(t, [(0, 0), (4, 0.1), (T_DROP, 0.14), (T_LAND, 0.24), (T_LAND + 0.5, 0)])
        fr[wings] += light(GOLD, crowd * (1 + 0.3 * murmur(t)[wings]) * (0.6 + 0.4 * w_in[wings]))

        # the tower: poles drawn bottom-up in silver, the crown in gold
        build = keys(t, [(3, -0.1), (9, 1.1)])
        tower = keys(t, [(3, 0), (9, 1), (T_LAND, 1), (T_LAND + 1, 0.6), (D - 3, 0)])
        pole = smoothstep(build - 0.06, build, h) * 0 + (h <= build) * 1.0
        pole_I = np.zeros(G.N)
        pole_I[poles] = tower * 0.22 * pole[poles] * (0.85 + 0.15 * np.cos(h[poles] * 40 - t * 2))
        fr += light(SILVER, pole_I)
        crown = keys(t, [(8.5, 0), (9.5, 0.45), (T_LAND, 0.45), (T_LAND + 0.2, 1.0), (T_LAND + 3, 0.5), (D - 3, 0)])
        fr[PF] += light(GOLD, crown * (0.85 + 0.15 * shimmer(t)[PF]))

        # the ball: a sphere of light, faceted, spinning faster as it falls
        bz = ball_z(t)
        c = np.array([cx, 150.0, bz])
        v = P - c
        d = np.linalg.norm(v, axis=1)
        on = keys(t, [(T_RAISE - 1, 0), (T_RAISE + 0.5, 1), (T_LAND, 1), (T_LAND + 0.1, 1.6), (T_LAND + 2.5, 0.7), (D - 3, 0)])
        if on > 0:
            spin = 0.25 * t + 0.03 * max(0, t - T_DROP) ** 2
            lon = (np.arctan2(v[:, 0], v[:, 2]) / (2 * np.pi) + spin) % 1
            ring = np.clip(d / R, 0, 1.5)
            fid = (np.floor(lon * 16).astype(int) * 3 + np.floor(ring * 6).astype(int)) % 96
            tw = 0.55 + 0.45 * np.sin(facet_tw[fid] + t * (3 + 4 * smoothstep(T_DROP, T_LAND, t)))
            body = smoothstep(R + 25, R - 35, d)
            rim = np.exp(-((d - R) / 35) ** 2)
            col = FACETS[fid % len(FACETS)]
            fr += light(col, on * body * (0.35 + 0.6 * tw ** 3))
            fr += light(WHITE, on * 0.5 * rim * tw)
            # glow spilling from the ball onto the wings as it nears the street
            near = np.exp(-np.clip(d - R, 0, None) / 120)
            fr[wings] += light(CHAMP, on * 0.35 * near[wings] * smoothstep(T_LAND - 8, T_LAND, t))

        # the last ten seconds: the crowd counts, a pulse runs out along both wings each second
        if T_LAND - 10 <= t < T_LAND:
            ph = (t - (T_LAND - 10)) % 1.0
            k = int(t - (T_LAND - 10))
            pulse = np.exp(-((wing_dist - ph * 520) / 50) ** 2) * np.exp(-ph / 0.6)
            fr += light(CHAMP, (0.5 + 0.05 * k) * pulse * (wing_dist > 0))

        # midnight: the crowd erupts outward from the tower, gold and silver
        if t >= T_LAND:
            tb = t - T_LAND
            front = tb * 600
            lit = smoothstep(front, front - 80, wing_dist) * (w_in >= 0)
            wave = np.exp(-((wing_dist - front) / 40) ** 2)
            # the crowd jumps: groups of ~30 units bounce at their own pace
            col = crowd_col[grp]
            bounce = np.abs(np.sin(np.pi * (tb * jump_f[grp] + jump_p[grp]))) ** 2
            fall = keys(tb, [(0, 1), (3, 1), (8, 0.45), (D - T_LAND - 3, 0)])
            m = np.zeros(G.N)
            m[wings] = 1
            fr += light(col, 0.8 * fall * lit * m * (0.45 + 0.55 * bounce))
            fr += light(WHITE, wave * m)
            # streamers tumble down the poles (toward the street)
            sw = np.zeros(G.N)
            for j in range(4):
                y0 = (tb * 0.35 + j * 0.25) % 1
                sw[poles] += np.exp(-((h[poles] - (1 - y0)) / 0.03) ** 2)
            fr += light(ROSE, 0.7 * fall * sw * smoothstep(0.5, 1.5, tb))
            fr += light(WHITE, 0.6 * np.exp(-tb / 0.15))

        # camera flashes: a pixel pops white and its neighbours catch a little
        live = flashes[(flashes[:, 0] <= t) & (flashes[:, 0] > t - 0.25)]
        for tf, node, a in live:
            e = a * np.exp(-(t - tf) / 0.05)
            nd = np.abs(G.pd - G.pd[int(node)])
            fr += light(WHITE, e * np.exp(-(nd / 6) ** 2))
    return out
