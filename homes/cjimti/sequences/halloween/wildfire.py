"""Wildfire: A match is struck on the porch; fire spreads along the roof, jumps ahead, burns out.
Then blue ghost-fire races in from both ends and detonates on the porch."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, smooth_noise, Flicker, colormap, nframes

CODE = 'SC2'
TITLE = 'Wildfire'
KIND = 'show'
DESCRIPTION = 'A match strikes on the porch. Fire spreads around the corners, embers jump ahead, then blue ghost-fire races in from both ends.'
VOICEOVER = "One match. One spark on the porch. That's all it ever takes."

PALE = hexc('#ffd070')
PURPLE = hexc('#5000c0')
WHITE = hexc('#ffffff')


def porch_center(G):
    pf = G.seg['Porch Front']
    return pf[len(pf) // 2]


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    D = 64.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    d0 = pd[porch_center(G)]
    dist = np.abs(pd - d0)
    V, T0 = 70.0, 3.0
    t_ign = T0 + dist / V + 0.5 * smooth_noise(rng, pd, 60)
    jumps = []
    for side in (-1, 1):
        end = 0 if side < 0 else G.length
        for _ in range(2):
            ds = rng.uniform(220, abs(end - d0) - 120)
            ps = d0 + side * ds
            t_nat = T0 + ds / V
            ts = t_nat - rng.uniform(2.0, 3.5)
            jumps.append((ps, ts))
            t_ign = np.minimum(t_ign, ts + np.abs(pd - ps) / V)
    burn = 7 + 1.5 * smooth_noise(rng, pd, 80)
    fl = Flicker(rng, G.N, 2, 9)
    tw = Flicker(rng, G.N, 0.5, 3)
    heat_map = colormap([(0, (0, 0, 0)), (0.1, (0.04, 0, 0)), (0.3, (0.25, 0.01, 0)), (0.5, (0.7, 0.05, 0)),
                         (0.7, (1, 0.17, 0)), (0.9, (1, 0.38, 0.02)), (1.15, (1, 0.75, 0.3))])
    # ghost fire: both ends to porch centre, arriving together at T2 + 12
    T2 = 44.0
    t2 = np.where(pd < d0, T2 + pd / d0 * 12, T2 + (G.length - pd) / (G.length - d0) * 12)
    blue_head, blue_tail = hexc('#a0f0ff'), hexc('#0830ff')
    centre = np.abs(pd - d0) < 8

    for f in range(len(out)):
        t = f * DT
        fr = out[f]
        tau = t - t_ign
        rise = smoothstep(0, 0.6, tau)
        core = 1 + 0.25 * np.exp(-np.clip(tau, 0, None) / 0.8)
        fade = smoothstep(burn, burn + 3, tau)
        tongues = 0.5 + 0.5 * np.sin(pd * 0.045 - 5.3 * t + 2 * np.sin(pd * 0.013 + t))
        flick = 0.45 + 0.35 * (0.5 + 0.5 * fl(t)) + 0.3 * tongues
        heat = rise * (1 - fade) * core * flick
        emb = fade * np.exp(-np.clip(tau - burn - 3, 0, None) / 5) * np.clip(tw(t), 0, 1) ** 2
        heat = heat + 0.45 * emb
        heat *= 1 - smoothstep(-0.2, 0.3, t - t2)          # ghost fire extinguishes it
        fr += heat_map(heat)

        if 1.8 < t < T0 + 0.3:                                # match strike
            sp = rng.random(G.N) < 0.5
            fr[centre & sp] += PALE * rng.uniform(0.3, 1.0)
        for ps, ts in jumps:                                  # flying embers
            if ts - 0.6 < t < ts:
                front = d0 + np.sign(ps - d0) * V * max(0, ts - 0.6 - T0)
                p = lerp(front, ps, (t - (ts - 0.6)) / 0.6)
                fr += light(PALE, np.clip(1 - np.abs(pd - p) / 10, 0, 1))

        tau2 = t - t2
        head = np.exp(-(tau2 / 0.18) ** 2) * (tau2 > -0.5)
        tail = np.where(tau2 > 0, 0.55 * np.exp(-tau2 / 1.0) * (0.8 + 0.2 * fl(t)), 0)
        glow = np.where(tau2 > 0, 0.16 * np.exp(-tau2 / 6), 0)
        fr += light(blue_head, head) + light(blue_tail, tail) + light(PURPLE, glow)

        if t >= T2 + 12:                                      # detonation on the porch
            tb = t - (T2 + 12)
            ring = np.exp(-((dist - tb * 900) / 70) ** 2) * np.exp(-tb / 1.5)
            fr += light(WHITE, ring + 0.9 * np.exp(-tb / 0.25))
            fr += light(PURPLE, 0.3 * np.exp(-(tb - 0.5) / 2.5) * (tb > 0.3))
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A brushfire in A Phrygian at 100 BPM (beat 0 is the ignition), all acoustic: the match, a crackle made of one grain
# per burning pixel (so it follows the fire front around the house and thins as it burns out), a roar under it, and
# big ethnic drums whose pattern grows bar by bar with how much of the roof is alight. Trombones carry the tune; each
# corner the fire turns gets a cymbal swell and a low horn; each ember that jumps ahead whistles across and pops where
# it lands. When the fire is out the band goes cold: the score turns electronic, a tritone away (D# against A), and the
# blue fronts race in from both ends as rising tremolo strings and an accelerating drum pair that meet in the porch
# blast. Everything is panned to where it happens on the house as seen from the street.

V, T0, T2, D = 70.0, 3.0, 44.0, 64.0        # as in render(): fire speed, ignition, ghost start, length
TG = T2 + 12                                # the ghost fronts meet on the porch and detonate
BEAT = 0.6                                  # 100 BPM
BAR = 4 * BEAT
FIRE_CHORDS = ['Am', 'Am', 'Bb', 'Am', 'Gm', 'Dm', 'Bb', 'A', 'Am', 'Bb', 'Am', 'Am']   # bar k starts T0 + k * BAR
ROOTS = {'Am': 45, 'Bb': 46, 'Gm': 43, 'Dm': 50, 'A': 45}
TRIAD = {'Am': (57, 60, 64), 'Bb': (58, 62, 65), 'Gm': (55, 58, 62), 'Dm': (57, 62, 65), 'A': (57, 61, 64)}
OSTINATO = [0, 0, 12, 0, 7, 0, 12, 10]      # cello eighths over each bar's root
DRUM_LEVEL = [1, 2, 2, 3, 4, 4, 4, 4, 3, 2, 2, 1]
PATTERN = {                                 # sixteenth -> drum: M big mallet, H hand, h soft hand, K rim click
    1: {0: 'M'},
    2: {0: 'M', 8: 'M', 14: 'h'},
    3: {0: 'M', 4: 'K', 6: 'H', 8: 'M', 11: 'h', 12: 'K', 14: 'H'},
    4: {0: 'M', 3: 'h', 4: 'K', 6: 'H', 8: 'M', 10: 'H', 11: 'h', 12: 'K', 14: 'M', 15: 'H'},
}
THEME = [                                   # trombones: (bar, beat, note, beats)
    (3, 0, 'A3', 2), (3, 2, 'Bb3', 1), (3, 3, 'A3', 1),
    (4, 0, 'G3', 1), (4, 1, 'F3', 1), (4, 2, 'D3', 2),
    (5, 0, 'F3', 1), (5, 1, 'G3', 1), (5, 2, 'A3', 1), (5, 3, 'C4', 1),
    (6, 0, 'D4', 3), (6, 3, 'C4', 0.5), (6, 3.5, 'Bb3', 0.5),
    (7, 0, 'C#4', 2), (7, 2, 'A3', 2),
    (8, 0, 'E3', 4),
]
GHOST_CHORD = (51, 54, 57, 61)              # D#m7b5: the cold chord, a tritone from the fire's A


def fire_plan(G, seed=2):
    """The fire's timetable, drawn from the same generator in the same order as render(): per-pixel ignition, the
    ember jumps (landing, time, where the front was when it left), burn length and the ghost arrival."""
    rng = np.random.default_rng(seed)
    pd = G.pd
    d0 = pd[porch_center(G)]
    t_ign = T0 + np.abs(pd - d0) / V + 0.5 * smooth_noise(rng, pd, 60)
    jumps = []
    for side in (-1, 1):
        end = 0 if side < 0 else G.length
        for _ in range(2):
            ds = rng.uniform(220, abs(end - d0) - 120)
            ps = d0 + side * ds
            ts = T0 + ds / V - rng.uniform(2.0, 3.5)
            jumps.append((ps, ts, d0 + side * V * max(0, ts - 0.6 - T0)))
            t_ign = np.minimum(t_ign, ts + np.abs(pd - ps) / V)
    burn = 7 + 1.5 * smooth_noise(rng, pd, 80)
    t2 = np.where(pd < d0, T2 + pd / d0 * 12, T2 + (G.length - pd) / (G.length - d0) * 12)
    return d0, t_ign, jumps, burn, t2


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    rng = np.random.default_rng(22)
    nS = M.n
    tune = -12                              # these VSCO2 files are named an octave below where they sound
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=tune)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=tune)
    cello = M.sampler('Strings/Cello Section/spic/*.wav', tune=tune)
    cb = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=tune)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=tune)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=tune)
    vlatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=tune)
    vpizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=tune)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=tune)
    glock = M.sampler('Percussion/Glock/*.wav', tune=tune)
    big = M.hits('VSCO 1 Percussion/drums/other/ethnic/giant/mallet/*_f*.wav')
    hand = M.hits('VSCO 1 Percussion/drums/other/ethnic/giant/hand/*_hit_f*.wav')
    hand_s = M.hits('VSCO 1 Percussion/drums/other/ethnic/giant/hand/*_hit_[mp]*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/other/ethnic/giant/EthnicLargeStick_rimshot_*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_m[fp]_*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    gong = M.hits('Percussion/gongHit_fff.wav')
    scrape = M.hits('Percussion/gongscrape_pp.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Short_v1.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_fff_*.wav')

    for name, gain, rev in (('crackle', 0.4, 0.05), ('roar', 0.3, 0.1), ('drums', 0.42, 0.16), ('low', 0.3, 0.1),
                            ('brass', 0.3, 0.25), ('strings', 0.3, 0.25), ('metal', 0.35, 0.3), ('fx', 0.4, 0.2),
                            ('pad', 0.3, 0.45)):
        M.bus(name, gain=gain, reverb=rev)

    d0, t_ign, jumps, burn, t2 = fire_plan(G)
    pd, L = G.pd, G.length
    order = np.argsort(pd)
    xs, ds = G.pos[order, 0], pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    pans = pan_at(pd)
    gl, gr = np.cos((pans + 1) * np.pi / 4) * np.sqrt(2), np.sin((pans + 1) * np.pi / 4) * np.sqrt(2)

    def place(bus, sig, t0, times, ps, gain=1.0):
        """Add sig at t0 with a pan that moves through (absolute times, pans)."""
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.interp(tt, times, ps) + 1) * np.pi / 4
        M.add(bus, sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)]), t0, gain)

    def noise(seconds, lo, hi, seed):       # band-limited noise by FFT, unit RMS
        k = int(seconds * SR)
        X = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, k))
        f = np.fft.rfftfreq(k, 1 / SR)
        X *= (f > lo) * (f < hi) / np.sqrt(np.maximum(f, lo) / lo)
        y = np.fft.irfft(X, k)
        return y / (np.sqrt((y ** 2).mean()) + 1e-12)

    def bar(k, beat=0.0):
        return T0 + k * BAR + beat * BEAT

    # ---- heat of every pixel on a 25 ms grid, the same envelope shape as render() ----
    dt = 0.025
    tg = np.arange(0, D, dt)
    tau = tg[:, None] - t_ign[None, :]
    fade = smoothstep(burn, burn + 3, tau)
    flame = smoothstep(0, 0.6, tau) * (1 - fade)
    ember = fade * np.exp(-np.clip(tau - burn - 3, 0, None) / 5)
    out = 1 - smoothstep(-0.2, 0.3, tg[:, None] - t2[None, :])
    flame, ember = flame * out, ember * out
    lit = flame.mean(1)                     # fraction of the house on fire

    def lit_at(t):
        return float(np.interp(t, tg, lit))

    # ---- crackle: one grain per pop, per pixel, at its own place on the house ----
    lam = (2.6 * flame + 0.5 * ember) * dt
    cnt = rng.poisson(lam)
    fi, pi = np.nonzero(cnt)
    times = tg[fi] + rng.uniform(0, dt, len(fi))
    amps = (0.25 + rng.exponential(0.5, len(fi))) * (0.4 + 0.6 * flame[fi, pi] + 0.3 * ember[fi, pi])
    pix = pi
    times = np.concatenate([times, t_ign])  # every pixel bursts as the front reaches it
    amps = np.concatenate([amps, rng.uniform(1.2, 1.8, G.N)])
    pix = np.concatenate([pix, np.arange(G.N)])
    sp = np.arange(int(1.8 / dt), int((T0 + 0.3) / dt))   # match sparks on the porch centre
    st = np.repeat(tg[sp], 2) + rng.uniform(0, dt, 2 * len(sp))
    times = np.concatenate([times, st])
    amps = np.concatenate([amps, rng.uniform(0.3, 1.0, len(st))])
    pix = np.concatenate([pix, np.full(len(st), porch_center(G))])
    for ps, ts, _ in jumps:                 # the landing ember spits
        k = int(np.argmin(np.abs(pd - ps)))
        tl = ts + rng.exponential(0.08, 14)
        times = np.concatenate([times, tl])
        amps = np.concatenate([amps, rng.uniform(1.0, 2.2, 14)])
        pix = np.concatenate([pix, np.full(14, k)])
    popish = rng.random(len(times)) < 0.18
    imp = np.zeros((2, 2, nS))
    s = np.clip((times * SR).astype(int), 0, nS - 1)
    for j, m in enumerate((~popish, popish)):
        np.add.at(imp[j, 0], s[m], amps[m] * gl[pix[m]])
        np.add.at(imp[j, 1], s[m], amps[m] * gr[pix[m]])
    kt = np.arange(int(0.02 * SR)) / SR
    knoise = np.random.default_rng(5).normal(0, 1, len(kt))
    tick = np.diff(np.concatenate([[0], knoise * np.exp(-kt / 0.0012)]))
    pop = np.convolve(knoise * np.exp(-kt / 0.006), np.ones(6) / 6, 'same')
    nf = 1 << int(np.ceil(np.log2(nS + len(kt))))
    crack = np.zeros((2, nS))
    for j, kern in enumerate((tick / np.abs(tick).max(), pop / np.abs(pop).max() * 0.7)):
        K = np.fft.rfft(kern, nf)
        crack += np.fft.irfft(np.fft.rfft(imp[j], nf) * K, nf)[:, :nS]
    M.add('crackle', crack * 0.35, 0.0)

    # ---- roar: low noise, each side as loud as the fire on that side ----
    ts_ = np.arange(nS) / SR
    roar = np.vstack([noise(nS / SR, 40, 700, 11), noise(nS / SR, 40, 700, 12)])
    side = np.vstack([(flame * gl).mean(1), (flame * gr).mean(1)])
    roar *= np.vstack([np.interp(ts_, tg, side[0]), np.interp(ts_, tg, side[1])])
    M.add('roar', roar * 0.5, 0.0)

    # ---- 0-3: darkness, then the match: scratch, flare, the fire catching ----
    pc = float(pan_at(d0))
    M.add('fx', noise(6.0, 100, 900, 3)[None, :].repeat(2, 0) * np.linspace(0, 1, int(6 * SR)) ** 3 * 0.004, 0.0)
    k = int(0.17 * SR)
    rasp = np.repeat(rng.uniform(0.2, 1.0, k // 240 + 1), 240)[:k]
    scratch = noise(0.17, 1800, 9000, 4) * rasp * np.exp(-np.arange(k) / SR / 0.09)
    M.add('fx', np.vstack([scratch, scratch]) * 0.22, 1.8, 1.0, pc)
    k = int(1.6 * SR)
    te = np.arange(k) / SR
    flare = noise(1.6, 900, 7000, 6) * np.clip(te / 0.05, 0, 1) * np.exp(-te / 0.7)
    M.add('fx', np.vstack([flare, flare]) * 0.12, 1.85, 1.0, pc)
    M.add('fx', whoosh(1.1, 70, 900, 0.6, seed=8), T0 - 0.3, 0.9, pc)
    M.add('drums', hand_s.play(90), T0 + 0.1, 0.8, pc)
    M.add('low', tuba.play(n('A1'), 80, dur=2.2, release=0.8), T0 + 0.1, 0.8)

    # ---- 3-31: the fire. Drums grow with it, cellos drive, trombones sing, the corners and embers land ----
    for b, c in enumerate(FIRE_CHORDS):
        lvl = DRUM_LEVEL[b]
        for step, kind in PATTERN[lvl].items():
            t = bar(b) + step * BEAT / 4
            v = int(45 + 75 * min(1.0, lit_at(t) / 0.55))
            p = 0.25 * np.sin(1.7 * step)
            if kind == 'M':
                M.add('drums', big.play(v), t, 1.0, p)
            elif kind == 'H':
                M.add('drums', hand.play(v - 5), t, 0.8, p)
            elif kind == 'h':
                M.add('drums', hand_s.play(v - 15), t, 0.6, p)
            else:
                M.add('drums', rim.play(v - 10), t, 0.5, p)
        if lvl == 4:
            for e in range(16):
                M.add('drums', tenor.play(60 + 20 * (e % 4 == 0)), bar(b) + e * BEAT / 4, 0.35, -0.3)
            M.add('drums', timp.play(110, pitch=-3), bar(b), 0.6)
        if b == 7:                          # fill into the turn
            for e in range(4):
                M.add('drums', big.play(100 + 6 * e), bar(b, 3) + e * BEAT / 4, 0.8, -0.4 + 0.27 * e)
        if b >= 1:                          # cello ostinato from the first corners on
            vel = int(45 + 70 * min(1.0, lit_at(bar(b)) / 0.55))
            for e, off in enumerate(OSTINATO):
                t = bar(b, e / 2)
                M.add('low', cello.play(ROOTS[c] + off, vel, dur=0.25), t, 0.7, -0.25)
                if e % 2 == 0 and b >= 3:
                    M.add('low', cb.play(ROOTS[c] - 12, vel, dur=0.5), t, 0.8, 0.0)
        if 4 <= b <= 7:                     # violins shimmer over the peak
            for m in TRIAD[c]:
                M.add('strings', vtrem.play(m + 12, 80, dur=BAR, release=0.3), bar(b), 0.5, 0.3)
    for b0, beat, m, beats in THEME:
        t = bar(b0, beat)
        v = int(60 + 45 * min(1.0, lit_at(t) / 0.55))
        M.add('brass', tbn.play(n(m), v, dur=beats * BEAT * 0.95, release=0.15), t, 1.0, 0.15)
        if 5 <= b0 <= 7:
            M.add('brass', horn.play(n(m) + 12, v - 10, dur=beats * BEAT * 0.95, release=0.15), t, 0.7, -0.15)
    M.add('drums', big.play(124), bar(8), 1.0)        # the turn: the fire has peaked
    M.add('metal', crash.play(110), bar(8), 0.8)
    M.add('low', tuba.play(n('A1'), 110, dur=2.0, release=1.0), bar(8), 1.0)

    segs = G.path_segments()                # the corners: the fire turns onto the next run of roof
    corners = []
    for (_, a), (nm, b2) in zip(segs[:-1], segs[1:]):
        edge = (pd[G.path[a]].max() + pd[G.path[b2]].min()) / 2
        new = G.path[b2] if edge > d0 else G.path[a]
        near = new[np.abs(pd[new] - edge) < 30]
        corners.append((float(t_ign[near].min()), edge))
    for tc, edge in corners:
        p = float(pan_at(edge))
        M.add('metal', swell.play(80, dur=1.75), tc - 1.5, 0.6, p)
        M.add('drums', big.play(118), tc, 1.0, p)
        c = FIRE_CHORDS[min(11, int((tc - T0) // BAR))]
        M.add('brass', horn.play(ROOTS[c], 100, dur=1.2, release=0.4), tc, 0.9, p)

    for ps, ts, front in jumps:             # an ember whistles ahead of the front and pops where it lands
        place('fx', whoosh(0.6, 700, 5200, 0.5, seed=int(ts * 10)), ts - 0.6, [ts - 0.6, ts],
              [float(pan_at(front)), float(pan_at(ps))], 0.8)
        p = float(pan_at(ps))
        M.add('drums', rim.play(115), ts, 0.8, p)
        c = FIRE_CHORDS[min(11, int((ts - T0) // BAR))]
        M.add('strings', vpizz.play(TRIAD[c][2] + 12, 110), ts, 0.9, p)
        M.add('strings', vpizz.play(TRIAD[c][0] + 24, 100), ts + 0.1, 0.7, p)

    # ---- 31-44: the house is dark; the last embers tick; the cold creeps in ----
    t_out = float((t_ign + burn + 3).max())
    M.add('low', ctrem.play(n('A2'), 50, dur=7.0, release=2.5), bar(11), 0.5, -0.2)
    M.add('metal', scrape.play(80), t_out, 0.4, float(pan_at(pd[np.argmax(t_ign + burn)])))
    pad = [(36.0, 51, 22, 8.0), (36.0, 57, 18, 8.0)]
    for i, (t, m) in enumerate(((38.0, 87), (40.4, 81), (42.2, 85))):
        M.add('metal', glock.play(m, 50 + 8 * i), t, 0.3, (-0.5, 0.5, 0.0)[i])

    # ---- 44-56: blue fronts race in from both ends; rising tremolo, accelerating drums; they meet on the porch ----
    pad += [(T2, m, 50, 12.0) for m in GHOST_CHORD]

    def front(sgn, t):                      # where each ghost head is
        u = np.clip((t - T2) / 12, 0, 1)
        return u * d0 if sgn < 0 else L - u * (L - d0)

    gt = np.linspace(T2 - 1, TG, 60)
    for sgn, start, seed in ((-1, 63, 31), (1, 57, 32)):
        k = int((TG - T2 + 0.3) * SR)
        te = np.arange(k) / SR
        hiss = noise(k / SR, 3000, 12000, seed) * (0.25 + 0.75 * (te / 12) ** 2) * np.clip(te / 0.3, 0, 1)
        hiss[int((TG - 0.2 - T2) * SR):] = 0
        place('fx', np.vstack([hiss, hiss]) * 0.035, T2, gt, pan_at(front(sgn, gt)))
        strand = np.zeros((2, int(14 * SR)))
        for i in range(12):
            a = (vtrem if sgn < 0 else vlatrem).play(start + 2 * i, 50 + 5 * i, dur=1.15 if i < 11 else 0.85, release=0.2)
            s0 = int(i * SR)
            strand[:, s0:s0 + a.shape[1]] += a[:, :strand.shape[1] - s0]
        place('strings', strand, T2, gt, pan_at(front(sgn, gt)), 0.6)
    for edge in [e for _, e in corners]:    # each head passes a corner: a cold glint
        sgn = -1 if edge < d0 else 1
        tc = float(np.interp(edge, pd[np.argsort(pd)], t2[np.argsort(pd)]))
        M.add('metal', glock.play(87 if sgn < 0 else 81, 100), tc, 0.8, float(pan_at(edge)))
    ph, i = 0.0, 0
    for t in np.arange(T2, TG - 0.3, 0.005):   # drum pair, rate 1.2/s doubling every 4 s, alternating fronts
        ph += 1.2 * 2 ** (3 * (t - T2) / 12) * 0.005
        if ph >= 1:
            ph -= 1
            sgn = -1 if i % 2 == 0 else 1
            p = float(pan_at(front(sgn, t)))
            u = (t - T2) / 12
            v = int(40 + 70 * u)
            M.add('drums', (big if u > 0.5 else hand).play(v), t, 0.8, p)
            if i % 2 == 0 or u > 0.6:
                M.add('low', cb.play(39 if sgn < 0 else 45, v, dur=0.3), t, 0.6, p)
            i += 1
    M.add('drums', troll.play(100, dur=1.4), TG - 1.6, 0.5)
    M.add('metal', swell.play(100, dur=1.3), TG - 1.5, 0.7, pc)

    # ---- 56: detonation; the ring blows out to both ends and the purple glow dies away ----
    M.add('drums', big.play(127), TG, 1.6, pc)
    M.add('drums', bd.play(127), TG, 1.6, pc)
    M.add('drums', timp.play(127, pitch=-3), TG, 0.8)
    M.add('metal', gong.play(127), TG, 1.3, pc)
    M.add('metal', crash.play(127), TG, 0.9, pc)
    M.add('low', tuba.play(n('A1'), 127, dur=3.5, release=2.0), TG, 1.6)
    M.add('low', cb.play(n('A1'), 127), TG, 0.8)
    for m in ('A2', 'E3', 'A3'):
        M.add('brass', tbn.play(n(m), 120, dur=2.5, release=1.5), TG, 1.1, 0.0)
    M.add('strings', vtrem.play(n('D#6'), 90, dur=4.0, release=2.0), TG + 0.3, 0.6, 0.0)
    for sgn in (-1, 1):
        reach = (d0 if sgn < 0 else L - d0) / 900
        place('fx', whoosh(reach + 0.4, 2500, 300, 0.6, seed=50 + sgn), TG, [TG, TG + reach],
              [pc, float(pan_at(0 if sgn < 0 else L))], 0.9)
    pad += [(TG, 45, 90, 4.5), (TG, 52, 80, 4.5), (TG, 63, 70, 5.0)]

    M.add('pad', M.synth('Pads/Ghost Pad').render(pad, D), 0.0)
