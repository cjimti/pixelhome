"""There Were Shepherds: night fields on the wings, the angel's silver rising up the porch, and the glory on the fields.

Night. Left and Right are the fields, a dark green under a blue night sky, and on each a handful of shepherds'
lanterns glow and sway: they come up one by one as the soprano begins, "There were shepherds abiding in the field",
and keep watch over their flocks by night. The soprano narrates from Porch Front, the far light, in silver, every
syllable a soft glow there.

"And lo, the angel of the Lord came upon them": the strings' rising figures, four semiquavers to a beat, each beat a
silver streak that climbs Porch Left and Porch Right from the front corners to the back of the porch in four steps,
one per note. Porch Front gathers the silver beat by beat until the angel stands there, bright. "And the glory of the
Lord shone round about them": white-gold pours out of the porch, down its sides and out across the fields from the
inside corners to the free ends, and the lanterns are lost in it. "And they were sore afraid": the glory on the fields
trembles and shrinks back, and the strings' two forte chords jolt the fields twice before the silence.

"And the angel said unto them": the silver on Porch Front again, steady now, and on "Fear not" the fields calm and
their lanterns return. "Good tidings of great joy" spreads the silver down the porch sides; "which shall be to all
people": the two forte chords light the porch and the fields, then the whole house. "For unto you is born this day,
in the city of David": quiet again, and a small gold light kindles in the middle of Porch Front, where the star
stands over the porch; it grows through "a Saviour", and on "which is Christ the Lord" and the closing chords it
fills the porch with warm gold and lights the fields with it, and the scene holds there.

The music is Handel's own: Messiah No. 14, both recitatives ("There were shepherds" and the accompanied "And lo, the
angel of the Lord"), and No. 15, "And the angel said unto them", complete, transcribed from Prout's full score
(Novello, 1902) into there_were_shepherds.musicxml (numbered on through the three) and timed by
scripts/score_excerpt.py, the accompagnato at Prout's Andante, the seccos at crotchet 80. Strings as Handel scored
them, with the string chords Prout gives for the seccos and a harpsichord continuo; the soprano's line on a flute
with an oboe. A soft cymbal swell rises into the glory.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS11'
TITLE = 'There Were Shepherds'
KIND = 'show'
DESCRIPTION = ("Shepherds' lanterns in the night fields on the wings; the angel's silver climbs the porch with the "
               "strings' rising figures, the glory of the Lord pours over the fields, and the angel says: fear not.")
VOICEOVER = 'There were shepherds abiding in the field, keeping watch over their flock by night.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 3.0
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Soprano', 'Vn1', 'Vn2', 'Va', 'Bassi')}
SOP = PART['Soprano']
S_ON = np.array([n[0] for n in SOP])
SING = EX['singing']


def sung(word):
    """When the first phrase containing word starts."""
    return next(p[0] for p in SING if word in p[3])


def word_at(phrase_word, k):
    """Onset of the k-th note of the phrase containing phrase_word."""
    t0 = sung(phrase_word)
    return [n[0] for n in SOP if n[0] >= t0 - 0.01][k]


T_LO = BAR[5]                               # "And lo": the strings' figures
BEAT_LO = (BAR[6] - BAR[5]) / 4
FIGS = [BAR[5] + k * BEAT_LO for k in range(24)]                 # each beat's figure, bars 5-10
TOPS = [max(n[2] for n in PART['Vn1'] if f - 0.01 <= n[0] < f + BEAT_LO - 0.01) for f in FIGS]
T_GLORY = word_at('glory', 2)               # "glo-"
T_ABOUT = BAR[10]                           # "shone round about them" done: the strings settle
T_AFRAID = word_at('afraid', 0)             # "and they were sore afraid"
T_JOLT = [BAR[11], BAR[11] + BEAT_LO]       # the two forte chords
T_ANGEL = BAR[12]                           # No. 15
T_FEAR = sung('Fear')
T_TIDINGS = sung('tidings')
T_PEOPLE = [BAR[16] + 2 * (BAR[17] - BAR[16]) / 4, BAR[16] + 3 * (BAR[17] - BAR[16]) / 4]   # "all people" chords
T_BORN = BAR[17]
T_SAVIOUR = BAR[19]
T_CHRIST = BAR[20]
T_LORD = [BAR[20] + 2 * (END - BAR[20]) / 4, BAR[20] + 3 * (END - BAR[20]) / 4]       # the closing chords

NIGHT = hexc('#0b1a4a')
FIELD = hexc('#123a26')                     # the fields at night
LANTERN = hexc('#ffa838')
SILVER = hexc('#e6f0ff')                    # the soprano, the angel
GLORY = hexc('#fff2c8')
GOLD = hexc('#ffd040')


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    fields = np.isin(seg, ['Left', 'Right'])
    front = seg == 'Porch Front'
    runs = np.isin(seg, ['Porch Left', 'Porch Right'])
    pl, pr = G.pd[G.seg['Porch Left']], G.pd[G.seg['Porch Right']]
    pf = G.pd[G.seg['Porch Front']]
    pf0, pf1 = float(pf.min()), float(pf.max())
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    off = np.abs(d - mid) / half                       # 0 at the middle of Porch Front, 1 at its corners
    # up the porch: 0 at the front corners of the porch runs, 1 at the back (Porch Front's corners)
    up = np.zeros(G.N)
    up[seg == 'Porch Left'] = (d[seg == 'Porch Left'] - pl.min()) / (pl.max() - pl.min())
    up[seg == 'Porch Right'] = (pr.max() - d[seg == 'Porch Right']) / (pr.max() - pr.min())
    # out over the fields: 0 at the inside corners (beside the porch), 1 at the far ends
    l0, l1 = float(G.pd[G.seg['Left']].min()), float(G.pd[G.seg['Left']].max())
    r0, r1 = float(G.pd[G.seg['Right']].min()), float(G.pd[G.seg['Right']].max())
    away = np.zeros(G.N)
    away[seg == 'Left'] = (l1 - d[seg == 'Left']) / (l1 - l0)
    away[seg == 'Right'] = (d[seg == 'Right'] - r0) / (r1 - r0)
    # the shepherds' lanterns: five on each field, lit one by one through the first phrase
    lan = [l0 + (l1 - l0) * u for u in (0.12, 0.3, 0.47, 0.66, 0.85)] + \
          [r0 + (r1 - r0) * u for u in (0.1, 0.27, 0.45, 0.62, 0.8)]
    lan = np.array(lan) + rng.uniform(-10, 10, len(lan))
    order = rng.permutation(len(lan))
    lit_at = np.empty(len(lan))
    lit_at[order] = 0.4 + np.arange(len(lan)) * 0.75
    sway = rng.uniform(0, 2 * np.pi, len(lan))
    rate = rng.uniform(0.25, 0.5, len(lan))
    flick = Flicker(rng, len(lan), 0.8, 3.0)
    slow = Flicker(rng, G.N, 0.1, 0.35)
    shake = Flicker(rng, G.N, 4.0, 10.0)
    figs = np.array(FIGS)
    for f in range(F):
        t = f * DT
        # the night: sky on Side and the porch, the fields dark green
        n = 0.09 * (0.9 + 0.1 * slow(t))
        fr = light(NIGHT, n * (side + runs + front) * 1.0) + light(FIELD, 0.17 * fields * (0.9 + 0.1 * slow(t)))
        # the glory on the fields: pours out from the porch, trembles on "sore afraid", jolts, and goes
        g_out = smoothstep(T_GLORY + 0.3, T_GLORY + 3.0, t)
        g_back = smoothstep(T_AFRAID, T_JOLT[0], t)
        front_g = g_out * 1.15 - away
        field_glory = smoothstep(0.0, 0.25, front_g) * (1 - 0.65 * g_back) * fields
        jolt = sum(np.exp(-max(0.0, t - tj) / 0.3) * (t >= tj) for tj in T_JOLT)
        fade = 1 - smoothstep(T_JOLT[1] + 0.3, T_ANGEL - 0.2, t)
        field_glory = field_glory * fade
        trem = 1 + 0.25 * g_back * shake(t)
        fr += light(GLORY, 0.55 * field_glory * trem) + light(GLORY, 0.55 * jolt * fade * fields)
        # the lanterns: lost in the glory, back on "Fear not"
        lan_lvl = 1 - 0.9 * g_out * (1 - smoothstep(T_FEAR - 0.3, T_FEAR + 2.0, t))
        fl = flick(t)
        c = lan + 7.0 * np.sin(rate * t * 2 * np.pi + sway)
        on = smoothstep(lit_at, lit_at + 0.8, t) * (0.85 + 0.15 * fl) * lan_lvl
        lan_i = np.zeros(G.N)
        for k in range(len(lan)):
            lan_i = np.maximum(lan_i, on[k] * np.exp(-((d - c[k]) / 7.0) ** 2))
        fr += light(LANTERN, 0.5 * lan_i * fields)
        # the angel: silver gathering on Porch Front through "And lo"
        angel = 0.0
        if t >= T_LO:
            k = int(np.searchsorted(figs, t, side='right'))
            angel = 0.55 * min(1.0, k / len(figs)) * (1 - 0.4 * smoothstep(T_ABOUT, T_ANGEL, t))
        angel += 0.32 * smoothstep(T_ANGEL - 0.5, T_ANGEL + 0.5, t) * (1 - smoothstep(T_BORN - 0.5, T_BORN + 1.0, t) * 0.5)
        fr += light(SILVER, angel * front * (0.8 + 0.2 * np.exp(-(off / 0.6) ** 2)))
        # the strings' rising figures: each beat a silver streak up the porch sides, a step a semiquaver
        if T_LO - 0.01 <= t < BAR[11]:
            k = int(np.searchsorted(figs, t, side='right')) - 1
            if k >= 0:
                a = (t - figs[k]) / BEAT_LO
                step = min(3, int(a * 4))
                head = (step + smoothstep(0, 0.35, a * 4 - step)) / 3.6
                strength = 0.55 + 0.25 * (TOPS[k] - 81) / 3
                tail = np.clip(1 - (head - up) / 0.35, 0, 1) * (up <= head + 0.05)
                glow = np.exp(-((up - head) / 0.08) ** 2)
                fr += light(SILVER, strength * np.maximum(0.7 * tail, glow) * runs * np.exp(-a * 0.4))
        # the glory pours out of the porch on "glory"
        if t >= T_GLORY - 0.2:
            p = smoothstep(T_GLORY - 0.2, T_GLORY + 1.5, t) * (1 - 0.6 * smoothstep(T_ABOUT, T_ANGEL, t)
                                                               - 0.4 * smoothstep(T_ANGEL, T_FEAR + 1.0, t))
            fr += light(GLORY, 0.62 * p * (front + runs * smoothstep(0.0, 0.3, p * 1.4 - (1 - up))))
        # the soprano's syllables: a soft silver glow at the middle of Porch Front
        j = int(np.searchsorted(S_ON, t, side='right')) - 1
        if j >= 0:
            nn = SOP[j]
            a = t - nn[0]
            env = (1.0 if a < nn[1] else np.exp(-(a - nn[1]) / 0.3)) * smoothstep(0, 0.05, a)
            w = 0.35 + 0.1 * (nn[2] - 72) / 8
            fr += light(SILVER, 0.3 * env * np.exp(-(off / max(0.15, w)) ** 2) * front)
        # "good tidings of great joy": the silver spreads down the porch sides
        if t >= T_TIDINGS:
            s = smoothstep(T_TIDINGS, T_PEOPLE[0], t) * (1 - 0.7 * smoothstep(T_BORN - 0.3, T_BORN + 1.5, t))
            fr += light(SILVER, 0.32 * s * runs * smoothstep(0.0, 0.4, up - (1 - s)))
        # "which shall be to all people": porch and fields, then the whole house
        for i, tp in enumerate(T_PEOPLE):
            if t >= tp:
                e = np.exp(-(t - tp) / 0.55)
                reach = (runs + front + fields) if i == 0 else np.ones(G.N)
                fr += light(GLORY, (0.5 + 0.12 * i) * e * reach)
        # "for unto you is born this day": a small gold light in the middle of Porch Front, the star's place
        if t >= T_BORN:
            grow = smoothstep(T_BORN, T_SAVIOUR + 1.0, t)
            full = smoothstep(T_LORD[0] - 0.1, T_LORD[1] + 0.8, t)
            r = 0.12 + 0.18 * grow + 0.9 * full
            core = np.exp(-(off / r) ** 2)
            twinkle = 0.92 + 0.08 * np.sin(t * 5.3)
            fr += light(GOLD, (0.3 + 0.25 * grow + 0.25 * full) * core * front * twinkle)
            fr += light(GOLD, 0.45 * full * runs * smoothstep(0.0, 1.0, up))
            fr += light(GOLD, 0.42 * full * fields * (1 - 0.4 * away))
            for tl in T_LORD:
                if t >= tl:
                    fr += light(GLORY, 0.4 * np.exp(-(t - tl) / 0.45) * (front + runs + fields))
        if t > END:
            fr = fr * (1 - 0.15 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them, first violins left to the bassi right, a harpsichord continuo in the
    recitatives; the soprano on a flute with an oboe, from the porch. A soft cymbal swell into the glory."""
    o = Orchestra(M, level=4.1)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    lo = lambda t: T_LO - 0.01 <= t < BAR[12] - 0.01
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            if lo(t):
                vel = v + 6 if p in ('Vn1', 'Vn2') else v
            else:
                vel = v - (14 if dd > 1.0 else 0)                  # the seccos' held chords sit under the voice
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.1), vel - 6, pan[p], 0.4)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.1), vel - 4, pan[p], 0.42)
            else:
                o.play('cellos', m, t, max(dd, 0.12), vel, pan[p], 0.48)
                if not lo(t) or t >= BAR[11] - 0.01:
                    o.play('basses', m if m < 48 else m - 12, t, max(dd, 0.2), vel - 10, pan[p], 0.3)
    for t, dd, m, v, h, _ in SOP:                                     # the soprano, from the porch
        dd = dd + 0.6 if dd < 0.6 and any(abs(t + dd - p[1]) < 0.02 for p in SING) else dd
        o.play('flutes', m, t, max(dd, 0.18), v + 10, 0.0, 0.62)
        o.play('oboes', m, t, max(dd, 0.18), v - 6, 0.0, 0.26)
    hp = M.synth('Keys/Digi Harpsi')
    notes = []
    for t, dd, m, v, h, _ in PART['Bassi']:                            # the continuo: bass and the strings' chord
        if lo(t):
            continue
        notes.append((t, m + 12 if m < 40 else m, 84, min(dd, 0.6)))
        for p in ('Vn1', 'Vn2', 'Va'):
            for n in PART[p]:
                if n[0] <= t + 0.01 < n[0] + n[1]:
                    notes.append((t + 0.03, n[2], 70, 0.5))
    for p in ('Vn1', 'Vn2', 'Va'):                                     # and the chord's changes over a held bass
        for n in PART[p]:
            if not lo(n[0]) and not any(abs(n[0] - b[0]) < 0.02 for b in PART['Bassi']):
                notes.append((n[0] + 0.03, n[2], 66, 0.5))
    M.add('harp', hp.render(sorted(notes), D + 2.0), 0.0, 0.4, 0.0)
    o.hit('cymbal swell', T_GLORY - 1.7, 64, gain=0.14, pan=0.0)
