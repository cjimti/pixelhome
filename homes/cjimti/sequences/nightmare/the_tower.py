"""Experiments in the Tower: the Pumpkin King shuts himself in his tower and tries to work Christmas out.

The porch is the tower's lit window, with the king at his bench on Porch Front and the wings dim violet with
beakers glowing green. A busy patter (bassoon and pizzicato, an original tune that runs the notes of his own theme
in quick eighths) drives the experiments, one after another, each lighting the whole house: a green scanner beam
sweeps the roofline end to end and back, bleeping as it crosses the toy on his bench; beakers bubble, green, violet
and pink bubbles swelling and popping all along the roof; he cuts a toy open and the stuffing bursts out; he taps
a red ornament and it shatters, red and gold shards flying the length of the house; a snowflake twinkles on the
bench and melts the instant he touches it, a blue drip running away; a candy cane's red and white stripes twirl
across the whole house until he snaps it and they fly apart. Then he scrawls equations: a chalk pen writes
left to right from the Left wing to the free end of Right, leaving white marks and gold equals signs behind.
Days and nights pass, faster and faster: sun sweeps over the house, nights fall with the window lit, a clock
ticking quicker. He slumps to his lament in A minor on the bassoon, crumpling his notes and tossing them out to
the wings. Then, in the dark, a spark over his head: EUREKA. A white flash, a burst the length of the roof, and
his theme in A major on the whole band, flame thrown out along the roof on every note, the wings flooding orange
and gold, red and orange bulbs chasing: he doesn't need to understand Christmas, he'll make it himself.

compose() lays the music end to end: render() and score() read its events and marks, so every experiment lands on
the patter."""
import numpy as np
from pixelhome.audio import SR, slide
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (THEMES, Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, DUSK,
                                 NIGHT, MOON, BONE, WHITE, GOLD, ICE, WARM, RED, PINK, BLUE)

CODE = 'NM07'
TITLE = 'Experiments in the Tower'
KIND = 'show'
DESCRIPTION = ('Locked in his tower, the Pumpkin King scans, boils, dissects and scribbles equations across the '
               'whole roof while days and nights race by, until a spark over the porch: he will do Christmas himself.')
VOICEOVER = ('Locked in his tower, the Pumpkin King set out to solve Christmas, like a scientist. '
             'It would not be solved.')

CHALK = hexc('#e8f0ff')
SCAN = hexc('#40ffa0')


def _eighths(bars):
    """Bars of eighth notes as text ('A3', 'E4*2' held two eighths, '.' a rest) -> melody [(beat, beats, note)]."""
    mel = []
    for i, bar in enumerate(bars):
        b = 4.0 * i
        for tok in bar.split():
            n, _, k = tok.partition('*')
            k = int(k or 1)
            if n != '.':
                mel.append((b, 0.5 * k, n))
            b += 0.5 * k
    return mel


# The tower patter: an original tune for this scene, the king's own notes (A, C, E, F) run in quick eighths, as if
# his lament had been put to work. It turns back into his theme, in major, at the eureka.
THEMES.setdefault('tower patter', dict(meter=4, bpm=144, name="The tower patter: the king at work, A minor",
    melody=_eighths(['A3 C4 E4 F4 E4 C4 A3 C4', 'D4 F4 A4 G#4 A4 F4 D4 F4', 'E4 G#4 B4 E4 D4 B3 G#3 B3',
                     'A3 C4 E4 A4 E4*2 A3*2', 'F4 A4 C5 B4 A4 F4 C4 F4', 'D4 F4 A4 D5 C5 A4 F4 D4',
                     'E4 G#4 B4 D5 C5 B4 A4 G#4', 'A4 E4 C4 E4 A3*4']),
    chords=[(0, 4, 'Am'), (4, 4, 'Dm'), (8, 4, 'E'), (12, 4, 'Am'), (16, 4, 'F'), (20, 4, 'Dm'), (24, 4, 'E7'),
            (28, 4, 'Am')]))


def compose():
    C = Chart()
    C.rest(2.0)                                                         # the tower window lights
    C.mark('lab1')
    C.play('tower patter', style='march', bpm=144, tag='lab1')          # scanner, beakers, the toy
    C.mark('lab2')
    C.play('tower patter', style='march', bpm=144, tag='lab2')          # ornament, snowflake, candy cane
    C.mark('scrawl')
    C.play('tower patter', style='drive', bars=(4, 8), bpm=168, tag='scrawl')     # equations across the roof
    C.mark('days')
    C.play('king', style='hold', bars=(4, 8), bpm=120, tune=False, tag='days')    # days and nights race by
    C.mark('gloom')
    C.play('king', style='waltz', bars=(0, 4), bpm=80, tag='gloom')     # he slumps, crumpling his notes
    C.mark('spark')
    C.rest(1.4)                                                         # in the dark, an idea
    C.mark('eureka')
    C.play('king', style='waltz', bars=(8, 16), bpm=100, major=True, tag='eureka')
    C.mark('final')
    C.rest(2.6)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
DB1, DB2 = C.downbeats('lab1'), C.downbeats('lab2')
T_SCAN, T_BUBBLE, T_TOY, T_CUT = DB1[0], DB1[3], DB1[5], DB1[6]
T_ORN, T_TAP, T_SHATTER = DB2[0], DB2[1], DB2[2]
T_FLAKE, T_TOUCH = DB2[3], DB2[4] + 0.4
T_CANE, T_SNAP = DB2[5], DB2[7]


def bubbles(S):
    """The beakers' bubbles: (time, path distance, colour index), mostly over the porch."""
    rng = np.random.default_rng(707)
    out = []
    for t in np.sort(rng.uniform(T_BUBBLE, T_TOY - 0.2, 34)):
        p = rng.normal(S.mid, 520) if rng.random() < 0.7 else rng.uniform(S.at('Left', 0), S.L)
        out.append((float(t), float(np.clip(p, S.at('Left', 0), S.L - 10)), int(rng.integers(3))))
    return out


def tosses(S):
    """The crumpled notes he throws: (time, side), on the lament's long notes."""
    return [(t, 1 if i % 2 else -1) for i, (t, d, m) in enumerate(n for n in C.tunes('gloom') if n[1] > 1.0)]


def scan_pos(S, t):
    """The scanner beam: end to end and back, from the free end of Right."""
    u = np.clip((t - T_SCAN) / (T_BUBBLE - T_SCAN), 0, 1)
    return S.L * np.abs(2 * u - 1)                                      # the free end of Right, Side, and back


def render(G, seed=7):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    p_king, p_bench = mid + 55, mid - 55
    beats = np.array([b[0] for b in C.beats])
    bub = bubbles(S)
    bcols = (SLIME, VIOLET, PINK)
    toss = tosses(S)
    eu = C.tunes('eureka')
    eu_t = np.array([n[0] for n in eu])
    eu_downs = np.array(C.downbeats('eureka'))
    # the chalk: marks of two to four pixels with gaps, and gold equals signs, fixed for the whole scene
    marks = (rng.random(G.N) < 0.62).astype(float) * rng.uniform(0.35, 0.8, G.N)
    eq = (G.pi % 17 < 2) & (rng.random(G.N) < 0.8)
    x0, x1 = S.at('Left', 0), L
    lab = S.porch | S.wings
    pen_t0, pen_t1 = M['scrawl'], M['days']
    t_spark, t_eu, t_fin = M['spark'], M['eureka'], M['final']
    side = S.run['Side']
    DOWNS = [x for x in C.downbeats() if M['lab1'] <= x < M['days']]

    for f in range(F):
        t = f * DT
        beat = pulse(t, beats, 0.12)
        up = smoothstep(0, 1.8, t)
        dim = 1.0 - 0.8 * smoothstep(t_spark - 0.6, t_spark + 0.2, t) * (t < t_eu)
        # the tower: a violet room, beakers glowing green on the porch sides, the window warm on Porch Front
        fr = light(DUSK, 0.45 * up * dim * np.ones(G.N))
        fr += light(SLIME, 0.35 * up * dim * (S.run['Porch Left'] | S.run['Porch Right']) *
                    (0.75 + 0.25 * np.sin(3 * t + d / 40)))
        fr += light(WARM, 0.5 * up * dim * S.run['Porch Front'] * (0.85 + 0.15 * beat))
        fr += light(VIOLET, 0.15 * up * dim * side)
        # the work's own pulse: a green wave out from the bench on every bar of the patter
        if M['lab1'] <= t < M['days']:
            for t0 in [x for x in DOWNS if t - 1.2 < x <= t]:
                a = t - t0
                fr += light(SLIME, 0.7 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_bench) - 1100 * a) / 110) ** 2))

        # 1. the scanner: a green beam sweeping the whole roof, bleeping over the toy on the bench
        if T_SCAN <= t < T_BUBBLE:
            p = scan_pos(S, t)
            fr += light(SCAN, 1.0 * np.exp(-((d - p) / 35) ** 2) + 0.4 * np.exp(-((d - p) / 200) ** 2))
            for k in range(1, 6):                                       # its afterglow
                fr += light(SCAN, 0.5 * (1 - k / 6) * np.exp(-((d - scan_pos(S, t - 0.06 * k)) / 40) ** 2))
            near = np.exp(-((p - p_bench) / 60) ** 2)
            fr += light(ICE, 0.8 * near * S.blob(p_bench, 30))
            fr = S.sprite(fr, p_bench, [(1, GOLD, 0.8), (0, ICE if near > 0.3 else GOLD, 0.9), (-1, GOLD, 0.8)], 1.0)
        # 2. the beakers: bubbles swell and pop all along the roof, the porch boiling green
        if T_BUBBLE <= t < T_TOY + 0.6:
            fr += light(SLIME, 0.35 * S.porch * (0.6 + 0.4 * np.sin(13 * t + d / 23)) *
                        smoothstep(T_BUBBLE, T_BUBBLE + 0.4, t) * smoothstep(T_TOY + 0.6, T_TOY, t))
            for tb, p, c in bub:
                a = t - tb
                if -0.5 <= a < 0:                                       # swelling
                    s = 1 + a / 0.5
                    fr += light(bcols[c], 1.0 * s * np.exp(-((d - p) / (8 + 34 * s)) ** 2))
                elif 0 <= a < 0.45:                                     # pop
                    fr += light(WHITE, 1.0 * np.exp(-a / 0.08) * np.exp(-((d - p) / 40) ** 2))
                    ring_ = np.exp(-((np.abs(d - p) - 40 - 400 * a) / 16) ** 2)
                    fr += light(bcols[c], 0.9 * np.exp(-a / 0.18) * ring_)
        # 3. the toy: a teddy on the bench, the knife, then the stuffing bursting out
        if T_TOY <= t < T_ORN:
            gap = 6 * smoothstep(T_CUT, T_CUT + 0.6, t)
            lv = smoothstep(T_TOY, T_TOY + 0.3, t)
            for sgn in (-1, 1):
                fr = S.sprite(fr, p_bench + sgn * gap * 5, [(1, GOLD, 0.9), (0, WARM, 1.0), (-1, GOLD, 0.9)], lv)
            if T_CUT - 0.8 <= t < T_CUT:                                # the blade drawn across
                kp = p_bench + 40 - 80 * smoothstep(T_CUT - 0.8, T_CUT, t)
                fr += light(WHITE, 1.0 * S.blob(kp, 6))
            fr += light(WARM, 0.5 * lv * S.porch * (0.6 + 0.4 * beat))
            fr += S.burst([(T_CUT, 1.0, p_bench)], t, seed=3, n=18, reach=0.6, colors=(WHITE, BONE, WARM))
            if T_CUT <= t < T_CUT + 0.8:
                fr += light(GOLD, 0.6 * np.exp(-(t - T_CUT) / 0.25) * S.wings)
        # 4. the ornament: tapped twice, then shattered the length of the house
        if T_ORN <= t < T_FLAKE:
            whole = t < T_SHATTER
            if whole:
                tap = pulse(t, [T_TAP, T_TAP + 0.42], 0.15)
                fr += light(RED, (0.8 + 0.4 * tap) * S.blob(p_bench, 14) + 0.3 * S.porch)
                fr += light(GOLD, 0.9 * S.blob(p_bench + 18, 5))
                fr += light(WHITE, 0.8 * tap * S.blob(p_bench, 8))
            fr += S.burst([(T_SHATTER, 1.2, p_bench)], t, seed=4, n=40, reach=1.4, colors=(RED, GOLD, WHITE, RED))
            a = t - T_SHATTER
            if 0 <= a < 1.5:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.1) * S.porch)
                fr += light(RED, 0.75 * np.exp(-a / 0.5) * np.ones(G.N))
        # 5. the snowflake: twinkling on the bench, snow on the wings; it melts the instant he touches it
        if T_FLAKE <= t < T_CANE:
            a = t - T_TOUCH
            if a < 0:
                tw = 0.7 + 0.3 * np.sin(2 * np.pi * 3 * t)
                fr += light(WHITE, tw * S.blob(p_bench, 7))
                fr += light(ICE, 0.45 * S.blob(p_bench, 60) + 0.2 * S.porch)
                fr += S.snowfall(t, 0.8) * (S.wings | S.run['Side'])[:, None] * smoothstep(T_FLAKE, T_FLAKE + 0.5, t)
            else:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.1) * S.blob(p_bench, 25))
                pdrip = p_bench - 260 * smoothstep(0.2, 1.8, a)          # the drip runs away down Porch Left
                fr += light(BLUE, 0.9 * np.exp(-a / 1.2) * S.blob(pdrip, 10))
                fr += light(ICE, 0.25 * np.exp(-a / 0.6) * lab)
        # 6. the candy cane: red and white stripes twirling across the house, until he snaps it
        if T_CANE <= t < M['scrawl'] + 0.8:
            lv = smoothstep(T_CANE, T_CANE + 0.5, t)
            a = t - T_SNAP
            fly = 0 if a < 0 else 900 * a
            dd = np.where(d < p_bench, d + fly, d - fly)
            stripe = (np.floor((dd - 160 * t) / 22) % 2) == 0
            keep = 1.0 if a < 0 else np.exp(-a / 0.4) * (np.abs(d - p_bench) > fly)
            reach = smoothstep(T_CANE, T_CANE + 1.5, t) * L
            span = np.exp(-np.maximum(np.abs(d - p_bench) - reach, 0) / 40)
            fr += light(np.where(stripe[:, None], RED, WHITE), 0.75 * lv * keep * span)
            if 0 <= a < 0.3:
                fr += light(WHITE, 1.0 * np.exp(-a / 0.07) * S.blob(p_bench, 40))
        # 7. the equations: a chalk pen writing from the Left wing to the free end of Right
        if pen_t0 <= t < M['gloom'] + 1.0:
            u = smoothstep(pen_t0, pen_t1 - 0.3, t) if t < pen_t1 else 1.0
            pen = x0 + (x1 - x0) * (t - pen_t0) / (pen_t1 - 0.3 - pen_t0)
            pen = min(pen, x1)
            written = (d >= x0) & (d <= pen)
            fade = smoothstep(M['gloom'] + 1.0, M['days'] + 1.0, t)
            fr += light(CHALK, 0.7 * marks * written * fade)
            fr += light(GOLD, 0.9 * eq * written * fade)
            if t < pen_t1:
                jit = 0.7 + 0.3 * np.sin(57 * t)
                fr += light(WHITE, jit * S.blob(pen, 8)) + light(CHALK, 0.4 * S.blob(pen, 50))
        # 8. days and nights: the sun sweeping over, faster and faster, the window lit each night
        if M['days'] <= t < M['gloom']:
            u = (t - M['days']) / (M['gloom'] - M['days'])
            ph = 7.0 * u ** 1.5
            day = 0.5 - 0.5 * np.cos(2 * np.pi * ph)
            sun = L * (1 - ph % 1.0)
            fr = fr * (1 - 0.6 * day)
            fr += light(ICE, 0.35 * day * np.ones(G.N)) + light(GOLD, 0.9 * day * S.blob(sun, 90))
            fr += light(NIGHT, 0.35 * (1 - day) * np.ones(G.N))
            fr += light(WARM, 0.6 * (1 - day) * S.run['Porch Front'])
        # 9. the gloom: he slumps; the room goes dull violet, a dull red throb, crumpled notes tossed to the wings
        if M['gloom'] <= t < t_spark:
            g = smoothstep(M['gloom'], M['gloom'] + 1.0, t)
            fr *= 1 - 0.4 * g
            fr += light(RED, 0.25 * g * pulse(t, C.downbeats('gloom'), 0.5) * S.porch)
            sink = (t - M['gloom']) / 3.0 % 1.0                         # slow violet sweeps sinking in to him
            fr += light(VIOLET, 0.45 * g * np.exp(-((np.abs(d - p_king) - 1300 * (1 - sink)) / 120) ** 2))
            for tt, sd in toss:
                a = t - tt
                if 0 <= a < 1.8:
                    for k in range(4):
                        p = p_king + sd * 800 * (1 - np.exp(-max(a - 0.05 * k, 0) / 0.5))
                        fr += light(BONE, (1.0 - 0.22 * k) * np.exp(-a / 1.0) * S.blob(p, 14))
        # 10. the spark: in the dark, a point of light over him that grows
        if t_spark <= t < t_eu + 0.3:
            s = smoothstep(t_spark + 0.2, t_eu, t)
            fr += light(WHITE, (0.3 + 0.9 * s) * S.blob(p_king, 4 + 14 * s))
            fr += light(GOLD, 0.5 * s * S.blob(p_king, 80))
        # 11. EUREKA: a flash, a burst, then his theme in major: flame on every note, the wings orange and gold
        if t >= t_eu:
            a = t - t_eu
            if a < 0.5:
                fr += light(WHITE, 0.85 * np.exp(-a / 0.12) * np.ones(G.N))
            fr += S.burst([(t_eu, 1.3, p_king), (t_fin - 0.05, 1.2, mid)], t, seed=11, n=40, reach=1.4,
                          colors=(GOLD, WHITE, ORANGE, RED))
            lv = smoothstep(0, 0.6, a) * smoothstep(D, D - 1.5, t)
            dn = pulse(t, eu_downs, 0.35)
            chase = ((G.pi + int(t * 10)) % 8 < 4)
            fr += light(np.where(chase[:, None], PUMPKIN, RED), lv * (0.6 + 0.4 * dn) * (S.wings | side))
            fr += light(GOLD, lv * (0.5 + 0.35 * dn) * S.porch)
            for j in np.flatnonzero((eu_t <= t) & (eu_t > t - 1.0)):
                b = t - eu_t[j]
                sd = 1 if j % 2 else -1
                front = p_king + sd * (200 + 1100 * b)
                fr += light(FLAME, 1.2 * np.exp(-b / 0.45) * np.exp(-((d - front) / 110) ** 2))

        # the king himself, at his bench; he paces through the days, slumps in the gloom, stands tall at the eureka
        pk = p_king
        if M['days'] <= t < M['gloom']:
            pk = p_king + 50 * np.sin(2 * np.pi * (t - M['days']) * 0.9)
        lvl = up * (1.0 - 0.35 * smoothstep(M['gloom'], M['gloom'] + 1, t) * (t < t_eu))
        glow = 0.3 + (0.6 * smoothstep(t_eu, t_eu + 0.5, t) if t >= t_eu else 0)
        fr = S.jack(fr, pk, lvl * smoothstep(D, D - 1.5, t), facing=-1, glow=glow)
        out[f] = fr
    return np.clip(out, 0, 1)


def _blip(B, t, f0, f1, dur, gain, pan):
    """A bubble's bloop: a short sine chirp."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / dur)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dur) ** 2
    B._sfx(sig, t, gain, pan)


def _hum(B, t0, t1, pos, S):
    """The scanner's hum, rising as the beam crosses the house, following it."""
    for k in range(int((t1 - t0) / 0.25)):
        t = t0 + 0.25 * k
        n = int(0.3 * SR)
        tt = np.arange(n) / SR
        f = 160 + 60 * np.sin(2 * np.pi * 3 * (t + tt))
        sig = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR))
        sig *= np.sin(np.pi * tt / 0.3)
        B._sfx(sig, t, 0.06, S.pan(pos(t)))


def _crumple(B, t, pan, seed):
    n = int(0.35 * SR)
    sig = B._noise(0, 1200, 7000, seed, n=n) * B._wobble(n, 60, seed + 1, 0.95) * np.exp(-np.arange(n) / (0.12 * SR))
    B._sfx(sig, t, 0.3, pan)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.4)
    p_king, p_bench = S.mid + 55, S.mid - 55
    parts = {
        ('lab1', 'tune'): [('bassoons', 0, 6, 0.8), ('pizz', 12, -2, 0.5)],
        ('lab1', 'bass'): [('basses pizz', 0, 0, 0.6), ('tuba', -12, -10, 0.4)],
        ('lab1', 'chord'): [('pizz', 0, -6, 0.4)],
        ('lab2', 'tune'): [('clarinets', 0, 6, 0.75), ('xylo', 12, -8, 0.35), ('pizz', 0, -4, 0.4)],
        ('lab2', 'bass'): [('basses pizz', 0, 0, 0.6), ('tuba', -12, -6, 0.5)],
        ('lab2', 'chord'): [('pizz', 0, -6, 0.4), ('muted horn', 0, -14, 0.3)],
        ('scrawl', 'tune'): [('xylo', 12, -4, 0.45), ('violins', 0, 0, 0.55), ('flutes', 12, -10, 0.35)],
        ('scrawl', 'bass'): [('cellos', 0, -2, 0.5), ('tuba', -12, -4, 0.5)],
        ('scrawl', 'chord'): [('violas', 0, -10, 0.35)],
        ('days', 'hold'): [('violas', 0, -6, 0.45), ('horns', 0, -16, 0.3), ('choir', 12, -18, 0.3)],
        ('days', 'pedal'): [('cellos', 0, -6, 0.55)],
        ('gloom', 'tune'): [('bassoons', 0, 6, 0.85), ('cellos', 12, -10, 0.35)],
        ('gloom', 'bass'): [('basses', 0, -8, 0.5)],
        ('gloom', 'chord'): [('violas', 0, -14, 0.3)],
        ('eureka', 'tune'): [('horns', 0, 10, 0.9), ('trumpets', 0, 2, 0.55), ('violins', 12, 0, 0.6),
                             ('choir', 0, 2, 0.7)],
        ('eureka', 'bass'): [('tuba', -12, 6, 0.8), ('basses', 0, 0, 0.55), ('timpani', 0, 6, 0.4)],
        ('eureka', 'chord'): [('trombones', 0, -6, 0.5), ('violas', 0, -8, 0.4), ('xylo', 12, -12, 0.3)],
    }
    B.perform(C.events, parts)
    # the tower window lights: a low chord and a creak
    B.play('cellos trem', 45, 0.0, 2.0, 70, gain=0.4)
    B.hit('gong scrape', 0.1, 90, gain=0.3)
    B.effects([(0, -4), (T_SCAN, 0), (M['scrawl'], -3), (M['days'], -2), (M['gloom'], -5), (M['spark'], 0),
               (M['eureka'] + 1, -6), (M['final'] - 0.5, 0)])
    # 1. the scanner hums along with its beam, bleeping as it crosses the toy
    _hum(B, T_SCAN, T_BUBBLE, lambda t: scan_pos(S, t), S)
    tt = np.arange(T_SCAN, T_BUBBLE, 0.01)
    pos = np.array([scan_pos(S, t) for t in tt])
    cross = tt[1:][np.diff(np.sign(pos - p_bench)) != 0]
    for t in cross:
        B.play('glock', 69, t, 0.2, 100, pan=S.pan(p_bench), gain=0.5)
        B.play('glock', 64, t + 0.09, 0.2, 90, pan=S.pan(p_bench), gain=0.4)
    # 2. bubbles: each pops with a bloop where it is
    for i, (t, p, c) in enumerate(bubbles(S)):
        f0 = 300 + 150 * c + 40 * (i % 5)
        _blip(B, t - 0.06, f0, f0 * 2.6, 0.09, 0.5, S.pan(p))
    # 3. the toy: the knife scrapes, the stuffing bursts
    B.hit('scrape', T_CUT - 0.8, 100, gain=0.5, pan=S.pan(p_bench), fx=True)
    B.hit('slapstick', T_CUT, 115, gain=0.8, pan=S.pan(p_bench))
    B.whoosh(T_CUT, 0.5, up=True, pan=S.pan(p_bench), gain=0.7)
    # 4. the ornament: two taps on glass, then it shatters
    for tp in (T_TAP, T_TAP + 0.42):
        B.play('glock', 72, tp, 0.2, 90, pan=S.pan(p_bench), gain=0.45)
        B.hit('triangle', tp, 80, gain=0.3, pan=S.pan(p_bench))
    B.shatter(T_SHATTER, pan=S.pan(p_bench), gain=1.0)
    # 5. the snowflake twinkles (celesta), then melts at a touch: a ping and a sad slide down, a drip
    for k, m in enumerate((88, 91, 95, 91, 88, 95, 98, 91)):
        B.play('celesta', m - 12, T_FLAKE + 0.2 + 0.28 * k, 0.4, 80, gain=0.45)
    B.hit('triangle', T_TOUCH, 100, gain=0.5, pan=S.pan(p_bench))
    B.M.add('fx', slide(0, 1.2, 1400, 350, 1.3, amp=0.22), T_TOUCH + 0.05, 0.9, S.pan(p_bench))
    _blip(B, T_TOUCH + 1.5, 900, 300, 0.12, 0.5, S.pan(p_bench - 260))
    # 6. the candy cane: a twirl, then a crack as he snaps it
    B.whoosh(T_CANE, 1.4, up=True, pan=0.0, gain=0.5)
    B.hit('wood', T_SNAP, 124, gain=0.9, pan=S.pan(p_bench))
    B.hit('slapstick', T_SNAP + 0.03, 120, gain=0.7, pan=S.pan(p_bench))
    # 7. the chalk scratching left to right with the pen
    x0, x1 = S.at('Left', 0), S.L
    t0, t1 = M['scrawl'], M['days'] - 0.3
    rng = np.random.default_rng(77)
    t = t0
    while t < t1:
        pen = x0 + (x1 - x0) * (t - t0) / (t1 - t0)
        B.hit('guiro', t, int(rng.integers(70, 110)), gain=0.7, pan=S.pan(pen), fx=True)
        t += rng.uniform(0.12, 0.3)
    # 8. days and nights: a clock ticking ever faster
    td0, td1 = M['days'], M['gloom']
    k = 0
    t = td0
    while t < td1:
        B.hit('claves' if k % 2 else 'wood', t, 100, gain=0.5, pan=0.0)
        u = (t - td0) / (td1 - td0)
        t += 0.5 / (1 + 4 * u)
        k += 1
    # 9. crumpled notes tossed to the wings
    for i, (t, sd) in enumerate(tosses(S)):
        _crumple(B, t - 0.2, sd * 0.3, 300 + i)
        B.whoosh(t, 0.6, up=False, pan=sd * 0.7, gain=0.35)
    # 10. the spark: a bell tree climbing into a ping, the cymbal swelling to the flash
    B.hit('bell tree', M['spark'] + 0.1, 90, gain=0.5, pan=S.pan(p_king))
    B.hit('triangle', M['spark'] + 0.3, 110, gain=0.5, pan=S.pan(p_king))
    B.hit('cymbal swell', M['eureka'] - 1.3, 110, gain=0.6)
    # 11. EUREKA
    B.boom(M['eureka'], pan=0.0, gain=0.9)
    B.hit('crash', M['eureka'], 124, gain=0.7)
    B.hit('crash', M['final'] - 0.05, 124, gain=0.7)
    B.hit('bass drum', M['final'] - 0.05, 124, gain=0.7)
    B.hit('timpani roll', M['final'] - 1.5, 100, gain=0.4)
    B.finish()
