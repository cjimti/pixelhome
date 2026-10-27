"""Occasions a sequence can belong to. A sequence's occasion is the folder it lives in:
homes/<home>/sequences/<occasion>/<sequence>.py. Order here is calendar order; the site starts the list at the next
upcoming one. `date` is MM-DD, approximate for holidays that move (it only drives that ordering).
`prefix` is the CODE prefix new sequences in that occasion use (e.g. XM01..XM10)."""

OCCASIONS = [
    dict(id='new-years', date='01-01', label="New Year's", accent='#f2c14e', prefix='NY'),
    dict(id='mlk-day', date='01-19', label='Martin Luther King Jr. Day', accent='#7fb2ff', prefix='MK'),
    dict(id='valentines', date='02-14', label="Valentine's Day", accent='#ff5d8f', prefix='VD'),
    dict(id='presidents-day', date='02-16', label="Presidents' Day", accent='#5b8def', prefix='PR'),
    dict(id='st-patricks', date='03-17', label="St. Patrick's Day", accent='#3ccb6b', prefix='SP'),
    dict(id='easter', date='04-05', label='Easter', accent='#b794f6', prefix='EA'),
    dict(id='mothers-day', date='05-10', label="Mother's Day", accent='#ff8fb8', prefix='MO'),
    dict(id='memorial-day', date='05-25', label='Memorial Day', accent='#c9d4e8', prefix='MM'),
    dict(id='juneteenth', date='06-19', label='Juneteenth', accent='#e5484d', prefix='JT'),
    dict(id='fathers-day', date='06-21', label="Father's Day", accent='#4fb3bf', prefix='FA'),
    dict(id='independence-day', date='07-04', label='Independence Day', accent='#4f8cff', prefix='IN'),
    dict(id='labor-day', date='09-07', label='Labor Day', accent='#f59e3b', prefix='LB'),
    dict(id='indigenous-peoples-day', date='10-12', label="Indigenous Peoples' Day", accent='#d9823b', prefix='IP'),
    dict(id='halloween', date='10-31', label='Halloween', accent='#ff6a1f', prefix='HW'),
    dict(id='veterans-day', date='11-11', label='Veterans Day', accent='#9fb3c8', prefix='VT'),
    dict(id='thanksgiving', date='11-26', label='Thanksgiving', accent='#d98a3a', prefix='TG'),
    dict(id='christmas', date='12-25', label='Christmas', accent='#e5484d', prefix='XM'),
    dict(id='fun', label='Just for fun', accent='#2ee6c8', prefix='FN'),
]

BY_ID = {o['id']: o for o in OCCASIONS}

KINDS = {
    'show': 'Short, bright pieces meant to be watched.',
    'ambient': 'All-night loops: dim, slow, never dark. Dithered so very low fades stay smooth.',
}
