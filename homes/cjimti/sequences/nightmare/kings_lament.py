"""The King's Lament: after the party the Pumpkin King slips away alone and climbs the spiral hill.

The last of the party dies away on the porch (a few orange and green sparks, the town's windows going out) and the
graveyard comes up in moonlight: night blue on every run, the big moon over the porch, grey headstones and a slow
mist on the wings, and the spiral hill curling on Left, pale stripes winding in towards its top. The Pumpkin King
stands in the middle of the porch, then trudges out along Porch Left and onto Left with Zero trailing
behind him, nose glowing. His lament plays in A minor, slowly, on a lone oboe over a harp; every note he sighs
sends a pale ripple out from him along the roof. At the foot of the hill the strings take the tune and he climbs,
slowly, while the curl turns under him. At the top he turns to the moon and the lament swells on the whole band:
the moon grows until it fills the porch, and on the last note the hill uncurls flat under his feet, a bright
line unrolling from where he stands to both ends of the house. He is left on the flat hill under the moon, and
the dog comes up to him with a small woof.

compose() lays the music end to end (pixelhome/nightmare.py): render() and score() both read its events, so the
ripples, the climb and the uncurling land on the music."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.nightmare import (drift, Chart, Band, Stage, pulse, ORANGE, SLIME, PUMPKIN, MOON, ICE, NIGHT, GREY, WHITE,
                                 VIOLET, DUSK)

CODE = 'NM02'
TITLE = "The King's Lament"
KIND = 'show'
DESCRIPTION = ('Jack slips away from the party and trudges out along the left wing, Zero behind him, to climb Spiral '
    'Hill under the moon. At his saddest note the hill unrolls flat.')
VOICEOVER = ('The party is over, and Jack is tired of being the Pumpkin King. He walks out alone, to the hill where '
    'nobody follows.')

HILL = hexc('#5a8cff')
PALE = hexc('#b8d0ff')


def compose():
    C = Chart()
    C.rest(3.0)                                             # the party dies away; the graveyard comes up
    C.mark('solo')
    C.play('king', style='arp', bars=(0, 8), bpm=72, tag='solo')        # a lone oboe; he walks out
    C.mark('climb')
    C.play('king', style='waltz', bars=(8, 16), bpm=76, tag='climb')    # the strings take it; he climbs
    C.mark('swell')
    C.play('king', style='hold', bars=(12, 16), bpm=64, tag='swell')    # at the top, the whole band
    C.rest(4.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
T_FLAT = C.tunes('swell')[-1][0]                            # the last note: the hill uncurls


def hill_at(S):
    return S.at('Left', 0.4)


def jack_path(S, t):
    """Where Jack is, and which way he faces."""
    h = hill_at(S)
    foot = S.at('Left', 0.95)
    p = keys(t, [(0, S.mid), (M['solo'] + 1.0, S.mid), (M['climb'] - 0.5, foot), (M['swell'] - 1.0, h)])
    facing = -1 if t < M['swell'] - 0.6 else 1              # he turns to the moon at the top
    return float(p), facing


def render(G, seed=2):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    h = hill_at(S)
    sighs = np.array([n[0] for n in C.tunes()])
    beats = np.array([b[0] for b in C.beats])
    rng = np.random.default_rng(seed)
    mist_off = rng.uniform(0, 1000)
    wings = S.wings | S.run['Side']
    party = [(0.1, 1.0, mid - 120), (0.7, 0.9, mid + 140), (1.4, 0.8, S.at('Left', 0.6)), (2.0, 0.8, S.at('Right', 0.4)), (2.7, 0.6, mid)]
    dog_p = S.at('Porch Front', 0.75)

    for f in range(F):
        t = f * DT
        p, facing = jack_path(S, t)
        swell = smoothstep(M['swell'], T_FLAT, t)
        flat = smoothstep(T_FLAT, T_FLAT + 2.5, t)
        up = smoothstep(0.5, 3.5, t)

        # the graveyard in moonlight (the hill is drawn below, so it can uncurl)
        fr = S.graveyard(t, lv=0.25 + 0.85 * up, moon=1.0 + 0.6 * swell, hill=0.0)
        m = 0.5 + 0.5 * drift(9, d - 30 * t + mist_off + 1e5, 160.0)
        fr += light(GREY, 0.5 * up * np.clip(m - 0.2, 0, 1) * wings)
        beams = 0.5 + 0.5 * np.sin(d / 70.0 - 0.6 * t) * np.sin(d / 190.0 + 0.25 * t)
        fr += light(MOON, (0.22 + 0.3 * swell) * up * beams ** 3 * (S.run['Right'] | S.run['Side']))
        fr += light(MOON, 0.75 * swell * S.blob(mid, 160 + 260 * swell))      # the moon grows as he sings
        fr += light(PALE, 0.35 * swell * S.porch)

        # what is left of the party: the town fading on the porch, a last few sparks
        gone = 1 - smoothstep(0.5, 4.0, t)
        if gone > 0:
            fr += S.town(t, lv=gone) * (S.porch | S.wings)[:, None]
            fr += S.burst(party, t, seed=3, n=12, colors=(ORANGE, SLIME, PUMPKIN))

        # the spiral hill: stripes winding in to its top; it turns while he climbs and unrolls on the last note
        r = np.abs(d - h)
        wind = (1 - flat) * 7.0 * np.log1p(r / 25.0)
        spin = 2.0 * t + 6.0 * smoothstep(M['climb'], M['swell'], t)
        curl = 0.5 + 0.5 * np.cos(wind - spin * (1 - flat))
        width = 175 + 900 * flat
        hump = smoothstep(width + 40, width - 40, r) * (S.run['Left'] + flat * ~S.run['Left'])
        fr += light(HILL, 0.8 * up * hump * (0.3 + 0.7 * curl) * (1 - 0.5 * flat))
        fr += light(PALE, 0.6 * up * hump * curl ** 4 * (1 - flat))

        # the uncurling: a bright line unrolls from his feet to both ends of the house, then settles
        if t >= T_FLAT:
            a = t - T_FLAT
            reach = 2600 * smoothstep(0, 2.2, a)
            front = np.exp(-((r - reach) / 40) ** 2)
            fr += light(WHITE, 0.95 * np.exp(-a / 1.2) * front)
            fr += light(PALE, (0.55 * np.exp(-a / 1.5) + 0.2) * (r < reach))
            if a < 0.5:
                fr += light(WHITE, 0.7 * np.exp(-a / 0.12) * S.blob(p, 120))

        # every sigh of the lament: a pale ripple out from him along the roof
        for t0 in sighs[(sighs <= t) & (sighs > t - 2.0)]:
            a = t - t0
            big = 1.0 + 0.6 * (t0 >= M['climb']) + 0.6 * (t0 >= M['swell'])
            fr += light(MOON, 0.45 * big * np.exp(-a / 0.7) * np.exp(-((np.abs(d - p) - 320 * a) / (50 + 40 * a)) ** 2))

        # his run in his own pale violet, brighter as the lament grows; a beat pulse under the swell
        on = S.run_at(p)
        beat = pulse(t, beats, 0.3) if t >= M['climb'] else 0.0
        fr += light(DUSK, (0.35 + 0.3 * swell + 0.1 * beat) * up * on)
        if M['swell'] <= t < T_FLAT + 1:
            fr += light(VIOLET, 0.25 * beat * wings)

        # Zero trails him out, waits at the foot of the hill, and comes up to him at the end
        if t < M['solo'] + 1.0:
            dp, dfac = dog_p, -1
        elif t < M['swell']:
            dp, dfac = min(p + 85 + 10 * np.sin(2 * np.pi * 0.7 * t), S.at('Left', 0.98) + 60), -1
            dp = max(dp, p + 60)
        else:
            dp, dfac = keys(t, [(M['swell'], p + 85), (T_FLAT + 1.5, p + 85), (D - 2.0, p + 22)]), -1
        dog_lvl = smoothstep(0.8, 2.5, t)
        fr = S.zero(fr, float(dp), 0.9 * dog_lvl, dfac, t, nose=1.0)

        # Jack himself
        glow = 0.4 + 0.5 * swell + 0.4 * pulse(t, sighs, 0.25) * (t >= M['swell'])
        fr = S.jack(fr, p, smoothstep(0, 1.0, t), facing=facing, glow=glow)
        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def gliss(B, section, t0, notes, step, v=88, gain=0.6, pan=None):
    """A run of notes step seconds apart (a harp sweep)."""
    for i, m in enumerate(notes):
        B.play(section, m, t0 + i * step, 0.8, v, pan, gain)


def score(M_, G):
    S = Stage(G)
    B = Band(M_, level=3.4)
    hill = S.pan(hill_at(S))
    parts = {
        ('solo', 'tune'): [('oboes', 0, 6, 0.85)],
        ('solo', 'arp'): [('harp', 0, -4, 0.5)],
        ('solo', 'pedal'): [('cellos', 0, -14, 0.4)],
        ('climb', 'tune'): [('violins', 0, 4, 0.8), ('violas', -12, -6, 0.45)],
        ('climb', 'bass'): [('cellos', 0, -4, 0.55), ('basses', 0, -10, 0.35)],
        ('climb', 'chord'): [('violas', 0, -16, 0.3), ('harp', 0, -14, 0.3)],
        ('swell', 'tune'): [('violins', 0, 10, 0.85), ('horns', 0, 8, 0.75), ('choir', 0, 4, 0.7),
                            ('flutes', 12, -6, 0.3)],
        ('swell', 'hold'): [('trombones', 0, -6, 0.45), ('violas', 0, -4, 0.45), ('choir', 0, -8, 0.4)],
        ('swell', 'pedal'): [('basses', 0, 0, 0.55), ('tuba', 0, -4, 0.5), ('cellos', 0, -2, 0.5)],
    }
    B.perform(C.events, parts, pan=lambda t, m, role: 0.6 * S.pan(jack_path(S, t)[0]) if role == 'tune' else None)
    # the party dies away: a cheer of the choir fading, a last firework or two
    for m in (52, 56, 59, 64):
        B.play('choir', m, 0.0, 2.5, 80, gain=0.3)
    for tb, pp in ((0.2, -0.1), (0.9, 0.2)):
        B.hit('crash', tb, 70, gain=0.25, pan=pp)
    B.effects([(0, -10), (M['solo'], -12), (M['swell'], -10), (T_FLAT, -2), (T_FLAT + 3, -12)])
    B.wind(0.5, D, level=lambda tt: 0.25 + 0.2 * np.clip((tt - M['climb']) / 10, 0, 1), pan=-0.3, seed=21)
    # the swell to the top and the hill unrolling
    B.hit('timpani roll', M['swell'] - 0.5, 88, gain=0.35, pan=hill)
    B.hit('cymbal swell', T_FLAT - 1.7, 108, gain=0.55, pan=hill)
    B.hit('crash', T_FLAT, 112, gain=0.5, pan=hill)
    B.hit('gong', T_FLAT + 0.02, 96, gain=0.4, pan=hill)
    B.whoosh(T_FLAT, 2.0, up=False, pan=hill, gain=0.6)
    gliss(B, 'harp', T_FLAT, [57, 60, 64, 69, 72, 76, 81, 84, 88], 0.07, gain=0.55, pan=hill)
    # the last bars ring on: a harp chord and the dog's small woof
    gliss(B, 'harp', D - 3.4, [45, 52, 57, 60, 64, 69], 0.12, v=70, gain=0.45, pan=hill)
    B.woof(D - 2.2, pan=hill, big=0.6)
    B.finish()
