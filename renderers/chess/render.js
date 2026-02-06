#!/usr/bin/env node
/**
 * Chess board renderer using Chessground + Playwright.
 *
 * Usage:
 *   node render.js --fen "<FEN>" --output board.png [--arrows "e2e4:green,d7d5:red"] [--size 800] [--last-move "e2e4"]
 *
 * Examples:
 *   node render.js --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --output board.png
 *   node render.js --fen "start" --output start.png --arrows "e2e4:green,d2d4:blue" --size 600
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { parseArgs } = require('util');

const { values: args } = parseArgs({
  options: {
    fen:       { type: 'string', default: 'start' },
    output:    { type: 'string', default: 'board.png' },
    arrows:    { type: 'string', default: '' },
    size:      { type: 'string', default: '800' },
    'last-move': { type: 'string', default: '' },
  },
});

function parseArrows(arrowStr) {
  if (!arrowStr) return [];
  return arrowStr.split(',').map(entry => {
    const [move, brush] = entry.split(':');
    const orig = move.slice(0, 2);
    const dest = move.slice(2, 4);
    return { orig, dest, brush: brush || 'green' };
  });
}

function parseLastMove(moveStr) {
  if (!moveStr || moveStr.length < 4) return undefined;
  return [moveStr.slice(0, 2), moveStr.slice(2, 4)];
}

function readAsset(relPath) {
  return fs.readFileSync(path.join(__dirname, 'node_modules', '@lichess-org', 'chessground', relPath), 'utf-8');
}

(async () => {
  const size = parseInt(args.size, 10);
  const config = {
    fen: args.fen,
    arrows: parseArrows(args.arrows),
    lastMove: parseLastMove(args['last-move']),
  };

  // Read Chessground assets from node_modules
  const cgBaseCSS = readAsset('assets/chessground.base.css');
  const cgBrownCSS = readAsset('assets/chessground.brown.css');
  const cgPiecesCSS = readAsset('assets/chessground.cburnett.css');
  const cgJS = readAsset('dist/chessground.min.js');

  // Convert ESM export to global assignment so it works in a plain <script>
  // e.g. "export{Xt as Chessground,nr as initModule}" → "window.Chessground=Xt;"
  const exportMatch = cgJS.match(/export\{(\w+) as Chessground/);
  const cgInternalName = exportMatch ? exportMatch[1] : 'Chessground';
  const cgScript = cgJS.replace(/export\{[^}]+\}/, `window.Chessground=${cgInternalName};`);

  // Build self-contained HTML with inlined assets
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    ${cgBaseCSS}
    ${cgBrownCSS}
    ${cgPiecesCSS}
    * { margin: 0; padding: 0; }
    body { background: transparent; }
    #board {
      width: ${size}px;
      height: ${size}px;
    }
  </style>
</head>
<body>
  <div id="board"></div>
  <script>
    ${cgScript}

    const config = ${JSON.stringify(config)};
    const ground = window.Chessground(document.getElementById('board'), {
      fen: config.fen || 'start',
      viewOnly: true,
      coordinates: true,
      drawable: {
        enabled: false,
        visible: true,
        autoShapes: config.arrows || [],
      },
      highlight: {
        lastMove: true,
      },
      lastMove: config.lastMove || undefined,
    });
  </script>
</body>
</html>`;

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: size + 40, height: size + 40 },
  });

  await page.setContent(html, { waitUntil: 'networkidle' });

  // Wait for the board to render
  await page.waitForSelector('cg-board', { timeout: 5000 });
  await page.waitForTimeout(200);

  const board = await page.$('#board');
  await board.screenshot({ path: args.output, omitBackground: true });

  await browser.close();
  console.log(`Rendered: ${args.output} (${size}x${size})`);
})();
