"""Find homes and their sequences on disk."""
import glob, importlib.util, os
from dataclasses import dataclass
from .home import Home
from .occasions import BY_ID, KINDS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOMES = os.path.join(ROOT, 'homes')


@dataclass
class Sequence:
    home: str
    occasion: str
    id: str
    path: str
    code: str
    title: str
    kind: str
    description: str

    def load(self):
        name = f'pixelhome_seq.{self.home}.{self.occasion}.{self.id}'.replace('-', '_')
        spec = importlib.util.spec_from_file_location(name, self.path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod


def homes():
    return sorted(os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(HOMES, '*', 'home.json')))


def load_home(home_id):
    return Home(os.path.join(HOMES, home_id))


def sequences(home_id):
    """All sequences of a home, validated, sorted by occasion order then code."""
    out = []
    base = os.path.join(HOMES, home_id, 'sequences')
    for path in sorted(glob.glob(os.path.join(base, '*', '*.py'))):
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.startswith('_'):
            continue
        occasion = os.path.basename(os.path.dirname(path))
        if occasion not in BY_ID:
            raise SystemExit(f'{path}: unknown occasion folder {occasion!r} (see pixelhome/occasions.py)')
        s = Sequence(home_id, occasion, stem.replace('_', '-'), path, '', '', '', '')
        mod = s.load()
        missing = [k for k in ('CODE', 'TITLE', 'KIND', 'DESCRIPTION', 'render') if not hasattr(mod, k)]
        if missing:
            raise SystemExit(f'{path}: missing {", ".join(missing)}')
        if mod.KIND not in KINDS:
            raise SystemExit(f'{path}: KIND must be one of {", ".join(KINDS)}')
        s.code, s.title, s.kind, s.description = mod.CODE, mod.TITLE, mod.KIND, mod.DESCRIPTION
        out.append(s)
    order = {o: i for i, o in enumerate(BY_ID)}
    out.sort(key=lambda s: (order[s.occasion], s.kind != 'show', s.code))
    codes = [s.code for s in out]
    dup = {c for c in codes if codes.count(c) > 1}
    if dup:
        raise SystemExit(f'{home_id}: duplicate CODE {", ".join(sorted(dup))}')
    return out
