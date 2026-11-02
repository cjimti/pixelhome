"""Crop staves from a scanned score page with their tracked lines drawn on, to check doubtful noteheads by eye.

The companion of scripts/noteheads.py: where it marks a head '?', or a pitch looks wrong against the harmony, crop
the staves here and look.

    uv run --group score python scripts/staff_lines.py page.png out.png 300 1500 1.5 S:612:G A:870:G

x0 x1 is the stretch of the page to crop, scale enlarges it, and each staff is NAME:TOP:CLEF as in noteheads.py.
The five staff lines are drawn red, ledger-line positions pink, and every 420 px the line and space positions are
labelled with their pitch (lines red, spaces blue).
"""
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TOP = {'G': ('F', 5), 'T': ('F', 4), 'F': ('A', 3)}
ST = 'CDEFGAB'


def font(size):
    for f in ('/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def main(argv):
    path, out, x0, x1, sc = argv[0], argv[1], int(argv[2]), int(argv[3]), float(argv[4])
    im = Image.open(path).convert('RGB')
    dark = np.array(im.convert('L')) < 125
    label_font = font(13)
    tiles = []
    for spec in argv[5:]:
        p = spec.split(':')
        top, clef = float(p[1]), p[2]
        sp = float(p[3]) if len(p) > 3 else 18.8
        tops, t = {}, top
        for x in range(x0, x1, 40):             # follow the staff in windows of 40 px
            prof = dark[:, x:x + 40].mean(1)
            best = (-1, t)
            for off in np.arange(-3, 3.01, 0.5):
                s = sum(prof[int(round(t + off + k * sp))] for k in range(5))
                if s > best[0]:
                    best = (s, t + off)
            if best[0] > 1.5:
                t = best[1]
            tops[x] = t
        ya, yb = int(top - 4 * sp), int(top + 8 * sp)
        c = im.crop((x0, ya, x1, yb)).copy()
        d = ImageDraw.Draw(c)
        s, o = TOP[clef]
        base = ST.index(s) + 7 * o
        for x, t in tops.items():
            for k in range(-6, 15):
                y = t + k * sp / 2 - ya
                col = (230, 0, 0) if k % 2 == 0 and 0 <= k <= 8 else ((255, 150, 150) if k % 2 == 0 else None)
                if col:
                    d.line([(x - x0, y), (x - x0 + 40, y)], fill=col, width=1)
        c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
        d = ImageDraw.Draw(c)
        for xl in range(0, x1 - x0, 420):
            t = tops[x0 + (xl // 40) * 40]
            for k in range(-6, 15):
                y = (t + k * sp / 2 - ya) * sc
                i = base - k
                d.text((xl * sc + 2, y - 7), f'{ST[i % 7]}{i // 7}', fill=(0, 90, 220) if k % 2 else (200, 0, 0),
                       font=label_font)
        tiles.append(c)
    W, H = max(t.width for t in tiles), sum(t.height for t in tiles)
    sheet = Image.new('RGB', (W, H), 'white')
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height
    sheet.save(out)


if __name__ == '__main__':
    if len(sys.argv) < 7:
        sys.exit(__doc__)
    main(sys.argv[1:])
