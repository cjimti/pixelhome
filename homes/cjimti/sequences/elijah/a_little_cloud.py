"""A Little Cloud: the youth looks toward the sea, again and again, and finds nothing, until a cloud rises there.

The scene opens where the last one ended: the dust of the drought, Left cold where Baal's altar was, Elijah's amber
at his place on Right and the last of the mourning silver fading from Porch Front. "Go up now, child, and look toward
the sea": the youth is a small pale-sky light at the back corner of the porch, and when Elijah sends him his look
sweeps out from Porch Front, down Porch Right and the length of Right to its free end, the sea, and finds nothing
there. "There is nothing. The heavens are as brass": the look comes back empty and the sky on Porch Front turns a
dull brass. Then Mendelssohn's silence, held on the house: nothing moves. "Go up again": the look goes out a second
time, and comes back with "The earth is as iron under me", the house's two wings turning iron grey, and again the
silence.

"Behold, a little cloud ariseth now from the waters": the third look goes out, and at the free end of Right a small
grey-blue shape rises, the size of a man's hand, growing with each phrase. "The heavens are black with clouds and with
wind": dark storm cloud rolls in from the sea along the whole roofline, churning, with gusts of wind racing through
it and lightning flickering far off inside, while the storm "rusheth louder and louder", until the whole house is
under it. Elijah's amber holds steady through it all.

The music is Mendelssohn's own: three passages of No. 19, transcribed from the Novello octavo vocal score (1870) into
a_little_cloud.musicxml and timed by scripts/score_excerpt.py at the marked tempos, its two silences held. Elijah is
played on cellos and horns, the youth on flute. A production adds the weather: the sea's murmur at the free end, then
the wind rising and thunder far off.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL13'
TITLE = 'A Little Cloud'
KIND = 'show'
DESCRIPTION = ("The youth looks out toward the sea, again and again: there is nothing. Then a little cloud rises at "
               "the free end of Right, like a man's hand, and the storm rolls in over the whole house.")
VOICEOVER = 'Go up, and look toward the sea. And he looked, and said: there is nothing.'

EX = excerpt(__file__)                      # No. 19 bars 26-34, 51-56, 72-81
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
YOUTH = [n for n in EX['notes'] if n[5] == 'Youth']
SING = EX['singing']
EL_ON = np.array([n[0] for n in ELIJAH])
YO_ON = np.array([n[0] for n in YOUTH])
LOOKS = [BAR[27] + 1.3, BAR[52] + 0.4, BAR[73] - 0.4]           # "look toward the sea", "Behold"
REPLIES = [s[0] for s in SING if s[2] == 'Youth' and s[3].startswith('There is nothing')]
BRASS_AT = [s for s in SING if s[2] == 'Youth' and 'brass' in s[3]][0][:2]
IRON_AT = [s for s in SING if s[2] == 'Youth' and 'iron' in s[3]][0][:2]
SILENCES = [(BAR[34] + 3.0, BAR[35]), (BAR[56] + 3.0, BAR[57])]      # the fermata rests after "me."
T_CLOUD = BAR[73] + 2.4                     # the look reaches the sea and finds it
T_HAND = BAR[76]                            # "it is like a man's hand"
T_BLACK = BAR[77] + 0.6                     # "The heavens are black with clouds and with wind"
T_STORM = BAR[80]                           # "the storm rusheth louder and louder"
SWEEP = 2.4

DUST = hexc('#3a2008')                      # the drought
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
ASH = hexc('#3a4250')                       # where Baal's altar was
SILVER = hexc('#d8ecff')
SKY = hexc('#9cd8ff')                       # the youth
BRASSY = hexc('#8a6a30')                    # "the heavens are as brass"
IRON = hexc('#5a6070')                      # "the earth is as iron"
CLOUD = hexc('#7890b0')                     # the little cloud
STORM = hexc('#182438')                     # the storm cloud
GUST = hexc('#a0b8d0')
FLASH = hexc('#c8d8ff')


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    r0, r1 = span(G, 'Right')
    p0, p1 = span(G, 'Porch Front')
    return dict(home=r0 + 0.35 * (r1 - r0), youth=p1 - 0.12 * (p1 - p0), sea=r1, heaven=0.5 * (p0 + p1))


def frozen(t):
    """Time that stands still in Mendelssohn's silences: whatever flickers holds."""
    for a, b in SILENCES:
        if a <= t < b:
            return a
    return t


def render(G, seed=13):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p = places(G)
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    wings = np.isin(G.seg_of, ['Left', 'Right'])
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    span_all = d.max() - d.min()
    sea, yo = p['sea'], p['youth']
    gusts = np.sort(rng.uniform(T_BLACK, D, 26))
    gusts = np.concatenate([gusts[gusts < T_STORM][::2], gusts[gusts >= T_STORM]])
    flashes = [T_STORM - 2.2, T_STORM + 1.6, T_STORM + 4.6, D - 1.4]
    flash_at = rng.uniform(d.min() + 200, sea - 100, len(flashes))

    for f in range(F):
        t = f * DT
        ft = frozen(t)
        fr = light(DUST, 0.26 * np.ones(G.N))
        fr += light(ASH, 0.22 * left)

        # the storm rolling in from the sea: its front moves from the free end of Right back over the whole house
        if t >= T_BLACK:
            front = sea - (span_all + 200) * smoothstep(T_BLACK, D - 1.0, t) ** 0.8
            under = smoothstep(front - 60, front + 60, d)
            churn = 0.5 + 0.5 * np.sin(d / 37.0 - 1.7 * t) * np.sin(d / 23.0 + 1.1 * t)
            loud = 0.6 + 0.4 * smoothstep(T_STORM, D, t)
            fr = fr * (1 - 0.75 * under[:, None])
            fr += light(STORM, under * (0.35 + 0.25 * churn) * loud)
            fr += light(CLOUD, under * 0.22 * churn ** 3 * loud)
            for g in gusts:
                a = t - g
                if 0 <= a < 1.6:
                    x = sea - 900 * a
                    fr += light(GUST, 0.8 * loud * np.exp(-a / 0.8) * under * np.exp(-((d - x) / 50) ** 2))
            for k, tf in enumerate(flashes):
                a = t - tf
                if 0 <= a < 0.5:
                    fl = np.exp(-a / 0.07) + 0.5 * np.exp(-np.maximum(a - 0.18, 0) / 0.06) * (a > 0.18)
                    fr += light(FLASH, 0.8 * fl * under * np.exp(-((d - flash_at[k]) / 160) ** 2))
        else:
            under = np.zeros(G.N)

        # the people's candles, low, stirring in the wind
        lvl = 0.22 + 0.06 * smoothstep(T_CLOUD, T_CLOUD + 3, t)
        fr += light(CANDLE, cand * people * lvl * (0.7 + 0.3 * flick(ft)) * (1 - 0.3 * under))

        # Porch Front: the last of the mourning silver, then the sky as brass
        fr += light(SILVER, 0.12 * (1 - smoothstep(0.0, 3.0, t)) * heaven)
        b0, b1 = BRASS_AT
        fr += light(BRASSY, 0.45 * smoothstep(b0, b0 + 1.5, t) * (1 - smoothstep(BAR[35], BAR[35] + 2.0, t)) * heaven)
        i0, i1 = IRON_AT
        fr += light(IRON, 0.4 * smoothstep(i0, i0 + 1.5, t) * (1 - smoothstep(BAR[57], BAR[57] + 2.0, t)) * wings
                    * (1 - np.exp(-((d - p['home']) / 40) ** 2)))

        # Elijah: amber, flaring with every word, breathing slowly when he waits
        e = p['home']
        j = int(np.searchsorted(EL_ON, t, side='right')) - 1
        voice = float(np.exp(-(t - EL_ON[j]) / 0.45)) if j >= 0 else 0.0
        breathe = 0.08 * np.sin(2 * np.pi * ft / 4.0)
        fr += light(AMBER, (0.62 + breathe + 0.3 * voice) * np.exp(-((d - e) / 22) ** 2)
                    + (0.12 + 0.2 * voice) * np.exp(-((d - e) / 70) ** 2))
        fr += light(CORE, (0.4 + 0.4 * voice) * np.exp(-((d - e) / 5) ** 2))

        # the youth: a small pale-sky light at the back corner of the porch, brighter as he speaks
        k = int(np.searchsorted(YO_ON, t, side='right')) - 1
        speak = float(np.exp(-(t - YO_ON[k]) / 0.35)) if k >= 0 else 0.0
        come = smoothstep(BAR[26], BAR[26] + 2.0, t)
        fr += light(SKY, come * (0.45 + 0.4 * speak) * np.exp(-((d - yo) / 10) ** 2))
        # his looks: out from him to the sea, and back empty
        for n, lt in enumerate(LOOKS):
            a = t - lt
            if 0 <= a < SWEEP + 1.0:
                u = smoothstep(0, 1, min(a / SWEEP, 1.0))
                x = yo + (sea - yo) * u
                fade = 1.0 if a < SWEEP else np.exp(-(a - SWEEP) / 0.3)
                trail = np.where((d <= x) & (d >= yo), np.exp(-(x - d) / 120), 0)
                fr += light(SKY, fade * (0.95 * np.exp(-((d - x) / 22) ** 2) + 0.4 * trail))
        for rt in REPLIES:
            a = t - rt
            if 0 <= a < SWEEP:
                x = sea + (yo - sea) * smoothstep(0, 1, a / SWEEP)
                fr += light(SKY, 0.5 * np.exp(-((d - x) / 22) ** 2))

        # the little cloud at the sea, growing with every phrase until the storm takes it
        if t >= T_CLOUD:
            grow = smoothstep(T_CLOUD, T_HAND + 2.0, t) * 0.6 + 0.4 * smoothstep(T_HAND, T_BLACK, t)
            w = 6 + 34 * grow
            rise = 0.35 + 0.45 * smoothstep(T_CLOUD, T_CLOUD + 1.5, t)
            fr += light(CLOUD, rise * (0.6 + 0.4 * grow) * np.exp(-((d - (sea - w)) / w) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Elijah on cellos and horns, the youth on flute, the accompaniment on the orchestra; the sea, the wind and the
    thunder far off."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    p = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=2.9)
    size = lambda t: 0.3 if t < T_BLACK else 0.4 + 0.5 * smoothstep(T_BLACK, D, t)
    o.tutti(tidy(ORCH), size=size)
    pe, py, ps = pan_at(p['home']), pan_at(p['youth']), pan_at(p['sea'])
    for t, d, m, v, h, who in ELIJAH:
        o.play('cellos', m, t, d, v + 4, pe, 0.6)
        o.play('horns', m, t, d, v - 4, pe, 0.4)
    for t, d, m, v, h, who in YOUTH:
        o.play('flutes', m, t, d, v + 8, py, 0.7)
        o.play('clarinets', m - 12, t, d, v - 10, py, 0.2)

    o.effects([(0.0, -9.0), (T_BLACK - 1.0, -9.0), (T_STORM, -2.0)])
    for lt in LOOKS[:2]:
        o.wind(lt + 0.8, lt + 5.5, level=0.25, pan=ps, seed=int(lt))          # the sea's murmur, empty
    o.wind(T_CLOUD - 1.0, D, level=lambda tt: 0.3 + 0.7 * np.clip((tt - T_BLACK) / (D - T_BLACK), 0, 1),
           pan=lambda tt: ps - 1.4 * np.clip((tt - T_BLACK) / (D - T_BLACK), 0, 1), seed=19)
    o.thunder(T_STORM - 2.2, near=0.1, pan=0.3, gain=0.7)
    o.thunder(T_STORM + 1.6, near=0.25, pan=-0.2, gain=0.8)
    o.thunder(T_STORM + 4.6, near=0.4, pan=0.1, gain=0.9)
    o.hit('timpani roll', T_STORM, 90, pitch=-5, gain=0.35)
    o.hit('cymbal swell', D - 3.0, 96, gain=0.3)
