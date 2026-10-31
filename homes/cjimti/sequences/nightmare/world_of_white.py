"""A World of White: the Pumpkin King tumbles into Christmas Town and runs from wonder to wonder as the house
bursts into Christmas colour, verse by verse.

Dark, then a whump: he lands in a snowdrift in the middle of the porch in a burst of white, and snow begins to
fall on every run. The wonder theme plays five times, a little fuller each time, on celesta, glockenspiel,
strings and sleigh bells. First verse, snow: he stands astonished in a soft blue glow, turning this way and that,
sparkles flying off him with the celesta. Second, the bulbs: strings of red, green, gold and blue bulbs switch on
a run at a time, porch first, then out along both wings, and he dashes to each as it lights. Third, a snowball
fight: children in bright hats on the two wings hurl snowballs the whole length of the house past him, white
streaks that burst where they land, while warm windows glow. Fourth, the carollers: a row of candles on Porch
Front, each glowing as the choir sings its note, and on the porch sides couples kiss under the mistletoe in pink
bursts. Fifth, a key higher on the whole band: a toy train chugs round the house from the free end of Right,
red engine, coloured cars and white puffs of smoke, with the king running after it. It ends with the whole house
in Christmas colour and the king in the middle of it, sparkling.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events, so every
bulb, snowball and kiss lands on the music."""
import numpy as np
from pixelhome.audio import slide
from pixelhome.fx import DT, nframes, light, perc, smoothstep, keys, hexc, Flicker
from pixelhome.nightmare import (Chart, Band, Stage, pulse, RED, GREEN, GOLD, BLUE, WHITE, ICE, WARM, PINK, MOON)

CODE = 'NM05'
TITLE = 'A World of White'
KIND = 'show'
DESCRIPTION = ('The king lands in Christmas Town and the house fills with it bit by bit: snow, coloured bulbs run by '
               'run, snowballs flying the length of the roof, carollers, kisses, and a toy train going round.')
VOICEOVER = ('He lands in something cold, and soft, and white. And everything around him is glowing.')

SNOWY = hexc('#7090d0')
PINE = hexc('#00b020')
BERRY = hexc('#ff1020')
CANDLE = hexc('#ffb840')
HATS = [hexc('#ff2010'), hexc('#10d040'), hexc('#2050ff'), hexc('#ffc000')]

VERSES = [('snow', 'arp', 300, 0), ('bulbs', 'arp', 300, 0), ('snowball', 'gallop', 300, 0),
          ('carols', 'hold', 300, 0), ('train', 'gallop', 320, 2)]
RUN_ORDER = ['Porch Front', 'Porch Left', 'Porch Right', 'Left', 'Right', 'Side']


def compose():
    C = Chart()
    C.rest(3.0)                                             # dark, then he lands in the snow
    for tag, style, bpm, tr in VERSES:
        C.mark(tag)
        C.play('wonder', style=style, bpm=bpm, transpose=tr, tag=tag)
    C.mark('finale')
    C.rest(3.6)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
T_LAND = 0.9


def bulb_times():
    """When each run's bulbs switch on: the second verse's downbeats, from the second one."""
    downs = C.downbeats('bulbs')
    return {r: downs[1 + i] for i, r in enumerate(RUN_ORDER)}


def throws():
    """The snowballs: (time thrown, from, to) on each downbeat and half-bar of the third verse."""
    out = []
    downs = C.downbeats('snowball')
    beat = 60 / 300
    for i, t0 in enumerate(downs):
        for j, dt in enumerate((0.0, 3 * beat)):
            out.append((t0 + dt, (i + j) % 2))
    return out


def king_at(S, t):
    """Where the king is: he lands mid-porch and rushes from sight to sight."""
    mid = S.mid
    if t < M['bulbs']:
        return mid, (1 if int(max(t - M['snow'], 0) / (6 * 0.2)) % 2 else -1)
    if t < M['snowball']:
        bt = bulb_times()
        p, last = mid, None
        for r in RUN_ORDER:
            if t >= bt[r] - 0.1:
                last = r
        if last is None:
            return mid, 1
        target = S.at(last, 0.5) if last != 'Side' else S.at('Left', 0.15)
        prev = [r for r in RUN_ORDER if bt[r] < bt[last]]
        src = (S.at(prev[-1], 0.5) if prev[-1] != 'Side' else S.at('Left', 0.15)) if prev else mid
        u = smoothstep(bt[last] - 0.1, bt[last] + 0.5, t)
        return src + (target - src) * u, (1 if target > src else -1)
    if t < M['carols']:
        p = keys(t, [(M['snowball'] - 0.2, S.at('Left', 0.15)), (M['snowball'] + 1.2, mid)])
        return p, 1 if t > M['snowball'] + 1.2 and int(t * 2) % 2 else -1
    if t < M['train']:
        pts = [(M['carols'], mid), (M['carols'] + 3.5, mid), (M['carols'] + 4.3, S.at('Porch Left', 0.5)),
               (M['carols'] + 6.3, S.at('Porch Left', 0.5)), (M['carols'] + 7.3, S.at('Porch Right', 0.5)),
               (M['train'] - 0.4, S.at('Porch Right', 0.5)), (M['train'] + 0.2, S.at('Right', 0.2))]
        p = keys(t, pts)
        return p, 1 if p > S.mid else -1
    if t < M['finale']:
        tp = train_at(S, t)
        return max(tp + 140, min(tp + 260, S.L + 200)), -1
    return keys(t, [(M['finale'], S.at('Left', 0.5)), (M['finale'] + 1.0, S.mid)]), 1


def train_at(S, t):
    """The engine's position: in from the free end of Right, round the whole house and off down the Side."""
    return S.L + 30 - (S.L + 300) * (t - M['train']) / (M['finale'] - M['train'])


def bulbs(S, t, fl):
    """The strings of coloured bulbs in clusters of three, red, green, gold and blue (so the colours still read
    from across the street), twinkling a little."""
    cols = np.array([RED, GREEN, GOLD, BLUE])[(S.G.pi // 4) % 4]
    on = (S.G.pi % 4 != 3) * (0.85 + 0.15 * fl(t))
    return perc(on)[:, None] * cols


def render(G, seed=5):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    fl = Flicker(rng, G.N, 0.3, 1.5)
    bt = bulb_times()
    tunes = C.tunes()
    tune_t = np.array([n[0] for n in tunes])
    beats = np.array([b[0] for b in C.beats])
    downs = np.array(C.downbeats())
    windows = (rng.random(G.N) < 0.12) * rng.uniform(0.6, 1.0, G.N) * (~S.porch)
    kids = [S.at('Left', 0.45), S.at('Right', 0.55)]
    balls = throws()
    carols = [S.at('Porch Front', u) for u in (0.12, 0.31, 0.5, 0.69, 0.88)]
    kiss_at = [S.at('Porch Left', 0.5), S.at('Porch Right', 0.5)]
    kisses = [(C.downbeats('carols')[k], kiss_at[k % 2]) for k in (2, 4, 6)]
    train_cars = [(0, [(2, GOLD, 1.0), (1, RED, 1.0), (0, RED, 1.0), (-1, RED, 0.9), (-2, None, 0)]),
                  (-6, [(1, GREEN, 1.0), (0, GREEN, 1.0), (-1, GREEN, 1.0)]),
                  (-11, [(1, BLUE, 1.0), (0, BLUE, 1.0), (-1, BLUE, 1.0)]),
                  (-16, [(1, GOLD, 1.0), (0, GOLD, 1.0), (-1, GOLD, 1.0)]),
                  (-21, [(1, RED, 1.0), (0, PINE, 1.0), (-1, RED, 1.0)])]
    run_names = list(S.run)

    for f in range(F):
        t = f * DT
        beat = pulse(t, beats, 0.15)
        land = t >= T_LAND
        world = smoothstep(T_LAND, T_LAND + 2.5, t)
        fr = np.zeros((G.N, 3))

        # snow on a soft blue, every run, from the moment he lands
        lit = smoothstep(M['bulbs'], M['snowball'], t)
        fr += light(SNOWY, 0.3 * world * (1 - 0.6 * lit) * np.ones(G.N))
        fr += S.snowfall(t, amount=0.9 * world * (1 - 0.4 * lit), seed=3)
        if land and t < T_LAND + 1.6:                       # the whump: a burst of snow out of the drift
            a = t - T_LAND
            fr += light(WHITE, 1.0 * np.exp(-a / 0.25) * smoothstep(900 * a + 80, 900 * a - 80, np.abs(d - mid)))
        fr += S.burst([(T_LAND, 1.2, mid)], t, seed=8, n=24, colors=(WHITE, ICE))

        # the bulbs, run by run, then the whole house; the beat pulses them in the last verse
        mask = np.zeros(G.N)
        for r in RUN_ORDER:
            a = t - bt[r]
            if a >= 0:
                mask += S.run[r] * (0.8 + 0.6 * np.exp(-a / 0.4))
                if a < 0.6:
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * S.run[r])
        level = keys(t, [(M['bulbs'], 0.75), (M['snowball'] - 0.5, 0.75), (M['snowball'] + 0.5, 0.45),
                         (M['train'] - 0.5, 0.45), (M['train'] + 0.5, 0.6), (M['finale'], 0.6), (M['finale'] + 0.3, 1.0)])
        level = level * (1 + 0.5 * beat * (t >= M['train']))
        fr += bulbs(S, t, fl) * perc(np.clip(mask, 0, 1.3) * level)[:, None]

        # warm windows glow on the wings from the snowball fight on
        win = smoothstep(M['snowball'], M['snowball'] + 2.0, t)
        fr += light(WARM, 0.7 * win * windows)

        # verse one: wonder rippling off him on every celesta note
        if M['snow'] <= t < M['bulbs'] + 1.0:
            for j in np.flatnonzero((tune_t <= t) & (tune_t > t - 1.2) & (tune_t < M['bulbs'])):
                a = t - tune_t[j]
                side = 1 if j % 2 else -1
                fr += light(ICE, 0.7 * np.exp(-a / 0.5) * np.exp(-((d - mid - side * (40 + 500 * a)) / 50) ** 2))
            fr += light(ICE, 0.35 * S.porch * (1 - smoothstep(M['bulbs'], M['bulbs'] + 1.0, t)))

        # verse three: the snowball fight, the length of the house past him
        if M['snowball'] - 0.3 <= t < M['carols'] + 1.5:
            for i, k in enumerate(kids):
                fr = S.sprite(fr, k, [(1, HATS[2 * i], 1.0), (0, WHITE, 0.6), (-3, HATS[2 * i + 1], 1.0),
                                      (-4, WHITE, 0.6)], 1.0 - smoothstep(M['carols'], M['carols'] + 1.5, t))
            for tb, side in balls:
                a = t - tb
                src, dst = kids[side], kids[1 - side]
                if 0 <= a < 0.9:
                    p = src + (dst - src) * smoothstep(0, 0.9, a)
                    fr = fr * (1 - 0.8 * S.blob(p, 30))[:, None]
                    fr += light(WHITE, 1.0 * S.blob(p, 14))
                    fr += light(ICE, 0.7 * np.exp(-np.abs(d - p) / 110) * S.span(min(p, src), max(p, src)))
            fr += S.burst([(tb + 0.9, 1.0, kids[1 - side]) for tb, side in balls], t, seed=9, n=10,
                          colors=(WHITE, ICE), reach=0.4)

        # verse four: carollers on Porch Front (a candle each, glowing on its note); kisses under the mistletoe
        if M['carols'] - 0.5 <= t < M['train'] + 1.0:
            vis = smoothstep(M['carols'] - 0.5, M['carols'] + 0.5, t) * (1 - smoothstep(M['train'], M['train'] + 1, t))
            j = int(np.searchsorted(tune_t, t, side='right')) - 1
            sing = -1
            if j >= 0 and M['carols'] <= tune_t[j] < M['train']:
                sing = (tunes[j][2] - 62) % 5
                s_lvl = np.exp(-(t - tune_t[j]) / 0.4)
            fr += light(CANDLE, 0.35 * vis * S.run['Porch Front'])
            for i, p in enumerate(carols):
                lv = vis * (0.65 + (0.6 * s_lvl if i == sing else 0.0))
                fr = S.sprite(fr, p, [(1, CANDLE, 1.0), (0, WARM, 0.6), (-1, MOON, 0.5)], lv)
                if i == sing:
                    fr += light(CANDLE, 0.6 * s_lvl * vis * S.blob(p, 40))
            for p in kiss_at:
                fr = S.sprite(fr, p, [(1, PINE, 0.9), (0, BERRY, 1.0), (-1, PINE, 0.9)], vis)
            for tk, p in kisses:
                a = t - tk
                if -1.0 <= a < 1.8:
                    gap = 4.5 * max(0, 6 * (1 - smoothstep(-1.0, 0.0, a)))
                    lv = vis * (1 - smoothstep(1.0, 1.8, a))
                    fr = S.sprite(fr, p - 12 - gap, [(0, PINK, 1.0)], lv)
                    fr = S.sprite(fr, p + 12 + gap, [(0, PINK, 1.0)], lv)
                    if a >= 0:
                        fr += light(PINK, 0.9 * np.exp(-a / 0.5) * S.blob(p, 30 + 120 * a))
            fr += S.burst([(tk, 0.9, p) for tk, p in kisses], t, seed=10, n=12, colors=(PINK, BERRY, WHITE),
                          reach=0.5)

        # verse five: the toy train round the house, puffing smoke
        if M['train'] <= t < M['finale'] + 1.0:
            tp = train_at(S, t)
            for off, px in train_cars:
                cp = tp - off * 4.5 * -1
                if -20 < cp < S.L + 20:
                    fr = S.sprite(fr, cp, px, 1.0, -1)
            if -20 < tp < S.L + 20:
                fr += light(GOLD, 0.6 * S.blob(tp - 18, 30))
                fr += light(RED, 0.45 * S.run_at(tp))
                fr += light(WHITE, 0.5 * S.blob(tp + 8, 20))
            for tb in beats[(beats <= t) & (beats > t - 1.5) & (beats >= M['train'])][::1]:
                a = t - tb
                pp = train_at(S, tb)
                if (tb - M['train']) / (60 / 320) % 3 < 0.5:
                    fr += light(WHITE, 0.6 * np.exp(-a / 0.5) * S.blob(pp + 30 * a, 12 + 25 * a))

        # the finale: the whole house in Christmas colour, bursts round the king
        if t >= M['finale']:
            a = t - M['finale']
            fr += light(WHITE, 0.8 * np.exp(-a / 0.3) * np.ones(G.N))
            fr += S.burst([(M['finale'] + k * 0.35, 1.2, mid + (k - 2) * 220) for k in range(5)], t, seed=11,
                          n=20, colors=(RED, GREEN, GOLD, BLUE, WHITE))

        # downbeats flash a white wash out from the king in the fuller verses
        if M['bulbs'] <= t < M['finale']:
            for t0 in downs[(downs <= t) & (downs > t - 1.0) & (downs >= M['bulbs'])]:
                a = t - t0
                kp = king_at(S, t0)[0]
                fr += light(ICE, 0.35 * np.exp(-a / 0.35) * np.exp(-((np.abs(d - kp) - 900 * a) / 60) ** 2))

        # the king
        kp, kf = king_at(S, t)
        if land and -15 < kp < S.L + 15:
            spark = pulse(t, tune_t, 0.2)
            fr = S.jack(fr, float(kp), min(1.0, 3 * (t - T_LAND)), facing=kf, glow=0.4 + 0.3 * spark)
        out[f] = fr * float(smoothstep(D, D - 1.2, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=3.0)
    bt = bulb_times()
    parts = {
        ('snow', 'tune'): [('celesta', 12, 0, 0.7)],
        ('snow', 'arp'): [('harp', 0, -6, 0.45)],
        ('snow', 'pedal'): [('violins', 12, -20, 0.25), ('cellos', 0, -16, 0.35)],
        ('bulbs', 'tune'): [('celesta', 12, 0, 0.6), ('glock', 0, -4, 0.55)],
        ('bulbs', 'arp'): [('harp', 0, -4, 0.45)],
        ('bulbs', 'pedal'): [('violins', 12, -12, 0.35), ('violas', 0, -12, 0.35), ('cellos', 0, -10, 0.4)],
        ('snowball', 'tune'): [('flutes', 0, 0, 0.6), ('glock', 0, -2, 0.5), ('violins', 0, -6, 0.45)],
        ('snowball', 'bass'): [('basses pizz', 0, 0, 0.6), ('tuba', -12, -10, 0.4)],
        ('snowball', 'chord'): [('pizz', 0, 0, 0.5)],
        ('carols', 'tune'): [('choir', 0, 4, 0.75), ('violins', 0, -4, 0.5), ('celesta', 12, -14, 0.3)],
        ('carols', 'hold'): [('horns', 0, -16, 0.35), ('violas', 0, -10, 0.35)],
        ('carols', 'pedal'): [('cellos', 0, -6, 0.5), ('basses', 0, -12, 0.35)],
        ('train', 'tune'): [('trumpets', 0, 4, 0.65), ('glock', 0, 0, 0.5), ('violins', 0, 0, 0.55),
                            ('choir', 0, -4, 0.45)],
        ('train', 'bass'): [('tuba', -12, 2, 0.65), ('basses pizz', 0, 0, 0.5)],
        ('train', 'chord'): [('horns', 0, -8, 0.4), ('pizz', 0, 0, 0.45)],
    }
    B.perform(C.events, parts, pan=lambda t, m, role: 0.5 * S.pan(king_at(S, t)[0]) if role == 'tune' else None)
    B.effects([(0, 0), (M['snow'], -4), (M['snowball'], -2), (M['carols'], -8), (M['train'], -3), (D, -3)])
    # the fall ends: a whump in the snow, then a shimmer as he looks up
    B.whoosh(0.0, T_LAND, up=False, gain=0.7)
    B.boom(T_LAND, pan=0.0, gain=0.5)
    B.hit('bell tree', T_LAND + 0.9, 90, gain=0.5)
    B.hit('cymbal swell', M['snow'] - 1.6, 80, gain=0.35)
    # sleigh bells from the second verse, fuller as it goes
    B.sleigh_bells(M['bulbs'], M['carols'], beat=0.4, v=80, gain=0.5)
    B.sleigh_bells(M['carols'], M['train'], beat=0.6, v=70, gain=0.35)
    B.sleigh_bells(M['train'], M['finale'], beat=60 / 320, v=96, gain=0.6, pan=lambda tt: 0.6 * S.pan(train_at(S, tt)))
    # each run's bulbs switch on with a ping
    for i, r in enumerate(RUN_ORDER):
        p = S.pan(S.at(r, 0.5))
        B.play('glock', 79 + [0, 2, 4, 7, 9, 12][i], bt[r], 0.5, 100, p, 0.5)
        B.hit('triangle', bt[r], 90, gain=0.35, pan=p)
    # the snowballs: a whoosh down the house and a splat
    kids = [S.at('Left', 0.45), S.at('Right', 0.55)]
    for tb, side in throws():
        a, b = S.pan(kids[side]), S.pan(kids[1 - side])
        B.whoosh(tb, 0.9, up=bool(side), pan=0.5 * (a + b), gain=0.35)
        B.hit('slapstick', tb + 0.9, 100, gain=0.45, pan=b)
    # kisses under the mistletoe: a little harp flourish and a smack
    for k in (2, 4, 6):
        tk = C.downbeats('carols')[k]
        p = S.pan(S.at('Porch Left' if k % 4 == 2 else 'Porch Right', 0.5))
        for j, m in enumerate((74, 79, 83, 86)):
            B.play('harp', m, tk - 0.25 + 0.06 * j, 0.6, 80, p, 0.4)
        B.hit('claves', tk, 90, gain=0.3, pan=p)
    # the train: a toot as it comes in and as it goes, and its chuffing
    for tw in (M['train'] + 0.1, M['train'] + 4.4, M['finale'] - 1.0):
        pp = S.pan(min(max(train_at(S, tw), 0.0), S.L))
        B.M.add('fx', slide(0.0, 0.05, 700, 880, 0.35, amp=0.5), tw, 0.3, pp)
        B.M.add('fx', slide(0.0, 0.05, 880, 1050, 0.45, amp=0.5), tw + 0.4, 0.3, pp)
    beat = 60 / 320
    t = M['train']
    while t < M['finale']:
        B.hit('snare', t, 60, gain=0.18, pan=0.6 * S.pan(min(max(train_at(S, t), 0.0), S.L)), fx=True)
        t += 1.5 * beat
    # the finale: a last chord on everything, a crash and the bells
    tf = M['finale']
    for m in (57, 61, 64, 69):
        B.play('choir', m, tf, 3.0, 96, gain=0.5)
        B.play('violins', m + 12, tf, 3.0, 96, gain=0.4)
        B.play('horns', m, tf, 3.0, 100, gain=0.45)
    B.play('tuba', 33, tf, 3.0, 100, gain=0.5)
    B.play('basses', 45, tf, 3.0, 100, gain=0.45)
    B.hit('crash', tf, 118, gain=0.55)
    B.hit('bell tree', tf + 0.1, 110, gain=0.5)
    B.hit('timpani', tf, 116, pitch=-3, gain=0.5)
    B.sleigh_bells(tf, tf + 2.2, beat=0.1, v=100, gain=0.6)
    B.finish()
