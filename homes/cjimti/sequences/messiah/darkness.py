"""The People That Walked in Darkness: the house goes as dark as it can, one dim light wanders, and Porch Front opens.

"For behold, darkness shall cover the earth." Under the strings' trembling figures the house sinks, run by run, into a
blue-black bed, the deepest it can hold without going out; the bass's deep amber voice speaks from the back of the
porch and grows fainter with it. "And gross darkness the people": the last warmth drains away.

Then the air, which Handel writes with all the strings in unison with the singer, wandering, as if feeling its way.
On the house it is one dim amber point of light, alone in the dark, wandering the roofline: every note moves it, up
the line when the tune climbs and back when it falls, never settling, never finding the way. Each time the voice
says "darkness" the point shrinks.

"Have seen a great light": on the first "light" a glow opens in the middle of Porch Front, the far light at the back of
the scene, and on the second, forte, the whole of Porch Front opens in white-gold, spilling down the porch runs. The
wandering point turns toward it, and the scene holds there: the house still dark, the far light open.

The music is Handel's own: Messiah No. 10, the strings' first two bars and the recitative from "For behold" to "and
gross darkness the people", and No. 11 from its upbeat to the first "have seen a great light", transcribed from
Prout's full score (Novello, 1902) into darkness.musicxml (No. 11 numbered on from No. 10) and timed by
scripts/score_excerpt.py, the recitative a little quicker than Prout's mark. Strings only, as Handel scored them; the
bass's line on cellos and a bassoon, and in the air the strings in unison with it.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS08'
TITLE = 'The People That Walked in Darkness'
KIND = 'show'
DESCRIPTION = ("Darkness covers the earth: the house sinks to its deepest blue-black, one dim light wanders the "
               "roofline feeling its way, and on \"a great light\" Porch Front opens.")
VOICEOVER = 'The people that walked in darkness have seen a great light.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 3.0
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Bass', 'Vn1', 'Vn2', 'Va', 'Bassi')}
VOICE = PART['Bass']
V_ON = np.array([n[0] for n in VOICE])
T_BEHOLD = VOICE[0][0]                      # "For behold"
T_GROSS = BAR[8]                            # "and gross darkness"
T_AIR = BAR[12]                             # No. 11's upbeat
LINE = [n for n in PART['Vn1'] if n[0] >= T_AIR - 0.01]          # the unison tune
L_ON = np.array([n[0] for n in LINE])
T_LIGHT1 = BAR[24] + 0.5 * (BAR[25] - BAR[24])                   # "light," the first
T_LIGHT2 = BAR[25] + (END - BAR[25]) * 2 / 3                       # "light," forte (the air's bar 13, beat 3)
DARK_WORDS = [p[0] for p in EX['singing'] if 'dark' in p[3]]

BED = hexc('#06081a')                       # darkness
NIGHT = hexc('#14204a')
AMBER = hexc('#e08a20')                     # the bass
GLORY = hexc('#fff2c8')
GOLD = hexc('#ffd040')


def render(G, seed=8):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    front = seg == 'Porch Front'
    runs = np.isin(seg, ['Porch Left', 'Porch Right'])
    pf = G.pd[G.seg['Porch Front']]
    pf0, pf1 = float(pf.min()), float(pf.max())
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    l0 = float(G.pd[G.seg['Left']].min())
    r1 = float(G.pd[G.seg['Right']].max())
    off = np.abs(d - mid) / half
    # each run sinks in turn on "darkness shall cover the earth", the porch last
    order = {'Right': 0.0, 'Side': 0.15, 'Left': 0.3, 'Porch Right': 0.5, 'Porch Left': 0.6, 'Porch Front': 0.8}
    lag = np.array([order[s] for s in seg])
    tremble = Flicker(rng, G.N, 3.0, 9.0)
    slow = Flicker(rng, G.N, 0.08, 0.3)
    # the wandering point: each note of the tune moves it, by how far the tune moved
    pos = np.zeros(len(LINE))
    p = l0 + 160.0
    for k, n in enumerate(LINE):
        if k:
            step = (n[2] - LINE[k - 1][2]) * 13.0
            p += step + 5.5 + 4.0 * np.sign(rng.uniform(-1, 1))      # wandering, and drifting on
            if p < l0 + 40 or p > r1 - 40:
                p -= 2 * step
        pos[k] = p
    for f in range(F):
        t = f * DT
        # the bed: from a dim blue night down to the deepest blue-black, run by run
        sink = np.clip((t - T_BEHOLD - lag * 6.0) / 9.0, 0, 1)
        sink = smoothstep(0, 1, sink)
        gross = smoothstep(T_GROSS, T_GROSS + 6.0, t)
        lvl = 0.16 * (1 - sink) + 0.045 * sink - 0.012 * gross
        lvl = lvl * (0.9 + 0.1 * slow(t))
        # the strings' trembling figures, faint, until the air
        tr = 0.025 * (1 - smoothstep(T_AIR - 2.0, T_AIR, t)) * np.maximum(tremble(t), 0)
        fr = light(NIGHT, (lvl + tr) * (1 - sink * 0.5)) + light(BED, 0.06 * sink)
        # the bass's voice in No. 10: a deep amber glow at the back of the porch, fading with the light
        j = int(np.searchsorted(V_ON, t, side='right')) - 1
        if 0 <= j and t < T_AIR - 0.05:
            n = VOICE[j]
            a = t - n[0]
            on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.4)
            g = np.exp(-(off / 0.45) ** 2) * front
            fr += light(AMBER, (0.5 - 0.25 * gross) * on * smoothstep(0, 0.1, a) * g)
        # the air: one dim point, wandering with the tune
        if t >= T_AIR - 0.5:
            k = int(np.searchsorted(L_ON, t, side='right')) - 1
            k = max(k, 0)
            a = t - L_ON[k]
            c = pos[k] if k == 0 else pos[k - 1] + (pos[k] - pos[k - 1]) * smoothstep(0.0, 0.22, a)
            shrink = 1.0
            for tw in DARK_WORDS:
                if tw >= T_AIR and 0 <= t - tw < 2.5:
                    shrink = min(shrink, 0.55 + 0.45 * smoothstep(0.3, 2.5, t - tw))
            seen = smoothstep(T_LIGHT1, T_LIGHT2 + 1.5, t)
            if seen > 0:                                          # it turns toward the light
                c = c + (mid - c) * 0.6 * seen
            w = 12.0 * shrink
            bright = (0.3 + 0.15 * np.exp(-a / 0.15)) * shrink * smoothstep(T_AIR - 0.5, T_AIR + 0.3, t)
            fr += light(AMBER, bright * np.exp(-((d - c) / w) ** 2))
        # the great light: a glow in the middle of Porch Front on the first "light", all of it on the second
        if t >= T_LIGHT1 - 0.2:
            a1 = smoothstep(T_LIGHT1 - 0.2, T_LIGHT1 + 1.2, t)
            a2 = smoothstep(T_LIGHT2 - 0.1, T_LIGHT2 + 0.8, t)
            r = 0.25 * a1 + 0.85 * a2
            inside = smoothstep(r + 0.12, r - 0.12, off) * front
            core = np.exp(-(off / max(0.15, r)) ** 2)
            fr += light(GLORY, (0.4 * a1 + 0.5 * a2) * inside * (0.85 + 0.15 * core))
            fr += light(GOLD, 0.3 * a2 * np.exp(-max(0.0, t - T_LIGHT2) / 1.2) * front)
            dist = np.where(runs, np.minimum(np.abs(d - pf0), np.abs(d - pf1)), 1e9)
            fr += light(GLORY, 0.3 * a2 * np.exp(-dist / 70.0) * runs)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them; the bass's line on cellos with a bassoon, from the porch; a harpsichord
    continuo for the recitative."""
    o = Orchestra(M, level=3.8)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (8 if t < T_AIR else 2)
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.12), vel - 4, pan[p], 0.42)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel - 4, pan[p], 0.45)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 8, pan[p], 0.36)
    for t, dd, m, v, h, _ in VOICE:
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('cellos', m, t, max(dd, 0.16), v + 10, 0.0, 0.6)
        o.play('bassoons', m, t, max(dd, 0.16), v - 2, 0.0, 0.32)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(90, v - 8)), min(dd, 0.4)) for t, dd, m, v, h, _ in PART['Bassi']
             if t < T_AIR]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.4, 0.0)
    # the great light: a soft cymbal swell into it and a held organ-like glow of strings
    o.hit('cymbal swell', T_LIGHT2 - 1.6, 60, gain=0.12, pan=0.0)
