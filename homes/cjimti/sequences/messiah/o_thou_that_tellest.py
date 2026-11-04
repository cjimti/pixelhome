"""O Thou That Tellest: the alto's rose light tells its tidings, the house brightens on every "arise", and the chorus joins.

"Behold, a virgin shall conceive": the alto's soft rose-violet voice at the back of the porch, alone in a quiet night
house, and a small light gathering in the middle of Porch Front as she sings. On "Emmanuel" it grows, and on "God with
us" it reaches out over the porch to the wings, the people.

Then the air, a gentle lilt in six-eight: the whole house sways in slow warm waves rolling out from the porch, two to
a bar, the alto's rose voice breathing on Porch Front, "O thou that tellest good tidings to Zion", and the strings'
answer warming the wings. "Arise, shine, for thy light is come": on every "arise" a wave of bright gold-white rises
from the porch over the whole house, and the house stays brighter after it, a step at a time; "shine" glitters, and
"thy light is come" spreads to the ends of the wings.

The chorus joins in white-gold, the whole house's colour: the sopranos on the porch, then the basses lighting Left
and the tenors Right; their "arise, arise" flares the whole house twice, and "the glory of the Lord is risen upon
thee" fills it with warm gold to the last chord.

The music is Handel's own: Messiah No. 8 whole, and from No. 9 the voice's first "O thou that tellest good tidings to
Zion" with the strings' answer, "Arise, shine, for thy light is come" with its three "arise"s, the chorus's entry and
its "arise, arise," and its "glory of the Lord is risen upon thee.", transcribed from Prout's full score (Novello,
1902) into o_thou_that_tellest.musicxml (No. 9 numbered on from No. 8: its bar n is bar 10 + n) and timed by
scripts/score_excerpt.py at Prout's tempo. Handel's strings and voices: the alto's line on violas and a clarinet, the
chorus on strings with oboes and a bassoon doubling and an organ under it, a harpsichord continuo for the recitative
and the air.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.ring import Orchestra, excerpt

CODE = 'MS07'
TITLE = 'O Thou That Tellest'
KIND = 'show'
DESCRIPTION = ("The alto's rose light tells good tidings in a gentle lilt; on every \"arise, shine\" the house brightens "
               "another step, and the chorus joins in white-gold.")
VOICEOVER = 'Arise, shine, for thy light is come.'

EX = excerpt(__file__)
BAR = {int(m): t for m, t in EX['bars']}
END = EX['seconds']
HOLD = 3.0
D = round(END + HOLD, 2)
CHOIR = ('S', 'A', 'T', 'B')
PART = {p: sorted(n for n in EX['notes'] if n[5] == p) for p in ('Alto', 'Vn1', 'Vn2', 'Va', 'Bassi') + CHOIR}
ALTO = PART['Alto']
A_ON = np.array([n[0] for n in ALTO])
SEG = EX['segments']
T_AIR = SEG[1]['start']                     # No. 9
T_ARISE = SEG[2]['start']                   # "arise, shine"
T_CHORUS = SEG[3]['start']                  # the chorus's upbeat
T_TUTTI = SEG[4]['start']                   # "arise, arise"
T_GLORY = SEG[5]['start']                   # "glory of the Lord is risen upon thee"
T_EMMANUEL = BAR[4] + 0.875 * (BAR[5] - BAR[4])
T_GODWITH = BAR[6]
ARISES = [BAR[86], BAR[90], BAR[91], BAR[92]]                     # "-rise" in the air
TUTTI = [BAR[125], BAR[126]]                                      # the chorus's two
SHINE = [BAR[86] + 0.5 * (BAR[87] - BAR[86]), BAR[92] + 0.5 * (BAR[93] - BAR[92])]
COME = [BAR[87], BAR[93]]                                          # "thy light is come"
ECHO = BAR[25]                                                     # the strings' answer
DOTTED = (BAR[23] - BAR[22]) / 2                                   # a dotted crotchet, the lilt's beat
ENTRY = {'S': T_CHORUS, 'B': BAR[117] + (BAR[118] - BAR[117]) * 5 / 6, 'T': BAR[118] + (BAR[119] - BAR[118]) * 5 / 6}

ROSE = hexc('#c890d8')                      # the alto
NIGHT = hexc('#1a1838')
WARM = hexc('#ffc890')
LIGHT = hexc('#fff0d0')
GLORY = hexc('#fff2c8')                     # the chorus
GOLD = hexc('#ffb84a')


def onsets(part, t0=0.0, t1=1e9):
    return np.array([n[0] for n in PART[part] if t0 - 0.01 <= n[0] < t1])


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    side = seg == 'Side'
    left, right = seg == 'Left', seg == 'Right'
    wings = left | right
    front = seg == 'Porch Front'
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    pf = G.pd[G.seg['Porch Front']]
    mid, half = 0.5 * (float(pf.min()) + float(pf.max())), 0.5 * (float(pf.max()) - float(pf.min()))
    off = np.abs(d - mid) / half
    far = np.abs(d - mid) / max(mid - float(G.pd[G.seg['Left']].min()), float(G.pd[G.seg['Right']].max()) - mid)
    glit = Flicker(rng, G.N, 2.0, 6.0)
    slow = Flicker(rng, G.N, 0.1, 0.3)
    v1 = onsets('Vn1', T_AIR, T_CHORUS)
    choir_on = {p: onsets(p) for p in CHOIR}
    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        if t < T_AIR:
            # ---- No. 8: a quiet night house, the alto's rose voice at the back of the porch ----
            fr += light(NIGHT, (0.2 + 0.02 * slow(t)) * np.where(side, 0.7, 1.0)) + light(ROSE, 0.1 * wings)
            j = int(np.searchsorted(A_ON, t, side='right')) - 1
            if j >= 0:
                n = ALTO[j]
                a = t - n[0]
                on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.4)
                fr += light(ROSE, (0.3 + 0.2 * smoothstep(0, 0.1, a)) * on * np.exp(-(off / 0.7) ** 2) * front)
            # the promise: a small light gathering in the middle of Porch Front, growing on "Emmanuel"
            grow = 0.12 + 0.4 * smoothstep(1.0, T_EMMANUEL, t) + 0.3 * smoothstep(T_EMMANUEL, T_GODWITH, t)
            fr += light(WARM, (0.25 + 0.35 * grow) * np.exp(-(off / max(0.1, 0.35 * grow)) ** 2) * front
                        * smoothstep(0.5, 3.0, t))
            # "God with us": it reaches out over the porch to the wings
            if t >= T_GODWITH - 0.1:
                r = smoothstep(T_GODWITH - 0.1, T_AIR, t)
                fr += light(WARM, 0.4 * smoothstep(r * 1.05 + 0.05, r * 1.05 - 0.15, far) * (1 - side))
        else:
            # ---- No. 9: the lilt, slow warm waves rolling out from the porch two to a bar ----
            u = (t - T_AIR) / DOTTED
            wave = 0.5 + 0.5 * np.cos(2 * np.pi * (u - 1.4 * far))
            # how bright the house is: a step up on every "arise", the chorus brighter still
            k = sum(1 for ta in ARISES if t >= ta)
            step = sum(smoothstep(ta - 0.25, ta + 0.6, t) for ta in ARISES)
            base = 0.22 + 0.09 * step
            chorus = smoothstep(T_CHORUS - 0.2, T_CHORUS + 0.6, t)
            col = (1 - chorus) * ((1 - 0.1 * step) * ROSE + 0.1 * step * GOLD) + chorus * GLORY
            col = (1 - chorus) * np.clip(col, 0, 1) + chorus * GLORY
            lvl = (base + 0.1 * wave + 0.02 * slow(t)) * (1 - chorus) + chorus * (0.2 + 0.06 * wave)
            fr += light(col, lvl * np.where(side, 0.6, 1.0))
            if t < T_CHORUS:
                # the alto's voice, breathing on Porch Front
                j = int(np.searchsorted(A_ON, t, side='right')) - 1
                if j >= 0 and ALTO[j][0] >= T_AIR - 0.01:
                    n = ALTO[j]
                    a = t - n[0]
                    on = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.35)
                    g = np.exp(-(off / (0.6 + 0.04 * k)) ** 2) * front
                    fr += light(ROSE, (0.32 + 0.25 * smoothstep(0, 0.1, a)) * on * g)
                    fr += light(LIGHT, 0.1 * on * g * np.exp(-a / 0.25))
                # the strings' figures warm the wings, a glint a note
                i = int(np.searchsorted(v1, t, side='right')) - 1
                if i >= 0:
                    a = t - v1[i]
                    amt = 0.24 if ECHO <= t < BAR[26] or BAR[88] <= t < BAR[89] else 0.1
                    fr += light(WARM, amt * np.exp(-a / 0.2) * wings)
            # every "arise": a wave of bright gold-white rising from the porch over the whole house
            for ta in ARISES + TUTTI:
                a = t - (ta - 0.25)
                if 0 <= a < 2.5:
                    r = a / 0.7
                    front_edge = smoothstep(r + 0.05, r - 0.25, far)
                    crest = np.exp(-((far - r) / 0.12) ** 2)
                    fade = np.exp(-max(0.0, a - 0.8) / 1.0)
                    big = 1.25 if ta in TUTTI else 1.0
                    fr += light(LIGHT, (0.45 * front_edge + 0.35 * crest) * big * fade * (1 - 0.4 * side))
                    fr += light(GOLD, 0.25 * big * front_edge * fade * np.exp(-a / 0.4))
            # "shine": a glitter
            for ts in SHINE:
                if 0 <= t - ts < 1.4:
                    e = smoothstep(0, 0.1, t - ts) * np.exp(-(t - ts) / 0.5)
                    fr += light(LIGHT, 0.25 * e * np.maximum(glit(t), 0) * (1 - side))
            # "thy light is come": the light spreads to the ends of the wings
            for tc in COME:
                if 0 <= t - tc < 3.0:
                    a = t - tc
                    reach = smoothstep(0.2, 1.0, far) * smoothstep(0, 1.2, a) * np.exp(-max(0.0, a - 1.5) / 0.8)
                    fr += light(WARM, 0.22 * reach * (1 - side))
            # the chorus: sopranos on the porch, basses on Left, tenors on Right, each from its entry
            if t >= T_CHORUS - 0.05 and t < T_GLORY:
                places = {'S': porch, 'B': left, 'T': right, 'A': porch}
                for p in ('S', 'B', 'T'):
                    if t < ENTRY[p] - 0.02:
                        continue
                    on_ = choir_on[p]
                    j = int(np.searchsorted(on_, t, side='right')) - 1
                    if j < 0:
                        continue
                    a = t - on_[j]
                    lit = smoothstep(ENTRY[p] - 0.02, ENTRY[p] + 0.25, t)
                    fr += light(GLORY, (0.48 + 0.22 * np.exp(-a / 0.2)) * lit * places[p])
            # "the glory of the Lord is risen upon thee": warm gold filling the house to the last chord
            if t >= T_GLORY - 0.3:
                g = smoothstep(T_GLORY - 0.3, BAR[147], t)
                last = smoothstep(BAR[148] - 0.05, BAR[148] + 0.3, t)
                settle = smoothstep(END, D, t)
                lvl = (0.35 + 0.2 * g + 0.15 * last - 0.12 * settle) * (0.95 + 0.05 * wave)
                fr = fr * (1 - 0.6 * g) + light((1 - g) * GLORY + g * GOLD, lvl * np.where(side, 0.75, 1.0))
                fr += light(LIGHT, 0.25 * last * np.exp(-max(0.0, t - BAR[148]) / 0.8) * np.exp(-(off / 0.8) ** 2)
                            * front)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Strings as Handel scored them, first violins left to basses right; the alto on violas and a clarinet from the
    porch; the chorus on strings with oboes and a bassoon doubling and an organ under it, sopranos and altos from the
    porch, basses from Left and tenors from Right as on the house; a harpsichord continuo for the recitative and the
    air; a soft cymbal swell into each "arise"."""
    o = Orchestra(M, level=2.7)
    pan = {'Vn1': -0.45, 'Vn2': -0.15, 'Va': 0.15, 'Bassi': 0.4}
    for p in ('Vn1', 'Vn2', 'Va', 'Bassi'):
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            vel = v - (4 if dd < 0.2 else 0)
            if p in ('Vn1', 'Vn2'):
                o.play('violins', m, t, max(dd, 0.12), vel - (4 if p == 'Vn1' else 6), pan[p], 0.42)
            elif p == 'Va':
                o.play('violas', m, t, max(dd, 0.12), vel - 4, pan[p], 0.42)
            else:
                o.play('cellos', m if m >= 36 else m + 12, t, max(dd, 0.15), vel - 2, pan[p], 0.5)
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.2), vel - 10, pan[p], 0.32)
    for t, dd, m, v, h, _ in ALTO:                                      # the alto, from the porch
        o.play('violas', m, t, max(dd, 0.14), v + 10, 0.05, 0.6)
        o.play('clarinets', m, t, max(dd, 0.14), v - 4, 0.05, 0.3)
    choir = {'S': ([('violins', 0, 0, 0.32), ('oboes', 0, -8, 0.2)], -0.05),
             'A': ([('violins', 0, -4, 0.24), ('violas', 0, -2, 0.25)], 0.05),
             'T': ([('violas', 0, 0, 0.3), ('bassoons', 0, -8, 0.17)], 0.55),
             'B': ([('cellos', 0, 0, 0.34), ('bassoons', 0, -6, 0.22)], -0.55)}
    for p in CHOIR:
        secs, pp = choir[p]
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            for sec, tr, dv, g in secs:
                o.play(sec, m + tr, t, max(dd * 0.95, 0.12), v + 4 + dv, pp, g)
    # the organ under the chorus (the VSCO2 pipe organ, as in Elijah's "Your Light Break Forth")
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, _Voice, _fade_out, _load

    class Pipes(_Voice):
        """The VSCO2 pipe organ: samples are numbered, every third key."""

        def __init__(self, pattern, first):
            self.zones = {}
            for path in sorted(glob.glob(os.path.join(VSCO, pattern))):
                self.zones[first + int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', path).group(1))] = path
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.3):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]
            idx = np.arange(int((dur + release) * SR)) * 2 ** ((n - k) / 12)
            idx = idx[idx < a.shape[1] - 1]
            res = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            return _fade_out(res * (vel / 127) ** 1.3, dur, release)

    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.06, reverb=0.45)
    M.bus('pedal', gain=0.09, reverb=0.35)
    for p in CHOIR:
        for t, dd, m, v, h, _ in PART[p]:
            dd = dd + HOLD if abs(t + dd - END) < 0.02 else dd
            if p == 'B':
                M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
            else:
                M.add('organ', man.play(m, v, dd), t - 0.03, 1.0, choir[p][1] * 0.5)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m + 12 if m < 40 else m, int(min(90, v - 8)), min(dd, 0.4)) for t, dd, m, v, h, _ in PART['Bassi']
             if t < T_CHORUS]
    # the recitative's chords over the held bass: D, D, A7 over the pedal, then E7, A, and D, E, A
    chords = [(0.0, (62, 66, 69)), (BAR[2], (62, 66, 69)), (BAR[3], (61, 64, 67)), (BAR[4], (62, 66, 69)),
              (BAR[4] + 1.5, (62, 64, 68)), (BAR[5], (61, 64, 69)), (BAR[6], (62, 66, 69)), (BAR[6] + 1.5, (64, 68, 71)),
              (BAR[6] + 2.25, (61, 64, 69))]
    for tc, ms in chords:
        notes += [(tc + 0.02 * q, m, 60, 1.4) for q, m in enumerate(ms)]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.36, 0.0)
    for ta in ARISES + TUTTI:
        o.hit('cymbal swell', ta - 1.4, 56, gain=0.09, pan=0.0)
