"""Snow on Halloween Town: Santa forgives, flies off to put Christmas right, and snow falls on Halloween Town.

Halloween Town at night, violet with orange windows. On the porch the Pumpkin King and Santa face each other; the
king bows his head on each downbeat of his theme, low and sorry. Santa's carol answers on warm brass: Santa
glows red and gold, leaps into his own sleigh and flies off along the right wing and out at its end, sleigh bells
jingling; then streaks back in from that end and over the whole house, a red and gold blaze trailing sparkle,
and out along Side, and where he passed the first snow begins to fall. To the wonder theme on celesta, white
flakes twinkle down on the town for the first time, a glint on every note. Then the citizens play in it, the
town's march and the wonder theme braided in turns: snowballs fly from run to run and splat white on the march's
downbeats, and on the wonder's phrases the three troublemakers ride a sled from the porch down a wing in a spray
of snow. The violet and orange is gradually dusted white, and the town sparkles to the last chord.

compose() lays the music end to end (pixelhome/nightmare.py); render() and score() both read its events."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (Chart, Band, Stage, pulse, ORANGE, PUMPKIN, VIOLET, WHITE, GOLD, ICE, RED, MOON,
                                 WARM, DUSK, BONE)

CODE = 'NM19'
TITLE = 'Snow on Halloween Town'
KIND = 'show'
DESCRIPTION = ('The Pumpkin King says sorry and Santa streaks off over the house in his red and gold sleigh. Behind '
               'him, for the first time, snow falls on Halloween Town: snowballs fly, a sled races down a wing, and '
               'the violet and orange turns white.')
VOICEOVER = ('Christmas was put right that night. And then, for the very first time, it began to snow.')

FROST = hexc('#e8f0ff')


def compose():
    C = Chart()
    C.rest(1.0)
    C.mark('sorry')
    C.play('king', style='hold', bars=(12, 16), bpm=84, tag='sorry')        # the king says sorry
    C.mark('santa')
    C.play('santa', style='march', bars=(0, 8), bpm=112, tag='santa')       # Santa flies off to put it right
    C.mark('snow')
    C.play('wonder', style='arp', bars=(0, 8), bpm=300, tag='snow')         # the first snow
    C.mark('play1')
    C.play('town', style='march', bars=(0, 4), bpm=132, tag='play1')        # snowballs
    C.mark('play2')
    C.play('wonder', style='gallop', bars=(0, 4), bpm=330, tag='play2')     # the sled
    C.mark('play3')
    C.play('town', style='march', bars=(4, 8), bpm=132, tag='play3')
    C.mark('play4')
    C.play('wonder', style='gallop', bars=(4, 8), bpm=330, tag='play4')
    C.rest(2.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks


def sleigh_path(S):
    """Santa's sleigh: off the porch along the right wing and out its end, then back in from there over the house."""
    t0, t1 = M['santa'], M['snow']
    h = (t0 + t1) / 2
    out = [(t0 + 2.0, S.mid + 60), (h, S.L + 200)]
    back = [(h + 0.6, S.L + 60), (t1 + 0.6, -260)]
    return out, back


def santa_sleigh(S, fr, p, facing, t, lvl=1.0):
    """Santa's own sleigh: four pairs of gold reindeer, the red sleigh with gold trim, Santa in it."""
    for i in range(4):
        leap = 0.75 + 0.25 * np.sin(2 * np.pi * (2.5 * t + i / 4))
        fr = S.sprite(fr, p - facing * i * 4 * 4.5, [(1, WARM, 1.0 * leap), (0, GOLD, 0.7 * leap), (-1, WARM, 0.5)],
                      lvl, facing)
    x = p - facing * 18 * 4.5
    fr = S.sprite(fr, x, [(2, GOLD, 1.0), (1, RED, 1.0), (0, RED, 1.0), (-1, RED, 1.0), (-2, GOLD, 1.0)], lvl, facing)
    fr = S.santa(fr, x - facing * 5 * 4.5, lvl, facing)
    fr += light(RED, 0.4 * lvl * S.blob(x, 70))
    fr += light(GOLD, 0.3 * lvl * S.blob(p, 60))
    return fr


def render(G, seed=19):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    rng = np.random.default_rng(seed)
    t_so, t_sa, t_sn, t_end = M['sorry'], M['santa'], M['snow'], M['end']
    out_p, back_p = sleigh_path(S)
    t_back0, t_back1 = back_p[0][0], back_p[1][0]
    sorry_downs = np.array(C.downbeats('sorry'))
    santa_beats = np.array([b[0] for b in C.beats if b[2] == 'santa'])
    glints = [e[0] for e in C.events if e[5] in ('snow', 'play2', 'play4') and e[4] in ('arp', 'tune', 'chord')]
    glint_p = rng.uniform(0, S.L, len(glints))
    glints = np.array(glints)
    # snowballs on the march's downbeats: (t, from, to)
    spots = [S.at(r, u) for r, u in (('Left', 0.3), ('Porch Left', 0.4), ('Porch Front', 0.5), ('Porch Right', 0.5),
                                     ('Right', 0.4), ('Right', 0.8), ('Left', 0.7))]
    balls = []
    for k, tb in enumerate(C.downbeats('play1') + C.downbeats('play3')):
        for j in range(2 if k >= 4 else 1):
            a, b = rng.choice(len(spots), 2, replace=False)
            balls.append((tb + 0.25 * j, spots[a], spots[b]))
    sleds = [(M['play2'], S.at('Porch Left', 0.9), S.at('Left', 0.05)),
             (M['play4'], S.at('Porch Right', 0.1), S.L + 30)]
    snow_downs = np.array(C.downbeats('snow') + C.downbeats('play2') + C.downbeats('play4'))
    beats_play = np.array([b[0] for b in C.beats if b[2].startswith('play')])

    for f in range(F):
        t = f * DT
        up = smoothstep(0, 1.5, t)
        snow = smoothstep(t_back0 + 1.0, t_sn + 2.0, t)                       # snow falling
        white = 0.55 * smoothstep(t_sn, t_end - 2.0, t)                       # the town dusted white
        town = S.town(t, lv=up * (1.35 + 0.25 * pulse(t, beats_play, 0.2)), mist=0.5 * (1 - snow))
        fr = town * (1 - 0.55 * white) + light(FROST, 0.55 * white * np.ones(G.N))
        fr += S.snowfall(t, amount=snow * (0.8 + 0.2 * white))
        # gusts of snow drifting along the roof on the wonder theme's downbeats
        for tb in snow_downs[(snow_downs <= t) & (snow_downs > t - 3)]:
            a = t - tb
            fr += light(ICE, 0.45 * np.exp(-a / 1.0) * np.exp(-((d - (S.L - 900 * a)) / 160) ** 2))
        # glints: a sparkle on every note of the wonder theme
        for gt, gp in zip(glints[(glints <= t) & (glints > t - 0.5)], glint_p[(glints <= t) & (glints > t - 0.5)]):
            a = t - gt
            fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * S.blob(gp, 10 + 30 * a))
        # the king and Santa on the porch: he bows on each downbeat, Santa glows, laughs, leaps into his sleigh
        jl = up * (1.0 - smoothstep(t_sn, t_sn + 2.0, t))
        if jl > 0:
            bow = 1.0 - 0.45 * pulse(t, sorry_downs, 0.6)
            fr = S.jack(fr, mid - 70, jl * bow, facing=1, glow=0.35)
        if t < t_sa + 2.4:
            lv = 1.0 - smoothstep(t_sa + 1.6, t_sa + 2.4, t)
            laugh = pulse(t, santa_beats, 0.2) if t >= t_sa else 0.0
            fr += light(RED, (0.4 + 0.3 * laugh) * up * lv * S.blob(mid + 70, 60))
            fr = S.santa(fr, mid + 70, up * lv, facing=-1)
            fr += light(RED, 0.35 * up * lv * (S.run['Porch Right'] | S.run['Right']))
            fr += light(MOON, 0.3 * up * lv * (1 - smoothstep(t_sa - 1, t_sa + 1, t)) *
                        (S.run['Porch Left'] | S.run['Left']))
            # forgiven: a gold wave out from Santa as his carol starts
            if t >= t_sa:
                a = t - t_sa
                fr += light(GOLD, 0.8 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - mid - 70) - 700 * a) / 90) ** 2))
        # the sleigh: off along the right wing, then back over the whole house trailing sparkle and snow
        if out_p[0][0] - 0.4 <= t < out_p[1][0]:
            p = keys(t, [(out_p[0][0] - 0.4, mid + 70)] + out_p)
            fr += light(GOLD, 0.5 * S.span(mid, p) * np.exp(-np.abs(d - p) / 150))
            fr = santa_sleigh(S, fr, p, 1, t)
        if t_back0 <= t < t_back1:
            u = (t - t_back0) / (t_back1 - t_back0)
            p = back_p[0][1] + (back_p[1][1] - back_p[0][1]) * u
            behind = d - p
            wake = (behind > 0) * np.exp(-np.clip(behind, 0, None) / 300)
            fr += light(GOLD, 0.8 * wake * (0.6 + 0.4 * np.sin(d / 5 + 30 * t)))
            fr += light(RED, 0.3 * wake)
            fr = santa_sleigh(S, fr, p, -1, t)
        # snowballs: flying from run to run, splatting white
        for tb, pa, pb in balls:
            a = t - tb
            if 0 <= a < 0.7:
                pp = pa + (pb - pa) * smoothstep(0, 0.7, a)
                fr += light(WHITE, 1.0 * S.blob(pp, 18))
                fr += light(ICE, 0.4 * S.blob(pp, 50))
            elif 0.7 <= a < 1.6:
                b = a - 0.7
                fr += light(WHITE, 1.0 * np.exp(-b / 0.25) * S.blob(pb, 30 + 200 * b))
                fr += light(ICE, 0.5 * np.exp(-b / 0.4) * S.blob(pb, 60))
        # the sled: the three troublemakers riding down a wing in a spray of snow
        for ts, pa, pb in sleds:
            a = t - ts
            dur = 3.6
            if 0 <= a < dur + 0.5:
                u = np.clip(a / dur, 0, 1) ** 1.6
                pp = pa + (pb - pa) * u
                fc = 1 if pb > pa else -1
                spray = (-fc * (d - pp) > 0) * np.exp(-np.abs(d - pp) / 120) * (a < dur)
                fr += light(WHITE, 0.9 * spray * (0.6 + 0.4 * np.sin(d / 3 + 40 * t)))
                fr += light(ICE, 0.8 * S.blob(pp, 90) * (a < dur))
                fr = S.trio(fr, pp, 1.3 if a < dur else 1.3 * (dur + 0.5 - a) / 0.5, facing=fc, gap=4, t=t, bounce=1.0)
        # the last chord: a white sparkle over the whole town
        if t >= t_end - 2.5:
            a = t - (t_end - 2.5)
            fr += light(WHITE, 0.5 * np.exp(-a / 0.3) * np.ones(G.N))
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=2.7)
    parts = {
        ('sorry', 'tune'): [('clarinets', 0, 0, 0.6), ('cellos', -12, -8, 0.4)],
        ('sorry', 'hold'): [('choir', 0, -24, 0.35), ('violas', 0, -16, 0.35)],
        ('sorry', 'pedal'): [('basses', -12, -10, 0.45)],
        ('santa', 'tune'): [('horns', 0, 6, 0.8), ('trumpets', 0, -4, 0.45), ('violins', 12, -6, 0.45)],
        ('santa', 'bass'): [('tuba', -12, 0, 0.65), ('basses pizz', 0, -6, 0.5)],
        ('santa', 'chord'): [('trombones', 0, -12, 0.35), ('pizz', 0, -6, 0.4)],
        ('santa', 'snare'): [('sleigh', 0, -10, 0.5)],
        ('santa', 'tick'): [('sleigh', 0, -20, 0.3)],
        ('snow', 'tune'): [('celesta', 12, -2, 0.7), ('flutes', 12, -6, 0.5)],
        ('snow', 'arp'): [('harp', 0, -6, 0.5), ('glock', 12, -16, 0.25)],
        ('snow', 'pedal'): [('violas', 0, -16, 0.4), ('cellos', 0, -14, 0.4)],
        ('play1', 'tune'): [('clarinets', 0, 4, 0.6), ('xylo', 12, -2, 0.45), ('violins', 12, -6, 0.4)],
        ('play3', 'tune'): [('clarinets', 0, 4, 0.6), ('xylo', 12, -2, 0.45), ('violins', 12, -6, 0.4),
                            ('horns', 0, -4, 0.5)],
        ('play1', 'bass'): [('tuba', -12, 0, 0.6), ('basses pizz', 0, -6, 0.5)],
        ('play3', 'bass'): [('tuba', -12, 0, 0.6), ('basses pizz', 0, -6, 0.5)],
        ('play1', 'chord'): [('pizz', 0, -2, 0.45)],
        ('play3', 'chord'): [('pizz', 0, -2, 0.45), ('horns', 0, -14, 0.3)],
        ('play1', 'snare'): [('tambourine', 0, -12, 0.35)],
        ('play3', 'snare'): [('tambourine', 0, -12, 0.35)],
        ('play2', 'tune'): [('celesta', 12, -2, 0.55), ('flutes', 12, -6, 0.45), ('violins', 12, -10, 0.35)],
        ('play4', 'tune'): [('celesta', 12, -2, 0.55), ('flutes', 12, -6, 0.45), ('violins', 12, -6, 0.45),
                            ('choir', 0, -10, 0.5)],
        ('play2', 'bass'): [('cellos', 0, -6, 0.5)],
        ('play4', 'bass'): [('cellos', 0, -6, 0.5), ('tuba', -12, -6, 0.4)],
        ('play2', 'chord'): [('harp', 0, -6, 0.45)],
        ('play4', 'chord'): [('harp', 0, -6, 0.45), ('violas', 0, -12, 0.35)],
        ('play2', 'tick'): [('sleigh', 0, -14, 0.35)],
        ('play4', 'tick'): [('sleigh', 0, -14, 0.35)],
    }
    B.perform(C.events, parts)
    out_p, back_p = sleigh_path(S)
    t_end = M['end']
    # the last chord: G major, the whole band and a cymbal
    for m, sec in ((43, 'tuba'), (55, 'horns'), (59, 'horns'), (62, 'trumpets'), (67, 'violins'), (71, 'violins')):
        B.play(sec, m, t_end - 2.5, 2.2, 105, gain=0.55)
    B.play('choir', 67, t_end - 2.5, 2.2, 90, gain=0.4)
    B.play('celesta', 79, t_end - 2.5, 1.5, 90, gain=0.4)
    B.hit('crash', t_end - 2.5, 112, gain=0.5)
    B.hit('triangle', t_end - 2.5, 110, gain=0.5)
    B.hit('cymbal swell', M['snow'] - 1.5, 90, gain=0.4)
    B.hit('triangle', M['snow'], 100, gain=0.4)
    # the stage: sleigh bells and whooshes with the sleigh, snowballs and the sled
    B.effects([(0, -6), (M['santa'], -4), (back_p[0][0], -1), (M['snow'], -8), (M['play1'], -5)])
    pan_out = lambda tt: S.pan(keys(tt, out_p))
    B.sleigh_bells(out_p[0][0] - 0.4, out_p[1][0], beat=0.22, pan=pan_out, v=95)
    pan_back = lambda tt: S.pan(back_p[0][1] + (back_p[1][1] - back_p[0][1]) *
                                np.clip((tt - back_p[0][0]) / (back_p[1][0] - back_p[0][0]), 0, 1))
    B.sleigh_bells(back_p[0][0], back_p[1][0], beat=0.18, pan=pan_back, v=105)
    B.whoosh(back_p[0][0], seconds=1.4, up=True, pan=0.8, gain=0.8)
    B.whoosh(back_p[0][0] + 1.6, seconds=2.0, up=False, pan=-0.6, gain=0.7)
    rng = np.random.default_rng(19)
    for k, tb in enumerate(C.downbeats('play1') + C.downbeats('play3')):
        for j in range(2 if k >= 4 else 1):
            pp = float(rng.uniform(-0.8, 0.8))
            B.whoosh(tb + 0.25 * j, seconds=0.6, up=False, pan=pp, gain=0.3)
            B.hit('hoof soft', tb + 0.25 * j + 0.7, 110, gain=0.6, pan=-pp, fx=True)
    for ts, pp in ((M['play2'], -0.5), (M['play4'], 0.8)):
        B.whoosh(ts, seconds=3.6, up=False, pan=pp, gain=0.6)
    B.finish()
