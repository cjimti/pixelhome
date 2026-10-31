"""Leaf Fall: Autumn on the roofline, as a quick waltz. Under everything the canopy drifts along the whole house in
leaf colours, flowing with the wind and lifting on every downbeat. Leaves come down on the beats, each a glow that
flutters and flips as it drifts down, sharpening until it lands with a flash; on the roof it skitters with the
breeze into a pile at the nearest corner, and the five corner piles grow into bright many-coloured heaps that
breathe with the waltz. The fall thickens from one leaf a bar to one a beat to two.

A first gust streaks the length of the house and tosses half of every pile on to the next corner. Then a
whirlwind spins up in the porch: the porch piles lift and the leaves whirl round the porch's U faster and faster
in swirling bands, until it collapses and flings them out to the piles at the porch's front corners. The trees let
go: a downpour of leaves on every beat over the whole house, the canopy at its brightest, the piles at their
biggest. Then the wind drops dead for a bar, and the big gust comes: its front runs from the Left corner to the
free end of Right, every pile exploding into a tumbling bundle that rolls ahead of it and bursts out of the end,
wind streaks racing after. In the calm one last leaf swings down on to Porch Front, and where it lands a ripple of
every autumn colour runs out to both ends of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, colormap, nframes

CODE = 'TG03'
TITLE = 'Leaf Fall'
KIND = 'show'
DESCRIPTION = ('Leaves waltz down on the beat and drift into piles at the corners. A gust tosses them, a whirlwind '
               'spins the porch, the trees let go, and one big gust blows every pile out the end of the house.')
VOICEOVER = "The trees are letting go, and the wind wants a dance."

LEAF = [hexc(c) for c in ('#ff8a18', '#d0102a', '#ffb000', '#ff5200', '#c04008', '#ff6a00')]
BROWN = hexc('#5a1c04')
WIND = hexc('#ffe6c8')
GOLD = hexc('#ffaa00')
canopy_map = colormap([(0.0, (1.0, 0.3, 0.02)), (0.2, (0.85, 0.04, 0.06)), (0.4, (1.0, 0.55, 0.0)),
                       (0.6, (0.75, 0.15, 0.01)), (0.8, (1.0, 0.4, 0.0)), (1.0, (1.0, 0.3, 0.02))])

D = 90.0
BEAT = 0.4
BAR = 3 * BEAT                          # a quick waltz, one bar every 1.2 s
CORNERS = np.array([491.0, 894.0, 1311.0, 1660.0, 2033.0])
END = 2512.0
PORCH_MID = (894.0 + 2033.0) / 2
T_GUST1 = 19 * BAR                      # 22.8: a gust from the Left corner to the free end
GUST1_V = 1000.0
T_WHIRL, T_BURST = 38 * BAR, 45.5 * BAR  # 45.6 the whirlwind spins up in the porch; 54.6 it collapses
T_POUR = 46 * BAR                       # 55.2: the trees let go
T_STILL, T_GUST = 57 * BAR, 58 * BAR    # 68.4: the wind drops dead; 69.6: the big gust
GUST_V = 800.0
T_LAST, T_LAND = 67 * BAR, 70 * BAR     # 80.4: the last leaf lets go; 84.0: it lands
SLOT = 6.0


def wind_at(t):
    return keys(t, [(0, 40), (T_GUST1 - 1, 60), (T_GUST1, 250), (T_GUST1 + 2.5, 60), (T_WHIRL, 90), (T_POUR, 150),
                    (T_STILL - 0.4, 150), (T_STILL, 0), (T_GUST, 0), (T_GUST + 0.3, 800), (T_GUST + 4, 500),
                    (T_GUST + 7, 40), (D, 30)])


def leaves(seed=23):
    """Every falling leaf: (landing time on a beat, landing path distance, colour, fall seconds, drift, flip rate).
    The fall thickens: a leaf a bar, then a beat, then two, a downpour, and nothing during the gusts."""
    rng = np.random.default_rng(seed)
    out = []

    def add(t, k):
        for _ in range(k):
            p = rng.uniform(40, END - 40)
            if p < 491 and rng.uniform() < 0.6:          # the front of the house sees most of them
                p = rng.uniform(491, END - 40)
            out.append((float(t), float(p), int(rng.integers(0, len(LEAF))), float(rng.uniform(1.4, 2.4)),
                        float(rng.uniform(-90, 90)), float(rng.uniform(0.7, 1.4))))

    for b in range(2, 10):                  # a leaf on each downbeat
        add(b * BAR, 1)
    for b in range(10, 38):                 # one a beat, two on the downbeats, then more
        for k in range(3):
            t = b * BAR + k * BEAT
            if T_GUST1 - 0.5 <= t < T_GUST1 + 2.5:
                continue
            add(t, 1 + (k == 0 and b >= 22) + (b >= 30 and k == 2))
    for b in range(38, 46):                 # the whirlwind: a few on the porch, drawn in
        t = b * BAR
        out.append((float(t), float(rng.uniform(1000, 1950)), int(rng.integers(0, len(LEAF))), 1.8, 0.0, 1.0))
    for b in range(46, 57):                 # the downpour
        for k in range(3):
            add(b * BAR + k * BEAT, 3 if k == 0 else 2)
    return sorted(out)


def nearest_corner(p):
    return int(np.argmin(np.abs(CORNERS - p)))


def simulate(G, seed=23):
    """The roof, frame by frame: where every landed leaf is and how bright, for render() and score().
    Returns per-frame lists of (position, colour index, kind) with kind 0 skittering, 1 piled, 2 whirling,
    3 in the gust's bundle; and the events [(kind, t, position)]."""
    LV = leaves(seed)
    rng = np.random.default_rng(seed + 1)
    L = len(LV)
    land_t = np.array([l[0] for l in LV])
    land_p = np.array([l[1] for l in LV])
    col = np.array([l[2] for l in LV])
    state = np.zeros(L, int)                # 0 not landed, 1 skitter, 2 pile, 3 whirl, 4 bundle, 5 gone, 6 riding gust 1
    lp = land_p.copy()
    target = np.zeros(L)
    slots = np.zeros((len(CORNERS), 2), int)
    phase = rng.uniform(0, 2 * np.pi, L)
    lag = rng.uniform(0, 120, L)
    ride_to = np.zeros(L)
    events = []
    F = nframes(D)
    frames = []
    omega, burst = 0.0, False

    def to_pile(k, c):
        s = 0 if lp[k] < CORNERS[c] else 1
        target[k] = CORNERS[c] + (-1 if s == 0 else 1) * (4 + SLOT * min(slots[c, s], 34))
        slots[c, s] += 1
        state[k] = 1

    for f in range(F):
        t = f * DT
        w = wind_at(t)
        new = np.where((state == 0) & (land_t <= t))[0]
        for k in new:
            events.append(('land', t, lp[k]))
            if T_WHIRL <= t < T_BURST and 960 < lp[k] < 1970:
                state[k] = 3
            else:
                to_pile(k, nearest_corner(lp[k]))
        sk = state == 1                     # skitter toward the pile slot
        v = np.clip((target - lp) * 1.5, -60 - w * 0.6, 60 + w * 0.6)
        lp[sk] += v[sk] * DT
        settle = sk & (np.abs(target - lp) < 1.0)
        state[settle] = 2
        for k in np.where(settle)[0]:
            events.append(('pile', t, lp[k]))
        # gust 1: its front lifts half of every pile and every skittering leaf on to the next corner downstream
        front1 = 491 + GUST1_V * (t - T_GUST1)
        if T_GUST1 <= t < T_GUST1 + 2.2:
            lift = ((state == 1) | ((state == 2) & (np.arange(L) % 2 == 0))) & (lp <= front1) & (lp >= 491 - 5)
            for k in np.where(lift)[0]:
                down = CORNERS[CORNERS > lp[k] + 20]
                ride_to[k] = down[0] + rng.uniform(-30, 30) if len(down) else END + 40
                state[k] = 6
        ri = state == 6
        lp[ri] = np.minimum(lp[ri] + (GUST1_V * 0.85) * DT, ride_to[ri])
        for k in np.where(ri & (lp >= ride_to - 1))[0]:
            if ride_to[k] > END:
                state[k] = 5
            else:
                to_pile(k, nearest_corner(lp[k]))
        # the whirlwind: porch piles lift and whirl round the porch's U, then fly out to the front corners
        if T_WHIRL <= t < T_BURST:
            omega += (2.0 + 5.0 * smoothstep(T_WHIRL, T_BURST, t)) * DT
            lift = (state == 2) & ((np.abs(lp - 1311) < 120) | (np.abs(lp - 1660) < 120)) & \
                (t > T_WHIRL + 0.6 * (np.arange(L) % 5))
            state[lift] = 3
            if lift.any():
                slots[2:4] = 0
        wh = state == 3
        if wh.any():
            A = 470 * smoothstep(T_WHIRL, T_WHIRL + 2.5, t)
            goal = PORCH_MID + A * np.sin(omega + phase)
            lp[wh] += (goal[wh] - lp[wh]) * min(1, 6 * DT)
        if t >= T_BURST and not burst:
            burst = True
            for k in np.where(state == 3)[0]:
                to_pile(k, 1 if lp[k] < PORCH_MID else 4)
                events.append(('fling', t, lp[k]))
        # the big gust: every leaf on the roof joins the bundle rolling ahead of its front, out the free end
        front = 491 + GUST_V * (t - T_GUST)
        if t >= T_GUST:
            grab = ((state == 1) | (state == 2)) & (lp <= front)
            for k in np.where(grab)[0]:
                events.append(('lift', t, lp[k]))
            state[grab] = 4
            bu = state == 4
            lp[bu] = front - lag[bu] * (0.4 + 0.6 * smoothstep(T_GUST, T_GUST + 2, t))
            gone = bu & (lp > END + 10)
            for k in np.where(gone)[0]:
                events.append(('gone', t, END))
            state[gone] = 5
        on = np.where((state >= 1) & (state <= 4) | (state == 6))[0]
        kind = np.select([state[on] == 1, state[on] == 2, state[on] == 3, state[on] == 6], [0, 1, 2, 3], 3)
        frames.append((lp[on].copy(), col[on].copy(), kind, land_t[on].copy(), phase[on].copy()))
    return LV, frames, events


def render(G, seed=23):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    rng = np.random.default_rng(seed + 7)
    rustle = Flicker(rng, 600, 0.6, 2.0)
    shimmer = Flicker(rng, n, 0.3, 1.2)
    LV, frames, events = simulate(G, seed)
    lcol = np.array(LEAF)
    windpos = np.cumsum([wind_at(f * DT) * DT for f in range(F)])
    PORCH = (pdp > 894) & (pdp < 2033)

    for f in range(F):
        t = f * DT
        buf = light(BROWN, keys(t, [(0, 0), (1.5, 0.07), (87, 0.07), (90, 0)]) * np.ones(n))
        down = np.exp(-((t + 1e-6) % BAR) / 0.18)
        beat = np.exp(-((t + 1e-6) % BEAT) / 0.12)
        still = smoothstep(T_STILL, T_STILL + 0.3, t) * (1 - smoothstep(T_GUST, T_GUST + 0.1, t))

        # the canopy: leaf colours drifting with the wind, lifting on each downbeat
        lvl = keys(t, [(0, 0), (2.4, 0.45), (T_POUR - 2, 0.5), (T_POUR, 0.6), (T_STILL, 0.6), (T_GUST, 0.4),
                       (T_GUST + 3, 0.15), (T_GUST + 6, 0.4), (T_LAND, 0.4), (89, 0.3), (90, 0)])
        cpos = (pdp - windpos[f]) / 520
        cc = canopy_map(cpos % 1.0)
        bands = (0.5 + 0.5 * np.cos(2 * np.pi * cpos * 2.5)) ** 2
        ci = lvl * (0.3 + 0.55 * bands + 0.15 * shimmer(t) + 0.4 * down * (1 - still))
        buf += cc * (np.clip(ci, 0, None) ** 2.2)[:, None]

        # falling leaves: a glow that flutters, flips and sharpens as it drifts down to land on the beat
        for (tl, p, c, fd, drift, flip) in LV:
            u = (t - (tl - fd)) / fd
            if not 0 <= u < 1:
                continue
            x = p - drift * (1 - u) + 25 * np.sin(2 * np.pi * flip * t + p) * (1 - u)
            face = 0.35 + 0.65 * np.cos(np.pi * flip * (t - tl + fd)) ** 2
            wdt = 30 - 22 * u
            I = (0.2 + 0.8 * u * u) * face * 0.95
            buf += light(lcol[c], I * np.exp(-((pdp - x) / wdt) ** 2))

        # on the roof: skittering leaves, the piles (breathing on the downbeat), the whirl and the bundle
        lp, cl, kind, lt, ph = frames[f]
        if len(lp):
            age = t - lt
            flash = np.exp(-np.clip(age, 0, None) / 0.18) * (age >= 0)
            rs = rustle(t)[np.arange(len(lp)) % 600]
            amp = np.select([kind == 0, kind == 1, kind == 2, kind == 3],
                            [0.8, 0.8 * (1 + 0.3 * down), 0.95, 1.0], 1.0) * (1 + 0.1 * rs) + 0.6 * flash
            wid = np.select([kind == 1, kind == 2, kind == 3], [5.0, 7.0, 8.0], 5.0)
            jig = np.where(kind == 3, 18 * np.sin(9 * t + ph), 0) + np.where(kind == 2, 0, 1.5 * rs)
            I = amp[:, None] * np.exp(-((pdp[None, :] - (lp + jig)[:, None]) / wid[:, None]) ** 2)
            buf += np.einsum('ln,lc->nc', np.clip(I, 0, None) ** 2.2, lcol[cl])
            fl = flash[:, None] * np.exp(-((pdp[None, :] - lp[:, None]) / 14) ** 2)
            buf += np.einsum('ln,c->nc', np.clip(0.7 * fl, 0, None) ** 2.2, WIND)

        # gust 1: a white streak running the length of the house
        if T_GUST1 <= t < T_GUST1 + 2.6:
            fr = 491 + GUST1_V * (t - T_GUST1)
            streak = np.exp(-np.clip(fr - pdp, 0, None) / 160) * (pdp <= fr) * (pdp >= 300)
            buf += light(WIND, 0.55 * streak * (1 - smoothstep(T_GUST1 + 2.0, T_GUST1 + 2.6, t)))

        # the whirlwind: bands swirling round the porch, faster as it spins up, a flash as it bursts
        if T_WHIRL <= t < T_BURST + 1.5:
            spin = smoothstep(T_WHIRL, T_WHIRL + 2, t) * (1 - smoothstep(T_BURST, T_BURST + 0.8, t))
            sp = (t - T_WHIRL) * (1.5 + 2.5 * smoothstep(T_WHIRL, T_BURST, t))
            band = (0.5 + 0.5 * np.cos(2 * np.pi * ((pdp - 894) / 190 - sp))) ** 3
            buf += canopy_map(((pdp - 894) / 600 + 0.3 * t) % 1.0) * \
                (np.clip(spin * (0.25 + 0.4 * band + 0.2 * beat), 0, None) ** 2.2 * PORCH)[:, None]
            u = t - T_BURST
            if u >= 0:
                buf += light(WIND, 0.8 * np.exp(-u / 0.2) * PORCH)
                ring = np.exp(-((np.abs(pdp - PORCH_MID) - 1100 * u) / 50) ** 2) * np.exp(-u / 0.6)
                buf += light(GOLD, 0.7 * ring)

        # the big gust: streaks racing after the front, a burst out of the free end
        if t >= T_GUST:
            fr = 491 + GUST_V * (t - T_GUST)
            fade = 1 - smoothstep(T_GUST + 4, T_GUST + 6.5, t)
            streaks = (0.5 + 0.5 * np.cos(2 * np.pi * (pdp / 140 - (t - T_GUST) * 6))) ** 4
            behind = np.clip((fr - pdp) / 40, 0, 1)
            buf += light(WIND, 0.3 * streaks * behind * fade)
            buf += light(WIND, 0.8 * np.exp(-((pdp - fr) / 30) ** 2) * (fr < END + 30))
            side = (pdp < 491) * smoothstep(T_GUST, T_GUST + 0.3, t)     # Side's air pours toward the corner
            buf += light(WIND, 0.3 * streaks * side * fade)
            te = T_GUST + (END - 491) / GUST_V
            if t >= te:
                u = t - te
                buf += light(GOLD, np.exp(-u / 0.35) * np.exp(-((END - pdp) / 260) ** 2))
                for k in range(8):          # leaves spraying back from the end as it bursts
                    p = END - (200 + 90 * k) * (1 - np.exp(-u / 0.4))
                    buf += light(LEAF[k % len(LEAF)], 0.8 * np.exp(-u / 0.6) * np.exp(-((pdp - p) / 8) ** 2))

        # the last leaf: a big one swinging down on to Porch Front; where it lands, a ripple to both ends
        if T_LAST <= t:
            u = (t - T_LAST) / (T_LAND - T_LAST)
            if u < 1:
                swing = 150 * (1 - u) * np.sin(2 * np.pi * u * 2.5)
                x = 1486 + swing
                face = 0.4 + 0.6 * np.cos(2 * np.pi * u * 5) ** 2
                buf += light(LEAF[2], (0.4 + 0.65 * u * u) * face * np.exp(-((pdp - x) / (55 - 40 * u)) ** 2))
            else:
                v = t - T_LAND
                fade = keys(t, [(T_LAND, 1), (87, 1), (90, 0)])
                buf += light(LEAF[2], (0.9 * np.exp(-v / 0.3) + 0.65) * np.exp(-((pdp - 1486) / 7) ** 2) * fade)
                ab = np.abs(pdp - 1486)
                for k in range(4):          # rings of every autumn colour, one a beat
                    vk = v - BEAT * k
                    if vk >= 0:
                        ring = np.exp(-((ab - 900 * vk) / 90) ** 2) * np.exp(-vk / 1.6)
                        buf += light(LEAF[(k * 2) % len(LEAF)], ring)
                glow = np.clip((900 * v - ab) / 300, 0, 1) * (0.32 + 0.08 * shimmer(t))
                buf += canopy_map((pdp / 700 + 0.1 * t) % 1.0) * (np.clip(glow * fade, 0, None) ** 2.2)[:, None]
        out[f][G.path] = buf
    return np.clip(out, 0, 1, out=out)


# ---------------------------------------------------------------- music ----------------------------------------------
# A quick fiddle waltz in G, a bar every 1.2 s, its downbeat the canopy's lift: pizzicato bass on one, harp and
# banjo on two and three, the fiddle's tune and a clarinet answering. Every leaf that lands plucks the chord of the
# moment on harp, higher the further right it lands; leaves settling into piles tap the marimba. Gust one is a
# whoosh and a flute run left to right; the whirlwind swirls marimba arpeggios up and down round the porch over
# tremolo strings and bursts on a cymbal; the downpour brings in horns, glockenspiel and the whole band. The wind
# drops dead for a bar, the big gust rolls in on timpani and crashes, a harp shower spills out of the free end, and
# in the calm the fiddle plays alone until the last leaf's falling clarinet lands on a golden chord, the ripple a
# harp glissando out to both ends.

CH = {'G': (43, (55, 59, 62)), 'C': (48, (55, 60, 64)), 'D7': (50, (54, 57, 60)), 'Em': (40, (55, 59, 64)),
      'Am': (45, (57, 60, 64)), 'D': (50, (54, 57, 62))}
TUNE_A = [(0, 'D5', 2), (2, 'B4', 1), (3, 'G4', 2), (5, 'B4', 1), (6, 'C5', 1), (7, 'E5', 1), (8, 'G5', 1),
          (9, 'D5', 3), (12, 'E5', 2), (14, 'C5', 1), (15, 'A4', 2), (17, 'C5', 1), (18, 'B4', 1), (19, 'A4', 1),
          (20, 'F#4', 1), (21, 'G4', 3)]
TUNE_B = [(0, 'G5', 2), (2, 'F#5', 1), (3, 'E5', 2), (5, 'B4', 1), (6, 'C5', 1), (7, 'D5', 1), (8, 'E5', 1),
          (9, 'D5', 3), (12, 'A4', 2), (14, 'B4', 1), (15, 'C5', 2), (17, 'E5', 1), (18, 'D5', 1), (19, 'C5', 1),
          (20, 'A4', 1), (21, 'G4', 3)]
CH_A = ['G', 'G', 'C', 'G', 'C', 'Am', 'D7', 'G']
CH_B = ['Em', 'Em', 'C', 'G', 'Am', 'C', 'D7', 'G']
# the form, by bar: which phrase's chords, and from which bar it starts
FORM = [(0, 'G'), (2, CH_A), (10, CH_B), (18, ['G', 'C', 'G', 'D7']), (22, CH_A), (30, CH_B),
        (38, ['Em', 'Em', 'Am', 'Am', 'C', 'C', 'D', 'D7']), (46, CH_A), (54, ['C', 'Am', 'D7']), (57, None),
        (58, ['G', 'C', 'G', 'D7', 'G']), (63, CH_A[:4]), (67, ['C', 'Am', 'D7']), (70, 'G')]


def chord_at(b):
    """Chord name for bar b, or None in the bar of stillness."""
    for start, ch in reversed(FORM):
        if b >= start:
            if ch is None:
                return None
            return ch if isinstance(ch, str) else ch[min(b - start, len(ch) - 1) if len(ch) < 8 else (b - start) % 8]
    return 'G'


def score(M, G):
    from pixelhome.audio import note, whoosh
    n = note
    LV, frames, events = simulate(G)
    fid = M.sampler('Strings/Solo Violin/Arco Vib/*.wav')    # labelled at pitch
    harp = M.sampler('Strings/Harp/*.wav')
    banjo = M.sampler('Strings/Solo Violin/Pizz/*.wav')
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    flute_s = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    cswell = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    tri = M.hits('VSCO 1 Percussion/varMetal/triangle/1/triangle1_hit_mp*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    shake = M.hits('Percussion/Tamb1-Shake*.wav')

    for name, gain, rev in (('fiddle', 0.5, 0.22), ('wind', 0.4, 0.25), ('harp', 0.42, 0.3), ('banjo', 0.5, 0.15),
                            ('bass', 0.6, 0.08), ('leaf', 0.32, 0.3), ('mallet', 0.4, 0.22), ('brass', 0.4, 0.25),
                            ('strings', 0.32, 0.3), ('drums', 0.55, 0.2), ('fx', 0.45, 0.25)):
        M.bus(name, gain=0.6 * gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def travel(sig, d0, d1):
        a = (np.linspace(pan_at(d0), pan_at(d1), sig.shape[1]) + 1) * np.pi / 4
        return sig * np.sqrt(2) * np.vstack([np.cos(a), np.sin(a)])

    def tones(c, lo, hi):
        pcs = {m % 12 for m in CH[c][1]} | {CH[c][0] % 12}
        return [m for m in range(lo, hi + 1) if m % 12 in pcs]

    def tune(b0, phrase, inst, bus, vel, shift=0, gain=1.0, pan=-0.05):
        for b, m, d in phrase:
            M.add(bus, inst.play(n(m) + shift, vel, dur=d * BEAT * 0.95, release=0.25), b0 * BAR + b * BEAT, gain, pan)

    # ---- the waltz: bass on one, harp and banjo on two and three ----
    for b in range(1, 75):
        c = chord_at(b)
        if c is None or T_LAST <= b * BAR < T_LAND:
            continue
        t = b * BAR
        root, ch = CH[c]
        big = 1.0 + 0.3 * (T_POUR <= t < T_STILL) + 0.2 * (T_GUST <= t < T_GUST + 5)
        soft = 0.6 if (T_GUST + 6 <= t < T_LAST) or t >= T_LAND + 1 else 1.0
        M.add('bass', bass.play(root + (7 if b % 2 else 0), int(96 * soft)), t, big, -0.1)
        for k in (1, 2):
            for m in ch:
                M.add('banjo', banjo.play(m + 12, int((70 + 8 * (k == 1)) * soft)), t + k * BEAT, 0.5 * big, 0.15)
                M.add('harp', harp.play(m, int(60 * soft)), t + k * BEAT, 0.4 * big, -0.15)
        if T_GUST1 + 3 <= t < T_STILL:
            M.add('drums', tamb.play(70), t + BEAT, 0.35, 0.3)
            M.add('drums', tamb.play(60), t + 2 * BEAT, 0.3, 0.3)

    # ---- the tune ----
    for i, m in enumerate(('G3', 'B3', 'D4', 'G4', 'B4', 'D5')):
        M.add('harp', harp.play(n(m), 70 + 4 * i), 0.3 + 0.12 * i, 0.9, -0.5 + 0.2 * i)
    tune(2, TUNE_A, fid, 'fiddle', 92)
    tune(10, TUNE_B, fid, 'fiddle', 96)
    tune(22, TUNE_A, fid, 'fiddle', 100)
    tune(22, TUNE_A, clar, 'wind', 70, shift=-12, gain=0.7)
    tune(30, TUNE_B, fid, 'fiddle', 102)
    tune(30, TUNE_B, flute_s, 'wind', 72, gain=0.6)
    tune(46, TUNE_A, fid, 'fiddle', 108)
    tune(46, TUNE_A, tpt, 'brass', 96, shift=-12, gain=0.8)
    tune(46, TUNE_A, horn, 'brass', 90, shift=-24, gain=0.6)
    tune(63, TUNE_A[:8], fid, 'fiddle', 78)

    # ---- every leaf that lands: the chord of the moment on harp, higher further right; piles tap the marimba ----
    for kind, t, d in events:
        b = int(t // BAR)
        c = chord_at(b) or 'G'
        if kind == 'land' and abs(t - T_LAND) > 0.1:
            tt = tones(c, n('D4'), n('D6'))
            m = tt[int(round((pan_at(d) / 0.85 + 1) / 2 * (len(tt) - 1)))]
            M.add('leaf', harp.play(m, 92 + int(M.rng.integers(-10, 10))), t, 0.8, pan_at(d))
        elif kind == 'pile' and t < T_GUST:
            M.add('mallet', mar.play(int(M.rng.choice(tones(c, n('G3'), n('D5')))), 55), t, 0.5, pan_at(d))

    # ---- gust one: a whoosh and a flute run, left to right ----
    M.add('fx', travel(whoosh(2.4, 300, 2600, 0.8, seed=31), 491, END), T_GUST1, 1.0)
    run = [m for m in range(n('G4'), n('G6')) if m % 12 in (7, 9, 11, 0, 2, 4, 6)]
    for i, m in enumerate(run):
        M.add('wind', flute.play(m, 90), T_GUST1 + 0.12 * i, 0.9, pan_at(491 + (END - 491) * i / len(run)))
    M.add('drums', cswell.play(80, dur=1.5), T_GUST1 - 1.2, 0.5)

    # ---- the whirlwind: marimba arpeggios round the porch, tremolo rising, a cymbal as it bursts ----
    t = T_WHIRL
    i = 0
    while t < T_BURST:
        c = chord_at(int(t // BAR)) or 'Em'
        arp = tones(c, n('E4'), n('E6'))
        k = i % (2 * len(arp) - 2)
        m = arp[k if k < len(arp) else 2 * len(arp) - 2 - k]
        x = PORCH_MID + 470 * np.sin(i * 0.6)
        M.add('mallet', mar.play(m, 80 + int(30 * smoothstep(T_WHIRL, T_BURST, t))), t, 0.8, pan_at(x))
        i += 1
        t += BEAT / 2 if t < T_WHIRL + 4 * BAR else BEAT / 4
    for j, tt in enumerate(np.arange(T_WHIRL, T_BURST, BAR)):
        c = chord_at(int(tt // BAR)) or 'Em'
        M.add('strings', trem.play(CH[c][1][0] + 12 + j, 60 + 6 * j, dur=BAR, release=0.05), tt, 1.0, pan_at(PORCH_MID))
    M.add('fx', whoosh(T_BURST - T_WHIRL, 200, 1500, 0.4, seed=40), T_WHIRL, 0.6, pan_at(PORCH_MID))
    M.add('drums', crash.play(115), T_BURST, 0.8, pan_at(PORCH_MID))
    M.add('drums', timp.play(115), T_BURST, 0.8, pan_at(PORCH_MID))
    for sgn in (-1, 1):
        M.add('fx', travel(whoosh(0.8, 2500, 400, 0.6, seed=41 + sgn), PORCH_MID, PORCH_MID + sgn * 560), T_BURST, 0.9)

    # ---- the downpour: shimmer and glockenspiel on every beat ----
    for tt in np.arange(T_POUR, T_STILL, BEAT):
        c = chord_at(int(tt // BAR)) or 'G'
        M.add('mallet', glock.play(int(M.rng.choice(tones(c, n('G5'), n('E6')))), 70), tt, 0.5, 0.0)
        M.add('drums', shake.play(55), tt, 0.3, 0.2)

    # ---- the stillness, then the big gust ----
    M.add('drums', troll.play(80, dur=BAR), T_STILL, 0.5, -0.6)
    M.add('drums', crash.play(124), T_GUST, 1.0, -0.6)
    M.add('drums', timp.play(124), T_GUST, 1.0, -0.6)
    seg = 1.2
    te = T_GUST + (END - 491) / GUST_V
    for i, ts in enumerate(np.arange(T_GUST - 0.2, te + 0.4, seg / 2)):
        d = np.clip(491 + (ts + seg / 2 - T_GUST) * GUST_V, 0, END)
        M.add('fx', whoosh(seg, 250, 3200, 0.9, seed=60 + i), ts, 1.0, pan_at(d))
    for j, cd in enumerate(CORNERS):
        tc = T_GUST + max(0, cd - 491) / GUST_V
        for i, m in enumerate(tones('G', n('G3') + 2 * j, n('G5') + 2 * j)[:6]):
            M.add('harp', harp.play(m, 96), tc + 0.04 * i, 0.8, pan_at(cd + 30 * i))
        M.add('drums', timp.play(100 + 4 * j, pitch=j), tc, 0.6, pan_at(cd))
    M.add('drums', crash.play(118), te, 0.8, 0.85)
    shower = tones('G', n('D4'), n('D6'))[::-1]
    for i in range(len(shower)):
        M.add('harp', harp.play(shower[i], 92 - 2 * i), te + 0.07 * i, 0.8, 0.85)
    for m in (n('G3'), n('B3'), n('D4'), n('G4')):
        M.add('brass', horn.play(m, 100, dur=2.4, release=0.8), T_GUST, 0.6)
        M.add('strings', vln.play(m + 12, 96, dur=2.4, release=0.8), T_GUST, 0.6)
    M.add('fx', whoosh(3.0, 1500, 250, 0.6, seed=99), te, 0.8, 0.85)

    # ---- the last leaf: a falling clarinet, a golden chord, the ripple on harp to both ends ----
    fall = (('D5', 2), ('C5', 1), ('B4', 2), ('A4', 1), ('G4', 2), ('F#4', 1), ('E4', 2), ('D4', 1))
    tt = T_LAST
    for m, d in fall:
        M.add('wind', clar.play(n(m), 76, dur=d * BEAT * 0.98, release=0.3), tt, 0.9, pan_at(1486))
        tt += d * BEAT
    M.add('strings', cello.play(n('D3'), 60, dur=T_LAND - T_LAST, release=0.3), T_LAST, 0.7)
    M.add('leaf', harp.play(n('G4'), 104), T_LAND, 1.2, pan_at(1486))
    M.add('drums', tri.play(90), T_LAND, 0.6)
    hold = D - T_LAND - 1.5
    for m, inst, bus, v in ((n('G2'), cello, 'strings', 80), (n('D3'), cello, 'strings', 72), (n('B3'), horn, 'brass', 80),
                            (n('G4'), vln, 'strings', 76), (n('D4'), clar, 'wind', 70)):
        M.add(bus, inst.play(m, v, dur=hold, release=1.5), T_LAND, 1.0)
    gl = tones('G', n('G3'), n('G6'))
    for i, m in enumerate(gl):
        for sgn in (-1, 1):
            M.add('harp', harp.play(m, 84), T_LAND + 0.08 * i, 0.45, pan_at(1486 + sgn * 900 * 0.08 * i))
    M.add('mallet', glock.play(n('D6'), 80), T_LAND + 1.0, 0.6)
    M.add('mallet', glock.play(n('G5'), 70), T_LAND + 2.2, 0.6)
