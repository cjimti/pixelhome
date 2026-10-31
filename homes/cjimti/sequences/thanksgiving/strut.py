"""Strut: A proud tom turkey pops up in the middle of the Porch Front, gobbles, and fans his tail open across it:
seventeen broad feathers in bronze, copper and chestnut with gold tips, bands of sheen rolling out along them on the
beat. He struts step by step, footprints glowing behind him, to the Left wing and shows off there. A rival in green
bronze charges in from the free end of Right and fans back. They duel across the porch: gobble for gobble, each one
a bolt of colour flung the length of the house at the other, faster and faster, until both fire at once and the
bolts smash together over the porch. They walk in to face off at the porch and puff up at each other in turn, the
front line between the two tails shoved back and forth, the tom gaining ground, then a held breath and one last
puff: his tail fills the whole house and shoves the rival out the end of Right. Victory bands roll round the house.
Then the dinner triangle rings from the kitchen at the end of Right, rings of silver rolling down the house. His fan
sputters shut, the colour drains out of him, and he bolts out the back along the Side in a burst of feathers that fly
to both ends of the house. A moment later he peeks round the free end of Right, gives one small gobble and one small
fan, and ducks away.

The yard is never still: straw chevrons march in toward him on the beat along every run."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG12'
TITLE = 'Strut'
KIND = 'show'
DESCRIPTION = ('A proud tom fans his tail across the porch, struts, and duels a rival gobble for gobble, then puffs '
               'up until his tail fills the whole house. Then someone rings the dinner bell.')
VOICEOVER = "Every barnyard has one show-off, and this one has feathers to spare."

D = 90.0
SEED = 12
BEAT = 0.6                                      # 100 bpm
STRAW = hexc('#ff9010')
BRONZE = hexc('#a83a04')
COPPER = hexc('#ff4a00')
CHESTNUT = hexc('#d00804')
GOLD = hexc('#ffb000')
TIP = hexc('#ffb818')
RED = hexc('#ff0010')
DULL = hexc('#5a2008')
SILVER = hexc('#d8e8ff')
WHITE = hexc('#fff4e0')
R_A, R_B, R_C, R_TIP = hexc('#50a000'), hexc('#00d080'), hexc('#a8a000'), hexc('#f0ffd0')   # the rival's tail
EMERALD = hexc('#00ff60')
NFEATHER = 17
SEG_LO = np.array([0, 492, 894, 1311, 1660, 2033])
SEG_HI = np.array([491, 893, 1310, 1659, 2032, 2513])
MID = 1486.0                                    # the middle of the Porch Front
LEFT_C, RIGHT_C = 692.0, 2272.0                 # the middles of the two wings
END = 2512.0


def b(k):
    return k * BEAT


T_POP = b(4)
# moves: (start beat, end beat, from, to, steps)
MOVES = [(16, 32, MID, LEFT_C, 16), (64, 72, LEFT_C, MID, 16)]
R_MOVES = [(64, 72, RIGHT_C, 1716.0, 16)]       # the rival walks in to face him at the porch
T_RIVAL_IN, T_RIVAL_AT = b(38), b(41)
# gobbles before and after the duel: (beat, who, size)
GOBBLES = [(6, 'T', 0.8), (34, 'T', 1.0), (43, 'R', 1.0), (102, 'T', 1.2), (106, 'T', 1.2), (110, 'T', 1.3),
           (114, 'T', 1.4)]
# the duel: each gobble flings a bolt at the other; both fire at once at the end and the bolts collide
DUEL = [(44, 'T'), (46, 'R'), (48, 'T'), (50, 'R'), (52, 'T'), (53.5, 'R'), (55, 'T'), (56, 'R'), (57, 'T'),
        (58, 'R'), (59, 'T'), (59.5, 'R'), (60, 'T'), (60.5, 'R'), (61, 'T'), (61.5, 'R'), (62, 'T'), (62, 'R')]
BOLT = 1580.0                                   # bolt speed, units/s: a wing to the other in a second
T_CLASH = b(62) + (RIGHT_C - LEFT_C) / 2 / BOLT
# the face-off: (beat, who pushes, where the front line between the two tails ends up)
PUSH = [(72, 'T', 1700), (76, 'R', 1600), (80, 'T', 1850), (84, 'R', 1730), (88, 'T', 2000), (90, 'R', 1920),
        (92, 'T', 2100), (93, 'R', 2060), (94, 'T', 2180), (95, 'R', 2160), (100, 'T', 3300)]
B0 = MID + 50
T_HOLD, T_MEGA = b(96), b(100)
T_BELL = b(118)
T_SAG, T_FLEE, T_GONE = b(121), b(125), b(130)
T_PEEK, T_PEEK_GOB, T_PEEK_FAN, T_DUCK = b(138), b(140), b(141), b(145)


def stepper(t, moves, c):
    for k0, k1, c0, c1, steps in moves:
        t0, t1 = b(k0), b(k1)
        if t >= t0:
            u = min(1.0, (t - t0) / (t1 - t0)) * steps
            k = min(steps - 1, int(u))
            step = k + float(smoothstep(0.0, 0.62, u - k)) if u < steps else steps
            c = c0 + (c1 - c0) * step / steps
    return c


def position(t):
    """Where the tom is (path distance) and which way he faces (+1 toward the Right)."""
    c = stepper(t, MOVES, MID)
    face = -1 if b(16) <= t < b(64) else 1
    if t >= T_FLEE:
        u = (t - T_FLEE) / (T_GONE - T_FLEE)
        c, face = MID - (MID + 80) * u ** 1.6, -1
    return c, face


def walking(t):
    return any(b(k0) <= t < b(k1) for k0, k1, *_ in MOVES)


def front(t):
    """The front line between the two tails in the face-off."""
    B = B0
    for k, who, x in PUSH:
        B = float(keys(t, [(b(k), B), (b(k) + (0.9 if x > END else 0.3) * BEAT, x)])) if t >= b(k) else B
    return B


def bolts():
    """(start time, from, to, colour, who)."""
    out = []
    for k, who in DUEL:
        if who == 'T':
            out.append((b(k), LEFT_C, RIGHT_C, RED, who))
        else:
            out.append((b(k), RIGHT_C, LEFT_C, EMERALD, who))
    return out


def rival(t):
    """Rival's centre and fan half-width; None while he isn't on the house."""
    if t < T_RIVAL_IN:
        return None
    if t < T_RIVAL_AT:
        u = (t - T_RIVAL_IN) / (T_RIVAL_AT - T_RIVAL_IN)
        return END + 60 - (END + 60 - RIGHT_C) * smoothstep(0, 1, u) ** 0.7, 0.0
    if t < b(72):
        c = stepper(t, R_MOVES, RIGHT_C)
        W = keys(t, [(T_RIVAL_AT, 0), (b(42), 180), (b(63.5), 180), (b(64), 50), (b(71.5), 50), (b(72), 180)])
        return c, float(W)
    Wr = keys(t, [(b(72), 180), (b(76), 180), (b(76.3), 210), (b(84), 200), (b(84.3), 220), (b(90), 190),
                  (b(95), 130), (b(99), 120)])
    B = front(t)
    if B > END + 2 * Wr + 40:
        return None
    return B + Wr, float(Wr)


def tom_fan(t):
    if t < b(72):
        return float(keys(t, [(0, 0), (b(8), 0), (b(10), 172), (b(16), 172), (b(17), 50), (b(32), 50), (b(34), 200),
                              (b(63.5), 200), (b(64), 50)]))
    if t < T_SAG:
        return front(t) - MID
    u = (t - T_SAG) / (T_FLEE - T_SAG)
    stutter = np.floor(u * 8) / 8 * 0.7 + 0.3 * u            # it closes in jerks
    return max(0.0, (front(T_SAG) - MID) * (1 - stutter) * (1 + 0.15 * np.sin(40 * t)))


def gobble_env(u, dur):
    """Syllables of a gobble: fast pulses over dur seconds, falling off."""
    if u < 0 or u > dur + 0.2:
        return 0.0
    ph = (u * 9.0) % 1.0
    return float(np.exp(-ph / 0.25) * (u < dur) * (1 - 0.4 * u / dur))


def fan(pdp, c, W, t, pal, rate=0.5):
    """Feathers across [c - W, c + W]: (intensity, colour). Bands of sheen roll outward along them."""
    A, B_, C, T_ = pal
    u = (pdp - c) / W
    au = np.abs(u)
    inside = np.clip((1 - au) * W / 6, 0, 1)
    k = np.clip(np.floor((u + 1) / 2 * NFEATHER), 0, NFEATHER - 1)
    v = (u + 1) / 2 * NFEATHER - k
    gap = smoothstep(0.0, 0.14, v) * smoothstep(1.0, 0.86, v)
    sheen = 0.5 + 0.5 * np.cos(2 * np.pi * (au * min(6.0, 2.2 * W / 172) ** 0.6 * 2 - rate * t / BEAT))
    col = lerp(lerp(A, B_, sheen[:, None]), C, (k % 3 == 1)[:, None] * 0.9)
    col = lerp(col, T_, smoothstep(0.8, 0.9, au)[:, None] * 0.85)
    I = inside * (0.15 + 0.85 * gap) * (0.6 + 0.4 * sheen)
    return I, col


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    quiver = Flicker(rng, n, 3.0, 8.0)
    BL = bolts()
    TOM = (BRONZE, COPPER, CHESTNUT, TIP)
    RIV = (R_A, R_B, R_C, R_TIP)
    NF = 56
    f_v = rng.choice([-1, 1], NF) * rng.uniform(300, 1700, NF)
    f_t = T_FLEE + rng.uniform(0, 0.8, NF)
    f_c = np.array([TIP, COPPER, CHESTNUT, GOLD, BRONZE])[rng.integers(0, 5, NF)]
    f_ph = rng.uniform(0, 2 * np.pi, NF)
    off = rng.uniform(0, 1, NFEATHER)

    for f in range(F):
        t = f * DT
        kb = t / BEAT
        beat = np.exp(-((kb % 1.0) * BEAT) / 0.12)
        buf = np.zeros((n, 3))
        c, face = position(t)
        W = tom_fan(t)
        drain = smoothstep(T_SAG, T_FLEE, t) * (t < T_PEEK)
        vis = smoothstep(T_POP - 0.3, T_POP + 0.2, t) * (t < T_GONE)
        rv = rival(t)
        flinch = 1.0
        rflinch = 1.0

        # the yard: straw chevrons marching in toward him on the beat, along every run
        tgt = c if t < T_GONE else END
        ph = np.abs(pdp - tgt) / 150 + 0.5 * kb
        stripe = (0.5 + 0.5 * np.cos(2 * np.pi * ph)) ** 3
        yard = keys(t, [(0, 0), (2.0, 0.4), (T_HOLD, 0.4), (T_MEGA - 0.6, 0.15), (T_MEGA, 0.4), (T_BELL, 0.4),
                        (T_BELL + 0.3, 0.12), (T_GONE, 0.15), (T_GONE + 2, 0.4), (88, 0.4), (90, 0)])
        buf += light(STRAW, yard * (0.3 + 0.7 * stripe) * (0.75 + 0.45 * beat * (t < T_BELL or t > T_GONE)))

        # bolts in flight: a comet flung down the house; it lands on the other one and makes him flinch
        for t0, p0, p1, col, who in BL:
            u = t - t0
            dist = abs(p1 - p0)
            ta = dist / BOLT
            sgn = np.sign(p1 - p0)
            if 0 <= u < ta:
                x = p0 + sgn * BOLT * u
                if t >= T_CLASH and t0 == b(62):
                    continue
                trail = np.clip(-(pdp - x) * sgn, 0, None)
                buf += light(col, np.exp(-((pdp - x) / 12) ** 2) +
                             0.7 * np.exp(-trail / 120) * (trail > 0) * (trail < dist))
            elif ta <= u < ta + 0.6 and t0 != b(62):
                g = np.exp(-(u - ta) / 0.15)
                buf += light(col, 0.9 * g * np.exp(-((pdp - p1) / 80) ** 2))
                if who == 'T':
                    rflinch = min(rflinch, 1 - 0.4 * g)
                else:
                    flinch = min(flinch, 1 - 0.4 * g)
        u = t - T_CLASH
        if 0 <= u < 2.5:                             # the two bolts smash together over the porch
            buf += light(WHITE, 1.0 * np.exp(-u / 0.12) * np.exp(-((pdp - MID) / 160) ** 2))
            for col, sg in ((RED, -1), (EMERALD, 1)):
                ring = np.exp(-(((pdp - MID) * sg - 1300 * u) / 60) ** 2) * ((pdp - MID) * sg > 0)
                buf += light(col, 0.9 * ring * np.exp(-u / 1.0))
            flinch = min(flinch, 1 - 0.35 * np.exp(-max(u - 0.5, 0) / 0.3) * (u > 0.5))
            rflinch = min(rflinch, 1 - 0.35 * np.exp(-max(u - 0.5, 0) / 0.3) * (u > 0.5))

        # the face-off: each puff flares the pusher's tail and strikes sparks off the front line
        flare, rflare = 1.0, 1.0
        if b(72) <= t < T_SAG:
            B = front(t)
            for k, who, x in PUSH:
                uu = t - b(k)
                if 0 <= uu < 1.0:
                    g = np.exp(-uu / 0.25)
                    if who == 'T':
                        flare += 0.7 * g
                    else:
                        rflare += 0.7 * g
                    if B < END:
                        buf += light(WHITE, 0.9 * g * np.exp(-((pdp - B) / 25) ** 2))
            if T_HOLD <= t < T_MEGA:                 # the held breath: both tails tremble, tighter and tighter
                hold = smoothstep(T_HOLD, T_MEGA, t)
                buf += light(WHITE, 0.5 * hold * (0.5 + 0.5 * np.sin(2 * np.pi * (4 + 10 * hold) * t)) *
                             np.exp(-((pdp - B) / 20) ** 2) * (t < T_MEGA - 0.3))

        # the rival: green-bronze tail and a red head
        if rv is not None:
            rc, rW = rv
            if rW * rflinch > 2:
                I, col = fan(pdp, rc, rW * rflinch, t, RIV, 0.7)
                buf += light(1.0, np.clip(I * rflare * (1 + 0.2 * quiver(t)), 0, 1.3)) * col
            buf += light(R_A, 0.8 * np.exp(-((pdp - rc) / 10) ** 2))
            rh = rc - 18 if t < b(72) or T_RIVAL_IN <= t < T_RIVAL_AT else rc - 12
            buf += light(RED, np.exp(-((pdp - rh) / 7) ** 2))
            if t < T_RIVAL_AT:                       # dust as he charges in
                for k in range(6):
                    buf += light(R_C, 0.4 * (1 - k / 6) * np.exp(-((pdp - rc - 30 * (k + 1)) / 12) ** 2))

        if vis > 0:
            # his tail
            Wf = W * flinch
            if Wf > 2:
                I, col = fan(pdp, c, Wf, t, TOM, 0.5 if t < T_MEGA else 1.0)
                if t >= T_MEGA:                      # victory: bands roll out round the whole house on every beat
                    band = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(pdp - c) / 260 - kb))
                    I = I * (0.45 + 0.75 * band ** 2) * (1 + 0.25 * beat)
                    col = lerp(col, GOLD, (band ** 6)[:, None] * 0.6)
                if t >= T_BELL:                      # frozen by the bell, then sputtering
                    I = I * (1 - 0.45 * smoothstep(T_BELL, T_BELL + 0.3, t))
                    if t >= T_SAG:
                        kk = np.clip(np.floor(((pdp - c) / max(Wf, 1) + 1) / 2 * NFEATHER), 0, NFEATHER - 1).astype(int)
                        I = I * (np.sin(2 * np.pi * (6 + 9 * off[kk]) * t + 7 * off[kk]) > -0.2)
                col = lerp(col, DULL, drain)
                rattle = 1 + 0.25 * quiver(t) * (Wf > 100)
                pulse = 1 + 0.25 * beat * (t < T_BELL) * (b(10) <= t)
                I = I * rattle * pulse * flare * (1 - 0.6 * drain) * vis
                buf += light(1.0, np.clip(I, 0, 1.25)) * col
            # his run thumps with each step; footprints glow behind him and fade
            for k0, k1, c0, c1, steps in MOVES:
                t0, t1 = b(k0), b(k1)
                per = (t1 - t0) / steps
                if t0 <= t < t1 + 2.0:
                    for s in range(steps):
                        ts = t0 + (s + 0.62) * per
                        uu = t - ts
                        if 0 <= uu < 2.0:
                            ps = c0 + (c1 - c0) * (s + 1) / steps
                            buf += light(GOLD, 0.8 * np.exp(-uu / 0.7) * np.exp(-((pdp - ps) / 6) ** 2))
                            if uu < 0.3:
                                s_ = min(5, int(np.searchsorted(SEG_HI, ps)))
                                onrun = (pdp >= SEG_LO[s_]) & (pdp <= SEG_HI[s_])
                                buf += light(COPPER, 0.5 * np.exp(-uu / 0.1) * onrun)
            # his body and head: bigger as he puffs; the head bobs forward when he walks
            puff = 1 + 0.6 * smoothstep(b(72), T_MEGA + 0.5, t) * (1 - drain)
            d = pdp - c
            buf += light(lerp(BRONZE, DULL, drain), vis * 0.85 * np.exp(-(d / (10 * puff)) ** 2))
            buf += light(GOLD, vis * 0.3 * (1 - drain) * np.exp(-(d / (45 * puff)) ** 2))
            bob = 0.0
            if walking(t):
                per = 1.0 if t < b(64) else 0.5
                bob = 9 * np.sin(2 * np.pi * t / (per * BEAT)) + 18
            elif t >= T_FLEE:
                bob = 26
            hp = c + face * bob
            snood = 1.0
            for k, who, sz in GOBBLES:
                if who == 'T':
                    snood += 0.6 * gobble_env(t - b(k), 0.5 + 0.3 * sz)
            buf += light(lerp(RED, CHESTNUT, drain), vis * np.clip(snood, 0, 1.4) * np.exp(-((pdp - hp) / (8 * puff)) ** 2))

        # gobbles: the gobbler's run floods red in syllables, and red rings run out from his head both ways
        for k, who, sz in GOBBLES + [(k, w, 0.9 + 0.2 * (k - 44) / 18) for k, w in DUEL]:
            u = t - b(k)
            if not (0 <= u < 1.6):
                continue
            if who == 'T':
                cg, _ = position(b(k))
            else:
                r_ = rival(b(k))
                if r_ is None:
                    continue
                cg = r_[0]
            dur = 0.35 + 0.3 * min(sz, 1.2) if k < 44 or k > 62 else 0.3
            g = gobble_env(u, dur)
            s_ = min(5, int(np.searchsorted(SEG_HI, cg)))
            onrun = (pdp >= SEG_LO[s_]) & (pdp <= SEG_HI[s_])
            buf += light(RED if who == 'T' else EMERALD, 0.7 * min(sz, 1.2) * g * onrun)
            if k < 44 or k > 62:
                for lag in (0.0, 0.2, 0.4):
                    uu = u - lag
                    if uu > 0:
                        ring = np.exp(-((np.abs(pdp - cg) - 900 * uu * sz) / 70) ** 2)
                        buf += light(RED if who == 'T' else EMERALD, min(sz, 1.0) * ring * np.exp(-uu / (0.6 * sz)))

        # the mega puff: a white-gold shock rolls out from him to both ends
        u = t - T_MEGA
        if 0 <= u < 2.0:
            ring = np.exp(-((np.abs(pdp - MID) - 1500 * u) / 90) ** 2)
            buf += light(WHITE, 0.95 * ring * np.exp(-u / 0.8))
            buf += light(GOLD, 0.6 * np.exp(-u / 0.2))
            streak = np.clip(1 - np.abs(pdp - (2200 + 900 * u)) / 200, 0, 1)   # the rival flung out the end
            buf += light(EMERALD, 0.9 * np.exp(-u / 0.35) * streak)

        # the dinner triangle from the kitchen at the free end of Right: silver rings down the whole house
        u = t - T_BELL
        if 0 <= u < 3.0:
            for kd in range(13):
                ud = u - kd * 0.16
                if ud >= 0:
                    ring = np.exp(-((END - pdp - 1500 * ud) / 50) ** 2)
                    buf += light(SILVER, 0.7 * ring * np.exp(-ud / 1.2))
            ding = sum(np.exp(-(u - k * 0.16) / 0.07) * (u >= k * 0.16) for k in range(13))
            near = np.clip((pdp - 2040) / 300, 0, 1) * (pdp > 2034)
            buf += light(SILVER, np.clip(ding, 0, 1.0) * near * (0.7 + 0.3 * quiver(t)))

        # fleeing: dust behind him, and a burst of feathers flying to both ends of the house
        if T_FLEE <= t < T_GONE + 6:
            if t < T_GONE:
                buf += light(GOLD, 0.9 * np.exp(-((pdp - c) / 14) ** 2))     # a streak of him, running for it
                for k in range(6):
                    p, _ = position(t - 0.06 * (k + 1))
                    buf += light(STRAW, 0.7 * (1 - k / 6) * np.exp(-((pdp - p) / 14) ** 2))
            for i in range(NF):
                uu = t - f_t[i]
                if 0 <= uu < 6.0:
                    p = MID + f_v[i] * 0.9 * (1 - np.exp(-uu / 0.9))
                    tw = 0.55 + 0.45 * np.cos(f_ph[i] + 9 * uu)
                    g = 1.1 * np.exp(-uu / 3.0) * tw
                    buf += light(f_c[i], g * np.exp(-((pdp - p) / 10) ** 2))

        # the peek: round the free end of Right, a small gobble and a small fan
        if T_PEEK <= t < T_DUCK + 0.6:
            pk = keys(t, [(T_PEEK, 2540), (T_PEEK + 0.5, 2490), (T_DUCK, 2490), (T_DUCK + 0.5, 2550)])
            fanw = keys(t, [(T_PEEK_FAN, 0), (T_PEEK_FAN + 0.3, 34), (T_DUCK - 0.3, 34), (T_DUCK, 0)])
            if fanw > 1:
                uu = (pdp - pk - 10) / fanw
                ins = np.clip((1 - np.abs(uu)) * fanw / 4, 0, 1)
                kk = np.floor((uu + 1) / 2 * 5)
                buf += light(1.0, 0.85 * ins) * np.where((kk % 2 == 0)[:, None], COPPER, GOLD)
            buf += light(BRONZE, 0.9 * np.exp(-((pdp - pk - 8) / 8) ** 2))
            buf += light(RED, np.exp(-((pdp - pk + 10) / 5) ** 2))
            ug = t - T_PEEK_GOB
            if 0 <= ug < 1:
                buf += light(RED, 0.6 * np.exp(-ug / 0.3) * np.exp(-((np.abs(pdp - pk) - 500 * ug) / 20) ** 2))

        out[f][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A strut in Bb at 100 bpm, a beat to each of his steps: walking pizzicato bass, a log drum on every footfall where it
# lands on the house, a snare on two and four, the strut tune on muted trumpet. His tail opens with a ratchet and a
# harp sweep under a horn chord; gobbles are synthesized and panned to the gobbler. The rival charges in on a snare roll
# and a bassoon scramble; the duel is call and response, a trumpet stab with every gobble of his and a trombone answer
# for every gobble of the rival's, each bolt a whoosh across the stereo and a bonk where it lands, closer and closer
# together until both fire and the bolts crash in a cymbal over the porch. In the face-off each of his puffs goes up a
# semitone with timpani and a brass stab, each push back is a growl of low trombones; a roll, a held breath, and the
# mega puff lands in Eb with the whole band and the strut tune. The dinner triangle stops everything. The fan wheezes
# shut on a trombone fall, he flees on a xylophone run with glockenspiel feathers, and a pizzicato tiptoe and one small
# gobble finish it.

CH = {'Bb': (58, 62, 65), 'Eb': (55, 58, 63), 'F7': (57, 63, 65), 'Gm': (55, 58, 62), 'Cm': (55, 60, 63),
      'B': (59, 63, 66), 'C': (55, 60, 64), 'Db': (56, 61, 65), 'D': (57, 62, 66), 'Ab': (56, 60, 63),
      'Bb7': (56, 62, 65), 'Ab7': (54, 60, 63)}
ROOTS = {'Bb': 34, 'Eb': 39, 'F7': 41, 'Gm': 43, 'Cm': 36, 'B': 35, 'C': 36, 'Db': 37, 'D': 38, 'Ab': 44,
         'Bb7': 34, 'Ab7': 44}
# the strut tune, by bar of four beats: (beat, note, beats)
STRUT = [[(0, 'Bb3', 1), (1, 'D4', 0.5), (1.5, 'F4', 0.5), (2, 'G4', 1), (3, 'F4', 1)],
         [(0, 'Eb4', 0.5), (0.5, 'E4', 0.5), (1, 'F4', 1.5), (2.5, 'D4', 0.5), (3, 'Bb3', 1)],
         [(0, 'Eb4', 1), (1, 'G4', 0.5), (1.5, 'Bb4', 0.5), (2, 'C5', 1), (3, 'Bb4', 1)],
         [(0, 'Ab4', 0.5), (0.5, 'G4', 0.5), (1, 'F4', 1), (2, 'D4', 0.5), (2.5, 'C4', 0.5), (3, 'Bb3', 1)]]
STRUT_CH = ['Bb', 'Bb', 'Eb', 'F7']


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    mute = M.sampler('Brass/Trumpet/straightM-sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tpt_st = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    hmute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vpizz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    fall = M.hits('Brass/OldTrombone/Fall/*.wav')
    wood = M.hits('Percussion/LogDrumHi_MedM_v2*.wav')
    block = M.hits('VSCO 1 Percussion/varWood/claves_m*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[57]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-6]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v2*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')

    for name, gain, rev in (('tune', 0.3, 0.2), ('brass', 0.22, 0.25), ('bass', 0.38, 0.08), ('drums', 0.3, 0.12),
                            ('steps', 0.3, 0.1), ('wind', 0.26, 0.2), ('strings', 0.22, 0.3), ('harp', 0.28, 0.3),
                            ('bells', 0.24, 0.25), ('fx', 0.2, 0.2), ('gobble', 0.3, 0.18), ('bell', 0.3, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    L = G.length
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def mono(sig):
        return np.vstack([sig, sig])

    def moving(sig, t0, ts, ps):
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.clip(np.interp(tt, ts, ps), -1, 1) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def gobble(dur=0.75, f0=480.0, rate=11.0, seed=0):
        """A turkey's gobble: a buzzy, fast warble of syllables falling in pitch."""
        r = np.random.default_rng(seed)
        tt = np.arange(int(dur * SR)) / SR
        ph = (tt * rate * (1 + 0.15 * tt / dur)) % 1
        f = f0 * (1 + 0.32 * np.sin(2 * np.pi * ph)) * (1 - 0.22 * tt / dur)
        phase = 2 * np.pi * np.cumsum(f) / SR
        sig = sum(np.exp(-((k * f - 1400) / 1100) ** 2) / k ** 0.5 * np.sin(k * phase) for k in range(1, 10))
        syl = np.sin(np.pi * ph) ** 0.6 * r.uniform(0.6, 1.0, int(dur * rate * 1.2) + 2)[(tt * rate).astype(int)]
        rasp = np.convolve(r.normal(0, 1, len(tt)), np.ones(6) / 6, 'same') * 0.25
        env = np.clip(tt / 0.02, 0, 1) * np.clip((dur - tt) / 0.12, 0, 1)
        out = (sig / 3 + rasp) * syl * env
        return mono(out / (np.abs(out).max() + 1e-9))

    def play_tune(bars, k0, inst, bus, vel, beat=BEAT, shift=0, gain=1.0, pan=0.0):
        for j, bar in enumerate(bars):
            for e, m, ln in bar:
                t = b(k0) + (4 * j + e) * beat
                p = pan(t) if callable(pan) else pan
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * beat * 0.92, release=0.15), t, gain, p)

    def walk_bass(k0, chords, beat=BEAT, vel=85, shift=0):
        """Walking bass under a bar per chord: root, third, fifth, sixth."""
        for j, c in enumerate(chords):
            r = ROOTS[c] + shift
            third = 3 if c in ('Gm', 'Cm') else 4
            for e, iv in enumerate((0, third, 7, 9)):
                t = b(k0) + (4 * j + e) * beat
                M.add('bass', pizz.play(r + 12 + iv, vel), t, 0.9, -0.15)
            M.add('bass', tuba.play(r, vel - 5), b(k0) + 4 * j * beat, 0.7)

    def comp(k0, chords, beat=BEAT, vel=70, shift=0):
        for j, c in enumerate(chords):
            for e in (1, 3):
                t = b(k0) + (4 * j + e) * beat
                M.add('drums', snare.play(vel), t, 0.6, 0.15)
                for m in CH[c]:
                    M.add('brass', hmute.play(m + shift, vel - 5, dur=0.22), t, 0.4, 0.2)
            M.add('drums', bd.play(vel), b(k0) + 4 * j * beat, 0.6)
            M.add('drums', bd.play(vel - 15), b(k0) + (4 * j + 2) * beat, 0.5)

    def gob(t, who, sz, seed, short=False):
        if who == 'T':
            c, face = position(t)
            p = pan_at(c + face * 18)
            sig = gobble(0.35 if short else 0.55 + 0.25 * sz, 440 + 90 * sz, rate=11 + 2 * sz, seed=seed)
        else:
            r_ = rival(t)
            p = pan_at(r_[0] if r_ else END)
            sig = gobble(0.35 if short else 0.7, 360 + 40 * sz, rate=10, seed=100 + seed)
        M.add('gobble', sig, t, 0.6 + 0.4 * min(sz, 1.2), p)

    def fan_open(t0, t1, centre, w, key=58, inst=horn):
        p = pan_at(centre)
        M.add('fx', ratchet.play(110, dur=t1 - t0 + 0.3), t0, 0.9, p)
        M.add('fx', whoosh(t1 - t0 + 0.2, 300, 2400, 0.8, seed=int(t0 * 10)), t0, 0.8, p)
        steps = 12
        for i in range(steps):            # the harp sweeps out to both edges of the fan
            m = [0, 4, 7, 12, 16, 19, 24][i % 7] + key - 12 + 12 * (i // 7)
            for sgn in (-1, 1):
                M.add('harp', harp.play(m, 80), t0 + (t1 - t0) * i / steps, 0.6, pan_at(centre + sgn * w * i / steps))
        for m in CH['Bb']:
            M.add('brass', inst.play(m - 12 + (key - 58), 92, dur=t1 - t0 + 1.6, release=0.5), t0 + 0.2, 0.7, p)
        M.add('bells', glock.play(key + 12, 80), t1, 0.6, p)

    def steps_of(moves, half=False, vel=100, pan_fn=None):
        for k0, k1, c0, c1, steps in moves:
            per = (b(k1) - b(k0)) / steps
            for k in range(steps):
                t = b(k0) + (k + 0.62) * per
                ps = c0 + (c1 - c0) * (k + 1) / steps
                M.add('steps', wood.play(vel, pitch=-2 if k % 2 else 0), t, 0.8, pan_at(ps))

    pm = pan_at(MID)
    pl, pr = pan_at(LEFT_C), pan_at(RIGHT_C)

    # ---- b0-16: the yard; he pops up, gobbles, fans his tail across the Porch Front ----
    walk_bass(0, ['Bb'], vel=72)
    for k in range(4):
        M.add('steps', block.play(75), b(k), 0.5, 0.0)
        M.add('steps', block.play(55), b(k + 0.5), 0.4, 0.0)
    M.add('wind', bsn.play(n('F2'), 110), T_POP - 0.12, 1.0, pm)
    M.add('wind', bsn.play(n('Bb2'), 115), T_POP, 1.0, pm)
    M.add('drums', crash.play(90), T_POP, 0.5, pm)
    M.add('drums', bd.play(110), T_POP, 0.8, pm)
    walk_bass(4, ['Bb', 'Eb', 'F7'], vel=78)
    comp(8, ['Eb', 'F7'], vel=72)
    for i, (k, who, sz) in enumerate(GOBBLES):
        gob(b(k), who, sz, i)
    fan_open(b(8), b(10), MID, 172)
    M.add('strings', trem.play(n('F4'), 62, dur=b(6)), b(10), 0.6, pm)
    M.add('strings', trem.play(n('D4'), 62, dur=b(6)), b(10), 0.6, pm)
    M.add('fx', slide(0.0, b(1), 900, 500, b(1), 0.25), b(16), 0.8, pm)     # the fan folds

    # ---- b16-32: the strut, a beat to each step, Porch Front to the Left wing ----
    play_tune(STRUT, 16, mute, 'tune', 104, pan=lambda t: pan_at(position(t)[0]) * 0.6)
    walk_bass(16, STRUT_CH)
    comp(16, STRUT_CH, vel=78)
    steps_of(MOVES[:1])
    for k in range(16):
        t = b(16) + (k + 0.62) * BEAT
        M.add('wind', bsn.play(n('Bb2') + [0, 4, 7, 4][k % 4], 85), t, 0.5, pan_at(position(t)[0]))

    # ---- b32-44: display on the Left; the rival charges in from the end of Right and fans back ----
    fan_open(b(32), b(34), LEFT_C, 200)
    walk_bass(32, ['Bb', 'Eb'], vel=84)
    comp(32, ['Bb', 'Eb'], vel=76)
    play_tune([STRUT[2], STRUT[3]], 32, clar, 'wind', 92, pan=pl * 0.6)
    r = sroll.play(100, dur=T_RIVAL_AT - T_RIVAL_IN)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]), T_RIVAL_IN, 0.7, pan_at(2400))
    for i, t in enumerate(np.arange(T_RIVAL_IN, T_RIVAL_AT, 0.12)):
        M.add('steps', wood.play(105, pitch=1 if i % 2 else -1), t, 0.6, pan_at(rival(t)[0]))
        M.add('wind', bsn.play(n('Bb1') + i, 95), t, 0.6, pan_at(rival(t)[0]))
    M.add('drums', slap.play(110), T_RIVAL_AT, 0.8, pr)
    fan_open(b(41), b(42), RIGHT_C, 180, key=53, inst=bone)
    M.add('brass', bone.play(n('F3'), 100, dur=0.3), b(43) + 0.75, 0.7, pr)
    M.add('brass', bone.play(n('E3'), 100, dur=0.6), b(43) + 1.05, 0.7, pr)
    walk_bass(40, ['Gm'], vel=86)

    # ---- b44-63: the duel. Call and response, closer and closer; both fire and the bolts crash over the porch ----
    for k in range(44, 62):
        c = 'Gm' if (k // 4) % 2 == 0 else 'Cm'
        M.add('bass', pizz.play(ROOTS[c] + 12 + (0, 7, 12, 7)[k % 4], 92), b(k), 0.9, -0.1)
        M.add('drums', bd.play(95), b(k), 0.5)
        if k % 2:
            M.add('drums', snare.play(88), b(k), 0.6, 0.15)
        if k >= 54:
            M.add('drums', snare.play(70), b(k + 0.5), 0.5, 0.15)
        if k >= 58:
            M.add('drums', snare.play(60), b(k + 0.25), 0.4, 0.15)
            M.add('drums', snare.play(60), b(k + 0.75), 0.4, 0.15)
    M.add('strings', trem.play(n('G3'), 60, dur=b(18)), b(44), 0.5)
    for i, m in enumerate(('D4', 'Eb4', 'E4', 'F4')):
        M.add('strings', trem.play(n(m), 55 + 6 * i, dur=b(4.5)), b(44 + 4.5 * i), 0.5)
    tn, rn = 0, 0
    tstab = [n(m) for m in ('D4', 'F4', 'G4', 'A4', 'Bb4', 'C5', 'D5', 'Eb5', 'F5')]
    rstab = [n(m) for m in ('A2', 'C3', 'D3', 'E3', 'F3', 'G3', 'A3', 'Bb3', 'C4')]
    for j, (k, who) in enumerate(DUEL):
        t = b(k)
        sz = 0.9 + 0.2 * (k - 44) / 18
        gob(t, who, sz, 20 + j, short=k >= 55)
        src, dst = (LEFT_C, RIGHT_C) if who == 'T' else (RIGHT_C, LEFT_C)
        ta = abs(dst - src) / BOLT
        if who == 'T':
            M.add('brass', tpt_st.play(tstab[min(tn, 8)], 112, dur=0.25), t, 0.7, pl)
            tn += 1
        else:
            M.add('brass', bone.play(rstab[min(rn, 8)], 108, dur=0.3), t, 0.8, pr)
            rn += 1
        w = whoosh(ta if k < 62 else ta / 2, 600, 2400, 0.5, seed=50 + j)
        M.add('fx', moving(w, t, [t, t + ta], [pan_at(src), pan_at(dst)]), t, 0.6)
        if k < 62:
            M.add('steps', block.play(110), t + ta, 0.7, pan_at(dst))
    M.add('drums', crash.play(127), T_CLASH, 1.0, pm)
    M.add('drums', bd.play(127), T_CLASH, 1.0, pm)
    M.add('drums', timp.play(124), T_CLASH, 0.9, pm)
    M.add('drums', slap.play(120), T_CLASH, 0.8, pm)
    M.add('brass', tuba_s.play(n('G1'), 115, dur=0.8), T_CLASH, 0.9)
    M.add('fx', ratchet.play(90, dur=0.5), T_CLASH + 0.4, 0.5, pm)

    # ---- b64-72: both walk in, double time, to face off at the porch ----
    half = BEAT / 2
    play_tune(STRUT, 64, mute, 'tune', 110, beat=half, pan=lambda t: pan_at(position(t)[0]) * 0.6)
    play_tune(STRUT, 64, clar, 'wind', 90, beat=half, shift=12, gain=0.5, pan=lambda t: pan_at(position(t)[0]) * 0.6)
    walk_bass(64, STRUT_CH, beat=half, vel=95)
    comp(64, STRUT_CH, beat=half, vel=82)
    steps_of(MOVES[1:], vel=95)
    steps_of(R_MOVES, vel=85)

    # ---- b72-100: the face-off. His puffs climb a semitone each; the rival growls back on low trombones ----
    keys_up = ['Bb', 'B', 'C', 'Db', 'D']
    ku = 0
    pushes = [p for p in PUSH if p[0] < 100]
    for j, (k, who, x) in enumerate(pushes):
        t = b(k)
        nxt = b(pushes[j + 1][0]) if j + 1 < len(pushes) else T_HOLD
        pp = pan_at(min(x, END))
        M.add('fx', whoosh(0.5, 250, 2500, 0.8, seed=60 + j), t - 0.1, 0.7, pp)
        if who == 'T':
            c = keys_up[min(ku, 4)]
            M.add('drums', timp.play(112 + 3 * ku, pitch=ku), t, 0.9, pm)
            M.add('drums', bd.play(120), t, 0.9)
            M.add('drums', crash.play(80 + 8 * ku), t, 0.35 + 0.1 * ku)
            M.add('fx', ratchet.play(110, dur=0.5), t, 0.6, pm)
            for m in CH[c]:
                M.add('brass', tpt_st.play(m + 12 * (ku > 2) - 12 * (ku > 3), 118, dur=0.35), t, 0.7, pm)
                M.add('brass', horn.play(m - 12, 100, dur=max(0.4, nxt - t - 0.1), release=0.3), t + 0.05, 0.6, pm)
            M.add('bass', tuba_s.play(ROOTS[c], 100, dur=max(0.4, nxt - t - 0.05)), t, 0.9)
            M.add('strings', trem.play(CH[c][2], 66 + 6 * ku, dur=max(0.4, nxt - t)), t, 0.6)
            gob(t + 0.25, 'T', 1.0, 70 + j, short=True)
            ku += 1
        else:
            for m in ('E2', 'F2', 'Bb2'):
                M.add('brass', bone.play(n(m), 112, dur=0.5), t, 0.7, pp)
            M.add('drums', timp.play(110, pitch=-5), t, 0.8, pp)
            gob(t + 0.15, 'R', 0.8, 80 + j, short=True)
        # the beat goes on underneath: pizz roots on every beat, snare on the offbeats, busier toward the end
        k1 = pushes[j + 1][0] if j + 1 < len(pushes) else 96
        c = keys_up[max(0, ku - 1)]
        for kk in np.arange(k, k1, 1.0):
            M.add('bass', pizz.play(ROOTS[c] + 12 + (0, 7, 12, 7)[int(kk) % 4], 90), b(kk), 0.9, -0.1)
            M.add('drums', snare.play(80), b(kk + 0.5), 0.5, 0.15)
            if k >= 88:
                M.add('drums', snare.play(65), b(kk + 0.25), 0.4, 0.15)
                M.add('drums', snare.play(65), b(kk + 0.75), 0.4, 0.15)
    # the held breath: a roll that swells, then half a beat of silence
    r = troll.play(110, dur=T_MEGA - T_HOLD - 0.3)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 1.5, T_HOLD, 0.8)
    r = sroll.play(100, dur=T_MEGA - T_HOLD - 0.3)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_HOLD, 0.6)
    M.add('strings', trem.play(n('A4'), 80, dur=T_MEGA - T_HOLD - 0.3), T_HOLD, 0.6)
    M.add('strings', trem.play(n('Bb4'), 80, dur=T_MEGA - T_HOLD - 0.3), T_HOLD, 0.6)

    # ---- b100: the mega puff. Eb, the whole band, the strut tune; victory gobbles ----
    M.add('drums', crash.play(127), T_MEGA, 1.0)
    M.add('drums', bd.play(127), T_MEGA, 1.0)
    M.add('drums', timp.play(127, pitch=5), T_MEGA, 1.0, pm)
    M.add('fx', whoosh(1.4, 200, 3000, 1.0, seed=99), T_MEGA - 0.2, 0.9)
    w = whoosh(0.9, 2400, 400, 0.8, seed=98)
    M.add('fx', moving(w, T_MEGA, [T_MEGA, T_MEGA + 0.9], [pan_at(2200), 1.0]), T_MEGA, 0.8)
    M.add('brass', bone.play(n('F2'), 100, dur=0.25), T_MEGA + 0.3, 0.7, 0.9)        # the rival yelps off
    M.add('brass', bone.play(n('C2'), 100, dur=0.6), T_MEGA + 0.55, 0.7, 0.95)
    vic = ['Eb', 'Eb', 'Ab', 'Bb7']
    play_tune(STRUT, 100, tpt, 'tune', 118, shift=5)
    play_tune(STRUT, 100, horn, 'brass', 104, shift=5 - 12, gain=0.7)
    play_tune(STRUT, 100, glock, 'bells', 82, shift=17, gain=0.4)
    walk_bass(100, vic, vel=104)
    comp(100, vic, vel=96, shift=0)
    for k in range(100, 116, 4):
        for m in CH[vic[(k - 100) // 4]]:
            M.add('strings', vln.play(m + 12, 78, dur=b(4)), b(k), 0.5)
    for k in (116, 117):
        for m in CH['Eb']:
            M.add('brass', tpt_st.play(m + 12, 120, dur=0.3), b(k), 0.7)
        M.add('drums', bd.play(120), b(k), 0.9)
        M.add('drums', crash.play(100), b(k), 0.5)
        M.add('bass', tuba.play(n('Eb2'), 110), b(k), 0.9)
    r = troll.play(80, dur=b(1.5))
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]), b(116.5), 0.5)

    # ---- b118: the dinner triangle. Everything stops ----
    pk = pan_at(2450)
    for k in range(13):
        M.add('bell', tri.play(120 - 2 * k), T_BELL + 0.16 * k, 1.0, pk)
    M.add('strings', vln.play(n('E5'), 50, dur=2.0), T_BELL + 0.3, 0.4, pk)

    # ---- b121: the fan wheezes shut, he droops ----
    M.add('fx', fall.play(110), T_SAG, 1.2, pm)
    M.add('fx', slide(0.0, T_FLEE - T_SAG, 1100, 260, T_FLEE - T_SAG + 0.2, 0.4, shape=0.7), T_SAG, 1.0, pm)
    N = int((T_FLEE - T_SAG) * SR)
    tt = np.arange(N) / SR
    hiss = np.convolve(M.rng.normal(0, 1, N), np.ones(8) / 8, 'same') * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * tt))
    M.add('fx', mono(hiss * np.linspace(1, 0.1, N) * 0.6), T_SAG, 0.6, pm)
    M.add('brass', bone.play(n('Bb2'), 90, dur=0.8), T_SAG + 0.3, 0.7, pm)
    M.add('brass', bone.play(n('A2'), 90, dur=1.2), T_SAG + 1.1, 0.7, pm)
    M.add('gobble', gobble(0.35, 300, rate=8, seed=77), T_FLEE - 0.4, 0.5, pm)        # a very small gulp

    # ---- b125-130: he bolts out the back along the Side; feathers everywhere ----
    tt = np.linspace(T_FLEE, T_GONE, 40)
    ps = [pan_at(position(t)[0]) for t in tt]
    for i, t in enumerate(np.arange(T_FLEE, T_GONE, 0.1)):
        M.add('steps', wood.play(110, pitch=-2 if i % 2 else 1), t, 0.6, pan_at(position(t)[0]))
    scale = [n(m) for m in ('F5', 'D5', 'C5', 'Bb4', 'A4', 'G4', 'F4', 'Eb4', 'D4', 'C4', 'Bb3')]
    for i, t in enumerate(np.arange(T_FLEE, T_FLEE + 2.4, 0.1)):
        M.add('wind', xylo.play(scale[i % len(scale)] + 12 * (i < 11), 110), t, 0.6, pan_at(position(t)[0]))
    fr = np.random.default_rng(5)
    for t in np.sort(fr.uniform(T_FLEE, T_FLEE + 3.0, 22)):        # the feathers: glockenspiel twinkles all over
        M.add('bells', glock.play(n(str(fr.choice(['Bb5', 'D6', 'F5', 'C6', 'G5']))), int(fr.integers(55, 90))), t,
              0.5, float(fr.uniform(-0.9, 0.9)))
    r = sroll.play(100, dur=T_GONE - T_FLEE)
    M.add('drums', r, T_FLEE, 0.5, -0.5)
    w = whoosh(T_GONE - T_FLEE, 2400, 300, 0.9, seed=9)
    M.add('fx', moving(w, T_FLEE, tt, ps), T_FLEE, 0.8)
    M.add('drums', slap.play(100), T_GONE, 0.6, -0.95)
    M.add('drums', bd.play(90), T_GONE, 0.6, -0.95)

    # ---- b130-146: tiptoe; the peek, a small gobble, a small fan ----
    for i, t in enumerate(np.arange(b(131), T_PEEK, BEAT / 2)):
        M.add('strings', vpizz.play(n(('Bb4', 'D5', 'F4', 'Bb4', 'Eb5', 'D5')[i % 6]), 64), t, 0.8, 0.4)
        if i % 2 == 0:
            M.add('bass', pizz.play(n('Bb2') if i % 4 == 0 else n('F2'), 70), t, 0.7)
    prr = pan_at(2495)
    M.add('wind', clar.play(n('F4'), 80), T_PEEK, 0.8, prr)
    M.add('wind', clar.play(n('Bb4'), 80), T_PEEK + 0.25, 0.8, prr)
    M.add('gobble', gobble(0.45, 640, rate=13, seed=88), T_PEEK_GOB, 0.6, prr)
    M.add('fx', ratchet.play(80, dur=0.35), T_PEEK_FAN, 0.5, prr)
    M.add('bells', glock.play(n('Bb5'), 70), T_PEEK_FAN + 0.3, 0.6, prr)
    M.add('brass', mute.play(n('F4'), 80, dur=0.3), T_DUCK, 0.6, prr)
    M.add('brass', mute.play(n('Bb3'), 80, dur=0.8), T_DUCK + 0.4, 0.6, prr)
    M.add('bass', pizz.play(n('Bb2'), 90), T_DUCK + 0.4, 0.9)
    M.add('harp', harp.play(n('Bb3'), 60), T_DUCK + 0.45, 0.7)
