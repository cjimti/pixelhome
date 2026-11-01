"""Cut an excerpt of a score out of MusicXML, timed by bar times, into the Ring's <name>.score.json shape.

The sibling of scripts/ring_excerpt.py for works that have no dataset: the oratorios (Elijah, Judas Maccabaeus,
Messiah). The notes come from a MusicXML transcription of a public-domain score; the timing comes from either

  --bars FILE   bar times tapped against a recording: CSV rows `measure,start` (seconds; fractional measures such as
                12.5 for a beat inside bar 12 are fine, and the row after the excerpt's last bar is needed), the same
                kind of data as the Ring dataset's performance annotations. Name the recording with --perf.
  --tempo       or the score's own tempo markings (<sound tempo>, <metronome>), with a fermata holding its note or
                rest --fermata times as long (default 2) and --hold M=SECONDS adding a pause at measure position M (put it
                where nothing starts, such as the start of a silent bar: a note starting exactly at M would start
                before the pause).

Written silences (rests, fermata rests, general pauses) are kept as time with no notes in it, so they come out as real
gaps in the JSON.

    uv run python scripts/score_excerpt.py score.musicxml 1-40 52-71 --bars taps.csv --perf "Conductor 1968" \\
        --part P1=S --part P2=A --part P3=T --part P4=B --part P5=Orch \\
        --source "Novello vocal score (1847), transcribed" --act "Elijah, No. 13" --out homes/.../name.score.json

Ranges are measure numbers as printed (end exclusive), spliced end to end with --gap seconds between them. The JSON
is what pixelhome.ring.excerpt() loads: source, act, perf, seconds, segments, bars, singing, notes, with each note
[t, d, midi, velocity, hand, part]. part is the label given with --part ID=LABEL[:HAND] (ID is the MusicXML part id,
name or abbreviation); hand is 0 for the upper line and 1 for the lower, as in the Ring's piano reduction (a
two-staff part's lower staff is hand 1; otherwise a part's hand comes from its register unless :HAND sets it).
singing is each part's lyric phrases, [t0, t1, part, text]. Repeats are not expanded; dynamics set velocity
(hairpins are not interpolated), accents add to it and staccato shortens.
"""
import argparse
import csv
import json
import os
import re
import xml.etree.ElementTree as ET

import numpy as np

STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
DYN = {'pppp': 22, 'ppp': 30, 'pp': 42, 'p': 55, 'mp': 68, 'mf': 80, 'f': 96, 'ff': 110, 'fff': 120, 'ffff': 126}
ONE_OFF = {'sf': 118, 'sfz': 120, 'sffz': 124, 'fz': 116, 'rfz': 110, 'rf': 108, 'sfp': 116, 'fp': 100}
BEAT = {'whole': 4.0, 'half': 2.0, 'quarter': 1.0, 'eighth': 0.5, '16th': 0.25, '32nd': 0.125}
LOW = re.compile(r'^(t|b|ten|tenor|bar|baritone|bass|basses|bsn|bassoon|vc|vlc|cello|cb|kb|tuba|tbn|ped)', re.I)


def local(tag):
    return tag.rsplit('}', 1)[-1]


def strip_ns(root):
    for e in root.iter():
        e.tag = local(e.tag)
    return root


def load(path):
    """The score's root, from .musicxml/.xml or a compressed .mxl."""
    if path.endswith('.mxl'):
        import zipfile
        with zipfile.ZipFile(path) as z:
            cont = strip_ns(ET.fromstring(z.read('META-INF/container.xml')))
            name = cont.find('.//rootfile').get('full-path')
            return strip_ns(ET.fromstring(z.read(name)))
    return strip_ns(ET.parse(path).getroot())


def measure_numbers(measures):
    """Printed measure numbers, in order: the number attribute where it is an integer, else one past the last."""
    out, last = [], None
    for m in measures:
        try:
            n = int(m.get('number'))
        except (TypeError, ValueError):
            n = (last + 1) if last is not None else 0
        if last is not None and n <= last:
            n = last + 1
        out.append(n)
        last = n
    return out


def read(root):
    """The score as dict(parts={id: dict(name, abbr, staves, notes=[[q0, q1, midi, vel, staff, lyric]])},
    numbers, starts (quarter at each measure's start, plus the end), tempos [(q, bpm)], fermatas [(q0, q1)]).
    Offsets are read per measure first; measure lengths are the furthest any part reaches (so pickups and short
    bars come out right) and only then turned into quarters from the start."""
    names = {}
    for sp in root.iter('score-part'):
        names[sp.get('id')] = ((sp.findtext('part-name') or '').strip(), (sp.findtext('part-abbreviation') or '').strip())
    parts = root.findall('part')
    if not parts:
        raise SystemExit('no <part> elements: only partwise MusicXML is read')
    numbers = measure_numbers(parts[0].findall('measure'))
    lengths = [0.0] * len(numbers)
    nominals = [4.0] * len(numbers)
    raw, tempos, fermatas = {}, [], set()                       # offsets as (measure index, quarters into it)
    for pi, part in enumerate(parts):
        pid = part.get('id')
        div, staves, transpose, nominal = 1, 1, 0, 4.0
        vel, one_off = DYN['mf'], {}
        notes, open_ties = [], {}
        measures = part.findall('measure')
        if len(measures) != len(numbers):
            raise SystemExit(f'part {pid} has {len(measures)} measures, the first part {len(numbers)}')
        for k, meas in enumerate(measures):
            cur, last_on, reach = 0.0, 0.0, 0.0
            for e in meas:
                if e.tag == 'attributes':
                    div = int(float(e.findtext('divisions') or div))
                    staves = int(e.findtext('staves') or staves)
                    t = e.find('time')
                    if t is not None and t.findtext('beats'):
                        beats = sum(int(x) for x in t.findtext('beats').split('+'))
                        nominal = beats * 4.0 / int(t.findtext('beat-type'))
                    tr = e.find('transpose')
                    if tr is not None:
                        transpose = int(float(tr.findtext('chromatic') or 0)) + 12 * int(tr.findtext('octave-change') or 0)
                elif e.tag == 'backup':
                    cur -= int(e.findtext('duration')) / div
                elif e.tag == 'forward':
                    cur += int(e.findtext('duration')) / div
                    reach = max(reach, cur)
                elif e.tag in ('direction', 'sound'):
                    snd = e if e.tag == 'sound' else e.find('sound')
                    off = cur + (int(e.findtext('offset')) / div if e.findtext('offset') else 0.0)
                    if pi == 0 and snd is not None and snd.get('tempo'):
                        tempos.append((k, off, float(snd.get('tempo'))))
                    elif pi == 0 and e.tag == 'direction':
                        mm = e.find('.//metronome')
                        if mm is not None and mm.findtext('per-minute'):
                            unit = BEAT.get(mm.findtext('beat-unit'), 1.0) * (1.5 if mm.find('beat-unit-dot') is not None else 1)
                            try:
                                tempos.append((k, off, float(mm.findtext('per-minute')) * unit))
                            except ValueError:
                                pass
                    dyn = e.find('.//dynamics')
                    if dyn is not None and len(dyn):
                        d = dyn[0].tag
                        if d in DYN:
                            vel = DYN[d]
                        elif d in ONE_OFF:
                            one_off[(k, round(off, 4))] = ONE_OFF[d]
                            if d in ('sfp', 'fp'):
                                vel = DYN['p']
                    if snd is not None and snd.get('dynamics'):
                        vel = int(np.clip(float(snd.get('dynamics')) * 0.9, 1, 127))
                elif e.tag == 'note':
                    grace = e.find('grace') is not None
                    chord = e.find('chord') is not None
                    dur = 0.0 if grace else int(e.findtext('duration') or 0) / div
                    on = last_on if chord else cur
                    if not chord and not grace:
                        cur += dur
                        reach = max(reach, cur)
                    last_on = on
                    if e.find('.//fermata') is not None:           # a fermata in any part holds everyone
                        fermatas.add((k, on, on + dur))
                    p = e.find('pitch')
                    if p is None:
                        continue                                   # a rest, or unpitched percussion
                    midi = 12 * (int(p.findtext('octave')) + 1) + STEP[p.findtext('step')] + \
                        int(float(p.findtext('alter') or 0)) + transpose
                    staff = int(e.findtext('staff') or 1)
                    v = one_off.pop((k, round(on, 4)), vel)
                    end = on + dur
                    art = e.find('.//articulations')
                    if art is not None and any(a.tag in ('accent', 'strong-accent') for a in art):
                        v = min(127, v + 14)
                    if art is not None and any(a.tag in ('staccato', 'staccatissimo', 'spiccato') for a in art):
                        end = on + dur * 0.5
                    ly = e.find('lyric')
                    lyric = (ly.findtext('syllabic') or 'single', ly.findtext('text')) \
                        if ly is not None and ly.findtext('text') is not None else None
                    ties = {t.get('type') for t in e.findall('tie')}
                    key = (staff, e.findtext('voice') or '1', midi)
                    if 'stop' in ties and key in open_ties:
                        n = open_ties.pop(key)
                        n[1] = (k, end)
                        if 'start' in ties:
                            open_ties[key] = n
                        continue
                    n = [(k, on), (k, end), midi, int(v), staff, lyric]
                    notes.append(n)
                    if 'start' in ties:
                        open_ties[key] = n
            lengths[k] = max(lengths[k], reach)
            nominals[k] = nominal
        raw[pid] = dict(name=names.get(pid, (pid, ''))[0], abbr=names.get(pid, ('', ''))[1], staves=staves, notes=notes)
    lengths = [ln if ln > 0 else nm for ln, nm in zip(lengths, nominals)]   # an empty measure keeps its time signature
    starts = np.concatenate([[0.0], np.cumsum(lengths)])
    q = lambda ko: float(starts[ko[0]] + ko[1])
    for p in raw.values():
        p['notes'] = [[q(a), q(b), m, v, s, ly] for a, b, m, v, s, ly in p['notes']]
    return dict(parts=raw, numbers=numbers, starts=starts,
                tempos=sorted((q((k, o)), bpm) for k, o, bpm in tempos),
                fermatas=sorted((q((k, a)), q((k, b))) for k, a, b in fermatas))


def position(score, q):
    """Quarter-note offset -> measure position (printed number plus the fraction of the bar)."""
    st, nums = score['starts'], score['numbers']
    k = int(np.clip(np.searchsorted(st, q, side='right') - 1, 0, len(nums) - 1))
    return nums[k] + (q - st[k]) / max(st[k + 1] - st[k], 1e-9)


def tempo_timing(score, fermata=2.0, holds=(), bpm=None, scale=1.0):
    """Measure position -> seconds from the score's tempo markings: points (positions, seconds)."""
    st = score['starts']
    tempos = score['tempos'] or [(0.0, bpm or 100.0)]
    if bpm:
        tempos = [(0.0, bpm)]
    if tempos[0][0] > 0:
        tempos = [(0.0, tempos[0][1])] + tempos
    cuts = sorted({float(x) for x in st} | {q for q, _ in tempos} | {q for f in score['fermatas'] for q in f})
    pos, sec, s = [], [], 0.0
    hold = {}
    for m, extra in holds:
        k = score['numbers'].index(int(np.floor(m))) if int(np.floor(m)) in score['numbers'] else None
        if k is None:
            raise SystemExit(f'--hold: no measure {m}')
        q = st[k] + (m - np.floor(m)) * (st[k + 1] - st[k])
        cuts = sorted(set(cuts) | {q})
        hold[q] = hold.get(q, 0.0) + extra
    for a, b in zip(cuts[:-1], cuts[1:]):
        pos.append(position(score, a))
        sec.append(s)
        if hold.get(a):                     # a pause at a: whatever ends there ends before it, what follows waits
            s += hold[a]
            pos.append(position(score, a) + 1e-6)
            sec.append(s)
        t = [x for x in tempos if x[0] <= a + 1e-9][-1][1] * scale
        stretch = fermata if any(f0 <= a + 1e-9 and b <= f1 + 1e-9 for f0, f1 in score['fermatas']) else 1.0
        s += (b - a) * 60.0 / t * stretch
    pos.append(score['numbers'][-1] + 1.0)
    sec.append(s)
    return np.array(pos), np.array(sec)


def tapped_timing(path):
    """Measure position -> seconds from a CSV of bar times: rows measure,start (a header row is skipped)."""
    with open(path, newline='', encoding='utf-8') as f:
        text = f.read()
    rows = list(csv.reader(text.splitlines(), delimiter=';' if ';' in text and ',' not in text else ','))
    pts = []
    for r in rows:
        try:
            pts.append((float(r[0]), float(r[1])))
        except (ValueError, IndexError):
            continue
    pts.sort()
    m, s = np.array([p[0] for p in pts]), np.array([p[1] for p in pts])
    if np.any(np.diff(s) <= 0):
        raise SystemExit(f'{path}: bar times must increase with the measures')
    return m, s


def label_parts(score, specs):
    """{part id: (label, hand or None)} from --part ID=LABEL[:HAND]. With no --part every part is kept under its
    abbreviation or name; with some, only the parts named (and the rest too if '*' is one of them)."""
    want = {}
    for spec in specs:
        key, _, val = spec.partition('=')
        lab, _, hand = val.partition(':')
        want[key] = (lab or key, int(hand) if hand else None)
    out = {}
    for pid, p in score['parts'].items():
        hit = next((want[k] for k in (pid, p['name'], p['abbr']) if k in want), None)
        if hit is None and want and '*' not in want:
            continue
        out[pid] = hit or (p['abbr'] or p['name'] or pid, None)
    return out


def hand_of(p, label, hand, staff):
    if hand is not None:
        return hand
    if p['staves'] > 1:
        return min(staff - 1, 1)
    if LOW.match(label) or LOW.match(p['name']):
        return 1
    pitches = [n[2] for n in p['notes']]
    return int(bool(pitches) and float(np.median(pitches)) < 55)


def phrases(notes, sec, gap=0.35):
    """A part's lyric syllables as sung lines: (t0, t1, text), split where it rests gap seconds or more."""
    out, cur = [], None
    for q0, q1, _, _, _, ly in sorted((n for n in notes if n[5]), key=lambda n: n[0]):
        t0, t1 = sec(q0), sec(q1)
        syl, txt = ly
        if cur and t0 - cur[1] < gap:
            cur[2] += ('' if cur[3] in ('begin', 'middle') else ' ') + txt
            cur[1], cur[3] = max(cur[1], t1), syl
        else:
            if cur:
                out.append(cur[:3])
            cur = [t0, t1, txt, syl]
    if cur:
        out.append(cur[:3])
    return out


def excerpt(score, labels, mx, sx, ranges, gap):
    pos = lambda q: position(score, q)
    out = dict(notes=[], bars=[], singing=[], segments=[])
    t_at = 0.0
    for a, b in ranges:
        if a < mx[0] - 1e-9 or b > mx[-1] + 1e-9:
            raise SystemExit(f'measures {a:g}-{b:g} are outside the timing ({mx[0]:g}-{mx[-1]:g})')
        s0 = float(np.interp(a, mx, sx))
        sec = lambda m: float(np.interp(m, mx, sx)) - s0 + t_at
        for pid, (label, hand) in labels.items():
            p = score['parts'][pid]
            for q0, q1, n, v, staff, _ in p['notes']:
                m0, m1 = pos(q0), pos(q1) if q1 > q0 else pos(q0)
                if a <= m0 < b or m0 < a < m1 - 0.05:              # notes still sounding at the start are carried in
                    m0 = max(m0, a)
                    out['notes'].append([round(sec(m0), 4), round(max(0.03, sec(min(m1, b)) - sec(m0)), 4), n, v,
                                         hand_of(p, label, hand, staff), label])
            inside = [nt for nt in p['notes'] if nt[5] and a <= pos(nt[0]) < b]
            for t0, t1, text in phrases(inside, lambda q: sec(min(pos(q), b))):
                out['singing'].append([round(t0, 3), round(t1, 3), label, text])
        for m in range(int(np.ceil(a)), int(np.floor(b)) + 1):
            out['bars'].append([m, round(sec(m), 4)])
        out['segments'].append(dict(measures=[a, b], start=round(t_at, 4), seconds=round(sec(b) - t_at, 4)))
        t_at = sec(b) + gap
    out['notes'].sort(key=lambda n: (n[0], n[2], n[4], n[5]))
    out['singing'].sort()
    out['seconds'] = round(t_at - gap, 4)
    return out


def silences(ex, least=0.5):
    """Stretches of least seconds or more inside the excerpt where nothing sounds: [(t0, t1)]."""
    end, out = 0.0, []
    for t, d, *_ in ex['notes']:
        if t - end >= least:
            out.append((round(end, 3), round(t, 3)))
        end = max(end, t + d)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('score', help='MusicXML (.musicxml, .xml or .mxl)')
    ap.add_argument('ranges', nargs='+', help='measure ranges a-b (end exclusive), spliced in order')
    how = ap.add_mutually_exclusive_group(required=True)
    how.add_argument('--bars', help='CSV of bar times tapped against a recording: measure,start')
    how.add_argument('--tempo', action='store_true', help="time the excerpt from the score's tempo markings")
    ap.add_argument('--bpm', type=float, help='with --tempo: one tempo (quarter notes a minute) for the whole score')
    ap.add_argument('--scale', type=float, default=1.0, help='with --tempo: multiply every tempo')
    ap.add_argument('--fermata', type=float, default=2.0, help='with --tempo: how many times longer a fermata holds')
    ap.add_argument('--hold', action='append', default=[], metavar='M=SECONDS',
                    help='with --tempo: add SECONDS of time at measure position M (a pause the score leaves implicit)')
    ap.add_argument('--part', action='append', default=[], metavar='ID=LABEL[:HAND]',
                    help="label a part (id, name or abbreviation); when any are given, only those parts are kept "
                         "(add '*' to keep the rest under their own names)")
    ap.add_argument('--gap', type=float, default=0.0)
    ap.add_argument('--source', default='')
    ap.add_argument('--act', default='')
    ap.add_argument('--perf', default='')
    ap.add_argument('--out')
    a = ap.parse_args()
    score = read(load(a.score))
    ranges = [tuple(float(x) for x in r.split('-')) for r in a.ranges]
    if a.bars:
        mx, sx = tapped_timing(a.bars)
        perf = a.perf or os.path.splitext(os.path.basename(a.bars))[0]
    else:
        holds = [(float(h.split('=')[0]), float(h.split('=')[1])) for h in a.hold]
        mx, sx = tempo_timing(score, a.fermata, holds, a.bpm, a.scale)
        perf = a.perf or 'score tempo markings'
    labels = label_parts(score, a.part)
    ex = excerpt(score, labels, mx, sx, ranges, a.gap)
    ex = dict(source=a.source, act=a.act, perf=perf, **{k: ex[k] for k in ('seconds', 'segments', 'bars', 'singing', 'notes')})
    print(f"{a.act or a.score} {a.ranges} ({perf}): {ex['seconds']:.1f} s, {len(ex['notes'])} notes, "
          f"{len(ex['bars'])} bars, {len(ex['singing'])} sung lines; parts "
          + ', '.join(f'{lab}' for lab, _ in labels.values()))
    gaps = silences(ex)
    if gaps:
        print('silences: ' + ', '.join(f'{t0:.2f}-{t1:.2f} s' for t0, t1 in gaps))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
        with open(a.out, 'w', encoding='utf-8') as f:
            json.dump(ex, f, separators=(',', ':'), ensure_ascii=False)


if __name__ == '__main__':
    main()
