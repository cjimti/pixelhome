"""Three Little Troublemakers: the Pumpkin King sends for the three troublemakers, and in their walking bathtub
they scheme, each trying to outdo the others, how to bring him the man in red.

Halloween Town glows violet. On Porch Front the king summons them to his sly theme in A minor on muted horn and
bassoon, and over the porch flashes the one he wants: Santa, red and white, a red glow on the whole porch. The
three pop up one by one, each in a flood of its colour on its run, cackling: the devil (red) on Porch Left, the
witch (violet and green) on Porch Front, the skeleton (white and green) on Porch Right. Their walking bathtub
clatters up to collect them and stomps off down Porch Right to their treehouse out on the Right wing, its claw
feet clacking. There they scheme to their gleeful patter in C minor, a verse each, each idea bigger than the last
and the key going up a step each time. The devil's: a cage; red bars slam down one per bar over Porch Front around
Santa, the left wing flashing red. The witch's: a trap; two violet jaws with green teeth ratchet in from both ends
of the house and SNAP shut over the porch. The skeleton's: take him to the boogeyman; the boogeyman's glowing
sack rises over the porch, green bugs crawling over the whole house, and Santa is dragged into him. Then they
squabble: the three bash about over the tub, sparks flying, the house flashing red, violet and white in turn.
They agree, and to the patter on the whole band, red, violet and white bands race along the roof to the free
end of Right, and the tub stomps off out of it with all three aboard, a last burst behind them.

compose() lays the music end to end: render() and score() read its events and marks."""
import numpy as np
from pixelhome.audio import SR
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, FLAME, SLIME, VIOLET, DUSK, MOON,
                                 BONE, WHITE, GOLD, RED, BUG, BURLAP, WARM)

CODE = 'NM09'
TITLE = 'Three Little Troublemakers'
KIND = 'show'
DESCRIPTION = ('The king sends for the devil, the witch and the skeleton. In their walking bathtub they each '
               'scheme bigger: red cage bars slam down, giant jaws snap shut, the boogeyman rises over the porch.')
VOICEOVER = ('The Pumpkin King needed someone sneaky for a very special job. '
             'He sent for the three worst troublemakers in town.')

DEVIL, WITCH, SKEL = RED, VIOLET, BONE
MASKS = [[(1, RED, 1.0), (0, RED, 0.85), (-1, FLAME, 0.6)],
         [(1, VIOLET, 1.0), (0, SLIME, 0.7), (-1, VIOLET, 0.6)],
         [(1, BONE, 1.0), (0, None, 0), (-1, SLIME, 0.6)]]
GLOW = [RED, VIOLET, MOON]
VERSES = ('devil', 'witch', 'skeleton')


def compose():
    C = Chart()
    C.rest(2.0)
    C.mark('summon')
    C.play('king', style='waltz', bars=(0, 4), bpm=120, tag='summon')           # the king sends for them
    C.mark('pop')
    C.play('trio', style='gallop', bars=(0, 4), bpm=360, tag='pop')             # one, two, three
    C.mark('tub')
    C.play('trio', style='gallop', bars=(4, 8), bpm=360, tag='tub')             # the bathtub walks them home
    for i, v in enumerate(VERSES):                                              # each idea bigger, a step higher
        C.mark(v)
        C.play('trio', style='gallop', bpm=360 + 10 * i, transpose=2 * i, tag=v)
    C.mark('squabble')
    C.play('trio', style='drive', bars=(0, 4), bpm=420, transpose=5, tag='squabble')
    C.play('trio', style='drive', bars=(0, 4), bpm=420, transpose=5, tag='squabble')
    C.mark('finale')
    C.play('trio', style='gallop', bpm=400, transpose=5, tag='finale')
    C.mark('out')
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
SUM_DB = C.downbeats('summon')
T_SANTA = SUM_DB[1]
T_POPS = C.downbeats('pop')[:3]
T_ALL = C.downbeats('pop')[3]
DB = {v: C.downbeats(v) for v in VERSES}
T_SNAP = DB['witch'][-1] + 0.5
T_LOCK = DB['devil'][-1] + 0.5
SQ_DB = C.downbeats('squabble')
SQ_HITS = sorted(SQ_DB + [t + (SQ_DB[1] - SQ_DB[0]) / 2 for t in SQ_DB])


def places(S):
    return dict(king=S.mid + 40, santa=S.mid, tree=S.at('Right', 0.6),
                pops=[S.at('Porch Left', 0.5), S.at('Porch Front', 0.22), S.at('Porch Right', 0.5)])


def tub_pos(S, P, t):
    """The walking bathtub: up to the porch, down Porch Right to the treehouse, and at the end out the free end."""
    if t < M['tub']:
        return P['pops'][2]
    if t < M['devil']:
        return P['pops'][2] + (P['tree'] - P['pops'][2]) * smoothstep(M['tub'], M['devil'] - 0.2, t)
    if t < M['out'] - 3.0:
        return P['tree']
    return P['tree'] + (S.L + 120 - P['tree']) * smoothstep(M['out'] - 3.0, M['out'] + 0.6, t)


def tub(S, fr, p, t, walking):
    """A white enamel bathtub, gold claw feet flickering as it walks."""
    step = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 3 * t)) if walking else 0.5
    px = [(4, GOLD, 0.4 + 0.5 * step), (3, BONE, 0.75)] + [(o, WHITE, 0.5) for o in range(2, -12, -1)] + \
         [(-12, BONE, 0.75), (-13, GOLD, 0.9 - 0.5 * step)]
    return S.sprite(fr, p, px, 1.0, -1)


def render(G, seed=9):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    P = places(S)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    beats = np.array([b[0] for b in C.beats])
    downs = np.array(C.downbeats())
    left = S.run['Side'] | S.run['Left']
    bugs_ph = rng.uniform(0, 1, G.N)
    bugs_on = rng.random(G.N) < 0.35
    sq_who = [i % 3 for i in range(len(SQ_HITS))]

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.8, t)
        dn = pulse(t, downs, 0.25)
        fr = S.town(t, lv=up, mist=0.8) + light(DUSK, 0.25 * up * np.ones(G.N))
        pt = tub_pos(S, P, t)

        # the summons: the king on Porch Front, and over the porch, the man in red
        if t < M['tub'] + 1.0:
            kl = up * smoothstep(M['tub'] + 1.0, M['tub'], t)
            fr = S.jack(fr, P['king'], kl, facing=-1, glow=0.4)
            fr += light(PUMPKIN, 0.4 * kl * S.run['Porch Front'] * (0.8 + 0.2 * dn))
        if T_SANTA <= t < M['pop']:
            a = t - T_SANTA
            s = smoothstep(0, 0.3, a) * smoothstep(M['pop'], M['pop'] - 0.5, t)
            fr += light(WHITE, 0.8 * np.exp(-a / 0.15) * S.porch)
            fr += light(RED, 0.6 * s * S.porch)
            fr = S.santa(fr, P['santa'] - 60, s, facing=1)
            fr += light(RED, 0.4 * s * S.wings)
        # the three pop up, one by one, each in its own colour, then cackle together
        for i in range(3):
            if T_POPS[i] <= t < M['tub'] + 0.2:
                a = t - T_POPS[i]
                p = P['pops'][i]
                if t >= M['tub']:                               # hop into the tub
                    p = p + (pt - p) * smoothstep(M['tub'], M['tub'] + 0.2, t)
                fr += light(GLOW[i], 1.0 * np.exp(-a / 0.3) * S.run_at(P['pops'][i]) + 0.6 * S.blob(p, 50))
                cack = pulse(t, [T_ALL], 0.4)
                fr += light(GLOW[i], 0.5 * cack * S.run_at(P['pops'][i]))
                fr = S.sprite(fr, p, MASKS[i], 1.0 + 0.3 * cack, 1)

        # 1. the devil's cage: red bars slam down over Porch Front around Santa, one a bar
        if M['devil'] <= t < M['witch'] + 0.5:
            db = DB['devil']
            fade = smoothstep(M['witch'] + 0.5, M['witch'], t)
            fr = S.santa(fr, P['santa'] + 20, 0.9 * fade, facing=1)
            for k, tb in enumerate(db):
                if t >= tb:
                    a = t - tb
                    pb = P['santa'] + (k - 3.5) * 42
                    fr += light(RED, (0.9 + 0.6 * np.exp(-a / 0.15)) * fade * np.exp(-((d - pb) / 7) ** 2))
                    fr += light(WHITE, 0.8 * np.exp(-a / 0.1) * S.blob(pb, 20))
            fr += light(RED, (0.3 + 0.5 * dn) * left * fade)
            if t >= T_LOCK:
                fr += light(RED, 0.8 * np.exp(-(t - T_LOCK) / 0.3) * S.porch)
        # 2. the witch's trap: violet jaws with green teeth ratchet in from both ends and snap shut over the porch
        if M['witch'] <= t < M['skeleton'] + 0.6:
            db = DB['witch']
            k = np.searchsorted(db, t, side='right')
            u = (k - 1 + smoothstep(0, 0.2, t - db[max(k - 1, 0)])) / len(db)
            u = 1.0 if t >= T_SNAP else 0.9 * u
            gap = (1 - u) * (mid - 0) + 10
            jaw = np.abs(d - mid) > gap
            teeth = (G.pi % 6 == 0)
            fade = smoothstep(M['skeleton'] + 0.6, M['skeleton'], t)
            fr = fr * (1 - 0.7 * jaw[:, None])
            fr += light(VIOLET, 0.8 * jaw * fade) + light(SLIME, 1.0 * (jaw & teeth) * fade)
            fr += light(SLIME, 0.9 * np.exp(-((np.abs(d - mid) - gap) / 10) ** 2) * fade)
            if t < T_SNAP:
                fr = S.santa(fr, P['santa'] + 20, 0.9, facing=1)
            else:
                a = t - T_SNAP
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * np.ones(G.N))
                fr += light(SLIME, 0.7 * np.exp(-a / 0.4) * S.porch)
        # 3. the skeleton's idea: take him to the boogeyman; the sack rises, bugs everywhere, Santa dragged in
        if M['skeleton'] <= t < M['squabble'] + 0.6:
            db = DB['skeleton']
            a = t - M['skeleton']
            fade = smoothstep(M['squabble'] + 0.6, M['squabble'], t)
            rise = smoothstep(0, db[2] - M['skeleton'], a) * fade
            fr = fr * (1 - 0.3 * rise)
            fr += light(BURLAP, (0.45 + 0.3 * dn) * rise * S.porch)
            fr += light(SLIME, 0.35 * rise * (S.wings | S.run['Side']) * (0.6 + 0.4 * np.sin(2 * t + d / 60)))
            crawl = (bugs_ph + 0.8 * t + d / 400) % 1.0
            fr += light(BUG, 0.9 * rise * bugs_on * np.exp(-((crawl - 0.5) / 0.08) ** 2))
            for tb in db:
                if 0 <= t - tb < 1.2:
                    b = t - tb
                    fr += light(BUG, 0.7 * rise * np.exp(-b / 0.4) * np.exp(-((np.abs(d - mid) - 1100 * b) / 100) ** 2))
            pull = smoothstep(db[4], db[7], t)
            if pull < 1:
                fr = S.santa(fr, P['santa'] - 140 + 140 * pull, 0.9 * fade * (1 - pull), facing=1)
            fr = S.oogie(fr, mid, rise * (1 + 0.25 * dn), t, size=0.7 + 0.6 * rise)
        # 4. the squabble: they bash about over the tub, sparks flying, the house flashing their colours in turn
        if M['squabble'] <= t < M['finale']:
            j = int(np.searchsorted(SQ_HITS, t, side='right')) - 1
            if j >= 0:
                a = t - SQ_HITS[j]
                c = GLOW[sq_who[j]]
                fr += light(c, 0.75 * np.exp(-a / 0.25) * (S.wings | S.run['Side']))     # the porch keeps its sparks
            fr += S.burst([(th, 0.9, pt + 40 * np.sin(th * 7)) for th in SQ_HITS], t, seed=19, n=10, reach=0.5,
                          colors=(RED, VIOLET, WHITE, SLIME))
        # 5. the finale: bands of their colours racing to the free end of Right, a burst on every bar
        if t >= M['finale']:
            a = t - M['finale']
            lv = smoothstep(0, 0.6, a) * smoothstep(D, D - 1.2, t)
            band = ((d - 520 * a) / 70) % 3
            col = np.where((band < 1)[:, None], RED, np.where((band < 2)[:, None], VIOLET, BONE))
            fr = fr * (1 - 0.5 * lv)
            fr += light(col, lv * (0.55 + 0.35 * dn) * np.ones(G.N))
            fr += S.burst([(tb, 1.1, min(tub_pos(S, P, tb), L - 5)) for tb in C.downbeats('finale')] +
                          [(M['out'] + 0.4, 1.4, L - 5)], t, seed=23, n=24, reach=1.0, colors=(RED, VIOLET, WHITE))

        # the tub and its three passengers
        if t >= M['tub'] and pt < L + 60:
            walking = (M['tub'] <= t < M['devil']) or t >= M['out'] - 3.0
            fr = tub(S, fr, pt, t, walking)
            lead = -1
            for i, v in enumerate(VERSES):
                if M[v] <= t < (M[VERSES[i + 1]] if i < 2 else M['squabble']):
                    lead = i
            for i in range(3):
                po = pt - 2 * 4.0 - i * 5 * 4.0
                bounce = 0.75 + 0.25 * max(0.0, np.sin(2 * np.pi * (2 * t + i / 3)))
                if M['squabble'] <= t < M['finale']:
                    po += 35 * np.sin(2 * np.pi * (1.3 + 0.4 * i) * t + 2 * i)
                lvl = bounce * (1.4 if i == lead else 1.0)
                fr = S.sprite(fr, po, MASKS[i], lvl, -1)
                if i == lead:
                    fr += light(GLOW[i], (0.5 + 0.4 * dn) * S.run['Right'] + 0.5 * S.blob(po, 40))
        out[f] = fr
    return np.clip(out, 0, 1)


def _cackle(B, t, f0, pan, n=6, rate=7.0, seed=0):
    """A cackle: ha-ha-ha, buzzy vowels falling in pitch."""
    dur = n / rate + 0.1
    m = int(dur * SR)
    tt = np.arange(m) / SR
    f = f0 * (1.0 - 0.25 * tt / dur) * (1 + 0.04 * np.sin(2 * np.pi * 6 * tt))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    gate = np.clip(np.sin(np.pi * ((tt * rate) % 1.0)) * 1.6, 0, 1) ** 2 * (tt < n / rate)
    breath = B._noise(0, 800, 4000, seed, n=m)
    sig = gate * (0.7 * saw + 0.3 * np.sin(2 * ph) + 0.25 * breath)
    k = np.ones(12) / 12
    sig = np.convolve(sig, k, 'same')
    B._sfx(sig / (np.abs(sig).max() + 1e-9), t, 0.22, pan)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=2.4)
    parts = {
        ('summon', 'tune'): [('muted horn', 0, 6, 0.8), ('bassoons', -12, 0, 0.5)],
        ('summon', 'bass'): [('basses pizz', 0, 0, 0.6)],
        ('summon', 'chord'): [('pizz', 0, -4, 0.4)],
        ('pop', 'tune'): [('xylo', 0, -2, 0.45), ('pizz', 12, 0, 0.45)],
        ('pop', 'bass'): [('basses pizz', 0, 0, 0.6)],
        ('pop', 'chord'): [('pizz', 0, -6, 0.35)],
        ('tub', 'tune'): [('tuba', -12, 4, 0.7), ('bassoons', 0, 0, 0.6)],
        ('tub', 'bass'): [('basses pizz', 0, 0, 0.6)],
        ('tub', 'chord'): [('muted horn', 0, -10, 0.35)],
        ('devil', 'tune'): [('bassoons', 0, 6, 0.8), ('muted horn', 0, 0, 0.55), ('xylo', 0, -10, 0.3)],
        ('devil', 'bass'): [('tuba', -12, 0, 0.65), ('basses pizz', 0, -4, 0.45)],
        ('devil', 'chord'): [('pizz', 0, -4, 0.45)],
        ('witch', 'tune'): [('oboes', 0, 6, 0.75), ('clarinets', 0, 0, 0.55), ('pizz', 12, -2, 0.4)],
        ('witch', 'bass'): [('cellos pizz', 0, 0, 0.55), ('basses pizz', 0, -4, 0.45)],
        ('witch', 'chord'): [('pizz', 0, -4, 0.45), ('harp', 0, -6, 0.35)],
        ('skeleton', 'tune'): [('xylo', 0, 4, 0.6), ('marimba', 0, 4, 0.6), ('pizz', 12, 0, 0.4)],
        ('skeleton', 'bass'): [('tuba', -12, 2, 0.65), ('basses pizz', 0, -2, 0.5)],
        ('skeleton', 'chord'): [('pizz', 0, -2, 0.45), ('buzz trombone', 0, -12, 0.35)],
        ('squabble', 'tune'): [('trumpets', 0, 0, 0.5), ('xylo', 0, 0, 0.45), ('violins', 0, -4, 0.45)],
        ('squabble', 'bass'): [('tuba', -12, 2, 0.6), ('cellos', 0, -4, 0.45)],
        ('squabble', 'chord'): [('violas', 0, -10, 0.35)],
        ('finale', 'tune'): [('trumpets', 0, 6, 0.65), ('horns', 0, 4, 0.6), ('violins', 0, 2, 0.55),
                             ('xylo', 0, -2, 0.45), ('choir', 0, 0, 0.6)],
        ('finale', 'bass'): [('tuba', -12, 6, 0.8), ('basses', 0, 0, 0.5), ('timpani', 0, 4, 0.35)],
        ('finale', 'chord'): [('trombones', 0, -4, 0.5), ('pizz', 0, -2, 0.45)],
    }
    B.perform(C.events, parts)
    B.play('cellos trem', 45, 0.0, 2.0, 70, gain=0.4)
    B.effects([(0, -4), (T_SANTA, 0), (M['devil'], -3), (M['squabble'], 0), (M['finale'], -4),
               (M['out'] - 0.5, 0)])
    # the man in red: a sleigh-bell shimmer and a gasp of cymbal
    B.sleigh_bells(T_SANTA, T_SANTA + 1.4, beat=0.12, pan=S.pan(P['santa']), gain=0.6)
    B.hit('cymbal swell', T_SANTA - 1.0, 100, gain=0.4)
    # pop, pop, pop, and all three cackle
    pitches = (180, 420, 300)
    for i, tp in enumerate(T_POPS):
        B.hit('slapstick', tp, 120, gain=0.8, pan=S.pan(P['pops'][i]))
        _cackle(B, tp + 0.15, pitches[i], S.pan(P['pops'][i]), n=3, seed=10 + i)
    for i in range(3):
        _cackle(B, T_ALL + 0.03 * i, pitches[i], S.pan(P['pops'][i]), n=6, seed=20 + i)
    # the tub's claw feet clacking down to the treehouse (and off at the end)
    for t0, t1 in ((M['tub'], M['devil'] - 0.2), (M['out'] - 3.0, M['out'] + 0.6)):
        t, k = t0, 0
        while t < t1:
            B.hit('claves' if k % 2 else 'wood', t, 100, gain=0.45, pan=S.pan(min(tub_pos(S, P, t), S.L)), fx=True)
            t += 1 / 6
            k += 1
    # 1. the cage: a metal clang for each bar, the door locked with a crash
    for k, tb in enumerate(DB['devil']):
        B.hit('anvil', tb, 110, gain=0.45, pan=S.pan(P['santa'] + (k - 3.5) * 42), fx=True)
    B.clash(T_LOCK, pan=S.pan(P['santa']), gain=0.8)
    _cackle(B, T_LOCK + 0.3, pitches[0], S.pan(P['tree']), n=5, seed=31)
    # 2. the trap: the ratchet with each step of the jaws, then SNAP
    for tb in DB['witch']:
        B.hit('ratchet', tb, 100, gain=0.5, pan=0.0, fx=True)
    B.clash(T_SNAP, pan=0.0, gain=1.0)
    B.hit('crash', T_SNAP, 124, gain=0.6)
    B.hit('bass drum', T_SNAP, 124, gain=0.6)
    _cackle(B, T_SNAP + 0.4, pitches[1], S.pan(P['tree']), n=6, seed=32)
    # 3. the boogeyman: a low rumble rising, bugs crawling, his laugh on the buzzing trombone
    db = DB['skeleton']
    B.hit('timpani roll', M['skeleton'], 100, pitch=-5, gain=0.5)
    B.swarm(db[2], M['squabble'], level=0.6, pan=0.0)
    for k, m in enumerate((43, 46, 43, 41, 38)):
        B.play('buzz trombone', m, db[5] + 0.3 * k, 0.28, 110, pan=S.pan(S.mid), gain=0.7)
    B.boom(db[4], pan=0.0, gain=0.6)
    _cackle(B, db[-1] + 0.6, pitches[2], S.pan(P['tree']), n=6, seed=33)
    # 4. the squabble: thwacks, a ratchet, whooshes
    for j, th in enumerate(SQ_HITS):
        B.hit('slapstick' if j % 2 else 'wood', th, 120, gain=0.7, pan=S.pan(P['tree']) + 0.1 * ((j % 3) - 1))
        if j % 3 == 2:
            B.whoosh(th, 0.4, up=bool(j % 2), pan=S.pan(P['tree']), gain=0.5)
    B.hit('ratchet', SQ_HITS[len(SQ_HITS) // 2], 110, gain=0.6, pan=S.pan(P['tree']), fx=True)
    # 5. off they go: all three cackle, a crash on the way out
    for i in range(3):
        _cackle(B, M['out'] - 0.2 + 0.04 * i, pitches[i], 0.85, n=7, seed=40 + i)
    B.hit('crash', M['out'] + 0.4, 124, gain=0.6)
    B.hit('bass drum', M['out'] + 0.4, 120, gain=0.6)
    B.finish()
