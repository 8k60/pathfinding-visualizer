"""
maze.py — MODULE 5: Maze Generation (Recursive Backtracking)
=============================================================

Carves a "perfect" maze (exactly one route between any two open cells, no
loops) using the iterative form of recursive backtracking, a randomised
depth-first search driven by an explicit LIFO stack.

Why the "2-step rule"?
----------------------
Picture the grid as a lattice: cells on ODD (row, col) coordinates are
"rooms", and the cells between them are "walls". Moving two cells jumps
from one room to the next, and the cell in between is the wall that gets
knocked down. That is why the carver starts on an odd coordinate and always
looks exactly two steps away.
"""

import random
from typing import Callable

from grid import handle_quit_events
from node import Node

# Two-step jumps in the four cardinal directions: (d_row, d_col).
TWO_STEP_DIRECTIONS = ((-2, 0), (2, 0), (0, -2), (0, 2))


def generate_maze(draw: Callable[[], None], grid: list[list[Node]], rows: int) -> None:
    """Turn the whole grid into a randomly carved perfect maze."""

    # Step 1: fill everything with walls.
    for row in grid:
        for node in row:
            node.make_barrier()
    draw()

    # Step 2: seed the carver on an odd-coordinate room.
    first = grid[1][1]
    first.reset()
    visited = {first}
    stack = [first]  # Python list used as a LIFO stack (append / pop).

    # Step 3: depth-first carving.
    while stack:
        handle_quit_events()

        current = stack[-1]  # Peek at the top of the stack without removing it.

        # Collect unvisited rooms exactly two steps away. The bounds check uses
        # 0 < r < rows - 1 so the outermost ring always stays a solid border.
        candidates = []
        for d_row, d_col in TWO_STEP_DIRECTIONS:
            r, c = current.row + d_row, current.col + d_col
            if 0 < r < rows - 1 and 0 < c < rows - 1:
                room = grid[r][c]
                if room not in visited:
                    # The wall between `current` and `room` sits at the midpoint.
                    wall = grid[current.row + d_row // 2][current.col + d_col // 2]
                    candidates.append((room, wall))

        if candidates:
            # Go deeper: pick a random direction, knock down the wall between,
            # carve the new room, and make it the new top of the stack.
            room, wall = random.choice(candidates)
            wall.reset()
            room.reset()
            visited.add(room)
            stack.append(room)
        else:
            # Dead end: BACKTRACK to the previous room and try another branch.
            stack.pop()

        draw()  # Animate each carving / backtracking step.
