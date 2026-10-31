"""The Workshop: Halloween Town makes Christmas its own way, on a conveyor belt that runs the whole roof.

A factory whistle, and the belt starts at the free end of Right: grey slats running the whole roofline toward
Side, lit a run at a time. Presents ride it in red, green, orange and violet, and at the five corners of the
house hammers ring in turn on the beat, each strike a white flash and a spray of sparks, to the workshop theme in
A minor (a busy, mechanical tune on xylophone, pizzicato and bassoon over an oom-pah). The toys come out wrong.
A shrunken head rides in on Right and shrivels to a point in a green flash; a striped snake on Porch Front
swallows a little Christmas tree whole, star and all, a bulge sliding down it; a yellow duck on Left honks, bares
white fangs and bites, flashing the wing red. On Porch Front the rag doll sews the red suit to her theme: a red
span grows a stitch at a time with white trim at its ends. On Left, four skeleton reindeer are fitted with
harnesses, a red strap and a gold bell flashing on each with a jingle. Then the whole works runs flat out: the
belt at double speed, toys streaming, hammers on every corner on every beat, the band in full, and a last crash
with every corner blazing.

compose() lays the music end to end: render() and score() read its events and marks."""
import numpy as np
from pixelhome.audio import SR, slide
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, DUSK, MOON,
                                 BONE, WHITE, GOLD, RED, GREEN, GREY, WARM, BLUE, SALLY)

CODE = 'NM10'
TITLE = 'The Workshop'
KIND = 'show'
DESCRIPTION = ('A conveyor belt of toys runs the whole roof while hammers spark at every corner. The toys come out '
               'wrong: a shrinking head, a snake that swallows a tree, a duck with fangs. The red suit is sewn and the '
               'skeleton reindeer get their harnesses.')
VOICEOVER = ('All of Halloween Town went to work making Christmas. '
             'They did it the only way they knew how.')

YELLOW = hexc('#ffe000')
SKIN = hexc('#70c020')
SLAT = hexc('#a0a8c0')
TOYS = (RED, GREEN, ORANGE, VIOLET, BLUE)


def compose():
    C = Chart()
    C.rest(1.6)                                                     # the whistle; the belt starts
    C.mark('build')
    C.play('workshop', style='march', bpm=132, tag='build')
    C.mark('wrong')
    C.play('workshop', style='march', bpm=132, tag='wrong')         # the toys come out wrong
    C.mark('suit')
    C.play('sally', style='waltz', bars=(0, 4), bpm=120, tag='suit')    # the rag doll sews the suit
    C.mark('reindeer')
    C.play('workshop', style='drive', bars=(0, 4), bpm=132, tag='reindeer')   # harnesses for the reindeer
    C.mark('finale')
    C.play('workshop', style='march', bpm=144, tag='finale')
    C.mark('out')
    C.rest(1.8)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
WDB = C.downbeats('wrong')
T_HEAD, T_SNAKE, T_DUCK = WDB[1] + 0.2, WDB[4] + 0.2, WDB[6] + 0.2
SUIT_T = [n[0] for n in C.tunes('suit')]
RDB = C.downbeats('reindeer')
HAMMER_TAGS = ('build', 'wrong', 'reindeer', 'finale')
HAMMERS = [t for t, k, g in C.beats if g in HAMMER_TAGS]


def belt_speed(t):
    """How fast the belt runs (units a second, toward Side)."""
    return keys(t, [(0.8, 0.0), (1.8, 150.0), (M['suit'], 150.0), (M['suit'] + 0.5, 90.0), (M['finale'] - 0.5, 90.0),
                    (M['finale'] + 0.5, 300.0), (M['out'], 300.0), (D, 120.0)])


_T = np.arange(int(D / DT) + 2) * DT
_X = np.concatenate([[0.0], np.cumsum([float(belt_speed(t)) for t in _T[:-1]]) * DT])


def belt_x(t):
    return float(np.interp(t, _T, _X))


def corners(S):
    return [S.at(r, 0) - 2 for r in ('Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')]


def hammer_hits(S):
    """(time, corner index): in turn round the corners on every beat; in the finale every corner on every beat."""
    out = []
    for i, t in enumerate(HAMMERS):
        if t >= M['finale']:
            out += [(t, k) for k in range(5)]
        else:
            out.append((t, (4 - i) % 5))
    return out


def toys():
    """Presents put on the belt at the free end of Right: (time, colour index), one a bar, two a bar at the end."""
    out = []
    for g in ('build', 'wrong', 'reindeer', 'finale'):
        db = C.downbeats(g)
        for k, t in enumerate(db):
            out.append((t, (k * 3 + len(out)) % len(TOYS)))
            if g == 'finale':
                out.append((t + (db[1] - db[0]) / 2, (k + 2) % len(TOYS)))
    return out


def ride(S, t, te):
    """Where a toy put on the belt at te is at t."""
    return S.L - (belt_x(t) - belt_x(te))


def entry_for(S, p, t):
    """When a toy must be put on the belt to be at p at t."""
    target = belt_x(t) - (S.L - p)
    return float(np.interp(target, _X, _T))


def places(S):
    return dict(head=S.at('Right', 0.5), snake=S.at('Porch Front', 0.5), duck=S.at('Left', 0.55),
                doll=S.at('Porch Front', 0.2), suit=S.at('Porch Front', 0.62),
                deer=[S.at('Left', u) for u in (0.2, 0.4, 0.6, 0.8)])


def render(G, seed=10):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    P = places(S)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array([b[0] for b in C.beats])
    hits = hammer_hits(S)
    hit_t = np.array([h[0] for h in hits])
    cn = corners(S)
    gifts = toys()
    te_head = entry_for(S, P['head'], T_HEAD)
    te_snake = entry_for(S, P['snake'], T_SNAKE)
    te_duck = entry_for(S, P['duck'], T_DUCK)

    for f in range(F):
        t = f * DT
        beat = pulse(t, beats, 0.12)
        on = smoothstep(L - 2600 * smoothstep(1.0, 2.6, t), L - 2600 * smoothstep(1.0, 2.6, t) + 60, d)
        bx = belt_x(t)
        # the belt: grey slats running toward Side over a violet works, warm lamps here and there
        slat = ((d + bx) / 26.0) % 1.0 < 0.45
        xmas = smoothstep(M['finale'] - 0.3, M['finale'] + 0.5, t)
        scol = np.where((((d + bx) / 52.0) % 2 < 1)[:, None], RED, GREEN)
        fr = light(DUSK, 0.35 * on) + light(SLAT, 0.5 * (1 - xmas) * on * slat * (0.85 + 0.15 * beat))
        fr += light(scol, 0.75 * xmas * on * slat * (0.8 + 0.2 * beat))
        fr += light(PUMPKIN, 0.3 * on * (G.pi % 25 == 12))
        lv_all = smoothstep(D, D - 1.2, t)

        # hammers at the corners: a white strike and a spray of sparks
        for j in np.flatnonzero((hit_t <= t) & (hit_t > t - 0.5)):
            a = t - hit_t[j]
            p = cn[hits[j][1]]
            fr += light(WHITE, 1.1 * np.exp(-a / 0.08) * S.blob(p, 22))
            fr += light(GOLD, 0.9 * np.exp(-a / 0.2) * S.blob(p, 110))
            fr += light(WARM, 0.45 * np.exp(-a / 0.3) * S.blob(p, 260) * (t < M['finale']))
        fr += S.burst([(t0, 0.7, cn[k]) for t0, k in hits if t - 1.6 < t0 <= t], t, seed=5, n=6, reach=0.25,
                      colors=(GOLD, WHITE))

        # the presents riding the belt
        for i, (te, c) in enumerate(gifts):
            if te <= t:
                p = ride(S, t, te)
                if -20 < p <= L:
                    rib = GOLD if i % 2 else WHITE
                    fr = S.sprite(fr, p, [(2, TOYS[c], 0.9), (1, TOYS[c], 0.95), (0, rib, 1.0), (-1, TOYS[c], 0.95),
                                          (-2, TOYS[c], 0.9)], 1.0)
                    fr += light(TOYS[c], 0.6 * S.blob(p, 40))

        # the wrong toys. A shrunken head that shrivels to a point
        if te_head <= t < T_HEAD + 1.5:
            p = ride(S, t, te_head)
            a = t - T_HEAD
            size = 1.0 if a < 0 else np.exp(-a / 0.35)
            fr += light(SKIN, 1.0 * np.exp(-((d - p) / (6 + 34 * size)) ** 2) * (size > 0.05))
            fr = S.sprite(fr, p, [(2, None, 0), (1, SKIN, 0.6), (0, SKIN, 0.6), (-1, None, 0)], 1.0 * size)
            if a >= 0:
                fr += light(SLIME, 1.0 * np.exp(-a / 0.5) * (S.run['Right'] | S.run['Porch Right']))
            fr += S.burst([(T_HEAD + 0.6, 0.9, P['head'])], t, seed=31, n=16, reach=0.5, colors=(SLIME, WHITE))
        # a striped snake that swallows a little tree, star and all
        if te_snake - 1.5 <= t < T_SNAKE + 3.0:
            p = ride(S, t, te_snake)
            a = t - T_SNAKE
            lunge = 0 if a < 0 else 20 * np.exp(-a / 0.3) * (a < 1)
            for o in range(20):
                c = GREEN if (o // 2) % 2 else GOLD
                bulge = 0.5 * np.exp(-((o - 18 * min(max(a - 0.3, 0) / 1.8, 1)) / 1.5) ** 2) if a > 0.3 else 0
                fr = S.sprite(fr, p + o * 4.5, [(0, c, 0.7 + bulge)], 1.0, cut=False)
            fr = S.sprite(fr, p - lunge, [(1, RED, 1.0), (0, None, 0)], 1.0, -1)
            if a < 0.25:                                            # the tree waits ahead of it
                tp = p - 40
                fr = S.sprite(fr, tp, [(2, GOLD, 1.0), (1, GREEN, 0.9), (0, GREEN, 0.9), (-1, GREEN, 0.9)], 1.0, -1)
            if a >= 0.25:
                b = a - 0.25
                fr += light(GREEN, 1.0 * np.exp(-b / 0.5) * S.porch)
                fr += light(GOLD, 0.9 * np.exp(-b / 0.2) * S.blob(p, 60))
            fr += S.burst([(T_SNAKE + 0.25, 1.0, P['snake'])], t, seed=32, n=20, reach=0.7, colors=(GOLD, GREEN))
        # a duck that honks, bares its fangs and bites
        if te_duck <= t < T_DUCK + 2.0:
            p = ride(S, t, te_duck)
            a = t - T_DUCK
            fr = S.sprite(fr, p, [(2, ORANGE, 1.0), (1, YELLOW, 1.0), (0, YELLOW, 1.0), (-1, YELLOW, 0.9),
                                  (-2, YELLOW, 0.8)], 1.0, -1)
            fr += light(YELLOW, 0.5 * S.blob(p, 40))
            if -1.0 <= a < -0.5 or -0.5 <= a < 0:
                fr += light(YELLOW, 0.6 * pulse(t, [T_DUCK - 1.0, T_DUCK - 0.6], 0.15) * S.run['Left'])
            if a >= 0:
                fr += light(WHITE, 1.0 * np.exp(-a / 0.2) * (S.blob(p - 12, 6) + S.blob(p - 20, 6)))
                fr += light(RED, 1.0 * np.exp(-a / 0.5) * (S.run['Left'] | S.run['Side'] | S.run['Porch Left']))
            fr += S.burst([(T_DUCK, 1.0, P['duck'])], t, seed=33, n=20, reach=0.7, colors=(WHITE, RED, YELLOW))

        # the red suit, sewn on Porch Front by the rag doll, a stitch at a time
        if M['suit'] - 0.5 <= t < M['finale'] + 1.0:
            lv = smoothstep(M['suit'] - 0.5, M['suit'], t) * smoothstep(M['finale'] + 1.0, M['finale'], t)
            fr = fr * (1 - 0.4 * lv * S.porch[:, None])
            fr += light(SALLY, 0.3 * lv * S.porch)
            k = int(np.searchsorted(SUIT_T, t, side='right'))
            n = k / len(SUIT_T)
            half = 6 + 90 * n
            fr += light(RED, 0.95 * lv * S.span(P['suit'] - half, P['suit'] + half))
            if n >= 1:
                fr += light(WHITE, 0.9 * lv * (S.blob(P['suit'] - half, 6) + S.blob(P['suit'] + half, 6)))
            if k > 0:
                a = t - SUIT_T[k - 1]
                side = 1 if k % 2 else -1
                fr += light(WHITE, lv * np.exp(-a / 0.15) * S.blob(P['suit'] + side * half, 5))
                fr += light(RED, 0.5 * lv * np.exp(-a / 0.25) * S.wings)
            fr = S.sally(fr, P['doll'], lv, facing=1)
        # the skeleton reindeer on Left, each fitted with a red strap and a gold bell on a downbeat
        if M['reindeer'] - 0.5 <= t < M['out']:
            lv = smoothstep(M['reindeer'] - 0.5, M['reindeer'], t)
            for i, p in enumerate(P['deer']):
                leap = 0.8 + 0.2 * np.sin(2 * np.pi * (1.5 * t + i / 4))
                fr = S.sprite(fr, p, [(2, BONE, 1.0), (1, BONE, 0.7), (0, BONE, 0.5), (-1, BONE, 0.5),
                                      (-2, BONE, 0.4)], lv * leap, -1)
                if t >= RDB[i]:
                    a = t - RDB[i]
                    fr = S.sprite(fr, p - 4.0, [(0, RED, 0.9), (-1, GOLD, 0.9)], 1.0, -1, cut=False)
                    fr += light(GOLD, 0.9 * np.exp(-a / 0.3) * S.blob(p, 50))
                    fr += light(RED, 0.6 * np.exp(-a / 0.4) * S.run['Left'])
        # flat out: the whole house pulsing Christmas red and green on the beat
        if t >= M['finale']:
            a = t - M['finale']
            lv = smoothstep(0, 1.0, a)
            col = np.where(((G.pi + int(bx / 26)) % 6 < 3)[:, None], RED, GREEN)
            fr += light(col, lv * 0.5 * beat * np.ones(G.N))
            if t >= M['out']:
                b = t - M['out']
                for p in cn:
                    fr += light(WHITE, 1.0 * np.exp(-b / 0.6) * S.blob(p, 140))
                fr += light(GOLD, 0.8 * np.exp(-b / 0.7) * np.ones(G.N))
        out[f] = fr * lv_all
    return np.clip(out, 0, 1)


def _whistle(B, t, dur=1.2):
    """The factory whistle: a steamy chord."""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = np.clip(tt / 0.08, 0, 1) * np.clip((dur - tt) / 0.3, 0, 1)
    sig = sum(np.sin(2 * np.pi * f * (1 + 0.01 * np.sin(2 * np.pi * 5 * tt)) * tt) for f in (587, 740, 880))
    sig = env * (sig / 3 + 0.25 * B._noise(0, 2000, 8000, 5, n=n))
    B._sfx(sig, t, 0.35, 0.8)


def _belt_hum(B, t0, t1):
    n = int((t1 - t0) * SR)
    tt = np.arange(n) / SR
    sp = np.array([float(belt_speed(t0 + x)) for x in tt[::SR // 20]])
    sp = np.interp(np.arange(n), np.arange(len(sp)) * (SR // 20), sp) / 300.0
    hum = B._noise(0, 60, 400, 7, n=n) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 9 * tt)) * 0.3)
    B._sfx(hum * sp, t0, 0.35, 0.0)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    cn = corners(S)
    B = Band(M_, level=2.7)
    parts = {
        ('build', 'tune'): [('xylo', 0, 2, 0.5), ('bassoons', 0, 2, 0.6), ('pizz', 0, -2, 0.4)],
        ('build', 'bass'): [('tuba', -12, 0, 0.65), ('basses pizz', 0, -4, 0.45)],
        ('build', 'chord'): [('pizz', 0, -4, 0.4)],
        ('wrong', 'tune'): [('clarinets', 0, 4, 0.6), ('xylo', 0, 0, 0.45), ('muted horn', 0, -6, 0.4)],
        ('wrong', 'bass'): [('tuba', -12, 2, 0.7), ('basses pizz', 0, -4, 0.45)],
        ('wrong', 'chord'): [('pizz', 0, -4, 0.4), ('muted horn', 0, -14, 0.25)],
        ('suit', 'tune'): [('oboes', 0, 4, 0.75), ('pizz', 12, -10, 0.3)],
        ('suit', 'bass'): [('basses pizz', 0, 0, 0.55)],
        ('suit', 'chord'): [('harp', 0, -4, 0.45)],
        ('reindeer', 'tune'): [('trumpets', 0, -2, 0.5), ('xylo', 0, 0, 0.45), ('violins', 0, -4, 0.45)],
        ('reindeer', 'bass'): [('tuba', -12, 2, 0.65), ('cellos', 0, -4, 0.45)],
        ('reindeer', 'chord'): [('violas', 0, -10, 0.3)],
        ('finale', 'tune'): [('trumpets', 0, 6, 0.6), ('horns', 0, 4, 0.55), ('violins', 0, 2, 0.55),
                             ('xylo', 0, 0, 0.5), ('choir', 0, -2, 0.55)],
        ('finale', 'bass'): [('tuba', -12, 6, 0.8), ('basses', 0, 0, 0.5), ('timpani', 0, 2, 0.35)],
        ('finale', 'chord'): [('trombones', 0, -4, 0.45), ('pizz', 0, -2, 0.45)],
    }
    B.perform(C.events, parts)
    B.effects([(0, 0), (M['build'] + 1, -5), (T_HEAD - 0.3, -1), (M['suit'], -6), (M['reindeer'], -3),
               (M['finale'], -6), (M['out'] - 0.3, -1)])
    _whistle(B, 0.1)
    _belt_hum(B, 0.8, D)
    # the hammers ring at the corners, an anvil where each strikes
    for t, k in hammer_hits(S):
        if t < M['finale'] or k in (1, 3):
            B.hit('anvil', t, 96 if t < M['finale'] else 108, gain=0.35, pan=S.pan(cn[k]), fx=True)
    # the toys: the head shrivels, the snake hisses and gulps, the duck honks and bites
    B.M.add('fx', slide(0, 0.8, 900, 120, 0.9, amp=0.22), T_HEAD, 0.9, S.pan(P['head']))
    B.hit('guiro', T_HEAD + 0.1, 110, gain=0.6, pan=S.pan(P['head']), fx=True)
    hiss = B._noise(0, 3000, 9000, 9, n=int(1.0 * SR)) * np.hanning(int(1.0 * SR))
    B._sfx(hiss, T_SNAKE - 0.9, 0.3, S.pan(P['snake']))
    B.hit('slapstick', T_SNAKE + 0.25, 120, gain=0.7, pan=S.pan(P['snake']))
    for k, m in enumerate((38, 35, 31)):
        B.play('tuba', m, T_SNAKE + 0.4 + 0.25 * k, 0.3, 110, pan=S.pan(P['snake']), gain=0.8)
    for th in (T_DUCK - 1.0, T_DUCK - 0.6):
        B.play('muted horn', 57, th, 0.15, 120, pan=S.pan(P['duck']), gain=0.9)
        B.play('buzz trombone', 50, th, 0.15, 110, pan=S.pan(P['duck']), gain=0.6)
    B.clash(T_DUCK, pan=S.pan(P['duck']), gain=0.7)
    B.scream(T_DUCK + 0.1, pan=S.pan(P['duck']), gain=0.6)
    # the suit: a little zip with every stitch
    for i, t in enumerate(SUIT_T):
        B.whoosh(t, 0.15, up=bool(i % 2), pan=S.pan(P['suit']), gain=0.3)
    # the reindeer: a clank and a jingle for each harness
    for i, t in enumerate(RDB):
        B.hit('metal', t, 110, gain=0.45, pan=S.pan(P['deer'][i]), fx=True)
        B.sleigh_bells(t, t + 0.6, beat=0.1, pan=S.pan(P['deer'][i]), gain=0.8)
    # flat out, then the last crash
    B.hit('cymbal swell', M['out'] - 1.5, 110, gain=0.5)
    B.hit('crash', M['out'], 124, gain=0.7)
    B.hit('bass drum', M['out'], 124, gain=0.7)
    B.hit('anvil', M['out'], 124, gain=0.6)
    B.finish()
