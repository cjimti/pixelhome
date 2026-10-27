"""Is Anyone There?: a seance around the porch table. A struck match lights ten candles around the
porch notch (the table), outward from the front door. The sitters ask four questions, each one a
music-box phrase whose syllables roll out of the porch down both wings as warm ripples; the house
answers with knocks, lit where they land: one for yes from the far back end of Side, two for no
from the free end of Right, one right at the front door, among the candles. Asked if it wants them
to leave, it says no from both ends at once and then knocks its way in along both wings to the
table. Cold drafts run down the roofline from the free ends and every candle leans the way the
wind goes; two drafts meet at the table and the flames shrink blue and nearly die. A planchette
appears at the door and glides all over the house, stopping at six letters (each one stays lit);
then the table levitates: the candles slide back up the porch rails, the light of the wings is
drawn in, it all shakes harder and harder until the spirit slams the door. One flash, a shockwave
out of the door, every candle blown out in a puff of smoke. Darkness. Then, at the very back of
the house where the first knock came from, one candle relights, cold blue, and knocks once: yes.

Everything is in path distance (G.pd), so knocks, ripples, drafts and the planchette move evenly
across runs with different pixel spacing. The show runs on an internal 80 BPM waltz (3/4); all the
cue times are beats so the score below takes its hits from the same constants."""
import numpy as np
from pixelhome.fx import DT, hexc, light, smoothstep, lerp, Flicker, nframes

CODE = 'HW07'
TITLE = 'Is Anyone There?'
KIND = 'show'
DESCRIPTION = ('A seance at the porch table: the house answers questions with knocks where they land, '
               'blows cold drafts through the candles, spells with a planchette and lifts the table, '
               'until the spirit slams the door. One candle comes back on its own.')

BEAT = 0.75                                  # 80 BPM, 3/4


def B(k):
    return k * BEAT


D = B(110)                                   # 82.5 s

# ---- the table: porch notch (Porch Left 896-1309, Porch Front 1314-1658, Porch Right 1662-2030) ----
DOOR = 1486.0                                # the middle of Porch Front
PL_BACK, PR_BACK = 1309.0, 1662.0            # the two back corners of the porch
CANDLES = np.array([1000.0, 1110.0, 1220.0, 1360.0, 1440.0, 1530.0, 1610.0, 1750.0, 1860.0, 1960.0])
LIGHT_ORDER = [4, 5, 3, 6, 2, 7, 1, 8, 0, 9]  # outward from the door, alternating sides
T_MATCH = B(2)
T_LIT = {k: B(3 + i) for i, k in enumerate(LIGHT_ORDER)}
INTRO = ['A4', 'D5', 'F5', 'E5', 'D5', 'Bb4', 'A4', 'C#5', 'E5', 'D5']   # one note per candle, beats 3..12

BACK_END, RIGHT_END = 8.0, 2504.0            # the free ends
# questions: syllables (beat, note); the ripple of each syllable leaves the porch on its beat
QUESTIONS = [
    [(15, 'A4'), (15.5, 'A4'), (16, 'C5'), (16.5, 'D5'), (17, 'E5')],                       # is anyone there?
    [(24, 'A4'), (24.5, 'A4'), (25, 'C5'), (25.5, 'C5'), (26, 'D5'), (26.5, 'F5'), (27, 'E5')],  # are you a friendly spirit?
    [(33, 'A4'), (33.5, 'C5'), (34, 'D5'), (34.5, 'E5'), (35, 'G5')],                       # are you here with us?
    [(42, 'E5'), (42.5, 'D5'), (43, 'C5'), (43.5, 'A4'), (44, 'Bb4'), (44.5, 'A4')],          # do you want us to leave?
]
SYLLABLES = [s for q in QUESTIONS for s in q]
# knocks: (beat, path distance, strength)
ANSWERS = [(20, BACK_END, 0.75),                                   # yes
           (30, RIGHT_END, 0.8), (30.5, RIGHT_END, 0.8),           # no
           (38, DOOR, 1.0),                                        # yes, here, at the door
           (47, BACK_END, 0.85), (47.5, RIGHT_END, 0.85)]          # no, from both ends
RUN = [(48 + 0.5 * i, float(np.interp(i // 2, [0, 5], [60, 905])) if i % 2 == 0 else
        float(np.interp(i // 2, [0, 5], [2460, 2025])), 0.55 + 0.04 * i) for i in range(12)]
KNOCKS = ANSWERS + RUN
# drafts: (beat, start distance, direction, strength); the last two meet at the table
SPEED_DRAFT, LEN_DRAFT = 700.0, 320.0
GUSTS = [(54, 0.0, 1, 0.7), (57, 0.0, 1, 0.85), (60, 2512.0, -1, 0.9), (63, 0.0, 1, 1.0), (63, 2512.0, -1, 1.0)]
# the planchette: appears at the door, glides to six letters, returns to the door
T_PLAN, GLIDE = 66, 1.5
STOPS = [(69, 2330.0, 'E5'), (71, 1150.0, 'D5'), (73, 300.0, 'C5'), (75, 1800.0, 'A4'), (77, 700.0, 'F4'),
         (79, 2470.0, 'D4'), (81, DOOR, None)]
T_LIFT, T_SLAM = 81, 93                      # the table rises, then the door slams
WAVE = 1400.0                                # slam shockwave speed
T_RELIGHT, T_LAST = 101, 104                 # the blue candle, its knock
BLUE_AT = 10.0

FLAME = hexc('#ff8418')
TIP = hexc('#ffc860')
HALO = hexc('#ff6010')
COLD = hexc('#4f86ff')
DRAFT = hexc('#3c74ff')
KNOCK = hexc('#e4ecff')
VOICE = hexc('#ffa040')
PLAN = hexc('#e6eeff')
LETTER = hexc('#70ffa8')
SMOKE = hexc('#80889c')
BASE = hexc('#3a1666')
TABLE = hexc('#ff7a30')
PULL = hexc('#7a6cff')


def blowout(k):
    """When the slam's shockwave puts candle k out."""
    return B(T_SLAM) + abs(CANDLES[k] - DOOR) / WAVE + 0.02


def plan_pos(t):
    """Planchette position and speed (units/s) at time t."""
    prev = DOOR
    for b, d, _ in STOPS:
        if t < B(b - GLIDE):
            return prev, 0.0
        if t < B(b):
            u = (t - B(b - GLIDE)) / B(GLIDE)
            e = u * u * (3 - 2 * u)
            return lerp(prev, d, e), (d - prev) * 6 * u * (1 - u) / B(GLIDE)
        prev = d
    return prev, 0.0


def render(G, seed=7):
    rng = np.random.default_rng(seed)
    pdp = G.pd[G.path]
    L = G.length
    NC = len(CANDLES)
    porch = ((pdp > 893) & (pdp < 2033)).astype(float)
    wing = 1 - porch
    fl_slow = Flicker(rng, NC, 1.2, 4.0)
    fl_fast = Flicker(rng, NC, 6.0, 13.0)
    shake_f = rng.uniform(7.5, 11.5, NC)
    shake_p = rng.uniform(0, 2 * np.pi, NC)
    sway_p = rng.uniform(0, 2 * np.pi, NC)
    tex_p = rng.uniform(0, 2 * np.pi, 3)
    pull_off = rng.uniform(0, 1, 6)
    t_out = np.array([blowout(k) for k in range(NC)])
    t_lit = np.array([T_LIT[k] for k in range(NC)])
    ts_slam = B(T_SLAM)

    F = nframes(D)
    out = np.zeros((F, G.N, 3))
    for fi in range(F):
        t = fi * DT
        buf = np.zeros((G.N, 3))
        fade = 1 - smoothstep(D - 1.8, D - 0.1, t)

        # ---- the room: a faint violet floor until the slam ----
        base = 0.1 * smoothstep(0.2, 1.5, t) * (1 - smoothstep(ts_slam, ts_slam + 0.6, t))
        buf += light(BASE, base * np.ones(G.N))

        # ---- candles ----
        lev = np.where(t >= t_lit, smoothstep(t_lit, t_lit + 0.3, t) + 0.7 * np.exp(-np.maximum(t - t_lit, 0) / 0.18), 0.0)
        lev = lev * (1 + 0.1 * fl_slow(t))
        lev = np.where(t >= t_out, lev * np.exp(-np.maximum(t - t_out, 0) / 0.05), lev)
        lean = 0.12 * np.sin(2 * np.pi * 0.23 * t + sway_p)
        cold = np.zeros(NC)
        push = np.zeros(NC)
        draft_px = np.zeros(G.N)
        for b, s0, sg, st in GUSTS:
            tg = B(b)
            if t < tg:
                continue
            front = SPEED_DRAFT * (t - tg)
            if front > L + 3000:
                continue
            u = sg * (pdp - s0)
            inb = smoothstep(front - LEN_DRAFT, front - 0.55 * LEN_DRAFT, u) * (1 - smoothstep(front - 30, front + 10, u))
            tex = 0.6 + 0.4 * np.sin(u / 23 - 9 * t + tex_p[0]) * np.sin(u / 57 + 4 * t + tex_p[1])
            draft_px += st * 0.5 * inb * tex
            a = (front - sg * (CANDLES - s0)) / SPEED_DRAFT          # seconds since the draft reached each candle
            pres = np.where(a > 0, smoothstep(0, 0.25, a) * np.exp(-np.maximum(a - 0.5, 0) / 0.9), 0.0)
            lean = lean + sg * st * pres
            push = push + st * pres
            cold = np.maximum(cold, st * pres)
        clash = np.clip(push - np.abs(lean), 0, 1.2)               # opposite drafts meeting: the flames shrink
        lean = np.clip(lean, -1, 1)
        lev = lev * (1 - 0.72 * np.clip(clash, 0, 1)) * (1 + 0.3 * np.clip(push, 0, 1) * fl_fast(t))
        # knocks make the flames jump
        for b, d, st in KNOCKS + [(T_LAST, BLUE_AT, 0.5)]:
            tk = B(b) + np.abs(CANDLES - d) / 650.0
            dip = np.where(t >= tk, np.exp(-np.maximum(t - tk, 0) / 0.18), 0.0)
            lev = lev * (1 - 0.45 * st * dip)
            lean = lean + 0.5 * st * dip * np.sign(CANDLES - d + 1e-3)
        # levitation: slide back up the rails, shake harder and harder; snaps down at the slam
        ul = smoothstep(B(T_LIFT), ts_slam - 0.3, t) if t < ts_slam else 0.0
        cpos = CANDLES.copy()
        if ul > 0:
            cpos = np.where(CANDLES < PL_BACK, CANDLES + ul * 0.65 * (PL_BACK - CANDLES), cpos)
            cpos = np.where(CANDLES > PR_BACK, CANDLES - ul * 0.65 * (CANDLES - PR_BACK), cpos)
            cpos = cpos + (1.5 + 13 * ul ** 2) * np.sin(2 * np.pi * shake_f * t + shake_p)
            cold = np.maximum(cold, 0.25 * ul)
            lev = lev * (1 + 0.25 * ul)
        cold = np.clip(cold, 0, 1)
        core_c = FLAME[None] * (1 - cold[:, None]) + COLD[None] * cold[:, None]
        tip_c = TIP[None] * (1 - cold[:, None]) + COLD[None] * cold[:, None]
        dd = pdp[None, :] - cpos[:, None]
        core = (0.85 * lev)[:, None] * np.exp(-((dd - 5 * lean[:, None]) / 5.5) ** 2)
        tip = (0.6 * lev)[:, None] * np.exp(-((dd - 14 * lean[:, None]) / (4 + 4 * np.abs(lean[:, None]))) ** 2)
        halo = np.clip(((0.2 * np.minimum(lev, 1))[:, None] * np.exp(-(dd / 65) ** 2)).sum(0), 0, 0.28)
        buf += np.einsum('kn,kc->nc', (np.clip(core, 0, 1.2) ** 2.2), core_c)
        buf += np.einsum('kn,kc->nc', (np.clip(tip, 0, 1.2) ** 2.2), tip_c)
        buf += light(HALO, halo * (1 - 0.6 * np.max(cold)))

        # ---- the match ----
        if T_MATCH - 0.05 <= t < t_lit.max() + 0.4:
            if t < T_LIT[LIGHT_ORDER[0]] - 0.45:
                mp = DOOR
            else:
                mp = CANDLES[LIGHT_ORDER[-1]]
                for i, k in enumerate(LIGHT_ORDER):
                    t1 = T_LIT[k]
                    p0 = DOOR if i == 0 else CANDLES[LIGHT_ORDER[i - 1]]
                    if t < t1:
                        mp = lerp(p0, CANDLES[k], smoothstep(t1 - 0.45, t1, t))
                        break
                    if i + 1 < len(LIGHT_ORDER) and t < T_LIT[LIGHT_ORDER[i + 1]] - 0.45:
                        mp = CANDLES[k]
                        break
            mi = 0.75 + 0.9 * np.exp(-max(t - T_MATCH, 0) / 0.12) + 0.1 * np.sin(37 * t)
            mi *= 1 - smoothstep(t_lit.max(), t_lit.max() + 0.4, t)
            buf += light(TIP, mi * np.exp(-((pdp - mp) / 6) ** 2))

        # ---- the sitters' voices: warm ripples out of the porch down both wings ----
        vo = np.zeros(G.N)
        for b, _ in SYLLABLES:
            ts = B(b)
            if not (ts <= t < ts + 2.2):
                continue
            r = 640 * (t - ts)
            k = np.exp(-(t - ts) * 1.3) * smoothstep(0, 0.06, t - ts)
            vo += 0.5 * k * np.exp(-(((896 - pdp) - r) / 70) ** 2) * (pdp < 896)
            vo += 0.5 * k * np.exp(-(((pdp - 2030) - r) / 70) ** 2) * (pdp > 2030)
            vo += 0.12 * k * porch
        buf += light(VOICE, np.clip(vo, 0, 0.5))

        # ---- knocks: a burst where it lands and a ring running out from it ----
        kn = np.zeros(G.N)
        for b, d, st in ANSWERS + [(T_LAST, BLUE_AT, 0.5)]:     # something gathers where it is about to knock
            tk = B(b)
            if tk - 1.8 <= t < tk:
                g = smoothstep(tk - 1.8, tk - 0.05, t) ** 2
                buf += light(COLD, 0.3 * st * g * np.exp(-((pdp - d) / (110 - 60 * g)) ** 2))
        for b, d, st in KNOCKS + [(T_LAST, BLUE_AT, 0.5)]:
            tk = B(b)
            if not (tk <= t < tk + 1.8):
                continue
            a = t - tk
            kn += st * 0.95 * np.exp(-((pdp - d) / 40) ** 2) * np.exp(-a / 0.2)
            r = 650 * a
            ring = np.exp(-((np.abs(pdp - d) - r) / 34) ** 2) * np.exp(-a / 0.8)
            kn += st * 0.8 * ring
        buf += light(KNOCK, np.clip(kn, 0, 1))

        # ---- drafts ----
        buf += light(DRAFT, np.clip(draft_px, 0, 0.6))

        # ---- the planchette and its letters ----
        tp = B(T_PLAN)
        if tp <= t < ts_slam:
            pi = smoothstep(tp, tp + 1.2, t)
            for j, lagt in enumerate((0.0, 0.035, 0.07, 0.105)):
                p, v = plan_pos(t - lagt)
                p += (1.5 + 13 * ul ** 2) * np.sin(2 * np.pi * 8.8 * t + 0.4) if ul > 0 else 0.0
                if j and abs(v) < 250:
                    continue
                w = 1.0 if j == 0 else 0.45 / j
                ring = np.exp(-((pdp - p) / 20) ** 2) - 0.85 * np.exp(-((pdp - p) / 6.5) ** 2)
                glow = 0.22 * np.exp(-((pdp - p) / 45) ** 2)
                buf += light(PLAN, pi * w * np.clip(0.75 * ring + glow, 0, 1) * (1 + 0.1 * np.sin(3 * t)))
            for b, d, _ in STOPS[:-1]:
                if t >= B(b):
                    a = t - B(b)
                    li = 0.3 + 0.7 * np.exp(-a / 0.3)
                    if t >= B(T_LIFT):
                        li *= 1 - 0.5 * smoothstep(B(T_LIFT), ts_slam, t)
                    buf += light(LETTER, li * np.exp(-((pdp - d) / 6) ** 2))

        # ---- levitation: the table glows and shakes, the wings' light is drawn into it ----
        if ul > 0:
            sh = 1 + 0.35 * ul * np.sin(2 * np.pi * 9.3 * t) * np.sin(2 * np.pi * 0.7 * t + 1)
            buf += light(TABLE, (0.08 + 0.32 * ul ** 1.5) * sh * porch)
            pl = np.zeros(G.N)
            for j in range(6):                 # dashes sliding in from both free ends, faster and faster
                ph = (pull_off[j] + (t - B(T_LIFT)) * (0.35 + 0.5 * ul)) % 1
                x = ph * 893
                pl += np.exp(-((pdp - x) / 30) ** 2) + np.exp(-((pdp - (L - ph * (L - 2033))) / 30) ** 2)
            buf += light(PULL, 0.42 * ul * np.clip(pl, 0, 1) * wing)

        # ---- the slam: one flash, a burst at the door, the shockwave, smoke ----
        if ts_slam <= t < ts_slam + 4.5:
            a = t - ts_slam
            buf += light(KNOCK, 0.8 * np.exp(-a / 0.07) * np.ones(G.N))
            buf += light(KNOCK, np.exp(-((pdp - DOOR) / 50) ** 2) * np.exp(-a / 0.25))
            r = WAVE * a
            buf += light(KNOCK, 0.85 * np.exp(-((np.abs(pdp - DOOR) - r) / 40) ** 2) * np.exp(-a / 0.9))
            sm = np.zeros(G.N)
            for k in range(NC):
                b2 = t - t_out[k]
                if b2 <= 0:
                    continue
                for sgn in (-1, 1):
                    cpk = CANDLES[k] + sgn * 26 * b2
                    sm += 0.3 * np.exp(-b2 / 1.1) * smoothstep(0, 0.15, b2) * np.exp(-((pdp - cpk) / (8 + 14 * b2)) ** 2)
            buf += light(SMOKE, np.clip(sm, 0, 0.4))

        # ---- the blue candle at the very back of the house ----
        tr = B(T_RELIGHT)
        if t >= tr:
            a = t - tr
            lv = smoothstep(0, 0.5, a) * (1 + 0.6 * np.exp(-a / 0.3)) * (1 + 0.08 * np.sin(2 * np.pi * 2.3 * t)
                                                                           + 0.05 * np.sin(2 * np.pi * 5.1 * t))
            tk = B(T_LAST)
            if t >= tk:
                lv *= 1 - 0.4 * np.exp(-(t - tk) / 0.2)
            buf += light(COLD, 0.85 * lv * np.exp(-((pdp - BLUE_AT) / 6) ** 2))
            buf += light(hexc('#a8ccff'), 0.5 * lv * np.exp(-((pdp - BLUE_AT - 4) / 4) ** 2))
            buf += light(COLD, 0.16 * lv * np.exp(-((pdp - BLUE_AT) / 80) ** 2))

        out[fi][G.path] = np.clip(buf * fade, 0, 1)
    return out


# ---------------------------------------------------------------- music ----------------------------------------------
# A parlour waltz in D minor at the lights' 80 BPM, played on a music box, an upright piano and a glass harmonica
# (sine partials with a slow rubbed attack, synthesized here). The music box asks each question; the waltz falls silent
# before every answer so the knocks (log drum, slit drum and a muted bass drum, panned to where they land) are heard
# alone. The drafts bring a solo violin over a contrabass tremolo and wind; the planchette's letters are the first
# question's notes turned upside down on the music box, with harp glides between them; the levitation climbs in string
# tremolo, timpani and table legs rattling on wood until the slam (gong, bass drum, slapstick, a low piano cluster).

PROG = {1: 'Dm', 2: 'Gm', 3: 'A7', 4: 'Dm', 5: 'Dm', 6: None, 7: 'Dm', 8: 'Gm', 9: 'A7', 10: None, 11: 'Dm',
        12: 'Bb', 13: None, 14: 'Gm', 15: 'Eb', 16: 'A7', 17: 'A7'}
CHORD = {'Dm': (50, 53, 57), 'Gm': (50, 55, 58), 'A7': (49, 55, 57), 'Bb': (50, 53, 58), 'Eb': (51, 55, 58),
         'A': (49, 52, 57), 'D': (50, 54, 57)}
ROOT = {'Dm': 38, 'Gm': 43, 'A7': 33, 'Bb': 34, 'Eb': 39, 'A': 33, 'D': 38}


def score(M, G):
    from pixelhome.audio import SR, note, whoosh
    n = note
    rng = M.rng
    piano = M.sampler('Keys/Upright Nr1/UR1_*_mf_*.wav')          # labelled at pitch
    harp = M.sampler('Strings/Harp/*.wav')
    cbpizz = M.sampler('Strings/Solo Contrabass/Pizz/*.wav', tune=-12)   # these sets are labelled an octave low
    cbtrem = M.sampler('Strings/Solo Contrabass/Trem/*.wav', tune=-12)
    cello = M.sampler('Strings/Cello Section/susvib/*.wav', tune=-12)
    ctrem = M.sampler('Strings/Cello Section/trem/*.wav', tune=-12)
    vtrem = M.sampler('Strings/Viola Section/trem/*.wav', tune=-12)
    violin = M.sampler('Strings/Solo Violin/Arco Vib/*.wav', tune=-12)
    clar = M.sampler('Woodwinds/Clarinet/susLong/*.wav', tune=-12)
    box = M.synth('Plucks/Magic Music Box')
    bed = M.synth('Pads/Still')
    loglo = M.hits('Percussion/LogDrumLo_MedM_v3*.wav')
    loglo_s = M.hits('Percussion/LogDrumLo_MedM_v1*.wav')
    loghi = M.hits('Percussion/LogDrumHi_MedM_v2*.wav')
    slit = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum0_ff_*.wav')
    slit_s = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum1_mp_*.wav')
    slit_p = M.hits('VSCO 1 Percussion/varWood/log_drum/slitdrum2_ppp_*.wav')
    bdm = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_mf*.wav')
    bdm_p = M.hits('VSCO 1 Percussion/drums/bass/bdrum_muted_pp*.wav')
    bd_big = M.hits('VSCO 1 Percussion/drums/bass/bdrum_fff_*.wav')
    gong = M.hits('VSCO 1 Percussion/varMetal/Gong/gong_hit_fff.wav')
    gong_s = M.hits('Percussion/gongHit_p.wav')
    bowcym = M.hits('Percussion/susCymb1-bow-*.wav')
    slap = M.hits('VSCO 1 Percussion/varWood/slapstick[0-9].wav')
    troll = M.hits('Percussion/Timpani/Rolls/*.wav')
    timp = M.hits('Percussion/Timpani/Timpani1_Hit*.wav')
    flex = M.hits('VSCO 1 Percussion/varMetal/various/flexatone_long*.wav')
    chimes = M.hits('VSCO 1 Percussion/varMetal/various/windchimes_slowDesc1.wav')
    tri = M.hits('Percussion/Triangle6-HitM_v1*.wav')
    cabasa = M.hits('VSCO 1 Percussion/varMetal/various/cabasa_roll*.wav')

    for name, gain, rev in (('box', 0.75, 0.3), ('piano', 0.42, 0.22), ('glass', 0.3, 0.4), ('bed', 0.45, 0.3),
                            ('bass', 0.38, 0.12), ('strings', 0.36, 0.3), ('violin', 0.3, 0.32), ('harp', 0.34, 0.35),
                            ('knock', 0.85, 0.2), ('perc', 0.5, 0.22), ('fx', 0.4, 0.3), ('wind', 0.42, 0.25)):
        M.bus(name, gain=gain, reverb=rev)

    order = np.argsort(G.pd)
    xs, ds = G.pos[order, 0], G.pd[order]
    x0, x1 = xs.min(), xs.max()

    def pan_at(d):                          # path distance -> left/right across the facade, as seen from the street
        x = np.interp(d, ds, xs)
        return float(0.85 * (2 * (x - x0) / (x1 - x0) - 1))

    L = G.length

    def bar(k):
        return B(3 * k)

    def one(synth, m, vel, dur, tail=2.5):  # a single synth note, rendered on its own so it can be panned
        return synth.render([(0.0, m, vel, dur)], dur + tail)

    def glass(notes, seconds):
        """Glass harmonica: near-sine partials, a slow rubbed attack and a slow beating."""
        out = np.zeros(int(seconds * SR) + SR)
        for t, m, vel, dur in notes:
            f = 440.0 * 2 ** ((m - 69) / 12)
            ln = int((dur + 1.4) * SR)
            tt = np.arange(ln) / SR
            vib = 1 + 0.0012 * np.sin(2 * np.pi * 4.7 * tt)
            ph = 2 * np.pi * f * np.cumsum(vib) / SR
            s = np.sin(ph) + 0.18 * np.sin(2 * ph + 0.3) + 0.05 * np.sin(3 * ph)
            s *= 1 + 0.12 * np.sin(2 * np.pi * 0.9 * tt)
            env = np.clip(tt / 0.4, 0, 1) ** 2 * np.where(tt < dur, 1.0, np.exp(-(tt - dur) / 0.45))
            a = int(t * SR)
            e = min(len(out), a + ln)
            out[a:e] += (vel / 127) * 0.22 * (s * env)[:e - a]
        return np.vstack([out, out])

    box_c = []                              # music box notes that sit in the middle
    piano_n = []
    glass_n = []
    bed_n = []

    def waltz(k, c, vel=62):                # one bar of oom-pah-pah
        t = bar(k)
        r = ROOT[c]
        piano_n.append((t, r - 12 if r > 40 else r, vel + 6, BEAT * 1.6))
        M.add('bass', cbpizz.play(r - 12 if r > 40 else r, vel + 20), t, 0.9, -0.1)
        for j in (1, 2):
            for m in CHORD[c]:
                piano_n.append((t + B(j), m + 12, vel - 6 * (j == 2), BEAT * 0.7))

    # ---- 0-9 s: the match, ten candles, the parlour tune ----
    M.add('fx', whoosh(0.18, 2500, 6000, 0.5, seed=11), T_MATCH - 0.05, 0.6, pan_at(DOOR))
    M.add('fx', whoosh(0.7, 300, 900, 0.45, seed=12), T_MATCH + 0.05, 0.5, pan_at(DOOR))
    for k in range(1, 5):
        waltz(k, PROG[k], 54 + 3 * k)
    bed_n += [(0.3, n('D3'), 60, 8.5), (0.3, n('A3'), 50, 8.5)]
    for i, k in enumerate(LIGHT_ORDER):
        t, p = T_LIT[k], pan_at(CANDLES[k])
        M.add('box', one(box, n(INTRO[i]), 96, BEAT * (1.8 if i == 9 else 0.9)), t, 1.0, p)
        M.add('fx', whoosh(0.25, 400, 1400, 0.25, seed=20 + i), t - 0.08, 0.35, p)

    # ---- the questions ----
    for qi, q in enumerate(QUESTIONS):
        for j, (b, m) in enumerate(q):
            last = j == len(q) - 1
            M.add('box', one(box, n(m), 92 + 14 * last, BEAT * (1.6 if last else 0.45)), B(b), 1.0, 0.0)
            M.add('box', one(box, n(m) - 12, 60, BEAT * 0.4), B(b), 0.55, 0.0)
    for k in (5, 7, 8, 9, 11, 12, 14, 15):
        waltz(k, PROG[k], 60)
    # the waltz holds its breath before each answer: glass harmonica and the bed only
    glass_n += [(bar(5), n('D4'), 80, 6.2), (bar(5), n('A4'), 70, 6.2),
                (bar(8) + B(1), n('E4'), 76, 6.0), (bar(8) + B(1), n('A4'), 70, 6.0), (bar(8) + B(1), n('C#5'), 60, 6.0),
                (bar(11), n('D4'), 82, 6.4), (bar(11), n('F4'), 72, 6.4), (bar(11), n('Bb4'), 66, 6.4),
                (bar(14), n('Eb4'), 80, 6.5), (bar(14), n('G4'), 70, 6.5), (bar(14), n('Bb4'), 66, 6.5)]
    bed_n += [(bar(5), n('D3'), 55, 6.5), (bar(8), n('A2'), 55, 6.5), (bar(11), n('Bb2'), 55, 6.5),
              (bar(14), n('Eb3'), 52, 4.5)]

    def knock(b, d, st, lo=True):
        t, p = B(b), pan_at(d)
        M.add('knock', (loglo if lo else loghi).play(int(70 + 55 * st)), t, 1.0 * st, p)
        M.add('knock', slit.play(int(60 + 60 * st)), t, 0.55 * st, p)
        M.add('knock', bdm.play(int(60 + 60 * st)), t - 0.08, 0.7 * st, p)   # the sample speaks late

    for b, d, st in ANSWERS:
        knock(b, d, st)
    # after each answer: a reply in the low strings or harp
    M.add('harp', harp.play(n('D3'), 70), B(21), 0.8, pan_at(BACK_END))
    M.add('harp', harp.play(n('A3'), 66), B(21.5), 0.7, pan_at(BACK_END))
    M.add('harp', harp.play(n('D4'), 62), B(22), 0.6, pan_at(BACK_END))
    M.add('strings', cello.play(n('Bb2'), 80, dur=2.0), B(31), 0.8, 0.5)
    M.add('strings', cello.play(n('A2'), 76, dur=1.6), B(31) + 2.0, 0.8, 0.5)
    M.add('perc', bowcym.play(80, dur=4.0), B(38) + 0.1, 0.6, 0.0)
    M.add('bass', cbtrem.play(n('D2'), 80, dur=3.0), B(38), 0.9, 0.0)
    M.add('strings', cello.play(n('D3'), 78, dur=2.6), B(38.5), 0.7, -0.2)
    M.add('strings', cello.play(n('F3'), 70, dur=2.6), B(38.5), 0.6, 0.2)

    # ---- the knock run: in along both wings; the pulse under it speeds up ----
    for i, (b, d, st) in enumerate(RUN):
        knock(b, d, st, lo=(i % 2 == 0))
    for i, m in enumerate(('D2', 'Eb2', 'E2', 'F2', 'F#2', 'G2')):
        M.add('bass', cbpizz.play(n(m), 96 + 4 * i), B(48 + i), 1.0)
        M.add('strings', vtrem.play(n(m) + 24, 60 + 6 * i, dur=BEAT * 1.05), B(48 + i), 0.6, -0.3)
        M.add('strings', vtrem.play(n(m) + 27, 60 + 6 * i, dur=BEAT * 1.05), B(48 + i), 0.6, 0.3)
    M.add('perc', troll.play(70, dur=B(6)), B(48), 0.5)
    M.add('perc', timp.play(110, pitch=-1), B(54), 0.8)

    # ---- the drafts: wind running down the roofline, a violin over a contrabass tremolo ----
    for gi, (b, s0, sg, st) in enumerate(GUSTS):
        tg = B(b)
        dur = (L + LEN_DRAFT) / SPEED_DRAFT
        w = whoosh(dur, 180, 900, 0.5 * st, seed=60 + gi)
        sl = int(0.25 * SR)                 # panned in slices to follow the draft along the house
        for a in range(0, w.shape[1], sl):
            front = SPEED_DRAFT * (a / SR) - LEN_DRAFT / 2
            d = np.clip(s0 + sg * front, 0, L)
            M.add('wind', w[:, a:a + sl], tg + a / SR, 1.0, pan_at(d))
        arrive = tg + abs(DOOR - s0) / SPEED_DRAFT
        M.add('perc', bowcym.play(int(60 + 30 * st), dur=3.0), arrive - 0.6, 0.45 * st, pan_at(DOOR))
    M.add('bass', cbtrem.play(n('D2'), 74, dur=B(12)), B(54), 0.9)
    M.add('strings', ctrem.play(n('A2'), 60, dur=B(9)), B(55), 0.6, -0.3)
    vio = [(54, 'D4', 2), (56, 'F4', 1), (57, 'E4', 1.5), (58.5, 'D4', 1.5), (60, 'Bb4', 2), (62, 'A4', 1),
           (63, 'G4', 1), (64, 'F4', 1), (65, 'E4', 2)]
    for b, m, dur in vio:
        M.add('violin', violin.play(n(m), 92, dur=B(dur) + 0.1, release=0.3), B(b), 1.0, 0.15)
    for b, m, dur in ((54, 'A3', 3), (57, 'G3', 3), (60, 'F3', 3), (63, 'C#3', 3)):
        M.add('violin', clar.play(n(m), 82, dur=B(dur), release=0.3), B(b), 0.75, -0.2)
    glass_n += [(B(54), n('D4'), 70, B(5.5)), (B(54), n('F4'), 60, B(5.5)), (B(60), n('D4'), 70, B(5.5)),
                (B(60), n('G4'), 64, B(5.5)), (B(63), n('C#4'), 70, B(3)), (B(63), n('E4'), 64, B(3))]
    M.add('fx', flex.play(70, dur=3.0), B(63) + 1.8, 0.5, pan_at(DOOR))   # the two drafts meet at the table: the flames gutter

    # ---- the planchette: glides (harp) and letters (the first question, upside down) ----
    M.add('fx', chimes.play(70), B(T_PLAN) - 0.2, 0.6, pan_at(DOOR))
    bed_n += [(B(66), n('D3'), 58, B(15)), (B(66), n('A3'), 48, B(15))]
    glass_n += [(B(66), n('A4'), 62, B(6)), (B(72), n('Bb4'), 62, B(6)), (B(78), n('A4'), 62, B(3))]
    prev = DOOR
    for i, (b, d, m) in enumerate(STOPS):
        t0 = B(b - GLIDE)
        steps = 7
        for s in range(steps):              # a quiet harp run that follows the glide
            u = (s + 0.5) / steps
            e = u * u * (3 - 2 * u)
            hm = n('D3') + [0, 3, 5, 7, 10, 12, 15][s if d > prev else steps - 1 - s]
            M.add('harp', harp.play(hm, 54), t0 + u * B(GLIDE) - 0.05, 0.55, pan_at(lerp(prev, d, e)))
        if m is not None:
            p = pan_at(d)
            M.add('box', one(box, n(m), 104, BEAT * 1.2), B(b), 1.0, p)
            M.add('perc', tri.play(60), B(b), 0.35, p)
            M.add('harp', harp.play(n(m) - 12, 70), B(b), 0.6, p)
        prev = d
    for k in range(66, 81, 3):              # a slow heartbeat under it
        M.add('perc', bdm_p.play(80), B(k) - 0.06, 0.8)
        M.add('perc', bdm_p.play(60), B(k) + 0.18, 0.6)

    # ---- the levitation: rising tremolo, timpani, the table legs rattling ----
    for i in range(12):
        t = B(T_LIFT + i)
        m = n('D3') + i
        M.add('strings', vtrem.play(m + 12, 70 + 4 * i, dur=BEAT * 1.05), t, 0.5 + 0.04 * i, -0.3)
        M.add('strings', ctrem.play(m, 70 + 4 * i, dur=BEAT * 1.05), t, 0.5 + 0.04 * i, 0.3)
    M.add('bass', cbtrem.play(n('D2'), 90, dur=B(12)), B(T_LIFT), 0.8)
    M.add('perc', troll.play(90, dur=B(12)), B(T_LIFT), 0.6)
    M.add('perc', troll.play(110, dur=B(6)), B(T_LIFT + 6), 0.6)
    M.add('fx', flex.play(80, dur=4.0), B(T_LIFT + 2), 0.45, pan_at(DOOR))
    M.add('fx', flex.play(95, dur=B(T_SLAM - T_LIFT - 7)), B(T_LIFT + 7), 0.55, pan_at(DOOR))
    M.add('perc', cabasa.play(80, dur=B(T_SLAM - T_LIFT - 8)), B(T_LIFT + 8), 0.35, pan_at(DOOR))
    t = B(T_LIFT) + 0.3
    while t < B(T_SLAM) - 0.15:            # legs knocking on the floor, faster as it shakes harder
        u = (t - B(T_LIFT)) / B(T_SLAM - T_LIFT)
        leg = int(rng.integers(0, 4))
        M.add('knock', slit_p.play(int(60 + 50 * u)), t, 0.25 + 0.4 * u, pan_at(CANDLES[[0, 3, 6, 9][leg]]))
        t += lerp(0.38, 0.07, u ** 0.8) * float(rng.uniform(0.85, 1.15))
    glass_n += [(B(81), n('D4'), 70, B(12)), (B(84), n('Eb4'), 64, B(9)), (B(87), n('E4'), 64, B(6)),
                (B(90), n('F4'), 70, B(3))]

    # ---- the slam ----
    ts = B(T_SLAM)
    M.add('knock', bd_big.play(127), ts - 0.08, 1.0)
    M.add('knock', loglo.play(127), ts, 1.0)
    M.add('knock', slap.play(127), ts, 0.8)
    M.add('perc', gong.play(120), ts, 0.8)
    M.add('perc', timp.play(127, pitch=-3), ts, 0.9)
    for m in ('D1', 'A1', 'D2', 'Eb2'):
        M.add('piano', piano.play(n(m), 120), ts, 0.8)
    for k in range(len(CANDLES)):           # each candle puffs out as the wave reaches it
        M.add('fx', whoosh(0.3, 900, 300, 0.35, seed=90 + k), blowout(k) - 0.05, 0.5, pan_at(CANDLES[k]))
    M.add('wind', whoosh(4.5, 500, 150, 0.4, seed=99), ts + 0.2, 0.6)

    # ---- the blue candle at the back of the house, and its knock ----
    tr = B(T_RELIGHT)
    pb = pan_at(BLUE_AT)
    M.add('fx', whoosh(0.4, 400, 1200, 0.3, seed=120), tr - 0.15, 0.5, pb)
    M.add('perc', gong_s.play(60), tr - 0.1, 0.25, pb)
    M.add('box', one(box, n('A4'), 90, BEAT * 1.5), tr, 1.0, pb)
    glass_n += [(tr, n('D4'), 64, B(8)), (tr, n('A4'), 54, B(8))]
    knock(T_LAST, BLUE_AT, 0.55)
    for i, (b, m) in enumerate(((105.5, 'A4'), (106, 'A4'), (106.5, 'C5'), (107, 'D5'))):   # is anyone... there?
        M.add('box', one(box, n(m), 80 - 6 * i, BEAT * (2.5 if i == 3 else 0.45)), B(b), 0.9, pb)
    M.add('bass', cbpizz.play(n('D2'), 70), B(107), 0.8)

    M.add('piano', piano_render(piano, piano_n), 0.0)
    M.add('glass', glass(glass_n, D), 0.0)
    M.add('bed', bed.render(bed_n, D), 0.0)


def piano_render(piano, notes):
    """Sum piano notes into one buffer (all panned centre-left by the bus)."""
    from pixelhome.audio import SR
    end = max(t + d for t, _, _, d in notes) + 3.0
    out = np.zeros((2, int(end * SR)))
    for t, m, v, d in notes:
        s = piano.play(m, v, dur=d, release=0.25)
        a = int(t * SR)
        e = min(out.shape[1], a + s.shape[1])
        out[:, a:e] += s[:, :e - a]
    return out
