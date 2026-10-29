"""The Town Square: Halloween Town's big night opens. A lantern gutters over the front door and green
mist creeps in from both free ends; then the town turns up one run at a time on the downbeat: a grinning
jack-o'-lantern pops up over the porch, two ghosts on the porch sides, a bat flapping on each wing, and a
black cat (two green eyes and an arched back) out at the end of the right wing. Side only ever carries mist. The march starts and the characters sing the
tune between them, a note each in turn: pumpkin, ghosts, bats, cat. In the bridge a wave runs along them
and back, each jumping as it passes; then they all bob together while the pumpkin shouts rings out from
the door. The beat doubles and they go wild: bats loop their wings, ghosts zoom up and down the porch
sides, the pumpkin's eyes flash left-right. Everything freezes in violet while the pumpkin's eyes look
left, then right. SHOUT: everyone jumps, stomp, stomp, STOMP, a big bright final chord, the pumpkin winks,
and one last hit.

Characters are drawn as spans in path distance with exact span-over-pixel coverage (as in Bone Yard),
so they keep their size on every run. Times are module constants on the 120 BPM grid, shared with
score()."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes, Flicker

CODE = 'NB01'
TITLE = 'The Town Square'
KIND = 'show'
DESCRIPTION = ('Halloween Town turns up a run at a time: a jack-o\'-lantern, two ghosts, two bats and a black cat, '
               'who sing the march between them, go wild on the double-time, and finish with a shout and a wink.')

BPM = 120
BEAT = 60 / BPM
ORANGE = hexc('#ff5200')
YELLOW = hexc('#ffc030')
HOT = hexc('#ffa030')
MIST = hexc('#50ff20')
VIOLET = hexc('#5a10ff')
GHOST = hexc('#dfe8ff')
BAT = hexc('#9a3cff')
RED = hexc('#ff2010')
CAT = hexc('#3a4cff')
EYES = hexc('#60ff20')

CHARS = [  # who, the run they stand on, kind, when they pop up, where along the run (-1..1 of its half), facing
    ('pumpkin', 'Porch Front', 'pumpkin', 8.0, 0.0, 1.0),
    ('ghost L', 'Porch Left', 'ghost', 12.0, 0.0, 1.0),
    ('ghost R', 'Porch Right', 'ghost', 12.0, 0.0, 1.0),
    ('bat L', 'Left', 'bat', 16.0, 0.0, 1.0),
    ('bat R', 'Right', 'bat', 16.0, -0.45, 1.0),
    ('cat', 'Right', 'cat', 20.0, 0.45, -1.0),          # out by the free end, facing the house
]
KINDS = {c[0]: c[2] for c in CHARS}
ROLE = {'pumpkin': 0, 'ghost': 1, 'bat': 2, 'cat': 3}       # who sings which beat of the bar
WAVE = ['bat L', 'ghost L', 'pumpkin', 'ghost R', 'bat R', 'cat', 'bat R', 'ghost R', 'pumpkin',
        'ghost L']                                         # the bridge's wave, along and back, a beat each
TOWN = CHARS[0][3]                           # the band starts when the pumpkin pops up
CALL, BRIDGE, HOOK, DOUBLE, BREATH, SHOUT = 20.0, 32.0, 40.0, 44.0, 50.0, 52.0
STOMPS = (53.5, 54.0, 55.0)
FINAL, WINK, BUTTON = 55.0, 58.5, 59.0
D = 60.0


def _back(u, c1=1.7):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def _hit(f, k=0.12):
    """Flash envelope f seconds after a hit."""
    return float(np.exp(-f / k)) if f >= 0 else 0.0


def blob(x, c, w):
    return np.exp(-((x - c) / w) ** 2)


def _beat(t, t0):
    j, f = divmod((t - t0) / BEAT, 1)
    return int(j), f * BEAT


def _state(name, kind, t0, t, ph):
    """One character's animation at t: centre offset, scale, flash, eye look, and a kind-specific
    'act' (pumpkin: eye boost, ghost: ooh, bat: wing flap, cat: arch)."""
    if t < t0:
        return None
    off, sc, fl, look, act = 0.0, 1.0, 0.0, 0.0, 0.0
    u = (t - t0) / 0.4
    sc = _back(u) if u < 1 else 1.0
    fl = _hit(t - t0, 0.25)
    out = -1.0 if name in ('ghost L', 'bat L') else 1.0     # away from the middle of the house
    if kind == 'ghost':
        off = 8 * np.sin(2 * np.pi * t / (4 * BEAT) + ph)
    elif kind == 'bat':
        off = 18 * np.sin(2 * np.pi * t / 1.7 + ph)
    if CALL <= t < BRIDGE:                       # each sings its beat of the bar
        j, f = _beat(t, CALL)
        if j % 4 == ROLE[kind]:
            a = _hit(f, 0.18)
            act += a
            fl += 0.8 * a
            sc += 0.15 * a
            if kind == 'ghost':
                off += out * 25 * a
    elif BRIDGE <= t < HOOK:                     # the wave
        j, f = _beat(t, BRIDGE)
        if WAVE[j % len(WAVE)] == name:
            a = _hit(f, 0.2)
            sc += 0.3 * a
            fl += a
            act += a
    elif HOOK <= t < DOUBLE:                     # everyone together
        j, f = _beat(t, HOOK)
        a = _hit(f, 0.15)
        sc += 0.15 * a
        fl += 0.5 * a
        act += 0.6 * a
    elif DOUBLE <= t < BREATH:                   # wild
        j, f = divmod((t - DOUBLE) / (BEAT / 2), 1)
        a = _hit(f * BEAT / 2, 0.08)
        fl += 0.4 * a
        wild = smoothstep(DOUBLE, DOUBLE + 1, t)
        if kind == 'bat':
            off = lerp(off, 90 * np.sin(2 * np.pi * (t - DOUBLE) / 1.2 + ph), wild)
            act = 1.0
        elif kind == 'ghost':
            off = lerp(off, 110 * np.sin(2 * np.pi * (t - DOUBLE) / 0.9 + ph), wild)
        elif kind == 'pumpkin':
            look = 12 if int(j) % 2 else -12
        else:
            act = 1.0
    elif BREATH <= t < SHOUT:                    # frozen; eyes look left, then right
        look = keys(t, [(BREATH + 0.2, 0), (BREATH + 0.45, -12), (BREATH + 1.0, -12), (BREATH + 1.25, 12),
                        (SHOUT - 0.2, 12), (SHOUT, 0)])
        fl = -0.45
    else:
        fl += _hit(t - SHOUT, 0.4)
        sc += 0.35 * _hit(t - SHOUT, 0.5)
        for ts in STOMPS:
            a = _hit(t - ts, 0.15)
            sc += 0.25 * a
            fl += 0.7 * a
            act += a
        if t >= FINAL:
            sc += 0.1 * smoothstep(FINAL, FINAL + 0.3, t)
            fl += 0.25 + 1.0 * _hit(t - BUTTON, 0.2)
            act += 0.5
    return off, sc, fl, look, act


def _sprite(kind, c, s, st, t, ph):
    """Spans (a, z, I, layer) for one character centred at c, facing s (+1 along the path)."""
    off, sc, fl, look, act = st
    c = c + off
    sc *= SIZE[kind]
    I = np.clip(0.75 + 0.35 * fl, 0.25, 1.6)
    sp = []

    def add(a, z, w, layer):
        sp.append((c + s * a * sc, c + s * z * sc, w * I, layer))

    if kind == 'pumpkin':
        e = look
        wink = WINK <= t < WINK + 0.45
        eyes = [(-50 + e, -26 + e), (26 + e, 50 + e)]
        edges = [-72, eyes[0][0], eyes[0][1], -7, 7, eyes[1][0], eyes[1][1], 72]
        for a, z in zip(edges[0::2], edges[1::2]):
            add(a, z, 0.8, 'orange')
        for k, (a, z) in enumerate(eyes):
            add(a, z, 0 if (wink and k == 1) else 1.0 + 0.5 * act, 'yellow')
            if wink and k == 1:
                add(a, z, 0.8, 'orange')
        add(-7, 7, 0.85, 'yellow')
    elif kind == 'ghost':
        e = look * 0.6
        for a, z in ((-30, -16 + e), (-8 + e, 8 + e), (16 + e, 30)):
            add(a, z, 0.8 + 0.4 * act, 'ghost')
        T = 34 + 14 * np.sin(2 * np.pi * 1.4 * t + ph)
        for q, k in enumerate((0.5, 0.3, 0.14)):
            add(30 + T * q / 3, 30 + T * (q + 1) / 3, k, 'ghost')
    elif kind == 'bat':
        flap = abs(np.sin(2 * np.pi * (3.0 + 3.0 * min(act, 1)) * t + ph))
        W = 16 + 26 * flap + 18 * min(act, 1)
        for a, z in ((-10, -6), (-2, 2), (6, 10)):
            add(a, z, 0.9, 'bat')
        for a, z in ((-6, -2), (2, 6)):
            add(a, z, 1.0, 'red')
        add(-10 - W, -10, 0.55, 'bat')
        add(10, 10 + W, 0.55, 'bat')
    else:                                        # the cat, facing the front of the house
        arch = min(act, 1)
        blink = ((t + ph) % 3.1) < 0.12
        flick = 12 * np.sin(2 * np.pi * 0.6 * t + ph) + 15 * arch
        add(-100 + flick, -58, 0.35 + 0.2 * arch, 'cat')
        add(-58, 14 + 6 * arch, 0.45 + 0.35 * arch, 'cat')
        e = look * 0.5
        for a, z in ((18, 24 + e), (31 + e, 37 + e), (44 + e, 50)):
            add(a, z, 0.55, 'cat')
        for a, z in ((24 + e, 31 + e), (37 + e, 44 + e)):
            add(a, z, 0 if blink or (WINK <= t < WINK + 0.45 and a > 30) else 1.0 + 0.6 * arch, 'eyes')
    return sp


SIZE = {'pumpkin': 1.0, 'ghost': 1.35, 'bat': 1.5, 'cat': 1.25}
def _place(G, run, frac):
    """Path distance of a point frac (-1..1) of the way along a run's half length from its middle."""
    dd = G.pd[G.seg[run]]
    return float(dd.mean() + frac * (dd.max() - dd.min()) / 2)


LAYERS = {'orange': ORANGE, 'yellow': YELLOW, 'ghost': GHOST, 'bat': BAT, 'red': RED, 'cat': CAT, 'eyes': EYES}


def render(G, seed=31):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    w = np.gradient(d)
    e0, e1 = d - w / 2, d + w / 2
    mid = G.pd[G.seg['Porch Front']].mean()
    r = np.abs(d - mid)                          # along the roof from the front door
    side = np.isin(np.arange(G.N), G.pi[G.seg['Side']])
    flick = Flicker(rng, G.N, 4, 11)
    chars = []
    first = {}
    for name, run, kind, t0, frac, s in CHARS:
        chars.append((name, kind, t0, _place(G, run, frac), s, rng.uniform(0, 2 * np.pi)))
        first[run] = min(first.get(run, t0), t0)
    lit = {run: np.isin(np.arange(G.N), G.pi[G.seg[run]]) for run in first}

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))

        # the lantern over the door until the pumpkin pops up in its place
        lan = keys(t, [(1, 0), (3, 0.5), (7.6, 0.5), (8.05, 0)])
        fr += light(ORANGE, lan * (1 + 0.15 * flick(t)) * blob(r, 0, 30))

        # green mist over the whole roof from the start, thinning once the town is up (Side keeps it)
        mlev = keys(t, [(0.8, 0), (3, 0.2), (18, 0.2), (22, 0.07), (BREATH, 0.07), (BREATH + 0.4, 0)])
        wob = 0.5 + 0.5 * np.sin(d / 70 - 0.9 * t) * np.sin(d / 31 + 0.5 * t + 1)
        fr += light(MIST, (mlev + 0.08 * side * keys(t, [(20, 0), (23, 1), (BREATH, 1), (BREATH + 0.4, 0)])) *
                    (0.4 + 0.6 * wob))

        # a warm glow under each run once its character is up, pulsing on the beat
        bed = np.zeros(G.N)
        for run, t0 in first.items():
            if t >= t0:
                bed += lit[run] * 0.1 * smoothstep(t0, t0 + 0.5, t)
        pulse = 1.0
        if TOWN <= t < BREATH:
            pulse = 1 + 0.6 * _hit(((t - TOWN) % BEAT), 0.1)
        bed *= pulse * keys(t, [(BREATH, 1), (BREATH + 0.2, 0.3), (SHOUT, 0.3), (SHOUT + 0.1, 1.6), (FINAL, 1.3),
                               (BUTTON + 0.4, 1.3), (D - 0.3, 0)])
        fr += light(ORANGE, bed)

        # the chant: rings out from the door every two beats in the hook
        if HOOK <= t < DOUBLE + 1.5:
            ring = np.zeros(G.N)
            for tw in np.arange(HOOK, DOUBLE, 2 * BEAT):
                age = t - tw
                if 0 < age < 1.5:
                    ring = np.maximum(ring, (1 - age / 1.5) * blob(r, 80 + 700 * age, 40))
            fr += light(HOT, 0.45 * ring)

        # the characters
        spans = []
        for name, kind, t0, c, s, ph in chars:
            st = _state(name, kind, t0, t, ph)
            if st is not None:
                spans += _sprite(kind, c, s, st, t, ph)
        fade = 1 - smoothstep(D - 0.6, D - 0.1, t)
        if spans:
            for layer, col in LAYERS.items():
                sp = [x for x in spans if x[3] == layer]
                if not sp:
                    continue
                a = np.array([(min(p[0], p[1]), max(p[0], p[1]), p[2]) for p in sp])
                ov = np.clip(np.minimum(a[:, 1:2], e1) - np.maximum(a[:, 0:1], e0), 0, None) / w
                fr += light(col, np.clip(a[:, 2] @ ov, 0, 1.2) * fade)

        # holding its breath; the shout; the button
        fr += light(VIOLET, np.full(G.N, keys(t, [(BREATH, 0), (BREATH + 0.4, 0.12), (SHOUT - 0.1, 0.22), (SHOUT, 0)])))
        if SHOUT <= t < SHOUT + 3:
            fr += light(HOT, 0.9 * _hit(t - SHOUT, 0.5) * np.ones(G.N))
        if STOMPS[-1] <= t < STOMPS[-1] + 2:
            fr += light(HOT, 0.45 * _hit(t - STOMPS[-1], 0.35) * np.ones(G.N))
        if BUTTON <= t:
            fr += light(HOT, 0.9 * _hit(t - BUTTON, 0.3) * fade * np.ones(G.N))
        out[f][G.path] = np.clip(fr, 0, 1)
    return out


# ---- music: D minor at 120 (a bar is 2 s). TUNE (THEME) is the town's march. Each character arrives with
# its own sound (pumpkin: a horn stab and a timpani; ghosts: an 'ooh'; bats: a squeak and a xylophone trill;
# cat: a meow), and in the call the four of them sing the tune between them, a note each on their beat:
# trumpet pumpkin, 'ooh' ghosts, xylophone bats, a meow that slides onto the cat's note. The bridge is a new
# tune in F on trumpet and clarinet with a marimba note for each jump of the wave, the hook is the band in
# unison with the choir on every ring, then double time, a held breath, the shout, stomp-stomp-STOMP, a D
# major chord, a tink for the wink and a last hit. ----

THEME = [                                   # (beat, note, beats): four bars
    (0, 'D4', 1), (1, 'F4', .5), (1.5, 'E4', .5), (2, 'D4', 1), (3, 'A3', 1),
    (4, 'Bb3', .5), (4.5, 'C4', .5), (5, 'D4', .5), (5.5, 'E4', .5), (6, 'F4', 1), (7, 'E4', 1),
    (8, 'G4', 1), (9, 'F4', .5), (9.5, 'E4', .5), (10, 'F4', 1), (11, 'D4', 1),
    (12, 'E4', .5), (12.5, 'C#4', .5), (13, 'A3', 1), (14, 'D4', 2)]
TUNE = THEME                                # the hook the finale quotes
BRIDGE_TUNE = [                             # in F: four bars
    (0, 'A4', 1), (1, 'C5', 1), (2, 'A4', .5), (2.5, 'G4', .5), (3, 'F4', 1),
    (4, 'G4', 1), (5, 'Bb4', 1), (6, 'G4', .5), (6.5, 'F4', .5), (7, 'E4', 1),
    (8, 'F4', 1), (9, 'A4', 1), (10, 'D5', 1.5), (11.5, 'C5', .5),
    (12, 'Bb4', .5), (12.5, 'A4', .5), (13, 'G4', .5), (13.5, 'E4', .5), (14, 'A4', 2)]
CHORDS = ['Dm', 'Bb', 'Gm', 'A']            # one a bar
CHORDS_B = ['F', 'C', 'Dm', 'A']
VOICE = {'Dm': ('D3', 'F3', 'A3'), 'Bb': ('D3', 'F3', 'Bb3'), 'Gm': ('D3', 'G3', 'Bb3'), 'A': ('C#3', 'E3', 'A3'),
         'F': ('C3', 'F3', 'A3'), 'C': ('C3', 'E3', 'G3'), 'D': ('D3', 'F#3', 'A3')}
ROOT = {'Dm': ('D2', 'A2'), 'Bb': ('Bb1', 'F2'), 'Gm': ('G1', 'D2'), 'A': ('A1', 'E2'), 'F': ('F1', 'C2'),
        'C': ('C2', 'G1'), 'D': ('D2', 'A1')}


def score(M, G):
    from pixelhome.audio import SR, note as n, slide
    pizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    ghost = M.synth('Pads/Ghost Pad')
    ooh = M.synth('Pads/Ooh')
    choir = M.synth('Pads/Synth Choir MW O-Ah')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fmp]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    for name, gain, rev in (('bass', 0.27, 0.08), ('band', 0.18, 0.18), ('tune', 0.26, 0.2), ('drums', 0.24, 0.12),
                            ('pad', 0.14, 0.4), ('box', 0.2, 0.35), ('voices', 0.24, 0.25), ('fx', 0.16, 0.2)):
        M.bus(name, gain=gain, reverb=rev)

    x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()

    order = np.argsort(G.pd)
    ds, xs = G.pd[order], G.pos[order, 0]
    at = {c[0]: _place(G, c[1], c[4]) for c in CHARS}

    def pan(name):                          # a character's place across the facade, from the street
        return float(0.85 * (2 * (np.interp(at[name], ds, xs) - x0) / (x1 - x0) - 1))

    who = {k: [nm for nm, kk in KINDS.items() if kk == k] for k in ROLE}

    def chord(t):
        if BRIDGE <= t < HOOK:
            return CHORDS_B[int((t - BRIDGE) // (4 * BEAT)) % 4]
        return CHORDS[int((t - TOWN) // (4 * BEAT)) % 4]

    def theme(inst, t0, bus, vel, shift=0, gain=1.0, p=0.0, tune=THEME, bars=4):
        for b, m, ln in tune:
            if b < 4 * bars:
                M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * 0.9), t0 + b * BEAT, gain, p)

    def hz(m):
        return 440 * 2 ** ((m - 69) / 12)

    def meow(t, m, p, gain=1.0):            # a slide-whistle meow that lands on m
        f = hz(m)
        s = slide(0.0, 0.14, f * 0.7, f, 0.32, 0.3) + slide(0.14, 0.32, f, f * 0.85, 0.32, 0.12)
        M.add('voices', s, t, gain, p)

    def squeak(t, p):
        M.add('fx', slide(0.0, 0.08, 1800, 2600, 0.1, 0.25), t, 0.8, p)

    # the dark, the lantern, the mist
    s = trem.play(n('D2'), 70, dur=TOWN)
    M.add('bass', s * np.linspace(0.2, 1, s.shape[1]) ** 2, 0.0, 0.9)
    notes = [(2 + b * BEAT, n(m) + 12, 70, ln * BEAT * 0.9) for b, m, ln in THEME if b < 8]
    M.add('box', box.render(notes, D), 0.0)
    mist = ghost.render([(2.0, n('D4'), 70, 6.5), (2.0, n('A4'), 60, 6.5), (2.5, n('F4'), 55, 6.0)], D)
    M.add('pad', mist, 0.0, 0.7, -0.75)
    M.add('pad', mist, 0.0, 0.7, 0.75)
    r = troll.play(90, dur=2.0)
    M.add('drums', r * np.linspace(0.1, 1, r.shape[1]) ** 2, 6.0, 0.5)

    # arrivals, each with its own sound
    hey = []
    for name, run, kind, t0, frac, _ in CHARS:
        p = pan(name)
        M.add('drums', bd.play(100), t0, 0.5, p)
        if kind == 'pumpkin':
            M.add('drums', timp.play(118), t0, 0.8, p)
            for m in VOICE['Dm']:
                M.add('band', horn.play(n(m) + 12, 112, dur=0.3), t0, 0.6, p)
            hey += [(t0, n(m) + 12, 110, 0.5) for m in VOICE['Dm']]
        elif kind == 'ghost':
            M.add('voices', ooh.render([(0.0, n('A4'), 90, 1.2)], 3.0), t0, 1.0, p)
            M.add('fx', slide(0.0, 0.6, 400, 900, 0.8, 0.2), t0, 0.6, p)
        elif kind == 'bat':
            squeak(t0, p)
            for j in range(6):
                M.add('tune', xylo.play(n('A5') if j % 2 else n('C6'), 90), t0 + 0.06 * j, 0.45, p)
        else:
            meow(t0, n('A4'), p, 1.2)
    M.add('pad', choir.render(hey, D), 0.0, 1.2, pan('pumpkin'))

    # the band
    for k, t in enumerate(np.arange(TOWN, BREATH, BEAT)):
        c, beat = chord(t), k % 4
        M.add('bass', pizz.play(n(ROOT[c][beat % 2]), 100 if beat == 0 else 84), t, 1.0, -0.1)
        if t >= 12:
            for m in VOICE[c]:
                M.add('band', bsn.play(n(m), 72, dur=0.15), t + BEAT / 2, 0.45, 0.25)
        if t >= 16 and beat in (0, 2):
            M.add('bass', tuba.play(n(ROOT[c][0]), 104), t, 0.8)
        if t >= CALL and t < DOUBLE:
            M.add('drums', snare.play(95 if beat in (1, 3) else 70), t, 0.45, 0.15)
        if t >= CALL and beat == 0:
            M.add('drums', bd.play(100), t, 0.7)
    theme(clar, 12.0, 'tune', 100)

    # the call: the characters sing the tune between them, a note each on their beat
    ghosts = []
    for rep, (t0, bars) in enumerate(((CALL, 4), (CALL + 16 * BEAT, 2))):
        for b, m, ln in THEME:
            if b >= 4 * bars:
                continue
            t = t0 + b * BEAT
            role = int(b) % 4
            kind = [k for k, v in ROLE.items() if v == role][0]
            for name in who[kind]:
                p = pan(name)
                g = 1.0 / len(who[kind]) ** 0.5
                if kind == 'pumpkin':
                    M.add('voices', tpt.play(n(m) + 12, 110, dur=ln * BEAT * 0.8), t, g, p)
                elif kind == 'ghost':
                    ghosts.append((t, n(m) + 12, 100, ln * BEAT * 0.85))
                elif kind == 'bat':
                    M.add('voices', xylo.play(n(m) + 12, 112), t, 0.9 * g, p)
                    M.add('voices', xylo.play(n(m) + 12, 90), t + 0.07, 0.5 * g, p)
                    if b == int(b):
                        squeak(t, p)
                else:
                    meow(t, n(m) + 12, p, 1.1)
                    M.add('voices', clar.play(n(m) + 12, 96, dur=ln * BEAT * 0.8), t + 0.05, 0.6, p)
    o = ooh.render(ghosts, D)
    M.add('voices', o, 0.0, 0.5, pan('ghost L'))
    M.add('voices', o, 0.0, 0.5, pan('ghost R'))

    # the bridge: a new tune in F; a marimba note for each jump of the wave
    theme(tpt, BRIDGE, 'tune', 104, gain=0.8, tune=BRIDGE_TUNE)
    theme(clar, BRIDGE, 'tune', 96, gain=0.6, tune=BRIDGE_TUNE, shift=-12)
    wave_notes = ['F4', 'G4', 'A4', 'C5', 'D5', 'F5', 'D5', 'C5', 'A4', 'G4']
    for j in range(int((HOOK - BRIDGE) / BEAT)):
        nm = WAVE[j % len(WAVE)]
        M.add('band', mar.play(n(wave_notes[j % len(WAVE)]), 108), BRIDGE + j * BEAT, 0.9, pan(nm))
    M.add('drums', crash_s.play(95), BRIDGE, 0.5)

    # the hook: everyone in unison, the choir on every ring
    theme(horn, HOOK, 'tune', 118, bars=2)
    theme(tpt, HOOK, 'tune', 108, shift=12, gain=0.6, bars=2)
    theme(xylo, HOOK, 'tune', 100, shift=12, gain=0.5, bars=2)
    hums = []
    for t in np.arange(HOOK, DOUBLE, 2 * BEAT):
        hums += [(t, n(m) + 12, 90, 2 * BEAT * 0.7) for m in VOICE[chord(t)]]
        M.add('band', bone.play(n(ROOT[chord(t)][0]) + 12, 92, dur=0.4), t, 0.5)
    M.add('pad', choir.render(hums, D), 0.0, 1.4)
    M.add('drums', crash.play(110), HOOK, 0.6)

    # double time: snare eighths, climbing brass, bats squeaking as they loop
    for k, t in enumerate(np.arange(DOUBLE, BREATH, BEAT / 2)):
        M.add('drums', snare.play(90 + int(25 * (t - DOUBLE) / (BREATH - DOUBLE))), t, 0.55, -0.35 if k % 2 else 0.35)
        if k % 3 == 0:
            squeak(t, pan('bat L') if k % 2 else pan('bat R'))
    for k, m in enumerate(('D3', 'Eb3', 'E3', 'F3', 'F#3', 'G#3')):
        M.add('band', bone.play(n(m), 90 + 5 * k, dur=0.95), DOUBLE + k, 0.7)
        M.add('band', horn_s.play(n(m) + 7, 85 + 5 * k, dur=0.95), DOUBLE + k, 0.5)
    r = troll.play(100, dur=BREATH - DOUBLE)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, DOUBLE, 0.6)

    # holding its breath (the eyes go left: tick; right: tick), then the shout
    M.add('pad', vtrem.play(n('A4'), 50, dur=SHOUT - BREATH), BREATH, 0.5)
    M.add('drums', ccresc.play(100, dur=SHOUT - BREATH + 0.05), BREATH + 0.3, 0.4)
    M.add('tune', xylo.play(n('A4'), 90), BREATH + 0.45, 0.6, -0.5)
    M.add('tune', xylo.play(n('A4'), 90), BREATH + 1.25, 0.6, 0.5)
    for m in ('D3', 'F3', 'A3', 'D4'):
        M.add('band', horn_s.play(n(m), 124, dur=1.4), SHOUT, 0.8)
    for m in ('D2', 'A2'):
        M.add('band', bone.play(n(m), 124, dur=1.4), SHOUT, 0.8)
    M.add('bass', tuba.play(n('D2'), 127), SHOUT, 1.2)
    M.add('pad', choir.render([(SHOUT, n(m) + 12, 120, 1.4) for m in VOICE['Dm']], D), 0.0, 1.4)
    M.add('drums', timp.play(127), SHOUT, 1.2)
    M.add('drums', bd_ff.play(127), SHOUT, 1.4)
    M.add('drums', crash.play(120), SHOUT, 1.0)

    # stomp, stomp, STOMP, and a big D major chord
    for k, ts in enumerate(STOMPS):
        big = 1.0 if k < 2 else 1.3
        c = 'A' if k < 2 else 'D'
        M.add('drums', bd_ff.play(120), ts, 1.0 * big)
        M.add('drums', timp.play(120, pitch=-2 if k < 2 else 0), ts, 0.8 * big)
        M.add('bass', tuba.play(n(ROOT[c][0]), 120), ts, big)
        for m in VOICE[c]:
            M.add('band', horn.play(n(m) + 12, 118, dur=0.3), ts, 0.7 * big)
            M.add('band', tpt.play(n(m) + 12, 115, dur=0.25), ts, 0.5 * big)
    dur = WINK - FINAL + 0.3
    for m in ('D3', 'F#3', 'A3', 'D4'):
        M.add('band', horn_s.play(n(m), 118, dur=dur), FINAL, 0.6)
    for m in ('F#4', 'A4'):
        M.add('band', tpt_s.play(n(m), 112, dur=dur), FINAL, 0.45)
    M.add('pad', choir.render([(FINAL, n(m) + 12, 115, dur) for m in VOICE['D']], D), 0.0, 1.3)
    M.add('bass', tuba.play(n('D2'), 125), FINAL, 1.0)
    M.add('drums', crash.play(120), FINAL, 0.9)
    r = troll.play(90, dur=dur)
    M.add('drums', r * np.linspace(0.6, 1, r.shape[1]), FINAL + 0.2, 0.4)
    for j in range(20):                     # a xylophone roll under it
        M.add('tune', xylo.play(n(('D5', 'A4')[j % 2]), 80 + j), FINAL + 0.15 * j, 0.35)

    # the wink, and the last hit
    M.add('tune', xylo.play(n('A5'), 118), WINK, 0.8, pan('pumpkin'))
    M.add('drums', tri.play(110), WINK, 0.8, pan('pumpkin'))
    M.add('fx', slide(0.0, 0.2, 700, 1500, 0.22, 0.25), WINK + 0.05, 0.7, pan('pumpkin'))
    for m in ('D3', 'A3', 'D4'):
        M.add('band', horn.play(n(m) + 12, 125, dur=0.3), BUTTON, 0.8)
        M.add('band', tpt.play(n(m) + 12, 122, dur=0.25), BUTTON, 0.7)
    M.add('bass', tuba.play(n('D2'), 127, dur=0.3), BUTTON, 1.2)
    M.add('drums', bd_ff.play(127), BUTTON, 1.3)
    M.add('drums', timp.play(127), BUTTON, 1.0)
    M.add('drums', crash_s.play(120), BUTTON, 1.0)
