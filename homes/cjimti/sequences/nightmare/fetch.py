"""Fetch in the Graveyard: Zero rises from his grave, chases a bone round the roof, and the two wander
off into strange woods until dawn.

The graveyard in moonlight, the Pumpkin King on the porch. Out on Right a grey headstone glows, a white mist climbs
out of it and Zero's nose lights up in a burst of orange that floods the wing: woof. His own little tune
plays on the glockenspiel while he bounds about his grave. The king throws a rib bone: it flies along the roof in
a white streak to the far end of Left, and the dog dashes after it, past Jack, the whole way round the porch,
and catches it in a spray of sparks (woof). He trots back with it and drops it at Jack's feet. A second throw
sends it out to the free end of Right; the third and biggest flies over the left wing and off down the Side, and
the dog races after it into the dark, Jack following. Then a long walk all night: the two come back in from
the free end of Right into woods that turn grey-green and strange, dark trunks swaying and pale green eyes
glinting, the dog's nose lighting the way ahead while Jack's lament plays on a far-off celesta. Dawn breaks
pale from the porch outwards and the woods fade to a pale pink-gold.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events, so every
throw, catch and woof lands on the music."""
import numpy as np
from pixelhome.audio import slide
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (drift, Chart, Band, Stage, pulse, NOSE, BONE, WHITE, MOON, GREY, NIGHT, GOLD, PINK,
                                 ORANGE, VIOLET)

CODE = 'NM03'
TITLE = 'Fetch in the Graveyard'
KIND = 'show'
DESCRIPTION = ('Zero rises from his grave on the right wing, nose aglow, and races round the house after the bones Jack '
    'throws. Then the two wander off into grey-green woods until a pale dawn.')
VOICEOVER = 'Only one friend follows Jack everywhere. Zero is small, and see-through, and his nose glows.'

MOSS = hexc('#40c070')
SAGE = hexc('#90b8a0')
EYE = hexc('#a0ff40')
DAWN = hexc('#ffc8a0')
ROSE = hexc('#ff8090')

THROWS = 3


def compose():
    C = Chart()
    C.rest(2.5)                                             # the graveyard comes up
    C.mark('rise')
    C.rest(3.0)                                             # the dog rises from his grave
    C.mark('play')
    C.play('zero', style='march', bpm=120, tag='play')      # he bounds about his grave
    for i in range(THROWS):
        C.mark(f'throw{i}')
        C.play('zero', style='drive', bpm=132, tag=f'throw{i}', transpose=2 * i)
        if i < THROWS - 1:
            C.mark(f'back{i}')
            C.play('zero', style='march', bpm=132, tag=f'back{i}', transpose=2 * i)
    C.mark('follow')
    C.play('zero', style='hold', bpm=100, tag='follow', transpose=4)        # Jack follows him off
    C.mark('woods')
    C.play('king', style='arp', bars=(0, 8), bpm=84, tag='woods')           # all night through the woods
    C.mark('dawn')
    C.rest(6.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def places(S):
    grave = S.at('Right', 0.3)
    king = S.at('Porch Front', 0.3)
    targets = [S.at('Left', 0.35), S.at('Right', 0.88), -150.0]
    return grave, king, targets


def bone_at(S, t):
    """(where the bone is or None, flying?) for time t."""
    grave, king, targets = places(S)
    for i in range(THROWS):
        t0 = M[f'throw{i}']
        t1 = M[f'back{i}'] if i < THROWS - 1 else M['follow']
        if t0 <= t < t0 + 1.3:                              # in flight
            u = smoothstep(0, 1.3, t - t0) ** 0.8
            return king + (targets[i] - king) * u, True
    return None, False


def dog_at(S, t):
    """Where Zero is and which way he faces, and whether he carries the bone."""
    grave, king, targets = places(S)
    if t < M['throw0'] + 0.3:
        hop = 30 * np.sin(2 * np.pi * 0.5 * (t - M['play'])) if t >= M['play'] else 0.0
        return grave + hop, -1 if np.cos(2 * np.pi * 0.5 * (t - M['play'])) > 0 else 1, False
    prev = grave
    for i in range(THROWS):
        t0 = M[f'throw{i}']
        tb = M[f'back{i}'] if i < THROWS - 1 else M['follow']
        if t < tb:
            p = keys(t, [(t0 + 0.3, prev), (tb - 0.25, targets[i])])
            return p, (1 if targets[i] > prev else -1), False
        if i < THROWS - 1:
            tn = M[f'throw{i + 1}']
            home = king + 20
            if t < tn + 0.3:
                p = keys(t, [(tb, targets[i]), (tn - 0.3, home)])
                return p, (1 if home > targets[i] else -1), t < tn - 0.3
            prev = home
    # the woods: back in from the free end of Right, nosing about ahead of Jack
    if t >= M['woods']:
        k = king_at(S, t)[0]
        return k - 60 - 50 * np.sin(2 * np.pi * 0.23 * (t - M['woods'])), -1, False
    return -200.0, -1, False


def king_at(S, t):
    grave, king, targets = places(S)
    if t < M['follow']:
        return king, (1 if t < M['throw0'] else -1)
    if t < M['woods']:
        return keys(t, [(M['follow'], king), (M['woods'] - 0.2, -60.0)]), -1
    return keys(t, [(M['woods'], S.L + 30), (M['dawn'] + 1.0, S.at('Porch Right', 0.3))]), -1


def woods(S, t, lv, rng_off):
    """The woods all night: grey-green mist, dark trunks swaying, pale green eyes glinting here and there."""
    d = S.d
    m = 0.5 + 0.5 * drift(12, d - 22 * t + rng_off + 1e5, 130.0)
    sway = 6 * np.sin(0.7 * t + d / 300)
    trunk = np.exp(-(((d + sway) % 75 - 37) / 7) ** 2)
    fr = light(MOSS, 0.6 * lv * (0.35 + 0.65 * m) * (1 - 0.85 * trunk))
    fr += light(SAGE, 0.25 * lv * np.clip(m - 0.55, 0, 1) * 2)
    return fr


def render(G, seed=3):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    grave, king, targets = places(S)
    beats = np.array([b[0] for b in C.beats])
    tunes = np.array([n[0] for n in C.tunes()])
    rng = np.random.default_rng(seed)
    eyes = [(rng.uniform(M['woods'], M['dawn']), rng.uniform(0, S.L)) for _ in range(14)]
    catches = [(M[f'back{i}'] if i < THROWS - 1 else M['follow']) - 0.25 for i in range(THROWS)]
    drops = [M[f'throw{i + 1}'] - 0.3 for i in range(THROWS - 1)]
    off = rng.uniform(0, 1000)
    wings = S.wings | S.run['Side']

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 2.5, t)
        night = 1 - smoothstep(M['woods'] - 1.5, M['woods'] + 3.0, t)
        wood = smoothstep(M['woods'] - 1.0, M['woods'] + 4.0, t) * (1 - smoothstep(M['dawn'], M['dawn'] + 3.0, t))
        dawn = smoothstep(M['dawn'] - 1.0, M['dawn'] + 3.5, t)
        beat = pulse(t, beats, 0.15)

        fr = S.graveyard(t, lv=up * night, moon=1.0, hill=0.7) if night > 0 else np.zeros((G.N, 3))
        if wood > 0:
            fr += woods(S, t, wood, off)
            for te, pe in eyes:                             # pale green eyes, two by two, blinking in the trees
                a = t - te
                if 0 <= a < 2.5:
                    e = wood * np.sin(np.pi * a / 2.5) * (0.3 if 1.0 < a < 1.15 else 1.0)
                    fr += light(EYE, 0.7 * e * (S.blob(pe, 5) + S.blob(pe + 14, 5)))
        if dawn > 0:                                        # dawn breaks pale from the porch outwards
            reach = 200 + 1500 * dawn
            wash = smoothstep(reach + 200, reach - 200, np.abs(d - mid))
            fr = fr * (1 - 0.6 * dawn * wash)[:, None]
            fr += light(DAWN, 0.55 * dawn * wash) + light(ROSE, 0.3 * dawn * wash * (0.5 + 0.5 * np.sin(d / 120 - 0.4 * t)))
            fr += light(GOLD, 0.5 * dawn * S.blob(mid, 200))

        # the dog rises: the headstone glows, a mist climbs out, the nose lights in a burst over the wing
        if M['rise'] - 1.0 <= t < M['play'] + 1.0:
            a = t - M['rise']
            stone = smoothstep(-1.0, 0.5, a) * (1 - smoothstep(2.0, 3.0, a))
            fr += light(GREY, 0.9 * stone * S.blob(grave, 10))
            mist = smoothstep(0.0, 2.6, a) * (1 - smoothstep(3.0, 4.0, a))
            fr += light(MOON, 0.7 * mist * S.blob(grave, 25 + 80 * smoothstep(0, 2.6, a)))
        if M['play'] <= t < M['play'] + 1.5:
            a = t - M['play']
            fr += light(NOSE, 0.95 * np.exp(-a / 0.35) * S.run['Right'])
            fr += light(WHITE, 0.8 * np.exp(-a / 0.1) * S.blob(grave, 60))

        # the tune: each glockenspiel note a little sparkle round the dog, the beat pulsing the wings orange
        dp, dfac, carry = dog_at(S, t)
        for t0 in tunes[(tunes <= t) & (tunes > t - 0.6) & (tunes < M['woods'])]:
            a = t - t0
            fr += light(WHITE, 0.6 * np.exp(-a / 0.15) * S.blob(dp + 30 * np.sin(t0 * 7), 14))
        if M['play'] <= t < M['follow']:
            fr += light(NOSE, 0.4 * beat * wings)

        # the bone in flight: a white streak along the roof with a long tail
        bp, flying = bone_at(S, t)
        if flying:
            i = max(k for k in range(THROWS) if M[f'throw{k}'] <= t)
            src = king
            tail = S.span(min(bp, src), max(bp, src)) * np.exp(-np.abs(d - bp) / 320)
            fr += light(BONE, 0.85 * tail)
            fr += light(NOSE, 0.25 * S.run_at(bp))
            if bp > -10:
                fr = S.sprite(fr, bp, [(1, BONE, 1.0), (0, WHITE, 0.7), (-1, BONE, 1.0)], 1.0)
            fr += light(WHITE, 0.4 * S.blob(bp, 30))
        # the throw: a flash off Jack; the catch and the drop: sparks
        for k in range(THROWS):
            a = t - M[f'throw{k}']
            if 0 <= a < 0.6:
                fr += light(BONE, 0.8 * np.exp(-a / 0.15) * S.blob(king, 80))
        fr += S.burst([(tc, 1.3, max(targets[k], 20.0)) for k, tc in enumerate(catches)], t, seed=5, n=22,
                      colors=(WHITE, NOSE, BONE))
        fr += S.burst([(td, 0.6, king + 20) for td in drops], t, seed=6, n=8, colors=(BONE, NOSE))

        # where the bone lies when nobody is carrying or throwing it
        for k in range(THROWS - 1):
            if catches[k] - 0.0 <= t < M[f'throw{k + 1}'] and not carry:
                fr = S.sprite(fr, king + 35, [(1, BONE, 0.8), (0, BONE, 0.4), (-1, BONE, 0.8)], 0.8)

        # the dog: his nose floods his run as he dashes; he carries the bone home in his mouth
        moving = M['throw0'] + 0.3 <= t < M['follow'] or t >= M['woods']
        if moving and -50 < dp < S.L + 50:
            fr += light(NOSE, 0.4 * S.run_at(dp) * (1 - 0.6 * (t >= M['woods'])))
            fr += light(WHITE, 0.35 * S.blob(dp, 45) * (t < M['follow']))
        if t >= M['woods']:
            fr += light(NOSE, 0.55 * wood * S.blob(dp - 40, 70))        # the nose lights the way
        if carry and -15 < dp < S.L + 15:
            fr = S.sprite(fr, dp + dfac * 3 * 4.5, [(1, BONE, 1.0), (0, BONE, 0.5), (-1, BONE, 1.0)], 1.0, dfac)
        dlvl = smoothstep(M['rise'] + 1.5, M['play'], t) * (1 - dawn * 0.3)
        if -15 < dp < S.L + 15:
            fr = S.zero(fr, float(dp), dlvl, dfac, t, nose=1.0 + 0.3 * beat)

        # Jack: on the porch for the throws, follows the dog off, walks back in through the woods
        kp, kf = king_at(S, t)
        klvl = up * (1 - smoothstep(M['woods'] - 0.6, M['woods'] - 0.2, t) + smoothstep(M['woods'], M['woods'] + 1.5, t))
        if -15 < kp < S.L + 15:
            fr = S.jack(fr, float(kp), min(1.0, klvl), facing=kf, glow=0.35)
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=4.1)
    grave, king, targets = places(S)
    parts = {
        ('play', 'tune'): [('glock', 0, 0, 0.75), ('flutes', -12, -6, 0.35)],
        ('play', 'bass'): [('basses pizz', 0, 0, 0.6), ('tuba', -12, -10, 0.4)],
        ('play', 'chord'): [('pizz', 0, -4, 0.45)],
        'tune': [('glock', 0, 0, 0.7), ('xylo', -12, -4, 0.45), ('flutes', -12, -8, 0.3)],
        'bass': [('tuba', -12, 0, 0.6), ('basses pizz', 0, -4, 0.5)],
        'chord': [('pizz', 0, -4, 0.45)],
        'snare': [('snare', 0, -12, 0.3)],
        ('follow', 'tune'): [('glock', 0, -10, 0.55), ('clarinets', -12, -6, 0.45)],
        ('follow', 'hold'): [('violas', 0, -16, 0.35)],
        ('follow', 'pedal'): [('cellos', 0, -14, 0.4)],
        ('woods', 'tune'): [('flutes', 0, -4, 0.6), ('clarinets', -12, -10, 0.35)],
        ('woods', 'arp'): [('celesta', 12, -10, 0.45), ('harp', 0, -12, 0.3)],
        ('woods', 'pedal'): [('ghost', 12, -10, 0.6), ('cellos', 0, -16, 0.35)],
    }
    B.perform(C.events, parts)
    # the graveyard: an owl, the wind
    B.play('clarinets', 55, 1.0, 0.35, 70, -0.6, 0.5)
    B.play('clarinets', 52, 1.45, 0.6, 64, -0.6, 0.45)
    B.effects([(0, -6), (M['rise'], -4), (M['play'], 0), (M['woods'], -6), (M['dawn'], -10)])
    B.wind(0.0, M['play'] + 1.0, level=0.35, pan=0.5, seed=31)
    # he rises: a ghostly swell, a harp sweep, his nose lights with a bell tree, and the first woof
    gp = S.pan(grave)
    for m in (52, 56, 59, 64):
        B.play('ghost', m, M['rise'], 3.2, 80, gp, 0.5)
    for i, m in enumerate([52, 56, 59, 64, 68, 71, 76, 80]):
        B.play('harp', m, M['rise'] + 1.0 + i * 0.22, 0.8, 80, gp, 0.5)
    B.hit('bell tree', M['play'] - 0.3, 100, gain=0.55, pan=gp)
    B.woof(M['play'], pan=gp, big=1.0)
    # the tune's woof at the end of each time he plays it
    for tag in ['play'] + [f'back{i}' for i in range(THROWS - 1)]:
        t_last = C.tunes(tag)[-1][0]
        B.woof(t_last, pan=S.pan(dog_at(S, t_last)[0]), big=0.8)
    # the throws: a slide whistle with the bone, a whoosh after it, the dog's scrabble and his catch
    for i in range(THROWS):
        t0 = M[f'throw{i}']
        tc = (M[f'back{i}'] if i < THROWS - 1 else M['follow']) - 0.25
        pa, pb = S.pan(king), S.pan(max(targets[i], 0.0))
        B.M.add('fx', slide(0.0, 1.2, 600, 1800 if i < 2 else 2400, 1.3, amp=0.5), t0, 0.35,
                float(0.5 * (pa + pb)))
        B.hit('slapstick', t0, 100, gain=0.5, pan=pa)
        B.whoosh(t0 + 0.1, 1.2, up=True, pan=pb, gain=0.7)
        B.hit('wood', tc, 110, gain=0.6, pan=pb)
        B.woof(tc + 0.05, pan=pb, big=1.0)
        B.woof(tc + 0.35, pan=pb, big=0.8)
        if i < THROWS - 1:
            B.hit('wood', M[f'throw{i + 1}'] - 0.3, 90, gain=0.4, pan=pa)           # he drops it at Jack's feet
    B.woof(M['follow'] + 1.5, pan=-0.9, big=0.5)                                    # far off, down the Side
    # the woods: a far-off bark now and then, the wind among the trunks; dawn: a held chord and a woof
    B.wind(M['woods'], M['dawn'] + 2.0, level=0.3, pan=0.0, seed=33)
    B.woof(M['woods'] + 6.0, pan=0.7, big=0.4)
    B.woof(M['woods'] + 12.5, pan=0.4, big=0.45)
    for m in (52, 59, 64, 68):
        B.play('choir', m, M['dawn'], 4.5, 72, gain=0.35)
        B.play('violins', m + 12, M['dawn'] + 0.3, 4.0, 60, gain=0.3)
    B.play('cellos', 40, M['dawn'], 4.5, 70, gain=0.4)
    B.hit('triangle', M['dawn'] + 0.5, 80, gain=0.4)
    B.woof(D - 1.8, pan=S.pan(S.at('Porch Right', 0.3)), big=0.6)
    B.finish()
