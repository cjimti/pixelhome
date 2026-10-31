"""Intermission: five minutes in Fafner's forest before Siegfried, and the brass calling the street back.

The house is the forest at midday: a deep green bed with sunlight dappling through it, and a bright green-gold fill
closing in from the wing ends toward the middle of Porch Front (pixelhome/intermission.py's countdown), so anyone
on the street can see how long is left. On every minute, as the countdown's wave runs over the filled part, the
Woodbird flits in ahead of the fill: a magenta point, white at its heart, hopping on each note of its call toward
the porch and then away. When the fill meets in the middle the brass call the audience back, and every note of the
fanfare flashes gold and white from the middle of Porch Front while the house swells, then settles for the show.

The music is Wagner's own, as an opera house's interval would have it: soft music to wait by, then the call-back.
The waiting music is the Forest Murmurs from Act II (bars 720 to 755, 764 to 787 and 818 to 871), Siegfried's
reverie under the lime tree and the forest in full voice with the Woodbird singing in it, timed like Solti's 1958
Vienna Philharmonic recording; the notes come from the Wagner Ring Dataset's piano reduction (pixelhome/ring.py),
orchestrated gently: the murmuring on strings, the horns' low pedal, the bird's calls on flute, oboe and clarinet.
Each minute a harp rolls the chord the forest is on and a solo flute plays the Woodbird's call over it. Then, as at
Bayreuth, where the audience is called back from each interval by a fanfare of a motif from the coming act played
from the balcony: Siegfried's horn call on the horns, the Sword on trumpets landing as the fill meets, and the horn
call again, farther off, as the house settles."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, nframes
from pixelhome.intermission import SECONDS, MARKS, countdown, order, reach
from pixelhome.leitmotifs import play as motif
from pixelhome.ring import Orchestra, excerpt, tidy

CODE = 'SF31'
TITLE = 'Intermission'
KIND = 'intermission'
DESCRIPTION = ('The house becomes a sunlit forest while bright green-gold closes in toward the porch, counting '
               'down five minutes; a magenta Woodbird flits in each minute, and a brass fanfare calls everyone back.')

D = SECONDS
FULL = MARKS['full']
EX = excerpt(__file__)                      # Act II, bars 720-755, 764-787 and 818-871, Solti 1958
T_BIRDS = EX['segments'][2]['start']        # the forest in full voice, the Woodbird singing in it

BED = hexc('#10a030')                       # deep forest
FILL = hexc('#c8f020')                      # sunlit green-gold
EDGE = hexc('#fff8c0')
SUN = hexc('#ffd040')
BIRD = hexc('#ff30d0')
WHITE = hexc('#ffffff')
GOLD = hexc('#ffc020')

# The Woodbird's call (Donington 27a) twice each minute: its beat, and when the two calls start after the minute
CALL_BEAT = 0.42
CALL_AT = (0.35, 2.9)


def call_notes(m):
    """(t, midi, dur) of the Woodbird's two calls for the minute at m, untransposed; the first call's long note is
    cut short where the second begins."""
    out = []
    for c, a in enumerate(CALL_AT):
        for t, n, v, d in motif('woodbird_call', m + a, CALL_BEAT):
            if c == 0:
                d = min(d, m + CALL_AT[1] - t - 0.1)
            out.append((t, n, d))
    return out


# The call-back: Siegfried's horn call, the Sword landing on FULL, the horn call again, farther off
HORN_BEAT = 0.4
SWORD_BEAT = 0.5
T_HORN1 = FULL - 4.6
T_SWORD = FULL - 0.5 * SWORD_BEAT            # the Sword's pickup, so its C lands as the fill meets
T_HORN2 = FULL + 5.6


def fanfare():
    """[(t, midi, dur, section, strength)] of the call-back's melody."""
    out = [(t, m, d, 'horns', 0.7) for t, m, v, d in motif('siegfried_horn', T_HORN1, HORN_BEAT)]
    out += [(t, m, d, 'trumpets', 1.0) for t, m, v, d in motif('sword', T_SWORD, SWORD_BEAT)]
    out += [(t, m, d, 'horns', 0.55) for t, m, v, d in motif('siegfried_horn', T_HORN2, HORN_BEAT)]
    return out


def bird_path(G, k, m):
    """The Woodbird's flight for minute k (at m seconds): from where it lands ahead of the fill, a hop per note
    toward the porch, then away. Returns a function t -> (path distance, level)."""
    v = order(G)
    reach_t = reach(m)
    right = k % 2 == 0                       # alternate wings
    side = (['Right', 'Porch Right'] if right else ['Left', 'Porch Left'])
    idx = np.concatenate([G.seg[s] for s in side] + [G.seg['Porch Front']])
    mid = np.mean(G.pd[G.seg['Porch Front']])
    idx = idx[(G.pd[idx] > mid) if right else (G.pd[idx] < mid)]
    start = G.pd[idx[np.argmin(np.abs(v[idx] - 0.75 * reach_t))]]
    end = G.pd[idx[np.argmin(np.abs(v[idx] - 0.3 * reach_t))]]
    notes = call_notes(m)
    hops = [start + (end - start) * (i + 1) / len(notes) for i in range(len(notes))]
    t_in, t_out = m - 0.6, notes[-1][0] + notes[-1][2] + 0.3

    def at(t):
        p = start + (start - end) * 0.8 * (1 - smoothstep(t_in, notes[0][0] - 0.1, t))   # flies in
        for (tn, _, _), h in zip(notes, hops):
            a = smoothstep(tn - 0.06, tn + 0.12, t)
            p = p + (h - p) * a
        p = p + (start - end) * 0.8 * smoothstep(t_out, t_out + 0.7, t)      # flies back off the way it came
        lvl = smoothstep(t_in, t_in + 0.3, t) * (1 - smoothstep(t_out + 0.2, t_out + 0.7, t))
        return p, lvl
    return at, t_in, t_out + 0.8


def render(G, seed=31):
    out = countdown(G, bed=BED, fill=FILL, edge=EDGE, level=(0.37, 0.64), seed=seed)
    F = len(out)
    t = np.arange(F) * DT
    d = G.pd
    v = order(G)
    reach_t = reach(t)

    # sunlight dappling through the leaves, on the part still to fill, gone by the finale
    for f0 in range(0, F, 400):
        tt = t[f0:f0 + 400, None]
        open_ = 1 - smoothstep(-0.03, 0.03, v[None] - reach_t[f0:f0 + 400, None])
        dap = np.clip(np.sin(2 * np.pi * (d[None] / 420 - tt / 29)) * np.sin(2 * np.pi * (d[None] / 170 + tt / 41)),
                      0, 1) ** 2
        out[f0:f0 + 400] += light(SUN, 0.32 * dap * open_ * (1 - smoothstep(FULL - 6, FULL, tt)))

    # the Woodbird each minute: magenta, white at its heart, the green dimmed round it so it reads
    for k, m in enumerate(MARKS['minutes']):
        at, t0, t1 = bird_path(G, k, m)
        for f in range(int(t0 / DT), min(F, int(t1 / DT) + 1)):
            p, lvl = at(f * DT)
            if lvl <= 0:
                continue
            flap = 0.85 + 0.15 * np.sin(2 * np.pi * 9 * f * DT)
            out[f] *= (1 - 0.9 * lvl * np.exp(-((d - p) / 50) ** 2))[:, None]
            out[f] += light(BIRD, 1.1 * lvl * flap * np.exp(-((d - p) / 18) ** 2))
            out[f] += light(WHITE, 0.85 * lvl * flap * np.exp(-((d - p) / 3.5) ** 2))
        for tn, _, _ in call_notes(m):                       # each note a small magenta ring
            p, _ = at(tn + 0.15)
            for f in range(int(tn / DT), min(F, int((tn + 1.0) / DT))):
                a = f * DT - tn
                out[f] += light(BIRD, 0.6 * np.exp(-a / 0.35) * np.exp(-((np.abs(d - p) - 260 * a) / 50) ** 2))

    # the fanfare: every note flashes white and gold out of the middle of Porch Front, the green parting before it
    c = np.mean(d[G.seg['Porch Front']])
    for tn, mm, dn, sec, s in fanfare():
        for f in range(int(tn / DT), min(F, int((tn + 1.4) / DT))):
            a = f * DT - tn
            r = 30 + 900 * s * (1 - np.exp(-a / 0.45))
            ring = np.exp(-((np.abs(d - c) - r) / (45 + 50 * s)) ** 2)
            e = np.exp(-a / 0.55)
            out[f] *= (1 - 0.45 * e * smoothstep(r + 60, r - 60, np.abs(d - c)))[:, None]
            out[f] += light(WHITE, 0.9 * s * e * ring) + light(GOLD, 0.6 * s * e * ring)
            out[f] += light(WHITE, 0.8 * s * np.exp(-a / 0.15) * np.exp(-((d - c) / (30 + 60 * s)) ** 2))
    return np.clip(out, 0, 1)


def chord_at(notes, t0, t1):
    """Pitch-class weights and the lowest note of the excerpt sounding between t0 and t1."""
    w, low = np.zeros(12), 127
    for n in notes:
        ov = min(n[0] + n[1], t1) - max(n[0], t0)
        if ov > 0:
            w[n[2] % 12] += ov * (1.5 if n[4] == 1 else 1.0)
            low = min(low, n[2])
    return w, low


def score(M, G):
    """The Forest Murmurs on the orchestra, a harp and the Woodbird's call each minute, the brass to call them back."""
    order_ = np.argsort(G.pd)
    xs, ds = G.pos[order_, 0], G.pd[order_]
    x0, x1 = xs.min(), xs.max()

    def pan_at(dd):                          # path distance -> left/right across the facade, from the street
        return float(0.85 * (2 * (np.interp(dd, ds, xs) - x0) / (x1 - x0) - 1))

    o = Orchestra(M, level=3.0)
    end = EX['seconds']
    notes = []
    for n in tidy(EX['notes']):              # gentler than the stage: velocities pulled in, the last bars fading out
        n = list(n)
        n[3] = float(np.clip(0.7 * n[3] + 14, 1, 88)) * float(np.interp(n[0], [end - 7, end], [1, 0.55]))
        notes.append(n)
    k = [0]

    def role(t, d, m, v, h):
        if t >= T_BIRDS and h == 0 and m >= 76 and d < 1.0:        # the Woodbird in the forest
            k[0] += 1
            return [(('flutes', 'oboes', 'clarinets')[(k[0] // 6) % 3], -12 if m > 88 else 0, 2, 0.5)]
        if h == 1 and m < 54 and d >= 1.5:                          # the horns' low pedal under the murmurs
            return [('horns', 0 if m >= 41 else 12, -6, 0.45), ('cellos', 0, -8, 0.35)]
        return None

    o.tutti(notes, size=lambda t: 0.3, role=role, pan=lambda t, m: 0.25 * np.sin(2 * np.pi * t / 37))

    # each minute: a harp rolls the forest's chord, and a solo flute plays the Woodbird's call over it
    for kk, m in enumerate(MARKS['minutes']):
        w, low = chord_at(EX['notes'], m - 0.5, m + 2.5)
        pcs = [int(p) for p in np.argsort(w)[::-1][:3] if w[p] > 0]
        at, _, _ = bird_path(G, kk, m)
        bird = pan_at(at(m + 1.0)[0])
        roll = [low - 12 if low >= 48 else low] + [n for n in range(48, 86) if n % 12 in pcs][:9]
        for j, n in enumerate(roll):
            o.play('harp', n, m + 0.06 * j, 2.0, 78 - 2 * j, pan=0.6 * bird, gain=0.8)
        tr = max(range(-6, 6), key=lambda s: sum(w[(n + s) % 12] for _, n, _ in call_notes(m)))
        for tn, n, dn in call_notes(m):
            o.play('flutes', n + tr, tn, max(dn, 0.2), 74, pan=bird, gain=0.65)

    # the call-back from the balcony: the horn call, the Sword on trumpets landing as the fill meets, the horn call
    # again, farther off. Under the Sword the trombones hold its harmony and the timpani roll in
    for tn, mm, dn, sec, s in fanfare():
        o.play(sec, mm, tn, dn + 0.1, int(70 + 36 * s), pan=0.0, gain=0.55 + 0.35 * s)
        if sec == 'trumpets':
            o.play('horns', mm - 12, tn, dn + 0.1, 92, pan=-0.1, gain=0.5)
        elif s >= 0.6:
            o.play('horns', mm + 12, tn, dn + 0.1, 70, pan=0.15, gain=0.3)
    sword_end = T_SWORD + 8 * SWORD_BEAT
    for n in (36, 43, 48, 52):
        o.play('trombones', n, FULL, sword_end - FULL + 0.4, 84, pan=0.05, gain=0.5)
    o.hit('timpani roll', FULL - 1.2, 84, pitch=-4, gain=0.35)
    o.hit('timpani', FULL, 100, pitch=-4, gain=0.5)
    o.hit('timpani', sword_end - 1.0, 96, pitch=-4, gain=0.4)
