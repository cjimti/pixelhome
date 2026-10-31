"""Here They Come: a jaunty 2/4 at 120 (a bar is a second). The front door is the middle of the Porch Front and
the house is waiting: amber dashes marching in toward the door on every beat, the porch ticking like a clock.
Then the relatives arrive, family by family, each in its own colour. A car's headlights sweep along a dark run
toward the porch (in off the free end of Right, or popping up on the Left wing), doors thunk with a flash each,
and the family marches up to the door in step, a block of its colour for each of them, hopping a step a beat.
The doorbell flashes the Porch Front (once for the grandparents, twice for the aunt, a frantic eight for the
cousins' kids, who bounce off the door while they wait), the door opens, and the family's colour bursts out of it
and rolls to both ends of the house, joining the party: a conga of stripes in every family's colour that marches
round the whole roofline to the band, hugs popping white on the beat. The uncle and the neighbours arrive at
once from both sides, racing each other to the porch. With everyone in, the party fills the house, marching one
way, then the other, then pulsing out from the door on every beat, faster and brighter. A pink flash at the Right
end: one last cousin. The party freezes and dims while she sprints up to the door and rings, slowly; the door
ticks, three times; it opens, everyone rushes to it at once, the stripes squeezing in from both ends to a blazing
knot at the door, a held breath, and the group hug goes off: a gold flash that floods out to both ends, and the
whole house dances in every family's colour and gold to the last chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, nframes

CODE = 'TG18'
TITLE = 'Here They Come'
KIND = 'show'
DESCRIPTION = ('The relatives arrive. Headlights sweep up to the porch, the doorbell rings again and again, each '
               'family bursts in its own colour, and the house becomes one big conga line until the group hug.')
VOICEOVER = "Ding dong! Somebody get the door, the whole family is pulling into the driveway."

D = 90.0
SEED = 18
BEAT = 0.5                                     # 2/4 at 120: a bar a second
DOOR = 1486.0                                  # middle of the Porch Front
AMBER = hexc('#ff7a12')
GOLD = hexc('#ffb000')
HUG = hexc('#fff0c8')
LAMP = hexc('#fff6dc')
TAIL = hexc('#ff1000')
PINK = hexc('#ff3aa0')
T_ARRIVE = 61.5                                # the last cousin flashes at the Right end; the party freezes
T_LAST_RING = 64.5
T_TICKS = (65.5, 66.5, 67.5)
T_OPEN_LAST, T_HELD, T_BOOM = 68.0, 71.5, 72.0

# side 'R' arrives off the free end of Right and walks up Porch Right; 'L' pops up on the Left wing
FAMILIES = [
    dict(name='grandparents', col='#a040ff', n=2, side='R', car=(4.0, 7.0), park=2200.0, doors=(7.5, 8.0),
         walk=(8.0, 11.0), rings=(11.0,), open=12.0),
    dict(name='aunt', col='#00d8c0', n=3, side='L', car=(13.0, 15.0), park=760.0, doors=(15.5, 15.8, 16.1),
         walk=(16.0, 18.0), rings=(18.0, 18.75), open=19.5),
    dict(name='cousins', col='#30ff30', n=5, side='R', car=(21.0, 22.5), park=2260.0, doors=(23.0, 23.2, 23.4, 23.6,
                                                                                           23.8),
         walk=(24.0, 25.5), rings=tuple(25.5 + 0.25 * k for k in range(8)), open=28.0, horn=20.5),
    dict(name='uncle', col='#ff1818', n=2, side='L', car=(30.5, 33.0), park=780.0, doors=(33.5, 34.0),
         walk=(34.0, 37.0), rings=(37.0,), open=38.0),
    dict(name='neighbours', col='#2a5cff', n=4, side='R', car=(30.5, 33.0), park=2200.0,
         doors=(33.5, 33.7, 33.9, 34.1), walk=(34.0, 37.0), rings=(37.0,), open=38.0),
]
LAST = dict(name='last cousin', col='#ff3aa0', n=1, side='R', walk=(62.0, T_LAST_RING), park=2600.0)


def spot(fam, k):
    """Where person k of a family waits by the door."""
    sgn = 1 if fam['side'] == 'R' else -1
    return DOOR + sgn * (30 + 40 * k)


def car_at(t, fam):
    t0, t1 = fam['car']
    start = 2640.0 if fam['side'] == 'R' else fam['park'] - 280
    u = np.clip((t - t0) / (t1 - t0), 0, 1)
    return fam['park'] + (start - fam['park']) * (1 - u) ** 2


def walker(t, fam, k):
    """Person k's position on the way to the door: hopping a step a beat (the kids run and bounce)."""
    t0, t1 = fam['walk']
    p0, p1 = fam['park'], spot(fam, k)
    if fam['name'] in ('cousins', 'last cousin'):
        ta = t1 - 0.25 * k if fam['name'] == 'cousins' else t1
        u = np.clip((t - t0) / (ta - t0), 0, 1)
        x = p0 + (p1 - p0) * u
        if t > ta:
            a = t - ta
            x = p1 + 90 * np.exp(-a / 2.5) * np.sin(2 * np.pi * (1.4 + 0.2 * k) * a + k) * (k % 2 * 2 - 1)
        return x
    steps = round((t1 - t0) / BEAT)
    u = (t - t0) / BEAT
    if u <= 0:
        return p0 + (1 if fam['side'] == 'R' else -1) * 40 * k
    s = min(int(u), steps)
    s = s + (float(smoothstep(0, 0.5, u - s)) if s < steps else 0.0)
    start = p0 + (1 if fam['side'] == 'R' else -1) * 40 * k
    return start + (p1 - start) * s / steps


def rings():
    """(time, kind): 'ding' alone for the kids, 'dingdong' otherwise, 'slow' for the last one."""
    out = []
    for fam in FAMILIES:
        for t in fam['rings']:
            if fam['name'] == 'neighbours':
                continue
            out.append((t, 'ding' if fam['name'] == 'cousins' else 'dingdong'))
    out.append((T_LAST_RING, 'slow'))
    return sorted(out)


def opens():
    """(time, colours that come in)."""
    out = {}
    for fam in FAMILIES:
        out.setdefault(fam['open'], []).append(hexc(fam['col']))
    out[T_OPEN_LAST] = [PINK]
    return sorted(out.items())


def hugs(seed=SEED):
    """Every hug: (time, place, size). At the door as each family comes in, then on the beat all over the house."""
    rng = np.random.default_rng(seed)
    out = []
    for t_open, cols in opens()[:-1]:
        for k in range(2 * len(cols) + 1):
            out.append((t_open + 0.5 + 0.25 * k, DOOR + rng.uniform(-60, 60), 1.0))
    t = 20.0
    while t < T_ARRIVE - 0.5:
        n_in = sum(1 for o, _ in opens() if o < t)
        busy = 1 if t < 42 else (2 if t < 56 else 3)
        if rng.uniform() < 0.3 * n_in:
            for _ in range(busy):
                out.append((t, rng.uniform(560, 2480), 0.7))
        t += BEAT
    return sorted(out)


def party_speed(t):
    """How fast the conga marches (units a second, + toward the Right end)."""
    return float(np.interp(t, [0, 40, 42, 49.5, 50.5, 55.5, 56.5, T_ARRIVE, T_ARRIVE + 0.3, T_BOOM, T_BOOM + 0.5, 79.5,
                               80.5, 83.5, 84.5, 90],
                           [90, 110, 220, 220, -260, -260, 380, 380, 0, 0, 320, 320, -320, -320, 160, 120]))


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    seg_lo = np.array(sorted(G.pd[G.seg[s]].min() for s in G.seg))
    seg_of = np.searchsorted(seg_lo, pdp, side='right') - 1
    pf = seg_of == 3
    rng_list = rings()
    ring_t = np.array([r[0] for r in rng_list])
    op = opens()
    hug_list = hugs(seed)
    hug_t = np.array([h[0] for h in hug_list])
    rng = np.random.default_rng(seed + 3)
    tw_p = rng.uniform(0, 2 * np.pi, G.N)
    offset = 0.0
    d0 = np.abs(pdp - DOOR)

    def g(c, w):
        return np.exp(-((pdp - c) / w) ** 2)

    for f in range(F):
        t = f * DT
        offset += party_speed(t) * DT
        beat_ph = (t / BEAT) % 1.0
        pulse = np.exp(-beat_ph / 0.15)
        on_bar = np.exp(-((t % 1.0) / 0.12))
        buf = np.zeros((G.N, 3))
        fade = keys(t, [(0, 0), (1.0, 1), (88.5, 1), (90, 0)])

        # ---- the runs where something is arriving go dark for contrast ----
        busy = np.zeros(G.N)
        for fam in FAMILIES:
            t0, t1 = fam['car']
            if t0 - 0.3 <= t < fam['walk'][1] + 0.3:
                runs = {int(np.searchsorted(seg_lo, car_at(min(t, t1), fam), side='right') - 1)}
                if t >= fam['walk'][0]:
                    runs |= {int(np.searchsorted(seg_lo, walker(t, fam, 0), side='right') - 1)}
                for r in runs:
                    busy = np.maximum(busy, (seg_of == r) * smoothstep(t0 - 0.3, t0, t))

        # ---- the house waiting: amber dashes marching in toward the door, the porch ticking ----
        wait = 1 - smoothstep(12.0, 14.0, t)
        if wait > 0:
            steps = np.floor(t / BEAT) + smoothstep(0, 0.4, beat_ph)
            dash = 0.5 + 0.5 * np.cos(2 * np.pi * (d0 / 120 + steps * 0.5))
            buf += light(AMBER, wait * fade * (1 - 0.8 * busy) * (0.12 + 0.3 * dash ** 4))
            tick = ((pdp < DOOR) == (int(t / BEAT) % 2 == 0)) * pf
            buf += light(AMBER, wait * fade * 0.55 * pulse * tick)

        # ---- the party: a conga of every family's colour that has come in, marching round the house ----
        cols = [hexc('#ff7a12')]
        n_pix = np.ones(G.N, int)
        for t_open, cs in op:
            if t_open == T_OPEN_LAST:
                continue
            reached = (t - t_open) * 1000 > d0
            for c in cs:
                cols.append(c)
                n_pix += reached
        if t >= T_OPEN_LAST:
            cols.append(PINK)
        cols = np.array(cols)
        W = float(np.interp(t, [0, 42, 50, 56, 62, 71.9, 72, 90], [170, 150, 120, 100, 100, 100, 150, 150]))
        s = pdp - offset
        # the rush: everyone squeezing in from both ends toward the door
        squeeze = 1.0
        if t >= T_OPEN_LAST + 0.3:
            squeeze = 1 + 6 * smoothstep(T_OPEN_LAST + 0.3, T_HELD, t) * (t < T_BOOM)
            s = DOOR + (pdp - DOOR) * squeeze - offset
        k = np.floor(s / W).astype(int)
        frac = s / W - k
        n_use = np.where(t >= T_OPEN_LAST, len(cols) - 1, n_pix - 1)
        idx = 1 + np.mod(k, np.maximum(n_use, 1))
        idx = np.where(n_use == 0, 0, idx)
        idx = np.where(t >= T_BOOM, np.mod(k, len(cols) - 1) + 1, idx)
        edge = np.sin(np.pi * frac) ** 0.45
        n_in = float(np.sum(np.array([o for o, _ in op]) <= t))
        lvl = (0.3 + 0.06 * n_in) * edge * (1 + 0.35 * pulse)
        if 56 <= t < T_ARRIVE:                                      # pulsing out from the door on every beat
            lvl = lvl * (0.6 + 0.7 * np.exp(-((d0 - 1200 * beat_ph) / 160) ** 2))
        hush = 1 - 0.75 * smoothstep(T_ARRIVE, T_ARRIVE + 0.3, t) * (1 - smoothstep(T_OPEN_LAST, T_OPEN_LAST + 0.3, t))
        for tk in (T_LAST_RING,) + T_TICKS:                         # every head turns to the door: a ripple in
            uk = t - tk
            if 0 <= uk < 1.6:
                hush = hush + 0.6 * np.exp(-((d0 - (1300 - 1000 * uk)) / 120) ** 2) * (1300 - 1000 * uk > 0)
        rush_env = 1.0
        if T_OPEN_LAST + 0.3 <= t < T_BOOM:
            w = 1500 / squeeze
            rush_env = np.exp(-(d0 / w) ** 4) * (1 + 0.8 * smoothstep(T_OPEN_LAST, T_HELD, t))
            if t >= T_HELD:                                         # the held breath: a tight bright knot only
                rush_env = rush_env * np.exp(-(d0 / 60) ** 2) * 1.3
        party_on = smoothstep(12.0, 12.5, t) * (1 - smoothstep(T_BOOM - 0.05, T_BOOM, t)) + (t >= T_BOOM)
        if t >= T_BOOM:
            lvl = (0.45 + 0.3 * pulse) * edge
            reach = np.clip((1100 * (t - T_BOOM) - d0) / 150, 0, 1)
            lvl = lvl * reach * keys(t, [(T_BOOM, 1.0), (86, 1.0), (88, 0.8), (90, 0.6)])
        visible = n_pix > 1 if t < T_OPEN_LAST else np.ones(G.N, bool)
        inten = np.clip(lvl * hush * rush_env * party_on * (1 - 0.75 * busy) * visible, 0, 1)
        buf += light(1.0, inten) * cols[idx] * fade
        if t >= T_BOOM:                                            # gold twinkles all through the finale
            reach = np.clip((1100 * (t - T_BOOM) - d0) / 150, 0, 1)
            tw = 0.5 + 0.5 * np.sin(2 * np.pi * 1.3 * t + tw_p)
            buf += light(GOLD, reach * (0.12 + 0.25 * tw ** 6 + 0.12 * on_bar) * fade)

        # ---- cars: headlights sweeping along the dark run, tail lights; doors flash ----
        for fam in FAMILIES:
            t0, t1 = fam['car']
            if t0 <= t < t1 + 1.2:
                c = car_at(t, fam)
                dr = -1 if fam['side'] == 'R' else 1
                on = smoothstep(t0, t0 + 0.15, t) * (1 - smoothstep(t1 + 0.5, t1 + 1.1, t))
                ahead = (pdp - c) * dr
                beam = np.where(ahead > 0, np.exp(-ahead / 320) * (1 - np.exp(-(ahead / 30) ** 2)), 0)
                buf += light(LAMP, on * (np.exp(-((pdp - c) / 8) ** 2) + np.exp(-((pdp - c + dr * 22) / 8) ** 2)
                                         + 0.6 * beam))
                buf += light(TAIL, on * 0.8 * np.exp(-((pdp - c + dr * 70) / 9) ** 2))
                if fam['side'] == 'L' and t < t0 + 0.5:             # it pops up on the Left wing
                    buf += light(LAMP, 0.8 * np.exp(-(t - t0) / 0.12) * g(c, 60))
            for td in fam['doors']:
                if 0 <= t - td < 0.4:
                    buf += light(LAMP, 0.8 * np.exp(-(t - td) / 0.08) * g(fam['park'], 40))
            if fam.get('horn') is not None and 0 <= t - fam['horn'] < 0.8:      # beep beep, off past the Right end
                u = t - fam['horn']
                buf += light(LAMP, float((u % 0.34) < 0.18) * 0.9 * g(2512, 70))

        # ---- the families marching up to the door, a block of colour each, hopping in step ----
        for fam in FAMILIES + [LAST]:
            t0, t1 = fam['walk']
            t_end = fam.get('open', T_OPEN_LAST) + 0.3
            if not (t0 - 0.1 <= t < t_end):
                continue
            col = hexc(fam['col'])
            for kk in range(fam['n']):
                x = walker(t, fam, kk)
                hop = 0.75 + 0.25 * pulse
                w = 11 if fam['name'] not in ('cousins', 'last cousin') else 8
                buf += light(col, hop * np.clip((w + 4 - np.abs(pdp - x)) / 4, 0, 1))
                buf += light(col, 0.3 * g(x, 40))
            if t < t1:                                              # the run they're on pulses with their steps
                r = int(np.searchsorted(seg_lo, walker(t, fam, 0), side='right') - 1)
                buf += light(col, 0.22 * pulse * (seg_of == r))
        if T_ARRIVE <= t < T_ARRIVE + 0.6:                          # pink flash at the Right end
            buf += light(PINK, 0.95 * np.exp(-(t - T_ARRIVE) / 0.15) * g(2512, 120))
        if LAST['walk'][0] <= t < T_LAST_RING:                      # her wake
            x = walker(t, LAST, 0)
            behind = pdp - x
            buf += light(PINK, 0.6 * np.where(behind > 0, np.exp(-behind / 200), 0) * (pdp < 2520))

        # ---- the doorbell: the Porch Front flashes, ding high and bright, dong wider ----
        for i in np.nonzero((t - ring_t >= 0) & (t - ring_t < 1.6))[0]:
            tr, kind = rng_list[i]
            u = t - tr
            gap = 0.9 if kind == 'slow' else 0.4
            buf += light(HUG, 0.8 * np.exp(-u / 0.15) * pf)
            if kind != 'ding' and u > gap:
                buf += light(HUG, 0.6 * np.exp(-(u - gap) / 0.25) * np.exp(-((d0 - 600 * (u - gap)) / 100) ** 2))
        for tk in T_TICKS:                                          # the door ticks in the hush
            if 0 <= t - tk < 0.5:
                buf += light(AMBER, 0.7 * np.exp(-(t - tk) / 0.12) * g(DOOR, 70))
        # ---- the door opens: amber spills out and the family's colour bursts out to both ends ----
        for t_open, cs in op:
            u = t - t_open
            if 0 <= u < 3:
                buf += light(AMBER, 0.85 * np.exp(-u / 0.5) * g(DOOR, 120))
                for j, c in enumerate(cs):
                    front = 1000 * u - 140 * j
                    buf += light(c, 0.95 * np.exp(-((d0 - front) / 70) ** 2) * (0 < front) * (u < 2.6))
        # ---- hugs: a white-gold burst where they meet, a ring out ----
        for i in np.nonzero((t - hug_t >= 0) & (t - hug_t < 0.8))[0]:
            th, where, size = hug_list[i]
            u = t - th
            r = np.abs(pdp - where)
            hh = hush if t < T_BOOM else 1.0
            buf += light(HUG, hh * size * 0.95 * np.exp(-u / 0.12) * np.exp(-(r / 12) ** 2))
            buf += light(GOLD, hh * size * 0.55 * np.exp(-((r - 260 * u) / 20) ** 2) * np.exp(-u / 0.3))
        # ---- the group hug: a flash at the door, a gold flood out to both ends ----
        if t >= T_BOOM:
            u = t - T_BOOM
            buf += light(HUG, 0.95 * np.exp(-u / 0.35) * np.exp(-(d0 / 200) ** 2))
            front = 1100 * u
            buf += light(GOLD, 0.95 * np.exp(-((d0 - front) / 80) ** 2) * (u < 2.5))
            for tb in (80.0, 84.0):                                 # each phrase: a gold sweep end to end
                ub = t - tb
                if 0 <= ub < 2.0:
                    hd = G.length * ub / 1.6 if tb == 80.0 else G.length * (1 - ub / 1.6)
                    buf += light(GOLD, 0.7 * np.exp(-((pdp - hd) / 120) ** 2))
            if t >= 86.0:
                buf += light(HUG, 0.5 * np.exp(-(t - 86.0) / 0.3))
        out[f][G.path] = buf
    return np.clip(out, 0, 1)


# ---------------------------------------------------------------- music ----------------------------------------------
# A jaunty tune in G, 2/4 at 120 (a bar a second), on a little band: tuba, pizzicato, a banjo-ish violin pizz, clarinet
# and a snare that joins as the house fills. A wood block ticks at the door while it waits. Each family's car brings
# its own instrument in on top (bassoon for the grandparents, oboe for the aunt, piccolo and xylophone for the kids,
# a trombone for the uncle, trumpet for the neighbours, flute for the last cousin), and every car is an engine that
# rolls along the roof to where it parks, then its doors, footsteps in step and the doorbell, in B and G like the
# tune. Every hug is a glockenspiel sparkle where it is, and the chatter inside grows with every family. The race
# is two engines and a snare on every eighth; the party is the tune for everyone, the bridge on trumpet, then the
# tune again over a drum that pounds every beat. The last cousin's flash stops the band; her slow doorbell, three
# ticks, then a drum roll and rising strings rush everyone to the door, a held breath, and the group hug is a crash,
# a cheer and the tune for the whole band.

CH = {'G': (43, 47, 50), 'D': (50, 54, 57), 'D7': (50, 54, 57, 60), 'C': (48, 52, 55), 'Em': (40, 43, 47),
      'Am': (45, 48, 52), 'B7': (47, 51, 54, 57)}
ROOTS = {'G': (43, 38), 'D': (38, 45), 'D7': (38, 45), 'C': (36, 43), 'Em': (40, 47), 'Am': (45, 40), 'B7': (47, 42)}
# (bar, eighth, note, eighths)
TUNE = [(0, 0, 'D4', 1), (0, 1, 'G4', 1), (0, 2, 'B4', 1), (0, 3, 'G4', 1), (1, 0, 'A4', 2), (1, 2, 'F#4', 1),
        (1, 3, 'D4', 1), (2, 0, 'E4', 1), (2, 1, 'G4', 1), (2, 2, 'C5', 1), (2, 3, 'B4', 1), (3, 0, 'A4', 3),
        (4, 0, 'B4', 1), (4, 1, 'D5', 1), (4, 2, 'C5', 1), (4, 3, 'B4', 1), (5, 0, 'A4', 1), (5, 1, 'G4', 1),
        (5, 2, 'F#4', 1), (5, 3, 'A4', 1), (6, 0, 'G4', 1), (6, 1, 'E4', 1), (6, 2, 'D4', 1), (6, 3, 'F#4', 1),
        (7, 0, 'G4', 3)]
TUNE_CH = ['G', 'G', 'D', 'D', 'C', 'C', 'D', 'D7', 'G', 'G', 'D', 'D', 'C', 'D', 'G', 'G']      # by beat
BRIDGE = [(0, 0, 'E5', 2), (0, 2, 'D5', 1), (0, 3, 'B4', 1), (1, 0, 'C5', 2), (1, 2, 'A4', 2), (2, 0, 'D5', 2),
          (2, 2, 'C5', 1), (2, 3, 'A4', 1), (3, 0, 'B4', 3), (4, 0, 'C5', 1), (4, 1, 'B4', 1), (4, 2, 'A4', 1),
          (4, 3, 'G4', 1), (5, 0, 'F#4', 1), (5, 1, 'A4', 1), (5, 2, 'D5', 2), (6, 0, 'C5', 1), (6, 1, 'A4', 1),
          (6, 2, 'F#4', 1), (6, 3, 'A4', 1), (7, 0, 'G4', 3)]
BRIDGE_CH = ['Em', 'Em', 'C', 'Am', 'D', 'D', 'G', 'G', 'C', 'C', 'D', 'D', 'Am', 'D7', 'G', 'G']
VOWELS = {'a': (780, 1200, 2500), 'e': (500, 1850, 2500), 'i': (320, 2200, 2900), 'o': (520, 880, 2400),
          'u': (360, 800, 2300)}


def score(M, G):
    from pixelhome.audio import SR, note as n
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    clar_l = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    picc = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tbn = M.sampler('Brass/OldTrombone/Short/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    banjo = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cel = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    tbell = M.sampler('Percussion/TB_hit_*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit_v1*.wav')
    snare = M.hits('Percussion/Snare2-taps*.wav')
    shit = M.hits('Percussion/Snare2-HitSN*.wav')
    sn_roll = M.hits('Percussion/Snare2-rollNS*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')

    for name, gain, rev in (('melody', 0.4, 0.22), ('guest', 0.34, 0.22), ('band', 0.28, 0.16), ('bass', 0.36, 0.08),
                            ('strings', 0.24, 0.28), ('mallet', 0.3, 0.2), ('drums', 0.42, 0.14), ('bell', 0.4, 0.3),
                            ('car', 0.22, 0.12), ('fx', 0.5, 0.15), ('crowd', 0.3, 0.25)):
        M.bus(name, gain=0.7 * gain, reverb=rev)
    M.fader('crowd', [(0, 0), (T_ARRIVE, 0), (T_ARRIVE + 0.3, -30), (T_OPEN_LAST, -30), (T_OPEN_LAST + 0.4, -6),
                      (T_HELD, -6), (T_HELD + 0.05, -30), (T_BOOM, 0)])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def away(d):
        return float(np.clip(1 - (d - 2512) / 300, 0.2, 1)) if d > 2512 else 1.0

    def travel(sig, pans):                  # a sound that moves while it plays, along a pan curve
        a = (np.interp(np.linspace(0, 1, sig.shape[1]), np.linspace(0, 1, len(pans)), pans) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    door_p = pan_at(DOOR)
    E8 = 0.25
    nrng = np.random.default_rng(SEED + 7)

    def lowpass_noise(seconds, fc, lo=30):
        nn = int(seconds * SR)
        x = np.fft.rfft(nrng.normal(0, 1, nn))
        fr = np.fft.rfftfreq(nn, 1 / SR)
        x *= np.exp(-(fr / fc) ** 2) * (fr > lo)
        y = np.fft.irfft(x, nn)
        return y / (np.abs(y).max() + 1e-9)

    def tune(t0, phrase, inst, bus, vel, up=0, gain=1.0, pan=0.0, short=0.9, bars=None):
        for b, e, m, ln in phrase:
            if bars is not None and b >= bars:
                continue
            M.add(bus, inst.play(n(m) + up, vel, dur=ln * E8 * short, release=0.1), t0 + b + e * E8, gain, pan)

    def band(t0, chords, vel, snare_on=False, tuba_on=True, banjo_on=True, drive=False):
        """Oom-pah: the bass on the beats, pizzicato chords and a banjo pluck off them; snare on the offbeats."""
        for k, c in enumerate(chords):
            t = t0 + k * 0.5
            r = ROOTS[c][k % 2]
            if tuba_on:
                M.add('bass', tuba.play(r, vel), t, 1.0)
            M.add('bass', pizz.play(r, vel - 10), t, 0.6)
            for m in CH[c][:3]:
                M.add('band', pizz.play(m + 12, vel - 22), t + E8, 0.5, 0.2)
            if banjo_on:
                tones_ = sorted(m + 12 * o for m in CH[c] for o in (1, 2) if 55 <= m + 12 * o <= 76)
                for j, m in enumerate(tones_[:3]):
                    M.add('band', banjo.play(m, vel - 15), t + E8 + 0.03 * j, 0.45, -0.25)
            if snare_on:
                M.add('drums', snare.play(vel - 20), t + E8, 0.6)
                if k % 4 == 3:
                    M.add('drums', tamb.play(vel - 25), t + E8, 0.5, 0.3)
            if drive:
                M.add('drums', bd.play(vel), t, 0.7)
                M.add('drums', snare.play(vel - 30), t + E8 / 2 * 3, 0.35)

    # ---- the crowd: a library of syllables, men, women and kids, talking inside ----
    def syllable(f0, dur, v0, v1, rng):
        nn = int(dur * SR)
        tt = np.arange(nn) / SR
        uu = tt / dur
        f = f0 * (1 + rng.uniform(-0.12, 0.18) * uu + 0.04 * np.sin(np.pi * uu))
        ph = 2 * np.pi * np.cumsum(f) / SR
        F0, F1 = np.array(VOWELS[v0]), np.array(VOWELS[v1])
        sig = np.zeros(nn)
        for k in range(1, 30):
            fk = k * f0
            if fk > 3600:
                break
            Fm = F0[:, None] * (1 - uu) + F1[:, None] * uu
            a = (np.exp(-((fk - Fm[0]) / 130) ** 2) + 0.6 * np.exp(-((fk - Fm[1]) / 170) ** 2)
                 + 0.2 * np.exp(-((fk - Fm[2]) / 220) ** 2) + 0.05 / k)
            sig += a * np.sin(k * ph)
        env = np.sin(np.pi * np.clip(uu, 0, 1)) ** 0.6
        sig = sig * env
        sig /= np.abs(sig).max() + 1e-9
        return sig

    crng = np.random.default_rng(SEED + 11)
    vk = list(VOWELS)
    lib = {}
    for kind, (lo, hi) in (('man', (100, 140)), ('woman', (180, 240)), ('kid', (250, 330))):
        lib[kind] = [syllable(crng.uniform(lo, hi), crng.uniform(0.1, 0.2), vk[crng.integers(5)], vk[crng.integers(5)],
                              crng) for _ in range(28)]

    def babble(t0, t1, kind, pan, level, rate=1.0):
        t = t0
        while t < t1:
            phrase_end = t + crng.uniform(0.8, 2.4)
            pitch = crng.uniform(0.9, 1.15)
            while t < min(phrase_end, t1):
                s = lib[kind][crng.integers(len(lib[kind]))]
                if pitch != 1.0:
                    idx = np.arange(0, len(s) - 1, pitch)
                    s = np.interp(idx, np.arange(len(s)), s)
                M.add('crowd', np.vstack([s, s]) * 0.25, t, level * crng.uniform(0.6, 1.0),
                      float(np.clip(pan + crng.uniform(-0.15, 0.15), -1, 1)))
                t += len(s) / SR * crng.uniform(0.9, 1.3) / rate
            t += crng.uniform(0.4, 1.6) / rate

    def cheer(t, pan, size=1.0, kind=None):
        for j in range(int(3 + 3 * size)):
            k = kind or ('man', 'woman', 'kid')[crng.integers(3)]
            s = lib[k][crng.integers(len(lib[k]))]
            idx = np.arange(0, len(s) - 1, crng.uniform(1.1, 1.4))
            s = np.interp(idx, np.arange(len(s)), s)
            M.add('crowd', np.vstack([s, s]) * 0.4, t + crng.uniform(0, 0.12), size, pan + crng.uniform(-0.1, 0.1))

    kinds = {'grandparents': ('man', 'woman'), 'aunt': ('woman', 'kid', 'man'), 'cousins': ('kid',) * 4 + ('woman',),
             'uncle': ('man', 'woman'), 'neighbours': ('man', 'woman', 'kid', 'kid')}
    for fam in FAMILIES:
        for k in range(fam['n']):
            kind = kinds[fam['name']][k % len(kinds[fam['name']])]
            p = float(crng.uniform(-0.8, 0.8))
            babble(fam['open'] + 0.8, T_ARRIVE, kind, p, 0.5)
            babble(T_BOOM + 1.0, D - 1.5, kind, p, 0.4, rate=1.3)

    # ---- cars: engine along the roof to where it parks, tyres, doors; footsteps in step up to the door ----
    for fam in FAMILIES:
        t0, t1 = fam['car']
        dur = t1 - t0 + 1.0
        tt = np.arange(int(dur * SR)) / SR
        rumble = lowpass_noise(dur, 160) * (1 + 0.5 * np.sin(2 * np.pi * 31 * tt))
        rumble += 0.5 * np.sin(2 * np.pi * (48 - 14 * np.clip(tt / (t1 - t0), 0, 1)) * tt)
        rumble *= np.clip(tt / 0.3, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)
        ps = [pan_at(car_at(t0 + x, fam)) for x in np.linspace(0, dur, 20)]
        gs = np.array([away(car_at(t0 + x, fam)) for x in np.linspace(0, dur, 20)])
        sig = np.vstack([rumble, rumble]) * 0.5 * np.interp(np.linspace(0, 1, len(tt)), np.linspace(0, 1, 20), gs)
        M.add('car', travel(sig, ps), t0, 1.0)
        crunch = lowpass_noise(0.8, 2500, lo=400) * np.exp(-np.arange(int(0.8 * SR)) / SR / 0.25)
        M.add('car', np.vstack([crunch, crunch]) * 0.3, t1 - 0.5, 0.9, pan_at(fam['park']))
        for k, td in enumerate(fam['doors']):
            nn = int(0.3 * SR)
            tt = np.arange(nn) / SR
            thud = np.sin(2 * np.pi * (85 - 30 * tt / 0.3) * tt) * np.exp(-tt / 0.07)
            thud += 0.4 * lowpass_noise(0.3, 900) * np.exp(-tt / 0.03)
            M.add('fx', np.vstack([thud, thud]) * 0.5, td, 0.9, pan_at(fam['park']))
            M.add('fx', clave.play(70), td + 0.005, 0.3, pan_at(fam['park']))
        if fam.get('horn') is not None:
            for j in range(2):
                nn = int(0.2 * SR)
                tt = np.arange(nn) / SR
                b = np.sign(np.sin(2 * np.pi * 415 * tt)) + np.sign(np.sin(2 * np.pi * 523 * tt))
                b = b * np.clip(tt / 0.01, 0, 1) * np.clip((0.2 - tt) / 0.02, 0, 1) * 0.12
                M.add('fx', np.vstack([b, b]), fam['horn'] + 0.34 * j, 0.8, 0.95)
        # footsteps: in step on the beat, the kids pattering
        w0, w1 = fam['walk']
        step = 0.15 if fam['name'] == 'cousins' else BEAT
        t = w0
        while t < w1 + 0.01:
            x = walker(t + 0.05, fam, 0)
            M.add('fx', wood.play(int(nrng.uniform(40, 60))), t, 0.35 * away(x), pan_at(x))
            t += step
    t = LAST['walk'][0]
    while t < T_LAST_RING:
        x = walker(t, LAST, 0)
        M.add('fx', wood.play(55), t, 0.35 * away(x), pan_at(x))
        t += 0.14

    # ---- doorbells: B down to G, the kids just the ding over and over; the door: a latch and a creak ----
    for tr, kind in rings():
        M.add('bell', tbell.play(n('B4'), 105), tr, 1.0, door_p)
        M.add('bell', glock.play(n('B5'), 70), tr, 0.5, door_p)
        if kind != 'ding':
            gap = 0.9 if kind == 'slow' else 0.4
            M.add('bell', tbell.play(n('G4'), 100), tr + gap, 1.0, door_p)
            M.add('bell', glock.play(n('G5'), 64), tr + gap, 0.5, door_p)
    M.add('bell', tbell.play(n('D5'), 100), 37.05, 0.8, door_p)          # both families ring at once
    for t_open, cs in opens():
        M.add('fx', clave.play(90), t_open, 0.5, door_p)
        M.add('fx', guiro.play(90, pitch=-5), t_open + 0.05, 0.5, door_p)
        if t_open != T_OPEN_LAST:
            cheer(t_open + 0.3, door_p, 1.2 + 0.4 * len(cs))
            for j in range(8):                                             # the colour rolling out both ways
                sgn = 1 if j % 2 else -1
                M.add('mallet', glock.play(n('G5') + (0, 4, 7, 12)[j % 4], 80), t_open + 0.12 * j, 0.45,
                      pan_at(DOOR + sgn * 1000 * 0.12 * j))
    # ---- hugs: a sparkle where they meet ----
    sparkle = [n('G5'), n('B5'), n('D6'), n('G6')]
    for th, where, size in hugs():
        pw = pan_at(where)
        for j, m in enumerate(sparkle[:2 + int(2 * size)]):
            M.add('mallet', glock.play(m, int(55 + 30 * size)), th + 0.04 * j, 0.5 * size, pw)
        if size >= 1:
            cheer(th, pw, 0.5)

    # ---- the band ----
    # 0-4: waiting; the clock ticks at the door
    for b in range(13):
        M.add('drums', wood.play(100 if b % 2 == 0 else 80), b * 1.0, 1.0 if b < 4 else 0.8 * (1 - b / 13), door_p)
        M.add('drums', wood.play(75), b * 1.0 + 0.5, 0.8 if b < 4 else 0.6 * (1 - b / 13), door_p)
    band(0.0, ['G', 'D'] * 4, 64, tuba_on=False, banjo_on=False)
    tune(2.0, [(0, 0, 'D4', 1), (0, 2, 'D4', 1), (1, 0, 'C4', 1), (1, 2, 'A3', 1)], clar, 'melody', 70)
    # 4-12: A, clarinet; 12-20: A, violins and the tuba
    band(4.0, TUNE_CH, 76, tuba_on=False)
    tune(4.0, TUNE, clar, 'melody', 88)
    band(12.0, TUNE_CH, 84)
    tune(12.0, TUNE, vln, 'melody', 86, short=0.8)
    tune(12.0, TUNE, clar, 'melody', 70, up=-12, gain=0.5)
    # 20-28: B, xylophone and piccolo: the kids
    band(20.0, BRIDGE_CH, 90, snare_on=True)
    tune(20.0, BRIDGE, xylo, 'mallet', 104)
    tune(20.0, BRIDGE, picc, 'melody', 76, gain=0.6)
    # 28-30: a fill as the door opens
    for k in range(8):
        M.add('drums', shit.play(80 + 5 * k), 28.0 + k * E8, 0.6, -0.5 + 0.14 * k)
    band(28.0, ['G', 'G', 'D', 'D7'], 92, snare_on=True)
    # 30-38: the race: A on trombone and trumpet, a snare on every eighth
    band(30.0, TUNE_CH, 96, snare_on=True, drive=True)
    tune(30.0, TUNE, tbn, 'melody', 104, up=-12)
    tune(30.0, TUNE, tpt, 'melody', 96, gain=0.8)
    for k in range(32):
        M.add('drums', snare.play(60 + k), 30.0 + k * E8, 0.4)
    # 38-42: half the bridge, everyone cheering
    band(38.0, BRIDGE_CH[:8], 96, snare_on=True)
    tune(38.0, BRIDGE, clar, 'melody', 96, bars=4)
    tune(38.0, BRIDGE, vln, 'melody', 86, up=-12, short=0.8, bars=4)
    # 42-50: the party: A, everyone
    M.add('drums', crash.play(110), 42.0, 0.6)
    band(42.0, TUNE_CH, 102, snare_on=True, drive=True)
    tune(42.0, TUNE, tpt, 'melody', 102)
    tune(42.0, TUNE, clar, 'melody', 92, gain=0.8)
    tune(42.0, TUNE, xylo, 'mallet', 92, gain=0.7)
    # 50-58: B, trumpet and horn; the conga turns round
    M.add('drums', crash.play(100), 50.0, 0.5)
    M.add('guest', fall.play(n('G3'), 110), 49.6, 0.6)
    band(50.0, BRIDGE_CH, 102, snare_on=True, drive=True)
    tune(50.0, BRIDGE, tpt, 'melody', 104)
    tune(50.0, BRIDGE, horn, 'melody', 92, up=-12, short=0.8)
    # 58-61.5: A again, pounding every beat, cut off by the last cousin
    band(58.0, TUNE_CH[:7], 106, snare_on=True, drive=True)
    tune(58.0, TUNE, tpt, 'melody', 106, bars=4)
    tune(58.0, TUNE, clar, 'melody', 96, bars=4)
    tune(58.0, TUNE, xylo, 'mallet', 96, gain=0.7, bars=4)
    for k in range(7):
        M.add('drums', timp.play(95 + 3 * k), 58.0 + k * BEAT, 0.5)
    # the last cousin: a cymbal choke and a flute sprinting in
    M.add('drums', crash.play(90), T_ARRIVE, 0.4, 0.9)
    for j, m in enumerate(('D5', 'E5', 'F#5', 'G5', 'A5', 'B5', 'C6', 'D6') * 2):
        M.add('guest', flute.play(n(m) - 12, 92), LAST['walk'][0] + j * 0.15, 0.8,
              pan_at(walker(LAST['walk'][0] + j * 0.15, LAST, 0)))
    # the hush: one soft held chord
    for m in (n('C3'), n('G3'), n('E4')):
        M.add('strings', cel.play(m, 50, dur=T_OPEN_LAST - T_ARRIVE - 0.4, release=0.4), T_ARRIVE + 0.3, 0.7)
    for tk in T_TICKS:
        M.add('drums', wood.play(110), tk, 0.9, door_p)
    # the rush: snare roll and strings climbing to the door; a held breath
    M.add('drums', sn_roll.play(90, dur=T_HELD - T_OPEN_LAST - 0.3), T_OPEN_LAST + 0.3, 0.9, door_p)
    climb = ['D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C5', 'C#5', 'D5', 'D#5', 'E5', 'F#5']
    for k, m in enumerate(climb):
        tk = T_OPEN_LAST + 0.3 + k * (T_HELD - T_OPEN_LAST - 0.3) / len(climb)
        M.add('strings', trem.play(n(m) - 12, 64 + 4 * k, dur=0.3, release=0.05), tk, 0.9)
    M.add('bass', tuba.play(n('D2'), 110), T_HELD - 0.5, 0.9)
    # the group hug: a crash, a cheer and the tune for the whole band
    M.add('drums', crash.play(124), T_BOOM, 0.8, door_p)
    M.add('drums', bd.play(124), T_BOOM, 1.0, door_p)
    M.add('drums', timp.play(120), T_BOOM, 0.8)
    cheer(T_BOOM, door_p, 2.5)
    cheer(T_BOOM + 0.25, -0.5, 1.5)
    cheer(T_BOOM + 0.35, 0.5, 1.5)
    for j in range(12):
        sgn = 1 if j % 2 else -1
        M.add('mallet', glock.play(sparkle[j % 4], 84), T_BOOM + 0.1 * j, 0.5, pan_at(DOOR + sgn * 1100 * 0.1 * j))
    t0 = T_BOOM
    band(t0, TUNE_CH, 106, snare_on=True, drive=True)
    tune(t0, TUNE, tpt, 'melody', 104)
    tune(t0, TUNE, clar, 'melody', 96, gain=0.8)
    tune(t0, TUNE, vln, 'melody', 88, up=-12, short=0.8)
    tune(t0, TUNE, xylo, 'mallet', 94, gain=0.7)
    t0 = 80.0
    M.add('drums', crash.play(110), t0, 0.6, -0.6)
    band(t0, BRIDGE_CH[8:], 106, snare_on=True, drive=True)
    tune(t0, [(b - 4, e, m, ln) for b, e, m, ln in BRIDGE if b >= 4], tpt, 'melody', 104)
    tune(t0, [(b - 4, e, m, ln) for b, e, m, ln in BRIDGE if b >= 4], clar, 'melody', 94, gain=0.8)
    t1 = 84.0
    M.add('drums', crash.play(110), t1, 0.6, 0.6)
    for k, c in enumerate(['C', 'D7', 'G', 'G']):
        M.add('bass', tuba.play(ROOTS[c][0], 108), t1 + k * 0.5, 1.0)
        M.add('drums', bd.play(110), t1 + k * 0.5, 0.8)
        for m in CH[c]:
            M.add('band', pizz.play(m + 12, 96), t1 + k * 0.5, 0.6)
            M.add('melody', tpt.play(m + 12, 98, dur=0.2), t1 + k * 0.5, 0.5)
    tf = 86.0
    for m, inst, v in ((n('G2'), cel, 92), (n('D3'), cel, 88), (n('G3'), horn, 92), (n('B3'), horn, 88),
                       (n('D4'), vln, 88), (n('G4'), clar_l, 92)):
        M.add('melody' if inst in (vln, clar_l) else 'strings', inst.play(m, v, dur=D - tf - 0.8, release=1.0), tf, 0.8)
    M.add('drums', crash.play(110), tf, 0.7)
    M.add('drums', timp.play(115), tf, 0.8)
    M.add('bass', tuba.play(n('G1'), 112), tf, 1.0)
    cheer(tf + 0.1, 0.0, 2.0)
    for k, m in enumerate(('G2', 'B2', 'D3', 'G3', 'B3', 'D4', 'G4')):
        M.add('band', banjo.play(n(m) + 12, 92), tf + 0.04 * k, 0.6)

    # ---- each family's instrument as its car pulls up ----
    def stinger(fam, t):
        p = pan_at(fam['park'])
        name = fam['name']
        if name == 'grandparents':
            tune(t, [(0, 0, 'G2', 1), (0, 1, 'B2', 1), (0, 2, 'D3', 1), (0, 3, 'G3', 2)], bsn, 'guest', 104, pan=p)
        elif name == 'aunt':
            tune(t, [(0, 0, 'B4', 1), (0, 1, 'C5', 1), (0, 2, 'D5', 2), (1, 0, 'G4', 2)], oboe, 'guest', 100, pan=p)
        elif name == 'cousins':
            for j in range(8):
                M.add('guest', picc.play(n('D5') + (0, 4, 7, 12)[j % 4], 94), t + j * 0.09, 0.7, p)
        elif name == 'uncle':
            M.add('guest', fall.play(n('D3'), 112), t, 0.9, p)
            tune(t + 0.6, [(0, 0, 'G2', 1), (0, 2, 'G3', 1)], tbn, 'guest', 112, pan=p)
        else:
            tune(t, [(0, 0, 'D4', 1), (0, 1, 'D4', 0.5), (0, 1.5, 'D4', 0.5), (0, 2, 'G4', 2), (1, 0, 'B4', 2)], tpt,
                 'guest', 106, pan=p)

    for fam in FAMILIES:
        stinger(fam, fam['car'][1] - 0.4)
