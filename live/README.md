# Pixelhome Live

The **Live** button on pixelhome.app (or `pixelhome.app/#live`) plays whatever the house is playing right
now, lights and soundtrack, from the same moment. No video or audio is streamed: the site already has every
sequence and MP3, so all that travels is a few bytes saying which file FPP is on and how far in.

```
FPP (Pi) --POST /push/<house>, on change + heartbeat--> Worker --> Durable Object "House" --WebSocket--> viewers
```

- `pi/pixelhome-live.py`: runs on the Pi as a systemd service. Reads `127.0.0.1/api/fppd/status` once a
  second; sends on a change of sequence, start/stop or a jump in position, plus every 30 s while playing
  and every minute while idle. Outbound only.
- `src/worker.js`: the relay (`live.pixelhome.app`). `/push/<house>` needs the `PUSH_TOKEN` secret;
  `/ws/<house>` takes viewers from pixelhome.app (and localhost:8000); `/state/<house>` returns the state as JSON.
- The site matches FPP's file names against the catalog (`fseqName`, and `introName` + `.fseq` for intros),
  so the files in the FPP playlist must be the ones uploaded from the site. Anything else shows as "not on this site".

## Staying free

It runs on the Workers **Free** plan, where hitting a daily limit makes requests fail until 00:00 UTC
instead of billing. Nothing here can create a charge as long as the account is on the Free plan; a bill is
only possible after subscribing to Workers Paid. A night costs roughly 2,000 pushes plus one request per
viewer visit, against 100,000 requests a day. The objects are SQLite-backed (the only kind Free allows),
viewer sockets hibernate (no duration charged while waiting) and send nothing inbound, and the Worker caps
viewers per house (`MAX_VIEWERS`) and ignores pushes closer than 0.5 s apart.

## Setup

```sh
cd live && npm install
npx wrangler login
npx wrangler deploy                                   # creates the Worker and live.pixelhome.app
python3 install_pi.py                                 # first run makes ~/.config/pixelhome/live-token
npx wrangler secret put PUSH_TOKEN < ~/.config/pixelhome/live-token
```

`install_pi.py` installs over FPP's API (upload to the scripts folder, then "Run Script"); run it again to
update the Pi after changing `pi/pixelhome-live.py`. On the Pi: `systemctl status pixelhome-live`.
Locally: `npx wrangler dev --port 8788` with `PUSH_TOKEN=...` in `.dev.vars`.
