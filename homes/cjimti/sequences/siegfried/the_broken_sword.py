"""The Broken Sword: Mime has made Siegfried a new sword. "Ich schuf die Waffe scharf", he says, and holds it out,
and a white steel blade grows along Porch Front from his hands toward the anvil, gleaming on every note. Siegfried
takes it and tries it, the strings shivering in a fortissimo tremolo; then, at the top of a run, he smashes it on
the anvil: a white flash over the whole house, steel shards flying out in both directions to the ends of the
roofline, chased by an orange flare of the forge. "Da hast du die Stücken, schändlicher Stümper!"

The music is Wagner's own: Act I, bars 314 to 424, as Solti's 1958 Vienna Philharmonic recording takes them, from
the end of Siegfried's tale of the bear through Mime's offer, the trial and the blow, and Siegfried's whole tirade,
to Mime's "Nun tobst du wieder wie toll!". The notes come from the Wagner Ring Dataset's piano reduction
(pixelhome/ring.py): Mime's offer on violins with a trumpet glinting, the trial's tremolo on the violins, Siegfried's
scorn on horns and violins, trumpets on top at its two climaxes. The staging adds the blow: steel shattering on the
anvil with a boom, the shards ringing as they fly, a cymbal swelling into it, cymbals and timpani on the climaxes,
the anvil pounded at their tops, and the forge fire roaring with his anger.

Mime cringes, dim and shaking. Siegfried's scorn burns the whole house emerald, a surge racing out from him on
every bar of his tirade and the house blazing at its two climaxes, sparks flying as he pounds the anvil, until
Mime protests and the fury cools, with Siegfried at the anvil's right hand and Mime creeping back to its left.

compose() tags every note; stage(), cave(), figure() and sparks() are the cave, shared word for word by Act I's
scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF03'
TITLE = 'The Broken Sword'
KIND = 'show'
DESCRIPTION = ('The dwarf holds out a gleaming new sword. Siegfried tries it, smashes it to pieces on the anvil, '
               'and storms at him.')
VOICEOVER = ('Mime forges sword after sword. '
             'And Siegfried smashes every one of them to pieces.')

K = 2                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 314-424, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_SWORD = [BAR[321]]                        # "Ich schuf die Waffe scharf": Mime holds out the new sword
T_TEST = BAR[325]                           # Siegfried takes it and tries it
T_SMASH = BAR[342]                          # he smashes it on the anvil, at the top of the run
T_PEAKS = [(BAR[385], BAR[391]), (BAR[402], BAR[418])]     # the two climaxes of his tirade
T_REST = BAR[419]                           # "Nun tobst du wieder wie toll!"

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
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')

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


def smashes():
    return [T_SMASH]


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). The right hand under Mime's offer
    and Siegfried's trial is the Sword's gleam ('sword'); the right hand of everything Siegfried sings is his
    audacity ('aud'), the loudest notes of the two climaxes 'peak'; 'smash' marks the blow (silent)."""
    N = []
    for t, d, m, v, h in EX['notes']:
        part = 'orch'
        if h == 0 and T_SWORD[0] <= t < T_SMASH:
            part = 'sword'
        elif h == 0 and (t < T_SWORD[0] or t > T_SMASH + 0.3):
            part = 'peak' if any(a <= t < b for a, b in T_PEAKS) and v >= 105 else 'aud'
        N.append((t, d, m, v, part, 0))
    N.append((T_SMASH, 0.1, 24, 0, 'smash', 0))
    return sorted(N, key=lambda e: e[0])


def fury_at(t):
    """How hot his scorn burns: from the smash, flaring at the two climaxes, cooling at Mime's protest."""
    f = 0.3 * smoothstep(T_SMASH, T_SMASH + 0.6, t)
    for a, b in T_PEAKS:
        f += 0.45 * smoothstep(a - 0.4, a + 0.4, t) * (1 - smoothstep(b - 0.5, b + 0.8, t))
    return f * (1 - 0.6 * smoothstep(T_REST - 1, T_REST + 2, t))


def render(G, seed=3):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, anvil = S['d'], S['anvil']
    N = compose()
    p_mime, p_hero = at(G, 'Porch Front', MIME_AT), at(G, 'Porch Front', HERO_AT)
    p_strike = at(G, 'Porch Front', 0.56)
    ham = [(t, 0.9, anvil) for t, _, m, v, part, k in N if part == 'peak' and m >= note('G5')]
    ham_t = np.array([h[0] for h in ham])
    sm = smashes()
    shards = [(ts, 1.0 + 0.3 * k, anvil) for k, ts in enumerate(sm)]
    sword = [e for e in N if e[4] == 'sword']
    grumble = [(T_REST, 1.2, 60, 100, 'grumble', 0), (BAR[421], 1.2, 60, 100, 'grumble', 0),
               (BAR[423], 1.0, 60, 100, 'grumble', 0)]
    aud_on = np.array(sorted({e[0] for e in N if e[4] == 'aud'}))
    surges = []                             # every bar of the tirade: an emerald surge out from him, by its loudness
    for (m, bt), (_, nt) in zip(EX['bars'], EX['bars'][1:] + [[0, D]]):
        if T_SMASH + 0.5 < bt < T_REST:
            vs = [n[3] for n in EX['notes'] if bt <= n[0] < nt]
            surges.append((bt, (max(vs) / 127) ** 2 if vs else 0.0))
    jag = np.random.default_rng(seed).uniform(0.4, 1.0, G.N)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(LV)
        fury = fury_at(t)
        fr = cave(S, T, lv)

        # the blade held out: white steel growing from Mime's hands to the anvil, flashing at each note
        for k, t0 in enumerate(T_SWORD):
            ts = sm[k]
            if t0 <= t < ts + 0.05:
                grow = smoothstep(t0, t0 + 1.5, t)
                tip = p_mime + 10 + grow * (anvil - p_mime + 15)
                notes = [e for e in sword if e[5] == k and e[0] <= t]
                glint = np.exp(-(t - notes[-1][0]) / 0.25) if notes else 0.0
                blade = (d > p_mime + 8) * (d < tip) * 1.0
                fr = fr * (1 - 0.9 * blade)[:, None]
                fr += light(STEEL, (0.7 + 0.3 * glint) * blade)
                fr += light(STEEL, 0.5 * glint * np.exp(-((d - tip) / 60) ** 2))
                if notes:                   # each note of the Sword sends a steel gleam out to both ends
                    a = t - notes[-1][0]
                    fr += light(STEEL, 0.75 * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 1100 * a) / 80) ** 2))
                fr += light(HILT, 0.9 * np.exp(-((d - p_mime - 9) / 4) ** 2))
                sweep = p_mime + ((t - t0) * 160) % (tip - p_mime + 1)
                fr += light(WHITE, 0.6 * blade * np.exp(-((d - sweep) / 8) ** 2))

        # the smash: a white flash over the whole house, steel shards to both ends, the forge flaring orange
        for k, ts in enumerate(sm):
            a = t - ts
            if 0 <= a < 3.0:
                s = 0.55 + 0.2 * k
                fr += light(WHITE, min(1.0, s * np.exp(-a / 0.08)) * (0.5 + 0.5 * jag))
                fr += light(FORGE, (0.9 + 0.1 * k) * np.exp(-a / 0.7) * np.exp(-((np.abs(d - anvil) - 1300 * a) / 200) ** 2))
                fr += light(FORGE, 0.55 * np.exp(-a / 0.9))
                fr += light(STEEL, 0.35 * np.exp(-a / 0.4) * jag)
                fr += light(HEAT, np.exp(-a / 0.2) * S['heat'] ** 0.4)
        fr += light(STEEL, np.clip(sparks(S, shards, t, 31, n=40, reach=1.3) + sparks(S, shards, t, 33, n=40), 0, 1.0))
        for t0, dur, m, v, part, k in grumble:  # every grumble a yellow shudder out from Mime
            a = t - t0
            if 0 <= a < 1.0:
                fr += light(MIME, 0.6 * np.exp(-a / 0.4) * np.exp(-((np.abs(d - p_mime) - 900 * a) / 70) ** 2))

        # the climaxes of his tirade: he pounds the anvil, every top note a white-hot flash and sparks
        i = int(np.searchsorted(ham_t, t, side='right')) - 1
        if i >= 0 and t - ham_t[i] < 1.0:
            a = t - ham_t[i]
            fr += light(HEAT, min(1.0, 1.1 * np.exp(-a / 0.09)) * S['heat'] ** 0.5)
            fr += light(FORGE, 0.5 * np.exp(-a / 0.3) * (S['forge'] + S['walls']))
        fr += light(SPARK, np.clip(sparks(S, ham, t, 32), 0, 1.0))

        # his scorn: the whole house burns emerald, a shockwave out from him on every note
        if fury > 0:
            fr = fr * (1 - 0.6 * fury)
            fr += light(SIEGFRIED, fury * (0.45 + 0.15 * np.sin(2 * np.pi * (d / 300 - 1.4 * t))))
        for bt, sv in surges:
            a = t - bt
            if 0 <= a < 1.4:
                fr += light(SIEGFRIED, 1.3 * sv * np.exp(-a / 0.45) *
                            np.exp(-((np.abs(d - p_hero) - 1700 * a) / 280) ** 2))
        j = int(np.searchsorted(aud_on, t, side='right')) - 1
        if j >= 0 and t - aud_on[j] < 1.2:
            a = t - aud_on[j]
            fr += light(HEAD, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - p_hero) - 1500 * a) / 90) ** 2))

        # Siegfried strides to the anvil for each smash and back; Mime cringes after each
        ps = p_hero
        for ts in sm:
            ps += (p_strike - p_hero) * smoothstep(ts - 1.6, ts - 0.4, t) * (1 - smoothstep(ts + 1.0, ts + 3.0, t))
        cringe = max([np.exp(-(t - ts) / 6.0) for ts in sm if ts <= t], default=0.0)
        shake = 4 * cringe * np.sin(2 * np.pi * 9 * t)
        mlvl = 0.75 - 0.4 * cringe
        if t > T_REST:
            mlvl = keys(t, [(T_REST, mlvl), (D - 4, 0.6)])
        fr = figure(fr, S, p_mime - 12 * cringe + shake, MIME, mlvl)
        fr = hero(fr, S, ps, keys(t, [(0, 0.8), (T_SMASH, 1.0), (T_REST, 1.0), (D - 2, 0.8)]))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; the sword shatters on the anvil."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    forge = pan_at(at(G, 'Porch Front', 0.5))
    hero_p = pan_at(at(G, 'Porch Front', HERO_AT))
    o = Orchestra(M, level=1.7)
    tag = {(round(e[0], 4), e[2]): e[4] for e in compose()}
    trem_a, trem_b = BAR[332], BAR[340]

    def role(t, d, m, v, h):
        p = tag.get((round(t, 4), m), 'orch')
        if p == 'sword' and t >= trem_b:    # the run up to the blow: violins and flutes
            return [('violins', 0, 0, 0.6), ('flutes', 0, -8, 0.4)]
        if p == 'sword' and t < T_TEST:     # Mime's offer: the strings climb, a trumpet glints on top
            return [('violins', 0, -4, 0.5), ('clarinets', -12, -10, 0.35)] + \
                ([('trumpets', 0, -12, 0.35)] if d >= 0.4 else [])
        if p in ('aud', 'peak'):            # Siegfried's scorn: horns and violins, trumpets at the climaxes
            parts = [('violins', 0, -2, 0.5), ('horns', -12 if m >= note('C5') else 0, -6, 0.5)]
            if p == 'peak':
                parts.append(('trumpets', 0, -10, 0.4))
            return parts
        return None

    notes = [n for n in EX['notes'] if not (n[4] == 0 and trem_a <= n[0] < trem_b)]
    notes += tidy([n for n in EX['notes'] if n[4] == 0 and trem_a <= n[0] < trem_b])
    o.tutti(sorted(notes), size=lambda t: 0.6 if t < T_SMASH else 1.0, role=role,
            pan=lambda t, m: hero_p * 0.6 if t > T_SMASH else forge * 0.4)
    # the blow: steel shattering on the anvil, shards ringing out both ways
    o.shatter(T_SMASH, forge, 1.0)
    o.hit('anvil', T_SMASH, 127, gain=0.9, pan=forge)
    o.boom(T_SMASH, forge, 0.7)
    rng = np.random.default_rng(341)
    for k in range(9):
        o.hit('triangle', T_SMASH + 0.15 + rng.uniform(0, 1.4), int(rng.uniform(70, 110)), gain=0.25,
              pan=float(rng.uniform(-0.9, 0.9)))
    o.hit('cymbal swell', T_SMASH - 2.6, 96, gain=0.4, pan=forge)
    for a, b in T_PEAKS:                    # the climaxes: cymbal and timpani
        o.hit('crash', a, 115, gain=0.5, pan=hero_p)
        o.hit('timpani', a, 118, pitch=-4, gain=0.6, pan=hero_p)
    for t, d, m, v, p, k in compose():      # he pounds the anvil at the top of the climaxes
        if p == 'peak' and m >= note('G5'):
            o.hit('anvil', t, 108, gain=0.4, pan=forge)
    o.fire(0.0, D, lambda tt: 0.25 + 0.35 * fury_at(tt), pan=forge, crackle=6.0)
    o.effects([(0.0, -2.0), (T_SWORD[0], -8.0), (T_SMASH - 0.5, -8.0), (T_SMASH, 0.0), (D, 0.0)])
