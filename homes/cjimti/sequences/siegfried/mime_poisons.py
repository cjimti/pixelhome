"""The Poisoned Drink: day in the forest. Siegfried stands at the middle of Porch Front with the Ring's gold glint
on him; Mime waits on Right. The Woodbird darts back in from the free end of Right and gives its warning call
(Donington 27a): since he tasted the dragon's blood, Siegfried will hear what Mime means, not what he says.

Mime creeps up over Porch Right all smiles, his smithing motif (50) sweet in the oboe and his whining nursery song
(72) on the bassoon, and a soft warm yellow glow pulses round him. But under every phrase his true thoughts break
through: a sickly poison green wave bursts out of him over the whole house, harder and faster as he gives himself
away, with his frustrated motif (71) snarling in the low strings and xylophone.

He holds out the drink: a pool of poison green bubbles between them on Porch Front. Nothung's motif (43) rings out
on the trumpet and the sword strikes: one white flash over the house, and Mime's yellow bursts into sparks that fly
out to both ends and are gone. Far off at the free end of Right, Alberich's laugh, his curse (13) in the basses,
rolls in as a red ripple. Then Siegfried's motif (53) sounds alone on the horn, and the bird comes back to sing
(27) and settles on Right.

compose() holds every note; stage(), forest(), figure() and sparks() are the forest and the cave, shared word for
word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.leitmotifs import play

CODE = 'SF21'
TITLE = 'The Poisoned Drink'
KIND = 'show'
DESCRIPTION = ('Mime comes to Siegfried all sweetness, but now Siegfried can hear what he really means, in green '
               'flashes of poison. Mime holds out a poisoned drink, and the sword strikes him down.')
VOICEOVER = ('Mime smiles, and offers a drink. But Siegfried can hear what he is really thinking. '
             'The drink is poison.')

K = 10                                      # this scene's place on Act II's shared clock: T = t + 80 K
BEAT = 0.5
T_WARN = 3.5                                # the bird's warning call
T_CREEP = 7.0                               # Mime creeps up
T_SWEET = [9.0, 21.0, 33.0]                 # his smithing motif, sweet in the oboe
T_LAMENT = [14.0, 27.0]                     # his nursery song
T_THOUGHT = [12.0, 17.5, 22.5, 26.0, 30.0, 33.5, 36.5, 38.8, 40.6]   # his true thoughts breaking through
T_DRINK = 42.0                              # he holds out the drink
T_NOTHUNG = 48.6                            # the sword's motif
T_STRIKE = 50.0                             # the blow
T_LAUGH = 54.5                              # Alberich's laugh, far off
T_HERO = 60.0
T_SONG = 66.0                               # the bird sings again and settles
D = 80.0

NIGHT = hexc('#14a878')
MOON = hexc('#6080ff')
DAY = hexc('#18a020')
SUN = hexc('#ffd040')
CAVE = hexc('#8a2000')
SCALE = hexc('#c88a20')
EYE = hexc('#ff0000')
STONE = hexc('#8a8a80')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
ALBERICH = hexc('#ff1000')
MUD = hexc('#5a1200')
WHITE = hexc('#ffffff')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
BIRD = hexc('#ff30d0')
HOT = hexc('#fff0ff')
MIME = hexc('#e0c800')
SWEET = hexc('#ffd860')
POISON = hexc('#60ff20')
STEEL = hexc('#e8f8ff')
HILT = hexc('#ffcc40')

DAY_LV = dict(night=0.2, day=0.7, shafts=0.75, cave=0.35, eyes=0.0)


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def stage(G):
    """The forest outside Fafner's cave as profiles over the house: the porch is the cave mouth (darkest at the
    back, the middle of Porch Front), Left, Right and Side the trees, with two eyes on Porch Front."""
    d = G.pd
    rng = np.random.default_rng(1857)       # the same trees and light in every scene, so the cuts match
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right'])
    mid = at(G, 'Porch Front', 0.5)
    return dict(
        d=d, mid=mid, porch=porch,
        trees=(~porch) * (0.6 + 0.4 * smooth_noise(rng, d, 35.0)),
        mouth=porch * (0.35 + 0.65 * np.exp(-((d - mid) / 160) ** 2)),
        eyes=np.exp(-((d - at(G, 'Porch Front', 0.4)) / 5) ** 2) + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 5) ** 2),
        edge=porch * (1 - np.exp(-((d - mid) / 220) ** 2)),
        shaft_at=rng.uniform(0, d.max(), 9), shaft_v=rng.uniform(-14, 14, 9), shaft_w=rng.uniform(25, 60, 9),
        leaf=Flicker(rng, G.N, 0.1, 0.6),
        smoulder=Flicker(rng, G.N, 0.3, 1.5),
    )


def forest(S, T, lv):
    """The forest at shared time T with levels lv (night, day, shafts, cave, eyes)."""
    d, leaf = S['d'], S['leaf'](T)
    fr = light(NIGHT, lv['night'] * S['trees'] * (0.85 + 0.15 * leaf))
    fr += light(DAY, lv['day'] * S['trees'] * (0.8 + 0.2 * leaf))
    fr += light(NIGHT, 0.4 * (lv['night'] + lv['day']) * S['edge'])
    L = d.max()
    shafts = np.zeros_like(d)
    for p, v, w in zip(S['shaft_at'], S['shaft_v'], S['shaft_w']):
        c = (p + v * T) % L
        shafts += np.exp(-((d - c) / w) ** 2)
    shafts *= ~S['porch']
    fr += light(MOON, lv['shafts'] * (1 - min(1.0, 2 * lv['day'])) * shafts)
    fr += light(SUN, lv['shafts'] * min(1.0, 2 * lv['day']) * shafts)
    fr += light(CAVE, lv['cave'] * S['mouth'] * (0.75 + 0.25 * S['smoulder'](T)))
    fr += light(EYE, lv['eyes'] * S['eyes'])
    return fr


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the forest, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


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



def woodbird(fr, S, pos, t, lvl, T):
    """The Woodbird: a hot magenta point with a white-hot centre, its wings flickering, a short comet trail."""
    d = S['d']
    flick = 0.78 + 0.22 * np.sin(2 * np.pi * 11 * T)
    for k, lag in enumerate((0.24, 0.16, 0.08)):
        fr = fr + light(BIRD, 0.35 * (k + 1) / 3 * lvl * np.exp(-((d - pos(t - lag)) / 9) ** 2))
    p = pos(t)
    fr = fr + light(BIRD, lvl * flick * np.exp(-((d - p) / 8) ** 2))
    fr = fr + light(BIRD, 0.35 * lvl * np.exp(-((d - p) / 30) ** 2))
    return fr + light(HOT, 0.8 * lvl * np.exp(-((d - p) / 3) ** 2))


def compose():
    """Every note: (time, seconds, midi, velocity, part, k)."""
    N = []

    def add(t, d, m, v, part, k=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, k))

    for t, m, v, d in play('woodbird_call', T_WARN, 0.5, 0, 92):
        add(t, d, m, v, 'call')
    for k, t0 in enumerate(T_SWEET):
        for t, m, v, d in play('mime', t0, 0.55, 12, 78):
            add(t, d, m, v, 'sweet', k)
    for k, t0 in enumerate(T_LAMENT):
        for t, m, v, d in play('mime_lament', t0, 0.5, 0, 74):
            add(t, d, m, v, 'lament', k)
    for k, t0 in enumerate(T_THOUGHT):
        for t, m, v, d in play('mime_frustrated', t0, 0.4, -12, 92 + 3 * k):
            add(t, d, m, v, 'thought', k)
    for m in ('E3', 'F3', 'Ab3', 'B3'):
        add(T_DRINK, T_STRIKE - T_DRINK, m, 66, 'drink')
    for t, m, v, d in play('nothung', T_NOTHUNG, 0.35, 0, 118):
        add(t, d, m, v, 'nothung')
    add(T_STRIKE, 0.1, 'C1', 125, 'strike')
    for t, m, v, d in play('curse', T_LAUGH, 0.6, -24, 92):
        add(t, d, m, v, 'laugh')
    for k, t0 in enumerate((T_HERO, T_HERO + 3.5)):
        for t, m, v, d in play('siegfried', t0, 0.55, -12, 98 - 8 * k):
            add(t, d, m, v, 'hero', k)
    for t, m, v, d in play('woodbird', T_SONG, 0.55, 0, 88, line='melody'):
        add(t, d, m, v, 'bird')
    for t, m, v, d in play('woodbird', T_SONG, 0.55, 0, 56, line='bass'):
        add(t, d, m, v, 'birdbed')
    for m in ('E2', 'B2', 'E3'):
        add(0.0, D, m, 50, 'murmur')
    return sorted(N, key=lambda e: e[0])


def bird_track(G):
    """Where the bird is: back in from the free end of Right, a hop on its warning, hops on its song, home."""
    N = compose()
    rng = np.random.default_rng(271)
    perch, home = at(G, 'Right', 0.2), at(G, 'Right', 0.3)
    pts = [(0.0, G.pd.max() + 60), (2.0, G.pd.max() + 60), (3.4, perch)]
    p = perch
    for e in N:
        if e[4] in ('call', 'bird'):
            p = float(np.clip(p + rng.uniform(-40, 40), at(G, 'Right', 0.08), at(G, 'Right', 0.5)))
            pts += [(e[0], pts[-1][1]), (e[0] + 0.25, p)]
    pts += [(T_SONG + 6.5, p), (T_SONG + 7.5, home)]
    return lambda t: keys(t, pts)


def render(G, seed=21):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    bird = bird_track(G)
    bird_on = np.array([e[0] for e in N if e[4] in ('call', 'bird')])
    sweet = [e for e in N if e[4] in ('sweet', 'lament')]
    hero_on = (T_HERO, T_HERO + 3.5)
    p_s = at(G, 'Porch Front', 0.5)
    p_cup = at(G, 'Porch Front', 0.62)
    m_from, m_to = at(G, 'Right', 0.4), at(G, 'Porch Front', 0.72)
    rng = np.random.default_rng(seed)
    bubble = Flicker(rng, G.N, 2.0, 6.0)
    scatter = [(T_STRIKE, 1.0, m_to)]

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = dict(DAY_LV)
        dread = smoothstep(T_THOUGHT[0], T_DRINK, t) * (1 - smoothstep(T_STRIKE, T_STRIKE + 3, t))
        lv['day'] *= 1 - 0.7 * dread
        lv['shafts'] *= 1 - 0.8 * dread
        fr = forest(S, T, lv)

        # Mime: creeping up over Porch Right, a sweet warm glow round him on every sweet phrase
        pm = keys(t, [(T_CREEP, m_from), (T_CREEP + 5, m_to)])
        if t < T_STRIKE:
            for t0, dur, m, v, part, k in sweet:
                a = t - t0
                if 0 <= a < dur + 0.6:
                    fr += light(SWEET, 0.5 * np.exp(-a / (dur + 0.3)) * np.exp(-((d - pm) / 110) ** 2))
            # his true thoughts: a poison green wave bursting out of him over the whole house
            for k, t0 in enumerate(T_THOUGHT):
                a = t - t0
                if 0 <= a < 2.0:
                    g = (0.75 + 0.03 * k) * np.exp(-a / 0.8)
                    fr += light(POISON, (0.55 + 0.04 * k) * np.exp(-a / 0.35))
                    fr += light(POISON, g * np.exp(-((np.abs(d - pm) - 900 * a) / (220 + 15 * k)) ** 2))
                    fr += light(WHITE, 0.7 * np.exp(-a / 0.1) * np.exp(-((d - pm) / 30) ** 2))
            fr = figure(fr, S, pm, MIME, 0.7 + 0.1 * dread)

        # the drink: a pool of poison bubbling between them
        if T_DRINK <= t < T_STRIKE + 0.4:
            grow = smoothstep(T_DRINK, T_DRINK + 2, t)
            pool = np.exp(-((d - p_cup) / 40) ** 2)
            fr += light(POISON, (0.55 + 0.35 * np.clip(bubble(T), 0, None)) * grow * pool)
            fr += light(WHITE, 0.6 * grow * np.clip(bubble(T * 1.7) - 0.85, 0, None) * 4 * pool)

        # Siegfried; Nothung flashing on its motif, then the blow
        fr = figure(fr, S, p_s, SIEGFRIED, 0.8)
        fr += light(HEAD, 0.5 * np.exp(-((d - p_s) / 4) ** 2))
        fr += light(GOLD, 0.8 * np.exp(-((d - p_s - 9) / 4) ** 2))
        if T_NOTHUNG <= t < T_STRIKE:
            a = t - T_NOTHUNG
            blade = smoothstep(p_s + 5, p_s + 15, d) * smoothstep(p_s + 15 + 80 * min(1, a / 1.0) + 5,
                                                                  p_s + 15 + 80 * min(1, a / 1.0) - 5, d)
            fr += light(STEEL, 0.95 * blade)
            fr += light(HILT, 0.9 * np.exp(-((d - p_s - 10) / 4) ** 2))
        if T_STRIKE <= t < T_STRIKE + 2:
            a = t - T_STRIKE
            fr += light(WHITE, 0.9 * np.exp(-a / 0.25))
            fr += light(STEEL, 0.9 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - m_to) - 1100 * a) / 140) ** 2))
            fr += light(MIME, 0.9 * np.exp(-a / 0.5) * np.exp(-((np.abs(d - m_to) - 700 * a) / 120) ** 2))
        # Mime scattered: his yellow bursts into sparks to both ends of the house
        fr += light(MIME, np.clip(1.4 * sparks(S, scatter, t, 22, n=70, reach=1.3), 0, 1))

        # Alberich's laugh, far off: a red ripple rolling in from the free end of Right
        if T_LAUGH <= t < T_LAUGH + 5:
            a = t - T_LAUGH
            for j in range(3):
                b = a - 0.9 * j
                if b > 0:
                    fr += light(BLOOD, 0.95 * np.exp(-b / 1.5) * np.exp(-((d - (L - 650 * b)) / 160) ** 2))
            fr += light(ALBERICH, 0.8 * np.exp(-a / 0.8) * np.exp(-((d - L) / 50) ** 2))

        # his strength: emerald surges out from him
        for t0 in hero_on:
            a = t - t0
            if 0 <= a < 2.5:
                fr += light(SIEGFRIED, 0.9 * np.exp(-a / 1.0) * np.exp(-((np.abs(d - p_s) - 800 * a) / 160) ** 2))

        # the bird: flashes rippling out on each note
        if t >= 2.0:
            i = int(np.searchsorted(bird_on, t, side='right')) - 1
            if i >= 0 and t - bird_on[i] < 0.8:
                a = t - bird_on[i]
                fr += light(BIRD, 0.6 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - bird(t)) - 500 * a) / 50) ** 2))
            fr = woodbird(fr, S, bird, t, 0.9, T)
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

    for name, gain, rev in (('low', 0.36, 0.25), ('brass', 0.33, 0.3), ('perc', 0.33, 0.28), ('winds', 0.36, 0.32),
                            ('strings', 0.26, 0.35), ('mallet', 0.22, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    fl = M.sampler('Woodwinds/Flute/susNV/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Sus/*.wav', tune=-12)
    ob_st = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')

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

    bird = bird_track(G)
    hero = pan_at(at(G, 'Porch Front', 0.5))
    mime_from, mime_to = pan_at(at(G, 'Right', 0.4)), pan_at(at(G, 'Porch Front', 0.72))

    def pan_mime(t):
        return mime_from + (mime_to - mime_from) * float(smoothstep(T_CREEP, T_CREEP + 5, t))

    far = pan_at(G.pd.max())
    for t, d, m, v, part, k in compose():
        if part in ('call', 'bird'):
            M.add('winds', fl.play(m, v, dur=d * 1.1, release=0.15), t, 0.9, pan_at(bird(t)))
            M.add('winds', ob_st.play(m, v - 22), t, 0.35, pan_at(bird(t)))
        elif part == 'birdbed':
            M.add('strings', harp.play(m, v), t, 0.6, pan_at(bird(t)))
        elif part == 'sweet':
            M.add('winds', ob.play(m, v, dur=d * 1.1, release=0.2), t, 0.8, pan_mime(t))
            M.add('strings', harp.play(m - 12, v - 16), t, 0.5, pan_mime(t))
        elif part == 'lament':
            M.add('winds', bsn.play(m, v, dur=d * 1.1, release=0.2), t, 0.85, pan_mime(t))
        elif part == 'thought':
            M.add('mallet', xylo.play(m + 24, v - 8), t, 0.7, pan_mime(t))
            M.add('low', vcs.play(m, v), t, 0.85, pan_mime(t))
            M.add('low', cbs.play(m - 12, v - 8), t, 0.6, pan_mime(t))
            if t == T_THOUGHT[k]:
                M.add('perc', timp.play(v - 16, pitch=-2), t, 0.5, pan_mime(t))
        elif part == 'drink':
            hold('strings', vtrem, m, t, t + d, v, mime_to, rise=1.5, fall=0.3, gain=0.4)
        elif part == 'nothung':
            M.add('brass', tpt.play(m, v, dur=d * 1.1, release=0.25), t, 0.95, hero)
        elif part == 'strike':
            M.add('perc', crash.play(v), t, 1.0, mime_to)
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, mime_to)
            M.add('brass', tbn.play(note('D2'), 118, dur=1.5, release=0.6), t, 0.8, mime_to)
        elif part == 'laugh':
            if d > 1.0:
                hold('low', vc, m + 12, t, t + d, v, far, rise=0.1, fall=0.8, gain=0.6)
            else:
                M.add('low', cbs.play(m + 12, v), t, 0.8, far)
            M.add('brass', tbn.play(m + 12, v - 16, dur=d * 1.05, release=0.3), t, 0.5, far)
        elif part == 'hero':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.3), t, 0.85, hero)
            M.add('strings', vc.play(m - 12, v - 16, dur=d * 1.1, release=0.3), t, 0.5, hero)
        elif part == 'murmur':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.0, rise=3.0, fall=2.0, gain=0.26)
