"""Dad Joke: the Left wing is Dad, the Right wing is the kid, the Porch Front is the drum kit.
Every syllable lights the speaker's wing (the bright spot slides with the pitch, so questions rise)
and sends a packet of light round the porch to the listener. Three jokes: a groan, a bigger groan,
and a third that the kid walks out on (off the free end of Right) before the punchline. Dad laughs
at it anyway, alone, until the laugh fills the house and the kid comes back in to laugh with him."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, smoothstep, keys, lerp, Flicker, nframes

CODE = 'FA02'
TITLE = 'Dad Joke'
KIND = 'show'
DESCRIPTION = ('Dad is the left wing, the kid is the right, the porch is the drum kit. Three jokes, '
               'with timing: ba-dum-tss, the eye roll, the groan, and a kid who walks out before the punchline.')

DAD = hexc('#ffa040')
KID = hexc('#4fd0d8')
GOLD = hexc('#ffd890')
BRASS = hexc('#c08030')
ROOM = hexc('#203060')
GROAN = hexc('#7a9a70')
CRICKET = hexc('#60ff40')


def say(t0, pattern, gap=0.08):
    """pattern: list of (dur, amp, pitch) or ('-', pause). -> syllables [(t, dur, amp, pitch)], end time."""
    out, t = [], t0
    for s in pattern:
        if s[0] == '-':
            t += s[1]
            continue
        d, a, p = s
        out.append((t, d, a, p))
        t += d + gap
    return out, t


def laugh(t0, k, amp=1.0, rate=0.26, p0=0.9, p1=0.4):
    return [(t0 + i * rate, 0.15, amp * (1 - 0.25 * i / max(1, k - 1)), lerp(p0, p1, i / max(1, k - 1)))
            for i in range(k)]


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    D = 70.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    x = G.pd[G.path]
    pi = np.arange(n)
    L = (pi >= 81) & (pi <= 178)
    R = (pi >= 381) & (pi <= 500)
    PF = (pi >= 261) & (pi <= 331)
    ROOMS = ~(L | R | PF)
    # position along each wing, 0 at the inner (porch) end, 1 at the outer end
    uL = np.clip((x[178] - x) / (x[178] - x[81]), 0, 1)
    uR = np.clip((x - x[381]) / (x[500] - x[381]), 0, 1)
    uPF = (x - x[261]) / (x[331] - x[261])
    shimmer = Flicker(rng, n, 0.1, 0.6)
    sparkle = rng.uniform(0, 1, (int(D / DT) + 2, n))

    dad, kid = [], []
    # joke 1
    s, e = say(2.5, [(0.22, 0.7, 0.4), (0.25, 0.9, 0.7), (0.3, 0.8, 0.5)]); kid += s
    s, e = say(4.6, [(0.2, 0.8, 0.5), (0.25, 0.9, 0.7), (0.28, 0.8, 0.5), ('-', 0.35),
                     (0.2, 0.8, 0.5), (0.45, 1.0, 0.3)]); dad += s
    drums = [(7.4, 1.0)]
    dad += laugh(8.3, 6)
    eyeroll = [(10.1, 1.5)]
    s, e = say(12.0, [(0.55, 0.5, 0.15)]); kid += s                   # "dad."
    # joke 2: a question, so the pitch climbs
    s, e = say(14.0, [(0.18, 0.8, 0.4), (0.15, 0.7, 0.35), (0.12, 0.6, 0.35), (0.2, 0.85, 0.55),
                      (0.2, 0.7, 0.45), (0.2, 0.85, 0.55), (0.14, 0.6, 0.5), (0.14, 0.6, 0.55),
                      (0.2, 0.8, 0.7), (0.4, 1.0, 0.98)]); dad += s
    s, e = say(18.1, [(0.4, 0.45, 0.2)]); kid += s                    # "...why?"
    roll = (19.1, 21.2)
    s, e = say(21.4, [(0.16, 0.8, 0.5), (0.22, 0.85, 0.6), (0.14, 0.6, 0.45), (0.14, 0.6, 0.45),
                      (0.3, 1.0, 0.8), (0.3, 1.0, 0.85), (0.22, 0.8, 0.6), (0.12, 0.6, 0.5),
                      (0.12, 0.6, 0.5), (0.5, 1.05, 0.25)]); dad += s
    drums.append((24.5, 1.15))
    dad += laugh(25.3, 8)
    groans = [(27.6, 3.0, 1.0)]
    # joke 3: the kid has heard this one
    s, e = say(32.4, [(0.2, 0.8, 0.5), ('-', 0.25), (0.15, 0.7, 0.5), (0.12, 0.6, 0.45),
                      (0.18, 0.8, 0.6), (0.15, 0.7, 0.5), (0.15, 0.7, 0.5), (0.2, 0.8, 0.55)]); dad += s
    groans.append((34.4, 1.0, 0.6))
    walkout = (35.4, 37.4)
    s, e = say(37.6, [(0.2, 0.7, 0.5), (0.2, 0.8, 0.6), (0.15, 0.7, 0.5), (0.2, 0.75, 0.6),
                      (0.25, 0.85, 0.7), (0.18, 0.7, 0.5), ('-', 0.6), (0.2, 0.8, 0.5),
                      (0.22, 0.9, 0.65), (0.3, 1.0, 0.8), (0.55, 1.05, 0.3)]); dad += s
    limp = 42.4
    crickets = [43.3, 43.65, 44.4, 44.75]
    dad += laugh(45.8, 2, 0.5, 0.45, 0.5, 0.45)
    dad += laugh(47.0, 4, 0.75, 0.3)
    dad += laugh(48.6, 10, 1.0, 0.27)
    big = (48.6, 53.6)                                                # the laugh fills the house
    peek = (54.0, 55.0)
    kid += laugh(55.6, 1, 0.6, 0.3, 0.5, 0.5)
    kid += laugh(56.5, 2, 0.75, 0.3, 0.6, 0.5)
    kid += laugh(57.8, 7, 0.9, 0.29, 0.8, 0.4)
    dad += laugh(57.9, 8, 0.85, 0.31, 0.8, 0.4)

    def voice(syl, t):
        A, P = 0.0, 0.5
        for t0, d, a, p in syl:
            if t0 - 0.03 <= t <= t0 + d + 0.05:
                u = np.clip((t - t0 + 0.03) / (d + 0.08), 0, 1)
                e = a * np.sin(np.pi * u) ** 0.7
                if e > A:
                    A, P = e, p
        return A, P

    # packets: (t emit, amp, source pd, direction, colour, stop pd)
    packets = [(t0 + d / 2, a, x[178], +1, DAD) for t0, d, a, p in dad] + \
              [(t0 + d / 2, a, x[381], -1, KID) for t0, d, a, p in kid]
    V = 1500.0

    for f in range(len(out)):
        t = f * DT
        buf = np.zeros((n, 3))
        fade = keys(t, [(0, 0), (2, 1), (66, 1), (70, 0)])
        sh = 1 + 0.05 * shimmer(t)

        # the room: Side and the porch sides, a dim evening blue
        room = 0.07 + 0.03 * np.sin(2 * np.pi * t / 9)
        bl = keys(t, [(48.6, 0), (52, 1), (54.5, 1), (60, 0.4), (64, 0)])
        buf += light(ROOM, room * fade * ROOMS * sh)

        # ---- Dad
        A, P = voice(dad, t)
        base = 0.14 * fade
        spot = np.exp(-((uL - P) / 0.26) ** 2)
        IL = base + A * (0.12 + 0.85 * spot)
        buf += light(DAD, IL * L * sh)

        # ---- kid
        kidc = KID
        A, P = voice(kid, t)
        spot = np.exp(-((uR - P) / 0.26) ** 2)
        IR = 0.13 * fade + A * (0.12 + 0.85 * spot)
        for tg, dur, depth in groans:                      # the groan: the wing sags and drains
            if tg <= t < tg + dur + 0.6:
                u = (t - tg) / dur
                g = depth * smoothstep(0, 0.25, u) * (1 - smoothstep(0.85, 1.2, u))
                sag = 1 - 0.85 * g * np.sin(np.pi * np.clip(uR, 0, 1)) ** 0.8 * smoothstep(0, 1, min(u, 1))
                IR = (IR + 0.25 * g * (1 - 0.6 * u)) * sag
                kidc = lerp(KID, GROAN, g)
        kid_mask = np.ones(n)
        if t >= walkout[0]:
            # the kid gathers up and leaves by the free end; later peeks back in
            w = smoothstep(walkout[0], walkout[0] + 0.5, t)
            blob = keys(t, [(walkout[0] + 0.4, x[381] + 140), (walkout[1], x[500] + 60)])
            if t < peek[0]:
                gathered = np.exp(-((x - blob) / 35) ** 2) * 0.35
                IR = lerp(IR, gathered, w)
            else:
                pk = keys(t, [(peek[0], x[500] + 50), (peek[1], x[500] - 40), (56.9, x[500] - 60),
                              (57.6, x[500] - 60)])
                spread = smoothstep(56.9, 57.8, t)
                gathered = np.exp(-((x - pk) / 30) ** 2) * 0.35
                IR = lerp(gathered + A * np.exp(-((x - pk) / 30) ** 2), IR, spread)
        buf += light(kidc, IR * R * sh)

        # eye roll: a bright pupil goes up and over the wing
        for te, dur in eyeroll:
            if te <= t < te + dur:
                u = (t - te) / dur
                pos = 0.15 + 0.7 * smoothstep(0, 1, u)
                arc = np.sin(np.pi * u)
                buf += light(hexc('#e0ffff'), (0.3 + 0.5 * arc) * np.exp(-((uR - pos) / 0.06) ** 2) * R)

        # ---- packets of speech travelling round the porch
        for te, a, src, d, col in packets:
            age = t - te
            if 0 <= age < 1.4:
                pos = src + d * V * age
                env = np.exp(-age / 0.9) * a
                buf += light(col, 0.75 * env * np.exp(-((x - pos) / 26) ** 2) * ~(L | R))

        # ---- the drum kit
        I_pf = 0.05 * fade
        for td, amp in drums:
            u = t - td
            if 0 <= u < 2.2:
                ba = np.exp(-u / 0.09) * np.exp(-((uPF - 0.3) / 0.2) ** 2)
                dum = (u >= 0.22) * np.exp(-max(0, u - 0.22) / 0.12) * np.exp(-((uPF - 0.7) / 0.2) ** 2)
                tss = (u >= 0.55) * np.exp(-max(0, u - 0.55) / 0.6)
                spark = sparkle[f] ** 6
                buf += light(BRASS, amp * 0.9 * (ba + dum) * PF)
                buf += light(GOLD, amp * tss * (0.25 + 0.9 * spark) * PF)
        if roll[0] <= t < roll[1] + 0.2:
            u = (t - roll[0]) / (roll[1] - roll[0])
            r = (0.1 + 0.5 * u) * (sparkle[f] ** 3) * (1 - smoothstep(1.0, 1.1, u))
            buf += light(BRASS, r * PF)
        if limp <= t < limp + 1.5:                          # the sad, limp "tss"
            u = t - limp
            buf += light(hexc('#7090b0'), 0.35 * np.exp(-u / 0.35) * sparkle[f] ** 4 * PF)
        buf += light(BRASS, I_pf * PF)

        # crickets on Side while nobody laughs
        for tc in crickets:
            if tc <= t < tc + 0.3:
                u = (t - tc) / 0.3
                c1 = np.exp(-((x - 180) / 4) ** 2) + np.exp(-((x - 300) / 4) ** 2)
                buf += light(CRICKET, 0.3 * np.sin(np.pi * u) * ((u * 12) % 1 < 0.5) * c1)

        # the big laugh spreads from Dad through the whole house: every HA sends a ripple outward
        if big[0] <= t < 64:
            reach = keys(t, [(big[0], 0.25), (big[1], 1.0)])
            for t0, d, a, p in dad:
                age = t - t0
                if t0 >= big[0] and 0 <= age < 2.5:
                    r = 950 * age
                    dl = np.where(x < x[81], x[81] - x, np.where(x > x[178], x - x[178], 0))
                    ring = np.exp(-((dl - r) / 70) ** 2) * (dl > 0)
                    buf += light(GOLD, 0.45 * a * reach * ring * np.exp(-age / 1.4) * (1 - 0.7 * R))
            buf += light(GOLD, 0.1 * bl * ~L * (1 - R))

        out[f][G.path] = np.clip(buf, 0, 1)
    return out
