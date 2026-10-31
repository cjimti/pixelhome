"""The Phone Call: Peppermint Patty phones, invites herself to his Thanksgiving dinner, then her friends; the phone keeps ringing.

The yard at the end of the afternoon; Charlie Brown pops up on the porch and mopes about to his wistful theme,
his zigzag shirt swinging on the porch and spreading to the wings, each bass step sending a little amber ripple out
from him. The phone rings: the porch rattles white and gold, a ring running out to both ends on every ring, and he
jumps for it. On the line, Peppermint Patty, way off at the free end of Right: her brash theme on a muted trumpet,
every note a green dash racing down the wire to him, Right churning green behind her while his yellow shrinks to the
phone. Half way she invites herself: a ping-pong table appears on the porch with a green place set. Stop-time: three
times he tries to get a word in (a yellow flash from him) and three times her green slams back over him; the second
time she adds Marcie (an orange place). She hangs up, the green drains out the end of the roof, and he
is alone with his theme in the dusk: violet swells from him, and a stove glows on the porch, sputters and dies (he
can't cook). A hush, the house nearly dark; then the phone again, a ring that fills the whole house. She's back: the
boy with the ball cap too (a red place). Then it never stops: the trio doubles up, the house a green and yellow
marquee with a run flashing on every bar, rings coming faster and faster from the phone while callers' dashes stream
in from Right and he dashes back and forth on the porch. The main title takes the house in zigzags of yellow, green,
orange and red, a sweep from the end of Right, the last chord. A breath of quiet. The phone rings.

compose() lays the music end to end (pixelhome/chef_charlie.py) and lists the rings; render() and score() both read
its events, marks and rings, so every flash lands on the music. boy_p() is his position, shared too."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, ORANGE, RED, GOLD, GREEN,
                                    GLASSES, CAP, VIOLET, BLUE)

CODE = 'CC02'
TITLE = 'The Phone Call'
KIND = 'show'
DESCRIPTION = ("Peppermint Patty phones and invites herself to Charlie Brown's Thanksgiving dinner, then Marcie and "
    "Franklin. He's going to Grandma's and can't cook. He hangs up. The phone rings again, and again.")
VOICEOVER = 'One phone call, and suddenly Charlie Brown is hosting Thanksgiving for everybody.'


def compose():
    C = Chart()
    C.rings = []                                                    # (start, seconds) of every ring of the phone
    C.rest(1.6)                                                     # the yard comes up
    C.mark('mope')
    C.play('boy', style='two', bars=(0, 8), bpm=112, tag='mope')    # he mopes about the porch
    C.mark('ring1')
    C.rings += [(C.t, 1.1), (C.t + 1.8, 1.1)]
    C.rest(2.9)
    C.mark('answer')
    C.rest(0.7)                                                     # he picks up
    C.mark('call')
    C.play('tomboy', style='swing', bars=(0, 8), tag='call')        # she talks; half way she invites herself
    C.mark('stop')
    C.play('tomboy', style='stop', bars=(4, 8), tag='stop')         # he tries to get a word in
    C.mark('alone')
    C.play('boy', style='ballad', bars=(4, 8), bpm=96, tag='alone')  # he hangs up: Grandma's, and he can't cook
    C.mark('hush')
    C.rest(1.0)
    C.mark('ring2')
    C.rings.append((C.t, 1.1))
    C.rest(1.5)
    C.mark('call2')
    C.play('tomboy', style='swing', bars=(4, 8), bpm=152, tag='call2')          # she's back, with another friend
    C.mark('frenzy')
    t0, beat = C.play('tomboy', style='drive', bars=(0, 8), bpm=168, tag='frenzy')
    C.rings += [(t0 + k * beat, 0.5 if k < 28 else 0.3) for k in (0, 8, 14, 18, 22, 24, 26, 28, 29, 30, 31)]
    C.mark('finale')
    C.play('title', style='swing', tag='finale')
    C.mark('button')
    C.button('F6', bpm=152, beats=2)
    C.rest(1.4)
    C.mark('gag')
    C.rings.append((C.t, 0.9))                                      # and again
    C.rest(2.5)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
RINGS = C.rings

PLACES = {}


def places(S):
    """Where things are: his spot and the phone on Porch Front, the table further along it, her at Right's far end."""
    if not PLACES:
        PLACES.update(home=S.at('Porch Front', 0.22), phone=S.at('Porch Front', 0.4),
                      table=S.at('Porch Front', 0.76), her=S.at('Right', 0.86))
    return PLACES


def boy_p(S, t):
    """Pacing on the porch, to the phone when it rings, a few steps away after she hangs up, frantic in the frenzy."""
    P = places(S)
    ph = P['phone'] - 12
    if t < M['ring1']:
        return P['home'] + 40 * np.sin(2 * np.pi * (t - M['mope']) / (16 * 60 / 112))
    if t < M['alone']:
        return P['home'] + (ph - P['home']) * float(smoothstep(M['ring1'] + 0.2, M['answer'], t))
    if t < M['ring2']:
        return ph - 50 * float(smoothstep(M['alone'] + 1, M['alone'] + 5, t))
    if t < M['frenzy']:
        return ph - 50 + 50 * float(smoothstep(M['ring2'] + 0.1, M['ring2'] + 0.5, t))
    if t < M['finale']:
        k = (t - M['frenzy']) / (2 * 60 / 168)                     # back and forth every two beats
        return ph + 55 * (2 * float(smoothstep(0, 1, np.abs((k % 2) - 1))) - 1)
    return ph


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The tune plays the roofline: each note sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def dashes(S, t, times, a, b, cols, lv, travel=0.8, life=1.0, w=30.0):
    """A dash of light leaving a at each of times and racing to b (the voice down the wire)."""
    out = np.zeros((S.N, 3))
    times = np.asarray(times, float)
    for i in np.flatnonzero((times <= t) & (times > t - life)):
        x = t - times[i]
        front = a + (b - a) * min(x / travel, 1.0)
        out += light(cols[i % len(cols)], lv * (1 - x / life) * np.exp(-((S.d - front) / w) ** 2))
    return out


def ringing(S, t, origin, lv=1.0, reach=1.0):
    """The phone's bell: while it rings the lights round it rattle white and gold (alternate pixels swapping twenty
    times a second, so the level holds steady), and each ring sends a gold ring out along the roof."""
    out = np.zeros((S.N, 3))
    for t0, dur in RINGS:
        a = t - t0
        if 0 <= a < dur:
            env = float(smoothstep(0, 0.03, a) * smoothstep(dur, dur - 0.06, a))
            area = np.clip(S.blob(origin, 150 * reach) + 0.6 * S.porch * min(reach, 1.0), 0, 1)
            if reach >= 2.5:                                        # the whole house rings
                area = np.ones(S.N)
            alt = ((S.G.pi + int(a * 20)) % 2).astype(float)
            out += light(WHITE, lv * env * area * alt) + light(GOLD, lv * env * area * (1 - alt))
        if 0 <= a < 3:
            out += S.wave(t, t0, GOLD, 0.8 * lv, origin=origin, speed=900, width=60, decay=0.6 * reach)
    return out


def render(G, seed=2):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    tunes = {g: C.tunes(g) for g in ('mope', 'call', 'stop', 'alone', 'call2', 'frenzy', 'finale')}
    notes = {g: [n[0] for n in v] for g, v in tunes.items()}
    last = {g: v[-1][0] for g, v in tunes.items()}
    mope_bass = C.times('bass', 'mope')
    mope_downs = C.downbeats('mope')
    hits = C.times('hit', 'stop')
    call_downs, call2_downs = C.downbeats('call'), C.downbeats('call2')
    alone_downs = C.downbeats('alone')
    fz_beats, fz_downs = C.beat_times('frenzy'), C.downbeats('frenzy')
    fin_beats, fin_downs = C.beat_times('finale'), C.downbeats('finale')
    b_fin = 60 / 152
    places_at = [(call_downs[4], -4, GREEN), (hits[1], 0, GLASSES), (call2_downs[3], 4, CAP)]
    fin_cols = [YELLOW, GREEN, YELLOW, ORANGE, YELLOW, RED, GREEN, YELLOW]
    yard_lv = [(0, 0.0), (1.6, 0.85), (M['ring1'], 0.85), (M['ring1'] + 0.3, 0.6), (M['alone'], 0.6),
               (M['alone'] + 3, 0.7), (M['hush'], 0.55), (M['hush'] + 0.7, 0.1), (M['ring2'], 0.1),
               (M['ring2'] + 0.3, 0.6), (M['finale'], 0.5), (M['finale'] + 1, 0.3), (M['end'], 0.3)]
    phone = P['phone']

    for f in range(F):
        t = f * DT
        sad = float(smoothstep(M['alone'], M['alone'] + 3, t) * smoothstep(M['ring2'] + 0.3, M['ring2'], t))
        fr = S.yard(t, lv=float(keys(t, yard_lv)), leaves=1.0 + 0.4 * sad, sun=1 - 0.7 * sad)
        p = boy_p(S, t)
        beat = pulse(t, beats, 0.14)

        # he mopes: his zigzag swings on the porch, spreads to the wings at bar 5; every bass step ripples out
        if M['mope'] <= t < M['ring1'] + 0.4:
            a = t - M['mope']
            fade = float(smoothstep(M['ring1'] + 0.4, M['ring1'], t))
            if a < 0.6:
                fr += light(WHITE, 0.8 * np.exp(-a / 0.15) * S.blob(p, 50))
            ph = a / (60 / 112)
            wing = float(smoothstep(mope_downs[4] - 0.3, mope_downs[4] + 1.0, t))
            mask = np.clip(S.porch * smoothstep(0, 1.2, a) + S.wings * wing, 0, 1) * fade
            fr = fr * (1 - 0.55 * mask[:, None]) + S.zigzag(ph, lv=0.75, travel=0.15, mask=mask)
            for tb in [x for x in mope_bass if x <= t][-2:]:
                fr += S.wave(t, tb, AMBER, 0.6 * fade, origin=boy_p(S, tb), speed=600, width=50, decay=0.5)
            fr += keyboard(S, t, tunes['mope'], GOLD, 0.6 * fade, width=32)
            fr += S.sweep(t, last['mope'], 1.6, GOLD, 0.7, frm='centre', width=100, trail=0.6)

        # the bell: the porch rattles, rings run out along the roof (the second call fills the whole house)
        reach = 2.5 if M['ring2'] <= t < M['call2'] else 1.6 if t >= M['frenzy'] else 1.0
        fr += ringing(S, t, phone, lv=1.0, reach=reach)

        # on the line: green dashes down the wire from her, her green churning up the wire, pushing his yellow to the phone
        on_call = M['call'] <= t < M['alone'] or M['call2'] <= t < M['frenzy']
        if M['answer'] <= t < M['alone'] + 1.0 or M['call2'] - 0.3 <= t < M['frenzy'] + 0.5:
            if M['call2'] - 0.3 <= t:
                a0, gname = M['call2'], 'call2'
                fade = float(smoothstep(M['frenzy'] + 0.5, M['frenzy'], t))
            else:
                a0, gname = M['call'], 'call'
                fade = float(smoothstep(M['alone'] + 1.0, M['alone'], t))
            a = t - a0
            on = float(smoothstep(-0.3, 0.2, a)) * fade
            corner = S.at('Porch Right', 1.0)
            if gname == 'call':                                    # her green pushes up the wire toward the phone
                frontier = corner - (corner - phone - 25) * float(smoothstep(M['call'], M['stop'], t))
            else:
                frontier = phone + 25
            frontier = L - (L - frontier) * float(smoothstep(-0.3, 0.6, a))
            her_side = S.span(frontier, L + 20) * on
            bt = 60 / (152 if gname == 'call2' else 144)
            fr = fr * (1 - 0.55 * her_side[:, None])
            fr += S.chase(-2 * a / bt, cols=(GREEN, GREEN, None), lv=0.75, spacing=2, mask=her_side)
            nts = notes['call'] + notes['stop'] if gname == 'call' else notes['call2']
            fr += dashes(S, t, nts, P['her'] - 10, S.at('Left', 0.0), (GREEN,), 0.95 * fade, travel=1.6, life=1.8)
            fr += light(GREEN, 0.5 * pulse(t, nts, 0.15) * S.blob(P['her'], 40) * fade)
            mine = S.span(S.at('Left', 0.0), min(frontier, phone + 25) - 10) * (1 - her_side) * on
            fr = fr * (1 - 0.5 * mine[:, None]) + S.zigzag(a / bt, lv=0.55, mask=mine)
            fr = S.tomboy(fr, P['her'], on, facing=-1, t=t)
            if a < 0.6 and a >= 0:
                fr += light(GREEN, 0.9 * np.exp(-a / 0.2) * S.run['Right'])

        # she invites herself: the porch floods green and a table appears with her place set
        tb = places_at[0][0]
        if tb <= t < M['stop']:
            b = t - tb
            fr += light(GREEN, 0.85 * np.exp(-b / 0.9) * S.porch)
            fr += light(WHITE, 0.6 * np.exp(-b / 0.15) * S.blob(P['table'], 60))

        # stop-time: he tries (yellow from him), she slams back (green from the end of Right) - three times
        if M['stop'] <= t < M['alone']:
            for i, th in enumerate(hits):
                a = t - th
                if 0 <= a < 1.4:
                    fr += light(YELLOW, 0.9 * np.exp(-a / 0.18) * S.span(S.at('Left', 0.0), phone + 10))
                    u = float(smoothstep(0.18, 0.45, a))
                    front = L - (L - phone) * u
                    fr += light(GREEN, 0.95 * u * np.exp(-max(a - 0.45, 0) / 0.5) * S.span(front, L))
            b = t - hits[1]
            if 0 <= b < 2:                                         # Marcie: an orange place
                fr += S.confetti([(hits[1] + 0.3, 0.9, P['table'])], t, colors=(GLASSES, ORANGE, WHITE), n=18,
                                 reach=0.4, seed=5)
        # she hangs up: the green drains out the end of Right
        if M['alone'] <= t < M['alone'] + 1.4:
            a = t - M['alone']
            front = phone + (L + 200 - phone) * float(smoothstep(0, 1.0, a))
            fr += light(GREEN, 0.8 * S.span(front, L + 100) * np.exp(-a / 0.8))

        # alone: violet swells from him on each bar; a stove glows on the porch, sputters, dies
        if M['alone'] <= t < M['ring2']:
            fade = float(smoothstep(M['hush'] + 0.6, M['hush'], t))
            for tb in alone_downs:
                fr += S.wave(t, tb, VIOLET, 1.0 * fade, origin=p, speed=420, width=170, decay=1.8)
                fr += S.wave(t, tb + 0.3, BLUE, 0.6 * fade, origin=p, speed=300, width=90, decay=1.4)
            fr += keyboard(S, t, tunes['alone'], GOLD, 0.5 * fade, width=34)
            mine = S.span(p - 70, p + 40)
            fr = fr * (1 - 0.4 * mine[:, None]) + S.zigzag((t - M['alone']) / 0.625 / 2, lv=0.45 * fade, mask=mine)
            if alone_downs[1] <= t < alone_downs[3] + 0.4:
                a = t - alone_downs[1]
                die = float(smoothstep(alone_downs[3] - 0.6, alone_downs[3] + 0.3, t))
                spit = 0.8 + 0.2 * np.sin(23 * t) * np.sin(7.3 * t)
                flame = S.run['Porch Front'] * (0.6 + 0.4 * np.sin(0.09 * d - 9 * t) * np.sin(0.05 * d + 5 * t))
                fr += light(ORANGE, (1.0 * smoothstep(0, 0.8, a) * spit * (1 - die)) * np.maximum(flame, S.blob(P['table'], 90)))
                fr += light(RED, 0.7 * (1 - die) * smoothstep(0, 1.5, a) * S.blob(P['table'], 40))
            a = t - alone_downs[3]
            if 0 <= a < 1.5:                                       # out: a puff of smoke-blue
                fr += light(BLUE, 0.5 * np.exp(-a / 0.4) * S.blob(P['table'], 90))

        # the place settings, once there is a dinner to set
        if t >= places_at[0][0] and t < M['button'] + 0.5:
            b = t - places_at[0][0]
            food = [(o, c) for tp, o, c in places_at if t >= tp]
            glow = 1.0 + 0.3 * beat
            fr = S.table(fr, P['table'], min(1.0, b / 0.2) * glow * (1 - 0.3 * (M['hush'] <= t < M['ring2'])),
                         half=6, net=False, food=food)
            for tp, o, c in places_at:
                b = t - tp
                if 0 <= b < 0.8:
                    fr += light(c, 0.9 * np.exp(-b / 0.25) * S.blob(P['table'] + 5 * o, 40))

        # the frenzy: a green and yellow marquee on the whole house, a run flashing on each bar, callers streaming in
        if M['frenzy'] <= t < M['finale'] + 0.5:
            a = t - M['frenzy']
            u = a / (M['finale'] - M['frenzy'])
            fade = float(smoothstep(M['finale'] + 0.5, M['finale'], t))
            lv = (0.55 + 0.4 * u) * fade
            fr = fr * (1 - 0.5 * fade) + S.chase(2 * a / (60 / 168), cols=(GREEN, YELLOW, None), lv=lv, spacing=3)
            fr += S.run_flash(t, fz_downs, cols=(GREEN, YELLOW, ORANGE, RED), lv=0.8 * fade, decay=0.3)
            fr += dashes(S, t, notes['frenzy'], L + 30, phone + 8, (GREEN, GLASSES, CAP), 0.85 * fade)
            fr += light(WHITE, 0.4 * pulse(t, fz_beats, 0.08) * S.blob(p, 30) * fade)

        # the finale: zigzags on the whole house, a colour a bar, a run flashing on every beat, a sweep, the button
        if t >= M['finale'] and t < M['gag']:
            ph = (t - M['finale']) / b_fin
            bar = min(int(ph // 4), 7)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.2, t))
            fr = fr * (1 - 0.6 * fade) + S.zigzag(ph, lv=0.85 * fade, col=fin_cols[bar], travel=0.25 * (bar >= 4))
            fr += S.run_flash(t, fin_beats, cols=(WHITE, YELLOW), lv=0.55 * fade, decay=0.15)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.7 * fade)
            fr += S.sweep(t, fin_downs[6], 2.4, WHITE, 0.9, frm='right', width=90, trail=0.5)
            a = t - last['finale']
            if 0 <= a < 1.2:
                fr += light(YELLOW, 0.7 * np.exp(-a / 0.3) * np.ones(S.N))
            a = t - M['button']
            if a >= 0:
                fr += light(YELLOW, np.exp(-a / 0.45) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-a / 0.12) * np.ones(S.N))

        # the boy, over everything; the phone beside him jumps while it rings
        if t >= M['mope']:
            ringing_now = any(t0 <= t < t0 + dur for t0, dur in RINGS)
            jit = 3 * np.sin(2 * np.pi * 20 * t) if ringing_now else 0.0
            fr = S.sprite(fr, phone + 6 + jit, [(1, RED, 1.0), (0, RED, 1.0)], 1.0)
            run = 1.0 if M['frenzy'] <= t < M['finale'] else 0.0
            facing = 1 if t >= M['ring1'] else (1 if np.cos(2 * np.pi * (t - M['mope']) / (16 * 60 / 112)) > 0 else -1)
            jump = 0.0
            for t0, dur in RINGS:
                if 0 <= t - t0 < 0.3:
                    jump = 0.3
            lvl = min(1.0, (t - M['mope']) / 0.2) * (0.9 + 0.15 * beat + jump)
            fr = S.boy(fr, p, lvl, facing=facing, t=t, run=run, glow=0.3 + 0.15 * (t >= M['finale']))

        out[f] = fr * float(smoothstep(D, D - 1.0, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    trumpet = [('harmon trumpet', 0, 6, 1.0), ('buzz trombone', -12, -14, 0.3)]
    parts = {
        ('mope', 'tune'): [('piano', 0, -2, 0.85)],
        ('mope', 'comp'): [('piano', 0, -14, 0.4)],
        ('call', 'tune'): trumpet,
        ('call', 'comp'): [('piano', 0, -10, 0.45)],
        ('stop', 'tune'): [('harmon trumpet', 0, 8, 1.0)],
        ('stop', 'hit'): [('piano', 0, 6, 0.8), ('muted horn', 0, -4, 0.45)],
        ('alone', 'tune'): [('piano', 0, -4, 0.85)],
        ('alone', 'comp'): [('piano', 0, -14, 0.45), ('choir', 12, -22, 0.35)],
        ('call2', 'tune'): trumpet,
        ('call2', 'comp'): [('piano', 0, -10, 0.45)],
        ('frenzy', 'tune'): [('harmon trumpet', 0, 10, 0.9), ('piano', 12, -12, 0.35), ('xylo', 12, -10, 0.3)],
        ('frenzy', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -12, 0.3)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('vibes', 0, -10, 0.25)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.4)],
    }
    B.perform(C.events, parts)
    ph = S.pan(P['phone'])
    her = S.pan(P['her'])
    B.effects([(0, -2), (M['frenzy'], 0), (M['finale'], -3), (M['gag'] - 0.2, 0)])
    # the yard: a soft open chord before he pops up
    for m in (63, 67, 70, 74):
        B.play('choir', m, 0.2, 1.6, 48, gain=0.3)
    B.boing(M['mope'], pan=S.pan(P['home']), gain=0.6)
    # every ring of the phone, his jump at the first, the receiver up and down
    for t0, dur in RINGS:
        B.phone(t0, rings=1, pan=ph, ring=dur, gain=1.0 if t0 < M['frenzy'] else 0.85)
    B.boing(M['ring1'] + 0.05, pan=ph, gain=0.5, high=1.4)
    B.hit('claves', M['answer'] + 0.1, 100, pitch=-5, gain=0.5, pan=ph, fx=True)
    B.hit('woodblock', M['call'] - 0.05, 90, gain=0.4, pan=her)
    # she invites herself and her friends: a bright ding for each place set
    B.ding(C.downbeats('call')[4], pan=S.pan(P['table']), gain=0.8)
    B.ding(C.times('hit', 'stop')[1] + 0.3, pan=S.pan(P['table']), gain=0.7)
    B.ding(C.downbeats('call2')[3], pan=S.pan(P['table']), gain=0.8)
    for th in C.times('hit', 'stop')[:3]:                          # his tries, cut off: a little gulp each
        B.slide(th + 0.15, 0.25, up=True, pan=ph, gain=0.3, lo=700, hi=1000)
    # she hangs up: the receiver clicks and the dial tone hums away
    B.hit('claves', M['alone'], 110, pitch=-7, gain=0.5, pan=ph, fx=True)
    B.whoosh(M['alone'] + 0.1, 0.9, up=False, pan=lambda tt: her, gain=0.35)
    # the stove sputters and dies
    downs = C.downbeats('alone')
    B.fire(downs[1], downs[3] + 0.2, level=0.5, pan=S.pan(P['table']))
    B.fall(downs[3] + 0.2, pan=S.pan(P['table']), gain=0.6)
    # the second call: a cymbal swell into the ring, he dashes for it
    B.hit('cymbal swell', M['ring2'] - 0.8, 80, gain=0.3)
    B.steps(M['ring2'] + 0.1, M['ring2'] + 0.5, beat=0.12, pan=ph, gain=0.7)
    # the frenzy: his feet back and forth
    B.steps(M['frenzy'], M['finale'], beat=60 / 168, pan=lambda tt: S.pan(boy_p(S, tt)), gain=0.5)
    # the finale's sweep and the button, and the last ring
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - M['finale']) / 10)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.boing(M['gag'] + 0.05, pan=ph, gain=0.5, high=1.4)
    B.finish()
