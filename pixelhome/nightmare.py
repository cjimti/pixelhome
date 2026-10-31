"""Nightmare: a retelling, on one roofline, of the Pumpkin King who found Christmas. Shared by the scenes in
homes/<home>/sequences/nightmare/.

It is a faithful, affectionate interpretation, not a copy: the story beats are the familiar ones, the music is
our own. THEMES are original tunes written for these scenes in the style the story calls for (minor-key marches,
waltzes, celesta and sleigh bells, a swing number for the boogeyman), and each comes back wherever its character
does, the way a film score reprises its themes.

    C = Chart()                                     a scene's music, laid end to end
    C.play('town', style='march', bars=(0, 8))      a theme with its accompaniment, from the current time
    C.events                                        [(t, d, midi, vel, role, tag)] for render() and score()
    B = Band(M); B.perform(C.events, parts); B.finish()      in score(): the orchestra plays the chart

    S = Stage(G)                                    distances, runs, pans and the characters' drawing helpers
    S.jack(fr, p, lvl, facing)                      characters drawn at path distance p (see the methods)
"""
import numpy as np
from .audio import note
from .fx import DT, hexc, light, perc, smoothstep, smooth_noise, Flicker
from . import ring

# ---------------------------------------------------------------------------------------------------- colours

ORANGE = hexc('#ff5000')
PUMPKIN = hexc('#ff7800')
FLAME = hexc('#ff2800')
SLIME = hexc('#30ff10')
VIOLET = hexc('#7010ff')
UV = hexc('#5000ff')
NIGHT = hexc('#0c1ca8')
DUSK = hexc('#3a0a80')
MOON = hexc('#d0dcff')
BONE = hexc('#fff0d0')
WHITE = hexc('#ffffff')
GREY = hexc('#8890a0')
RED = hexc('#ff0010')
GREEN = hexc('#00d020')
GOLD = hexc('#ffb000')
ICE = hexc('#90c8ff')
WARM = hexc('#ffa040')
BLUE = hexc('#1040ff')
PINK = hexc('#ff4090')
NOSE = hexc('#ff3000')              # the ghost dog's glowing nose
SALLY = hexc('#4a7cff')             # the rag doll's blue
HAIR = hexc('#e00818')
BURLAP = hexc('#b0a020')            # the boogeyman's sack under blacklight
BUG = hexc('#60ff00')

# ---------------------------------------------------------------------------------------------------- themes
# Each theme: meter (beats a bar), bpm, melody [(beat, beats, note)] and chords [(beat, beats, symbol)], beats
# counted from its first bar. All original, written for these scenes.

THEMES = {
    'town': dict(meter=4, bpm=120, name="The citizens' march: Halloween Town's own night, E minor",
        melody=[(0, 1, 'E4'), (1, .5, 'E4'), (1.5, .5, 'F#4'), (2, 1, 'G4'), (3, 1, 'B4'),
                (4, 1.5, 'C5'), (5.5, .5, 'B4'), (6, 1, 'A#4'), (7, 1, 'B4'),
                (8, 1, 'E5'), (9, .5, 'D5'), (9.5, .5, 'C5'), (10, 1, 'B4'), (11, 1, 'G4'),
                (12, 1, 'A4'), (13, 1, 'F#4'), (14, 1, 'D#4'), (15, 1, 'B3'),
                (16, .5, 'E4'), (16.5, .5, 'G4'), (17, .5, 'B4'), (17.5, .5, 'E5'), (18, 1, 'D5'), (19, 1, 'C5'),
                (20, .5, 'B4'), (20.5, .5, 'A4'), (21, .5, 'G4'), (21.5, .5, 'F#4'), (22, 1, 'G4'), (23, 1, 'E4'),
                (24, 1, 'F4'), (25, 1, 'A4'), (26, 1, 'C5'), (27, .5, 'B4'), (27.5, .5, 'A4'),
                (28, 1, 'B4'), (29, 1, 'D#4'), (30, 2, 'E4')],
        chords=[(0, 4, 'Em'), (4, 2, 'C'), (6, 2, 'B7'), (8, 4, 'Em'), (12, 4, 'B7'), (16, 2, 'Em'), (18, 2, 'Am'),
                (20, 2, 'C'), (22, 2, 'Em'), (24, 4, 'F'), (28, 2, 'B7'), (30, 2, 'Em')]),
    'king': dict(meter=3, bpm=96, name="The Pumpkin King's lament, A minor (major=True for his triumph)",
        melody=[(0, 1, 'A3'), (1, 1, 'C4'), (2, 1, 'E4'), (3, 2, 'F4'), (5, 1, 'E4'),
                (6, 1, 'D4'), (7, 1, 'F4'), (8, 1, 'A4'), (9, 3, 'G#4'),
                (12, 1.5, 'A4'), (13.5, .5, 'B4'), (14, 1, 'C5'), (15, 2, 'D5'), (17, 1, 'C5'),
                (18, 1, 'B4'), (19, 1, 'A4'), (20, 1, 'G#4'), (21, 3, 'A4'),
                (24, 1, 'C5'), (25, 1, 'B4'), (26, 1, 'A4'), (27, 2, 'G4'), (29, 1, 'F4'),
                (30, 1, 'E4'), (31, 1, 'F4'), (32, 1, 'G4'), (33, 3, 'A4'),
                (36, 1, 'B4'), (37, 1, 'C5'), (38, 1, 'D5'), (39, 2, 'E5'), (41, 1, 'D5'),
                (42, 1, 'C5'), (43, 1, 'B4'), (44, 1, 'G#4'), (45, 3, 'A4')],
        chords=[(0, 3, 'Am'), (3, 3, 'F'), (6, 3, 'Dm'), (9, 3, 'E'), (12, 3, 'Am'), (15, 3, 'Dm'), (18, 3, 'E7'),
                (21, 3, 'Am'), (24, 3, 'F'), (27, 3, 'C'), (30, 3, 'Dm'), (33, 3, 'F'), (36, 3, 'E7'), (39, 3, 'Am'),
                (42, 3, 'E7'), (45, 3, 'Am')],
        major=[(0, 3, 'A'), (3, 3, 'D'), (6, 3, 'D'), (9, 3, 'E'), (12, 3, 'A'), (15, 3, 'D'), (18, 3, 'E7'),
               (21, 3, 'A'), (24, 3, 'F#m'), (27, 3, 'D'), (30, 3, 'Bm'), (33, 3, 'D'), (36, 3, 'E7'), (39, 3, 'A'),
               (42, 3, 'E7'), (45, 3, 'A')]),
    'wonder': dict(meter=6, bpm=330, name='Christmas Town: snow and wonder, G major in 6/8 (beats are eighths)',
        melody=[(0, 1, 'D4'), (1, 1, 'G4'), (2, 1, 'B4'), (3, 2, 'A4'), (5, 1, 'G4'),
                (6, 1, 'F#4'), (7, 1, 'A4'), (8, 1, 'D5'), (9, 3, 'C5'),
                (12, 1, 'B4'), (13, 1, 'G4'), (14, 1, 'E4'), (15, 2, 'C5'), (17, 1, 'B4'),
                (18, 3, 'A4'), (21, 3, 'D4'),
                (24, 1, 'E4'), (25, 1, 'F#4'), (26, 1, 'G4'), (27, 1, 'A4'), (28, 1, 'B4'), (29, 1, 'C5'),
                (30, 2, 'D5'), (32, 1, 'B4'), (33, 3, 'G4'),
                (36, 1, 'E4'), (37, 1, 'G4'), (38, 1, 'C5'), (39, 1, 'B4'), (40, 1, 'A4'), (41, 1, 'F#4'),
                (42, 6, 'G4')],
        chords=[(0, 6, 'G'), (6, 6, 'D7'), (12, 6, 'C'), (18, 6, 'D'), (24, 6, 'C'), (30, 6, 'G'), (36, 3, 'C'),
                (39, 3, 'D7'), (42, 6, 'G')]),
    'sally': dict(meter=3, bpm=84, name="The rag doll's song, D minor",
        melody=[(0, 2, 'A4'), (2, 1, 'G4'), (3, 1.5, 'F4'), (4.5, .5, 'E4'), (5, 1, 'D4'),
                (6, 2, 'E4'), (8, 1, 'C#4'), (9, 3, 'D4'),
                (12, 1, 'F4'), (13, 1, 'G4'), (14, 1, 'A4'), (15, 2, 'Bb4'), (17, 1, 'A4'),
                (18, 1, 'G4'), (19, 1, 'F4'), (20, 1, 'E4'), (21, 3, 'D4'),
                (24, 2, 'D5'), (26, 1, 'C5'), (27, 1.5, 'Bb4'), (28.5, .5, 'A4'), (29, 1, 'G4'),
                (30, 2, 'A4'), (32, 1, 'E4'), (33, 3, 'F4'),
                (36, 1, 'G4'), (37, 1, 'A4'), (38, 1, 'Bb4'), (39, 2, 'C#5'), (41, 1, 'A4'),
                (42, 1, 'D5'), (43, 1, 'E4'), (44, 1, 'C#4'), (45, 3, 'D4')],
        chords=[(0, 3, 'Dm'), (3, 3, 'Bb'), (6, 3, 'A7'), (9, 3, 'Dm'), (12, 3, 'F'), (15, 3, 'Gm'), (18, 3, 'A7'),
                (21, 3, 'Dm'), (24, 3, 'Bb'), (27, 3, 'Gm'), (30, 3, 'A7'), (33, 3, 'Dm'), (36, 3, 'Gm'),
                (39, 3, 'A7'), (42, 3, 'A7'), (45, 3, 'Dm')]),
    'trio': dict(meter=6, bpm=360, name="The three troublemakers' patter, C minor in 6/8 (beats are eighths)",
        melody=[(0, 1, 'C4'), (1, 1, 'Eb4'), (2, 1, 'G4'), (3, 1, 'Ab4'), (4, 1, 'G4'), (5, 1, 'Eb4'),
                (6, 1, 'F4'), (7, 1, 'D4'), (8, 1, 'B3'), (9, 3, 'G3'),
                (12, 1, 'C4'), (13, 1, 'Eb4'), (14, 1, 'G4'), (15, 1, 'C5'), (16, 1, 'B4'), (17, 1, 'Ab4'),
                (18, 2, 'G4'), (20, 1, 'F#4'), (21, 3, 'G4'),
                (24, 1, 'Ab4'), (25, 1, 'G4'), (26, 1, 'F4'), (27, 1, 'Eb4'), (28, 1, 'D4'), (29, 1, 'C4'),
                (30, 1, 'B3'), (31, 1, 'D4'), (32, 1, 'F4'), (33, 3, 'Ab4'),
                (36, 1, 'G4'), (37, 1, 'Eb4'), (38, 1, 'C4'), (39, 1, 'F#4'), (40, 1, 'G4'), (41, 1, 'B3'),
                (42, 3, 'C4'), (45, 1, 'G3'), (46, 2, 'C4')],
        chords=[(0, 6, 'Cm'), (6, 6, 'G7'), (12, 3, 'Cm'), (15, 3, 'Ab'), (18, 6, 'G'), (24, 3, 'Fm'), (27, 3, 'Cm'),
                (30, 6, 'G7'), (36, 3, 'Cm'), (39, 3, 'D7'), (42, 6, 'Cm')]),
    'boogey': dict(meter=4, bpm=132, swing=True, name="The boogeyman's shuffle, G minor blues (swung)",
        melody=[(0, .5, 'G3'), (.5, .5, 'Bb3'), (1, .5, 'C4'), (1.5, .5, 'Db4'), (2, 1, 'D4'), (3, 1, 'Bb3'),
                (4, .5, 'F4'), (4.5, .5, 'D4'), (5, .5, 'F4'), (5.5, 2.5, 'G4'),
                (8, .5, 'C4'), (8.5, .5, 'Eb4'), (9, .5, 'F4'), (9.5, .5, 'Gb4'), (10, 1, 'G4'), (11, 1, 'Eb4'),
                (12, .5, 'Bb3'), (12.5, .5, 'G3'), (13, .5, 'Bb3'), (13.5, 2.5, 'C4'),
                (16, 1, 'D4'), (17, 1, 'F#4'), (18, 1, 'A4'), (19, .5, 'C5'), (19.5, .5, 'Bb4'),
                (20, .5, 'A4'), (20.5, .5, 'G4'), (21, .5, 'F#4'), (21.5, .5, 'Eb4'), (22, 2, 'D4'),
                (24, .5, 'G4'), (24.5, .5, 'F4'), (25, .5, 'D4'), (25.5, .5, 'Bb3'), (26, .5, 'C4'), (26.5, .5, 'Db4'),
                (27, 1, 'D4'), (28, 4, 'G3')],
        chords=[(0, 8, 'Gm7'), (8, 4, 'Cm7'), (12, 4, 'Gm7'), (16, 8, 'D7'), (24, 2, 'Gm7'), (26, 2, 'D7'),
                (28, 4, 'Gm')]),
    'workshop': dict(meter=4, bpm=132, name='Making toys: the whole town at work, A minor',
        melody=[(0, .5, 'A4'), (.5, .5, 'E4'), (1, .5, 'A4'), (1.5, .5, 'C5'), (2, .5, 'B4'), (2.5, .5, 'E4'),
                (3, .5, 'G#4'), (3.5, .5, 'B4'),
                (4, .5, 'C5'), (4.5, .5, 'A4'), (5, .5, 'E5'), (5.5, .5, 'A4'), (6, .5, 'D5'), (6.5, .5, 'C5'),
                (7, 1, 'B4'),
                (8, .5, 'F4'), (8.5, .5, 'A4'), (9, .5, 'C5'), (9.5, .5, 'F5'), (10, .5, 'E5'), (10.5, .5, 'C5'),
                (11, .5, 'A4'), (11.5, .5, 'C5'),
                (12, .5, 'D5'), (12.5, .5, 'B4'), (13, .5, 'G#4'), (13.5, .5, 'E4'), (14, 2, 'A4'),
                (16, .5, 'A4'), (16.5, .5, 'E4'), (17, .5, 'A4'), (17.5, .5, 'C5'), (18, .5, 'B4'), (18.5, .5, 'E4'),
                (19, .5, 'G#4'), (19.5, .5, 'B4'),
                (20, .5, 'C5'), (20.5, .5, 'A4'), (21, .5, 'E5'), (21.5, .5, 'A4'), (22, .5, 'D5'), (22.5, .5, 'C5'),
                (23, 1, 'B4'),
                (24, .5, 'F4'), (24.5, .5, 'A4'), (25, .5, 'C5'), (25.5, .5, 'F5'), (26, .5, 'E5'), (26.5, .5, 'C5'),
                (27, .5, 'A4'), (27.5, .5, 'C5'),
                (28, .5, 'D5'), (28.5, .5, 'B4'), (29, .5, 'G#4'), (29.5, .5, 'B4'), (30, 2, 'E5')],
        chords=[(0, 2, 'Am'), (2, 2, 'E'), (4, 2, 'Am'), (6, 2, 'E'), (8, 2, 'F'), (10, 2, 'Am'), (12, 2, 'E'),
                (14, 2, 'Am'), (16, 2, 'Am'), (18, 2, 'E'), (20, 2, 'Am'), (22, 2, 'E'), (24, 2, 'F'), (26, 2, 'Am'),
                (28, 4, 'E')]),
    'zero': dict(meter=4, bpm=120, name='The ghost dog, E major (a glockenspiel tune with a woof at the end)',
        melody=[(0, .5, 'B4'), (.5, .5, 'E5'), (1, .5, 'G#5'), (1.5, .5, 'B5'), (2, .75, 'A5'), (2.75, .25, 'G#5'),
                (3, 1, 'F#5'),
                (4, .5, 'E5'), (4.5, .5, 'F#5'), (5, .5, 'G#5'), (5.5, .5, 'A5'), (6, 1, 'B5'), (7, 1, 'E5')],
        chords=[(0, 2, 'E'), (2, 2, 'B7'), (4, 2, 'E'), (6, 1, 'B7'), (7, 1, 'E')]),
    'santa': dict(meter=4, bpm=104, name="Santa's carol, warm brass, F major",
        melody=[(0, 1, 'C4'), (1, 1, 'F4'), (2, 1, 'A4'), (3, 1, 'G4'),
                (4, 1, 'F4'), (5, .5, 'E4'), (5.5, .5, 'D4'), (6, 2, 'C4'),
                (8, 1, 'Bb3'), (9, 1, 'D4'), (10, 1, 'G4'), (11, 1, 'F4'),
                (12, 2, 'E4'), (14, 2, 'G4'),
                (16, 1, 'A4'), (17, 1, 'C5'), (18, 1, 'Bb4'), (19, 1, 'A4'),
                (20, 1.5, 'G4'), (21.5, .5, 'F4'), (22, 2, 'D4'),
                (24, 1, 'C4'), (25, 1, 'F4'), (26, 1, 'E4'), (27, 1, 'G4'),
                (28, 4, 'F4')],
        chords=[(0, 2, 'F'), (2, 2, 'C'), (4, 2, 'Dm'), (6, 2, 'C'), (8, 2, 'Bb'), (10, 2, 'F'), (12, 2, 'C'),
                (14, 2, 'C7'), (16, 2, 'F'), (18, 2, 'Bb'), (20, 2, 'Gm'), (22, 2, 'Bb'), (24, 2, 'F'), (26, 2, 'C7'),
                (28, 4, 'F')]),
}

QUALITY = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10), 'm7': (0, 3, 7, 10), 'maj7': (0, 4, 7, 11),
           'dim': (0, 3, 6), 'dim7': (0, 3, 6, 9), 'aug': (0, 4, 8), 'm6': (0, 3, 7, 9), '6': (0, 4, 7, 9),
           'sus4': (0, 5, 7)}


def chord(sym):
    """'F#m7' -> (root pitch class, intervals)."""
    root = sym[:2] if len(sym) > 1 and sym[1] in '#b' else sym[:1]
    return note(root + '4') % 12, QUALITY[sym[len(root):]]


def voicing(sym, low=55):
    """The chord's tones from low up within an octave and a half: what the middle of the band plays."""
    pc, iv = chord(sym)
    r = low + (pc - low) % 12
    out = sorted({(r + i - low) % 12 + low for i in iv})
    return out


def bass_note(sym, fifth=False, low=40):
    """The chord's root (or fifth) in the bass, E2..D#3."""
    pc, iv = chord(sym)
    return low + (pc + (iv[2] if fifth else 0) - low) % 12


def _swing(b):
    """Swung eighths: the off-beat eighth moves from half to two thirds of the beat."""
    whole = np.floor(b + 1e-9)
    f = b - whole
    return whole + np.where(f < 0.5, f * 4 / 3, 2 / 3 + (f - 0.5) * 2 / 3)


# accompaniment styles: how each bar's chords are played. Each yields (beat, beats, midi, vel, role)
def _accompany(chords, meter, style, b0, b1):
    out = []
    for cb, cl, sym in chords:
        for b in np.arange(cb, cb + cl, 1.0):
            if not b0 <= b < b1:
                continue
            k = int(round(b)) % meter
            first = b == cb
            if style == 'march':                    # oom-pah: bass on 1 and 3, chords off the beat
                if k % 2 == 0:
                    out.append((b, .5, bass_note(sym, fifth=(k == 2 and not first)), 100, 'bass'))
                else:
                    out += [(b, .4, m, 82, 'chord') for m in voicing(sym)]
                out.append((b + .5, .3, None, 70, 'snare' if k % 2 else 'tick'))
            elif style == 'waltz':                  # bass on 1, chord on 2 and 3
                if k == 0:
                    out.append((b, 1, bass_note(sym), 96, 'bass'))
                else:
                    out += [(b, .6, m, 74, 'chord') for m in voicing(sym)]
            elif style == 'gallop':                 # 6/8 in eighths: bass on 1 and 4, chords on 3 and 6
                if k in (0, 3):
                    out.append((b, 1, bass_note(sym, fifth=k == 3), 98, 'bass'))
                elif k in (2, 5):
                    out += [(b, .5, m, 78, 'chord') for m in voicing(sym)]
                if k in (0, 3):
                    out.append((b, .3, None, 80, 'tick'))
            elif style == 'shuffle':                # walking bass, chords on 2 and 4, a ride on every beat
                pc, iv = chord(sym)
                walk = [0, iv[1], iv[2], iv[2] + 2 if len(iv) < 4 else iv[3]]
                out.append((b, .9, bass_note(sym) + walk[k % 4], 96, 'bass'))
                if k % 2:
                    out += [(b, .3, m, 76, 'chord') for m in voicing(sym)]
                out.append((b, .3, None, 70, 'snare' if k % 2 else 'tick'))
            elif style == 'drive':                  # eighth-note bass and chords on every beat, for chases
                out.append((b, .45, bass_note(sym), 100, 'bass'))
                out.append((b + .5, .45, bass_note(sym) + 12, 84, 'bass'))
                out += [(b, .3, m, 80, 'chord') for m in voicing(sym)]
                out.append((b + .5, .3, None, 76, 'snare' if k % 2 else 'tick'))
            elif style == 'arp':                    # broken chords, an eighth apart, for celesta and harp
                tones = voicing(sym, 60)
                for j in range(2):
                    out.append((b + .5 * j, .5, tones[(2 * k + j) % len(tones)], 72, 'arp'))
                if first:
                    out.append((b, cl, bass_note(sym), 80, 'pedal'))
            elif style == 'hold':                   # long chords and a pedal bass
                if first:
                    out += [(b, cl, m, 70, 'hold') for m in voicing(sym)]
                    out.append((b, cl, bass_note(sym), 76, 'pedal'))
    return out


class Chart:
    """A scene's music laid end to end: themes and their accompaniment, rests, and the times everything lands.
    events are (t, d, midi or None, vel, role, tag): role is 'tune', 'bass', 'chord', 'arp', 'hold', 'pedal',
    'snare' or 'tick' (midi None for those two), and tag is whatever the scene passed (the theme's name by
    default), so render() can find its moments. beats lists (t, beat in bar, tag) for every beat played."""

    def __init__(self, start=0.0):
        self.t = start
        self.events, self.beats, self.marks = [], [], {}

    def play(self, theme, style='march', bars=None, bpm=None, transpose=0, major=False, tune=True, tag=None,
             vel=96, octave=0):
        """Play bars (first, last) of a theme from now, its tune (unless tune=False) over style. Returns (t0, beat)."""
        th = THEMES[theme]
        meter, beat = th['meter'], 60.0 / (bpm or th['bpm'])
        a, b = bars if bars else (0, int(np.ceil(max(x[0] + x[1] for x in th['melody']) / meter)))
        b0, b1 = a * meter, b * meter
        sw = _swing if th.get('swing') else (lambda x: x)
        tag = tag or theme
        t0 = self.t - b0 * beat
        chords = th['major'] if major else th['chords']
        tr = transpose + 12 * octave
        if tune:
            for mb, ml, n in th['melody']:
                if b0 <= mb < b1:
                    m = note(n) + tr
                    if major and n[0] in 'CFG' and n[1:2] != '#':
                        m += 1                      # A minor's C, F and G sharpened into A major
                    s = float(sw(mb))
                    self.events.append((t0 + s * beat, ml * beat, m, vel, 'tune', tag))
        for sb, sl, m, v, role in _accompany(chords, meter, style, b0, b1):
            s = float(sw(sb))
            self.events.append((t0 + s * beat, sl * beat, None if m is None else m + transpose, v, role, tag))
        for k in range(b0, b1):
            self.beats.append((t0 + k * beat, k % meter, tag))
        self.t = t0 + b1 * beat
        return t0 + b0 * beat, beat

    def rest(self, seconds):
        self.t += seconds
        return self.t

    def mark(self, name):
        self.marks[name] = self.t
        return self.t

    def tunes(self, tag=None):
        """The tune's notes (t, d, midi) in time order, of one tag or all."""
        return sorted((e[0], e[1], e[2]) for e in self.events if e[4] == 'tune' and (tag is None or e[5] == tag))

    def downbeats(self, tag=None):
        return [t for t, k, g in self.beats if k == 0 and (tag is None or g == tag)]


# ---------------------------------------------------------------------------------------------------- the band

EXTRA = {
    'pizz': (None, 'Strings/Violin Section/Pizz/*.wav', 'strings', 0.3),
    'cellos pizz': (None, 'Strings/Cello Section/pizzT/*.wav', 'low', -0.25),
    'basses pizz': (None, 'Strings/Solo Contrabass/Pizz/*.wav', 'low', 0.2),
    'xylo': (None, 'Percussion/Xylo/*.wav', 'perc', 0.1),
    'marimba': (None, 'Percussion/Marimba/*.wav', 'perc', -0.1),
    'muted horn': ('Brass/F Horn/mute/*.wav', None, 'brass', -0.3),
    'buzz trombone': ('Brass/OldTrombone/Buzz/*.wav', None, 'brass', 0.1),
}
HITS = {'snare': 'Percussion/Snare2-HitSN_v[3579]*.wav', 'snare roll': 'Percussion/Snare2-rollSN_v[35]*.wav',
        'ride': 'Percussion/susCymb1-hitstick_mp*.wav', 'sleigh': 'Percussion/Sleighbells_Hit*.wav',
        'slapstick': 'VSCO 1 Percussion/varWood/slapstick[0-9].wav', 'wood': 'VSCO 1 Percussion/varWood/wood_click*.wav',
        'ratchet': 'Percussion/Ratchet1-Crank*.wav', 'bell tree': 'Percussion/BellTree_Stroke*.wav',
        'claves': 'Percussion/Claves1_Hit*.wav', 'tambourine': 'Percussion/Tamb1-Hit*.wav',
        'guiro': 'Percussion/Guiro-Hit*.wav', 'cowbell': 'Percussion/Cowbell1_Hit*.wav'}
SYNTHS = {'choir': 'Pads/Synth Choir MW O-Ah', 'celesta': 'Plucks/Magic Music Box', 'ghost': 'Pads/Ghost Pad'}

# what each role of a chart plays on by default; a scene passes parts={role or (tag, role): [(section, transpose,
# velocity change, gain)]} to change any of it (an empty list is silence)
DEFAULT = {'tune': [('violins', 0, 0, 0.6)], 'bass': [('tuba', -12, 0, 0.7), ('basses pizz', 0, -6, 0.5)],
           'chord': [('pizz', 0, -6, 0.45)], 'arp': [('celesta', 12, 0, 0.5)], 'hold': [('choir', 0, -10, 0.5)],
           'pedal': [('cellos', 0, -10, 0.5)], 'snare': [('snare', 0, -10, 0.35)], 'tick': []}


class Band(ring.Orchestra):
    """The Ring's orchestra (strings, winds, brass, timpani and its stage effects: thunder, wind, fire, boom,
    clash, shatter) with what this story adds: pizzicato, xylophone and marimba, muted horn, the old buzzing
    trombone, snare and sleigh bells, and three Surge voices (a choir's 'oo-ah', a celesta-like music
    box and a ghostly pad) collected while the scene plays and rendered by finish()."""

    def __init__(self, M, level=1.0):
        super().__init__(M, level)
        self.extra = {}
        for name, (sus, short, _, _) in EXTRA.items():
            self.extra[name] = (M.sampler(sus, tune=-12) if sus else None,
                                M.sampler(short, tune=0 if name in ('xylo', 'marimba') else -12)
                                if short else None)
        for name, p in HITS.items():
            self.hits[name] = M.hits(p)
        self.synths = {name: M.synth(p) for name, p in SYNTHS.items()}
        self.queued = {name: [] for name in SYNTHS}
        M.bus('voices', gain=0.16 * level, reverb=0.4)
        self.level = level

    def play(self, section, m, t, d, v, pan=None, gain=1.0):
        if section in self.synths:
            self.queued[section].append((t, int(m), int(np.clip(v, 1, 127)), d, pan, gain))
            return
        if section in self.hits:
            self.hit(section, t, int(np.clip(v, 1, 127)), gain=gain, pan=pan or 0.0)
            return
        if section not in self.extra:
            return super().play(section, m, t, d, v, pan, gain)
        sus, short = self.extra[section]
        _, _, bus, p = EXTRA[section]
        pan = p if pan is None else pan
        v = int(np.clip(v, 1, 127))
        if sus is not None and (d >= 0.25 or short is None):
            if d > 1.2:
                self.hold(bus, sus, m, t, t + d, v, pan, gain)
            else:
                self.M.add(bus, sus.play(m, v, dur=d, release=0.15), t, gain, pan)
        else:
            self.M.add(bus, short.play(m, v), t, gain, pan)

    def perform(self, events, parts=None, pan=None):
        """Play a chart's events; parts overrides DEFAULT by role or (tag, role); pan(t, midi, role) places them."""
        parts = parts or {}
        for t, d, m, v, role, tag in events:
            plan = parts.get((tag, role), parts.get(role, DEFAULT.get(role, [])))
            for section, tr, dv, g in plan:
                pp = pan(t, m, role) if pan else None
                if m is None:
                    self.play(section, 0, t, d, v + dv, pp, g)
                else:
                    self.play(section, m + tr, t, d, v + dv, pp, g)

    def finish(self):
        """Render the Surge voices: everything queued on each, one pass per pan position."""
        seconds = self.M.seconds + 4
        for name, notes in self.queued.items():
            if not notes:
                continue
            groups = {}
            for t, m, v, d, pan, g in notes:
                groups.setdefault((pan, g), []).append((t, m, v, d))
            for (pan, g), ns in groups.items():
                sig = self.synths[name].render(sorted(ns), seconds)
                self.M.add('voices', sig, 0.0, g * (0.6 if name == 'celesta' else 1.0), pan)

    # ---- the stage effects this story needs beyond the Ring's

    def woof(self, t, pan=0.0, big=1.0):
        """The ghost dog's bark: a muted-horn yap with a breath of noise."""
        from .audio import SR
        self.play('muted horn', note('A3'), t, 0.12, int(96 + 20 * big), pan, 0.9 * big)
        self.play('muted horn', note('E4'), t + 0.02, 0.1, int(90 + 20 * big), pan, 0.6 * big)
        n = int(0.12 * SR)
        puff = self._noise(0, 300, 2500, int(t * 1000) + 3, n=n) * np.exp(-np.arange(n) / (0.03 * SR))
        self._sfx(puff, t, 0.25 * big, pan)

    def sleigh_bells(self, t0, t1, beat=0.25, pan=0.0, v=90, gain=1.0):
        """Sleigh bells shaken from t0 to t1, beat seconds apart; pan may be pan(t)."""
        t = t0
        while t < t1:
            pp = pan(t) if callable(pan) else pan
            self.M.add('fx', self.hits['sleigh'].play(int(v)), t, 0.35 * gain, float(np.clip(pp, -1, 1)))
            t += beat

    def scream(self, t, pan=0.0, gain=1.0, high=1.0):
        """A frightened shriek from a house: a voice-like wail that slides up and falls."""
        from .audio import SR
        n = int(0.9 * SR)
        tt = np.arange(n) / SR
        f = (700 + 500 * high) * (1 + 0.5 * np.sin(np.pi * np.clip(tt / 0.9, 0, 1))) * (1 + 0.03 * np.sin(2 * np.pi * 7 * tt))
        ph = 2 * np.pi * np.cumsum(f) / SR
        env = np.clip(tt / 0.04, 0, 1) * np.exp(-tt / 0.45)
        sig = env * (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph))
        sig += 0.3 * env * self._noise(0, 1500, 5000, int(t * 997), n=n)
        self._sfx(sig / np.abs(sig).max(), t, 0.22 * gain, pan)

    def siren(self, t0, t1, pan=0.0, gain=1.0):
        """An air-raid siren rising and falling from t0 to t1."""
        from .audio import SR
        n = int((t1 - t0) * SR)
        tt = np.arange(n) / SR
        f = 300 + 500 * (0.5 - 0.5 * np.cos(2 * np.pi * tt / 4.0))
        ph = 2 * np.pi * np.cumsum(f) / SR
        env = np.clip(tt / 1.0, 0, 1) * np.clip((t1 - t0 - tt) / 1.5, 0, 1)
        sig = env * (np.sin(ph) + 0.5 * np.sign(np.sin(ph)) * 0.3)
        self._sfx(sig, t0, 0.18 * gain, pan)

    def flak(self, t, pan=0.0, gain=1.0):
        """An anti-aircraft burst: a thump and a crack."""
        self.hit('bass drum', t, 120, gain=0.6 * gain, pan=pan, fx=True)
        self.hit('snare', t + 0.01, 120, gain=0.4 * gain, pan=pan, fx=True)
        from .audio import SR
        n = int(0.25 * SR)
        crack = self._noise(0, 800, 8000, int(t * 1000) + 11, n=n) * np.exp(-np.arange(n) / (0.04 * SR))
        self._sfx(crack, t, 0.5 * gain, pan)

    def whoosh(self, t, seconds=0.8, up=True, pan=0.0, gain=1.0):
        """Something flying past or swirling."""
        from .audio import whoosh
        w = whoosh(seconds, 300 if up else 3000, 3000 if up else 300, 0.5, seed=int(t * 100))
        self.M.add('fx', w, t, gain, pan)

    def swarm(self, t0, t1, level=1.0, pan=0.0, seed=4):
        """Bugs pouring out: a buzzing, skittering hiss."""
        from .audio import SR
        dur = t1 - t0
        n = int(dur * SR)
        tt = np.arange(n) / SR
        buzz = np.sin(2 * np.pi * 180 * tt + 3 * np.sin(2 * np.pi * 23 * tt)) * self._wobble(n, 9, seed, 0.9)
        hiss = self._noise(0, 2000, 7000, seed + 1, n=n) * self._wobble(n, 14, seed + 2, 0.9)
        fade = np.clip(tt / 0.3, 0, 1) * np.clip((dur - tt) / 1.0, 0, 1)
        self._sfx((0.5 * buzz + 0.6 * hiss) * fade * level, t0, 0.5, pan)


# ---------------------------------------------------------------------------------------------------- the stage

def drift(seed, x, scale, octaves=2):
    """Smooth noise in [-1, 1] over coordinates x on a lattice fixed in space, so x - v t moves with t (fx.smooth_noise
    re-bases its lattice on the smallest coordinate, which cancels any drift)."""
    rng = np.random.default_rng(seed)
    out, amp, total = np.zeros_like(x, float), 1.0, 0.0
    for o in range(octaves):
        s = scale / 2 ** o
        n = 4096
        lat = rng.uniform(-1, 1, n)
        lat[-1] = lat[0]                                    # periodic, so wrapping round leaves no seam
        out += amp * np.interp((x / s) % (n - 1), np.arange(n), lat)
        total += amp
        amp *= 0.5
    return out / total


class Stage:
    """The house as the story's stage. d is each node's distance along the roofline (G.pd), L its length; runs by
    name; at(run, u) a point u of the way along a run; pan(p) where a point sounds from the street. The porch is the
    centre of every scene (Halloween Town's square, the hill's moon, the boogeyman's lair); the wings are its
    surroundings and are never left dark while the porch has the action; nothing enters on Side, it only exits."""

    RUNS = ('Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')

    def __init__(self, G, seed=0):
        self.G = G
        self.d = G.pd
        self.L = float(G.length)
        self.N = G.N
        self.path = G.path
        self.pp = G.pd[G.path]                              # distance along the path, by path index
        self.run = {r: G.seg_of == r for r in self.RUNS}
        self.porch = self.run['Porch Left'] | self.run['Porch Front'] | self.run['Porch Right']
        self.wings = self.run['Left'] | self.run['Right']
        self.mid = self.at('Porch Front', 0.5)
        self.rng = np.random.default_rng(1993 + seed)
        order = np.argsort(G.pd)
        self._xs, self._ds = G.pos[order, 0], G.pd[order]
        self._x0, self._x1 = self._xs.min(), self._xs.max()

    def at(self, run, u):
        s = self.d[self.G.seg[run]]
        return float(s.min() + u * (s.max() - s.min()))

    def pan(self, p):
        """Path distance -> left/right across the facade as heard from the street."""
        x = np.interp(p, self._ds, self._xs)
        return float(0.85 * (2 * (x - self._x0) / (self._x1 - self._x0) - 1))

    def run_at(self, p):
        """The run that holds path distance p, as a mask."""
        return self.run[self.G.seg_of[self.path[self.k(p)]]]

    def blob(self, p, w):
        return np.exp(-((self.d - p) / w) ** 2)

    def span(self, a, b, soft=8.0):
        """1 between path distances a and b, soft-edged."""
        return smoothstep(a - soft, a + soft, self.d) * smoothstep(b + soft, b - soft, self.d)

    def k(self, p):
        """Nearest path index to distance p."""
        return int(np.clip(np.searchsorted(self.pp, p), 0, self.N - 1))

    def k_off(self, p):
        """Path index of distance p, running on past either free end (about 4 units a pixel beyond Right, 6 beyond
        the back of Side), so a sprite can walk in or out of the house instead of piling up on its last pixel."""
        if p > self.pp[-1]:
            return self.N - 1 + int(round((p - self.pp[-1]) / 4.0))
        if p < 0:
            return int(round(p / 6.0))
        return self.k(p)

    # ---- pixel sprites. A sprite is a list of (offset in pixels along the path, colour, level); offsets run
    # ahead of the centre for positive values in the facing direction. dark pixels are colour None: they cut
    # what is behind them, which is how eyes and stitches read on a line of lights.

    def sprite(self, fr, p, pixels, lvl=1.0, facing=1, cut=True):
        if lvl <= 0:
            return fr
        k0 = self.k_off(p)
        offs = [o for o, _, _ in pixels]
        if cut:                                             # the figure stands in front of the backdrop
            for o in range(min(offs) - 1, max(offs) + 2):
                k = k0 + facing * o
                if 0 <= k < self.N:
                    fr[self.path[k]] *= 1 - min(1.0, lvl * 1.5) * (0.9 if min(offs) <= o <= max(offs) else 0.5)
        for o, col, v in pixels:
            k = k0 + facing * o
            if 0 <= k < self.N and col is not None:
                fr[self.path[k]] += light(col, lvl * v)
        return fr

    def jack(self, fr, p, lvl=1.0, facing=1, glow=0.0, t=0.0):
        """The Pumpkin King: a bright white skull with two dark eye sockets and a dark grin, his tall pinstriped
        body trailing behind (thin white stripes on black), a little bat bow tie at the neck."""
        px = [(2, BONE, 1.0), (1, None, 0), (0, BONE, 1.0), (-1, None, 0), (-2, BONE, 1.0), (-3, BONE, 0.9),
              (-4, VIOLET, 0.25)]
        for j in range(5, 15):
            px.append((-j, WHITE if j % 2 else None, 0.42 if j % 2 else 0))
        fr = self.sprite(fr, p, px, lvl, facing)
        if glow:
            fr += light(MOON, glow * lvl * self.blob(p, 40))
        return fr

    def sally(self, fr, p, lvl=1.0, facing=1):
        """The rag doll: long red hair, a pale blue face, and her patchwork dress behind in blue, yellow, red and
        green with dark stitches between the patches."""
        px = [(2, SALLY, 0.9), (1, SALLY, 0.95), (0, HAIR, 0.85), (-1, HAIR, 0.85), (-2, HAIR, 0.7),
              (-3, None, 0), (-4, BLUE, 0.55), (-5, GOLD, 0.5), (-6, None, 0), (-7, RED, 0.5), (-8, GREEN, 0.5),
              (-9, None, 0), (-10, BLUE, 0.45), (-11, GOLD, 0.4)]
        return self.sprite(fr, p, px, lvl, facing)

    def zero(self, fr, p, lvl=1.0, facing=1, t=0.0, nose=1.0):
        """The ghost dog: a glowing orange-red nose in front, a little white sheet of a body trailing behind,
        its wispy tail wagging."""
        wag = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)
        px = [(1, NOSE, 1.0 * nose), (0, BONE, 0.55), (-1, BONE, 0.7), (-2, BONE, 0.6), (-3, BONE, 0.45),
              (-4, BONE, 0.3 + 0.15 * wag), (-5, BONE, 0.15 + 0.15 * wag), (-6, BONE, 0.08 * wag)]
        fr = self.sprite(fr, p, px, lvl, facing)
        fr += light(NOSE, 0.45 * nose * lvl * self.blob(p + facing * 6, 18))
        return fr

    def oogie(self, fr, p, lvl=1.0, t=0.0, size=1.0):
        """The boogeyman: a huge lumpy burlap sack glowing under blacklight, two dark eyes and a dark grin, its
        edges seething with green."""
        half = int(13 * size)
        px = [(o, None, 0) if o in (-3, 3) else (o, BURLAP, 0.85 * (0.8 + 0.2 * np.sin(1.7 * o + 2.0 * t)))
              for o in range(-half, half + 1)]
        fr = self.sprite(fr, p, px, lvl, 1)
        edge = np.exp(-((np.abs(self.d - p) - half * 4.5) / 10) ** 2)
        fr += light(BUG, 0.6 * lvl * edge * (0.7 + 0.3 * np.sin(9 * t)))
        return fr

    def santa(self, fr, p, lvl=1.0, facing=1):
        """Santa: a white beard and trim at the front, a red coat, and his sack behind."""
        px = [(1, WHITE, 0.9), (0, WHITE, 0.8), (-1, RED, 1.0), (-2, RED, 1.0), (-3, WHITE, 0.6), (-4, RED, 0.9),
              (-5, RED, 0.9), (-6, None, 0), (-7, WARM, 0.45), (-8, WARM, 0.45)]
        return self.sprite(fr, p, px, lvl, facing)

    def trio(self, fr, p, lvl=1.0, facing=1, gap=5, t=0.0, bounce=0.0):
        """The three troublemakers in a row, small masks: the devil (red), the witch (purple and green) and the
        skeleton (white and green)."""
        masks = [[(1, RED, 1.0), (0, RED, 0.85), (-1, FLAME, 0.6)],
                 [(1, VIOLET, 1.0), (0, SLIME, 0.7), (-1, VIOLET, 0.6)],
                 [(1, BONE, 1.0), (0, None, 0), (-1, SLIME, 0.6)]]
        for i, m in enumerate(masks):
            hop = bounce * max(0.0, np.sin(2 * np.pi * (2 * t + i / 3)))
            fr = self.sprite(fr, p - facing * i * gap * 4.5, m, lvl * (0.75 + 0.25 * hop), facing)
        return fr

    def mayor(self, fr, p, lvl=1.0, happy=1.0):
        """The mayor: a tall dark hat and a face that spins between a happy orange and a worried pale blue."""
        face = happy * PUMPKIN + (1 - happy) * ICE
        px = [(3, VIOLET, 0.3), (2, None, 0), (1, face, 1.0), (0, face, 1.0), (-1, face, 1.0), (-2, None, 0),
              (-3, RED, 0.5)]
        return self.sprite(fr, p, px, lvl, 1)

    def sleigh(self, fr, p, lvl=1.0, facing=1, t=0.0, nose=1.0, gap=4, driver=True):
        """The coffin sleigh: the ghost dog's nose leading, four skeleton reindeer, the dark coffin sleigh, and the
        Pumpkin King driving."""
        fr = self.zero(fr, p, lvl, facing, t, nose)
        x = p - facing * 9 * 4.5
        for i in range(4):
            leap = 0.75 + 0.25 * np.sin(2 * np.pi * (2.5 * t + i / 4))
            fr = self.sprite(fr, x - facing * i * gap * 4.5, [(1, BONE, 0.9 * leap), (0, BONE, 0.6 * leap),
                                                               (-1, BONE, 0.4)], lvl, facing)
        x -= facing * (4 * gap + 2) * 4.5
        fr = self.sprite(fr, x, [(2, RED, 0.6), (1, DUSK, 0.6), (0, DUSK, 0.6), (-1, DUSK, 0.6), (-2, RED, 0.6)],
                         lvl, facing)
        if driver:
            fr = self.sprite(fr, x - facing * 6 * 4.5, [(1, BONE, 1.0), (0, None, 0), (-1, BONE, 1.0),
                                                        (-2, None, 0), (-3, RED, 0.8), (-4, RED, 0.8)], lvl, facing)
        return fr

    def present(self, fr, p, col, lvl=1.0, ribbon=GOLD):
        return self.sprite(fr, p, [(1, col, 0.9), (0, ribbon, 1.0), (-1, col, 0.9)], lvl, 1)

    # ---- backdrops, each -> (N,3) PWM at time t with levels 0..1

    def town(self, t, lv=1.0, mist=1.0, windows=1.0, seed=0):
        """Halloween Town at night: a deep violet sky on every run, orange windows here and there that flicker,
        and green mist drifting along the roof."""
        rng = np.random.default_rng(31 + seed)
        if not hasattr(self, '_town'):
            self._town = dict(win=(rng.random(self.N) < 0.09) * rng.uniform(0.6, 1.0, self.N),
                              fl=Flicker(rng, self.N, 0.3, 2.5), mist=rng.uniform(0, 1000))
        T = self._town
        fr = light(DUSK, 0.32 * lv * np.ones(self.N))
        fr += light(PUMPKIN, 0.75 * lv * windows * T['win'] * (0.8 + 0.2 * T['fl'](t)))
        m = 0.5 + 0.5 * drift(7, self.d - 40 * t + T['mist'], 180.0)
        fr += light(SLIME, 0.6 * lv * mist * np.clip(m - 0.3, 0, 1) * 1.4)
        return fr

    def christmas(self, t, lv=1.0, snow=1.0, bulbs=1.0, seed=0):
        """Christmas Town: strings of coloured bulbs (red, green, gold, blue) on a soft snowy blue, warm windows, and
        snowflakes twinkling down the whole roof."""
        if not hasattr(self, '_xmas'):
            rng = np.random.default_rng(25 + seed)
            cols = np.array([RED, GREEN, GOLD, BLUE])
            self._xmas = dict(cols=cols[self.G.pi % 4], fl=Flicker(rng, self.N, 0.2, 1.0),
                              ph=rng.uniform(0, 1, self.N), rate=rng.uniform(0.25, 0.6, self.N))
        X = self._xmas
        fr = light(ICE, 0.22 * lv * np.ones(self.N))
        on = (self.G.pi % 2 == 0) * (0.8 + 0.2 * X['fl'](t))
        fr += perc(0.85 * lv * bulbs * on)[:, None] * X['cols']
        ph = (X['ph'] + X['rate'] * t) % 1.0
        flake = np.exp(-((ph - 0.5) / 0.04) ** 2)
        fr += light(WHITE, 0.8 * lv * snow * flake)
        return fr

    def snowfall(self, t, amount=1.0, seed=3):
        """Snow alone: white flakes sparkling on and off all along the roof."""
        rng = np.random.default_rng(seed)
        ph = (rng.uniform(0, 1, self.N) + rng.uniform(0.3, 0.7, self.N) * t) % 1.0
        return light(WHITE, 0.9 * amount * np.exp(-((ph - 0.5) / 0.05) ** 2))

    def graveyard(self, t, lv=1.0, moon=1.0, hill=1.0):
        """The graveyard and the spiral hill under the moon: moonlit blue, the moon a big pale glow over the porch,
        the curl of the hill as a paler hump on Left, and grey headstones."""
        fr = light(NIGHT, 0.35 * lv * np.ones(self.N))
        fr += light(MOON, 0.85 * lv * moon * self.blob(self.mid, 70))
        fr += light(MOON, 0.25 * lv * moon * self.blob(self.mid, 220))
        h = self.at('Left', 0.45)
        curl = 0.5 + 0.5 * np.cos((self.d - h) / 18.0)
        fr += light(ICE, 0.4 * lv * hill * self.blob(h, 120) * (0.6 + 0.4 * curl))
        stones = (self.G.pi % 23 == 7) & ~self.porch
        fr += light(GREY, 0.45 * lv * stones)
        return fr

    def lair(self, t, lv=1.0):
        """The boogeyman's lair under the town: blacklight violet, green glow pulsing."""
        fr = light(UV, 0.5 * lv * np.ones(self.N))
        g = 0.5 + 0.5 * np.sin(2 * np.pi * (self.d / 300.0 - 0.4 * t))
        fr += light(SLIME, 0.35 * lv * g ** 3)
        return fr

    def fog(self, t, density=1.0, seed=5):
        """Grey fog rolling along the roof."""
        m = 0.5 + 0.5 * drift(seed, self.d - 25 * t, 140.0)
        return light(GREY, 0.55 * density * (0.4 + 0.6 * m))

    def burst(self, hits, t, seed=0, n=14, reach=1.0, colors=(WHITE,)):
        """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline -> (N,3) PWM."""
        out = np.zeros((self.N, 3))
        for i, (th, s, p0) in enumerate(hits):
            a = t - th
            if not 0 <= a < 1.6:
                continue
            rng = np.random.default_rng(seed * 1000 + i)
            v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
            ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
            life = np.exp(-a / rng.uniform(0.35, 0.9, n))
            for j in range(n):
                out += light(colors[j % len(colors)], s * life[j] * np.exp(-((self.d - ps[j]) / 7) ** 2))
        return out


def pulse(t, times, decay=0.18):
    """1 at each time, decaying after it: for lights that hit with the beat or the tune."""
    times = np.asarray(times)
    a = t - times[(times <= t) & (times > t - 6 * decay)]
    return float(np.exp(-a / decay).sum()) if len(a) else 0.0
