"""The Rag Doll's Vision: alone at night, Sally holds a flower that becomes a little Christmas tree and
bursts into flames, and she sings her worry to the sky.

Night falls from the porch outward: the whole house a deep night blue, stars twinkling on every run, crickets.
On Porch Front Sally (blue face, red hair, patchwork) holds a flower, pink petals around a gold heart, that
sways and glows to a harp playing her theme's chords. On a celesta's phrase of the Christmas wonder tune it grows
into a little Christmas tree, a green span widening over the porch, bulbs popping on red, gold and blue with each
note and a star on top. Then it bursts into flames: a white flash, a roar, fire climbing over the porch and a red
glow across the house, then burning down to embers. She sings her worry to the night: her theme in D minor as a
slow, aching song, the oboe first, then the violins, over the harp and low cellos, a choir breathing under the
second half. The house is the night sky: two pale sweeps cross it slowly in opposite directions, stars twinkle,
the burnt tree's embers drift out along the roof and fade, her blue glow swells on every note, and each long
note sends a wave of her blue out to the wings. At the song's peak, the whole house swells blue and violet. At the
end, the last ember floats away and the sky settles, still glowing.

compose() lays the music end to end: render() and score() read its events and marks."""
import numpy as np
from pixelhome.audio import SR
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, FLAME, VIOLET, NIGHT, DUSK, MOON, WHITE,
                                 GOLD, ICE, RED, GREEN, BLUE, PINK, SALLY)

CODE = 'NM11'
TITLE = "Sally's Vision"
KIND = 'show'
DESCRIPTION = ("Alone under the stars, Sally's flower becomes a little Christmas tree over the porch and bursts into "
    'flames. Then she sings her worry to the night, the house a slow, starry sky full of embers.')
VOICEOVER = "Sally had a feeling about Jack's plan. A terrible, fiery feeling."

EMBER = hexc('#ff6010')


def compose():
    C = Chart()
    C.rest(3.0)                                                         # night falls; stars; crickets
    C.mark('flower')
    C.play('sally', style='arp', bars=(0, 4), bpm=72, tune=False, tag='flower')   # the flower, on the harp
    C.mark('tree')
    C.play('wonder', style='arp', bars=(0, 2), bpm=300, tag='tree')     # it becomes a little Christmas tree
    C.mark('flames')
    C.rest(4.5)                                                         # and bursts into flames
    C.mark('song')
    C.play('sally', style='arp', bars=(0, 8), bpm=72, tag='song1')      # her worry, on the oboe
    C.mark('song2')
    C.play('sally', style='arp', bars=(8, 16), bpm=72, tag='song2')     # then the violins
    C.mark('after')
    C.rest(3.5)
    C.mark('end')
    return C


def pad():
    """A choir breathing under the second half of the song: the same chords, held."""
    P = Chart(start=M['song2'])
    P.play('sally', style='hold', bars=(8, 16), bpm=72, tune=False, tag='pad')
    return P


C = compose()
D = C.marks['end']
M = C.marks
SONG = C.tunes('song1') + C.tunes('song2')
TREE_NOTES = [n[0] for n in C.tunes('tree')]


def embers(S):
    """The burnt tree's embers: (start, side, speed, life, colour index), thick at first, then fewer."""
    rng = np.random.default_rng(1111)
    out = []
    t = M['flames'] + 0.6
    while t < M['after'] - 2.0:
        out.append((t, rng.choice([-1, 1]), rng.uniform(110, 300), rng.uniform(3.0, 8.0), int(rng.integers(2))))
        u = (t - M['flames']) / (M['after'] - M['flames'])
        t += 0.12 + 1.2 * u
    out.append((M['after'] - 2.0, 1, 160, 5.0, 0))                      # the last one
    return out


def render(G, seed=11):
    S = Stage(G)
    d, mid, L = S.d, S.mid, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    p_doll, p_tree = mid - 45, mid + 25
    star_on = rng.random(G.N) < 0.14
    star_ph = rng.uniform(0, 2 * np.pi, G.N)
    star_rate = rng.uniform(0.6, 1.6, G.N)
    arp = [e[0] for e in C.events if e[4] == 'arp' and e[5] == 'flower']
    song_t = np.array([n[0] for n in SONG])
    song_d = np.array([n[1] for n in SONG])
    song_m = np.array([n[2] for n in SONG])
    longs = song_t[song_d > 1.2]
    peaks = song_t[song_m >= 73]
    emb = embers(S)
    bulbs = np.array([RED, GOLD, BLUE])

    for f in range(F):
        t = f * DT
        fall = smoothstep(0, 3.0, t)
        reach = 200 + 1400 * fall
        sky = smoothstep(reach + 150, reach - 150, np.abs(d - mid))
        end = 1.0 - 0.35 * smoothstep(M['after'], D, t)
        # the night sky: deep blue, two slow pale sweeps crossing, stars twinkling
        fr = light(NIGHT, 0.4 * sky * end * np.ones(G.N))
        w1 = L * ((t / 11.0) % 1.0)
        w2 = L * (1 - (t / 15.0) % 1.0)
        fr += light(MOON, 0.45 * sky * end * np.exp(-((d - w1) / 260) ** 2))
        fr += light(VIOLET, 0.45 * sky * end * np.exp(-((d - w2) / 300) ** 2))
        tw = np.maximum(0, np.sin(star_rate * t + star_ph)) ** 6
        fr += light(WHITE, 0.6 * sky * star_on * tw)

        # the flower, swaying in her hands, petals glinting with the harp
        if M['flower'] - 1.0 <= t < M['tree'] + 1.0:
            lv = smoothstep(M['flower'] - 1.0, M['flower'] + 0.5, t) * smoothstep(M['tree'] + 1.0, M['tree'], t)
            sw = p_tree + 5 * np.sin(2 * np.pi * 0.4 * t)
            g = pulse(t, arp, 0.4)
            grow = smoothstep(M['flower'], M['tree'], t)
            fr = S.sprite(fr, sw, [(2, PINK, 1.0), (1, GOLD, 1.0), (0, PINK, 1.0), (-1, GREEN, 0.7), (-2, GREEN, 0.6)],
                          lv, -1)
            fr += light(PINK, lv * (0.35 + 0.25 * grow + 0.15 * g) * S.blob(sw, 50 + 60 * grow))
            fr += light(PINK, lv * 0.25 * grow * S.porch)
        # the little Christmas tree: a green span widening, bulbs popping on with each note, a star on top
        if M['tree'] <= t < M['flames'] + 1.2:
            g = smoothstep(M['tree'], M['flames'] - 0.3, t)
            burnt = smoothstep(M['flames'] + 0.1, M['flames'] + 1.2, t)
            half = 14 + 90 * g
            span = S.span(p_tree - half, p_tree + half)
            fr += light(GREEN, 0.9 * (1 - burnt) * span)
            k = int(np.searchsorted(TREE_NOTES, t, side='right'))
            lit = (G.pi % 12 < k) & (G.pi % 3 == 0)
            fr += light(bulbs[G.pi % 3 * 0 + (G.pi // 3) % 3], 1.0 * (1 - burnt) * (span > 0.5) * lit)
            fr += light(GOLD, (1 - burnt) * (1.0 * S.blob(p_tree, 6) + 0.4 * S.blob(p_tree, 30)))
            fr += light(WHITE, 0.5 * (1 - burnt) * pulse(t, TREE_NOTES, 0.2) * S.blob(p_tree, 8))
            fr += S.snowfall(t, 0.6 * (1 - burnt)) * sky[:, None]
        # the flames: a flash, fire climbing over the porch, a red glow across the house, then embers
        if M['flames'] <= t < M['song'] + 2.0:
            a = t - M['flames']
            if a < 0.4:
                fr += light(WHITE, 1.0 * np.exp(-a / 0.1) * S.porch)
            h = smoothstep(0, 1.0, a) * (1 - smoothstep(1.8, 5.5, a))
            rch = 60 + 420 * h
            flick = 0.7 + 0.3 * np.sin(19 * t + d / 6) * np.sin(7 * t - d / 11)
            core = smoothstep(rch + 40, rch - 40, np.abs(d - p_tree))
            fr = fr * (1 - 0.6 * core[:, None]) * (1 - 0.6 * h)
            fr += light(FLAME, 1.1 * h * core * flick)
            fr += light(GOLD, 0.8 * h * smoothstep(rch * 0.45 + 20, rch * 0.45 - 20, np.abs(d - p_tree)) * flick)
            fr += light(RED, 0.55 * h * np.ones(G.N))
        for t0, sd, sp, life, c in emb:
            a = t - t0
            if 0 <= a < life:
                p = p_tree + sd * sp * a + 20 * np.sin(1.3 * a + t0)
                v = (1 - a / life) * (0.7 + 0.3 * np.sin(13 * t + t0 * 7))
                fr += light(EMBER if c else GOLD, 1.0 * v * S.blob(p, 8))

        # her song: her blue glow swells on every note, long notes send waves out, the peak swells the house
        if t >= M['song'] - 0.5:
            lv = smoothstep(M['song'] - 0.5, M['song'] + 1.0, t) * end
            nt = pulse(t, song_t, 0.7)
            fr += light(SALLY, lv * (0.3 + 0.3 * min(nt, 1.2)) * S.porch * (0.6 + 0.4 * S.blob(p_doll, 300)))
            for t0 in longs[(longs <= t) & (longs > t - 3.0)]:
                b = t - t0
                fr += light(SALLY, 0.8 * lv * np.exp(-b / 1.4) * np.exp(-((np.abs(d - p_doll) - 500 * b) / 180) ** 2))
            pk = pulse(t, peaks, 1.4)
            fr += light(SALLY, 0.6 * lv * min(pk, 1.0) * np.ones(G.N))
            fr += light(VIOLET, 0.5 * lv * min(pk, 1.0) * (S.wings | S.run['Side']))

        # Sally: she shies back from the flames
        back = 30 * smoothstep(M['flames'], M['flames'] + 0.3, t) * (1 - smoothstep(M['song'], M['song'] + 3, t))
        fr = S.sally(fr, p_doll - back, smoothstep(1.5, 3.0, t), facing=1)
        fr += light(SALLY, 0.35 * smoothstep(1.5, 3.0, t) * S.blob(p_doll - back - 20, 50))
        out[f] = fr * float(smoothstep(D + 0.2, D - 1.8, t))
    return np.clip(out, 0, 1)


def _crickets(B, t0, t1, seed=3):
    rng = np.random.default_rng(seed)
    t = t0
    while t < t1:
        n = int(0.05 * SR)
        tt = np.arange(n) / SR
        f = rng.uniform(4200, 4800)
        chirp = np.sin(2 * np.pi * f * tt) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 60 * tt))) * np.hanning(n)
        pan = rng.uniform(-0.9, 0.9)
        for k in range(3):
            B._sfx(chirp, t + 0.07 * k, 0.05, pan)
        t += rng.uniform(0.3, 0.9)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=4.2)
    p_tree = S.mid + 25
    parts = {
        ('flower', 'arp'): [('harp', 0, 0, 0.6)],
        ('flower', 'pedal'): [('cellos', 0, -14, 0.4)],
        ('tree', 'tune'): [('celesta', 12, 0, 0.6), ('glock', 0, -10, 0.35)],
        ('tree', 'arp'): [('harp', 12, -6, 0.4)],
        ('tree', 'pedal'): [('violas', 0, -14, 0.35)],
        ('song1', 'tune'): [('oboes', 0, 4, 0.9)],
        ('song1', 'arp'): [('harp', 0, -2, 0.85)],
        ('song1', 'pedal'): [('cellos', 0, -10, 0.5)],
        ('song2', 'tune'): [('violins', 0, 6, 0.8), ('oboes', 0, -10, 0.3)],
        ('song2', 'arp'): [('harp', 0, 0, 0.85)],
        ('song2', 'pedal'): [('cellos', 0, -6, 0.55), ('basses', 0, -12, 0.35)],
        ('pad', 'hold'): [('choir', 0, -16, 0.2), ('violas', 0, -16, 0.3)],
        ('pad', 'pedal'): [],
    }
    B.perform(C.events, parts)
    B.perform(pad().events, parts)
    B.effects([(0, -8), (M['flames'] - 0.2, 2), (M['song'], -10), (M['after'], -10)])
    _crickets(B, 0.5, M['flames'])
    _crickets(B, M['after'] - 4, D, seed=4)
    # night falls: a low hush
    B.play('ghost', 50, 0.0, 3.0, 60, gain=0.4)
    # the tree: a bell tree and a breath of sleigh bells
    B.hit('bell tree', M['tree'], 90, gain=0.4, pan=S.pan(p_tree))
    B.sleigh_bells(M['tree'] + 0.2, M['flames'] - 0.2, beat=0.15, pan=S.pan(p_tree), v=70, gain=0.4)
    # the flames: a whoosh, a boom, the roar, then embers crackling quietly under the start of the song
    tf = M['flames']
    B.whoosh(tf - 0.3, 0.6, up=True, pan=S.pan(p_tree), gain=0.8)
    B.boom(tf, pan=S.pan(p_tree), gain=0.7)
    B.hit('crash', tf, 110, gain=0.4)
    B.fire(tf, M['song'] + 1.0, level=lambda tt: np.clip(1.0 - 0.18 * (tt - tf), 0.15, 1.0), pan=S.pan(p_tree))
    B.fire(M['song'], M['song'] + 9.0, level=0.12, pan=S.pan(p_tree), crackle=4.0, seed=8)
    for m in (38, 44, 50, 53):                                          # a diminished stab, held and fading
        B.play('cellos trem' if m < 48 else 'violas trem', m, tf, 3.5, 100, gain=0.5)
    B.play('horns', 56, tf, 2.0, 100, gain=0.5)
    B.play('horns', 50, tf, 2.0, 100, gain=0.5)
    B.hit('timpani roll', tf + 0.1, 100, pitch=-5, gain=0.5)
    B.play('ghost', 45, tf + 1.0, 3.5, 70, gain=0.5)
    # the end: a last harp chord
    for k, m in enumerate((50, 57, 62, 65, 69)):
        B.play('harp', m, M['after'] + 0.1 + 0.12 * k, 2.5, 70, gain=0.5)
    B.finish()
