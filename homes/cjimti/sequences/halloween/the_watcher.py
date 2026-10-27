"""The Watcher: The house wakes up: wing fronts are eyes, the porch is a toothy mouth."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, lerp, heartbeat, Flicker, nframes

CODE = 'SC1'
TITLE = 'The Watcher'
KIND = 'show'
DESCRIPTION = 'The house wakes up. The wing fronts are eyes that look around and blink; the porch is a toothy mouth that talks, laughs and lunges.'

AMBER = hexc('#ffa000')
EYE_RED = hexc('#ff0800')
TOXIC = hexc('#30ff10')
ORANGE = hexc('#ff3000')
PALE = hexc('#ffd070')
DEEP_RED = hexc('#a00000')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')
RED = hexc('#ff0000')


def render(G, seed=1):
    rng = np.random.default_rng(seed)
    D = 66.0
    out = np.zeros((nframes(D), G.N, 3))


    eyes = [(G.seg['Left'], G.span_u(G.seg['Left'])), (G.seg['Right'], G.span_u(G.seg['Right']))]
    M, uM = G.seg['Porch Front'], G.span_u(G.seg['Porch Front'])
    O = np.concatenate([G.seg['Side'], G.seg['Porch Left'], G.seg['Porch Right']])
    flick = Flicker(rng, G.N, 0.3, 1.5)
    ember = Flicker(rng, G.N, 1.0, 4.0)

    blinks = [9.0, 16.5, 24.2, 31.0, 35.6]
    syl, t = [], 28.3
    while t < 37.5:
        d = rng.uniform(0.12, 0.3)
        syl.append((t, d, rng.uniform(0.5, 1.0)))
        t += d + rng.uniform(0.05, 0.22)
    for k in range(4):                       # MUA-HA-HA-HA
        for j in range(4):
            syl.append((38.3 + k * 1.35 + j * 0.2, 0.15 if j else 0.3, 1.0))

    def talk(t):
        e = 0.0
        for s, d, a in syl:
            if s <= t <= s + d:
                e = max(e, a * np.sin(np.pi * (t - s) / d) ** 2)
        return e

    teeth = 1 - np.abs(2 * (((uM + 1) / 2 * 9) % 1) - 1)   # 9 pointed teeth
    teeth = teeth ** 1.3
    corners = 1 - 0.6 * np.abs(uM) ** 4

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        fl = 1 + 0.04 * flick(t)
        o = keys(t, [(3, 0), (5.5, 1), (44, 1), (46, 0.4), (49, 0.35), (49.5, 1.05), (50, 1.05), (50.01, 0),
                     (57.5, 0), (59, 0.2), (62, 0.2), (62.5, 0)])
        o *= 1 - max([max(0.0, 1 - abs(t - b) / 0.13) for b in blinks])
        gaze = keys(t, [(5, 0), (6.5, -0.9), (10, -0.9), (11.3, 0.85), (14.5, 0.85), (15.3, 0.3), (17.3, -0.45),
                        (19.8, -0.45), (20.0, 0), (28, 0), (30, 0.15), (32, -0.1), (44, 0), (57.5, -0.9), (62.5, 0.9)])
        pw = keys(t, [(5, 0.06), (19.9, 0.06), (20.2, 0.14), (24, 0.08), (44, 0.05), (49.4, 0.03)])
        anger = keys(t, [(28, 0), (38, 0.35), (44, 0.7), (46, 1.0)])
        eI = keys(t, [(3, 0), (5.5, 0.85), (44, 0.9), (49, 0.8), (49.5, 1.0), (50, 1.0), (50.01, 0), (57.5, 0),
                      (59, 0.5), (62.5, 0.5)])
        ecol = TOXIC if t > 55 else lerp(AMBER, EYE_RED, anger)
        for idx, u in eyes:
            lid = np.clip((o - np.abs(u)) / 0.08, 0, 1)
            shape = 0.55 + 0.45 * (1 - u ** 2)
            pupil = np.clip((np.abs(u - gaze * 0.55) - pw) / 0.04, 0, 1)
            fr[idx] += light(ecol, eI * lid * shape * (0.03 + 0.97 * pupil) * fl[idx])

        # mouth
        grin = keys(t, [(20.5, 0), (23, 0.7), (44, 0.7), (46, 0.35), (49, 0.35), (49.4, 0)])
        mo = grin + (0.4 * talk(t) if 28 < t < 44 else 0.0)
        reveal = keys(t, [(20.5, 0), (22.5, 1.1)])
        rmask = np.clip((reveal - np.abs(uM)) / 0.1, 0, 1)
        mcol = lerp(lerp(ORANGE, PALE, teeth[:, None] * min(1, mo * 1.5)), EYE_RED, anger * 0.6)
        fr[M] += perc(mo * corners * (0.25 + 0.75 * teeth) * rmask)[:, None] * mcol
        fr[M] += light(DEEP_RED, 0.45 * mo * (1 - teeth) * rmask)

        # head outline
        oI = keys(t, [(2, 0), (5, 0.18), (44, 0.18), (49.4, 0.18), (49.5, 0)])
        if 44 < t < 49.5:
            oI += 0.4 * heartbeat(t, 44, keys(t, [(44, 1.0), (49.5, 0.45)]))
        ocol = lerp(PURPLE, RED, anger)
        fr[O] += light(ocol, oI * (1 + 0.15 * np.sin(2 * np.pi * t / 4)) * fl[O])

        # the lunge
        if 50 <= t < 50.45:
            strobe = any(s <= t < s + 0.06 for s in (50.0, 50.16, 50.32))
            fr[:] = WHITE * (1.0 if strobe else 0.15)
        elif t >= 50.45:
            e = 0.35 * np.exp(-(t - 50.45) / 1.8) * np.clip(ember(t), 0, 1) ** 2
            fr[:] += light(RED, e)
    return out
