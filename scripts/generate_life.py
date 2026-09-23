#!/usr/bin/env python3
"""
Generate an animated Conway's Game of Life ASCII SVG.
GitHub strips <script>, so this uses the SMIL "flipbook" technique:
every generation is pre-rendered as a <text> block, all stacked, and a
single discrete <animate> on each block's opacity cycles through them.
Loops forever via repeatCount="indefinite".
"""
import random
import sys

COLS = 70
ROWS = 40
GENERATIONS = 60
FRAME_DUR = 0.28          # seconds per generation
FONT_SIZE = 11
CHAR_W = 6.6
LINE_H = 11
ALIVE = "#"
DEAD = " "
FILL = "#c9d1d9"
BG = "#0d1117"
SEED = 7


def random_grid(cols, rows, density=0.32, seed=SEED):
    rnd = random.Random(seed)
    return [[1 if rnd.random() < density else 0 for _ in range(cols)] for _ in range(rows)]


def step(grid):
    rows, cols = len(grid), len(grid[0])
    new = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    rr, cc = (r + dr) % rows, (c + dc) % cols  # toroidal wrap
                    n += grid[rr][cc]
            alive = grid[r][c]
            if alive and n in (2, 3):
                new[r][c] = 1
            elif not alive and n == 3:
                new[r][c] = 1
            else:
                new[r][c] = 0
    return new


def render_frame(grid):
    return "\n".join("".join(ALIVE if v else DEAD for v in row) for row in grid)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(frames):
    n = len(frames)
    width = round(COLS * CHAR_W) + 20
    height = round(ROWS * LINE_H) + 20
    dur = n * FRAME_DUR

    defs = (
        "\n  <defs>\n    <style>\n"
        "      .fr { font-family: 'JetBrains Mono','Liberation Mono','DejaVu Sans Mono',monospace;\n"
        f"            font-size: {FONT_SIZE}px; fill: {FILL}; white-space: pre; }}\n"
        "    </style>\n  </defs>"
    )

    body = []
    # discrete opacity keyframes: frame i is 1 only during its own slot
    keytimes = [round(i / n, 4) for i in range(n)] + [1]
    for i, frame_text in enumerate(frames):
        lines = frame_text.split("\n")
        tspans = "".join(
            f'<tspan x="10" dy="{LINE_H if li else 0}">{esc(line)}</tspan>'
            for li, line in enumerate(lines)
        )
        values = ["0"] * n
        values[i] = "1"
        values_attr = ";".join(values + [values[0]])
        keytimes_attr = ";".join(str(kt) for kt in keytimes)

        body.append(
            f'  <text y="18" class="fr" opacity="0">{tspans}'
            f'<animate attributeName="opacity" values="{values_attr}" '
            f'keyTimes="{keytimes_attr}" dur="{dur}s" begin="0s" '
            f'calcMode="discrete" repeatCount="indefinite"/>'
            f'</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'  <rect width="100%" height="100%" fill="{BG}"/>{defs}\n'
        + "\n".join(body)
        + "\n</svg>"
    )
    return svg


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "life.svg"
    grid = random_grid(COLS, ROWS)
    frames = []
    for _ in range(GENERATIONS):
        frames.append(render_frame(grid))
        grid = step(grid)
    svg = build_svg(frames)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}: {GENERATIONS} generations, {COLS}x{ROWS} grid, ~{GENERATIONS*FRAME_DUR:.1f}s loop")


if __name__ == "__main__":
    main()
