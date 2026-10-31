"""Fog on Christmas Eve: the town sees its king off, a fog stops him, and Zero's nose lights the way.

The Halloween town at night, everyone out: the citizens pop up along the wings and the porch a beat at a time, bobbing
in orange, green, violet and bone, to their march played quietly, while the coffin sleigh waits on the right wing
(four skeleton reindeer, the dark coffin, the Pumpkin King at the reins) and he stands on the porch. Then a thick
grey fog rolls in from both ends of the house and swallows everything, crowd, sleigh and all, to Jack's lament
in A minor on low strings and the wind. Out of the grey a small red-orange nose lights on the porch: Zero,
to his own glockenspiel tune, his glow pushing the fog back a little more on every note; he barks. The king's
theme turns to A major as the dog flies along Porch Right to the head of the team, and the reindeer light up gold
one by one. The sleigh bells start, a gold ring bursts off the sleigh and it takes off, accelerating round the
porch and along the left wing and away down Side, the whole band on Jack's triumph; behind it the fog is torn
open into a lane of clear night, gold sparkle and twinkling stars. The dog's tune comes back on the celesta as the
bells fade away down Side, the lane glittering.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() read its marks and events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, PUMPKIN, SLIME, VIOLET, BONE, WHITE, GOLD, RED, DUSK,
                                 NOSE, NIGHT, GREY, MOON)

CODE = 'NM14'
TITLE = 'Fog on Christmas Eve'
KIND = 'show'
DESCRIPTION = ("The town gathers to see Jack's coffin sleigh off, but a fog swallows the house. Watch for Zero's glowing "
    'nose: it leads the team round the porch and away down the side, tearing a clear lane through the fog.')
VOICEOVER = 'On Christmas Eve all of Halloween Town came out to see Jack fly. And then the fog rolled in.'

CROWD = (PUMPKIN, SLIME, VIOLET, BONE)
FOGC = hexc('#9aa4b4')



class Offstage(Stage):
    """The shared Stage, but a sprite whose centre is past either free end is drawn partly or not at all instead of
    being clamped onto the end pixel, so things can walk in and out of the ends."""

    def sprite(self, fr, p, pixels, lvl=1.0, facing=1, cut=True):
        if lvl <= 0:
            return fr
        if p < self.pp[0]:
            k0 = int(np.floor((p - self.pp[0]) / 6.1))
        elif p > self.pp[-1]:
            k0 = self.N - 1 + int(np.ceil((p - self.pp[-1]) / 4.0))
        else:
            k0 = self.k(p)
        offs = [o for o, _, _ in pixels]
        if cut:
            for o in range(min(offs) - 1, max(offs) + 2):
                k = k0 + facing * o
                if 0 <= k < self.N:
                    fr[self.path[k]] *= 1 - min(1.0, lvl * 1.5) * (0.9 if min(offs) <= o <= max(offs) else 0.5)
        for o, col, v in pixels:
            k = k0 + facing * o
            if 0 <= k < self.N and col is not None:
                fr[self.path[k]] += light(col, lvl * v)
        return fr


def compose():
    C = Chart()
    C.rest(1.5)
    C.mark('gather')
    C.play('town', style='march', bars=(0, 4), bpm=120, tag='gather')      # the citizens gather
    C.mark('fog')
    C.play('king', style='hold', bars=(0, 4), bpm=80, tag='fog')           # the fog rolls in: his lament
    C.mark('nose')
    C.play('zero', style='arp', bpm=120, tag='nose')                       # a glowing nose in the grey
    C.mark('lead')
    C.play('king', style='waltz', bars=(0, 4), bpm=96, major=True, tag='lead')    # to the head of the team
    C.mark('launch')
    C.play('king', style='waltz', bars=(8, 16), bpm=120, major=True, tag='launch')  # up and away
    C.mark('away')
    C.play('zero', style='arp', bpm=108, tag='away')                       # the bells fade down Side
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
M = C.marks
D = M['end']
T_OFF = M['launch'] + 1.2                   # the sleigh leaves the ground
T_GONE = M['launch'] + 7.5                  # and is gone down Side


def team(S, fr, p, lvl, t, gold=1.0, lit=4):
    """The coffin sleigh behind the nose at p, facing toward Side: four skeleton reindeer (lit of them glowing), the
    coffin with red trim, Jack at the reins."""
    x = p + 9 * 4.5
    for i in range(4):
        leap = 0.75 + 0.25 * np.sin(2 * np.pi * (2.5 * t + i / 4))
        on = 1.0 if i < lit else 0.35
        fr = S.sprite(fr, x + i * 18, [(1, BONE, 0.9 * leap * on), (0, BONE, 0.6 * leap * on),
                                       (-1, BONE, 0.4 * on)], lvl, -1)
        if gold and i < lit:
            fr += light(GOLD, 0.35 * gold * lvl * S.blob(x + i * 18, 14))
    x += 18 * 4 + 9
    fr = S.sprite(fr, x, [(2, RED, 0.7), (1, DUSK, 0.6), (0, DUSK, 0.6), (-1, DUSK, 0.6), (-2, RED, 0.7)], lvl, -1)
    fr = S.sprite(fr, x + 27, [(1, BONE, 1.0), (0, None, 0), (-1, BONE, 1.0), (-2, None, 0), (-3, BONE, 0.5),
                               (-4, BONE, 0.4)], lvl, -1)
    return fr


def nose_path(t, p0):
    """Where the nose is after take-off: accelerating from p0 down the path and off the end of Side."""
    u = np.clip((t - T_OFF) / (T_GONE - T_OFF), 0, 1)
    return p0 - (p0 + 260) * (0.35 * u + 0.65 * u * u)


class Fog:
    """Thick fog drifting both ways along the roof in two layers, so it visibly rolls. (The shared Stage.fog draws its
    noise through fx.smooth_noise, which re-bases the lattice on its coordinates' minimum, so it never moves.)"""

    def __init__(self, d, seed=5):
        rng = np.random.default_rng(seed)
        self.d = d
        self.a = rng.uniform(0, 1, 401)
        self.b = rng.uniform(0, 1, 401)
        self.a[-1], self.b[-1] = self.a[0], self.b[0]

    def __call__(self, t):
        k = np.arange(401)
        m1 = np.interp(((self.d + 45 * t) / 140) % 400, k, self.a)
        m2 = np.interp(((self.d - 70 * t) / 60) % 400, k, self.b)
        m = smoothstep(0.1, 0.9, 0.6 * m1 + 0.4 * m2)
        return m


def render(G, seed=14):
    S = Offstage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    p_sleigh = S.at('Right', 0.18)
    p_king = mid - 40
    beats = np.array([b[0] for b in C.beats])
    gather = C.downbeats('gather')
    gb = [b[0] for b in C.beats if b[2] == 'gather']
    # the crowd: a citizen every so often along the front, each arriving on a beat of the march
    spots = [p for p in np.arange(S.at('Left', 0.06), S.at('Right', 0.95), 62)
             if not (p_sleigh - 30 < p < p_sleigh + 175) and abs(p - p_king) > 70]
    arrive = [gb[min(int(rng.integers(0, len(gb))), len(gb) - 1)] for _ in spots]
    ccol = [CROWD[i % 4] for i in range(len(spots))]
    nose_t = np.array([n[0] for n in C.tunes('nose')])
    lead_t = np.array([n[0] for n in C.tunes('lead')])
    launch_t = np.array([n[0] for n in C.tunes('launch')])
    stars = (rng.random(G.N) < 0.25) * rng.uniform(0.4, 1.0, G.N)
    sph = rng.uniform(0, 2 * np.pi, G.N)
    t_pass = np.full(G.N, np.inf)
    fogn = Fog(d)
    away_t = np.array([n[0] for n in C.tunes('away')])                 # when the sleigh's nose passed each pixel

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.5, t)
        beat = pulse(t, beats, 0.15)
        fr = S.town(t, lv=up * (0.9 + 0.1 * beat), mist=0.5)

        # ---- the citizens gather, bobbing; Jack on the porch
        crowd = smoothstep(M['away'], M['away'] - 3, t)
        for p, ta, col in zip(spots, arrive, ccol):
            if t < ta:
                continue
            a = t - ta
            bob = 0.75 + 0.25 * np.sin(2 * np.pi * 1.5 * t + p / 40)
            lvl = crowd * (smoothstep(0, 0.1, a) * bob + 0.7 * np.exp(-a / 0.25))
            fr = S.sprite(fr, p, [(1, col, 1.0), (0, col, 0.7), (-1, col, 0.35)], lvl, 1, cut=False)
        if M['gather'] <= t < M['fog'] + 4:
            for t0 in gather:
                a = t - t0
                if 0 <= a < 1.2:
                    fr += light(GOLD, 0.4 * np.exp(-a / 0.35) * np.exp(-((np.abs(d - mid) - 1100 * a) / 80) ** 2))
        jl = smoothstep(M['gather'], M['gather'] + 1.0, t) * (1 - smoothstep(M['lead'] + 1, M['lead'] + 3, t))
        if jl > 0:
            fr += light(MOON, 0.3 * jl * S.porch)
            fr = S.jack(fr, p_king, jl, facing=1, glow=0.4)

        # ---- the sleigh: waiting on the right wing, then away round the house
        if t < T_OFF:
            p = p_sleigh
            lit = 0 if t < M['lead'] else int(np.clip((t - M['lead'] - 2.5) / 0.9 + 1, 0, 4))
        else:
            p = nose_path(t, p_sleigh)
            lit = 4
        passed = (d >= p) & (d <= p_sleigh) & np.isinf(t_pass) & (t >= T_OFF)
        t_pass[passed] = t
        rise = smoothstep(T_OFF - 0.6, T_OFF, t)
        fr = team(S, fr, p, 1.0, t, gold=0.4 + 0.6 * rise, lit=lit)

        # ---- the fog rolls in from both ends and swallows the house
        roll = smoothstep(M['fog'], M['fog'] + 5.0, t)
        cover = np.maximum(smoothstep(roll * (L / 2 + 150) + 60, roll * (L / 2 + 150) - 60, d),
                       smoothstep(L - roll * (L / 2 + 150) - 60, L - roll * (L / 2 + 150) + 60, d))
        # the nose's glow pushes the fog back; the sleigh's lane tears it open
        if M['nose'] <= t < M['lead']:
            np_ = mid + 60
            grow = smoothstep(M['nose'], M['nose'] + 0.6, t)
            hole = 70 + 45 * sum(1 for x in nose_t if x <= t)
        elif M['lead'] <= t < T_OFF:
            np_ = keys(t, [(M['lead'], mid + 60), (M['lead'] + 3.0, p_sleigh)])
            grow, hole = 1.0, 260
        else:
            np_ = p if t >= T_OFF else mid + 60
            grow = 1.0 if t >= T_OFF else 0.0
            hole = 260
        clear = grow * smoothstep(hole + 60, hole - 60, np.abs(d - np_)) * 0.7
        since = t - t_pass
        lane = np.where(np.isfinite(since), smoothstep(0, 0.5, since), 0.0)
        thick = cover * (1 - clear) * (1 - lane)
        fm = fogn(t)
        fr = fr * (1 - (0.75 + 0.2 * fm) * thick)[:, None] + light(FOGC, (0.22 + 0.5 * fm) * thick)

        # ---- Zero: his nose lights the grey, every note brighter; he flies to the head of the team
        if M['nose'] <= t < T_OFF:
            nb = 1.0 + 0.6 * pulse(t, nose_t, 0.25)
            fr += light(NOSE, 0.5 * grow * nb * S.blob(np_, 60 + 10 * nb))
            fr = S.zero(fr, np_, grow, facing=-1 if t >= M['lead'] else 1, t=t, nose=min(1.0, nb))
        if t >= T_OFF and p > -40:
            fr += light(NOSE, 0.6 * S.blob(p, 50))
            fr = S.zero(fr, p, 1.0, facing=-1, t=t)

        # ---- his triumph: each note of Jack's theme throws gold out from the team
        for times, src in ((lead_t, np_ if t < T_OFF else p), (launch_t, p if p > 60 else mid)):
            for j in np.flatnonzero((times <= t) & (times > t - 0.9)):
                b = t - times[j]
                fr += light(GOLD, 0.55 * np.exp(-b / 0.3) * np.exp(-((np.abs(d - src) - 60 - 700 * b) / 60) ** 2) *
                            (1 - 0.6 * thick))
        # take-off: a gold ring bursts off the sleigh
        a = t - T_OFF
        if 0 <= a < 1.5:
            fr += light(WHITE, 0.8 * np.exp(-a / 0.15) * S.blob(p_sleigh + 80, 150))
            fr += light(GOLD, 1.0 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_sleigh - 80) - 1300 * a) / 90) ** 2))
            fr += light(GOLD, 0.5 * np.exp(-a / 0.4) * np.ones(G.N))
        # the lane: clear night, twinkling stars, gold sparkle fading behind the sleigh
        if np.any(lane > 0):
            tw = 0.5 + 0.5 * np.sin(3.0 * t + sph)
            fr += light(NIGHT, 0.35 * lane)
            fr += light(WHITE, 0.7 * lane * stars * tw)
            spark = np.where(np.isfinite(since), np.exp(-np.clip(since, 0, None) / 1.2), 0.0)
            fr += light(GOLD, 0.9 * spark * lane * (0.6 + 0.4 * np.sin(23 * t + 3 * sph)))
        # the dog's tune again as the bells fade: each note sends a gold sparkle down the lane after the sleigh
        for j in np.flatnonzero((away_t <= t) & (away_t > t - 1.6)):
            b = t - away_t[j]
            front = mid - 1000 * b
            fr += light(GOLD if j % 2 else WHITE, 0.9 * np.exp(-b / 0.6) * np.exp(-((d - front) / 35) ** 2))
            fr += light(NOSE, 0.3 * np.exp(-b / 0.25) * S.blob(mid, 60))
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Offstage(G)
    B = Band(M_, level=2.4)
    p_sleigh = S.at('Right', 0.18)
    parts = {
        ('gather', 'tune'): [('bassoons', 0, 4, 0.7), ('clarinets', 0, -6, 0.4), ('choir', 0, -10, 0.4)],
        ('gather', 'bass'): [('basses pizz', 0, 0, 0.6), ('cellos pizz', 12, -8, 0.4)],
        ('gather', 'chord'): [('pizz', 0, -10, 0.35)],
        ('gather', 'snare'): [('snare', 0, -24, 0.25)],
        ('fog', 'tune'): [('cellos', 0, 6, 0.75), ('clarinets', -12, -6, 0.35)],
        ('fog', 'hold'): [('ghost', 0, -10, 0.45), ('violas', 0, -16, 0.3)],
        ('fog', 'pedal'): [('basses', 0, -6, 0.5)],
        ('nose', 'tune'): [('glock', 0, 0, 0.6), ('celesta', 0, -6, 0.4)],
        ('nose', 'arp'): [('harp', 0, -8, 0.4)],
        ('nose', 'pedal'): [('cellos', 0, -14, 0.35)],
        ('lead', 'tune'): [('horns', 0, 8, 0.85), ('violins', 12, -6, 0.45), ('choir', 0, -4, 0.5)],
        ('lead', 'bass'): [('tuba', -12, -2, 0.6), ('basses', 0, -8, 0.45)],
        ('lead', 'chord'): [('violas', 0, -10, 0.4), ('harp', 12, -10, 0.35)],
        ('launch', 'tune'): [('horns', 0, 10, 0.9), ('trumpets', 0, 2, 0.6), ('violins', 12, 0, 0.6),
                             ('choir', 0, 4, 0.8), ('glock', 12, -6, 0.3)],
        ('launch', 'bass'): [('tuba', -12, 6, 0.8), ('basses', 0, 0, 0.55), ('timpani', 0, 6, 0.4)],
        ('launch', 'chord'): [('trombones', 0, -8, 0.45), ('violas', 0, -8, 0.4)],
        ('away', 'tune'): [('celesta', 0, -2, 0.55), ('glock', 0, -10, 0.35)],
        ('away', 'arp'): [('harp', 0, -10, 0.35)],
        ('away', 'pedal'): [('cellos', 0, -14, 0.3), ('choir', 12, -14, 0.3)],
    }
    B.perform(C.events, parts)
    B.effects([(0, -4), (M['fog'], -4), (M['nose'], -6), (M['lead'], -4), (T_OFF - 0.5, 0), (M['launch'] + 6, -5)])
    # the crowd murmurs: little pops along the front as citizens arrive
    for i, t0 in enumerate(C.downbeats('gather')):
        B.hit('wood', t0 + 0.25, 90, gain=0.4, pan=0.6 * np.sin(i * 2.1))
    # the fog: wind from both ends, a gong scrape
    B.wind(M['fog'] - 0.5, M['lead'] + 1.0, level=lambda tt: np.clip(0.3 + 0.15 * (tt - M['fog']), 0.3, 0.9), pan=0.0)
    B.hit('gong scrape', M['fog'] + 0.3, 100, gain=0.4)
    # the nose: a bell tree as it lights, a bark at the end of his tune
    B.hit('bell tree', M['nose'], 100, gain=0.5, pan=S.pan(S.mid + 60))
    B.woof(M['nose'] + 3.6, pan=S.pan(S.mid + 60))
    B.woof(M['lead'] + 2.9, pan=S.pan(p_sleigh), big=0.8)
    # to the head of the team: a whoosh along Porch Right; each reindeer lights with a triangle
    B.whoosh(M['lead'] + 0.3, 2.5, True, pan=0.5, gain=0.6)
    for i in range(4):
        B.hit('triangle', M['lead'] + 2.5 + 0.9 * i, 100, gain=0.35, pan=S.pan(p_sleigh + 40 + 18 * i))
    # take-off: sleigh bells from the right wing round the house and away down Side
    pan = lambda tt: S.pan(float(nose_path(tt, p_sleigh)) + 80)
    B.sleigh_bells(M['lead'] + 2.5, T_OFF, beat=60 / 96 / 2, pan=S.pan(p_sleigh + 60), v=70, gain=0.6)
    B.sleigh_bells(T_OFF, M['away'] + 4.0, beat=60 / 120 / 2, pan=pan, v=96, gain=1.0)
    B.hit('cymbal swell', T_OFF - 1.4, 100, gain=0.5)
    B.hit('crash', T_OFF, 120, gain=0.55)
    B.hit('bass drum', T_OFF, 120, gain=0.6)
    B.whoosh(T_OFF, 1.6, True, pan=S.pan(S.mid), gain=1.0)
    B.whoosh(T_GONE - 1.5, 1.8, False, pan=-0.8, gain=0.9)
    B.hit('crash', M['away'], 110, gain=0.4, pan=-0.6)
    B.finish()
