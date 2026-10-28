"""Possessed: An innocent warm-white roofline that browns out, glitches, desyncs, dissolves into a
heartbeat, flatlines, and comes back as if nothing happened."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, heartbeat, nframes

CODE = 'SC5'
TITLE = 'Possessed'
KIND = 'show'
DESCRIPTION = 'Innocent warm white that browns out, glitches, desyncs, dissolves into a heartbeat, flatlines and comes back.'
VOICEOVER = 'A quiet house, warm and bright. Nothing to worry about... nothing at all.'

WHITE = hexc('#ffffff')
WARM = hexc('#ff8a30')
CYAN = hexc('#00e0ff')
RED = hexc('#ff0000')


def porch_center(G):
    pf = G.seg['Porch Front']
    return pf[len(pf) // 2]


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    D = 60.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    idx = np.arange(n, dtype=float)
    segs = [G.pi[G.seg[name]] for name in sorted(G.seg)]
    seg_id = np.empty(n, int)
    for i, s in enumerate(segs):
        seg_id[s] = i
    dips = sorted(rng.uniform(8, 14, 9))
    dropouts = [(11.5, 12.6, 'Side'), (13.0, 13.5, 'Porch Right')]
    static_t = sorted(rng.uniform(14, 24, 13))
    offsets = rng.integers(-60, 60, (100, len(segs)))
    clip_len = rng.uniform(0.15, 0.3, len(segs))
    clip_col = [hexc(c) for c in ('#00ffd0', '#ff00a0', '#80ff00', '#ffffff', '#0040ff', '#ff6000')]
    die = rng.uniform(34.5, 39.5, n)
    pdp = G.pd[G.path]
    d0 = G.pd[porch_center(G)]
    frozen = None

    def base(t):
        return light(WARM, np.full(n, 0.5))

    def corrupt(t):
        hue = 0.5 + 0.5 * np.sin(idx * 0.03 - t * 2.5)
        buf = light(lerp(hexc('#3000ff'), hexc('#00ffa0'), hue[:, None]), np.full(n, 0.35))
        k = int(t / 0.4)
        torn = np.empty_like(buf)
        for i, s in enumerate(segs):
            torn[s] = np.roll(buf, offsets[k % 100, i], axis=0)[s]
        p = (t - 14) * 120 % n
        for off, col in ((-6, RED), (0, WHITE), (6, CYAN)):
            torn += light(col, np.clip(1 - np.abs(idx - p - off) / 8, 0, 1) * 0.9)
        return torn

    for f in range(len(out)):
        t = f * DT
        if t < 14:
            buf = base(t)
            dip = min([1.0] + [0.3 for d in dips if d <= t < d + 0.12])
            buf *= dip ** 2.2
            for a, b, name in dropouts:
                if a <= t < b and (name != 'Porch Right' or (f % 3)):
                    buf[G.pi[G.seg[name]]] = 0
        elif t < 24:
            buf = corrupt(t)
            if any(s <= t < s + 0.15 for s in static_t):
                m = rng.random(n) < 0.35
                buf[m] = rng.random((m.sum(), 3)) ** 3 + WHITE * 0.3
        elif t < 34:
            buf = np.zeros((n, 3))
            sync = ((t - 24) % 2.0) < 0.12
            for i, s in enumerate(segs):
                lt = 0.0 if sync else (t % clip_len[i]) * (1 + i * 0.37)
                ph = (idx[s] - idx[s].min()) / len(s)
                saw = ((ph * 3 - lt * 4) % 1) ** 4
                buf[s] = light(WHITE if sync else clip_col[i], saw * (1.0 if sync else 0.8))
            frozen = buf.copy()
        elif t < 40:
            u = t - die
            burn = np.exp(-(u / 0.12) ** 2)
            buf = frozen * (u < 0)[:, None] + light(RED, burn * (u > -0.15))
        elif t < 50:
            period = keys(t, [(40, 1.1), (50, 0.5)])
            buf = np.zeros((n, 3))
            dist = np.abs(pdp - d0)
            delay = dist / 450
            ph = np.array([heartbeat(t - dl, 40, period) for dl in delay[::4]])
            env = np.interp(idx, idx[::4], ph)
            buf += light(RED, 1.1 * env * np.exp(-dist / 2500))
        elif t < 53:
            buf = light(RED, np.full(n, 0.28 * (t < 52.6)))
        elif t < 57:
            buf = np.zeros((n, 3))
        else:
            buf = light(WARM, np.full(n, keys(t, [(57, 0), (60, 0.5)])))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A music box lullaby in F major, 3/4, that the house is possessed out of. It runs down like a spring with the brownout
# (varispeed: slower and flatter, sagging at every dip), the porch-side harp drops out with the Side run and a bad
# connection buzzes on Porch Right. The corruption cuts the tune into 0.4 s blocks that jump, stutter and change key
# with the torn segments, under a scanner tone that follows the RGB comet and bursts of static. Then each run gets
# its own stuck instrument looping at that run's clip length while two choirs drift apart, all snapping to one F on
# the white syncs. The freeze holds the last 80 ms, fading pixel by pixel under 501 burn-out crackles; a heartbeat
# from the porch accelerates over rising tremolo, flatlines, and after the dark someone winds the box up again.
# Every time below is computed from render()'s own constants and seeded draws.

PBEAT = 0.5                                 # lullaby beat in box time (3/4, a bar is 1.5 s)
TUNE = [                                    # (bar, beat, note, beats): an original sixteen-bar lullaby
    (0, 0, 'C6', 2), (0, 2, 'A5', 1), (1, 0, 'F5', 1), (1, 1, 'A5', 1), (1, 2, 'C6', 1),
    (2, 0, 'D6', 2), (2, 2, 'C6', 1), (3, 0, 'A5', 3),
    (4, 0, 'Bb5', 2), (4, 2, 'G5', 1), (5, 0, 'E5', 1), (5, 1, 'G5', 1), (5, 2, 'Bb5', 1),
    (6, 0, 'A5', 1), (6, 1, 'G5', 1), (6, 2, 'F5', 1), (7, 0, 'G5', 3),
    (8, 0, 'C6', 2), (8, 2, 'A5', 1), (9, 0, 'F6', 1), (9, 1, 'E6', 1), (9, 2, 'D6', 1),
    (10, 0, 'C6', 2), (10, 2, 'Bb5', 1), (11, 0, 'A5', 3),
    (12, 0, 'G5', 1), (12, 1, 'A5', 1), (12, 2, 'Bb5', 1), (13, 0, 'A5', 2), (13, 2, 'G5', 1),
    (14, 0, 'F5', 3), (15, 0, 'C6', 1), (15, 1, 'F6', 2)]
BARS = ['F', 'F', 'Bb', 'F', 'C7', 'C', 'F', 'C', 'F', 'Bb', 'C7', 'F', 'C7', 'C7', 'F', 'F']
HARP = {'F': ('F3', 'A4', 'C5'), 'Bb': ('Bb2', 'D4', 'F4'), 'C': ('C3', 'G4', 'C5'), 'C7': ('C3', 'E4', 'Bb4')}
STUCK = {                                   # per run (sorted name order, as render() tears them): sound, two notes
    'Left': ('glock', 'C6', 'A5'), 'Porch Front': ('box', 'F5', 'A5'), 'Porch Left': ('harp', 'D6', 'C6'),
    'Porch Right': ('bell', 'Bb5', 'G5'), 'Right': ('vpizz', 'E5', 'G5'), 'Side': ('marimba', 'A4', 'F4')}


def _plan(G, seed=5):
    """render()'s seeded draws, in render()'s order, and the heartbeat peaks at the porch centre."""
    rng = np.random.default_rng(seed)
    n = G.N
    segs = sorted(G.seg)
    dips = sorted(rng.uniform(8, 14, 9))
    static_t = sorted(rng.uniform(14, 24, 13))
    offsets = rng.integers(-60, 60, (100, len(segs)))
    clip_len = rng.uniform(0.15, 0.3, len(segs))
    die = rng.uniform(34.5, 39.5, n)
    t = np.arange(40.0, 50.0, 0.001)
    env = np.array([heartbeat(x, 40, keys(x, [(40, 1.1), (50, 0.5)])) for x in t])
    pk = np.nonzero((env[1:-1] > env[:-2]) & (env[1:-1] >= env[2:]) & (env[1:-1] > 0.3))[0] + 1
    beats = [(float(t[i]), 'lub' if env[i] > 0.85 else 'dub') for i in pk]
    return dict(segs=segs, dips=dips, static_t=static_t, offsets=offsets, clip_len=clip_len, die=die, beats=beats)


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    P = _plan(G)
    T = M.n / SR

    box_s = M.synth('Plucks/Magic Music Box')
    bell_s = M.synth('Plucks/Bell 1')
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav')
    mar = M.sampler('Percussion/Marimba/*.wav')
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav')
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav')
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav')
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    bd_soft = M.hits('Percussion/BDrumNewhit_v[2-4]*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    zap = M.hits('Percussion/zap*.wav')
    wind = M.hits('Percussion/Ratchet1-Slow*.wav')

    for name, gain, rev in (('box', 0.5, 0.3), ('harp', 0.3, 0.25), ('buzz', 0.12, 0.05), ('glitch', 0.22, 0.1),
                            ('pad', 0.7, 0.35), ('voices', 0.45, 0.18), ('choir', 0.25, 0.35), ('hits', 0.5, 0.15),
                            ('freeze', 0.8, 0.05), ('pops', 0.16, 0.12), ('heart', 0.6, 0.08),
                            ('strings', 0.5, 0.3), ('ghost', 1.0, 0.6), ('tone', 0.05, 0.15)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    span = {k: float(pan_at(G.pd[G.seg[k]].mean())) for k in G.seg}
    pdp = G.pd[G.path]
    pf = G.seg['Porch Front']
    centre = float(pan_at(G.pd[pf[len(pf) // 2]]))

    def stereo(mono, pan):                  # per-sample constant-power pan
        a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
        return np.vstack([mono * np.cos(a), mono * np.sin(a)]) * np.sqrt(2)

    def tline(t0, t1):
        return t0 + np.arange(int(round((t1 - t0) * SR))) / SR

    def warp(src, tau):                     # read a box-time recording at box times tau (s)
        x = np.clip(tau, 0, src.shape[1] / SR - 1e-3) * SR
        return np.vstack([np.interp(x, np.arange(src.shape[1]), src[c]) for c in range(2)])

    def ramp_mask(t, spans, fade=0.004):    # 1 outside the spans, 0 inside, with short ramps
        m = np.ones_like(t)
        for a, b in spans:
            m = np.minimum(m, 1 - np.clip(np.minimum(t - a, b - t) / fade + 0.5, 0, 1))
        return m

    # ---- the lullaby, recorded once in box time: music box tune, harp waltz on the porch side ----
    BOX = len(BARS) * 3 * PBEAT
    tune = [(b * 1.5 + k * PBEAT, n(m), 92, d * PBEAT * 0.9) for b, k, m, d in TUNE]
    box_src = box_s.render(tune, BOX + 2)
    harp_src = np.zeros((2, int((BOX + 2) * SR)))
    for b, c in enumerate(BARS):
        for k, m in enumerate(HARP[c]):
            s = harp.play(n(m), 70 if k == 0 else 52, dur=1.4 - 0.5 * k)
            at = int((b * 1.5 + k * PBEAT) * SR)
            e = min(harp_src.shape[1], at + s.shape[1])
            harp_src[:, at:e] += s[:, :e - at]

    # ---- 0-14: innocent, then the brownout: the spring runs down from 8 s, sagging at each 0.12 s dip ----
    TA = 0.25
    ta = tline(TA, 14.0)
    u = np.clip((ta - 8) / 6, 0, 1)
    rate = 1 - 0.3 * u * u * (3 - 2 * u)
    dipm = ramp_mask(ta, [(d, d + 0.12) for d in P['dips']], 0.01)
    rate = rate * (0.72 + 0.28 * dipm)
    gain_a = 0.3 + 0.7 * dipm
    tau_a = np.concatenate([[0], np.cumsum(rate[:-1])]) / SR
    side_m = ramp_mask(ta, [(11.5, 12.6)], 0.006)                            # Side drops out: the harp goes
    M.add('box', warp(box_src, tau_a) * gain_a, TA, 1.0, 0.1)
    M.add('harp', warp(harp_src, tau_a) * gain_a * side_m, TA, 1.0, span['Side'])

    tb = tline(13.0, 13.5)                  # Porch Right's bad connection: dark one frame in three
    f = np.floor(tb / DT + 1e-9).astype(int)
    lit = (f % 3 != 0).astype(float)
    lit = np.convolve(lit, np.ones(48) / 48, 'same')
    ph = 2 * np.pi * 120 * (tb - 13.0)
    hum = (np.sin(ph) + 0.6 * np.sin(2 * ph) + 0.4 * np.sign(np.sin(3 * ph)) * 0.5) * (1 - lit) \
        + 0.15 * np.sin(ph) * lit
    hum += 0.5 * M.rng.normal(0, 1, len(tb)) * (1 - lit)
    M.add('buzz', np.vstack([hum, hum]), 13.0, 1.0, span['Porch Right'])

    # ---- 14-24: corruption. The tune is cut in render()'s 0.4 s blocks: jump, stutter or change key ----
    tau14 = tau_a[-1] + rate[-1] / SR
    off = P['offsets']
    parts = []
    for k in range(35, 60):
        t0 = max(14.0, k * 0.4)
        tk = tline(t0, min(24.0, (k + 1) * 0.4)) - t0
        o = off[k % 100]
        rk = 2 ** (int(round(o[2] / 20)) / 12)
        start = tau14 + (k - 35) * 0.4 + o[0] / 60 * 0.75
        if abs(o[1]) > 30:                  # a stuck grain, 40-90 ms long
            g = 0.04 + 0.05 * (o[3] + 60) / 120
            parts.append(start + (tk * rk) % g)
        else:
            parts.append(start + tk * rk)
    tau_b = np.mod(np.concatenate(parts), BOX)
    M.add('box', warp(box_src, tau_b) * 0.8, 14.0, 1.0, 0.1)
    M.add('harp', warp(harp_src, tau_b) * 0.6, 14.0, 1.0, -0.3)
    M.add('pad', M.synth('Pads/Ghost Pad').render([(14.0, n('F2'), 90, 9.6), (14.0, n('C3'), 80, 9.6),
                                                   (14.0, n('Db4'), 70, 9.6)], 26.0,
                                                  bends=[(14 + 0.05 * i, int(900 * np.sin(i * 0.37))) for i in
                                                         range(200)]), 0.0)
    tc = tline(14.0, 24.0)                  # the RGB comet, 120 px/s along the path: a scanner tone that follows it
    p = (tc - 14) * 120 % G.N
    fr = 330 * 2 ** (2 * p / G.N)
    ph = 2 * np.pi * np.cumsum(fr) / SR
    sc = 0.5 * np.sin(ph) + 0.18 * np.sin(3 * ph + 0.3) + 0.25 * np.sin(1.5 * ph)   # R, W, C as a fifth stack
    M.add('glitch', stereo(sc * np.clip((tc - 14) / 0.05, 0, 1), pan_at(pdp[p.astype(int)])), 14.0, 0.55)
    M.add('glitch', zap.play(120), 14.0, 1.0, 0.0)
    for i, s in enumerate(P['static_t']):   # static bursts: 35% of the pixels turn to snow
        ns = int(0.15 * SR)
        hold = np.repeat(M.rng.uniform(0, 1, ns // 96 + 1) ** 2, 96)[:ns]
        st = M.rng.normal(0, 1, (2, ns)) * hold * np.clip(np.arange(ns)[::-1] / 240, 0, 1)
        M.add('glitch', st, s, 0.9)
        M.add('glitch', zap.play(100, pitch=float(M.rng.uniform(-7, 5)), dur=0.15), s, 0.6,
              float(M.rng.uniform(-0.7, 0.7)))

    # ---- 24-34: desync. Each run loops its own stuck pair of notes at its clip length; white syncs every 2 s ----
    syncs = [24.0 + 2 * j for j in range(5)]
    insync = lambda t: any(s <= t < s + 0.12 for s in syncs)
    play = {'glock': lambda m, v, d: glock.play(m, v, d), 'harp': lambda m, v, d: harp.play(m, v, d),
            'marimba': lambda m, v, d: mar.play(m, v, d), 'vpizz': lambda m, v, d: vpizz.play(m, v, d)}
    synth_notes = {'box': [], 'bell': []}
    for i, name in enumerate(P['segs']):
        kind, a, b = STUCK[name]
        cl = float(P['clip_len'][i])
        for j, t in enumerate(np.arange(np.ceil(24 / cl) * cl, 34.0, cl)):
            if insync(t) or insync(t + 0.05):
                continue
            m = n(a if j % 2 == 0 else b)
            if kind in synth_notes:
                synth_notes[kind].append((t, m, 84, cl * 0.8))
            else:
                M.add('voices', play[kind](m, 84, cl), t, 0.8, span[name])
    M.add('voices', M.synth('Plucks/Magic Music Box').render(synth_notes['box'], 35.0), 0.0, 0.9)   # Porch Front, centre
    M.add('voices', bell_s.render(synth_notes['bell'], 35.0), 0.0, 0.5, span['Porch Right'])
    for s in syncs:                         # everyone on one F, hard
        for kind, m in (('glock', 'F6'), ('harp', 'F5'), ('marimba', 'F4'), ('vpizz', 'F5')):
            M.add('hits', play[kind](n(m), 120, 0.9), s, 0.8)
        M.add('hits', cpizz.play(n('F2'), 120), s, 1.0)
        M.add('hits', bd.play(118), s, 0.9)
        M.add('hits', crash_s.play(105), s, 0.45)
    for sign, delay in ((-1, 0.0), (1, 0.37)):                # two choirs, in tune only at the syncs
        bends = []
        for t in np.arange(24.0, 34.0, 0.02):
            last = max(s for s in syncs if s <= t)
            bends.append((t, int(sign * 2600 * min(1.0, (t - last) / 1.8) ** 1.5)))
        ch = M.synth('Pads/Ooh').render([(24.0 + delay, n(m), 80, 10.0 - delay) for m in ('F4', 'Ab4', 'C5')],
                                        35.0, bends=bends)
        M.add('choir', ch, 0.0, 0.8, -0.5 * sign)

    # ---- 34-40: freeze. The last 80 ms loops, fading as the pixels burn out one by one ----
    s0, s1 = int(33.92 * SR), int(34.0 * SR)
    grain = sum(M.buses[b]['sig'][:, s0:s1] * M.buses[b]['gain'] for b in ('voices', 'choir', 'hits', 'box'))
    for b in ('voices', 'choir', 'hits', 'box', 'harp', 'pad', 'glitch'):
        M.buses[b]['sig'][:, s1:] *= 0
        M.buses[b]['sig'][:, s1 - 96:s1] *= np.linspace(1, 0, 96)
    tf = tline(34.0, 40.0)
    reps = int(np.ceil(len(tf) / grain.shape[1]))
    die = P['die']
    alive = np.interp(tf, np.sort(die), np.linspace(1, 0, len(die)), left=1.0, right=0.0)
    M.add('freeze', np.tile(grain, reps)[:, :len(tf)] * alive, 34.0)
    for j in range(G.N):                    # each pixel's red burn: a crackle where it is
        npop = int(M.rng.integers(500, 1600))
        x = M.rng.normal(0, 1, npop) * np.exp(-np.arange(npop) / (npop / 5))
        x = np.diff(np.concatenate([[0], x])) if j % 2 else x
        M.add('pops', np.vstack([x, x]), float(die[j]) - 0.06, float(M.rng.uniform(0.5, 1.0)), float(pan_at(pdp[j])))

    # ---- 40-50: the heartbeat from the porch, period 1.1 -> 0.5 s, over a chromatic tremolo rise ----
    for t, kind in P['beats']:
        lub = kind == 'lub'
        nt = int(0.35 * SR)
        tt = np.arange(nt) / SR
        fq = (62 if lub else 52) * np.exp(-tt / 0.12) + 34
        th = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-tt / (0.11 if lub else 0.08)) * np.clip(tt / 0.004, 0, 1)
        M.add('heart', np.vstack([th, th]), t - 0.02, 1.0 if lub else 0.7, centre)
        M.add('heart', (bd if lub else bd_soft).play(110 if lub else 90), t - 0.02, 0.5 if lub else 0.35, centre)
    for i, (t, m) in enumerate(((40.0, 'F2'), (42.5, 'Gb2'), (45.0, 'G2'), (47.5, 'Ab2'))):
        M.add('strings', ctrem.play(n(m), 60 + 15 * i, dur=2.6), t, 0.6 + 0.2 * i)
    for t, m, d in ((43.0, 'C5', 7.0), (46.0, 'Db5', 4.0), (48.0, 'D5', 2.0)):
        M.add('strings', vtrem.play(n(m), 70 + 10 * (t > 45), dur=d), t, 0.5 + 0.1 * (t - 43) / 5, 0.25)
    tg = tline(41.0, 49.5)                  # far away, the lullaby, very slow
    ghost = warp(box_src, 0.55 * (tg - 41.0)) * np.clip((tg - 41) / 1.5, 0, 1) * np.clip((49.5 - tg) / 1.0, 0, 1)
    M.add('ghost', ghost, 41.0, 0.35, -0.2)

    # ---- 50-52.6: flatline; 52.6-57 dark; someone winds the box; 57: the lullaby, as if nothing happened ----
    tt = tline(50.0, 52.6)
    tone = np.sin(2 * np.pi * 1000 * tt) + 0.08 * np.sin(2 * np.pi * 2000 * tt)
    tone *= np.clip((tt - 50) / 0.01, 0, 1) * np.clip((52.6 - tt) / 0.002, 0, 1)
    M.add('tone', np.vstack([tone, tone]), 50.0, 1.0, centre)
    M.add('hits', wind.play(100), 55.3, 1.0, centre)
    tr = tline(57.0, min(T, 61.0))
    v = np.clip(0.55 + 0.45 * (tr - 57) / 2, 0, 1)
    M.add('box', warp(box_src, tr - 57.0) * v, 57.0, 1.0, 0.1)
    M.add('harp', warp(harp_src, tr - 57.0) * v, 57.0, 1.0, span['Side'])
