"""Spoken intros: a short clip to schedule before a sequence, a line read in a cloned voice over the occasion's
bed, with the house showing the voice as a red waveform out from the centre of Left, Porch Front and Right.

A sequence opts in with `VOICEOVER = "the line"` (and optionally `VOICEOVER_TAKE = n` for a different reading,
`VOICEOVER_VOICE = name` for another reference voice than the occasion's). `python -m pixelhome intro` renders it
locally to homes/<home>/intros/<occasion>/<name>.mp3 plus <name>.json, the voice's loudness at 40 fps; both are
committed, and the build turns the JSON into the FSEQ. Voices are ~10 s reference recordings in
~/.cache/pixelhome/voice/<name>.wav, never committed; Chatterbox runs in its own venv (scripts/audio-setup.sh).
"""
import hashlib, json, os, subprocess
import numpy as np
from . import catalog
from .fx import DT, hexc, light

PRE, POST = 2.2, 2.8                    # seconds of bed before the first word and after the last
EXAGGERATION, CFG = 0.5, 0.5            # Chatterbox's defaults: the reading that sounded most like a person
RED = hexc('#ff0800')
WAVE = ('Left', 'Porch Front', 'Right')
FLOOR = 0.04                            # perceptual: the three runs never go fully dark while it plays


def _cache():
    from .audio import CACHE
    return CACHE


def paths(s):
    base = os.path.join(catalog.HOMES, s.home, 'intros', s.id)
    return base + '.mp3', base + '.json'


# ---------------------------------------------------------------------------- the lights

def frames(home, env):
    """(F, N, 3) PWM: each run in WAVE lights out from its middle as far as the voice is loud."""
    env = np.asarray(env, float)
    F = len(env)
    out = np.zeros((F, home.N, 3))
    t = np.arange(F) * DT
    floor = FLOOR * np.clip(t / 0.6, 0, 1) * np.clip((t[-1] - t) / 0.8, 0, 1)
    for name in WAVE:
        if name not in home.seg:
            continue
        idx = home.seg[name]
        d = home.pd[idx]
        u = np.abs(d - (d.min() + d.max()) / 2) / ((d.max() - d.min()) / 2)       # 0 middle .. 1 ends
        e = env[:, None]
        reach = np.clip((e - u[None, :]) / 0.08, 0, 1)                            # soft front edge
        core = 0.55 + 0.45 * np.clip(1 - u[None, :] / np.maximum(e, 1e-3), 0, 1)  # brightest in the middle
        out[:, idx] = light(RED, np.maximum(floor[:, None], reach * core * (0.35 + 0.65 * e)))
    return out


# ---------------------------------------------------------------------------- the voice

def _takes(jobs):
    """Render the readings that aren't cached yet, all in one Chatterbox run."""
    todo = [j for j in jobs if not os.path.exists(j['out'])]
    if not todo:
        return
    py = os.path.join(_cache(), 'chatterbox', 'bin', 'python')
    if not os.path.exists(py):
        raise SystemExit(f'{py} not found: run scripts/audio-setup.sh')
    script = os.path.join(catalog.ROOT, 'scripts', 'chatterbox-say.py')
    tmp = [dict(j, out=j['out'] + '.tmp.wav') for j in todo]
    subprocess.run([py, script, json.dumps(tmp)], check=True, env=dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK='1'))
    for j in tmp:
        os.replace(j['out'], j['out'][:-len('.tmp.wav')])


def _job(mod, s):
    voice = getattr(mod, 'VOICEOVER_VOICE', s.occasion)
    ref = os.path.join(_cache(), 'voice', voice + '.wav')
    if not os.path.exists(ref):
        raise SystemExit(f'{s.id}: no reference voice {ref}')
    take = int(getattr(mod, 'VOICEOVER_TAKE', 0))
    h = hashlib.sha256(json.dumps([mod.VOICEOVER, EXAGGERATION, CFG, take]).encode())
    h.update(open(ref, 'rb').read())
    out = os.path.join(_cache(), 'intro-voice', h.hexdigest()[:20] + '.wav')
    return dict(text=mod.VOICEOVER, ref=ref, out=out, seed=take, exaggeration=EXAGGERATION, cfg=CFG)


def _envelope(v, sr):
    """Voice (mono, at sr, already offset by PRE) -> loudness 0..1 per 40 fps frame: fast up, eased down."""
    hop = int(round(DT * sr))
    F = int(np.ceil(len(v) / hop))
    w = np.pad(v, (hop, F * hop - len(v) + hop)) ** 2
    rms = np.sqrt(np.convolve(w, np.ones(2 * hop) / (2 * hop), 'same')[hop:hop + F * hop:hop] + 1e-12)
    db = 20 * np.log10(rms / np.percentile(rms[rms > rms.max() * 1e-3], 95))
    e = np.clip((db + 30) / 30, 0, 1) ** 1.3
    for i in range(1, F):
        e[i] = max(e[i], e[i - 1] * np.exp(-DT / 0.12))
    return e


# ---------------------------------------------------------------------------- the beds

# phrases for the music box, one picked per intro: before the first word, and the answer after the last
BOX = [(['D5', 'F5', 'A5', 'G5'], ['F5', 'E5', 'D5', 'C#5', 'D5']),
       (['A4', 'D5', 'E5', 'F5'], ['E5', 'C#5', 'A4', 'D5']),
       (['F5', 'E5', 'D5', 'A4'], ['Bb4', 'A4', 'G4', 'A4', 'D5'])]


def _bed_halloween(n, rng, s0, s1):
    """D minor under the voice. Before the first word: a bell, a music-box phrase and the choir on Dm. While it
    speaks: Bb, Gm, A in choir and low strings. After the last word: home to Dm, and the music box answers.
    A faint wind underneath. s0, s1: seconds where the voice starts and stops."""
    import pedalboard as pb
    from .audio import SR, Sampler, Synth, VSCO, _load, note
    t = np.arange(n) / SR
    T = n / SR
    mid = (s0 + s1) / 2
    home = s1 + 0.5
    chords = [(0.0, ['D3', 'F3', 'A3'], 'D2'), (s0, ['D3', 'F3', 'Bb3'], 'Bb1'), (mid, ['D3', 'G3', 'Bb3'], 'G1'),
              (s1 - 0.6, ['C#3', 'E3', 'A3'], 'A1'), (home, ['D3', 'F3', 'A3'], 'D2')]
    choir, ends = [], [c[0] for c in chords[1:]] + [T]
    for (c0, triad, _), c1 in zip(chords, ends):
        choir += [(c0, note(m), 40 + 6 * (i == 2), c1 - c0 + 0.15) for i, m in enumerate(triad)]
    voices = Synth('Pads/Ooh').render(choir, T + 2)[:, :n] * np.clip(t / 1.2, 0, 1)
    cello = Sampler('Strings/Cello Section/susvib/*.wav', rng, tune=-12)
    low = np.zeros((2, n))
    for (c0, _, root), c1 in zip(chords, ends):
        a = cello.play(note(root) + 12, 70, dur=c1 - c0 + 0.3, release=0.6)
        k0 = int(c0 * SR)
        k = min(n - k0, a.shape[1])
        fade = np.clip(np.arange(k) / (0.4 * SR), 0, 1)
        low[:, k0:k0 + k] += a[:, :k] * fade
    box = Synth('Plucks/Magic Music Box')
    pre, post = BOX[int(rng.integers(len(BOX)))]
    music = box.render([(0.9 + 0.34 * i, note(m), 60 - 4 * i, 0.5) for i, m in enumerate(pre)]
                       + [(home + 0.15 + 0.38 * i, note(m), 54, 0.6) for i, m in enumerate(post)], T + 3)[:, :n]
    music = pb.Pedalboard([pb.LowpassFilter(3500), pb.Reverb(room_size=0.6, damping=0.5, wet_level=0.35,
                                                             dry_level=0.8)])(music.astype(np.float32), SR)
    g = _load(os.path.join(VSCO, 'Percussion/gongHit_p.wav'))
    idx = np.arange(0, g.shape[1] - 1, 2 ** (-5 / 12))
    g = np.vstack([np.interp(idx, np.arange(g.shape[1]), g[c]) for c in range(2)])
    bell = np.zeros((2, n))
    b0 = int(0.25 * SR)
    k = min(n - b0, g.shape[1])
    bell[:, b0:b0 + k] = g[:, :k]
    bell = pb.Pedalboard([pb.LowpassFilter(1800), pb.Reverb(room_size=0.9, damping=0.5, wet_level=0.6, dry_level=0.25,
                                                            width=1.0)])(bell.astype(np.float32), SR)
    air = rng.normal(0, 1, (2, n)).astype(np.float32)
    air = pb.Pedalboard([pb.HighpassFilter(200), pb.LowpassFilter(600),
                         pb.LadderFilter(pb.LadderFilter.Mode.BPF12, cutoff_hz=380, resonance=0.4)])(air, SR)
    gust = np.clip(np.sin(2 * np.pi * t / 6.5 + rng.uniform(0, 6.3)), 0, 1) ** 2      # comes and goes
    wind = air / np.abs(air).max() * gust
    return [(voices, -37.0, None), (low, -40.0, None), (music, -34.0, slice(int(0.9 * SR), int(2.4 * SR))),
            (bell, -33.0, slice(b0, int(2.5 * SR))), (wind, -50.0, None)]


BEDS = {'halloween': _bed_halloween}


def _rms(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def _at(x, db, part=None):
    """x scaled so its rms (over part) sits at db."""
    return x * 10 ** ((db - _rms(x if part is None else x[:, part])) / 20)


def mix(take, occasion, seed):
    """Voice file -> (stereo mix, voice loudness per frame)."""
    import pedalboard as pb
    from pedalboard.io import AudioFile
    from .audio import SR
    with AudioFile(take).resampled_to(SR) as f:
        v = f.read(f.frames)[0].astype(np.float64)
    v /= np.abs(v).max() + 1e-9
    n = int((PRE + len(v) / SR + POST) * SR)
    s = int(PRE * SR)
    dry = pb.Pedalboard([pb.HighpassFilter(80), pb.Compressor(threshold_db=-20, ratio=2.5, attack_ms=5,
                                                              release_ms=120)])(v[None].astype(np.float32), SR)[0]
    voice = np.zeros((2, n))
    voice[:, s:s + len(dry)] = dry
    room = pb.Pedalboard([pb.HighpassFilter(200), pb.Reverb(room_size=0.22, damping=0.6, wet_level=1.0, dry_level=0.0,
                                                            width=0.7)])
    voice = _at(voice + 0.07 * room(voice.astype(np.float32), SR), -17.0, slice(s, s + len(dry)))
    t = np.arange(n) / SR
    out = voice
    if occasion in BEDS:
        lvl = np.convolve(np.abs(voice[0]), np.ones(SR // 4) / (SR // 4), 'same')
        duck = 1 - 0.5 * np.clip(lvl / (np.percentile(lvl[s:s + len(dry)], 90) + 1e-9), 0, 1)
        said = np.flatnonzero(np.abs(dry) > 0.05 * np.abs(dry).max())       # where the words actually are
        s0, s1 = PRE + said[0] / SR, PRE + said[-1] / SR
        bed = sum(_at(x, db, part) for x, db, part in BEDS[occasion](n, np.random.default_rng(seed), s0, s1))
        out = voice + bed * duck
    out = out * np.clip(t / 0.4, 0, 1) * np.clip((n / SR - t) / 1.6, 0, 1)
    out = pb.Pedalboard([pb.Limiter(threshold_db=-2.0, release_ms=120), pb.Gain(-1.0)])(out.astype(np.float32), SR)
    env = _envelope(np.pad(dry.astype(np.float64), (s, n - s - len(dry))), SR)
    return out, env


def intro(want, occasion=None):
    """Render the intro of every matching sequence that has a VOICEOVER line."""
    from .audio import SR, write_mp3
    from .build import _matches
    todo = []
    for h in catalog.homes():
        for s in catalog.sequences(h, occasion):
            if not _matches(s, want):
                continue
            mod = s.load()
            if not hasattr(mod, 'VOICEOVER'):
                print(f'{h}/{s.id}: no VOICEOVER')
                continue
            todo.append((s, _job(mod, s)))
    os.makedirs(os.path.join(_cache(), 'intro-voice'), exist_ok=True)
    _takes([j for _, j in todo])
    for s, j in todo:
        audio, env = mix(j['out'], s.occasion, int(hashlib.sha256(s.id.encode()).hexdigest()[:8], 16))
        mp3, js = paths(s)
        write_mp3(mp3, audio)
        with open(js, 'w') as f:
            json.dump(dict(seconds=round(audio.shape[1] / SR, 3), fps=round(1 / DT), env=np.round(env, 3).tolist()),
                      f, separators=(',', ':'))
        print(f'{s.home}/{s.id}: {mp3} {audio.shape[1] / SR:.1f}s  rms {_rms(audio):.1f} dBFS  "{j["text"]}"')
