"""The Kick: Lucy holds the football and swears she won't pull it away; he runs, she pulls it, he flies.

The yard comes up at the end of an autumn afternoon (a violet sky, a low sun over the porch, leaves falling) and the
drummer counts in on brushes. The main title swings, and Charlie Brown's shirt takes over the house a run
at a time: yellow with black zigzag bands that zig and zag on the beat, each note of the piano sparking where it would
sit on a keyboard laid across the front. He walks in from the free end of Right to his own wistful theme, kicking up
leaves. Lucy pops up on the porch with the football; her teasing figure climbs a step every two bars while
blue "come on" pulses run from her to him, and on the fourth bar she floods the porch blue: she promises. Stop-time:
on each hit he lunges and loses his nerve, twice; then the held breath, the house dimmed to the three of them. A
snare roll winds him up, Right filling yellow behind him, and he runs: the trio doubles its tempo, the path he has
covered fills with his zigzag and the wings flash amber on every bar, faster for the sprint. At the ball, silence:
she yanks it away, he kicks nothing, and he flies the whole length of the porch with a slide whistle, a yellow comet,
and lands flat on Left. The thud runs out across every run, the leaves jump, he sees stars, and she laughs at him on
a buzzing trombone, tossing the ball, her taunts running down the roof to him while the leaves pile on. He sits up to
the end of his theme as warm swells breathe out from him, and the main title comes back on the whole house: zigzags
in yellow, orange and red, every beat flashing a run, a sweep from the free end of Right to the back of Side, and a
last chord. A Thanksgiving tradition.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks,
so every hit, step and flash lands on the music. boy_p() and ball_p() are his and the ball's positions, shared too."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, ORANGE, RED, GOLD, DRESS,
                                    LEAVES)

CODE = 'CC01'
TITLE = 'The Kick'
KIND = 'show'
DESCRIPTION = ('Lucy holds the football and promises not to pull it away. Charlie Brown lunges twice, loses his nerve, '
    'then runs the length of the house. She pulls it. He flies across the porch and lands flat.')
VOICEOVER = 'Every Thanksgiving Lucy holds the football, and every year Charlie Brown believes her.'


def compose():
    C = Chart()
    C.rest(2.4)                                                     # the yard comes up; leaves falling
    C.mark('count')
    C.play('title', style='brushes', bars=(0, 1), tune=False, tag='count')      # four swishes count it in
    C.mark('title')
    C.play('title', style='swing', tag='title')                     # the shirt takes the house, run by run
    C.mark('walk')
    C.play('boy', style='two', bars=(0, 4), bpm=112, tag='walk')    # he walks in from the end of Right
    C.mark('tease')
    C.play('football', style='swing', bars=(0, 4), tag='tease')     # she sets the ball; bar 4 she promises
    C.mark('stop')
    C.play('football', style='stop', bars=(4, 8), tag='stop')       # two false starts, the held breath
    C.mark('ready')
    C.rest(1.3)                                                     # the snare roll winds him up
    C.mark('run')
    C.play('football', style='drive', bars=(0, 4), bpm=168, tag='run')
    C.mark('sprint')
    C.play('football', style='drive', bars=(4, 6), bpm=192, tag='sprint')
    C.mark('pull')
    C.rest(0.9)                                                     # silence: she yanks it, he kicks nothing
    C.mark('fly')
    C.rest(1.9)                                                     # he flies the length of the porch
    C.mark('land')
    C.rest(1.1)                                                     # flat on his back
    C.mark('laugh')
    C.play('football', style='two', bars=(0, 4), bpm=104, tag='laugh')          # her figure, mocking
    C.mark('up')
    C.play('boy', style='ballad', bars=(4, 8), bpm=96, tag='up')    # he sits up
    C.mark('finale')
    C.play('title', style='swing', tag='finale')                    # a Thanksgiving tradition
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
    """Where things are (path distances): the ball and the girl on Porch Front, his mark on Right, where he lands."""
    if not PLACES:
        PLACES.update(ball=S.mid + 30, girl=S.mid + 14, enter=S.L + 50, mark=S.at('Right', 0.35),
                      land=S.at('Left', 0.45))
    return PLACES


def boy_p(S, t):
    """The boy's position at time t: walking in, two lunges and a step back, the run, the flight, flat on Left."""
    P = places(S)
    if t < M['tease']:
        return P['enter'] + (P['mark'] - P['enter']) * float(smoothstep(M['walk'], M['walk'] + 7.0, t))
    if t < M['ready']:
        p = P['mark']
        hits = C.times('hit', 'stop')
        for i, th in enumerate(hits[:2]):                           # a lunge toward the ball, and back
            a = t - th
            if a >= 0:
                p -= 45 * float(smoothstep(0, 0.22, a)) * float(smoothstep(1.2, 0.4, a))
        if len(hits) > 3 and t >= hits[3]:
            p += 28 * float(smoothstep(hits[3], hits[3] + 0.6, t))  # the wind-up step back
        return p
    p0 = P['mark'] + 28
    if t < M['run']:
        return p0
    if t < M['pull']:
        u = (t - M['run']) / (M['pull'] - M['run'])
        return p0 + (P['ball'] - 10 - p0) * u ** 1.6               # accelerating
    if t < M['fly']:
        return P['ball'] - 10
    if t < M['land']:
        u = (t - M['fly']) / (M['land'] - M['fly'])
        return P['ball'] - 10 + (P['land'] - P['ball'] + 10) * u
    return P['land']


def ball_p(S, t):
    """The ball: on the porch, yanked back past the girl at the pull, tossed up and down while she laughs."""
    P = places(S)
    if t < M['pull']:
        return P['ball']
    if t < M['laugh']:
        return P['ball'] - 70 * float(smoothstep(M['pull'], M['pull'] + 0.15, t))
    beat = 60 / 104
    return P['ball'] - 70 + 22 * abs(np.sin(np.pi * (t - M['laugh']) / beat))


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The piano plays the roofline: each note of the tune sparks where its pitch sits across the front."""
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
    beats = np.array(C.beat_times())
    reveal = ['Porch Front', 'Left', 'Right', 'Porch Left', 'Porch Right', 'Side']
    t_title = C.downbeats('title')
    t_count = C.beat_times('count')
    tease_beats = C.beat_times('tease')
    tease_downs = C.downbeats('tease')
    hits = C.times('hit', 'stop')
    run_downs = C.downbeats('run') + C.downbeats('sprint')
    run_beats = np.array(C.beat_times('run') + C.beat_times('sprint'))
    laugh_tune = np.array([n[0] for n in C.tunes('laugh')])
    laugh_downs = C.downbeats('laugh')
    up_downs = C.downbeats('up')
    fin_beats = np.array(C.beat_times('finale'))
    fin_downs = C.downbeats('finale')
    tunes = {g: C.tunes(g) for g in ('title', 'walk', 'tease', 'stop', 'up', 'finale')}
    last_title = tunes['title'][-1][0]
    last_fin = tunes['finale'][-1][0]
    last_up = tunes['up'][-1][0]
    b_title = 60 / 152
    fin_cols = [YELLOW, ORANGE, YELLOW, RED, YELLOW, GOLD, ORANGE, YELLOW]
    yard_lv = [(0, 0.0), (2.4, 1.0), (M['title'], 1.0), (M['title'] + 1, 0.45), (M['walk'] - 0.5, 0.45),
               (M['walk'] + 1.0, 1.0), (hits[2] - 0.1, 1.0), (hits[2] + 0.4, 0.4), (M['ready'], 0.5),
               (M['run'], 0.8), (M['pull'], 0.8), (M['pull'] + 0.12, 0.18), (M['fly'] + 0.8, 0.25),
               (M['land'], 0.35), (M['laugh'], 0.9), (M['finale'], 0.9), (M['finale'] + 1, 0.4), (M['end'], 0.4)]
    leaf_amt = [(0, 0.6), (3, 1.0), (M['laugh'], 1.0), (M['up'], 1.4), (M['finale'], 1.0), (M['finale'] + 2, 1.6),
                (M['end'], 1.0)]

    for f in range(F):
        t = f * DT
        fr = S.yard(t, lv=float(keys(t, yard_lv)), leaves=float(keys(t, leaf_amt)),
                    wind=-25.0 if t < M['finale'] else -60.0)
        p = boy_p(S, t)
        beat = pulse(t, beats, 0.14)

        # the count-in: four amber washes out from the porch
        for tc in t_count:
            fr += S.wave(t, tc, AMBER, 0.55, speed=700, width=90, decay=0.35)

        # the title: the shirt takes the house a run at a time, zigzags on the beat, the piano sparking the roofline
        if M['title'] <= t < M['walk'] + 1.0:
            ph = (t - M['title']) / b_title
            shown = np.zeros(S.N)
            for i, r in enumerate(reveal):
                a = t - t_title[i]
                if a >= 0:
                    shown = np.maximum(shown, S.run[r] * float(smoothstep(0, 0.15, a)))
                    if a < 0.6:
                        fr += light(WHITE, 0.8 * np.exp(-a / 0.18) * S.run[r])
            fade = float(smoothstep(M['walk'] + 1.0, M['walk'], t))
            zig = S.zigzag(ph, lv=0.9 * fade, travel=0.25 * (t > t_title[6]), mask=shown)
            fr = fr * (1 - 0.65 * shown[:, None] * fade) + zig
            fr += keyboard(S, t, tunes['title'], WHITE, 0.75 * fade)
            a = t - last_title
            if 0 <= a < 1.2:                                       # the last note: the whole house yellow
                fr += light(YELLOW, 0.9 * np.exp(-a / 0.35) * np.ones(S.N))

        # he walks in, leaves kicking up at every step of the bass
        if M['walk'] <= t < M['run']:
            fr += keyboard(S, t, tunes['walk'], WHITE, 0.55, width=34)
            steps = [tb for tb in C.times('bass', 'walk') if tb <= t]
            hits_w = [(tb, 0.7, boy_p(S, tb) + 10) for tb in steps[-3:]]
            fr += S.burst(hits_w, t, seed=3, n=5, reach=0.1, colors=LEAVES, life=1.0)
            for tb in steps[-2:]:                                  # each step sends a ripple along the roof
                fr += S.wave(t, tb, AMBER, 0.8, origin=boy_p(S, tb), speed=650, width=60, decay=0.6)

        # she pops up on the porch with the ball; blue "come on" pulses run from her to him on every beat
        if M['tease'] <= t < M['pull']:
            a = t - M['tease']
            lvl = float(smoothstep(0, 0.12, a))
            if a < 0.8:
                fr += light(DRESS, 0.9 * np.exp(-a / 0.25) * S.run['Porch Front'])
            for tb in (tease_beats if t < M['stop'] else hits):
                b = t - tb
                if 0 <= b < 0.9:
                    front = P['ball'] + (p - P['ball']) * b / 0.7
                    fr += light(DRESS, 1.0 * (1 - b / 0.9) * smoothstep(45, 15, np.abs(d - front)) *
                                (d > P['ball']) * (d < p + 20))
            if len(tease_downs) > 3 and tease_downs[3] <= t < M['stop']:      # she promises: the porch floods blue
                b = t - tease_downs[3]
                fr += light(DRESS, 0.8 * np.exp(-b / 1.0) * S.porch)
                fr += light(WHITE, 0.5 * np.exp(-b / 0.2) * S.porch)
            fr += keyboard(S, t, tunes['tease'] + tunes['stop'], DRESS, 0.6, width=34)
            fr = S.bossy(fr, P['girl'], lvl, facing=1)
            if t >= tease_downs[1]:
                b = t - tease_downs[1]
                glint = pulse(t, [n[0] for n in tunes['tease'] + tunes['stop']], 0.15)
                fr = S.football(fr, P['ball'], min(1.0, smoothstep(0, 0.1, b) + 0.3 * glint))
                if b < 0.5:
                    fr += light(WHITE, 0.8 * np.exp(-b / 0.12) * S.blob(P['ball'], 40))

        # stop-time: every hit flashes the front of the house; the third is the held breath
        if M['stop'] <= t < M['ready']:
            for i, th in enumerate(hits):
                a = t - th
                if 0 <= a < 1.0:
                    fr += light(YELLOW if i % 2 else WHITE, 0.75 * np.exp(-a / 0.16) * S.front)
            if len(hits) > 2 and t >= hits[2]:
                fr += light(YELLOW, 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 1.6 * (t - hits[2]))) * S.blob(p, 60))

        # the snare roll: Right fills with yellow from its free end up to him
        if M['ready'] <= t < M['run']:
            u = (t - M['ready']) / (M['run'] - M['ready'])
            front = L - (L - p) * u
            fr += light(YELLOW, (0.4 + 0.5 * u) * S.span(front, L) * (0.7 + 0.3 * np.sin(40 * t)))

        # the run: the path he has covered fills with his zigzag; footfalls flash; the wings flash on every bar
        if M['run'] <= t < M['pull'] + 0.3:
            p0 = P['mark'] + 28
            fade = float(smoothstep(M['pull'] + 0.3, M['pull'], t))
            ph = (t - M['run']) / (60 / 168)
            behind = S.span(p, p0 + 10) * fade
            fr = fr * (1 - 0.6 * behind[:, None]) + S.zigzag(ph, lv=0.85, travel=-0.5, mask=behind)
            fr += light(WHITE, 0.6 * pulse(t, run_beats, 0.1) * S.blob(p, 30) * fade)
            fr += S.run_flash(t, run_downs, cols=(AMBER, ORANGE), runs=('Left', 'Side', 'Porch Left', 'Left'),
                              lv=0.85, decay=0.35)
            if t >= M['sprint']:                                   # the sprint: chevrons to the ball
                for tb in C.beat_times('sprint'):
                    b = t - tb
                    if 0 <= b < 0.5:
                        front = p - (p - P['ball']) * b / 0.3
                        fr += light(YELLOW, 0.8 * (1 - b / 0.5) * np.exp(-((d - front) / 18) ** 2))

        # the pull: she yanks the ball, everything holds its breath, he swings at nothing
        if M['pull'] <= t < M['fly']:
            a = t - M['pull']
            if a > 0.5:
                b = a - 0.5
                fr += light(YELLOW, 0.9 * np.exp(-b / 0.1) * S.span(p - 60, p))
        # the flight: a yellow comet the length of the porch, widest at the top of the arc, sparks behind
        if M['fly'] <= t < M['land']:
            u = (t - M['fly']) / (M['land'] - M['fly'])
            arc = 4 * u * (1 - u)
            fr += light(YELLOW, (0.6 + 0.4 * arc) * S.blob(p, 25 + 50 * arc))
            fr += light(WHITE, 0.5 * arc * S.blob(p, 15))
            tail = S.span(p, P['ball']) * np.exp(-(d - p) / 160) * (0.5 + 0.5 * np.sin(0.6 * d - 50 * t))
            fr += light(GOLD, 0.6 * tail)
        # the landing: a thud runs out across every run, the house shakes, the leaves jump
        if t >= M['land']:
            a = t - M['land']
            if a < 3:
                fr += S.wave(t, M['land'], WHITE, 1.0, origin=P['land'], speed=1500, width=70, decay=0.9)
                fr += S.wave(t, M['land'] + 0.12, YELLOW, 0.8, origin=P['land'], speed=1100, width=50, decay=0.9)
                fr += light(WHITE, np.exp(-a / 0.1) * S.blob(P['land'], 90))
                fr += S.confetti([(M['land'], 1.0, P['land'])], t, colors=LEAVES, n=30, reach=0.5, seed=4)
                fr *= 1 + 0.4 * np.sin(2 * np.pi * 15 * a) * np.exp(-a / 0.25)

        # she laughs: the porch flashes blue on every note, taunts run down the roof to him, leaves pile on him
        if M['laugh'] <= t < M['up'] + 4:
            fade = float(smoothstep(M['up'] + 4, M['up'], t))
            fr += light(DRESS, 0.6 * pulse(t, laugh_tune, 0.2) * S.run['Porch Front'] * fade)
            for tb in laugh_downs:
                b = t - tb
                if 0 <= b < 1.4:
                    front = P['girl'] - (P['girl'] - P['land']) * b / 1.1
                    fr += light(DRESS, 0.8 * (1 - b / 1.4) * np.exp(-((d - front) / 30) ** 2) * (d < P['girl']))
            pile = float(smoothstep(M['laugh'], M['up'], t)) * fade
            fr += S.leaves(t, 1.2 * pile, wind=-6, n=40, seed=9) * S.span(P['land'] - 140, P['land'] + 100)[:, None]
            fr += light(AMBER, 0.35 * pile * S.blob(P['land'], 50))
        if t >= M['pull'] and t < M['up'] + 4:
            fade = float(smoothstep(M['up'] + 4, M['up'], t))
            gp = P['girl'] - 90 * float(smoothstep(M['up'], M['up'] + 4, t))
            fr = S.bossy(fr, gp, fade, facing=1 if t < M['laugh'] else -1)
            fr = S.football(fr, ball_p(S, t) - (P['girl'] - gp), fade)

        # he sits up: warm swells breathe out from him on every bar; his last note warms the whole house
        if M['up'] <= t < M['finale']:
            fr += keyboard(S, t, tunes['up'], GOLD, 0.5)
            for tb in up_downs:
                fr += S.wave(t, tb, AMBER, 0.6, origin=p, speed=500, width=140, decay=1.4)
            fr += S.sweep(t, last_up, 2.0, GOLD, 0.7, frm='side', width=120, trail=1.0)

        # the finale: zigzags on the whole house, a colour a bar, a run flashing on every beat, a sweep, the button
        if t >= M['finale']:
            ph = (t - M['finale']) / b_title
            bar = min(int(ph // 4), 7)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            fr = fr * (1 - 0.6 * fade) + S.zigzag(ph, lv=0.85 * fade, col=fin_cols[bar], travel=0.25 * (bar >= 4))
            fr += S.run_flash(t, fin_beats, cols=(WHITE, YELLOW), lv=0.6, decay=0.15)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.7)
            fr += S.sweep(t, fin_downs[6], 2.4, WHITE, 0.9, frm='right', width=90, trail=0.5)
            a = t - last_fin
            if 0 <= a < 1.2:
                fr += light(YELLOW, 0.7 * np.exp(-a / 0.3) * np.ones(S.N))
            a = t - M['button']
            if a >= 0:
                fr += light(YELLOW, np.exp(-a / 0.45) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * np.ones(S.N))

        # the boy himself, over everything: upright, flying, flat, sitting up
        if t >= M['walk'] - 0.2:
            if t < M['land']:
                run = 1.0 if M['run'] <= t < M['pull'] else 0.0
                bob = 0.85 + 0.15 * beat
                fr = S.boy(fr, p, min(1.2, bob + 0.3 * (M['fly'] <= t)), facing=-1, t=t, run=run)
            elif t < M['up'] + 3:
                u = float(smoothstep(M['up'], M['up'] + 3, t))
                fr = S.boy_flat(fr, p, 1 - u)
                fr = S.stars(fr, p + 18, t, 0.9 * float(smoothstep(M['up'] + 1.5, M['up'], t)))
                if u > 0:
                    fr = S.boy(fr, p, u, facing=1, t=t)
            else:
                fr = S.boy(fr, p, 1.0 + 0.2 * beat, facing=1, t=t, glow=0.45)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    parts = {
        ('title', 'tune'): [('piano', 0, 8, 0.85), ('vibes', 0, -10, 0.3)],
        ('walk', 'tune'): [('piano', 0, -4, 0.8)],
        ('walk', 'comp'): [('piano', 0, -14, 0.4)],
        ('tease', 'tune'): [('harmon trumpet', 0, 6, 1.0), ('piano', 12, -24, 0.25)],
        ('stop', 'tune'): [('harmon trumpet', 0, 8, 1.0)],
        ('stop', 'hit'): [('piano', 0, 6, 0.8), ('muted horn', 0, -4, 0.45)],
        ('run', 'tune'): [('piano', 0, 10, 0.85), ('xylo', 12, -8, 0.3)],
        ('sprint', 'tune'): [('piano', 0, 14, 0.9), ('xylo', 12, -4, 0.35), ('trumpets', 0, -10, 0.35)],
        ('sprint', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -12, 0.3)],
        ('laugh', 'tune'): [('buzz trombone', 0, 6, 0.75), ('muted horn', 0, -6, 0.4)],
        ('laugh', 'comp'): [('piano', 0, -16, 0.35)],
        ('up', 'tune'): [('piano', 0, -2, 0.85)],
        ('up', 'comp'): [('piano', 0, -12, 0.45), ('choir', 12, -22, 0.35)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('vibes', 0, -10, 0.3)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    # the yard at the end of the afternoon: a soft open chord on the choir and vibes before the count-in
    for m in (65, 69, 72, 76):
        B.play('choir', m, 0.3, 2.3, 50, gain=0.35)
    B.play('vibes', 77, 1.2, 1.2, 60, gain=0.25)
    # his footsteps in, and her pop up with the ball
    B.steps(M['walk'], M['walk'] + 7.0, beat=60 / 112, pan=lambda tt: S.pan(boy_p(S, tt)), gain=0.7)
    B.boing(M['tease'], pan=S.pan(P['girl']), gain=0.8)
    B.hit('woodblock', C.downbeats('tease')[1], 110, gain=0.6, pan=S.pan(P['ball']))
    B.play('choir', 76, C.downbeats('tease')[3], 1.6, 60, gain=0.35)          # she promises, sweetly
    B.play('choir', 72, C.downbeats('tease')[3], 1.6, 56, gain=0.35)
    # two false starts: a scuff and a gulp each; the held breath on a tremolo
    for th in C.times('hit', 'stop')[:2]:
        B.steps(th, th + 0.3, beat=0.14, pan=S.pan(P['mark']), gain=0.8)
        B.slide(th + 0.5, 0.35, up=False, pan=S.pan(P['mark']), gain=0.4, lo=700, hi=1100)
    th = C.times('hit', 'stop')[2]
    B.play('violins trem', 68, th, 2.2, 60, gain=0.3)
    # the wind-up roll, then the run's footsteps, faster and faster
    B.roll(M['ready'], M['run'], pan=S.pan(P['mark']), gain=0.9)
    B.hit('cymbal swell', M['ready'] - 0.2, 90, gain=0.35)
    ts, t = [], M['run']
    while t < M['pull']:
        ts.append(t)
        u = (t - M['run']) / (M['pull'] - M['run'])
        t += 0.3 - 0.14 * u
    for t in ts:
        B.hit('hoof soft', t, 96, gain=0.4, pan=S.pan(boy_p(S, t)), fx=True)
    # the pull: the ball whooshes away, a beat of nothing, the kick at air, then the flight and the thud
    B.effects([(0, -3), (M['pull'] - 0.5, 1), (M['laugh'] + 1, -3), (M['finale'], -4)])
    B.whoosh(M['pull'], 0.35, up=True, pan=S.pan(P['ball']), gain=0.9)
    B.whoosh(M['pull'] + 0.5, 0.4, up=False, pan=S.pan(P['ball']), gain=0.8)
    B.slide(M['fly'], 1.0, up=True, pan=S.pan(P['ball']), gain=0.9, lo=450, hi=1500)
    B.slide(M['fly'] + 0.95, 0.95, up=False, pan=S.pan(P['land']), gain=0.9, lo=350, hi=1500)
    B.hit('cymbal swell', M['fly'] - 0.3, 100, gain=0.4)
    B.thud(M['land'], pan=S.pan(P['land']), gain=1.0)
    B.hit('crash', M['land'], 118, gain=0.5, pan=S.pan(P['land']))
    B.hit('timpani', M['land'] + 0.02, 120, pitch=-5, gain=0.5)
    B.hit('vibraslap', M['land'] + 0.4, 110, gain=0.5, pan=S.pan(P['land']))
    for k in range(3):                                              # stars: three little glock twinkles
        B.play('glock', 84 - 3 * k, M['land'] + 0.6 + 0.18 * k, 0.3, 70, pan=S.pan(P['land']), gain=0.35)
    # she laughs; his groan of a fall on the trombone as the figure ends
    B.kids(M['laugh'] + 0.1, M['laugh'] + 1.8, 'laugh', level=0.7, pan=S.pan(P['girl']), voices=1, seed=2)
    B.fall(M['up'] - 1.2, pan=S.pan(P['land']), gain=0.7)
    # the finale's sweep and the button
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - M['finale']) / 10)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.finish()
