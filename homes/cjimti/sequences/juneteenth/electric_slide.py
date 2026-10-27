"""Electric Slide: The cookout line dance, done by the whole roof. Every run is a row of dancers; the
step pattern (grapevine right, grapevine left, back, forward, turn) is a vector in the yard, so dancers
on runs that point that way slide and dancers on the perpendicular runs bounce in place. Each quarter
turn swaps who slides and who bounces. One dancer at the free end of the Right wing is always a little
late, goes the wrong way on the first grapevine, bumps into a neighbour, and keeps dancing after the music stops."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, nframes

CODE = 'JT03'
TITLE = 'Electric Slide'
KIND = 'show'
DESCRIPTION = ('The whole roof does the Electric Slide. Each quarter turn swaps which runs slide and which bounce; '
               'one dancer on the end is always late, goes the wrong way, and keeps going after the music stops.')

RED = hexc('#e8202a')
GREEN = hexc('#14b048')
GOLD = hexc('#ffb020')
WHITE = hexc('#fff4e0')
BLUSH = hexc('#ff2050')
FLOOR = hexc('#103018')

BEAT = 0.5
T0 = 8.0                    # first beat of the dance
WALLS = 4
STEP = 9.0                  # one step, in layout units

# (beat in the 16-count, frame axis 'a' right / 'b' back, signed steps)
PATTERN = [(0, 'a', 1), (1, 'a', 1), (2, 'a', 1), (4, 'a', -1), (5, 'a', -1), (6, 'a', -1),
           (8, 'b', 1), (9, 'b', 1), (10, 'b', 1), (12, 'b', -1.5), (14, 'b', -1.5)]
TOUCH = [3, 7, 11, 15]


def offset(beat, steps):
    """Formation offset (a, b) at a (float) beat, from [(beat, axis, n)], each step eased over half a beat."""
    a = b = 0.0
    for bt, ax, n in steps:
        u = smoothstep(bt, bt + 0.55, beat) * n * STEP
        if ax == 'a':
            a += u
        else:
            b += u
    return a, b


def render(G, seed=3):
    rng = np.random.default_rng(seed)
    D = 52.0
    out = np.zeros((nframes(D), G.N, 3))
    pdp = G.pd[G.path]
    P = G.pos[G.path]
    END = T0 + WALLS * 16 * BEAT            # music stops

    # dancers: evenly spaced inside each run; each knows its run's direction in the yard
    base, dirs, cols, seg_of, lo, hi = [], [], [], [], [], []
    palette = [RED, GREEN, GOLD]
    for k, (name, pi) in enumerate(G.path_segments()):
        i0, i1 = pi.min(), pi.max()
        d0, d1 = pdp[i0], pdp[i1]
        v = P[i1] - P[i0]
        v = np.array([v[0], v[2]]) / np.linalg.norm([v[0], v[2]])
        n = int((d1 - d0 - 30) // 38)
        ps = np.linspace(d0 + 18, d1 - 18, n)
        for j, p in enumerate(ps):
            base.append(p); dirs.append(v); cols.append(palette[(j + k) % 3])
            seg_of.append(k); lo.append(d0); hi.append(d1)
    base, dirs, cols = np.array(base), np.array(dirs), np.array(cols)
    lo, hi = np.array(lo), np.array(hi)
    M = len(base)
    late = int(np.argmax(base))             # the dancer at the right free end
    nb = late - 1
    sat = np.zeros(G.N)
    seg_pix = np.zeros(G.N, int)
    for k, (name, pi) in enumerate(G.path_segments()):
        seg_pix[pi] = k
    same = np.array(seg_of)[:, None] == seg_pix[None, :]
    appear = rng.uniform(2.5, 5.5, M)

    def pose(beat, late_one=False):
        """World displacement (x, z) of the formation and the touch envelope."""
        if beat < 0:
            return np.zeros(2), 0.0
        wall = min(int(beat // 16), WALLS - 1)
        bb = beat - wall * 16
        steps = PATTERN
        if late_one and wall == 0:          # goes the wrong way, then hurries back
            steps = [(bt, ax, -n if (ax == 'a' and bt < 3) else n) for bt, ax, n in PATTERN]
            steps = steps + [(7.2, 'a', 3), (7.6, 'a', 3)]
        a, b = offset(min(bb, 16.0), steps)
        th = (wall + smoothstep(14, 15, bb)) * np.pi / 2 if beat < WALLS * 16 else WALLS * np.pi / 2
        r_hat = np.array([np.cos(th), np.sin(th)])
        b_hat = np.array([np.sin(th), -np.cos(th)])
        touch = max([np.exp(-((bb - tb - 0.1) / 0.16) ** 2) for tb in TOUCH])
        return a * r_hat + b * b_hat, touch

    for f in range(len(out)):
        t = f * DT
        beat = (t - T0) / BEAT
        dancing = T0 <= t < END
        disp, touch = pose(beat) if dancing else (np.zeros(2), 0.0)
        along = dirs @ disp                                  # slide along the run
        perp = np.abs(dirs[:, 0] * disp[1] - dirs[:, 1] * disp[0])  # can't slide: bounce
        step_phase = (beat % 1) if dancing else 0.0
        bounce = np.exp(-((step_phase - 0.3) / 0.18) ** 2) * (perp > 1) * 0.6 if dancing else 0.0
        pos = base + along
        amp = np.full(M, 0.62) + 0.3 * touch + 0.25 * bounce
        width = np.full(M, 6.5) + 5 * bounce * np.ones(M)
        amp = amp * smoothstep(appear, appear + 1.2, t)

        # the late one
        bonk = 0.0
        if dancing:
            ld, lt = pose(beat - 0.22, late_one=True)
            pos[late] = base[late] + dirs[late] @ ld
            lp = abs(dirs[late, 0] * ld[1] - dirs[late, 1] * ld[0])
            amp[late] = 0.62 + 0.3 * lt + 0.25 * (lp > 1) * np.exp(-((((beat - 0.22) % 1) - 0.3) / 0.18) ** 2) * 0.6
            gap = pos[late] - pos[nb]
            if gap < 24:                                     # bump
                bonk = smoothstep(24, 12, gap)
                pos[late] = max(pos[late], pos[nb] + 13)
                pos[nb] -= 7 * bonk
        if t >= END:                                         # music stops; everyone holds the pose...
            hold = keys(t, [(END, 1.0), (END + 0.4, 0.75), (D - 4, 0.75), (D, 0)])
            amp *= hold
            # ...except the late one, who does one more grapevine, notices, and blushes
            sb = (t - END - 1.2) / BEAT
            sa, _ = offset(sb, [(0, 'a', 1), (1, 'a', 1), (2, 'a', 1), (6, 'a', -1.5), (7, 'a', -1.5)])
            pos[late] = base[late] + sa * (dirs[late] @ np.array([1.0, 0.0]))
        pos = np.clip(pos, lo + 4, hi - 4)

        d = pdp[None, :] - pos[:, None]
        blob = np.exp(-(d / width[:, None]) ** 2) * same
        I = blob * amp[:, None]
        buf = np.einsum('mn,mc->nc', perc(np.clip(I, 0, 1.2)), cols)
        if bonk > 0:
            buf += light(WHITE, 0.9 * bonk * np.exp(-((pdp - 0.5 * (pos[late] + pos[nb])) / 10) ** 2))
        if t >= END + 4.4:
            bl = keys(t, [(END + 4.4, 0), (END + 5.0, 1), (D - 3, 1), (D, 0)])
            buf += light(BLUSH, 0.75 * bl * np.exp(-((pdp - pos[late]) / 9) ** 2))
            buf[:, :] *= 1.0
        # count-in on the porch: 5, 6, 7, 8
        if 6.0 <= t < T0:
            c = ((t - 6.0) / BEAT) % 1
            buf += light(GOLD, 0.25 * np.exp(-c / 0.15) * (seg_pix == 3))
        # the floor: a low green bass on every beat while the music plays
        if dancing:
            buf += light(FLOOR, 0.16 + 0.06 * np.exp(-step_phase / 0.2))
        out[f][G.path] = buf
    return out
