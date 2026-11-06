// Fast deterministic recording: load page once, drive renderAt(t) per frame.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const OUT = path.join(__dirname, 'frames');
  fs.mkdirSync(OUT, { recursive: true });   // keep existing files; every frame name is overwritten below
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.log('PAGE ERROR:', e.message));
  const url = 'file:///' + path.join(__dirname, 'kimi-showcase.html').replace(/\\/g, '/') + '?t=0';
  await page.goto(url, { waitUntil: 'networkidle' });

  const FPS = 30, TOTAL = 44, frames = FPS * TOTAL;
  const t0 = Date.now();
  for (let f = 0; f < frames; f++) {
    await page.evaluate(t => window.__render(t), f / FPS);
    await page.screenshot({ path: path.join(OUT, 'f' + String(f).padStart(5, '0') + '.png') });
    if (f % 300 === 0) console.log('frame', f, ((Date.now() - t0) / 1000).toFixed(0) + 's');
  }
  console.log('done', frames, 'in', ((Date.now() - t0) / 1000).toFixed(0) + 's');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
