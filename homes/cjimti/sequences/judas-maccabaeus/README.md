# Judas Maccabaeus on the roofline

Handel's *Judas Maccabaeus* (HWV 63) in 15 shows of about 85 seconds, `JM01`..`JM15`, plus an intermission (`JM16`),
for the eight nights of Hanukkah. Each night opens with that night's candle-lighting show (`homes/cjimti/sequences/
hanukkah/`), and the lights' glow stays on the porch through the whole set. Epic: #43.

## About the work

Handel wrote *Judas Maccabaeus* in the summer of 1746, and it was first performed at Covent Garden on 1 April 1747.
Thomas Morell's libretto, drawn from 1 Maccabees and Josephus, tells the revolt of the Maccabees against the Seleucid
king Antiochus IV: the death of their father Mattathias, Judas taking command, the victories, the cleansing and
rededication of the Temple in Jerusalem, and peace.

It was written for a British occasion. Handel and Morell wrote it after the Battle of Culloden and dedicated it to
the Duke of Cumberland, and the Jewish story was the vehicle: a concert oratorio on Jewish history by a Lutheran
composer, not Jewish liturgical music. It has long been associated with Hanukkah, the festival of the rededication.

The libretto has the victory, not the oil. 1 Maccabees gives the eight days of dedication; the miracle of the oil
that burned for eight days comes from the Talmud, and isn't in Morell's text. Rabbinic tradition puts the light at
the centre and the battles at the edge, so here the candle-lighting show carries the light, before the set begins.

"See, the conqu'ring hero comes" was borrowed: Handel wrote it for *Joshua* (1748) and added it to *Judas* in later
revivals. It is now the best-known number in both.

There is a thread to *Elijah*, the set that plays on the Ring nights: both turn on refusing idols. "We never will bow
down to the rude stock or sculptur'd stone" is the refusal Elijah makes on Mount Carmel.

## Where the music comes from

Every note is transcribed by hand from a public-domain score: Vincent Novello's vocal score of *Judas Maccabaeus*,
published by Novello, Ewer and Co. in London, read from the copy on the Internet Archive (`handelsoratorioj00hand`,
from the University of Toronto's music library). The soloists and the chorus are read note for note; where the
keyboard reduction's inner voices are hard to read, its harmony, rhythm and register are kept and the voicing is
approximate. The Overture, which the vocal score gives only as a keyboard reduction too small to read reliably, is
read part by part from the full score Handel's publisher's successor William Randall printed in London in 1769
(`judasmacchabaeus00hand_0`, from the University of North Carolina's music library). The timing follows the scores'
tempo markings, and where a number has none, a tempo that suits it; not a recording.

There is no choir in the sample library (the VSCO 2 Community Edition orchestra), so the sung lines are played on
instruments, each character's on its own, and the chorus on strings with woodwinds doubling. Handel's continuo
harpsichord, which the library doesn't have, is a Surge XT harpsichord. Trumpets and timpani are kept for the
martial numbers. The battles get the sounds a staged production would give them, under the music. Every pitch is
Handel's.

## The stage

From the street the porch is the back of the scene, as on the Ring and Elijah stages.

| place on the house | what it is |
|--------------------|------------|
| **Porch Front** | the Temple in Jerusalem, and the glow of the hanukkiah's lights, which stays through the set. |
| **Left** | Modein and the hills, where the Maccabees gather. |
| **Right** | the field of battle, where the Seleucid armies come in. |
| **Free end of Right** | the road from Antioch: enemies enter here. |
| **Porch Left / Porch Right** | the approaches to Jerusalem, and the people lining them. |
| **Side** | the wilderness the Maccabees retreat into. Nothing begins there. |

The scenes are rendered once and play on all eight nights, so they can't show which night it is: the porch carries
the same warm glow every night, and the night's own lights are shown in its candle-lighting show.

## Who is who

| character | colour | voice (sung lines played on) |
|-----------|--------|------------------------------|
| Judas Maccabaeus (tenor) | brass gold `#ffc83c` | trumpets, horns |
| Simon, his brother (bass) | deep blue `#2850c8` | bassoons, cellos |
| Israelitish Woman (soprano) | white-silver `#e8f0ff` | oboe |
| Israelitish Man (alto) | sky blue `#5aa0ff` | flute, violas |
| the Maccabees and the people (chorus) | blue `#1e5bd8` and white `#f2f6ff` | strings, winds doubling |
| the Seleucid armies | royal purple `#6a2ca0`, helmet glints `#c08a40` | low brass, timpani, drums |
| the idols in the Temple | stone grey `#6a6a6a` | |
| the Temple light | olive-oil gold `#ffb33a`, flame tips `#fff1c0` | |

Blue and white are the colours of the tallit, and later of the flag of Israel.

## The cuts

Numbers are the Novello edition's (its index, PDF p. 7); PDF page = printed page + 8. Bars are numbered straight
through each scene's MusicXML (compact numbering), and each scene's docstring says which printed bars they are. The
voices are read note for note; the keyboard reduction's harmony, rhythm and register are kept, its voicing
approximate where the scan is unclear (most in JM11's right hand and JM03's recitative chords).

```sh
# JM01 Overture: from the 1769 Randall full score (PDF pp. 13-14): the Grave's bars 1-4, 18, 19 and the second-time
# chord 21 (here 1-7), at crotchet 60, and the Allegro's bars 1-29 (here 8-36), cut halfway through bar 29 on the F
# major chord, at quaver 112; score() holds the chord 3 s
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/overture.musicxml 1-36.5 --tempo \
    --part P1=Vn1 --part P2=Vn2 --part P3=Va --part P4=Bassi \
    --source "Randall full score (London, 1769), transcribed" --act "Judas Maccabaeus, No. 1, Overture" \
    --out homes/cjimti/sequences/judas-maccabaeus/overture.score.json

# JM02 Mourn, Ye Afflicted Children: No. 2, the upbeat and bars 1-8, bars 17-22 ("Your friend and father is no
# more", to the voices-alone pp) and bars 40-45, the close (compact 1-21), Largo at crotchet 58
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/mourn_ye_afflicted.musicxml 1-9.875 10-22 \
    --tempo --gap 0.4 --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 2" \
    --out homes/cjimti/sequences/judas-maccabaeus/mourn_ye_afflicted.score.json

# JM03 O Father, Whose Almighty Power: No. 8 to "and seas adore!" (bars 1-12, the orchestra's bar before "The heav'ns"
# left out), its Allegro's first four bars, the basses' "And grant a leader bold and brave" (13-16), and the end of
# No. 9, Simon's "To Israel's distressful pray'r" to "victory!" (17-25); Larghetto 50, Allegro 100, the recitative 72
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/o_father.musicxml \
    1.6667-6 6.6667-12.6667 13-16.25 17.25-26 --tempo --gap 0.4 \
    --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Simon --part P6=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 8-9" \
    --out homes/cjimti/sequences/judas-maccabaeus/o_father.score.json

# JM10 We Never Will Bow Down: No. 52, the Andante's first eight bars (p. 133) and last eight (p. 136), the A tempo
# giusto's first seven (p. 137) and the last system's bars 3-8 (p. 140) (compact 1-29); Andante 63, giusto 92
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/we_never_will_bow_down.musicxml \
    1-8.66 9.666-23.5 24.5-30 --tempo \
    --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Orch \
    --source "Novello vocal score (c. 1870), transcribed" --act "Judas Maccabaeus, No. 52" \
    --out homes/cjimti/sequences/judas-maccabaeus/we_never_will_bow_down.score.json

# JM11 Father of Heav'n: No. 53, the air's bars 5-18 (compact 1-14), from the ritornello to "the Feast of Lights.",
# at crotchet 42 (slow for its Andante larghetto, to give the scene its time)
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/father_of_heaven.musicxml 1-14.25 \
    --tempo --part P1=Voice --part P2=Orch \
    --source "Novello vocal score (c. 1870), transcribed" --act "Judas Maccabaeus, No. 53" \
    --out homes/cjimti/sequences/judas-maccabaeus/father_of_heaven.score.json

# JM12 See, the Conqu'ring Hero Comes: No. 58 (its page heading misprints No. 59), the Chorus of Youths (1-8), the
# Full Chorus's "See" (9-16) and "Sports prepare" (17-24), and the last "See" (25-32, as 9-16); unmarked, crotchet 100
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/see_the_conquering_hero.musicxml 1-33 \
    --tempo --part P1=S1 --part P2=S2 --part P3=A --part P4=T --part P5=B --part P6=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 58" \
    --out homes/cjimti/sequences/judas-maccabaeus/see_the_conquering_hero.score.json
```

Notes for later scenes: this copy is a folio print, so `scripts/noteheads.py` reads it at about 285 dpi (staff
spacing about 33 px at 500 dpi), and the tenor is in the C clef on the fourth line (clef `C` in `noteheads.py` and
`staff_lines.py`). The singer of No. 53 isn't named in this printing (Handel's Priest, an alto); JM11 gives the voice
the Israelitish Man's sky blue and flute. JM12 opens on JM11's last frame (its `CARRY`).

## The scenes

| code | title | what happens on the house |
|------|-------|---------------------------|
| JM01 | Overture | The house in Seleucid purple, the Temple on Porch Front grey with idols. A few blue lights hidden on Left, in the hills. |
| JM02 | Mourn, Ye Afflicted Children | Mattathias has died. The people's blue and white lights on the porch runs dim in long falling phrases, a slow lament toward the Temple. |
| JM03 | O Father, Whose Almighty Power | The prayer. The blue lights gather on Left and steady. Simon's deep blue names Judas, and a single brass-gold light appears among them. |
| JM10 | We Never Will Bow Down | The grey idols stand on Porch Front. On "we never will bow down" every blue and white light holds steady, refusing, and the grey cracks and falls away, leaving the Temple dark, empty and clean. |
| JM11 | Father of Heav'n | The Feast of Dedication: olive-oil gold returns to the Temple, slowly, from the middle outward. |
| JM12 | See, the Conqu'ring Hero Comes | Judas returns: one gold light coming up Porch Left toward the Temple, then lights joining him, then the whole house lining the road. |

The rest (JM04-JM09, JM13-JM16) are #72, #73 and #74.
