"""The Potion: the hall of the Gibichungs, the four of them in it as Siegfried's arrival left them.

The music is Wagner's own, Act I as Solti's 1958 recording takes it: Gutrune's welcome as she brings the drinking
horn (bars 473-476); Siegfried's toast, "Vergäss' ich alles, was du mir gabst ... Brünnhilde, bring' ich dir!"
(484-495); and the love potion taking him, "Die so mit dem Blitz den Blick du mir seng'st", her lowered eyes,
"Ha, schönstes Weib!" to "zünden mein Blut!" (506-522). The notes come from the Wagner Ring Dataset's piano
reduction (pixelhome/ring.py): Gutrune's music on oboes and clarinets, the potion on clarinets and bassoons, the
passion on the full orchestra. His toast is not in the reduction; it is played as he sings it, on horns and
cellos, from the printed vocal score (Schott, Pl. 23263, pp. 68-69; archive.org gtterdmmerung00wagn_0). A gong
scrape as he drinks, a cymbal swell as the love potion takes him.

Gutrune comes down from beside the throne with the drinking horn, rose waves out from her on each chord. He lifts
it to Brünnhilde and the house fills with a field of silver points, every note he sings a silver wave out from
him. Then he drinks, and a tide of sickly violet pours out of him along the roofline while the silver points go
out one after another. The love potion takes him: every note of its climbing lines slams a whole run, emerald and
rose by turns, rings running out from the two of them; as she lowers her eyes the whole house surges rose and
emerald together, and his passion drives the slams on to the end.

compose() tags every note; stage(), hall(), figure(), wave() and blow() are the hall, shared word for word by
Act I's hall scenes (GD07-GD12) on a clock that runs on from scene to scene."""
import numpy as np
from pixelhome.audio import note
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker, smooth_noise
from pixelhome.ring import Orchestra, accents, excerpt, tidy

CODE = 'GD10'
TITLE = 'The Potion'
KIND = 'show'
DESCRIPTION = ('Gutrune offers Siegfried a drink. He drinks to Brunnhilde, the potion wipes her from his memory in '
               'a tide of violet, and he burns for Gutrune instead.')
VOICEOVER = ('Siegfried raises the cup to Brunnhilde, and drinks. '
             'In one swallow he forgets her completely.')

K = 3                                       # this scene's place on Act I's shared clock: T = t + 80 K
EX = excerpt(__file__)                      # Act I, bars 473-476, 484.5-495 and 506-522, Solti 1958
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
T_WALK = (0.5, BAR[476])                    # "Willkommen, Gast": Gutrune brings him the horn
T_TOAST = BAR[485]                          # he drinks to Brünnhilde: silver
T_DRINK = BAR[494]                          # he drinks: the potion
T_LOVE = BAR[506]                           # the love potion takes him
T_GUT2 = BAR[511]                           # she lowers her eyes: her music in full, rose and emerald together
T_PASSION = BAR[513]                        # "Ha, schönstes Weib!"
T_SETTLE = BAR[520]
# His toast, from the vocal score (Schott, Pl. 23263, pp. 68-69; archive.org gtterdmmerung00wagn_0):
# (bar, beat, beats, note as written for tenor, sounding an octave lower). 3/4, E flat major.
TOAST = [(484, 2.5, 0.5, 'Bb4'),
         (485, 0, 0.75, 'Eb5'), (485, 0.75, 0.25, 'G4'), (485, 1, 1, 'D5'), (485, 2, 1, 'C5'),
         (486, 0, 1 / 3, 'Bb4'), (486, 1 / 3, 1 / 3, 'Ab4'), (486, 2 / 3, 1 / 3, 'G4'), (486, 1, 1, 'F4'),
         (486, 2.75, 0.25, 'Bb4'),
         (487, 0, 0.75, 'Eb5'), (487, 0.75, 0.25, 'G4'), (487, 1, 0.75, 'C5'), (487, 1.75, 0.25, 'Eb4'),
         (487, 2, 1 / 3, 'G4'), (487, 2 + 1 / 3, 1 / 3, 'Ab4'), (487, 2 + 2 / 3, 1 / 3, 'Bb4'),
         (488, 0, 2, 'C5'),
         (489, 2.5, 0.5, 'F4'), (490, 0, 2, 'Ab4'), (490, 2, 1, 'C5'),
         (491, 0, 0.75, 'C5'), (491, 0.75, 0.25, 'Db5'), (491, 1, 4 / 3, 'Eb5'), (491, 7 / 3, 1 / 3, 'Db5'),
         (491, 8 / 3, 1 / 3, 'C5'),
         (492, 0, 1, 'Eb5'), (492, 1, 1, 'Db5'),
         (493, 0, 1, 'F5'), (493, 1, 0.5, 'Db5'), (493, 1.5, 0.5, 'Bb4'), (493, 2, 0.75, 'G4'), (493, 2.75, 0.25, 'F4'),
         (494, 0, 2, 'Db5')]

AMBER = hexc('#ff8a20')
PURPLE = hexc('#6a10c0')
TORCH = hexc('#ffb040')
HEAT = hexc('#fff0a0')
REED = hexc('#2a6a20')
RIVER = hexc('#0c1c8c')
TEAL = hexc('#0a7c8a')
FOAM = hexc('#14c080')
HAGEN = hexc('#7a00ff')
SPEAR = hexc('#c8d8ff')
GUNTHER = hexc('#ffb020')
GUTRUNE = hexc('#ff4090')
SIEGFRIED = hexc('#00ff40')
HEAD = hexc('#e8ffe8')
POTION = hexc('#a050ff')
BLOOD = hexc('#c00010')
GOLD = hexc('#ffaa00')
WHITE = hexc('#ffffff')
SILVER = hexc('#f4f8ff')

START = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)    # where GD09 left the hall
END = dict(hall=0.55, drapes=0.5, torches=0.85, bank=0.4, river=0.6, gloom=0.0)      # where GD11 picks it up
GUNTHER_AT = ('Porch Front', 0.62)
GUTRUNE_FROM = ('Porch Front', 0.38)
GUTRUNE_AT = ('Porch Front', 0.75)          # at Siegfried's side
HAGEN_AT = ('Porch Left', 0.35)
SIEGFRIED_AT = ('Porch Front', 0.85)
FIGS_END = dict(gunther=(*GUNTHER_AT, 0.8), gutrune=(*GUTRUNE_AT, 0.8), hagen=(*HAGEN_AT, 0.75),
                siegfried=(*SIEGFRIED_AT, 0.85))


def at(G, seg, u):
    """Path distance u of the way along a segment."""
    s = G.pd[G.seg[seg]]
    return float(s.min() + u * (s.max() - s.min()))


RUNS = ['Left', 'Right', 'Side', 'Right', 'Left']
TORCHES = [('Left', 0.2), ('Left', 0.55), ('Left', 0.88), ('Porch Left', 0.2), ('Porch Left', 0.7),
           ('Porch Front', 0.15), ('Porch Front', 0.5), ('Porch Front', 0.85), ('Porch Right', 0.3),
           ('Porch Right', 0.8), ('Side', 0.6)]


def stage(G):
    """The hall of the Gibichungs as profiles over the house: the hall on the porch, its far walls on Left and the
    Side, torches along them, the riverbank on Right with the Rhine running past its free end."""
    d = G.pd
    rng = np.random.default_rng(1848)       # the same torches, drapes and river in every scene, so the cuts match
    seg = G.seg_of
    porch = np.isin(seg, ['Porch Left', 'Porch Front', 'Porch Right'])
    walls = np.isin(seg, ['Left', 'Side'])
    mid = at(G, 'Porch Front', 0.5)
    river = smoothstep(at(G, 'Right', 0.55), at(G, 'Right', 1.0), d)
    tp = np.array([at(G, s, u) for s, u in TORCHES])
    return dict(
        d=d, mid=mid, porch=porch, walls=walls, torch_at=tp,
        hall=porch * (0.6 + 0.4 * np.exp(-((d - mid) / 200) ** 2)) + walls * (0.45 + 0.2 * smooth_noise(rng, d, 50.0)),
        drape=(porch | walls) * (0.5 + 0.5 * np.sin(2 * np.pi * d / 140)) ** 2,
        torch=np.exp(-((d[None, :] - tp[:, None]) / 9) ** 2).sum(0),
        glow=np.exp(-((d[None, :] - tp[:, None]) / 45) ** 2).sum(0),
        bank=(seg == 'Right') * (1 - river) * (0.7 + 0.3 * smooth_noise(rng, d, 30.0)),
        river=river,
        fl=Flicker(rng, G.N, 3.0, 9.0),
        sway=Flicker(rng, G.N, 0.2, 0.7),
    )


def hall(S, T, lv):
    """The hall at shared time T with levels lv (hall, drapes, torches, bank, river, gloom)."""
    d, fl = S['d'], S['fl'](T)
    fr = light(AMBER, lv['hall'] * S['hall'] * (0.85 + 0.15 * fl))
    fr += light(PURPLE, lv['drapes'] * S['drape'] * (0.85 + 0.15 * S['sway'](T)))
    fr += light(TORCH, lv['torches'] * np.clip(S['torch'], 0, 1) * (0.75 + 0.25 * fl))
    fr += light(AMBER, 0.6 * lv['torches'] * np.clip(S['glow'], 0, 1) * (0.8 + 0.2 * fl))
    fr += light(REED, lv['bank'] * S['bank'])
    u = 0.5 + 0.5 * np.sin(2 * np.pi * (d / 90 - 0.55 * T)) * np.sin(2 * np.pi * (d / 230 - 0.2 * T) + 1.0)
    fr += light(RIVER + (TEAL - RIVER) * u[:, None], lv['river'] * S['river'])
    fr += light(FOAM, lv['river'] * S['river'] * np.clip(u - 0.75, 0, None) * 3)
    return fr * (1 - lv['gloom'])


def figure(fr, S, p, col, lvl, w=16.0):
    """A person at path distance p: a body that stands in front of the hall, and a halo."""
    body = np.exp(-((S['d'] - p) / w) ** 2)
    fr = fr * (1 - 0.85 * min(1.0, lvl / 0.2) * body)[:, None]
    return fr + light(col, lvl * body) + light(col, 0.35 * lvl * np.exp(-((S['d'] - p) / (3 * w)) ** 2))


def wave(S, p, a, speed=1200.0, width=90.0, life=0.9):
    """A ring running out both ways from p, a seconds after it starts -> perceptual."""
    return np.exp(-a / life) * np.exp(-((np.abs(S['d'] - p) - speed * a) / width) ** 2) * (a >= 0)


def blow(fr, S, p, a, s=1.0):
    """Hagen's blow, a seconds after it lands at p: the house knocked dark and a black-violet shock out from him."""
    if not 0 <= a < 2.5:
        return fr
    fr = fr * (1 - 0.9 * s * np.exp(-a / 0.9))
    fr = fr + light(HAGEN, 0.5 * s * np.exp(-a / 0.35))
    fr = fr + light(HAGEN, s * wave(S, p, a, 1100.0, 230.0, 1.2))
    fr = fr + light(SPEAR, 0.9 * s * np.exp(-a / 0.12) * np.exp(-((S['d'] - p + 18) / 8) ** 2))
    return fr


def toast():
    """His toast in seconds: (time, seconds, midi as sung)."""
    seg = next(g for g in EX['segments'] if g['measures'][0] == 484.5)
    bars = [(484.5, seg['start'])] + sorted((m, t) for m, t in EX['bars'] if 485 <= m <= 495)
    when = lambda pos: float(np.interp(pos, [b[0] for b in bars], [b[1] for b in bars]))
    out = []
    for b, x, n, name in TOAST:
        a = max(b + x / 3, 484.5)
        t0 = when(a)
        out.append((t0, when(b + (x + n) / 3) - t0, note(name) - 12))
    return out


def compose():
    """Every note of the excerpt, tagged: (time, seconds, midi, velocity, part, hand, trem): Gutrune's welcome
    'gutrune', the toast's accompaniment 'toast', the potion 'potion', the love potion 'love', her lowered eyes
    'gutrune2', his passion 'passion'; and his sung toast, 'voice'."""
    N = []
    for t, d, m, v, h, trem in tidy(EX['notes']):
        part = ('gutrune' if t < T_TOAST else 'toast' if t < T_DRINK else 'potion' if t < T_LOVE else 'love'
                if t < T_GUT2 else 'gutrune2' if t < T_PASSION else 'passion')
        N.append((t, d, m, v, part, h, trem))
    for t, d, m in toast():
        N.append((t, d, m, 92, 'voice', 0, False))
    return sorted(N, key=lambda e: e[0])


def render(G, seed=10):
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    S = stage(G)
    d = S['d']
    L = d.max()
    N = compose()
    gut = [e for e in N if e[4] in ('gutrune', 'gutrune2') and e[5] == 0 and e[1] >= 0.4]
    sung = [e for e in N if e[4] == 'voice']
    pot = [T_DRINK + 0.2, T_DRINK + 1.6, T_DRINK + 3.0]
    love_t = accents([e for e in N if e[4] in ('love', 'passion') and e[5] == 0], n=1, space=0.3)
    love_m = [max(e[2] for e in N if abs(e[0] - t0) < 0.02 and e[5] == 0) for t0 in love_t]
    lo, hi = min(love_m), max(love_m)
    p_gun, p_hag, p_sf = at(G, *GUNTHER_AT), at(G, *HAGEN_AT), at(G, *SIEGFRIED_AT)
    g0, g1 = at(G, *GUTRUNE_FROM), at(G, *GUTRUNE_AT)
    runs = ['Porch Front', 'Right', 'Left', 'Porch Right', 'Side', 'Porch Left']
    rng = np.random.default_rng(seed)
    pts = rng.uniform(0, L, 70)                     # the silver of her memory, point by point
    out_at = T_DRINK + 0.4 + np.sort(rng.uniform(0, 5.5, 70))[rng.permutation(70)]
    tw = rng.uniform(0, 2 * np.pi, 70)

    for f in range(F):
        t = f * DT
        T = t + 80 * K
        fr = hall(S, T, START)
        p_gut = g0 + (g1 - g0) * smoothstep(*T_WALK, t)

        # Gutrune's motif: rose waves out from her over the whole house
        for t0, dur, m, v, part, h, _ in gut:
            a = t - t0
            if 0 <= a < 1.5:
                fr += light(GUTRUNE, (0.7 + 0.15 * (part == 'gutrune2')) * wave(S, p_gut, a, 1300.0, 140.0, 0.7))
                fr += light(GUTRUNE, 0.35 * np.exp(-a / 0.3) * S['porch'])

        # the toast to Brunnhilde: silver floods the house, a field of silver points over every run
        mem = smoothstep(T_TOAST, T_TOAST + 1.5, t)
        for t0, dur, m, v, part, h, _ in sung:          # every note he sings to her: a silver wave from him
            a = t - t0
            if 0 <= a < 1.6:
                fr += light(SILVER, (0.6 + 0.4 * (m >= note('Eb4'))) * wave(S, p_sf, a, 1300.0, 180.0, 0.9))
        if mem > 0:
            alive = (t < out_at).astype(float)
            dying = np.exp(-np.clip(t - out_at, 0, None) / 0.15) * (t >= out_at)
            g = mem * (alive * (0.65 + 0.35 * np.sin(7.0 * t + tw)) + 1.6 * dying)
            pts_l = (g[:, None] * np.exp(-((d[None, :] - pts[:, None]) / 7) ** 2)).sum(0)
            fr += light(SILVER, np.clip(pts_l, 0, 1.1))
            fr += light(SILVER, 0.25 * mem * (1 - smoothstep(T_DRINK, T_DRINK + 8, t)))

        # the potion: each chord a tide of sickly violet pouring out of him along the roofline
        for i, t0 in enumerate(pot):
            a = t - t0
            if 0 <= a < 6.0:
                reach = min(1.0, a / 2.2) * L
                tide = smoothstep(reach + 120, reach - 120, np.abs(d - p_sf))
                g = (0.6 + 0.12 * i) * np.exp(-max(a - 2.5, 0) / 1.4)
                fr = fr * (1 - 0.5 * g * tide)[:, None]
                fr += light(POTION, g * tide * (0.7 + 0.3 * np.sin(2 * np.pi * (d / 120 - 1.2 * t))))
                fr += light(WHITE, 0.6 * np.exp(-a / 0.1) * np.exp(-((d - p_sf) / 25) ** 2))
        if T_DRINK <= t < T_LOVE:
            fr += light(POTION, 0.35 * smoothstep(T_DRINK, T_DRINK + 3, t) * (1 - smoothstep(T_LOVE - 2, T_LOVE, t)))

        # the love potion: every note slams a whole run, emerald and rose by turns, rings out from both of them
        for i, (m, t0) in enumerate(zip(love_m, love_t)):
            a = t - t0
            dur = 0.4
            if 0 <= a < 2.0:
                u = (m - lo) / (hi - lo)
                run = G.seg_of == runs[i % len(runs)]
                col = SIEGFRIED if i % 2 == 0 else GUTRUNE
                g = (0.7 + 0.3 * u) * np.exp(-a / (0.35 + dur))
                fr = fr * (1 - 0.6 * np.exp(-a / 0.4) * run)[:, None]
                fr += light(col, g * run)
                fr += light(col, 0.75 * wave(S, p_sf if i % 2 == 0 else p_gut, a, 1500.0, 110.0, 0.6))

        # her motif in full: the whole house surges rose and emerald together, the two colours chasing
        if T_GUT2 <= t < T_PASSION + 1.0:
            a = t - T_GUT2
            g = smoothstep(0, 0.5, a) * (1 - smoothstep(T_PASSION - T_GUT2 - 1.0, T_PASSION - T_GUT2 + 1.0, a))
            ph = np.sin(2 * np.pi * (d / 300 - 0.9 * a))
            fr += light(GUTRUNE, 0.9 * g * np.clip(ph, 0, 1))
            fr += light(SIEGFRIED, 0.9 * g * np.clip(-ph, 0, 1))
            fr += light(WHITE, 0.7 * np.exp(-a / 0.12))

        # settled at her side: the two of them keep throwing rings of emerald and rose round the house
        if t >= T_SETTLE:
            g = smoothstep(T_SETTLE, T_SETTLE + 1.5, t) * (1 - smoothstep(D - 3.5, D - 0.5, t))
            for j in range(3):
                a = (t - T_SETTLE - 1.3 * j) % 3.9
                fr += light(SIEGFRIED if j % 2 == 0 else GUTRUNE, 0.6 * g * wave(S, (p_sf + p_gut) / 2, a, 900.0, 120.0, 1.0))

        # the four of them; Siegfried burns brighter once the potion has him
        burn = smoothstep(T_LOVE, T_LOVE + 2, t) * (1 - smoothstep(T_SETTLE, D - 2, t))
        fr = figure(fr, S, p_gun, GUNTHER, 0.8)
        fr = figure(fr, S, p_gut, GUTRUNE, 0.8 + 0.15 * burn)
        fr = fr * (1 - 0.45 * np.exp(-((d - p_hag) / 70) ** 2))[:, None]
        fr = figure(fr, S, p_hag, HAGEN, 0.75)
        fr += light(SPEAR, 0.45 * np.exp(-((d - p_hag + 18) / 6) ** 2))
        fr = figure(fr, S, p_sf, SIEGFRIED, 0.85 + 0.15 * burn)
        fr += light(HEAD, 0.8 * (0.85 + 0.15 * burn) * np.exp(-((d - p_sf) / 6) ** 2))
        if T_DRINK - 0.5 <= t < T_LOVE:          # the memory leaving him: a violet veil over his head
            fr += light(POTION, 0.5 * np.exp(-((d - p_sf) / 30) ** 2) * smoothstep(T_DRINK - 0.5, T_DRINK, t))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Wagner's notes, orchestrated from the piano reduction; his toast sung on horns and cellos."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                         # path distance -> left/right across the facade, from the street
        x = np.interp(dd, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.4)
    sf = pan_at(at(G, *SIEGFRIED_AT))
    gut = lambda t: pan_at(at(G, *GUTRUNE_FROM) + (at(G, *GUTRUNE_AT) - at(G, *GUTRUNE_FROM)) * smoothstep(*T_WALK, t))

    def role(t, d, m, v, h):
        if t < T_TOAST or T_GUT2 <= t < T_PASSION:          # Gutrune's music: oboes and clarinets, violas under
            return ([('oboes', 0, 8, 0.6), ('violins', 0, -8, 0.35)] if h == 0 else
                    [('clarinets', 0, 4, 0.55), ('violas', 0, -6, 0.4)])
        if t < T_DRINK:                                     # under the toast: soft strings, clarinets
            return [('violins' if m >= 55 else 'violas', 0, -6, 0.4)] if h == 0 else [('cellos', 0, -4, 0.45)]
        if t < T_LOVE:                                      # the potion: clarinets and bassoons, low and slow
            return [('clarinets', 0, 6, 0.6)] if h == 0 else [('bassoons', 0, 4, 0.6)]
        return None

    o.tutti([[t, d, m, v, h, tr] for t, d, m, v, part, h, tr in compose() if part != 'voice'],
            size=lambda t: 1.0 if t >= T_PASSION else 0.7, role=role,
            pan=lambda t, m: gut(t) if t < T_TOAST or T_GUT2 <= t < T_PASSION else sf if t < T_LOVE else 0.0)
    for t, d, m in toast():                                  # his toast: horns and cellos, as he sings it
        o.play('horns', m, t, max(d, 0.15), 100, sf, 0.75)
        o.play('cellos', m, t, max(d, 0.15), 92, sf, 0.45)
    # the stage: the drink, and the love potion taking hold
    o.hit('triangle', T_WALK[1] - 0.3, 70, gain=0.25, pan=sf)          # the horn handed over
    o.hit('gong scrape', T_DRINK + 0.2, 96, gain=0.45, pan=sf)        # he drinks: the forgetting
    o.hit('cymbal swell', T_LOVE - 1.4, 92, gain=0.4)
    o.hit('crash', T_PASSION, 112, gain=0.45)
    o.hit('timpani roll', T_SETTLE - 1.0, 100, pitch=-4, gain=0.4)
    o.effects([(0, -10), (D, -10)])
