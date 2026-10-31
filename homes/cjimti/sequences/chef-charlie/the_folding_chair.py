"""The Folding Chair: Snoopy battles a folding lawn chair that won't stay up, then sets out the ping-pong table.

The backyard at evening (a deep blue sky, the lawn along the wings, the party bulbs still dark); the drummer counts in
on brushes. Snoopy pops up on the porch and struts out along Porch Right onto Right to his jaunty theme, carrying
a folded lawn chair, a white marquee running along the roof he has crossed. Stop-time: on the first hit the chair
half opens, on the second it's up (green-and-white webbing spreading along Right), on the third he goes to sit, and
on the fourth it folds with a clatter, sparks and the house shaking. Again, carefully: bass and brushes only, a tiptoe
on pizzicato strings, the webbing spreading slowly as the rest of the house dims; he pats it; a held breath; it
holds; he turns and woofs in triumph, gold on the porch, and it clatters shut behind him. The battle: the trio doubles
up and the chair hops from run to run, snapping open and shut on every beat, landing with a crash and a burst of
sparks every other bar while he chases it and the whole house runs a green-and-white marquee, faster for the last
round, until it folds up with him inside. Stars. He kicks free and flings it off the back of Side, a comet and a far
away clatter. Then the main title: he sets out the ping-pong table on the porch, unfolding a beat at a time, the net
clicks in, and the party bulbs light up a run on every bar. Four chairs pop open round the table; the last one wobbles
and stays up. His strut on the whole house in webbing stripes and zigzags, a sweep from the end of Right, and on the
last chord he sits.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks.
chair() (where the chair is and how open) and dog_p() are shared too, so every clatter lands on the music."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, WHITE, GOLD, AMBER, LAWN, TABLE, BEAGLE, WARM, ICE,
                                    GREEN, YELLOW)

CODE = 'CC04'
TITLE = 'The Folding Chair'
KIND = 'show'
DESCRIPTION = ('Snoopy takes on a folding lawn chair that will not stay up, round after round, until it folds up with '
    'him inside. Then he sets out the ping-pong table in the backyard.')
VOICEOVER = 'Before any dinner, Snoopy must defeat one stubborn folding lawn chair.'


def compose():
    C = Chart()
    C.rest(1.4)                                                     # the backyard comes up
    C.mark('count')
    C.play('beagle', style='brushes', bars=(0, 1), tune=False, tag='count')
    C.mark('strut')
    C.play('beagle', style='swing', bars=(0, 4), tag='strut')       # out onto Right with the chair
    C.mark('try1')
    C.play('beagle', style='stop', bars=(4, 8), tag='try1')         # half, up, sit... clatter
    C.mark('try2')
    C.play('beagle', style='walk', bars=(0, 4), bpm=104, tag='try2')    # again, carefully
    C.mark('hold')
    C.rest(1.4)                                                     # it holds
    C.mark('woof')
    C.rest(0.8)                                                     # he woofs in triumph
    C.mark('clatter2')
    C.rest(1.0)                                                     # it folds behind him
    C.mark('fight')
    C.play('beagle', style='drive', bars=(0, 8), bpm=150, tag='fight')
    C.mark('fight2')
    C.play('beagle', style='drive', bars=(4, 8), bpm=168, tag='fight2')
    C.mark('heap')
    C.rest(1.4)                                                     # folded up with him inside
    C.mark('fling')
    C.rest(1.4)                                                     # he flings it off the back of Side
    C.mark('table')
    C.play('title', style='swing', tag='table')                     # the ping-pong table, the bulbs
    C.mark('set')
    C.play('beagle', style='swing', bars=(4, 8), bpm=132, tag='set')    # four chairs pop open
    C.mark('finale')
    C.play('beagle', style='swing', bpm=132, tag='finale')
    C.mark('button')
    C.button('C6', bpm=132, beats=2)
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
HITS = C.times('hit', 'try1')
LANDS = [C.downbeats('fight')[i] for i in (1, 3, 5, 7)] + [C.downbeats('fight2')[i] for i in (1, 3)]
FLIGHT = 0.45

PLACES = {}


def places(S):
    if not PLACES:
        PLACES.update(chair=S.at('Right', 0.3), table=S.mid, side_end=-80.0,
                      spots=[S.at('Porch Front', 0.72), S.at('Left', 0.5), S.at('Porch Front', 0.25),
                             S.at('Right', 0.55), S.at('Left', 0.8), S.mid])
        P = PLACES
        P['stand'] = P['chair'] - 30
        P['seats'] = [S.mid - 150, S.mid + 150, S.mid - 100, S.mid + 100]
    return PLACES


def chair(S, t):
    """(where the chair is, how open 0..1, flying?) at time t."""
    P = places(S)
    if t < M['try1']:
        return dog_p(S, t) + 28, 0.0, False
    if t < M['try2']:
        u = 0.0
        if t >= HITS[0]:
            u = 0.5 * float(smoothstep(HITS[0], HITS[0] + 0.1, t))
        if t >= HITS[1]:
            u = 0.5 + 0.5 * float(smoothstep(HITS[1], HITS[1] + 0.1, t))
        if t >= HITS[3]:
            u = float(smoothstep(HITS[3] + 0.08, HITS[3], t))
        return P['chair'], u, False
    if t < M['fight']:
        u = float(smoothstep(M['try2'] + 0.3, M['try2'] + 4.4, t))
        if t >= M['clatter2']:
            u = float(smoothstep(M['clatter2'] + 0.08, M['clatter2'], t))
        return P['chair'], u, False
    if t < M['heap']:
        prev = P['chair']
        for i, tl in enumerate(LANDS):
            if t < tl - FLIGHT:
                bt = 60 / (150 if t < M['fight2'] else 168)
                snap = 1.0 if ((t - M['fight']) / bt) % 1.0 < 0.5 else 0.25
                return prev, snap, False
            if t < tl:
                x = (t - tl + FLIGHT) / FLIGHT
                return prev + (P['spots'][i] - prev) * x, 0.0, True
            prev = P['spots'][i]
        return prev, 0.0, False
    if t < M['fling'] + 0.15:
        return P['spots'][-1], 0.0, False
    if t < M['fling'] + 1.15:
        x = float(np.clip((t - M['fling'] - 0.15) / 1.0, 0, 1))
        return P['spots'][-1] + (P['side_end'] - P['spots'][-1]) * x ** 1.3, 0.0, True
    return P['side_end'] - 200, 0.0, False


def dog_p(S, t):
    """Up on the porch, out to his spot on Right, a step toward the chair to sit, chasing it, then by the table."""
    P = places(S)
    if t < M['try1']:
        return S.mid + (P['stand'] - S.mid) * float(smoothstep(M['strut'] + 0.5, M['try1'] - 0.5, t))
    if t < M['try2']:
        p = P['stand']
        if t >= HITS[2]:
            p += 18 * float(smoothstep(HITS[2], HITS[2] + 0.5, t))
        return p
    if t < M['fight']:
        p = P['stand'] + 18 * float(smoothstep(M['try2'] + 0.5, M['try2'], t))
        if t >= M['woof']:                                          # he turns to the porch to crow about it
            p -= 30 * float(smoothstep(M['woof'], M['woof'] + 0.3, t))
        return p
    if t < M['fling']:
        return chair(S, max(t - 0.5, M['fight']))[0] - 26
    if t < M['table']:
        return P['spots'][-1] - 26
    if t < M['set']:
        return S.mid + 100 + 30 * np.sin(2 * np.pi * (t - M['table']) / (8 * 60 / 152))
    if t < M['finale']:
        dn = C.downbeats('set')
        i = int(np.clip(np.searchsorted(dn, t + 0.3) - 1, 0, 3))
        return P['seats'][i] + 22
    return S.mid


def draw_chair(S, fr, p, u, lvl=1.0, small=False):
    """A folding lawn chair on the roofline: folded, a short silver stick; open, green-and-white webbing between
    silver ends."""
    half = int(round(1 + (3 if small else 5) * u))
    px = []
    for o in range(-half, half + 1):
        if abs(o) == half:
            px.append((o, ICE, 0.8))
        elif u < 0.3:
            px.append((o, ICE, 0.55))
        else:
            px.append((o, LAWN if o % 2 else WHITE, 0.95 if o % 2 else 0.6))
    return S.sprite(fr, p, px, lvl, 1)


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The tune plays the roofline: each note sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


FIREFLY = hexc("#b8ff20")
DARK = np.zeros(3)


def fireflies(S, t, lv, n=40, seed=5):
    """Fireflies over the evening lawn: n points drifting slowly along the roof, each glowing up and fading out on
    its own few-second cycle, so the yard is never still."""
    rng = np.random.default_rng(seed)
    p0, sp = rng.uniform(0, S.L, n), rng.uniform(-14, 14, n)
    ph, per = rng.uniform(0, 1, n), rng.uniform(2.2, 4.5, n)
    pos = p0 + sp * t + 22 * np.sin(2 * np.pi * t / (1.7 * per) + 6.28 * ph)
    glow = np.clip(np.sin(2 * np.pi * (t / per + ph)), 0, 1) ** 3
    w = np.exp(-((S.d[:, None] - pos[None, :]) / 7.0) ** 2) * glow[None, :]
    return light(FIREFLY, lv * np.clip(w.sum(1), 0, 1.2))


def webbing(S, t, p, w, lv, phase=0.0):
    """The chair's webbing as a big look: green and white bands along the roof either side of p for w units."""
    if w <= 0 or lv <= 0:
        return np.zeros((S.N, 3)), np.zeros(S.N)
    m = S.span(p - w, p + w, soft=10)
    return S.stripes(phase, (LAWN, WHITE), lv=lv, period=22, mask=m), m


def render(G, seed=4):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    tags = ('strut', 'try1', 'try2', 'fight', 'fight2', 'table', 'set', 'finale')
    tunes = {g: C.tunes(g) for g in tags}
    last = {g: v[-1][0] for g, v in tunes.items()}
    downs = {g: C.downbeats(g) for g in tags}
    gbeats = {g: C.beat_times(g) for g in tags}
    bulb = (G.pi % 6 == 0).astype(float)
    bulb_runs = ['Left', 'Right', 'Porch Left', 'Porch Right', 'Side']
    bulb_on = {r: downs['table'][3 + i] for i, r in enumerate(bulb_runs)}
    bulb_on['Porch Front'] = downs['table'][2]
    clatters = [(HITS[3], 1.0), (M['clatter2'], 1.3)] + [(tl, 1.0) for tl in LANDS[:-1]] + [(LANDS[-1], 1.4)]
    yard_lv = [(0, 0.0), (1.4, 0.9), (M['try2'] + 2, 0.9), (M['hold'], 0.55), (M['woof'], 0.55),
               (M['woof'] + 0.2, 0.9), (M['heap'], 0.9), (M['heap'] + 0.3, 0.3), (M['fling'] + 1.2, 0.3),
               (M['table'], 0.8), (M['end'], 0.8)]
    fin_cols = [WHITE, GREEN, WHITE, GOLD]

    for f in range(F):
        t = f * DT
        lv_y = float(keys(t, yard_lv))
        fr = S.backyard(t, lv=lv_y, bulbs=0.0)
        # the party bulbs: dark until he sets the table, then a run at a time
        lit = np.zeros(S.N)
        for r, tb in bulb_on.items():
            if t >= tb:
                lit = np.maximum(lit, S.run[r] * float(smoothstep(tb, tb + 0.2, t)))
                a = t - tb
                if a < 0.6:
                    fr += light(WHITE, 0.8 * np.exp(-a / 0.18) * S.run[r])
        fr += fireflies(S, t, 0.85 * lv_y * (1 - 0.6 * float(smoothstep(M['fight'], M['fight'] + 0.5, t)
                                                         * smoothstep(M['heap'] + 0.3, M['heap'], t))))
        sway = 0.75 + 0.25 * np.sin(2 * np.pi * (0.25 * t - d / 700.0))
        fr += light(WARM, 0.95 * bulb * lit * sway)
        beat = pulse(t, beats, 0.14)
        pdog = dog_p(S, t)
        pc, u, flying = chair(S, t)

        # the count-in: four white washes out from the porch
        for tc in C.beat_times('count'):
            fr += S.wave(t, tc, WHITE, 0.5, speed=700, width=90, decay=0.35)

        # the strut: a white marquee along all he has crossed, a ripple at each step
        if M['strut'] <= t < M['try1'] + 1.0:
            a = t - M['strut']
            fade = float(smoothstep(M['try1'] + 1.0, M['try1'], t))
            if a < 0.7:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.2) * S.run['Porch Front'])
            crossed = S.span(S.at('Porch Front', 0.2), pdog) * fade
            fr = fr * (1 - 0.5 * crossed[:, None]) + S.chase(2 * a / 0.5, cols=(BEAGLE, BEAGLE, None), lv=0.65,
                                                             spacing=2, mask=crossed)
            yard = (S.wings + S.run['Side']) * (1 - crossed) * float(smoothstep(0, 1.0, a)) * fade
            fr = fr * (1 - 0.4 * yard[:, None]) + S.zigzag(a / 0.5, lv=0.45, col=BEAGLE, travel=0.25, mask=yard)
            for tb in [x for x in C.times('bass', 'strut') if x <= t][-2:]:
                fr += S.wave(t, tb, WHITE, 0.55 * fade, origin=dog_p(S, tb), speed=600, width=45, decay=0.45)
            fr += keyboard(S, t, tunes['strut'], WHITE, 0.55 * fade)

        # try one: the webbing spreads with the chair, a flash on each hit; the fourth hit folds it
        if M['try1'] <= t < M['try2']:
            web, m = webbing(S, t, pc, 30 + 230 * u, 0.85 * min(1.0, 2 * u), phase=(t - M['try1']) / 0.5)
            fr = fr * (1 - 0.6 * m[:, None]) + web
            for i, th in enumerate(HITS[:3]):
                a = t - th
                if 0 <= a < 0.8:
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * S.front)
            if HITS[2] <= t < HITS[3]:                             # he goes to sit: the porch holds its breath
                fr += light(GOLD, 0.35 * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * (t - HITS[2]))) * S.blob(pdog, 60))
            echo = (S.run['Left'] + S.run['Side'] + S.run['Porch Left']) * 1.0
            fr = fr * (1 - 0.3 * echo[:, None]) + S.stripes((t - M['try1']) / 0.5, (LAWN, DARK, WHITE, DARK), lv=0.4,
                                                            period=22, mask=echo)
            fr += keyboard(S, t, tunes['try1'], WHITE, 0.5)

        # try two: carefully; the webbing spreads slowly as the house dims; it breathes on each beat; it holds
        if M['try2'] <= t < M['clatter2']:
            a = t - M['try2']
            breath = 1.0 + 0.25 * pulse(t, gbeats['try2'], 0.25) if t < M['hold'] else 0.9 + 0.1 * np.sin(2 * np.pi * 0.8 * a)
            web, m = webbing(S, t, pc, 30 + 300 * u, 0.85 * u * breath, phase=0.0)
            fr = fr * (1 - 0.6 * m[:, None]) + web
            fr += keyboard(S, t, tunes['try2'], LAWN, 0.45)
            if t >= M['woof']:                                     # triumph! gold on the porch and Left
                b = t - M['woof']
                fr += light(GOLD, 0.85 * np.exp(-b / 0.5) * (S.porch + S.run['Left']))
                fr += S.wave(t, M['woof'], WHITE, 0.9, origin=pdog, speed=1000, width=60, decay=0.6)

        # the battle: a green-and-white marquee on the whole house; the chair snaps on every beat where it sits
        if M['fight'] <= t < M['heap'] + 0.3:
            a = t - M['fight']
            two = t >= M['fight2']
            bt = 60 / (168 if two else 150)
            fade = float(smoothstep(M['heap'] + 0.3, M['heap'], t))
            fr = fr * (1 - 0.5 * fade) + S.chase(2 * a / bt, cols=(LAWN, WHITE, None), lv=(0.6 if two else 0.45) * fade,
                                                 spacing=3)
            if not flying:
                web, m = webbing(S, t, pc, 25 + 70 * u, 0.9 * u * fade, phase=a / bt)
                fr = fr * (1 - 0.6 * m[:, None]) + web
            else:                                                 # in the air: a white comet
                fr += light(WHITE, 0.9 * S.blob(pc, 30))
            fr += keyboard(S, t, tunes['fight2' if two else 'fight'], WHITE, 0.55 * fade)
            fr += light(WHITE, 0.4 * pulse(t, gbeats['fight2' if two else 'fight'], 0.08) * S.blob(pdog, 30) * fade)

        # every clatter: sparks both ways, a ring out from the chair, the run it hit flashes, the house shakes
        for i, (tc, big) in enumerate(clatters):
            a = t - tc
            if 0 <= a < 2.0:
                where = chair(S, tc + 0.01)[0]
                fr += S.burst([(tc, big, where)], t, seed=20 + i, n=int(14 * big), reach=0.4 * big,
                              colors=(WHITE, ICE, GOLD))
                fr += S.wave(t, tc, WHITE, 0.8 * big, origin=where, speed=1200, width=60, decay=0.5 * big)
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * S.run_at(where))
                fr *= 1 + 0.4 * np.sin(2 * np.pi * 15 * a) * np.exp(-a / 0.25)

        # the heap: stars over him; the fling: a comet off the back of Side and a clatter far away
        if M['heap'] <= t < M['fling'] + 0.6:
            fr = S.stars(fr, pc + 15, t, 0.9 * float(smoothstep(M['fling'] + 0.6, M['fling'], t)))
        if M['fling'] + 0.15 <= t < M['fling'] + 1.2:
            tail = S.span(pc, P['spots'][-1]) * np.exp(-np.abs(d - pc) / 200) * (0.5 + 0.5 * np.sin(0.5 * d + 40 * t))
            fr += light(WHITE, 0.9 * S.blob(pc, 30)) + light(LAWN, 0.6 * tail)
        a = t - (M['fling'] + 1.15)
        if 0 <= a < 1.0:
            fr += light(WHITE, 0.7 * np.exp(-a / 0.2) * S.blob(20, 80))

        # the table: it unfolds a beat at a time on the porch, the net clicks in, green rolls out on each unfold
        if t >= M['table'] and t < M['button'] + 0.4:
            k = int(np.searchsorted(gbeats['table'], t, side='right'))
            half = int(min(14, 2 * k))
            if half > 0:
                fr = S.table(fr, P['table'], 1.0 + 0.15 * beat, half=half, net=t >= downs['table'][2])
            if t < downs['table'][2] + 0.5:
                for tb in gbeats['table'][:8]:
                    fr += S.wave(t, tb, TABLE, 0.7, origin=P['table'], speed=700, width=50, decay=0.5)
            a = t - downs['table'][2]
            if 0 <= a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S.blob(P['table'], 40))
            if t < M['set']:
                fr += keyboard(S, t, tunes['table'], WHITE, 0.6)
                fr += S.sweep(t, last['table'], 1.6, TABLE, 0.8, frm='centre', width=110, trail=0.6)

        # the chairs: four pop open round the table on the bars, the last one wobbles and stays; webbing on the wings
        if t >= M['set']:
            a = t - M['set']
            dn = downs['set']
            if t < M['finale'] + 0.5:
                fade = float(smoothstep(M['finale'] + 0.5, M['finale'], t))
                fr = fr * (1 - 0.4 * S.wings[:, None] * fade) + S.stripes(a / (60 / 132), (LAWN, WHITE), lv=0.6 * fade,
                                                                           period=22, mask=S.wings)
                fr += keyboard(S, t, tunes['set'], WHITE, 0.55 * fade)
            for i, tb in enumerate(dn):
                b = t - tb
                if b >= 0:
                    uu = float(smoothstep(0, 0.12, b))
                    if i == 3 and b < 1.6:                         # the wobble
                        uu = 0.75 + 0.25 * np.cos(2 * np.pi * 3 * b) * np.exp(-b / 0.5) if b > 0.12 else uu
                    fr = draw_chair(S, fr, P['seats'][i], uu, small=True)
                    if b < 0.6:
                        fr += S.burst([(tb, 0.7, P['seats'][i])], t, seed=40 + i, n=8, reach=0.15,
                                      colors=(LAWN, WHITE))

        # the finale: webbing stripes then zigzags on the whole house, a run on each beat, a sweep, the button
        if t >= M['finale']:
            ph = (t - M['finale']) / (60 / 132)
            bar = min(int(ph // 4), 7)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            if bar < 4:
                look = S.stripes(ph, (LAWN, WHITE), lv=0.75 * fade, period=26)
            else:
                look = S.zigzag(ph, lv=0.85 * fade, col=fin_cols[bar % 4], travel=0.3)
            fr = fr * (1 - 0.6 * fade) + look
            fr += S.run_flash(t, gbeats['finale'], cols=(WHITE, GOLD), lv=0.5 * fade, decay=0.15)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.6 * fade)
            fr += S.sweep(t, downs['finale'][6], 2.4, WHITE, 0.9, frm='right', width=90, trail=0.5)
            a = t - last['finale']
            if 0 <= a < 1.2:
                fr += light(GOLD, 0.6 * np.exp(-a / 0.3) * np.ones(S.N))
            a = t - M['button']
            if a >= 0:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.15) * np.ones(S.N))
                fr += light(LAWN, 0.9 * np.exp(-a / 0.5) * np.ones(S.N))

        # the chair and Snoopy, over everything
        if M['strut'] <= t < M['fling'] + 1.2:
            fr = draw_chair(S, fr, pc, u, 1.0)
        if t >= M['strut']:
            lvl = min(1.0, (t - M['strut']) / 0.15) * (0.95 + 0.15 * beat)
            facing = 1
            if M['woof'] <= t < M['fight'] or (M['fight'] <= t < M['heap'] and chair(S, t)[0] < pdog):
                facing = -1
            if M['heap'] <= t < M['fling'] + 0.15:
                lvl *= 0.45                                       # folded up inside it
            fr = S.beagle(fr, pdog, lvl, facing=facing, t=t)
            if M['finale'] <= t:                                  # on the last chord he sits: a bounce of light
                a = t - M['button']
                if 0 <= a < 1.0:
                    fr += light(WHITE, 0.8 * np.exp(-a / 0.2) * S.blob(pdog, 40))

        out[f] = fr * float(smoothstep(D, D - 1.2, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=0.96)
    parts = {
        ('strut', 'tune'): [('clarinets', 0, 4, 0.8), ('piano', 0, -8, 0.45)],
        ('strut', 'comp'): [('piano', 0, -12, 0.45)],
        ('try1', 'tune'): [('clarinets', 0, 6, 0.8)],
        ('try1', 'hit'): [('piano', 0, 6, 0.8), ('muted horn', 0, -4, 0.45)],
        ('try2', 'tune'): [('pizz', 0, 0, 0.9), ('piano', 12, -30, 0.2)],
        ('fight', 'tune'): [('piano', 0, 10, 0.85), ('xylo', 12, -8, 0.3), ('clarinets', 0, -6, 0.5)],
        ('fight', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -14, 0.3)],
        ('fight2', 'tune'): [('piano', 0, 14, 0.9), ('xylo', 12, -4, 0.35), ('trumpets', 0, -10, 0.35)],
        ('fight2', 'comp'): [('piano', 0, -2, 0.5), ('horns', 0, -10, 0.35)],
        ('table', 'tune'): [('piano', 0, 8, 0.85), ('vibes', 0, -12, 0.25)],
        ('set', 'tune'): [('clarinets', 0, 4, 0.75), ('piano', 0, -6, 0.5)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('clarinets', 0, -10, 0.35)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    B.effects([(0, -2), (M['fight'], 0), (M['table'], -3)])
    pc = lambda t: S.pan(chair(S, t)[0])
    # crickets of a sort: a soft open chord as the backyard comes up
    for m in (60, 64, 67, 71):
        B.play('choir', m, 0.2, 1.3, 46, gain=0.3)
    B.boing(M['strut'], pan=S.pan(S.mid), gain=0.8)
    B.woof(M['strut'] + 0.25, pan=S.pan(S.mid))
    B.steps(M['strut'] + 0.5, M['try1'] - 0.5, beat=0.5, pan=lambda tt: S.pan(dog_p(S, tt)), gain=0.6)
    # try one: a clack as it half opens, a clack as it's up, his steps to sit, the clatter and a fall
    B.hit('claves', HITS[0], 110, pitch=-3, gain=0.5, pan=S.pan(P['chair']), fx=True)
    B.hit('woodblock', HITS[1], 110, gain=0.5, pan=S.pan(P['chair']), fx=True)
    B.steps(HITS[2], HITS[2] + 0.5, beat=0.18, pan=S.pan(P['chair']), gain=0.7)
    B.chair(HITS[3], pan=S.pan(P['chair']), seed=1)
    B.fall(HITS[3] + 0.7, pan=S.pan(P['chair']), gain=0.6)
    # try two: careful ratchet clicks as it unfolds, pats on each beat, a held breath, the woof, the clatter
    for k in range(6):
        B.hit('ratchet', M['try2'] + 0.4 + 0.6 * k, 70, gain=0.25, pan=S.pan(P['chair']), fx=True)
    for tb in C.beat_times('try2')[8:]:
        B.hit('taps', tb, 60, gain=0.2, pan=S.pan(P['chair']))
    B.play('violins trem', 76, M['hold'], 1.4, 50, gain=0.25)
    B.woof(M['woof'], pan=S.pan(P['stand']), big=1.2)
    B.woof(M['woof'] + 0.3, pan=S.pan(P['stand']), big=1.0)
    B.chair(M['clatter2'], pan=S.pan(P['chair']), gain=1.2, seed=2)
    B.hit('crash', M['clatter2'], 100, gain=0.35, pan=S.pan(P['chair']))
    # the battle: the chair snapping on the beats, a slide whistle for each flight, a clatter each landing
    for tb in C.beat_times('fight') + C.beat_times('fight2'):
        if not any(tl - FLIGHT - 0.05 <= tb <= tl + 0.2 for tl in LANDS):
            B.hit('slapstick', tb + 0.01, 80, gain=0.25, pan=pc(tb), fx=True)
    for i, tl in enumerate(LANDS):
        B.slide(tl - FLIGHT, FLIGHT, up=i % 2 == 0, pan=pc(tl - FLIGHT / 2), gain=0.6)
        B.chair(tl, pan=pc(tl + 0.01), gain=1.0 if i < len(LANDS) - 1 else 1.3, seed=3 + i)
    B.hit('crash', LANDS[-1], 115, gain=0.45, pan=pc(LANDS[-1] + 0.01))
    B.thud(LANDS[-1] + 0.05, pan=pc(LANDS[-1] + 0.01), gain=0.6)
    B.steps(M['fight'], M['heap'], beat=60 / 150 / 2, pan=lambda tt: S.pan(dog_p(S, tt)), gain=0.35)
    # stars, then the fling: a whoosh off the back of Side, a far clatter
    for k in range(3):
        B.play('glock', 84 - 3 * k, M['heap'] + 0.3 + 0.18 * k, 0.3, 70, pan=S.pan(P['spots'][-1]), gain=0.35)
    B.boing(M['fling'], pan=S.pan(P['spots'][-1]), gain=0.7)
    B.whoosh(M['fling'] + 0.15, 1.0, up=False, pan=lambda tt: S.pan(chair(S, tt)[0]), gain=0.9)
    B.chair(M['fling'] + 1.15, pan=-0.85, gain=0.35, seed=9)
    # the table: a clack for each unfold, the net's click, a chime for each run of bulbs
    tb_beats = C.beat_times('table')
    for tb in tb_beats[:7]:
        B.hit('woodblock', tb, 90, pitch=-2, gain=0.35, pan=S.pan(P['table']), fx=True)
    B.hit('claves', C.downbeats('table')[2], 115, gain=0.5, pan=S.pan(P['table']), fx=True)
    for i, tb in enumerate(C.downbeats('table')[3:8]):
        B.play('glock', [72, 76, 79, 84, 88][i], tb, 0.6, 76, gain=0.4)
    # the chairs pop open, the last one wobbles (tick-tock) and stays
    for i, tb in enumerate(C.downbeats('set')):
        B.hit('claves', tb, 108, pitch=-2 + i, gain=0.5, pan=S.pan(P['seats'][i]), fx=True)
    tb = C.downbeats('set')[3]
    for k in range(4):
        B.hit('woodblock', tb + 0.2 + 0.17 * k, 70 - 8 * k, pitch=3 * (k % 2), gain=0.3, pan=S.pan(P['seats'][3]))
    # the finale's sweep and the button; he sits
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - M['finale']) / 12)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.boing(M['button'] + 0.1, pan=S.pan(S.mid), gain=0.6, high=0.8)
    B.finish()
