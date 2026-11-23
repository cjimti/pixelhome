#!/usr/bin/env python3
"""Set the controller's pixel-port strings from home.json: each virtual string named for a run gets that run's pixel
count and start channel, and no null nodes (the F-Amps at the start of each port amplify the data without taking a
pixel's worth of it). Everything else on the ports stays as it is (which port a run is on, its order, brightness,
gamma, colour order). Over FPP's API (no SSH).

    python3 scripts/fpp_strings.py              # show what would change
    python3 scripts/fpp_strings.py --apply      # change it and restart fppd

Run it after `fpp_sync.py --apply` has put FSEQs with the new channel count on the player (homes/cjimti/HARDWARE.md ›
Re-stringing a run).
"""
import argparse, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = 'channel/output/co-bbbStrings'


def call(base, method, path, data=None):
    req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(), method=method)
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--home', default='cjimti')
    ap.add_argument('--fpp', help="the player's host (default: home.json's controller host)")
    ap.add_argument('--apply', action='store_true', help='make the changes and restart fppd (default: print the plan)')
    a = ap.parse_args()
    spec = json.load(open(os.path.join(ROOT, 'homes', a.home, 'home.json')))
    base = f'http://{a.fpp or spec["controller"]["host"]}/api/'
    want = {s['name']: (s['nodes'], s['start_channel'] - 1) for s in spec['segments']}   # FPP counts channels from 0

    cfg = call(base, 'GET', PATH)
    seen, changes = {}, []
    for out in cfg['channelOutputs']:
        for port in out['outputs']:
            for vs in port['virtualStrings']:
                name = vs.get('description', '')
                if name not in want:
                    if vs.get('pixelCount'):
                        sys.exit(f'port {port["portNumber"] + 1}: string {name!r} has pixels but no run in home.json')
                    continue
                seen[name] = seen.get(name, 0) + 1
                n, ch = want[name]
                if (vs['pixelCount'], vs['startChannel']) != (n, ch):
                    changes.append(f'port {port["portNumber"] + 1} {name}: {vs["pixelCount"]} pixels at channel '
                                   f'{vs["startChannel"] + 1} -> {n} at {ch + 1}')
                    vs['pixelCount'], vs['startChannel'] = n, ch
                if vs.get('nullNodes') or vs.get('endNulls'):
                    changes.append(f'port {port["portNumber"] + 1} {name}: {vs.get("nullNodes", 0)} null nodes, '
                                   f'{vs.get("endNulls", 0)} end nulls -> none')
                    vs['nullNodes'], vs['endNulls'] = 0, 0
    missing = [n for n in want if seen.get(n) != 1]
    if missing:
        sys.exit('each run needs exactly one virtual string named for it; check: ' + ', '.join(missing))
    if not changes:
        print('the port strings already match home.json')
        return
    print('\n'.join(changes))
    if not a.apply:
        print('(plan only; --apply to change it)')
        return
    call(base, 'POST', PATH, cfg)
    call(base, 'GET', 'system/fppd/restart')
    print('applied; fppd restarting')


if __name__ == '__main__':
    main()
