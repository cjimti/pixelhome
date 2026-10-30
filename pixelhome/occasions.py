"""Occasions and their playlists. A sequence lives in homes/<home>/sequences/<playlist>/<sequence>.py; the folder
is its playlist, and every playlist belongs to an occasion. An occasion's own id is also a playlist (its main one,
e.g. halloween/), and PLAYLISTS adds others under it (the Nightmare Before Christmas under Halloween, each Ring
opera under the Ring Cycle). The folder stays in a sequence's id (<playlist>/<name>), so moving a playlist to
another occasion changes no ids, links or file paths.

Order here is calendar order; the site starts the list at the next upcoming occasion. `date` is MM-DD,
approximate for holidays that move (it only drives that ordering). `prefix` is the CODE prefix new sequences in a
playlist use (e.g. XM01..XM10)."""

OCCASIONS = [
    dict(id='new-years', date='01-01', label="New Year's", accent='#f2c14e', prefix='NY'),
    dict(id='valentines', date='02-14', label="Valentine's Day", accent='#ff5d8f', prefix='VD'),
    dict(id='presidents-day', date='02-16', label="Presidents' Day", accent='#5b8def', prefix='PR'),
    dict(id='st-patricks', date='03-17', label="St. Patrick's Day", accent='#3ccb6b', prefix='SP'),
    dict(id='easter', date='04-05', label='Easter', accent='#b794f6', prefix='EA'),
    dict(id='mothers-day', date='05-10', label="Mother's Day", accent='#ff8fb8', prefix='MO'),
    dict(id='memorial-day', date='05-25', label='Memorial Day', accent='#c9d4e8', prefix='MM'),
    dict(id='fathers-day', date='06-21', label="Father's Day", accent='#4fb3bf', prefix='FA'),
    dict(id='independence-day', date='07-04', label='Independence Day', accent='#4f8cff', prefix='IN'),
    dict(id='ring-cycle', date='08-13', label='Ring Cycle', accent='#e8b923'),   # Bayreuth, 13 August 1876
    dict(id='labor-day', date='09-07', label='Labor Day', accent='#f59e3b', prefix='LB'),
    dict(id='halloween', date='10-31', label='Halloween', accent='#ff6a1f', prefix='HW'),
    dict(id='veterans-day', date='11-11', label='Veterans Day', accent='#9fb3c8', prefix='VT'),
    dict(id='thanksgiving', date='11-26', label='Thanksgiving', accent='#d98a3a', prefix='TG'),
    dict(id='christmas', date='12-25', label='Christmas', accent='#e5484d', prefix='XM'),
    dict(id='other', label='Other', accent='#2ee6c8', prefix='OT'),
]

# Playlists besides each occasion's own, in the order they list under it.
PLAYLISTS = [
    dict(id='nightmare-before-christmas', occasion='halloween', label='The Nightmare Before Christmas',
         accent='#7fd13b', prefix='NB'),
    dict(id='das-rheingold', occasion='ring-cycle', label='Das Rheingold', accent='#e8b923', prefix='RG'),
    dict(id='die-walkure', occasion='ring-cycle', label='Die Walküre', accent='#e2502c', prefix='WK'),
    dict(id='siegfried', occasion='ring-cycle', label='Siegfried', accent='#20e050', prefix='SF'),
]

BY_ID = {o['id']: o for o in OCCASIONS}
PLAYLIST = {o['id']: dict(o, occasion=o['id']) for o in OCCASIONS}     # playlist id -> its occasion, label, accent
PLAYLIST.update({p['id']: p for p in PLAYLISTS})


def playlists(occasion):
    """Playlist ids of an occasion, its own first."""
    return [occasion] + [p['id'] for p in PLAYLISTS if p['occasion'] == occasion]


KINDS = {
    'show': 'Short, bright pieces meant to be watched.',
    'ambient': 'All-night loops: dim, slow, never dark. Dithered so very low fades stay smooth.',
}
