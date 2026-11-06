# KIMI K3.1 Pro — Motion Benchmark Showcase

A deterministic, frame-accurate motion graphics showcase built to benchmark
motion/video generation capability. The deliverable is a 44-second 1920×1080
video with a synthesized synthwave soundtrack.

**[Watch the final render → `kimi-k3-gmi-showcase.mp4`](kimi-k3-gmi-showcase.mp4)**

## Specs

| | |
|---|---|
| Duration | 44.0 s |
| Frame rate | 30 fps (1320 frames) |
| Resolution | 1920 × 1080 |
| Scenes | 5 (name boot → modalities → capacity counters → spec bars → outro) |
| Video | H.264 (`libx264`, CRF 17) |
| Audio | AAC 192 kbps, mono 44.1 kHz WAV source |
| Style | White type on black, neon-lime `#C8FF1E` glass panels, synthwave grid + horizon glow |

## How it works

The animation is **fully deterministic**: every visual state is a pure function
of time `t` (seconds). There are no CSS transitions/keyframes and no
`requestAnimationFrame` loops, so any instant can be reproduced exactly —
which is what makes frame-by-frame capture reliable.

```
kimi-showcase.html  ── renderAt(t) ──▶  frames/f00000.png … f01319.png
driver.js           ── window.__render(t)     │
                                              ▼
assets/make_audio.py ─▶ soundtrack.wav ─▶ ffmpeg ─▶ kimi-k3-gmi-showcase.mp4
record.js (Playwright) ─────────────────┘
```

You can inspect any single frame in a browser without rendering the video:
open `kimi-showcase.html?t=12` to see the exact state at t = 12 s.

## Files

| Path | Purpose |
|---|---|
| `kimi-showcase.html` | The 1920×1080 stage, all scenes and styling |
| `driver.js` | `renderAt(t)` — computes scene/opacity/counters/bars from `t` |
| `record.js` | Playwright/Chromium capture of 1320 PNG frames into `frames/` |
| `assets/make_audio.py` | NumPy synth that generates the 44 s `soundtrack.wav` |
| `assets/soundtrack.wav` | Generated soundtrack (110 BPM, Am–F–C–G: pads, bass, arp, drums, risers) |
| `assets/gmi-logo*.png` | GMI wordmarks (original + white-recolored, alpha preserved) |
| `kimi-k3-gmi-showcase.mp4` | Final muxed H.264/AAC deliverable |

## Reproduce

```bash
npm install                      # Playwright
npx playwright install chromium  # one-time browser download
node record.js                   # ~4.5 min → frames/f00000.png … f01319.png

python assets/make_audio.py      # requires numpy → assets/soundtrack.wav

ffmpeg -framerate 30 -i frames/f%05d.png -i assets/soundtrack.wav \
  -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k \
  -shortest kimi-k3-gmi-showcase.mp4
```

`node_modules/` and `frames/` are gitignored: both are regenerable build
artifacts and are not part of the source tree.

## Notes / gotchas

- **Do not add CSS animations or transitions to the HTML.** Timing-based
  animation was the original cause of inconsistent recorded frames; the page is
  intentionally animation-free and driven only by `driver.js`.
- `assets/make_audio.py` currently writes to an absolute Windows path; adjust it
  to `assets/soundtrack.wav` if you run it from a different checkout location.
- The horizon glow sits at `bottom: 14%` (softened to 30 px / 90 px blur) so it
  does not overlap scene text at t = 2 s and t = 38 s.
