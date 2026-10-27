"""Hop: A bunny comes in at the free back end of Side and hops the whole roofline. Every hop is a
real ballistic arc: constant speed along the roof, parabolic height, drawn as a body that blurs and
dims as it lifts off and squashes bright when it lands, leaving fading footprints and puffs of
dust. At the corners it stops, ears up, and turns its head to look back. It drops painted eggs on
the way and does a twisting binky on the porch. Then three babies arrive in a hurry, hopping
twice as fast, and collect the eggs. At the very end the mother peeks back in at the right end."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, smooth_noise, nframes

CODE = 'EA02'
TITLE = 'Hop'
KIND = 'show'
DESCRIPTION = 'A bunny hops the whole roofline in real arcs, stopping at corners with ears up to look around and leaving eggs behind. Three babies follow in a hurry to collect them.'


def lin(h):
    return hexc(h) ** 2.2


LAWN = lin('#2b6b45')
FUR = lin('#fff1e2')
EAR = lin('#ffa8c8')
TAIL = lin('#ffffff')
PRINT = lin('#c8a8ff')
DUST = lin('#ffe4b0')
EGG_COLS = [(lin('#ff8fbf'), lin('#ffe17a')), (lin('#8fcfff'), lin('#ffffff')),
            (lin('#7ff0bd'), lin('#b99cff')), (lin('#ffad85'), lin('#8fcfff'))]


def plan(t, s, stops, end, L, dur, gap, H):
    """Hop from s to end; stops = [(s_stop, seconds, kind)]. Returns a list of segments."""
    segs = []
    targets = [(a, d, k) for a, d, k in stops] + [(end, 0.0, 'exit')]
    for goal, wait, kind in targets:
        dist = goal - s
        n = max(1, int(np.ceil(abs(dist) / L)))
        step = dist / n
        for i in range(n):
            segs.append(dict(kind='hop', t0=t, t1=t + dur, s0=s, s1=s + step, H=H))
            t += dur
            s += step
            segs.append(dict(kind='rest', t0=t, t1=t + gap, s0=s, s1=s, H=0))
            t += gap
        if wait > 0:
            segs.append(dict(kind=kind, t0=t, t1=t + wait, s0=s, s1=s, H=H))
            t += wait
    return segs


def state(segs, t):
    """(s, height 0..1, segment, phase u) at time t."""
    if t < segs[0]['t0']:
        return segs[0]['s0'], 0.0, None, 0.0
    for g in segs:
        if g['t0'] <= t < g['t1']:
            u = (t - g['t0']) / (g['t1'] - g['t0'])
            if g['kind'] == 'hop':
                return g['s0'] + (g['s1'] - g['s0']) * u, 4 * u * (1 - u), g, u
            if g['kind'] == 'binky':
                k = (u * 2) % 1                            # two high spinning hops in place
                return g['s0'], 2.2 * 4 * k * (1 - k), g, u
            return g['s0'], 0.0, g, u
    g = segs[-1]
    return g['s1'], 0.0, None, 1.0


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 61.0
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    n = G.N
    lawn = 0.8 + 0.2 * smooth_noise(rng, pdp, 40)
    END = G.length + 45

    def blob(c, w):
        return np.exp(-((pdp - c) / w) ** 2)

    mama_stops = [(476, 2.6, 'look'), (870, 2.0, 'egg'), (1150, 1.6, 'egg'), (1485, 2.6, 'binky'),
                  (2028, 2.4, 'look'), (2300, 1.8, 'egg')]
    mama = plan(1.5, -40.0, mama_stops, END, 52.0, 0.42, 0.1, 1.0)

    egg_spots = []                                         # (s, time laid, colours)
    for g in mama:
        if g['kind'] == 'egg':
            egg_spots.append([g['s0'] - 42, g['t0'] + 0.6 * (g['t1'] - g['t0']), EGG_COLS[len(egg_spots)], None])
    egg_spots.append([1485 + 46, None, EGG_COLS[3], None])  # the binky shakes one loose
    for g in mama:
        if g['kind'] == 'binky':
            egg_spots[-1][1] = g['t1'] - 0.2

    owner = [0, 1, 2, 0]
    babies = []
    for b, t0 in enumerate((35.0, 36.1, 37.4)):
        stops = sorted((egg_spots[j][0] + 8, 0.8, f'grab{j}') for j in range(4) if owner[j] == b)
        if b == 2:
            stops = sorted(stops + [(1440, 2.2, 'look')])
        babies.append(plan(t0, -30.0, stops, END + 20, 40.0, 0.24, 0.04, 0.8))
    for b, segs in enumerate(babies):
        for g in segs:
            if g['kind'].startswith('grab'):
                egg_spots[int(g['kind'][4:])][3] = (b, g['t0'] + 0.35)

    landings = [(g['s1'], g['t1'], 1.0) for g in mama if g['kind'] == 'hop']
    for segs in babies:
        landings += [(g['s1'], g['t1'], 0.6) for g in segs if g['kind'] == 'hop']
    for g in mama:
        if g['kind'] == 'binky':
            landings += [(g['s0'], g['t0'] + (g['t1'] - g['t0']) * k, 1.2) for k in (0.5, 1.0)]
    land_s = np.array([a for a, _, _ in landings])
    land_t = np.array([b for _, b, _ in landings])
    land_w = np.array([c for _, _, c in landings])

    def facing(segs, t, s):
        """+1/-1 travel direction, smoothly turned during a look-back."""
        _, _, g, u = state(segs, t)
        base = 1.0
        if g is not None and g['kind'] == 'look':
            return keys(u, [(0.2, 1.0), (0.35, -1.0), (0.6, -1.0), (0.75, 1.0)])
        if g is not None and g['kind'] == 'binky':
            k = (u * 2) % 1
            return np.cos(2 * np.pi * smoothstep(0.15, 0.85, k))
        return base

    def ears_up(segs, t):
        _, h, g, u = state(segs, t)
        if g is None:
            return 0.4
        if g['kind'] == 'hop':
            return 0.25 + 0.2 * (1 - h)
        if g['kind'] == 'rest':
            return 0.45
        up = smoothstep(0, 0.12, u) * (1 - smoothstep(0.88, 1, u))
        if g['kind'] == 'look':
            twitch = 0.25 * np.exp(-((u - 0.5) / 0.03) ** 2)
            return 0.45 + 0.55 * up - twitch
        return 0.45 + 0.55 * up

    def draw_bunny(buf, segs, t, scale, carry):
        s, h, g, u = state(segs, t)
        if s < -60 or s > G.length + 60:
            return
        fc = facing(segs, t, s)
        landed = [x for x in segs if x['kind'] == 'hop' and 0 <= t - x['t1'] < 0.18]
        squash = np.exp(-(t - landed[0]['t1']) / 0.07) if landed else 0.0
        crouch = 0.0
        if g is not None and g['kind'] == 'rest':
            crouch = np.sin(np.pi * u)
        w = scale * (13.0 + 16.0 * h) * (1 + 0.35 * squash - 0.15 * crouch)
        I = (1.0 - 0.42 * h + 0.1 * squash) * (0.8 + 0.2 * scale)
        if h > 0.02:                                       # its shadow on the roof, sharp near the ground
            buf += light(PRINT, 0.3 * scale * (1 - 0.5 * h) * blob(s, scale * (9 + 10 * h)))
        body = FUR if carry is None else 0.7 * FUR + 0.5 * carry
        buf += light(body, I * blob(s, w))
        e = ears_up(segs, t)
        for off in (19.0, 29.0):
            p = s + fc * scale * (off * (0.6 + 0.5 * e))
            buf += light(EAR, (0.35 + 0.65 * e) * I * blob(p, 3.4 * scale + 3 * h))
        buf += light(TAIL, 0.75 * I * blob(s - fc * scale * 21, 4.5 * scale + 3 * h))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        buf += light(LAWN, 0.22 * lawn * keys(t, [(0, 0), (1.2, 1), (58.5, 1), (61, 0)]))

        # footprints and dust where feet hit the roof
        age = t - land_t
        ok = (age >= 0) & (age < 9)
        for s0, a, wgt in zip(land_s[ok], age[ok], land_w[ok]):
            buf += light(PRINT, 0.32 * wgt * np.exp(-a / 3.0) * blob(s0, 3.0))
            if a < 0.6:
                spread = 70 * wgt * 0.25 * (1 - np.exp(-a / 0.25))
                dI = 0.45 * wgt * np.exp(-a / 0.2)
                buf += light(DUST, dI * (blob(s0 - 6 - spread, 3) + blob(s0 + 6 + spread, 3)))

        # eggs: laid, then grabbed by a baby
        for j, (s0, tl, (c1, c2), grab) in enumerate(egg_spots):
            if tl is None or t < tl:
                continue
            a = t - tl
            I = 0.7 * (1 + 0.5 * np.exp(-a / 0.3))
            if grab is not None and t > grab[1]:
                ga = t - grab[1]
                if ga > 0.4:
                    continue
                I *= 1 - ga / 0.4
                buf += light(lin('#ffffff'), 0.7 * np.exp(-ga / 0.1) * blob(s0, 20))
            u = (pdp - s0) / 15
            env = np.clip(1 - u ** 2, 0, 1)
            mix = (0.5 + 0.5 * np.tanh(3 * np.sin(u * 2.6 * np.pi)))[:, None]
            buf += ((env * I) ** 2.2)[:, None] * (c1 * (1 - mix) + c2 * mix)

        draw_bunny(buf, mama, t, 1.0, None)
        for b, segs in enumerate(babies):
            carry = None
            for (s0, tl, (c1, c2), grab) in egg_spots:
                if grab is not None and grab[0] == b and t > grab[1] + 0.2:
                    carry = c1
            draw_bunny(buf, segs, t, 0.62, carry)

        # the peek: two ears appear at the free right end, twitch, and go
        pk = keys(t, [(56.0, 0), (56.8, 1), (58.4, 1), (59.0, 0)])
        if pk > 0:
            tw = 1 - 0.5 * np.exp(-((t - 57.7) / 0.08) ** 2)
            for off in (19.0, 29.0):
                buf += light(EAR, pk * tw * blob(G.length + 24 - off * pk, 3.4))
        out[f][G.path] = buf
    return out
