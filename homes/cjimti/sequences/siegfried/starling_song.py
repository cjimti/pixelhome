"""The Starling Song: Mime whines his nursery song of how he raised the boy, "Als zullendes Kind zog ich dich auf",
and a broad wash of sulphur yellow rocks back and forth across the whole house like a cradle, pulsing on every
note. Then Siegfried has had enough: "So muß ich dich fassen!" He seizes Mime by the throat, emerald closing round
the yellow, a surge racing out from the two of them on every bar while Mime shakes. Mime fumbles for the mother's
name, a yellow shudder at every chord, and gives in: "Sieglinde mochte sie heißen", and hearth amber floods Right;
then the father, and Wälsung blue rolls out over Left and Side, until "Erschlagen sei er": Siegfried lets Mime
go, blue and amber run back together onto the porch and flare there as emerald.

The music is Wagner's own: Act I, bars 508 to 532, 914 to 946 and 1046 to 1066, as Solti's 1958 Vienna
Philharmonic recording takes them. The orchestra's notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py); the reduction has no voices, so Mime's song comes from the printed vocal score (Schirmer 1914,
archive.org 31761034115105, pp. 21-22) and is played as he sings it, on clarinet and bassoon with an oboe an octave
above, over the orchestra's soft sighing chords (violas and horns) and its rocking (harp and cellos). Siegfried's
attack is the full orchestra; Sieglinde's motif is on the cellos with an oboe above, the Wälsungs' arpeggios on
violins and clarinets. The staging adds a crash and a thud as he seizes Mime, and a gong when the father is named
slain; the forge crackles, held well down under the singing.

compose() tags every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt

CODE = 'SF04'
TITLE = 'The Starling Song'
KIND = 'show'
DESCRIPTION = ('Mime whines about how he raised the boy, and Siegfried will not hear it. He wants to know who '
               'his parents were, and at last the dwarf tells him: Siegmund and Sieglinde.')
VOICEOVER = ('Every bird in the forest has a mother and a father. '
             'Siegfried wants to know: where are mine?')

K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 508-532, 914-946 and 1046-1066, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
LAMENT_BEAT = 0.62                          # the cradle rocks over two of these a side
T_LAMENT = [0.0]                            # Mime's nursery song
T_GRAB = EX['segments'][1]['start']         # "So muß ich dich fassen": he seizes Mime
T_CUT = [T_GRAB]                            # the song snuffed out
T_SL = [BAR[1050], BAR[1053]]               # "Sieglinde mochte sie heißen": the mother
T_SM = [BAR[1057], BAR[1061]]               # "Dann frag' ich, wie hieß mein Vater?": the father
T_LET = BAR[1063]                           # "Erschlagen sei er": he lets Mime go
# Mime's Starling Song, from the vocal score (Schirmer 1914, archive.org 31761034115105, pp. 21-22): (bar, start,
# length in quarters, note as written; a tenor, so it sounds an octave lower). 3/4; the upbeat is in 2/2. A grace
# note is (bar, -1, 0, note), just before the beat.
SONG = [(511, 3, 1, 'C5'), (512, -1, 0, 'Db5'), (512, 0, 1, 'C5'), (512, 1, 1, 'Bb4'), (512, 2, 1, 'Ab4'),
        (513, 0, 2, 'G4'), (514, -1, 0, 'C5'), (514, 0, 1, 'Bb4'), (514, 1, 1, 'Ab4'), (514, 2, 1, 'G4'),
        (515, 0, 2, 'F4'), (516, 0, 1, 'Gb4'), (516, 1, 1, 'Ab4'), (516, 2, 1, 'Bb4'), (517, 0, 1, 'C5'),
        (517, 1, 1, 'F4'), (517, 2, 1, 'F4'), (518, 0, 1, 'Gb4'), (518, 1, 1, 'Ab4'), (518, 2, 1, 'Bb4'),
        (519, 0, 2, 'C5'), (520, -1, 0, 'Eb5'), (520, 0, 1, 'Db5'), (520, 1, 1, 'C5'), (520, 2, 1, 'Bb4'),
        (521, 0, 2, 'Ab4'), (522, -1, 0, 'Db5'), (522, 0, 1, 'C5'), (522, 1, 1, 'Bb4'), (522, 2, 1, 'Ab4'),
        (523, 0, 2, 'G4'), (524, -1, 0, 'C5'), (524, 0, 1, 'Bb4'), (524, 1, 1, 'Ab4'), (524, 2, 1, 'G4'),
        (525, 0, 1, 'F4'), (525, 1, 1, 'F4'), (525, 2, 1, 'G4'), (526, 0, 2, 'Ab4'), (526, 2, 1, 'F4'),
        (527, 0, 1, 'C5'), (527, 2, 1, 'F4'), (528, 0, 1, 'Gb4'), (528, 1, 1, 'Ab4'), (528, 2, 1, 'Bb4'),
        (529, 0, 2, 'Ab4'), (529, 2, 1, 'F4'), (530, -1, 0, 'Eb5'), (530, 0, 1, 'C5'), (530, 1, 1, 'Bb4'),
        (530, 2, 1, 'Ab4'), (531, 0, 1, 'Ab4'), (531, 2, 1, 'F4')]

ROCK = hexc('#3a1608')
EMBER = hexc('#a01a00')
FORGE = hexc('#ff4a08')
HEAT = hexc('#fff0a0')
SPARK = hexc('#ffb020')
FOREST = hexc('#18a020')
GOLD = hexc('#ffaa00')
MIME = hexc('#e0c800')
MIME_DIM = hexc('#6a5a00')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
SIEGMUND = hexc('#30a8ff')
SIEGLINDE = hexc('#ffa860')

LV = dict(bed=0.28, forge=0.55, walls=0.45, mouth=0.55)          # the cave at every Act I cut
MIME_AT, HERO_AT = 0.32, 0.7                                       # their places on Porch Front


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """Mime's cave as profiles over the house: the anvil in the middle of Porch Front, the forge fire across Porch
    Front, the chimney walls on Porch Left and Right, rock everywhere else, the mouth at the free end of Right."""
    d = G.pd
    anvil = at(G, 'Porch Front', 0.5)
    rng = np.random.default_rng(1876)       # the same fire and rock in every scene, so the cuts match
    seg = G.seg_of
    return dict(
        d=d, anvil=anvil,
        heat=np.exp(-((d - anvil) / 22) ** 2),
        forge=(seg == 'Porch Front') * (0.55 + 0.45 * np.exp(-((d - anvil) / 120) ** 2)),
        walls=np.isin(seg, ['Porch Left', 'Porch Right']) * (0.35 + 0.65 * smoothstep(
            at(G, 'Porch Left', 0.0), at(G, 'Porch Left', 1.0), d) * (1 - smoothstep(
                at(G, 'Porch Right', 0.0), at(G, 'Porch Right', 1.0), d))),
        rock=0.75 + 0.25 * smooth_noise(rng, d, 60.0),
        spill=np.exp(-np.clip(np.maximum(at(G, 'Porch Left', 0.0) - d, d - at(G, 'Porch Right', 1.0)), 0, None) / 450),
        mouth=smoothstep(at(G, 'Right', 0.72), at(G, 'Right', 1.0), d),
        fire=Flicker(rng, G.N, 0.8, 3.5),
        lick=Flicker(rng, G.N, 2.5, 7.0),
        leaf=Flicker(rng, G.N, 0.1, 0.5),
    )


def cave(S, T, lv):
    """The cave at shared time T with levels lv (bed, forge, walls, mouth)."""
    fire, lick = S['fire'](T), S['lick'](T)
    fr = light(ROCK, lv['bed'] * S['rock'])
    fr += light(FORGE, lv['forge'] * S['forge'] * (0.8 + 0.2 * fire))
    fr += light(EMBER, 0.6 * lv['forge'] * S['heat'] * (0.7 + 0.3 * fire))
    fr += light(FORGE, lv['walls'] * S['walls'] * (0.7 + 0.3 * np.clip(lick, -1, 1)))
    fr += light(EMBER, 0.8 * lv['walls'] * S['spill'] * (1 - S['walls'] - S['forge']).clip(0) * (0.8 + 0.2 * fire))
    fr += light(FOREST, lv['mouth'] * S['mouth'] * (0.85 + 0.15 * S['leaf'](T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the cave, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Hammer blows [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
    d = S['d']
    out = np.zeros_like(d)
    for i, (th, s, p0) in enumerate(hits):
        a = t - th
        if not 0 <= a < 1.6:
            continue
        rng = np.random.default_rng(seed * 1000 + i)
        v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
        ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
        life = np.exp(-a / rng.uniform(0.35, 0.9, n))
        out += (s * life[:, None] * np.exp(-((d[None, :] - ps[:, None]) / 7) ** 2)).sum(0)
    return out


def hero(fr, S, p, lvl, w=16.0):
    """Siegfried: an emerald figure with a white-hot head."""
    fr = figure(fr, S, p, SIEGFRIED, lvl, w)
    return fr + light(HEAD, 0.9 * lvl * np.exp(-((S['d'] - p) / 5) ** 2))


def song():
    """Mime's song in seconds: (time, seconds, midi as sung)."""
    bars = [(m, t) for m, t in EX['bars'] if m < 600]
    when = lambda pos: float(np.interp(pos, [b[0] for b in bars], [b[1] for b in bars]))
    out = []
    for b, x, n, name in SONG:
        per = 4 if b == 511 else 3
        if x < 0:
            t0 = when(b) - 0.07
            out.append((t0, 0.07, note(name) - 12))
        else:
            t0 = when(b + x / per)
            out.append((t0, when(b + (x + n) / per) - t0, note(name) - 12))
    return out


def compose():
    """Every note, tagged: (time, seconds, midi, velocity, part, k). Mime's song from the vocal score ('lament'); in
    the excerpt, the right hand under it is the orchestra's sighing chords ('sigh'), the left hand its rocking
    ('rock'); the right hand of Siegfried's attack is his strength ('grab'); the right hand from "Sieglinde" is her
    motif ('sieglinde') and from "wie hieß mein Vater?" the Wälsungs' ('siegmund'); everything else 'orch'."""
    N = [(t, d, m, 96, 'lament', 0) for t, d, m in song()]
    for t, d, m, v, h in EX['notes']:
        part = 'orch'
        if t < T_GRAB:
            part = 'sigh' if h == 0 else 'rock'
        elif t < EX['segments'][2]['start']:
            part = 'grab' if h == 0 else 'orch'
        elif h == 0 and t < T_SL[0]:
            part = 'fumble'
        elif h == 0 and T_SL[0] <= t < T_SM[0]:
            part = 'sieglinde'
        elif h == 0 and t >= T_SM[0]:
            part = 'siegmund'
        N.append((t, d, m, v, part, 0))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=4):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    L = d.max()
    N = compose()
    p_mime, p_hero = at(G, 'Porch Front', MIME_AT), at(G, 'Porch Front', HERO_AT)
    p_grab = at(G, 'Porch Front', 0.42)
    lam_on = np.array(sorted({e[0] for e in N if e[4] == 'lament'}))
    sm_on = np.array(sorted({e[0] for e in N if e[4] == 'siegmund'}))
    sl_on = np.array(sorted({e[0] for e in N if e[4] == 'sieglinde'}))
    pl0, pr1 = at(G, 'Porch Left', 0.0), at(G, 'Porch Right', 1.0)
    father = np.clip((pl0 - d) / pl0, 0, 1)                    # 0 at the porch, 1 at the back of Side
    mother = np.clip((d - pr1) / (L - pr1), 0, 1)              # 0 at the porch, 1 at the free end of Right
    sl_end = T_SM[0] + 2.0
    fumble = np.array(sorted({e[0] for e in N if e[4] == 'fumble'}))
    grab_bars = [(bt, max([n[3] for n in EX['notes'] if bt <= n[0] < bt + 0.6] or [0]) / 127)
                 for m, bt in EX['bars'] if 914 <= m < 946]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = cave(S, T, dict(LV))

        # the cradle: a wide yellow wash rocking across the house, pulsing on every note, snuffed at each cut
        song = 0.0
        for t0, tc in zip(T_LAMENT, T_CUT):
            song = max(song, smoothstep(t0 - 0.2, t0 + 0.8, t) * (1 - smoothstep(tc, tc + 0.15, t)))
        if song > 0:
            i = int(np.searchsorted(lam_on, t, side='right')) - 1
            pulse = np.exp(-(t - lam_on[i]) / 0.3) if i >= 0 else 0.0
            sway = np.sin(2 * np.pi * t / (4 * LAMENT_BEAT))
            centre = anvil + sway * 0.55 * L
            fr = fr * (1 - 0.4 * song)
            fr += light(MIME, song * (0.7 + 0.3 * pulse) * np.exp(-((d - centre) / 600) ** 2))

        # each cut: a horn stab, an emerald slash out from him to both ends
        for tc in T_CUT:
            a = t - tc
            if 0 <= a < 1.0:
                front = 2600 * a
                fr += light(SIEGFRIED, (np.abs(d - p_hero) < front) * np.exp(-a / 0.35) * 0.9)
                fr += light(HEAD, np.exp(-((np.abs(d - p_hero) - front) / 40) ** 2) * np.exp(-a / 0.5))

        # he seizes Mime: emerald closing round the yellow, Mime shaking
        held = smoothstep(T_GRAB - 0.5, T_GRAB, t) * (1 - smoothstep(T_LET, T_LET + 1.5, t))
        ps = p_hero + (p_grab - p_hero) * held
        if T_GRAB <= t < T_GRAB + 2.5:
            a = t - T_GRAB
            fr += light(WHITE, 0.6 * np.exp(-a / 0.1))
            fr += light(SIEGFRIED, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_mime) - 1200 * a) / 120) ** 2))
        for bt, sv in grab_bars:            # his grip: an emerald surge out from the two of them on every bar
            a = t - bt
            if 0 <= a < 1.2:
                fr += light(SIEGFRIED, 1.4 * sv * np.exp(-a / 0.45) *
                            np.exp(-((np.abs(d - p_grab) - 1600 * a) / 220) ** 2))
        k = int(np.searchsorted(fumble, t, side='right')) - 1      # Mime fumbling for the name: a shudder each chord
        if k >= 0 and t - fumble[k] < 1.2 and t < T_SL[0]:
            a = t - fumble[k]
            fr += light(MIME, 0.8 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_mime) - 900 * a) / 120) ** 2))
            fr += light(SIEGFRIED, 0.4 * np.exp(-a / 0.3) * np.exp(-((d - p_grab) / 200) ** 2))
        if held > 0:
            r = 140 - 80 * smoothstep(T_GRAB, T_GRAB + 4, t)
            ring = np.exp(-((np.abs(d - p_mime) - r) / 18) ** 2)
            fr += light(SIEGFRIED, 0.7 * held * ring * (0.75 + 0.25 * np.sin(2 * np.pi * 3 * t)))

        # the father: Wälsung blue rolling out from the porch over Left and Side, a wave on every note
        blue = smoothstep(T_SM[0], T_SM[0] + 3, t) * (1 - smoothstep(T_LET, T_LET + 3, t))
        if blue > 0:
            reach = smoothstep(T_SM[0], T_SM[0] + 8, t)
            fr = fr * (1 - 0.5 * blue * (d < pl0))[:, None]
            fr += light(SIEGMUND, 0.75 * blue * (father <= reach + 0.02) * (d < pl0 + 30))
            i = int(np.searchsorted(sm_on, t, side='right')) - 1
            if i >= 0 and t - sm_on[i] < 1.5:
                a = t - sm_on[i]
                fr += light(SIEGMUND, 0.7 * np.exp(-a / 0.5) * np.exp(-((pl0 - d - 1300 * a) / 70) ** 2))
        # the mother: hearth amber flooding Right, fading as her phrase sinks
        amber = smoothstep(T_SL[0], T_SL[0] + 3, t) * (1 - 0.6 * smoothstep(T_SL[1] + 3, sl_end, t)) \
            * (1 - smoothstep(T_LET, T_LET + 3, t))
        if amber > 0:
            reach = smoothstep(T_SL[0], T_SL[0] + 7, t)
            fr = fr * (1 - 0.5 * amber * (d > pr1))[:, None]
            fr += light(SIEGLINDE, 0.75 * amber * (mother <= reach + 0.02) * (d > pr1 - 30))
            i = int(np.searchsorted(sl_on, t, side='right')) - 1
            if i >= 0 and t - sl_on[i] < 1.5:
                a = t - sl_on[i]
                fr += light(SIEGLINDE, 0.7 * np.exp(-a / 0.5) * np.exp(-((d - pr1 - 1300 * a) / 70) ** 2))
        # he lets go: blue and amber run back onto the porch and flare there as emerald
        if T_LET <= t < T_LET + 5:
            a = t - T_LET
            u = smoothstep(0, 1.8, a)
            fr += light(SIEGMUND, 0.8 * (1 - u) * np.exp(-((d - (pl0 - (1 - u) * pl0)) / 80) ** 2))
            fr += light(SIEGLINDE, 0.8 * (1 - u) * np.exp(-((d - (pr1 + (1 - u) * (L - pr1))) / 80) ** 2))
            fl = smoothstep(1.6, 2.0, a) * np.exp(-max(a - 2.0, 0) / 1.2)
            fr += light(SIEGFRIED, 0.95 * fl * np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']))
            fr += light(SIEGFRIED, 0.5 * fl)

        shake = 5 * held * np.sin(2 * np.pi * 11 * t)
        mlvl = keys(t, [(0, 0.85), (T_GRAB, 0.85), (T_GRAB + 1, 0.5), (T_LET, 0.5),
                        (D - 5, 0.6)])
        fr = figure(fr, S, p_mime + shake, MIME, mlvl)
        fr = hero(fr, S, ps, keys(t, [(0, 0.8), (T_GRAB - 0.5, 1.0), (T_LET + 3, 1.0), (D - 4, 0.8)]))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction, and Mime's song as he sings it."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    mime_p = pan_at(at(G, 'Porch Front', MIME_AT))
    hero_p = pan_at(at(G, 'Porch Front', HERO_AT))
    o = Orchestra(M, level=2.6)
    tag = {(round(e[0], 4), e[2]): e[4] for e in compose()}

    def role(t, d, m, v, h):
        p = tag.get((round(t, 4), m), 'orch')
        if p == 'sigh':                     # the sighing chords under his song: violas and horns, soft
            return [('violas', 0, -30, 0.45), ('horns', 0, -36, 0.3)]
        if p == 'rock':                     # the rocking: harp and cellos, plucked
            return [('harp', 0, -20, 0.55), ('cellos', 0, -32, 0.35)]
        if p == 'fumble':                   # his dithering: clarinets and bassoons
            return [('clarinets', 0, -10, 0.55), ('bassoons', -12, -14, 0.4)]
        if p == 'sieglinde':                # her motif on the cellos, an oboe above
            return [('cellos', 0, -4, 0.75), ('oboes', 12, -14, 0.35)]
        if p == 'siegmund':                 # the Wälsungs' arpeggios: violins, clarinets on the long notes
            return [('violins', 0, -8, 0.5)] + ([('clarinets', 0, -8, 0.5)] if d >= 0.8 else [])
        return None

    o.tutti(EX['notes'], size=lambda t: 1.0 if T_GRAB <= t < EX['segments'][2]['start'] else 0.5, role=role,
            pan=lambda t, m: hero_p * 0.5 if T_GRAB <= t else mime_p * 0.6)
    for t, d, m in song():                  # Mime's song: clarinet and bassoon as he sings it, an oboe above
        o.play('clarinets', m, t, max(d, 0.1), 104, mime_p, 0.85)
        o.play('bassoons', m, t, max(d, 0.1), 96, mime_p, 0.5)
        o.play('oboes', m + 12, t, max(d, 0.1), 80, mime_p, 0.3)
    # he seizes Mime by the throat: a crash, a thud, and his grip on every bar
    o.hit('crash', T_GRAB, 118, gain=0.6, pan=mime_p)
    o.boom(T_GRAB, mime_p, 0.7)
    o.hit('timpani roll', T_GRAB + 0.5, 100, pitch=-4, gain=0.5, pan=mime_p)
    o.hit('cymbal swell', T_SL[0] - 2.8, 80, gain=0.3, pan=pan_at(at(G, 'Right', 0.6)))
    o.hit('gong', T_LET + 1.6, 96, gain=0.35)                  # "Erschlagen": the father slain
    o.fire(0.0, D, 0.22, pan=pan_at(at(G, 'Porch Front', 0.5)), crackle=4.0)
    o.effects([(0.0, -10.0), (T_GRAB - 0.3, -10.0), (T_GRAB, 0.0), (EX['segments'][2]['start'], 0.0),
               (T_SL[0], -10.0), (D, -10.0)])
