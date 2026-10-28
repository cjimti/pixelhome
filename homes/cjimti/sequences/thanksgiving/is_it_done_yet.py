"""Is It Done Yet?: The porch is the oven, its sides are the oven walls, the Right wing is the kitchen
timer and the Left wing is where the hungry family waits. The oven heats with a real thermal lag and
glows through blackbody colours. Someone keeps walking over to open the door: a blast of light, the
heat rolls out along the porch sides, the oven drops back to red and the timer gains time. The
peeks get faster. Then the cook stands guard and bats them away, twice. The timer runs out, dings,
and the turkey comes out golden."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, colormap, nframes

CODE = 'TG02'
TITLE = 'Is It Done Yet?'
KIND = 'show'
DESCRIPTION = ('The porch is the oven and the Right wing is the timer. Someone keeps opening the door to check, '
               'heat pours out, the timer gains time, until the cook stands guard. Ding.')

GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
CRANBERRY = hexc('#c0102a')
WARM = hexc('#ffc27a')
BROWN = hexc('#7a3008')

D = 70.0
# blackbody-ish ramp for the oven: dull red -> cherry -> orange -> amber
heat_map = colormap([(0.0, (0, 0, 0)), (0.15, (0.05, 0.0, 0.0)), (0.35, (0.22, 0.01, 0.0)), (0.55, (0.6, 0.04, 0.0)),
                     (0.75, (1.0, 0.16, 0.0)), (0.9, (1.0, 0.33, 0.02)), (1.05, (1.0, 0.55, 0.12))])

# peeks: (time the asker sets off, speed of the walk); blocks: (time the cook rushes out, which side)
WALK = (500, 1300)               # an asker walks from the Left wing to the oven door
PEEKS = [(12.0, 330), (22.0, 420), (29.5, 520), (34.5, 650)]
BLOCKS = [(42.0, 'left'), (47.5, 'right')]
R0, R1 = 2036.0, 2511.8          # the timer bar on the Right wing
SET = (4, 6)                     # the timer is wound up
SHUT = 2.3                       # the door is shut again this long after the asker arrives
WIND = (0.4, 1.6)                # ...and the timer gains time between these
SWAT = 0.67                      # a blocked asker meets the cook this long after the rush
MEET = {'left': 990.0, 'right': 1960.0}       # ...here
RING, GLOW, STEAM = 0.42, 1.5, (2.0, 0.9)    # after the ding: ring spacing, the glow, the steam puffs
PUFF = (1330, 75)                # where each puff of steam rises on the Porch Front


def arrive(t0, v):
    """When an asker who set off at t0 reaches the oven door."""
    return t0 + 800 / v


def cook(F):
    """Oven temperature, timer remaining (0..1), door opening per frame, and the time of the ding."""
    T = np.zeros(F)
    rem = np.zeros(F)
    temp, r = 0.0, 0.0
    door = np.zeros(F)
    for f in range(F):
        t = f * DT
        open_amt = 0.0
        for t0, v in PEEKS:
            ta = arrive(t0, v)                                       # arrives at the door
            open_amt = max(open_amt, smoothstep(ta - 0.1, ta + 0.15, t) * (1 - smoothstep(ta + 1.8, ta + SHUT, t)))
        door[f] = open_amt
        target = 0.0 if t < 2 else 1.0
        rate = 0.09 + 1.8 * open_amt
        target = target * (1 - 0.85 * open_amt)
        temp += (target - temp) * rate * DT
        T[f] = temp
        if SET[0] <= t < SET[1]:
            r = smoothstep(SET[0], SET[1], t)
        elif t >= SET[1]:
            r -= DT / 30
            for t0, v in PEEKS:
                ta = arrive(t0, v)
                if ta + WIND[0] <= t < ta + WIND[1]:
                    r += 0.16 * DT / 1.2
            r = max(r, 0.0)
        rem[f] = r
    ding = next(f for f in range(nframes(7), F) if rem[f] <= 0) * DT
    return T, rem, door, ding


def render(G, seed=22):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pdp = G.pd[G.path]
    n = G.N
    PF = (pdp > 1312) & (pdp < 1660)
    PL = (pdp > 893) & (pdp <= 1312)
    PR = (pdp >= 1660) & (pdp < 2033)
    LW = (pdp > 490) & (pdp <= 893)
    RW = pdp >= 2033
    # distance from the oven along each wall (0 at the back corner, 1 at the front)
    wall = np.where(PL, (1310 - pdp) / 415, np.where(PR, (pdp - 1660) / 370, 0))

    T, rem, door, ding = cook(F)

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        Tf = T[f]
        # oven window with rising convection shimmer, oven walls warm from the back
        conv = 0.5 + 0.5 * np.sin(pdp * 0.05 - 2.1 * t + 1.7 * np.sin(pdp * 0.017 + 0.6 * t))
        h = Tf * (0.82 + 0.16 * conv)
        done = smoothstep(ding + 1.2, ding + 3.5, t)
        h = h * (1 - done) + done * 0.62
        oven = heat_map(h)
        golden = light(BROWN, 0.55 + 0.1 * conv) + light(GOLD, 0.45 * conv)
        ovenc = oven * (1 - done) + golden * done
        buf[PF] += ovenc[PF]
        buf[PL | PR] += heat_map(0.55 * h * np.exp(-wall / 0.35))[PL | PR] * (1 - done)

        # door open: a flash on the window and a heat cloud rolling forward along both porch sides
        for t0, v in PEEKS:
            ta = arrive(t0, v)
            u = t - ta
            if 0 <= u < 3.0:
                buf[PF] += light(WARM, 0.65 * np.exp(-u / 0.35) * np.ones(PF.sum()))
                front = u / 1.6
                puff = np.exp(-((wall - front) / 0.18) ** 2) * np.exp(-u / 1.1)
                buf[PL | PR] += light(AMBER, 0.8 * puff[PL | PR])
            # the asker walks from the Left wing to the oven and back, slower
            ta_back = ta + SHUT
            if t0 <= t < ta_back + 800 / (0.5 * v):
                if t < ta:
                    x = WALK[0] + v * (t - t0)
                elif t < ta_back:
                    x = WALK[1] - 6 * np.sin(np.pi * (t - ta) / SHUT)
                else:
                    x = WALK[1] - 0.5 * v * (t - ta_back)
                buf += light(CRANBERRY, 0.9 * np.exp(-((pdp - x) / 11) ** 2))

        # blocked: the cook (gold) rushes out from the oven and pushes the asker back
        for tb, side in BLOCKS:
            u = t - tb
            if 0 <= u < 4.5:
                if side == 'left':
                    meet = MEET[side]
                    ax = 520 + 700 * u if u < SWAT else meet - 380 * (u - SWAT) * (1 + 0.3 * (u - SWAT))
                    cx = 1300 - 900 * u if u < 0.34 else meet + 12 + 120 * max(0, u - 0.9)
                    cx = max(cx, meet + 12)
                else:
                    meet = MEET[side]
                    ax = 2530 - 850 * u if u < SWAT else meet + 380 * (u - SWAT) * (1 + 0.3 * (u - SWAT))
                    cx = 1660 + 900 * u if u < 0.34 else meet - 12 - 120 * max(0, u - 0.9)
                    cx = min(cx, meet - 12)
                cx = np.clip(cx, 1000 if side == 'left' else 1660, 1300 if side == 'left' else 1950)
                fade = 1 - smoothstep(3.3, 4.5, u)
                buf += light(CRANBERRY, 0.9 * fade * np.exp(-((pdp - ax) / 11) ** 2))
                buf += light(GOLD, fade * np.exp(-((pdp - cx) / 13) ** 2))
                hit = np.exp(-((u - SWAT) / 0.12) ** 2)                 # the swat
                buf += light(WARM, 0.8 * hit * np.exp(-((pdp - meet) / 30) ** 2))

        # the family waiting on the Left wing: a low murmur that grows hungrier
        hunger = keys(t, [(3, 0), (8, 0.12), (40, 0.22), (ding, 0.25), (ding + 0.5, 0.0)])
        mur = 0.5 + 0.5 * np.sin(pdp * 0.08 + 3.0 * t) * np.sin(pdp * 0.021 - 1.3 * t)
        buf[LW] += light(CRANBERRY, hunger * (0.6 + 0.4 * mur[LW]))

        # the timer: a gold bar draining toward the house, a tick at its tip
        r = rem[f]
        if SET[0] <= t < ding + 0.1:
            tip = R0 + r * (R1 - R0)
            bar = np.clip((tip - pdp) / 6 + 0.5, 0, 1) * RW
            tick = 0.5 + 0.5 * np.cos(2 * np.pi * t) ** 8
            buf += light(GOLD, 0.22 * bar) + light(WARM, 0.5 * tick * np.exp(-((pdp - tip) / 5) ** 2) * RW)
            gain = rem[f] - rem[max(0, f - 8)]
            if gain > 0:
                buf += light(CRANBERRY, min(1, gain * 40) * 0.6 * np.exp(-((pdp - tip) / 25) ** 2) * RW)
        # DING: three gold rings out of the timer, then warmth over the whole house
        u = t - ding
        if u >= 0:
            for k in range(3):
                uk = u - RING * k
                if uk >= 0:
                    ring = np.exp(-((np.abs(pdp - R0) - 700 * uk) / 50) ** 2) * np.exp(-uk / 0.6)
                    buf += light(GOLD, 0.9 * ring * (pdp > 1600)) + light(WARM, 0.9 * np.exp(-uk / 0.12) * RW)
            glow = smoothstep(GLOW, 4.5, u) * keys(t, [(ding, 1), (64, 1), (70, 0)])
            dist = np.abs(pdp - 1486)
            spread = smoothstep(0, 1, (900 * (u - GLOW) / 2.0 - dist) / 300)
            cheer = (0.5 + 0.5 * np.sin(pdp * 0.06 - 4 * t)) ** 3
            buf += light(AMBER, glow * spread * (0.26 + 0.12 * cheer))
            # steam from the bird
            for k in range(5):
                uk = u - STEAM[0] - STEAM[1] * k
                if 0 < uk < 4:
                    p = PUFF[0] + PUFF[1] * k + 18 * np.sin(uk * 2 + k)
                    buf[PF] += light(WARM, 0.35 * np.sin(np.pi * uk / 4) * np.exp(-((pdp[PF] - p) / 18) ** 2))
            buf *= keys(t, [(65, 1.0), (70, 0.0)])
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A kitchen march in F at the timer's pace: its lamp ticks every half second, so a woodblock tick-tock is the pulse
# under everything. Upright piano and pizzicato bass keep time; a clarinet sings the waiting tune, then a flute, then
# the cook's horn. Each peek is a tiptoeing bassoon to the oven, a creak, a whoosh of heat out both porch sides, the
# ratchet of the timer winding back, a slam, and a slow bassoon back down. The cook's swats are slapstick with a sad
# trombone. The ding is glock and triangle, then the whole band in F as the bird comes out.

BEAT = 0.5                                  # the timer lamp's tick peaks on every half second
PROG = ['F', 'Bb', 'C7', 'F', 'Dm', 'Gm', 'C7', 'F']
CHORD = {'F': ('A3', 'C4', 'F4'), 'Bb': ('Bb3', 'D4', 'F4'), 'C7': ('Bb3', 'C4', 'E4'), 'Dm': ('A3', 'D4', 'F4'),
         'Gm': ('Bb3', 'D4', 'G4')}
ROOT = {'F': ('F2', 'C2'), 'Bb': ('Bb1', 'F2'), 'C7': ('C2', 'G2'), 'Dm': ('D2', 'A2'), 'Gm': ('G2', 'D2')}
TUNE = [  # (beat in the 8-bar phrase, note, beats)
    (0, 'C5', 1.5), (1.5, 'A4', 0.5), (2, 'F4', 1), (3, 'A4', 1),
    (4, 'Bb4', 1.5), (5.5, 'D5', 0.5), (6, 'F5', 1), (7, 'D5', 1),
    (8, 'C5', 1), (9, 'E4', 0.5), (9.5, 'G4', 0.5), (10, 'Bb4', 1), (11, 'G4', 1),
    (12, 'A4', 1.5), (13.5, 'G4', 0.5), (14, 'F4', 2),
    (16, 'D5', 1.5), (17.5, 'C5', 0.5), (18, 'A4', 1), (19, 'F4', 1),
    (20, 'G4', 1.5), (21.5, 'A4', 0.5), (22, 'Bb4', 1), (23, 'D5', 1),
    (24, 'C5', 1), (25, 'Bb4', 0.5), (25.5, 'A4', 0.5), (26, 'G4', 1), (27, 'E4', 1),
    (28, 'F4', 3)]
FMAJ = [5, 7, 9, 10, 0, 2, 4]               # pitch classes of F major, for the harmony a sixth above
UP = ['F3', 'G3', 'A3', 'Bb3', 'C4', 'D4', 'E4', 'F4', 'G4']       # tiptoeing to the oven, one note per 100 units


def score(M, G):
    from pixelhome.audio import note, slide, whoosh
    n = note
    F = nframes(D)
    T, rem, door, ding = cook(F)
    piano = M.sampler('Keys/Upright Nr1/UR1_*_mf_*.wav')
    harp = M.sampler('Strings/Harp/*.wav')
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    fall = M.sampler('Brass/OldTrombone/Fall/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    marim = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    guiro = M.hits('Percussion/Guiro-Slow*.wav')
    logd = M.hits('Percussion/LogDrumLo*.wav')
    thud = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_m*.wav')
    cym = M.hits('Percussion/susCymb1-hit_mp*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*_v3_*.wav')
    tri = M.hits('VSCO 1 Percussion/varMetal/triangle/1/triangle1_hit_mp*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')

    for name, gain, rev in (('keys', 0.34, 0.15), ('bass', 0.5, 0.08), ('tune', 0.42, 0.22), ('tick', 0.42, 0.06),
                            ('walk', 0.4, 0.12), ('perc', 0.6, 0.12), ('fx', 0.16, 0.25), ('brass', 0.36, 0.2),
                            ('strings', 0.3, 0.3), ('bell', 0.4, 0.3), ('pad', 0.16, 0.3)):
        M.bus(name, gain=0.62 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def rem_at(t):
        return float(rem[min(F - 1, int(round(t / DT)))])

    def tip(t):                             # pan of the timer bar's tip
        return pan_at(R0 + rem_at(t) * (R1 - R0))

    def bar_chord(t, t0):
        return PROG[int((t - t0) // (4 * BEAT)) % len(PROG)]

    sides = (pan_at(1100), pan_at(1850))    # the two porch walls
    oven_pan = pan_at(1486)
    for j, m in enumerate(('C4', 'F4', 'A4', 'C5', 'F5')):                       # the kitchen light goes on
        M.add('bell', harp.play(n(m), 64), 0.3 + 0.09 * j, 0.6, -0.2)

    # ---- the oven: a warm pad on F that swells with the temperature and sags when the door is open ----
    hum = M.synth('Pads/MKS-70 Warm Pad').render([(2.0, n(m), 70, ding - 0.5) for m in ('F2', 'C3', 'A3')], D)
    tt = np.arange(hum.shape[1]) / 48000
    M.add('pad', hum * (0.15 + 0.85 * np.interp(tt, np.arange(F) * DT, T)), 0.0, 1.0, oven_pan)
    M.add('perc', troll.play(50, dur=2.0), 1.6, 0.35, oven_pan)

    # ---- the timer is wound: a ratchet and a marimba run up the Right wing, then the first tick ----
    M.add('perc', ratchet.play(90, dur=SET[1] - SET[0]), SET[0], 0.6, pan_at((R0 + R1) / 2))
    for i, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5')):
        t = SET[0] + i * (SET[1] - SET[0]) / 8
        M.add('walk', marim.play(n(m), 70 + 5 * i), t, 0.8, pan_at(R0 + (R1 - R0) * smoothstep(SET[0], SET[1], t)))
    M.add('bell', tri.play(90), SET[1], 0.7, pan_at(R1))

    # ---- the ticking clock, from the moment the lamp starts until the ding ----
    k = 0
    while SET[0] + k * BEAT < ding:
        t = SET[0] + k * BEAT
        M.add('tick', wood.play(92 if k % 2 == 0 else 74, pitch=0 if k % 2 == 0 else -4), t, 1.0, tip(t))
        k += 1

    # ---- the waiting band: three passes of the tune from when the timer is set, then the last seconds ----
    T0 = float(SET[1])
    end = T0 + 3 * 16
    k = -8                                  # two soft bars in as the oven lights
    while T0 + k * BEAT < end:
        t = T0 + k * BEAT
        c = bar_chord(t, T0)
        v = 84 if k >= 0 else 60 + 2 * k + 16
        if k % 2 == 0:
            M.add('bass', pizz.play(n(ROOT[c][(k // 2) % 2]), v + 16), t, 1.0, -0.15)
        else:
            for m in CHORD[c]:
                M.add('keys', piano.play(n(m), v), t, 0.6, 0.1)
        if t >= T0 + 16 and k % 2 == 1:     # a tambourine joins on the off-beats as the peeks speed up
            M.add('perc', tamb.play(60), t, 0.35, 0.3)
        k += 1
    for rep, (inst, oct_, vel) in enumerate(((clar, 0, 96), (flute, 0, 90), (horn, -12, 100))):
        for b, m, d in TUNE:
            t = T0 + rep * 16 + b * BEAT
            M.add('tune' if rep < 2 else 'brass', inst.play(n(m) + oct_, vel, dur=d * BEAT * 0.95, release=0.15), t,
                  1.0 if rep < 2 else 0.9, -0.05)
        if rep == 2:                        # the cook's tune gets a clarinet a sixth above
            for b, m, d in TUNE:
                pc = n(m) % 12
                up = (FMAJ[(FMAJ.index(pc) + 5) % 7] - pc) % 12
                M.add('tune', clar.play(n(m) + up, 70, dur=d * BEAT * 0.95), T0 + 32 + b * BEAT, 0.5, 0.1)
    # the last seconds: only the clock, a timpani roll and the piano hanging on C7
    M.add('perc', troll.play(70, dur=ding - end), end, 0.4, tip(end))
    k = 0
    while end + k * BEAT < ding - 0.05:
        t = end + k * BEAT
        for m in CHORD['C7']:
            M.add('keys', piano.play(n(m), 64 + 6 * k), t, 0.6, 0.1)
        if k % 2 == 0:
            M.add('bass', pizz.play(n('C2'), 96), t, 1.0, -0.15)
        k += 1

    # ---- the peeks ----
    for i, (t0, v) in enumerate(PEEKS):
        ta = arrive(t0, v)
        for j, m in enumerate(UP):           # tiptoe up to the oven
            x = WALK[0] + 100 * j
            M.add('walk', bsn.play(n(m), 80 + 3 * j, dur=0.18), t0 + (x - WALK[0]) / v, 1.0, pan_at(x))
        M.add('perc', guiro.play(70, dur=0.45), ta - 0.35, 0.5, oven_pan)           # the hinge
        M.add('perc', cym.play(80), ta, 0.5, oven_pan)                             # the blast of light
        for j, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
            M.add('bell', harp.play(n(m), 90), ta + 0.04 * j, 0.6, oven_pan)
        for sd, p in enumerate(sides):                                              # heat rolls out both sides
            M.add('fx', whoosh(1.8, 140, 1100, 0.5, seed=10 * i + sd), ta, 0.9, p)
        M.add('perc', ratchet.play(85, dur=WIND[1] - WIND[0]), ta + WIND[0], 0.55, tip(ta + WIND[1]))
        M.add('perc', logd.play(110), ta + SHUT - 0.05, 0.8, oven_pan)            # slam
        M.add('perc', thud.play(100), ta + SHUT - 0.05, 0.6, oven_pan)
        for j, m in enumerate(reversed(UP)):  # and the long walk back, an octave down and slower
            x = WALK[1] - 100 * j
            M.add('walk', bsn.play(n(m) - 12, 72 - 2 * j, dur=0.3), ta + SHUT + (WALK[1] - x) / (0.5 * v), 1.0,
                  pan_at(x))

    # ---- the cook stands guard ----
    for tb, side in BLOCKS:
        meet = MEET[side]
        start, home = (520, 1300) if side == 'left' else (2530, 1660)
        for j in range(3):                  # the asker hurries in
            M.add('walk', bsn.play(n(UP[2 * j + 2]), 90, dur=0.12), tb + j * SWAT / 3, 1.0,
                  pan_at(start + (meet - start) * j / 3))
        for j, m in enumerate(('C5', 'C5', 'F5')):                                  # the cook charges out
            M.add('brass', tpt.play(n(m), 100 + 10 * j, dur=0.12 if j < 2 else 0.3), tb + 0.12 * j, 0.9,
                  pan_at(home + (meet - home) * j / 3))
        M.add('perc', slap.play(127), tb + SWAT, 1.0, pan_at(meet))                # SWAT
        M.add('perc', crash_s.play(100), tb + SWAT, 0.5, pan_at(meet))
        M.add('perc', timp.play(110), tb + SWAT, 0.6, pan_at(meet))
        M.add('fx', slide(0.0, 0.8, 1400, 420, 0.85, 0.5), tb + SWAT + 0.05, 1.2, pan_at((meet + start) / 2))
        M.add('brass', fall.play(n('Bb3'), 100), tb + SWAT + 0.9, 0.7, pan_at(start))

    # ---- DING, and dinner ----
    for k in range(3):
        M.add('bell', glock.play(n('A5'), 124 - 8 * k), ding + RING * k, 1.6, pan_at(R0))
        M.add('bell', glock.play(n('A6'), 100 - 8 * k), ding + RING * k, 0.6, pan_at(R0))
        M.add('bell', tri.play(110), ding + RING * k, 0.8, pan_at(R0))
    tg = ding + GLOW
    M.add('perc', troll.play(90, dur=GLOW), ding + 0.2, 0.5, oven_pan)
    M.add('perc', cym.play(100), tg, 0.6, 0.0)
    M.add('perc', timp.play(110), tg, 0.7, 0.0)
    for k, c in enumerate(['F', 'Bb', 'C7', 'F']):
        t = tg + 4 * BEAT * k
        for m in CHORD[c]:
            M.add('strings', vln.play(n(m) + 12, 80, dur=4 * BEAT + 0.3, release=0.4), t, 0.5)
        M.add('strings', cello.play(n(ROOT[c][0]) + 12, 86, dur=4 * BEAT + 0.3, release=0.4), t, 0.6)
        for j in range(4):
            tj = t + j * BEAT
            if j % 2 == 0:
                M.add('bass', pizz.play(n(ROOT[c][j // 2]), 104), tj, 1.0, -0.15)
            else:
                for m in CHORD[c]:
                    M.add('keys', piano.play(n(m), 90), tj, 0.6, 0.1)
    for b, m, d in TUNE[:15]:               # the tune again, in horn and clarinet together
        M.add('brass', horn.play(n(m) - 12, 104, dur=d * BEAT * 0.95, release=0.2), tg + b * BEAT, 0.9, -0.1)
        M.add('tune', clar.play(n(m), 96, dur=d * BEAT * 0.95, release=0.2), tg + b * BEAT, 0.9, 0.1)
    for k in range(5):                      # steam off the bird
        t = ding + STEAM[0] + STEAM[1] * k
        for j, m in enumerate(('C5', 'F5', 'A5')):
            M.add('bell', harp.play(n(m) + 2 * (k % 2), 70), t + 0.12 * j, 0.5, pan_at(PUFF[0] + PUFF[1] * k))
    tf = tg + 16 * BEAT                     # the last chord, held to the end
    for m in ('F2', 'C3', 'F3', 'A3'):
        M.add('brass', horn.play(n(m) + 12, 96, dur=D - tf, release=1.5), tf, 0.6)
    for m in CHORD['F']:
        M.add('strings', vln.play(n(m) + 12, 84, dur=D - tf, release=1.5), tf, 0.5)
        M.add('keys', piano.play(n(m), 96), tf, 0.7, 0.1)
    M.add('bass', pizz.play(n('F2'), 110), tf, 1.0, -0.15)
    M.add('strings', cello.play(n('F3'), 90, dur=D - tf, release=1.5), tf, 0.6)
    M.add('perc', timp.play(100), tf, 0.6)
    M.add('perc', crash_s.play(80), tf, 0.4)
    for j, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('bell', harp.play(n(m), 84), tf + 0.06 * j, 0.6, 0.1)
