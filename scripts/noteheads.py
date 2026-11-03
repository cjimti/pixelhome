"""Find the noteheads on a scanned score page and name their pitches, staff by staff and bar by bar.

A helper for transcribing a public-domain score by hand (the oratorios: see homes/cjimti/sequences/elijah/README.md).
Render the page at 500 dpi in grey (`pdftoppm -r 500 -gray -png -f N -l N score.pdf page`), read off the barline x
positions and each staff's top line y near the left edge from the image, then:

    uv run --group score python scripts/noteheads.py page.png 310,820,1400,2010 S:612:G A:870:G T:1130:T B:1390:F

Each staff is NAME:TOP:CLEF[:SPACING] (clef G treble, T treble an octave down (the tenor), F bass, C the tenor C
clef on the fourth line; spacing between staff lines in pixels, about 18.85 at 500 dpi for the Novello octavo). It
prints one row per staff, the bars split by '|', each head as X KIND:PITCH, KIND F filled, H hollow (a half or whole
note found as a hole in the ink), f a filled head found only by the looser second pass. A '?' marks a head between a
line and a space: check it with scripts/staff_lines.py. Accidentals are not read (the key and the page say what they
are), and rhythms are read by eye.

Staves slope by about 10 px across a page, so each staff is tracked across the bar in windows; a fixed search window
locks onto the wrong line.
"""
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

TOP = {'G': ('F', 5), 'T': ('F', 4), 'F': ('A', 3), 'C': ('E', 4)}      # the pitch on each clef's top line
ST = 'CDEFGAB'


def refine(im, top, sp, x0, x1):
    """Snap a staff's top line (and spacing) to the image within x0..x1."""
    prof = (im[:, x0:x1] < 120).mean(1)
    best = (-1, top, sp)
    for dsp in np.arange(-0.4, 0.41, 0.1):
        for off in np.arange(-7, 7.01, 0.5):
            t = top + off
            s = sum(prof[int(round(t + k * (sp + dsp)))] for k in range(5))
            if s > best[0]:
                best = (s, t, sp + dsp)
    return best[1], best[2]


def track(dark, top0, sp0, xa, xb, step=60):
    """The top line y and spacing at each x from xa to xb, following the staff across the page."""
    out = {}
    top, sp = top0, sp0
    for x in range(xa, xb, step):
        prof = dark[:, x:x + step].mean(1)
        best = (-1, top, sp)
        for dsp in np.arange(-0.3, 0.31, 0.1):
            for off in np.arange(-3, 3.01, 0.5):
                t = top + off
                s = sum(prof[int(round(t + k * (sp + dsp)))] for k in range(5))
                if s > best[0]:
                    best = (s, t, sp + dsp)
        if best[0] > 1.5:                       # lines found here (else keep the last)
            top, sp = best[1], best[2]
        out[x] = (top, sp)
    return out


def name(top, sp, clef, y):
    s, o = TOP[clef]
    k = (y - top) / (sp / 2)
    i = ST.index(s) + 7 * o - round(k)
    return f'{ST[i % 7]}{i // 7}' + ('?' if abs(k - round(k)) > 0.3 else '')


def loose(im, top, sp, clef, x0, x1, up=3.0, dn=3.0):
    """Filled heads by a looser pass: staff lines erased, holes filled, opened with a head-sized element."""
    top, sp = refine(im, top, sp, x0, x1)
    y0, y1 = int(top - up * sp), int(top + (4 + dn) * sp)
    a = im[y0:y1, x0:x1] < 125
    for k in range(-int(up) - 1, int(4 + dn) + 2):
        yl = int(round(top + k * sp)) - y0
        for yy in range(yl - 1, yl + 2):
            if 2 <= yy < a.shape[0] - 3:
                a[yy] = a[yy] & (a[yy - 3] & a[yy + 3])
    a = ndimage.binary_closing(a, structure=np.ones((3, 3), bool))
    a = ndimage.binary_fill_holes(a)
    b = ndimage.binary_opening(a, structure=np.ones((max(3, int(sp * 0.55)), max(3, int(sp * 0.75))), bool))
    lab, n = ndimage.label(b)
    out = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (0.85 * sp <= w <= 1.6 * sp) or h < 0.6 * sp:
            continue
        nh = max(1, round(h / (sp * 0.95)))
        if nh > 1 and h / nh < 0.75 * sp:
            continue
        cx = x0 + (sl[1].start + sl[1].stop) / 2
        for j in range(nh):
            out.append((int(cx), name(top, sp, clef, y0 + sl[0].start + (j + 0.5) * h / nh).rstrip('?')))
    return sorted(out)


def heads(dark, top_at, x0, x1, clef):
    """Filled and hollow heads between x0 and x1 on the tracked staff."""
    tops = [top_at[x] for x in sorted(top_at) if x0 - 60 <= x < x1]
    top = np.mean([t for t, s in tops])
    sp = np.mean([s for t, s in tops])
    y0, y1 = int(top - 4 * sp), int(top + 8 * sp)
    a = dark[y0:y1, x0:x1].copy()
    for k in range(-4, 9):                      # erase line pixels where no stroke continues above and below
        yl = int(round(top + k * sp)) - y0
        for yy in range(yl - 2, yl + 3):
            if 3 <= yy < a.shape[0] - 3:
                a[yy] &= (a[yy - 3] & a[yy + 3])
    filled = ndimage.binary_opening(a, np.ones((max(3, int(sp * .5)), max(3, int(sp * .7))), bool))
    raw = dark[y0:y1, x0:x1]
    holes = ndimage.binary_fill_holes(raw) & ~raw
    out = []
    lab, n = ndimage.label(filled)
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (0.8 * sp <= w <= 1.7 * sp) or h < 0.55 * sp:
            continue
        nh = max(1, round(h / (sp * 0.95)))
        for j in range(nh):
            out.append(((sl[1].start + sl[1].stop) / 2, sl[0].start + (j + .5) * h / nh, 'F'))
    lab, n = ndimage.label(holes)
    cand = []
    for sl in ndimage.find_objects(lab):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if 0.4 * sp <= w <= 1.5 * sp and 2 <= h <= 0.95 * sp:
            cand.append([sl[1].start, sl[1].stop, sl[0].start, sl[0].stop])
    cand.sort(key=lambda c: (c[0], c[2]))
    merged = []
    for c in cand:                              # a hollow head split by a staff line is one head
        for m in merged:
            if abs((m[0] + m[1]) / 2 - (c[0] + c[1]) / 2) < 0.45 * sp and -1 <= c[2] - m[3] <= 5:
                m[1] = max(m[1], c[1])
                m[3] = max(m[3], c[3])
                break
        else:
            merged.append(list(c))
    for c0, c1, r0, r1 in merged:
        h, w = r1 - r0, c1 - c0
        cy = (r0 + r1) / 2
        if not (0.3 * sp <= h <= 0.95 * sp and w > 1.1 * h):
            continue
        if not (-3.2 * sp <= cy + y0 - top <= 6.2 * sp):
            continue
        r = int(cy)
        lft = raw[r, max(0, c0 - int(.3 * sp)):c0].mean() if c0 > 0 else 0
        rgt = raw[r, c1:c1 + int(.3 * sp)].mean()
        if lft > .3 and rgt > .3:               # ink on both sides: a head's outline, not a gap between strokes
            out.append(((c0 + c1) / 2, cy, 'H'))
    return [(int(x0 + cx), kind, name(top, sp, clef, cy + y0)) for cx, cy, kind in sorted(out)]


def main(argv):
    path, xs = argv[0], [int(v) for v in argv[1].split(',')]
    im = np.array(Image.open(path).convert('L')).astype(float)
    dark = im < 125
    for spec in argv[2:]:
        p = spec.split(':')
        label, top, clef = p[0], float(p[1]), p[2]
        sp = float(p[3]) if len(p) > 3 else 18.85
        ta = track(dark, top, sp, xs[0], xs[-1])
        row = []
        for a, b in zip(xs[:-1], xs[1:]):
            tops = [ta[x] for x in sorted(ta) if a - 60 <= x < b]
            t, s_ = np.mean([q[0] for q in tops]), np.mean([q[1] for q in tops])
            mine = heads(dark, ta, a + 6, b - 3, clef)
            extra = [(x, 'f', pt) for x, pt in loose(im, t, s_, clef, a + 6, b - 3)
                     if not any(abs(m[0] - x) < 10 for m in mine)]
            row.append(' '.join(f'{x}{k}:{pt}' for x, k, pt in sorted(mine + extra)))
        print(label.ljust(3), ' | '.join(row))


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1:])
