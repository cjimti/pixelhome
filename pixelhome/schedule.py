"""Show nights: a home's schedule.py worked out against the catalog into exact times (data/schedule.json).

Every set is its playlist's shows, each after its spoken intro, in catalog order; an intermission is the playlist's
`intermission` sequence. A set may have an opener: one show (a sequence id) played after the set's intermission and
straight before it, as Hanukkah's candle-lighting show opens a night's Judas Maccabaeus. FPP takes a moment between items (measured at about 0.17 s on the cjimti player), which
adds up over a night, so it is counted in.
"""
import datetime as dt, importlib.util, os
from zoneinfo import ZoneInfo
from . import catalog
from .occasions import PLAYLIST

GAP = 0.17          # seconds FPP takes between playlist items


def load(home):
    path = os.path.join(catalog.HOMES, home, 'schedule.py')
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location(f'pixelhome_schedule_{home}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _at(day, hhmm, tz):
    h, m = map(int, hhmm.split(':'))
    return dt.datetime.combine(day, dt.time(0), tz) + dt.timedelta(hours=h, minutes=m)


def _iso(t):
    return t.isoformat(timespec='seconds')


def lengths(metas):
    """playlist -> dict(set=seconds, items=n, intermission=meta or None) from the catalog's sequences."""
    out = {}
    for m in metas:
        p = out.setdefault(m['playlist'], dict(set=0.0, items=0, intermission=None))
        if m['kind'] == 'show':
            p['set'] += m['seconds'] + (m['introFrames'] / m['fps'] if m.get('intro') else 0)
            p['items'] += 1 + bool(m.get('intro'))
        elif m['kind'] == 'intermission':
            p['intermission'] = m
    return out


def nights(home, metas):
    """The home's nights with every set and intermission timed, or None if it has no schedule."""
    mod = load(home)
    if mod is None:
        return None
    tz = ZoneInfo(mod.TIMEZONE)
    plen = lengths(metas)
    by_id = {m['id']: m for m in metas}
    out = []

    def info(pl):
        if pl not in PLAYLIST:
            raise SystemExit(f'{home}/schedule.py: unknown playlist {pl!r}')
        return dict(playlist=pl, label=PLAYLIST[pl]['label'], occasion=PLAYLIST[pl]['occasion'],
                    accent=PLAYLIST[pl]['accent'])

    for spec in mod.NIGHTS:
        d0, d1 = (dt.date.fromisoformat(d) for d in spec['dates'])
        for k in range((d1 - d0).days + 1):
            day = d0 + dt.timedelta(days=k)
            each = spec['each_night'][k % len(spec['each_night'])] if 'each_night' in spec else None
            t = _at(day, spec['shows'], tz)
            blocks = []

            def add(pl, note, until=None, opener=None):
                """Time the next set (after its intermission if it isn't the first, then its opener if it has one);
                False if it would end late."""
                nonlocal t
                if pl not in plen or not plen[pl]['set']:
                    raise SystemExit(f'{home}/schedule.py: no shows with music in playlist {pl!r}')
                op = None
                if opener:
                    op = by_id.get(opener)
                    if op is None or op['kind'] != 'show':
                        raise SystemExit(f'{home}/schedule.py: no show with music {opener!r} to open {pl!r}')
                im = plen[pl]['intermission'] if blocks else None
                run = plen[pl]['set'] + GAP * (plen[pl]['items'] + 1)
                op_run = (op['seconds'] + (op['introFrames'] / op['fps'] if op.get('intro') else 0)
                          + GAP * (2 + bool(op.get('intro')))) if op else 0
                if until is not None and t + dt.timedelta(seconds=(im['seconds'] + GAP if im else 0) + op_run + run) > until:
                    return False
                if im:
                    end = t + dt.timedelta(seconds=im['seconds'] + GAP)
                    blocks.append(dict(info(pl), kind='intermission', start=_iso(t), end=_iso(end),
                                       fseqName=im['fseqName']))
                    t = end
                if op:
                    end = t + dt.timedelta(seconds=op_run)
                    blocks.append(dict(info(op['playlist']), kind='show', id=op['id'], label=op['title'],
                                       start=_iso(t), end=_iso(end), fseqName=op['fseqName']))
                    t = end
                end = t + dt.timedelta(seconds=run)
                blocks.append(dict(info(pl), kind='set', start=_iso(t), end=_iso(end)))
                if note:
                    blocks[-1]['note'] = note
                t = end
                return True

            for step in spec['program']:
                name = lambda pl: pl and (pl.replace('{each}', each) if each else pl)
                if 'sets' in step:
                    for pl in step['sets']:
                        add(name(pl), step.get('note'), opener=name(step.get('opener')))
                else:
                    until = _at(day, step['until'], tz)
                    i = 0
                    while add(name(step['rotation'][i % len(step['rotation'])]), step.get('note'), until):
                        i += 1
            out.append(dict(date=day.isoformat(),
                            dayStart=_iso(_at(day, mod.DAY[0], tz)), lightsOn=_iso(_at(day, mod.DAY[1], tz)),
                            lightsOff=_iso(_at(day + dt.timedelta(days=1), mod.DAY[0], tz)),
                            day=info(spec['day']), late=info(spec['late']), blocks=blocks))
    return dict(home=home, timezone=mod.TIMEZONE, nights=out)
