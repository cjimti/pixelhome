"""Re-string a run: change its pixel count in homes/<home>/home.json, move the start channels after it, and print what
follows from it. The run keeps its ends (first/last positions), so lengths and distances don't change, and neither do
pieces that place things by run name, distance or G.first/last/mid/corners.

The rest of a re-string, in order (homes/cjimti/HARDWARE.md › Re-stringing a run):

    python -m pixelhome restring "Porch Right" 74     # this: home.json
    uv run --group audio python -m pixelhome music --stale         # re-render the soundtracks that moved
    make verify                                                    # build: every FSEQ at the new channel count
    python3 scripts/fpp_sync.py --apply                            # FSEQs onto the player
    python3 scripts/fpp_strings.py --apply                         # the controller's port strings, from home.json
"""
import json, os, re
from . import catalog
from .home import Home


def restring(home_id, run, count):
    path = os.path.join(catalog.HOMES, home_id, 'home.json')
    text = open(path).read()
    spec = json.loads(text)
    segs = {s['name']: s for s in spec['segments']}
    if run not in segs:
        raise SystemExit(f'{home_id}: no run {run!r} (runs: {", ".join(segs)})')
    old = segs[run]['nodes']
    delta = 3 * (count - old)
    if not delta:
        print(f'{run} already has {count} pixels')
        return
    start = segs[run]['start_channel']
    for s in spec['segments']:                      # one block per segment: name, start_channel, nodes, ...
        pat = re.compile(r'("name":\s*' + re.escape(json.dumps(s['name'])) + r',\s*"start_channel":\s*)(\d+)(,\s*"nodes":\s*)(\d+)')
        m = pat.search(text)
        if not m:
            raise SystemExit(f'{path}: expected "name", "start_channel", "nodes" in that order for {s["name"]}')
        ch, n = s['start_channel'] + (delta if s['start_channel'] > start else 0), count if s['name'] == run else s['nodes']
        text = text[:m.start()] + f'{m.group(1)}{ch}{m.group(3)}{n}' + text[m.end():]
    before = sum(s['nodes'] for s in spec['segments'])
    after = before + count - old
    text = re.sub(rf'\b{before} RGB pixels\b', f'{after} RGB pixels', text)
    open(path, 'w').write(text)

    G = Home(os.path.join(catalog.HOMES, home_id))
    print(f'{home_id}: {run} {old} -> {count} pixels; {before} -> {G.N} pixels, {G.channels} channels\n')
    print(f'  {"run":12} {"pixels":>6}  {"channels":>11}  {"path index":>10}  spacing')
    for name, _ in G.path_segments():
        s = next(x for x in G.spec['segments'] if x['name'] == name)
        d = G.pd[G.seg[name]]
        a, b = s['start_channel'], s['start_channel'] + 3 * s['nodes'] - 1
        print(f'  {name:12} {s["nodes"]:>6}  {a:>5}-{b:<5}  {G.first(name):>4}-{G.last(name):<5}  '
              f'{(d.max() - d.min()) / s["nodes"]:.1f}')
    print(f'\n  corners (last path index before each turn): {", ".join(f"{c}|{c + 1}" for c in G.corners)}; '
          f'free ends 0 and {G.N - 1}')
    print('\nNext: music --stale, make verify, fpp_sync.py --apply, fpp_strings.py --apply; then the counts in the '
          "home's README.md and HARDWARE.md and on site/about/hardware/ (index.html, box.js).")
