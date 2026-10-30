"""The Annunciation of Death: while Sieglinde lies senseless on Left and Siegmund keeps watch over her, the
whole pass falls silent. The slate and the dawn drain away into indigo, pale motes drift through it, and the low
strings hold their breath. Then the Wagner tubas (tubas and horns) sound the power of fate (Donington 84), the
two chords of the Annunciation: on the first a pale light gathers over the middle of Porch Front, on the second
Brünnhilde is there, her silver glowing wide over the porch with her gold glints, shield and spear. Only those
about to die can see her.

Fate inevitable (Donington 85), the question that hangs, answers in the horns and tubas; the fate chords come
again a tone higher, each one a slow pulse of her silver, and a pale beam of her gaze reaches down Porch Left
onto Left, to him. Siegmund's blue lifts toward her to his own weary motif (Donington 35a) in the cellos: who
are you? She tells him where he is going. Valhalla (Donington 63) rises in the brass, slow and grand, and over
the porch the battlements of the gods' castle blaze white-gold in the indigo, chord by chord, with the fallen
heroes glinting along them; a second, softer Valhalla with harps, and the castle fades. Then fate again, low:
he must follow her. The scene ends as it began, utterly still: indigo, her silver over the porch, the beam on
him, and Sieglinde's amber faint beside him.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play, melody

CODE = 'WK16'
TITLE = 'The Annunciation of Death'
KIND = 'show'
DESCRIPTION = ('Brünnhilde appears to Siegmund, and only a man who is about to die can see her. '
               'Slowly and gravely she tells him that tomorrow he will fall, and go with her to Valhalla.')
VOICEOVER = ('Everything goes quiet. Siegmund looks up, and sees someone who should not be there. '
             'She has come to tell him he is going to die.')

BEAT = 1.0                                  # a quarter note at 60: slow and grave
T_HUSH = 0.5                                # the pass drains into indigo
T_FATE = [6.0, 21.0, 53.0]                  # the Annunciation chords, three times
TR_FATE = [0, 2, -2]
T_INEV = [15.0, 30.0, 62.0]                 # fate inevitable answers
T_WEARY = 31.5                              # Siegmund: who are you?
T_VAL = [37.5, 45.6]                        # Valhalla, grand and then soft
T_STILL = 68.5
D = 80.0
K = 15
GLINTS = (-24, -9, 10, 23)

SLATE = hexc('#3a3a4a')
DAWN = hexc('#ff9a5a')
DAWNHI = hexc('#ffc890')
INDIGO = hexc('#2a1a5a')
PALE = hexc('#a0b0c0')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
BGOLD = hexc('#ffd060')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')
CASTLE = hexc('#fff0c0')
BLAZE = hexc('#ffe8a0')


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def pass_bed(G):
    """The rocky pass at dawn: slate ridges on the wings and Side, warm light on the porch heights.
    Returns f(T, wings, porch) -> (N,3), T on the shared clock."""
    d, z = G.pd, G.pos[:, 2]
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    ridge = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 170 + 0.35 * np.sin(d / 430)))
    crag = 0.5 + 0.5 * np.cos(2 * np.pi * d / 61 + 2.0 * np.sin(d / 97))
    height = 0.55 + 0.45 * smoothstep(-160, -560, z)

    def f(T, wings=1.0, porch_lvl=1.0):
        cloud = 0.85 + 0.15 * np.cos(2 * np.pi * (d / 900 - T / 40))
        sl = (0.62 + 0.22 * ridge + 0.1 * crag) * cloud * ~porch * wings
        glow = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - T / 25))
        dw = (0.44 + 0.08 * glow) * height * porch * porch_lvl
        return light(SLATE, sl) + light(DAWN, dw) + light(DAWNHI, 0.2 * glow * height * porch * porch_lvl)
    return f


def indigo_bed(G):
    """The hush of fate: indigo over the whole house, slow swells, pale motes drifting. f(T, level) -> (N,3)."""
    d = G.pd
    rng = np.random.default_rng(160)
    motes = rng.uniform(0, G.length, 26)
    speed = rng.uniform(-9, 9, 26)
    phase = rng.uniform(0, 2 * np.pi, 26)

    def f(T, lvl=1.0):
        swell = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 700 - T / 30))
        fr = light(INDIGO, lvl * (0.66 + 0.2 * swell))
        q = (motes + speed * T) % G.length
        a = (0.5 + 0.5 * np.sin(2 * np.pi * T / 5.0 + phase)) ** 2
        g = (a[None, :] * np.exp(-((d[:, None] - q[None, :]) / 9) ** 2)).max(axis=1)
        return fr + light(PALE, lvl * 0.5 * g)
    return f


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=0):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    # the hush: low strings hold their breath, a soft timpani roll
    add(0.0, T_FATE[0] + 0.5, 'D2', 84, 'trem')
    add(0.0, T_FATE[0] + 0.5, 'D1', 76, 'pedal')
    add(T_HUSH + 1.0, T_FATE[0] - T_HUSH - 0.5, 'A2', 58, 'trem')
    add(T_FATE[0] - 2.5, 2.5, 'D2', 70, 'roll')
    # the Annunciation chords, the question that answers them; three times
    for j, (t0, tr) in enumerate(zip(T_FATE, TR_FATE)):
        for t, m, v, d in play('fate', t0, BEAT, tr, (96, 100, 84)[j]):
            add(t, d * 1.02, m, v, 'fate', j)
    for j, t0 in enumerate(T_INEV):
        for t, m, v, d in play('fate_inevitable', t0, BEAT, -12 + (0, 2, -2)[j], (80, 86, 74)[j]):
            add(t, d * 1.02, m, v, 'inev', j)
    add(T_FATE[0] + 4, T_INEV[0] - T_FATE[0], 'Db1', 70, 'pedal')
    # Siegmund: who are you?
    for t, m, v, d in play('siegmund_weary', T_WEARY, 0.75, 0, 84, 'bass'):
        add(t, d, m, v, 'weary')
    # Valhalla: grand, then soft with harps
    for j, t0 in enumerate(T_VAL):
        for t, m, v, d in play('valhalla', t0, BEAT, 0, (100, 76)[j]):
            add(t, d * 1.02, m, v, 'valhalla', j)
    for i, t in enumerate(np.arange(T_VAL[1], T_VAL[1] + 8.0, 0.25)):
        add(t, 0.8, note('Db4') + (0, 5, 8, 12, 17, 12, 8, 5)[i % 8], 70, 'harp', i)
    # the stillness: a held chord, very soft, over a pedal D
    for m in ('D2', 'A2', 'F3'):
        add(T_STILL - 2, D - T_STILL + 2, m, 56, 'pad')
    add(T_STILL, D - T_STILL, 'D1', 64, 'pedal')
    return sorted(N, key=lambda e: e[0])


def choreography(G):
    """Fixed places: Brünnhilde over the middle of Porch Front, Siegmund and Sieglinde on Left."""
    F = nframes(D)
    t = np.arange(F) * DT
    return dict(t=t, brunn=np.full(F, at(G, 'Porch Front', 0.5)), mund=np.full(F, at(G, 'Left', 0.55)),
                linde=np.full(F, at(G, 'Left', 0.7)))


def render(G, seed=16):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    z = G.pos[:, 2]
    bed = pass_bed(G)
    ind = indigo_bed(G)
    C = choreography(G)
    N = compose()
    b, mn, ln = C['brunn'][0], C['mund'][0], C['linde'][0]
    tw = Flicker(rng, G.N, 2.0, 6.0)
    heights = smoothstep(-200, -560, z) * porch

    def ons(*parts):
        return [e for e in N if e[4] in parts]

    def chords(*parts):
        return sorted({e[0] for e in ons(*parts)})

    fate_on = chords('fate', 'inev')
    val_on = [chords('valhalla')[i] for i in range(len(chords('valhalla')))]
    weary_on = chords('weary')
    heroes = rng.uniform(0, 1, G.N) < 0.09

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        hush = smoothstep(T_HUSH, T_FATE[0], t)
        fr = bed(T, 1 - hush, 1 - hush) + ind(T, hush)

        # her coming: the pale gathers on the first chord, she is there on the second
        appear = smoothstep(T_FATE[0], T_FATE[0] + 3.5, t)
        here = smoothstep(T_FATE[0] + 3.6, T_FATE[0] + 5.5, t)
        i = int(np.searchsorted(fate_on, t, side='right')) - 1
        pulse = np.exp(-(t - fate_on[i]) / 1.2) if i >= 0 else 0.0
        fr += light(PALE, (0.55 * appear * (1 - 0.5 * here) + 0.2 * pulse * appear) * np.exp(-((d - b) / 150) ** 2))
        bl = here * (0.78 + 0.18 * pulse)
        fr += light(BRUNN, bl * np.exp(-((d - b) / 18) ** 2) + 0.3 * bl * np.exp(-((d - b) / 90) ** 2))
        fr += light(BRUNN, 0.14 * bl * porch * (0.85 + 0.15 * np.cos(2 * np.pi * T / 8)))
        for j, o in enumerate(GLINTS):
            g = 0.5 + 0.5 * np.sin(2 * np.pi * (0.7 + 0.23 * j) * T + 1.7 * j)
            fr += light(BGOLD, bl * 0.75 * g ** 3 * np.exp(-((d - b - o) / 6) ** 2))
        fr += light(BGOLD, 0.55 * here * np.exp(-((d - b - 16) / 7) ** 2))
        line = smoothstep(b - 46, b - 40, d) * smoothstep(b - 12, b - 18, d)
        fr += light(SPEAR, 0.45 * here * line)

        # her gaze: a pale beam down Porch Left onto Left, to him
        gaze = smoothstep(T_FATE[1], T_FATE[1] + 4.0, t)
        if gaze > 0:
            span = smoothstep(mn - 10, mn + 20, d) * smoothstep(b + 10, b - 30, d)
            ripple = 0.75 + 0.25 * np.cos(2 * np.pi * ((b - d) / 160 - T / 4))
            fr += light(PALE, gaze * (0.3 + 0.15 * pulse) * span * ripple)

        # Valhalla: the battlements blaze over the porch in the indigo, chord by chord
        vin = smoothstep(T_VAL[0] - 0.5, T_VAL[0] + 0.5, t) * (1 - smoothstep(T_VAL[1] + 5.0, T_FATE[2] - 0.5, t))
        if vin > 0:
            j = int(np.searchsorted(val_on, t, side='right')) - 1
            chord = np.exp(-(t - val_on[j]) / 0.7) if j >= 0 else 0.0
            soft = 1 - 0.45 * smoothstep(T_VAL[1] - 0.5, T_VAL[1] + 1.0, t)
            crenel = (np.cos(2 * np.pi * d / 46) > -0.1)
            rise = smoothstep(T_VAL[0], T_VAL[0] + 6.0, t)
            fr += light(CASTLE, vin * soft * (0.45 + 0.35 * rise + 0.25 * chord) * heights * (0.55 + 0.45 * crenel))
            fr += light(BLAZE, vin * soft * 0.4 * chord * np.exp(-((d - b) / (200 + 300 * rise)) ** 2))
            fr += light(BLAZE, vin * soft * 0.25 * (1 - porch) * chord)
            fr += light(BGOLD, vin * soft * 0.7 * heroes * heights * (0.4 + 0.6 * tw(t)))

        # Siegmund, looking up: his blue lifts toward her
        k = int(np.searchsorted(weary_on, t, side='right')) - 1
        say = np.exp(-(t - weary_on[k]) / 0.5) if k >= 0 else 0.0
        sm = 0.66 + 0.1 * smoothstep(T_FATE[1], T_FATE[1] + 6, t) + 0.15 * say
        fr += light(SIEGMUND, sm * np.exp(-((d - mn) / 16) ** 2) + 0.25 * sm * np.exp(-((d - mn) / 60) ** 2))
        blade = smoothstep(mn - 32, mn - 29, d) * smoothstep(mn - 15, mn - 18, d)
        fr += light(STEEL, sm * 0.7 * blade * (0.85 + 0.15 * tw(t)))
        fr += light(HILT, sm * 0.7 * np.exp(-((d - mn + 12) / 3.5) ** 2))
        # Sieglinde, senseless
        sl = 0.352 * (1 - 0.15 * hush)
        fr += light(SIEGLINDE, sl * np.exp(-((d - ln) / 15) ** 2) + 0.25 * sl * np.exp(-((d - ln) / 55) ** 2))
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

    C = choreography(G)
    for name, gain, rev in (('low', 0.18, 0.25), ('tubas', 0.15, 0.45), ('brass', 0.17, 0.4),
                            ('strings', 0.16, 0.35), ('harp', 0.18, 0.5), ('perc', 0.17, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    gong = M.hits('Percussion/gongHit_p*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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

    pb = pan_at(C['brunn'][0])
    pm = pan_at(C['mund'][0])
    lowest = {j: min(e[2] for e in compose() if e[4] == 'fate' and e[5] == j) for j in range(3)}
    for t, d, m, v, part, k in compose():
        if part == 'trem':
            hold('low', trem, m, t, t + d, v, 0.0, rise=0.6, fall=1.5, gain=0.8)
        elif part == 'roll':
            M.add('perc', roll.play(v, dur=d), t, 0.6, pb)
        elif part in ('fate', 'inev'):
            # the Wagner tubas: tubas below, horns above, warm and dark
            if m < note('C3'):
                hold('tubas', tuba, m + (12 if m < note('E2') else 0), t, t + d, v, pb, rise=0.25, fall=1.2, gain=0.9)
            elif m < note('G3'):
                hold('tubas', tbn, m, t, t + d, v - 6, pb, rise=0.25, fall=1.2, gain=0.7)
            else:
                hold('tubas', horn, m, t, t + d, v, pb, rise=0.25, fall=1.2, gain=0.8)
            if part == 'fate' and t - T_FATE[k] < 0.01 and m == lowest[k]:
                M.add('perc', gong.play(80 + 10 * (k == 1)), t, 0.6, pb)
        elif part == 'pedal':
            hold('low', cb, m + 12, t, t + d, v, 0.0, rise=1.5, fall=2.0)
        elif part == 'weary':
            M.add('strings', vc.play(m + 12, v, dur=d * 1.05, release=0.4), t, 1.0, pm)
        elif part == 'valhalla':
            s = tuba if m < note('C3') else (tbn if m < note('C4') else (horn if k else tpt))
            g = 0.75 if s is not tpt else 0.5
            M.add('brass', s.play(m, v, dur=d * 1.05, release=0.8), t, g, pb + (0.3 if m % 2 else -0.3) * (m > note('C3')))
        elif part == 'harp':
            M.add('harp', harp.play(m, v), t, 0.8, -0.6 + 1.2 * ((k * 5) % 8) / 7)
        elif part == 'pad':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v, 0.0, rise=2.0, fall=1.5, gain=0.7)
