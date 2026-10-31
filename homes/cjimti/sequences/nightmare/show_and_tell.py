"""Show and Tell: back in Halloween Town the Pumpkin King shows the town what he found, and the town gets every
bit of it wrong.

A meeting bell, and Halloween Town comes up in violet and orange, the citizens crowding in a face at a time round
the porch sides and both wings to the march (bassoon and pizzicato). The mayor's face glows by the stage. On Porch
Front the king shows his treasures one by one, each unveiled in a sparkle of the Christmas Town tune on celesta
and sleigh bells, and each time the town's march answers with what the crowd makes of it: a red present with a
gold bow (they lean in; it snaps at them, red jaws and white flashes, and they flinch), a red and white stocking
(something lumpy and green is in it: a foot? they gasp), a shining gold ornament (one green citizen slides up and
swallows it with a crunch), and a teddy bear (the whole crowd shrieks and scatters to the ends of the house).
Then he tells them about the king of Christmas, and in their heads he becomes a monster: a huge red body swells
over the porch, and two great lobster claws on the porch sides snap on the downbeats to low brass and anvils
while the crowd comes running back and roars on every snap. The two tunes collide: the town's march on tuba and
buzzing trombone across the left of the house in orange and green, the Christmas tune on piccolo and glockenspiel
across the right in coloured bulbs, the line between them sloshing back and forth until they mix. The march ends
fortissimo with the whole town on board, the claws snapping and the house flashing orange and green.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events, so every
snap, gasp and roar lands on the music."""
import numpy as np
from pixelhome.fx import DT, nframes, light, perc, smoothstep, keys, hexc
from pixelhome.nightmare import (drift, Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, BONE, WHITE,
                                 RED, GREEN, GOLD, BLUE, ICE, MOON, WARM)

CODE = 'NM06'
TITLE = 'Show and Tell'
KIND = 'show'
DESCRIPTION = ('On the porch the king shows the town a present, a stocking, an ornament and a teddy bear, and the '
               'crowd round the house gets each one wrong. Then giant red claws snap over the porch and the town roars.')
VOICEOVER = ('The king calls a town meeting. He has seen something wonderful. Now he only has to explain it.')

TEDDY = hexc('#c06020')
LUMP = hexc('#40c020')
CROWD = [PUMPKIN, SLIME, VIOLET, BONE, FLAME, hexc('#ffd040')]
GIFTS = ['present', 'stocking', 'ornament', 'teddy']
REACT = [((4, 6), 'drive', 132), ((2, 4), 'march', 132), ((6, 8), 'march', 132), ((0, 2), 'drive', 150)]


def compose():
    C = Chart()
    C.rest(2.0)                                             # the meeting bell; the town comes up
    C.mark('gather')
    C.play('town', style='march', bars=(0, 4), bpm=120, tag='gather')
    for i, g in enumerate(GIFTS):
        C.mark(g)
        C.play('wonder', style='arp', bars=(2 * i, 2 * i + 2), bpm=330, tag=g)          # he shows it
        bars, style, bpm = REACT[i]
        C.mark(f'r{i}')
        C.play('town', style=style, bars=bars, bpm=bpm, tag=f'r{i}')                   # what they make of it
    C.mark('claws')
    C.play('town', style='hold', bars=(4, 8), bpm=100, transpose=-12, octave=0, tag='claws')
    C.mark('collide')
    t0 = C.t
    C.play('town', style='march', bars=(0, 8), bpm=120, tag='collide')
    t1 = C.t
    C.t = t0
    C.play('wonder', style='none', bpm=180, tag='xmas', vel=92)                         # both at once
    C.t = max(C.t, t1)
    C.mark('roar')
    C.play('town', style='march', bars=(4, 8), bpm=132, tag='roar')
    C.mark('hit')
    C.rest(2.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def crowd(S, rng):
    """The citizens: where each stands (path distance), its colour, when it arrives, which way is outward."""
    spots = []
    for run, a, b, n in (('Left', 0.06, 0.94, 10), ('Porch Left', 0.08, 0.7, 7), ('Porch Right', 0.3, 0.92, 5),
                         ('Right', 0.05, 0.92, 12), ('Side', 0.5, 0.95, 4)):
        for u in np.linspace(a, b, n):
            spots.append(S.at(run, u + rng.uniform(-0.02, 0.02)))
    p = np.array(spots)
    out = np.sign(p - S.mid)
    cols = np.array([CROWD[i % len(CROWD)] for i in range(len(p))])
    arrive = M['gather'] + 0.5 + rng.permutation(len(p)) / len(p) * 6.5
    return p, cols, arrive, out


def render(G, seed=6):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    cp, ccol, carr, cout = crowd(S, rng)
    town_beats = np.array([b[0] for b in C.beats if b[2] != 'xmas'])
    downs = np.array(C.downbeats())
    react_beats = {i: np.array([b[0] for b in C.beats if b[2] == f'r{i}']) for i in range(4)}
    claw_downs = np.array(C.downbeats('claws') + C.downbeats('roar'))
    wonder_t = np.array([n[0] for n in C.tunes() if n[0] < M['claws'] and any(M[g] <= n[0] < M[f'r{i}']
                                                                              for i, g in enumerate(GIFTS))])
    town_t = np.array([n[0] for n in C.tunes('collide')])
    xmas_t = np.array([n[0] for n in C.tunes('xmas')])
    gift_p = mid - 15
    king_p = mid + 30
    may_p = S.at('Porch Left', 0.88)
    clawL, clawR = S.at('Porch Left', 0.45), S.at('Porch Right', 0.5)
    xcols = np.array([RED, GREEN, GOLD, BLUE])[(G.pi // 4) % 4] * (G.pi % 4 != 3)[:, None]
    gulp = 7                                                # the citizen who swallows the ornament

    for f in range(F):
        t = f * DT
        beat = pulse(t, town_beats, 0.15)
        up = smoothstep(0, 2.0, t)
        lvt = up * (0.85 + 0.15 * beat)
        fr = S.town(t, lv=lvt, mist=0.0)
        # the town's green mist, drawn here on a lattice offset well clear of zero: Stage.town's drift wraps its
        # lattice when d - 40 t goes negative, which shows as a seam later in a long scene
        m = 0.5 + 0.5 * drift(7, d - 40 * t + 1e5, 180.0)
        fr += light(SLIME, 0.6 * lvt * 0.6 * np.clip(m - 0.3, 0, 1) * 1.4)
        fr += light(VIOLET, 0.12 * up * S.porch)

        # the crowd's mood: lean in when shown something, flinch, scatter at the bear, roar for the claws
        lean = sum(smoothstep(M[g], M[g] + 1.0, t) * (1 - smoothstep(M[f'r{i}'], M[f'r{i}'] + 0.5, t))
                   for i, g in enumerate(GIFTS))
        flinch = pulse(t, react_beats[0], 0.2) + 0.6 * pulse(t, react_beats[1][::2], 0.25)
        scatter = smoothstep(M['r3'], M['r3'] + 1.2, t) * (1 - smoothstep(M['claws'], M['claws'] + 3.0, t))
        joy = smoothstep(M['claws'], M['claws'] + 2.0, t)
        bounce = joy * pulse(t, town_beats, 0.18)
        shift = cout * (-18 * lean + 25 * flinch + 320 * scatter - 12 * bounce * np.sin(cp))
        pos = cp + shift
        here = smoothstep(carr, carr + 0.25, t)
        if M['ornament'] <= t:                              # the gulper slides up to the stage, and back
            g_go = smoothstep(M['r2'], M['r2'] + 0.8, t) * (1 - smoothstep(M['r2'] + 2.5, M['teddy'], t))
            pos[gulp] = pos[gulp] + (gift_p - 30 - pos[gulp]) * g_go
        lv = here * (0.75 + 0.5 * bounce + 0.4 * flinch) * (1 - 0.3 * scatter)
        col = ccol * (1 - 0.6 * min(1.0, flinch + scatter))
        col = col + ICE * 0.6 * min(1.0, flinch + scatter)
        W = perc(lv[:, None] * np.exp(-((d[None, :] - pos[:, None]) / 5.0) ** 2))
        fr = fr * (1 - 0.7 * np.clip(W.sum(0), 0, 1))[:, None] + W.T @ col
        fr += S.burst([(carr[k], 0.5, cp[k]) for k in range(len(cp))], t, seed=12, n=3, colors=(PUMPKIN,), reach=0.15)

        # the stage: the gift being shown, sparkling with the Christmas tune
        for j in np.flatnonzero((wonder_t <= t) & (wonder_t > t - 0.6)):
            a = t - wonder_t[j]
            fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * S.blob(gift_p + 40 * np.sin(wonder_t[j] * 9), 10))
        for i, g in enumerate(GIFTS):
            t0, t1 = M[g], (M[GIFTS[i + 1]] if i < 3 else M['claws'])
            if not t0 <= t < t1:
                continue
            a = t - t0
            show = smoothstep(0, 0.4, a)
            fr += light(GOLD, 0.5 * np.exp(-a / 0.6) * S.run['Porch Front'])
            fr += light(WARM, 0.25 * show * S.blob(gift_p, 70))
            rb = M[f'r{i}']
            if g == 'present':
                snap = pulse(t, react_beats[0], 0.12) if t >= rb else 0.0
                jaw = 2 + int(3 * (1 - min(1.0, snap)))
                fr = S.sprite(fr, gift_p, [(jaw, RED, 1.0), (jaw - 1, RED, 0.9), (0, GOLD, 1.0), (1 - jaw, RED, 0.9),
                                           (-jaw, RED, 1.0)], show)
                if t >= rb:
                    fr += light(WHITE, 0.8 * snap * S.blob(gift_p, 25))
                    fr += light(RED, 0.6 * snap * S.run['Porch Front'])
            elif g == 'stocking':
                fr = S.sprite(fr, gift_p, [(3, WHITE, 1.0), (2, WHITE, 0.9), (1, RED, 1.0), (0, RED, 1.0),
                                           (-1, RED, 1.0), (-2, RED, 1.0), (-3, RED, 0.9)], show)
                if t >= rb:                                 # something lumpy in the toe: a foot?
                    lump = smoothstep(rb, rb + 0.6, t)
                    fr = S.sprite(fr, gift_p - 3 * 4.9, [(0, LUMP, 1.0), (-1, LUMP, 0.8)], lump)
                    fr += light(ICE, 0.6 * pulse(t, [rb + 0.6], 0.4) * (S.wings | S.porch))
            elif g == 'ornament':
                eaten = smoothstep(rb + 1.6, rb + 1.8, t)
                glint = 0.75 + 0.25 * np.sin(11 * t)
                fr = S.sprite(fr, gift_p, [(2, GOLD, 0.7), (1, GOLD, 1.0), (0, WHITE, glint), (-1, GOLD, 1.0),
                                           (-2, GOLD, 0.7), (3, RED, 0.6)], show * (1 - eaten))
                if t >= rb + 1.6:
                    a2 = t - rb - 1.6
                    fr += light(SLIME, 0.9 * np.exp(-a2 / 0.4) * S.blob(gift_p - 20, 40))
            elif g == 'teddy':
                fr = S.sprite(fr, gift_p, [(2, TEDDY, 0.9), (1, None, 0), (0, TEDDY, 1.0), (-1, None, 0),
                                           (-2, TEDDY, 0.9), (-3, TEDDY, 0.8), (-4, TEDDY, 0.7)], show)
                if t >= rb:                                 # the shriek: white flashes all down both wings
                    sh = pulse(t, react_beats[3][:4], 0.15)
                    fr += light(ICE, 0.6 * sh * (S.wings | S.run['Side']))

        # the king of Christmas, as they imagine him: a red body swelling over the porch, two lobster claws
        vis = smoothstep(M['claws'], M['claws'] + 2.5, t) * (1 - smoothstep(M['collide'], M['collide'] + 1.5, t))
        vis = max(vis, smoothstep(M['roar'] - 0.5, M['roar'] + 0.5, t))
        if vis > 0:
            snap = pulse(t, claw_downs, 0.18)
            fr = fr * (1 - 0.5 * vis * S.porch)[:, None]
            fr += light(RED, (0.55 + 0.25 * snap) * vis * S.run['Porch Front'] * (0.85 + 0.15 * np.sin(d / 25 + 3 * t)))
            fr += light(FLAME, 0.4 * vis * S.blob(mid, 120))
            for e in (-35, 35):
                fr = S.sprite(fr, mid + e, [(0, WHITE, 1.0)], vis)
            for c in (clawL, clawR):
                gap = 8 + 60 * (1 - min(1.0, snap))
                jaws = (smoothstep(gap / 2 + 70, gap / 2 + 60, np.abs(d - c)) *
                        smoothstep(gap / 2 - 4, gap / 2 + 4, np.abs(d - c)))
                fr += light(RED, 1.0 * vis * jaws)
                fr += light(WHITE, 0.8 * vis * snap * S.blob(c, 15))
            fr += light(ORANGE, 0.55 * vis * joy * snap * (S.wings | S.run['Side']))      # the town roars

        # the collision: march on the left in orange and green, Christmas on the right in bulbs, the border sloshing
        if M['collide'] <= t < M['roar'] + 0.5:
            a = t - M['collide']
            span = M['roar'] - M['collide']
            border = mid + 700 * np.sin(2 * np.pi * a / 5.0) * (1 - smoothstep(span - 4, span, a))
            mix = smoothstep(span - 4, span, a)
            left = smoothstep(border + 40, border - 40, d)
            lt = pulse(t, town_t, 0.25)
            xt = pulse(t, xmas_t, 0.2)
            towncol = PUMPKIN if int(a / 0.5) % 2 else SLIME
            fr += light(towncol, (0.35 + 0.4 * lt) * (left + mix * (1 - left)))
            fr = fr * (1 - 0.5 * (1 - left) * (1 - mix))[:, None]
            fr += xcols * perc((0.55 + 0.45 * xt) * ((1 - left) + mix * left))[:, None]
            fr += light(WHITE, 0.8 * np.exp(-((d - border) / 20) ** 2) * (1 - mix))

        # the roar: the whole house flashing orange and green on the beat; the last hit
        if M['roar'] <= t < M['hit']:
            c = PUMPKIN if int((t - M['roar']) / (60 / 132)) % 2 else SLIME
            fr += light(c, 0.5 * beat * np.ones(G.N))
        if t >= M['hit']:
            a = t - M['hit']
            fr += light(WHITE, 0.9 * np.exp(-a / 0.25) * np.ones(G.N))
            fr += S.burst([(M['hit'] + k * 0.12, 1.2, mid + (k - 2) * 300) for k in range(5)], t, seed=13, n=18,
                          colors=(PUMPKIN, SLIME, RED, WHITE))

        # the mayor by the stage: worried at every scare, beaming for the claws
        happy = keys(t, [(0, 1.0), (M['r0'], 1.0), (M['r0'] + 0.3, 0.0), (M['stocking'], 0.6), (M['r1'] + 0.5, 0.0),
                         (M['ornament'], 0.6), (M['r2'] + 1.6, 0.0), (M['teddy'], 0.5), (M['r3'] + 0.2, 0.0),
                         (M['claws'] + 2.0, 0.0), (M['claws'] + 4.0, 1.0)])
        fr = S.mayor(fr, may_p + 30 * scatter * -1, smoothstep(M['gather'], M['gather'] + 1, t), happy)

        # the king on the stage, presenting
        kp = king_p if t < M['claws'] else mid
        tell = pulse(t, downs, 0.3) * (M['claws'] <= t < M['collide'])
        fr = S.jack(fr, kp, up, facing=-1 if t < M['claws'] else 1, glow=0.35 + 0.4 * tell + 0.3 * joy * beat)
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def roar(B, t, seconds=1.2, pan=0.0, gain=1.0, seed=0):
    """A crowd cheering: a burst of voices (band-passed noise with a ragged swell) and a choir shout."""
    from pixelhome.audio import SR
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    env = np.clip(tt / 0.08, 0, 1) * np.exp(-tt / (0.45 * seconds))
    sig = B._noise(0, 250, 3200, seed or int(t * 1000), n=n) * env * B._wobble(n, 12, seed + 3, 0.6)
    B._sfx(sig, t, 0.5 * gain, pan)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.4)
    mid = S.pan(S.mid)
    parts = {
        ('gather', 'tune'): [('bassoons', 0, 2, 0.7), ('pizz', 12, -6, 0.4)],
        ('gather', 'bass'): [('basses pizz', 0, 0, 0.6), ('tuba', -12, -12, 0.35)],
        ('gather', 'chord'): [('pizz', 0, -8, 0.35)],
        'tune': [('celesta', 12, 0, 0.65), ('glock', 0, -8, 0.4)],
        'arp': [('harp', 0, -6, 0.4)],
        'pedal': [('violins', 12, -18, 0.25)],
        ('r0', 'tune'): [('bassoons', 0, 6, 0.7), ('muted horn', 0, 0, 0.5)],
        ('r1', 'tune'): [('clarinets', 0, 4, 0.6), ('muted horn', 0, 0, 0.5)],
        ('r2', 'tune'): [('buzz trombone', 0, 10, 0.9), ('bassoons', 0, 0, 0.5)],
        ('r3', 'tune'): [('xylo', 0, 4, 0.6), ('violins', 0, 4, 0.55), ('piccolo', 0, -8, 0.3)],
        ('claws', 'tune'): [('tuba', 0, 12, 0.8), ('trombones', 12, 6, 0.6), ('cellos', 12, 0, 0.5)],
        ('claws', 'hold'): [('trombones', 0, -10, 0.4), ('cellos trem', 12, -6, 0.4)],
        ('claws', 'pedal'): [('basses', 12, 0, 0.6), ('timpani roll', 0, -20, 0.3)],
        ('collide', 'tune'): [('tuba', -12, 8, 0.75), ('buzz trombone', 0, 6, 0.7), ('bassoons', 0, 0, 0.5)],
        ('collide', 'bass'): [('tuba', -12, 0, 0.6), ('basses pizz', 0, -4, 0.5)],
        ('collide', 'chord'): [('pizz', 0, -4, 0.45)],
        ('xmas', 'tune'): [('glock', 0, 0, 0.6), ('piccolo', 0, -6, 0.4), ('celesta', 12, -6, 0.5)],
        ('roar', 'tune'): [('trumpets', 0, 8, 0.7), ('trombones', 0, 6, 0.65), ('horns', 0, 4, 0.6),
                           ('choir', 0, 4, 0.75), ('xylo', 12, 0, 0.4)],
        ('roar', 'bass'): [('tuba', -12, 8, 0.8), ('basses', 0, 0, 0.5), ('timpani', 0, 0, 0.35)],
        ('roar', 'chord'): [('horns', 0, -6, 0.5), ('violins', 12, -6, 0.4)],
    }

    B.perform([e for e in C.events if e[5] != 'xmas'], parts,
              pan=lambda t, m, role: -0.6 if (M['collide'] <= t < M['roar'] and role == 'tune') else None)
    B.perform([e for e in C.events if e[5] == 'xmas'], parts, pan=lambda t, m, role: 0.6)
    B.effects([(0, -4), (M['present'], -2), (M['claws'], 0), (M['collide'], -6), (M['roar'], -2), (M['hit'], 0)])
    # the meeting bell, the crowd murmuring in
    B.hit('gong', 0.3, 100, pitch=-2, gain=0.5, pan=mid)
    B.hit('gong', 1.3, 90, pitch=-2, gain=0.4, pan=mid)
    for k, m in enumerate((48, 52, 55, 51, 46, 53)):
        B.play('choir', m, M['gather'] + 0.8 * k, 1.6, 60, 0.7 * np.sin(k * 2.1), 0.22)
    # each gift's reveal: sleigh bells; then what the crowd hears in it
    for i, g in enumerate(GIFTS):
        B.sleigh_bells(M[g], M[f'r{i}'], beat=0.18, v=80, gain=0.45, pan=mid)
    rb = [b[0] for b in C.beats if b[2] == 'r0']
    for k, tb in enumerate(rb):                             # the present snaps at them
        B.hit('slapstick', tb, 110, gain=0.6, pan=mid)
        B.hit('anvil', tb, 80, gain=0.2, pan=mid)
    B.play('choir', 76, M['r0'] + 0.05, 0.4, 90, gain=0.35)
    B.play('choir', 79, M['r0'] + 0.05, 0.4, 90, gain=0.35)
    t1 = M['r1']                                            # the stocking: a foot?
    B.hit('scrape', t1 + 0.5, 100, gain=0.5, pan=mid)
    B.play('choir', 72, t1 + 0.6, 0.8, 90, gain=0.4)
    B.play('choir', 77, t1 + 0.6, 0.8, 90, gain=0.4)
    B.play('muted horn', 55, t1 + 1.8, 0.4, 100, mid, 0.7)
    B.play('muted horn', 53, t1 + 2.2, 0.8, 96, mid, 0.7)
    t2 = M['r2'] + 1.6                                      # the ornament: crunch, gulp, burp
    B.hit('slapstick', t2, 120, gain=0.7, pan=mid - 0.1)
    B.hit('glass', t2 + 0.05, 100, gain=0.5, pan=mid - 0.1)
    for k, m in enumerate((45, 43, 40, 36)):
        B.play('tuba', m, t2 + 0.4 + 0.12 * k, 0.15, 100, mid, 0.6)
    B.play('buzz trombone', 40, t2 + 1.2, 0.5, 110, mid, 0.9)
    t3 = M['r3']                                            # the teddy bear: the whole town shrieks and runs
    for k, pp in enumerate((-0.7, 0.6, -0.3, 0.85, 0.2)):
        B.scream(t3 + 0.12 * k, pan=pp, gain=0.8, high=0.6 + 0.2 * k)
    B.whoosh(t3 + 0.3, 1.0, up=True, pan=-0.6, gain=0.5)
    B.whoosh(t3 + 0.4, 1.0, up=True, pan=0.6, gain=0.5)
    B.hit('ratchet', t3 + 0.2, 100, gain=0.4)
    # the claws: a clank on every snap and a roar from the crowd once they are back
    claws = C.downbeats('claws') + C.downbeats('roar')
    for k, tb in enumerate(claws):
        B.clash(tb, pan=0.5 * (-1) ** k, v=110, gain=0.6)
        if tb >= M['claws'] + 2.0:
            roar(B, tb + 0.05, 1.0, pan=0.7 * (-1) ** (k + 1), gain=0.8, seed=k + 1)
    B.hit('timpani roll', M['claws'], 100, pitch=-5, gain=0.45, pan=mid)
    B.hit('cymbal swell', M['collide'] - 1.6, 100, gain=0.45)
    # the collision: sleigh bells on the Christmas side, snare on the town's
    B.sleigh_bells(M['collide'], M['roar'], beat=0.333, v=86, gain=0.5, pan=0.6)
    t = M['collide']
    while t < M['roar']:
        B.hit('snare', t + 0.25, 70, gain=0.25, pan=-0.6)
        t += 0.5
    # the town on board: a crash, a roar, the last hit
    B.hit('crash', M['roar'], 116, gain=0.5)
    roar(B, M['roar'], 2.0, pan=0.0, gain=1.0, seed=50)
    roar(B, M['hit'], 2.4, pan=0.0, gain=1.2, seed=51)
    for m in (52, 59, 64, 67):
        B.play('choir', m, M['hit'], 2.0, 110, gain=0.5)
        B.play('trombones', m - 12, M['hit'], 1.6, 116, gain=0.5)
    B.play('tuba', 28 + 12, M['hit'], 1.6, 116, gain=0.6)
    B.hit('crash', M['hit'], 124, gain=0.6)
    B.hit('bass drum', M['hit'], 124, gain=0.7)
    B.hit('timpani', M['hit'], 124, pitch=-5, gain=0.5)
    B.finish()
