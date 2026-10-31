"""Buttered Toast: Snoopy runs the toaster like a factory line, and the toast flies.

The kitchen comes up warm (gold walls, the checked floor along the wings, the stove glowing over the porch) and the
brushes count in. Snoopy pops up at the toaster in his chef's hat and struts out along Right to his own theme, the
floor tiles marching under him on every beat, and comes back with the loaf. The production line starts on a boogie
riff: slices of bread march in from both ends of the house to the toaster, a step on every beat of the bass, each
one clunking in. Stop-time: the coils heat, the porch glowing redder on every hit and the heat pulsing out along the
roof; on the third hit the toaster jumps and nothing comes out (a false pop), then a held breath in the near dark.
The first pop throws two slices out to the wings. The main title swings and every bar pops two more, Snoopy
flicking butter after each one on the backbeat; the tempo goes up and a slice pops on every beat; then the feast's
tune, double time, and toast on every eighth, flying the length of the house and landing anywhere while butter
zigzags race the runs. Every slice that lands stays where it fell, so the roofline fills with toast. Then it all
stops: one more slice in, the coils tick... and a last, enormous pop throws gold out across the whole house. The
beagle's strut comes back as the finale, the toast on every run glowing to the beat, a sweep from the free end of
Right, and the last chord.

compose() lays out the music (pixelhome/chef_charlie.py); slices() lists every slice of toast (when it pops, where it
lands, when it is buttered) from the same chart, so render() and score() share it."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys, hexc
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, WHITE, YELLOW, AMBER, ORANGE, RED, GOLD, TOAST,
                                    BUTTER, BEAGLE)

CODE = 'CC05'
TITLE = 'Buttered Toast'
KIND = 'show'
DESCRIPTION = ('Snoopy runs the toaster like a factory line. Bread marches in, the coils glow, and toast flies out '
    'across the whole house, faster and faster, buttered on the fly, until the roof is covered.')
VOICEOVER = "Snoopy puts on his chef's hat and fires up the toaster."

BREAD = hexc('#fff0d0')
SILVER = hexc('#c8d8ff')

# the toaster's own riff: a boogie figure that climbs, original to this scene
TOASTER = dict(id='toaster', meter=4, bpm=132, swing=True, name='The toaster: a boogie riff, C',
               melody=[(0, .5, 'C4'), (.5, .5, 'E4'), (1, .5, 'G4'), (1.5, .5, 'A4'), (2, .5, 'Bb4'), (2.5, .5, 'A4'),
                       (3, .5, 'G4'), (3.5, .5, 'E4'),
                       (4, .5, 'F4'), (4.5, .5, 'A4'), (5, .5, 'C5'), (5.5, .5, 'D5'), (6, .5, 'Eb5'), (6.5, .5, 'D5'),
                       (7, 1, 'C5'),
                       (8, .5, 'G4'), (8.5, .5, 'Bb4'), (9, 1, 'C5'), (10, .5, 'Eb4'), (10.5, .5, 'E4'), (11, 1, 'G4'),
                       (12, .5, 'D5'), (12.5, .5, 'B4'), (13, .5, 'G4'), (13.5, .5, 'F4'), (14, 1, 'D4'),
                       (15, .5, 'F#4'), (15.5, .5, 'G4')],
               chords=[(0, 4, 'C7'), (4, 4, 'F7'), (8, 4, 'C7'), (12, 4, 'G7')])


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the kitchen comes up
    C.mark('count')
    C.play('beagle', style='brushes', bars=(0, 1), tune=False, tag='count')
    C.mark('strut')
    C.play('beagle', style='swing', tag='strut')                    # out along Right and back with the loaf
    C.mark('load')
    C.play(TOASTER, style='walk', tag='load')                       # bread marches in from both ends
    C.mark('heat')
    C.play(TOASTER, style='stop', tag='heat')                       # the coils heat; a false pop on hit three
    C.mark('wait')
    C.rest(1.0)                                                     # the held breath
    C.mark('line')
    C.play('title', style='swing', tag='line')                      # two slices a bar, butter on the backbeat
    C.mark('faster')
    C.play('title', style='drive', bpm=176, tag='faster')           # a slice on every beat
    C.mark('storm')
    C.play('feast', style='drive', tag='storm')                     # toast on every eighth
    C.mark('hold')
    C.rest(1.5)                                                     # it all stops; one more slice in
    C.mark('finale')
    C.play('beagle', style='swing', bpm=132, tag='finale')          # the last, enormous pop, and the strut
    C.mark('button')
    C.button('C6', bpm=132, beats=2)
    C.rest(2.2)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks
_SL = []


def slices(S):
    """Every slice of toast: (pop time, lands at path distance, flight seconds, buttered at). The first pop throws
    two to the wings; the title pops two a bar; the faster title one a beat; the storm one every eighth, anywhere."""
    if _SL:
        return _SL
    rng = np.random.default_rng(55)
    out = []
    for i, tb in enumerate(C.downbeats('line')):
        beat = 60 / 152
        a = rng.uniform(0.15, 0.85)
        b = rng.uniform(0.15, 0.85)
        out.append((tb, S.at('Left', a) if i % 2 == 0 else S.at('Porch Left', b), 1.2, tb + 2.5 * beat))
        out.append((tb, S.at('Right', b) if i % 2 == 0 else S.at('Porch Right', a), 1.2, tb + 3.5 * beat))
    targets = ('Left', 'Right', 'Porch Left', 'Porch Right', 'Porch Front')
    for i, tb in enumerate(C.beat_times('faster')):
        p = S.at(targets[i % 5], rng.uniform(0.05, 0.95))
        out.append((tb, p, 0.95, tb + 1.15))
    beat = 60 / 184
    for i, tb in enumerate(C.beat_times('storm')):
        for h in (0, 0.5):
            p = rng.uniform(40, S.L - 20)
            out.append((tb + h * beat, p, 0.7 + 0.5 * abs(p - S.mid) / S.L, tb + h * beat + 1.2))
    _SL.extend(out)
    return _SL


def beagle_p(S, t):
    """Snoopy: pops up at the toaster, struts out along Right and back a step a beat, minds the toaster, darts
    about in the storm, dances by it at the end."""
    toaster = S.mid
    far = S.at('Right', 0.72)
    sb = np.array(C.beat_times('strut'))
    if t < M['load']:
        k = np.searchsorted(sb, t) - 1
        if k < 0:
            return toaster + 18
        frac = float(smoothstep(0.0, 0.55, (t - sb[k]) / (60 / 120)))
        u = (k + frac) / 16.0
        out = 1 - abs(1 - u) if u <= 2 else 0.0
        return toaster + 18 + (far - toaster - 18) * min(1.0, out)
    if t < M['storm']:
        return toaster + 18
    if t < M['hold']:
        return toaster + 18 + 150 * np.sin(2 * np.pi * 0.9 * (t - M['storm']))
    return toaster + 18


def flying(S, t, sl, lv=1.0):
    """The toast in the air: a white flash at the toaster, a golden slice arcing out to where it lands (widest at the
    top of the arc), crumbs behind it, a little gold splash where it lands."""
    out = np.zeros((S.N, 3))
    d = S.d
    for t0, p1, dur, _ in sl:
        a = t - t0
        if a < 0 or a > dur + 0.4:
            continue
        if a < 0.3:
            out += light(WHITE, lv * np.exp(-a / 0.1) * S.blob(S.mid, 45))
        if a <= dur:
            u = a / dur
            q = S.mid + (p1 - S.mid) * u
            arc = 4 * u * (1 - u)
            w = 10 + 16 * arc
            out += light(TOAST, lv * (0.9 + 0.3 * arc) * smoothstep(q - w, q - w + 5, d) * smoothstep(q + w, q + w - 5, d))
            out += light(WHITE, 0.6 * lv * np.exp(-((d - q) / 5.0) ** 2))
            dr = 1 if p1 > S.mid else -1
            tail = (d - q) * -dr
            out += light(GOLD, 0.5 * lv * (tail > 0) * np.exp(-np.maximum(tail, 0) / 60) * (np.abs(d - q) < abs(p1 - S.mid)) *
                         (0.5 + 0.5 * np.sin(0.5 * d - 40 * t)))
        else:
            out += light(GOLD, 0.7 * lv * np.exp(-(a - dur) / 0.12) * S.blob(p1, 22))
    return out


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The piano plays the roofline: each note of the tune sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


def kitchen(S, t, lv, shift=0.0, stove=1.0):
    """The kitchen with its checked floor marching along the wings (shift in tiles, toward the porch)."""
    tile = (np.floor(np.abs(S.d - S.mid) / 18.0 - shift) % 2).astype(float)
    floor = S.wings | S.run['Side']
    fr = light(GOLD, 0.3 * lv * (1 - 0.6 * floor))
    fr += floor[:, None] * (light(RED, 0.55 * lv * tile) + light(WHITE, 0.2 * lv * (1 - tile)))
    fr += light(ORANGE, 0.7 * lv * stove * S.blob(S.mid, 110) * (0.85 + 0.15 * np.sin(7 * t + S.d * 0.05)))
    return fr


def render(G, seed=5):
    S = Stage(G)
    d, mid = S.d, S.mid
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    sl = slices(S)
    land = np.array([s[0] + s[2] for s in sl])
    butt = np.array([s[3] for s in sl])
    pops = sorted({s[0] for s in sl if s[0] < M['storm']})
    W = np.exp(-((d[:, None] - np.array([s[1] for s in sl])[None, :]) / 6.0) ** 2)    # each slice where it lies
    beats = np.array(C.beat_times())
    t_count = C.beat_times('count')
    strut_beats = C.beat_times('strut')
    strut_downs = C.downbeats('strut')
    load_beats = np.array(C.beat_times('load'))
    heat_hits = C.times('hit', 'heat')
    line_beats = C.beat_times('line')
    faster_beats = C.beat_times('faster')
    faster_downs = C.downbeats('faster')
    storm_beats = C.beat_times('storm')
    storm_downs = C.downbeats('storm')
    fin_beats = C.beat_times('finale')
    fin_downs = C.downbeats('finale')
    tunes = {g: C.tunes(g) for g in ('strut', 'load', 'heat', 'line', 'faster', 'storm', 'finale')}
    lv_kit = [(0, 0.0), (2.0, 1.0), (M['heat'], 1.0), (M['wait'], 0.55), (M['wait'] + 0.2, 0.3),
              (M['line'], 0.3), (M['line'] + 0.1, 0.8), (M['hold'], 0.8), (M['hold'] + 0.3, 0.35),
              (M['finale'], 0.35), (M['finale'] + 0.5, 0.75), (M['end'], 0.75)]

    for f in range(F):
        t = f * DT
        # the floor marches a tile a beat while the line runs
        nb = np.searchsorted(beats, t)
        shift = 0.0
        if M['strut'] <= t < M['heat'] or M['line'] <= t < M['hold'] or t >= M['finale']:
            prev = beats[max(nb - 1, 0)]
            shift = nb + float(smoothstep(0, 0.25, t - prev))
        heat = float(keys(t, [(0, 0.2), (M['heat'], 0.25), (M['wait'], 1.0), (M['line'] + 0.3, 0.6),
                              (M['hold'], 0.6), (M['finale'], 1.0), (M['finale'] + 1, 0.4)]))
        fr = kitchen(S, t, float(keys(t, lv_kit)), shift, stove=0.6 + 0.6 * heat)

        for tc in t_count:                                         # the count: four warm washes out of the porch
            fr += S.wave(t, tc, AMBER, 0.55, speed=700, width=90, decay=0.35)

        # the strut: paws flash on every beat, a ripple out along the roof, the tune sparks, runs flash on the bar
        if M['strut'] <= t < M['load'] + 0.5:
            fade = float(smoothstep(M['load'] + 0.5, M['load'], t))
            a = t - M['strut']
            if a < 0.6:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.15) * S.run['Porch Front'])
            for tb in strut_beats:
                if tb <= t < tb + 1.5:
                    fr += S.wave(t, tb, GOLD, 0.6 * fade, origin=beagle_p(S, tb), speed=600, width=45, decay=0.4)
            fr += S.run_flash(t, strut_downs, cols=(ORANGE, GOLD), runs=('Right', 'Left', 'Porch Right', 'Porch Left'),
                              lv=0.7 * fade, decay=0.4)
            fr += keyboard(S, t, tunes['strut'], WHITE, 0.6 * fade)
            if t >= strut_downs[4]:                                 # the loaf he brings back
                fr += light(BREAD, 0.8 * fade * S.blob(beagle_p(S, t) - 26, 10))

        # the production line: bread marches in from both ends, a step on every beat, clunking into the toaster
        if M['load'] <= t < M['heat'] + 0.4:
            fade = float(smoothstep(M['heat'] + 0.4, M['heat'], t))
            k = np.searchsorted(load_beats, t)
            step = k + (float(smoothstep(0, 0.22, t - load_beats[k - 1])) if k > 0 else 0)
            dist = np.abs(d - mid) - 24
            u = (dist / 60.0 + step / 3.0) % 1.0
            slice_ = smoothstep(0.62, 0.7, u) * smoothstep(0.98, 0.9, u) * (dist > 0)
            ramp = float(smoothstep(M['load'], M['load'] + 1.5, t))
            fr = fr * (1 - 0.6 * slice_[:, None] * ramp * fade) + light(BREAD, 0.85 * ramp * fade * slice_)
            fr += light(WHITE, 0.7 * pulse(t, load_beats, 0.12) * S.blob(mid, 26) * fade)
            fr += keyboard(S, t, tunes['load'], ORANGE, 0.5 * fade, width=30)

        # stop-time: the coils heat; each hit the porch glows redder and the heat pulses out; hit three is a false pop
        if M['heat'] <= t < M['line']:
            k = sum(1 for h in heat_hits if h <= t)
            glow = 0.15 + 0.2 * k
            fr += light(RED, glow * S.porch * (0.75 + 0.25 * np.sin(2 * np.pi * (1 + k) * t)))
            fr += light(ORANGE, 0.6 * glow * S.blob(mid, 160))
            for i, th in enumerate(heat_hits):
                fr += S.wave(t, th, ORANGE if i != 2 else WHITE, 0.9, speed=900, width=60, decay=0.7)
                a = t - th
                if 0 <= a < 0.6:
                    fr += light(RED, 0.6 * np.exp(-a / 0.15) * S.wings)
            fr += keyboard(S, t, tunes['heat'], ORANGE, 0.6, width=30)
            if t >= M['wait']:                                     # the held breath: the coils tick
                a = t - M['wait']
                fr += light(RED, 0.5 * (0.5 + 0.5 * np.cos(2 * np.pi * 5 * a)) * S.blob(mid, 30))

        # toast in the air, and every slice that has landed lying where it fell (butter on it once flicked)
        on = (t >= land).astype(float)
        if on.any():
            bt = (t >= butt).astype(float) * on
            glow = 1.0
            if M['hold'] <= t < M['finale']:
                glow = 0.7
            if t >= M['finale']:
                glow = 0.75 + 0.35 * pulse(t, fin_beats, 0.2)
            tl = np.clip(W @ on, 0, 1)
            bl = np.clip(W @ bt, 0, 1)
            fr = fr * (1 - 0.5 * tl[:, None]) + light(TOAST, 0.75 * glow * tl) + light(BUTTER, 0.45 * glow * bl)
        fr += flying(S, t, sl)
        if M['line'] <= t < M['storm']:
            for t0 in pops:
                if t0 <= t < t0 + 2.5:
                    fr += S.wave(t, t0, GOLD, 0.55, speed=1300, width=50, decay=0.6)

        # the line: the first pop flashes the house; butter flicks out to each slice on the backbeat
        if M['line'] <= t < M['faster']:
            a = t - M['line']
            if a < 1.5:
                fr += S.wave(t, M['line'], WHITE, 1.0, speed=1600, width=80, decay=0.8)
                fr += light(GOLD, 0.6 * np.exp(-a / 0.3) * np.ones(S.N))
            for t0, p1, dur, tb in sl:
                b = t - tb + 0.3
                if 0 <= b < 0.5 and tb < M['faster']:
                    q = mid + (p1 - mid) * min(1.0, b / 0.3)
                    fr += light(BUTTER, (1 - b / 0.5) * np.exp(-((d - q) / 12) ** 2))
            fr += S.run_flash(t, line_beats, cols=(GOLD, ORANGE), lv=0.35, decay=0.2)
            fr += keyboard(S, t, tunes['line'], BUTTER, 0.55)

        # faster: a slice a beat; marquee bulbs chase round the porch; the wings flash on the bar
        if M['faster'] <= t < M['storm']:
            ph = 2 * (t - M['faster']) / (60 / 176)
            fr += S.chase(ph, cols=(BUTTER, None, TOAST, None), lv=0.55, spacing=2, mask=S.porch)
            fr += S.run_flash(t, faster_downs, cols=(WHITE, BUTTER), runs=('Left', 'Right'), lv=0.6, decay=0.3)
            fr += keyboard(S, t, tunes['faster'], WHITE, 0.55)

        # the storm: butter zigzags race every run, a run flashing on each beat
        if M['storm'] <= t < M['hold'] + 0.3:
            fade = float(smoothstep(M['hold'] + 0.3, M['hold'], t))
            ph = (t - M['storm']) / (60 / 184)
            bar = int(ph // 4)
            zig = S.zigzag(ph, lv=0.5 * fade, col=BUTTER if bar % 2 == 0 else GOLD, period=70, travel=0.4 * (-1) ** bar)
            fr = fr * (1 - 0.3 * fade) + zig
            fr += S.run_flash(t, storm_beats, cols=(WHITE, BUTTER, GOLD), lv=0.5 * fade, decay=0.15)
            fr += S.run_flash(t, storm_downs, cols=(ORANGE,), runs=('Side', 'Side'), lv=0.6 * fade, decay=0.4)

        # the hold: one slice goes in, the coils tick, then the last enormous pop throws gold across the house
        if M['hold'] <= t < M['finale']:
            a = t - M['hold']
            fr += light(BREAD, 0.8 * float(smoothstep(0.2, 0.5, a)) * S.blob(mid, 10))
            fr += light(RED, 0.5 * (0.5 + 0.5 * np.cos(2 * np.pi * 4 * a)) * float(smoothstep(0.5, 1.4, a)) *
                        S.blob(mid, 40))
        if t >= M['finale']:
            a = t - M['finale']
            if a < 4:
                fr += light(WHITE, 0.9 * np.exp(-a / 0.12) * np.ones(S.N))
                fr += S.sweep(t, M['finale'], 0.9, GOLD, 1.0, frm='centre', width=120, trail=0.8)
                fr += S.confetti([(M['finale'], 1.0, mid)], t, colors=(GOLD, BUTTER, TOAST, WHITE), n=40, reach=1.6,
                                 seed=5)
            ph = (t - M['finale']) / (60 / 132)
            fade = float(smoothstep(M['button'] + 0.6, M['button'] + 0.1, t))
            fr += S.chase(2 * ph, cols=(BUTTER, None, None), lv=0.5 * fade, spacing=2, mask=S.porch)
            fr += S.run_flash(t, fin_beats, cols=(BUTTER, GOLD, WHITE), lv=0.45 * fade, decay=0.2)
            fr += keyboard(S, t, tunes['finale'], WHITE, 0.6)
            fr += S.sweep(t, fin_downs[6], 2.2, WHITE, 0.8, frm='right', width=90, trail=0.5)
            b = t - M['button']
            if b >= 0:
                fr += light(BUTTER, np.exp(-b / 0.5) * np.ones(S.N))
                fr += light(WHITE, 0.8 * np.exp(-b / 0.12) * np.ones(S.N))

        # the toaster on the porch, and Snoopy in his chef's hat
        if t >= M['strut'] - 0.1:
            body = S.span(mid - 14, mid + 14)
            fr = fr * (1 - 0.5 * body[:, None]) + light(SILVER, 0.45 * body)
            fr += light(RED, 0.8 * heat * S.blob(mid, 5))
            b = pulse(t, beats, 0.14)
            jump = 0.0
            if len(heat_hits) > 2 and 0 <= t - heat_hits[2] < 0.5:
                jump = 1.0
            p = beagle_p(S, t)
            facing = 1 if (M['strut'] <= t < M['strut'] + 8 or t >= M['finale'] and int((t - M['finale']) / 1.82) % 2)\
                else -1
            if M['storm'] <= t < M['hold']:
                facing = 1 if np.cos(2 * np.pi * 0.9 * (t - M['storm'])) > 0 else -1
            fr = S.beagle(fr, p + 12 * jump, min(1.2, 0.85 + 0.25 * b + 0.3 * jump), facing=facing, t=t, chef=True)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def score(M_, G):
    S = Stage(G)
    mid = S.mid
    sl = slices(S)
    B = Band(M_, level=0.83)
    parts = {
        ('strut', 'tune'): [('piano', 0, 6, 0.85), ('xylo', 12, -16, 0.2)],
        ('load', 'tune'): [('piano', 0, 6, 0.8), ('marimba', 0, -10, 0.35)],
        ('heat', 'tune'): [('harmon trumpet', 0, 6, 0.9), ('piano', 0, -8, 0.4)],
        ('heat', 'hit'): [('piano', 0, 6, 0.8), ('muted horn', 0, -4, 0.45)],
        ('line', 'tune'): [('piano', 0, 10, 0.85), ('xylo', 12, -10, 0.25)],
        ('faster', 'tune'): [('piano', 0, 12, 0.85), ('xylo', 12, -8, 0.3)],
        ('storm', 'tune'): [('piano', 0, 14, 0.9), ('harmon trumpet', 0, -4, 0.5), ('xylo', 12, -6, 0.3)],
        ('storm', 'comp'): [('piano', 0, -4, 0.5), ('horns', 0, -14, 0.3)],
        ('finale', 'tune'): [('piano', 0, 10, 0.85), ('harmon trumpet', 0, -4, 0.45), ('vibes', 0, -12, 0.25)],
        ('finale', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -16, 0.25)],
        ('button', 'hit'): [('piano', 0, 0, 0.9), ('horns', 0, -4, 0.5), ('trombones', -12, -6, 0.4)],
    }
    B.perform(C.events, parts)
    # the kitchen: a warm open chord before the count; Snoopy pops up with a woof
    for m in (60, 64, 67, 70):
        B.play('choir', m, 0.2, 1.9, 48, gain=0.3)
    B.boing(M['strut'], pan=S.pan(mid), gain=0.8)
    B.woof(M['strut'] + 0.25, pan=S.pan(mid))
    B.steps(M['strut'] + 0.5, M['load'], beat=60 / 120, pan=lambda tt: S.pan(beagle_p(S, tt)), gain=0.5)
    # the line: a clunk on every beat as each slice goes in, the lever pushed down at the end
    for tb in C.beat_times('load'):
        B.hit('wood', tb, 100, gain=0.5, pan=S.pan(mid))
    B.hit('ratchet', M['load'], 90, gain=0.4, pan=S.pan(mid))
    B.hit('claves', M['heat'] - 0.1, 110, pitch=-7, gain=0.5, pan=S.pan(mid))
    B.slide(M['heat'] - 0.1, 0.4, up=False, pan=S.pan(mid), gain=0.4, lo=400, hi=900)
    # the coils heat; the false pop (a boing, a woof, nothing); the roll into the first pop
    B.fire(M['heat'], M['line'] + 0.5, level=lambda tt: np.clip((tt - M['heat']) / (M['line'] - M['heat']), 0.1, 1) * 0.3,
           pan=S.pan(mid), crackle=8)
    h3 = C.times('hit', 'heat')[2]
    B.boing(h3 + 0.05, pan=S.pan(mid), gain=0.9, high=1.6)
    B.woof(h3 + 0.4, pan=S.pan(mid), big=0.7)
    B.roll(M['wait'] - 0.2, M['line'], pan=S.pan(mid), gain=0.8)
    B.hit('cymbal swell', M['wait'] - 0.6, 90, gain=0.35)
    # every slice: a pop as it leaves, a pat as it lands; butter flicked on the backbeat in the line
    for t0, p1, dur, tb in sl:
        storm = t0 >= M['storm']
        g = 0.45 if storm else 0.8
        B.toast_pop(t0, pan=S.pan(mid), gain=g, fly=not storm)
        B.hit('hoof soft', t0 + dur, 80, gain=0.35 if storm else 0.6, pan=S.pan(p1), fx=True)
        if tb < M['faster']:
            B.whoosh(tb - 0.3, 0.3, up=True, pan=S.pan(p1), gain=0.3)
    B.hit('crash', M['line'], 110, gain=0.4)
    B.ding(M['faster'], pan=S.pan(mid), gain=0.8)
    B.ding(M['storm'], pan=S.pan(mid), gain=0.8)
    B.effects([(0, -3), (M['line'], 0), (M['storm'], -3), (M['hold'], 0), (M['finale'] + 2, -3)])
    # the hold: one more slice in, the lever, the timer ticking; the last enormous pop
    B.hit('claves', M['hold'] + 0.3, 110, pitch=-7, gain=0.5, pan=S.pan(mid))
    for k in range(5):
        B.hit('woodblock', M['hold'] + 0.6 + 0.18 * k, 70 + 6 * k, pitch=5, gain=0.35, pan=S.pan(mid))
    B.toast_pop(M['finale'], pan=S.pan(mid), gain=1.6)
    B.slide(M['finale'] + 0.02, 1.1, up=True, gain=0.8, lo=450, hi=1700)
    B.hit('crash', M['finale'], 122, gain=0.55)
    B.hit('timpani', M['finale'] + 0.02, 118, pitch=-5, gain=0.45)
    B.kids(M['finale'] + 0.3, M['finale'] + 1.6, 'cheer', level=0.35, voices=5, seed=3)
    B.woof(M['finale'] + 1.0, pan=S.pan(mid))
    B.whoosh(C.downbeats('finale')[6], 2.0, up=False, gain=0.5, pan=lambda tt: 0.8 - 1.6 * (tt - C.downbeats('finale')[6]) / 2.2)
    B.hit('cymbal swell', M['button'] - 1.6, 100, gain=0.4)
    B.hit('crash', M['button'], 122, gain=0.55)
    B.crunch(M['button'] + 0.8, bites=2, pan=S.pan(mid), gain=0.7)
    B.finish()
