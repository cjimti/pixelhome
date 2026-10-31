"""Making Up: Marcie tells Peppermint Patty she was wrong, and Peppermint Patty goes to say she's sorry.

After the blow-up the backyard is a cold blue evening. Charlie Brown sits alone out at the end of Right, and his
zigzag shirt has drained to blue across the whole house, zigging slowly to his wistful theme played as a ballad,
blue leaves drifting. On the porch Peppermint Patty is still fuming: her brash tune stomps in a two-feel, every note a green
flare across a porch run, every bar a green shove out from her. Then Marcie pops up beside her in
orange, glasses glinting, and tells her, to a patient waltz of her own (an original tune for this scene): her words
run out from the porch over both wings in orange chevrons, and over the second time through Peppermint Patty's green shrinks
in toward her until there's nothing left of it. One beat of stillness, the house dimmed to the two girls. Peppermint Patty's
tune comes back slow and sheepish on a muted trumpet as she walks the length of the porch and out along Right to him,
her green trail filling the path behind her. When she reaches him the house holds its breath, then green and yellow
braid together in stripes that spread from the two of them over every run while his theme warms up, and the main
title swings out over the whole house: zigzags in yellow and green, a run flashing on every beat, a sweep from the
free end of Right, the kids cheering, and a last chord.

compose() lays the music end to end (pixelhome/chef_charlie.py); render() and score() read its events and marks.
tom_p() is Peppermint Patty's position, shared by both."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, GREEN, GLASSES, BLUE, DUSK,
                                    GOLD, NIGHT, ORANGE)

CODE = 'CC11'
TITLE = 'Making Up'
KIND = 'show'
DESCRIPTION = ('Charlie Brown sits alone in the cold blue yard. Marcie tells Peppermint Patty she was wrong, and Patty '
               'walks all the way out to him to say she is sorry.')
VOICEOVER = 'Marcie tells Peppermint Patty she was wrong, so Patty goes to apologise.'

# Marcie: patient and earnest, a jazz waltz in A minor turning to C (original, for this scene).
GLASSES_THEME = dict(meter=3, bpm=132, swing=True, id='glasses', name='Marcie: a patient waltz',
    melody=[(0, 1, 'E4'), (1, 1, 'A4'), (2, 1, 'B4'), (3, 2, 'C5'), (5, 1, 'B4'),
            (6, 1, 'A4'), (7, 1, 'G4'), (8, 1, 'E4'), (9, 3, 'F4'),
            (12, 1, 'D4'), (13, 1, 'G4'), (14, 1, 'A4'), (15, 2, 'B4'), (17, 1, 'A4'),
            (18, 1, 'G#4'), (19, 1, 'B4'), (20, 1, 'D5'), (21, 3, 'C5')],
    chords=[(0, 3, 'Am7'), (3, 3, 'Fmaj7'), (6, 3, 'C6'), (9, 3, 'Dm7'), (12, 3, 'G7'), (15, 3, 'Em7'),
            (18, 3, 'E7'), (21, 3, 'Am7')])


def compose():
    C = Chart()
    C.rest(1.4)                                                     # the cold blue yard comes up
    C.mark('alone')
    C.play('boy', style='ballad', bars=(0, 4), bpm=92, tag='alone')             # he sits alone
    C.mark('fume')
    C.play('tomboy', style='two', bpm=126, tag='fume')              # she is still fuming
    C.mark('tell')
    C.play(GLASSES_THEME, style='waltz', tag='tell')                # Marcie tells her
    C.mark('tell2')
    C.play(GLASSES_THEME, style='swing', tag='tell2')               # and the green drains out of her
    C.mark('still')
    C.rest(1.6)                                                     # the realisation
    C.mark('walk')
    C.play('tomboy', style='ballad', bars=(0, 4), bpm=84, tag='walk')           # sheepish, out to him
    C.mark('sorry')
    C.rest(1.2)                                                     # she reaches him: a held breath
    C.mark('braid')
    C.play('boy', style='two', bars=(4, 8), bpm=104, tag='braid')   # green and yellow, together
    C.mark('joy')
    C.play('title', style='swing', tag='joy')
    C.mark('button')
    C.button('F6', bpm=152, beats=2)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
PLACES = {}


def places(S):
    if not PLACES:
        PLACES.update(boy=S.at('Right', 0.72), tom=S.mid + 22, gls=S.mid - 22)
    return PLACES


def tom_p(S, t):
    """Peppermint Patty: on the porch, then the length of the porch and out along Right to stand beside him."""
    P = places(S)
    end = P['boy'] - 26
    u = float(smoothstep(M['walk'] + 0.3, M['sorry'] - 0.2, t))
    return P['tom'] + (end - P['tom']) * u


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The tune plays the roofline: each note sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def render(G, seed=1):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    tunes = {g: C.tunes(g) for g in ('alone', 'fume', 'tell', 'tell2', 'walk', 'braid', 'joy')}
    fume_t = [n[0] for n in tunes['fume']]
    fume_downs = C.downbeats('fume')
    tell_downs = C.downbeats('tell') + C.downbeats('tell2')
    tell_t = np.array([n[0] for n in tunes['tell'] + tunes['tell2']])
    walk_beats = C.beat_times('walk')
    braid_beats = np.array(C.beat_times('braid'))
    braid_downs = C.downbeats('braid')
    joy_beats = np.array(C.beat_times('joy'))
    joy_downs = C.downbeats('joy')
    alone_beat = 60 / 92
    b_title = 60 / 152
    porch_runs = ('Porch Front', 'Porch Left', 'Porch Right')
    last_joy = tunes['joy'][-1][0]
    bg = [(0, 0.0), (1.4, 0.8), (M['tell2'], 0.8), (M['still'], 0.6), (M['still'] + 0.2, 0.2), (M['walk'], 0.3),
          (M['walk'] + 1.5, 0.65), (M['sorry'], 0.65), (M['braid'], 0.8), (M['joy'], 0.5), (D, 0.5)]
    blues = [(0, 1.0), (M['sorry'], 1.0), (M['braid'] + 2.0, 0.0), (D, 0.0)]

    for f in range(F):
        t = f * DT
        lv = float(keys(t, bg))
        tp = tom_p(S, t)
        meet = P['boy'] - 13

        # the cold evening: deep blue, a few blue-tinted leaves; his shirt drained to blue on every run
        fr = light(NIGHT, 0.45 * lv * np.ones(S.N)) + light(DUSK, 0.3 * lv * np.ones(S.N))
        fr += 0.5 * lv * S.leaves(t, 0.8, wind=-12, n=45, seed=3) * np.array([0.4, 0.5, 1.0])
        bl = float(keys(t, blues))
        if bl > 0:
            ph = (t - M['alone']) / alone_beat
            fr = fr * (1 - 0.4 * bl) + S.zigzag(ph / 2, lv=0.55 * bl * lv, col=BLUE, period=64, travel=0.1)

        # he sits alone: each note of his theme a slow gold breath out from him
        if M['alone'] <= t < M['fume'] + 2:
            fr += keyboard(S, t, tunes['alone'], GOLD, 0.45, decay=0.5, width=34)
            for n in tunes['alone'][::2]:
                fr += S.wave(t, n[0], AMBER, 0.45, origin=P['boy'], speed=300, width=90, decay=1.2)

        # she fumes: every note a green flare across a porch run, every bar a green shove out from her
        if M['fume'] <= t < M['still']:
            fade = float(smoothstep(M['still'], M['tell2'], t)) if t > M['tell2'] else 1.0
            fr += S.run_flash(t, fume_t, cols=(GREEN,), runs=porch_runs, lv=0.85, decay=0.22) if t < M['tell'] else 0
            for tb in fume_downs:
                fr += S.wave(t, tb, GREEN, 0.9, origin=P['tom'], speed=900, width=70, decay=0.7)
            # her green holds the porch, then shrinks to nothing as she listens
            if t >= M['tell']:
                w = 340 * (1 - float(smoothstep(M['tell2'], M['still'] - 0.4, t)))
                fr += light(GREEN, 0.55 * fade * S.span(P['tom'] - 4, P['tom'] + w) *
                            (0.8 + 0.2 * np.sin(2 * np.pi * (t - M['tell']) / (60 / 132))))
            else:
                fr += light(GREEN, 0.45 * S.porch)

        # Marcie tells her: orange chevrons run out from the porch over both wings on her notes,
        # her glasses glinting on every bar
        if M['tell'] <= t < M['still'] + 1:
            fade = float(smoothstep(M['still'] + 1, M['still'], t))
            for j in np.flatnonzero((tell_t <= t) & (tell_t > t - 1.6)):
                b = t - tell_t[j]
                r = 60 + 650 * b
                ring = np.exp(-((np.abs(d - P['gls']) - r) / 55) ** 2) * (1 - b / 1.6)
                fr += light(GLASSES if j % 3 else AMBER, 1.0 * fade * ring)
            # her side of it spreads from the porch over the house: her orange zigzag replaces his blue
            u = float(smoothstep(M['tell'], M['still'] - 1.0, t))
            reach = 40 + 1500 * u
            zone = S.span(P['gls'] - reach, P['gls'] + reach, 60) * fade * (1 - S.porch * (t < M['tell2']))
            ph = (t - M['tell']) / (60 / 132)
            fr = fr * (1 - 0.7 * zone[:, None]) + S.zigzag(ph / 3, lv=0.6, col=GLASSES, period=64, travel=0.1,
                                                           mask=zone)
            a = t - M['tell']
            if a < 0.7:
                fr += light(GLASSES, 0.9 * np.exp(-a / 0.2) * S.run['Porch Front'])

        # the realisation: stillness, the two girls alone in the dark; a slow white heartbeat on the tomboy
        if M['still'] <= t < M['walk']:
            a = t - M['still']
            fr += light(WHITE, 0.5 * np.exp(-((a - 0.5) / 0.15) ** 2) * S.blob(P['tom'], 30))
            fr += light(GREEN, 0.3 * np.exp(-((a - 1.1) / 0.2) ** 2) * S.blob(P['tom'], 60))

        # she walks out to him, the path behind her filling green, a ripple on every step
        if M['walk'] <= t < M['braid'] + 2:
            fade = float(smoothstep(M['braid'] + 2, M['braid'], t))
            trail = S.span(P['tom'], tp, 6) * fade
            fr = fr * (1 - 0.4 * trail[:, None]) + light(GREEN, 0.5 * trail * (0.85 + 0.15 * np.sin(d / 9 - 4 * t)))
            for tb in walk_beats:
                if tb <= t:
                    fr += S.wave(t, tb, GREEN, 0.5 * fade, origin=tom_p(S, tb), speed=400, width=40, decay=0.6)
            fr += keyboard(S, t, tunes['walk'], GREEN, 0.4 * fade, decay=0.45)

        # she's sorry: the house holds its breath, then green and yellow braid in stripes out from the two of them
        if M['sorry'] <= t < M['joy'] + 1.5:
            a = t - M['sorry']
            fade = float(smoothstep(M['joy'] + 1.5, M['joy'], t))
            fr += light(WHITE, 0.6 * np.exp(-((a - 0.6) / 0.25) ** 2) * S.blob(meet, 40))
            if t >= M['braid']:
                u = float(smoothstep(M['braid'], M['joy'], t))
                reach = 60 + u * 2600
                zone = S.span(meet - reach, meet + reach, 30)
                ph = (t - M['braid']) / (60 / 104)
                stripes = S.stripes(ph, [GREEN, YELLOW], lv=0.8, period=34, mask=zone * fade)
                fr = fr * (1 - 0.75 * zone[:, None] * fade) + stripes
                fr += light(WHITE, 0.55 * pulse(t, braid_beats, 0.12) * S.blob(meet, 50))
                for tb in braid_downs:
                    fr += S.wave(t, tb, WHITE, 0.7, origin=meet, speed=1100, width=60, decay=0.8)
                fr += keyboard(S, t, tunes['braid'], WHITE, 0.5)

        # the main title on the whole house: zigzags in yellow and green, a run on every beat, a sweep, the button
        if t >= M['joy']:
            ph = (t - M['joy']) / b_title
            bar = min(int(ph // 4), 7)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            col = (YELLOW, GREEN, YELLOW, ORANGE, YELLOW, GREEN, GOLD, YELLOW)[bar]
            fr = fr * (1 - 0.6 * fade) + S.zigzag(ph, lv=0.85 * fade, col=col, travel=0.25 * (bar >= 4))
            fr += S.run_flash(t, joy_beats, cols=(WHITE, GREEN, YELLOW), lv=0.6, decay=0.15)
            fr += keyboard(S, t, tunes['joy'], WHITE, 0.7)
            fr += S.sweep(t, joy_downs[6], 2.4, WHITE, 0.9, frm='right', width=90, trail=0.5)
            fr += S.confetti([(joy_downs[0], 1.0, meet), (joy_downs[4], 1.0, S.mid)], t,
                             colors=(GREEN, YELLOW, WHITE, ORANGE), n=28, seed=3)
            a = t - last_joy
            if 0 <= a < 1.2:
                fr += light(YELLOW, 0.7 * np.exp(-a / 0.3) * np.ones(S.N))
            a = t - M['button']
            if a >= 0:
                fr += light(YELLOW, np.exp(-a / 0.45) * np.ones(S.N))
                fr += light(GREEN, 0.4 * np.exp(-a / 0.8) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * np.ones(S.N))

        # the characters, over everything
        bob = 1.0
        fr = S.boy(fr, P['boy'], 0.8 + 0.2 * (t >= M['braid']) * pulse(t, braid_beats, 0.2) + 0.2 * (t >= M['joy']),
                   facing=-1, t=t, glow=0.25 if t < M['braid'] else 0.45)
        if t >= M['fume'] - 0.3:
            stomp = pulse(t, fume_downs, 0.15) if t < M['tell'] else 0.0
            fr = S.tomboy(fr, tp, min(1.2, 0.85 + 0.3 * stomp), facing=1 if t >= M['walk'] else -1, t=t)
        if M['tell'] - 0.1 <= t < M['sorry'] + 3:
            u = float(smoothstep(M['tell'] - 0.1, M['tell'] + 0.15, t) * smoothstep(M['sorry'] + 3, M['sorry'], t))
            glint = pulse(t, tell_downs, 0.25) if t < M['still'] else 0.0
            fr = S.glasses(fr, P['gls'], u * bob, facing=1, t=t, glint=min(glint, 1.0))

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    from pixelhome.audio import note
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.12)
    parts = {
        ('alone', 'tune'): [('piano', 0, -6, 0.85)],
        ('alone', 'comp'): [('piano', 0, -16, 0.45), ('choir', 12, -26, 0.3)],
        ('fume', 'tune'): [('harmon trumpet', 0, 8, 1.0), ('piano', 0, -10, 0.4)],
        ('fume', 'comp'): [('piano', 0, -6, 0.5)],
        ('tell', 'tune'): [('piano', 0, -2, 0.85), ('celesta', 12, -26, 0.25)],
        ('tell', 'comp'): [('piano', 0, -14, 0.45)],
        ('tell2', 'tune'): [('piano', 0, 2, 0.85), ('flutes', 0, -14, 0.35)],
        ('tell2', 'comp'): [('piano', 0, -12, 0.45)],
        ('walk', 'tune'): [('harmon trumpet', 0, -6, 0.9)],
        ('walk', 'comp'): [('piano', 0, -18, 0.4)],
        ('braid', 'tune'): [('piano', 0, 4, 0.85), ('harmon trumpet', 0, -10, 0.45)],
        ('braid', 'comp'): [('piano', 0, -10, 0.5), ('choir', 12, -18, 0.35)],
        ('joy', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('xylo', 12, -14, 0.25)],
        ('joy', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    boy, tom, gls = S.pan(P['boy']), S.pan(P['tom']), S.pan(P['gls'])
    # the cold evening: a soft minor chord on the choir before he sits down to his theme
    for m in (62, 65, 69, 72):
        B.play('choir', m, 0.2, 1.6, 44, gain=0.3)
    B.wind(0.0, M['fume'], level=0.2, pan=boy)
    B.slide(C.downbeats('alone')[-1] + 1.6, 0.7, up=False, pan=boy, gain=0.35, lo=500, hi=800)   # his sigh
    # she fumes: a stomp on every bar
    for tb in C.downbeats('fume'):
        B.hit('hoof', tb, 104, gain=0.6, pan=tom, fx=True)
    # Marcie pops up beside her
    B.boing(M['tell'], pan=gls, gain=0.6, high=1.2)
    B.play('glock', note('E5'), M['tell'] + 0.05, 0.4, 70, pan=gls, gain=0.3)
    # the realisation: a low bass note and a tiny gasp
    B.play('bass', note('A1') + 12, M['still'] + 0.4, 1.0, 90, pan=tom, gain=0.7)
    B.kids(M['still'] + 0.9, M['still'] + 1.5, 'gasp', level=0.45, pan=tom, voices=1, seed=4)
    # her footsteps out to him
    B.steps(M['walk'] + 0.3, M['sorry'] - 0.2, beat=60 / 84, pan=lambda tt: S.pan(tom_p(S, tt)), gain=0.6)
    # she's sorry: a held breath on the choir, then the braid's warm swell
    for m in (65, 69, 72, 77):
        B.play('choir', m, M['sorry'], 1.4, 50, pan=boy, gain=0.35)
    B.hit('cymbal swell', M['braid'] - 0.9, 80, gain=0.3, pan=boy)
    B.play('glock', note('C6'), M['braid'], 0.5, 80, pan=boy, gain=0.35)
    # the title on the whole house: the kids cheer, a sweep, the button
    B.kids(M['joy'] + 0.1, M['joy'] + 2.4, 'cheer', level=0.6, pan=0.0, voices=6, seed=6)
    B.whoosh(C.downbeats('joy')[6], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - M['joy']) / 13)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.effects([(0, -3), (M['joy'], -4)])
    B.finish()
