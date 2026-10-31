"""The Unraveling: Oogie Boogie's last game, and the Pumpkin King pulls the thread that undoes him.

Oogie Boogie's lair glows blacklight violet with green pulsing through it. Santa hangs tied on the left of Porch
Front, the fire pit simmers red on Porch Left, and Oogie Boogie lurks dim on the right of the porch. Sally
slips in from the free end of Right on a hushed pizzicato of her theme, along the wing and round the porch to
Santa, and Oogie Boogie lights up: caught. To his swung shuffle he gloats, pulsing on the beat, and rolls dice down
the right wing four times (white dice tumbling, pips showing), and on the last roll the captives slide toward the
pit as its flames leap. Then a white-orange streak bursts in from the free end of Right with a boom: the Pumpkin
King. They fight in turns, Oogie Boogie's theme against Jack's. Blades fly from the sack at him and he hops
aside; he lunges back with orange blows; Oogie Boogie spins a slot machine on the right wing (three reels of
colours stopping one by one on skulls, a green jackpot, the skulls flying at him); Jack strikes again. Then he
catches a gold thread in the burlap and pulls, backing away along the wing: the sack shrinks and pours out as a
swarm of green bugs that scatter over the whole roof, down to one last little bug crawling along the porch, which
is squashed with a white splat. Santa and Sally are free: the lair warms to red, blue and white on the
king's theme in major.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() both read its events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, UV, WHITE, GOLD,
                                 BONE, RED, GREEN, BLUE, BUG, BURLAP, SALLY, MOON, WARM)

CODE = 'NM18'
TITLE = 'The Unraveling'
KIND = 'show'
DESCRIPTION = ("In Oogie Boogie's glowing lair Sally is caught freeing Santa, dice tumble down the wing and the fire pit "
    'flares. Jack bursts in, dodges blades and a slot machine of skulls, and pulls the thread that pours '
    'Oogie Boogie out as a swarm of bugs across the whole roof.')
VOICEOVER = 'Deep beneath the town, Oogie Boogie was rolling the dice. But Jack was coming.'

STEEL = hexc('#d0e8ff')
REEL = [RED, GOLD, GREEN, BLUE, VIOLET]


def compose():
    C = Chart()
    C.rest(1.5)
    C.mark('sneak')
    C.play('sally', style='arp', bars=(0, 4), bpm=96, tag='sneak')              # Sally slips in
    C.mark('caught')
    C.rest(1.0)                                                                  # caught
    C.mark('gloat')
    C.play('boogey', style='shuffle', bars=(0, 8), bpm=132, tag='gloat')         # dice, and toward the pit
    C.mark('burst')
    C.rest(1.2)                                                                  # Jack bursts in
    C.mark('trick1')
    C.play('boogey', style='drive', bars=(0, 4), bpm=150, tag='trick1')          # blades
    C.mark('dodge1')
    C.play('king', style='drive', bars=(0, 4), bpm=150, tag='dodge1')            # Jack strikes back
    C.mark('trick2')
    C.play('boogey', style='drive', bars=(4, 8), bpm=150, tag='trick2')          # the slot machine
    C.mark('dodge2')
    C.play('king', style='drive', bars=(4, 8), bpm=150, tag='dodge2')
    C.mark('thread')
    C.rest(1.5)                                                                  # a loose thread
    C.mark('unravel')
    C.rest(5.5)                                                                  # the sack pours out as bugs
    C.mark('last')
    C.rest(2.2)                                                                  # the last little bug
    C.mark('saved')
    C.play('king', style='waltz', bars=(12, 16), bpm=100, major=True, tag='saved')
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
PIPS = {1: [0, 0, 1, 0, 0], 2: [1, 0, 0, 0, 1], 3: [1, 0, 1, 0, 1], 4: [1, 1, 0, 1, 1], 5: [1, 1, 1, 0, 1, 1, 1][:5],
        6: [1, 1, 1, 1, 1]}


class Places:
    def __init__(self, S):
        self.oog = S.at('Porch Front', 0.7)
        self.santa = S.at('Porch Front', 0.12)
        self.sally = S.at('Porch Front', 0.27)
        self.pit = S.at('Porch Left', 0.72)
        self.jack0 = S.at('Porch Right', 0.4)
        self.dice = (S.at('Right', 0.05), S.at('Right', 0.55))
        self.reels = [S.at('Right', u) for u in (0.3, 0.55, 0.8)]
        self.pull = S.at('Right', 0.15)


def jack_path(S, P):
    """Jack's position through the fight: hops aside on the blades, lunges in on his blows."""
    pts = [(M['burst'], S.L + 20), (M['burst'] + 0.6, P.jack0)]
    for tag, lunge in (('trick1', False), ('dodge1', True), ('trick2', False), ('dodge2', True)):
        downs = C.downbeats(tag)
        for i, tb in enumerate(downs):
            if lunge:
                pts += [(tb + 0.05, P.oog + 95), (tb + 0.5, P.jack0 - 40)]
            else:
                pts += [(tb + 0.1, P.jack0 + (70 if i % 2 else -50))]
    pts += [(M['thread'], P.oog + 85), (M['unravel'] + 2.5, P.pull), (M['last'], P.pull),
            (M['last'] + 1.2, P.oog - 120), (M['saved'] + 2, S.mid + 30)]
    pts = sorted(pts)
    clean = [pts[0]]
    for p in pts[1:]:
        if p[0] - clean[-1][0] > 0.04:
            clean.append(p)
    return clean


def render(G, seed=18):
    S = Stage(G)
    d, mid = S.d, S.mid
    P = Places(S)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    t_sn, t_ca, t_gl, t_bu = M['sneak'], M['caught'], M['gloat'], M['burst']
    t_t1, t_d1, t_t2, t_d2 = M['trick1'], M['dodge1'], M['trick2'], M['dodge2']
    t_th, t_un, t_la, t_sa = M['thread'], M['unravel'], M['last'], M['saved']
    jp = jack_path(S, P)
    gloat_beats = np.array([b[0] for b in C.beats if b[2] == 'gloat'])
    rolls = C.downbeats('gloat')[::2]
    tip = rolls[-1]
    blades = [n[0] for n in C.tunes('trick1')][::2]
    blows = np.array([n[0] for n in C.tunes('dodge1') + C.tunes('dodge2')])
    sneak_steps = np.array([b[0] for b in C.beats if b[2] == 'sneak'])
    stops = [t_t2 + 2.2, t_t2 + 3.1, t_t2 + 4.0]
    jackpot = t_t2 + 4.4
    # the swarm: bugs born as the sack unravels, each running off along the roof
    nb = 260
    born = np.sort(rng.uniform(t_un, t_un + 4.2, nb))
    v0 = rng.uniform(180, 1000, nb) * rng.choice([-1, 1], nb)
    life = rng.uniform(2.0, 3.6, nb)
    wig = rng.uniform(0, 2 * np.pi, nb)
    p_last = P.oog - 60

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.5, t)
        saved = smoothstep(t_sa, t_sa + 3, t)
        dim = 1 - 0.45 * smoothstep(t_un, t_un + 0.8, t) * (1 - smoothstep(t_la + 1.4, t_la + 2.2, t))
        fr = S.lair(t, lv=0.62 * up * dim * (1 - 0.7 * saved))
        # the fire pit on Porch Left: simmering, flaring when the captives are tipped toward it
        flare = keys(t, [(tip - 0.2, 0.35), (tip + 1.5, 1.0), (t_bu, 1.0), (t_bu + 1.5, 0.4), (t_sa, 0.4),
                         (t_sa + 3, 0.0)])
        flick = 0.7 + 0.3 * np.sin(21 * t + d / 6) * np.sin(5 * t - d / 13)
        fr += light(FLAME, up * flare * S.blob(P.pit, 70 + 160 * flare) * flick)
        fr += light(GOLD, 0.6 * up * flare * S.blob(P.pit, 25 + 40 * flare) * flick)
        # Santa, tied (and Sally beside him once caught), sliding toward the pit on the last roll
        slide = smoothstep(tip, tip + 3.0, t) * (1 - smoothstep(t_la + 1.5, t_sa + 1.5, t))
        ps = P.santa + (P.pit + 70 - P.santa) * slide
        pr = P.sally + (P.pit + 135 - P.sally) * slide
        if t < t_sa:
            fr += light(RED, 0.25 * up * S.blob(ps, 50))
        fr = S.santa(fr, ps, up, facing=1)
        # Sally sneaking in from the free end of Right, tiptoeing on the beat
        if t >= t_sn:
            psal = np.interp(t, [t_sn, t_ca], [S.L + 15, P.sally]) if t < t_ca else pr
            if t_sa <= t:
                psal = P.sally + (pr - P.sally) * (1 - saved)
            tip_toe = 0.8 + 0.2 * pulse(t, sneak_steps, 0.12) if t < t_ca else 1.0
            fr += light(SALLY, 0.3 * S.blob(psal, 60))
            fr = S.sally(fr, psal, tip_toe, facing=-1)
        # Oogie Boogie: dim and lurking, lights up when she's caught, pulses with his shuffle, unravels
        if t < t_un + 4.5:
            size = 1.0 - smoothstep(t_un, t_un + 4.2, t) * 0.92
            lit = 0.35 + 0.65 * smoothstep(t_ca, t_ca + 0.2, t)
            bump = pulse(t, gloat_beats, 0.15) if t_gl <= t < t_bu else 0.0
            for tb in blows[(blows <= t) & (blows > t - 0.4)]:
                bump += 0.8 * np.exp(-(t - tb) / 0.1)
            if t_ca <= t < t_ca + 0.6:
                fr += light(SLIME, 0.9 * np.exp(-(t - t_ca) / 0.2) * np.ones(G.N))
            fr += light(BUG, 0.35 * lit * S.blob(P.oog, 140 * size + 20))
            fr = S.oogie(fr, P.oog, up * min(1.3, lit + 0.3 * bump), t, size=max(size, 0.1))
        # dice: rolled down the right wing on every other downbeat, tumbling then landing
        for k, tr in enumerate(rolls):
            a = t - tr
            if 0 <= a < 2.2:
                for j, pd0 in enumerate(P.dice):
                    u = 1 - np.exp(-a / 0.35)
                    pdie = P.oog + (pd0 + 140 * j - P.oog) * u
                    face = (int(a * 14) + 3 * j) % 6 + 1 if a < 0.9 else [5, 6, 3, 6][k] if j else [2, 4, 1, 6][k]
                    px = [(o - 3, BONE, 0.35) for o in (0, 6)] + \
                         [(o - 2, WHITE if PIPS[face][o] else None, 1.0) for o in range(5)]
                    fr = S.sprite(fr, pdie, px, 1.0 if a < 1.8 else (2.2 - a) / 0.4)
                    if 0.9 <= a < 1.3:
                        fr += light(RED, 0.8 * np.exp(-(a - 0.9) / 0.15) * S.blob(pdie, 50))
        # Jack bursts in from the free end of Right
        if t_bu <= t < t_bu + 1.0:
            a = t - t_bu
            fr += light(ORANGE, 0.8 * np.exp(-((a - 0.6) / 0.15) ** 2) * np.ones(G.N))
            fr += light(WHITE, 0.6 * np.exp(-((a - 0.6) / 0.08) ** 2) * np.ones(G.N))
        if t >= t_bu:
            pj = keys(t, jp)
            fr += light(ORANGE, 0.35 * S.blob(pj, 70))
            if t < t_bu + 0.6:
                fr += light(WHITE, 0.7 * smoothstep(pj - 10, pj + 30, d) * np.exp(-np.clip(d - pj, 0, None) / 200))
            fr = S.jack(fr, pj, 1.0, facing=-1, glow=0.4)
        # blades flying from the sack at him, silver streaks
        for tb in blades:
            a = t - tb
            if 0 <= a < 0.9:
                pb = P.oog + 60 + 1100 * a
                fr += light(STEEL, 1.0 * smoothstep(pb - 70, pb, d) * smoothstep(pb + 6, pb, d))
                fr += light(WHITE, 0.6 * S.blob(pb, 10))
        # Jack's blows: orange bursts between them
        for tb in blows[(blows <= t) & (blows > t - 0.5)]:
            a = t - tb
            fr += light(ORANGE, 0.9 * np.exp(-a / 0.12) * S.blob(P.oog + 75, 50))
        if t_d1 <= t < t_t2 or t_d2 <= t < t_th:
            fr += light(PUMPKIN, 0.3 * pulse(t, C.downbeats('dodge1') + C.downbeats('dodge2'), 0.2) *
                        (S.wings | S.run['Side']))
        # the slot machine on the right wing: reels spinning, stopping on skulls, the green jackpot
        if t_t2 <= t < jackpot + 1.6:
            for i, pr_ in enumerate(P.reels):
                spinning = t < stops[i]
                for o in range(-5, 6):
                    if spinning:
                        col = REEL[(int(t * 18) + o + 2 * i) % len(REEL)]
                        fr = S.sprite(fr, pr_ + 4 * o, [(0, col, 0.9)], 1.0, cut=False)
                if not spinning:
                    a = t - stops[i]
                    fr = S.sprite(fr, pr_, [(2, BONE, 1.0), (1, None, 0), (0, BONE, 1.0), (-1, None, 0),
                                            (-2, BONE, 1.0), (-3, BONE, 0.7)], 1.0)
                    fr += light(WHITE, 0.6 * np.exp(-a / 0.15) * S.blob(pr_, 40))
                fr += light(GOLD, 0.35 * S.blob(pr_, 55))
            if t >= jackpot:
                a = t - jackpot
                fr += light(SLIME, 0.8 * np.exp(-a / 0.3) * S.run['Right'])
                for i, pr_ in enumerate(P.reels):          # the skulls fly at him
                    psk = pr_ - 700 * a
                    fr += light(BONE, 0.9 * (a < 1.4) * S.blob(psk, 9))
        # a loose thread: gold from the sack to his hand as he backs away pulling it
        if t_th <= t < t_un + 4.4:
            pj = keys(t, jp)
            a0, a1 = sorted((P.oog + 40, pj))
            shimmer = 0.75 + 0.25 * np.sin(d / 4 - 20 * t)
            fr += light(GOLD, (0.9 if t < t_un else 0.6) * S.span(a0, a1, 3) * shimmer)
            if t < t_un:
                fr += light(GOLD, 0.8 * np.exp(-((t - t_th) % 0.5) / 0.15) * S.blob(P.oog + 50, 18))
        # the swarm: bugs pouring out and scattering across the whole roof
        if t_un <= t < t_la + 1:
            a = t - born
            alive = (a >= 0) & (a < life)
            if alive.any():
                aa = a[alive]
                pb = P.oog + np.sign(v0[alive]) * 40 + v0[alive] * aa * (1 - 0.15 * aa) + \
                    12 * np.sin(9 * aa + wig[alive])
                lv = np.clip(1 - aa / life[alive], 0, 1) ** 0.5 * (0.7 + 0.3 * np.sin(25 * aa + wig[alive]))
                k = np.exp(-((d[None, :] - pb[:, None]) / 6) ** 2) * lv[:, None]
                fr += light(BUG, np.clip(k.sum(0), 0, 1.2))
                fr += light(BURLAP, 0.3 * np.exp(-a[alive].min() / 0.5) * S.blob(P.oog, 80))
            fr += light(SLIME, 0.25 * np.exp(-(t - t_un) / 1.5) * np.ones(G.N))
        # the last little bug, crawling along the porch until it's squashed
        if t_la <= t < t_la + 2.2:
            a = t - t_la
            sq = t_la + 1.35
            if t < sq:
                pl = p_last - 90 * a
                fr += light(BUG, (0.9 + 0.1 * np.sin(30 * t)) * S.blob(pl, 5))
                fr += light(BUG, 0.25 * S.blob(pl, 25))
            else:
                b = t - sq
                pl = p_last - 90 * (sq - t_la)
                fr += light(WHITE, 1.0 * np.exp(-b / 0.1) * S.blob(pl, 40))
                fr += light(BUG, 0.5 * np.exp(-b / 0.4) * S.blob(pl, 15))
        # saved: the lair warms to Santa's red, Sally's blue and Jack's white
        if t >= t_sa:
            fr += light(RED, 0.4 * saved * (S.run['Left'] | S.run['Side'] | S.run['Porch Left']))
            fr += light(SALLY, 0.45 * saved * (S.run['Right'] | S.run['Porch Right']))
            fr += light(WARM, 0.35 * saved * S.run['Porch Front'])
            fr += light(GOLD, 0.4 * saved * pulse(t, C.downbeats('saved'), 0.3) * np.ones(G.N))
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = Places(S)
    B = Band(M_, level=2.75)
    parts = {
        ('sneak', 'tune'): [('clarinets', 0, -4, 0.55), ('pizz', 12, -10, 0.3)],
        ('sneak', 'arp'): [('harp', 0, -8, 0.45)],
        ('sneak', 'pedal'): [('basses pizz', 0, -6, 0.5)],
        ('gloat', 'tune'): [('buzz trombone', 0, 4, 0.8), ('trombones', 0, -2, 0.5), ('bassoons', 0, -6, 0.4)],
        ('gloat', 'bass'): [('basses pizz', 0, 4, 0.7), ('tuba', -12, -6, 0.4)],
        ('gloat', 'chord'): [('muted horn', 0, -8, 0.4)],
        ('gloat', 'snare'): [('ride', 0, -10, 0.4)],
        ('gloat', 'tick'): [('ride', 0, -20, 0.25)],
        ('trick1', 'tune'): [('buzz trombone', 0, 6, 0.8), ('trombones', 0, 2, 0.6)],
        ('trick2', 'tune'): [('buzz trombone', 0, 6, 0.8), ('trombones', 0, 2, 0.6), ('xylo', 12, -6, 0.35)],
        ('dodge1', 'tune'): [('horns', 0, 8, 0.8), ('trumpets', 0, 0, 0.55), ('violins', 12, -2, 0.5)],
        ('dodge2', 'tune'): [('horns', 0, 8, 0.8), ('trumpets', 0, 0, 0.55), ('violins', 12, -2, 0.5)],
        'bass': [('cellos', 0, -2, 0.5), ('basses', -12, -6, 0.4)],
        'chord': [('violas', 0, -10, 0.35), ('pizz', 0, -6, 0.35)],
        'snare': [('snare', 0, -4, 0.45)],
        ('saved', 'tune'): [('horns', 0, 6, 0.8), ('violins', 12, -2, 0.6), ('choir', 0, -6, 0.6)],
        ('saved', 'bass'): [('tuba', -12, 0, 0.6), ('basses', 0, -6, 0.5)],
        ('saved', 'chord'): [('violas', 0, -8, 0.4), ('harp', 0, -6, 0.4)],
    }
    B.perform(C.events, parts)
    t_ca, t_gl, t_bu, t_t1, t_t2 = M['caught'], M['gloat'], M['burst'], M['trick1'], M['trick2']
    t_th, t_un, t_la, t_sa = M['thread'], M['unravel'], M['last'], M['saved']
    rolls = C.downbeats('gloat')[::2]
    blades = [n[0] for n in C.tunes('trick1')][::2]
    blows = [n[0] for n in C.tunes('dodge1') + C.tunes('dodge2')]
    stops = [t_t2 + 2.2, t_t2 + 3.1, t_t2 + 4.0]
    jackpot = t_t2 + 4.4
    jp = jack_path(S, P)
    # caught: a stinger
    B.hit('gong', t_ca, 110, pitch=-2, gain=0.4)
    B.hit('ratchet', t_ca + 0.05, 110, gain=0.6)
    for m in (43, 49, 55):
        B.play('trombones', m, t_ca, 0.9, 115, gain=0.5)
    B.play('violins trem', 75, t_ca, 0.9, 100, gain=0.4)
    # the burst, the thread and the unravelling
    B.hit('crash', t_bu + 0.6, 124, gain=0.7)
    B.hit('timpani roll', t_th, 100, pitch=-3, gain=0.5)
    B.play('violins trem', 80, t_th, t_un - t_th + 1.0, 90, gain=0.4)
    for i in range(16):
        tt = t_un + i * 0.26
        B.play('xylo', 84 - i, tt, 0.2, 100 - 2 * i, gain=0.45)
        B.play('bassoons', 58 - i, tt, 0.25, 100 - 2 * i, gain=0.45)
    for i in range(5):
        B.play('pizz', 84 + (i % 2) * 3, t_la + i * 0.25, 0.1, 80, gain=0.35, pan=S.pan(P.oog - 60))
    for m in (45, 57, 61, 64):
        B.play('horns', m, t_sa - 0.05, 0.5, 100, gain=0.3)
    # the stage
    B.effects([(0, -4), (t_gl, -6), (rolls[-1], -2), (t_bu, 2), (t_t1 + 1, -3), (t_th, 0), (t_un, 2),
               (t_sa, -8)])
    for k, tr in enumerate(rolls):
        for j in range(6):
            B.hit('wood' if j % 2 else 'claves', tr + 0.13 * j, 100 - 6 * j, gain=0.5, pan=0.6, fx=True)
        B.hit('slapstick', tr + 0.9, 110, gain=0.5, pan=0.7, fx=True)
    B.fire(rolls[-1], t_bu + 2.0, level=0.7, pan=S.pan(P.pit), seed=6)
    B.hit('ratchet', rolls[-1] + 0.3, 100, gain=0.5, pan=S.pan(P.pit), fx=True)
    B.scream(rolls[-1] + 1.0, pan=S.pan(P.sally), gain=0.7, high=1.3)
    B.whoosh(t_bu, seconds=0.7, up=True, pan=0.85, gain=0.9)
    B.boom(t_bu + 0.6, pan=S.pan(P.jack0), gain=1.0)
    for tb in blades:
        B.whoosh(tb, seconds=0.5, up=False, pan=S.pan(P.oog + 300), gain=0.5)
        B.hit('metal', tb + 0.35, 110, gain=0.5, pan=S.pan(P.jack0), fx=True)
    for tb in blows[::2]:
        B.clash(tb, pan=S.pan(P.oog + 70), v=112, gain=0.6)
    B.hit('ratchet', t_t2, 100, gain=0.6, pan=0.6, fx=True)
    B.hit('ratchet', t_t2 + 1.0, 100, gain=0.6, pan=0.6, fx=True)
    for i, ts in enumerate(stops):
        B.hit('cowbell', ts, 110, gain=0.5, pan=S.pan(P.reels[i]), fx=True)
    B.hit('bell tree', jackpot, 110, gain=0.6, pan=0.6, fx=True)
    for m in (67, 71, 74, 79):
        B.play('glock', m, jackpot + 0.06 * (m - 67) / 4, 0.3, 110, gain=0.4)
    B.whoosh(jackpot + 0.1, seconds=1.0, up=False, pan=0.4, gain=0.6)
    B.hit('scrape', t_th, 100, gain=0.6, pan=S.pan(P.oog), fx=True)
    B.swarm(t_un, t_la + 0.6, level=1.0, pan=S.pan(P.oog))
    B.swarm(t_un + 0.8, t_la + 0.3, level=0.6, pan=-0.6, seed=7)
    B.swarm(t_un + 1.2, t_la + 0.3, level=0.6, pan=0.8, seed=9)
    sq = t_la + 1.35
    B.hit('slapstick', sq, 124, gain=0.8, pan=S.pan(P.oog - 180), fx=True)
    B.hit('bass drum', sq, 110, gain=0.5, pan=S.pan(P.oog - 180), fx=True)
    B.finish()
