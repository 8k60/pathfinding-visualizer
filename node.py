"""
node.py — MODULE 2: The Node Class (Grid Cell)
===============================================

A Node is one square of the grid. It holds:
  * its POSITION  (row/col indices and x/y pixel coordinates),
  * its STATE     (encoded as a colour: empty, wall, open, closed, path ...),
  * its COST      (the terrain weight paid to step INTO this cell),
  * its NEIGHBORS (the walkable cells adjacent to it; this is the graph's edge list).

The grid is really a graph, and the algorithms only ever talk to it through
this class's public methods.
"""

import pygame

from config import (
    BLACK, BLUE, BROWN, GREEN, ORANGE, PURPLE, RED, TURQUOISE, WHITE, YELLOW,
    COST_BARRIER, COST_DEFAULT, COST_HIGHWAY, COST_SWAMP, COST_WATER,
    TERRAIN_COLORS,
)

# The four cardinal directions as (d_row, d_col): Up, Down, Left, Right.
CARDINAL_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))

# Colours that represent a temporary search state rather than terrain.
SEARCH_STATE_COLORS = (RED, GREEN, PURPLE)


class Node:
    """A single cell of the pathfinding grid."""

    def __init__(self, row: int, col: int, width: int, total_rows: int):
        self.row = row
        self.col = col
        # Pixel coordinates of the cell's top-left corner.
        # Column -> horizontal (x) axis, Row -> vertical (y) axis.
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors: list["Node"] = []
        self.width = width
        self.total_rows = total_rows
        self.weight = COST_DEFAULT

    # ------------------------------------------------------------------
    # State evaluators (return booleans)
    # ------------------------------------------------------------------
    def get_pos(self) -> tuple[int, int]:
        """Return the cell's (row, col) grid index."""
        return self.row, self.col

    def is_closed(self) -> bool:
        return self.color == RED

    def is_open(self) -> bool:
        return self.color == GREEN

    def is_barrier(self) -> bool:
        return self.color == BLACK

    def is_start(self) -> bool:
        return self.color == ORANGE

    def is_end(self) -> bool:
        return self.color == TURQUOISE

    def is_search_state(self) -> bool:
        """True if the colour is a temporary algorithm marker (open/closed/path)."""
        return self.color in SEARCH_STATE_COLORS

    # ------------------------------------------------------------------
    # Terrain modifiers: these change colour AND weight together
    # ------------------------------------------------------------------
    def reset(self) -> None:
        """Back to a plain, empty path cell (cost 1)."""
        self.color = WHITE
        self.weight = COST_DEFAULT

    def make_barrier(self) -> None:
        """Impassable wall. Infinite cost; also excluded from neighbour lists."""
        self.color = BLACK
        self.weight = COST_BARRIER

    def make_swamp(self) -> None:
        self.color = BROWN
        self.weight = COST_SWAMP

    def make_water(self) -> None:
        self.color = BLUE
        self.weight = COST_WATER

    def make_highway(self) -> None:
        self.color = YELLOW
        self.weight = COST_HIGHWAY

    # ------------------------------------------------------------------
    # Search-state modifiers: these change colour only.
    # The weight is left alone on purpose, so the terrain cost survives the
    # visualisation and can be restored afterwards (see restore_terrain).
    # ------------------------------------------------------------------
    def make_closed(self) -> None:
        self.color = RED

    def make_open(self) -> None:
        self.color = GREEN

    def make_path(self) -> None:
        self.color = PURPLE

    # Endpoints are treated as plain ground (cost 1) so the start and end
    # cells never add hidden terrain cost to the result.
    def make_start(self) -> None:
        self.color = ORANGE
        self.weight = COST_DEFAULT

    def make_end(self) -> None:
        self.color = TURQUOISE
        self.weight = COST_DEFAULT

    def restore_terrain(self) -> None:
        """Repaint the cell with the colour of its terrain weight.

        Used to wipe a previous search (red/green/purple) off the board while
        keeping the swamps, water and highways the user painted, so A* and
        Dijkstra can be compared on exactly the same map.
        """
        if self.is_search_state():
            self.color = TERRAIN_COLORS[self.weight]

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(self, win: pygame.Surface) -> None:
        """Draw this cell as a filled square.

        When a search colour (red/green/purple) covers a non-default terrain
        cell, a smaller square in the terrain colour is drawn in the middle so
        you can still see WHICH terrain the algorithm went through or avoided.
        """
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

        if self.is_search_state() and self.weight != COST_DEFAULT:
            inset = max(2, self.width // 4)
            inner = self.width - 2 * inset
            pygame.draw.rect(
                win,
                TERRAIN_COLORS[self.weight],
                (self.x + inset, self.y + inset, inner, inner),
            )

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------
    def update_neighbors(self, grid: list[list["Node"]]) -> None:
        """Rebuild self.neighbors from the four cardinal directions.

        A neighbour is added only if it is (a) inside the grid bounds and
        (b) not a barrier. This is how walls are removed from the graph:
        the algorithms never see an edge into a wall at all.
        """
        self.neighbors = []
        for d_row, d_col in CARDINAL_DIRECTIONS:
            r, c = self.row + d_row, self.col + d_col
            if 0 <= r < self.total_rows and 0 <= c < self.total_rows:
                candidate = grid[r][c]
                if not candidate.is_barrier():
                    self.neighbors.append(candidate)

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------
    def __lt__(self, other: "Node") -> bool:
        # PriorityQueue compares tuples element by element. Our tuples always
        # contain a unique counter before the Node, so this should never be
        # reached; it is defined as a safety net so a tie can never raise
        # "TypeError: '<' not supported between instances of 'Node'".
        return False

    def __repr__(self) -> str:
        return f"Node(row={self.row}, col={self.col}, weight={self.weight})"
