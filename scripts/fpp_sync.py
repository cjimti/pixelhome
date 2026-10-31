#!/usr/bin/env python3
"""Make an FPP player hold exactly what the site has: every sequence, soundtrack and spoken intro from a build,
and playlists for each of the site's playlists, with and without intros. Over FPP's own API (no SSH).

    uv run python -m pixelhome build                      # writes dist/ (sync reads dist/data/catalog.json)
    python3 scripts/fpp_sync.py                           # show the plan
    python3 scripts/fpp_sync.py --apply                   # do it

For each playlist on the site (an occasion's own, or one under it: Nightmare, each Ring opera) it writes:

    "<Label> Music"             the shows with their soundtracks
    "<Label> Music wIntros"     each show after its spoken intro
    "<Label> Loops"             its ambient loops (all night, or all day for Daytime), if it has any

and from the home's show times (dist/data/<home>/schedule.json, from homes/<home>/schedule.py) a playlist for each
kind of night ("Halloween + Nightmare Night (10 sets)": each set's wIntros playlist, the intermissions between) and
FPP's whole schedule: every day and night still to come, the daytime loops, the evening loops until the first show,
the night's playlist at its published time, and the loops again until the next morning.

A playlist that already exists keeps its order (items still on the site stay where they are, new ones go at the
end), so a hand-arranged running order survives a sync. Files are uploaded when missing or a different size.
Then everything else goes: sequences, music and playlists the site doesn't have, and any schedule entry that isn't
one of the home's nights. The sequence and song
FPP is playing right now are never overwritten or deleted; the next sync catches up with them.
"""
import argparse, datetime as dt, json, os, sys, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
q = urllib.parse.quote


class FPP:
    def __init__(self, host):
        self.base = f'http://{host}/api/'

    def call(self, method, path, data=None, ctype='application/json'):
        body = data if isinstance(data, (bytes, type(None))) else json.dumps(data).encode()
        req = urllib.request.Request(self.base + path, data=body, method=method)
        if body is not None:
            req.add_header('Content-Type', ctype)
        with urllib.request.urlopen(req, timeout=600) as r:
            raw = r.read()
        try:
            return json.loads(raw)
        except ValueError:
            return raw

    def get(self, path):
        return self.call('GET', path)


def wanted(dist, home):
    """From the build's catalog: files {dir: {name: local path}} and playlists [(name, desc, items)]."""
    cat = json.load(open(os.path.join(dist, 'data', 'catalog.json')))
    seqs = [m for h in cat['homes'] if h['id'] == home for m in h['sequences']]
    files = {'sequences': {}, 'music': {}}
    for m in seqs:
        files['sequences'][m['fseqName']] = os.path.join(dist, m['fseq'])
        if m.get('audio'):
            files['music'][m['audioName']] = os.path.join(dist, m['audio'])
        if m.get('intro'):
            files['sequences'][m['introName'] + '.fseq'] = os.path.join(dist, m['intro'])
            files['music'][m['introName'] + '.mp3'] = os.path.join(dist, m['introAudio'])

    def item(seq, song, seconds):
        it = dict(type='both' if song else 'sequence', enabled=1, playOnce=0, sequenceName=seq)
        if song:
            it.update(mediaName=song, videoOut='--Default--')
        it.update(timecode='Default', duration=int(round(seconds)))
        return it

    def show(m):
        return item(m['fseqName'], m.get('audioName'), m['seconds'])

    def intro(m):
        return [item(m['introName'] + '.fseq', m['introName'] + '.mp3', m['introFrames'] / m['fps'])] if m.get('intro') else []

    lists = []
    for m in seqs:
        if m['kind'] == 'intermission':
            files['sequences'][m['fseqName']] = os.path.join(dist, m['fseq'])
    for o in cat['occasions']:
        for p in o['playlists']:
            mine = [m for m in seqs if m['playlist'] == p['id']]
            shows = [m for m in mine if m['kind'] == 'show']
            loops = [m for m in mine if m['kind'] == 'ambient']
            label = p['label']
            if shows:
                lists.append((f'{label} Music', f'{label}: the shows with their soundtracks', [show(m) for m in shows]))
                if any(m.get('intro') for m in shows):
                    lists.append((f'{label} Music wIntros', f'{label}: each show after its spoken intro',
                                  [x for m in shows for x in intro(m) + [show(m)]]))
            if loops:
                lists.append((f'{label} Loops', f'{label}: the ambient loops with their soundtracks',
                              [show(m) for m in loops]))
    sched = os.path.join(dist, 'data', home, 'schedule.json')
    return files, lists, (json.load(open(sched)) if os.path.exists(sched) else None), {m['fseqName']: m for m in seqs}


def nights(sched, by_name, now, names):
    """Night playlists [(name, desc, items)] and FPP schedule entries for every night not over yet."""
    lists, entries = {}, []
    t = lambda iso: dt.datetime.fromisoformat(iso)
    hms = lambda d: d.strftime('%H:%M:%S')

    def entry(playlist, start, end, repeat, stop):
        return dict(enabled=1, sequence=0, playlist=playlist, day=7, startTime=hms(start), startTimeOffset=0,
                    endTime=hms(end), endTimeOffset=0, repeat=repeat, startDate=start.date().isoformat(),
                    endDate=start.date().isoformat(), stopType=stop)

    for n in sched['nights']:
        on, off = t(n['lightsOn']), t(n['lightsOff'])
        if off <= now:
            continue
        late = f"{n['late']['label']} Loops"
        entries.append(entry(f"{n['day']['label']} Loops", t(n['dayStart']), on, 1, 1))
        if not n['blocks']:
            entries.append(entry(late, on, off, 1, 0))
            continue
        b0, b1 = t(n['blocks'][0]['start']), t(n['blocks'][-1]['end'])
        b1 = b1.replace(second=0) + dt.timedelta(minutes=1)
        sets = [b for b in n['blocks'] if b['kind'] == 'set']
        labels = list(dict.fromkeys(b['label'] for b in sets))
        name = f"{' + '.join(labels)} Night ({len(sets)} sets)"
        items = []
        for b in n['blocks']:
            if b['kind'] == 'set':
                with_intros = f"{b['label']} Music wIntros"
                items.append(dict(type='playlist', enabled=1, playOnce=0,
                                  name=with_intros if with_intros in names else f"{b['label']} Music"))
            else:
                m = by_name[b['fseqName']]
                items.append(dict(type='both' if m.get('audioName') else 'sequence', enabled=1, playOnce=0,
                                  sequenceName=m['fseqName'], **({'mediaName': m['audioName'], 'videoOut': '--Default--'}
                                                               if m.get('audioName') else {}),
                                  timecode='Default', duration=int(round(m['seconds']))))
        lists[name] = (name, f"{' and '.join(labels)} taking turns, intermissions between", items)
        if on < b0:
            entries.append(entry(late, on, b0, 1, 1))       # hard stop: the show starts on the minute
        entries.append(entry(name, b0, b1, 0, 0))
        entries.append(entry(late, b1, off, 1, 0))
    return list(lists.values()), entries


def keep_order(items, old):
    """items in the order of the existing playlist old (pairs of intro and show stay together), new ones last."""
    if not old:
        return items
    rank = {it.get('sequenceName'): i for i, it in enumerate(old.get('mainPlaylist', []))}
    groups, cur = [], []
    for it in items:                            # an intro and the show after it travel as one
        cur.append(it)
        if not it['sequenceName'].endswith(' intro.fseq'):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    known = [g for g in groups if g[-1]['sequenceName'] in rank]
    new = [g for g in groups if g[-1]['sequenceName'] not in rank]
    known.sort(key=lambda g: rank[g[-1]['sequenceName']])
    return [it for g in known + new for it in g]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--fpp', default='fpp.local')
    ap.add_argument('--home', default='cjimti')
    ap.add_argument('--dist', default=os.path.join(ROOT, 'dist'))
    ap.add_argument('--apply', action='store_true', help='make the changes (default: print the plan)')
    a = ap.parse_args()
    fpp = FPP(a.fpp)
    files, lists, sched, by_name = wanted(a.dist, a.home)
    night_lists, new_sched = nights(sched, by_name, dt.datetime.now().astimezone(), {n for n, _, _ in lists}) if sched else ([], None)
    have = {d: {f['name']: f['sizeBytes'] for f in fpp.get(f'files/{d}')['files']} for d in files}
    status = fpp.get('fppd/status')
    playing = {status.get('current_sequence', ''), status.get('current_song', '')}

    upload = [(d, n, p) for d in files for n, p in sorted(files[d].items())
              if have[d].get(n) != os.path.getsize(p) and n not in playing]
    delete = [(d, n) for d in files for n in sorted(have[d]) if n not in files[d]]
    lists_have = fpp.get('playlists')
    lists_new = {name for name, _, _ in lists + night_lists}
    drop_lists = [p for p in lists_have if p not in lists_new]
    old_sched = fpp.get('schedule')
    if new_sched is None:            # no show times: keep the entries that still point at something
        seq_names = set(files['sequences'])
        new_sched = [e for e in old_sched
                     if (e['playlist'] in seq_names if e.get('sequence') else e['playlist'] in lists_new)]
    sched_changed = new_sched != old_sched

    mb = sum(os.path.getsize(p) for _, _, p in upload) / 1e6
    print(f'upload {len(upload)} files ({mb:.0f} MB); delete {len(delete)} files; write {len(lists) + len(night_lists)} playlists; '
          f'delete {len(drop_lists)} playlists; schedule {len(old_sched)} -> {len(new_sched)} entries'
          + ('' if sched_changed else ' (unchanged)'))
    for d, n, _ in upload:
        print(f'  + {d}/{n}')
    for d, n in delete:
        print(f'  - {d}/{n}' + ('  (playing now: left for the next sync)' if n in playing else ''))
    for name, _, items in lists + night_lists:
        print(f'  = playlist {name} ({len(items)} items)' + ('' if name in lists_have else ', new'))
    for p in drop_lists:
        print(f'  - playlist {p}')
    if sched_changed:
        for e in new_sched:
            print(f"  @ {e['startDate']} {e['startTime'][:5]}-{e['endTime'][:5]} {e['playlist']}")
    if not a.apply:
        print('(plan only: run with --apply)')
        return

    for i, (d, n, p) in enumerate(upload, 1):
        with open(p, 'rb') as f:
            r = fpp.call('POST', f'file/{d}/{q(n)}', f.read(), 'application/octet-stream')
        if not (isinstance(r, dict) and r.get('status') == 'OK'):
            sys.exit(f'upload of {d}/{n} failed: {r}')
        print(f'  [{i}/{len(upload)}] {d}/{n}')
    for name, desc, items in lists + night_lists:
        old = fpp.get(f'playlist/{q(name)}') if name in lists_have else None
        pl = dict(name=name, version=3, repeat=0, loopCount=0, desc=desc, random=0, empty=False, leadIn=[],
                  mainPlaylist=items if (name, desc, items) in night_lists else keep_order(items, old), leadOut=[])
        fpp.call('POST', f'playlist/{q(name)}', pl)
    if sched_changed:
        fpp.call('POST', 'schedule', new_sched)
        fpp.call('POST', 'schedule/reload', b'')
    for p in drop_lists:
        fpp.call('DELETE', f'playlist/{q(p)}')
    for d, n in delete:
        if n not in playing:
            fpp.call('DELETE', f'file/{d}/{q(n)}')
    print('done')


if __name__ == '__main__':
    main()
