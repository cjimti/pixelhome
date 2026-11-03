"""Father of Heav'n: the Feast of Dedication. The Temple is clean, and its light comes back, slowly, from the middle.

The scene opens where We Never Will Bow Down ended: the people's blue and white bands over the whole house, the Temple
on Porch Front dark and empty but for the lights' glow. Through the ritornello the house quiets to a low, steady
blue and white and breathes with the strings' phrases, slow and wide.

Then the priest's prayer, "Father of Heav'n!", first with the voice alone. The voice is a soft sky blue at the back of
the porch runs, either side of the Temple, swelling with each note. On the first "Heav'n!" a single point of olive-oil
gold appears in the middle of Porch Front, and with every line of the prayer it widens, a little at a time, along the
Temple: "from thy eternal throne", "look with an eye of blessing down", "while we prepare with holy rites"; on "to
solemnize the Feast of Lights" it reaches both ends of Porch Front, the flame tips flickering in it, and on the held
last note it brightens once and stays. Nothing moves fast; it is the quietest light in the set.

The music is Handel's own: Judas Maccabaeus No. 53, the air's ritornello from its fifth bar and the first period of
the air to "the Feast of Lights", transcribed from the Novello vocal score into father_of_heaven.musicxml and timed by
scripts/score_excerpt.py at the marked tempo, Andante larghetto. The voice is played on a flute with violas under its
long notes; the accompaniment on soft strings, its bass on cellos and basses with a harpsichord continuo.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes, smoothstep, keys, Flicker
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM11'
TITLE = "Father of Heav'n"
KIND = 'show'
DESCRIPTION = ("The Feast of Dedication: the Temple on the porch is clean, and to the priest's prayer its olive-oil light "
               "comes back, slowly, from the middle outward, until it fills Porch Front.")

EX = excerpt(__file__)                      # No. 53 bars 5-18 of the air, numbered 1-14
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICE = [n for n in EX['notes'] if n[5] == 'Voice']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
T_FA = VOICE[0][0]                          # "Fa-ther of Heav'n!", the voice alone
T_LIGHTS = BAR[14]                          # "Lights.", held
# how far the Temple light has reached from the middle of Porch Front (0..1 of its half-length), line by line
REACH = [(0.0, 0.0), (T_FA, 0.0), (BAR[4] + 0.5, 0.06), (BAR[6] + 2.8, 0.14), (BAR[8] + 3.0, 0.3),
         (BAR[10] + 2.5, 0.5), (BAR[12] + 2.0, 0.78), (BAR[13] + 4.0, 1.0), (D, 1.0)]
PHRASES = [BAR[b] for b in (1, 2, 3, 5)] + [BAR[9], BAR[11]]      # the strings' phrases the house breathes with

BLUE = hexc('#1e5bd8')                      # the people, as JM10 left them
WHITE = hexc('#f2f6ff')
SKY = hexc('#5aa0ff')                       # the priest's voice
OIL = hexc('#ffb33a')                       # the Temple light
TIP = hexc('#fff1c0')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    seg = G.seg_of
    temple = seg == 'Porch Front'
    house = ~temple
    pf0, pf1 = span(G, 'Porch Front')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    mid, half = 0.5 * (pf0 + pf1), 0.5 * (pf1 - pf0)
    off = np.abs(d - mid) / half                                # 0 in the middle of the Temple, 1 at its ends
    band = (np.sin(2 * np.pi * d / 110.0) > 0.25).astype(float)
    # the voice: near the back of each porch run, beside the Temple
    back = np.zeros(G.N)
    lmask, rmask = seg == 'Porch Left', seg == 'Porch Right'
    back[lmask] = np.exp(-((pl1 - d[lmask]) / 28.0) ** 2)
    back[rmask] = np.exp(-((d[rmask] - pr0) / 28.0) ** 2)
    glow = Glow(G, seed)
    shimmer = Flicker(rng, G.N, 0.15, 0.5)
    flame = Flicker(rng, G.N, 1.5, 5.0)
    v_on = np.array([n[0] for n in VOICE])
    for f in range(F):
        t = f * DT
        # the people: from JM10's last level down to a low, steady blue and white, breathing with the phrases
        breath = 0.0
        for tp in PHRASES:
            a = t - tp
            if 0 <= a < 6.0:
                breath = max(breath, np.sin(np.pi * a / 6.0) ** 2)
        lvl = keys(t, [(0.0, 0.64), (6.0, 0.32), (D - 3.0, 0.3), (D, 0.34)]) + 0.06 * breath
        lvl = lvl * (0.95 + 0.05 * shimmer(t))
        fr = light(BLUE, lvl * band * house) + light(WHITE, lvl * (1 - band) * house)
        fr += glow.frame(t, 0.8)
        # the priest's voice, swelling with each note
        j = int(np.searchsorted(v_on, t, side='right')) - 1
        if j >= 0:
            n = VOICE[j]
            a = t - n[0]
            held = 1.0 if a < n[1] else np.exp(-(a - n[1]) / 0.6)
            sw = smoothstep(0.0, 0.12, a) * (0.55 + 0.45 * np.exp(-a / 0.8))
            fr += light(SKY, 0.85 * held * sw * back)
        # the Temple light: a point in the middle, widening line by line to the ends of Porch Front
        r = keys(t, REACH)
        if r > 0:
            inside = smoothstep(r + 0.06, r - 0.06, off) * temple
            core = np.exp(-(off / max(r, 0.02)) ** 2 * 2.0) * temple
            lvl_t = 0.3 + 0.35 * r + 0.25 * smoothstep(T_LIGHTS, T_LIGHTS + 0.8, t) * (1 - 0.4 * smoothstep(D - 1.5, D, t))
            fr += light(OIL, lvl_t * inside * (0.92 + 0.08 * flame(t)) + 0.25 * core * smoothstep(0, 0.1, r))
            tips = np.maximum(flame(t), 0) * smoothstep(0.75, 1.0, r)
            fr += light(TIP, 0.35 * tips * inside)
        a = t - T_FA
        if 0 <= a < 2.5:                                    # the first point, kindled on "Fa-"
            fr += light(TIP, 0.5 * smoothstep(0.0, 1.0, a) * (1 - smoothstep(1.5, 2.5, a))
                        * np.exp(-((d - mid) / 4.0) ** 2) * temple)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The voice on a flute from the middle of the porch, violas under its long notes; the accompaniment on soft
    strings, the bass on cellos and basses, and a harpsichord continuo playing the reduction."""
    o = Orchestra(M, level=4.1)
    for t, dd, m, v, h, who in VOICE:
        o.play('flutes', m, t, dd, v + 18, 0.0, 0.7)
        if dd >= 0.7:
            o.play('violas', m - 12, t, dd, v - 2, 0.0, 0.25)
    for t, dd, m, v, h, who in ORCH:
        if h == 0:
            o.play('violins', m, t, max(dd, 0.3), v - 6, -0.25 if m >= 65 else 0.25, 0.32)
        else:
            o.play('cellos', m, t, max(dd, 0.3), v - 2, 0.1, 0.45)
            if m < 52:
                o.play('basses', m + 12 if m < 36 else m, t, max(dd, 0.3), v - 8, 0.1, 0.35)
    hp = M.synth('Keys/Digi Harpsi')
    notes = [(t, m, int(min(110, v + 10)), min(dd, 0.3)) for t, dd, m, v, h, who in ORCH]
    M.add('harp', hp.render(notes, D + 2.0), 0.0, 0.4, 0.0)
    o.play('harp', 72, T_LIGHTS + 0.05, 2.5, 60, 0.0, 0.4)
    o.play('harp', 79, T_LIGHTS + 0.2, 2.5, 55, 0.0, 0.35)
