"""Music for shows. A sequence module may define `score(M)`, which writes its soundtrack into the mix `M`
from the same timings that drive its lights; `python -m pixelhome music` renders it to
homes/<home>/audio/<occasion>/<name>.mp3, which is committed (CI only copies it into the site).

Rendering is local: it needs Surge XT's Python module (surgepy) and the VSCO2 Community Edition samples
in ~/.cache/pixelhome (see scripts/audio-setup.sh). Run with `uv run --group audio`.

Instruments:
  M.synth(patch)            a Surge XT factory patch, e.g. 'Keys/Circus 1'; .render([(t, note, vel, dur)], seconds)
  M.sampler(pattern)        pitched VSCO2 samples (glob under the library), e.g. 'Percussion/Xylo/*.wav'
  M.hits(pattern)           unpitched one-shots, a random round-robin pick per hit
  slide(), whoosh()         small numpy sound effects
Each returns stereo (2, n) float arrays or writes into a bus with M.add(bus, signal, t).

Pitch: most VSCO2 CE sets are labelled with C3 as middle C, so a note asked of them sounds an octave higher
(`tune=-12` plays them as written); Harp, Upright piano and Solo Violin pizz are labelled at pitch. Shows play
outdoors to the street, so nothing should sit piercingly high: `music` renders a score twice, and on the
second pass each instrument made with M.sampler/M.synth drops by octaves until the middle of its part sits a
fifth or more under its ceiling (E6, or C7 for bells and mallets), and any note still over the ceiling folds
down an octave. Pass ceiling=None to keep an instrument where it was written.
"""
import glob
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

SR = 48000
CACHE = os.environ.get('PIXELHOME_CACHE', os.path.expanduser('~/.cache/pixelhome'))
VSCO = os.path.join(CACHE, 'vsco2')
SURGE = os.path.join(CACHE, 'surge')
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
NOTE_RE = re.compile(r'(?:^|[_\- ])([A-G])(#|b)?(-?\d)(?=[_\- .]|$)')
AT_PITCH = ('Strings/Harp/', 'Keys/Upright', 'Strings/Solo Violin/Pizz/')    # the VSCO2 sets labelled at pitch
BRIGHT = ('Percussion/Glock', 'Percussion/Xylo', 'Percussion/TB_hit', 'Plucks/Bell', 'Plucks/Fantasy Bell',
          'Plucks/Magic Music Box', 'Pads/Bells')
CEILING, CEILING_BRIGHT = 88, 96         # E6, C7: no note sounds above these
CENTRE = 7                               # a part's median sits at least a fifth under its ceiling


def note(name):
    """'C4' -> 60, 'F#2' -> 42, 'Bb3' -> 58."""
    m = re.fullmatch(r'([A-G])(#|b)?(-?\d)', name)
    return 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + {'#': 1, 'b': -1, None: 0}[m.group(2)]


def _surgepy():
    os.environ.setdefault('SURGE_DATA_HOME', os.path.join(SURGE, 'resources', 'data'))
    sys.path.insert(0, os.path.join(SURGE, 'build', 'src', 'surge-python'))
    import surgepy
    return surgepy


_WAV = {}


def _load(path):
    if path not in _WAV:
        from pedalboard.io import AudioFile
        with AudioFile(path).resampled_to(SR) as f:
            a = f.read(f.frames)
        if a.shape[0] == 1:
            a = np.vstack([a, a])
        a = a[:2].astype(np.float64)
        _WAV[path] = a / (np.abs(a).max() + 1e-9)     # every sample at full scale; velocity and gain set levels
    return _WAV[path]


def _pan(sig, pan):
    """Constant-power pan, -1 left .. 1 right."""
    a = (pan + 1) * math.pi / 4
    return sig * np.array([[math.cos(a) * math.sqrt(2)], [math.sin(a) * math.sqrt(2)]])


def _ceiling(name, ceiling):
    if ceiling != 'auto':
        return ceiling
    return CEILING_BRIGHT if name.startswith(BRIGHT) else CEILING


def _octaves(heard, ceiling):
    """Octaves to drop a part so the middle of what it plays sits a fifth under the ceiling."""
    if ceiling is None or not heard:
        return 0
    return max(0, math.ceil((np.median(heard) - (ceiling - CENTRE)) / 12))


class _Voice:
    """What M.sampler and M.synth instruments share: the probe pass records what they sound, the second
    pass moves them down by the planned octaves and folds the outliers."""
    shift, ceiling, heard = 0, None, None

    def _place(self, m):
        """Sounding pitch m -> sounding pitch to play."""
        if self.heard is not None:
            self.heard.append(m)
        if self.ceiling is None:
            return m
        m -= 12 * self.shift
        while m > self.ceiling:
            m -= 12
        return m


def _fade_out(sig, start, length):
    n = sig.shape[1]
    s = int(start * SR)
    if s >= n:
        return sig
    e = min(n, s + max(1, int(length * SR)))
    sig = sig[:, :e].copy()
    sig[:, s:e] *= np.linspace(1, 0, e - s) ** 2
    return sig


class Sampler(_Voice):
    """Pitched samples: the nearest recorded note is resampled to the one asked for. Velocity layers
    (_v1 soft .. _vN loud) and round robins (_rr1..) are picked from the file names when present."""
    label = 0                               # sounding pitch minus the note in the file name

    def __init__(self, pattern, rng, gain=1.0, tune=0):
        self.zones = {}
        for p in sorted(glob.glob(os.path.join(VSCO, pattern))):
            m = NOTE_RE.search(os.path.basename(p))
            if not m:
                continue
            n = 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + {'#': 1, 'b': -1, None: 0}[m.group(2)]
            v = re.search(r'_v(\d+)', p)
            self.zones.setdefault(n, {}).setdefault(int(v.group(1)) if v else 1, []).append(p)
        if not self.zones:
            raise FileNotFoundError(f'no samples match {pattern} under {VSCO}')
        self.keys = np.array(sorted(self.zones))
        self.rng, self.gain, self.tune = rng, gain, tune
        self.label = 0 if pattern.startswith(AT_PITCH) else 12

    def play(self, n, vel=100, dur=None, release=0.12):
        n = self._place(n + self.tune + self.label) - self.label
        k = int(self.keys[np.argmin(np.abs(self.keys - n))])
        layers = self.zones[k]
        lv = sorted(layers)
        li = lv[min(len(lv) - 1, int(vel / 128 * len(lv)))]
        a = _load(layers[li][int(self.rng.integers(len(layers[li])))])
        r = 2 ** ((n - k) / 12)
        idx = np.arange(0, a.shape[1] - 1, r)
        out = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
        out *= self.gain * (vel / 127) ** (1.0 if len(lv) > 1 else 1.7)
        return _fade_out(out, dur, release) if dur is not None else out


class Hits:
    """Unpitched one-shots chosen at random from a glob (use separate globs for separate dynamics)."""

    def __init__(self, pattern, rng, gain=1.0):
        self.files = sorted(glob.glob(os.path.join(VSCO, pattern)))
        if not self.files:
            raise FileNotFoundError(f'no samples match {pattern} under {VSCO}')
        self.rng, self.gain = rng, gain

    def play(self, vel=100, pitch=0.0, dur=None):
        a = _load(self.files[int(self.rng.integers(len(self.files)))])
        if pitch:
            idx = np.arange(0, a.shape[1] - 1, 2 ** (pitch / 12))
            a = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
        out = a * self.gain * (vel / 127) ** 1.7
        return _fade_out(out, dur, 0.05) if dur is not None else out


class Synth(_Voice):
    """A Surge XT instance with a factory patch. Notes are (t, midi note, velocity, duration) and land on
    Surge's 32-sample blocks (0.7 ms); bends are (t, value -8192..8191)."""

    def __init__(self, patch):
        sp = _surgepy()
        self.s = sp.createSurge(SR)
        path = os.path.join(self.s.getFactoryDataPath(), 'patches_factory', patch + '.fxp')
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        self.s.loadPatch(path)
        self.bs = self.s.getBlockSize()

    def render(self, notes, seconds, bends=(), ch=0):
        s, bs = self.s, self.bs
        nb = int(math.ceil(seconds * SR / bs)) + 1
        ev = []
        for t, n, v, d in notes:
            n = self._place(int(n))
            ev.append((int(t * SR / bs), 1, int(n), int(v)))
            ev.append((int((t + d) * SR / bs), 0, int(n), 0))
        for t, v in bends:
            ev.append((int(t * SR / bs), 2, int(v), 0))
        ev.sort(key=lambda e: (e[0], e[1]))
        buf = s.createMultiBlock(nb)
        b, i = 0, 0
        while b < nb:
            while i < len(ev) and ev[i][0] <= b:
                _, kind, n, v = ev[i]
                if kind == 1:
                    s.playNote(ch, n, v, 0)
                elif kind == 0:
                    s.releaseNote(ch, n, 0)
                else:
                    s.pitchBend(ch, n)
                i += 1
            step = (ev[i][0] - b) if i < len(ev) else nb - b
            step = max(1, min(step, nb - b))
            s.processMultiBlock(buf, b, step)
            b += step
        return np.asarray(buf, dtype=np.float64)


def slide(t0, t1, f0, f1, seconds, amp=0.3, shape=0.5):
    """Slide whistle from f0 to f1 Hz between t0 and t1 (relative to the returned buffer start)."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    u = np.clip((t - t0) / max(t1 - t0, 1e-3), 0, 1)
    u = u ** shape if f1 > f0 else 1 - (1 - u) ** shape
    f = f0 * (f1 / f0) ** u
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.clip(t / 0.03, 0, 1) * np.clip((seconds - t) / 0.06, 0, 1)
    rng = np.random.default_rng(7)
    breath = np.convolve(rng.normal(0, 1, n), np.ones(24) / 24, 'same') * 0.08
    sig = amp * env * (np.sin(ph) + 0.12 * np.sin(2 * ph) + breath * (1 + np.sin(ph)))
    return np.vstack([sig, sig])


def whoosh(seconds, f0=300.0, f1=3000.0, amp=0.25, seed=0):
    """Band-passed noise sweeping from f0 to f1: something flying past."""
    n = int(seconds * SR)
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    t = np.arange(n) / n
    fc = f0 * (f1 / f0) ** t
    # two cascaded one-pole low-pass minus high-pass, with a moving cutoff
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(n)
    z = 0.0
    for i in range(n):
        z = (1 - a[i]) * x[i] + a[i] * z
        y[i] = z
    y = np.diff(np.concatenate([[0], y])) * 6
    env = np.sin(np.pi * t) ** 1.5
    sig = amp * env * y / (np.abs(y).max() + 1e-9)
    return np.vstack([sig, sig])


class Mix:
    """Buses summed through a shared reverb send and a gentle master (compressor, limiter). With loop=True (all-night
    ambient pieces) the mix is a seamless loop: whatever rings past the end, reverb included, wraps round onto the
    start, and there are no fades."""
    TAIL = 10                       # seconds rendered past the end of a loop, then wrapped onto its start

    def __init__(self, seconds, seed=1, plan=None, loop=False):
        self.seconds = seconds
        self.loop = loop
        self.n = int(seconds * SR) + (self.TAIL if loop else 1) * SR
        self.rng = np.random.default_rng(seed)
        self.buses = {}
        self.plan = plan            # octaves to drop each instrument, by creation order; None on the probe pass
        self.voices = []

    def bus(self, name, gain=1.0, pan=0.0, reverb=0.15):
        self.buses[name] = dict(sig=np.zeros((2, self.n)), gain=gain, pan=pan, reverb=reverb)

    def add(self, bus, sig, t=0.0, gain=1.0, pan=None):
        b = self.buses[bus]
        s = int(round(t * SR))
        if s < 0:
            sig, s = sig[:, -s:], 0
        e = min(self.n, s + sig.shape[1])
        if e <= s:
            return
        part = sig[:, :e - s] * gain
        if pan is not None:
            part = _pan(part, pan)
        b['sig'][:, s:e] += part

    def _voice(self, v, name, ceiling):
        v.name = name
        v.ceiling = _ceiling(name, ceiling)
        if self.plan is None:
            v.heard = []
        else:
            v.shift = self.plan[len(self.voices)]
        self.voices.append(v)
        return v

    def synth(self, patch, ceiling='auto'):
        return self._voice(Synth(patch), patch, ceiling)

    def sampler(self, pattern, gain=1.0, tune=0, ceiling='auto'):
        return self._voice(Sampler(pattern, self.rng, gain, tune), pattern, ceiling)

    def planned(self):
        """After the probe pass: octaves to drop each instrument on the second."""
        return [_octaves(v.heard, v.ceiling) for v in self.voices]

    def hits(self, pattern, gain=1.0):
        return Hits(pattern, self.rng, gain)

    def render(self, fade_in=0.0, fade_out=1.5):
        import pedalboard as pb
        dry = np.zeros((2, self.n))
        send = np.zeros((2, self.n))
        for b in self.buses.values():
            s = _pan(b['sig'], b['pan']) * b['gain']
            dry += s
            send += s * b['reverb']
        verb = pb.Pedalboard([pb.HighpassFilter(250), pb.Reverb(room_size=0.82, damping=0.45, wet_level=1.0,
                                                               dry_level=0.0, width=1.0)])
        wet = verb(send.astype(np.float32), SR)
        out = dry + wet
        N = int(self.seconds * SR)
        master = pb.Pedalboard([pb.HighpassFilter(30), pb.Compressor(threshold_db=-18, ratio=2.0, attack_ms=10,
                                                                     release_ms=180),
                                pb.Gain(2.5), pb.Limiter(threshold_db=-2.0, release_ms=120),
                                pb.Gain(-1.0)])   # JUCE's limiter brings its threshold up to 0 dBFS
        if self.loop:
            out, tail = out[:, :N].copy(), out[:, N:]
            out[:, :tail.shape[1]] += tail
            # run the master over two passes and keep the second, so its compressor starts the loop where it ends
            return master(np.concatenate([out, out], axis=1).astype(np.float32), SR)[:, N:]
        out = out[:, :N]
        t = np.arange(out.shape[1]) / SR
        env = np.ones_like(t)
        if fade_in:
            env *= np.clip(t / fade_in, 0, 1)
        env *= np.clip((self.seconds - t) / fade_out, 0, 1)
        out *= env
        return master(out.astype(np.float32), SR)

    def write(self, path, audio=None):
        audio = self.render() if audio is None else audio
        write_mp3(path, audio)
        return audio


def write_mp3(path, audio):
    """Stereo (2, n) float at SR -> 192k MP3, byte-reproducible."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(audio.T, -1, 1) * 32767).astype('<i2')
    import wave
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, 'mix.wav')
        with wave.open(w, 'wb') as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(SR)
            f.writeframes(pcm.tobytes())
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', w, '-codec:a', 'libmp3lame', '-b:a', '192k',
                        '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', path], check=True)


def audio_path(s):
    """Where a sequence's soundtrack lives: homes/<home>/audio/<occasion>/<name>.mp3."""
    from . import catalog
    return os.path.join(catalog.HOMES, s.home, 'audio', s.id + '.mp3')


def music(want, occasion=None, video=False, out=None):
    """Render the score of every matching sequence that has one; with video, also an MP4 of the lights with it."""
    import time
    from . import catalog
    from .build import _matches, preview
    for h in catalog.homes():
        home = catalog.load_home(h)
        for s in catalog.sequences(h, occasion):
            if not _matches(s, want):
                continue
            mod = s.load()
            if not hasattr(mod, 'score'):
                print(f'{h}/{s.id}: no score()')
                continue
            t = time.time()
            seconds = len(mod.render(home)) / 40 if not hasattr(mod, 'D') else float(mod.D)
            loop = getattr(mod, 'KIND', 'show') == 'ambient'
            probe = Mix(seconds, loop=loop)
            mod.score(probe, home)
            M = Mix(seconds, plan=probe.planned(), loop=loop)
            mod.score(M, home)
            moved = [f'{v.name} -{v.shift * 12}' for v in M.voices if v.shift]
            path = audio_path(s)
            a = M.write(path)
            peak = float(np.abs(a).max())
            rms = float(np.sqrt((a ** 2).mean()))
            print(f'{h}/{s.id}: {path} {seconds:.0f}s  peak {peak:.2f}  rms {20 * np.log10(rms + 1e-9):.1f} dBFS  '
                  f'{os.path.getsize(path) / 1e6:.1f} MB  in {time.time() - t:.1f}s')
            if moved:
                print('  lowered (semitones): ' + ', '.join(moved))
            if video:
                out = out or os.path.join(catalog.ROOT, 'build', 'preview')
                preview([s.code], out, s.playlist, True)
                v = os.path.join(out, f'{h} {s.code} {s.title} preview.mp4')
                subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', v, '-i', path, '-c:v', 'copy', '-c:a', 'aac',
                                '-b:a', '192k', '-shortest', v.replace(' preview.mp4', ' with music.mp4')], check=True)
                print(v.replace(' preview.mp4', ' with music.mp4'))
