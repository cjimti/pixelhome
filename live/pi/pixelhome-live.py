#!/usr/bin/env python3
"""Pixelhome Live, the Pi side: reads FPP's status once a second and tells the Live relay what is playing.

It sends only when something changes (a new sequence, start, stop, a jump in position) plus a heartbeat:
every 30 s while playing, every minute while idle. That's around two thousand small requests a day.
Connections go out from the Pi only; nothing on the Pi is opened to the internet.

Config: /home/fpp/media/config/pixelhome-live.json {"url": "https://live.pixelhome.app/push/<house>", "token": "..."}
"""
import json, time, urllib.request

CONF = '/home/fpp/media/config/pixelhome-live.json'
STATUS = 'http://127.0.0.1/api/fppd/status'
BEAT_PLAYING, BEAT_IDLE, JUMP_MS = 30, 60, 1500


def read_status():
    with urllib.request.urlopen(STATUS, timeout=3) as r:
        d = json.load(r)
    playing = d.get('status_name') == 'playing'
    ms = d.get('milliseconds_elapsed')
    if not isinstance(ms, (int, float)):
        ms = float(d.get('seconds_played') or 0) * 1000
    pl = d.get('current_playlist') or {}
    return dict(status='playing' if playing else 'idle',
                seq=(d.get('current_sequence') or '') if playing else '',
                song=(d.get('current_song') or '') if playing else '',
                playlist=(pl.get('playlist') or '') if playing else '',
                ms=int(ms) if playing else 0)


def send(conf, s):
    req = urllib.request.Request(conf['url'], data=json.dumps(s).encode(), method='POST',
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer ' + conf['token'],
                                          'User-Agent': 'pixelhome-live/1'})
    with urllib.request.urlopen(req, timeout=10) as r:
        r.read()


def main():
    with open(CONF) as f:
        conf = json.load(f)
    last, sent_at, retry_at = None, 0.0, 0.0
    while True:
        t0 = time.monotonic()
        try:
            s = read_status()
        except Exception:
            s = None                       # fppd restarting; try again next second
        if s is not None and t0 >= retry_at:
            key = (s['status'], s['seq'], s['song'])
            beat = BEAT_PLAYING if s['status'] == 'playing' else BEAT_IDLE
            due = last is None or key != last[0] or t0 - sent_at >= beat
            if not due and s['status'] == 'playing':
                expected = last[1] + (t0 - last[2]) * 1000
                due = abs(s['ms'] - expected) > JUMP_MS
            if due:
                try:
                    send(conf, s)
                    last, sent_at = (key, s['ms'], t0), t0
                except Exception as e:
                    print('push failed:', e, flush=True)
                    retry_at = t0 + 15         # back off; the relay or the network is down
        time.sleep(max(0.0, 1.0 - (time.monotonic() - t0)))


if __name__ == '__main__':
    main()
