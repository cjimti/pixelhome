"""Cornucopia: The Side is a woven horn of plenty, narrow at the free back end and opening at the
front-left corner. Harvest spills out of it: pumpkins, gourds, apples, corn and cranberries, each a
body with its own size and mass, rolling with real momentum along the Left wing, up the Porch Left
and onto the porch table, knocking into each other and packing up in a row. Last comes a pumpkin too
big for the horn's mouth. It sticks, the horn strains, it pops free, slams into the back of the row,
and like a Newton's cradle the shock runs the length of the pile and fires the little cranberry at
the front off down the Porch Right and out the end of the house."""
import numpy as np
from pixelhome.fx import DT, hexc, light, keys, smoothstep, Flicker, nframes

CODE = 'TG08'
TITLE = 'Cornucopia'
KIND = 'show'
DESCRIPTION = ('The Side is a horn of plenty. Pumpkins, apples, corn and cranberries roll out with real momentum and '
               'pack up on the porch, until one pumpkin too many sends a cranberry flying out the far end.')

PUMPKIN = hexc('#ff5200')
APPLE = hexc('#c0102a')
GOLD = hexc('#ffb000')
AMBER = hexc('#ff8a18')
CRAN = hexc('#d0183a')
WARM = hexc('#ffc27a')
BROWN = hexc('#7a2c06')
DEEP = hexc('#4a1604')
D = 56.0
MOUTH = 478.0
TABLE = 1486.0
KINDS = {'pumpkin': (15, PUMPKIN), 'gourd': (10, GOLD), 'apple': (8, APPLE), 'corn': (13, GOLD),
         'cran': (3.5, CRAN), 'pear': (8, AMBER)}         # radius, colour
STRAIN = (34.5, 36.0)               # the stuck pumpkin starts to strain, and is at full strain
SHAKE = 3.1                         # Hz, its rocking in the mouth


def render(G, seed=28, log=None):
    """log, a list, collects what score() plays to: ('spill', t, kind), ('pos', t, [x of each item]),
    ('knock', t, x, impulse, a, b), ('pop', t), ('shock', t), ('fire', t), ('out', t)."""
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    n = G.N
    pdp = G.pd[G.path]
    weave = Flicker(rng, n, 0.05, 0.2)

    order = ['cran'] + list(rng.choice(['pumpkin', 'gourd', 'apple', 'corn', 'cran', 'pear', 'apple', 'cran'], 21))
    spawn_t = 4.0 + np.cumsum(rng.uniform(0.6, 1.7, len(order))) * 0.95
    spawn_t[0] = 4.0
    items = []
    for k, tt in zip(order, spawn_t):
        R, col = KINDS[k]
        items.append(dict(R=R, col=col, m=R ** 2, t0=tt, x=MOUTH - 30.0, v=rng.uniform(380, 520), on=False,
                          big=False, kind=k, i=len(items)))
    BIG = dict(R=24, col=PUMPKIN, m=24 ** 2, t0=33.0, x=MOUTH - 45.0, v=0.0, on=False, big=True, kind='big',
               i=len(items))
    items.append(BIG)
    stuck_until = 38.6
    shock_t = None
    shot = None                      # the cranberry that gets fired
    slope, visc, coulomb = 70.0, 0.55, 25.0
    SUB = 4
    dt = DT / SUB

    for f in range(F):
        t = f * DT
        for it in items:
            if not it['on'] and t >= it['t0']:
                it['on'] = True
                if log is not None:
                    log.append(('spill', it['t0'], it['kind']))
        live = [it for it in items if it['on'] and it is not shot]
        for _ in range(SUB):
            for it in live:
                if it['big'] and t < stuck_until:
                    it['x'] = MOUTH - 24 + 5 * np.sin(2 * np.pi * SHAKE * t) * smoothstep(*STRAIN, t)
                    it['v'] = 0.0
                    continue
                if it['big'] and t >= stuck_until and it.get('popped') is None:
                    it['v'] = 820.0
                    it['popped'] = True
                    if log is not None:
                        log.append(('pop', t))
                d = TABLE - it['x']
                a = slope * np.sign(d) * min(1, abs(d) / 40) - visc * it['v']
                if abs(it['v']) > 1e-3:
                    a -= coulomb * np.sign(it['v'])
                it['v'] += a * dt
                if abs(it['v']) < 2 and abs(d) < 400:
                    it['v'] *= 0.9
                it['x'] += it['v'] * dt
            live.sort(key=lambda z: z['x'])
            for _ in range(3):                          # contacts between neighbours
                for a_, b_ in zip(live[:-1], live[1:]):
                    gap = b_['x'] - a_['x'] - (a_['R'] + b_['R'])
                    if gap < 0:
                        if a_['big'] and a_.get('popped') and shock_t is None and a_['v'] > 200:
                            shock_t = t
                            a_['v'] = 0.0
                            if log is not None:
                                log.append(('shock', t))
                        ma, mb = a_['m'], b_['m']
                        rel = a_['v'] - b_['v']
                        if rel > 0:
                            e = 0.25
                            j = (1 + e) * rel / (1 / ma + 1 / mb)
                            if log is not None:
                                log.append(('knock', t, a_['x'] + a_['R'], j, a_['i'], b_['i']))
                            a_['v'] -= j / ma
                            b_['v'] += j / mb
                        corr = -gap / (ma + mb)
                        if not (a_['big'] and t < stuck_until):
                            a_['x'] -= corr * mb
                        b_['x'] += corr * ma
        if shot is not None:
            shot['v'] -= 0.35 * shot['v'] * DT
            shot['x'] += shot['v'] * DT
        # the shock reaches the front of the row: fire the front cranberry
        if shock_t is not None and shot is None:
            row = sorted([it for it in items if it['on']], key=lambda z: z['x'])
            span = row[-1]['x'] - row[0]['x']
            if t >= shock_t + span / 2600:
                shot = row[-1]
                shot['v'] = 1350.0
                shot['fired'] = t
                if log is not None:
                    log.append(('fire', t))

        buf = np.zeros((n, 3))
        # the horn: woven, narrow at the back, wide at the mouth, strains when the pumpkin is stuck
        horn = pdp < MOUTH + 6
        widen = np.clip(pdp / MOUTH, 0, 1)
        strain = smoothstep(*STRAIN, t) * (1 - smoothstep(stuck_until, stuck_until + 0.4, t))
        tex = 0.6 + 0.4 * np.sin(pdp * 0.42 + 3 * np.sin(pdp * 0.05)) ** 2
        hI = keys(t, [(0, 0), (3, 0.42), (52, 0.42), (56, 0)]) * (0.25 + 0.75 * widen ** 1.5) * tex
        hI = hI * (1 + 0.12 * weave(t) + strain * 0.5 * np.sin(2 * np.pi * 6.2 * t) * widen ** 3)
        buf += light(BROWN, hI * horn) + light(AMBER, 0.35 * hI * horn * widen ** 4)
        # each spill: the mouth gives a small cough of light
        for it in items:
            u = t - it['t0']
            if 0 <= u < 0.5:
                buf += light(WARM, 0.35 * np.exp(-u / 0.15) * np.exp(-((pdp - MOUTH) / 20) ** 2))
        # table glow under the pile
        buf += light(DEEP, keys(t, [(0, 0), (3, 0.12), (52, 0.12), (56, 0)]) * (~horn))

        for it in items:
            if not it['on']:
                continue
            x, R = it['x'], it['R']
            if x - R > G.length + 5:
                continue
            body = np.clip((R - np.abs(pdp - x)) / 2.5 + 0.5, 0, 1)
            roll = 0.72 + 0.28 * np.cos((pdp - x) / R * 1.6 + x / R)       # a highlight that turns as it rolls
            emerge = smoothstep(it['t0'], it['t0'] + 0.25, t)
            I = (0.8 if R > 4 else 1.0) * body * roll * emerge
            buf += light(it['col'], I)
            if it is shot:
                for k in range(1, 10):
                    buf += light(CRAN, 0.6 * (1 - k / 10) * np.exp(-((pdp - x + k * 1350 * DT * 0.8) / 4) ** 2))
        # the shock wave through the row
        if shock_t is not None and t - shock_t < 1.2:
            u = t - shock_t
            row = sorted([it for it in items if it['on'] and it is not shot], key=lambda z: z['x'])
            x0 = row[0]['x']
            front = x0 + 2600 * u
            buf += light(WARM, 0.85 * np.exp(-((pdp - front) / 30) ** 2) * (pdp < row[-1]['x'] + 40) * np.exp(-u / 0.6))
            buf += light(WARM, 0.6 * np.exp(-u / 0.12) * np.exp(-((pdp - x0) / 30) ** 2))
        # plink: the cranberry leaves through the free end
        if shot is not None and shot['x'] > G.length:
            tt = shot.get('out_t')
            if tt is None:
                shot['out_t'] = t
                tt = t
                if log is not None:
                    log.append(('out', t))
            u = t - tt
            buf += light(WARM, 0.9 * np.exp(-u / 0.2) * np.exp(-((pdp - G.length) / 25) ** 2))
        if log is not None:
            log.append(('pos', t, [it['x'] if it['on'] else np.nan for it in items]))
        buf *= keys(t, [(52, 1), (56, 0)])
        out[f][G.path] = buf
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A harvest jig in Bb, 6/8 at 1.2 s a bar from the first spill: pizzicato bass and upright piano, a bassoon then a
# clarinet with the tune. Every item that rolls out tumbles down a marimba (xylophone for the small ones), a note for
# each half turn it actually makes, so the runs slow as it slows; the bigger it is the lower and heavier. Each spill
# is a log-drum cough at the mouth, each arrival a woodblock knock where it hits the row. The stuck pumpkin grunts
# on a bassoon in time with its rocking, pops with a slide whistle, thunders down, and the shock ripples the length of
# the pile in claves before the cranberry flies out on a slide whistle and lands with a plink. Then the band again.

BAR = 1.2
PROG = ['Bb', 'Eb', 'Bb', 'F', 'Bb', 'Eb', 'F', 'Bb'] * 2 + ['Gm', 'Eb', 'Bb', 'F', 'Gm', 'Eb', 'F', 'Bb']
CHORD = {'Bb': (34, 41, (62, 65, 70)), 'Eb': (39, 46, (63, 67, 70)), 'F': (41, 36, (60, 63, 65, 69)),
         'Gm': (43, 38, (62, 67, 70))}      # root, fifth, chord (F with its seventh)
TUNE_A = [[(0, 'F4', 2), (2, 'Bb4', 1), (3, 'D5', 2), (5, 'C5', 1)], [(0, 'Bb4', 2), (2, 'G4', 1), (3, 'Eb5', 3)],
          [(0, 'D5', 2), (2, 'C5', 1), (3, 'Bb4', 2), (5, 'A4', 1)], [(0, 'C5', 3), (3, 'F4', 3)],
          [(0, 'F4', 2), (2, 'Bb4', 1), (3, 'D5', 2), (5, 'F5', 1)], [(0, 'G5', 2), (2, 'F5', 1), (3, 'Eb5', 2), (5, 'C5', 1)],
          [(0, 'D5', 2), (2, 'C5', 1), (3, 'A4', 2), (5, 'C5', 1)], [(0, 'Bb4', 6)]]
TUNE_B = [[(0, 'D5', 1), (1, 'D5', 1), (2, 'G5', 1), (3, 'F5', 2), (5, 'D5', 1)], [(0, 'Eb5', 2), (2, 'C5', 1), (3, 'G4', 3)],
          [(0, 'Bb4', 1), (1, 'C5', 1), (2, 'D5', 1), (3, 'F5', 2), (5, 'D5', 1)], [(0, 'C5', 3), (3, 'A4', 2), (5, 'C5', 1)],
          [(0, 'Bb4', 2), (2, 'D5', 1), (3, 'G5', 2), (5, 'F5', 1)], [(0, 'Eb5', 2), (2, 'G5', 1), (3, 'Bb4', 2), (5, 'C5', 1)],
          [(0, 'D5', 2), (2, 'F4', 1), (3, 'A4', 2), (5, 'C5', 1)], [(0, 'Bb4', 3)]]
TUMBLE = {'pumpkin': ('mar', 'Bb3', 112), 'big': ('mar', 'F3', 124), 'corn': ('mar', 'A4', 92),
          'gourd': ('mar', 'F4', 96), 'apple': ('mar', 'C5', 86), 'pear': ('xylo', 'D5', 72), 'cran': ('xylo', 'F5', 60)}


def score(M, G):
    from pixelhome.audio import note, slide, whoosh
    n = note
    ev = []
    render(G, log=ev)                       # the same simulation: every spill, half turn, knock, the pop and the shot
    spill = [(t, k) for e, t, *k in ev if e == 'spill']
    kinds = [k[0] for _, k in spill]
    T = np.array([e[1] for e in ev if e[0] == 'pos'])
    P = np.array([e[2] for e in ev if e[0] == 'pos'])
    t_of = {e[0]: e[1] for e in ev if e[0] in ('pop', 'shock', 'fire', 'out')}
    T0, BIG, POP, SHOCK, FIRE, OUT = spill[0][0], spill[-1][0], t_of['pop'], t_of['shock'], t_of['fire'], t_of['out']
    T1 = OUT + 0.6                          # the band comes back after the plink

    mar = M.sampler('Percussion/Marimba/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    bass = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    bsn_s = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    log = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum1_mp*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    crash = M.hits('Percussion/cymbal-crashshort*.wav')

    for name, gain, rev in (('bass', 0.25, 0.1), ('piano', 0.2, 0.18), ('tune', 0.2, 0.25), ('tumble', 0.13, 0.18),
                            ('perc', 0.7, 0.15), ('drums', 0.55, 0.2), ('brass', 0.3, 0.25), ('fx', 0.3, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    def chord_at(t, t0=T0):
        k = int((t - t0) // BAR)
        return PROG[min(max(k, 0), len(PROG) - 1)] if t < BIG else 'Bb'

    def tones(c, top):                      # the chord's notes from top down an octave and a half
        pcs = {m % 12 for m in CHORD[c][2]}
        return [m for m in range(top, top - 19, -1) if m % 12 in pcs]

    def groove(t0, bars, prog, vel=90, tamb_on=False):
        for k in range(bars):
            t, c = t0 + k * BAR, prog[k % len(prog)]
            root, fifth, ch = CHORD[c]
            M.add('bass', bass.play(root, vel), t, 1.0, -0.1)
            M.add('bass', bass.play(fifth, vel - 12), t + BAR / 2, 0.8, -0.1)
            for e in (2, 5):
                for m in ch:
                    M.add('piano', piano.play(m - 12 * (m > 66), vel - 30 + 6 * (e == 2)), t + e * BAR / 6, 0.6, 0.15)
            if tamb_on:
                M.add('perc', tamb.play(55), t + BAR / 2, 0.4, 0.3)

    def tune(inst, bars, t0, bus, vel, pan, shift=0):
        for i, bar in enumerate(bars):
            for e, m, dur in bar:
                M.add(bus, inst.play(n(m) + shift, vel, dur=dur * BAR / 6 * 0.9, release=0.15),
                      t0 + i * BAR + e * BAR / 6, 1.0, pan)

    # ---- the horn fills with light; a vamp, then the jig from the first spill until the big pumpkin ----
    groove(T0 - 3 * BAR, 3, ['Bb', 'F', 'Bb'], 76)
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4')):
        M.add('tune', harp.play(n(m), 70), 0.3 + 0.1 * i, 0.7, pan_at(MOUTH))
    groove(T0, 16, PROG)
    groove(T0 + 16 * BAR, 8, PROG[16:], 94, True)
    tune(bsn, TUNE_A, T0, 'tune', 96, -0.25, -12)
    tune(clar, TUNE_A, T0 + 8 * BAR, 'tune', 84, 0.0)
    tune(clar, TUNE_B, T0 + 16 * BAR, 'tune', 88, 0.0)
    tune(bsn, [[(0, 'Bb3', 3), (3, 'D4', 3)], [(0, 'Eb4', 6)], [(0, 'D4', 3), (3, 'F4', 3)], [(0, 'C4', 6)],
               [(0, 'D4', 3), (3, 'Bb3', 3)], [(0, 'G3', 6)], [(0, 'A3', 3), (3, 'C4', 3)], [(0, 'Bb3', 3)]],
         T0 + 16 * BAR, 'tune', 74, -0.3)

    # ---- spills, tumbles and knocks, all from the simulation ----
    for (t, _), k in zip(spill, kinds):
        M.add('perc', log.play(96 + 31 * (k in ('pumpkin', 'big'))), t, 0.8, pan_at(MOUTH))
    for i, k in enumerate(kinds):
        inst, top, vel = TUMBLE[k]
        inst = mar if inst == 'mar' else xylo
        R = KINDS[k][0] if k in KINDS else 24
        x = P[:, i]
        live = ~np.isnan(x)
        t0 = T[live][0]
        tt, xx = T[live], x[live]
        end = (POP, SHOCK + 0.05) if k == 'big' else (t0, min(FIRE, SHOCK))
        sel = (tt >= end[0]) & (tt <= end[1])
        tt, xx = tt[sel], xx[sel]
        v = np.abs(np.gradient(xx, DT))
        still = np.nonzero((v < 20) & (tt > tt[0] + 0.5))[0]
        if len(still):
            tt, xx, v = tt[:still[0]], xx[:still[0]], v[:still[0]]
        s = np.concatenate([[0], np.cumsum(np.abs(np.diff(xx)))])
        step = max(np.pi * R, 28.0)
        marks = np.arange(step, s[-1], step)
        when = np.interp(marks, s, tt)
        last = -1.0
        for j, (w, mk) in enumerate(zip(when, marks)):
            if w - last < 0.06:
                continue
            last = w
            sp = float(np.interp(w, tt, v))
            tn = tones(chord_at(w), n(top))
            m = tn[(j % 3 + j // 3) % len(tn)]
            M.add('tumble', inst.play(m, int(np.clip(vel * (sp / 450) ** 0.4, 30, 127))), w, 1.0,
                  pan_at(np.interp(w, tt, xx)))
    knocks = sorted((e[1], e[2], e[3]) for e in ev if e[0] == 'knock' and e[3] > 300 and e[1] < SHOCK)
    group = []
    for t, x, j in knocks + [(1e9, 0, 0)]:  # an arrival pushes the whole row in one instant: one knock per instant
        if group and t - group[0][0] > 0.15:
            _, xk, jk = max(group, key=lambda g: g[2])
            M.add('perc', wood.play(int(np.clip(76 + 30 * np.log10(jk / 300), 70, 127))), group[0][0], 1.0,
                  pan_at(xk))
            group = []
        group.append((t, x, j))

    # ---- the big one: stuck in the mouth, rocking, straining; the horn groans ----
    M.add('brass', tuba.play(n('Bb1'), 110), BIG, 1.0, pan_at(MOUTH))
    M.add('drums', timp.play(100, pitch=-3), BIG, 0.7, pan_at(MOUTH))
    M.add('tune', clar.play(n('D5'), 70, dur=0.35), BIG + 0.6, 0.8, 0.0)      # "uh..."
    M.add('tune', clar.play(n('Db5'), 66, dur=0.6), BIG + 1.0, 0.8, 0.0)      # "...oh"
    k0 = int(np.ceil((STRAIN[0] - 0.25 / SHAKE) * SHAKE))
    for i, k in enumerate(range(k0, int((POP - 0.25 / SHAKE) * SHAKE) + 1)):  # a grunt at every forward rock
        t = (k + 0.25) / SHAKE
        g = smoothstep(STRAIN[0] - 0.3, STRAIN[1], t)
        M.add('tune', bsn.play(n('Bb2') + i // 2, int(60 + 50 * g)), t, 0.4 + 0.6 * g, pan_at(MOUTH))
        M.add('perc', wood.play(int(50 + 40 * g)), t, 0.4 * g, pan_at(MOUTH))
    M.add('drums', troll.play(70, dur=POP - STRAIN[1]), STRAIN[1], 0.6, pan_at(MOUTH))
    M.add('brass', bsn_s.play(n('F2'), 90, dur=POP - STRAIN[0], release=0.1), STRAIN[0], 0.6, pan_at(MOUTH))

    # ---- POP; it thunders down to the row; the shock runs the pile; the cranberry flies ----
    M.add('fx', slide(0.0, 0.14, 500, 1500, 0.18, 0.5), POP - 0.02, 1.0, pan_at(MOUTH))
    M.add('perc', slap.play(120), POP, 0.9, pan_at(MOUTH))
    M.add('drums', crash.play(90), POP, 0.4, pan_at(MOUTH))
    M.add('fx', whoosh(SHOCK - POP, 150, 900, 0.6, seed=8), POP, 0.8, pan_at((MOUTH + TABLE) / 2))
    M.add('drums', troll.play(90, dur=SHOCK - POP), POP + 0.1, 0.7, pan_at((MOUTH + TABLE) / 2))
    xs_row = np.sort(P[np.searchsorted(T, SHOCK)])
    xs_row = xs_row[~np.isnan(xs_row)]
    M.add('drums', bd.play(124), SHOCK, 1.0, pan_at(xs_row[0]))
    M.add('drums', timp.play(124, pitch=-5), SHOCK, 0.9, pan_at(xs_row[0]))
    M.add('drums', crash.play(118), SHOCK, 0.7, pan_at(xs_row[0]))
    M.add('brass', tuba.play(n('Bb1'), 124), SHOCK, 1.0, pan_at(xs_row[0]))
    up = [m for m in range(n('Bb3'), n('Bb6')) if m % 12 in (10, 0, 2, 3, 5, 7, 9)]
    for i, x in enumerate(xs_row):          # click, click, click: the shock through every item to the front
        t = SHOCK + (x - xs_row[0]) / 2600
        M.add('perc', clave.play(90 + int(30 * i / len(xs_row))), t, 0.6, pan_at(x))
        M.add('tumble', xylo.play(up[min(i, len(up) - 1)], 90), t, 0.7, pan_at(x))
    xc = P[:, kinds.index('cran')]          # the shot is the front cranberry: the first one out
    for i, t in enumerate(np.arange(FIRE, OUT, 0.1)):         # a slide whistle that follows it down the house
        u0, u1 = (t - FIRE) / (OUT - FIRE), min(1, (t + 0.1 - FIRE) / (OUT - FIRE))
        f0, f1 = 700 * 2.6 ** u0, 700 * 2.6 ** u1
        M.add('fx', slide(0.0, 0.1, f0, f1, 0.11, 1.0), t, 0.9, pan_at(np.interp(t, T, xc)))
    M.add('tumble', glock.play(n('F6'), 80), OUT, 0.8, pan_at(G.length))
    M.add('tumble', glock.play(n('Bb5'), 60), OUT + 0.12, 0.5, pan_at(G.length))

    # ---- the band again, horn on the tune, and a final chord as the horn's light goes down ----
    M.add('perc', wood.play(100), T1 - BAR / 3, 0.8, 0.0)
    M.add('perc', wood.play(100), T1 - BAR / 6, 0.8, 0.0)
    groove(T1, 8, PROG[:8], 98, True)
    tune(horn, TUNE_A, T1, 'brass', 96, -0.1)
    tune(clar, TUNE_A, T1, 'tune', 70, 0.15, -12)
    fin = T1 + 8 * BAR
    for i, m in enumerate(('Bb2', 'F3', 'Bb3', 'D4', 'F4', 'Bb4', 'D5')):
        M.add('tune', harp.play(n(m), 90), fin + 0.06 * i, 0.9, -0.5 + 0.15 * i)
    M.add('bass', bass.play(n('Bb1'), 110), fin, 1.0)
    M.add('brass', tuba.play(n('Bb1'), 110), fin, 0.8)
    M.add('brass', horn.play(n('D4'), 90, dur=2.5, release=1.0), fin, 0.8, -0.1)
    M.add('tune', clar.play(n('F4'), 80, dur=2.5, release=1.0), fin, 0.8, 0.15)
    M.add('drums', timp.play(100), fin, 0.6)
    M.add('perc', wood.play(110), fin, 0.6, pan_at(TABLE))
