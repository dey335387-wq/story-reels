// node render.js <outdir> [t1,t2,...]   -> JPEG frames (all 450 frames at 30fps if no list)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname, out = process.argv[2], list = process.argv[3], page = process.env.PAGE || 'scene.html', NF = +(process.env.NF || 450);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); });
}).listen(+(process.env.PORT||8765));
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1.5 });
  p.on('console', m => { if (m.type() === 'error') console.log('PAGE', m.text()); });
  await p.goto('http://localhost:'+(process.env.PORT||8765)+'/' + page);
  await p.waitForFunction('window.READY === true', null, { timeout: 60000 });
  await p.evaluate(() => document.fonts.ready);
  const ts = list ? list.split(',').map(Number) : Array.from({ length: NF }, (_, i) => i / 30);
  for (let i = 0; i < ts.length; i++) {
    await p.evaluate(t => window.renderFrame(t), ts[i]);
    await p.screenshot({ path: path.join(out, list ? `f_${ts[i]}.jpg` : `f${String(i).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 92 });
    if (i % 50 === 0) console.log('frame', i);
  }
  await b.close(); srv.close();
})();
