"""Spoken intros: a short clip to schedule before a sequence, a line read in a cloned voice over the playlist's (or
its occasion's) bed, with the house showing the voice as a red waveform out from the centre of Left, Porch Front and
Right.

A sequence opts in with `VOICEOVER = "the line"`: a line to set the mood, which is followed by the card's
DESCRIPTION so the street knows what to look for (a string of pixels is abstract). Optionally `VOICEOVER_TAKE = n`
for a different reading, `VOICEOVER_VOICE = name` for another reference voice than the occasion's. `python -m pixelhome intro` renders it
locally to homes/<home>/intros/<playlist>/<name>.mp3 plus <name>.json, the voice's loudness at 40 fps; both are
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
VOICES = {'halloween': 'halloween-accent',  # the owner's voice, as re-read with the slight British accent
          'das-rheingold': 'halloween-accent', 'die-walkure': 'halloween-accent', 'siegfried': 'halloween-accent',
          'gotterdammerung': 'halloween-accent'}
GAP, BREATH = 0.7, 0.35                 # pause after the mood line, and between the description's parts


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
    subprocess.run([py, script, json.dumps(todo)], check=True, env=dict(os.environ, PYTORCH_ENABLE_MPS_FALLBACK='1'))


def _parts(text, limit=200):
    """Sentences grouped into parts of at most ~limit characters: Chatterbox wanders on long text."""
    out = []
    for sent in [x.strip() for x in text.replace('. ', '.|').split('|') if x.strip()]:
        if out and len(out[-1]) + 1 + len(sent) <= limit:
            out[-1] += ' ' + sent
        else:
            out.append(sent)
    return out


def _jobs(mod, s):
    """One reading per part: the mood line, then the description."""
    voice = getattr(mod, 'VOICEOVER_VOICE', VOICES.get(s.playlist, VOICES.get(s.occasion, s.occasion)))
    ref = os.path.join(_cache(), 'voice', voice + '.wav')
    if not os.path.exists(ref):
        raise SystemExit(f'{s.id}: no reference voice {ref}')
    take = int(getattr(mod, 'VOICEOVER_TAKE', 0))
    jobs = []
    for text in [mod.VOICEOVER] + _parts(getattr(mod, 'DESCRIPTION', '')):
        h = hashlib.sha256(json.dumps([text, EXAGGERATION, CFG, take]).encode())
        h.update(open(ref, 'rb').read())
        out = os.path.join(_cache(), 'intro-voice', h.hexdigest()[:20] + '.wav')
        jobs.append(dict(text=text, ref=ref, out=out, seed=take, exaggeration=EXAGGERATION, cfg=CFG))
    return jobs


def _spoken(files):
    """The parts' readings, trimmed of their own silence, joined with a pause after the mood line."""
    from pedalboard.io import AudioFile
    from .audio import SR
    out = []
    for i, f in enumerate(files):
        with AudioFile(f).resampled_to(SR) as a:
            v = a.read(a.frames)[0].astype(np.float64)
        on = np.flatnonzero(np.abs(v) > 0.02 * np.abs(v).max())
        v = v[max(0, on[0] - int(0.03 * SR)):on[-1] + int(0.15 * SR)]
        if i:
            out.append(np.zeros(int((GAP if i == 1 else BREATH) * SR)))
        out.append(v / (np.abs(v).max() + 1e-9))
    return np.concatenate(out)


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
    home = s1 + 0.5
    walk = [(['D3', 'F3', 'Bb3'], 'Bb1'), (['D3', 'G3', 'Bb3'], 'G1'), (['D3', 'F3', 'A3'], 'D2'), (['C3', 'E3', 'G3'], 'C2')]
    chords = [(0.0, ['D3', 'F3', 'A3'], 'D2')]
    for i, c0 in enumerate(np.arange(s0, s1 - 2.5, 4.0)):        # a chord every 4 s while it speaks
        chords.append((float(c0), *walk[i % len(walk)]))
    chords += [(s1 - 0.6, ['C#3', 'E3', 'A3'], 'A1'), (home, ['D3', 'F3', 'A3'], 'D2')]
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


def _bed_das_rheingold(n, rng, s0, s1):
    """E flat under the voice, as the Prelude begins: the double basses' low E flat, the bassoons' B flat a
    moment later, and before the first word the horns rise through the Nature motif. Violas hold the chord while
    it speaks; after the last word a muted horn gives the Gold's call in E flat."""
    from .audio import SR, Sampler, note
    from .leitmotifs import play
    T = n / SR

    def track(s, notes, release=0.4):
        out = np.zeros((2, n))
        for t, m, v, d in notes:
            a = s.play(m, v, dur=d, release=release)
            k0 = int(t * SR)
            k = min(n - k0, a.shape[1])
            if k > 0:
                out[:, k0:k0 + k] += a[:, :k]
        return out

    def drone(s, notes, t0, vel, step=2.5):
        """Sustained notes from t0 to the end: overlapping windows of the sample past its attack."""
        out = np.zeros((2, n))
        w = int(2 * step * SR)
        win = np.hanning(w)
        for m in notes:
            for t in np.arange(t0 - step, T, step):
                a = s.play(note(m), vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
                a = a * win[:a.shape[1]]
                k0 = int(t * SR)
                if k0 < 0:
                    a, k0 = a[:, -k0:], 0
                k = min(n - k0, a.shape[1])
                out[:, k0:k0 + k] += a[:, :k]
        rise = np.clip((np.arange(n) / SR - t0) / 1.2, 0, 1)
        return out * rise

    low = drone(Sampler('Strings/Solo Contrabass/SusNV/*.wav', rng, tune=-12), ['Eb1', 'Eb2'], 0.0, 90)
    fifth = drone(Sampler('Woodwinds/Bassoon/sus/*.wav', rng, tune=-12), ['Bb1'], 0.9, 80)
    violas = drone(Sampler('Strings/Viola Section/susvib/*.wav', rng, tune=-12), ['Eb3', 'G3', 'Bb3'], s0, 60)
    horns = track(Sampler('Brass/F Horn/sus/*.wav', rng, tune=-12), play('nature', 0.2, 0.3, 12, 84), 0.8)
    call = track(Sampler('Brass/F Horn/mute/*.wav', rng, tune=-12), play('gold', s1 + 0.45, 0.3, -4, 96), 0.6)
    pre, post = slice(0, int(min(s0, 3.8) * SR)), slice(int((s1 + 0.45) * SR), int((s1 + 2.7) * SR))
    return [(low, -38.0, None), (fifth, -44.0, None), (violas, -45.0, slice(int(s0 * SR), int(s1 * SR))),
            (horns, -35.0, pre), (call, -34.0, post)]


def _bed_die_walkure(n, rng, s0, s1):
    """D minor, as Die Walküre begins: low strings racing up the storm motif over a D tremolo before the first
    word, the tremolo alone under the voice, and after the last word the horns give the Valkyries' call."""
    from .audio import SR, Sampler, note
    from .leitmotifs import play

    def track(s, notes, release=0.3):
        out = np.zeros((2, n))
        for t, m, v, d in notes:
            a = s.play(m, v, dur=d, release=release)
            k0 = int(t * SR)
            k = min(n - k0, a.shape[1])
            if k > 0:
                out[:, k0:k0 + k] += a[:, :k]
        return out

    T = n / SR
    trem = Sampler('Strings/Cello Section/trem/*.wav', rng, tune=-12)
    pulse = track(trem, [(t, note(m), 76, 2.6) for t in np.arange(0.0, T, 2.2) for m in ('D2', 'A2')], 0.6)
    pulse *= np.clip(np.arange(n) / SR / 0.8, 0, 1)
    storm = track(Sampler('Strings/Cello Section/spic/*.wav', rng, tune=-12), play('storm', 0.2, 0.2, 0, 100), 0.1)
    horns = track(Sampler('Brass/F Horn/sus/*.wav', rng, tune=-12), play('valkyries', s1 + 0.4, 0.28, 0, 100), 0.4)
    pre, post = slice(0, int(min(s0, 3.2) * SR)), slice(int((s1 + 0.4) * SR), int(min(T, s1 + 2.8) * SR))
    return [(pulse, -41.0, None), (storm, -36.0, pre), (horns, -34.0, post)]


def _bed_siegfried(n, rng, s0, s1):
    """B flat minor, as Siegfried begins: a timpani roll on the low B flat and the bassoons brooding over the Ring
    before the first word, the roll alone under the voice, and after the last word Siegfried's horn call."""
    from .audio import SR, Hits, Sampler
    from .leitmotifs import play

    def track(s, notes, release=0.3):
        out = np.zeros((2, n))
        for t, m, v, d in notes:
            a = s.play(m, v, dur=d, release=release)
            k0 = int(t * SR)
            k = min(n - k0, a.shape[1])
            if k > 0:
                out[:, k0:k0 + k] += a[:, :k]
        return out

    T = n / SR
    rolls = Hits('Percussion/Timpani/Rolls/*.wav', rng)
    roll = np.zeros((2, n))
    for t in np.arange(0.0, T, 2.8):
        a = rolls.play(80, pitch=-4, dur=3.0)
        k0 = int(t * SR)
        k = min(n - k0, a.shape[1])
        roll[:, k0:k0 + k] += a[:, :k]
    roll *= np.clip(np.arange(n) / SR / 0.8, 0, 1)
    brood = track(Sampler('Woodwinds/Bassoon/sus/*.wav', rng, tune=-12), play('ring_under', 0.2, 0.5, 3, 80), 0.4)
    horn = track(Sampler('Brass/F Horn/sus/*.wav', rng, tune=-12), play('siegfried_horn', s1 + 0.4, 0.3, 5, 100), 0.4)
    pre, post = slice(0, int(min(s0, 3.2) * SR)), slice(int((s1 + 0.4) * SR), int(min(T, s1 + 2.8) * SR))
    return [(roll, -42.0, None), (brood, -36.0, pre), (horn, -34.0, post)]


def _bed_gotterdammerung(n, rng, s0, s1):
    """E flat minor, as Götterdämmerung begins in the Norns' night: a low E flat held by the basses, the Norns'
    motif in the cellos before the first word, and after the last word Hagen's falling tritone on the tubas over a
    timpani stroke."""
    from .audio import SR, Hits, Sampler, note
    from .leitmotifs import play

    def track(s, notes, release=0.3):
        out = np.zeros((2, n))
        for t, m, v, d in notes:
            a = s.play(m, v, dur=d, release=release)
            k0 = int(t * SR)
            k = min(n - k0, a.shape[1])
            if k > 0:
                out[:, k0:k0 + k] += a[:, :k]
        return out

    T = n / SR
    cb = Sampler('Strings/Solo Contrabass/SusNV/*.wav', rng, tune=-12)
    low = track(cb, [(t, note('Eb2'), 84, 2.6) for t in np.arange(0.0, T, 2.2)], 0.6)
    low *= np.clip(np.arange(n) / SR / 1.0, 0, 1)
    norns = track(Sampler('Strings/Cello Section/susvib/*.wav', rng, tune=-12), play('norns', 0.2, 0.22, -12, 90), 0.5)
    hagen = track(Sampler('Brass/Tuba/sus/*.wav', rng, tune=-12), play('hagen', s1 + 0.4, 0.5, -12, 110), 0.5)
    timp = np.zeros((2, n))
    a = Hits('Percussion/Timpani/Timpani1_Hit*.wav', rng).play(110, pitch=-6)
    k0 = int((s1 + 0.9) * SR)
    k = max(0, min(n - k0, a.shape[1]))
    timp[:, k0:k0 + k] += a[:, :k]
    pre, post = slice(0, int(min(s0, 3.2) * SR)), slice(int((s1 + 0.4) * SR), int(min(T, s1 + 2.8) * SR))
    return [(low, -42.0, None), (norns, -35.0, pre), (hagen + 0.6 * timp, -33.0, post)]


def _bed_nightmare(n, rng, s0, s1):
    """E minor under the voice, from the playlist's own themes (pixelhome/nightmare.py): before the first word,
    pizzicato strings pick out the start of the citizens' march over a low E; the choir holds Em, C and B7 while it
    speaks; after the last word the music box answers with the opening of the king's lament, in E minor."""
    import pedalboard as pb
    from .audio import SR, Sampler, Synth, note
    t = np.arange(n) / SR
    T = n / SR

    def track(s, notes, release=0.3):
        out = np.zeros((2, n))
        for t0, m, v, d in notes:
            a = s.play(m, v, dur=d, release=release)
            k0 = int(t0 * SR)
            k = min(n - k0, a.shape[1])
            if k > 0:
                out[:, k0:k0 + k] += a[:, :k]
        return out

    beat = 0.42
    march = [(0, 1, 'E4'), (1, .5, 'E4'), (1.5, .5, 'F#4'), (2, 1, 'G4'), (3, 1, 'B4')]
    pizz = track(Sampler('Strings/Violin Section/Pizz/*.wav', rng, tune=-12),
                 [(0.3 + b * beat, note(m), 92, d * beat) for b, d, m in march])
    bass = track(Sampler('Strings/Solo Contrabass/Pizz/*.wav', rng, tune=-12),
                 [(0.3 + b * beat, note('E2' if b % 2 == 0 else 'B1'), 96, 0.4) for b in range(4)])
    chords = [(0.0, ['E3', 'G3', 'B3'])]
    walk = [['E3', 'G3', 'C4'], ['D#3', 'F#3', 'B3'], ['E3', 'G3', 'B3']]
    for i, c0 in enumerate(np.arange(s0, s1 - 2.0, 3.5)):
        chords.append((float(c0), walk[i % len(walk)]))
    chords.append((s1 + 0.4, ['E3', 'G3', 'B3']))
    ends = [c[0] for c in chords[1:]] + [T]
    choir = [(c0, note(m), 42, c1 - c0 + 0.15) for (c0, triad), c1 in zip(chords, ends) for m in triad]
    voices = Synth('Pads/Ooh').render(choir, T + 2)[:, :n] * np.clip(t / 1.0, 0, 1)
    lament = [(0, 1, 'E4'), (1, 1, 'G4'), (2, 1, 'B4'), (3, 2, 'C5'), (5, 1, 'B4')]
    box = Synth('Plucks/Magic Music Box').render([(s1 + 0.5 + 0.4 * b, note(m), 58, 0.4 * d) for b, d, m in lament],
                                                 T + 3)[:, :n]
    box = pb.Pedalboard([pb.LowpassFilter(3500), pb.Reverb(room_size=0.6, damping=0.5, wet_level=0.35,
                                                           dry_level=0.8)])(box.astype(np.float32), SR)
    pre, post = slice(0, int(min(s0, 2.4) * SR)), slice(int((s1 + 0.5) * SR), int(min(T, s1 + 2.9) * SR))
    return [(voices, -38.0, None), (pizz, -33.0, pre), (bass, -38.0, pre), (box, -34.0, post)]


BEDS = {'halloween': _bed_halloween, 'das-rheingold': _bed_das_rheingold, 'die-walkure': _bed_die_walkure,
        'siegfried': _bed_siegfried, 'gotterdammerung': _bed_gotterdammerung,
        'nightmare': _bed_nightmare}


def _rms(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)


def _at(x, db, part=None):
    """x scaled so its rms (over part) sits at db."""
    return x * 10 ** ((db - _rms(x if part is None else x[:, part])) / 20)


def mix(files, playlist, seed):
    """Readings of the parts -> (stereo mix, voice loudness per frame)."""
    import pedalboard as pb
    from .audio import SR
    v = _spoken(files)
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
    if playlist in BEDS:
        lvl = np.convolve(np.abs(voice[0]), np.ones(SR // 4) / (SR // 4), 'same')
        duck = 1 - 0.5 * np.clip(lvl / (np.percentile(lvl[s:s + len(dry)], 90) + 1e-9), 0, 1)
        said = np.flatnonzero(np.abs(dry) > 0.05 * np.abs(dry).max())       # where the words actually are
        s0, s1 = PRE + said[0] / SR, PRE + said[-1] / SR
        bed = sum(_at(x, db, part) for x, db, part in BEDS[playlist](n, np.random.default_rng(seed), s0, s1))
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
            todo.append((s, _jobs(mod, s)))
    os.makedirs(os.path.join(_cache(), 'intro-voice'), exist_ok=True)
    _takes([j for _, js in todo for j in js])
    for s, js in todo:
        bed = s.playlist if s.playlist in BEDS else s.occasion
        audio, env = mix([j['out'] for j in js], bed, int(hashlib.sha256(s.id.encode()).hexdigest()[:8], 16))
        mp3, js = paths(s)
        write_mp3(mp3, audio)
        with open(js, 'w') as f:
            json.dump(dict(seconds=round(audio.shape[1] / SR, 3), fps=round(1 / DT), env=np.round(env, 3).tolist()),
                      f, separators=(',', ':'))
        print(f'{s.home}/{s.id}: {mp3} {audio.shape[1] / SR:.1f}s  rms {_rms(audio):.1f} dBFS')
