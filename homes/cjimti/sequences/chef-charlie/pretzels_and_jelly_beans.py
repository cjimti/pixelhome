"""Pretzels and Jelly Beans: Snoopy twists the pretzels, Woodstock helps with the jelly beans.

The backyard comes up at evening (a deep blue sky, the lawn along the wings, party bulbs swaying on every run) and the
brushes count in. Snoopy pops up on the porch with the ping-pong table to his strut, the table's green slab
drawing itself out, and sets a bowl down on every bar with a clink. Then the pretzels, to a jazz waltz of its own:
the run he is working on twists into a braid, two brown strands crossing back and forth on the beat with salt
sparkling on them, a new run every two bars until the whole roofline is pretzel, and on every bar one flies from the
twist into the bowls. Woodstock flies in from the free end of Right to his twitter, chirping, and wants
to help: he takes a pretzel twice his size and wobbles off with it along Right, lower and lower, and drops it with a
thud and a trombone's fall. Third time round he zips about the porch and comes back with the jar of jelly beans.
The main title, in two: the bird flies the length of the house and back, pouring, and every note of the tune drops a
bean of the next colour where he is, so the roofline fills with a scatter of red, orange, yellow, green, blue,
violet, pink and white. Then the title swings and the beans sort themselves into rainbow stripes that march a band
on every beat, the runs flashing. A breath: the house dims, the bird takes one bean for himself (a gulp). The
feast's tune plays out: rainbow stripes and pretzel braids on alternate runs, confetti on every bar, a sweep from the
free end of Right and the last chord.

compose() lays out the music (pixelhome/chef_charlie.py); beans() lists every jelly bean (when it lands, where, its
colour) and bird_p() is the bird's flight, both shared by render() and score()."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, perc, hexc
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, WHITE, AMBER, GOLD, PRETZEL, JELLY, BIRD, TABLE,
                                    WARM)

CODE = 'CC07'
TITLE = 'Pretzels and Jelly Beans'
KIND = 'show'
DESCRIPTION = ('Snoopy twists pretzels until the whole roof is braided. Woodstock helps, drops a pretzel twice his size, '
    'then pours a rainbow of jelly beans across the house and sorts them into stripes.')
VOICEOVER = 'Snoopy twists the pretzels, and Woodstock pours the jelly beans.'

SALT = hexc('#f0f4ff')

# the pretzels: a jazz waltz full of turns, the tune twisting back on itself; original to this scene
TWIST = dict(id='twist', meter=3, bpm=138, swing=True, name='Twisting the pretzels: a jazz waltz, F major, 12 bars',
             melody=[(0, 1, 'C5'), (1, .5, 'A4'), (1.5, .5, 'Bb4'), (2, 1, 'C5'),
                     (3, 1, 'D5'), (4, .5, 'Bb4'), (4.5, .5, 'A4'), (5, 1, 'G4'),
                     (6, .5, 'E4'), (6.5, .5, 'G4'), (7, .5, 'Bb4'), (7.5, .5, 'D5'), (8, 1, 'C5'),
                     (9, 2, 'A4'), (11, 1, 'F4'),
                     (12, 1, 'F4'), (13, .5, 'A4'), (13.5, .5, 'G4'), (14, 1, 'F4'),
                     (15, 1, 'B4'), (16, .5, 'D5'), (16.5, .5, 'C5'), (17, 1, 'B4'),
                     (18, .5, 'Bb4'), (18.5, .5, 'A4'), (19, .5, 'G4'), (19.5, .5, 'F4'), (20, 1, 'E4'),
                     (21, 2, 'G4'), (23, 1, 'C5'),
                     (24, 1, 'E5'), (25, .5, 'C5'), (25.5, .5, 'D5'), (26, 1, 'E5'),
                     (27, 1, 'D5'), (28, .5, 'F#4'), (28.5, .5, 'A4'), (29, 1, 'C5'),
                     (30, 1, 'Bb4'), (31, 1, 'G4'), (32, 1, 'E4'),
                     (33, 3, 'F4')],
             chords=[(0, 3, 'Fmaj7'), (3, 3, 'Gm7'), (6, 3, 'C7'), (9, 3, 'Fmaj7'), (12, 3, 'Dm7'), (15, 3, 'G7'),
                     (18, 3, 'Gm7'), (21, 3, 'C7'), (24, 3, 'Am7'), (27, 3, 'D7'), (30, 2, 'Gm7'), (32, 1, 'C7'),
                     (33, 3, 'F6')])

ORDER = ('Porch Front', 'Left', 'Right', 'Porch Left', 'Porch Right', 'Side')     # the runs, as they get twisted


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the backyard comes up
    C.mark('count')
    C.play('beagle', style='brushes', bars=(0, 1), tune=False, tag='count')
    C.mark('set')
    C.play('beagle', style='swing', bars=(0, 4), tag='set')         # the table, a bowl a bar
    C.mark('twist')
    C.play(TWIST, style='waltz', tag='twist')                       # a run twisted every two bars
    C.mark('bird')
    C.play('bird', style='two', bars=(0, 4), tag='bird')            # he flies in
    C.mark('carry')
    C.play('bird', style='swing', bars=(0, 4), tag='carry')         # a pretzel twice his size; he drops it
    C.mark('zip')
    C.play('bird', style='drive', bars=(0, 4), tag='zip')           # he zips off for the jelly beans
    C.mark('beans')
    C.play('title', style='two', bpm=132, tag='beans')              # poured the length of the house
    C.mark('sort')
    C.play('title', style='swing', tag='sort')                      # rainbow stripes march
    C.mark('gulp')
    C.rest(1.0)                                                     # one for the bird
    C.mark('finale')
    C.play('feast', style='swing', bpm=168, tag='finale')
    C.mark('button')
    C.button('D6', bpm=168, beats=2)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
_BEANS = []


def bird_p(S, t):
    """The bird: in from the free end of Right to the table; off along Right with the pretzel, sagging; zipping round
    the porch; the length of the house and back, pouring; riding the stripes; fluttering over the table."""
    mid = S.mid
    if t < M['carry']:
        u = float(smoothstep(M['bird'], M['carry'] - 1.0, t))
        return S.L + 60 + (mid + 80 - S.L - 60) * u + 25 * np.sin(2 * np.pi * 1.4 * t) * (u < 1)
    if t < M['zip']:
        u = float(smoothstep(M['carry'], M['zip'] - 1.2, t))
        return mid + 80 + (S.at('Right', 0.4) - mid - 80) * u + 6 * np.sin(2 * np.pi * 3 * t)
    if t < M['beans']:
        u = (t - M['zip']) / (M['beans'] - M['zip'])
        return S.at('Right', 0.4) + (mid + 80 - S.at('Right', 0.4)) * u + 140 * np.sin(2 * np.pi * 1.5 * (t - M['zip']))
    if t < M['sort']:
        u = (t - M['beans']) / (M['sort'] - M['beans'])
        return 1500 + 1000 * np.sin(2 * np.pi * u)
    if t < M['finale']:
        return mid + 80 + 40 * abs(np.sin(np.pi * (t - M['sort']) * 152 / 60))
    return mid + 90 + 60 * np.sin(2 * np.pi * 0.6 * (t - M['finale']))


def beans(S):
    """Every jelly bean: (lands at, path distance, colour index). Each note of the title drops one where the bird is,
    and each beat of the bass one more, the colours in rainbow turn."""
    if _BEANS:
        return _BEANS
    rng = np.random.default_rng(77)
    times = sorted({round(n[0], 4) for n in C.tunes('beans')} | set(C.times('bass', 'beans')))
    for i, t in enumerate(times):
        _BEANS.append((t + 0.25, float(np.clip(bird_p(S, t) + rng.uniform(-35, 35), 0, S.L)), i % len(JELLY)))
    return _BEANS


def braid(S, phase, period=100.0, lv=1.0, mask=None, t=0.0, travel=0.15):
    """Pretzel: two brown strands crossing back and forth (they twist one way and back on each unit of phase), with
    salt sparkling on them -> (N,3) PWM."""
    tri = 1 - np.abs(2 * ((phase / 2.0) % 1.0) - 1)
    off = 0.35 * (2 * tri - 1)
    u1 = (S.d / period - off - travel * phase) % 1.0
    u2 = (S.d / period + off - travel * phase + 0.5) % 1.0
    s = np.maximum(smoothstep(0.16, 0.1, np.abs(u1 - 0.5)), smoothstep(0.16, 0.1, np.abs(u2 - 0.5)))
    salt = (np.sin(S.d * 1.37) > 0.9) * (0.5 + 0.5 * np.sin(23 * t + S.d * 3.1)) * s
    m = 1.0 if mask is None else mask
    return light(PRETZEL, lv * s * m) + light(SALT, 0.6 * lv * salt * m)


def toss(S, t, hits, col, lv=1.0):
    """Things flying in an arc: [(t0, from, to, seconds)] a bright slug widest at the top of its arc, a flash where it
    lands."""
    out = np.zeros((S.N, 3))
    for t0, a, b, dur in hits:
        x = t - t0
        if x < 0 or x > dur + 0.4:
            continue
        if x <= dur:
            u = x / dur
            q = a + (b - a) * u
            arc = 4 * u * (1 - u)
            out += light(col, lv * (0.8 + 0.2 * arc) * np.exp(-((S.d - q) / (6 + 10 * arc)) ** 2))
            out += light(SALT, 0.5 * lv * np.exp(-((S.d - q) / 4) ** 2))
        else:
            out += light(GOLD, 0.7 * lv * np.exp(-(x - dur) / 0.12) * S.blob(b, 20))
    return out


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The piano plays the roofline: each note of the tune sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def render(G, seed=7):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    t_count = C.beat_times('count')
    set_downs = C.downbeats('set')
    twist_downs = C.downbeats('twist')
    twist_beats = C.beat_times('twist')
    bird_downs = C.downbeats('bird') + C.downbeats('carry') + C.downbeats('zip')
    zip_beats = C.beat_times('zip')
    sort_beats = C.beat_times('sort')
    sort_downs = C.downbeats('sort')
    fin_beats = C.beat_times('finale')
    fin_downs = C.downbeats('finale')
    tunes = {g: C.tunes(g) for g in ('set', 'twist', 'bird', 'carry', 'zip', 'beans', 'sort', 'finale')}
    bn = beans(S)
    bt = np.array([b[0] for b in bn])
    Wb = perc(np.exp(-((d[:, None] - np.array([b[1] for b in bn])[None, :]) / 5.0) ** 2))
    cols = np.array([JELLY[b[2]] for b in bn])
    twist_at = {r: twist_downs[2 * i] for i, r in enumerate(ORDER)}
    tosses = [(tb + 0.1, S.at(ORDER[min(i // 2, 5)], 0.5), mid + (-30 if i % 2 else 30), 0.8)
              for i, tb in enumerate(twist_downs)]
    drop_t = M['zip'] - 1.0
    drop_p = S.at('Right', 0.4)
    lv_yard = [(0, 0.0), (2.0, 1.0), (M['beans'], 1.0), (M['beans'] + 1, 0.6), (M['gulp'], 0.6),
               (M['gulp'] + 0.3, 0.3), (M['finale'], 0.3), (M['finale'] + 0.5, 0.7), (D, 0.7)]

    for f in range(F):
        t = f * DT
        b = pulse(t, beats, 0.15)
        fr = S.backyard(t, float(keys(t, lv_yard)), bulbs=0.8 + 0.4 * b)

        for tc in t_count:
            fr += S.wave(t, tc, AMBER, 0.55, speed=700, width=90, decay=0.35)

        # setting the table: a flash as he pops up, a warm ripple and a run flash for each bowl
        if M['set'] <= t < M['twist'] + 1:
            a = t - M['set']
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S.run['Porch Front'])
            for tb in set_downs:
                if tb <= t < tb + 2:
                    fr += S.wave(t, tb, WARM, 0.8, speed=900, width=60, decay=0.6)
            fr += S.run_flash(t, C.beat_times('set'), cols=(TABLE, WARM), runs=('Left', 'Right', 'Porch Left', 'Porch Right'),
                              lv=0.45, decay=0.25)
            fr += keyboard(S, t, tunes['set'], WHITE, 0.55)

        # the pretzels: a run twisted every two bars (a white flash as it starts), the braid twisting on the beat
        if t >= M['twist']:
            ph = (t - M['twist']) / (60 / 138)
            if t >= M['finale']:
                ph = (t - M['finale']) / (60 / 168) * 0.5
            mask = np.zeros(S.N)
            for r, t0 in twist_at.items():
                if t >= t0:
                    mask = np.maximum(mask, S.run[r] * float(smoothstep(t0, t0 + 0.5, t)))
                    if t < t0 + 0.6:
                        fr += light(SALT, 0.8 * np.exp(-(t - t0) / 0.15) * S.run[r])
            dim = float(keys(t, [(M['twist'], 1.0), (M['bird'], 1.0), (M['bird'] + 1, 0.55), (M['beans'], 0.55), (M['beans'] + 2, 0.35), (M['sort'], 0.3),
                                 (M['sort'] + 3, 0.0), (M['finale'], 0.0), (M['finale'] + 0.4, 1.0), (D, 1.0)]))
            if t >= M['finale']:
                mask = (S.run['Left'] | S.run['Porch Front'] | S.run['Side']).astype(float)
            if dim > 0:
                fr = fr * (1 - 0.6 * dim * mask[:, None]) + braid(S, ph, lv=0.9 * dim, mask=mask, t=t)
            if t < M['bird']:
                fr += toss(S, t, tosses, PRETZEL)
                fr += keyboard(S, t, tunes['twist'], SALT, 0.45)

        # the bird: flies in, wobbles off with a pretzel and drops it, zips about; a yellow trail behind him
        if M['bird'] - 0.2 <= t < M['beans']:
            bp = bird_p(S, t)
            for tb in bird_downs:
                if tb <= t < tb + 2:
                    fr += S.wave(t, tb, BIRD, 0.9, origin=bird_p(S, tb), speed=800, width=50, decay=0.6)
            fr += keyboard(S, t, tunes['bird'] + tunes['carry'] + tunes['zip'], BIRD, 0.5, width=22)
            if M['carry'] <= t < drop_t:                           # the pretzel, sagging as he struggles
                sag = float(smoothstep(M['carry'], drop_t, t))
                fr += light(PRETZEL, (1.0 - 0.4 * sag) * S.blob(bp - 14, 9))
            a = t - drop_t
            if 0 <= a < 1.5:
                fr += S.wave(t, drop_t, PRETZEL, 1.0, origin=drop_p, speed=1200, width=60, decay=0.6)
                fr += light(PRETZEL, np.exp(-a / 0.6) * S.blob(drop_p, 14))
            if M['zip'] <= t:
                fr += S.run_flash(t, zip_beats, cols=(BIRD, WHITE), runs=('Porch Left', 'Porch Front', 'Porch Right'),
                                  lv=0.4, decay=0.15)

        # the beans: dropped where the bird is, one a note, and they stay; then they sort into marching stripes
        on = (t >= bt).astype(float)
        if on.any() and t < M['finale']:
            keep = float(keys(t, [(M['sort'], 1.0), (M['sort'] + 3, 0.0)]))
            if keep > 0:
                fall = np.exp(-np.maximum(t - bt, 0) / 0.15) * on
                lvl = (0.9 + 0.6 * fall) * on * keep
                fr = fr * (1 - 0.6 * np.clip(Wb @ on, 0, 1)[:, None] * keep) + (Wb * lvl[None, :]) @ cols
        if M['beans'] <= t < M['sort']:
            bp = bird_p(S, t)
            fr += light(BIRD, 0.4 * S.blob(bp, 60))
        if M['sort'] <= t < M['gulp'] + 0.4:
            k = np.searchsorted(sort_beats, t)
            step = k + (float(smoothstep(0, 0.2, t - sort_beats[k - 1])) if k > 0 else 0)
            rise = float(smoothstep(M['sort'], M['sort'] + 3, t)) * float(smoothstep(M['gulp'] + 0.4, M['gulp'], t))
            st = S.stripes(step, JELLY, lv=0.8 * rise, period=36.0)
            fr = fr * (1 - 0.7 * rise) + st
            fr += S.run_flash(t, sort_downs, cols=(WHITE,), runs=('Left', 'Right', 'Porch Front'), lv=0.5, decay=0.3)
            fr += keyboard(S, t, tunes['sort'], WHITE, 0.5)
        if M['gulp'] <= t < M['finale']:
            a = t - M['gulp']
            bp = bird_p(S, t)
            fr += light(JELLY[0], float(smoothstep(0.1, 0.3, a)) * float(smoothstep(0.75, 0.55, a)) * S.blob(bp + 12, 6))

        # the finale: rainbow stripes and pretzel braids on alternate runs, confetti on every bar, the sweep, the button
        if t >= M['finale']:
            ph = (t - M['finale']) / (60 / 168)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.1, t))
            other = (S.run['Porch Left'] | S.run['Porch Right'] | S.run['Right']).astype(float)
            fr = fr * (1 - 0.6 * other[:, None]) + S.stripes(np.floor(ph) + float(smoothstep(0, 0.2, ph % 1)), JELLY,
                                                             lv=0.85 * fade, period=36.0, mask=other)
            fr += S.confetti([(tb, 0.9, mid) for tb in fin_downs], t, colors=JELLY, n=28, reach=1.4, seed=7)
            fr += S.run_flash(t, fin_beats, cols=(WHITE, BIRD), lv=0.35 * fade, decay=0.15)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.6)
            fr += S.sweep(t, fin_downs[6], 2.0, WHITE, 0.8, frm='right', width=90, trail=0.5)
            bb = t - M['button']
            if bb >= 0:
                fr += light(GOLD, np.exp(-bb / 0.5) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-bb / 0.12) * np.ones(S.N))

        # the table on the porch (its bowls filling), Snoopy beside it, the bird
        if t >= M['set'] - 0.1:
            grow = float(smoothstep(M['set'], M['set'] + 1.2, t))
            half = max(1, int(round(12 * grow)))
            food = []
            for i, tb in enumerate(set_downs):
                if t >= tb + 0.3:
                    o = (-9, 9, -4, 4)[i]
                    if t >= M['sort'] and i >= 2:
                        food.append((o, JELLY[(i + int(t * 3)) % len(JELLY)]))
                    elif t >= M['twist'] + 1 and i < 2:
                        food.append((o, PRETZEL))
                    else:
                        food.append((o, WHITE))
            fr = S.table(fr, mid, 0.9, half=half, food=[x for x in food if abs(x[0]) <= half])
            jump = 0.3 * pulse(t, twist_downs, 0.2) if M['twist'] <= t < M['bird'] else 0.0
            facing = 1 if t < M['finale'] else (1 if int((t - M['finale']) / 1.43) % 2 else -1)
            fr = S.beagle(fr, mid - 80 + 10 * jump, min(1.2, 0.85 + 0.25 * b + jump), facing=facing, t=t, chef=True)
        if t >= M['bird'] - 0.2:
            bp = bird_p(S, t)
            facing = -1 if t < M['carry'] else 1
            if M['zip'] <= t < M['finale']:
                facing = 1 if np.cos(2 * np.pi * 1.5 * (t - M['zip'])) > 0 else -1
            if M['beans'] <= t < M['sort']:
                facing = 1 if np.cos(2 * np.pi * (t - M['beans']) / (M['sort'] - M['beans'])) > 0 else -1
            fr = S.bird(fr, bp, 1.0, t=t, facing=facing)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    mid = S.mid
    B = Band(M_, level=1.0)
    parts = {
        ('set', 'tune'): [('piano', 0, 6, 0.85)],
        ('twist', 'tune'): [('piano', 0, 6, 0.85), ('marimba', 0, -12, 0.3)],
        ('twist', 'comp'): [('piano', 0, -10, 0.45)],
        ('bird', 'tune'): [('xylo', 0, 0, 0.6), ('piano', 0, -6, 0.5)],
        ('carry', 'tune'): [('buzz trombone', -12, 0, 0.6), ('piano', 0, -8, 0.45)],
        ('zip', 'tune'): [('xylo', 0, 6, 0.65), ('piano', 0, -2, 0.55)],
        ('beans', 'tune'): [('piano', 0, 6, 0.85), ('glock', 12, -20, 0.15)],
        ('sort', 'tune'): [('piano', 0, 10, 0.85), ('xylo', 12, -10, 0.25)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -2, 0.5), ('xylo', 12, -12, 0.2)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4)],
    }
    B.perform(C.events, parts)
    for m in (65, 69, 72, 76):
        B.play('choir', m, 0.2, 1.9, 48, gain=0.3)
    # the table: he pops up with it, a woof, its legs unfolding; a clink for each bowl set down
    B.boing(M['set'], pan=S.pan(mid), gain=0.8)
    B.woof(M['set'] + 0.3, pan=S.pan(mid))
    for k in range(3):
        B.hit('wood', M['set'] + 0.5 + 0.15 * k, 100, gain=0.5, pan=S.pan(mid))
    for i, tb in enumerate(C.downbeats('set')):
        B.clink(tb + 0.3, pan=S.pan(mid + (-45, 45, -20, 20)[i]), gain=0.8, pitch=i)
    # the pretzels: a guiro twist on every run, a little slide for each one tossed, a tap as it lands in a bowl
    downs = C.downbeats('twist')
    for i, tb in enumerate(downs):
        p0 = S.at(ORDER[min(i // 2, 5)], 0.5)
        if i % 2 == 0:
            B.hit('guiro', tb, 100, gain=0.6, pan=S.pan(p0))
        B.slide(tb + 0.1, 0.5, up=True, pan=S.pan(p0), gain=0.25, lo=600, hi=1200)
        B.hit('woodblock', tb + 0.9, 90, gain=0.4, pan=S.pan(mid))
    # the bird: chirps on every bar; the strain of the pretzel (a wobbling slide), the drop and the fall
    for k, tt in enumerate(C.downbeats('bird') + C.downbeats('carry') + C.downbeats('zip')):
        B.chirp(tt + 0.1, n=3 + k % 3, pan=S.pan(bird_p(S, tt)), gain=0.9, seed=k)
    B.slide(M['carry'] + 0.5, 2.0, up=True, pan=S.pan(bird_p(S, M['carry'] + 1)), gain=0.3, lo=900, hi=1100)
    drop = M['zip'] - 1.0
    B.slide(drop - 0.5, 0.5, up=False, pan=S.pan(S.at('Right', 0.4)), gain=0.6, lo=500, hi=1300)
    B.thud(drop, pan=S.pan(S.at('Right', 0.4)), gain=0.6)
    B.fall(drop + 0.15, pan=S.pan(S.at('Right', 0.4)), gain=0.5)
    B.whoosh(M['zip'], 0.4, up=True, pan=S.pan(mid), gain=0.4)
    B.hit('maraca', M['beans'] - 0.3, 100, gain=0.5, pan=S.pan(mid))
    # the beans: each one a glockenspiel tinkle in the key, where it lands
    tones = [77, 81, 84, 86, 89, 91, 93, 96]
    for t0, p, ci in beans(S):
        B.play('glock', tones[ci] - 12, t0, 0.3, 80, pan=S.pan(p), gain=0.4)
    B.effects([(0, -3), (M['carry'], 0), (M['beans'], -3), (M['finale'], -2)])
    # the sort: a ratchet as they fall into line; the gulp
    B.hit('ratchet', M['sort'], 90, gain=0.35)
    B.slide(M['gulp'] + 0.4, 0.4, up=False, pan=S.pan(bird_p(S, M['gulp'])), gain=0.5, lo=600, hi=1500)
    B.chirp(M['gulp'] + 0.85, n=2, pan=S.pan(bird_p(S, M['gulp'])), gain=1.0, seed=9)
    # the finale: a cheer, confetti on every bar, the sweep and the button
    B.kids(M['finale'] + 0.1, M['finale'] + 1.5, 'cheer', level=0.35, voices=5, seed=5)
    B.hit('crash', M['finale'], 115, gain=0.45)
    for tb in C.downbeats('finale'):
        B.hit('tambourine', tb, 100, gain=0.35, pan=S.pan(mid))
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5,
             pan=lambda tt: 0.8 - 1.6 * (tt - C.downbeats('finale')[6]) / 2.0)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.chirp(M['button'] + 0.7, n=4, pan=S.pan(mid + 90), gain=1.0, seed=11)
    B.finish()
