"""The Sentence: the storm still holds the whole house, Wotan stands in deep blue at the left of the rock with
his spear beside him, and the sisters' trembling knot hides Brünnhilde's dimmed silver.

She comes forward. Her own motif (Donington 88), quietly, on a horn: her silver grows and steps out from the
knot toward him while the sisters draw back behind her. Wotan pronounces her punishment over his grief (82),
slow, in the trombones and horns over low strings: every long note a slow wave of deep blue rolling out from
him over the rock. She is no longer a Valkyrie. As he says it the descending chords (22b) fall softly in the
woodwinds and strings, and her gold glints go out one by one. She will lie asleep here on the rock for the
first man who finds her: the magic sleep (16) in the woodwinds, its sliding chords breathing soft violet over
the porch, and she sinks to her knees, her light dimming.

The sisters wail, falling cries on violins and piccolo, their lights flaring and leaning toward her; he
threatens any who stay with her with the same fate, a thunderclap and his spear (73) flashing out. They
scatter in terror, four galloping out the free end of Right and four away along the Left wing and Side, a
last broken scrap of the Ride going with them. The two are left alone. The storm drains away: the thunderhead
thins, the clouds over the wings turn slowly to evening rose and blue, the rock to dark slate washed with
dusk violet, and the music settles to a quiet E major.

compose() holds every note, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.leitmotifs import play

CODE = 'WK24'
TITLE = 'The Sentence'
KIND = 'show'
DESCRIPTION = ('Brünnhilde steps out to face her father, and Wotan pronounces her sentence: she is no longer a '
               'Valkyrie, and she will sleep on this rock until the first man who finds her wakes her. Her '
               'sisters flee in terror, and the storm dies away into evening.')
VOICEOVER = ('She comes out from behind her sisters and stands in front of her father. '
             'Now he tells her what she has lost.')

T_FORWARD = 1.0                             # she comes forward
HBEAT = 0.6
T_GRIEF = 8.0                               # Wotan's grief: the sentence
GBEAT = 0.8
T_FALL = 19.0                               # no longer a Valkyrie: the descending chords
T_SLEEP = 31.0                              # the magic sleep
SLBEAT = 0.6
T_KNEEL = 36.0
WAILS = [43.0, 44.4, 45.6, 46.9, 48.0, 49.2]
T_THREAT = 51.6                             # he threatens them
T_SCATTER = 55.0                            # they flee
T_ALONE = 60.0
T_EVE = 60.0                                # the storm turning to evening
D = 80.0
CLOCK = 80.0 * 23

COLS = [hexc(h) for h in ('#ff4040', '#ff9a20', '#f0e040', '#40e070', '#40d0ff', '#6060ff', '#c050ff', '#ff60c0')]
KNOT = ('Porch Front', 0.66)
RING = [-60, -44, -28, -12, 12, 28, 44, 60]
WOTAN_C = hexc('#1a3cff')
WBLUE = WOTAN_C
SPEAR = hexc('#c8d8ff')
SILVER = hexc('#f4f8ff')
GOLD = hexc('#ffd060')
SLEEP = hexc('#7a6aff')
THUNDER = hexc('#060a24')
CLOUD = hexc('#2a3448')
STORM = hexc('#5a6a8a')
ROCK = hexc('#343c50')
NAVY = hexc('#0c1438')
FLASH = hexc('#e0e8ff')
WHITE = hexc('#ffffff')
# the evening stage, exactly as Was It So Shameful? (WK25) begins
ECLOUD, EVE, NIGHT = hexc('#3a4c96'), hexc('#b8488e'), hexc('#2232a0')
EROCK, DUSK = hexc('#38468a'), hexc('#7a40d0')


def at(G, seg, u):
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


def compose():
    """Every note: (time, seconds, midi, velocity, part, who)."""
    N = []

    def add(t, d, m, v, part, who=None):
        N.append((float(t), float(d), note(m) if isinstance(m, str) else int(m), int(v), part, who))

    add(0.0, T_GRIEF + 2.0, 'D2', 84, 'trem')                                   # the storm, still roaring
    for k in range(2):
        for t, m, v, d in play('storm', 0.2 + k * 3.6, 0.3, 0, 96 - 10 * k):
            add(t, d * 1.05, m, v, 'storm')
    for t, m, v, d in play('brunnhilde', T_FORWARD + 0.6, HBEAT, 0, 88):        # "Hier bin ich, Vater"
        add(t, d, m, v, 'here' if m >= note('Eb4') else 'herelow')
    for t, m, v, d in play('wotan_grief', T_GRIEF, GBEAT, -12, 104):            # the sentence
        add(t, d * 1.02, m, v, 'grief')
    for b, ch in ((0, ('E2', 'B2', 'G3')), (4, ('D2', 'A2', 'F#3')), (11, ('C2', 'G2', 'E3')), (16, ('D2', 'A2', 'F3')),
                  (20, ('A1', 'E2', 'C3')), (24, ('E2', 'B2', 'G#3'))):
        b1 = {0: 4, 4: 11, 11: 16, 16: 20, 20: 24, 24: 28}[b]
        for m in ch:
            add(T_GRIEF + b * GBEAT, (b1 - b) * GBEAT * 1.05, m, 72, 'griefpad')
    for t, m, v, d in play('valkyries_descent', T_FALL, 0.9, -12, 82):          # no longer a Valkyrie
        add(t, d * 1.3, m, v, 'fall')
    for t, m, v, d in play('sleep', T_SLEEP, SLBEAT, 0, 74):                    # she will sleep on the rock
        add(t, d * 1.05, m, v, 'sleep')
    for i, tw in enumerate(WAILS):                                              # the sisters wail
        top = note('E5') - i
        for j in range(4):
            add(tw + j * 0.14, 0.3, top - j, 96 - 4 * j, 'wail', (4, 0, 6, 2, 7, 1)[i])
    add(WAILS[0], T_THREAT - WAILS[0], 'E3', 74, 'plead')
    add(WAILS[0], T_THREAT - WAILS[0], 'G3', 70, 'plead')
    add(T_THREAT - 0.8, 0.8, 'D1', 104, 'surge')
    add(T_THREAT, 2.5, 'D1', 124, 'thunder')
    for t, m, v, d in play('spear', T_THREAT + 0.1, 0.34, 0, 118):
        if t < T_THREAT + 0.1 + 6 * 0.34:
            add(t, d * 1.1, m, v, 'spear')
    for k in range(2):                                                          # they scatter
        for t, m, v, d in play('ride', T_SCATTER + 0.3 + k * 1.8, 0.3, 3 * k, 100 - 12 * k):
            add(t, d * 1.4, m, v, 'ride', 4 if k == 0 else 0)
    for h in range(14):
        add(T_SCATTER + 0.3 + h * 0.45, 0.1, 'B1', 88 - 4 * h, 'hoof', 4 if h % 2 else 0)
    for t, m, v, d in play('wotan_grief', T_ALONE + 1.0, 1.0, -12, 78):         # alone: his grief, once more, softly
        if t < T_ALONE + 1.0 + 11 * 1.0:
            add(t, d * 1.02, m, v, 'grief')
    for m in ('E2', 'B2', 'E3', 'G#3'):                                         # evening: a quiet E major
        add(T_ALONE + 4.0, D - T_ALONE - 4.0, m, 60, 'evening')
    for ts in (3.0, 6.5, 14.0, 24.5):
        add(ts, 2.0, 'D1', 96, 'distant')
    return sorted(N, key=lambda e: e[0])


def follow(target, rate):
    """Critically damped chase of a target track (per frame), `rate` in 1/s per frame."""
    x = np.empty_like(target)
    x[0], v = target[0], 0.0
    for f in range(1, len(target)):
        w = rate[f]
        v += (w * w * (target[f] - x[f - 1]) - 2 * w * v) * DT
        x[f] = x[f - 1] + v * DT
    return x


def tremble(k, tt):
    """A sister shaking in the knot (as in the last scene)."""
    return 3.5 * np.sin(2 * np.pi * (5.3 * tt + k / 8)) + 2.0 * np.sin(2 * np.pi * (8.1 * tt + k / 3))


def choreography(G):
    """Per frame: the sisters, Brünnhilde and Wotan (path distance)."""
    F = nframes(D)
    t = np.arange(F) * DT
    L = G.length
    tt = t + CLOCK
    K = at(G, *KNOT)
    pos = np.zeros((8, F))
    for k in range(8):
        knot = K + RING[k] + tremble(k, tt)
        lo_ = smoothstep(T_FORWARD, T_FORWARD + 3.0, t)
        back = knot + (90 + 0.3 * RING[k]) * lo_                                 # drawing back behind her, loosening
        lean = -18 * sum(np.exp(-((t - w - 0.3) / 0.5) ** 2) for w in WAILS)    # leaning toward her as they wail
        go = T_SCATTER + 0.35 * (k % 4)
        away = (L + 160) if k >= 4 else -160.0
        flee = follow(np.where(t < go, back + lean, away), np.full(F, 2.0))
        pos[k] = np.where(t < go, back + lean, flee)
    B = at(G, 'Porch Front', 0.55)
    bpos = K + (B - K) * smoothstep(T_FORWARD + 0.5, T_FORWARD + 4.5, t)
    wpos = np.full(F, at(G, 'Porch Front', 0.3))
    return dict(t=t, pos=pos, bpos=bpos, wpos=wpos)


def rock_bed(d, tt, porch, stone):
    """Act III: storm clouds billowing over the wings and Side, the still, dark rock on the porch (shared by WK19-WK24)."""
    c1 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 430 - 0.03 * tt))
    c2 = 0.5 + 0.5 * np.cos(2 * np.pi * (d / 160 + 0.055 * tt) + 1)
    billow = 0.6 * c1 + 0.4 * c1 * c2
    wing = 1 - porch
    return (light(CLOUD, (0.38 + 0.62 * billow ** 1.5) * wing) + light(STORM, 0.6 * billow ** 3 * wing)
            + light(NAVY, 0.4 * wing) + light(ROCK, 0.6 * stone * porch) + light(NAVY, 0.4 * porch))


def thunderhead(fr, d, tt, front, amt):
    """Wotan's storm: a blue-black mass rolling in past `front` (path distance), a roaring blue edge (WK22-WK24).
    amt may be per pixel."""
    inside = 1 / (1 + np.exp(-(d - front) / 45))
    churn = (0.5 + 0.5 * np.cos(2 * np.pi * (d / 330 + 0.17 * tt))) * (0.6 + 0.4 * np.cos(2 * np.pi * (d / 140 - 0.29 * tt)))
    edge = np.exp(-((d - front) / 70) ** 2)
    fr = fr * (1 - 0.75 * amt * inside)[:, None]
    return (fr + light(THUNDER, 0.9 * amt * inside) + light(WBLUE, amt * (0.1 + 0.55 * churn ** 2) * inside)
            + light(WBLUE, 0.7 * amt * edge * (0.7 + 0.3 * churn)))


def stage(d, ta, porch):
    """The rock (porch) and the evening sky over the wings, on the opera's clock ta (as WK25-WK30 have it)."""
    bt = ta - 1920.0
    rock = np.interp(bt, [0, 160, 240, 320, 400, 480], [.42, .42, .43, .38, .34, .3])
    sky = np.interp(bt, [0, 80, 160, 240, 320, 480], [.4, .41, .41, .38, .34, .3])
    eve = np.interp(bt, [0, 80, 160, 240], [.45, .85, 1.0, .9])
    night = np.interp(bt, [200, 320, 400], [0.0, .6, .85])
    u = 0.5 + 0.3 * np.sin(2 * np.pi * (d / 520 - 0.011 * ta)) + 0.2 * np.sin(2 * np.pi * (d / 190 + 0.023 * ta) + 1.1)
    sk = ECLOUD + (EVE - ECLOUD) * (eve * (0.35 + 0.65 * u))[:, None]
    sk = sk + (NIGHT - sk) * night
    rk = EROCK + (DUSK - EROCK) * (0.25 + 0.45 * u)[:, None]
    return light(sk, sky * (0.7 + 0.3 * u) * (1 - porch)) + light(rk, rock * (0.8 + 0.2 * u) * porch)


def render(G, seed=24):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    L = G.length
    C = choreography(G)
    N = compose()
    porch = np.isin(G.seg_of, ['Porch Left', 'Porch Front', 'Porch Right']).astype(float)
    stone = 0.8 + 0.2 * np.interp(d / 18, np.arange(int(L / 18) + 2), np.random.default_rng(30).uniform(-1, 1, int(L / 18) + 2))
    jag = [0.55 + 0.45 * np.random.default_rng(100 + k).random(G.N) for k in range(8)]
    K = at(G, *KNOT)
    here = np.array([e[0] for e in N if e[4] == 'here'])
    grief = [(e[0], e[1]) for e in N if e[4] == 'grief' and e[1] >= 2.5]
    fall = sorted({e[0] for e in N if e[4] == 'fall'})
    sleep = sorted({e[0] for e in N if e[4] == 'sleep'})
    wail = [np.array([e[0] for e in N if e[4] == 'wail' and e[5] == k]) for k in range(8)]
    spear_t = np.array([e[0] for e in N if e[4] == 'spear'])
    tw = Flicker(rng, G.N, 1.5, 5.0)

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    def last(arr, t, tau, span=2.0):
        i = int(np.searchsorted(arr, t, side='right')) - 1
        return float(np.exp(-(t - arr[i]) / tau)) if i >= 0 and t - arr[i] < span else 0.0

    def bolt(age, a, b, k):
        """A fork of lightning from a to b: grows in 60 ms, flickers three times, gone in a second."""
        if not 0 <= age < 1.0:
            return np.zeros(G.N)
        reach = a + (b - a) * min(1.0, age / 0.06)
        lo, hi = min(a, reach), max(a, reach)
        fl = sum(np.exp(-((age - s) / 0.04) ** 2) for s in (0.0, 0.12, 0.3)) + 0.45 * np.exp(-age / 0.3)
        return ((d >= lo) & (d <= hi)) * jag[k % len(jag)] * min(fl, 1.2)

    for f in range(F):
        t = f * DT
        tt = t + CLOCK
        pw, pb = C['wpos'][f], C['bpos'][f]

        # the storm, holding, then draining away into the evening of the next scene
        calm = smoothstep(T_EVE - 4, T_ALONE + 10, t)
        amt = (1 - calm) * (1 - 0.5 * porch)
        storm = thunderhead(rock_bed(d, tt, porch, stone), d, tt, -120.0, amt)
        sw = ((t + 80 - 0.2) / 3.6) % 1.0
        storm += light(WBLUE, 0.5 * (1 - calm) * (1 - sw) * np.exp(-((np.abs(d - pw) - 1600 * sw) / 160) ** 2) * (1 - 0.6 * porch))
        eve = smoothstep(T_EVE, D - 1.5, t)
        fr = storm * (1 - eve) + stage(d, tt, porch) * eve

        # the sentence: each long note of his grief a slow wave of deep blue rolling out over the rock
        for tg, dg in grief:
            if tg <= t < tg + 3.0:
                age = t - tg
                r = 40 + 900 * smoothstep(0, 2.6, age)
                fr += light(WBLUE, 0.65 * (1 - age / 3.0) * np.exp(-((np.abs(d - pw) - r) / 150) ** 2))
        # the descending chords: bands of pale light falling over her from the ends of the porch
        for td in fall:
            if td <= t < td + 1.5:
                age = t - td
                j = fall.index(td)
                q = pb + (1 - 2 * (j % 2)) * (520 - 55 * j)
                fr += light(FLASH * 0.5 + GOLD * 0.3, 0.5 * np.exp(-age / 0.5) * blob(q, 90))
        # the magic sleep: soft violet breathing over the porch, centred on her
        sl = smoothstep(T_SLEEP - 1, T_SLEEP + 3, t) * (1 - smoothstep(T_SLEEP + 13, T_SCATTER, t))
        if sl > 0:
            sp = last(np.array(sleep), t, 0.9, 3.0)
            br = 0.6 + 0.4 * np.sin(2 * np.pi * (np.abs(d - pb) / 300 - 0.12 * tt))
            fr += light(SLEEP, sl * (0.5 + 0.25 * sp) * br * (0.35 + 0.65 * porch) * (0.5 + 0.5 * blob(pb, 400)))

        # Wotan: from the god of the storm, spear at his side, to the father alone with her at evening
        th = smoothstep(T_THREAT - 0.1, T_THREAT + 0.1, t) * np.exp(-max(t - T_THREAT, 0) / 1.2)
        sp_ = last(spear_t, t, 0.3, 1.0)
        soft = smoothstep(T_ALONE, D - 2.0, t)
        wb = 0.85 + 0.3 * th
        storm_w = light(WOTAN_C, wb * blob(pw, 34) + 0.35 * wb * blob(pw, 180))
        eve_w = light(WOTAN_C, 0.85 * blob(pw, 24) + 0.3 * blob(pw, 90))
        fr += storm_w * (1 - soft) + eve_w * soft
        fr += light(SPEAR, (1 - soft) * (0.55 + 0.4 * th + 0.3 * sp_) * smoothstep(pw + 20, pw + 40, d)
                    * smoothstep(pw + 150 + 300 * th, pw + 120 + 300 * th, d))
        if T_THREAT <= t < T_THREAT + 1.0:
            age = t - T_THREAT
            fr += light(WHITE, 0.8 * bolt(age, pw, L, 1) + 0.8 * bolt(age, pw, 0.0, 2))
            fr += light(FLASH, 0.45 * np.exp(-age / 0.15) * np.ones(G.N))

        # Brünnhilde: hidden and dim; stepping out, bright; her godhood going, glint by glint; kneeling
        fwd = smoothstep(T_FORWARD + 0.5, T_FORWARD + 3.0, t)
        hp = last(here, t, 0.4, 1.5)
        kneel = smoothstep(T_KNEEL, T_KNEEL + 6.0, t)
        lvl = 0.45 + 0.35 * fwd - 0.3 * kneel + 0.15 * hp
        hidden = 1 - fwd
        core_w = 9 + 11 * fwd
        halo = 0.135 / 0.45 * (1 - fwd) + 0.22 / 0.5 * fwd
        halo_w = 30 + 50 * fwd
        fr += light(SILVER, lvl * blob(pb, core_w) + halo * lvl * blob(pb, halo_w))
        gone = int(np.searchsorted(np.array(fall), t, side='right'))           # a glint goes out with every chord
        kept = max(0, 3 - gone // 3)
        gl = 0.3 * hidden + 0.65 * fwd
        for kg in range(kept):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, gl * blob(q, 5) * (1 - smoothstep(T_FALL, T_FALL + 4, t) * (kg == kept - 1) * 0))
        faint = smoothstep(T_FALL + 4, T_KNEEL + 4, t)
        if faint > 0:                                                            # what is left: a faint scatter of gold
            g = (rng.random(G.N) < 0.05) * blob(pb, 40)
            fr += light(GOLD, 0.25 * faint * g)

        # the sisters: drawing back behind her, wailing, leaning toward her; then gone in terror
        for k in range(8):
            p = C['pos'][k][f]
            vis = smoothstep(-150, 0, p) * smoothstep(L + 150, L, p)
            if vis <= 0:
                continue
            wl = last(wail[k], t, 0.25, 1.2)
            loose = smoothstep(T_FORWARD, T_FORWARD + 3.0, t)
            b = vis * (0.8 + 0.35 * wl + 0.3 * th)
            fr += light(COLS[k], b * blob(p, 8 + 3 * loose) + (0.15 + 0.05 * loose) * b * blob(p, 30 + 10 * loose))
            if t > T_SCATTER and abs(p - C['pos'][k][max(f - 4, 0)]) > 8:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 26, 2)):
                    trail = np.maximum(trail, blob(C['pos'][k][max(f - lag, 0)], 20) * (1 - j / 12.5))
                fr += light(COLS[k], 0.7 * vis * trail)
            for tc in wail[k]:
                if tc <= t < tc + 0.8:
                    age = t - tc
                    r = 15 + 200 * age ** 0.7
                    fr += light(COLS[k], 0.4 * (1 - age / 0.8) * np.exp(-((np.abs(d - p) - r) / 22) ** 2))
        if t < T_FORWARD + 3.0:                                                 # the knot's glow, opening
            fr += light(SILVER * 0.4 + WBLUE * 0.2, 0.2 * (1 - smoothstep(T_FORWARD, T_FORWARD + 3.0, t)) * blob(K, 90))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    from pixelhome.audio import SR, whoosh
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(float(np.clip(np.interp(t, C['t'], C['pos'][k]), 0, G.length)))

    for name, gain, rev in (('brass', 0.25, 0.32), ('low', 0.25, 0.22), ('strings', 0.23, 0.38), ('winds', 0.23, 0.4),
                            ('perc', 0.22, 0.3), ('fx', 0.1, 0.3)):
        M.bus(name, gain=gain, reverb=rev)
    horn = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tbn = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    vn = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Violin Section/Trem/*.wav', tune=-12)
    va = M.sampler('Strings/Viola Section/susvib/*.wav', tune=-12)
    vc = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    vcs = M.sampler('Strings/Cello Section/spic/*.wav', tune=-12)
    trem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    cb = M.sampler('Strings/Solo Contrabass/SusNV/*.wav', tune=-12)
    cbs = M.sampler('Strings/Solo Contrabass/Spic/*.wav', tune=-12)
    fl = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    ob = M.sampler('Woodwinds/Oboe/Vib/*.wav', tune=-12)
    cl = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/sus/*.wav', tune=-12)
    pic = M.sampler('Woodwinds/Piccolo/Stac/*.wav', tune=-12)
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    roll = M.hits('Percussion/Timpani/Rolls/*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[3-6]*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    snare = M.hits('Percussion/Snare2-taps_v[1-3]*.wav')

    def hold(bus, s, m, t0, t1, vel, pan=0.0, step=2.5, rise=0.8, fall=1.0, gain=1.0):
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
            M.add(bus, a * e, t, gain, pan)
            t += step

    wp = pan_at(at(G, 'Porch Front', 0.3))
    bp = pan_at(at(G, 'Porch Front', 0.55))
    for t, d, m, v, part, who in compose():
        if part == 'trem':
            hold('low', trem, m + 12, t, t + d, v, 0.0, rise=0.05, fall=3.0, gain=0.55)
        elif part == 'storm':
            M.add('low', cbs.play(m + 12, v), t, 0.7, -0.15)
            M.add('low', vcs.play(m + 12, v - 6), t, 0.6, 0.15)
        elif part == 'distant':
            M.add('perc', roll.play(v - 20, dur=d), t, 0.5, -0.5 if t % 2 < 1 else 0.6)
        elif part == 'here':
            M.add('brass', horn.play(m, v, dur=d * 1.05, release=0.4), t, 0.85, bp)
        elif part == 'herelow':
            hold('strings', va if m >= note('C3') else vc, m, t, t + d, v - 20, bp, rise=0.4, fall=1.0, gain=0.4)
        elif part == 'grief':
            M.add('brass', tbn.play(m, v, dur=d, release=0.6), t, 0.85, wp)
            M.add('brass', horn.play(m, v - 14, dur=d, release=0.6), t, 0.45, wp)
        elif part == 'griefpad':
            s = cb if m < note('C2') else (vc if m < note('C3') else va)
            hold('strings', s, m + (12 if s is cb else 0), t, t + d, v, 0.0, rise=0.6, fall=1.2, gain=0.45)
        elif part == 'fall':
            if m >= note('C5'):
                M.add('winds', fl.play(m - 12, v, dur=d, release=0.5), t, 0.6, bp)
            elif m >= note('A3'):
                M.add('strings', vn.play(m, v - 6, dur=d, release=0.5), t, 0.5, bp)
            else:
                M.add('winds', bsn.play(m, v - 6, dur=d, release=0.5), t, 0.6, bp)
        elif part == 'sleep':
            s = fl if m >= note('Bb4') else (ob if m >= note('Eb4') else (cl if m >= note('B2') else bsn))
            M.add('winds', s.play(m, v - (8 if s is fl else 0), dur=d, release=0.6), t, 0.5, bp)
        elif part == 'wail':
            pa = pan_of(who, t)
            M.add('strings', vn.play(m, v, dur=d, release=0.15), t, 0.6, pa)
            M.add('winds', pic.play(m, v - 10), t, 0.35, pa)
        elif part == 'plead':
            hold('strings', vtrem, m + 12, t, t + d, v, 0.3, rise=1.0, fall=0.4, gain=0.4)
        elif part == 'surge':
            M.add('perc', roll.play(v, dur=d + 0.2), t, 0.8, wp)
        elif part == 'thunder':
            M.add('perc', crash.play(v), t, 0.8, wp)
            M.add('perc', bd.play(v), t, 0.9, wp)
            M.add('perc', timp.play(v, pitch=-6), t, 0.9, wp)
            M.add('fx', whoosh(1.2, 2500, 200, 0.6, seed=51), t, 0.6, wp)
        elif part == 'spear':
            M.add('brass', tbn.play(m, v, dur=d, release=0.3), t, 1.0, wp)
            M.add('low', tuba.play(m - 12, v - 6, dur=d, release=0.3), t, 0.8, wp)
        elif part == 'ride':
            M.add('brass', horn.play(m, v, dur=d, release=0.15), t, 0.8, pan_of(who, t))
        elif part == 'hoof':
            M.add('perc', snare.play(v), t, 0.5, pan_of(who, t))
        elif part == 'evening':
            s = cb if m < note('B2') else (vc if m < note('E3') else va)
            hold('strings', s, m + (12 if s is cb else 0), t, t + d, v, 0.0, rise=3.0, fall=1.0, gain=0.5)
