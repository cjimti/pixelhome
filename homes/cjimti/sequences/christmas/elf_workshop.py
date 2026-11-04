"""Elf Workshop: The roofline is a conveyor belt running from the free end of Right round to the front-left
corner, its rollers ticking past in steel blue. An elf pops up at every corner and the belt whirs into motion.
Parts come in at the free end of Right on the beat; at the first corner an elf hammers each one into a toy
(an orange spark), at the top of the Porch Right another paints it (a splash of its new colour), at the far
corner of the Porch Front another wraps it in red, green, gold or blue paper with a white ribbon, and at the foot
of the Porch Left the last one ties a gold bow on. The parcels stack up at the front-left corner, and every
dozen the gate opens and they whoosh down the Side into the sleigh at the back with a bell. The music speeds
up and the belt with it, parts coming in on every beat, faster and faster: the wrapper can't keep up, unwrapped
toys bunch up along the Porch Front, a red beacon flashes, the queue backs up nearly to the paint corner. The
boss elf pops up over the jam and pulls the lever: everything stops dead. A breath; a whistle; the belt starts
again at a cheerful pace, the wrapper clears the backlog in a flurry, the last parcels ride round, and the whole
lot whooshes to the sleigh. Then the elves wrap the house itself: red paper with gold ribbon rolls from the
free end of Right all the way round to the back of the Side, a gold bow pops on the porch, and the sleigh
bells ring.

Music: an original workshop polka in F major whose tempo is the belt's: 120 bpm, then an accelerando to 170 as
the belt speeds up, a dead stop at the lever and a fresh start at 132. Every part on the belt is a tick of the
wood block when it comes in, an anvil when it is hammered, a soft splash and a glockenspiel note when it is
painted, a rustle and a harp pluck when it is wrapped, a triangle when the bow goes on; each batch to the sleigh
is a whoosh and sleigh bells, panned along the Side. The jam has a two-tone muted-trumpet alarm; the lever is a
ratchet and a clunk into silence; the restart is the boss's whistle. The finale plays the polka in full,
a harp glissando and swelling strings follow the paper round the house, and the bow lands on a cymbal and
the last chord."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'CH13'
TITLE = 'Elf Workshop'
KIND = 'show'
DESCRIPTION = ('The roof is a conveyor belt: elves at every corner hammer, paint and wrap toys until it runs too fast '
               'and jams. The boss pulls the lever, and the parcels whoosh off to the sleigh.')
VOICEOVER = "The big night is coming, the orders are in, and the elves are about to fall behind."

BELT = hexc('#4a62b0')
NIGHT = hexc('#0c1660')
PART = hexc('#d0c0a8')
WOOD = hexc('#ff9a40')
TOYS = [hexc(c) for c in ('#ff1a1a', '#1a50ff', '#10d040', '#ffd010', '#c020ff')]
PAPER = [hexc(c) for c in ('#ff1010', '#08c830', '#ffb000', '#1840ff')]
RIBBON = hexc('#fff4e8')
GOLD = hexc('#ffb818')
ELF = hexc('#18e040')
HAT = hexc('#ff1020')
SPARK = hexc('#ffa030')
ALARM = hexc('#ff0800')
SLEIGH = hexc('#ff2010')

D = 86.0
SEED = 61
T_BELT = 2.0                                      # the belt starts
T_ACCEL, T_TOP = 28.0, 46.4                       # the accelerando: 120 -> 170 bpm
BPM0, BPM1, BPM2 = 120.0, 170.0, 132.0
V0 = 112.0                                        # belt speed at 120 bpm, units/s
V2 = 165.0                                        # belt speed after the restart
GAP_Q, GAP_D = 20.0, 13.0                         # spacing in the wrapping queue and in the stack at the dock
DOCK_N = 12                                       # a batch for the sleigh
CHUTE_V = 950.0
WRAP_SLOW = 0.5                                   # how long the wrapper takes, before the jam


def bpm(t):
    return BPM0 + (BPM1 - BPM0) * float(np.clip((t - T_ACCEL) / (T_TOP - T_ACCEL), 0, 1))


def tempo_map():
    """Beat times: 120 bpm, the accelerando, the lever on the first beat after the top, then the restart at 132."""
    A, t = [], 0.0
    while t < T_TOP:
        A.append(t)
        t += 60.0 / bpm(t)
    lever = t
    restart = lever + 2.0
    B = list(restart + np.arange(0, (D - restart) / (60 / BPM2)) * 60 / BPM2)
    return np.array(A), lever, restart, np.array(B)


BEATS_A, T_LEVER, T_RESTART, BEATS_B = tempo_map()
T_BOSS = float(BEATS_A[-4])                       # the boss elf pops up over the jam
RB = 60 / BPM2                                    # a beat after the restart
T_LAST_IN = T_RESTART + 16 * RB                   # the last part comes in
T_SHIP = T_RESTART + 48 * RB                      # the last batch goes to the sleigh
T_WRAP0 = T_RESTART + 52 * RB                     # the elves wrap the house
T_WRAP1 = T_RESTART + 64 * RB
T_BOW = T_RESTART + 68 * RB
T_FINAL = T_RESTART + 78 * RB


def geom(G):
    x = G.pd[G.path]
    c = [float((x[i] + x[i + 1]) / 2) for i in (80, 178, 260, 331, 380)]
    return dict(c1=c[0], c2=c[1], c3=c[2], c4=c[3], c5=c[4], L=float(G.length))


def entries():
    """When each part comes in: every other beat, then every beat as the tempo climbs; after the restart every
    other beat again."""
    A = BEATS_A
    out = [A[k] for k in range(len(A)) if A[k] >= T_BELT + 0.5 and A[k] < 22.0 and k % 2 == 0]
    out += [A[k] for k in range(len(A)) if 22.0 <= A[k] < T_LEVER - 1.0]
    out += [b for k, b in enumerate(BEATS_B) if T_RESTART + 1 < b <= T_LAST_IN and k % 2 == 0]
    return np.array(out)


def belt_v(t):
    if t < T_BELT:
        return 0.0
    if t < T_LEVER:
        return V0 * bpm(t) / BPM0 * float(smoothstep(T_BELT, T_BELT + 0.8, t))
    if t < T_RESTART:
        return 0.0
    return V2 * float(smoothstep(T_RESTART, T_RESTART + 0.3, t))


def wrap_time(t):
    return WRAP_SLOW if t < T_LEVER else 0.08


def simulate(G, seed=SEED):
    """Run the workshop frame by frame: positions and stages of every item, the belt's travel, and every event
    (hammer, paint, wrap, bow, ship, sleigh) with its time and place."""
    rng = np.random.default_rng(seed)
    g = geom(G)
    c1, c2, c3, c4, c5, L = (g[k] for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'L'))
    F = nframes(D)
    ent = entries()
    ni = len(ent)
    toy = rng.integers(0, len(TOYS), ni)
    paper = rng.integers(0, len(PAPER), ni)
    pos = np.full(ni, np.nan)
    st = np.zeros(ni, int)            # 0 not in, 1 belt, 2 queued/wrapping, 3 dock, 4 chute, 5 gone
    done = np.zeros(ni, int)          # 0 part, 1 toy, 2 painted, 3 wrapped, 4 bowed
    P = np.full((F, ni), np.nan)
    S = np.zeros((F, ni), int)
    belt = np.zeros(F)
    qlen = np.zeros(F, int)
    ev = []
    queue, dock = [], []
    wrap_end = -1.0
    s = 0.0
    for f in range(F):
        t = f * DT
        v = belt_v(t)
        s += v * DT
        belt[f] = s
        for i in np.where((ent <= t) & (st == 0))[0]:
            st[i], pos[i] = 1, L + 6
        moving = v > 0

        def move(i, p1):
            p0 = pos[i]
            if done[i] == 0 and p0 > c5 >= p1:
                done[i] = 1
                ev.append(('hammer', t, c5, i))
            if done[i] == 1 and p0 > c4 >= p1:
                done[i] = 2
                ev.append(('paint', t, c4, i))
            if done[i] == 3 and p0 > c2 >= p1:
                done[i] = 4
                ev.append(('bow', t, c2, i))
            pos[i] = p1

        if moving:
            # the wrapping station: finish the one in hand, take the next when it reaches the corner
            if queue and wrap_end >= 0 and t >= wrap_end:
                i = queue.pop(0)
                done[i], st[i] = 3, 1
                pos[i] = c3 - 1
                ev.append(('wrap', t, c3, i))
                wrap_end = -1.0
            for k, i in enumerate(queue):                          # the queue shuffles forward to its slots
                move(i, max(c3 + GAP_Q * k, pos[i] - max(v, 320.0) * DT))
            if queue and wrap_end < 0 and pos[queue[0]] <= c3 + 0.5:
                wrap_end = t + wrap_time(t)
            for k, i in enumerate(dock):
                pos[i] = max(c1 + 8 + GAP_D * k, pos[i] - v * DT)
            for i in np.where(st == 1)[0]:
                p1 = pos[i] - v * DT
                if done[i] < 3 and p1 <= c3 + GAP_Q * len(queue):
                    p1 = max(p1, c3 + GAP_Q * len(queue))
                    queue.append(i)
                    st[i] = 2
                    if len(queue) == 1 and wrap_end < 0 and p1 <= c3 + 0.5:
                        wrap_end = t + wrap_time(t)
                elif done[i] == 4 and p1 <= c1 + 8 + GAP_D * len(dock):
                    p1 = c1 + 8 + GAP_D * len(dock)
                    dock.append(i)
                    st[i] = 3
                    ev.append(('dock', t, p1, i))
                move(i, p1)
        # a batch for the sleigh: on a beat, when the stack is full (or the last one)
        on_beat = np.any(np.abs(np.concatenate([BEATS_A, BEATS_B]) - t) < DT / 2)
        if dock and moving and on_beat and (len(dock) >= DOCK_N or abs(t - T_SHIP) < DT / 2):
            for i in dock:
                st[i] = 4
            ev.append(('ship', t, c1, list(dock)))
            dock = []
        for i in np.where(st == 4)[0]:
            pos[i] -= CHUTE_V * DT
            if pos[i] < 0:
                st[i] = 5
                if not any(e[0] == 'sleigh' and abs(e[1] - t) < 0.3 for e in ev):
                    ev.append(('sleigh', t, 0.0, i))
        P[f] = np.where((st >= 1) & (st <= 4), pos, np.nan)
        S[f] = done
        qlen[f] = len(queue)
    return dict(g=g, ent=ent, toy=toy, paper=paper, P=P, S=S, belt=belt, qlen=qlen, ev=ev, ni=ni)


def render(G, seed=SEED):
    W = simulate(G, seed)
    g, P, S, belt, qlen, ev, toy, paper = (W[k] for k in ('g', 'P', 'S', 'belt', 'qlen', 'ev', 'toy', 'paper'))
    c1, c2, c3, c4, c5, L = (g[k] for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'L'))
    rng = np.random.default_rng(seed + 1)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    n = G.N
    side_m = d < c1
    flake = Flicker(rng, n, 0.2, 0.8)
    stations = [(c5, SPARK), (c4, TOYS[3]), (c3, GOLD), (c2, RIBBON)]
    pops = list(BEATS_A[1:5] - 0.1)
    toy_c, paper_c = np.array(TOYS)[toy], np.array(PAPER)[paper]
    evs = {k: [e for e in ev if e[0] == k] for k in ('hammer', 'paint', 'wrap', 'bow', 'ship', 'sleigh', 'dock')}

    def dot(x, c, lvl, w):
        return light(c, lvl * np.exp(-((d - x) / w) ** 2))

    for f in range(F):
        t = f * DT
        master = keys(t, [(0, 0), (0.6, 1), (D - 1.5, 1), (D, 0)])
        stopped = T_LEVER <= t < T_RESTART
        buf = light(NIGHT, 0.14 * np.ones(n))
        wrapped = 0.0 if t < T_WRAP0 else 1.0

        # the belt: rollers ticking past, steel blue, on every run but the Side (the chute to the sleigh)
        ph = (d + belt[f]) % 34
        roll = np.where(ph < 12, 1.0, 0.0) * (~side_m)
        buf += light(BELT, 0.3 * roll * smoothstep(0.2, 1.2, t) * (1 - wrapped))
        buf += light(NIGHT, 0.1 * side_m) + light(RIBBON, 0.6 * np.clip(flake(t) - 1.6, 0, None) * side_m)
        # the sleigh, waiting at the back of the Side
        bell = sum(np.exp(-max(0.0, t - e[1]) / 0.4) for e in evs['sleigh'] if e[1] <= t)
        buf += dot(14, SLEIGH, 0.55 + 0.4 * min(1.0, bell), 14) + dot(14, GOLD, 0.6 * min(1.0, bell), 26)

        # the stations: an elf with a red hat at every corner, a lamp in the station's colour
        for k, (x, colr) in enumerate(stations):
            up = smoothstep(pops[k], pops[k] + 0.25, t)
            frantic = 0.0
            if not stopped:
                last = [e[1] for e in evs[('hammer', 'paint', 'wrap', 'bow')[k]] if e[1] <= t]
                if last:
                    a = t - last[-1]
                    frantic = np.exp(-a / 0.12)
            bounce = 0.0 if stopped else 0.2 * frantic
            buf += dot(x + 16, ELF, (0.7 + 0.3 * frantic) * up * (1 - 0.5 * wrapped), 6) + dot(x + 24, HAT, 0.8 * up * (1 - 0.5 * wrapped), 4)
            buf += dot(x, colr, (0.22 + bounce) * up * (1 - wrapped), 18)
        # the dock: an elf counting parcels at the front-left corner
        buf += dot(c1 - 10, ELF, 0.7 * smoothstep(T_BELT - 0.1, T_BELT + 0.15, t), 6) + dot(c1 - 18, HAT, 0.8 * smoothstep(T_BELT - 0.1, T_BELT + 0.15, t), 4)

        # station actions: hammer sparks, splashes of paint, a gold swirl of paper, a bow's glint
        for e in evs['hammer']:
            a = t - e[1]
            if 0 <= a < 0.35:
                buf += dot(c5, RIBBON, np.exp(-a / 0.05), 8) + dot(c5, SPARK, 0.9 * np.exp(-a / 0.12), 22 + 60 * a)
        for e in evs['paint']:
            a = t - e[1]
            if 0 <= a < 0.45:
                buf += dot(c4 - 8, toy_c[e[3]], 0.95 * np.exp(-a / 0.15), 16 + 50 * a)
        for e in evs['wrap']:
            a = t - e[1]
            if 0 <= a < 0.4:
                buf += dot(c3, paper_c[e[3]], 0.9 * np.exp(-a / 0.12), 18) + dot(c3, GOLD, 0.6 * np.exp(-a / 0.08), 30)
        for e in evs['bow']:
            a = t - e[1]
            if 0 <= a < 0.4:
                buf += dot(c2, GOLD, np.exp(-a / 0.1), 10)

        # the items
        p = P[f]
        live = ~np.isnan(p)
        if live.any():
            idx = np.where(live)[0]
            xs = p[idx]
            stg = S[f][idx]
            col = np.where((stg == 0)[:, None], PART, np.where((stg == 1)[:, None], WOOD, toy_c[idx]))
            col = np.where((stg >= 3)[:, None], paper_c[idx], col)
            lvl = np.select([stg == 0, stg == 1, stg == 2], [0.7, 0.8, 0.9], 0.9)
            wid = np.where(stg >= 3, 9.0, np.where(stg == 0, 5.5, 7.0))
            near = np.abs(d[:, None] - xs[None]) < 30
            K = np.where(near, np.exp(-((d[:, None] - xs[None]) / wid[None]) ** 2), 0)
            buf += (K * perc(lvl)[None]) @ col
            rib = (stg >= 3)
            if rib.any():
                Kr = np.where(near[:, rib], np.exp(-((d[:, None] - xs[rib][None]) / 2.6) ** 2), 0)
                buf += light(RIBBON, np.clip(0.75 * Kr.sum(1), 0, 1))
            bow = (stg >= 4)
            if bow.any():
                gl = 0.4 + 0.3 * np.sin(2 * np.pi * 3 * t + xs[bow] * 0.1)
                Kb = np.where(near[:, bow], np.exp(-((d[:, None] - xs[bow][None] - 5) / 3) ** 2), 0)
                buf += light(GOLD, np.clip((Kb * gl[None]).sum(1), 0, 1))

        # the jam: a red beacon over the wrapping corner while the queue backs up
        if qlen[f] >= 7 and t < T_LEVER:
            on = ((t * 3.0) % 1.0) < 0.5
            buf += dot(c3 + 30, ALARM, 1.0 * on, 16) + dot(c4 - 30, ALARM, 0.8 * (not on) * (qlen[f] >= 11), 16)
        # the boss: pops up over the jam, pulls the lever, starts it all again
        if T_BOSS <= t < T_RESTART + 2.0:
            xb = 0.5 * (c3 + c4) + 40
            up = smoothstep(T_BOSS, T_BOSS + 0.3, t) * (1 - smoothstep(T_RESTART + 1.2, T_RESTART + 2.0, t))
            buf += dot(xb, ELF, 1.0 * up, 11) + dot(xb + 16, GOLD, 0.95 * up, 6)
            a = t - T_LEVER
            if 0 <= a < 0.6:
                buf += light(ALARM, 0.35 * np.exp(-a / 0.15) * np.ones(n))
            a = t - T_RESTART
            if 0 <= a < 0.6:
                buf += dot(xb, ELF, np.exp(-a / 0.2), 60)
        # the batches to the sleigh: a gold streak down the Side
        for e in evs['ship']:
            a = t - e[1]
            if 0 <= a < 0.9:
                x = c1 - CHUTE_V * a
                buf += dot(x, GOLD, 0.8 * (1 - a / 0.9), 30)

        # the elves wrap the house: red paper with gold ribbon from the free end of Right round to the Side
        if t >= T_WRAP0:
            u = smoothstep(T_WRAP0, T_WRAP1, t) if t < T_WRAP1 else 1.0
            front = L + 20 - u * (L + 40)
            cov = d >= front
            ribbon = (np.abs(((d + 60) % 240) - 120) < 9)
            shine = 0.08 * np.sin(2 * np.pi * (d / 300 - 0.6 * t))
            buf = np.where(cov[:, None], light(HAT, (0.7 + shine) * np.ones(n)) * (~ribbon)[:, None]
                           + light(GOLD, 0.95 * ribbon) , buf)
            if t < T_WRAP1 + 0.2:
                buf += dot(front, RIBBON, 0.9, 14) + dot(front, GOLD, 0.6, 40)
            # the bow on the porch
            if t >= T_BOW:
                a = t - T_BOW
                xb = 0.5 * (c3 + c4)
                buf += dot(xb, GOLD, 1.0, 22 + 12 * smoothstep(0, 0.3, a)) + dot(xb, RIBBON, np.exp(-a / 0.12), 50 + 400 * a)
                for k in (-1, 1):
                    buf += dot(xb + k * 40, GOLD, 0.85, 14)
                if a > 0.4:                                         # the whole wrapped house sparkles
                    tw = np.clip(flake(2 * t) - 1.2, 0, None)
                    buf += light(RIBBON, 0.8 * tw)
                    # a sheen sweeps round the paper, the ribbons pulse on the beat, the elves cheer
                    ph_ = ((t - T_BOW) % (4 * RB)) / (4 * RB)
                    sweep = L + 150 - ph_ * (L + 300)
                    buf += light(RIBBON, 0.55 * np.exp(-((d - sweep) / 80) ** 2))
                    pulse = np.exp(-(((t - T_RESTART) % RB) / 0.12))
                    buf += light(GOLD, 0.35 * pulse * ribbon)
                    for k, x in enumerate([c5, c4, c3, c2, c1]):
                        hop = np.exp(-(((t - T_RESTART + 0.5 * RB * (k % 2)) % RB) / 0.15))
                        buf += dot(x + 14, ELF, 0.75 + 0.25 * hop, 7) + dot(x + 14 + 8 + 6 * hop, HAT, 0.9, 4)
            if t >= T_FINAL:
                a = t - T_FINAL
                buf += light(GOLD, 0.35 * np.exp(-a / 0.4) * np.ones(n))
        out[f][G.path] = np.clip(buf, 0, 1) * master
    return out


# ---- music: a workshop polka in F major whose tempo is the belt's ----
POLKA = 'F4 A4 C5 A4 | Bb4 G4 E4 C4 | F4 A4 C5 F5 | E5 C5 G4:2 | D5 Bb4 G4 Bb4 | C5 A4 F4 A4 | G4 C5 E4 G4 | F4:2 r:2'
POLKA_CH = [('F', 'A', 'C'), ('C', 'E', 'G', 'Bb'), ('F', 'A', 'C'), ('C', 'E', 'G'), ('Bb', 'D', 'F'),
            ('F', 'A', 'C'), ('C', 'E', 'G', 'Bb'), ('F', 'A', 'C')]
PAINT_NOTES = ('F5', 'A5', 'C6', 'G5', 'D6')                # a glockenspiel note for each paint colour


def beat_at(arr, x):
    """Time of fractional beat x on a beat grid (extrapolated past its end)."""
    if x <= len(arr) - 1:
        return float(np.interp(x, np.arange(len(arr)), arr))
    return float(arr[-1] + (x - len(arr) + 1) * (arr[-1] - arr[-2]))


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    W = simulate(G)
    g, ev, ent, toy, qlen = W['g'], W['ev'], W['ent'], W['toy'], W['qlen']
    c1, c2, c3, c4, c5, L = (g[k] for k in ('c1', 'c2', 'c3', 'c4', 'c5', 'L'))

    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    fl_st = M.sampler('Woodwinds/Flute/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    viola = M.sampler('Strings/Viola Section/pizz/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    trem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    wah = M.sampler('Brass/Trumpet/harmonM-sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    block = M.hits('Percussion/LogDrumHi_MedM_v2*.wav')
    anvil = M.hits('Percussion/Anvil_Hit1_v[12]*.wav')
    cabasa = M.hits('VSCO 1 Percussion/varMetal/various/cabasa_[1-6].wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    click = M.hits('VSCO 1 Percussion/varWood/wood_click_pp*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    brake = M.hits('Percussion/BrakeDrum1_Hammer_v3*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_big = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    snare = M.hits('Percussion/Snare2-HitSN_v[35]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v5*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    crash_mf = M.hits('Percussion/cymbal-crash1_mf*.wav')
    sleigh = M.hits('Percussion/Sleighbells_Hit*.wav')
    sleigh_sh = M.hits('Miscellania Raw/Misc 2/sleighbell*_shake*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_fastAsc1.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit_v[13]*.wav')

    for name, gain, rev in (('tune', 0.5, 0.15), ('pizz', 0.54, 0.1), ('harm', 0.42, 0.3), ('perc', 0.47, 0.12),
                            ('belt', 0.33, 0.12), ('fx', 0.33, 0.15), ('sparkle', 0.29, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    for bus in ('tune', 'pizz', 'harm', 'perc', 'belt', 'sparkle'):     # the lever: everything stops dead
        M.fader(bus, [(T_LEVER - 0.005, 0.0), (T_LEVER + 0.03, -70.0), (T_RESTART - 0.6, -70.0),
                      (T_RESTART - 0.55, 0.0)])

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(np.clip(dd, 0, L), ds, xs)
        return 0.85 * (2 * (x - x0) / (x1 - x0) - 1)

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def chord(names, octave):
        outl, last = [], -1
        for c in names:
            m = n(c + str(octave))
            while m <= last:
                m += 12
            outl.append(m)
            last = m
        return outl

    def pff(seconds=0.25, amp=0.5, seed=0):
        k = int(seconds * SR)
        x = np.random.default_rng(seed).normal(0, 1, k)
        y = np.convolve(x, np.ones(6) / 6, 'same')
        tt = np.arange(k) / SR
        return amp * y / (np.abs(y).max() + 1e-9) * np.clip(tt / 0.003, 0, 1) * np.exp(-tt / (seconds / 4))

    def bar_of_polka(grid, b0, k, insts, vel=98, bass=True, inst_b=None, comp=True):
        """Bar k of the polka from beat b0 of a beat grid."""
        toks = POLKA.split('|')[k % 8].split()
        b = 0.0
        for tok in toks:
            nm, _, bt = tok.partition(':')
            bt = float(bt) if bt else 1.0
            if nm != 'r':
                t = beat_at(grid, b0 + b)
                dur = beat_at(grid, b0 + b + bt) - t
                for inst, bus, gn, pn, dv in insts:
                    M.add(bus, inst.play(n(nm) + dv, vel, dur=dur * 0.55, release=0.08), t, gn, pn)
            b += bt
        ch = POLKA_CH[k % 8]
        for j in range(4):
            t = beat_at(grid, b0 + j)
            if bass and j % 2 == 0:
                root = n(ch[0] + '2') if j == 0 else n(ch[2] + '2') - (12 if n(ch[2] + '2') > n(ch[0] + '2') + 5 else 0)
                M.add('pizz', (inst_b or cello).play(root, 100), t, 0.8 if inst_b is None else 0.65)
            elif comp and j % 2 == 1:
                for m in chord(ch[:3], 3):
                    M.add('pizz', viola.play(m, 75), t, 0.35, 0.2)

    A, B = BEATS_A, BEATS_B
    # ---- 0-2: the elves pop up, the belt whirs into motion ----
    for k, (x, m) in enumerate(zip((c5, c4, c3, c2), ('C5', 'F5', 'A5', 'C6'))):
        M.add('sparkle', xylo.play(n(m) - 12, 95), A[1 + k] - 0.1, 0.7, pan_at(x))
        M.add('pizz', viola.play(n(m) - 12, 85), A[1 + k] - 0.1, 0.5, pan_at(x))
    M.add('perc', sleigh_sh.play(80), 0.1, 0.5, pan_at(0))
    for m in ('F3', 'C4', 'A4'):
        M.add('harm', vln.play(n(m), 60, dur=T_BELT - 0.3, release=0.3), 0.3, 0.35)
    tt = np.arange(int((T_LEVER - T_BELT) * SR)) / SR + T_BELT
    sp = np.array([belt_v(t) for t in tt[::480]])
    v_ = np.interp(tt, tt[::480], sp)
    f0 = 45 + 0.25 * v_
    ph = 2 * np.pi * np.cumsum(f0) / SR
    hum = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * np.clip(v_ / V0, 0, 1.6) * 0.05
    hum[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    M.add('fx', np.vstack([hum, hum]), T_BELT, 1.0)
    tt2 = np.arange(int((D - T_RESTART) * SR)) / SR + T_RESTART
    v2 = np.interp(tt2, tt2[::480], np.array([belt_v(t) for t in tt2[::480]]))
    ph2 = 2 * np.pi * np.cumsum(45 + 0.25 * v2) / SR
    hum2 = (np.sin(ph2) + 0.5 * np.sin(2 * ph2) + 0.25 * np.sin(3 * ph2)) * np.clip(v2 / V0, 0, 1.6) * 0.05
    hum2 *= np.clip((T_WRAP0 + 1.0 - tt2) / 1.0, 0, 1)
    M.add('fx', np.vstack([hum2, hum2]), T_RESTART, 1.0)

    # ---- 2-47: the polka, on the belt's tempo, getting busier as it speeds up ----
    b0 = 4
    k = 0
    while b0 + 4 <= len(A):
        t0 = A[b0]
        insts = [(clar, 'tune', 0.75, -0.15, 0)]
        if t0 >= 12:
            insts.append((fl_st, 'tune', 0.45, 0.2, 0))
        if t0 >= T_ACCEL:
            insts.append((tpt, 'tune', 0.5, 0.1, 0))
        if t0 >= 38:
            insts.append((xylo, 'sparkle', 0.4, 0.3, 0))
        bar_of_polka(A, b0, k, insts, vel=96 + min(20, int(max(0, t0 - 20))))
        if t0 >= 20:
            for j in (1, 3):
                M.add('perc', snare.play(70 + min(30, int(t0 - 20))), beat_at(A, b0 + j), 0.35)
        if t0 >= 34:
            for j in range(8):
                M.add('perc', snare.play(55), beat_at(A, b0 + j / 2), 0.2, 0.2)
        b0 += 4
        k += 1
    # the jam: a two-tone alarm with the beacon
    on = (qlen >= 7) & (np.arange(len(qlen)) * DT < T_LEVER)
    if on.any():
        ta, tb = np.argmax(on) * DT, T_LEVER
        k_ = int((tb - ta) * SR)
        tt = np.arange(k_) / SR + ta
        hi = ((tt * 3.0) % 1.0) < 0.5
        f = np.where(hi, 880.0, 660.0)
        ph = 2 * np.pi * np.cumsum(f) / SR
        amp = 0.07 * np.clip((tt - ta) / 2.0, 0.3, 1)
        al = amp * (np.sin(ph) + 0.3 * np.sin(2 * ph))
        M.add('belt', mono(al, np.full(k_, pan_at(c3 + 30))), ta, 1.0)
        for j, tw in enumerate(np.arange(np.ceil(ta * 3) / 3, tb - 0.1, 2 / 3)):
            M.add('tune', wah.play(n('A4') - 12, 85, dur=0.15), tw, 0.45, pan_at(c3 + 30))
            M.add('tune', wah.play(n('F4') - 12, 85, dur=0.15), tw + 1 / 3, 0.45, pan_at(c3 + 30))
    # the boss pops up; the lever
    M.add('tune', bsn.play(n('C3'), 105, dur=0.2), T_BOSS, 0.8, pan_at(0.5 * (c3 + c4)))
    M.add('tune', bsn.play(n('F2'), 105, dur=0.3), T_BOSS + 0.25, 0.8, pan_at(0.5 * (c3 + c4)))
    r = ratchet.play(100)
    M.add('fx', r[:, :int(0.6 * SR)], T_LEVER - 0.55, 0.7, pan_at(0.5 * (c3 + c4)))
    for h, gn in ((bd_big, 1.0), (brake, 0.7), (timp, 0.7)):
        M.add('fx', h.play(118), T_LEVER, gn, pan_at(0.5 * (c3 + c4)))
    # the restart: the boss's whistle, then away
    M.add('fx', slide(0.0, 0.12, 1200, 2200, 0.25, 0.4, 0.5), T_RESTART - 0.5, 0.8, pan_at(0.5 * (c3 + c4)))
    M.add('fx', slide(0.0, 0.1, 1500, 2600, 0.2, 0.4, 0.5), T_RESTART - 0.2, 0.8, pan_at(0.5 * (c3 + c4)))
    M.add('perc', crash_mf.play(95), T_RESTART, 0.5)

    # ---- after the restart: the polka at 132, the whole band ----
    for k in range(12):                                            # 48 beats up to the last batch
        bk = 4 * k
        insts = [(tpt, 'tune', 0.7, 0.1, 0), (clar, 'tune', 0.55, -0.15, 0), (glock, 'sparkle', 0.3, 0.3, 12)]
        bar_of_polka(B, bk, k if k < 8 else k - 4, insts, vel=106, inst_b=tuba)
        for j in range(8):
            M.add('perc', sleigh.play(100 if j % 2 == 0 else 75), beat_at(B, bk + j / 2), 0.4, (-0.35, 0.35)[j % 2])
        for j in (1, 3):
            M.add('perc', snare.play(85), beat_at(B, bk + j), 0.35)
    # ---- the elves wrap the house: a harp glissando follows the paper, strings swell ----
    k0 = 52
    for j, (ch, beats) in enumerate(((('F', 'A', 'C'), 4), (('Bb', 'D', 'F'), 4), (('C', 'E', 'G', 'Bb'), 4))):
        t0 = beat_at(B, k0 + 4 * j)
        for m in chord(ch, 3):
            M.add('harm', vln.play(m + 12, 65 + 12 * j, dur=4 * RB, release=0.3), t0, 0.4, 0.15)
            M.add('harm', horn.play(m, 60 + 12 * j, dur=4 * RB, release=0.3), t0, 0.35, -0.2)
        M.add('pizz', tuba.play(n(ch[0] + '2'), 100), t0, 0.7)
    gl = []
    for o in (3, 4, 5):
        gl += chord(('F', 'A', 'C'), o)
    gl = gl[::-1] + gl
    for j, m in enumerate(gl):
        u = j / (len(gl) - 1)
        tj = T_WRAP0 + u * (T_WRAP1 - T_WRAP0)
        M.add('harm', harp.play(m, 85), tj, 0.6, pan_at(L - u * L))
    r = sroll.play(100, dur=T_BOW - T_WRAP1 + 1.0)
    M.add('perc', r * np.linspace(0.1, 1, r.shape[1]) ** 2, T_WRAP1 - 1.0, 0.55)
    w = whoosh(T_WRAP1 - T_WRAP0, 300, 2000, 0.6, seed=7)
    M.add('fx', mono(w[0], np.linspace(pan_at(L), pan_at(0), w.shape[1])), T_WRAP0, 0.4)
    # ---- the bow, and the polka's last phrase ----
    M.add('perc', crash.play(118), T_BOW, 0.7)
    M.add('perc', bd.play(118), T_BOW, 0.9)
    M.add('sparkle', chimes.play(100), T_BOW, 0.6)
    for i, m in enumerate(chord(('F', 'A', 'C'), 4) + [n('F5')]):
        M.add('sparkle', glock.play(m, 100), T_BOW + 0.05 * i, 0.6, pan_at(0.5 * (c3 + c4)))
    for k in range(2):
        bk = 70 + 4 * k
        insts = [(tpt, 'tune', 0.75, 0.1, 0), (clar, 'tune', 0.55, -0.15, 0), (glock, 'sparkle', 0.3, 0.3, 12),
                 (xylo, 'sparkle', 0.35, -0.3, 0)]
        bar_of_polka(B, bk, 5 + k, insts, vel=110, inst_b=tuba)
        for j in range(8):
            M.add('perc', sleigh.play(105 if j % 2 == 0 else 80), beat_at(B, bk + j / 2), 0.45, (-0.35, 0.35)[j % 2])
    for m in chord(('F', 'A', 'C'), 3):
        M.add('harm', horn.play(m, 100, dur=2 * RB, release=0.2), beat_at(B, 68), 0.5, -0.2)
    # ---- the last chord ----
    M.add('perc', crash.play(118), T_FINAL, 0.7)
    M.add('perc', bd.play(118), T_FINAL, 0.9)
    M.add('perc', timp.play(115, pitch=-2), T_FINAL, 0.7)
    for m in chord(('F', 'A', 'C'), 3):
        M.add('harm', horn.play(m, 110, dur=1.4, release=0.5), T_FINAL, 0.55, -0.2)
        M.add('tune', tpt_s.play(m + 12, 108, dur=1.3, release=0.5), T_FINAL, 0.45, 0.2)
    M.add('pizz', tuba.play(n('F1') + 12, 115, dur=1.2), T_FINAL, 0.8)
    M.add('perc', sleigh_sh.play(105), T_FINAL, 0.6)

    # ---- every item: in with a wood block, hammered, painted, wrapped, bowed, stacked, shipped ----
    for te in ent:
        M.add('belt', block.play(80, pitch=float(M.rng.uniform(-1, 1))), te, 0.6, pan_at(L))
    for kind, t, x, i in [e for e in ev if e[0] in ('hammer', 'paint', 'wrap', 'bow', 'dock')]:
        p = pan_at(x)
        if kind == 'hammer':
            M.add('belt', anvil.play(int(M.rng.integers(70, 90)), pitch=float(M.rng.uniform(-1.5, 1.5))), t, 0.45, p)
        elif kind == 'paint':
            M.add('belt', mono(pff(0.22, 0.35, int(t * 100)), np.full(int(0.22 * SR), p)), t, 0.8)
            M.add('sparkle', glock.play(n(PAINT_NOTES[toy[i]]) - 12, 70), t, 0.45, p)
        elif kind == 'wrap':
            M.add('belt', cabasa.play(80), t, 0.5, p)
            M.add('sparkle', harp.play(n(('F4', 'A4', 'C5', 'F5')[i % 4]), 75), t, 0.45, p)
        elif kind == 'bow':
            M.add('belt', tri.play(55), t, 0.35, p)
        elif kind == 'dock':
            M.add('belt', click.play(70), t, 0.45, p)
    for e in ev:
        if e[0] == 'ship':
            w = whoosh(0.7, 600, 3000, 0.8, seed=int(e[1] * 10))
            M.add('fx', mono(w[0], np.linspace(pan_at(c1), pan_at(0) - 0.1, w.shape[1])), e[1], 0.6)
            M.add('perc', sleigh_sh.play(95), e[1], 0.5, pan_at(c1 * 0.5))
        elif e[0] == 'sleigh':
            M.add('perc', sleigh.play(110), e[1], 0.6, pan_at(0))
            M.add('sparkle', glock.play(n('C5'), 85), e[1], 0.45, pan_at(0))
            M.add('sparkle', glock.play(n('F5'), 85), e[1] + 0.1, 0.45, pan_at(0))
