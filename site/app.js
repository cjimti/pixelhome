(async function () {
  const $ = (id) => document.getElementById(id);
  const status = $('status');
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const CACHE_SIZE = 4;           // decoded sequences kept in memory (night loops are ~9 MB each)

  let CAT;
  try {
    CAT = await (await fetch('data/catalog.json')).json();
  } catch (e) {
    status.textContent = 'Could not load the sequence catalog. Reload the page to try again.';
    return;
  }
  const occasion = Object.fromEntries(CAT.occasions.map((o) => [o.id, o]));
  // Start the list at the next holiday (a holiday stays first through the day after it); undated ones last.
  {
    const d = new Date(Date.now() - 864e5);
    const today = `${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    const key = (o) => !o.date ? '2' : (o.date >= today ? '0' : '1') + o.date;
    CAT.occasions.sort((a, b) => key(a).localeCompare(key(b)));
  }
  $('built').textContent = 'Built ' + new Date(CAT.built).toLocaleDateString(undefined, { dateStyle: 'medium' });

  // ---------- scene ----------
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

  // Everything that depends on the home's layout lives in `H`, rebuilt when the home changes.
  let H = null;
  const target = new THREE.Vector3();
  const VIEWS = { street: { az: 0, el: 0.16, dist: 1.43 }, corner: { az: -0.62, el: 0.34, dist: 1.35 }, above: { az: 0, el: 1.4, dist: 1.55 } };

  function buildHouse(home, layout) {
    if (H) {
      scene.remove(H.group);
      H.group.traverse((o) => { if (o.geometry) o.geometry.dispose(); if (o.material) o.material.dispose(); });
    }
    const P = layout.pixels, N = P.length / 3;
    const group = new THREE.Group();
    let x0 = Infinity, x1 = -Infinity, z0 = Infinity, z1 = -Infinity, ySum = 0;
    for (let k = 0; k < N; k++) {
      x0 = Math.min(x0, P[k*3]); x1 = Math.max(x1, P[k*3]);
      z0 = Math.min(z0, P[k*3+2]); z1 = Math.max(z1, P[k*3+2]);
      ySum += P[k*3+1];
    }
    const span = Math.max(x1 - x0, z1 - z0, 1);
    target.set((x0 + x1) / 2, ySum / N - 40 * span / 1224, (z0 + z1) / 2 - 0.08 * (z1 - z0));
    scene.fog = new THREE.Fog(0x060504, 2.1 * span, 5.3 * span);

    const ground = new THREE.Mesh(new THREE.PlaneGeometry(span * 8, span * 8), new THREE.MeshLambertMaterial({ color: 0x0d0c0b }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.set(target.x, 0, target.z);
    group.add(ground);
    if (layout.meshVerts.length) {
      const hg = new THREE.BufferGeometry();
      hg.setAttribute('position', new THREE.Float32BufferAttribute(layout.meshVerts, 3));
      hg.setIndex(layout.meshTris);
      const geo = hg.toNonIndexed();
      geo.computeVertexNormals();
      group.add(new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ color: 0x2b2521, side: THREE.DoubleSide })));
    }

    // light spill: one point light per run of pixels, coloured by that run's average
    const runs = [];
    let start = 0;
    for (let k = 1; k <= N; k++) {
      const gap = k === N ? Infinity : Math.hypot(P[k*3]-P[k*3-3], P[k*3+1]-P[k*3-2], P[k*3+2]-P[k*3-1]);
      if (gap > 30) {
        const mid = Math.floor((start + k - 1) / 2);
        const light = new THREE.PointLight(0x000000, 0, 650 * span / 1224, 1.4);
        light.position.set(P[mid*3], P[mid*3+1] - 25, P[mid*3+2] + 40);
        group.add(light);
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
      group.add(p);
    }
    const offGeo = new THREE.BufferGeometry();
    offGeo.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
    group.add(new THREE.Points(offGeo, new THREE.PointsMaterial({ size: 3, color: 0x3a332c, transparent: true, opacity: 0.6, depthWrite: false })));
    scene.add(group);
    H = { home, N, span, group, runs, pixelGeo, colors };
  }

  // ---------- camera ----------
  const cam = { ...VIEWS.street };
  let goal = null;
  function placeCamera() {
    // narrow (portrait) stages pull back so the whole roofline still fits across
    const d = cam.dist * H.span * Math.max(1, (16 / 9) / camera.aspect);
    const c = Math.cos(cam.el);
    camera.position.set(target.x + d * c * Math.sin(cam.az), target.y + d * Math.sin(cam.el), target.z + d * c * Math.cos(cam.az));
    camera.lookAt(target);
  }
  const viewButtons = document.querySelectorAll('.views button');
  function setView(name) {
    goal = { ...VIEWS[name] };
    if (reduceMotion) { Object.assign(cam, goal); goal = null; }
    viewButtons.forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.view === name)));
  }
  viewButtons.forEach((b) => b.addEventListener('click', () => setView(b.dataset.view)));

  // Touch: horizontal drags orbit, vertical swipes scroll the page (touch-action: pan-y), pinch zooms.
  const stage = $('stage');
  const pointers = new Map();
  let pinch = 0;
  stage.addEventListener('pointerdown', (e) => {
    if (e.target.closest('button')) return;
    stage.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    goal = null;
    viewButtons.forEach((b) => b.setAttribute('aria-pressed', 'false'));
  });
  stage.addEventListener('pointermove', (e) => {
    const p = pointers.get(e.pointerId);
    if (!p) return;
    if (pointers.size === 1) {
      cam.az -= (e.clientX - p.x) * 0.006;
      cam.el = Math.min(1.5, Math.max(0.03, cam.el + (e.clientY - p.y) * 0.005));
    }
    p.x = e.clientX; p.y = e.clientY;
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      if (pinch) cam.dist = Math.min(3.7, Math.max(0.4, cam.dist * pinch / d));
      pinch = d;
    }
  });
  const release = (e) => { pointers.delete(e.pointerId); pinch = 0; };
  stage.addEventListener('pointerup', release);
  stage.addEventListener('pointercancel', release);
  stage.addEventListener('wheel', (e) => {
    e.preventDefault();
    goal = null;
    cam.dist = Math.min(3.7, Math.max(0.4, cam.dist * Math.exp(e.deltaY * 0.0012)));
  }, { passive: false });

  function resize() {
    const w = canvas.clientWidth, h = canvas.clientHeight, r = renderer.getPixelRatio();
    if (canvas.width !== Math.round(w * r) || canvas.height !== Math.round(h * r)) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
  }

  // ---------- sequence data ----------
  const cache = new Map();         // url -> Uint8Array, least recently used first
  let seq = null;                  // { meta, data, channels, fps, frames }
  let t = 0, playing = false, scrubbing = false;
  const exposure = $('exposure');

  // Each sequence ships as a lossless PNG: one row per frame, one image pixel per LED, channel order.
  async function loadPng(url) {
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
    return out;
  }
  async function cached(url) {
    let data = cache.get(url);
    if (data) cache.delete(url);
    else data = await loadPng(url);
    cache.set(url, data);
    while (cache.size > CACHE_SIZE) cache.delete(cache.keys().next().value);
    return data;
  }

  async function decompressBlock(bytes, format) {
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream(format));
    return new Uint8Array(await new Response(stream).arrayBuffer());
  }

  async function parseFseq(buf) {
    const dv = new DataView(buf);
    if (String.fromCharCode(...new Uint8Array(buf, 0, 4)) !== 'PSEQ') throw new Error('This is not an FSEQ file.');
    const off = dv.getUint16(4, true), major = dv.getUint8(7);
    if (major !== 2) throw new Error(`This is an FSEQ version ${major} file. Only version 2 is supported.`);
    const chans = dv.getUint32(10, true), frames = dv.getUint32(14, true), step = dv.getUint8(18);
    const ctype = dv.getUint8(20) & 15, nblk = dv.getUint8(21) | ((dv.getUint8(20) >> 4) << 8), nsparse = dv.getUint8(22);
    let data;
    if (ctype === 0) {
      data = new Uint8Array(buf, off, chans * frames);
    } else {
      const format = ctype === 1 ? 'zstd' : 'deflate';
      try { new DecompressionStream(format); } catch (e) {
        throw new Error('This file is zstd-compressed, which this browser cannot unpack. Try Chrome, or save the file uncompressed.');
      }
      const parts = [];
      let pos = off;
      for (let i = 0; i < nblk; i++) {
        const size = dv.getUint32(32 + i * 8 + 4, true);
        if (!size) continue;
        parts.push(await decompressBlock(new Uint8Array(buf, pos, size), format));
        pos += size;
      }
      data = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
      let o = 0;
      for (const p of parts) { data.set(p, o); o += p.length; }
    }
    if (nsparse) {
      const base = 32 + nblk * 8;
      const u24 = (at) => dv.getUint8(at) | (dv.getUint8(at + 1) << 8) | (dv.getUint8(at + 2) << 16);
      const ranges = [];
      for (let i = 0; i < nsparse; i++) ranges.push([u24(base + i * 6), u24(base + i * 6 + 3)]);
      if (!(ranges.length === 1 && ranges[0][0] === 0)) {
        const full = Math.max(...ranges.map(([s, c]) => s + c));
        const out = new Uint8Array(full * frames);
        for (let f = 0; f < frames; f++) {
          let src = f * chans;
          for (const [s, c] of ranges) { out.set(data.subarray(src, src + c), f * full + s); src += c; }
        }
        return { data: out, channels: full, frames, fps: 1000 / step };
      }
    }
    return { data, channels: chans, frames, fps: 1000 / step };
  }

  // ---------- library ----------
  const filters = { occasion: '', kind: '', q: '' };
  const cards = new Map();         // sequence id -> list row

  function fmt(s, tenths = true) {
    const m = Math.floor(s / 60), r = s - m * 60;
    return `${m}:${(tenths ? r.toFixed(1) : Math.round(r).toString()).padStart(tenths ? 4 : 2, '0')}`;
  }
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

  function renderLibrary() {
    const home = H.home;
    cards.clear();
    const sel = $('occasions');
    sel.replaceChildren();
    const counts = {};
    home.sequences.forEach((s) => { counts[s.occasion] = (counts[s.occasion] || 0) + 1; });
    sel.append(new Option(`All occasions (${home.sequences.length})`, ''));
    CAT.occasions.filter((o) => counts[o.id]).forEach((o) => sel.append(new Option(`${o.label} (${counts[o.id]})`, o.id)));

    const groups = $('groups');
    groups.replaceChildren();
    for (const o of CAT.occasions) {
      const list = home.sequences.filter((s) => s.occasion === o.id);
      if (!list.length) continue;
      const g = el('div', 'group');
      g.dataset.occasion = o.id;
      g.style.setProperty('--c', o.accent);
      g.append(el('h3', null, o.label));
      for (const s of list) {
        const b = el('button', 'item');
        b.type = 'button';
        const r1 = el('span', 'r1');
        r1.append(el('span', 'c', s.code), el('span', 't', s.title));
        if (s.kind === 'ambient') r1.append(el('span', 'k', 'All night'));
        r1.append(el('span', 'dur', fmt(s.seconds, false)));
        b.append(r1, el('span', 'd', s.description));
        b.addEventListener('click', () => choose(s));
        b._seq = s;
        cards.set(s.id, b);
        g.append(b);
      }
      groups.append(g);
    }
    applyFilters();
  }

  function applyFilters() {
    const q = filters.q.trim().toLowerCase();
    let shown = 0;
    $('occasions').value = filters.occasion;
    document.querySelectorAll('#kinds button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.kind === filters.kind)));
    document.querySelectorAll('.group').forEach((g) => {
      let n = 0;
      g.querySelectorAll('.item').forEach((c) => {
        const s = c._seq;
        const ok = (!filters.occasion || s.occasion === filters.occasion) && (!filters.kind || s.kind === filters.kind) &&
          (!q || `${s.code} ${s.title} ${s.description}`.toLowerCase().includes(q));
        c.hidden = !ok;
        n += ok;
      });
      g.hidden = !n;
      shown += n;
    });
    const total = H.home.sequences.length;
    $('count').textContent = shown === total ? `${total}` : `${shown} of ${total}`;
    $('empty').hidden = shown > 0;
  }
  document.querySelectorAll('#kinds button').forEach((b) => b.addEventListener('click', () => { filters.kind = b.dataset.kind; applyFilters(); }));
  $('occasions').addEventListener('change', (e) => { filters.occasion = e.target.value; applyFilters(); });
  $('search').addEventListener('input', (e) => { filters.q = e.target.value; applyFilters(); });

  // ---------- choosing / playing ----------
  const wide = matchMedia('(min-width: 760px)');     // sidebar layout: the list scrolls on its own
  function setAccent(occ) {
    document.documentElement.style.setProperty('--accent', (occasion[occ] || CAT.occasions[0] || { accent: '#ff6a1f' }).accent);
  }

  function mark(meta) {
    cards.forEach((c, id) => c.setAttribute('aria-current', String(id === meta.id)));
    $('nowCode').textContent = meta.code;
    $('nowName').textContent = meta.title;
    $('nowDesc').textContent = meta.description || '';
    const row = cards.get(meta.id);
    if (row && wide.matches) row.scrollIntoView({ block: 'nearest' });
    const dl = $('download');
    dl.hidden = !meta.fseq;
    if (meta.fseq) {
      dl.href = meta.fseq;
      dl.download = meta.fseqName;
      dl.textContent = `Download .fseq · ${(meta.fseqBytes / 1e6).toFixed(1)} MB`;
    }
    setAccent(meta.occasion);
    document.title = `${meta.title} · Pixelhome`;
  }

  let loadToken = 0;
  async function choose(meta, startAt = 0, autoplay = true) {
    mark(meta);
    history.replaceState(null, '', `#${H.home.id}/${meta.id}`);
    const token = ++loadToken;
    status.hidden = false;
    status.textContent = 'Loading sequence…';
    try {
      const data = await cached(meta.data);
      if (token !== loadToken) return;
      seq = { meta, data, channels: H.home.channels, fps: meta.fps, frames: meta.frames };
      exposure.value = meta.kind === 'ambient' ? 4 : 1;
      exposure.dispatchEvent(new Event('input'));
      t = startAt;
      status.hidden = true;
      setPlaying(autoplay && !reduceMotion);
    } catch (e) {
      if (token === loadToken) status.textContent = 'This sequence did not load. Check your connection and pick it again.';
    }
  }

  function setPlaying(p) {
    playing = p && !!seq;
    $('play').setAttribute('aria-label', playing ? 'Pause' : 'Play');
    $('playIcon').innerHTML = playing ? '<path d="M6 4.5h4.5v15H6zM13.5 4.5H18v15h-4.5z"/>' : '<path d="M7 4.5v15l13-7.5z"/>';
  }
  $('play').addEventListener('click', () => setPlaying(!playing));
  document.addEventListener('keydown', (e) => {
    if (e.target.closest('input, select, a') || (e.target.closest('button') && !e.target.closest('.item'))) return;
    if (e.code === 'Space') { e.preventDefault(); setPlaying(!playing); }
    if (e.code === 'ArrowUp' || e.code === 'ArrowDown') {
      const rows = [...cards.values()].filter((c) => !c.hidden && !c.closest('.group').hidden);
      if (!rows.length) return;
      e.preventDefault();
      const i = rows.findIndex((c) => seq && c._seq.id === seq.meta.id);
      const next = i < 0 ? 0 : (i + (e.code === 'ArrowUp' ? -1 : 1) + rows.length) % rows.length;
      choose(rows[next]._seq);
    }
    if (seq && (e.code === 'ArrowLeft' || e.code === 'ArrowRight')) {
      const dur = seq.frames / seq.fps;
      t = (t + (e.code === 'ArrowLeft' ? -5 : 5) + dur) % dur;
    }
  });

  const scrub = $('scrub');
  scrub.addEventListener('input', () => { if (seq) t = scrub.value * seq.frames / seq.fps; scrubbing = true; });
  scrub.addEventListener('change', () => { scrubbing = false; });
  exposure.addEventListener('input', () => { $('expOut').textContent = (+exposure.value).toFixed(1) + '×'; });

  // drop / pick your own
  const drop = $('drop'), file = $('file'), dropMsg = $('dropMsg');
  $('pick').addEventListener('click', () => file.click());
  async function openFile(f) {
    dropMsg.hidden = false;
    dropMsg.className = '';
    dropMsg.textContent = `Reading ${f.name}…`;
    try {
      const s = await parseFseq(await f.arrayBuffer());
      if (s.channels < H.home.channels) throw new Error(`This file has ${s.channels} channels; this home needs ${H.home.channels}.`);
      const meta = { id: 'file', code: 'FILE', title: f.name.replace(/\.fseq$/i, ''), occasion: seq ? seq.meta.occasion : '' };
      loadToken++;
      seq = { meta, data: s.data, channels: s.channels, fps: s.fps, frames: s.frames };
      mark(meta);
      t = 0;
      status.hidden = true;
      setPlaying(true);
      dropMsg.textContent = `Playing ${f.name}: ${fmt(s.frames / s.fps)} at ${Math.round(s.fps)} fps.`;
    } catch (e) {
      dropMsg.className = 'err';
      dropMsg.textContent = e.message || 'This file could not be read.';
    }
  }
  file.addEventListener('change', () => file.files[0] && openFile(file.files[0]));
  let dragDepth = 0;
  document.addEventListener('dragenter', (e) => { e.preventDefault(); dragDepth++; drop.classList.add('over'); });
  document.addEventListener('dragover', (e) => e.preventDefault());
  document.addEventListener('dragleave', () => { if (--dragDepth <= 0) { dragDepth = 0; drop.classList.remove('over'); } });
  document.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDepth = 0;
    drop.classList.remove('over');
    const f = e.dataTransfer.files[0];
    if (f) openFile(f);
  });

  // ---------- frame loop ----------
  const gammaLUT = new Float32Array(256 * 81);   // exposure 1.0..8.0 in 0.0875 steps x byte value
  let brightness = 0.8;
  function buildLUT() {
    for (let e = 0; e < 81; e++) for (let v = 0; v < 256; v++)
      gammaLUT[e * 256 + v] = Math.min(1, (v / 255) * brightness * (1 + e * 0.0875)) ** (1 / 2.2);
  }

  let lastTime = '';
  function paint() {
    if (!seq) return;
    const { N, colors, runs, pixelGeo } = H;
    const f = Math.min(seq.frames - 1, Math.floor(t * seq.fps));
    const base = f * seq.channels;
    const lut = Math.round((+exposure.value - 1) / 0.0875) * 256;
    const d = seq.data;
    for (let i = 0; i < N * 3; i++) colors[i] = gammaLUT[lut + d[base + i]];
    pixelGeo.attributes.color.needsUpdate = true;
    for (const r of runs) {
      let R = 0, G = 0, B = 0;
      for (let k = r.start; k < r.end; k++) { R += colors[k*3]; G += colors[k*3+1]; B += colors[k*3+2]; }
      const n = r.end - r.start, I = Math.max(R, G, B) / n;
      r.light.color.setRGB(R / n / (I || 1), G / n / (I || 1), B / n / (I || 1));
      r.light.intensity = I * 2.2;
    }
    const dur = seq.frames / seq.fps;
    const label = `<b>${fmt(t)}</b> / ${fmt(dur, false)}`;
    if (label !== lastTime) { $('time').innerHTML = label; lastTime = label; }
    if (!scrubbing) scrub.value = t / dur;
  }

  let last = performance.now();
  function tick(now) {
    requestAnimationFrame(tick);
    if (!H) return;
    const dt = Math.min(0.1, (now - last) / 1000);
    last = now;
    if (playing && seq) t = (t + dt) % (seq.frames / seq.fps);
    if (goal) {
      const k = 1 - Math.exp(-dt * 4);
      for (const key of ['az', 'el', 'dist']) cam[key] += (goal[key] - cam[key]) * k;
      if (Math.abs(goal.az - cam.az) + Math.abs(goal.el - cam.el) + Math.abs(goal.dist - cam.dist) < 0.001) goal = null;
    }
    resize();
    placeCamera();
    paint();
    renderer.render(scene, camera);
  }

  // ---------- homes ----------
  async function openHome(home, seqId) {
    status.hidden = false;
    status.textContent = 'Loading the house…';
    let layout;
    try {
      layout = await (await fetch(home.layout)).json();
    } catch (e) {
      status.textContent = 'Could not load this home. Reload the page to try again.';
      return;
    }
    seq = null;
    buildHouse(home, layout);
    brightness = (home.controller && home.controller.brightness) || 1;
    buildLUT();
    const c = home.controller;
    $('homeSpec').textContent = `${home.name} · ${home.pixels} pixels · ${home.segments} runs` +
      (c ? ` · ${c.hardware || 'controller'} at ${Math.round(brightness * 100)}%` : '');
    if (c) $('ctrlNote').textContent = `${Math.round(brightness * 100)}% brightness and gamma ${c.gamma ?? 1}`;
    $('homeSelect').value = home.id;
    renderLibrary();
    const list = home.sequences;
    if (!list.length) { status.textContent = 'This home has no sequences yet.'; return; }
    const pick = list.find((s) => s.id === seqId);
    if (pick) choose(pick);
    else {
      const first = CAT.occasions.map((o) => list.find((s) => s.occasion === o.id)).find(Boolean) || list[0];
      choose(first, first.seconds * 0.3);
    }
  }

  const sel = $('homeSelect');
  CAT.homes.forEach((h) => sel.append(new Option(h.name, h.id)));
  sel.hidden = CAT.homes.length < 2;
  sel.addEventListener('change', () => openHome(CAT.homes.find((h) => h.id === sel.value)));

  function fromHash() {
    const [hid, ...rest] = decodeURIComponent(location.hash.slice(1)).split('/');   // #home/occasion/name
    return { home: CAT.homes.find((h) => h.id === hid), seqId: rest.join('/') };
  }
  window.addEventListener('hashchange', () => {
    const { home, seqId } = fromHash();
    if (!home) return;
    if (!H || home.id !== H.home.id) openHome(home, seqId);
    else { const s = home.sequences.find((x) => x.id === seqId); if (s && (!seq || seq.meta.id !== s.id)) choose(s); }
  });

  if (!CAT.homes.length) { status.textContent = 'No homes yet.'; return; }
  const initial = fromHash();
  await openHome(initial.home || CAT.homes[0], initial.seqId);
  requestAnimationFrame(tick);
})();
