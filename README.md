# DDW 10.020 — Midterm Revision App

An interactive Streamlit app for revising the midterm topics in **Data Driven
World (10.020)**. It is derived from the Mini Project 1 sorting app: the sorting
engine and its visual style are kept, while Exercises 2 and 3 are re-purposed and
Exercise 4 is added for revision.

## The five sections

| Page | What it does |
|------|--------------|
| **Home** | Landing page with shortcuts to each exercise. |
| **Exercise 1 — Sorting Visualizer** | Generate a random array and watch **Bubble, Insertion, Heap, Merge** and **Quick** sort animate step by step (comparisons & swaps), with live time/space-complexity metrics (peak memory + runtime). Below the visualizer, an **information & code-along guide** (one `st.tabs` per algorithm) gives a plain-English explanation, best/average/worst + space complexity, and a Python implementation to code along with. |
| **Exercise 2 — Complexity Quiz** | Randomly generated questions on **Big-O (O), little-o (o), Θ and Ω**. Two kinds: *(a)* read a code snippet and pick its **time or space** complexity; *(b)* given `f(n)` and `g(n)`, select **every** notation for which `f ∈ N(g)`. Scored, with immediate feedback and a teaching explanation after every answer. All state via `st.session_state`. |
| **Exercise 3 — Graph Traversal (MRT)** | A guided graph tutorial on a small **Singapore MRT** subgraph. Explains vertices / edges / adjacency, then steps through **BFS (queue, FIFO)** and **DFS (stack, LIFO)** one frontier operation at a time. Renders the (collapsible) network map, the evolving frontier / visited set / visit order, and the eventual **BFS & DFS spanning trees** — all with `st.graphviz_chart`. A **BFS vs DFS** tab covers the DDW concepts (colours, `d`/`f` times, shortest paths), the O(V + E) complexity and memory-shape differences, and when to use each. |
| **Exercise 4 — Object-Oriented Programming** | A hands-on OOP workshop (Weeks 4–5): a **live `Fraction` class** whose dunder methods (`__str__`/`__add__`/`__lt__`/`__eq__`/`__repr__`) react to your inputs, followed by concept tabs — classes & objects, encapsulation & properties, dunder methods, inheritance & `super()`, polymorphism & abstract methods, and class/static methods — each with a runnable example and a "special technique" call-out. |

## Running it

Uses [`uv`](https://docs.astral.sh/uv/) for the virtual environment and packages.

```bash
# from this directory (DDW-Midterm-Revision/)
uv sync                         # create the venv and install deps
uv run streamlit run Home.py    # launch the multipage app
```

Then open the printed local URL (default <http://localhost:8501>). Use the sidebar
to switch between Home and the three exercises.

To run headless (no browser auto-open):

```bash
uv run streamlit run Home.py --server.headless true
```

## Tests

```bash
uv run pytest -q
```

Covers the preserved sort algorithms/metrics/views, plus the new `Models/Graph.py`
(BFS/DFS correctness, spanning trees) and `Models/Complexity.py` (question
generation + grading), and Streamlit `AppTest` smoke journeys for every page.

## The MRT subgraph (Exercise 3)

Twelve hub stations, connected when a train runs directly between them along a
real MRT line (intermediate stops contracted away). Interchanges give the graph
cycles, so BFS and DFS produce visibly different spanning trees.

- **Stations:** Jurong East, Bishan, Botanic Gardens, Buona Vista, HarbourFront,
  Outram Park, Chinatown, Serangoon, Dhoby Ghaut, City Hall, Raffles Place,
  Marina Bay.
- **Lines:** North-South (NSL), East-West (EWL), North-East (NEL), Circle (CCL),
  Downtown (DTL) — edges are coloured by line.
- Neighbours are visited in **alphabetical order** so every run is reproducible.

## Project layout

```
Home.py                     # landing page (multipage entry point)
pages/
  1_Exercise_1.py           # sorting visualizer (kept)
  2_Exercise_2.py           # complexity quiz (new)
  3_Exercise_3.py           # MRT graph traversal (new)
  4_Exercise_4.py           # OOP workshop (new)
Models/
  Algorithms.py             # Bubble/Insertion/Heap/Merge/Quick sorts (kept + Quick added)
  Complexity.py             # quiz question generator (new)
  Graph.py                  # MRT graph + BFS/DFS traces (new)
  SortGuide.py              # per-algorithm code-along guide content (new)
  OOPDemo.py                # live Fraction class for the OOP demo (new)
  OOPGuide.py               # OOP concept + example-code content (new)
Utilities/
  GraphView.py              # sort-visualizer render helpers + colour palette (kept)
  TransitView.py            # MRT graphviz + frontier/visited chips (new)
  Metrics.py                # timing/memory + st.metric row (kept)
library.py                  # random-array helpers (kept)
tests/                      # pytest suites
```

`st.graphviz_chart` renders DOT **client-side**, so no system Graphviz binary is
required — the graphs are built as DOT strings.
