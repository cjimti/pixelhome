"""Over the River: Grandma invites everyone, they all pile into the car and sing their way there through the snow.

The backyard is dim and blue after the quarrel, and the old telephone rings at Charlie Brown's end of the
house, the free end of Right: white bells on the porch rail, three times. It is Grandma, and her warm voice comes down
the line from her house at the far end of Left, a gold pulse running the whole roof on every bar of her homey tune
while the kids light up along Right one by one; on the last bar they cheer. A horn: her car pulls in from past the
end of Right and the kids hop in, a boing and a bright flash of their colour each. Then the engine putts and the song
starts: "Over the River and Through the Wood" (Lydia Maria Child, 1844, a traditional tune in the public domain) as
a jazz waltz. The car drives the whole roofline toward Grandma's, the snowy road streaming past it, fence posts and
pines going by and snow falling, and the stretch it has driven stays white with its tracks. First the kids' choir
sings it with the trio along Right and up Porch Right through the wood; then the trio takes it over the river, Porch
Front turned to rolling blue water with the car on the bridge; then everybody, a step higher, with sleigh bells,
down Porch Left and along Left, every beat lighting a run gold and the tune throwing snow sparks back from the car.
Grandma's windows grow warmer as they near. On the last long note the car stops at her door, two beeps, one beat of
stillness, and her house opens: warm gold sweeps the whole roof from her end to Charlie Brown's, rings run out from her door,
the kids cheer and leaves and confetti fly, and her tune closes it on the whole band.

compose() lays the music end to end (pixelhome/chef_charlie.py); render() and score() read its events and marks.
car_p() is the car's position, shared by both."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, YELLOW, WHITE, AMBER, ORANGE, GOLD, GREEN, GLASSES,
                                    STRIPE, CAP, ICE, SNOW, WARM, SEA, FOAM, BROWN, NIGHT, LEAVES, JELLY, CAR)

CODE = 'CC12'
TITLE = 'Over the River'
KIND = 'show'
DESCRIPTION = ("Charlie Brown's grandmother phones and invites everyone. The gang piles into her car and sings its "
               'way through the snow, over the river and through the wood, to her warm front door.')
VOICEOVER = 'Grandma invites everyone, so Charlie Brown and the gang pile in and sing.'

# "Over the River and Through the Wood": the traditional tune (public domain), in C, 3/4, as it is printed in
# children's songbooks; here a jazz waltz. Beats from the first bar; 32 bars (two halves of 16).
RIVER = dict(meter=3, bpm=160, swing=True, id='river', name='Over the River and Through the Wood (traditional)',
    melody=[(0, 1, 'G4'), (1, 1, 'G4'), (2, 1, 'G4'),                       # O-ver the
            (3, 1, 'G4'), (4, 1, 'E4'), (5, 1, 'F4'),                       # riv-er and
            (6, 2, 'G4'), (8, 1, 'G4'),                                     # through the
            (9, 2, 'G4'), (11, 1, 'G4'),                                    # wood, to
            (12, 1, 'C5'), (13, 1, 'C5'), (14, 1, 'C5'),                    # grand-fa-ther's
            (15, 2, 'B4'), (17, 1, 'A4'),                                   # house we
            (18, 5, 'G4'), (23, 1, 'G4'),                                   # go; the
            (24, 1, 'F4'), (25, 1, 'F4'), (26, 1, 'F4'),                    # horse knows the
            (27, 2, 'F4'), (29, 1, 'G4'),                                   # way to
            (30, 1, 'E4'), (31, 1, 'E4'), (32, 1, 'E4'),                    # car-ry the
            (33, 2, 'E4'), (35, 1, 'E4'),                                   # sleigh through
            (36, 2, 'D4'), (38, 1, 'D4'),                                   # white and
            (39, 2, 'D4'), (41, 1, 'E4'),                                   # drift-ed
            (42, 3, 'D4'), (45, 3, 'G4'),                                   # snow.
            (48, 1, 'G4'), (49, 1, 'G4'), (50, 1, 'G4'),                    # O-ver the
            (51, 1, 'G4'), (52, 1, 'E4'), (53, 1, 'F4'),                    # riv-er and
            (54, 2, 'G4'), (56, 1, 'G4'),                                   # through the
            (57, 2, 'G4'), (59, 1, 'G4'),                                   # wood, oh,
            (60, 2, 'C5'), (62, 1, 'C5'),                                   # how the
            (63, 2, 'B4'), (65, 1, 'A4'),                                   # wind does
            (66, 5, 'G4'), (71, 1, 'G4'),                                   # blow! it
            (72, 2, 'C5'), (74, 1, 'C5'),                                   # stings the
            (75, 2, 'B4'), (77, 1, 'A4'),                                   # toes and
            (78, 2, 'G4'), (80, 1, 'E4'),                                   # bites the
            (81, 2, 'C4'), (83, 1, 'D4'),                                   # nose as
            (84, 1, 'E4'), (85, 1, 'E4'), (86, 1, 'E4'),                    # o-ver the
            (87, 2, 'D4'), (89, 1, 'D4'),                                   # ground we
            (90, 6, 'C4')],                                                 # go.
    chords=[(3 * i, 3, s) for i, s in enumerate(
        ['C6', 'G7', 'Am7', 'C6', 'Fmaj7', 'G7', 'C6', 'C7', 'Fmaj7', 'G7', 'C6', 'Am7', 'D7', 'D7', 'G6', 'G7',
         'C6', 'G7', 'Am7', 'C6', 'Fmaj7', 'G7', 'C6', 'C7', 'Fmaj7', 'Em7', 'Am7', 'Dm7', 'C6', 'G7', 'C6', 'C6'])])

KIDS = (('boy', YELLOW), ('tomboy', GREEN), ('glasses', GLASSES), ('blanket', STRIPE), ('cap', CAP))


def compose():
    C = Chart()
    C.rest(1.2)                                                     # the dim backyard comes up
    C.mark('phone')
    C.rest(5.8)                                                     # the telephone rings three times
    C.mark('grandma')
    C.play('grandma', style='two', tag='grandma')                   # her warm voice down the line
    C.mark('horn')
    C.play(RIVER, style='brushes', bars=(0, 4), bpm=160, tune=False, tag='pile')   # the car pulls in, they hop in
    C.mark('sing')
    C.play(RIVER, style='waltz', bars=(0, 16), bpm=160, tag='v1')   # the kids' choir, through the wood
    C.mark('river')
    C.play(RIVER, style='waltz', bars=(16, 32), bpm=160, tag='v2')  # the trio, over the river
    C.mark('all')
    C.play(RIVER, style='waltz', bars=(16, 30), bpm=168, transpose=2, tag='v3')   # everybody, a step up
    C.mark('go')
    C.play(RIVER, style='hold', bars=(30, 32), bpm=168, transpose=2, tag='go')    # the last long note: arrival
    C.mark('door')
    C.rest(0.9)                                                     # two beeps, a beat of stillness
    C.mark('open')
    C.play('grandma', style='swing', bars=(5, 8), bpm=120, tag='home')            # her house opens
    C.mark('button')
    C.button('F6', bpm=120, beats=3)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
PLACES = {}


def places(S):
    """Path distances: the kids waiting along Right, where the car parks, the river (Porch Front), Grandma's door."""
    if not PLACES:
        PLACES.update(enter=S.L + 60, park=S.at('Right', 0.62), gran=S.at('Left', 0.07),
                      kids=[S.at('Right', 0.3 + 0.12 * i) for i in range(len(KIDS))],
                      river=(S.at('Porch Front', 0.0), S.at('Porch Front', 1.0)), house=S.at('Left', 0.0))
    return PLACES


def hops():
    """When each kid hops into the car: the downbeats of the pile-in vamp, after the car stops."""
    downs = C.downbeats('pile')
    return [downs[0] + 0.35 + 0.42 * i for i in range(len(KIDS))]


def car_p(S, t):
    """The car: in from past the end of Right to park by the kids, then the whole roofline to Grandma's door, steady
    through the song and easing to a stop on the last long note."""
    P = places(S)
    if t < M['horn']:
        return P['enter']
    if t < M['sing']:
        return P['enter'] + (P['park'] - P['enter']) * float(smoothstep(M['horn'], M['horn'] + 1.4, t))
    t1 = M['go'] + 0.8
    u = np.clip((t - M['sing']) / (t1 - M['sing']), 0, 1)
    # ease out of the start and into the stop, constant speed between
    a = 0.06
    s = np.where(u < a, u * u / (2 * a), np.where(u > 1 - a, 1 - (1 - u) ** 2 / (2 * a), u - a / 2)) / (1 - a)
    return P['park'] + (P['gran'] - P['park']) * float(s)


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
    rings = [M['phone'] + 0.3 + 1.8 * i for i in range(3)]
    g_downs = C.downbeats('grandma')
    g_tune = C.tunes('grandma')
    hop_t = hops()
    song = {g: C.tunes(g) for g in ('v1', 'v2', 'v3', 'go')}
    song_notes = song['v1'] + song['v2'] + song['v3'] + song['go']
    note_t = np.array([n[0] for n in song_notes])
    beats3 = np.array(C.beat_times('v3'))
    downs_song = np.array(C.downbeats('v1') + C.downbeats('v2') + C.downbeats('v3'))
    home_beats = np.array(C.beat_times('home'))
    home_downs = C.downbeats('home')
    lo, hi = P['river']
    river = S.span(lo, hi, 4)
    bridge = (G.pi % 4 == 0) * S.run['Porch Front']
    house = S.span(P['house'] - 5, P['gran'] + 30, 4) * S.run['Left']
    win = house * (G.pi % 5 < 3)
    lv_bg = [(0, 0.0), (M['phone'], 0.9), (M['grandma'], 1.0), (M['horn'], 0.9), (M['sing'], 1.0),
             (M['go'], 1.0), (M['door'] + 0.9, 0.55), (M['open'] + 1.5, 0.35), (D, 0.35)]
    snow_amt = [(0, 0.3), (M['horn'], 0.5), (M['sing'], 0.8), (M['all'], 1.3), (M['go'], 1.0), (M['open'], 0.5),
                (D, 0.3)]
    fin_cols = (WARM, GOLD, ORANGE, YELLOW)

    for f in range(F):
        t = f * DT
        lv = float(keys(t, lv_bg))
        p = car_p(S, t)
        driving = M['sing'] <= t < M['door']

        # the backdrop: the dim blue backyard, then the snowy road streaming past the car
        road = float(smoothstep(M['horn'] + 1.0, M['sing'] + 0.5, t))
        fr = S.backyard(t, lv * 0.85 * (1 - road), bulbs=0.8) if road < 1 else np.zeros((S.N, 3))
        if road > 0:
            fr += S.road(t, lv * road, snow=float(keys(t, snow_amt)), speed=110.0 if driving else 20.0)
        else:
            fr += S.snowfall(t, 0.35 * lv)

        # Grandma's house at the far end of Left: warm windows, warmer as the car nears, wide open at the end
        near = float(smoothstep(P['gran'] + 1400, P['gran'], p)) if t >= M['sing'] else 0.0
        hw = 0.35 + 0.15 * near + 0.5 * float(smoothstep(M['open'], M['open'] + 0.4, t))
        fr = fr * (1 - 0.5 * house[:, None]) + light(WARM, hw * win) + light(AMBER, 0.25 * hw * house)

        # the telephone: the bells on the porch rail by the boy's end shiver white and gold on each ring
        for tr in rings:
            a = t - tr
            if 0 <= a < 1.4:
                ring = (a < 1.1) * (0.6 + 0.4 * np.sin(2 * np.pi * 20 * a))
                fr += light(WHITE, 0.8 * ring * S.blob(P['kids'][0], 30))
                fr += light(GOLD, 0.5 * (a < 1.1) * S.run['Right'] * np.exp(-a / 0.5))

        # Grandma on the line: a gold pulse from her house down the whole roof to the boy on every bar, her tune
        # sparking the front; the kids light up one by one, and on the last bar they cheer
        if M['grandma'] <= t < M['horn'] + 1.0:
            fade = float(smoothstep(M['horn'] + 1.0, M['horn'], t))
            for i, tb in enumerate(g_downs):
                b = t - tb
                if 0 <= b < 3.0:
                    front = P['gran'] + (P['kids'][0] - P['gran']) * min(b / 1.6, 1.0)
                    head = (b < 1.9) * (1 - b / 3.0)
                    fr += light(WARM, 1.0 * fade * head * np.exp(-((d - front) / 110) ** 2))
                    fr += light(WHITE, 0.5 * fade * head * np.exp(-((d - front) / 25) ** 2))
                    wake = S.span(P['gran'], front, 20) * np.exp(-np.maximum(b - (d - P['gran']) /
                                                                 (P['kids'][0] - P['gran']) * 1.6, 0) / 0.9)
                    fr += light(GOLD if i % 2 else ORANGE, 0.6 * fade * wake)
            fr += keyboard(S, t, g_tune, WARM, 0.55 * fade, width=32)
            a = t - g_downs[-1]
            if 0 <= a < 3:
                fr += S.confetti([(g_downs[-1], 1.0, P['kids'][2])], t, colors=[c for _, c in KIDS], n=28,
                                 reach=0.7, seed=2)

        # the car pulls in, and each kid hops in with a flash of their colour
        if M['horn'] <= t < M['sing'] + 1.0:
            for i, th in enumerate(hop_t):
                a = t - th
                if 0 <= a < 0.8:
                    fr += light(KIDS[i][1], 0.9 * np.exp(-a / 0.2) * S.blob(p, 40))
                    fr += S.wave(t, th, KIDS[i][1], 0.6, origin=p, speed=900, width=50, decay=0.4)

        # the drive: the stretch behind the car stays white with its tracks, headlights glow on each downbeat
        if t >= M['sing']:
            done = S.span(p + 8, P['park'], 6) * (t < M['open'] + 2.0)
            fade = float(smoothstep(M['open'] + 2.0, M['open'], t))
            beat_n = (t - M['sing']) / (60 / 160)
            if t < M['river']:                                      # a ribbon of the gang's colours behind the car
                ribbon = S.stripes(beat_n / 2, [c for _, c in KIDS], lv=0.55, period=26.0, mask=done * fade)
            elif t < M['all']:                                      # ice and snow over the river
                ribbon = S.stripes(beat_n / 2, [ICE, SNOW, SEA, ICE], lv=0.45, period=26.0, mask=done * fade)
            else:                                                   # gold on the last stretch
                ribbon = S.stripes(beat_n / 2, [GOLD, WARM, ORANGE, YELLOW], lv=0.55, period=26.0, mask=done * fade)
            fr = fr * (1 - 0.7 * done[:, None]) + ribbon
            if driving:
                fr += light(WARM, 0.6 * pulse(t, downs_song, 0.25) * S.blob(p - 50, 45))
                ahead = S.span(0, p - 10, 10) * (1 - house)        # the road ahead brightens on every bar
                fr *= (1 + 0.6 * pulse(t, downs_song, 0.3) * ahead)[:, None]

        # over the river: Porch Front rolls blue while the car crosses it, a plank bridge under the car
        if M['river'] - 4 <= t < M['all'] + 3:
            rv = float(smoothstep(M['river'] - 4, M['river'] - 1, t) * smoothstep(M['all'] + 3, M['all'], t))
            fr = fr * (1 - 0.8 * rv * river[:, None]) + S.sea(t, rv, swell=1.0, speed=-50) * river[:, None]
            fr += light(BROWN, 0.55 * rv * bridge * S.blob(p, 60))
            fr += light(FOAM, 0.4 * rv * pulse(t, C.downbeats('v2'), 0.3) * river)

        # the song: each note throws a snow spark back from the car; everybody's verse lights a run gold on each beat
        if driving:
            for j in np.flatnonzero((note_t <= t) & (note_t > t - 1.2)):
                b = t - note_t[j]
                q = p + 25 + 520 * b
                fr += light(SNOW if j % 2 else ICE, 1.0 * np.exp(-b / 0.45) * np.exp(-((d - q) / 16) ** 2))
            if t >= M['all']:
                fr += S.run_flash(t, beats3, cols=(GOLD, WARM, AMBER), lv=0.55, decay=0.22,
                                  runs=('Right', 'Left', 'Porch Front', 'Porch Right', 'Porch Left'))
                fr += S.chase(2 * (t - M['all']) / (60 / 168), cols=(GOLD, None, None), lv=0.35,
                              mask=S.span(P['gran'], p - 15))

        # the arrival: stillness, then her house opens and warm gold sweeps the whole roof, rings from her door
        if t >= M['open']:
            a = t - M['open']
            fr += S.sweep(t, M['open'], 2.2, WARM, 1.0, frm='side', width=140, trail=1.5)
            for k, tb in enumerate(home_downs):
                fr += S.wave(t, tb, fin_cols[k % 4], 0.8, origin=P['gran'], speed=900, width=90, decay=1.0)
            fr += S.confetti([(M['open'] + 0.1, 1.0, P['gran']), (home_downs[1], 0.9, S.mid),
                              (home_downs[2], 0.9, S.at('Right', 0.5))], t, colors=LEAVES + JELLY[:3], n=30, seed=5)
            hold = float(smoothstep(0.5, 2.5, a))
            fr += S.zigzag((t - M['open']) / 0.5, lv=0.45 * hold * float(smoothstep(M['button'] + 0.8,
                           M['button'] + 0.2, t)), col=WARM, travel=0.25)
            fr += S.run_flash(t, home_beats, cols=(GOLD, WHITE), lv=0.45, decay=0.15)
            b = t - M['button']
            if b >= 0:
                fr += light(WARM, np.exp(-b / 0.5) * np.ones(S.N))
                fr += light(WHITE, 0.7 * np.exp(-b / 0.12) * np.ones(S.N))

        # the kids waiting along Right, then the car with them in it
        if t < hop_t[-1] + 0.1:
            for i, (who, col) in enumerate(KIDS):
                lit = float(smoothstep(g_downs[min(i + 1, len(g_downs) - 1)] - 0.1,
                                       g_downs[min(i + 1, len(g_downs) - 1)] + 0.2, t)) if i else 1.0
                if t >= hop_t[i]:
                    continue
                kp = P['kids'][i]
                lvl = (0.35 + 0.65 * lit) * float(smoothstep(M['phone'] - 0.5, M['phone'] + 0.5, t))
                if who == 'boy':
                    fr = S.boy(fr, kp, lvl, facing=-1, t=t, glow=0.25)
                elif who == 'tomboy':
                    fr = S.tomboy(fr, kp, lvl, facing=-1)
                elif who == 'glasses':
                    fr = S.glasses(fr, kp, lvl, facing=-1)
                elif who == 'blanket':
                    fr = S.blanket_boy(fr, kp, lvl, facing=-1, t=t)
                else:
                    fr = S.cap_boy(fr, kp, lvl, facing=-1)
        if t >= M['horn']:
            n_in = sum(t >= h for h in hop_t)
            bob = 0.9 + 0.15 * pulse(t, note_t, 0.15) if driving else 1.0
            fr = S.car(fr, p, bob, facing=-1, t=t if driving or t < M['sing'] else 0.0, color=CAR,
                       lights=1.0 if t < M['open'] + 1.5 else 0.6)
            if 0 < n_in:                                            # the kids' colours glowing in the windows
                fr += light(KIDS[(int(t * 2)) % n_in][1], 0.35 * S.blob(p + 10, 8))

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    from pixelhome.audio import note
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.1)
    choir = [('choir', 0, 4, 0.9), ('celesta', 12, -24, 0.35)]
    parts = {
        ('grandma', 'tune'): [('piano', 0, -2, 0.85), ('vibes', 12, -26, 0.2)],
        ('grandma', 'comp'): [('piano', 0, -14, 0.45)],
        ('v1', 'tune'): choir + [('piano', 0, -24, 0.3)],
        ('v1', 'comp'): [('piano', 0, -12, 0.45)],
        ('v2', 'tune'): [('piano', 0, 6, 0.9), ('choir', 0, -18, 0.4)],
        ('v2', 'comp'): [('piano', 0, -10, 0.5)],
        ('v3', 'tune'): [('choir', 0, 8, 0.9), ('piano', 0, 6, 0.75), ('harmon trumpet', 0, -4, 0.55),
                         ('xylo', 12, -16, 0.25)],
        ('v3', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -18, 0.25)],
        ('v3', 'bass'): [('bass', 0, 4, 0.85)],
        ('go', 'tune'): [('choir', 0, 6, 0.95), ('piano', 0, 4, 0.7), ('harmon trumpet', 0, -4, 0.5),
                         ('violins', 12, -20, 0.3)],
        ('go', 'hold'): [('choir', 0, -10, 0.5), ('violins', 0, -24, 0.3)],
        ('go', 'pedal'): [('bass', 0, -4, 0.7)],
        ('home', 'tune'): [('piano', 0, 8, 0.85), ('harmon trumpet', 0, 0, 0.55), ('choir', 12, -14, 0.4)],
        ('home', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -14, 0.3)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4),
                            ('choir', 12, -10, 0.45)],
    }
    B.perform(C.events, parts)
    boy = S.pan(P['kids'][0])
    # the telephone, then a soft wondering chord as he answers
    B.phone(M['phone'] + 0.3, rings=3, pan=boy, gain=0.9)
    for m in (65, 69, 72, 76):
        B.play('choir', m, M['phone'] + 5.0, 2.0, 46, gain=0.3)
    # the kids cheer at the end of her invitation
    g_downs = C.downbeats('grandma')
    B.kids(g_downs[-1] + 0.2, g_downs[-1] + 2.4, 'cheer', level=0.75, pan=S.pan(P['kids'][2]), voices=6, seed=3)
    # the car: a horn as it pulls in, a boing for each kid hopping in, the engine for the whole drive
    B.horn(M['horn'] + 0.1, beeps=2, pan=S.pan(P['park']), gain=1.0)
    rev = lambda tt: np.clip((tt - M['sing']) / 2.0, 0, 1) * 0.5 * (tt < M['go'] + 0.8)
    t0 = M['horn']
    while t0 < M['door']:                                           # in pieces, so it follows the car across
        t1 = min(t0 + 4.0, M['door'])
        B.engine(t0 - 0.4 * (t0 > M['horn']), t1 + 0.4, pan=S.pan(car_p(S, (t0 + t1) / 2)), gain=0.35, rev=rev)
        t0 = t1
    for i, th in enumerate(hops()):
        B.boing(th, pan=S.pan(car_p(S, th)), gain=0.6, high=0.9 + 0.12 * i)
    # sleigh bells on every beat of everybody's verse; a whoosh of wind over the river
    for tb in C.beat_times('v3') + C.beat_times('go')[:3]:
        B.hit('sleigh', tb, 70, gain=0.22, pan=S.pan(car_p(S, tb)))
    B.wind(M['river'] - 1.0, M['all'], level=0.25, pan=S.pan(S.mid))
    # the arrival: two beeps, a breath of stillness, her door opens on a swell and a cheer
    B.horn(M['door'] - 0.55, beeps=2, pan=S.pan(P['gran']), gain=0.9)
    B.hit('cymbal swell', M['open'] - 1.0, 96, gain=0.35)
    B.hit('crash', M['open'], 112, gain=0.45, pan=S.pan(P['gran']))
    B.play('glock', note('C6'), M['open'], 0.6, 90, pan=S.pan(P['gran']), gain=0.4)
    B.kids(M['open'] + 0.1, M['open'] + 2.6, 'cheer', level=0.8, pan=S.pan(P['gran']), voices=7, seed=8)
    B.hit('cymbal swell', M['button'] - 1.4, 96, gain=0.35)
    B.hit('crash', M['button'], 118, gain=0.5)
    B.effects([(0, -3), (M['open'], -2), (M['button'], -4)])
    B.finish()
