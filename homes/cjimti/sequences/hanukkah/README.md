# Hanukkah on the roofline

Eight candle-lighting shows, one for each night of Hanukkah (`HN01`..`HN08`), about a minute each. On night *n* the
hanukkiah on the porch is kindled with *n* lights and the shamash, to the hymn sung after the lights, *Ma'oz Tzur*.
Each night's show opens that night's program, before Handel's *Judas Maccabaeus*
(`homes/cjimti/sequences/judas-maccabaeus/`). Tickets: #69 under the epic #43.

## About the work

Hanukkah remembers the rededication of the Temple in Jerusalem in 164 BCE, after the revolt of the Maccabees against
the Seleucid king Antiochus IV. 1 Maccabees tells of eight days of dedication; the Talmud (Shabbat 21b) tells of a
single cruse of pure oil that burned for eight days, and so for eight nights a light is added to the hanukkiah, one
more each night, until all eight burn.

The lights are kindled by a ninth, the shamash, the helper, set apart from the others. The custom followed here: the
lights are added from right to left, and lit left to right, the newest first. Facing the house from the street, the
first night's light is the rightmost.

After the lights are kindled, *Ma'oz Tzur* is sung, "Rock of Ages": a hymn from the thirteenth century, signed in its
acrostic by a poet named Mordecai, to a melody German Jews have sung for it since at least the eighteenth century.

The blessings said over kindling a hanukkiah are not spoken in these shows: they belong to lighting real lights, and
said over a recording they would be said in vain.

## Where the music comes from

The melody is *Ma'oz Tzur*'s traditional one, as the Union Hymnal (Central Conference of American Rabbis, 1897) prints
it with Gustav Gottheil's English, No. 107, "Rock of Ages (Chanuccah)", read from the copy on the Internet Archive
(`unionhymnal0000unse_l7i5`) and checked note by note against the tune as it is sung today. One verse, at the hymnal's
Maestoso, plays on an oboe from the middle of the porch, where the lights are. The strings' plain harmony under it is
our own; a harp sounds each light as it catches.

## The stage

| place on the house | what it is |
|--------------------|------------|
| **Porch Front** | the hanukkiah: nine places, eight lights in two groups of four, the shamash in the middle with a wider gap on each side. |
| **Porch Left / Porch Right** | warm a little with each light. |
| **Left, Right and Side** | low blue while the lights are kindled; when they are all lit, a warm glow spreads out along them from the porch. |

## Who is who

| light | colour |
|-------|--------|
| the flames | olive-oil gold `#ffb33a`, tips `#fff1c0` |
| the shamash | the same, a little whiter, brighter and wider |
| the night before the lights | low blue `#0c2a8a` |
| the lights' glow over the house | olive-oil gold |

## How the shows are built

Every night is the same show with its own number of lights: `pixelhome/hanukkah.py`'s `Night(n, __file__)` does the
work, and each `the_<n>th_night.py` names its night. Over about 67 seconds:

- 0-6 s: the house dims from a warm evening to low blue; at 3.4 s the shamash is struck (a white flash) and its flame
  grows, a harp spread under it.
- From 6 s, *Ma'oz Tzur*, eight phrases of four bars: on each of the first *n* phrases the shamash's flame is carried
  along Porch Front to the next light, which catches on the phrase's downbeat, a harp note sounding from its place.
  The porch runs warm as the night's lights come.
- After the last light, the glow spreads from the porch out to the free ends of the house until the hymn ends; on
  the first night it takes most of the hymn, on the eighth the last phrase.
- The last 5.5 s: the lights settle and stay, the last chord held, a harp spread.

`Hanukkiah` and `places()` are the porch's nine places and their flames; `Glow` is the generic glow the Judas scenes
carry on Porch Front. The scenes are rendered ahead of time and play on all eight nights, so they can't show the
night's own lights: only the candle-lighting show does.

The melody's transcription and cut:

```sh
uv run python scripts/shorthand.py <notes file> homes/cjimti/sequences/hanukkah/maoz_tzur.musicxml
uv run python scripts/score_excerpt.py homes/cjimti/sequences/hanukkah/maoz_tzur.musicxml 1-33 --tempo \
    --part P1=Melody --source "Union Hymnal No. 107 (CCAR, 1897), transcribed" --act "Ma'oz Tzur" \
    --out homes/cjimti/sequences/hanukkah/maoz_tzur.score.json
```

Each night has a spoken intro, one line (`VOICEOVER`), for example "The third night of Hanukkah. Three lights, and the
one that lights them.", over the Hanukkah bed in `pixelhome/intro.py`: Ma'oz Tzur's first notes on an oboe before the
words, F major strings under them, and a harp spread and the end of the hymn's first phrase after.

Still to come: a schedule that opens night *n* with show *n* (#43).
