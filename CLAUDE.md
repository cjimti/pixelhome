# Pixelhome: notes for agents

Sequences are Python modules that render frames. The site (pixelhome.app) is built from them in CI;
never commit `dist/`, `build/`, FSEQ or PNG output. The generated things that are committed are a show's
soundtrack, `homes/<home>/audio/<occasion>/<name>.mp3`, and its spoken intro, `homes/<home>/intros/...`:
they need local tools CI doesn't have.

## Sequence contract

- File: `homes/<home>/sequences/<occasion>/<name>.py`. The folder is the occasion and must be an id
  in `pixelhome/occasions.py`. The id on the site is `<occasion>/<name>` with `_` changed to `-`.
- Module constants: `CODE` (unique per home: the occasion's `prefix` from `occasions.py` plus two
  digits, e.g. `XM01`..`XM10`; Halloween's originals are `SC1`.. and `NT1`..), `TITLE`,
  `KIND` (`'show'` or `'ambient'`), `DESCRIPTION` (one or two sentences for the card).
- `render(G, seed=N) -> ndarray (F, G.N, 3)`, float PWM 0..1, node (channel) order.
- Length: shows 40-90 s, ambient loops 120-180 s (`looped()`). Every frame ships to the site and
  to FPP, so length is size. Render time should stay under ~15 s; vectorize over pixels with numpy.
- Module docstring: `"""Title: what happens, for someone reading the code."""`
- Files starting with `_` are ignored by discovery. A sequence imports only from `pixelhome` and
  the standard library/numpy; keep each one self-contained.

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
- `show` pieces may be bright and fast, but avoid full-house strobing longer than a moment.
- Pieces are specific to a home's segment names. Read `homes/<home>/README.md` (shape, corners,
  path indices, spacing, what reads from the street) before designing for a home.

## Music (optional)

A show or an ambient loop may define `score(M, G)` that writes its soundtrack into the mix `M` (`pixelhome/audio.py`): Surge XT
patches, VSCO2 CE samples, slide whistles, whooshes. Take every hit from the same timings render() uses,
pan sounds to where they happen on the house, and compose something original (no existing songs).
`homes/cjimti/sequences/halloween/bone_yard.py` is the reference. One-time setup: `scripts/audio-setup.sh`.
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
and `.json` (the voice's loudness at 40 fps). Both are committed; the build turns the JSON into a red
out-from-centre waveform FSEQ on Left, Porch Front and Right. Takes are cached by text and voice, so a reading
only changes when its line does; `VOICEOVER_TAKE = n` asks for a different reading of the same line.
(`INTRO` is taken: Seance's score uses it for a tune.)

## Checking work

```sh
uv run python -m pixelhome preview --occasion <occasion> --out build/preview/<occasion> <CODE>
uv run python -m pixelhome list
make verify                                     # full build, required before committing
```

`preview` validates the render and writes two images to look at with an image viewer:
`... timeline.png` (time down at 10 rows/s, the roofline path left to right: Side, Left, Porch
Left, Porch Front, Porch Right, Right) and `... stills.png` (12 moments of the house from above,
street at the bottom). It prints peak, mean, how much of the house is lit, the largest frame-to-
frame jumps, and the loop seam (should be ~0 for ambient loops). `--video` adds an MP4. Plain
`build` wipes `dist/`; don't run it while others are working in the same checkout.
