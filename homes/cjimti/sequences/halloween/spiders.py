"""Spiders: The roof glows like a lit window; spiders are silhouettes that scurry, pause, leave silk.
Then something much bigger walks across the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, Flicker, nframes

CODE = 'SC4'
TITLE = 'Spiders'
KIND = 'show'
DESCRIPTION = 'Silhouette spiders scurry, pause and leave silk across a glowing roof. Then something much bigger walks across.'

ORANGE = hexc('#ff3000')
RED = hexc('#ff0000')


class _Spider:
    def __init__(self, rng, pos, size, born, speed=(25, 60)):
        self.rng, self.p, self.size, self.born = rng, float(pos), size, born
        self.target, self.wait, self.speed = self.p, rng.uniform(0.3, 1.2), speed
        self.v, self.dir, self.phase, self.flee = 0.0, 1, 0.0, None

    def step(self, n):
        if self.flee is not None:
            target, v = self.flee, 90.0
        else:
            if self.wait > 0:
                self.wait -= DT
                return
            if abs(self.target - self.p) < 0.5:
                self.wait = self.rng.uniform(0.4, 2.5)
                self.target = float(np.clip(self.p + self.rng.uniform(-90, 90), 3, n - 4))
                self.v = self.rng.uniform(*self.speed)
                return
            target, v = self.target, self.v
        delta = target - self.p
        step = np.sign(delta) * min(abs(delta), v * DT)
        self.dir = 1 if step >= 0 else -1
        self.p += step
        self.phase += abs(step) / (1.5 * self.size)

    def draw(self, idx, dark, eyes):
        s = self.size
        d = idx - self.p
        dark[:] = np.maximum(dark, np.clip(1.5 - np.abs(d) / s, 0, 1))
        alt = int(self.phase) % 2
        for k in range(1, 5):
            if (k + alt) % 2 == 0:
                for sgn in (-1, 1):
                    dark[:] = np.maximum(dark, 0.85 * np.clip(1 - np.abs(d - sgn * (s + k * s)) / max(1, s * 0.6), 0, 1))
        e = self.p + self.dir * (s + 0.2)
        eyes[:] = np.maximum(eyes, np.clip(1 - np.abs(idx - e) / max(0.8, s * 0.3), 0, 1))


def render(G, seed=4):
    rng = np.random.default_rng(seed)
    D = 61.0
    n = G.N
    out = np.zeros((nframes(D), n, 3))
    idx = np.arange(n, dtype=float)
    cand = Flicker(rng, n, 0.5, 3)
    silk = np.zeros(n)
    pf0 = G.pi[G.seg['Porch Front'][0]]
    crew = [_Spider(rng, pf0, 1.0, 3.0)]
    for b in (14, 17, 20, 23):
        crew.append(_Spider(rng, rng.uniform(20, n - 20), 1.0, b))
    giant = _Spider(rng, -40, 6.0, 45.0)
    giant.flee = n + 60

    for f in range(len(out)):
        t = f * DT
        bgI = keys(t, [(0, 0), (3, 0.42), (53, 0.42), (57, 0)])
        bg = light(ORANGE, bgI * (1 + 0.08 * cand(t)))
        dark = np.zeros(n)
        eyes = np.zeros(n)
        for sp in crew:
            if t < sp.born:
                continue
            if t > 35 and sp.flee is None:
                sp.flee = -20.0 if sp.p < n / 2 else n + 20.0
            sp.step(n)
            k = int(round(sp.p))
            if 0 <= k < n:
                silk[k] = max(silk[k], 1.0)
            grow = smoothstep(sp.born, sp.born + 0.5, t)
            dk, ey = np.zeros(n), np.zeros(n)
            sp.draw(idx, dk, ey)
            dark = np.maximum(dark, dk * grow)
            eyes = np.maximum(eyes, ey * grow * 0.5)
        if t >= giant.born and giant.p < n + 50:
            giant.target = n + 60
            giant.p += 52 * DT * (0.6 + 0.4 * abs(np.sin(np.pi * t * 0.9)))
            giant.phase = t * 1.8
            if 0 <= giant.p < n:
                silk[max(0, int(giant.p) - 3):int(giant.p) + 3] = 1.0
            giant.draw(idx, dark, eyes)
        silk *= 0.997
        buf = (bg + light(hexc('#d0d8ff'), 0.2 * silk)) * (1 - dark)[:, None]
        buf += light(RED, eyes * keys(t, [(0, 0.5), (55, 0.5), (55.5, 1.0)]))
        if t > 53:                                          # only the giant's eyes remain, blinking twice
            ge = np.zeros(n)
            gpos = min(giant.p, n - 3)
            for o in (-1.5, 1.5):
                ge = np.maximum(ge, np.clip(1 - np.abs(idx - (gpos + o)), 0, 1))
            blink = 0 if any(abs(t - b) < 0.1 for b in (57.5, 58.4)) else 1
            buf = buf * (1 - smoothstep(53, 55, t)) + light(RED, ge * blink * keys(t, [(53, 0), (54, 1), (60, 1), (60.5, 0)]))
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A spider scherzo in E Phrygian at 108 BPM, the giant's stride (it changes legs every 1/1.8 s and lunges every two
# steps). Every sound below is a moment in render(), found by replaying its spiders with the same seed: each spider's
# legs tick on spiccato strings whose pitch follows where it is on the roofline (climbing to the right, a semitone
# trill between leg pairs); a silk shimmer swells with the silk on the roof; the bass, the bassoon tune and the harp
# stop dead whenever every spider freezes, and high tremolo holds the breath until one moves. They all bolt at 35 s,
# the roof sits empty, and then the big one walks across in timpani, bass drum and low brass. Panned to where it
# happens on the house as seen from the street. VSCO2 names most strings, winds and brass an octave low
# (A3 sounds A4), so those samplers take tune=-12 to sound the written note.

BPM_BEAT = 1 / 1.8                          # the giant's step, used as the beat for everything
PHRYG = [0, 1, 3, 5, 7, 8, 10]              # E Phrygian: E F G A B C D


def _replay(G, seed=4):
    """Re-run render()'s spiders without drawing: positions, leg phase and silk per frame, giant position."""
    rng = np.random.default_rng(seed)
    D = 61.0
    n = G.N
    Flicker(rng, n, 0.5, 3)
    pf0 = G.pi[G.seg['Porch Front'][0]]
    crew = [_Spider(rng, pf0, 1.0, 3.0)]
    for b in (14, 17, 20, 23):
        crew.append(_Spider(rng, rng.uniform(20, n - 20), 1.0, b))
    _Spider(rng, -40, 6.0, 45.0)                # the giant's constructor draws from rng too
    F = nframes(D)
    pos, ph = np.full((F, len(crew)), np.nan), np.zeros((F, len(crew)))
    silk_sum, gpos = np.zeros(F), np.full(F, -40.0)
    silk = np.zeros(n)
    gp = -40.0
    for f in range(F):
        t = f * DT
        for i, sp in enumerate(crew):
            if t < sp.born:
                continue
            if t > 35 and sp.flee is None:
                sp.flee = -20.0 if sp.p < n / 2 else n + 20.0
            sp.step(n)
            k = int(round(sp.p))
            if 0 <= k < n:
                silk[k] = max(silk[k], 1.0)
            pos[f, i], ph[f, i] = sp.p, sp.phase
        if t >= 45.0 and gp < n + 50:
            gp += 52 * DT * (0.6 + 0.4 * abs(np.sin(np.pi * t * 0.9)))
            if 0 <= gp < n:
                silk[max(0, int(gp) - 3):int(gp) + 3] = 1.0
        gpos[f] = gp
        silk *= 0.997
        silk_sum[f] = silk.sum()
    return pos, ph, silk_sum, gpos, [sp.born for sp in crew]


def score(M, G):
    from pixelhome.audio import note, whoosh, SR
    n = note
    N = G.N
    pos, ph, silk_sum, gpos, born = _replay(G)
    F = len(pos)
    T = np.arange(F) * DT
    B = BPM_BEAT

    vln = M.sampler('Strings/Solo Violin/spic/*.wav', tune=-12)
    vlns = M.sampler('Strings/Violin Section/Spic/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/spic/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    vpz = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    cbp = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    cbt = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    vcz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav')
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f*_[12].wav')
    bdl = M.hits('VSCO 1 Percussion/drums/bass/bdrum_p*_[12].wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v3*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll_v5*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_mf*.wav')
    gongp = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_pp*.wav')
    gliss = M.hits('Miscellania Raw/Misc 2/glock_glisses/glock_fx_down_chromatic_fast*.wav')

    for name, gain, rev in (('skitter', 0.22, 0.15), ('bass', 0.6, 0.08), ('tune', 0.2, 0.2), ('harp', 0.3, 0.3),
                            ('silk', 0.3, 0.5), ('hush', 0.3, 0.35), ('drums', 0.6, 0.2), ('brass', 0.5, 0.25),
                            ('glint', 0.45, 0.45), ('fx', 0.15, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()

    def pan_at(p):                          # path index (may be off the house) -> left/right as seen from the street
        x = np.interp(p, np.arange(N), xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def pitch_at(p, base):                  # roofline position -> a note of E Phrygian, ~1.8 octaves over the house
        st = int(np.clip(p, 0, N - 1) // 40)
        return base + 12 * (st // 7) + PHRYG[st % 7]

    # ---- moves, pauses, exits and freezes, from the replay ----
    moving = np.zeros(pos.shape, bool)
    moving[1:] = np.abs(np.diff(np.nan_to_num(pos, nan=-999.0), axis=0)) > 1e-9
    on = ~np.isnan(pos) & (pos > -1) & (pos < N)
    act = on & (T[:, None] < 35)
    frz = (act.sum(1) >= 2) & ((moving & act).sum(1) == 0)
    frz |= (act.sum(1) == 1) & (T > 3.5) & ((moving & act).sum(1) == 0)
    edges = np.diff(np.r_[0, frz.astype(int), 0])
    freezes = [(T[a], T[b - 1] + DT) for a, b in zip(np.nonzero(edges == 1)[0], np.nonzero(edges == -1)[0])
               if T[b - 1] - T[a] >= 0.4]

    def frozen(t):
        return any(a <= t < b for a, b in freezes)

    # ---- 0-3 s: the roof glows up like a lit window ----
    M.add('hush', cbs.play(n('E1'), 70, dur=4.5, release=1.5), 0.0, 0.8)
    M.add('hush', M.synth('Pads/Ghost Pad').render([(0.0, n('E3'), 60, 13.5), (0.0, n('B3'), 52, 13.5),
                                                    (37.9, n('E3'), 64, 7.0), (37.9, n('B3'), 56, 7.0),
                                                    (40.0, n('F4'), 48, 4.9)], 61.0), 0.0, 0.8)
    for i, m in enumerate(('E2', 'B2', 'E3', 'F3', 'B3', 'E4')):     # a harp rises with the light
        M.add('harp', harp.play(n(m), 60 + 6 * i), 0.4 * i + 0.6, 0.8, -0.2 + 0.08 * i)

    # ---- the spiders: legs on spiccato, pitch by position, one voice each ----
    voices = [(vln, n('E5'), 1.0), (vla, n('E4'), 0.9), (vlns, n('B4'), 0.8), (vc, n('E3'), 1.0),
              (vpz, n('E5'), 0.9)]
    births = []
    for i, (inst, base, g) in enumerate(voices):
        tb = born[i]
        p0 = pos[int(round(tb / DT)), i]
        births.append((tb, p0))
        M.add('skitter', vpz.play(pitch_at(p0, n('E5')) + 12, 90), tb, 0.9, pan_at(p0))   # plink: it arrives
        M.add('glint', glock.play(pitch_at(p0, n('E6')), 70), tb + 0.05, 0.7, pan_at(p0))
        legs = np.floor(ph[:, i]).astype(int)
        fast = T > 35
        step = np.where(fast, 3, 2)
        tick = np.nonzero(np.diff(legs // step, prepend=legs[0] // step[0]) != 0)[0]
        prev = -10.0
        for f in tick:
            t, p = T[f], pos[f, i]
            if not (-1 < p < N + 1):
                continue
            fresh = t - prev > 0.3              # first step of a run lands harder
            prev = t
            m = pitch_at(p, base) + (legs[f] // step[f]) % 2
            v = (86 if fresh else 58 + int(M.rng.integers(0, 10))) + (14 if fast[f] else 0)
            M.add('skitter', inst.play(m, v, dur=0.12, release=0.05), t, g, pan_at(p))
        # a silk thread glints where it stops
        stops = np.nonzero(moving[:-1, i] & ~moving[1:, i] & on[1:, i] & (T[1:] < 35))[0] + 1
        for f in stops:
            M.add('glint', glock.play(pitch_at(pos[f, i], n('E6')) + 7, 52), T[f], 0.6, pan_at(pos[f, i]))
        # leaving the house: a pizz flick at the end it went off
        out = np.nonzero(~np.isnan(pos[:, i]) & ((pos[:, i] <= -1) | (pos[:, i] >= N)))[0]
        if len(out):
            te, pe = T[out[0]], pos[out[0], i]
            M.add('skitter', vpz.play(n('E6') if pe > 0 else n('F6'), 100), te, 1.0, pan_at(pe))
            M.add('fx', whoosh(0.35, 2500, 600, 0.3, seed=60 + i), te - 0.2, 0.8, pan_at(pe))

    # ---- breath-holding: high tremolo while every spider on the roof is frozen ----
    for k, (a, b) in enumerate(freezes):
        d = b - a
        for m in (('E5', 'F5') if k % 2 == 0 else ('F5', 'B5')):
            M.add('hush', trem.play(n(m), 55, dur=d, release=0.25), a + 0.05, 0.6, 0.1 * (-1) ** k)

    # ---- 3-14: the first one alone; a slow heartbeat in the bass ----
    for k in range(6, 26, 2):
        t = k * B
        if not frozen(t):
            M.add('bass', cbp.play(n('E1') if k % 4 == 2 else n('B1'), 80), t, 0.6)

    # ---- 14.4-35: the crew; Phrygian ostinato and a creeping bassoon tune, both stop whenever everyone freezes ----
    T0 = 26 * B                                          # 14.44 s, bar 0
    bars = ['Em', 'F', 'Em', 'B7']
    BASS = {'Em': [(0, 'E2'), (1, 'B1'), (1.5, 'E2'), (2, 'F2'), (3, 'E2')],
            'F': [(0, 'F2'), (1, 'C2'), (1.5, 'F2'), (2, 'E2'), (3, 'F2')],
            'B7': [(0, 'B1'), (1, 'C2'), (2, 'D#2'), (3, 'F#2')]}
    UP = {'Em': ('E3', 'G3', 'B3'), 'F': ('F3', 'A3', 'C4'), 'B7': ('D#3', 'A3', 'B3')}
    for bar in range(9):
        c = bars[bar % 4]
        for b, m in BASS[c]:
            t = T0 + (4 * bar + b) * B
            if not frozen(t):
                M.add('bass', cbp.play(n(m), 92 + 8 * (b == 0)), t, 0.55)
                if bar >= 4 and n(m) - 12 >= n('E1'):    # second half: the low string doubles it
                    M.add('bass', cbp.play(n(m) - 12, 84), t, 0.4)
        for b in (1, 3):
            t = T0 + (4 * bar + b) * B
            if not frozen(t):
                for m in UP[c]:
                    M.add('bass', vcz.play(n(m), 70), t, 0.3, -0.3)
    TUNE_A = [(0, 'E3'), (0.5, 'F3'), (1, 'G3'), (1.5, 'F3'), (2, 'E3'), (3, 'B2'), (3.5, 'C3'),
              (4, 'F3'), (4.5, 'G3'), (5, 'A3'), (5.5, 'G3'), (6, 'F3'), (7, 'C3'), (7.5, 'E3')]
    TUNE_B = [(0, 'E3'), (0.5, 'G3'), (1, 'B3'), (1.5, 'C4'), (2, 'B3'), (3, 'G3'),
              (4, 'D#3'), (4.5, 'F#3'), (5, 'A3'), (6, 'B3'), (6.5, 'A3'), (7, 'D#3'), (7.5, 'F#3')]
    LICK = [(0, 'E4'), (0.5, 'F4'), (1, 'G4'), (1.5, 'A4'), (2, 'B4'), (2.5, 'C5'), (3, 'B4'), (3.5, 'F4')]
    for start, phrase, inst, sh, v in ((2, TUNE_A, bsn, 0, 96), (4, TUNE_B, bsn, 0, 100), (6, TUNE_A, bsn, 0, 104),
                                      (6, TUNE_A, clar, 12, 92), (8, LICK, clar, 0, 100), (8, LICK, bsn, -12, 100)):
        for b, m in phrase:
            t = T0 + (4 * start + b) * B
            if not frozen(t):
                M.add('tune', inst.play(n(m) + sh, v, dur=0.22, release=0.06), t, 1.0, 0.15)
    for bar in range(6, 9):                              # harp spins its web: arpeggios from bar 6
        c = bars[bar % 4]
        arp = [n(m) + 12 for m in UP[c]] + [n(UP[c][0]) + 24]
        for e in range(8):
            t = T0 + (4 * bar + e / 2) * B
            if not frozen(t):
                M.add('harp', harp.play(arp[e % 4] + 12 * (e >= 4), 72), t, 0.7, 0.4 - 0.1 * (e % 4))
    TF = 63 * B                                          # 35.0 s: everyone bolts
    M.add('hush', trem.play(n('E5'), 80, dur=0.6, release=0.1), TF - B, 0.8)
    M.add('hush', trem.play(n('F5'), 80, dur=0.6, release=0.1), TF - B, 0.8)
    M.add('drums', troll.play(70, dur=0.6), TF - B, 0.5)

    # ---- 35: the stampede ----
    M.add('drums', timp.play(118), TF, 1.0)
    M.add('drums', bd.play(110), TF, 0.7)
    for m in ('E3', 'F3', 'B3', 'E4'):
        M.add('brass', horn.play(n(m), 116, dur=0.25, release=0.1), TF, 0.7)
        M.add('skitter', vlns.play(n(m) + 12, 120, dur=0.2), TF, 0.6)
    M.add('glint', gliss.play(100), TF + 0.05, 1.0, -0.4)
    M.add('glint', gliss.play(100), TF + 0.3, 1.0, 0.4)
    M.add('bass', cbp.play(n('E1'), 120), TF)
    for m in ('E5', 'F5', 'B5', 'E6'):                  # the whole string section shrieks while they run
        M.add('hush', trem.play(n(m), 110, dur=2.9, release=0.4), TF, 0.7)
    M.add('drums', troll.play(100, dur=2.9), TF, 0.6)
    for e, m in enumerate(('E3', 'D3', 'C3', 'B2', 'A2', 'G2', 'F2', 'E2')):   # the bass runs off with them
        M.add('bass', cbp.play(n(m), 100 - 4 * e), TF + (e + 1) * B / 2, 0.8)

    # ---- 38-45: the roof is empty; silk fades; something is coming ----
    M.add('hush', cbt.play(n('E1'), 60, dur=4.2, release=0.3), 40.8, 1.0, -0.6)
    M.add('drums', troll.play(60, dur=2.0), 43.0, 0.6, -0.75)
    for k in range(70, 81, 2):                           # heartbeat, lub-dub, growing
        t = k * B
        M.add('bass', cbp.play(n('E1'), 60 + 4 * (k - 70)), t, 0.5)
        M.add('bass', cbp.play(n('E1'), 45 + 4 * (k - 70)), t + B / 2, 0.4)

    # ---- silk shimmer, following how much silk is on the roof ----
    shim = M.synth('Pads/Bells and Sweep').render([(2.5, n('E5'), 70, 57.0), (2.5, n('B5'), 64, 57.0),
                                                   (2.5, n('F6'), 50, 57.0)], 61.0)
    lv = silk_sum / max(silk_sum.max(), 1e-9)
    ts = np.arange(shim.shape[1]) / SR
    env = np.interp(ts, T, np.sqrt(lv))
    env *= np.interp(ts, [0, 53, 55.5, 61], [1, 1, 0, 0])       # the roof fades out from 53
    M.add('silk', shim * env, 0.0)

    # ---- 45-57: the giant; a step every 1/1.8 s, a lunge on every other one ----
    TG = 81 * B                                          # 45.0
    k_end = int(np.ceil(T[np.argmax(gpos >= N - 3)] / B))  # its eyes reach the right end at 57.1 and stop
    for k in range(81, k_end):
        t = k * B
        p = float(gpos[min(F - 1, int(round(t / DT)))])
        lunge = (k - 81) % 2 == 0
        far = np.interp(t, [45.0, 46.0, 53.0, 55.0, 57.1], [0.45, 1.0, 1.0, 0.5, 0.3])
        v = (124 if lunge else 104) * far
        pp = pan_at(np.clip(p, -40, N + 40))
        M.add('drums', bd.play(int(v)), t, 1.0, pp)
        M.add('drums', timp.play(int(v), pitch=-7 if lunge else -6), t, 0.9, pp)
        M.add('bass', cbp.play(n('E1') if lunge else n('F1'), int(min(127, v + 6))), t, 1.0, pp)
        if lunge and 46 < t < 53:
            M.add('drums', gongp.play(90), t, 0.35, pp)
    M.add('hush', cbt.play(n('E1'), 90, dur=8.2, release=1.0), TG, 1.0)
    M.add('drums', gong.play(110), 45.9, 0.8, pan_at(0))   # it steps onto the house
    # the giant's theme: low brass, one chord per lunge
    GIANT = [('E', ('E1', 'B1', 'E2', 'G3')), ('F', ('F1', 'C2', 'F2', 'A3')), ('E', ('E1', 'B1', 'E2', 'B3')),
             ('F', ('F1', 'C2', 'F2', 'C4')), ('G', ('G1', 'D2', 'G2', 'B3')), ('F', ('F1', 'C2', 'F2', 'A3')),
             ('Bb', ('A#1', 'F2', 'A#2', 'D4')), ('B7', ('B1', 'F#2', 'A2', 'D#4'))]
    for i, (_, chord) in enumerate(GIANT):
        t = TG + 2 * i * B
        v = 80 + 5 * i
        M.add('brass', tuba.play(n(chord[0]) + 12, v, dur=2 * B, release=0.15), t, 1.0)
        M.add('brass', tbn.play(n(chord[1]) + 12, v, dur=2 * B, release=0.15), t, 0.8)
        M.add('brass', tbn.play(n(chord[2]) + 12, v - 6, dur=2 * B, release=0.15), t, 0.6)
        M.add('brass', horn.play(n(chord[3]), v + 10, dur=2 * B, release=0.15), t, 0.7, 0.1)
    t = TG + 16 * B                                      # 53.9: lights gone, the last chord hangs
    for m, inst, g in (('E2', tuba, 1.0), ('B2', tbn, 0.7), ('E3', tbn, 0.6)):
        M.add('brass', inst.play(n(m), 62, dur=1.6, release=1.2), t, 0.6 * g)

    # ---- 55: only its eyes, and they flare ----
    M.add('hush', trem.play(n('E5'), 96, dur=2.0, release=0.8), 55.0, 0.9, pan_at(gpos[int(55 / DT)]))
    M.add('hush', trem.play(n('F5'), 96, dur=2.0, release=0.8), 55.0, 0.9, pan_at(gpos[int(55 / DT)]))
    for m in ('E3', 'F3', 'B3'):
        M.add('brass', horn.play(n(m), 122, dur=0.35, release=0.2), 55.0, 0.8, pan_at(gpos[int(55 / DT)]))
    M.add('drums', gong.play(120), 55.0, 0.9, pan_at(gpos[int(55 / DT)]))

    # ---- 57.5, 58.4: it blinks twice; 60: the eyes go out ----
    pe = pan_at(N - 3)
    for tb, m in ((57.5, 'E6'), (58.4, 'F6')):
        M.add('skitter', vpz.play(n(m), 84), tb - 0.1, 0.8, pe)
        M.add('glint', glock.play(n(m) + 12, 60), tb, 0.6, pe)
    M.add('bass', cbp.play(n('E1'), 110), 60.0, 1.0, pe)
    M.add('drums', bdl.play(90), 60.0, 0.8, pe)
    M.add('drums', gongp.play(80), 60.05, 0.6, pe)
    M.add('harp', harp.play(n('E2'), 70), 60.0, 0.8, pe)
