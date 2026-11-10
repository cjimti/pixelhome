"""Render one sequence, and work out what a render depends on so the build can cache it.

A render's output depends on the sequence's module, the files beside it that share its name or that it names (its
`.score.json`, another scene's excerpt), the `pixelhome` modules it imports at module level and theirs, this module
and its own imports, the home and the locked packages. `deps()` finds those files; imports made inside a function
aren't followed (in this code they fetch audio constants for score()), so a render must import what it needs at the top.
"""
import ast, functools, hashlib, os, time
import numpy as np
from PIL import Image
from . import fseq, power
from .fx import DT, to_bytes, to_bytes_dithered

PKG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PKG)
WEB_MAX_SECONDS = 120        # longer sequences go to the web player at half frame rate
MAX_SECONDS = 15 * 60


def frames(s, home):
    """One sequence -> float frames (F, N, 3), checked."""
    out = np.asarray(s.load().render(home))
    if out.ndim != 3 or out.shape[1:] != (home.N, 3):
        raise ValueError(f'{s.path}: render returned {out.shape}, expected (frames, {home.N}, 3)')
    if not np.isfinite(out).all():
        raise ValueError(f'{s.path}: render returned NaN or inf')
    if not 1 <= len(out) * DT <= MAX_SECONDS:
        raise ValueError(f'{s.path}: {len(out) * DT:.1f}s is outside 1s..{MAX_SECONDS}s')
    return power.night(home, out, s.id) if power.is_night_loop(s) else out


def write(s, home, dest):
    """Render a sequence into dest/ as seq.fseq, seq.png and meta.json."""
    t0 = time.time()
    data = frames(s, home)
    data = to_bytes_dithered(data) if s.kind == 'ambient' else to_bytes(data)
    step = int(round(DT * 1000))
    fseq.write(os.path.join(dest, 'seq.fseq'), data, step)
    every = 2 if len(data) * DT > WEB_MAX_SECONDS else 1
    web = data[::every]
    Image.fromarray(web.reshape(len(web), -1, 3), 'RGB').save(os.path.join(dest, 'seq.png'), optimize=True)
    return dict(id=s.id, code=s.code, title=s.title, occasion=s.occasion, kind=s.kind, description=s.description,
                seconds=round(len(data) * DT, 2), fps=round(1000 / (step * every)), frames=len(web),
                fseq=f'fseq/{s.home}/{s.id}.fseq', fseqName=f'{s.code} {s.title}.fseq',
                fseqBytes=os.path.getsize(os.path.join(dest, 'seq.fseq')),
                data=f'data/{s.home}/{s.id}.png', renderSeconds=round(time.time() - t0, 2))


# ---------------------------------------------------------------------------- what a render depends on

def _module_level(tree):
    """The nodes that run when a module is imported: everything but the insides of functions."""
    todo = list(tree.body)
    while todo:
        node = todo.pop()
        yield node
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            todo += list(ast.iter_child_nodes(node))


@functools.lru_cache(maxsize=None)
def _scan(path):
    """(pixelhome module files path imports at module level, the strings it contains)."""
    tree = ast.parse(open(path, 'rb').read(), path)
    in_pkg = os.path.dirname(os.path.abspath(path)) == PKG
    mod = lambda name: os.path.join(PKG, name + '.py')
    found = set()
    for node in _module_level(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == 'pixelhome' or a.name.startswith('pixelhome.'):
                    found.add(mod(a.name.split('.', 1)[1]) if '.' in a.name else mod('__init__'))
        elif isinstance(node, ast.ImportFrom):
            if node.level == 1 and in_pkg:
                base = node.module
            elif node.level == 0 and node.module and (node.module + '.').startswith('pixelhome.'):
                base = node.module[len('pixelhome.'):] if '.' in node.module else None
            else:
                continue
            if base:
                found.add(mod(base))
            else:                                   # from pixelhome import fx, ring / from . import fx
                found.add(mod('__init__'))
                found.update(mod(a.name) for a in node.names)
    if found:
        found.add(mod('__init__'))
    strings = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    return frozenset(p for p in found if os.path.exists(p)), frozenset(strings)


def deps(*paths):
    """Every file the given sequence (or pixelhome) modules depend on, sorted."""
    seen, todo = set(), [os.path.abspath(p) for p in paths]
    while todo:
        p = todo.pop()
        if p in seen:
            continue
        seen.add(p)
        if not p.endswith('.py'):
            continue
        imports, strings = _scan(p)
        todo += imports
        d = os.path.dirname(p)
        if d != PKG:                                # a sequence: what's beside it with its name, or named in it
            stem = os.path.basename(p)[:-3]
            for f in os.listdir(d):
                first = f.split('.')[0]
                if os.path.isfile(os.path.join(d, f)) and (first == stem or f in strings or first + '.py' in strings):
                    todo.append(os.path.join(d, f))
    return sorted(seen)


@functools.lru_cache(maxsize=None)
def digest(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def key(kind, *paths):
    """A cache key for output made from these files and everything they depend on."""
    h = hashlib.sha256(kind.encode() + b'\0')
    for p in sorted(set(deps(*paths)) | {os.path.join(ROOT, 'uv.lock')}):
        h.update(os.path.relpath(p, ROOT).encode() + b'\0' + digest(p).encode() + b'\0')
    return h.hexdigest()[:40]
