/* The controller box in 3D on the About hardware page: the Kulp K8-PB, two Mean Well LRS-350-12 supplies, the fuse block
   and the wiring, built from a photo of the box and the makers' drawings. Model space is the mounting plate in mm.
   three.js (r128, the same build the player uses) and its OrbitControls load only when the figure comes near the
   screen, and it renders only while it is on screen. */
(() => {
  const fig = document.getElementById('box3d');
  if (!fig) return;
  const load = src => new Promise((ok, fail) => {
    const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = fail; document.body.appendChild(s);
  });
  const start = () => (window.THREE ? Promise.resolve() : load('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'))
    .then(() => load('https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js'))
    .catch(() => {}).then(model);
  const io = new IntersectionObserver(([e]) => { if (e.isIntersecting) { io.disconnect(); start(); } }, { rootMargin: '400px' });
  io.observe(fig);

function model() {
  const INFO = {
    k8:   { group: 'comp', name: 'Kulp K8-PB controller', chips: ['fpp2.local', 'FPP 10.4', 'rev 2.5'], sw: '#2f8a4a',
            text: 'A PocketBeagle 2 on a K8-PB with 8 pixel ports, each behind its own eFuse that trips at about 5.2 A. Power comes in on the two big screw terminals at the bottom (5–18 V, no reverse-polarity protection). Ports 1 and 2 run the house; 3–8 are wired out but unused.' },
    psu1: { group: 'comp', name: 'PSU1 · LRS-350-12', chips: ['12 V', '29 A', '348 W'], sw: '#b9bcc0',
            text: 'Feeds the K8-PB and the fuse block over 10 AWG, so both far-end injection lines come from here. Gets its AC from PSU2 over a jumper.' },
    psu2: { group: 'comp', name: 'PSU2 · LRS-350-12', chips: ['12 V', '29 A', 'for the expansion'], sw: '#b9bcc0',
            text: 'Here for the expansion: the roofline is going onto a new metal rail with a pixel every 2 inches instead of 3, about 752 pixels instead of 501 when every run is done (Porch Front is: 107 where it had 71). Its AC is already wired (the cord lands here and is jumped across to PSU1) and its V− is tied to PSU1’s, so when the new rail goes up its outputs can feed more injection with no new wiring in the box. Its DC outputs are unused until then.' },
    fuse: { group: 'comp', name: 'Faststorm fuse block', chips: ['6-way', '2 × 5 A', '10 AWG feed'], sw: '#d2a15a',
            text: 'A 6-way blade block, 85 × 88. PSU1’s 10 AWG +V lands on the positive nut at the bottom and −V on the negative nut at the top, which feeds the two negative bus bars. Two 5 A fuses sit in the left slots of the first two rows, one per far-end injection line, each leaving from its row’s left screw; the injection negatives come off the left bus bar. The other four slots are empty. Used without its cover.' },
    box:  { group: 'comp', name: 'QILIPSU IP66 enclosure', chips: ['IP66', 'UL 94 V-0', 'PC/ABS'], sw: '#c9ccd0',
            text: '415 × 315 × 183 outside, 382 × 282 inside, mounting plate 371 × 271 × 4.5. Sits on the ground with the lid on top; every cable enters through glands in its front wall.' },
    glands: { group: 'comp', name: 'Cable glands', chips: ['11 glands'], sw: '#e9e7e2',
            text: 'All in the front wall: 8 port cables in two rows of four (ports 1–4 on the row nearer the lid, 5–8 nearer the ground, left to right), 2 injection lines (the black glands) and the AC cord (far right).' },
    feed_ctrl: { group: 'wire', name: 'Controller feed', chips: ['10 AWG', 'PSU1 → K8-PB'], wire: ['var(--red)', 'var(--blk)'], g: 7,
            text: 'PSU1 +V and −V to the K8-PB’s V+ and V− terminals.' },
    feed_fuse: { group: 'wire', name: 'Fuse block feed', chips: ['10 AWG', 'PSU1 → fuse block'], wire: ['var(--red)', 'var(--blk)'], g: 7,
            text: 'PSU1 +V to the fuse block’s positive nut (bottom) and −V to its negative nut (top, above the bus bars).' },
    vneg: { group: 'wire', name: 'V− jumper', chips: ['10 AWG', 'PSU1 ↔ PSU2'], wire: ['var(--blk)', 'var(--blk)'], g: 7,
            text: 'Ties the two supplies’ negatives together, so anything PSU2 powers later shares the controller’s ground.' },
    ac_cord: { group: 'wire', name: 'AC cord', chips: ['16 AWG', '3-conductor'], wire: ['#e8e6e0', '#2f8f3a'], g: 4,
            text: 'Mains in through the right-hand gland to PSU2’s L, N and ground terminals.' },
    ac_jump: { group: 'wire', name: 'AC jumper', chips: ['16 AWG', 'PSU2 → PSU1'], wire: ['#e8e6e0', '#2f8f3a'], g: 4,
            text: 'The same 3-conductor cord, carrying L, N and ground from PSU2 across to PSU1.' },
    inj1: { group: 'wire', name: 'Injection, port 1', chips: ['18 AWG', '5 A fuse'], wire: ['var(--red)', 'var(--blk)'], g: 4,
            text: 'From fuse 1 and the left negative bus bar out to the far end of port 1, the back end of Side. Disconnected until a fault in the line is fixed; port 1 runs from the controller end alone until then.' },
    inj2: { group: 'wire', name: 'Injection, port 2', chips: ['18 AWG', '5 A fuse'], wire: ['var(--red)', 'var(--blk)'], g: 4,
            text: 'From fuse 2 and the left negative bus bar out to the far end of port 2, the free end of Right.' },
  };
  const GLAND_POS = ['top row (nearer the lid), 1st from the left', 'top row, 2nd from the left', 'top row, 3rd from the left', 'top row, 4th from the left',
    'bottom row (nearer the ground), 1st from the left', 'bottom row, 2nd from the left', 'bottom row, 3rd from the left', 'bottom row, 4th from the left'];
  const PORTS = [
    { chips: ['house', '261 px', 'ch 1–783'], text: 'Porch Left, then Left, then Side, ending at the back corner. Its far-end injection from fuse 1 is disconnected until a fault in that line is fixed.' },
    { chips: ['house', '276 px', 'ch 784–1611'], text: 'Porch Front, then Porch Right, then Right. Far-end injection from fuse 2 at the free end of Right.' },
  ];
  for (let i = 0; i < 8; i++) {
    const p = PORTS[i] || { chips: ['spare'], text: 'Wired out to its gland, not connected to any pixels yet.' };
    INFO['port' + (i + 1)] = { group: 'port', n: i + 1, name: 'Port ' + (i + 1), chips: [...p.chips, '18 AWG'],
      text: `${p.text} A 3-conductor cable (V+, data, ground). On the board: column ${(i >> 1) + 1}, ${i & 1 ? 'bottom' : 'top'}. Gland: ${GLAND_POS[i]}.` };
  }
  const OVERVIEW = `<span class="bx-kicker">Power path</span>
    <ol>
      <li>The AC cord comes in through the front wall to PSU2.</li>
      <li>An AC jumper carries it across to PSU1.</li>
      <li>PSU1 feeds the K8-PB and the fuse block over 10 AWG.</li>
      <li>Two 5 A fuses feed the far-end injection lines.</li>
      <li>The K8-PB sends data and power out on 8 port cables.</li>
      <li>PSU2 waits for the expansion.</li>
    </ol>
    <p class="bx-foot">Click a part in the model or the list for its details.</p>`;

  const stage = document.getElementById('bx-stage');
  const canvas = document.getElementById('bx-c');
  const tagsEl = document.getElementById('bx-tags');
  const tip = document.getElementById('bx-tip');
  const detail = document.getElementById('bx-detail');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!window.THREE || !THREE.OrbitControls) {
    detail.innerHTML = '<span class="bx-kicker">3D unavailable</span><p>The 3D library did not load. Reload the page to try again.</p>';
    return;
  }

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x15120f);
  const camera = new THREE.PerspectiveCamera(32, 1, 5, 6000);
  const controls = new THREE.OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 180;
  controls.maxDistance = 1800;
  controls.maxPolarAngle = Math.PI / 2 - 0.04; // stay above the ground

  // Model space is the mounting plate as seen in the photo: x across (0..371), z down the plate (0..271),
  // y off the plate, up. The box sits on the ground, lid up, with the gland wall (z = 271) facing the front.
  const root = new THREE.Group();
  scene.add(root);
  const W = (x, y, z) => new THREE.Vector3(x - 185.5, y, z - 135.5);

  const parts = {};
  const pickables = [];
  const P = id => parts[id] || (parts[id] = { meshes: [], mats: [] });
  function mat(id, color, o = {}, fixed = false) {
    const m = new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.6, metalness: 0 }, o));
    if (!fixed) P(id).mats.push(m);
    return m;
  }
  function put(id, mesh, cast = true) {
    mesh.castShadow = cast; mesh.receiveShadow = true;
    mesh.userData.part = id; P(id).meshes.push(mesh); pickables.push(mesh); root.add(mesh);
    return mesh;
  }
  function box(id, m, x0, x1, y0, y1, z0, z1) {
    const me = new THREE.Mesh(new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0), m);
    me.position.copy(W((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2));
    return put(id, me);
  }
  function cyl(id, m, r, h, x, y, z, axis = 'y', seg = 24) {
    const me = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), m);
    if (axis === 'z') me.rotation.x = Math.PI / 2;
    if (axis === 'x') me.rotation.z = Math.PI / 2;
    me.position.copy(W(x, y, z));
    return put(id, me);
  }
  function ring(id, m, r, t, x, y, z) {
    const me = new THREE.Mesh(new THREE.TorusGeometry(r, t, 8, 48), m);
    me.rotation.x = Math.PI / 2;
    me.position.copy(W(x, y, z));
    return put(id, me, false);
  }
  function tube(id, m, pts, r) {
    const curve = new THREE.CatmullRomCurve3(pts.map(p => W(p[0], p[1], p[2])), false, 'centripetal');
    const me = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(48, pts.length * 28), r, 10, false), m);
    return put(id, me);
  }
  function dot(id, m, r, x, y, z) {
    const me = new THREE.Mesh(new THREE.SphereGeometry(r, 12, 8), m);
    me.position.copy(W(x, y, z));
    return put(id, me, false);
  }
  function canvasTex(w, h, draw) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); t.anisotropy = 4;
    return t;
  }
  function decal(id, tex, x0, x1, z0, z1, y) {
    const me = new THREE.Mesh(new THREE.PlaneGeometry(x1 - x0, z1 - z0), new THREE.MeshBasicMaterial({ map: tex, transparent: true }));
    me.rotation.x = -Math.PI / 2;
    me.position.copy(W((x0 + x1) / 2, y, (z0 + z1) / 2));
    me.userData.part = id; P(id).meshes.push(me); pickables.push(me); root.add(me);
    return me;
  }
  const SANS = 'Helvetica, Arial, sans-serif';

  // ---------- ground, box and plate ----------
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({ color: 0x1d1915, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.position.set(0, -16, 0); ground.receiveShadow = true; scene.add(ground);

  const shellMat = mat('box', 0xc9ccd0, { transparent: true, opacity: 0.16, depthWrite: false, side: THREE.DoubleSide, roughness: 0.4 });
  const shell = [];
  const ix0 = 185.5 - 191, ix1 = 185.5 + 191, iz0 = 135.5 - 141, iz1 = 135.5 + 141, t = 3.5;
  shell.push(box('box', shellMat, ix0 - t, ix1 + t, -15.5, -12, iz0 - t, iz1 + t));
  shell.push(box('box', shellMat, ix0 - t, ix0, -12, 101, iz0 - t, iz1 + t));
  shell.push(box('box', shellMat, ix1, ix1 + t, -12, 101, iz0 - t, iz1 + t));
  shell.push(box('box', shellMat, ix0, ix1, -12, 101, iz0 - t, iz0));
  shell.push(box('box', shellMat, ix0, ix1, -12, 101, iz1, iz1 + t));
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(382 + 2 * t, 116.5, 282 + 2 * t)),
    new THREE.LineBasicMaterial({ color: 0x8c8f93, transparent: true, opacity: 0.55 }));
  edges.position.copy(W(185.5, (101 - 15.5) / 2, 135.5)); root.add(edges);
  shell.forEach(m => { m.castShadow = false; });

  const plateTex = canvasTex(742, 542, (g, w, h) => {
    g.fillStyle = '#d5d6d2'; g.fillRect(0, 0, w, h);
    for (let x = 0; x <= w; x += 10) { g.fillStyle = x % 50 === 0 ? '#b8bab5' : '#c7c9c4'; g.fillRect(x, 0, 1, h); }
    for (let y = 0; y <= h; y += 10) { g.fillStyle = y % 50 === 0 ? '#b8bab5' : '#c7c9c4'; g.fillRect(0, y, w, 1); }
  });
  const plateMats = [0, 0, 0, 0, 0, 0].map((_, i) => mat('box', i === 2 ? 0xffffff : 0xd5d6d2, i === 2 ? { map: plateTex, roughness: 0.8 } : { roughness: 0.8 }));
  const plate = new THREE.Mesh(new THREE.BoxGeometry(371, 4.5, 271), plateMats);
  plate.position.copy(W(185.5, 2.25, 135.5)); put('box', plate, false);
  const bossMat = mat('box', 0xc2c4c0);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) cyl('box', bossMat, 5, 12, 185.5 + sx * 179.5, -6, 135.5 + sz * 129.5);

  // ---------- K8-PB ----------
  const pcb = mat('k8', 0x14231a, { roughness: 0.5 });
  const blackPart = mat('k8', 0x121212, { roughness: 0.55 });
  const metal = mat('k8', 0xc9c9c4, { metalness: 0.7, roughness: 0.35 });
  for (const [x, z] of [[9, 39], [91, 39], [9, 141], [91, 141]]) cyl('k8', metal, 2.5, 3.5, x, 6.25, z, 'y', 12);
  box('k8', pcb, 5, 95, 8, 9.6, 35, 145);
  [[13, 35], [38, 60], [63, 85]].forEach(([a, b]) => box('k8', blackPart, a, b, 9.6, 22, 37, 53));
  // PocketBeagle 2 on its headers
  box('k8', blackPart, 48, 52, 9.6, 17, 60, 96); box('k8', blackPart, 86, 90, 9.6, 17, 60, 96);
  box('k8', mat('k8', 0xc8272b, { roughness: 0.45 }), 46, 92, 17, 18.6, 58, 98);
  box('k8', blackPart, 60, 76, 18.6, 20.4, 70, 86);
  // OLED
  box('k8', mat('k8', 0x1d3f8c, { roughness: 0.5 }), 14, 42, 16, 17.2, 60, 86);
  box('k8', blackPart, 15, 41, 9.6, 16, 62, 84);
  const oled = canvasTex(256, 140, (g, w, h) => {
    g.fillStyle = '#05070a'; g.fillRect(0, 0, w, h);
    g.font = `bold 21px ${'Menlo, Consolas, monospace'}`; g.textBaseline = 'top';
    g.fillStyle = '#ffd400'; g.fillText('Host: FPP2', 8, 6);
    g.fillStyle = '#28d7ff';
    ['Status: playing', 'Seq: DY01 Daylig', 'Remaining: 01:18', 'PL: Daytime Loop'].forEach((s, i) => g.fillText(s, 8, 32 + i * 26));
  });
  decal('k8', oled, 16, 40, 64, 80, 17.3);
  // power input terminal + silkscreen
  box('k8', blackPart, 10, 34, 9.6, 21, 128, 143);
  cyl('k8', metal, 3, 1.6, 16, 21.6, 133); cyl('k8', metal, 3, 1.6, 28, 21.6, 133);
  decal('k8', canvasTex(400, 110, (g) => {
    g.fillStyle = '#f4f1ea'; g.font = `600 40px ${SANS}`; g.fillText('V+ 5-18V', 6, 46);
    g.font = `700 34px ${SANS}`; g.fillText('Kulp Lights', 190, 96); g.font = `500 26px ${SANS}`; g.fillText('K8-PB v2.5', 6, 96);
  }), 37, 80, 130, 142, 9.7);
  // 8 pluggable port terminals, two rows of four: port 1 top left, port 2 under it, port 3 top of the next column...
  const green = mat('k8', 0x2f8a4a, { roughness: 0.55 });
  const portX = i => 14 + (i >> 1) * 19 + 8;
  const digit = n => canvasTex(64, 64, (g) => { g.fillStyle = '#f4f1ea'; g.font = `700 54px ${SANS}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(String(n), 32, 35); });
  for (let i = 0; i < 8; i++) {
    const x0 = 14 + (i >> 1) * 19, z0 = (i & 1) ? 112 : 101;
    box('k8', green, x0, x0 + 16, 9.6, 19, z0, z0 + 9);
    [-4.5, 0, 4.5].forEach(d => cyl('k8', metal, 1.3, 1, x0 + 8 + d, 19.4, z0 + 3, 'y', 10));
    decal('k8', digit(i + 1), x0 + 11.5, x0 + 16, z0 + 4.5, z0 + 9, 19.1);
  }
  // LEDs, and the board's blue glow seen in the photo
  const blueLed = new THREE.MeshStandardMaterial({ color: 0x5577ff, emissive: 0x3355ff, emissiveIntensity: 2 });
  const redLed = new THREE.MeshStandardMaterial({ color: 0xff3322, emissive: 0xff2211, emissiveIntensity: 2 });
  dot('k8', blueLed, 1.4, 89, 19.8, 64);
  dot('k8', redLed, 1.4, 84, 19.8, 95);
  const glow = new THREE.PointLight(0x3a5cff, 1.1, 320, 2);
  glow.position.copy(W(92, 40, 66)); root.add(glow);

  // ---------- power supplies ----------
  const tx = (x0, k) => x0 + 16 + k * 10.4;
  const TERM = ['+V', '+V', '+V', '-V', '-V', '-V', '⏚', 'N', 'L'];
  function psu(id, x0) {
    const body = mat(id, 0xb9bcc0, { metalness: 0.55, roughness: 0.38 });
    const dark = mat(id, 0x26272a, { metalness: 0.3, roughness: 0.6 });
    const blk = mat(id, 0x1b1b1d, { roughness: 0.7 });
    const screw = mat(id, 0xd8d8d2, { metalness: 0.8, roughness: 0.3 });
    box(id, body, x0, x0 + 115, 4.5, 34.5, 5, 203);
    box(id, body, x0, x0 + 115, 4.5, 8, 203, 221);
    box(id, blk, x0 + 8, x0 + 107, 8, 19, 205, 219);
    for (let k = 0; k <= 9; k++) box(id, blk, tx(x0, k) - 5.8, tx(x0, k) - 4.6, 19, 22.5, 205, 219);
    for (let k = 0; k < 9; k++) cyl(id, screw, 2.6, 1.6, tx(x0, k), 19.8, 211, 'y', 14);
    cyl(id, dark, 29, 0.8, x0 + 38, 34.9, 49, 'y', 40);
    [9, 16.5, 24].forEach(r => ring(id, body, r, 1.3, x0 + 38, 35.4, 49));
    cyl(id, body, 4.5, 1.2, x0 + 38, 35.5, 49, 'y', 16);
    for (const zz of [172, 181, 190]) { box(id, dark, x0 + 18, x0 + 48, 34.5, 34.8, zz - 2, zz + 2); box(id, dark, x0 + 65, x0 + 95, 34.5, 34.8, zz - 2, zz + 2); }
    decal(id, canvasTex(260, 650, (g, w, h) => {
      g.fillStyle = '#d9b23a'; g.fillRect(0, 0, w, h);
      g.save(); g.translate(w / 2, h / 2); g.rotate(-Math.PI / 2);
      g.fillStyle = '#3a2e10'; g.font = `600 30px ${SANS}`; g.textAlign = 'center';
      ['AC INPUT VOLTAGE CAN BE', 'SELECTED BY SWITCH CHECK', 'INPUT VOLTAGE AVOIDING', 'DAMAGE BEFORE POWER ON'].forEach((s, i) => g.fillText(s, 0, -62 + i * 40));
      g.restore();
    }), x0 + 80, x0 + 106, 62, 127, 34.6);
    decal(id, canvasTex(990, 60, (g) => {
      g.fillStyle = '#2b2b2e'; g.font = `700 40px ${SANS}`; g.textAlign = 'center'; g.textBaseline = 'middle';
      TERM.forEach((s, k) => g.fillText(s, (8 + 10.4 * k) * 10, 32));
    }), x0 + 8, x0 + 107, 196.5, 202.5, 34.6);
    decal(id, canvasTex(640, 90, (g) => {
      g.fillStyle = '#2b2b2e'; g.font = `800 44px ${SANS}`; g.fillText('MEAN WELL', 6, 42);
      g.font = `600 34px ${SANS}`; g.fillText('LRS-350-12 · 12V 29A', 6, 84);
    }), x0 + 10, x0 + 74, 141, 150, 34.6);
    const led = new THREE.MeshStandardMaterial({ color: 0x55ff7a, emissive: 0x22ff55, emissiveIntensity: 1.6 });
    dot(id, led, 1.6, x0 + 4.5, 9.4, 212);
  }
  psu('psu1', 118);
  psu('psu2', 245);

  // ---------- fuse block ----------
  const fb = mat('fuse', 0x161617, { roughness: 0.5 });
  const fbm = mat('fuse', 0xd4d4cf, { metalness: 0.75, roughness: 0.3 });
  const brass = mat('fuse', 0xc9a95a, { metalness: 0.7, roughness: 0.35 });
  // Faststorm 6-way blade block, 85 x 88 (from the maker's drawing): negative nut at the top, two negative bus bars
  // of three screws under it, three rows of two fuses (each with its own output screw on the outer edge), positive nut
  // at the bottom. Fuses in the left slots of rows 1 and 2; the other four slots are empty.
  box('fuse', fb, 7, 92, 4.5, 14, 180, 268);
  [[11, 184], [88, 184], [11, 264], [88, 264]].forEach(([x, z]) => cyl('fuse', fbm, 2.4, 1.2, x, 14.4, z, 'y', 12));
  box('fuse', fbm, 14, 45, 14, 15.6, 197, 208); box('fuse', fbm, 55, 86, 14, 15.6, 197, 208);
  [20, 30, 41, 59, 69, 80].forEach(x => cyl('fuse', fbm, 3, 2, x, 16.4, 202.5, 'y', 14));
  const fuseTan = mat('fuse', 0xcf9d55, { roughness: 0.35 });
  const lens = mat('fuse', 0x8e1d1d, { roughness: 0.25 });
  box('fuse', fb, 45, 54, 14, 16, 214, 252);
  [220.5, 233.5, 246].forEach((z, i) => {
    box('fuse', fb, 20, 44, 14, 17, z - 4, z + 4); box('fuse', fb, 56, 79, 14, 17, z - 4, z + 4);
    if (i < 2) { box('fuse', fuseTan, 23, 41, 17, 28, z - 2.6, z + 2.6); box('fuse', fbm, 26, 38, 28, 29, z - 2, z + 2); }
    cyl('fuse', lens, 1.4, 1.2, 47.5, 16.5, z, 'y', 10); cyl('fuse', lens, 1.4, 1.2, 51.5, 16.5, z, 'y', 10);
    box('fuse', fbm, 9, 20, 14, 15.4, z - 5, z + 5); box('fuse', fbm, 79, 90, 14, 15.4, z - 5, z + 5);
    cyl('fuse', fbm, 3.2, 2, 14.5, 16, z, 'y', 14); cyl('fuse', fbm, 3.2, 2, 84.5, 16, z, 'y', 14);
  });
  // negative nut at the top, positive nut at the bottom (gland end)
  cyl('fuse', fbm, 3.4, 14, 49, 21, 188, 'y', 16); cyl('fuse', fbm, 6.2, 4, 49, 16, 188, 'y', 6);
  cyl('fuse', fbm, 3.4, 14, 49, 21, 259, 'y', 16); cyl('fuse', fbm, 6.2, 4, 49, 16, 259, 'y', 6);
  decal('fuse', canvasTex(400, 80, (g) => { g.fillStyle = '#e8e4dc'; g.font = `italic 700 54px ${SANS}`; g.fillText('Faststorm', 10, 60); }), 32, 66, 209, 216, 14.1);

  // ---------- glands (front wall) ----------
  const gWhite = mat('glands', 0xe9e7e2, { roughness: 0.5 });
  const gBlack = mat('glands', 0x1e1e1e, { roughness: 0.5 });
  // ports 1-4 on the top row (nearer the lid, higher y), 5-8 on the bottom row (nearer the ground), left to right
  const GL = { ports: [[99, 62], [133, 62], [166, 62], [197, 62], [106, 34], [143, 34], [170, 34], [193, 34]],
               inj: [[224, 48], [250, 48]], ac: [289, 45] };
  function gland(m, x, y) {
    cyl('glands', m, 9.5, 6, x, y, iz1 - 3, 'z', 6);
    cyl('glands', m, 10, 10, x, y, iz1 + t + 5, 'z', 24);
    cyl('glands', m, 7, 4, x, y, iz1 + t + 12, 'z', 20);
  }
  GL.ports.forEach(([x, y]) => gland(gWhite, x, y));
  GL.inj.forEach(([x, y]) => gland(gBlack, x, y));
  gland(gWhite, GL.ac[0], GL.ac[1]);
  const OUT = iz1 + 60; // where cables leave the scene, in front of the box

  // ---------- 10 AWG ----------
  const R10 = 2.5, R16 = 1.3;
  const red10 = id => mat(id, 0xc8322a, { roughness: 0.45 });
  const blk10 = id => mat(id, 0x1a1817, { roughness: 0.45 });
  const p1 = k => tx(118, k), p2 = k => tx(245, k);
  tube('feed_ctrl', red10('feed_ctrl'), [[p1(0), 17, 212], [p1(0), 15, 223], [p1(0) - 6, 26, 236], [104, 40, 214], [56, 40, 172], [30, 28, 154], [28, 22, 143], [28, 21, 135]], R10);
  tube('feed_ctrl', blk10('feed_ctrl'), [[p1(3), 17, 212], [p1(3), 15, 223], [p1(3) - 4, 28, 240], [110, 44, 206], [52, 45, 170], [18, 31, 152], [16, 22, 143], [16, 21, 135]], R10);
  tube('feed_fuse', red10('feed_fuse'), [[p1(1), 17, 212], [p1(1), 15, 223], [p1(1) - 2, 18, 242], [112, 30, 268], [66, 31, 271], [52, 28, 265], [49, 27, 259]], R10);
  tube('feed_fuse', blk10('feed_fuse'), [[p1(4), 17, 212], [p1(4), 15, 223], [p1(4) - 8, 26, 232], [124, 40, 226], [108, 44, 204], [90, 40, 184], [62, 34, 178], [52, 28, 184], [49, 25, 188]], R10);
  tube('vneg', blk10('vneg'), [[p1(5), 17, 212], [p1(5), 14, 223], [p1(5) + 6, 11, 240], [240, 10, 250], [p2(3) - 6, 11, 240], [p2(3), 14, 223], [p2(3), 17, 212]], R10);
  // zip tie on the power pair, as in the photo
  const tie = mat('feed_ctrl', 0xe9e6df, { roughness: 0.6 });
  const zt = new THREE.Mesh(new THREE.TorusGeometry(6.5, 1.1, 6, 24), tie);
  zt.position.copy(W(40, 34, 163)); zt.rotation.set(0.0, 0.9, 0); put('feed_ctrl', zt, false);

  // ---------- AC (16 AWG cord, black jacket) ----------
  const jacket = id => mat(id, 0x1f1d1c, { roughness: 0.55 });
  const COND = [0x1a1a1a, 0xece9e2, 0x2f8f3a]; // L, N, ground
  const condIdx = { 8: 0, 7: 1, 6: 2 };
  const [acx, acy] = GL.ac;
  tube('ac_cord', jacket('ac_cord'), [[acx, acy, OUT], [acx, acy, iz1 + 10], [acx, acy, 262], [302, 56, 246], [342, 52, 238], [354, 32, 232], [338, 18, 230]], 3.6);
  [8, 7, 6].forEach(k => tube('ac_cord', mat('ac_cord', COND[condIdx[k]], { roughness: 0.45 }),
    [[338, 18, 230], [p2(k) + 2, 15, 226], [p2(k), 15, 222], [p2(k), 17.5, 212]], R16));
  tube('ac_jump', jacket('ac_jump'), [[316, 19, 233], [292, 26, 246], [244, 26, 247], [214, 19, 233]], 3.4);
  [8, 7, 6].forEach(k => {
    tube('ac_jump', mat('ac_jump', COND[condIdx[k]], { roughness: 0.45 }), [[316, 19, 233], [p2(k) - 1, 18.5, 225], [p2(k) - 0.6, 18.5, 214]], R16);
    tube('ac_jump', mat('ac_jump', COND[condIdx[k]], { roughness: 0.45 }), [[214, 19, 233], [p1(k) + 1, 18.5, 225], [p1(k) + 0.6, 18.5, 214]], R16);
  });

  // ---------- injection (18 AWG pairs) ----------
  function injection(id, row, busX, gl) {
    // fuse output: the left screw of its row; negative: a screw on the left bus bar (as in the photo)
    const z = [220.5, 233.5][row];
    const start = [3, 22, z + 8];
    tube(id, mat(id, 0xc8322a, { roughness: 0.45 }), [[14.5, 16.5, z], [8, 18, z + 2], start], R16);
    tube(id, mat(id, 0x1a1817, { roughness: 0.45 }), [[busX, 17.5, 202.5], [busX - 4, 24, 198], [4, 26, 204], [2, 24, z], start], R16);
    tube(id, jacket(id), [start, [4, 30, 258], [24, 52, 264], [110, 84, 262], [200, 72, 262], [gl[0], gl[1] + 4, 266], [gl[0], gl[1], iz1 + 6], [gl[0], gl[1], OUT]], 3);
  }
  injection('inj1', 0, 20, GL.inj[0]);
  injection('inj2', 1, 30, GL.inj[1]);

  // ---------- 8 port cables ----------
  GL.ports.forEach(([gx, gy], i) => {
    const id = 'port' + (i + 1), cx = portX(i), top = !(i & 1);
    const head = top ? [[cx - 3, 15, 109], [cx - 3, 25, 116], [cx - 3, 27, 126]] : [[cx + 3, 15, 120], [cx + 3, 21, 126]];
    tube(id, mat(id, 0x1d1b1a, { roughness: 0.55 }), [...head, [66 + i * 1.6, 30 + (i % 2) * 2.4, 140], [96 + i * 5, 44 + (i % 3), 186 + i * 2.5],
      [gx, gy + 7, 250], [gx, gy, iz1 - 6], [gx, gy, iz1 + 10], [gx, gy, OUT]], 2.7); // 18 AWG 3-conductor
  });
  const zt2 = new THREE.Mesh(new THREE.TorusGeometry(10.5, 1.2, 6, 28), mat('tie', 0xe9e6df, { roughness: 0.6 }));
  zt2.position.copy(W(71.5, 31, 140)); zt2.rotation.set(0, 0.25, 0); put('tie', zt2, false);

  // ---------- lights ----------
  scene.add(new THREE.HemisphereLight(0xf3ece4, 0x2a2320, 0.7));
  const key = new THREE.DirectionalLight(0xffffff, 0.8);
  key.position.set(-350, 900, 500); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -420, right: 420, top: 420, bottom: -420, near: 100, far: 2400 });
  key.shadow.bias = -0.0006;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xbfd0ff, 0.28); fill.position.set(600, 250, -400); scene.add(fill);

  // ---------- labels ----------
  const TAGS = [
    ['k8', 'K8-PB', [50, 26, 30]], ['psu1', 'PSU1', [175, 40, 20]], ['psu2', 'PSU2', [302, 40, 20]],
    ['fuse', 'Fuse block', [50, 34, 214]], ['ac_cord', 'AC in', [acx + 22, acy, iz1 + 30]], ['glands', 'Glands', [150, 76, iz1 + 24]],
  ].map(([id, text, p]) => {
    const el = document.createElement('div'); el.className = 'bx-tag'; el.textContent = text; tagsEl.appendChild(el);
    return { id, el, p: W(p[0], p[1], p[2]) };
  });
  const tmp = new THREE.Vector3();
  function placeTags() {
    const w = stage.clientWidth, h = stage.clientHeight;
    for (const tg of TAGS) {
      tmp.copy(tg.p); root.localToWorld(tmp); tmp.project(camera);
      const vis = tmp.z < 1 && Math.abs(tmp.x) < 1.1 && Math.abs(tmp.y) < 1.1;
      tg.el.hidden = !vis;
      if (vis) { tg.el.style.left = ((tmp.x + 1) / 2 * w).toFixed(1) + 'px'; tg.el.style.top = ((1 - tmp.y) / 2 * h).toFixed(1) + 'px'; }
      tg.el.classList.toggle('on', tg.id === selected);
    }
  }

  // ---------- selection ----------
  let selected = null, hovered = null;
  const ACC = new THREE.Color(0xff6a1f);
  function paint() {
    for (const [id, p] of Object.entries(parts)) {
      const on = id === selected, hv = id === hovered && !on;
      for (const m of p.mats) {
        m.emissive.copy(on || hv ? ACC : new THREE.Color(0));
        m.emissiveIntensity = on ? 0.45 : hv ? 0.18 : 0;
      }
    }
  }
  const listItems = {};
  function chipHTML(c) { return `<span class="bx-chip">${c}</span>`; }
  function showDetail() {
    if (!selected) { detail.innerHTML = OVERVIEW; return; }
    const d = INFO[selected];
    detail.innerHTML = `<span class="bx-kicker">${d.group === 'comp' ? 'Component' : d.group === 'port' ? 'Port cable' : 'Wiring'}</span><h2>${d.name}</h2>
      <div class="bx-chips">${d.chips.map(chipHTML).join('')}</div><p>${d.text}</p>`;
  }
  function select(id, fly) {
    selected = id;
    Object.entries(listItems).forEach(([k, b]) => b.setAttribute('aria-current', String(k === id)));
    showDetail(); paint();
    if (fly && id) focusPart(id);
  }
  function buildList() {
    for (const [id, d] of Object.entries(INFO)) {
      const li = document.createElement('li');
      const b = document.createElement('button'); b.type = 'button'; b.className = d.group === 'port' ? 'bx-part bx-pbtn' : 'bx-part'; b.setAttribute('aria-current', 'false');
      const sw = d.group === 'port' ? '' : d.wire
        ? `<span class="bx-sw bx-wire" style="--g:${d.g}px;background:linear-gradient(90deg, ${d.wire[0]} 0 50%, ${d.wire[1]} 50% 100%)"></span>`
        : `<span class="bx-sw" style="background:${d.sw}"></span>`;
      b.innerHTML = d.group === 'port' ? `<b>${d.n}</b><small>${d.chips[0]}</small>` : `${sw}<span>${d.name}</span><small>${d.chips[0]}</small>`;
      if (d.group === 'port') b.setAttribute('aria-label', d.name + ', ' + d.chips[0]);
      b.addEventListener('click', () => select(selected === id ? null : id, selected !== id));
      li.appendChild(b);
      document.getElementById(d.group === 'comp' ? 'bx-list-comp' : d.group === 'port' ? 'bx-list-port' : 'bx-list-wire').appendChild(li);
      listItems[id] = b;
    }
  }
  buildList(); showDetail();

  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  function pick(ev) {
    const r = canvas.getBoundingClientRect();
    ndc.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(ndc, camera);
    const hits = ray.intersectObjects(pickables, false).filter(h => h.object.visible && INFO[h.object.userData.part]);
    const h = hits.find(x => x.object.userData.part !== 'box') || hits[0];
    return h ? h.object.userData.part : null;
  }
  let down = null;
  canvas.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY }; });
  canvas.addEventListener('pointerup', e => {
    if (!down) return;
    const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y); down = null;
    if (moved > 5) return;
    const id = pick(e);
    select(id === selected ? null : id, false);
  });
  canvas.addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse' || e.buttons) { if (hovered) { hovered = null; tip.hidden = true; paint(); } return; }
    const id = pick(e);
    if (id !== hovered) { hovered = id; paint(); canvas.classList.toggle('hot', !!id); }
    if (id) {
      const r = stage.getBoundingClientRect();
      tip.textContent = INFO[id].name; tip.hidden = false;
      tip.style.left = (e.clientX - r.left) + 'px'; tip.style.top = (e.clientY - r.top) + 'px';
    } else tip.hidden = true;
  });
  canvas.addEventListener('pointerleave', () => { hovered = null; tip.hidden = true; paint(); });

  // ---------- camera ----------
  let anim = null;
  function fly(pos, target, ms = 700) {
    if (reduce) { camera.position.copy(pos); controls.target.copy(target); controls.update(); return; }
    anim = { p0: camera.position.clone(), t0: controls.target.clone(), p1: pos, t1: target, start: performance.now(), ms };
  }
  function focusPart(id) {
    const b = new THREE.Box3();
    parts[id].meshes.forEach(m => { if (m.visible) b.expandByObject(m); });
    if (b.isEmpty()) return;
    const c = b.getCenter(new THREE.Vector3()), s = b.getSize(new THREE.Vector3()).length();
    const dir = camera.position.clone().sub(controls.target).normalize();
    fly(c.clone().add(dir.multiplyScalar(Math.max(s * 1.9, 280))), c);
  }
  const VIEWS = {
    'v-front': [new THREE.Vector3(-50, 225, 690), new THREE.Vector3(0, 25, 80)],
    'v-top':   [new THREE.Vector3(0, 940, 70), new THREE.Vector3(0, 0, 10)],
    'v-side':  [new THREE.Vector3(720, 420, 520), new THREE.Vector3(0, 20, 30)],
  };
  Object.keys(VIEWS).forEach(id => document.getElementById('bx-' + id).addEventListener('click', () => {
    Object.keys(VIEWS).forEach(k => document.getElementById('bx-' + k).setAttribute('aria-pressed', String(k === id)));
    fly(VIEWS[id][0].clone(), VIEWS[id][1].clone());
  }));
  camera.position.copy(VIEWS['v-front'][0]); controls.target.copy(VIEWS['v-front'][1]);

  document.getElementById('bx-t-shell').addEventListener('change', e => { shell.forEach(m => { m.visible = e.target.checked; }); edges.visible = e.target.checked; });
  document.getElementById('bx-t-tags').addEventListener('change', e => { tagsEl.hidden = !e.target.checked; });

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    // keep the whole box in frame on tall, narrow screens
    camera.fov = w / h < 0.9 ? 44 : 32;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  resize();

  const ease = x => 1 - Math.pow(1 - x, 3);
  function frame(now) {
    if (anim) {
      const k = Math.min(1, (now - anim.start) / anim.ms), e = ease(k);
      camera.position.lerpVectors(anim.p0, anim.p1, e);
      controls.target.lerpVectors(anim.t0, anim.t1, e);
      if (k >= 1) anim = null;
    }
    controls.update();
    renderer.render(scene, camera);
    if (!tagsEl.hidden) placeTags();
    if (onScreen) requestAnimationFrame(frame); else running = false;
  }
  let onScreen = true, running = true;
  new IntersectionObserver(([e]) => {
    onScreen = e.isIntersecting;
    if (onScreen && !running) { running = true; requestAnimationFrame(frame); }
  }).observe(stage);
  requestAnimationFrame(frame);
}
})();
