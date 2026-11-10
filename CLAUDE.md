# Pixelhome: notes for agents

Sequences are Python modules that render frames. The site (pixelhome.app) is built from them in CI;
never commit `dist/`, `build/`, FSEQ or PNG output. The generated things that are committed are a show's
soundtrack, `homes/<home>/audio/<occasion>/<name>.mp3`, and its spoken intro, `homes/<home>/intros/...`:
they need local tools CI doesn't have.

## Sequence contract

- File: `homes/<home>/sequences/<playlist>/<name>.py`. The folder is the playlist: an occasion's id (its own
  playlist) or one of `PLAYLISTS` in `pixelhome/occasions.py`, which puts it under an occasion (Nightmare
  under Halloween, each Ring opera under the Ring Cycle). The id on the site is
  `<playlist>/<name>` with `_` changed to `-`; moving a playlist to another occasion changes no ids or paths.
- Module constants: `CODE` (unique per home: the playlist's `prefix` from `occasions.py` plus two
  digits, e.g. `CH01`..`CH10`; Halloween's originals are `SC1`.. and `NT1`..), `TITLE`,
  `KIND` (`'show'`, `'ambient'` or `'intermission'`), `DESCRIPTION` (one or two sentences for the card).
- `render(G, seed=N) -> ndarray (F, G.N, 3)`, float PWM 0..1, node (channel) order.
- Length: shows 40-90 s, ambient loops 120-180 s (`looped()`), intermissions 300 s. Every frame ships to the site and
  to FPP, so length is size. Render time should stay under ~15 s; vectorize over pixels with numpy.
- Module docstring: `"""Title: what happens, for someone reading the code."""`
- Files starting with `_` are ignored by discovery. A sequence imports only from `pixelhome` and
  the standard library/numpy; keep each one self-contained.
- The build caches each render by the files it depends on (`deps()` in `pixelhome/rendering.py`): its module,
  the files beside it that share its name or that it names, and the `pixelhome` modules it imports at module level.
  Imports inside a function aren't followed, so import what render() needs at the top.

## The Home (`G`, see `pixelhome/home.py`)

- `G.N` pixels; `G.pos` (N,3) positions in layout units (x across the front, y up, +z toward the
  street; the default camera looks from +z).
- `G.seg[name]` node indices of a segment, in channel order.
- `G.path` node indices in physical order along the roofline; `G.pi` path index by node;
  `G.pd` distance along the path by node; `G.length` path length.
- `G.path_segments()` [(name, path indices)] in path order. `G.span_u(idx)` -1..1 across x.
- Writing in path order: `out[f][G.path] = buf` where `buf` is (N,3) in path order.

## Effects (`pixelhome/fx.py`)

`DT` (1/40 s), `nframes(seconds)`, `hexc('#rrggbb')`, `perc(i)`, `light(color, intensity)`,
`smoothstep`, `keys(t, [(t, v), ...])` eased keyframes, `lerp`, `heartbeat`, `smooth_noise`,
`Flicker`, `colormap`, `catmull_closed`, `looped(draw, seconds, floor=(level, color))` for seamless
loops, `candle_bed`.

## Rules that matter

- Intensities are perceptual; colours/frames are PWM. `light()` converts. Don't apply gamma twice.
- Determinism: all randomness from `np.random.default_rng(seed)`. The build must be reproducible.
- `ambient` pieces play all night: peaks around 0.4 perceptual, never fully dark, nothing fast or
  strobing. They are dithered on output. Use `looped()` so the end flows into the start.
- Power: `pixelhome/power.py` cuts every all-night loop to under half of what it renders (porch kept, wings and
  Side thinned to sparse light and drifting pools), so compose them as usual. The daytime loop isn't touched by it:
  Daylight is sparkles composed to a quarter of the draw of the lit roofline it replaced.
- `show` pieces may be bright and fast, but avoid full-house strobing longer than a moment.
- Pieces are specific to a home's segment names. Read `homes/<home>/README.md` (shape, corners,
  path indices, spacing, what reads from the street) before designing for a home.

## Intermissions and show times

A playlist's `intermission.py` (`KIND = 'intermission'`) plays for five minutes before each of its sets in a night's
rotation. It is built on `pixelhome/intermission.py`'s `countdown()`: the house stays lit while a fill closes in on
the porch, so the street can see how long is left; its score marks each minute and calls the street back at the
finale (`MARKS`), at about -19 dBFS.
`homes/<home>/schedule.py` says which sets play which nights at clock times (a set can have an `opener`, one show
straight before it: Hanukkah's candle-lighting for the night) (and which loops keep the house lit
by day and late at night: it is never dark). The build works it out against the
catalog into `data/<home>/schedule.json` (the Live page's show times), and `scripts/fpp_sync.py --apply` writes
the same nights into FPP (a playlist per kind of night and the whole schedule), uploads what changed and removes
what the site doesn't have. Change the schedule, `make verify`, then sync.

## Music (optional)

A show or an ambient loop may define `score(M, G)` that writes its soundtrack into the mix `M` (`pixelhome/audio.py`): Surge XT
patches, VSCO2 CE samples, slide whistles, whooshes. Take every hit from the same timings render() uses,
pan sounds to where they happen on the house. A piece we invent gets original music (no existing songs); a piece
that recreates a real work (the Ring operas) plays that work's actual music (never invented substitutes).
The Ring scenes take their notes from the Wagner Ring Dataset: `scripts/ring_excerpt.py` cuts bars of an act, timed
like a recording, into `<name>.score.json` beside the sequence (committed), and `pixelhome/ring.py` loads it and
orchestrates it (`Orchestra`). Pick the most dynamic passages that tell each scene's story; it's an entertaining
interpretation, not a purist one. Augment the score as a staged production would: every event the lights show gets
a sound (thunder with lightning, hoofbeats, clashes, fire; `Orchestra.thunder`, `gallop`, `clash`, `fire`...), and
sung melodies that matter can come from a public-domain vocal score, played on an instrument.
The oratorios (Elijah, then Judas Maccabaeus and Messiah) have no dataset: their notes are transcribed by hand from
public-domain vocal scores with `scripts/noteheads.py` and `scripts/staff_lines.py` (pitches off 500 dpi scans; `uv
run --group score`), `scripts/shorthand.py` (a notes file to MusicXML, every bar checked) and `scripts/clash.py`
(misreads), then cut with `scripts/score_excerpt.py --tempo`; `homes/cjimti/sequences/elijah/README.md` has the
method and every scene's cut.
`homes/cjimti/sequences/halloween/bone_yard.py` is the reference. One-time setup: `scripts/audio-setup.sh`.
For now the build leaves a sequence off the site until its MP3 exists (the module stays; `preview`, `list` and
`music` still see it).
Shows play outdoors to the street, so keep melodies in the middle register. Most VSCO2 sets are labelled an
octave low (`tune=-12` plays them as written), and the engine lowers parts that sit high and folds any note
above E6 (C7 for bells and mallets); `music` prints what it lowered.
Ambient pieces render as seamless loops (whatever rings past the end wraps onto the start, no fades) and play
all night, also over an FM transmitter: keep them soft (rms around -22 dBFS), with no beat and nothing startling.
Render: `uv run --group audio python -m pixelhome music [--video] <CODE>` (writes the MP3, and with
`--video` a preview MP4 with sound). If a show's timing changes, re-render its music. Never auto-play
audio on the machine you are working on.

## Spoken intros (optional)

A sequence may set `VOICEOVER = "..."`: one or two spoken sentences (about 4-8 s) to play before it, written
to be heard, not the card's DESCRIPTION. `uv run --group audio python -m pixelhome intro <CODE>` reads it with
Chatterbox in the owner's cloned voice (`~/.cache/pixelhome/voice/<occasion>.wav`, never committed), puts it
over the occasion's bed (`BEDS` in `pixelhome/intro.py`) and writes `homes/<home>/intros/<occasion>/<name>.mp3`
and `.json` (the voice's loudness at 40 fps). Both are committed; the build turns the JSON into the
intro's FSEQ, in the occasion's accent (Halloween in red): the show's title as a Morse marquee on Left, each spoken word
in 8-bit ASCII on Porch Front, and a waveform out from the centre of Right. Takes are cached by text and voice, so a reading
only changes when its line does; `VOICEOVER_TAKE = n` asks for a different reading of the same line.
(`INTRO` is taken: Is Anyone There?'s score uses it for a tune.)

## Site pages

`pixelhome/pages.py` writes every page as static HTML at build time: `/` (the schedule: tonight's program and the
coming nights, from `data/<home>/schedule.json`), `/library/`, `/sets/`, `/<playlist>/` for each set and occasion, `/<playlist>/<name>/` for each sequence,
and `404.html`. Paths in pages are root-absolute (`/style.css`, `/data/...`). `site/app.js` is the player on top:
it plays a page's `.list .item[data-id]` rows, and on the library builds the list and filters itself. A set page's
text is its README's `## About the work`, `## The stage` and `## Who is who` sections (`README_SECTIONS`), written
for visitors; the rest of a README is for the repo. `SETS` in `occasions.py` lists the sets featured on `/sets/`.
Show times are in the HTML (the home page, and a set page's "When it plays"); `site/schedule.js` works out "now" in
the browser (hides what is over, says Tonight, points to Live while a show is on), since the build only runs on a
release. Every set and sequence page has its own 1200x630 share card (`cards/`, `share.label()`), set in the site's
fonts from `pixelhome/fonts/` (OFL).
Every page has the same header (`top()` in `pages.py`, styled by `site/header.css`); the static About and Live pages
carry `<!--sitehead-->` where the build puts it.

## Live mode

`live/` is the Cloudflare Worker and Pi service behind the site's Live button (see `live/README.md`). It must
stay within the Workers Free plan: no paid-only features, nothing that sends viewers' messages inbound.

## Tickets and PRs

Every session starts from this process, not only from the last handoff.

- Tickets exist before work starts. A branch gathers every open, unblocked ticket that fits one reviewable PR (about
  one set of scenes, roughly 20 minutes of new audio, per review). Work that has no ticket gets one first, under its
  epic. A handoff's numbered list is the order of work, not the PR's scope.
- Every PR closes all of its tickets, one `Closes #n` line each. A ticket too big for one PR becomes an epic with
  sub-issues.
- Branch from a freshly fetched `origin/main` with `--no-track` (`git fetch && git switch -c <name> --no-track
  origin/main`); a branch that tracks `main` breaks the owner's push.
- Committing, pushing and opening the PR each wait for the owner's word, and the owner pushes. Approval for one
  step is not approval for the next.
- At the end of a session, post a handoff comment on the epic: the state, and what comes next. Its steps are for the
  next session; don't start them, not even the branch, unless the owner asks.

## Branches, PRs and releases

Work goes on a branch and lands on `main` through a PR; CI (`.github/workflows/pages.yml`) builds every PR and every
push to `main`, but only a tag deploys: merged work goes live when it is released. A release is a tag on `main`,
`vMAJOR.MINOR.PATCH` (a new set or occasion is a minor, fixes are a patch): `git tag v1.2.0 origin/main && git push
origin v1.2.0`. `release.yml` publishes a GitHub release with notes generated from the PRs merged since the last
tag (sections in `.github/release.yml`, by label), and Pages deploys the tag. Tag a commit that hasn't been
released before: Pages ignores a second deploy of the same commit. The site's footers show the version the build
came from (`version()` in `pixelhome/build.py`, from `git describe`).

## Checking work

```sh
uv run python -m pixelhome preview --occasion <occasion> --out build/preview/<occasion> <CODE>
uv run python -m pixelhome list
make verify                                     # full build, required before committing
make serve-only                                 # serve the last build without building
```

`preview` validates the render and writes two images to look at with an image viewer:
`... timeline.png` (time down at 10 rows/s, the roofline path left to right: Side, Left, Porch
Left, Porch Front, Porch Right, Right) and `... stills.png` (12 moments of the house from above,
street at the bottom). It prints peak, mean, how much of the house is lit, the largest frame-to-
frame jumps, and the loop seam (should be ~0 for ambient loops). `--video` adds an MP4. Plain
`build` wipes `dist/`; don't run it while others are working in the same checkout.
