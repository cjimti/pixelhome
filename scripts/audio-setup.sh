#!/bin/sh
# One-time setup for rendering soundtracks (`python -m pixelhome music`): builds Surge XT's Python module and
# fetches the VSCO2 Community Edition samples into ~/.cache/pixelhome (override with PIXELHOME_CACHE).
# Needs git, cmake, a C++ toolchain (Xcode command line tools) and ffmpeg. Takes about 10 minutes and 3 GB.
set -e
cd "$(dirname "$0")/.."
CACHE="${PIXELHOME_CACHE:-$HOME/.cache/pixelhome}"
mkdir -p "$CACHE"
uv sync --group audio
PY="$PWD/.venv/bin/python"

if [ ! -d "$CACHE/vsco2" ]; then
  git clone --depth 1 https://github.com/sgossner/VSCO-2-CE.git "$CACHE/vsco2"
fi

if [ ! -d "$CACHE/surge" ]; then
  # Surge main: the 1.3.x release tags no longer compile with current Apple clang
  git clone --depth 1 https://github.com/surge-synthesizer/surge.git "$CACHE/surge"
  git -C "$CACHE/surge" submodule update --init --recursive --depth 1
fi
if ! ls "$CACHE"/surge/build/src/surge-python/surgepy*.so >/dev/null 2>&1; then
  cmake -S "$CACHE/surge" -B "$CACHE/surge/build" -DCMAKE_BUILD_TYPE=Release -DSURGE_BUILD_PYTHON_BINDINGS=ON \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DPython_EXECUTABLE="$PY" -DPYTHON_EXECUTABLE="$PY"
  cmake --build "$CACHE/surge/build" --target surgepy --parallel
fi
echo "ready: uv run --group audio python -m pixelhome music <CODE>"
