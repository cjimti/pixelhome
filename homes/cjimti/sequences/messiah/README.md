# Messiah on the roofline

Handel's *Messiah* (HWV 56), Part One and the Hallelujah chorus, in 15 shows of about 85 seconds, `MS01`..`MS15`,
plus an intermission (`MS16`), for the nights from the end of Hanukkah through Christmas. It is a playlist under the
Christmas occasion (`messiah` in `pixelhome/occasions.py`). Ticket: #44; epic: #45.

## About the work

Handel composed *Messiah* in about three and a half weeks in August and September 1741. It was first performed in
Dublin on 13 April 1742, in the Great Music Hall on Fishamble Street, as a benefit for prisoners and hospitals. The
libretto is Charles Jennens's, and every word of it is scripture, from the King James Bible and the psalter of the
Book of Common Prayer.

It was written for Lent and Easter; the Christmas tradition came later, because Part One is the prophecy and the
nativity. This set plays Part One, mostly Isaiah, with Malachi, Haggai and Luke's shepherds, and closes with the
Hallelujah from Part Two, as many Christmas performances do.

There are no characters. The soloists narrate and reflect; nobody plays Mary, the shepherds or the angel. On the
house the soloists are voices of light, and the chorus is the whole house.

It ends a season of three oratorios on the house, after Mendelssohn's *Elijah* and Handel's *Judas Maccabaeus*, and
the three share the Hebrew prophets. *Elijah* closes on Malachi's promise that Elijah will return; *Messiah* opens its
prophecy with Malachi too: "The Lord, whom ye seek, shall suddenly come to His temple." Christian tradition reads
these passages of Malachi and Isaiah as prophecies of Christ, and that is the reading Jennens's libretto sets; Jewish
tradition reads them differently. Each set presents its own work's tradition on its own nights.

Every note is Handel's, transcribed by hand from Ebenezer Prout's edition of the full score (Novello, London, 1902):
the strings, the voices, and the trumpets and timpani where Handel has them. There is no choir in the sample library,
so the sung lines are played on instruments, every voice with its own colour and instrument, and the lights follow
the notes.

## The stage

From the street the porch is the back of the scene, as on the house's other oratorio and opera stages.

| place on the house | what it is |
|--------------------|------------|
| **Porch Front** | the far light: where the glory appears, where the angel speaks from, where the trumpets sound from afar. |
| **Left and Right** | the land and the people, and in the nativity scenes the fields with the shepherds. |
| **Porch Left / Porch Right** | the way between: the road, the highway in the desert. |
| **Side** | the bed and the full-house moments. |

Any star in the set hangs where the Christmas playlist's star does, over the middle of Porch Front.

## Who is who

| voice | colour | played on |
|-------|--------|-----------|
| tenor (Comfort ye, Ev'ry valley) | warm white `#fff0d8` | violins and oboe |
| bass (Thus saith the Lord, The people that walked in darkness) | deep amber `#e08a20` | cellos and bassoon |
| alto (But who may abide, O thou that tellest, He shall feed His flock) | soft rose-violet `#c890d8` | violas, clarinet |
| soprano (the angel's narration, Rejoice greatly) | silver `#e6f0ff` | flute and oboe |
| chorus | the whole house, white-gold `#fff2c8` | strings, winds doubling, organ |
| trumpets | bright gold `#ffd040` | trumpets |
| darkness | deep blue-black `#06081a` | |
| the refiner's fire | white `#ffffff` and gold `#ffb020` | |

## Where the music comes from

Every note is transcribed by hand from Ebenezer Prout's edition of the full score (Novello and Company, London,
1902), read from the copy on the Internet Archive (`messiahsacredora00hand_0`, from the University of Toronto's
music library). PDF page = printed page + 26. A full score has each part on its own staff, so the strings are read
part by part, not guessed from a keyboard reduction. Only Handel's parts are kept: the strings, the voices, and the
two trumpets and timpani in Nos. 17 and 44. Prout's "additional accompaniments" (flutes, oboes, clarinets,
bassoons, horns, trombones and organ, his re-writing of Mozart's) are left out; the orchestration here adds its own
doublings, as a performance would. Prout's chords for strings in the secco recitatives, printed for use without a
keyboard, are read where a scene uses them (Nos. 14, 15 and 19) and left out elsewhere (No. 8).

The timing follows the score's tempo marks, not a recording; where a scene needed a little more speed to fit, the
command and the scene's docstring say so. There is no choir in the sample library (the VSCO 2 Community Edition
orchestra), so the sung lines are played on instruments: the soloists each on their own (see who is who above),
the chorus on strings with oboes and bassoons doubling and the VSCO2 organ under the big choruses, and a Surge XT
harpsichord for the continuo. The trumpets are held back until "Glory to God", their first entry in the work, and
play there on their own distant, reverberant bus ("da lontano"). A staged production would add sounds where the
lights show an event (the thunder under "I will shake the heavens", the fire under "refiner's fire", cymbal swells
into the glory), so these scenes add them too. Every pitch is Handel's.

## The cuts

Each scene's numbers are transcribed into MusicXML beside it (`<name>.musicxml`: the soloists, the chorus's sopranos,
altos, tenors and basses, each string part, the trumpets and timpani, each on its own part), with the helpers in
`scripts/` (`noteheads.py` and `staff_lines.py`, with the alto clef `A` for the violas, `shorthand.py`,
`clash.py`). Only the bars a scene plays are transcribed; the rest stay empty so the measure numbers match the score.
Several numbers in one scene are numbered on (the scene's docstring and the comment say how).

Reading the full score: the scan's pages are tilted by up to a degree, which throws off notehead detection across a
whole page (straighten the page image first); staff spacing is about 24.4 px at 500 dpi; heads on ledger lines above
the staff can read a step high.

```sh
# MS01 Sinfony: No. 1 (pp. 1-7): the Grave's bars 1-4, 9-11 and the second-time chord (printed as bar 12; the
# first-time bar is left out), at crotchet 60; the fugue's exposition, bars 13-25 cut after beat 2 at the first
# cadence, at 116; and the end from the ff entry at the letter F, bars 86-97, Più lento (unmarked) at 80
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/sinfony.musicxml 1-5 9-25.5 86-98 --tempo \
    --part P1=Vn1 --part P2=Vn2 --part P3=Va --part P4=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 1, Sinfony" \
    --perf "Grave at crotchet 60 and Allegro moderato at 116, as marked; Piu lento at 80" \
    --out homes/cjimti/sequences/messiah/sinfony.score.json

# MS02 Comfort Ye: No. 2 (pp. 8-10): the opening and the tenor's first "Comfort ye" to the ad lib. "Comfort ye"
# (bars 1-8), Larghetto at quaver 76 (Prout marks 72), the ad lib. bar at crotchet 30; and the recitative from the
# letter C, "The voice of him that crieth" to "for our God" (bars 30-37), at crotchet 72
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/comfort_ye.musicxml 1-9 30-38 --tempo \
    --part P1=Tenor --part P2=Vn1 --part P3=Vn2 --part P4=Va --part P5=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 2" \
    --perf "Larghetto at quaver 76 (Prout marks 72), the ad lib. bar at crotchet 30, the recitative at crotchet 72" \
    --out homes/cjimti/sequences/messiah/comfort_ye.score.json

# MS03 Ev'ry Valley: No. 3 (pp. 11-18): the ritornello's opening (bars 1-3, cut before the upbeat), the tenor's first
# "Ev'ry valley" to the first "exalted" (10-20.75; the second long run left out), "and ev'ry mountain" to the first
# long "plain" (24.5-33.25), the Adagio close from the upbeat "the" (72.875-76.5) and the closing ritornello's last
# bars (82.875-84); Andante at crotchet 84 (Prout marks 80), Adagio at 46
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/every_valley.musicxml 1-3.75 10-20.75 24.5-33.25 \
    72.875-76.5 82.875-85 --tempo --part P1=Tenor --part P2=Vn1 --part P3=Vn2 --part P4=Va --part P5=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 3" \
    --perf "Andante at crotchet 84 (Prout marks 80), Adagio at 46; fermatas doubled" \
    --out homes/cjimti/sequences/messiah/every_valley.score.json

# MS04 And the Glory of the Lord: No. 4 (pp. 19-35): the ritornello's last two bars and the altos' entry to the first
# round of "shall be revealed" (bars 9-24), the tutti "and the glory ... shall be revealed" (33-38), "and all flesh
# shall see it together" to the first "hath spoken it" (43-56), and the close from "it, for the mouth of the Lord"
# through the Adagio (129-138); Allegro at crotchet 108 (Prout marks 100), Adagio at crotchet 54
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/and_the_glory.musicxml 9-25 33-39 43-57 129-139 \
    --tempo --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Vn1 --part P6=Vn2 --part P7=Va --part P8=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 4" \
    --perf "Allegro at crotchet 108 (Prout marks 100), Adagio at crotchet 54" \
    --out homes/cjimti/sequences/messiah/and_the_glory.score.json

# MS05 But Who May Abide: No. 5, bars 1-8 ("Thus saith the Lord" to "the heav'ns and the earth,", the strings'
# upbeat figure at the end of bar 8 left out), Allegro maestoso at crotchet 84 (Prout 76); No. 6 numbered on (bar n =
# 40 + n): bars 12-18 (the ritornello's last chord, "But who may abide the day of His coming?" and the strings' echo,
# cut before "and who"), Larghetto at quaver 96 (88); the Prestissimo's bars 59-72 ("For He is like a refiner's fire"
# twice, ending on the D7), crotchet 144 (138); the Adagio, bars 148-150, at 60 (unmarked), and the last Prestissimo,
# bars 151-158 to the final chord, at 144
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/but_who_may_abide.musicxml 1-9 52-58.6667 99-113 \
    188-198.5 --tempo --gap 0.4 --part P1=Bass --part P2=Alto --part P3=Vn1 --part P4=Vn2 --part P5=Va --part P6=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 5-6" \
    --perf "Allegro maestoso at crotchet 84 (Prout marks 76), Larghetto at quaver 96 (88), Prestissimo at crotchet 144 (138), Adagio at 60" \
    --out homes/cjimti/sequences/messiah/but_who_may_abide.score.json

# MS06 And He Shall Purify: No. 7 (pp. 51-64): the sopranos' subject and the entries of the basses, altos and tenors
# to the full chorus's "and He shall purify" (bars 1-16), and the close from "of Levi" through "that they may offer
# unto the Lord an offering in righteousness" and the strings' last bars (51-58); Allegro at crotchet 72, as marked
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/and_he_shall_purify.musicxml 1-17 51-59 --tempo \
    --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Vn1 --part P6=Vn2 --part P7=Va --part P8=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 7" \
    --perf "Allegro at crotchet 72, as Prout marks it" \
    --out homes/cjimti/sequences/messiah/and_he_shall_purify.score.json

# MS07 O Thou That Tellest: No. 8 whole (bars 1-6, the voice and the Bassi; the string chords on p. 65 are Prout's, for
# use without a keyboard, and are left out), at crotchet 80; No. 9 numbered on (bar n = 10 + n): bars 12-15 (the
# voice's first "O thou that tellest good tidings to Zion," and the strings' answer), bars 75-83 to "come:" ("arise,
# shine" and the three "arise"s), the chorus's upbeat and bars 107-110 to the sopranos' "Jerusalem," (cut before the
# altos' "O"), the tutti "arise, arise," (bar 114's upbeat to 116, cut before "say"), and "glory of the Lord is risen
# upon thee." (bars 135-138, cut after the final chord's first quaver; score() holds it 3 s); Andante at quaver 138,
# as marked
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/o_thou_that_tellest.musicxml \
    1-7 22-26 85-93.8333 116.8333-120.8333 124.8333-126.8333 145-148.1667 --tempo --gap 0.4 \
    --part P1=Alto --part P2=S --part P3=A --part P4=T --part P5=B --part P6=Vn1 --part P7=Vn2 --part P8=Va --part P9=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 8-9" \
    --perf "Recitative at crotchet 80, Andante at quaver 138, as marked" \
    --out homes/cjimti/sequences/messiah/o_thou_that_tellest.score.json

# MS08 The People That Walked in Darkness: No. 10 (p. 85) bars 1-2 and from "For behold" to the second "the people:"
# (5.75-10), at quaver 96 (Prout marks 72); No. 11 (pp. 87-88) numbered on (its upbeat bar 12, its bar n = 12 + n),
# from the upbeat to the second "have seen a great light" (its bars 0-13.75, here 12-25.75), Larghetto at crotchet 72;
# score() holds the D major chord 3 s
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/darkness.musicxml 1-3 5.75-11 12-25.75 --tempo \
    --part P1=Bass --part P2=Vn1 --part P3=Vn2 --part P4=Va --part P5=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 10-11" \
    --perf "Andante larghetto at quaver 96 (Prout marks 72), Larghetto at crotchet 72, as marked" \
    --out homes/cjimti/sequences/messiah/darkness.score.json

# MS09 For Unto Us a Child Is Born: No. 12 (pp. 93-114): the ritornello's last bar and the sopranos' first "For unto us
# a Child is born, unto us a Son is given" (bars 6 to halfway through 10), "upon His shoulder" to the first names
# (29-37), the last names to the final cadence (83-91), and the strings' last two bars (98-99); Andante allegro at
# crotchet 76, as marked
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/for_unto_us.musicxml 6-10.5 29-38 83-92 98-100 \
    --tempo --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Vn1 --part P6=Vn2 --part P7=Va --part P8=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 12" \
    --perf "Andante allegro at crotchet 76, as Prout marks it" \
    --out homes/cjimti/sequences/messiah/for_unto_us.score.json

# MS10 Pifa: No. 13 (pp. 115-116): the opening phrase over the C drone (bars 1-4), the middle section from the
# letter A over the G drone to its half close (bars 12 and 14-21; bar 13, a repeat of 14's figure, left out), and the
# da capo's last two bars with the fermata (31-32); Larghetto at quaver 132, as marked
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/pifa.musicxml 1-5 12-13 14-22 31-33 --tempo \
    --part P1=Vn1 --part P2=Vn2 --part P3=Va --part P4=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 13, Pastoral Symphony" \
    --perf "Larghetto at quaver 132, as marked; the last fermata held twice its length" \
    --out homes/cjimti/sequences/messiah/pifa.score.json

# MS11 There Were Shepherds: Nos. 14 and 15 complete (pp. 117-118), numbered on: No. 14's secco bars 1-4, the
# accompagnato "And lo" bars 5-11, No. 15 bars 12-20; seccos at crotchet 80, the accompagnato at Prout's 56
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/there_were_shepherds.musicxml 1-21 --tempo \
    --part P1=Soprano --part P2=Vn1 --part P3=Vn2 --part P4=Va --part P5=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 14-15" \
    --perf "Recitatives at crotchet 80, the accompagnato Andante at crotchet 56, as marked" \
    --out homes/cjimti/sequences/messiah/there_were_shepherds.score.json

# MS12 Glory to God: No. 16, the soprano's whole recitative (bars 3-8), at crotchet 72; No. 17 (numbered on, bar n =
# 8 + n) bars 1-7 (here 9-15), 10-16 at A (18-24), 26-28 at C (34-36) and 40-42 cut halfway through bar 42 on "men."
# (48-50.5), at Prout's crotchet 80; score() holds the last chord 3 s
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/glory_to_god.musicxml 3-16 18-25 34-37 48-50.5 \
    --tempo --part P1=Soprano --part P2=S --part P3=A --part P4=T --part P5=B --part P6=Tr1 --part P7=Tr2 \
    --part P8=Vn1 --part P9=Vn2 --part P10=Va --part P11=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 16-17" \
    --perf "Prout's tempo marks: the recitative at crotchet 72, the chorus at 80" \
    --out homes/cjimti/sequences/messiah/glory_to_god.score.json

# MS13 Rejoice Greatly: No. 18 (pp. 127-134): the ritornello's last bar through the first statement and the strings'
# answer, to the F major cadence on bar 25's third beat (8-25.75), the return's "rejoice ... and shout, shout, shout,
# shout, rejoice greatly" (84.25-90.25), the closing ritornello's cadence (105-108); Allegro at Prout's crotchet 88
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/rejoice_greatly.musicxml 8-25.75 84.25-90.25 \
    105-109 --tempo --part P1=Soprano --part P2=Vn1 --part P3=Vn2 --part P4=Va --part P5=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 18" \
    --perf "Allegro at crotchet 88, as marked" --out homes/cjimti/sequences/messiah/rejoice_greatly.score.json

# MS14 He Shall Feed His Flock: No. 19 complete and from No. 20 (pp. 135-137), No. 20 numbered on (its upbeat bar 9,
# its bar n = 9 + n): the recitative to the "sing." chords (1-8.5), the alto from its upbeat "He" to "with His arm"
# (its bars 4-9, here 13.9167-18.75), the soprano from her upbeat "Come" to "He will give you rest" and the next
# downbeat's B flat chord (its bars 25-31, here 34.9167-40.1667); recitative at crotchet 88 (a little quicker to
# fit), the Larghetto at Prout's quaver 112
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/he_shall_feed_his_flock.musicxml 1-8.5 \
    13.9167-18.75 34.9167-40.1667 --tempo \
    --part P1=Alto --part P2=Soprano --part P3=Vn1 --part P4=Vn2 --part P5=Va --part P6=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, Nos. 19-20" \
    --perf "Recitative at crotchet 88, the Larghetto at quaver 112, as marked" \
    --out homes/cjimti/sequences/messiah/he_shall_feed_his_flock.score.json

# MS15 Hallelujah: No. 44, the first Hallelujahs (4-7, to the rest), "For the Lord God omnipotent reigneth" and the
# answering Hallelujahs where trumpets and timpani enter (12-14, 16), "The kingdom of this world is become" (from the
# upbeat of 34 to "-come,"), the three held steps of King of Kings (51.5-54, 57.5-60, 63.5-66) into the fortissimo
# "and Lord of Lords" (to the first half of 69), and the end (90, second beat, to 94); crotchet 84 (Prout marks 72),
# the grand pause held 1.5 s longer, the last Hallelujah Adagio at 58 (Handel's autograph mark; Prout prints none);
# score() holds the chord 2.5 s
uv run python scripts/score_excerpt.py homes/cjimti/sequences/messiah/hallelujah.musicxml 4-7.75 12-15 16-16.75 \
    33.75-37.75 51.5-54.25 57.5-60.25 63.5-69.5 90.25-95 --tempo --hold 92.5=1.5 --part P1=S --part P2=A --part P3=T \
    --part P4=B --part P5=Tr1 --part P6=Tr2 --part P7=Timp --part P8=Vn1 --part P9=Vn2 --part P10=Va --part P11=Bassi \
    --source "Prout full score (Novello, London, 1902), transcribed" --act "Messiah, No. 44" \
    --perf "crotchet 84 (Prout marks 72), the last Hallelujah Adagio at 58 after a held grand pause" \
    --out homes/cjimti/sequences/messiah/hallelujah.score.json
```

## The scenes

| code | title | length | what happens on the house |
|------|-------|-------:|---------------------------|
| MS01 | Sinfony | 1:28 | The overture: the Grave's heavy dotted pulses roll along the house in deep blue, then the fugue's four voices enter one run at a time, each string part its own light. |
| MS02 | Comfort Ye | 1:21 | The tenor's warm white light alone on Porch Front, opening a little wider with each "comfort ye"; then "the voice of him that crieth in the wilderness", and the light finds the road. |
| MS03 | Ev'ry Valley | 1:28 | The roofline as a landscape of bright hills and dark valleys. The tenor sings, and the porch valley rises behind his voice, the hills sink, the crooked land straightens, until the house is one level light. |
| MS04 | And the Glory of the Lord | 1:27 | The first chorus: glory rises white-gold on Porch Front and spreads out run by run, each voice of the choir lighting its own part of the house, until the whole house shines on "hath spoken it". |
| MS05 | But Who May Abide | 1:27 | "I will shake the heavens": the bass's amber makes the house tremble. Then the alto's calm rose light alternates with the refiner's fire, white-hot and fast, sparks thrown off along the roofline. |
| MS06 | And He Shall Purify | 1:22 | The chorus's running semiquavers race along the roofline as fine bright lines, burning off the dark impurities in sparks, until the whole house shines clean gold. |
| MS07 | O Thou That Tellest | 1:20 | The alto's rose light tells good tidings in a gentle lilt; on every "arise, shine" the house brightens another step, and the chorus joins in white-gold. |
| MS08 | The People That Walked in Darkness | 1:22 | Darkness covers the earth: the house sinks to its deepest blue-black, one dim light wanders the roofline feeling its way, and on "a great light" Porch Front opens. |
| MS09 | For Unto Us a Child Is Born | 1:20 | Light running figures for "unto us a Child is born", then the five great names, each a full blaze on its own run, Wonderful on Left round to the Prince of Peace on Right, and the same runs answer every time the names return. |
| MS10 | Pifa | 1:27 | The Pastoral Symphony: night fields on Left and Right, small soft lanterns swaying to the siciliano, and a low warm drone glowing on the porch. |
| MS11 | There Were Shepherds | 1:12 | Shepherds' lanterns in the night fields on the wings; the angel's silver climbs the porch with the strings' rising figures, the glory of the Lord pours over the fields, and the angel says: fear not. |
| MS12 | Glory to God | 1:22 | A multitude of the heavenly host: silver multiplies across the house, the trumpets sound for the first time from the far porch in bright gold, and peace on earth glows warm on the fields. |
| MS13 | Rejoice Greatly | 1:18 | The soprano's coloratura as quick silver runs racing along the roofline, the violins throwing gold sparkles, four bursts of silver on "shout", and the house landing in full gold. |
| MS14 | He Shall Feed His Flock | 1:28 | Slow, wide, warm waves roll in toward the porch to the siciliano, and the house's lights gather there like a flock: first to the alto's rose, then around the soprano's silver, "Come unto Him". |
| MS15 | Hallelujah | 1:26 | The finale: full-house bursts on every Hallelujah, the unison "For the Lord God omnipotent reigneth" as one steady line, the sopranos' King of Kings climbing round the house run by run, and after Handel's grand pause the last chord in full warm gold. |
| MS16 | Intermission | 5:00 | The house waits in night blue under a small star over the porch, and warm gold fills it from both wings over five minutes, until the gold meets under the star and Messiah begins again. |

Fifteen shows, about 21 minutes, and the five-minute intermission: the house waits in night blue under a small star
over the porch while gold fills it, to the set's quiet numbers (Pifa, He shall feed His flock, Comfort ye), and the
Sinfony's Grave calls the street back. Every scene has a spoken intro (`VOICEOVER`) over the Messiah bed in
`pixelhome/intro.py` (a distant trumpet's D, A and D, strings holding D major, a harp after the last word).

"His yoke is easy" (No. 21), Part One's own closing chorus, is left out to end on the Hallelujah. Parts Two and Three
can come back at Easter as their own set (#44).

## Readings to check by ear

The voices and the bassi were read note by note; the inner strings are less certain where semiquaver beams merge
with the heads. The places the transcriptions are least sure of:

- MS01: Grave bar 10 bassi D3 (no accidental seen); bars 86, 95, 96 viola notes.
- MS02: the tenor's ad lib. rhythm in bar 8; the violins' demisemiquaver figures in bars 1-3.
- MS04: Vn1 ledger notes in bars 14-16; violas in bars 37-38.
- MS05: No. 6 bars 62, 64, 65, 71 inner strings; bar 72, the alto's "fire," taken at the lower of Prout's two octaves.
- MS06: violin semiquavers in bars 51-54 partly rebuilt from the figure's pattern.
- MS07: the viola's double stops in No. 9 bars 80-81, approximated.
- MS09: the violins' semiquaver figure under the names (bars 33-37 and 85-86).
- MS10: bar 20 bass and Vn2 rhythm; bar 21 Vn1.
- MS11, MS14: inner notes of Prout's secco chords (Nos. 14, 15, 19).
- MS12: No. 17 second violins in bars 3, 4, 10, 28; bar 40 bass and second trumpet.
- MS13: No. 18 violas in bars 8, 12, 86, 107; the splice from "rejoice greatly" into the closing ritornello.
- MS15: trumpets and timpani in bars 90-93; violins in 16 and 90-91. The first "King of Kings" on A4, sopranos and
  altos in unison, is as printed.
