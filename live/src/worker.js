// Pixelhome Live: relays what the house is playing to the site's viewers.
//
// The Pi POSTs a few bytes of state to /push (what is playing, how far in) whenever it changes and as a
// heartbeat. One Durable Object per house keeps the latest state and sends it to every viewer connected to
// /ws. Viewers never send anything; the site already has every sequence and soundtrack, so it plays the
// same one from the same moment.
//
// Built for the Workers Free plan, where going over a limit makes requests fail instead of billing: the
// objects are SQLite-backed (all Free allows), sockets use the Hibernation API (no duration while idle),
// outgoing messages are free, and viewers' sockets carry nothing inbound.
import { DurableObject } from 'cloudflare:workers';

const HOUSES = ['cjimti'];
const ORIGINS = ['https://pixelhome.app', 'https://www.pixelhome.app', 'http://localhost:8000', 'http://127.0.0.1:8000'];
const MAX_VIEWERS = 250;          // per house; past this new viewers are turned away, not billed
const MIN_PUSH_MS = 500;          // a runaway Pi can't spend the request allowance

export class House extends DurableObject {
  async current() {
    return (await this.ctx.storage.get('state')) || { status: 'offline' };
  }

  // age: how long ago the Pi reported this, so a viewer can work out the position now without clocks agreeing
  view(s) {
    return JSON.stringify({ ...s, age: s.at ? Date.now() - s.at : null, at: undefined });
  }

  async fetch(request) {
    if (this.ctx.getWebSockets().length >= MAX_VIEWERS) return new Response('Too many viewers right now', { status: 503 });
    const [client, server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server);
    server.send(this.view(await this.current()));
    return new Response(null, { status: 101, webSocket: client });
  }

  async push(s) {
    const prev = await this.current();
    const now = Date.now();
    const changed = prev.status !== s.status || prev.seq !== s.seq || prev.song !== s.song;
    if (!changed && prev.at && now - prev.at < MIN_PUSH_MS) return false;
    const state = { ...s, at: now };
    await this.ctx.storage.put('state', state);
    const msg = this.view(state);
    for (const ws of this.ctx.getWebSockets()) {
      try { ws.send(msg); } catch (e) { /* closing */ }
    }
    return true;
  }

  async state() {
    return { ...JSON.parse(this.view(await this.current())), viewers: this.ctx.getWebSockets().length };
  }

  webSocketMessage() { /* viewers don't talk */ }

  webSocketClose(ws, code) {
    try { ws.close(code === 1005 ? 1000 : code, 'bye'); } catch (e) { /* already closed */ }
  }
}

function same(a, b) {
  const x = new TextEncoder().encode(a), y = new TextEncoder().encode(b);
  if (x.length !== y.length) return false;
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x[i] ^ y[i];
  return d === 0;
}

const str = (v, n) => (typeof v === 'string' ? v.slice(0, n) : '');

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const [, route, house] = url.pathname.split('/');
    if (!HOUSES.includes(house)) return new Response('Not found', { status: 404 });
    const stub = env.HOUSE.getByName(house);
    const origin = request.headers.get('Origin');
    const cors = ORIGINS.includes(origin) ? { 'Access-Control-Allow-Origin': origin, Vary: 'Origin' } : {};

    if (route === 'ws') {
      if (request.headers.get('Upgrade') !== 'websocket') return new Response('Expected a WebSocket', { status: 426 });
      if (!ORIGINS.includes(origin)) return new Response('Forbidden', { status: 403 });
      return stub.fetch(request);
    }

    if (route === 'push' && request.method === 'POST') {
      const auth = request.headers.get('Authorization') || '';
      if (!env.PUSH_TOKEN || !same(auth, `Bearer ${env.PUSH_TOKEN}`)) return new Response('Unauthorized', { status: 401 });
      const body = await request.text();
      if (body.length > 2048) return new Response('Too large', { status: 413 });
      let s;
      try { s = JSON.parse(body); } catch (e) { return new Response('Bad JSON', { status: 400 }); }
      const ok = await stub.push({
        status: s.status === 'playing' ? 'playing' : 'idle',
        seq: str(s.seq, 200), song: str(s.song, 200), playlist: str(s.playlist, 200),
        ms: Number.isFinite(s.ms) ? Math.max(0, Math.round(s.ms)) : 0,
      });
      return new Response(ok ? 'ok' : 'skipped');
    }

    if (route === 'state' && request.method === 'GET') {
      return Response.json(await stub.state(), { headers: { ...cors, 'Cache-Control': 'no-store' } });
    }

    return new Response('Not found', { status: 404 });
  },
};
