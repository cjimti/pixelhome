"""Fricka's Demand: the rocky pass at dawn, Wotan alone on Porch Left, and the rose glimmer at the free end of Right
growing. Fricka comes on in her chariot drawn by rams: a rushing rose streak with two pale lights pulling ahead of
it, tearing along Right to the porch to galloping staccato bassoons and racing strings, a cymbal as she pulls up
on Porch Right. Wotan comes forward onto Porch Front to meet her.

She is the goddess of marriage, and she has come for Siegmund. The argument takes the whole house, as it did
over the castle: her rose floods in from the right, his deep blue holds from the left, and the front between them
surges back and forth over the porch, sparking where they meet. Her reproaches are agitated oboe and violas over
driving cellos: Hunding's marriage has been broken, and by a brother and sister. Wotan answers with his
treaties (Donington 14) in trombones and tubas, and the blue pushes back; he pleads for the free hero, the
Wälsung who acts without the gods (Siegmund's motif, 35, on the horns). She tears that apart: he made the hero,
he left him the sword (the Sword, 45, twisted into the minor), and the rose drives deep.

Then she turns his own law against him: his spear (73), the long descending scale in the full trombones, drawn
as a steel line out from her toward him, one step for every note, the treaties carved on it. Wotan frustrated
(70) sinks through the low strings: he gives in, and swears Siegmund will fall. His blue drains away to almost
nothing and he slumps in the middle of the porch, dimmed. Fricka, triumphant, sweeps back out the way she came,
out the free end of Right with her rams; the rose ebbs from the house, and Brünnhilde comes galloping back in
through the same gap, to her own motif (88) on a horn, and stops on Porch Right when she sees her father's face.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import MOTIFS, play

CODE = 'WK12'
TITLE = "Fricka's Demand"
KIND = 'show'
DESCRIPTION = ('Fricka, goddess of marriage, arrives in her chariot pulled by rams, and she wants Siegmund dead. '
               'Watch their colours fight over the house until Wotan, bound by his own laws, gives in.')
VOICEOVER = ('Here comes Fricka, and she is furious. Her husband has been breaking his own rules, '
             'and she is about to make him pay for it.')

K = 11                                      # this scene's place in the shared clock (t + 80 * K)
T_ARRIVE = 4.6                              # she pulls up on Porch Right
BEAT = 0.5
REPROACH = [5.5, 10.0]                      # her first reproaches
T_TREATY = 14.5                             # his treaties
TBEAT = 0.52
T_SHAME = 23.5                              # brother and sister!
T_HERO = 31.0                               # the free hero
T_SWORD = 37.0                              # you gave him the sword
T_SPEAR = 43.5                              # his own law against him
SBEAT = 0.5
T_YIELD = 50.5                              # Wotan frustrated: he gives in
YBEAT = 0.55
T_TRIUMPH = 58.5
T_LEAVE = 61.0                              # she sweeps out the free end of Right
T_BRUNN = 66.5                              # Brünnhilde gallops back in
T_STOP = 74.0
D = 80.0

SLATE = hexc('#3a3a4a')
RIDGE = hexc('#5a5a70')
DAWN = hexc('#ff7a3a')
GLOW = hexc('#ffb070')
WOTAN = hexc('#1a3cff')
SPEAR = hexc('#c8d8ff')
BRUNN = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
ROSE = hexc('#ff9ad0')
RAM = hexc('#f0e4c8')
MAUVE = hexc('#a050e0')
WHITE = hexc('#ffffff')

SLATE_L, RIDGE_L, DAWN_L, GLOW_L = 0.5, 0.3, 0.55, 0.3
WOTAN_L, BRUNN_L, FRICKA_L, ROSE_END = 0.75, 0.75, 0.78, 0.42
CRUSHED = 0.6                               # what is left of Wotan at the end


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    for m in ('B1', 'F#2', 'D3'):                                               # WK11's held chord
        add(0.0, 2.0, m, 66, 'held')
    for j in range(int(T_ARRIVE / 0.2)):                                        # the rams gallop in
        add(j * 0.2, 0.12, ('A2', 'A2', 'E3', 'A2')[j % 4], 84 + 2 * j, 'rams', 'fricka')
    for j in range(20):
        add(1.0 + j * 0.18, 0.2, note('A3') + j, 80 + j, 'rush')
    add(T_ARRIVE, 1.0, 'A1', 112, 'arrive')

    phrases = [
        [(0, .5, 'E4'), (.5, .5, 'G4'), (1, 1, 'Bb4'), (2, .5, 'A4'), (2.5, .5, 'G4'), (3, .5, 'F4'), (3.5, .5, 'E4'),
         (4, 1, 'D4'), (5, .5, 'E4'), (5.5, .5, 'F4'), (6, 1.5, 'A4')],
        [(0, .5, 'G4'), (.5, .5, 'Bb4'), (1, 1, 'D5'), (2, .5, 'C#5'), (2.5, .5, 'Bb4'), (3, .5, 'A4'), (3.5, .5, 'G4'),
         (4, 1, 'F4'), (5, .5, 'E4'), (5.5, .5, 'F4'), (6, 1.5, 'D4')]]
    for k, (t0, ph) in enumerate(zip(REPROACH, phrases)):                      # her reproaches
        for b, d, n in ph:
            add(t0 + b * BEAT, d * BEAT, n, 98 + 4 * k, 'fricka', 'fricka')
        for j, ch in enumerate((('D3', 'A3', 'F4'), ('G2', 'D3', 'Bb3'), ('A2', 'E3', 'C#4'))):
            for m in ch:
                add(t0 + j * 1.4, 1.5, m, 78 + 4 * k, 'trem')
    for k in range(int((T_TREATY - REPROACH[0]) / (BEAT / 2))):                # the cellos drive under her
        m = ('D2', 'D2', 'F2', 'D2', 'A1', 'D2', 'Bb1', 'A1')[k % 8]
        add(REPROACH[0] + k * BEAT / 2, BEAT / 2 * 0.8, m, 88 + 8 * (k % 4 == 0), 'drive')
    for t, m, v, d in play('treaties', T_TREATY, TBEAT, 0, 104):               # his treaties
        add(t, d, m, v, 'treaty', 'wotan')

    shame = [(0, .25, 'F5'), (.25, .25, 'E5'), (.5, .5, 'D5'), (1, .5, 'C#5'), (1.5, .5, 'Bb4'), (2, 1, 'A4'),
             (3, .5, 'Bb4'), (3.5, .5, 'C#5'), (4, 1, 'E5'), (5, .5, 'D5'), (5.5, .5, 'A4'), (6, 1.5, 'F4'),
             (8, .5, 'G4'), (8.5, .5, 'A4'), (9, 1, 'Bb4'), (10, .5, 'C#5'), (10.5, .5, 'D5'), (11, 2, 'F5')]
    for b, d, n in shame:                                                       # brother and sister!
        add(T_SHAME + b * BEAT, d * BEAT, n, 110, 'fricka', 'fricka')
    for k in range(int((T_HERO - T_SHAME) / (BEAT / 2))):
        m = ('G2', 'G2', 'Bb2', 'G2', 'D2', 'G2', 'Eb2', 'D2')[k % 8]
        add(T_SHAME + k * BEAT / 2, BEAT / 2 * 0.8, m, 96 + 8 * (k % 4 == 0), 'drive')
    add(T_SHAME + 11 * BEAT, 1.0, 'D2', 116, 'hit')
    for t, m, v, d in play('siegmund', T_HERO, 0.3, 0, 94):                    # the free hero
        add(t, d, m, v, 'hero', 'wotan')
    for b, d, n in MOTIFS['sword']['notes']:                                    # you gave him the sword!
        add(T_SWORD + b * 0.42, d * 0.42, note(n) - 1 - (1 if n[0] == 'E' else 0), 108, 'fricka', 'fricka')
    for k in range(int((T_SPEAR - T_SWORD) / (BEAT / 2))):
        m = ('B1', 'B1', 'D2', 'B1', 'F#1', 'B1', 'G1', 'F#1')[k % 8]
        add(T_SWORD + k * BEAT / 2, BEAT / 2 * 0.8, m, 100 + 8 * (k % 4 == 0), 'drive')
    for t, m, v, d in play('spear', T_SPEAR, SBEAT, 0, 120):                   # his own law
        add(t, d, m, v, 'spear', 'fricka')
    add(T_SPEAR, 1.0, 'Bb1', 124, 'hit')
    for t, m, v, d in play('treaties', T_SPEAR + 1.0, TBEAT * 0.6, 12, 84, line='melody'):
        add(t, d, m, v, 'carved')
    for t, m, v, d in play('wotan_frustrated', T_YIELD, YBEAT, 0, 100):        # he gives in
        add(t, d, m, v, 'yield', 'wotan')
    for m in ('D2', 'A2', 'F3'):
        add(T_YIELD, T_STOP - T_YIELD, m, 72, 'gloom')
    triumph = [(0, .5, 'A4'), (.5, .5, 'D5'), (1, 1, 'F5'), (2, .5, 'E5'), (2.5, .5, 'D5'), (3, 2, 'A5')]
    for b, d, n in triumph:                                                     # triumphant
        add(T_TRIUMPH + b * BEAT, d * BEAT, n, 104, 'fricka', 'fricka')
    for m in ('D3', 'A3', 'F4', 'A4'):
        add(T_TRIUMPH, 2.6, m, 90, 'trem')
    for j in range(int((T_BRUNN - T_LEAVE) / 0.2)):                             # the rams, away
        add(T_LEAVE + j * 0.2, 0.12, ('A2', 'A2', 'E3', 'A2')[j % 4], 96 - 2 * j, 'rams', 'fricka')
    for j in range(16):
        add(T_LEAVE + 0.3 + j * 0.15, 0.2, note('D5') - j, 90 - 2 * j, 'rush')

    for t, m, v, d in play('ride', T_BRUNN, 0.36, 0, 88, line='melody'):       # Brünnhilde, back
        add(t, d, m, v, 'ride')
    for t, m, v, d in play('brunnhilde', T_BRUNN + 2.4, 0.55, 0, 90):
        add(t, d, m, v, 'motif' if m >= note('Bb3') else 'motif_low', 'brunn' if m >= note('Bb3') else None)
    for t, m, v, d in play('wotan_frustrated', T_STOP, 0.6, -12, 80, line='melody'):   # she sees his face
        if t < D - 1.5:
            add(t, d, m, v, 'brood')
    for m in ('D2', 'A2', 'D3', 'F3'):
        add(T_STOP, D - T_STOP, m, 78, 'gloom')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def front_marks(G):
    """Where the front between her rose (to its right) and his blue (to its left) stands, over time."""
    L = G.length
    P = lambda seg, u: at(G, seg, u)                                            # noqa: E731
    marks = [(0.0, L + 200), (T_ARRIVE - 1.0, L + 200), (T_ARRIVE + 0.5, P('Right', 0.3)),
             (REPROACH[0] + 1.5, P('Porch Front', 0.55)), (REPROACH[0] + 4.0, P('Porch Front', 0.45)),
             (REPROACH[1] + 1.5, P('Porch Left', 0.8)), (T_TREATY, P('Porch Left', 0.75)),
             (T_TREATY + 3.0, P('Porch Front', 0.5)), (T_TREATY + 8.0, P('Porch Right', 0.55)),
             (T_SHAME + 1.0, P('Porch Front', 0.6)), (T_SHAME + 6.5, P('Porch Left', 0.6)),
             (T_HERO, P('Porch Left', 0.65)), (T_HERO + 5.0, P('Porch Right', 0.35)),
             (T_SWORD + 0.5, P('Porch Front', 0.7)), (T_SWORD + 4.5, P('Porch Left', 0.7)),
             (T_SPEAR, P('Porch Left', 0.75)), (T_SPEAR + 5.5, P('Left', 0.9)),
             (T_YIELD + 7.5, P('Left', 0.45)), (T_LEAVE, P('Left', 0.4)), (T_LEAVE + 4.0, L + 200)]
    return marks


def choreography(G):
    """Per frame: Wotan, Fricka, Brünnhilde (path distance), and the front of the argument."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    W0 = at(G, 'Porch Left', 0.5)
    sway = 5 * np.sin(2 * np.pi * (t + 80 * K) / 6.0)
    w_t = W0 + sway
    w_t = np.where(t >= T_ARRIVE, at(G, 'Porch Front', 0.25), w_t)
    w_t = np.where(t >= T_TREATY, at(G, 'Porch Front', 0.33), w_t)
    w_t = np.where(t >= T_SHAME, at(G, 'Porch Front', 0.28), w_t)
    w_t = np.where(t >= T_HERO, at(G, 'Porch Front', 0.36), w_t)
    w_t = np.where(t >= T_SWORD, at(G, 'Porch Front', 0.3), w_t)
    w_t = np.where(t >= T_YIELD, at(G, 'Porch Front', 0.4), w_t)
    wot = follow(w_t, np.where(t < T_YIELD, 2.0, 0.8))
    f_t = np.full(F, L + 150)
    arr = (t >= 0) & (t < T_ARRIVE + 1)
    f_t[arr] = L + 150 + (at(G, 'Porch Right', 0.3) - L - 150) * smoothstep(0.3, T_ARRIVE, t[arr]) ** 0.7
    f_t[t >= T_ARRIVE + 1] = at(G, 'Porch Right', 0.3)
    for t0, u in ((REPROACH[0], 0.85), (REPROACH[1], 0.75), (T_SHAME, 0.68), (T_SWORD, 0.62)):
        f_t[(t >= t0) & (t < t0 + 4.0)] = at(G, 'Porch Front', u)
    f_t[(t >= T_SPEAR) & (t < T_TRIUMPH)] = at(G, 'Porch Front', 0.72)
    f_t[(t >= T_TRIUMPH) & (t < T_LEAVE)] = at(G, 'Porch Front', 0.8)
    lv = t >= T_LEAVE
    f_t[lv] = at(G, 'Porch Front', 0.8) + (L + 200 - at(G, 'Porch Front', 0.8)) * smoothstep(T_LEAVE, T_BRUNN - 0.5, t[lv]) ** 1.4
    fri = follow(f_t, np.where((t < T_ARRIVE + 1) | (t >= T_LEAVE), 8.0, 3.0))
    b_t = np.full(F, L + 150)
    bi = t >= T_BRUNN
    b_t[bi] = L + 150 + (at(G, 'Porch Right', 0.6) - L - 150) * smoothstep(T_BRUNN, T_STOP, t[bi])
    br = follow(b_t, np.full(F, 4.0))
    ts, us = zip(*front_marks(G))
    front = follow(np.interp(t, ts, us), np.full(F, 3.0))
    crush = 1 - (1 - CRUSHED) * smoothstep(T_YIELD + 1, T_TRIUMPH + 2, t)
    return dict(t=t, wotan=wot, fricka=fri, brunn=br, front=front, crush=crush)


def rocks(G):
    """The pass's fixed parts: jagged ridges on the wings, the heights of the porch (shared with WK11)."""
    rng = np.random.default_rng(1111)
    d = G.pd
    pf = at(G, 'Porch Front', 0.5)
    lat = rng.uniform(0, 1, 80)
    xs = np.linspace(d.min() - 50, d.max() + 50, 80)
    jag = np.interp(d, xs, lat)
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    return dict(pf=pf, jag=jag, height=np.exp(-((d - pf) / 430) ** 2), porch=porch,
                drift=Flicker(rng, G.N, 0.05, 0.2), shim=Flicker(rng, G.N, 0.3, 1.0))


def draw_pass(G, P, tt, level=1.0):
    d = G.pd
    cloud = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 520 - 0.025 * tt))
    fr = light(SLATE, level * SLATE_L * (0.75 + 0.25 * cloud) * (1 - 0.4 * P['height']))
    fr += light(RIDGE, level * RIDGE_L * P['jag'] ** 2 * (0.8 + 0.2 * P['drift'](tt)) * (1 - 0.5 * P['height']))
    fr += light(DAWN, level * DAWN_L * P['height'] * (0.88 + 0.12 * P['shim'](tt)))
    fr += light(GLOW, level * GLOW_L * P['height'] ** 3 * (0.8 + 0.2 * cloud))
    return fr


def draw_wotan(G, p, b, spear=0.35):
    d = G.pd
    fr = light(WOTAN, b * np.exp(-((d - p) / 30) ** 2) + 0.35 * b * np.exp(-((d - p) / 140) ** 2))
    shaft = smoothstep(p + 15, p + 30, d) * smoothstep(p + 110, p + 95, d)
    fr += light(SPEAR, spear * (b / WOTAN_L) * shaft)
    return fr


def draw_brunn(G, p, b, tt):
    d = G.pd
    fr = light(BRUNN, b * np.exp(-((d - p) / 24) ** 2) + 0.3 * b * np.exp(-((d - p) / 120) ** 2))
    fr += light(GOLD, (b / BRUNN_L) * 0.6 * (0.75 + 0.25 * np.sin(2 * np.pi * tt / 1.7)) * np.exp(-((d - p - 14) / 7) ** 2))
    return fr


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, L = G.pd, G.length
    P = rocks(G)
    pf = P['pf']
    C = choreography(G)
    N = compose()
    wsung = np.array([e[0] for e in N if e[5] == 'wotan'])
    fsung = np.array([e[0] for e in N if e[5] == 'fricka' and e[4] != 'rams'])
    bsung = np.array([e[0] for e in N if e[5] == 'brunn'])
    shoves = np.array([e[0] for e in N if e[4] == 'fricka' and e[1] >= BEAT])
    spear = np.array([e[0] for e in N if e[4] == 'spear'])
    carved = np.array([e[0] for e in N if e[4] == 'carved'])
    tw = Flicker(rng, G.N, 0.3, 1.2)
    edge_n = Flicker(rng, G.N, 1.5, 4.0)

    for f in range(F):
        t = f * DT
        tt = t + 80 * K
        wp, fp, bp = C['wotan'][f], C['fricka'][f], C['brunn'][f]
        crush = C['crush'][f]
        argue = smoothstep(T_ARRIVE - 0.5, T_ARRIVE + 2.0, t) * (1 - smoothstep(T_LEAVE, T_LEAVE + 4.5, t))
        fr = draw_pass(G, P, tt, 1 - 0.55 * argue)

        # the rose glimmer at the door grows into her chariot; it streaks in along Right
        if t < T_ARRIVE + 1.5:
            g = ROSE_END * (0.85 + 0.15 * np.sin(2 * np.pi * tt / 1.3)) * (1 - smoothstep(0.2, 1.0, t))
            fr += light(ROSE, g * np.exp(-((L - d) / 90) ** 2))

        # the argument: her rose from the right, his blue from the left, the front surging over the porch
        if argue > 0:
            u = C['front'][f] + 25 * edge_n(t)
            edge = 40
            rose = smoothstep(u - edge, u + edge, d)
            blue = 1 - rose
            seam = np.exp(-((d - u) / 45) ** 2)
            si = int(np.searchsorted(shoves, t, side='right')) - 1
            jolt = np.exp(-(t - shoves[si]) / 0.2) if si >= 0 and t - shoves[si] < 1 else 0.0
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 300 - 0.7 * t))
            fr += light(ROSE, argue * (0.46 + 0.12 * wave + 0.15 * jolt) * rose)
            fr += light(WOTAN, argue * crush * (0.48 + 0.12 * (1 - wave)) * blue)
            fr += light(WHITE, argue * (0.3 + 0.45 * jolt) * seam ** 3 * (0.6 + 0.4 * tw(t)))
            fr += light(MAUVE, argue * 0.35 * seam)

        # his own law turned on him: a steel line drawn from her toward him, a step for every note
        if T_SPEAR - 0.1 <= t < T_TRIUMPH + 2:
            n = int(np.searchsorted(spear, t, side='right'))
            if n > 0:
                grown = (n - 1 + smoothstep(spear[n - 1], spear[n - 1] + 0.25, t)) / len(spear)
                tip = fp + (wp + 40 - fp) * grown
                fade = 1 - smoothstep(T_YIELD + 3, T_TRIUMPH + 2, t)
                shaft = smoothstep(tip - 12, tip + 12, d) * smoothstep(fp + 10, fp - 10, d)
                ci = int(np.searchsorted(carved, t, side='right')) - 1
                rune = 0.0
                if ci >= 0 and t - carved[ci] < 1.2:
                    q = fp + (tip - fp) * ((ci * 0.37) % 1)
                    rune = np.exp(-((d - q) / 18) ** 2) * np.exp(-(t - carved[ci]) / 0.35)
                hit = np.exp(-(t - spear[n - 1]) / 0.25)
                fr += light(SPEAR, fade * (0.8 * shaft + 0.7 * hit * np.exp(-((d - tip) / 18) ** 2)))
                fr += light(WHITE, fade * (0.8 * rune + 0.3 * hit * shaft))
                if t < T_SPEAR + 1.0:
                    fr += light(SPEAR, 0.5 * np.exp(-(t - T_SPEAR) / 0.3) * np.ones(G.N))

        # he gives in: the blue drains out of the wings toward him and goes out
        if T_YIELD <= t < T_TRIUMPH + 3:
            a = (t - T_YIELD) / (T_TRIUMPH + 3 - T_YIELD)
            r = 1400 * (1 - a)
            fr += light(WOTAN, 0.35 * (1 - a) * np.exp(-((np.abs(d - wp) - r) / 80) ** 2))

        # Wotan
        i = int(np.searchsorted(wsung, t, side='right')) - 1
        wf = np.exp(-(t - wsung[i]) / 0.3) if i >= 0 and t - wsung[i] < 1.2 else 0.0
        fr += draw_wotan(G, wp, WOTAN_L * crush * (1 + 0.3 * wf))

        # Fricka and her rams, with a rose train behind her when she drives
        if -200 < fp < L + 120:
            i = int(np.searchsorted(fsung, t, side='right')) - 1
            ff = np.exp(-(t - fsung[i]) / 0.25) if i >= 0 and t - fsung[i] < 1.2 else 0.0
            b = FRICKA_L * (1 + 0.3 * ff)
            fr += light(ROSE, b * np.exp(-((d - fp) / 28) ** 2) + 0.35 * b * np.exp(-((d - fp) / 130) ** 2))
            fr += light(WHITE, 0.35 * ff * np.exp(-((d - fp) / 11) ** 2))
            drive = (1 - smoothstep(T_ARRIVE, T_ARRIVE + 1.2, t)) + smoothstep(T_LEAVE - 0.3, T_LEAVE + 0.5, t)
            if drive > 0:
                ahead = -1 if t < T_LEAVE else 1                                # the rams pull ahead of her
                for k, off in enumerate((45, 75)):
                    q = fp + ahead * off + 4 * np.sin(2 * np.pi * 5 * t + k)
                    fr += light(RAM, drive * 0.7 * np.exp(-((d - q) / 9) ** 2))
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 26, 2)):
                    q = C['fricka'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 34) ** 2) * (1 - n_ / 12.5))
                fr += light(ROSE, 0.65 * drive * trail)

        # Brünnhilde, galloping back in by the same gap
        if bp < L + 120:
            i = int(np.searchsorted(bsung, t, side='right')) - 1
            bf = np.exp(-(t - bsung[i]) / 0.25) if i >= 0 and t - bsung[i] < 1.0 else 0.0
            if abs(bp - C['brunn'][max(f - 4, 0)]) > 6:
                trail = np.zeros(G.N)
                for n_, lag in enumerate(range(2, 20, 2)):
                    q = C['brunn'][max(f - lag, 0)]
                    trail = np.maximum(trail, np.exp(-((d - q) / 26) ** 2) * (1 - n_ / 9.5))
                fr += light(BRUNN, 0.5 * trail)
            fr += draw_brunn(G, bp, BRUNN_L * (1 + 0.3 * bf * (t < T_STOP)), tt)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)
    pf = pan_at(at(G, 'Porch Front', 0.5))

    def pt(key, t):
        return pan_at(np.clip(np.interp(t, C['t'], C[key]), 0, G.length))

    for name, gain, rev in (('strings', 0.18, 0.3), ('low', 0.2, 0.18), ('brass', 0.2, 0.3), ('winds', 0.2, 0.3),
                            ('perc', 0.2, 0.28), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vatrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsus = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            M.add(bus, a * e, t, gain, pan)
            t += step

    for t, d, m, v, part, who in compose():
        if part == 'held':
            hold('strings', vatrem if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v,
                 pt('wotan', t), rise=0.05, fall=1.0, gain=0.6)
        elif part == 'rams':
            M.add('low', bsn.play(m, v), t, 0.9, pt('fricka', t))
            M.add('low', cbs.play(m, v - 10), t, 0.5, pt('fricka', t))
        elif part == 'rush':
            M.add('strings', vns.play(m, v), t, 0.7, pt('fricka', t))
        elif part == 'arrive':
            M.add('perc', crash.play(v), t, 0.9, pt('fricka', t))
            M.add('perc', timp.play(v, pitch=-3), t, 0.9, pt('fricka', t))
            M.add('fx', whoosh(1.2, 3000, 400, 0.6, seed=12), t - 0.6, 0.8, pt('fricka', t))
        elif part == 'fricka':
            pa = pt('fricka', t)
            M.add('winds', ob.play(m, v, dur=d * 1.05, release=0.25), t, 1.0, pa)
            M.add('strings', va.play(m - 12, v - 8, dur=d * 1.05, release=0.35), t, 0.8, pa)
        elif part == 'trem':
            M.add('strings', (vtrem if m >= note('A3') else vatrem).play(m, v, dur=d, release=0.2), t, 0.6,
                  pt('fricka', t) if m % 2 else pt('wotan', t))
        elif part == 'drive':
            M.add('low', cbs.play(m + 12, v), t, 0.8, -0.1)
            M.add('low', vcs.play(m + 12, v - 10), t, 0.6, 0.1)
        elif part == 'treaty':
            pa = pt('wotan', t)
            if m >= note('Gb3'):
                M.add('brass', horn.play(m, v, dur=d, release=0.5), t, 0.7, pa + 0.1)
            elif m >= note('Bb2'):
                M.add('brass', tbn.play(m, v, dur=d, release=0.5), t, 0.6, pa)
            else:
                M.add('low', tuba.play(m + 12, v, dur=d, release=0.5), t, 0.6, pa)
                M.add('low', cb.play(m + 12, v - 10, dur=d, release=0.5), t, 0.6, pa)
        elif part == 'hit':
            M.add('perc', timp.play(v, pitch=-4), t, 1.0, pf)
            M.add('perc', crash.play(v), t, 0.7, pf)
        elif part == 'hero':
            pa = pt('wotan', t)
            if m >= note('D3') and d > 0.3:
                hold('brass', horn, m, t, t + d, v, pa, rise=0.2, fall=0.8, gain=0.7)
            else:
                M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.4), t, 0.9, pa)
        elif part == 'spear':
            pa = pt('fricka', t) + (pt('wotan', t) - pt('fricka', t)) * min(1.0, (t - T_SPEAR) / 5.5)
            M.add('brass', tbn.play(m, v, dur=d, release=0.4), t, 1.0, pa)
            M.add('brass', tbn.play(m + 12, v - 10, dur=d, release=0.4), t, 0.6, pa + 0.1)
            M.add('low', tuba.play(m, v - 6, dur=d, release=0.4), t, 0.7, pa)
            M.add('low', cb.play(m, v - 16, dur=d, release=0.4), t, 0.5, pa)
        elif part == 'carved':
            M.add('brass', horn.play(m - 12, v, dur=d, release=0.4), t, 0.6, pt('fricka', t))
        elif part == 'yield':
            pa = pt('wotan', t)
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.5), t, 1.0, pa)
            M.add('low', bsus.play(m - 12, v - 10, dur=d * 1.05, release=0.5), t, 0.7, pa)
            M.add('brass', tbn.play(m, v - 20, dur=d * 1.05, release=0.5), t, 0.4, pa)
        elif part == 'gloom':
            hold('strings', vatrem if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v,
                 pt('wotan', t), rise=2.0, fall=1.5, gain=0.6)
        elif part == 'ride':
            M.add('brass', horn.play(m, v, dur=d * 1.1, release=0.2), t, 1.1, pt('brunn', t))
        elif part == 'motif':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 1.0, pt('brunn', t))
        elif part == 'motif_low':
            hold('strings', va if m >= note('C3') else cb, m + (12 if m < note('C3') else 0), t, t + d, v - 10,
                 pt('brunn', t), rise=0.3, fall=0.8, gain=0.5)
        elif part == 'brood':
            M.add('strings', vc.play(m, v, dur=d * 1.05, release=0.5), t, 0.9, pt('wotan', t))
