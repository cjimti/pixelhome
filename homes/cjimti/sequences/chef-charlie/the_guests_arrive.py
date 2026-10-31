"""The Guests Arrive: the tomboy, Marcie and Franklin come to the backyard table.

The backyard comes up at evening (a deep blue sky, the lawn along the wings, party bulbs swaying) with the ping-pong
table set on the porch, and the drummer counts in. The main title swings while strings of party lights fill the house
a run at a time, each run in one of the guests' colours, chasing on the beat, the piano sparking the roofline. Then the
wait: Charlie Brown stands by the table to his own wistful theme, and every bar a lookout beam runs out from
him to the end of Right and back. A clock ticks on the table. Headlights come in on the third bar, a near miss: they
pass, and he sags. Then a car really does pull in from the free end of Right, honks twice (Right flashes gold with each
beep), and backs away, leaving Peppermint Patty. She strides to the table on her brash theme, a green marquee rushing
along behind her, a green ripple at every step and the wings flashing green on every bar; at her theme's peak a green
wave crosses the whole house. Marcie trails in on her own polite little tune (clarinet), an orange
marquee following her, every note a glint of white along the roof. Franklin pops up on Left with a red
burst and bounces to his seat on his ball-park tune, red and white bulbs chasing behind him. Three folding chairs
clatter, one per guest, each seat flashing white then glowing in its guest's colour. Then the feast theme twice over the
whole house: stripes of every kid's colour marching on the beat, runs flashing, confetti thrown from the table on every
bar of the second chorus, a sweep out from the porch, and a button. Nobody has looked at the menu yet.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks.
Marcie' tune and Franklin's are this scene's own, original."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, tri, YELLOW, WHITE, AMBER, GOLD, GREEN, GLASSES, CAP,
                                    STRIPE, BLANKET, WARM, TOAST, POPCORN, PRETZEL, JELLY, ICE)

CODE = 'CC08'
TITLE = 'The Guests Arrive'
KIND = 'show'
DESCRIPTION = ('Charlie Brown waits by the ping-pong table. A car honks: Peppermint Patty strides in, Marcie trails '
    'behind, Franklin bounces up, and three folding chairs clatter into place.')
VOICEOVER = 'The table is set in the backyard, and here come the guests.'

# Marcie: a polite, tidy little tune (C major, four bars, a two-feel)
GLASSES_T = dict(meter=4, bpm=112, swing=True, id='glasses',
                 melody=[(0, 1, 'E4'), (1, 1, 'G4'), (2, .5, 'C5'), (2.5, .5, 'B4'), (3, 1, 'A4'),
                         (4, .5, 'G4'), (4.5, .5, 'A4'), (5, .5, 'G4'), (5.5, .5, 'E4'), (6, 2, 'D4'),
                         (8, 1, 'F4'), (9, 1, 'A4'), (10, .5, 'D5'), (10.5, .5, 'C5'), (11, 1, 'B4'),
                         (12, .5, 'A4'), (12.5, .5, 'B4'), (13, .5, 'D5'), (13.5, .5, 'B4'), (14, 2, 'C5')],
                 chords=[(0, 4, 'Cmaj7'), (4, 2, 'Am7'), (6, 2, 'D7'), (8, 2, 'Dm7'), (10, 2, 'G7'),
                         (12, 2, 'Dm7'), (14, 2, 'Cmaj7')])
# Franklin: a confident ball-park bounce (B flat, four bars)
CAP_T = dict(meter=4, bpm=132, swing=True, id='cap',
             melody=[(0, .5, 'D4'), (.5, .5, 'F4'), (1, .5, 'G4'), (1.5, .5, 'Bb4'), (2, 1, 'C5'), (3, 1, 'Bb4'),
                     (4, .5, 'G4'), (4.5, .5, 'Bb4'), (5, 1, 'D5'), (6, .5, 'C5'), (6.5, .5, 'Bb4'), (7, 1, 'G4'),
                     (8, .5, 'D4'), (8.5, .5, 'F4'), (9, .5, 'G4'), (9.5, .5, 'Bb4'), (10, 1, 'Eb5'), (11, 1, 'D5'),
                     (12, .5, 'C5'), (12.5, .5, 'A4'), (13, .5, 'F4'), (13.5, .5, 'A4'), (14, 2, 'Bb4')],
             chords=[(0, 4, 'Bb6'), (4, 4, 'Gm7'), (8, 4, 'Eb7'), (12, 2, 'F7'), (14, 2, 'Bb6')])


def compose():
    C = Chart()
    C.rest(2.4)                                                     # the backyard comes up
    C.mark('count')
    C.play('title', style='brushes', bars=(0, 1), tune=False, tag='count')
    C.mark('title')
    C.play('title', style='swing', tag='title')                     # party lights fill the house
    C.mark('wait')
    C.play('boy', style='ballad', bars=(0, 4), bpm=92, tag='wait')   # he waits; a near miss
    C.mark('car')
    C.play('tomboy', style='walk', bars=(0, 2), tune=False, tag='car')          # a car pulls in and honks
    C.mark('tomboy')
    C.play('tomboy', style='swing', tag='tomboy')                   # she strides to the table
    C.mark('glasses')
    C.play(GLASSES_T, style='two', bpm=104, tag='glasses')          # Marcie trails in
    C.mark('cap')
    C.play(CAP_T, style='swing', bpm=126, tag='cap')                # Franklin pops up
    C.mark('seat')
    C.play('feast', style='brushes', bars=(0, 2), tune=False, tag='seat')       # three chairs clatter
    C.mark('feast')
    C.play('feast', style='swing', tag='feast')
    C.mark('feast2')
    C.play('feast', style='swing', tag='feast2')
    C.mark('button')
    C.button('D6', bpm=184, beats=4)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks

PLACES = {}


def places(S):
    """Where everyone ends up around the table on Porch Front, where the car stops, where Franklin pops up."""
    if not PLACES:
        m = S.mid
        PLACES.update(table=m, boy=m - 65, cap=m - 125, tom=m + 70, gl=m + 125, blanket=S.at('Porch Left', 0.82),
                      stop=S.at('Right', 0.5), cap_up=S.at('Left', 0.45), enter=S.L + 45)
    return PLACES


def car_p(S, t):
    """The car: in from past the end of Right, easing to a stop, backing out again once she is out."""
    P = places(S)
    t0 = M['car']
    if t < M['tomboy']:
        return P['enter'] + 30 + (P['stop'] - P['enter'] - 30) * float(smoothstep(t0, t0 + 1.7, t)) ** 0.7
    return P['stop'] + (P['enter'] + 60 - P['stop']) * float(smoothstep(M['tomboy'] + 0.3, M['tomboy'] + 2.2, t))


def tom_p(S, t):
    P = places(S)
    return P['stop'] + (P['tom'] - P['stop']) * float(smoothstep(M['tomboy'] + 0.4, M['glasses'] - 2.5, t))


def gl_p(S, t):
    P = places(S)
    return P['enter'] + (P['gl'] - P['enter']) * float(smoothstep(M['glasses'] - 3.0, M['cap'] - 1.0, t))


def cap_p(S, t):
    P = places(S)
    return P['cap_up'] + (P['cap'] - P['cap_up']) * float(smoothstep(M['cap'] + 0.6, M['seat'] - 0.6, t))


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The piano plays the roofline: each note of the tune sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


REVEAL = ('Porch Front', 'Left', 'Right', 'Porch Left', 'Porch Right', 'Side')
RUNCOL = (YELLOW, GREEN, GLASSES, STRIPE, BLANKET, CAP)
FEAST_COLS = (YELLOW, GREEN, GLASSES, CAP, BLANKET, STRIPE)
FOOD = [(-8, TOAST), (-7, TOAST), (-4, POPCORN), (-3, POPCORN), (3, PRETZEL), (4, PRETZEL), (7, JELLY[0]),
        (8, JELLY[2])]


def render(G, seed=1):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    b_title = 60 / 152
    t_title = C.downbeats('title')
    t_count = C.beat_times('count')
    tunes = {g: C.tunes(g) for g in ('title', 'wait', 'tomboy', 'glasses', 'cap', 'feast', 'feast2')}
    last_title = tunes['title'][-1][0]
    wait_downs = C.downbeats('wait')
    wait_beats = C.beat_times('wait')
    honks = [M['car'] + 1.95, M['car'] + 1.95 + 0.32]
    tom_bass = C.times('bass', 'tomboy')
    tom_downs = C.downbeats('tomboy')
    gl_tune = [n[0] for n in tunes['glasses']]
    cap_downs = C.downbeats('cap')
    cap_beats = C.beat_times('cap')
    seat_beats = C.beat_times('seat')
    chairs = [(seat_beats[1], P['tom'], GREEN), (seat_beats[3], P['gl'], GLASSES), (seat_beats[5], P['cap'], CAP)]
    f1_beats = np.array(C.beat_times('feast'))
    f2_beats = np.array(C.beat_times('feast2'))
    f2_downs = C.downbeats('feast2')
    b_feast = 60 / 184
    lv_key = [(0, 0.0), (2.4, 1.0), (M['wait'], 1.0), (M['wait'] + 1, 0.7), (M['car'], 0.7), (M['tomboy'], 1.0),
              (M['feast'], 1.0), (M['feast'] + 1, 0.55), (M['end'], 0.55)]

    for f in range(F):
        t = f * DT
        fr = S.backyard(t, lv=float(keys(t, lv_key)))
        beat = pulse(t, beats, 0.14)
        tl = t >= M['title']

        # the count-in: four warm washes out from the table
        for tc in t_count:
            fr += S.wave(t, tc, AMBER, 0.55, speed=700, width=90, decay=0.35)

        # the title: strings of party lights fill the house a run at a time, each a guest's colour, chasing
        if M['title'] <= t < M['wait'] + 1.0:
            ph = (t - M['title']) / b_title
            fade = float(smoothstep(M['wait'] + 1.0, M['wait'], t))
            for i, r in enumerate(REVEAL):
                a = t - t_title[i]
                if a >= 0:
                    m = S.run[r] * float(smoothstep(0, 0.15, a)) * fade
                    fr = fr * (1 - 0.5 * m[:, None]) + S.chase((-1) ** i * 2 * ph, (RUNCOL[i], None), 0.85,
                                                               spacing=2, mask=m)
                    if a < 0.6:
                        fr += light(WHITE, 0.75 * np.exp(-a / 0.18) * S.run[r] * fade)
            if t >= t_title[6]:
                fr += S.run_flash(t, C.beat_times('title')[24:], cols=(WHITE, GOLD), lv=0.55 * fade, decay=0.15)
            fr += keyboard(S, t, tunes['title'], WHITE, 0.7 * fade)
            a = t - last_title
            if 0 <= a < 1.2:
                fr += light(WARM, 0.85 * np.exp(-a / 0.35) * np.ones(S.N))

        # the wait: a lookout beam out to the end of Right and back every bar; the clock ticks; a near miss
        if M['wait'] <= t < M['car'] + 0.6:
            fade = float(smoothstep(M['car'] + 0.6, M['car'], t))
            ph = (t - M['wait']) / (60 / 92)
            fr += S.zigzag(ph, lv=0.5 * fade, col=YELLOW, mask=S.run['Left'] | S.run['Side'])
            bar = 4 * 60 / 92
            for i, tb in enumerate(wait_downs):
                a = t - tb
                if 0 <= a < bar:
                    q = P['boy'] + (L + 20 - P['boy']) * tri(a / bar * 1.0)
                    reach = 0.45 if i == 2 else 1.0                  # the near miss: he only half looks
                    fr += light(WARM, 1.0 * fade * np.exp(-((d - q) / 60) ** 2) * (d > P['boy']) * reach)
                    fr += light(AMBER, 0.45 * fade * S.span(P['boy'], q) * reach * (0.75 + 0.25 * np.sin(0.15 * d)))
            for tb in wait_beats:
                a = t - tb
                if 0 <= a < 0.5:
                    fr += light(WHITE, 0.55 * np.exp(-a / 0.08) * S.blob(P['table'], 12))
            if len(wait_downs) > 2:                                  # headlights pass along Right, and are gone
                a = t - wait_downs[2]
                if 0 <= a < 2.4:
                    q = L + 40 - 520 * a / 2.4
                    vis = float(smoothstep(0, 0.3, a) * smoothstep(2.4, 1.6, a))
                    fr += light(WHITE, 0.9 * vis * np.exp(-((d - q) / 14) ** 2))
                    fr += light(WARM, 0.5 * vis * np.exp(-((d - q + 30) / 40) ** 2))

        # the party bulbs dance to the band on the runs nobody is walking along: every beat they flip
        if M['tomboy'] <= t < M['feast']:
            nb = int(np.searchsorted(beats, t))
            idle = (S.run['Left'] | S.run['Side'] | S.run['Porch Left']) if t < M['cap'] else \
                (S.run['Right'] | S.run['Porch Right'] | S.run['Side'])
            sec = float(smoothstep(M['tomboy'], M['tomboy'] + 0.5, t) * smoothstep(M['feast'], M['feast'] - 0.3, t))
            fr += S.chase(3 * nb, (WARM, GOLD, None), 0.55 * sec, spacing=2, mask=idle.astype(float))

        # the car: in from the end of Right, two honks that flash Right gold, then it backs away
        if M['car'] <= t < M['tomboy'] + 2.4:
            for th in honks:
                a = t - th
                if 0 <= a < 0.8:
                    fr += light(GOLD, 0.85 * np.exp(-a / 0.15) * (S.run['Right'] | S.run['Porch Right']))
                    fr += light(WHITE, 0.6 * np.exp(-a / 0.06) * S.blob(car_p(S, t), 50))
            fr = S.car(fr, car_p(S, t), 1.0, facing=-1, t=t * (t < M['car'] + 1.7 or t > M['tomboy'] + 0.3))

        # the tomboy: a green marquee rushing behind her, a ripple at every step, the wings flash on every bar
        if M['tomboy'] <= t < M['seat']:
            p = tom_p(S, t)
            fade = float(smoothstep(M['glasses'] + 2.0, M['glasses'] - 0.5, t))
            a = t - M['tomboy']
            if a < 0.8:
                fr += light(GREEN, np.exp(-a / 0.2) * S.blob(P['stop'], 60))
            behind = S.span(p, P['stop'] + 30) * fade
            ph = (t - M['tomboy']) / (60 / 144)
            fr = fr * (1 - 0.55 * behind[:, None]) + S.chase(4 * ph, (GREEN, GREEN, None), 0.85, spacing=2,
                                                             mask=behind)
            for tb in [x for x in tom_bass if x <= t][-3:]:
                fr += S.wave(t, tb, GREEN, 0.7 * fade, origin=tom_p(S, tb), speed=700, width=40, decay=0.4)
            fr += S.run_flash(t, tom_downs, cols=(GREEN,), runs=('Left', 'Side', 'Left', 'Porch Left'), lv=0.8 * fade,
                              decay=0.4)
            fr += keyboard(S, t, tunes['tomboy'], GREEN, 0.6 * fade, width=30)
            if len(tom_downs) > 4:                                   # her peak: a green wave across the house
                fr += S.wave(t, tom_downs[4], GREEN, 0.95, origin=p, speed=900, width=110, decay=1.2)
                fr += S.wave(t, tom_downs[4] + 0.1, WHITE, 0.5, origin=p, speed=900, width=40, decay=0.6)
            if t >= M['glasses'] - 2.5:                              # she stomps to a stop at the table
                a = t - (M['glasses'] - 2.5)
                if a < 1.2:
                    fr += S.burst([(M['glasses'] - 2.5, 0.8, P['tom'])], t, seed=5, n=10, reach=0.25,
                                  colors=(GREEN, WHITE))

        # Marcie: an orange marquee trailing her in, a glint along the roof on every note
        if M['glasses'] - 3.0 <= t < M['seat']:
            p = gl_p(S, t)
            fade = float(smoothstep(M['cap'] + 1.5, M['cap'] - 0.5, t))
            behind = S.span(p, L) * fade
            ph = (t - M['glasses']) / (60 / 104)
            fr = fr * (1 - 0.5 * behind[:, None]) + S.chase(2 * ph, (GLASSES, None, None), 0.8, spacing=3,
                                                            mask=behind)
            for i, tn in enumerate(gl_tune):
                a = t - tn
                if 0 <= a < 0.8:
                    q = p - (90 + 30 * (i % 4)) * a / 0.8
                    fr += light(WHITE, 0.8 * fade * (1 - a / 0.8) * np.exp(-((d - q) / 10) ** 2))
            fr += S.run_flash(t, C.downbeats('glasses'), cols=(GLASSES,), runs=('Left', 'Porch Left'),
                              lv=0.85 * fade, decay=0.6)

        # Franklin: pops up on Left in a red burst; red and white bulbs chase behind him
        if M['cap'] <= t < M['feast']:
            p = cap_p(S, t)
            fade = float(smoothstep(M['seat'] + 1.0, M['seat'], t))
            a = t - M['cap']
            if a < 1.6:
                fr += light(CAP, np.exp(-a / 0.3) * S.run['Left'])
                fr += S.burst([(M['cap'], 1.0, P['cap_up'])], t, seed=8, n=14, reach=0.4, colors=(CAP, WHITE))
            behind = S.span(P['cap_up'] - 40, p) * fade
            ph = (t - M['cap']) / (60 / 126)
            fr = fr * (1 - 0.5 * behind[:, None]) + S.chase(-2 * ph, (CAP, WHITE, None), 0.8, spacing=2, mask=behind)
            fr += S.run_flash(t, cap_beats, cols=(CAP, WHITE), runs=('Right', 'Porch Right', 'Right', 'Side'),
                              lv=0.6 * fade, decay=0.2)
            fr += keyboard(S, t, tunes['cap'], CAP, 0.5 * fade)

        # three folding chairs clatter into place, one per guest: a white burst, then the seat glows its colour
        if t >= M['seat']:
            for tc, pc, col in chairs:
                a = t - tc
                if a >= 0:
                    fr += S.burst([(tc, 0.9, pc)], t, seed=11, n=8, reach=0.12, colors=(WHITE, col), life=0.8)
                    fr += light(col, (0.35 + 0.5 * np.exp(-a / 0.3)) * S.blob(pc, 30) *
                                float(smoothstep(M['button'] + 0.5, M['button'], t)))
                    if a < 0.5:
                        fr += light(col, 0.6 * np.exp(-a / 0.15) * S.run['Left' if pc < P['table'] else 'Right'])

        # the feast theme twice: stripes of every kid's colour marching on the beat, runs flashing, confetti
        if t >= M['feast']:
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            n_b = (t - M['feast']) / b_feast
            dr = 1 if t < M['feast2'] else -1
            rise = float(smoothstep(M['feast'], M['feast'] + 0.4, t))
            fr = fr * (1 - 0.6 * rise * fade) + S.stripes(dr * n_b, FEAST_COLS, lv=0.75 * rise * fade, period=46)
            fr += S.run_flash(t, f1_beats if t < M['feast2'] else f2_beats, cols=(WHITE,), lv=0.45 * fade, decay=0.12)
            fr += keyboard(S, t, tunes['feast'] + tunes['feast2'], WHITE, 0.65 * fade)
            fr += S.confetti([(tb, 0.9, P['table']) for tb in f2_downs], t, colors=JELLY, n=20, reach=0.9, seed=6)
            if len(f2_downs) > 6:
                fr += S.sweep(t, f2_downs[6], 1.6, WHITE, 0.8, frm='centre', width=80, trail=0.4)
            a = t - M['button']
            if a >= 0:
                fr += light(WARM, np.exp(-a / 0.5) * np.ones(S.N))
                fr += light(WHITE, 0.7 * np.exp(-a / 0.12) * np.ones(S.N))

        # the table and the people, over everything
        if tl:
            fr = S.table(fr, P['table'], min(1.0, (t - M['title']) / 0.5), half=10, food=FOOD)
        if t >= M['feast']:                                          # the bird flits over the table for the feast
            q = P['table'] + 40 * np.sin(2 * np.pi * 0.7 * (t - M['feast']))
            fr = S.bird(fr, q, 1.0, t=t, facing=1 if np.cos(2 * np.pi * 0.7 * (t - M['feast'])) > 0 else -1)
        bob = 0.85 + 0.25 * beat
        if t >= M['title'] + 1.0:
            sag = 1.0
            if len(wait_downs) > 2 and wait_downs[2] + 1.6 <= t < M['car'] + 1.0:
                sag = 0.65                                           # the near miss: he droops
            fr = S.boy(fr, P['boy'], min(1.2, bob * sag), facing=1, t=t, glow=0.3 * sag)
            fr = S.blanket_boy(fr, P['blanket'], 0.9, facing=1, t=t)
        if t >= M['tomboy']:
            fr = S.tomboy(fr, tom_p(S, t), 1.0 + 0.2 * beat, facing=-1, t=t)
        if t >= M['glasses'] - 3.0:
            vis = float(smoothstep(M['glasses'] - 3.0, M['glasses'] - 2.0, t))
            glint = pulse(t, gl_tune, 0.15) if t < M['cap'] else 0.3 * beat
            fr = S.glasses(fr, gl_p(S, t), vis, facing=-1, t=t, glint=min(1.0, glint))
        if t >= M['cap']:
            hop = 0.15 * abs(np.sin(np.pi * (t - M['cap']) / (60 / 126)))
            fr = S.cap_boy(fr, cap_p(S, t), 1.0 + hop, facing=1, t=t)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    parts = {
        ('title', 'tune'): [('piano', 0, 8, 0.85), ('xylo', 12, -12, 0.22)],
        ('wait', 'tune'): [('piano', 0, -6, 0.85)],
        ('wait', 'comp'): [('piano', 0, -14, 0.4)],
        ('tomboy', 'tune'): [('trumpets', 0, -2, 0.5), ('piano', 0, -2, 0.6)],
        ('tomboy', 'comp'): [('piano', 0, -6, 0.5)],
        ('glasses', 'tune'): [('clarinets', 0, 2, 0.75), ('piano', 12, -22, 0.3)],
        ('glasses', 'comp'): [('piano', 0, -12, 0.45)],
        ('cap', 'tune'): [('piano', 0, 6, 0.8), ('muted horn', 0, -2, 0.5)],
        ('cap', 'comp'): [('piano', 0, -8, 0.45)],
        ('feast', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5)],
        ('feast', 'comp'): [('piano', 0, -6, 0.5)],
        ('feast2', 'tune'): [('piano', 0, 12, 0.85), ('trumpets', 0, -8, 0.4), ('choir', 0, -16, 0.3)],
        ('feast2', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -14, 0.28)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    # evening in the backyard: a soft open chord before the count-in
    for m in (62, 66, 69, 73):
        B.play('choir', m, 0.3, 2.3, 50, gain=0.3)
    # the wait: the clock on the table ticks; the near miss passes by and he sighs on a slide whistle
    for i, tb in enumerate(C.beat_times('wait')):
        B.hit('wood', tb, 70 + 12 * (i % 2), pitch=0 if i % 2 else 5, gain=0.35, pan=S.pan(P['table']))
    tw = C.downbeats('wait')[2]
    B.engine(tw, tw + 2.4, pan=lambda tt: S.pan(P['enter'] - 520 * (tt - tw) / 2.4), gain=0.5, rev=0.5)
    B.slide(tw + 1.7, 0.6, up=False, pan=S.pan(P['boy']), gain=0.45, lo=500, hi=900)
    # the car: engine, a squeak of brakes, two honks, the door, the kids piling out, and away
    B.engine(M['car'], M['tomboy'] + 2.4, pan=lambda tt: S.pan(car_p(S, tt)), gain=0.9,
             rev=lambda tt: 0.6 - 0.4 * ((tt > M['car'] + 1.2) & (tt < M['tomboy'] + 0.3)))
    B.slide(M['car'] + 1.4, 0.3, up=True, pan=S.pan(P['stop']), gain=0.25, lo=1800, hi=2400)
    B.horn(M['car'] + 1.95, beeps=2, pan=S.pan(P['stop']), gain=1.0, beep=0.2, gap=0.12)
    B.hit('woodblock', M['tomboy'] - 0.1, 100, pitch=-5, gain=0.4, pan=S.pan(P['stop']))
    B.kids(M['car'] + 2.7, M['tomboy'] + 1.0, 'chatter', level=0.5, pan=S.pan(P['stop']), voices=3, seed=1)
    # her stride: footsteps, a stomp to a stop
    B.steps(M['tomboy'] + 0.4, M['glasses'] - 2.5, beat=60 / 144, pan=lambda tt: S.pan(tom_p(S, tt)), gain=0.6)
    B.hit('bass drum', M['glasses'] - 2.5, 100, gain=0.4, pan=S.pan(P['tom']))
    B.hit('crash', C.downbeats('tomboy')[4], 100, gain=0.3, pan=S.pan(tom_p(S, C.downbeats('tomboy')[4])))
    # Marcie: daintier steps, a glint of a triangle on her first note
    B.steps(M['glasses'] - 3.0, M['cap'] - 1.0, beat=60 / 104, pan=lambda tt: S.pan(gl_p(S, tt)), gain=0.4, v=64)
    B.clink(M['glasses'], pan=S.pan(gl_p(S, M['glasses'])), gain=0.5)
    # Franklin pops up
    B.boing(M['cap'], pan=S.pan(P['cap_up']), gain=0.9, high=1.3)
    B.hit('cowbell', M['cap'] + 0.02, 96, gain=0.3, pan=S.pan(P['cap_up']))
    B.steps(M['cap'] + 0.6, M['seat'] - 0.6, beat=60 / 126, pan=lambda tt: S.pan(cap_p(S, tt)), gain=0.5)
    # three folding chairs clatter, the kids settle in chattering
    sb = C.beat_times('seat')
    for i, (tb, pc) in enumerate([(sb[1], P['tom']), (sb[3], P['gl']), (sb[5], P['cap'])]):
        B.chair(tb, pan=S.pan(pc), gain=0.7, seed=i)
    B.kids(M['seat'] + 0.4, M['feast'] + 1.5, 'chatter', level=0.5, pan=S.pan(P['table']), voices=4, seed=4)
    # confetti on the second chorus: a bell tree each bar
    for tb in C.downbeats('feast2')[::2]:
        B.hit('bell tree', tb, 80, gain=0.25, pan=S.pan(P['table']))
    B.whoosh(C.downbeats('feast2')[6], 1.4, up=True, gain=0.4)
    B.effects([(0, -3), (M['car'], 0), (M['feast'], -4)])
    B.hit('cymbal swell', M['button'] - 1.4, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.kids(M['button'] + 0.1, M['button'] + 1.6, 'cheer', level=0.45, pan=S.pan(P['table']), voices=5, seed=7)
    B.finish()
