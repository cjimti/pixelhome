# Pixelhome: notes for agents

Sequences are Python modules that render frames. The site (pixelhome.app) is built from them in CI;
never commit `dist/`, `build/`, FSEQ or PNG output.

## Sequence contract

- File: `homes/<home>/sequences/<occasion>/<name>.py`. The folder is the occasion and must be an id
  in `pixelhome/occasions.py`. The id on the site is the file name with `_` changed to `-`.
- Module constants: `CODE` (unique per home, e.g. `HW6`, `XM1`, `NY1`, `FN1`), `TITLE`,
  `KIND` (`'show'` or `'ambient'`), `DESCRIPTION` (one or two sentences for the card).
- `render(G, seed=N) -> ndarray (F, G.N, 3)`, float PWM 0..1, node (channel) order. 1 s to 15 min.
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
- Pieces are specific to a home's segment names. Check `homes/<home>/home.json` before using one.

## Checking work

```sh
uv run python -m pixelhome list
uv run python -m pixelhome build <match>        # validates shape, NaN, duration
uv run python -m pixelhome preview <match>      # prints peak / max step; writes MP4 + timeline PNG
```

Look at the timeline PNG (time down, path along) to judge a piece without playing it.
