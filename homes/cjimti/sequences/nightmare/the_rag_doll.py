"""The Rag Doll: she drugs the mad doctor's soup, drops out of his tower, sews herself back together and slips off
through town with a basket for the Pumpkin King.

Halloween Town glows violet with orange windows on every run. On Porch Front, the mad doctor's kitchen: a pot
bubbling orange over the porch, the doctor (a bright domed head, dark goggles, grey behind) on its right, the rag
doll (blue face, red hair, a patchwork dress) on its left, to her own theme in D minor on clarinet and pizzicato.
She tips a vial: three green drops fall into the pot, each a green flash, and the soup turns green. The doctor
leans in and sniffs (a curl of steam runs to him), slurps (a green streak), and nods off: his head sinks and dims,
and he snores three times, each breath in drawing the house's light in to him and each snore rolling a big blue
wave out over the whole house, three white Z's drifting off along Right. Then she climbs out of the window at the
porch's right corner and lowers herself down Porch Right on a rope, hand over hand on the beat, to her theme on the
oboe. The rope snaps: she drops to the corner with a slide whistle, lands with a thud and a puff of dust, and
flies apart along Right in six pieces (face, hair, four patches). A needle glints back and forth, a stitch on each
note of her theme on pizzicato, and each stitch pulls a piece home until she's whole again in a flash of blue.
With a basket on her arm she slips through town back across the porch, past the sleeping doctor, to the king's
door on Left (an orange door), on her theme in full strings, pausing on every bar. She sets the basket down,
knocks three times (the door flares at each), and runs off along Side as the door opens and floods Left with
warm light.

compose() lays the music end to end: render() and score() read its events and marks."""
import numpy as np
from pixelhome.audio import SR, slide
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, SLIME, VIOLET, DUSK, MOON, BONE,
                                 WHITE, GOLD, ICE, WARM, RED, GREEN, BLUE, GREY, SALLY, HAIR)

CODE = 'NM08'
TITLE = 'The Rag Doll'
KIND = 'show'
DESCRIPTION = ('The rag doll drops a sleeping draught in the mad doctor\'s soup and he snores the house blue. She '
               'climbs down from his tower, falls to pieces along the right wing, stitches herself whole and slips off '
               'with a basket for the king.')
VOICEOVER = ('The mad doctor kept his rag doll locked in his tower. '
             'Tonight, she had other plans, and a little something for his soup.')

DRAUGHT = hexc('#40ff60')
SOUP = hexc('#ff6a10')


def compose():
    C = Chart()
    C.rest(2.0)                                                 # the town, the doctor's kitchen, the pot
    C.mark('soup')
    C.play('sally', style='waltz', bars=(0, 4), bpm=92, tag='soup')
    C.mark('snore')
    C.rest(5.4)                                                 # he nods off and snores, three times
    C.mark('climb')
    C.play('sally', style='waltz', bars=(4, 8), bpm=80, tag='climb')
    C.mark('fall')
    C.rest(2.4)                                                 # the rope snaps; she falls and comes apart
    C.mark('stitch')
    C.play('sally', style='waltz', bars=(0, 4), bpm=108, tag='stitch')
    C.mark('walk')
    C.play('sally', style='waltz', bars=(8, 16), bpm=100, tag='walk')
    C.mark('knock')
    C.rest(4.8)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
SOUP_DB = C.downbeats('soup')
T_DROPS = [SOUP_DB[1] + 0.2 * k for k in range(3)]             # three drops of the draught
T_SNIFF, T_SLURP = SOUP_DB[2], SOUP_DB[3]
T_SNORES = [M['snore'] + 1.2 + 1.4 * k for k in range(3)]       # each snore: breath in, then out at +0.6
T_SNAP = M['fall'] + 0.2
T_LAND = M['fall'] + 0.9
STITCHES = [n[0] for n in C.tunes('stitch')]
T_KNOCKS = [M['knock'] + 0.6 + 0.32 * k for k in range(3)]
T_RUN = M['knock'] + 1.8


def places(S):
    return dict(pot=S.mid, doc=S.mid + 55, doll=S.mid - 55, window=S.at('Porch Front', 1.0),
                rope_end=S.at('Porch Right', 0.62), land=S.at('Right', 0.2), door=S.at('Left', 0.3))


def doctor(S, fr, p, lvl, nod=0.0):
    """The mad doctor: a big bright domed head with dark goggles, his grey chair behind; nod sinks and dims him."""
    h = 1.0 - 0.55 * nod
    px = [(2, BONE, h), (1, BONE, h), (0, None, 0), (-1, ICE, 0.5 * h), (-2, BONE, 0.8 * h), (-3, None, 0),
          (-4, GREY, 0.55), (-5, GREY, 0.55), (-6, None, 0), (-7, GREY, 0.45), (-8, GREY, 0.45)]
    fr = S.sprite(fr, p, px, lvl, -1)
    return fr + light(ICE, 0.25 * lvl * h * S.blob(p - 5, 30))


PIECES = [[(1, SALLY, 0.95), (0, SALLY, 0.9)], [(1, HAIR, 0.9), (0, HAIR, 0.85), (-1, HAIR, 0.7)],
          [(0, BLUE, 0.7), (-1, GOLD, 0.6)], [(0, RED, 0.7), (-1, GREEN, 0.6)], [(0, BLUE, 0.6)], [(0, GOLD, 0.6)]]
HOME = [0, -2, -5, -8, -11, -13]                                # where each piece sits on her, pixels behind her face


def scatter(S, P):
    """Where each piece lands along Right after the fall (path distance) and when it is stitched home."""
    rng = np.random.default_rng(808)
    to = P['land'] + np.array([40, 140, -20, 230, 300, 90]) + rng.uniform(-10, 10, 6)
    home_t = [STITCHES[min(1 + i, len(STITCHES) - 1)] for i in range(6)]
    return to, home_t


def walk_pos(P, t):
    """Her path along the town from where she landed to the king's door: a sneak, a bar at a time."""
    downs = C.downbeats('walk')
    k = np.searchsorted(downs, t, side='right') - 1
    if k < 0:
        return P['land']
    bar = (downs[1] - downs[0])
    u = (k + smoothstep(0.0, 0.7, (t - downs[k]) / bar)) / len(downs)
    return P['land'] + (P['door'] - P['land']) * min(u, 1.0)


def render(G, seed=8):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    P = places(S)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array([b[0] for b in C.beats])
    tos, home_t = scatter(S, P)
    walk_t = np.array([n[0] for n in C.tunes('walk')])

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.8, t)
        beat = pulse(t, beats, 0.15)
        fr = S.town(t, lv=1.0 * up, mist=0.7) + light(DUSK, 0.3 * up * np.ones(G.N))
        # the pot: bubbling orange, turning green with the draught
        green = smoothstep(T_DROPS[0], T_SLURP, t)
        if t < M['climb'] + 1:
            pot = (1 - green) * SOUP + green * DRAUGHT
            fr += light(pot, (0.9 + 0.2 * np.sin(11 * t + d / 7)) * S.blob(P['pot'], 30) * up)
            fr += light(pot, 0.5 * up * S.porch * (0.75 + 0.25 * beat) * (0.8 + 0.2 * np.sin(5 * t + d / 30)))
            for k in range(3):                                  # steam puffs drifting up out of it
                ph = (t * 0.6 + k / 3) % 1.0
                for sgn in (-1, 1):
                    fr += light(BONE, 0.4 * (1 - ph) * S.blob(P['pot'] + sgn * 140 * ph, 10)) * up
        # the draught: three green drops from her hand into the pot
        for td in T_DROPS:
            a = t - td
            if -0.35 <= a < 0:
                p = P['doll'] + 8 + (P['pot'] - P['doll'] - 8) * (1 + a / 0.35)
                fr += light(DRAUGHT, 1.0 * S.blob(p, 6))
            elif 0 <= a < 0.6:
                fr += light(DRAUGHT, 1.0 * np.exp(-a / 0.2) * (S.blob(P['pot'], 50) + 0.8 * S.porch + 0.4 * S.wings))
        # he sniffs: a curl of steam runs to him; he slurps: a green streak
        if T_SNIFF <= t < T_SNIFF + 1.0:
            a = t - T_SNIFF
            fr += light(WHITE, 0.7 * np.exp(-a / 0.5) * S.blob(P['pot'] + 55 * smoothstep(0, 0.6, a), 12))
        if T_SLURP <= t < T_SLURP + 1.0:
            a = t - T_SLURP
            fr += light(DRAUGHT, 0.9 * np.exp(-a / 0.4) * S.span(P['pot'], P['pot'] + 55 * smoothstep(0, 0.3, a)))
        # the snores: breath in draws the light in to him; out, a big blue wave over the house, Z's drifting off
        for ts in T_SNORES:
            a = t - ts
            if 0 <= a < 0.6:
                fr *= 1 - 0.6 * smoothstep(0, 0.6, a)
                fr += light(ICE, 0.9 * smoothstep(0, 0.6, a) * S.blob(P['doc'], 60))
                fr += light(BLUE, 0.6 * np.exp(-((np.abs(d - P['doc']) - 1200 * (1 - a / 0.6)) / 150) ** 2))
            elif 0.6 <= a < 2.6:
                b = a - 0.6
                fr += light(BLUE, 1.1 * np.exp(-b / 0.9) * np.exp(-((np.abs(d - P['doc']) - 900 * b) / 200) ** 2))
                fr += light(SALLY, 0.6 * np.exp(-b / 0.6) * np.ones(G.N))
                for z in range(3):
                    pz = P['doc'] + 350 + 380 * max(b - 0.25 * z, 0)
                    fr += light(WHITE, 1.0 * np.exp(-b / 1.0) * (b > 0.25 * z) * S.blob(pz, 12))

        # the doctor: alert, then nodding off; he sleeps through the rest
        nod = smoothstep(T_SLURP + 0.3, M['snore'] + 1.0, t)
        lean = 18 * pulse(t, [T_SNIFF], 0.5)
        sleepy = up * (1 - 0.4 * smoothstep(M['walk'] + 10, D, t))
        fr = doctor(S, fr, P['doc'] - lean, sleepy, nod)

        # the rag doll
        if t < M['climb']:
            fr = S.sally(fr, P['doll'], up, facing=1)
            fr += light(SALLY, 0.5 * up * S.blob(P['doll'] - 20, 60))
            if SOUP_DB[0] <= t < T_DROPS[-1] + 0.3:             # the vial in her hand
                fr += light(DRAUGHT, 0.8 * S.blob(P['doll'] + 14, 6))
        elif t < T_SNAP:
            # to the window, then down the rope hand over hand on the beat
            db = C.downbeats('climb')
            if t < db[1]:
                p = P['doll'] + (P['window'] - P['doll']) * smoothstep(M['climb'], db[1], t)
            else:
                k = np.searchsorted(beats, t, side='right') - 1
                steps = np.sum((beats >= db[1]) & (beats <= t))
                total = np.sum((beats >= db[1]) & (beats < M['fall']))
                frac = smoothstep(0, 0.35, t - beats[k])
                p = P['window'] + (P['rope_end'] - P['window']) * min((steps - 1 + frac) / total, 1.0)
                fr += light(GOLD, 0.7 * S.span(P['window'], p))  # the rope
            fr = S.sally(fr, p, 1.0, facing=1)
            fr += light(SALLY, 0.6 * S.run_at(p) * (0.7 + 0.3 * beat) + 0.7 * S.blob(p, 70))
            fr += light(SALLY, 0.4 * S.wings)
        elif t < T_LAND:
            # the rope snaps; she drops to the corner
            u = ((t - T_SNAP) / (T_LAND - T_SNAP)) ** 2
            p = P['rope_end'] + (S.at('Porch Right', 1.0) + 8 - P['rope_end']) * u
            fr = S.sally(fr, p, 1.0, facing=1)
            fr += light(SALLY, 0.8 * S.blob(p, 60))
            fr += light(GOLD, 0.8 * np.exp(-(t - T_SNAP) / 0.2) * S.span(P['window'], P['rope_end']))
        elif t < M['walk']:
            # in pieces along Right, each stitched home in turn
            a = t - T_LAND
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * S.blob(P['land'], 60))
                fr += light(GREY, 0.6 * np.exp(-a / 0.3) * S.run['Right'])
            fr += light(SALLY, 0.55 * S.run['Right'] + 0.3 * S.porch)
            fly = 1 - np.exp(-a / 0.15)
            for i, px in enumerate(PIECES):
                start = P['land'] + HOME[i] * 4.0
                pi_ = start + (tos[i] - start) * fly
                if t >= home_t[i] - 0.35:
                    b = smoothstep(home_t[i] - 0.35, home_t[i], t)
                    pi_ = tos[i] + (start - tos[i]) * b
                hop = 0.75 + 0.25 * abs(np.sin(2 * np.pi * 1.5 * a + i))
                fr = S.sprite(fr, pi_, px, hop, facing=1)
            # the needle, glinting from piece to piece on each stitch
            k = int(np.searchsorted(STITCHES, t, side='right')) - 1
            if k >= 0:
                j = min(k + 1, 5)
                tgt = tos[j] if t < home_t[j] - 0.35 else P['land']
                b = smoothstep(STITCHES[k], STITCHES[k] + 0.2, t)
                pn = P['land'] + (tgt - P['land']) * (1 - b if k % 2 else b)
                fr += light(WHITE, 1.0 * S.blob(pn, 5))
                fr += light(WHITE, 0.8 * np.exp(-(t - STITCHES[k]) / 0.15) * S.blob(P['land'], 40))
                fr += light(HAIR, 0.5 * np.exp(-(t - STITCHES[k]) / 0.2) * S.run['Right'])
            done = smoothstep(home_t[-1], home_t[-1] + 0.3, t)
            if done > 0:
                fr += light(SALLY, 1.0 * np.exp(-(t - home_t[-1]) / 0.5) * np.ones(G.N))
        elif t < T_RUN:
            # through town with the basket, to the king's door
            p = walk_pos(P, t)
            fr = S.sally(fr, p, 1.0, facing=-1)
            fr = S.sprite(fr, p - 4 * 4.5, [(1, WARM, 0.9), (0, RED, 0.9), (-1, WARM, 0.9)], 1.0, -1, cut=False)
            fr += light(SALLY, 0.7 * S.blob(p, 200))
            for j in np.flatnonzero((walk_t <= t) & (walk_t > t - 0.8)):
                fr += light(SALLY, 0.5 * np.exp(-(t - walk_t[j]) / 0.35) * S.run_at(p))
        else:
            # she runs off along Side
            u = smoothstep(T_RUN, T_RUN + 1.4, t)
            p = P['door'] - 30 - (P['door'] - 30 + 60) * u
            fr = S.sally(fr, p, 1.0 - 0.3 * u, facing=-1)

        # the king's door on Left: it flares at each knock and opens at the end
        if t >= M['walk']:
            dl = smoothstep(M['walk'], M['walk'] + 2, t)
            fr += light(PUMPKIN, 0.7 * dl * S.blob(P['door'], 18))
            fr += light(WHITE, 0.9 * pulse(t, T_KNOCKS, 0.12) * S.blob(P['door'], 30))
            fr += light(PUMPKIN, 0.5 * pulse(t, T_KNOCKS, 0.2) * S.run['Left'])
            op = smoothstep(T_RUN + 0.5, T_RUN + 1.2, t)
            fr += light(WARM, 0.9 * op * (S.run['Left'] | S.run['Side']) * (0.5 + 0.5 * S.blob(P['door'], 220)))
        if t >= M['knock'] + 0.2:                               # the basket left on the step
            fr = S.sprite(fr, P['door'] - 14, [(1, WARM, 0.9), (0, RED, 0.9), (-1, WARM, 0.9)], 1.0, -1)
        out[f] = fr * float(smoothstep(D, D - 1.2, t))
    return np.clip(out, 0, 1)


def _snore(B, t, pan, seed):
    """A snore: a rough low drone breathing in, then a rattle out with a little whistle on top."""
    n = int(1.6 * SR)
    tt = np.arange(n) / SR
    env_in = np.clip(tt / 0.6, 0, 1) * (tt < 0.6)
    env_out = np.clip((tt - 0.6) / 0.08, 0, 1) * np.exp(-np.clip(tt - 0.6, 0, None) / 0.45) * (tt >= 0.6)
    f = np.where(tt < 0.6, 90 + 30 * tt, 75 - 10 * (tt - 0.6))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    rattle = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * tt))
    noise = B._noise(0, 200, 2500, seed, n=n)
    sig = 0.5 * env_in * noise + env_out * (0.8 * saw * rattle + 0.4 * noise)
    B._sfx(sig / np.abs(sig).max(), t, 0.35, pan)
    B.M.add('fx', slide(0, 0.7, 900, 1500, 0.8, amp=0.12), t + 0.65, 0.8, pan)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=4.5)
    parts = {
        ('soup', 'tune'): [('clarinets', 0, 4, 0.8), ('pizz', 12, -8, 0.3)],
        ('soup', 'bass'): [('basses pizz', 0, 0, 0.6)],
        ('soup', 'chord'): [('pizz', 0, -4, 0.45)],
        ('climb', 'tune'): [('oboes', 0, 6, 0.85)],
        ('climb', 'bass'): [('cellos', 0, -4, 0.5), ('basses pizz', 0, -4, 0.4)],
        ('climb', 'chord'): [('harp', 0, -2, 0.5), ('violas', 0, -12, 0.3)],
        ('stitch', 'tune'): [('pizz', 12, 4, 0.6), ('xylo', 12, -8, 0.35), ('clarinets', 0, -4, 0.45)],
        ('stitch', 'bass'): [('basses pizz', 0, 0, 0.6)],
        ('stitch', 'chord'): [('pizz', 0, -4, 0.4)],
        ('walk', 'tune'): [('violins', 0, 6, 0.75), ('oboes', 0, -4, 0.45), ('celesta', 12, -14, 0.35)],
        ('walk', 'bass'): [('cellos', 0, 0, 0.55), ('basses pizz', 0, -2, 0.45)],
        ('walk', 'chord'): [('violas', 0, -10, 0.35), ('harp', 0, -4, 0.45)],
    }
    B.perform(C.events, parts)
    # the town at night, a bubbling pot
    B.play('cellos trem', 50, 0.0, 2.2, 66, gain=0.4)
    for k in range(int(M['snore'] / 0.37)):
        tb = 0.3 + 0.37 * k + 0.1 * np.sin(k)
        B.play('marimba', 45 + (k * 7) % 12, tb, 0.2, 50, pan=S.pan(P['pot']), gain=0.18)
    B.effects([(0, -6), (T_DROPS[0], 0), (M['climb'], -3), (T_SNAP - 0.1, 2), (M['stitch'], -1), (M['walk'], -8),
               (M['knock'], 0)])
    for k, td in enumerate(T_DROPS):                            # plink, plink, plink
        B.play('glock', 69 - 3 * k, td, 0.2, 100, pan=S.pan(P['pot']), gain=0.5)
        B.play('pizz', 69 - 3 * k, td, 0.2, 90, pan=S.pan(P['pot']), gain=0.4)
    # the sniff and the slurp
    n = int(0.6 * SR)
    sniff = B._noise(0, 1500, 6000, 41, n=n) * np.clip(np.arange(n) / n, 0, 1) ** 2 * B._wobble(n, 8, 42, 0.8)
    B._sfx(sniff, T_SNIFF, 0.35, S.pan(P['doc']))
    B.M.add('fx', slide(0, 0.5, 300, 700, 0.55, amp=0.15), T_SLURP, 0.8, S.pan(P['doc']))
    B._sfx(B._noise(0, 300, 3000, 43, n=int(0.5 * SR)) * np.hanning(int(0.5 * SR)), T_SLURP, 0.25, S.pan(P['doc']))
    for i, ts in enumerate(T_SNORES):
        _snore(B, ts, S.pan(P['doc']), 50 + i)
    B.play('bassoons', 38, M['snore'] + 0.3, 0.8, 80, gain=0.6)          # a drowsy bassoon sinking
    B.play('bassoons', 33, M['snore'] + 1.0, 1.0, 70, gain=0.6)
    # the rope snaps; she falls, lands and comes apart
    B.play('pizz', 43, T_SNAP, 0.2, 120, pan=S.pan(P['rope_end']), gain=0.7)
    B.hit('wood', T_SNAP, 120, gain=0.7, pan=S.pan(P['rope_end']))
    B.M.add('fx', slide(0, 0.65, 1800, 300, 0.7, amp=0.25), T_SNAP + 0.05, 0.9, S.pan(P['rope_end']))
    B.boom(T_LAND, pan=S.pan(P['land']), gain=0.6)
    B.hit('slapstick', T_LAND, 124, gain=0.8, pan=S.pan(P['land']))
    tos, home_t = scatter(S, P)
    for i, p in enumerate(tos):
        B.hit('wood', T_LAND + 0.08 + 0.05 * i, 100, gain=0.5, pan=S.pan(p))
    # the stitches: a little zip with each
    for i, ts in enumerate(STITCHES):
        B.whoosh(ts, 0.18, up=bool(i % 2), pan=S.pan(P['land']), gain=0.35)
    B.hit('bell tree', home_t[-1], 100, gain=0.5, pan=S.pan(P['land']))
    # the knocks, and the door opening
    for tk in T_KNOCKS:
        B.hit('wood', tk, 124, gain=0.9, pan=S.pan(P['door']))
        B.hit('slapstick', tk, 90, gain=0.3, pan=S.pan(P['door']))
    for k in range(6):                                           # her footsteps scurrying off
        B.hit('wood', T_RUN + 0.15 * k, 70, gain=0.3, pan=S.pan(P['door']) - 0.05 * k)
    B.hit('gong scrape', T_RUN + 0.6, 90, gain=0.35, pan=S.pan(P['door']))
    B.play('harp', 62, T_RUN + 0.7, 1.5, 80, gain=0.5)
    B.play('harp', 69, T_RUN + 0.9, 1.5, 80, gain=0.5)
    B.play('harp', 74, T_RUN + 1.1, 2.0, 80, gain=0.5)
    B.finish()
