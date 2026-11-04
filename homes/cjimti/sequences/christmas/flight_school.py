"""Reindeer Flight School: Night. Side and Left are snowy ground, the porch is the sky, and the Right wing is the
runway: its blue lights blink on one by one from the free end and start chasing toward the porch, where the last
two burn red at the edge. Three young reindeer (red, green and blue harnesses) trot in from the free end of Right
and line up. Ready, set: the first gallops down the runway, trips at the edge and tumbles head over heels into the
snowbank on Porch Right, a white burst, dizzy stars circling, and trudges back covered in snow. The second gets
airborne: up Porch Right, over the Porch Front, a wobbly loop-the-loop, a panicky turn back and a crash-landing in
a heap on the runway. The third gallops, skids to a stop at the very edge, teeters, freezes, gulps, and scurries
back. Then sleigh bells: an elder flies in low from the free end of Right, climbs over the porch, turns a perfect
loop, sails along Left and up Side and out the back of the house, comes round and glides in from the free end of
Right to land without a sound. The three line up again together, the elder rings them off, and they gallop in
formation, harness bells ringing, lift off the end of the runway and fly the whole house, out the back, round, and
over it all again, away up Side into the night in a long trail of sparkle; the house fills with stars.

The music is original, at 120 bpm in D. Each runway light comes on with a glock note; the trot is wood blocks.
Every attempt has its own "ready, set" on the timpani and a galloping ostinato on xylophone and log drums as the
lights chase. The trip is a slide whistle and a cymbal into the snowbank's poof, the dizzy stars a cuckoo on the
glock, the trudge a sulky bassoon. The second flight climbs on trumpets, loops on a harp glissando, wobbles on
tremolo strings and crashes on slapstick and ratchet. The third skids on a guiro, teeters to a ticking bassoon and
gulps on a low pizzicato. The elder brings sleigh bells and the flight theme on horns; the formation flight is
that theme for the full band, sleigh bells on every beat, and it fades with them into the night before the last
chord."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'CH19'
TITLE = 'Reindeer Flight School'
KIND = 'show'
DESCRIPTION = ('Three young reindeer practise take-offs on the runway: one tumbles into a snowbank, one loops and '
               'crash-lands, one is too scared to go. After an elder shows them how, all three fly a lap of the '
               'house together and away into the night.')
VOICEOVER = "Runway lights on, harness bells on: it's the first day of flight school for three young reindeer."

SNOW = hexc('#a8c8ff')
SKY = hexc('#0c24a8')
STAR = hexc('#fff4d8')
TARMAC = hexc('#18284a')
RUNWAY = hexc('#2858ff')
EDGE = hexc('#ff1808')
WHITE = hexc('#ffffff')
BODY = hexc('#e06008')
HEAD = hexc('#ffb070')
GOLD = hexc('#ffb000')
HARNESS = np.array([hexc('#ff1010'), hexc('#10e030'), hexc('#2070ff'), GOLD])
SPARK = np.array([GOLD, WHITE, hexc('#ffe080')])

D = 86.0
SEED = 19
BEAT = 0.5                                       # 120 bpm
BAR = 4 * BEAT


def at(bar, beat=0.0):
    return bar * BAR + beat * BEAT


RIGHT0 = 2036.0                                  # the runway: the Right wing, from its free end toward the porch
LIGHTS = np.linspace(2490, 2062, 12)             # runway lights; the last two are the red edge lights
SNOWBANK = 1965.0                                # on Porch Right, just past the end of the runway
EXIT, ENTER = -40.0, 2560.0                      # off the back of Side; in again past the free end of Right

T_LIGHTS = [0.5 + 0.25 * k for k in range(12)]
A_READY, A_GO, A_TRIP, A_SNOW = at(3), at(4), at(5), at(5, 2)
A_SHAKE = 16.5
B_READY, B_GO, B_LIFT, B_LOOP, B_TURN, B_CRASH = at(8), at(9), at(10), 22.5, 24.0, at(13)
C_READY, C_GO, C_SKID, C_GULP = at(15), at(16), at(17), at(18, 2)
E_IN, E_LOOP, E_OUT, E_BACK, E_LAND = at(20), 42.5, at(24), at(24, 2), at(25, 2)
F_LINE, F_READY, F_GO, F_LIFT, F_OUT, F_BACK, F_GONE = at(26), at(27), at(28), at(29), 63.0, at(32), at(36)
T_CHORD = at(41)
FORM = (0.0, 28.0, 56.0)                         # formation spacing behind the leader (A)


def seg(t, t0, t1, p0, p1, ease='lin'):
    u = np.clip((t - t0) / (t1 - t0), 0, 1)
    if ease == 'in':
        u = u * u
    elif ease == 'out':
        u = 1 - (1 - u) ** 2
    elif ease == 'smooth':
        u = u * u * (3 - 2 * u)
    return p0 + (p1 - p0) * u


def track(t, plan):
    """plan: [(t0, t1, p0, p1, ease)] in order; before the first, the first p0; between, the last p1; NaN where p is None."""
    if t < plan[0][0]:
        return plan[0][2]
    for t0, t1, p0, p1, e in plan:
        if t < t1:
            if t < t0:
                return prev
            if p0 is None:
                return np.nan
            return seg(t, t0, t1, p0, p1, e)
        prev = p1
    return prev


def loop_path(t, t0, t1, p0, dist, r):
    """Along the path by `dist` over [t0, t1] with a loop in it: it swings back by about r on the way."""
    u = np.clip((t - t0) / (t1 - t0), 0, 1)
    return p0 + dist * u + r * np.sin(2 * np.pi * u) * np.sign(-dist)


def cast():
    """Frame by frame: where each of A, B, C and the elder is (NaN off the house), which way they face, whether
    they are in the air."""
    F = nframes(D)
    P = np.full((F, 4), np.nan)
    AIR = np.zeros((F, 4), bool)
    for f in range(F):
        t = f * DT
        # A: trip, tumble, snowbank, trudge back; formation leader
        a = track(t, [(1.0, 3.0, 2580.0, 2380.0, 'out'), (A_GO, A_TRIP, 2380.0, 2080.0, 'in'),
                      (A_TRIP, A_SNOW, 2080.0, SNOWBANK, 'out'), (13.0, A_SHAKE, SNOWBANK, 2380.0, 'lin'),
                      (F_LINE, F_LINE + 2, 2380.0, 2300.0, 'smooth'), (F_GO, F_LIFT, 2300.0, 2040.0, 'in'),
                      (F_LIFT, F_OUT, 2040.0, EXIT - 70, 'lin'), (F_OUT, F_BACK, None, None, 'lin'),
                      (F_BACK, F_GONE, ENTER, EXIT - 70, 'lin'), (F_GONE, D + 1, None, None, 'lin')])
        if A_TRIP <= t < A_SNOW:                 # head over heels: little bounces
            a += 10 * abs(np.sin(3 * np.pi * (t - A_TRIP) / (A_SNOW - A_TRIP)))
        if 13.0 <= t < A_SHAKE:                  # trudging: a limp
            a += 4 * abs(np.sin(2 * np.pi * 2 * t))
        P[f, 0] = a
        AIR[f, 0] = F_LIFT <= t < F_GONE
        # B: lift-off, a wobbly loop, a turn back, a crash
        if t < B_LIFT or t >= B_CRASH:
            b = track(t, [(1.4, 3.4, 2610.0, 2410.0, 'out'), (B_GO, B_LIFT, 2410.0, 2040.0, 'in'),
                          (B_CRASH, B_CRASH + 0.01, 2230.0, 2230.0, 'lin'), (27.5, 31.0, 2230.0, 2410.0, 'lin'),
                          (F_LINE, F_LINE + 2, 2410.0, 2300.0 + FORM[1], 'smooth'),
                          (F_GO, F_LIFT, 2300.0 + FORM[1], 2040.0 + FORM[1], 'in'),
                          (F_LIFT, F_OUT, 2040.0 + FORM[1], EXIT - 70 + FORM[1], 'lin'), (F_OUT, F_BACK, None, None, 'lin'),
                          (F_BACK, F_GONE, ENTER + FORM[1], EXIT - 70 + FORM[1], 'lin'), (F_GONE, D + 1, None, None, 'lin')])
            if B_CRASH <= t < B_CRASH + 0.8:     # in a heap: bounce, bounce
                b += 14 * abs(np.sin(3 * np.pi * (t - B_CRASH) / 0.8)) * (1 - (t - B_CRASH) / 0.8)
            if 27.5 <= t < 31.0:
                b += 4 * abs(np.sin(2 * np.pi * 2 * t))
        elif t < 21.5:
            b = seg(t, B_LIFT, 21.5, 2040.0, 1660.0)
        elif t < B_LOOP:
            b = seg(t, 21.5, B_LOOP, 1660.0, 1420.0)
        elif t < B_TURN:
            b = loop_path(t, B_LOOP, B_TURN, 1420.0, -110.0, 75.0) + 8 * np.sin(2 * np.pi * 5 * t)
        else:
            b = seg(t, B_TURN, B_CRASH, 1310.0, 2230.0, 'smooth') + 18 * np.sin(2 * np.pi * 3 * t) * \
                (1 - smoothstep(B_CRASH - 0.4, B_CRASH, t))
        P[f, 1] = b
        AIR[f, 1] = (B_LIFT <= t < B_CRASH) or (F_LIFT <= t < F_GONE)
        # C: gallop, skid, teeter, freeze, scurry back
        c = track(t, [(1.8, 3.8, 2640.0, 2440.0, 'out'), (C_GO, C_SKID, 2440.0, 2060.0, 'in'),
                      (C_SKID, C_SKID + 0.4, 2060.0, 2045.0, 'out'), (38.0, 40.0, 2045.0, 2440.0, 'in'),
                      (F_LINE, F_LINE + 2, 2440.0, 2300.0 + FORM[2], 'smooth'),
                      (F_GO, F_LIFT, 2300.0 + FORM[2], 2040.0 + FORM[2], 'in'),
                      (F_LIFT, F_OUT, 2040.0 + FORM[2], EXIT - 70 + FORM[2], 'lin'), (F_OUT, F_BACK, None, None, 'lin'),
                      (F_BACK, F_GONE, ENTER + FORM[2], EXIT - 70 + FORM[2], 'lin'), (F_GONE, D + 1, None, None, 'lin')])
        if C_SKID + 0.4 <= t < C_GULP:           # teetering on the edge
            c -= 7 * np.sin(2 * np.pi * 1.5 * (t - C_SKID - 0.4)) * (1 - smoothstep(36.4, C_GULP, t))
        if C_GULP <= t < 38.0:
            c += 1.5 * np.sin(2 * np.pi * 11 * t)
        P[f, 2] = c
        AIR[f, 2] = F_LIFT <= t < F_GONE
        # the elder: in low from the free end, a perfect loop, round the house, a soft landing
        if t < E_IN:
            e = np.nan
        elif t < 41.5:
            e = seg(t, E_IN, 41.5, ENTER, 2040.0)
        elif t < E_LOOP:
            e = seg(t, 41.5, E_LOOP, 2040.0, 1660.0)
        elif t < 43.5:
            e = loop_path(t, E_LOOP, 43.5, 1660.0, -260.0, 70.0)
        elif t < E_OUT:
            e = seg(t, 43.5, E_OUT, 1400.0, EXIT)
        elif t < E_BACK:
            e = np.nan
        else:
            e = track(t, [(E_BACK, E_LAND, ENTER, 2300.0, 'out'), (E_LAND + 1.0, E_LAND + 3.5, 2300.0, 2495.0, 'smooth')])
        P[f, 3] = e
        AIR[f, 3] = (E_IN <= t < E_LAND)
    P[P > G_LEN + 30] = np.nan
    FACE = -np.ones((F, 4))
    v = np.diff(P, axis=0, prepend=P[:1])
    for f in range(1, F):
        FACE[f] = np.where(v[f] > 0.4, 1.0, np.where(v[f] < -0.4, -1.0, FACE[f - 1]))
    return P, AIR, FACE


G_LEN = 2512.0


def chase_phase(F):
    """How far the runway lights' chase has run, frame by frame: slow, and fast while someone gallops."""
    t = np.arange(F) * DT
    speed = np.full(F, 140.0)
    for g0, g1 in ((A_GO, A_TRIP), (B_GO, B_LIFT), (C_GO, C_SKID), (F_GO, F_LIFT)):
        speed[(t >= g0 - 0.5) & (t < g1 + 0.3)] = 520.0
    return np.cumsum(speed) * DT


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]
    N = G.N
    ground = x < 892
    sky = (x >= 892) & (x < RIGHT0)
    runway = x >= RIGHT0
    P, AIR, FACE = cast()
    phase = chase_phase(F)
    stars = (rng.random(N) < 0.09) & sky
    star_tw = Flicker(rng, N, 0.2, 1.0)
    glint = Flicker(rng, N, 0.5, 2.0)
    fin_stars = rng.random(N) < 0.22
    fin_col = SPARK[rng.integers(0, len(SPARK), N)]
    sp_tw = rng.uniform(0, 2 * np.pi, 200)
    burst_v = rng.uniform(-1, 1, 60)
    scale = np.array([1.0, 1.0, 1.0, 1.35])
    nfl = 45
    fl_x = rng.uniform(0, G.length, nfl)
    fl_v = rng.uniform(12, 30, nfl)
    fl_ph = rng.uniform(0, 2 * np.pi, nfl)

    def splat(fr, pos, inten, cols):
        ok = ~np.isnan(pos) & (inten > 0) & (pos > -5) & (pos < G.length + 5)
        if not ok.any():
            return fr
        pos, inten, cols = pos[ok], inten[ok], cols[ok]
        j = np.clip(np.searchsorted(x, pos) - 1, 0, N - 2)
        u = np.clip((pos - x[j]) / (x[j + 1] - x[j]), 0, 1)
        for jj, w in ((j, 1 - u), (j + 1, u)):
            np.add.at(fr, jj, (perc(inten) * w)[:, None] * cols)
        return fr

    for f in range(F):
        t = f * DT
        master = keys(t, [(0, 0.0), (0.8, 1.0), (D - 2.0, 1.0), (D - 0.2, 0.0)])
        # snowy ground, night sky with stars over the porch, the dark runway
        fr = light(SNOW, 0.24 * (1 + 0.2 * glint(t)) * ground)
        fr += light(SKY, 0.22 * sky * np.ones(N)) + light(STAR, stars * np.clip(0.45 + 0.35 * star_tw(t), 0, 1))
        fr += light(TARMAC, 0.16 * runway)
        # snow drifting down over everything
        fx_ = (fl_x - fl_v * t + 14 * np.sin(0.7 * t + fl_ph)) % G.length
        fi = 0.38 + 0.18 * np.sin(1.9 * t + fl_ph)
        fr = splat(fr, fx_, fi, np.tile(WHITE, (nfl, 1)))
        # the snowbank on Porch Right
        bank = np.exp(-((x - SNOWBANK) / 22) ** 2)
        fr += light(WHITE, 0.4 * bank)

        # runway lights: on one by one, then chasing toward the porch
        for k, lx in enumerate(LIGHTS):
            on = smoothstep(T_LIGHTS[k], T_LIGHTS[k] + 0.08, t)
            if on <= 0:
                continue
            edge = k >= 10
            ch = 0.0 if edge else np.exp(-((((2490 - lx) - phase[f]) % 160) - 0) ** 2 / 300)
            flash = np.exp(-(t - T_LIGHTS[k]) / 0.15) if t >= T_LIGHTS[k] else 0
            if edge:
                inten = on * (0.75 + 0.25 * np.sin(2 * np.pi * 1.5 * t))
                fr += light(EDGE, inten * np.exp(-((x - lx) / 4) ** 2))
            else:
                inten = on * (0.5 + 0.5 * ch) + 0.5 * flash
                fr += light(RUNWAY, inten * np.exp(-((x - lx) / 4) ** 2))
                fr += light(WHITE, (0.6 * ch * on + 0.5 * flash) * np.exp(-((x - lx) / 3) ** 2))

        # sparkle trails behind anyone flying
        for c in range(4):
            n_tr = 100 if t >= F_LIFT and c < 3 else 48
            ks = np.arange(1, n_tr)
            fs = f - ks
            ok = fs >= 0
            fs = np.clip(fs, 0, None)
            pos = np.where(ok & AIR[fs, c], P[fs, c], np.nan)
            age = ks / n_tr
            tw = 0.5 + 0.5 * np.sin(11 * t + sp_tw[ks])
            inten = (1 - age) ** 1.3 * (0.35 + 0.6 * tw) * 0.9
            cols = np.where((ks % 3 == 0)[:, None], HARNESS[c], SPARK[ks % len(SPARK)])
            fr = splat(fr, pos + 6 * np.sin(ks * 1.3), inten, cols)

        # the reindeer
        for c in range(4):
            p = P[f, c]
            if np.isnan(p):
                continue
            fc = FACE[f, c]
            s = scale[c]
            r = (x - p) * fc / s
            run = 0.85 + 0.15 * abs(np.sin(2 * np.pi * 4 * t + c))
            snowy = 0.0
            if c == 0 and A_SNOW <= t < A_SHAKE + 0.3:
                snowy = 0.7
            fr = fr * (1 - np.exp(-(r / 15) ** 2))[:, None]
            body = np.exp(-((r + 2) / 7) ** 2)
            head = np.exp(-((r - 9) / 3.5) ** 2)
            har = np.exp(-((r + 1) / 2.2) ** 2)
            up = 1.15 if AIR[f, c] else 1.0
            fr += light(lerp(BODY, WHITE, snowy), 0.8 * run * up * body)
            fr += light(lerp(HEAD, WHITE, snowy), 0.85 * run * up * head)
            fr += light(HARNESS[c], 0.95 * har)
            fr += light(WHITE, 0.7 * np.exp(-((r - 6) / 1.6) ** 2))          # antlers catching the light
            if c == 3 or (t >= F_GO and t < F_GONE):                         # harness bells glinting
                fr += light(GOLD, (0.5 + 0.5 * np.sin(2 * np.pi * 6 * t)) * np.exp(-((r + 6) / 2) ** 2))
            if AIR[f, c]:
                fr += light(GOLD, 0.25 * np.exp(-(r / 18) ** 2))

        # ready, set: the one about to go blinks twice
        for k, (tr_, who) in enumerate(((A_READY, 0), (B_READY, 1), (C_READY, 2))):
            for e in (0, 2):
                tb = tr_ + e * BEAT
                if tb <= t < tb + 0.4 and not np.isnan(P[f, who]):
                    fr += light(WHITE, 0.8 * np.exp(-(t - tb) / 0.12) * np.exp(-((x - P[f, who]) / 14) ** 2))
        if F_READY <= t < F_GO:
            for e in (0, 2):
                tb = F_READY + e * BEAT
                if tb <= t < tb + 0.4:
                    fr += light(GOLD, 0.8 * np.exp(-(t - tb) / 0.12) * np.exp(-((x - P[f, 3]) / 18) ** 2))

        # the snowbank burst
        if A_SNOW <= t < A_SNOW + 1.5:
            ts = t - A_SNOW
            fr += light(WHITE, np.exp(-ts / 0.15) * np.exp(-((x - SNOWBANK) / (20 + 300 * ts)) ** 2))
            px_ = SNOWBANK + burst_v * 420 * (1 - np.exp(-3 * ts))
            fr = splat(fr, px_, np.full(len(px_), 0.85 * (1 - ts / 1.5)), np.tile(SNOW, (len(px_), 1)))
        # dizzy stars over A in the snowbank, and over B in his heap
        for c, t0, t1 in ((0, A_SNOW + 0.3, 13.2), (1, B_CRASH + 0.6, 27.6)):
            if t0 <= t < t1 and not np.isnan(P[f, c]):
                for k in range(2):
                    sx = P[f, c] + 13 * np.sin(2 * np.pi * 1.6 * t + np.pi * k)
                    fr += light(GOLD, 0.9 * np.exp(-((x - sx) / 2.5) ** 2))
        # the crash
        if B_CRASH <= t < B_CRASH + 0.6:
            fr += light(WHITE, np.exp(-(t - B_CRASH) / 0.12) * np.exp(-((x - 2230) / 45) ** 2))
            fr += light(GOLD, 0.8 * np.exp(-(t - B_CRASH) / 0.25) * np.exp(-((x - 2230) / 90) ** 2))
        # the skid: sparks off the hooves
        if C_SKID <= t < C_SKID + 0.5:
            for k in range(4):
                sx = 2060 + 40 * (t - C_SKID) * (k + 1) + 10 * k
                fr += light(GOLD, (1 - (t - C_SKID) / 0.5) * np.exp(-((x - sx) / 2.5) ** 2))
        # A shakes off the snow
        if A_SHAKE <= t < A_SHAKE + 0.8:
            ts = t - A_SHAKE
            for k in range(8):
                sx = 2380 + (k - 3.5) * 14 * (1 + 6 * ts)
                fr += light(SNOW, 0.8 * (1 - ts / 0.8) * np.exp(-((x - sx) / 2.5) ** 2))

        # finale: the night fills with stars; the runway lights cheer on the downbeats
        if t >= F_GONE - 2:
            fl = keys(t, [(F_GONE - 2, 0.0), (F_GONE + 3, 1.0)])
            tw2 = np.clip(0.4 + 0.5 * star_tw(t * 1.3), 0, 1)
            fr += perc(0.75 * fl * fin_stars * tw2)[:, None] * fin_col
            for k in range(4):
                tb = at(38 + k)
                if tb <= t < tb + 0.8:
                    fr += light(RUNWAY, 0.6 * np.exp(-(t - tb) / 0.25) * runway)
            if T_CHORD <= t < T_CHORD + 1.5:
                fr += light(GOLD, 0.45 * np.exp(-(t - T_CHORD) / 0.4) * np.ones(N))
        out[f][G.path] = np.clip(fr, 0, 1) * master
    return out


# ---- music: original, 120 bpm in D ----
FLIGHT = [
    [(0, 'A4', 1), (1, 'D5', 1), (2, 'F#5', 1.5), (3.5, 'E5', 0.5)],
    [(0, 'D5', 1), (1, 'B4', 1), (2, 'A4', 2)],
    [(0, 'G4', 1), (1, 'B4', 1), (2, 'E5', 1.5), (3.5, 'D5', 0.5)],
    [(0, 'C#5', 1), (1, 'E5', 1), (2, 'A4', 2)],
    [(0, 'A4', 1), (1, 'D5', 1), (2, 'F#5', 1.5), (3.5, 'G5', 0.5)],
    [(0, 'A5', 1), (1, 'F#5', 1), (2, 'D5', 2)],
    [(0, 'E5', 1), (1, 'G5', 1), (2, 'F#5', 1), (3, 'E5', 1)],
    [(0, 'D5', 3), (3, 'A4', 1)],
]
FLIGHT_CH = ['D', 'Bm', 'Em', 'A', 'D', 'D', 'A7', 'D']
CH = {'D': ('F#3', 'A3', 'D4'), 'Bm': ('F#3', 'B3', 'D4'), 'Em': ('G3', 'B3', 'E4'), 'A': ('E3', 'A3', 'C#4'),
      'A7': ('E3', 'G3', 'C#4'), 'G': ('G3', 'B3', 'D4'), 'Dm': ('F3', 'A3', 'D4')}
BASS = {'D': ('D2', 'A2'), 'Bm': ('B1', 'F#2'), 'Em': ('E2', 'B2'), 'A': ('A1', 'E2'), 'A7': ('A1', 'E2'),
        'G': ('G2', 'D2'), 'Dm': ('D2', 'A2')}
GALLOP = ['D5', 'A4', 'F#4', 'A4']
VAMP = [(0, 'D'), (1, 'G'), (2, 'A'), (3, 'D'), (5, 'A'), (6, 'Dm'), (7, 'Dm'), (8, 'A'), (9, 'D'), (14, 'D'), (16, 'D'),
        (19, 'D')]
LIGHT_NOTES = ['D4', 'E4', 'F#4', 'G4', 'A4', 'B4', 'C#5', 'D5', 'E5', 'F#5', 'A4', 'A4']


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    P, AIR, FACE = cast()

    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    horn_st = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    log = M.hits('Percussion/LogDrumHi_MedM*.wav')
    log_lo = M.hits('Percussion/LogDrumLo_MedM*.wav')
    block = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    ratchet = M.hits('Percussion/Ratchet1-Fast*.wav')
    guiro = M.hits('Percussion/Guiro-Fast*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[mp]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('tune', 0.36, 0.18), ('harm', 0.27, 0.26), ('bass', 0.42, 0.06), ('drums', 0.34, 0.1),
                            ('motif', 0.32, 0.2), ('perc', 0.38, 0.12), ('fx', 0.3, 0.16)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    L = G.length

    def pan_at(dd):
        if np.isnan(dd):
            return 0.0
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def where(c, t):
        return float(P[min(int(t / DT), len(P) - 1), c])

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def follow(sig, c, t0):                           # a mono signal panned along with a reindeer
        tt = t0 + np.arange(sig.shape[1]) / SR
        idx = np.clip((tt / DT).astype(int), 0, len(P) - 1)
        pp = P[idx, c]
        pans = np.array([pan_at(v) for v in pp[::480]])
        return mono(sig[0], np.repeat(pans, 480)[:sig.shape[1]])

    def tune(bars, k0, inst, bus='tune', vel=100, pan=0.0, gain=1.0, octave=0, long=None):
        for j, b in enumerate(bars):
            for e, m, ln in b:
                pl = long if (long is not None and ln >= 1.5) else inst
                M.add(bus, pl.play(n(m) + octave, vel, dur=ln * BEAT * 0.92), at(k0 + j, e), gain, pan)

    def oompah(k0, chords, vel=96, gain=1.0):
        for j, c in enumerate(chords):
            k = k0 + j
            for e in (0, 2):
                M.add('bass', tuba.play(n(BASS[c][e // 2]), vel), at(k, e), gain)
                M.add('drums', bd.play(vel - 10), at(k, e), 0.6 * gain)
            for e in (1, 3):
                for m in CH[c]:
                    M.add('harm', horn_st.play(n(m), vel - 15), at(k, e), 0.45 * gain, -0.2)
                M.add('drums', snare.play(vel - 25), at(k, e), 0.4 * gain, 0.1)

    def pad(t0, c, dur, vel=65, gain=1.0):
        for m in CH[c]:
            M.add('harm', vln.play(n(m) + 12, vel, dur=dur, release=0.5), t0, 0.35 * gain, 0.25)
        M.add('harm', vc.play(n(BASS[c][0]) + 12, vel, dur=dur, release=0.5), t0, 0.5 * gain, -0.25)

    def ready(t0, c):                                 # ready ... set ...
        for e, v in ((0, 85), (2, 100)):
            M.add('perc', timp.play(v, pitch=-2 + 2 * (e // 2)), t0 + e * BEAT, 0.7, pan_at(where(c, t0)))
        r = sroll.play(80, dur=BEAT * 1.9)
        M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, t0 + 2.1 * BEAT, 0.5, pan_at(where(c, t0)))

    def gallop(t0, t1, c, vel=95):                    # the run: xylophone ostinato, hooves, galloping
        k = 0
        t = t0
        while t < t1:
            p = pan_at(where(c, t))
            M.add('motif', xylo.play(n(GALLOP[k % 4]), vel), t, 0.5, p)
            M.add('perc', (log if k % 2 else log_lo).play(vel - 5), t, 0.6, p)
            if k % 4 == 3:
                M.add('perc', log.play(vel - 15), t + BEAT / 8, 0.4, p)
            k += 1
            t += BEAT / 2

    # under the lessons: a light vamp, pizzicato bass and staccato clarinets (it drops out for the comic beats)
    for k, c in VAMP:
        for e in (0, 2):
            M.add('bass', cello.play(n(BASS[c][e // 2]), 95), at(k, e), 0.8)
        for e in (1, 3):
            for m in CH[c]:
                M.add('harm', clar.play(n(m) + 12, 80, dur=0.2), at(k, e), 0.45, 0.2)
                M.add('harm', pizz.play(n(m) + 12, 75), at(k, e), 0.35, -0.2)
        M.add('drums', snare.play(60), at(k, 1), 0.3, 0.1)
        M.add('drums', snare.play(60), at(k, 3), 0.3, 0.1)

    # ---- 0-6: the runway lights come on; three young reindeer trot in ----
    for k in range(3):
        pad(at(k), ('D', 'G', 'A')[k], BAR * 0.98, 55)
    for k, tl in enumerate(T_LIGHTS):
        M.add('motif', glock.play(n(LIGHT_NOTES[k]), 78), tl, 0.5, pan_at(LIGHTS[k]))
    M.add('perc', tri.play(80), T_LIGHTS[10], 0.5, pan_at(LIGHTS[10]))
    for c in range(3):
        for k in range(16):
            t = 1.0 + 0.4 * c + k * 0.125
            M.add('perc', block.play(70), t, 0.35, pan_at(where(c, t)))

    # ---- 6-17: the first: ready, set, gallop, trip, into the snowbank ----
    ready(A_READY, 0)
    oompah(4, ['D'], 96)
    gallop(A_GO, A_TRIP, 0)
    pa = pan_at(2080)
    M.add('fx', slide(0.0, 0.9, 1400, 260, 1.0, 0.45, 0.7), A_TRIP, 0.8, pa)
    for k in range(3):
        M.add('perc', slap.play(100 - 15 * k), A_TRIP + 0.33 * k, 0.6, pan_at(where(0, A_TRIP + 0.33 * k)))
    ps = pan_at(SNOWBANK)
    M.add('perc', crash.play(110), A_SNOW, 0.55, ps)
    M.add('drums', bd.play(115), A_SNOW, 0.9, ps)
    M.add('fx', whoosh(0.9, 4000, 400, 1.0, seed=11), A_SNOW, 0.7, ps)
    for k in range(4):                                # dizzy: a cuckoo on the glock
        M.add('motif', glock.play(n(('A5', 'F#5')[k % 2]), 75), A_SNOW + 0.5 + 0.4 * k, 0.4, ps)
    for e, m in ((0, 'D3'), (1, 'C#3'), (2, 'C3'), (3, 'B2')):
        M.add('tune', bsn.play(n(m), 90, dur=0.4), at(6, e), 0.7, ps)
    for k in range(7):                                # the trudge back: a sulky bassoon and tuba
        t = 13.0 + 0.5 * k
        M.add('tune', bsn.play(n(('D3', 'A2', 'Bb2', 'A2', 'D3', 'A2', 'D2')[k]), 92, dur=0.35), t, 0.8,
              pan_at(where(0, t)))
        M.add('bass', tuba.play(n(('D2', 'A1')[k % 2]), 80), t, 0.5)
    M.add('perc', shake.play(80), A_SHAKE, 0.5, pan_at(2380))
    M.add('perc', tri.play(60), A_SHAKE + 0.1, 0.4, pan_at(2380))

    # ---- 16-31: the second: airborne, a wobbly loop, a crash ----
    ready(B_READY, 1)
    pad(at(8), 'A', BAR, 60)
    gallop(B_GO, B_LIFT, 1)
    for k, m in enumerate(('D4', 'F#4', 'A4', 'D5')):
        M.add('tune', tpt.play(n(m), 105, dur=0.3), B_LIFT + 0.15 * k, 0.7, pan_at(2040))
    M.add('tune', tpt_s.play(n('F#5'), 100, dur=1.2, release=0.3), B_LIFT + 0.6, 0.6, pan_at(1800))
    oompah(10, ['D', 'G'], 95)
    w = whoosh(B_LOOP - B_LIFT, 400, 2500, 0.8, seed=20)
    M.add('fx', follow(w, 1, B_LIFT), B_LIFT, 0.7)
    gl = [n(m) for m in ('D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'F#5', 'D5', 'A4', 'F#4', 'D4')]
    for k, m in enumerate(gl):                        # the loop: a harp glissando up and over
        t = B_LOOP + 1.5 * k / len(gl)
        M.add('harm', harp.play(m, 85), t, 0.8, pan_at(where(1, t)))
    for m in ('A4', 'C5', 'Eb5'):
        M.add('harm', trem.play(n(m), 75, dur=B_CRASH - B_TURN, release=0.1), B_TURN, 0.6, pan_at(1800))
    M.add('fx', slide(0.0, 0.5, 900, 1500, 0.55, 0.35), B_TURN, 0.6, pan_at(1310))
    w = whoosh(B_CRASH - B_TURN, 2500, 500, 0.8, seed=24)
    M.add('fx', follow(w, 1, B_TURN), B_TURN, 0.7)
    pb = pan_at(2230)
    M.add('perc', crash.play(115), B_CRASH, 0.5, pb)
    M.add('drums', bd.play(118), B_CRASH, 0.9, pb)
    M.add('perc', ratchet.play(100, dur=0.6), B_CRASH + 0.05, 0.6, pb)
    for k in range(3):
        M.add('perc', slap.play(110 - 20 * k), B_CRASH + 0.27 * k, 0.6, pb)
    M.add('tune', bone.play(n('A3'), 95, dur=0.4), B_CRASH + 0.9, 0.7, pb)
    M.add('tune', bone.play(n('Ab3'), 95, dur=0.4), B_CRASH + 1.35, 0.7, pb)
    M.add('tune', bone.play(n('G3'), 95, dur=1.1, release=0.3), B_CRASH + 1.8, 0.7, pb)
    for k in range(4):
        M.add('motif', glock.play(n(('A5', 'F#5')[k % 2]), 70), B_CRASH + 0.7 + 0.4 * k, 0.35, pb)
    for k in range(7):                                # hobbling back
        t = 27.5 + 0.5 * k
        M.add('perc', block.play(75), t, 0.4, pan_at(where(1, t)))
        M.add('motif', pizz.play(n(('D4', 'A3')[k % 2]), 80), t, 0.5, pan_at(where(1, t)))
    pad(at(14), 'D', BAR, 55)

    # ---- 30-40: the third: gallop, skid, teeter, gulp, scurry back ----
    ready(C_READY, 2)
    oompah(15, ['A'], 92)
    gallop(C_GO, C_SKID, 2)
    pc = pan_at(2050)
    M.add('perc', guiro.play(110, dur=0.5), C_SKID, 0.8, pc)
    M.add('fx', slide(0.0, 0.4, 1600, 700, 0.45, 0.4), C_SKID, 0.6, pc)
    M.add('perc', choke.play(80), C_SKID + 0.4, 0.3, pc)
    for k in range(6):                                # teetering: tick, tock
        t = C_SKID + 0.4 + 0.333 * k
        M.add('tune', bsn.play(n(('A2', 'E3')[k % 2]), 90, dur=0.25), t, 0.8, pc)
        M.add('perc', block.play(70), t, 0.4, pc)
    M.add('harm', trem.play(n('E5'), 60, dur=2.5, release=0.2), C_SKID + 0.4, 0.4, pc)
    M.add('harm', trem.play(n('F5'), 60, dur=2.5, release=0.2), C_SKID + 0.4, 0.4, pc)
    M.add('bass', cello.play(n('A1') + 12, 110), C_GULP, 0.9, pc)               # gulp
    M.add('fx', slide(0.0, 0.15, 300, 520, 0.2, 0.4), C_GULP + 0.02, 0.6, pc)
    for k in range(8):                                # scurrying back on tiptoe
        t = 38.0 + 0.25 * k
        M.add('motif', pizz.play(n(('A4', 'F#4', 'E4', 'D4', 'C#4', 'B3', 'A3', 'D4')[k]), 80), t, 0.5,
              pan_at(where(2, t)))

    # ---- 40-54: sleigh bells: the elder's demonstration ----
    M.add('perc', shake.play(110), E_IN - 0.4, 0.6, 0.8)
    for k in range(int((E_OUT - E_IN) / BEAT)):
        t = E_IN + k * BEAT
        M.add('perc', sleigh.play(100 if k % 2 == 0 else 80), t, 0.4, pan_at(where(3, t)))
    for j, c in enumerate(FLIGHT_CH[:4]):
        pad(at(20 + j), c, BAR * 0.98, 75)
        for e in (0, 2):
            M.add('bass', tuba_s.play(n(BASS[c][e // 2]), 92, dur=0.9), at(20 + j, e), 0.6)
    tune(FLIGHT[:4], 20, horn, 'tune', 100, 0.0)
    tune(FLIGHT[:4], 20, flute, 'tune', 80, 0.2, gain=0.5)
    gl = [n(m) for m in ('D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6', 'A5', 'F#5', 'D5', 'A4', 'F#4', 'D4')]
    for k, m in enumerate(gl):                        # the perfect loop
        t = E_LOOP + 1.0 * k / len(gl)
        M.add('harm', harp.play(m, 92), t, 0.9, pan_at(where(3, t)))
    w = whoosh(E_OUT - E_IN, 500, 2200, 0.7, seed=40)
    M.add('fx', follow(w, 3, E_IN), E_IN, 0.5)
    M.add('perc', shake.play(70), E_OUT, 0.3, -0.85)                             # far away round the back
    M.add('perc', shake.play(95), E_BACK - 0.2, 0.5, 0.85)
    M.add('motif', chimes.play(90), E_BACK, 0.4, 0.8)
    tune([[(0, 'E5', 1), (1, 'C#5', 1), (2, 'D5', 2)]], 25, horn, 'tune', 95, 0.5)
    for m in ('D3', 'A3', 'F#4'):
        M.add('harm', vln.play(n(m) + 12, 75, dur=3.0, release=0.8), E_LAND, 0.4, 0.5)
    M.add('perc', tri.play(85), E_LAND, 0.5, pan_at(2300))
    M.add('bass', tuba_s.play(n('D2'), 85, dur=2.5, release=0.6), E_LAND, 0.6)

    # ---- 52-56: the three line up together; the elder rings them off ----
    oompah(26, ['A'], 92)
    for k in range(4):
        M.add('perc', block.play(80), F_LINE + 0.5 * k, 0.4, pan_at(2330))
    for e in (0, 2):
        M.add('perc', shake.play(105), F_READY + e * BEAT, 0.6, pan_at(2495))
        M.add('perc', timp.play(95 + 10 * e // 2, pitch=-2 + e), F_READY + e * BEAT, 0.7, pan_at(2330))
    r = troll.play(95, dur=BEAT * 1.9)
    M.add('perc', r * np.linspace(0.2, 1, r.shape[1]) ** 2, F_READY + 2.1 * BEAT, 0.6)

    # ---- 56-72: in formation, the flight theme for everyone ----
    gallop(F_GO, F_LIFT, 0, 105)
    oompah(28, FLIGHT_CH, 108)
    tune(FLIGHT, 28, tpt, 'tune', 108, -0.15, long=tpt_s)
    tune(FLIGHT, 28, horn, 'tune', 98, 0.15, gain=0.6, octave=-12)
    tune(FLIGHT, 28, glock, 'motif', 82, 0.0, gain=0.35)
    for j, c in enumerate(FLIGHT_CH):
        pad(at(28 + j), c, BAR * 0.98, 88)
    for k in range(int((F_GONE - F_GO) / BEAT)):      # harness bells on every beat, where they are
        t = F_GO + k * BEAT
        pp = pan_at(where(0, t)) if not np.isnan(where(0, t)) else 0.0
        M.add('perc', sleigh.play(105 if k % 2 == 0 else 85), t, 0.5, pp)
    M.add('drums', crash.play(118), F_LIFT, 0.5, pan_at(2040))
    M.add('perc', timp.play(115), F_LIFT, 0.8, pan_at(2040))
    w = whoosh(F_OUT - F_LIFT, 500, 3000, 0.8, seed=58)
    M.add('fx', follow(w, 0, F_LIFT), F_LIFT, 0.5)
    M.add('perc', shake.play(100), F_BACK - 0.3, 0.5, 0.85)
    w = whoosh(F_GONE - F_BACK, 600, 3500, 0.8, seed=64)
    M.add('fx', follow(w, 0, F_BACK), F_BACK, 0.5)
    for k, m in enumerate(('A4', 'D5', 'F#5', 'A5')):
        M.add('motif', glock.play(n(m), 85), F_LIFT + 0.12 * k, 0.5, pan_at(2000))

    # ---- 72-86: away into the night; the house fills with stars ----
    M.add('motif', chimes.play(100), F_GONE - 0.2, 0.6, -0.8)
    for k in range(8):                                # the bells, fading into the distance
        M.add('perc', sleigh.play(int(90 - 8 * k)), F_GONE + 0.5 * k, 0.4 * (1 - k / 8), -0.85)
    for j, c in enumerate(('G', 'D', 'A', 'D')):
        pad(at(36 + j), c, BAR * 0.98, 70 + 5 * j)
    tune([[(0, 'F#5', 2), (2, 'E5', 2)], [(0, 'D5', 2), (2, 'A4', 2)], [(0, 'B4', 1), (1, 'C#5', 1), (2, 'E5', 2)],
          [(0, 'D5', 4)]], 36, flute, 'tune', 85, 0.0)
    for k in range(12):
        M.add('motif', glock.play(n(('D5', 'F#5', 'A5', 'E5', 'B5', 'A5')[k % 6]), 60), at(36) + 0.66 * k, 0.3,
              -0.8 + 0.14 * k)
    for k in range(3):
        M.add('perc', tri.play(80), at(38 + k), 0.4, pan_at(2300))
        M.add('perc', shake.play(85), at(38 + k), 0.4, pan_at(2495))
        M.add('bass', tuba.play(n(('D2', 'A1', 'D2')[k]), 90), at(38 + k), 0.6)
    r = troll.play(95, dur=1.0)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_CHORD - 1.0, 0.6)
    for m in ('D4', 'F#4', 'A4'):
        M.add('tune', tpt_s.play(n(m), 110, dur=2.8, release=1.0), T_CHORD, 0.6)
    for m in ('D3', 'A3', 'F#4'):
        M.add('harm', horn.play(n(m), 108, dur=3.0, release=1.0), T_CHORD, 0.6)
        M.add('harm', vln.play(n(m) + 12, 95, dur=3.0, release=1.0), T_CHORD, 0.4)
    M.add('bass', tuba_s.play(n('D2'), 112, dur=3.0, release=1.0), T_CHORD, 0.9)
    M.add('perc', crash.play(110), T_CHORD, 0.5)
    M.add('drums', bd.play(110), T_CHORD, 0.8)
    M.add('perc', shake.play(110), T_CHORD, 0.6, pan_at(2495))
    M.add('motif', chimes.play(95), T_CHORD + 0.1, 0.5)
