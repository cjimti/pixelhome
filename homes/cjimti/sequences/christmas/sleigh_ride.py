"""Sleigh Ride: Santa's team flies a 3-D spline around and over the house: a lead reindeer with a red lamp,
four pairs of reindeer and the sleigh follow the same track at fixed arc-length offsets, shedding a
glitter trail that falls under gravity. The team lands on the porch roof (hoofbeats), Santa goes down
the chimney and presents appear on the wings, then the team gallops off, banks along the street side
and climbs away into the night."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, lerp, nframes

CODE = 'CH01'
TITLE = 'Sleigh Ride'
KIND = 'show'
DESCRIPTION = ('A red lamp leads Santa\'s team on a flight around and over the house, lands on the porch roof '
               'with a clatter of hooves, leaves presents on both wings and takes off over the street.')
VOICEOVER = "Bundle up and watch the sky: Santa's sleigh is coming in to land on our roof."

NIGHT = hexc('#0a1440')
STAR = hexc('#c8d8ff')
NOSE = hexc('#ff1000')
DEER = hexc('#ffa050')
SLEIGH = hexc('#ff2008')
GOLD = hexc('#ffb030')
GLINT = hexc('#fff0c0')
HOOF = hexc('#fff4e0')
GIFTS = [hexc(c) for c in ('#ff1a10', '#10c040', '#ffb020', '#3050ff', '#ff3070', '#f0f0ff')]


D = 72.0
SEED = 21
APPROACH = np.array([(-1000, 480, -1000), (-700, 280, -760), (-598, 190, -520), (-598, 175, -260),
                     (-540, 168, -146), (-300, 165, -147), (-150, 170, -160), (160, 175, -188),
                     (400, 168, -191), (640, 180, -191), (800, 230, -260), (720, 250, -330),
                     (460, 215, -200), (230, 190, -195), (152, 172, -330), (152, 158, -520),
                     (110, 151, -569), (0, 150, -569), (-120, 150, -569), (-140, 150, -569)], float)
DEPART = np.array([(-140, 150, -569), (-196, 152, -569), (-196, 165, -450), (-196, 175, -240),
                   (-280, 178, -147), (-480, 178, -147), (-596, 190, -260), (-596, 220, -500),
                   (-620, 300, -700), (-800, 600, -1100), (-1100, 1000, -1500)], float)
TEAM = [(0, 'nose')] + [(o, 'deer') for o in (38, 70, 102, 134)] + [(196, 'sleigh')]
REAR = 196 + 40
T_LAND, T_GO = 34.5, 47.0                   # the team stands on the porch roof between these
LANDING, TAKEOFF = (30.5, 34.5), (46.5, 50.5)   # galloping on the roof
SANTA_DOWN = (35.5, 36.5)                   # Santa dims away down the chimney
SANTA_UP = 43.0                             # and comes back up with three flashes: ho, ho, ho
HO = (43.3, 43.9, 44.5)
GIFTS_IN = (37.0, 3.4)                      # presents appear one by one from 37 s over 3.4 s


def open_spline(pts, per=80):
    """Open Catmull-Rom through pts (K,3) -> dense polyline (M,3) and its cumulative arc length."""
    P = np.vstack([pts[:1], pts, pts[-1:]])
    f = np.linspace(0, 1, per, endpoint=False)[:, None]
    seg = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        seg.append(0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f ** 2 +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3))
    seg.append(P[-2:-1])
    line = np.vstack(seg)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])
    return line, s


def at(line, s, q):
    q = np.clip(q, 0, s[-1])
    return np.stack([np.interp(q, s, line[:, c]) for c in range(3)], -1)


class _Flight:
    """The track, the leader's arc length per frame, and every random draw render() makes before its frame loop,
    in render()'s order, so score() can replay the same flight."""

    def __init__(self, G, seed):
        rng = self.rng = np.random.default_rng(seed)
        F = self.F = nframes(D)
        P = G.pos
        L1, S1 = open_spline(APPROACH)
        L2, _ = open_spline(DEPART)
        line = self.line = np.vstack([L1, L2[1:]])
        S = self.S = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(line, axis=0), axis=1))])

        # leader arc length: integrate eased speed profiles, scaled to land exactly at the stop
        tt = np.arange(F) * DT
        stop = S1[-1]
        v1 = np.array([keys(t, [(2, 0), (5, 1), (27, 1), (30, 0.45), (T_LAND, 0)]) for t in tt])
        v2 = np.array([keys(t, [(T_GO, 0), (50, 0.5), (54, 1), (66, 1.25)]) for t in tt])
        s1, s2 = np.cumsum(v1) * DT, np.cumsum(v2) * DT
        s1 *= stop / s1[-1]
        s2 *= (S[-1] + REAR - stop) / s2[np.searchsorted(tt, 67.5)]
        self.lead_s = s1 + s2

        self.stars = rng.choice(G.N, 40, replace=False)
        self.sph = rng.uniform(0, 2 * np.pi, 40)
        self.sfr = rng.uniform(0.1, 0.4, 40)
        self.gift_seg = np.concatenate([G.seg['Left'], G.seg['Right']])
        self.gx = P[self.gift_seg, 0]
        boxes = []
        for lo, hi in ((-590, -200), (158, 625)):
            x = lo + rng.uniform(8, 20)
            while x < hi - 20:
                w = rng.uniform(26, 48)
                boxes.append((x, x + w, len(boxes) % len(GIFTS), rng.uniform(37, 40.5)))
                x += w + rng.uniform(14, 28)
        order = rng.permutation(len(boxes))
        self.boxes = [(a, b, c, GIFTS_IN[0] + GIFTS_IN[1] * k / len(boxes)) for k, (a, b, c, _) in zip(order, boxes)]
        self.ptw = rng.uniform(4, 9, 400)

    def pose(self, q):
        a, b = at(self.line, self.S, np.array([q - 3, q, q + 3]))[[0, 1, 2]], None
        tang = a[2] - a[0]
        tang /= np.linalg.norm(tang) + 1e-9
        return a[1], np.array([-tang[2], 0, tang[0]])

    def frames(self):
        """Per frame: t, the team members in the air or on the roof [(kind, centre, perp)], whether parked, the
        glitter launched [(pos, vel, life)] and the hooves that strike the roof [(centre, perp)]."""
        rng, S, pose = self.rng, self.S, self.pose
        prev_sleigh = None
        for f in range(self.F):
            t = f * DT
            lead = self.lead_s[f]
            parked = T_LAND <= t < T_GO
            sleigh_pos = None
            members = []
            for off, kind in TEAM:
                q = lead - off
                if q < 0 or q > S[-1]:
                    continue
                c, perp = pose(q)
                members.append((kind, c, perp))
                if kind == 'sleigh':
                    sleigh_pos = c

            # glitter shed by the sleigh: launched slightly up and back
            shed = []
            if sleigh_pos is not None and prev_sleigh is not None and not parked and 3 < t < 68:
                vel = (sleigh_pos - prev_sleigh) / DT
                for _ in range(3 if np.linalg.norm(vel) > 20 else 0):
                    pos = sleigh_pos + rng.normal(0, 6, 3)
                    v = 0.25 * vel + rng.normal(0, 25, 3) + np.array([0, 20, 0])
                    shed.append((pos, v, rng.uniform(2.0, 4.0)))
            prev_sleigh = sleigh_pos

            # hoofbeats on the porch roof: gallop on landing and take-off, idle stamps while parked
            rolling = (LANDING[0] < t < LANDING[1]) or (TAKEOFF[0] < t < TAKEOFF[1])
            beats = []
            for j, (off, kind) in enumerate(TEAM[1:5]):
                q = lead - off
                if q < 0:
                    continue
                cx, perp = pose(q)
                if abs(cx[1] - 150) > 4:                  # only hooves on the roof make a sound
                    continue
                beat = False
                if rolling:
                    ph = (t * 3.2 + j * 0.27) % 1
                    beat = any(abs(ph - b) < DT * 1.6 for b in (0.0, 0.12, 0.24))
                elif parked and rng.random() < 0.012:
                    beat = True
                if beat:
                    beats.append((j, cx, perp))
            yield t, members, parked, shed, beats


def render(G, seed=SEED):
    fl = _Flight(G, seed)
    F = fl.F
    out = np.zeros((F, G.N, 3))
    P = G.pos
    W = np.array([1.0, 1.6, 1.0])          # height counts more: things above the roof read dimmer
    stars, sph, sfr = fl.stars, fl.sph, fl.sfr
    gift_seg, gx, boxes = fl.gift_seg, fl.gx, fl.boxes

    pv = np.zeros((400, 3))
    pp = np.zeros((400, 3))
    page = np.full(400, 99.0)
    plife = np.ones(400)
    ptw = fl.ptw
    nxt = 0
    hoof = np.zeros(G.N)

    for f, (t, members, parked, shed, beats) in enumerate(fl.frames()):
        fr = out[f]
        sky = keys(t, [(0, 0), (2, 0.09), (66, 0.09), (71.5, 0)])
        fr += light(NIGHT, np.full(G.N, sky))
        tw = np.clip(np.sin(2 * np.pi * sfr * t + sph), 0, 1) ** 3
        fr[stars] += light(STAR, 0.22 * tw * sky / 0.09)

        for kind, c, perp in members:
            hf = np.exp(-((c[1] - 150) / 110) ** 2)     # high above the roof reads faint
            d = np.linalg.norm((P - c)[:, [0, 2]], axis=1)
            if kind == 'nose':
                pulse = 1 + 0.25 * np.sin(2 * np.pi * 1.3 * t)
                fr += light(NOSE, 0.95 * hf * pulse * np.exp(-(d / 16) ** 2))
                fr += light(NOSE, 0.25 * hf * np.exp(-(d / 50) ** 2))
            elif kind == 'deer':
                for side in (-1, 1):                  # each pair runs side by side
                    dd = np.linalg.norm((P - c - side * 9 * perp)[:, [0, 2]], axis=1)
                    fr += light(DEER, 0.6 * hf * np.exp(-(dd / 13) ** 2))
            else:
                santa = 1.0
                if parked:
                    santa = keys(t, [(SANTA_DOWN[0], 1), (SANTA_DOWN[1], 0.25), (SANTA_UP, 0.25), (HO[0], 1.2),
                                     (43.6, 0.5), (HO[1], 1.2), (44.2, 0.5), (HO[2], 1.2), (45, 1)])
                fr += light(SLEIGH, 0.85 * hf * santa * np.exp(-(d / 26) ** 2))
                fr += light(GOLD, 0.35 * hf * np.exp(-((d - 30) / 8) ** 2))

        # glitter falls under gravity with drag
        for pos, v, life in shed:
            k = nxt % 400
            nxt += 1
            pp[k] = pos
            pv[k] = v
            page[k] = 0
            plife[k] = life
        live = page < plife
        if live.any():
            pv[live] *= np.exp(-1.6 * DT)
            pv[live, 1] -= 60 * DT
            pp[live] += pv[live] * DT
            page[live] += DT
            idx = np.nonzero(live)[0]
            dd = np.linalg.norm((P[None] - pp[idx, None]) * W, axis=2)
            amp = (1 - page[idx] / plife[idx]) * (0.6 + 0.4 * np.sin(ptw[idx] * page[idx] * 6.28))
            g = (amp[:, None] * np.exp(-(dd / 9) ** 2)).max(0)
            fr += light(GLINT, 0.8 * g) + light(GOLD, 0.3 * g)
        page[~live] = 99

        hoof *= np.exp(-DT / 0.09)
        for j, cx, perp in beats:
            for side in (-1, 1):
                dd = np.linalg.norm(P - cx - side * 9 * perp, axis=1)
                hoof = np.maximum(hoof, np.exp(-(dd / 7) ** 2))
        fr += light(HOOF, 0.9 * hoof)

        # presents left under the eaves while Santa is inside
        if t > GIFTS_IN[0]:
            I = np.zeros(len(gift_seg))
            col = np.zeros((len(gift_seg), 3))
            for a, b, c, t0 in boxes:
                m = (gx > a) & (gx < b)
                u = (gx[m] - a) / (b - a)
                ribbon = np.exp(-((u - 0.5) / 0.07) ** 2)
                e = keys(t, [(t0, 0), (t0 + 0.5, 1), (68, 1), (71.5, 0)])
                I[m] = e * (0.32 + 0.3 * ribbon)
                col[m] = lerp(GIFTS[c], GOLD, ribbon[:, None])
            fr[gift_seg] += (np.clip(I, 0, None) ** 2.2)[:, None] * col
    return out


# ---- music: a sleigh-ride trot in F at 96 bpm ----
# Bar 0 starts when the team sets off (2 s), so the downbeats fall on the show's moments: bar 13 is the landing
# (34.5 s), bar 14 the first present (37 s), bar 18 the take-off (47 s), bar 26 the last of the team over the
# horizon (67 s), bar 28 the end. Sleigh bells trot on the eighths while the team flies, panned to it and louder as it
# comes down to the roof; flute and pizzicato carry the tune on the way in, a clarinet sings over the swoop past the
# street, the landing gallop clatters in wood on the roof where each pair of hooves strikes, a slide whistle takes
# Santa down the chimney and back up, every present rings a glockenspiel note where it appears, low brass gives his
# three flashes their ho-ho-ho, and the whole band takes the tune for the take-off and the climb away.

BEAT = 60 / 96
BAR = 4 * BEAT
T0 = 2.0                                    # bar 0: the team sets off


def bt(bar, beat=0.0):
    return T0 + bar * BAR + beat * BEAT


CHORDS = {                                  # bass root, fifth, and the chord in the middle
    'F': ('F2', 'C3', ('A3', 'C4', 'F4')),
    'Bb': ('Bb1', 'F2', ('Bb3', 'D4', 'F4')),
    'C7': ('C2', 'G2', ('Bb3', 'E4', 'G4')),
    'A7': ('A1', 'E2', ('C#4', 'E4', 'G4')),
    'Dm': ('D2', 'A2', ('A3', 'D4', 'F4')),
    'Gm': ('G1', 'D2', ('Bb3', 'D4', 'G4')),
    'Gm7': ('G1', 'D2', ('Bb3', 'D4', 'F4')),
}
# the tune, a bar per row: (beat, note, beats)
TUNE_A = [
    [(0, 'C5', 1), (1, 'A4', .5), (1.5, 'C5', .5), (2, 'F5', 1), (3, 'E5', 1)],
    [(0, 'D5', 1.5), (1.5, 'C5', .5), (2, 'A4', 1), (3, 'F4', 1)],
    [(0, 'G4', .5), (.5, 'A4', .5), (1, 'Bb4', .5), (1.5, 'D5', .5), (2, 'F5', 1), (3, 'D5', 1)],
    [(0, 'C5', 2), (2, 'G4', .5), (2.5, 'A4', .5), (3, 'Bb4', .5), (3.5, 'B4', .5)],
    [(0, 'C5', 1), (1, 'A4', .5), (1.5, 'C5', .5), (2, 'F5', 1), (3, 'G5', 1)],
    [(0, 'A5', 1.5), (1.5, 'G5', .5), (2, 'E5', 1), (3, 'C#5', 1)],
    [(0, 'D5', .5), (.5, 'E5', .5), (1, 'F5', .5), (1.5, 'D5', .5), (2, 'Bb4', 1), (3, 'D5', 1)],
    [(0, 'C5', 1), (1, 'E5', 1), (2, 'F5', 2)],
]
HARM_A = [('F', 'F'), ('F', 'F'), ('Bb', 'Bb'), ('C7', 'C7'), ('F', 'F'), ('A7', 'A7'), ('Dm', 'Bb'), ('C7', 'F')]
TUNE_B = [                                  # the swoop out over the street and down to the porch
    [(0, 'D5', 2), (2, 'F5', 1), (3, 'D5', 1)],
    [(0, 'C5', 2), (2, 'A4', 1), (3, 'C5', 1)],
    [(0, 'Bb4', 1), (1, 'A4', 1), (2, 'G4', 1), (3, 'D5', 1)],
    [(0, 'C5', 4)],
    [(0, 'Bb4', 2), (2, 'C5', 2)],
]
HARM_B = [('Bb', 'Bb'), ('F', 'F'), ('Gm', 'Gm'), ('C7', 'C7'), ('Gm7', 'C7')]
TUNE_END = [(0, 'C5', 1), (1, 'E5', 1), (2, 'G5', 1), (3, 'E5', 1)]   # the last bar of the climb, into bar 26
GIFT_NOTES = ('C5', 'D5', 'F5', 'G5', 'A5', 'C6', 'D6', 'C6', 'A5', 'G5', 'F5', 'D5', 'C5', 'F5')
HO_NOTES = ('C3', 'A2', 'F2')


def _sounds(G):
    """What score() needs from render()'s flight, frame by frame: time, where the team is (centre x, height),
    glitter launched, and each hoof strike (time, which pair, x), one per strike."""
    fl = _Flight(G, SEED)
    ts, xs, ys, shed, beats, last = [], [], [], [], [], {}
    for t, members, parked, sh, bt_ in fl.frames():
        if members:
            c = np.mean([m[1] for m in members], axis=0)
            xs.append(c[0])
            ys.append(c[1])
        else:
            xs.append(xs[-1] if xs else -1000.0)
            ys.append(1000.0)
        ts.append(t)
        shed.append(len(sh))
        for j, cx, _ in bt_:
            if t - last.get(j, -1) > 0.03:        # render() lights a strike on one or two frames
                beats.append((t, j, cx[0]))
            last[j] = t
    return np.array(ts), np.array(xs), np.array(ys), np.array(shed), beats, fl.boxes


def score(M, G):
    from pixelhome.audio import SR, note, whoosh, slide
    n = note
    ts, tx, ty, tshed, beats, boxes = _sounds(G)

    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    flute_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    clar_st = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/stac/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    bell = M.hits('Percussion/Sleighbells_Hit*.wav')
    bell2 = M.hits('VSCO 1 Percussion/varMetal/various/sleighbell1_hit_[123].wav')
    shake = M.hits('VSCO 1 Percussion/varMetal/various/sleighbell[12]_shake1.wav')
    tree = M.hits('Percussion/BellTree_Stroke*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_asc1.wav')
    hoof = M.hits('Percussion/LogDrumHi_MedM*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click_[fm]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/Timpani1_Roll*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    crash = M.hits('Percussion/cymbal-crash1_mf*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    thump = M.hits('Percussion/BDrumNewhit_v[3-4]*.wav')

    for name, gain, rev in (('tune', 0.3, 0.2), ('counter', 0.26, 0.22), ('bass', 0.34, 0.08), ('chords', 0.22, 0.15),
                            ('bells', 0.7, 0.12), ('hooves', 0.24, 0.08), ('perc', 0.36, 0.15), ('fx', 0.3, 0.2),
                            ('glitter', 0.25, 0.35)):
        M.bus(name, gain=0.88 * gain, reverb=rev)

    x0, x1 = G.pos[:, 0].min(), G.pos[:, 0].max()

    def pan_x(x):                            # x across the facade -> left/right from the street
        return float(np.clip(0.85 * (2 * (x - x0) / (x1 - x0) - 1), -0.95, 0.95))

    def team(t):                             # where the team is at t: pan, and how near (high above reads faint)
        x = np.interp(t, ts, tx)
        y = np.interp(t, ts, ty)
        return pan_x(x), 0.12 + 0.88 * np.exp(-((y - 150) / 160) ** 2)

    def mono(sig, pans):                     # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def line(bars, k0, sus, st, bus='tune', vel=96, pan=0.0, gain=1.0, octave=0):
        for j, bar in enumerate(bars):
            for b, m, ln in bar:
                inst = st if (st is not None and ln <= 0.5) else sus
                M.add(bus, inst.play(n(m) + octave, vel, dur=ln * BEAT * 0.92, release=0.15), bt(k0 + j, b), gain, pan)

    def band(k0, harm, vel=90, chords=True, gain=1.0):
        """Oom-pah in pizzicato: bass on 1 and 3, the chord on 2 and 4."""
        for j, (c1, c2) in enumerate(harm):
            for half, c in ((0, c1), (1, c2)):
                root, fifth, ch = CHORDS[c]
                M.add('bass', bass.play(n(root if half == 0 or c1 != c2 else fifth), vel), bt(k0 + j, 2 * half), gain)
                if chords:
                    for m in ch:
                        M.add('chords', pizz.play(n(m), vel - 10), bt(k0 + j, 2 * half + 1), 0.5 * gain, -0.2)

    def held(k0, harm, inst, vel=60, gain=1.0, bus='chords', pan=0.25):
        for j, (c1, c2) in enumerate(harm):
            for half, c in ((0, c1), (1, c2)) if c1 != c2 else ((0, c1),):
                ln = 2 if c1 != c2 else 4
                for m in CHORDS[c][2]:
                    M.add(bus, inst.play(n(m), vel, dur=ln * BEAT * 0.98, release=0.3), bt(k0 + j, 2 * half), 0.4 * gain,
                          pan)

    # ---- the pickup: the red lamp appears far away ----
    s = shake.play(70)
    M.add('bells', s * np.linspace(0.05, 1, s.shape[1])[None] ** 2, 0.0, 0.5, pan_x(-1000))
    for k, m in enumerate(('F3', 'A3', 'C4', 'F4', 'A4', 'C5', 'F5')):
        M.add('counter', harp.play(n(m), 70 + 4 * k), 0.9 + 0.08 * k, 0.6, -0.5)
    line([[(3, 'G4', .5), (3.5, 'A4', .5)]], -1, flute, flute_st, vel=80)

    # ---- the sleigh bells: on every eighth while the team flies, at the team, nearer = louder ----
    for e in range(int((D - T0) / (BEAT / 2))):
        t = T0 + e * BEAT / 2
        flying = (3.0 < t < LANDING[0] + 0.5) or (TAKEOFF[0] + 1.0 < t < 67.0)
        if not flying:
            continue
        p, near = team(t)
        acc = e % 2 == 0
        M.add('bells', (bell if acc else bell2).play(100 if acc else 76), t, 0.55 * near, p)
        if e % 8 == 7 and near > 0.4:                # a shake into every bar
            M.add('bells', shake.play(64, dur=0.6), t, 0.35 * near, p)

    # ---- the glitter: a faint music box twinkling at the sleigh for as long as it sheds ----
    rng = np.random.default_rng(SEED + 100)
    sparkle = []
    twinkle = [n(m) for m in ('A5', 'C6', 'D6', 'F6', 'G6')]
    for e in range(int(D / (BEAT / 2))):
        t = e * BEAT / 2 + rng.uniform(0, 0.08)
        k = int(t / DT)
        if k < len(tshed) and tshed[max(0, k - 2):k + 3].sum() > 0 and rng.random() < 0.45:
            sparkle.append((t, twinkle[int(rng.integers(len(twinkle)))], int(rng.integers(40, 70)), 0.25))
    sig = box.render(sparkle, D + 1).mean(0)
    tt = np.arange(sig.shape[0]) / SR
    M.add('glitter', mono(sig, np.array([team(t)[0] for t in tt[::480]]).repeat(480)[:len(sig)]), 0.0)
    M.add('fx', tree.play(90), 4.6, 0.5, team(4.6)[0])                    # the trail begins
    M.add('fx', tree.play(90), 48.6, 0.5, team(48.6)[0])

    # ---- bars 0-7: the way in, round the back, along the Left wing and across the front ----
    line(TUNE_A, 0, flute, flute_st, vel=92)
    line(TUNE_A[4:], 4, glock, None, 'counter', vel=70, gain=0.5, pan=0.2)
    band(0, HARM_A, vel=84)
    for j in range(8):                                                   # the harp rolls each bar's chord
        for k, m in enumerate(CHORDS[HARM_A[j][0]][2]):
            M.add('counter', harp.play(n(m) - 12, 64), bt(j) + 0.04 * k, 0.5, -0.4)
    for j in (3, 7):
        M.add('perc', tri.play(80), bt(j + 1), 0.5, 0.3)

    # ---- bars 8-12: the swoop out past the end of Right, back and down onto the porch roof ----
    line(TUNE_B[:4], 8, clar, clar_st, vel=96, pan=0.15)
    line(TUNE_B[4:], 12, clar, clar_st, vel=76, pan=0.15)               # held back for the touchdown
    held(8, HARM_B, horn, vel=70)
    band(8, HARM_B[:3], vel=80, chords=False)
    for j, (c1, _) in enumerate(HARM_B[:4]):                             # flute answers in eighths
        for k, m in enumerate(CHORDS[c1][2]):
            M.add('counter', flute_st.play(n(m) + 12, 70), bt(8 + j, 2.5 + 0.5 * k), 0.5, -0.3)
    M.add('fx', whoosh(3.0, 350, 2600, 0.9, seed=1), 19.8, 0.5, 0.85)       # out over the street, past Right
    M.add('fx', whoosh(3.0, 2600, 400, 0.9, seed=2), 25.6, 0.45, 0.45)      # down onto the porch
    # the landing: strings tremble, timpani and snare roll up to the touchdown
    for m in ('G3', 'Bb3', 'D4', 'F4'):
        a = trem.play(n(m), 70, dur=2 * BAR, release=0.1)
        M.add('chords', a * np.linspace(0.3, 0.8, a.shape[1])[None], bt(11), 0.3, 0.1)
    r = troll.play(100, dur=BAR)
    M.add('perc', r * np.linspace(0.2, 1, r.shape[1])[None] ** 2, bt(12), 0.4)
    r = sroll.play(90, dur=BAR)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1])[None] ** 2, bt(12), 0.25, 0.1)

    # ---- bar 13: touchdown, then Santa slides down the chimney ----
    p_sleigh = pan_x(56)
    for m in ('F3', 'A3', 'C4', 'F4', 'A4'):
        M.add('chords', horn.play(n(m), 90, dur=0.4, release=0.3), T_LAND, 0.5)
    M.add('tune', flute.play(n('F5'), 96, dur=0.5, release=0.3), T_LAND)
    M.add('bass', bass.play(n('F2'), 110), T_LAND)
    for m in ('C4', 'F4', 'A4'):
        M.add('tune', tpt.play(n(m), 104), T_LAND, 0.6)
        M.add('chords', pizz.play(n(m), 110), T_LAND, 0.6)
    M.add('perc', timp.play(120), T_LAND, 1.0)
    M.add('perc', crash.play(100), T_LAND, 0.6)
    M.add('bells', shake.play(90), T_LAND, 0.7, p_sleigh)
    sd = SANTA_DOWN[1] - SANTA_DOWN[0]
    M.add('fx', slide(0.0, sd, 1400, 260, sd + 0.1, 0.5), SANTA_DOWN[0], 0.8, p_sleigh)
    M.add('fx', thump.play(70), SANTA_DOWN[1] + 0.05, 0.6, p_sleigh)    # he lands in the fireplace
    for k, m in enumerate(('C4', 'B3', 'Bb3', 'A3', 'Ab3', 'G3')):     # the bassoon tiptoes down after him
        M.add('counter', bsn.play(n(m), 80), SANTA_DOWN[0] + k * sd / 5, 0.6, p_sleigh)

    # ---- bars 14-15: the presents, each a glockenspiel note where it appears ----
    for k, (a, b, c, t0) in enumerate(sorted(boxes, key=lambda bx: bx[3])):
        p = pan_x((a + b) / 2)
        m = n(GIFT_NOTES[k % len(GIFT_NOTES)])
        M.add('counter', glock.play(m, 96), t0, 0.7, p)
        M.add('counter', harp.play(m - 12, 80), t0, 0.4, p)
    for j, (c, bline) in enumerate((('F', ('F3', 'A3', 'C4', 'A3')), ('Bb', ('Bb3', 'D4', 'C4', 'E3')))):
        root, fifth, ch = CHORDS[c]
        M.add('bass', bass.play(n(root), 80), bt(14 + j), 0.9)
        M.add('bass', bass.play(n(fifth), 70), bt(14 + j, 2), 0.9)
        for m in ch:
            M.add('chords', horn.play(n(m), 50, dur=BAR * 0.98, release=0.4), bt(14 + j), 0.3, 0.3)
        for k, m in enumerate(bline):
            M.add('counter', bsn.play(n(m), 70), bt(14 + j, k), 0.45, -0.25)

    # ---- bar 16-17: up the chimney, ho ho ho, and the band winds up for the take-off ----
    M.add('bass', bass.play(n('C2'), 80), bt(16), 0.9)
    for m in CHORDS['C7'][2]:
        M.add('chords', horn.play(n(m), 50, dur=BAR, release=0.4), bt(16), 0.3, 0.3)
    up0 = SANTA_UP - 0.45
    M.add('fx', slide(0.0, HO[0] - up0, 300, 1500, HO[0] - up0 + 0.05, 0.5), up0, 0.8, p_sleigh)
    for t, m in zip(HO, HO_NOTES):
        M.add('tune', bone.play(n(m) + 12, 110), t, 0.9, p_sleigh)
        M.add('bass', tuba.play(n(m), 110), t, 0.8, p_sleigh)
        M.add('bells', shake.play(80, dur=0.5), t, 0.5, p_sleigh)
    for k, m in enumerate(('C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'Bb4', 'B4')):    # the run up into the take-off
        M.add('counter', clar_st.play(n(m), 70 + 4 * k), bt(17, 0.5 * k), 0.6, -0.2)
        M.add('chords', pizz.play(n(m) - 12, 70 + 4 * k), bt(17, 0.5 * k), 0.4, 0.2)
    r = sroll.play(90, dur=BAR)
    M.add('perc', r * np.linspace(0.05, 1, r.shape[1])[None] ** 2, bt(17), 0.45, 0.1)
    for m in ('C3', 'E3', 'G3', 'Bb3'):
        a = trem.play(n(m) + 12, 70, dur=BAR, release=0.1)
        M.add('chords', a * np.linspace(0.2, 1, a.shape[1])[None], bt(17), 0.3, 0.1)

    # ---- bars 18-25: take-off, the whole band: back along the Left wing, up the Side and away ----
    end = [list(b) for b in TUNE_A]
    end[7] = TUNE_END
    harm = HARM_A[:7] + [('C7', 'C7')]
    line(end, 18, tpt_s, tpt, vel=100, pan=-0.1)
    line(end, 18, flute, flute_st, vel=88, gain=0.6, pan=0.15)
    line(end, 18, glock, None, 'counter', vel=76, gain=0.5, pan=0.25)
    band(18, harm, vel=96)
    held(18, harm, horn, vel=72)
    M.add('perc', crash.play(100), T_GO, 0.5)
    M.add('perc', timp.play(110), T_GO, 0.8)
    for j in range(8):
        for b in (1, 3):
            M.add('perc', tamb.play(80), bt(18 + j, b), 0.35, 0.35)
    for j in (3, 7):
        M.add('perc', tri.play(90), bt(18 + j + 1), 0.5, 0.3)
    M.add('fx', whoosh(5.0, 300, 3000, 0.9, seed=3), 56.8, 0.45, -0.8)      # up the Side and into the sky

    # ---- bar 26-27: the team is a star over the horizon ----
    for m in ('F2', 'C3'):
        M.add('bass', bass.play(n(m), 100), bt(26), 0.9)
    for m in ('F3', 'A3', 'C4', 'F4', 'A4'):
        M.add('chords', horn.play(n(m), 80, dur=3.5, release=1.2), bt(26), 0.55)
    M.add('tune', tpt_s.play(n('F5'), 96, dur=2.6, release=1.0), bt(26), 0.8)
    M.add('tune', flute.play(n('F5'), 88, dur=3.0, release=1.0), bt(26), 0.5)
    M.add('perc', crash.play(90), bt(26), 0.45)
    M.add('fx', chimes.play(80), bt(26) + 0.2, 0.4, -0.6)
    for k, m in enumerate(('F4', 'A4', 'C5', 'F5', 'A5', 'C6')):
        M.add('counter', harp.play(n(m), 76), bt(26) + 0.06 * k, 0.55, -0.4)
    M.add('counter', glock.play(n('F5'), 80), bt(27), 0.5, -0.9)
    M.add('bells', shake.play(60, dur=1.5), bt(27), 0.25, -0.95)

    # ---- the hooves, wherever each pair strikes the porch roof ----
    pr = np.random.default_rng(SEED + 200)
    for t, j, x in beats:
        idle = T_LAND <= t < TAKEOFF[0]
        vel = 72 if idle else 88
        pitch = -1.5 * j + pr.uniform(-0.4, 0.4)
        M.add('hooves', hoof.play(vel, pitch=pitch), t, 0.8, pan_x(x))
        M.add('hooves', click.play(vel - 10, pitch=pitch), t, 0.35, pan_x(x))
