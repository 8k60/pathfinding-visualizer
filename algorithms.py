"""
algorithms.py — MODULE 4: Pathfinding Algorithms (Topography Aware)
====================================================================

Two best-first searches over a WEIGHTED grid graph:

    * A*        priority = g(n) + h(n)   (informed search)
    * Dijkstra  priority = g(n)          (uninformed search)

Terminology
-----------
g(n)  "g_score"  The cheapest known cost from START to n so far. On weighted
                 terrain this is a sum of terrain weights, not a step count:
                 walking through 3 swamp cells costs 15, not 3.
h(n)  heuristic  An estimate of the remaining cost from n to END.
f(n)  "f_score"  g(n) + h(n), A*'s estimate of the full START->n->END cost.

Edge-weight convention: moving from `current` into `neighbor` costs
`neighbor.weight`, the price of ENTERING the neighbour's terrain.

Both functions take a zero-argument `draw` callback and call it while they
work, so the user can watch the frontier (GREEN) and the explored region
(RED) grow in real time.
"""

import math
from dataclasses import dataclass
from queue import PriorityQueue
from typing import Callable

from config import HEURISTIC_WEIGHT
from grid import handle_quit_events
from node import Node

Grid = list[list[Node]]
DrawFn = Callable[[], None]


# ---------------------------------------------------------------------------
# Result object: used to compare the algorithms in the legend's status line
# ---------------------------------------------------------------------------
@dataclass
class SearchResult:
    algorithm: str
    found: bool
    cost: float = math.inf       # Total terrain cost of the path found.
    nodes_expanded: int = 0      # How many nodes were popped and closed.
    path_steps: int = 0          # Number of moves in the final path.

    def summary(self) -> str:
        if not self.found:
            return (f"{self.algorithm}: NO PATH exists   "
                    f"(expanded {self.nodes_expanded} nodes)")
        return (f"{self.algorithm}: cost {self.cost:g}   |   "
                f"expanded {self.nodes_expanded} nodes   |   "
                f"{self.path_steps} steps")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def h(p1: tuple[int, int], p2: tuple[int, int]) -> int:
    """Manhattan distance between two (row, col) positions.

    With 4-directional movement (no diagonals) the fewest moves between two
    cells is |dr| + |dc|, so this is the natural distance measure for our grid.
    """
    r1, c1 = p1
    r2, c2 = p2
    return abs(r1 - r2) + abs(c1 - c2)


def reconstruct_path(came_from: dict[Node, Node], current: Node,
                     draw: DrawFn) -> int:
    """Walk backwards from END to START through `came_from`, colouring each
    node PURPLE. Return the number of steps in the path.

    `came_from[n]` stores the node we arrived at n from on its cheapest known
    route. Following those links backwards traces the optimal path in reverse.
    The start and end cells keep their own colours.
    """
    steps = 0
    while current in came_from:
        current = came_from[current]
        steps += 1
        if not current.is_start():
            current.make_path()
        draw()
    return steps


# ---------------------------------------------------------------------------
# A* (A-Star)
# ---------------------------------------------------------------------------
def a_star(draw: DrawFn, grid: Grid, start: Node, end: Node) -> SearchResult:
    """Weighted A* search from `start` to `end`.

    HOW A* SEARCHES (compare with dijkstra() below)
    -----------------------------------------------
    A* ranks every frontier node by f = g + h. The g part pulls it towards
    nodes that were cheap to reach; the h part pulls it towards nodes that
    are GEOMETRICALLY CLOSE TO THE GOAL. As a result the explored (RED)
    region stretches into a narrow cone pointing at END. Nodes "behind"
    the start have a large h, so they sit at the back of the queue and are
    usually never expanded.

    On weighted terrain this gives a characteristic look: A* heads straight
    at the goal, and only when it hits expensive swamp or water (g jumps)
    does it start spilling sideways to look for a cheaper way round. It is
    "optimistic first, careful only when forced".

    WHY THE HEURISTIC IS SCALED (an important teaching point)
    ----------------------------------------------------------
    A* is only guaranteed to return the CHEAPEST path if h never
    OVERESTIMATES the true remaining cost (the heuristic must be
    "admissible"). Plain Manhattan distance assumes every step costs at least
    1, but a highway step costs only 0.5. Near a highway, raw Manhattan
    would overestimate, and A* could return a path that is not the cheapest.
    Multiplying by the cheapest terrain cost (HEURISTIC_WEIGHT = 0.5, set in
    config.py) makes h a guaranteed lower bound again. It is also
    "consistent", so a node never needs to be re-opened once closed.
    Set HEURISTIC_WEIGHT = 1.0 to trade correctness for a faster, greedier
    search and watch it skip highway shortcuts.
    """
    count = 0  # Tie-breaker: insertion order for nodes with equal priority.
    open_set: PriorityQueue = PriorityQueue()

    # g_score: cheapest known cost from start to each node (infinity = unknown).
    g_score = {node: math.inf for row in grid for node in row}
    g_score[start] = 0

    end_pos = end.get_pos()

    def heuristic(node: Node) -> float:
        return HEURISTIC_WEIGHT * h(node.get_pos(), end_pos)

    # Queue entries are (f_score, h_score, count, node).
    # h_score is the SECOND key: among nodes with equal f, prefer the one
    # closer to the goal. This tie-break keeps A* from fanning out across
    # large equal-f plateaus, which are common on uniform terrain.
    start_h = heuristic(start)
    open_set.put((start_h, start_h, count, start))

    came_from: dict[Node, Node] = {}
    closed: set[Node] = set()   # Nodes whose cheapest cost is final.
    expanded = 0

    while not open_set.empty():
        handle_quit_events()  # Keep the window responsive.

        _, _, _, current = open_set.get()

        # PriorityQueue has no "decrease-key" operation, so when we find a
        # cheaper route to a node we simply push it AGAIN with a better
        # priority. The old, worse entry is still in the queue; it is "stale"
        # and is skipped here when it eventually comes out ("lazy deletion").
        if current in closed:
            continue
        closed.add(current)
        expanded += 1

        # Goal test happens when END is POPPED, not when it is first queued.
        # Popping means no cheaper route to END can still exist.
        if current is end:
            steps = reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return SearchResult("A*", True, g_score[end], expanded, steps)

        for neighbor in current.neighbors:
            if neighbor in closed:
                continue

            # TOPOGRAPHY-AWARE RELAXATION: the cost of the move is the
            # terrain weight of the cell being entered, not a flat 1.
            temp_g_score = g_score[current] + neighbor.weight

            if temp_g_score < g_score[neighbor]:
                # A cheaper route to `neighbor` was found through `current`.
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                h_score = heuristic(neighbor)
                f_score = temp_g_score + h_score
                count += 1
                open_set.put((f_score, h_score, count, neighbor))
                if neighbor is not end:
                    neighbor.make_open()          # GREEN: queued on frontier

        draw()

        if current is not start:
            current.make_closed()                 # RED: fully evaluated

    # The queue emptied without reaching END: it is walled off.
    return SearchResult("A*", False, nodes_expanded=expanded)


# ---------------------------------------------------------------------------
# Dijkstra
# ---------------------------------------------------------------------------
def dijkstra(draw: DrawFn, grid: Grid, start: Node, end: Node) -> SearchResult:
    """Dijkstra's shortest-path search from `start` to `end`.

    HOW DIJKSTRA SEARCHES (compare with a_star() above)
    ---------------------------------------------------
    Dijkstra is A* with h(n) = 0 for every node. Its priority is ONLY
    g(n), the cost already paid to get there. It has no idea where END is,
    which is why it is called an "uninformed" search.

    Physically, this makes the search spread out like a RIPPLE from a stone
    dropped in a pond. Every node is expanded in strict order of travel cost
    from the start, in ALL directions equally, including directly away
    from the goal. The RED region is an "iso-cost contour": every red cell
    is cheaper to reach than every cell still outside it.

    On weighted terrain the ripple shows the topography very clearly:
      * On plain ground it grows as a diamond (Manhattan circle).
      * It races ALONG yellow highways (0.5), which stick out like fingers.
      * It slows to a crawl in brown swamp (5) and barely seeps into blue
        water (10). The wavefront visibly bends around expensive terrain.

    A* (above) uses h to aim at the goal, so it usually expands far fewer
    nodes. Dijkstra always pays for its blindness with a much larger
    explored area. Both return a path of the SAME minimum cost (A* thanks to
    its admissible, scaled heuristic). Compare the "cost" and "expanded"
    numbers in the status line after running each on the same map.
    """
    count = 0
    open_set: PriorityQueue = PriorityQueue()

    g_score = {node: math.inf for row in grid for node in row}
    g_score[start] = 0

    # Queue entries are (g_score, count, node). Note there is NO heuristic
    # term: the queue is ordered purely by distance from the start.
    open_set.put((0, count, start))

    came_from: dict[Node, Node] = {}
    closed: set[Node] = set()
    expanded = 0

    while not open_set.empty():
        handle_quit_events()

        _, _, current = open_set.get()

        # Lazy deletion of stale duplicate entries (see a_star for details).
        if current in closed:
            continue
        closed.add(current)
        expanded += 1

        # With non-negative weights, the first time a node is popped its g is
        # final, so popping END means we hold the cheapest path to it.
        if current is end:
            steps = reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return SearchResult("Dijkstra", True, g_score[end], expanded, steps)

        for neighbor in current.neighbors:
            if neighbor in closed:
                continue

            # Same terrain-aware edge cost as A*.
            temp_g_score = g_score[current] + neighbor.weight

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                count += 1
                # Priority = g only. Contrast with A*'s (g + h).
                open_set.put((temp_g_score, count, neighbor))
                if neighbor is not end:
                    neighbor.make_open()          # GREEN: queued on frontier

        draw()

        if current is not start:
            current.make_closed()                 # RED: fully evaluated

    return SearchResult("Dijkstra", False, nodes_expanded=expanded)
