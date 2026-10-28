"""Food Coma: After dinner the house dozes off. It breathes slowly: on each inhale the warm light is
drawn in from both free ends and gathers on the porch, like a chest filling; on the exhale it spreads
back out along the wings to the ends. Every few breaths it snores, a slow rattle across the Porch
Front, and the breath after a snore whistles out as a little light running down the Right wing. Now
and then three Z's float off the porch and up the Side, getting smaller, out the back of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, Flicker, nframes, looped

CODE = 'TG09'
TITLE = 'Food Coma'
KIND = 'ambient'
DESCRIPTION = ('After dinner the house dozes. Light is drawn in to the porch on every slow breath and let out to '
               'the ends, with the occasional snore, a whistle, and Z\'s drifting off the back.')

AMBER = hexc('#ff7a14')
CORE = hexc('#ffa040')
DUSK = hexc('#a01818')
WARM = hexc('#ffc27a')
FLOOR_COLOR = hexc('#a02008')
FLOOR = 0.1
LOOP = 150.0
CHEST = 1486.0


def _schedule(rng, Dt):
    """Each breath has its own length, with a snore every few: [(start, period, snore)]; and when Z's float off."""
    breaths = []
    t = 0.0
    k = 0
    while t < Dt + 10:
        period = rng.uniform(5.6, 7.2)
        snore = (k % 4 == 3) or (rng.random() < 0.1)
        breaths.append((t, period, snore))
        t += period
        k += 1
    zz = []
    t = rng.uniform(10, 25)
    while t < Dt:
        zz.append(t)
        t += rng.uniform(28, 45)
    return breaths, zz


def _breath(ph):
    """How full the chest is at a phase of the breath: inhale over 40%, exhale over 45%, then a rest."""
    return smoothstep(0, 0.4, ph) * (1 - smoothstep(0.42, 0.87, ph))


def render(G, seed=29):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    n = G.N
    dist = np.abs(pdp - CHEST)
    PF = (pdp > 1312) & (pdp < 1660)
    RW = pdp > 2036

    def draw(Dt):
        out = np.zeros((nframes(Dt), n, 3), np.float32)
        tex = Flicker(rng, n, 0.04, 0.2)
        breaths, zz = _schedule(rng, Dt)
        starts = np.array([b[0] for b in breaths])

        for f in range(len(out)):
            t = f * DT
            i = int(np.searchsorted(starts, t, side='right') - 1)
            t0, per, snore = breaths[i]
            ph = (t - t0) / per
            b = _breath(ph)
            L = lerp(1250, 420, b)
            amp = 0.17 * np.sqrt(1250 / L) ** 0.9
            I = amp * np.exp(-(dist / L) ** 2) + 0.05
            I = I * (1 + 0.08 * tex(t))
            col = lerp(DUSK, AMBER, np.clip(np.exp(-(dist / L) ** 2) * 1.2, 0, 1)[:, None])
            buf = light(1.0, I) * col
            if snore:
                # a slow rattle on the porch at the top of the inhale
                s = smoothstep(0.2, 0.38, ph) * (1 - smoothstep(0.4, 0.5, ph))
                rattle = 0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t + pdp * 0.03)
                buf[PF] += light(CORE, (0.12 * s * rattle)[PF])
            # the breath after a snore whistles out along the Right wing
            if i > 0 and breaths[i - 1][2] and 0.42 < ph < 0.9:
                u = (ph - 0.42) / 0.48
                x = 2036 + u * 520
                buf += light(WARM, 0.2 * np.sin(np.pi * u) * np.exp(-((pdp - x) / 18) ** 2) * RW)
            # Z's float off the porch, up the Side, smaller and dimmer as they rise
            for tz in zz:
                for j in range(3):
                    u = t - tz - 1.6 * j
                    if 0 < u < 16:
                        x = 1300 - 85 * u                   # porch -> Porch Left -> Left -> up the Side
                        size = 14 * (1 - 0.6 * u / 16) * (1 - 0.15 * j)
                        a = 0.3 * smoothstep(0, 1.5, u) * (1 - smoothstep(10, 16, u)) * (1 - 0.15 * j)
                        buf += light(WARM, a * np.exp(-((pdp - x) / size) ** 2))
            out[f][G.path] = buf
        return out
    return looped(draw, LOOP, floor=(FLOOR, FLOOR_COLOR))


# ---- music: an all-night loop, slow breathing ----
# The breath is the whole structure. A low reed organ and a warm pad hold a sleepy chord in Bb that swells in on
# every inhale, as the light gathers on the porch, and lets go on the exhale; soft air is drawn in from both
# ends of the house and let out again. The chord moves on after each snore. A snore is a quiet low bassoon
# purring at the rattle's rate on the porch; the breath after it whistles softly down the Right wing; and each
# Z that floats off the back is a tiny glockenspiel note, three of them rising, drifting left up the Side.

MUSIC_SEED = 43
LOOP_FADE = 12.0                    # looped()'s default head/tail blend
CHORDS = (                          # one per snore inside the loop: pedal, low, three upper voices
    ('Bb1', 'F2', 'D3', 'F3', 'Bb3'),       # Bb
    ('Eb2', 'Bb2', 'G3', 'Bb3', 'D4'),      # Eb maj7
    ('G2', 'D3', 'F3', 'Bb3', 'D4'),        # Gm7
    ('Eb2', 'Bb2', 'G3', 'Bb3', 'C4'),      # Eb6
    ('F2', 'C3', 'Eb3', 'A3', 'C4'),        # F7, drowsy
    ('Bb1', 'F2', 'D3', 'F3', 'A3'),        # Bb maj7, and back to sleep
)


def _light_events(G, seed=29):
    """The breaths and Z's render() draws, by replaying its random stream."""
    rng = np.random.default_rng(seed)
    Flicker(rng, G.N, 0.04, 0.2)
    return _schedule(rng, LOOP + LOOP_FADE)


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note, slide
    rng = np.random.default_rng(MUSIC_SEED)
    N = int(LOOP * SR)
    for name, gain, rev in (('pad', 0.5, 0.28), ('air', 0.09, 0.12), ('snore', 0.22, 0.15), ('whistle', 0.18, 0.3),
                            ('zz', 0.7, 0.45)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    pdp = G.pd[G.path]

    def pan_pd(p):                          # distance along the path -> left/right from the street
        return 0.85 * (2 * (np.interp(p, pdp, xs) - x0) / (x1 - x0) - 1)

    def panned(mono, pan):                  # constant power; pan may be a per-sample array
        a = (np.asarray(pan) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def put(bus, sig, t, gain=1.0):         # add around the loop: whatever passes the end comes in at the start
        s = int(round((t % LOOP) * SR))
        while sig.shape[1]:
            k = min(sig.shape[1], N - s)
            M.add(bus, sig[:, :k], s / SR, gain)
            sig, s = sig[:, k:], 0

    def ramp(n, up):
        u = np.linspace(0, 1, max(n, 1)) if up else np.linspace(1, 0, max(n, 1))
        return np.sin(u * np.pi / 2) ** 2

    def at_rate(ctl, rate, n):              # control signal -> sample rate
        return np.interp(np.arange(n) / SR, np.arange(len(ctl)) / rate, ctl)

    breaths, zz = _light_events(G)
    starts = np.array([b[0] for b in breaths])

    # ---- the breath at 40 Hz round the loop, blended over the seam the way looped() blends the frames ----
    CR = 40
    T = np.arange(int((LOOP + LOOP_FADE) * CR)) / CR
    i = np.searchsorted(starts, T, side='right') - 1
    per = np.array([b[1] for b in breaths])[i]
    chest = _breath((T - starts[i]) / per)
    n0, c = int(LOOP * CR), int(LOOP_FADE * CR)
    w = np.linspace(0, 1, c, endpoint=False)
    chest = np.concatenate([chest[:c] * w + chest[n0:n0 + c] * (1 - w), chest[c:n0]])

    # ---- the pad: each voice moves on at the exhale after a snore, the others following a little behind ----
    changes = [starts[k + 1] + 0.42 * breaths[k + 1][1] for k, b in enumerate(breaths[:-1]) if b[2] and b[0] < LOOP]
    seq = sorted(zip(changes, CHORDS))
    pad = np.zeros((2, N), np.float32)
    voices = [
        (M.synth('Winds/Low'), 0, 34, 0.35, 0.0, 0.0),        # (instrument, chord voice, velocity, gain, pan, stagger)
        (M.synth('Winds/Low'), 1, 38, 0.6, 0.3, 2.5),
        (M.synth('Pads/Canadians'), 2, 44, 0.7, -0.35, 5.0),
        (M.synth('Pads/Canadians'), 3, 42, 0.7, 0.4, 1.0),
        (M.synth('Pads/Canadians'), 4, 38, 0.6, -0.1, 8.0),
    ]
    XF = 5.0
    for inst, vi, vel, gain, pan, lag in voices:
        merged = []
        for t, m in ((s + lag, ch[vi]) for s, ch in seq):
            if not merged or merged[-1][1] != m:
                merged.append((t, m))
        if len(merged) > 1 and merged[0][1] == merged[-1][1]:   # same note across the seam: one long note
            merged[0] = (merged[-1][0], merged[0][1])
            merged.pop()
        for j, (t, m) in enumerate(merged):
            length = ((merged[(j + 1) % len(merged)][0] - t) % LOOP or LOOP) + XF
            a = inst.render([(0.0, note(m), vel, length)], length + 0.5).astype(np.float32)
            k, f = a.shape[1], int(XF * SR)
            env = np.ones(k, np.float32)
            env[:f] = ramp(f, True)
            e = int(length * SR)
            env[e - f:e] = ramp(f, False)
            env[e:] = 0
            idx = (int(round(((t - XF / 2) % LOOP) * SR)) + np.arange(k)) % N
            pad[:, idx] += panned(a.mean(0) * env * gain, pan)
    pad *= at_rate(0.35 + 0.65 * chest, CR, N).astype(np.float32)   # in on the inhale, out on the exhale
    M.add('pad', pad, 0.0)
    del pad

    # ---- the air: drawn in from both ends on the inhale, let out from the porch on the exhale ----
    flow = np.diff(np.concatenate([chest, chest[:1]])) * CR
    flow = np.convolve(np.concatenate([flow[-20:], flow, flow[:20]]), np.hanning(21) / np.hanning(21).sum(), 'same')[20:-20]
    inhale, exhale = np.clip(flow, 0, None) / flow.max(), np.clip(-flow, 0, None) / -flow.min()
    ar = np.random.default_rng(MUSIC_SEED)
    air = np.zeros((2, N))
    for lvl, lo, gain in ((inhale, 900.0, 1.0), (exhale, 520.0, 0.8)):
        for pan, wide in ((-0.75, 1), (0.0, 0), (0.75, 1)):
            x = ar.normal(0, 1, (1, N + SR)).astype(np.float32)
            x = pb.Pedalboard([pb.HighpassFilter(180), pb.LowpassFilter(lo), pb.LowpassFilter(lo * 1.4)])(x, SR)[0]
            x = np.concatenate([x[:SR] * np.sqrt(np.linspace(0, 1, SR)) + x[N:] * np.sqrt(np.linspace(1, 0, SR)), x[SR:N]])
            gather = chest if wide == 0 else 1 - chest        # on the ends while the chest is empty, then in the middle
            env = at_rate(lvl ** 1.2 * (0.25 + 0.75 * gather), CR, N)
            air += panned(x / np.abs(x).max() * env * gain, pan)
    M.add('air', air, 0.0)
    del air

    # ---- the snores: a low bassoon, purring at the rattle's rate on the porch ----
    bassoon = M.sampler('Woodwinds/Bassoon/sus/*_v1_*.wav', tune=-12)
    porch = float(pan_pd(1486))
    for k, (t0, p, snore) in enumerate(breaths):
        if not snore or t0 > LOOP + LOOP_FADE:
            continue
        on, off = t0 + 0.2 * p, t0 + 0.5 * p
        wgt = float(_shown(on))
        if wgt < 0.05:
            continue
        root = next((ch for s, ch in reversed(seq) if s <= on), seq[-1][1])[0]
        a = bassoon.play(note(root) + 12, 70, dur=off - on + 0.6, release=0.4).mean(0)
        L = a.shape[0]
        tt = on + np.arange(L) / SR
        s = smoothstep(on, t0 + 0.38 * p, tt) * (1 - smoothstep(t0 + 0.4 * p, off + 0.3, tt))
        rattle = 0.4 + 0.6 * (0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * tt + 1486 * 0.03))
        pos = np.cumsum(2 ** ((-35 * smoothstep(on, off, tt)) / 1200))   # sags a little, comic
        pos = pos[pos < L - 1]
        a = np.interp(pos, np.arange(L), a) * (s * rattle)[:len(pos)] * wgt
        put('snore', panned(a, porch), on)

    # ---- the whistle: the breath after a snore whistles out down the Right wing ----
    soft = pb.Pedalboard([pb.LowpassFilter(2400)])
    for k in range(1, len(breaths)):
        if not breaths[k - 1][2]:
            continue
        t0, p, _ = breaths[k]
        on, dur = t0 + 0.42 * p, 0.48 * p
        wgt = float(_shown(on + dur / 2))
        if wgt < 0.05:
            continue
        top = note('F5') + int(rng.choice([0, 2, -2]))
        sig = slide(0.0, dur, 440 * 2 ** ((top - 69) / 12), 440 * 2 ** ((top - 5 - 69) / 12), dur, amp=0.25, shape=0.8)[0]
        u = np.arange(len(sig)) / len(sig)
        sig = soft((sig * np.sin(np.pi * u) ** 2 * wgt).astype(np.float32)[None, :], SR)[0]
        put('whistle', panned(sig, pan_pd(2036 + u * 520)), on)

    # ---- the Z's: three tiny rising glockenspiel notes as they float off up the Side ----
    glock = M.sampler('Percussion/Glock/*.wav')
    tiny = pb.Pedalboard([pb.LowpassFilter(3500)])
    for tz in zz:
        ch = next((c for s, c in reversed(seq) if s <= tz % LOOP), seq[-1][1])
        trio = sorted({note(m) % 12 for m in ch[2:]})
        base = note('C5')
        notes = sorted(base + ((pc - base) % 12) for pc in trio)
        for j, m in enumerate(notes):
            t = tz + 1.6 * j + 0.7
            wgt = float(_shown(t))
            if wgt < 0.05:
                continue
            a = glock.play(m, int(rng.integers(34, 44)), dur=2.5, release=1.2)
            a = tiny(a.astype(np.float32), SR).mean(0) * wgt * (1 - 0.15 * j)
            put('zz', panned(a, pan_pd(1300 - 85 * 0.7)), t)


def _shown(T):
    """How much of render time T reaches the loop (looped() blends 150..162 s into the first 12 s)."""
    T = np.asarray(T, float)
    return np.where(T < LOOP_FADE, np.clip(T / LOOP_FADE, 0, 1),
                    np.where(T < LOOP, 1.0, np.clip(1 - (T - LOOP) / LOOP_FADE, 0, 1)))
