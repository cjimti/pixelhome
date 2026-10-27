"""Two Hearts: the two wing fronts are two hearts, beating at different tempos. Every lub sends a pulse
along the roof; pulses from the two hearts collide on the porch and spark where they meet, so the spark's
position shows how far apart the hearts are. Then each heart starts listening: a spark past the
midpoint means that heart was early, so it eases off (a phase-locked loop). The spark walks in to the
porch centre and locks there, and the house beats as one."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'VD02'
TITLE = 'Two Hearts'
KIND = 'show'
DESCRIPTION = ('The two wings are two hearts beating out of step. Their pulses race along the roof and spark '
               'where they collide; as the hearts fall into sync the spark settles on the porch.')

ROSE = hexc('#ff2448')
CRIMSON = hexc('#ff0818')
GOLD = hexc('#ffa040')
WARM = hexc('#ffc890')
BLUSH = hexc('#ff5a50')
WINE = hexc('#a00008')


def envelope(x):
    """Lub-dub over one cycle, x in [0,1)."""
    return np.exp(-((x - 0.03) / 0.05) ** 2) + 0.65 * np.exp(-((x - 0.24) / 0.06) ** 2)


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 62.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    L = G.length
    pf = G.seg['Porch Front']
    c = G.pd[pf[len(pf) // 2]]
    order = np.argsort(G.path)                      # node -> path position
    left, right = G.seg['Left'], G.seg['Right']
    cl, cr = G.pd[left].mean(), G.pd[right].mean()
    wing = np.zeros(G.N)
    wing[G.pi[left]] = 1 - G.span_u(left) ** 2
    wing[G.pi[right]] = 1 - G.span_u(right) ** 2
    isL = np.zeros(G.N, bool); isL[G.pi[left]] = True
    isR = np.zeros(G.N, bool); isR[G.pi[right]] = True
    fl = Flicker(rng, G.N, 0.2, 0.8)
    V = 640.0

    # simulate hearts and pulses together. Rightward pulses leave the left heart, leftward pulses the
    # right heart; when two cross they annihilate in a spark. Each heart "listens" to where the spark
    # landed: if it was on the far side of the midpoint, that heart was early, so it eases off.
    start = (3.0, 7.5)
    mid = 0.5 * ((cl + 200) + (cr - 238))
    p = np.array([0.0, 0.62])
    ph = np.zeros((F, 2))
    beats = [[], []]
    R, Lp, sparks, pulses = [], [], [], []
    err, tau = 0.0, 0.6
    for f in range(F):
        t = f * DT
        g = keys(t, [(26, 0.0), (36, 0.5), (42, 1.0)])
        f1 = keys(t, [(0, 1.02), (44, 1.06), (52, 1.06), (60, 0.8)])
        f2 = keys(t, [(0, 1.27), (32, 1.2), (42, 1.06), (52, 1.06), (60, 0.8)])
        kp = g / (2 * tau)
        dp = np.array([f1 * (1 - kp * err), f2 * (1 + kp * err)])
        err *= np.exp(-DT / tau)
        new = p + dp * DT
        for i, pos0 in ((0, cl + 200), (1, cr - 238)):
            if np.floor(new[i]) > np.floor(p[i]) and t > start[i]:
                beats[i].append(t)
                (R if i == 0 else Lp).append(pos0)
        p = new
        ph[f] = p
        R = [x + V * DT for x in R if x + V * DT < cr - 220]
        Lp = [x - V * DT for x in Lp if x - V * DT > cl + 180]
        R.sort(reverse=True)
        Lp.sort()
        while R and Lp and R[0] >= Lp[0]:
            xs = 0.5 * (R[0] + Lp[0])
            sparks.append((t, xs))
            err = float(np.clip((xs - mid) / V, -0.8, 0.8))
            R.pop(0)
            Lp.pop(0)
        pulses.append((list(R), list(Lp)))

    for f in range(F):
        t = f * DT
        buf = np.zeros((G.N, 3))
        master = keys(t, [(D - 5, 1), (D - 0.3, 0)])
        on = [smoothstep(start[0], start[0] + 1.5, t), smoothstep(start[1], start[1] + 1.5, t)]
        e = [envelope(ph[f, 0] % 1) * on[0], envelope(ph[f, 1] % 1) * on[1]]
        sync = smoothstep(42, 47, t)
        # the hearts themselves: a resting glow that squeezes in toward the middle on each beat
        rest = 0.17 + 0.04 * fl(t)
        IL = (rest * on[0] + 0.85 * e[0] * (0.25 + 0.75 * wing)) * isL
        IR = (rest * on[1] + 0.85 * e[1] * (0.25 + 0.75 * wing)) * isR
        colR = lerp(CRIMSON, ROSE, sync)
        buf += light(ROSE, IL * master) + light(colR, IR * master)

        # pulses travelling outward to the free ends
        out_l = np.zeros(G.N)
        out_r = np.zeros(G.N)
        for tb in beats[0]:
            sb = t - tb
            if 0 < sb < 3:
                out_l = np.maximum(out_l, np.exp(-sb / 1.5) * np.exp(-((pdp - (cl - 200 - V * sb)) / 28) ** 2) * (pdp < cl - 150))
        for tb in beats[1]:
            sb = t - tb
            if 0 < sb < 3:
                out_r = np.maximum(out_r, np.exp(-sb / 1.5) * np.exp(-((pdp - (cr + 238 + V * sb)) / 28) ** 2) * (pdp > cr + 190))
        buf += light(ROSE, 0.45 * out_l * master) + light(colR, 0.45 * out_r * master)
        # pulses toward each other (simulated: they annihilate where they meet)
        toward = np.zeros(G.N)
        away = np.zeros(G.N)
        for x in pulses[f][0]:
            toward = np.maximum(toward, np.exp(-((pdp - x) / 28) ** 2))
        for x in pulses[f][1]:
            away = np.maximum(away, np.exp(-((pdp - x) / 28) ** 2))
        k = keys(t, [(0, 0.55), (42, 0.55), (48, 0.75)])
        buf += light(ROSE, k * toward * master) + light(colR, k * away * master)
        # sparks where they met; when in sync they all land on the same spot and pile up
        glow = np.zeros(G.N)
        for ts, xs in sparks:
            sb = t - ts
            if 0 <= sb < 6:
                w = 14 + 90 * sb
                flash = np.exp(-sb / 0.18) * np.exp(-((pdp - xs) / (14 + 40 * sb)) ** 2)
                buf += light(WARM, 1.1 * flash * master)
                glow += np.exp(-sb / (0.7 + 1.6 * sync)) * np.exp(-((pdp - xs) / w) ** 2)
        glow = np.clip(glow, 0, 1.2)
        gcol = lerp(lerp(GOLD, CRIMSON, sync), lerp(GOLD, WARM, sync), np.clip(glow - 0.6, 0, 0.6)[:, None] / 0.6)
        buf += (np.clip((0.45 + 0.15 * sync) * glow * master, 0, None) ** 2.2)[:, None] * gcol

        # once in sync the whole porch becomes the shared heart
        if sync > 0:
            ej = 0.5 * (e[0] + e[1])
            dist = np.abs(pdp - c)
            porch = np.exp(-(dist / 330) ** 2)
            buf += light(WINE, sync * master * (0.18 + 0.55 * ej) * porch)
            side = (pdp < 490) * (1 - pdp / 490) * 0 + (pdp < 490) * np.clip(pdp / 490, 0, 1)
            buf += light(WINE, 0.25 * sync * master * ej * side)
        out[f][G.path] = buf
    return out
