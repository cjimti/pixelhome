"""Call Forth Thy Powers: Judas takes command, and his gold runs the length of the ranks on Left and back.

It opens where Arm, Arm, Ye Brave! (JM04) ended: the rank of blue and white lights steady along Left on a low blue,
Simon's deep blue and Judas's gold among them, the Seleucid purple on Right and Side, the people on the porch runs and
the idols grey in the Temple over the lights' glow. The orchestra's opening runs, in unison, are a white spark racing
down Left and back up it, high notes toward the porch and low ones toward the far corner of the house.

Then Judas: "Call forth thy pow'rs, my soul, and dare the conflict of unequal war." His gold leaves its place and
follows his voice along Left, toward the porch as it climbs and away as it falls, so his long runs on "war" carry it
the length of the rank and back; every light it passes flares and stays a little brighter, until the whole rank is
lit by him. "Great is the glory of the conq'ring sword": the gold grows, each "sword" is a white stroke along the rank,
and on "That triumphs in sweet liberty restor'd" the purple on Right shrinks back. The closing ritornello runs its
spark down the rank once more and Judas's gold returns to its place; the last frame is the rank steady and bright,
which is where Disdainful of Danger (JM06) begins.

The music is Handel's own: No. 13, the air's A section and its B section ("Great is the glory") to "restor'd.", run
into the last three bars, its closing ritornello, as the da capo would, transcribed from the Novello vocal score into
call_forth_thy_powers.musicxml and timed by scripts/score_excerpt.py at crotchet 96. Judas plays on horns, with a
trumpet joining him for "Great is the glory"; the strings play the reduction, the runs in unison on violins, cellos
and basses, and a harpsichord plays the continuo. render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM05'
TITLE = 'Call Forth Thy Powers'
KIND = 'show'
DESCRIPTION = ("Judas takes command: his gold follows his voice up and down the ranks on Left, and every light it "
               "passes flares and stays brighter, until the whole rank shines.")
VOICEOVER = 'Judas, the new leader, takes up the sword, and calls on his soul to rise to the fight.'

EX = excerpt(__file__)              # No. 13 bars 1-30 (compact 1-30, cut after "restor'd.") and 43-45 (31-33)
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 3.0, 2)  # the last chord held
NOTES = EX['notes']
JUDAS = sorted([n for n in NOTES if n[5] == 'Judas'], key=lambda n: n[0])
ORCH = [n for n in NOTES if n[5] == 'Orch']
QUARTER = BAR[2] - BAR[1]
T_SING = JUDAS[0][0]                # "Call forth"
T_GREAT = BAR[22]                   # the B section
SWORDS = [BAR[24], BAR[25]]         # "sword,"
T_LIBERTY = BAR[25] + 2 * QUARTER   # "That triumphs in sweet liberty restor'd"
T_CODA = BAR[32] - 0.75 * QUARTER   # the closing ritornello
T_LAST = BAR[33]                    # the last chord
T_END = T_LAST + 1.0
RITORNELLI = [(0.0, BAR[3]), (BAR[11], BAR[12]), (BAR[20], BAR[22]), (T_CODA, T_LAST)]
# the unison runs: the bass line's semiquavers where the orchestra plays alone
RUNS = sorted([(n[0], n[2]) for n in ORCH if n[4] == 1 and n[1] < 0.2 and any(a <= n[0] < b for a, b in RITORNELLI)])

PURPLE = hexc('#6a2ca0')            # the Seleucid armies
STONE = hexc('#6a6a6a')             # the idols
BLUE = hexc('#1e5bd8')              # the Maccabees
WHITE = hexc('#f2f6ff')
SIMON_C = hexc('#2850c8')           # Simon
GOLD = hexc('#ffc83c')              # Judas
CORE = hexc('#fff4d0')
RANK = 12


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


class Stage:
    """JM04's last frame, this scene's ground: the rank on Left with Simon and Judas, the porch, the idols, the purple."""

    def __init__(self, G):
        d, seg = G.pd, G.seg_of
        self.d = d
        self.left = (seg == 'Left').astype(float)
        self.right = (seg == 'Right').astype(float)
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
        mid = self.l0 + 0.55 * L
        self.sc = mid - 0.12 * L                            # Simon
        self.jc = mid + 0.04 * L                            # Judas's place
        self.simon = (1.3 * np.exp(-((d - self.sc) / 7) ** 2) + 0.5 * np.exp(-((d - self.sc) / 24) ** 2)) * self.left
        self.pos = self.l0 + np.linspace(0.06, 0.94, RANK) * L
        self.shape = np.exp(-((d[None, :] - self.pos[:, None]) / 6.0) ** 2) * self.left
        self.white = np.arange(RANK) % 2 == 1

    def ground(self, glow, t, purple=1.0, people=1.0):
        fr = light(PURPLE, 0.42 * purple * self.right + 0.42 * (self.right_side - self.right) + 0.14 * self.porch)
        fr += light(BLUE, 0.2 * self.left)
        fr += light(STONE, 0.5 * self.idols) + glow.frame(t, 0.55)
        fr += light(BLUE, 0.66 * people * self.blue_p) + light(WHITE, 0.8 * 0.66 * people * self.white_p)
        fr += light(SIMON_C, 0.5 * self.simon)
        return fr

    def rank(self, lv):
        return light(BLUE, (lv * ~self.white) @ self.shape) + light(WHITE, 0.8 * (lv * self.white) @ self.shape)

    def judas(self, p, size=1.0):
        d, left = self.d, self.left
        return (light(GOLD, 1.4 * 0.85 * size * np.exp(-((d - p) / (9 * size)) ** 2) * left)
                + light(GOLD, 0.18 * size * np.exp(-((d - p) / 34) ** 2) * left))

    def end(self, glow, t):
        """The last frame: the ground, every light of the rank at full (1.0), Judas's gold in its place."""
        return self.ground(glow, t) + self.rank(np.ones(RANK)) + self.judas(self.jc)


def where_on_left(st, m, lo, hi, pad=0.04):
    u = np.clip((m - lo) / (hi - lo), 0, 1)
    return st.l0 + (pad + (1 - 2 * pad) * u) * (st.l1 - st.l0)


def judas_path(st):
    """Judas's gold along Left at each frame: following his voice's pitch while he sings, home to his place between."""
    F = nframes(D)
    lo, hi = min(n[2] for n in JUDAS), max(n[2] for n in JUDAS)
    starts = np.array([n[0] for n in JUDAS])
    ends = np.array([n[0] + n[1] for n in JUDAS])
    p, out, singing = st.jc, np.empty(F), np.zeros(F, bool)
    for f in range(F):
        t = f * DT
        i = int(np.searchsorted(starts, t, side='right')) - 1
        if i >= 0 and t < ends[i] + 0.6 and t < T_CODA:
            target, tau = where_on_left(st, JUDAS[i][2], lo, hi), 0.08
            singing[f] = t < ends[i] + 0.05
        else:
            target, tau = st.jc, 0.5
        p += (target - p) * min(1.0, DT / tau)
        out[f] = p
    return out, singing


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    st = Stage(G)
    d = st.d
    glow = Glow(G, seed)
    flick = Flicker(rng, G.N, 0.6, 2.2)
    path, singing = judas_path(st)
    run_t = np.array([r[0] for r in RUNS])
    run_m = np.array([r[1] for r in RUNS])
    rlo, rhi = run_m.min(), run_m.max()
    base = np.full(RANK, 0.75)              # each light's steady level, raised each time Judas passes it
    flash = np.zeros(RANK)
    near_prev = np.zeros(RANK, bool)
    for f in range(F):
        t = f * DT
        settle = smoothstep(T_LAST, T_END, t)
        great = smoothstep(T_GREAT - 0.3, T_GREAT + 1.0, t) * (1 - smoothstep(T_CODA - 1.0, T_CODA + 0.5, t))
        shrink = smoothstep(T_LIBERTY, T_LIBERTY + 2.0, t) * (1 - smoothstep(T_CODA, T_LAST, t))
        fr = st.ground(glow, t, purple=1 - 0.4 * shrink, people=0.92 + 0.08 * flick(t))
        fr += light(BLUE, 0.1 * great * st.left)
        # Judas's gold, and the lights it passes
        p = path[f]
        near = np.abs(st.pos - p) < 14.0
        if singing[f]:
            hit = near & ~near_prev
            flash[hit] = 1.0
            base[hit] = np.minimum(1.0, base[hit] + 0.08)
        near_prev = near
        flash *= np.exp(-DT / 0.4)
        # the orchestra's unison runs: a spark down and up the rank, the lights flickering as it passes
        spark = 0.0
        if len(run_t):
            j = int(np.searchsorted(run_t, t, side='right')) - 1
            for k in range(max(0, j - 3), j + 1):                # the spark and its short trail
                a = t - run_t[k]
                if 0 <= a < 0.6:
                    sp = where_on_left(st, run_m[k], rlo, rhi)
                    fr += light(WHITE, 1.1 * np.exp(-a / 0.15) * np.exp(-((d - sp) / 8.0) ** 2) * st.left)
                    spark = spark + np.exp(-((st.pos - sp) / 20.0) ** 2) * np.exp(-a / 0.15)
        # "sword": a white stroke along the rank from Judas
        stroke = np.zeros(RANK)
        for ts in SWORDS:
            a = t - ts
            if 0 <= a < 1.2:
                front = 500 * a
                stroke += np.exp(-((np.abs(st.pos - p) - front) / 35.0) ** 2) * np.exp(-a / 0.5)
                fr += light(WHITE, 0.7 * np.exp(-((np.abs(d - p) - front) / 20.0) ** 2) * np.exp(-a / 0.4) * st.left)
        lv = base + 0.9 * flash + 0.4 * spark + 0.6 * stroke
        lv = (1 - settle) * lv + settle * 1.0
        fr += st.rank(lv)
        size = 1.0 + 0.35 * great + 0.25 * singing[f]
        fr += st.judas(p, size)
        if singing[f]:
            fr += light(CORE, 0.5 * np.exp(-((d - p) / 3.0) ** 2) * st.left)
        if t < 1.0:                                           # the opening flows from JM04's last frame
            u = smoothstep(0.0, 1.0, t)
            fr = u * fr + (1 - u) * (st.ground(glow, t) + st.rank(np.full(RANK, 0.75)) + st.judas(st.jc))
        if settle > 0:
            fr = (1 - settle) * fr + settle * st.end(glow, t)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Judas on horns, following his gold across the house, a trumpet with him in "Great is the glory"; the strings on
    the reduction, the runs in unison on violins, cellos and basses; the harpsichord continuo; the last chord held."""
    st = Stage(G)
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    lo, hi = min(n[2] for n in JUDAS), max(n[2] for n in JUDAS)
    o = Orchestra(M, level=1.95)
    for t, dd, m, v, h, who in JUDAS:
        pan = pan_at(where_on_left(st, m, lo, hi))
        o.play('horns', m, t, dd * 0.95, v + 6, pan, 0.75)
        if T_GREAT - 0.01 <= t < T_LIBERTY:
            o.play('trumpets', m, t, dd * 0.92, v - 6, pan, 0.3)
    alone = lambda t: any(a <= t < b for a, b in RITORNELLI)
    for t, dd, m, v, h, who in ORCH:
        if h == 1:
            o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.12) * 0.95, v - 4, None, 0.45)
            if m < 55:
                o.play('basses', m, t, max(dd, 0.12) * 0.95, v - 10, None, 0.3)
        else:
            if alone(t) and dd < 0.2:                        # the unison runs on violins too
                o.play('violins', m if m >= 55 else m + 12, t, dd * 0.95, v - 4, None, 0.45)
            else:
                o.play('violins' if m >= 55 else 'violas', m, t, max(dd, 0.12) * 0.9, v - 18, None, 0.2)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, int(min(100, v)), min(dd, 0.25)) for t, dd, m, v, h, who in ORCH if h == 1 or dd >= 0.3]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.45, 0.0)
    for m, sec in ((38, 'basses'), (50, 'cellos'), (57, 'violas'), (62, 'violins'), (66, 'violins'), (69, 'violins')):
        o.play(sec, m, T_LAST, D - T_LAST - 0.3, 88, 0.0, 0.3)
