# Pixelhome

Pixel light sequences for a home's roofline, written as Python scripts, played by
[FPP](https://github.com/FalconChristmas/fpp), previewed in 3D at **[pixelhome.app](https://pixelhome.app)**.

Each sequence computes every pixel, frame by frame, from the home's real 3D layout. There is no
sequencing editor: sequences are code, written by hand or by agents. Halloween is first; Christmas,
New Year's and the other holidays follow; everything else goes in `other`.

## Layout

```
homes/<home>/home.json           the home model: segments, channels, physical path, controller
homes/<home>/house.obj           house mesh for the 3D preview, in layout coordinates
homes/<home>/source/             source files the model came from (Blender, etc.)
homes/<home>/sequences/<occasion>/<sequence>.py
pixelhome/                       library: effects (fx), home model, FSEQ writer, build, xLights importer
site/                            the static player (HTML, CSS, JS; no build step)
```

Occasion folders are listed in `pixelhome/occasions.py` (`halloween`, `christmas`, `new-years`,
`valentines`, `st-patricks`, `easter`, `independence-day`, `thanksgiving`, `other`).

## Commands

Requires [uv](https://docs.astral.sh/uv/). `ffmpeg` only for `preview`.

```sh
uv sync
uv run python -m pixelhome list                 # homes and sequences
uv run python -m pixelhome build                # render everything into dist/
uv run python -m pixelhome build wildfire       # just the matching sequences
uv run python -m pixelhome preview wildfire     # MP4 + timeline PNG in build/preview/
python3 -m http.server -d dist 8000             # view the site at localhost:8000
```

## Writing a sequence

Add `homes/<home>/sequences/<occasion>/<name>.py`:

```python
"""Title: what it looks like, in a sentence or two."""
import numpy as np
from pixelhome.fx import DT, hexc, light, nframes

CODE = 'XM1'                 # unique within the home, shown on the card
TITLE = 'Candy Cane'
KIND = 'show'                # 'show' or 'ambient' (all-night loop: dim, slow, dithered)
DESCRIPTION = 'Red and white stripes march around the roof.'


def render(G, seed=1):
    """G is the Home. Return float frames (F, G.N, 3): PWM values 0..1 per pixel, channel order."""
    out = np.zeros((nframes(30.0), G.N, 3))
    ...
    return out
```

Colours are PWM values (what the pixel is driven at); use `light(color, intensity)` to go from
perceptual intensity to PWM. Frames run at 40 fps (`DT = 0.025`). Use the seeded `rng` for all
randomness so builds are reproducible. See `CLAUDE.md` for the full set of conventions.

## Output

The build writes, per sequence:

- `fseq/<home>/<id>.fseq`: FSEQ v2, zstd-compressed, 40 fps, for FPP. Upload to FPP's sequence
  folder. The files are rendered for the brightness and gamma in `home.json` `controller`
  (80% and gamma 1.0 for `cjimti`): set the FPP output to match, or the sequence will look wrong.
- `data/<home>/<id>.png`: the same frames losslessly packed for the web player (one row per frame,
  one image pixel per LED). Sequences longer than two minutes are halved to 20 fps here.

Nothing generated is committed. GitHub Actions renders everything on each push to `main` and
deploys to GitHub Pages.

## Adding a home

Homes laid out in xLights can be imported:

```sh
uv run python -m pixelhome.xlights ~/path/to/xlights/show homes/<id> --name "My House" \
  --path "Side:-1,Left:-1,Porch Left:-1,Porch Front:1,Porch Right:1,Right:1"
```

Single Line models become segments and the Mesh view object becomes `house.obj`. `--path` is the
order the roofline runs physically (segment and direction); sequences sweep along it. Otherwise
write `home.json` by hand: each segment is a straight run with a start channel, node count and the
positions of its first and last pixel.

## License

MIT
