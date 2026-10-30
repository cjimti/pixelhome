"""Waking the Dragon: night outside Fafner's cave, after the stand-off, the Wanderer in blue at Left 0.7 and
Alberich in red at Right 0.3.

The music is Wagner's own, from Act II as Solti's 1958 Vienna Philharmonic recording takes it: the Wanderer's call
into the cave and the dragon stirring (bars 388 to 401), Fafner's "Ich lieg' und besitz': laßt mich schlafen!"
(440 to 448), and the storm in which the Wanderer rides away (474 to 487). The notes come from the Wagner Ring
Dataset's piano reduction (pixelhome/ring.py): the low tremolo on cellos and basses, the dragon's tritones (Eb and
A) on tuba and basses, and the storm's rushing scales and chords on the full orchestra. Fafner's own voice,
which the reduction leaves out, is played as written on tuba and trombones, the way his voice comes through a
speaking-trumpet on stage: "Wer stört mir den Schlaf?" (A, A, A, G, C sharp) and "Ich lieg' und besitz': laßt
mich schlafen!" (F, B, F, F, B; C, C, C, G flat), from the printed vocal score (Schirmer, archive.org
31761034115105, pp. 165 and 167). A production adds the dragon: a deep growl as the eyes open, a slow breath
out of the cave as he yawns and settles, and the wind and a thunderclap as the Wanderer rides off.

The Wanderer calls into the cave: each call throws a pale blue beam down the front of the house into the porch.
Alberich shouts too, red bursts flung into the cave mouth. The dragon stirs: every low note of his tritone heaves
an ochre shudder out of the cave, run by run, and as the tremolo surges two red eyes snap open on Porch Front in
a red flash over the whole house. Each word of his voice floods the house in stone and scale from the cave out.
Then he yawns ("laßt mich schlafen"): the eyes sink shut and the cave fades back to a smoulder. The Wanderer
laughs and goes: he turns into a blue storm-light and sweeps the length of the house out the free end of Right
past Alberich, who shrinks into the dark and hides, his curse grumbling low.

compose() tags every note of the excerpt and Fafner's line; stage(), forest(), figure() and sparks() are the
forest and the cave, shared word for word by Act II's scenes on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, keys, Flicker, smooth_noise
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'SF13'
TITLE = 'Waking the Dragon'
KIND = 'show'
DESCRIPTION = ('The Wanderer and the dwarf shout into the cave. Two red eyes open, a huge voice asks who disturbs '
               'its sleep, then yawns and goes back to sleep. The Wanderer vanishes in a gust of blue.')
VOICEOVER = ('Wake up, dragon, they shout into the cave. And something very large opens its eyes.')

K = 2                                       # this scene's place on Act II's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act II, bars 388-401, 440.5-448 and 474-487, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
SUNG = {(s[2], s[3][:6]): s[0] for s in EX['singing']}
T_SHOUT = [s[0] for s in EX['singing'] if s[2] == 'Alberich' and s[0] < BAR[402]]
T_EYES = BAR[395]                           # the tremolo surges: the eyes snap open
T_YAWN = BAR[447]                           # "schla-fen": the eyes sink shut
T_GO = BAR[474]                             # the Wanderer rides off in the storm
T_HIDE = [s[0] for s in EX['singing'] if s[2] == 'Alberich' and s[0] > T_GO]
# Fafner's voice, from the vocal score: (bar, beat, beats, note), 3/4
VOICE = [(398, 1, 2, 'A3'), (399, 0, 3, 'A3'), (400, 0, 2, 'A3'), (400, 2, 1, 'G3'), (401, 0, 3, 'C#3'),
         (440, 2, 1, 'F3'), (441, 0, 4, 'B2'), (442, 2, 0.75, 'F3'), (442, 2.75, 0.25, 'F3'), (443, 0, 4, 'B2'),
         (446, 0, 2, 'C3'), (446, 2, 1, 'C3'), (447, 0, 3, 'C3'), (448, 0, 1, 'Gb2')]

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
WANDERER = hexc('#1a3cff')
WANDER_SOFT = hexc('#5a78ff')
SPEAR = hexc('#c8d8ff')

START = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)       # where SF12 left the forest
END = dict(night=0.65, day=0.0, shafts=0.65, cave=0.35, eyes=0.0)         # where SF14 picks it up
ALB_AT = 0.3                                # Alberich's watch, on Right
WAN_AT = 0.7                                # the Wanderer, on Left


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


def when(pos):
    """Measure position -> seconds in the excerpt, within whichever segment holds it."""
    for seg in EX['segments']:
        a, b = seg['measures']
        if a <= pos <= b:
            pts = [(a, seg['start'])] + [(m, t) for m, t in EX['bars'] if a < m <= b]
            return float(np.interp(pos, [p[0] for p in pts], [p[1] for p in pts]))
    return None


def voice():
    """Fafner's line in seconds: (time, seconds, midi)."""
    out = []
    for b, beat, n, name in VOICE:
        t0, t1 = when(b + beat / 3), when(b + (beat + n) / 3)
        if t0 is not None and t1 is not None:
            out.append((t0, t1 - t0, note(name)))
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, k). 'spear' is the Wanderer's call
    (the orchestra's long notes under it), 'dragon' a low note of the dragon's tritone, 'voice' Fafner's line,
    'storm' the storm's music; 'laugh' and 'mutter' mark the Wanderer's laugh and Alberich's curse for the lights."""
    N = []
    for t, d, m, v, h in sorted(EX['notes']):
        if t < BAR[390] and h == 0 and d >= 0.5:
            part = 'spear'
        elif t < T_GO and h == 1 and d >= 0.5 and m < 50:
            part = 'dragon'
        elif t >= T_GO:
            part = 'storm'
        else:
            part = 'bed'
        N.append((t, d, m, v, part, None))
    for t, d, m in voice():
        N.append((t, d, m, 100, 'voice', None))
    for t0 in (sg[0] for sg in EX['singing'] if sg[2] == 'Der Wanderer' and sg[0] < BAR[390]):
        for k in range(3):                  # each call rings out three times down the front of the house
            N.append((t0 + 0.45 * k, 0.4, 60, 0, 'spear', None))
    for k in range(3):
        N.append((T_GO + 0.35 * k, 0.2, 60, 0, 'laugh', None))
    for t0 in T_HIDE:
        N.append((t0, 1.0, 40, 0, 'mutter', None))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=13):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d, mid = S['d'], S['mid']
    L = d.max()
    N = compose()
    p_alb, p_wan = at(G, 'Right', ALB_AT), at(G, 'Left', WAN_AT)
    spear_on = np.array(sorted({round(e[0], 2) for e in N if e[4] == 'spear'}))
    gusts = np.array(accents([(e[0], e[1], e[2], e[3]) for e in N if e[4] == 'storm'], vmin=100, n=2, space=0.45))
    loud = np.zeros(nframes(D))
    for e in N:
        if e[4] == 'storm':
            loud[min(len(loud) - 1, int(e[0] / DT))] += (e[3] / 127) ** 2
    loud = np.convolve(loud, np.exp(-np.arange(60) / 20.0))[:len(loud)]
    loud = np.clip(loud / (loud.max() + 1e-9) * 1.6, 0, 1)
    dragon = [e for e in N if e[4] == 'dragon']
    voice = np.array(sorted({e[0] for e in N if e[4] == 'voice'}))
    laugh = sorted({e[0] for e in N if e[4] == 'laugh'})
    mutter = sorted({e[0] for e in N if e[4] == 'mutter'})
    runs = ['Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right']
    order = [3, 2, 4, 1, 5, 0]               # the shudder spreads from the cave out, run by run
    gust = Flicker(np.random.default_rng(seed + 1), G.N, 2.0, 6.0)
    lo, hi = note('Eb2'), note('A2')

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        lv = {k: START[k] for k in START}
        awake = smoothstep(T_EYES - 0.05, T_EYES + 0.15, t) * (1 - smoothstep(T_YAWN, T_GO, t))
        lv['eyes'] = awake
        lv['cave'] += 0.45 * awake
        fr = forest(S, T, lv)

        # the Wanderer calls into the cave: a pale blue beam down the front of the house per note of his spear
        for t0 in spear_on:
            a = t - t0
            if 0 <= a < 1.2:
                front = p_wan + (mid - p_wan) * min(1.0, a / 0.35)
                beam = (d >= p_wan) * (d <= front)
                fr += light(WANDER_SOFT, 0.8 * np.exp(-a / 0.45) * beam)
                fr += light(SPEAR, 0.9 * np.exp(-a / 0.3) * np.exp(-((d - front) / 30) ** 2))
        # Alberich shouts: red bursts flung into the cave mouth
        for t0 in T_SHOUT:
            a = t - t0
            if 0 <= a < 1.2:
                front = p_alb - (p_alb - mid) * min(1.0, a / 0.35)
                beam = (d <= p_alb) * (d >= front)
                fr += light(BLOOD, 0.85 * np.exp(-a / 0.4) * beam)

        # the eyes snap open: a red flash out of the cave over the whole house
        if T_EYES <= t < T_EYES + 2:
            a = t - T_EYES
            fr += light(EYE, 0.95 * np.exp(-a / 0.5) * smoothstep(1400 * a + 100, 1400 * a - 100, np.abs(d - mid)))
            fr += light(WHITE, 0.6 * np.exp(-a / 0.08) * S['porch'])

        # Fafner's motif: every note a huge ochre shudder, run by run out from the cave
        for i, (t0, dur, m, v, part, k) in enumerate(dragon):
            a = t - t0
            if 0 <= a < 1.6:
                u = (m - lo) / (hi - lo)
                run = G.seg_of == runs[order[i % 6]]
                shake = 0.75 + 0.25 * np.sin(2 * np.pi * 9 * a)
                fr += light(SCALE, (0.85 + 0.25 * u) * np.exp(-a / 0.7) * shake * run)
                fr += light(CAVE, 0.8 * np.exp(-a / 0.4) * S['mouth'])

        # his voice: each word of the giants' motif floods the house in stone and scale from the cave out
        j = int(np.searchsorted(voice, t, side='right')) - 1
        if j >= 0 and t - voice[j] < 1.5 and t < T_GO:
            a = t - voice[j]
            reach = 1300 * min(1.0, a / 0.3)
            flood = smoothstep(reach + 80, reach - 80, np.abs(d - mid))
            fr += light(SCALE, 1.0 * np.exp(-a / 0.8) * flood)
            fr += light(STONE, 0.6 * np.exp(-a / 0.25) * flood)

        if awake > 0:
            fr += light(EYE, 0.55 * awake * (np.exp(-((d - at(G, 'Porch Front', 0.4)) / 25) ** 2)
                                             + np.exp(-((d - at(G, 'Porch Front', 0.6)) / 25) ** 2)))
        for t0 in mutter:
            a = t - t0
            if 0 <= a < 2.0:
                fr += light(BLOOD, 0.6 * np.exp(-a / 0.6) * np.exp(-((np.abs(d - p_alb) - 450 * a) / 90) ** 2))

        # the yawn: a slow ochre breath out of the cave as the eyes sink shut
        if T_YAWN <= t < T_GO + 2:
            a = (t - T_YAWN) / (T_GO + 2 - T_YAWN)
            fr += light(SCALE, 0.8 * np.sin(np.pi * a) * S['mouth'])

        # the Wanderer laughs (blue flickers round him), then sweeps the length of the house as storm-light
        for t0 in laugh:
            a = t - t0
            if 0 <= a < 0.5:
                fr += light(WANDER_SOFT, 0.7 * np.exp(-a / 0.12) * np.exp(-((d - p_wan) / 160) ** 2))
        if T_GO <= t < T_GO + 6:
            a = t - T_GO
            front = p_wan + (L + 200 - p_wan) * smoothstep(0, 4.0, a)
            body = smoothstep(front - 700, front - 40, d) * smoothstep(front + 60, front - 20, d)
            fr += light(WANDER_SOFT, 1.0 * body * (0.85 + 0.15 * gust(T)) * (1 - smoothstep(4, 6, a)))
            fr += light(WANDERER, 0.6 * body * (1 - smoothstep(4, 6, a)))
            fr += light(SPEAR, 0.9 * np.exp(-((d - front) / 40) ** 2))

        # the storm he rides away in: the house flickers storm-blue with it, and every accent a gust of light
        # racing after him to the free end of Right
        if t >= T_GO:
            fr += light(WANDER_SOFT, 0.6 * loud[f] * (0.6 + 0.4 * gust(T * 2)) * (d > p_wan - 300))
            for t0 in gusts[(gusts <= t) & (gusts > t - 1.5)]:
                a = t - t0
                start = p_wan + (L - p_wan) * min(1.0, (t0 - T_GO) / 8.0) * 0.6
                front = start + 1100 * a
                fr += light(SPEAR, 1.0 * np.exp(-a / 0.6) * np.exp(-((d - front) / 110) ** 2))
                fr += light(WANDERER, 0.9 * np.exp(-a / 0.7) * smoothstep(front + 40, front - 800, d) * (d > start))

        # Alberich: flinches at the dragon, shrinks into hiding at the end
        alvl = keys(t, [(0, 0.7), (T_EYES, 0.7), (T_EYES + 0.5, 0.45), (T_YAWN + 2, 0.6), (T_GO + 2, 0.6),
                        (T_HIDE[0] + 4, 0.3)])
        for t0 in T_SHOUT:
            if 0 <= t - t0 < 0.6:
                alvl += 0.3 * np.exp(-(t - t0) / 0.2)
        fr += light(MUD, 0.6 * alvl * np.exp(-((d - p_alb) / 70) ** 2))
        fr = figure(fr, S, p_alb, ALBERICH, min(alvl, 1.0))
        if t < T_GO:
            wl = 0.8 + 0.2 * sum(np.exp(-(t - t0) / 0.25) for t0 in spear_on if 0 <= t - t0 < 1)
            fr = figure(fr, S, p_wan, WANDERER, min(wl, 1.0), 18.0)
            fr += light(SPEAR, 0.5 * np.exp(-((d - p_wan - 22) / 6) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, Fafner's voice through the speaking-trumpet, and the dragon and the storm around them."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    cave = pan_at(at(G, 'Porch Front', 0.5))
    wan = pan_at(at(G, 'Left', WAN_AT))
    o = Orchestra(M, level=2.65)
    parts = {(round(t, 4), m): part for t, d, m, v, part, k in compose()}

    def role(t, d, m, v, h):
        part = parts.get((round(t, 4), m))
        if part == 'dragon':
            return [('tuba', 0, 8, 0.8), ('basses', -12 if m >= 40 else 0, 0, 0.55), ('cellos', 0, -6, 0.4)]
        if part == 'spear':
            return [('trombones', 0, 6, 0.7), ('horns', 0, 0, 0.45)]
        return None

    def pan(t, m):
        if t < T_GO:
            return cave * 0.6
        return float(np.clip(wan + (1.0 - wan) * min(1.0, (t - T_GO) / 6.0), -0.9, 0.9))

    o.tutti(tidy(EX['notes']), size=lambda t: 0.5 if t < T_GO else 1.0, role=role, pan=pan)
    for t, d, m in voice():                                 # Fafner, out of the cave
        o.play('tuba', m, t, d, 112, cave, 0.95)
        o.play('trombones', m, t, d, 104, cave, 0.6)
        o.play('basses', m - 12, t, d, 96, cave, 0.4)
    # the dragon and the storm: they lead where the staging needs them, and back off under his voice
    o.effects([(0.0, -4), (T_EYES - 1.0, -2), (T_EYES, 2), (T_EYES + 4.0, -2), (BAR[398], -9), (BAR[402] - 0.5, -9),
               (BAR[441] - 1.0, -10), (T_YAWN, -4), (T_GO - 0.5, 0), (T_GO + 1.0, 2), (T_HIDE[0], -6)])
    o.thunder(T_EYES, near=0.15, pan=cave, gain=1.0)        # his growl as the eyes open
    o.hit('timpani roll', T_EYES - 2.5, 96, gain=0.45, pan=cave)
    o.wind(T_YAWN - 0.5, T_GO + 3.0, level=lambda tt: np.sin(np.pi * np.clip((tt - T_YAWN + 0.5) / (T_GO + 3.5 - T_YAWN), 0, 1)),
           pan=cave, seed=13)                               # the yawn: a slow breath out of the cave
    o.wind(T_GO - 0.5, D, level=lambda tt: 1.0 - 0.75 * np.clip((tt - T_GO - 6) / 10, 0, 1),
           pan=lambda tt: float(np.clip(wan + (1.0 - wan) * (tt - T_GO) / 6.0, -0.9, 0.9)), seed=14)
    o.thunder(T_GO + 0.1, near=0.6, pan=wan, gain=0.9)
