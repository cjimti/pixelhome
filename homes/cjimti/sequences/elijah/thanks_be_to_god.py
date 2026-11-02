"""Thanks Be to God: the rain comes, the drought is washed away, and the waters rush along the whole house.

The scene opens where the last one ended: the storm cloud dark over every run, churning, Elijah's amber on Right, the
people's candles low in the dust of the drought. The orchestra's first chord breaks it: rain. Blue streaks fall from
Porch Front, heaven, out along every run toward the street and the free ends, faster and thicker with every bar, and
where they fall the ochre of the drought washes away and the storm cloud thins. "Thanks be to God! He laveth the
thirsty land": the basses first, then the whole chorus, and with every phrase the people's candles on Porch Left and
Porch Right warm back up, until they burn at full warmth for the first time since the curse.

"The waters gather, they rush along!": the orchestra's rushing sixteenths become wave trains racing the roofline from
the sea at the free end of Right round to the far end of Side, crests of white spray on every sforzando. "The stormy
billows are high, their fury is mighty": the waves rise high and hard, the whole house heaving in blue, each furious
run of the orchestra a surge with spray thrown off its crest, and the waves hold still in the bars where the
orchestra drops out and the chorus sings alone. "But the Lord is above them, and Almighty": heaven on Porch Front
fills with a calm silver light, and under it the waves smooth out, slower and lower, into an even shimmer.

Then the last page: the orchestra's run down from on high, and "Thanks be to God! He laveth the thirsty land!" sung
in octaves by the whole chorus, the house full of warm candlelight over the blue, swelling on every word. On the last
held chord the rain falls quiet and the house settles: a calm rain-blue bed on every run, the people's candles at
full warmth, Elijah's amber at his place on Right and heaven a soft silver. The end of Part One.

The music is Mendelssohn's own: three passages of No. 20, transcribed from the Novello octavo vocal score (1870) into
thanks_be_to_god.musicxml and timed by scripts/score_excerpt.py at the marked tempo. The chorus is played on strings
with woodwinds and horns doubling, the orchestra's part on the full orchestra with brass and timpani on its
sforzandos. A production adds the weather: rain on the roof, thickening to a downpour, thunder rolling off into the
distance, the rush of the waves.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy, accents

CODE = 'EL14'
TITLE = 'Thanks Be to God'
KIND = 'show'
DESCRIPTION = ("The rain falls from heaven down every run and washes the drought away. The people's candles burn "
               "warm again, and the waters rush along the whole roofline: the end of Part One.")
VOICEOVER = 'And there was a great rain. Thanks be to God.'

EX = excerpt(__file__)                      # No. 20 bars 1-24, 53-73, 129-140
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
T_WATERS = BAR[20]                          # "The waters gather" (the orchestra's rush)
T_HOLD = BAR[24]                            # the orchestra's last sforzandos of the passage
T_BILLOWS = BAR[54] - 0.48                  # "The stormy billows are high"
T_LORD = BAR[65]                            # "But the Lord is above them"
T_LAST = BAR[129]                           # the last page: the run down
T_THANKS = BAR[131]                         # "Thanks be to God!" in octaves
T_END = BAR[140]                            # the last chord
# the orchestra's sixteenth runs and sforzandos: crests on the waves
RUNS = [BAR[b] for b in (20, 21, 22, 23, 55, 59, 61)]
SFZ = accents(ORCH, 0.0, D, vmin=110, n=3, space=0.25)
PHRASES = sorted({round(s[0], 3) for s in EX['singing'] if s[2] in VOICES})
CALM = [(BAR[58], BAR[59]), (BAR[62], BAR[63])]          # the chorus alone: the waves hold

DUST = hexc('#3a2008')                      # the drought, washed away
STORM = hexc('#182438')                     # the storm cloud the last scene left
CLOUD = hexc('#7890b0')
RAIN = hexc('#2060ff')                      # rain
SPRAY = hexc('#80c8ff')
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
SILVER = hexc('#d8ecff')                    # heaven, above the waters
SKY = hexc('#9cd8ff')                       # the youth, from the last scene


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    r0, r1 = span(G, 'Right')
    p0, p1 = span(G, 'Porch Front')
    return dict(home=r0 + 0.35 * (r1 - r0), heaven=0.5 * (p0 + p1), youth=p1 - 0.12 * (p1 - p0), sea=r1)


def rain_level(t):
    """How hard it rains: breaking at the first chord, a downpour by the waters, easing under the Lord, quiet at the
    last chord."""
    a = smoothstep(0.0, 4.0, t) * (0.55 + 0.45 * smoothstep(4.0, T_WATERS, t))
    a *= 1 - 0.45 * smoothstep(T_LORD, T_LORD + 6.0, t)
    a *= 1 - smoothstep(T_END - 1.0, D - 2.2, t)
    return a


def wave_level(t):
    """How high the waters run."""
    w = 0.6 * smoothstep(T_WATERS - 0.5, T_WATERS + 1.0, t) * (1 - 0.6 * smoothstep(T_HOLD, T_HOLD + 2.0, t))
    w = max(w, smoothstep(T_BILLOWS - 0.5, T_BILLOWS + 1.5, t) * (1 - 0.75 * smoothstep(T_LORD, T_LORD + 7.0, t)))
    w = max(w, 0.25 * smoothstep(T_THANKS, T_THANKS + 1.0, t))
    return w * (1 - smoothstep(T_END, D - 2.0, t))


def render(G, seed=14):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p = places(G)
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    hc = p['heaven']
    away = np.abs(d - hc)                       # distance from the middle of heaven along the roofline
    side = np.sign(d - hc)
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    cand = cand / cand.max()
    flick = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.6, 2.2)
    # raindrops: each falls from heaven outward along one side of the roofline
    K = 40
    t0 = rng.uniform(-3.0, 3.0, K)
    period = rng.uniform(1.6, 2.6, K)
    speed = rng.uniform(380.0, 620.0, K)
    sides = np.where(rng.random(K) < 0.5, -1.0, 1.0)
    lanes = rng.uniform(0, 1, K)
    reach = away.max()
    wet = np.zeros(G.N)                         # how much of the drought the rain has washed away, per pixel
    sfz = np.array(SFZ)
    phrases = np.array(PHRASES)

    for f in range(F):
        t = f * DT
        w = wave_level(t)
        r = rain_level(t) * (1 - 0.8 * w)
        # the rain washes the dust away where it falls, from heaven outward
        front = reach * 1.1 * smoothstep(0.5, BAR[12], t)
        wet = np.maximum(wet, smoothstep(front, front - 120, away))
        storm = 1 - smoothstep(0.5, BAR[10], t) * (0.35 + 0.65 * wet)
        fr = light(DUST, 0.26 * (1 - wet))
        churn = 0.5 + 0.5 * np.sin(d / 37.0 - 1.7 * t) * np.sin(d / 23.0 + 1.1 * t)
        fr = fr * (1 - 0.75 * storm[:, None])
        fr += light(STORM, storm * (0.35 + 0.25 * churn))
        fr += light(CLOUD, storm * 0.22 * churn ** 3)
        bed = 0.18 * wet * smoothstep(0.5, 6.0, t)
        fr += light(RAIN, bed)

        # the drops: streaks falling from heaven out along every run
        if r > 0.01:
            age = np.mod(t - t0, period)
            pos = age * speed
            live = (pos < reach + 40) & (lanes < r)
            if live.any():
                pp, ss = pos[live], sides[live]
                dist = (away[None, :] - pp[:, None])
                on_side = (side[None, :] == ss[:, None]) | (away[None, :] < 8)
                streak = np.where(dist <= 0, np.exp(dist / 22.0), np.exp(-dist / 4.0)) * on_side
                fr += light(RAIN, np.clip(0.5 * streak.sum(0), 0, 0.7))
                fr += light(SPRAY, np.clip(0.4 * (np.exp(-(dist / 4.0) ** 2) * on_side).sum(0), 0, 0.6))

        # the waters: wave trains racing the roofline from the sea round to Side, crests of spray
        if w > 0.01:
            frozen = next((a for a, b in CALM if a <= t < b), None)
            tw = frozen if frozen is not None else t
            fury = smoothstep(T_BILLOWS, T_BILLOWS + 1.0, t) * (1 - smoothstep(T_LORD, T_LORD + 5.0, t))
            k = 1 / (240.0 - 80.0 * fury)
            v = 200.0 + 100.0 * fury
            phase = (d + v * tw) * k * 2 * np.pi
            crest = np.maximum(np.sin(phase), 0) ** (1.5 + 2 * fury)
            fr += light(RAIN, w * (0.2 + 0.7 * crest))
            surge = 0.0
            for rt in RUNS:
                a = tw - rt
                if 0 <= a < 1.6:
                    surge = max(surge, np.exp(-a / 0.5))
            i = int(np.searchsorted(sfz, tw, side='right')) - 1
            hit = float(np.exp(-(tw - sfz[i]) / 0.2)) if i >= 0 else 0.0
            fr += light(SPRAY, w * crest * (0.3 + 0.55 * surge + 0.6 * hit))

        # heaven: the youth's point fading, then the calm silver of "the Lord is above them"
        fr += light(SKY, 0.45 * (1 - smoothstep(0.0, 3.0, t)) * np.exp(-((d - p['youth']) / 10) ** 2))
        lord = smoothstep(T_LORD - 0.5, T_LORD + 4.0, t) * (1 - 0.55 * smoothstep(T_LAST, T_LAST + 3.0, t))
        silver = 0.15 + 0.45 * lord + 0.12 * lord * shimmer(t)
        fr += light(SILVER, (silver * smoothstep(0.0, 3.0, t)) * heaven)
        if lord > 0.01:                                  # its light reaching down over the waters
            fr += light(SILVER, 0.18 * lord * np.exp(-away / 300.0) * (1 - heaven))

        # the people: candles warming up with every phrase, at full warmth by the end
        warm = 0.25 + 0.35 * smoothstep(BAR[6], BAR[19], t)
        j = int(np.searchsorted(phrases, t, side='right')) - 1
        lift = 0.18 * np.exp(-(t - phrases[j]) / 0.7) if j >= 0 and t < T_END else 0.0
        steady = smoothstep(T_END, D - 1.5, t)
        lvl = warm + lift * (1 - steady)
        fr += light(CANDLE, cand * people * lvl * ((0.8 + 0.2 * flick(t)) * (1 - steady) + steady))
        if t >= T_THANKS:                                # the octaves: warm light over the whole house
            fr += light(CANDLE, 0.22 * smoothstep(T_THANKS, T_THANKS + 1.0, t) * (1 - steady) * (1 - people))

        # Elijah: amber at his place on Right, steady through the storm
        e = p['home']
        fr += light(AMBER, 0.62 * np.exp(-((d - e) / 22) ** 2) + 0.12 * np.exp(-((d - e) / 70) ** 2))
        fr += light(CORE, 0.4 * np.exp(-((d - e) / 5) ** 2))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The chorus on strings, woodwinds doubling the sopranos and horns the inner voices; the orchestra's part on the
    full orchestra; rain, thunder rolling away and the rush of the waves."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    p = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.15)
    o.tutti(tidy(ORCH), size=lambda t: 0.6 if T_LORD <= t < T_LAST else 1.0)
    parts = {'S': [('violins', 0, -2, 0.5), ('flutes', 0, -10, 0.3), ('oboes', 0, -10, 0.25)],
             'A': [('violas', 0, -2, 0.5), ('clarinets', 0, -8, 0.3)],
             'T': [('cellos', 0, -2, 0.5), ('horns', 0, -6, 0.35)],
             'B': [('cellos', 0, -2, 0.45), ('basses', -12, -6, 0.4), ('trombones', 0, -10, 0.25)]}
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))
    side = {'S': pl, 'A': pl, 'T': pr, 'B': pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, 0.6 * side[who], g)
    for t in SFZ:
        o.hit('timpani', t, 108, pitch=-5, gain=0.3)
    o.hit('cymbal swell', T_WATERS - 1.2, 96, gain=0.25)
    o.hit('crash', T_WATERS, 100, gain=0.25)
    o.hit('timpani roll', T_LAST, 100, pitch=-5, gain=0.35)
    o.hit('crash', T_THANKS, 108, gain=0.3)
    o.hit('timpani roll', T_END, 104, pitch=-5, gain=0.35)

    # the weather: rain on the roof (high noise, thickening), thunder rolling away, the waves
    o.effects([(0.0, -2.0), (T_WATERS, -5.0), (T_LORD, -9.0), (T_LAST, -12.0)])
    rain = lambda tt: 0.25 + 0.55 * np.array([rain_level(x) for x in np.atleast_1d(tt)])
    o.fire(0.0, D, level=rain, pan=0.0, crackle=30.0, seed=41)            # the patter of rain on the roof
    o.thunder(0.4, near=0.7, pan=pan_at(p['sea']), gain=0.9)
    o.thunder(BAR[8], near=0.35, pan=-0.3, gain=0.6)
    o.thunder(BAR[16], near=0.15, pan=0.4, gain=0.45)
    o.wind(T_WATERS - 0.5, T_HOLD + 2.0, level=0.5, pan=lambda tt: pan_at(p['sea']) - 1.5 * (tt - T_WATERS) / 6.0)
    o.wind(T_BILLOWS, T_LORD + 4.0, level=lambda tt: 0.8 - 0.5 * np.clip((tt - T_LORD) / 4.0, 0, 1), pan=0.0, seed=21)
    o.thunder(BAR[57], near=0.5, pan=0.2, gain=0.6)
