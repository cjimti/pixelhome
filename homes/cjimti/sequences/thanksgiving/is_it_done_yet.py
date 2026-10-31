"""Is It Done Yet?: The porch is the oven (Porch Front its window, the porch sides its walls), the Right wing is the
kitchen timer and Left, with Side behind it, is where the hungry family waits. Flames run in from the porch's
front corners and the oven roars with heat stripes rolling out of the window, faster and hotter as it heats; the
timer bar ratchets out to the free end of Right and ticks, its cells swapping on every beat; the family's
impatience runs along Left toward the oven in pulses that quicken.

Someone keeps checking: a little conga of cranberry runs from Left up to the door, the door flies open (a blast of
light on the window) and heat rolls out in waves along both porch sides and down both wings, blowing the asker
back, dropping the oven back to red and ratcheting the timer back out. The peeks come faster: two at once (one
sneaking along the timer from the free end), then the whole family in a rush. The cook rises out of the oven in
gold and paces guard in front of it, and the next askers get swatted: a burst where they meet and the asker flies
back out the end of the house, left, then right, then both at once. The timer runs out: DING! The family leaps,
the cook opens the door, and... not yet. Everything droops and the timer winds back. Then the longest wait: the oven
roaring, the cook pacing faster, the family creeping in, the last eight ticks counted on the whole house. DING,
DING, DING: three gold rings roll out of the timer across the whole house, the turkey comes out golden and steaming,
and the house feasts in gold to a last full chord."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, colormap, nframes

CODE = 'TG02'
TITLE = 'Is It Done Yet?'
KIND = 'show'
DESCRIPTION = ('The porch is the oven and the Right wing is the timer. The family keeps opening the door, heat pours '
               'out, the cook stands guard and swats them away, a false ding, then the real one.')
VOICEOVER = "The bird's been in for hours, and somebody just can't stop checking."

GOLD = hexc('#ffaa00')
AMBER = hexc('#ff7a10')
CRANBERRY = hexc('#d0102a')
WARM = hexc('#ffd0a0')
WHITE = hexc('#fff2e0')
BROWN = hexc('#7a3008')
RED = hexc('#ff1800')

D = 90.0
BEAT, BAR = 0.5, 2.0
DOOR_L, DOOR_R = 1311.0, 1660.0         # the oven window, Porch Front
OVEN = 1486.0
P0, P1 = 893.0, 2033.0                  # the porch's front corners
R0, R1 = 2033.0, 2512.0                 # the timer on Right
L0 = 490.0                              # where Left starts (Side behind it)
heat_map = colormap([(0.0, (0.02, 0.0, 0.0)), (0.2, (0.08, 0.0, 0.0)), (0.4, (0.3, 0.01, 0.0)),
                     (0.6, (0.75, 0.05, 0.0)), (0.8, (1.0, 0.2, 0.0)), (0.95, (1.0, 0.4, 0.04)), (1.05, (1.0, 0.6, 0.15))])

T_IGNITE, T_WIND, T_FAMILY = 1.0, 4.0, 5.0
# peeks: (start, arrive at the door, from which side, how many, timer gained)
PEEKS = [(12.0, 14.0, 'L', 1, 0.12), (20.0, 21.5, 'L', 1, 0.14), (26.0, 27.0, 'L', 1, 0.16),
         (31.0, 32.0, 'LR', 1, 0.25), (36.0, 37.0, 'L', 3, 0.3)]
T_COOK = 38.0
SWATS = [(44.0, 44.75, 'L'), (48.0, 48.75, 'R'), (52.0, 52.75, 'L'), (52.0, 53.25, 'R')]
MEET = {'L': 1100.0, 'R': 1850.0}
T_FALSE, T_NOTYET, T_REWIND = 58.0, 59.0, (59.5, 60.5)
T_COUNT, T_DING = 70.0, 74.0
T_FEAST, T_FINAL = 76.0, 86.0


def timer():
    """Remaining fraction of the timer per frame: wound up, draining, ratcheting back at each peek in four steps,
    running out at the false ding, wound back a third, and out again at the real one."""
    F = nframes(D)
    ts = np.arange(F) * DT
    gain_t = sum(1.0 for _ in PEEKS)
    total = 1 + sum(p[4] for p in PEEKS)
    c = total / (T_FALSE - 6.0 - gain_t)
    rem = np.zeros(F)
    r, cur, base = 0.0, None, 0.0
    for f, t in enumerate(ts):
        if T_WIND <= t < 6.0:
            r = np.floor(8 * smoothstep(T_WIND, 6.0, t)) / 8
        elif 6.0 <= t < T_FALSE:
            g = [p for p in PEEKS if p[1] <= t < p[1] + 1.0]
            if g:
                if cur is not g[0]:
                    cur, base = g[0], r
                r = base + g[0][4] * np.ceil(4 * (t - g[0][1]) / 1.0) / 4
            else:
                cur = None
                r -= c * DT
        elif T_FALSE <= t < T_REWIND[0]:
            r = 0.0
        elif T_REWIND[0] <= t < T_REWIND[1]:
            r = 0.35 * np.ceil(6 * (t - T_REWIND[0]) / (T_REWIND[1] - T_REWIND[0])) / 6
        elif T_REWIND[1] <= t < T_DING:
            r = 0.35 * (T_DING - t) / (T_DING - T_REWIND[1])
        else:
            r = 0.0
        rem[f] = max(r, 0.0)
    return rem



def oven():
    """Oven temperature per frame: it heats with a lag, drops at every peek (hardest at the family rush), and roars
    at full heat once the cook is guarding it."""
    F = nframes(D)
    T = np.zeros(F)
    v = 0.0
    for f in range(F):
        t = f * DT
        target = smoothstep(T_IGNITE, T_IGNITE + 2, t)
        for _, ta, side, k, _ in PEEKS:
            if ta <= t < ta + 0.4:
                target = 0.0 if k > 1 else 0.1
        rate = 0.22 + (4.0 if any(ta <= t < ta + 0.4 for _, ta, *_ in PEEKS) else 0) + 0.25 * (t > T_COOK)
        v += (target - v) * rate * DT
        T[f] = v
    return T


def cook_x(t):
    """Where the cook stands: pacing in front of the oven, faster as it gets late, dashing out to each swat."""
    pts = [(T_COOK, OVEN)]
    tt, s = T_COOK + 1.0, 1
    while tt < T_DING:
        period = BAR if tt < 54 else (BAR / 2 if tt < 66 else BEAT)
        pts.append((tt, OVEN + s * (110 if tt < 66 else 70)))
        s, tt = -s, tt + period / 2
    for ts, tm, side in SWATS:
        pts = [p for p in pts if not (tm - 0.45 <= p[0] <= tm + 1.25)]
    for ts, tm, side in SWATS:
        if (ts, tm, side) == SWATS[3]:
            continue
        pts += [(tm - 0.4, OVEN), (tm, MEET[side]), (tm + 0.6, MEET[side])]
        if (ts, tm, side) == SWATS[2]:
            pts += [(SWATS[3][1], MEET['R']), (SWATS[3][1] + 0.6, MEET['R'])]
        pts.append((pts[-1][0] + 0.6, OVEN))
    return keys(t, sorted(pts))


def conga(pdp, head, dirn, k=1):
    """k little cranberry bars behind a head, moving in direction dirn: a group, not a dot."""
    out = np.zeros_like(pdp)
    for j in range(3 * k):
        p = head - dirn * 42 * j
        out += np.clip((13 - np.abs(pdp - p)) / 4, 0, 1)
    return out


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    PF = (pdp >= DOOR_L) & (pdp <= DOOR_R)
    PW = ((pdp >= P0) & (pdp < DOOR_L)) | ((pdp > DOOR_R) & (pdp <= P1))
    PORCH = PF | PW
    LW = (pdp >= L0) & (pdp < P0)
    SIDE = pdp < L0
    RW = pdp > R0
    away = np.abs(pdp - OVEN)                       # distance out of the oven along the path
    flick = Flicker(rng, n, 1.5, 5.0)
    shimmer = Flicker(rng, n, 0.4, 1.4)
    rem = timer()
    T = oven()
    hunger = np.array([keys(f * DT, [(0, 0), (T_FAMILY, 0.2), (36, 0.6), (T_FALSE, 0.7), (T_COUNT, 0.85),
                                     (T_DING, 1.0)]) for f in range(F)])
    ph_fam = np.cumsum(2 * np.pi * (1.0 + 4.0 * hunger) * DT)     # pulses per second along Left
    ph_oven = np.cumsum(2 * np.pi * (0.5 + 1.5 * T) * DT)
    blasts = [(ta, k * (2 if side == 'LR' else 1)) for _, ta, side, k, _ in PEEKS]

    for f in range(F):
        t = f * DT
        buf = light(BROWN, keys(t, [(0, 0), (1, 0.06), (87, 0.06), (90, 0)]) * np.ones(n))
        Tf = T[f]
        done = smoothstep(T_DING + 0.8, T_DING + 2.0, t)
        notyet = smoothstep(T_NOTYET, T_NOTYET + 0.3, t) * (1 - smoothstep(T_REWIND[1], T_REWIND[1] + 1.5, t))

        # ---------------- the oven ----------------
        lit = np.clip((900 * (t - T_IGNITE) - (np.where(pdp < OVEN, pdp - P0, P1 - pdp))) / 40, 0, 1) * PORCH
        roll = (0.5 + 0.5 * np.cos(2 * np.pi * away / 200 - ph_oven[f])) ** 3      # heat stripes rolling outward
        h = (0.2 + 0.85 * Tf) * (0.55 + 0.5 * roll + 0.05 * flick(t)) * np.where(PF, 0.95, 0.75 - 0.2 * np.clip((away - 175) / 400, 0, 1))
        h = h * (1 - 0.35 * notyet)
        ovenc = heat_map(np.clip(h, 0, 1.05))
        beat = np.exp(-((t + 1e-6) % BEAT) / 0.12)
        golden = light(BROWN, 0.5 + 0.15 * roll) + light(GOLD, (0.55 + 0.3 * roll) * PF + 0.3 * roll * PW)
        buf += (ovenc * (1 - done) + golden * done) * lit[:, None] * (1 + 0.25 * beat * (t > 6))
        if t < T_IGNITE + 1.2:                      # the flame fronts running in from the corners
            fr = 900 * (t - T_IGNITE)
            front = np.exp(-((np.where(pdp < OVEN, pdp - P0, P1 - pdp) - fr) / 18) ** 2) * PORCH
            buf += light(AMBER, front * (t >= T_IGNITE))

        # ---------------- the timer ----------------
        r = rem[f]
        if T_WIND <= t < T_DING + 0.3:
            tip = R0 + r * (R1 - R0)
            bar = np.clip((tip - pdp) / 5 + 0.5, 0, 1) * RW
            k = int((t + 1e-6) / BEAT)
            cell = (np.floor((pdp - R0) / 40) + k) % 2
            tick = 0.5 + 0.5 * beat
            late = smoothstep(T_COUNT - 4, T_DING, t)
            buf += light(GOLD, bar * (0.22 + 0.35 * cell * tick + 0.15 * late * beat))
            buf += light(WARM, 0.9 * beat * np.exp(-((pdp - tip) / 8) ** 2) * RW)
            gained = rem[f] - rem[max(0, f - 20)]
            if gained > 0.01:                       # wound back: the new stretch flashes red
                fresh = (pdp > R0 + rem[max(0, f - 20)] * (R1 - R0)) & (pdp < tip)
                buf += light(RED, 0.8 * fresh)

        # ---------------- the family ----------------
        fam = smoothstep(T_FAMILY, T_FAMILY + 1.5, t)
        pops = np.clip((np.floor((pdp - L0) / 50) * 0.12 + T_FAMILY - t) * -8, 0, 1)    # heads pop up one by one
        pulse = (0.5 + 0.5 * np.cos(2 * np.pi * (pdp - L0) / 100 - ph_fam[f])) ** 4    # running toward the oven
        hg = hunger[f]
        creep = smoothstep(T_COUNT - 4, T_DING, t)
        fam_I = (0.18 + 0.12 * hg + (0.25 + 0.5 * hg) * pulse) * pops * (1 - 0.5 * notyet)
        buf += light(CRANBERRY, fam_I * LW * (1 - done))
        buf += light(CRANBERRY, (0.1 + 0.12 * (0.5 + 0.5 * np.cos(pdp / 60 - 1.5 * t))) * SIDE * fam * (1 - done))
        if creep > 0:                               # the family creeps in along the porch wall
            reach = P0 + 300 * creep
            buf += light(CRANBERRY, 0.45 * pulse * ((pdp >= P0) & (pdp < reach)) * (1 - done))

        # ---------------- peeks: run to the door, the blast, blown back ----------------
        for t0, ta, side, k, g in PEEKS:
            if not t0 <= t < ta + 3.5:
                continue
            for sd in (['L', 'R'] if side == 'LR' else [side]):
                start, door, dirn = (700.0, DOOR_L, 1) if sd == 'L' else (R1, DOOR_R, -1)
                if t < ta:
                    head = start + (door - start) * (t - t0) / (ta - t0)
                else:
                    v = np.clip((t - ta - 0.3) / 1.2, 0, 1)
                    end = 520.0 if sd == 'L' else R1 + 40
                    head = door + (end - door) * (1 - (1 - v) ** 2)
                fade = 1 - smoothstep(ta + 1.8, ta + 2.4, t)
                buf += light(CRANBERRY, 0.95 * fade * conga(pdp, head, dirn if t < ta else -dirn, k))
        for ta, size in blasts:
            u = t - ta
            if 0 <= u < 3.0:
                buf += light(WHITE, (0.9 + 0.1 * size) * np.exp(-u / 0.3) * PF + 0.5 * np.exp(-u / 0.2) * PW)
                for w in range(2 + min(size, 3)):      # waves of heat roll out along the porch and down the wings
                    uw = u - 0.22 * w
                    if uw > 0:
                        front = 175 + 950 * uw
                        a = np.exp(-uw / (0.7 + 0.15 * size))
                        buf += light(WARM, a * np.exp(-((away - front) / 60) ** 2) * ~PF)

        # ---------------- the cook ----------------
        if t >= T_COOK:
            rise = smoothstep(T_COOK, T_COOK + 1.0, t)
            fade = 1 - smoothstep(T_DING + 1.5, T_DING + 2.5, t)
            if t < T_COOK + 1.2:                    # rises out of the oven: gold spreading across the window
                buf += light(GOLD, 0.8 * np.clip((350 * rise - np.abs(pdp - OVEN)) / 30, 0, 1) * PF
                             * np.exp(-max(0, t - T_COOK - 0.6) / 0.3))
            cx = cook_x(t)
            body = np.clip((32 - np.abs(pdp - cx)) / 6, 0, 1)
            buf += light(GOLD, (0.95 + 0.1 * beat) * body * rise * fade)
            buf += light(WARM, 0.35 * np.exp(-((pdp - cx) / 70) ** 2) * rise * fade)

        # ---------------- swats ----------------
        for ts, tm, side in SWATS:
            if not ts <= t < tm + 2.0:
                continue
            start, end, dirn = (600.0, 0.0, 1) if side == 'L' else (R1, R1 + 60, -1)
            meet = MEET[side]
            if t < tm:
                head = start + (meet - start) * (t - ts) / (tm - ts)
                d_ = dirn
            else:
                v = np.clip((t - tm) / 1.0, 0, 1)
                head = meet + (end - meet) * (1 - (1 - v) ** 2)
                d_ = -dirn
            fade = 1 - smoothstep(tm + 1.1, tm + 1.6, t)
            buf += light(CRANBERRY, 0.95 * fade * conga(pdp, head, d_))
            u = t - tm
            if u >= 0:
                buf += light(WHITE, np.exp(-u / 0.12) * np.exp(-((pdp - meet) / 50) ** 2))
                ring = np.exp(-((np.abs(pdp - meet) - 800 * u) / 30) ** 2) * np.exp(-u / 0.35)
                buf += light(GOLD, 0.8 * ring)
                if side == 'L' and 1.0 <= u < 1.6:  # lands at the back of Side
                    buf += light(WARM, 0.8 * np.exp(-(u - 1.0) / 0.2) * np.exp(-(pdp / 60) ** 2))

        # ---------------- the false ding, and not yet ----------------
        u = t - T_FALSE
        if 0 <= u < 1.0:
            ring = np.exp(-((np.abs(pdp - R0) - 1000 * u) / 40) ** 2) * np.exp(-u / 0.5)
            buf += light(GOLD, 0.9 * ring)
            buf += light(GOLD, 0.5 * np.exp(-u / 0.4) * LW)
            buf += light(WHITE, 0.8 * smoothstep(0.4, 0.55, u) * np.exp(-max(0, u - 0.55) / 0.3) * PF)
        if notyet > 0:                              # everything droops to red
            buf += light(RED, 0.35 * notyet * (1 - smoothstep(T_NOTYET, T_NOTYET + 1.5, t)) * PORCH)

        # ---------------- the last eight ticks, counted on the whole house ----------------
        if T_COUNT <= t < T_DING:
            k = int((t - T_COUNT) / BEAT)
            u = t - T_COUNT - k * BEAT
            reach = 300 + 280 * k
            w = np.clip((reach - np.abs(pdp - R0)) / 60, 0, 1)
            buf += light(GOLD, (0.25 + 0.06 * k) * np.exp(-u / 0.18) * w)

        # ---------------- DING DING DING, and the feast ----------------
        u = t - T_DING
        if u >= 0:
            for k in range(3):
                uk = u - BEAT * k
                if uk >= 0:
                    ring = np.exp(-((np.abs(pdp - R0) - 1100 * uk) / 50) ** 2) * np.exp(-uk / 1.2)
                    buf += light(GOLD, ring) + light(WARM, 0.9 * np.exp(-uk / 0.12) * RW)
            buf += light(WHITE, 0.8 * smoothstep(1.2, 1.4, u) * np.exp(-max(0, u - 1.4) / 0.35) * PF)
            fade = keys(t, [(T_DING, 1), (87, 1), (90, 0)])
            spread = np.clip((900 * (u - 1.5) - away) / 250, 0, 1)
            glow = (0.3 + 0.1 * shimmer(t)) * spread
            if t >= T_FEAST:
                v = t - T_FEAST
                bt = np.exp(-((t + 1e-6) % BEAT) / 0.12)
                if t < 80:                          # gold stripes run out of the oven, one a beat
                    st = (0.5 + 0.5 * np.cos(2 * np.pi * (away / 180 - v / BEAT))) ** 3
                    buf += light(GOLD, (0.55 + 0.25 * bt) * st * spread)
                elif t < 84:                        # the family's cranberry runs in, gold runs out
                    st_in = (0.5 + 0.5 * np.cos(2 * np.pi * (away / 150 + v / BEAT))) ** 3
                    st_out = (0.5 + 0.5 * np.cos(2 * np.pi * (away / 150 - v / BEAT))) ** 3
                    buf += light(CRANBERRY, 0.6 * st_in * (pdp < OVEN)) + light(GOLD, 0.6 * st_out * (pdp >= OVEN))
                    buf += light(AMBER, 0.4 * bt * PF)
                elif t < T_FINAL:                   # everybody claps on the beat
                    buf += light(GOLD, (0.25 + 0.5 * bt) * spread)
                else:
                    w2 = t - T_FINAL
                    buf += light(WARM, 0.85 * np.exp(-w2 / 0.4))
                    buf += light(GOLD, 0.45 * np.exp(-w2 / 2.2))
            buf += light(GOLD, glow * fade)
            for k in range(8):                      # steam off the bird, drifting across the window
                uk = u - 2.0 - 1.1 * k
                if 0 < uk < 3:
                    p = OVEN + (-1) ** k * (40 + 25 * k) + 30 * np.sin(uk * 2.5 + k)
                    buf += light(WHITE, 0.55 * np.sin(np.pi * uk / 3) * np.exp(-((pdp - p) / 16) ** 2) * PF * fade)
        out[f][G.path] = buf
    return np.clip(out, 0, 1, out=out)


# ---------------------------------------------------------------- music ----------------------------------------------
# A kitchen rag in F at 120 to the minute, on the timer's own tick: a woodblock tick-tock under everything, stride
# piano and tuba oom-pah, the waiting tune on clarinet, then flute. Each peek tiptoes up on bassoon (or clarinet from
# the right), the door creaks, heat blasts out in a cymbal and whooshes down both sides, the ratchet winds the timer
# back and a slide whistle blows the asker home; the family rush is a stampede on snare and tuba. The cook arrives
# on a trumpet call and marches his tune on horn; every swat is a slapstick and a crash with a slide whistle out to
# the end of the house. The false ding cheers for one bar and falls flat on a sad trombone. The last wait climbs on
# tremolo strings and timpani, the last eight ticks rise on marimba, and the real ding brings in the whole band.

PROG = ['F', 'Bb', 'C7', 'F', 'Dm', 'Gm', 'C7', 'F']
CHORD = {'F': ('A3', 'C4', 'F4'), 'Bb': ('Bb3', 'D4', 'F4'), 'C7': ('Bb3', 'C4', 'E4'), 'Dm': ('A3', 'D4', 'F4'),
         'Gm': ('Bb3', 'D4', 'G4')}
ROOT = {'F': ('F2', 'C2'), 'Bb': ('Bb1', 'F2'), 'C7': ('C2', 'G2'), 'Dm': ('D2', 'A2'), 'Gm': ('G2', 'D2')}
TUNE = [
    (0, 'C5', 1.5), (1.5, 'A4', 0.5), (2, 'F4', 1), (3, 'A4', 1),
    (4, 'Bb4', 1.5), (5.5, 'D5', 0.5), (6, 'F5', 1), (7, 'D5', 1),
    (8, 'C5', 1), (9, 'E4', 0.5), (9.5, 'G4', 0.5), (10, 'Bb4', 1), (11, 'G4', 1),
    (12, 'A4', 1.5), (13.5, 'G4', 0.5), (14, 'F4', 2),
    (16, 'D5', 1.5), (17.5, 'C5', 0.5), (18, 'A4', 1), (19, 'F4', 1),
    (20, 'G4', 1.5), (21.5, 'A4', 0.5), (22, 'Bb4', 1), (23, 'D5', 1),
    (24, 'C5', 1), (25, 'Bb4', 0.5), (25.5, 'A4', 0.5), (26, 'G4', 1), (27, 'E4', 1),
    (28, 'F4', 3)]
UP = ['F3', 'G3', 'A3', 'Bb3', 'C4', 'D4', 'E4', 'F4']


def score(M, G):
    from pixelhome.audio import note, slide, whoosh
    n = note
    piano = M.sampler('Keys/Upright Nr1/UR1_*_mf_*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clar_s = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    banjo = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    marim = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    guiro = M.hits('Percussion/Guiro-Slow*.wav')
    thud = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_m*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    snare = M.hits('Percussion/Snare2-HitSN*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN*.wav')
    cym = M.hits('Percussion/susCymb1-hit_f_rr*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*_v3_*.wav')
    tri = M.hits('VSCO 1 Percussion/varMetal/triangle/1/triangle1_hit_mp*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')

    for name, gain, rev in (('keys', 0.4, 0.15), ('bass', 0.55, 0.08), ('tune', 0.5, 0.22), ('tick', 1.2, 0.06),
                            ('walk', 0.5, 0.12), ('perc', 0.6, 0.12), ('fx', 0.3, 0.25), ('brass', 0.45, 0.2),
                            ('strings', 0.35, 0.3), ('bell', 0.45, 0.3), ('drums', 0.55, 0.15)):
        M.bus(name, gain=0.5 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    rem = timer()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def travel(sig, d0, d1):
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    def tip(t):
        return pan_at(R0 + rem[min(len(rem) - 1, int(round(t / DT)))] * (R1 - R0))

    oven_p, fam_p, sides = pan_at(OVEN), pan_at(700), (pan_at(1100), pan_at(1850))

    def band(t0, t1, vel=84, chords=PROG, gaps=()):
        k = 0
        while t0 + k * BEAT < t1 - 1e-6:
            t = t0 + k * BEAT
            if not any(a <= t < b for a, b in gaps):
                c = chords[int(k // 4) % len(chords)]
                if k % 2 == 0:
                    M.add('bass', tuba.play(n(ROOT[c][(k // 2) % 2]), vel + 8), t, 1.0, -0.1)
                else:
                    for m in CHORD[c]:
                        M.add('keys', piano.play(n(m), vel), t, 0.6, 0.1)
            k += 1

    def tune(t0, inst, bus, vel, shift=0, gain=1.0, pan=-0.05, upto=32):
        for b, m, d in TUNE:
            if b < upto:
                M.add(bus, inst.play(n(m) + shift, vel, dur=d * BEAT * 0.92, release=0.15), t0 + b * BEAT, gain, pan)

    # ---- the oven lights, the timer winds, the family pops up ----
    for j, m in enumerate(('C4', 'F4', 'A4', 'C5', 'F5')):
        M.add('bell', harp.play(n(m), 70), 0.3 + 0.09 * j, 0.7, oven_p)
    M.add('fx', travel(whoosh(1.2, 200, 1800, 0.6, seed=1), P0, DOOR_L), T_IGNITE, 0.8)
    M.add('fx', travel(whoosh(1.2, 200, 1800, 0.6, seed=2), P1, DOOR_R), T_IGNITE, 0.8)
    M.add('drums', troll.play(70, dur=2.0), T_IGNITE + 0.6, 0.5, oven_p)
    for i in range(8):
        t = T_WIND + i * 0.25
        M.add('perc', ratchet.play(90, dur=0.2), t, 0.6, pan_at(R0 + (R1 - R0) * (i + 1) / 8))
        M.add('walk', marim.play(n(['F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5'][i]), 80 + 4 * i), t, 0.8,
              pan_at(R0 + (R1 - R0) * (i + 1) / 8))
    M.add('bell', tri.play(100), 6.0, 0.8, pan_at(R1))
    for i in range(8):
        M.add('walk', banjo.play(n(UP[i]) + 12, 80), T_FAMILY + 0.12 * i, 0.8, pan_at(L0 + 50 * i))

    # ---- the ticking clock, every beat until the ding (stopped dead by the false ding's droop) ----
    k = 0
    while 6.0 + k * BEAT < T_DING:
        t = 6.0 + k * BEAT
        if not (T_FALSE <= t < T_REWIND[1]):
            late = smoothstep(T_COUNT - 4, T_DING, t)
            M.add('tick', wood.play(int(92 + 30 * late) if k % 2 == 0 else int(74 + 30 * late),
                                    pitch=0 if k % 2 == 0 else -4), t, 1.0, tip(t))
        k += 1

    # ---- the waiting band: clarinet then flute over the peeks; the cook's march on horn ----
    band(6.0, T_COOK, gaps=[(p[1], p[1] + 1.0) for p in PEEKS])
    tune(6.0, clar, 'tune', 96)
    tune(22.0, flute, 'tune', 92)
    for t in np.arange(22.5, T_COOK, BAR / 2):
        M.add('drums', tamb.play(70), t, 0.4, 0.3)
    band(40.0, T_FALSE, vel=92)
    tune(40.0, horn, 'brass', 104, shift=-12)
    tune(40.0, clar_s, 'tune', 90)
    for t in np.arange(40.0, T_FALSE, BEAT):
        M.add('drums', snare.play(70 if (t / BEAT) % 2 else 50), t, 0.5)
    band(56.0, T_FALSE, vel=96, chords=['Bb', 'C7'])

    # ---- the peeks ----
    for i, (t0, ta, side, k, g) in enumerate(PEEKS):
        for sd in (['L', 'R'] if side == 'LR' else [side]):
            start, door = (700.0, DOOR_L) if sd == 'L' else (R1, DOOR_R)
            steps = int(round((ta - t0) / (BEAT / 2)))
            for j in range(steps):
                t = t0 + j * BEAT / 2
                x = start + (door - start) * j / steps
                inst = bsn if sd == 'L' else clar_s
                M.add('walk', inst.play(n(UP[j % 8]) + (12 if sd == 'R' else 0), 86 + 3 * j, dur=0.15), t,
                      1.0 + 0.4 * (k > 1), pan_at(x))
            M.add('fx', travel(slide(0.0, 1.2, 1300, 400, 1.3, 0.45), door, 520 if sd == 'L' else R1), ta + 0.3, 1.0)
            M.add('perc', thud.play(110), ta + 1.5, 0.8, pan_at(520 if sd == 'L' else R1))
        if k > 1:                            # the family rush: a stampede
            M.add('drums', sroll.play(100, dur=ta - t0), t0, 0.8, fam_p)
            for j in range(int((ta - t0) / (BEAT / 2))):
                M.add('bass', tuba.play(n('C2') + j, 100), t0 + j * BEAT / 2, 0.9, fam_p)
        M.add('perc', guiro.play(80, dur=0.4), ta - 0.35, 0.6, oven_p)
        size = k * (2 if side == 'LR' else 1)
        M.add('drums', (crash if size > 1 else cym).play(100 + 8 * min(size, 3)), ta, 0.7, oven_p)
        M.add('drums', bd.play(115), ta, 0.8, oven_p)
        for j, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
            M.add('bell', harp.play(n(m), 92), ta + 0.04 * j, 0.6, oven_p)
        for sd, p in enumerate(sides):
            M.add('fx', whoosh(1.8, 140, 1400, 0.7, seed=10 * i + sd), ta, 1.0, p)
        M.add('perc', ratchet.play(95, dur=1.0), ta, 0.7, tip(ta + 1.0))

    # ---- the cook: a trumpet call as he rises, and the swats ----
    for j, m in enumerate(('C5', 'C5', 'C5', 'F5')):
        M.add('brass', tpt.play(n(m), 110, dur=0.15 if j < 3 else 0.6), T_COOK + 0.25 * j + (0.25 if j == 3 else 0),
              1.0, oven_p)
    M.add('drums', timp.play(110), T_COOK + 1.0, 0.7, oven_p)
    M.add('drums', crash.play(100), T_COOK + 1.0, 0.5, oven_p)
    for ts, tm, side in SWATS:
        start = 600.0 if side == 'L' else R1
        meet = MEET[side]
        for j in range(3):
            M.add('walk', (bsn if side == 'L' else clar_s).play(n(UP[2 * j + 2]) + (12 if side == 'R' else 0), 96,
                                                               dur=0.12), ts + j * (tm - ts) / 3, 1.0,
                  pan_at(start + (meet - start) * j / 3))
        M.add('brass', tpt.play(n('F5'), 115, dur=0.2), tm - 0.4, 0.9, pan_at(meet))
        M.add('perc', slap.play(127), tm, 1.0, pan_at(meet))
        M.add('drums', crash.play(105), tm, 0.6, pan_at(meet))
        M.add('drums', timp.play(110), tm, 0.6, pan_at(meet))
        end = 0.0 if side == 'L' else R1
        M.add('fx', travel(slide(0.0, 0.9, 1500, 380, 1.0, 0.45), meet, end), tm + 0.05, 1.1)
        M.add('brass', fall.play(n('Bb3'), 100), tm + 1.0, 0.6, pan_at(end))

    # ---- the false ding: a bar of cheering, then not yet ----
    M.add('bell', glock.play(n('A5'), 124), T_FALSE, 1.4, pan_at(R0))
    M.add('bell', tri.play(110), T_FALSE, 0.8, pan_at(R0))
    for m in ('F3', 'A3', 'C4', 'F4'):
        M.add('brass', tpt.play(n(m) + 12, 110, dur=0.3), T_FALSE + 0.5, 0.6)
        M.add('keys', piano.play(n(m), 100), T_FALSE + 0.5, 0.6)
    M.add('perc', guiro.play(90, dur=0.4), T_FALSE + 0.6, 0.6, oven_p)
    for j, m in enumerate(('Bb3', 'A3', 'Ab3')):
        M.add('brass', tbn.play(n(m), 100, dur=0.45, release=0.1), T_NOTYET + 0.5 * j, 0.9)
    M.add('brass', fall.play(n('G3'), 110), T_NOTYET + 1.5, 0.9)
    M.add('perc', ratchet.play(100, dur=1.0), T_REWIND[0], 0.8, pan_at(R0 + 0.2 * (R1 - R0)))

    # ---- the last wait: tremolo climbing, timpani heartbeat, the piano hanging on C7; eight ticks ----
    band(T_REWIND[1] + 0.5, T_COUNT, vel=80, chords=['F', 'Dm', 'Bb', 'C7'])
    tune(62.0, clar_s, 'tune', 84, upto=16)            # the waiting tune again, nervously, under the tremolo
    for j, t in enumerate(np.arange(62.0, T_DING, BAR)):
        M.add('strings', trem.play(n('C4') + j, 60 + 6 * j, dur=BAR, release=0.05), t, 1.0, oven_p)
        M.add('strings', trem.play(n('E4') + j, 56 + 6 * j, dur=BAR, release=0.05), t, 0.8, oven_p)
    for t in np.arange(62.0, T_DING, BEAT * 2):
        M.add('drums', timp.play(80 + int(2 * (t - 62)), pitch=-5), t, 0.6, oven_p)
    for k in range(8):
        t = T_COUNT + k * BEAT
        M.add('walk', marim.play(n(UP[k]) + 12, 100 + 3 * k), t, 1.0, pan_at(R0))
        for m in CHORD['C7']:
            M.add('keys', piano.play(n(m), 80 + 4 * k), t, 0.6, 0.1)
        M.add('bass', pizz.play(n('C2'), 100), t, 1.0, -0.1)
        M.add('drums', snare.play(80 + 5 * k), t, 0.6)

    # ---- DING DING DING, and the feast ----
    for k in range(3):
        M.add('bell', glock.play(n('A5'), 124 - 6 * k), T_DING + BEAT * k, 1.6, pan_at(R0))
        M.add('bell', tri.play(110), T_DING + BEAT * k, 0.8, pan_at(R0))
    M.add('drums', troll.play(95, dur=1.2), T_DING + 0.2, 0.6, oven_p)
    M.add('drums', crash.play(118), T_DING + 1.5, 0.8)
    M.add('drums', bd.play(124), T_DING + 1.5, 0.9)
    for j, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5')):
        M.add('bell', harp.play(n(m), 96), T_DING + 1.5 + 0.05 * j, 0.6, oven_p)
    band(T_FEAST, T_FINAL, vel=104)
    tune(T_FEAST, tpt_s, 'brass', 106, shift=-12, upto=16)
    tune(T_FEAST, horn, 'brass', 100, shift=-24, gain=0.6, upto=16)
    tune(T_FEAST, clar, 'tune', 96, upto=16)
    for t in np.arange(T_FEAST, T_FINAL, BEAT):
        M.add('drums', snare.play(80 if (t / BEAT) % 2 else 60), t, 0.5)
    for t in np.arange(84.0, T_FINAL, BEAT):     # everybody claps
        M.add('drums', slap.play(90), t, 0.5, 0.0)
    for k in range(8):
        t = T_DING + 2.0 + 1.1 * k
        M.add('bell', harp.play(n(('C5', 'F5', 'A5', 'C6')[k % 4]), 72), t, 0.5, oven_p)
    tf = T_FINAL
    M.add('drums', crash.play(118), tf, 0.8)
    M.add('drums', timp.play(118), tf, 0.8)
    M.add('bass', tuba.play(n('F1'), 118), tf, 1.0)
    hold = D - tf - 1.2
    for m, inst, bus, v in ((n('F2'), cello, 'strings', 90), (n('C3'), cello, 'strings', 84),
                            (n('A3'), horn, 'brass', 96), (n('F4'), tpt_s, 'brass', 96), (n('C5'), vln, 'strings', 84)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), tf, 1.0)
    for j, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('bell', harp.play(n(m), 90), tf + 0.06 * j, 0.6, -0.8 + 0.2 * j)
