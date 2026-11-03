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

# JM04 Arm, Arm, Ye Brave!: No. 10, the ritornello's bars 1-4 and Simon's bars 14-27 to "your zeal demands." (compact
# 1-18, cut after its third beat), at crotchet 108, and No. 11, the chorus's bars 1-21 to the first "thy sceptre to
# obey." (19-39) and its last nine bars, 41-49 (40-48), at crotchet 132
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/arm_arm_ye_brave.musicxml 1-18.75 19-49 \
    --tempo --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Simon --part P6=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 10-11" \
    --out homes/cjimti/sequences/judas-maccabaeus/arm_arm_ye_brave.score.json

# JM05 Call Forth Thy Powers: No. 13, the A section and the B section ("Great is the glory") to "restor'd." (bars 1-30,
# cut after its first beat), run into the closing ritornello, bars 43-45 from their second beat (compact 31-33), as
# the da capo would; Allegro at crotchet 96
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/call_forth_thy_powers.musicxml \
    1-30.25 31.25-34 --tempo --part P1=Judas --part P2=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 13" \
    --out homes/cjimti/sequences/judas-maccabaeus/call_forth_thy_powers.score.json

# JM06 Disdainful of Danger: No. 22, "generally sung as a Trio, and repeated in Chorus": the ritornello (bars 1-13),
# the trio from the sign to "foe," (p. 52, 14-22) and its "That thy pow'r" (p. 53, 23-31), pp. 55-56 as the chorus
# repeats it (32-55) and the closing ritornello's last eight bars (56-64); Allegro, quaver 144
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/disdainful_of_danger.musicxml 1.6667-65 \
    --tempo --part P1=A --part P2=T --part P3=B --part P4=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 22" \
    --out homes/cjimti/sequences/judas-maccabaeus/disdainful_of_danger.score.json

# JM07 Fall'n Is the Foe: No. 27, the ritornello's first four bars (1-4), the chorus from its entry to the tutti
# "O Lord!" on C (pp. 69-70, 5-21), and p. 75: the hammered "Fall'n" (22-26) and "Where warlike Judas" to the end
# (27-30, the system's first beat left out); Allegro moderato, crotchet 92
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/fallen_is_the_foe.musicxml 1-27 27.5-31 \
    --tempo --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 27" \
    --out homes/cjimti/sequences/judas-maccabaeus/fallen_is_the_foe.score.json

# JM08 Sion Now Her Head Shall Raise: No. 31, the duet's bars 16-28 (compact 1-13), the end of the ritornello and the
# first voice's (the Woman's) whole first statement, at crotchet 80; No. 32, the chorus's bars 1-18 (14-31) and its
# last seven sung bars, p. 89's second system (32-38), at 88
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/sion_now_her_head.musicxml 1-39 --tempo \
    --part P1=Woman --part P2=S1 --part P3=S2 --part P4=A --part P5=T --part P6=B --part P7=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 31-32" \
    --out homes/cjimti/sequences/judas-maccabaeus/sion_now_her_head.score.json

# JM09 Sound an Alarm!: No. 45, the full-orchestra Allegro on p. 118, its first three systems (compact 1-18), from
# "Sound an alarm!" to Judas's last "Sound an alarm!" (fermata); No. 46, bars 2-16 of p. 119 (19-33) and bars 3-16 of
# p. 121 (34-47), cut after the last chord; dotted crotchet 72
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/sound_an_alarm.musicxml 1-47.5 --tempo \
    --part P1=Judas --part P2=S --part P3=A --part P4=T --part P5=B --part P6=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 45-46" \
    --out homes/cjimti/sequences/judas-maccabaeus/sound_an_alarm.score.json

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

# JM13 March, and Sing unto God: No. 59, the March's first strain (bars 1-12, p. 156), played twice (piano, then forte,
# as the copy's pencilled note asks), at crotchet 112; No. 60 at crotchet 100: p. 161 system 2 bars 2-4, "To crown this
# conquest... with unmeasur'd praise." (13-15); system 3, "Sing unto God... high affections raise" (16-19); p. 162
# system 2 bar 2's last beat, "To" (20); bar 3, "crown" (21); and system 3, the last five bars (22-26)
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/march_and_sing.musicxml \
    1-13 1-13 13.25-19.75 20.75-27 --tempo \
    --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 59-60" \
    --out homes/cjimti/sequences/judas-maccabaeus/march_and_sing.score.json

# JM14 O Lovely Peace: No. 66, the upbeat and the ritornello's first two bars (here 1-3), the first voice's verse and
# the second's from the ritornello's cadence (p. 173 system 2 bar 5 to the end of system 4, here 6-22), the two
# together (p. 174 system 1 bars 1-6, here 23-28), and the Adagio close from "And" to "corn." (p. 175 system 3 bars 2-7,
# here 29-34); Allegro at dotted crotchet 52, Adagio at 30; the singers are unnamed in print
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/o_lovely_peace.musicxml \
    1.8333-4 6-29 29.8333-35 --tempo --part P1=Woman --part P2=Man --part P3=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, No. 66" \
    --out homes/cjimti/sequences/judas-maccabaeus/o_lovely_peace.score.json

# JM15 Rejoice, O Judah: No. 67, Simon's first phrase from the upbeat "Re-" to "harmonious join." (its bars 14-18, here
# 1-5, cut 1.75-5.75), Andante allegro at crotchet 88; No. 68, the basses' opening "Hallelujah, Amen" (bars 1-2, here
# 6-7) and "O Judah, rejoice" to the end (bars 14-37, here 8-31), Allegro 100, the Adagio from bar 34's second beat at 54
uv run python scripts/score_excerpt.py homes/cjimti/sequences/judas-maccabaeus/rejoice_o_judah.musicxml 1.75-5.75 6-32 \
    --tempo --part P1=Simon --part P2=S --part P3=A --part P4=T --part P5=B --part P6=Orch \
    --source "Novello vocal score (Vincent Novello, c. 1870), transcribed" --act "Judas Maccabaeus, Nos. 67-68" \
    --out homes/cjimti/sequences/judas-maccabaeus/rejoice_o_judah.score.json
```

Notes for later scenes: this copy is a folio print, so `scripts/noteheads.py` reads it at about 285 dpi (staff
spacing about 33 px at 500 dpi), and the tenor is in the C clef on the fourth line (clef `C` in `noteheads.py` and
`staff_lines.py`). Several singers aren't named in this printing: No. 53 (Handel's Priest, an alto), which JM11 gives
the Israelitish Man's sky blue and flute; No. 67's "Bass Voice", which JM15 gives Simon; and the two voices of No. 66,
which JM14 gives the Israelitish Woman and Man. No. 32 (JM08) is a five-part chorus with a soprano solo, given to the
Woman.

Every scene opens on the last frame of the one before it. Where the two are built differently, the later scene
rebuilds the earlier one's last frame in its own code and crossfades out of it over its first seconds (`CARRY`, and a
function named for the earlier scene's end, such as `jm05_end()` in JM06): change both scenes together. JM09 settles
onto JM10's first frame the same way, and the intermission (JM16) hands over to the Overture's first frame.

## The scenes

| code | title | what happens on the house |
|------|-------|---------------------------|
| JM01 | Overture | The house in Seleucid purple, the Temple on Porch Front grey with idols. A few blue lights hidden on Left, in the hills. |
| JM02 | Mourn, Ye Afflicted Children | Mattathias has died. The people's blue and white lights on the porch runs dim in long falling phrases, a slow lament toward the Temple. |
| JM03 | O Father, Whose Almighty Power | The prayer. The blue lights gather on Left and steady. Simon's deep blue names Judas, and a single brass-gold light appears among them. |
| JM04 | Arm, Arm, Ye Brave! | Simon's deep blue calls, and on each bar a blue or white light steps into a rank along Left; the chorus answers "We come, in bright array" and the rank marches in place on the beat. On each "Judah" Judas's gold flares and the purple on Right shrinks back. |
| JM05 | Call Forth Thy Powers | Judas's gold follows his voice up and down the rank on Left; every light it passes flares and stays brighter, each "sword" is a white stroke, and the closing runs send a spark down the rank. |
| JM06 | Disdainful of Danger | The Maccabees go out to fight: three voices step out ahead of the ranks on Left, then the chorus takes it up and the whole column marches round the corner and down Porch Left, Judas leading. |
| JM07 | Fall'n Is the Foe | The first victory: the blue and white sweep onto the field on Right, every "Fall'n" breaks a block of Seleucid purple that scatters back to the road from Antioch, and Judas's gold swings like a sword at the end. |
| JM08 | Sion Now Her Head Shall Raise | The Woman's white-silver climbs Porch Left as she sings and warm gold rises from the porch runs toward the Temple; harp glints climb the porch on every "Tune your harps", and the chorus lifts the whole house. |
| JM09 | Sound an Alarm! | Judas's gold calls on Left as purple pours in from the free end of Right; on "We hear" the blue and white ranks charge across the house behind him and meet it on Porch Right, steel clashing on every stroke, until the purple is driven off the end. |
| JM10 | We Never Will Bow Down | The grey idols stand on Porch Front. On "we never will bow down" every blue and white light holds steady, refusing, and the grey cracks and falls away, leaving the Temple dark, empty and clean. |
| JM11 | Father of Heav'n | The Feast of Dedication: olive-oil gold returns to the Temple, slowly, from the middle outward. |
| JM12 | See, the Conqu'ring Hero Comes | Judas returns: one gold light coming up Porch Left toward the Temple, then lights joining him, then the whole house lining the road. |
| JM13 | March, and Sing unto God | The people's blue and white march toward the Temple along every run, a pace on each beat, gold joining them the second time; every chord of "To crown this conquest" lifts the whole house, and gold pours from the Temple for "Sing unto God". |
| JM14 | O Lovely Peace | The purple is long gone: slow, wide waves of corn gold and pasture green; the Woman's white-silver on Left, the Man's sky blue answering on Right, coming in along the porch runs together, settling to a steady gold. |
| JM15 | Rejoice, O Judah | Simon's deep blue calls Judah to rejoice and the basses answer; then the whole house bursts into blue and white with gold in the Temple, a wave of gold on every Hallelujah, white and gold on every Amen, and on the last Amen it all settles back to the glow on the porch. |
| JM16 | Intermission | Five minutes: the house waits in blue, and white fills it from both wings toward the porch, the lights' glow steady on the Temple, to the quiet numbers of the set; the Overture's Grave on horns and trumpets calls the street back. |

Every scene, and every candle-lighting show, has a spoken intro (`VOICEOVER`), over the Hanukkah bed in
`pixelhome/intro.py` (Ma'oz Tzur's first notes on an oboe). None of them says the Hebrew blessings: those are said
over kindling a real hanukkiah.
