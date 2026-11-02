// Show times on the home page and the set pages. The build writes every showing into the HTML (data-start and
// data-end, the times in the home's time zone), but it only runs on a release, so "now" is worked out here: what is
// over is hidden, nights say Tonight and Tomorrow, the next night of shows leads the home page, and a show that is on
// points to Live. Nothing is fetched.
(function () {
  const root = document.querySelector('[data-tz]');
  if (!root) return;
  const tz = root.dataset.tz;
  const $ = (id) => document.getElementById(id);
  const $$ = (sel, el = document) => [...el.querySelectorAll(sel)];
  const ymd = new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' });
  const clock = new Intl.DateTimeFormat('en-US', { timeZone: tz, hour: 'numeric', minute: '2-digit' });
  const at = (iso) => clock.format(new Date(iso)).replace(' AM', ' am').replace(' PM', ' pm');
  const start = (el) => Date.parse(el.dataset.start);
  const end = (el) => Date.parse(el.dataset.end);
  const tracked = new WeakMap();      // each date label's own text, before Tonight or Tomorrow replaced it

  function dayWord(date, now) {
    if (date === ymd.format(now)) return 'Tonight';
    if (date === ymd.format(now + 864e5)) return 'Tomorrow';
    return '';
  }

  // a list with data-fold="n" shows its first n visible items until its "more" button opens it
  function fold(list) {
    const n = +list.dataset.fold;
    const items = [...list.children].filter((el) => !el.hidden);
    items.forEach((el, i) => el.classList.toggle('later', i >= n && !list.classList.contains('open')));
    const more = list.nextElementSibling;
    if (more && more.classList.contains('more')) {
      more.hidden = items.length <= n || list.classList.contains('open');
      if (!more.dataset.wired) {
        more.dataset.wired = '1';
        more.addEventListener('click', () => { list.classList.add('open'); fold(list); });
      }
    }
  }

  function update() {
    const now = Date.now();
    $$('.when[data-date]').forEach((el) => {
      if (!tracked.has(el)) tracked.set(el, el.textContent);
      const w = dayWord(el.dataset.date, now);
      el.textContent = w ? `${w}, ${tracked.get(el).split(', ').slice(1).join(', ')}` : tracked.get(el);
      el.classList.toggle('soon', !!w);
    });
    $$('[data-start][data-end]').forEach((el) => {
      el.classList.toggle('over', end(el) <= now);
      el.classList.toggle('on', start(el) <= now && now < end(el));
    });

    // the home page: the first night that isn't over leads, the rest follow
    const slot = $('tonight');
    if (slot) {
      const box = root.querySelector('.nights');
      const nights = $$('.night', root).sort((a, b) => a.dataset.date.localeCompare(b.dataset.date));
      const upcoming = nights.filter((n) => end(n) > now);
      const first = upcoming[0];
      nights.forEach((n) => { if (n !== first) { box.append(n); n.hidden = end(n) <= now; } });
      if (first && first.parentNode !== slot) slot.append(first);
      if (first) first.hidden = false;
      slot.hidden = !first;
      $('coming').hidden = upcoming.length < 2;
      $('offseason').hidden = !!first;
      const today = first && first.dataset.date === ymd.format(now);
      $('schedHead').textContent = !first ? 'Between seasons' : today ? 'Tonight on the house' : 'Next on the house';
      const on = first && first.querySelector('.blocks li.on');
      const onNow = $('onNow');
      onNow.hidden = !on;
      if (on) {
        const name = on.classList.contains('im') ? 'Intermission' : on.querySelector('.what a').textContent;
        onNow.querySelector('.txt').textContent = `On the house now: ${name}, until ${at(on.dataset.end)}.`;
      }
      // between seasons: the next three occasions by date
      const mmdd = ymd.format(now).slice(5);
      $$('#comingUp [data-mmdd]')
        .sort((a, b) => ((a.dataset.mmdd < mmdd) + a.dataset.mmdd).localeCompare((b.dataset.mmdd < mmdd) + b.dataset.mmdd))
        .forEach((el, i) => { el.hidden = i >= 3; el.parentNode.append(el); });
    }

    // a set page: its showings still to come, and the next one under the title
    const shows = root.querySelector('.showings');
    if (shows) {
      const rows = $$('.showing', shows);
      rows.forEach((r) => { r.hidden = end(r) <= now; });
      const left = rows.filter((r) => !r.hidden);
      shows.hidden = !left.length;
      root.querySelector('.when .none').hidden = !!left.length;
      const next = root.querySelector('.intro .next');
      const t = left.length && $$('.t', left[0]).find((x) => end(x) > now);
      if (next) {
        next.hidden = !t;
        if (t) {
          const w = dayWord(left[0].querySelector('.when').dataset.date, now);
          const when = t.classList.contains('on') ? 'on the house now' : `${w ? w.toLowerCase() : tracked.get(left[0].querySelector('.when'))} at ${at(t.dataset.start)}`;
          next.innerHTML = '';
          next.append('Next: ', Object.assign(document.createElement('a'), { href: t.classList.contains('on') ? '/live/' : '#when', textContent: when }));
        }
      }
    }
    $$('[data-fold]', root).forEach(fold);
  }

  update();
  setInterval(update, 30e3);
})();
