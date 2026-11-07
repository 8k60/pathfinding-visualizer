"""
main.py — MODULE 6: The Main Event Loop (Control Flow & Brush System)
======================================================================

Run with:   python main.py

Controls
--------
Left click / drag   1st click = Start, 2nd click = End, then paint with brush
Right click / drag  Erase (reset) a cell
1 / 2 / 3 / 4       Brush: Wall / Swamp / Water / Highway
SPACE               Run A*
D                   Run Dijkstra
M                   Generate a maze (clears start/end)
C                   Clear the entire grid
R                   Reset the last search, keeping walls and terrain
L                   Show / hide the legend

Suggested experiment: paint a band of water between Start and End with a
narrow highway gap, run A* (SPACE), then Dijkstra (D) on the same map. The
previous search is cleared automatically before each run, so you can compare
the "cost" and "expanded" figures in the status line directly.
"""

import pygame

from algorithms import a_star, dijkstra
from config import (
    BRUSH_HIGHWAY, BRUSH_SWAMP, BRUSH_WALL, BRUSH_WATER, DEFAULT_BRUSH, FPS,
    ROWS, WIDTH, create_window,
)
from grid import (
    draw, get_clicked_pos, legend_height, make_grid, reset_search,
    update_all_neighbors,
)
from maze import generate_maze
from node import Node

# Key -> brush name.
BRUSH_KEYS = {
    pygame.K_1: BRUSH_WALL,
    pygame.K_2: BRUSH_SWAMP,
    pygame.K_3: BRUSH_WATER,
    pygame.K_4: BRUSH_HIGHWAY,
}

# Brush name -> unbound Node method. A lookup table replaces a long
# if/elif chain and makes adding a new terrain a one-line change.
BRUSH_ACTIONS = {
    BRUSH_WALL: Node.make_barrier,
    BRUSH_SWAMP: Node.make_swamp,
    BRUSH_WATER: Node.make_water,
    BRUSH_HIGHWAY: Node.make_highway,
}

# Key -> (algorithm function, display name).
ALGORITHM_KEYS = {
    pygame.K_SPACE: (a_star, "A*"),
    pygame.K_d: (dijkstra, "Dijkstra"),
}


def main(win: pygame.Surface, width: int) -> None:
    rows = ROWS
    grid = make_grid(rows, width)

    start: Node | None = None
    end: Node | None = None
    current_brush = DEFAULT_BRUSH
    status = "Left-click to place Start, then End. Paint terrain, then SPACE (A*) or D (Dijkstra)."
    show_legend = True

    # After placing Start or End, ignore the left button until it is released.
    # Otherwise holding the click and moving slightly would drop the End
    # right next to the Start, or paint a wall over the next cell.
    left_click_locked = False

    clock = pygame.time.Clock()

    def redraw() -> None:
        """Zero-argument draw callback handed to the algorithms.

        It is a closure: it reads grid, current_brush, status, etc. from
        main()'s scope at CALL time, so it always draws the latest state.
        """
        draw(win, grid, rows, width, current_brush, status, show_legend)

    def pointer_over_legend(pos: tuple[int, int]) -> bool:
        """True if the mouse is over the legend panel (clicks there are ignored)."""
        return show_legend and pos[1] >= width - legend_height()

    run = True
    while run:
        clock.tick(FPS)
        redraw()

        # ------------------------------------------------------------------
        # Discrete events: window close and key presses
        # ------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.KEYDOWN:
                # Brush selection.
                if event.key in BRUSH_KEYS:
                    current_brush = BRUSH_KEYS[event.key]
                    status = f"Brush set to {current_brush.upper()}."

                # Run a pathfinding algorithm.
                elif event.key in ALGORITHM_KEYS:
                    if not (start and end):
                        status = "Place both a Start and an End node first."
                        continue
                    algorithm, name = ALGORITHM_KEYS[event.key]
                    reset_search(grid)            # Wipe the previous run's colours.
                    update_all_neighbors(grid)    # Rebuild graph edges (walls may have changed).
                    status = f"Running {name}..."
                    result = algorithm(redraw, grid, start, end)
                    status = result.summary()

                # Maze generation.
                elif event.key == pygame.K_m:
                    start = end = None            # They'd be overwritten by walls anyway.
                    status = "Carving maze (recursive backtracking)..."
                    generate_maze(redraw, grid, rows)
                    status = "Maze ready. Place Start and End on white cells."

                # Clear everything.
                elif event.key == pygame.K_c:
                    start = end = None
                    grid = make_grid(rows, width)
                    status = "Grid cleared."

                # Clear only the search visualisation.
                elif event.key == pygame.K_r:
                    reset_search(grid)
                    status = "Search cleared. Terrain kept."

                # Toggle legend visibility.
                elif event.key == pygame.K_l:
                    show_legend = not show_legend

        # ------------------------------------------------------------------
        # Continuous mouse state: polled every frame so click-and-drag paints
        # ------------------------------------------------------------------
        buttons = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()

        if not buttons[0]:
            left_click_locked = False

        if buttons[0] and not left_click_locked and not pointer_over_legend(pos):
            # LEFT CLICK: Start -> End -> paint with the current brush.
            row, col = get_clicked_pos(pos, rows, width)
            node = grid[row][col]

            if not start and node is not end:
                start = node
                start.make_start()
                left_click_locked = True

            elif not end and node is not start:
                end = node
                end.make_end()
                left_click_locked = True

            elif node is not start and node is not end:
                BRUSH_ACTIONS[current_brush](node)

        elif buttons[2] and not pointer_over_legend(pos):
            # RIGHT CLICK: erase the cell (and forget it if it was an endpoint).
            row, col = get_clicked_pos(pos, rows, width)
            node = grid[row][col]
            node.reset()
            if node is start:
                start = None
            elif node is end:
                end = None

    pygame.quit()


if __name__ == "__main__":
    main(create_window(WIDTH), WIDTH)
