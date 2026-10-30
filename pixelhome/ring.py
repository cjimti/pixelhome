"""Wagner's actual music for the Ring sequences.

Each Ring scene plays an excerpt of the real score: its notes come from the Wagner Ring Dataset (Christof Weiß,
Vlora Arifi-Müller, Michael Krause, Frank Zalkow, Stephanie Klauk, Rainer Kleinertz and Meinard Müller, Zenodo
7672157, CC BY 3.0), a piano reduction of the full score of all eleven acts, timed by the measure positions of a
recorded performance. scripts/ring_excerpt.py cuts the excerpt and writes it beside the sequence as
<name>.score.json, which is committed; excerpt() loads it.

To cut new excerpts, fetch the dataset's scores and annotations (about 190 MB of a 10.5 GB zip) into
~/.cache/pixelhome/wagner-ring:

    uv run --no-project --with remotezip python -c "from remotezip import RemoteZip; z = RemoteZip('https://zenodo.org/api/records/7672157/files/WagnerRing_Public_zenodo_v0-1.zip/content'); [z.extract(n, '.') for n in z.namelist() if any(k in n for k in ('score_midi', 'ann_score', 'ann_audio_measure')) and not n.endswith('/')]"
"""
import json
import os

import numpy as np

CREDIT = 'Wagner Ring Dataset (Weiß, Arifi-Müller, Krause, Zalkow, Klauk, Kleinertz, Müller), CC BY 3.0'


def excerpt(module_file):
    """The excerpt beside a sequence module: dict(seconds, bars=[[measure, t]], singing=[[t0, t1, who, text]],
    notes=[[t, seconds, midi, velocity, hand]]) with hand 0 the right hand (upper staff) and 1 the left."""
    path = os.path.splitext(module_file)[0] + '.score.json'
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def tidy(notes, run=0.035, gap=0.2, least=3):
    """The piano reduction made playable: a cluster of grace notes written at one instant becomes a quick run, lowest
    first (run seconds apart), and least or more short notes repeated on one pitch in one hand (a tremolo, gap seconds
    or less apart) merge into one held note. Returns [t, d, midi, vel, hand, trem] with trem True for a tremolo."""
    raw = sorted({(n[0], n[2], n[4]): list(n[:5]) for n in notes}.values())     # duplicates written twice go
    out, i = [], 0
    while i < len(raw):
        j = i
        while j < len(raw) and raw[j][0] == raw[i][0] and raw[j][1] <= 0.031 and raw[j][4] == raw[i][4]:
            j += 1
        if j - i > 1:
            grp = sorted({(n[2], n[4]): n for n in raw[i:j]}.values(), key=lambda n: n[2])
            out += [[n[0] + run * q, 0.06, n[2], n[3], n[4]] for q, n in enumerate(grp)]
            i = j
        else:
            out.append(list(raw[i][:5]))
            i += 1
    res, open_ = [], {}
    def close(k):
        t0, t1, v, c, parts = open_.pop(k)
        res.extend([[t0, t1 - t0, k[0], v, k[1], True]] if c >= least else [p + [False] for p in parts])
    for t, d, m, v, h in sorted(out):
        k = (m, h)
        if k in open_ and d < 0.25 and t - open_[k][1] <= gap:
            o = open_[k]
            o[1], o[2], o[3] = t + d, max(o[2], v), o[3] + 1
            o[4].append([t, d, m, v, h])
            continue
        if k in open_:
            close(k)
        if d < 0.25:
            open_[k] = [t, t + d, v, 1, [[t, d, m, v, h]]]
        else:
            res.append([t, d, m, v, h, False])
    for k in list(open_):
        close(k)
    return sorted(res)



def accents(notes, t0=0.0, t1=1e9, vmin=0, n=3, space=0.3):
    """Times in [t0, t1) where n or more notes at velocity vmin or more strike together, at least space seconds
    apart: the orchestra's hits, for flashes and percussion."""
    c = {}
    for e in notes:
        if t0 <= e[0] < t1 and e[3] >= vmin:
            c[round(e[0], 2)] = c.get(round(e[0], 2), 0) + 1
    out = []
    for k in sorted(k for k, v in c.items() if v >= n):
        if not out or k - out[-1] >= space:
            out.append(k)
    return out


# Sections of the orchestra: (sustained samples, short samples or None, bus, pan).
SECTIONS = {
    'violins': ('Strings/Violin Section/susVib/*.wav', 'Strings/Violin Section/Spic/*.wav', 'strings', 0.3),
    'violins trem': ('Strings/Violin Section/Trem/*.wav', None, 'strings', 0.3),
    'violas': ('Strings/Viola Section/susvib/*.wav', 'Strings/Viola Section/spic/*.wav', 'strings', -0.15),
    'cellos': ('Strings/Cello Section/susvib/*.wav', 'Strings/Cello Section/spic/*.wav', 'low', -0.25),
    'violas trem': ('Strings/Viola Section/trem/*.wav', None, 'strings', -0.15),
    'cellos trem': ('Strings/Cello Section/trem/*.wav', None, 'low', -0.25),
    'basses': ('Strings/Solo Contrabass/SusNV/*.wav', 'Strings/Solo Contrabass/Spic/*.wav', 'low', 0.2),
    'horns': ('Brass/F Horn/sus/*.wav', 'Brass/F Horn/stac/*.wav', 'brass', -0.3),
    'trumpets': ('Brass/Trumpet/sus/*.wav', 'Brass/Trumpet/stac/*.wav', 'brass', 0.25),
    'trombones': ('Brass/Tenor Trombone/sus/*.wav', 'Brass/Tenor Trombone/stac/*.wav', 'brass', 0.1),
    'tuba': ('Brass/Tuba/sus/*.wav', 'Brass/Tuba/stac/*.wav', 'low', 0.0),
    'flutes': ('Woodwinds/Flute/susvib/*.wav', 'Woodwinds/Flute/stac/*.wav', 'winds', -0.4),
    'piccolo': ('Woodwinds/Piccolo/Sus/*.wav', 'Woodwinds/Piccolo/Stac/*.wav', 'winds', -0.45),
    'oboes': ('Woodwinds/Oboe/Vib/*.wav', 'Woodwinds/Oboe/Stacc/*.wav', 'winds', 0.35),
    'clarinets': ('Woodwinds/Clarinet/susLong/*.wav', 'Woodwinds/Clarinet/stac/*.wav', 'winds', -0.2),
    'bassoons': ('Woodwinds/Bassoon/sus/*.wav', 'Woodwinds/Bassoon/stac/*.wav', 'winds', 0.2),
    'harp': (None, 'Strings/Harp/*.wav', 'harp', 0.4),
    'glock': (None, 'Percussion/Glock/*.wav', 'perc', 0.0),
}
HITS = {'timpani': 'Percussion/Timpani/Timpani1_Hit*.wav', 'timpani roll': 'Percussion/Timpani/Rolls/*.wav',
        'crash': 'Percussion/cymbal-crash1_f*.wav', 'gong': 'Percussion/gongHit_f*.wav',
        'bass drum': 'Percussion/BDrumNewhit_v[4-7]*.wav', 'anvil': 'Percussion/Anvil_Hit1_*.wav',
        'cymbal swell': 'Percussion/susCymb1-cresc-Median*.wav', 'metal': 'Miscellania Raw/Misc 1/metal_hit*.wav',
        'glass': 'Miscellania Raw/Misc 1/glass_break*.wav', 'hoof': 'Percussion/LogDrumLo_MedM_v[23]*.wav',
        'hoof soft': 'Percussion/Tumba-HitN_v[12]*.wav', 'scrape': 'Percussion/susCymb1-scrape*.wav',
        'gong scrape': 'Percussion/gongscrape_mf.wav', 'brake drum': 'Percussion/BrakeDrum1_Hammer_v[23]*.wav',
        'triangle': 'Percussion/Triangle3-Hit*.wav'}
BUSES = (('brass', 0.12, 0.28), ('low', 0.11, 0.2), ('strings', 0.09, 0.3), ('winds', 0.06, 0.3),
         ('harp', 0.07, 0.35), ('perc', 0.09, 0.25), ('fx', 0.2, 0.3))


class Orchestra:
    """Wagner's notes on the VSCO2 orchestra. play() sounds one note on a section (sustained notes longer than a
    second are held by overlapping windows of the sample, short ones use the section's staccato or spiccato);
    tutti() orchestrates a whole excerpt from the piano reduction by hand and register, fuller as size() grows:
    the right hand on violins (violas under its long notes, flutes and piccolo on top), the left hand's tune from
    F#3 up on horns (trombones, then trumpets an octave up as the orchestra grows) or, when it moves fast, on violas
    and cellos, and the bass on cellos and basses (tuba under its long notes); tremolos from tidy() go to the strings' tremolo.
    Pass role() to recolour any note.
    level scales every bus, for the loudness target."""

    def __init__(self, M, level=1.0):
        self.M = M
        for name, gain, rev in BUSES:
            M.bus(name, gain=gain * level, reverb=rev)
        self.sus, self.short = {}, {}
        for name, (sus, short, _, _) in SECTIONS.items():
            if sus:
                self.sus[name] = M.sampler(sus, tune=-12)
            if short:
                self.short[name] = M.sampler(short, tune=0 if name in ('harp', 'glock') else -12)
        self.hits = {name: M.hits(p) for name, p in HITS.items()}

    def hold(self, bus, s, m, t0, t1, vel, pan=0.0, gain=1.0, step=2.5, rise=0.08, fall=0.6):
        """A note sustained from t0 to t1: overlapping windows of its sample."""
        from pixelhome.audio import SR
        a0 = s.play(m, vel)
        step = min(step, (a0.shape[1] / SR - 0.35) / 2)
        w = int(2 * step * SR)
        win = np.hanning(w)
        t = t0 - step
        while t < t1 + fall:
            a = s.play(m, vel)[:, int(0.25 * SR):int(0.25 * SR) + w]
            a = a * win[:a.shape[1]]
            tt = t + np.arange(a.shape[1]) / SR
            e = np.clip((tt - t0) / rise, 0, 1) * np.clip(1 - (tt - t1) / fall, 0, 1)
            self.M.add(bus, a * e, t, gain, pan)
            t += step

    def play(self, section, m, t, d, v, pan=None, gain=1.0):
        """One note on a section: midi m at t for d seconds, velocity v (1..127)."""
        sus, short, bus, p = SECTIONS[section]
        pan = p if pan is None else pan
        v = int(np.clip(v, 1, 127))
        if section in self.sus and (d >= 0.25 or section not in self.short):
            s = self.sus[section]
            if d > 1.2:
                self.hold(bus, s, m, t, t + d, v, pan, gain)
            else:
                self.M.add(bus, s.play(m, v, dur=d, release=0.15), t, gain, pan)
        else:
            self.M.add(bus, self.short[section].play(m, v), t, gain, pan)

    def hit(self, name, t, v=100, pitch=0.0, gain=0.5, pan=0.0, fx=False):
        """A percussion hit; fx=True makes it a stage effect (footsteps, blows), on the effects bus and its fader."""
        if fx:
            self.M.add('fx', self.hits[name].play(v, pitch=pitch), t, gain * 0.45, pan)    # same level as on perc
        else:
            self.M.add('perc', self.hits[name].play(v, pitch=pitch), t, gain, pan)

    # Stage effects: what a production adds so the house's lights have a sound. pan may be a number or pan(t).

    def effects(self, points):
        """Ride the effects' level through the scene, as a sound designer would: [(t, dB), ...]. Let them lead where the
        staging needs them (the storm, a sword stroke) and back them off where the music must be clear (a theme, a
        sung line, a tender moment)."""
        self.M.fader('fx', points)

    def _noise(self, seconds, lo, hi, seed, n=None):
        """Band-limited noise, lo..hi Hz, unit peak (n samples, or seconds' worth)."""
        from pixelhome.audio import SR
        n = n or max(1, int(seconds * SR))
        f = np.fft.rfftfreq(n, 1 / SR)
        spec = np.fft.rfft(np.random.default_rng(seed).normal(0, 1, n))
        spec *= (f >= lo) & (f <= hi)
        x = np.fft.irfft(spec, n)
        return x / (np.abs(x).max() + 1e-9)

    def _wobble(self, n, rate, seed, depth=0.7):
        """A slow random swell, 1 - depth .. 1, rate wobbles a second, for n samples."""
        from pixelhome.audio import SR
        k = max(2, int(n / SR * rate) + 2)
        pts = np.random.default_rng(seed).uniform(1 - depth, 1, k)
        return np.interp(np.linspace(0, k - 1, n), np.arange(k), pts)

    def _sfx(self, sig, t, gain, pan):
        if callable(pan):
            pan = pan(t)
        self.M.add('fx', np.vstack([sig, sig]), t, gain, float(np.clip(pan, -1, 1)))

    def thunder(self, t, near=1.0, pan=0.0, gain=1.0, seed=0):
        """Lightning's thunder: near (1) a sharp crack at once, a boom and a long roll; far (0) a late, soft rumble."""
        from pixelhome.audio import SR
        seed = seed or int(t * 1000)
        if near > 0.4:
            n = int(0.35 * SR)
            crack = self._noise(0, 400, 7000, seed, n=n) * np.exp(-np.arange(n) / (0.05 * SR))
            self._sfx(crack, t, 0.9 * near * gain, pan)
            self.hit('crash', t, int(80 + 40 * near), gain=0.35 * near * gain, pan=pan(t) if callable(pan) else pan, fx=True)
            self.hit('bass drum', t + 0.02, 124, gain=0.8 * near * gain, fx=True)
        lag = 0.15 + 1.4 * (1 - near)
        dur = 2.5 + 3.0 * near
        n = int(dur * SR)
        tt = np.arange(n) / SR
        env = np.clip(tt / (0.08 + 0.5 * (1 - near)), 0, 1) * np.exp(-tt / (0.35 * dur))
        roll = self._noise(0, 25, 140 + 160 * near, seed + 1, n=n) * env * self._wobble(n, 7, seed + 2)
        self._sfx(roll, t + lag, (0.7 + 0.8 * near) * gain, pan)
        self.hit('timpani roll', t + lag, int(70 + 50 * near), pitch=-5, gain=0.5 * gain, fx=True)
        self.hit('timpani', t + lag, int(80 + 40 * near), pitch=-7, gain=0.5 * near * gain, fx=True)

    def gallop(self, t0, t1, beat=0.42, pan=0.0, v=96, gain=1.0):
        """Hoofbeats from t0 to t1: a galloping three-beat (da-da-DUM) every beat seconds."""
        t = t0
        while t < t1:
            for k, (dt, dv, name) in enumerate(((0.0, -18, 'hoof soft'), (0.11, -10, 'hoof soft'), (0.22, 0, 'hoof'))):
                if t + dt < t1:
                    self.M.add('fx', self.hits[name].play(int(np.clip(v + dv, 1, 127))), t + dt, 0.27 * gain,
                               float(np.clip(pan(t + dt) if callable(pan) else pan, -1, 1)))
            t += beat

    def hoof(self, t, pan=0.0, v=100, gain=1.0):
        """One hoof landing (a leap, a stamp)."""
        pp = pan(t) if callable(pan) else pan
        self.M.add('fx', self.hits['hoof'].play(int(np.clip(v, 1, 127))), t, 0.27 * gain, float(np.clip(pp, -1, 1)))

    def clash(self, t, pan=0.0, v=118, gain=1.0):
        """Steel on steel: a sword striking, a spear meeting a sword."""
        pp = pan(t) if callable(pan) else pan
        self.hit('metal', t, v, gain=0.6 * gain, pan=pp, fx=True)
        self.hit('anvil', t, v, gain=0.45 * gain, pan=pp, fx=True)
        self.hit('brake drum', t + 0.01, v - 10, gain=0.3 * gain, pan=pp, fx=True)

    def shatter(self, t, pan=0.0, gain=1.0):
        """Something breaking apart: a sword in pieces, a spell broken."""
        pp = pan(t) if callable(pan) else pan
        self.clash(t, pp, 124, gain)
        self.hit('glass', t + 0.03, 110, gain=0.5 * gain, pan=pp, fx=True)
        self.hit('crash', t, 120, gain=0.5 * gain, pan=pp, fx=True)

    def boom(self, t, pan=0.0, gain=1.0):
        """A great blow: a spear struck on rock, a door flung open, a body falling, a god arriving."""
        pp = pan(t) if callable(pan) else pan
        self.hit('bass drum', t, 126, gain=0.9 * gain, pan=pp, fx=True)
        self.hit('timpani', t, 124, pitch=-6, gain=0.7 * gain, pan=pp, fx=True)
        self.hit('gong', t + 0.02, 110, gain=0.4 * gain, pan=pp, fx=True)

    def fire(self, t0, t1, level=1.0, pan=0.0, crackle=12.0, seed=5):
        """Fire from t0 to t1: a roar (level 0..1, or level(t)) with crackles, crackle a second at full level."""
        from pixelhome.audio import SR
        dur = t1 - t0
        n = int(dur * SR)
        tt = t0 + np.arange(n) / SR
        lv = level(tt) if callable(level) else np.full(n, float(level))
        fade = np.clip((tt - t0) / 0.8, 0, 1) * np.clip((t1 - tt) / 1.2, 0, 1)
        roar = self._noise(0, 60, 900, seed, n=n) * self._wobble(n, 3, seed + 1, 0.5) * lv * fade
        self._sfx(roar, t0, 0.9, pan)
        rng = np.random.default_rng(seed + 2)
        k = int(dur * crackle)
        for tc in np.sort(rng.uniform(t0, t1, k)):
            a = float(np.interp(tc, tt, lv * fade))
            if a > 0.05 and rng.random() < a:
                m = int(rng.uniform(0.004, 0.02) * SR)
                c = self._noise(0, 1500, 9000, int(tc * 1e4), n=m) * np.exp(-np.arange(m) / (0.003 * SR))
                self._sfx(c, tc, 0.35 * a * rng.uniform(0.4, 1.0), (pan(tc) if callable(pan) else pan) +
                          rng.uniform(-0.3, 0.3))

    def wind(self, t0, t1, level=1.0, pan=0.0, seed=9):
        """Storm wind from t0 to t1, gusting; level 0..1 or level(t)."""
        from pixelhome.audio import SR
        dur = t1 - t0
        n = int(dur * SR)
        tt = t0 + np.arange(n) / SR
        lv = level(tt) if callable(level) else np.full(n, float(level))
        fade = np.clip((tt - t0) / 1.5, 0, 1) * np.clip((t1 - tt) / 1.5, 0, 1)
        w = self._noise(0, 150, 1400, seed, n=n) * self._wobble(n, 0.8, seed + 1, 0.8) * lv * fade
        self._sfx(w, t0, 0.6, pan)

    def tutti(self, notes, size=lambda t: 1.0, role=None, pan=None):
        """Orchestrate excerpt notes [t, d, midi, vel, hand]. size(t) 0..1 is how full the orchestra is; role(t, d, m,
        v, hand) may return a list of (section, transpose, velocity change, gain) to play instead (an empty list is
        silence) or None for the default; pan(t, m) moves the notes across the house."""
        F3, E2, F5, B5 = 54, 40, 77, 83
        for n in notes:
            t, d, m, v, hand = n[:5]
            parts = role(t, d, m, v, hand) if role else None
            if parts is None and len(n) > 5 and n[5]:     # a tremolo from tidy()
                s = size(t)
                parts = [('violins trem' if m >= 55 else 'violas trem' if m >= 48 else 'cellos trem', 0, -4, 0.6)]
                if hand == 1 and m < 48 and s >= 0.5:
                    parts.append(('basses', -12 if m >= E2 else 0, -8, 0.4))
            if parts is None:
                s = size(t)
                if hand == 0:
                    parts = [('violins' if m >= 55 else 'violas', 0, -6, 0.55)]
                    if d >= 0.4 and s >= 0.5:
                        parts.append(('violas', -12, -14, 0.3))
                    if m >= F5 and s >= 0.3:
                        parts.append(('piccolo' if m >= B5 and s >= 0.6 else 'flutes', 0, -14, 0.4))
                elif m >= F3:
                    if d < 0.3:
                        parts = [('violas' if m >= 60 else 'cellos', 0, -6, 0.5)]
                    else:
                        parts = [('horns', 0, 0, 0.8)]
                        if s >= 0.5:
                            parts.append(('trombones', 0, -6, 0.55))
                        if s >= 0.8:
                            parts.append(('trumpets', 12, -16, 0.35))
                else:
                    parts = [('cellos', 0, 0, 0.7), ('basses', -12 if m >= E2 else 0, -6, 0.55)]
                    if d > 0.5 and s >= 0.6:
                        parts.append(('tuba', 0, -10, 0.45))
            for section, tr, dv, g in parts:
                self.play(section, m + tr, t, d, v + dv, pan(t, m) if pan else None, g)
