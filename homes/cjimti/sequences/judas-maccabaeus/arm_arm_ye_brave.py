"""Arm, Arm, Ye Brave!: Simon calls the Maccabees to arms, and they fall into ranks along Left.

It opens where O Father, Whose Almighty Power (JM03) ended (CARRY, from JM03's last frame: change both together):
Seleucid purple on Right and Side, the Temple grey with its idols over the lights' glow, the people on the porch runs,
and on Left, in the hills of Modein, the gathered blue round Simon's deep blue and the gold of Judas. Over the
orchestra's opening bars the last of the purple leaves Left and a low blue fills it, lifting on every beat.

Then Simon: "Arm, arm, ye brave! a noble cause, the cause of Heav'n your zeal demands." His deep blue swells on every
note he sings, and on each bar a new light steps into line along Left, blue and white in turn, until the hills hold a
whole rank of them, Judas's gold among them.

The chorus answers, "We come, in bright array": the rank marches in place on the beat, every other light stepping up
on the one beat and the rest on the next, and each chord the chorus sings lifts the whole line and the people on the
porch. "Judah," three times, soft, loud, louder: each time Judas's gold flares and a wave runs from him along the rank,
and the purple on Right shrinks back. "Judah, thy sceptre to obey", the trumpets and drums, and on the last chord the
rank stands steady and bright, which is where Call Forth Thy Powers (JM05) begins.

The music is Handel's own: No. 10, the air's first four bars and Simon's first section (bars 14-27), and No. 11, the
chorus's first 21 bars and its last nine, transcribed from the Novello vocal score into arm_arm_ye_brave.musicxml and
timed by scripts/score_excerpt.py at the score's Allegro (crotchet 108 for the air, 132 for the chorus). Simon plays
on bassoons and cellos over strings and oboes; the chorus on strings with oboes and bassoons doubling, trumpets on
the sopranos' forte lines and the orchestra's fanfare, and timpani; a harpsichord plays the continuo. render() and
score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM04'
TITLE = 'Arm, Arm, Ye Brave!'
KIND = 'show'
DESCRIPTION = ("Simon calls the Maccabees to arms, and blue and white lights step into ranks along Left; the chorus "
               "answers 'We come, in bright array' and the ranks march in place on the beat.")
VOICEOVER = 'Arm, arm, ye brave! Simon calls the people to war, and they answer: we come in bright array.'

EX = excerpt(__file__)              # No. 10 bars 1-4 and 14-27 (compact 1-18), No. 11 bars 1-21 and 41-49 (19-48)
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 3.0, 2)  # the last chord held
NOTES = EX['notes']
SIMON = [n for n in NOTES if n[5] == 'Simon']
VOICES = ('S', 'A', 'T', 'B')
SUNG = [n for n in NOTES if n[5] in VOICES]
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_SIMON = BAR[5]                    # "Arm, arm, ye brave!"
T_CHORUS = BAR[19]                  # No. 11
T_WE = min(n[0] for n in SUNG)      # "We come"
JUDAH = [BAR[31], BAR[32], BAR[33]]  # "Judah," p, f, ff
T_LAST = BAR[48]                    # the last chord
BEAT_A = BAR[2] - BAR[1]           # the air's bar
BEAT = (BAR[20] - BAR[19]) / 3      # the chorus's crotchet
SIMON_ON = np.array(sorted(n[0] for n in SIMON))
CHORDS = np.array(sorted({round(n[0], 3) for n in SUNG}))
CHORD_V = np.array([max(n[3] for n in SUNG if abs(n[0] - t) < 0.002) for t in CHORDS])

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
STONE = hexc('#6a6a6a')             # the idols
BLUE = hexc('#1e5bd8')              # the Maccabees
WHITE = hexc('#f2f6ff')
SIMON_C = hexc('#2850c8')           # Simon
GOLD = hexc('#ffc83c')              # Judas
GLINT = hexc('#c08a40')             # helmet glints
CARRY = 3.0                         # seconds JM03's last frame takes to give way
T3, T3_VICTORY, T3_LAST = 76.85, 70.3666, 72.0332   # JM03's last frame, its "victory" and last chord (o_father.py)
RANK = 12                           # lights in the rank on Left
STEP_IN = list(range(6, 18))        # the bar each one steps into line on


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


class Stage:
    """The pieces JM03 left on the house, which this scene keeps: the porch's people, the idols, Simon and Judas."""

    def __init__(self, G):
        d, seg = G.pd, G.seg_of
        self.d = d
        self.left = (seg == 'Left').astype(float)
        self.right_side = np.isin(seg, ['Right', 'Side']).astype(float)
        runL, runR = seg == 'Porch Left', seg == 'Porch Right'
        self.porch = (runL | runR).astype(float)
        front = seg == 'Porch Front'
        pl0, pl1 = span(G, 'Porch Left')
        pr0, pr1 = span(G, 'Porch Right')
        pf0, pf1 = span(G, 'Porch Front')
        self.l0, self.l1 = span(G, 'Left')
        L = self.l1 - self.l0
        bp, wp = np.zeros(G.N), np.zeros(G.N)
        for a, b in ((pl0, pl1), (pr0, pr1)):
            for k, c in enumerate(np.arange(a + 10, b - 6, 21)):
                g = np.exp(-((d - c) / 4.0) ** 2)
                if k % 2:
                    wp += g
                else:
                    bp += g
        self.blue_p, self.white_p = np.minimum(bp, 1) * self.porch, np.minimum(wp, 1) * self.porch
        idols = np.zeros(G.N)
        for k in range(4):
            c = pf0 + (0.14 + 0.24 * k) * (pf1 - pf0)
            idols += smoothstep(14, 9, np.abs(d - c))
        self.idols = np.minimum(idols, 1) * front
        self.mid = self.l0 + 0.55 * L
        self.sc = self.mid - 0.12 * L                       # Simon
        self.jc = self.mid + 0.04 * L                       # Judas
        gather = self.l0 + np.array([0.31, 0.42, 0.5, 0.68, 0.79]) * L
        g = sum(np.exp(-((d - c) / 6.0) ** 2) for c in gather)
        self.gathered = np.minimum(g, 1) * self.left        # JM03's gathered blue
        self.simon = (1.3 * np.exp(-((d - self.sc) / 7) ** 2) + 0.5 * np.exp(-((d - self.sc) / 24) ** 2)) * self.left
        self.judas = np.exp(-((d - self.jc) / 9) ** 2) * self.left
        self.judas_wide = np.exp(-((d - self.jc) / 34) ** 2) * self.left
        self.hills = np.exp(-((d - self.mid) / 50) ** 2) * self.left
        # the rank: RANK lights evenly along Left, blue and white in turn
        self.pos = self.l0 + np.linspace(0.06, 0.94, RANK) * L
        self.shape = np.exp(-((d[None, :] - self.pos[:, None]) / 6.0) ** 2) * self.left   # (RANK, N)
        self.white = np.arange(RANK) % 2 == 1

    def jm03_end(self, G):
        """JM03's last frame, as o_father.py draws it at its last frame (T3, its seed's flicker): the purple held back
        on Right and Side with its helmet glints, the gathered blue, the people, Simon, Judas, the idols."""
        rng = np.random.default_rng(3)
        flick, slow = Flicker(rng, G.N, 0.6, 2.2), Flicker(rng, G.N, 0.1, 0.4)
        t = T3
        sl = 0.9 + 0.1 * slow(t)
        fr = light(PURPLE, (0.42 * self.right_side + 0.126 * self.left) * sl + 0.14 * self.porch)
        fr += light(BLUE, 0.16 * self.left * sl)
        fr += light(GLINT, 0.18 * self.right_side * np.maximum(flick(t * 0.5), 0) ** 4)
        fr += light(STONE, 0.5 * self.idols) + Glow(G, 3).frame(t, 0.55)
        fr += light(BLUE, 1.3 * self.gathered * (0.9 + 0.1 * flick(t))) + light(BLUE, 0.22 * self.hills)
        lev = 0.66 * (0.88 + 0.12 * flick(t))
        fr += light(BLUE, lev * self.blue_p) + light(WHITE, 0.8 * lev * self.white_p)
        fr += light(SIMON_C, 0.75 * self.simon)
        flare = np.exp(-(t - T3_VICTORY) / 0.8) + 0.6 * np.exp(-(t - T3_LAST) / 0.7)
        fr += light(GOLD, 1.4 * (0.85 + 0.4 * flare) * self.judas) + light(GOLD, (0.18 + 0.35 * flare) * self.judas_wide)
        fr += light(WHITE, 0.4 * flare * np.exp(-((self.d - self.jc) / 2.5) ** 2) * self.left)
        return fr

    def end(self, glow, t):
        """This scene's last frame, where JM05 begins: the rank steady along Left on a low blue, Simon and Judas in it,
        the purple on Right and Side, the people on the porch runs, the idols over the glow."""
        fr = light(PURPLE, 0.42 * self.right_side + 0.14 * self.porch)
        fr += light(BLUE, 0.2 * self.left)
        fr += light(STONE, 0.5 * self.idols) + glow.frame(t, 0.55)
        fr += light(BLUE, 0.66 * self.blue_p) + light(WHITE, 0.8 * 0.66 * self.white_p)
        lv = np.full(RANK, 0.75)
        fr += light(BLUE, (lv * ~self.white) @ self.shape) + light(WHITE, 0.8 * (lv * self.white) @ self.shape)
        fr += light(SIMON_C, 0.5 * self.simon)
        fr += light(GOLD, 1.4 * 0.85 * self.judas) + light(GOLD, 0.18 * self.judas_wide)
        return fr


def last_onset(onsets, t):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    return (t - onsets[i], i) if i >= 0 else (1e9, -1)


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    st = Stage(G)
    d = st.d
    glow = Glow(G, seed)
    flick = Flicker(rng, G.N, 0.6, 2.2)
    slow = Flicker(rng, G.N, 0.1, 0.4)
    step_t = np.array([BAR[b] for b in STEP_IN])
    order = np.argsort(np.abs(st.pos - st.jc))               # nearest Judas first
    appear = np.empty(RANK)
    appear[order] = step_t
    T_END = T_LAST + 0.8
    jm03 = st.jm03_end(G)
    for f in range(F):
        t = f * DT
        settle = smoothstep(T_LAST, T_END, t)                # into the last frame
        # the bed: purple held on Right and Side; on Left it gives way to a low blue over the opening bars
        gone = smoothstep(CARRY * 0.5, T_SIMON, t)
        sl = 0.9 + 0.1 * slow(t)
        recoil = sum(smoothstep(tj, tj + 0.6, t) for tj in JUDAH) / 3 * (1 - settle)   # shrinking back on "Judah"
        fr = light(PURPLE, (0.42 * (1 - 0.35 * recoil) * st.right_side + 0.126 * (1 - gone) * st.left + 0.14 * st.porch) * sl)
        beat = 0.0
        if t < T_SIMON:                                       # the opening bars: the blue lifts on every beat
            a = ((t - CARRY * 0.5) / (BEAT_A / 4)) % 1.0 if t > CARRY * 0.5 else 1.0
            beat = np.exp(-a / 0.3) * gone
        fr += light(BLUE, (0.16 + 0.04 * gone + 0.18 * beat) * st.left)
        fr += light(STONE, 0.5 * st.idols) + glow.frame(t, 0.55)
        # the gathered blue of JM03 thins out as the rank forms
        rank_in = smoothstep(T_SIMON, T_CHORUS, t)
        fr += light(BLUE, 1.3 * (1 - rank_in) * st.gathered * (0.9 + 0.1 * flick(t)))
        fr += light(BLUE, 0.22 * (1 - rank_in) * st.hills)
        # the chorus's chords lift the people on the porch and the rank
        a, i = last_onset(CHORDS, t)
        chord = np.exp(-a / 0.35) * CHORD_V[i] / 100 if i >= 0 else 0.0
        lev = (0.66 + 0.25 * chord) * (0.88 + 0.12 * flick(t))
        fr += light(BLUE, lev * st.blue_p) + light(WHITE, 0.8 * lev * st.white_p)
        # Simon: deep blue, swelling on every note he sings, steadier once the chorus comes in
        a, i = last_onset(SIMON_ON, t)
        word = np.exp(-a / 0.3) if t < T_CHORUS else 0.0
        sim = 0.75 + 0.45 * word - 0.25 * smoothstep(T_CHORUS, T_CHORUS + 2.0, t)
        fr += light(SIMON_C, sim * st.simon)
        fr += light(WHITE, 0.4 * word * np.exp(-((d - st.sc) / 2.5) ** 2) * st.left)
        # the rank: each light steps into line on its bar with a flash, then marches in place on the chorus's beats
        on = smoothstep(0.0, 0.3, t - appear)
        flash = np.where(t >= appear, np.exp(-(t - appear) / 0.25), 0.0)
        march = np.zeros(RANK)
        if T_WE <= t < T_LAST:
            k = int((t - T_CHORUS) / BEAT)
            ph = (t - T_CHORUS) / BEAT - k
            up = np.exp(-ph / 0.3)
            march = np.where(np.arange(RANK) % 2 == k % 2, up, 0.0)
        lv = on * (0.5 + 0.6 * march + 0.3 * chord + 1.0 * flash)
        # "Judah": a wave from Judas along the rank, larger each time
        wave = np.zeros(RANK)
        flare = 0.0
        for k, tj in enumerate(JUDAH):
            a = t - tj
            if 0 <= a < 2.5:
                size = (0.6, 0.9, 1.3)[k]
                front = 160 * a
                wave += size * np.exp(-((np.abs(st.pos - st.jc) - front) / 30.0) ** 2) * np.exp(-a / 1.2)
                flare = max(flare, size * np.exp(-a / 0.6))
        lv = lv + wave
        if t >= T_LAST:                                       # the last chord: a flash, then steady
            a = t - T_LAST
            lv = lv + 0.6 * np.exp(-a / 0.3)
        lv = (1 - settle) * lv + settle * 0.75
        fr += light(BLUE, (lv * ~st.white) @ st.shape) + light(WHITE, 0.8 * (lv * st.white) @ st.shape)
        # Judas: steady gold among them, flaring on "Judah"
        fr += light(GOLD, 1.4 * (0.85 + 0.5 * flare) * st.judas) + light(GOLD, (0.18 + 0.4 * flare) * st.judas_wide)
        fr += light(WHITE, 0.5 * flare * np.exp(-((d - st.jc) / 2.5) ** 2) * st.left)
        # the opening carries JM03's last frame, and the end settles into this scene's last frame
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * jm03
        if settle > 0:
            fr = (1 - settle) * fr + settle * st.end(glow, t)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The ritornello on violins and oboes over cellos, basses and harpsichord; Simon on bassoons and cellos from
    where he stands on Left; the chorus on strings with oboes and bassoons doubling, trumpets on the sopranos' forte
    lines and on the orchestra's fanfare, timpani on the downbeats of the loud bars and the last chord."""
    st = Stage(G)
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pleft = pan_at(st.mid)
    o = Orchestra(M, level=2.4)
    forte = [(BAR[22] - 0.01, BAR[24]), (BAR[32] - 0.01, BAR[34]), (BAR[40] - 0.01, D)]
    loud = lambda t: any(a <= t < b for a, b in forte)
    # Simon
    for t, dd, m, v, h, who in SIMON:
        o.play('bassoons', m, t, dd * 0.95, v, pleft, 0.6)
        o.play('cellos', m, t, dd * 0.95, v - 4, pleft, 0.45)
    # the chorus
    parts = {'S': [('violins', 0, 0, 0.5), ('oboes', 0, -8, 0.3)],
             'A': [('violins', 0, -4, 0.35), ('violas', 0, -2, 0.3)],
             'T': [('violas', 0, -2, 0.45), ('bassoons', 0, -10, 0.22)],
             'B': [('cellos', 0, -2, 0.5), ('bassoons', 0, -8, 0.28)]}
    side = {'S': -0.35, 'A': -0.15, 'T': 0.15, 'B': 0.35}
    for t, dd, m, v, h, who in SUNG:
        for section, tr, dv, gg in parts[who]:
            o.play(section, m + tr, t, dd * 0.92, v + dv, side[who], gg)
        if who == 'B':
            o.play('basses', m - 12 if m >= 52 else m, t, dd * 0.92, v - 8, 0.0, 0.4)
        if who == 'S' and loud(t):
            o.play('trumpets', m, t, dd * 0.9, v - 4, -0.1, 0.4)
    # the orchestra where it plays alone, and its bass under everything
    alone = lambda t: t < T_SIMON or (T_CHORUS - 0.01 <= t < T_WE) or t >= BAR[46] - 0.01
    oboe_bars = (BAR[6] - 0.01, BAR[10])
    for t, dd, m, v, h, who in ORCH:
        if h == 1:
            if t < T_CHORUS:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.2) * 0.9, v - 6, None, 0.45)
                if m < 52:
                    o.play('basses', m, t, max(dd, 0.2) * 0.9, v - 10, None, 0.35)
            continue
        if alone(t):
            o.play('violins', m, t, max(dd, 0.15) * 0.9, v - 6, None, 0.35)
            if t >= T_CHORUS and m >= 67:
                o.play('trumpets', m, t, max(dd, 0.15) * 0.9, v - 8, 0.1, 0.3)
        elif oboe_bars[0] <= t < oboe_bars[1]:
            o.play('oboes', m, t, max(dd, 0.15) * 0.9, v - 10, 0.25, 0.3)
        elif t < T_CHORUS:
            o.play('violins', m, t, max(dd, 0.15) * 0.9, v - 14, None, 0.25)
    # the continuo: a harpsichord on the reduction, plucked short
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, int(min(105, v)), min(dd, 0.3)) for t, dd, m, v, h, who in ORCH]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.45, 0.0)
    # the drums: the downbeats of the forte bars, a roll into the last statement, the last chord
    for b in (22, 23, 32, 33, 39, 40, 42, 43, 44, 46, 47):
        o.hit('timpani', BAR[b], 100, pitch=0 if b not in (39, 44) else -5, gain=0.3, pan=0.2)
    o.hit('timpani roll', BAR[45] - 0.8, 80, pitch=0, gain=0.2, pan=0.2)
    o.hit('timpani', T_LAST, 110, pitch=0, gain=0.4, pan=0.2)
    for k, tj in enumerate(JUDAH):
        o.hit('timpani', tj, 70 + 18 * k, pitch=-5, gain=0.15 + 0.1 * k, pan=0.2)
    # the last chord held under the settling
    for m, sec in ((48, 'cellos'), (36, 'basses'), (55, 'violas'), (64, 'violins'), (72, 'violins'), (60, 'trumpets'),
                   (67, 'trumpets')):
        o.play(sec, m, T_LAST, D - T_LAST - 0.3, 92, 0.0, 0.3)
