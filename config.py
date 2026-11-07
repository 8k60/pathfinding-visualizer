"""
config.py — MODULE 1: Global Configurations, Setup & Colours
=============================================================

Every other module imports its "magic numbers" from here, so changing the
window size, grid resolution, terrain costs or palette only ever requires an
edit in ONE place (the Single Source of Truth principle).
"""

import math

import pygame

# ---------------------------------------------------------------------------
# Pygame initialisation
# ---------------------------------------------------------------------------
# pygame.init() boots every pygame sub-system (display, events, timers ...).
# pygame.font.init() is called explicitly as well because the UI legend needs
# the font engine; calling it twice is harmless.
pygame.init()
pygame.font.init()

# ---------------------------------------------------------------------------
# Window / grid geometry
# ---------------------------------------------------------------------------
WIDTH = 800             # The window is square: WIDTH x WIDTH pixels.
ROWS = 50               # Grid is ROWS x ROWS cells -> each cell is 16 px.
WINDOW_TITLE = "Pathfinding Visualizer: A* vs Dijkstra on Weighted Terrain"


def create_window(width: int = WIDTH) -> pygame.Surface:
    """Create and return the square display surface.

    It is wrapped in a function, rather than created when the module is
    imported, so other modules (and unit tests) can import the configuration
    without a window popping up as a side effect.
    """
    win = pygame.display.set_mode((width, width))
    pygame.display.set_caption(WINDOW_TITLE)
    return win


# ---------------------------------------------------------------------------
# Colour taxonomy (RGB tuples)
# ---------------------------------------------------------------------------
# Terrain colours: these describe what a cell IS (its travel cost).
WHITE = (255, 255, 255)      # Default empty path       (cost 1)
BROWN = (139, 90, 43)        # Swamp terrain            (cost 5)
BLUE = (30, 100, 220)        # Deep water terrain       (cost 10)
YELLOW = (255, 215, 0)       # Highway terrain          (cost 0.5)
BLACK = (0, 0, 0)            # Barrier / wall           (cost infinity)

# Special endpoints.
ORANGE = (255, 165, 0)       # Start node
TURQUOISE = (64, 224, 208)   # End node

# Search-state colours: these describe what the ALGORITHM is doing.
RED = (235, 64, 52)          # Closed / visited (already expanded)
GREEN = (60, 200, 90)        # Open / queued (on the frontier)
PURPLE = (128, 0, 128)       # Final shortest path

# Chrome.
GREY = (128, 128, 128)       # Grid lines
LEGEND_BG = (20, 20, 20)     # Legend panel background
LEGEND_TEXT = (240, 240, 240)
LEGEND_ACCENT = (255, 215, 0)
LEGEND_ALPHA = 215           # 0 = fully transparent, 255 = opaque

# ---------------------------------------------------------------------------
# Terrain travel costs (the edge weight paid to ENTER a cell)
# ---------------------------------------------------------------------------
COST_DEFAULT = 1
COST_SWAMP = 5
COST_WATER = 10
COST_HIGHWAY = 0.5
COST_BARRIER = math.inf

# The cheapest possible step on the map. A* uses it to keep its heuristic
# admissible (see algorithms.py for the full explanation).
MIN_TERRAIN_COST = min(COST_DEFAULT, COST_SWAMP, COST_WATER, COST_HIGHWAY)

# Multiplier applied to the Manhattan heuristic inside A*.
#   = MIN_TERRAIN_COST -> A* is guaranteed to find the cheapest path.
#   = 1.0              -> A* is faster and greedier but can miss highway shortcuts.
# Try both and watch how the search changes.
HEURISTIC_WEIGHT = MIN_TERRAIN_COST

# Reverse lookup: weight -> colour. Used to repaint terrain after a search has
# painted cells red/green/purple, and to draw the terrain "inset" on top of
# search colours so the terrain stays visible during a run.
TERRAIN_COLORS = {
    COST_DEFAULT: WHITE,
    COST_SWAMP: BROWN,
    COST_WATER: BLUE,
    COST_HIGHWAY: YELLOW,
    COST_BARRIER: BLACK,
}

# ---------------------------------------------------------------------------
# Brush system
# ---------------------------------------------------------------------------
BRUSH_WALL = "wall"
BRUSH_SWAMP = "swamp"
BRUSH_WATER = "water"
BRUSH_HIGHWAY = "highway"
DEFAULT_BRUSH = BRUSH_WALL

# ---------------------------------------------------------------------------
# Fonts & timing
# ---------------------------------------------------------------------------
# Font(None, size) loads pygame's bundled default font, which works on every
# OS. SysFont lookups can fail on minimal systems.
LEGEND_FONT = pygame.font.Font(None, 20)
LEGEND_PADDING = 6
FPS = 120                    # Frame cap for the idle editor loop.
