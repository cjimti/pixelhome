"""The Big Game: Football on the roofline, with the porch as the sky. A pass from the Left wing climbs
the Porch Left, hangs at its apex across the Porch Front (far away and high in the street view) and
drops down the Porch Right to the Right wing, its shadow sliding along the wing fronts below. Play
one is overthrown out the free end. Play two is a run that ends in a pile-up at the porch corner and
a fumble that bounces along the porch. Play three: the quarterback scrambles all the way to the back
of the Side and throws the Hail Mary down the entire roof. Touchdown, and the whole house does the wave."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG05'
TITLE = 'The Big Game'
KIND = 'show'
DESCRIPTION = ('Football on the roof, with the porch as the sky: passes arc up and over the porch, a fumble bounces '
               'along it, and a Hail Mary from the back of the house ends in a touchdown and a stadium wave.')

HOME = hexc('#ff8a18')         # amber jerseys
AWAY = hexc('#c0102a')         # cranberry jerseys
BALL = hexc('#ff9030')
WARM = hexc('#ffc27a')
GOLD = hexc('#ffb000')
BROWN = hexc('#5a1c04')
D = 60.0
SEED = 25

# the three plays: quarterbacks, the runner and the balls as (time, path distance) waypoints. Each play lines up at
# its first waypoint and is snapped at the second.
QB1 = [(2.5, 700), (5.0, 700), (5.8, 640), (7.0, 640), (8.0, 690), (12.5, 690)]
BALL1 = [(5.0, 700), (5.8, 645), (6.0, 650), (6.5, 892), (7.6, 1311), (9.1, 1660), (9.9, 2033), (10.4, 2290),
         (11.4, 2600)]
RUNNER2 = [(14.0, 700), (16.0, 700), (17.0, 820), (17.4, 800), (18.2, 1000), (18.6, 980), (19.3, 1282), (21.5, 1282),
           (23.0, 1505), (27.0, 1505)]
QB3 = [(29.5, 760), (32.5, 760), (33.2, 640), (33.8, 690), (34.5, 492), (35.0, 520), (36.2, 120), (36.6, 150),
       (37.0, 70), (40, 70)]
BALL3 = [(32.5, 760), (37.0, 72), (37.15, 80), (38.0, 491), (38.9, 892), (40.0, 1311), (41.0, 1660), (41.9, 2033),
         (42.6, 2445), (43.0, 2470), (50.0, 2470)]
TD = 42.6
GROAN = (11.3, 0.7)              # the overthrow's three groans down the Right wing
FLASH = (0.4, 0.75)              # the end zone flashes three times after the touchdown
WAVES = ((2.8, -1), (8.2, 1))    # (seconds after the touchdown, direction): the stadium waves
WAVE_SPEED = 620
EXCITE = [(0, 0.1), (3, 0.1), (19.2, 0.2), (19.6, 0.1), (23.0, 0.25), (24.5, 0.1), (42.6, 0.1), (43.0, 0.3), (55, 0.15),
          (60, 0)]                # how worked up the crowd is


def fumble(rng):
    """The loose ball's bounces after the pile-up, as (time, path distance), ending where it is recovered."""
    hops = [(19.45, 1290)]
    p, tt = 1290.0, 19.45
    for k in range(7):
        tt += 0.42 - 0.035 * k
        p += rng.uniform(-30, 70) * (1 - k / 9)
        hops.append((tt, p))
    hops.append((22.9, 1505))
    return hops


def track(pts, F, sigma=0.12):
    """Per-frame path position from (time, pd) waypoints, linear then smoothed. NaN outside."""
    t = np.arange(F) * DT
    ts = np.array([p[0] for p in pts], float)
    xs = np.array([p[1] for p in pts], float)
    x = np.interp(t, ts, xs)
    k = max(1, int(sigma / DT * 3))
    w = np.exp(-0.5 * (np.arange(-k, k + 1) * DT / sigma) ** 2)
    w /= w.sum()
    x = np.convolve(np.concatenate([np.full(k, x[0]), x, np.full(k, x[-1])]), w, 'valid')
    x[(t < ts[0]) | (t > ts[-1])] = np.nan
    return x


def height(x):
    """How 'high' the ball is: the porch sides climb, the Porch Front is the top of the arc."""
    return float(np.clip(np.interp(x, [892, 1311, 1660, 2033], [0, 1, 1, 0]), 0, 1))


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    X = G.pos[G.path, 0]
    wingf = ((pdp > 492) & (pdp < 892)) | (pdp > 2036)
    crowd_f = Flicker(rng, n, 0.5, 3.0)

    players = []                      # (colour, waypoints, size)

    def add(col, pts, size=8.0):
        players.append((col, track(pts, F), size, pts[0][0], pts[-1][0]))

    # --- play 1: overthrown ---
    add(HOME, QB1)                                                                                  # QB
    add(HOME, [(2.5, 2180), (6.0, 2180), (9.5, 2330), (10.3, 2350), (11.2, 2470), (12.5, 2480)])    # receiver
    add(AWAY, [(2.5, 2140), (6.0, 2140), (9.8, 2300), (12.5, 2330)])
    add(AWAY, [(2.5, 2250), (6.0, 2250), (10.0, 2390), (12.5, 2420)])
    ball1 = track(BALL1, F, 0.15)

    # --- play 2: the run, the pile-up, the fumble ---
    add(HOME, RUNNER2)                                                                              # runner
    for k, p0 in enumerate((1760, 1860, 1960)):
        add(AWAY, [(14.0, p0), (16.0, p0), (19.25, 1298 + 6 * k), (21.5, 1300 + 9 * k), (23.5, 1330 + 30 * k),
                   (26.0, 1700 + 60 * k)])
    add(HOME, [(14.0, 600), (16.0, 600), (19.2, 1270), (21.6, 1276), (23.4, 1495), (27.0, 1495)])   # blocker
    hops = fumble(rng)
    ball2 = track([(16.0, 700), (19.3, 1282), (19.45, 1290)] + hops[1:] + [(27.0, 1505)], F, 0.08)
    hop_times = np.array([h[0] for h in hops])

    # --- play 3: the Hail Mary ---
    add(HOME, QB3, 9)                                                                               # QB
    add(AWAY, [(29.5, 820), (32.5, 820), (34.0, 650), (35.5, 400), (36.8, 140), (37.3, 110), (40, 110)])
    add(HOME, [(29.5, 2140), (32.5, 2140), (36.0, 2290), (36.6, 2270), (40.0, 2400), (42.6, 2445),
               (43.0, 2470), (50, 2470)], 9)                                                         # receiver
    add(AWAY, [(29.5, 2200), (32.5, 2200), (37.0, 2330), (41.5, 2410), (42.6, 2425), (43.5, 2350),
               (45.0, 2350)])
    ball3 = track(BALL3, F, 0.12)

    def ball_draw(buf, x, t, high):
        spin = 0.75 + 0.25 * np.cos(2 * np.pi * 7 * t)
        size = 6 + 4 * (1 - high)
        buf += light(BALL, (0.85 + 0.15 * (1 - high)) * spin * np.exp(-((pdp - x) / size) ** 2))
        buf += light(WARM, 0.5 * max(0, np.cos(2 * np.pi * 7 * t)) ** 8 * np.exp(-((pdp - x) / 3) ** 2))

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        excite = keys(t, EXCITE)
        crowd = (0.5 + 0.5 * crowd_f(t)) * excite
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.12), (56, 0.12), (60, 0)]) + 0.6 * crowd)
        for col, tr, size, ta, tb in players:
            x = tr[f]
            if np.isnan(x):
                continue
            fade = smoothstep(ta, ta + 0.6, t) * (1 - smoothstep(tb - 0.8, tb, t))
            buf += light(col, 0.85 * fade * np.exp(-((pdp - x) / size) ** 2))
        # balls and their shadow on the wing fronts
        for tr, t0, t1 in ((ball1, 5.95, 11.4), (ball2, 19.45, 27), (ball3, 37.1, 42.6)):
            x = tr[f]
            if np.isnan(x) or not (t0 <= t <= t1 + 0.01):
                continue
            hi = height(x)
            ball_draw(buf, x, t, hi)
            for k in range(1, 8):                                   # motion blur behind the ball
                xk = tr[max(0, f - k)]
                if not np.isnan(xk) and t - k * DT >= t0:
                    buf += light(BALL, 0.45 * (1 - k / 8) * np.exp(-((pdp - xk) / 5) ** 2))
            if tr is not ball2:
                xa = X[int(np.argmin(np.abs(pdp - tr[nframes(t0)])))]
                xb = X[int(np.argmin(np.abs(pdp - min(tr[nframes(t1) - 1], 2511))))]
                xs = xa + (xb - xa) * (t - t0) / (t1 - t0)
                buf += light(BROWN, 0.6 * hi * np.exp(-((X - xs) / 18) ** 2) * wingf)
        # play 1: the groan, a sad trombone down the Right wing
        if 11.0 < t < 14.0:
            for k in range(3):
                u = t - GROAN[0] - GROAN[1] * k
                if 0 < u < 0.9:
                    buf += light(AWAY, 0.3 * np.sin(np.pi * u / 0.9) * (pdp > 2036) * (1 - 0.25 * k))
        # play 2: the pile-up jiggles and sparks; each fumble bounce flashes where it lands
        if 19.2 < t < 21.6:
            j = rng.normal(0, 4, 1)[0]
            buf += light(WARM, 0.45 * np.exp(-((pdp - 1290 - j) / 14) ** 2) * (0.5 + 0.5 * np.sin(40 * t)))
        for th in hop_times[1:]:
            u = t - th
            if 0 <= u < 0.25:
                buf += light(WARM, 0.7 * np.exp(-u / 0.07) * np.exp(-((pdp - ball2[f]) / 9) ** 2))
        if 22.9 < t < 25:
            buf += light(HOME, 0.5 * np.exp(-(t - 22.9) / 0.6) * ((pdp > 492) & (pdp < 1311)))
        # play 3: TOUCHDOWN
        u = t - TD
        if u >= 0:
            catch = np.exp(-u / 0.25)
            buf += light(WARM, 0.9 * catch * np.exp(-((pdp - 2450) / 20) ** 2))
            ez = (pdp > 2380)
            for k in range(3):
                uk = u - FLASH[0] - FLASH[1] * k
                if 0 < uk < 0.7:
                    buf += light(GOLD, 0.85 * np.exp(-uk / 0.25) * ez)
            # the wave: every pixel is a fan who stands up when the wave reaches them, then sits slowly
            for w0, direction in WAVES:
                front = (u - w0) * WAVE_SPEED
                pos = (G.length - pdp) if direction < 0 else pdp
                lag = front - pos
                stand = np.where(lag > 0, np.exp(-lag / 320), np.exp(-(lag / 35) ** 2))
                shirt = np.where(((pdp // 32) % 2 == 0)[:, None], HOME, GOLD)
                if -1 < u - w0 < 6:
                    buf += light(1.0, stand * (0.8 if direction < 0 else 0.6)) * shirt
            buf += light(HOME, 0.2 * smoothstep(13, 15, u) * keys(t, [(55, 1), (60, 0)]))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A marching band in Bb at 120 BPM with an original fight song: trumpets on the tune, tuba and trombones oom-pah,
# marching snare and bass drum. Each play lines up on a bass drum, counts "hut, hut" on the tenor drums and is snapped
# on a cymbal. Balls in the air are a slide whistle that climbs with the ball's height and follows it across the house;
# the overthrow gets three sad trombones, the pile-up a timpani rumble, every fumble bounce a xylophone note, the Hail
# Mary a long crescendo and the touchdown the whole band. The stadium waves get brass sweeps that run with the wave.
# The crowd is filtered noise that follows the lights' excitement; the referee is a synthesized pea whistle.

BEAT = 0.5
SONG = ['Bb', 'Eb', 'F7', 'Bb', 'Bb', 'Eb', 'F7', 'Bb']
FIGHT = [  # per bar: (beat, note, beats)
    [(0, 'F4', 1), (1, 'Bb4', 1), (2, 'D5', 1.5), (3.5, 'Bb4', 0.5)],
    [(0, 'Eb5', 1.5), (1.5, 'D5', 0.5), (2, 'C5', 1), (3, 'Bb4', 1)],
    [(0, 'A4', 1), (1, 'C5', 1), (2, 'F5', 1.5), (3.5, 'Eb5', 0.5)],
    [(0, 'D5', 2), (2, 'Bb4', 1)],
    [(0, 'F4', 0.5), (0.5, 'F4', 0.5), (1, 'Bb4', 1), (2, 'D5', 1), (3, 'F5', 1)],
    [(0, 'G5', 1.5), (1.5, 'F5', 0.5), (2, 'Eb5', 1), (3, 'G4', 1)],
    [(0, 'F4', 1), (1, 'A4', 1), (2, 'C5', 1), (3, 'Eb5', 1)],
    [(0, 'D5', 1), (1, 'Bb4', 1), (2, 'Bb4', 1)]]
CHORD = {'Bb': ('D4', 'F4', 'Bb4'), 'Eb': ('Eb4', 'G4', 'Bb4'), 'F7': ('Eb4', 'F4', 'A4')}
ROOT = {'Bb': ('Bb1', 'F2'), 'Eb': ('Eb2', 'Bb1'), 'F7': ('F2', 'C2')}
TONES = {'Bb': (46, 50, 53), 'Eb': (51, 55, 58), 'F7': (53, 57, 60, 63)}     # chord tones for the wave sweeps


def score(M, G):
    from pixelhome.audio import note, slide, whoosh, SR
    n = note
    F = nframes(D)
    L = G.length
    rng = np.random.default_rng(SEED)       # the same draws as render(): the crowd flicker, then the fumble
    Flicker(rng, G.N, 0.5, 3.0)
    hops = fumble(rng)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_l = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    bone_l = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fm]*.wav')
    snare_g = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_p*.wav')
    rim = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_rimshot*.wav')
    roll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f*_[12].wav')
    bd_big = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff*.wav')
    tenor = M.hits('VSCO 1 Percussion/drums/tenor/tenor_lower/tenor_f*.wav')
    clash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*_v5_*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')

    for name, gain, rev in (('melody', 0.4, 0.2), ('band', 0.3, 0.18), ('bass', 0.5, 0.08), ('drums', 0.45, 0.12),
                            ('perc', 0.5, 0.12), ('fx', 0.16, 0.2), ('crowd', 0.1, 0.3), ('ref', 0.05, 0.2),
                            ('bells', 0.3, 0.25)):
        M.bus(name, gain=0.9 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def moving(sig, t0, ts, ps):            # constant-power pan that follows (time, pan) points
        tt = t0 + np.arange(sig.shape[1]) / SR
        a = (np.interp(tt, ts, ps) + 1) * np.pi / 4
        return sig * np.vstack([np.cos(a), np.sin(a)]) * np.sqrt(2)

    def whistle(t0, ts, fs, amp=0.35):      # a slide whistle that follows a frequency curve, from t0 to ts[-1]
        tt = np.arange(int((ts[-1] - t0) * SR)) / SR + t0
        f = np.interp(tt, ts, fs)
        ph = 2 * np.pi * np.cumsum(f) / SR
        u = tt - t0
        env = np.clip(u / 0.05, 0, 1) * np.clip((ts[-1] - tt) / 0.3, 0, 1)
        breath = np.convolve(M.rng.normal(0, 1, len(tt)), np.ones(24) / 24, 'same') * 0.08
        sig = amp * env * (np.sin(ph) + 0.12 * np.sin(2 * ph) + breath * (1 + np.sin(ph)))
        return np.vstack([sig, sig])

    def flight(waypoints, sigma, t0, t1, lo, span):     # whistle for a ball in the air, panned with the ball
        x = track(waypoints, F, sigma)
        fr = np.arange(nframes(t0), min(F, nframes(t1)))
        ts = fr * DT
        xb = np.nan_to_num(x[fr], nan=L)
        h = np.array([height(v) for v in xb])
        fs = lo * 2 ** (span * h + 0.25 * (ts - t0) / (t1 - t0))
        ps = np.array([pan_at(v) for v in xb])
        M.add('fx', moving(whistle(ts[0], ts, fs), ts[0], ts, ps), ts[0])

    def ref(t, dur=0.5, blasts=1):          # pea whistle: a 2.8 kHz tone rattled by the pea
        for b in range(blasts):
            tt = np.arange(int(dur * SR)) / SR
            f = 2800 + 140 * np.sign(np.sin(2 * np.pi * 32 * tt))
            ph = 2 * np.pi * np.cumsum(f) / SR
            env = np.clip(tt / 0.02, 0, 1) * np.clip((dur - tt) / 0.05, 0, 1)
            sig = env * (np.sin(ph) + 0.3 * np.sin(2 * ph))
            M.add('ref', np.vstack([sig, sig]), t + b * (dur + 0.12), 1.0, 0.0)

    # ---- the crowd: band-passed noise breathing with the lights' excitement, plus swells for the big moments ----
    N = int(D * SR)
    spec = np.fft.rfft(M.rng.normal(0, 1, (2, N)), axis=1)
    fq = np.fft.rfftfreq(N, 1 / SR)
    spec *= (fq / 350) ** 2 / (1 + (fq / 350) ** 2) / (1 + (fq / 2200) ** 2)
    noise = np.fft.irfft(spec, N, axis=1)
    noise /= np.abs(noise).max()
    tt = np.arange(N) / SR
    babble = 1 + 0.25 * np.sin(2 * np.pi * 1.7 * tt) * np.sin(2 * np.pi * 0.31 * tt + 1)
    tackle, recover, throw = RUNNER2[6][0], hops[-1][0], BALL3[2][0]
    env = np.array([keys(t, EXCITE) for t in tt[::480]]) / 0.3
    ext = np.array([keys(t, [(0, 0), (throw, 0), (TD, 1.4), (TD + 1.5, 0.4), (D, 0.4)]) for t in tt[::480]])
    env = np.interp(tt, tt[::480], 0.35 + env + ext)
    M.add('crowd', noise * babble * env, 0.0)
    M.add('crowd', whoosh(2.0, 1400, 250, 0.9, seed=5), GROAN[0] - 0.2, 1.0, pan_at(2300))     # awww
    M.add('crowd', whoosh(1.6, 300, 1800, 0.9, seed=6), tackle - 0.3, 0.8, pan_at(1290))       # oooh
    M.add('crowd', whoosh(2.5, 400, 2400, 1.0, seed=7), recover - 0.3, 0.9, pan_at(1000))      # yeah!

    # ---- the band ----
    def bar_of(t, t0):
        return int((t - t0) // (4 * BEAT))

    def march(t0, t1, bars, stop=None, vel=100):
        """The fight song from t0, bars by index into FIGHT, with oom-pah and drums; nothing at or after stop."""
        stop = stop if stop is not None else t1
        for i, b in enumerate(bars):
            tb = t0 + 4 * BEAT * i
            c = SONG[b]
            for bt, m, d in FIGHT[b]:
                t = tb + bt * BEAT
                if t >= stop:
                    continue
                M.add('melody', tpt.play(n(m), vel, dur=d * BEAT * 0.85, release=0.08), t, 1.0, 0.05)
                M.add('melody', tpt.play(n(m) - 12, vel - 10, dur=d * BEAT * 0.85, release=0.08), t, 0.5, -0.1)
                M.add('bells', glock.play(n(m) + 12, vel - 20), t, 0.4, 0.2)
            for k in range(4):
                t = tb + k * BEAT
                if t >= stop:
                    continue
                if k % 2 == 0:
                    M.add('bass', tuba.play(n(ROOT[c][k // 2]), vel + 6), t, 1.0, -0.05)
                    M.add('drums', bd.play(vel), t, 0.9, 0.0)
                else:
                    for m in CHORD[c]:
                        M.add('band', bone.play(n(m) - 12, vel - 8, dur=0.2), t, 0.7, -0.25)
                        M.add('band', horn.play(n(m), vel - 20, dur=0.2), t, 0.5, 0.25)
            for e in range(8):              # snare: hit, -, hit, hit | hit, -, hit, hit, accents on the beat
                t = tb + e * BEAT / 2
                if t < stop and e % 4 != 1:
                    M.add('drums', (snare if e % 2 == 0 else snare_g).play(vel if e % 4 == 0 else vel - 25), t,
                          0.7, 0.1)
            if i == 0 and tb < stop:
                M.add('drums', clash.play(vel), tb, 0.5)

    def cadence(t0, t1, vel=90):            # drums alone between plays
        e = 0
        while t0 + e * BEAT / 2 < t1:
            t = t0 + e * BEAT / 2
            if e % 8 in (0, 2, 3, 5, 6):
                M.add('drums', snare.play(vel if e % 4 == 0 else vel - 22), t, 0.7, 0.1)
            if e % 4 == 0:
                M.add('drums', bd.play(vel - 10), t, 0.8)
            e += 1

    def buzz(t0, t1, v0, v1, p=0.1):        # a snare roll in sixteenths, v0 -> v1
        k, nk = 0, int((t1 - t0) / (BEAT / 4))
        while k < nk:
            M.add('drums', snare_g.play(v0 + (v1 - v0) * k / max(1, nk - 1)), t0 + k * BEAT / 4, 0.6, p)
            k += 1

    def lineup(tl, ts):                     # set, hut, hut, snap
        M.add('drums', bd_big.play(105), tl, 0.9)
        for m in ('D4', 'F4', 'Bb4'):
            M.add('band', tpt_l.play(n(m), 96, dur=0.4), tl, 0.6, 0.0)
        buzz(tl + BEAT, ts - 2 * BEAT, 60, 105)
        k = 1
        while tl + k * BEAT < ts:             # the tuba waits on F
            M.add('bass', tuba.play(n('F2'), 84 + 4 * k), tl + k * BEAT, 0.8)
            k += 1
        for k in (2, 1):
            M.add('drums', tenor.play(110), ts - k * BEAT, 0.9, pan_at(700))
        M.add('drums', crash_s.play(110), ts, 0.6)
        M.add('perc', slap.play(100), ts, 0.6, pan_at(700))

    # ---- 0-14: pregame and play one, overthrown ----
    cadence(0.0, QB1[0][0], 104)
    for t, m, d in ((0.0, 'F4', 0.4), (0.5, 'Bb4', 0.4), (1.0, 'D5', 0.4), (1.5, 'F5', 0.9)):   # band takes the field
        M.add('melody', tpt.play(n(m), 108, dur=d), t, 1.0, 0.05)
        M.add('band', bone.play(n(m) - 12, 100, dur=d), t, 0.8, -0.2)
    lineup(QB1[0][0], QB1[1][0])
    march(QB1[1][0], GROAN[0], range(3))
    flight(BALL1, 0.15, BALL1[2][0], BALL1[-1][0], 480, 1.5)
    ref(BALL1[-1][0], 0.55)
    for k, m in enumerate(('Bb3', 'A3', 'Ab3')):                                  # the groan
        t = GROAN[0] + GROAN[1] * k
        if k < 2:
            M.add('melody', bone_l.play(n(m), 100, dur=0.6, release=0.15), t, 1.0, pan_at(2300))
        else:
            M.add('melody', fall.play(n(m), 108), t, 1.0, pan_at(2300))
    M.add('bass', tuba.play(n('F2'), 90), GROAN[0] + 2 * GROAN[1] + 0.9)
    cadence(13.0, RUNNER2[0][0], 80)

    # ---- 14-29: play two, the run, the pile-up and the fumble ----
    lineup(RUNNER2[0][0], RUNNER2[1][0])
    march(RUNNER2[1][0], tackle, (4, 5), stop=tackle)
    for t, x in RUNNER2[2:6]:                                                     # the jukes
        M.add('perc', wood.play(110), t, 0.9, pan_at(x))
        M.add('fx', slide(0.0, 0.18, 700, 1500, 0.2, 0.5), t, 0.6, pan_at(x))
    p = pan_at(1290)
    M.add('drums', bd_big.play(127), tackle, 1.0, p)
    M.add('drums', clash.play(120), tackle, 0.7, p)
    M.add('drums', timp.play(120, pitch=-3), tackle, 0.8, p)
    M.add('perc', slap.play(127), tackle, 0.8, p)
    M.add('drums', troll.play(90, dur=RUNNER2[7][0] - tackle), tackle + 0.1, 0.7, p)
    M.add('perc', ratchet.play(80, dur=1.5), tackle + 0.3, 0.6, p)
    for k, (t, x) in enumerate(hops[1:-1]):                                       # the loose ball
        m = n('Bb5') - [0, 3, 5, 2, 7, 5, 10][k % 7]
        M.add('perc', xylo.play(m, 112 - 5 * k), t, 1.0, pan_at(x))
        M.add('perc', wood.play(100), t, 0.6, pan_at(x))
        M.add('fx', slide(0.0, 0.12, 500, 1100, 0.14, 0.5), t, 0.4, pan_at(x))
    buzz(hops[-2][0] + BEAT / 2, recover, 60, 110, pan_at(1450))                 # it squirts along the porch...
    t = recover                                                                   # recovered: home team ball
    M.add('drums', clash.play(115), t, 0.6, pan_at(1000))
    for m in ('Bb3', 'D4', 'F4', 'Bb4'):
        M.add('melody', tpt_l.play(n(m), 110, dur=0.5, release=0.2), t, 0.6, pan_at(900))
    ref(t + 0.25, 0.4, 2)
    march(np.ceil(recover / BEAT) * BEAT, QB3[0][0] + 1.5, range(4))

    # ---- 29.5-42.6: play three, the scramble and the Hail Mary ----
    lineup(QB3[0][0], QB3[1][0])
    t0 = QB3[1][0]
    climb = ['F2', 'Gb2', 'G2', 'Ab2', 'A2']
    e = 0
    while t0 + e * BEAT / 2 < throw:                                              # chase: tuba eighths, climbing
        t = t0 + e * BEAT / 2
        r = n(climb[min(len(climb) - 1, e // 4)])
        M.add('bass', tuba.play(r + (7 if e % 2 else 0), 96), t, 0.9, -0.05)
        M.add('drums', snare_g.play(70 + 2 * e), t, 0.6, 0.1)
        e += 1
    for t, x in QB3[2:9]:                                                         # each cut of the scramble
        M.add('perc', wood.play(110), t, 0.8, pan_at(x))
        M.add('melody', bone.play(n('F3'), 100, dur=0.15), t, 0.7, pan_at(x))
    M.add('perc', rim.play(120), throw, 0.9, pan_at(70))                          # the throw
    M.add('drums', bd_big.play(115), throw, 0.9, pan_at(70))
    flight(BALL3, 0.12, throw, TD, 420, 1.4)
    M.add('drums', troll.play(110, dur=TD - throw), throw, 0.8)
    M.add('drums', roll.play(100, dur=TD - throw), throw + 1.5, 0.5)
    wp = [w for w in BALL3 if throw < w[0] <= TD]                                 # the band climbs with the ball
    for k, (t, x) in enumerate(wp):
        for m in (n('F3') + 2 * k, n('A3') + 2 * k, n('C4') + 2 * k):
            M.add('band', tpt_l.play(m, 80 + 8 * k, dur=t - (wp[k - 1][0] if k else throw), release=0.1),
                  wp[k - 1][0] if k else throw, 0.45, pan_at(x))
        M.add('bass', tuba.play(n('F2'), 90 + 5 * k), t, 1.0)

    # ---- TOUCHDOWN ----
    pz = pan_at(2450)
    M.add('drums', bd_big.play(127), TD, 1.0, pz)
    M.add('drums', clash.play(127), TD, 0.8, pz)
    M.add('drums', timp.play(127), TD, 0.8, pz)
    for m in ('Bb3', 'D4', 'F4', 'Bb4', 'D5'):
        M.add('melody', tpt_l.play(n(m), 120, dur=FLASH[0] - 0.05, release=0.1), TD, 0.6, pz)
    M.add('bass', tuba.play(n('Bb1'), 124), TD)
    ref(TD + 0.05, 1.0)
    for k in range(3):                      # TOUCH - DOWN - !
        t = TD + FLASH[0] + FLASH[1] * k
        M.add('drums', bd_big.play(124), t, 1.0, pz)
        M.add('drums', timp.play(118), t, 0.7, pz)
        M.add('drums', (clash if k == 2 else crash_s).play(118), t, 0.7, pz)
        for m in CHORD['Bb']:
            M.add('melody', tpt.play(n(m) + (12 if k == 2 else 0), 118, dur=0.3), t, 0.6, pz)
        M.add('bass', tuba.play(n('Bb1') + 7 * (k == 1), 120), t)

    # ---- the waves: the fight song, and a brass sweep that runs along with each wave ----
    T5 = np.ceil((TD + FLASH[0] + 2 * FLASH[1] + BEAT) / BEAT) * BEAT
    march(T5, T5 + 8 * 4 * BEAT, (0, 1, 2, 3, 7))
    end = T5 + 5 * 4 * BEAT
    for j, (w0, direction) in enumerate(WAVES):
        for k in range(17):
            pos = L * k / 16
            d = L - pos if direction < 0 else pos
            t = TD + w0 + pos / WAVE_SPEED
            c = SONG[[0, 1, 2, 3, 7][min(4, bar_of(t, T5))]] if t < end else 'Bb'
            asc = sorted(m for m in {r + 12 * o for r in TONES[c] for o in range(-1, 4)} if n('Bb3') <= m <= n('Bb5'))
            m = asc[int(k * (len(asc) - 1) / 16)]
            M.add('band', tpt.play(m, 96 + k + 6 * j, dur=0.3), t, 0.9, pan_at(d))
            M.add('band', bone.play(m - 12, 96 + k + 6 * j, dur=0.3), t, 0.8, pan_at(d))
        tt0 = TD + w0
        tw = np.linspace(tt0, tt0 + L / WAVE_SPEED, 20)
        dw = L - (tw - tt0) * WAVE_SPEED if direction < 0 else (tw - tt0) * WAVE_SPEED
        sw = whoosh(L / WAVE_SPEED + 0.5, 300, 1600, 1.0, seed=20 + j)
        M.add('crowd', moving(sw, tt0, tw, [pan_at(d) for d in dw]), tt0, 1.4)
    # the final chord, held under the glow while the lights go down
    for m in ('Bb3', 'D4', 'F4', 'Bb4'):
        M.add('melody', tpt_l.play(n(m), 110, dur=D - end, release=1.5), end, 0.5)
        M.add('band', horn.play(n(m) - 12, 100, dur=D - end, release=1.5), end, 0.6)
    M.add('band', bone_l.play(n('Bb2'), 104, dur=D - end, release=1.5), end, 0.7)
    M.add('bass', tuba.play(n('Bb1'), 124), end)
    M.add('drums', clash.play(120), end, 0.7)
    M.add('drums', bd_big.play(120), end, 0.9)
    M.add('drums', troll.play(90, dur=D - end - 1.0), end + 0.3, 0.6)
