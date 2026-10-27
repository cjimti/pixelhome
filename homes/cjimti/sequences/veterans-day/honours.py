"""Honours: The roofline is a line of soldiers at attention, one every 24 units along the path. A
reviewing officer (gold) enters at the free back end and walks the whole line, halting and turning
at each corner; each soldier snaps a salute as the officer approaches (its point leans and
brightens like a raised hand) and holds until the officer has passed, then stands down a shade
warmer. Then the seven riflemen take post at the seven fixed points of the house, its two free ends
and its five corners, and fire three volleys; the smoke from each drifts down the wind."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, smoothstep, Flicker, nframes

CODE = 'VT04'
TITLE = 'Honours'
KIND = 'show'
DESCRIPTION = ('An officer walks the ranks along the roof and each soldier salutes as he passes. Then riflemen '
               'at the two ends and five corners fire three volleys, and the smoke drifts away.')

NAVY = hexc('#1c34ff')
SILVER = hexc('#aab8ff')
WHITE = hexc('#fff0dc')
GOLD = hexc('#ff9a24')
FLASH = hexc('#ffd8a0')
SMOKE = hexc('#8a92b8')
RED = hexc('#ff1a14')


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    pd = G.pd
    P = G.pos
    pts = [G.path[i] for i in (0, 80, 178, 260, 331, 380, 500)]
    wp = [pd[k] for k in pts]

    # soldiers: one every 24 units of path; each pixel knows its soldier's centre
    SP = 24.0
    sid = np.round((pd - SP / 2) / SP)
    sc = sid * SP + SP / 2
    off = pd - sc
    breathe = Flicker(rng, G.N, 0.05, 0.2)

    # officer's walk: eased legs between the seven points, a short halt at each corner
    T0, V, halt = 3.0, 82.0, 0.7
    walk, t = [(T0 - 1.0, -60.0), (T0, wp[0])], T0
    for a, b in zip(wp[:-1], wp[1:]):
        t += (b - a) / V
        walk.append((t, b))
        t += halt
        walk.append((t, b))
    walk.append((t + 1.2, G.length + 70))
    t_end = t + 1.2
    salute = np.zeros(G.N)
    reviewed = np.zeros(G.N)

    volleys = [t_end + 5.5, t_end + 10.5, t_end + 15.5]
    wind = np.array([1.0, 0.0, 0.3])
    D = round(volleys[-1] + 11.0)
    out = np.zeros((nframes(D), G.N, 3))

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        on = keys(t, [(0, 0), (2.5, 1), (D - 5, 1), (D, 0)])
        fr += light(NAVY, 0.1 * on)

        p = keys(t, walk) if t < t_end + 0.1 else G.length + 200
        ahead = sc - p                                      # >0: officer has not reached him yet
        want = ((ahead < 95) & (ahead > -70)).astype(float)
        rate = np.where(want > salute, DT / 0.18, DT / 0.45)  # snap up, lower slowly
        salute = np.clip(salute + np.sign(want - salute) * rate, 0, 1)
        reviewed = np.maximum(reviewed, (ahead < -70).astype(float) * smoothstep(0, 1, 1 - salute))

        # a soldier: a soft point; saluting, it leans toward the officer and brightens
        lean = 4.5 * salute
        w = 3.2 + 1.6 * salute
        body = np.exp(-((off + lean * np.sign(ahead + 1e-6)) / w) ** 2)
        hand = salute * np.exp(-((off + 7.5 * np.sign(ahead + 1e-6)) / 2.6) ** 2)
        lvl = (0.3 + 0.07 * reviewed + 0.5 * salute) * on * (1 + 0.05 * breathe(t))
        col = lerp(lerp(SILVER, hexc('#ffb860'), 0.85 * reviewed[:, None]), WHITE, salute[:, None])
        fr += light(col, lvl * np.maximum(body, 0.9 * hand))

        # the officer
        if T0 - 1 < t < t_end + 0.1:
            fr += light(GOLD, 0.95 * np.exp(-((pd - p) / 9) ** 2))
            fr += light(GOLD, 0.25 * np.exp(-((pd - p) / 40) ** 2))

        # the firing party at the seven points
        party = keys(t, [(t_end + 1, 0), (t_end + 3, 1), (volleys[-1] + 6, 1), (volleys[-1] + 9, 0)])
        if party > 0:
            dpt = np.min([np.abs(pd - q) for q in wp], axis=0)
            aim = 0.0
            for v in volleys:
                aim = max(aim, smoothstep(v - 2.2, v - 0.05, t) * (t < v))
            fr += light(RED, party * (0.3 + 0.35 * aim) * np.exp(-(dpt / 7) ** 2))
            for v in volleys:
                tv = t - v
                if tv < 0 or tv > 7:
                    continue
                flash = np.exp(-tv / 0.12)
                fr += light(FLASH, flash * np.exp(-(dpt / (14 + 160 * tv)) ** 2) * 1.0)
                r = 15 + 120 * np.sqrt(tv)
                smoke = 0.0
                for k in pts:
                    c = P[k] + wind * 45 * tv
                    d = np.linalg.norm(P - c, axis=1)
                    smoke = np.maximum(smoke, np.exp(-(d / r) ** 2))
                fr += light(SMOKE, 0.42 * smoke * np.exp(-tv / 2.0) * smoothstep(0, 0.25, tv))
    return out
