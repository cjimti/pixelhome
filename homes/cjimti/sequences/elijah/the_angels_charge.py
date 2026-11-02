"""The Angels' Charge: an angel sends Elijah away into hiding, and eight angels go with him.

The house is still the drought: dust on every run, the people's candles low on Porch Left and Porch Right. An
Angel's silver light wakes in the middle of Porch Front (heaven) and flares with every word she sings: "Elijah, get
thee hence". On the first "Elijah" his amber answers on Right, and each time she names him a thin silver thread runs
down Porch Right to him. "Depart and turn thee eastward, thither hide thee by Cherith's brook": the amber stirs
toward the porch. "And the Lord thy God hath commanded the ravens to feed thee there; so do according unto his
word": the silver gathers, waiting.

Then the double quartet, "For He shall give His angels charge over thee": the Angel's light breaks into eight
silver points that fall down Porch Right to Elijah, four on each side of him, and when the voices begin he sets
out. He walks the whole roofline from Right toward Side, across the porch and down Left, and the eight go with
him: the first quartet just ahead, the second just behind, each point flaring when its voice sings and standing a
little nearer or farther from him with its pitch, so the chords show as a cluster breathing around the amber. "That
they shall protect thee in all the ways thou goest": the points close in on every "protect". He reaches the front
corner of the house, where Side begins, as the second quartet sings "charge over thee" for the last time, and the
points settle, faint, around him.

The music is Mendelssohn's own: No. 6 and the first twenty-seven bars of No. 7, transcribed from the Novello octavo
vocal score into the_angels_charge.musicxml and timed by scripts/score_excerpt.py at the marked tempos. The Angel
is played on flute and oboe; the eight voices of the double quartet on woodwinds, horn and cellos, each panned to
where its point is on the house; the accompaniment's pulsing chords and rising arpeggios on the strings.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL04'
TITLE = "The Angels' Charge"
KIND = 'show'
DESCRIPTION = ("An angel sends Elijah into hiding by the brook Cherith. Then eight silver lights, the double quartet's "
               "voices, gather around his amber and go with him the whole way round the house.")
VOICEOVER = 'For He shall give His angels charge over thee, that they shall protect thee in all the ways thou goest.'

EX = excerpt(__file__)                      # No. 6 (bars 1-9), No. 7 bars 1-27 (10-36)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
ANGEL = [n for n in EX['notes'] if n[5] == 'Angel']
UPPER = ('S1', 'S2', 'A1', 'A2')            # the first quartet
LOWER = ('T1', 'T2', 'B1', 'B2')            # the second
VOICE = {v: [n for n in EX['notes'] if n[5] == v] for v in UPPER + LOWER}
T_QUARTET = BAR[10]                         # Allegro non troppo
T_WALK = BAR[11]                            # "For He shall give His angels"
T_END = BAR[36]                             # the second quartet's last "thee"
AN_ON = np.array([n[0] for n in ANGEL])
NAMES = [AN_ON[0], AN_ON[6]]                # "E-li-jah" in bars 1 and 2
PROTECT = [n[0] for v in UPPER + LOWER for n in VOICE[v] if n[1] >= 0.4]

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
SILVER = hexc('#d8ecff')                    # the angels
SILVER_CORE = hexc('#ffffff')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def onsets(notes):
    return np.array([n[0] for n in notes]), np.array([n[2] for n in notes]), np.array([n[3] for n in notes])


def walk(G):
    """Elijah's place along the path at time t: still on Right, then from Right to the front corner of the house."""
    r0, r1 = span(G, 'Right')
    s0, s1 = span(G, 'Side')
    home = r0 + 0.35 * (r1 - r0)
    goal = span(G, 'Left')[0] + 12          # at the front corner of the house, where Side begins
    stir = r0 + 0.25 * (r1 - r0)

    def at(t):
        if t < BAR[4]:
            return home
        if t < T_WALK:
            return home + (stir - home) * smoothstep(BAR[4], BAR[9], t)
        u = (t - T_WALK) / (T_END - T_WALK)
        return stir + (goal - stir) * smoothstep(0, 1, min(max(u, 0.0), 1.0) ** 0.9)
    return at


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    h0, h1 = span(G, 'Porch Front')
    pr0, pr1 = span(G, 'Porch Right')
    mid = 0.5 * (h0 + h1)
    at = walk(G)

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    voices = {v: onsets(VOICE[v]) for v in UPPER + LOWER}
    prot = np.array(sorted(PROTECT))

    for f in range(F):
        t = f * DT
        fr = light(DUST, 0.28 * np.ones(G.N))
        fr += light(CANDLE, cand * people * 0.4 * (0.75 + 0.25 * flick(t)))
        e = at(t)

        # the Angel: a point in the middle of heaven, flaring on every note, until it breaks into eight
        if t < T_QUARTET + 2.5:
            j = int(np.searchsorted(AN_ON, t, side='right')) - 1
            voice = float(np.exp(-(t - AN_ON[j]) / 0.4)) if j >= 0 else 0.0
            show = smoothstep(0, 1.2, t) * (1 - smoothstep(T_QUARTET, T_QUARTET + 2.0, t))
            gather = smoothstep(BAR[6], BAR[9], t)
            fr += light(SILVER, show * ((0.55 + 0.4 * voice) * np.exp(-((d - mid) / 14) ** 2)
                                        + (0.2 + 0.25 * gather) * np.exp(-((d - mid) / 70) ** 2) * heaven))
            fr += light(SILVER_CORE, show * (0.35 + 0.5 * voice) * np.exp(-((d - mid) / 4) ** 2))
            # each "Elijah": a thread of silver down Porch Right to him
            for tn in NAMES:
                a = t - tn
                if 0 <= a < 2.5:
                    front = h1 + (e - h1) * min(a / 0.9, 1.0)
                    band = np.exp(-((d - front) / 14) ** 2) + 0.5 * ((d > h1 - 5) & (d < front))
                    fr += light(SILVER, 0.95 * np.exp(-a / 1.1) * band)

        # Elijah's amber: on Right from his first name, then walking
        on = smoothstep(NAMES[0] - 0.2, NAMES[0] + 0.6, t)
        sway = 1 + 0.08 * np.sin(2 * np.pi * t / 2.4)
        fr += light(AMBER, on * (0.85 * np.exp(-((d - e) / (16 * sway)) ** 2) + 0.15 * np.exp(-((d - e) / 45) ** 2)))
        fr += light(CORE, on * 0.6 * np.exp(-((d - e) / 5) ** 2))

        # the eight: falling down Porch Right to him over the first bar, then flanking him
        if t >= T_QUARTET:
            arrive = smoothstep(T_QUARTET, T_WALK, t)
            close = 0.0
            i = int(np.searchsorted(prot, t, side='right')) - 1
            if i >= 0:
                close = float(np.exp(-(t - prot[i]) / 0.8))
            for g, group in enumerate((UPPER, LOWER)):
                side = -1 if g == 0 else 1          # first quartet ahead (toward Side), second behind
                for k, v in enumerate(group):
                    ts, ms, vs = voices[v]
                    j = int(np.searchsorted(ts, t, side='right')) - 1
                    flare = float(np.exp(-(t - ts[j]) / 0.35)) if j >= 0 else 0.0
                    m = ms[j] if j >= 0 else 64
                    sung = j >= 0 and t - ts[j] < 2.2
                    off = (38 + 22 * k + 0.8 * (m - 62)) * (1 - 0.25 * close)
                    target = e + side * off
                    start = mid + (k - 1.5) * 9 + side * 6
                    p = start + (target - start) * arrive
                    lvl = (0.35 + 0.3 * sung + 0.45 * flare) * smoothstep(T_QUARTET, T_QUARTET + 0.6, t)
                    fade = 1 - 0.55 * smoothstep(T_END - 1.0, D, t)
                    fr += light(SILVER, lvl * fade * np.exp(-((d - p) / 6.5) ** 2))
                    fr += light(SILVER_CORE, 0.5 * flare * fade * np.exp(-((d - p) / 3.5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The Angel on flute and oboe; the double quartet on woodwinds, horn and cellos, panned with its points; the
    accompaniment on strings."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    at = walk(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.6)
    h0, h1 = span(G, 'Porch Front')
    mid = 0.5 * (h0 + h1)

    def role(t, d, m, v, hand):
        if t < T_QUARTET - 0.01:                     # the recitative's held chords
            if hand == 0:
                return [('violins' if m >= 60 else 'violas', 0, -8, 0.45)]
            return [('cellos', 0, -6, 0.5), ('basses', -12 if m >= 40 else 0, -10, 0.35)]
        if hand == 0:                                # the pulsing chords and the rising arpeggios
            return [('violins' if m >= 62 else 'violas', 0, -10, 0.42)]
        return [('cellos', 0, -8, 0.5), ('basses', -12 if m >= 40 else 0, -12, 0.35)]
    o.tutti(ORCH, role=role, pan=lambda t, m: 0.6 * pan_at(at(t)) if t >= T_WALK else 0.0)

    for t, d, m, v, h, who in ANGEL:
        o.play('flutes', m, t, d, v - 2, pan_at(mid), 0.55)
        o.play('oboes', m, t, d, v - 10, pan_at(mid), 0.3)

    sections = {'S1': ('flutes', 0.5), 'S2': ('oboes', 0.45), 'A1': ('clarinets', 0.5), 'A2': ('violas', 0.4),
                'T1': ('horns', 0.45), 'T2': ('clarinets', 0.4), 'B1': ('bassoons', 0.5), 'B2': ('cellos', 0.55)}
    for g, group in enumerate((UPPER, LOWER)):
        side = -1 if g == 0 else 1
        for k, v in enumerate(group):
            section, gain = sections[v]
            for t, d, m, vel, h, who in VOICE[v]:
                p = pan_at(at(t) + side * (38 + 22 * k))
                o.play(section, m, t, d, vel - 4, p, gain)
    o.hit('triangle', T_QUARTET, 70, gain=0.15, pan=pan_at(mid))
    o.hit('cymbal swell', T_END - 2.0, 60, gain=0.12, pan=pan_at(at(T_END)))
