"""When the house plays what. The build turns this into the show times on the Live page (data/schedule.json), and
scripts/fpp_sync.py writes the same nights into FPP's scheduler, so the times people read are the times it plays.

The house is never dark: the `day` loops run from DAY[0] until DAY[1], the `late` loops from then until the shows,
and again after them until DAY[0] the next morning. Clock times, not sunset, so the times can be published.

A night's `program` starts at `shows` and runs its steps in order, each straight after the last:
  dict(sets=[playlist, ...])                    those sets, once each
  dict(rotation=[playlist, ...], until='HH:MM')  the playlists take turns until the next set would end past `until`
  dict(sets=[playlist], opener=sequence id)       that set, opened by one show played straight before it
A set is a playlist's shows, each after its spoken intro; every set but the night's first comes after its own
five-minute intermission (an opener plays after it). `note` labels a step's sets on the Live page ('Early show').
With `each_night`, the nights take its entries in turn, and '{each}' in a step stands for that night's (a playlist,
or anything else a step names, such as part of a sequence id).
"""

TIMEZONE = 'America/Los_Angeles'
DAY = ('07:00', '16:30')
FAMILY = ['thanksgiving', 'chef-charlie']   # the family sets, round again between the night's bigger sets

NIGHTS = [
    # the night before Halloween: loops only (the schedule started partway through it)
    dict(dates=('2026-10-30', '2026-10-30'), shows='18:00', day='daytime', late='halloween', program=[]),
    # Halloween night: the two Halloween sets take turns until midnight
    dict(dates=('2026-10-31', '2026-10-31'), shows='18:00', day='daytime', late='halloween',
         program=[dict(rotation=['halloween', 'nightmare'], until='24:00')]),
    # The Ring: an opera a night, round the cycle every four nights, an early show and a late show with the
    # Thanksgiving sets taking turns in between; Elijah straight after the early show (the first three nights, as
    # they played)
    dict(dates=('2026-11-01', '2026-11-03'), shows='17:30', day='daytime', late='thanksgiving',
         each_night=['das-rheingold', 'die-walkure', 'siegfried'],
         program=[dict(sets=['{each}'], note='Early show'),
                  dict(sets=['elijah']),
                  dict(rotation=['thanksgiving', 'chef-charlie'], until='20:30'),
                  dict(sets=['{each}'], note='Late show')]),
    # From then on every night has the same shape: the family sets (Thanksgiving and Chef Charlie) lead, and come
    # round again between the night's early show, Elijah and its late show.
    # The Ring through the eve of Hanukkah, the cycle carrying on from Götterdämmerung
    dict(dates=('2026-11-04', '2026-12-03'), shows='17:30', day='daytime', late='thanksgiving',
         each_night=['gotterdammerung', 'das-rheingold', 'die-walkure', 'siegfried'],
         program=[dict(sets=FAMILY),
                  dict(sets=['{each}'], note='Early show'),
                  dict(sets=FAMILY),
                  dict(sets=['elijah']),
                  dict(sets=FAMILY),
                  dict(sets=['{each}'], note='Late show')]),
    # Hanukkah, eight nights: Judas Maccabaeus is the early and late show, each time opened by that night's
    # candle-lighting
    dict(dates=('2026-12-04', '2026-12-11'), shows='17:30', day='daytime', late='hanukkah',
         each_night=['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth'],
         program=[dict(sets=FAMILY),
                  dict(sets=['judas-maccabaeus'], opener='hanukkah/the-{each}-night', note='Early show'),
                  dict(sets=FAMILY),
                  dict(sets=['elijah']),
                  dict(sets=FAMILY),
                  dict(sets=['judas-maccabaeus'], opener='hanukkah/the-{each}-night', note='Late show')]),
]
