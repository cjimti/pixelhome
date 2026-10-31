"""The Doors in the Trees: at dawn the Pumpkin King wanders into a grove where seven trees have doors, and the last
one pulls him in.

A pale grove at dawn on every run, grey-green trunks against a cool sky. The king walks in from the free end of
Right and slowly round the whole front of the house to the far end of Left, his lament wandering on a clarinet
over a harp. As he comes to each tree its door lights in a flood of its own colours over its run, with a sound of
its own, then settles to a glow: a beating pink-red heart (a sweet violin sigh), a pastel egg (a flute's little
run), a green shamrock (a jig on the flute and a tambourine), a brown and orange turkey fanning its tail (a
gobbling trombone), a red, white and blue firework that bursts in sparks (a whistle and a bang), and a
jack-o'-lantern (his own town's march on a bassoon). He passed a dark trunk in the middle of the porch without a
look; now, with every door glowing in a ring round the house, it wakes behind him: a Christmas tree, green with a
red ornament and a gold star, twinkling with snow to a celesta and sleigh bells. He hurries back to it and opens
it. The door splits in two on a blaze of white, and a swirl of snow and coloured light rushes out over the whole
house, red, green, gold and blue bands pouring in towards the porch; he spins in the middle of it and is sucked
in, and everything tumbles after him down into the dark.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events and the
door times, so every door lights on its own sound."""
import numpy as np
from pixelhome.audio import note, slide
from pixelhome.fx import DT, nframes, light, perc, smoothstep, keys, hexc, Flicker
from pixelhome.nightmare import (drift, Chart, Band, Stage, pulse, RED, PINK, GREEN, GOLD, ORANGE, PUMPKIN, FLAME, WHITE,
                                 BLUE, ICE, MOON)

CODE = 'NM04'
TITLE = 'The Doors in the Trees'
KIND = 'show'
DESCRIPTION = ('A ring of trees with doors lights up one by one round the house as Jack passes: a heart, an egg, a '
    "shamrock, a turkey, a firework, a jack-o'-lantern. Then the Christmas tree on the porch opens.")
VOICEOVER = 'Lost in the woods at dawn, Jack finds a circle of trees. Every one of them has a door.'

SAGE = hexc('#40a070')
SKY = hexc('#2858b0')
BARK = hexc('#40302a')
BROWN = hexc('#a04810')
LAV = hexc('#b080ff')
MINT = hexc('#60ffb0')
LEMON = hexc('#fff060')
BLUSH = hexc('#ff80c0')
NAVY = hexc('#1030ff')
PINE = hexc('#00a018')
PEACH = hexc('#ffb090')

# the doors, in the order he comes to them: (name, run, where along it, pixels, flood colour)
DOORS = [
    ('heart', 'Right', 0.72, [(3, PINK, 0.6), (2, RED, 1.0), (1, RED, 1.0), (0, PINK, 0.9), (-1, RED, 1.0),
                              (-2, RED, 1.0), (-3, PINK, 0.6)], RED),
    ('egg', 'Right', 0.28, [(3, LAV, 0.9), (2, MINT, 0.9), (1, LEMON, 0.9), (0, BLUSH, 1.0), (-1, LEMON, 0.9),
                            (-2, MINT, 0.9), (-3, LAV, 0.9)], BLUSH),
    ('shamrock', 'Porch Right', 0.5, [(3, GREEN, 0.7), (2, GREEN, 1.0), (1, None, 0), (0, GREEN, 1.0),
                                      (-1, None, 0), (-2, GREEN, 1.0), (-3, GREEN, 0.7)], GREEN),
    ('turkey', 'Porch Left', 0.5, [(3, RED, 0.9), (2, ORANGE, 1.0), (1, BROWN, 1.0), (0, GOLD, 1.0),
                                   (-1, BROWN, 1.0), (-2, ORANGE, 1.0), (-3, RED, 0.9)], BROWN),
    ('firework', 'Left', 0.72, [(3, NAVY, 1.0), (2, WHITE, 0.9), (1, RED, 1.0), (0, WHITE, 1.0), (-1, RED, 1.0),
                                (-2, WHITE, 0.9), (-3, NAVY, 1.0)], NAVY),
    ('pumpkin', 'Left', 0.28, [(3, ORANGE, 1.0), (2, None, 0), (1, ORANGE, 1.0), (0, None, 0), (-1, ORANGE, 1.0),
                               (-2, None, 0), (-3, ORANGE, 1.0)], PUMPKIN),
]
TREE = [(4, GOLD, 1.0), (3, PINE, 0.7), (2, PINE, 0.9), (1, PINE, 1.0), (0, RED, 1.0), (-1, PINE, 1.0),
        (-2, PINE, 0.9), (-3, PINE, 0.7), (-4, BARK, 0.6)]


def compose():
    C = Chart()
    C.rest(3.0)                                             # dawn comes up on the grove
    C.mark('walk')
    C.play('king', style='arp', bars=(0, 16), bpm=84, tag='walk')       # he wanders round the ring of doors
    C.mark('turn')
    C.rest(1.0)
    C.mark('call')
    C.play('wonder', style='arp', bars=(0, 4), bpm=300, tag='call')     # the Christmas tree door wakes
    C.mark('open')
    C.rest(1.6)
    C.mark('swirl')
    C.rest(4.5)
    C.mark('fall')
    C.rest(4.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def walk_ends(S):
    return S.L + 20, S.at('Left', 0.12)


def king_at(S, t):
    a, b = walk_ends(S)
    if t < M['turn']:
        u = np.clip((t - M['walk']) / (M['turn'] - M['walk']), 0, 1)
        return float(a + (b - a) * u), -1
    if t < M['open']:
        return float(keys(t, [(M['turn'] + 0.6, b), (M['open'] - 0.2, S.mid - 25)])), 1
    return S.mid - 25, 1


def door_times(S):
    """When he comes to each door (a little before he reaches it)."""
    a, b = walk_ends(S)
    out = []
    for name, run, u, px, col in DOORS:
        p = S.at(run, u)
        out.append(M['walk'] + (a - p) / (a - b) * (M['turn'] - M['walk']) - 0.4)
    return out


def grove(S, t, lv, off):
    """The grove at dawn: a cool pale sky between grey-green trunks, mist drifting."""
    d = S.d
    m = 0.5 + 0.5 * drift(14, d - 18 * t + off + 1e5, 150.0)
    trunk = np.exp(-(((d + 4 * np.sin(0.5 * t + d / 250)) % 90 - 45) / 9) ** 2)
    fr = light(SKY, 0.36 * lv * (0.4 + 0.6 * m) * (1 - trunk))
    fr += light(PEACH, 0.32 * lv * np.clip(m - 0.5, 0, 1) * 2 * (1 - trunk))
    fr += light(SAGE, 0.3 * lv * trunk)
    return fr


def render(G, seed=4):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    off = rng.uniform(0, 1000)
    times = door_times(S)
    where = [S.at(run, u) for _, run, u, _, _ in DOORS]
    call = np.array([n[0] for n in C.tunes('call')])
    fl = Flicker(rng, G.N, 0.5, 4.0)
    snow_ph, snow_rate = rng.uniform(0, 1, G.N), rng.uniform(0.6, 1.4, G.N)
    bands = np.array([RED, GREEN, GOLD, BLUE])
    tree_p = mid

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 3.0, t)
        swirl = smoothstep(M['swirl'] - 0.3, M['swirl'] + 1.5, t)
        fall = smoothstep(M['fall'], D - 0.5, t)
        world = up * (1 - swirl)
        fr = grove(S, t, world, off) if world > 0 else np.zeros((G.N, 3))

        # the doors: each lights in a flood of its colours as he comes to it, then glows on
        for i, (name, run, u, px, col) in enumerate(DOORS):
            a = t - times[i]
            if a < 0:
                fr = S.sprite(fr, where[i], [(o, BARK, 0.5) for o, _, _ in px], 0.6 * up)
                continue
            glow = (0.75 + 0.25 * np.exp(-a / 1.5)) * (1 - swirl)
            if name == 'heart':
                glow *= 0.85 + 0.15 * pulse(t % 1.0, [0.0, 0.25], 0.12)
            if name == 'pumpkin':
                glow *= 0.85 + 0.15 * fl(t)[S.k(where[i])]
            if a < 2.5:
                fr += light(col, 0.85 * np.exp(-a / 0.8) * S.run[run] * (1 - swirl))
                fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * S.blob(where[i], 40))
            fr = fr * (1 - 0.6 * glow * S.blob(where[i], 110))[:, None]
            fr += light(col, 1.0 * glow * S.blob(where[i], 110))
            fr += light(col, 0.45 * glow * S.run[run])
            fr = S.sprite(fr, where[i], px, glow)
            if name == 'firework':
                fr += S.burst([(times[i] + 0.3, 1.0, where[i])], t, seed=7, n=18, colors=(RED, WHITE, NAVY))
            if name == 'turkey' and a < 3.0:                # he fans his tail: the door's colours spread and fold
                fan = np.sin(np.pi * np.clip(a / 1.5, 0, 1))
                fr += light(ORANGE, 0.6 * fan * np.exp(-((np.abs(d - where[i]) - 60 * fan) / 15) ** 2))

        # the Christmas tree door in the middle of the porch: a dark trunk, until it wakes and calls him
        wake = smoothstep(M['turn'] - 0.5, M['call'] + 0.5, t) * (1 - smoothstep(M['open'], M['open'] + 0.4, t))
        if t < M['open'] + 0.4:
            fr = S.sprite(fr, tree_p, [(o, BARK, 0.5) for o, _, _ in TREE], 0.6 * up * (1 - wake))
            if wake > 0:
                tw = pulse(t, call, 0.2)
                fr += light(PINE, (0.5 * wake + 0.25 * tw) * S.run['Porch Front'])
                fr += light(GOLD, 0.4 * tw * S.blob(tree_p, 60))
                ph = (snow_ph + snow_rate * t) % 1.0
                fr += light(WHITE, 0.9 * wake * np.exp(-((ph - 0.5) / 0.04) ** 2) * S.porch)
                fr = S.sprite(fr, tree_p, TREE, wake * (0.85 + 0.25 * tw))

        # he opens it: the door splits on a blaze of white
        if M['open'] <= t < M['swirl'] + 1.0:
            a = t - M['open']
            gap = int(min(6, 1 + a * 6))
            half_l = [(o - gap, c, v) for o, c, v in TREE if o < 0]
            half_r = [(o + gap, c, v) for o, c, v in TREE if o > 0]
            fade = 1 - smoothstep(M['swirl'], M['swirl'] + 0.8, t)
            fr += light(WHITE, 0.9 * smoothstep(0, 0.5, a) * S.blob(tree_p, 15 + 30 * a) * fade)
            fr += light(ICE, 0.5 * smoothstep(0.2, 1.2, a) * S.porch * fade)
            fr = S.sprite(fr, tree_p, half_l + half_r, fade)

        # the swirl: snow and coloured bands pour in over the whole house towards the porch
        if swirl > 0:
            r = np.abs(d - mid)
            reach = 2700 * (1 - fall) + 10
            inside = smoothstep(reach + 60, reach - 60, r)
            phase = r / 110.0 + 3.5 * (t - M['swirl']) * (1 + fall)
            idx = np.floor(phase).astype(int) % 4
            band = 0.5 + 0.5 * np.cos(2 * np.pi * phase)
            lv = swirl * (1 - fall) ** 1.5
            fr += perc(0.9 * lv * band * inside)[:, None] * bands[idx]
            ph = (snow_ph + 2.5 * snow_rate * t) % 1.0
            fr += light(WHITE, 0.95 * lv * np.exp(-((ph - 0.5) / 0.05) ** 2) * inside)
            fr += light(WHITE, 0.6 * swirl * (1 - fall) * S.blob(mid, 60 + 100 * (1 - fall)))

        # Jack: walks round, hurries back, spins in the swirl and is sucked in
        kp, kf = king_at(S, t)
        if t >= M['swirl']:
            a = t - M['swirl']
            kp = mid - 25 * (1 - smoothstep(0, 3.0, a)) + 12 * np.sin(9 * a)
            kf = 1 if int(a * 6) % 2 else -1
        klvl = up * (1 - smoothstep(M['fall'] - 0.5, M['fall'] + 1.5, t))
        if -15 < kp < S.L + 15:
            fr = S.jack(fr, float(kp), klvl, facing=kf, glow=0.3 + 0.5 * swirl)
        out[f] = fr * float(1 - smoothstep(D - 1.2, D, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=3.9)
    times = door_times(S)
    pans = [S.pan(S.at(run, u)) for _, run, u, _, _ in DOORS]
    parts = {
        ('walk', 'tune'): [('clarinets', 0, 4, 0.75)],
        ('walk', 'arp'): [('harp', 0, -6, 0.45)],
        ('walk', 'pedal'): [('ghost', 12, -10, 0.45), ('cellos', 0, -14, 0.35)],
        ('call', 'tune'): [('celesta', 12, 0, 0.7), ('glock', 0, -10, 0.45)],
        ('call', 'arp'): [('harp', 0, -8, 0.4)],
        ('call', 'pedal'): [('violins', 12, -18, 0.3), ('cellos', 0, -14, 0.35)],
    }
    B.perform(C.events, parts, pan=lambda t, m, role: 0.6 * S.pan(king_at(S, t)[0]) if role == 'tune' else None)
    # dawn in the grove: birds and a harp
    for k, (tb, m) in enumerate([(0.6, 79), (0.75, 81), (1.6, 76), (1.7, 79), (2.4, 83)]):
        B.play('flutes', m, tb, 0.1, 70, 0.7 - 0.5 * k / 4, 0.35)
    B.effects([(0, -6), (M['walk'], -4), (M['open'], 0), (M['swirl'], 3), (M['fall'] + 1, 0), (D, -8)])
    # each door's own sound as it lights
    for (name, *_), t, pp in zip(DOORS, times, pans):
        if name == 'heart':
            B.play('violins', note('E5'), t, 0.6, 90, pp, 0.6)
            B.play('violins', note('C5'), t + 0.6, 1.2, 84, pp, 0.55)
            for k in range(3):
                B.hit('timpani', t + k, 70, pitch=-8, gain=0.3, pan=pp)
                B.hit('timpani', t + k + 0.25, 60, pitch=-8, gain=0.25, pan=pp)
        elif name == 'egg':
            for k, m in enumerate(['C5', 'D5', 'E5', 'G5', 'E5', 'C6']):
                B.play('flutes', note(m), t + 0.11 * k, 0.12, 84, pp, 0.5)
            B.hit('wood', t + 0.8, 90, gain=0.4, pan=pp)
            B.hit('wood', t + 0.95, 80, gain=0.35, pan=pp)
        elif name == 'shamrock':
            for k, m in enumerate(['G4', 'A4', 'B4', 'D5', 'B4', 'G4', 'A4', 'B4', 'A4']):
                B.play('flutes', note(m), t + 0.15 * k, 0.14, 88, pp, 0.5)
                B.hit('tambourine', t + 0.15 * k, 70 + 20 * (k % 3 == 0), gain=0.3, pan=pp)
        elif name == 'turkey':
            for k in range(6):
                B.play('trombones', note('E3') + (2 if k % 2 else 0), t + 0.09 * k, 0.1, 110, pp, 0.8)
                B.play('buzz trombone', note('E3') + (2 if k % 2 else 0), t + 0.09 * k, 0.3, 110, pp, 1.0)
            B.hit('guiro', t + 0.6, 90, gain=0.4, pan=pp)
        elif name == 'firework':
            B.M.add('fx', slide(0.0, 0.3, 900, 2600, 0.35, amp=0.5), t, 0.3, pp)
            B.boom(t + 0.3, pan=pp, gain=0.6)
            B.hit('crash', t + 0.3, 110, gain=0.4, pan=pp)
            B.hit('snare roll', t + 0.35, 90, gain=0.3, pan=pp)
        elif name == 'pumpkin':
            for k, (dt, dur, m) in enumerate([(0, .4, 'E4'), (.4, .2, 'E4'), (.6, .2, 'F#4'), (.8, .4, 'G4'), (1.2, .4, 'B4')]):
                B.play('bassoons', note(m), t + dt, dur, 96, pp, 0.7)
            B.hit('gong', t, 80, gain=0.25, pan=pp)
    # the Christmas tree door: sleigh bells; he opens it
    B.sleigh_bells(M['call'], M['open'], beat=0.2, pan=0.0, v=80, gain=0.8)
    B.hit('gong scrape', M['open'], 90, gain=0.5)
    B.play('cellos', 40, M['open'], 1.4, 80, 0.0, 0.5)
    B.hit('crash', M['open'] + 0.5, 100, gain=0.45)
    for m in (55, 59, 62, 67):
        B.play('choir', m, M['open'] + 0.4, 5.5, 90, gain=0.5)
        B.play('violins trem', m + 12, M['open'] + 0.6, 5.0, 80, gain=0.35)
    # the swirl: wind and whooshes, the bells shaken hard; then everything tumbles down into the dark
    B.wind(M['open'] + 0.8, M['fall'] + 3.0, level=lambda tt: np.clip(1.1 - 0.25 * np.maximum(tt - M['fall'], 0), 0, 1),
           pan=0.0, seed=41)
    B.sleigh_bells(M['swirl'], M['fall'], beat=0.1, pan=lambda tt: 0.6 * np.sin(5 * tt), v=100, gain=0.7)
    for k in range(4):
        B.whoosh(M['swirl'] + k * 1.1, 1.2, up=True, pan=0.6 * (-1) ** k, gain=0.6)
    B.hit('cymbal swell', M['swirl'] - 0.5, 100, gain=0.5)
    B.hit('crash', M['swirl'] + 1.0, 116, gain=0.5)
    B.whoosh(M['fall'], 3.5, up=False, pan=0.0, gain=0.9)
    for k, m in enumerate([88, 84, 81, 79, 76, 72, 69, 67, 64, 60, 57, 55, 52, 48, 45]):
        B.play('harp', m, M['fall'] + 0.12 * k, 0.8, 92 - 2 * k, 0.4 * np.sin(3 * k), 0.55)
        B.play('glock', m, M['fall'] + 0.2 + 0.18 * k, 0.5, 80 - 3 * k, -0.3, 0.3 if m < 85 else 0.0)
    B.hit('timpani roll', M['fall'] + 0.5, 90, pitch=-5, gain=0.4)
    B.play('basses', 33, M['fall'] + 0.5, 3.5, 90, 0.0, 0.5)
    B.finish()
