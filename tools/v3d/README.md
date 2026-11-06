# 3D voxel style (sample 2026-11-06)
- scene.html: Three.js scene (original voxel character "Chotu", cozy room, floating cards, 3D "?", countdown, confetti).
- render.js: headless Chromium (Playwright) renders frames via window.renderFrame(t) -> JPEGs (~0.6 s/frame).
- Three.js comes from GitHub (npm is blocked here): git clone --depth 1 --branch r170 --filter=blob:none --sparse https://github.com/mrdoob/three.js three && cd three && git sparse-checkout set build examples/fonts examples/jsm/geometries examples/jsm/loaders  (place `three/` next to scene.html)
