"""Blush: the house has a face (the wing fronts are cheeks, the porch front a smile) and it gets
complimented. A gold whisper arrives from the right free end; the cheeks blush, and the blush is a
real heat-diffusion simulation along the roof, spreading round the corners and coloured by
temperature from wine through rose to a white-hot glow. A second compliment overheats it, so the
house fans itself with cool strokes from both free ends. Just as it recovers, one more whisper, and
the whole house goes red at once."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'VD05'
TITLE = 'Blush'
KIND = 'show'
DESCRIPTION = ('The house is paid a compliment and blushes: the colour spreads from the cheeks round the corners, '
               'overheats, gets fanned down from both ends, and then one more compliment sets it off again.')

GOLD = hexc('#ffa040')
WARM = hexc('#ffb070')
FAN = hexc('#ffd8b0')

BLUSH_MAP = colormap([(0.0, (0, 0, 0)), (0.08, (0.012, 0.0, 0.001)), (0.25, (0.11, 0.002, 0.006)),
                      (0.5, (0.45, 0.012, 0.04)), (0.75, (0.85, 0.07, 0.11)), (0.95, (1.0, 0.2, 0.16)),
                      (1.15, (1.0, 0.45, 0.3)), (1.4, (1.0, 0.7, 0.5))])


def render(G, seed=25):
    rng = np.random.default_rng(seed)
    D = 58.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    seg = {name: idx for name, idx in G.path_segments()}
    cheekL, cheekR = pdp[seg['Left']].mean(), pdp[seg['Right']].mean()
    pfi = seg['Porch Front']
    c = pdp[pfi].mean()
    upf = np.zeros(G.N)
    upf[pfi] = np.linspace(-1, 1, len(pfi))
    mouth = np.zeros(G.N, bool); mouth[pfi] = True
    fl = Flicker(rng, G.N, 0.3, 1.5)
    shimmer = Flicker(rng, G.N, 1.0, 3.0)

    # heat equation on the path, flux form for the uneven spacing; free ends insulated
    dx = np.diff(pdp)
    cell = np.concatenate([[dx[0] / 2], (dx[:-1] + dx[1:]) / 2, [dx[-1] / 2]])
    KAPPA = 9000.0
    # Laplacian operator; backward Euler (I - dt*k*A)^-1 is unconditionally stable for the tiny corner gaps
    A = np.zeros((G.N, G.N))
    for i, d in enumerate(dx):
        w = 1.0 / d
        A[i, i] -= w / cell[i]; A[i, i + 1] += w / cell[i]
        A[i + 1, i + 1] -= w / cell[i + 1]; A[i + 1, i] += w / cell[i + 1]
    step = {k: np.linalg.inv(np.eye(G.N) - DT * KAPPA * k * A) for k in (1.0, 4.0)}
    T = np.zeros(G.N)
    src_shape = np.exp(-((pdp - cheekL) / 70) ** 2) + np.exp(-((pdp - cheekR) / 80) ** 2)
    whispers = [(6.0, 9.2), (22.5, 25.5), (46.0, 48.6)]      # leaves the free end, reaches the porch

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(0, 0), (1.5, 1), (D - 4, 1), (D - 0.3, 0)])
        # sources: the cheeks heat up after each whisper
        q = (keys(t, [(9.0, 0), (10.5, 0.75), (15, 0.6), (19, 0.0)]) +
             keys(t, [(25.3, 0), (26.2, 1.5), (31.5, 1.35), (34, 0)]) +
             keys(t, [(48.4, 0), (48.7, 3.0), (49.6, 0)]))
        q_all = keys(t, [(48.6, 0), (48.9, 1.6), (49.8, 0)])
        kap = 4.0 if 48.5 < t < 50.5 else 1.0                # the last blush goes everywhere at once
        cool = 0.09
        fan = np.zeros(G.N)
        if 34.5 < t < 45.5:                                  # fanning strokes from both free ends
            for t0 in np.arange(34.5, 44.5, 1.25):
                s = t - t0
                if 0 < s < 3:
                    front = 330 * s
                    fan = np.maximum(fan, np.exp(-((pdp - front) / 90) ** 2) + np.exp(-((L - pdp - front) / 90) ** 2))
            fan *= keys(t, [(34.5, 0), (35.5, 1), (44, 1), (45.5, 0)])
        T = T + DT * (q * src_shape + q_all - cool * T - 0.9 * fan * T)
        T = np.clip(step[kap] @ T, 0, None)

        heat = T * (0.92 + 0.08 * fl(t))
        buf += BLUSH_MAP(heat)
        hot = np.clip(T - 1.0, 0, None)
        buf += light(WARM, 0.35 * hot * np.clip(shimmer(t), 0, 1))
        buf += light(FAN, 0.38 * fan * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t)) ** 2)

        # the smile: warm white on the porch front; bashful (narrow) while blushing, beaming at the end
        width = keys(t, [(0, 0.95), (9.5, 0.95), (12, 0.45), (20, 0.7), (25.5, 0.3), (36, 0.3), (44, 0.85),
                         (48.6, 0.85), (49.2, 0.2), (51.5, 0.2), (54, 1.0)])
        smile_I = keys(t, [(0, 0), (2, 0.34), (25.5, 0.34), (27, 0.2), (44, 0.34), (52, 0.34), (54, 0.45)])
        smile = smile_I * np.clip(1 - (upf / width) ** 2, 0, 1) ** 0.7 * mouth
        buf += light(WARM, smile)
        # the whispers: a little gold glint that runs in from the right free end to the porch
        for t0, t1 in whispers:
            if t0 <= t <= t1 + 0.4:
                u = smoothstep(t0, t1, t)
                p = lerp(L + 10, c + 60, u)
                wig = 6 * np.sin(2 * np.pi * 2.3 * t)
                a = 0.9 * (1 - smoothstep(t1, t1 + 0.4, t))
                buf += light(GOLD, a * np.exp(-((pdp - p - wig) / 9) ** 2))
                buf += light(WARM, 0.5 * a * np.exp(-((pdp - p - wig) / 3.5) ** 2))
        out[f][G.path] = buf * master
    return out
