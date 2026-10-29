"""Stitched Together: a patchwork rag doll sits on the porch roof swaying to a waltz. She crouches, hops
off, and comes down in pieces: her head, both arms, her patchwork dress and her striped legs fly out
along the roof and land all over the house. Dazed, her head sees stars. Then the pieces scoot home on
the beat, inchworm hops, legs first; one arm sets off the wrong way, stops, thinks, and turns round.
A needle zips in off the free right end and stitches every joint (a bright stitch at each), she stands,
ta-da... and there is an arm sticking out of the top of her head, waving. She notices, yanks it off,
it flies round to where it belongs and the needle stitches it on properly. Ta-da again, and she dances
a polka: hop-step-close-step with her arms out, skips along the porch kicking on the offbeat, twirls
her skirt into a spray of coloured sparkles, and kicks. A curtsy, the needle sews a pink bow on her head, and her patchwork spreads out
over the whole house as a stitched quilt for the last chorus and a bright final chord.

The doll is a stack of parts along the roofline in path distance (head with hair and two eyes, arm,
dress of colour patches, arm, striped legs with shoes), drawn with exact span-over-pixel coverage like
Bone Yard's skeletons, so she keeps her size on every run. The polka is 126 BPM in 2/4 (bt(bar, beat));
every time below is a module constant shared with score()."""
import numpy as np
from pixelhome.fx import DT, hexc, light, perc, smoothstep, keys, lerp, nframes

CODE = 'NB05'
TITLE = 'Stitched Together'
KIND = 'show'
DESCRIPTION = ('A patchwork rag doll hops off the porch roof and lands in pieces all over the house. The pieces '
               'scoot back, a needle stitches her up (one arm in the wrong place), and she dances a reel.')

BPM = 126
BEAT = 60 / BPM                             # 2/4: a bar is two beats
BAR = 2 * BEAT
D = 64.0


def bt(bar, beat=0.0):
    return (2 * bar + beat) * BEAT


SKIN = hexc('#b8ccff')
HAIR = hexc('#d01818')
PATCH = [hexc(c) for c in ('#2048ff', '#b01a80', '#ffb020', '#10b0c0', '#ff3020')]
STOCK = [hexc('#e0e8ff'), hexc('#5030c0')]
SHOE = hexc('#ff2a40')
STITCH = hexc('#ffffff')
NEEDLE = hexc('#e8f0ff')
THREAD = hexc('#ffc040')
STAR = hexc('#ffe040')
BOW = hexc('#ff4aa0')
NIGHT = hexc('#1a2c90')
SPOT = hexc('#ffb860')
FLASH = hexc('#fff0d0')

K = 1.3                                     # figure scale: about 220 units head to toe
LEN = {p: K * v for p, v in (('head', 28.0), ('armA', 20.0), ('body', 50.0), ('armB', 20.0), ('legs', 36.0))}
RIGHT = ['head', 'armA', 'body', 'armB', 'legs']
WRONG = ['armB', 'head', 'armA', 'body', 'legs']    # an arm sewn on the top of her head
LOOSE, SEWN = 12.0, 3.0                     # joint gaps before and after stitching

CROUCH, JUMP, FALL, SPLAT = bt(8), bt(8, 1), bt(9), bt(10)
LAND_AT = {'head': ('Right', -150), 'armA': ('Left', 0), 'body': ('Porch Left', 0), 'armB': ('Right', 150),
           'legs': ('Porch Right', 0)}       # where each piece comes down (always on a front run): run and offset
SCOOT = {'legs': (bt(13), bt(18)), 'armB': (bt(13, 1), bt(19)), 'body': (bt(14), bt(20)),
         'head': (bt(14, 1), bt(21)), 'armA': (bt(15), bt(22))}   # (first hop, arrival); a hop on every beat
ASTRAY, HUH, TURN = 3, bt(17), bt(18)        # armA's wrong-way hops, its moment of doubt, when it turns back
NEEDLE_IN, STITCH0 = bt(23), bt(24)          # the needle flies in; joint j is stitched from STITCH0 + j*JSTEP
JSTEP = 2 * BAR
TADA, WAVE, NOTICE, YANK, CATCH = bt(32), bt(32, 1), bt(35), bt(36), bt(36, 1)
RESEW = (CATCH + 0.05, CATCH + 0.3)          # the two new joints, three quick passes each
TADA2 = bt(37, 1)
REEL, CURTSY, BOW_ON, FINALE, CHORD, END = bt(39), bt(55), bt(56, 1), bt(57), bt(63), bt(65, 1)
QUILT_V = 700.0                              # how fast the quilt spreads from her


def _back(u, c1=1.6):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def _layout(order, gaps):
    """Part -> offset of its first end from the figure's first end, and the figure's half length."""
    u, cur = {}, 0.0
    for i, p in enumerate(order):
        u[p] = cur
        cur += LEN[p] + (gaps[i] if i < len(gaps) else 0.0)
    return u, cur / 2


def _centres(c, order, gaps):
    u, half = _layout(order, gaps)
    return {p: c - half + u[p] + LEN[p] / 2 for p in order}


def centre(G):
    return float(G.pd[G.seg['Porch Front']].mean())


def landings(G):
    """Where each piece lands and when: {part: (centre, time)}. Flights start at SPLAT from her assembled
    position and take longer the further they go."""
    mid = {k: float(G.pd[G.seg[k]].mean()) for k in G.seg}
    start = _centres(centre(G), RIGHT, [SEWN] * 4)
    out = {}
    for p, (run, off) in LAND_AT.items():
        x = mid[run] + off
        out[p] = (x, SPLAT + 0.35 + abs(x - start[p]) / 1800)
    return out


def hops(G):
    """Each piece's hops home: {part: [(start time, from, to), ...]}, every hop one BEAT long."""
    slots = _centres(centre(G), WRONG, [LOOSE] * 4)
    land = landings(G)
    out = {}
    for p, (t0, t1) in SCOOT.items():
        a, b = land[p][0], slots[p]
        hs = []
        if p == 'armA':                     # off the wrong way first, a pause, then home
            away = a - np.sign(b - a) * 55 * ASTRAY
            for k in range(ASTRAY):
                hs.append((t0 + k * BEAT, lerp(a, away, k / ASTRAY), lerp(a, away, (k + 1) / ASTRAY)))
            a, t0 = away, TURN
        n = int(round((t1 - t0) / BEAT))
        for k in range(n):
            hs.append((t0 + k * BEAT, lerp(a, b, k / n), lerp(a, b, (k + 1) / n)))
        out[p] = hs
    return out


def passes():
    """The needle's stitching passes: [(time, joint, order)] with joint indexing that order's joints."""
    out = []
    for j in range(4):
        for k in range(4):
            out.append((STITCH0 + j * JSTEP + BEAT + k * BEAT / 2, j, 'WRONG'))
    for j, t0 in zip((2, 3), RESEW):
        for k in range(3):
            out.append((t0 + k * 0.1, j, 'RIGHT'))
    for k in range(4):                      # the bow
        out.append((BOW_ON - 0.8 + k * 0.2, -1, 'RIGHT'))
    return out


def sparkles(G, seed=55):
    """Coloured sparkles thrown off her skirt: (time, start, speed, life, colour index)."""
    rng = np.random.default_rng(seed)
    t0, x0, v, life, col = [], [], [], [], []
    bursts = [(REEL + (8 + k) * BAR + b * BEAT, 4) for k in range(4) for b in range(2)]
    bursts += [(TADA, 10), (TADA2, 14), (BOW_ON, 16), (CHORD, 30)]
    for t, n in bursts:
        for _ in range(n):
            t0.append(t)
            x0.append(0.0)                  # relative to her centre at that moment
            v.append(rng.uniform(150, 420) * rng.choice([-1, 1]))
            life.append(rng.uniform(0.8, 1.6))
            col.append(rng.integers(len(PATCH)))
    return np.array(t0), np.array(x0), np.array(v), np.array(life), np.array(col)


def _hit(f, k=0.09):
    return float(np.exp(-max(f, 0) * BEAT / k))


def _offkick(f, amp):
    """A kick that lands on the offbeat: out and back in the second half of the beat."""
    return amp * np.sin(np.pi * (2 * f - 1)) if f >= 0.5 else 0.0


def reel(t):
    """Her polka: (centre offset, arm spread, kick, skirt spin, flash) at time t of the dance."""
    b = (t - REEL) / BEAT
    bar, j = int(b // 2), int(b) % 2
    f = b - int(b)
    off, arms, kick, fl = 0.0, 0.0, 0.0, 0.25 * _hit(f) if j else 0.6 * _hit(f)
    spin = 0.0
    if bar < 4:                             # hop-step-close-step: a step to one side each bar, arms out
        tgt = lambda k: 24.0 * (1 if k % 2 == 0 else -1)
        step = lerp(tgt(bar - 1) if bar else 0.0, tgt(bar), smoothstep(0, 0.5, f) if j == 0 else 1.0)
        off = step - (5 * np.sin(np.pi * f) * np.sign(tgt(bar)) if j == 1 else 0.0)   # the close
        arms = 8 * np.sin(np.pi * (b % 2) / 2)
    elif bar < 8:                           # skip along the porch and back, kicking on the offbeat
        u = (b - 8) / 8
        off = -150 * np.sin(np.pi * u)
        kick = _offkick(f, 14)
        arms = 3.0
    elif bar < 12:                          # the twirl: skirt spins, arms flung out
        spin = 70 * (b - 16)
        arms = 10 + 4 * np.sin(2 * np.pi * b)
        off = 12 * np.sin(np.pi * b)
    elif bar < 15:                          # kicks on every offbeat
        kick = _offkick(f, 20)
        arms = 6.0 if f >= 0.5 else 0.0
        fl = max(0.7 * _hit(f), 0.5 * _hit(f - 0.5) if f >= 0.5 else 0)
    else:                                   # wind up into the curtsy
        arms = 12 * smoothstep(0, 1, (b - 30) / 2)
    return off, arms, kick, spin, fl


def render(G, seed=5):
    L = G.length
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    c0 = centre(G)
    land = landings(G)
    H = hops(G)
    PS = passes()
    sp_t, _, sp_v, sp_l, sp_c = sparkles(G)
    start = _centres(c0, RIGHT, [SEWN] * 4)
    wrong_sewn = _centres(c0, WRONG, [SEWN] * 4)

    def draw(spans, p, x, I, stretch=1.0, spin=0.0, blink=False):
        """Spans (a, z, intensity, colour) for part p centred at x."""
        h = LEN[p] * stretch / 2
        a0 = x - h

        def seg(v0, v1, col, k=1.0):
            spans.append((a0 + v0 * K * stretch, a0 + v1 * K * stretch, I * k, col))
        if p == 'head':
            seg(0, 8, HAIR)
            seg(8, 12, SKIN)
            if blink:
                seg(12, 22, SKIN)
            else:
                seg(15.5, 18.5, SKIN)
            seg(22, 28, SKIN)
        elif p in ('armA', 'armB'):
            seg(0, 20, SKIN, 0.85)
        elif p == 'body':
            s = spin % 50
            v = -s % 10
            k = int(np.floor(s / 10))
            if v > 0:
                seg(0, v, PATCH[(k - 1) % 5])
            while v < 50:
                seg(v, min(v + 10, 50), PATCH[k % 5])
                v += 10
                k += 1
        else:
            for k in range(5):
                seg(6 * k, 6 * k + 6, STOCK[k % 2], 0.9)
            seg(30, 36, SHOE)

    def joint_marks(spans, cen, order, gaps, I):
        for i in range(4):
            a, b = order[i], order[i + 1]
            x = (cen[a] + LEN[a] / 2 + cen[b] - LEN[b] / 2) / 2
            if gaps[i] <= SEWN + 0.5:
                for s in (-2.4, 2.4):
                    spans.append((x + s - 0.9, x + s + 0.9, I, STITCH))

    def scoot_pos(p, t):
        hs = H[p]
        if t < hs[0][0]:
            return land[p][0], 1.0
        for t0, a, b in hs:
            if t0 <= t < t0 + BEAT:
                u = smoothstep(0, 0.6, (t - t0) / BEAT)
                return lerp(a, b, u), 1 + 0.4 * np.sin(np.pi * u)
        return hs[-1][2], 1.0

    def wrong_gaps(t):
        g = []
        for j in range(4):
            s = STITCH0 + j * JSTEP
            g.append(lerp(LOOSE, SEWN, smoothstep(s + BEAT, s + 2.6 * BEAT, t)))
        return g

    def right_gaps(t):
        return [SEWN, SEWN] + [lerp(LOOSE, SEWN, smoothstep(r, r + 0.3, t)) for r in RESEW]

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        spans = []
        fl = 0.0
        blink = (t % 3.1) < 0.12
        I = smoothstep(0.3, 1.6, t) * (1 - smoothstep(END + 0.6, D - 0.2, t))
        cen, stretch, spin, order, gaps = None, {}, 0.0, RIGHT, [SEWN] * 4
        c = c0

        if t < SPLAT:                       # sitting, swaying, crouch, hop
            c = c0 + 10 * np.sin(2 * np.pi * t / BAR) * (t < CROUCH)
            g = SEWN
            if t >= CROUCH:
                g = keys(t, [(CROUCH, SEWN), (JUMP - 0.05, 0.5), (JUMP + 0.15, 14), (FALL, 9), (SPLAT, 4)])
                spin = 300 * max(0.0, t - FALL)
                if JUMP <= t < FALL:
                    I *= 0.65
            gaps = [g] * 4
            cen = _centres(c, RIGHT, gaps)
            if t >= SPLAT - 0.1:
                fl = 1.0
        elif t < SCOOT['armA'][1] + 0.4:   # in pieces: flight, landing, daze, the scoot home
            cen, order = {}, WRONG
            for p in RIGHT:
                x, tl = land[p]
                if t < tl:
                    u = (t - SPLAT) / (tl - SPLAT)
                    cen[p] = lerp(start[p], x, _back(u, 1.2))
                    stretch[p] = 1.3
                else:
                    pos, st = scoot_pos(p, t)
                    wob = 3 * np.sin(2 * np.pi * 9 * t) * np.exp(-(t - tl) * 2.5) if t < tl + 2 else 0
                    cen[p] = pos + wob
                    stretch[p] = st
            hx = cen['head']
            if land['head'][1] < t < SCOOT['head'][0]:      # seeing stars
                for k in range(3):
                    x = hx + 22 * np.sin(2 * np.pi * 1.3 * t + 2.1 * k)
                    spans.append((x - 2, x + 2, 0.75, STAR))
            if HUH <= t < TURN:             # the stray arm stops and thinks: a slow uncertain pulse
                fl = 0.0
            gaps = [LOOSE] * 4
        elif t < YANK:                      # stitched up wrong
            order, gaps = WRONG, wrong_gaps(t)
            cen = _centres(c0, order, gaps)
            if t >= TADA:
                fl = _hit((t - TADA) / BEAT, 0.15)
            if WAVE <= t < NOTICE:          # the arm on her head waves
                cen['armB'] += 7 * np.sin(2 * np.pi * (t - WAVE) / BEAT)
            if NOTICE <= t < YANK:          # she notices: a double take
                sh = 5 * np.sin(2 * np.pi * 5 * (t - NOTICE)) * (t - NOTICE < 0.6)
                cen['head'] += sh
                cen['armB'] += sh
        elif t < CATCH:                     # yanked off, flown round to the other side
            u = (t - YANK) / (CATCH - YANK)
            a = wrong_sewn
            b = _centres(c0, RIGHT, [SEWN, SEWN, LOOSE, LOOSE])
            cen = {p: lerp(a[p], b[p], smoothstep(0, 1, u)) for p in RIGHT}
            cen['armB'] = lerp(a['armB'], b['armB'], _back(u, 1.0))
            stretch['armB'] = 1.4
            fl = 0.6 * _hit((t - YANK) / BEAT)
            gaps = [SEWN, SEWN, LOOSE, LOOSE]
        else:                               # sewn on right; ta-da, the reel, the curtsy, the finale
            gaps = right_gaps(t)
            off = arms = kick = 0.0
            if t >= TADA2:
                fl = _hit((t - TADA2) / BEAT, 0.18)
            if REEL <= t < CURTSY:
                off, arms, kick, spin, fl = reel(t)
            elif t >= CURTSY:
                squash = keys(t, [(CURTSY, 0), (CURTSY + 0.6, 1), (BOW_ON + 0.2, 1), (BOW_ON + 0.6, 0)])
                gaps = [lerp(gp, 0.5, squash) for gp in gaps]
                I *= 1 - 0.25 * squash
                if t >= BOW_ON:
                    fl = _hit((t - BOW_ON) / BEAT, 0.15)
                if t >= FINALE:
                    b = (t - FINALE) / BEAT
                    fl = max(0.35 * _hit(b % 1), _hit((t - CHORD) / BEAT, 0.25) if t >= CHORD else 0)
                    arms = 6 * (np.sin(np.pi * b) > 0)
            gaps = [gaps[0], gaps[1] + arms, gaps[2] + arms, gaps[3] + kick]
            c = c0 + off
            cen = _centres(c, RIGHT, gaps)

        Ib = I * (0.75 + 0.25 * fl)
        for p in RIGHT:
            draw(spans, p, cen[p], Ib, stretch.get(p, 1.0), spin, blink and p == 'head')
        if t < SPLAT or t >= NEEDLE_IN:
            joint_marks(spans, cen, order, gaps, 0.9 * I)

        # the needle: in off the right end, stitching each joint, then the bow
        nx = None
        if NEEDLE_IN <= t < STITCH0:
            u = smoothstep(NEEDLE_IN, STITCH0, t)
            a, b = WRONG[0], WRONG[1]
            tx = (cen[a] + LEN[a] / 2 + cen[b] - LEN[b] / 2) / 2
            nx = lerp(L + 30, tx, u)
        elif STITCH0 <= t < TADA or RESEW[0] - 0.2 <= t < TADA2 or BOW_ON - 1.0 <= t < BOW_ON:
            near = [(pt, j, o) for pt, j, o in PS if pt <= t + 0.2]
            pt, j, o = near[-1] if near else PS[0]
            ordr = WRONG if o == 'WRONG' else RIGHT
            if j < 0:
                tx = cen['head'] - LEN['head'] / 2 - 4
            else:
                a, b = ordr[j], ordr[j + 1]
                tx = (cen[a] + LEN[a] / 2 + cen[b] - LEN[b] / 2) / 2
            side = 1 if (len(near) % 2) else -1
            nx = tx + 9 * side * np.cos(np.pi * np.clip((t - pt + 0.2) / 0.2, 0, 1))
            spans.append((min(nx, tx), max(nx, tx), 0.35 * I, THREAD))
        if nx is not None:
            spans.append((nx - 5, nx + 5, I, NEEDLE))

        # the bow on her head
        if t >= BOW_ON:
            hx = cen['head'] - LEN['head'] / 2
            pop = 1 + 0.6 * _hit((t - BOW_ON) / BEAT, 0.2)
            spans.append((hx - 14 * pop, hx - 8, I, BOW))
            spans.append((hx - 8, hx - 5, 0.6 * I, BOW))
            spans.append((hx - 5, hx + 1 * pop, I, BOW))

        # sparkles off her skirt
        live = (sp_t <= t) & (t < sp_t + sp_l)
        if live.any():
            u = (t - sp_t[live]) / sp_l[live]
            x = cen['body'] + sp_v[live] * 0.5 * (1 - np.exp(-(t - sp_t[live]) / 0.5))
            for xx, uu, cc in zip(x, u, sp_c[live]):
                spans.append((xx - 2.5, xx + 2.5, I * 0.9 * (1 - uu), PATCH[cc]))

        A = np.array([s[0] for s in spans])
        Z = np.array([s[1] for s in spans])
        Ks = np.array([s[2] for s in spans])
        C = np.array([s[3] for s in spans])
        ov = np.clip(np.minimum(Z[:, None], e1) - np.maximum(A[:, None], e0), 0, None) / w
        buf = (perc(np.clip(Ks, 0, 1.2))[:, None] * ov).T @ C
        cov = np.clip(ov.sum(0), 0, 1)

        # the night, a spotlight while she dances, and the quilt
        bg = light(NIGHT, 0.14 * smoothstep(0, 1.5, t) * (1 - smoothstep(END, D, t)) * np.ones(G.N))
        if REEL - 0.6 <= t < FINALE + 1:
            sp = smoothstep(REEL - 0.6, REEL, t) * (1 - smoothstep(FINALE, FINALE + 1, t))
            bg += light(SPOT, 0.13 * sp * np.exp(-((pdp - cen['body']) / 230) ** 2))
        if t >= FINALE:
            r = np.abs(pdp - c0)
            front = QUILT_V * (t - FINALE)
            q = smoothstep(front, front - 30, r) * (1 - smoothstep(END, D - 0.3, t))
            rel = (pdp - c0) / 44
            k = np.floor(rel).astype(int) % 5
            fr = rel % 1
            b = (t - FINALE) / BEAT
            lev = 0.34 + 0.08 * _hit(b % 1) + 0.5 * (_hit((t - CHORD) / BEAT, 0.3) if t >= CHORD else 0)
            bg += (perc(q * lev)[:, None] * np.array(PATCH)[k])
            dots = (fr < 0.05) | (fr > 0.95)
            bg += light(STITCH, 0.5 * q * dots)
            if t >= CHORD:
                bg += light(FLASH, 0.85 * q * np.exp(-(t - CHORD) / 0.45))
        out[fi][G.path] = np.clip(buf + bg * (1 - cov)[:, None], 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A perky polka in D at 126 (bt(bar, beat), 2/4). TUNE is the hook, eight bars that bounce off the A below and
# skip up to the E above; VERSE is the answer in G, the pieces' scooting-home tune. Oom-pah underneath: tuba or
# pizzicato on the beat, offbeat chords on a reedy organ with clarinet and oboe doubling the leads (the nearest
# thing to an accordion). Every hit below is a moment in render(): the hop, the slide-whistle fall, a plop where
# each piece lands, a pluck for every hop home (each piece its own instrument), the stray arm's "huh?", a plink
# for every needle pass, ta-das, the waving arm as a wah-wah horn on each beat, the yank, kicks on the offbeat,
# sparkles off her skirt, the bow, and the big last chord.

TUNE = [                                    # (beat, note, beats): eight bars of 2/4
    (0, 'D5', .5), (.5, 'A4', .5), (1, 'F#4', .5), (1.5, 'A4', .5),
    (2, 'D5', .5), (2.5, 'E5', .25), (2.75, 'F#5', .25), (3, 'E5', 1),
    (4, 'C#5', .5), (4.5, 'A4', .5), (5, 'E4', .5), (5.5, 'A4', .5),
    (6, 'C#5', .5), (6.5, 'D5', .25), (6.75, 'E5', .25), (7, 'D5', 1),
    (8, 'B4', .5), (8.5, 'D5', .5), (9, 'G5', .5), (9.5, 'F#5', .5),
    (10, 'E5', .5), (10.5, 'D5', .5), (11, 'C#5', .5), (11.5, 'B4', .5),
    (12, 'A4', .5), (12.5, 'B4', .25), (12.75, 'C#5', .25), (13, 'D5', .5), (13.5, 'E5', .5),
    (14, 'D5', 1.5)]
VERSE = [
    (0, 'B4', .5), (.5, 'B4', .5), (1, 'C5', .5), (1.5, 'D5', .5),
    (2, 'E5', .5), (2.5, 'D5', .5), (3, 'B4', 1),
    (4, 'A4', .5), (4.5, 'A4', .5), (5, 'B4', .5), (5.5, 'C5', .5),
    (6, 'D5', .5), (6.5, 'C5', .5), (7, 'A4', 1),
    (8, 'B4', .5), (8.5, 'B4', .5), (9, 'C5', .5), (9.5, 'D5', .5),
    (10, 'E5', .5), (10.5, 'F#5', .5), (11, 'G5', 1),
    (12, 'F#5', .5), (12.5, 'E5', .5), (13, 'D5', .5), (13.5, 'C#5', .5),
    (14, 'D5', 1.5)]
TUNE_CHORDS = ['D', 'A7', 'A7', 'D', 'G', 'A7', 'D', 'D']
VERSE_CHORDS = ['G', 'G', 'D7', 'D7', 'G', 'C', 'A7', 'D']
CH = {'D': ('F#3', 'A3', 'D4'), 'A7': ('E3', 'G3', 'C#4'), 'G': ('G3', 'B3', 'D4'), 'D7': ('F#3', 'C4', 'D4'),
      'C': ('E3', 'G3', 'C4')}
ROOT = {'D': ('D2', 'A1'), 'A7': ('A1', 'E2'), 'G': ('G1', 'D2'), 'D7': ('D2', 'A1'), 'C': ('C2', 'G1')}
PLAN = [(0, TUNE_CHORDS), (8, ['A7', 'A7']), (13, VERSE_CHORDS), (21, ['D', 'A7']), (24, TUNE_CHORDS),
        (32, ['D']), (39, TUNE_CHORDS), (47, VERSE_CHORDS), (55, ['A7', 'A7']), (57, TUNE_CHORDS[:6] + ['A7'])]


def score(M, G):
    from pixelhome.audio import note as n, slide, whoosh
    harp = M.sampler('Strings/Harp/*.wav')
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_l = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    organ = M.synth('Keys/House Organ')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    log = M.hits('Percussion/LogDrum*_MedM_v2*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    btree = M.hits('Percussion/BellTree_Stroke*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')
    for name, gain, rev in (('tune', 0.25, 0.2), ('band', 0.2, 0.14), ('bass', 0.31, 0.06), ('hops', 0.16, 0.15),
                            ('perc', 0.27, 0.12), ('drums', 0.23, 0.12), ('fx', 0.13, 0.2), ('brass', 0.21, 0.2),
                            ('sparkle', 0.14, 0.3), ('squeeze', 0.075, 0.15)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        return float(0.85 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    c0 = centre(G)
    pc = pan_at(c0)
    squeeze = []                            # offbeat organ chords: the accordion's bellows

    def chord_at(t):
        k = int(t // BAR + 1e-6)
        for b0, prog in reversed(PLAN):
            if k >= b0:
                return prog[min(k - b0, len(prog) - 1)]
        return 'D'

    def melody(seq, inst, t0, bus, vel, shift=0, gain=1.0, p=0.0, beats=(0, 99), legato=0.85):
        for b, m, ln in seq:
            if beats[0] <= b < beats[1]:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * legato), t0 + (b - beats[0]) * BEAT,
                      gain, p)

    def lead(seq, t0, vel=100, beats=(0, 99), gain=1.0, p=0.0):
        """The reedy lead: clarinet and oboe in unison, a touch apart in the stereo."""
        melody(seq, clar, t0, 'tune', vel, gain=0.8 * gain, p=p - 0.12, beats=beats)
        melody(seq, oboe, t0, 'tune', vel - 8, gain=0.6 * gain, p=p + 0.12, beats=beats)

    def oompah(k0, k1, big=True):           # bass on the beat, chords on the offbeats
        for k in range(k0, k1):
            c = chord_at(bt(k) + 0.01)
            for j in (0, 1):
                t = bt(k, j)
                M.add('bass', (tuba if big else cb).play(n(ROOT[c][j]), 104 if j == 0 else 92), t, 1.0)
                if big:
                    M.add('drums', bd.play(88 if j == 0 else 70), t, 0.5)
                for m in CH[c]:
                    M.add('band', pizz.play(n(m) + 12, 76), t + BEAT / 2, 0.45, -0.25)
                    squeeze.append((t + BEAT / 2, n(m) + 12, 74, BEAT * 0.35))
                if big:
                    M.add('drums', snare.play(70), t + BEAT / 2, 0.35, 0.2)
            if big and k % 2 == 0:
                M.add('perc', tamb.play(78), bt(k), 0.5, 0.3)

    # ---- 0-7.6: she sits and bounces; the hook on music box and glock over a light oom-pah ----
    oompah(0, 8, big=False)
    notes = [(b * BEAT, n(m) + 12, 66, ln * BEAT * 0.85) for b, m, ln in TUNE]
    M.add('tune', box.render(notes, D), 0.0, 0.9)
    melody(TUNE, glock, 0.0, 'sparkle', 70, gain=0.4)

    # ---- the hop and the fall ----
    M.add('band', bsn.play(n('A2'), 96, dur=0.3), CROUCH, 0.8, pc)
    M.add('fx', slide(0.0, 0.35, 500, 1400, 0.4, 0.3), JUMP, 0.9, pc)
    M.add('fx', slide(0.0, SPLAT - FALL, 1500, 260, SPLAT - FALL, 0.28, shape=0.6), FALL, 1.0, pc)
    M.add('drums', bd.play(124), SPLAT, 1.0, pc)
    M.add('drums', crash_s.play(110), SPLAT, 0.8, pc)
    M.add('drums', timp.play(118, pitch=-4), SPLAT, 0.8, pc)
    M.add('perc', slap.play(120), SPLAT, 0.9, pc)
    land = landings(G)
    plop = {'head': -3, 'armA': 5, 'body': -7, 'armB': 3, 'legs': 0}
    for p, (x, tl) in land.items():         # each piece plops down where it lands
        M.add('perc', log.play(115, pitch=plop[p]), tl, 1.0, pan_at(x))
        M.add('fx', whoosh(tl - SPLAT, 1800, 400, 0.18, seed=len(p)), SPLAT, 0.5, pan_at(x))

    # ---- dazed: stars round her head, a dizzy little glock figure ----
    hx = pan_at(land['head'][0])
    for k, t in enumerate(np.arange(land['head'][1] + 0.3, SCOOT['legs'][0] - 0.2, 0.19)):
        M.add('sparkle', glock.play(n(('E5', 'C#5', 'A4', 'C#5')[k % 4]), 72), t, 0.8, hx)
    M.add('fx', slide(0.0, 1.0, 900, 600, 1.0, 0.18, shape=0.8), land['head'][1] + 0.4, 0.6, hx)

    # ---- the scoot home: the verse on the reedy lead, a pluck for every hop ----
    oompah(13, 23)
    lead(VERSE, bt(13), 100)
    voice = {'legs': (wood, None), 'armB': (xylo, 0), 'body': (pizz, -12), 'head': (mar, 0), 'armA': (xylo, 12)}
    H = hops(G)
    for p, hs in H.items():
        inst, sh = voice[p]
        for k, (t0, a, b) in enumerate(hs):
            p_at = pan_at(lerp(a, b, 0.5))
            astray = p == 'armA' and k < ASTRAY
            if inst is wood:
                M.add('hops', wood.play(90), t0, 0.9, p_at)
                continue
            ch = CH[chord_at(t0 + 0.01)]
            m = n(ch[k % 3]) + 12 + sh - (k if astray else 0)
            M.add('hops', inst.play(m, 88), t0, 0.8, p_at)
        M.add('perc', clave.play(115), hs[-1][0] + BEAT * 0.6, 0.8, pan_at(hs[-1][2]))
        M.add('sparkle', glock.play(n('D6'), 90), hs[-1][0] + BEAT * 0.6, 0.6, pan_at(hs[-1][2]))
    pa = pan_at(H['armA'][ASTRAY - 1][2])
    M.add('band', bsn.play(n('D3'), 100, dur=0.25), HUH, 0.9, pa)       # "huh?"
    M.add('band', bsn.play(n('A3'), 104, dur=0.35), HUH + 0.3, 0.9, pa)
    M.add('fx', slide(0.0, 0.25, 700, 1600, 0.3, 0.3), TURN - 0.3, 0.8, pa)

    # ---- the needle: in off the right end, a plink for every pass; the hook on flute ----
    M.add('fx', whoosh(STITCH0 - NEEDLE_IN, 600, 3500, 0.35, seed=9), NEEDLE_IN, 0.8, 0.7)
    for j, m in enumerate(('A3', 'D4', 'F#4', 'A4', 'D5')):
        M.add('band', harp.play(n(m), 80), NEEDLE_IN + j * 0.08, 0.6, 0.5)
    oompah(24, 32, big=False)
    melody(TUNE, flute, STITCH0, 'tune', 92, gain=0.8)
    step = {}
    for pt, j, o in passes():
        k = step.get((j, o), 0)
        step[(j, o)] = k + 1
        ch = CH[chord_at(pt)]
        m = n(ch[k % 3]) + 24 + 12 * (k >= 3)
        M.add('sparkle', (glock if k % 2 else xylo).play(m, 92), pt, 0.7, pc)

    # ---- ta-da, the waving arm, the double take, the yank ----
    def tada(t, big=1.0):
        M.add('brass', tpt.play(n('A4'), 110, dur=0.12), t - 0.16, 0.8 * big, pc)
        M.add('brass', tpt_s.play(n('D5'), 118, dur=0.8 * big), t, 0.9 * big, pc)
        for m in ('D3', 'F#3', 'A3'):
            M.add('brass', horn.play(n(m), 108, dur=0.9), t, 0.5 * big, pc)
        M.add('drums', crash.play(110), t, 0.6 * big, pc)
        M.add('drums', timp.play(115), t, 0.6 * big, pc)
    tada(TADA)
    for k in range(int(round((NOTICE - WAVE) / BEAT))):     # wah-wah with each wave of the arm on her head
        t = WAVE + k * BEAT + BEAT / 4
        M.add('brass', mute.play(n('A3'), 100, dur=0.18), t, 0.9, pc)
        M.add('brass', mute.play(n('G3'), 92, dur=0.2), t + BEAT / 2, 0.9, pc)
    M.add('perc', ratchet.play(90, dur=0.5), NOTICE, 0.5, pc)
    M.add('band', bsn.play(n('D2'), 104, dur=0.3), NOTICE + 0.4, 1.0, pc)   # "hm?"
    M.add('band', bsn.play(n('A2'), 104, dur=0.4), NOTICE + 0.7, 1.0, pc)
    M.add('perc', slap.play(124), YANK, 1.0, pc)
    M.add('fx', slide(0.0, 0.08, 400, 1300, 0.1, 0.35), YANK, 0.9, pc)
    M.add('fx', slide(0.0, CATCH - YANK, 1300, 700, CATCH - YANK, 0.25, shape=0.4), YANK + 0.1, 0.8, pc)
    M.add('perc', clave.play(120), CATCH, 0.9, pc)
    tada(TADA2, 1.3)
    for j in range(2):                      # one, two: count in the polka
        M.add('perc', clave.play(105 + 10 * j), bt(38, j), 0.7, pc)
        M.add('drums', bd.play(85 + 15 * j), bt(38, j), 0.5)

    # ---- the polka: the hook, then the verse, the whole band ----
    k_reel = int(round(REEL / BAR))
    oompah(k_reel, k_reel + 16)
    lead(TUNE, REEL, 106)
    melody(TUNE, glock, REEL, 'sparkle', 80, gain=0.5, p=-0.1)
    melody(VERSE, flute, REEL + 8 * BAR, 'tune', 98, gain=0.8, legato=0.8)
    melody(VERSE, xylo, REEL + 8 * BAR, 'sparkle', 86, gain=0.6, p=0.15)
    lead(VERSE, REEL + 8 * BAR, 92, gain=0.5)
    for bar in range(16):
        t = REEL + bar * BAR
        if bar % 4 == 3:
            M.add('perc', tri.play(90), t + BEAT, 0.6, 0.4)
        if 4 <= bar < 8 or 12 <= bar < 15:  # kicks on the offbeat, where she is
            for j in (0, 1):
                tk = t + (j + 0.75) * BEAT
                off = reel(tk)[0]
                M.add('perc', (wood if bar < 8 else slap).play(108), tk, 0.8, pan_at(c0 + off))
        if 8 <= bar < 12 and bar % 2 == 0:  # the twirl: violins swirl up
            sv = vtrem.play(n('D4') + 3 * (bar - 8), 80, dur=2 * BAR)
            M.add('band', sv * np.linspace(0.3, 1, sv.shape[1]), t, 0.5, 0.2)
        if bar == 15:
            r = troll.play(90, dur=BAR)
            M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), t, 0.6)
    st, sx, sv_, sl, scol = sparkles(G)
    for k, t in enumerate(np.unique(st)):   # a ping for each burst off her skirt
        M.add('sparkle', glock.play(n(('D6', 'A5', 'F#5', 'B5')[k % 4]), 84), t, 0.7, pc)

    # ---- the curtsy, the bow ----
    for m in ('E3', 'G3', 'C#4', 'A4'):
        M.add('band', clar_l.play(n(m), 70, dur=2 * BAR), CURTSY, 0.35, -0.1)
    for j, m in enumerate(('A5', 'E5', 'C#5', 'A4', 'E4', 'C#4', 'A3')):
        M.add('band', harp.play(n(m), 80), CURTSY + 0.2 + j * 0.07, 0.6, -0.3)
    M.add('perc', btree.play(110), BOW_ON, 0.8, pc)
    for m in ('D5', 'F#5', 'A5'):
        M.add('sparkle', glock.play(n(m), 95), BOW_ON, 0.6, pc)
    r = ccresc.play(100, dur=FINALE - BOW_ON + 0.1)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]), BOW_ON, 0.4)

    # ---- the quilt and the last chorus: the hook, big, into the final chord ----
    kf = int(round(FINALE / BAR))
    oompah(kf, kf + 6)
    for inst, sh, vel, g, p, bus in ((tpt, 0, 110, 0.7, 0.1, 'tune'), (clar, 0, 104, 0.6, -0.15, 'tune'),
                                     (oboe, 0, 96, 0.45, 0.15, 'tune'), (flute, 12, 92, 0.35, 0.2, 'tune'),
                                     (glock, 0, 90, 0.5, 0.0, 'sparkle')):
        melody(TUNE, inst, FINALE, bus, vel, shift=sh, gain=g, p=p, beats=(0, 12), legato=0.9)
    for j, m in enumerate(('A4', 'B4', 'C#5')):             # the run up into the last chord
        M.add('brass', tpt.play(n(m), 112, dur=0.15), CHORD - BEAT + j * BEAT / 3, 0.7)
        M.add('sparkle', xylo.play(n(m) + 12, 100), CHORD - BEAT + j * BEAT / 3, 0.5)
    r = troll.play(100, dur=BAR)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), CHORD - BAR, 0.6)
    for m in ('D3', 'F#3', 'A3', 'D4'):
        M.add('brass', horn.play(n(m), 118, dur=END - CHORD + 1), CHORD, 0.55)
    for m in ('D4', 'F#4', 'A4'):
        M.add('brass', tpt_s.play(n(m), 116, dur=END - CHORD), CHORD, 0.45)
    M.add('tune', flute.play(n('D5'), 100, dur=END - CHORD), CHORD, 0.4)
    M.add('bass', tuba.play(n('D2'), 124), CHORD, 1.1)
    M.add('bass', cb.play(n('D1'), 124), CHORD, 0.9)
    for j, m in enumerate(('D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5', 'F#5', 'A5')):
        M.add('band', harp.play(n(m), 100), CHORD + j * 0.05, 0.7)
    M.add('drums', crash.play(124), CHORD, 1.0)
    M.add('drums', bd.play(124), CHORD, 1.0)
    M.add('drums', timp.play(124), CHORD, 0.9)
    M.add('perc', btree.play(110), CHORD + 0.3, 0.7)
    squeeze += [(CHORD, n(m) + 12, 90, END - CHORD) for m in CH['D']]
    M.add('squeeze', organ.render(squeeze, D), 0.0)
