"""Grand Finale: the curtain call. The ten numbers come back one after another, each with its own hook,
style and colour, and each brings its character out onto its own stretch of roof, left to right in
story order: the jack-o'-lantern (march), the ghost dog chasing its bone (rag), a cluster of Christmas
bulbs while bulbs ping on across the whole house (waltz), the scientist with his ornament shattering and
his gold idea bulb lighting (patter), the rag doll's hop-step-close (polka), the jack-in-the-box popping
while hammers ring the corners (swing), the three troublemakers tiptoeing (shuffle), the lumpy sack
laughing in blacklight (boogie), the sleigh streaking the length of the house as snow starts (anthem),
and presents popping everywhere (galop). By then the whole cast stands in a line, and the march and the
anthem play at once while orange, red and green dance between them under the snow. Everyone bows three
times, a burst runs out from the porch, the house goes bright on the last chord, and a last button hit.

Every character stands and enters on the front runs; Side, which the street never sees, only carries fill
(bulbs, snow, colour). The sleigh streaks in off the free end of Right and out along Side.

Characters are spans in path distance drawn with exact span-over-pixel coverage, so they keep their size
on every run. Every time is a module constant (or computed from SECTIONS), shared with score()."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, nframes

CODE = 'NB11'
TITLE = 'Grand Finale'
KIND = 'show'
DESCRIPTION = ('The curtain call: every number comes back with its tune and its character, until the whole cast '
               'is lined up along the roof, dancing in orange, red and green under the snow, for one last bow.')

# ---- the running order: (style, BPM, beats played, beats a bar) ----
SECTIONS = [('march', 120, 16, 4), ('rag', 96, 8, 4), ('waltz', 150, 12, 3), ('patter', 144, 16, 2),
            ('polka', 126, 16, 2), ('swing', 132, 16, 4), ('shuffle', 120, 8, 4), ('boogie', 120, 16, 4),
            ('anthem', 84, 8, 4), ('galop', 150, 16, 2)]
INTRO = 2.5
CP_BPM, CP_BEATS = 120, 16                  # the counterpoint: the march against the anthem, in D major


def _times():
    t, out = INTRO, []
    for _, bpm, beats, _ in SECTIONS:
        out.append(t)
        t += beats * 60 / bpm
    return out, t


START, TCP = _times()                       # each section's downbeat; the counterpoint
TBOW = TCP + CP_BEATS * 60 / CP_BPM         # three bows, half a second apart
BOWS = (TBOW, TBOW + 0.5, TBOW + 1.0)
TEND = TBOW + 2.0                           # the last chord
TBUTTON = TEND + 3.5                        # the button
D = TBUTTON + 2.0


def slots(G):
    """Where each number's character stands: ten even slots along the front runs (Left to the free end of
    Right). Side is never watched from the street, so nothing stands, enters or appears there."""
    f0, f1 = G.pd[G.seg['Side']].max() + 30, G.length - 30
    return [f0 + (k + 0.5) * (f1 - f0) / 10 for k in range(10)]


def sleigh_lead(G, u):
    """The sleigh's nose during the anthem streak (u 0..1): in off the free end of Right, the length of the
    house, and out along Side."""
    return G.length + 60 - (G.length + 360) * smoothstep(0, 1, u)
CORNERS = (80.5, 178.5, 260.5, 331.5, 380.5)


def sb(i, b):
    """Time of beat b of section i."""
    return START[i] + b * 60 / SECTIONS[i][1]


def grid(t):
    """(time of beat 0, seconds a beat) of whatever is playing at t."""
    if t < INTRO:
        return 0.0, 0.5
    for i in range(len(SECTIONS) - 1, -1, -1):
        if t >= START[i] and t < TCP:
            return START[i], 60 / SECTIONS[i][1]
    return TCP, 60 / CP_BPM


ORANGE = hexc('#ff5200')
EYE = hexc('#ffd040')
STEM = hexc('#30c020')
GHOST = hexc('#c8d8ff')
NOSE = hexc('#ff2a08')
BONE = hexc('#fff0d6')
BULBS = [hexc(c) for c in ('#ff1a10', '#10d040', '#ffb020', '#2050ff', '#ff5a00')]
PALE = hexc('#eef2ff')
GOLD = hexc('#ffb020')
RED = hexc('#ff1a10')
GREEN = hexc('#10d040')
HAIR = hexc('#ff2008')
DOLL_BLUE = hexc('#2a50ff')
PLUM = hexc('#a01a70')
BOX = hexc('#10b040')
SPRING = hexc('#e0e0e0')
TROUBLE = [hexc('#ff6a00'), hexc('#8a20ff'), hexc('#d8ffe8')]
BURLAP = hexc('#c08a40')
LIME = hexc('#9aff00')
UV = hexc('#4a00ff')
SNOW = hexc('#f0f4ff')
HAMMER = hexc('#fff0c0')
WASH = [hexc(c) for c in ('#ff4000', '#6080ff', '#ffb020', '#20c0a0', '#a01a70', '#ff1a10', '#8a20ff', '#4a00ff',
                          '#ffb020', '#ff1a10')]


def _back(u, c1=1.6):
    u = np.clip(u, 0, 1)
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def _events(G):
    """The random parts, shared by render() and score(): the bulbs' ping groups, the galop's presents, the
    snowflakes."""
    rng = np.random.default_rng(1111)
    L = G.length
    bc = np.arange(12.0, L, 24.0)
    rank = np.argsort(np.argsort(np.abs(bc - slots(G)[2])))
    group = rank * SECTIONS[2][2] // len(bc)              # pinged on beat `group` of the waltz
    nb = SECTIONS[9][2]
    gift_x = rng.uniform(G.pd[G.seg['Side']].max() + 60, L - 60, nb)     # presents only pop on the front
    gift_c = rng.integers(0, len(BULBS), nb)
    S = 1000
    flake_t = np.sort(rng.uniform(START[8], TBUTTON, S))
    flake_px = rng.integers(0, G.N, S)
    flake_l = rng.uniform(0.8, 1.8, S)
    return dict(bc=bc, group=group, gift_x=gift_x, gift_c=gift_c, flake_t=flake_t, flake_px=flake_px,
                flake_l=flake_l)


def render(G, seed=111):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd[G.path]
    L = G.length
    mid = G.pd[G.seg['Porch Front']].mean()
    m = (d[1:] + d[:-1]) / 2
    lo = np.r_[d[0] - (d[1] - d[0]) / 2, m]
    hi = np.r_[m, d[-1] + (d[-1] - d[-2]) / 2]
    slot = slots(G)
    front = np.ones(G.N, bool)
    front[G.pi[G.seg['Side']]] = False
    corner = np.interp(CORNERS, np.arange(G.N), d)
    ev = _events(G)
    bc, group = ev['bc'], ev['group']
    bshape = np.zeros((len(bc), G.N))
    for j, c in enumerate(bc):
        bshape[j] = np.exp(-((d - c) / 6.0) ** 2)
    bcol = np.array([BULBS[j % len(BULBS)] for j in range(len(bc))])
    bping = np.array([sb(2, g) for g in group])
    bph = np.random.default_rng(5).uniform(0, 2 * np.pi, len(bc))

    def cov(a, z):
        return np.clip((np.minimum(z, hi) - np.maximum(a, lo)) / (hi - lo), 0, 1)

    def add(fr, a, z, col, I):
        if I > 0.002:
            fr += light(col, I * cov(a, z))

    def presence(k, t):
        """Size and brightness of character k: pops in on its downbeat, leads its own section, stands by
        dimmer after, back at full for the counterpoint, bows, and shines to the end."""
        if t < START[k]:
            return 0.0, 0.0
        s = _back((t - START[k]) / 0.35)
        end = START[k + 1] if k + 1 < len(START) else TCP
        b = 1.0 if t < end else keys(t, [(end, 1.0), (end + 0.6, 0.5), (TCP - 0.5, 0.5), (TCP, 1.0)])
        for tb in BOWS:
            u = (t - tb) / 0.45
            if 0 < u < 1:
                s *= 1 - 0.4 * np.sin(np.pi * u)
        b *= keys(t, [(TBUTTON + 0.3, 1), (D - 0.2, 0)])
        return s, b

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        g0, gb = grid(t)
        ph = ((t - g0) / gb) % 1
        beat = int((t - g0) // gb)
        pulse = np.exp(-ph * gb / 0.12)

        # the intro: a glow gathering over the porch
        if t < INTRO + 0.5:
            add(fr, mid - 40, mid + 40, GOLD, keys(t, [(0, 0), (2.3, 0.45), (INTRO, 0.6), (INTRO + 0.5, 0)]))
            # the wings and the rest of the front glow warm from the first moment
            fr += light(ORANGE, keys(t, [(0, 0.06), (INTRO, 0.14), (INTRO + 0.5, 0)]) * front)

        # each section's own colour, low under everything
        for i in range(len(SECTIONS)):
            end = START[i + 1] if i + 1 < len(START) else TCP
            w = keys(t, [(START[i] - 0.2, 0), (START[i] + 0.2, 1), (end - 0.2, 1), (end + 0.2, 0)])
            if w > 0:
                fr += light(WASH[i], 0.13 * w * np.ones(G.N))

        # the bulbs: ping on across the house in the waltz, stay as a low string of lights after
        if t >= START[2]:
            on = smoothstep(bping, bping + 0.1, t)
            pop = np.where(t >= bping, 0.5 * np.exp(-(t - bping) / 0.25), 0)
            lev = keys(t, [(START[3], 0.5), (START[3] + 0.6, 0.07), (TCP - 0.5, 0.07), (TCP, 0.16), (TEND, 0.16),
                           (TEND + 0.3, 0.55), (TBUTTON + 0.3, 0.4), (D - 0.2, 0)])
            if t < START[3]:
                lev = 0.5
            tw = 1 + 0.2 * np.sin(2.1 * t + bph)
            I = (on * lev * tw + pop)[:, None] * bshape
            fr += ((np.clip(I, 0, None) ** 2.2)[..., None] * bcol[:, None, :]).sum(0)

        # snow from the anthem on
        if t >= START[8]:
            live = (ev['flake_t'] <= t) & (t < ev['flake_t'] + ev['flake_l'])
            u = (t - ev['flake_t'][live]) / ev['flake_l'][live]
            sn = np.zeros(G.N)
            np.maximum.at(sn, ev['flake_px'][live], 0.45 * np.sin(np.pi * u) ** 2)
            fr += light(SNOW, sn * keys(t, [(TBUTTON, 1), (D - 0.2, 0)]))

        # ---- the cast ----
        bob = 6 * np.sin(2 * np.pi * ph)

        s, b = presence(0, t)                               # the jack-o'-lantern
        if b > 0:
            c = slot[0] + bob
            k = s * (1 + (0.18 * pulse if START[0] <= t < START[1] else 0))
            add(fr, c - 28 * k, c + 28 * k, ORANGE, 0.5 * b)
            add(fr, c - 15 * k, c - 7 * k, EYE, 0.8 * b)
            add(fr, c + 7 * k, c + 15 * k, EYE, 0.8 * b)
            add(fr, c + 28 * k, c + 34 * k, STEM, 0.5 * b)

        s, b = presence(1, t)                               # the ghost dog and his bone
        if b > 0:
            c = slot[1]
            if START[1] <= t < START[2]:
                u = ((t - START[1]) / (2 * 60 / 96)) % 1
                side = 1 if int((t - START[1]) / (2 * 60 / 96)) % 2 == 0 else -1
                bx = c + side * 110 * np.sin(np.pi * u)
                c = c + side * 60 * np.sin(np.pi * np.clip(u - 0.15, 0, 1))
                add(fr, bx - 10, bx + 10, BONE, 0.6 * b)
                add(fr, bx - 13, bx - 9, BONE, 0.8 * b)
                add(fr, bx + 9, bx + 13, BONE, 0.8 * b)
            else:
                c = c + bob
                add(fr, c + 16 * s, c + 34 * s, BONE, 0.55 * b)
            wag = 4 * np.sin(2 * np.pi * 3 * t)
            add(fr, c - 24 * s, c + 10 * s, GHOST, 0.42 * b)
            add(fr, c - 38 * s + wag, c - 24 * s, GHOST, 0.25 * b)
            add(fr, c + 10 * s, c + 16 * s, NOSE, 0.85 * b)

        s, b = presence(2, t)                               # a cluster of bulbs
        if b > 0:
            for j, off in enumerate((-48, -24, 0, 24, 48)):
                c = slot[2] + off * s
                add(fr, c - 5, c + 5, BULBS[j], 0.6 * b * (0.85 + 0.15 * np.sin(3 * t + j)))

        s, b = presence(3, t)                               # the scientist: shattering ornaments, then his idea
        if b > 0:
            c = slot[3] + bob
            add(fr, c - 10 * s, c + 10 * s, PALE, 0.5 * b)
            if START[3] <= t < START[4]:
                bar, u = divmod((t - START[3]) / (2 * 60 / 144), 1)
                if int(bar) % 2 == 1:
                    add(fr, c + 16, c + 24, GOLD, 0.9 * b * np.exp(-u / 0.5))
                else:
                    if u < 0.25:
                        add(fr, c - 38, c - 28, RED, 0.6 * b)
                    else:
                        v = (u - 0.25) / 0.75
                        for sp in (-1, 1):
                            for r in (25, 45, 65):
                                x = c - 33 + sp * r * v
                                add(fr, x - 2, x + 2, GOLD if r == 45 else RED, 0.7 * b * (1 - v))
            else:
                add(fr, c + 16 * s, c + 24 * s, GOLD, 0.7 * b)

        s, b = presence(4, t)                               # the rag doll's hop-step-close
        if b > 0:
            c = slot[4] + bob
            if START[4] <= t < START[5]:
                bar, u = divmod((t - START[4]) / (2 * 60 / 126), 1)
                side = 1 if int(bar) % 2 == 0 else -1
                c = slot[4] + side * 28 * (2 * smoothstep(0, 0.5, u) - 1)
            for a, z, col in ((-30, -24, HAIR), (-24, -14, PALE), (-14, -4, DOLL_BLUE), (-4, 4, PLUM), (4, 14, DOLL_BLUE),
                              (14, 18, PALE), (18, 22, RED), (22, 26, PALE), (26, 30, RED)):
                add(fr, c + a * s, c + z * s, col, 0.55 * b)

        s, b = presence(5, t)                               # the jack-in-the-box, and the hammers
        if b > 0:
            c = slot[5]
            if START[5] <= t < START[6]:
                u = ((t - START[5]) / (4 * 60 / 132)) % 1
                ext = 55 * _back(u / 0.2) * (1 - smoothstep(0.7, 1.0, u))
                fr += light(HAMMER, 0.6 * pulse * np.exp(-((d - corner[beat % 5]) / 18) ** 2))
            else:
                ext = 40 + bob
            add(fr, c - 22 * s, c + 6 * s, BOX, 0.5 * b)
            add(fr, c - 22 * s, c - 18 * s, RED, 0.6 * b)
            for x in np.arange(c + 8, c + 6 + ext, 7):
                add(fr, x, x + 3, SPRING, 0.4 * b)
            add(fr, c + 6 + ext, c + 16 + ext, PALE, 0.6 * b * s)
            add(fr, c + 16 + ext, c + 19 + ext, RED, 0.8 * b * s)

        s, b = presence(6, t)                               # the three troublemakers, tiptoeing
        if b > 0:
            e8 = int((t - g0) / (gb / 2))
            for j, off in enumerate((-36, 0, 36)):
                hop = 8 if (START[6] <= t < START[7] and e8 % 3 == j) else 0
                c = slot[6] + off * s + hop + (bob if t >= START[7] else 0)
                add(fr, c - 8 * s, c + 8 * s, TROUBLE[j], (0.55 + 0.25 * (hop > 0)) * b)

        s, b = presence(7, t)                               # the sack, laughing in blacklight
        if b > 0:
            c = slot[7]
            w = s * (1 + 0.08 * np.sin(2 * np.pi * ph))
            add(fr, c - 46 * w, c + 46 * w, BURLAP, 0.38 * b)
            add(fr, c - 16 * w, c - 8 * w, LIME, 0.8 * b)
            add(fr, c + 8 * w, c + 16 * w, LIME, 0.8 * b)
            if START[7] <= t < START[8]:
                fr += light(UV, 0.13 * np.ones(G.N))
                if beat % 2 == 1:
                    add(fr, c - 6 * w, c + 6 * w, LIME, 0.7 * pulse * b)
                    fr += light(LIME, 0.1 * pulse * np.ones(G.N))

        if START[8] <= t < START[9]:                        # the sleigh streaks the length of the house
            u = (t - START[8]) / (0.8 * (START[9] - START[8]))
            if u < 1:
                lead = sleigh_lead(G, u)
                trail = np.where(d > lead, np.exp(-(d - lead) / 160), 0) * (0.5 + 0.5 * np.sin(d * 0.9 + 30 * t)) ** 4
                fr += light(GOLD, 0.5 * trail)
                add(fr, lead - 4, lead + 4, NOSE, 0.9)
                for off in (30, 55, 80, 105):
                    add(fr, lead + off - 3, lead + off + 3, BONE, 0.5)
                add(fr, lead + 135, lead + 150, PALE, 0.55)
        s, b = presence(8, t)
        if t >= START[8] + 0.8 * (START[9] - START[8]):     # ...and the nose lands in its place
            s = _back((t - START[8] - 0.8 * (START[9] - START[8])) / 0.35)
            c = slot[8] + bob
            add(fr, c - 4 * s, c + 4 * s, NOSE, 0.9 * b)
            for off in (14, 24, 34, 44):
                add(fr, c - off * s - 2, c - off * s + 2, BONE, 0.45 * b)

        s, b = presence(9, t)                               # a present, and presents popping everywhere
        if b > 0:
            c = slot[9] + bob
            add(fr, c - 20 * s, c + 20 * s, RED, 0.5 * b)
            add(fr, c - 3 * s, c + 3 * s, GOLD, 0.8 * b)
            add(fr, c + 20 * s, c + 28 * s, GOLD, 0.7 * b)
        if START[9] <= t < TCP + 0.5:
            for j, (x, ci) in enumerate(zip(ev['gift_x'], ev['gift_c'])):
                u = t - sb(9, j)
                if 0 <= u < 0.6:
                    v = u / 0.6
                    add(fr, x - 14, x + 14, BULBS[ci], 0.75 * (1 - v))
                    for sp in (-1, 1):
                        for r in (30, 60, 90):
                            xx = x + sp * r * v
                            add(fr, xx - 3, xx + 3, BULBS[(ci + r // 30) % len(BULBS)], 0.75 * (1 - v))

        # the counterpoint: orange, red and green dancing between the cast
        if TCP <= t < TEND + 0.5:
            bar = int((t - TCP) / (4 * 60 / CP_BPM))
            dirn = 1 if bar % 2 == 0 else -1
            stripe = (((d + dirn * 140 * (t - TCP)) // 60).astype(int)) % 3
            lev = 0.16 * keys(t, [(TCP, 0), (TCP + 0.3, 1), (TEND, 1), (TEND + 0.4, 0)]) * (1 + 0.3 * pulse)
            for j, col in enumerate((ORANGE, RED, GREEN)):
                fr += light(col, lev * (stripe == j))

        # the last chord: a burst from the porch, the whole house bright for a moment, then the button
        if t >= TEND:
            u = t - TEND
            fr += light(GOLD, 0.9 * np.exp(-u / 1.2) * np.exp(-((np.abs(d - mid) - 1100 * u) / 60) ** 2))
            glow = keys(t, [(TEND, 0.85), (TEND + 0.8, 0.32), (TBUTTON, 0.3), (TBUTTON + 0.01, 0.7),
                            (TBUTTON + 0.5, 0.3), (D - 0.2, 0)])
            fr += light(hexc('#ffe0a0'), glow * np.ones(G.N))
        out[f][G.path] = fr
    return out


# ---- music: the medley. Each hook comes back in its own style and colour, following its character
# across the house (the lead is panned toward its slot), joined by pickups, fills, a stop-time gag and
# key lifts; then the Town Square march (in D major) against the Fog anthem (in D, at half speed), which
# share a progression; three bows; a big D major chord and a button. ----

TUNES = {                                   # (beat, note, beats), copied from each number
    'march': [(0, 'D4', 1), (1, 'F4', .5), (1.5, 'E4', .5), (2, 'D4', 1), (3, 'A3', 1), (4, 'Bb3', .5), (4.5, 'C4', .5),
              (5, 'D4', .5), (5.5, 'E4', .5), (6, 'F4', 1), (7, 'E4', 1), (8, 'G4', 1), (9, 'F4', .5), (9.5, 'E4', .5),
              (10, 'F4', 1), (11, 'D4', 1), (12, 'E4', .5), (12.5, 'C#4', .5), (13, 'A3', 1), (14, 'D4', 2)],
    'rag': [(0, 'G4', .5), (.5, 'B4', .5), (1, 'D5', .75), (1.75, 'B4', .25), (2, 'C5', .5), (2.5, 'D5', .5),
            (3, 'E5', 1), (4, 'D5', .5), (4.5, 'B4', .25), (4.75, 'G4', .75), (5.5, 'A4', .5), (6, 'B4', .5),
            (6.5, 'A4', .5), (7, 'G4', 1)],
    'waltz': [(0, 'A4', 1), (1, 'C5', 1), (2, 'F5', 1), (3, 'E5', 1.5), (4.5, 'D5', .5), (5, 'C5', 1), (6, 'D5', 1),
              (7, 'Bb4', 1), (8, 'G4', 1), (9, 'C5', 3)],
    'patter': [(0, 'G4', .5), (.5, 'G4', .5), (1, 'Bb4', .5), (1.5, 'A4', .5), (2, 'G4', .5), (2.5, 'F#4', .5),
               (3, 'G4', 1), (4, 'C5', .5), (4.5, 'C5', .5), (5, 'Bb4', .5), (5.5, 'A4', .5), (6, 'Bb4', .5),
               (6.5, 'A4', .5), (7, 'G4', 1), (8, 'D5', .5), (8.5, 'D5', .5), (9, 'C5', .5), (9.5, 'Bb4', .5),
               (10, 'A4', .5), (10.5, 'Bb4', .5), (11, 'C5', .5), (11.5, 'A4', .5), (12, 'Bb4', .5), (12.5, 'G4', .5),
               (13, 'F#4', .5), (13.5, 'A4', .5), (14, 'G4', 1), (15, 'D4', .5), (15.5, 'D4', .5)],
    'polka': [(0, 'D5', .5), (.5, 'A4', .5), (1, 'F#4', .5), (1.5, 'A4', .5), (2, 'D5', .5), (2.5, 'E5', .25),
              (2.75, 'F#5', .25), (3, 'E5', 1), (4, 'C#5', .5), (4.5, 'A4', .5), (5, 'E4', .5), (5.5, 'A4', .5),
              (6, 'C#5', .5), (6.5, 'D5', .25), (6.75, 'E5', .25), (7, 'D5', 1), (8, 'B4', .5), (8.5, 'D5', .5),
              (9, 'G5', .5), (9.5, 'F#5', .5), (10, 'E5', .5), (10.5, 'D5', .5), (11, 'C#5', .5), (11.5, 'B4', .5),
              (12, 'A4', .5), (12.5, 'B4', .25), (12.75, 'C#5', .25), (13, 'D5', .5), (13.5, 'E5', .5), (14, 'D5', 1.5)],
    'swing': [(0, 'Bb4', .5), (.5, 'D5', .5), (1, 'F5', 1), (2, 'Eb5', .5), (2.5, 'D5', .5), (3, 'C5', 1),
              (4, 'D5', .5), (4.5, 'C5', .5), (5, 'Bb4', .5), (5.5, 'G4', .5), (6, 'F4', 2), (8, 'Bb4', .5),
              (8.5, 'D5', .5), (9, 'F5', 1), (10, 'G5', .5), (10.5, 'F5', .5), (11, 'Eb5', 1), (12, 'D5', .5),
              (12.5, 'C5', .5), (13, 'D5', .5), (13.5, 'Eb5', .5), (14, 'F5', 2)],
    'shuffle': [(0, 'E5', .5), (.5, 'D5', .5), (1, 'B4', 1), (2, 'E5', .5), (2.5, 'D5', .5), (3, 'B4', 1),
                (4, 'G4', .5), (4.5, 'A4', .5), (5, 'B4', .5), (5.5, 'D5', .5), (6, 'C5', 1), (7, 'B4', 1)],
    'boogie': [(0, 'E4', .5), (.5, 'G4', .5), (1, 'A4', 1), (2, 'C5', .5), (2.5, 'A4', .5), (3, 'G4', 1),
               (4, 'F#4', .5), (4.5, 'A4', .5), (5, 'C5', .5), (5.5, 'D5', .5), (6, 'C5', 1), (7, 'A4', 1),
               (8, 'E5', .5), (8.5, 'D5', .5), (9, 'C5', .5), (9.5, 'A4', .5), (10, 'G4', 1), (11, 'A4', 1),
               (12, 'C5', .5), (12.5, 'A4', .5), (13, 'G4', .5), (13.5, 'E4', .5), (14, 'A4', 2)],
    'anthem': [(0, 'C4', 1), (1, 'F4', 1), (2, 'G4', 1), (3, 'A4', 1), (4, 'C5', 2), (6, 'Bb4', 1), (7, 'A4', 1),
               (8, 'G4', 1.5), (9.5, 'A4', .5), (10, 'F4', 1), (11, 'D4', 1), (12, 'C4', 3)],
    'galop': [(0, 'D5', .5), (.5, 'B4', .5), (1, 'G4', .5), (1.5, 'B4', .5), (2, 'D5', .5), (2.5, 'E5', .5),
              (3, 'D5', 1), (4, 'C5', .5), (4.5, 'A4', .5), (5, 'F#4', .5), (5.5, 'A4', .5), (6, 'C5', .5),
              (6.5, 'D5', .5), (7, 'C5', 1), (8, 'B4', .5), (8.5, 'G4', .5), (9, 'B4', .5), (9.5, 'D5', .5),
              (10, 'G5', 1), (11, 'F#5', .5), (11.5, 'E5', .5), (12, 'D5', .5), (12.5, 'C5', .5), (13, 'A4', .5),
              (13.5, 'F#4', .5), (14, 'G4', 2)],
}
CHORDS = {                                  # (chords, beats each)
    'march': (['Dm', 'Bb', 'Gm', 'A'], 4), 'rag': (['G', 'G', 'D7', 'G'], 2), 'waltz': (['F', 'C', 'Gm', 'C'], 3),
    'patter': (['G', 'D', 'C', 'G', 'G', 'D', 'D', 'G'], 2), 'polka': (['D', 'A7', 'A7', 'D', 'G', 'A7', 'D', 'D'], 2),
    'swing': (['Bb', 'F', 'Bb', 'F7'], 4), 'shuffle': (['Em', 'Em', 'Am', 'C'], 2), 'boogie': (['A7', 'D7', 'A7', 'E7'], 4),
    'anthem': (['F', 'Bb', 'Gm', 'C'], 2), 'galop': (['G', 'G', 'D7', 'D7', 'G', 'C', 'D7', 'G'], 2),
    'cp': (['D', 'G', 'Em', 'A'], 4),
}
PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
QUAL = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10)}


def _chord(name):
    r, i = PC[name[0]], 1
    if len(name) > 1 and name[1] in 'b#':
        r, i = r + (1 if name[1] == '#' else -1), 2
    return r % 12, QUAL[name[i:]]


def voicing(name, lo=53):
    """The chord's notes, one each, at or above `lo` (F3)."""
    r, iv = _chord(name)
    return sorted(lo + ((r + k) % 12 - lo) % 12 for k in iv)


def root(name, lo=36):
    return lo + (_chord(name)[0] - lo) % 12


def swing(b):
    """Swung eighths: an offbeat eighth lands two thirds of the way through its beat."""
    return b - 0.5 + 2 / 3 if abs(b % 1 - 0.5) < 1e-6 else b


def score(M, G):
    from pixelhome.audio import SR, note as n, slide, whoosh
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn = M.sampler('Brass/F Horn/stac/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    bone = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    buzz = M.sampler('Brass/OldTrombone/Buzz/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    tuba_s = M.sampler('Brass/Tuba/sus/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    oboe = M.sampler('Woodwinds/Oboe/Stacc/*.wav', tune=-12)
    flute = M.sampler('Woodwinds/Flute/susvib/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    xylo = M.sampler('Percussion/Xylo/*.wav', tune=-12)
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    harp = M.sampler('Strings/Harp/*.wav')
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    pizz = M.sampler('Strings/Cello Section/pizzT/*.wav', tune=-12)
    cbp = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)
    vln = M.sampler('Strings/Violin Section/susVib/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    organ = M.synth('Keys/House Organ')
    choir = M.synth('Pads/Synth Choir MW O-Ah')
    snare = M.hits('VSCO 1 Percussion/drums/snare/drum3_marching/snare3_[fmp]*.wav')
    sroll = M.hits('Percussion/Snare2-rollSN_v[35]*.wav')
    bd = M.hits('VSCO 1 Percussion/drums/bass/bdrum_f_*.wav')
    bd_ff = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    crash = M.hits('VSCO 1 Percussion/varMetal/Cymbals/clash/crash_hit_ff*.wav')
    choke = M.hits('Percussion/cymbal-crashshort*.wav')
    ccresc = M.hits('Percussion/susCymb1-cresc-Short*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    btree = M.hits('Percussion/BellTree_Stroke*.wav')
    sleigh = M.hits('Percussion/Sleighbells*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    maraca = M.hits('VSCO 1 Percussion/varWood/maraca*.wav')
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    anvil = M.hits('Percussion/Anvil_Hit1*.wav')
    fall = M.hits('Brass/OldTrombone/Fall/*.wav')
    for name, gain, rev in (('lead', 0.26, 0.2), ('band', 0.18, 0.18), ('bass', 0.3, 0.08), ('drums', 0.22, 0.12),
                            ('fx', 0.18, 0.2), ('sparkle', 0.12, 0.35), ('pad', 0.12, 0.4)):
        M.bus(name, gain=gain, reverb=rev)

    L = G.length
    d = G.pd[G.path]
    xs = G.pos[G.path, 0]
    x0, x1 = xs.min(), xs.max()
    mid = G.pd[G.seg['Porch Front']].mean()

    def pan_at(q):                          # path distance -> left/right across the facade, from the street
        return float(0.85 * (2 * (np.interp(q, d, xs) - x0) / (x1 - x0) - 1))

    slot = slots(G)
    P = [pan_at(q) for q in slot]
    corner = np.interp(CORNERS, np.arange(G.N), d)
    ev = _events(G)
    boxes, organs, hums = [], [], []

    def mono(sig, pans):
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def mel(inst, i, vel, shift=0, gain=1.0, upto=None, swung=False, bus='lead', fix=None, tune=None, t0=None,
            bpm=None, aug=1, pan=None):
        """Play section i's hook (or `tune`) from t0, up to beat `upto` (notes are cut there)."""
        style, sbpm, beats, _ = SECTIONS[i] if i is not None else ('cp', CP_BPM, CP_BEATS, 4)
        bt = 60 / (bpm or sbpm)
        t0 = START[i] if t0 is None else t0
        upto = beats if upto is None else upto
        p = 0.5 * P[i] if pan is None else pan
        for b, m, ln in (tune or TUNES[style]):
            b, ln = b * aug, ln * aug
            if b >= upto:
                continue
            ln = min(ln, upto - b)
            mm = n(m) + shift
            if fix:
                mm = fix(mm)
            bb = swing(b) if swung else b
            if inst is box:
                boxes.append((t0 + bb * bt, mm, vel, ln * bt * 0.9))
            else:
                M.add(bus, inst.play(mm, vel, dur=ln * bt * 0.9), t0 + bb * bt, gain, p)

    def chord_at(style, b):
        ch, per = CHORDS[style]
        return ch[int(b // per) % len(ch)]

    def pop_slot(i, vel=112):               # a character pops in: a hit and a stab where it stands
        M.add('drums', timp.play(vel), START[i], 0.5, P[i])
        M.add('fx', glock.play(n('D6') if i % 2 else n('A5'), 90), START[i], 0.5, P[i])

    # ---- intro: a snare roll and a brass pickup ----
    r = sroll.play(90, dur=INTRO - 0.3)
    M.add('drums', r * np.linspace(0.15, 1, r.shape[1]) ** 2, 0.3, 0.6)
    for k in range(3):
        M.add('lead', tpt.play(n('A4'), 100 + 8 * k, dur=0.2), INTRO - 0.75 + 0.25 * k, 0.8)

    # ---- 1: the march (D minor, 120) ----
    i, bt = 0, 0.5
    pop_slot(i)
    M.add('drums', crash.play(110), START[i], 0.6)
    mel(tpt, i, 108)
    mel(xylo, i, 90, 12, 0.35)
    for b in range(16):
        c, t = chord_at('march', b), sb(i, b)
        if b % 2 == 0:
            M.add('bass', tuba.play(root(c), 104 if b % 4 == 0 else 92), t)
            M.add('drums', bd.play(100), t, 0.7)
        else:
            for m in voicing(c):
                M.add('band', horn.play(m, 84, dur=0.2), t, 0.5, -0.2)
            M.add('drums', snare.play(95), t, 0.6, 0.15)
    M.add('fx', mute.play(n('D3'), 115, dur=0.15), sb(i, 15), 0.8, P[1])          # the dog barks...
    M.add('fx', bsn.play(n('D3'), 110, dur=0.15), sb(i, 15), 0.6, P[1])
    M.add('fx', slide(0, 0.35, 450, 950, 0.4, 0.35), sb(i, 15.3), 0.7, P[1])     # ...and he's off

    # ---- 2: the rag (G, 96): stride piano, the bone thrown and fetched ----
    i, bt = 1, 60 / 96
    pop_slot(i)
    mel(xylo, i, 105)
    mel(clar, i, 92, 0, 0.6)
    for b in range(8):
        c, t = chord_at('rag', b), sb(i, b)
        if b % 2 == 0:
            M.add('bass', piano.play(root(c), 100), t, 0.8)
            M.add('bass', tuba.play(root(c), 80), t, 0.4)
        else:
            for m in voicing(c, 55):
                M.add('band', piano.play(m, 82, dur=0.25), t, 0.7, 0.1)
        M.add('drums', tamb.play(70), t + bt / 2, 0.3, 0.3)
    for k in range(4):                      # four throws, two beats each, left and right of him
        t, side = sb(i, 2 * k), 1 if k % 2 == 0 else -1
        p = pan_at(slot[1] + side * 80)
        M.add('fx', slide(0, bt, 600, 1150, bt, 0.22), t, 0.6, p)
        M.add('fx', slide(0, bt, 1150, 600, bt, 0.22), t + bt, 0.6, p)
        for j in range(3):
            M.add('drums', wood.play(70), t + 0.25 * bt + 0.07 * j, 0.4, P[1])
    for j, m in enumerate(('F4', 'G4', 'A4', 'C5', 'D5', 'F5', 'G5', 'A5')):          # gliss into the waltz
        M.add('fx', harp.play(n(m), 90), sb(i, 7) + 0.07 * j, 0.6, P[2])
    M.add('drums', sleigh.play(90), sb(i, 7.5), 0.5, P[2])

    # ---- 3: the waltz (F, 150): music box and flute, bulbs pinging across the house ----
    i, bt = 2, 0.4
    pop_slot(i)
    mel(box, i, 92)
    mel(flute, i, 80, 0, 0.5)
    for b in range(12):
        c, t = chord_at('waltz', b), sb(i, b)
        if b % 3 == 0:
            M.add('bass', pizz.play(root(c) + 12, 100), t, 0.9)
        else:
            for m in voicing(c, 57):
                M.add('band', harp.play(m, 76), t, 0.5, 0.15)
    pent = ['F5', 'G5', 'A5', 'C6', 'D6', 'F6']
    for g in range(12):                     # each beat a group of bulbs pings on
        sel = ev['group'] == g
        if sel.any():
            M.add('sparkle', glock.play(n(pent[g % len(pent)]), 80), sb(i, g), 0.9, pan_at(ev['bc'][sel].mean()))
    for k in range(4):                      # tick-tock into the lab
        M.add('drums', wood.play(100 if k % 2 == 0 else 80, pitch=0 if k % 2 == 0 else 5), sb(i, 10 + 0.5 * k), 0.7,
              P[3])

    # ---- 4: the patter (G major, 144): ornaments shattering, the idea bulb ----
    i, bt = 3, 60 / 144
    pop_slot(i)
    major = lambda mm: mm + 1 if mm % 12 == 10 else mm          # Bb -> B
    mel(clar, i, 104, 0, 0.75, fix=major)
    mel(bsn, i, 100, -12, 0.4, fix=major)
    for b in range(16):
        c, t = chord_at('patter', b), sb(i, b)
        if b % 2 == 0:
            M.add('bass', cbp.play(root(c), 100), t, 0.4)
        else:
            for m in voicing(c, 55):
                M.add('band', pizz.play(m, 80), t, 0.3)
        M.add('drums', wood.play(55), t, 0.3, 0.3)
        M.add('drums', wood.play(45, pitch=5), t + bt / 2, 0.25, 0.3)
    for bar in range(8):
        t = sb(i, 2 * bar)
        if bar % 2 == 1:                    # the idea
            M.add('sparkle', glock.play(n('G5'), 100), t, 1.0, P[3])
            M.add('sparkle', tri.play(90), t, 0.6, P[3])
        else:                               # an ornament shatters
            M.add('fx', choke.play(70), t + 0.25 * 2 * bt, 0.25, P[3])
            for j, m in enumerate(('E6', 'B5', 'G6')):
                M.add('sparkle', glock.play(n(m), 70), t + 0.25 * 2 * bt + 0.04 * j, 0.6, P[3])
    M.add('sparkle', tri.play(110), START[4], 0.8, P[4])        # DING into the polka

    # ---- 5: the polka (D, 126): reedy lead, oom-pah ----
    i, bt = 4, 60 / 126
    pop_slot(i)
    mel(clar, i, 104, 0, 0.7)
    mel(oboe, i, 96, 0, 0.4)
    for b in range(16):
        c, t = chord_at('polka', b), sb(i, b)
        r0 = root(c)
        M.add('bass', tuba.play(r0 if b % 2 == 0 else r0 + 7, 100), t, 0.55)
        M.add('drums', bd.play(85), t, 0.5)
        organs.extend((t + bt / 2, m, 70, bt * 0.4) for m in voicing(c, 57))
        M.add('drums', tamb.play(80), t + bt / 2, 0.22, 0.25)
        M.add('drums', wood.play(50), t, 0.2, P[4])            # her steps
    for k in range(4):                      # a fill into the swing
        M.add('drums', snare.play(90 + 8 * k), sb(i, 15 + 0.25 * k), 0.6, 0.15)
    M.add('drums', timp.play(100), sb(i, 15.75), 0.5)

    # ---- 6: the swing (Bb, 132): the hammers ring the hook at the corners, the jack pops ----
    i, bt = 5, 60 / 132
    pop_slot(i)
    mel(xylo, i, 104, upto=15, swung=True)
    mel(glock, i, 84, 0, 0.45, upto=15, swung=True, bus='sparkle')
    mel(clar, i, 86, -12, 0.5, upto=15, swung=True)
    for b in range(15):
        c, t = chord_at('swing', b), sb(i, b)
        M.add('fx', anvil.play(80 if b % 2 else 95), t, 0.45, pan_at(corner[b % 5]))
        if b % 2 == 0:
            M.add('bass', tuba.play(root(c), 100), t, 0.9)
            M.add('drums', bd.play(85), t, 0.5)
        else:
            for m in voicing(c):
                M.add('band', horn.play(m, 82, dur=0.2), t, 0.45, -0.2)
            M.add('drums', snare.play(80), t, 0.45, 0.15)
        M.add('drums', snare.play(45), sb(i, swing(b + 0.5)), 0.25, 0.15)
    for bar in range(4):                    # the jack-in-the-box pops on each bar
        t = sb(i, 4 * bar)
        M.add('fx', slide(0, 0.18, 320, 980, 0.22, 0.3), t, 0.6, P[5])
    M.add('drums', choke.play(100), sb(i, 15), 0.5)             # stop! uh-oh
    M.add('fx', bsn.play(n('G3'), 105, dur=0.2), sb(i, 15), 0.9, P[6])
    M.add('fx', bsn.play(n('E3'), 100, dur=0.3), sb(i, 15.5), 0.9, P[6])

    # ---- 7: the shuffle (E minor, 120): the troublemakers tiptoe ----
    i, bt = 6, 0.5
    pop_slot(i, 90)
    mel(buzz, i, 100, -12, 0.9, swung=True)
    mel(flute, i, 84, 0, 0.45, swung=True)
    for b in range(8):
        c, t = chord_at('shuffle', b), sb(i, b)
        M.add('bass', cbp.play(root(c), 96), t, 0.9)
        for e in (0, 0.5):
            for m in voicing(c, 55):
                M.add('band', pizz.play(m, 70 if e else 82), sb(i, swing(b + e)), 0.45, P[6] * 0.5)
            M.add('drums', maraca.play(60), sb(i, swing(b + e)), 0.3, 0.3)
        if b % 2 == 1:
            M.add('drums', snare.play(50), t, 0.35)
    M.add('fx', fall.play(100, dur=0.6), sb(i, 7.3), 0.5, P[7])

    # ---- 8: the boogie (A, 120): piano left hand, muted brass ----
    i, bt = 7, 0.5
    pop_slot(i)
    M.add('drums', bd_ff.play(105), START[i], 0.6)
    mel(mute, i, 108, 0, 0.7, upto=16, swung=True)
    mel(tpt, i, 92, 0, 0.3, upto=16, swung=True)
    walk = (0, 4, 7, 9, 10, 9, 7, 4)
    for b in range(16):
        c, t = chord_at('boogie', b), sb(i, b)
        r0 = root(c, 33)
        for e in (0, 0.5):
            M.add('bass', piano.play(r0 + walk[int((b % 4) * 2 + e * 2)], 96 if e == 0 else 84), sb(i, swing(b + e)),
                  0.4)
        if b % 2 == 0:
            M.add('drums', bd.play(85), t, 0.5)
        else:
            M.add('drums', snare.play(80), t, 0.5, 0.15)
            for m in voicing(c, 57):
                M.add('band', mute.play(m, 76, dur=0.15), t, 0.35, P[7] * 0.5)
    r = troll.play(100, dur=2 * bt)                             # roll up into the anthem
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, sb(i, 14), 0.5)
    r = ccresc.play(100, dur=2 * bt + 0.05)
    M.add('drums', r * np.linspace(0.2, 1, r.shape[1]) ** 2, sb(i, 14) - 0.05, 0.3)

    # ---- 9: the anthem (F, 84): the sleigh streaks the house; snow starts ----
    i, bt = 8, 60 / 84
    M.add('drums', crash.play(118), START[i], 0.8)
    M.add('drums', timp.play(120), START[i], 0.8)
    mel(horn_s, i, 112, 0, 1.0, pan=0.0)
    mel(vln, i, 100, 12, 0.6, pan=0.0)
    for b in range(0, 8, 2):
        c = chord_at('anthem', b)
        hums.extend((sb(i, b), m + 12, 96, 2 * bt * 0.95) for m in voicing(c))
        M.add('bass', tuba_s.play(root(c), 96, dur=2 * bt * 0.95), sb(i, b), 0.5)
        if b % 4 == 0:
            M.add('drums', timp.play(100), sb(i, b), 0.5)
    for e in np.arange(0, 8, 0.5):
        M.add('drums', sleigh.play(70), sb(i, e), 0.25, 0.2)
    dur = 0.8 * (START[9] - START[8])
    w = whoosh(dur, 250, 2600, 0.5, seed=8)[0]
    tt = np.arange(len(w)) / SR
    lead = sleigh_lead(G, np.clip(tt / dur, 0, 1))
    pans = np.interp(tt, tt[::480], [pan_at(np.clip(q, 0, L)) for q in lead[::480]])
    M.add('fx', mono(w, pans), START[i], 0.9)
    M.add('fx', slide(0, 0.3, 1300, 520, 0.35, 0.3), sb(i, 7.5), 0.6)      # down into the galop

    # ---- 10: the galop (G, 150): presents popping all over ----
    i, bt = 9, 0.4
    pop_slot(i)
    M.add('drums', crash.play(115), START[i], 0.7)
    mel(tpt, i, 108, upto=15)
    mel(xylo, i, 96, 0, 0.5, upto=15)
    for b in range(16):
        c, t = chord_at('galop', b), sb(i, b)
        M.add('bass', tuba.play(root(c), 100), t, 0.9)
        M.add('drums', bd.play(85), t, 0.5)
        for m in voicing(c):
            M.add('band', horn.play(m, 80, dur=0.12), t + bt / 2, 0.4, -0.2)
        M.add('drums', snare.play(80), t + bt / 2, 0.45, 0.15)
        x = ev['gift_x'][b]                 # a present pops where render() pops it
        M.add('fx', slap.play(80), t, 0.3, pan_at(x))
        M.add('sparkle', glock.play(n(['G5', 'A5', 'B5', 'D6', 'E6'][ev['gift_c'][b]]), 80), t + 0.03, 0.6, pan_at(x))
    for k, m in enumerate(('A3', 'C#4', 'E4', 'G4')):            # the lift to D
        M.add('band', horn_s.play(n(m), 100 + 5 * k, dur=(16 - 14 - 0.5 * k) * bt), sb(i, 14 + 0.5 * k), 0.6)
    for k, m in enumerate(('A4', 'B4', 'C#5')):
        M.add('lead', tpt.play(n(m), 110, dur=0.12), sb(i, 15 + k / 3), 0.8)
    r = sroll.play(95, dur=2 * bt)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]) ** 2, sb(i, 14), 0.5)

    # ---- the counterpoint (D major, 120): the march against the anthem at half speed ----
    def tcp(b):
        return TCP + b * 60 / CP_BPM
    to_major = lambda mm: mm + 1 if mm % 12 in (5, 10, 0) else mm       # F->F#, Bb->B, C->C#
    M.add('drums', crash.play(124), TCP, 1.0)
    M.add('drums', bd_ff.play(120), TCP, 0.8)
    mel(tpt, None, 112, 0, 1.0, tune=TUNES['march'], t0=TCP, bpm=CP_BPM, fix=to_major, pan=-0.2)
    mel(xylo, None, 96, 12, 0.4, tune=TUNES['march'], t0=TCP, bpm=CP_BPM, fix=to_major, pan=-0.2)
    mel(horn_s, None, 112, -3, 1.1, tune=TUNES['anthem'], t0=TCP, bpm=CP_BPM, aug=2, upto=16, pan=0.25)
    mel(vln, None, 100, 9, 0.6, tune=TUNES['anthem'], t0=TCP, bpm=CP_BPM, aug=2, upto=16, pan=0.25)
    mel(bone, None, 96, -15, 0.6, tune=TUNES['anthem'], t0=TCP, bpm=CP_BPM, aug=2, upto=16, pan=0.1)
    for b in range(16):
        c, t = chord_at('cp', b), tcp(b)
        if b % 4 == 0:
            hums.extend((t, m + 12, 100, 2 * 0.95) for m in voicing(c))
            M.add('drums', timp.play(105), t, 0.5)
        if b % 2 == 0:
            M.add('bass', tuba.play(root(c), 108), t, 1.0)
            M.add('drums', bd.play(95), t, 0.6)
        else:
            for m in voicing(c):
                M.add('band', horn.play(m, 88, dur=0.2), t, 0.5, -0.2)
            M.add('drums', snare.play(100), t, 0.6, 0.15)
        for e in (0, 0.5):
            M.add('drums', sleigh.play(70), t + e * 0.5, 0.25, 0.2)
    for j in np.flatnonzero((ev['flake_t'] >= TCP) & (ev['flake_t'] < TBOW))[::7]:
        M.add('sparkle', glock.play(n(['D6', 'F#6', 'A5', 'E6'][j % 4]), 50), ev['flake_t'][j], 0.35,
              pan_at(d[ev['flake_px'][j]]))

    # ---- three bows, then the last chord and the button ----
    for k, (tb, ch) in enumerate(zip(BOWS, ('G', 'A', 'A7'))):
        for m in voicing(ch):
            M.add('band', horn.play(m, 112, dur=0.25), tb, 0.7)
            M.add('lead', tpt.play(m + 12, 108, dur=0.2), tb, 0.6)
        M.add('bass', tuba.play(root(ch), 115), tb, 1.0)
        M.add('drums', bd_ff.play(105 + 6 * k), tb, 0.6)
        M.add('drums', choke.play(90), tb, 0.35)
    r = troll.play(110, dur=TEND - BOWS[-1] - 0.25)
    M.add('drums', r * np.linspace(0.3, 1, r.shape[1]) ** 2, BOWS[-1] + 0.25, 0.6)
    hold = TBUTTON - TEND - 0.3
    for m in ('D3', 'F#3', 'A3', 'D4'):
        M.add('band', horn_s.play(n(m), 124, dur=hold), TEND, 0.85)
    for m in ('D4', 'F#4', 'A4'):
        M.add('lead', tpt_s.play(n(m), 120, dur=hold), TEND, 0.6)
    for m in ('D2', 'A2'):
        M.add('band', bone.play(n(m), 120, dur=hold), TEND, 0.7)
    M.add('lead', vln.play(n('D5'), 110, dur=hold), TEND, 0.6)
    M.add('bass', tuba_s.play(n('D2'), 124, dur=hold), TEND, 1.0)
    hums.extend((TEND, m + 12, 120, hold) for m in voicing('D'))
    M.add('drums', crash.play(127), TEND, 1.2)
    M.add('drums', bd_ff.play(127), TEND, 1.2)
    M.add('drums', timp.play(127), TEND, 1.1)
    M.add('sparkle', btree.play(110), TEND + 0.1, 1.0)
    r = troll.play(100, dur=hold)
    M.add('drums', r * np.linspace(0.6, 0.2, r.shape[1]), TEND + 0.2, 0.4)
    for j, m in enumerate(('D5', 'F#5', 'A5', 'D6')):         # glitter on the burst, out from the porch
        M.add('sparkle', glock.play(n(m), 90), TEND + 0.12 * j, 0.6, (-1) ** j * 0.25 * j)
    for m in ('D3', 'A3', 'D4'):                               # the button
        M.add('band', horn.play(n(m), 124, dur=0.25), TBUTTON, 0.9)
        M.add('lead', tpt.play(n(m) + 12, 120, dur=0.2), TBUTTON, 0.7)
    M.add('bass', tuba.play(n('D2'), 127), TBUTTON, 1.1)
    M.add('drums', bd_ff.play(127), TBUTTON, 1.2)
    M.add('drums', timp.play(127), TBUTTON, 1.0)
    M.add('drums', choke.play(115), TBUTTON, 0.7)
    M.add('sparkle', glock.play(n('D6'), 110), TBUTTON + 0.05, 0.7)

    M.add('lead', box.render(boxes, D), 0.0, 1.0, 0.5 * P[2])
    M.add('band', organ.render(organs, D), 0.0, 0.18, 0.5 * P[4])
    M.add('pad', choir.render(hums, D), 0.0, 1.0)
