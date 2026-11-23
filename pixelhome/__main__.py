"""pixelhome command line.

  python -m pixelhome list                      every home and sequence
  python -m pixelhome build [--out dist] [match ...]
                                                render sequences, write the site to dist/
  python -m pixelhome preview [--occasion O] [--video] match [...]
                                                timeline + stills PNGs (and MP4) into build/preview/
  uv run --group audio python -m pixelhome music [--occasion O] [--video] match [...]
                                                render each matching show's score() to homes/<home>/audio/ (MP3)
  uv run --group audio python -m pixelhome music --stale [--check] [match ...]
                                                re-render the soundtracks whose score no longer matches its MP3
                                                (--check: list them, exit 1 if any)
  uv run --group audio python -m pixelhome music --stamp match [...]
                                                record the matching scores as matching their MP3s, without rendering
  python -m pixelhome restring [--home H] RUN COUNT
                                                a run re-strung with COUNT pixels: home.json and its channels
  uv run --group audio python -m pixelhome intro [--occasion O] match [...]
                                                read each matching sequence's VOICEOVER line in its occasion's voice,
                                                to homes/<home>/intros/ (MP3 + loudness JSON for the FSEQ)

`match` is a substring of a sequence id, code or title (case-insensitive).
"""
import argparse, os, sys
from . import catalog
from .build import build, preview


def main():
    ap = argparse.ArgumentParser(prog='python -m pixelhome', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('list')
    b = sub.add_parser('build')
    b.add_argument('--out', default=os.path.join(catalog.ROOT, 'dist'))
    b.add_argument('match', nargs='*')
    p = sub.add_parser('preview')
    p.add_argument('--out', default=os.path.join(catalog.ROOT, 'build', 'preview'))
    p.add_argument('--occasion', help='only load this playlist folder, or every playlist of this occasion')
    p.add_argument('--video', action='store_true', help='also write an MP4 (needs ffmpeg)')
    p.add_argument('match', nargs='+')
    m = sub.add_parser('music')
    m.add_argument('--occasion', help='only load this playlist folder, or every playlist of this occasion')
    m.add_argument('--video', action='store_true', help='also write the preview MP4 with the music')
    m.add_argument('--stale', action='store_true', help="only the scores whose cues no longer match their MP3's")
    m.add_argument('--check', action='store_true', help='with --stale: list them and exit 1 if any, render nothing')
    m.add_argument('--stamp', action='store_true', help="record the scores' cues as matching their MP3s, no render")
    m.add_argument('match', nargs='*')
    r = sub.add_parser('restring')
    r.add_argument('--home', default='cjimti')
    r.add_argument('run')
    r.add_argument('count', type=int)
    i = sub.add_parser('intro')
    i.add_argument('--occasion', help='only load this playlist folder, or every playlist of this occasion')
    i.add_argument('match', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'list':
        for h in catalog.homes():
            home = catalog.load_home(h)
            print(f'{h}: {home.name} ({home.N} pixels)')
            for s in catalog.sequences(h):
                print(f'  {s.code:6} {s.occasion:12} {s.kind:8} {s.id:16} {s.title}')
    elif a.cmd == 'build':
        build(os.path.abspath(a.out), a.match)
    elif a.cmd == 'intro':
        from .intro import intro
        intro(a.match, a.occasion)
    elif a.cmd == 'music':
        from .audio import music, stamp, stale
        if a.stamp:
            stamp(a.match, a.occasion)
        elif a.stale:
            return stale(a.match, a.occasion, check=a.check, video=a.video)
        else:
            if not a.match:
                ap.error('music needs a match (or --stale)')
            music(a.match, a.occasion, a.video)
    elif a.cmd == 'restring':
        from .restring import restring
        restring(a.home, a.run, a.count)
    else:
        preview(a.match, a.out, a.occasion, a.video)


if __name__ == '__main__':
    sys.exit(main())
