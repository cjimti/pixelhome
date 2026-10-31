"""Shot Down: the coffin sleigh is chased across the sky by searchlights and flak, hit, and falls in flames.

The coffin sleigh comes in from the free end of Right on a jaunty major waltz of Jack's theme, sleigh bells
jingling, a gold glow round it and a present popping off the roof on every downbeat as it delivers along the
wings. Then the siren starts: three icy searchlights stab up and rake the roof, closing on the sleigh, and the
king's theme turns minor and driving. Flak bursts (gold and white flashes throwing sparks) chase the sleigh as it
dodges back and forth across the house, each one closer. A burst hits it (a red flicker, smoke starts trailing),
then another, then a direct hit: the whole house flashes white and orange, the sleigh becomes a fireball, and it
falls with a long trail of fire and smoke to the porch, the cemetery, where it crashes in a blast of flame.
The embers die into a hush. Down in Halloween Town the news arrives: the town comes up grey and violet, its
windows dim, and slow tolls ripple out from the porch while Jack's theme mourns on cellos and a choir.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() both read its events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, VIOLET, DUSK, WHITE, GOLD,
                                 ICE, GREY, RED, GREEN, BLUE, NIGHT, SLIME)

CODE = 'NM16'
TITLE = 'Shot Down'
KIND = 'show'
DESCRIPTION = ("Jack's coffin sleigh delivers along the wings until searchlights rake the roof and flak bursts chase it "
    'back and forth. It is hit, bursts into flame and falls onto the porch, and Halloween Town goes grey with '
    'mourning.')
VOICEOVER = "Over the sleeping world Jack's sleigh flew on, until the searchlights found it."

SMOKE = hexc('#606878')


def compose():
    C = Chart()
    C.rest(0.5)
    C.mark('fly')
    C.play('king', style='waltz', bars=(4, 8), bpm=112, major=True, tag='fly')     # a breath: still delivering
    C.mark('alarm')
    C.play('king', style='drive', bars=(0, 16), bpm=160, tag='chase')               # searchlights and flak
    C.mark('struck')
    C.rest(0.8)                                                                     # a direct hit, the fireball
    C.mark('fall')
    C.rest(3.2)                                                                     # down in flames
    C.mark('crash')
    C.rest(2.6)                                                                     # embers, a hush
    C.mark('news')
    C.play('king', style='hold', bars=(10, 16), bpm=62, tag='mourn')                # the town mourns
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def plan(S):
    """The sleigh's nose along the path, frame by frame, and the flak: [(t, strength, where)], and the hits."""
    F = nframes(D)
    ts = np.arange(F) * DT
    t_fly, t_al, t_st, t_fall, t_cr = M['fly'], M['alarm'], M['struck'], M['fall'], M['crash']
    ch = t_st - t_al
    pts = [(t_al + ch * u, S.at(r, v)) for u, r, v in
           [(0.0, 'Porch Left', 0.3), (0.14, 'Porch Right', 0.4), (0.26, 'Right', 0.85), (0.4, 'Porch Left', 0.3),
            (0.52, 'Right', 0.5), (0.64, 'Left', 0.6), (0.76, 'Porch Front', 0.9), (0.88, 'Right', 0.7),
            (1.0, 'Right', 0.35)]]
    p_hit = pts[-1][1]
    pos = np.empty(F)
    for f, t in enumerate(ts):
        if t < t_al:
            pos[f] = np.interp(t, [t_fly - 0.5, t_al], [S.L + 30, S.at('Porch Left', 0.3)])
        elif t < t_st:
            pos[f] = keys(t, pts)
        elif t < t_fall:
            pos[f] = p_hit + 40 * smoothstep(t_st, t_fall, t)
        else:                                       # falling: slow, then faster, to the cemetery on the porch
            u = np.clip((t - t_fall) / (t_cr - t_fall), 0, 1)
            pos[f] = p_hit + 40 + (S.mid - p_hit - 40) * u ** 1.6
    vel = np.gradient(pos)
    facing = np.where(vel >= 0, 1, -1)
    beats = [b[0] for b in C.beats if b[2] == 'chase']
    rng = np.random.default_rng(16)
    flak = []
    for i, tb in enumerate(beats):
        if tb < t_al + 1.6 or tb > t_st - 0.2 or i % 2:
            continue
        u = (tb - t_al) / ch
        f = int(tb / DT)
        miss = (320 * (1 - u) + 50) * rng.choice([-1, 1]) * rng.uniform(0.6, 1.0)
        flak.append((tb, 0.9, float(pos[f] + miss)))
    hits = [t_al + 0.55 * ch, t_al + 0.8 * ch]
    for th in hits:
        flak.append((th, 1.1, float(pos[int(th / DT)])))
    return pos, facing, sorted(flak), hits


def render(G, seed=16):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    pos, facing, flak, hits = plan(S)
    rng = np.random.default_rng(seed)
    t_fly, t_al, t_st, t_fall, t_cr, t_news = M['fly'], M['alarm'], M['struck'], M['fall'], M['crash'], M['news']
    downs_fly = C.downbeats('fly')
    beats = np.array([b[0] for b in C.beats])
    tolls = C.downbeats('mourn')
    windows = (rng.random(G.N) < 0.08) * rng.uniform(0.5, 1.0, G.N)
    beam_w = [(0.9, 0.0, 520), (1.3, 2.1, 420), (0.7, 4.0, 620)]
    presents = [(tb, float(pos[int(tb / DT)] + 230)) for tb in downs_fly[1:]]
    pcols = [RED, GREEN, GOLD, BLUE]
    flak_t = np.array([x[0] for x in flak])

    for f in range(F):
        t = f * DT
        p, fc = pos[f], int(facing[f])
        fr = np.zeros((G.N, 3))
        if t < t_news:
            # the sleeping world below: a deep blue night and warm windows, colder once the alarm sounds
            alarm = smoothstep(t_al, t_al + 2, t)
            up = smoothstep(0, 1.5, t) * (1 - 0.7 * smoothstep(t_cr, t_news, t))
            fr += light(NIGHT, (0.3 - 0.06 * alarm) * up * np.ones(G.N))
            fr += light(ORANGE if alarm < 0.5 else RED, (0.45 - 0.15 * alarm) * up * windows)
        if t < t_st:
            # gold sleigh magic round it (and below, a present popping off the roof on each downbeat)
            fr += light(GOLD, (0.5 if t < t_al else 0.3) * S.blob(p - fc * 80, 150))
            # searchlights: three icy beams raking the roof, closing on the sleigh
            if t >= t_al:
                on = smoothstep(t_al, t_al + 0.6, t)
                close = 1 - 0.75 * smoothstep(t_al, t_st, t)
                for w, ph, amp in beam_w:
                    b = p + amp * close * np.sin(w * 2.2 * (t - t_al) + ph)
                    fr += light(ICE, on * (0.75 * S.blob(b, 38) + 0.15 * S.blob(b, 140)))
            # smoke trails behind once hit
            nh = sum(t >= th for th in hits)
            if nh:
                behind = -fc * (d - p)
                fr += light(SMOKE, 0.35 * nh * (behind > 0) * np.exp(-np.clip(behind, 0, None) / (120 * nh)) *
                            (0.7 + 0.3 * np.sin(d / 9 + 13 * t)))
            flick = 1.0
            for th in hits:
                if 0 <= t - th < 0.8:
                    flick = 0.4 + 0.6 * (int((t - th) * 16) % 2)
                    fr += light(RED, 0.7 * np.exp(-(t - th) / 0.3) * S.blob(p, 160))
            fr = S.sleigh(fr, p, flick, fc, t)
            for k, (tp, pp) in enumerate(presents):
                a = t - tp
                if 0 <= a < 1.2:
                    fr += light(pcols[k % 4], 1.0 * np.exp(-a / 0.6) * S.blob(pp, 50 + 120 * a))
                    fr += light(WHITE, 0.8 * np.exp(-a / 0.08) * S.blob(pp, 30))
        # flak: gold and white flashes throwing sparks, a puff of smoke after
        for th, s, where in [x for x in flak if 0 <= t - x[0] < 1.6]:
            a = t - th
            fr += light(WHITE, s * 1.0 * np.exp(-a / 0.08) * S.blob(where, 65))
            fr += light(GOLD, s * 0.8 * np.exp(-a / 0.22) * S.blob(where, 130))
            fr += light(SMOKE, 0.3 * smoothstep(0.1, 0.4, a) * np.exp(-a / 0.8) * S.blob(where, 70 + 40 * a))
        fr += S.burst([x for x in flak if 0 <= t - x[0] < 1.6], t, seed=3, n=10, reach=0.35,
                      colors=(WHITE, GOLD, FLAME))
        # the direct hit: the whole house flashes white then orange, the sleigh is a fireball
        if t_st <= t < t_cr:
            a = t - t_st
            fr += light(WHITE, 0.9 * np.exp(-a / 0.08) * np.ones(G.N))
            fr += light(ORANGE, 0.6 * np.exp(-a / 0.35) * np.ones(G.N))
            flick = 0.75 + 0.25 * np.sin(31 * t + d / 7) * np.sin(7 * t - d / 11)
            fr += light(FLAME, 1.0 * S.blob(p, 45) * flick)
            fr += light(GOLD, 0.9 * S.blob(p, 18))
            # the fall: a trail of fire and smoke back to where it was hit
            p0 = pos[int(t_st / DT)]
            lo, hi = min(p, p0), max(p, p0)
            trail = S.span(lo, hi) * np.exp(-np.abs(d - p) / 260)
            fr += light(FLAME, 0.8 * trail * flick)
            fr += light(SMOKE, 0.5 * S.span(lo, hi) * (1 - np.exp(-np.abs(d - p) / 260)) *
                        (0.6 + 0.4 * np.sin(d / 13 - 5 * t)))
        # the crash on the porch: a blast of flame across the cemetery, dying to embers
        if t_cr <= t < t_news + 3:
            a = t - t_cr
            fr += light(WHITE, 1.0 * np.exp(-a / 0.1) * S.blob(mid, 260))
            reach = 60 + 750 * (1 - np.exp(-a / 0.4))
            flick = 0.7 + 0.3 * np.sin(23 * t + d / 8) * np.sin(6 * t - d / 15)
            fr += light(FLAME, np.exp(-a / 1.5) * smoothstep(reach + 40, reach - 40, np.abs(d - mid)) * flick)
            ember = (0.5 + 0.5 * np.sin(d / 5 + 3 * t)) * np.exp(-a / 2.5)
            fr += light(ORANGE, 0.4 * ember * S.blob(mid, 160))
            # the wings stay lit: a low red glow of the fire
            fr += light(RED, 0.3 * np.exp(-a / 3.0) * (S.wings | S.run['Side']))
        # Halloween Town hears the news: grey violet, windows dim, slow tolls out from the porch
        if t >= t_news - 1.5:
            up = smoothstep(t_news - 1.5, t_news + 1.5, t)
            fr += S.town(t, lv=0.8 * up, mist=0.15, windows=0.45 - 0.25 * smoothstep(t_news, D, t)) * \
                np.array([0.75, 0.7, 1.0])
            fr += light(GREY, 0.12 * up * np.ones(G.N))
            for tb in tolls:
                a = t - tb
                if 0 <= a < 3.5:
                    ring = np.exp(-((np.abs(d - mid) - 380 * a) / 90) ** 2)
                    fr += light(VIOLET, 0.85 * np.exp(-a / 1.6) * ring)
                    fr += light(GREY, 0.35 * np.exp(-a / 0.6) * S.blob(mid, 120))
            # a jack-o'-lantern at the porch, guttering out
            lan = 0.7 * (1 - smoothstep(t_news + 4, D - 1.5, t)) * up
            fr = S.sprite(fr, mid, [(2, PUMPKIN, 1.0), (1, None, 0), (0, ORANGE, 0.9), (-1, None, 0),
                                    (-2, PUMPKIN, 1.0)], lan * (0.85 + 0.15 * np.sin(9 * t)))
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.1)
    pos, facing, flak, hits = plan(S)
    sp = lambda tt: S.pan(pos[min(int(tt / DT), len(pos) - 1)])
    parts = {
        ('fly', 'tune'): [('horns', 0, 4, 0.7), ('violins', 12, -4, 0.5), ('glock', 12, -12, 0.25)],
        ('fly', 'bass'): [('tuba', -12, 0, 0.6), ('basses pizz', 0, -6, 0.5)],
        ('fly', 'chord'): [('pizz', 0, -4, 0.45)],
        ('chase', 'tune'): [('trumpets', 0, 6, 0.7), ('horns', 0, 4, 0.7), ('violins', 12, 0, 0.5)],
        ('chase', 'bass'): [('cellos', 0, 0, 0.5), ('basses', -12, -4, 0.45)],
        ('chase', 'chord'): [('trombones', 0, -12, 0.35), ('violas', 0, -10, 0.35)],
        ('chase', 'snare'): [('snare', 0, -4, 0.5)],
        ('mourn', 'tune'): [('cellos', 0, 2, 0.8), ('choir', 12, -12, 0.45)],
        ('mourn', 'hold'): [('choir', 0, -20, 0.35), ('violas', 0, -16, 0.35)],
        ('mourn', 'pedal'): [('basses', -12, -10, 0.5)],
    }
    B.perform(C.events, parts)
    t_al, t_st, t_fall, t_cr, t_news = M['alarm'], M['struck'], M['fall'], M['crash'], M['news']
    # timpani drive the chase on the beat, harder as the flak closes in
    for t, k, g in C.beats:
        if g == 'chase':
            B.hit('timpani', t, int(90 + 30 * (t - t_al) / (t_st - t_al)), pitch=-5 if k == 0 else -3,
                  gain=0.35 + 0.15 * (k == 0))
    B.hit('crash', t_al, 118, gain=0.5)
    # the fall: strings slide down chromatically, and the hush after
    for i in range(12):
        tt = t_fall + i * 0.26
        B.play('violins', 76 - i, tt, 0.3, 100 - 3 * i, gain=0.45)
        B.play('cellos', 52 - i, tt, 0.3, 100 - 3 * i, gain=0.4)
    B.play('cellos trem', 40, t_cr + 0.3, t_news - t_cr, 60, gain=0.3)
    for tb in C.downbeats('mourn'):
        B.hit('gong', tb, 70, pitch=-5, gain=0.22)
    # stage effects
    B.effects([(0, -5), (t_al - 0.5, -2), (t_al + 2, -1), (t_st - 0.3, -1), (t_st, 3), (t_cr + 2.5, 0), (t_news, -9)])
    B.sleigh_bells(M['fly'] - 0.5, t_st, beat=0.27, pan=sp, v=80, gain=0.8)
    B.siren(t_al - 0.3, t_st + 1.2, pan=0.0, gain=1.0)
    for th, s, where in flak:
        B.flak(th, pan=S.pan(where), gain=0.8 * s)
    for th in hits:
        B.clash(th, pan=sp(th), v=110, gain=0.7)
        B.boom(th, pan=sp(th), gain=0.5)
    B.shatter(t_st, pan=sp(t_st))
    B.boom(t_st, pan=sp(t_st), gain=1.0)
    B.hit('crash', t_st, 124, gain=0.6)
    B.fire(t_st, t_cr + 0.6, level=0.9, pan=sp)
    B.whoosh(t_fall - 0.2, seconds=t_cr - t_fall + 0.3, up=False, pan=0.0, gain=0.8)
    B.boom(t_cr, pan=0.0, gain=1.2)
    B.hit('bass drum', t_cr + 0.12, 120, gain=0.6)
    B.fire(t_cr, t_news + 1.5, level=lambda tt: np.clip(1.0 - 0.3 * (tt - t_cr), 0.1, 1.0), pan=0.0, seed=8)
    B.finish()
