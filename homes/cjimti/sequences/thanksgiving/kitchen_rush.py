"""Kitchen Rush: The last hour before dinner, on a clock that keeps speeding up. The Porch Front is the clock: a
gold bar that shrinks toward its middle, its pendulum swinging end to end on every beat. Side is the oven, heat
rolling out of it. The four other runs are the burners, lit one by one with a blue whoomp: potatoes on Left, gravy on
Porch Left, cranberries on Porch Right, green beans on Right. Each pot rolls, stripes rising from its middle to its
rims a stripe a beat, so they speed up with the clock and stand out more as the pot heats, and they boil over in
turn: foam surges out past both ends and rolls on down the whole roof, a lid clangs down and its ring runs out to the
ends. Timers ring on the oven, the clock and the counter. The mixer whips the potatoes into whirling stripes, smoke
creeps out of the oven, the smoke alarm flashes red at the corner until a towel waves it quiet, and the turkey comes
out. In the final rush the beat runs round the stove pot to pot, the clock runs out, every dish shoots from its pot
to the table, the house holds its breath for one beat, and they all land on the Porch Front at the same instant: a
gold shock runs round the house and every dish's colour parades round the roof."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'TG15'
TITLE = 'Kitchen Rush'
KIND = 'show'
DESCRIPTION = ('The last hour before dinner. Four burners boil over in turn, timers ring, pans clang, the mixer whirs '
               'and the smoke alarm goes off, and then every dish lands on the table at exactly the same moment.')
VOICEOVER = "One hour till dinner, four pots on the stove, and absolutely nothing is ready."

FLAME = hexc('#1838ff')
CREAM = hexc('#ffe8c0')
GRAVY = hexc('#d05808')
CRAN = hexc('#ff0020')
BEAN = hexc('#20d010')
TURKEY = hexc('#ff7a10')
OVEN = hexc('#ff4000')
CLOCK = hexc('#ffb000')
WHITE = hexc('#fff4e8')
SMOKE = hexc('#8090a8')
ALARM = hexc('#ff0000')
GOLD = hexc('#ffb000')

D = 90.0
SEED = 15
TEMPO = [(0, 104), (20, 104), (78, 172), (90, 172)]        # the clock speeds up (bpm)


def beat_times():
    ts = np.arange(0, D + 1, 0.001)
    ph = np.cumsum(np.interp(ts, [p[0] for p in TEMPO], [p[1] for p in TEMPO]) / 60 * 0.001)
    return np.concatenate([[0.0], np.interp(np.arange(1, int(ph[-1])), ph, ts)])


BT = beat_times()


def snap(t, unit=1):
    """Time of the beat (a multiple of `unit` beats) nearest t."""
    k = int(round(np.interp(t, BT, np.arange(len(BT))) / unit)) * unit
    return float(BT[k])


def beat_at(t):
    return int(np.searchsorted(BT, t, side='right') - 1)


K_LAND = int(round(np.interp(82.0, BT, np.arange(len(BT))) / 4)) * 4
T_LAND = float(BT[K_LAND])                # everything lands on the table
T_RUN = float(BT[K_LAND - 8])             # the dishes leave their pots
T_HUSH = float(BT[K_LAND - 1])           # the held breath
T_TURKEY = snap(62.0, 4)
PF0, PF1, MID = 1314.0, 1658.0, 1486.0
# name, run (lo, hi), colour, lit at, boils over at, slot on the table
POTS = [('potatoes', 492.0, 892.0, CREAM, snap(1.5), snap(20.0, 4), 1345.0),
        ('gravy', 896.0, 1309.0, GRAVY, snap(3.0), snap(36.0, 4), 1412.0),
        ('cranberries', 1662.0, 2030.0, CRAN, snap(4.5), snap(28.0, 4), 1560.0),
        ('beans', 2036.0, 2512.0, BEAN, snap(6.0), snap(44.0, 4), 1627.0)]
TIMERS = [(snap(24.0, 2), 245.0, 260.0), (snap(32.0, 2), MID, 200.0), (snap(40.0, 2), 2420.0, 140.0)]
DING = 0.22
MIX0, MIX1 = snap(48.0, 4), snap(54.5, 4)
SMOKE0 = 50.0
ALARM0 = snap(56.0)
ALARM_FLASHES = [ALARM0 + 0.4 * k for k in range(13)]
TOWEL0, TOWEL1 = ALARM0 + 2.6, ALARM0 + 5.4
ALARM_AT = 893.0
TURKEY_AT = 560.0
LID = 1.0                                 # the lid clangs this long after a boil-over


def kitchen(seed=SEED):
    """Bubbles (time, pot, position, size) from each pot's heat; the cranberries pop instead of bubbling."""
    rng = np.random.default_rng(seed)
    ev = []
    for f in range(nframes(T_RUN)):
        t = f * DT
        for k, (_, lo, hi, _, ign, boil, _) in enumerate(POTS):
            if t < ign + 1:
                continue
            h = heat(t, ign, boil)
            rate = 2 + 14 * h ** 2
            for _ in range(rng.poisson(rate * DT)):
                c = (lo + hi) / 2 + (hi - lo) / 2 * rng.uniform(-0.85, 0.85)
                ev.append((t, k, c, rng.uniform(0.6, 1.0)))
    return ev


def heat(t, ign, boil):
    """0..1: how hard a pot is going."""
    h = 0.45 * smoothstep(ign + 1, ign + 8, t) + 0.55 * smoothstep(ign + 8, boil, t) ** 2
    after = smoothstep(boil + 1.5, boil + 3, t)
    h = h * (1 - after) + 0.55 * after
    return h + 0.35 * smoothstep(T_TURKEY, T_RUN, t)


def render(G, seed=SEED):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    rng = np.random.default_rng(seed + 1)
    flick = Flicker(rng, n, 3.0, 9.0)
    slow = Flicker(rng, n, 0.2, 0.7)
    ev = kitchen(seed)
    bt_ = np.array([e[0] for e in ev])
    sizzle = {k: (rng.uniform(-1, 1, 30), rng.uniform(0, 1.4, 30)) for k in range(4)}

    def g(c, w):
        return np.exp(-((pdp - c) / w) ** 2)

    def band(lo, hi, soft=3.0):
        return np.clip((pdp - lo) / soft + 0.5, 0, 1) * np.clip((hi - pdp) / soft + 0.5, 0, 1)

    def dish_pos(k, t):
        """Where pot k's dish is during the final run: from the middle of its run to its slot on the table."""
        _, lo, hi, _, _, _, slot = POTS[k]
        u = np.clip((t - T_RUN) / (T_LAND - T_RUN), 0, 1)
        return lerp((lo + hi) / 2, slot, u ** 2.2)

    for f in range(F):
        t = f * DT
        buf = np.zeros((n, 3))
        k_b = beat_at(t)
        ph = (t - BT[k_b]) / (BT[k_b + 1] - BT[k_b])            # 0..1 through the current beat
        landed = t >= T_LAND
        fade = keys(t, [(0, 0), (0.6, 1), (87, 1), (90, 0)])

        # ---- the oven on Side: heat, timers, smoke ----
        if not landed:
            shimmer = 0.7 + 0.3 * np.cos(2 * np.pi * (pdp / 90 - 0.7 * t))      # heat rolling out of the oven
            buf += light(OVEN, (0.3 + 0.05 * slow(t)) * shimmer * band(0, 490, 8) * fade)

        # ---- the burners ----
        for k, (name, lo, hi, col, ign, boil, slot) in enumerate(POTS):
            if t < ign or landed:
                continue
            u = t - ign
            run = band(lo, hi)
            c, half = (lo + hi) / 2, (hi - lo) / 2
            edge = np.clip(np.abs(pdp - c) / half, 0, 1)
            h = heat(t, ign, boil)
            turned = 0.65 if t > boil + 2 else 1.0
            # the pots throb on the beat once the first one has boiled over, harder and harder; all out in the rush
            rush = np.exp(-ph / 0.18) * (0.35 * smoothstep(POTS[0][5], ALARM0, t) + 0.65 * (t >= T_TURKEY))
            # the flame: a blue ring strongest at the run's ends, with an ignition whoomp
            fl = (0.28 + 0.08 * flick(t)) * turned * (0.4 + 0.6 * edge) + 0.85 * np.exp(-u / 0.18)
            buf += light(FLAME, run * fl)
            buf += light(WHITE, 0.7 * np.exp(-u / 0.12) * np.exp(-((np.abs(pdp - c) - half * smoothstep(0, 0.25, u))
                                                                    / 20) ** 2) * run)
            # the contents
            if t < T_RUN:
                cont = (0.24 + 0.5 * h + 0.25 * rush) * (1 - 0.3 * edge ** 2) * (1 + 0.15 * slow(t))
                # it rolls: stripes rise from the middle of the pot to its rims, a stripe a beat, so they speed up
                # with the clock and stand out more as the pot heats
                roll = 0.5 + 0.5 * np.cos(2 * np.pi * (np.abs(pdp - c) / 70 - (k_b + ph) * (1 + (t >= T_TURKEY))))
                con = min(0.85, 0.3 + 0.6 * h)
                cont = cont * (1 - con + 1.25 * con * roll)
                if T_TURKEY <= t < T_RUN:                  # who needs stirring: the beat runs round the stove pot to pot
                    cont = cont + 0.55 * (k_b % 4 == k) * np.exp(-ph / 0.35)      # pots are in path order
                if name == 'potatoes' and MIX0 <= t < MIX1:        # the mixer: whirling stripes and two beaters
                    m = t - MIX0
                    spd = 3 + 9 * smoothstep(0, 1.5, m)
                    stripes = 0.5 + 0.5 * np.cos(2 * np.pi * (pdp / 34 - spd * m))
                    cont = cont * (0.4 + 0.9 * stripes)
                    for s in (-1, 1):
                        bx = c + s * 45 + 30 * np.sin(2 * np.pi * 6 * m + s)
                        buf += light(WHITE, 0.8 * g(bx, 6))
                buf += light(col, run * cont)
            else:                                                  # gathered into a dish and off to the table
                gather = smoothstep(T_RUN, T_LAND, t)
                buf += light(col, run * (0.6 * (1 - 0.7 * gather)) * (1 - 0.3 * edge ** 2))
            # boil-over: foam surges out past both ends, sizzles, a lid clangs, the flame goes down
            ub = t - boil
            if 0 <= ub < 3.2:
                reach = half * 1.8 * smoothstep(0, 0.6, ub)
                buf += light(col, 0.85 * run * np.exp(-ub / 1.0))
                foam = np.clip((reach - np.abs(pdp - c)) / 15, 0, 1) * (1 - smoothstep(2.0, 3.2, ub))
                buf += light(lerp(col, WHITE, 0.55), 0.95 * foam * (1 + 0.15 * flick(t)))
                xs, ts = sizzle[k]
                for x_, t_ in zip(xs, ts):
                    us = ub - 0.5 - t_
                    if 0 <= us < 0.2:
                        buf += light(WHITE, 0.9 * np.exp(-us / 0.06) * g(c + x_ * reach, 3))
                ul = ub - LID
                if 0 <= ul < 0.5:
                    buf += light(WHITE, 0.95 * np.exp(-ul / 0.1) * g(c, 110))
                if ub < 2.4:                                   # the surge rolls on down the whole roof both ways
                    for sgn in (-1, 1):
                        buf += light(lerp(col, WHITE, 0.25), 0.8 * (1 - ub / 2.4) ** 1.5 * g(c + sgn * (half + 700 * ub), 45))
                if 0 <= ul < 1.6:                              # the clang rings out
                    for sgn in (-1, 1):
                        buf += light(WHITE, 0.55 * (1 - ul / 1.6) * g(c + sgn * 1100 * ul, 30))
        # bubbles (and the cranberries' pops)
        for i in np.nonzero((t - bt_ >= 0) & (t - bt_ < 0.3))[0]:
            te, k, c, sz = ev[i]
            ue = t - te
            if POTS[k][0] == 'cranberries':
                buf += light(CRAN, 1.0 * sz * np.exp(-ue / 0.08) * g(c, 5 + 20 * ue))
            else:
                buf += light(lerp(POTS[k][3], WHITE, 0.6), 0.75 * sz * np.exp(-ue / 0.1) * g(c, 4))

        # ---- the clock on the Porch Front: a bar shrinking to the middle, ticking at its ends ----
        if not landed:
            left = max(0.0, 1 - t / T_LAND)
            half = (PF1 - PF0) / 2 * left
            tick = np.exp(-ph / 0.08)
            urgent = smoothstep(T_RUN - 2, T_RUN, t)
            buf += light(CLOCK, (0.36 + 0.5 * urgent * tick) * band(MID - half, MID + half) * fade)
            buf += light(WHITE, 0.75 * tick * (g(MID - half, 5) + g(MID + half, 5)) * fade)
            swing = MID - (half + 6) * np.cos(np.pi * (k_b + smoothstep(0, 1, ph)))   # the pendulum, end to end each beat
            buf += light(lerp(CLOCK, WHITE, 0.5), (0.8 + 0.2 * urgent) * (g(swing, 9) + 0.3 * g(swing, 30)) * fade)
        # timers: three dings where they ring
        for tt, c, w in TIMERS:
            for j in range(3):
                ud = t - tt - j * DING
                if 0 <= ud < 0.2:
                    buf += light(lerp(GOLD, WHITE, 0.6), 0.95 * np.exp(-ud / 0.07) * g(c, w))
        # smoke out of the oven, the alarm, the towel
        smoke = smoothstep(SMOKE0, ALARM0, t) * (1 - smoothstep(TOWEL1 - 0.5, TOWEL1 + 1.5, t))
        if smoke > 0:
            reach = 490 + 300 * smoothstep(SMOKE0, ALARM0 + 1, t)
            buf += light(SMOKE, 0.38 * smoke * np.clip((reach - pdp) / 80, 0, 1) * (1 + 0.3 * slow(t)))
        for ta in ALARM_FLASHES:
            ua = t - ta
            if 0 <= ua < 0.2:
                buf += light(ALARM, 0.95 * g(ALARM_AT, 130)) + light(WHITE, 0.8 * g(ALARM_AT, 8))
        if TOWEL0 <= t < TOWEL1:
            ut = t - TOWEL0
            tx = 450 + 380 * np.sin(2 * np.pi * 0.9 * ut)
            buf += light(WHITE, 0.55 * g(tx, 40) * smoothstep(0, 0.3, ut))
        # the turkey: pops up on Left out of the oven, sizzling, then runs to the table with the rest
        if T_TURKEY <= t < T_LAND:
            u = t - T_TURKEY
            x = TURKEY_AT if t < T_RUN else lerp(TURKEY_AT, MID, ((t - T_RUN) / (T_LAND - T_RUN)) ** 2.2)
            buf += light(TURKEY, (0.85 + 0.1 * flick(t)) * g(x, 22) + 0.25 * g(x, 70))
            buf += light(WHITE, 0.9 * np.exp(-u / 0.15) * g(TURKEY_AT, 60))
        # one beat of held breath before the landing: everything sinks but the dishes in the air
        if T_HUSH <= t < T_LAND:
            buf *= 0.3
        # the dishes on the way
        if T_RUN <= t < T_LAND:
            for k, p in enumerate(POTS):
                x = dish_pos(k, t)
                buf += light(p[3], 0.9 * g(x, 14) + 0.45 * g(x, 220))
                c0 = (p[1] + p[2]) / 2                             # the dish lights its path to the table
                buf += light(p[3], 0.45 * band(min(c0, x), max(c0, x), 20))
                for j in range(1, 6):                              # speed streak
                    xj = dish_pos(k, t - j * DT)
                    buf += light(p[3], 0.45 * (1 - j / 6) * g(xj, 10))

        if T_RUN <= t < T_LAND:                                    # the whole house winds up to the landing
            buf += light(GOLD, 0.32 * smoothstep(T_RUN, T_LAND, t) * fade)
        # ---- dinner: everything lands at once ----
        if landed:
            u = t - T_LAND
            front = 1300 * u
            dist = np.abs(pdp - MID)
            behind = np.clip((front - dist) / 120, 0, 1)
            buf += light(GOLD, (0.38 * np.exp(-u / 1.2) + 0.2) * behind * fade * (1 + 0.08 * slow(t)))
            buf += light(WHITE, 0.95 * np.exp(-((dist - front) / 60) ** 2) * (u < 2.2))
            buf += light(WHITE, 0.95 * np.exp(-u / 0.2) * band(PF0, PF1))
            for p in POTS:
                buf += light(p[3], 0.75 * fade * g(p[6], 20))
            buf += light(TURKEY, 0.9 * fade * g(MID, 26))
            # the feast: every dish's colour in stripes travelling round the house, pulsing every other beat
            stripe = ((pdp + 320 * u) // 110).astype(int) % 5
            cols = np.array([CREAM, GRAVY, CRAN, BEAN, TURKEY])[stripe]
            pulse = 0.75 + 0.5 * np.exp(-((k_b % 2) + ph) * (BT[k_b + 1] - BT[k_b]) / 0.15)
            feast = 0.42 * smoothstep(1.2, 2.6, u) * fade * pulse * (1 - band(PF0, PF1, 20))
            buf += light(1.0, feast) * cols
            for c in (1380.0, 1593.0):                             # two candles
                buf += light(CLOCK, (0.6 + 0.12 * flick(t)[int(c) % n]) * fade * smoothstep(1.0, 2.5, u) * g(c, 4))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# Frantic strings in D minor on a clock that speeds up from 104 to 172 bpm, every note on the lights' own beats. A
# woodblock is the clock's tick; each burner lights with a gas whoomp and a harp swipe. Spiccato violins, violas and
# cellos saw away in eighths, louder and busier as the pots heat, with bubbles from each pot and pops from the
# cranberries where they are on the house. A boil-over is a brass stab, a hiss of foam and a string run, then the lid
# clangs. Timers ding on glockenspiel and triangle, the mixer whirs up, the smoke alarm beeps with its flashes over a
# timpani roll and a towel whooshes. The turkey gets a horn ta-da, then the rush: the whole band at full tilt over
# a snare roll, E7, A7; one beat of only the clock ticking, and everything lands on a big D major chord, with
# pizzicato, timpani and string chords on every other beat as the dishes parade round the house.

CH = {'Dm': (62, 65, 69), 'Bb': (62, 65, 70), 'Gm': (62, 67, 70), 'A': (61, 64, 69), 'A7': (61, 67, 69),
      'C': (60, 64, 67), 'F': (60, 65, 69), 'E7': (62, 64, 68), 'D': (62, 66, 69)}
ROOT = {'Dm': 38, 'Bb': 34, 'Gm': 43, 'A': 45, 'A7': 45, 'C': 36, 'F': 41, 'E7': 40, 'D': 38}


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    vln = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vsus = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    csus = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cpizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    hstac = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    tri = M.hits('Percussion/Triangle3-Hit*.wav')
    metal = M.hits('Miscellania Raw/Misc 1/metal_hit*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1*.wav')
    bubbles = M.hits('Miscellania Raw/Misc 1/bubbles*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    sroll = M.hits('Percussion/Snare2-rollNS_v5*.wav')
    snare = M.hits('Percussion/Snare2-HitNS_v5*.wav')
    crash = M.hits('Percussion/cymbal-crash1_ff*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[5-7]*.wav')
    susc = M.hits('Percussion/susCymb1-cresc-Short*.wav')

    for name, gain, rev in (('vln', 0.3, 0.2), ('low', 0.34, 0.15), ('brass', 0.3, 0.25), ('wind', 0.24, 0.15),
                            ('harp', 0.26, 0.3), ('mallet', 0.3, 0.25), ('tick', 0.9, 0.05), ('perc', 0.45, 0.15),
                            ('drums', 0.5, 0.18), ('kitchen', 0.4, 0.1), ('fx', 0.22, 0.15)):
        M.bus(name, gain=gain * 0.58, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        return float(0.85 * (2 * (np.interp(d, ds, xs) - x0) / (x1 - x0) - 1))

    nr = np.random.default_rng(11)

    def noise(sec, lp=1, hp=True):
        y = nr.normal(0, 1, int(sec * SR))
        if lp > 1:
            y = np.convolve(y, np.ones(lp) / lp, 'same')
        if hp:
            y = np.diff(np.concatenate([[0], y]))
        return y / (np.abs(y).max() + 1e-9)

    def hiss(sec):
        k = np.arange(int(sec * SR)) / SR
        y = noise(sec, 3) * np.clip(k / 0.05, 0, 1) * np.exp(-k / (sec / 3))
        return np.vstack([y, y]) * 0.6

    def whir(sec):
        k = np.arange(int(sec * SR)) / SR
        f = 90 + 110 * np.clip(k / 1.5, 0, 1) + 10 * np.sin(2 * np.pi * 0.7 * k)
        p = 2 * np.pi * np.cumsum(f) / SR
        y = (np.sin(p) + 0.5 * np.sin(2 * p) + 0.33 * np.sin(3 * p) + 0.25 * np.sin(4 * p)) * (1 + 0.4 * np.sin(p / 4))
        y = y + 0.4 * noise(sec, 6)
        y *= np.clip(k / 0.3, 0, 1) * np.clip((sec - k) / 0.25, 0, 1)
        return np.vstack([y, y]) * 0.25

    def beep(sec=0.18):
        k = np.arange(int(sec * SR)) / SR
        p = 2 * np.pi * 1550 * k
        y = (np.sin(p) + 0.25 * np.sin(3 * p)) * np.clip(k / 0.005, 0, 1) * np.clip((sec - k) / 0.01, 0, 1)
        return np.vstack([y, y]) * 0.18

    def whoomp():
        k = np.arange(int(0.6 * SR)) / SR
        y = np.sin(2 * np.pi * (70 - 30 * k) * k) * np.exp(-k / 0.15) + 0.5 * noise(0.6, 20, False) * np.exp(-k / 0.12)
        return np.vstack([y, y]) * 0.7

    # ---- the clock: a tick on every beat until the landing; pizz tick-tock under the opening ----
    for k in range(K_LAND):
        t = BT[k]
        M.add('tick', wood.play(85 if k % 2 == 0 else 70, pitch=0 if k % 2 == 0 else 3), t, 1.0, pan_at(MID))
    for k in range(0, int(np.interp(POTS[3][4] + 1, BT, np.arange(len(BT))))):
        M.add('low', cpizz.play(n('D3') if k % 2 == 0 else n('A2'), 80), BT[k], 0.8, -0.1)

    # ---- burners light ----
    for name, lo, hi, col, ign, boil, slot in POTS:
        p = pan_at((lo + hi) / 2)
        M.add('kitchen', whoomp(), ign, 1.0, p)
        M.add('fx', whoosh(0.4, 200, 1500, 0.5, seed=int(ign * 10)), ign, 0.8, p)
        for i in range(6):
            M.add('harp', harp.play(n('D3') + [0, 3, 7, 12, 15, 19][i], 75), ign + 0.03 * i, 0.7, p)

    # ---- the strings: by beat, the chord plan for each bar ----
    def chord_at(k):
        t, bar = BT[k], k // 4
        if t < T_TURKEY:
            plan = ['Dm', 'Dm', 'Bb', 'A'] if t < POTS[0][5] else ['Dm', 'Gm', 'Bb', 'A']
            if MIX0 <= t < ALARM0:
                plan = ['Dm', 'Dm', 'Gm', 'A']
            return plan[bar % 4]
        rem = K_LAND - k
        if rem <= 4:
            return 'A7'
        if rem <= 8:
            return 'E7'
        return ['Dm', 'Bb', 'Gm', 'A'][bar % 4]

    k0 = int(np.interp(POTS[3][4], BT, np.arange(len(BT))))
    for k in range(k0, K_LAND):
        t, dt = BT[k], BT[k + 1] - BT[k]
        c = chord_at(k)
        lo, mid, hi = CH[c]
        inten = 0.45 + 0.35 * smoothstep(POTS[3][4], 44, t) + 0.2 * smoothstep(T_TURKEY, T_LAND, t)
        alarm = ALARM0 - 0.2 <= t < T_TURKEY
        if alarm:                                                  # under the alarm: tremolo pedal, timp roll
            continue
        v = int(60 + 50 * inten)
        M.add('vln', vln.play(hi + 12 if k % 2 else mid + 12, v), t, 1.0, 0.3)
        M.add('vln', vln.play(mid + 12 if k % 2 else lo + 12, v - 8), t + dt / 2, 1.0, 0.3)
        if t > 12:
            M.add('vln', vla.play(lo, v - 10), t + dt / 2, 0.9, -0.1)
        M.add('low', vcs.play(ROOT[c] + 12, v), t, 1.0, -0.3)
        M.add('low', vcs.play(ROOT[c] + 12, v - 15), t + dt / 2, 0.8, -0.3)
        if k % 4 == 0:
            M.add('low', cb.play(ROOT[c], v), t, 1.0, -0.1)
        if t > POTS[0][5] and k % 8 in (4, 5, 6, 7):               # a woodwind patter answering, every other bar
            for e in range(2):
                m = [hi, mid, lo, mid][(2 * k + e) % 4] + 12
                M.add('wind', (clar if k % 16 < 8 else oboe).play(m, v - 10), t + e * dt / 2, 0.8, 0.15)
        if k == K_LAND - 1:                                        # the held breath
            continue
        if t >= T_TURKEY:                                          # the rush: brass hits and a drum on every beat
            M.add('drums', snare.play(70 + 20 * (k % 2 == 0)), t, 0.5, 0.0)
            if k % 2 == 0:
                for m in (lo, mid):
                    M.add('brass', hstac.play(m - 12, 95), t, 0.7, -0.1)
                M.add('low', cb.play(ROOT[c], 105), t, 0.6)

    # ---- bubbles and pops, where each pot is ----
    for i, (te, k, c, sz) in enumerate(kitchen()):
        if POTS[k][0] == 'cranberries':
            M.add('kitchen', wood.play(int(60 + 50 * sz), pitch=8 + 4 * sz), te, 0.7, pan_at(c))
        elif i % 2 == 0:
            M.add('kitchen', bubbles.play(int(60 + 40 * sz), pitch=nr.uniform(-2, 5), dur=0.4), te, 0.35, pan_at(c))

    # ---- boil-overs: stab, hiss, run up, lid clang ----
    for name, lo, hi, col, ign, boil, slot in POTS:
        p = pan_at((lo + hi) / 2)
        c = chord_at(beat_at(boil))
        for m in CH[c]:
            M.add('brass', horn.play(m - 12, 115, dur=0.5, release=0.2), boil, 0.9, p)
            M.add('brass', bone.play(m - 24, 110, dur=0.5, release=0.2), boil, 0.7, p)
        M.add('drums', susc.play(100), boil - 0.8, 0.6, p)
        M.add('drums', crash.play(110), boil, 0.7, p)
        M.add('kitchen', hiss(2.6), boil, 1.0, p)
        M.add('drums', timp.play(115), boil, 0.8, p)
        for i in range(8):
            M.add('vln', vln.play(n('D4') + [0, 2, 3, 5, 7, 9, 10, 12][i] + 12, 100), boil + 0.05 + 0.06 * i, 0.9, p)
        M.add('perc', metal.play(120), boil + LID, 1.0, p)
        M.add('perc', anvil.play(110), boil + LID, 0.6, p)

    # ---- timers ----
    for tt, c, w in TIMERS:
        for j in range(3):
            M.add('mallet', glock.play(n('A5'), 110), tt + j * DING, 0.8, pan_at(c))
            M.add('perc', tri.play(100), tt + j * DING, 0.6, pan_at(c))

    # ---- the mixer ----
    pl = pan_at(692)
    M.add('fx', whir(MIX1 - MIX0), MIX0, 1.6, pl)
    for k in range(beat_at(MIX0), beat_at(MIX1), 4):
        M.add('vln', trem.play(n('A4'), 80, dur=BT[k + 4] - BT[k], release=0.1), BT[k], 0.8, 0.2)

    # ---- smoke, the alarm, the towel ----
    M.add('vln', trem.play(n('A3'), 70, dur=T_TURKEY - SMOKE0, release=0.2), SMOKE0, 0.8, 0.0)
    M.add('low', ctrem.play(n('A2'), 80, dur=T_TURKEY - ALARM0, release=0.2), ALARM0, 0.9, -0.2)
    M.add('drums', troll.play(80, dur=T_TURKEY - ALARM0 - 0.2), ALARM0, 0.6)
    for ta in ALARM_FLASHES:
        M.add('fx', beep(), ta, 1.0, pan_at(ALARM_AT))
    for i in range(int((TOWEL1 - TOWEL0) / (1 / 1.8))):
        M.add('fx', whoosh(0.4, 400, 2200, 0.5, seed=30 + i), TOWEL0 + 0.1 + i / 1.8, 1.0, pan_at(450))

    # ---- the turkey: ta-da ----
    pt = pan_at(TURKEY_AT)
    for i, (m, ln) in enumerate((('A4', 0.15), ('A4', 0.15), ('D5', 0.6))):
        M.add('brass', tpt.play(n(m), 110, dur=ln, release=0.1), T_TURKEY + [0, 0.18, 0.36][i], 1.0, pt)
        M.add('brass', horn.play(n(m) - 5 if i < 2 else n('F#4'), 100, dur=ln, release=0.1),
              T_TURKEY + [0, 0.18, 0.36][i], 0.8, pt)
    M.add('drums', timp.play(110), T_TURKEY + 0.36, 0.8, pt)
    M.add('kitchen', hiss(1.5), T_TURKEY, 0.6, pt)

    # ---- the dishes fly: a rising whoosh for each, a snare roll to the landing ----
    for k, p in enumerate(POTS):
        a = (pan_at((p[1] + p[2]) / 2) + 1) * np.pi / 4
        b = (pan_at(p[6]) + 1) * np.pi / 4
        w = whoosh(T_LAND - T_RUN, 300, 2600, 0.5, seed=60 + k)
        ang = np.linspace(a, b, w.shape[1])
        M.add('fx', w * np.sqrt(2) * np.vstack([np.cos(ang), np.sin(ang)]) * 0.8, T_RUN)
    M.add('drums', sroll.play(90, dur=T_HUSH - T_RUN), T_RUN, 0.7)
    M.add('drums', troll.play(100, dur=T_HUSH - T_RUN), T_RUN, 0.6)

    # ---- dinner: the D major chord ----
    hold = D - T_LAND - 1.0
    for m, inst, bus, v, gn in ((n('D2'), tuba, 'brass', 110, 1.0), (n('D3'), bone, 'brass', 110, 0.9),
                                (n('A3'), bone, 'brass', 105, 0.8), (n('F#4'), horn, 'brass', 110, 1.0),
                                (n('A4'), horn, 'brass', 105, 0.9), (n('D5'), tpt, 'brass', 110, 1.0),
                                (n('F#5'), vsus, 'vln', 110, 1.0), (n('A4'), vsus, 'vln', 105, 0.9),
                                (n('D3'), csus, 'low', 110, 1.0), (n('A3'), csus, 'low', 100, 0.8)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), T_LAND, gn)
    M.add('low', cb.play(n('D2'), 127), T_LAND, 1.2)
    M.add('drums', crash.play(127), T_LAND, 0.9)
    M.add('drums', bd.play(127), T_LAND, 1.0)
    M.add('drums', timp.play(127), T_LAND, 1.0)
    M.add('perc', metal.play(110), T_LAND, 0.5, pan_at(MID))
    for i, m in enumerate(('D3', 'F#3', 'A3', 'D4', 'F#4', 'A4', 'D5', 'F#5', 'A5', 'D6')):
        M.add('harp', harp.play(n(m), 90), T_LAND + 0.04 * i, 0.8, -0.7 + 0.15 * i)
    for j, k in enumerate(range(K_LAND + 2, len(BT) - 1, 2)):      # the feast pulses round the house: pizz and timp
        t = BT[k]
        if t > D - 1.5:
            break
        M.add('low', cb.play(n('D2') if j % 2 == 0 else n('A2'), 110 - 3 * j), t, 0.9)
        M.add('low', cpizz.play(n('D3') if j % 2 == 0 else n('A3'), 100 - 3 * j), t, 0.6, -0.2)
        M.add('drums', timp.play(100 - 4 * j, pitch=0 if j % 2 == 0 else -5), t, 0.5)
        for m in (n('F#4'), n('A4'), n('D5')):
            M.add('vln', vln.play(m, 95 - 3 * j), BT[k + 1], 0.5, 0.3)
    for j in range(6):                                             # the dinner bell
        M.add('perc', tri.play(110 - 8 * j), T_LAND + 1.0 + 0.3 * j, 0.7, pan_at(MID))
    M.add('mallet', glock.play(n('D6'), 90), T_LAND + 1.0, 0.6, pan_at(MID))
    M.add('mallet', glock.play(n('A5'), 80), T_LAND + 1.3, 0.6, pan_at(MID))
    M.add('mallet', glock.play(n('F#5'), 80), T_LAND + 1.6, 0.6, pan_at(MID))
