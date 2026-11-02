"""The Lord Passed By: on Horeb a wind tears down every run, the whole house quakes, fire takes it, and the Lord is in
none of them; then, in the dark, one faint point of silver on Porch Front widens into calm light over everything.

The house is a dim night slate throughout, Left and Right never dark. There is no figure for God and none for Elijah:
the elements are the scene. The wind is hard white-blue streaks running out from the porch along every run, thicker
as the orchestra swells, a great gust sweeping the whole roofline on "God the Lord passed by"; it drops dead in the
written silence before "But yet the Lord was not in the tempest", sung unaccompanied while the last dust settles.
The earthquake is the house shaking segment against segment: a cracked rock texture on every run pushed back and
forth, neighbouring runs out of step, jolted on each chord, never flashing. Then the fire, red to gold to white along
everything, rising with "there came a fire" and flaring on every syllable of "But yet the Lord was not in the fire"
(sung in octaves) until it collapses into embers on the held note. Each time Porch Front, heaven, stays empty.

Then E major, pianissimo, the house almost dark: "a still small voice", the whole chorus on one B, and at "still" a
single faint silver point appears in the middle of Porch Front. It slowly widens along Porch Front, out down the porch
runs and over the wings, so that by "onward came the Lord" calm silver light lies over the whole house, which is how
EL21 (Holy, Holy, Holy) begins.

The music is Mendelssohn's own: No. 34, transcribed from the Novello octavo vocal score into
the_lord_passed_by.musicxml and timed by scripts/score_excerpt.py at the marked Allegro molto (minim 100), its
fermatas doubled: the wind (bars 1-15), "not in the tempest" (30-35), the sea upheaved (45-47), "not in the
earthquake" (64-71), "there came a fire" (74-77) and "not in the fire" to "onward came the Lord" (110-134). The
chorus is played on the orchestra (strings with winds and horns, trombones in the octaves of "not in the fire",
flutes, clarinets and soft horns on the still small voice), the accompaniment orchestrated from the piano reduction;
a production adds the wind, the earthquake's rumble and blows, and the fire's roar, and nothing at all after it.

render() and score() both read the notes and bars from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL20'
TITLE = 'The Lord Passed By'
KIND = 'show'
DESCRIPTION = ("On Horeb a wind tears along every run, the house quakes, fire takes it, and the Lord is in none of "
               "them. Then one faint silver point appears in the dark, and widens over everything.")
VOICEOVER = 'Not in the wind. Not in the earthquake. Not in the fire.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
SYLL = np.array(sorted({round(n[0], 3) for n in SUNG}))

# the scene's spans, from the bars
T_BEHOLD = BAR[6]                 # "Behold" (the wind is at its height just before)
T_PASSED = BAR[8]                 # "Lord passed by", held
T_WIND1 = BAR[10]                 # "And a mighty wind..."
T_CALM1 = BAR[30]                 # the wind drops: "Lord." and the written silence
T_NOT1 = BAR[31]                  # "But yet the Lord was not in the tempest"
T_QUAKE = BAR[45]                 # "And the sea was upheaved"
T_NOT2 = BAR[66]                  # "But yet the Lord was not in the earthquake"
T_FIRE = BAR[74]                  # "And after the earthquake there came a fire"
T_NOT3 = BAR[110]                 # "But yet the Lord was not in the fire"
T_HOLD3 = BAR[114]                # the held D sharp: the fire dies
T_STILL = BAR[115]                # E major, pianissimo
T_POINT = BAR[119]                # "still small voice": the point
T_IN = BAR[127]                   # "And in that still voice"
T_LORD = BAR[131]                 # "onward came the Lord"

NIGHT = hexc('#3a4c80')
WIND = hexc('#cfe2ff')
GUST = hexc('#ffffff')
DUST = hexc('#6a6058')
ROCK = hexc('#5a3216')
CRACK = hexc('#ff5010')
RED = hexc('#ff3000')
GOLD = hexc('#ffc040')
WHITE = hexc('#fff6e0')
EMBER = hexc('#a02000')
SILVER = hexc('#d8ecff')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def chord_hits(t0, t1, least=3):
    """Onsets in [t0, t1) where the accompaniment strikes least or more notes at once."""
    on = {}
    for n in ORCH:
        if t0 <= n[0] < t1:
            on[round(n[0], 3)] = on.get(round(n[0], 3), 0) + 1
    return np.array(sorted(t for t, k in on.items() if k >= least))


def loudness(t0, t1):
    """The accompaniment's loudness through [t0, t1): (times, 0..1), from velocities and how many notes sound."""
    ts = np.arange(t0, t1 + DT, 0.1)
    v = np.zeros_like(ts)
    for n in ORCH:
        if n[0] < t1 and n[0] + n[1] > t0:
            a, b = np.searchsorted(ts, n[0]), np.searchsorted(ts, n[0] + n[1])
            v[a:b] += n[3] / 127.0
    return ts, np.clip(v / 6.0, 0, 1)


def render(G, seed=34):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p0, p1 = span(G, 'Porch Front')
    centre = 0.5 * (p0 + p1)
    s_out = np.abs(d - centre)                     # distance out from heaven's middle, along the roofline
    side = np.sign(d - centre)
    heaven = G.seg_of == 'Porch Front'
    names = [n for n, _ in G.path_segments()]
    seg_k = np.array([names.index(s) for s in G.seg_of])

    # the wind: streaks out along every run, more and brighter as the orchestra swells
    lt, lv = loudness(0, T_CALM1)
    streaks = []
    t = 0.0
    while t < T_CALM1:
        lev = float(np.interp(t, lt, lv))
        rate = 8 + 40 * lev                         # streaks a second
        t += rng.exponential(1.0 / rate)
        streaks.append((t, rng.choice([-1, 1]), rng.uniform(0, 300), rng.uniform(900, 1700),
                        rng.uniform(40, 110), 0.5 + 0.5 * lev))
    st = np.array(streaks)
    wind_hits = chord_hits(T_WIND1, T_CALM1)

    # the earthquake: a cracked texture on every run, shifted to and fro, neighbouring runs out of step
    tex = smooth_noise(rng, d, 26.0, octaves=3)
    cracks = np.clip((np.abs(smooth_noise(rng, d, 40.0, octaves=2)) < 0.12) * 1.0, 0, 1)
    quake_hits = chord_hits(T_QUAKE, T_NOT2, least=2)
    phase = rng.uniform(0, 2 * np.pi, len(names)) + np.pi * (np.arange(len(names)) % 2)

    # the fire
    flick = Flicker(rng, G.N, 2.0, 9.0)
    lick = Flicker(rng, G.N, 0.6, 2.2)
    fire_syll = SYLL[(SYLL >= T_NOT3) & (SYLL < T_HOLD3)]
    tongues = smooth_noise(rng, d, 30.0, octaves=2)
    tongues2 = smooth_noise(rng, d, 55.0, octaves=2)

    def last(arr, t, tau, span_=1.5):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span_ else 0.0

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        # the night: never dark; heaven a shade darker while it is empty
        night = 0.3 if t < T_STILL else 0.3 - 0.08 * smoothstep(T_STILL, T_STILL + 2.0, t)
        fr += light(NIGHT, night * (1 - 0.4 * heaven * (t < T_POINT)) * np.ones(G.N))

        if t < T_CALM1 + 0.6:                      # the wind
            drop = 1 - smoothstep(T_CALM1, T_CALM1 + 0.6, t)
            w = np.zeros(G.N)
            act = st[(st[:, 0] <= t) & (st[:, 0] > t - 2.0)]
            for t0, sd, s0, v, ln, b in act:
                head = s0 + v * (t - t0)
                on = (side == sd) | (s_out < 12)
                behind = head - s_out                 # > 0 behind the head: a tail; < 0 ahead: a sharp front
                prof = np.where(behind >= 0, np.exp(-np.clip(behind, 0, None) / ln), np.exp(-(behind / 8) ** 2))
                w += on * b * prof
            gust = last(wind_hits, t, 0.25) * 0.35 if t >= T_WIND1 else 0.0
            lev = float(np.interp(t, lt, lv))
            air = 0.5 + 0.5 * np.sin(0.018 * s_out - 9.0 * t) * np.sin(0.007 * s_out - 4.0 * t + 1.0)
            fr += light(WIND, np.clip(0.95 * w + gust + (0.15 + 0.35 * lev) * air, 0, 1) * drop * (1 - 0.6 * heaven))
            fr += light(DUST, 0.3 * drop * (1 - heaven))
            # "God the Lord passed by": one great gust sweeping the whole house, left to right
            if T_PASSED <= t < T_WIND1:
                u = (t - T_PASSED) / (T_WIND1 - T_PASSED)
                head = -200 + u * (G.length + 400)
                g = np.exp(-((d - head) / 160) ** 2) + 0.4 * np.exp(-np.clip(head - d, 0, None) / 500) * (d < head)
                fr += light(GUST, 0.8 * g * (1 - 0.7 * heaven))
        if T_CALM1 <= t < T_QUAKE + 0.5:           # "not in the tempest": the dust settles, a breath on each syllable
            k = 1 - smoothstep(T_NOT1, T_QUAKE, t)
            fr += light(DUST, (0.25 + 0.15 * last(SYLL, t, 0.4)) * k * (1 - heaven))

        if T_QUAKE <= t < T_FIRE + 0.8:            # the earthquake
            grow = smoothstep(T_QUAKE, T_QUAKE + 1.5, t)
            calm = 1 - 0.75 * smoothstep(T_NOT2, T_NOT2 + 3.0, t)      # aftershocks under "not in the earthquake"
            fade = 1 - smoothstep(T_FIRE, T_FIRE + 0.8, t)
            jolt = last(quake_hits, t, 0.18)
            amp = (14 + 24 * jolt) * grow * calm
            shift = amp * np.sin(2 * np.pi * 3.2 * t + phase[seg_k])
            tx = np.interp(d + shift, d[G.path], tex[G.path])
            cr = np.interp(d + shift, d[G.path], cracks[G.path])
            lev = grow * calm * fade * (1 - 0.8 * heaven)
            rock = 0.5 + 0.35 * np.sin(2 * np.pi * 2.4 * t + phase[seg_k])          # run against run
            fr += light(ROCK, (0.45 + 0.25 * tx + 0.25 * jolt) * (0.55 + 0.45 * rock) * lev)
            fr += light(CRACK, (0.7 + 0.3 * jolt) * cr * (0.4 + 0.6 * rock) * lev)

        if T_FIRE <= t < T_STILL + 0.6:            # the fire
            rise = smoothstep(T_FIRE, T_FIRE + 3.5, t)
            flare = last(fire_syll, t, 0.35) if T_NOT3 <= t < T_HOLD3 else 0.0
            die = 1 - smoothstep(T_HOLD3, T_STILL, t)
            tongue = np.interp((d * 1.0 + 160 * t) % G.length, d[G.path], tongues[G.path])
            tongue2 = np.interp((d * 1.0 - 110 * t) % G.length, d[G.path], tongues2[G.path])
            heat = np.clip((0.6 + 0.4 * tongue + 0.3 * tongue2 + 0.12 * flick(t)) * rise * (0.8 + 0.4 * flare),
                           0, 1.3)
            lev = die * (1 - 0.5 * heaven)
            fr += light(RED, 0.95 * np.clip(heat, 0, 1) * lev)
            fr += light(GOLD, 0.85 * np.clip(heat - 0.4, 0, 1) * lev)
            fr += light(WHITE, 0.8 * np.clip(heat - 0.85, 0, 1) * lev)
            ember = smoothstep(T_HOLD3, T_HOLD3 + 1.0, t) * (1 - smoothstep(T_STILL, T_STILL + 0.6, t))
            fr += light(EMBER, 0.5 * ember * (0.6 + 0.4 * lick(t)) * (1 - heaven))

        if t >= T_POINT:                           # the still small voice
            a = t - T_POINT
            point = smoothstep(0, 1.5, a)
            w = 2.0 + 30 * smoothstep(0, T_IN - T_POINT, a) + 240 * smoothstep(T_IN - T_POINT, D - T_POINT, a) ** 1.5
            reach = np.exp(-(s_out / w) ** 2)
            spread = smoothstep(T_LORD - 2.0, D, t)                   # by "onward came the Lord", everywhere
            lev = 0.45 * point * reach + 0.42 * spread
            fr += light(SILVER, np.clip(lev, 0, 0.55))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Mendelssohn's chorus and accompaniment on the orchestra; the wind under the first part, a rumble and blows
    under the earthquake, the fire's roar; then nothing but the music."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.45)

    def size(t):
        if t < T_CALM1:
            return 0.9
        if t < T_FIRE:
            return 0.6
        if t < T_STILL:
            return 1.0
        return 0.3

    def role(t, d, m, v, hand):
        if t >= T_STILL:                       # the still small voice: soft strings, no brass
            return [('violins' if m >= 55 else 'violas', 0, -2, 0.6)] if hand == 0 else \
                [('cellos', 0, 0, 0.65), ('basses', -12 if m >= 40 else 0, -8, 0.45)]
        return None
    o.tutti(tidy(ORCH), size=size, role=role, pan=lambda t, m: 0.25 * (2 * (m - 40) / 50 - 1))

    def parts(t):
        if T_NOT3 <= t < T_STILL:              # "not in the fire", in octaves: brass and strings
            return {'S': [('trumpets', 0, -6, 0.4), ('violins', 0, -4, 0.5)], 'A': [('horns', 0, 0, 0.5)],
                    'T': [('trombones', 0, 0, 0.5), ('cellos', 0, -4, 0.45)], 'B': [('trombones', 0, -4, 0.4)]}
        if t >= T_STILL:                       # the still small voice
            return {'S': [('flutes', 0, 4, 0.7), ('violins', 0, -6, 0.4)], 'A': [('clarinets', 0, 2, 0.6)],
                    'T': [('horns', 0, -4, 0.55)], 'B': [('bassoons', 0, 0, 0.55), ('cellos', 0, -8, 0.4)]}
        return {'S': [('violins', 0, -2, 0.5), ('oboes', 0, -12, 0.3)], 'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -12, 0.3)],
                'T': [('horns', 0, -2, 0.55)], 'B': [('cellos', 0, 0, 0.55), ('bassoons', 0, -10, 0.35)]}

    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts(t)[who]:
            o.play(section, m + tr, t, d, v + dv, 0.0, g)

    # the wind, rising with the orchestra, dropping dead at the silence
    lt, lv = loudness(0, T_CALM1)
    o.wind(0.0, T_CALM1 + 0.5, level=lambda tt: 0.35 + 0.65 * np.interp(tt, lt, lv),
           pan=lambda tt: 0.6 * np.sin(tt * 0.7))
    # the earthquake: a long low rumble, a blow on each chord
    t = T_QUAKE
    k = 0
    while t < T_NOT2 + 2.0:                  # the ground rolling, again and again, out of step across the house
        o.thunder(t, near=0.3 if t < T_NOT2 else 0.1, pan=[-0.6, 0.5, -0.1, 0.7, -0.4][k % 5], gain=2.0, seed=40 + k)
        t += 1.6
        k += 1
    o.boom(T_QUAKE, pan=-0.3, gain=1.0)
    for k, th in enumerate(chord_hits(T_QUAKE, T_NOT2, least=2)[::2]):
        o.hit('timpani', th, 118, pitch=-6, gain=0.6, pan=pan_at(400 + 300 * (k % 5)), fx=True)
    o.boom(BAR[64], pan=0.4, gain=0.7)
    o.thunder(BAR[66], near=0.1, pan=0.2, gain=0.5)
    # the fire, roaring up and flaring with the octaves, dying on the held note
    o.fire(T_FIRE, T_STILL - 0.4, level=lambda tt: 0.4 + 0.6 * smoothstep(T_FIRE, T_FIRE + 3.0, tt) *
           (1 - 0.8 * smoothstep(T_HOLD3, T_STILL, tt)), pan=0.0, crackle=14)
    o.effects([(0, -6), (T_BEHOLD, -9), (T_WIND1, -7), (T_NOT1, -14), (T_QUAKE - 0.1, -14), (T_QUAKE, 0),
               (T_NOT2, -8), (T_FIRE, -5), (T_NOT3, -8), (T_STILL, -30)])
