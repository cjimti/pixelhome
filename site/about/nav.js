/* The About pages' sidebar: under the current page's link, a list of its sections (each <section id> with an <h2>),
   the one being read highlighted as you scroll. Wide screens only show it (style.css); without JS the sidebar still
   links the three pages. */
(() => {
  const here = document.querySelector('.aboutnav a[aria-current="page"]');
  const secs = [...document.querySelectorAll('.aboutmain > section[id]')].filter(s => s.querySelector(':scope > h2'));
  if (!here || !secs.length) return;
  const ol = document.createElement('ol');
  const links = new Map();
  for (const s of secs) {
    const a = document.createElement('a');
    a.href = `#${s.id}`;
    a.textContent = s.querySelector(':scope > h2').textContent;
    const li = document.createElement('li');
    li.append(a);
    ol.append(li);
    links.set(s, a);
  }
  here.parentElement.append(ol);
  // The section being read is the last one whose top has passed a line a third of the way down the window.
  const mark = () => {
    const line = innerHeight / 3;
    let cur = null;
    for (const s of secs) if (s.getBoundingClientRect().top <= line) cur = s;
    for (const [s, a] of links) a.classList.toggle('on', s === cur);
  };
  let queued = false;
  addEventListener('scroll', () => {
    if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; mark(); }); }
  }, { passive: true });
  addEventListener('resize', mark);
  mark();
})();
