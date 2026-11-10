// Takes the static images used in the 2026 battery post:
//   data/preview/battery-map-germany-2026.jpg       social preview of the 2026 map
//   data/battery_map_comparison_2022_2026.jpg       2022 and 2026 side by side
//
// Usage: serve the built site locally (bundle exec jekyll serve), then
//   node _scripts/screenshot_maps.js http://localhost:4000
// Requires Playwright (npm install playwright).
const { chromium } = require('playwright');
const path = require('path');

const base = process.argv[2] || 'http://localhost:4000';
const data = path.join(__dirname, '..', 'data');

(async () => {
  const browser = await chromium.launch();

  let page = await browser.newPage({ viewport: { width: 1200, height: 800 } });
  await page.goto(`${base}/data/battery_map_germany_2026.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);
  await page.screenshot({
    path: path.join(data, 'preview', 'battery-map-germany-2026.jpg'), type: 'jpeg', quality: 85,
  });

  // both maps next to each other, same extent and same circle scale
  page = await browser.newPage({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: 2 });
  await page.goto(`${base}/404.html`);
  await page.setContent(`
    <body style="margin:0;display:flex;gap:4px;background:#fff">
      <iframe src="${base}/data/battery_map_germany_2022.html?static" style="border:0;width:598px;height:800px"></iframe>
      <iframe src="${base}/data/battery_map_germany_2026.html?static" style="border:0;width:598px;height:800px"></iframe>
    </body>`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({
    path: path.join(data, 'battery_map_comparison_2022_2026.jpg'), type: 'jpeg', quality: 80,
  });

  await browser.close();
})();
