"""Fetch!: a little ghost dog plays fetch on the roof. Wisps gather by the front door into a dog: a white
ghost body, a wagging wisp of a tail and a glowing orange nose that lights with a woof. His owner, a pale
figure over the porch, throws a bone; it sails along the roof onto the left wing, the dog scrabbles after
it, sniffs, picks it up and trots it back. He rolls over for applause. The second throw goes right and he
snatches it the moment it lands; then he chases his tail, faster and faster, until he's dizzy and stars
circle him. The third throw goes the length of the right wing and he overtakes it and catches it in the
air. He begs, wagging, and boops his owner's hand. The last throw is a big one: the bone sails off round
the back of the house (out along Side) and the dog shoots off after it. Nothing. His owner looks after
them, something crashes back there... and then, from the other way, the dog's tail backs in out of the
free right end, then the dog, tugging, and behind him a bone the size of a whole skeleton. How did he get
round there? Heave by heave he drags it up to the porch and drops it with a thud, barks three times, and
everyone dances while sparkles go off along the roof, to a big finish.

Everything is placed in path distance and drawn as spans with exact span-over-pixel coverage, so the dog
and the bones keep their size on every run. Times are in beats of a 96 BPM ragtime (BEAT), shared with
score() through the module constants and _plan()."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, keys, lerp, nframes

CODE = 'NB02'
TITLE = 'Fetch!'
KIND = 'show'
DESCRIPTION = ('A little ghost dog plays fetch along the roof, faster every throw, with tricks in between. The '
               'last throw sails round the back of the house, and he drags in something much too big from the '
               'other end.')

NIGHT = hexc('#1a2c90')
GHOST = hexc('#cfe0ff')
NOSE = hexc('#ff4a10')
BONE = hexc('#fff0d6')
MAN = hexc('#ffd8a8')
GOLD = hexc('#ffc040')
SPARKS = [hexc(c) for c in ('#ffc040', '#ff6a10', '#ffffff', '#7fd13b')]

BPM = 96
BEAT = 60 / BPM                              # ragtime: a bar is four beats, 2.5 s
APPEAR, POP = 4.0, 7.0                       # wisps gather into the dog; his nose lights with a woof
THROWS = [  # thrown, beats in the air, where it lands from the owner, dog sets off, gets it, picks up, home
    (8.0, 2.0, -900.0, 8.5, 10.5, 11.0, 15.0),
    (20.0, 1.5, 520.0, 20.25, 21.5, 21.5, 24.5),
    (30.0, 2.0, 1000.0, 30.0, 31.5, 31.5, 33.5),        # caught in the air
]
ROLL = (17.0, 19.0)                          # rolls over
SPIN, DIZZY = (25.0, 28.0), (28.0, 29.5)      # chases his tail, then the stars
BEG, BOOP = (35.0, 39.0), 38.0               # begs, wagging, and boops his owner
WIND, FLING, FLY, GO, GONE = 39.0, 40.0, 2.0, 40.5, 42.5   # the big throw, out round the back (along Side)
LOOKS, CRASH = (43.5, 46.0), 45.0            # the owner looks after them, then the other way; a crash back there
DRAG, HEAVE = (48.0, 64.0), 0.6               # tugging the giant bone in from the right end, a heave a beat
DROP = 64.0
WOOFS = (POP, 16.0, 24.75, 34.0, 34.5, 65.0, 66.0, 67.0)
PARTY, TA, FINAL, OUT = (68.0, 76.0), 76.0, 78.0, 82.0
D = 84 * BEAT

K = 1.0
TOY = [(-13, -8, 1.0), (-8, 8, 0.7), (8, 13, 1.0)]                 # a bone: knob, shaft, knob
GIANT = [(0, 55, 1.0), (55, 465, 0.72), (465, 520, 1.0)]           # a bone as long as a skeleton


def _hit(f, k=0.12):
    """Flash envelope f beats after a hit."""
    return float(np.exp(-max(f, 0) * BEAT / k)) if f >= 0 else 0.0


def _plan(G):
    """Where everything is: the owner, the dog's spot, each throw's path and catch, the drag."""
    L = G.length
    TP = float(G.pd[G.seg['Porch Front']].mean())
    P = dict(L=L, TP=TP, HOME=TP - 45.0, throws=[])
    for tb, fl, off, go, at, pick, back in THROWS:
        th = dict(tb=tb, fl=fl, tgt=TP + off, go=go, at=at, pick=pick, back=back, sgn=float(np.sign(off)))
        th['catch'] = _flight(th, TP, min(at, tb + fl))[0]
        th['air'] = at < tb + fl
        P['throws'].append(th)
    P['last'] = dict(tb=FLING, fl=FLY, tgt=-90.0, sgn=-1.0)
    x0, x1 = L + 112.0, TP + 140.0             # the dog's nose, all of him still off the right end .. by the porch
    a = 0.5 + np.arange(16) / 15
    P['heave'] = (x0, (x1 - x0) * a / a.sum())
    return P


def _flight(th, TP, b):
    """A thrown bone: position and height (0..1) at beat b."""
    u = float(np.clip((b - th['tb']) / th['fl'], 0, 1))
    return TP + (th['tgt'] - TP) * (1 - (1 - u) ** 2), 4 * u * (1 - u)


def _heave(P, b):
    x0, a = P['heave']
    x = x0
    for k, ak in enumerate(a):
        x += ak * smoothstep(0, HEAVE, b - DRAG[0] - k)
    return float(x)


def _dog(P, b):
    """The dog at beat b: nose position, facing (+1: nose toward the free right end), squash (body length
    factor), wag rate (Hz), visibility, and what he carries ('toy', 'giant' or None)."""
    TP, HOME, L = P['TP'], P['HOME'], P['L']
    pos, s, k, wag, alpha, carry = HOME, 1.0, 1.0, 2.0, 1.0, None
    if b < APPEAR:
        return pos, s, k, wag, 0.0, None
    if b < POP:
        alpha = smoothstep(APPEAR + 1.0, POP, b)
    for th in P['throws']:
        out = float(np.sign(th['catch'] - HOME))
        if th['go'] <= b < th['at']:
            u = (b - th['go']) / (th['at'] - th['go'])
            return lerp(HOME, th['catch'], smoothstep(0, 1, u)), out, 1.0, 0.0, 1.0, None
        if th['at'] <= b < th['pick']:
            return th['catch'] + 3 * np.sin(2 * np.pi * 4 * b), out, 0.85, 1.0, 1.0, None   # sniff sniff
        if th['pick'] <= b < th['back']:
            u = (b - th['pick']) / (th['back'] - th['pick'])
            trot = 4 * abs(np.sin(np.pi * 2 * b))
            return lerp(th['catch'], HOME, smoothstep(0, 1, u)) + trot * -out, -out, 1.0, 4.0, 1.0, 'toy'
    if ROLL[0] <= b < ROLL[1]:
        c = np.cos(2 * np.pi * (b - ROLL[0]) / (ROLL[1] - ROLL[0]))
        return pos, 1.0 if c >= 0 else -1.0, max(abs(c), 0.12), 3.0, 1.0, None
    if SPIN[0] <= b < SPIN[1]:
        c = np.cos(2 * np.pi * 0.6 * (b - SPIN[0]) ** 2)
        return pos, 1.0 if c >= 0 else -1.0, max(abs(c), 0.12), 0.0, 1.0, None
    if DIZZY[0] <= b < DIZZY[1]:
        return pos + 12 * np.sin(2 * np.pi * 1.5 * (b - DIZZY[0])) * (DIZZY[1] - b), 1.0, 0.9, 0.5, 1.0, None
    if BEG[0] <= b < BEG[1]:
        return keys(b, [(37.4, HOME), (BOOP, TP - 24), (38.6, HOME)]), 1.0, 1.0, 7.0, 1.0, None
    if WIND <= b < GO:
        return pos - 6 * smoothstep(WIND, FLING, b), 1.0, 0.85, 7.0, 1.0, None
    if GO <= b < DRAG[0]:
        u = np.clip((b - GO) / (GONE - GO), 0, 1)
        return lerp(HOME, -160, u ** 1.4), -1.0, 1.0, 0.0, 1.0 if b < GONE else 0.0, None
    if DRAG[0] <= b < DROP:                      # backing in, tugging: nose toward the bone behind him
        return _heave(P, b), 1.0, 1.0, 1.5, 1.0, 'giant'
    x1 = P['heave'][0] + P['heave'][1].sum()
    if DROP <= b < DROP + 1:
        return keys(b, [(DROP + 0.25, x1), (DROP + 1, HOME)]), -1.0, 1.0, 5.0, 1.0, None
    if PARTY[0] <= b < OUT:
        return HOME + 10 * abs(np.sin(np.pi * b)), 1.0 if int(b) % 4 < 2 else -1.0, 1.0, 7.0, 1.0, None
    return pos, s, k, 6.0, alpha, carry


def _toy(P, b):
    """The thrown bone: position, height (0..1) and whether it is drawn."""
    TP, HOME = P['TP'], P['HOME']
    prev = 1.0
    for th in P['throws']:
        if prev <= b < th['tb']:                 # in his hand; wound back for the throw
            back = smoothstep(th['tb'] - 0.6, th['tb'] - 0.15, b) * (1 - smoothstep(th['tb'] - 0.15, th['tb'], b))
            return TP + th['sgn'] * (16 - 34 * back), 0.0, True
        end = min(th['at'], th['tb'] + th['fl'])
        if th['tb'] <= b < end:
            x, h = _flight(th, TP, b)
            return x, h, True
        if end <= b < th['pick']:              # landed: a couple of bounces
            f = b - end
            return th['tgt'] + th['sgn'] * 14 * abs(np.sin(2 * np.pi * 1.5 * f)) * np.exp(-3 * f), 0.0, True
        if th['pick'] <= b < th['back']:
            x, s = _dog(P, b)[:2]
            return x + s * 12, 0.0, True
        if th['back'] <= b < th['back'] + 0.6:
            return HOME + 18, 0.0, True
        prev = th['back'] + 0.6
    lt = P['last']
    if prev <= b < lt['tb']:
        back = smoothstep(WIND, lt['tb'] - 0.15, b) * (1 - smoothstep(lt['tb'] - 0.15, lt['tb'], b))
        return TP + lt['sgn'] * (16 - 40 * back), 0.0, True
    if lt['tb'] <= b < lt['tb'] + lt['fl']:
        u = (b - lt['tb']) / lt['fl']
        return lerp(TP, lt['tgt'], u ** 0.8), 4 * u * (1 - u), True
    return 0.0, 0.0, False


def render(G, seed=37):
    rng = np.random.default_rng(seed)
    P = _plan(G)
    L, TP = P['L'], P['TP']
    pdp = G.pd[G.path]
    w = np.gradient(pdp)
    e0, e1 = pdp - w / 2, pdp + w / 2
    wisp0 = rng.uniform(-700, 700, 6)
    NS = 260
    sp_t = np.sort(rng.uniform(PARTY[0], OUT, NS))
    sp_x = rng.uniform(0, L, NS)
    sp_c = rng.integers(0, len(SPARKS), NS)
    stars = rng.uniform(0, 2 * np.pi, 3)

    def cover(spans):
        if not spans:
            return np.zeros(G.N)
        sp = np.array(spans)
        a = np.minimum(sp[:, 0], sp[:, 1])[:, None]
        z = np.maximum(sp[:, 0], sp[:, 1])[:, None]
        ov = np.clip(np.minimum(z, e1) - np.maximum(a, e0), 0, None) / w
        return np.clip(sp[:, 2] @ ov, 0, 1)

    def put(spans, parts, origin, s, I, scale=1.0):
        for a, z, wt in parts:
            spans.append((origin + s * a * scale, origin + s * z * scale, I * wt))

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        b = t / BEAT
        ghost, nose, bone, man, gold = [], [], [], [], []
        fade = 1 - smoothstep(OUT, OUT + 1.2, b)

        # the owner over the porch: a pale figure; an arm out for each throw; he looks about while waiting
        Im = smoothstep(0.5, 2.0, b) * fade
        lean = keys(b, [(LOOKS[0] - 0.3, 0), (LOOKS[0], -9), (LOOKS[1] - 0.3, -9), (LOOKS[1], 9), (DRAG[0] + 2, 9),
                        (DRAG[0] + 3, 0)])
        jump = 1 + 0.6 * _hit(b - DROP - 0.25, 0.25)
        if PARTY[0] <= b < OUT:
            jump += 0.25 * _hit(b % 1)
        c = TP + lean
        put(man, [(-7, 7, 1.0), (-17, -9, 0.45), (9, 17, 0.45)], c, 1.0, Im * jump)
        for tb, sg in [(th['tb'], th['sgn']) for th in P['throws']] + [(FLING, -1.0)]:
            arm = keys(b, [(tb - 0.5, 0), (tb, 1), (tb + 0.5, 0)])
            if arm > 0:
                put(man, [(9, 9 + 30 * arm, 0.6)], c, sg, Im)

        # the toy bone
        x, h, vis = _toy(P, b)
        if vis:
            put(bone, TOY, x, 1.0, (0.85 + 0.15 * h) * fade, 1 + 0.6 * h)

        # the dog
        pos, s, k, wag, alpha, carry = _dog(P, b)
        if b >= APPEAR and alpha < 1 and b < POP:     # the wisps gathering into him
            u = smoothstep(APPEAR, POP - 0.5, b)
            for x0 in wisp0:
                ghost.append((pos + x0 * (1 - u) - 10, pos + x0 * (1 - u) + 10, 0.5 * (1 - alpha)))
        if alpha > 0:
            Id = alpha * fade
            bark = max(_hit(b - wb, 0.15) for wb in WOOFS)
            T = 26 + 14 * (0.5 + 0.5 * np.sin(2 * np.pi * wag * t))
            put(ghost, [(6, 28, 0.85), (28, 32, 0.45), (32, 72, 0.6)], pos, -s, Id, k)
            put(ghost, [(72, 72 + T / 3, 0.45), (72 + T / 3, 72 + 2 * T / 3, 0.3), (72 + 2 * T / 3, 72 + T, 0.15)],
                pos, -s, Id, k)
            Inose = smoothstep(POP - 0.3, POP, b) * (0.85 + 0.6 * bark)
            nose.append((pos - 6, pos + 6 + 6 * bark, Inose * fade))
            v = (pos - _dog(P, b - DT / BEAT)[0]) / DT
            if abs(v) > 250:                      # a streak behind him when he runs
                tl = min(abs(v) * 0.06, 110)
                base = pos - np.sign(v) * 72 * k
                for q, kk in enumerate((0.35, 0.2, 0.08)):
                    ghost.append((base - np.sign(v) * tl * q / 3, base - np.sign(v) * tl * (q + 1) / 3, kk * Id))
            if carry == 'giant':                  # the giant bone, front knob in his mouth
                put(bone, GIANT, pos + 8, 1.0, 0.85 * fade)
            if DIZZY[0] <= b < DIZZY[1] + 0.5:     # stars round his head
                for ph in stars:
                    a = pos + 26 * np.sin(2 * np.pi * 1.2 * b + ph)
                    gold.append((a - 4, a + 4, 0.8 * (1 - smoothstep(DIZZY[1], DIZZY[1] + 0.5, b))))
        if DROP <= b < OUT + 2:                   # the giant bone where he dropped it, bouncing once
            x1 = P['heave'][0] + P['heave'][1].sum()
            f = b - DROP
            bounce = -22 * abs(np.sin(2 * np.pi * 1.2 * f)) * np.exp(-2.5 * f)
            glow = 0.85 + (0.3 * _hit(b % 1) if PARTY[0] <= b else 0) + 0.4 * _hit(f, 0.3)
            put(bone, GIANT, x1 + 8 - bounce, 1.0, glow * fade)

        Ig, In, Ib, Im_, Iy = cover(ghost), cover(nose), cover(bone), cover(man), cover(gold)
        sky = 0.14 * smoothstep(0, 1.5, b) * fade
        buf = light(NIGHT, sky * (1 - np.clip(Ig + Ib + Im_, 0, 1)))
        buf += light(GHOST, Ig) + light(NOSE, In) + light(BONE, Ib) + light(MAN, Im_) + light(GOLD, Iy)

        # the party: sparkles all along the roof, a gold wash on the ta, a ring out from the owner on the chord
        if b >= PARTY[0]:
            live = (sp_t <= b) & (b < sp_t + 1.2)
            for x0, c0, t0 in zip(sp_x[live], sp_c[live], sp_t[live]):
                buf += light(SPARKS[c0], 0.7 * fade * (1 - (b - t0) / 1.2) * np.exp(-((pdp - x0) / 9) ** 2))
            buf += light(GOLD, 0.6 * _hit(b - TA, 0.3) * np.ones(G.N))
            if b >= FINAL:
                r = np.abs(pdp - TP)
                ring = np.exp(-((r - 900 * (b - FINAL) * BEAT) / 60) ** 2) * _hit(b - FINAL, 1.2)
                buf += light(GOLD, 0.8 * ring) + light(SPARKS[1], 0.3 * fade * np.ones(G.N) *
                                                      smoothstep(FINAL, FINAL + 0.5, b))
        out[fi][G.path] = np.clip(buf, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# Ragtime in G at the lights' 96 BPM: upright piano stride (bass on one and three, chords on two and four),
# xylophone and clarinet on the tune. TUNE is the A strain, eight bars on the throws and again for the
# party; the B strain, in C, is the drag, a tuba grunt on every heave. Every throw is a slide whistle that
# rises and falls with the bone's height and follows it across the house; his paws scrabble on wood blocks
# as he runs, panned with him; every woof is a muted-horn bark; the tricks get a whistle, a whoosh and
# stars. The big throw stops the band dead, there's a crash off to the right, and the drag brings it back.

TUNE = [                                     # (beat, note, beats): the A strain's hook, four bars
    (0, 'G4', .5), (0.5, 'B4', .5), (1, 'D5', .75), (1.75, 'B4', .25), (2, 'C5', .5), (2.5, 'D5', .5), (3, 'E5', 1),
    (4, 'D5', .5), (4.5, 'B4', .25), (4.75, 'G4', .75), (5.5, 'A4', .5), (6, 'B4', .5), (6.5, 'A4', .5), (7, 'G4', 1),
    (8, 'E5', .5), (8.5, 'D5', .25), (8.75, 'C#5', .25), (9, 'D5', .75), (9.75, 'B4', .25), (10, 'A4', .5),
    (10.5, 'G4', .5), (11, 'E4', 1),
    (12, 'D4', .5), (12.5, 'G4', .5), (13, 'B4', .5), (13.5, 'A4', .5), (14, 'G4', 1.5)]
TUNE_B = [                                   # the drag: the B strain, in C
    (0, 'E5', 1), (1, 'E5', .5), (1.5, 'D5', .5), (2, 'C5', .5), (2.5, 'E5', .5), (3, 'G5', 1),
    (4, 'F5', .5), (4.5, 'E5', .5), (5, 'D5', .5), (5.5, 'C5', .5), (6, 'D5', 1), (7, 'A4', 1),
    (8, 'E5', 1), (9, 'E5', .5), (9.5, 'D5', .5), (10, 'C5', .5), (10.5, 'E5', .5), (11, 'A5', 1),
    (12, 'G5', .5), (12.5, 'E5', .5), (13, 'D5', .5), (13.5, 'B4', .5), (14, 'C5', 2)]
HARM_A = ['G', 'G', 'D7', 'G', 'A7', 'A7', 'D7', 'G']     # a chord every half bar
HARM_B = ['C', 'C', 'Dm', 'G7', 'C', 'A7', 'G7', 'C']
CH = {'G': ('G3', 'B3', 'D4'), 'D7': ('F#3', 'C4', 'D4'), 'A7': ('G3', 'C#4', 'E4'), 'C': ('G3', 'C4', 'E4'),
      'Dm': ('F3', 'A3', 'D4'), 'G7': ('F3', 'B3', 'D4')}
BASS = {'G': ('G2', 'D2'), 'D7': ('D2', 'A1'), 'A7': ('A1', 'E2'), 'C': ('C2', 'G2'), 'Dm': ('D2', 'A1'),
        'G7': ('G1', 'D2')}


def score(M, G):
    from pixelhome.audio import SR, note, slide, whoosh
    n = note
    P = _plan(G)
    L, TP, HOME = P['L'], P['TP'], P['HOME']
    piano = M.sampler('Keys/Upright Nr1/*.wav')
    xylo = M.sampler('Percussion/Xylo/*.wav')
    glock = M.sampler('Percussion/Glock/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/stac/*.wav', tune=-12)
    bsn = M.sampler('Woodwinds/Bassoon/stac/*.wav', tune=-12)
    mute = M.sampler('Brass/F Horn/mute/*.wav', tune=-12)
    tpt = M.sampler('Brass/Trumpet/stac/*.wav', tune=-12)
    tpt_s = M.sampler('Brass/Trumpet/sus/*.wav', tune=-12)
    horn_s = M.sampler('Brass/F Horn/sus/*.wav', tune=-12)
    tuba = M.sampler('Brass/Tuba/stac/*.wav', tune=-12)
    bone_s = M.sampler('Brass/Tenor Trombone/sus/*.wav', tune=-12)
    wood = M.hits('VSCO 1 Percussion/varWood/wood_click*.wav')
    clave = M.hits('Percussion/Claves1_Hit*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    guiro = M.hits('VSCO 1 Percussion/varWood/guiro_short*.wav')
    tamb = M.hits('Percussion/Tamb1-Hit*.wav')
    tri = M.hits('Percussion/Triangle3-Hit_v1*.wav')
    ratchet = M.hits('Percussion/Ratchet1-Crank*.wav')
    crash = M.hits('Percussion/cymbal-crash1_f*.wav')
    crash_s = M.hits('Percussion/cymbal-crashshort*.wav')
    bd = M.hits('Percussion/BDrumNewhit_v[4-7]*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    for name, gain, rev in (('piano', 0.42, 0.15), ('tune', 0.36, 0.2), ('bass', 0.45, 0.08), ('perc', 0.5, 0.12),
                            ('dog', 0.42, 0.15), ('fx', 0.2, 0.2), ('brass', 0.3, 0.2), ('drums', 0.42, 0.15)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, from the street
        x = np.interp(np.clip(d, 0, L), ds, xs)
        p = 0.85 * (2 * (x - x0) / (x1 - x0) - 1)
        return float(np.clip(p + 0.15 * np.sign(d - L) * (d > L) - 0.15 * (d < 0), -1, 1))

    def T(b):
        return b * BEAT

    def mono(sig, pans):                    # a mono signal panned sample by sample
        a = (np.clip(pans, -1, 1) + 1) * np.pi / 4
        return np.vstack([sig * np.cos(a), sig * np.sin(a)]) * np.sqrt(2)

    def stride(b0, b1, harm, vel=92, rest=()):
        """Stride piano: bass on 1 and 3, chord on 2 and 4; one chord a half bar."""
        for b in range(int(b0), int(b1)):
            if b in rest:
                continue
            c = harm[((b - int(b0)) // 2) % len(harm)]
            if b % 2 == 0:
                M.add('piano', piano.play(n(BASS[c][(b // 2) % 2]), vel, dur=BEAT * 0.8), T(b), 1.0, -0.15)
                M.add('bass', tuba.play(n(BASS[c][(b // 2) % 2]), vel - 10), T(b), 0.5)
            else:
                for m in CH[c]:
                    M.add('piano', piano.play(n(m), vel - 14, dur=BEAT * 0.45), T(b), 0.55, 0.1)

    def melody(tune, b0, inst, bus='tune', vel=100, gain=1.0, pan=0.0, shift=0):
        for bb, m, ln in tune:
            M.add(bus, inst.play(n(m) + shift, vel, dur=ln * BEAT * 0.9), T(b0 + bb), gain, pan)

    def woof(b, big=1.0):
        p = pan_at(_dog(P, b)[0])
        M.add('dog', mute.play(n('D3'), int(100 * min(big, 1.2)), dur=0.13), T(b), 1.0 * big, p)
        M.add('dog', bsn.play(n('D2'), 90, dur=0.12), T(b) + 0.01, 0.6 * big, p)

    def claws(b0, b1, step=0.25, vel=(55, 85)):
        for b in np.arange(b0, b1, step):
            M.add('perc', wood.play(int(M.rng.integers(*vel)), pitch=float(M.rng.uniform(-2, 4))), T(b), 0.55,
                  pan_at(_dog(P, b)[0]))

    def whistle(th, b0, fl, top=1500.0):   # a slide whistle on the bone's arc, panned along its flight
        nsamp = int(T(fl) * SR)
        u = np.arange(nsamp) / nsamp
        h = 4 * u * (1 - u)
        f = 520 * (top / 520) ** h
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig = 0.32 * (np.sin(ph) + 0.12 * np.sin(2 * ph)) * np.clip(u / 0.03, 0, 1) * np.clip((1 - u) / 0.05, 0, 1)
        bs = b0 + u * fl
        pans = np.interp(bs, bs[::400], [pan_at(_toy(P, q)[0]) for q in bs[::400]])
        M.add('fx', mono(sig, pans), T(b0), 1.0)

    # ---- intro: two bars of vamp; the wisps gather (glock, both sides inward) and his nose lights: woof ----
    stride(0, 8, ['G', 'G', 'D7', 'D7'], 80)
    for j, m in enumerate(('D4', 'G4', 'B4', 'D5', 'G5', 'B4')):
        M.add('tune', glock.play(n(m), 70 + 6 * j), T(APPEAR + 0.5 * j), 0.5, 0.6 * (-1) ** j * (1 - j / 6))
    M.add('tune', xylo.play(n('G5'), 110), T(POP), 0.8, pan_at(HOME))

    # ---- A strain twice, eight bars each, under three throws and three tricks ----
    stride(8, 40, HARM_A)
    melody(TUNE, 8, xylo, vel=104)
    melody(TUNE, 8, piano, vel=86, gain=0.6, shift=12)
    melody(TUNE, 24, clar, vel=104)
    melody(TUNE, 24, xylo, vel=90, gain=0.6)
    for b in range(8, 40, 2):
        M.add('drums', tamb.play(70), T(b + 1), 0.5, 0.2)

    for th in P['throws']:
        M.add('perc', slap.play(70), T(th['tb']), 0.5, pan_at(TP))
        end = min(th['at'], th['tb'] + th['fl'])
        whistle(th, th['tb'], end - th['tb'])
        claws(th['go'], th['at'], 0.25, (70, 110))
        p = pan_at(th['catch'])
        if th['air']:                        # snapped out of the air
            M.add('perc', slap.play(118), T(th['at']), 1.0, p)
            M.add('tune', xylo.play(n('D6'), 115), T(th['at']), 0.6, p)
        else:
            for j, bb in enumerate((0, 0.33, 0.55)):
                M.add('perc', clave.play(110 - 30 * j), T(end + bb), 0.8, p)
            if th['pick'] > th['at']:        # sniff, sniff, chomp
                for bb in (0, 0.25):
                    M.add('perc', guiro.play(70), T(th['at'] + bb), 0.4, p)
                M.add('perc', wood.play(115, pitch=-5), T(th['pick']), 0.8, p)
                M.add('dog', bsn.play(n('G2'), 100, dur=0.1), T(th['pick']), 0.6, p)
        claws(th['pick'], th['back'], 0.5, (45, 70))
        M.add('perc', clave.play(90), T(th['back'] + 0.1), 0.6, pan_at(HOME + 18))
    for wb in WOOFS:
        if wb < DROP:
            woof(wb)

    # tricks: a roll-over whistle and a ta-da; the spin whooshes faster and the whistle climbs, then dizzy stars
    M.add('fx', slide(0.0, T(1), 1300, 500, T(1), 0.3), T(ROLL[0]), 0.8, pan_at(HOME))
    M.add('fx', slide(0.0, T(0.9), 500, 1300, T(1), 0.3), T(ROLL[0] + 1), 0.8, pan_at(HOME))
    for m in ('B4', 'G5'):
        M.add('tune', xylo.play(n(m), 115), T(ROLL[1]), 0.6, pan_at(HOME))
    turns = 0.6 * (np.arange(0, SPIN[1] - SPIN[0], 0.01)) ** 2
    halfs = np.searchsorted(turns, np.arange(0.5, turns[-1], 0.5))
    for j, i in enumerate(halfs):
        M.add('fx', whoosh(0.22, 300 + 60 * j, 1500 + 120 * j, 0.35, seed=j), T(SPIN[0] + 0.01 * i), 0.6,
              pan_at(HOME) + 0.15 * (-1) ** j)
    M.add('fx', slide(0.0, T(3), 400, 1600, T(3), 0.25, shape=1.6), T(SPIN[0]), 0.6, pan_at(HOME))
    for j, m in enumerate(('E6', 'C6', 'A5', 'F5', 'D5', 'B4')):
        M.add('tune', glock.play(n(m), 80), T(DIZZY[0] + 0.25 * j), 0.5, pan_at(HOME) + 0.2 * np.sin(j))
    nw = int(T(1.5) * SR)
    tw = np.arange(nw) / SR
    wob = 0.25 * np.sin(2 * np.pi * (700 + 120 * np.sin(2 * np.pi * 3 * tw)) * tw) * np.exp(-tw / 0.7)
    M.add('fx', np.vstack([wob, wob]), T(DIZZY[0]), 0.7, pan_at(HOME))
    for b in np.arange(BEG[0], BEG[1], 0.5):  # the wag
        M.add('drums', tamb.play(80), T(b), 0.6, pan_at(HOME) - 0.1)
    M.add('perc', tri.play(110), T(BOOP), 0.9, pan_at(TP))
    M.add('tune', glock.play(n('G5'), 100), T(BOOP), 0.6, pan_at(TP))

    # ---- the big throw: ratchet wind-up, a long whistle off the end, the band stops dead ----
    M.add('perc', ratchet.play(100, dur=T(1)), T(WIND), 0.8, pan_at(TP))
    whistle(P['last'], FLING, FLY, 2000)
    claws(GO, GONE, 0.25, (75, 115))
    M.add('fx', whoosh(T(1), 400, 3500, 0.5, seed=9), T(GONE - 1), 0.8, -0.9)
    for m in ('G3', 'D4', 'G4'):
        M.add('brass', tpt.play(n(m), 115, dur=0.2), T(GO), 0.6)
    M.add('drums', crash_s.play(100), T(GO), 0.6)
    # waiting: a clock ticks, he looks after them (huh?), a crash round the back, he looks the other way
    for b in np.arange(GONE + 0.5, DRAG[0], 1.0):
        M.add('perc', clave.play(55), T(b), 0.4)
    for b, m, p in ((LOOKS[0], 'B4', -0.4), (LOOKS[1], 'B4', 0.4)):
        M.add('tune', xylo.play(n(m), 90), T(b), 0.6, p)
        M.add('tune', xylo.play(n('D5'), 90), T(b) + 0.12, 0.6, p)
    M.add('drums', crash.play(120), T(CRASH), 0.6, -1.0)
    M.add('drums', bd.play(110), T(CRASH), 0.5, -1.0)
    for j in range(5):
        M.add('perc', wood.play(110 - 15 * j, pitch=-3 - j), T(CRASH) + 0.09 * j, 0.6, -1.0)
    M.add('perc', ratchet.play(80, dur=0.4), T(CRASH + 0.4), 0.4, -1.0)

    # ---- the drag: the B strain, a heave a beat (tuba grunt, the giant bone scraping where it is) ----
    stride(DRAG[0], DROP, HARM_B, 88, rest=())
    melody(TUNE_B, DRAG[0], bone_s, 'brass', 92, 0.7, -0.1, shift=-12)
    melody([x for x in TUNE_B if x[0] >= 8], DRAG[0], clar, 'tune', 100, 0.8)
    for k in range(16):
        b = DRAG[0] + k
        xd = _heave(P, b + HEAVE)
        M.add('bass', tuba.play(n('C2') if k % 2 == 0 else n('G1'), 100 + k), T(b), 0.7, pan_at(xd))
        M.add('perc', guiro.play(85), T(b), 0.6, pan_at(xd + 260))
        if k % 4 == 3:
            M.add('dog', bsn.play(n('G2'), 95, dur=0.25), T(b + 0.5), 0.5, pan_at(xd))   # a grunt

    # ---- the drop, three barks, then the A strain for the party and a big finish ----
    xb = P['heave'][0] + P['heave'][1].sum() + 268
    M.add('drums', bd.play(127), T(DROP), 1.2, pan_at(xb))
    M.add('drums', timp.play(127, pitch=-3), T(DROP), 1.0, pan_at(xb))
    M.add('drums', crash.play(110), T(DROP), 0.6, pan_at(xb))
    M.add('bass', tuba.play(n('C1'), 125), T(DROP), 1.0, pan_at(xb))
    for j, bb in enumerate((0.42, 0.83)):
        M.add('perc', clave.play(100 - 25 * j, pitch=-4), T(DROP + bb), 0.8, pan_at(xb))
    M.add('fx', slide(0.0, 0.25, 900, 400, 0.3, 0.3), T(DROP + 0.25), 0.7, pan_at(TP))       # the owner jumps
    for j, (wb, big) in enumerate(zip(WOOFS[-3:], (0.9, 1.0, 1.25))):
        woof(wb, big)
        M.add('tune', xylo.play(n(('G4', 'B4', 'D5')[j]), 110), T(wb), 0.6, pan_at(HOME))
    stride(PARTY[0], TA, HARM_A, 100)
    melody(TUNE[:14], PARTY[0], xylo, vel=112)
    melody(TUNE[:14], PARTY[0], clar, vel=108, gain=0.9, shift=0)
    melody(TUNE[:14], PARTY[0], tpt, 'brass', 100, 0.5, 0.2)
    for b in range(int(PARTY[0]), int(TA)):
        M.add('drums', tamb.play(90 if b % 2 else 70), T(b), 0.6, 0.2)
        if b % 2 == 0:
            M.add('drums', bd.play(95), T(b), 0.6)
    rng = np.random.default_rng(37)          # the same sparkles render() lights
    rng.uniform(-700, 700, 6)
    sp_t = np.sort(rng.uniform(PARTY[0], OUT, 260))
    sp_x = rng.uniform(0, L, 260)
    for j in range(0, 260, 9):
        M.add('tune', glock.play(n(('G5', 'B5', 'D6', 'E5')[j % 4]), 60), T(sp_t[j]), 0.3, pan_at(sp_x[j]))
    # ta! ... and the last chord
    for m in CH['D7']:
        M.add('brass', tpt.play(n(m) + 12, 118, dur=0.25), T(TA), 0.6)
    M.add('drums', crash_s.play(115), T(TA), 0.8)
    M.add('drums', bd.play(120), T(TA), 0.9)
    M.add('bass', tuba.play(n('D2'), 120), T(TA), 0.9)
    for bb, m in ((TA + 1, 'A4'), (TA + 1.5, 'B4'), (TA + 1.75, 'C#5')):
        M.add('tune', xylo.play(n(m), 110), T(bb), 0.7)
    dur = T(OUT - FINAL) + 0.6
    for m in ('G3', 'B3', 'D4', 'G4'):
        M.add('brass', horn_s.play(n(m), 115, dur=dur), T(FINAL), 0.55)
        M.add('piano', piano.play(n(m), 115, dur=dur), T(FINAL), 0.5)
    for m in ('B4', 'D5'):
        M.add('brass', tpt_s.play(n(m), 110, dur=dur), T(FINAL), 0.45)
    M.add('bass', tuba.play(n('G1'), 125), T(FINAL), 1.0)
    M.add('drums', crash.play(120), T(FINAL), 0.9)
    M.add('drums', timp.play(125), T(FINAL), 0.9)
    M.add('fx', slide(0.0, T(2), 500, 1800, T(2.2), 0.3), T(FINAL), 0.7)
    for j in range(16):                      # a xylophone roll under the chord
        M.add('tune', xylo.play(n(('G5', 'D5')[j % 2]), 75 + 2 * j), T(FINAL) + 0.07 * j, 0.4)
    M.add('drums', bd.play(127), T(OUT), 1.0)
    M.add('bass', tuba.play(n('G1'), 127, dur=0.3), T(OUT), 1.0)
    for m in ('G3', 'D4', 'G4'):
        M.add('brass', tpt.play(n(m), 122, dur=0.25), T(OUT), 0.7)
    M.add('drums', crash_s.play(120), T(OUT), 0.9)
