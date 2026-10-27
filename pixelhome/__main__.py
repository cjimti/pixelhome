"""pixelhome command line.

  python -m pixelhome list                      every home and sequence
  python -m pixelhome build [--out dist] [match ...]
                                                render sequences, write the site to dist/
  python -m pixelhome preview match [...]       MP4 preview + timeline PNG into build/preview/

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
    p.add_argument('match', nargs='+')
    a = ap.parse_args()
    if a.cmd == 'list':
        for h in catalog.homes():
            home = catalog.load_home(h)
            print(f'{h}: {home.name} ({home.N} pixels)')
            for s in catalog.sequences(h):
                print(f'  {s.code:6} {s.occasion:12} {s.kind:8} {s.id:16} {s.title}')
    elif a.cmd == 'build':
        build(os.path.abspath(a.out), a.match)
    else:
        preview(a.match, a.out)


if __name__ == '__main__':
    sys.exit(main())
