"""Your Light Break Forth: the end of Elijah. The righteous shine, Malachi's promise that Elijah will come again, and
the house filling with morning light to the last Amen.

The scene opens where the chariot left it, the whole house glowing gold, heaven warm on Porch Front and a last ember
at the far end of Side, where Elijah went. "Then, then shall the righteous shine forth as the sun in their
heav'nly Father's realm": the tenor's every note sends a warm ring out from the middle of the porch, the people's
candles brighten on Porch Left and Porch Right, and on "shine" a sun-warm glow opens across Porch Front.

"Behold, God hath sent Elijah the prophet": a silver voice on Porch Front, flaring with every syllable, and Elijah
comes back. His amber leaves heaven, runs down Porch Right toward the street and along Right to his old place,
arriving on the forte chord of "prophet". "Before the coming of the great and dreadful day of the Lord": the house
darkens, a slow red swells from heaven on "dreadful", and falls away to a quiet C major on "Lord".

"And then shall your light break forth as the light of morning": the orchestra's rushing scales throw streaks of
light out from the porch to both ends of the house, and morning light breaks out of Porch Front and spreads. "Thou
fillest heav'n with glory": heaven blazes. Then the Amen, the bass rising a semitone at a time under it: every step
pushes the morning light further out along the roofline, the sopranos' notes glinting on it, until the whole house
is full, warm and still, held through the last chord.

The music is Mendelssohn's own: No. 39 bars 1-6, No. 40 to "the day of the Lord", and the first five and last
eighteen bars of No. 42, transcribed from the Novello octavo vocal score into your_light_break_forth.musicxml and
timed by scripts/score_excerpt.py at the marked tempos. The tenor plays on horns and violas, the soprano on flutes and
oboe, the chorus on strings with woodwinds doubling, and the Amen on the full orchestra with the organ Mendelssohn's
score has; a production adds a harp as Elijah descends, a timpani roll under "dreadful", a cymbal swell into the
light, and timpani under the last Amen.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL23'
TITLE = 'Your Light Break Forth'
KIND = 'show'
DESCRIPTION = ("The righteous shine forth, Elijah is promised again, and morning light breaks out of heaven and fills "
               "the house to the last Amen.")
VOICEOVER = 'Behold, I will send you Elijah the prophet. And then shall your light break forth, as the morning.'

EX = excerpt(__file__)                      # No. 39 bars 1-6, No. 40 bars 1-8, No. 42 bars 1-5 and its last 18
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
VOICES = ('S', 'A', 'T', 'B')
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
SUNG = [n for n in EX['notes'] if n[5] in VOICES]
TENOR = [n for n in EX['notes'] if n[5] == 'Tenor']
SOPRANO = [n for n in EX['notes'] if n[5] == 'Soprano']
T_SENT = BAR[7]                             # No. 40: "Behold, God hath sent Elijah"
T_PROPHET = BAR[10]                         # the forte chord on "prophet": Elijah arrives
T_DREAD = BAR[13]                           # "dreadful day"
T_LORD = BAR[14]
T_LIGHT = BAR[15]                           # No. 42: "And then shall your light break forth"
T_CLOSE = BAR[20]                           # "Thou fillest heav'n with glory"
T_HEAVEN = BAR[21]
T_AMEN = BAR[23]                            # the bass's first "Amen"; it rises a semitone at a time from here
T_LAST = BAR[37]
TEN_ON = np.array([n[0] for n in TENOR])
SOP_ON = np.array([n[0] for n in SOPRANO])
RUNS = [BAR[15], BAR[17], BAR[19]]          # the orchestra's rushing scales
BASS = sorted((n[0], n[2]) for n in SUNG if n[5] == 'B' and n[0] >= T_CLOSE - 0.01)
STEPS = np.array([t for t, m in BASS if t >= T_AMEN - 0.01])
S_AMEN = np.array([n[0] for n in SUNG if n[5] == 'S' and n[0] >= T_AMEN - 0.01])

GOLD = hexc('#ffc040')                      # what the chariot left
CANDLE = hexc('#ffcf8a')                    # the people
SUN = hexc('#ffd890')                       # the righteous shining
SILVER = hexc('#d8ecff')                    # the voice from heaven
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
RED = hexc('#ff3000')                       # the dreadful day
MORNING = hexc('#ffd49a')                   # the light of morning
WHITE = hexc('#ffffff')
HEAVEN = hexc('#fff0c8')                    # heaven's warm light, as the chariot left it


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    p0, p1 = span(G, 'Porch Front')
    r0, r1 = span(G, 'Right')
    return dict(heaven=0.5 * (p0 + p1), home=r0 + 0.35 * (r1 - r0))


def outward(G):
    """0 at the middle of Porch Front to 1 at the farthest end of the house, along the roofline."""
    h = places(G)['heaven']
    out = np.abs(G.pd - h)
    return out / out.max()


def elijah_at(G, t):
    """Elijah comes down from heaven, along Porch Right and Right, to his place, arriving on "prophet"."""
    p = places(G)
    k = smoothstep(BAR[9], T_PROPHET, t)
    return p['heaven'] + (p['home'] - p['heaven']) * k


def reach(t):
    """How far out along the house the morning light has come (0..1.05)."""
    r = 0.12 * smoothstep(T_LIGHT + 0.5, BAR[17], t) + 0.18 * smoothstep(BAR[17], BAR[18] + 1.0, t)
    r += 0.12 * smoothstep(BAR[19], T_CLOSE, t) + 0.1 * smoothstep(T_CLOSE, T_AMEN, t)
    k = int(np.searchsorted(STEPS, t, side='right'))           # each step of the rising bass pushes it out
    if k:
        frac = smoothstep(0, 0.9, t - STEPS[k - 1])
        r += 0.53 * (k - 1 + frac) / len(STEPS)
    return r


def render(G, seed=39):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    u = outward(G)
    p = places(G)
    seg = G.seg_of
    people = np.isin(seg, ['Porch Left', 'Porch Right'])
    front = seg == 'Porch Front'
    s0, s1 = span(G, 'Side')
    p0, p1 = span(G, 'Porch Front')
    pf = np.clip(1 - np.abs(d - p['heaven']) / (0.5 * (p1 - p0)), 0, 1)       # 1 at heaven's middle, 0 at its ends
    cand = np.zeros(G.N)
    for name in ('Porch Left', 'Porch Right'):
        a, b = span(G, name)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    shimmer = Flicker(rng, G.N, 0.8, 3.0)
    glint = rng.uniform(0, 1, G.N)

    for f in range(F):
        t = f * DT
        # the bed: the chariot's gold, cooling to a quiet warm dark through the promise, then morning
        gold = 0.2 * (1 - smoothstep(0.5, T_SENT, t))
        dusk = 0.12 + 0.06 * smoothstep(T_SENT, T_SENT + 4, t)
        dread = smoothstep(T_DREAD - 1.5, T_DREAD + 0.5, t) * (1 - smoothstep(T_LORD, T_LORD + 1.5, t))
        fr = light(GOLD, (gold + dusk * (1 - 0.5 * dread)) * np.ones(G.N))

        # where Elijah went: the ember at Side's far end, going out
        ember = 0.5 * (1 - smoothstep(0.0, 4.0, t))
        if ember > 0:
            fr += light(AMBER, ember * np.exp(-((d - s0) / 8) ** 2))

        # heaven: warm at first (as the chariot left it), the sun opening across it on "shine"
        warm = 0.6 * (1 - smoothstep(2.0, T_SENT - 1, t))
        sun = smoothstep(BAR[3], BAR[3] + 2.0, t) * (1 - smoothstep(BAR[6] + 1.0, T_SENT + 1.5, t))
        fr += light(HEAVEN, warm * front) + light(SUN, 0.7 * sun * pf ** 0.7 * front)

        # the righteous: every note of the tenor sends a warm ring out from heaven; the candles brighten
        if t < T_SENT + 2:
            i0 = int(np.searchsorted(TEN_ON, t - 3.0))
            i1 = int(np.searchsorted(TEN_ON, t, side='right'))
            for k in range(i0, i1):
                a = t - TEN_ON[k]
                ring = np.exp(-((u - a / 3.0) / 0.08) ** 2)
                fr += light(SUN, 0.8 * np.exp(-a / 2.0) * ring)
        lit = 0.35 + 0.25 * smoothstep(BAR[2], BAR[5], t) - 0.2 * smoothstep(T_SENT, T_SENT + 3, t) \
            + 0.35 * smoothstep(T_LIGHT, T_CLOSE, t)
        fr += light(CANDLE, cand * people * lit * (1 - 0.6 * dread) * (0.75 + 0.25 * flick(t)))

        # the voice from heaven: silver on Porch Front, flaring with every syllable
        if T_SENT - 0.5 <= t < T_LIGHT + 1.0:
            j = int(np.searchsorted(SOP_ON, t, side='right')) - 1
            word = float(np.exp(-(t - SOP_ON[j]) / 0.5)) if j >= 0 else 0.0
            on = smoothstep(T_SENT - 0.5, T_SENT + 1.0, t) * (1 - smoothstep(T_LIGHT, T_LIGHT + 1.0, t))
            fr += light(SILVER, on * (0.35 + 0.45 * word) * pf ** 0.5 * front)
            fr += light(WHITE, on * 0.5 * word * np.exp(-((d - p['heaven']) / 6) ** 2))
            i0 = int(np.searchsorted(SOP_ON, t - 2.5))         # each syllable a silver wave down to the people
            for k in range(i0, j + 1):
                a = t - SOP_ON[k]
                wave = np.exp(-((u - 0.12 - a / 4.0) / 0.06) ** 2) * (u < 0.62)
                fr += light(SILVER, 0.7 * on * np.exp(-a / 1.2) * wave)

        # Elijah: sent from heaven to his place on Right, flaring as he lands, then staying through the end
        if t >= BAR[9] - 0.5:
            e = elijah_at(G, t)
            come = smoothstep(BAR[9] - 0.5, BAR[9] + 0.5, t)
            land = float(np.exp(-(t - T_PROPHET) / 0.7)) if t >= T_PROPHET else 0.0
            size = 14 + 16 * land
            fr += light(AMBER, come * (0.75 + 0.5 * land) * np.exp(-((d - e) / size) ** 2))
            fr += light(CORE, come * (0.5 + 0.4 * land) * np.exp(-((d - e) / 4) ** 2))
            if t < T_PROPHET:                       # a trail behind him as he comes down
                fr += light(AMBER, 0.55 * come * np.exp(-np.clip(np.sign(e - p['heaven']) * (e - d), 0, None) / 60)
                            * (np.abs(d - p['heaven']) < np.abs(e - p['heaven'])))

        # the dreadful day: a slow red from heaven, darkening the house
        if dread > 0.01:
            fr += light(RED, 0.5 * dread * np.exp(-(u / 0.35) ** 2))

        # the light breaks forth: a streak out to both ends on every rushing scale
        for tr in RUNS:
            a = t - tr
            if 0 <= a < 1.6:
                head = a / 0.7
                streak = np.exp(-((u - head) / 0.06) ** 2) + 0.4 * (u < head) * np.exp(-(head - u) / 0.15)
                fr += light(WHITE if a < 0.4 else MORNING, 0.9 * np.exp(-a / 0.9) * streak)

        # morning: the light filling the house outward from heaven, its edge bright
        if t >= T_LIGHT:
            r = reach(t)
            filled = smoothstep(r + 0.03, r - 0.03, u)
            edge = np.exp(-((u - r) / 0.04) ** 2) * (r < 1.0)
            full = smoothstep(T_LAST - 6, T_LAST, t)
            lvl = 0.55 + 0.12 * full + 0.06 * (shimmer(t) - 0.5) * (1 - full)
            fr = fr * (1 - 0.6 * filled[:, None]) + light(MORNING, lvl * filled) + light(WHITE, 0.45 * edge)
            # "Thou fillest heav'n with glory": heaven blazes
            blaze = smoothstep(T_HEAVEN - 0.3, T_HEAVEN + 0.4, t) * (1 - 0.5 * smoothstep(T_HEAVEN + 1.5, T_AMEN, t))
            fr += light(WHITE, 0.55 * blaze * pf ** 0.5 * front)
            # the sopranos' Amen: a glint on the light for each note
            j = int(np.searchsorted(S_AMEN, t, side='right')) - 1
            if j >= 0 and t < T_LAST:
                g = float(np.exp(-(t - S_AMEN[j]) / 0.5))
                pick = (glint > 0.92) * filled
                fr += light(WHITE, 0.3 * g * pick)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """The tenor on horns and violas, the soprano on flutes and oboe, the chorus on strings with woodwinds doubling and
    the organ in the close, the orchestra from the piano reduction; harp, timpani and cymbal as a production would."""
    import glob
    import os
    import re
    from pixelhome.audio import SR, VSCO, _Voice, _load, _fade_out

    class Pipes(_Voice):
        """The VSCO2 pipe organ: samples are numbered, every third key."""

        def __init__(self, pattern, first):
            self.zones = {}
            for path in sorted(glob.glob(os.path.join(VSCO, pattern))):
                self.zones[first + int(re.search(r'_(\d+)(?:_rr\d+)?\.wav$', path).group(1))] = path
            self.keys = np.array(sorted(self.zones))

        def play(self, n, vel=100, dur=1.0, release=0.3):
            n = self._place(n)
            k = int(self.keys[np.argmin(np.abs(self.keys - n))])
            a = _load(self.zones[k])[:, int(0.04 * SR):]
            idx = np.arange(int((dur + release) * SR)) * 2 ** ((n - k) / 12)
            idx = idx[idx < a.shape[1] - 1]
            res = np.vstack([np.interp(idx, np.arange(a.shape[1]), a[c]) for c in range(2)])
            return _fade_out(res * (vel / 127) ** 1.3, dur, release)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    p = places(G)
    heaven = pan_at(p['heaven'])
    o = Orchestra(M, level=1.25)

    def size(t):
        if t < T_SENT:
            return 0.35
        if t < T_LIGHT:
            return 0.3
        if t < T_CLOSE:
            return 1.0
        return 0.75 + 0.25 * smoothstep(T_AMEN, T_LAST, t)
    o.tutti(tidy(ORCH), size=size)

    # the righteous: the tenor on horns and violas
    for t, d, m, v, h, who in TENOR:
        o.play('horns', m, t, d, v, heaven, 0.6)
        o.play('violas', m, t, d, v - 8, heaven, 0.35)
    # the voice from heaven: flutes and oboe
    for t, d, m, v, h, who in SOPRANO:
        o.play('flutes', m, t, d, v + 4, heaven, 0.55)
        o.play('oboes', m, t, d, v - 6, heaven, 0.35)

    # the chorus: strings with woodwinds doubling; the organ joins in the close
    parts = {'S': [('violins', 0, -6, 0.45), ('oboes', 0, -10, 0.3), ('flutes', 0, -12, 0.25)],
             'A': [('violas', 0, -6, 0.45), ('clarinets', 0, -10, 0.3)],
             'T': [('cellos', 0, -6, 0.45), ('horns', 0, -10, 0.35)],
             'B': [('cellos', 0, -6, 0.4), ('basses', -12, -8, 0.4), ('bassoons', 0, -10, 0.3)]}
    pl = pan_at(0.5 * sum(span(G, 'Porch Left')))
    pr = pan_at(0.5 * sum(span(G, 'Porch Right')))
    pan_of = {'S': 0.5 * pl, 'A': 0.25 * pl, 'T': 0.25 * pr, 'B': 0.5 * pr}
    for t, d, m, v, h, who in SUNG:
        for section, tr, dv, g in parts[who]:
            o.play(section, m + tr, t, d, v + dv, pan_of[who], g)
        if t >= T_CLOSE and d >= 0.6 and who in ('S', 'A'):
            o.play('trumpets' if who == 'S' else 'horns', m - (12 if m > 74 else 0), t, d, v - 12, pan_of[who], 0.3)
    man = M._voice(Pipes('Keys/Organ/Loud/Rode_Man3Open_*.wav', 35), 'Keys/Organ/Loud manual', 'auto')
    ped = M._voice(Pipes('Keys/Organ/Loud/Rode_Pedal_*.wav', 35), 'Keys/Organ/Loud pedal', 'auto')
    M.bus('organ', gain=0.12, reverb=0.45)
    M.bus('pedal', gain=0.17, reverb=0.35)
    for t, d, m, v, h, who in SUNG:
        if t >= T_LIGHT - 0.1:
            dd = d + (2.0 if t >= T_LAST - 0.05 else 0.0)
            if who == 'B':
                M.add('pedal', ped.play(m, v, dd), t - 0.03, 1.0, 0.0)
            else:
                M.add('organ', man.play(m, v, dd), t - 0.03, 1.0, pan_of[who] * 0.5)

    # Elijah sent from heaven: a harp running down as he comes, a soft swell into "prophet"
    notes = [84, 79, 76, 72, 67, 64, 60, 55, 52, 48]
    for k, m in enumerate(notes):
        tt = BAR[9] + k * (T_PROPHET - BAR[9] - 0.2) / len(notes)
        o.play('harp', m, tt, 0.6, 70, pan_at(elijah_at(G, tt)), 0.7)
    o.hit('cymbal swell', T_PROPHET - 1.6, 80, gain=0.2, pan=pan_at(p['home']))
    # the dreadful day: a timpani roll under it, a low gong
    o.hit('timpani roll', T_DREAD - 0.3, 84, pitch=-7, gain=0.3, pan=heaven)
    o.hit('gong', T_DREAD + 0.2, 70, gain=0.15, pan=heaven)
    # the light breaks forth: a cymbal swell into it, timpani on the scales' tops
    o.hit('cymbal swell', T_LIGHT - 1.4, 92, gain=0.25)
    for tr in RUNS:
        o.hit('timpani', tr + 0.6, 104, pitch=-2, gain=0.3)
    # the Amen: a timpani roll growing under the last bars, the last chord struck
    o.hit('timpani roll', BAR[34], 84, pitch=-2, gain=0.25)
    o.hit('timpani roll', BAR[36], 100, pitch=-2, gain=0.3)
    o.hit('timpani', T_LAST, 112, pitch=-2, gain=0.4)
    o.hit('cymbal swell', T_LAST - 1.4, 90, gain=0.2)
