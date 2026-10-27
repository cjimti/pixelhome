"""Dog Tags: All-night loop. Every 15 units along the roof hangs a pair of dog tags, two pixels of
dull steel. Each tag turns slowly on its chain (its own pendulum period, its partner slightly out of
step) and is a small mirror: its brightness is the specular reflection (Blinn-Phong, n.h to a high
power) of two moving lights toward a viewer in the street, using real 3-D positions. A cool moon
drifts across the sky over the loop and a warm watch-lamp circles the house, and a slow breeze rolls
along the roof turning the tags together, so the glints travel in soft bands wherever the angles
line up, while tags facing away stay dull."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, nframes, looped

CODE = 'VT06'
TITLE = 'Dog Tags'
KIND = 'ambient'
DESCRIPTION = ('A pair of dog tags hangs every few inches along the roof, turning slowly on their chains and '
               'catching the moonlight and a passing lamp.')

STEEL = hexc('#7c86b8')
MOON = hexc('#c8d4ff')
LAMP = hexc('#ffb860')
FLOOR_COLOR = hexc('#3a48ff')
FLOOR = 0.08
LOOP = 150.0


def norm(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def render(G, seed=36):
    rng = np.random.default_rng(seed)
    P = G.pos
    pd = G.pd
    N = G.N
    # tags: pixels grouped in pairs every 15 units; gaps between pairs stay dim steel
    slot = pd % 15.0
    tag = np.where(slot < 4.5, 0, np.where(slot < 9.0, 1, -1))
    pair = np.floor(pd / 15.0).astype(int)
    npair = pair.max() + 1
    # yaw pendulum per pair, periods that divide the loop so it is exactly periodic
    kp = rng.integers(22, 46, npair)
    per = LOOP / kp
    amp = rng.uniform(0.12, 0.28, npair)
    ph = rng.uniform(0, 2 * np.pi, npair)
    base = rng.normal(0, 0.08, npair)
    lag = np.where(tag == 1, 0.7, 0.0)                     # the second tag swings a little behind
    viewer = np.array([0.0, 160.0, 1600.0])
    V = norm(viewer - P)

    def draw(D):
        out = np.zeros((nframes(D), N, 3), np.float32)
        for f in range(len(out)):
            t = f * DT
            # a slow breeze rolls along the roof and turns the tags together as it passes
            breeze = 0.55 * np.sin(2 * np.pi * (pd / 650 - t / (LOOP / 5))) + 0.3 * np.sin(2 * np.pi * (pd / 1700 + t / (LOOP / 2)))
            yaw = base[pair] + breeze + amp[pair] * np.sin(2 * np.pi * t / per[pair] + ph[pair] - lag)
            n = np.stack([np.sin(yaw), np.zeros(N), np.cos(yaw)], -1)
            # moon: across the sky once per loop (and back), always above and a little in front
            a = 1.2 * np.sin(2 * np.pi * t / LOOP)
            moon = np.array([np.sin(a) * 4000, 700.0, np.cos(a) * 2500 - 900])
            # watch-lamp: circles the house at roof height, twice per loop
            b = 2 * np.pi * t / (LOOP / 2)
            lamp = np.array([16 + 820 * np.cos(b), 230.0, -390 + 620 * np.sin(b)])
            I = np.zeros((N, 3))
            for src, col, k, shin in ((moon, MOON, 0.36, 30), (lamp, LAMP, 0.36, 20)):
                Ld = norm(src - P)
                H = norm(Ld + V)
                s = np.clip((n * H).sum(1), 0, 1) ** shin
                if src is lamp:
                    d = np.linalg.norm(src - P, axis=1)
                    s = s / (1 + (d / 700) ** 2) * 1.6
                I += perc(k * np.clip(s, 0, 1.2))[:, None] * col
            steel = np.where(tag >= 0, 0.11, 0.07)
            fr = perc(steel)[:, None] * STEEL + I
            fr *= np.where(tag >= 0, 1.0, 0.6)[:, None]
            cap = perc(0.44) / np.maximum(fr.max(1), 1e-6)
            out[f] = fr * np.minimum(1.0, cap)[:, None]
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))
