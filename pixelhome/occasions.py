"""Occasions a sequence can belong to. A sequence's occasion is the folder it lives in:
homes/<home>/sequences/<occasion>/<sequence>.py. Order here is the order on the site."""

OCCASIONS = [
    dict(id='halloween', label='Halloween', accent='#ff6a1f'),
    dict(id='christmas', label='Christmas', accent='#e5484d'),
    dict(id='new-years', label="New Year's", accent='#f2c14e'),
    dict(id='valentines', label="Valentine's Day", accent='#ff5d8f'),
    dict(id='st-patricks', label="St. Patrick's Day", accent='#3ccb6b'),
    dict(id='easter', label='Easter', accent='#b794f6'),
    dict(id='independence-day', label='Independence Day', accent='#4f8cff'),
    dict(id='thanksgiving', label='Thanksgiving', accent='#d98a3a'),
    dict(id='fun', label='Just for fun', accent='#2ee6c8'),
]

BY_ID = {o['id']: o for o in OCCASIONS}

KINDS = {
    'show': 'Short, bright pieces meant to be watched.',
    'ambient': 'All-night loops: dim, slow, never dark. Dithered so very low fades stay smooth.',
}
