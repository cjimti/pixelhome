"""Occasions and their playlists. A sequence lives in homes/<home>/sequences/<playlist>/<sequence>.py; the folder
is its playlist, and every playlist belongs to an occasion. An occasion's own id is also a playlist (its main one,
e.g. halloween/), and PLAYLISTS adds others under it (the Nightmare Before Christmas under Halloween, each Ring
opera under the Ring Cycle). The folder stays in a sequence's id (<playlist>/<name>), so moving a playlist to
another occasion changes no ids, links or file paths.

Order here is calendar order; the site starts the list at the next upcoming occasion. `date` is MM-DD,
approximate for holidays that move (it only drives that ordering). `prefix` is the CODE prefix new sequences in a
playlist use (e.g. XM01..XM10). `desc` describes a playlist (for an occasion, its own playlist) on the site and
the Live page; `set` names an occasion's own playlist when it isn't the occasion's name (Halloween Variety)."""

OCCASIONS = [
    dict(id='new-years', date='01-01', label="New Year's", accent='#f2c14e', prefix='NY',
         desc='Countdowns, champagne and confetti to ring in the year.'),
    dict(id='valentines', date='02-14', label="Valentine's Day", accent='#ff5d8f', prefix='VD',
         desc='Hearts, roses and love letters for the sweethearts on the street.'),
    dict(id='presidents-day', date='02-16', label="Presidents' Day", accent='#5b8def', prefix='PR',
         desc='Stars, columns and history in red, white and blue.'),
    dict(id='st-patricks', date='03-17', label="St. Patrick's Day", accent='#3ccb6b', prefix='SP',
         desc='Shamrocks, rainbows and a little luck of the Irish.'),
    dict(id='easter', date='04-05', label='Easter', accent='#b794f6', prefix='EA',
         desc='Spring colours, painted eggs and a bunny or two.'),
    dict(id='mothers-day', date='05-10', label="Mother's Day", accent='#ff8fb8', prefix='MO',
         desc='Bouquets, breakfast in bed and a big hug for Mom.'),
    dict(id='memorial-day', date='05-25', label='Memorial Day', accent='#c9d4e8', prefix='MM',
         desc='Quiet tributes to those who gave everything.'),
    dict(id='fathers-day', date='06-21', label="Father's Day", accent='#4fb3bf', prefix='FA',
         desc='Road trips, grills and dad jokes, for Dad.'),
    dict(id='independence-day', date='07-04', label='Independence Day', accent='#4f8cff', prefix='IN',
         desc='Fireworks, bells and Old Glory for the Fourth.'),
    dict(id='ring-cycle', date='08-13', label='Ring Cycle', accent='#e8b923',
         desc="Wagner's Ring told across the roofline, opera by opera."),   # Bayreuth, 13 August 1876
    dict(id='labor-day', date='09-07', label='Labor Day', accent='#f59e3b', prefix='LB',
         desc='Mills, freight trains and the people who build things.'),
    dict(id='halloween', date='10-31', label='Halloween', accent='#ff6a1f', prefix='HW',
         desc='Spooky-fun originals: ghosts, bats, bones and a few frights.', set='Halloween Variety'),
    dict(id='veterans-day', date='11-11', label='Veterans Day', accent='#9fb3c8', prefix='VT',
         desc='Honouring everyone who served.'),
    dict(id='thanksgiving', date='11-26', label='Thanksgiving', accent='#d98a3a', prefix='TG',
         desc='Turkeys, pies, parades and the whole family round the table.', set='Thanksgiving Variety'),
    dict(id='christmas', date='12-25', label='Christmas', accent='#e5484d', prefix='XM',
         desc='Classic bulbs, snow and a few Christmas capers.'),
    dict(id='other', label='Other', accent='#2ee6c8', prefix='OT',
         desc='Everything else: colour, nature and light for any night.'),
]

# Playlists besides each occasion's own, in the order they list under it.
PLAYLISTS = [
    dict(id='nightmare', occasion='halloween', label='Nightmare', accent='#7fd13b', prefix='NM',
         desc="Jack Skellington's story retold in twenty scenes, with original music."),
    dict(id='chef-charlie', occasion='thanksgiving', label='Chef Charlie', accent='#f2c200', prefix='CC',
         desc="Charlie Brown, chef Snoopy and a backyard feast of toast and popcorn, retold scene by scene."),
    dict(id='daytime', occasion='other', label='Daytime', accent='#8fd3ff', prefix='DY',
         desc='Something mellow for the daylight hours, until the shows start tonight.'),
    dict(id='das-rheingold', occasion='ring-cycle', label='Das Rheingold', accent='#e8b923', prefix='RG',
         desc='The gold is stolen from the Rhine, and the gods take Valhalla.'),
    dict(id='die-walkure', occasion='ring-cycle', label='Die Walküre', accent='#e2502c', prefix='WK',
         desc='The Volsung twins, the Ride of the Valkyries and the magic fire.'),
    dict(id='siegfried', occasion='ring-cycle', label='Siegfried', accent='#20e050', prefix='SF',
         desc='Siegfried forges the sword, slays the dragon and wakes Brünnhilde.'),
    dict(id='gotterdammerung', occasion='ring-cycle', label='Götterdämmerung', accent='#a040ff', prefix='GD',
         desc="Betrayal, the death of the hero and the gods' Valhalla in flames."),
]

BY_ID = {o['id']: o for o in OCCASIONS}
# playlist id -> its occasion, label, accent, desc
PLAYLIST = {o['id']: dict(o, occasion=o['id'], label=o.get('set', o['label'])) for o in OCCASIONS}
PLAYLIST.update({p['id']: p for p in PLAYLISTS})


def playlists(occasion):
    """Playlist ids of an occasion, its own first."""
    return [occasion] + [p['id'] for p in PLAYLISTS if p['occasion'] == occasion]


KINDS = {
    'show': 'Short, bright pieces meant to be watched.',
    'ambient': 'All-night loops: dim, slow, never dark. Dithered so very low fades stay smooth.',
    'intermission': 'Five minutes between shows: the house stays lit and counts down to the next one.',
}
