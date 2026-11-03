"""Sion Now Her Head Shall Raise: after the first victory, warm light rises from the porch toward the Temple and the
people tune their harps.

The scene opens where Fall'n Is the Foe (JM07) ended, the ranks on the field, which give way over the first two
seconds (CARRY, from JM07's last frame: change both together) to the night after the battle, held still: night blue over the house, the people's blue and white
low on the wings, the Temple on Porch Front with its grey idols and the faint glow of the lights. The Israelitish
Woman sings alone, a white-silver light at the street end of Porch Left that climbs the road to the Temple a step
with every phrase, brightening on each note. On "raise" warm gold rises from the street ends of both porch runs
toward the Temple, and it stays, a little higher with each phrase. Every "Tune your harps" is answered by the harp:
a cascade of bright glints up the porch runs, one on each plucked note.

Then the chorus (No. 32), forte: the Woman's long "harps" over five voices, and the whole house comes up, the blue
and white bands on Left, Right and Side lifting on every chord. "Sion now her head shall raise": a great wave of gold
climbs both porch runs into the Temple, and the Temple's glow swells round the idols. The inner voices tune their
harps again over the basses' long "raise" (glints along the wings now), the full chorus sings "Tune your harps to
songs of praise", gold running out from the porch along the wings on every bar, and the last "praise." settles the
house into a warm, steady tableau: gold on the porch runs, the people's blue and white on the wings, the Temple
glowing. That last frame is where Sound an Alarm! (JM09) begins (TABLEAU there: change both together).

The music is Handel's own: No. 31, the duet's first voice from the last bar of its ritornello through her first
statement, and No. 32, the chorus's first eighteen bars and its last seven sung bars, transcribed from the Novello
vocal score into sion_now_her_head.musicxml and timed by scripts/score_excerpt.py (the duet's Andante at crotchet 80,
the chorus at 88). The Woman plays on an oboe over a harpsichord continuo and soft strings; the chorus on strings
with oboes and bassoons doubling; a harp plucks every glint. render() and score() both read the notes from the
excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM08'
TITLE = 'Sion Now Her Head Shall Raise'
KIND = 'show'
DESCRIPTION = ("After the victory, warm light rises from the porch toward the Temple while the Woman sings, harp glints "
               "climb the porch on every 'Tune your harps', and the chorus lifts the whole house.")
VOICEOVER = 'After the first victory, the people take up their harps. Sion now her head shall raise.'

EX = excerpt(__file__)              # No. 31 bars 16-28 (compact 1-13), No. 32 bars 1-18 (14-31) and its last seven (32-38)
BAR = {int(m): t for m, t in EX['bars']}
END = round(EX['seconds'] + 3.0, 2)  # the last chord held
D = END
NOTES = EX['notes']
WOMAN = [n for n in NOTES if n[5] == 'Woman']
CHORUS = [n for n in NOTES if n[5] in ('S1', 'S2', 'A', 'T', 'B')]
ORCH = [n for n in NOTES if n[5] == 'Orch']
T_CHORUS = BAR[14]                  # No. 32: the Woman's "harps" and the chorus, forte
T_SION = BAR[18]                    # "Sion now her head shall raise"
T_RAISE = BAR[22]                   # "raise;": the basses hold it, the inner voices tune their harps
T_FULL = BAR[27]                    # the full chorus: "Tune your harps to songs of praise"
T_FINAL = BAR[38]                   # "praise."
RAISE_SOLO = BAR[5]                 # the Woman's "raise;"
# the harp answers each "harps": a cascade up the porch runs (the duet, the chorus's first bars) or along the wings
HARPS = [BAR[b] for b in (7, 9, 11, 15, 18, 24, 26, 28, 32, 36)]
ON_WINGS = {BAR[24], BAR[26]}
WOMAN_ON = np.array(sorted(n[0] for n in WOMAN))
CH_ON = np.array(sorted({round(n[0], 3) for n in CHORUS}))
CH_VEL = np.array([max(n[3] for n in CHORUS if abs(n[0] - t) < 0.002) for t in CH_ON])

NIGHT = hexc('#0a1a4a')
BLUE = hexc('#1e5bd8')              # the people
WHITE = hexc('#f2f6ff')
SILVER = hexc('#e8f0ff')            # the Israelitish Woman
OIL = hexc('#ffb33a')               # warm light, the Temple light
TIP = hexc('#fff1c0')               # glints
STONE = hexc('#6a6a6a')             # the idols
IDOLS = (0.13, 0.37, 0.63, 0.87)    # where the idols stand along Porch Front (as in We Never Will Bow Down)
WIDE = 0.09


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def parts(G):
    """Masks and coordinates the scene and its tableau use."""
    d, seg = G.pd, G.seg_of
    pf0, pf1 = span(G, 'Porch Front')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    temple = (seg == 'Porch Front').astype(float)
    runs = np.isin(seg, ['Porch Left', 'Porch Right']).astype(float)
    wings = np.isin(seg, ['Left', 'Right']).astype(float)
    side = (seg == 'Side').astype(float)
    up = np.zeros(G.N)                                      # 0 at the street end of a porch run, 1 at the Temple
    m = seg == 'Porch Left'
    up[m] = (d[m] - pl0) / (pl1 - pl0)
    m = seg == 'Porch Right'
    up[m] = (pr1 - d[m]) / (pr1 - pr0)
    u = np.clip((d - pf0) / (pf1 - pf0), -1, 2)
    idol = np.max([np.clip(1 - np.abs(u - c) / WIDE, 0, 1) ** 0.4 for c in IDOLS], 0) * temple
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
    return dict(temple=temple, runs=runs, wings=wings, side=side, up=up, idol=idol, band=band)


def opening(G):
    """The first frame, held still for the first bars: night blue, the people low on the wings, the Temple's idols."""
    p = parts(G)
    house = 1 - p['temple']
    return (light(NIGHT, 0.22 * house) + light(BLUE, 0.16 * p['band'] * (p['wings'] + 0.5 * p['side']))
            + light(WHITE, 0.12 * (1 - p['band']) * (p['wings'] + 0.5 * p['side']))
            + light(OIL, 0.22 * 0.8 * p['temple']) + light(STONE, 0.45 * p['idol']))


def tableau(G):
    """The last frame, steady: warm gold on the porch runs, blue and white bands on the wings and Side, the Temple
    glowing round its idols. Sound an Alarm! (JM09) opens on it."""
    p = parts(G)
    wings = p['wings'] + 0.6 * p['side']
    return (light(NIGHT, 0.12 * (1 - p['temple'])) + light(OIL, 0.5 * p['runs'] * (0.75 + 0.25 * p['up']))
            + light(BLUE, 0.42 * p['band'] * wings) + light(WHITE, 0.32 * (1 - p['band']) * wings)
            + light(OIL, 0.22 * 1.6 * p['temple']) + light(TIP, 0.05 * p['temple']) + light(STONE, 0.5 * p['idol']))


def pulse(t, onsets, vel, tau):
    i = int(np.searchsorted(onsets, t, side='right')) - 1
    if i < 0:
        return 0.0
    return float(np.exp(-(t - onsets[i]) / tau) * vel[i] / 100)


PURPLE7 = hexc('#6a2ca0')
GOLD7, CORE7 = hexc('#ffc83c'), hexc('#fff4d0')
CARRY = 2.0                         # seconds Fall'n Is the Foe's last frame (JM07) takes to give way to the night
JM07_END = 82.57                    # JM07's length: its Glow is carried on from there (change with JM07)


def jm07_end(G, glow7, t):
    """Fall'n Is the Foe's last frame (JM07), rebuilt: the Maccabees' ranks over all of Porch Right and Right, blue and
    white in turn every 21 units, Judas's gold in the middle of the field, blue on Left, Porch Left and Side, the idols
    over the glow. Change it with JM07 (its ranks(), SHIFT1 and the end of its render())."""
    d, seg = G.pd, G.seg_of
    l0, l1 = span(G, 'Left')
    p0, p1 = span(G, 'Porch Left')
    q0, q1 = span(G, 'Porch Right')
    f0, f1 = span(G, 'Porch Front')
    r0, r1 = span(G, 'Right')
    base = np.arange(l0 + 14, l1 - 6, 21.0)
    white = np.arange(len(base)) % 2 == 1
    pos = base + 1162.0
    vis = np.where(pos < p1, smoothstep(p1 - 4, p1 - 30, pos), smoothstep(q0 + 4, q0 + 30, pos))
    shape = np.exp(-((d[None, :] - pos[:, None]) / 4.0) ** 2)
    lvl = 0.48 * vis
    fr = light(WHITE, (lvl * white) @ shape) + light(BLUE, 1.25 * (lvl * ~white) @ shape)
    grid = np.arange(base[0] + 1162.0, r1 - 4, 21.0)
    gw = np.arange(len(grid)) % 2 == 1
    g = 0.48 * (grid > pos[-1] + 1)
    gshape = np.exp(-((d[None, :] - grid[:, None]) / 4.0) ** 2)
    fr += light(WHITE, (g * gw) @ gshape) + light(BLUE, 1.25 * (g * ~gw) @ gshape)
    fr += light(BLUE, 0.22 * np.isin(seg, ['Side', 'Porch Left', 'Left']))
    idols = np.zeros(G.N)
    for k in range(4):
        idols += smoothstep(14, 9, np.abs(d - (f0 + (0.14 + 0.24 * k) * (f1 - f0))))
    fr += light(STONE, 0.5 * np.minimum(idols, 1) * (seg == 'Porch Front')) + glow7.frame(JM07_END + t, 0.55)
    j = 0.5 * (r0 + r1)
    fr += light(GOLD7, 0.95 * np.exp(-((d - j) / 6.0) ** 2)) + light(CORE7, 0.6 * np.exp(-((d - j) / 2.5) ** 2))
    fr += light(GOLD7, 0.15 * np.exp(-((d - j) / 30.0) ** 2))
    return fr


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p = parts(G)
    temple, runs, wings, side, up, idol, band = (p[k] for k in ('temple', 'runs', 'wings', 'side', 'up', 'idol', 'band'))
    house = 1 - temple
    glow = Glow(G, seed)
    glow7 = Glow(G, 7)
    flick = Flicker(rng, G.N, 0.3, 1.2)
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    first, last = opening(G), tableau(G)
    # each harp cascade: six glints climbing a porch run (or running out along a wing), alternating sides
    glints = []
    for k, th in enumerate(HARPS):
        for j in range(6):
            tg = th + 0.11 * j
            if th in ON_WINGS:
                pos = (l1 - (0.1 + 0.14 * j) * (l1 - l0)) if k % 2 == 0 else (r0 + (0.1 + 0.14 * j) * (r1 - r0))
            else:
                f = 0.08 + 0.16 * j + rng.uniform(-0.03, 0.03)
                pos = (pl0 + f * (pl1 - pl0)) if (k + j) % 2 == 0 else (pr1 - f * (pr1 - pr0))
            glints.append((tg, pos))
    # the Woman's light: a step up Porch Left with each of her phrases, from the street end to near the Temple
    w_steps = [BAR[2], BAR[6], BAR[8], BAR[10], BAR[12], T_CHORUS]
    w_pos = [pl0 + f * (pl1 - pl0) for f in (0.12, 0.3, 0.45, 0.6, 0.72, 0.85)]
    for f in range(F):
        t = f * DT
        sh = 0.92 + 0.08 * flick(t)
        chorus = smoothstep(T_CHORUS - 0.3, T_CHORUS + 1.5, t)
        full = smoothstep(T_FULL - 0.5, T_FULL + 2.0, t)
        # the house: night blue, the people's bands coming up with the chorus and lifting on its chords
        ch = pulse(t, CH_ON, CH_VEL, 0.5) if t >= T_CHORUS else 0.0
        ppl = 0.16 + 0.18 * chorus + 0.1 * full + 0.24 * ch * chorus
        wv = wings + 0.5 * side + 0.5 * side * chorus
        fr = light(NIGHT, (0.22 - 0.1 * chorus) * house * sh)
        fr += light(BLUE, ppl * band * wv * sh) + light(WHITE, 0.78 * ppl * (1 - band) * wv * sh)
        # warm light on the porch runs: rising from the street ends on "raise", higher with every phrase after
        rise = smoothstep(RAISE_SOLO, RAISE_SOLO + 2.2, t)
        reach = min(1.0, 0.45 * rise + 0.1 * sum(t >= b for b in w_steps[2:]) + 0.3 * chorus)
        front = smoothstep(reach + 0.05, reach - 0.15, up)
        warm = (0.2 + 0.18 * chorus + 0.1 * full) * rise
        fr += light(OIL, warm * front * runs * sh)
        # the Temple: the lights' glow round the idols, swelling as Sion raises her head
        sion = smoothstep(T_SION, T_RAISE, t)
        fr += glow.frame(t, 0.8 + 0.4 * chorus + 0.6 * sion)
        fr += light(STONE, (0.45 + 0.05 * chorus) * idol)
        # "Sion now her head shall raise": a wave of gold climbing both porch runs into the Temple on each bar
        for b in range(18, 23):
            a = t - BAR[b]
            if 0 <= a < 2.2:
                pos = smoothstep(0, 1.6, a)
                fr += light(OIL, 0.55 * (1 - smoothstep(1.4, 2.2, a)) * np.exp(-((up - pos) / 0.12) ** 2) * runs)
                fr += light(TIP, 0.25 * np.exp(-((a - 1.6) / 0.3) ** 2) * temple)
        # the full chorus: gold running out from the porch along the wings on every bar
        if t >= T_FULL:
            for b in range(27, 39):
                a = t - BAR[b]
                if 0 <= a < 2.0:
                    out_l = np.clip((l1 - d) / (l1 - l0), -1, 2)
                    out_r = np.clip((d - r0) / (r1 - r0), -1, 2)
                    pos = 1.2 * a / 2.0
                    w = np.exp(-((out_l - pos) / 0.1) ** 2) * (G.seg_of == 'Left') + \
                        np.exp(-((out_r - pos) / 0.1) ** 2) * (G.seg_of == 'Right')
                    fr += light(OIL, 0.75 * np.exp(-a / 1.2) * w)
        # the harp's glints
        for tg, pos in glints:
            a = t - tg
            if 0 <= a < 0.9:
                fr += light(TIP, np.exp(-a / 0.25) * np.exp(-((d - pos) / 5.0) ** 2))
                fr += light(OIL, 0.5 * np.exp(-a / 0.45) * np.exp(-((d - pos) / 16.0) ** 2))
        # the Woman: white-silver, a step up the road with each phrase, brightening on each note
        if t < T_FINAL + 2.0:
            wp = w_pos[0]
            for ts, ps in zip(w_steps, w_pos):
                wp = wp + (ps - wp) * smoothstep(ts - 0.6, ts + 0.3, t)
            k = int(np.searchsorted(WOMAN_ON, t, side='right')) - 1
            note = np.exp(-(t - WOMAN_ON[k]) / 0.5) if k >= 0 else 0.0
            sing = smoothstep(BAR[2] - 1.0, BAR[2] + 0.4, t) * (1 - smoothstep(BAR[17], BAR[18], t))
            wl = sing * (0.55 + 0.45 * note)
            fr += light(SILVER, wl * np.exp(-((d - wp) / 5.0) ** 2))
            fr += light(SILVER, 0.3 * wl * np.exp(-((d - wp) / 20.0) ** 2))
        # the final chord: everything settles into the tableau
        settle = smoothstep(T_FINAL, END - 0.4, t)
        if settle > 0:
            fr = (1 - settle) * fr + settle * last
        # the opening: held still at first, giving way to the scene
        hold = 1 - smoothstep(2.0, 3.2, t)
        if hold > 0:
            fr = (1 - hold) * fr + hold * first
        # before that, Fall'n Is the Foe's last frame (JM07) gives way to the night after the battle
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * jm07_end(G, glow7, t)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The Woman on an oboe over soft strings and a harpsichord continuo, from where her light is; the chorus on
    strings with oboes and bassoons doubling, sopranos from Left, tenors and basses from Right; a harp cascade on every
    glint, from where it climbs."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    o = Orchestra(M, level=2.2)
    wpan = pan_at(pl0 + 0.5 * (pl1 - pl0))
    for t, dur, m, v, h, who in WOMAN:
        o.play('oboes', m, t, dur * 0.97, 70 + 0.3 * v, wpan, 1.4)
    chorus_parts = {'S1': [('violins', 0, 0, 0.45), ('oboes', 0, -10, 0.22)],
                    'S2': [('violins', 0, -4, 0.35), ('flutes', 0, -10, 0.2)],
                    'A': [('violins', 0, -4, 0.3), ('violas', 0, -2, 0.35)],
                    'T': [('violas', 0, -2, 0.42), ('bassoons', 0, -10, 0.22)],
                    'B': [('cellos', 0, -2, 0.48), ('bassoons', 0, -8, 0.26)]}
    side = {'S1': pan_at(sum(span(G, 'Left')) / 2), 'S2': pan_at(sum(span(G, 'Porch Left')) / 2), 'A': 0.0,
            'T': pan_at(sum(span(G, 'Porch Right')) / 2), 'B': pan_at(sum(span(G, 'Right')) / 2)}
    for t, dur, m, v, h, who in CHORUS:
        for sec, tr, dv, g in chorus_parts[who]:
            o.play(sec, m + tr, t, dur * 0.97, 62 + 0.35 * v + dv, 0.6 * side[who], g)
        if who == 'B':
            o.play('basses', m - 12 if m >= 50 else m, t, dur * 0.97, 58 + 0.3 * v, 0.0, 0.32)
    # the accompaniment: soft strings where it plays alone, its bass on cellos under the chorus
    for t, dur, m, v, h, who in ORCH:
        if t < T_CHORUS - 0.01:
            o.play('violins' if h == 0 and m >= 55 else 'violas' if h == 0 else 'cellos', m, t, dur * 0.95,
                   54 + 0.2 * v, None, 0.32 if h == 0 else 0.42)
        elif h == 1:
            o.play('cellos', m if m >= 36 else m + 12, t, dur * 0.95, 56 + 0.2 * v, 0.0, 0.25)
    # the continuo: a harpsichord on the accompaniment, and on the basses' notes with the inner voices over them
    cont = [(t, m, int(min(100, 60 + 0.3 * v)), min(dur, 0.35)) for t, dur, m, v, h, who in ORCH]
    for t, dur, m, v, h, who in CHORUS:
        if who == 'B':
            cont.append((t, m, 74, min(dur, 0.35)))
            for cm in sorted({n[2] for n in CHORUS if abs(n[0] - t) < 0.02 and n[5] in ('A', 'T')}):
                cont.append((t, cm, 64, min(dur, 0.35)))
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, END + 2.0), 0.0, 0.4, 0.0)
    # the harp: a rising spread of the chord sounding at each "harps", from where the glints climb
    for k, th in enumerate(HARPS):
        sounding = sorted({n[2] for n in NOTES if n[0] <= th + 0.02 < n[0] + n[1]})
        pcs = sorted({m % 12 for m in sounding}) or [7, 11, 2]
        notes = []
        m = 55
        while len(notes) < 6:
            m += 1
            if m % 12 in pcs:
                notes.append(m)
        for j, mm in enumerate(notes):
            if th in ON_WINGS:
                pos = (l1 - (0.1 + 0.14 * j) * (l1 - l0)) if k % 2 == 0 else (r0 + (0.1 + 0.14 * j) * (r1 - r0))
            else:
                f = 0.08 + 0.16 * j
                pos = (pl0 + f * (pl1 - pl0)) if (k + j) % 2 == 0 else (pr1 - f * (pr1 - pr0))
            o.play('harp', mm, th + 0.11 * j, 1.2, 78, pan_at(pos), 0.75)
    # the last chord held: strings under it, a last harp spread
    for m in (43, 55, 59, 62, 67):
        o.play('cellos' if m < 50 else 'violas' if m < 60 else 'violins', m, T_FINAL + 0.4, END - T_FINAL - 0.8, 52,
               None, 0.3)
    for j, mm in enumerate((55, 59, 62, 67, 71, 74, 79)):
        o.play('harp', mm, T_FINAL + 0.5 + 0.12 * j, 2.0, 66, 0.6 * (j - 3) / 3, 0.6)
