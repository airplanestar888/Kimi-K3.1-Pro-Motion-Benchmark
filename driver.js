// Deterministic driver: reads ?t=SECONDS from URL and renders exact frame state.
// All animation is computed from t (seconds). No reliance on rAF timing.
function renderAt(timeSec) {
  const t = (typeof timeSec === 'number')
    ? timeSec
    : parseFloat(new URLSearchParams(location.search).get('t') || '0');

  const DUR = [0, 9, 9, 9, 9, 8];          // scene durations
  // scene index at time t
  let idx = 0, acc = 0;
  for (let i = 1; i <= 5; i++) {
    if (t < acc + DUR[i] || i === 5) { idx = i - 1; break; }
    acc += DUR[i];
  }
  const lt = t - acc;                       // local time in scene

  const easeOut = p => 1 - Math.pow(1 - p, 3);
  const easeInOut = p => p < .5 ? 2*p*p : 1 - Math.pow(-2*p + 2, 2) / 2;
  const clamp01 = x => Math.max(0, Math.min(1, x));
  const fadeIn  = (x, d) => clamp01(x / d);

  const scenes = [1,2,3,4,5].map(i => document.getElementById('s'+i));
  scenes.forEach(s => s.style.opacity = 0);
  scenes[idx].style.opacity = 1;

  // background motion (grid scroll, horizon pulse, sweep)
  const grid = document.getElementById('bgGrid');
  grid.style.backgroundPosition = '0 ' + ((t * 90 / 2.6) % 90) + 'px';
  const hz = document.getElementById('bgHz');
  hz.style.opacity = 0.75 + 0.25 * Math.sin(t * 2 * Math.PI / 3.2);
  const sw = document.getElementById('bgSweep');
  const swY = -200 + ((t * 1300 / 7) % 1300);
  sw.style.top = swY + 'px';

  const sc = scenes[idx];

  if (idx === 0) {
    const chars = sc.querySelectorAll('.bigname span');
    chars.forEach((c, i) => {
      const d = 0.15 + i * 0.13;
      const p = easeOut(clamp01((lt - d) / 0.7));
      c.style.opacity = p;
      c.style.transform = 'translateY(' + (60 * (1 - p)) + 'px)';
    });
    const sub = sc.querySelector('.sub');
    const ps = easeOut(clamp01((lt - 1.15) / 0.9));
    sub.style.opacity = ps;
    sub.style.transform = 'translateY(' + (26 * (1 - ps)) + 'px)';
    const bar = document.getElementById('limebar');
    const pb = easeInOut(clamp01((lt - 1.25) / 1.1));
    bar.style.width = (760 * pb) + 'px';
  }

  if (idx === 1) {
    const cards = sc.querySelectorAll('.glass');
    cards.forEach((c, i) => {
      const p = easeOut(clamp01((lt - 0.1 - i * 0.16) / 0.8));
      c.style.opacity = p;
      c.style.transform = 'translateY(' + (70 * (1 - p)) + 'px) scale(' + (0.94 + 0.06 * p) + ')';
    });
    // gentle float
    cards.forEach((c, i) => {
      if (lt > 1.2) c.style.transform = 'translateY(' + Math.sin(t*1.4 + i*1.1)*8 + 'px)';
    });
  }

  if (idx === 2) {
    const stats = sc.querySelectorAll('.stat');
    stats.forEach((st, i) => {
      const p = easeOut(clamp01((lt - 0.1 - i * 0.17) / 0.75));
      st.style.opacity = p;
      st.style.transform = 'translateX(' + (-60 * (1 - p)) + 'px)';
      const val = st.querySelector('.val');
      const target = parseInt(val.dataset.count, 10);
      const suf = val.dataset.suffix || '';
      const pc = easeOut(clamp01((lt - 0.6 - i * 0.17) / 1.4));
      val.textContent = Math.round(target * pc) + suf;
    });
  }

  if (idx === 3) {
    const panel = sc.querySelector('.panel');
    const pp = easeOut(clamp01(lt / 0.6));
    panel.style.opacity = pp;
    panel.style.transform = 'scale(' + (0.96 + 0.04 * pp) + ')';
    const fills = sc.querySelectorAll('.bfill');
    fills.forEach((f, i) => {
      const p = easeInOut(clamp01((lt - 0.45 - i * 0.14) / 1.2));
      f.style.width = (parseFloat(f.dataset.pct) * p) + '%';
    });
  }

  if (idx === 4) {
    const wm = sc.querySelector('.wordmark');
    const p0 = easeOut(clamp01(lt / 0.9));
    wm.style.opacity = p0;
    wm.style.transform = 'scale(' + (0.92 + 0.08 * p0) + ')';
    wm.style.letterSpacing = (46 - 16 * p0) + 'px';
    const t2 = sc.querySelector('.tag2');
    const p2 = easeOut(clamp01((lt - 0.7) / 0.9));
    t2.style.opacity = p2; t2.style.transform = 'translateY(' + (26*(1-p2)) + 'px)';
    const t3 = sc.querySelector('.tag3');
    const p3 = easeOut(clamp01((lt - 1.15) / 0.9));
    t3.style.opacity = p3; t3.style.transform = 'translateY(' + (26*(1-p3)) + 'px)';
    const fl = sc.querySelector('.footline');
    fl.style.opacity = clamp01((lt - 0.3) / 0.6) * 0.9;
  }
}
window.__render = renderAt;
