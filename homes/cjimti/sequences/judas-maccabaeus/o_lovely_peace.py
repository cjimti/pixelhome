"""O Lovely Peace: the war is over, and two voices sing of peace and plenty over a quiet countryside.

It opens where March, and Sing unto God (JM13) ended, the people's blue and white bands round the Temple's light, and
over the first bars that gives way to the land at peace (JM13_END, rebuilt from JM13's last frame: change both
together). The purple is long gone. The whole house is a soft pastoral light, ripe corn and green pasture, moving in
waves so wide and slow that it hardly seems to move at all. The ritornello warms it from the porch outward.

Then the duet. The Israelitish Woman sings first, "O lovely Peace, with Plenty crown'd": her white-silver light grows
softly over Left with each phrase she sings, and fades as she rests. The Israelitish Man answers from Right in sky
blue. Together, "O lovely, lovely Peace", their two lights come in along the porch runs toward the Temple. At the
Adagio, "And smile with wavy corn", everything slows and warms to the scene's warmest, and on "corn." it settles to a
steady warm gold over the house round the Temple's light, which is where Rejoice, O Judah (JM15) begins.

The music is Handel's own: No. 66, the duet's upbeat and first two bars of ritornello, the first voice's verse, the
second's, the first phrase they sing together, and the Adagio close, transcribed from the Novello vocal score into
o_lovely_peace.musicxml and timed by scripts/score_excerpt.py (Allegro at dotted crotchet 52, unhurried for a
pastoral, the Adagio at 30). The score names no voices; the Woman's line is played on an oboe and the Man's on a flute,
over soft strings and a harpsichord continuo; the ritornello's tune on violins with a flute, as the score marks.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, Flicker, hexc, light, nframes, smoothstep
from pixelhome.hanukkah import Glow
from pixelhome.ring import Orchestra, excerpt

CODE = 'JM14'
TITLE = 'O Lovely Peace'
KIND = 'show'
DESCRIPTION = ("The purple is long gone: soft pastoral light, ripe corn and green pasture, slow and wide, and two "
               "voices of peace, white-silver on Left and sky blue on Right, coming together at the Temple.")
VOICEOVER = 'The war is over. Two voices sing of peace, of flocks on the hills and corn in the fields.'

EX = excerpt(__file__)              # No. 66: upbeat and ritornello (1-3), the verses (6-22), together (23-28), Adagio
BAR = {int(m): t for m, t in EX['bars']}
D = round(EX['seconds'] + 1.5, 2)
NOTES = EX['notes']
WOMAN = [n for n in NOTES if n[5] == 'Woman']
MAN = [n for n in NOTES if n[5] == 'Man']
T_VERSE = BAR[7]                    # the Woman's "O lovely Peace"
T_TOGETHER = BAR[23]                # "O lovely, lovely Peace", the two together
T_ADAGIO = EX['segments'][2]['start']   # "And smile with wavy corn"
T_LAST = BAR[34]                    # "corn."

BLUE = hexc('#1e5bd8')
WHITE = hexc('#f2f6ff')
OIL = hexc('#ffb33a')
CORN = hexc('#ffc870')              # ripe corn
PASTURE = hexc('#8ccf5a')           # green pasture
SILVER = hexc('#e8f0ff')            # the Israelitish Woman
SKY = hexc('#5aa0ff')               # the Israelitish Man
WARM = hexc('#ffcf8a')              # where the scene settles
CARRY = 4.0                         # seconds JM13's last frame takes to give way


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def jm13_end(G):
    """March, and Sing unto God (JM13)'s last frame (its last_frame() at t = 85.9): blue and white bands over the
    house, Side a little dimmer, the Temple warm."""
    seg = G.seg_of
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    house = (1 - temple) * (1 - 0.4 * side)
    b = (np.sin(2 * np.pi * G.pd / 110.0) > 0.25).astype(float)
    return (light(BLUE, 0.42 * b * house) + light(WHITE, 0.36 * (1 - b) * house)
            + light(OIL, 0.45 * temple) + Glow(G, 13).frame(85.9, 1.0))


def last_frame(G, glow, t):
    """Where the scene settles: a steady warm gold over the house (Side a little dimmer), the Temple's light on the
    porch. JM15 opens on this."""
    seg = G.seg_of
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    return light(WARM, 0.34 * (1 - temple) * (1 - 0.3 * side)) + light(OIL, 0.4 * temple) + glow.frame(t, 1.0)


def voice_level(notes, t, rise=0.5, tau=1.8):
    """A singer's light: rising softly on each note, fading slowly through rests."""
    v = 0.0
    for n in notes:
        if n[0] > t:
            break
        a = t - n[0]
        held = min(a, n[1])
        v = max(v, smoothstep(0.0, rise, a) * np.exp(-max(a - n[1], 0.0) / tau) * (0.8 + 0.2 * np.exp(-held / 1.5)))
    return v


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d, seg = G.pd, G.seg_of
    glow = Glow(G, seed)
    temple = (seg == 'Porch Front').astype(float)
    side = (seg == 'Side').astype(float)
    house = (1 - temple) * (1 - 0.3 * side)
    f0, f1 = span(G, 'Porch Front')
    mid = 0.5 * (f0 + f1)
    toward = np.abs(d - mid)
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    pl0, pl1 = span(G, 'Porch Left')
    pr0, pr1 = span(G, 'Porch Right')
    shimmer = Flicker(rng, G.N, 0.05, 0.2)
    start = jm13_end(G)
    for f in range(F):
        t = f * DT
        # the land at peace: corn and pasture in waves about 900 units long, drifting a wave every 20 s
        warmth = smoothstep(T_ADAGIO, T_LAST, t)
        wave = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 900.0 - t / 20.0))
        green = (0.5 + 0.5 * np.sin(2 * np.pi * (d / 1300.0 + t / 31.0) + 1.0)) * (1 - warmth)
        lvl = (0.28 + 0.12 * wave + 0.03 * shimmer(t)) * (1 + 0.12 * warmth)
        out_from = smoothstep(-150.0, 150.0, 300.0 * (t - 0.5) - toward)
        lvl = lvl * (0.6 + 0.4 * out_from)                      # the ritornello warms it from the porch outward
        fr = light(CORN, lvl * (1 - 0.8 * green) * house) + light(PASTURE, 0.9 * lvl * green * house)
        fr += light(OIL, 0.4 * temple) + glow.frame(t, 1.0)
        # the voices: the Woman's white-silver over Left, the Man's sky blue over Right; together they come in along
        # the porch runs toward the Temple
        come = smoothstep(T_TOGETHER - 1.0, T_TOGETHER + 6.0, t)
        cw = (l0 + 0.55 * (l1 - l0)) * (1 - come) + (pl0 + 0.55 * (pl1 - pl0)) * come
        cm = (r0 + 0.4 * (r1 - r0)) * (1 - come) + (pr0 + 0.45 * (pr1 - pr0)) * come
        width = 150.0 - 70.0 * come
        settle = smoothstep(T_LAST, T_LAST + 3.5, t)
        vw = voice_level(WOMAN, t) * (1 - settle)
        vm = voice_level(MAN, t) * (1 - settle)
        fr += light(SILVER, 0.65 * vw * np.exp(-((d - cw) / width) ** 2) * (1 - temple))
        fr += light(SKY, 0.8 * vm * np.exp(-((d - cm) / width) ** 2) * (1 - temple))
        if settle > 0:
            fr = (1 - settle) * fr + settle * last_frame(G, glow, t)
        carry = 1 - smoothstep(0.0, CARRY, t)
        if carry > 0:
            fr = (1 - carry) * fr + carry * start
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The Woman on an oboe from Left, the Man on a flute from Right, both moving in toward the middle when they sing
    together; soft strings and a harpsichord under them; the ritornello's tune on violins with a flute."""
    o = Orchestra(M, level=4.6)
    for t, dd, m, v, h, part in NOTES:
        come = float(smoothstep(T_TOGETHER - 1.0, T_TOGETHER + 6.0, t))
        if part == 'Woman':
            o.play('oboes', m, t, dd * 0.97, v + 2, -0.5 + 0.25 * come, 0.75)
        elif part == 'Man':
            o.play('flutes', m, t, dd * 0.97, v + 6, 0.5 - 0.25 * come, 0.85)
        elif h == 0:                                            # the ritornello and the Adagio's chords
            top = m == max(n[2] for n in NOTES if n[5] == 'Orch' and n[4] == 0 and abs(n[0] - t) < 0.01)
            o.play('violins', m, t, dd * 0.95, v - 10, -0.1, 0.4 if top else 0.25)
            if top and t < T_VERSE:
                o.play('flutes', m + 12 if m < 72 else m, t, dd * 0.95, v - 14, 0.1, 0.3)
        else:
            o.play('cellos', m if m >= 36 else m + 12, t, dd * 0.95, v - 14, 0.0, 0.45)
            if dd >= 0.6:
                o.play('basses', m - 12 if m >= 40 else m, t, dd * 0.95, v - 20, 0.0, 0.28)
    cont = [(t, m, 62, min(dd, 0.45)) for t, dd, m, v, h, part in NOTES if part == 'Orch' and h == 1]
    M.add('harp', M.synth('Keys/Digi Harpsi').render(cont, D + 2.0), 0.0, 0.3, 0.0)
