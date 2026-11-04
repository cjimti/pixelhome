"""He Shall Feed His Flock: slow warm waves roll in toward the porch, and the lights gather there like a flock.

"Then shall the eyes of the blind be opened": the house is dim and warm, and the alto speaks in soft rose-violet from
the middle of Porch Front. On "opened" a row of small lights opens across the wings and the porch sides, each one
widening from a point like an eye opening; on "unstopped" they ring once. "Then shall the lame man leap as an hart":
a light bounds along the house in three leaps, from Left round the porch to Right. "And the tongue of the dumb shall
sing": the strings' two forte chords bloom the whole house warm.

Then the siciliano. The house breathes in slow, wide waves of warm rose and amber that roll in from both ends toward
Porch Front, one crest every half bar, rocking with the 12/8 lilt. Scattered over Left and Right are the flock, a dozen
soft warm-white lights; while the alto sings "He shall feed His flock like a shepherd, and He shall gather the lambs
with His arm", they drift in toward the porch on every long note of the tune, step by step, and by "with His arm" they
are gathered on the porch sides. The alto's own light, rose, glows at the middle of Porch Front.

The soprano takes the tune a fourth higher, "Come unto Him, all ye that labour", in silver: her light opens out from the
porch farther with each "come", the waves turn silver-gold, and the flock settles on Porch Front around her. "And He
will give you rest": the waves smooth out into one even warm light, and the last chord holds, the flock at rest on the
porch.

The music is Handel's own: Messiah No. 19, the alto recitative complete, and from No. 20 the alto's first statement
from its upbeat to "with His arm" and the soprano's "Come unto Him" from its upbeat to "He will give you rest" and the
next downbeat, transcribed from Prout's full score (Novello, 1902) into he_shall_feed_his_flock.musicxml (No. 20
numbered on from No. 19) and timed by scripts/score_excerpt.py, the Larghetto at Prout's quaver 112 and the
recitative at crotchet 88. Strings as Handel scored them, with the string chords Prout gives for the recitative and a
harpsichord continuo; the alto's line on violas with a clarinet, the soprano's on a flute with an oboe.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS14'
TITLE = 'He Shall Feed His Flock'
KIND = 'show'
DESCRIPTION = ("Slow, wide, warm waves roll in toward the porch to the siciliano, and the house's lights gather there "
               "like a flock: first to the alto's rose, then around the soprano's silver, \"Come unto Him\".")
VOICEOVER = 'He shall feed His flock like a shepherd, and He will give you rest.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Alto', 'Soprano', 'Vn1', 'Vn2', 'Va', 'Bassi')}
ALTO, SOP = PART['Alto'], PART['Soprano']
SEG = EX['segments']
T_AIR = SEG[1]['start']                     # No. 20, the alto's upbeat
T_COME = SEG[2]['start']                    # the soprano's upbeat
BEAT = (BAR[15] - BAR[14]) / 4              # a dotted crotchet
SING = EX['singing']


def first(word, after=0.0):
    return next(p[0] for p in SING if word in p[3] and p[0] >= after)


T_OPENED = [n[0] for n in ALTO if n[0] < T_AIR][14]            # "o-pened"
T_UNSTOP = [n[0] for n in ALTO if BAR[4] + 1.0 < n[0] < BAR[5]][1]      # "un-stop-ped"
T_LEAP = [n[0] for n in ALTO if BAR[5] <= n[0] < BAR[6]][4:7]   # "leap as an"
T_SING = [BAR[8], BAR[8] + (BAR[8] - BAR[7]) / 4]             # the forte chords
ALTO_LONG = [n[0] for n in ALTO if n[0] >= T_AIR - 0.01 and n[1] >= BEAT * 0.6]   # the tune's long notes: the flock steps
COMES = [n[0] for n in SOP if n[2] >= 77 and n[1] >= BEAT * 0.6] or [T_COME]
T_REST = first('give you rest', T_COME)

ROSE = hexc('#c890d8')                      # the alto
SILVER = hexc('#e6f0ff')                    # the soprano
AMBER = hexc('#ffa860')
WARM = hexc('#ffc890')
SHEEP = hexc('#fff0dc')
DUSK = hexc('#1a1838')


def steps(t, onsets, n_total):
    """0..1: the share of onsets passed by t, each step eased over most of a beat."""
    if not len(onsets) or t <= onsets[0]:
        return 0.0
    k = int(np.searchsorted(onsets, t, side='right'))
    a = smoothstep(0.0, BEAT * 0.8, t - onsets[k - 1])
    return min(1.0, (k - 1 + a) / n_total)


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    front = seg == 'Porch Front'
    runs = np.isin(seg, ['Porch Left', 'Porch Right'])
    wings = np.isin(seg, ['Left', 'Right'])
    pf = G.pd[G.seg['Porch Front']]
    pf0, pf1 = float(pf.min()), float(pf.max())
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    off = np.abs(d - mid) / half
    to_porch = np.clip(np.maximum(pf0 - d, d - pf1), 0, None)          # distance along the line to Porch Front
    l0, r1 = float(G.pd[G.seg['Left']].min()), float(G.pd[G.seg['Right']].max())
    breathe = Flicker(rng, G.N, 0.08, 0.25)
    # the eyes that open: eight points on the wings and the porch sides
    eyes = np.concatenate([rng.uniform(l0 + 30, pf0 - 40, 4), rng.uniform(pf1 + 40, r1 - 30, 4)])
    # the flock: twelve lights on Left and Right that walk in to the porch sides, then onto Porch Front
    n = 12
    start = np.concatenate([np.sort(rng.uniform(l0 + 20, pf0 - 430, n // 2)),
                            np.sort(rng.uniform(pf1 + 380, r1 - 20, n // 2))])
    mid_t = np.concatenate([pf0 - np.linspace(360, 30, n // 2), pf1 + np.linspace(30, 330, n // 2)])
    end_t = mid + np.concatenate([np.linspace(-0.9, -0.15, n // 2), np.linspace(0.15, 0.9, n // 2)]) * half
    bob = rng.uniform(0, 2 * np.pi, n)
    a_long = np.array(ALTO_LONG)
    s_long = np.array([x[0] for x in SOP if x[1] >= BEAT * 0.6])
    a_on = np.array([x[0] for x in ALTO])
    s_on = np.array([x[0] for x in SOP])
    for f in range(F):
        t = f * DT
        air = smoothstep(T_AIR - 0.5, T_AIR + 1.5, t)
        rest = smoothstep(T_REST, T_REST + 3.5, t)
        silver = smoothstep(T_COME - 0.5, T_COME + 4.0, t)
        # the bed: dim dusk in the recitative; in the air, slow warm waves rolling in toward the porch
        fr = light(DUSK, 0.1 * np.ones(G.N))
        lilt = (t - T_AIR) / BEAT
        lilt = lilt + 0.18 * np.sin(2 * np.pi * lilt)                     # long-short, the siciliano's rock
        wave = 0.5 + 0.5 * np.cos(2 * np.pi * (to_porch / 520.0 + lilt / 2.0))
        wave = (1 - rest) * wave + rest * 0.6
        warm = (1 - silver)[..., None] * (0.55 * AMBER + 0.45 * ROSE) + silver * (0.5 * WARM + 0.5 * SILVER)
        lvl = air * (0.11 + 0.23 * wave) * (0.94 + 0.06 * breathe(t)) + 0.12 * (1 - air)
        lvl = lvl * (1 - 0.35 * side)
        fr += light(warm, lvl)
        if t < T_AIR + 1.0:
            # the eyes of the blind, opened
            if t >= T_OPENED - 0.1:
                o = smoothstep(T_OPENED - 0.1, T_OPENED + 1.6, t) * (1 - air)
                ring = 1 + 0.8 * np.exp(-max(0.0, t - T_UNSTOP) / 0.5) * (t >= T_UNSTOP)
                w = 3.0 + 12.0 * o
                e = np.max(np.exp(-((d[:, None] - eyes[None]) / w) ** 2), axis=1)
                fr += light(WARM, 0.4 * o * ring * e * (~side))
            # the lame man leaps as an hart: three bounds, Left, the porch, Right
            for i, tl in enumerate(T_LEAP):
                a = t - tl
                if 0 <= a < 0.9:
                    c = [l0 + 0.45 * (pf0 - l0), mid, pf1 + 0.55 * (r1 - pf1)][i]
                    hop = np.sin(np.pi * min(a / 0.5, 1.0))
                    fr += light(WARM, 0.85 * np.exp(-a / 0.5) * np.exp(-((d - c) / (20 + 60 * hop)) ** 2))
            # the tongue of the dumb shall sing: two warm blooms
            for tc in T_SING:
                if t >= tc:
                    fr += light(WARM, 0.55 * np.exp(-(t - tc) / 0.5) * np.ones(G.N))
            # the alto's syllables in the recitative: rose at the middle of Porch Front
            j = int(np.searchsorted(a_on, t, side='right')) - 1
            if j >= 0 and ALTO[j][0] < T_AIR - 0.1:
                nn = ALTO[j]
                a = t - nn[0]
                env = (1.0 if a < nn[1] else np.exp(-(a - nn[1]) / 0.3)) * smoothstep(0, 0.05, a)
                fr += light(ROSE, 0.42 * env * np.exp(-(off / 0.45) ** 2) * front)
        # the voices in the air: the alto's rose, then the soprano's silver, at the porch, opening out with "come"
        for part, on, col, t0, t1 in ((ALTO, a_on, ROSE, T_AIR - 0.1, T_COME), (SOP, s_on, SILVER, T_COME - 0.1, D)):
            if t0 <= t < t1 + 1.5:
                j = int(np.searchsorted(on, t, side='right')) - 1
                if j >= 0:
                    nn = part[j]
                    a = t - nn[0]
                    env = (1.0 if a < nn[1] else np.exp(-(a - nn[1]) / 0.6)) * smoothstep(0, 0.15, a)
                    env *= 1 - smoothstep(t1, t1 + 1.5, t)
                    reach = 0.5 + 0.25 * (nn[2] - (65 if part is ALTO else 70)) / 7
                    if part is SOP:
                        k = int(np.searchsorted(np.array(COMES), t, side='right'))
                        reach += 0.5 * min(k, 3) * (1 - 0.5 * rest)
                    g = np.exp(-(off / max(0.3, reach)) ** 2) * front + \
                        np.exp(-(to_porch / (90 + 260 * max(0.0, reach - 0.8))) ** 2) * runs * 0.6
                    fr += light(col, 0.5 * env * g)
        # the flock: in from the wings to the porch sides on the alto's long notes, onto Porch Front on the soprano's
        if t >= T_AIR - 1.0:
            g1 = steps(t, a_long, len(a_long))
            g2 = steps(t, s_long, len(s_long))
            pos = start + (mid_t - start) * smoothstep(0, 1, g1)
            pos = pos + (end_t - pos) * smoothstep(0, 1, g2)
            pos = pos + 4.0 * np.sin(2 * np.pi * t / (2 * BEAT) + bob)
            show = smoothstep(T_AIR - 1.0, T_AIR + 1.5, t)
            sheep = np.max(np.exp(-((d[:, None] - pos[None]) / 11.0) ** 2), axis=1)
            fr += light(SHEEP, (0.6 + 0.1 * rest) * show * sheep * (~side))
        if t > END:
            fr = fr * (1 - 0.12 * smoothstep(END, D, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them, first violins left to the bassi right, with a harpsichord continuo in the
    recitative; the alto on violas with a clarinet, the soprano on a flute with an oboe, from the porch."""
    o = Orchestra(M, level=3.8)
    pan = {'Vn1': -0.45, 'Vn2': -0.2, 'Va': 0.2, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (14 if t < T_AIR - 0.1 and dd > 1.0 else 2)
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.14), vel - 4, pan[p], 0.42)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.14), vel - 2, pan[p], 0.42)
            else:
                o.play('cellos', m, t, max(dd, 0.16), vel, pan[p], 0.5)
                o.play('basses', m if m < 48 else m - 12, t, max(dd, 0.2), vel - 10, pan[p], 0.3)
    for t, dd, m, v, h, _ in ALTO:                                    # the alto, from the porch
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('violas', m, t, max(dd, 0.18), v + 14, 0.0, 0.55)
        o.play('clarinets', m, t, max(dd, 0.18), v - 2, 0.0, 0.3)
    for t, dd, m, v, h, _ in SOP:                                     # the soprano, from the porch
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('flutes', m, t, max(dd, 0.18), v + 14, 0.0, 0.6)
        o.play('oboes', m, t, max(dd, 0.18), v - 2, 0.0, 0.24)
    hp = M.synth('Keys/Digi Harpsi')
    notes = []
    for t, dd, m, v, h, _ in PART['Bassi']:
        if t < T_AIR - 0.1:                                           # the recitative: bass and the strings' chord
            notes.append((t, m + 12 if m < 40 else m, 84, min(dd, 0.6)))
            for p in ('Vn1', 'Vn2', 'Va'):
                for nn in PART[p]:
                    if nn[0] <= t + 0.01 < nn[0] + nn[1]:
                        notes.append((t + 0.03, nn[2], 70, 0.5))
        else:
            notes.append((t, m + 12 if m < 40 else m, 66, min(dd, 0.5)))
    for p in ('Vn1', 'Vn2', 'Va'):
        for nn in PART[p]:
            if nn[0] < T_AIR - 0.1 and not any(abs(nn[0] - b[0]) < 0.02 for b in PART['Bassi']):
                notes.append((nn[0] + 0.03, nn[2], 66, 0.5))
    M.add('harp', hp.render(sorted(notes), D + 2.0), 0.0, 0.38, 0.0)
