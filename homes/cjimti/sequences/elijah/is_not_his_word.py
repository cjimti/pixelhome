"""Is Not His Word Like a Fire?: Elijah's hammer comes down on Baal's altar until it breaks, and a voice mourns.

The scene opens where the last one ended, the warm light of "The Lord is God" filling the house and the embers of
the offering on Right. The light settles back into the dust of the drought, and on Left Baal's bronze altar shows
again, cold. Then the aria, Allegro con fuoco: every blow of the orchestra's hammering ritornello is a stroke of
amber from Elijah's place on Right, a flash that rings out along the roofline, and his light flares with every word,
"Is not His word like a fire, and like a hammer that breaketh the rock into pieces?" On each "hammer" a bolt of
amber flies from him the whole way round the house, over the porch, and strikes the bronze on Left, which cracks a
little more at every blow. On "breaketh the rock into pieces" the orchestra's chord breaks it: the bronze bursts into
glints that scatter and go out, and Left is left cold and grey, the idol gone. Piu lento, "Is not His word like a
hammer", Elijah stands alone, and the orchestra's closing chords hammer the amber out across the whole house.

Then No. 18, the arioso: "Woe, woe unto them who forsake Him!" A single silver voice mourns on Porch Front, heaven,
swelling and sinking with her line, while the people's candles dim and the dust settles over the house again. Left
stays cold. The scene ends quiet, the voice fading on "against Him".

The music is Mendelssohn's own: No. 17 (its opening, "breaketh the rock into pieces" and the Piu lento with the
close) and the first nine bars of No. 18, transcribed from the Novello octavo vocal score (1870) into
is_not_his_word.musicxml and timed by scripts/score_excerpt.py at the marked tempos. Elijah is played on cellos and
horns, with trombones on the hammer; the mourning alto on oboe and clarinet. A production adds the hammer: an anvil
on every bolt that strikes, a crash and a breaking as the altar goes.

render() and score() both read the notes from the excerpt."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes, Flicker
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'EL12'
TITLE = 'Is Not His Word Like a Fire?'
KIND = 'show'
DESCRIPTION = ("Elijah's word comes down like a hammer: amber strokes ring out from Right and strike Baal's bronze "
               "altar on Left until it breaks into pieces and goes cold. Then a single silver voice mourns.")
VOICEOVER = 'Is not His word like a fire, and like a hammer that breaks the rock in pieces?'

EX = excerpt(__file__)                      # No. 17 bars 1-26, 78-90; No. 18 (bars 91-99)
BAR = {int(m): t for m, t in EX['bars']}
D = EX['seconds']
ORCH = [n for n in EX['notes'] if n[5] == 'Orch']
ELIJAH = [n for n in EX['notes'] if n[5] == 'Elijah']
ALTO = [n for n in EX['notes'] if n[5] == 'Alto']
T_BREAK = BAR[80]                           # "pie-ces": the altar breaks
T_LENTO = BAR[82]
T_CLOSE = BAR[86]
T_WOE = BAR[91]                             # No. 18
EL_ON = np.array([n[0] for n in ELIJAH])
AL_ON = np.array([n[0] for n in ALTO])
# the orchestra's hammer: the bass's blows in the ritornellos and the close
HAMMER_BARS = (1, 2, 5, 6, 9, 18, 25, 26, 86, 87, 88, 89)
BLOWS = np.array(sorted({round(n[0], 3) for n in ORCH if n[4] == 1 and n[1] >= 0.15
                         and any(BAR[b] - 0.01 <= n[0] < BAR[b] + 1.3 for b in HAMMER_BARS)}))
# on every "hammer" a bolt flies to Baal's altar
BOLTS = [BAR[b] for b in (8, 10, 16, 22, 23, 84)]
FLIGHT = 0.9

DUST = hexc('#3a2008')                      # the drought
WARM = 0.6 * hexc('#ffcf8a') + 0.4 * hexc('#ffc040')   # "The Lord is God", the light the last scene left
CANDLE = hexc('#ffcf8a')                    # the people
AMBER = hexc('#ffb040')                     # Elijah
CORE = hexc('#fff4d0')
BRONZE = hexc('#b06a10')                    # Baal's altar
GLINT = hexc('#ffcc55')
ASH = hexc('#3a4250')                       # what is left of it
EMBER = hexc('#ff3000')                     # the offering on Right, burning down
SILVER = hexc('#d8ecff')                    # the mourning voice


def span(G, seg):
    s = G.pd[G.seg[seg]]
    return float(s.min()), float(s.max())


def places(G):
    l0, l1 = span(G, 'Left')
    r0, r1 = span(G, 'Right')
    p0, p1 = span(G, 'Porch Front')
    return dict(elijah0=r0 + 0.22 * (r1 - r0), home=r0 + 0.35 * (r1 - r0), altar=r0 + 0.5 * (r1 - r0),
                baal=(l0 + 0.15 * (l1 - l0), l0 + 0.55 * (l1 - l0)), heaven=p0 + 0.5 * (p1 - p0))


def elijah_at(G, t):
    p = places(G)
    return p['elijah0'] + (p['home'] - p['elijah0']) * smoothstep(0.5, 4.0, t)


def strength(t):
    """How whole Baal's altar is: cracked a little by every bolt that lands, broken at "pieces"."""
    hits = sum(1 for b in BOLTS if b + FLIGHT <= t and b < T_BREAK)
    return 0.0 if t >= T_BREAK else max(0.0, 1.0 - 0.13 * hits)


def render(G, seed=12):
    rng = np.random.default_rng(seed)
    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    d = G.pd
    p = places(G)
    left = G.seg_of == 'Left'
    heaven = G.seg_of == 'Porch Front'
    people = np.isin(G.seg_of, ['Porch Left', 'Porch Right'])
    b0, b1 = p['baal']
    bc = 0.5 * (b0 + b1)
    altar = smoothstep(b0, b0 + 12, d) * (1 - smoothstep(b1 - 12, b1, d))
    cand = np.zeros(G.N)
    for seg in ('Porch Left', 'Porch Right'):
        a, b = span(G, seg)
        for c in np.arange(a + 14, b - 8, 26):
            cand += np.exp(-((d - c) / 5.0) ** 2)
    flick = Flicker(rng, G.N, 2.0, 7.0)
    glint = Flicker(rng, G.N, 3.0, 9.0)
    burn = Flicker(rng, G.N, 4.0, 12.0)
    shards = rng.uniform(-1, 1, 24)                 # where each piece of the altar flies, as a fraction of 140 units
    shard_at = bc + 0.5 * (b1 - b0) * rng.uniform(-1, 1, 24)

    for f in range(F):
        t = f * DT
        fr = light(DUST, 0.26 * np.ones(G.N))
        # the warm light of the last scene, settling back into the dust
        warm = 1 - smoothstep(0.0, 3.5, t)
        if warm > 0:
            fr += light(WARM, 0.68 * warm * np.ones(G.N))
        # the offering's embers on Right, burning down
        emb = 0.7 * (1 - smoothstep(1.0, 14.0, t))
        if emb > 0.01:
            fr += light(EMBER, emb * np.exp(-((d - p['altar']) / 40) ** 2) * (0.7 + 0.3 * burn(t)))

        # the people: candles, flaring at the break, dimming as the voice mourns
        lvl = 0.38 * (1 - 0.45 * smoothstep(T_WOE, T_WOE + 6.0, t)) + 0.55 * warm
        if T_BREAK <= t < T_BREAK + 2.0:
            lvl += 0.35 * np.exp(-(t - T_BREAK) / 0.5)
        fr += light(CANDLE, cand * people * lvl * (0.75 + 0.25 * flick(t)))

        # Baal's altar: cold bronze showing as the warm light goes, cracking at every bolt, broken at "pieces"
        s = strength(t)
        show = smoothstep(1.0, 4.0, t)
        if s > 0:
            jolt = 0.0
            for b in BOLTS:
                a = t - (b + FLIGHT)
                if 0 <= a < 0.6:
                    jolt = max(jolt, np.exp(-a / 0.18))
            fr += light(BRONZE, show * (0.25 + 0.4 * s + 0.4 * jolt) * altar)
            fr += light(GLINT, show * (0.4 * s * np.maximum(glint(t) - 0.6, 0) * 2.5 + 0.7 * jolt) * altar)
        if t >= T_BREAK:
            a = t - T_BREAK
            if a < 2.5:                              # the pieces fly and go out
                for k in range(len(shards)):
                    x = shard_at[k] + 140 * shards[k] * (1 - np.exp(-a / 0.5))
                    fr += light(GLINT, 0.9 * np.exp(-a / 0.6) * np.exp(-((d - x) / 5) ** 2) * left)
                fr += light(hexc('#ffffff'), 0.6 * np.exp(-a / 0.15) * altar)
            fr += light(ASH, 0.22 * smoothstep(T_BREAK, T_BREAK + 3.0, t) * left)

        # Elijah: amber, flaring on every word; a ring of light out from him on every blow of the hammer
        e = elijah_at(G, t)
        j = int(np.searchsorted(EL_ON, t, side='right')) - 1
        voice = float(np.exp(-(t - EL_ON[j]) / 0.35)) if j >= 0 and t < T_WOE else 0.0
        i = int(np.searchsorted(BLOWS, t, side='right')) - 1
        blow = float(np.exp(-(t - BLOWS[i]) / 0.18)) if i >= 0 else 0.0
        calm = 1 - 0.3 * smoothstep(T_WOE, T_WOE + 4.0, t) * (1 - smoothstep(D - 4.0, D - 0.5, t))
        fr += light(AMBER, calm * (0.62 + 0.3 * voice + 0.4 * blow) * np.exp(-((d - e) / 22) ** 2)
                    + calm * (0.12 + 0.2 * voice) * np.exp(-((d - e) / 60) ** 2))
        fr += light(CORE, calm * (0.4 + 0.4 * voice + 0.5 * blow) * np.exp(-((d - e) / 5) ** 2))
        for k in range(max(0, i - 2), i + 1):
            if k >= 0:
                a = t - BLOWS[k]
                if a < 0.9:
                    r = 25 + 500 * a
                    fr += light(AMBER, 0.75 * np.exp(-a / 0.3) * np.exp(-((np.abs(d - e) - r) / 22) ** 2))
        if T_CLOSE <= t < T_WOE:                     # the closing chords: amber over the whole house
            for k in range(i - 1, i + 1):
                if k >= 0 and BLOWS[k] >= T_CLOSE:
                    fr += light(AMBER, 0.25 * np.exp(-(t - BLOWS[k]) / 0.3) * np.ones(G.N))

        # the bolts: on every "hammer" an amber bolt flies from Elijah round the house to Baal's altar
        for b in BOLTS:
            a = t - b
            if 0 <= a < FLIGHT:
                u = smoothstep(0, 1, a / FLIGHT)
                x = e + (bc - e) * u
                trail = np.where((d - x) * np.sign(e - bc) >= 0, np.exp(-np.abs(d - x) / 110), 0)
                fr += light(AMBER, 1.0 * np.exp(-((d - x) / 16) ** 2) + 0.55 * trail)
                fr += light(CORE, 0.8 * np.exp(-((d - x) / 6) ** 2))

        # the mourning voice on Porch Front: silver swelling with every note of her line, fading at the end
        if t >= T_WOE - 1.0:
            k = int(np.searchsorted(AL_ON, t, side='right')) - 1
            note = float(np.exp(-(t - AL_ON[k]) / 0.8)) if k >= 0 else 0.0
            come = smoothstep(T_WOE - 1.0, T_WOE + 1.5, t)
            hc = p['heaven']
            fade = 1 - smoothstep(D - 3.5, D - 0.5, t)
            fr += light(SILVER, come * fade * (0.3 + 0.35 * note) * np.exp(-((d - hc) / (60 + 40 * note)) ** 2) * heaven)
            fr += light(SILVER, come * 0.12 * heaven)
        out[f] = fr
    return np.clip(out, 0, 1)


def score(M, G):
    """Elijah on cellos and horns, with trombones under every "hammer" and the break; the accompaniment on the full
    orchestra, its hammering ritornellos at full size; the alto on oboe with clarinet below."""
    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()
    p = places(G)

    def pan_at(dd):
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=1.45)
    sung = [(n[0], n[0] + n[1]) for n in ELIJAH + ALTO]
    size = lambda t: 0.45 if any(a - 0.05 <= t < b for a, b in sung) else (0.35 if t >= T_WOE else 1.0)
    o.tutti(tidy(ORCH), size=size, pan=lambda t, m: 0.3 * pan_at(elijah_at(G, t)) if t < T_WOE else 0.0)

    hammer = [(b, b + 2 * (BAR[9] - BAR[8])) for b in BOLTS] + [(BAR[78], T_LENTO)]
    for t, d, m, v, h, who in ELIJAH:
        pe = pan_at(elijah_at(G, t))
        o.play('cellos', m, t, d, v + 2, pe, 0.6)
        o.play('horns', m, t, d, v - 4, pe, 0.45)
        if any(a <= t < b for a, b in hammer):
            o.play('trombones', m, t, d, v - 6, pe, 0.4)
    ph = pan_at(p['heaven'])
    for t, d, m, v, h, who in ALTO:
        o.play('oboes', m, t, d, v + 4, ph, 0.6)
        o.play('clarinets', m - 12, t, d, v - 8, ph, 0.25)

    pb = pan_at(0.5 * sum(p['baal']))
    o.effects([(0.0, -3.0), (T_WOE - 1.0, -3.0), (T_WOE + 1.0, -12.0)])
    o.fire(0.0, 9.0, level=lambda tt: 0.5 * (1 - np.clip(tt / 9.0, 0, 1)), pan=pan_at(p['altar']), crackle=8.0)
    for b in BOLTS:
        o.hit('anvil', b + FLIGHT, 112, gain=0.25, pan=pb, fx=True)
        o.hit('timpani', b + FLIGHT, 104, pitch=-5, gain=0.3, pan=pb)
    for t in BLOWS:
        o.hit('anvil', t, 84, gain=0.08, pan=pan_at(elijah_at(G, t)))
    o.shatter(T_BREAK, pan=pb, gain=0.8)
    o.boom(T_BREAK, pan=pb, gain=0.7)
    o.hit('timpani roll', BAR[78], 96, pitch=-5, gain=0.3)
    o.hit('cymbal swell', T_CLOSE - 1.2, 90, gain=0.2)
    for b in (86, 88, 89):
        o.hit('timpani', BAR[b], 112, pitch=-5, gain=0.35)
