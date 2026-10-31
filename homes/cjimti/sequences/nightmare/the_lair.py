"""The Boogeyman's Lair: a blacklit gambling den under the town, and a swing number for its host.

The den comes up in blacklight violet with green glow pulsing along the roof. Santa hangs tied on Porch Left, red
and white, struggling. Out of the porch grows the boogeyman, a huge lumpy burlap sack glowing under the
blacklight with two dark eyes and a grin, to a low buzzing trombone glissando, and the band strikes up his swung
shuffle: trombones on the tune, a walking bass, a ride cymbal. He dances on every beat (he swells and sways), every
note he sings throws burlap-gold light out along the porch, and the wings flash violet and green on the backbeat.

He spins the roulette wheel: a swipe streaks down Porch Left and the left wing becomes the wheel, violet and lime
pockets sliding past and slowing (a ratchet ticking each one) while a white ball swings through them in shorter
and shorter arcs and drops into a pocket; he laughs till he shakes. He flings two dice down Porch Right onto the
right wing: they tumble, rattling, and come up six and five. Then he turns on his prisoner: the band drives, the
pit under Santa on Porch Left roars into flame and climbs toward him, red flashes as he struggles. The shuffle
comes round again full (trumpets join, everything at once: the wheel spinning, the dice tumbling to double six,
the flames, bugs dancing the whole roof) and he ends it with a big bow and a lime flash.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() read its marks and events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, FLAME, SLIME, VIOLET, BONE, WHITE, GOLD, RED, UV,
                                 BURLAP, BUG)

CODE = 'NM13'
TITLE = "The Boogeyman's Lair"
KIND = 'show'
DESCRIPTION = ('A huge burlap sack runs a blacklit gambling den and sings a swing number at his prisoner: watch '
               'the roulette wheel spin on the left wing, dice tumble on the right, and the fire pit flare under '
               'Santa on the porch.')
VOICEOVER = ('Deep under the town, where the dice never stop rolling, the boogeyman has a guest. And he loves '
             'to play.')

LIME = hexc('#9aff00')
PIP = hexc('#f0ffd0')
BPM = 132
BEAT = 60 / BPM


def compose():
    C = Chart()
    C.rest(2.5)                                                 # the den comes up; Santa hangs tied
    C.mark('rise')
    C.rest(2.0)                                                 # the boogeyman grows up out of the porch
    C.mark('song')
    C.play('boogey', style='shuffle', bpm=BPM, tag='song')      # he sings and dances
    C.mark('wheel')
    C.play('boogey', style='shuffle', bars=(0, 4), bpm=BPM, tag='wheel')   # roulette on the left wing
    C.mark('dice')
    C.play('boogey', style='shuffle', bars=(4, 8), bpm=BPM, tag='dice')    # dice on the right
    C.mark('pit')
    C.play('boogey', style='drive', bars=(4, 8), bpm=BPM, tag='pit')       # he turns on his prisoner
    C.mark('shout')
    C.play('boogey', style='shuffle', bpm=BPM, tag='shout')     # everything at once
    C.mark('button')
    C.rest(2.6)
    C.mark('end')
    return C


C = compose()
M = C.marks
D = M['end']
POCKETS = 12
# spins of the wheel: (start, stop, pockets a second at the start, pocket the ball drops into)
SPINS = [(M['wheel'] + 0.3, M['wheel'] + 6.4, 7.0, 5), (M['shout'] + 0.5, M['shout'] + 12.0, 6.0, 8)]
# throws of the dice: (thrown, faces)
THROWS = [(M['dice'] + 0.4, (6, 5)), (M['shout'] + 3.0, (6, 6))]
PIPS = {1: [0.5], 2: [0.2, 0.8], 3: [0.15, 0.5, 0.85], 4: [0.12, 0.37, 0.63, 0.88],
        5: [0.1, 0.3, 0.5, 0.7, 0.9], 6: [0.08, 0.25, 0.42, 0.58, 0.75, 0.92]}


class Den:
    """Where the wheel, the ball, the dice and the fire are at any moment; render() draws them, score() hears them."""

    def __init__(self, S):
        self.S = S
        self.W0, self.W1 = S.at('Left', 0.0) + 10, S.at('Left', 1.0) - 10
        self.PW = (self.W1 - self.W0) / POCKETS
        self.dice = (S.at('Right', 0.3), S.at('Right', 0.7))
        self.DH = 0.12 * (S.at('Right', 1) - S.at('Right', 0))
        self.santa = S.at('Porch Left', 0.45)
        self.throw_from = S.at('Porch Right', 0.2)

    def turned(self, k, t):
        """Pockets spin k has turned at t, and how far through it is."""
        t0, t1, rate, _ = SPINS[k]
        u = float(np.clip((t - t0) / (t1 - t0), 0, 1))
        return rate * (t1 - t0) * (u - u * u / 2), u

    def landing(self, k):
        s_end, _ = self.turned(k, SPINS[k][1])
        j = SPINS[k][3]
        if (j + int(np.floor(s_end))) % 2:                # a lime pocket
            j += 1
        return self.W0 + self.PW * (j + 0.5 - (s_end % 1))

    def ball(self, k, t):
        t0, t1, _, _ = SPINS[k]
        u = float(np.clip((t - t0) / (t1 - t0), 0, 1))
        land = self.landing(k)
        amp = min(land - self.W0, self.W1 - land) * (1 - u) ** 1.5
        return land + amp * np.sin(2 * np.pi * (t - t0) / 1.0)

    def ticks(self, k):
        """Times a pocket edge passes: the wheel's ratchet."""
        out, last = [], 0
        for t in np.arange(SPINS[k][0], SPINS[k][1], 0.004):
            s, _ = self.turned(k, t)
            if int(s) > last:
                out.append(t)
                last = int(s)
        return out

    def die(self, j, k, t):
        """Die j of throw k: (centre, face, tumbling) or None before it is thrown."""
        th, faces = THROWS[k]
        a = t - th
        if a < 0:
            return None
        u = smoothstep(0, 1.0, a)
        p = self.throw_from + (self.dice[j] - self.throw_from) * u
        tumbling = a < 1.8
        face = int(1 + (int(a / 0.11) * 7 + j * 3 + k) % 6) if tumbling else faces[j]
        return p, face, tumbling


def render(G, seed=13):
    S = Stage(G)
    dn = Den(S)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    beats = np.array([b[0] for b in C.beats])
    backs = np.array([b[0] for b in C.beats if b[1] in (1, 3)])
    sung = np.array([n[0] for n in C.tunes()])
    left, right, side = S.run['Left'], S.run['Right'], S.run['Side']
    porchL = S.run['Porch Left']
    NB = 60
    bug_p, bug_v, bug_ph = rng.uniform(0, L, NB), rng.uniform(80, 220, NB) * rng.choice([-1, 1], NB), \
        rng.uniform(0, 2 * np.pi, NB)

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 2.0, t)
        beat = pulse(t, beats, 0.14)
        back = pulse(t, backs, 0.2)
        playing = M['song'] <= t < M['button'] + 0.3
        fr = S.lair(t, lv=up * (0.9 + 0.2 * beat))
        if playing:                                     # the wings flash violet and green on the backbeat
            k = int(np.searchsorted(backs, t, side='right'))
            fr += light(VIOLET if k % 2 else SLIME, 0.5 * back * (S.wings | side))

        # ---- the roulette wheel on the left wing
        wheel = smoothstep(M['wheel'] - 0.5, M['wheel'] + 0.3, t)
        if wheel > 0:
            ks = 1 if t >= SPINS[1][0] else 0
            s, u = dn.turned(ks, t)
            j = np.floor((d - dn.W0) / dn.PW + s)
            fpos = ((d - dn.W0) / dn.PW + s) % 1
            edge = smoothstep(0.0, 0.12, fpos) * smoothstep(1.0, 0.88, fpos)
            onw = left * (d > dn.W0) * (d < dn.W1)
            pocket = np.where(j % 2 == 0, 1.0, 0.0)
            spinning = 0.3 + 0.7 * (1 - u) if SPINS[ks][0] <= t < SPINS[ks][1] else 0.3
            fr = fr * (1 - 0.8 * wheel * onw)[:, None]
            fr += light(LIME, 0.75 * wheel * onw * edge * pocket)
            fr += light(VIOLET, 0.8 * wheel * onw * edge * (1 - pocket))
            fr += light(GOLD, 0.2 * wheel * spinning * left * (1 - edge))
            t0, t1 = SPINS[ks][0], SPINS[ks][1]
            if t0 <= t:
                bp = dn.ball(ks, min(t, t1))
                landed = t >= t1
                lvl = 1.0 if not landed else 0.8 + 0.2 * np.sin(2 * np.pi * 4 * t)
                fr += light(WHITE, lvl * np.exp(-((d - bp) / 6) ** 2))
                if landed and t - t1 < 1.5:             # it drops: the pocket blazes
                    fr += light(LIME, 0.9 * np.exp(-(t - t1) / 0.6) * np.exp(-((d - bp) / dn.PW * 1.6) ** 4))
            # the swipe that starts each spin: a streak down Porch Left into the wheel
            for t0, _, _, _ in SPINS:
                a = t - (t0 - 0.35)
                if 0 <= a < 0.6:
                    front = mid - 80 - (mid - 80 - dn.W1) * smoothstep(0, 0.35, a)
                    fr += light(BUG, 0.9 * np.exp(-a / 0.4) * np.exp(-((d - front) / 50) ** 2))

        # ---- the dice on the right wing
        for k in range(len(THROWS)):
            if k == 0 and t >= THROWS[1][0]:
                continue
            for jd in range(2):
                st = dn.die(jd, k, t)
                if st is None:
                    continue
                p, face, tumbling = st
                a = t - THROWS[k][0]
                half = dn.DH * (0.4 + 0.6 * smoothstep(0, 1.0, a))
                body = S.span(p - half, p + half, 4)
                fr = fr * (1 - 0.9 * body)[:, None]
                fr += light(RED, 0.3 * body)                        # red dice with white pips
                for q in PIPS[face]:
                    pp = p - half + 2 * half * q
                    fr += light(PIP, 1.0 * np.exp(-((d - pp) / 3.5) ** 2) * body)
                if not tumbling and a - 1.8 < 1.0:      # they settle: a flash on the right wing
                    fr += light(LIME, 0.6 * np.exp(-(a - 1.8) / 0.35) * right)

        # ---- Santa tied up on Porch Left, struggling; the fire pit beneath him
        fire = keys(t, [(M['pit'], 0.0), (M['pit'] + 2.0, 0.6), (M['shout'] - 0.2, 1.0), (M['shout'] + 1.5, 0.5),
                        (M['button'], 0.6), (D - 1.0, 0.0)])
        if fire > 0:
            reach = 40 + 160 * fire
            flick = 0.7 + 0.3 * np.sin(19 * t + d / 6) * np.sin(6 * t - d / 11)
            near = smoothstep(reach + 25, reach - 25, np.abs(d - dn.santa)) * porchL
            fr = fr * (1 - 0.8 * near)[:, None]
            fr += light(RED, 0.45 * fire * porchL)
            fr += light(FLAME, 1.0 * fire * near * flick)
            fr += light(GOLD, 0.6 * fire * smoothstep(reach * 0.4 + 20, reach * 0.4 - 20, np.abs(d - dn.santa)) * flick)
        wr = 0.5 + 0.5 * np.sin(2 * np.pi * 2.2 * t)
        jig = 3 * np.sin(2 * np.pi * 3.1 * t)
        fr = S.santa(fr, dn.santa + jig, up * (0.8 + 0.2 * wr), facing=1)
        for o in (-2, 3):                               # the ropes
            kk = S.k(dn.santa + jig) + o
            fr[S.path[kk]] = light(GOLD, 0.35 * up)
        if fire > 0.3:
            fr += light(RED, 0.4 * fire * wr * S.blob(dn.santa, 40))

        # ---- the boogeyman: grows up out of the porch, then dances on every beat
        grow = smoothstep(M['rise'], M['song'], t)
        if grow > 0:
            k = int(np.searchsorted(beats, t, side='right'))
            sway = (10 if k % 2 else -10) * min(1.0, beat) if playing else 0.0
            bow = 1.0
            if t > M['button']:                         # the big bow, then pops back up
                a = t - M['button']
                bow = 1 - 0.4 * smoothstep(0.2, 0.6, a) * (1 - smoothstep(1.2, 1.5, a))
            if M['wheel'] + 6.4 <= t < M['wheel'] + 7.3 or M['dice'] + 2.2 <= t < M['dice'] + 3.4:
                sway = 6 * np.sin(2 * np.pi * 9 * t)    # he laughs till he shakes
            size = (0.4 + 1.1 * grow) * (1 + 0.1 * min(beat, 1.0)) * bow
            lvl = grow * (0.85 + 0.25 * min(beat, 1.0))
            fr += light(BURLAP, (0.3 + 0.25 * min(beat, 1.0)) * lvl * S.porch)
            fr = S.oogie(fr, mid + sway, lvl, t, size)
            # every note he sings throws his light out along the porch
            for jn in np.flatnonzero((sung <= t) & (sung > t - 0.8)):
                b = t - sung[jn]
                front = 80 + 900 * b
                fr += light(BURLAP, 0.7 * np.exp(-b / 0.3) * np.exp(-((np.abs(d - mid) - front) / 60) ** 2))

        # ---- bugs dance the whole roof in the last chorus
        bugs = smoothstep(M['shout'], M['shout'] + 1.0, t) * smoothstep(D, D - 1.5, t)
        if bugs > 0:
            ps = (bug_p + bug_v * (t - M['shout']) + 25 * np.sin(2 * np.pi * 2 * t + bug_ph)) % L
            for pb in ps:
                fr += light(BUG, 0.8 * bugs * (0.6 + 0.4 * beat) * np.exp(-((d - pb) / 6) ** 2))

        # ---- the button: a lime flash over the whole den
        if t >= M['button']:
            a = t - M['button']
            fr += light(LIME, 0.85 * np.exp(-a / 0.35) * np.ones(G.N))
        out[f] = fr * float(smoothstep(D, D - 1.0, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    dn = Den(S)
    B = Band(M_, level=2.4)
    from pixelhome.audio import note
    ride = [('ride', 0, -12, 0.45)]
    parts = {
        'snare': [('ride', 0, -12, 0.45), ('snare', 0, -34, 0.18)], 'tick': ride,
        ('song', 'tune'): [('trombones', 0, 8, 0.8), ('buzz trombone', 0, 0, 0.45)],
        ('song', 'bass'): [('basses pizz', 0, 4, 0.75), ('cellos pizz', 12, -8, 0.4)],
        ('song', 'chord'): [('muted horn', 0, -10, 0.4), ('pizz', 0, -10, 0.3)],
        ('wheel', 'tune'): [('muted horn', 0, 6, 0.7), ('clarinets', 0, -4, 0.45), ('xylo', 12, -10, 0.25)],
        ('wheel', 'bass'): [('basses pizz', 0, 4, 0.75), ('cellos pizz', 12, -8, 0.4)],
        ('wheel', 'chord'): [('muted horn', 0, -12, 0.35)],
        ('dice', 'tune'): [('trombones', 0, 6, 0.7), ('marimba', 12, -6, 0.35)],
        ('dice', 'bass'): [('basses pizz', 0, 4, 0.75), ('cellos pizz', 12, -8, 0.4)],
        ('dice', 'chord'): [('muted horn', 0, -10, 0.4)],
        ('pit', 'tune'): [('buzz trombone', 0, 8, 0.85), ('tuba', -12, 0, 0.5), ('trombones', 0, -2, 0.5)],
        ('pit', 'bass'): [('basses', 0, 0, 0.6), ('cellos', 0, -6, 0.45)],
        ('pit', 'chord'): [('trombones', 0, -12, 0.35), ('violins trem', 12, -14, 0.25)],
        ('pit', 'snare'): [('snare', 0, -14, 0.3)], ('pit', 'tick'): [('ride', 0, -10, 0.45)],
        ('shout', 'tune'): [('trombones', 0, 10, 0.85), ('trumpets', 0, 0, 0.5), ('buzz trombone', 0, 0, 0.45),
                            ('choir', 0, -6, 0.35)],
        ('shout', 'bass'): [('basses pizz', 0, 6, 0.8), ('cellos pizz', 12, -6, 0.45), ('tuba', -12, -10, 0.35)],
        ('shout', 'chord'): [('muted horn', 0, -6, 0.45), ('horns', 0, -16, 0.3)],
    }
    B.perform(C.events, parts)
    # the swung "a" of the ride's spang-a-lang, before each backbeat, and a feathered bass drum
    for t, k, tag in C.beats:
        if k in (0, 2) and tag != 'pit':
            B.hit('ride', t + BEAT * 2 / 3, 70, gain=0.3)
        B.hit('bass drum', t, 60, gain=0.25)
    pL, pR, pC = S.pan(S.at('Left', 0.5)), S.pan(S.at('Right', 0.5)), S.pan(S.mid)
    B.effects([(0, -4), (M['wheel'], 0), (M['pit'], -3), (M['shout'], -7), (M['button'], 0)])
    # the den comes up: a low drone, the prisoner's plaintive carol on an oboe
    B.play('cellos trem', 31, 0.0, 4.5, 60, gain=0.5)
    B.play('ghost', 55, 0.0, 4.5, 60, gain=0.3)
    for i, n in enumerate(('C4', 'F4', 'A4', 'G4')):
        B.play('oboes', note(n) - 1, 0.6 + 0.45 * i, 0.45, 70, S.pan(dn.santa), 0.4)
    # he grows up out of the porch: a buzzing trombone glissando up, a swell
    for i, m in enumerate(range(31, 44, 2)):
        B.play('buzz trombone', m, M['rise'] + 0.25 * i, 0.3, 90 + 3 * i, pC, 0.7)
    B.hit('cymbal swell', M['rise'], 100, gain=0.5)
    B.hit('crash', M['song'], 116, gain=0.5)
    # the wheel: swipe, ratchet ticks slowing, the ball rattling and dropping, his laugh
    for k, (t0, t1, _, _) in enumerate(SPINS):
        B.whoosh(t0 - 0.35, 0.5, False, pan=pL)
        for tk in dn.ticks(k)[::2]:
            B.hit('wood', tk, 80, gain=0.5, pan=pL, fx=True)
        B.hit('claves', t1, 120, gain=0.7, pan=S.pan(dn.landing(k)), fx=True)
        B.hit('triangle', t1 + 0.05, 110, gain=0.4, pan=S.pan(dn.landing(k)))
    def laugh(t0, pan):
        for i, n in enumerate(('G3', 'F3', 'D3', 'Bb2', 'G2')):
            B.play('buzz trombone', note(n), t0 + 0.17 * i, 0.15, 112, pan, 0.8)
            B.play('tuba', note(n) - 12, t0 + 0.17 * i, 0.15, 100, pan, 0.4)
    laugh(SPINS[0][1] + 0.1, pC)
    # the dice: rattle while they tumble, two clacks as they land, a laugh
    for k, (th, _) in enumerate(THROWS):
        B.whoosh(th - 0.1, 0.6, True, pan=pR, gain=0.7)
        for i in range(int(1.8 / 0.09)):
            tt = th + 0.09 * i
            B.hit('claves' if i % 3 else 'wood', tt, 70 + (i * 13) % 40, gain=0.35, pan=pR + 0.15 * np.sin(i), fx=True)
        B.hit('slapstick', th + 1.8, 120, gain=0.6, pan=S.pan(dn.dice[0]))
        B.hit('slapstick', th + 1.86, 120, gain=0.6, pan=S.pan(dn.dice[1]))
    laugh(THROWS[0][0] + 2.0, pC)
    # the pit roars under Santa; timpani roll; he cries out
    B.hit('timpani roll', M['pit'], 100, gain=0.5, pan=S.pan(dn.santa))
    B.fire(M['pit'], M['shout'] + 3.0, level=lambda tt: np.clip(0.4 + 0.25 * (tt - M['pit']), 0.4, 1.0),
           pan=S.pan(dn.santa))
    for i, n in enumerate(('A4', 'G4', 'F4')):
        B.play('oboes', note(n), M['pit'] + 2.5 + 0.5 * i, 0.4, 96, S.pan(dn.santa), 0.5)
    B.hit('crash', M['shout'], 120, gain=0.5)
    # the button: a big stab, a gong, his laugh
    for m, sec, g in ((43, 'trombones', 0.8), (31, 'tuba', 0.8), (55, 'trumpets', 0.5), (46, 'horns', 0.6),
                      (43, 'buzz trombone', 0.6), (31, 'basses', 0.6)):
        B.play(sec, m, M['button'], 0.5, 122, gain=g)
    B.hit('crash', M['button'], 124, gain=0.6)
    B.hit('bass drum', M['button'], 124, gain=0.7)
    laugh(M['button'] + 0.7, pC)
    B.finish()
