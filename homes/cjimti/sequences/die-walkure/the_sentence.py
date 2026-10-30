"""The Sentence: the storm still holds the whole house, Wotan stands in deep blue at the left of the rock with
his spear beside him, and Brünnhilde steps out from the sisters' trembling knot to face him, silver with three
gold glints, while they draw back behind her.

The music is Wagner's own: Act III, bars 772 to 792, 860 to 880 and 936 to 947, as Solti's 1958 Vienna
Philharmonic recording takes them. Wotan pronounces her sentence ("Wunschmaid bist du nicht mehr; Walküre bist
du gewesen: nun sei fortan, was so du noch bist!"), she cries out ("Du verstößest mich?") and he casts her out
of Valhalla; the sisters storm him with their great ensemble of horror and pleading ("Halt ein, o Vater! ...
Wende die Schmach!"); he threatens any who stay with her ("sonst erharrt Jammer euch hier!"), they wail "Weh'!"
and flee. The notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py): his lines in
trombones and horns over cellos, basses and tuba, the sisters' outcry in violins with flutes and piccolo on top
over horns and violas, the flight on the full orchestra with trumpets. The stage is heard too: the storm's wind
holds, then drains away; each wave of his blue thuds, each glint going out is a cymbal scrape and a fading bell,
she sinks to her knees on a soft gong, his threat is a thunderclap with his spear ringing out, the sisters'
hooves gallop off to both ends of the house, and the thunder rolls away into the distance. The effects sit low under the sentence and back right off for the
sisters' outcry; they lead at his threat and their flight, then drain away with the storm.

Every heavy chord of his sentence is a slow wave of deep blue rolling out from him over the rock, and each line
of it takes one of her gold glints: a band of pale light falls over her and the glint goes out. As he casts
her out she sinks to her knees in a breath of sleeping violet. Then the sisters: each flares and throws a ring
of her colour toward Brünnhilde as she joins the outcry, leaning in, until all eight blaze together. He
threatens them, a thunderclap and his spear flashing out across the house; they wail and scatter in terror,
four galloping out the free end of Right and four away along the Left wing and Side. The two are left alone,
and the storm drains away: the clouds over the wings turn to evening rose and blue, the rock to dark slate
washed with dusk violet.

compose() tags every note of the excerpt, choreography() every position; render() and score() read both."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes
from pixelhome.ring import Orchestra, excerpt

CODE = 'WK24'
TITLE = 'The Sentence'
KIND = 'show'
DESCRIPTION = ('Brünnhilde steps out to face her father, and Wotan pronounces her sentence: she is no longer a '
               'Valkyrie. Her sisters cry out against it, until he threatens them with the same fate, and they '
               'flee in terror as the storm dies away into evening.')
VOICEOVER = ('She comes out from behind her sisters and stands in front of her father. '
             'Now he tells her what she has lost.')

EX = excerpt(__file__)                      # Act III, bars 772-792, 860-880 and 936-947, Solti 1958
SING = EX['singing']
D = EX['seconds']
line = lambda w: next(x for x in SING if x[3].startswith(w))
T_SEAM = EX['segments'][1]['start']         # the sisters' outcry
T_FORWARD = 0.5                             # she comes forward
WOTAN = [(x[0], x[1]) for x in SING if x[2] == 'Wotan' and x[0] < T_SEAM]
GLINTS = [line('Wunschmaid')[0], line('Walküre')[0], line('nun sei')[0]]     # each line of the sentence takes a glint
HERE = (line('Du verstößest')[0], line('Du verstößest')[1])                 # her cry
T_KNEEL = line('Nicht send')[0]             # cast out of Valhalla
T_THREAT = line('sonst erharrt')[0]         # he threatens them
WEH = [x[0] for x in SING if x[3].startswith('Weh')]
T_SCATTER = WEH[0]                          # they flee
T_EVE = D - 7.0                             # the storm turning to evening
CLOCK = 80.0 * 23

NAMES = ['Gerhilde', 'Ortlinde', 'Waltraute', 'Schwertleite', 'Helmwige', 'Siegrune', 'Grimgerde', 'Rossweisse']
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


def onsets(notes, win=0.06):
    """Chords: (time, weight) where weight is the summed velocity of the notes struck together."""
    out = []
    for t, d, m, v, h in notes:
        if out and t - out[-1][0] < win:
            out[-1][1] += v / 127
        else:
            out.append([t, v / 127])
    return np.array(out)


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, who). The left hand below C3 is 'low',
    above it 'brass'; the right hand 'wail' during the sisters' outcry (who = a sister), 'high' otherwise. Silent
    markers (velocity 0): 'word' on his heavy chords while he sings, 'glint' at each line of the sentence, 'cry'
    (who = a sister) as each joins the outcry, 'here' on her cry, 'thunder' at his threat, 'spear' on the accents
    after it, 'weh' at each wail."""
    N = []
    sisters = [(x[0], x[1], [k for k, n in enumerate(NAMES) if n in x[2]]) for x in SING
               if any(n in x[2] for n in NAMES)]
    j = 0
    for t, d, m, v, h in EX['notes']:
        if h == 1:
            N.append((t, d, m, v, 'low' if m < 48 else 'brass', None))
        elif T_SEAM <= t < T_THREAT:
            who = [k for a, b, ks in sisters if a <= t < b for k in ks] or list(range(8))
            N.append((t, d, m, v, 'wail', who[j % len(who)]))
            j += 1
        else:
            N.append((t, d, m, v, 'high', None))
    ons = onsets(EX['notes'])
    med = np.median(ons[:, 1])
    last = -9.0
    for t, w in ons:
        if any(a - 0.3 <= t < b for a, b in WOTAN) and w > med and t - last > 0.8:
            N.append((float(t), 3.0, 40, 0, 'word', None))
            last = t
        if HERE[0] <= t < HERE[1] and w > med:
            N.append((float(t), 0.5, 64, 0, 'here', None))
        if T_THREAT + 0.5 <= t < T_THREAT + 4.0 and w > med:
            N.append((float(t), 0.4, 40, 0, 'spear', None))
    seen = set()
    for a, b, ks in sorted(sisters):
        for k in ks:
            if (k, round(a, 1)) not in seen and a < T_THREAT:
                seen.add((k, round(a, 1)))
                N.append((a, 0.8, 76, 0, 'cry', k))
    for g in GLINTS:
        N.append((g, 1.5, 60, 0, 'glint', None))
    N.append((T_THREAT, 2.5, 26, 0, 'thunder', None))
    for w in WEH:
        N.append((w, 1.0, 76, 0, 'weh', None))
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
    CRIES = [[e[0] for e in compose() if e[4] == 'cry' and e[5] == k] for k in range(8)]
    for k in range(8):
        knot = K + RING[k] + tremble(k, tt)
        lo_ = smoothstep(T_FORWARD, T_FORWARD + 3.0, t)
        back = knot + (90 + 0.3 * RING[k]) * lo_                                 # drawing back behind her, loosening
        lean = -22 * sum(np.exp(-((t - w - 0.3) / 0.5) ** 2) for w in CRIES[k])  # leaning toward her as they cry out
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
    grief = [(e[0], e[1]) for e in N if e[4] == 'word']
    fall = sorted(e[0] for e in N if e[4] == 'glint')
    wail = [np.array([e[0] for e in N if e[4] == 'cry' and e[5] == k]) for k in range(8)]
    flick = [np.array(sorted({e[0] for e in N if e[4] == 'wail' and e[5] == k})) for k in range(8)]
    spear_t = np.array([e[0] for e in N if e[4] == 'spear'])
    weh = np.array([e[0] for e in N if e[4] == 'weh'])
    ons = onsets(EX['notes'])                                                   # the music's loudness, 0..1
    env = np.zeros(F)
    for t0, w in ons:
        f0 = int(t0 / DT)
        n = min(F - f0, nframes(1.5))
        env[f0:f0 + n] += w * np.exp(-np.arange(n) * DT / 0.4)
    env = np.clip(env / np.percentile(env, 95), 0, 1.2)

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
        calm = smoothstep(T_EVE - 2, D - 1.0, t)
        amt = (1 - calm) * (0.7 + 0.4 * env[f]) * (1 - 0.5 * porch)
        storm = thunderhead(rock_bed(d, tt, porch, stone), d, tt, -120.0, amt)
        sw = ((t + 80 - 0.2) / 2.4) % 1.0
        storm += light(WBLUE, 0.5 * (1 - calm) * (1 - sw) * np.exp(-((np.abs(d - pw) - 1600 * sw) / 160) ** 2) * (1 - 0.6 * porch))
        eve = smoothstep(T_EVE, D - 0.5, t)
        fr = storm * (1 - eve) + stage(d, tt, porch) * eve

        # the sentence: each long note of his grief a slow wave of deep blue rolling out over the rock
        for tg, dg in grief:
            if tg <= t < tg + 3.0:
                age = t - tg
                r = 40 + 900 * smoothstep(0, 2.6, age)
                fr += light(WBLUE, 0.85 * (1 - age / 3.0) * np.exp(-((np.abs(d - pw) - r) / 150) ** 2))
                fr += light(SPEAR, 0.5 * np.exp(-age / 0.2) * blob(pw, 60))
        # each line of the sentence: bands of pale light falling over her from both ends of the house
        for j, td in enumerate(fall):
            if td <= t < td + 1.6:
                age = t - td
                u = smoothstep(0, 1.2, age)
                for side in (-1, 1):
                    q = pb + side * 700 * (1 - u)
                    fr += light(FLASH * 0.5 + GOLD * 0.4, 0.8 * (1 - 0.5 * u) * blob(q, 90))
                fr += light(GOLD, 0.6 * np.exp(-((age - 1.2) / 0.15) ** 2) * blob(pb, 40))
        # cast out: soft violet breathing over the porch, centred on her as she kneels
        sl = smoothstep(T_KNEEL - 1, T_KNEEL + 2, t) * (1 - smoothstep(T_SEAM + 1, T_SEAM + 5, t))
        if sl > 0:
            sp = 0.5
            br = 0.6 + 0.4 * np.sin(2 * np.pi * (np.abs(d - pb) / 300 - 0.12 * tt))
            fr += light(SLEEP, sl * (0.5 + 0.25 * sp) * br * (0.35 + 0.65 * porch) * (0.5 + 0.5 * blob(pb, 400)))

        # Wotan: from the god of the storm, spear at his side, to the father alone with her at evening
        th = smoothstep(T_THREAT - 0.1, T_THREAT + 0.1, t) * np.exp(-max(t - T_THREAT, 0) / 1.2)
        sp_ = last(spear_t, t, 0.3, 1.0)
        soft = smoothstep(T_EVE, D - 1.0, t)
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
        hp = last(here, t, 0.3, 1.5)
        kneel = smoothstep(T_KNEEL, T_KNEEL + 6.0, t)
        lvl = 0.45 + 0.35 * fwd - 0.3 * kneel + 0.35 * hp
        if HERE[0] <= t < HERE[1] + 1.0:                                        # her cry: reaching toward him
            fr += light(SILVER, 0.5 * hp * blob(pb + (pw - pb) * min(1.0, 3 * (1 - hp)), 14))
        hidden = 1 - fwd
        core_w = 9 + 11 * fwd
        halo = 0.135 / 0.45 * (1 - fwd) + 0.22 / 0.5 * fwd
        halo_w = 30 + 50 * fwd
        fr += light(SILVER, lvl * blob(pb, core_w) + halo * lvl * blob(pb, halo_w))
        gone = int(np.searchsorted(np.array(fall) + 1.2, t, side='right'))     # a glint goes out with every line
        kept = max(0, 3 - gone)
        gl = 0.3 * hidden + 0.65 * fwd
        for kg in range(kept):
            q = pb + 18 * np.sin(2 * np.pi * (0.8 * tt + kg / 2))
            fr += light(GOLD, gl * blob(q, 5))
        faint = smoothstep(fall[-1] + 1, T_KNEEL + 4, t)
        if faint > 0:                                                            # what is left: a faint scatter of gold
            g = (rng.random(G.N) < 0.05) * blob(pb, 40)
            fr += light(GOLD, 0.25 * faint * g)

        # the sisters: drawing back behind her, wailing, leaning toward her; then gone in terror
        for k in range(8):
            p = C['pos'][k][f]
            vis = smoothstep(-150, 0, p) * smoothstep(L + 150, L, p)
            if vis <= 0:
                continue
            wl = last(wail[k], t, 0.35, 1.5)
            fk = last(flick[k], t, 0.15, 0.6)
            wh = last(weh, t, 0.4, 1.5)
            loose = smoothstep(T_FORWARD, T_FORWARD + 3.0, t)
            outcry = smoothstep(T_SEAM, T_SEAM + 20, t) * (1 - smoothstep(T_THREAT, T_THREAT + 1, t))
            b = vis * (0.8 + 0.35 * wl + 0.3 * fk + 0.3 * th + 0.4 * wh + 0.35 * outcry * env[f])
            fr += light(COLS[k], b * blob(p, 8 + 3 * loose + 6 * outcry) + (0.15 + 0.05 * loose + 0.25 * outcry) * b
                        * blob(p, 30 + 10 * loose + 40 * outcry))
            if t > T_SCATTER and abs(p - C['pos'][k][max(f - 4, 0)]) > 8:
                trail = np.zeros(G.N)
                for j, lag in enumerate(range(2, 26, 2)):
                    trail = np.maximum(trail, blob(C['pos'][k][max(f - lag, 0)], 20) * (1 - j / 12.5))
                fr += light(COLS[k], 0.7 * vis * trail)
            for tc in wail[k]:
                if tc <= t < tc + 0.8:
                    age = t - tc
                    r = 15 + 400 * age ** 0.7
                    fr += light(COLS[k], 0.7 * (1 - age / 0.8) * np.exp(-((np.abs(d - p) - r) / 40) ** 2))
            if outcry > 0:                                                      # their colours flooding the clouds
                fr += light(COLS[k], 0.42 * outcry * vis * (0.3 + 0.7 * env[f]) * (1 - porch)
                            * (0.5 + 0.5 * np.cos(2 * np.pi * (d / 260 - 0.3 * tt + k / 8))) ** 3)
        if t < T_FORWARD + 3.0:                                                 # the knot's glow, opening
            fr += light(SILVER * 0.4 + WBLUE * 0.2, 0.2 * (1 - smoothstep(T_FORWARD, T_FORWARD + 3.0, t)) * blob(K, 90))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction: his lines in trombones and horns over the low strings
    and tuba, the sisters' outcry in violins, flutes and piccolo over horns and violas, the flight on the full
    orchestra; thunder at his threat."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    C = choreography(G)

    def pan_of(k, t):
        return pan_at(float(np.clip(np.interp(t, C['t'], C['pos'][k]), 0, G.length)))

    o = Orchestra(M, level=LEVEL)
    wp = pan_at(at(G, 'Porch Front', 0.3))
    bp = pan_at(at(G, 'Porch Front', 0.55))
    for t, d, m, v, part, who in compose():
        if part == 'low':
            o.play('cellos', m, t, d, v, -0.2, 0.75)
            o.play('basses', m - 12 if m >= 40 else m, t, d, v - 6, 0.2, 0.55)
            if d > 0.5:
                o.play('tuba', m, t, d, v - 10, wp, 0.5)
        elif part == 'brass':
            if t >= T_SEAM and t < T_THREAT and m >= 60:
                o.play('horns', m, t, d, v - 4, 0.0, 0.7)
                o.play('violas', m, t, d, v - 8, -0.2, 0.4)
            elif d >= 0.3:
                o.play('trombones', m, t, d, v, wp, 0.75)
                o.play('horns', m, t, d, v - 8, -wp, 0.55)
            else:
                o.play('violas' if m >= 60 else 'cellos', m, t, d, v - 4, wp, 0.5)
        elif part == 'wail':
            pa = pan_of(who, t)
            o.play('violins', m, t, d, v - 2, pa, 0.6)
            if m >= 76:
                o.play('piccolo' if m >= 84 else 'flutes', m, t, d, v - 12, pa, 0.4)
        elif part == 'high':
            o.play('violins', m, t, d, v - 4, bp, 0.6)
            if d >= 0.4:
                o.play('violas', m - 12, t, d, v - 14, -0.2, 0.3)
            if t >= T_THREAT:
                if d >= 0.3:
                    o.play('trumpets', m, t, d, v - 10, 0.1, 0.4)
                if m >= 79:
                    o.play('piccolo', m, t, 0.1, v - 12, -0.3, 0.35)
        elif part == 'thunder':
            o.hit('crash', t, 124, gain=0.8, pan=wp, fx=True)
            o.hit('bass drum', t, 124, gain=0.8, pan=wp, fx=True)
            o.hit('timpani', t, 124, pitch=-6, gain=0.9, pan=wp, fx=True)
        elif part == 'weh':
            o.hit('timpani', t, 112, pitch=-4, gain=0.6)
        elif part == 'glint':
            o.hit('timpani roll', t, 84, gain=0.35, pan=bp)
            o.hit('scrape', t + 0.9, 90, gain=0.35, pan=bp, fx=True)                 # a glint goes out
            o.play('glock', 86, t + 1.1, 0.4, 80, bp, 0.3)
        elif part == 'word':                                               # each wave of blue: a heavy thud
            o.hit('bass drum', t, 92, gain=0.45, pan=wp, fx=True)
        elif part == 'cry':                                                # each sister's ring thrown toward her
            o.hit('crash', t, 72, gain=0.18, pan=pan_of(who, t), fx=True)
        elif part == 'spear':                                              # his spear flashing out
            o.clash(t, wp, 112, gain=0.55)
    # the stage: the storm's wind holding, then draining away; his threat a thunderclap; the sisters galloping off
    o.wind(0.0, T_EVE + 4.0, level=lambda tt: 0.75 * (1 - smoothstep(T_SCATTER + 1.0, T_EVE + 3.0, tt)), pan=0.2)
    o.thunder(T_THREAT, near=1.0, pan=wp, gain=1.2)
    o.hit('gong', T_KNEEL, 80, gain=0.35, pan=bp, fx=True)                          # she sinks to her knees
    for side in (1, -1):
        o.gallop(T_SCATTER, T_SCATTER + 3.0, beat=0.33, v=104, gain=1.0,
                 pan=lambda t, s=side: s * (0.3 + 0.7 * smoothstep(T_SCATTER, T_SCATTER + 3.0, t)))
        o.gallop(T_SCATTER + 3.0, T_SCATTER + 6.0, beat=0.33, v=84, gain=0.45, pan=side * 1.0)
    o.thunder(T_SCATTER + 4.0, near=0.2, pan=0.7, gain=0.8)                # the storm rolling away
    o.thunder(T_EVE - 1.5, near=0.0, pan=-0.6, gain=0.6)
    # the fader: under his sentence and the sisters' outcry the music leads; his threat and their flight are the
    # effects', then they drain away with the storm
    o.effects([(0.0, -9), (T_SEAM - 1.0, -9), (T_SEAM, -14), (T_THREAT - 0.6, -14), (T_THREAT - 0.2, 2),
               (T_SCATTER + 4.0, 0), (T_EVE, -8), (D, -10)])


LEVEL = 1.8
