"""Rejoice Greatly: the soprano's coloratura as quick bright silver runs along the house, the most joyful motion in the set.

The house is lit warm, a low gold that rises whenever the strings play forte and sinks back when they drop to piano,
and the violins' semiquavers throw small gold sparkles across the wings and the porch, one for every note. The
ritornello's last bar opens it, forte.

The soprano is silver. Her plain notes, "Rejoice, rejoice", "O daughter of Zion", glow at the middle of Porch Front, the
far light; but every time the words break into a run, the silver leaves the porch and races along the roofline, a
comet with a tail, one step for every semiquaver, its head bobbing a little up and down the line with the tune. The
runs take turns: one from the left end of Left toward the right, the next from the free end of Right back toward the
left, and the longest, "rejoice" over four bars, crosses the whole house from Left to the end of Right. Side, the house's
flank, keeps the warm light and nothing starts there.

Then the return: one more run, and "and shout, shout, shout, shout": four bursts of silver, on Left, on Right, on Porch
Front and on the whole porch, each opening out from its middle. "Rejoice greatly": a last run and a bow. The closing
ritornello brings the whole house up to warm gold for its cadence, drops to the porch for the piano echo, and lands on
the last chord in full gold, held.

The music is Handel's own: Messiah No. 18, the 4/4 Allegro, from the ritornello's last bar through the soprano's
first statement to the strings' answer after the first long "rejoice", then from the return's "rejoice" through "and
shout ... rejoice greatly", and the closing ritornello's cadence, transcribed from Prout's full score (Novello, 1902)
into rejoice_greatly.musicxml and timed by scripts/score_excerpt.py at Prout's Allegro. Strings as Handel scored
them, with a harpsichord continuo; the soprano's line on a flute with an oboe.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS13'
TITLE = 'Rejoice Greatly'
KIND = 'show'
DESCRIPTION = ("The soprano's coloratura as quick silver runs racing along the roofline, the violins throwing gold "
               "sparkles, four bursts of silver on \"shout\", and the house landing in full gold.")
VOICEOVER = 'Rejoice greatly, O daughter of Zion: behold, thy King cometh unto thee.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 2.5
D = round(END + HOLD, 2)
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Soprano', 'Vn1', 'Vn2', 'Va', 'Bassi')}
SOP = PART['Soprano']
SEG = EX['segments']
T_RETURN = SEG[1]['start']
T_CODA = SEG[2]['start']
T_ECHO = BAR[106] + 0.375 * (BAR[107] - BAR[106])                 # bar 106: the piano echo
T_FORTE2 = BAR[107] + 0.5 * (BAR[108] - BAR[107])
T_LAST = BAR[108]
SHOUTS = [p[0] for p in EX['singing'] if 'shout' in p[3]]


def runs():
    """The soprano's melismas: unbroken runs of six or more short notes, as lists of notes."""
    out, cur = [], []
    for n in SOP:
        if n[1] <= 0.2 and (not cur or n[0] - (cur[-1][0] + cur[-1][1]) < 0.05):
            cur.append(n)
        else:
            if len(cur) >= 6:
                out.append(cur)
            cur = [n] if n[1] <= 0.2 else []
    if len(cur) >= 6:
        out.append(cur)
    return out


RUNS = runs()
IN_RUN = {tuple(n) for r in RUNS for n in r}
PLAIN = [n for n in SOP if tuple(n) not in IN_RUN]
P_ON = np.array([n[0] for n in PLAIN])

WARM = hexc('#ffb848')
GOLD = hexc('#ffd040')
SILVER = hexc('#e6f0ff')                    # the soprano
WHITE = hexc('#ffffff')
NIGHT = hexc('#0e1a48')


def loudness():
    """The strings' dynamic through the excerpt, 0 (piano) .. 1 (forte), from their velocities, smoothed."""
    F = nframes(D)
    v = np.full(F, np.nan)
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, d, m, vel, h, _ in PART[p]:
            a, b = int(t / DT), int(min(t + max(d, 0.25), D) / DT)
            v[a:b] = np.fmax(v[a:b], np.clip((vel - 55) / 41, 0, 1))
    # hold the last level through rests, then smooth over a quarter second
    last = 0.6
    for i in range(F):
        if np.isnan(v[i]):
            v[i] = last
        last = v[i]
    k = np.ones(10) / 10
    return np.convolve(v, k, mode='same')


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    front = seg == 'Porch Front'
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    left, right = seg == 'Left', seg == 'Right'
    pf = G.pd[G.seg['Porch Front']]
    mid, half = 0.5 * (pf.min() + pf.max()), 0.5 * (pf.max() - pf.min())
    off = np.abs(d - mid) / half
    a0, a1 = float(G.pd[G.seg['Left']].min()) + 15, float(G.pd[G.seg['Right']].max()) - 10
    lm = float(G.pd[G.seg['Left']].mean())
    rm = float(G.pd[G.seg['Right']].mean())
    loud = loudness()
    shimmer = Flicker(rng, G.N, 0.2, 0.8)
    # each run: where it starts and which way it goes; the head steps once per note and bobs with the pitch
    plans = []
    for k, r in enumerate(RUNS):
        n = len(r)
        travel = min(a1 - a0, n * 62.0)
        if n >= 40:
            s, e = a0, a1
        elif k % 2 == 0:
            s = a0 + rng.uniform(0, 120)
            e = s + travel
        else:
            s = a1 - rng.uniform(0, 120)
            e = s - travel
        on = np.array([x[0] for x in r])
        pitch = np.array([x[2] for x in r], float)
        bob = (pitch - pitch.mean()) * 9.0 * np.sign(e - s)
        plans.append((on, r[-1][0] + r[-1][1], s, e, bob, pitch))
    # the violins' sparkles: one per semiquaver, on the wings and the porch
    v1 = [n for n in PART['Vn1']]
    sp_t = np.array([n[0] for n in v1])
    allowed = np.where(~side)[0]
    sp_at = rng.choice(allowed, len(v1))
    sp_vel = np.array([n[3] for n in v1], float)
    for f in range(F):
        t = f * DT
        L = loud[f]
        # the warm bed, rising with the strings' forte; a night blue under it
        bed = (0.2 + 0.2 * L) * (0.92 + 0.08 * shimmer(t))
        fr = light(NIGHT, 0.08 * np.ones(G.N)) + light(WARM, bed * (1 - 0.25 * front))
        # the sparkles
        i1 = int(np.searchsorted(sp_t, t, side='right'))
        i0 = int(np.searchsorted(sp_t, t - 0.3))
        if i1 > i0:
            amp = np.zeros(G.N)
            age = t - sp_t[i0:i1]
            e = np.exp(-age / 0.12) * (0.7 + 0.4 * (sp_vel[i0:i1] - 50) / 50)
            np.maximum.at(amp, sp_at[i0:i1], e)
            amp = np.maximum(amp, 0.8 * np.maximum(np.roll(amp, 1), np.roll(amp, -1)))
            amp = np.maximum(amp, 0.5 * np.maximum(np.roll(amp, 2), np.roll(amp, -2)))
            fr += light(GOLD, amp)
        # the runs: a silver comet racing the roofline
        for on, t1, s, e, bob, pitch in plans:
            if on[0] - 0.05 <= t < t1 + 0.6:
                k = int(np.searchsorted(on, t, side='right')) - 1
                k = max(k, 0)
                n = len(on)
                a = smoothstep(0, 0.07, t - on[k])
                u = min(1.0, (k + a) / n)
                head = s + (e - s) * u + bob[k] * (1 if t < t1 else 0)
                dirn = np.sign(e - s)
                behind = (head - d) * dirn                    # distance behind the head, along its way
                tail = np.exp(-np.clip(behind, 0, None) / 140.0) * (behind > -6) * (behind < 500)
                core = np.exp(-(behind / 24.0) ** 2)
                fade = 1 - smoothstep(t1, t1 + 0.6, t)
                bright = (0.85 + 0.2 * (pitch[k] - 72) / 8) * fade
                fr += light(SILVER, bright * (0.6 * tail + 0.55 * core) * (~side))
        # the plain notes: silver at the middle of Porch Front
        j = int(np.searchsorted(P_ON, t, side='right')) - 1
        if j >= 0:
            nn = PLAIN[j]
            a = t - nn[0]
            env = (1.0 if a < nn[1] else np.exp(-(a - nn[1]) / 0.25)) * smoothstep(0, 0.04, a)
            w = 0.3 + 0.35 * np.clip((nn[2] - 65) / 14, 0, 1)
            fr += light(SILVER, 0.65 * env * np.exp(-(off / w) ** 2) * front)
            fr += light(SILVER, 0.25 * env * porch * (1 - front) * 0.6)
        # shout: four bursts of silver
        for i, ts in enumerate(SHOUTS):
            if ts - 0.02 <= t < ts + 1.0:
                a = t - ts
                c, reach = [(lm, 200.0), (rm, 240.0), (mid, half), (mid, 900.0)][i]
                r = reach * smoothstep(0, 0.35, a)
                ring = np.exp(-((np.abs(d - c) - r) / 30.0) ** 2) + (np.abs(d - c) < r) * 0.45
                fr += light(WHITE if i == 3 else SILVER, 0.85 * np.exp(-a / 0.45) * ring)
        # the closing ritornello: the whole house in warm gold, the porch alone for the echo, then all of it again
        if t >= T_CODA - 0.1:
            up = smoothstep(T_CODA - 0.1, T_CODA + 0.6, t)
            echo = smoothstep(T_ECHO - 0.1, T_ECHO + 0.3, t) * (1 - smoothstep(T_FORTE2 - 0.1, T_FORTE2 + 0.2, t))
            house = up * (1 - 0.8 * echo)
            fr += light(GOLD, 0.42 * house * np.ones(G.N)) + light(GOLD, 0.3 * echo * porch)
            if t >= T_LAST:
                a = t - T_LAST
                fr += light(GOLD, (0.25 + 0.3 * np.exp(-a / 0.5)) * np.ones(G.N))
                fr += light(WHITE, 0.3 * np.exp(-a / 0.35) * front)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them, first violins left to the bassi right, with a harpsichord continuo; the
    soprano on a flute with an oboe, from the porch."""
    o = Orchestra(M, level=3.4)
    pan = {'Vn1': -0.45, 'Vn2': -0.2, 'Va': 0.2, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.1), v - (6 if p == 'Vn1' else 9), pan[p], 0.4)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.1), v - 4, pan[p], 0.42)
            else:
                o.play('cellos', m, t, max(dd, 0.12), v - 2, pan[p], 0.48)
                o.play('basses', m if m < 48 else m - 12, t, max(dd, 0.16), v - 10, pan[p], 0.3)
    for t, dd, m, v, h, _ in SOP:                                     # the soprano, from the porch
        dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
        o.play('flutes', m, t, max(dd, 0.12), v + 12, 0.0, 0.62)
        o.play('oboes', m, t, max(dd, 0.12), v - 4, 0.0, 0.26)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(96, v - 6)), min(dd, 0.3)) for t, dd, m, v, h, _ in PART['Bassi']]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.4, 0.0)
