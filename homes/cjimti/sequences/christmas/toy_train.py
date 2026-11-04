"""Toy Train: A wind-up train runs the whole roofline from the free back end of Side to the free end
of Right: engine with a headlight beam and firebox, tender, four lit coaches and a caboose with a red
tail lamp. The cars are masses on spring couplers, so when the engine brakes for each of the five
corners the train bunches up and stretches out again like a slinky; smoke puffs chuff out of the
stack in time with the wheels. It runs off the right end, comes back round from the back of the
house, and pulls into a stop on the Left wing with a bump that ripples down the train."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, lerp, Flicker, nframes

CODE = 'XM02'
TITLE = 'Toy Train'
KIND = 'show'
DESCRIPTION = ('A toy train runs the whole roofline, slowing for every corner so the cars bunch up and '
               'stretch out, chuffing smoke. It leaves at the right end and comes round again from the back.')

RAIL = hexc('#8090b0')
HEAD = hexc('#fff0c8')
ENGINE = hexc('#c01808')
BRASS = hexc('#ffb030')
FIRE = hexc('#ff4000')
WINDOW = hexc('#ffc060')
TAIL = hexc('#ff0800')
SMOKE = hexc('#c0c8d8')
COACH = [hexc(c) for c in ('#108030', '#a01010', '#1840a0', '#a06a08')]
CABOOSE = hexc('#d01008')


D = 64.0
SEED = 22
CORNER_IDX = (80, 178, 260, 331, 380)                    # the five corners, by path index
CARS = [('engine', 48), ('tender', 22)] + [('coach', 34)] * 4 + [('caboose', 30)]
GAP = 6.0
REST = np.array([CARS[i][1] + GAP for i in range(len(CARS) - 1)])
STOP = 640.0                                             # where the engine's nose stops on the second run


def _corners(G):
    x = G.pd[G.path]
    return np.array([(x[i] + x[i + 1]) / 2 for i in CORNER_IDX])


def _simulate(G, rng):
    """The train, frame by frame: yields (t, pos, vel, puffs, whistles, state) after each step. pos/vel are the
    cars' fronts and speeds; puffs [s, t0, size] already aged and drifted for this frame; whistles the time of every
    toot so far; state this frame's moments: a new chuff (s, size), a corner toot, t_off, t_stop, the caboose lost."""
    Ltr = G.length
    corners = _corners(G)
    cars, rest = CARS, REST
    K, C = 60.0, 7.0                                     # coupler stiffness, damping (per unit mass)
    VMAX, VCORNER, ACC = 145.0, 38.0, 60.0

    def vlim(s):
        s = np.atleast_1d(s)
        lim = VMAX - (VMAX - VCORNER) * np.exp(-((s[:, None] - corners[None]) / 45) ** 2).max(1)
        return lim.min()

    def start(front):
        return front - np.concatenate([[0], np.cumsum(rest)]), np.zeros(len(cars))

    pos, vel = start(-20.0)
    run = 1
    puffs = []                                          # [s, t0, size]
    chuff_phase = 0.0
    t_off = None
    t_stop = None
    loose = False
    whistles = []

    for f in range(nframes(D)):
        t = f * DT
        state = dict(chuff=None, toot=None, t_off=False, t_stop=False, lost=False)
        # engine control: speed limit for the corners anywhere under the train, accel limited
        go = t > 2.5 if run == 1 else t > t_off + 3.0
        if go:
            span = np.linspace(pos[0] - 30, pos[0] + 50, 5)
            target = vlim(span)
            if run == 2:
                target = min(target, np.sqrt(max(0.0, 2 * 30 * (STOP - pos[0]))))
        else:
            target = 0.0
        for _ in range(4):
            h = DT / 4
            dv = np.clip(target - vel[0], -ACC * 1.6 * h, ACC * h)
            vel[0] += dv
            if run == 2 and pos[0] >= STOP and vel[0] < 4:
                vel[0] = 0.0
            stretch = (pos[:-1] - pos[1:]) - rest
            rel = vel[:-1] - vel[1:]
            force = K * stretch + C * rel
            if loose:
                force[-1] = 0.0                          # the caboose's coupler has let go
            acc = -0.8 * vel                             # rolling friction
            acc[1:] += force
            acc[1:-1] -= force[1:]
            if loose:
                acc[-1] = -9.0 - 0.3 * vel[-1]           # ...and it rolls back down the grade
            vel[1:] += acc[1:] * h
            pos += vel * h
        if run == 1 and pos[-1] > Ltr + 40 and t_off is None:
            t_off = t
            state['t_off'] = True
            run = 2
            pos, vel = start(-20.0)

        speed = vel[0]
        if run == 2 and t_stop is None and pos[0] >= STOP - 1 and speed == 0:
            t_stop = t
            state['t_stop'] = True
        if t_stop is not None and not loose and t > t_stop + 3.5:
            loose = True
            whistles += [t + 0.8, t + 2.6, t + 3.2]
            state['lost'] = True
        # chuffs: four per wheel turn, a puff of smoke from the stack
        chuff_phase += speed * DT / 22.0
        if chuff_phase >= 1 and speed > 2:
            chuff_phase -= 1
            puffs.append([pos[0] - 10, t, rng.uniform(0.7, 1.1)])
            state['chuff'] = (pos[0] - 10, puffs[-1][2])
        if run == 2 and t > 50 and speed < 1 and rng.random() < 0.02:
            puffs.append([pos[0] - 10, t, rng.uniform(0.4, 0.7)])
            state['chuff'] = (pos[0] - 10, puffs[-1][2])

        # toot-toot: two swells of the headlight beam as the engine nears each corner
        for c in list(corners) + [STOP - 60]:
            if pos[0] < c - 110 <= pos[0] + speed * DT:
                whistles.append(t)
                state['toot'] = c
        # smoke: drifts back, swells, fades
        keep = []
        for p in puffs:
            if t - p[1] > 2.8:
                continue
            keep.append(p)
            p[0] -= 6 * DT
        puffs = keep
        yield t, pos, vel, puffs, whistles, state


def render(G, seed=SEED):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    x = G.pd[G.path]                                    # track coordinate of each pixel, path order
    fire = Flicker(rng, 1, 2, 7)
    cars, rest = CARS, REST
    sleepers = 0.5 + 0.5 * np.cos(2 * np.pi * x / 14)

    for f, (t, pos, vel, puffs, whistles, _) in enumerate(_simulate(G, rng)):
        fr = np.zeros((G.N, 3))
        # track bed
        rail = keys(t, [(0, 0), (1.5, 0.085), (62, 0.085), (65.5, 0)])
        fr += light(RAIL, rail * (0.75 + 0.25 * sleepers))

        toot = sum(np.exp(-((t - w - d) / 0.09) ** 2) for w in whistles for d in (0.0, 0.32))

        # cars
        for i, (kind, ln) in enumerate(cars):
            a, b = pos[i] - ln, pos[i]
            body = smoothstep(a - 1.5, a + 1.5, x) * (1 - smoothstep(b - 1.5, b + 1.5, x))
            if not body.any():
                continue
            u = np.clip((x - a) / ln, 0, 1)
            if kind == 'engine':
                rod = 0.5 + 0.5 * np.sin(2 * np.pi * (x - a) / 12 - pos[0] / 6)
                fr += light(ENGINE, 0.45 * body * (u < 0.62))
                fr += light(BRASS, 0.3 * body * (u >= 0.62) + 0.12 * body * rod * (u < 0.62))
                fl = 0.75 + 0.25 * fire(t)[0]
                fr += light(FIRE, 0.7 * fl * np.exp(-((x - (a + 7)) / 4) ** 2))
                fr += light(HEAD, 1.0 * np.exp(-((x - (b - 1)) / 2.2) ** 2))
                ahead = x - b
                beam = np.where(ahead > 0, np.exp(-ahead / 55) * (0.5 + 0.5 * smoothstep(0, 6, ahead)), 0)
                fr += light(HEAD, (0.38 + 0.5 * toot) * beam)
            elif kind == 'tender':
                fr += light(BRASS, 0.22 * body)
            elif kind == 'coach':
                c = COACH[(i - 2) % 4]
                fr += light(c, 0.42 * body)
                win = sum(np.exp(-((x - (a + ln * w)) / 2.6) ** 2) for w in (0.22, 0.5, 0.78))
                fr += light(WINDOW, 0.6 * win * body)
            else:
                fr += light(CABOOSE, 0.42 * body)
                fr += light(WINDOW, 0.45 * np.exp(-((x - (a + ln * 0.5)) / 3) ** 2) * body)
                lamp = 0.85 + 0.15 * np.sin(2 * np.pi * 1.5 * t)
                fr += light(TAIL, lamp * np.exp(-((x - (a + 1)) / 2.2) ** 2))
            # couplers: a little brass glint when they are pulled taut or crushed
            if i > 0:
                st = abs((pos[i - 1] - pos[i]) - rest[i - 1])
                fr += light(BRASS, min(1, st / 4) * 0.5 * np.exp(-((x - (b + GAP / 2)) / 2) ** 2))

        # smoke: drifts back, swells, fades
        for p in puffs:
            age = t - p[1]
            w = 5 + 9 * age
            amp = p[2] * 0.42 * np.exp(-age / 0.9) * smoothstep(0, 0.12, age)
            cloud = amp * np.exp(-((x - p[0]) / w) ** 2)
            fr *= 1 - 0.9 * cloud[:, None]             # smoke hides the cars under it
            fr += light(SMOKE, cloud)

        out[f][G.path] = fr * keys(t, [(D - 3, 1), (D - 0.5, 0)])
    return out


# ---- music: a wind-up toy march in G ----
# The wind-up key ratchets, then a march on glockenspiel and clarinet over a bassoon and pizzicato oom-pah, with
# sleigh bells on the off-beats. The tempo map is anchored on the lights: each of the five corner toot-toots is
# the downbeat of a new phrase, and the melody rests there for the whistle to answer. As the train runs flat out
# off the right end the band breaks into a galop that ends with it; it comes round again to the tune, slows into
# the station and cadences on the stop. Then the caboose comes loose: a bassoon rolls down the scale after it, the
# engine whistles, and a last phrase plays it off. Every chuff is a puff of steam, every coupler that bunches or
# snaps taut clanks where it is, the brakes hiss, and the caboose clicks over the rail joints as it rolls away.

MUSIC_SEED = 122
# (beat, seconds): toots at 6.48, 11.55, 16.73, 21.43, 26.30; off the end 34.90; toot 41.90; stop 47.45;
# caboose loose 50.98; last chord 60.5
TEMPO = ((8, 6.48), (16, 11.55), (24, 16.73), (32, 21.43), (40, 26.30), (56, 34.90), (68, 41.90), (76, 47.45),
         (82, 50.98), (96, 60.5))
CH = {
    'G': ('G2', 'D3', ('G3', 'B3', 'D4')), 'C': ('C3', 'G2', ('G3', 'C4', 'E4')),
    'D7': ('D3', 'A2', ('F#3', 'C4', 'D4')), 'D': ('D3', 'A2', ('F#3', 'A3', 'D4')),
    'Em': ('E3', 'B2', ('G3', 'B3', 'E4')), 'Am': ('A2', 'E3', ('A3', 'C4', 'E4')),
    'A7': ('A2', 'E3', ('G3', 'C#4', 'E4')),
}
# phrases of eight beats; each starts with a beat's rest where the whistle toots: (beat, note, beats)
PHRASES = {
    'P1': [(1, 'G4', .5), (1.5, 'A4', .5), (2, 'B4', .5), (2.5, 'G4', .5), (3, 'B4', .5), (3.5, 'D5', .5),
           (4, 'E5', 1), (5, 'D5', 1), (6, 'C5', 1), (7, 'A4', 1)],
    'P2': [(1, 'G4', .5), (1.5, 'A4', .5), (2, 'B4', .5), (2.5, 'G4', .5), (3, 'B4', .5), (3.5, 'D5', .5),
           (4, 'C5', 1), (5, 'E5', 1), (6, 'D5', 2)],
    'P3': [(1, 'D5', .5), (1.5, 'C5', .5), (2, 'B4', .5), (2.5, 'C5', .5), (3, 'D5', .5), (3.5, 'B4', .5),
           (4, 'C5', 1), (5, 'A4', 1), (6, 'B4', .5), (6.5, 'A4', .5), (7, 'G4', .5), (7.5, 'F#4', .5)],
    'P4': [(1, 'E5', .5), (1.5, 'D5', .5), (2, 'C5', .5), (2.5, 'E5', .5), (3, 'D5', .5), (3.5, 'B4', .5),
           (4, 'A4', 1), (5, 'D5', 1), (6, 'G4', 2)],
    'PR': [(1, 'D5', .5), (1.5, 'C5', .5), (2, 'B4', .5), (2.5, 'C5', .5), (3, 'D5', .5), (3.5, 'B4', .5),
           (4, 'A4', .5), (4.5, 'B4', .5), (5, 'C5', .5), (5.5, 'A4', .5), (6, 'F#4', 1), (7, 'A4', 1), (8, 'G4', 3)],
}
HARM = {'P1': ('G', 'G', 'C', 'D7'), 'P2': ('G', 'Em', 'Am', 'D'), 'P3': ('G', 'G', 'Am', 'D7'),
        'P4': ('C', 'C', 'D7', 'G'), 'PR': ('G', 'G', 'Am', 'D7')}
GALOP = ('G', 'C', 'D', 'G', 'Em', 'A7', 'D', 'D7')      # beats 40-56, two beats each


def _beat_time():
    """Beat -> seconds through the anchors, a monotone cubic so the tempo eases between them."""
    b = np.array([0.0] + [a for a, _ in TEMPO])
    t = np.array([TEMPO[0][1] - (TEMPO[1][1] - TEMPO[0][1])] + [s for _, s in TEMPO])
    d = np.diff(t) / np.diff(b)
    m = np.concatenate([[d[0]], (d[:-1] + d[1:]) / 2, [d[-1]]])

    def at(x):
        x = np.asarray(x, float)
        i = np.clip(np.searchsorted(b, x) - 1, 0, len(b) - 2)
        h = b[i + 1] - b[i]
        u = (x - b[i]) / h
        y = (t[i] * (2 * u ** 3 - 3 * u ** 2 + 1) + h * m[i] * (u ** 3 - 2 * u ** 2 + u) +
             t[i + 1] * (-2 * u ** 3 + 3 * u ** 2) + h * m[i + 1] * (u ** 3 - u ** 2))
        lo, hi = x < b[0], x > b[-1]
        y = np.where(lo, t[0] + (x - b[0]) * d[0], np.where(hi, t[-1] + (x - b[-1]) * d[-1], y))
        return float(y) if y.ndim == 0 else y
    return at


def _light_events(G):
    """Replay render()'s simulation (the same random draws) and keep what the score needs, frame by frame."""
    rng = np.random.default_rng(SEED)
    Flicker(rng, 1, 2, 7)
    rec = dict(t=[], pos=[], vel=[], chuffs=[], toots=[], t_off=None, t_stop=None, t_lost=None)
    for t, pos, vel, puffs, whistles, st in _simulate(G, rng):
        rec['t'].append(t)
        rec['pos'].append(pos.copy())
        rec['vel'].append(vel.copy())
        if st['chuff']:
            rec['chuffs'].append((t, st['chuff'][0], st['chuff'][1], vel[0]))
        for k in ('t_off', 't_stop'):
            if st[k]:
                rec[k] = t
        if st['lost']:
            rec['t_lost'] = t
        rec['whistles'] = list(whistles)
    for k in ('t', 'pos', 'vel'):
        rec[k] = np.array(rec[k])
    return rec


def score(M, G):
    import pedalboard as pb
    from pixelhome.audio import SR, note
    n = note
    rng = np.random.default_rng(MUSIC_SEED)
    at = _beat_time()
    ev = _light_events(G)
    T, P, V = ev['t'], ev['pos'], ev['vel']
    L = G.length

    for name, gain, rev in (('tune', 0.4, 0.18), ('bells', 0.85, 0.22), ('band', 0.32, 0.12), ('bass', 0.45, 0.06),
                            ('perc', 0.5, 0.12), ('steam', 0.45, 0.1), ('whistle', 0.32, 0.2), ('clank', 0.45, 0.1)):
        M.bus(name, gain=gain, reverb=rev)
    M.duck('steam', ['tune', 'band', 'bass'], margin=4.0, floor=-6.0)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def away(dd):                            # off either end of the track the train is round the back: quieter
        out = max(0.0, -dd, dd - L)
        return float(np.exp(-out / 140))

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    sleigh = M.hits('Miscellania Raw/Misc 2/sleighbell1_hit_[123].wav')
    sleigh_q = M.hits('Miscellania Raw/Misc 2/sleighbell1_hit_quiet.wav')
    shake = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake1.wav')
    tri = M.hits('Percussion/Triangle3-HitM_v1*.wav')
    crank = M.hits('Percussion/Ratchet1-Crank*.wav')
    clank = M.hits('Percussion/BrakeDrum1_Hammer_v[12]*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v2*.wav')
    clave = M.hits('VSCO 1 Percussion/varWood/claves_pp1.wav')
    bd = M.hits('Percussion/BDrumNewhit_v3*.wav')
    cym = M.hits('Percussion/susCymb1-hit_mp*.wav')

    # ---- steam: one noise burst per puff, in a few colours ----
    def burst(lo, hi, length, seed):
        x = np.random.default_rng(seed).normal(0, 1, (1, int(length * SR))).astype(np.float32)
        x = pb.Pedalboard([pb.HighpassFilter(lo), pb.LowpassFilter(hi), pb.LowpassFilter(hi * 1.3)])(x, SR)[0]
        tt = np.arange(x.size) / SR
        env = np.clip(tt / 0.008, 0, 1) * np.exp(-tt / (length / 4))
        return x / (np.abs(x).max() + 1e-9) * env
    puffs = [burst(500 + 150 * k, 2600 + 300 * k, 0.22, MUSIC_SEED + k) for k in range(5)]
    for i, (t, s, size, v) in enumerate(ev['chuffs']):
        sig = puffs[int(rng.integers(len(puffs)))]
        accent = 1.0 if i % 4 == 0 else 0.7
        g = 0.55 * size * accent * (0.6 + 0.4 * min(1, v / 145)) * away(s)
        M.add('steam', mono(sig, np.full(sig.size, pan_at(s))), t, g)

    # ---- brakes and departures: a hiss that follows how hard the engine slows (or pulls away) ----
    acc = np.gradient(V[:, 0], DT)
    brake = np.clip(-acc / 90, 0, 1) * (V[:, 0] > 1)
    pull = np.clip(acc / 60, 0, 1) * (V[:, 0] < 70)
    lvl = np.convolve(0.5 * brake + 0.35 * pull, np.hanning(9) / np.hanning(9).sum(), 'same')
    nS = int(T[-1] * SR)
    hiss = np.random.default_rng(MUSIC_SEED + 9).normal(0, 1, (1, nS)).astype(np.float32)
    hiss = pb.Pedalboard([pb.HighpassFilter(3000), pb.LowpassFilter(9000)])(hiss, SR)[0]
    hiss /= np.abs(hiss).max()
    ts = np.arange(nS) / SR
    env = np.interp(ts, T, lvl * np.array([away(p) for p in P[:, 0]]))
    M.add('steam', mono(hiss * env, np.interp(ts, T, [pan_at(p - 10) for p in P[:, 0]])), 0.0, 0.5)

    # ---- the whistle: a three-note steam chord, shaped like the headlight's swell ----
    def whistle(w, pan):
        tt = np.arange(int(0.9 * SR)) / SR - 0.25
        env = sum(np.exp(-((tt - d) / 0.09) ** 2) for d in (0.0, 0.32)) ** 0.5
        scoop = 1 - 0.02 * np.exp(-np.clip(tt + 0.25, 0, None) / 0.05)
        sig = np.zeros_like(tt)
        for k, m in enumerate(('G4', 'B4', 'D5')):
            f = 440 * 2 ** ((n(m) - 69) / 12) * scoop * (1 + 0.002 * k)
            ph = 2 * np.pi * np.cumsum(f) / SR
            sig += np.sin(ph) + 0.15 * np.sin(2 * ph)
        breath = np.convolve(np.random.default_rng(int(w * 100)).normal(0, 1, tt.size), np.ones(16) / 16, 'same')
        sig = (sig / 3 + 0.25 * breath) * env
        M.add('whistle', mono(sig, np.full(tt.size, pan)), w - 0.25, 0.6)
    for w in ev['whistles']:
        f = min(len(T) - 1, int(round(w / DT)))
        whistle(w, pan_at(P[f, 0]))
        M.add('perc', tri.play(85), w, 0.5, pan_at(P[f, 0]))

    # ---- couplers: a clank where the cars bunch up hard, a lighter clink where they snap taut ----
    stretch = (P[:, :-1] - P[:, 1:]) - REST[None]
    last = np.full(stretch.shape[1], -9.0)
    for f in range(1, len(T) - 1):
        for i in range(stretch.shape[1]):
            a = abs(stretch[f, i])
            if a > 2.5 and a >= abs(stretch[f - 1, i]) and a > abs(stretch[f + 1, i]) and T[f] - last[i] > 0.35:
                last[i] = T[f]
                s = P[f, i + 1] + GAP / 2
                if not 0 <= s <= L:
                    continue
                v = int(np.clip(60 + 12 * a, 60, 120))
                if stretch[f, i] < 0:
                    M.add('clank', clank.play(v, pitch=7 + i), T[f], 0.5, pan_at(s))
                else:
                    M.add('clank', clank.play(v - 20, pitch=14 + i), T[f], 0.3, pan_at(s))

    # ---- the wind-up: a few cranks of the key at the engine, then the brake off ----
    for k, tk in enumerate((0.1, 0.55, 1.0)):
        M.add('perc', crank.play(95 - 8 * k), tk, 0.5, pan_at(0))
    M.add('bells', glock.play(n('G5'), 90), 1.45, 0.5, pan_at(0))

    # ---- the band ----
    def melody(name, b0, vel=100, glk=True, gain=1.0):
        for b, m, ln in PHRASES[name]:
            t = at(b0 + b)
            d = at(b0 + b + ln) - t
            M.add('tune', clar.play(n(m), vel, dur=d * 0.85), t, 0.9 * gain, -0.1)
            if glk:
                M.add('bells', glock.play(n(m) + 12, vel - 15), t, 0.45 * gain, 0.15)

    def oompah(b0, chords, vel=96, bells=True, gain=1.0):
        for j, c in enumerate(chords):
            root, fifth, triad = CH[c]
            for e, bass in ((0, root), (1, fifth)):
                b = b0 + 2 * j + e
                M.add('bass', bsn.play(n(bass), vel, dur=0.3), at(b), 0.8 * gain, -0.15)
                M.add('bass', cello.play(n(bass), vel), at(b), 0.6 * gain, 0.1)
                for m in triad:
                    M.add('band', vln.play(n(m), vel - 18), at(b + 0.5), 0.35 * gain, 0.25)
                if bells:
                    M.add('perc', sleigh.play(vel - 20), at(b + 0.5), 0.35 * gain, -0.3)

    oompah(0, ('G', 'G', 'D7', 'D7'), 88)                          # the vamp: off he goes
    M.add('perc', shake.play(90), at(1.5), 0.5, pan_at(0))
    for k, name in enumerate(('P1', 'P2', 'P3', 'P4')):
        b0 = 8 + 8 * k
        oompah(b0, HARM[name])
        melody(name, b0)
        M.add('bells', harp.play(n('G5'), 80), at(b0), 0.3, pan_at(P[int(round(at(b0) / DT)), 0]))
    # the galop: flat out down the Right wing and off the end, running eighths on xylophone and flute
    for j, c in enumerate(GALOP):
        root, fifth, triad = CH[c]
        b0 = 40 + 2 * j
        arp = [n(m) + 12 for m in triad] + [n(triad[0]) + 24]
        if j % 2:
            arp = arp[::-1]
        for e in range(4):
            t = at(b0 + e / 2)
            M.add('tune', xylo.play(arp[e], 100), t, 0.5, 0.2)
            M.add('tune', flute.play(arp[e], 92, dur=0.2), t, 0.45, -0.1)
        for e in (0, 1):
            M.add('bass', bsn.play(n(root if e == 0 else fifth), 104, dur=0.25), at(b0 + e), 0.9, -0.15)
            M.add('bass', cello.play(n(root if e == 0 else fifth), 104), at(b0 + e), 0.6, 0.1)
            for m in triad:
                M.add('band', vln.play(n(m), 90), at(b0 + e + 0.5), 0.4, 0.25)
            M.add('perc', sleigh.play(100), at(b0 + e + 0.5), 0.4, -0.3)
        M.add('perc', sleigh_q.play(80), at(b0 + 0.25), 0.3, -0.3)
    for m in CH['G'][2]:                                            # gone: a chord as the caboose leaves
        M.add('band', horn.play(n(m), 92, dur=1.4), at(56), 0.5, 0.6)
    M.add('bass', bsn_s.play(n('G2'), 96, dur=1.4), at(56), 0.7, 0.4)
    M.add('perc', cym.play(90), at(56), 0.5, pan_at(L))
    # round the back of the house: a music box far off, then the vamp as he comes back into view on the Side
    for k, m in enumerate(('D5', 'B4', 'G4', 'A4', 'B4', 'C5')):
        M.add('bells', glock.play(n(m) + 12, 70), at(57.5 + k * 0.5), 0.35, 0.0)
    oompah(60, ('G', 'G', 'D7', 'D7'), 84, gain=0.85)
    M.add('perc', shake.play(85), at(61), 0.45, pan_at(0))
    # back to the tune, slowing into the station: the cadence lands on the stop
    oompah(68, HARM['PR'])
    melody('PR', 68)
    t_stop = ev['t_stop']
    for m in CH['G'][2]:
        M.add('band', horn.play(n(m), 96, dur=2.2), t_stop, 0.55, -0.4)
    M.add('bass', bsn_s.play(n('G2'), 100, dur=2.2), t_stop, 0.8, -0.3)
    M.add('bass', cello.play(n('G2'), 110), t_stop, 0.8, -0.3)
    M.add('tune', clar.play(n('G4'), 96, dur=2.0), t_stop, 0.8, -0.1)
    M.add('bells', glock.play(n('G5'), 100), t_stop, 0.5, -0.3)
    M.add('perc', bd.play(110), t_stop, 0.7, pan_at(STOP))
    M.add('perc', shake.play(95), t_stop, 0.5, pan_at(STOP))
    burst_big = burst(400, 5000, 1.4, MUSIC_SEED + 20)                # the engine lets off steam
    M.add('steam', mono(burst_big, np.full(burst_big.size, pan_at(STOP - 10))), t_stop + 0.3, 0.6)
    # waiting at the platform: pizzicato tick-tock
    for k in range(4):
        b = 78 + k
        M.add('band', vln.play(n('D4') if k % 2 else n('G4'), 80), at(b), 0.45, -0.2)
    # the caboose lets go: a clang at its coupler, then the bassoon rolls down the scale after it
    t_lost = ev['t_lost']
    f = int(round(t_lost / DT))
    sc = P[f, -1] + 30
    M.add('clank', anvil.play(105), t_lost, 0.6, pan_at(sc))
    M.add('perc', clank.play(110, pitch=3), t_lost + 0.05, 0.5, pan_at(sc))
    run = ['D4', 'C#4', 'C4', 'B3', 'Bb3', 'A3', 'Ab3', 'G3', 'F#3', 'F3', 'E3', 'Eb3', 'D3']
    for k, m in enumerate(run):
        tk = t_lost + 0.35 + 0.24 * k
        M.add('tune', bsn.play(n(m), 100 - 2 * k, dur=0.2), tk, 1.0, pan_at(sc - 12 * k))
    for k, m in enumerate(('E5', 'D#5', 'D5')):                     # the engine calls after it
        w = ev['whistles'][-3 + k]
        M.add('tune', clar.play(n(m) - 12, 90, dur=0.5), w + 0.62, 0.7, pan_at(STOP))
    # the caboose rolls away over the rail joints
    cab = P[f:, -1]
    for j in range(1, len(cab)):
        for off in (4, 26):
            a, b = (cab[j - 1] - off) // 28, (cab[j] - off) // 28
            if a != b:
                tt = T[f + j]
                M.add('perc', clave.play(70, pitch=-5 if off == 26 else 0), tt, 0.6, pan_at(cab[j]))
    # the last phrase: the tune once more, gently, and the final chord
    tag = [(84, 'B4', 1), (85, 'C5', 1), (86, 'D5', 2), (88, 'B4', 1), (89, 'A4', 1), (90, 'G4', 1), (91, 'A4', 1),
           (92, 'B4', 2), (94, 'A4', 2)]
    for b, m, ln in tag:
        t = at(b)
        M.add('tune', clar.play(n(m), 84, dur=(at(b + ln) - t) * 0.9), t, 0.8, -0.1)
        M.add('bells', glock.play(n(m) + 12, 74), t, 0.35, 0.15)
    for j, c in enumerate(('G', 'C', 'G', 'D7', 'G', 'D7')):
        root, fifth, triad = CH[c]
        b = 84 + 2 * j
        M.add('bass', cello.play(n(root), 84), at(b), 0.6, 0.1)
        for m in triad:
            M.add('band', vln.play(n(m), 70), at(b + 1), 0.3, 0.25)
    tf = at(96)
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('band', horn.play(n(m), 90, dur=2.6), tf, 0.45, 0.0)
    M.add('tune', clar.play(n('G4'), 90, dur=2.4), tf, 0.7, -0.1)
    M.add('bass', bsn_s.play(n('G2'), 92, dur=2.6), tf, 0.7)
    for k, m in enumerate(('G4', 'B4', 'D5', 'G5', 'B5')):
        M.add('bells', harp.play(n(m), 80), tf + 0.06 * k, 0.4, 0.2)
    M.add('bells', glock.play(n('G5'), 95), tf, 0.5)
    M.add('perc', shake.play(95), tf, 0.5)
    M.add('perc', tri.play(95), tf, 0.5)
