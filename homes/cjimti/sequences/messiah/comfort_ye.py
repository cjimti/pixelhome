"""Comfort Ye: the tenor's warm white alone on Porch Front, each "comfort ye" opening outward, then the road lit.

The house waits in a soft dusk, Left and Right gently lit, and the strings' quiet repeated chords breathe through them.
Porch Front, the far light, holds only an ember. The tenor's voice is warm white on Porch Front, unhurried: each
"comfort ye" begins as a small light in the middle of the porch and opens slowly outward, wider each time, and the
strings' soft answering chords swell once on Left and Right. On the last "Comfort ye", sung alone and free while
the strings are silent, the light opens across the whole of Porch Front.

Then the recitative. "The voice of him that crieth in the wilderness": from the ends of Porch Front the light finds
the road, travelling down Porch Left and Porch Right toward the street a step with every syllable, and the strings'
chords pulse along it. "Prepare ye the way of the Lord": the road fills with light. "Make straight in the desert a
highway": a bright line runs the length of both roads, straight from the porch to the street. "For our God": the
porch and the road hold in warm white, Left and Right warm beside them.

The music is Handel's own: Messiah No. 2, the strings' opening and the tenor's first "Comfort ye" to the ad lib.
"Comfort ye" (bars 1-8), and the recitative from "The voice of him that crieth" to "for our God" (bars 30-37),
transcribed from Prout's full score (Novello, 1902) into comfort_ye.musicxml and timed by scripts/score_excerpt.py,
the Larghetto a little quicker than Prout's mark. Strings only, as Handel scored it; the tenor's line on violins and
an oboe, a harpsichord continuo in the recitative.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS02'
TITLE = 'Comfort Ye'
KIND = 'show'
DESCRIPTION = ("The tenor's warm white light alone on Porch Front, opening a little wider with each \"comfort ye\"; "
               "then \"the voice of him that crieth in the wilderness\", and the light finds the road.")
VOICEOVER = 'Comfort ye, comfort ye my people, saith your God.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.5                                  # the last chord rings
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Tenor', 'Vn1', 'Vn2', 'Va', 'Bassi')}
TEN = PART['Tenor']
T_ON = np.array([n[0] for n in TEN])
STRINGS = sorted({round(n[0], 3) for p in ('Vn1', 'Vn2', 'Va', 'Bassi') for n in PART[p]})
S_ON = np.array(STRINGS)
T_ADLIB = BAR[8]                            # "Comfort ye," ad lib., the strings silent
T_RECIT = BAR[30]
SING = EX['singing']
PHRASES = [(s[0], s[1]) for s in SING]
T_COMFORT = [BAR[4], TEN[[i for i, n in enumerate(TEN) if n[0] >= BAR[5]][0]][0], T_ADLIB]    # each "comfort ye"
T_VOICE = [s[0] for s in SING if s[3].startswith('The voice')][0]
T_PREPARE = [s[0] for s in SING if s[3].startswith('Prepare')][0] - 0.4      # its upbeat "Pre-" is in the bar before
T_STRAIGHT = [s[0] for s in SING if s[3].startswith('make straight')][0]
T_GOD = [s[0] for s in SING if s[3].startswith('for our God')][0]
FP = [BAR[4] + 0.5 * (BAR[5] - BAR[4]), BAR[7] + 0.5 * (BAR[8] - BAR[7])]   # the strings' soft answering chords

WARM = hexc('#fff0d8')                      # the tenor
DUSK = hexc('#1a2a5c')
AMBER = hexc('#ff9a48')


def render(G, seed=2):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    front = seg == 'Porch Front'
    wings = np.isin(seg, ['Left', 'Right'])
    side = seg == 'Side'
    roads = np.isin(seg, ['Porch Left', 'Porch Right'])
    pf = G.pd[G.seg['Porch Front']]
    pf0, pf1 = float(pf.min()), float(pf.max())
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    off = np.abs(d - mid)
    # the road: 0 at the porch's back corners, 1 at the street end of each porch run
    road = np.zeros(G.N)
    for nm in ('Porch Left', 'Porch Right'):
        idx = G.seg[nm]
        s = G.pd[idx]
        road[idx] = (s - s.min()) / (s.max() - s.min())
        if nm == 'Porch Left':
            road[idx] = 1 - road[idx]
    outward = np.zeros(G.N)                                     # Left and Right: 0 at the porch, 1 at the free ends
    for nm in ('Left', 'Right'):
        idx = G.seg[nm]
        s = G.pd[idx]
        outward[idx] = (s.max() - s) / (s.max() - s.min()) if nm == 'Left' else (s - s.min()) / (s.max() - s.min())
    recit_notes = np.array([n[0] for n in TEN if n[0] >= T_RECIT])
    to_prepare = recit_notes[recit_notes < T_PREPARE]
    breathe = Flicker(rng, G.N, 0.1, 0.35)
    for f in range(F):
        t = f * DT
        # the dusk: Left and Right gently lit, breathing with the strings' quiet chords
        i = int(np.searchsorted(S_ON, t, side='right')) - 1
        pulse = 0.07 * np.exp(-(t - S_ON[i]) / 0.25) if i >= 0 and t - S_ON[i] < 1.5 else 0.0
        alone = smoothstep(T_ADLIB - 0.3, T_ADLIB + 1.5, t) * (1 - smoothstep(T_RECIT - 0.6, T_RECIT, t))
        swell = sum(0.22 * np.exp(-max(0.0, t - tf) / 1.4) * smoothstep(tf - 0.1, tf + 0.1, t) for tf in FP)
        lw = (0.34 + pulse + swell) * (1 - 0.4 * alone) * (0.92 + 0.08 * breathe(t))
        ripple = np.zeros(G.N)
        for k in range(max(0, i - 3), i + 1):                   # each soft chord a ripple out along Left and Right
            a = t - S_ON[k]
            if 0 <= a < 2.0 and S_ON[k] < T_ADLIB:
                ripple += np.exp(-((outward - a / 1.6) / 0.12) ** 2) * np.exp(-a / 0.9)
        fr = light(DUSK, (0.16 + 0.06 * (1 - alone)) * (side | roads)) + light(DUSK, 0.6 * lw * wings)
        fr += light(AMBER, (lw + 0.12 * np.minimum(ripple, 1.5)) * wings)
        ember = 0.12 + 0.14 * smoothstep(0.0, BAR[4], t)
        fr += light(WARM, ember * np.exp(-(off / 40.0) ** 2) * front)              # the ember on Porch Front
        # the tenor: warm white on Porch Front, each "comfort ye" opening outward a little wider
        j = int(np.searchsorted(T_ON, t, side='right')) - 1
        if j >= 0:
            n = TEN[j]
            a = t - n[0]
            on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.6)
            if t < T_RECIT:
                k = max(i for i, tc in enumerate(T_COMFORT) if tc <= t + 0.01)
                widest = (0.45, 0.8, 1.15)[k] * half
                op = smoothstep(T_COMFORT[k], T_COMFORT[k] + 3.0, t)
                w = 25.0 + (widest - 25.0) * op
                g = smoothstep(w + 25.0, w - 25.0, off) * front
                lv = (0.58 + 0.12 * smoothstep(0, 0.12, a) + 0.08 * (n[2] - 52) / 12) * on
                fr += light(WARM, lv * g)
                if k == 2:                                          # alone: it spills down the porch runs
                    fr += light(WARM, 0.35 * lv * op * np.exp(-road / 0.15) * roads)
            else:
                lv = max(0.4 * smoothstep(T_RECIT, T_VOICE, t), (0.6 + 0.15 * np.exp(-a / 0.15)) * on)
                fr += light(WARM, lv * front)
        # the recitative: the light finds the road, a step down Porch Left and Porch Right with every syllable
        if t >= T_RECIT:
            k = int(np.searchsorted(to_prepare, t, side='right'))
            step = k / max(1, len(to_prepare))
            if k < len(to_prepare) and k > 0:
                step = (k - 1 + smoothstep(0, 0.25, t - to_prepare[k - 1])) / len(to_prepare)
            reach = 0.08 + 0.92 * step if t >= T_VOICE else 0.08 * smoothstep(T_RECIT, T_VOICE, t)
            fill = smoothstep(T_PREPARE, T_PREPARE + 2.5, t)
            along = smoothstep(reach + 0.05, reach - 0.05, road)
            head = np.exp(-((road - reach) / 0.05) ** 2) * (1 - fill)
            lv = (0.35 + 0.25 * fill) * along + 0.35 * head
            # "make straight in the desert a highway": a bright line runs the length of both roads
            if t >= T_STRAIGHT:
                u = (t - T_STRAIGHT) / 3.0
                lv = lv + 0.45 * np.exp(-((road - u) / 0.08) ** 2) * (u < 1.2)
                lv = lv + 0.15 * smoothstep(T_STRAIGHT, T_STRAIGHT + 3.0, t)
            # the strings' chords pulse along the road
            if i >= 0 and S_ON[i] >= T_RECIT - 0.01:
                lv = lv + 0.25 * np.exp(-(t - S_ON[i]) / 0.3) * along
            fr += light(WARM, lv * roads)
            # for our God: the porch, the road and the wings hold warm
            god = smoothstep(T_GOD, END, t)
            fr += light(WARM, 0.25 * god * front) + light(AMBER, 0.2 * god * wings)
        if t > END:
            fr = fr * (1 - 0.2 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The strings as Handel scored them, first violins left to basses right; the tenor on violins with an oboe, from
    the porch; a harpsichord continuo under the recitative's chords."""
    o = Orchestra(M, level=4.0)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (4 if dd < 0.2 else 0)
            if p == 'Vn1':
                o.play('violins', m, t, max(dd, 0.14), vel - 4, pan[p], 0.45)
            elif p == 'Vn2':
                o.play('violins', m, t, max(dd, 0.14), vel - 6, pan[p], 0.4)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.14), vel - 4, pan[p], 0.45)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel - 2, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 10, pan[p], 0.32)
    for t, dd, m, v, h, _ in TEN:                                       # the tenor's line, from the porch
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('violins', m + 12, t, max(dd, 0.16), v + 8, 0.0, 0.62)
        o.play('oboes', m + 12, t, max(dd, 0.16), v - 6, 0.0, 0.3)
        if dd >= 0.6:
            o.play('violas', m, t, dd, v - 10, 0.0, 0.25)
    # the continuo: in the recitative a chord with every string chord, from the parts sounding
    hp = M.synth('Keys/Digi Harpsi')
    notes = []
    for tb in S_ON[S_ON >= T_RECIT - 0.01]:
        ch = sorted({n[2] for p in ('Vn2', 'Va') for n in PART[p] if abs(n[0] - tb) < 0.02})
        bass = [n[2] for n in PART['Bassi'] if abs(n[0] - tb) < 0.02]
        dur = 1.2 if tb < END - 0.5 else HOLD + 0.8
        notes += [(tb + 0.02 * k, m, 70, dur) for k, m in enumerate(bass + ch)]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.45, 0.0)
