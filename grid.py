"""
grid.py — MODULE 3: Grid Rendering & UI Legend
===============================================

Helper functions for the Pygame canvas: building the grid, drawing it,
drawing the on-screen legend, and turning mouse pixels into grid indices.
It also has a few small grid utilities shared by the other modules.
"""

import sys
from functools import lru_cache

import pygame

from config import (
    BLACK, BLUE, BROWN, GREY, ORANGE, PURPLE, TURQUOISE, WHITE, YELLOW,
    LEGEND_ACCENT, LEGEND_ALPHA, LEGEND_BG, LEGEND_FONT, LEGEND_PADDING,
    LEGEND_TEXT,
)
from node import Node

# Static control lines shown in the legend.
CONTROL_LINES = (
    "L-Click: Start, End, then paint   R-Click: Erase   "
    "1: Wall  2: Swamp  3: Water  4: Highway",
    "Space: A*   D: Dijkstra   M: Maze   C: Clear   "
    "R: Reset search   L: Toggle legend",
)

# Colour key: (label, colour). Costs are shown next to each terrain.
TERRAIN_KEY = (
    ("Path 1", WHITE),
    ("Highway 0.5", YELLOW),
    ("Swamp 5", BROWN),
    ("Water 10", BLUE),
    ("Wall inf", BLACK),
    ("Start", ORANGE),
    ("End", TURQUOISE),
    ("Route", PURPLE),
)

# 2 control lines + 1 colour-key line + 1 status line.
LEGEND_LINE_COUNT = len(CONTROL_LINES) + 2


# ---------------------------------------------------------------------------
# Grid construction
# ---------------------------------------------------------------------------
def make_grid(rows: int, width: int) -> list[list[Node]]:
    """Return a rows x rows 2D list of Node objects, indexed grid[row][col]."""
    gap = width // rows  # Pixel width of one cell.
    return [[Node(r, c, gap, rows) for c in range(rows)] for r in range(rows)]


def update_all_neighbors(grid: list[list[Node]]) -> None:
    """Rebuild every node's adjacency list. Call this just before a search,
    because walls may have been painted or erased since the last run."""
    for row in grid:
        for node in row:
            node.update_neighbors(grid)


def reset_search(grid: list[list[Node]]) -> None:
    """Remove red/green/purple search markers but keep walls and terrain."""
    for row in grid:
        for node in row:
            node.restore_terrain()


def handle_quit_events() -> None:
    """Drain the event queue while a long animation runs.

    The search and maze loops never return control to main() until they
    finish, so the window would freeze and "Not Responding" would appear if
    they didn't keep pumping events. Closing the window exits cleanly.
    Other events (key presses, clicks) are dropped on purpose, so input made
    during an animation doesn't fire actions after it ends.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------
def draw_grid(win: pygame.Surface, rows: int, width: int) -> None:
    """Draw the GREY lines that separate the cells."""
    gap = width // rows
    for i in range(rows + 1):
        # Horizontal line for row boundary i.
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        # Vertical line for column boundary i.
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))


@lru_cache(maxsize=256)
def _render_text(text: str, color: tuple[int, int, int]) -> pygame.Surface:
    """Render text once and cache it. font.render() is fairly costly and the
    legend is redrawn every frame, often with the same strings."""
    return LEGEND_FONT.render(text, True, color)


def legend_height() -> int:
    """Pixel height of the legend panel (used to ignore clicks under it)."""
    return LEGEND_PADDING * 2 + LEGEND_FONT.get_linesize() * LEGEND_LINE_COUNT


def draw_legend(win: pygame.Surface, current_brush: str | None = None,
                status: str = "") -> None:
    """Draw a semi-transparent panel along the bottom with controls, a colour
    key, the active brush and the result of the last search."""
    win_w, win_h = win.get_size()
    height = legend_height()
    top = win_h - height
    line_h = LEGEND_FONT.get_linesize()

    # A surface with per-pixel alpha lets the grid show through faintly.
    panel = pygame.Surface((win_w, height), pygame.SRCALPHA)
    panel.fill((*LEGEND_BG, LEGEND_ALPHA))
    win.blit(panel, (0, top))

    y = top + LEGEND_PADDING

    # 1) Control lines.
    for line in CONTROL_LINES:
        win.blit(_render_text(line, LEGEND_TEXT), (LEGEND_PADDING, y))
        y += line_h

    # 2) Colour key with small swatches.
    x = LEGEND_PADDING
    swatch = line_h - 4
    for label, color in TERRAIN_KEY:
        pygame.draw.rect(win, color, (x, y + 1, swatch, swatch))
        pygame.draw.rect(win, GREY, (x, y + 1, swatch, swatch), 1)
        text = _render_text(label, LEGEND_TEXT)
        win.blit(text, (x + swatch + 4, y))
        x += swatch + 4 + text.get_width() + 12

    # Active brush, right-aligned on the same line.
    if current_brush:
        brush_text = _render_text(f"Brush: {current_brush.upper()}", LEGEND_ACCENT)
        win.blit(brush_text, (win_w - brush_text.get_width() - LEGEND_PADDING, y))
    y += line_h

    # 3) Status line (last search result, hints, etc.).
    if status:
        win.blit(_render_text(status, LEGEND_ACCENT), (LEGEND_PADDING, y))


def draw(win: pygame.Surface, grid: list[list[Node]], rows: int, width: int,
         current_brush: str | None = None, status: str = "",
         show_legend: bool = True) -> None:
    """Redraw one full frame: background, cells, grid lines, legend, flip.

    The algorithms receive this as a zero-argument callback (via a closure in
    main.py), so they can animate without knowing anything about rendering.
    """
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    if show_legend:
        draw_legend(win, current_brush, status)
    pygame.display.update()


# ---------------------------------------------------------------------------
# Input translation
# ---------------------------------------------------------------------------
def get_clicked_pos(pos: tuple[int, int], rows: int, width: int) -> tuple[int, int]:
    """Translate raw pixel coordinates (x, y) into grid indices (row, col).

    y (vertical) gives the row and x (horizontal) gives the column. The
    result is clamped so a click on the very last pixel can't go out of range.
    """
    gap = width // rows
    x, y = pos
    row = min(max(y // gap, 0), rows - 1)
    col = min(max(x // gap, 0), rows - 1)
    return row, col
