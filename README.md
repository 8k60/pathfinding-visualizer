# Pathfinding Visualizer

An interactive `pygame` visualizer for comparing **A\*** and **Dijkstra** on a grid
with weighted terrain, plus a recursive-backtracking maze generator.

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Input | Action |
|---|---|
| Left click / drag | 1st click: Start, 2nd click: End, then paint with the active brush |
| Right click / drag | Erase a cell |
| `1` `2` `3` `4` | Brush: Wall / Swamp / Water / Highway |
| `Space` | Run A\* |
| `D` | Run Dijkstra |
| `M` | Generate a maze |
| `C` | Clear the grid |
| `R` | Clear the last search, keep the terrain |
| `L` | Show / hide the legend |

## Terrain costs

| Terrain | Colour | Cost to enter |
|---|---|---|
| Highway | Yellow | 0.5 |
| Path | White | 1 |
| Swamp | Brown | 5 |
| Water | Blue | 10 |
| Wall | Black | impassable |

After each run, the status line shows the path cost, how many cells were
explored and the number of steps, so you can compare the two algorithms on
the same map.

## Project layout

| File | Role |
|---|---|
| `config.py` | Pygame setup, window size, colours, terrain costs |
| `node.py` | `Node` class: a grid cell's state, weight and neighbours |
| `grid.py` | Grid creation, rendering, legend, mouse-to-cell mapping |
| `algorithms.py` | A\*, Dijkstra, heuristic, path reconstruction |
| `maze.py` | Recursive-backtracking maze generator |
| `main.py` | Event loop, brush system and controls |

A\* scales its Manhattan heuristic by the cheapest terrain cost (0.5) so it
never overestimates and always returns the cheapest path. Set
`HEURISTIC_WEIGHT = 1.0` in `config.py` to see a faster, greedier search that
can miss highway shortcuts.
