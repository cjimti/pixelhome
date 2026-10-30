"""Heil dir, Sonne!: the summit of the rock in the last of the night, the fire low round the porch, Brünnhilde a
sleeping silver glow at the summit and Siegfried, emerald, beside her at Porch Front 0.42.

He bends to kiss her: a thread of emerald reaches across to the silver, and where they touch the whole house
flashes. She wakes. There is no Commons example for her awakening, so it is composed: harp arpeggios climbing
out of E minor into C major under four brass chords, each louder and higher than the last, and each one a wave
of sunrise rolling out from the summit to both ends of the house, rose at its front, gold behind, while the
night, the storm and the fire drain away and the sky comes up rose, gold and blue on every run. Her glow
becomes Brünnhilde herself, silver white with gold glints, sitting up at Porch Front 0.55.

"Heil dir, Sonne! Heil dir, Licht!": her greeting to the sun, composed for horns and violins, each phrase ending
in a burst of gold out from her. Then her own motif (Donington 88) on the horns rolls silver and gold waves out
over the house, and Transformation (91), twice, sweeps the whole roofline through rose, gold and sky blue, a
band of colour racing end to end on every note. Siegfried answers with his motif (53), emerald waves from him,
and the two of them stand in the full sunrise.

compose() holds every note; stage(), sky(), fire() and figure() are the rock and the sky, shared word for word by
Act III's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise, colormap
from pixelhome.leitmotifs import play

CODE = 'SF28'
TITLE = 'Heil dir, Sonne!'
KIND = 'show'
DESCRIPTION = ('Siegfried kisses the sleeping Brünnhilde and she wakes. Night turns to sunrise across the whole '
               'house as she greets the sun, the light and the shining day.')
VOICEOVER = ('He kisses her, and she wakes. '
             'Hail to the sun, she sings. Hail to the light.')

K = 5                                       # this scene's place on Act III's shared clock: T = t + 80 K
T_REACH = 1.0                               # he bends to kiss her
T_KISS = 4.5
T_CHORDS = [7.0, 10.0, 13.0, 16.5]          # the awakening: four brass chords, rising
CHORDS = [('E3', 'G3', 'B3', 'E4'), ('C3', 'G3', 'C4', 'E4', 'G4'), ('E3', 'C4', 'E4', 'G4', 'C5'),
          ('C2', 'C3', 'G3', 'E4', 'G4', 'C5')]
T_HEIL = [21.0, 26.5]                       # "Heil dir, Sonne! Heil dir, Licht!"
HEIL = [[(0, 1.5, 'G4'), (1.5, 0.5, 'C5'), (2, 2.5, 'E5')],
        [(0, 1.0, 'A4'), (1.0, 0.5, 'C5'), (1.5, 0.5, 'E5'), (2, 3.0, 'G5')]]
HBEAT = 0.8
T_BRUNN = 32.5                              # her motif on the horns
T_TRANS = [41.0, 50.0]                      # Transformation, twice
T_SIEG = [60.0, 64.5]                       # Siegfried answers
D = 80.0

STORM = hexc('#1a2ab0')
CLOUD = hexc('#4a6aff')
RAIN = hexc('#a8bcdc')
BOLT = hexc('#e8f0ff')
ROCK = hexc('#38468a')
DUSK = hexc('#7a40d0')
RED, ORANGE, AMBER = hexc('#ff2000'), hexc('#ff5000'), hexc('#ffb020')
FIRE = colormap([(0.0, hexc('#300400')), (0.3, RED), (0.55, ORANGE), (0.8, AMBER), (1.0, hexc('#fff0b0'))])
SUNRISE = colormap([(0.0, hexc('#ff4080')), (0.5, hexc('#ffc020')), (1.0, hexc('#40a0ff'))])
SILVER = hexc('#f4f8ff')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
MOSS = hexc('#30c020')
EARTH = hexc('#3a2410')
ERDA_HI = hexc('#60ff30')
TWILIGHT = hexc('#a0207a')
EMERALD = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
GLINT = hexc('#ffd060')
ROSE = hexc('#ff4080')
SUN = hexc('#ffc020')
SKYBLUE = hexc('#40a0ff')
WHITE = hexc('#ffffff')

SUMMIT = dict(storm=0.25, rock=0.35, fire=0.4, wide=0.0, dawn=0.0, sleeper=0.7)
DAWN = dict(storm=0.0, rock=0.35, fire=0.15, wide=0.0, dawn=0.75, sleeper=0.0)
SIEG_AT, BRUNN_AT = 0.42, 0.55              # their places on Porch Front at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Brünnhilde's rock and the sky as profiles over the house: the porch is the rock, the summit the middle of
    Porch Front; the wings and Side are sky."""
    d = G.pd
    rng = np.random.default_rng(1871)       # the same clouds and rain in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    summit = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, summit=summit, porch=porch, sky=~porch,
        crag=porch * (0.7 + 0.3 * smooth_noise(rng, d, 40.0)),
        db=np.abs(d - summit),
        rain=Flicker(rng, G.N, 4.0, 11.0),
        fl=Flicker(rng, G.N, 4.0, 11.0),
        jag=rng.uniform(0.3, 1.0, G.N),
    )


def heat(d, T):
    """Flame heat along the roofline (0..1): tongues of several sizes licking both ways."""
    h = (0.45 + 0.24 * np.sin(2 * np.pi * (d / 173 - 0.53 * T)) + 0.2 * np.sin(2 * np.pi * (d / 109 + 0.71 * T) + 1.3)
         + 0.13 * np.sin(2 * np.pi * (d / 67 - 1.37 * T) + 2.1) + 0.09 * np.sin(2 * np.pi * (d / 41 + 1.9 * T) + 0.4))
    swell = 0.75 + 0.25 * np.sin(2 * np.pi * (d / 410 + 0.23 * T)) * np.sin(2 * np.pi * (d / 260 - 0.31 * T) + 0.7)
    return np.clip((h * swell - 0.15) * 1.5, 0, 1)


def fire(S, T, ring, wide, boost=0.0):
    """The magic fire: `ring` round the rock (the porch, leaving the summit clear), `wide` out over the sky."""
    q = np.clip(heat(S['d'], T) + 0.18 * S['fl'](T) + 0.3 * boost, 0, 1)
    clear = 1 - 0.8 * np.exp(-(S['db'] / 42) ** 2)
    lvl = (ring * S['porch'] + wide * S['sky']) * clear
    return light(FIRE(q), lvl * (0.45 + 0.7 * q))


def sky(S, T, lv):
    """The sky and the rock at shared time T with levels lv (storm, rock, fire, wide, dawn, sleeper)."""
    d = S['d']
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.05 * T)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.09 * T) + 1.1)
    st = STORM + (CLOUD - STORM) * u[:, None]
    fr = light(st, lv['storm'] * (0.7 + 0.3 * u) * S['sky'])
    fr += light(RAIN, 0.6 * lv['storm'] * S['sky'] * np.clip(S['rain'](T) - 1.0, 0, None) ** 2)
    rk = ROCK + (DUSK - ROCK) * (0.25 + 0.45 * u)[:, None]
    fr += light(rk, lv['rock'] * S['crag'])
    fr += light(SUNRISE(np.clip(0.15 + 0.7 * u + 0.15 * np.sin(0.2 * T), 0, 1)), lv['dawn'] * (0.75 + 0.25 * u))
    fr += fire(S, T, lv['fire'], lv['wide'])
    fr += light(SILVER, lv['sleeper'] * np.exp(-(S['db'] / 22) ** 2))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the sky, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: emerald, with a white-hot head."""
    fr = figure(fr, S, p, EMERALD, lvl, w)
    return fr + light(HEAD, 0.8 * lvl * np.exp(-((S['d'] - p) / (0.35 * w)) ** 2))


def heroine(fr, S, p, lvl, T, w=16.0):
    """Brünnhilde awake: silver white, with gold glints round her."""
    fr = figure(fr, S, p, SILVER, lvl, w)
    tw = 0.5 + 0.5 * np.sin(2 * np.pi * (S['d'] / 23 + 1.3 * T)) * np.sin(2 * np.pi * (S['d'] / 37 - 0.9 * T))
    return fr + light(GLINT, 0.8 * lvl * tw ** 3 * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for m in ('E2', 'B2'):
        add(0.0, T_CHORDS[0], m, 56, 'night')
    for j, m in enumerate(('B4', 'E5', 'Ab5')):
        add(T_KISS + 0.1 * j, 2.0, m, 70, 'kiss')
    for k, (t0, ch) in enumerate(zip(T_CHORDS, CHORDS)):
        nxt = T_CHORDS[k + 1] if k + 1 < len(T_CHORDS) else T_HEIL[0] - 0.5
        for m in ch:
            add(t0, nxt - t0 + 0.3, m, 88 + 10 * k, 'chord', k)
        arp = ('E3', 'G3', 'B3', 'E4', 'G4', 'B4') if k == 0 else ('C3', 'E3', 'G3', 'C4', 'E4', 'G4', 'C5')
        for j in range(int((nxt - t0) / 0.14)):
            add(t0 + 0.14 * j, 0.6, arp[j % len(arp)], 70 + 4 * k, 'harp')
    for k, t0 in enumerate(T_HEIL):
        for b, dd, m in HEIL[k]:
            add(t0 + b * HBEAT, dd * HBEAT, m, 104 + 6 * k, 'heil', k)
        for m in (('C3', 'G3', 'E4'), ('F3', 'C4', 'A4'))[k]:
            add(t0, 4.5 * HBEAT, m, 80, 'heilbed', k)
    for t, m, v, d in play('brunnhilde', T_BRUNN, 0.75, 0, 108):
        add(t, d, m, v, 'brunn')
    for k, t0 in enumerate(T_TRANS):
        for t, m, v, d in play('transformation', t0, 0.55, -5, 100 + 8 * k):
            add(t, d, m, v, 'trans', k)
        for m in ('C3', 'G3', 'C4'):
            add(t0, 8.0, m, 74, 'transbed', k)
    for k, t0 in enumerate(T_SIEG):
        for t, m, v, d in play('siegfried', t0, 0.75, -12, 110 + 6 * k):
            add(t, d, m, v, 'sieg', k)
    for m in ('C2', 'G2', 'C3', 'E3', 'G3', 'C4'):
        add(T_SIEG[1] + 3.0, D - T_SIEG[1] - 3.0, m, 70, 'final')
    for j in range(int((D - T_SIEG[1] - 3.0) / 0.2)):
        add(T_SIEG[1] + 3.0 + 0.2 * j, 0.8, ('C4', 'E4', 'G4', 'C5', 'G4', 'E4')[j % 6], 62, 'harp', 9)
    return sorted(N, key=lambda e: e[0])


def render(G, seed=28):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, summit = S['d'], S['summit']
    L = d.max()
    reach = max(summit, L - summit)
    N = compose()
    heil_ends = [t0 + HEIL[k][-1][0] * HBEAT for k, t0 in enumerate(T_HEIL)]
    heil_on = np.array(sorted({e[0] for e in N if e[4] == 'heil'}))
    brunn = np.array(sorted({e[0] for e in N if e[4] == 'brunn'}))
    trans = [e for e in N if e[4] == 'trans']
    sieg = np.array(sorted({e[0] for e in N if e[4] == 'sieg'}))
    ps = at(G, 'Porch Front', SIEG_AT)
    pb0, pb1 = summit, at(G, 'Porch Front', BRUNN_AT)
    hue = np.linspace(0, 1, len(trans))

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i]) if i >= 0 and t - ts[i] < span else None

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        # night drains away chord by chord into the sunrise
        up = np.interp(t, [T_CHORDS[0], T_CHORDS[1], T_CHORDS[2], T_CHORDS[3], T_CHORDS[3] + 3],
                       [0.0, 0.3, 0.55, 0.8, 1.0])
        lv = {k: SUMMIT[k] + (DAWN[k] - SUMMIT[k]) * up for k in SUMMIT}
        wake = smoothstep(T_CHORDS[1], T_CHORDS[3] + 2, t)
        lv['sleeper'] = SUMMIT['sleeper'] * (1 - wake)
        mid = smoothstep(T_HEIL[0] - 1, T_HEIL[0] + 1, t) * (1 - smoothstep(T_SIEG[1] + 3, T_SIEG[1] + 9, t))
        lv['dawn'] *= 1 - 0.5 * mid             # the bed steps back so the waves over it stand out
        fr = sky(S, T, lv)

        # the kiss: a thread of emerald reaching to her, and a flash where they touch
        if T_REACH <= t < T_KISS + 0.2:
            u = smoothstep(T_REACH, T_KISS, t)
            tip = ps + (summit - ps) * u
            span = (d >= ps - 4) & (d <= tip + 4)
            fr += light(EMERALD, 0.9 * span * (0.6 + 0.4 * u))
        if T_KISS <= t < T_KISS + 2.5:
            a = t - T_KISS
            fr += light(WHITE, min(1.0, 0.9 * np.exp(-a / 0.12)) * np.exp(-((d - summit) / 40) ** 2))
            fr += light(EMERALD, 0.8 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - summit) - 1500 * a) / 150) ** 2))
            fr += light(SILVER, 0.7 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - summit) - 1100 * a) / 150) ** 2))

        # each awakening chord: a wave of sunrise out from the summit to both ends, rose at the front, gold behind
        for k, t0 in enumerate(T_CHORDS):
            a = t - t0
            if 0 <= a < 3.5:
                front = reach * min(1.0, a / 1.6)
                dist = np.abs(d - summit)
                band = np.exp(-((dist - front) / 220) ** 2)
                behind = smoothstep(front + 40, front - 200, dist) * np.exp(-a / 1.6)
                g = 0.7 + 0.1 * k
                fr += light(ROSE, g * band) + light(SUN, g * 0.8 * behind)
                fr += light(WHITE, (0.4 + 0.15 * k) * np.exp(-a / 0.12) * np.exp(-(dist / 80) ** 2))

        # "Heil dir, Sonne!": each note lights her brighter, each phrase ends in a burst of gold out from her
        pb = pb0 + (pb1 - pb0) * smoothstep(T_CHORDS[2], T_HEIL[0], t)
        a = recent(heil_on, t, 1.0)
        if a is not None:
            fr += light(SUN, 0.6 * np.exp(-a / 0.4) * np.exp(-((d - pb) / 140) ** 2))
        for te in heil_ends:
            a = t - te
            if 0 <= a < 3.0:
                fr += light(SUN, 0.95 * np.exp(-a / 1.2) * np.exp(-((np.abs(d - pb) - 1400 * (1 - np.exp(-a / 0.7))) / 260) ** 2))
                fr += light(GLINT, 0.6 * np.exp(-a / 0.8) * S['porch'])

        # her motif: silver and gold waves out over the house
        a = recent(brunn, t, 2.5)
        if a is not None:
            r = 1400 * (1 - np.exp(-a / 0.7))
            fr += light(SILVER, 0.95 * np.exp(-a / 1.1) * np.exp(-((np.abs(d - pb) - r) / 260) ** 2))
            fr += light(GLINT, 0.6 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - pb) - 0.8 * r) / 100) ** 2))

        # Transformation: a band of colour racing end to end on every note, rose to gold to sky blue
        for j, (t0, dur, m, v, part, k) in enumerate(trans):
            a = t - t0
            if 0 <= a < 1.8:
                c = SUNRISE(np.array([hue[j]]))[0]
                x = (a / 1.4) * L if (j + k) % 2 == 0 else L - (a / 1.4) * L
                fr += light(c, 1.0 * np.exp(-a / 1.3) * np.exp(-((d - x) / 400) ** 2))

        # Siegfried answers: emerald waves out from him
        a = recent(sieg, t, 2.0)
        if a is not None:
            r = 1500 * (1 - np.exp(-a / 0.6))
            fr += light(EMERALD, 1.0 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - ps) - r) / 280) ** 2))
        final = smoothstep(T_SIEG[1] + 3, T_SIEG[1] + 6, t)
        fr += light(SKYBLUE, 0.25 * final * S['sky'] * (0.6 + 0.4 * np.sin(2 * np.pi * (d / 700 - 0.08 * t))))

        # the two of them
        fr = hero(fr, S, ps, 0.85)
        if wake > 0:
            fr = heroine(fr, S, pb, 0.9 * wake, T)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    for name, gain, rev in (('low', 0.26, 0.25), ('brass', 0.28, 0.32), ('harp', 0.22, 0.4), ('strings', 0.24, 0.35),
                            ('perc', 0.24, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    swell = M.hits('Percussion/susCymb1-cresc-Median*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=1.5, fall=1.5, gain=1.0):
        """A note sustained from t0 to t1 (and released over `fall`): overlapping windows of its sample."""
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            env = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * env, t, gain, pan)
            t += step

    her = pan_at(at(G, 'Porch Front', BRUNN_AT))
    him = pan_at(at(G, 'Porch Front', SIEG_AT))
    for t, d, m, v, part, k in compose():
        if part == 'night':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=2.0, fall=2.0, gain=0.5)
        elif part == 'kiss':
            M.add('harp', glock.play(m - 12, v), t, 0.5, her)
            M.add('harp', harp.play(m - 12, v), t, 0.8, her)
        elif part == 'chord':
            s = tuba if m < note('C3') else tbn if m < note('C4') else horn if m < note('G4') else tpt
            mm = m if s in (tuba, tbn) else m - 12
            hold('brass', s, mm, t, t + d, v, 0.0, rise=0.25, fall=1.2, gain=0.7)
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.7, her if k != 9 else 0.0)
        elif part == 'heil':
            hold('brass', horn, m - 12, t, t + d, v, her, rise=0.1, fall=0.8, gain=0.8)
            hold('strings', vn, m, t, t + d, v - 10, her, rise=0.1, fall=0.8, gain=0.6)
        elif part == 'heilbed':
            hold('strings', vc, m, t, t + d, v, 0.0, rise=0.3, fall=1.0, gain=0.6)
        elif part == 'brunn':
            if m >= note('C4'):
                hold('brass', horn, m - 12, t, t + d, v, her, rise=0.05, fall=0.6, gain=0.8)
            else:
                M.add('low', tbn.play(m, v - 10, dur=d * 1.05, release=0.3), t, 0.8, her)
        elif part == 'trans':
            hold('strings', vn, m, t, t + d, v, 0.0, rise=0.1, fall=0.8, gain=0.7)
            if d >= 1.0:
                M.add('brass', horn.play(m - 12, v - 16, dur=d * 1.05, release=0.4), t, 0.5, 0.0)
        elif part == 'transbed':
            hold('low', vc, m, t, t + d, v, 0.0, rise=0.5, fall=1.5, gain=0.55)
        elif part == 'sieg':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.9, him)
            M.add('brass', tpt.play(m, v - 20, dur=d * 1.1, release=0.3), t, 0.4, him)
        elif part == 'final':
            s = tuba if m < note('C3') else tbn if m < note('C4') else horn
            hold('brass', s, m if s is not horn else m - 12, t, t + d, v, 0.0, rise=1.0, fall=1.5, gain=0.6)
    for k, t0 in enumerate(T_CHORDS):
        M.add('perc', timp.play(90 + 10 * k, pitch=-4), t0, 0.8)
        if k == len(T_CHORDS) - 1:
            M.add('perc', crash.play(118), t0, 0.8)
    M.add('perc', swell.play(100), T_CHORDS[0] - 3.0, 0.5)
    M.add('perc', roll.play(100, pitch=-4, dur=3.0), T_CHORDS[3] - 3.0, 0.5)
    for t0 in T_TRANS:
        M.add('perc', crash.play(96), t0, 0.5)
