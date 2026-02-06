# Chess Board Renderer (Proof-of-Concept)

Renders chess board positions as PNG images using [Chessground](https://github.com/lichess-org/chessground) (the Lichess board UI) and [Playwright](https://playwright.dev/) for headless screenshot capture.

## Setup

```bash
cd renderers/chess
npm install
```

This installs Chessground, Playwright, and downloads a headless Chromium browser.

## Usage

```bash
# Basic: render a FEN position
node render.js --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --output board.png

# With arrows (orig+dest:color, comma-separated)
node render.js --fen "start" --output annotated.png --arrows "e2e4:green,d2d4:blue"

# With last move highlight
node render.js --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --output board.png --last-move "e2e4"

# Custom size (default: 800)
node render.js --fen "start" --output small.png --size 400
```

## Python Integration

```python
import subprocess

def render_chess_board(fen, output_path, arrows=None, size=800):
    cmd = ["node", "renderers/chess/render.js", "--fen", fen, "--output", output_path, "--size", str(size)]
    if arrows:
        cmd.extend(["--arrows", arrows])
    subprocess.run(cmd, check=True)
```

## Comparison with python-chess SVG

| Feature | python-chess SVG | Chessground (this) |
|---------|-----------------|-------------------|
| Dependencies | None (built-in) | Node.js + Playwright + Chromium |
| Render time | ~1ms | ~500ms (browser startup) |
| Output format | SVG (convert via CairoSVG) | PNG (direct) |
| Visual quality | Good, functional | Lichess-quality, polished |
| Arrows/highlights | Yes | Yes, with labels |
| Piece themes | One (Burnett) | Lichess Burnett (extensible) |
| Animation | No | No (screenshot) |

Use python-chess for fast, dependency-free rendering. Use this for higher visual fidelity when Node.js is available.
