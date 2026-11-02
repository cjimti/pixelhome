# Elijah on the roofline

Mendelssohn's *Elijah* (Op. 70, 1846) in 23 shows of about 85 seconds, `EL01`..`EL23`, plus an intermission
(`EL24`), played in order (#41). Each scene plays Mendelssohn's actual notes, cut from the most dramatic passages of
a number, and stages them the way the Ring scenes do: every character has a colour and an instrument, and the
lights follow the notes. It is its own occasion (`elijah` in `pixelhome/occasions.py`) and is meant to run on the
Ring nights, between Wagner's operas.

## About the work

*Elijah* (Op. 70) is Felix Mendelssohn's oratorio on the prophet Elijah, staged on the house scene by scene.

Mendelssohn wrote it for the Birmingham Festival, where he conducted its first performance, in English, at
Birmingham Town Hall on 26 August 1846; he revised it for London the next year. The text, by Julius Schubring in
German and translated into English by William Bartholomew, follows the books of Kings.

Elijah foretells a drought on Israel. He raises a widow's son, then challenges the priests of Baal on Mount Carmel:
their god does not answer, and fire falls from heaven on Elijah's altar. The rain returns. Hunted by Queen Jezebel,
Elijah flees into the wilderness, where an angel feeds him, and on Mount Horeb God passes by, not in the wind, the
earthquake or the fire, but in a still, small voice. At the end he is carried up to heaven in a chariot of fire.

Each scene plays Mendelssohn's own notes, transcribed by hand from a public-domain vocal score (Novello, Ewer and
Co., London, 1870 and 1881) and timed by its tempo markings. There is no choir in the sample library, so the sung lines are
played on orchestral instruments; every character has a colour and an instrument, and the lights follow the notes.
God never appears as a figure, only in what light does: fire that falls, rain that comes, a single faint point at
Horeb.

All 23 scenes are built, from Elijah's curse to the last Amen, about 31 minutes, with a five-minute intermission
before them in which the drought turns to rain while the oratorio's quiet numbers play softly. Part One runs from
the curse and the drought through the contest on Mount Carmel, the priests of Baal calling on a god who does not
answer (with Mendelssohn's silences frozen on the house), the fire from heaven, and the rain. Part Two runs from the
voice calling Israel and Jezebel's fury through Elijah's flight into the wilderness, the angels who watch over him,
Horeb, where God is not in the wind, the earthquake or the fire but in the still small voice, and the chariot of
fire, to Malachi's promise that Elijah will come again and the light of morning. It is the start of an oratorio
season on the house, with Handel's *Judas Maccabaeus* and *Messiah* to follow.

## Where the music comes from

There is no dataset like the Ring's for *Elijah*, so every note is transcribed by hand from a public-domain score,
the Novello, Ewer and Co. octavo vocal score, read from two printings of the same plates on the Internet Archive:
London, 1881 (`31761122531270`), and the 1870 printing (`elijahoratorioin00mend`), which is clean where the 1881
copy's pages are covered and has the pages it lacks. The soloists and the chorus's sopranos, altos, tenors and basses
are read note for note. Where the piano reduction's inner voices were hard to read in the scan, the harmony, rhythm
and register are kept and the voicing is approximate.

The timing follows the score's own tempo markings, not a recording: each passage at its marked metronome speed,
fermatas held twice as long, and Mendelssohn's silences in "Baal, hear and answer" held as a conductor would hold
them.

There is no choir in the sample library (the VSCO 2 Community Edition orchestra), so the sung lines are played on
instruments: every character has an instrument of their own (see who is who below), the chorus plays on strings with
woodwinds doubling, and the organ Mendelssohn's score has joins the big choruses. A staged production would add
thunder with the lightning, wind, fire, rain and hoofbeats, so these scenes add them too, wherever the lights show
them. Every pitch is Mendelssohn's.

## The cuts

Each number is transcribed into MusicXML beside its scene (`<name>.musicxml`: the soloists, the sopranos, altos,
tenors and basses as their own parts, the accompaniment as a two-staff piano part), with the helpers in `scripts/`
(`noteheads.py` and `staff_lines.py` to read pitches off 500 dpi scans, `shorthand.py` to turn a notes file into
MusicXML checking every bar adds up, `clash.py` to catch misreads). `scripts/score_excerpt.py` cuts the bars a scene
uses into `<name>.score.json`, the same shape the Ring scenes load with `pixelhome.ring.excerpt()`, each note
labelled with its part (`S`, `A`, `T`, `B`, a soloist's name, `Orch`).

The timing comes from the score's own tempo markings (`--tempo`): fermatas held twice as long, and pauses a
conductor would take (Mendelssohn's silences in No. 13) added with `--hold`. The `perf` field of each JSON says
how it was timed. EL09, for example:

```sh
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/hear_and_answer.musicxml 1-78 --tempo \
    --hold 72=1.5 --hold 76=2.0 --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 13: Baal! hear and answer" \
    --perf "Presto, dotted crotchet = 126, as marked; fermatas doubled, the silences held" \
    --out homes/cjimti/sequences/elijah/hear_and_answer.score.json
```

EL09 transcribes the whole number. The other scenes transcribe only the bars they play: the bars a scene leaves out
stay empty in its MusicXML, so the measure numbers still match the score (the numbers count from the number's first
bar, the recitative included). The scene's cut, in the commands below, splices the transcribed passages together.

```sh
# EL01 The Curse: the Introduction (bars 1-12) and the Overture's upbeat and first nine bars (13-22), cut on the
# downbeat of bar 22; from the 1870 printing, whose first pages the 1881 copy lacks
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_curse.musicxml 1-22.25 --tempo \
    --part El.=Elijah --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70: Introduction (As God the Lord of Israel liveth) and Overture" \
    --perf "Grave, crotchet = 60; Overture, crotchet = 92, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/the_curse.score.json

# EL02 Help, Lord!: No. 1 bars 1-14 and No. 2 bars 0-4 (15-19), the unison "Lord, bow thine ear"
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/help_lord.musicxml 1-20 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 1: Help, Lord!; No. 2: Lord, bow thine ear" \
    --perf "Andante lento, crotchet = 76; Sostenuto ma non troppo, quaver = 100, as marked" \
    --out homes/cjimti/sequences/elijah/help_lord.score.json

# EL03 Rend Your Hearts: No. 3 to "rend your hearts" (bars 1-2), No. 4 bars 1-19 (3-21) and No. 5 bars 1-18
# (22-39), cut before the basses' "His"; from the 1870 printing, whose pp. 17-18 the 1881 copy lacks
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/rend_your_hearts.musicxml 1-2.6875 3-39.75 \
    --tempo --part Ob.=Obadiah --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 3: Ye people, rend your hearts; No. 4: If with all your hearts; No. 5: Yet doth the Lord see it not" \
    --perf "Recitative at crotchet = 72; Andante con moto, crotchet = 72; Allegro vivace, minim = 96, as marked" \
    --out homes/cjimti/sequences/elijah/rend_your_hearts.score.json

# EL04 The Angels' Charge: No. 6 (bars 1-9) and the first 27 bars of No. 7 (10-36), cut halfway through bar 36,
# before the first quartet's "That their hands"; from the 1870 printing, whose pp. 29-32 the 1881 copy lacks
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_angels_charge.musicxml 1-36.5 --tempo \
    --part An.=Angel --part "S. 1=S1" --part "S. 2=S2" --part "A. 1=A1" --part "A. 2=A2" --part "T. 1=T1" \
    --part "T. 2=T2" --part "B. 1=B1" --part "B. 2=B2" --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 6: Elijah, get thee hence; No. 7: For He shall give His angels charge over thee" \
    --perf "Recitative at crotchet = 72, Andante at 66; Allegro non troppo, crotchet = 126, as marked" \
    --out homes/cjimti/sequences/elijah/the_angels_charge.score.json

# EL05 The Widow's Son: No. 8, the widow's plea (bars 13-25), Elijah's three prayers (67-71, 86-92, 111-114) and the
# son reviving (115-121); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_widows_son.musicxml 13-26 67-72 86-93 111-122 \
    --tempo --part W.=Widow --part El.=Elijah --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 8: What have I to do with thee" \
    --perf "Andante agitato, dotted crotchet = 66; Andante sostenuto, crotchet = 58; Andante con moto, dotted crotchet = 63; recitatives at crotchet = 66 and 72, as marked; the fermata doubled" \
    --out homes/cjimti/sequences/elijah/the_widows_son.score.json

# EL06 Before Ahab: No. 10, Elijah's oath (bars 2-5), the Allegro vivace and Ahab (14-26), the people's "Thou art
# Elijah" (27-31), Elijah's answer to "thy father's house" (32-35), and the challenge from "Rise then" to "put no
# fire" (63-65) spliced to "and the God who by fire shall answer" and the chorus (71-84); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/before_ahab.musicxml 2-6 14-35.5 63-66 71-85 --tempo \
    --part El.=Elijah --part Ah.=Ahab --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 10: As God the Lord of Sabaoth liveth" \
    --perf "Grave, crotchet = 60; Allegro vivace, crotchet = 144; recitatives at crotchet = 84, Maestoso at 80; a tempo, minim = 92, as marked" \
    --out homes/cjimti/sequences/elijah/before_ahab.score.json

# EL07 Baal, We Cry to Thee: No. 11, the Andante grave from the half-bar upbeat (bars 1.5-21.5 and 25.5-32), one
# repeat of "Heed the sacrifice" left out, then the "us!" and the Allegro non troppo's first bars (33-35); from the
# 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/baal_we_cry.musicxml 1.5-21.5 25.5-36 --tempo \
    --part "S. 1=S1" --part "S. 2=S2" --part "A. 1=A1" --part "A. 2=A2" --part "T. 1=T1" --part "T. 2=T2" \
    --part "B. 1=B1" --part "B. 2=B2" --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 11: Baal, we cry to thee" \
    --perf "Andante grave e maestoso, crotchet = 84; Allegro non troppo, crotchet = 160, as marked" \
    --out homes/cjimti/sequences/elijah/baal_we_cry.score.json

# EL08 Call Him Louder: the close of No. 11 (bars 117-141) and all of No. 12, numbered on from it: the recitative
# from its upbeat (142.75-152) and the chorus "Hear our cry, O Baal" (153-174); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/call_him_louder.musicxml 117-142 142.75-175 --tempo \
    --part El.=Elijah --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 11: Baal, we cry to thee (the close); No. 12: Call him louder; Hear our cry, O Baal" \
    --perf "Allegro non troppo, crotchet = 160; recitative at crotchet = 100; Allegro vivace, crotchet = 160, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/call_him_louder.score.json

# EL10 Lord God of Abraham: "Draw near, all ye people" closing No. 13 (bars 1-3), Elijah's first phrase of the aria
# No. 14 (its bars 7-12, here 10-15) and the outer phrases of the quartet No. 15 (its bars 1-5 and 13-17, here 42-46
# and 54-58); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/lord_god_of_abraham.musicxml 1.25-4 10-16 42.5-46.75 54.75-59 \
    --tempo --part El.=Elijah --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 13: Draw near, all ye people; No. 14: Lord God of Abraham; No. 15: Cast thy burden upon the Lord" \
    --perf "Recitative and Adagio, crotchet = 63; Più adagio, crotchet = 52, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/lord_god_of_abraham.score.json

# EL11 The Fire Descends: No. 16, the recitative (bars 1-6), the chorus's first six bars (7-12) and "Before Him" to
# the end of the chorale (32-60)
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_fire_descends.musicxml 1.6-13 32-61 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part El.=Elijah --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 16: O Thou, who makest Thine angels spirits; The fire descends from heav'n" \
    --perf "Recitative at crotchet = 69; Allegro con fuoco, crotchet = 152, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/the_fire_descends.score.json

# EL12 Is Not His Word Like a Fire?: No. 17, the opening (bars 1-26), "breaketh the rock into pieces?" (78-81), the Più
# lento and the close (82-90), and No. 18 to "against Him" (91-99); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/is_not_his_word.musicxml 1-27 78-99.75 --tempo \
    --part El.=Elijah --part Al.=Alto --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 17: Is not His word like a fire?; No. 18: Woe unto them" \
    --perf "Allegro con fuoco e marcato, minim = 92; Piu lento at minim = 72; Lento, quaver = 96, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/is_not_his_word.score.json

# EL13 A Little Cloud: No. 19, "Go up now, child" and the youth's first answer (bars 26-34), "Go up again" and the
# second (51-56), and "Behold, a little cloud" to "louder and louder" (72.875-81); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/a_little_cloud.musicxml 26-35 51-57 72.875-82 --tempo \
    --part El.=Elijah --part Yo.=Youth --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 19: O man of God (Go up now, child; Behold, a little cloud)" \
    --perf "Andante sostenuto, crotchet = 66; recitatives at crotchet = 80, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/a_little_cloud.score.json

# EL14 Thanks Be to God: No. 20, the opening to "they rush along!" (bars 1-24), "The stormy billows" to "and Almighty"
# (53-73) and the last page (129-140); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/thanks_be_to_god.musicxml 1-25 53.667-74 129-141 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 20: Thanks be to God" \
    --perf "Allegro moderato ma con fuoco, crotchet = 126, as marked; the last fermata doubled" \
    --out homes/cjimti/sequences/elijah/thanks_be_to_god.score.json

# EL15 Hear Ye, Israel: No. 21 to "hear what the Lord speaketh:" (bars 1-17) and the first twenty bars of No. 22
# (18-37), to the half close on "thy help is near"; from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/hear_ye_israel.musicxml 1-38 --tempo \
    --part Sop.=Soprano --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 21: Hear ye, Israel; No. 22: Be not afraid" \
    --perf "Adagio, quaver = 80; Allegro maestoso ma moderato, crotchet = 112, as marked; the fermata doubled" \
    --out homes/cjimti/sequences/elijah/hear_ye_israel.score.json

# EL16 The Queen: No. 23, the Queen's questions and the people's answers (bars 29-38), spliced at her "The" (44) to
# her oath and "He shall perish!" (45-55), and No. 24 bars 1-10 (56-65); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_queen.musicxml 29-38.75 44.875-65.25 --tempo \
    --part Qu.=Jezebel --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 23: Have ye not heard he hath prophesied; No. 24: Woe to him" \
    --perf "Andante and recitative at crotchet = 72; Allegro moderato, crotchet = 100, as marked" \
    --out homes/cjimti/sequences/elijah/the_queen.score.json

# EL17 It Is Enough: No. 25, Obadiah's recitative to "journey" (bars 1-11), and No. 26 bars 1-17 (12-28), to the
# second "it is enough,"; from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/it_is_enough.musicxml 1-11.875 12-29 --tempo \
    --part Ob.=Obadiah --part El.=Elijah --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 25: Man of God; No. 26: It is enough" \
    --perf "Recitative at crotchet = 76, Lento at 54; Adagio, crotchet = 66, as marked; the fermata doubled" \
    --out homes/cjimti/sequences/elijah/it_is_enough.score.json

# EL18 Lift Thine Eyes: No. 27 (bars 1-7), No. 28 to "the maker of heaven and earth" (its bars 1-16, numbered 9-24)
# and No. 29 to the tenors' "sleeps" (its bars 1-9, numbered 48-56); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/lift_thine_eyes.musicxml 1-7.5 9-25 48-56.5 --tempo --gap 1.5 \
    --part Ten.=Tenor --part "S. 1=S1" --part "S. 2=S2" --part "A. 1=A1" --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 27: See, now he sleepeth; No. 28: Lift thine eyes; No. 29: He, watching over Israel" \
    --perf "Recitative at crotchet = 66; Andante con moto, quaver = 100; Allegro moderato, crotchet = 126, as marked" \
    --out homes/cjimti/sequences/elijah/lift_thine_eyes.score.json

# EL19 O Rest in the Lord: No. 30, the Angel to "the mount of God" (bars 1-6), No. 31's first nine bars (34-42, to the
# second "desires") and No. 32's first eight (68-75); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/o_rest_in_the_lord.musicxml 1-6.75 34-42.5 68-76 --tempo --gap 1.0 \
    --part An.=Angel --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 30: Arise, Elijah; No. 31: O rest in the Lord; No. 32: He that shall endure to the end" \
    --perf "Recitative at crotchet = 72, Tempo Adagio at 56; Andantino, crotchet = 72; Andante sostenuto, crotchet = 66, as marked" \
    --out homes/cjimti/sequences/elijah/o_rest_in_the_lord.score.json

# EL20 The Lord Passed By: No. 34, every turn of the text (wind, earthquake, fire, the still small voice), the long
# repetitions left out
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_lord_passed_by.musicxml \
    1-16 30-36 45-48 64-72 74-78 110-135 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 34: Behold! God the Lord passed by" \
    --perf "Allegro molto, minim = 100, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/the_lord_passed_by.score.json

# EL21 Holy, Holy, Holy: No. 35, the recitative and both "Holy"s (bars 1-11, cut before the quartet's "the Lord
# Sabaoth") and "Now His glory hath filled all the earth" to the chorus's "Holy is God the Lord" (17-30); from the
# 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/holy_holy_holy.musicxml 1-11.75 17-31 --tempo --gap 1.0 \
    --part Al.=Alto --part "S. 1=S1" --part "S. 2=S2" --part "A. 1=A1" --part "A. 2=A2" \
    --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 35: Above Him stood the Seraphim; Holy, holy, holy is God the Lord" \
    --perf "Recitative at crotchet = 72; Adagio non troppo, crotchet = 72, as marked" \
    --out homes/cjimti/sequences/elijah/holy_holy_holy.score.json

# EL22 The Fiery Chariot: No. 38, the opening to "fire;", "And when the Lord would take him away" and the second
# "there came a fiery chariot" to the end
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_fiery_chariot.musicxml 1-5.5 32-35 39.75-59 \
    --tempo --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 38: Then did Elijah" \
    --perf "Moderato maestoso, crotchet = 76, as marked; the closing ritard taken and the fermata doubled" \
    --out homes/cjimti/sequences/elijah/the_fiery_chariot.score.json

# EL23 Your Light Break Forth: No. 39 bars 1-6 (1-6 here), No. 40 bars 1-8 to "the day of the Lord." (7-14), No. 42
# bars 1-5 (15-19) and its last 18 bars, "Thou fillest heav'n with glory" and the Amen (20-37); from the 1870 printing
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/your_light_break_forth.musicxml 1-14.5 15-38 --tempo \
    --part Ten.=Tenor --part Sop.=Soprano --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1870), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 39: Then shall the righteous shine forth; No. 40: Behold, God hath sent Elijah; No. 42: And then shall your light break forth" \
    --perf "Andante, crotchet = 80; recitative, Andante sostenuto, crotchet = 69; Andante maestoso, crotchet = 96; Allegro, minim = 96, as marked; the last fermata doubled" \
    --out homes/cjimti/sequences/elijah/your_light_break_forth.score.json
```

When a scene's numbers come one after another, they share one MusicXML, numbered straight through (each file's
first lines say which bars are which number). The voices are read note for note. Where the piano reduction's inner
voices were hard to read in the scan (EL09's section E, parts of EL20's and EL22's accompaniment, the rushing chords
of EL02's first bars, the bass under EL01's fugal answer, parts of EL03's accompaniment, and the accompaniments of
EL04 to EL08, EL10, EL12 to EL19 and EL21, whose tremolos and repeated figures are written as chords or repeated
chords), the harmony, rhythm and register are kept and the voicing is approximate; where the reduction doubles the
chorus (EL07's Andante, EL11's chorale, parts of EL14, EL16, the close of EL23) the accompaniment doubles the voices. The Internet Archive
also has the 1870 printing of the same plates (`elijahoratorioin00mend`), which is clean where the 1881 copy's
pages are covered (No. 16's first pages) and has the pages the 1881 copy lacks (Nos. 6 to 10, and every number from No. 11 on, are read from it).

There is no choir in the sample library, so sung lines are played on instruments, as in the Ring.

Every scene has a spoken intro (`VOICEOVER`, read by `pixelhome intro` in the owner's voice, `halloween-accent` as
for the Ring) over the Elijah bed in `pixelhome/intro.py`: a low D drone of double basses and bassoons with a little
dry wind, the curse's first chord on trombones before the first word and the rest of its chords after the last.

## The stage

From the street the porch is the back of the scene.

| place on the house | what it is |
|--------------------|------------|
| **Porch Front** | heaven, the far sky. Light that acts from here is the only way God appears. |
| **Right** | Elijah's altar on Mount Carmel, and Elijah's place in Part One. |
| **Left** | the altar of Baal and his priests. |
| **Porch Left / Porch Right** | the people of Israel, watching from both sides. |
| **Free end of Right** (path 500) | the sea. The little cloud rises here. |
| **Side** | the wilderness in Part Two: Beersheba, the juniper tree, Horeb. |

Subjects never begin on Side, a dim themed bed keeps every run lit, and the last frame of each scene sets up the
first of the next. God is never a figure: only what light does (fire that falls, rain that comes, a wind, and at
Horeb a single faint point).

## Who is who

| character | colour | voice (sung lines played on) |
|-----------|--------|------------------------------|
| Elijah (bass-baritone) | white-hot amber `#ffb040`, core `#fff4d0` | cellos and horns; the curse on low brass |
| Obadiah (tenor) | teal `#20b0a0` | violas, clarinet |
| the Angel(s) (soprano, alto) | silver-white `#d8ecff` | flutes, oboe |
| the Widow (soprano) | rose `#e07a8a` | oboe |
| her son | one small warm point `#ffd8a0` | harp, when he lives again |
| the Youth (treble) | pale sky `#9cd8ff` | flute |
| the voice from heaven (soprano, Nos. 21 and 40) | silver-white `#d8ecff` on Porch Front | flutes, oboe |
| the righteous (tenor, No. 39) | sun-warm gold `#ffd890` | horns, violas |
| Ahab (tenor) | iron grey `#8a8f98` | bassoons |
| Jezebel (alto) | wine `#a01860` | low clarinet, trombones under her crowd |
| priests of Baal (chorus) | burnished bronze `#b06a10`, brassy glints `#ffcc55` | brass, timpani |
| the people of Israel (chorus) | warm candle `#ffcf8a`, many small lights | strings with winds doubling |
| drought | dust ochre bed `#3a2008` | |
| rain | blue `#2060ff`, spray `#80c8ff` | |
| fire from heaven | white `#ffffff` to gold `#ffc040` to red `#ff3000` | |

## The scenes

| code | title | numbers | status |
|------|-------|---------|--------|
| EL01 | The Curse | Introduction, Overture | built: the curse on Right, every chord burning the amber further; the fugue draining the house to dust |
| EL02 | Help, Lord! | 1, 2 | built: the people's cries flaring up the porch, the harvest falling in gold, the prayer climbing to a dark sky |
| EL03 | Rend Your Hearts | 3, 4, 5 | built: Obadiah's teal walking among the people; red pulses from heaven that never reach them |
| EL04 | The Angels' Charge | 6, 7 | built: the Angel on Porch Front; eight silver points, the double quartet, walking with Elijah from Right to the front corner |
| EL05 | The Widow's Son | 8 | built: the widow's rose and her son's warm point on Left; Elijah's amber reaching farther at each prayer, and the point lit again |
| EL06 | Before Ahab | 10 | built: Ahab's iron grey against Elijah's amber; the people turned grey and back; Baal's bronze altar on Left and the unlit wood on Right |
| EL07 | Baal, We Cry to Thee | 11 | built: the double chorus around Baal's bronze altar on Left, each choir flaring its half of the run, glints flung toward a dark heaven |
| EL08 | Call Him Louder | 11 (end), 12 | built: the priests tiring, Elijah's taunts as amber flicks from Right, and their louder cry entering voice by voice along Left |
| EL09 | Hear and Answer | 13 | built: the whole chorus, 77 bars, with Mendelssohn's silences frozen on the house |
| EL10 | Lord God of Abraham | 13 (end), 14, 15 | built: the people drawn near, Elijah's prayer as slow amber breathing, and warmth spreading over the house on "Cast thy burden" |
| EL11 | The Fire Descends | 16 | built: the recitative, the fire falling down Porch Right onto the altar, the people bowing, and the chorale |
| EL12 | Is Not His Word Like a Fire? | 17, 18 | built: amber hammer strokes from Right; a bolt on every "hammer" cracking Baal's bronze until it shatters and Left goes cold; a silver voice mourning on Porch Front |
| EL13 | A Little Cloud | 19 | built: the youth's looks sweeping to the free end of Right and coming back empty, brass and iron, the silences held; the cloud like a man's hand rising, and the storm rolling in |
| EL14 | Thanks Be to God | 20 | built: the rain falling from Porch Front down every run, the drought washed away, the candles warm again; wave trains and billows, stilled under "the Lord is above them"; the end of Part One |
| EL15 | Hear Ye, Israel | 21, 22 | built: the soprano's silver calling down the porch runs; "Be not afraid" filling the house with warm light from the porch outward |
| EL16 | The Queen | 23, 24 | built: Jezebel's wine seeping from Left through the people; "Woe to him" closing in on Elijah's amber along Right |
| EL17 | It Is Enough | 25, 26 | built: Obadiah's teal warning; Elijah's walk round the house to the free end of Side, his amber sinking there |
| EL18 | Lift Thine Eyes | 27, 28, 29 | built: Elijah asleep at the free end of Side; angels camping round the house, three crossing to him, and a wave that never stops along the whole roofline |
| EL19 | O Rest in the Lord | 30, 31, 32 | built: the Angel waking him and leading him up Side; a still rose-gold hold; the people's candles round him, then night on Horeb |
| EL20 | The Lord Passed By | 34 | built: wind, earthquake and fire, then the still small voice as one silver point on Porch Front |
| EL21 | Holy, Holy, Holy | 35 | built: four silver layers across heaven, the whole house swelling with the chorus, glory filling every run, and the light gathering into Elijah on Right |
| EL22 | The Fiery Chariot | 38 | built: the chariot of fire racing the roofline from Right and leaving at the free end of Side |
| EL23 | Your Light Break Forth | 39, 40, 42 | built: the righteous shining out from heaven; Elijah sent back down to his place, the dreadful day passing red; morning light breaking out of Porch Front and filling the house outward to the Amen, over the rising bass |
| EL24 | Intermission | | built: five minutes on `countdown()`, drought ochre filling with rain blue, to the quiet numbers (Nos. 28, 14, 15, 31, 32, 39, 29) played softly and the curse chords calling the street back |

The plan of the 23 scenes is in #41.
