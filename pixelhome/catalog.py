"""Find homes and their sequences on disk."""
import glob, importlib.util, os
from dataclasses import dataclass
from .home import Home
from .occasions import BY_ID, KINDS, PLAYLIST, PLAYLISTS, playlists

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOMES = os.path.join(ROOT, 'homes')


@dataclass
class Sequence:
    home: str
    occasion: str
    playlist: str
    id: str
    path: str
    code: str
    title: str
    kind: str
    description: str

    def load(self):
        name = f'pixelhome_seq.{self.home}.{self.id}'.replace('-', '_').replace('/', '.')
        spec = importlib.util.spec_from_file_location(name, self.path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


def homes():
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(HOMES, '*', 'home.json')))


def load_home(home_id):
    return Home(os.path.join(HOMES, home_id))


def sequences(home_id, occasion=None):
    """All sequences of a home, validated, sorted by occasion, playlist, then code. `occasion` narrows it to one
    playlist folder, or to every playlist of an occasion; only those modules are imported, so a broken file
    elsewhere doesn't get in the way."""
    out = []
    base = os.path.join(HOMES, home_id, 'sequences')
    folders = playlists(occasion) if occasion in BY_ID else [occasion or '*']
    for path in sorted(p for f in folders for p in glob.glob(os.path.join(base, f, '*.py'))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.startswith('_'):
            continue
        playlist = os.path.basename(os.path.dirname(path))
        if playlist not in PLAYLIST:
            raise SystemExit(f'{path}: unknown playlist folder {playlist!r} (see pixelhome/occasions.py)')
        s = Sequence(home_id, PLAYLIST[playlist]['occasion'], playlist, f"{playlist}/{stem.replace('_', '-')}",
                     path, '', '', '', '')
        mod = s.load()
        missing = [k for k in ('CODE', 'TITLE', 'KIND', 'DESCRIPTION', 'render') if not hasattr(mod, k)]
        if missing:
            raise SystemExit(f'{path}: missing {", ".join(missing)}')
        if mod.KIND not in KINDS:
            raise SystemExit(f'{path}: KIND must be one of {", ".join(KINDS)}')
        s.code, s.title, s.kind, s.description = mod.CODE, mod.TITLE, mod.KIND, mod.DESCRIPTION
        out.append(s)
    order = {o: i for i, o in enumerate(BY_ID)}
    within = {p['id']: i + 1 for i, p in enumerate(PLAYLISTS)}           # an occasion's own playlist first
    out.sort(key=lambda s: (order[s.occasion], within.get(s.playlist, 0), s.kind != 'show', s.code))
    codes = [s.code for s in out]
    dup = {c for c in codes if codes.count(c) > 1}
    if dup:
        raise SystemExit(f'{home_id}: duplicate CODE {", ".join(sorted(dup))}')
    return out
