"""Alberich: night on the shore before the hall of the Gibichungs. The porch is the hall's doors, dark wood with a
torch glow at the seams; the wings and Side are the shore under a deep blue night and a cold moon; Hagen's spear
stands on Porch Front, a steel glint. Hagen, ultraviolet in black, sleeps sitting against the doors, breathing on
his own falling tritone (Donington 61a) in the tubas.

The moonlight surges and his father comes to him in a dream: Alberich, red in his muddy halo, creeps in from the
free end of Right ("Schläfst du, Hagen, mein Sohn?"). Every phrase of the dwarf rolls a red wave out over the
house from where he stands, and every answer of the sleeping son a wave of violet the other way; where they meet
they crack white. The Ring (8) races round the whole house as a gold loop on each of its notes, and the Curse
(13) slashes blood red from the doors out to both ends. Three times Alberich demands an oath ("Schwörst du mir,
Hagen?"), louder each time, and three times the whole house flashes red to violet: "Mir selbst schwör' ich's."

The dream breaks: Alberich shrinks back out of the free end of Right as a red comet, and dawn comes up red over
the shore in great surges from the river end, while Hagen rises and stands by his spear.

compose() holds every note; stage(), shore(), figure(), torches(), crowd() and sparks() are the shore, shared word
for word by Act II's scenes (GD15-GD21) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'GD15'
TITLE = 'Alberich'
KIND = 'show'
DESCRIPTION = ('Night on the shore. Hagen sleeps by his spear, and his father Alberich comes to him in a dream: red '
               'waves against violet, the Ring racing round the house, until he swears to win it. Then a red dawn.')
VOICEOVER = ('Hagen sleeps with his eyes open. In the moonlight, his father creeps up beside him, and whispers '
             'about the Ring.')

K = 0                                       # this scene's place on Act II's shared clock: T = t + 80 K
T_HAGEN = [1.0, 6.0, 11.0]                  # the sleeper's tritone
T_IN = 8.0                                  # Alberich creeps in
T_THERE = 19.0
PHRASES = [(20.0, 'a'), (24.5, 'h'), (28.0, 'a'), (32.5, 'h'), (44.0, 'a'), (47.5, 'h')]
T_RING = 35.0
T_CURSE = 39.5
T_SWEAR = [51.0, 53.4, 55.8]                # "Schwörst du mir, Hagen?"
T_GONE = 58.5                               # the dream breaks
T_DAWN = 61.0
D = 80.0

NIGHT = hexc('#1a2ab0')
MOON = hexc('#80a0ff')
RED_DAWN = hexc('#ff1030')
ORANGE_DAWN = hexc('#ff6a10')
WOOD = hexc('#5a2008')
HALL = hexc('#ff8a20')
SPEAR = hexc('#c8d8ff')
TORCH = hexc('#ff6a10')
FLAME = hexc('#ffd060')
HAGEN = hexc('#7a00ff')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
GOLD = hexc('#ffaa00')
BLOOD = hexc('#c00010')
WHITE = hexc('#ffffff')

START = dict(night=0.62, moon=0.45, dawn=0.0, hall=0.45, spear=0.55)
END = dict(night=0.3, moon=0.1, dawn=0.6, hall=0.5, spear=0.6)        # where GD16 picks the shore up
HAGEN_AT = ('Porch Front', 0.35)            # by the doors, beside his spear
HAGEN_LVL = (0.45, 0.8)                     # asleep at the start; standing at the end


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The shore before the hall as profiles over the house: the porch is the hall's doors, its seams lit from
    inside, the spear upright in the middle of Porch Front; the wings and Side are the shore, the river beyond the
    free end of Right."""
    d = G.pd
    rng = np.random.default_rng(1874)       # the same shore, moonlight and torches in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    spear = at(G, 'Porch Front', 0.5)
    L = d.max()
    return dict(
        d=d, L=L, porch=porch, shore=~porch, spear=spear,
        doors=porch * (0.65 + 0.35 * smooth_noise(rng, d, 30.0)),
        seams=porch * np.clip(np.sin(2 * np.pi * (d - at(G, 'Porch Left', 0.0)) / 95) * 3 - 2.2, 0, 1),
        tip=np.exp(-((d - spear) / 7) ** 2),
        river=smoothstep(L - 600, L, d),      # the dawn comes up from the river end
        sand=~porch * (0.7 + 0.3 * smooth_noise(rng, d, 70.0)),
        flick=Flicker(rng, G.N, 3.0, 9.0),
        glow=Flicker(rng, G.N, 0.6, 2.0),
    )


def shore(S, T, lv):
    """The shore at shared time T with levels lv (night, moon, dawn, hall, spear)."""
    d = S['d']
    drift = np.sin(2 * np.pi * (d / 310 + 0.07 * T)) * np.sin(2 * np.pi * (d / 170 - 0.05 * T) + 0.6)
    fr = light(NIGHT, lv['night'] * S['sand'] * (0.85 + 0.15 * drift))
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 600 - 0.03 * T))
    fr += light(MOON, lv['moon'] * S['shore'] * (0.4 + 0.6 * u) ** 2)
    sky = RED_DAWN + (ORANGE_DAWN - RED_DAWN) * (0.5 + 0.5 * np.sin(2 * np.pi * (d / 450 + 0.05 * T)))[:, None]
    fr += light(sky, lv['dawn'] * S['shore'] * (0.75 + 0.25 * drift) * (0.7 + 0.3 * S['river']))
    fr += light(WOOD, (0.4 + 0.6 * lv['hall']) * S['doors'])
    fr += light(HALL, lv['hall'] * S['seams'] * (0.8 + 0.2 * S['glow'](T)))
    fr += light(SPEAR, lv['spear'] * S['tip'] * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * T)))
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the shore, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def crowd(S, n, seed=1717):
    """Where n vassals stand with their torches, spread over the shore and the porch runs (not on the spear)."""
    rng = np.random.default_rng(seed)
    p = np.sort(rng.uniform(20, S['L'] - 15, n))
    return p[np.abs(p - S['spear']) > 30]


def torches(S, T, ps, lvl, seed=7):
    """Torches at path distances ps (lvl a scalar or one per torch): orange flames with a flickering gold core."""
    d = S['d']
    lvl = np.broadcast_to(np.asarray(lvl, float), np.shape(ps))
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 2 * np.pi, len(ps))
    fq = rng.uniform(5, 11, len(ps))
    fl = 0.8 + 0.2 * np.sin(fq * T + ph)
    g = np.exp(-((d[None, :] - np.asarray(ps)[:, None]) / 7) ** 2)
    out = light(TORCH, np.clip((lvl * fl)[:, None] * g, 0, None).sum(0).clip(0, 1.2))
    return out + light(FLAME, np.clip((0.6 * lvl * fl ** 3)[:, None] * g ** 4, 0, None).sum(0).clip(0, 1))


def sparks(S, hits, t, seed, n=14, reach=1.0):
    """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline, -> perceptual."""
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


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    add(0.0, T_DAWN, 'Bb1', 62, 'pedal')
    for k, t0 in enumerate(T_HAGEN):
        for t, m, v, d in play('hagen', t0, 1.2, -12, 86 - 4 * k):
            add(t, d, m, v, 'hagen', k)
    for j in range(10):                     # his creeping steps: a muttered figure in the low strings
        add(T_IN + j * 1.1, 0.3, ('Bb1', 'B1', 'C2', 'B1')[j % 4], 70 + 2 * j, 'creep')
    for k, (t0, who) in enumerate(PHRASES):
        if who == 'a':
            for j, m in enumerate(('Bb3', 'Db4', 'C4', 'Bb3', 'Ab3', 'G3')):
                add(t0 + j * 0.45, 0.42, m, 92 + 2 * k, 'alberich', k)
        else:
            for t, m, v, d in play('hagen', t0, 0.9, 0, 100 + 2 * k):
                add(t, d, m, v, 'answer', k)
    for t, m, v, d in play('ring', T_RING, 0.5, -12, 96):
        add(t, d, m, v, 'ring')
    for t, m, v, d in play('curse', T_CURSE, 0.5, -12, 110):
        add(t, d, m, v, 'curse')
    for k, t0 in enumerate(T_SWEAR):
        for j, m in enumerate(('Bb3', 'Eb4', 'Gb4')):
            add(t0 + j * 0.3, 0.32, m, 100 + 8 * k, 'swear', k)
        add(t0 + 1.0, 1.0, 'E2', 104 + 8 * k, 'oath', k)
        add(t0 + 1.0, 1.0, 'Bb1', 104 + 8 * k, 'oath', k)
    for t, m, v, d in play('ring', T_GONE, 0.3, 0, 70):
        add(t, d, m, v, 'away')
    for t, m, v, d in play('dawn', T_DAWN, 0.62, 0, 96):
        add(t, d, m, v, 'dawn')
    for m in ('Bb2', 'D3', 'F3'):
        add(T_DAWN + 2.0, D - T_DAWN - 2.0, m, 60, 'morning')
    return sorted(N, key=lambda e: e[0])


def alberich_at(G, t):
    """Where Alberich is at time t (None when he is not there)."""
    if t < T_IN or t > T_GONE + 2.0:
        return None
    a, b = G.pd.max() + 30, at(G, 'Porch Front', 0.62)
    if t < T_GONE:
        return a + (b - a) * smoothstep(T_IN, T_THERE, t)
    return b + (a - b) * smoothstep(T_GONE, T_GONE + 2.0, t)


def render(G, seed=15):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, L = S['d'], S['L']
    N = compose()
    p_h = at(G, *HAGEN_AT)
    ring_on = np.array(sorted({e[0] for e in N if e[4] == 'ring'}))
    curse_on = np.array(sorted({e[0] for e in N if e[4] == 'curse'}))
    dawn_on = np.array(sorted({e[0] for e in N if e[4] == 'dawn'}))
    sleep_on = [(e[0], e[1]) for e in N if e[4] == 'hagen']

    def recent(ts, t, span):
        i = int(np.searchsorted(ts, t, side='right')) - 1
        return (t - ts[i], i) if i >= 0 and t - ts[i] < span else (None, i)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: keys(t, [(0, START[k]), (T_DAWN, START[k]), (T_DAWN + 14, END[k])]) for k in START}
        dream = smoothstep(T_IN - 2, T_IN + 2, t) * (1 - smoothstep(T_GONE, T_GONE + 2.5, t))
        lv['moon'] += 0.3 * dream
        fr = shore(S, T, lv)

        # each dream phrase: red rolls out from the father, violet from the son, and they crack white where they meet
        pa = alberich_at(G, t)
        for t0, who in PHRASES:
            a = t - t0
            if 0 <= a < 3.2:
                src = alberich_at(G, t0) if who == 'a' else p_h
                r = 1500 * (1 - np.exp(-a / 1.2))
                ring_ = np.exp(-((np.abs(d - src) - r) / 230) ** 2) * np.exp(-a / 1.4)
                fr += light(ALBERICH if who == 'a' else HAGEN, 1.0 * ring_)
                fr += light(MUD if who == 'a' else NIGHT, 0.6 * np.exp(-a / 0.8) * np.exp(-((d - src) / 200) ** 2))

        # the Ring: a gold loop racing round the whole house on each of its notes
        a, i = recent(ring_on, t, 3.0)
        if a is not None:
            c = (ring_on[i] * 211 + a * 1400) % L
            fr += light(GOLD, np.exp(-a / 0.9) * (np.exp(-((d - c) / 60) ** 2) + np.exp(-((d - (L - c)) / 60) ** 2)))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.2) * np.exp(-((d - c) / 12) ** 2))

        # the Curse: blood red slashes from the doors out to both ends
        a, i = recent(curse_on, t, 2.5)
        if a is not None:
            front = min(1.0, a / 0.7) * max(S['spear'], L - S['spear'])
            slash = smoothstep(front + 50, front - 50, np.abs(d - S['spear']))
            fr += light(BLOOD, 0.95 * slash * np.exp(-a / 1.1))

        # three oaths demanded: the whole house red, then the son's violet answer flooding over it
        for k, t0 in enumerate(T_SWEAR):
            a = t - t0
            if 0 <= a < 2.4:
                s = 0.7 + 0.15 * k
                fr += light(ALBERICH, s * smoothstep(0, 0.1, a) * np.exp(-a / 0.5))
                b = a - 1.0
                if b >= 0:
                    fr += light(HAGEN, s * np.exp(-b / 0.6) * smoothstep(1100 * b + 60, 1100 * b - 60, np.abs(d - p_h)))
                    fr += light(WHITE, 0.6 * np.exp(-b / 0.08) * np.exp(-((d - p_h) / 30) ** 2))

        # Alberich: creeping in, and the dream breaking as he shrinks out of the free end of Right
        if pa is not None:
            lvl = 0.85 * dream * (1 - 0.3 * smoothstep(T_GONE, T_GONE + 1.5, t))
            fr += light(MUD, 0.65 * lvl * np.exp(-((d - pa) / 80) ** 2))
            fr = figure(fr, S, pa, ALBERICH, lvl)
            if t > T_GONE:
                tail = smoothstep(pa, pa - 260, d) * (d > pa - 260) * (d <= pa)
                fr += light(ALBERICH, 0.7 * lvl * tail * (d - pa + 260) / 260)

        # dawn: red surges in from the river end on each note of the Dawn motif
        a, i = recent(dawn_on, t, 3.0)
        if a is not None:
            front = L - 2700 * (1 - np.exp(-a / 0.9))
            fr += light(RED_DAWN, 0.85 * np.exp(-a / 1.4) * smoothstep(front - 80, front + 80, d) * S['shore'])
            fr += light(ORANGE_DAWN, 0.8 * np.exp(-a / 0.6) * np.exp(-((d - front) / 50) ** 2))

        # the sleeper's tritone: each note a violet swell over the doors and out along the shore
        for t0, dur in sleep_on:
            a = t - t0
            if 0 <= a < dur + 1.5:
                g = smoothstep(0, 0.3, a) * np.exp(-a / (dur + 0.5))
                fr += light(HAGEN, 0.75 * g * np.exp(-((d - p_h) / (250 + 400 * a)) ** 2))

        # Hagen: asleep against the doors, breathing; he rises at dawn
        breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / 4.5)
        rise = smoothstep(T_DAWN + 2, T_DAWN + 8, t)
        lvl = HAGEN_LVL[0] * (0.8 + 0.2 * breath) * (1 - rise) + HAGEN_LVL[1] * rise
        fr = figure(fr, S, p_h, HAGEN, lvl)
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

    for name, gain, rev in (('low', 0.36, 0.25), ('winds', 0.31, 0.35), ('brass', 0.33, 0.3), ('perc', 0.3, 0.3),
                            ('strings', 0.28, 0.35)):
        M.bus(name, gain=gain, reverb=rev)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    gong = M.hits('Percussion/gongHit_f*.wav')

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

    ph = pan_at(at(G, *HAGEN_AT))
    river = pan_at(at(G, 'Right', 0.9))

    def pa(t):
        p = alberich_at(G, t)
        return pan_at(p) if p is not None else river

    for t, d, m, v, part, k in compose():
        if part == 'pedal':
            hold('low', ctrem, m + 12, t, t + d, v, 0.0, rise=3.0, fall=3.0, gain=0.45)
        elif part in ('hagen', 'answer'):
            hold('low', tuba, m, t, t + d, v, ph, rise=0.2, fall=1.0, gain=0.9)
            if part == 'answer':
                M.add('brass', tbn.play(m + 12, v - 10, dur=d, release=0.4), t, 0.6, ph)
            M.add('perc', timp.play(v - 20, pitch=-6), t, 0.5, ph)
        elif part == 'creep':
            M.add('low', cbs.play(m, v), t, 0.8, pa(t))
        elif part == 'alberich':
            M.add('winds', bsn.play(m - 12, v, dur=d * 1.2, release=0.2), t, 0.9, pa(t))
            M.add('winds', clar.play(m, v - 14, dur=d * 1.2, release=0.2), t, 0.5, pa(t))
        elif part == 'ring':
            M.add('winds', clar.play(m + 12, v, dur=d * 1.1, release=0.3), t, 0.8, 0.0)
            M.add('winds', bsn.play(m, v - 10, dur=d * 1.1, release=0.3), t, 0.6, 0.0)
        elif part == 'curse':
            if d > 1.2:
                hold('brass', tbn, m + 12, t, t + d, v, ph, rise=0.15, fall=1.0, gain=0.9)
            else:
                M.add('brass', tbn.play(m + 12, v, dur=d * 1.05, release=0.3), t, 0.9, ph)
            if t == min(e[0] for e in compose() if e[4] == 'curse'):
                M.add('perc', gong.play(100), t, 0.6, ph)
        elif part == 'swear':
            M.add('winds', bsn.play(m - 12, v, dur=d * 1.1, release=0.15), t, 0.9, pa(t))
            M.add('brass', tbn.play(m - 12, v - 16, dur=d * 1.1, release=0.15), t, 0.5, pa(t))
        elif part == 'oath':
            M.add('low', tuba.play(m, v, dur=d, release=0.5), t, 0.9, ph)
            if m == note('E2'):
                M.add('perc', timp.play(v, pitch=-6), t, 0.9, ph)
        elif part == 'away':
            M.add('winds', clar.play(m + 12, v, dur=d, release=0.2), t, 0.5, river)
        elif part == 'dawn':
            hold('strings', vc, m, t, t + d, v, river * 0.6, rise=0.2, fall=1.0, gain=0.75)
            if m >= note('D3'):
                M.add('brass', horn.play(m, v - 16, dur=d * 1.05, release=0.4), t, 0.5, river * 0.6)
        elif part == 'morning':
            hold('strings', vln, m + 12, t, t + d, v, 0.0, rise=5.0, fall=1.5, gain=0.45)
