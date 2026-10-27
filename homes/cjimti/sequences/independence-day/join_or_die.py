"""Join, or Die: Franklin's 1754 cartoon on the roofline. The snake is cut into six pieces, one per
roof run, with gaps at the five corners. The head lies at the back of the Side, by the free end;
the tail (with a rattle) at the far end of Right. Each piece wriggles on its own and slowly grows
weaker. Then, from the head down, the pieces slide together and each corner closes with a click
and a jolt of life, except the Porch Front piece, which backs away, sulks, and finally rushes in to
close both its gaps at once. United, a wave of colour runs from tail to head and the ochre woodcut
becomes red and white bands with a blue head. The snake tests its tongue, shakes its rattle,
ripples, and slithers away out of the free end. Then the tongue peeks back in.

Everything is drawn in body coordinates (distance from the head), so the scale pattern, the
bands and the ripples travel with the snake when it moves, and the pieces' gaps are real gaps in
that body."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, nframes

CODE = 'IN10'
TITLE = 'Join, or Die'
KIND = 'show'
DESCRIPTION = ("Franklin's snake, cut into six pieces at the corners of the house. They wriggle, weaken, then "
               "join up one by one (the porch front sulks first). United, it turns red, white and blue and "
               "slithers away.")

OCHRE = hexc('#c86a10')
DARK = hexc('#200800')
RED = hexc('#ff1410')
WHITE = hexc('#f4ece2')
BLUE = hexc('#1a34ff')
EYE = hexc('#ffffff')
TONGUE = hexc('#ff0820')


def render(G, seed=30):
    rng = np.random.default_rng(seed)
    D = 61.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    L = G.length
    H0 = 30.0                                           # where the head starts (room for the tongue)
    corners = np.array([(x[a] + x[a + 1]) / 2 for a in (80, 178, 260, 331, 380)]) - H0   # in body coords
    blen = L - H0 - 4
    # gap half-widths at each corner over time: open, then each closes (porch front piece sulks)
    close_t = [14.5, 16.8, 25.0, 25.0, 21.0]
    def gap(j, t):
        g = 24.0 + 3 * np.sin(2 * np.pi * 0.4 * t + j)
        if j in (2, 3):
            g = keys(t, [(0, g), (18.5, g), (20.5, 48.0), (23.5, 52.0), (24.6, 40.0), (25.0, 0.0)])
            return float(g)
        c = close_t[j]
        return float(g * (1 - smoothstep(c - 0.6, c, t)))
    appear = [2.0, 2.6, 3.2, 3.8, 4.4, 5.0]
    piece_of_s = lambda s: np.searchsorted(corners, s)
    life = np.ones(6)
    unite_t = 27.0

    for f in range(F):
        t = f * DT
        head = H0 - keys(t, [(41.0, 0.0), (43.5, 50.0), (55.0, L + 120.0)])   # slithering out the free end
        s = x - head                                    # body coordinate of every pixel
        k = piece_of_s(s)
        inside = (s >= 0) & (s <= blen)
        # gaps at the corners (only while still in pieces)
        cut = np.ones(G.N)
        for j in range(5):
            g = gap(j, t)
            if g > 0.2:
                cut *= 1 - np.exp(-((s - corners[j]) / max(g, 1e-3)) ** 8)
        # each piece: appears, wriggles, weakens until it joins
        for p in range(6):
            joined = (t >= close_t[p - 1] if p > 0 else True) and (t >= close_t[p] if p < 5 else True)
            if p == 0:
                joined = t >= close_t[0]
            if t < unite_t and not joined:
                life[p] = max(0.45, life[p] - DT * 0.03)
            else:
                life[p] = min(1.0, life[p] + DT * 1.2)
        vis = np.array([smoothstep(appear[p], appear[p] + 0.5, t) for p in range(6)])[np.clip(k, 0, 5)]
        lf = life[np.clip(k, 0, 5)]
        wig = np.where(t < unite_t, 7 * np.sin(2 * np.pi * (0.5 + 0.4 * (1 - lf)) * t + 1.7 * k) * lf, 0.0)
        # slither: once united the skin flows with the body; a travelling ripple of light
        ss = s - wig
        diamond = np.abs(((ss / 34.0) % 1) - 0.5) * 2          # 0 at the diamond centre
        scales = smoothstep(0.35, 0.6, diamond)
        taper = 0.55 + 0.45 * (1 - np.clip(s / blen, 0, 1)) ** 0.7
        headness = np.exp(-(np.clip(s, 0, None) / 26) ** 2)
        ripple = 1.0
        if t > unite_t + 1:
            ripple = 0.8 + 0.2 * np.sin(2 * np.pi * (s / 220.0 - 0.6 * t))
        I = 0.62 * taper * lf * vis * cut * ripple * inside
        I = I * (1 + 0.5 * headness)
        # colour: ochre woodcut until united, then a wave from tail to head turns it red, white, blue
        front = blen - (blen + 80) * smoothstep(unite_t, unite_t + 3.0, t)
        u = smoothstep(front - 30, front + 30, s)
        wood = lerp(DARK * 4, OCHRE, scales[:, None])
        band = np.where(((ss / 90.0) % 1)[:, None] < 0.5, RED[None], WHITE[None] * 0.8)
        band = lerp(band, BLUE[None], np.clip(headness * 1.6, 0, 1)[:, None])
        col = lerp(wood, band, u[:, None])
        buf = col * perc(I)[:, None]
        # joining clicks
        for j in range(5):
            dtj = t - close_t[j]
            if 0 <= dtj < 0.6:
                buf += light(WHITE, (1.0 if j in (2, 3) else 0.8) * np.exp(-dtj / 0.12) *
                             np.exp(-((s - corners[j]) / 18) ** 2))
        if 0 <= t - unite_t < 1.0:                         # a shiver of life down the body
            buf += light(WHITE, 0.35 * np.exp(-((s - (t - unite_t) * 2600) / 60) ** 2) * inside)
        # the eye
        eye = s - 10
        buf += light(EYE, 0.7 * vis * np.exp(-(eye / 3) ** 2) * (s > -5) * (t < 55.5))
        # the tongue: flicks out ahead of the head (toward the free end)
        flicks = [7.0, 12.0, 28.5, 29.2, 33.0, 36.5, 38.8]
        for tf in flicks:
            dtf = t - tf
            if 0 <= dtf < 0.4:
                reach = 26 * np.sin(np.pi * dtf / 0.4)
                buf += light(TONGUE, 0.8 * np.exp(-((s + reach * 0.5) / max(reach * 0.5, 1)) ** 4) * (s < 0))
        if 57.5 <= t < 58.3:                               # peeking back in after it has gone
            reach = 30 * np.sin(np.pi * (t - 57.5) / 0.8)
            buf += light(TONGUE, 0.8 * np.exp(-((x - reach * 0.5) / max(reach * 0.5, 1)) ** 4))
        # the rattle
        tail = np.exp(-((s - blen + 8) / 10) ** 2) * inside
        shake = 0.0
        if 30.5 < t < 33.0 or 37.0 < t < 38.5 or 10.0 < t < 10.6:
            shake = 0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)
        buf += light(WHITE * 0.8 + OCHRE * 0.2, (0.15 + 0.6 * shake) * tail * vis * lf)
        out[f][G.path] = np.clip(buf, 0, 1)
    return out
