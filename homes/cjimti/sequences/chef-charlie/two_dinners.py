"""Two Dinners: Linus says host them early, then go to Grandma's; Snoopy volunteers as chef.

Charlie Brown frets on the porch beside the three places the phone call left him, each of them blinking at
him from the wings on every bar. Linus strolls in from the free end of Right to his gentle jazz
waltz, his blue blanket rippling along every run he has crossed and a soft swell breathing out of him on each bar.
Then the idea, told across the house: Left lights up as an early dinner (a green ping-pong table, the three guests'
colours), Right as Grandma's (a warm amber house with lit windows), first one then the other on alternate bars with a
white dash running from one to the other, until both glow together. Relief: the main title and the boy's zigzag take
the house run by run. Then the snag: who will cook? The zigzag drains back into him and a trombone falls. Pop: the
beagle springs up on the porch and struts to his theme, a white-and-black marquee on the porch and his zigzag on the
wings, a woof running out each time; on bar 5 the chef's toque goes on with a burst of white, and his strut takes the
whole house. Woodstock flutters in from the end of Right, twittering sparks along the roof, and lands on
the toque; they duet in a yellow-and-white marquee. Into the kitchen: the trio doubles up, the checked tiles march on
the wings, the stove roars over the porch while Snoopy stirs, a run flashes on every bar and chevrons rush in from
both ends. The feast theme on the whole house in zigzags, a sweep from the end of Right, the button.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks.
The positions of the boys, Snoopy and the bird are functions both of them share."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, ORANGE, RED, GOLD, GREEN,
                                    GLASSES, CAP, BLANKET, BIRD, BEAGLE, WARM, TABLE, ICE, LEAVES)

CODE = 'CC03'
TITLE = 'Two Dinners'
KIND = 'show'
DESCRIPTION = ("Linus has the answer: serve an early dinner, then go on to Grandma's. But who will cook? Snoopy puts on "
    "his chef's hat, and Woodstock signs on.")
VOICEOVER = 'Two dinners in one day, and the only cook is Snoopy.'


def compose():
    C = Chart()
    C.rest(1.5)                                                     # the yard comes up
    C.mark('worry')
    C.play('boy', style='two', bars=(0, 4), bpm=104, tag='worry')   # three places set, and no dinner
    C.mark('blanket')
    C.play('blanket', style='waltz', bars=(0, 8), tag='blanket')    # he strolls in from the end of Right
    C.mark('idea')
    C.play('blanket', style='waltz', bars=(8, 16), tag='idea')      # an early dinner here, Grandma's there
    C.mark('relief')
    C.play('title', style='swing', bars=(0, 4), tag='relief')
    C.mark('snag')
    C.rest(1.4)                                                     # but who will cook?
    C.mark('beagle')
    C.play('beagle', style='swing', bars=(0, 4), tag='beagle')      # pop: Snoopy struts
    C.mark('chef')
    C.play('beagle', style='swing', bars=(4, 8), tag='chef')        # the toque goes on
    C.mark('bird')
    C.play('bird', style='swing', tag='bird')                       # the bird flutters in
    C.mark('duet')
    C.play('bird', style='swing', tag='duet')
    C.mark('kitchen')
    C.play('beagle', style='drive', bpm=150, tag='kitchen')         # into the kitchen
    C.mark('finale')
    C.play('feast', style='swing', tag='finale')
    C.mark('button')
    C.button('D6', bpm=184, beats=2)
    C.rest(2.0)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks

PLACES = {}


def places(S):
    if not PLACES:
        PLACES.update(boy=S.at('Porch Front', 0.3), blanket=S.at('Porch Front', 0.47), table=S.at('Porch Front', 0.78),
                      aside=S.at('Porch Right', 0.55), dog=S.at('Porch Front', 0.62), enter=S.L + 50,
                      early=(S.at('Left', 0.12), S.at('Left', 0.88)), gran=(S.at('Right', 0.14), S.at('Right', 0.86)))
    return PLACES


def blanket_p(S, t):
    """In from the end of Right over the first eight bars of his waltz, then aside onto Porch Right for Snoopy."""
    P = places(S)
    if t < M['blanket']:
        return P['enter']
    if t < M['snag']:
        u = float(np.clip((t - M['blanket']) / (M['idea'] - M['blanket'] - 0.6), 0, 1))
        return P['enter'] + (P['blanket'] - P['enter']) * (1 - (1 - u) ** 1.6)
    return P['blanket'] + (P['aside'] - P['blanket']) * float(smoothstep(M['snag'], M['beagle'] + 1.5, t))


def dog_p(S, t):
    """Snoopy: struts back and forth on the porch (a turn every bar), still in the duet, stirring in the kitchen."""
    P = places(S)
    if t < M['bird']:
        k = (t - M['beagle']) / (4 * 60 / 120)
        return P['dog'] + 40 * np.sin(np.pi * k)
    if t < M['kitchen']:
        return P['dog']
    if t < M['finale']:
        return P['dog'] + 14 * np.sin(2 * np.pi * (t - M['kitchen']) / (60 / 150))
    return P['dog']


def dog_facing(t):
    if t < M['bird']:
        k = (t - M['beagle']) / (4 * 60 / 120)
        return 1 if np.cos(np.pi * k) >= 0 else -1
    return 1


def bird_p(S, t):
    """Fluttering in from the end of Right on a wavy line to the front of the toque, hopping there after."""
    P = places(S)
    perch = dog_p(S, t) + dog_facing(t) * 36
    if t < M['duet']:
        u = float(np.clip((t - M['bird']) / (M['duet'] - M['bird'] - 0.4), 0, 1))
        e = 1 - (1 - u) ** 2
        return P['enter'] - 20 + (perch - P['enter'] + 20) * e + 40 * np.sin(2 * np.pi * 1.5 * (t - M['bird'])) * (1 - e)
    return perch


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The tune plays the roofline: each note sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def render(G, seed=3):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    tags = ('worry', 'blanket', 'idea', 'relief', 'beagle', 'chef', 'bird', 'duet', 'kitchen', 'finale')
    tunes = {g: C.tunes(g) for g in tags}
    notes = {g: np.array([n[0] for n in v]) for g, v in tunes.items()}
    last = {g: v[-1][0] for g, v in tunes.items()}
    downs = {g: C.downbeats(g) for g in tags}
    gbeats = {g: C.beat_times(g) for g in tags}
    early = S.span(*P['early'], soft=12)
    gran = S.span(*P['gran'], soft=12)
    reveal = ['Porch Front', 'Left', 'Right', 'Porch Left']
    fin_cols = [WHITE, BIRD, ORANGE, WHITE, YELLOW, GOLD, BIRD, WHITE]
    yard_lv = [(0, 0.0), (1.5, 0.75), (M['idea'], 0.7), (M['idea'] + 1, 0.45), (M['snag'], 0.45),
               (M['snag'] + 0.3, 0.12), (M['beagle'], 0.12), (M['beagle'] + 0.3, 0.6), (M['kitchen'], 0.6),
               (M['kitchen'] + 0.4, 0.0), (M['end'], 0.0)]
    kit_lv = [(0, 0.0), (M['kitchen'], 0.0), (M['kitchen'] + 0.4, 0.8), (M['finale'], 0.8), (M['finale'] + 1, 0.35),
              (M['end'], 0.35)]
    guests = ((GREEN, 0.25), (GLASSES, 0.5), (CAP, 0.75))

    for f in range(F):
        t = f * DT
        fr = S.yard(t, lv=float(keys(t, yard_lv)), leaves=1.0, sun=0.7)
        kl = float(keys(t, kit_lv))
        if kl > 0:
            fr += S.kitchen(t, lv=kl)
        beat = pulse(t, beats, 0.14)
        p = P['boy']
        pb = blanket_p(S, t)

        # he frets: the three places blink at him from the wings on every bar, his zigzag uneasy on the porch
        if M['worry'] <= t < M['blanket'] + 1.0:
            fade = float(smoothstep(M['blanket'] + 1.0, M['blanket'], t))
            ph = (t - M['worry']) / (60 / 104)
            fr = fr * (1 - 0.5 * S.porch[:, None] * fade) + S.zigzag(ph, lv=0.6 * fade, mask=S.porch)
            fr += S.run_flash(t, gbeats['worry'][::2], cols=(GREEN, GLASSES, CAP), runs=('Left', 'Right', 'Side'),
                              lv=0.85 * fade, decay=0.6)
            fr += keyboard(S, t, tunes['worry'], GOLD, 0.55 * fade, width=32)
        if t < M['idea'] + 1.0:
            fade = float(smoothstep(M['idea'] + 1.0, M['idea'], t)) * min(1.0, t / 1.5)
            fr = S.table(fr, P['table'], fade * (0.85 + 0.25 * beat), half=6, net=False,
                         food=[(-4, GREEN), (0, GLASSES), (4, CAP)])

        # Linus strolls in: his blanket ripples blue along all he has crossed, a swell each bar
        if M['blanket'] <= t < M['relief']:
            a = t - M['blanket']
            fade = float(smoothstep(M['relief'], M['idea'] + 1.5, t))
            crossed = S.span(pb + 20, L + 30) * fade
            rip = 0.4 + 0.35 * np.sin(2 * np.pi * (d / 130.0 - 0.7 * a))
            fr = fr * (1 - 0.5 * crossed[:, None]) + light(BLANKET, rip * crossed)
            fr += light(WHITE, 0.25 * np.clip(np.sin(2 * np.pi * (d / 130.0 - 0.7 * a)) - 0.6, 0, 1) * crossed)
            for tb in downs['blanket']:
                fr += S.wave(t, tb, ICE, 0.55, origin=pb, speed=380, width=110, decay=1.2)
            fr += keyboard(S, t, tunes['blanket'], ICE, 0.55, width=30)
            mine = S.span(S.at('Porch Left', 0.5), p + 40)
            fr = fr * (1 - 0.4 * mine[:, None]) + S.zigzag(a / (60 / 132), lv=0.4, mask=mine)

        # the idea: an early dinner on Left, Grandma's on Right, alternate bars, a dash from one to the other
        if M['idea'] <= t < M['snag']:
            a = t - M['idea']
            fade = float(smoothstep(M['snag'], M['relief'] + 0.5, t))
            dn = downs['idea']
            bar = int(np.clip(np.searchsorted(dn, t, side='right') - 1, 0, 7))
            bt = dn[1] - dn[0]
            lv_e = lv_g = 0.25
            if bar < 6:
                x = t - dn[bar]
                s = 0.35 + 0.65 * np.exp(-x / 1.0)
                if bar % 2 == 0:
                    lv_e = max(lv_e, s)
                else:
                    lv_g = max(lv_g, s)
                if bar % 2 == 0 and x < bt:                        # first this, then that: a dash from Left to Right
                    q = P['early'][1] + (P['gran'][0] - P['early'][1]) * x / bt
                    fr += light(WHITE, 0.85 * np.exp(-((d - q) / 30) ** 2))
            else:
                lv_e = lv_g = 0.6 + 0.35 * float(smoothstep(dn[6], dn[7], t))
            lv_e, lv_g = lv_e * fade, lv_g * fade
            for pool, lvp, col in ((early, lv_e, TABLE), (gran, lv_g, WARM)):
                fr = fr * (1 - 0.6 * pool[:, None] * min(1.0, 2 * lvp)) + light(col, lvp * pool)
            for col, u in guests:
                q = P['early'][0] + u * (P['early'][1] - P['early'][0])
                fr += light(col, 1.1 * lv_e * np.exp(-((d - q) / 9) ** 2))
            for u in (0.3, 0.5, 0.7):                              # Grandma's lit windows
                q = P['gran'][0] + u * (P['gran'][1] - P['gran'][0])
                fr += light(WHITE, 0.9 * lv_g * np.exp(-((d - q) / 7) ** 2))
            fr += light(RED, 0.6 * lv_g * np.exp(-((d - P['gran'][0]) / 10) ** 2))
            fr += keyboard(S, t, tunes['idea'], ICE, 0.5, width=30)
            fr += S.sweep(t, last['idea'], 1.4, YELLOW, 0.8, frm='centre', width=110, trail=0.5)

        # relief: the main title, his zigzag taking the house a run at a time
        if M['relief'] <= t < M['snag'] + 1.4:
            a = t - M['relief']
            dn = downs['relief']
            shown = np.zeros(S.N)
            for i, r in enumerate(reveal):
                b = t - dn[i]
                if b >= 0:
                    m = S.run[r] + (S.run['Porch Right'] if r == 'Porch Left' else 0)
                    shown = np.maximum(shown, m * float(smoothstep(0, 0.15, b)))
                    if b < 0.6:
                        fr += light(WHITE, 0.8 * np.exp(-b / 0.18) * m)
            # the snag: everything drains back into him
            if t >= M['snag']:
                u = float(smoothstep(M['snag'], M['snag'] + 1.0, t))
                shown = shown * S.span(p - (1 - u) * 1500 - 30, p + (1 - u) * 1500 + 30)
            zig = S.zigzag(a / (60 / 152), lv=0.85, mask=shown)
            fr = fr * (1 - 0.65 * shown[:, None]) + zig
            fr += keyboard(S, t, tunes['relief'], WHITE, 0.7)

        # Snoopy pops up and struts: a white marquee on the porch, his zigzag on the wings, a woof every other bar
        pd_ = dog_p(S, t)
        if M['beagle'] <= t < M['bird'] + 1.0:
            a = t - M['beagle']
            fade = float(smoothstep(M['bird'] + 1.0, M['bird'], t))
            if a < 0.7:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.2) * S.run['Porch Front'])
            ph = a / 0.5
            if t < M['chef']:
                fr = fr * (1 - 0.5 * S.porch[:, None]) + S.chase(2 * ph, cols=(BEAGLE, BEAGLE, None), lv=0.6,
                                                                 spacing=2, mask=S.porch)
                fr = fr * (1 - 0.4 * S.wings[:, None]) + S.zigzag(ph, lv=0.5, col=BEAGLE, travel=0.25, mask=S.wings)
                for tb in downs['beagle'][::2]:
                    fr += S.wave(t, tb + 0.1, WHITE, 0.8, origin=pd_, speed=900, width=50, decay=0.6)
                fr += keyboard(S, t, tunes['beagle'], WHITE, 0.55)
            else:                                                 # the toque: a burst, and the whole house struts
                b = t - M['chef']
                fr += S.burst([(M['chef'], 1.0, pd_)], t, seed=7, n=18, reach=0.6, colors=(WHITE, BEAGLE, GOLD))
                fr += light(WHITE, 0.9 * np.exp(-b / 0.12) * S.blob(pd_, 80))
                fr = fr * (1 - 0.6 * fade) + S.zigzag(ph, lv=0.8 * fade, col=BEAGLE, travel=0.5)
                fr += S.run_flash(t, gbeats['chef'], cols=(WHITE, GOLD), lv=0.5 * fade, decay=0.15)
                fr += keyboard(S, t, tunes['chef'], GOLD, 0.7 * fade)
                fr += S.wave(t, last['chef'], WHITE, 0.9, origin=pd_, speed=1100, width=70, decay=0.7)

        # the bird: in from the end of Right on a wavy line, twittering sparks along the roof; then the duet
        pbird = bird_p(S, t)
        if M['bird'] <= t < M['kitchen'] + 0.5:
            a = t - M['bird']
            fade = float(smoothstep(M['kitchen'] + 0.5, M['kitchen'], t))
            if t < M['duet']:
                trail = S.span(pbird, min(pbird + 160, L + 40)) * np.exp(-np.maximum(d - pbird, 0) / 70)
                fr += light(BIRD, 0.7 * trail)
                fr = fr * (1 - 0.3 * S.wings[:, None]) + S.zigzag(a / 0.5, lv=0.4, col=BEAGLE, travel=0.5,
                                                                  mask=S.porch)
                fr += S.burst([(t0, 0.8, S.note_at(m)) for t0, _, m in tunes['bird'] if t - 0.8 < t0 <= t], t,
                              seed=11, n=7, reach=0.2, colors=(BIRD, WHITE), life=0.8)
                flit = (S.wings + S.run['Side']) * float(smoothstep(0, 0.5, a))
                fr = fr * (1 - 0.3 * flit[:, None]) + S.chase(-a * 24, cols=(BIRD, None, None), lv=0.55, spacing=2,
                                                              mask=flit)
                fr += keyboard(S, t, tunes['bird'], BIRD, 0.75, decay=0.15, width=18)
            else:
                k = int(np.searchsorted(notes['duet'], t, side='right'))
                fr = fr * (1 - 0.55 * fade) + S.chase(k, cols=(BIRD, BIRD, BEAGLE, BEAGLE, None, None), lv=0.7 * fade,
                                                      spacing=2)
                for tb in downs['duet']:
                    fr += S.wave(t, tb, BIRD, 0.7 * fade, origin=pd_, speed=800, width=60, decay=0.6)
                fr += keyboard(S, t, tunes['duet'], WHITE, 0.6 * fade, decay=0.15, width=20)
            a = t - (M['duet'] - 0.4)
            if 0 <= a < 0.8:                                       # he lands
                fr += light(BIRD, 0.9 * np.exp(-a / 0.2) * S.blob(pbird, 60))

        # the kitchen: tiles marching on the wings, the stove roaring as he stirs, a run on every bar, chevrons
        if M['kitchen'] <= t < M['finale'] + 0.5:
            a = t - M['kitchen']
            on = float(smoothstep(0, 0.4, a) * smoothstep(M['finale'] + 0.5, M['finale'], t))
            fr += S.sweep(t, M['kitchen'], 0.8, WHITE, 0.9, frm='centre', width=80, trail=0.3)
            bt = 60 / 150
            floor = S.wings + S.run['Side']
            fr = fr * (1 - 0.5 * on * floor[:, None]) + S.stripes(a / bt, (RED, WHITE), lv=0.7 * on, period=18,
                                                                   mask=floor)
            fr += light(ORANGE, 0.5 * on * (0.6 + 0.4 * np.sin(0.08 * d - 11 * t)) * S.porch)
            fr += S.run_flash(t, downs['kitchen'], cols=(WHITE, BIRD, ORANGE), lv=0.8 * on, decay=0.3)
            fr += keyboard(S, t, tunes['kitchen'], WHITE, 0.65 * on)
            fr += light(WHITE, 0.5 * pulse(t, gbeats['kitchen'], 0.1) * S.blob(pd_, 30) * on)
            for tb in downs['kitchen'][6:] + gbeats['kitchen'][-4:]:
                fr += S.sweep(t, tb, 0.35, WHITE, 0.7, frm='ends', width=50, trail=0.15)

        # the finale: zigzags on the whole house, a colour a bar, a run flashing on every beat, a sweep, the button
        if t >= M['finale']:
            ph = (t - M['finale']) / (60 / 184)
            bar = min(int(ph // 4), 7)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            fr = fr * (1 - 0.6 * fade) + S.zigzag(ph / 2, lv=0.85 * fade, col=fin_cols[bar], travel=0.25 * (bar >= 4))
            fr += S.run_flash(t, gbeats['finale'], cols=(WHITE, BIRD), lv=0.55 * fade, decay=0.12)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.7 * fade)
            fr += S.sweep(t, downs['finale'][6], 1.6, WHITE, 0.9, frm='right', width=90, trail=0.4)
            a = t - last['finale']
            if 0 <= a < 1.2:
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.ones(S.N))
            a = t - M['button']
            if a >= 0:
                fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * np.ones(S.N))
                fr += light(GOLD, 0.9 * np.exp(-a / 0.5) * np.ones(S.N))

        # the characters, over everything
        if t >= M['worry'] - 0.3:
            facing = 1
            fr = S.boy(fr, p, min(1.0, (t - M['worry'] + 0.3) / 0.3) * (0.9 + 0.15 * beat), facing=facing, t=t,
                       glow=0.3 + 0.2 * (M['relief'] <= t < M['snag']))
        if M['blanket'] <= t:
            fr = S.blanket_boy(fr, pb, 1.0 - 0.4 * (t >= M['beagle'] + 1.5), facing=-1 if t < M['snag'] else 1, t=t)
        if t >= M['beagle']:
            lvl = min(1.0, (t - M['beagle']) / 0.15) * (0.95 + 0.15 * beat)
            fr = S.beagle(fr, pd_, lvl, facing=dog_facing(t), t=t, chef=t >= M['chef'])
        if t >= M['bird']:
            hop = 0.15 * pulse(t, notes['duet'], 0.1) if t >= M['duet'] else 0.0
            fr = S.bird(fr, pbird, min(1.0, (t - M['bird']) / 0.3) + hop, t=t, facing=-1 if t < M['duet'] else 1)

        out[f] = fr * float(smoothstep(D, D - 1.2, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    parts = {
        ('worry', 'tune'): [('piano', 0, -2, 0.85)],
        ('worry', 'comp'): [('piano', 0, -14, 0.4)],
        ('blanket', 'tune'): [('piano', 0, -4, 0.8), ('flutes', 0, -16, 0.3)],
        ('blanket', 'comp'): [('piano', 0, -12, 0.45)],
        ('idea', 'tune'): [('piano', 0, 0, 0.8), ('flutes', 0, -10, 0.35)],
        ('idea', 'comp'): [('piano', 0, -12, 0.45), ('choir', 12, -20, 0.4)],
        ('relief', 'tune'): [('piano', 0, 8, 0.85)],
        ('beagle', 'tune'): [('clarinets', 0, 4, 0.8), ('piano', 0, -10, 0.4)],
        ('chef', 'tune'): [('piano', 0, 8, 0.85), ('harmon trumpet', 0, -2, 0.5), ('xylo', 12, -10, 0.3)],
        ('chef', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('bird', 'tune'): [('flutes', 0, 4, 0.8), ('xylo', 0, -8, 0.35)],
        ('bird', 'comp'): [('piano', 0, -14, 0.4)],
        ('duet', 'tune'): [('flutes', 0, 4, 0.75), ('clarinets', -12, 0, 0.6), ('xylo', 0, -10, 0.3)],
        ('duet', 'comp'): [('piano', 0, -12, 0.45)],
        ('kitchen', 'tune'): [('piano', 0, 10, 0.85), ('xylo', 12, -8, 0.3), ('trumpets', 0, -12, 0.3)],
        ('kitchen', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -12, 0.3)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('flutes', 0, -10, 0.3)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    B.effects([(0, -2), (M['kitchen'], 0), (M['finale'], -3)])
    for m in (63, 67, 70, 74):                                      # the yard: a soft open chord
        B.play('choir', m, 0.2, 1.4, 48, gain=0.3)
    # his footsteps in (soft, on the waltz's first beat and its third)
    steps = [tb for tb in C.times('bass', 'blanket') if tb < M['idea'] - 0.6]
    for tb in steps:
        B.hit('hoof soft', tb, 70, gain=0.35, pan=S.pan(blanket_p(S, tb)), fx=True)
    # the idea: a bell for the early dinner, a warm chime for Grandma's, both at the end
    dn = C.downbeats('idea')
    for i in range(6):
        if i % 2 == 0:
            B.clink(dn[i], pan=S.pan(np.mean(P['early'])), gain=0.7)
        else:
            B.play('glock', 72, dn[i], 0.8, 80, pan=S.pan(np.mean(P['gran'])), gain=0.5)
    B.play('choir', 79, dn[6], 2.5, 60, gain=0.35)
    # the snag: who will cook?
    B.fall(M['snag'] + 0.1, pan=S.pan(P['boy']), gain=0.7)
    # pop: Snoopy, his woofs, the toque
    B.boing(M['beagle'], pan=S.pan(P['dog']), gain=0.8)
    B.woof(M['beagle'] + 0.25, pan=S.pan(P['dog']))
    for tb in C.downbeats('beagle')[::2][1:]:
        B.woof(tb + 0.1, pan=S.pan(dog_p(S, tb)), big=0.8)
    B.hit('bell tree', M['chef'] - 0.3, 100, gain=0.5, pan=S.pan(P['dog']))
    B.hit('crash', M['chef'], 100, gain=0.35, pan=S.pan(P['dog']))
    B.ding(M['chef'] + 0.05, pan=S.pan(P['dog']), gain=0.6)
    # the bird: twitters on its way in, a happy flurry on landing, chirps in the duet
    for k in range(5):
        tc = M['bird'] + 0.3 + k * 1.05
        B.chirp(tc, n=3, pan=S.pan(bird_p(S, tc)), gain=0.8, seed=k)
    B.chirp(M['duet'] - 0.4, n=6, pan=S.pan(P['dog']), gain=1.0, seed=9)
    for tb in C.downbeats('duet')[1:]:
        B.chirp(tb + 0.05, n=2, pan=S.pan(P['dog']), gain=0.7, seed=int(tb))
    B.woof(C.downbeats('duet')[2] + 0.4, pan=S.pan(P['dog']), big=0.7)
    # the kitchen: pots and pans on the bars, a timer's ding, the stove
    for i, tb in enumerate(C.downbeats('kitchen')):
        B.clink(tb + 0.02, pan=S.pan(P['dog']) + (0.2 if i % 2 else -0.2), gain=0.5, pitch=-2 * (i % 3))
    B.fire(M['kitchen'] + 0.5, M['finale'], level=0.35, pan=S.pan(P['dog']))
    B.ding(M['finale'] - 0.05, pan=S.pan(P['dog']), gain=0.7)
    # the finale's sweep and the button
    B.whoosh(C.downbeats('finale')[6], 1.6, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - M['finale']) / 8)
    B.hit('cymbal swell', M['button'] - 1.4, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.woof(M['button'] + 0.5, pan=S.pan(P['dog']), big=1.0)
    B.finish()
