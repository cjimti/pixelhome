"""Cut an excerpt of Wagner's Ring out of the Wagner Ring Dataset, timed like a real performance.

The dataset (Weiß, Zalkow, Müller et al., Zenodo 7672157, CC BY 3.0) has every act as a piano reduction of the full
score (MIDI) with measure annotations, and the measure positions in 16 recorded performances. An excerpt is one or
more measure ranges of an act: its notes come from the score, its timing from a performance's measures (so the
tempo and rubato are that conductor's), spliced end to end. The result is a small JSON file a sequence loads with
pixelhome.ring.excerpt(); it is committed, so the build doesn't need the dataset.

    uv run --with mido python scripts/ring_excerpt.py B-3 263-302 --perf Solti1958 --out homes/.../name.json

Ranges are measure numbers as in the dataset's annotations (bar 1 is the first full bar; Walküre II and III open
on an upbeat, measure 0); several ranges are spliced with
--gap seconds between them. Fetch the dataset's scores and annotations first (see pixelhome/ring.py).
"""
import argparse
import csv
import json
import os

import numpy as np

ROOT = os.path.expanduser(os.environ.get('WAGNER_RING', '~/.cache/pixelhome/wagner-ring'))
ACTS = {'A': 'Das Rheingold', 'B-1': 'Die Walküre, Act I', 'B-2': 'Die Walküre, Act II', 'B-3': 'Die Walküre, Act III',
        'C-1': 'Siegfried, Act I', 'C-2': 'Siegfried, Act II', 'C-3': 'Siegfried, Act III',
        'D-0': 'Götterdämmerung, Prologue', 'D-1': 'Götterdämmerung, Act I', 'D-2': 'Götterdämmerung, Act II',
        'D-3': 'Götterdämmerung, Act III'}


def rows(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=';'))


def score(act):
    """Notes of an act as (measure position, measure length, midi, velocity, hand), measure positions fractional."""
    import mido
    mid = mido.MidiFile(os.path.join(ROOT, '01_RawData/score_midi', f'Wagner_WWV086{act}.mid'))
    tpb = mid.ticks_per_beat
    sigs, t = [], 0
    for msg in mid.tracks[0]:
        t += msg.time
        if msg.type == 'time_signature':
            sigs.append((t, msg.numerator * 4 * tpb // msg.denominator))
    # bar lines in ticks, one bar per time signature length from the start. The MIDI's first bar is the act's first
    # annotated measure: 0 where the act opens on an upbeat (Walküre II and III), 1 everywhere else
    first = int(float(rows(os.path.join(ROOT, '02_Annotations/ann_score_timesignatures',
                                        f'Wagner_WWV086{act}.csv'))[0]['measure']))
    bars = [0]
    end = max(sum(msg.time for msg in tr) for tr in mid.tracks)
    k, t = 0, 0
    while t < end:
        while k + 1 < len(sigs) and sigs[k + 1][0] <= t:
            k += 1
        t += sigs[k][1]
        bars.append(t)
    bars = np.array(bars, float)
    notes = []
    hands = [tr for tr in mid.tracks if any(msg.type == 'note_on' for msg in tr)]     # right hand, left hand
    for hand, tr in enumerate(hands):
        t, on = 0, {}
        for msg in tr:
            t += msg.time
            if msg.type == 'note_on' and msg.velocity:
                on.setdefault(msg.note, []).append((t, msg.velocity))
            elif msg.type in ('note_off', 'note_on') and on.get(msg.note):
                t0, v = on[msg.note].pop(0)
                notes.append((t0, t, msg.note, v, hand))
    meas = lambda tick: first + np.interp(tick, bars, np.arange(len(bars)))
    return [(float(meas(a)), float(meas(b)), n, v, h) for a, b, n, v, h in notes]


def timing(act, perf):
    """Measure position -> seconds in a recorded performance."""
    r = rows(os.path.join(ROOT, '02_Annotations/ann_audio_measure', f'Wagner_WWV086{act}_{perf}.csv'))
    return np.array([float(x['measure']) for x in r]), np.array([float(x['start']) for x in r])


def excerpt(act, ranges, perf, gap):
    notes = score(act)
    mx, sx = timing(act, perf)
    sing = rows(os.path.join(ROOT, '02_Annotations/ann_score_singing', f'Wagner_WWV086{act}.csv'))
    out = dict(notes=[], bars=[], singing=[], segments=[])
    t_at = 0.0
    for a, b in ranges:
        s0 = float(np.interp(a, mx, sx))
        sec = lambda m: float(np.interp(m, mx, sx)) - s0 + t_at
        for m0, m1, n, v, h in notes:
            if a <= m0 < b or m0 < a < m1 - 0.05:          # notes still sounding at the start are carried in
                m0 = max(m0, a)
                out['notes'].append([round(sec(m0), 4), round(max(0.03, sec(min(m1, b)) - sec(m0)), 4), n, v, h])
        for m in range(int(np.ceil(a)), int(np.floor(b)) + 1):
            out['bars'].append([m, round(sec(m), 4)])
        for x in sing:
            p0, p1 = float(x['measure_start']), float(x['measure_end'])
            if p1 > a and p0 < b:
                out['singing'].append([round(sec(max(p0, a)), 3), round(sec(min(p1, b)), 3), x['person'], x['text']])
        out['segments'].append(dict(measures=[a, b], start=round(t_at, 4), seconds=round(sec(b) - t_at, 4)))
        t_at = sec(b) + gap
    out['notes'].sort()
    out['seconds'] = round(t_at - gap, 4)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('act', choices=sorted(ACTS))
    ap.add_argument('ranges', nargs='+', help='measure ranges a-b (end exclusive), spliced in order')
    ap.add_argument('--perf', default='Solti1958')
    ap.add_argument('--gap', type=float, default=0.0)
    ap.add_argument('--out')
    a = ap.parse_args()
    ranges = [tuple(float(x) for x in r.split('-')) for r in a.ranges]
    ex = excerpt(a.act, ranges, a.perf, a.gap)
    ex = dict(source='Wagner Ring Dataset (Zenodo 7672157), CC BY 3.0', act=ACTS[a.act], perf=a.perf,
              **{k: ex[k] for k in ('seconds', 'segments', 'bars', 'singing', 'notes')})
    print(f"{ACTS[a.act]} {a.ranges} ({a.perf}): {ex['seconds']:.1f} s, {len(ex['notes'])} notes, "
          f"{len(ex['bars'])} bars, {len(ex['singing'])} sung lines")
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with open(a.out, 'w') as f:
            json.dump(ex, f, separators=(',', ':'))


if __name__ == '__main__':
    main()
