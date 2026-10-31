"""The First Thanksgiving: Linus says grace and tells the story of the crossing and the first feast.

The backyard at the table, everyone seated. Linus stands at the head of the table on Porch Left and
the house drops to candlelight while his gentle waltz plays: every bar a ring of light breathes out from him across the
whole roof, gold and then his blanket's blue. As he begins the story the sea rises out of the porch, a blue wipe to both
ends with foam sparkling on every note of a harp. A little ship (brown hull, white sails between dark masts, a red
lantern at the stern) sails in from the free end of Right on his theme, swells rolling through every run on each bar.
Then the storm: his theme turned to G minor at double time, the sea grey and fast, rain streaking, the ship tossed;
lightning cracks down on a run on every other bar (now and then the whole house for an instant) with thunder, and at
the height of it a great white wave breaks over the whole house from the end of Right. Calm: the sea smooths, a sunrise
swells gold over the porch, the shore grows green and brown out along Left, and the ship glides in to land at the corner
of the porch with a swell of the choir. Then the harvest on Grandma's homey tune: the fields fill run by run with corn
gold and green, pumpkins popping up on the beat. The harvest feast on the feast theme: stripes of roast, corn,
cranberry, pine and pumpkin marching across the house, leaves thrown up on every bar, a sweep from the porch. And back
in the backyard: amen, a last warm ring out from him over the table, the kids' choir on the final chord.

compose() lays the music end to end (pixelhome/chef_charlie.py): render() and score() both read its events and marks.
The storm's tune is Linus's own theme, moved into G minor here."""
import numpy as np
from pixelhome.fx import DT, nframes, light, smoothstep, keys
from pixelhome.audio import note
from pixelhome.chef_charlie import (Chart, Band, Stage, pulse, voicing, THEMES, WHITE, AMBER, GOLD, ORANGE, BROWN,
                                    RED, BLANKET, WARM, SEA, FOAM, ICE, SUN, LAWN, PINE, TURKEY, CRANBERRY, LEAVES,
                                    TOAST, POPCORN, PRETZEL, JELLY)

CODE = 'CC09'
TITLE = 'The First Thanksgiving'
KIND = 'show'
DESCRIPTION = ('Linus says grace and tells how the Pilgrims crossed a stormy sea, landed, brought in their first harvest '
    'and shared a feast with their Wampanoag neighbours.')
VOICEOVER = 'Before they eat, Linus tells everyone how Thanksgiving began.'


def _minor(n):
    """A note of the blanket theme moved from G major into G minor."""
    m = note(n)
    m = m - 1 if m % 12 in (11, 4, 6, 1, 8) else m
    return ('C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B')[m % 12] + str(m // 12 - 1)


_BL = THEMES['blanket']
STORM = dict(meter=3, bpm=168, swing=False, id='storm',
             melody=[(b, ln, _minor(n)) for b, ln, n in _BL['melody'] if b < 24],
             chords=[(0, 3, 'Gm7'), (3, 3, 'Cm7'), (6, 3, 'Am7b5'), (9, 3, 'D7'), (12, 3, 'Gm7'), (15, 3, 'Eb7'),
                     (18, 3, 'Am7b5'), (21, 3, 'D7')])
AMEN = dict(meter=4, bpm=66, swing=False, id='amen', melody=[(0, 2, 'E4'), (2, 2, 'D4')],
            chords=[(0, 2, 'C'), (2, 2, 'G')])


def compose():
    C = Chart()
    C.rest(2.0)                                                     # the backyard, everyone at the table
    C.mark('grace')
    C.play('blanket', style='waltz', bars=(0, 8), bpm=112, tag='grace')         # he says grace
    C.mark('dissolve')
    C.play('blanket', style='arp', bars=(8, 12), bpm=112, tag='dissolve')       # the sea rises out of the porch
    C.mark('voyage')
    C.play('blanket', style='waltz', bars=(0, 8), bpm=138, tag='voyage')        # the ship sails in
    C.mark('storm')
    C.play(STORM, style='drive', tag='storm')                       # the storm
    C.mark('storm2')
    C.play(STORM, style='drive', bpm=184, tag='storm2')             # the height of it: the great wave
    C.mark('calm')
    C.play('blanket', style='hold', bars=(12, 16), bpm=100, tag='calm')         # calm, sunrise, the landing
    C.mark('harvest')
    C.play('grandma', style='two', bpm=108, tag='harvest')          # the fields fill
    C.mark('feast')
    C.play('feast', style='swing', tag='feast')                     # the harvest feast
    C.mark('amen')
    C.play(AMEN, style='hold', tag='amen')                          # back at the table: amen
    C.rest(2.6)
    C.mark('end')
    return C


C = compose()
D = C.marks['end']
M = C.marks

PLACES = {}


def places(S):
    """The table and the kids round it (as they sat down in The Guests Arrive), and the ship's course."""
    if not PLACES:
        m = S.mid
        PLACES.update(table=m, boy=m - 65, cap=m - 125, tom=m + 70, gl=m + 125, blanket=S.at('Porch Left', 0.82),
                      enter=S.L + 40, sea1=S.at('Right', 0.35), sea2=S.at('Porch Right', 0.45),
                      land=S.at('Porch Front', 0.22), shore=S.at('Left', 0.0))
    return PLACES


def ship_p(S, t):
    """The ship: in from past the end of Right, tossed through the storm, gliding in to land by the porch corner."""
    P = places(S)
    if t < M['storm']:
        u = float(smoothstep(M['voyage'], M['storm'], t))
        return P['enter'] + (P['sea1'] - P['enter']) * u + 6 * np.sin(2 * np.pi * 0.7 * t)
    if t < M['calm']:
        u = (t - M['storm']) / (M['calm'] - M['storm'])
        return P['sea1'] + (P['sea2'] - P['sea1']) * u + 26 * np.sin(2 * np.pi * 1.25 * t) * np.sin(np.pi * u)
    u = float(smoothstep(M['calm'], M['harvest'] - 1.0, t))
    return P['sea2'] + (P['land'] - P['sea2']) * u


def ship(S, fr, p, lvl=1.0, t=0.0, lantern=1.0):
    """The ship: a brown hull fore and aft, white sails between two dark masts, a red lantern at the stern; it sails
    toward Side (facing -1)."""
    px = [(6, BROWN, 0.7), (5, BROWN, 0.95), (4, WHITE, 0.95), (3, WHITE, 1.0), (2, None, 0), (1, WHITE, 1.0),
          (0, WHITE, 1.0), (-1, WHITE, 0.95), (-2, None, 0), (-3, WHITE, 0.9), (-4, WHITE, 0.85), (-5, BROWN, 0.95),
          (-6, BROWN, 0.9), (-7, RED, 0.9 * lantern * (0.75 + 0.25 * np.sin(5 * t)))]
    return S.sprite(fr, p, px, lvl, facing=-1)


def keyboard(S, t, notes, col, lv, decay=0.3, width=26.0):
    """The tune plays the roofline: each note sparks where its pitch sits across the front."""
    out = np.zeros((S.N, 3))
    for t0, dur, m in notes:
        a = t - t0
        if 0 <= a < 6 * decay:
            out += light(col, lv * np.exp(-a / decay) * S.blob(S.note_at(m), width))
    return out


FIELD_ORDER = ('Left', 'Porch Front', 'Right', 'Porch Left', 'Porch Right', 'Side')
FEAST_COLS = (TURKEY, GOLD, CRANBERRY, PINE, ORANGE, WARM)
FOOD = [(-8, TOAST), (-7, TOAST), (-4, POPCORN), (-3, POPCORN), (3, PRETZEL), (4, PRETZEL), (7, JELLY[0]),
        (8, JELLY[2])]


def render(G, seed=1):
    S = Stage(G)
    P = places(S)
    d, L = S.d, S.L
    rng = np.random.default_rng(seed)
    rain_ph = rng.uniform(0, 1, S.N)
    rain_sp = rng.uniform(1.6, 2.6, S.N)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    beats = np.array(C.beat_times())
    grace_downs = C.downbeats('grace')
    arp_notes = [e[0] for e in C.events if e[4] == 'arp']
    voy_downs = C.downbeats('voyage')
    st_beats = np.array(C.beat_times('storm') + C.beat_times('storm2'))
    st_downs = C.downbeats('storm') + C.downbeats('storm2')
    bolts = C.downbeats('storm')[1::2] + C.downbeats('storm2')[0::2]
    big_wave = C.downbeats('storm2')[6]
    harvest_downs = C.downbeats('harvest')
    harvest_beats = C.beat_times('harvest')
    feast_beats = np.array(C.beat_times('feast'))
    feast_downs = C.downbeats('feast')
    tunes = {g: C.tunes(g) for g in ('grace', 'voyage', 'storm', 'storm2', 'calm', 'harvest', 'feast')}
    last_feast = tunes['feast'][-1][0]
    b_feast = 60 / 184
    land_t = M['harvest'] - 1.0
    yard_lv = [(0, 0.0), (1.6, 1.0), (M['grace'], 1.0), (M['grace'] + 1.5, 0.6), (M['dissolve'] + 3, 0.4),
               (M['voyage'], 0.0), (M['amen'] - 0.6, 0.0), (M['amen'] + 0.3, 0.8), (M['end'], 0.8)]
    sea_lv = [(M['dissolve'], 0.0), (M['voyage'], 1.0), (M['harvest'] - 1.0, 1.0), (M['harvest'] + 0.6, 0.0)]
    storm_k = [(M['storm'] - 1.0, 0.0), (M['storm'], 1.0), (M['calm'], 1.0), (M['calm'] + 3.0, 0.0)]

    for f in range(F):
        t = f * DT
        fr = np.zeros((S.N, 3))
        lv_y = float(keys(t, yard_lv))
        if lv_y > 0:
            fr += S.backyard(t, lv=lv_y)
        beat = pulse(t, beats, 0.14)

        # grace: candlelight, a ring breathing out from him every bar, gold then blue
        if M['grace'] <= t < M['voyage']:
            fade = float(smoothstep(M['dissolve'] + 2.5, M['dissolve'], t))
            fr += light(WARM, 0.35 * fade * S.blob(P['table'], 160) * (0.9 + 0.1 * np.sin(13 * t)))
            for i, tb in enumerate(grace_downs):
                col = GOLD if i % 2 == 0 else BLANKET
                fr += S.wave(t, tb, col, 1.0 * fade, origin=P['blanket'], speed=520, width=130, decay=3.0)
            fr += keyboard(S, t, tunes['grace'], GOLD, 0.45 * fade, decay=0.5, width=34)
            fr += light(BLANKET, 0.4 * fade * S.blob(P['blanket'] - 40, 50))

        # the sea rises out of the porch, a wipe to both ends; then the sea itself
        if M['dissolve'] <= t < M['voyage'] + 0.5:
            fr += S.sweep(t, M['dissolve'] + 0.4, M['voyage'] - M['dissolve'] - 0.8, SEA, 0.9, frm='centre',
                          width=140, trail=3.0)
            for tn in arp_notes:
                a = t - tn
                if 0 <= a < 0.6:
                    q = S.mid + (np.sin(tn * 7.7) * 0.5) * (t - M['dissolve']) * 220
                    fr += light(FOAM, 0.9 * np.exp(-a / 0.18) * S.blob(q, 14))
        lv_s = float(keys(t, sea_lv))
        if lv_s > 0:
            st = float(keys(t, storm_k))
            fr = fr * (1 - lv_s) + S.sea(t, lv=lv_s * (0.85 + 0.15 * beat), swell=1.0 - 0.5 * (t > M['calm'] + 2),
                                         speed=60 + 40 * (t > M['voyage']), storm=st)

        # the swell: big dark troughs and bright crests rolling toward Side, faster and deeper in the storm
        if lv_s > 0:
            st = float(keys(t, storm_k))
            amp = (0.7 + 0.15 * st) * lv_s
            heave = 0.5 + 0.5 * np.sin(2 * np.pi * (d + (150 + 170 * st) * t) / (420 + 120 * st))
            fr *= (1 - amp) + 1.5 * amp * heave[:, None]

        # the voyage: a swell rolls through every run on each bar, from the ship's side of the house
        if M['voyage'] <= t < M['storm'] + 1:
            for tb in voy_downs:
                a = t - tb
                if 0 <= a < 6:
                    q = L - 430 * a
                    fr += light(FOAM, 0.9 * np.exp(-a / 3.0) * np.exp(-((d - q) / 40) ** 2))
                    fr += light(SEA, 0.8 * np.exp(-a / 3.0) * np.exp(-((d - q - 90) / 90) ** 2))
            fr += keyboard(S, t, tunes['voyage'], FOAM, 0.4, width=24)

        # the storm: rain, swells on every beat, lightning on every other bar, and the great wave
        if M['storm'] <= t < M['calm'] + 2:
            st = float(keys(t, storm_k))
            drop = np.exp(-((((d * 0.013 + rain_sp * t * 3.1 + rain_ph) % 1.0) - 0.5) / 0.035) ** 2)
            fr += light(ICE, 0.55 * st * drop)
            fr += S.run_flash(t, st_beats, cols=(FOAM, SEA), runs=('Right', 'Porch Front', 'Left', 'Porch Right',
                                                                   'Porch Left', 'Side'), lv=0.45 * st, decay=0.2)
            for tb in st_downs:
                a = t - tb
                if 0 <= a < 3:
                    q = L - 900 * a
                    fr += light(FOAM, 0.7 * st * np.exp(-a / 1.2) * np.exp(-((d - q) / 60) ** 2))
            for i, tb in enumerate(bolts):
                a = t - tb
                if 0 <= a < 0.7:
                    brng = np.random.default_rng(100 + i)
                    run = S.RUNS[int(brng.integers(1, 6))]
                    jag = (np.sin(d * brng.uniform(0.05, 0.12) + brng.uniform(0, 6)) > 0.2)
                    flick = np.exp(-a / 0.07) + 0.7 * np.exp(-max(a - 0.15, 0) / 0.06) * (a > 0.15)
                    fr += light(WHITE, min(1.0, 1.2 * flick) * S.run[run] * (0.5 + 0.5 * jag))
                    fr += light(ICE, 0.9 * np.exp(-a / 0.35) * S.run[run])
                    if i % 2 == 0:                                   # now and then the whole house, for an instant
                        fr += light(WHITE, 0.55 * np.exp(-a / 0.05) * np.ones(S.N))
            a = t - big_wave
            if 0 <= a < 4:
                fr += S.sweep(t, big_wave, 1.4, FOAM, 1.0, frm='right', width=160, trail=0.8)
                fr += S.sweep(t, big_wave + 0.15, 1.4, WHITE, 0.7, frm='right', width=60, trail=0.3)
            fr += keyboard(S, t, tunes['storm'] + tunes['storm2'], ICE, 0.45 * st, width=22)

        # calm: sunrise swells gold over the porch, the shore grows out along Left, the ship lands
        if M['calm'] <= t < M['harvest'] + 1.0:
            u = float(smoothstep(M['calm'], M['harvest'], t))
            fade = float(smoothstep(M['harvest'] + 1.0, M['harvest'], t))
            fr += light(SUN, 0.8 * u * fade * S.blob(S.mid, 120 + 200 * u))
            fr += light(GOLD, 0.4 * u * fade * S.blob(S.mid, 500))
            edge = P['shore'] + (P['land'] - 30 - P['shore']) * u
            shore = S.span(0, P['shore'] + (edge - P['shore'])) * (d <= edge + 8)
            shore = np.maximum(shore, S.span(P['shore'] - (edge - P['shore']) * 0.6, P['shore']))
            fr = fr * (1 - 0.8 * shore[:, None] * fade) + (light(LAWN, 0.7 * shore) + light(BROWN, 0.35 * shore *
                                                             (np.sin(0.08 * d) > 0.3))) * fade
            fr += keyboard(S, t, tunes['calm'], GOLD, 0.5 * fade, decay=0.6, width=40)
            a = t - land_t
            if 0 <= a < 3:
                fr += S.wave(t, land_t, GOLD, 0.9, origin=P['land'], speed=700, width=100, decay=1.2)
                fr += light(WHITE, 0.7 * np.exp(-a / 0.15) * S.blob(P['land'], 50))

        # the harvest: the fields fill run by run, corn gold and green; pumpkins pop up on the beat
        if M['harvest'] <= t < M['feast'] + 0.8:
            fade = float(smoothstep(M['feast'] + 0.8, M['feast'], t))
            fr += S.yard(t, lv=0.5 * fade, leaves=0.6, sun=0.6) * fade
            for i, r in enumerate(FIELD_ORDER):
                if i < len(harvest_downs):
                    a = t - harvest_downs[i]
                    if a >= 0:
                        grow = float(smoothstep(0, 0.6, a))
                        sway = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 22.0) - 2.5 * t)
                        stalk = (np.sin(2 * np.pi * d / 22.0) > -0.2) * grow
                        m = S.run[r] * fade
                        fr = fr * (1 - 0.6 * m[:, None] * grow)
                        fr += light(GOLD, (0.55 + 0.35 * sway) * stalk * m) + light(PINE, 0.5 * (1 - stalk) * m * grow)
                        if a < 0.5:
                            fr += light(WHITE, 0.6 * np.exp(-a / 0.15) * S.run[r] * fade)
            for j, tb in enumerate(harvest_beats):
                a = t - tb
                if 0 <= a and j % 2 == 1:
                    q = S.L * ((j * 0.618) % 1.0)
                    pv = float(smoothstep(0, 0.15, a)) * (1 + 0.8 * np.exp(-a / 0.15))
                    fr += light(ORANGE, 0.9 * fade * pv * np.exp(-((d - q) / 11) ** 2))
            for tb in harvest_downs:                                 # wind through the corn on every bar
                a = t - tb
                if 0 <= a < 3:
                    q = L - 650 * a
                    fr += light(WARM, 0.7 * fade * np.exp(-a / 1.5) * np.exp(-((d - q) / 70) ** 2))
            fr += keyboard(S, t, tunes['harvest'], WARM, 0.55 * fade, width=30)

        # the feast: harvest stripes marching on the beat, leaves on every bar, a sweep out from the porch
        if M['feast'] <= t < M['amen'] + 0.8:
            fade = float(smoothstep(M['amen'] + 0.8, M['amen'], t))
            rise = float(smoothstep(M['feast'], M['feast'] + 0.4, t))
            n_b = (t - M['feast']) / b_feast
            fr = fr * (1 - 0.65 * rise * fade) + S.stripes(n_b, FEAST_COLS, lv=0.75 * rise * fade, period=44)
            fr += S.run_flash(t, feast_beats, cols=(WARM, WHITE), lv=0.5 * fade, decay=0.13)
            fr += S.confetti([(tb, 0.9, S.mid) for tb in feast_downs], t, colors=LEAVES, n=22, reach=1.0, seed=3)
            fr += S.sweep(t, feast_downs[6], 1.5, GOLD, 0.85 * fade, frm='centre', width=90, trail=0.5)
            a = t - last_feast
            if 0 <= a < 1.5:
                fr += light(GOLD, 0.8 * np.exp(-a / 0.4) * np.ones(S.N) * fade)

        # amen: a last warm ring out from him over the table
        if t >= M['amen']:
            a = t - M['amen']
            fr += S.wave(t, M['amen'] + 0.2, WARM, 0.8, origin=P['blanket'], speed=450, width=150, decay=2.0)
            fr += S.wave(t, M['amen'] + 1.8, GOLD, 0.6, origin=P['blanket'], speed=450, width=150, decay=2.0)
            fr += light(WARM, 0.35 * float(smoothstep(0, 1, a)) * S.blob(P['table'], 160))

        # the ship
        if M['voyage'] - 0.5 <= t < M['harvest'] + 1.2:
            vis = float(smoothstep(M['voyage'] - 0.5, M['voyage'] + 0.3, t) *
                        smoothstep(M['harvest'] + 1.2, M['harvest'] + 0.2, t))
            toss = 1.0
            if M['storm'] <= t < M['calm']:
                toss = 0.85 + 0.15 * np.sin(2 * np.pi * 2.5 * t)
            fr = ship(S, fr, ship_p(S, t), vis * toss, t=t)

        # the table and the kids: at grace and amen
        kids = float(smoothstep(M['grace'] - 2.0, M['grace'] - 1.0, t) * smoothstep(M['dissolve'] + 3.0,
                                                                                   M['dissolve'] + 1.0, t))
        kids = max(kids, float(smoothstep(M['amen'] - 0.6, M['amen'] + 0.3, t)))
        if kids > 0:
            bow = 0.65 if M['grace'] + 0.5 <= t < M['dissolve'] else 0.9    # heads bowed
            fr = S.table(fr, P['table'], kids, half=10, food=FOOD)
            fr = S.boy(fr, P['boy'], kids * bow, facing=1, t=t, glow=0.15)
            fr = S.cap_boy(fr, P['cap'], kids * bow, facing=1, t=t)
            fr = S.tomboy(fr, P['tom'], kids * bow, facing=-1, t=t)
            fr = S.glasses(fr, P['gl'], kids * bow, facing=-1, t=t)
            fr = S.blanket_boy(fr, P['blanket'], kids * (1.0 + 0.2 * beat), facing=1, t=t)

        out[f] = fr * float(smoothstep(D, D - 1.5, t))
    return np.clip(out, 0, 1)


def pad(B, theme, tag, section, gain, low=55, vel=60, start=0, pan=None):
    """Sustained chords under a passage on section (strings, choir), one per chord of the theme, timed off the chart.
    start is the theme's beat the passage began on."""
    th = THEMES[theme] if isinstance(theme, str) else theme
    downs = C.downbeats(tag)
    beat = (downs[1] - downs[0]) / th['meter']
    n_beats = len(C.beat_times(tag))
    t0, t_end = M[tag], M[tag] + n_beats * beat
    for cb, cl, sym in th['chords']:
        if start <= cb < start + n_beats:
            ts = t0 + (cb - start) * beat
            for m in voicing(sym, low, rootless=False):
                B.play(section, m, ts, min(cl * beat, t_end - ts) + 0.2, vel, pan, gain)


def score(M_, G):
    S = Stage(G)
    P = places(S)
    B = Band(M_, level=1.0)
    parts = {
        ('grace', 'tune'): [('piano', 0, -4, 0.85)],
        ('grace', 'comp'): [('piano', 0, -14, 0.4), ('choir', 12, -24, 0.3)],
        ('dissolve', 'arp'): [('harp', 0, 0, 0.7), ('glock', 12, -30, 0.15)],
        ('dissolve', 'pedal'): [('cellos', 0, -16, 0.4)],
        ('voyage', 'tune'): [('oboes', 0, 0, 0.7), ('piano', 0, -14, 0.4)],
        ('voyage', 'comp'): [('harp', 0, -6, 0.5)],
        ('storm', 'tune'): [('horns', 0, 8, 0.6), ('piano', 0, 0, 0.6)],
        ('storm', 'comp'): [('piano', 0, -4, 0.5)],
        ('storm2', 'tune'): [('horns', 0, 12, 0.65), ('trumpets', 0, -2, 0.4), ('piano', 0, 4, 0.6)],
        ('storm2', 'comp'): [('piano', 0, 0, 0.5), ('trombones', -12, -10, 0.3)],
        ('calm', 'tune'): [('flutes', 0, 0, 0.7), ('piano', 0, -10, 0.5)],
        ('calm', 'hold'): [('choir', 0, -4, 0.55)],
        ('calm', 'pedal'): [('cellos', 0, -12, 0.4)],
        ('harvest', 'tune'): [('piano', 0, 0, 0.85), ('clarinets', 0, -10, 0.4)],
        ('harvest', 'comp'): [('piano', 0, -10, 0.45), ('choir', 12, -24, 0.3)],
        ('feast', 'tune'): [('piano', 0, 10, 0.85), ('trumpets', 0, -6, 0.45)],
        ('feast', 'comp'): [('piano', 0, -6, 0.5), ('horns', 0, -14, 0.3)],
        ('amen', 'tune'): [('choir', 12, 0, 0.45), ('piano', 0, -6, 0.6)],
        ('amen', 'hold'): [('choir', 0, -4, 0.45), ('horns', 0, -16, 0.3)],
        ('amen', 'pedal'): [('cellos', 0, -10, 0.45)],
    }
    B.perform(C.events, parts)
    # evening at the table, the candle's soft chord
    for m in (59, 62, 66, 71):
        B.play('choir', m, 0.2, 2.0, 48, gain=0.3)
    # the voyage: strings swell under the waltz, the sea washes; the storm: tremolo strings, wind, thunder
    pad(B, 'blanket', 'voyage', 'violins', 0.25, low=55, vel=56)
    pad(B, STORM, 'storm', 'violins trem', 0.35, low=55, vel=74)
    pad(B, STORM, 'storm2', 'violins trem', 0.4, low=55, vel=86)
    pad(B, STORM, 'storm2', 'cellos trem', 0.35, low=43, vel=84)
    B.wind(M['dissolve'] + 2, M['storm'], level=0.35, pan=0.3)
    B.wind(M['storm'] - 0.5, M['calm'] + 2.5, level=0.7, pan=0.0)
    B.hit('timpani roll', M['storm'] - 0.6, 90, gain=0.4)
    for i, tb in enumerate(C.downbeats('storm')[1::2] + C.downbeats('storm2')[0::2]):
        B.thunder(tb, near=0.6 + 0.4 * (i % 2 == 0), pan=0.6 * np.sin(i * 2.1), gain=0.8, seed=i)
    bw = C.downbeats('storm2')[6]
    B.whoosh(bw - 0.3, 1.6, up=False, gain=0.8, pan=lambda tt: 0.8 - 1.6 * (tt - bw) / 1.6)
    B.hit('crash', bw, 120, gain=0.55)
    B.hit('timpani', bw, 124, pitch=-5, gain=0.5)
    B.hit('bass drum', bw + 0.02, 120, gain=0.5)
    # the landing: a harp glissando up, a bell, a glow of choir
    land_t = M['harvest'] - 1.0
    for k, m in enumerate((55, 59, 62, 67, 71, 74, 79)):
        B.play('harp', m, land_t - 0.5 + 0.06 * k, 1.2, 80, pan=S.pan(P['land']), gain=0.5)
    B.O.hit('triangle', land_t, 90, gain=0.5, pan=S.pan(P['land']))
    # the harvest: pumpkins popping up (a woodblock pop on every other beat)
    for j, tb in enumerate(C.beat_times('harvest')):
        if j % 2 == 1:
            B.hit('woodblock', tb, 76, pitch=-2 + (j % 5), gain=0.25, pan=S.pan(S.L * ((j * 0.618) % 1.0)))
    # the feast: tambourine on the backbeat, a whoosh on the sweep, the last note rung
    for k, tb in enumerate(C.beat_times('feast')):
        if k % 2 == 1:
            B.hit('tambourine', tb, 72, gain=0.25)
    B.whoosh(C.downbeats('feast')[6], 1.2, up=True, gain=0.4)
    B.hit('cymbal swell', M['amen'] - 1.4, 90, gain=0.35)
    B.hit('crash', M['amen'] - 0.02, 100, gain=0.3)
    B.effects([(0, -3), (M['storm'], 0), (M['calm'] + 2, -3)])
    B.finish()
