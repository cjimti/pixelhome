// Live: the house as it is right now, for someone standing in front of it with a phone.
// The Pi tells live.pixelhome.app which file FPP is playing and how far in; this page already has every
// sequence and soundtrack, so it plays the same one from the same moment. Nothing is sent from here.
// With the music on, the lights follow the phone's own audio (so they match what you hear), and only the
// audio is nudged toward the house, gently, because phones cut out on every seek.
(async function () {
  const $ = (id) => document.getElementById(id);
  const ROOT = '../';
  const HOUSE = 'cjimti';
  const RELAY = `wss://live.pixelhome.app/ws/${HOUSE}`;
  const track = (name, params = {}) => { try { if (window.gtag) gtag('event', name, params); } catch (e) { /* analytics blocked */ } };
  const msg = (text) => { $('msg').hidden = !text; $('msg').textContent = text || ''; };

  let CAT, home, layout;
  try {
    CAT = await (await fetch(ROOT + 'data/catalog.json')).json();
    home = CAT.homes.find((h) => h.id === HOUSE);
    layout = await (await fetch(ROOT + home.layout)).json();
  } catch (e) {
    msg('Could not load the house. Reload the page to try again.');
    return;
  }
  const accents = Object.fromEntries(CAT.occasions.map((o) => [o.id, o.accent]));

  // ---------- the house (the same scene as the main page, from the street, still) ----------
  const canvas = $('view');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x060504);
  const camera = new THREE.PerspectiveCamera(38, 16 / 9, 10, 40000);
  scene.add(new THREE.AmbientLight(0x2c3038, 0.55));
  const moon = new THREE.DirectionalLight(0x7f90b8, 0.32);
  moon.position.set(-0.6, 1.4, 0.8);
  scene.add(moon);
  function glowTexture(stops) {
    const c = document.createElement('canvas');
    c.width = c.height = 64;
    const g = c.getContext('2d');
    const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    stops.forEach(([o, a]) => grad.addColorStop(o, `rgba(255,255,255,${a})`));
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    return new THREE.CanvasTexture(c);
  }
  const GLOWS = [
    [150, glowTexture([[0, 0.5], [0.25, 0.18], [1, 0]]), 0.22],
    [40, glowTexture([[0, 1], [0.35, 0.35], [1, 0]]), 0.55],
    [8, glowTexture([[0, 1], [0.6, 0.9], [1, 0]]), 1],
  ];
  const P = layout.pixels, N = P.length / 3;
  let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity, ySum = 0;
  for (let k = 0; k < N; k++) {
    x0 = Math.min(x0, P[k*3]); x1 = Math.max(x1, P[k*3]);
    z0 = Math.min(z0, P[k*3+2]); z1 = Math.max(z1, P[k*3+2]);
    ySum += P[k*3+1];
  }
  const span = Math.max(x1 - x0, z1 - z0, 1);
  const target = new THREE.Vector3((x0 + x1) / 2, ySum / N - 40 * span / 1224, (z0 + z1) / 2 - 0.08 * (z1 - z0));
  scene.fog = new THREE.Fog(0x060504, 2.1 * span, 5.3 * span);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(span * 8, span * 8), new THREE.MeshLambertMaterial({ color: 0x0d0c0b }));
  ground.rotation.x = -Math.PI / 2;
  ground.position.set(target.x, 0, target.z);
  scene.add(ground);
  if (layout.meshVerts.length) {
    const hg = new THREE.BufferGeometry();
    hg.setAttribute('position', new THREE.Float32BufferAttribute(layout.meshVerts, 3));
    hg.setIndex(layout.meshTris);
    const geo = hg.toNonIndexed();
    geo.computeVertexNormals();
    scene.add(new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ color: 0x2b2521, side: THREE.DoubleSide })));
  }
  const runs = [];
  for (let k = 1, start = 0; k <= N; k++) {
    const gap = k === N ? Infinity : Math.hypot(P[k*3]-P[k*3-3], P[k*3+1]-P[k*3-2], P[k*3+2]-P[k*3-1]);
    if (gap > 30) {
      const mid = Math.floor((start + k - 1) / 2);
      const light = new THREE.PointLight(0x000000, 0, 650 * span / 1224, 1.4);
      light.position.set(P[mid*3], P[mid*3+1] - 25, P[mid*3+2] + 40);
      scene.add(light);
      runs.push({ start, end: k, light });
      start = k;
    }
  }
  const pixelGeo = new THREE.BufferGeometry();
  pixelGeo.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  const colors = new Float32Array(N * 3);
  pixelGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  for (const [size, map, opacity] of GLOWS) {
    const p = new THREE.Points(pixelGeo, new THREE.PointsMaterial({ size, map, vertexColors: true, transparent: true,
      opacity, blending: THREE.AdditiveBlending, depthWrite: false }));
    p.renderOrder = 2;
    scene.add(p);
  }
  const offGeo = new THREE.BufferGeometry();
  offGeo.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  scene.add(new THREE.Points(offGeo, new THREE.PointsMaterial({ size: 3, color: 0x3a332c, transparent: true, opacity: 0.6, depthWrite: false })));

  function placeCamera() {
    const w = canvas.clientWidth, h = canvas.clientHeight, r = renderer.getPixelRatio();
    if (canvas.width !== Math.round(w * r) || canvas.height !== Math.round(h * r)) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    const d = 1.12 * span * Math.max(1, (16 / 9) / camera.aspect), el = 0.2;
    camera.position.set(target.x, target.y + d * Math.sin(el), target.z + d * Math.cos(el));
    camera.lookAt(target);
  }

  const brightness = (home.controller && home.controller.brightness) || 1;
  function lut(exposure) {         // byte value -> displayed level, as the main page does at this exposure
    const out = new Float32Array(256);
    for (let v = 0; v < 256; v++) out[v] = Math.min(1, (v / 255) * brightness * exposure) ** (1 / 2.2);
    return out;
  }
  const LUT_SHOW = lut(1), LUT_NIGHT = lut(1 + 34 * 0.0875);   // night loops are dim on purpose; lift them like the main page

  // ---------- sequence data ----------
  const cache = new Map();
  async function loadPng(url) {
    if (cache.has(url)) return cache.get(url);
    const res = await fetch(url);
    if (!res.ok) throw new Error(res.status);
    const bmp = await createImageBitmap(await res.blob(), { colorSpaceConversion: 'none', premultiplyAlpha: 'none' });
    const c = document.createElement('canvas');
    c.width = bmp.width;
    c.height = bmp.height;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(bmp, 0, 0);
    bmp.close();
    const rgba = g.getImageData(0, 0, c.width, c.height).data;
    c.width = c.height = 0;
    const out = new Uint8Array(rgba.length / 4 * 3);
    for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
      out[j] = rgba[i]; out[j + 1] = rgba[i + 1]; out[j + 2] = rgba[i + 2];
    }
    cache.set(url, out);
    while (cache.size > 2) cache.delete(cache.keys().next().value);
    return out;
  }

  // FPP's file name -> what to play: the sequence, or its spoken intro
  function find(name) {
    for (const s of home.sequences) {
      if (s.fseqName === name)
        return { key: s.id, meta: s, data: ROOT + s.data, frames: s.frames, fps: s.fps, audio: s.audio && ROOT + s.audio, lut: s.kind === 'ambient' ? LUT_NIGHT : LUT_SHOW };
      if (s.introName && `${s.introName}.fseq` === name)
        return { key: s.id + ' intro', meta: s, intro: true, data: ROOT + s.introData, frames: s.introFrames, fps: 40, audio: ROOT + s.introAudio, lut: LUT_SHOW };
    }
    return null;
  }

  // ---------- what the house is doing ----------
  let state = null, anchor = null, recv = 0;   // the last report, and when it arrived here
  let cur = null;                              // what is loaded and showing: find() plus data
  let wanted = null;                           // what the house is on (may still be loading)
  const livePos = () => (anchor ? (anchor.ms + performance.now() - anchor.recv) / 1000 : 0);

  function setAccent(occ) {
    document.documentElement.style.setProperty('--accent', accents[occ] || '#ff6a1f');
  }
  function show(kicker, title, desc, on) {
    $('kicker').textContent = kicker;
    $('title').textContent = title;
    $('desc').textContent = desc;
    $('onair').classList.toggle('off', !on);
    document.title = on ? `${title} · Live · Pixelhome` : 'Live · Pixelhome';
  }
  function dark(kicker, title, desc, on = false) {
    wanted = null;
    cur = null;
    colors.fill(0);
    pixelGeo.attributes.color.needsUpdate = true;
    for (const r of runs) r.light.intensity = 0;
    $('bar').style.width = '0';
    show(kicker, title, desc, on);
    msg('');
    syncAudio();
  }

  async function apply(st) {
    state = st;
    if (st.status === 'offline') return dark('Live', 'The house is offline', 'We can’t reach the lights right now. Keep this page open; it will join in when they’re back.');
    if (st.status !== 'playing') return dark('Live', 'The show is resting', 'The lights are taking a break. Keep this page open; it will join in when the show starts again.');
    anchor = { ms: st.ms + (st.age || 0), recv: performance.now() };
    const w = find(st.seq);
    if (!w) return dark('Now playing', 'Something special', 'This one isn’t on the website yet, so just watch the house!', true);
    setAccent(w.meta.occasion);
    show('Now playing', w.intro ? `${w.meta.title} Intro` : w.meta.title, w.meta.description, true);
    if (cur && cur.key === w.key) { syncAudio(); return; }
    if (wanted && wanted.key === w.key) return;   // already loading
    wanted = w;
    msg('Loading the lights…');
    try {
      const data = await loadPng(w.data);
      if (wanted !== w) return;                   // the house moved on while this loaded
      cur = { ...w, bytes: data };
      msg('');
      syncAudio();
    } catch (e) {
      if (wanted === w) { wanted = null; msg('The lights didn’t load. They’ll try again with the next song.'); }
    }
  }

  // ---------- the music ----------
  const music = new Audio();
  music.preload = 'auto';
  let soundOn = false, seekedAt = 0, needSeek = false, wake = null;
  const audioClock = () => soundOn && cur && music.dataset.key === cur.key && !music.paused && !music.seeking && music.readyState >= 2;
  function syncAudio() {
    if (!soundOn || !cur || !cur.audio) {
      if (!music.paused) music.pause();
      return;
    }
    const at = livePos();
    if (music.dataset.key !== cur.key) {
      music.dataset.key = cur.key;
      music.src = cur.audio;
      needSeek = true;                             // set the position once the phone knows the file
      seekedAt = performance.now();
      music.play().catch(blocked);
      return;
    }
    if (music.paused && !music.ended) {
      if (music.readyState >= 1) music.currentTime = at;
      seekedAt = performance.now();
      music.play().catch(blocked);
      return;
    }
    // only a real slip, and never while the last correction is still settling: each seek is a gap in the sound
    if (music.seeking || performance.now() - seekedAt < 15e3 || !isFinite(music.duration) || at >= music.duration) return;
    if (Math.abs(music.currentTime - at) > 1) {
      music.currentTime = at;
      seekedAt = performance.now();
    }
  }
  music.addEventListener('loadedmetadata', () => {
    if (needSeek) { needSeek = false; music.currentTime = livePos(); }
  });
  function blocked() {
    soundOn = false;
    showSound();
    keepAwake(false);
  }
  const ICON_ON = '<path d="M3 9v6h4l5 4V5L7 9H3zm13.5 3A4.5 4.5 0 0 0 14 8v8a4.5 4.5 0 0 0 2.5-4zM14 3.2v2.1a7 7 0 0 1 0 13.4v2.1a9 9 0 0 0 0-17.6z"/>';
  const ICON_OFF = '<path d="M3 9v6h4l5 4V5L7 9H3zm13.6 3 2.7-2.7-1.4-1.4-2.7 2.7-2.7-2.7-1.4 1.4 2.7 2.7-2.7 2.7 1.4 1.4 2.7-2.7 2.7 2.7 1.4-1.4z"/>';
  function showSound() {
    $('sound').setAttribute('aria-pressed', String(soundOn));
    $('soundText').textContent = soundOn ? 'Music on · tap to mute' : 'Tap to hear the music';
    $('soundIcon').innerHTML = soundOn ? ICON_ON : ICON_OFF;
    $('note').textContent = soundOn ? 'Turn your phone’s volume up. The screen stays on while the music plays.'
      : 'The music plays from your phone, in time with the lights.';
  }
  async function keepAwake(on) {
    try {
      if (on && !wake && 'wakeLock' in navigator) {
        wake = await navigator.wakeLock.request('screen');
        wake.addEventListener('release', () => { wake = null; });
      } else if (!on && wake) {
        await wake.release();
      }
    } catch (e) { /* not allowed here; the phone may dim */ }
  }
  $('sound').addEventListener('click', () => {
    soundOn = !soundOn;
    showSound();
    keepAwake(soundOn);
    track(soundOn ? 'live_sound_on' : 'live_sound_off', { sequence_id: cur ? cur.meta.id : '' });
    if (!soundOn) { music.pause(); return; }
    // this tap is what lets the phone play sound: start the element now, even before there's a song
    if (cur && cur.audio) syncAudio();
    else {
      music.dataset.key = '';
      music.src = 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=';
      music.play().catch(() => {});
    }
  });
  showSound();

  // ---------- the relay ----------
  let ws = null, retry = 2, timer = 0;
  function connect() {
    clearTimeout(timer);
    const sock = new WebSocket(RELAY);
    ws = sock;
    sock.onopen = () => { retry = 2; };
    sock.onmessage = (e) => {
      if (ws !== sock) return;
      recv = performance.now();
      try { apply(JSON.parse(e.data)); } catch (err) { /* not a state message */ }
    };
    sock.onclose = () => {
      if (ws !== sock) return;
      ws = null;
      msg('Reconnecting to the house…');
      timer = setTimeout(connect, retry * 1000);
      retry = Math.min(60, retry * 2);
    };
  }
  connect();
  track('live_view');
  // back from the lock screen or another app: reconnect at once if the phone dropped it, and catch up
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) return;
    if (!ws) connect();
    if (soundOn) keepAwake(true);
    seekedAt = 0;
    syncAudio();
  });
  // keep the music in step, and notice a Pi that has gone quiet (it reports every 30 s playing, every minute idle)
  setInterval(() => {
    syncAudio();
    if (!state || !recv || state.status === 'offline') return;
    const age = (state.age || 0) + performance.now() - recv;
    if (age > (state.status === 'playing' ? 90e3 : 180e3)) apply({ status: 'offline' });
  }, 3e3);

  // ---------- drawing ----------
  function paint() {
    if (!cur) return;
    const at = audioClock() ? music.currentTime : livePos();
    const f = Math.max(0, Math.min(cur.frames - 1, Math.floor(at * cur.fps)));
    const base = f * home.channels, d = cur.bytes, L = cur.lut;
    for (let i = 0; i < N * 3; i++) colors[i] = L[d[base + i]];
    pixelGeo.attributes.color.needsUpdate = true;
    for (const r of runs) {
      let R = 0, G = 0, B = 0;
      for (let k = r.start; k < r.end; k++) { R += colors[k*3]; G += colors[k*3+1]; B += colors[k*3+2]; }
      const n = r.end - r.start, I = Math.max(R, G, B) / n;
      r.light.color.setRGB(R / n / (I || 1), G / n / (I || 1), B / n / (I || 1));
      r.light.intensity = I * 2.2;
    }
    $('bar').style.width = `${Math.min(100, (100 * at * cur.fps) / cur.frames).toFixed(2)}%`;
  }
  function tick() {
    requestAnimationFrame(tick);
    placeCamera();
    paint();
    renderer.render(scene, camera);
  }
  requestAnimationFrame(tick);
})();
