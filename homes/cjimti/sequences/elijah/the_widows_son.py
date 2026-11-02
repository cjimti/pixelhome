"""The Widow's Son: a widow's child stops breathing, Elijah prays three times, and on the third the child lives.

Elijah's amber stands where the last scene left him, at the front corner of Side, still in the drought's dust. Out
on Left are the widow's rose light and, beside her, her son: one small warm point, breathing slowly. "Help me, man
of God, my son is sick!": her rose flares with every word over the orchestra's trembling, and with every line the
son's point breathes slower and dimmer; "there is no breath left in him", and it goes out.

Elijah comes onto Left and prays. "Give me thy son! Turn unto her, O Lord, my God": with every note he sings, a
thread of amber reaches from him along the roofline toward the dark point, and falls back short when he stops.
"Lord, my God, let the spirit of this child return": it reaches farther, and the point stirs once, and stays dark.
Then the third prayer, fortissimo, "O let the spirit of this child return, that he again may live!": the amber
runs all the way, and on "live!" it touches him, and the point lights again, warm, and stays. The orchestra swells
and the warmth blooms around the two of them, and the widow's rose opens: "The Lord hath heard thy prayer, the soul
of my son reviveth."

The music is Mendelssohn's own: four passages of No. 8, transcribed from the Novello octavo vocal score into
the_widows_son.musicxml and timed by scripts/score_excerpt.py at the marked tempos. The widow is played on oboe,
Elijah on cellos and horns, and the son is heard only once he lives again, on the harp.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt

CODE = 'EL05'
TITLE = "The Widow's Son"
KIND = 'show'
DESCRIPTION = ("A widow's son stops breathing: one small warm light goes out. Elijah prays three times, his amber "
               "reaching farther each time, and on the third the light comes back.")
VOICEOVER = 'Lord my God, let the spirit of this child return, that he again may live.'

EX = excerpt(__file__)                      # No. 8 bars 13-25, 67-71, 86-92, 111-121
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
WIDOW = [n for n in EX['notes'] if n[5] == 'Widow']
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_GONE = BAR[25] + 0.6                      # the last "no breath left in him": the point is out
PRAYERS = [(BAR[67], BAR[86] - 0.01, 0.45), (BAR[86], BAR[111] - 0.01, 0.75), (BAR[111], BAR[115], 1.0)]
T_LIVE = BAR[115]                           # "live!"
T_HEARD = BAR[117]                          # "The Lord hath heard thy prayer"
WI_ON = np.array([n[0] for n in WIDOW])
EL_ON = np.array([n[0] for n in ELIJAH])

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
ROSE = hexc('#e07a8a')                      # the widow
SON = hexc('#ffd8a0')                       # her son


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    """Where Elijah starts and stands, the son and the widow, along the path."""
    s0, s1 = span(G, 'Side')
    l0, l1 = span(G, 'Left')
    start = l0 + 12                         # where the last scene left him, just round the corner onto Left
    stand = l0 + 0.2 * (l1 - l0)
    son = l0 + 0.58 * (l1 - l0)
    widow = l0 + 0.8 * (l1 - l0)
    return start, stand, son, widow


def elijah_at(G, t):
    start, stand, son, widow = places(G)
    return start + (stand - start) * smoothstep(BAR[25] - 4, BAR[67] + 1.0, t)


def reach(t):
    """How far the amber thread reaches toward the son, 0..1: growing with each note of a prayer, falling back after."""
    r = 0.0
    for a, b, most in PRAYERS:
        if t < a:
            break
        notes = EL_ON[(EL_ON >= a - 0.01) & (EL_ON < b)]
        sung = notes[notes <= t]
        grow = most * len(sung) / max(len(notes), 1)
        if len(sung):
            grow = most * (len(sung) - 1 + min((t - sung[-1]) / 0.35, 1.0)) / max(len(notes), 1)
        if t < b:
            r = grow
        elif most < 1.0:
            r = most * np.exp(-(t - b) / 1.2)
        else:
            r = 1.0
    return r


def son_level(t):
    """The son's light: breathing and failing through the plea, out, a stir in the second prayer, alive at "live!"."""
    if t < T_GONE:
        fail = 1 - smoothstep(0, T_GONE, t)
        breath = 0.5 + 0.5 * np.sin(2 * np.pi * t / (2.2 + 2.5 * (1 - fail)))
        return (0.25 + 0.45 * fail) * (0.6 + 0.4 * breath) * (1 - smoothstep(T_GONE - 1.5, T_GONE, t))
    a, b, _ = PRAYERS[1]
    stir = 0.25 * np.exp(-((t - (b - 1.5)) / 0.4) ** 2)
    if t < T_LIVE:
        return stir
    alive = smoothstep(T_LIVE, T_LIVE + 0.6, t)
    return alive * (0.75 + 0.15 * np.sin(2 * np.pi * (t - T_LIVE) / 3.0))


def render(G, seed=5):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    left = G.seg_of == 'Left'
    start, stand, son, widow = places(G)

    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    tremble = Flicker(rng, G.N, 7.0, 14.0)

    for f in range(F):
        t = f * DT
        fr = light(DUST, 0.28 * np.ones(G.N))
        warm = 0.4 + 0.25 * smoothstep(T_LIVE + 1.0, T_HEARD + 2.0, t)
        fr += light(CANDLE, cand * people * warm * (0.75 + 0.25 * flick(t)))
        e = elijah_at(G, t)

        # the widow: rose, flaring with each word, trembling with the orchestra in her plea, opening at the end
        j = int(np.searchsorted(WI_ON, t, side='right')) - 1
        voice = float(np.exp(-(t - WI_ON[j]) / 0.4)) if j >= 0 else 0.0
        plea = 1 - smoothstep(BAR[25] + 1, BAR[67], t)
        joy = smoothstep(T_LIVE + 1.5, T_HEARD + 1.0, t)
        lvl = 0.5 + 0.2 * plea + 0.5 * voice + 0.4 * joy
        blob = np.exp(-((d - widow) / (20 + 14 * joy)) ** 2)
        fr += light(ROSE, lvl * blob * (1 + 0.3 * plea * (tremble(t) - 0.5)))
        fr += light(ROSE, (0.28 + 0.3 * joy) * np.exp(-((d - widow) / 70) ** 2))
        if t < BAR[67]:                                   # her cries rippling out from her
            for k in range(max(j - 3, 0), j + 1):
                a = t - WI_ON[k]
                if 0 <= a < 1.6:
                    ring = np.exp(-((np.abs(d - widow) - 25 - 110 * a) / 12) ** 2)
                    fr += light(ROSE, 0.55 * np.exp(-a / 0.6) * ring)

        # Elijah
        on = 1.0
        j = int(np.searchsorted(EL_ON, t, side='right')) - 1
        sing = float(np.exp(-(t - EL_ON[j]) / 0.5)) if j >= 0 and t > PRAYERS[0][0] else 0.0
        fr += light(AMBER, on * ((0.7 + 0.25 * sing) * np.exp(-((d - e) / 16) ** 2)
                                + 0.15 * np.exp(-((d - e) / 45) ** 2)))
        fr += light(CORE, on * (0.45 + 0.35 * sing) * np.exp(-((d - e) / 5) ** 2))

        # the prayers: a thread of amber reaching toward the son
        r = reach(t)
        if r > 0.005:
            tip = e + (son - e) * r
            thread = ((d > e) & (d < tip)) * (0.25 + 0.2 * sing)
            fr += light(AMBER, thread + (0.55 + 0.35 * sing) * np.exp(-((d - tip) / 8) ** 2))

        # the son
        s = son_level(t)
        fr += light(SON, 1.1 * s * np.exp(-((d - son) / 6) ** 2))
        if t >= T_LIVE:                                   # the warmth blooming out from him
            a = t - T_LIVE
            ring = np.exp(-((np.abs(d - son) - 90 * min(a / 3.0, 1.0)) / 18) ** 2) * np.exp(-a / 2.5)
            fr += light(SON, 0.8 * ring * left)
            fr += light(SON, 0.3 * smoothstep(T_LIVE, T_HEARD, t) * np.exp(-((d - 0.5 * (son + widow)) / 90) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The widow on oboe, Elijah on cellos and horns, the orchestra on strings (trembling in her plea, brass and
    timpani in the fortissimo prayer), and the son on the harp once he lives."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    start, stand, son, widow = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.4)
    T_P1, T_P3 = PRAYERS[0][0], PRAYERS[2][0]

    def role(t, d, m, v, hand):
        if t < T_P1 - 0.01:                           # the plea: trembling strings
            if hand == 0:
                if d >= 0.5:
                    return [('violins trem' if m >= 60 else 'violas trem', 0, -6, 0.5)]
                return [('violins' if m >= 62 else 'violas', 0, -6, 0.45)]
            return [('cellos', 0, -4, 0.55), ('basses', -12 if m >= 40 else 0, -8, 0.4)]
        if T_P3 - 0.01 <= t < T_LIVE - 0.01:          # the fortissimo prayer
            if hand == 0:
                return [('violins' if m >= 62 else 'violas', 0, -2, 0.55),
                        ('trombones', -12 if m > 64 else 0, -6, 0.4)]
            return [('cellos', 0, 0, 0.6), ('basses', -12 if m >= 40 else 0, -4, 0.5), ('tuba', 0, -8, 0.35)]
        if hand == 0:
            return [('violins' if m >= 62 else 'violas', 0, -8, 0.42)]
        return [('cellos', 0, -6, 0.5), ('basses', -12 if m >= 40 else 0, -10, 0.35)]
    o.tutti(ORCH, role=role, pan=lambda t, m: 0.5 * pan_at(son))

    for t, d, m, v, h, who in WIDOW:
        o.play('oboes', m, t, d, v + 2, pan_at(widow), 0.6)
        o.play('violins', m, t, d, v - 12, pan_at(widow), 0.25)
    for t, d, m, v, h, who in ELIJAH:
        e = elijah_at(G, t)
        o.play('cellos', m, t, d, v + 2, pan_at(e), 0.6)
        o.play('horns', m, t, d, v - 6, pan_at(e), 0.4)

    # the son lives: a harp, arpeggiating the orchestra's chords from "live!" on
    for t, d, m, v, h, who in ORCH:
        if t >= T_LIVE - 0.01 and h == 0:
            o.play('harp', m, t + 0.04 * (m % 5), max(d, 0.6), 84, pan_at(son), 0.45)
    for k, m in enumerate((60, 64, 67, 72, 76, 79, 84)):
        o.play('harp', m, T_LIVE + 0.07 * k, 1.5, 92, pan_at(son), 0.5)
    for t in (BAR[111], BAR[112], BAR[113]):
        o.hit('timpani', t, 110, pitch=-5, gain=0.35)
    o.hit('timpani roll', BAR[114], 100, pitch=-5, gain=0.3)
    o.hit('cymbal swell', BAR[116] - 1.0, 90, gain=0.25, pan=pan_at(son))
    o.hit('triangle', T_LIVE, 80, gain=0.2, pan=pan_at(son))
