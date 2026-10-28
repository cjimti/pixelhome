"""Leaf Fall: Autumn leaves fall through real 3-D space onto the roof. Each one flutters as it drops,
gliding side to side and flipping its bright face and dull back toward the street; its light gathers
and sharpens as it nears the roofline. Leaves that hit the roof skitter along it in the breeze and
drift into piles that grow at the five corners. A gust halfway through sends a flurry across; the
last big gust lifts every pile and blows the whole lot out of the free right end. One last leaf."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG03'
TITLE = 'Leaf Fall'
KIND = 'show'
DESCRIPTION = ('Leaves flutter down through 3-D space, flipping as they fall, land on the roof and drift into piles '
               'at the corners, until a gust blows every pile out the end of the house.')

LEAF = [hexc(c) for c in ('#ff8a18', '#c0102a', '#ffb000', '#ff5200', '#a83a08', '#e06010')]
BROWN = hexc('#5a1c04')
D = 66.0
CORNERS = np.array([491.0, 894.0, 1311.0, 1660.0, 2033.0])
Y_ROOF = 150.0


def render(G, seed=23, log=None):
    """log, a list, collects the events score() plays to: (kind, t, path distance), kind land/miss/pile/gone."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    P = G.pos[G.path]                       # path order
    pdp = G.pd[G.path]
    xz = P[:, [0, 2]]

    # spawn schedule: a trickle that thickens, a flurry with the mid gust, then quiet, then one last leaf
    spawn = list(rng.uniform(1, 12, 10)) + list(rng.uniform(10, 30, 38)) + list(rng.uniform(28, 38, 30)) + \
        list(rng.uniform(38, 47, 18))
    spawn = np.sort(np.array(spawn))
    L = len(spawn) + 1
    spawn = np.append(spawn, 58.5)
    j = rng.integers(0, n, L)
    j[-1] = 296                               # last leaf aims for the middle of the porch
    # offset sideways from the roof, so some miss and fall past
    seg_dir = np.gradient(xz, axis=0)
    seg_dir /= np.linalg.norm(seg_dir, axis=1, keepdims=True) + 1e-9
    normal = np.stack([-seg_dir[:, 1], seg_dir[:, 0]], 1)
    start = xz[j] + normal[j] * rng.normal(0, 18, L)[:, None] - np.array([1.0, 0]) * rng.uniform(0, 30, L)[:, None]
    start[-1] = xz[296]
    h0 = rng.uniform(260, 460, L)
    h0[-1] = 380
    omega = 2 * np.pi * rng.uniform(0.45, 0.8, L)
    phase = rng.uniform(0, 2 * np.pi, L)
    swing = rng.uniform(25, 55, L)
    ang = rng.uniform(0, 2 * np.pi, L)
    sdir = np.stack([np.cos(ang), np.sin(ang)], 1)
    vdesc = rng.uniform(55, 80, L)
    col = np.array([LEAF[k] for k in rng.integers(0, len(LEAF), L)])
    col[-1] = LEAF[2]

    # state
    state = np.zeros(L, int)                  # 0 waiting, 1 falling, 2 on roof, 3 in a pile, 4 gone
    pos = start.copy()
    h = h0.copy()
    lp = np.zeros(L)                          # path position once on the roof
    target = np.zeros(L)
    landed_at = np.zeros(L)
    fade_out = np.zeros(L)
    slots = np.zeros((len(CORNERS), 2), int)
    blow_v = rng.uniform(260, 520, L)
    rustle = Flicker(rng, L, 0.4, 1.6)
    glint = Flicker(rng, n, 0.1, 0.5)

    for f in range(F):
        t = f * DT
        wind = keys(t, [(0, 6), (28, 9), (31, 90), (35, 90), (39, 10), (50, 10), (52, 160), (56.5, 50), (58.5, 0), (66, 0)])
        buf = np.zeros((n, 3))
        buf += light(BROWN, keys(t, [(0, 0), (2, 0.08), (62, 0.08), (66, 0)]) * (1 + 0.2 * glint(t)))

        # start falling
        state[(state == 0) & (spawn <= t)] = 1
        fa = state == 1
        if fa.any():
            th = omega[fa] * t + phase[fa]
            edge = np.abs(np.cos(th))                         # gliding flat falls slowly, edge-on falls fast
            h[fa] -= vdesc[fa] * (0.35 + 1.1 * (1 - edge)) * DT
            glide = swing[fa, None] * omega[fa, None] * np.cos(th)[:, None] * sdir[fa]
            pos[fa] += (glide + np.array([wind, 0.0])) * DT
            # draw: a spot that sharpens and brightens as the leaf comes down to the roof
            hh = np.clip(h[fa] - Y_ROOF, 0, None)
            face = 0.3 + 0.7 * (0.5 + 0.5 * np.cos(th)) ** 2
            amp = face * 1.05 * np.exp(-hh / 320) * smoothstep(0, 0.8, t - spawn[fa])
            rad = 11 + 0.2 * hh
            d2 = ((xz[None, :, :] - pos[fa][:, None, :]) ** 2).sum(-1)
            I = amp[:, None] * np.exp(-d2 / rad[:, None] ** 2)
            buf += np.einsum('ln,lc->nc', I ** 2.2, col[fa])
            # reaching roof height: land on the nearest pixel if close enough, else fall past
            idx = np.where(fa)[0][h[fa] <= Y_ROOF]
            for k in idx:
                dd = ((xz - pos[k]) ** 2).sum(1)
                m = int(np.argmin(dd))
                if dd[m] < 42 ** 2:
                    state[k] = 2
                    lp[k] = pdp[m]
                    landed_at[k] = t
                    c = int(np.argmin(np.abs(CORNERS - lp[k])))
                    s = 0 if lp[k] < CORNERS[c] else 1
                    target[k] = CORNERS[c] + (-1 if s == 0 else 1) * (5 + 7.5 * min(slots[c, s], 16))
                    slots[c, s] += 1
                    if log is not None:
                        log.append(('land', t, lp[k]))
                else:
                    state[k] = 4
                    fade_out[k] = t
                    if log is not None:
                        log.append(('miss', t, pdp[m]))
        # leaves that missed: a last dim glimpse as they pass the roofline
        for k in np.where((state == 4) & (t - fade_out < 0.5) & (fade_out > 0))[0]:
            d2 = ((xz - pos[k]) ** 2).sum(1)
            buf += light(col[k], 0.5 * (1 - (t - fade_out[k]) / 0.5) * np.exp(-d2 / 16 ** 2))

        # on the roof: skitter toward the corner pile, rustle in the breeze
        roof = (state == 2) | (state == 3)
        if roof.any():
            gust_front = (t - 52.0) * 520
            blown = roof & (t > 52.0) & (gust_front > lp) & (landed_at < 56)
            calm = roof & ~blown
            step = np.where(landed_at > 56, 0, target - lp)
            v = np.clip(step * 1.2, -45, 45) * (1 + wind / 60)
            lp[calm & (state == 2)] += v[calm & (state == 2)] * DT
            settle = (state == 2) & (np.abs(target - lp) < 1.0)
            state[settle] = 3
            # the big gust: everything goes, faster the further it has been pushed
            lp[blown] += blow_v[blown] * smoothstep(0, 1.2, t - 52 - lp[blown] / 520) * DT
            gone = roof & (lp > G.length + 30)
            state[gone] = 4
            if log is not None:
                log += [('pile', t, lp[k]) for k in np.where(settle)[0]] + [('gone', t, G.length) for k in np.where(gone)[0]]
            on = np.where((state == 2) | (state == 3))[0]
            jig = rustle(t)[on] * (0.6 + wind / 50) * np.where(state[on] == 3, 0.4, 1.2)
            land = np.exp(-(t - landed_at[on]) / 0.25) * (t > landed_at[on])       # a flash as it lands
            amp = np.where(state[on] == 3, 0.68, 0.6) * (1 + 0.08 * rustle(t)[on]) * (1 + 0.7 * land)
            w = np.where(state[on] == 3, 5.2, 4.5)
            I = amp[:, None] * np.exp(-((pdp[None, :] - (lp[on] + jig)[:, None]) / w[:, None]) ** 2)
            buf += np.einsum('ln,lc->nc', np.clip(I, 0, None) ** 2.2, col[on])
        buf *= keys(t, [(63, 1.0), (66, 0.0)])
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A slow waltz in F, 3/4 with one bar to every 1.625 s so the big gust lands on a downbeat: upright piano oom-pah-pah,
# clarinet and flute trading an autumn tune, a string pad. Every leaf that lands is a harp pluck from the chord of the
# moment, higher the further right it lands; leaves that miss are a soft pizzicato as they fall past; settling into a
# pile is a marimba tap. The gusts are whooshes that sweep across with the wind, the last one lifting each corner pile
# with a strum as its front passes and shaking out the free end in a shower. The last leaf gets the last note.

BAR = 1.625
GUST, GUST_V = 52.0, 520.0                  # the big gust and the speed of its front, as in render()
LAST = 58.5                                 # the last leaf's spawn
PROG = ['F', 'F'] + ['F', 'Am', 'Bb', 'F', 'Dm', 'Gm', 'C', 'F'] + ['Bb', 'C', 'Am', 'Dm', 'Gm', 'C', 'F', 'C7'] + \
    ['Bb', 'Gm', 'C', 'C7'] + ['F', 'Am', 'Bb', 'F', 'Dm', 'Gm', 'C', 'F'] + ['Dm', 'C7'] + ['F'] * 9
CHORD = {'F': (41, (57, 60, 65)), 'Am': (45, (57, 60, 64)), 'Bb': (46, (58, 62, 65)), 'Dm': (50, (57, 62, 65)),
         'Gm': (43, (58, 62, 67)), 'C': (48, (55, 60, 64)), 'C7': (48, (55, 58, 64))}
TUNE_A = [[(0, 'A4', 2), (2, 'C5', 1)], [(0, 'E5', 1.5), (1.5, 'D5', .5), (2, 'C5', 1)], [(0, 'D5', 2), (2, 'F4', 1)],
          [(0, 'A4', 3)], [(0, 'F5', 2), (2, 'E5', 1)], [(0, 'D5', 1.5), (1.5, 'C5', .5), (2, 'Bb4', 1)],
          [(0, 'G4', 1), (1, 'Bb4', 1), (2, 'E5', 1)], [(0, 'F4', 3)]]
TUNE_B = [[(0, 'D5', 1), (1, 'F5', 1), (2, 'D5', 1)], [(0, 'E5', 2), (2, 'G4', 1)], [(0, 'C5', 1), (1, 'E5', 1), (2, 'A5', 1)],
          [(0, 'F5', 2), (2, 'D5', 1)], [(0, 'Bb4', 1.5), (1.5, 'D5', .5), (2, 'G5', 1)], [(0, 'E5', 2), (2, 'C5', 1)],
          [(0, 'F5', 1), (1, 'C5', 1), (2, 'A4', 1)], [(0, 'Bb4', 2), (2, 'C5', 1)]]


def score(M, G):
    from pixelhome.audio import note, whoosh
    n = note
    ev = []
    render(G, log=ev)                       # the same simulation: when and where every leaf lands, misses, settles, leaves
    harp = M.sampler('Strings/Harp/*.wav')
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vla = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    pizz = M.sampler('Strings/Violin Section/Pizz/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    cym = M.hits('Percussion/susCymb1-cresc-Long_v1.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')

    for name, gain, rev in (('piano', 0.24, 0.2), ('harp', 0.42, 0.3), ('wind', 0.2, 0.3), ('pad', 0.16, 0.4),
                            ('pizz', 0.3, 0.25), ('mallet', 0.25, 0.25), ('drums', 0.6, 0.3), ('fx', 0.7, 0.3)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def chord_at(t):
        return PROG[min(len(PROG) - 1, int(t // BAR))]

    def tones(c, lo, hi):                   # the chord's notes between lo and hi
        pcs = {m % 12 for m in CHORD[c][1]} | {CHORD[c][0] % 12}
        return [m for m in range(lo, hi + 1) if m % 12 in pcs]

    def pluck(c, d, lo, hi):                # a chord tone, higher the further right on the facade
        tt = tones(c, lo, hi)
        return tt[int(round((pan_at(d) / 0.85 + 1) / 2 * (len(tt) - 1)))]

    def tune(inst, bars, b0, bus, vel, pan, shift=0):
        for i, bar in enumerate(bars):
            for b, m, dur in bar:
                t = (b0 + i) * BAR + b * BAR / 3
                M.add(bus, inst.play(n(m) + shift, vel, dur=dur * BAR / 3 * 0.95, release=0.25), t, 1.0, pan)

    # ---- the waltz: oom on one, pah-pah on two and three; the piano sits out the hush before the big gust ----
    for k in range(1, len(PROG)):
        t, c = k * BAR, PROG[k]
        if 30 <= k < 32 or t >= LAST:
            continue
        root, ch = CHORD[c]
        soft = 0.75 if k >= 32 else 1.0
        M.add('piano', piano.play(root + (7 if k % 2 and c not in ('Dm', 'Am') else 0), 78), t, soft, -0.2)
        for b in (1, 2):
            for m in ch:
                M.add('piano', piano.play(m, 56 + 6 * (b == 1)), t + b * BAR / 3, 0.55 * soft, 0.1)
    # the pad breathes under the chords and swells with each gust
    for k in range(0, len(PROG)):
        t, c = k * BAR, PROG[k]
        if t >= 63.5:
            break
        swell = 1.0 + 0.7 * (18 <= k < 22) + 0.4 * (k >= 32)
        root, ch = CHORD[c]
        M.add('pad', vla.play(root + 12, int(min(110, 60 * swell)), dur=BAR, release=0.4), t, 0.8, -0.3)
        M.add('pad', vln.play(ch[1], int(min(110, 54 * swell)), dur=BAR, release=0.4), t, 0.7, 0.3)
    # the tune: clarinet, then flute, then both, under whatever the leaves are doing
    harp_roll = [n('F3'), n('C4'), n('F4'), n('A4'), n('C5'), n('F5')]
    for i, m in enumerate(harp_roll):
        M.add('harp', harp.play(m, 70 + 4 * i), 0.3 + 0.12 * i, 0.9, -0.4 + 0.16 * i)
    tune(clar, TUNE_A, 2, 'wind', 82, -0.15)
    tune(flute, TUNE_B, 10, 'wind', 76, 0.15)
    tune(clar, TUNE_A, 22, 'wind', 86, -0.15)
    tune(flute, [[(0, 'C5', 3)], [(0, 'A4', 1.5), (1.5, 'Bb4', 1.5)], [(0, 'D5', 3)], [(0, 'C5', 3)],
                 [(0, 'A4', 3)], [(0, 'Bb4', 3)], [(0, 'G4', 1.5), (1.5, 'Bb4', 1.5)], [(0, 'A4', 3)]],
         22, 'wind', 62, 0.25)
    M.add('pad', clar.play(n('Bb4'), 58, dur=2 * BAR, release=0.5), 30 * BAR, 0.8, -0.1)    # the hush: a held question
    M.add('pad', flute.play(n('E5'), 54, dur=2 * BAR, release=0.5), 30 * BAR, 0.7, 0.1)

    # ---- the leaves ----
    for kind, t, d in ev:
        c, p = chord_at(t), pan_at(d)
        if kind == 'land':
            M.add('harp', harp.play(pluck(c, d, n('D4'), n('C6')), 88 + int(M.rng.integers(-10, 10))), t, 0.9, p)
        elif kind == 'miss':
            M.add('pizz', pizz.play(pluck(c, d, n('F3'), n('F5')), 70), t, 0.8, p)
            M.add('fx', whoosh(0.35, 1200, 400, 0.25, seed=int(t * 40)), t - 0.1, 0.3, p)
        elif kind == 'pile' and t < GUST:
            M.add('mallet', mar.play(pluck(c, d, n('F3'), n('C5')), 60), t, 0.7, p)

    # ---- the mid gust: wind up to 90 from 28 to 31, held to 35, gone by 39 ----
    M.add('fx', whoosh(11.0, 200, 1600, 0.6, seed=31), 28.0, 0.9, 0.0)
    for i, m in enumerate(tones('Bb', n('Bb3'), n('D6'))):          # harp glissando with the wind, left to right
        M.add('harp', harp.play(m, 64 + 3 * i), 30.6 + 0.05 * i, 0.6, -0.7 + 0.1 * i)
    M.add('drums', cym.play(60), 28.5, 0.35)

    # ---- the big gust: the front runs the path at GUST_V, each corner pile goes up as it passes ----
    M.add('drums', troll.play(70, dur=3.2), GUST - 2.6, 0.5, -0.5)
    M.add('drums', timp.play(110), GUST, 0.8, -0.5)
    M.add('pad', vln.play(n('C5'), 96, dur=6.0, release=1.2), GUST, 0.9, 0.0)
    M.add('pad', vla.play(n('A3'), 96, dur=6.0, release=1.2), GUST, 0.9, 0.0)
    seg = 1.6                               # the whoosh runs the facade in pieces so its pan follows the front
    for i, ts in enumerate(np.arange(GUST - 0.4, GUST + G.length / GUST_V + 0.4, seg / 2)):
        d = np.clip((ts + seg / 2 - GUST) * GUST_V, 0, G.length)
        M.add('fx', whoosh(seg, 250, 3200, 0.9, seed=60 + i), ts, 1.0, pan_at(d))
    for j, cd in enumerate(CORNERS):
        t = GUST + cd / GUST_V
        for i, m in enumerate(tones('F', n('F3') + 3 * j, n('F5') + 2 * j)[:6]):
            M.add('harp', harp.play(m, 92), t + 0.045 * i, 0.75, pan_at(cd + 30 * i))
    gone = [t for kind, t, d in ev if kind == 'gone']
    shower = tones('F', n('C4'), n('C6'))[::-1]
    for i, t in enumerate(gone):            # every leaf out the free end, a falling shower
        M.add('harp', harp.play(shower[i % len(shower)], 74 - 24 * i // len(gone)), t, 0.6, 0.85)
    M.add('drums', tri.play(70), gone[0], 0.4, 0.85)
    M.add('fx', whoosh(2.5, 1500, 300, 0.5, seed=99), gone[-1] - 1.0, 0.7, 0.85)

    # ---- one last leaf flutters down to the porch, and the waltz ends where it lands ----
    land = [(t, d) for kind, t, d in ev if kind == 'land'][-1]
    t, d = land
    fall = (('C5', 1.0), ('A4', 0.8), ('Bb4', 0.8), ('G4', 1.2), ('E4', 0.9))
    at = np.concatenate([[0], np.cumsum([x for _, x in fall])])
    at = LAST + 0.2 + at * (t - 0.5 - LAST) / at[-1]       # the falling line arrives just as the leaf does
    for i, (m, dur) in enumerate(fall):
        M.add('wind', clar.play(n(m), 70 - 3 * i, dur=at[i + 1] - at[i], release=0.3), at[i], 0.9, -0.1)
    M.add('harp', harp.play(n('F4'), 96), t, 1.0, pan_at(d))
    for i, m in enumerate((n('F2'), n('C3'), n('A3'), n('C4'), n('F4'), n('A4'))):
        M.add('piano', piano.play(m, 70), t + 0.06 * i, 0.8, -0.2 + 0.08 * i)
    M.add('pad', clar.play(n('A4'), 64, dur=2.6, release=0.8), t, 0.8, -0.1)
    M.add('pad', vla.play(n('F3'), 70, dur=2.6, release=0.8), t, 0.9, 0.0)
