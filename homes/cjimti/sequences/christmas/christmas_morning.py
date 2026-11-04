"""Christmas Morning: Night: the wings are deep blue with a few stars, the porch sides are the tree (green, its
bulbs twinkling) and the Porch Front is the pile of presents under it. The sun comes up from the free end of Right
and sweeps the house into warm morning; an alarm rings at the end of Right and two pairs of feet (pink and cyan)
race in along it and dive into the pile. One by one the presents are opened: each shakes, its ribbon is pulled
off in a streak to a free end, its paper is torn in three rips that throw bursts of its colour out along the
wings (the scraps stay where they land), and out comes the gift. A spinning top whirls in rainbow stripes down the
porch and along Left, wobbles and topples. A toy rocket fizzes, launches, shoots up Side and out the back, and
comes round the house in from the free end of Right to land back in the pile. A pair of socks flops out (wah-wah).
A music box opens and a ballerina turns while its notes float out along the wings in pastel lights. Then only the
big box is left. It wobbles; it thumps; it wobbles harder, faster, until it stops dead. Silence. A yip. One more
thump, and a puppy bursts out in a shower of paper over the whole house and runs laps, out to the end of Right,
all the way to the back of Side and back again, kicking up the scraps and ribbons as he goes, skidding and barking
at every turn, chases his tail on the porch and sits; and the house fills with the colours of every present.

The music is original, at 120 bpm in G: a slow dawn theme on flute, glock and strings; an alarm bell and a patter
of footsteps on wood blocks; then a bouncy unwrapping tune on clarinet and pizzicato under each present, with a
zip for every ribbon and a rip for every tear. The top whirls on xylophone scales and clatters over; the rocket
gets a fizz, a whoosh across the stereo and away, a distant one behind the house and a trumpet flourish as it comes
home; the socks a trombone wah-wah; the music box its own little tune, every note a light. The big box is a
bassoon's uh-oh over timpani thumps that crowd together and a rising string tremolo, a bar of silence, a yip, and
the burst; the puppy's laps are a galop for the full band with a bark and a skid at every turn and a glock
sparkle for the scraps he kicks; the dawn theme comes back for everyone at the end."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'CH18'
TITLE = 'Christmas Morning'
KIND = 'show'
DESCRIPTION = ('Dawn breaks and feet race to the tree: a ribbon zips off, paper flies, and out come a spinning top, '
               'a toy rocket, socks and a music box. The last big box wobbles and wobbles until a puppy bursts out '
               'and runs laps round the house.')
VOICEOVER = "Wake up, the sun is up! It's Christmas morning, and one big box has holes in the lid."

NIGHT = hexc('#0c2cb8')
MORNING = hexc('#ffa22c')
STAR = hexc('#e8f0ff')
SUN = hexc('#fff0b0')
TREE = hexc('#07a020')
RED = hexc('#ff1010')
GOLD = hexc('#ffaa00')
BLUE = hexc('#1040ff')
GREEN = hexc('#10c030')
PURPLE = hexc('#a020ff')
WHITE = hexc('#fff4e8')
PINK = hexc('#ff40a0')
CYAN = hexc('#20c8ff')
GREY = hexc('#7880a0')
PUP = hexc('#ff7a10')
PUP_HEAD = hexc('#ffc070')
BULBS = np.array([RED, GOLD, BLUE, PINK])
PASTEL = np.array([hexc('#ff70c0'), hexc('#70b8ff'), hexc('#b0ff70'), hexc('#ffd070')])
FINALE_COLS = np.array([RED, GOLD, GREEN, BLUE, PURPLE])

D = 86.0
SEED = 18
BEAT = 0.5                                          # 120 bpm
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


BIG = (1410.0, 1560.0)                              # the big box, the middle of the Porch Front
BIG_C = 1485.0
PRESENTS = [  # name, span on the Porch Front, box, ribbon, bar it is opened in, which way its ribbon zips
    dict(name='top', a=1318.0, b=1360.0, body=RED, ribbon=GOLD, bar=6, zip=-1),
    dict(name='rocket', a=1612.0, b=1654.0, body=BLUE, ribbon=WHITE, bar=10, zip=1),
    dict(name='socks', a=1364.0, b=1404.0, body=GREEN, ribbon=RED, bar=15, zip=-1),
    dict(name='mbox', a=1566.0, b=1606.0, body=PURPLE, ribbon=GOLD, bar=17, zip=1),
]
for _p in PRESENTS:
    _p['c'] = 0.5 * (_p['a'] + _p['b'])
    _p['shake'] = at(_p['bar'])
    _p['zip_t'] = at(_p['bar'], 1)
    _p['rips'] = [at(_p['bar'], 2), at(_p['bar'], 2.5), at(_p['bar'], 3)]
    _p['open'] = at(_p['bar'] + 1)
ZIP_V = 1800.0
T_SUN0, T_SUN1 = 4.0, 7.2                           # the sun sweeps in from the free end of Right
T_ALARM = at(3, 2)
KIDS = [(PINK, 2540.0, 1690.0), (CYAN, 2590.0, 1720.0)]   # colour, start, where they dive into the pile
T_RUN0, T_RUN1 = at(4), at(5, 3)
TOP_PATH = [(at(7), 1339.0), (15.0, 1180.0), (16.0, 960.0), (17.0, 760.0), (18.0, 900.0), (19.0, 690.0),
            (at(9, 3), 700.0)]
T_TOPPLE = at(9, 3)
T_IGNITE, T_LAUNCH, T_GONE, T_RETURN, T_LAND = at(11), at(11, 2), at(12, 2), at(13), at(13, 3)
T_CHEER = at(14)
T_SOCKS = at(16)
T_MB0, T_MB1 = at(18), at(22)
MB_TUNE = [  # (bar, beat, note): the music box's tune; every note floats out as a light
    (18, 0, 'B4'), (18, 1, 'D5'), (18, 1.5, 'C5'), (18, 2, 'B4'), (18, 3, 'G4'),
    (19, 0, 'A4'), (19, 1, 'C5'), (19, 1.5, 'B4'), (19, 2, 'A4'), (19, 3, 'F#4'),
    (20, 0, 'G4'), (20, 0.5, 'B4'), (20, 1, 'D5'), (20, 2, 'E5'), (20, 2.5, 'D5'), (20, 3, 'B4'),
    (21, 0, 'C5'), (21, 1, 'A4'), (21, 2, 'D5'),
]
T_SPOT = at(22)
THUMPS = [at(22, b) for b in (0, 2)] + [at(23, b) for b in (0, 1.5, 2, 3)] + \
         [at(24, b) for b in (0, 1, 2, 2.5, 3, 3.5)] + [at(25, b / 2) for b in range(8)]
T_STILL = at(26)
T_YIP = at(27)
T_THUMP = at(27, 2)
T_BURST = at(28)
PUP_PATH = [(T_BURST, BIG_C), (at(29), 2470.0), (at(29, 0.5), 2470.0), (at(32), 30.0), (at(32, 0.5), 30.0),
            (at(35), 2470.0), (at(35, 0.5), 2470.0), (at(36, 2), BIG_C)]
TURNS = [(at(29), 2470.0), (at(32), 30.0), (at(35), 2470.0)]
T_CHASE, T_SIT = at(36, 2), at(38)
BARKS = [at(38, 2), at(38, 3)]
T_CHORD = at(41)


def zip_head(p, t):
    """The ribbon's leading end, from the box to past a free end."""
    return p['c'] + p['zip'] * ZIP_V * (t - p['zip_t'])


def top_x(t):
    return float(keys(t, TOP_PATH))


def rocket_x(t):
    if t < T_LAUNCH:
        return PRESENTS[1]['c']
    if t < T_GONE:
        u = (t - T_LAUNCH) / (T_GONE - T_LAUNCH)
        return PRESENTS[1]['c'] - (PRESENTS[1]['c'] + 40) * u ** 2
    if t < T_RETURN:
        return np.nan
    u = min(1.0, (t - T_RETURN) / (T_LAND - T_RETURN))
    return 2560 - (2560 - PRESENTS[1]['c']) * (1 - (1 - u) ** 2)


def wobble(t):
    """The big box: (tilt -1..1, thump kick 0..1)."""
    if t < T_SPOT or t >= T_BURST:
        return 0.0, 0.0
    kick = sum(np.exp(-(t - th) / 0.12) for th in THUMPS + [T_THUMP] if t >= th)
    amp = keys(t, [(T_SPOT, 0.2), (T_STILL - 0.1, 1.0), (T_STILL, 0.0), (T_THUMP, 0.0), (T_THUMP + 0.05, 1.0),
                   (T_BURST, 0.6)])
    freq = keys(t, [(T_SPOT, 1.0), (T_STILL, 4.0)])
    return float(amp * np.sin(2 * np.pi * freq * (t - T_SPOT))), float(min(kick, 1.5))


def pup_track():
    """The puppy's position, frame by frame (NaN before he is out), and which way he faces."""
    F = nframes(D)
    t = np.arange(F) * DT
    ts = np.array([p[0] for p in PUP_PATH])
    xs = np.array([p[1] for p in PUP_PATH])
    x = np.interp(t, ts, xs)
    k = 4
    w = np.exp(-0.5 * (np.arange(-k, k + 1) / 2.0) ** 2)
    w /= w.sum()
    x = np.convolve(np.pad(x, k, mode='edge'), w, 'valid')
    chase = (t >= T_CHASE) & (t < T_SIT)
    x[chase] += 26 * np.sin(2 * np.pi * 2.0 * (t[chase] - T_CHASE)) * np.sin(np.pi * (t[chase] - T_CHASE) / (T_SIT - T_CHASE))
    x[t < T_BURST] = np.nan
    v = np.gradient(np.nan_to_num(x, nan=BIG_C)) / DT
    face = np.sign(v)
    for i in range(1, F):                            # hold the facing through the pauses
        if face[i] == 0:
            face[i] = face[i - 1] or 1
    return x, face


def litter(G):
    """Every scrap of paper and ribbon: thrown out by the rips and the burst, sliding to a stop where it lands,
    kicked on again by the puppy. Returns per-frame positions and brightness, colours, and the kicks."""
    rng = np.random.default_rng(SEED + 1)
    F = nframes(D)
    L = G.length
    spawn, x0, v0, col = [], [], [], []
    for p in PRESENTS:
        for tr in p['rips']:
            k = 14
            spawn += [tr] * k
            x0 += list(rng.uniform(p['a'], p['b'], k))
            v0 += list(rng.uniform(900, 2800, k) * rng.choice([-1, 1], k))
            col += [p['body']] * (k - 3) + [p['ribbon']] * 3
    k = 170
    spawn += [T_BURST] * k
    x0 += list(rng.uniform(*BIG, k))
    v0 += list(rng.uniform(500, 3200, k) * rng.choice([-1, 1], k))
    col += [[GOLD, RED, WHITE, GREEN, BLUE, PURPLE][i % 6] for i in range(k)]
    spawn, x, v, col = np.array(spawn), np.array(x0), np.array(v0), np.array(col)
    n = len(x)
    alive = np.ones(n, bool)
    last_kick = np.full(n, -9.0)
    px, pface = pup_track()
    X = np.full((F, n), np.nan)
    I = np.zeros((F, n))
    kicks = []
    for f in range(F):
        t = f * DT
        on = (spawn <= t) & alive
        x = np.where(on, x + v * DT, x)
        v = np.where(on, v * 0.95, v)
        v[np.abs(v) < 12] = 0
        alive &= (x > -5) & (x < L + 5)
        if not np.isnan(px[f]):
            hit = on & alive & (np.abs(x - px[f]) < 14) & (t - last_kick > 0.7) & (np.abs(v) < 300)
            if hit.any():
                idx = np.nonzero(hit)[0]
                v[idx] = pface[f] * rng.uniform(450, 1150, len(idx))
                last_kick[idx] = t
                for i in idx:
                    kicks.append((t, float(x[i])))
        on = (spawn <= t) & alive
        X[f, on] = x[on]
        I[f, on] = 0.5 + 0.45 * np.clip(np.abs(v[on]) / 700, 0, 1)
    return X, I, col, kicks


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    N = G.N
    tree = ((x > 892) & (x < 1311)) | ((x > 1660) & (x < 2033))
    front = (x >= 1311) & (x <= 1660)
    wings = ~(tree | front)
    tw = Flicker(rng, N, 0.15, 0.6)
    bulb = ((x // 22) % 2 == 0) & tree
    bulb_col = BULBS[((x // 44) % len(BULBS)).astype(int)]
    stars = rng.random(N) < 0.07
    star_tw = Flicker(rng, N, 0.3, 1.2)
    ign = rng.uniform(0.3, 1.0, F)
    px, pface = pup_track()
    LX, LI, LC, kicks = litter(G)
    mb_t = np.array([at(b, e) for b, e, _ in MB_TUNE])
    mb_dir = np.where(np.arange(len(MB_TUNE)) % 2 == 0, -1.0, 1.0)
    mb_v = rng.uniform(170, 260, len(MB_TUNE))
    mb_c = PASTEL[np.arange(len(MB_TUNE)) % len(PASTEL)]

    def splat(fr, pos, inten, cols, width=1):
        """Add point lights at path positions to the frame (each lands on its two nearest pixels)."""
        ok = ~np.isnan(pos) & (inten > 0)
        if not ok.any():
            return fr
        pos, inten, cols = pos[ok], inten[ok], cols[ok]
        j = np.clip(np.searchsorted(x, pos) - 1, 0, N - 2)
        u = np.clip((pos - x[j]) / (x[j + 1] - x[j]), 0, 1)
        for jj, w in ((j, 1 - u), (j + 1, u)):
            np.add.at(fr, jj, (perc(inten) * w)[:, None] * cols)
        return fr

    for f in range(F):
        t = f * DT
        fr = np.zeros((N, 3))
        master = keys(t, [(0, 0.0), (1.0, 1.0), (D - 2.0, 1.0), (D - 0.2, 0.0)])

        # night into morning: the sun sweeps in from the free end of Right
        b = keys(t, [(T_SUN0, G.length + 30), (T_SUN1, -60.0)])
        day = smoothstep(b - 40, b + 40, x)
        lvl = keys(t, [(T_SPOT, 1.0), (T_SPOT + 1, 0.75), (T_STILL, 0.6), (T_BURST, 0.6), (T_BURST + 0.5, 1.0)])
        night = light(NIGHT, 0.24 * np.ones(N)) + light(STAR, stars * np.clip(0.35 + 0.25 * star_tw(t), 0, 1))
        morning = light(MORNING, lvl * 0.28 * (1 + 0.1 * tw(t)))
        bed = night * (1 - day)[:, None] + morning * day[:, None]
        if T_SUN0 <= t < T_SUN1 + 0.3:
            bed += light(SUN, 0.95 * np.exp(-((x - b) / 30) ** 2))
        wob, kick = wobble(t)
        bed = bed * (1 + 0.35 * kick)                    # every thump of the big box shakes the house
        fr = np.where(front[:, None], 0, bed)

        # the tree on the porch sides, bulbs twinkling
        tl = keys(t, [(0, 0.55), (T_SUN1, 1.0)])
        tree_fr = light(TREE, tl * 0.32 * ~bulb) + bulb_col * perc(tl * np.clip(0.55 + 0.3 * tw(t), 0, 1) * bulb)[:, None]
        fr = np.where(tree[:, None], tree_fr * (1 + 0.35 * kick), fr)

        # the presents
        pl = keys(t, [(0, 0.35), (T_SUN1, 0.7)])
        for p in PRESENTS:
            inb = (x >= p['a']) & (x <= p['b'])
            sh = 0.0
            if p['shake'] <= t < p['zip_t']:
                sh = 0.25 * np.sin(2 * np.pi * 8 * t)
            opened = t >= p['open']
            body = 0.12 if opened else pl * (1 + sh)
            rib = np.abs(x - p['c']) < 3.5
            if t < p['zip_t']:
                fr = np.where((inb & rib)[:, None], light(p['ribbon'], pl * 1.25 * np.ones(N)), fr)
                fr = np.where((inb & ~rib)[:, None], light(p['body'], body * np.ones(N)), fr)
            else:
                fr = np.where(inb[:, None], light(p['body'], body * np.ones(N)), fr)
            # the ribbon zips off to a free end
            if p['zip_t'] <= t < p['zip_t'] + 2.0:
                h = zip_head(p, t)
                tail = p['c'] + p['zip'] * max(0.0, ZIP_V * (t - p['zip_t'] - 0.15))
                lo, hi = min(h, tail), max(h, tail)
                seg = (x >= lo) & (x <= hi)
                ramp = np.clip(1 - np.abs(x - h) / max(hi - lo, 1), 0.2, 1)
                fr = np.where(seg[:, None], light(p['ribbon'], 0.95 * ramp), fr)
                fr += light(WHITE, 0.9 * np.exp(-((x - h) / 4) ** 2))
        # the big box: a gold box with a red ribbon cross; it wobbles, it thumps
        if t < T_BURST:
            inb = (x >= BIG[0]) & (x <= BIG[1])
            shift = 9 * wob
            rel = (x - BIG_C - shift) / 75
            bl = pl * keys(t, [(T_SPOT, 1.0), (T_SPOT + 0.5, 1.25)]) * (1 + 0.35 * wob * rel) * (1 + 0.3 * kick)
            rib = np.abs(x - BIG_C - shift) < 4
            edge = np.abs(np.abs(x - BIG_C) - 75) < 4
            fr = np.where(inb[:, None], light(GOLD, bl * np.ones(N)), fr)
            fr = np.where((inb & rib)[:, None], light(RED, 1.1 * pl * np.ones(N)), fr)
            fr += light(WHITE, 0.6 * kick * edge * inb)
            if T_YIP <= t < T_YIP + 0.4:                 # a yip from inside
                fr += light(PUP_HEAD, np.exp(-(t - T_YIP) / 0.12) * np.exp(-((x - BIG_C) / 6) ** 2))
        else:
            inb = (x >= BIG[0]) & (x <= BIG[1])
            fr = np.where(inb[:, None], light(GOLD, 0.12 * np.ones(N)), fr)
        # the opened gifts' boxes stay dim; the porch front between gifts glows faintly
        gap = front & ~((x >= BIG[0]) & (x <= BIG[1]))
        for p in PRESENTS:
            gap &= ~((x >= p['a']) & (x <= p['b']))
        fr = np.where(gap[:, None], light(TREE, 0.22 * tl * np.ones(N)), fr)

        # an alarm rings at the end of Right
        if T_ALARM <= t < T_ALARM + 1.0:
            ring = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 10 * t))
            fr += light(GOLD, (0.5 + 0.5 * ring) * inside_end(x, G.length))

        # feet racing in along Right
        if T_RUN0 <= t < T_RUN1 + 0.6:
            for k, (c, s0, s1) in enumerate(KIDS):
                u = smoothstep(T_RUN0 + 0.15 * k, T_RUN1 - 0.1 * k, t)
                kx = lerp(s0, s1, u)
                step = 0.7 + 0.3 * abs(np.sin(2 * np.pi * 4 * t + k))
                fade = 1 - smoothstep(T_RUN1, T_RUN1 + 0.5, t)
                fr = fr * (1 - 0.9 * np.exp(-((x - kx) / 14) ** 2) * fade)[:, None]
                fr += light(c, step * fade * np.exp(-((x - kx) / 8) ** 2))
                for j in range(1, 7):                    # footprints fading behind
                    tj = np.floor(t * 8) / 8 - j / 8
                    if tj >= T_RUN0:
                        pj = lerp(s0, s1, smoothstep(T_RUN0 + 0.15 * k, T_RUN1 - 0.1 * k, tj))
                        fr += light(c, 0.55 * (1 - j / 7) * fade * np.exp(-((x - pj) / 4) ** 2))
            if t >= T_RUN1:                              # they dive into the pile
                fr += light(WHITE, 0.8 * np.exp(-(t - T_RUN1) / 0.2) * np.exp(-((x - 1700) / 40) ** 2))

        # the spinning top
        if at(7) <= t < T_TOPPLE + 1.5:
            tx = top_x(t)
            if t < T_TOPPLE:
                el = t - at(7)
                ph = 14 * el - 1.2 * smoothstep(17.5, T_TOPPLE, t) * el
                tx += 12 * smoothstep(17.8, T_TOPPLE, t) * np.sin(2 * np.pi * 3 * t)
                r = x - tx
                cols = np.array([RED, GOLD, BLUE, GREEN])[((r / 6 + ph * 4) // 1 % 4).astype(int)]
                on = np.abs(r) < 16
                fr = np.where(on[:, None], perc(0.95) * cols, fr)
                fr += light(WHITE, 0.7 * np.exp(-(r / 2.5) ** 2))
            else:
                tp = t - T_TOPPLE
                r = x - tx
                fr += light(WHITE, np.exp(-tp / 0.12) * np.exp(-(r / 20) ** 2))
                fr = np.where((np.abs(r) < 20)[:, None], light(RED, 0.4 * (1 - tp / 1.5) * np.ones(N)), fr)

        # the rocket
        if T_IGNITE <= t < T_LAND + 1.2:
            rx = rocket_x(t)
            if t < T_LAUNCH:                             # fizzing on the pad
                sp = np.exp(-((x - rx - rng.normal(0, 14)) / 4) ** 2)
                fr += light(GOLD, ign[f] * sp) + light(WHITE, 0.4 * ign[f] * np.exp(-((x - rx) / 5) ** 2))
            elif not np.isnan(rx) and t < T_LAND:
                back = x - rx                            # behind the rocket, the way it came (it always flies left)
                trail = np.where(back > 0, np.exp(-back / 140), 0) * (back < 500)
                fr += light(hexc('#ff5a00'), 0.95 * trail * ign[f] ** 0.3)
                fr += light(GOLD, 0.8 * np.exp(-(back / 18) ** 2) * (back > 0))
                fr += light(WHITE, np.exp(-((x - rx) / 4) ** 2))
            if t >= T_LAND:
                tl_ = t - T_LAND
                fr += light(WHITE, 0.8 * np.exp(-tl_ / 0.3) * np.exp(-((x - PRESENTS[1]['c']) / (10 + 60 * tl_)) ** 2))
        if T_CHEER <= t < T_CHEER + 1.5:                 # everyone cheers: the wings flash gold
            fr += light(GOLD, 0.45 * np.exp(-(t - T_CHEER) / 0.4) * wings)

        # the socks
        if T_SOCKS <= t < T_SOCKS + 4.0:
            ts_ = t - T_SOCKS
            sx = PRESENTS[2]['c'] - 14 * smoothstep(0, 0.6, ts_)
            sag = keys(t, [(T_SOCKS, 0.8), (T_SOCKS + 0.6, 0.6), (T_SOCKS + 2.8, 0.25), (T_SOCKS + 4.0, 0.0)])
            fr = np.where((np.abs(x - sx) < 20)[:, None], light(GREY, sag * np.ones(N)), fr)
            fr += light(WHITE, 0.5 * np.exp(-ts_ / 0.2) * np.exp(-((x - sx) / 20) ** 2))

        # the music box: a ballerina turns; every note floats out along the wings
        if T_MB0 <= t < T_MB1 + 4.0:
            c = PRESENTS[3]['c']
            lid = keys(t, [(T_MB0, 0.0), (T_MB0 + 0.4, 1.0), (T_MB1, 1.0), (T_MB1 + 1.0, 0.0)])
            fr += light(hexc('#ff90c0'), 0.5 * lid * np.exp(-((x - c) / 14) ** 2))
            turn = np.cos(2 * np.pi * 0.75 * (t - T_MB0))
            fr += light(WHITE, lid * (0.55 + 0.45 * abs(turn)) * np.exp(-((x - c - 5 * turn) / 3) ** 2))
            el = t - mb_t
            live = (el >= 0) & (el < 4.5)
            if live.any():
                nx = c + mb_dir * mb_v * el
                ni = np.clip(1 - el / 4.5, 0, 1) ** 0.7 * smoothstep(0, 0.1, el) * live
                for off in (-5, 0, 5):
                    fr = splat(fr, np.where(live, nx + off, np.nan), ni * (1 if off == 0 else 0.75), mb_c)

        # the burst: a white flash on the porch
        if T_BURST <= t < T_BURST + 0.8:
            tb = t - T_BURST
            fr += light(WHITE, np.exp(-tb / 0.18) * np.exp(-((x - BIG_C) / (40 + 900 * tb)) ** 2))

        # scraps of paper and ribbon
        fr = splat(fr, LX[f], LI[f], LC)
        fr = splat(fr, LX[f] + 4, 0.7 * LI[f], LC)

        # the puppy
        if not np.isnan(px[f]):
            pp, fc = px[f], pface[f]
            spd = abs(px[f] - px[f - 1]) / DT if f else 0
            gait = 0.85 + 0.15 * abs(np.sin(2 * np.pi * 5 * t))
            r = (x - pp) * fc
            fr = fr * (1 - np.exp(-(r / 14) ** 2))[:, None]
            fr += light(PUP, gait * np.exp(-(r / 8) ** 2))
            fr += light(PUP_HEAD, gait * np.exp(-((r - 10) / 3.5) ** 2))
            wag = 0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)
            fr += light(WHITE, (0.4 + 0.6 * wag) * np.exp(-((r + 13 + 2 * wag) / 2.5) ** 2))
            if spd > 150:                                # a streak behind him when he runs
                fr += light(GOLD, 0.45 * np.where(r < -14, np.exp((r + 14) / 50), 0) * (r > -170))
        for tb in BARKS + [tt for tt, _ in TURNS]:
            if tb <= t < tb + 0.3 and not np.isnan(px[f]):
                fr += light(WHITE, 0.8 * np.exp(-(t - tb) / 0.08) * np.exp(-((x - px[f]) / 22) ** 2))

        # finale: every present's colour rolls out from the porch over the whole house
        if t >= T_SIT:
            fl = keys(t, [(T_SIT, 0.0), (T_SIT + 1.5, 1.0)])
            d0 = np.abs(x - BIG_C)
            k = (np.floor((d0 - 400 * (t - T_SIT)) / 60) % len(FINALE_COLS)).astype(int)
            front_on = d0 < 400 * (t - T_SIT) + 40
            roll = perc(0.5 * fl * front_on * (1 + 0.15 * tw(t)))[:, None] * FINALE_COLS[k]
            keep = np.exp(-((x - px[f]) / 16) ** 2) if not np.isnan(px[f]) else 0
            fr = fr * np.clip(1 - 0.8 * fl * front_on + keep, 0, 1)[:, None] + roll * (1 - keep)[:, None]
            if T_CHORD <= t < T_CHORD + 1.2:
                fr += light(SUN, 0.5 * np.exp(-(t - T_CHORD) / 0.35) * np.ones(N))
        out[f][G.path] = np.clip(fr, 0, 1) * master
    return out


def inside_end(x, L):
    return np.exp(-((x - (L - 25)) / 18) ** 2)


# ---- music: original, 120 bpm in G ----
DAWN = [
    [(0, 'D5', 2), (2, 'B4', 1), (3, 'G4', 1)],
    [(0, 'A4', 1.5), (1.5, 'B4', 0.5), (2, 'C5', 1), (3, 'E5', 1)],
    [(0, 'D5', 2), (2, 'G5', 1), (3, 'F#5', 1)],
    [(0, 'E5', 1), (1, 'D5', 1), (2, 'A4', 2)],
]
DAWN_CH = ['G', 'Am', 'G', 'D']
UNWRAP = [
    [(0, 'G4', 0.5), (0.5, 'B4', 0.5), (1, 'D5', 0.5), (1.5, 'B4', 0.5), (2, 'C5', 0.5), (2.5, 'A4', 0.5),
     (3, 'F#4', 0.5), (3.5, 'A4', 0.5)],
]
GALOP = [
    [(0, 'B4', 0.5), (0.5, 'D5', 0.5), (1, 'G5', 0.5), (1.5, 'D5', 0.5), (2, 'B4', 0.5), (2.5, 'D5', 0.5), (3, 'G5', 1)],
    [(0, 'A4', 0.5), (0.5, 'C5', 0.5), (1, 'F#5', 0.5), (1.5, 'C5', 0.5), (2, 'A4', 0.5), (2.5, 'C5', 0.5), (3, 'F#5', 1)],
    [(0, 'G5', 0.5), (0.5, 'F#5', 0.5), (1, 'E5', 0.5), (1.5, 'D5', 0.5), (2, 'C5', 0.5), (2.5, 'B4', 0.5), (3, 'A4', 0.5),
     (3.5, 'G4', 0.5)],
    [(0, 'A4', 0.5), (0.5, 'B4', 0.5), (1, 'C5', 0.5), (1.5, 'A4', 0.5), (2, 'D5', 2)],
    [(0, 'B4', 0.5), (0.5, 'D5', 0.5), (1, 'G5', 0.5), (1.5, 'D5', 0.5), (2, 'B4', 0.5), (2.5, 'D5', 0.5), (3, 'G5', 1)],
    [(0, 'C5', 0.5), (0.5, 'E5', 0.5), (1, 'G5', 0.5), (1.5, 'E5', 0.5), (2, 'C5', 0.5), (2.5, 'E5', 0.5), (3, 'A5', 1)],
    [(0, 'G5', 0.5), (0.5, 'E5', 0.5), (1, 'D5', 0.5), (1.5, 'B4', 0.5), (2, 'A4', 0.5), (2.5, 'C5', 0.5), (3, 'F#4', 1)],
    [(0, 'G4', 1), (1, 'D5', 1), (2, 'G5', 2)],
]
GALOP_CH = ['G', 'D7', 'C', 'D', 'G', 'C', 'D7', 'G']
CH = {'G': ('G3', 'B3', 'D4'), 'Am': ('A3', 'C4', 'E4'), 'D': ('F#3', 'A3', 'D4'), 'D7': ('F#3', 'C4', 'D4'),
      'C': ('G3', 'C4', 'E4'), 'Em': ('G3', 'B3', 'E4')}
BASS = {'G': ('G2', 'D2'), 'Am': ('A2', 'E2'), 'D': ('D2', 'A2'), 'D7': ('D2', 'A2'), 'C': ('C2', 'G2'),
        'Em': ('E2', 'B2')}


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    px, pface = pup_track()
    LX, LI, LC, kicks = litter(G)

    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    flute_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    mbox = M.synth('Plucks/Magic Music Box')
    bell = M.hits('Percussion/Triangle6-Hit_v2*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    log = M.hits('Percussion/LogDrumHi_MedM*.wav')
    log_lo = M.hits('Percussion/LogDrumLo_MedM*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('Percussion/Guiro-Fast*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')

    for name, gain, rev in (('tune', 0.36, 0.18), ('harm', 0.26, 0.26), ('bass', 0.42, 0.06), ('drums', 0.34, 0.1),
                            ('motif', 0.32, 0.2), ('perc', 0.38, 0.12), ('fx', 0.3, 0.16)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def tone(fr, amp, buzz=0.12):
        ph = 2 * np.pi * np.cumsum(fr) / SR
        return amp * (np.sin(ph) + buzz * np.sin(2 * ph) + 0.6 * buzz * np.sin(3 * ph))

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, gain=1.0, octave=0, long=None):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 1.5) else inst
                M.add(bus, pl.play(n(m) + octave, vel, dur=ln * BEAT * 0.92), at(k0 + j, e), gain, pan)

    def oompah(k0, chords, vel=96, gain=1.0, drums=True):
        for j, c in enumerate(chords):
            k = k0 + j
            for e in (0, 2):
                M.add('bass', tuba.play(n(BASS[c][e // 2]), vel), at(k, e), gain)
                if drums:
                    M.add('drums', bd.play(vel - 10), at(k, e), 0.6 * gain)
            for e in (1, 3):
                for m in CH[c]:
                    M.add('harm', horn_st.play(n(m), vel - 15), at(k, e), 0.45 * gain, -0.2)
                    M.add('harm', pizz.play(n(m) + 12, vel - 10), at(k, e), 0.4 * gain, 0.2)
                if drums:
                    M.add('drums', snare.play(vel - 25), at(k, e), 0.4 * gain, 0.1)

    def chord_pad(t0, c, dur, vel=70, gain=1.0):
        for m in CH[c]:
            M.add('harm', vln.play(n(m) + 12, vel, dur=dur, release=0.5), t0, 0.35 * gain, 0.25)
        M.add('harm', vc.play(n(BASS[c][0]) + 12, vel, dur=dur, release=0.5), t0, 0.5 * gain, -0.25)

    def bark(t, p, big=1.0):
        tt = np.arange(int(0.16 * SR)) / SR
        f = 380 + 700 * np.exp(-tt / 0.03)
        env = np.clip(tt / 0.004, 0, 1) * np.exp(-tt / 0.05)
        noise = np.convolve(M.rng.normal(0, 1, len(tt)), np.ones(6) / 6, 'same')
        sig = (tone(f, 0.5, 0.6) + 0.35 * noise) * env * big
        M.add('fx', mono(sig, np.full(len(tt), p)), t, 0.9)

    # ---- 0-8: dawn ----
    for j, c in enumerate(DAWN_CH):
        chord_pad(at(j), c, BAR * 0.98, 62 + 6 * j)
    tune(DAWN, 0, flute, 'tune', 80, 0.1)
    for j, b in enumerate(DAWN):
        for e, m, ln in b:
            M.add('motif', glock.play(n(m), 62), at(j, e), 0.35, -0.2)
    for i, m in enumerate(('G3', 'B3', 'D4', 'G4', 'B4', 'D5')):
        M.add('harm', harp.play(n(m), 70), T_SUN0 + 0.4 * i, 0.6, pan_at(L - 420 * i))
    M.add('motif', chimes.play(85), T_SUN0 + 0.4, 0.4, 0.6)
    pe = pan_at(L - 25)
    for k in range(20):                                  # the alarm clock
        M.add('perc', bell.play(100), T_ALARM + k * 0.05, 0.35, pe)
    M.add('perc', slap.play(90), T_ALARM + 1.0, 0.5, pe)

    # ---- 8-12: feet race in along Right ----
    for k in range(int((T_RUN1 - T_RUN0) * 8)):
        t = T_RUN0 + k / 8
        kid = k % 2
        c, s0, s1 = KIDS[kid]
        u = smoothstep(T_RUN0 + 0.15 * kid, T_RUN1 - 0.1 * kid, t)
        M.add('perc', (log if kid else log_lo).play(85 + int(M.rng.integers(-8, 8))), t, 0.6, pan_at(lerp(s0, s1, u)))
    oompah(4, ['G', 'D'], 88, drums=False)
    for j, (e, m) in enumerate(((0, 'G4'), (1, 'A4'), (2, 'B4'), (3, 'D5'), (4, 'C5'), (5, 'E5'), (6, 'F#5'))):
        M.add('tune', clar.play(n(m), 96, dur=0.4), at(4, e), 0.8, 0.4)
    M.add('fx', slide(0.0, 0.3, 500, 1400, 0.35, 0.4), T_RUN1, 0.6, pan_at(1700))
    M.add('perc', crash.play(80), T_RUN1, 0.3, pan_at(1700))

    # ---- each present: a shake, a ribbon zip, three rips, the reveal ----
    for p in PRESENTS:
        pp = pan_at(p['c'])
        k = p['bar']
        oompah(k, ['G', 'D7'] if p['name'] != 'socks' else ['G'], 92)
        tune(UNWRAP, k, clar, 'tune', 100, pp * 0.5)
        tune(UNWRAP, k, xylo, 'motif', 80, pp * 0.5, gain=0.4)
        M.add('perc', ratchet.play(70, dur=0.5), p['shake'], 0.4, pp)
        end = 0.0 if p['zip'] < 0 else L
        dur = abs(end - p['c']) / ZIP_V
        zs = slide(0.0, dur, 700, 2400, dur + 0.05, 0.4, 0.5)
        M.add('fx', mono(zs[0], np.linspace(pp, pan_at(end), zs.shape[1])), p['zip_t'], 0.8)
        for i, tr in enumerate(p['rips']):
            rip = whoosh(0.22 + 0.08 * i, 1500, 5000, 1.0, seed=int(10 * tr))
            M.add('fx', rip, tr, 0.6 + 0.2 * i, pp)
            M.add('perc', guiro.play(70, dur=0.2), tr, 0.4, pp)
        if p['name'] != 'socks':                         # a ta-da
            for m in ('G4', 'B4', 'D5'):
                M.add('tune', tpt.play(n(m), 100, dur=0.5), p['open'], 0.6, pp)
            M.add('perc', tri.play(95), p['open'], 0.5, pp)
            M.add('perc', crash.play(85), p['open'], 0.3, pp)

    # the top: whirring scales on the xylophone, a wobble, a clatter
    oompah(7, ['G', 'C', 'D'], 94)
    run = ['G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F#5', 'G5', 'F#5', 'E5', 'D5', 'C5', 'B4', 'A4']
    for k in range(int((T_TOPPLE - at(7)) * 8)):
        t = at(7) + k / 8
        M.add('motif', xylo.play(n(run[k % len(run)]), 85), t, 0.55, pan_at(top_x(t)))
    tt = np.arange(int((T_TOPPLE - at(7)) * SR)) / SR
    hum = tone(520 + 40 * np.sin(2 * np.pi * 6 * tt) + 140 * np.clip((tt - 3.5) / 2, 0, 1) * np.sin(2 * np.pi * 3 * tt),
               0.12, 0.25) * np.clip(tt / 0.3, 0, 1)
    M.add('fx', mono(hum, np.array([pan_at(top_x(at(7) + s)) for s in tt])), at(7), 0.6)
    tune([[(0, 'B4', 1), (1, 'C5', 1), (2, 'D5', 1), (3, 'G5', 1)], [(0, 'E5', 1), (1, 'C5', 1), (2, 'A4', 2)],
          [(0, 'F#4', 1), (1, 'A4', 1), (2, 'D5', 2)]], 7, flute, 'tune', 88, -0.2)
    pt = pan_at(top_x(T_TOPPLE))
    for i in range(5):
        M.add('perc', click.play(110 - 15 * i), T_TOPPLE + 0.09 * i * (1 + 0.3 * i), 0.7, pt)
    M.add('perc', choke.play(100), T_TOPPLE, 0.4, pt)
    M.add('fx', slide(0.0, 0.5, 1200, 300, 0.55, 0.4), T_TOPPLE, 0.6, pt)

    # the rocket: fizz, launch, away out the back, round the house, home
    pr = pan_at(PRESENTS[1]['c'])
    fz = np.random.default_rng(3).normal(0, 1, int(SR * (T_LAUNCH - T_IGNITE)))
    fz = np.convolve(fz, [1, -1], 'same') * np.linspace(0.3, 1, len(fz)) * 0.06
    M.add('fx', mono(fz, np.full(len(fz), pr)), T_IGNITE, 1.0)
    r = sroll.play(85, dur=1.0)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, T_IGNITE, 0.5, pr)
    M.add('drums', bd.play(110), T_LAUNCH, 0.8, pr)
    M.add('perc', timp.play(105), T_LAUNCH, 0.6, pr)
    w = whoosh(T_GONE - T_LAUNCH + 0.3, 300, 4000, 1.0, seed=23)
    M.add('fx', mono(w[0], np.array([pan_at(rocket_x(T_LAUNCH + s / SR) if T_LAUNCH + s / SR < T_GONE else 0)
                                     for s in range(w.shape[1])])), T_LAUNCH, 0.9)
    for k, m in enumerate(('D4', 'G4', 'B4', 'D5', 'G5')):
        M.add('tune', tpt.play(n(m), 105, dur=0.25), T_LAUNCH + 0.12 * k, 0.6, pr)
    M.add('fx', whoosh(1.0, 300, 900, 0.5, seed=25), T_GONE, 0.4, -0.6)          # far away behind the house
    w = whoosh(T_LAND - T_RETURN, 3000, 600, 1.0, seed=26)
    M.add('fx', mono(w[0], np.array([pan_at(rocket_x(T_RETURN + s / SR)) for s in range(w.shape[1])])), T_RETURN, 0.9)
    for e, m, ln in ((0, 'G4', 0.5), (0.5, 'B4', 0.5), (1, 'D5', 0.5), (1.5, 'G5', 1.5)):
        M.add('tune', (tpt_s if ln > 1 else tpt).play(n(m), 108, dur=ln * BEAT), at(13, e), 0.8, 0.3)
    M.add('perc', timp.play(110), T_LAND, 0.8, pr)
    M.add('perc', crash.play(105), T_LAND, 0.5, pr)
    oompah(14, ['G'], 105)
    tune([[(0, 'D5', 0.5), (0.5, 'B4', 0.5), (1, 'G4', 0.5), (1.5, 'B4', 0.5), (2, 'D5', 2)]], 14, tpt, 'tune', 105, 0.0)
    M.add('perc', sleigh.play(110), T_CHEER, 0.6)
    for k in range(6):
        M.add('perc', slap.play(80), T_CHEER + 0.18 * k, 0.25, -0.7 if k % 2 else 0.7)

    # the socks: wah, wah, wah, waaah
    ps = pan_at(PRESENTS[2]['c'])
    for k, m in enumerate(('Bb3', 'A3', 'Ab3', 'G3')):
        d = 0.42 if k < 3 else 1.4
        M.add('tune', bone.play(n(m), 100, dur=d, release=0.2), T_SOCKS + 0.5 * k, 0.9, ps)
    M.add('bass', tuba.play(n('G1') + 12, 90), T_SOCKS + 1.5, 0.6)

    # the music box
    pm = pan_at(PRESENTS[3]['c'])
    for b, e, m in MB_TUNE:
        a = mbox.render([(0, n(m), 100, 0.6)], 1.8)
        M.add('motif', a, at(b, e), 1.0, pm)
    for j, c in enumerate(['G', 'D', 'G', 'D']):
        for i, m in enumerate(CH[c]):
            M.add('harm', harp.play(n(m), 62), at(18 + j, i * 0.5), 0.5, pm - 0.2)
            M.add('harm', harp.play(n(m) + 12, 58), at(18 + j, 2 + i * 0.5), 0.4, pm + 0.2)
        chord_pad(at(18 + j), c, BAR * 0.98, 55, 0.8)
    M.add('perc', tri.play(70), T_MB0, 0.4, pm)

    # the big box: uh-oh, thumps crowding together, a rising tremolo; silence; a yip; the burst
    pb = pan_at(BIG_C)
    for k, (e, m) in enumerate(((0, 'D3'), (1, 'C#3'), (2, 'D3'), (3, 'A2'))):
        M.add('tune', bsn.play(n(m), 95, dur=0.4), at(22, e), 0.8, pb)
    for th in THUMPS:
        M.add('perc', timp.play(int(80 + 30 * (th - T_SPOT) / 8), pitch=-2), th, 0.7, pb)
        M.add('perc', log_lo.play(80), th, 0.4, pb)
    for k, m in enumerate(('D4', 'D#4', 'E4', 'F4')):
        M.add('harm', trem.play(n(m), 60 + 10 * k, dur=BAR, release=0.1), at(22 + k), 0.6, pb)
        M.add('bass', cello.play(n('D2'), 90), at(22 + k), 0.7)
        M.add('tune', bsn.play(n(('A2', 'Bb2', 'B2', 'C3')[k]), 95, dur=0.4), at(22 + k, 2), 0.6, pb)
    r = sroll.play(80, dur=2.0)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_STILL - 2.0, 0.5, pb)
    M.add('perc', choke.play(100), T_STILL, 0.5, pb)
    bark(T_YIP, pb, 0.5)
    M.add('perc', timp.play(115, pitch=-2), T_THUMP, 0.9, pb)
    r = troll.play(90, dur=1.0)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_BURST - 1.0, 0.6, pb)
    M.add('perc', crash.play(122), T_BURST, 0.6, pb)
    M.add('drums', bd.play(122), T_BURST, 0.9, pb)
    M.add('fx', whoosh(2.0, 500, 5000, 1.0, seed=56), T_BURST, 0.7)
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('tune', tpt_s.play(n(m), 115, dur=0.8, release=0.3), T_BURST, 0.5)
    M.add('motif', chimes.play(100), T_BURST + 0.1, 0.5)
    bark(T_BURST + 0.25, pb, 1.0)

    # ---- 56-72: the puppy's laps: a galop ----
    oompah(28, GALOP_CH, 108)
    tune(GALOP, 28, xylo, 'motif', 100, 0.0, gain=0.6)
    tune(GALOP, 28, tpt, 'tune', 100, 0.0, long=tpt_s)
    tune(GALOP, 28, flute_st, 'tune', 90, 0.2, gain=0.5, octave=0)
    for j in range(8):
        for e in range(8):
            M.add('perc', sleigh.play(95 if e % 2 == 0 else 70), at(28 + j, e / 2), 0.35, -0.3 if e % 2 else 0.3)
    for tt_, xx in TURNS:                                # skid and bark at every turn
        p = pan_at(xx)
        M.add('perc', guiro.play(100, dur=0.4), tt_ - 0.2, 0.7, p)
        M.add('fx', slide(0.0, 0.25, 1400, 600, 0.3, 0.35), tt_ - 0.15, 0.6, p)
        bark(tt_ + 0.05, p)
        bark(tt_ + 0.3, p, 0.8)
    last = -1.0
    for tk, xk in kicks:                                 # scraps kicked up: glock sparkles (no more than 8 a second)
        if tk - last >= 0.125:
            M.add('motif', glock.play(n(('G5', 'B5', 'D6', 'A5', 'E5')[int(xk) % 5]), 62), tk, 0.3, pan_at(xk))
            last = tk
    # the tail chase: round and round on the porch
    oompah(36, ['D', 'D7'], 104)
    for k in range(int((T_SIT - T_CHASE) * 8)):
        t = T_CHASE + k / 8
        M.add('motif', xylo.play(n(('D5', 'F#5', 'A5', 'F#5')[k % 4]), 90), t, 0.5, pan_at(px[int(t / DT)]))
    r = sroll.play(90, dur=T_SIT - T_CHASE)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), T_CHASE, 0.45)

    # ---- 76-86: he sits; two barks; the dawn theme for everyone ----
    for tb in BARKS:
        bark(tb, pb)
    for j, c in enumerate(DAWN_CH[:3]):
        oompah(38 + j, [c], 100)
        chord_pad(at(38 + j), c, BAR * 0.98, 85)
    tune(DAWN[:3], 38, tpt, 'tune', 104, 0.0, long=tpt_s)
    tune(DAWN[:3], 38, flute, 'tune', 90, 0.2, gain=0.6)
    tune(DAWN[:3], 38, glock, 'motif', 80, -0.2, gain=0.4)
    M.add('perc', sleigh.play(110), T_SIT, 0.6)
    r = troll.play(95, dur=1.0)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_CHORD - 1.0, 0.6)
    for m in ('G4', 'B4', 'D5'):
        M.add('tune', tpt_s.play(n(m), 112, dur=2.8, release=1.0), T_CHORD, 0.7)
    for m in ('G3', 'B3', 'D4'):
        M.add('harm', horn.play(n(m), 110, dur=3.0, release=1.0), T_CHORD, 0.6)
        M.add('harm', vln.play(n(m) + 12, 95, dur=3.0, release=1.0), T_CHORD, 0.4)
    M.add('bass', tuba.play(n('G2'), 115), T_CHORD, 0.9)
    M.add('perc', crash.play(118), T_CHORD, 0.6)
    M.add('drums', bd.play(118), T_CHORD, 0.9)
    M.add('motif', chimes.play(100), T_CHORD + 0.1, 0.5)
    for i, m in enumerate(('G4', 'B4', 'D5', 'G5', 'B5', 'D6')):
        M.add('motif', glock.play(n(m), 85), T_CHORD + 0.1 * i, 0.5, -0.6 + 0.24 * i)
    bark(T_CHORD + 1.5, pb, 0.7)
