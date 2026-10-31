"""Where's the Turkey?: the tomboy sees the menu and blows up; Charlie Brown is crushed and walks away.

Everyone is at the ping-pong table in the backyard, and the main title swings while the kids' colours march round the
house, eager. Snoopy pops up behind the table in his chef's hat and serves on his jaunty strut, the party bulbs
flipping on every beat: on every other bar he tosses a dish onto the table and a wave of its colour runs over the whole
house. Toast (with a pop), pretzels, popcorn (popping), jelly beans (Woodstock drops them in, a rainbow of
confetti). Then stop-time on Peppermint Patty's theme: on each hit she looks at another dish and a green pulse runs from
her to it; green creeps over her side of the house hit by hit, and on the last two she glares at him. A held breath:
the house drops dark but for her, green and trembling, under a snare roll. Then the outburst, a storm of green: her
theme at double time on blaring brass, a jagged green bolt cracking down a run on every beat with thunder on every bar,
green marquees rushing out from her both ways, sparks bursting, the dishes jumping on the table, a whole-house green
flash at the end of each phrase, faster still for the last four bars and a crash. Silence; the kids gasp. Then the boy's
own wistful theme, slow on a solo piano: he gets up and trudges away from the table along the porch and Left and out at
the back of Side, deep blue rings rolling out from him on every bar, a drizzle over his head, the house draining to blue
behind him; a trombone falls as he goes. Last, the tomboy alone at the table, her green dimmed to a slow pulse to a few
bars of her own theme, played softly, as if she is sorry. Marcie' lenses glint beside her.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, popcorn_times, YELLOW, WHITE, AMBER, GOLD, GREEN, GLASSES, CAP, STRIPE,
                                    BLANKET, BLUE, VIOLET, NIGHT, ICE, WARM, TOAST, POPCORN, PRETZEL, BUTTER, JELLY)

CODE = 'CC10'
TITLE = "Where's the Turkey?"
KIND = 'show'
DESCRIPTION = ('Snoopy serves toast, pretzels, popcorn and jelly beans. Peppermint Patty looks for the turkey and the '
    'pie, then erupts in a storm of green. Charlie Brown walks away, crushed.')
VOICEOVER = 'Toast, pretzels, popcorn and jelly beans, and then Peppermint Patty sees the menu.'

FEAST_COLS = (YELLOW, GREEN, GLASSES, CAP, BLANKET, STRIPE)
DISHES = (('toast', -7, TOAST), ('pretzels', -3, PRETZEL), ('popcorn', 3, POPCORN), ('jellybeans', 7, None))


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the backyard, everyone at the table
    C.mark('eager')
    C.play('title', style='swing', bars=(0, 4), tag='eager')        # the kids are hungry
    C.mark('serve')
    C.play('beagle', style='swing', bpm=112, tag='serve')           # Snoopy serves, dish by dish
    C.mark('look')
    C.play('tomboy', style='stop', bars=(0, 6), tag='look')         # she looks at each dish
    C.mark('breath')
    C.rest(1.4)                                                     # the held breath
    C.mark('blow')
    C.play('tomboy', style='drive', bpm=176, tag='blow')            # the storm of green
    C.mark('blow2')
    C.play('tomboy', style='drive', bars=(4, 8), bpm=196, tag='blow2')
    C.mark('crash')
    C.button('Bb7', bpm=196, beats=2, tag='crash', vel=122)
    C.mark('silence')
    C.rest(2.2)                                                     # silence; the kids gasp
    C.mark('crushed')
    C.play('boy', style='ballad', bars=(0, 8), bpm=84, tag='crushed')           # he walks away
    C.mark('alone')
    C.play('tomboy', style='ballad', bars=(0, 2), bpm=76, tag='alone')          # she is left at the table
    C.rest(3.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks

PLACES = {}


def places(S):
    """The table and the kids round it, where the dishes sit on the table, and where he walks out (past Side's end)."""
    if not PLACES:
        m = S.mid
        PLACES.update(table=m, boy=m - 65, cap=m - 125, tom=m + 70, gl=m + 125, blanket=S.at('Porch Left', 0.82),
                      exit=-45.0)
        for name, o, _ in DISHES:
            PLACES[name] = m + o * 4.85
    return PLACES


def serve_times():
    """When each dish lands: the downbeat of every other bar of the strut."""
    return C.downbeats('serve')[1::2]


def pops():
    """The corn popping after the popcorn lands: a storm of pops thinning out; lights and sound share it."""
    tl = serve_times()[2]
    return popcorn_times(tl + 0.05, tl + 3.4, lambda u: 3 + 26 * (1 - u) ** 1.5, seed=6)


def boy_p(S, t):
    """He sits at the table until the silence, then trudges off along the porch, Left and Side, out past its end."""
    P = places(S)
    t0, t1 = M['crushed'] + 1.5, M['alone'] - 1.0
    if t < t0:
        return P['boy']
    u = min(1.0, (t - t0) / (t1 - t0))
    return P['boy'] + (P['exit'] - P['boy']) * u


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
    beats = np.array(C.beat_times())
    landed = serve_times()
    serve_beats = C.beat_times('serve')
    look_hits = C.times('hit', 'look')
    blow_beats = C.beat_times('blow') + C.beat_times('blow2')
    blow_downs = C.downbeats('blow') + C.downbeats('blow2')
    phrase_ends = [C.downbeats('blow')[3], C.downbeats('blow')[7]]
    crushed_downs = C.downbeats('crushed')
    crushed_bass = C.times('bass', 'crushed')
    alone_tune = [n[0] for n in C.tunes('alone')]
    tunes = {g: C.tunes(g) for g in ('eager', 'serve', 'look', 'blow', 'blow2', 'crushed', 'alone')}
    exit_t = M['alone'] - 1.0
    POPS = pops()
    rng = np.random.default_rng(seed)
    drip_ph = rng.uniform(0, 1, S.N)
    lv_key = [(0, 0.0), (1.6, 1.0), (M['look'], 1.0), (M['look'] + 4, 0.8), (M['breath'], 0.8), (M['breath'] + 0.6, 0.15),
              (M['blow'], 0.4), (M['silence'], 0.4), (M['silence'] + 0.3, 0.25), (M['crushed'], 0.3),
              (M['end'], 0.3)]

    for f in range(F):
        t = f * DT
        fr = S.backyard(t, lv=float(keys(t, lv_key)))
        beat = pulse(t, beats, 0.14)
        bp = boy_p(S, t)

        # eager: the kids' colours march round the house under the title
        if M['eager'] - 0.4 <= t < M['serve'] + 0.5:
            fade = float(smoothstep(M['eager'] - 0.4, M['eager'], t) * smoothstep(M['serve'] + 0.5, M['serve'], t))
            nb = (t - M['eager']) / (60 / 152)
            fr = fr * (1 - 0.5 * fade) + S.stripes(nb, FEAST_COLS, lv=0.6 * fade, period=46)
            fr += S.run_flash(t, C.beat_times('eager'), cols=(WHITE,), lv=0.4 * fade, decay=0.12)
            fr += keyboard(S, t, tunes['eager'], WHITE, 0.6 * fade)

        # the serve: party bulbs flip on every beat; each dish lands with a wave of its colour over the whole house
        if M['serve'] <= t < M['look'] + 0.5:
            fade = float(smoothstep(M['look'] + 0.5, M['look'], t))
            nb = int(np.searchsorted(serve_beats, t))
            fr += S.chase(3 * nb, (WARM, BUTTER, None), 0.6 * fade, spacing=2, mask=S.wings | S.run['Side'])
            fr += S.run_flash(t, serve_beats, cols=(WHITE, WARM), runs=('Porch Left', 'Porch Right'), lv=0.5 * fade,
                              decay=0.18)
            fr += keyboard(S, t, tunes['serve'], WHITE, 0.55 * fade)
            for i, tl in enumerate(landed):
                name, o, col = DISHES[i]
                a = t - (tl - 0.45)
                if 0 <= a < 0.45:                                     # tossed up from Snoopy onto the table
                    q = P['table'] + (P[name] - P['table']) * a / 0.45
                    fr += light(WHITE, 0.9 * np.exp(-((d - q) / 8) ** 2))
                a = t - tl
                if a >= 0:
                    if col is None:                                    # jelly beans: a rainbow of confetti
                        fr += S.confetti([(tl, 1.0, P[name])], t, colors=JELLY, n=36, reach=1.6, seed=9)
                    else:
                        fr += S.wave(t, tl, col, 1.0, origin=P[name], speed=600, width=150, decay=1.8)
                        fr += S.wave(t, tl + 0.06, WHITE, 0.6, origin=P[name], speed=600, width=35, decay=0.8)
                    if name == 'popcorn' and a < 3:
                        fr += S.popcorn(POPS, t, lv=1.0, seed=4)

        # the look: stop-time, a green pulse from her to each dish; green creeps over her side of the house
        if M['look'] <= t < M['blow']:
            n_hit = int(np.searchsorted(look_hits, t, side='right'))
            creep = min(1.0, n_hit / 6.0)
            tremble = 0.8 + 0.2 * np.sin(2 * np.pi * (4 + 6 * creep) * t)
            side = (d > P['tom'] - 10).astype(float)
            fr += light(GREEN, 0.75 * creep * tremble * side * smoothstep(L + 50, P['tom'], d) ** 0.3)
            for i, th in enumerate(look_hits):
                a = t - th
                if 0 <= a < 1.2:
                    target = P[DISHES[i][0]] if i < 4 else P['boy']
                    q = P['tom'] + (target - P['tom']) * min(1.0, a / 0.35)
                    fr += light(GREEN, 1.0 * np.exp(-a / 0.5) * np.exp(-((d - q) / 12) ** 2))
                    if a > 0.35:
                        fr += light(WHITE if i < 4 else GREEN, 0.9 * np.exp(-(a - 0.35) / 0.2) *
                                    S.blob(target, 14 if i < 4 else 40))
                    fr += light(GREEN, 0.5 * np.exp(-a / 0.2) * S.run['Right'])
            fr += keyboard(S, t, tunes['look'], GREEN, 0.5, width=30)

        # the held breath: dark but for her, green and trembling
        if M['breath'] <= t < M['blow']:
            u = (t - M['breath']) / (M['blow'] - M['breath'])
            fr *= 1 - 0.6 * u
            fr += light(GREEN, (0.4 + 0.6 * u) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * S.blob(P['tom'], 30 + 60 * u))

        # the storm of green
        if M['blow'] <= t < M['silence']:
            p = P['tom']
            n_b = (t - M['blow']) / (60 / 176)
            fade = float(smoothstep(M['silence'], M['crash'] + 0.15, t))
            cols, sp = ((GREEN, GREEN, None, None), 5) if t < M['blow2'] else ((GREEN, WHITE, GREEN, None), 8)
            away = (S.chase(sp * n_b, cols, 0.75, spacing=2, mask=(d < p).astype(float)) +
                    S.chase(-sp * n_b, cols, 0.75, spacing=2, mask=(d > p).astype(float)))
            fr = fr * 0.5 + away * fade * (0.6 + 0.5 * min(1.0, pulse(t, blow_beats, 0.12)))
            for j, tb in enumerate(blow_beats):                       # a jagged green bolt down a run, every beat
                a = t - tb
                if 0 <= a < 0.5:
                    brng = np.random.default_rng(300 + j)
                    run = S.RUNS[(j * 2 + 1) % 6]
                    jag = np.sin(d * brng.uniform(0.06, 0.14) + brng.uniform(0, 6)) > 0.1
                    fr += light(GREEN, np.exp(-a / 0.14) * S.run[run] * (0.45 + 0.55 * jag))
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.05) * S.run[run] * jag)
            for tb in blow_downs:
                fr += S.wave(t, tb, GREEN, 0.9, origin=p, speed=1300, width=60, decay=0.5)
            fr += S.burst([(tb, 1.0, p) for tb in blow_downs], t, seed=12, n=12, reach=0.6, colors=(GREEN, WHITE),
                          life=1.0)
            for tb in phrase_ends:                                    # the end of each phrase: the whole house green
                a = t - tb
                if 0 <= a < 0.6:
                    fr += light(GREEN, np.exp(-a / 0.12) * np.ones(S.N))
            a = t - M['crash']
            if a >= 0:
                fr += light(GREEN, np.exp(-a / 0.25) * np.ones(S.N))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.06) * np.ones(S.N))
            fr += keyboard(S, t, tunes['blow'] + tunes['blow2'], WHITE, 0.6, width=20)
            fr *= fade + (1 - fade) * 0.3

        # crushed: he trudges off; deep blue rings out from him every bar, drizzle over him, the house drains blue
        if M['crushed'] <= t < M['end']:
            a0 = t - M['crushed']
            sad = float(smoothstep(0, 2.5, a0))
            fr += light(NIGHT, 0.35 * sad * np.ones(S.N))
            for i, tb in enumerate(crushed_downs):
                col = BLUE if i % 2 == 0 else VIOLET
                fr += S.wave(t, tb, col, 0.9, origin=boy_p(S, tb), speed=330, width=150, decay=2.6)
            for tb in [x for x in crushed_bass if x <= t][-2:]:
                fr += light(ICE, 0.6 * np.exp(-(t - tb) / 0.3) * S.blob(boy_p(S, tb), 22))
            if t < exit_t + 1:
                rain = np.exp(-((((drip_ph + 1.7 * t) % 1.0) - 0.5) / 0.05) ** 2)
                fr += light(ICE, 0.7 * rain * S.blob(bp, 55) * float(smoothstep(exit_t + 1, exit_t, t)))
                fr += light(BLUE, 0.4 * S.blob(bp, 90) * float(smoothstep(exit_t + 1, exit_t, t)))
            fr += keyboard(S, t, tunes['crushed'], ICE, 0.45, decay=0.5, width=30)

        # alone: the tomboy at the table, her green a slow pulse to her theme, played softly
        if t >= M['alone'] - 1.0:
            u = float(smoothstep(M['alone'] - 1.0, M['alone'], t))
            fr += light(GREEN, u * (0.25 + 0.6 * pulse(t, alone_tune, 0.5)) * S.blob(P['tom'], 60))
            fr += S.wave(t, M['alone'], GREEN, 0.5, origin=P['tom'], speed=300, width=120, decay=2.5)

        # the table and the dishes on it
        shake = 0.0
        if M['blow'] <= t < M['crash'] + 0.5:
            shake = 3.0 * (pulse(t, blow_beats, 0.08) > 0.3)
        fr = S.table(fr, P['table'], min(1.0, t / 1.5), half=10)
        for i, tl in enumerate(landed):
            if t >= tl:
                name = DISHES[i][0]
                fr = S.dish(fr, P[name] + shake * (1 if (i + int(t * 20)) % 2 else -1), name, 1.0, t=t)

        # Snoopy serving, the bird bringing the jelly beans
        if M['serve'] - 0.3 <= t < M['look'] + 0.8:
            vis = float(smoothstep(M['serve'] - 0.3, M['serve'] + 0.2, t) * smoothstep(M['look'] + 0.8, M['look'], t))
            hop = 0.15 * abs(np.sin(np.pi * (t - M['serve']) / (60 / 112)))
            fr = S.beagle(fr, P['table'] + 6, vis * (1 + hop), facing=1, t=t, chef=True)
        if len(landed) > 3 and landed[3] - 2.5 <= t < landed[3] + 1.5:
            a = t - (landed[3] - 2.5)
            q = L + 30 - (L + 30 - P['jellybeans']) * float(smoothstep(0, 2.5, a)) + 10 * np.sin(6 * a)
            fr = S.bird(fr, q, float(smoothstep(landed[3] + 1.5, landed[3] + 0.8, t)), t=t, facing=-1)

        # the kids
        kids = min(1.0, t / 1.5)
        cower = 0.7 if M['blow'] <= t < M['crushed'] else 1.0
        fr = S.cap_boy(fr, P['cap'], kids * cower, facing=1, t=t)
        fr = S.glasses(fr, P['gl'], kids * cower, facing=-1, t=t,
                       glint=0.8 * pulse(t, alone_tune, 0.4) if t >= M['alone'] else 0.0)
        fr = S.blanket_boy(fr, P['blanket'], kids * cower, facing=1, t=t)
        tom_lvl = kids * (1.0 + 0.3 * beat if M['look'] <= t < M['silence'] else 0.85)
        fr = S.tomboy(fr, P['tom'] + (4 * np.sin(2 * np.pi * 9 * t) if M['blow'] <= t < M['crash'] else 0),
                      tom_lvl, facing=-1, t=t)
        if t < exit_t + 1.0:
            if t < M['crushed'] + 1.5:
                lvl = kids * (0.6 if M['blow'] <= t else 1.0 + 0.2 * beat)
                fr = S.boy(fr, bp, lvl, facing=1, t=t, glow=0.3 if t < M['blow'] else 0.1)
            else:
                fr = S.boy(fr, bp, 0.75, facing=-1, t=t, run=0.4, glow=0.15)

        out[f] = fr * float(smoothstep(D, D - 2.0, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    parts = {
        ('eager', 'tune'): [('piano', 0, 8, 0.85)],
        ('serve', 'tune'): [('piano', 0, 6, 0.85), ('marimba', 0, -12, 0.3)],
        ('serve', 'comp'): [('piano', 0, -8, 0.45)],
        ('look', 'tune'): [('muted horn', 0, 4, 0.8), ('piano', 0, -10, 0.4)],
        ('look', 'hit'): [('piano', 0, 4, 0.75), ('horns', 0, -6, 0.4)],
        ('blow', 'tune'): [('trombones', 0, 10, 0.6), ('trumpets', 0, 4, 0.45), ('piano', 0, 10, 0.6)],
        ('blow', 'comp'): [('piano', 0, 0, 0.5), ('horns', 0, -8, 0.35)],
        ('blow2', 'tune'): [('trombones', 0, 16, 0.65), ('trumpets', 0, 10, 0.5), ('horns', 0, 6, 0.4),
                            ('piano', 0, 14, 0.6)],
        ('blow2', 'comp'): [('piano', 0, 4, 0.5), ('horns', 0, -4, 0.4)],
        ('crash', 'hit'): [('piano', 0, 0, 0.8), ('trombones', 0, 0, 0.5), ('trumpets', 0, 0, 0.4),
                           ('horns', 0, 0, 0.4)],
        ('crushed', 'tune'): [('piano', 0, -4, 0.9)],
        ('crushed', 'comp'): [('piano', 0, -16, 0.4), ('choir', 0, -26, 0.3)],
        ('alone', 'tune'): [('piano', 0, -14, 0.8)],
        ('alone', 'comp'): [('piano', 0, -22, 0.35)],
    }
    B.perform(C.events, parts)
    for m in (62, 66, 69, 73):                                       # evening at the table
        B.play('choir', m, 0.2, 2.0, 48, gain=0.3)
    B.kids(M['eager'] + 0.3, M['serve'] - 0.3, 'chatter', level=0.45, pan=S.pan(P['table']), voices=4, seed=3)
    # Snoopy pops up, woofs, and serves: a pop for the toast, a clink for the pretzels, popping corn, beans
    B.boing(M['serve'] - 0.2, pan=S.pan(P['table']), gain=0.8)
    B.woof(M['serve'] + 0.3, pan=S.pan(P['table']))
    landed = serve_times()
    for i, tl in enumerate(landed):
        name = DISHES[i][0]
        pn = S.pan(P[name])
        B.whoosh(tl - 0.45, 0.4, up=True, pan=pn, gain=0.35)
        if name == 'toast':
            B.toast_pop(tl - 0.5, pan=pn, gain=0.9, fly=False)
            B.clink(tl, pan=pn, gain=0.5)
        elif name == 'pretzels':
            B.clink(tl, pan=pn, gain=0.6)
            B.hit('wood', tl + 0.03, 96, gain=0.4, pan=pn)
        elif name == 'popcorn':
            B.popcorn(pops(), pan=0.0, gain=0.7, spread=0.8)
        else:
            B.chirp(tl - 2.0, n=5, pan=0.7, gain=0.8)
            B.chirp(tl - 0.6, n=3, pan=pn, gain=0.8, seed=2)
            for k, m in enumerate((72, 76, 79, 84, 88)):
                B.play('glock', m, tl + 0.07 * k, 0.4, 76, pan=pn, gain=0.3)
            B.hit('bell tree', tl, 84, gain=0.3, pan=pn)
    # the look: a questioning slide whistle on each dish, then a glare
    for i, th in enumerate(C.times('hit', 'look')):
        if i < 4:
            B.slide(th + 0.3, 0.35, up=True, pan=S.pan(P[DISHES[i][0]]), gain=0.35, lo=600, hi=1000)
    # the held breath: a roll, a swelling cymbal, tremolo strings
    B.roll(M['breath'], M['blow'], pan=S.pan(P['tom']), gain=1.0)
    B.hit('cymbal swell', M['breath'] - 0.3, 100, gain=0.45)
    B.play('violins trem', 70, M['breath'], M['blow'] - M['breath'], 74, gain=0.35)
    B.play('cellos trem', 46, M['breath'], M['blow'] - M['breath'], 74, gain=0.35)
    # the storm of green: thunder and timpani on every bar, crashes at the ends of the phrases
    downs = C.downbeats('blow') + C.downbeats('blow2')
    for i, tb in enumerate(downs):
        B.hit('timpani', tb, 112, pitch=-2 * (i % 2), gain=0.45, pan=S.pan(P['tom']))
        if i % 2 == 0:
            B.thunder(tb, near=0.7, pan=0.6 * np.sin(i * 1.7), gain=0.6, seed=i)
    for tb in (C.downbeats('blow')[3], C.downbeats('blow')[7]):
        B.hit('crash', tb, 118, gain=0.45, pan=S.pan(P['tom']))
    B.hit('cymbal swell', M['crash'] - 1.2, 110, gain=0.4)
    B.hit('crash', M['crash'], 124, gain=0.6)
    B.hit('bass drum', M['crash'], 124, gain=0.5)
    B.thunder(M['crash'], near=1.0, gain=0.8, seed=21)
    B.effects([(0, -3), (M['blow'], 0), (M['silence'], -2)])
    # silence: the kids gasp
    B.kids(M['silence'] + 0.3, M['silence'] + 1.2, 'gasp', level=0.6, pan=S.pan(P['table']), voices=4, seed=8)
    # he walks away: soft footsteps going off left, a trombone falling as he goes
    t0 = M['crushed'] + 1.5
    B.steps(t0, M['alone'] - 1.0, beat=60 / 84 * 2, pan=lambda tt: S.pan(boy_p(S, tt)), gain=0.4, v=60)
    B.fall(M['alone'] - 2.4, pan=-0.8, gain=0.55)
    B.kids(M['alone'] - 3.6, M['alone'] - 1.8, 'aww', level=0.35, pan=S.pan(P['table']), voices=4, seed=5)
    B.finish()
