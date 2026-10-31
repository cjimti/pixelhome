"""Chef Charlie: a retelling, on one roofline, of Charlie Brown who ends up hosting Thanksgiving for his
friends, with toast, pretzels, popcorn and jelly beans cooked by his beagle on a ping-pong table in the backyard.
Shared by the scenes in homes/<home>/sequences/chef-charlie/.

It is a faithful, affectionate interpretation, not a copy: the story beats are the familiar ones, the music is our own.
The idiom is a cool West Coast jazz trio (piano, walking pizzicato bass, brushes on snare and a ride cymbal), in
swinging 4/4 or a jazz waltz, with a children's choir for the warm moments and the orchestra for the big ones. THEMES
are original tunes written for these scenes, and each comes back wherever its character does. None of them quotes or
imitates the special's own music; keep it that way.

    C = Chart()                                     a scene's music, laid end to end
    C.play('title', style='swing', bars=(0, 8))     a theme with its trio accompaniment, from the current time
    C.events                                        [(t, d, midi, vel, role, tag)] for render() and score()
    B = Band(M); B.perform(C.events, parts); B.finish()      in score(): the trio (and friends) play the chart

    S = Stage(G)                                    distances, runs, pans, backdrops, the characters, big looks
    S.boy(fr, p, lvl, facing)                       characters drawn at path distance p (see the methods)

homes/<home>/sequences/chef-charlie/the_kick.py is the reference scene: copy its shape.
"""
import numpy as np
from .audio import note, slide as _slide_sig
from .fx import hexc, light, perc, smoothstep, Flicker

# ---------------------------------------------------------------------------------------------------- colours

YELLOW = hexc('#ffb800')            # Charlie Brown's shirt (a black zigzag across it: dark pixels)
SKIN = hexc('#ff9a5c')              # faces read as a warm peach on a pixel
WHITE = hexc('#ffffff')
BEAGLE = hexc('#fff2e0')            # Snoopy's white (a black ear: a dark pixel)
BIRD = hexc('#ffe400')              # Woodstock, brighter and greener than the boy's shirt
GREEN = hexc('#10e028')             # Peppermint Patty's shirt
STRIPE = hexc('#ff0a10')            # Linus's red-striped shirt
BLANKET = hexc('#1048ff')           # and his blue blanket
GLASSES = hexc('#ff6400')           # Marcie' orange
DRESS = hexc('#3a8cff')             # Lucy's blue dress (paler than the blanket)
PINK = hexc('#ff3c8c')              # Sally's dress
CAP = hexc('#e01020')               # Franklin
HAIR = hexc('#7a2a08')              # brown hair
BLOND = hexc('#ffd040')
RED = hexc('#ff0010')
ORANGE = hexc('#ff5a00')
AMBER = hexc('#ff8c00')
GOLD = hexc('#ffb000')
RUST = hexc('#d03000')
MAROON = hexc('#b00a30')
BROWN = hexc('#a04812')
BLUE = hexc('#1040ff')
VIOLET = hexc('#6a18ff')
DUSK = hexc('#3a1a9a')              # an autumn evening sky
SKY = hexc('#1a40d0')
NIGHT = hexc('#0a1478')
SUN = hexc('#ff6a08')               # a low sun
LAWN = hexc('#24b020')
TABLE = hexc('#00a848')             # the ping-pong table
BALL = hexc('#b8500e')              # the football
TOAST = hexc('#e8901a')
BUTTER = hexc('#ffe060')
POPCORN = hexc('#fff0c0')
PRETZEL = hexc('#b8600c')
TURKEY = hexc('#c05a14')
CRANBERRY = hexc('#e0002c')
SEA = hexc('#0030c8')
FOAM = hexc('#c8eeff')
ICE = hexc('#9cd0ff')
SNOW = hexc('#f4f8ff')
PINE = hexc('#008a30')
CAR = hexc('#e81818')               # Grandma's car (any colour may be passed)
WARM = hexc('#ffa848')              # a warm window, a lamp

LEAVES = (ORANGE, RED, GOLD, RUST, AMBER, MAROON)
JELLY = (RED, ORANGE, BIRD, GREEN, BLUE, VIOLET, PINK, WHITE)

# ---------------------------------------------------------------------------------------------------- themes
# Each theme: meter (beats a bar), bpm, swing (eighths swung), melody [(beat, beats, note)] and chords
# [(beat, beats, symbol)], beats counted from its first bar. All original, written for these scenes; melodies sit in
# the middle register (about C4..F5) because the show plays outdoors to the street.

THEMES = {
    'title': dict(meter=4, bpm=152, swing=True, name='Main title: a bright medium swing, F major, 8 bars',
        melody=[(0, 1.5, 'A4'), (1.5, .5, 'G4'), (2, .5, 'F4'), (2.5, .5, 'A4'), (3, 1, 'C5'),
                (4, .5, 'D5'), (4.5, .5, 'C5'), (5, .5, 'Ab4'), (5.5, 1.5, 'F4'), (7, .5, 'G4'), (7.5, .5, 'Ab4'),
                (8, 1, 'A4'), (9, .5, 'C5'), (9.5, .5, 'E5'), (10, .5, 'D5'), (10.5, .5, 'C5'), (11, 1, 'F#4'),
                (12, .5, 'G4'), (12.5, .5, 'Bb4'), (13, .5, 'D5'), (13.5, .5, 'F5'), (14, .5, 'E5'), (14.5, .5, 'C5'),
                (15, .5, 'Bb4'), (15.5, .5, 'G4'),
                (16, 1.5, 'A4'), (17.5, .5, 'C5'), (18, 1, 'E5'), (19, 1, 'C5'),
                (20, .5, 'Eb5'), (20.5, .5, 'Db5'), (21, 1, 'Bb4'), (22, .5, 'C5'), (22.5, .5, 'A4'), (23, 1, 'F#4'),
                (24, .5, 'G4'), (24.5, .5, 'A4'), (25, .5, 'Bb4'), (25.5, .5, 'B4'), (26, .5, 'C5'), (26.5, .5, 'D5'),
                (27, 1, 'E5'),
                (28, 1, 'F5'), (29, .5, 'D5'), (29.5, .5, 'C5'), (30, 2, 'F4')],
        chords=[(0, 4, 'Fmaj7'), (4, 4, 'Bb7'), (8, 2, 'Am7'), (10, 2, 'D7'), (12, 2, 'Gm7'), (14, 2, 'C7'),
                (16, 4, 'Fmaj7'), (20, 2, 'Eb7'), (22, 2, 'D7'), (24, 2, 'Gm7'), (26, 2, 'C7'), (28, 4, 'F6')]),
    'boy': dict(meter=4, bpm=100, swing=True, name='Charlie Brown: wistful, a sigh in every bar, E flat major',
        melody=[(0, 1.5, 'G4'), (1.5, .5, 'F4'), (2, 2, 'Eb4'),
                (4, .5, 'G4'), (4.5, .5, 'Bb4'), (5, 1.5, 'D5'), (6.5, .5, 'C5'), (7, 1, 'Bb4'),
                (8, 1.5, 'Ab4'), (9.5, .5, 'G4'), (10, 1, 'F4'), (11, 1, 'C5'),
                (12, 3, 'Bb4'), (15, .5, 'Ab4'), (15.5, .5, 'G4'),
                (16, 1.5, 'F4'), (17.5, .5, 'G4'), (18, 1, 'Bb4'), (19, 1, 'D5'),
                (20, 1.5, 'E5'), (21.5, .5, 'D5'), (22, 2, 'Bb4'),
                (24, 1, 'C5'), (25, .5, 'Ab4'), (25.5, .5, 'F4'), (26, 1, 'D4'), (27, 1, 'Ab4'),
                (28, 4, 'G4')],
        chords=[(0, 4, 'Ebmaj7'), (4, 4, 'Cm7'), (8, 4, 'Fm7'), (12, 4, 'Bb7'), (16, 4, 'Gm7'), (20, 4, 'C7'),
                (24, 2, 'Fm7'), (26, 2, 'Bb7'), (28, 4, 'Ebmaj7')]),
    'beagle': dict(meter=4, bpm=120, swing=True, name="Snoopy's strut: jaunty, chromatic, C major",
        melody=[(0, .5, 'C4'), (.5, .5, 'E4'), (1, .5, 'G4'), (1.5, .5, 'A4'), (2, 1, 'G4'), (3, .5, 'Eb4'),
                (3.5, .5, 'E4'),
                (4, 1, 'C#5'), (5, .5, 'A4'), (5.5, .5, 'G4'), (6, 1.5, 'E4'),
                (8, .5, 'D4'), (8.5, .5, 'F4'), (9, .5, 'A4'), (9.5, .5, 'C5'), (10, .5, 'B4'), (10.5, .5, 'Ab4'),
                (11, 1, 'G4'),
                (12, 1, 'E4'), (13, .5, 'G4'), (13.5, 1.5, 'C5'), (15, .5, 'G4'), (15.5, .5, 'Bb4'),
                (16, 1, 'A4'), (17, .5, 'F4'), (17.5, .5, 'A4'), (18, .5, 'C5'), (18.5, .5, 'Eb5'), (19, 1, 'D5'),
                (20, 1, 'C5'), (21, .5, 'A4'), (21.5, .5, 'F#4'), (22, 1, 'Eb4'), (23, 1, 'C4'),
                (24, .5, 'D4'), (24.5, .5, 'F4'), (25, .5, 'A4'), (25.5, .5, 'C5'), (26, .5, 'B4'), (26.5, .5, 'G4'),
                (27, .5, 'F4'), (27.5, .5, 'D4'),
                (28, 1, 'G4'), (29, .5, 'E4'), (29.5, .5, 'D#4'), (30, 2, 'E4')],
        chords=[(0, 4, 'C6'), (4, 4, 'A7'), (8, 2, 'Dm7'), (10, 2, 'G7'), (12, 4, 'C6'), (16, 4, 'F7'),
                (20, 4, 'F#dim7'), (24, 2, 'Dm7'), (26, 2, 'G7'), (28, 4, 'C6')]),
    'bird': dict(meter=4, bpm=168, swing=False, name="Woodstock's twitter: quick and chirpy, G major, 4 bars",
        melody=[(0, .25, 'D5'), (.25, .25, 'D5'), (.5, .5, 'G5'), (1, .25, 'F#5'), (1.25, .25, 'G5'), (1.5, .5, 'D5'),
                (2, .5, 'B4'), (2.5, .5, 'D5'), (3, 1, 'G5'),
                (4, .25, 'E5'), (4.25, .25, 'D5'), (4.5, .25, 'C5'), (4.75, .25, 'B4'), (5, .5, 'A4'), (5.5, .5, 'C5'),
                (6, 1, 'D5'), (7, .5, 'A4'), (7.5, .5, 'C5'),
                (8, .25, 'B4'), (8.25, .25, 'C5'), (8.5, .5, 'D5'), (9, .25, 'G5'), (9.25, .25, 'G5'), (9.5, .5, 'G5'),
                (10, .5, 'E5'), (10.5, .5, 'C5'), (11, 1, 'A4'),
                (12, .25, 'D5'), (12.25, .25, 'C5'), (12.5, .25, 'B4'), (12.75, .25, 'A4'), (13, .5, 'B4'),
                (13.5, .5, 'D5'), (14, .5, 'G5'), (14.5, .5, 'D5'), (15, 1, 'G4')],
        chords=[(0, 4, 'G6'), (4, 2, 'Cmaj7'), (6, 2, 'D7'), (8, 2, 'G6'), (10, 2, 'Am7'), (12, 2, 'D7'),
                (14, 2, 'G6')]),
    'tomboy': dict(meter=4, bpm=144, swing=True, name='Peppermint Patty: brash and bluesy, B flat, 8 bars',
        melody=[(0, .5, 'Bb4'), (.5, .5, 'Bb4'), (1, .5, 'Ab4'), (1.5, .5, 'F4'), (2, 1, 'Db4'), (3, .5, 'D4'),
                (3.5, .5, 'F4'),
                (4, 1, 'G4'), (5, .5, 'Gb4'), (5.5, .5, 'Eb4'), (6, 1.5, 'Db4'), (7.5, .5, 'Bb3'),
                (8, .5, 'Bb3'), (8.5, .5, 'D4'), (9, .5, 'F4'), (9.5, .5, 'Ab4'), (10, 1, 'Bb4'), (11, .5, 'B4'),
                (11.5, .5, 'C5'),
                (12, 1.5, 'B4'), (13.5, .5, 'G4'), (14, .5, 'F4'), (14.5, .5, 'D4'), (15, 1, 'B3'),
                (16, .5, 'C4'), (16.5, .5, 'Eb4'), (17, .5, 'G4'), (17.5, .5, 'Bb4'), (18, 1, 'C5'), (19, 1, 'G4'),
                (20, .5, 'A4'), (20.5, .5, 'Ab4'), (21, .5, 'F4'), (21.5, .5, 'Eb4'), (22, 1, 'C4'), (23, .5, 'A3'),
                (23.5, .5, 'C4'),
                (24, 1, 'D4'), (25, 1, 'Bb3'), (26, .5, 'B3'), (26.5, .5, 'D4'), (27, 1, 'F4'),
                (28, .5, 'Eb4'), (28.5, .5, 'C4'), (29, 1, 'G4'), (30, .5, 'A4'), (30.5, 1.5, 'Bb4')],
        chords=[(0, 4, 'Bb7'), (4, 4, 'Eb7'), (8, 4, 'Bb7'), (12, 4, 'G7'), (16, 4, 'Cm7'), (20, 4, 'F7'),
                (24, 2, 'Bb7'), (26, 2, 'G7'), (28, 2, 'Cm7'), (30, 2, 'F7')]),
    'blanket': dict(meter=3, bpm=132, swing=True, name='Linus: a gentle jazz waltz, G major, 16 bars',
        melody=[(0, 2, 'B4'), (2, 1, 'A4'), (3, 1, 'G4'), (4, 1, 'E4'), (5, 1, 'D4'), (6, 2, 'C5'), (8, 1, 'B4'),
                (9, 3, 'A4'),
                (12, 1, 'D5'), (13, 1, 'C#5'), (14, 1, 'B4'), (15, 2, 'G#4'), (17, 1, 'B4'), (18, 1, 'C5'),
                (19, 1, 'E5'), (20, 1, 'D5'), (21, 3, 'C5'),
                (24, 2, 'B4'), (26, 1, 'D5'), (27, 1, 'F5'), (28, 1, 'E5'), (29, 1, 'D5'), (30, 2, 'E5'), (32, 1, 'G4'),
                (33, 2, 'Eb5'), (35, 1, 'A4'),
                (36, 1, 'D5'), (37, 1, 'B4'), (38, 1, 'F#4'), (39, 2, 'G#4'), (41, 1, 'D5'), (42, 1, 'C5'),
                (43, 1, 'A4'), (44, 1, 'F#4'), (45, 3, 'G4')],
        chords=[(0, 3, 'Gmaj7'), (3, 3, 'Em7'), (6, 3, 'Am7'), (9, 3, 'D7'), (12, 3, 'Bm7'), (15, 3, 'E7'),
                (18, 3, 'Am7'), (21, 3, 'D7'), (24, 3, 'Gmaj7'), (27, 3, 'G7'), (30, 3, 'Cmaj7'), (33, 3, 'Cm6'),
                (36, 3, 'Bm7'), (39, 3, 'E7'), (42, 3, 'D7'), (45, 3, 'G6')]),
    'football': dict(meter=4, bpm=132, swing=True,
        name='The football: a teasing figure that climbs a step every two bars, A minor; bar 6 is the held breath',
        melody=[(0, .5, 'E4'), (.5, .5, 'G4'), (1, .5, 'A4'), (1.5, 1, 'C5'), (2.5, .5, 'A4'), (3, 1, 'F#4'),
                (4, .5, 'E4'), (4.5, .5, 'G4'), (5, .5, 'A4'), (5.5, .5, 'C5'), (6, .5, 'E5'), (6.5, .5, 'D5'),
                (7, 1, 'C5'),
                (8, .5, 'F#4'), (8.5, .5, 'A4'), (9, .5, 'B4'), (9.5, 1, 'D5'), (10.5, .5, 'B4'), (11, 1, 'G#4'),
                (12, .5, 'F#4'), (12.5, .5, 'A4'), (13, .5, 'B4'), (13.5, .5, 'D5'), (14, .5, 'F#5'), (14.5, .5, 'E5'),
                (15, 1, 'D5'),
                (16, .5, 'G#4'), (16.5, .5, 'B4'), (17, .5, 'C#5'), (17.5, 1, 'E5'), (18.5, .5, 'C#5'), (19, 1, 'A#4'),
                (20, .5, 'A4'), (20.5, .5, 'C5'), (21, .5, 'D5'), (21.5, .5, 'F5'), (22, .5, 'E5'), (22.5, .5, 'D5'),
                (23, 1, 'B4'),
                (24, 3, 'G#4'), (27, .5, 'B4'), (27.5, .5, 'D5'),
                (28, 1, 'Eb5'), (29, 1, 'C5'), (30, 2, 'E5')],
        chords=[(0, 2, 'Am7'), (2, 2, 'D7'), (4, 2, 'Am7'), (6, 2, 'D7'), (8, 2, 'Bm7'), (10, 2, 'E7'), (12, 2, 'Bm7'),
                (14, 2, 'E7'), (16, 2, 'C#m7'), (18, 2, 'F#7'), (20, 2, 'Dm7'), (22, 2, 'G7'), (24, 4, 'E7'),
                (28, 2, 'F7'), (30, 2, 'E7')]),
    'grandma': dict(meter=4, bpm=108, swing=True, name="Grandma's: warm and homey, a hymn with a lilt, F major",
        melody=[(0, 1, 'C4'), (1, 1, 'F4'), (2, 1.5, 'A4'), (3.5, .5, 'G4'),
                (4, 1, 'F4'), (5, 1, 'D4'), (6, 2, 'Bb4'),
                (8, 1, 'A4'), (9, .5, 'C5'), (9.5, .5, 'A4'), (10, 2, 'F4'),
                (12, 1, 'G4'), (13, 1, 'Bb4'), (14, 1.5, 'E4'), (15.5, .5, 'G4'),
                (16, 1.5, 'A4'), (17.5, .5, 'C5'), (18, 2, 'E5'),
                (20, 1, 'D5'), (21, 1, 'C5'), (22, 1, 'Db5'), (23, 1, 'Bb4'),
                (24, 1, 'A4'), (25, 1, 'G4'), (26, 1, 'Bb4'), (27, 1, 'E4'),
                (28, 4, 'F4')],
        chords=[(0, 4, 'Fmaj7'), (4, 4, 'Bbmaj7'), (8, 2, 'Am7'), (10, 2, 'Dm7'), (12, 2, 'Gm7'), (14, 2, 'C7'),
                (16, 4, 'Fmaj7'), (20, 2, 'Bbmaj7'), (22, 2, 'Bbm6'), (24, 2, 'Gm7'), (26, 2, 'C7'), (28, 4, 'F6')]),
    'feast': dict(meter=4, bpm=184, swing=True, name='The feast: up-tempo and joyful, call and answer, D major',
        melody=[(0, .5, 'F#4'), (.5, .5, 'A4'), (1, .5, 'B4'), (1.5, .5, 'D5'), (2, 1, 'D#5'), (3, 1, 'B4'),
                (4, .5, 'E5'), (4.5, .5, 'D5'), (5, .5, 'B4'), (5.5, .5, 'G4'), (6, 1, 'C#5'), (7, 1, 'A4'),
                (8, .5, 'F#4'), (8.5, .5, 'A4'), (9, .5, 'B4'), (9.5, .5, 'D5'), (10, 1, 'F#5'), (11, 1, 'D#5'),
                (12, .5, 'E5'), (12.5, .5, 'G5'), (13, .5, 'E5'), (13.5, .5, 'C#5'), (14, 1.5, 'A4'), (15.5, .5, 'C5'),
                (16, 1.5, 'B4'), (17.5, .5, 'G4'), (18, .5, 'F4'), (18.5, .5, 'D4'), (19, 1, 'B3'),
                (20, .5, 'A3'), (20.5, .5, 'D4'), (21, .5, 'F#4'), (21.5, .5, 'A4'), (22, 1, 'B4'), (23, 1, 'A4'),
                (24, .5, 'G#4'), (24.5, .5, 'B4'), (25, .5, 'D5'), (25.5, .5, 'E5'), (26, .5, 'G5'), (26.5, .5, 'E5'),
                (27, .5, 'C#5'), (27.5, .5, 'A4'),
                (28, 1, 'D5'), (29, .5, 'B4'), (29.5, .5, 'A4'), (30, 2, 'D5')],
        chords=[(0, 2, 'D6'), (2, 2, 'B7'), (4, 2, 'Em7'), (6, 2, 'A7'), (8, 2, 'D6'), (10, 2, 'B7'), (12, 2, 'Em7'),
                (14, 2, 'A7'), (16, 4, 'G7'), (20, 4, 'D6'), (24, 2, 'E7'), (26, 2, 'A7'), (28, 4, 'D6')]),
}

QUALITY = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10), 'm7': (0, 3, 7, 10), 'maj7': (0, 4, 7, 11),
           'dim': (0, 3, 6), 'dim7': (0, 3, 6, 9), 'aug': (0, 4, 8), 'm6': (0, 3, 7, 9), '6': (0, 4, 7, 9),
           'sus4': (0, 5, 7), '7sus4': (0, 5, 7, 10), 'm7b5': (0, 3, 6, 10), '9': (0, 4, 7, 10, 14),
           'maj9': (0, 4, 7, 11, 14), 'm9': (0, 3, 7, 10, 14), '7b9': (0, 4, 7, 10, 13), '13': (0, 4, 7, 10, 21),
           '7#9': (0, 4, 7, 10, 15)}


def chord(sym):
    """'F#m7' -> (root pitch class, intervals)."""
    root = sym[:2] if len(sym) > 1 and sym[1] in '#b' else sym[:1]
    return note(root + '4') % 12, QUALITY[sym[len(root):]]


def voicing(sym, low=52, rootless=True):
    """The chord as a jazz pianist's left hand would comp it, close within an octave from low (E3 by default):
    four-note chords drop the root and add the ninth (third, fifth, seventh, ninth), the cool trio sound; triads keep
    all three tones. rootless=False keeps the root."""
    pc, iv = chord(sym)
    tones = list(iv)
    if rootless and len(tones) >= 4:
        tones = [i for i in tones if i % 12 != 0]
        if not any(i in (13, 14, 15) for i in tones) and 'dim' not in sym:
            tones.append(14)
    return sorted({low + (pc + i - low) % 12 for i in tones})


def bass_note(sym, fifth=False, low=36):
    """The chord's root (or fifth) for the upright bass, C2..B2 (sounding)."""
    pc, iv = chord(sym)
    return low + (pc + (iv[2] if fifth else 0) - low) % 12


def _swing(b):
    """Swung eighths: the off-beat eighth moves from half to two thirds of the beat."""
    whole = np.floor(b + 1e-9)
    f = b - whole
    return whole + np.where(f < 0.5, f * 4 / 3, 2 / 3 + (f - 0.5) * 2 / 3)


# comping rhythms, one per bar in turn: (offset in beats, length in beats). The off-beat eighths get swung.
_COMP4 = [[(0, .9), (1.5, .4)], [(1, .4), (2.5, 1.2)], [(0, .4), (1.5, .4), (3, .4)], [(.5, .4), (2, 1.0)]]
_COMP3 = [[(1, .6), (2, .6)], [(1.5, .4), (2.5, .4)], [(1, .9)], [(.5, .4), (2, .8)]]


def _accompany(chords, meter, style, b0, b1):
    """The trio's accompaniment for beats b0..b1 of a theme. Yields (beat, beats, midi or None, vel, role):
    roles 'bass', 'comp', 'hit', 'hold', 'pedal', 'arp', and the drums 'brush', 'tap', 'ride', 'kick' (midi None)."""
    chords = sorted(chords)

    def at(b):
        for i, (cb, cl, sym) in enumerate(chords):
            if cb <= b + 1e-6 < cb + cl:
                return i
        return len(chords) - 1

    out = []
    prev = None
    for b in np.arange(float(b0), float(b1), 1.0):
        i = at(b)
        cb, cl, sym = chords[i]
        nxt = chords[i + 1][2] if i + 1 < len(chords) else chords[0][2]
        k = int(round(b)) % meter
        bar = int(round(b)) // meter
        first = abs(b - cb) < 1e-6
        last = b + 1 >= cb + cl - 1e-6                      # the beat before the chord changes
        root = bass_note(sym)
        pc, iv = chord(sym)

        def walk():
            nonlocal prev
            if first:
                m = root
            elif last:
                target = bass_note(nxt)
                up = (prev or root) > target if prev is not None else bar % 2 == 0
                m = target + (1 if up else -1)
            else:
                j = int(round(b - cb))
                tones = [0, iv[1], iv[2], iv[3] if len(iv) > 3 and iv[3] < 12 else 9]
                m = root + tones[j % 4]
            while m > 52:
                m -= 12
            prev = m
            return m

        if style == 'swing':                                # walking bass, comping, brushes and ride
            out.append((b, .9, walk(), 92 + 6 * (k == 0), 'bass'))
            if k == 0:
                for off, ln in (_COMP4 if meter == 4 else _COMP3)[bar % 4]:
                    s = sym if off < cl - (b - cb) else nxt
                    out += [(b + off, ln, m, 70 + 6 * (off == 0), 'comp') for m in voicing(s)]
            out.append((b, .9, None, 64, 'brush'))
            if k % 2 == 1:
                out.append((b, .2, None, 74, 'tap'))
            out.append((b, .3, None, 70 + 8 * (k % 2), 'ride'))
            if k % 2 == 1:
                out.append((b + .5, .2, None, 58, 'ride'))  # the skip: ding, ding-a ding
            if k == 0:
                out.append((b, .2, None, 40, 'kick'))
        elif style == 'two':                                # two-feel: bass on 1 and 3, light comping, brushes
            if k % 2 == 0:
                m = root if k == 0 or first else bass_note(sym, fifth=True)
                if last and not first:
                    m = bass_note(nxt) + (1 if bar % 2 else -1)
                out.append((b, 1.8, m, 92, 'bass'))
            if k == 0:
                for off, ln in [(1.5, .5), (3, .5)] if bar % 2 else [(0, 1.5), (2.5, .5)]:
                    s = sym if off < cl - (b - cb) else nxt
                    out += [(b + off, ln, m, 64, 'comp') for m in voicing(s)]
            out.append((b, 1.0, None, 58, 'brush'))
            if k % 2 == 1:
                out.append((b, .2, None, 66, 'tap'))
            out.append((b, .3, None, 60, 'ride'))
        elif style == 'waltz':                              # jazz waltz: bass on 1 and an approach on 3
            if k == 0:
                out.append((b, 1.8, root if first else bass_note(sym, fifth=True), 90, 'bass'))
            elif k == meter - 1:
                if last:
                    target = bass_note(nxt)
                    out.append((b, .9, target + (1 if bar % 2 else -1), 82, 'bass'))
                else:
                    out.append((b, .9, bass_note(sym, fifth=True), 80, 'bass'))
            if k == 0:
                for off, ln in _COMP3[bar % 4]:
                    s = sym if off < cl - (b - cb) else nxt
                    out += [(b + off, ln, m, 64, 'comp') for m in voicing(s)]
            out.append((b, .9, None, 56 + 8 * (k == 0), 'brush'))
            if k == 1:
                out.append((b, .2, None, 60, 'tap'))
            out.append((b, .3, None, 60, 'ride'))
            if k == 2:
                out.append((b + .5, .2, None, 50, 'ride'))
        elif style == 'ballad':                             # half-time: long chords, bass on 1 and 3, swirled brushes
            if k % 2 == 0:
                out.append((b, 1.9, root if (k == 0 or first) else bass_note(sym, fifth=True), 80, 'bass'))
            if first:
                out += [(b, cl, m, 60, 'comp') for m in voicing(sym)]
            if k % 2 == 0:
                out.append((b, 2.0, None, 50, 'brush'))
            if k == meter - 1:
                out.append((b, .2, None, 46, 'tap'))
        elif style == 'drive':                              # double-time for chases: walking eighths, stabs, ride eighths
            m = walk()
            out.append((b, .45, m, 100, 'bass'))
            out.append((b + .5, .4, m + 7 if not last else m, 84, 'bass'))
            out += [(b + (.5 if k % 2 else 0), .3, v, 78, 'comp') for v in voicing(sym)]
            out.append((b, .2, None, 82 + 12 * (k % 2), 'tap'))
            out.append((b + .5, .2, None, 52, 'tap'))
            out.append((b, .3, None, 78, 'ride'))
            out.append((b + .5, .3, None, 64, 'ride'))
            out.append((b, .2, None, 70, 'kick'))
        elif style == 'stop':                               # stop-time: one hit on each bar's downbeat, the tune alone
            if k == 0:
                out += [(b, .5, m, 104, 'hit') for m in voicing(sym)]
                out.append((b, .5, root, 108, 'bass'))
                out.append((b, .2, None, 110, 'tap'))
                out.append((b, .2, None, 100, 'kick'))
        elif style == 'walk':                               # bass and drums only: the piano lays out
            out.append((b, .9, walk(), 92 + 6 * (k == 0), 'bass'))
            out.append((b, .9, None, 62, 'brush'))
            if k % 2 == 1:
                out.append((b, .2, None, 70, 'tap'))
            out.append((b, .3, None, 68, 'ride'))
            if k % 2 == 1:
                out.append((b + .5, .2, None, 54, 'ride'))
        elif style == 'brushes':                            # drums alone: a count-in, a hush, a vamp to talk over
            out.append((b, .9, None, 60, 'brush'))
            if k % 2 == 1 or meter == 3 and k == 1:
                out.append((b, .2, None, 64, 'tap'))
            out.append((b, .3, None, 58, 'ride'))
        elif style == 'march':                              # a parade two-step: oom-pah and snare
            if k % 2 == 0:
                out.append((b, .5, bass_note(sym, fifth=(k == 2 and not first)), 100, 'bass'))
            else:
                out += [(b, .4, m, 80, 'comp') for m in voicing(sym, rootless=False)]
            out.append((b, .2, None, 84 if k % 2 else 60, 'tap'))
            out.append((b + .5, .2, None, 56, 'tap'))
        elif style == 'arp':                                # broken chords an eighth apart (vibes, celesta) and a pedal
            tones = voicing(sym, 60, rootless=False)
            for j in range(2):
                out.append((b + .5 * j, .5, tones[(2 * k + j) % len(tones)], 70, 'arp'))
            if first:
                out.append((b, cl, root, 76, 'pedal'))
        elif style == 'hold':                               # long chords and a pedal bass
            if first:
                out += [(b, cl, m, 66, 'hold') for m in voicing(sym, 55, rootless=False)]
                out.append((b, cl, root, 72, 'pedal'))
        else:
            raise ValueError(f'unknown style {style!r}')
    return out


class Chart:
    """A scene's music laid end to end: themes and their accompaniment, rests, and the times everything lands.

    events are (t, d, midi or None, vel, role, tag). role is 'tune' (the melody), 'bass' (walking upright bass),
    'comp' (piano chords), 'hit' (stop-time stabs), 'hold' and 'pedal' (long chords), 'arp' (broken chords), or a drum:
    'brush' (a brush swish), 'tap' (brush on the snare), 'ride' (ride cymbal), 'kick' (a feathered bass drum); drums
    have midi None. tag is whatever the scene passed (the theme's name by default) so render() can find its moments.
    beats lists (t, beat in bar, tag) for every beat played. marks holds the scene's named times (mark()).

    Styles: 'swing' (walking bass, comping, brushes, ride), 'two' (two-feel), 'waltz' (jazz waltz, for 3/4 themes),
    'ballad' (half-time, long chords), 'drive' (double-time, for chases and run-ups), 'stop' (stop-time: one hit a
    bar under the tune; the tension before a payoff), 'walk' (bass and drums, the piano lays out), 'brushes' (drums
    alone), 'march' (a parade two-step), 'arp' (broken chords), 'hold' (long chords)."""

    def __init__(self, start=0.0):
        self.t = start
        self.events, self.beats, self.marks = [], [], {}

    def play(self, theme, style='swing', bars=None, bpm=None, transpose=0, tune=True, tag=None, vel=96, octave=0):
        """Play bars (first, last) of a theme from now, its tune (unless tune=False) over style. theme is a name in
        THEMES or a dict of the same shape (a scene's own tune, e.g. a public-domain song). transpose moves
        everything; octave moves only the tune. Returns (t0, seconds a beat)."""
        th = THEMES[theme] if isinstance(theme, str) else theme
        meter, beat = th['meter'], 60.0 / (bpm or th['bpm'])
        a, b = bars if bars else (0, int(np.ceil(max(x[0] + x[1] for x in th['melody']) / meter)))
        b0, b1 = a * meter, b * meter
        sw = _swing if th.get('swing') else (lambda x: x)
        tag = tag or (theme if isinstance(theme, str) else th.get('id', 'tune'))
        t0 = self.t - b0 * beat
        if tune:
            for mb, ml, n in th['melody']:
                if b0 <= mb < b1:
                    s = float(sw(mb))
                    self.events.append((t0 + s * beat, ml * beat, note(n) + transpose + 12 * octave, vel, 'tune', tag))
        for sb, sl, m, v, role in _accompany(th['chords'], meter, style, b0, b1):
            s = float(sw(sb))
            self.events.append((t0 + s * beat, sl * beat, None if m is None else m + transpose, v, role, tag))
        for k in range(b0, b1):
            self.beats.append((t0 + k * beat, k % meter, tag))
        self.t = t0 + b1 * beat
        return t0 + b0 * beat, beat

    def button(self, sym, bpm=120, beats=2, tag='button', vel=110, transpose=0):
        """A final chord, the trio's last word: piano stab ('hit'), bass root, a snare and kick, held beats long.
        Returns its time."""
        t, beat = self.t, 60.0 / bpm
        self.events += [(t, beats * beat, m + transpose, vel, 'hit', tag) for m in voicing(sym, rootless=False)]
        self.events.append((t, beats * beat, bass_note(sym) + transpose, vel, 'bass', tag))
        self.events += [(t, .2, None, vel, 'tap', tag), (t, .2, None, vel, 'kick', tag)]
        self.beats.append((t, 0, tag))
        self.t += beats * beat
        return t

    def rest(self, seconds):
        self.t += seconds
        return self.t

    def mark(self, name):
        self.marks[name] = self.t
        return self.t

    def tunes(self, tag=None):
        """The tune's notes (t, d, midi) in time order, of one tag or all."""
        return sorted((e[0], e[1], e[2]) for e in self.events if e[4] == 'tune' and (tag is None or e[5] == tag))

    def times(self, role, tag=None):
        """Sorted distinct times of a role's events (e.g. 'bass', 'hit', 'tap'), of one tag or all."""
        return sorted({round(e[0], 4) for e in self.events if e[4] == role and (tag is None or e[5] == tag)})

    def beat_times(self, tag=None):
        return [t for t, k, g in self.beats if tag is None or g == tag]

    def downbeats(self, tag=None):
        return [t for t, k, g in self.beats if k == 0 and (tag is None or g == tag)]


def pulse(t, times, decay=0.18):
    """1 at each time, decaying after it: for lights that hit with the beat or the tune."""
    times = np.asarray(times, float)
    a = t - times[(times <= t) & (times > t - 6 * decay)]
    return float(np.exp(-a / decay).sum()) if len(a) else 0.0


def popcorn_times(t0, t1, rate, seed=6):
    """Kernels popping between t0 and t1: rate pops a second, a number or rate(u) for u 0..1 across the span (start
    slow, a storm, a last few). The same list drives the lights (Stage.popcorn) and the sound (Band.popcorn)."""
    rng = np.random.default_rng(seed)
    out, t = [], t0
    while t < t1:
        r = rate((t - t0) / max(t1 - t0, 1e-6)) if callable(rate) else rate
        t += rng.exponential(1.0 / max(r, 0.05))
        if t < t1:
            out.append(float(t))
    return out


# ---------------------------------------------------------------------------------------------------- sound design
# Small numpy sounds the band and the intro beds share. Each returns mono float arrays at audio.SR, peak about 1.

def _noise(n, lo, hi, seed):
    from .audio import SR
    f = np.fft.rfftfreq(n, 1 / SR)
    spec = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, n))
    spec *= (f >= lo) & (f <= hi)
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def brush_swish(seed=0, seconds=0.32):
    """A brush swept across the snare head: a soft rise and a hiss that fades."""
    from .audio import SR
    n = int(seconds * SR)
    tt = np.arange(n) / SR
    env = np.clip(tt / 0.05, 0, 1) ** 1.5 * np.exp(-np.maximum(tt - 0.05, 0) / 0.11)
    swirl = 1 + 0.25 * np.sin(2 * np.pi * (9 + seed % 3) * tt)
    x = _noise(n, 1800, 9000, 100 + seed) * env * swirl
    return x / (np.abs(x).max() + 1e-9)


def brush_tap(seed=0):
    """A brush slapped on the snare on 2 and 4: a papery crack with a little drum body under it."""
    from .audio import SR
    n = int(0.16 * SR)
    tt = np.arange(n) / SR
    x = _noise(n, 700, 7500, 200 + seed) * np.exp(-tt / 0.045)
    x += 0.35 * np.sin(2 * np.pi * 185 * tt) * np.exp(-tt / 0.03)
    return x / (np.abs(x).max() + 1e-9)


def snare_roll(seconds, seed=0, crescendo=True):
    """A brush roll on the snare, seconds long, building (crescendo) or even."""
    from .audio import SR
    n = int(seconds * SR)
    out = np.zeros(n)
    tap = brush_tap(seed)
    rng = np.random.default_rng(300 + seed)
    for t in np.arange(0, seconds, 1 / 26):
        k = int((t + rng.uniform(0, 0.006)) * SR)
        a = (0.25 + 0.75 * t / seconds) if crescendo else 0.6
        m = min(len(tap), n - k)
        if m > 0:
            out[k:k + m] += tap[:m] * a * rng.uniform(0.6, 1.0)
    return out / (np.abs(out).max() + 1e-9)


def _place(out, sig, t, gain=1.0):
    from .audio import SR
    k = int(round(t * SR))
    if k < 0:
        sig, k = sig[-k:], 0
    m = min(len(sig), len(out) - k)
    if m > 0:
        out[k:k + m] += sig[:m] * gain
    return out


def _voice(f, seconds, vowel=(800, 1200), seed=0):
    """A child's voice: a buzzy glottal tone following f (Hz per sample) through two vowel formants."""
    from .audio import SR
    n = len(f)
    ph = 2 * np.pi * np.cumsum(f) / SR
    src = sum(np.sin(k * ph) / k for k in range(1, 14))
    src += 0.05 * np.random.default_rng(seed).normal(0, 1, n)
    spec = np.fft.rfft(src)
    fr = np.fft.rfftfreq(n, 1 / SR)
    shape = sum(np.exp(-((fr - fv) / (90 + 0.12 * fv)) ** 2) * g for fv, g in zip(vowel, (1.0, 0.7)))
    shape += 0.15 * np.exp(-((fr - 2800) / 600) ** 2)
    x = np.fft.irfft(spec * shape, n)
    return x / (np.abs(x).max() + 1e-9)


# ---------------------------------------------------------------------------------------------------- the band

EXTRA = {
    'bass': (None, 'Strings/Solo Contrabass/Pizz/*.wav', 'bass', 0.05),
    'pizz': (None, 'Strings/Violin Section/Pizz/*.wav', 'strings', 0.3),
    'cellos pizz': (None, 'Strings/Cello Section/pizzT/*.wav', 'low', -0.25),
    'xylo': (None, 'Percussion/Xylo/*.wav', 'perc', 0.1),
    'marimba': (None, 'Percussion/Marimba/*.wav', 'perc', -0.1),
    'muted horn': ('Brass/F Horn/mute/*.wav', None, 'brass', -0.3),
    'harmon trumpet': ('Brass/Trumpet/harmonM-sus/*.wav', None, 'brass', 0.2),
    'buzz trombone': ('Brass/OldTrombone/Buzz/*.wav', None, 'brass', 0.1),
    'trombone fall': (None, 'Brass/OldTrombone/Fall/*.wav', 'brass', 0.1),
}
HITS = {'snare': 'Percussion/Snare2-HitSN_v[3579]*.wav', 'snare roll': 'Percussion/Snare2-rollSN_v[35]*.wav',
        'ride': 'Percussion/susCymb1-hitstick_pp*.wav', 'ride accent': 'Percussion/susCymb1-hitstick_mp*.wav',
        'kick': 'Percussion/BDrumNewhit_v[23]*.wav', 'taps': 'Percussion/Snare2-taps_v[12]*.wav',
        'sleigh': 'Percussion/Sleighbells_Hit*.wav', 'slapstick': 'VSCO 1 Percussion/varWood/slapstick[0-9].wav',
        'wood': 'VSCO 1 Percussion/varWood/wood_click*.wav', 'ratchet': 'Percussion/Ratchet1-Crank*.wav',
        'bell tree': 'Percussion/BellTree_Stroke*.wav', 'claves': 'Percussion/Claves1_Hit*.wav',
        'tambourine': 'Percussion/Tamb1-Hit*.wav', 'guiro': 'Percussion/Guiro-Hit*.wav',
        'cowbell': 'Percussion/Cowbell1_Hit*.wav', 'vibraslap': 'VSCO 1 Percussion/varWood/vibraslap1.wav',
        'woodblock': 'Percussion/LogDrumHi_MedM_v[23]*.wav', 'agogo': 'VSCO 1 Percussion/varMetal/various/agogoBell*.wav',
        'maraca': 'VSCO 1 Percussion/varWood/maraca[1-5].wav'}
SYNTHS = {'ep': 'Keys/EP 1', 'vibes': 'Keys/DX EP', 'choir': 'Pads/Ooh', 'oo-ah': 'Pads/Synth Choir MW O-Ah',
          'celesta': 'Plucks/Magic Music Box', 'organ': 'Keys/House Organ'}
PIANO = 'Keys/Upright Nr1/*_{}_*.wav'           # VS Upright No. 1: real piano, named notes every C and G, 3 dynamics
DRUMS = ('brush', 'tap', 'roll', 'chick')       # synthesized brushes (see brush_swish, brush_tap)
BUSES = (('keys', 0.15, 0.22), ('bass', 0.17, 0.1), ('drums', 0.4, 0.18))
LOUD = 2.2                                      # Band(level=1.0) lands a trio scene near -15.5 dBFS rms

# what each role of a chart plays on by default; a scene passes parts={role or (tag, role): [(section, transpose,
# velocity change, gain)]} to change any of it (an empty list is silence)
DEFAULT = {'tune': [('piano', 0, 0, 0.8)], 'comp': [('piano', 0, -8, 0.5)], 'hit': [('piano', 0, 0, 0.75)],
           'bass': [('bass', 0, 0, 0.8)], 'hold': [('choir', 0, -10, 0.5)], 'pedal': [('bass', 0, -8, 0.6)],
           'arp': [('vibes', 0, 0, 0.5)], 'brush': [('brush', 0, 0, 0.45)], 'tap': [('tap', 0, 0, 0.5)],
           'ride': [('ride', 0, 0, 0.35)], 'kick': [('kick', 0, 0, 0.35)]}


class Band:
    """The cool jazz trio and everything a staging adds, on top of the Ring's orchestra (pixelhome/ring.py: violins,
    violas, cellos, basses, horns, trumpets, trombones, tuba, flutes, piccolo, oboes, clarinets, bassoons, harp, glock,
    timpani, crash, gong... and its effects: thunder, wind, fire, boom, clash, whoosh via whoosh()).

    The trio: 'piano' (a sampled upright, three dynamic layers picked by velocity), 'bass' (upright bass pizzicato),
    and the drums: 'brush' (a swish), 'tap' (brush on the snare), 'roll', 'chick' (synthesized), 'ride', 'kick'.
    Surge voices: 'ep' (an electric piano), 'vibes' (a bell-like keys patch for vibraphone lines), 'choir' (children's
    'ooh'), 'oo-ah' (a fuller choir), 'celesta' (a music box), 'organ'. Also from the samples: 'pizz', 'cellos pizz',
    'xylo', 'marimba', 'muted horn', 'harmon trumpet' (the cool trumpet), 'buzz trombone', 'trombone fall' (a
    'wah-wah' fall), and HITS (snare, slapstick, wood, woodblock, claves, cowbell, vibraslap, ratchet, sleigh,
    tambourine, maraca, bell tree, agogo, taps, guiro).

    level scales every bus (the orchestra's too), for the loudness target: level=1.0 puts a typical scene near
    -15.5 dBFS rms; check with `music` and adjust by a few tenths."""

    def __init__(self, M, level=1.0):
        from . import ring
        level = level * LOUD
        self.O = ring.Orchestra(M, level)               # the orchestra, its buses and its stage effects
        self.M, self.level = M, level
        for name, gain, rev in BUSES:
            M.bus(name, gain=gain * level, reverb=rev)
        self.piano = {dyn: M.sampler(PIANO.format(dyn), tune=0) for dyn in ('pp', 'mf', 'f')}
        self.extra = {}
        for name, (sus, short, _, _) in EXTRA.items():
            self.extra[name] = (M.sampler(sus, tune=-12) if sus else None,
                                M.sampler(short, tune=0 if name in ('xylo', 'marimba') else -12) if short else None)
        self.hits = dict(self.O.hits)
        for name, p in HITS.items():
            self.hits[name] = M.hits(p)
        self.synths = {name: M.synth(p) for name, p in SYNTHS.items()}
        self.queued = {name: [] for name in SYNTHS}
        M.bus('voices', gain=0.16 * level, reverb=0.4)
        self._kit = {'brush': [brush_swish(i) for i in range(4)], 'tap': [brush_tap(i) for i in range(4)]}
        self._n = 0

    def __getattr__(self, name):
        """Anything else is the orchestra's: B.thunder, B.wind, B.fire, B.boom, B.clash, B.gallop, B.hoof, B.hold..."""
        if name == 'O':
            raise AttributeError(name)
        return getattr(self.O, name)

    # ---- playing notes

    def _keys(self, m, t, v, d, pan, gain):
        """One piano note: the layer by velocity, the sample cut to what is needed before it is repitched."""
        from .audio import SR, _load, _fade_out
        s = self.piano['pp' if v < 58 else 'mf' if v < 96 else 'f']
        n = s._place(m + s.tune + s.label) - s.label
        k = int(s.keys[np.argmin(np.abs(s.keys - n))])
        files = s.zones[k][min(s.zones[k])]
        a = _load(files[int(s.rng.integers(len(files)))])
        r = 2 ** ((n - k) / 12)
        ring_for = min(max(d, 0.15) + 0.5, 7.0)
        a = a[:, :int(ring_for * SR * r) + 2]
        idx = np.arange(0, a.shape[1] - 1, r)
        out = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
        out = _fade_out(out * (v / 127) ** 1.7, max(d, 0.15), 0.35)
        self.M.add('keys', out, t, gain, 0.0 if pan is None else pan)

    def drum(self, name, t, v=90, gain=1.0, pan=None, d=0.3):
        """One drum stroke: 'brush', 'tap', 'chick', 'roll' (d seconds long), 'ride', 'kick' or any HITS name."""
        v = int(np.clip(v, 1, 127))
        pp = 0.0 if pan is None else pan
        if name in self._kit:
            self._n += 1
            sig = self._kit[name][self._n % 4]
            if name == 'brush' and d > 0.5:                 # a long swirl for ballads
                from .audio import SR
                sig = brush_swish(self._n, seconds=min(d, 1.6)) * np.clip(np.hanning(int(min(d, 1.6) * SR)), 0, 1) ** 0.5
            self.M.add('drums', np.vstack([sig, sig]) * (v / 127) ** 1.5, t, gain * 0.8, pp - 0.15)
        elif name == 'chick':
            from .audio import SR
            n = int(0.05 * SR)
            sig = _noise(n, 5000, 12000, int(t * 1000)) * np.exp(-np.arange(n) / (0.012 * SR))
            self.M.add('drums', np.vstack([sig, sig]) * (v / 127) ** 1.5, t, gain * 0.3, pp + 0.3)
        elif name == 'roll':
            sig = snare_roll(max(d, 0.2), int(t * 100))
            self.M.add('drums', np.vstack([sig, sig]) * (v / 127) ** 1.5, t, gain * 0.5, pp - 0.15)
        elif name in ('ride', 'kick'):
            g = 0.5 if name == 'ride' else 0.7
            self.M.add('drums', self.hits['ride accent' if name == 'ride' and v > 96 else name].play(v), t, gain * g,
                       pp + (0.35 if name == 'ride' else 0.0))
        elif name in self.hits:
            self.M.add('perc', self.hits[name].play(v), t, gain, pp)

    def play(self, section, m, t, d, v, pan=None, gain=1.0):
        """One note on any section: midi m (sounding) at t for d seconds, velocity v (1..127); drums ignore m."""
        v = int(np.clip(v, 1, 127))
        if section == 'piano':
            return self._keys(int(m), t, v, d, pan, gain)
        if section in self.synths:
            self.queued[section].append((t, int(m), v, d, pan, gain))
            return
        if section in DRUMS or section in ('ride', 'kick') or section in self.hits:
            return self.drum(section, t, v, gain, pan, d)
        if section not in self.extra:
            return self.O.play(section, m, t, d, v, pan, gain)
        sus, short = self.extra[section]
        _, _, bus, p = EXTRA[section]
        pan = p if pan is None else pan
        if sus is not None and (d >= 0.25 or short is None):
            if d > 1.2:
                self.O.hold(bus, sus, m, t, t + d, v, pan, gain)
            else:
                self.M.add(bus, sus.play(m, v, dur=d, release=0.15), t, gain, pan)
        else:
            sig = short.play(m, v) if section != 'bass' else short.play(m, v, dur=max(d, 0.3), release=0.12)
            self.M.add(bus, sig, t, gain, pan)

    def perform(self, events, parts=None, pan=None):
        """Play a chart's events; parts overrides DEFAULT by role or (tag, role); pan(t, midi, role) places them."""
        parts = parts or {}
        for t, d, m, v, role, tag in events:
            plan = parts.get((tag, role), parts.get(role, DEFAULT.get(role, [])))
            for section, tr, dv, g in plan:
                pp = pan(t, m, role) if pan else None
                self.play(section, 0 if m is None else m + tr, t, d, v + dv, pp, g)

    def hit(self, name, t, v=100, pitch=0.0, gain=0.5, pan=0.0, fx=False):
        """A percussion hit by name (the orchestra's and HITS); fx=True puts it on the effects bus."""
        h = self.hits[name].play(int(np.clip(v, 1, 127)), pitch=pitch)
        self.M.add('fx' if fx else 'perc', h, t, gain * (0.45 if fx else 1.0), pan(t) if callable(pan) else pan)

    def effects(self, points):
        """Ride the effects' level through the scene: [(t, dB), ...] (see ring.Orchestra.effects)."""
        self.O.effects(points)

    def finish(self):
        """Render the Surge voices: everything queued on each, one pass per pan position. Call it last."""
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

    # ---- the stage effects: what a production adds so the lights have a sound. pan may be a number or pan(t).

    def _sfx(self, sig, t, gain, pan):
        if callable(pan):
            pan = pan(t)
        self.M.add('fx', np.vstack([sig, sig]), t, gain, float(np.clip(pan, -1, 1)))

    def toast_pop(self, t, pan=0.0, gain=1.0, fly=True):
        """The toaster lets go: a ka-chunk, a springy boing, and (fly) a little slide up as the toast leaves."""
        from .audio import SR
        self.hit('claves', t, 110, pitch=-7, gain=0.5 * gain, pan=pan, fx=True)
        self.hit('woodblock', t + 0.02, 100, pitch=-3, gain=0.4 * gain, pan=pan, fx=True)
        n = int(0.45 * SR)
        tt = np.arange(n) / SR
        f = 380 * (1 + 0.6 * np.exp(-tt / 0.05)) * (1 + 0.05 * np.sin(2 * np.pi * 24 * tt))
        boing = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.14)
        boing += 0.4 * np.sin(2 * 2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.07)
        self._sfx(boing / np.abs(boing).max(), t + 0.01, 0.35 * gain, pan)
        if fly:
            self.slide(t + 0.04, 0.35, up=True, pan=pan, gain=0.5 * gain)

    def pop(self, t, pan=0.0, gain=1.0, seed=0):
        """One kernel of corn popping: a tight, bright pop."""
        from .audio import SR
        rng = np.random.default_rng(int(t * 1e4) + seed)
        n = int(0.03 * SR)
        tt = np.arange(n) / SR
        lo = rng.uniform(600, 1400)
        x = _noise(n, lo, lo * 5, int(t * 1e4) + seed) * np.exp(-tt / rng.uniform(0.004, 0.009))
        x += 0.4 * np.sin(2 * np.pi * rng.uniform(500, 900) * tt) * np.exp(-tt / 0.006)
        self._sfx(x / (np.abs(x).max() + 1e-9), t, 0.4 * gain * rng.uniform(0.5, 1.0), pan)

    def popcorn(self, times, pan=0.0, gain=1.0, spread=0.4):
        """Corn popping at times (from popcorn_times), each pop panned around pan."""
        rng = np.random.default_rng(len(times))
        for i, t in enumerate(times):
            p = (pan(t) if callable(pan) else pan) + rng.uniform(-spread, spread)
            self.pop(t, float(np.clip(p, -1, 1)), 1.8 * gain, i)

    def phone(self, t, rings=1, pan=0.0, gain=1.0, ring=1.1, gap=0.7):
        """An old bell telephone ringing: a clapper rattling between two bells, ring seconds on, gap off. Returns the
        time the last ring ends."""
        from .audio import SR
        n = int(ring * SR)
        tt = np.arange(n) / SR
        bell = np.zeros(n)
        for j, k in enumerate(range(0, n, int(SR / 40))):
            f0 = 1180 if j % 2 else 1310
            m = min(n - k, int(0.12 * SR))
            s = np.arange(m) / SR
            stroke = (np.sin(2 * np.pi * f0 * s) + 0.5 * np.sin(2 * np.pi * f0 * 2.76 * s)) * np.exp(-s / 0.05)
            bell[k:k + m] += stroke
        bell *= np.clip(tt / 0.01, 0, 1) * np.clip((ring - tt) / 0.05, 0, 1)
        bell /= np.abs(bell).max() + 1e-9
        for r in range(rings):
            self._sfx(bell, t + r * (ring + gap), 0.45 * gain, pan)
        return t + rings * (ring + gap) - gap

    def chair(self, t, pan=0.0, gain=1.0, seed=0):
        """A folding lawn chair clattering down: metal rattles and a slap, falling in a ragged rhythm. Returns its end."""
        gain = 2.2 * gain
        rng = np.random.default_rng(40 + seed)
        dts = np.cumsum([0, .07, .05, .11, .06, .16, .09, .22])
        for i, dt in enumerate(dts):
            self.O.hit('metal', t + dt, int(110 - 6 * i), pitch=rng.uniform(2, 7), gain=0.5 * gain, pan=pan, fx=True)
            if i % 3 == 0:
                self.hit('wood', t + dt + 0.01, 100, gain=0.6 * gain, pan=pan, fx=True)
        self.hit('slapstick', t + dts[-1] + 0.05, 112, gain=0.8 * gain, pan=pan, fx=True)
        self.O.hit('scrape', t, 70, pitch=5, gain=0.15 * gain, pan=pan, fx=True)
        return t + dts[-1] + 0.3

    def whistle(self, t, seconds=0.5, pan=0.0, gain=1.0):
        """A referee's pea whistle: a bright trilling tone and breath."""
        from .audio import SR
        n = int(seconds * SR)
        tt = np.arange(n) / SR
        f = 2350 + 160 * np.sin(2 * np.pi * 34 * tt)
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.75 + 0.25 * np.sin(2 * np.pi * 34 * tt))
        x += 0.25 * _noise(n, 1800, 4500, int(t * 100))
        x *= np.clip(tt / 0.015, 0, 1) * np.clip((seconds - tt) / 0.04, 0, 1)
        self._sfx(x / np.abs(x).max(), t, 0.25 * gain, pan)

    def horn(self, t, beeps=2, pan=0.0, gain=1.0, beep=0.2, gap=0.12):
        """A car horn: beeps of a two-tone honk. Returns when it ends."""
        from .audio import SR
        n = int(beep * SR)
        tt = np.arange(n) / SR
        x = np.tanh(2.5 * (np.sin(2 * np.pi * 392 * tt) + 0.8 * np.sin(2 * np.pi * 494 * tt)))
        x *= np.clip(tt / 0.01, 0, 1) * np.clip((beep - tt) / 0.02, 0, 1)
        x = x / np.abs(x).max()
        for b in range(beeps):
            self._sfx(x, t + b * (beep + gap), 0.16 * gain, pan)
        return t + beeps * (beep + gap) - gap

    def engine(self, t0, t1, pan=0.0, gain=1.0, rev=None):
        """An old car's engine putt-putting from t0 to t1; rev(t) 0..1 raises its pitch."""
        from .audio import SR
        n = int((t1 - t0) * SR)
        tt = t0 + np.arange(n) / SR
        r = rev(tt) if callable(rev) else np.full(n, 0.3 if rev is None else float(rev))
        f = 38 + 30 * r
        ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.tanh(3 * np.sin(ph)) * (0.6 + 0.4 * np.sin(ph * 0.5) ** 2)
        x += 0.3 * _noise(n, 80, 600, int(t0 * 10))
        x *= np.clip((tt - t0) / 0.5, 0, 1) * np.clip((t1 - tt) / 0.8, 0, 1)
        self._sfx(x / (np.abs(x).max() + 1e-9), t0, 0.18 * gain, pan)

    def kids(self, t0, t1, mood='chatter', level=1.0, pan=0.0, voices=7, seed=0):
        """A crowd of kids from t0 to t1. mood: 'chatter' (babble), 'cheer' (a rising 'yay'), 'aww' (falling
        disappointment), 'laugh' (ha-ha-ha), 'gasp' (a sharp intake). Panned around pan (or pan(t))."""
        from .audio import SR
        dur = max(t1 - t0, 0.3)
        n = int(dur * SR)
        tt = np.arange(n) / SR
        rng = np.random.default_rng(700 + seed)
        mix = np.zeros(n)
        for v in range(voices):
            base = rng.uniform(270, 420)
            on = rng.uniform(0, 0.15 if mood != 'chatter' else 0.4)
            u = np.clip((tt - on) / max(dur - on, 1e-3), 0, 1)
            if mood == 'cheer':
                f = base * (1 + 0.35 * np.clip(u * 6, 0, 1) - 0.1 * u)
                env = np.clip((tt - on) / 0.08, 0, 1) * np.clip((dur - tt) / 0.5, 0, 1)
                vowel = (850, 1650)
            elif mood == 'aww':
                f = base * (1.25 - 0.4 * u)
                env = np.clip((tt - on) / 0.15, 0, 1) * np.clip((dur - tt) / 0.4, 0, 1)
                vowel = (700, 1100)
            elif mood == 'laugh':
                rate = rng.uniform(5.0, 6.5)
                f = base * (1.2 - 0.25 * u)
                env = np.clip(np.sin(np.pi * ((tt - on) * rate % 1.0)), 0, 1) ** 2 * (tt > on)
                env *= np.clip((dur - tt) / 0.4, 0, 1)
                vowel = (750, 1300)
            elif mood == 'gasp':
                f = base * (1.1 + 0.2 * u)
                env = np.clip((tt - on) / 0.03, 0, 1) * np.exp(-np.maximum(tt - on, 0) / 0.25)
                vowel = (600, 1700)
            else:                                       # chatter: syllables at random pitches
                syl = rng.uniform(4, 6.5)
                k = np.floor((tt - on) * syl).astype(int)
                steps = rng.uniform(0.85, 1.25, k.max() + 2)
                f = base * steps[np.clip(k, 0, None)]
                env = (np.sin(np.pi * (((tt - on) * syl) % 1.0)) ** 2) * (tt > on)
                env *= np.clip((dur - tt) / 0.3, 0, 1) * np.clip(tt / 0.3, 0, 1)
                vowel = (int(rng.choice([500, 700, 850])), int(rng.choice([1100, 1700, 2100])))
            f = f * (1 + 0.02 * np.sin(2 * np.pi * rng.uniform(4, 6) * tt))
            mix += _voice(f, dur, vowel, seed * 31 + v) * env * rng.uniform(0.6, 1.0)
        if mood == 'gasp':
            mix += 0.6 * _noise(n, 1200, 6000, 9 + seed) * np.exp(-tt / 0.2)
        self._sfx(mix / (np.abs(mix).max() + 1e-9), t0, 0.4 * level, pan)

    def woof(self, t, pan=0.0, big=1.0):
        """Snoopy's bark: a muted-horn yap with a puff of breath."""
        from .audio import SR
        self.play('muted horn', note('A3'), t, 0.12, int(96 + 20 * big), pan, 0.9 * big)
        self.play('muted horn', note('E4'), t + 0.02, 0.1, int(90 + 20 * big), pan, 0.6 * big)
        n = int(0.12 * SR)
        puff = _noise(n, 300, 2500, int(t * 1000) + 3) * np.exp(-np.arange(n) / (0.03 * SR))
        self._sfx(puff, t, 0.25 * big, pan)

    def chirp(self, t, n=4, pan=0.0, gain=1.0, seed=0):
        """The little bird's twitter: n quick chirps, each a short upward flick."""
        from .audio import SR
        rng = np.random.default_rng(int(t * 100) + seed)
        tc = t
        for i in range(n):
            m = int(rng.uniform(0.035, 0.07) * SR)
            s = np.arange(m) / SR
            f0 = rng.uniform(1700, 2400)
            f = f0 * (1 + 0.45 * s / s[-1])
            x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(np.sin(np.pi * s / s[-1]), 0, 1) ** 1.5
            self._sfx(x, tc, 0.25 * gain, pan)
            tc += rng.uniform(0.06, 0.11)

    def slide(self, t, seconds=0.6, up=True, pan=0.0, gain=1.0, lo=500.0, hi=1500.0):
        """A slide whistle: up (flying, popping up) or down (falling)."""
        sig = _slide_sig(0.0, seconds * 0.9, lo if up else hi, hi if up else lo, seconds + 0.05, amp=0.5)
        self.M.add('fx', sig, t, 0.5 * gain, float(np.clip(pan(t) if callable(pan) else pan, -1, 1)))

    def whoosh(self, t, seconds=0.6, up=True, pan=0.0, gain=1.0):
        """Something flying past: a ball yanked away, a swing that misses."""
        from .audio import whoosh
        w = whoosh(seconds, 300 if up else 3000, 3000 if up else 300, 0.5, seed=int(t * 100))
        self.M.add('fx', w, t, 1.8 * gain, float(np.clip(pan(t) if callable(pan) else pan, -1, 1)))

    def thud(self, t, pan=0.0, gain=1.0):
        """Somebody landing flat on his back: a heavy body thump, a slap, a little rattle of the ground."""
        from .audio import SR
        self.O.hit('bass drum', t, 124, gain=0.9 * gain, pan=pan(t) if callable(pan) else pan, fx=True)
        self.hit('slapstick', t + 0.005, 120, gain=0.7 * gain, pan=pan, fx=True)
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        thump = np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt / 0.12)
        thump += 0.3 * _noise(n, 60, 500, int(t * 100)) * np.exp(-tt / 0.08)
        self._sfx(thump / np.abs(thump).max(), t, 0.8 * gain, pan)

    def boing(self, t, pan=0.0, gain=1.0, high=1.0):
        """A spring's boing: bounces, double-takes, things springing up."""
        from .audio import SR
        n = int(0.5 * SR)
        tt = np.arange(n) / SR
        f = (220 * high) * (1 + 0.8 * np.clip(tt / 0.08, 0, 1)) * (1 + 0.07 * np.sin(2 * np.pi * 18 * tt))
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.18)
        self._sfx(x, t, 0.3 * gain, pan)

    def clink(self, t, pan=0.0, gain=1.0, pitch=0.0):
        """Plates and glasses: a triangle tapped high."""
        self.O.hit('triangle', t, 100, pitch=pitch + 5, gain=2.5 * gain, pan=pan(t) if callable(pan) else pan, fx=True)

    def crunch(self, t, bites=1, pan=0.0, gain=1.0):
        """Crunching toast or popcorn: bites of crackly noise."""
        from .audio import SR
        for b in range(bites):
            n = int(0.18 * SR)
            tt = np.arange(n) / SR
            rng = np.random.default_rng(int(t * 100) + b)
            grains = (rng.random(n) < 0.004).astype(float)
            x = np.convolve(grains, np.exp(-np.arange(200) / 30), 'same') * _noise(n, 900, 6000, b + int(t))
            x *= np.exp(-tt / 0.1)
            self._sfx(x / (np.abs(x).max() + 1e-9), t + 0.25 * b, 1.2 * gain, pan)

    def steps(self, t0, t1, beat=0.4, pan=0.0, gain=1.0, v=80):
        """Footsteps from t0 to t1, beat seconds apart (soft hand-drum taps); pan may follow the walker, pan(t)."""
        t, i = t0, 0
        while t < t1:
            self.hit('hoof soft', t, v - 10 * (i % 2), gain=1.25 * gain, pan=pan, fx=True)
            t += beat
            i += 1

    def roll(self, t0, t1, pan=0.0, gain=1.0, v=100, crescendo=True):
        """A snare roll building from t0 to t1 (the drummer winding up before a payoff)."""
        self.drum('roll', t0, v, gain, pan(t0) if callable(pan) else pan, t1 - t0)

    def fall(self, t, m=None, pan=0.0, gain=1.0):
        """A trombone's 'wah-wah' fall: the joke landed, the plan failed."""
        self.play('trombone fall', note('Bb2') if m is None else m, t, 1.5, 110, pan, 2.0 * gain)

    def ding(self, t, pan=0.0, gain=1.0):
        """A kitchen timer's ding (the toaster, the oven)."""
        self.O.play('glock', note('E5'), t, 0.6, 110, pan, 1.5 * gain)
        self.O.hit('triangle', t, 90, pitch=3, gain=0.7 * gain, pan=pan, fx=True)


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


def tri(x):
    """A triangle wave 0..1..0 with period 1: zigzags."""
    f = np.asarray(x, float) % 1.0
    return 1 - np.abs(2 * f - 1)


class Stage:
    """The house as the story's stage. d is each node's distance along the roofline (G.pd), L its length; run[name] a
    mask of each run; at(run, u) a point u of the way along a run; pan(p) where a point sounds from the street.

    The porch is the centre of most scenes (the kitchen, the ping-pong table, the football); the wings are the yard
    around it and are never left dark while the porch has the action. Nothing starts on Side: a character enters from
    the free end of Right (p > L, walking with facing=-1), from the porch, or pops up on a front run. Side is for exits
    and for whole-house payoffs.

    Characters are drawn with sprite() (a list of (offset, colour, level) pixels, colour None for a dark pixel that
    cuts the backdrop) at path distance p, facing +1 (toward Right) or -1 (toward Side). Backdrops return (N,3) PWM.
    Big looks (zigzag, sweep, wave, burst, confetti, popcorn, toast_burst, chase, run_flash) fill whole runs; use them,
    a lone sprite on 501 pixels reads as nothing from the street."""

    RUNS = ('Side', 'Left', 'Porch Left', 'Porch Front', 'Porch Right', 'Right')
    FRONT = ('Left', 'Porch Front', 'Right')            # the three runs that face the street

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
        self.front = self.run['Left'] | self.run['Porch Front'] | self.run['Right']
        self.mid = self.at('Porch Front', 0.5)
        self.rng = np.random.default_rng(1973 + seed)
        order = np.argsort(G.pd)
        self._xs, self._ds = G.pos[order, 0], G.pd[order]
        self._x0, self._x1 = self._xs.min(), self._xs.max()
        self.x = (G.pos[:, 0] - self._x0) / (self._x1 - self._x0)      # 0 (Side, Left's far end) .. 1 (Right's end)

    def at(self, run, u):
        """Path distance u (0..1) of the way along a run, in path direction (Left runs toward the porch, Right away)."""
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
        """1 between path distances a and b (either order), soft-edged."""
        a, b = min(a, b), max(a, b)
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

    def note_at(self, m, lo=55, hi=81):
        """Where a pitch lands across the front of the house, low notes at the left end of Left, high at the right end
        of Right (as the street sees a keyboard): a path distance, for lights that play the tune."""
        u = float(np.clip((m - lo) / (hi - lo), 0, 1))
        a, b = self.at('Left', 0.0), self.L
        return a + u * (b - a)

    # ---- pixel sprites. A sprite is a list of (offset in pixels along the path, colour, level); positive offsets run
    # ahead of p in the facing direction. Dark pixels are colour None: they cut what is behind them, which is how a
    # zigzag, an ear or a pair of eyes reads on a line of lights.

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

    def boy(self, fr, p, lvl=1.0, facing=1, t=0.0, run=0.0, glow=0.3):
        """Charlie Brown: a big round peach head in front, his yellow shirt behind with the black zigzag across
        it (dark pixels), dark shorts. run 0..1 makes the zigzag flicker like legs going; glow lights the run around him."""
        step = int(t * 8) % 2 if run > 0.3 else 0
        px = [(3, SKIN, 0.75), (2, SKIN, 1.0), (1, SKIN, 0.75), (0, None, 0),
              (-1, YELLOW, 1.0), (-2, YELLOW, 1.0), (-3 - step, None, 0), (-4 + step, YELLOW, 1.0), (-5, YELLOW, 1.0),
              (-6, None, 0), (-7, YELLOW, 0.9), (-8, None, 0), (-9, SKIN, 0.35 * (1 - 0.5 * step))]
        fr = self.sprite(fr, p, px, lvl, facing)
        if glow:
            fr += light(YELLOW, glow * lvl * self.blob(p - facing * 12, 50))
        return fr

    def boy_flat(self, fr, p, lvl=1.0, t=0.0):
        """The boy flat on his back: head and shirt spread wide and dim, the zigzag still there."""
        px = [(o, SKIN, 0.5) for o in (5, 4, 3)] + [(2, None, 0)] + \
             [(o, None if o in (-1, -4, -7) else YELLOW, 0.55) for o in range(1, -10, -1)]
        return self.sprite(fr, p, px, lvl, 1)

    def beagle(self, fr, p, lvl=1.0, facing=1, t=0.0, wag=1.0, chef=False):
        """Snoopy: a white head with its black nose at the front, a black ear (dark pixel), a white body and a
        wagging tail. chef=True puts his tall white chef's toque on, ahead of his nose."""
        w = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t) * wag
        px = [(3, None, 0), (2, BEAGLE, 1.0), (1, BEAGLE, 1.0), (0, None, 0), (-1, BEAGLE, 0.9), (-2, BEAGLE, 0.9),
              (-3, BEAGLE, 0.85), (-4, BEAGLE, 0.25 + 0.55 * w), (-5, BEAGLE, 0.15 + 0.3 * (1 - w))]
        if chef:
            px = [(6, WHITE, 1.0), (5, WHITE, 1.0), (4, WHITE, 0.7)] + px
        return self.sprite(fr, p, px, lvl, facing)

    def bird(self, fr, p, lvl=1.0, t=0.0, flutter=1.0, facing=1):
        """Woodstock: two bright pixels, wings beating, and a small glow of his own."""
        flap = 0.5 + 0.5 * np.sin(2 * np.pi * 9 * t) * flutter
        fr = self.sprite(fr, p, [(1, BIRD, 1.0), (0, BIRD, 0.9), (-1, BIRD, 0.25 + 0.6 * flap)], lvl, facing)
        fr += light(BIRD, 0.3 * lvl * self.blob(p, 14))
        return fr

    def kid(self, fr, p, body, lvl=1.0, facing=1, hair=None, face=SKIN, gap=True):
        """Any of the kids: a face in front, hair behind it (None for dark), and body, a list of colours from the neck
        back (None for a dark stripe). gap leaves a dark neck between head and body."""
        px = [(2, face, 0.9), (1, face, 1.0), (0, hair, 0.55 if hair is not None else 0)]
        o = -1
        if gap:
            px.append((o, None, 0))
            o -= 1
        for col in body:
            px.append((o, col, 0.95 if col is not None else 0))
            o -= 1
        return self.sprite(fr, p, px, lvl, facing)

    def tomboy(self, fr, p, lvl=1.0, facing=1, t=0.0):
        """Peppermint Patty: freckled face, brown hair, a green shirt and dark shorts."""
        return self.kid(fr, p, [GREEN, GREEN, GREEN, GREEN, None, SKIN], lvl, facing, hair=HAIR)

    def blanket_boy(self, fr, p, lvl=1.0, facing=1, t=0.0, wave=1.0):
        """Linus: a red-striped shirt (red and dark), and his blue blanket trailing behind,
        rippling."""
        fr = self.kid(fr, p, [STRIPE, None, STRIPE, None, STRIPE], lvl, facing, hair=None, gap=False)
        blank = [(-6 - j, BLANKET, 0.55 + 0.35 * np.sin(2 * np.pi * (1.2 * t - j / 5)) * wave) for j in range(7)]
        return self.sprite(fr, p, blank, lvl, facing, cut=False)

    def glasses(self, fr, p, lvl=1.0, facing=1, t=0.0, glint=0.0):
        """Marcie: white lenses that glint (glint 0..1), brown hair, an orange shirt."""
        px = [(2, SKIN, 0.8), (1, WHITE, 0.6 + 0.4 * glint), (0, HAIR, 0.55), (-1, None, 0),
              (-2, GLASSES, 1.0), (-3, GLASSES, 1.0), (-4, GLASSES, 0.9), (-5, GLASSES, 0.9)]
        fr = self.sprite(fr, p, px, lvl, facing)
        if glint:
            fr += light(WHITE, 0.6 * glint * lvl * self.blob(p + facing * 4, 10))
        return fr

    def bossy(self, fr, p, lvl=1.0, facing=1, t=0.0):
        """Lucy (football): black hair (dark), a blue dress."""
        return self.kid(fr, p, [DRESS, DRESS, DRESS, DRESS, DRESS], lvl, facing, hair=None)

    def sister(self, fr, p, lvl=1.0, facing=1, t=0.0):
        """His little sister: blonde curls and a pink dress."""
        return self.kid(fr, p, [PINK, PINK, PINK, PINK], lvl, facing, hair=BLOND, gap=False)

    def cap_boy(self, fr, p, lvl=1.0, facing=1, t=0.0):
        """Franklin: a red cap in front of his face, a white shirt."""
        px = [(3, CAP, 0.9), (2, SKIN, 0.8), (1, SKIN, 0.9), (0, None, 0), (-1, WHITE, 0.7), (-2, WHITE, 0.7),
              (-3, WHITE, 0.7), (-4, None, 0), (-5, BLUE, 0.6)]
        return self.sprite(fr, p, px, lvl, facing)

    def football(self, fr, p, lvl=1.0, t=0.0, spin=0.0):
        """The football: three brown pixels with a white lace in the middle; spin (turns a second) blinks the lace."""
        lace = 1.0 if spin == 0 else 0.5 + 0.5 * np.cos(2 * np.pi * spin * t)
        fr = self.sprite(fr, p, [(1, BALL, 0.95), (0, WHITE, 0.4 + 0.5 * lace), (-1, BALL, 0.95)], lvl, 1)
        fr += light(BALL, 0.35 * lvl * self.blob(p, 18))
        return fr

    def table(self, fr, p, lvl=1.0, half=12, net=True, food=()):
        """The ping-pong table: a green slab 2*half+1 pixels wide with white edges and a white net in the middle.
        food: [(offset in pixels, colour)] set out along it (a bowl of popcorn, a plate of toast)."""
        px = [(o, TABLE, 0.85) for o in range(-half, half + 1)]
        px[0], px[-1] = (-half, WHITE, 0.8), (half, WHITE, 0.8)
        if net:
            px[half] = (0, WHITE, 1.0)
        px = dict((o, (o, c, v)) for o, c, v in px)
        for o, col in food:
            px[o] = (o, col, 1.0)
        return self.sprite(fr, p, list(px.values()), lvl, 1)

    def car(self, fr, p, lvl=1.0, facing=1, t=0.0, color=CAR, lights=1.0):
        """A car: headlights in front (and their beam on the roof ahead), a coloured body with two pale windows,
        dark wheels turning, a red tail light."""
        spin = int(t * 10) % 2
        px = [(2, WHITE, 1.0 * lights), (1, color, 0.95), (0, color, 0.95), (-1, ICE, 0.6), (-2, color, 0.9),
              (-3, ICE, 0.6), (-4, color, 0.95), (-5, color, 0.95), (-6, RED, 0.8 * lights)]
        fr = self.sprite(fr, p, px, lvl, facing)
        for o in (0, -4):                                   # wheels: a dark pixel that ticks as they turn
            k = self.k_off(p) + facing * (o - spin)
            if 0 <= k < self.N:
                fr[self.path[k]] *= 0.25
        if lights:
            fr += light(WARM, 0.45 * lights * lvl * self.blob(p + facing * 40, 35))
        return fr

    def dish(self, fr, p, kind, lvl=1.0, t=0.0):
        """Food on the table: 'toast' (golden, a butter pat), 'popcorn' (cream, twinkling), 'pretzels' (brown),
        'jellybeans' (a rainbow), 'turkey' (roast brown, white drumstick ends), 'pie' (amber), 'cranberry'."""
        if kind == 'toast':
            px = [(1, TOAST, 0.9), (0, BUTTER, 1.0), (-1, TOAST, 0.9)]
        elif kind == 'popcorn':
            px = [(o, POPCORN, 0.7 + 0.3 * np.sin(11 * t + 2.3 * o)) for o in (-1, 0, 1)]
        elif kind == 'pretzels':
            px = [(1, PRETZEL, 0.9), (0, None, 0), (-1, PRETZEL, 0.9)]
        elif kind == 'jellybeans':
            px = [(o, JELLY[(o + int(t * 3)) % len(JELLY)], 0.95) for o in (-2, -1, 0, 1, 2)]
        elif kind == 'turkey':
            px = [(3, WHITE, 0.8), (2, TURKEY, 1.0), (1, TURKEY, 1.0), (0, TURKEY, 1.0), (-1, TURKEY, 1.0),
                  (-2, TURKEY, 1.0), (-3, WHITE, 0.8)]
        elif kind == 'pie':
            px = [(1, AMBER, 0.9), (0, GOLD, 0.8), (-1, AMBER, 0.9)]
        else:
            px = [(1, CRANBERRY, 0.9), (0, CRANBERRY, 1.0), (-1, CRANBERRY, 0.9)]
        return self.sprite(fr, p, px, lvl, 1)

    def stars(self, fr, p, t, lvl=1.0, n=3, r=14.0):
        """Seeing stars: n little coloured dots circling over a head at p (they swing back and forth through it)."""
        cols = (WHITE, BIRD, ICE, PINK)
        for i in range(n):
            ph = 2 * np.pi * (1.6 * t + i / n)
            q = p + r * np.sin(ph)
            fr += light(cols[i % len(cols)], lvl * (0.55 + 0.45 * np.cos(ph)) * np.exp(-((self.d - q) / 4.5) ** 2))
        return fr

    # ---- backdrops, each -> (N,3) PWM at time t with levels 0..1

    def leaves(self, t, amount=1.0, wind=-25.0, n=70, seed=0):
        """Autumn leaves falling: n leaves drifting along the roof with the wind (units a second, negative toward
        Side), fluttering side to side and turning over (red, orange, gold, rust), each fading in and out as it falls."""
        if amount <= 0:
            return np.zeros((self.N, 3))
        rng = np.random.default_rng(80 + seed)
        p0, fl, ph = rng.uniform(0, self.L, n), rng.uniform(0.25, 0.7, n), rng.uniform(0, 1, n)
        life = rng.uniform(3, 7, n)
        cols = np.array(LEAVES)[rng.integers(0, len(LEAVES), n)]
        pos = (p0 + wind * t + 14 * np.sin(2 * np.pi * fl * t + 6.28 * ph)) % self.L
        age = (t / life + ph) % 1.0
        vis = np.clip(np.sin(np.pi * age), 0, 1) ** 1.5 * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 1.3 * fl * t + 3 * ph)))
        w = np.exp(-((self.d[:, None] - pos[None, :]) / 7.5) ** 2) * vis[None, :] * amount
        return perc(np.clip(w, 0, 1.3)) @ cols

    def yard(self, t, lv=1.0, leaves=1.0, sun=1.0, wind=-25.0, seed=0):
        """The autumn yard at the end of the afternoon: a violet-blue sky on every run, a low orange sun glowing over
        the porch, and leaves falling all along the roof."""
        fr = light(DUSK, 0.42 * lv * np.ones(self.N))
        fr += light(SKY, 0.25 * lv * (1 - self.porch))
        fr += light(SUN, 0.8 * lv * sun * self.blob(self.mid, 170))
        fr += light(AMBER, 0.38 * lv * sun * self.blob(self.mid, 450))
        return fr + lv * self.leaves(t, leaves, wind, seed=seed)

    def kitchen(self, t, lv=1.0, stove=1.0, seed=0):
        """The kitchen: warm yellow walls on every run, a red-and-white checked floor along the wings, and the stove
        glowing and flickering over the porch."""
        if not hasattr(self, '_kfl'):
            self._kfl = Flicker(np.random.default_rng(12 + seed), self.N, 0.4, 2.0)
        fr = light(GOLD, 0.33 * lv * np.ones(self.N))
        tile = (np.floor(self.d / 18.0) % 2).astype(float)
        fr += self.wings[:, None] * (light(RED, 0.45 * lv * tile) + light(WHITE, 0.3 * lv * (1 - tile)))
        fr += light(ORANGE, 0.75 * lv * stove * self.blob(self.mid, 110) * (0.8 + 0.2 * self._kfl(t)))
        return fr

    def backyard(self, t, lv=1.0, bulbs=1.0, seed=0):
        """The backyard at evening: a deep blue sky, the lawn and hedges green along the wings, and a string of warm
        party bulbs swaying over every run."""
        if not hasattr(self, '_bfl'):
            self._bfl = Flicker(np.random.default_rng(14 + seed), self.N, 0.15, 0.8)
        fr = light(NIGHT, 0.4 * lv * np.ones(self.N))
        fr += light(LAWN, 0.4 * lv * self.wings)
        bulb = (self.G.pi % 6 == 0) * (0.85 + 0.15 * self._bfl(t))
        sway = 0.75 + 0.25 * np.sin(2 * np.pi * (0.25 * t - self.d / 700.0))
        fr += light(WARM, 0.9 * lv * bulbs * bulb * sway)
        return fr

    def sea(self, t, lv=1.0, swell=1.0, speed=60.0, storm=0.0):
        """The open sea under the Mayflower: deep blue, rolling crests travelling along the roof with white foam
        sparkling on them; storm 0..1 makes it greyer, rougher and faster."""
        sp = speed * (1 + storm)
        crest = 0.5 + 0.5 * np.sin(2 * np.pi * (self.d - sp * t) / (240 - 80 * storm))
        crest2 = 0.5 + 0.5 * np.sin(2 * np.pi * (self.d + 0.6 * sp * t) / 170 + 1.3)
        h = (0.6 * crest + 0.4 * crest2) * swell
        fr = light(SEA, lv * (0.3 + 0.35 * h))
        fr += light(hexc('#6070a0'), 0.35 * lv * storm * np.ones(self.N))
        foam = np.clip((h - 0.75) / 0.25, 0, 1) * (0.6 + 0.4 * np.sin(31 * t + self.d * 0.7))
        fr += light(FOAM, 0.8 * lv * foam)
        return fr

    def snowfall(self, t, amount=1.0, seed=3):
        """Snow alone: white flakes sparkling on and off all along the roof."""
        rng = np.random.default_rng(seed)
        ph = (rng.uniform(0, 1, self.N) + rng.uniform(0.3, 0.7, self.N) * t) % 1.0
        return light(SNOW, 0.9 * amount * np.exp(-((ph - 0.5) / 0.05) ** 2))

    def road(self, t, lv=1.0, snow=1.0, speed=120.0):
        """The snowy road to Grandma's: a night-blue sky, pine trees and fence posts streaming past along the roof
        (speed units a second toward Right: the car seems to drive toward Side), and snow falling."""
        fr = light(NIGHT, 0.38 * lv * np.ones(self.N))
        u = (self.d - speed * t) / 90.0
        pine = np.clip(1 - np.abs((u % 1.0) - 0.5) * 6, 0, 1)
        fr += light(PINE, 0.75 * lv * pine)
        post = np.clip(1 - np.abs(((self.d - 1.6 * speed * t) / 37.0) % 1.0 - 0.5) * 14, 0, 1)
        fr += light(WHITE, 0.35 * lv * post)
        return fr + self.snowfall(t, snow * lv)

    def night(self, t, lv=1.0, stars=1.0, seed=2):
        """A clear night: deep blue and twinkling stars (Snoopy's own feast on his roof)."""
        rng = np.random.default_rng(seed)
        if not hasattr(self, '_stars'):
            self._stars = dict(on=(rng.random(self.N) < 0.12) * rng.uniform(0.5, 1, self.N),
                               fl=Flicker(rng, self.N, 0.3, 1.4))
        S = self._stars
        fr = light(NIGHT, 0.38 * lv * np.ones(self.N))
        return fr + light(SNOW, 0.75 * lv * stars * S['on'] * (0.75 + 0.25 * S['fl'](t)))

    # ---- big looks that fill runs. Each -> (N,3) PWM to add (zigzag returns a full frame you can blend or add).

    def zigzag(self, phase, lv=1.0, col=YELLOW, dark=0.0, period=56.0, width=0.28, amp=0.5, mask=None, travel=0.0):
        """The boy's shirt across whole runs: col everywhere with black bands, and the bands zig one way and zag back
        over one unit of phase and zag back over the next (pass the beat count, e.g. t / beat, to lock it to the music;
        in the timeline the bands draw a zigzag). travel moves the bands along as well (periods per unit of phase). dark is the level left in
        the bands (0 black). mask limits it to some runs."""
        off = amp * (2 * tri(phase / 2.0) - 1) + travel * phase
        u = (self.d / period - off) % 1.0
        band = smoothstep(width / 2 + 0.06, width / 2, np.abs(u - 0.5))
        lvl = lv * (1 - (1 - dark) * band)
        if mask is not None:
            lvl = lvl * mask
        return light(col, lvl)

    def stripes(self, phase, cols, lv=1.0, period=40.0, mask=None):
        """Bands of cols repeating along the roof, moving one band per unit of phase (a marquee, candy stripes)."""
        k = np.floor(self.d / period + phase).astype(int) % len(cols)
        out = np.array(cols)[k] * perc(lv)
        return out * (mask[:, None] if mask is not None else 1)

    def chase(self, phase, cols=(YELLOW, None), lv=1.0, spacing=3, mask=None):
        """Theatre-marquee bulbs: every pixel in turn takes the next colour of cols (None is dark), stepping one pixel
        per unit of phase. Pass the beat count (or twice it) to lock it to the music."""
        k = (self.G.pi + int(np.floor(phase))) % (spacing * len(cols)) // spacing
        out = np.zeros((self.N, 3))
        for i, c in enumerate(cols):
            if c is not None:
                out += (k == i)[:, None] * c * perc(lv)
        return out * (mask[:, None] if mask is not None else 1)

    def run_flash(self, t, times, cols=(YELLOW,), runs=None, lv=1.0, decay=0.25):
        """Run by run on the beat: at each of times the next run in runs (default Left, Porch Front, Right, Porch
        Left, Porch Right) flashes the next of cols and fades over decay seconds."""
        runs = runs or ('Left', 'Porch Front', 'Right', 'Porch Left', 'Porch Right')
        times = np.asarray(times, float)
        out = np.zeros((self.N, 3))
        for i in np.flatnonzero((times <= t) & (times > t - 5 * decay)):
            a = t - times[i]
            out += light(cols[i % len(cols)], lv * np.exp(-a / decay) * self.run[runs[i % len(runs)]])
        return out

    def sweep(self, t, t0, dur, col=YELLOW, lv=1.0, frm='right', width=60.0, trail=0.6):
        """A whole-house wipe: a bright front crossing every run in dur seconds from frm ('right' end, 'side' end,
        'centre' out both ways, or 'ends' in to the porch), leaving a trail that fades over trail seconds."""
        a = t - t0
        if a < 0 or a > dur + 4 * trail + 0.5:
            return np.zeros((self.N, 3))
        far = max(self.mid, self.L - self.mid)
        dist = {'right': (self.L - self.d) / self.L, 'side': self.d / self.L,
                'centre': np.abs(self.d - self.mid) / far, 'ends': 1 - np.abs(self.d - self.mid) / far}[frm]
        since = a - np.clip(dist, 0, 1) * dur                  # how long ago the front passed each pixel
        hw = width / self.L * dur                               # the time the front takes to cross width
        head = np.exp(-(since / hw) ** 2)
        tail = (since > 0) * np.exp(-np.maximum(since, 0) / trail) * 0.55
        return light(col, lv * np.clip(head + tail, 0, 1))

    def wave(self, t, t0, col=WHITE, lv=1.0, origin=None, speed=1000.0, width=60.0, decay=0.8):
        """A ring of light running out both ways from origin (default the porch's middle) at speed units a second."""
        a = t - t0
        if a < 0 or a > 4 * decay + 3:
            return np.zeros((self.N, 3))
        o = self.mid if origin is None else origin
        return light(col, lv * np.exp(-a / decay) * np.exp(-((np.abs(self.d - o) - speed * a) / width) ** 2))

    def burst(self, hits, t, seed=0, n=14, reach=1.0, colors=(WHITE,), life=1.6):
        """Bursts [(time, strength, where)]: each throws n sparks both ways along the roofline -> (N,3) PWM."""
        out = np.zeros((self.N, 3))
        for i, (th, s, p0) in enumerate(hits):
            a = t - th
            if not 0 <= a < life:
                continue
            rng = np.random.default_rng(seed * 1000 + i)
            v = rng.uniform(500, 2600, n) * rng.choice([-1, 1], n) * reach
            ps = p0 + v * (1 - np.exp(-a / 0.6)) * 0.6
            lf = np.exp(-a / rng.uniform(0.35, 0.9, n))
            for j in range(n):
                out += light(colors[j % len(colors)], s * lf[j] * np.exp(-((self.d - ps[j]) / 7) ** 2))
        return out

    def confetti(self, hits, t, colors=JELLY, n=24, reach=1.0, seed=0):
        """Celebration: [(time, strength, where)] each throws n coloured sparks out both ways that drift, twinkle and
        settle slowly (slower and longer-lived than burst)."""
        out = np.zeros((self.N, 3))
        for i, (th, s, p0) in enumerate(hits):
            a = t - th
            if not 0 <= a < 3.0:
                continue
            rng = np.random.default_rng(seed * 1000 + 77 + i)
            v = rng.uniform(150, 900, n) * rng.choice([-1, 1], n) * reach
            ps = p0 + v * (1 - np.exp(-a / 0.8)) * 0.8
            tw = 0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(3, 7, n) * a + rng.uniform(0, 6, n))
            lf = np.exp(-a / rng.uniform(0.8, 1.6, n)) * tw
            w = np.exp(-((self.d[:, None] - ps[None, :]) / 6.0) ** 2) * (s * lf)[None, :]
            cols = np.array(colors)[np.arange(n) % len(colors)]
            out += perc(np.clip(w, 0, 1.2)) @ cols
        return out

    def popcorn(self, times, t, lo=None, hi=None, lv=1.0, seed=0):
        """Kernels popping at times (from popcorn_times) at random spots between path distances lo and hi (default the
        whole house): each a white-gold flash that jumps a little and fades in a quarter second."""
        lo = 0.0 if lo is None else lo
        hi = self.L if hi is None else hi
        times = np.asarray(times, float)
        sel = np.flatnonzero((times <= t) & (times > t - 0.6))
        out = np.zeros((self.N, 3))
        for i in sel:
            rng = np.random.default_rng(seed * 7919 + i)
            p = rng.uniform(lo, hi) + rng.uniform(-30, 30) * (1 - np.exp(-(t - times[i]) / 0.08))
            a = t - times[i]
            col = POPCORN if rng.random() < 0.8 else BUTTER
            out += light(col, lv * (np.exp(-a / 0.22) + 0.6 * np.exp(-a / 0.05)) * np.exp(-((self.d - p) / 8.0) ** 2))
        return out

    def toast_burst(self, hits, t, lv=1.0, flight=1.1, height=260.0):
        """Toast flying up out of the toaster: [(time, where, direction)] each launches a golden slice from where,
        out along the roof (direction +1/-1) and back down again over flight seconds, with a white flash at the pop
        and a trail of crumbs."""
        out = np.zeros((self.N, 3))
        for i, (th, p0, dr) in enumerate(hits):
            a = t - th
            if a < 0 or a > flight + 0.6:
                continue
            if a < 0.25:
                out += light(WHITE, 0.9 * lv * np.exp(-a / 0.08) * self.blob(p0, 30))
            u = np.clip(a / flight, 0, 1)
            q = p0 + dr * height * 4 * u * (1 - u) * 1.0
            if a <= flight:
                out += light(TOAST, lv * smoothstep(q - 12, q - 6, self.d) * smoothstep(q + 12, q + 6, self.d))
                out += light(BUTTER, 0.8 * lv * np.exp(-((self.d - q) / 4.0) ** 2))
                crumbs = np.exp(-((self.d - (q - dr * 25)) / 18) ** 2) * (0.5 + 0.5 * np.sin(40 * t + self.d))
                out += light(GOLD, 0.45 * lv * crumbs)
            else:
                out += light(GOLD, 0.6 * lv * np.exp(-(a - flight) / 0.15) * self.blob(p0, 25))
        return out
