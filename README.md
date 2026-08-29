# Pathfinding Learning Tool

An interactive desktop application for learning how graph search algorithms explore a map.
Built with Pygame as an A-Level Computer Science NEA project.

The tool loads a real road network (exported from OpenStreetMap), lets you pick a start and
end node, and then animates **Depth-First Search**, **Dijkstra's Algorithm**, or **A\***
as it searches for a route. Alongside the animation you can watch either a running
event log or the algorithm's pseudocode with the current line highlighted.

## Features

- **Three algorithms** - Depth-First Search, Dijkstra's Algorithm, and A\*.
- **Real map data** - three pre-bundled maps: Littlehampton, Worthing and Manhattan.
- **Step-through or auto-run** - run the search continuously, pause/resume it, or advance
  one step at a time.
- **Two console views**
  - *Pseudocode view* - shows the algorithm's pseudocode and highlights the line currently
    executing.
  - *Log view* - a scrolling history of what the algorithm just did (nodes visited,
    neighbours pushed, time taken, nodes searched).
- **Visual feedback** - start node (green), end node (red), current node (purple),
  visited edges (yellow), final path (green).
- **Session logs** - the full console history is written to `logs/logN.txt` on exit.
- **Map downloader** - a helper script to fetch and save new road networks by place name.

## Requirements

- Python 3.10+
- The following packages:

```bash
pip install pygame networkx shapely osmnx
```

| Package | Used for |
|---|---|
| `pygame` | Window, rendering and input |
| `networkx` | Reading the `.graphml` map files |
| `shapely` | Parsing/rescaling curved road geometry (WKT) |
| `osmnx` | `mapdownloader.py` only – downloading new maps from OpenStreetMap |

## Running

From the project directory:

```bash
python main.py
```

### Controls

Click a node in the map area to set the **start** node, then click another to set the
**end** node. Then use the buttons:

| Button | Action |
|---|---|
| **Start** | Begin the search with the selected algorithm |
| **Pause** / **Resume** | Halt or continue an auto-running search |
| **Next Step** | Advance the search by a single step (while paused) |
| **Reset** | Clear the current search and node selection |
| **Search Type** | Cycle Depth-First → Dijkstra's → A\* (only before a search starts) |
| **Change Console** | Toggle between the pseudocode view and the log view |
| **Next Map** | Load the next bundled map (Littlehampton → Worthing → Manhattan) |

## Downloading new maps

```bash
python mapdownloader.py
```

Enter a place name (e.g. `Brighton, England`). The drivable road network is saved to
`data/<place>.graphml` and previewed in a plot window. To make a new map selectable in the
app, add its name to the list passed to `NextMapButton` in [main.py](main.py) (line 45).

## Project structure

| File / folder | Contents |
|---|---|
| `main.py` | Application entry point: game loop, rendering, and the three algorithms |
| `ui.py` | `Region` and `Button` classes for the interface layout |
| `utils.py` | `Stack`, `PriorityQueue` (bubble-sorted min-queue), and node-rescaling helper |
| `mapdownloader.py` | Standalone OSMnx script for fetching new map data |
| `data/` | Bundled `.graphml` road networks |
| `depthfirst.txt`, `dijkstras.txt`, `astar.txt` | Pseudocode shown in the console panel |
| `fonts/` | Lexend and Roboto Mono font files |
| `logs/` | Session console logs (created on first exit) |

## Notes

- The window is a fixed 1280×720 and is not resizable.
- `PriorityQueue` uses a bubble sort on every enqueue; it favours readability for the NEA
  over performance, so very large maps will search slowly.
