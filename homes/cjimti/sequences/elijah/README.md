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
Co., London, 1881) and timed by its tempo markings. There is no choir in the sample library, so the sung lines are
played on orchestral instruments; every character has a colour and an instrument, and the lights follow the notes.
God never appears as a figure, only in what light does: fire that falls, rain that comes, a single faint point at
Horeb.

So far four scenes are built: No. 13, the priests of Baal calling on their god (*Baal, hear and answer*), with
Mendelssohn's silences frozen on the house; No. 16, Elijah calling down the fire and the people falling on their
faces (*The fire descends*); No. 34, the wind, the earthquake and the fire on Horeb, and the still small voice after
them (*Behold! God the Lord passed by*); and No. 38, the chariot of fire (*Then did Elijah*). It is the start of an
oratorio season on the house, with Handel's *Judas Maccabaeus* and *Messiah* to follow.

## Where the music comes from

There is no dataset like the Ring's for *Elijah*, so each number is transcribed by hand from a public-domain score,
the Novello, Ewer and Co. octavo vocal score (London, 1881; Internet Archive `31761122531270`), into MusicXML beside
its scene (`<name>.musicxml`, sopranos, altos, tenors and basses as their own parts, the accompaniment as a
two-staff piano part). `scripts/score_excerpt.py` cuts the bars a scene uses into `<name>.score.json`, the same
shape the Ring scenes load with `pixelhome.ring.excerpt()`, each note labelled with its part (`S`, `A`, `T`, `B`,
`Orch`).

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
# EL11 The Fire Descends: No. 16, the recitative (bars 1-6), the chorus's first six bars (7-12) and "Before Him" to
# the end of the chorale (32-60)
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_fire_descends.musicxml 1.6-13 32-61 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part El.=Elijah --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 16: O Thou, who makest Thine angels spirits; The fire descends from heav'n" \
    --perf "Recitative at crotchet = 69; Allegro con fuoco, crotchet = 152, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/the_fire_descends.score.json

# EL20 The Lord Passed By: No. 34, every turn of the text (wind, earthquake, fire, the still small voice), the long
# repetitions left out
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_lord_passed_by.musicxml \
    1-16 30-36 45-48 64-72 74-78 110-135 --tempo \
    --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 34: Behold! God the Lord passed by" \
    --perf "Allegro molto, minim = 100, as marked; fermatas doubled" \
    --out homes/cjimti/sequences/elijah/the_lord_passed_by.score.json

# EL22 The Fiery Chariot: No. 38, the opening to "fire;", "And when the Lord would take him away" and the second
# "there came a fiery chariot" to the end
uv run python scripts/score_excerpt.py homes/cjimti/sequences/elijah/the_fiery_chariot.musicxml 1-5.5 32-35 39.75-59 \
    --tempo --part S.=S --part A.=A --part T.=T --part B.=B --part Pno.=Orch \
    --source "Novello, Ewer and Co. octavo vocal score (London, 1881), transcribed; public domain" \
    --act "Elijah, Op. 70, No. 38: Then did Elijah" \
    --perf "Moderato maestoso, crotchet = 76, as marked; the closing ritard taken and the fermata doubled" \
    --out homes/cjimti/sequences/elijah/the_fiery_chariot.score.json
```

The voices are read note for note. Where the piano reduction's inner voices were hard to read in the scan (EL09's
section E, parts of EL20's and EL22's accompaniment), the harmony, rhythm and register are kept and the voicing is
approximate; in EL11's chorale the accompaniment doubles the voices, as the reduction does. The Internet Archive
also has the 1870 printing of the same plates (`elijahoratorioin00mend`), which is clean where the 1881 copy's
pages are covered (No. 16's first pages).

There is no choir in the sample library, so sung lines are played on instruments, as in the Ring.

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
| EL09 | Hear and Answer | 13 | built: the whole chorus, 77 bars, with Mendelssohn's silences frozen on the house |
| EL11 | The Fire Descends | 16 | built: the recitative, the fire falling down Porch Right onto the altar, the people bowing, and the chorale |
| EL20 | The Lord Passed By | 34 | built: wind, earthquake and fire, then the still small voice as one silver point on Porch Front |
| EL22 | The Fiery Chariot | 38 | built: the chariot of fire racing the roofline from Right and leaving at the free end of Side |

The full plan of 23 scenes is in #41.
