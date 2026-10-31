"""Snoopy's Feast: back home, Snoopy and Woodstock have a Thanksgiving dinner of their own.

A clear night over the backyard, stars twinkling on every run. Snoopy struts in from the free end of Right in his
tall chef's toque to his jaunty theme, one step a beat, and the house lights up behind him like theatre bulbs that
step with the walking bass, every bar flashing a run white. Woodstock pops up on the porch to his quick
twitter, yellow sparks flying off every note. The feast's theme sets the table: the ping-pong table appears on Porch
Front and a dish lands on it on every beat with a clink and a flash (toast, popcorn, pretzels, jelly beans,
cranberries, pie). A snare roll, and the turkey: a golden fanfare in stop-time, the whole house flashing roast gold
from the porch out. Then the twist: Woodstock looks at the turkey, the house goes still, and he understands what it
is. A gasp, and he faints flat, tumbling down the porch on a slide whistle and a trombone's wah-wah. Snoopy fans
him back with brushes on the snare, white swishes over him, and quietly gobbles the turkey himself, four crunches, the
platter shrinking, while Woodstock gets the jelly beans. The feast swings: rainbow jelly-bean stripes chase across
every run, crunch on the beat. Then the wishbone: the two of them pull it in stop-time, a white line between them
straining on every hit, and on the snap the little bird wins the big half and loops the whole house in a yellow
streak to his twitter. The main title closes it on the whole house, white and yellow zigzags, a run on every beat, a
sweep, a woof and a last chord.

compose() lays the music end to end (pixelhome/chef_charlie.py); render() and score() read its events and marks.
beagle_p() and bird_p() are the two of them, shared by both."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, GOLD, BIRD, BEAGLE, TURKEY,
                                    TOAST, POPCORN, PRETZEL, CRANBERRY, ORANGE, JELLY, NIGHT)

CODE = 'CC13'
TITLE = "Snoopy's Feast"
KIND = 'show'
DESCRIPTION = ('Back home, Snoopy and Woodstock sit down to a turkey dinner of their own. '
               'Woodstock takes one look at the turkey and faints. Then they pull the wishbone.')
VOICEOVER = 'Back home, Snoopy cooks a real turkey dinner, but Woodstock is a bird.'

DISHES = ((-9, 'toast'), (-6, 'popcorn'), (-3, 'pretzels'), (4, 'jellybeans'), (7, 'cranberry'), (10, 'pie'))


def compose():
    C = Chart()
    C.rest(1.2)                                                     # the night comes up
    C.mark('strut')
    C.play('beagle', style='swing', tag='strut')                    # the chef struts in
    C.mark('bird')
    C.play('bird', style='swing', tag='bird')                       # the little bird pops up
    C.mark('set')
    C.play('feast', style='two', bars=(0, 4), bpm=150, tag='set')   # the table, a dish a beat
    C.mark('roll')
    C.rest(1.5)                                                     # a snare roll
    C.mark('turkey')
    C.play('feast', style='stop', bars=(0, 2), bpm=150, tag='turkey')            # the turkey!
    C.mark('stare')
    C.rest(1.5)                                                     # the bird looks at it
    C.mark('faint')
    C.rest(2.2)                                                     # and faints
    C.mark('fan')
    C.play('beagle', style='brushes', bars=(0, 2), tune=False, tag='fan')        # fanned back to life
    C.mark('gobble')
    C.play('beagle', style='walk', bars=(6, 8), tag='gobble')       # Snoopy gobbles the turkey himself
    C.mark('feast')
    C.play('feast', style='swing', tag='feast')                     # dinner
    C.mark('wish')
    C.play('football', style='stop', bars=(4, 8), bpm=132, tag='wish')           # the wishbone
    C.mark('snap')
    C.rest(0.7)
    C.mark('loop')
    C.play('bird', style='drive', bpm=168, tag='loop')              # the bird wins, and loops the house
    C.play('bird', style='swing', bpm=168, tag='loop2')
    C.mark('finale')
    C.play('title', style='swing', bars=(2, 8), tag='finale')
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
        PLACES.update(table=S.mid, beagle=S.mid - 82, bird=S.mid + 78, enter=S.L + 40, floor=S.at('Porch Right', 0.4),
                      wb=S.mid, wb_dog=S.mid - 24, wb_bird=S.mid + 22)
    return PLACES


def beagle_p(S, t):
    """Snoopy: strutting in from past the end of Right a step a beat, then at his place; in to Woodstock to fan
    him; to the middle for the wishbone."""
    P = places(S)
    if t < M['bird']:
        beats = C.beat_times('strut')
        n = len(beats)
        k = sum(b <= t for b in beats)
        frac = 0.0
        if 0 < k < n:
            frac = float(smoothstep(0, 0.35, (t - beats[k - 1]) / (beats[k] - beats[k - 1])))
        u = min((k - 1 + frac) / (n - 1), 1.0) if k else 0.0
        return P['enter'] + (P['beagle'] - P['enter']) * u
    if t < M['fan']:
        return P['beagle']
    if t < M['gobble']:
        return P['beagle'] + (P['floor'] - 40 - P['beagle']) * float(smoothstep(M['fan'], M['fan'] + 0.8, t))
    if t < M['wish']:
        return float(keys(t, [(M['gobble'], P['floor'] - 40), (M['gobble'] + 1.0, P['beagle'])]))
    if t < M['finale']:
        return float(keys(t, [(M['wish'], P['beagle']), (M['wish'] + 0.8, P['wb_dog']),
                              (M['snap'], P['wb_dog']), (M['snap'] + 0.3, P['wb_dog'] - 30)]))
    return P['wb_dog'] - 30


def bird_p(S, t):
    """Woodstock: at his place, tumbling down the porch when he faints, back up, in for the wishbone, then around
    the whole house and home."""
    P = places(S)
    if t < M['faint']:
        return P['bird']
    if t < M['fan']:
        return P['bird'] + (P['floor'] - P['bird']) * float(smoothstep(M['faint'] + 0.3, M['faint'] + 1.6, t))
    if t < M['gobble']:
        return P['floor']
    if t < M['wish']:
        return float(keys(t, [(M['gobble'], P['floor']), (M['gobble'] + 1.0, P['bird'])]))
    if t < M['loop']:
        return float(keys(t, [(M['wish'], P['bird']), (M['wish'] + 0.8, P['wb_bird']), (M['snap'], P['wb_bird'])]))
    # the victory loop: out to the free end of Right, all the way back to the far end of Left, and home
    t0, t1 = M['loop'], M['finale']
    return float(keys(t, [(t0, P['wb_bird']), (t0 + 0.32 * (t1 - t0), S.L - 20), (t0 + 0.8 * (t1 - t0),
                          S.at('Left', 0.05)), (t1, P['bird'])]))


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
    strut_beats = C.beat_times('strut')
    strut_downs = C.downbeats('strut')
    bird_t = np.array([n[0] for n in C.tunes('bird')])
    set_beats = C.beat_times('set')
    turkey_hits = C.times('hit', 'turkey')
    gobble_t = C.downbeats('gobble') + [b for b in C.beat_times('gobble')[2::4]]
    gobble_t = sorted(gobble_t)[:4]
    feast_beats = np.array(C.beat_times('feast'))
    feast_downs = C.downbeats('feast')
    wish_hits = C.times('hit', 'wish')
    loop_t = np.array([n[0] for n in C.tunes('loop') + C.tunes('loop2')])
    fin_beats = np.array(C.beat_times('finale'))
    fin_downs = C.downbeats('finale')
    tunes = {g: C.tunes(g) for g in ('strut', 'set', 'feast', 'finale')}
    bg = [(0, 0.0), (1.2, 0.9), (M['stare'], 0.9), (M['stare'] + 0.25, 0.3), (M['fan'], 0.35), (M['gobble'], 0.7),
          (M['feast'], 0.6), (M['wish'], 0.6), (M['wish'] + 0.5, 0.35), (M['loop'], 0.7), (M['finale'], 0.5), (D, 0.5)]

    for f in range(F):
        t = f * DT
        lv = float(keys(t, bg))
        bp, wp = beagle_p(S, t), bird_p(S, t)
        fr = S.night(t, lv)
        fr += light(NIGHT, 0.25 * lv * S.wings)

        # the strut: theatre bulbs step along the stretch behind him with the walking bass, a run flashes each bar
        if M['strut'] <= t < M['set'] + 1:
            fade = float(smoothstep(M['set'] + 1, M['set'], t))
            nb = sum(b <= t for b in strut_beats)
            behind = S.span(bp + 10, L + 10, 8)
            fr = fr * (1 - 0.3 * behind[:, None]) + S.chase(2 * nb, cols=(BEAGLE, None, AMBER, None), lv=0.6 * fade,
                                                            spacing=2, mask=behind)
            fr += S.run_flash(t, strut_downs, cols=(WHITE, AMBER), lv=0.85 * fade, decay=0.5)
            fr += keyboard(S, t, tunes['strut'], WHITE, 0.5 * fade)

        # the bird pops up: a yellow flash on the porch, sparks off every note of his twitter
        if M['bird'] <= t < M['set'] + 2:
            a = t - M['bird']
            fr += light(BIRD, 0.9 * np.exp(-a / 0.25) * S.run['Porch Front'])
            nb = int((bird_t <= t).sum())
            fr += S.chase(nb, cols=(BIRD, None, None), lv=0.55 * float(smoothstep(M['set'] + 2, M['set'], t)),
                          spacing=2, mask=S.wings + S.run['Porch Left'] + S.run['Porch Right'])
            hits = [(tb, 0.7, P['bird']) for tb in bird_t]
            fr += S.burst(hits, t, seed=2, n=4, reach=0.25, colors=(BIRD, WHITE), life=0.8)

        # the table, a dish landing on every beat; then the turkey in the middle
        if t >= M['set'] - 0.2 and t < M['finale']:
            n_d = sum(b <= t for b in set_beats[1::2])
            fr = S.table(fr, P['table'], min(1.0, (t - M['set'] + 0.2) / 0.3), half=13, food=())
            for i, (o, kind) in enumerate(DISHES[:n_d]):
                fr = S.dish(fr, P['table'] + o * 4.9, kind, 1.0, t)
            for i, tb in enumerate(set_beats[1::2][:len(DISHES)]):
                a = t - tb
                if 0 <= a < 0.5:
                    fr += light(WHITE, 0.8 * np.exp(-a / 0.1) * S.blob(P['table'] + DISHES[i][0] * 4.9, 18))
                    fr += S.wave(t, tb, JELLY[i], 0.6, origin=P['table'], speed=1000, width=60, decay=0.5)
            if t < M['roll'] + 0.5:
                fr += S.run_flash(t, set_beats[1::2][:len(DISHES)], cols=(TOAST, POPCORN, PRETZEL, JELLY[4],
                                  CRANBERRY, AMBER), runs=('Left', 'Right', 'Porch Left', 'Porch Right', 'Side',
                                                           'Right'), lv=0.75, decay=0.9)
            # the turkey: whole, then gobbled bite by bite
            if t >= M['turkey']:
                bites = sum(b <= t for b in gobble_t)
                lvl = 1.0 - 0.25 * bites if t < M['feast'] else 0.0
                if lvl > 0:
                    fr = S.dish(fr, P['table'], 'turkey', lvl, t)

        # the turkey fanfare: gold flashing out over the house from the porch on every hit
        if M['roll'] <= t < M['stare'] + 0.5:
            if t < M['turkey']:
                u = (t - M['roll']) / (M['turkey'] - M['roll'])
                fr += light(GOLD, 0.5 * u * S.porch * (0.7 + 0.3 * np.sin(50 * t)))
            for i, th in enumerate(turkey_hits):
                a = t - th
                if 0 <= a < 1.5:
                    fr += S.wave(t, th, GOLD if i % 2 else TURKEY, 1.0, speed=1400, width=110, decay=0.7)
                    fr += light(WHITE, 0.6 * np.exp(-a / 0.1) * S.blob(P['table'], 60))
            fr += S.sweep(t, M['turkey'], 1.2, GOLD, 0.8, frm='centre', width=120, trail=0.5)
            if t >= M['turkey']:
                fr += light(GOLD, 0.45 * float(smoothstep(M['stare'] + 0.3, M['stare'], t)) * np.ones(S.N))

        # the stare: he looks at the turkey; a slow pulse from him to it, twice; then the gasp and the faint
        if M['stare'] <= t < M['fan']:
            a = t - M['stare']
            for k in (0.3, 0.9):
                b = a - k
                if 0 <= b < 0.6:
                    q = wp + (P['table'] - wp) * b / 0.4
                    fr += light(BIRD, 0.8 * (1 - b / 0.6) * np.exp(-((d - q) / 10) ** 2))
            b = t - M['faint']
            if 0 <= b < 2.2:
                fr += light(WHITE, 0.8 * np.exp(-b / 0.12) * S.blob(P['bird'], 50))
                tail = S.span(wp, P['bird'], 4) * np.exp(-np.abs(d - wp) / 60)
                fr += light(BIRD, 0.6 * tail * (b < 1.6))

        # fanned back to life: white swishes over him on every beat; Snoopy gobbles the turkey (crunches)
        if M['fan'] <= t < M['feast']:
            for tb in C.beat_times('fan'):
                a = t - tb
                if 0 <= a < 0.6:
                    q = wp + 30 * np.sin(np.pi * a / 0.6) * (1 if int(tb * 10) % 2 else -1)
                    fr += light(WHITE, 0.7 * (1 - a / 0.6) * np.exp(-((d - q) / 16) ** 2))
            for k, tb in enumerate(C.beat_times('fan')):
                fr += S.sweep(t, tb, 0.5, WHITE, 0.4, frm='side' if k % 2 else 'right', width=120, trail=0.3)
            fr += S.run_flash(t, gobble_t, cols=(TURKEY, GOLD), runs=('Porch Front', 'Left', 'Right', 'Porch Front'),
                              lv=0.8, decay=0.4)
            a = t - M['gobble']
            if 0 <= a < 0.5:
                fr += light(BIRD, 0.9 * np.exp(-a / 0.15) * S.blob(wp, 40))        # he's up!
            for tb in gobble_t:
                a = t - tb
                if 0 <= a < 0.5:
                    fr += S.burst([(tb, 0.7, P['table'])], t, seed=int(tb * 10), n=8, reach=0.2,
                                  colors=(TURKEY, GOLD, WHITE), life=0.5)

        # the feast: rainbow jelly-bean stripes chase every run, a crunch of light on the beat
        if M['feast'] <= t < M['wish'] + 0.6:
            fade = float(smoothstep(M['wish'] + 0.6, M['wish'], t))
            ph = (t - M['feast']) / (60 / 184)
            mask = (1 - S.blob(P['table'], 90)) * fade
            fr = fr * (1 - 0.6 * mask[:, None]) + S.stripes(ph / 2, list(JELLY[:7]), lv=0.65, period=30, mask=mask)
            fr += S.run_flash(t, feast_beats[::2], cols=(WHITE, GOLD), lv=0.45 * fade, decay=0.18)
            fr += keyboard(S, t, tunes['feast'], WHITE, 0.6 * fade)
            fr += S.confetti([(tb, 0.8, P['table']) for tb in feast_downs[::2]], t, colors=JELLY, n=16, seed=8)

        # the wishbone: a white line between them straining on every hit
        if M['wish'] + 0.6 <= t < M['loop']:
            k = sum(th <= t for th in wish_hits)
            c = t - (wish_hits[k - 1] if k else M['wish'])
            shove = (40 + 25 * k) * (1 if k % 2 else -1) * float(np.exp(-c / 0.6)) if k else 0.0
            edge = P['wb'] + shove
            tug = 0.35 + 0.1 * k
            fr = fr * 0.6 + light(BEAGLE, tug * S.span(0, edge, 15) * S.front) + \
                light(BIRD, tug * S.span(edge, L, 15) * S.front)
            a, b = sorted((bp + 6, wp - 4))
            strain = sum(np.exp(-(t - th) / 0.3) for th in wish_hits if th <= t)
            line = S.span(a, b, 3)
            fr += light(WHITE, (0.45 + 0.4 * min(strain, 1.2)) * line * (0.85 + 0.15 * np.sin(60 * t)))
            for i, th in enumerate(wish_hits):
                c = t - th
                if 0 <= c < 0.8:
                    fr += light(BEAGLE if i % 2 else BIRD, 0.7 * np.exp(-c / 0.2) * S.front)
            c = t - M['snap']
            if c >= 0:
                fr += light(WHITE, 1.0 * np.exp(-c / 0.1) * S.blob(P['wb'], 80))
                fr += S.burst([(M['snap'], 1.0, P['wb'])], t, seed=5, n=16, colors=(WHITE, BIRD))

        # the victory loop: a yellow streak round the whole house to his twitter
        if M['loop'] <= t < M['finale'] + 1:
            fade = float(smoothstep(M['finale'] + 1, M['finale'], t))
            prev = bird_p(S, max(t - 0.8, M['loop']))
            fr += light(BIRD, 0.85 * fade * S.span(prev, wp, 10) * np.exp(-np.abs(d - wp) / 400))
            fr += S.chase(int((loop_t <= t).sum()), cols=(BIRD, None, None, None), lv=0.4 * fade, spacing=2)
            fr += light(WHITE, 0.6 * fade * pulse(t, loop_t, 0.12) * S.blob(wp, 30))
            fr += S.wave(t, M['loop'], BIRD, 0.9, origin=P['wb'], speed=1200, width=80, decay=0.8)
            hits = [(tb, 0.5, bird_p(S, tb)) for tb in loop_t if t - 0.8 < tb <= t]
            fr += S.burst(hits, t, seed=11, n=4, reach=0.2, colors=(BIRD, YELLOW), life=0.8)

        # the finale: white and yellow zigzags on the whole house, a run on every beat, a sweep, the button
        if t >= M['finale']:
            ph = (t - M['finale']) / (60 / 152)
            bar = min(int(ph // 4), 5)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            col = (YELLOW, BEAGLE, YELLOW, ORANGE, YELLOW, GOLD)[bar]
            fr = fr * (1 - 0.6 * fade) + S.zigzag(ph, lv=0.85 * fade, col=col, travel=0.25 * (bar >= 2))
            fr += S.run_flash(t, fin_beats, cols=(WHITE, BIRD), lv=0.6, decay=0.15)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.7)
            fr += S.sweep(t, fin_downs[4], 2.4, WHITE, 0.9, frm='right', width=90, trail=0.5)
            a = t - M['button']
            if a >= 0:
                fr += light(YELLOW, np.exp(-a / 0.45) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * np.ones(S.N))

        # the two of them, over everything
        beat = pulse(t, C.beat_times(), 0.12)
        if t >= M['strut'] - 0.2:
            facing = -1 if t < M['bird'] else (1 if wp >= bp else -1)
            fr = S.beagle(fr, bp, 1.0 + 0.15 * beat, facing=facing, t=t, wag=1.0, chef=True)
        if t >= M['bird'] - 0.05:
            if M['faint'] + 0.3 <= t < M['gobble']:
                fl = 0.0                                            # out cold
                lvl = 0.55
            else:
                fl, lvl = 1.0, 1.0
            fr = S.bird(fr, wp, lvl, t=t, flutter=fl, facing=-1 if wp > bp else 1)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    from pixelhome.audio import note
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.05)
    parts = {
        ('strut', 'tune'): [('piano', 0, 6, 0.85), ('muted horn', 0, -10, 0.4)],
        ('strut', 'comp'): [('piano', 0, -10, 0.5)],
        ('bird', 'tune'): [('xylo', 0, -4, 0.6), ('piano', 12, -16, 0.4)],
        ('bird', 'comp'): [('piano', 0, -14, 0.4)],
        ('set', 'tune'): [('piano', 0, 4, 0.85), ('vibes', 12, -20, 0.25)],
        ('set', 'comp'): [('piano', 0, -12, 0.45)],
        ('turkey', 'tune'): [('harmon trumpet', 0, 10, 1.0), ('trumpets', 0, -6, 0.4)],
        ('turkey', 'hit'): [('piano', 0, 8, 0.8), ('horns', 0, -2, 0.5), ('trombones', -12, -4, 0.4)],
        ('gobble', 'tune'): [('buzz trombone', 0, 0, 0.7)],
        ('feast', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -4, 0.45), ('xylo', 12, -16, 0.25)],
        ('feast', 'comp'): [('piano', 0, -6, 0.5)],
        ('wish', 'tune'): [('muted horn', 0, 6, 0.7), ('piano', 0, -10, 0.4)],
        ('wish', 'hit'): [('piano', 0, 6, 0.8), ('pizz', 0, -6, 0.4)],
        ('loop', 'tune'): [('xylo', 0, 0, 0.6), ('piano', 0, 0, 0.6)],
        ('loop', 'comp'): [('piano', 0, -8, 0.45)],
        ('loop2', 'tune'): [('xylo', 0, 0, 0.6), ('piano', 0, 4, 0.7), ('flutes', 0, -12, 0.35)],
        ('loop2', 'comp'): [('piano', 0, -8, 0.45)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('vibes', 0, -10, 0.25)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    table, bird, dog = S.pan(P['table']), S.pan(P['bird']), S.pan(P['beagle'])
    # the night: a soft chord, a woof as he comes in, his footsteps
    for m in (60, 64, 67, 71):
        B.play('choir', m, 0.2, 1.3, 44, gain=0.3)
    B.woof(M['strut'] + 0.1, pan=S.pan(P['enter'] - 60), big=0.7)
    B.chirp(M['bird'], n=5, pan=bird, gain=0.9)
    B.boing(M['bird'], pan=bird, gain=0.5, high=1.4)
    # a dish on the table on every other beat: a clink each, rising
    for i, tb in enumerate(C.beat_times('set')[1::2][:6]):
        B.clink(tb, pan=S.pan(P['table'] + 4.9 * [-9, -6, -3, 4, 7, 10][i]), gain=0.6, pitch=2 * i)
    # the roll and the turkey
    B.roll(M['roll'], M['turkey'], pan=table, gain=0.9)
    B.hit('cymbal swell', M['roll'] - 0.2, 96, gain=0.4)
    B.hit('crash', M['turkey'], 118, gain=0.5, pan=table)
    # the stare: silence but a tiny chirp, twice; the gasp; the faint
    B.chirp(M['stare'] + 0.3, n=1, pan=bird, gain=0.6)
    B.chirp(M['stare'] + 0.9, n=1, pan=bird, gain=0.6)
    B.kids(M['faint'], M['faint'] + 0.6, 'gasp', level=0.4, pan=bird, voices=1, seed=9)
    B.slide(M['faint'] + 0.3, 1.2, up=False, pan=S.pan(P['floor']), gain=0.8, lo=400, hi=1600)
    B.thud(M['faint'] + 1.55, pan=S.pan(P['floor']), gain=0.3)
    B.fall(M['faint'] + 0.6, pan=S.pan(P['floor']), gain=0.6)
    # fanned back: a whoosh on every beat, then he's up with a chirp and a boing
    for tb in C.beat_times('fan'):
        B.whoosh(tb, 0.35, up=bool(int(tb * 10) % 2), pan=S.pan(P['floor']), gain=0.35)
    B.chirp(M['gobble'], n=4, pan=S.pan(P['floor']), gain=0.9)
    B.boing(M['gobble'] + 0.05, pan=S.pan(P['floor']), gain=0.5, high=1.3)
    # Snoopy gobbles the turkey: four crunches
    downs = sorted(C.downbeats('gobble') + C.beat_times('gobble')[2::4])[:4]
    for tb in downs:
        B.crunch(tb, bites=1, pan=table, gain=0.8)
    # the feast: a crunch on every other bar and clinks
    for i, tb in enumerate(C.downbeats('feast')):
        if i % 2:
            B.crunch(tb + 0.33, bites=2, pan=table, gain=0.5)
        else:
            B.clink(tb, pan=table, gain=0.4, pitch=4)
    # the wishbone: a creak on every hit, the snap, the bird's victory
    for th in C.times('hit', 'wish'):
        B.hit('guiro', th + 0.05, 90, gain=0.35, pan=table)
    B.hit('slapstick', M['snap'], 122, gain=0.7, pan=table, fx=True)
    B.hit('wood', M['snap'] + 0.01, 110, gain=0.5, pan=table, fx=True)
    B.kids(M['snap'] + 0.05, M['snap'] + 0.5, 'gasp', level=0.3, pan=table, voices=2, seed=12)
    B.slide(M['snap'] + 0.15, 0.5, up=True, pan=table, gain=0.6)
    B.chirp(M['loop'], n=6, pan=table, gain=1.0)
    t0, t1 = M['loop'], M['finale']
    B.whoosh(t0 + 0.1, 0.32 * (t1 - t0) - 0.2, up=True, gain=0.4, pan=lambda tt: 0.7)
    B.whoosh(t0 + 0.32 * (t1 - t0), 0.48 * (t1 - t0), up=False, gain=0.4, pan=lambda tt: -0.6)
    # the finale: sweep, woof and button
    B.whoosh(C.downbeats('finale')[4], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.woof(M['button'] + 0.5, pan=dog, big=1.0)
    B.effects([(0, -3), (M['finale'], -4)])
    B.finish()
