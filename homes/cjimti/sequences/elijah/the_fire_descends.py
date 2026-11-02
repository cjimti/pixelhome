"""The Fire Descends: Elijah calls the fire down, it falls from heaven onto his altar, and the people fall on their faces.

Elijah stands on Right in amber beside his altar, the unlit wood in the middle of Right; Baal's cold bronze altar is
on Left, the people's candles along Porch Left and Porch Right, and Porch Front, heaven, is dark. As he sings
"O Thou, who makest Thine angels spirits" silver points gather on Porch Front, more with each phrase, and on "Let
them now descend!" they draw together into one hard light in the middle of heaven.

Then the chorus: fire from heaven. White breaks from Porch Front, runs down Porch Right toward the street (which
reads as falling, in the street view) and lands on the altar, white to gold to red. Every "The fire descends from
heav'n!" the people cry sends another streak down after it, and the altar burns with the orchestra's racing figure;
Baal's bronze on Left goes colder. "Before Him upon your faces fall!": on every "fall" the people's candles drop to
the floor of the porch and slowly rise, and in the hush before the chorale they stay down, the fire banked to
embers. "The Lord is God": the candles rise, and warm light fills the house from the porch outward, swelling on each
held chord, until "before the Lord" holds it there.

The music is Mendelssohn's own: No. 16, the recitative and the chorus's first six bars, then from "Before Him" to
the end of the chorale, transcribed from the Novello octavo vocal score (1881) into the_fire_descends.musicxml and
timed by scripts/score_excerpt.py at the marked tempos (the recitative at crotchet 69, Allegro con fuoco at crotchet
152), its fermatas held twice as long. Elijah is played on cellos and horns, the people on strings with woodwinds
doubling and, in the chorale, the organ Mendelssohn's score has; the accompaniment is orchestrated from the piano
reduction. A production adds the fire: a rush as it falls, a blow as it lands, the roar of the burning offering.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL11'
TITLE = 'The Fire Descends'
KIND = 'show'
DESCRIPTION = ("Elijah calls on heaven, and fire falls down the porch onto his altar, white to gold to red. "
               "The people fall on their faces, then rise as warm light fills the house: the Lord is God.")
VOICEOVER = 'Then the fire of the Lord fell, and the people fell on their faces, and they said: the Lord is God.'

EX = excerpt(__file__)                      # No. 16: bars 1-12 (recitative, chorus start) and 32-60
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
T_FIRE = BAR[7]                             # the chorus: the fire falls
T_FALL = BAR[32]                           # "Before Him upon your faces fall!"
T_HUSH = BAR[38]                           # "fall . . . before Him", the fire banked
T_LORD = BAR[43] + 0.5 * (BAR[44] - BAR[43])  # "The Lord is God"
# every cry of "The fire descends": the first note of each sung phrase in the fire bars
CRIES = sorted({round(s[0], 3) for s in EX['singing'] if s[2] in VOICES and T_FIRE <= s[0] < T_FALL})
# every "fall": the sopranos' notes on that word (bars 34, 36, 38 and the last "fall!" of bar 42)
FALLS = [BAR[34], BAR[36], BAR[38], BAR[42] + 0.5 * (BAR[43] - BAR[42])]
FIG = np.array(sorted({round(n[0], 3) for n in ORCH if n[4] == 0 and n[1] < 0.2 and T_FIRE <= n[0] < T_FALL}))
FERMATAS = [BAR[43], BAR[45], BAR[47], BAR[50], BAR[53], BAR[60]]

DUST = hexc('#3a2008')                      # the drought
BRONZE = hexc('#b06a10')                    # Baal's altar
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
WOOD = hexc('#4a2a10')                      # his altar, unlit
SILVER = hexc('#d8ecff')                    # the angels
CANDLE = hexc('#ffcf8a')                    # the people
WHITE, GOLD, RED = hexc('#ffffff'), hexc('#ffc040'), hexc('#ff3000')   # fire from heaven


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def fire_colour(age):
    """Fire from heaven as it ages: white, then gold, then red."""
    age = np.asarray(age, float)[..., None]
    a = np.clip(age / 0.6, 0, 1)
    b = np.clip((age - 0.6) / 2.0, 0, 1)
    return (1 - a) * WHITE + a * ((1 - b) * GOLD + b * RED)


def render(G, seed=11):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    l0, l1 = span(G, 'Left')
    p0, p1 = span(G, 'Porch Front')
    r0, r1 = span(G, 'Right')
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    baal = l0 + 0.5 * (l1 - l0)
    elijah = r0 + 0.22 * (r1 - r0)
    altar = r0 + 0.5 * (r1 - r0)
    centre = p0 + 0.5 * (p1 - p0)
    porch = 0.5 * (span(G, 'Porch Left')[0] + span(G, 'Porch Right')[1])

    def blob(p, w):
        return np.exp(-((d - p) / w) ** 2)

    # the people: small candles along both porch runs, each with its own flicker
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 18, b - 10, 34):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 1.5, 6.0)
    burn = Flicker(rng, G.N, 4.0, 14.0)
    # the angels: points on Porch Front, appearing one by one as Elijah sings
    ang = np.sort(rng.uniform(p0 + 15, p1 - 15, 14))
    ang_t = np.sort(rng.uniform(0.3, BAR[6], len(ang)))
    el_on = np.array([n[0] for n in ELIJAH])
    streaks = [(T_FIRE, 1.0, 0.9)] + [(t, 0.7, 0.55) for t in CRIES if t > T_FIRE + 0.5]
    falls = np.array(FALLS)
    # how far the warm light has spread from the porch, and how strongly, through the chorale
    reach = max(np.abs(d - porch).max(), 1.0)

    def bow(t):
        """The people's candles, 1 standing, near 0 face down: each "fall" drops them, then they rise slowly."""
        if t < T_FALL:
            return 1.0
        if T_HUSH + 0.6 <= t < T_LORD:
            return 0.06
        k = falls[falls <= t]
        if len(k) == 0:
            return 1.0
        a = t - k[-1]
        down = 0.06 + 0.94 * (1 - np.exp(-max(a - 0.35, 0) / 1.4))
        return float(np.interp(a, [0, 0.35], [1, 0.06])) if a < 0.35 else down

    for f in range(F):
        t = f * DT
        fr = np.zeros((G.N, 3))
        lord = smoothstep(T_LORD, D - 4, t)                       # the chorale's warmth, 0..1
        swell = sum(np.exp(-((t - (tf + 1.2)) / 1.1) ** 2) for tf in FERMATAS if tf >= T_LORD - 1)

        # the drought over everything, heaven darker until the angels come
        fr += light(DUST, (0.28 - 0.1 * heaven) * np.ones(G.N))

        # Baal's altar on Left: cold bronze, colder once the fire has fallen on the other altar
        cold = 1 - 0.55 * smoothstep(T_FIRE, T_FIRE + 4, t)
        fr += light(BRONZE, left * (0.18 * cold) + 0.42 * cold * blob(baal, 40))

        # the angels gather on Porch Front as Elijah sings, and draw together on "Let them now descend!"
        if t < T_FIRE + 1.5:
            draw = smoothstep(BAR[6], T_FIRE, t)
            gone = 1 - smoothstep(T_FIRE, T_FIRE + 1.2, t)
            k = int(np.searchsorted(el_on, t, side='right')) - 1
            voice = float(np.exp(-(t - el_on[k]) / 0.5)) if k >= 0 else 0.0
            for p, ta in zip(ang, ang_t):
                if t >= ta:
                    pp = p + (centre - p) * draw
                    tw = 0.75 + 0.25 * np.sin(2 * np.pi * (0.6 * t + p / 37))
                    fr += light(SILVER, gone * smoothstep(ta, ta + 0.8, t) * (0.5 + 0.25 * voice) * tw * blob(pp, 7))
            fr += light(SILVER, gone * draw ** 2 * 0.9 * blob(centre, 10 + 20 * draw))

        # the fire falls: each streak runs from the middle of heaven down Porch Right onto the altar
        for ts, size, width in streaks:
            a = t - ts
            fall = 0.9 if size >= 1 else 0.6
            if 0 <= a < fall + 2.0:
                prog = min(1.0, a / fall)
                head = centre + (altar - centre) * prog ** 1.8
                after = max(a - fall, 0.0)
                trail = smoothstep(centre - 25, centre, d) * (d <= head + 8)
                glow = np.exp(-np.clip(head - d, 0, None) / (420 * size)) * np.exp(-after / (0.9 * size))
                fr += light(fire_colour(np.clip(a - 0.15 - (head - d) / 400, 0, None)),
                            size * trail * glow * (0.75 + 0.25 * burn(t)))
                fr += light(WHITE, size * np.exp(-after / 0.25) * blob(head, 22 * width + 10))
                if a >= fall:                                     # it lands: a flash on the altar
                    fr += light(fire_colour(after), size * np.exp(-after / 0.6) * blob(altar, 40 + 60 * size))

        # the burning offering on the altar: white to gold to red, racing with the orchestra's figure
        if t >= T_FIRE + 0.9:
            age = t - T_FIRE - 0.9
            i = int(np.searchsorted(FIG, t, side='right')) - 1
            race = float(np.exp(-(t - FIG[i]) / 0.08)) if i >= 0 and t - FIG[i] < 0.5 else 0.0
            level = 0.95 - 0.5 * smoothstep(T_HUSH, T_HUSH + 2.5, t) + 0.4 * lord
            col = fire_colour(age) if t < T_LORD else (1 - lord) * RED + lord * GOLD
            spread = 50 + 35 * (1 - smoothstep(T_HUSH, T_HUSH + 2.5, t))
            fr += light(col, level * (0.75 + 0.25 * burn(t) + 0.15 * race) * blob(altar, spread))
            fr += light(GOLD, 0.35 * level * race * blob(altar, 14))
        else:
            fr += light(WOOD, 0.55 * blob(altar, 60))

        # the people of Israel on both porch runs: they bow on every "fall", and rise with the chorale
        b = bow(t)
        rise = b if t < T_LORD else 0.06 + 0.94 * smoothstep(T_LORD, T_LORD + 12, t)
        fr += light(CANDLE, cand * (0.8 + 0.12 * flick(t)) * rise * people)
        if t >= T_LORD:                                           # warm light filling the house from the porch out
            front = smoothstep(0, 0.35, lord * 1.3 - np.abs(d - porch) / reach)
            warm = (1 - 0.4 * lord) * CANDLE + 0.4 * lord * GOLD
            fr += light(warm, (0.4 + 0.25 * lord + 0.15 * min(swell, 1.0)) * front)

        # Elijah, steady, his amber pulsing with his own voice
        k = int(np.searchsorted(el_on, t, side='right')) - 1
        voice = float(np.exp(-(t - el_on[k]) / 0.4)) if k >= 0 and t < T_FIRE + 1 else 0.0
        fr += light(AMBER, (0.8 + 0.15 * voice) * blob(elijah, 20) + 0.38 * blob(elijah, 110))
        fr += light(CORE, (0.45 + 0.3 * voice) * blob(elijah, 6))
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Elijah on cellos and horns over the strings' tremolo; the people on strings and woodwinds, with the organ in
    the chorale; the fire's rush, its landing and its roar."""
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, whoosh, _Voice, _load, _fade_out

    class Pipes(_Voice):
        """The VSCO2 pipe organ: samples are numbered, every third key (as in The Night Organist)."""

        def __init__(self, pattern, first):
            self.zones = {}
            for p in sorted(glob.glob(os.path.join(VSCO, pattern))):
                self.zones[first + int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', p).group(1))] = p
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.3):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]
            idx = np.arange(int((dur + release) * SR)) * 2 ** ((n - k) / 12)
            idx = idx[idx < a.shape[1] - 1]
            out = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            return _fade_out(out * (vel / 127) ** 1.3, dur, release)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    r0, r1 = span(G, 'Right')
    p0, p1 = span(G, 'Porch Front')
    altar, elijah, heaven = pan_at(r0 + 0.5 * (r1 - r0)), pan_at(r0 + 0.22 * (r1 - r0)), pan_at(0.5 * (p0 + p1))
    o = Orchestra(M, level=1.2)

    def size(t):
        if t < T_FIRE:
            return 0.3
        if t < T_HUSH:
            return 1.0
        if t < T_LORD:
            return 0.4
        return 0.5 + 0.5 * smoothstep(T_LORD, D - 8, t)
    o.tutti(tidy(ORCH), size=size, pan=lambda t, m: 0.25 * altar if t >= T_FIRE else 0.4 * elijah)

    # Elijah: cellos and horns, his "descend!" on low brass
    for t, d, m, v, h, who in ELIJAH:
        o.play('cellos', m, t, d, v - 4, elijah, 0.65)
        o.play('horns', m, t, d, v - 10, elijah, 0.5)
        if d > 1.0:
            o.play('trombones', m, t, d, v, elijah, 0.5)
            o.play('tuba', m - 12, t, d, v - 10, elijah, 0.35)

    # the people: strings with woodwinds doubling, the organ joining them in the chorale
    parts = {'S': [('violins', 0, -6, 0.45), ('oboes', 0, -10, 0.3), ('flutes', 0, -12, 0.25)],
             'A': [('violas', 0, -6, 0.45), ('clarinets', 0, -10, 0.3)],
             'T': [('cellos', 0, -6, 0.45), ('horns', 0, -10, 0.35)],
             'B': [('cellos', 0, -6, 0.4), ('basses', -12, -8, 0.4), ('bassoons', 0, -10, 0.3)]}
    pan_of = {'S': -0.35, 'A': -0.15, 'T': 0.15, 'B': 0.35}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pan_of[who] * 0.6, g)
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.16, reverb=0.45)
    M.bus('pedal', gain=0.22, reverb=0.35)
    for t, d, m, v, h, who in SUNG:
        if t >= T_LORD - 0.1:
            if who == 'B':
                M.add('pedal', ped.play(m, v, d), t - 0.03, 1.0, 0.0)
            else:
                M.add('organ', man.play(m, v, d), t - 0.03, 1.0, pan_of[who] * 0.5)

    # the fire: the rush as it falls from heaven, the blow as it lands, then the roar of the offering
    o.effects([(0, -6), (T_FIRE + 6, -6), (T_FALL, -12), (T_LORD, -16)])
    for k, t in enumerate([T_FIRE] + [c for c in CRIES if c > T_FIRE + 0.5]):
        big = 1.0 if k == 0 else 0.45
        M.add('fx', whoosh(0.6, 3000.0, 400.0, amp=0.5 * big, seed=k + 3), t - 0.05, 1.0, 0.5 * (heaven + altar))
        if k == 0:
            o.boom(t + 0.55, pan=altar)
            o.hit('crash', t + 0.55, 120, gain=0.5, pan=altar, fx=True)
            o.thunder(t + 0.5, near=0.9, pan=altar, seed=16)
        else:
            o.hit('timpani', t + 0.55, 104, pitch=-5, gain=0.35, pan=altar)
    roar = lambda tt: 0.9 * smoothstep(T_FIRE + 0.5, T_FIRE + 1.0, tt) * (1 - 0.6 * smoothstep(T_FALL, T_HUSH, tt))
    o.fire(T_FIRE + 0.5, T_LORD + 6, level=roar, pan=altar, crackle=14.0, seed=12)
    # "fall": the timpani under the people going down; the chorale's held chords
    for t in FALLS:
        o.hit('timpani roll', t, 90, pitch=-7, gain=0.35, pan=0.0)
    for t in FERMATAS[1:-1]:
        o.hit('timpani', t, 100, pitch=-5, gain=0.35)
    o.hit('cymbal swell', BAR[47] - 1.8, 100, gain=0.35)
    o.hit('timpani roll', BAR[60] - 0.4, 116, pitch=-5, gain=0.5)
    o.hit('crash', BAR[60], 104, gain=0.3)
