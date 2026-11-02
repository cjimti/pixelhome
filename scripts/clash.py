"""Flag the moments where the voices of a transcribed excerpt clash by a semitone, to catch misread notes.

    uv run python scripts/clash.py homes/cjimti/sequences/elijah/before_ahab.score.json [S,A,T,B,Orch]

Reads a <name>.score.json written by scripts/score_excerpt.py and prints each onset where a sung voice sits a
semitone from another sounding note (voice or orchestra), with the bar, the voices and the orchestra's pitch
classes. Passing notes and suspensions are flagged too; a misread usually shows as a clash held for a whole beat or
a chord that makes no sense. The optional second argument limits the parts considered.
"""
import json
import sys

N = 'C C# D Eb E F F# G Ab A Bb B'.split()


def main(path, parts=None):
    d = json.load(open(path))
    bars = d['bars']

    def bar_at(t):
        b = [m for m, s in bars if s <= t + 1e-6]
        return b[-1] if b else 0

    notes = [n for n in d['notes'] if parts is None or n[5] in parts]
    for t in sorted({round(n[0], 3) for n in notes}):
        snd = [(n[2], n[5]) for n in notes if n[0] <= t + 1e-3 < n[0] + n[1]]
        voices = [(m, p) for m, p in snd if p != 'Orch']
        pcs = {m % 12 for m, p in snd}
        bad = [(a, b) for a in {m % 12 for m, p in voices} for b in pcs if (b - a) % 12 == 1]
        if bad:
            print(f'bar {bar_at(t)} t={t:.2f}', ' '.join(f'{N[m % 12]}{m // 12 - 1}:{p}' for m, p in sorted(voices)),
                  '| orch', ' '.join(sorted({N[m % 12] for m, p in snd if p == 'Orch'})))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2].split(',') if len(sys.argv) > 2 else None)
